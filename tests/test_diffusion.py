"""Tests for navier3d.diffusion: VelocityDiffusionSystem.

Grids are nonsymmetric (nx != ny != nz) throughout.
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
from navier3d.diffusion import DiffusionSystemError, VelocityDiffusionSystem
from navier3d.fields import FaceField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import velocity_laplacian

NX, NY, NZ = 4, 5, 6


def mesh(n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=n_ghost)


def fbc(velocity, pressure="neumann", velocity_value=None, pressure_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
    )


def wall_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def random_full_velocity(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> VelocityField:
    rng = np.random.default_rng(seed)
    velocity = VelocityField.zeros(m)
    for comp in velocity.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(velocity, bcs)
    return velocity


# --------------------------------------------------------------------------
# Construction validation
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kwargs", [dict(nu=0.0), dict(dt=0.0), dict(theta=0.0), dict(theta=1.5), dict(component_axis=3), dict(formulation="not_a_formulation")])
def test_invalid_construction_rejected(kwargs) -> None:
    m = mesh(1)
    base = dict(mesh=m, bcs=wall_bcs(), component_axis=0, nu=0.1, dt=0.01, theta=1.0)
    base.update(kwargs)
    with pytest.raises(DiffusionSystemError):
        VelocityDiffusionSystem(**base)


# --------------------------------------------------------------------------
# Consistency against matrix-free operators.velocity_laplacian
# --------------------------------------------------------------------------

@pytest.mark.parametrize("theta", [1.0, 0.5])
@pytest.mark.parametrize("bcs_factory", [wall_bcs, periodic_bcs])
@pytest.mark.parametrize("axis", [0, 1, 2])
def test_diffusion_step_matches_matrix_free_theta_scheme(bcs_factory, theta, axis) -> None:
    m = mesh(1)
    bcs = bcs_factory()
    nu, dt = 0.1, 0.01
    u_n_full = random_full_velocity(m, bcs, seed=axis * 10 + int(theta * 100))

    system = VelocityDiffusionSystem(m, bcs, axis, nu, dt, theta)
    u_star_comp, diag = system.solve(u_n_full.components()[axis])
    assert diag.converged and diag.finite

    u_star_full = VelocityField(
        u=u_n_full.u if axis != 0 else u_star_comp,
        v=u_n_full.v if axis != 1 else u_star_comp,
        w=u_n_full.w if axis != 2 else u_star_comp,
    )
    apply_velocity_bc(u_star_full, bcs)

    lap_star = velocity_laplacian(u_star_full, m).components()[axis]
    lap_n = velocity_laplacian(u_n_full, m).components()[axis]
    lhs = (u_star_full.components()[axis].interior - u_n_full.components()[axis].interior) / dt
    rhs = nu * (theta * lap_star.interior + (1.0 - theta) * lap_n.interior)
    np.testing.assert_allclose(lhs, rhs, atol=1e-9)


def test_periodic_duplicate_synchronized_after_diffusion() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_n_full = random_full_velocity(m, bcs, seed=99)
    system = VelocityDiffusionSystem(m, bcs, 1, nu=0.05, dt=0.02, theta=0.5)
    v_star, diag = system.solve(u_n_full.v)
    np.testing.assert_allclose(v_star.interior[:, 0, :], v_star.interior[:, -1, :], atol=1e-10)


# --------------------------------------------------------------------------
# Boundary targets: no-slip, moving wall (velocity_inlet), pressure_outlet
# --------------------------------------------------------------------------

def test_no_slip_boundary_relaxes_toward_zero() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    u_n_full = random_full_velocity(m, bcs, seed=5)
    system = VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=1.0)
    u_star, diag = system.solve(u_n_full.u)
    assert np.max(np.abs(u_star.interior[0, :, :])) < 1e-10
    assert np.max(np.abs(u_star.interior[-1, :, :])) < 1e-10


def test_moving_wall_tangential_pin() -> None:
    m = mesh(1)
    lid_speed = 2.5
    lid = fbc("velocity_inlet", velocity_value=(lid_speed, 0.0, 0.0))
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=lid, z_min=w, z_max=w)
    u_n_full = random_full_velocity(m, bcs, seed=6)
    system = VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=1.0)
    u_star, diag = system.solve(u_n_full.u)
    # tangential ghost mirror: ghost = 2*lid_speed - interior, at the y_max boundary
    ng = m.n_ghost
    interior_adjacent = u_star.data[ng:-ng, -ng - 1, ng:-ng]
    # solve() only returns interior; refill ghosts via apply_velocity_bc on a full field
    full = VelocityField(u=u_star, v=u_n_full.v, w=u_n_full.w)
    apply_velocity_bc(full, bcs)
    ghost = full.u.data[ng:-ng, -ng, ng:-ng]
    np.testing.assert_allclose(ghost, 2.0 * lid_speed - interior_adjacent, atol=1e-10)


def test_free_slip_tangential_neumann_like() -> None:
    m = mesh(1)
    slip = fbc("free_slip")
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=w, x_max=w, y_min=slip, y_max=slip, z_min=w, z_max=w)
    u_n_full = random_full_velocity(m, bcs, seed=9)
    system = VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=1.0)
    u_star, diag = system.solve(u_n_full.u)
    assert diag.converged

    full = VelocityField(u=u_star, v=u_n_full.v, w=u_n_full.w)
    apply_velocity_bc(full, bcs)
    lap = velocity_laplacian(full, m).u
    # cross-check against matrix-free formula, exercising the Neumann-like
    # (free_slip) tangential branch specifically
    lhs = (u_star.interior - u_n_full.u.interior) / 0.01
    rhs = 0.1 * lap.interior
    np.testing.assert_allclose(lhs, rhs, atol=1e-9)


def test_pressure_outlet_zero_gradient_linkage() -> None:
    m = mesh(1)
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    inlet = fbc("velocity_inlet", velocity_value=(1.0, 0.0, 0.0))
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=inlet, x_max=outlet, y_min=w, y_max=w, z_min=w, z_max=w)
    u_n_full = random_full_velocity(m, bcs, seed=7)
    system = VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=1.0)
    u_star, diag = system.solve(u_n_full.u)
    # outlet: boundary face == adjacent interior (zero-gradient), not clamped to a target
    np.testing.assert_allclose(u_star.interior[-1, :, :], u_star.interior[-2, :, :], atol=1e-10)
    np.testing.assert_allclose(u_star.interior[0, :, :], 1.0, atol=1e-10)


# --------------------------------------------------------------------------
# Matrix/factorization reuse
# --------------------------------------------------------------------------

def test_matrix_and_factorization_reused_across_solves() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    system = VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=1.0)
    matrix_id = id(system.matrix)
    lu_id = id(system._lu)
    assembly_time = system.assembly_time

    rng = np.random.default_rng(8)
    u = FaceField.zeros(m, normal_axis=0)
    for _ in range(3):
        u.interior = rng.uniform(-1.0, 1.0, size=u.interior.shape)
        u, diag = system.solve(u)
        assert id(system.matrix) == matrix_id
        assert id(system._lu) == lu_id
        assert system.assembly_time == assembly_time


def test_mesh_bcs_shape_properties() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    system = VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=1.0)
    assert system.mesh is m
    assert system.bcs is bcs
    assert system.shape == system.matrix.shape
    assert system.shape == ((NX + 1) * NY * NZ, (NX + 1) * NY * NZ)


def test_no_dense_matrix() -> None:
    import scipy.sparse as sp

    m = mesh(1)
    system = VelocityDiffusionSystem(m, wall_bcs(), 0, nu=0.1, dt=0.01, theta=1.0)
    assert sp.issparse(system.matrix)
    assert system.matrix.format == "csr"


# --------------------------------------------------------------------------
# Solve API validation, NaN/Inf detection
# --------------------------------------------------------------------------

def test_solve_rejects_wrong_component_axis() -> None:
    m = mesh(1)
    system = VelocityDiffusionSystem(m, wall_bcs(), 0, nu=0.1, dt=0.01, theta=1.0)
    wrong = FaceField.zeros(m, normal_axis=1)
    with pytest.raises(DiffusionSystemError):
        system.solve(wrong)


def test_solve_rejects_mismatched_shape() -> None:
    m1 = mesh(1)
    m2 = StructuredMesh3D(nx=NX + 1, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    system = VelocityDiffusionSystem(m1, wall_bcs(), 0, nu=0.1, dt=0.01, theta=1.0)
    wrong = FaceField.zeros(m2, normal_axis=0)
    with pytest.raises(DiffusionSystemError):
        system.solve(wrong)


def test_diagnostics_report_finite_true_for_normal_solve() -> None:
    m = mesh(1)
    system = VelocityDiffusionSystem(m, wall_bcs(), 0, nu=0.1, dt=0.01, theta=1.0)
    u = FaceField.zeros(m, normal_axis=0)
    u.interior[:] = 0.5
    _, diag = system.solve(u)
    assert diag.finite
    assert diag.converged
    assert diag.method == "direct"
    assert diag.iterations == 1


@pytest.mark.parametrize("n_ghost", [1, 2])
def test_works_at_ng1_and_ng2(n_ghost: int) -> None:
    m = mesh(n_ghost)
    bcs = wall_bcs()
    system = VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=1.0)
    u = FaceField.zeros(m, normal_axis=0)
    assert u.n_ghost == n_ghost
    _, diag = system.solve(u)
    assert diag.converged
