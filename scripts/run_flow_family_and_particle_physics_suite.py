"""Flow-Family Hypothesis (TH2) and Physics + Particle History Investigation.

Executes:
1. Expanded Flow-Family Benchmark (4 Isotropic Decay G1 vs 4 Structured G3: 2 Taylor-Green + 2 Shear Layer).
2. Flow-Family specific Connectivity Effect (C_ROC) and Memory Effect (M_ROC).
3. Phase 8 Test: Eulerian Physics vs Eulerian Physics + Ordered Particle History vs Eulerian Physics + Shuffled Particle History.
4. Generates data for FLOW_FAMILY_ANALYSIS.md.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from navier3d.experimental.th1_suite import generate_flow_dataset
from navier3d.experimental.th1_targets_and_models import evaluate_lofo_classifier


def main():
    t0 = time.time()
    print("=" * 75)
    print("RUNNING FLOW-FAMILY EXPANDED BENCHMARK AND PHYSICS+PARTICLE SUITE")
    print("=" * 75)

    # 8 independent flow configurations: 4 G1 Isotropic, 4 G3 Structured
    expanded_configs = [
        # G1 Isotropic Seeds
        {"id": "flow_iso_seed101", "family": "isotropic", "re": 100.0, "seed": 101, "tier": "G1", "grid": 16},
        {"id": "flow_iso_seed102", "family": "isotropic", "re": 100.0, "seed": 102, "tier": "G1", "grid": 16},
        {"id": "flow_iso_seed103", "family": "isotropic", "re": 100.0, "seed": 103, "tier": "G1", "grid": 16},
        {"id": "flow_iso_seed104", "family": "isotropic", "re": 100.0, "seed": 104, "tier": "G1", "grid": 16},
        # G3 Structured Flows (2 Taylor-Green + 2 Shear Layer)
        {"id": "flow_tg_phase01", "family": "taylor_green", "re": 100.0, "seed": 201, "tier": "G3", "grid": 16},
        {"id": "flow_tg_phase02", "family": "taylor_green", "re": 100.0, "seed": 202, "tier": "G3", "grid": 16},
        {"id": "flow_shear_layer01", "family": "shear_layer", "re": 100.0, "seed": 301, "tier": "G3", "grid": 16},
        {"id": "flow_shear_layer02", "family": "shear_layer", "re": 100.0, "seed": 302, "tier": "G3", "grid": 16},
    ]

    print(f"Generating datasets for {len(expanded_configs)} physical flows...")
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
        for cfg in expanded_configs
    ]

    print("Evaluating LOFO models across all 8 flows...")
    # 1. Base representations
    res_p0_ord = evaluate_lofo_classifier(datasets, lambda d: d.p0_hist_int)
    res_p1_ord = evaluate_lofo_classifier(datasets, lambda d: d.p1_hist_int)
    res_p1_shuff = evaluate_lofo_classifier(datasets, lambda d: d.p1_shuff_int)
    res_p2_ord = evaluate_lofo_classifier(datasets, lambda d: d.p2_hist_int)
    
    # 2. Eulerian Physics vs Physics + Particle History (Phase 8 test)
    res_phys = evaluate_lofo_classifier(datasets, lambda d: d.physics_feats)
    res_phys_p0_ord = evaluate_lofo_classifier(
        datasets, lambda d: np.hstack([d.physics_feats, d.p0_hist_int])
    )
    res_phys_p0_shuff = evaluate_lofo_classifier(
        datasets, lambda d: np.hstack([d.physics_feats, d.p0_shuff_int])
    )
    res_phys_p1_ord = evaluate_lofo_classifier(
        datasets, lambda d: np.hstack([d.physics_feats, d.p1_hist_int])
    )

    # Compile Per-Flow breakdown
    n_flows = len(datasets)
    per_flow_records = []
    for i in range(n_flows):
        d = datasets[i]
        fid = d.flow_id
        tier = d.generalization_tier
        family = d.flow_family
        prev = float(np.mean(d.targets[0.25]))

        p0_auc = res_p0_ord["flow_metrics"][i]["roc_auc"]
        p1_auc = res_p1_ord["flow_metrics"][i]["roc_auc"]
        p1_shuff_auc = res_p1_shuff["flow_metrics"][i]["roc_auc"]
        p2_auc = res_p2_ord["flow_metrics"][i]["roc_auc"]
        phys_auc = res_phys["flow_metrics"][i]["roc_auc"]
        phys_p0_auc = res_phys_p0_ord["flow_metrics"][i]["roc_auc"]
        phys_p0_shuff_auc = res_phys_p0_shuff["flow_metrics"][i]["roc_auc"]
        phys_p1_auc = res_phys_p1_ord["flow_metrics"][i]["roc_auc"]

        c_roc = p1_auc - p0_auc
        m_roc = p1_auc - p1_shuff_auc
        g_particle_roc = phys_p0_auc - phys_auc
        g_thread_roc = phys_p1_auc - phys_auc
        p0_memory_over_phys = phys_p0_auc - phys_p0_shuff_auc

        per_flow_records.append({
            "flow_id": fid,
            "family": family,
            "tier": tier,
            "prevalence": prev,
            "P0_roc": p0_auc,
            "P1_roc": p1_auc,
            "P1_shuff_roc": p1_shuff_auc,
            "P2_roc": p2_auc,
            "Physics_roc": phys_auc,
            "Phys_plus_P0_ord_roc": phys_p0_auc,
            "Phys_plus_P0_shuff_roc": phys_p0_shuff_auc,
            "Phys_plus_P1_ord_roc": phys_p1_auc,
            "C_roc": c_roc,
            "M_roc": m_roc,
            "G_particle_roc": g_particle_roc,
            "G_thread_roc": g_thread_roc,
            "P0_memory_over_phys": p0_memory_over_phys,
        })

    # Summary by Tier (G1 vs G3)
    def _mean(key, t=None):
        vals = [r[key] for r in per_flow_records if (t is None or r["tier"] == t)]
        return float(np.mean(vals))

    flow_family_summary = {
        "n_flows_total": n_flows,
        "n_g1_isotropic": sum(1 for r in per_flow_records if r["tier"] == "G1"),
        "n_g3_structured": sum(1 for r in per_flow_records if r["tier"] == "G3"),
        "G1_Isotropic": {
            "P0_roc_mean": _mean("P0_roc", "G1"),
            "P1_roc_mean": _mean("P1_roc", "G1"),
            "Connectivity_C_roc_mean": _mean("C_roc", "G1"),
            "Memory_M_roc_mean": _mean("M_roc", "G1"),
            "Physics_roc_mean": _mean("Physics_roc", "G1"),
            "Phys_plus_P0_roc_mean": _mean("Phys_plus_P0_ord_roc", "G1"),
            "G_particle_roc_mean": _mean("G_particle_roc", "G1"),
            "G_thread_roc_mean": _mean("G_thread_roc", "G1"),
        },
        "G3_Structured": {
            "P0_roc_mean": _mean("P0_roc", "G3"),
            "P1_roc_mean": _mean("P1_roc", "G3"),
            "Connectivity_C_roc_mean": _mean("C_roc", "G3"),
            "Memory_M_roc_mean": _mean("M_roc", "G3"),
            "Physics_roc_mean": _mean("Physics_roc", "G3"),
            "Phys_plus_P0_roc_mean": _mean("Phys_plus_P0_ord_roc", "G3"),
            "G_particle_roc_mean": _mean("G_particle_roc", "G3"),
            "G_thread_roc_mean": _mean("G_thread_roc", "G3"),
        },
        "Overall_All_8_Flows": {
            "P0_roc_mean": _mean("P0_roc"),
            "P1_roc_mean": _mean("P1_roc"),
            "Connectivity_C_roc_mean": _mean("C_roc"),
            "Memory_M_roc_mean": _mean("M_roc"),
            "Physics_roc_mean": _mean("Physics_roc"),
            "Phys_plus_P0_roc_mean": _mean("Phys_plus_P0_ord_roc"),
            "Phys_plus_P0_shuff_roc_mean": _mean("Phys_plus_P0_shuff_roc"),
            "G_particle_roc_mean": _mean("G_particle_roc"),
            "G_thread_roc_mean": _mean("G_thread_roc"),
        },
        "per_flow_records": per_flow_records,
    }

    out_file = Path("evidence/flow_family_analysis_results.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(flow_family_summary, f, indent=2)

    print("\n" + "=" * 75)
    print("FLOW FAMILY (TH2) AND PHYSICS + PARTICLE SUMMARY")
    print("=" * 75)
    print(f"G1 Isotropic Connectivity C:  {flow_family_summary['G1_Isotropic']['Connectivity_C_roc_mean']:+.4f}")
    print(f"G3 Structured Connectivity C: {flow_family_summary['G3_Structured']['Connectivity_C_roc_mean']:+.4f}")
    print(f"Physics alone (Mean ROC):     {flow_family_summary['Overall_All_8_Flows']['Physics_roc_mean']:.4f}")
    print(f"Physics + P0 Particle (ROC):  {flow_family_summary['Overall_All_8_Flows']['Phys_plus_P0_roc_mean']:.4f}")
    print(f"Physics + P1 Thread (ROC):    {flow_family_summary['Overall_All_8_Flows']['G_thread_roc_mean']:+.4f}")
    print(f"Saved results to {out_file.resolve()}")


if __name__ == "__main__":
    main()
