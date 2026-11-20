"""Unit tests for Program LA1-R: Physical-Scale Localization and Enstrophy Weighting."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.la1r_physical_scale_math import evaluate_la1r_physical_profile


def test_la1r_physical_profile():
    """Verify that enstrophy-weighted profiles and physical thickness evaluate correctly."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    center = np.array([np.pi, np.pi, np.pi])
    prof = evaluate_la1r_physical_profile(center, vel, mesh, nu=0.01)

    assert len(prof.radii_phys) > 0
    assert len(prof.D_weighted_profile) == len(prof.radii_phys)
    assert np.all(np.isfinite(prof.D_weighted_profile))
    assert np.all(np.isfinite(prof.P_stretch_profile))
    assert prof.sheet_thickness_phys >= 0.0
