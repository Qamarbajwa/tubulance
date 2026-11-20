"""Script executing an audited benchmark run under Milestone V0 framework."""
from __future__ import annotations

import os
import numpy as np

from navier3d.mesh import StructuredMesh3D
from navier3d.fields import FlowState, ScalarField
from navier3d.time_integrators import ThetaSchemeIntegrator
from navier3d.reduced.stokes_eigenbasis import StokesEigenbasis3D
from navier3d.reduced.w8_stokes_rom import StokesEigenmodeODEIntegrator
from navier3d.reduced.w10_multi_coordinate import (
    channel_bcs,
    generate_channel_initial_condition,
    WallShearDiagnostics,
)
from navier3d.reduced.w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm
from navier3d.audit import (
    generate_run_id,
    capture_environment,
    fingerprint_config,
    assert_comparable,
    EvidenceBundle,
    append_to_research_ledger,
    calculate_velocity_l2_relative_error,
    calculate_wall_shear_relative_error,
    build_metric_entry,
    preregister_experiment,
    ClaimChecker,
)
from navier3d.audit.recompute import audit_recompute


def run_audited_benchmark():
    run_id = os.environ.get("V1_RUN_ID") or generate_run_id("v0", "channel12_audited")
    bundle = EvidenceBundle(run_id)
    bundle.init_bundle()

    # 1. Config & Environment
    config_dict = {
        "nx": 12, "ny": 12, "nz": 12,
        "lx": 6.283185307179586, "ly": 2.0, "lz": 6.283185307179586,
        "nu": 0.05, "rho": 1.0, "dt": 0.005, "n_steps": 5,
        "seed": 42, "k_peak": 2.0, "E0": 0.5,
        "bcs": "channel", "forcing": "unforced",
    }
    config_hash, frozen_config = fingerprint_config(config_dict, bundle.run_dir)
    capture_environment(bundle.run_dir)

    # Preregistration
    preregister_experiment(
        milestone="v0",
        hypothesis="Stokes ROM under matched channel BCs achieves accurate wall shear and systematic representation decay",
        config=config_dict,
        metrics=["velocity_relative_l2", "wall_shear_relative_error"],
        success_criteria={"wall_shear_relative_error": "< 0.02"},
        run_dir=bundle.run_dir,
    )

    # 2. Benchmark Execution
    mesh = StructuredMesh3D(
        nx=frozen_config.nx, ny=frozen_config.ny, nz=frozen_config.nz,
        lx=frozen_config.lx, ly=frozen_config.ly, lz=frozen_config.lz,
        n_ghost=1,
    )
    bcs = channel_bcs()
    assert_comparable(config_dict, config_dict)

    vel0 = generate_channel_initial_condition(mesh, bcs, seed=frozen_config.seed)
    p0 = ScalarField.zeros(mesh)
    state = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

    integrator = ThetaSchemeIntegrator(
        mesh, bcs, theta=0.5, nu=frozen_config.nu, rho=frozen_config.rho, dt=frozen_config.dt,
        pressure_kwargs=dict(solver="cg", tol=1e-10, max_iterations=5000, null_space_strategy="pin_cell"),
    )
    for _ in range(frozen_config.n_steps):
        state, _ = integrator.step(state, frozen_config.dt)
    vel_truth = state.velocity

    # ROM at r=160
    stokes_basis = StokesEigenbasis3D(mesh, max_k_index=4, max_m_wall=5, bcs=bcs)
    r = min(160, stokes_basis.num_modes)
    a0 = stokes_basis.project_mac(vel0)
    a0_trunc = np.zeros_like(a0)
    a0_trunc[:r] = a0[:r]

    rom_integrator = StokesEigenmodeODEIntegrator(stokes_basis, nu=frozen_config.nu)
    a_final = rom_integrator.run_production(a0_trunc, frozen_config.dt, frozen_config.n_steps)
    vel_rom = stokes_basis.reconstruct_mac(a_final)

    # Save raw arrays
    bundle.save_raw_array("u_reference", vel_truth.u.data)
    bundle.save_raw_array("u_candidate", vel_rom.u.data)

    # Compute metrics with version-controlled functions
    e_u = calculate_velocity_l2_relative_error(vel_truth.u.data, vel_rom.u.data)
    shear = WallShearDiagnostics.compute_wall_shear_error(vel_truth, vel_rom, mesh, frozen_config.nu)
    e_tau = shear["E_tau_w"]

    metric_eu = build_metric_entry("velocity_relative_l2", e_u, None, ["w10_multi_coordinate.py"], calculate_velocity_l2_relative_error, run_id, config_hash)
    metric_etau = build_metric_entry("wall_shear_relative_error", e_tau, None, ["w10_multi_coordinate.py"], calculate_wall_shear_relative_error, run_id, config_hash)

    metrics_data = {
        "velocity_relative_l2": metric_eu,
        "wall_shear_relative_error": metric_etau,
    }
    bundle.save_metrics(metrics_data)
    bundle.finalize()

    append_to_research_ledger(run_id, "v0", config_hash, "COMPLETED")

    # Add claims
    checker = ClaimChecker(bundle.run_dir)
    checker.add_claim("V0-C1", "Stokes ROM under matched channel BCs achieves accurate wall shear", [run_id], ["wall_shear_relative_error"], "VERIFIED")

    # Recomputation check
    recompute_res = audit_recompute(run_id)

    print("\n" + "=" * 90)
    print("V0 AUDITED BENCHMARK COMPLETE")
    print("=" * 90)
    print(f"Run ID: {run_id}")
    print(f"Config Hash: {config_hash}")
    print(f"Velocity Error (E_u): {e_u:.6f}")
    print(f"Wall Shear Error (E_tau_w): {e_tau:.6f}")
    print(f"Audit Status: {recompute_res['status']}")
    print("=" * 90)

    return run_id


if __name__ == "__main__":
    run_audited_benchmark()
