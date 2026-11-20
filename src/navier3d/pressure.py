"""Sparse pressure Poisson system: matrix assembly, null-space handling, solvers.

Solves the discrete Poisson equation ``L_h p = rhs`` (the same ``L_h`` as
:func:`navier3d.operators.scalar_laplacian`, but assembled once as an
explicit sparse matrix rather than applied matrix-free) for a **fixed**
mesh and pressure boundary-condition set. Matrix assembly is separated
from solving: construct one :class:`PressurePoissonSystem` per
(mesh, BC) pair and call :meth:`PressurePoissonSystem.solve` as many
times as needed (e.g. once per time step in the future projection loop)
without re-assembling.

Sign convention
----------------
Following the accepted convention for this milestone::

    A = -L_h,          A p = -b

``A`` is symmetric and **positive (semi-)definite** -- suitable for CG --
because ``L_h`` (and its constrained/eliminated variants below) is
negative (semi-)definite. Concretely, :meth:`PressurePoissonSystem.solve`
takes the *physical* right-hand side ``b`` (e.g. ``rho/dt * div(u*)`` in
the future projection step, matching ``L_h p = b``) and internally solves
``A p = -b`` for the homogeneous-BC case. See "Boundary elimination and
the correction vector" below for how this generalizes to inhomogeneous
Dirichlet/Neumann faces.

Matrix construction: separability
-----------------------------------
``L_h`` is separable: ``L_h = Lx (x) Iy (x) Iz + Ix (x) Ly (x) Iz + Ix (x) Iy (x) Lz``
(Kronecker sums), where ``Lx``, ``Ly``, ``Lz`` are the 1-D second-difference
operators along each axis, each independently modified for that axis's own
pair of boundary conditions. This is assembled directly with
``scipy.sparse.kron`` rather than looping over 3-D cells by hand -- both
more efficient and, because each 1-D operator is built and tested in
isolation, easier to verify. The flattening convention is C-order
(``numpy``'s default): flat index ``i*ny*nz + j*nz + k`` for cell
``(i, j, k)``.

Boundary elimination and the correction vector
-------------------------------------------------
A boundary-adjacent cell's stencil references a ghost value that is not
an independent unknown -- exactly the same ghost values
:func:`navier3d.boundary_conditions.apply_pressure_bc` would fill.
Substituting the same ghost formulas here (Neumann: ``ghost = interior +
d*g``; Dirichlet: ``ghost = 2*value - interior``; periodic: wrap) either
changes that row's diagonal coefficient (Neumann: -1/d^2 instead of
-2/d^2 for that axis's term; Dirichlet: -3/d^2) or, for the *inhomogeneous*
part, produces a constant term that does not multiply any unknown. That
constant is accumulated into a length-``N`` **correction vector** ``c``
(zero for periodic and *homogeneous* Neumann/Dirichlet faces) such that::

    L_h_full(p) = (L_h_matrix @ p) + c        for any p consistent with the BCs

so solving ``L_h p = b`` for the unknowns means ``L_h_matrix @ p = b - c``,
i.e. (sign convention above) ``A p = -(b - c) = c - b``.

Null space
----------
The assembled matrix has a 1-D null space (constant vectors) if and only
if **no** face uses a Dirichlet pressure BC (any mix of periodic and
homogeneous/inhomogeneous Neumann faces has this property; a single
Dirichlet face makes the matrix nonsingular). Two strategies are
supported for the singular case:

* ``"zero_mean"``: solve the singular-but-consistent system directly with
  CG (well-defined for a compatible symmetric PSD system), then subtract
  the mean from the solution so the returned pressure has zero mean by
  convention. Requires RHS compatibility (see below); **not** usable with
  ``solver="direct"`` (a direct sparse LU factorization of a singular
  matrix is unreliable) -- :class:`PressureSystemError` is raised at
  construction if that combination is requested.
* ``"pin_cell"``: eliminate one cell's pressure value (fixed to
  ``pinned_value``, default 0.0) from the system entirely, symmetrically
  (both its row *and* column), yielding a genuinely nonsingular SPD
  matrix usable with either solver. The resulting pressure differs from
  the ``zero_mean`` solution only by an additive constant (both are valid
  representatives of the same equivalence class); see
  ``tests/test_pressure.py::test_zero_mean_and_pin_cell_gradients_agree``.

RHS compatibility
------------------
For a singular (null-space-having) system, the discrete Fredholm
alternative requires ``sum_i b_i * dV_i ~= 0`` for a solution to exist
(the continuous analogue: ``integral(rhs) dV = closed-surface flux = 0``
for an all-Neumann/periodic problem). ``rhs_compatibility="strict"``
raises :class:`PressureSystemError` if this is violated beyond ``tol``;
``"mean_removal"`` instead silently subtracts the mean from ``b`` before
solving. Either way, the (pre-correction) compatibility error is recorded
in :class:`SolveDiagnostics`.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np
import scipy.sparse as sp

from .boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    apply_pressure_bc,
    apply_velocity_bc,
)
from .fields import ScalarField, VelocityField
from .linear_solvers import LinearSolver, LinearSolverError
from .mesh import StructuredMesh3D

_FACE_NAMES = ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max")


class PressureSystemError(ValueError):
    """Raised for invalid pressure-system configuration or an incompatible RHS."""


class NullSpaceStrategy(str, Enum):
    ZERO_MEAN = "zero_mean"
    PIN_CELL = "pin_cell"


class LinearSolverKind(str, Enum):
    DIRECT = "direct"
    CG = "cg"
    BICGSTAB = "bicgstab"
    GMRES = "gmres"


class RHSCompatibilityMode(str, Enum):
    STRICT = "strict"
    MEAN_REMOVAL = "mean_removal"


@dataclass
class SolveDiagnostics:
    """Structured record of one :meth:`PressurePoissonSystem.solve` call."""

    converged: bool
    method: str
    iterations: int
    initial_residual: float
    final_residual: float
    compatibility_error: float
    assembly_time: float
    solve_time: float
    null_space_strategy: Optional[str] = None
    relative_residual: float = 0.0
    preconditioner_time: float = 0.0
    rhs_time: float = 0.0


# --------------------------------------------------------------------------
# Per-axis 1-D operator assembly
# --------------------------------------------------------------------------

def _axis_matrix(n: int, d: float, lo_bc, hi_bc) -> sp.csr_matrix:
    """1-D contribution of one axis to ``L_h`` (not yet negated) for ``n``
    cells. Depends only on each face's BC *category* (periodic / neumann /
    dirichlet), never on the specific (scalar or spatially-varying) value
    -- that lives entirely in the correction array (:func:`_assemble_laplacian`)."""
    inv_d2 = 1.0 / (d * d)
    periodic = lo_bc.pressure_type is PressureBCType.PERIODIC
    rows, cols, vals = [], [], []
    for i in range(n):
        diag = -2.0 * inv_d2
        if i > 0:
            rows.append(i); cols.append(i - 1); vals.append(inv_d2)
        elif periodic:
            rows.append(i); cols.append(n - 1); vals.append(inv_d2)
        elif lo_bc.pressure_type is PressureBCType.NEUMANN:
            diag += inv_d2
        else:  # DIRICHLET
            diag -= inv_d2

        if i < n - 1:
            rows.append(i); cols.append(i + 1); vals.append(inv_d2)
        elif periodic:
            rows.append(i); cols.append(0); vals.append(inv_d2)
        elif hi_bc.pressure_type is PressureBCType.NEUMANN:
            diag += inv_d2
        else:
            diag -= inv_d2

        rows.append(i); cols.append(i); vals.append(diag)
    return sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()


def _has_null_space(bcs: BoundaryConditionSet) -> bool:
    return not any(bcs[name].pressure_type is PressureBCType.DIRICHLET for name in _FACE_NAMES)


def _tangential_shapes(mesh: StructuredMesh3D, axis: int) -> tuple:
    """``(full_padded_shape, interior_shape)`` of the two tangential axes
    for a face normal to ``axis`` -- the two shapes a per-face BC array is
    allowed to arrive in (see :class:`~navier3d.boundary_conditions.FaceBoundaryCondition`)."""
    ng = mesh.n_ghost
    sizes = (mesh.nx, mesh.ny, mesh.nz)
    tangential = [a for a in range(3) if a != axis]
    full = tuple(sizes[a] + 2 * ng for a in tangential)
    interior = tuple(sizes[a] for a in tangential)
    return full, interior


def _as_interior_tangential(value, mesh: StructuredMesh3D, axis: int, name: str):
    """Coerce a per-face BC value (scalar, full-ghost-padded array, or
    already-interior array) to the interior-only tangential shape the
    correction array needs."""
    if np.isscalar(value):
        return value
    arr = np.asarray(value, dtype=np.float64)
    full_shape, interior_shape = _tangential_shapes(mesh, axis)
    if arr.shape == interior_shape:
        return arr
    if arr.shape == full_shape:
        ng = mesh.n_ghost
        return arr[ng:-ng, ng:-ng] if ng > 0 else arr
    raise PressureSystemError(
        f"{name}: BC array shape {arr.shape} matches neither the interior tangential "
        f"shape {interior_shape} nor the full ghost-padded shape {full_shape}"
    )


def _topology_key(bcs: BoundaryConditionSet) -> tuple:
    """Fingerprint of the per-face pressure-BC *category* (periodic /
    neumann / dirichlet) that the assembled matrix's structure depends on
    -- never the specific (possibly time-varying) value. Two
    :class:`~navier3d.boundary_conditions.BoundaryConditionSet` instances
    with the same topology key are guaranteed to produce an identically
    *structured* matrix from :func:`_assemble_matrix` (values may differ)."""
    return tuple(bcs[name].pressure_type for name in _FACE_NAMES)


def _assemble_matrix(mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> sp.csr_matrix:
    """Assemble the full 3-D ``L_h`` sparse matrix (CSR, N=nx*ny*nz).
    Depends only on each face's BC *category*, never on the specific BC
    value -- see :func:`_assemble_correction` for the value-dependent part."""
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    axes = [
        (nx, mesh.dx, bcs.x_min, bcs.x_max),
        (ny, mesh.dy, bcs.y_min, bcs.y_max),
        (nz, mesh.dz, bcs.z_min, bcs.z_max),
    ]
    mats = [_axis_matrix(n, d, lo, hi) for n, d, lo, hi in axes]
    Ix, Iy, Iz = sp.identity(nx, format="csr"), sp.identity(ny, format="csr"), sp.identity(nz, format="csr")
    return (
        sp.kron(mats[0], sp.kron(Iy, Iz))
        + sp.kron(Ix, sp.kron(mats[1], Iz))
        + sp.kron(Ix, sp.kron(Iy, mats[2]))
    ).tocsr()


def _assemble_correction(mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> np.ndarray:
    """Assemble the correction array (shape (nx,ny,nz), C-order flattened
    on return) for the given mesh/BCs. Built as a genuine 3-D array (not
    three separable 1-D vectors outer-summed) so that spatially-varying
    (per-cell) Dirichlet/Neumann face data -- needed by Milestone 4's
    projection, which derives ``dp/dn`` from a generally non-uniform
    predictor velocity -- is handled correctly; a uniform (scalar) value
    reduces to exactly the Milestone 3 behavior. Depends on BC *values*
    (and, through them, may change every call in a time-stepping loop);
    see :func:`_assemble_matrix` for the value-independent part.
    """
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    axes = [
        (nx, mesh.dx, bcs.x_min, bcs.x_max),
        (ny, mesh.dy, bcs.y_min, bcs.y_max),
        (nz, mesh.dz, bcs.z_min, bcs.z_max),
    ]
    correction = np.zeros((nx, ny, nz), dtype=np.float64)
    for axis, (n, d, lo_bc, hi_bc) in enumerate(axes):
        if lo_bc.pressure_type is PressureBCType.PERIODIC:
            continue
        lo_idx = [slice(None)] * 3
        lo_idx[axis] = 0
        hi_idx = [slice(None)] * 3
        hi_idx[axis] = n - 1

        if lo_bc.pressure_type is PressureBCType.NEUMANN:
            g = _as_interior_tangential(lo_bc.pressure_gradient, mesh, axis, "lo face")
            correction[tuple(lo_idx)] += g / d
        else:
            v = _as_interior_tangential(lo_bc.pressure_value, mesh, axis, "lo face")
            correction[tuple(lo_idx)] += 2.0 * v / (d * d)

        if hi_bc.pressure_type is PressureBCType.NEUMANN:
            g = _as_interior_tangential(hi_bc.pressure_gradient, mesh, axis, "hi face")
            correction[tuple(hi_idx)] += g / d
        else:
            v = _as_interior_tangential(hi_bc.pressure_value, mesh, axis, "hi face")
            correction[tuple(hi_idx)] += 2.0 * v / (d * d)

    return correction.ravel(order="C")


def _assemble_laplacian(mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> tuple:
    """Convenience wrapper: ``(matrix, correction)`` in one call. See
    :func:`_assemble_matrix` / :func:`_assemble_correction`."""
    return _assemble_matrix(mesh, bcs), _assemble_correction(mesh, bcs)


def _pin_laplacian(L_h: sp.csr_matrix, pin_flat_index: int) -> tuple:
    """Eliminate ``pin_flat_index`` from ``L_h`` symmetrically (row *and*
    column), returning the modified matrix and a length-N vector
    ``pin_offdiag`` such that, for a pin fixed to ``pinned_value``, the
    additional known contribution to move to the RHS at row ``i`` is
    ``pin_offdiag[i] * pinned_value`` (zero at ``i == pin_flat_index``,
    where the row becomes the trivial identity constraint instead)."""
    L = L_h.tolil(copy=True)
    n = L.shape[0]
    col = np.asarray(L[:, pin_flat_index].todense()).ravel()
    pin_offdiag = col.copy()
    pin_offdiag[pin_flat_index] = 0.0
    L[:, pin_flat_index] = 0.0
    L[pin_flat_index, :] = 0.0
    L[pin_flat_index, pin_flat_index] = 1.0
    return L.tocsr(), pin_offdiag


class PressurePoissonSystem:
    """A pressure Poisson system for a fixed mesh and pressure BC set.

    The matrix (and, for ``solver="direct"``, its LU factorization) is
    assembled once at construction and reused by every :meth:`solve`
    call. The mesh is immutable for the lifetime of an instance.

    BCs may be updated via :meth:`update_bcs`, but **only** the per-face
    *value* (e.g. a time-varying inhomogeneous Neumann ``dp/dn`` derived
    from a new predictor velocity each time step -- exactly Milestone 4's
    ``project()`` use case) -- never the per-face *category*
    (periodic/neumann/dirichlet), which the matrix's structure depends on.
    :meth:`update_bcs` raises if the category (topology) would change;
    construct a new :class:`PressurePoissonSystem` for that. This keeps
    "the matrix was assembled for this BC topology" always true by
    construction, while still letting a time-stepping loop reuse the same
    matrix/factorization object across many solves with different
    inhomogeneous values -- see
    ``tests/test_pressure.py::test_update_bcs_reuses_matrix_object``.
    """

    def __init__(
        self,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet,
        *,
        solver: str = "cg",
        preconditioner: Optional[str] = None,
        null_space_strategy: str = "zero_mean",
        rhs_compatibility: str = "strict",
        tol: float = 1e-10,
        max_iterations: int = 10000,
        pin_index: tuple = (0, 0, 0),
        pinned_value: float = 0.0,
    ) -> None:
        self._mesh = mesh
        self._bcs = bcs
        self.solver = LinearSolverKind(solver)
        self.preconditioner = preconditioner
        self.null_space_strategy = NullSpaceStrategy(null_space_strategy)
        self.rhs_compatibility = RHSCompatibilityMode(rhs_compatibility)
        self.tol = tol
        self.max_iterations = max_iterations
        self.pinned_value = pinned_value

        if preconditioner not in (None, "jacobi", "amg"):
            raise PressureSystemError(f"unknown preconditioner {preconditioner!r}; expected None, 'jacobi', or 'amg'")

        i, j, k = pin_index
        if not (0 <= i < mesh.nx and 0 <= j < mesh.ny and 0 <= k < mesh.nz):
            raise PressureSystemError(f"pin_index {pin_index} is outside the mesh (nx={mesh.nx}, ny={mesh.ny}, nz={mesh.nz})")
        self._pin_flat_index = (i * mesh.ny + j) * mesh.nz + k

        self._has_null_space = _has_null_space(bcs)
        self._topology_key = _topology_key(bcs)

        if (
            self._has_null_space
            and self.null_space_strategy is NullSpaceStrategy.ZERO_MEAN
            and self.solver is LinearSolverKind.DIRECT
        ):
            raise PressureSystemError(
                "solver='direct' is incompatible with null_space_strategy='zero_mean' on a "
                "singular (periodic/all-Neumann) system: a direct sparse LU factorization of a "
                "singular matrix is unreliable. Use null_space_strategy='pin_cell' for a direct "
                "solve, or solver='cg' with 'zero_mean'."
            )

        t0 = time.perf_counter()
        L_h, correction = _assemble_laplacian(mesh, bcs)
        self._pin_offdiag = None
        if self._has_null_space and self.null_space_strategy is NullSpaceStrategy.PIN_CELL:
            L_h, self._pin_offdiag = _pin_laplacian(L_h, self._pin_flat_index)

        self._L_h = L_h
        self._correction = correction
        self._A = (-L_h).tocsr()  # A = -L_h, positive (semi-)definite
        self.assembly_time = time.perf_counter() - t0

        # A is always SPD (Milestone 3 sign convention, "Sign convention"
        # above; pin_cell elimination or a consistent singular system are
        # both still SPD/PSD) -- so every LinearSolverKind is valid here
        # (Milestone 7 Part A: the *caller* declares matrix_kind honestly;
        # pressure.py's matrix genuinely is SPD, unlike diffusion.py's
        # original pin-row formulation, see diffusion.py's own comment).
        try:
            self._linear_solver = LinearSolver(
                self._A,
                method=self.solver.value,
                matrix_kind="spd",
                preconditioner=preconditioner,
                rtol=self.tol,
                atol=0.0,
                max_iterations=self.max_iterations,
            )
        except LinearSolverError as exc:
            raise PressureSystemError(str(exc)) from exc
        self._lu = self._linear_solver._lu  # exposed for reuse-identity tests; see LinearSolver

    def update_bcs(self, bcs: BoundaryConditionSet) -> None:
        """Update BC *values* in place, reusing the cached matrix (and, for
        ``solver="direct"``, its LU factorization) unchanged -- only the
        correction array is recomputed. ``bcs`` must have the same per-face
        pressure-BC *category* (:func:`_topology_key`) as this system was
        constructed with; otherwise raises :class:`PressureSystemError`
        (construct a new :class:`PressurePoissonSystem` for a topology
        change -- that does require a new matrix).
        """
        new_key = _topology_key(bcs)
        if new_key != self._topology_key:
            raise PressureSystemError(
                "update_bcs: the per-face pressure BC category differs from the "
                "topology this system was assembled for; construct a new "
                "PressurePoissonSystem instead (only BC *values*, not categories, "
                "can be updated in place)"
            )
        self._bcs = bcs
        self._correction = _assemble_correction(self._mesh, bcs)

    # -- read-only access -------------------------------------------------

    @property
    def mesh(self) -> StructuredMesh3D:
        return self._mesh

    @property
    def bcs(self) -> BoundaryConditionSet:
        return self._bcs

    @property
    def matrix(self) -> sp.csr_matrix:
        """The assembled ``A = -L_h`` matrix (CSR), post null-space handling."""
        return self._A

    @property
    def laplacian_matrix(self) -> sp.csr_matrix:
        """The assembled ``L_h`` matrix (CSR, i.e. ``-A``), post null-space handling."""
        return self._L_h

    @property
    def has_null_space(self) -> bool:
        return self._has_null_space

    @property
    def shape(self) -> tuple:
        return self._A.shape

    # -- solving ------------------------------------------------------------

    def solve(self, rhs: ScalarField, x0: Optional[ScalarField] = None) -> tuple:
        """Solve ``L_h p = rhs`` (equivalently ``A p = -rhs`` up to the
        boundary correction and null-space handling described in the
        module docstring). Returns ``(pressure: ScalarField, diagnostics:
        SolveDiagnostics)``.
        """
        if rhs.n_ghost != self._mesh.n_ghost:
            raise PressureSystemError(
                f"rhs field n_ghost={rhs.n_ghost} does not match this system's mesh.n_ghost="
                f"{self._mesh.n_ghost}"
            )
        expected_shape = (
            self._mesh.nx + 2 * rhs.n_ghost,
            self._mesh.ny + 2 * rhs.n_ghost,
            self._mesh.nz + 2 * rhs.n_ghost,
        )
        if rhs.data.shape != expected_shape:
            raise PressureSystemError(
                f"rhs field shape {rhs.data.shape} is incompatible with this system's mesh "
                f"(nx={self._mesh.nx}, ny={self._mesh.ny}, nz={self._mesh.nz}); expected {expected_shape}"
            )

        t_rhs0 = time.perf_counter()
        b = rhs.interior.astype(np.float64).ravel(order="C").copy()
        dV = self._mesh.cell_volume
        compatibility_error = float(np.sum(b) * dV) if self._has_null_space else 0.0

        if self._has_null_space and self.null_space_strategy is NullSpaceStrategy.ZERO_MEAN:
            if self.rhs_compatibility is RHSCompatibilityMode.STRICT:
                if abs(compatibility_error) > self.tol * max(1.0, float(np.sum(np.abs(b)) * dV)):
                    raise PressureSystemError(
                        f"RHS is not compatible with a singular (periodic/all-Neumann) system: "
                        f"sum(b)*dV = {compatibility_error:.6e}, expected ~0 "
                        f"(rhs_compatibility='strict'; use 'mean_removal' to auto-correct)"
                    )
            else:
                b = b - np.mean(b)

        rhs_eff = b - self._correction
        if self._pin_offdiag is not None:
            rhs_eff = rhs_eff - self._pin_offdiag * self.pinned_value
            rhs_eff[self._pin_flat_index] = self.pinned_value

        b_internal = -rhs_eff  # A p = -rhs_eff

        x0_vec = None
        if x0 is not None:
            x0_vec = x0.interior.astype(np.float64).ravel(order="C").copy()
        rhs_time = time.perf_counter() - t_rhs0

        result_ls = self._linear_solver.solve(b_internal, x0=x0_vec)
        p_vec = result_ls.x
        converged = result_ls.converged
        iterations = result_ls.iterations
        initial_residual = result_ls.initial_residual
        final_residual = result_ls.final_residual
        solve_time = result_ls.solve_time

        if self._has_null_space and self.null_space_strategy is NullSpaceStrategy.ZERO_MEAN:
            p_vec = p_vec - np.mean(p_vec)

        result = ScalarField.zeros(self._mesh)
        result.interior = p_vec.reshape(self._mesh.nx, self._mesh.ny, self._mesh.nz, order="C")

        diagnostics = SolveDiagnostics(
            converged=converged,
            method=self.solver.value,
            iterations=iterations,
            initial_residual=initial_residual,
            final_residual=final_residual,
            compatibility_error=compatibility_error,
            assembly_time=self.assembly_time,
            solve_time=solve_time,
            null_space_strategy=self.null_space_strategy.value if self._has_null_space else None,
            relative_residual=result_ls.relative_residual,
            preconditioner_time=result_ls.preconditioner_time,
            rhs_time=rhs_time,
        )
        return result, diagnostics


def compute_initial_pressure(
    velocity: VelocityField,
    bcs: BoundaryConditionSet,
    mesh: StructuredMesh3D,
    rho: float,
    nu: float,
    *,
    convection_scheme: Optional[str] = None,
    forcing_field: Optional[VelocityField] = None,
    boundary_acceleration: Optional[VelocityField] = None,
    pressure_system: Optional[PressurePoissonSystem] = None,
    **pressure_kwargs,
) -> tuple[ScalarField, PressurePoissonSystem]:
    """Compute the mathematically consistent initial pressure :math:`p^0` for
    an initial velocity field :math:`u^0` under the incompressible
    Navier-Stokes (or Stokes) equations.

    Solves the discrete initial Pressure Poisson Equation (PPE)::

        L_h p^0 = rho * D_h(a^0)

    where the initial acceleration field :math:`a^0` evaluated at MAC face
    locations is::

        a^0 = f^0 + nu*L_{u,h}(u^0) - N(u^0) - du_boundary/dt

    with boundary conditions derived from the normal momentum equation
    at :math:`t=0`::

        dp/dn = rho * (n . a^0)

    on physical Neumann faces (walls, inlets, symmetry/free-slip).
    Periodic faces and Dirichlet pressure faces (outlets) retain their
    standard boundary conditions.

    Parameters
    ----------
    velocity : VelocityField
        The initial velocity field :math:`u^0` (should be discretely
        divergence-free; see :func:`navier3d.projection.project_initial_velocity`
        to project raw initial data).
    bcs : BoundaryConditionSet
        The boundary condition set for the domain.
    mesh : StructuredMesh3D
        The Cartesian structured mesh.
    rho : float
        Fluid density (> 0).
    nu : float
        Kinematic viscosity (> 0).
    convection_scheme : Optional[str]
        ``None`` (Stokes flow), ``"centered"``, or ``"upwind"`` for Navier-Stokes.
    forcing_field : Optional[VelocityField]
        Body force at :math:`t=0`, matching mesh component shapes.
    boundary_acceleration : Optional[VelocityField]
        Time derivative of prescribed boundary velocity at :math:`t=0` (0 for
        stationary or steady boundary conditions).
    pressure_system : Optional[PressurePoissonSystem]
        Existing pressure system to reuse (via ``update_bcs``) if available.
    **pressure_kwargs :
        Forwarded to :class:`PressurePoissonSystem` constructor if
        ``pressure_system`` is ``None`` (e.g. ``solver="direct"``,
        ``null_space_strategy="pin_cell"``).

    Returns
    -------
    p0 : ScalarField
        The consistent initial pressure field with ghosts filled according
        to ``p0_bcs``.
    system : PressurePoissonSystem
        The :class:`PressurePoissonSystem` used for the solve (for caching/reuse).
    """
    from . import operators
    from .convection import centered_convection, upwind_convection

    _convection_map = {"centered": centered_convection, "upwind": upwind_convection}
    if convection_scheme is not None and convection_scheme not in _convection_map:
        raise ValueError(f"convection_scheme must be None, 'centered', or 'upwind', got {convection_scheme!r}")
    if rho <= 0:
        raise ValueError(f"rho must be positive, got {rho!r}")
    if nu <= 0:
        raise ValueError(f"nu must be positive, got {nu!r}")

    apply_velocity_bc(velocity, bcs)

    a0 = VelocityField.zeros(mesh)
    lap_u = operators.velocity_laplacian(velocity, mesh)

    N0 = None
    if convection_scheme is not None:
        N0 = _convection_map[convection_scheme](velocity, mesh)

    for axis, comp_a in enumerate(a0.components()):
        comp_a.interior = nu * lap_u.components()[axis].interior
        if forcing_field is not None:
            comp_a.interior += forcing_field.components()[axis].interior
        if N0 is not None:
            comp_a.interior -= N0.components()[axis].interior
        if boundary_acceleration is not None:
            comp_a.interior -= boundary_acceleration.components()[axis].interior

    apply_velocity_bc(a0, bcs)

    updated_bcs = {}
    axis_faces = {0: ("x_min", "x_max"), 1: ("y_min", "y_max"), 2: ("z_min", "z_max")}
    for axis in range(3):
        lo_name, hi_name = axis_faces[axis]
        lo_bc = bcs[lo_name]
        hi_bc = bcs[hi_name]

        if lo_bc.pressure_type is PressureBCType.NEUMANN:
            g_lo = -rho * a0.components()[axis].boundary_layer("lo")
            updated_bcs[lo_name] = FaceBoundaryCondition(
                velocity_type=lo_bc.velocity_type,
                pressure_type=PressureBCType.NEUMANN,
                velocity_value=lo_bc.velocity_value,
                pressure_gradient_value=g_lo,
            )
        else:
            updated_bcs[lo_name] = lo_bc

        if hi_bc.pressure_type is PressureBCType.NEUMANN:
            g_hi = rho * a0.components()[axis].boundary_layer("hi")
            updated_bcs[hi_name] = FaceBoundaryCondition(
                velocity_type=hi_bc.velocity_type,
                pressure_type=PressureBCType.NEUMANN,
                velocity_value=hi_bc.velocity_value,
                pressure_gradient_value=g_hi,
            )
        else:
            updated_bcs[hi_name] = hi_bc

    p0_bcs = BoundaryConditionSet(**updated_bcs)

    div_a0 = operators.divergence(a0, mesh)
    rhs = ScalarField.zeros(mesh)
    rhs.interior = rho * div_a0.interior

    if pressure_system is not None:
        pressure_system.update_bcs(p0_bcs)
        system = pressure_system
    else:
        system = PressurePoissonSystem(
            mesh,
            p0_bcs,
            **pressure_kwargs,
        )

    p0, diag = system.solve(rhs)
    if not diag.converged:
        raise PressureSystemError(f"initial pressure solve did not converge: {diag}")
    apply_pressure_bc(p0, p0_bcs, spacing=mesh.spacing)
    return p0, system
