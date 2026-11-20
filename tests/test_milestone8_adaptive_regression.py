"""Milestone 8 Part 16: adaptive-stepping regression with the new
projection methods -- CFL stays controlled, variable-step AB2 stays
correct, pressure history survives dt changes, and adaptive/fixed-step
solutions converge toward the same result.
"""
import math

import numpy as np

from navier3d.adaptive import AdaptiveTimestepController
from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.fields import FlowState
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import ThetaSchemeIntegrator, run

RHO, NU = 1.0, 0.05
LX, LY, LZ = 1.0, 1.25, 1.0


def _mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=8, ny=10, nz=6, lx=LX, ly=LY, lz=LZ, n_ghost=1)


def _wall_bcs() -> BoundaryConditionSet:
    w = FaceBoundaryCondition(velocity_type=VelocityBCType.NO_SLIP, pressure_type=PressureBCType.NEUMANN)
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def _smooth_bump(X, Y, Z):
    return np.sin(math.pi * X / LX) * np.sin(math.pi * Y / LY) * np.sin(math.pi * Z / LZ)


def _initial_state(mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> FlowState:
    s0 = FlowState.zeros(mesh)
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(mesh.cell_centers_x(), mesh.cell_centers_y(), mesh.face_coords_z(), indexing="ij")
    s0.velocity.u.interior[:] = 0.6 * _smooth_bump(Xu, Yu, Zu)
    s0.velocity.v.interior[:] = 0.4 * _smooth_bump(Xv, Yv, Zv)
    s0.velocity.w.interior[:] = -0.3 * _smooth_bump(Xw, Yw, Zw)
    apply_velocity_bc(s0.velocity, bcs)
    return s0


def _run_adaptive(method: str, mesh, bcs, s0, cfl_target: float, dt_seed: float, T: float):
    integrator = ThetaSchemeIntegrator(
        mesh, bcs, rho=RHO, nu=NU, dt=dt_seed, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    controller = AdaptiveTimestepController(cfl_target=cfl_target, dt_min=dt_seed * 1e-3, dt_max=dt_seed * 10.0, growth_max=1.4, shrink_max=0.25)
    state = s0
    dt_prev = dt_seed
    cfls = []
    while state.time < T - 1e-12:
        decision = controller.next_dt(state.velocity, mesh, dt_previous=dt_prev)
        dt = min(decision.dt, T - state.time)
        state, diag = integrator.step(state, dt=dt)
        cfls.append(diag.cfl)
        dt_prev = dt
    return state, cfls


def _run_fixed(method: str, mesh, bcs, s0, dt: float, T: float):
    n_steps = round(T / dt)
    integrator = ThetaSchemeIntegrator(
        mesh, bcs, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    final_state, _ = run(integrator, s0, n_steps)
    return final_state


def test_adaptive_cfl_controlled_for_incremental_and_rotational() -> None:
    for method in ("incremental", "rotational"):
        mesh = _mesh()
        bcs = _wall_bcs()
        s0 = _initial_state(mesh, bcs)
        final, cfls = _run_adaptive(method, mesh, bcs, s0, cfl_target=0.5, dt_seed=0.001, T=0.005)
        assert max(cfls) <= 0.5 + 1e-9
        for comp in final.velocity.components():
            assert np.all(np.isfinite(comp.data))


def test_adaptive_and_fixed_step_converge_toward_same_solution() -> None:
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    T = 0.005

    reference = _run_fixed("incremental", mesh, bcs, s0, dt=T / 512, T=T)

    # coarse adaptive run: clearly resolvable temporal error
    coarse_final, _ = _run_adaptive("incremental", mesh, bcs, s0, cfl_target=2.0, dt_seed=T / 8, T=T)
    e_coarse = float(np.sqrt(np.mean((coarse_final.velocity.u.interior - reference.velocity.u.interior) ** 2)))

    # fine adaptive run: dt an order of magnitude smaller
    fine_final, _ = _run_adaptive("incremental", mesh, bcs, s0, cfl_target=0.2, dt_seed=T / 80, T=T)
    e_fine = float(np.sqrt(np.mean((fine_final.velocity.u.interior - reference.velocity.u.interior) ** 2)))

    assert e_fine < e_coarse, f"adaptive error did not shrink with a materially finer dt: coarse={e_coarse}, fine={e_fine}"
    # and the fine adaptive run genuinely agrees closely with the fixed-step reference
    assert e_fine < 1e-4


def test_pressure_history_survives_dt_changes() -> None:
    """Confirms p^n (via state.pressure) and the phi warm-start history
    remain valid/finite across a deliberately irregular dt sequence."""
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    integrator = ThetaSchemeIntegrator(
        mesh, bcs, rho=RHO, nu=NU, dt=0.001, theta=0.5, convection_scheme="centered",
        projection_method="rotational", chi=1.0, warm_start=True,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    state = s0
    for dt in [0.001, 0.004, 0.0005, 0.006, 0.0002]:
        state, diag = integrator.step(state, dt=dt)
        assert np.all(np.isfinite(state.pressure.data))
        assert diag.max_divergence < 1e-6
    assert integrator.history.previous_dt == 0.0002
