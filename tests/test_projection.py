"""Tests for navier3d.projection: project(), derive_pressure_bcs().

Grids are nonsymmetric (nx != ny != nz) throughout. Sections below map
directly to the 21 required-test list from the Milestone 4 review.
"""
import numpy as np
import pytest

from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_velocity_bc,
)
from navier3d.fields import ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import divergence, gradient, scalar_laplacian
from navier3d.projection import ProjectionError, ProjectionResult, derive_pressure_bcs, project

NX, NY, NZ = 6, 8, 10


def mesh(n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=n_ghost)


def fbc(velocity, pressure, velocity_value=None, pressure_value=None, pressure_gradient_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
        pressure_gradient_value=pressure_gradient_value,
    )


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def wall_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip", "neumann")
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def inlet_outlet_bcs(inlet_speed: float = 2.0) -> BoundaryConditionSet:
    w = fbc("no_slip", "neumann")
    inlet = fbc("velocity_inlet", "neumann", velocity_value=(inlet_speed, 0.0, 0.0))
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    return BoundaryConditionSet(x_min=inlet, x_max=outlet, y_min=w, y_max=w, z_min=w, z_max=w)


def random_velocity(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> VelocityField:
    rng = np.random.default_rng(seed)
    velocity = VelocityField.zeros(m)
    for comp in velocity.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(velocity, bcs)
    return velocity


def _velocity_l2(velocity: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> float:
    dV = mesh.cell_volume
    total = 0.0
    for axis, comp in enumerate(velocity.components()):
        interior = comp.interior
        if bcs.is_periodic_axis(axis):
            sl = [slice(None)] * 3
            sl[axis] = slice(0, -1)
            interior = interior[tuple(sl)]
        total += np.sum(interior ** 2)
    return float(np.sqrt(total * dV))


def _velocity_inner_product(a: VelocityField, b: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> float:
    dV = mesh.cell_volume
    total = 0.0
    for axis, (ca, cb) in enumerate(zip(a.components(), b.components())):
        ia, ib = ca.interior, cb.interior
        if bcs.is_periodic_axis(axis):
            sl = [slice(None)] * 3
            sl[axis] = slice(0, -1)
            ia, ib = ia[tuple(sl)], ib[tuple(sl)]
        total += np.sum(ia * ib)
    return float(total * dV)


def _kinetic_energy(velocity: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> float:
    return 0.5 * _velocity_l2(velocity, mesh, bcs) ** 2


# --------------------------------------------------------------------------
# 1. Random periodic predictor: many-orders divergence reduction
# --------------------------------------------------------------------------

def test_periodic_projection_reduces_divergence_many_orders() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=0)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-12, rhs_compatibility="mean_removal")
    assert result.max_divergence_before > 1.0
    assert result.max_divergence_after < 1e-8
    assert result.normalized_divergence_after < 1e-8
    reduction = result.max_divergence_before / max(result.max_divergence_after, 1e-300)
    assert reduction > 1e8


# --------------------------------------------------------------------------
# 2. Discrete algebraic cancellation
# --------------------------------------------------------------------------

def test_algebraic_cancellation_identity() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=1)
    rho, dt = 1.3, 0.02
    result = project(u_star, bcs, m, rho=rho, dt=dt, tol=1e-12, rhs_compatibility="mean_removal")

    lhs = divergence(result.velocity, m).interior
    lap_p = scalar_laplacian(result.pressure, m).interior
    rhs = divergence(u_star, m).interior - (dt / rho) * lap_p
    np.testing.assert_allclose(lhs, rhs, atol=1e-9)


# --------------------------------------------------------------------------
# 3. Idempotence
# --------------------------------------------------------------------------

def test_idempotence() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=2)
    result1 = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")
    result2 = project(result1.velocity, bcs, m, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")
    for c1, c2 in zip(result1.velocity.components(), result2.velocity.components()):
        np.testing.assert_allclose(c1.interior, c2.interior, atol=1e-7)


# --------------------------------------------------------------------------
# 4. Solenoidal preservation
# --------------------------------------------------------------------------

def test_solenoidal_constant_field_unchanged() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_s = VelocityField.zeros(m)
    u_s.u.data[:] = 2.0
    u_s.v.data[:] = -1.0
    u_s.w.data[:] = 0.5
    assert np.max(np.abs(divergence(u_s, m).interior)) < 1e-12

    result = project(u_s, bcs, m, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")
    for c_in, c_out in zip(u_s.components(), result.velocity.components()):
        np.testing.assert_allclose(c_out.interior, c_in.interior, atol=1e-8)


# --------------------------------------------------------------------------
# 5. Gradient removal
# --------------------------------------------------------------------------

def test_pure_gradient_field_projects_to_zero() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    rng = np.random.default_rng(3)
    phi = ScalarField.zeros(m)
    values = rng.uniform(-1.0, 1.0, size=phi.interior.shape)
    values -= values.mean()
    phi.interior = values
    from navier3d.boundary_conditions import apply_pressure_bc
    apply_pressure_bc(phi, bcs)

    u_star = gradient(phi, m)
    apply_velocity_bc(u_star, bcs)

    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")
    for comp in result.velocity.components():
        np.testing.assert_allclose(comp.interior, 0.0, atol=1e-7)


# --------------------------------------------------------------------------
# 6. Known Helmholtz decomposition
# --------------------------------------------------------------------------

def test_helmholtz_decomposition_recovers_solenoidal_part() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    rng = np.random.default_rng(4)
    phi = ScalarField.zeros(m)
    values = rng.uniform(-1.0, 1.0, size=phi.interior.shape)
    values -= values.mean()
    phi.interior = values
    from navier3d.boundary_conditions import apply_pressure_bc
    apply_pressure_bc(phi, bcs)
    grad_phi = gradient(phi, m)

    u_s = VelocityField.zeros(m)
    u_s.u.data[:] = 1.5
    u_s.v.data[:] = -0.5
    u_s.w.data[:] = 0.25

    u_star = VelocityField.zeros(m)
    for comp_out, comp_s, comp_g in zip(u_star.components(), u_s.components(), grad_phi.components()):
        comp_out.interior = comp_s.interior + comp_g.interior
    apply_velocity_bc(u_star, bcs)

    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")
    for comp_out, comp_s in zip(result.velocity.components(), u_s.components()):
        np.testing.assert_allclose(comp_out.interior, comp_s.interior, atol=1e-6)


# --------------------------------------------------------------------------
# 7. Pressure-offset invariance
# --------------------------------------------------------------------------

def test_pressure_offset_invariance() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=5)
    rho, dt = 1.0, 0.01
    result = project(u_star, bcs, m, rho=rho, dt=dt, tol=1e-13, rhs_compatibility="mean_removal")

    from navier3d.boundary_conditions import apply_pressure_bc
    p_shifted = ScalarField.zeros(m)
    p_shifted.interior = result.pressure.interior + 100.0
    apply_pressure_bc(p_shifted, result.pressure_bcs, spacing=m.spacing)
    grad_shifted = gradient(p_shifted, m)

    for comp_star, comp_grad, comp_out in zip(u_star.components(), grad_shifted.components(), result.velocity.components()):
        recomputed = comp_star.interior - (dt / rho) * comp_grad.interior
        np.testing.assert_allclose(recomputed, comp_out.interior, atol=1e-9)


# --------------------------------------------------------------------------
# 8 & 9. Orthogonality and energy
# --------------------------------------------------------------------------

def test_orthogonality_and_energy_periodic() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=6)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")

    removed = VelocityField.zeros(m)
    for comp_out, comp_star, comp_res in zip(removed.components(), u_star.components(), result.velocity.components()):
        comp_out.interior = comp_star.interior - comp_res.interior
    apply_velocity_bc(removed, bcs)

    inner = _velocity_inner_product(result.velocity, removed, m, bcs)
    scale = _velocity_l2(u_star, m, bcs) ** 2
    assert abs(inner) < 1e-8 * max(scale, 1.0)

    k_before = _kinetic_energy(u_star, m, bcs)
    k_after = _kinetic_energy(result.velocity, m, bcs)
    assert k_after <= k_before + 1e-8 * max(k_before, 1.0)


# --------------------------------------------------------------------------
# 10. Density / time-step scaling
# --------------------------------------------------------------------------

def test_rho_dt_scaling() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=7)

    r1 = project(u_star, bcs, m, rho=1.0, dt=0.1, tol=1e-13, rhs_compatibility="mean_removal")
    r2 = project(u_star, bcs, m, rho=2.0, dt=0.2, tol=1e-13, rhs_compatibility="mean_removal")  # same ratio
    r3 = project(u_star, bcs, m, rho=1.0, dt=0.05, tol=1e-13, rhs_compatibility="mean_removal")  # 2x ratio

    for c1, c2, c3 in zip(r1.velocity.components(), r2.velocity.components(), r3.velocity.components()):
        np.testing.assert_allclose(c1.interior, c2.interior, atol=1e-8)
        np.testing.assert_allclose(c1.interior, c3.interior, atol=1e-8)

    np.testing.assert_allclose(r2.pressure.interior, r1.pressure.interior, atol=1e-8)
    np.testing.assert_allclose(r3.pressure.interior, 2.0 * r1.pressure.interior, atol=1e-6)


def test_invalid_rho_or_dt_rejected() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=8)
    with pytest.raises(ValueError):
        project(u_star, bcs, m, rho=-1.0, dt=0.01)
    with pytest.raises(ValueError):
        project(u_star, bcs, m, rho=1.0, dt=0.0)


# --------------------------------------------------------------------------
# 11. Stationary no-slip walls
# --------------------------------------------------------------------------

def test_stationary_no_slip_walls() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    u_star = random_velocity(m, bcs, seed=9)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-12)

    assert np.max(np.abs(result.velocity.u.interior[0, :, :])) < 1e-10
    assert np.max(np.abs(result.velocity.u.interior[-1, :, :])) < 1e-10
    assert np.max(np.abs(result.velocity.v.interior[:, 0, :])) < 1e-10
    assert np.max(np.abs(result.velocity.w.interior[:, :, 0])) < 1e-10

    # tangential ghost mirror correctness: u's ghost just below y_min should equal -interior
    ng = m.n_ghost
    interior_adjacent = result.velocity.u.data[ng:-ng, ng, ng:-ng]
    ghost = result.velocity.u.data[ng:-ng, ng - 1, ng:-ng]
    np.testing.assert_allclose(ghost, -interior_adjacent, atol=1e-10)

    assert result.boundary_adjacent_max_divergence_after < 1e-6


# --------------------------------------------------------------------------
# 12. Moving wall
# --------------------------------------------------------------------------

def test_moving_wall_tangential_speed_survives() -> None:
    m = mesh(1)
    lid_speed = 3.0
    lid = fbc("velocity_inlet", "neumann", velocity_value=(lid_speed, 0.0, 0.0))
    w = fbc("no_slip", "neumann")
    bcs = BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=lid, z_min=w, z_max=w)
    u_star = random_velocity(m, bcs, seed=10)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-12)

    ng = m.n_ghost
    interior_adjacent = result.velocity.u.data[ng:-ng, -ng - 1, ng:-ng]
    ghost = result.velocity.u.data[ng:-ng, -ng, ng:-ng]
    np.testing.assert_allclose(ghost, 2.0 * lid_speed - interior_adjacent, atol=1e-10)
    # normal component at the lid is still impermeable (0)
    assert np.max(np.abs(result.velocity.v.interior[:, -1, :])) < 1e-10


# --------------------------------------------------------------------------
# 13. Prescribed normal velocity / inlet
# --------------------------------------------------------------------------

def test_inlet_normal_velocity_matches_target_pointwise() -> None:
    m = mesh(1)
    inlet_speed = 2.0
    bcs = inlet_outlet_bcs(inlet_speed)
    u_star = random_velocity(m, bcs, seed=11)  # non-uniform predictor at the inlet face
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="direct", tol=1e-12)

    inlet_face = result.velocity.u.interior[0, :, :]
    np.testing.assert_allclose(inlet_face, inlet_speed, atol=1e-9)
    assert result.max_divergence_after < 1e-6


def test_derive_pressure_bcs_neumann_gradient_matches_formula() -> None:
    m = mesh(1)
    bcs = inlet_outlet_bcs(2.0)
    u_star = random_velocity(m, bcs, seed=12)
    rho, dt = 1.5, 0.02
    pressure_bcs = derive_pressure_bcs(u_star, bcs, rho, dt)

    assert pressure_bcs.x_min.pressure_type is PressureBCType.NEUMANN
    u_face = u_star.u.boundary_layer("lo")
    expected_g = -1.0 * (rho / dt) * (u_face - 2.0)  # outward_sign=-1 on a _min face
    np.testing.assert_allclose(pressure_bcs.x_min.pressure_gradient_value, expected_g)


# --------------------------------------------------------------------------
# 14. Pressure outlet
# --------------------------------------------------------------------------

def test_pressure_outlet_does_not_overconstrain_normal_velocity() -> None:
    m = mesh(1)
    bcs = inlet_outlet_bcs(2.0)
    u_star = random_velocity(m, bcs, seed=13)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="direct", tol=1e-12)

    # outlet's pressure BC is untouched Dirichlet (not re-derived)
    assert result.pressure_bcs.x_max.pressure_type is PressureBCType.DIRICHLET
    assert result.pressure_bcs.x_max.pressure_value == pytest.approx(0.0)

    # outlet normal velocity is whatever the solve produced, NOT forced to a
    # specific target (unlike the inlet, which was); it varies across the
    # face (not a single constant), proving it was not clamped.
    outlet_face = result.velocity.u.interior[-1, :, :]
    assert np.std(outlet_face) > 1e-6
    assert result.max_divergence_after < 1e-6


# --------------------------------------------------------------------------
# 15. Closed-box / global compatibility
# --------------------------------------------------------------------------

def test_outlet_on_lo_side_face() -> None:
    """Same mechanism as the x_max-outlet tests but on a _min face, to
    exercise the 'lo' branch of the outlet-save/restore logic in project()."""
    m = mesh(1)
    w = fbc("no_slip", "neumann")
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    inlet = fbc("velocity_inlet", "neumann", velocity_value=(-2.0, 0.0, 0.0))
    bcs = BoundaryConditionSet(x_min=outlet, x_max=inlet, y_min=w, y_max=w, z_min=w, z_max=w)
    u_star = random_velocity(m, bcs, seed=21)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="direct", tol=1e-12)

    assert result.pressure_bcs.x_min.pressure_type is PressureBCType.DIRICHLET
    outlet_face = result.velocity.u.interior[0, :, :]
    assert np.std(outlet_face) > 1e-6  # not clamped to a single value
    np.testing.assert_allclose(result.velocity.u.interior[-1, :, :], -2.0, atol=1e-8)
    assert result.max_divergence_after < 1e-6


def test_closed_box_divergence_matches_boundary_flux() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    u_star = random_velocity(m, bcs, seed=14)
    dV = m.cell_volume

    total_div = float(np.sum(divergence(u_star, m).interior) * dV)

    flux = 0.0
    areas = (m.face_area_x, m.face_area_y, m.face_area_z)
    for axis, comp in enumerate(u_star.components()):
        hi = np.sum(comp.interior[tuple(-1 if a == axis else slice(None) for a in range(3))])
        lo = np.sum(comp.interior[tuple(0 if a == axis else slice(None) for a in range(3))])
        flux += (hi - lo) * areas[axis]

    assert total_div == pytest.approx(flux, abs=1e-9)
    # all walls -> flux is exactly zero (impermeable), so total divergence is too
    assert total_div == pytest.approx(0.0, abs=1e-9)


# --------------------------------------------------------------------------
# 16. Periodic duplicate normal faces stay synchronized
# --------------------------------------------------------------------------

def test_periodic_duplicate_faces_synchronized_after_projection() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=15)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-12, rhs_compatibility="mean_removal")

    for comp in result.velocity.components():
        lo = comp.boundary_layer("lo")
        hi = comp.boundary_layer("hi")
        np.testing.assert_allclose(lo, hi, atol=1e-9)


# --------------------------------------------------------------------------
# 17 & 18. zero_mean vs pin_cell, direct vs CG
# --------------------------------------------------------------------------

def test_zero_mean_and_pin_cell_give_same_corrected_velocity() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_velocity(m, bcs, seed=16)
    r_zm = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="cg", null_space_strategy="zero_mean", tol=1e-13, rhs_compatibility="mean_removal")
    r_pin = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="direct", null_space_strategy="pin_cell", rhs_compatibility="mean_removal")
    for c1, c2 in zip(r_zm.velocity.components(), r_pin.velocity.components()):
        np.testing.assert_allclose(c1.interior, c2.interior, atol=1e-6)


def test_direct_and_cg_give_same_corrected_velocity() -> None:
    m = mesh(1)
    bcs = wall_bcs()  # all-Neumann pressure (walls): singular, so direct needs pin_cell
    u_star = random_velocity(m, bcs, seed=17)
    r_direct = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="direct", null_space_strategy="pin_cell")
    r_cg = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="cg", null_space_strategy="pin_cell", tol=1e-13)
    for c1, c2 in zip(r_direct.velocity.components(), r_cg.velocity.components()):
        np.testing.assert_allclose(c1.interior, c2.interior, atol=1e-6)


# --------------------------------------------------------------------------
# 19. ng=1 and ng=2
# --------------------------------------------------------------------------

@pytest.mark.parametrize("n_ghost", [1, 2])
def test_projection_works_at_ng1_and_ng2(n_ghost: int) -> None:
    m = mesh(n_ghost)
    bcs = wall_bcs()
    u_star = random_velocity(m, bcs, seed=18)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-11)
    assert result.max_divergence_after < 1e-6
    assert result.velocity.u.n_ghost == n_ghost


# --------------------------------------------------------------------------
# 20. Nonsymmetric mesh / axis permutation
# --------------------------------------------------------------------------

def test_axis_permutation_distinct_inlet_targets() -> None:
    """Different inlet targets on different axes: catches a copy-pasted
    axis index in derive_pressure_bcs."""
    m = mesh(1)
    inlet_x = fbc("velocity_inlet", "neumann", velocity_value=(1.0, 0.0, 0.0))
    inlet_y = fbc("velocity_inlet", "neumann", velocity_value=(0.0, 2.0, 0.0))
    inlet_z = fbc("velocity_inlet", "neumann", velocity_value=(0.0, 0.0, 3.0))
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    bcs = BoundaryConditionSet(x_min=inlet_x, x_max=outlet, y_min=inlet_y, y_max=outlet, z_min=inlet_z, z_max=outlet)
    u_star = random_velocity(m, bcs, seed=19)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="direct", tol=1e-12)

    np.testing.assert_allclose(result.velocity.u.interior[0, :, :], 1.0, atol=1e-8)
    np.testing.assert_allclose(result.velocity.v.interior[:, 0, :], 2.0, atol=1e-8)
    np.testing.assert_allclose(result.velocity.w.interior[:, :, 0], 3.0, atol=1e-8)


# --------------------------------------------------------------------------
# 21. Projection failure path
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Matrix reuse across projections whose Neumann values change (M5 requirement)
# --------------------------------------------------------------------------

def test_project_reuses_pressure_system_across_changing_predictors() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    u_star1 = random_velocity(m, bcs, seed=30)
    result1 = project(u_star1, bcs, m, rho=1.0, dt=0.01, solver="direct", null_space_strategy="pin_cell")
    matrix_id = id(result1.pressure_system.matrix)
    lu_id = id(result1.pressure_system._lu)
    assembly_time = result1.pressure_system.assembly_time

    u_star2 = random_velocity(m, bcs, seed=31)  # a different predictor -> different Neumann values
    result2 = project(u_star2, bcs, m, rho=1.0, dt=0.01, pressure_system=result1.pressure_system)

    assert id(result2.pressure_system.matrix) == matrix_id
    assert id(result2.pressure_system._lu) == lu_id
    assert result2.pressure_system.assembly_time == assembly_time  # never re-assembled
    assert result2.max_divergence_after < 1e-6
    # the two predictors genuinely differ -> genuinely different pressure fields
    assert np.max(np.abs(result1.pressure.interior - result2.pressure.interior)) > 1e-6


def test_nonconverged_pressure_solve_raises_not_silently_returns() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    u_star = random_velocity(m, bcs, seed=20)
    with pytest.raises(ProjectionError):
        project(u_star, bcs, m, rho=1.0, dt=0.01, solver="cg", tol=1e-14, max_iterations=1)
