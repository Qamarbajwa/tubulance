"""Conservative MAC-grid nonlinear convection: N_h(u) = D_h(u (x) u).

Computes the discrete divergence of the momentum flux tensor
``u (x) u`` at each velocity component's *own* MAC location, so the
result can be combined directly with the diffusion/pressure terms at
that same location (Milestone 5's `diffusion.py` RHS, Milestone 4's
projection). Two interchangeable schemes share one interface:
``centered_convection`` (2nd order) and ``upwind_convection`` (1st
order, donor-cell). Skew-symmetric form is intentionally **not**
implemented -- the review marked it optional ("if it can be
implemented cleanly and independently verified"), and a discrete
skew-symmetric operator that is *actually* energy-neutral to roundoff
requires the advective-form differencing to be constructed as the exact
adjoint of the conservative form's interpolation choices; getting that
wrong silently produces a form that looks plausible but fails the very
energy test it exists to pass. Given the scope already committed for
this milestone, centered and upwind (both required, both independently
verified against the energy/conservation tests below) were prioritized
over an unverified third option.

Flux locations and interpolation (MAC layout, uniform spacing)
-------------------------------------------------------------------
Recall (``docs/architecture.md`` Section 3): ``p`` at cell centers,
``u`` at x-faces, ``v`` at y-faces, ``w`` at z-faces. The momentum flux
tensor's components live at three distinct MAC locations, none of which
coincide with any single field's own native storage location -- each
requires interpolation:

* **Diagonal fluxes** ``u^2``, ``v^2``, ``w^2`` live at **cell centers**
  (the same location as ``p``). ``u^2`` is formed by first averaging
  ``u`` from its two bounding x-faces onto the cell center
  (``u_cc = 0.5*(u[i] + u[i+1])``), then squaring -- *not* by averaging
  ``u^2`` values computed at the faces (these differ at O(dx^2), both
  are second-order accurate, but only the "average-then-square" choice
  is used throughout this module, consistently, since mixing the two
  would break the discrete product rule the energy test relies on).
* **Off-diagonal fluxes** ``uv``, ``uw``, ``vw`` live at shared **edges**:
  ``uv`` at the location where an x-face and a y-face coincide (constant
  z, i.e. ``(i*dx, j*dy, (k+0.5)*dz)`` -- sometimes called a "z-edge");
  ``uw`` at an x-face/z-face edge (constant y); ``vw`` at a y-face/z-face
  edge (constant x). Each requires interpolating *both* contributing
  components onto that edge: e.g. for ``uv``, ``u`` is averaged from its
  two y-neighbors onto the y-face location, and ``v`` is averaged from
  its two x-neighbors onto the x-face location, then multiplied.

Each component's convective term is the divergence of these fluxes,
evaluated using exactly the two flux locations bounding that component's
own control volume along each axis -- e.g. for ``u`` (at x-faces):

```
N_u = (u^2_cc[i] - u^2_cc[i-1]) / dx           (self term, cell centers bound the x-face)
    + (uv_edge[j+1] - uv_edge[j]) / dy          (cross term, z-edges bound the y-cell)
    + (uw_edge[k+1] - uw_edge[k]) / dz          (cross term, y-edges bound the z-cell)
```

and analogously (by permuting x<->y<->z, u<->v<->w) for ``N_v``, ``N_w``.
This module implements that permutation generically (`_self_term`,
`_cross_term`, parametrized by axis) rather than three independently
hand-written blocks, specifically to avoid the copy-paste axis-swap bugs
that a nonsymmetric-grid test is designed to catch -- verified directly
by ``tests/test_convection.py``'s axis-permutation and independent
interpolation-location tests.

Centered vs. upwind
-----------------------
Both schemes interpolate the *advecting* velocity (the flux tensor's
"velocity direction" factor -- ``u_avg`` in the self term, ``b_edge`` in
a cross term) identically, via simple averaging. They differ only in how
the *advected* quantity is formed: centered averages it the same way;
upwind selects the donor-cell value based on the sign of the local
advecting velocity (``phi_upwind = phi_lo if advecting >= 0 else
phi_hi``), the standard first-order donor-cell construction.

Axis-permutation equivariance
------------------------------
``_self_term``/``_cross_term`` are written once, generically, in terms of
a component's own ``normal_axis`` and the two other axes -- there is no
per-axis special-casing anywhere in this module. Consequently the
operator is exactly equivariant under a relabeling of ``(x,y,z)`` and
``(u,v,w)``: for any permutation ``(a,b,c)`` of the axes, ``N_a`` is
computed by the *same code path* that computes ``N_x`` for axis ``a=0``,
just with the roles of the axes swapped. This is verified directly (not
merely assumed from the code's structure) by
``tests/test_convection.py::test_4_axis_permutation_distinct_linear_fields``,
which uses a genuine 3-cycle (``u=y, v=z, w=x``, so no axis maps to
itself) and checks all three components against independently
hand-derived values; ``test_3``/``test_8``/``test_polynomial_z_...``
additionally isolate the ``(x,y)`` and ``(x,z)`` axis pairings
individually. A hand-written per-axis implementation (three separate
blocks) would not have this guarantee "for free" -- copy-paste axis
transcription errors are exactly the failure mode a nonsymmetric grid
(``nx != ny != nz``, used throughout this project's tests) is designed
to expose.

Semi-discrete vs. fully-discrete energy behavior
--------------------------------------------------
``tests/test_convection.py``'s energy tests (7 and 9) verify
``<u, N_h(u)>_F ~ 0`` (centered) for a *fixed*, already discretely
divergence-free velocity field -- this is a property of the **spatial**
convection operator alone, evaluated at a single instant, with no time
integration involved. It confirms centered convection does not, by
itself, manufacture or destroy kinetic energy at the semi-discrete
(continuous-in-time, discrete-in-space) level.

This is a *necessary* but not *sufficient* condition for the fully
discrete kinetic energy reported by ``ThetaSchemeIntegrator``
(``StepDiagnostics.kinetic_energy``) over an actual run to be
conserved: the observed energy drift over real time-stepped runs (see
``tests/test_navier_stokes_verification.py`` test C) also depends on
(a) the time-integration scheme's own truncation error (AB2/Heun-startup
convection, theta-scheme diffusion), (b) viscosity, which is *always*
strictly dissipative and not part of this operator at all, and (c) the
pressure projection, which enforces the discrete divergence-free
constraint each step but is itself only approximately accurate in time
(see ``docs/architecture.md``'s Milestone 6 correction section for the
measured temporal order of the projection step) and therefore
contributes its own small, non-zero effect on the discrete energy
budget. Test C's near-inviscid centered-vs-upwind comparison measures
that *combined* fully discrete effect, not the semi-discrete property
alone -- the two are related but not interchangeable, and are kept
distinct in both the tests and this documentation intentionally.

Energy inner product weighting (MAC dual volumes)
-----------------------------------------------------
``tests/test_convection.py``'s ``_inner_product`` (and the analogous
``_kinetic_energy`` helpers in ``test_navier_stokes_verification.py`` and
``time_integrators.py``) weight every velocity-component sample by the
same scalar ``mesh.cell_volume = dx*dy*dz``, regardless of which axis
that component is normal to. This is correct, not a simplification: on a
*uniform* Cartesian MAC grid, the natural finite-volume "dual cell"
associated with an x-face degree of freedom spans half a cell on each
side along x (``[(i-1/2)dx, (i+1/2)dx]``, centered on the face) and a
full cell along y and z -- total volume ``dx*dy*dz``, identical to a
u-face's, v-face's, or w-face's own dual volume, and identical to a
pressure cell's volume. All three components can therefore be summed
with one uniform weight in a discrete L2 inner product. Each periodic
axis's duplicate high-index face (the same physical DOF as the
low-index face -- see "Periodic duplicate normal faces" in
``docs/architecture.md``) is excluded from every such sum before
weighting, exactly as in the global-momentum-conservation test (6);
``test_6_naive_sum_including_duplicate_is_not_conserved`` demonstrates
this exclusion is load-bearing, not cosmetic.
"""
from __future__ import annotations

import numpy as np

from .fields import FaceField, VelocityField
from .mesh import StructuredMesh3D

_N_CELLS = {0: "nx", 1: "ny", 2: "nz"}


class ConvectionError(ValueError):
    """Raised when fields passed to a convection scheme are incompatible with the mesh."""


def _check_velocity(velocity: VelocityField, mesh: StructuredMesh3D, name: str) -> None:
    n_cells = (mesh.nx, mesh.ny, mesh.nz)
    for axis, comp in enumerate(velocity.components()):
        if comp.normal_axis != axis:
            raise ConvectionError(f"{name}: component {axis} has normal_axis={comp.normal_axis}")
        ng = comp.n_ghost
        if ng != mesh.n_ghost:
            raise ConvectionError(f"{name}: component {axis} n_ghost={ng} does not match mesh.n_ghost={mesh.n_ghost}")
        shape = [n_cells[0] + 2 * ng, n_cells[1] + 2 * ng, n_cells[2] + 2 * ng]
        shape[axis] = n_cells[axis] + 1 + 2 * ng
        if comp.data.shape != tuple(shape):
            raise ConvectionError(f"{name}: component {axis} shape {comp.data.shape} incompatible with mesh; expected {tuple(shape)}")


def _self_term(comp: FaceField, mesh: StructuredMesh3D, d_axis: float, scheme: str) -> np.ndarray:
    """``d(u_a^2)/da`` at ``comp``'s own locations, ``a = comp.normal_axis``."""
    axis = comp.normal_axis
    ng = comp.n_ghost
    n_cells_axis = getattr(mesh, _N_CELLS[axis])
    data = comp.data

    lo = [slice(None)] * 3
    lo[axis] = slice(0, data.shape[axis] - 1)
    hi = [slice(None)] * 3
    hi[axis] = slice(1, data.shape[axis])
    u_lo, u_hi = data[tuple(lo)], data[tuple(hi)]
    u_avg = 0.5 * (u_lo + u_hi)

    flux = u_avg * u_avg if scheme == "centered" else u_avg * np.where(u_avg >= 0.0, u_lo, u_hi)

    sl_hi = [slice(None)] * 3
    sl_lo = [slice(None)] * 3
    for a in range(3):
        if a == axis:
            sl_hi[a] = slice(ng, ng + n_cells_axis + 1)
            sl_lo[a] = slice(ng - 1, ng + n_cells_axis)
        else:
            sl_hi[a] = slice(ng, -ng)
            sl_lo[a] = slice(ng, -ng)
    return (flux[tuple(sl_hi)] - flux[tuple(sl_lo)]) / d_axis


def _cross_term(comp_a: FaceField, comp_b: FaceField, mesh: StructuredMesh3D, d_b: float, scheme: str) -> np.ndarray:
    """``d(u_a * u_b edge)/db`` at ``comp_a``'s own locations, contributing
    to component ``a``'s convective term (``b = comp_b.normal_axis != a``)."""
    a = comp_a.normal_axis
    b = comp_b.normal_axis
    c = 3 - a - b
    ng = comp_a.n_ghost
    n_cells = {0: mesh.nx, 1: mesh.ny, 2: mesh.nz}

    # comp_a's two neighbors straddling axis-b faces (advected quantity)
    a_lo_idx = [slice(None)] * 3
    a_lo_idx[b] = slice(0, comp_a.data.shape[b] - 1)
    a_hi_idx = [slice(None)] * 3
    a_hi_idx[b] = slice(1, comp_a.data.shape[b])
    a_lo, a_hi = comp_a.data[tuple(a_lo_idx)], comp_a.data[tuple(a_hi_idx)]

    # comp_b's two neighbors straddling axis-a faces (advecting velocity), always centered
    b_lo_idx = [slice(None)] * 3
    b_lo_idx[a] = slice(0, comp_b.data.shape[a] - 1)
    b_hi_idx = [slice(None)] * 3
    b_hi_idx[a] = slice(1, comp_b.data.shape[a])
    b_edge_full = 0.5 * (comp_b.data[tuple(b_lo_idx)] + comp_b.data[tuple(b_hi_idx)])

    a_sl = [None, None, None]
    a_sl[a] = slice(ng, ng + n_cells[a] + 1)
    a_sl[b] = slice(ng - 1, ng + n_cells[b])
    a_sl[c] = slice(ng, ng + n_cells[c])

    b_sl = [None, None, None]
    b_sl[a] = slice(ng - 1, ng + n_cells[a])
    b_sl[b] = slice(ng, ng + n_cells[b] + 1)
    b_sl[c] = slice(ng, ng + n_cells[c])

    b_edge = b_edge_full[tuple(b_sl)]
    if scheme == "centered":
        a_edge = 0.5 * (a_lo[tuple(a_sl)] + a_hi[tuple(a_sl)])
    else:
        a_lo_s, a_hi_s = a_lo[tuple(a_sl)], a_hi[tuple(a_sl)]
        a_edge = np.where(b_edge >= 0.0, a_lo_s, a_hi_s)

    edge = a_edge * b_edge

    hi_b = [slice(None)] * 3
    hi_b[b] = slice(1, n_cells[b] + 1)
    lo_b = [slice(None)] * 3
    lo_b[b] = slice(0, n_cells[b])
    return (edge[tuple(hi_b)] - edge[tuple(lo_b)]) / d_b


def _convection_component(velocity: VelocityField, mesh: StructuredMesh3D, axis: int, scheme: str) -> np.ndarray:
    comps = velocity.components()
    comp_a = comps[axis]
    spacings = (mesh.dx, mesh.dy, mesh.dz)
    result = _self_term(comp_a, mesh, spacings[axis], scheme)
    for b in range(3):
        if b == axis:
            continue
        result = result + _cross_term(comp_a, comps[b], mesh, spacings[b], scheme)
    return result


def _convection(velocity: VelocityField, mesh: StructuredMesh3D, scheme: str, name: str) -> VelocityField:
    _check_velocity(velocity, mesh, name)
    result = VelocityField.zeros(mesh)
    for axis, comp in enumerate(result.components()):
        comp.interior = _convection_component(velocity, mesh, axis, scheme)
    return result


def centered_convection(velocity: VelocityField, mesh: StructuredMesh3D) -> VelocityField:
    """Second-order centered conservative convection ``N_h(u) = D_h(u (x) u)``.

    Requires ``velocity``'s ghosts to already be filled
    (``apply_velocity_bc``) -- both the self term (normal-axis ghost, for
    faces adjacent to a boundary) and the cross terms (tangential ghosts)
    read one ghost layer.
    """
    return _convection(velocity, mesh, "centered", "centered_convection")


def upwind_convection(velocity: VelocityField, mesh: StructuredMesh3D) -> VelocityField:
    """First-order donor-cell upwind conservative convection. Same
    interface and ghost requirements as :func:`centered_convection`."""
    return _convection(velocity, mesh, "upwind", "upwind_convection")
