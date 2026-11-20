"""Milestone 8 Part 5: pressure-increment (phi) BC derivation, verified
distinct from p^n's BC set exactly where the derivation says they must
differ (pressure_outlet), and identical everywhere else.
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
from navier3d.fields import VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.projection import derive_phi_bcs, derive_pressure_bcs

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


def random_full_velocity(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> VelocityField:
    rng = np.random.default_rng(seed)
    velocity = VelocityField.zeros(m)
    for comp in velocity.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(velocity, bcs)
    return velocity


def _grad_scalar(val) -> float:
    return float(np.max(np.abs(np.atleast_1d(val))))


# --------------------------------------------------------------------------
# 1. Periodic: phi and p identical (both pass through unchanged)
# --------------------------------------------------------------------------

def test_periodic_phi_bcs_identical_to_pressure_bcs() -> None:
    m = mesh()
    p = fbc("periodic", "periodic")
    bcs = BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)
    u_star = random_full_velocity(m, bcs, seed=1)

    p_bcs = derive_pressure_bcs(u_star, bcs, rho=1.0, dt=0.01)
    phi_bcs = derive_phi_bcs(u_star, bcs, rho=1.0, dt=0.01)
    for face in ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max"):
        assert p_bcs[face].velocity_type is VelocityBCType.PERIODIC
        assert phi_bcs[face].velocity_type is VelocityBCType.PERIODIC
        assert phi_bcs[face].pressure_type is PressureBCType.PERIODIC


# --------------------------------------------------------------------------
# 2. Stationary no-slip wall: predictor's exact boundary pin makes the
#    derived Neumann g ~0 for BOTH p and phi (verified, not assumed)
# --------------------------------------------------------------------------

def test_stationary_wall_gives_near_zero_neumann_for_both_p_and_phi() -> None:
    m = mesh()
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)
    u_star = random_full_velocity(m, bcs, seed=2)  # apply_velocity_bc pins the normal boundary exactly

    p_bcs = derive_pressure_bcs(u_star, bcs, rho=1.0, dt=0.01)
    phi_bcs = derive_phi_bcs(u_star, bcs, rho=1.0, dt=0.01)
    for face in ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max"):
        # normal-axis interior of the tangential plane (away from the
        # corner-ghost artifacts documented in derive_phi_bcs) is exactly 0
        axis = {"x_min": 0, "x_max": 0, "y_min": 1, "y_max": 1, "z_min": 2, "z_max": 2}[face]
        g_p = p_bcs[face].pressure_gradient_value
        g_phi = phi_bcs[face].pressure_gradient_value
        interior_slice = tuple(slice(1, -1) for _ in range(np.ndim(np.atleast_1d(g_p)))) if np.ndim(g_p) > 0 else ()
        if np.ndim(g_p) > 0:
            np.testing.assert_allclose(np.asarray(g_p)[interior_slice], 0.0, atol=1e-10)
            np.testing.assert_allclose(np.asarray(g_phi)[interior_slice], 0.0, atol=1e-10)
        else:
            assert abs(g_p) < 1e-10
            assert abs(g_phi) < 1e-10


# --------------------------------------------------------------------------
# 3. Moving no-slip wall (velocity_inlet, zero normal component, nonzero
#    tangential speed): same normal-direction g~0 result -- wall motion
#    is purely tangential and doesn't enter the normal Neumann formula
# --------------------------------------------------------------------------

def test_moving_wall_normal_direction_unaffected_by_tangential_speed() -> None:
    m = mesh()
    moving_lid = fbc("velocity_inlet", velocity_value=(2.0, 0.0, 0.0))  # lid moving in x at y_max, normal=y so target=0
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=moving_lid, z_min=w, z_max=w)
    u_star = random_full_velocity(m, bcs, seed=3)

    p_bcs = derive_pressure_bcs(u_star, bcs, rho=1.0, dt=0.01)
    phi_bcs = derive_phi_bcs(u_star, bcs, rho=1.0, dt=0.01)
    g_p = np.asarray(np.atleast_1d(p_bcs.y_max.pressure_gradient_value))
    g_phi = np.asarray(np.atleast_1d(phi_bcs.y_max.pressure_gradient_value))
    np.testing.assert_allclose(g_p[1:-1, 1:-1] if g_p.ndim == 2 else g_p, 0.0, atol=1e-10)
    np.testing.assert_allclose(g_phi[1:-1, 1:-1] if g_phi.ndim == 2 else g_phi, 0.0, atol=1e-10)


# --------------------------------------------------------------------------
# 4. Velocity inlet (nonzero normal target): also g~0, same reasoning
# --------------------------------------------------------------------------

def test_velocity_inlet_gives_near_zero_neumann() -> None:
    m = mesh()
    inlet = fbc("velocity_inlet", velocity_value=(1.5, 0.2, -0.3))
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=3.0)
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=inlet, x_max=outlet, y_min=w, y_max=w, z_min=w, z_max=w)
    u_star = random_full_velocity(m, bcs, seed=4)

    phi_bcs = derive_phi_bcs(u_star, bcs, rho=1.0, dt=0.01)
    g_phi = np.asarray(np.atleast_1d(phi_bcs.x_min.pressure_gradient_value))
    np.testing.assert_allclose(g_phi[1:-1, 1:-1] if g_phi.ndim == 2 else g_phi, 0.0, atol=1e-10)


# --------------------------------------------------------------------------
# 5/6. Pressure outlet: THE key distinguishing case -- phi's Dirichlet
# value must be 0, NOT p's configured pressure_value
# --------------------------------------------------------------------------

@pytest.mark.parametrize("outlet_value", [0.0, 3.0, -7.5])
def test_pressure_outlet_phi_dirichlet_is_always_zero(outlet_value: float) -> None:
    m = mesh()
    inlet = fbc("velocity_inlet", velocity_value=(1.0, 0.0, 0.0))
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=outlet_value)
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=inlet, x_max=outlet, y_min=w, y_max=w, z_min=w, z_max=w)
    u_star = random_full_velocity(m, bcs, seed=5)

    p_bcs = derive_pressure_bcs(u_star, bcs, rho=1.0, dt=0.01)
    phi_bcs = derive_phi_bcs(u_star, bcs, rho=1.0, dt=0.01)

    assert p_bcs.x_max.pressure_type is PressureBCType.DIRICHLET
    assert p_bcs.x_max.pressure_value == pytest.approx(outlet_value)
    assert phi_bcs.x_max.pressure_type is PressureBCType.DIRICHLET
    assert phi_bcs.x_max.pressure_value == pytest.approx(0.0)


def test_mixed_inlet_outlet_only_outlet_face_differs() -> None:
    """Across a full mixed configuration, phi_bcs and p_bcs differ at
    EXACTLY the outlet face's Dirichlet value -- everywhere else (walls,
    inlet) they carry the same (here, ~0) Neumann gradient."""
    m = mesh()
    inlet = fbc("velocity_inlet", velocity_value=(1.0, 0.0, 0.0))
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=5.0)
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=inlet, x_max=outlet, y_min=w, y_max=w, z_min=w, z_max=w)
    u_star = random_full_velocity(m, bcs, seed=6)

    p_bcs = derive_pressure_bcs(u_star, bcs, rho=1.0, dt=0.01)
    phi_bcs = derive_phi_bcs(u_star, bcs, rho=1.0, dt=0.01)

    for face in ("x_min", "y_min", "y_max", "z_min", "z_max"):
        p_g = np.atleast_1d(p_bcs[face].pressure_gradient_value)
        phi_g = np.atleast_1d(phi_bcs[face].pressure_gradient_value)
        np.testing.assert_allclose(phi_g, p_g, atol=1e-12)
    assert p_bcs.x_max.pressure_value != phi_bcs.x_max.pressure_value


# --------------------------------------------------------------------------
# 7. Free-slip / symmetry: identical treatment to no_slip (target=0)
# --------------------------------------------------------------------------

def test_free_slip_and_symmetry_give_near_zero_neumann() -> None:
    m = mesh()
    fs = fbc("free_slip")
    sym = fbc("symmetry")
    bcs = BoundaryConditionSet(x_min=fs, x_max=fs, y_min=sym, y_max=sym, z_min=fs, z_max=fs)
    u_star = random_full_velocity(m, bcs, seed=7)
    phi_bcs = derive_phi_bcs(u_star, bcs, rho=1.0, dt=0.01)
    for face in ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max"):
        g = np.atleast_1d(phi_bcs[face].pressure_gradient_value)
        interior = g[1:-1, 1:-1] if g.ndim == 2 else g
        np.testing.assert_allclose(interior, 0.0, atol=1e-10)
