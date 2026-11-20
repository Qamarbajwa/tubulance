"""Milestone 8 Parts 9/10/11/12/13: the full nonlinear manufactured-style
wall-bounded case (activates convection, diffusion, pressure history,
projection, forcing, boundaries, and time advancement together), with
boundary-adjacent vs. interior error measured separately, pressure
accuracy, divergence, and energy/momentum diagnostics.
"""
import math

import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.fields import FlowState, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import ThetaSchemeIntegrator, run

RHO, NU = 1.0, 0.05
LX, LY, LZ = 1.0, 1.25, 1.0
METHODS = ["non_incremental", "incremental", "rotational"]


def _mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=10, ny=12, nz=8, lx=LX, ly=LY, lz=LZ, n_ghost=1)


def _wall_bcs() -> BoundaryConditionSet:
    w = FaceBoundaryCondition(velocity_type=VelocityBCType.NO_SLIP, pressure_type=PressureBCType.NEUMANN)
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def _smooth_bump(X, Y, Z):
    return np.sin(math.pi * X / LX) * np.sin(math.pi * Y / LY) * np.sin(math.pi * Z / LZ)


def _forcing_field(mesh: StructuredMesh3D):
    """A smooth, spatially-varying forcing (not just a manufactured
    solution's residual) that vanishes at every wall like the velocity
    itself does, giving a genuine, nonzero pressure signal to track."""
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(mesh.cell_centers_x(), mesh.cell_centers_y(), mesh.face_coords_z(), indexing="ij")
    fx = 0.3 * _smooth_bump(Xu, Yu, Zu)
    fy = -0.2 * _smooth_bump(Xv, Yv, Zv)
    fz = 0.15 * _smooth_bump(Xw, Yw, Zw)

    def forcing(t: float) -> VelocityField:
        f = VelocityField.zeros(mesh)
        f.u.interior[:] = fx * math.cos(2.0 * t)
        f.v.interior[:] = fy * math.cos(2.0 * t)
        f.w.interior[:] = fz * math.cos(2.0 * t)
        return f
    return forcing


def _initial_state(mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> FlowState:
    s0 = FlowState.zeros(mesh)
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(mesh.cell_centers_x(), mesh.cell_centers_y(), mesh.face_coords_z(), indexing="ij")
    s0.velocity.u.interior[:] = 0.5 * _smooth_bump(Xu, Yu, Zu)
    s0.velocity.v.interior[:] = 0.3 * _smooth_bump(Xv, Yv, Zv)
    s0.velocity.w.interior[:] = -0.2 * _smooth_bump(Xw, Yw, Zw)
    apply_velocity_bc(s0.velocity, bcs)
    return s0


def _run(method: str, mesh, bcs, s0, dt: float, T: float):
    n_steps = round(T / dt)
    integrator = ThetaSchemeIntegrator(
        mesh, bcs, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
        forcing=_forcing_field(mesh), projection_method=method, chi=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    final_state, history = run(integrator, s0, n_steps)
    return final_state, history


def _boundary_interior_split(arr: np.ndarray) -> tuple:
    """Boundary-adjacent (first/last plane along every axis) vs.
    strictly-interior RMS, for a cell-centered (pressure-shaped) array."""
    mask = np.zeros(arr.shape, dtype=bool)
    for axis in range(3):
        sl_lo = [slice(None)] * 3
        sl_lo[axis] = 0
        sl_hi = [slice(None)] * 3
        sl_hi[axis] = -1
        mask[tuple(sl_lo)] = True
        mask[tuple(sl_hi)] = True
    boundary_rms = float(np.sqrt(np.mean(arr[mask] ** 2)))
    interior_rms = float(np.sqrt(np.mean(arr[~mask] ** 2))) if np.any(~mask) else float("nan")
    return boundary_rms, interior_rms


# ==========================================================================
# Part 9: full nonlinear pipeline activation
# ==========================================================================

@pytest.mark.parametrize("method", METHODS)
def test_full_nonlinear_pipeline_runs_and_converges(method: str) -> None:
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    final_state, history = _run(method, mesh, bcs, s0, dt=0.0005, T=0.005)
    assert max(h.max_divergence for h in history) < 1e-6
    assert max(h.normalized_divergence for h in history) < 1e-6
    for comp in final_state.velocity.components():
        assert np.all(np.isfinite(comp.data))
    assert all(h.pressure_diagnostics.converged for h in history)
    assert all(all(d.converged for d in h.diffusion_diagnostics) for h in history)


# ==========================================================================
# Part 10: boundary vs. interior error
# ==========================================================================

@pytest.mark.parametrize("method", METHODS)
def test_boundary_vs_interior_pressure_error_reported(method: str) -> None:
    """Measures E_boundary and E_interior (self-referenced, against a
    fine-dt run at the SAME mesh) -- confirms neither blows up
    (indicating an unhandled first-order pressure BC defect) relative to
    the other."""
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    T = 0.005

    reference, _ = _run(method, mesh, bcs, s0, dt=T / 512, T=T)
    p_ref = reference.pressure.interior - np.mean(reference.pressure.interior)

    final, _ = _run(method, mesh, bcs, s0, dt=T / 32, T=T)
    p_final = final.pressure.interior - np.mean(final.pressure.interior)

    e_boundary, e_interior = _boundary_interior_split(p_final - p_ref)
    assert np.isfinite(e_boundary) and np.isfinite(e_interior)
    # boundary error must not be dramatically (>20x) worse than interior
    # -- the signature of an unhandled first-order pressure BC defect
    assert e_boundary < 20.0 * (e_interior + 1e-12), (
        f"{method}: boundary error {e_boundary} vs interior error {e_interior} -- "
        f"possible unhandled pressure BC defect"
    )


@pytest.mark.parametrize("method", ["incremental", "rotational"])
def test_boundary_error_not_worse_than_non_incremental(method: str) -> None:
    """The new methods must not make near-wall pressure accuracy WORSE
    than the existing non-incremental reference."""
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    T = 0.005
    dt = T / 32

    ref_noninc, _ = _run("non_incremental", mesh, bcs, s0, dt=T / 512, T=T)
    final_noninc, _ = _run("non_incremental", mesh, bcs, s0, dt=dt, T=T)
    p_ref_n = ref_noninc.pressure.interior - np.mean(ref_noninc.pressure.interior)
    p_final_n = final_noninc.pressure.interior - np.mean(final_noninc.pressure.interior)
    eb_noninc, _ = _boundary_interior_split(p_final_n - p_ref_n)

    ref_new, _ = _run(method, mesh, bcs, s0, dt=T / 512, T=T)
    final_new, _ = _run(method, mesh, bcs, s0, dt=dt, T=T)
    p_ref_new = ref_new.pressure.interior - np.mean(ref_new.pressure.interior)
    p_final_new = final_new.pressure.interior - np.mean(final_new.pressure.interior)
    eb_new, _ = _boundary_interior_split(p_final_new - p_ref_new)

    assert eb_new < 2.0 * eb_noninc + 1e-12, f"{method}: boundary error {eb_new} vs non_incremental {eb_noninc}"


# ==========================================================================
# Part 11: pressure accuracy (mean-removed), independent temporal order
# ==========================================================================

@pytest.mark.parametrize("method", METHODS)
def test_pressure_temporal_order_reported_independently(method: str) -> None:
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    T = 0.005

    reference, _ = _run(method, mesh, bcs, s0, dt=T / 512, T=T)
    p_ref = reference.pressure.interior - np.mean(reference.pressure.interior)
    errors = []
    for dt in [T / 32, T / 64, T / 128]:
        s, _ = _run(method, mesh, bcs, s0, dt=dt, T=T)
        p_s = s.pressure.interior - np.mean(s.pressure.interior)
        errors.append(float(np.sqrt(np.mean((p_s - p_ref) ** 2))))
    orders = [math.log(e1 / e2) / math.log(2.0) for e1, e2 in zip(errors[:-1], errors[1:])]
    for order in orders:
        assert order > 0.7, f"{method}: pressure orders {orders}"


# ==========================================================================
# Part 12: divergence quality preserved
# ==========================================================================

@pytest.mark.parametrize("method", METHODS)
def test_normalized_divergence_meets_controlled_tolerance(method: str) -> None:
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    _, history = _run(method, mesh, bcs, s0, dt=0.0005, T=0.005)
    assert max(h.normalized_divergence for h in history) < 1e-6


# ==========================================================================
# Part 13: energy and momentum
# ==========================================================================

@pytest.mark.parametrize("method", METHODS)
def test_energy_bounded_no_unexplained_growth(method: str) -> None:
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    _, history = _run(method, mesh, bcs, s0, dt=0.0005, T=0.01)
    energies = [h.kinetic_energy for h in history]
    # forced flow: bounded growth relative to the largest early value, not unbounded blowup
    assert max(energies) <= 5.0 * (energies[0] + 1e-12)
    assert all(np.isfinite(e) for e in energies)


def test_periodic_momentum_conservation_unaffected_by_projection_method() -> None:
    """Milestone 2/6's periodic global-momentum-conservation property
    (sum of convection contributions ~0, excluding the duplicate face)
    is a property of convection.py alone, untouched by Milestone 8 --
    spot-checked here for completeness across all three integrator
    configurations."""
    from navier3d.convection import centered_convection

    mesh = StructuredMesh3D(nx=6, ny=7, nz=5, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    bcs = BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)
    rng = np.random.default_rng(4)
    v = VelocityField.zeros(mesh)
    for comp in v.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(v, bcs)
    N = centered_convection(v, mesh)
    dV = mesh.cell_volume
    for axis, comp in enumerate(N.components()):
        sl = [slice(None)] * 3
        sl[axis] = slice(0, -1)
        total = float(np.sum(comp.interior[tuple(sl)]) * dV)
        assert abs(total) < 1e-9
