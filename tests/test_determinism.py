"""Milestone 7 Part M: deterministic behavior.

For a fixed backend, mesh, dt sequence, and initial state, repeated runs
must produce reproducible results -- bitwise, in fact, for this pure
NumPy/SciPy CPU pipeline (no threading nondeterminism, no random
initial guesses in any solver path here: Jacobi/AMG preconditioners and
CG/BiCGSTAB/GMRES are themselves deterministic given identical inputs).
This is checked directly rather than merely assumed. Bitwise equality is
NOT required (and not tested) across *different* backends/solvers or
hardware -- only within one fixed configuration, per the review.
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
from navier3d.fields import FlowState
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import ThetaSchemeIntegrator, run

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


@pytest.mark.parametrize("pressure_kwargs,diffusion_kwargs", [
    (dict(solver="direct", null_space_strategy="pin_cell"), dict(formulation="pinned", solver="direct")),
    (dict(solver="cg", null_space_strategy="zero_mean", rhs_compatibility="mean_removal", tol=1e-10),
     dict(formulation="spd", solver="cg", rtol=1e-10)),
])
def test_repeated_runs_are_bitwise_identical(pressure_kwargs, diffusion_kwargs) -> None:
    m = mesh()
    bcs = periodic_bcs()

    def build_and_run():
        integrator = ThetaSchemeIntegrator(
            m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
            pressure_kwargs=pressure_kwargs, diffusion_kwargs=diffusion_kwargs,
        )
        state = random_state(m, bcs, seed=42)
        final_state, history = run(integrator, state, n_steps=5)
        return final_state, history

    state_a, history_a = build_and_run()
    state_b, history_b = build_and_run()

    for comp_a, comp_b in zip(state_a.velocity.components(), state_b.velocity.components()):
        np.testing.assert_array_equal(comp_a.data, comp_b.data)
    np.testing.assert_array_equal(state_a.pressure.data, state_b.pressure.data)
    assert [h.cfl for h in history_a] == [h.cfl for h in history_b]
    assert [h.pressure_diagnostics.iterations for h in history_a] == [h.pressure_diagnostics.iterations for h in history_b]


def test_adaptive_dt_sequence_is_reproducible() -> None:
    from navier3d.adaptive import AdaptiveTimestepController

    m = mesh()
    bcs = periodic_bcs()

    def build_and_run():
        integrator = ThetaSchemeIntegrator(
            m, bcs, rho=1.0, nu=0.05, dt=0.01, theta=0.5, convection_scheme="centered",
            pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
        )
        controller = AdaptiveTimestepController(cfl_target=0.4, dt_min=1e-5, dt_max=0.05, growth_max=1.3, shrink_max=0.3)
        state = random_state(m, bcs, seed=7)
        dt_prev = integrator.dt
        dts = []
        for _ in range(6):
            decision = controller.next_dt(state.velocity, m, dt_previous=dt_prev)
            state, diag = integrator.step(state, dt=decision.dt)
            dts.append(decision.dt)
            dt_prev = decision.dt
        return dts, state

    dts_a, state_a = build_and_run()
    dts_b, state_b = build_and_run()
    assert dts_a == dts_b
    np.testing.assert_array_equal(state_a.velocity.u.data, state_b.velocity.u.data)
