"""Reusable implicit velocity-diffusion systems (theta-scheme).

Solves, for **one** velocity component at a time (MAC components live on
different-shaped grids, so each gets its own linear system):

```
(I - theta*nu*dt*L_h) u* = (I + (1-theta)*nu*dt*L_h) u^n + dt*nu*correction + dt*f
```

``theta=1`` is backward/implicit Euler (first-order); ``theta=0.5`` is
Crank-Nicolson (second-order) -- matching Milestone 5's required formula
exactly, with ``f`` evaluated at whatever time level the caller supplies
(e.g. the midpoint ``t^{n+1/2}`` for Crank-Nicolson). ``L_h`` here is the
same discrete Laplacian as :func:`navier3d.operators.velocity_laplacian`,
now assembled as an explicit sparse matrix (analogous to how
``pressure.py`` relates to ``operators.scalar_laplacian``).

Why this needs its own matrix assembly (not `pressure.py`'s)
-----------------------------------------------------------------
A velocity component's own face-normal axis has a fundamentally
different structure from a cell-centered scalar's axes: the boundary
*faces* are real MAC unknowns (not ghosts), always equal to a BC-
determined value for all time (0 for a no-slip/free-slip/symmetry wall,
a configured constant for `velocity_inlet`, a zero-gradient linkage to
the adjacent interior for `pressure_outlet`) -- never something the
diffusion PDE itself evolves. So along a component's own normal axis,
boundary *rows* of the linear system are algebraic constraints (an
identity "pin" to a fixed target, or a linkage between two unknowns),
not differential-equation rows; along its two tangential axes, the
boundary treatment is instead a ghost-elimination exactly analogous to
`pressure.py`'s Dirichlet/Neumann handling (`no_slip`/`velocity_inlet`
~ Dirichlet with value = the wall speed; `free_slip`/`symmetry` ~
homogeneous Neumann; `periodic` ~ wrap).

Because velocity BC *values* (unlike pressure's projection-derived
Neumann data) don't change during a simulation -- a no-slip target is
always 0, a `velocity_inlet` target is a fixed configured constant --
there is no `update_bcs`-style API here: once `mesh`, `bcs`, `nu`, `dt`,
`theta` are fixed, the matrix and its LU factorization are built exactly
once and reused for every `solve()` call for the life of the object
(Milestone 5's "reusable velocity-diffusion matrices/factorizations" and
"no matrix rebuild per timestep" requirements).

Well-posedness and solver choice
------------------------------------
Unlike the pure pressure Poisson matrix, ``M = I - theta*nu*dt*L_h`` is
**never singular** for ``theta, nu, dt > 0``: even if ``L_h`` itself has
a null space (e.g. a fully periodic/free-slip component, where a
constant field has zero Laplacian, mirroring `pressure.py`'s
all-Neumann/periodic case), the added identity term means
``M @ ones = ones - theta*nu*dt*0 = ones != 0``. So no null-space
handling, RHS compatibility checking, or `zero_mean`/`pin_cell` strategy
is needed here at all. Boundary-row overrides (pins/linkages) do,
however, break matrix symmetry (the same trade-off `pressure.py`'s
`pin_cell` strategy makes) -- so the default (`formulation="pinned"`)
assembly below offers only **direct** or general-matrix iterative
solves (`solver="direct"`/`"bicgstab"`/`"gmres"`, via
`linear_solvers.py`); CG is rejected for it (would be unreliable
without symmetric positive-definiteness).

**Milestone 7 Part C** adds an alternative, opt-in
(`formulation="spd"`) assembly that algebraically *eliminates* the
boundary/duplicate normal-axis degrees of freedom instead of pinning
them -- yielding a genuinely symmetric positive-definite matrix (on a
correspondingly smaller index space) for which `solver="cg"` **is**
valid and is that formulation's default. See the module-level comment
above `_assemble_velocity_diffusion_system_spd` for the full derivation
and `VelocityDiffusionSystem`'s docstring for the two formulations'
public-interface differences (there are none -- `solve()` always takes
and returns a full-shaped `FaceField` regardless of which internal
representation is in use).
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import scipy.sparse as sp

from .boundary_conditions import BoundaryConditionSet, VelocityBCType
from .fields import FaceField
from .linear_solvers import LinearSolver, LinearSolverError
from .mesh import StructuredMesh3D

_AXIS_FACES = {0: ("x_min", "x_max"), 1: ("y_min", "y_max"), 2: ("z_min", "z_max")}


class DiffusionSystemError(ValueError):
    """Raised for invalid velocity-diffusion system configuration."""


@dataclass
class DiffusionDiagnostics:
    """Structured record of one :meth:`VelocityDiffusionSystem.solve` call."""

    converged: bool
    method: str
    iterations: int
    residual: float
    finite: bool
    assembly_time: float
    solve_time: float
    relative_residual: float = 0.0
    preconditioner_time: float = 0.0
    rhs_time: float = 0.0


def _is_dirichlet_like(bc) -> bool:
    return bc.velocity_type in (VelocityBCType.NO_SLIP, VelocityBCType.VELOCITY_INLET)


def _tangential_matrix(n: int, d: float, lo_bc, hi_bc) -> sp.csr_matrix:
    """1-D matrix contribution for a tangential axis (cell-like, ``n``
    cells): `no_slip`/`velocity_inlet` ~ Dirichlet (diag -1/d^2 extra);
    `free_slip`/`symmetry` ~ homogeneous Neumann (diag +1/d^2 extra);
    `periodic` ~ wrap. Structurally identical to ``pressure.py``'s
    `_axis_matrix`, written separately here because the BC objects carry
    ``velocity_type`` rather than ``pressure_type``."""
    inv_d2 = 1.0 / (d * d)
    periodic = lo_bc.velocity_type is VelocityBCType.PERIODIC
    rows, cols, vals = [], [], []
    for i in range(n):
        diag = -2.0 * inv_d2
        if i > 0:
            rows.append(i); cols.append(i - 1); vals.append(inv_d2)
        elif periodic:
            rows.append(i); cols.append(n - 1); vals.append(inv_d2)
        elif _is_dirichlet_like(lo_bc):
            diag -= inv_d2
        else:
            diag += inv_d2

        if i < n - 1:
            rows.append(i); cols.append(i + 1); vals.append(inv_d2)
        elif periodic:
            rows.append(i); cols.append(0); vals.append(inv_d2)
        elif _is_dirichlet_like(hi_bc):
            diag -= inv_d2
        else:
            diag += inv_d2

        rows.append(i); cols.append(i); vals.append(diag)
    return sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()


def _tangential_correction(n: int, d: float, lo_bc, hi_bc, component_axis: int) -> np.ndarray:
    """Additive correction so this axis's tangential contribution to
    ``L_h(u)`` equals ``(matrix @ u) + correction``; zero for periodic and
    for `free_slip`/`symmetry` (homogeneous Neumann)."""
    c = np.zeros(n, dtype=np.float64)
    if lo_bc.velocity_type is VelocityBCType.PERIODIC:
        return c
    inv_d2 = 1.0 / (d * d)

    def target(bc):
        if bc.velocity_type is VelocityBCType.VELOCITY_INLET:
            return bc.velocity_value[component_axis]
        return 0.0

    if _is_dirichlet_like(lo_bc):
        c[0] += 2.0 * target(lo_bc) * inv_d2
    if _is_dirichlet_like(hi_bc):
        c[-1] += 2.0 * target(hi_bc) * inv_d2
    return c


def _normal_matrix_interior_rows(n_cells: int, d: float, lo_bc) -> sp.csr_matrix:
    """Matrix contribution for the component's own face-normal axis
    (``n_cells+1`` points), covering only the genuine diffusion-equation
    rows: interior rows ``1..n_cells-1`` (non-periodic) or all rows
    ``0..n_cells-1`` with wrap-skip-duplicate neighbors (periodic). The
    boundary row(s) -- ``0``/``n_cells`` non-periodic, or ``n_cells``
    (the periodic duplicate) -- get **zero** contribution here; the
    caller overrides them with an algebraic pin/linkage row instead (see
    module docstring)."""
    n = n_cells + 1
    inv_d2 = 1.0 / (d * d)
    periodic = lo_bc.velocity_type is VelocityBCType.PERIODIC
    rows, cols, vals = [], [], []
    if periodic:
        for i in range(n_cells):
            left = n_cells - 1 if i == 0 else i - 1
            right = 0 if i == n_cells - 1 else i + 1
            rows += [i, i, i]; cols += [left, i, right]; vals += [inv_d2, -2.0 * inv_d2, inv_d2]
    else:
        for i in range(1, n_cells):
            rows += [i, i, i]; cols += [i - 1, i, i + 1]; vals += [inv_d2, -2.0 * inv_d2, inv_d2]
    return sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()


def _assemble_velocity_diffusion_system(mesh: StructuredMesh3D, bcs: BoundaryConditionSet, component_axis: int, nu: float, dt: float, theta: float) -> tuple:
    """Returns ``(L_h, M, free_row_mask, boundary_rhs, correction)``:
    ``L_h`` the raw (matrix-only) velocity Laplacian contribution for
    this component (needed by ``solve()`` to form the explicit part of
    the RHS from ``u^n``); ``M`` the full ``(I - theta*nu*dt*L_h)``
    system with boundary rows overridden by pin/linkage constraints;
    ``free_row_mask`` (bool, True = genuine PDE row); ``boundary_rhs``
    (the fixed RHS value at non-free rows, meaningless elsewhere);
    ``correction`` the tangential-axis boundary correction (flattened,
    matches ``L_h_full(u) = L_h @ u + correction`` on tangential axes).
    """
    n_cells = (mesh.nx, mesh.ny, mesh.nz)
    spacing = (mesh.dx, mesh.dy, mesh.dz)
    faces = [(bcs.x_min, bcs.x_max), (bcs.y_min, bcs.y_max), (bcs.z_min, bcs.z_max)]

    shape = list(n_cells)
    shape[component_axis] = n_cells[component_axis] + 1
    shape = tuple(shape)
    N = shape[0] * shape[1] * shape[2]

    mats = []
    for axis in range(3):
        lo_bc, hi_bc = faces[axis]
        d = spacing[axis]
        if axis == component_axis:
            mats.append(_normal_matrix_interior_rows(n_cells[axis], d, lo_bc))
        else:
            mats.append(_tangential_matrix(shape[axis], d, lo_bc, hi_bc))

    Is = [sp.identity(shape[a], format="csr") for a in range(3)]
    L_h = (
        sp.kron(mats[0], sp.kron(Is[1], Is[2]))
        + sp.kron(Is[0], sp.kron(mats[1], Is[2]))
        + sp.kron(Is[0], sp.kron(Is[1], mats[2]))
    ).tocsr()

    correction = np.zeros(shape, dtype=np.float64)
    for axis in range(3):
        if axis == component_axis:
            continue
        lo_bc, hi_bc = faces[axis]
        c = _tangential_correction(shape[axis], spacing[axis], lo_bc, hi_bc, component_axis)
        bshape = [1, 1, 1]
        bshape[axis] = shape[axis]
        correction += c.reshape(bshape)

    M = (sp.identity(N, format="csr") - (theta * nu * dt) * L_h).tolil()
    free_row_mask = np.ones(N, dtype=bool)
    boundary_rhs = np.zeros(N, dtype=np.float64)

    lo_bc, hi_bc = faces[component_axis]
    periodic = lo_bc.velocity_type is VelocityBCType.PERIODIC
    n_cells_axis = n_cells[component_axis]

    def flat_indices_at(axis_index: int) -> np.ndarray:
        mask = np.zeros(shape, dtype=bool)
        idx = [slice(None)] * 3
        idx[component_axis] = axis_index
        mask[tuple(idx)] = True
        return np.flatnonzero(mask.ravel(order="C"))

    if periodic:
        lo_flat = flat_indices_at(0)
        hi_flat = flat_indices_at(n_cells_axis)
        for r, linked in zip(hi_flat, lo_flat):
            M[r, :] = 0.0
            M[r, r] = 1.0
            M[r, linked] = -1.0
            free_row_mask[r] = False
            boundary_rhs[r] = 0.0
    else:
        for side, axis_index, bc in (("lo", 0, lo_bc), ("hi", n_cells_axis, hi_bc)):
            flat = flat_indices_at(axis_index)
            if bc.velocity_type is VelocityBCType.PRESSURE_OUTLET:
                adjacent_index = 1 if side == "lo" else n_cells_axis - 1
                adjacent_flat = flat_indices_at(adjacent_index)
                for r, adj in zip(flat, adjacent_flat):
                    M[r, :] = 0.0
                    M[r, r] = 1.0
                    M[r, adj] = -1.0
                    free_row_mask[r] = False
                    boundary_rhs[r] = 0.0
            else:
                target = bc.velocity_value[component_axis] if bc.velocity_type is VelocityBCType.VELOCITY_INLET else 0.0
                for r in flat:
                    M[r, :] = 0.0
                    M[r, r] = 1.0
                    free_row_mask[r] = False
                    boundary_rhs[r] = target

    return L_h, M.tocsr(), free_row_mask, boundary_rhs, correction.ravel(order="C")


# --------------------------------------------------------------------------
# SPD-reduced normal-axis assembly (Milestone 7 Part C)
#
# The pin/linkage boundary ROWS above (`M[r,:]=0; M[r,r]=1[; M[r,adj]=-1]`)
# are what make `M` genuinely nonsymmetric: they overwrite a row without a
# matching column update. This alternative assembly instead ELIMINATES
# those boundary/duplicate normal-axis degrees of freedom from the linear
# system entirely -- substituting their known formula (a fixed target, an
# adjacent-value linkage, or a periodic duplicate) directly into the
# interior stencil -- exactly the same "ghost elimination" technique
# `pressure.py` already uses for a scalar's ghost cells, extended here to
# the component's own normal-axis boundary FACES (which, unlike a ghost,
# are real stored MAC values -- but algebraically eliminable all the
# same, since their value is always a known function of either a fixed
# constant or another unknown already in the system).
#
# Reduced DOF count along the normal axis: `n_cells` for a periodic
# component (face `n_cells`, the periodic duplicate of face `0`, is
# dropped entirely -- the same "periodic duplicate" convention used
# throughout this project, see docs/architecture.md); `n_cells - 1`
# otherwise (faces `0` and `n_cells` both eliminated, leaving interior
# faces `1..n_cells-1`). Tangential axes are unaffected -- they were
# already in eliminated ("cell-like") form via `_tangential_matrix`.
#
# Substitution formulas (derived from the SAME stencil
# `_normal_matrix_interior_rows` already uses, i.e. no discretization
# change -- only how the two boundary unknowns are removed from the
# system changes):
#
#   no_slip / velocity_inlet (fixed target T, a REAL stored face value,
#   not a mirrored ghost -- so no factor of 2, unlike a cell-centered
#   Dirichlet ghost): substituting u[boundary]=T into the interior row
#   adjacent to it adds `T/d^2` to that row's RHS correction; the row's
#   diagonal is unchanged.
#
#   pressure_outlet (u[boundary] = u[adjacent interior], the same
#   zero-gradient linkage the pin-row formulation enforces): substituting
#   u[boundary]=u[adjacent] into the interior row adjacent to it merges
#   the eliminated unknown's coefficient into the adjacent row's own
#   diagonal (`-2/d^2 -> -1/d^2`), with zero RHS contribution -- exactly
#   analogous to a homogeneous-Neumann modification.
#
#   periodic: the reduced axis is a standard periodic ring (identical
#   structure to `_tangential_matrix`'s periodic branch / `pressure.py`'s
#   periodic `_axis_matrix`) -- zero correction contribution.
#
# Mathematical equivalence with the original pin-row formulation is
# verified empirically (not just derived) by
# ``tests/test_diffusion.py``'s SPD-vs-pinned comparison tests, across
# every velocity BC type this project supports.
# --------------------------------------------------------------------------

def _reduced_normal_size(n_cells: int, lo_bc) -> int:
    if lo_bc.velocity_type is VelocityBCType.PERIODIC:
        return n_cells
    return n_cells - 1


def _normal_matrix_reduced(n_cells: int, d: float, lo_bc, hi_bc, component_axis: int) -> tuple:
    """SPD-reduced 1-D matrix + correction for the component's own
    normal axis. See the module-level comment above for the derivation."""
    inv_d2 = 1.0 / (d * d)
    periodic = lo_bc.velocity_type is VelocityBCType.PERIODIC

    if periodic:
        n = n_cells
        rows, cols, vals = [], [], []
        for i in range(n):
            left = n - 1 if i == 0 else i - 1
            right = 0 if i == n - 1 else i + 1
            rows += [i, i, i]; cols += [left, i, right]; vals += [inv_d2, -2.0 * inv_d2, inv_d2]
        matrix = sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
        return matrix, np.zeros(n, dtype=np.float64)

    n = n_cells - 1
    diag = np.full(n, -2.0 * inv_d2, dtype=np.float64)
    rows, cols, vals = [], [], []
    for i in range(n - 1):
        rows += [i, i + 1]; cols += [i + 1, i]; vals += [inv_d2, inv_d2]
    correction = np.zeros(n, dtype=np.float64)

    def target(bc):
        if bc.velocity_type is VelocityBCType.VELOCITY_INLET:
            return bc.velocity_value[component_axis]
        return 0.0

    if lo_bc.velocity_type is VelocityBCType.PRESSURE_OUTLET:
        diag[0] += inv_d2
    else:
        correction[0] += target(lo_bc) * inv_d2

    if hi_bc.velocity_type is VelocityBCType.PRESSURE_OUTLET:
        diag[-1] += inv_d2
    else:
        correction[-1] += target(hi_bc) * inv_d2

    rows += list(range(n)); cols += list(range(n)); vals += list(diag)
    matrix = sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
    return matrix, correction


def _assemble_velocity_diffusion_system_spd(mesh: StructuredMesh3D, bcs: BoundaryConditionSet, component_axis: int, nu: float, dt: float, theta: float) -> tuple:
    """SPD-reduced counterpart of :func:`_assemble_velocity_diffusion_system`.
    Returns ``(L_h, M, correction, reduced_shape)`` -- no
    ``free_row_mask``/``boundary_rhs``: every row of the reduced system
    is a genuine PDE row (that is the entire point)."""
    n_cells = (mesh.nx, mesh.ny, mesh.nz)
    spacing = (mesh.dx, mesh.dy, mesh.dz)
    faces = [(bcs.x_min, bcs.x_max), (bcs.y_min, bcs.y_max), (bcs.z_min, bcs.z_max)]

    reduced_shape = list(n_cells)
    lo_bc, hi_bc = faces[component_axis]
    reduced_shape[component_axis] = _reduced_normal_size(n_cells[component_axis], lo_bc)
    reduced_shape = tuple(reduced_shape)
    N = reduced_shape[0] * reduced_shape[1] * reduced_shape[2]

    mats = []
    normal_correction = None
    for axis in range(3):
        a_lo, a_hi = faces[axis]
        d = spacing[axis]
        if axis == component_axis:
            mat, normal_correction = _normal_matrix_reduced(n_cells[axis], d, a_lo, a_hi, component_axis)
            mats.append(mat)
        else:
            mats.append(_tangential_matrix(reduced_shape[axis], d, a_lo, a_hi))

    Is = [sp.identity(reduced_shape[a], format="csr") for a in range(3)]
    L_h = (
        sp.kron(mats[0], sp.kron(Is[1], Is[2]))
        + sp.kron(Is[0], sp.kron(mats[1], Is[2]))
        + sp.kron(Is[0], sp.kron(Is[1], mats[2]))
    ).tocsr()

    correction = np.zeros(reduced_shape, dtype=np.float64)
    for axis in range(3):
        a_lo, a_hi = faces[axis]
        bshape = [1, 1, 1]
        bshape[axis] = reduced_shape[axis]
        if axis == component_axis:
            correction += normal_correction.reshape(bshape)
        else:
            c = _tangential_correction(reduced_shape[axis], spacing[axis], a_lo, a_hi, component_axis)
            correction += c.reshape(bshape)

    M = (sp.identity(N, format="csr") - (theta * nu * dt) * L_h).tocsr()
    return L_h, M, correction.ravel(order="C"), reduced_shape


def _restrict_to_reduced(full_array: np.ndarray, component_axis: int, lo_bc) -> np.ndarray:
    """Extract the reduced-DOF entries from a full (``n_cells+1``-sized
    along ``component_axis``) array -- the inverse of
    :func:`_reconstruct_full_from_reduced`."""
    n_cells = full_array.shape[component_axis] - 1
    sl = [slice(None)] * 3
    if lo_bc.velocity_type is VelocityBCType.PERIODIC:
        sl[component_axis] = slice(0, n_cells)
    else:
        sl[component_axis] = slice(1, n_cells)
    return full_array[tuple(sl)]


def _reconstruct_full_from_reduced(reduced: np.ndarray, component_axis: int, lo_bc, hi_bc) -> np.ndarray:
    """Rebuild the full (``n_cells+1``-sized along ``component_axis``)
    array from a reduced solution, filling in the eliminated boundary/
    duplicate faces from their known formula (fixed target, adjacent-value
    linkage, or periodic duplicate) -- the same formulas
    :func:`_normal_matrix_reduced` used to eliminate them."""
    n_cells = reduced.shape[component_axis] if lo_bc.velocity_type is VelocityBCType.PERIODIC else reduced.shape[component_axis] + 1
    full_shape = list(reduced.shape)
    full_shape[component_axis] = n_cells + 1
    full = np.empty(tuple(full_shape), dtype=np.float64)

    def sl(a_index):
        s = [slice(None)] * 3
        s[component_axis] = a_index
        return tuple(s)

    if lo_bc.velocity_type is VelocityBCType.PERIODIC:
        s_body = [slice(None)] * 3
        s_body[component_axis] = slice(0, n_cells)
        full[tuple(s_body)] = reduced
        full[sl(n_cells)] = reduced[sl(0)]
        return full

    s_body = [slice(None)] * 3
    s_body[component_axis] = slice(1, n_cells)
    full[tuple(s_body)] = reduced

    def target(bc):
        if bc.velocity_type is VelocityBCType.VELOCITY_INLET:
            return bc.velocity_value[component_axis]
        return 0.0

    full[sl(0)] = reduced[sl(0)] if lo_bc.velocity_type is VelocityBCType.PRESSURE_OUTLET else target(lo_bc)
    full[sl(n_cells)] = reduced[sl(-1)] if hi_bc.velocity_type is VelocityBCType.PRESSURE_OUTLET else target(hi_bc)
    return full


class VelocityDiffusionSystem:
    """A reusable implicit velocity-diffusion system for one MAC velocity
    component. See module docstring for the discrete equation, why this
    needs its own matrix assembly (distinct from ``pressure.py``), and
    why no null-space handling is needed.

    ``formulation``:

    * ``"pinned"`` (default, unchanged from Milestone 5/6): boundary
      normal-axis rows are pin/linkage overrides; the assembled matrix
      is genuinely nonsymmetric, so only ``solver="direct"`` (default),
      ``"bicgstab"``, or ``"gmres"`` are valid -- **not** ``"cg"``
      (:class:`DiffusionSystemError`, matching the review's "do not
      silently use CG on a nonsymmetric matrix").
    * ``"spd"`` (Milestone 7 Part C): boundary normal-axis DOFs are
      algebraically eliminated instead (see the module-level comment
      above :func:`_assemble_velocity_diffusion_system_spd`), giving a
      genuinely symmetric positive-definite matrix on a *smaller*
      (boundary-DOF-free) index space -- ``system.matrix.shape`` differs
      from the ``"pinned"`` formulation's for the same mesh/BCs by
      design. ``solver="cg"`` (default for this formulation),
      ``"direct"``, ``"bicgstab"``, or ``"gmres"`` are all valid. The
      public ``solve()`` interface (``FaceField`` in, ``FaceField`` out,
      full ``n_cells+1``-sized data) is unchanged either way -- the
      reduced representation is purely internal, reconstructed via
      :func:`_reconstruct_full_from_reduced` after every solve.

    Mathematical equivalence between the two formulations (same PDE,
    same BCs, same discretization -- only how boundary DOFs are handled
    algebraically differs) is verified empirically in
    ``tests/test_diffusion.py``, not merely asserted.
    """

    def __init__(
        self,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet,
        component_axis: int,
        nu: float,
        dt: float,
        theta: float = 1.0,
        *,
        formulation: str = "pinned",
        solver: Optional[str] = None,
        preconditioner: Optional[str] = None,
        rtol: float = 1e-10,
        max_iterations: int = 10000,
    ):
        if component_axis not in (0, 1, 2):
            raise DiffusionSystemError(f"component_axis must be 0, 1, or 2, got {component_axis!r}")
        if nu <= 0:
            raise DiffusionSystemError(f"nu must be positive, got {nu!r}")
        if dt <= 0:
            raise DiffusionSystemError(f"dt must be positive, got {dt!r}")
        if not (0.0 < theta <= 1.0):
            raise DiffusionSystemError(f"theta must be in (0, 1], got {theta!r}")
        if formulation not in ("pinned", "spd"):
            raise DiffusionSystemError(f"formulation must be 'pinned' or 'spd', got {formulation!r}")

        self._mesh = mesh
        self._bcs = bcs
        self.component_axis = component_axis
        self.nu = nu
        self.dt = dt
        self.theta = theta
        self.formulation = formulation
        lo_bc, hi_bc = bcs[_AXIS_FACES[component_axis][0]], bcs[_AXIS_FACES[component_axis][1]]
        self._normal_faces = (lo_bc, hi_bc)

        solver = solver or ("cg" if formulation == "spd" else "direct")
        matrix_kind = "spd" if formulation == "spd" else "general"

        t0 = time.perf_counter()
        if formulation == "pinned":
            L_h, M, free_row_mask, boundary_rhs, correction = _assemble_velocity_diffusion_system(mesh, bcs, component_axis, nu, dt, theta)
            self._free_row_mask = free_row_mask
            self._boundary_rhs = boundary_rhs
        else:
            L_h, M, correction, self._reduced_shape = _assemble_velocity_diffusion_system_spd(mesh, bcs, component_axis, nu, dt, theta)
            self._free_row_mask = None
            self._boundary_rhs = None
        self._L_h = L_h
        self._M = M
        self._correction = correction
        self.assembly_time = time.perf_counter() - t0

        try:
            self._linear_solver = LinearSolver(
                self._M,
                method=solver,
                matrix_kind=matrix_kind,
                preconditioner=preconditioner,
                rtol=rtol,
                atol=0.0,
                max_iterations=max_iterations,
            )
        except LinearSolverError as exc:
            raise DiffusionSystemError(str(exc)) from exc
        self._lu = self._linear_solver._lu

    @property
    def mesh(self) -> StructuredMesh3D:
        return self._mesh

    @property
    def bcs(self) -> BoundaryConditionSet:
        return self._bcs

    @property
    def matrix(self) -> sp.csr_matrix:
        return self._M

    @property
    def shape(self) -> tuple:
        return self._M.shape

    def solve(self, u_n: FaceField, forcing: Optional[np.ndarray] = None, x0: Optional[FaceField] = None) -> tuple:
        """Advance one component from ``u_n`` (a :class:`FaceField` with
        this system's ``component_axis``) to ``u*``. ``forcing`` (if
        given) is a raw array matching ``u_n.interior``'s shape -- the
        body force ``f`` evaluated at whatever time level the caller's
        integrator scheme requires. ``x0`` (iterative ``"spd"``
        formulations only; ignored otherwise -- Milestone 7 Part D warm
        starts) is an optional initial guess, a :class:`FaceField` with
        this system's ``component_axis`` (typically the previous time
        step's own ``u*``). Returns ``(FaceField, DiffusionDiagnostics)``.
        """
        if u_n.normal_axis != self.component_axis:
            raise DiffusionSystemError(
                f"u_n.normal_axis={u_n.normal_axis} does not match this system's "
                f"component_axis={self.component_axis}"
            )
        if u_n.interior.shape != self._explicit_shape():
            raise DiffusionSystemError(
                f"u_n interior shape {u_n.interior.shape} is incompatible with this "
                f"system's mesh"
            )

        t_rhs0 = time.perf_counter()
        lo_bc, hi_bc = self._normal_faces
        if self.formulation == "spd":
            u_n_arr = _restrict_to_reduced(u_n.interior, self.component_axis, lo_bc)
        else:
            u_n_arr = u_n.interior

        u_n_vec = u_n_arr.astype(np.float64).ravel(order="C")
        explicit_L = self._L_h @ u_n_vec
        rhs = u_n_vec + (self.dt * self.nu * (1.0 - self.theta)) * explicit_L + (self.dt * self.nu) * self._correction
        if forcing is not None:
            forcing_arr = np.asarray(forcing, dtype=np.float64)
            if self.formulation == "spd":
                forcing_arr = _restrict_to_reduced(forcing_arr.reshape(u_n.interior.shape), self.component_axis, lo_bc)
            rhs = rhs + self.dt * forcing_arr.ravel(order="C")

        x0_vec = None
        if x0 is not None:
            x0_arr = x0.interior if self.formulation != "spd" else _restrict_to_reduced(x0.interior, self.component_axis, lo_bc)
            x0_vec = x0_arr.astype(np.float64).ravel(order="C")

        if self.formulation == "pinned":
            rhs = np.where(self._free_row_mask, rhs, self._boundary_rhs)
        rhs_time = time.perf_counter() - t_rhs0

        result_ls = self._linear_solver.solve(rhs, x0=x0_vec)
        u_star_vec = result_ls.x

        finite = bool(np.all(np.isfinite(u_star_vec)))
        residual = result_ls.final_residual if finite else float("nan")
        converged = finite and result_ls.converged

        if self.formulation == "spd":
            u_star_reduced = u_star_vec.reshape(self._reduced_shape, order="C")
            full = _reconstruct_full_from_reduced(u_star_reduced, self.component_axis, lo_bc, hi_bc)
        else:
            full = u_star_vec.reshape(u_n.interior.shape, order="C")

        result = FaceField.zeros(self._mesh, normal_axis=self.component_axis)
        result.interior = full

        diagnostics = DiffusionDiagnostics(
            converged=converged,
            method=result_ls.method,
            iterations=result_ls.iterations,
            residual=residual,
            finite=finite,
            assembly_time=self.assembly_time,
            solve_time=result_ls.solve_time,
            relative_residual=result_ls.relative_residual,
            preconditioner_time=result_ls.preconditioner_time,
            rhs_time=rhs_time,
        )
        return result, diagnostics

    def _explicit_shape(self) -> tuple:
        n_cells = (self._mesh.nx, self._mesh.ny, self._mesh.nz)
        shape = list(n_cells)
        shape[self.component_axis] = n_cells[self.component_axis] + 1
        return tuple(shape)
