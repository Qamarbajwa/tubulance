"""Milestone 7: matrix/preconditioner reuse+invalidation (Part E), warm
starts (Part D), and adaptive-timestep + variable-step AB2 integration
(Parts F, G, H) at the full ThetaSchemeIntegrator level.
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
from navier3d.fields import FlowState, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import ThetaSchemeIntegrator, run

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


def random_state(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> FlowState:
    rng = np.random.default_rng(seed)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.5, 0.5, size=comp.interior.shape)
    apply_velocity_bc(state.velocity, bcs)
    return state


# ==========================================================================
# Part E: diffusion matrix/preconditioner reuse and invalidation
# ==========================================================================

def test_same_dt_reuses_cached_diffusion_systems() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = random_state(m, bcs, seed=1)
    state, _ = integrator.step(state)
    ids_first = [id(s.matrix) for s in integrator.diffusion_systems]
    assert integrator.diffusion_cache_size == 1

    for _ in range(4):
        state, _ = integrator.step(state)  # dt unchanged every call
        assert [id(s.matrix) for s in integrator.diffusion_systems] == ids_first
        assert integrator.diffusion_cache_size == 1


def test_dt_change_invalidates_and_rebuilds_diffusion_systems() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = random_state(m, bcs, seed=2)
    state, _ = integrator.step(state)
    ids_dt1 = [id(s.matrix) for s in integrator.diffusion_systems]

    state, _ = integrator.step(state, dt=0.02)  # genuinely different dt -> new matrices
    ids_dt2 = [id(s.matrix) for s in integrator.diffusion_systems]
    assert ids_dt2 != ids_dt1
    assert integrator.diffusion_cache_size == 2

    state, _ = integrator.step(state, dt=0.01)  # back to a previously-seen dt -> reused, not rebuilt
    ids_dt1_again = [id(s.matrix) for s in integrator.diffusion_systems]
    assert ids_dt1_again == ids_dt1
    assert integrator.diffusion_cache_size == 2  # no new entry


def test_pressure_bc_values_alone_do_not_invalidate_matrix() -> None:
    """Unchanged from Milestone 5: a spatially-varying but same-TOPOLOGY
    forcing (changing the derived Neumann pressure BC *values* every
    step) reuses the same pressure matrix object."""
    m = mesh()
    bcs = periodic_bcs()

    def forcing(t):
        f = VelocityField.zeros(m)
        f.u.interior[:] = np.sin(t)  # value changes every step
        return f

    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, forcing=forcing,
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = random_state(m, bcs, seed=3)
    state, _ = integrator.step(state)
    matrix_id = id(integrator.pressure_system.matrix)
    for _ in range(3):
        state, _ = integrator.step(state)
        assert id(integrator.pressure_system.matrix) == matrix_id


# ==========================================================================
# Part D: warm starts
# ==========================================================================

def test_warm_start_reduces_pressure_and_diffusion_iterations() -> None:
    m = mesh()
    bcs = periodic_bcs()
    common = dict(
        mesh=m, bcs=bcs, rho=1.0, nu=0.1, dt=0.005, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(solver="cg", rhs_compatibility="mean_removal", tol=1e-11),
        diffusion_kwargs=dict(formulation="spd", solver="cg", rtol=1e-11),
    )
    state0 = random_state(m, bcs, seed=4)

    cold_integrator = ThetaSchemeIntegrator(**common, warm_start=False)
    warm_integrator = ThetaSchemeIntegrator(**common, warm_start=True)

    _, history_cold = run(cold_integrator, state0, n_steps=6)
    _, history_warm = run(warm_integrator, state0, n_steps=6)

    # skip step 1 (no warm-start history yet for either) -- compare the
    # steady-state behavior from step 2 onward, where warm starts should
    # measurably reduce iteration counts on this smoothly-evolving flow
    cold_pressure_iters = sum(h.pressure_diagnostics.iterations for h in history_cold[1:])
    warm_pressure_iters = sum(h.pressure_diagnostics.iterations for h in history_warm[1:])
    cold_diffusion_iters = sum(sum(d.iterations for d in h.diffusion_diagnostics) for h in history_cold[1:])
    warm_diffusion_iters = sum(sum(d.iterations for d in h.diffusion_diagnostics) for h in history_warm[1:])

    assert warm_pressure_iters <= cold_pressure_iters
    assert warm_diffusion_iters <= cold_diffusion_iters
    # and it must not be a NO-OP measured coincidence: at least one of the
    # two should show a strict reduction on this case
    assert warm_pressure_iters < cold_pressure_iters or warm_diffusion_iters < cold_diffusion_iters


def test_warm_start_direct_solver_is_a_documented_noop() -> None:
    """warm_start=True with the default direct solvers must not change
    the result (x0 is accepted but ignored for direct solves)."""
    m = mesh()
    bcs = periodic_bcs()
    state0 = random_state(m, bcs, seed=5)

    cold = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
                                  pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"), warm_start=False)
    warm = ThetaSchemeIntegrator(m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
                                  pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"), warm_start=True)
    state_cold, _ = run(cold, state0, n_steps=3)
    state_warm, _ = run(warm, state0, n_steps=3)
    np.testing.assert_allclose(state_cold.velocity.u.interior, state_warm.velocity.u.interior, atol=1e-12)


# ==========================================================================
# Parts F/G: adaptive dt loop + variable-step AB2 exercised end-to-end
# ==========================================================================

def test_adaptive_dt_loop_maintains_target_cfl_and_stays_stable() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=0.01, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    controller = AdaptiveTimestepController(cfl_target=0.4, dt_min=1e-5, dt_max=0.05, growth_max=1.3, shrink_max=0.3)
    state = random_state(m, bcs, seed=6)

    dt_sequence = []
    cfl_sequence = []
    dt_prev = integrator.dt
    for _ in range(15):
        decision = controller.next_dt(state.velocity, m, dt_previous=dt_prev)
        state, diag = integrator.step(state, dt=decision.dt)
        dt_sequence.append(decision.dt)
        cfl_sequence.append(diag.cfl)
        dt_prev = decision.dt

    assert all(np.isfinite(dt) and dt > 0.0 for dt in dt_sequence)
    assert max(cfl_sequence) <= 0.4 + 1e-9  # CFL controller kept every step at/under target
    assert len(set(np.round(dt_sequence, 10))) >= 2  # dt actually varied (not accidentally constant)
    for comp in state.velocity.components():
        assert np.all(np.isfinite(comp.data))


def test_step_rejects_nonpositive_dt_override() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5,
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = random_state(m, bcs, seed=42)
    with pytest.raises(ValueError):
        integrator.step(state, dt=0.0)
    with pytest.raises(ValueError):
        integrator.step(state, dt=-0.01)


def test_variable_dt_sequence_does_not_raise_and_history_is_finite() -> None:
    """Exercises the variable-step AB2 branch directly with successive
    steps of substantially different dt (the review's explicit request),
    confirming no crash/NaN across a deliberately irregular dt sequence."""
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=0.005, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = random_state(m, bcs, seed=7)
    dts = [0.005, 0.02, 0.002, 0.03, 0.001, 0.015]  # deliberately irregular, r far from 1 repeatedly
    for dt in dts:
        state, diag = integrator.step(state, dt=dt)
        assert diag.dt == pytest.approx(dt)
        for comp in state.velocity.components():
            assert np.all(np.isfinite(comp.data))


# ==========================================================================
# Part I: profiler smoke test at the integrator level
# ==========================================================================

def test_step_profile_and_cumulative_profiler_populated() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = random_state(m, bcs, seed=8)
    _, history = run(integrator, state, n_steps=3)

    for h in history:
        assert h.step_profile["total"] >= 0.0
        assert set(h.step_profile) >= {
            "boundary_conditions", "convection", "diffusion_rhs", "diffusion_solve",
            "pressure_rhs", "pressure_solve", "projection_correction", "diagnostics", "total",
        }

    cumulative = integrator.profiler.totals
    assert cumulative["total"] >= sum(h.step_profile["pressure_solve"] for h in history) - 1e-9
    text = integrator.profiler.format_report()
    assert "pressure_solve" in text
