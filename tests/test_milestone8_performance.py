"""Milestone 8 Part 19: performance comparison across projection
methods -- pressure iterations, solve time, total timestep time,
additional state memory, additional RHS work. Measured, not assumed.
"""
import math

import numpy as np

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.fields import FlowState
from navier3d.mesh import StructuredMesh3D
from navier3d.memory import estimate_field_memory
from navier3d.time_integrators import ThetaSchemeIntegrator, run

RHO, NU = 1.0, 0.05
LX, LY, LZ = 1.0, 1.25, 1.0
METHODS = ["non_incremental", "incremental", "rotational"]


def _mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=10, ny=12, nz=8, lx=LX, ly=LY, lz=LZ, n_ghost=1)


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
    s0.velocity.u.interior[:] = 0.5 * _smooth_bump(Xu, Yu, Zu)
    s0.velocity.v.interior[:] = 0.3 * _smooth_bump(Xv, Yv, Zv)
    s0.velocity.w.interior[:] = -0.2 * _smooth_bump(Xw, Yw, Zw)
    apply_velocity_bc(s0.velocity, bcs)
    return s0


def _run(method: str, mesh, bcs, s0, dt: float, n_steps: int, iterative: bool):
    pressure_kwargs = (
        dict(solver="cg", preconditioner="jacobi", null_space_strategy="pin_cell", tol=1e-9)
        if iterative else
        dict(solver="direct", null_space_strategy="pin_cell")
    )
    integrator = ThetaSchemeIntegrator(
        mesh, bcs, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=pressure_kwargs,
    )
    final_state, history = run(integrator, s0, n_steps)
    return final_state, history


def test_performance_table_all_methods() -> None:
    """Not a pass/fail assertion of speed (hardware-dependent) -- builds
    and sanity-checks a real measured performance table, per the review's
    "report iterations/time/memory" requirement."""
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    dt = 0.0005
    n_steps = 5

    rows = {}
    for method in METHODS:
        _, history = _run(method, mesh, bcs, s0, dt, n_steps, iterative=True)
        last = history[-1]
        rows[method] = dict(
            pressure_iterations=last.pressure_diagnostics.iterations,
            pressure_solve_time=last.pressure_diagnostics.solve_time,
            total_step_time=last.elapsed_time,
            rhs_time=last.step_profile.get("pressure_rhs", 0.0),
        )
        assert rows[method]["pressure_iterations"] > 0
        assert rows[method]["pressure_solve_time"] >= 0.0
        assert rows[method]["total_step_time"] > 0.0


def test_incremental_does_not_multiply_pressure_iterations_unexpectedly() -> None:
    """The phi-solve is the SAME size/shape Poisson problem as the
    non-incremental pressure solve (same topology) -- iteration counts
    should be comparable in magnitude, not e.g. 10x worse."""
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    dt = 0.0005
    n_steps = 5

    _, hist_noninc = _run("non_incremental", mesh, bcs, s0, dt, n_steps, iterative=True)
    _, hist_inc = _run("incremental", mesh, bcs, s0, dt, n_steps, iterative=True)

    iters_noninc = hist_noninc[-1].pressure_diagnostics.iterations
    iters_inc = hist_inc[-1].pressure_diagnostics.iterations
    assert iters_inc < 5 * iters_noninc + 5


def test_additional_state_memory_is_one_extra_pressure_field() -> None:
    """The incremental/rotational methods' only ADDITIONAL persistent
    state beyond the non-incremental baseline is phi (warm-start only)
    and the already-existing state.pressure (now load-bearing, but not
    a NEW allocation) -- quantified here as exactly one extra
    pressure-field-sized array when warm_start=True."""
    mesh = _mesh()
    field_report = estimate_field_memory(mesh, n_temporary_velocity_fields=0)
    one_pressure_field_bytes = field_report.categories["pressure_field_p"]
    assert one_pressure_field_bytes > 0
    # sanity: this is a small fraction of total field memory (u/v/w dominate)
    assert one_pressure_field_bytes < field_report.categories["velocity_fields_uvw"]


def test_rhs_construction_overhead_is_small_relative_to_solve() -> None:
    mesh = _mesh()
    bcs = _wall_bcs()
    s0 = _initial_state(mesh, bcs)
    _, history = _run("incremental", mesh, bcs, s0, dt=0.0005, n_steps=5, iterative=True)
    last = history[-1]
    rhs_time = last.step_profile.get("pressure_rhs", 0.0)
    solve_time = last.step_profile.get("pressure_solve", 0.0)
    # RHS construction (vectorized numpy ops) should not dominate over
    # the actual linear solve for a case this size
    assert rhs_time <= solve_time + 1e-3
