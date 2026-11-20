"""Test suite for Milestone TH3: Topology features, adaptive models, and validation."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.fields import VelocityField
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.th3_topology_features import (
    compute_local_velocity_gradient,
    extract_local_topology_features,
    TOPOLOGY_FEATURE_NAMES,
)
from navier3d.experimental.th3_adaptive_models import (
    generate_flow_dataset_th3,
    evaluate_th3_lofo_suite,
)


def test_topology_features_invariance_and_dimensions():
    """Verify topology features shape, non-triviality, and finite values."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    pts = np.array([
        [1.0, 1.0, 1.0],
        [2.0, 2.0, 2.0],
        [3.0, 3.0, 3.0],
    ])

    feats = extract_local_topology_features(pts, vel, mesh)
    assert feats.shape == (3, 14)
    assert len(TOPOLOGY_FEATURE_NAMES) == 14
    assert not np.isnan(feats).any()
    assert not np.isinf(feats).any()

    # Incompressibility / trace constraint: alpha + beta + gamma ~= 0
    alpha = feats[:, 6]
    beta = feats[:, 7]
    gamma = feats[:, 8]
    trace_S = alpha + beta + gamma
    assert np.all(np.abs(trace_S) < 1e-3)


def test_th3_flow_dataset_generation():
    """Verify single flow dataset generation with all topology and representations."""
    ds = generate_flow_dataset_th3(
        flow_id="test_iso",
        flow_family="isotropic",
        reynolds_num=100.0,
        generalization_tier="G1",
        grid_size=16,
        seed=42,
        obs_step=5,
        delta_step=3,
        tau_steps=3,
        n_objects=8,
    )
    assert ds.flow_id == "test_iso"
    assert ds.topology_feats.shape == (8, 14)
    assert ds.p0_hist_int.shape[0] == 8
    assert ds.p1_hist_int.shape[0] == 8
    assert len(ds.targets[0.25]) == 8


def test_th3_adaptive_lofo_execution():
    """Verify complete LOFO evaluation across miniature test flows."""
    ds1 = generate_flow_dataset_th3("f1", "isotropic", 100.0, "G1", 16, 101, obs_step=4, delta_step=2, tau_steps=2, n_objects=8)
    ds2 = generate_flow_dataset_th3("f2", "isotropic", 100.0, "G1", 16, 102, obs_step=4, delta_step=2, tau_steps=2, n_objects=8)
    ds3 = generate_flow_dataset_th3("f3", "taylor_green", 100.0, "G3", 16, 201, obs_step=4, delta_step=2, tau_steps=2, n_objects=8)

    res = evaluate_th3_lofo_suite([ds1, ds2, ds3], target_key=0.25)
    assert "model_summaries" in res
    assert "predictions_by_model" in res
    assert "A1_topology_gated_lagrangian" in res["model_summaries"]
    assert "B0_physics_only" in res["model_summaries"]
    assert "B1_particle_history" in res["model_summaries"]
    assert "B2_thread_history" in res["model_summaries"]
    assert "B8_oracle_selector" in res["model_summaries"]

    # Verify per-sample prediction serialization
    sample_preds = res["predictions_by_model"]["A1_topology_gated_lagrangian"]
    assert len(sample_preds) == 24  # 3 flows * 8 objects
    assert "gating_prob_thread" in sample_preds[0]
    assert 0.0 <= sample_preds[0]["gating_prob_thread"] <= 1.0
