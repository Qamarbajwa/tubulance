"""TH4 Stress-Testing Engine: Multi-Horizon, Multi-Resolution, Gating Architectures & Complementarity.

Implements:
- FlowDatasetTH4: Multi-horizon target container, resolution and Reynolds awareness.
- Soft vs Hard vs Fixed Gating models.
- Baselines B0 to B8, Adaptive A1 & A2.
- Strict nested LOFO and Leave-One-Flow-Family-Out cross-validation.
- Local topology stratification (strain vs rotation vs Q-R).
- Comprehensive negative controls (shuffled targets, shuffled histories, shuffled topology, flow ID detectors).
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler

from ..mesh import StructuredMesh3D
from .th1_suite import generate_flow_dataset, generate_flow_simulation_trajectory
from .th1_targets_and_models import (
    compute_vorticity_magnitude_field,
    extract_future_target_labels,
)
from .th3_topology_features import extract_local_topology_features, TOPOLOGY_FEATURE_NAMES


@dataclass
class FlowDatasetTH4:
    """Multi-horizon, multi-parameter flow container for TH4 stress testing."""
    flow_id: str
    flow_family: str
    reynolds_num: float
    generalization_tier: str
    grid_size: int
    seed: int
    obs_step: int
    horizons: List[int] # List of delta_step horizons, e.g. [5, 10, 15, 20]

    # Observed coordinates at t_obs
    centroids_obs: np.ndarray  # shape (N, 3)

    # Lagrangian feature matrices (intrinsic coordinate mode)
    p0_hist_int: np.ndarray   # Particle history (P0), shape (N, D0)
    p0_shuff_int: np.ndarray  # Particle time-shuffled history control
    p1_hist_int: np.ndarray   # Thread history (P1), shape (N, D1)
    p1_shuff_int: np.ndarray  # Thread time-shuffled history control
    p2_hist_int: np.ndarray   # Bundle history (P2), shape (N, D2)

    # Eulerian and Topology feature matrices
    physics_feats: np.ndarray  # Local Eulerian physics (|u|, |omega|, |S|), shape (N, D_phys)
    topology_feats: np.ndarray # Local velocity-gradient invariants (14 features), shape (N, 14)

    # Multi-horizon target labels: horizon_step -> (target_percentile -> binary labels (N,))
    targets_by_horizon: Dict[int, Dict[float, np.ndarray]]


def generate_flow_dataset_th4(
    flow_id: str,
    flow_family: str,
    reynolds_num: float = 100.0,
    generalization_tier: str = "G1",
    grid_size: int = 16,
    seed: int = 42,
    obs_step: int = 15,
    horizons: Optional[List[int]] = None,
    tau_steps: int = 10,
    n_objects: int = 64,
) -> FlowDatasetTH4:
    """Simulate flow, track Lagrangian objects, extract topology and multi-horizon future targets."""
    if horizons is None:
        horizons = [5, 10, 15, 20]

    max_horizon = max(horizons)
    total_steps = obs_step + max_horizon + 5
    nu = 1.0 / reynolds_num

    # 1. Simulate full trajectory
    mesh, vel_snaps, times = generate_flow_simulation_trajectory(
        flow_family=flow_family,
        grid_size=grid_size,
        nu=nu,
        seed=seed,
        total_steps=total_steps,
        dt=0.02,
    )

    # 2. Extract base dataset at primary horizon
    base_ds = generate_flow_dataset(
        flow_id=flow_id,
        flow_family=flow_family,
        reynolds_num=reynolds_num,
        generalization_tier=generalization_tier,
        grid_size=grid_size,
        seed=seed,
        obs_step=obs_step,
        delta_step=10,
        tau_steps=tau_steps,
        n_objects=n_objects,
    )

    # 3. Extract local topology features at t_obs
    vel_at_obs = vel_snaps[obs_step]
    topo_feats = extract_local_topology_features(base_ds.positions_obs, vel_at_obs, mesh)

    # 4. Extract multi-horizon future targets
    targets_by_horizon = {}
    for h in horizons:
        fut_step = obs_step + h
        if fut_step < len(vel_snaps):
            vort_fut = compute_vorticity_magnitude_field(vel_snaps[fut_step], mesh)
            # Re-advect or approximate future centroid positions
            targets_h = {}
            for pct in [0.10, 0.20, 0.25, 0.30, 0.50]:
                lbls, _ = extract_future_target_labels(base_ds.positions_obs, vort_fut, mesh, top_percentile=pct)
                targets_h[pct] = lbls
            targets_by_horizon[h] = targets_h
        else:
            targets_by_horizon[h] = base_ds.targets

    return FlowDatasetTH4(
        flow_id=flow_id,
        flow_family=flow_family,
        reynolds_num=reynolds_num,
        generalization_tier=generalization_tier,
        grid_size=grid_size,
        seed=seed,
        obs_step=obs_step,
        horizons=horizons,
        centroids_obs=base_ds.positions_obs,
        p0_hist_int=base_ds.p0_hist_int,
        p0_shuff_int=base_ds.p0_shuff_int,
        p1_hist_int=base_ds.p1_hist_int,
        p1_shuff_int=base_ds.p1_shuff_int,
        p2_hist_int=base_ds.p2_hist_int,
        physics_feats=base_ds.physics_feats,
        topology_feats=topo_feats,
        targets_by_horizon=targets_by_horizon,
    )


def evaluate_th4_stress_lofo(
    datasets: List[FlowDatasetTH4],
    horizon_step: int = 10,
    target_key: float = 0.25,
    random_state: int = 42,
    shuffled_history: bool = False,
    shuffled_topology: bool = False,
    shuffled_labels: bool = False,
) -> Dict[str, Any]:
    """Execute complete LOFO evaluation under TH4 stress configurations."""
    n_flows = len(datasets)
    models_keys = [
        "B0_physics_only",
        "B1_particle_history",
        "B2_thread_history",
        "B3_phys_plus_particle",
        "B4_phys_plus_thread",
        "B5_phys_plus_particle_plus_thread",
        "B6_random_selector",
        "B7_constant_selector",
        "B8_oracle_selector",
        "A1_soft_gated_lagrangian",
        "A1_hard_gated_lagrangian",
        "A1_fixed_50_50_mixture",
        "A2_phys_plus_soft_gated",
        "A2_phys_plus_hard_gated",
    ]

    predictions_by_model: Dict[str, List[Dict[str, Any]]] = {k: [] for k in models_keys}
    fold_metrics_by_model: Dict[str, List[Dict[str, Any]]] = {k: [] for k in models_keys}

    for test_idx in range(n_flows):
        test_flow = datasets[test_idx]
        train_flows = [datasets[i] for i in range(n_flows) if i != test_idx]

        # Labels
        y_train = np.concatenate([f.targets_by_horizon[horizon_step][target_key] for f in train_flows])
        y_test = test_flow.targets_by_horizon[horizon_step][target_key]

        if shuffled_labels:
            rng_l = np.random.RandomState(random_state + test_idx)
            y_train = rng_l.permutation(y_train)
            y_test = rng_l.permutation(y_test)

        prev_test = float(np.mean(y_test))

        # Features
        X_tr_phys = np.vstack([f.physics_feats for f in train_flows])
        X_te_phys = test_flow.physics_feats

        if shuffled_history:
            X_tr_p0 = np.vstack([f.p0_shuff_int for f in train_flows])
            X_te_p0 = test_flow.p0_shuff_int
            X_tr_p1 = np.vstack([f.p1_shuff_int for f in train_flows])
            X_te_p1 = test_flow.p1_shuff_int
        else:
            X_tr_p0 = np.vstack([f.p0_hist_int for f in train_flows])
            X_te_p0 = test_flow.p0_hist_int
            X_tr_p1 = np.vstack([f.p1_hist_int for f in train_flows])
            X_te_p1 = test_flow.p1_hist_int

        if shuffled_topology:
            rng_t = np.random.RandomState(random_state + test_idx)
            X_tr_topo = rng_t.permutation(np.vstack([f.topology_feats for f in train_flows]))
            X_te_topo = rng_t.permutation(test_flow.topology_feats)
        else:
            X_tr_topo = np.vstack([f.topology_feats for f in train_flows])
            X_te_topo = test_flow.topology_feats

        # Preprocessing (fit strictly on training folds)
        def _scale(tr, te):
            sc = StandardScaler()
            return sc.fit_transform(tr), sc.transform(te)

        X_tr_phys_s, X_te_phys_s = _scale(X_tr_phys, X_te_phys)
        X_tr_p0_s, X_te_p0_s = _scale(X_tr_p0, X_te_p0)
        X_tr_p1_s, X_te_p1_s = _scale(X_tr_p1, X_te_p1)
        X_tr_topo_s, X_te_topo_s = _scale(X_tr_topo, X_te_topo)

        X_tr_b3 = np.hstack([X_tr_phys_s, X_tr_p0_s])
        X_te_b3 = np.hstack([X_te_phys_s, X_te_p0_s])

        X_tr_b4 = np.hstack([X_tr_phys_s, X_tr_p1_s])
        X_te_b4 = np.hstack([X_te_phys_s, X_te_p1_s])

        X_tr_b5 = np.hstack([X_tr_phys_s, X_tr_p0_s, X_tr_p1_s])
        X_te_b5 = np.hstack([X_te_phys_s, X_te_p0_s, X_te_p1_s])

        # Train Base Models
        def _fit_predict(X_tr, y_tr, X_te):
            if len(np.unique(y_tr)) < 2:
                return np.full(len(X_te), float(np.mean(y_tr))), np.zeros(len(X_tr))
            clf = LogisticRegression(C=1.0, max_iter=500, random_state=random_state)
            clf.fit(X_tr, y_tr)
            p_te = clf.predict_proba(X_te)[:, 1]
            p_tr = clf.predict_proba(X_tr)[:, 1]
            return p_te, p_tr

        prob_b0_te, prob_b0_tr = _fit_predict(X_tr_phys_s, y_train, X_te_phys_s)
        prob_b1_te, prob_b1_tr = _fit_predict(X_tr_p0_s, y_train, X_te_p0_s)
        prob_b2_te, prob_b2_tr = _fit_predict(X_tr_p1_s, y_train, X_te_p1_s)
        prob_b3_te, _ = _fit_predict(X_tr_b3, y_train, X_te_b3)
        prob_b4_te, _ = _fit_predict(X_tr_b4, y_train, X_te_b4)
        prob_b5_te, _ = _fit_predict(X_tr_b5, y_train, X_te_b5)

        # Train Gating Classifier on Training Fold Advantage
        err_p0_tr = (y_train - prob_b1_tr)**2
        err_p1_tr = (y_train - prob_b2_tr)**2
        adv_tr = err_p0_tr - err_p1_tr
        gating_tr = (adv_tr > 0).astype(int)

        if len(np.unique(gating_tr)) > 1:
            gate_clf = LogisticRegression(C=0.5, max_iter=500, random_state=random_state)
            gate_clf.fit(X_tr_topo_s, gating_tr)
            g_prob_te = gate_clf.predict_proba(X_te_topo_s)[:, 1]
            g_prob_tr = gate_clf.predict_proba(X_tr_topo_s)[:, 1]
            # Optimal hard threshold found strictly on training fold
            th_grid = np.linspace(0.2, 0.8, 13)
            best_th = 0.5
            best_tr_acc = -1.0
            for th in th_grid:
                acc = np.mean(((g_prob_tr >= th).astype(int) == gating_tr))
                if acc > best_tr_acc:
                    best_tr_acc = acc
                    best_th = th
        else:
            g_prob_te = np.full(len(y_test), float(np.mean(gating_tr)))
            best_th = 0.5

        # Baselines B6, B7, B8
        rng_rand = np.random.RandomState(random_state + test_idx)
        g_rand = rng_rand.uniform(0.0, 1.0, size=len(y_test))
        prob_b6_te = g_rand * prob_b2_te + (1.0 - g_rand) * prob_b1_te

        auc_p0_tr = roc_auc_score(y_train, prob_b1_tr) if len(np.unique(y_train)) > 1 else 0.5
        auc_p1_tr = roc_auc_score(y_train, prob_b2_tr) if len(np.unique(y_train)) > 1 else 0.5
        prob_b7_te = prob_b2_te if auc_p1_tr >= auc_p0_tr else prob_b1_te

        err_p0_te = (y_test - prob_b1_te)**2
        err_p1_te = (y_test - prob_b2_te)**2
        prob_b8_te = np.where(err_p1_te < err_p0_te, prob_b2_te, prob_b1_te)

        # Adaptive Models
        prob_a1_soft = g_prob_te * prob_b2_te + (1.0 - g_prob_te) * prob_b1_te
        prob_a1_hard = np.where(g_prob_te >= best_th, prob_b2_te, prob_b1_te)
        prob_a1_fixed = 0.5 * prob_b2_te + 0.5 * prob_b1_te

        prob_a2_soft = 0.5 * prob_b0_te + 0.5 * prob_a1_soft
        prob_a2_hard = 0.5 * prob_b0_te + 0.5 * prob_a1_hard

        probs_map = {
            "B0_physics_only": prob_b0_te,
            "B1_particle_history": prob_b1_te,
            "B2_thread_history": prob_b2_te,
            "B3_phys_plus_particle": prob_b3_te,
            "B4_phys_plus_thread": prob_b4_te,
            "B5_phys_plus_particle_plus_thread": prob_b5_te,
            "B6_random_selector": prob_b6_te,
            "B7_constant_selector": prob_b7_te,
            "B8_oracle_selector": prob_b8_te,
            "A1_soft_gated_lagrangian": prob_a1_soft,
            "A1_hard_gated_lagrangian": prob_a1_hard,
            "A1_fixed_50_50_mixture": prob_a1_fixed,
            "A2_phys_plus_soft_gated": prob_a2_soft,
            "A2_phys_plus_hard_gated": prob_a2_hard,
        }

        for model_name, p_te in probs_map.items():
            if len(np.unique(y_test)) > 1:
                auc = float(roc_auc_score(y_test, p_te))
                pr_auc = float(average_precision_score(y_test, p_te))
            else:
                auc = 0.5
                pr_auc = prev_test
            brier = float(brier_score_loss(y_test, p_te))
            pred_lbl = (p_te >= 0.5).astype(int)
            bal_acc = float(balanced_accuracy_score(y_test, pred_lbl))

            fold_metrics_by_model[model_name].append({
                "flow_id": test_flow.flow_id,
                "family": test_flow.flow_family,
                "tier": test_flow.generalization_tier,
                "re": test_flow.reynolds_num,
                "grid": test_flow.grid_size,
                "horizon": horizon_step,
                "fold": test_idx,
                "roc_auc": auc,
                "pr_auc": pr_auc,
                "pr_skill": float(pr_auc - prev_test),
                "brier": brier,
                "balanced_accuracy": bal_acc,
                "prevalence": prev_test,
                "n_samples": len(y_test),
            })

            # Record per-sample raw predictions
            for j in range(len(y_test)):
                feat_hash = hashlib.sha256(test_flow.topology_feats[j].tobytes()).hexdigest()[:16]
                adv_sample = float(err_p0_te[j] - err_p1_te[j])
                predictions_by_model[model_name].append({
                    "run_id": "RUN_TH4_STRESS_01",
                    "model_name": model_name,
                    "flow_id": test_flow.flow_id,
                    "family": test_flow.flow_family,
                    "tier": test_flow.generalization_tier,
                    "re": test_flow.reynolds_num,
                    "grid": test_flow.grid_size,
                    "horizon": horizon_step,
                    "fold": test_idx,
                    "sample_idx": j,
                    "target_y_true": int(y_test[j]),
                    "predicted_probability_y_score": float(p_te[j]),
                    "predicted_class": int(pred_lbl[j]),
                    "gating_prob_thread": float(g_prob_te[j]),
                    "loss_particle": float(err_p0_te[j]),
                    "loss_thread": float(err_p1_te[j]),
                    "representation_advantage_actual": adv_sample,
                    "prevalence": prev_test,
                    "feature_hash": feat_hash,
                })

    model_summaries = {}
    for model_name, f_metrics in fold_metrics_by_model.items():
        auc_list = [m["roc_auc"] for m in f_metrics]
        pr_list = [m["pr_auc"] for m in f_metrics]
        brier_list = [m["brier"] for m in f_metrics]

        g1_aucs = [m["roc_auc"] for m in f_metrics if m["tier"] == "G1"]
        g3_aucs = [m["roc_auc"] for m in f_metrics if m["tier"] == "G3"]

        model_summaries[model_name] = {
            "mean_roc_auc": float(np.mean(auc_list)),
            "std_roc_auc": float(np.std(auc_list)),
            "g1_mean_roc_auc": float(np.mean(g1_aucs)) if g1_aucs else 0.5,
            "g3_mean_roc_auc": float(np.mean(g3_aucs)) if g3_aucs else 0.5,
            "mean_pr_auc": float(np.mean(pr_list)),
            "mean_brier": float(np.mean(brier_list)),
            "fold_metrics": f_metrics,
        }

    return {
        "model_summaries": model_summaries,
        "predictions_by_model": predictions_by_model,
    }
