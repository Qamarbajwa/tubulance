"""Unit tests for Branch NS-BLOWUP-1: Parabolic Rescaling of Extreme Events."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.ns_blowup1_rescaling_math import compute_parabolic_rescaled_profile


def test_ns_blowup1_parabolic_rescaling():
    """Verify parabolic rescaling normalizes peak vorticity and fits canonical limiting profiles."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    center = np.array([np.pi, np.pi, np.pi])
    prof = compute_parabolic_rescaled_profile(center, vel, mesh, nu=0.01)

    assert prof.q_max_raw > 0.0
    assert prof.rescaling_lambda > 0.0
    assert len(prof.rescaled_radii) == len(prof.normalized_q_profile)
    assert np.isclose(prof.normalized_q_profile[0], 1.0, atol=1e-6)
    assert prof.best_fit_geometry in ["BURGERS_SHEET", "BURGERS_TUBE", "ASYMMETRIC"]
    assert prof.burgers_sheet_l2_error >= 0.0
