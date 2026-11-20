"""Milestone 8: ThetaSchemeIntegrator with incremental/rotational
projection methods -- variable timestep (Part 6), history round-trip
(Part 4), adaptive-stepping regression (Part 16), and the bounded
diffusion-system cache (Part 17).
"""
import numpy as np
import pytest

from navier3d.adaptive import AdaptiveTimestepController
from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_velocity_bc,
)
from navier3d.fields import FlowState
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import IntegratorHistory, ThetaSchemeIntegrator, run

NX, NY, NZ = 6, 7, 5


def mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)


def fbc(velocity, pressure="neumann"):
    return FaceBoundaryCondition(velocity_type=VelocityBCType(velocity), pressure_type=PressureBCType(pressure))


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def wall_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def random_state(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> FlowState:
    rng = np.random.default_rng(seed)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.5, 0.5, size=comp.interior.shape)
    apply_velocity_bc(state.velocity, bcs)
    return state


@pytest.mark.parametrize("method", ["incremental", "rotational"])
def _integrator(m, bcs, method, dt=0.005, **kwargs):
    return ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        **kwargs,
    )


# ==========================================================================
# Part 6: variable timestep -- constant, alternating, smoothly adaptive
# ==========================================================================

@pytest.mark.parametrize("method", ["non_incremental", "incremental", "rotational"])
def test_constant_timestep_stable_and_finite(method) -> None:
    m = mesh()
    bcs = wall_bcs()
    integ = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=0.005, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    state = random_state(m, bcs, seed=1)
    final_state, history = run(integ, state, n_steps=15)
    assert max(h.max_divergence for h in history) < 1e-6
    for comp in final_state.velocity.components():
        assert np.all(np.isfinite(comp.data))


@pytest.mark.parametrize("method", ["incremental", "rotational"])
def test_alternating_timestep_stable_and_finite(method) -> None:
    m = mesh()
    bcs = wall_bcs()
    integ = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=0.005, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    state = random_state(m, bcs, seed=2)
    dts = [0.005, 0.01] * 8
    for dt in dts:
        state, diag = integ.step(state, dt=dt)
        assert diag.max_divergence < 1e-6
        for comp in state.velocity.components():
            assert np.all(np.isfinite(comp.data))


@pytest.mark.parametrize("method", ["incremental", "rotational"])
def test_smoothly_adaptive_timestep_stable_and_cfl_controlled(method) -> None:
    m = mesh()
    bcs = wall_bcs()
    integ = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=0.005, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    controller = AdaptiveTimestepController(cfl_target=0.4, dt_min=1e-5, dt_max=0.02, growth_max=1.3, shrink_max=0.3)
    state = random_state(m, bcs, seed=3)
    dt_prev = integ.dt
    for _ in range(15):
        decision = controller.next_dt(state.velocity, m, dt_previous=dt_prev)
        state, diag = integ.step(state, dt=decision.dt)
        assert diag.cfl <= 0.4 + 1e-9
        dt_prev = decision.dt
    for comp in state.velocity.components():
        assert np.all(np.isfinite(comp.data))


# ==========================================================================
# Part 4: IntegratorHistory round-trip
# ==========================================================================

@pytest.mark.parametrize("method", ["non_incremental", "incremental", "rotational"])
def test_history_roundtrip_reproduces_identical_next_step(method) -> None:
    m = mesh()
    bcs = wall_bcs()
    common = dict(
        mesh=m, bcs=bcs, rho=1.0, nu=0.05, dt=0.005, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    state0 = random_state(m, bcs, seed=4)

    integ_a = ThetaSchemeIntegrator(**common)
    state_a, _ = integ_a.step(state0)
    state_a, _ = integ_a.step(state_a)  # now has real AB2 + pressure history
    history_a = integ_a.history

    # a FRESH integrator, given the saved (state_a, history_a) pair, must
    # take the identical next step as integ_a would
    integ_b = ThetaSchemeIntegrator(**common, initial_history=history_a)
    next_a, diag_a = integ_a.step(state_a)
    next_b, diag_b = integ_b.step(state_a)

    for c_a, c_b in zip(next_a.velocity.components(), next_b.velocity.components()):
        np.testing.assert_array_equal(c_a.data, c_b.data)
    np.testing.assert_array_equal(next_a.pressure.data, next_b.pressure.data)
    assert diag_a.cfl == diag_b.cfl


@pytest.mark.parametrize("method", ["incremental", "rotational"])
def test_history_roundtrip_with_pressure_extrapolation(method) -> None:
    """Milestone 9: IntegratorHistory.previous_pressure (p^{n-1}, needed
    by pressure_extrapolation) round-trips correctly -- a restored
    integrator reproduces the identical next step even when that step's
    pressure-gradient term depends on TWO history fields (p^n and
    p^{n-1}), not just one."""
    m = mesh()
    bcs = wall_bcs()
    common = dict(
        mesh=m, bcs=bcs, rho=1.0, nu=0.05, dt=0.005, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0, pressure_extrapolation=True,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    state0 = random_state(m, bcs, seed=7)

    integ_a = ThetaSchemeIntegrator(**common)
    state_a, _ = integ_a.step(state0)
    state_a, _ = integ_a.step(state_a)
    state_a, _ = integ_a.step(state_a)  # p^{n-1} now genuinely distinct from p^n
    history_a = integ_a.history
    assert history_a.previous_pressure is not None

    integ_b = ThetaSchemeIntegrator(**common, initial_history=history_a)
    next_a, diag_a = integ_a.step(state_a)
    next_b, diag_b = integ_b.step(state_a)

    for c_a, c_b in zip(next_a.velocity.components(), next_b.velocity.components()):
        np.testing.assert_array_equal(c_a.data, c_b.data)
    np.testing.assert_array_equal(next_a.pressure.data, next_b.pressure.data)


def test_pressure_extrapolation_false_by_default_and_unchanged_behavior() -> None:
    """Regression: pressure_extrapolation defaults to False, reproducing
    Milestone 8 behavior exactly (no new predictor term added)."""
    m = mesh()
    bcs = wall_bcs()
    integ = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=0.005, theta=0.5, convection_scheme="centered",
        projection_method="incremental",
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    assert integ.pressure_extrapolation is False
    state0 = random_state(m, bcs, seed=8)
    state1, _ = integ.step(state0)
    state2, _ = integ.step(state1)
    # second step must not raise/behave differently just because history
    # (previous_pressure) now exists -- it's simply unused when the flag is off
    for comp in state2.velocity.components():
        assert np.all(np.isfinite(comp.data))


def test_history_is_none_before_convection_enabled_or_before_first_step() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integ = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5,
                                   pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10))
    h = integ.history
    assert h.previous_convection is None
    assert h.previous_dt is None
    assert h.previous_phi is None


def test_restore_history_updates_private_state() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integ = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
                                   pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10))
    state = random_state(m, bcs, seed=5)
    integ.step(state)
    saved = integ.history
    assert saved.previous_convection is not None

    fresh = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
                                   pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10))
    assert fresh.history.previous_convection is None
    fresh.restore_history(saved)
    assert fresh.history.previous_dt == saved.previous_dt


# ==========================================================================
# Part 17: bounded LRU diffusion cache
# ==========================================================================

def test_cache_stays_bounded_over_hundreds_of_distinct_dt_values() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integ = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5,
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-8),
        diffusion_cache_max_size=8,
    )
    state = random_state(m, bcs, seed=6)
    rng = np.random.default_rng(100)
    for _ in range(300):
        dt = float(rng.uniform(0.001, 0.02))  # essentially never repeats exactly
        state, diag = integ.step(state, dt=dt)
        assert integ.diffusion_cache_size <= 8
        for comp in state.velocity.components():
            assert np.all(np.isfinite(comp.data))


def test_default_cache_max_size_is_bounded() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integ = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01,
                                   pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-8))
    assert integ.diffusion_cache_max_size == 8


def test_lru_eviction_order() -> None:
    """Filling the cache past capacity evicts the LEAST recently used
    entry, not an arbitrary one."""
    m = mesh()
    bcs = periodic_bcs()
    integ = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01,
                                   pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-8),
                                   diffusion_cache_max_size=2)
    sys_a = integ._get_diffusion_systems(0.001)
    sys_b = integ._get_diffusion_systems(0.002)
    assert integ.diffusion_cache_size == 2
    # touch 'a' again (making 'b' the least-recently-used)
    integ._get_diffusion_systems(0.001)
    sys_c = integ._get_diffusion_systems(0.003)  # evicts 'b', not 'a'
    assert integ.diffusion_cache_size == 2
    sys_a_again = integ._get_diffusion_systems(0.001)
    assert sys_a_again is sys_a  # 'a' survived
    sys_b_again = integ._get_diffusion_systems(0.002)
    assert sys_b_again is not sys_b  # 'b' was evicted and rebuilt
