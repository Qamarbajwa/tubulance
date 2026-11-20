"""Milestone 8 Part 20: failure handling for the incremental/rotational
pressure-correction machinery. Failures must be explicit, never silent.
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
from navier3d.fields import FlowState, ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.projection import ProjectionError, project_incremental
from navier3d.time_integrators import IntegrationError, ThetaSchemeIntegrator, run

NX, NY, NZ = 6, 7, 5


def mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)


def fbc(velocity, pressure="neumann"):
    return FaceBoundaryCondition(velocity_type=VelocityBCType(velocity), pressure_type=PressureBCType(pressure))


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def random_state(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> FlowState:
    rng = np.random.default_rng(seed)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.5, 0.5, size=comp.interior.shape)
    apply_velocity_bc(state.velocity, bcs)
    return state


# --------------------------------------------------------------------------
# Invalid projection_method
# --------------------------------------------------------------------------

def test_invalid_projection_method_rejected() -> None:
    m = mesh()
    bcs = periodic_bcs()
    with pytest.raises(ValueError, match="projection_method"):
        ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, projection_method="not_a_method")


# --------------------------------------------------------------------------
# rotational requires nu
# --------------------------------------------------------------------------

def test_rotational_without_nu_rejected() -> None:
    m = mesh()
    bcs = periodic_bcs()
    u_star = VelocityField.zeros(m)
    apply_velocity_bc(u_star, bcs)
    p_prev = ScalarField.zeros(m)
    with pytest.raises(ValueError, match="nu"):
        project_incremental(u_star, p_prev, bcs, m, rho=1.0, dt=0.01, rotational=True, nu=None)


# --------------------------------------------------------------------------
# phi solve non-convergence
# --------------------------------------------------------------------------

def test_phi_non_convergence_raises_projection_error() -> None:
    m = mesh()
    bcs = periodic_bcs()
    rng = np.random.default_rng(1)
    u_star = VelocityField.zeros(m)
    for c in u_star.components():
        c.interior = rng.uniform(-1.0, 1.0, size=c.interior.shape)
    apply_velocity_bc(u_star, bcs)
    p_prev = ScalarField.zeros(m)
    with pytest.raises(ProjectionError, match="did not converge"):
        project_incremental(
            u_star, p_prev, bcs, m, rho=1.0, dt=0.01,
            solver="cg", tol=1e-14, max_iterations=1, rhs_compatibility="mean_removal",
        )


def test_integrator_phi_non_convergence_raises_integration_error() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
        projection_method="incremental",
        pressure_kwargs=dict(solver="cg", tol=1e-14, max_iterations=1, rhs_compatibility="mean_removal"),
    )
    state = random_state(m, bcs, seed=2)
    with pytest.raises(IntegrationError, match="projection failed"):
        integrator.step(state)


# --------------------------------------------------------------------------
# NaN/Inf pressure increment
# --------------------------------------------------------------------------

def test_nonfinite_forcing_with_incremental_method_raises() -> None:
    m = mesh()
    bcs = periodic_bcs()

    def bad_forcing(t):
        f = VelocityField.zeros(m)
        f.u.interior[:] = np.nan
        return f

    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, forcing=bad_forcing,
        projection_method="rotational",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = FlowState.zeros(m)
    with pytest.raises(IntegrationError, match="non-finite"):
        integrator.step(state)


# --------------------------------------------------------------------------
# Missing / incompatible pressure history
# --------------------------------------------------------------------------

def test_first_step_incremental_uses_zero_initial_pressure_without_error() -> None:
    """A fresh FlowState.zeros() has pressure=0 -- this is a valid,
    well-defined p^0 (not "missing" history), so the first incremental
    step must succeed normally, not raise."""
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
        projection_method="incremental",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = random_state(m, bcs, seed=3)
    new_state, diag = integrator.step(state)  # must not raise
    assert diag.max_divergence < 1e-6


def test_restore_history_with_wrong_mesh_shape_field_raises_downstream() -> None:
    """An IntegratorHistory built for one mesh, restored into an
    integrator for an incompatible mesh, must fail explicitly (via the
    normal shape-mismatch checks already enforced by convection.py/
    diffusion.py) the first time it's actually used, not silently
    produce wrong results."""
    m_small = StructuredMesh3D(nx=4, ny=4, nz=4, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)
    m_big = mesh()
    bcs_small = periodic_bcs()
    bcs_big = periodic_bcs()

    small_integrator = ThetaSchemeIntegrator(
        m_small, bcs_small, rho=1.0, nu=0.1, dt=0.01, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state_small = random_state(m_small, bcs_small, seed=4)
    small_integrator.step(state_small)
    incompatible_history = small_integrator.history

    big_integrator = ThetaSchemeIntegrator(
        m_big, bcs_big, rho=1.0, nu=0.1, dt=0.01, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
        initial_history=incompatible_history,
    )
    state_big = random_state(m_big, bcs_big, seed=5)
    with pytest.raises(Exception):  # navier3d.convection.ConvectionError (shape mismatch)
        big_integrator.step(state_big)


# --------------------------------------------------------------------------
# Bounded diffusion cache never silently unbounded
# --------------------------------------------------------------------------

def test_diffusion_cache_max_size_rejects_invalid_value() -> None:
    m = mesh()
    bcs = periodic_bcs()
    with pytest.raises(ValueError, match="diffusion_cache_max_size"):
        ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, diffusion_cache_max_size=0)
