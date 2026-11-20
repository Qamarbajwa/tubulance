"""Shared reusable linear-solver abstraction for ``pressure.py`` and
``diffusion.py`` (Milestone 7, Part A).

Both callers assemble a sparse matrix once (per mesh/BC-topology/nu/dt)
and solve it repeatedly (once per time step). Before this module, each
caller reimplemented its own direct/CG dispatch, its own diagnostics
struct, and its own iteration-counting callback. This module factors
that out into one place: a :class:`LinearSolver` wraps ONE fixed sparse
matrix, performing matrix-dependent setup exactly once (LU factorization
for ``"direct"``, a Jacobi diagonal or a PyAMG hierarchy for the chosen
preconditioner), and :meth:`LinearSolver.solve` may be called repeatedly
against different right-hand sides (and, for iterative methods, an
optional initial guess ``x0`` -- Part D's warm starts) reusing that
setup.

Matrix-property-driven solver selection (not "expose everything and let
the caller pick blindly")
------------------------------------------------------------------------
The review's Part A explicitly requires: "The implementation must select
solvers according to matrix properties, not merely expose arbitrary
choices... Do not silently use CG on nonsymmetric matrices." This module
enforces that by requiring the caller to *declare* what it knows about
the matrix's structure via ``matrix_kind``:

* ``MatrixKind.SPD`` -- symmetric positive (semi-)definite (e.g.
  ``pressure.py``'s ``A = -L_h``, or ``diffusion.py``'s new
  boundary-eliminated normal-axis formulation, Milestone 7 Part C).
  ``direct``, ``cg``, ``bicgstab``, and ``gmres`` are all valid.
* ``MatrixKind.GENERAL`` -- no symmetry/definiteness guarantee (e.g.
  ``diffusion.py``'s original boundary-pin-row formulation, which is
  genuinely nonsymmetric). ``cg`` is refused at construction time
  (:class:`LinearSolverError`); ``direct``, ``bicgstab``, and ``gmres``
  remain valid.

This is a static, construction-time check based on the caller's
declaration, not runtime matrix inspection (checking exact symmetry of a
large sparse matrix on every solve would itself be expensive) -- exactly
mirroring how ``pressure.py`` and ``diffusion.py`` already *know*
their own matrix's structure from how it was assembled, and simply need
to declare it truthfully.

Diagnostics
-----------
:class:`LinearSolveResult` reports ``setup_time`` (matrix-dependent
factorization/hierarchy construction -- charged once at
:class:`LinearSolver` construction, exposed on every result for
convenience), ``preconditioner_time`` (Jacobi diagonal / PyAMG hierarchy
construction, also once), and ``solve_time`` (the repeated part, charged
per call) as three separate numbers -- never merged -- so a caller
building a profiling breakdown (Part I) can attribute cost correctly
across many repeated solves that all share one ``setup_time``.

Optional PyAMG backend (Part B)
--------------------------------
``preconditioner="amg"`` uses `PyAMG <https://pyamg.readthedocs.io/>`_'s
Ruge-Stuben classical algebraic multigrid solver as a
:class:`~scipy.sparse.linalg.LinearOperator` preconditioner for CG (the
standard "AMG-preconditioned CG" pattern, robust for the SPD pressure
Poisson matrix regardless of BC topology, including the periodic/
all-Neumann null-space case -- the null space itself is still handled by
``pressure.py`` exactly as before, e.g. via ``pin_cell`` elimination or
post-solve mean removal; PyAMG only accelerates convergence of the
resulting SPD solve, it does not change what is being solved). PyAMG is
an optional dependency (``pip install -e ".[amg]"``); importing it here
is wrapped in a ``try/except`` so the rest of the package works without
it installed, and requesting ``preconditioner="amg"`` without it raises
a clear :class:`LinearSolverError` rather than an opaque
``ImportError`` deep in a solve call.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

try:
    import pyamg
    HAS_PYAMG = True
except ImportError:  # pragma: no cover - exercised only when pyamg is absent
    pyamg = None
    HAS_PYAMG = False


class LinearSolverError(RuntimeError):
    """Raised for an invalid solver/matrix/preconditioner combination, or
    (by a caller checking :attr:`LinearSolveResult.converged`) surfaced
    as a hard failure when a solve does not converge -- never silently
    continued past."""


class SolverMethod(str, Enum):
    DIRECT = "direct"
    CG = "cg"
    BICGSTAB = "bicgstab"
    GMRES = "gmres"


class MatrixKind(str, Enum):
    """What the caller declares it knows about the matrix's mathematical
    structure -- drives which solver methods are permitted. See module
    docstring, "Matrix-property-driven solver selection"."""

    SPD = "spd"
    GENERAL = "general"


_ITERATIVE_METHODS = {SolverMethod.CG, SolverMethod.BICGSTAB, SolverMethod.GMRES}

_VALID_METHODS_FOR_KIND = {
    MatrixKind.SPD: {SolverMethod.DIRECT, SolverMethod.CG, SolverMethod.BICGSTAB, SolverMethod.GMRES},
    MatrixKind.GENERAL: {SolverMethod.DIRECT, SolverMethod.BICGSTAB, SolverMethod.GMRES},
}

_SCIPY_SOLVERS = {
    SolverMethod.CG: spla.cg,
    SolverMethod.BICGSTAB: spla.bicgstab,
    SolverMethod.GMRES: spla.gmres,
}


@dataclass
class LinearSolveResult:
    """Structured result of one :meth:`LinearSolver.solve` call."""

    x: np.ndarray
    converged: bool
    iterations: int
    initial_residual: float
    final_residual: float
    relative_residual: float
    setup_time: float
    preconditioner_time: float
    solve_time: float
    method: str
    preconditioner: Optional[str]


class LinearSolver:
    """A reusable solver for one fixed sparse matrix. See module
    docstring for the setup/solve split and matrix-kind-driven method
    validation.

    Parameters
    ----------
    matrix : any SciPy sparse matrix (converted to CSR/CSC as needed).
    method : ``"direct"``, ``"cg"``, ``"bicgstab"``, or ``"gmres"``.
    matrix_kind : ``"spd"`` or ``"general"`` -- the caller's declaration
        of the matrix's structure (see module docstring). Required for
        every method, including ``"direct"``, so the declaration is
        always available for diagnostics/reporting even when it doesn't
        gate the solver choice.
    preconditioner : ``None``, ``"jacobi"``, or ``"amg"``. Ignored (must
        be ``None``) for ``method="direct"``.
    rtol, atol, max_iterations : forwarded to the SciPy iterative solver;
        ignored for ``method="direct"``.
    """

    def __init__(
        self,
        matrix,
        *,
        method: str = "cg",
        matrix_kind: str = "spd",
        preconditioner: Optional[str] = None,
        rtol: float = 1e-10,
        atol: float = 0.0,
        max_iterations: int = 10000,
    ) -> None:
        self.method = SolverMethod(method)
        self.matrix_kind = MatrixKind(matrix_kind)
        if self.method not in _VALID_METHODS_FOR_KIND[self.matrix_kind]:
            raise LinearSolverError(
                f"method={self.method.value!r} is not valid for matrix_kind="
                f"{self.matrix_kind.value!r} -- e.g. CG requires a symmetric "
                f"positive-(semi-)definite matrix, and this matrix is only declared "
                f"{self.matrix_kind.value!r}. Valid methods for this matrix_kind: "
                f"{sorted(m.value for m in _VALID_METHODS_FOR_KIND[self.matrix_kind])}."
            )
        if preconditioner not in (None, "jacobi", "amg"):
            raise LinearSolverError(f"unknown preconditioner {preconditioner!r}; expected None, 'jacobi', or 'amg'")
        if preconditioner is not None and self.method is SolverMethod.DIRECT:
            raise LinearSolverError("a preconditioner is not applicable to method='direct'")
        if preconditioner == "amg" and not HAS_PYAMG:
            raise LinearSolverError(
                "preconditioner='amg' requires the optional 'pyamg' package "
                "(pip install -e '.[amg]'); it is not installed"
            )

        self.preconditioner_kind = preconditioner
        self.rtol = rtol
        self.atol = atol
        self.max_iterations = max_iterations
        self.matrix = matrix.tocsr()
        n = self.matrix.shape[0]
        if self.matrix.shape[0] != self.matrix.shape[1]:
            raise LinearSolverError(f"matrix must be square, got shape {self.matrix.shape}")

        t0 = time.perf_counter()
        self._lu = None
        if self.method is SolverMethod.DIRECT:
            self._lu = spla.splu(self.matrix.tocsc())
        self.setup_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        self._preconditioner_operator = None
        self._amg_hierarchy = None
        if preconditioner == "jacobi":
            diag = self.matrix.diagonal()
            if np.any(diag == 0.0):
                raise LinearSolverError("jacobi preconditioner requires a matrix with a nonzero diagonal")
            self._preconditioner_operator = sp.diags(1.0 / diag, format="csr")
        elif preconditioner == "amg":
            self._amg_hierarchy = pyamg.ruge_stuben_solver(self.matrix)
            self._preconditioner_operator = self._amg_hierarchy.aspreconditioner()
        self.preconditioner_time = time.perf_counter() - t0

        self._zeros = np.zeros(n, dtype=np.float64)

    @property
    def shape(self) -> tuple:
        return self.matrix.shape

    def solve(self, b: np.ndarray, x0: Optional[np.ndarray] = None) -> LinearSolveResult:
        """Solve ``matrix @ x = b``. ``x0`` (iterative methods only) is
        an optional initial guess -- Part D's warm start; ignored (but
        accepted) for ``method="direct"``, which needs none."""
        b = np.asarray(b, dtype=np.float64)
        x0_arr = self._zeros if x0 is None else np.asarray(x0, dtype=np.float64)
        initial_residual = float(np.linalg.norm(b - self.matrix @ x0_arr))

        t0 = time.perf_counter()
        if self.method is SolverMethod.DIRECT:
            x = self._lu.solve(b)
            iterations = 1
            converged = True
        else:
            iteration_count = [0]

            def _callback(*_args) -> None:
                iteration_count[0] += 1

            solver_fn = _SCIPY_SOLVERS[self.method]
            kwargs = dict(
                x0=(x0_arr if x0 is not None else None),
                rtol=self.rtol,
                atol=self.atol,
                maxiter=self.max_iterations,
                M=self._preconditioner_operator,
                callback=_callback,
            )
            if self.method is SolverMethod.GMRES:
                kwargs["callback_type"] = "legacy"
            x, info = solver_fn(self.matrix, b, **kwargs)
            converged = info == 0
            iterations = iteration_count[0]
        solve_time = time.perf_counter() - t0

        final_residual = float(np.linalg.norm(b - self.matrix @ x))
        b_norm = float(np.linalg.norm(b))
        relative_residual = final_residual / b_norm if b_norm > 0.0 else final_residual

        return LinearSolveResult(
            x=x,
            converged=bool(converged),
            iterations=iterations,
            initial_residual=initial_residual,
            final_residual=final_residual,
            relative_residual=relative_residual,
            setup_time=self.setup_time,
            preconditioner_time=self.preconditioner_time,
            solve_time=solve_time,
            method=self.method.value,
            preconditioner=self.preconditioner_kind,
        )


def create_linear_solver(matrix, **kwargs) -> LinearSolver:
    """Thin functional wrapper matching the review's sketched API,
    ``create_linear_solver(method=..., matrix=..., preconditioner=...,
    rtol=..., ...)``. Equivalent to ``LinearSolver(matrix, **kwargs)``."""
    return LinearSolver(matrix, **kwargs)
