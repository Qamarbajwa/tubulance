"""Velocity projection: discrete incompressibility enforcement.

Implements the non-incremental (Chorin-type) fractional-step projection
documented in ``docs/architecture.md`` Section 5, built entirely from the
already-verified compatible operators (``operators.py``) and pressure
system (``pressure.py``):

```
L_h p = (rho/dt) * D_h(u*)          (pressure Poisson solve)
u^{n+1} = u* - (dt/rho) * G_h(p)     (velocity correction)
```

using ``L_h = D_h G_h`` exactly (Milestone 2's compatibility identity) and
Milestone 3's sign convention ``A = -L_h``, ``A p = -b`` (``pressure.py``'s
``PressurePoissonSystem.solve`` already implements this; ``project()``
below just supplies ``b = (rho/dt) * D_h(u*)``).

**This module does not compute a predictor.** ``u*`` is supplied by the
caller; no convection, diffusion, or time advancement happens here (that
is Milestones 5-7). ``project()`` is a single, stateless
predictor-in/corrected-out call.

Boundary pressure gradients: deriving ``dp/dn`` from a general predictor
------------------------------------------------------------------------
For a face with a prescribed normal-velocity target (`no_slip`,
`free_slip`, `symmetry` -> target 0; `velocity_inlet` -> the configured
normal component), the pressure Neumann condition needed to make the
*corrected* normal velocity hit that target follows directly from the
correction formula itself. At the boundary face (a real MAC unknown, not
a ghost -- see ``docs/architecture.md`` Section 3), the x-component
correction reads:

```
u_x^{n+1}[face] = u_x*[face] - (dt/rho) * (dp/dx)[face]
```

Setting the left side to the target and solving for ``(dp/dx)[face]``
gives a **coordinate-axis** derivative; converting to the **outward
normal** derivative ``dp/dn`` that ``pressure_gradient_value`` expects
requires a sign flip that depends on which side of the axis the face is
on (outward normal is ``-x_hat`` at ``x_min``, ``+x_hat`` at ``x_max``):

```
dp/dn = outward_sign * (rho/dt) * (u_n* - u_n_target)
```

with ``outward_sign = -1`` on a `_min` face and ``+1`` on a `_max` face,
and ``u_n`` here meaning the **coordinate** component of velocity (`u`,
`v`, or `w` -- whichever field is normal to that face), evaluated at that
face's own boundary-layer, *not* the outward-normal-signed velocity
(``derive_pressure_bcs`` below implements exactly this; see its
docstring for the algebra connecting the two sign conventions). Crucially,
because a general predictor is **not** spatially uniform along a
boundary face, ``dp/dn`` in general is **not** either -- ``u_n*`` above is
the predictor's own per-cell boundary value, giving a spatially-varying
Neumann condition (a full 2-D array over the face's tangential extent,
not a scalar). This is why Milestone 4 first required extending
``FaceBoundaryCondition.pressure_gradient_value`` and ``pressure.py``'s
correction-array assembly to accept array-valued (not just scalar) BC
data (``docs/architecture.md`` Section 10) -- a uniform target with a
uniform predictor is just the special case where that array happens to
be constant.

Assuming homogeneous Neumann (``dp/dn=0``) is correct **only** when the
predictor already satisfies the target everywhere on that face; this
module never makes that assumption implicitly -- it always computes the
(possibly zero) gradient explicitly from ``u*``.

`pressure_outlet` faces are **not** touched by this derivation: their
Dirichlet pressure BC is used exactly as configured, and no
normal-velocity target is imposed there (the corrected normal velocity
at an outlet is whatever the solve produces, not constrained to a
prescribed value) -- this is deliberate, not an oversight (requirement:
"verify Dirichlet pressure treatment without simultaneously
over-constraining normal velocity").

Reapplying velocity BCs after correction
------------------------------------------
``apply_velocity_bc`` is called on the corrected field to refresh
**tangential ghost cells** (e.g. `v`, `w`'s mirrors around an x-normal
wall): the correction step only ever writes to `.interior`, so those
ghosts still reflect the *predictor's* interior values afterward --
genuinely stale, not drift, and required for anything (e.g. future
diffusion) that reads them.

For **normal boundary-face values**, reapplication is deliberately
*not* uniform across BC types, because ``boundary_conditions.py``'s
``_normal_boundary_value`` has two different behaviors baked in:

* `no_slip` / `free_slip` / `symmetry` / `velocity_inlet` / `periodic`:
  the reapplied value is *exactly* the same target the derived pressure
  Neumann condition was constructed to hit, so reapplying only snaps
  away residual floating-point drift -- never a substantive change (if
  the pressure BC were wrong, the pre-reapplication value would be
  *substantially* off target, not just drift-off; the test suite checks
  values before this reapplication too, to keep that distinction
  visible).
* `pressure_outlet`: `_normal_boundary_value` does **not** reproduce the
  projection's result -- it applies a crude zero-gradient extrapolation
  from the adjacent interior cell (`boundary_conditions.py`'s Milestone-1
  fallback, written before a real pressure solve existed). Reapplying it
  here would silently over-write the correctly pressure-derived outflow
  velocity with that crude approximation -- exactly the "hides an
  inconsistent pressure BC" failure mode this milestone was told to
  avoid. So `pressure_outlet` faces' normal boundary values are saved
  *before* calling ``apply_velocity_bc`` and restored immediately after
  it (the tangential-ghost refresh for other components is unaffected by
  this save/restore, since it only touches this one face's own normal
  component).
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from . import operators
from .boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_pressure_bc,
    apply_velocity_bc,
)
from .fields import FaceField, ScalarField, VelocityField
from .mesh import StructuredMesh3D
from .pressure import PressurePoissonSystem, SolveDiagnostics

_AXIS_FACES = {0: ("x_min", "x_max"), 1: ("y_min", "y_max"), 2: ("z_min", "z_max")}


class ProjectionError(RuntimeError):
    """Raised when the pressure solve inside :func:`project` does not
    converge. No corrected velocity is computed or returned in that case
    -- silently returning a velocity "corrected" with a non-converged
    pressure field would misrepresent it as divergence-free when it is
    not."""


def _target_normal_velocity(face_bc: FaceBoundaryCondition, axis: int) -> float:
    if face_bc.velocity_type is VelocityBCType.VELOCITY_INLET:
        return face_bc.velocity_value[axis]
    # NO_SLIP, FREE_SLIP, SYMMETRY: impermeable wall.
    return 0.0


def _derive_face_pressure_bc(face_bc: FaceBoundaryCondition, comp_field: FaceField, axis: int, side: str, rho: float, dt: float) -> FaceBoundaryCondition:
    if face_bc.velocity_type in (VelocityBCType.PERIODIC, VelocityBCType.PRESSURE_OUTLET):
        return face_bc  # unchanged: periodic stays periodic; outlet Dirichlet is not re-derived.
    outward_sign = -1.0 if side == "lo" else 1.0
    u_star_face = comp_field.boundary_layer(side)  # full ghost-padded tangential shape
    target = _target_normal_velocity(face_bc, axis)
    g = outward_sign * (rho / dt) * (u_star_face - target)
    return FaceBoundaryCondition(
        velocity_type=face_bc.velocity_type,
        pressure_type=PressureBCType.NEUMANN,
        velocity_value=face_bc.velocity_value,
        pressure_gradient_value=g,
    )


def derive_pressure_bcs(u_star: VelocityField, bcs: BoundaryConditionSet, rho: float, dt: float) -> BoundaryConditionSet:
    """Derive the pressure BC set to use for the Poisson solve: every face
    with a prescribed normal-velocity target gets an inhomogeneous Neumann
    ``dp/dn`` (generally spatially-varying, see module docstring) computed
    from ``u_star``; `pressure_outlet` and `periodic` faces are unchanged.
    """
    components = {0: u_star.u, 1: u_star.v, 2: u_star.w}
    updated = {}
    for axis in range(3):
        lo_name, hi_name = _AXIS_FACES[axis]
        comp = components[axis]
        updated[lo_name] = _derive_face_pressure_bc(bcs[lo_name], comp, axis, "lo", rho, dt)
        updated[hi_name] = _derive_face_pressure_bc(bcs[hi_name], comp, axis, "hi", rho, dt)
    return BoundaryConditionSet(**updated)


def derive_phi_bcs(u_star: VelocityField, bcs: BoundaryConditionSet, rho: float, dt: float) -> BoundaryConditionSet:
    """Milestone 8: the pressure-*increment* ``phi``'s own BC set --
    distinct from :func:`derive_pressure_bcs` at exactly one place
    (`pressure_outlet`'s Dirichlet *value*), identical everywhere else.

    **Why they're identical for Neumann faces (no_slip / free_slip /
    symmetry / velocity_inlet, including a moving wall specified as a
    zero-normal-component velocity_inlet)**: this solver's predictor
    (``diffusion.py``) always pins a component's own normal-axis boundary
    *face* to its exact target -- 0 for an impermeable wall (stationary
    OR moving; wall motion is purely tangential, which never enters this
    normal-direction formula), or the configured value for
    `velocity_inlet` -- both at construction (the diffusion matrix's
    boundary row) and again via `apply_velocity_bc`'s reapplication
    before `project()`/`project_incremental()` ever see ``u_star``. So
    ``u_star``'s own boundary-normal value already exactly equals
    `_target_normal_velocity` regardless of whether the predictor also
    included a ``-(1/rho)*grad(p^n)`` term (Milestone 8's incremental
    predictor) or not (Milestone 6's non-incremental one) -- that term
    only affects *interior* rows of the diffusion solve, never a pinned
    boundary row. Consequently `_derive_face_pressure_bc`'s formula
    ``g = sign*(rho/dt)*(u_star_face - target)`` evaluates to (up to
    floating-point roundoff) exactly the same value -- effectively
    homogeneous Neumann -- whether it is being used to build ``p``'s BC
    (Milestone 4-6) or ``phi``'s BC (Milestone 8): **the same function,
    :func:`derive_pressure_bcs`, is mathematically correct for both**,
    and is reused here rather than reimplemented.

    **Why they differ at `pressure_outlet`**: the outlet's *absolute*
    pressure is fixed at the configured ``pressure_value`` for all time
    -- ``p^n`` already equals it there (by induction from the initial
    condition and this same invariant holding every step). For
    ``p^{n+1} = p^n + phi`` to *also* satisfy the same fixed outlet
    value, ``phi`` must be **zero** there, not ``pressure_value`` again
    (using ``pressure_value`` a second time would make
    ``p^{n+1} = p^n + phi = 2*pressure_value`` at that face -- a real,
    easy-to-get-wrong bug this function exists to avoid). This is the one
    substantive difference between ``p^n``'s and ``phi``'s BC sets.
    """
    base = derive_pressure_bcs(u_star, bcs, rho, dt)
    updated = {}
    for axis in range(3):
        lo_name, hi_name = _AXIS_FACES[axis]
        for face_name in (lo_name, hi_name):
            face_bc = base[face_name]
            if bcs[face_name].velocity_type is VelocityBCType.PRESSURE_OUTLET:
                updated[face_name] = FaceBoundaryCondition(
                    velocity_type=face_bc.velocity_type,
                    pressure_type=PressureBCType.DIRICHLET,
                    velocity_value=face_bc.velocity_value,
                    pressure_value=0.0,
                )
            else:
                updated[face_name] = face_bc
    return BoundaryConditionSet(**updated)


def _divergence_stats(div: ScalarField, velocity: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> dict:
    """``max``, ``rms``, volume-weighted ``l2``, normalized ``e_div``, and
    boundary-adjacent max |divergence|. ``e_div = |D_h u|_2 / (|u|_2/L + eps)``;
    ``|u|_2`` sums all three components' interior values (each periodic
    axis's duplicate high-index boundary face excluded, per
    ``docs/architecture.md`` "Periodic duplicate normal faces")."""
    d = div.interior
    dV = mesh.cell_volume
    max_div = float(np.max(np.abs(d)))
    rms_div = float(np.sqrt(np.mean(d ** 2)))
    l2_div = float(np.sqrt(np.sum(d ** 2) * dV))

    u_sq_sum = 0.0
    for axis, comp in enumerate(velocity.components()):
        interior = comp.interior
        if bcs.is_periodic_axis(axis):
            sl = [slice(None)] * 3
            sl[axis] = slice(0, -1)
            interior = interior[tuple(sl)]
        u_sq_sum += np.sum(interior ** 2)
    u_l2 = float(np.sqrt(u_sq_sum * dV))
    L = (mesh.lx * mesh.ly * mesh.lz) ** (1.0 / 3.0)
    eps = 1e-30
    e_div = l2_div / (u_l2 / L + eps)

    mask = np.zeros(d.shape, dtype=bool)
    any_physical_boundary = False
    for axis in range(3):
        if bcs.is_periodic_axis(axis):
            continue
        any_physical_boundary = True
        sl_lo = [slice(None)] * 3
        sl_lo[axis] = 0
        sl_hi = [slice(None)] * 3
        sl_hi[axis] = -1
        mask[tuple(sl_lo)] = True
        mask[tuple(sl_hi)] = True
    boundary_max = float(np.max(np.abs(d[mask]))) if any_physical_boundary else float("nan")

    return dict(max=max_div, rms=rms_div, l2=l2_div, e_div=e_div, boundary_max=boundary_max)


@dataclass
class ProjectionResult:
    """Structured result of one :func:`project` call.

    Three logically distinct diagnostics are kept separate throughout,
    never conflated (see module/`pressure.py` docstrings):
    ``pressure_diagnostics.final_residual`` (algebraic residual of the
    Poisson solve), ``*_divergence_after`` (post-projection PDE-level
    divergence), and boundary-condition error (not separately quantified
    here since the correction step makes it directly observable: check
    ``velocity``'s own boundary faces against the target, as
    ``tests/test_projection.py`` does).
    """

    velocity: VelocityField
    pressure: ScalarField
    divergence_before: ScalarField
    divergence_after: ScalarField
    max_divergence_before: float
    rms_divergence_before: float
    max_divergence_after: float
    rms_divergence_after: float
    l2_divergence_before: float
    l2_divergence_after: float
    normalized_divergence_before: float
    normalized_divergence_after: float
    boundary_adjacent_max_divergence_before: float
    boundary_adjacent_max_divergence_after: float
    pressure_bcs: BoundaryConditionSet
    pressure_diagnostics: SolveDiagnostics
    pressure_system: PressurePoissonSystem
    elapsed_time: float
    rhs_time: float = 0.0
    correction_time: float = 0.0
    projection_method: str = "non_incremental"
    phi: Optional[ScalarField] = None
    phi_diagnostics: Optional[SolveDiagnostics] = None


def project(
    u_star: VelocityField,
    bcs: BoundaryConditionSet,
    mesh: StructuredMesh3D,
    rho: float,
    dt: float,
    *,
    pressure_system: Optional[PressurePoissonSystem] = None,
    solver: str = "cg",
    preconditioner: Optional[str] = None,
    null_space_strategy: str = "zero_mean",
    rhs_compatibility: str = "mean_removal",
    tol: float = 1e-10,
    max_iterations: int = 10000,
    pin_index: tuple = (0, 0, 0),
    pressure_x0: Optional[ScalarField] = None,
) -> ProjectionResult:
    """Project ``u_star`` onto the space of discretely divergence-free
    velocity fields consistent with ``bcs``.

    Raises :class:`ProjectionError` if the pressure solve does not
    converge -- never returns a "corrected" velocity built from an
    unconverged pressure field.

    ``pressure_x0`` (Milestone 7 Part D): an optional initial guess for
    the pressure solve -- typically the *previous* time step's own
    pressure field, strongly correlated with the current step's solution
    for a smoothly-evolving flow. Ignored for ``solver="direct"``
    (meaningless there); forwarded to
    :meth:`~navier3d.pressure.PressurePoissonSystem.solve` for iterative
    solvers.

    ``pressure_system``: pass a :class:`PressurePoissonSystem` from a
    *previous* :func:`project` call (``result.pressure_system``) to reuse
    its matrix and (for ``solver="direct"``) factorization across calls --
    the natural pattern for a time-stepping loop, where the predictor
    changes every step (so the derived Neumann *values* change) but the
    BC *topology* (which face is a wall/inlet/outlet/periodic) does not.
    Internally this just calls ``pressure_system.update_bcs(...)``; the
    ``solver``/``preconditioner``/``null_space_strategy``/etc. keyword
    arguments are ignored when ``pressure_system`` is given (that system's
    own settings, fixed at its construction, are used instead). If
    omitted, a new system is constructed every call (correct but not
    matrix-reused -- fine for one-off use, wasteful in a tight time loop).
    """
    if rho <= 0:
        raise ValueError(f"rho must be positive, got {rho!r}")
    if dt <= 0:
        raise ValueError(f"dt must be positive, got {dt!r}")

    t0 = time.perf_counter()

    t_rhs0 = time.perf_counter()
    div_before = operators.divergence(u_star, mesh)
    stats_before = _divergence_stats(div_before, u_star, mesh, bcs)

    pressure_bcs = derive_pressure_bcs(u_star, bcs, rho, dt)

    rhs = ScalarField.zeros(mesh)
    rhs.interior = (rho / dt) * div_before.interior

    if pressure_system is not None:
        pressure_system.update_bcs(pressure_bcs)
        system = pressure_system
    else:
        system = PressurePoissonSystem(
            mesh,
            pressure_bcs,
            solver=solver,
            preconditioner=preconditioner,
            null_space_strategy=null_space_strategy,
            rhs_compatibility=rhs_compatibility,
            tol=tol,
            max_iterations=max_iterations,
            pin_index=pin_index,
        )
    rhs_time = time.perf_counter() - t_rhs0

    p, diag = system.solve(rhs, x0=pressure_x0)
    if not diag.converged:
        raise ProjectionError(f"pressure solve did not converge: {diag}")

    t_corr0 = time.perf_counter()
    apply_pressure_bc(p, pressure_bcs, spacing=mesh.spacing)
    grad_p = operators.gradient(p, mesh)

    corrected = VelocityField.zeros(mesh)
    for comp_out, comp_star, comp_grad in zip(corrected.components(), u_star.components(), grad_p.components()):
        comp_out.interior = comp_star.interior - (dt / rho) * comp_grad.interior

    # Save pressure_outlet faces' projection-computed normal velocity: see
    # "Reapplying velocity BCs after correction" above for why this must
    # not be overwritten by apply_velocity_bc's crude zero-gradient formula.
    outlet_saves = {}
    for axis in range(3):
        lo_name, hi_name = _AXIS_FACES[axis]
        comp = corrected.components()[axis]
        if bcs[lo_name].velocity_type is VelocityBCType.PRESSURE_OUTLET:
            outlet_saves[(axis, "lo")] = comp.boundary_layer("lo").copy()
        if bcs[hi_name].velocity_type is VelocityBCType.PRESSURE_OUTLET:
            outlet_saves[(axis, "hi")] = comp.boundary_layer("hi").copy()

    apply_velocity_bc(corrected, bcs)

    for (axis, side), saved in outlet_saves.items():
        corrected.components()[axis].boundary_layer(side)[...] = saved

    div_after = operators.divergence(corrected, mesh)
    stats_after = _divergence_stats(div_after, corrected, mesh, bcs)
    correction_time = time.perf_counter() - t_corr0

    elapsed = time.perf_counter() - t0

    return ProjectionResult(
        velocity=corrected,
        pressure=p,
        divergence_before=div_before,
        divergence_after=div_after,
        rhs_time=rhs_time,
        correction_time=correction_time,
        max_divergence_before=stats_before["max"],
        rms_divergence_before=stats_before["rms"],
        max_divergence_after=stats_after["max"],
        rms_divergence_after=stats_after["rms"],
        l2_divergence_before=stats_before["l2"],
        l2_divergence_after=stats_after["l2"],
        normalized_divergence_before=stats_before["e_div"],
        normalized_divergence_after=stats_after["e_div"],
        boundary_adjacent_max_divergence_before=stats_before["boundary_max"],
        boundary_adjacent_max_divergence_after=stats_after["boundary_max"],
        pressure_bcs=pressure_bcs,
        pressure_diagnostics=diag,
        pressure_system=system,
        elapsed_time=elapsed,
    )


def project_incremental(
    u_star: VelocityField,
    p_previous: ScalarField,
    bcs: BoundaryConditionSet,
    mesh: StructuredMesh3D,
    rho: float,
    dt: float,
    *,
    rotational: bool = False,
    nu: Optional[float] = None,
    chi: float = 1.0,
    pressure_system: Optional[PressurePoissonSystem] = None,
    solver: str = "cg",
    preconditioner: Optional[str] = None,
    null_space_strategy: str = "zero_mean",
    rhs_compatibility: str = "mean_removal",
    tol: float = 1e-10,
    max_iterations: int = 10000,
    pin_index: tuple = (0, 0, 0),
    phi_x0: Optional[ScalarField] = None,
) -> ProjectionResult:
    """Milestone 8: incremental (``rotational=False``) or rotational
    (``rotational=True``) pressure-correction projection.

    Unlike :func:`project` (the Milestone 4-6 non-incremental / Chorin
    method, preserved unchanged and still the library default), the
    caller is expected to have already folded ``-(1/rho)*grad(p_previous)``
    into the predictor that produced ``u_star`` (see
    ``time_integrators.py``'s module docstring, "Incremental/rotational
    predictor") -- this function only performs the *correction* half:

    ```
    L_h phi = (rho/dt) * D_h(u_star)              (same Poisson SHAPE as
                                                      project()'s, different
                                                      BCs -- see derive_phi_bcs)
    u^{n+1} = u_star - (dt/rho) * G_h(phi)          (same formula as project(),
                                                      phi in place of the full p)
    p^{n+1} = p_previous + phi                       (incremental)
                - chi*rho*nu*D_h(u_star)             (rotational, additionally)
    ```

    The rotational term's derivation, convention, and honest empirical
    verification of its actual accuracy in this solver's specific
    implicit-diffusion + AB2-convection discretization are in
    ``docs/architecture.md`` Section 15 ("Milestone 8") -- summarized:
    the classical van Kan (1986) / Timmermans-Minev-Van de Vosse (1996)
    rotational correction is derived for simpler (explicit or
    semi-implicit) diffusion treatments; adopted here as the standard,
    well-established form (dimensionally corrected to this codebase's
    variables, using kinematic ``nu`` and explicit ``rho`` rather than
    dynamic viscosity), with ``chi`` exposed as a configurable
    coefficient (default ``1.0``, the classical value) rather than
    silently hard-coded, and its actual observed temporal order in this
    solver measured directly rather than assumed.

    Raises :class:`ProjectionError` if the phi solve does not converge,
    or :class:`ValueError` if ``rotational=True`` and ``nu`` is not given
    (the rotational correction needs it and there is no sensible default).
    """
    if rho <= 0:
        raise ValueError(f"rho must be positive, got {rho!r}")
    if dt <= 0:
        raise ValueError(f"dt must be positive, got {dt!r}")
    if rotational and nu is None:
        raise ValueError("rotational=True requires nu (the rotational correction is chi*rho*nu*D_h(u_star))")

    t0 = time.perf_counter()

    t_rhs0 = time.perf_counter()
    div_before = operators.divergence(u_star, mesh)
    stats_before = _divergence_stats(div_before, u_star, mesh, bcs)

    phi_bcs = derive_phi_bcs(u_star, bcs, rho, dt)

    rhs = ScalarField.zeros(mesh)
    rhs.interior = (rho / dt) * div_before.interior

    if pressure_system is not None:
        pressure_system.update_bcs(phi_bcs)
        system = pressure_system
    else:
        system = PressurePoissonSystem(
            mesh,
            phi_bcs,
            solver=solver,
            preconditioner=preconditioner,
            null_space_strategy=null_space_strategy,
            rhs_compatibility=rhs_compatibility,
            tol=tol,
            max_iterations=max_iterations,
            pin_index=pin_index,
        )
    rhs_time = time.perf_counter() - t_rhs0

    phi, phi_diag = system.solve(rhs, x0=phi_x0)
    if not phi_diag.converged:
        raise ProjectionError(f"phi (pressure-correction) solve did not converge: {phi_diag}")

    t_corr0 = time.perf_counter()
    apply_pressure_bc(phi, phi_bcs, spacing=mesh.spacing)
    grad_phi = operators.gradient(phi, mesh)

    corrected = VelocityField.zeros(mesh)
    for comp_out, comp_star, comp_grad in zip(corrected.components(), u_star.components(), grad_phi.components()):
        comp_out.interior = comp_star.interior - (dt / rho) * comp_grad.interior

    outlet_saves = {}
    for axis in range(3):
        lo_name, hi_name = _AXIS_FACES[axis]
        comp = corrected.components()[axis]
        if bcs[lo_name].velocity_type is VelocityBCType.PRESSURE_OUTLET:
            outlet_saves[(axis, "lo")] = comp.boundary_layer("lo").copy()
        if bcs[hi_name].velocity_type is VelocityBCType.PRESSURE_OUTLET:
            outlet_saves[(axis, "hi")] = comp.boundary_layer("hi").copy()

    apply_velocity_bc(corrected, bcs)

    for (axis, side), saved in outlet_saves.items():
        corrected.components()[axis].boundary_layer(side)[...] = saved

    div_after = operators.divergence(corrected, mesh)
    stats_after = _divergence_stats(div_after, corrected, mesh, bcs)

    new_pressure = ScalarField.zeros(mesh)
    new_pressure.interior = p_previous.interior + phi.interior
    if rotational:
        new_pressure.interior = new_pressure.interior - chi * rho * nu * div_before.interior
    correction_time = time.perf_counter() - t_corr0

    elapsed = time.perf_counter() - t0

    return ProjectionResult(
        velocity=corrected,
        pressure=new_pressure,
        divergence_before=div_before,
        divergence_after=div_after,
        rhs_time=rhs_time,
        correction_time=correction_time,
        max_divergence_before=stats_before["max"],
        rms_divergence_before=stats_before["rms"],
        max_divergence_after=stats_after["max"],
        rms_divergence_after=stats_after["rms"],
        l2_divergence_before=stats_before["l2"],
        l2_divergence_after=stats_after["l2"],
        normalized_divergence_before=stats_before["e_div"],
        normalized_divergence_after=stats_after["e_div"],
        boundary_adjacent_max_divergence_before=stats_before["boundary_max"],
        boundary_adjacent_max_divergence_after=stats_after["boundary_max"],
        pressure_bcs=phi_bcs,
        pressure_diagnostics=phi_diag,
        pressure_system=system,
        elapsed_time=elapsed,
        projection_method="rotational" if rotational else "incremental",
        phi=phi,
        phi_diagnostics=phi_diag,
    )


def project_initial_velocity(
    velocity: VelocityField,
    bcs: BoundaryConditionSet,
    mesh: StructuredMesh3D,
    *,
    solver: str = "direct",
    null_space_strategy: str = "pin_cell",
    **pressure_kwargs,
) -> VelocityField:
    """Project a raw (potentially non-solenoidal) initial velocity field
    onto the discretely divergence-free (solenoidal) subspace consistent with ``bcs``.

    Performs a discrete Leray-Helmholtz projection::

        u_solenoidal = u_raw - G_h(phi),    L_h(phi) = D_h(u_raw)

    Parameters
    ----------
    velocity : VelocityField
        The raw initial velocity field.
    bcs : BoundaryConditionSet
        The physical boundary condition set.
    mesh : StructuredMesh3D
        The Cartesian structured mesh.
    solver : str
        Linear solver for the projection Poisson problem (default "direct").
    null_space_strategy : str
        Null space strategy (default "pin_cell").
    **pressure_kwargs :
        Additional arguments forwarded to :func:`project`.

    Returns
    -------
    VelocityField
        The discretely divergence-free initial velocity field satisfying normal BC targets.
    """
    apply_velocity_bc(velocity, bcs)
    result = project(
        velocity,
        bcs,
        mesh,
        rho=1.0,
        dt=1.0,
        solver=solver,
        null_space_strategy=null_space_strategy,
        **pressure_kwargs,
    )
    return result.velocity
