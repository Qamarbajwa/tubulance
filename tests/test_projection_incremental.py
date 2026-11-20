"""Milestone 8 Parts 2/3/14/15: project_incremental (incremental and
rotational pressure correction) at the projection.py level -- divergence-
free correction, internal consistency between the two variants, matrix
reuse, and warm starts.
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
from navier3d.projection import project, project_incremental

NX, NY, NZ = 6, 7, 5


def mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)


def fbc(velocity, pressure="neumann", velocity_value=None, pressure_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
    )


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def wall_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def channel_bcs() -> BoundaryConditionSet:
    inlet = fbc("velocity_inlet", velocity_value=(1.2, 0.1, -0.2))
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=2.0)
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=inlet, x_max=outlet, y_min=w, y_max=w, z_min=w, z_max=w)


def random_full_velocity(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> VelocityField:
    rng = np.random.default_rng(seed)
    velocity = VelocityField.zeros(m)
    for comp in velocity.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(velocity, bcs)
    return velocity


def random_pressure(m: StructuredMesh3D, seed: int) -> ScalarField:
    rng = np.random.default_rng(seed)
    p = ScalarField.zeros(m)
    p.interior = rng.uniform(-1.0, 1.0, size=p.interior.shape)
    return p


# --------------------------------------------------------------------------
# Divergence-free correction, both variants, across BC types
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bcs_factory", [periodic_bcs, wall_bcs, channel_bcs])
@pytest.mark.parametrize("rotational", [False, True])
def test_incremental_correction_is_divergence_free(bcs_factory, rotational: bool) -> None:
    m = mesh()
    bcs = bcs_factory()
    u_star = random_full_velocity(m, bcs, seed=1)
    p_prev = random_pressure(m, seed=2)
    result = project_incremental(
        u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=rotational, nu=0.1, chi=1.0,
        solver="direct", null_space_strategy="pin_cell",
    )
    assert result.max_divergence_after < 1e-9
    assert result.phi is not None
    assert result.phi_diagnostics.converged


# --------------------------------------------------------------------------
# Internal consistency: velocity correction depends ONLY on phi, so
# incremental and rotational must produce IDENTICAL velocity (only the
# pressure update differs)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bcs_factory", [periodic_bcs, wall_bcs, channel_bcs])
def test_incremental_and_rotational_velocity_identical(bcs_factory) -> None:
    m = mesh()
    bcs = bcs_factory()
    u_star = random_full_velocity(m, bcs, seed=3)
    p_prev = random_pressure(m, seed=4)
    r_inc = project_incremental(u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=False,
                                 solver="direct", null_space_strategy="pin_cell")
    r_rot = project_incremental(u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=True, nu=0.1, chi=1.0,
                                 solver="direct", null_space_strategy="pin_cell")
    for c_inc, c_rot in zip(r_inc.velocity.components(), r_rot.velocity.components()):
        np.testing.assert_allclose(c_inc.interior, c_rot.interior, atol=1e-12)
    # but pressure genuinely differs (rotational term is nonzero for a
    # generic divergent u_star)
    assert not np.allclose(r_inc.pressure.interior, r_rot.pressure.interior, atol=1e-10)


def test_rotational_pressure_matches_incremental_plus_correction_term() -> None:
    """Directly verifies the rotational formula
    p^{n+1} = p^n + phi - chi*rho*nu*D_h(u_star)."""
    from navier3d import operators
    m = mesh()
    bcs = wall_bcs()
    u_star = random_full_velocity(m, bcs, seed=5)
    p_prev = random_pressure(m, seed=6)
    rho, nu, chi = 1.3, 0.2, 1.0
    r_inc = project_incremental(u_star, p_prev, bcs, m, rho=rho, dt=0.01, rotational=False,
                                 solver="direct", null_space_strategy="pin_cell")
    r_rot = project_incremental(u_star, p_prev, bcs, m, rho=rho, dt=0.01, rotational=True, nu=nu, chi=chi,
                                 solver="direct", null_space_strategy="pin_cell")
    div_before = operators.divergence(u_star, m)
    expected = r_inc.pressure.interior - chi * rho * nu * div_before.interior
    np.testing.assert_allclose(r_rot.pressure.interior, expected, atol=1e-10)


@pytest.mark.parametrize("chi", [0.5, 1.0, 2.0])
def test_chi_scales_rotational_correction_linearly(chi: float) -> None:
    m = mesh()
    bcs = wall_bcs()
    u_star = random_full_velocity(m, bcs, seed=7)
    p_prev = random_pressure(m, seed=8)
    r_inc = project_incremental(u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=False,
                                 solver="direct", null_space_strategy="pin_cell")
    r_rot = project_incremental(u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=True, nu=0.1, chi=chi,
                                 solver="direct", null_space_strategy="pin_cell")
    diff = r_inc.pressure.interior - r_rot.pressure.interior
    from navier3d import operators
    div_before = operators.divergence(u_star, m)
    np.testing.assert_allclose(diff, chi * 1.0 * 0.1 * div_before.interior, atol=1e-10)


# --------------------------------------------------------------------------
# Part 14: pressure-system reuse (topology unaffected by incremental use)
# --------------------------------------------------------------------------

def test_pressure_system_reused_across_incremental_calls() -> None:
    m = mesh()
    bcs = wall_bcs()
    u_star1 = random_full_velocity(m, bcs, seed=9)
    p1 = random_pressure(m, seed=10)
    r1 = project_incremental(u_star1, p1, bcs, m, rho=1.0, dt=0.01, rotational=False,
                              solver="direct", null_space_strategy="pin_cell")
    matrix_id = id(r1.pressure_system.matrix)

    u_star2 = random_full_velocity(m, bcs, seed=11)
    p2 = r1.pressure
    r2 = project_incremental(u_star2, p2, bcs, m, rho=1.0, dt=0.01, rotational=False,
                              pressure_system=r1.pressure_system)
    assert id(r2.pressure_system.matrix) == matrix_id


def test_non_incremental_and_incremental_share_matrix_topology() -> None:
    """The phi system and the non-incremental p system have the SAME
    topology (derive_phi_bcs only changes a Dirichlet VALUE) -- a system
    built for one can be reused (update_bcs) by the other without a
    PressureSystemError."""
    m = mesh()
    bcs = channel_bcs()
    u_star = random_full_velocity(m, bcs, seed=12)
    p_prev = random_pressure(m, seed=13)

    r_noninc = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="direct")
    matrix_id = id(r_noninc.pressure_system.matrix)
    r_inc = project_incremental(u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=False,
                                 pressure_system=r_noninc.pressure_system)
    assert id(r_inc.pressure_system.matrix) == matrix_id


# --------------------------------------------------------------------------
# Part 15: warm starts for phi -- measured, not assumed
# --------------------------------------------------------------------------

def test_phi_warm_start_reduces_iterations() -> None:
    m = mesh()
    bcs = wall_bcs()
    u_star = random_full_velocity(m, bcs, seed=14)
    p_prev = random_pressure(m, seed=15)

    r_cold = project_incremental(
        u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=False,
        solver="cg", null_space_strategy="pin_cell", tol=1e-11,
    )
    r_warm = project_incremental(
        u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=False,
        solver="cg", null_space_strategy="pin_cell", tol=1e-11, phi_x0=r_cold.phi,
    )
    assert r_warm.phi_diagnostics.converged
    np.testing.assert_allclose(r_warm.phi.interior, r_cold.phi.interior, atol=1e-8)
    assert r_warm.phi_diagnostics.iterations <= r_cold.phi_diagnostics.iterations
