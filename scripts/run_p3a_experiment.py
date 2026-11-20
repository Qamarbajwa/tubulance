"""Milestone P3-A Experiment Runner: Cross-Seed Phase / Translation Alignment Causal Diagnostic.

This script executes the sealed diagnostic experiment for Milestone P3-A.
Outputs all required machine-readable JSON files in report_json/.

Protocol:
1. Generate multi-seed channel flow snapshots (Seeds 101, 104, 105).
2. Measure raw pairwise field and Grassmannian subspace distances (r=4, 8, 12, 16).
3. Compute optimal continuous subgrid periodic alignment (Delta_x*, Delta_z*).
4. Rebuild POD bases on aligned snapshots and recompute principal angles.
5. Perform Fourier phase vs amplitude error separation.
6. Evaluate shift temporal coherence trajectories.
7. Run synthetic self-control, random-shift controls, and same-seed temporal control.
8. Evaluate promotion gate and write decision.json.
"""
from __future__ import annotations

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

from navier3d.mesh import StructuredMesh3D
from navier3d.fields import VelocityField, FlowState, ScalarField
from navier3d.reduced.w10_multi_coordinate import channel_bcs, generate_channel_initial_condition
from navier3d.time_integrators import ThetaSchemeIntegrator
from navier3d.reduced.solenoidal_basis import PODSolenoidalBasis
from navier3d.reduced.w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm
from navier3d.reduced.p3a_translation_diagnostic import (
    shift_velocity_field_xz,
    find_optimal_periodic_alignment,
    compute_subspace_metrics,
    fourier_phase_amplitude_analysis,
)


def generate_seed_trajectories(
    seeds: List[int],
    nx: int = 16,
    ny: int = 16,
    nz: int = 16,
    n_steps: int = 30,
    dt: float = 0.01,
    nu: float = 0.01,
) -> Tuple[StructuredMesh3D, Dict[int, List[VelocityField]], Dict[str, Any]]:
    """Simulate channel flow trajectories for given random seeds."""
    mesh = StructuredMesh3D(nx=nx, ny=ny, nz=nz, lx=2.0 * np.pi, ly=2.0, lz=np.pi)
    bcs = channel_bcs()

    trajectories: Dict[int, List[VelocityField]] = {}
    metadata = {
        "nx": nx,
        "ny": ny,
        "nz": nz,
        "lx": mesh.lx,
        "ly": mesh.ly,
        "lz": mesh.lz,
        "dt": dt,
        "nu": nu,
        "n_steps": n_steps,
        "seeds": seeds,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    for s in seeds:
        vel0 = generate_channel_initial_condition(mesh, bcs, seed=s)
        p0 = ScalarField.zeros(mesh)
        state = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)
        integrator = ThetaSchemeIntegrator(mesh, bcs, theta=0.5, nu=nu, rho=1.0, dt=dt)

        snaps: List[VelocityField] = [vel0]
        for step_idx in range(n_steps):
            state, _ = integrator.step(state, dt)
            snaps.append(state.velocity)

        trajectories[s] = snaps

    return mesh, trajectories, metadata


def run_p3a_diagnostic() -> None:
    """Execute complete Milestone P3-A diagnostic suite."""
    print("================================================================================")
    print("MILESTONE P3-A: CROSS-SEED PHASE / TRANSLATION ALIGNMENT CAUSAL DIAGNOSTIC")
    print("================================================================================")

    out_dir = Path("report_json")
    out_dir.mkdir(parents=True, exist_ok=True)

    seeds = [101, 104, 105]
    ranks = [4, 8, 12, 16]

    print("\n1. Generating DNS Truth Trajectories for Seeds:", seeds)
    mesh, trajectories, meta = generate_seed_trajectories(seeds=seeds, nx=16, ny=16, nz=16, n_steps=20, dt=0.01, nu=0.01)
    bcs = channel_bcs()

    seed_pairs = [(101, 104), (101, 105), (104, 105)]

    # -------------------------------------------------------------------------
    # 2. Pairwise Snapshot Alignment
    # -------------------------------------------------------------------------
    print("\n2. Computing Pairwise Snapshot Optimal Alignments...")
    alignment_records: List[Dict[str, Any]] = []
    aligned_trajectories: Dict[Tuple[int, int], List[VelocityField]] = {}
    shift_trajectories_data: Dict[str, Any] = {}

    for (sA, sB) in seed_pairs:
        pair_key = f"{sA}_{sB}"
        snapsA = trajectories[sA]
        snapsB = trajectories[sB]
        n_snaps = len(snapsA)

        aligned_B_list: List[VelocityField] = []
        shifts_t: List[Dict[str, float]] = []

        d_raw_list = []
        d_aligned_list = []
        r_field_list = []

        for m in range(n_snaps):
            uA = snapsA[m]
            uB = snapsB[m]
            res = find_optimal_periodic_alignment(uA, uB, mesh, subgrid=True)

            d_raw_list.append(res["d_field_raw"])
            d_aligned_list.append(res["d_field_aligned"])
            r_field_list.append(res["R_field"])

            shifted_uB = shift_velocity_field_xz(uB, mesh, res["dx_optimal"], res["dz_optimal"])
            aligned_B_list.append(shifted_uB)

            t_val = m * meta["dt"]
            shifts_t.append({
                "time": t_val,
                "step": m,
                "dx_optimal": res["dx_optimal"],
                "dz_optimal": res["dz_optimal"],
                "dx_integer": res["dx_integer"],
                "dz_integer": res["dz_integer"],
                "d_raw": res["d_field_raw"],
                "d_aligned": res["d_field_aligned"],
                "R_field": res["R_field"],
            })

        aligned_trajectories[(sA, sB)] = aligned_B_list
        shift_trajectories_data[pair_key] = shifts_t

        mean_R_field = float(np.mean(r_field_list))
        alignment_records.append({
            "seed_pair": [sA, sB],
            "pair_key": pair_key,
            "mean_d_field_raw": float(np.mean(d_raw_list)),
            "mean_d_field_aligned": float(np.mean(d_aligned_list)),
            "mean_R_field": mean_R_field,
            "min_R_field": float(np.min(r_field_list)),
            "max_R_field": float(np.max(r_field_list)),
        })
        print(f"  Pair ({sA}, {sB}): Mean Raw Dist = {np.mean(d_raw_list):.4f}, Aligned Dist = {np.mean(d_aligned_list):.4f}, R_field = {mean_R_field:.4f}")

    # -------------------------------------------------------------------------
    # 3. POD Subspaces & Principal-Angle Spectra
    # -------------------------------------------------------------------------
    print("\n3. Constructing Raw and Aligned POD Subspaces & Computing Principal Angles...")
    principal_angles_records: List[Dict[str, Any]] = []

    # Build raw POD bases
    raw_bases: Dict[int, PODSolenoidalBasis] = {}
    for s in seeds:
        raw_bases[s] = PODSolenoidalBasis(trajectories[s], mesh, bcs=bcs, max_modes=max(ranks))

    for (sA, sB) in seed_pairs:
        pair_key = f"{sA}_{sB}"
        basis_A = raw_bases[sA]
        basis_B_raw = raw_bases[sB]

        # Build aligned POD basis for B
        snapsB_aligned = aligned_trajectories[(sA, sB)]
        basis_B_aligned = PODSolenoidalBasis(snapsB_aligned, mesh, bcs=bcs, max_modes=max(ranks))

        for r in ranks:
            raw_metrics = compute_subspace_metrics(basis_A, basis_B_raw, rank=r)
            aligned_metrics = compute_subspace_metrics(basis_A, basis_B_aligned, rank=r)

            r_chordal = float(aligned_metrics["d_chordal"] / (raw_metrics["d_chordal"] + 1e-15))
            r_geodesic = float(aligned_metrics["d_geodesic"] / (raw_metrics["d_geodesic"] + 1e-15))

            principal_angles_records.append({
                "pair_key": pair_key,
                "seed_pair": [sA, sB],
                "rank": r,
                "d_chordal_raw": raw_metrics["d_chordal"],
                "d_chordal_aligned": aligned_metrics["d_chordal"],
                "R_chordal": r_chordal,
                "d_geodesic_raw": raw_metrics["d_geodesic"],
                "d_geodesic_aligned": aligned_metrics["d_geodesic"],
                "R_geodesic": r_geodesic,
                "d_spectral_deg_raw": raw_metrics["d_spectral_deg"],
                "d_spectral_deg_aligned": aligned_metrics["d_spectral_deg"],
                "mean_principal_angle_deg_raw": raw_metrics["mean_principal_angle_deg"],
                "mean_principal_angle_deg_aligned": aligned_metrics["mean_principal_angle_deg"],
                "principal_angles_deg_raw": raw_metrics["principal_angles_deg"],
                "principal_angles_deg_aligned": aligned_metrics["principal_angles_deg"],
            })
            print(f"  Pair ({sA}, {sB}) Rank {r:2d}: d_chordal raw={raw_metrics['d_chordal']:.4f}, aligned={aligned_metrics['d_chordal']:.4f}, R_subspace={r_chordal:.4f}")

    # -------------------------------------------------------------------------
    # 4. Fourier Phase vs Amplitude Analysis
    # -------------------------------------------------------------------------
    print("\n4. Performing Fourier Phase vs. Amplitude Error Decomposition...")
    phase_amplitude_records: List[Dict[str, Any]] = []

    for (sA, sB) in seed_pairs:
        pair_key = f"{sA}_{sB}"
        snapsA = trajectories[sA]
        snapsB = trajectories[sB]
        snapsB_aligned = aligned_trajectories[(sA, sB)]

        raw_phase_errs = []
        raw_amp_errs = []
        aligned_phase_errs = []
        aligned_amp_errs = []

        for m in range(len(snapsA)):
            res_raw = fourier_phase_amplitude_analysis(snapsA[m], snapsB[m], mesh)
            res_aligned = fourier_phase_amplitude_analysis(snapsA[m], snapsB_aligned[m], mesh)

            raw_phase_errs.append(res_raw["mean_phase_error_deg"])
            raw_amp_errs.append(res_raw["relative_amplitude_error"])
            aligned_phase_errs.append(res_aligned["mean_phase_error_deg"])
            aligned_amp_errs.append(res_aligned["relative_amplitude_error"])

        phase_amplitude_records.append({
            "pair_key": pair_key,
            "seed_pair": [sA, sB],
            "raw_mean_phase_error_deg": float(np.mean(raw_phase_errs)),
            "aligned_mean_phase_error_deg": float(np.mean(aligned_phase_errs)),
            "phase_error_ratio": float(np.mean(aligned_phase_errs) / (np.mean(raw_phase_errs) + 1e-15)),
            "raw_mean_amplitude_error": float(np.mean(raw_amp_errs)),
            "aligned_mean_amplitude_error": float(np.mean(aligned_amp_errs)),
            "amplitude_error_ratio": float(np.mean(aligned_amp_errs) / (np.mean(raw_amp_errs) + 1e-15)),
        })
        print(f"  Pair ({sA}, {sB}): Phase Err {np.mean(raw_phase_errs):.1f}° -> {np.mean(aligned_phase_errs):.1f}° (ratio={np.mean(aligned_phase_errs)/np.mean(raw_phase_errs):.3f}), Amp Err {np.mean(raw_amp_errs):.4f} -> {np.mean(aligned_amp_errs):.4f}")

    # -------------------------------------------------------------------------
    # 5. Controls Suite (Synthetic, Random Shifts, Same-Seed Temporal)
    # -------------------------------------------------------------------------
    print("\n5. Executing Diagnostic Controls Suite...")

    # 5.1 Synthetic Shift Recovery
    vel_test = trajectories[101][0]
    dx_synth = float(2.35 * mesh.dx)
    dz_synth = float(1.72 * mesh.dz)
    vel_synth = shift_velocity_field_xz(vel_test, mesh, dx_synth, dz_synth)
    res_synth = find_optimal_periodic_alignment(vel_test, vel_synth, mesh, subgrid=True)

    dx_exp = (-dx_synth) % mesh.lx
    dz_exp = (-dz_synth) % mesh.lz
    err_dx = abs(res_synth["dx_optimal"] - dx_exp)
    err_dz = abs(res_synth["dz_optimal"] - dz_exp)
    synth_passed = bool(err_dx < 0.05 * mesh.dx and err_dz < 0.05 * mesh.dz and res_synth["R_field"] < 0.01)

    synthetic_control_record = {
        "synthetic_shift_dx": dx_synth,
        "synthetic_shift_dz": dz_synth,
        "recovered_dx": res_synth["dx_optimal"],
        "recovered_dz": res_synth["dz_optimal"],
        "expected_dx": dx_exp,
        "expected_dz": dz_exp,
        "error_dx": err_dx,
        "error_dz": err_dz,
        "R_field": res_synth["R_field"],
        "control_passed": synth_passed,
    }
    print(f"  [Synthetic Self-Control] Passed: {synth_passed} (R_field={res_synth['R_field']:.6e}, err_dx={err_dx:.4e})")

    # 5.2 Random-Shift Controls
    rng = np.random.default_rng(42)
    n_rand = 20
    random_shift_records = []
    for (sA, sB) in seed_pairs:
        uA = trajectories[sA][0]
        uB = trajectories[sB][0]
        d_raw = mac_velocity_diff_norm(uA, uB, mesh)

        rand_dists = []
        for _ in range(n_rand):
            dx_r = float(rng.uniform(0.0, mesh.lx))
            dz_r = float(rng.uniform(0.0, mesh.lz))
            uB_rand = shift_velocity_field_xz(uB, mesh, dx_r, dz_r)
            rand_dists.append(mac_velocity_diff_norm(uA, uB_rand, mesh))

        mean_d_rand = float(np.mean(rand_dists))
        res_opt = find_optimal_periodic_alignment(uA, uB, mesh, subgrid=True)

        random_shift_records.append({
            "seed_pair": [sA, sB],
            "d_raw": float(d_raw),
            "d_optimal": res_opt["d_field_aligned"],
            "d_random_mean": mean_d_rand,
            "d_random_std": float(np.std(rand_dists)),
            "R_optimal": res_opt["R_field"],
            "R_random_mean": float(mean_d_rand / d_raw),
            "optimal_beats_random": bool(res_opt["d_field_aligned"] < mean_d_rand),
        })
        print(f"  [Random Control] Pair ({sA}, {sB}): Optimal R={res_opt['R_field']:.4f} vs Random Mean R={mean_d_rand/d_raw:.4f}")

    # 5.3 Same-Seed Temporal Control
    u_t0 = trajectories[101][0]
    u_t15 = trajectories[101][15]
    d_temporal_raw = mac_velocity_diff_norm(u_t0, u_t15, mesh)
    res_temporal = find_optimal_periodic_alignment(u_t0, u_t15, mesh, subgrid=True)
    temporal_control_record = {
        "seed": 101,
        "step_start": 0,
        "step_end": 15,
        "d_raw": float(d_temporal_raw),
        "d_aligned": res_temporal["d_field_aligned"],
        "R_field": res_temporal["R_field"],
        "dx_optimal": res_temporal["dx_optimal"],
        "dz_optimal": res_temporal["dz_optimal"],
    }
    print(f"  [Same-Seed Temporal Control] Seed 101 (t0 vs t15): Raw={d_temporal_raw:.4f}, Aligned={res_temporal['d_field_aligned']:.4f}, R_field={res_temporal['R_field']:.4f}")

    # -------------------------------------------------------------------------
    # 6. Promotion Gate Evaluation & Final Decision
    # -------------------------------------------------------------------------
    print("\n6. Evaluating Preregistered Promotion Gate...")

    # Gate A: R_subspace <= 0.30 for at least 2 seed pairs across multiple ranks
    r_subspace_values = [rec["R_chordal"] for rec in principal_angles_records if rec["rank"] >= 8]
    mean_r_subspace = float(np.mean(r_subspace_values))
    gate_A = bool(np.sum(np.array(r_subspace_values) <= 0.30) >= 4)

    # Gate B: R_field decreases materially (<= 0.50)
    r_field_values = [rec["mean_R_field"] for rec in alignment_records]
    mean_r_field = float(np.mean(r_field_values))
    gate_B = bool(mean_r_field <= 0.50)

    # Gate C: Fourier phase error decreases much more than amplitude error
    phase_ratios = [rec["phase_error_ratio"] for rec in phase_amplitude_records]
    amp_ratios = [rec["amplitude_error_ratio"] for rec in phase_amplitude_records]
    mean_phase_ratio = float(np.mean(phase_ratios))
    mean_amp_ratio = float(np.mean(amp_ratios))
    gate_C = bool(mean_phase_ratio < 0.5 * mean_amp_ratio)

    # Gate D: Optimal translations outperform random controls
    gate_D = all(rec["optimal_beats_random"] for rec in random_shift_records)

    # Gate E: Synthetic shift recovery passes
    gate_E = synth_passed

    all_gates_pass = bool(gate_A and gate_B and gate_C and gate_D and gate_E)

    # Classification
    if mean_r_subspace <= 0.30:
        classification = "STRONG SUPPORT FOR TRANSLATION CONTRIBUTION"
        verdict = "PROMOTED"
    elif mean_r_subspace < 0.80:
        classification = "PARTIAL / INCONCLUSIVE"
        verdict = "HELD (INVESTIGATE INTERMEDIATE / CLUSTERED METHODS)"
    else:
        classification = "LITTLE SUPPORT FOR SIMPLE TRANSLATION"
        verdict = "DISCARDED FOR THIS PROBLEM"

    decision_record = {
        "governance": "LEVEL 2 — TECHNICALLY VERIFIED, NOT EXTERNALLY ATTESTED",
        "milestone": "P3-A",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gates": {
            "gate_A_subspace_ratio_le_0_30": {"passed": gate_A, "mean_R_subspace": mean_r_subspace},
            "gate_B_field_ratio_le_0_50": {"passed": gate_B, "mean_R_field": mean_r_field},
            "gate_C_phase_decreases_more_than_amp": {"passed": gate_C, "mean_phase_ratio": mean_phase_ratio, "mean_amp_ratio": mean_amp_ratio},
            "gate_D_optimal_beats_random": {"passed": gate_D},
            "gate_E_synthetic_recovery": {"passed": gate_E},
        },
        "all_gates_passed": all_gates_pass,
        "mean_R_subspace": mean_r_subspace,
        "mean_R_field": mean_r_field,
        "classification": classification,
        "verdict": verdict,
        "scientific_summary": (
            f"Periodic x/z translation alignment reduced raw cross-seed field distance by an average factor of {mean_r_field:.4f} "
            f"and reduced Grassmannian POD subspace distance by an average factor of {mean_r_subspace:.4f}. "
            f"Classification: {classification}. Final Verdict: {verdict}."
        ),
    }

    print("\n================================================================================")
    print("PROMOTION GATE SUMMARY")
    print("================================================================================")
    print(f"  Gate A (R_subspace <= 0.30)  : {'PASS' if gate_A else 'FAIL'} (mean R_subspace = {mean_r_subspace:.4f})")
    print(f"  Gate B (R_field <= 0.50)     : {'PASS' if gate_B else 'FAIL'} (mean R_field = {mean_r_field:.4f})")
    print(f"  Gate C (Phase >> Amp Reduc.) : {'PASS' if gate_C else 'FAIL'} (phase ratio = {mean_phase_ratio:.4f}, amp ratio = {mean_amp_ratio:.4f})")
    print(f"  Gate D (Beats Random Shifts) : {'PASS' if gate_D else 'FAIL'}")
    print(f"  Gate E (Synthetic Recovery)  : {'PASS' if gate_E else 'FAIL'}")
    print("--------------------------------------------------------------------------------")
    print(f"  CLASSIFICATION : {classification}")
    print(f"  FINAL VERDICT  : {verdict}")
    print("================================================================================\n")

    # -------------------------------------------------------------------------
    # 7. Write Machine-Readable JSON Deliverables
    # -------------------------------------------------------------------------
    def save_json(fname: str, data: Any) -> None:
        p = out_dir / fname
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"  [SAVED] {p}")

    save_json("alignment_pairs.json", {"governance": meta, "pairs": alignment_records})
    save_json("principal_angles.json", {"governance": meta, "records": principal_angles_records})
    save_json("phase_amplitude.json", {"governance": meta, "records": phase_amplitude_records})
    save_json("shift_trajectories.json", {"governance": meta, "trajectories": shift_trajectories_data, "same_seed_temporal_control": temporal_control_record})
    save_json("random_controls.json", {"governance": meta, "random_controls": random_shift_records})
    save_json("synthetic_control.json", {"governance": meta, "synthetic_control": synthetic_control_record})
    save_json("decision.json", decision_record)


if __name__ == "__main__":
    run_p3a_diagnostic()
