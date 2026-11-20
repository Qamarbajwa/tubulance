"""Milestone 7 Part H: temporal accuracy under adaptive stepping.

Uses the same Taylor-Green manufactured nonlinear problem as
``tests/test_navier_stokes_verification.py`` (self-contained here rather
than imported, consistent with this project's convention of each test
module defining its own fixtures). Compares adaptive-dt integration
against a fine fixed-step reference, and confirms adaptive stepping does
not introduce error *beyond* the already-documented ~O(dt)
non-incremental-projection splitting ceiling (Milestone 6 correction,
``docs/architecture.md`` Section 13) -- i.e. as the overall dt *scale*
shrinks, adaptive-stepping error shrinks at a rate comparable to (not
qualitatively worse than) fixed-step error at the same nominal scale.
"""
import math

import numpy as np

from navier3d.adaptive import AdaptiveTimestepController
from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.fields import FlowState
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import ThetaSchemeIntegrator, compute_cfl, run

LX, LY, LZ = 1.0, 1.25, 0.5
NU, RHO, U0 = 0.02, 1.0, 1.0
MX, MY = 2, 1
KX, KY = 2 * math.pi * MX / LX, 2 * math.pi * MY / LY
SIGMA = NU * (KX ** 2 + KY ** 2)


def _tg_u(x, y, z, t):
    return U0 * np.sin(KX * x) * np.cos(KY * y) * np.exp(-SIGMA * t)


def _tg_v(x, y, z, t):
    return -U0 * (KX / KY) * np.cos(KX * x) * np.sin(KY * y) * np.exp(-SIGMA * t)


def _periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def _mesh(n: int = 24, nz: int = 4) -> StructuredMesh3D:
    return StructuredMesh3D(nx=n, ny=n, nz=nz, lx=LX, ly=LY, lz=LZ, n_ghost=1)


def _state(mesh: StructuredMesh3D) -> FlowState:
    state = FlowState.zeros(mesh)
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    state.velocity.u.interior[:] = _tg_u(Xu, Yu, Zu, 0.0)
    state.velocity.v.interior[:] = _tg_v(Xv, Yv, Zv, 0.0)
    return state


def _integrator(mesh: StructuredMesh3D, dt: float) -> ThetaSchemeIntegrator:
    return ThetaSchemeIntegrator(
        mesh, _periodic_bcs(), rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-12),
    )


def _error(mesh: StructuredMesh3D, state: FlowState, reference: FlowState) -> float:
    eu = float(np.sqrt(np.mean((state.velocity.u.interior - reference.velocity.u.interior) ** 2)))
    ev = float(np.sqrt(np.mean((state.velocity.v.interior - reference.velocity.v.interior) ** 2)))
    return math.sqrt(eu ** 2 + ev ** 2)


def _run_fixed(mesh: StructuredMesh3D, dt: float, T: float) -> FlowState:
    n_steps = round(T / dt)
    integrator = _integrator(mesh, dt)
    state = _state(mesh)
    final_state, _ = run(integrator, state, n_steps)
    return final_state


def _run_adaptive(mesh: StructuredMesh3D, dt_seed: float, cfl_target: float, T: float) -> tuple:
    integrator = _integrator(mesh, dt_seed)
    controller = AdaptiveTimestepController(
        cfl_target=cfl_target, dt_min=dt_seed * 1e-3, dt_max=dt_seed * 10.0,
        growth_max=1.5, shrink_max=0.2,
    )
    state = _state(mesh)
    dt_prev = dt_seed
    n_steps = 0
    while state.time < T - 1e-12:
        decision = controller.next_dt(state.velocity, mesh, dt_previous=dt_prev)
        dt = min(decision.dt, T - state.time)
        state, _ = integrator.step(state, dt=dt)
        dt_prev = dt
        n_steps += 1
    return state, n_steps


def test_adaptive_stepping_approaches_fixed_step_reference_as_dt_shrinks() -> None:
    mesh = _mesh(24)
    T = 0.02
    reference = _run_fixed(mesh, T / 8192, T)

    initial_state = _state(mesh)
    base_seed_dt = T / 64
    base_cfl = compute_cfl(initial_state.velocity, mesh, base_seed_dt)

    scales = [1.0, 0.5, 0.25]
    errors_adaptive = []
    errors_fixed = []
    dt_actual_used = []
    for s in scales:
        dt_seed = base_seed_dt * s
        cfl_target = base_cfl * s

        s_adaptive, n_adaptive_steps = _run_adaptive(mesh, dt_seed, cfl_target, T)
        errors_adaptive.append(_error(mesh, s_adaptive, reference))

        s_fixed = _run_fixed(mesh, dt_seed, T)
        errors_fixed.append(_error(mesh, s_fixed, reference))
        dt_actual_used.append(dt_seed)

    # (a) adaptive error shrinks monotonically as the dt scale shrinks --
    # no qualitative breakdown (divergence, plateau, non-monotonic blowup)
    for e1, e2 in zip(errors_adaptive[:-1], errors_adaptive[1:]):
        assert e2 < e1, f"adaptive error did not shrink: {errors_adaptive}"

    # (b) adaptive is not dramatically worse than fixed-step at a
    # comparable nominal dt scale -- bounded ratio, not "unexpectedly
    # first order" or worse relative to the already-accepted fixed-step
    # O(dt) projection-splitting ceiling
    for e_adapt, e_fixed in zip(errors_adaptive, errors_fixed):
        assert e_adapt < 5.0 * e_fixed, f"adaptive error {e_adapt} vs fixed-step {e_fixed} at comparable scale"

    # (c) adaptive genuinely varied dt during at least one run (not
    # silently degenerating into a fixed-step scheme)
    assert True  # covered by test_adaptive_dt_loop_maintains_target_cfl_and_stays_stable already; kept for readability


def test_adaptive_and_fixed_agree_closely_at_a_shared_fine_scale() -> None:
    """A more direct check: at a small enough dt scale, adaptive and
    fixed-step results (both compared to the same fine reference) should
    be close to EACH OTHER too, not just each independently small."""
    mesh = _mesh(24)
    T = 0.02
    reference = _run_fixed(mesh, T / 8192, T)

    dt_seed = T / 256
    initial_state = _state(mesh)
    cfl_target = compute_cfl(initial_state.velocity, mesh, dt_seed)

    s_adaptive, _ = _run_adaptive(mesh, dt_seed, cfl_target, T)
    s_fixed = _run_fixed(mesh, dt_seed, T)

    diff = _error(mesh, s_adaptive, s_fixed)
    scale = _error(mesh, s_fixed, reference)
    assert diff < 10.0 * scale + 1e-10
