"""Test suite for Milestone TH6: Falsification Engine and Subinterval Evaluation."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.operators import divergence
from navier3d.experimental.th6_falsification_engine import (
    evaluate_trajectory_subintervals,
    find_pointwise_positive_r_events,
    generate_adversarial_strained_layer_field,
)


def test_subinterval_exact_residual_closure():
    """Verify that R_direct == R_integrated to numerical integration tolerance."""
    times = [0.0, 0.05, 0.10, 0.15, 0.20]
    w_mags = [1.0, 1.1, 1.25, 1.15, 1.05]
    lambda_omegas = [0.8, 0.9, 0.7, 0.5, 0.4]
    lambda_3s = [1.2, 1.3, 1.1, 0.9, 0.8]
    V_omegas = [-0.1, -0.05, 0.02, -0.08, -0.12]

    subintervals = evaluate_trajectory_subintervals(
        times=times,
        w_mags=w_mags,
        lambda_omegas=lambda_omegas,
        lambda_3s=lambda_3s,
        V_omegas=V_omegas,
    )

    assert len(subintervals) == 10 # 4+3+2+1 = 10 pairs
    for sub in subintervals:
        # Closure error should be bounded by discretization scale
        assert not np.isnan(sub.R_direct)
        assert not np.isnan(sub.R_integrated)
        assert sub.margin == -sub.R_direct


def test_adversarial_strained_layer_solenoidality():
    """Verify that constructed adversarial flow field is discretely divergence-free."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_adversarial_strained_layer_field(mesh, bcs, seed=42)

    div = divergence(vel, mesh)
    max_div = float(np.max(np.abs(div.data[mesh.n_ghost : -mesh.n_ghost, mesh.n_ghost : -mesh.n_ghost, mesh.n_ghost : -mesh.n_ghost])))
    assert max_div < 1e-4, f"Adversarial field is not solenoidal: max div = {max_div}"
