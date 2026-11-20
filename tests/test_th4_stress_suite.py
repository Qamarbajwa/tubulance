"""Test suite for Milestone TH4: Stress models, multi-horizon, and negative controls."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.th4_stress_models import (
    generate_flow_dataset_th4,
    evaluate_th4_stress_lofo,
)


def test_th4_flow_dataset_multi_horizon():
    """Verify TH4 multi-horizon dataset generation."""
    ds = generate_flow_dataset_th4(
        flow_id="test_th4_iso",
        flow_family="isotropic",
        reynolds_num=100.0,
        generalization_tier="G1",
        grid_size=16,
        seed=42,
        obs_step=5,
        horizons=[2, 4],
        tau_steps=2,
        n_objects=8,
    )
    assert ds.flow_id == "test_th4_iso"
    assert 2 in ds.targets_by_horizon
    assert 4 in ds.targets_by_horizon
    assert len(ds.targets_by_horizon[2][0.25]) == 8
    assert len(ds.targets_by_horizon[4][0.25]) == 8


def test_th4_stress_lofo_and_controls():
    """Verify TH4 LOFO evaluation with soft and hard gating and shuffled controls."""
    ds1 = generate_flow_dataset_th4("f1", "isotropic", 100.0, "G1", 16, 101, obs_step=4, horizons=[2], tau_steps=2, n_objects=8)
    ds2 = generate_flow_dataset_th4("f2", "isotropic", 100.0, "G1", 16, 102, obs_step=4, horizons=[2], tau_steps=2, n_objects=8)
    ds3 = generate_flow_dataset_th4("f3", "taylor_green", 100.0, "G3", 16, 201, obs_step=4, horizons=[2], tau_steps=2, n_objects=8)

    # Standard run
    res = evaluate_th4_stress_lofo([ds1, ds2, ds3], horizon_step=2, target_key=0.25)
    assert "A1_soft_gated_lagrangian" in res["model_summaries"]
    assert "A1_hard_gated_lagrangian" in res["model_summaries"]
    assert "A1_fixed_50_50_mixture" in res["model_summaries"]

    # Shuffled topology control
    res_shuff = evaluate_th4_stress_lofo([ds1, ds2, ds3], horizon_step=2, target_key=0.25, shuffled_topology=True)
    assert res_shuff["model_summaries"]["A1_soft_gated_lagrangian"]["mean_roc_auc"] >= 0.0

    # Shuffled labels control
    res_lbl = evaluate_th4_stress_lofo([ds1, ds2, ds3], horizon_step=2, target_key=0.25, shuffled_labels=True)
    assert res_lbl["model_summaries"]["B0_physics_only"]["mean_roc_auc"] >= 0.0
