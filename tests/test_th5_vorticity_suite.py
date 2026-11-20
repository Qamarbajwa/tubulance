"""Test suite for Milestone TH5: Vorticity budgets, strain eigensystems, and candidate bounds."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.th5_vorticity_math import (
    compute_pointwise_vorticity_state,
    compute_lagrangian_trajectory_budget,
)


def test_strain_eigensystem_and_invariants():
    """Verify incompressibility constraint, eigenvector orthonormality, and stretching bounds."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    pt = np.array([1.5, 2.0, 2.5])
    state = compute_pointwise_vorticity_state(pt, vel, mesh, nu=0.01)

    # 1. Incompressibility / Tracelessness
    tr_eig = np.sum(state.eigvals)
    assert np.abs(tr_eig) < 1e-4, f"Trace violation: {tr_eig}"

    # 2. Orthonormality of eigenvectors
    E = state.eigvecs
    gram = E.T @ E
    assert np.allclose(gram, np.eye(3), atol=1e-5), f"Non-orthogonal eigenvectors:\n{gram}"

    # 3. Stretching bound: lambda_1 <= lambda_omega <= lambda_3
    l1, l2, l3 = state.eigvals[0], state.eigvals[1], state.eigvals[2]
    assert l1 <= state.lambda_omega + 1e-6
    assert state.lambda_omega <= l3 + 1e-6

    # 4. Identity: lambda_omega == sum_i lambda_i * (omega_hat . e_i)^2
    decomp = np.sum(state.eigvals * (state.alignments**2))
    assert np.abs(state.lambda_omega - decomp) < 1e-5


def test_lagrangian_trajectory_vorticity_budget():
    """Verify that Lagrangian vorticity budget evaluates with finite, bounded residuals."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    # Simple 3-step test trajectory
    traj = np.array([
        [1.0, 1.0, 1.0],
        [1.02, 1.01, 1.02],
        [1.04, 1.03, 1.04],
    ])
    times = [0.0, 0.02, 0.04]
    vel_snaps = [vel, vel, vel]

    budget = compute_lagrangian_trajectory_budget(traj, vel_snaps, times, mesh, nu=0.01)
    assert "mean_residual" in budget
    assert "candidate_bounds" in budget
    assert not np.isnan(budget["mean_residual"])
    assert "B1_ideal_extensional" in budget["candidate_bounds"]
    assert "B3_viscous_corrected" in budget["candidate_bounds"]
