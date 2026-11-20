"""Tests for navier3d.time_integrators: ThetaSchemeIntegrator, run().

Rest-state (I) and constant-flow (J) preservation, and the algebraic
matrix-reuse guarantee, live here; the physics verification cases (A-H)
live in test_stokes_verification.py.
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
from navier3d.fields import FlowState, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import IntegrationError, StepDiagnostics, ThetaSchemeIntegrator, run

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


def periodic_kwargs() -> dict:
    return dict(rhs_compatibility="mean_removal", tol=1e-12)


def wall_kwargs() -> dict:
    return dict(solver="direct", null_space_strategy="pin_cell")


# --------------------------------------------------------------------------
# I. Rest-state preservation
# --------------------------------------------------------------------------

@pytest.mark.parametrize("theta", [1.0, 0.5])
def test_rest_state_preserved_exactly(theta: float) -> None:
    m = mesh(1)
    bcs = wall_bcs()
    integrator = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=theta, pressure_kwargs=wall_kwargs())
    state = FlowState.zeros(m)
    final_state, history = run(integrator, state, n_steps=50)
    for comp in final_state.velocity.components():
        assert np.max(np.abs(comp.data)) == 0.0
    assert np.max(np.abs(final_state.pressure.data)) == 0.0
    for h in history:
        assert h.max_velocity == 0.0
        assert h.kinetic_energy == 0.0


# --------------------------------------------------------------------------
# J. Constant-flow preservation (periodic)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("theta", [1.0, 0.5])
def test_constant_flow_preserved_to_roundoff(theta: float) -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    state = FlowState.zeros(m)
    state.velocity.u.data[:] = 2.0
    state.velocity.v.data[:] = -1.0
    state.velocity.w.data[:] = 0.5
    integrator = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=theta, pressure_kwargs=periodic_kwargs())
    final_state, history = run(integrator, state, n_steps=30)
    np.testing.assert_allclose(final_state.velocity.u.interior, 2.0, atol=1e-8)
    np.testing.assert_allclose(final_state.velocity.v.interior, -1.0, atol=1e-8)
    np.testing.assert_allclose(final_state.velocity.w.interior, 0.5, atol=1e-8)
    assert history[-1].max_divergence < 1e-8


# --------------------------------------------------------------------------
# Matrix reuse across steps
# --------------------------------------------------------------------------

def test_diffusion_and_pressure_matrices_reused_across_steps() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    integrator = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=1.0, pressure_kwargs=wall_kwargs())
    diffusion_matrix_ids = [id(s.matrix) for s in integrator.diffusion_systems]

    rng = np.random.default_rng(0)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.3, 0.3, size=comp.interior.shape)
    apply_velocity_bc(state.velocity, bcs)

    pressure_matrix_id = None
    for _ in range(5):
        state, diag = integrator.step(state)
        assert [id(s.matrix) for s in integrator.diffusion_systems] == diffusion_matrix_ids
        if pressure_matrix_id is None:
            pressure_matrix_id = id(integrator.pressure_system.matrix)
        else:
            assert id(integrator.pressure_system.matrix) == pressure_matrix_id


# --------------------------------------------------------------------------
# Diagnostics content
# --------------------------------------------------------------------------

def test_step_diagnostics_fields() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    integrator = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=1.0, pressure_kwargs=wall_kwargs())
    rng = np.random.default_rng(1)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.3, 0.3, size=comp.interior.shape)
    apply_velocity_bc(state.velocity, bcs)

    new_state, diag = integrator.step(state)
    assert isinstance(diag, StepDiagnostics)
    assert diag.time == pytest.approx(0.01)
    assert diag.dt == pytest.approx(0.01)
    assert diag.step == 1
    assert diag.max_velocity >= 0.0
    assert diag.kinetic_energy >= 0.0
    assert diag.max_divergence < 1e-6
    assert diag.l2_divergence < 1e-6
    assert len(diag.diffusion_diagnostics) == 3
    for d in diag.diffusion_diagnostics:
        assert d.converged and d.finite
    assert diag.pressure_diagnostics.converged
    assert diag.elapsed_time >= 0.0


# --------------------------------------------------------------------------
# Forcing callable
# --------------------------------------------------------------------------

def test_time_dependent_forcing_is_called_at_theta_weighted_time() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    calls = []

    def forcing(t):
        calls.append(t)
        f = VelocityField.zeros(m)
        f.u.data[:] = 1.0
        return f

    dt, theta = 0.02, 0.5
    integrator = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=dt, theta=theta, forcing=forcing, pressure_kwargs=periodic_kwargs())
    state = FlowState.zeros(m)
    state, diag = integrator.step(state)
    assert calls == [pytest.approx(0.0 + theta * dt)]
    # forcing actually influenced the velocity (not silently ignored)
    assert np.max(np.abs(state.velocity.u.interior)) > 0.0


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------

def test_invalid_construction_rejected() -> None:
    m = mesh(1)
    with pytest.raises(ValueError):
        ThetaSchemeIntegrator(m, wall_bcs(), rho=-1.0, nu=0.1, dt=0.01)
    with pytest.raises(ValueError):
        ThetaSchemeIntegrator(m, wall_bcs(), rho=1.0, nu=0.0, dt=0.01)
    with pytest.raises(ValueError):
        ThetaSchemeIntegrator(m, wall_bcs(), rho=1.0, nu=0.1, dt=0.0)
    with pytest.raises(ValueError):
        ThetaSchemeIntegrator(m, wall_bcs(), rho=1.0, nu=0.1, dt=0.01, convection_scheme="not_a_scheme")


def test_diffusion_max_iterations_failure_raises_integration_error() -> None:
    """A pressure solve that cannot converge (absurdly low max_iterations)
    must raise, not silently return a bogus step."""
    m = mesh(1)
    bcs = wall_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=1.0,
        pressure_kwargs=dict(solver="cg", null_space_strategy="pin_cell", tol=1e-14, max_iterations=1),
    )
    rng = np.random.default_rng(2)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.5, 0.5, size=comp.interior.shape)
    apply_velocity_bc(state.velocity, bcs)
    with pytest.raises(IntegrationError):
        integrator.step(state)


# --------------------------------------------------------------------------
# run() loop and callback
# --------------------------------------------------------------------------

def test_nonfinite_forcing_raises_integration_error() -> None:
    """A forcing callable that produces NaN must be caught by the diffusion
    solve's finite check, not silently propagated."""
    m = mesh(1)
    bcs = periodic_bcs()

    def bad_forcing(t):
        f = VelocityField.zeros(m)
        f.u.data[:] = np.nan
        return f

    integrator = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=1.0, forcing=bad_forcing, pressure_kwargs=periodic_kwargs())
    state = FlowState.zeros(m)
    with pytest.raises(IntegrationError):
        integrator.step(state)


def test_run_returns_history_and_invokes_callback() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=1.0, pressure_kwargs=periodic_kwargs())
    state = FlowState.zeros(m)
    seen_steps = []
    final_state, history = run(integrator, state, n_steps=4, callback=lambda s, d: seen_steps.append(s.step))
    assert len(history) == 4
    assert seen_steps == [1, 2, 3, 4]
    assert final_state.step == 4
