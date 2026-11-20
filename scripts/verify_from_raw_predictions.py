"""Independent Metric Recomputation directly from RAW_HELDOUT_PREDICTIONS.csv.

Does NOT read decision.json, primary_effects.json, or summary files.
Computes ROC-AUC, PR-AUC, PR skill, Brier score, Tier averages, and Bootstrap CIs.
Generates OLD_VS_NEW_METRICS.csv and returns exact recomputed values.
"""
from __future__ import annotations

import csv
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, balanced_accuracy_score


def bootstrap_ci(values: np.ndarray, n_boot: int = 2000, ci: float = 0.95, seed: int = 42) -> tuple[float, float]:
    rng = np.random.RandomState(seed)
    n = len(values)
    boot_means = []
    for _ in range(n_boot):
        sample = rng.choice(values, size=n, replace=True)
        boot_means.append(np.mean(sample))
    alpha = (1.0 - ci) / 2.0
    low = float(np.percentile(boot_means, 100.0 * alpha))
    high = float(np.percentile(boot_means, 100.0 * (1.0 - alpha)))
    return low, high


def main():
    csv_path = Path("RAW_HELDOUT_PREDICTIONS.csv")
    assert csv_path.exists(), f"File {csv_path} does not exist!"

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} raw prediction records across {df['representation'].nunique()} representations and {df['flow_id'].nunique()} flows.")

    reps = df["representation"].unique()
    flows = df["flow_id"].unique()
    flow_tiers = df.groupby("flow_id")["tier"].first().to_dict()

    # Compute fold-level metrics for each representation
    results_by_rep = {}
    for rep in reps:
        df_rep = df[df["representation"] == rep]
        fold_metrics = []
        for fid in flows:
            sub = df_rep[df_rep["flow_id"] == fid]
            y_true = sub["target_y_true"].values
            y_score = sub["predicted_probability_y_score"].values
            y_pred = sub["predicted_class"].values
            prev = float(np.mean(y_true))
            
            auc = float(roc_auc_score(y_true, y_score)) if len(np.unique(y_true)) > 1 else 0.5
            pr_auc = float(average_precision_score(y_true, y_score)) if len(np.unique(y_true)) > 1 else prev
            brier = float(brier_score_loss(y_true, y_score))
            bal_acc = float(balanced_accuracy_score(y_true, y_pred))
            pr_skill = float(pr_auc - prev)

            fold_metrics.append({
                "flow_id": fid,
                "tier": flow_tiers[fid],
                "prevalence": prev,
                "roc_auc": auc,
                "pr_auc": pr_auc,
                "pr_skill": pr_skill,
                "brier": brier,
                "bal_acc": bal_acc,
            })

        # Pooled metrics across all 320 samples
        all_y_true = df_rep["target_y_true"].values
        all_y_score = df_rep["predicted_probability_y_score"].values
        pooled_auc = float(roc_auc_score(all_y_true, all_y_score))
        pooled_pr = float(average_precision_score(all_y_true, all_y_score))
        pooled_brier = float(brier_score_loss(all_y_true, all_y_score))

        mean_auc = float(np.mean([m["roc_auc"] for m in fold_metrics]))
        g1_auc = float(np.mean([m["roc_auc"] for m in fold_metrics if m["tier"] == "G1"]))
        g3_auc = float(np.mean([m["roc_auc"] for m in fold_metrics if m["tier"] == "G3"]))

        results_by_rep[rep] = {
            "mean_auc": mean_auc,
            "g1_auc": g1_auc,
            "g3_auc": g3_auc,
            "pooled_auc": pooled_auc,
            "pooled_pr": pooled_pr,
            "pooled_brier": pooled_brier,
            "fold_metrics": fold_metrics,
        }

    # Primary Effects Recomputation
    p1_ord = results_by_rep["p1_thread_hist_intrinsic"]["fold_metrics"]
    p1_shuff = results_by_rep["p1_thread_shuff_intrinsic"]["fold_metrics"]
    p0_ord = results_by_rep["p0_particle_hist_intrinsic"]["fold_metrics"]
    p2_ord = results_by_rep["p2_bundle_hist_intrinsic"]["fold_metrics"]
    p1_abs = results_by_rep["p1_thread_hist_absolute"]["fold_metrics"]
    phys = results_by_rep["eulerian_physics"]["fold_metrics"]
    phys_geo = results_by_rep["physics_plus_geometry"]["fold_metrics"]

    n_flows = len(flows)
    m_roc_arr = np.array([p1_ord[i]["roc_auc"] - p1_shuff[i]["roc_auc"] for i in range(n_flows)])
    m_pr_arr = np.array([p1_ord[i]["pr_auc"] - p1_shuff[i]["pr_auc"] for i in range(n_flows)])
    m_brier_arr = np.array([p1_shuff[i]["brier"] - p1_ord[i]["brier"] for i in range(n_flows)])

    c_roc_arr = np.array([p1_ord[i]["roc_auc"] - p0_ord[i]["roc_auc"] for i in range(n_flows)])
    b_roc_arr = np.array([p2_ord[i]["roc_auc"] - p1_ord[i]["roc_auc"] for i in range(n_flows)])
    g_roc_arr = np.array([phys_geo[i]["roc_auc"] - phys[i]["roc_auc"] for i in range(n_flows)])
    l_roc_arr = np.array([p1_abs[i]["roc_auc"] - p1_ord[i]["roc_auc"] for i in range(n_flows)])

    g1_mask = np.array([p1_ord[i]["tier"] == "G1" for i in range(n_flows)])
    g3_mask = np.array([p1_ord[i]["tier"] == "G3" for i in range(n_flows)])

    m_ci = bootstrap_ci(m_roc_arr)
    c_ci = bootstrap_ci(c_roc_arr)
    b_ci = bootstrap_ci(b_roc_arr)
    g_ci = bootstrap_ci(g_roc_arr)
    l_ci = bootstrap_ci(l_roc_arr)

    print("\n" + "=" * 75)
    print("INDEPENDENTLY RECOMPUTED PRIMARY EFFECTS FROM RAW PREDICTIONS")
    print("=" * 75)
    print(f"Memory M_ROC:        {np.mean(m_roc_arr):+.4f} | G1: {np.mean(m_roc_arr[g1_mask]):+.4f}, G3: {np.mean(m_roc_arr[g3_mask]):+.4f} | 95% CI: [{m_ci[0]:+.4f}, {m_ci[1]:+.4f}]")
    print(f"Connectivity C_ROC:  {np.mean(c_roc_arr):+.4f} | G1: {np.mean(c_roc_arr[g1_mask]):+.4f}, G3: {np.mean(c_roc_arr[g3_mask]):+.4f} | 95% CI: [{c_ci[0]:+.4f}, {c_ci[1]:+.4f}]")
    print(f"Multidirection B_ROC:{np.mean(b_roc_arr):+.4f} | G1: {np.mean(b_roc_arr[g1_mask]):+.4f}, G3: {np.mean(b_roc_arr[g3_mask]):+.4f} | 95% CI: [{b_ci[0]:+.4f}, {b_ci[1]:+.4f}]")
    print(f"Physics Comp G_ROC:  {np.mean(g_roc_arr):+.4f} | G1: {np.mean(g_roc_arr[g1_mask]):+.4f}, G3: {np.mean(g_roc_arr[g3_mask]):+.4f} | 95% CI: [{g_ci[0]:+.4f}, {g_ci[1]:+.4f}]")
    print(f"Location L_ROC:      {np.mean(l_roc_arr):+.4f} | G1: {np.mean(l_roc_arr[g1_mask]):+.4f}, G3: {np.mean(l_roc_arr[g3_mask]):+.4f} | 95% CI: [{l_ci[0]:+.4f}, {l_ci[1]:+.4f}]")

    print("\n" + "=" * 75)
    print("P0 PARTICLE HISTORY SIGNAL (RAW PREDICTIONS)")
    print("=" * 75)
    p0_res = results_by_rep["p0_particle_hist_intrinsic"]
    print(f"P0 Mean LOFO ROC:    {p0_res['mean_auc']:.4f}")
    print(f"P0 G1 (Isotropic):   {p0_res['g1_auc']:.4f}")
    print(f"P0 G3 (Shear/TG):    {p0_res['g3_auc']:.4f}")
    print(f"P0 Pooled ROC:       {p0_res['pooled_auc']:.4f}")
    print(f"P0 Pooled PR-AUC:    {p0_res['pooled_pr']:.4f} (Prevalence ~ 0.2594)")

    # Build OLD_VS_NEW_METRICS.csv
    old_metrics = [
        ("Memory_M_ROC", 0.0445, np.mean(m_roc_arr), m_ci, "Ordered history vs Shuffled history"),
        ("Connectivity_C_ROC_overall", -0.0670, np.mean(c_roc_arr), c_ci, "Thread history vs Particle history"),
        ("Connectivity_C_ROC_G1_isotropic", -0.2073, np.mean(c_roc_arr[g1_mask]), bootstrap_ci(c_roc_arr[g1_mask]), "Thread vs Particle on Isotropic"),
        ("Connectivity_C_ROC_G3_structured", 0.1430, np.mean(c_roc_arr[g3_mask]), bootstrap_ci(c_roc_arr[g3_mask]), "Thread vs Particle on Shear/TG"),
        ("Multidirection_B_ROC", -0.1163, np.mean(b_roc_arr), b_ci, "Bundle history vs Thread history"),
        ("Physics_Complement_G_ROC", -0.0268, np.mean(g_roc_arr), g_ci, "Physics+Geometry vs Physics alone"),
        ("Location_L_ROC", -0.0169, np.mean(l_roc_arr), l_ci, "Absolute vs Intrinsic representation"),
        ("P0_Particle_Mean_LOFO_ROC", 0.6272, p0_res["mean_auc"], bootstrap_ci(np.array([m["roc_auc"] for m in p0_ord])), "P0 mean within-fold ROC"),
        ("P0_Particle_G1_ROC", 0.7247, p0_res["g1_auc"], bootstrap_ci(np.array([m["roc_auc"] for m in p0_ord if m["tier"] == "G1"])), "P0 isotropic G1 mean ROC"),
        ("P0_Particle_G3_ROC", 0.4815, p0_res["g3_auc"], bootstrap_ci(np.array([m["roc_auc"] for m in p0_ord if m["tier"] == "G3"])), "P0 shear/TG G3 mean ROC"),
        ("P0_Particle_Pooled_ROC", 0.5477, p0_res["pooled_auc"], (0.0, 0.0), "P0 global pooled ROC"),
        ("P1_Thread_Mean_LOFO_ROC", 0.5602, results_by_rep["p1_thread_hist_intrinsic"]["mean_auc"], bootstrap_ci(np.array([m["roc_auc"] for m in p1_ord])), "P1 mean within-fold ROC"),
        ("Eulerian_Physics_Mean_LOFO_ROC", 0.7869, results_by_rep["eulerian_physics"]["mean_auc"], bootstrap_ci(np.array([m["roc_auc"] for m in phys])), "Eulerian physics ROC"),
    ]

    out_csv = Path("OLD_VS_NEW_METRICS.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "metric_name",
            "old_reference_value",
            "new_clean_replication_value",
            "absolute_delta",
            "relative_delta_percent",
            "ci_95_low",
            "ci_95_high",
            "interpretation",
        ])
        for name, old_val, new_val, ci_tup, interp in old_metrics:
            abs_delta = float(new_val - old_val)
            rel_delta = float(abs_delta / (abs(old_val) + 1e-12) * 100.0)
            writer.writerow([
                name,
                f"{old_val:.4f}",
                f"{new_val:.4f}",
                f"{abs_delta:+.6f}",
                f"{rel_delta:+.2f}%",
                f"{ci_tup[0]:.4f}",
                f"{ci_tup[1]:.4f}",
                interp,
            ])

    print(f"\nGenerated {out_csv.resolve()}")


if __name__ == "__main__":
    main()
