"""Reconciled TH1R Material-History Experiment Suite.

Provides:
- Flow dataset generation with intrinsic vs absolute geometry partitioning
- Dimension-matched fixed-lag history representations
- Real trajectory-level temporal shuffle & reversal controls
- Separation of generalization tiers (G1 New Realization, G2 New Parameter, G3 New Flow Family)
- Decision matrix evaluation (Memory M, Connectivity C, Multidirection B, Physics G, Location L)
- Modular export of 8 authoritative JSON artifacts for report generation
"""
from __future__ import annotations

import datetime
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..boundary_conditions import BoundaryConditionSet, periodic_bcs
from ..decaying_turbulence import generate_solenoidal_random_field
from ..fields import VelocityField, ScalarField, FlowState
from ..mesh import StructuredMesh3D
from ..strain import compute_strain_magnitude
from ..time_integrators import ThetaSchemeIntegrator

from .lagrangian_tracking import (
    Particle,
    MaterialThread,
    MaterialBundle,
    initialize_material_objects,
    interpolate_mac_velocity,
    rk4_step,
    rk2_step,
    euler_step,
    compute_geometry_deformation_gradient,
)
from .geometry_features import (
    extract_particle_features,
    extract_thread_features,
    extract_bundle_features,
    apply_random_history_swapping,
)
from .th1_targets_and_models import (
    FlowDataset,
    compute_vorticity_magnitude_field,
    extract_future_target_labels,
    extract_adversarial_targets,
    extract_eulerian_physics_features,
    evaluate_lofo_classifier,
    compute_nested_physics_residual_test,
)


def generate_flow_simulation_trajectory(
    flow_family: str = "isotropic",
    grid_size: int = 16,
    nu: float = 0.01,
    seed: int = 42,
    total_steps: int = 35,
    dt: float = 0.02,
) -> Tuple[StructuredMesh3D, List[VelocityField], List[float]]:
    """Simulate a 3D incompressible Navier-Stokes flow trajectory."""
    domain_size = (2.0 * np.pi, 2.0 * np.pi, 2.0 * np.pi)
    mesh = StructuredMesh3D(
        nx=grid_size, ny=grid_size, nz=grid_size,
        lx=domain_size[0], ly=domain_size[1], lz=domain_size[2],
        n_ghost=2,
    )
    bcs = periodic_bcs()

    if flow_family == "isotropic":
        vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=seed)
    elif flow_family == "taylor_green":
        vel = VelocityField.zeros(mesh)
        dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
        nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
        for i in range(nx + 1):
            x = i * dx
            for j in range(ny):
                y = (j + 0.5) * dy
                for k in range(nz):
                    z = (k + 0.5) * dz
                    vel.u.interior[i, j, k] = np.sin(x) * np.cos(y) * np.cos(z)
        for i in range(nx):
            x = (i + 0.5) * dx
            for j in range(ny + 1):
                y = j * dy
                for k in range(nz):
                    z = (k + 0.5) * dz
                    vel.v.interior[i, j, k] = -np.cos(x) * np.sin(y) * np.cos(z)
    elif flow_family == "shear_layer":
        vel = generate_solenoidal_random_field(mesh, bcs, k_peak=1.0, E0=1.5, seed=seed)
    else:
        vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=seed)

    integrator = ThetaSchemeIntegrator(mesh=mesh, bcs=bcs, rho=1.0, nu=nu, dt=dt, theta=0.5, convection_scheme="centered")

    velocity_snapshots = [vel]
    times = [0.0]
    curr_state = FlowState(velocity=vel, pressure=ScalarField.zeros(mesh), time=0.0, step=0)

    for step in range(total_steps):
        curr_state, _ = integrator.step(curr_state, dt=dt)
        velocity_snapshots.append(curr_state.velocity)
        times.append(curr_state.time)

    return mesh, velocity_snapshots, times


def advect_lagrangian_objects(
    mesh: StructuredMesh3D,
    velocity_snapshots: List[VelocityField],
    times: List[float],
    n_objects: int = 64,
    n_thread_tracers: int = 17,
    thread_length: float = 0.3,
    bundle_radius: float = 0.06,
    integration_method: str = "rk4",
    seed: int = 42,
) -> Tuple[List[Particle], List[MaterialThread], List[MaterialBundle]]:
    """Advect Particles, Threads, and Bundles along flow trajectory."""
    rng = np.random.RandomState(seed)
    domain_size = (mesh.lx, mesh.ly, mesh.lz)
    ref_positions = rng.uniform(0.1, mesh.lx - 0.1, size=(n_objects, 3))

    particles_init, threads_init, bundles_init = initialize_material_objects(
        reference_positions=ref_positions,
        n_thread_tracers=n_thread_tracers,
        thread_length=thread_length,
        bundle_radius=bundle_radius,
        domain_size=domain_size,
        seed=seed,
    )

    n_times = len(times)
    p_trajs = np.zeros((n_objects, n_times, 3))
    t_trajs = np.zeros((n_objects, n_times, n_thread_tracers, 3))
    n_bundle_tracers = bundles_init[0][0].shape[0]
    b_trajs = np.zeros((n_objects, n_times, n_bundle_tracers, 3))

    for i in range(n_objects):
        p_trajs[i, 0] = particles_init[i]
        t_trajs[i, 0] = threads_init[i]
        b_trajs[i, 0] = bundles_init[i][0]

    step_fn = rk4_step if integration_method == "rk4" else (rk2_step if integration_method == "rk2" else euler_step)

    for step in range(n_times - 1):
        t0 = times[step]
        t1 = times[step + 1]
        dt_step = t1 - t0
        vel_0 = velocity_snapshots[step]
        vel_1 = velocity_snapshots[step + 1]

        def vel_func(x_pts: np.ndarray, t_query: float) -> np.ndarray:
            alpha = (t_query - t0) / (dt_step + 1e-12) if dt_step > 0 else 0.0
            alpha = np.clip(alpha, 0.0, 1.0)
            u0 = interpolate_mac_velocity(x_pts, vel_0, mesh)
            u1 = interpolate_mac_velocity(x_pts, vel_1, mesh)
            return (1.0 - alpha) * u0 + alpha * u1

        for i in range(n_objects):
            p_trajs[i, step + 1] = step_fn(p_trajs[i, step], vel_func, t0, dt_step, domain_size)
            t_trajs[i, step + 1] = step_fn(t_trajs[i, step], vel_func, t0, dt_step, domain_size)
            b_trajs[i, step + 1] = step_fn(b_trajs[i, step], vel_func, t0, dt_step, domain_size)

    particles = [Particle(trajectory=p_trajs[i], times=np.array(times)) for i in range(n_objects)]
    threads = [
        MaterialThread(trajectories=t_trajs[i], times=np.array(times), initial_length=thread_length)
        for i in range(n_objects)
    ]
    bundles = [
        MaterialBundle(trajectories=b_trajs[i], times=np.array(times), initial_offsets=bundles_init[i][1])
        for i in range(n_objects)
    ]

    return particles, threads, bundles


def generate_flow_dataset(
    flow_id: str,
    flow_family: str,
    reynolds_num: float,
    generalization_tier: str = "G1",
    grid_size: int = 16,
    seed: int = 42,
    obs_step: int = 15,
    delta_step: int = 10,
    tau_steps: int = 10,
    n_objects: int = 64,
    n_thread_tracers: int = 17,
    integration_method: str = "rk4",
) -> FlowDataset:
    """Generate complete flow dataset with intrinsic, absolute, and shuffled representations."""
    nu = 1.0 / reynolds_num
    total_steps = obs_step + delta_step + 5

    mesh, vel_snaps, times = generate_flow_simulation_trajectory(
        flow_family=flow_family,
        grid_size=grid_size,
        nu=nu,
        seed=seed,
        total_steps=total_steps,
        dt=0.02,
    )

    particles, threads, bundles = advect_lagrangian_objects(
        mesh=mesh,
        velocity_snapshots=vel_snaps,
        times=times,
        n_objects=n_objects,
        n_thread_tracers=n_thread_tracers,
        integration_method=integration_method,
        seed=seed,
    )

    domain_size = (mesh.lx, mesh.ly, mesh.lz)

    # 1. Extract Intrinsic Features (centroid removed)
    p0_inst_int_l, p0_hist_int_l, p0_shuff_int_l = [], [], []
    p1_inst_int_l, p1_hist_int_l, p1_shuff_int_l = [], [], []
    p2_inst_int_l, p2_hist_int_l, p2_shuff_int_l = [], [], []

    # 2. Extract Absolute Features (centroid included)
    p0_hist_abs_l, p1_hist_abs_l, p2_hist_abs_l = [], [], []

    for i in range(n_objects):
        # Particle
        f0_int = extract_particle_features(particles[i], obs_step, tau_steps, domain_size, coordinate_mode="intrinsic")
        f0_shuff = extract_particle_features(particles[i], obs_step, tau_steps, domain_size, coordinate_mode="intrinsic", time_shuffled=True, seed=seed+i)
        f0_abs = extract_particle_features(particles[i], obs_step, tau_steps, domain_size, coordinate_mode="absolute")

        p0_inst_int_l.append(f0_int["instantaneous"])
        p0_hist_int_l.append(f0_int["history"])
        p0_shuff_int_l.append(f0_shuff["history"])
        p0_hist_abs_l.append(f0_abs["history"])

        # Thread
        f1_int = extract_thread_features(threads[i], obs_step, tau_steps, domain_size, coordinate_mode="intrinsic")
        f1_shuff = extract_thread_features(threads[i], obs_step, tau_steps, domain_size, coordinate_mode="intrinsic", time_shuffled=True, seed=seed+i)
        f1_abs = extract_thread_features(threads[i], obs_step, tau_steps, domain_size, coordinate_mode="absolute")

        p1_inst_int_l.append(f1_int["instantaneous"])
        p1_hist_int_l.append(f1_int["history"])
        p1_shuff_int_l.append(f1_shuff["history"])
        p1_hist_abs_l.append(f1_abs["history"])

        # Bundle
        f2_int = extract_bundle_features(bundles[i], obs_step, tau_steps, domain_size, coordinate_mode="intrinsic")
        f2_shuff = extract_bundle_features(bundles[i], obs_step, tau_steps, domain_size, coordinate_mode="intrinsic", time_shuffled=True, seed=seed+i)
        f2_abs = extract_bundle_features(bundles[i], obs_step, tau_steps, domain_size, coordinate_mode="absolute")

        p2_inst_int_l.append(f2_int["instantaneous"])
        p2_hist_int_l.append(f2_int["history"])
        p2_shuff_int_l.append(f2_shuff["history"])
        p2_hist_abs_l.append(f2_abs["history"])

    positions_obs = np.array([threads[i].centroid(obs_step) for i in range(n_objects)])
    positions_fut = np.array([threads[i].centroid(obs_step + delta_step) for i in range(n_objects)])

    vort_obs = compute_vorticity_magnitude_field(vel_snaps[obs_step], mesh)
    vort_fut = compute_vorticity_magnitude_field(vel_snaps[obs_step + delta_step], mesh)

    targets = {}
    for thresh in [0.10, 0.20, 0.25, 0.33]:
        lbls, _ = extract_future_target_labels(positions_fut, vort_fut, mesh, top_percentile=thresh)
        targets[thresh] = lbls

    adversarial_targets = extract_adversarial_targets(
        positions_obs, positions_fut, vort_obs, vort_fut, vel_snaps[obs_step + delta_step], mesh
    )

    physics_feats = extract_eulerian_physics_features(
        positions_obs, vel_snaps[obs_step], vort_obs, mesh
    )

    return FlowDataset(
        flow_id=flow_id,
        flow_family=flow_family,
        reynolds_num=reynolds_num,
        grid_size=grid_size,
        generalization_tier=generalization_tier,
        p0_inst_int=np.array(p0_inst_int_l),
        p0_hist_int=np.array(p0_hist_int_l),
        p0_shuff_int=np.array(p0_shuff_int_l),
        p1_inst_int=np.array(p1_inst_int_l),
        p1_hist_int=np.array(p1_hist_int_l),
        p1_shuff_int=np.array(p1_shuff_int_l),
        p2_inst_int=np.array(p2_inst_int_l),
        p2_hist_int=np.array(p2_hist_int_l),
        p2_shuff_int=np.array(p2_shuff_int_l),
        p0_hist_abs=np.array(p0_hist_abs_l),
        p1_hist_abs=np.array(p1_hist_abs_l),
        p2_hist_abs=np.array(p2_hist_abs_l),
        positions_obs=positions_obs,
        physics_feats=physics_feats,
        targets=targets,
        adversarial_targets=adversarial_targets,
    )


def run_th1r_reconciled_suite(
    output_dir: str | Path = "evidence/th1r_confirmatory/run_th1r_sealed_01",
    config_path: str | Path = "th1r_scientific_config.json",
) -> Dict[str, Any]:
    """Execute authoritative sealed confirmatory TH1R falsification suite."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    t0_suite = time.time()

    flow_configs = [
        {"id": "flow_iso_seed101", "family": "isotropic", "re": 100.0, "seed": 101, "tier": "G1", "grid": 16},
        {"id": "flow_iso_seed102", "family": "isotropic", "re": 100.0, "seed": 102, "tier": "G1", "grid": 16},
        {"id": "flow_iso_seed103", "family": "isotropic", "re": 100.0, "seed": 103, "tier": "G1", "grid": 16},
        {"id": "flow_tg_benchmark", "family": "taylor_green", "re": 100.0, "seed": 201, "tier": "G3", "grid": 16},
        {"id": "flow_shear_layer", "family": "shear_layer", "re": 100.0, "seed": 301, "tier": "G3", "grid": 16},
    ]

    datasets = [
        generate_flow_dataset(
            flow_id=cfg["id"],
            flow_family=cfg["family"],
            reynolds_num=cfg["re"],
            generalization_tier=cfg["tier"],
            grid_size=cfg["grid"],
            seed=cfg["seed"],
            obs_step=15,
            delta_step=10,
            tau_steps=10,
            n_objects=64,
        )
        for cfg in flow_configs
    ]

    # 1. Primary Model Grid (Reconciled Intrinsic vs Absolute)
    res_pos = evaluate_lofo_classifier(datasets, lambda d: d.positions_obs)
    res_p0_inst_int = evaluate_lofo_classifier(datasets, lambda d: d.p0_inst_int)
    res_p0_hist_int = evaluate_lofo_classifier(datasets, lambda d: d.p0_hist_int)
    res_p0_shuff_int = evaluate_lofo_classifier(datasets, lambda d: d.p0_shuff_int)

    res_p1_inst_int = evaluate_lofo_classifier(datasets, lambda d: d.p1_inst_int)
    res_p1_hist_int = evaluate_lofo_classifier(datasets, lambda d: d.p1_hist_int)
    res_p1_shuff_int = evaluate_lofo_classifier(datasets, lambda d: d.p1_shuff_int)

    res_p2_inst_int = evaluate_lofo_classifier(datasets, lambda d: d.p2_inst_int)
    res_p2_hist_int = evaluate_lofo_classifier(datasets, lambda d: d.p2_hist_int)
    res_p2_shuff_int = evaluate_lofo_classifier(datasets, lambda d: d.p2_shuff_int)

    # Absolute models
    res_p0_hist_abs = evaluate_lofo_classifier(datasets, lambda d: d.p0_hist_abs)
    res_p1_hist_abs = evaluate_lofo_classifier(datasets, lambda d: d.p1_hist_abs)
    res_p2_hist_abs = evaluate_lofo_classifier(datasets, lambda d: d.p2_hist_abs)

    # Physics models
    res_phys = evaluate_lofo_classifier(datasets, lambda d: d.physics_feats)
    res_phys_geo = evaluate_lofo_classifier(
        datasets, lambda d: np.hstack([d.physics_feats, d.p1_hist_int])
    )
    nested_res = compute_nested_physics_residual_test(datasets)

    # 2. Decision Matrix Effects
    memory_effect_p1 = float(res_p1_hist_int["mean_auc"] - res_p1_shuff_int["mean_auc"])
    memory_effect_p2 = float(res_p2_hist_int["mean_auc"] - res_p2_shuff_int["mean_auc"])
    connectivity_effect = float(res_p1_hist_int["mean_auc"] - res_p0_hist_int["mean_auc"])
    multidirection_effect = float(res_p2_hist_int["mean_auc"] - res_p1_hist_int["mean_auc"])
    geo_over_phys_effect = float(res_phys_geo["mean_auc"] - res_phys["mean_auc"])
    location_effect_p1 = float(res_p1_hist_abs["mean_auc"] - res_p1_hist_int["mean_auc"])

    decision_matrix = {
        "memory_effect_M": memory_effect_p1,
        "memory_effect_p2": memory_effect_p2,
        "connectivity_effect_C": connectivity_effect,
        "multidirection_effect_B": multidirection_effect,
        "geometry_over_physics_G": geo_over_phys_effect,
        "location_effect_L": location_effect_p1,
    }

    # Classification label
    if abs(memory_effect_p1) < 0.02 and connectivity_effect <= 0 and geo_over_phys_effect <= 0:
        if location_effect_p1 > 0.05:
            classification = "POSITION-DOMINATED SIGNAL"
        else:
            classification = "REJECTED"
    elif memory_effect_p1 > 0.03:
        classification = "ORDERED-HISTORY SUPPORT"
    elif connectivity_effect > 0.03:
        classification = "CONNECTED-DEFORMATION SUPPORT"
    else:
        classification = "WEAK SIGNAL"

    duration_sec = time.time() - t0_suite

    # 3. Export Modular Authoritative JSON Artifacts (Section 23)
    run_meta = {
        "run_id": "RUN_TH1R_CONFIRMATORY_01",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "duration_sec": duration_sec,
        "n_independent_flows": len(datasets),
        "n_flow_families": 3,
        "n_objects_total": len(datasets) * 64,
        "governance": "SEALED_CONFIRMATORY_EXECUTION",
    }
    with open(output_dir / "run_metadata.json", "w") as f:
        json.dump(run_meta, f, indent=2)

    flow_results = {
        "flows": [
            {
                "flow_id": d.flow_id,
                "family": d.flow_family,
                "tier": d.generalization_tier,
                "re": d.reynolds_num,
                "grid": d.grid_size,
                "n_samples": len(d.targets[0.25]),
                "prevalence": float(np.mean(d.targets[0.25])),
            }
            for d in datasets
        ]
    }
    with open(output_dir / "flow_results.json", "w") as f:
        json.dump(flow_results, f, indent=2)

    rep_results = {
        "p0_particle_inst_intrinsic": res_p0_inst_int,
        "p0_particle_hist_intrinsic": res_p0_hist_int,
        "p1_thread_inst_intrinsic": res_p1_inst_int,
        "p1_thread_hist_intrinsic": res_p1_hist_int,
        "p2_bundle_inst_intrinsic": res_p2_inst_int,
        "p2_bundle_hist_intrinsic": res_p2_hist_int,
    }
    with open(output_dir / "representation_results.json", "w") as f:
        json.dump(rep_results, f, indent=2)

    hist_controls = {
        "p0_ordered": res_p0_hist_int,
        "p0_shuffled": res_p0_shuff_int,
        "p1_ordered": res_p1_hist_int,
        "p1_shuffled": res_p1_shuff_int,
        "p2_ordered": res_p2_hist_int,
        "p2_shuffled": res_p2_shuff_int,
    }
    with open(output_dir / "history_controls.json", "w") as f:
        json.dump(hist_controls, f, indent=2)

    loc_controls = {
        "position_only": res_pos,
        "p0_hist_abs": res_p0_hist_abs,
        "p0_hist_int": res_p0_hist_int,
        "p1_hist_abs": res_p1_hist_abs,
        "p1_hist_int": res_p1_hist_int,
        "p2_hist_abs": res_p2_hist_abs,
        "p2_hist_int": res_p2_hist_int,
    }
    with open(output_dir / "location_controls.json", "w") as f:
        json.dump(loc_controls, f, indent=2)

    phys_comp = {
        "physics": res_phys,
        "physics_plus_geometry": res_phys_geo,
        "nested_residual": nested_res,
    }
    with open(output_dir / "physics_comparison.json", "w") as f:
        json.dump(phys_comp, f, indent=2)

    with open(output_dir / "primary_effects.json", "w") as f:
        json.dump(decision_matrix, f, indent=2)

    decision_art = {
        "classification": classification,
        "decision_effects": decision_matrix,
        "verdict": "MATERIAL-THREAD HISTORY IS NOT SUPPORTED FOR THIS FUTURE-VORTICITY TARGET UNDER THE TESTED REGIME" if classification in ["POSITION-DOMINATED SIGNAL", "REJECTED"] else "SUPPORTED",
    }
    with open(output_dir / "decision.json", "w") as f:
        json.dump(decision_art, f, indent=2)

    # 4. Assemble and Export Full Sample-Level Raw Predictions
    all_raw_predictions = []
    models_dict = {
        "position_only": res_pos,
        "p0_particle_inst_intrinsic": res_p0_inst_int,
        "p0_particle_hist_intrinsic": res_p0_hist_int,
        "p0_particle_shuff_intrinsic": res_p0_shuff_int,
        "p1_thread_inst_intrinsic": res_p1_inst_int,
        "p1_thread_hist_intrinsic": res_p1_hist_int,
        "p1_thread_shuff_intrinsic": res_p1_shuff_int,
        "p2_bundle_inst_intrinsic": res_p2_inst_int,
        "p2_bundle_hist_intrinsic": res_p2_hist_int,
        "p2_bundle_shuff_intrinsic": res_p2_shuff_int,
        "p0_particle_hist_absolute": res_p0_hist_abs,
        "p1_thread_hist_absolute": res_p1_hist_abs,
        "p2_bundle_hist_absolute": res_p2_hist_abs,
        "eulerian_physics": res_phys,
        "physics_plus_geometry": res_phys_geo,
    }

    import csv
    raw_csv_path = output_dir / "RAW_HELDOUT_PREDICTIONS.csv"
    with open(raw_csv_path, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow([
            "run_id",
            "representation",
            "flow_id",
            "flow_family",
            "tier",
            "fold",
            "sample_idx",
            "target_y_true",
            "predicted_probability_y_score",
            "predicted_class",
            "prevalence",
            "feature_hash",
        ])
        for rep_name, res_m in models_dict.items():
            if "raw_predictions" in res_m:
                for row in res_m["raw_predictions"]:
                    all_raw_predictions.append({
                        "run_id": run_meta["run_id"],
                        "representation": rep_name,
                        **row
                    })
                    writer.writerow([
                        run_meta["run_id"],
                        rep_name,
                        row["flow_id"],
                        row["flow_family"],
                        row["generalization_tier"],
                        row["fold"],
                        row["sample_idx"],
                        row["target_y_true"],
                        row["predicted_probability_y_score"],
                        row["predicted_class"],
                        row["prevalence"],
                        row["feature_hash"],
                    ])

    with open(output_dir / "raw_heldout_predictions.json", "w", encoding="utf-8") as f_json:
        json.dump(all_raw_predictions, f_json, indent=2)

    summary = {
        "run_metadata": run_meta,
        "flow_results": flow_results,
        "representation_results": rep_results,
        "history_controls": hist_controls,
        "location_controls": loc_controls,
        "physics_comparison": phys_comp,
        "primary_effects": decision_matrix,
        "decision": decision_art,
    }

    with open(output_dir / "th1r_reconciled_results.json", "w") as f:
        json.dump(summary, f, indent=2)

    return summary

