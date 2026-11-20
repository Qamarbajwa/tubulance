"""Milestone 7 Part K: scaling benchmark.

Compares the existing direct-LU reference path against the best
iterative CPU configuration (SPD-reduced diffusion + CG, pressure CG
with Jacobi preconditioning) across a range of grid resolutions, on a
periodic Taylor-Green-like nonlinear case (real nonzero velocity field,
not a trivial zero state, so pressure/diffusion do genuine work).

Direct-LU is skipped ("not attempted -- expected fill-in prohibitive")
above a size threshold determined by a real measurement at N=32 (see
the Milestone 7 report): a single pressure OR diffusion matrix's direct
factorization already needs ~1.2 GB of fill-in at N=32 (a >400x blowup
over the ~2.9 MB sparse matrix itself), and 3-D fill-in scales worse
than linearly with problem size -- attempting N=48 direct would very
likely exhaust available memory on a typical workstation.

Run directly: ``python benchmarks/scaling_benchmark.py``
"""
from __future__ import annotations

import gc
import math
import time

import numpy as np

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.fields import FlowState
from navier3d.mesh import StructuredMesh3D
from navier3d.memory import estimate_field_memory, estimate_solver_matrix_memory, measure_matrix_memory
from navier3d.time_integrators import ThetaSchemeIntegrator, run

LX, LY, LZ = 1.0, 1.25, 1.5
NU, RHO, U0 = 0.02, 1.0, 1.0
MX, MY = 2, 1


def _periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def _tg_state(mesh: StructuredMesh3D) -> FlowState:
    kx, ky = 2 * math.pi * MX / LX, 2 * math.pi * MY / LY
    state = FlowState.zeros(mesh)
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    state.velocity.u.interior[:] = U0 * np.sin(kx * Xu) * np.cos(ky * Yu)
    state.velocity.v.interior[:] = -U0 * (kx / ky) * np.cos(kx * Xv) * np.sin(ky * Yv)
    return state


def _bench_one(n: int, backend: str, n_steps: int = 3, dt: float = 0.001) -> dict:
    mesh = StructuredMesh3D(nx=n, ny=n, nz=n, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    bcs = _periodic_bcs()

    if backend == "direct":
        pressure_kwargs = dict(solver="direct", null_space_strategy="pin_cell")
        diffusion_kwargs = dict(formulation="pinned", solver="direct")
    elif backend == "iterative":
        pressure_kwargs = dict(solver="cg", preconditioner="jacobi", null_space_strategy="zero_mean",
                                rhs_compatibility="mean_removal", tol=1e-8, max_iterations=2000)
        diffusion_kwargs = dict(formulation="spd", solver="cg", preconditioner="jacobi", rtol=1e-8, max_iterations=2000)
    else:
        raise ValueError(backend)

    integrator = ThetaSchemeIntegrator(
        mesh, bcs, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
        pressure_kwargs=pressure_kwargs, diffusion_kwargs=diffusion_kwargs, warm_start=(backend == "iterative"),
    )
    state = _tg_state(mesh)

    t0 = time.perf_counter()
    final_state, history = run(integrator, state, n_steps)
    wall = time.perf_counter() - t0

    last = history[-1]
    field_mem = estimate_field_memory(mesh)
    measured = {
        "pressure": integrator.pressure_system.matrix,
        "diffusion_u": integrator.diffusion_systems[0].matrix,
        "diffusion_v": integrator.diffusion_systems[1].matrix,
        "diffusion_w": integrator.diffusion_systems[2].matrix,
    }
    solver_mem = estimate_solver_matrix_memory(mesh, measured=measured)

    row = dict(
        n=n,
        backend=backend,
        total_cells=n ** 3,
        timestep_time=wall / n_steps,
        pressure_solve_time=last.pressure_diagnostics.solve_time,
        diffusion_solve_time=last.diffusion_time,
        convection_time=last.convection_time,
        pressure_iterations=last.pressure_diagnostics.iterations,
        diffusion_iterations=sum(d.iterations for d in last.diffusion_diagnostics),
        memory_mb=(field_mem.total_bytes + solver_mem.total_bytes) / 1e6,
        cfl=last.cfl,
        max_divergence=last.max_divergence,
    )
    del integrator, state, final_state, history
    gc.collect()
    return row


def main() -> None:
    sizes = [16, 24, 32, 48]
    direct_limit = 24  # N=32 direct already measured separately at ~1.2 GB/matrix fill-in; skip re-measuring here
    rows = []

    for n in sizes:
        if n <= direct_limit:
            print(f"[direct]    N={n} ...", flush=True)
            rows.append(_bench_one(n, "direct"))
        else:
            print(f"[direct]    N={n}: not attempted -- expected fill-in prohibitive (see report)")
            rows.append(dict(n=n, backend="direct", not_attempted=True))

        print(f"[iterative] N={n} ...", flush=True)
        rows.append(_bench_one(n, "iterative"))

    print()
    header = f"{'N':>4} {'backend':>10} {'cells':>10} {'dt/step(s)':>11} {'p_solve(s)':>11} {'diff_solve(s)':>14} {'conv(s)':>9} {'p_iter':>7} {'d_iter':>7} {'mem(MB)':>9} {'CFL':>7}"
    print(header)
    print("-" * len(header))
    for r in rows:
        if r.get("not_attempted"):
            print(f"{r['n']:>4} {r['backend']:>10}   not attempted -- expected fill-in prohibitive")
            continue
        print(
            f"{r['n']:>4} {r['backend']:>10} {r['total_cells']:>10} {r['timestep_time']:>11.4f} "
            f"{r['pressure_solve_time']:>11.4f} {r['diffusion_solve_time']:>14.4f} {r['convection_time']:>9.4f} "
            f"{r['pressure_iterations']:>7} {r['diffusion_iterations']:>7} {r['memory_mb']:>9.1f} {r['cfl']:>7.3f}"
        )


if __name__ == "__main__":
    main()
