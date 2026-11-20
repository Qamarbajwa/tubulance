"""Target construction, model families (G, P, GP), LOFO framework, and reconciliation metrics for TH1R."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    balanced_accuracy_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import StandardScaler

from ..fields import VelocityField, ScalarField
from ..mesh import StructuredMesh3D
from ..strain import compute_strain_magnitude
from .lagrangian_tracking import interpolate_mac_velocity


def compute_vorticity_magnitude_field(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
) -> ScalarField:
    """Compute cell-centered vorticity magnitude |omega| = |curl(u)|."""
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    u = velocity.u.interior
    v = velocity.v.interior
    w = velocity.w.interior

    u_cc = 0.5 * (u[:-1, :, :] + u[1:, :, :])
    v_cc = 0.5 * (v[:, :-1, :] + v[:, 1:, :])
    w_cc = 0.5 * (w[:, :, :-1] + w[:, :, 1:])

    du_dy = np.gradient(u_cc, dy, axis=1)
    du_dz = np.gradient(u_cc, dz, axis=2)
    dv_dx = np.gradient(v_cc, dx, axis=0)
    dv_dz = np.gradient(v_cc, dz, axis=2)
    dw_dx = np.gradient(w_cc, dx, axis=0)
    dw_dy = np.gradient(w_cc, dy, axis=1)

    wx = dw_dy - dv_dz
    wy = du_dz - dw_dx
    wz = dv_dx - du_dy

    omega_mag = np.sqrt(wx**2 + wy**2 + wz**2)
    res = ScalarField.zeros(mesh)
    res.interior[:] = omega_mag
    return res


def extract_future_target_labels(
    positions: np.ndarray,
    vorticity_field_future: ScalarField,
    mesh: StructuredMesh3D,
    top_percentile: float = 0.25,
) -> Tuple[np.ndarray, float]:
    """Construct binary target: does future centroid position occupy top X% vorticity?"""
    vort_interior = vorticity_field_future.interior
    thresh_val = float(np.quantile(vort_interior, 1.0 - top_percentile))

    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz

    px = np.clip(positions[:, 0] % lx, 0.0, lx - 1e-6)
    py = np.clip(positions[:, 1] % ly, 0.0, ly - 1e-6)
    pz = np.clip(positions[:, 2] % lz, 0.0, lz - 1e-6)

    ix = np.clip((px / dx).astype(int), 0, nx - 1)
    iy = np.clip((py / dy).astype(int), 0, ny - 1)
    iz = np.clip((pz / dz).astype(int), 0, nz - 1)

    sampled_vort = vort_interior[ix, iy, iz]
    targets = (sampled_vort >= thresh_val).astype(int)
    return targets, thresh_val


def extract_adversarial_targets(
    positions_obs: np.ndarray,
    positions_future: np.ndarray,
    vort_obs: ScalarField,
    vort_future: ScalarField,
    vel_future: VelocityField,
    mesh: StructuredMesh3D,
) -> Dict[str, np.ndarray]:
    """Extract alternative adversarial future targets."""
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz

    def _sample(field_data: np.ndarray, pos: np.ndarray) -> np.ndarray:
        px = np.clip(pos[:, 0] % lx, 0.0, lx - 1e-6)
        py = np.clip(pos[:, 1] % ly, 0.0, ly - 1e-6)
        pz = np.clip(pos[:, 2] % lz, 0.0, lz - 1e-6)
        ix = np.clip((px / dx).astype(int), 0, nx - 1)
        iy = np.clip((py / dy).astype(int), 0, ny - 1)
        iz = np.clip((pz / dz).astype(int), 0, nz - 1)
        return field_data[ix, iy, iz]

    w_obs = _sample(vort_obs.interior, positions_obs)
    w_fut = _sample(vort_future.interior, positions_future)

    target_enstrophy_growth = (w_fut > w_obs).astype(int)

    strain_mag_field = compute_strain_magnitude(vel_future, mesh)
    s_fut = _sample(strain_mag_field.interior, positions_future)
    s_thresh = np.quantile(strain_mag_field.interior, 0.75)
    target_high_strain = (s_fut >= s_thresh).astype(int)

    return {
        "enstrophy_growth": target_enstrophy_growth,
        "high_strain": target_high_strain,
    }


def extract_eulerian_physics_features(
    positions_obs: np.ndarray,
    velocity_obs: VelocityField,
    vorticity_obs: ScalarField,
    mesh: StructuredMesh3D,
) -> np.ndarray:
    """Extract explicit local Eulerian physics variables (Model Family P)."""
    u_interp = interpolate_mac_velocity(positions_obs, velocity_obs, mesh)
    speed = np.linalg.norm(u_interp, axis=1)

    strain_field = compute_strain_magnitude(velocity_obs, mesh)

    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz

    px = np.clip(positions_obs[:, 0] % lx, 0.0, lx - 1e-6)
    py = np.clip(positions_obs[:, 1] % ly, 0.0, ly - 1e-6)
    pz = np.clip(positions_obs[:, 2] % lz, 0.0, lz - 1e-6)
    ix = np.clip((px / dx).astype(int), 0, nx - 1)
    iy = np.clip((py / dy).astype(int), 0, ny - 1)
    iz = np.clip((pz / dz).astype(int), 0, nz - 1)

    w_local = vorticity_obs.interior[ix, iy, iz]
    s_local = strain_field.interior[ix, iy, iz]

    p_feats = np.column_stack([
        u_interp[:, 0], u_interp[:, 1], u_interp[:, 2],
        speed,
        w_local,
        s_local,
    ])
    return p_feats


@dataclass
class FlowDataset:
    """Container holding features and targets for one independent physical flow simulation."""
    flow_id: str
    flow_family: str
    reynolds_num: float
    grid_size: int
    generalization_tier: str  # G1, G2, or G3
    # Intrinsic geometry representations (centroid removed)
    p0_inst_int: np.ndarray
    p0_hist_int: np.ndarray
    p0_shuff_int: np.ndarray
    p1_inst_int: np.ndarray
    p1_hist_int: np.ndarray
    p1_shuff_int: np.ndarray
    p2_inst_int: np.ndarray
    p2_hist_int: np.ndarray
    p2_shuff_int: np.ndarray
    # Absolute geometry representations (with centroid)
    p0_hist_abs: np.ndarray
    p1_hist_abs: np.ndarray
    p2_hist_abs: np.ndarray
    # Physics & position
    positions_obs: np.ndarray
    physics_feats: np.ndarray
    targets: Dict[float, np.ndarray]
    adversarial_targets: Dict[str, np.ndarray]


def evaluate_lofo_classifier(
    datasets: List[FlowDataset],
    feature_extractor_fn: Any,
    target_key: float = 0.25,
    model_type: str = "logistic",
    adversarial_target: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute Leave-One-Flow-Out (LOFO) evaluation with strict training-only preprocessing."""
    n_flows = len(datasets)
    flow_metrics = []

    all_y_true = []
    all_y_prob = []

    for test_idx in range(n_flows):
        test_flow = datasets[test_idx]
        train_flows = [datasets[i] for i in range(n_flows) if i != test_idx]

        # 1. Assemble training data from training flows ONLY
        X_train_list = []
        y_train_list = []
        for flow in train_flows:
            X_f = feature_extractor_fn(flow)
            y_f = flow.adversarial_targets[adversarial_target] if adversarial_target else flow.targets[target_key]
            X_train_list.append(X_f)
            y_train_list.append(y_f)

        X_train = np.vstack(X_train_list)
        y_train = np.concatenate(y_train_list)

        X_test = feature_extractor_fn(test_flow)
        y_test = test_flow.adversarial_targets[adversarial_target] if adversarial_target else test_flow.targets[target_key]

        # 2. Preprocessing fit ONLY on training data
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 3. Model training
        if len(np.unique(y_train)) < 2:
            prob_test = np.full(len(y_test), float(np.mean(y_train)))
        else:
            clf = LogisticRegression(C=1.0, max_iter=500, random_state=42)
            clf.fit(X_train_scaled, y_train)
            prob_test = clf.predict_proba(X_test_scaled)[:, 1]

        # 4. Out-of-fold evaluation on test flow
        prevalence = float(np.mean(y_test))
        if len(np.unique(y_test)) > 1:
            auc = float(roc_auc_score(y_test, prob_test))
            pr_auc = float(average_precision_score(y_test, prob_test))
        else:
            auc = 0.5
            pr_auc = prevalence

        delta_pr = float(pr_auc - prevalence)
        pred_labels = (prob_test >= 0.5).astype(int)
        brier = float(brier_score_loss(y_test, prob_test))
        bal_acc = float(balanced_accuracy_score(y_test, pred_labels))
        prec = float(precision_score(y_test, pred_labels, zero_division=0))
        rec = float(recall_score(y_test, pred_labels, zero_division=0))

        flow_metrics.append({
            "flow_id": test_flow.flow_id,
            "flow_family": test_flow.flow_family,
            "generalization_tier": test_flow.generalization_tier,
            "roc_auc": auc,
            "pr_auc": pr_auc,
            "delta_pr": delta_pr,
            "brier": brier,
            "balanced_accuracy": bal_acc,
            "precision": prec,
            "recall": rec,
            "prevalence": prevalence,
            "n_samples": len(y_test),
        })

        all_y_true.extend(y_test.tolist())
        all_y_prob.extend(prob_test.tolist())

    all_y_true = np.array(all_y_true)
    all_y_prob = np.array(all_y_prob)

    overall_auc = float(roc_auc_score(all_y_true, all_y_prob)) if len(np.unique(all_y_true)) > 1 else 0.5
    overall_pr_auc = float(average_precision_score(all_y_true, all_y_prob)) if len(np.unique(all_y_true)) > 1 else 0.0
    overall_brier = float(brier_score_loss(all_y_true, all_y_prob))

    auc_vals = [m["roc_auc"] for m in flow_metrics]
    mean_auc = float(np.mean(auc_vals))
    std_auc = float(np.std(auc_vals))

    # Sample-level raw prediction records
    raw_predictions = []
    for test_idx in range(n_flows):
        test_flow = datasets[test_idx]
        train_flows = [datasets[i] for i in range(n_flows) if i != test_idx]
        X_train_list = [feature_extractor_fn(flow) for flow in train_flows]
        y_train_list = [flow.adversarial_targets[adversarial_target] if adversarial_target else flow.targets[target_key] for flow in train_flows]
        X_train = np.vstack(X_train_list)
        y_train = np.concatenate(y_train_list)
        X_test = feature_extractor_fn(test_flow)
        y_test = test_flow.adversarial_targets[adversarial_target] if adversarial_target else test_flow.targets[target_key]
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if len(np.unique(y_train)) < 2:
            prob_test = np.full(len(y_test), float(np.mean(y_train)))
        else:
            clf = LogisticRegression(C=1.0, max_iter=500, random_state=42)
            clf.fit(X_train_scaled, y_train)
            prob_test = clf.predict_proba(X_test_scaled)[:, 1]
            
        prevalence = float(np.mean(y_test))
        pred_labels = (prob_test >= 0.5).astype(int)
        
        import hashlib
        for j in range(len(y_test)):
            feat_bytes = np.ascontiguousarray(X_test[j]).tobytes()
            feat_hash = hashlib.sha256(feat_bytes).hexdigest()[:16]
            raw_predictions.append({
                "flow_id": test_flow.flow_id,
                "flow_family": test_flow.flow_family,
                "generalization_tier": test_flow.generalization_tier,
                "fold": test_idx,
                "sample_idx": j,
                "target_y_true": int(y_test[j]),
                "predicted_probability_y_score": float(prob_test[j]),
                "predicted_class": int(pred_labels[j]),
                "prevalence": prevalence,
                "feature_hash": feat_hash,
            })

    return {
        "mean_auc": mean_auc,
        "std_auc": std_auc,
        "overall_auc": overall_auc,
        "overall_pr_auc": overall_pr_auc,
        "overall_brier": overall_brier,
        "flow_metrics": flow_metrics,
        "dimension": X_train.shape[1],
        "raw_predictions": raw_predictions,
    }


def compute_nested_physics_residual_test(
    datasets: List[FlowDataset],
    target_key: float = 0.25,
) -> Dict[str, Any]:
    """Strict nested evaluation of Physics P vs Geometry G vs Combined P+G."""
    res_p = evaluate_lofo_classifier(datasets, lambda d: d.physics_feats, target_key=target_key)
    res_g = evaluate_lofo_classifier(datasets, lambda d: d.p1_hist_int, target_key=target_key)
    res_pg = evaluate_lofo_classifier(
        datasets, lambda d: np.hstack([d.physics_feats, d.p1_hist_int]), target_key=target_key
    )

    delta_auc = float(res_pg["mean_auc"] - res_p["mean_auc"])
    delta_brier = float(res_pg["overall_brier"] - res_p["overall_brier"])

    return {
        "physics_auc": res_p["mean_auc"],
        "geometry_auc": res_g["mean_auc"],
        "combined_auc": res_pg["mean_auc"],
        "delta_auc_pg_over_p": delta_auc,
        "delta_brier_pg_over_p": delta_brier,
        "has_residual_information": bool(delta_auc > 0.01 and delta_brier < -0.005),
    }
