"""Adaptive Lagrangian Models, Gating Selectors, and Validation Suite for Milestone TH3.

Provides:
- FlowDatasetTH3: Flow realization container with topology features and representations.
- Gating / Selector models trained strictly inside training folds.
- Baseline models: B0 to B8.
- Adaptive models: A1 (topology-gated particle/thread) and A2 (physics + gated Lagrangian).
- Strict Leave-One-Flow-Out (LOFO) and Leave-One-Flow-Family-Out (LOFFO) engines.
- Comprehensive serialization of raw out-of-fold sample predictions.
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
from .th3_topology_features import extract_local_topology_features


@dataclass
class FlowDatasetTH3:
    """Full dataset container for a single independent physical flow in TH3."""
    flow_id: str
    flow_family: str
    reynolds_num: float
    generalization_tier: str
    grid_size: int
    seed: int

    # Observed centroids at t_obs
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

    # Target labels at future horizon t_obs + delta_t
    targets: Dict[float, np.ndarray] # target_percentile -> binary labels (N,)


def generate_flow_dataset_th3(
    flow_id: str,
    flow_family: str,
    reynolds_num: float = 100.0,
    generalization_tier: str = "G1",
    grid_size: int = 16,
    seed: int = 42,
    obs_step: int = 15,
    delta_step: int = 10,
    tau_steps: int = 10,
    n_objects: int = 64,
) -> FlowDatasetTH3:
    """Simulate a physical flow, advect Lagrangian objects, extract topology and features."""
    nu = 1.0 / reynolds_num
    total_steps = obs_step + delta_step + 5

    # 1. Simulate trajectory
    mesh, vel_snaps, times = generate_flow_simulation_trajectory(
        flow_family=flow_family,
        grid_size=grid_size,
        nu=nu,
        seed=seed,
        total_steps=total_steps,
        dt=0.02,
    )

    # 2. Extract base Lagrangian and Physics dataset
    base_ds = generate_flow_dataset(
        flow_id=flow_id,
        flow_family=flow_family,
        reynolds_num=reynolds_num,
        generalization_tier=generalization_tier,
        grid_size=grid_size,
        seed=seed,
        obs_step=obs_step,
        delta_step=delta_step,
        tau_steps=tau_steps,
        n_objects=n_objects,
    )

    # 3. Extract local topology features at observation step
    vel_at_obs = vel_snaps[obs_step]
    topo_feats = extract_local_topology_features(base_ds.positions_obs, vel_at_obs, mesh)

    return FlowDatasetTH3(
        flow_id=flow_id,
        flow_family=flow_family,
        reynolds_num=reynolds_num,
        generalization_tier=generalization_tier,
        grid_size=grid_size,
        seed=seed,
        centroids_obs=base_ds.positions_obs,
        p0_hist_int=base_ds.p0_hist_int,
        p0_shuff_int=base_ds.p0_shuff_int,
        p1_hist_int=base_ds.p1_hist_int,
        p1_shuff_int=base_ds.p1_shuff_int,
        p2_hist_int=base_ds.p2_hist_int,
        physics_feats=base_ds.physics_feats,
        topology_feats=topo_feats,
        targets=base_ds.targets,
    )


def evaluate_th3_lofo_suite(
    datasets: List[FlowDatasetTH3],
    target_key: float = 0.25,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Execute complete LOFO evaluation of all baselines B0-B8 and adaptive models A1, A2."""
    n_flows = len(datasets)
    reps_keys = [
        "B0_physics_only",
        "B1_particle_history",
        "B2_thread_history",
        "B3_phys_plus_particle",
        "B4_phys_plus_thread",
        "B5_phys_plus_particle_plus_thread",
        "B6_random_selector",
        "B7_constant_selector",
        "B8_oracle_selector",
        "A1_topology_gated_lagrangian",
        "A2_phys_plus_gated_lagrangian",
    ]

    predictions_by_model: Dict[str, List[Dict[str, Any]]] = {k: [] for k in reps_keys}
    fold_metrics_by_model: Dict[str, List[Dict[str, Any]]] = {k: [] for k in reps_keys}

    for test_idx in range(n_flows):
        test_flow = datasets[test_idx]
        train_flows = [datasets[i] for i in range(n_flows) if i != test_idx]

        # Assemble training data
        y_train = np.concatenate([f.targets[target_key] for f in train_flows])
        y_test = test_flow.targets[target_key]
        prev_test = float(np.mean(y_test))

        # Base feature matrices
        X_tr_phys = np.vstack([f.physics_feats for f in train_flows])
        X_te_phys = test_flow.physics_feats

        X_tr_p0 = np.vstack([f.p0_hist_int for f in train_flows])
        X_te_p0 = test_flow.p0_hist_int

        X_tr_p1 = np.vstack([f.p1_hist_int for f in train_flows])
        X_te_p1 = test_flow.p1_hist_int

        X_tr_topo = np.vstack([f.topology_feats for f in train_flows])
        X_te_topo = test_flow.topology_feats

        # Preprocessing (fit exclusively on training data)
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

        # Build Gating / Selector Model on Training Folds ONLY
        err_p0_tr = (y_train - prob_b1_tr)**2
        err_p1_tr = (y_train - prob_b2_tr)**2
        adv_tr = err_p0_tr - err_p1_tr  # > 0 means thread had smaller error
        gating_target_tr = (adv_tr > 0).astype(int)

        if len(np.unique(gating_target_tr)) > 1:
            gate_clf = LogisticRegression(C=0.5, max_iter=500, random_state=random_state)
            gate_clf.fit(X_tr_topo_s, gating_target_tr)
            g_prob_te = gate_clf.predict_proba(X_te_topo_s)[:, 1]
        else:
            g_prob_te = np.full(len(y_test), float(np.mean(gating_target_tr)))

        # Baselines B6, B7, B8
        rng = np.random.RandomState(random_state + test_idx)
        g_rand = rng.uniform(0.0, 1.0, size=len(y_test))
        prob_b6_te = g_rand * prob_b2_te + (1.0 - g_rand) * prob_b1_te

        auc_p0_tr = roc_auc_score(y_train, prob_b1_tr) if len(np.unique(y_train)) > 1 else 0.5
        auc_p1_tr = roc_auc_score(y_train, prob_b2_tr) if len(np.unique(y_train)) > 1 else 0.5
        prob_b7_te = prob_b2_te if auc_p1_tr >= auc_p0_tr else prob_b1_te

        err_p0_te = (y_test - prob_b1_te)**2
        err_p1_te = (y_test - prob_b2_te)**2
        prob_b8_te = np.where(err_p1_te < err_p0_te, prob_b2_te, prob_b1_te)

        # Adaptive Model A1: Topology-gated Lagrangian representation
        prob_a1_te = g_prob_te * prob_b2_te + (1.0 - g_prob_te) * prob_b1_te

        # Adaptive Model A2: Eulerian Physics + Topology-gated Lagrangian representation
        prob_a2_te = 0.5 * prob_b0_te + 0.5 * prob_a1_te

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
            "A1_topology_gated_lagrangian": prob_a1_te,
            "A2_phys_plus_gated_lagrangian": prob_a2_te,
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
                    "run_id": "RUN_TH3_AUTONOMOUS_01",
                    "model_name": model_name,
                    "flow_id": test_flow.flow_id,
                    "family": test_flow.flow_family,
                    "tier": test_flow.generalization_tier,
                    "fold": test_idx,
                    "sample_idx": j,
                    "target_y_true": int(y_test[j]),
                    "predicted_probability_y_score": float(p_te[j]),
                    "predicted_class": int(pred_lbl[j]),
                    "gating_prob_thread": float(g_prob_te[j]),
                    "representation_advantage_actual": adv_sample,
                    "prevalence": prev_test,
                    "feature_hash": feat_hash,
                })

    # Summary Statistics across folds
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
