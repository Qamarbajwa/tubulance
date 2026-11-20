"""Test suite for Milestone TH7: Magnitude-Direction Decomposition and Viscous Influx Mathematics."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.th7_viscous_influx_math import compute_pointwise_viscous_decomposition


def test_magnitude_direction_exact_decomposition_closure():
    """Verify that xi . Delta(omega) == Delta(q) - q * ||grad(xi)||_F^2 to finite difference tolerance."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    pt = np.array([1.5, 2.0, 2.5])
    decomp = compute_pointwise_viscous_decomposition(pt, vel, mesh, nu=0.01)

    # Check that decomposition identity residual is small (bounded by O(eps^2) stencil error)
    rel_decomp_error = decomp.decomp_residual / (abs(decomp.xi_dot_lap_omega) + 1.0)
    assert rel_decomp_error < 0.15, f"Decomposition identity failed: rel error = {rel_decomp_error}"

    # Check non-negativity of direction penalty
    assert decomp.dir_decoherence_penalty >= 0.0

    # Check that V_log == mag_curvature_term + dir_penalty_term
    expected_V_log = decomp.mag_curvature_term + decomp.dir_penalty_term
    assert np.isclose(decomp.V_log, expected_V_log, atol=1e-4)


def test_peak_dissipation_maximum_principle():
    """Verify that when magnitude Laplacian is negative (Delta(q) <= 0), V_log is strictly non-positive."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    # Check across multiple grid points
    points = [np.array([x, y, z]) for x in [1.0, 2.0, 3.0] for y in [1.0, 2.0] for z in [1.5, 2.5]]
    for pt in points:
        decomp = compute_pointwise_viscous_decomposition(pt, vel, mesh, nu=0.01)
        if decomp.lap_q <= 0:
            assert decomp.V_log <= 1e-4, f"Maximum principle violation: lap_q = {decomp.lap_q}, V_log = {decomp.V_log}"
