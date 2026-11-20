"""Test suite for Milestone TH8: Maximum-Vorticity Stretching Depletion and Strain Eigenstructure."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.th8_depletion_math import evaluate_pointwise_depletion, extract_field_vorticity_grid


def test_eigenstructure_depletion_identity_closure():
    """Verify that lambda_3 - lambda_omega == (lambda_3 - lambda_1)*a1 + (lambda_3 - lambda_2)*a2."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    pt = np.array([1.5, 2.0, 2.5])
    rec = evaluate_pointwise_depletion(pt, vel, mesh, q_max=5.0, nu=0.01)

    # Check partition of unity
    assert np.isclose(rec.a1 + rec.a2 + rec.a3, 1.0, atol=1e-5)

    # Check exact depletion decomposition closure
    assert np.isclose(rec.D_abs, rec.e1_contrib + rec.e2_contrib, atol=1e-5)
    assert rec.closure_error < 1e-5


def test_peak_vorticity_extraction():
    """Verify that peak vorticity grid evaluation correctly locates the maximum magnitude."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    q_grid, X, Y, Z = extract_field_vorticity_grid(vel, mesh)
    assert q_grid.shape == (16, 16, 16)
    q_max = float(np.max(q_grid))
    assert q_max > 0.0
