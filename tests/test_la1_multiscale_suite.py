"""Unit tests for Side Branch LA1: Multiscale Localized vs Global Averaging."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.la1_multiscale_math import compute_multiscale_averages_at_center


def test_multiscale_profile_computation():
    """Verify that multiscale profile computation returns valid arrays and finite values."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    center = np.array([np.pi, np.pi, np.pi])
    prof = compute_multiscale_averages_at_center(
        center_pt=center,
        center_type="control",
        velocity=vel,
        mesh=mesh,
        kernel="spherical",
        nu=0.01,
    )

    assert len(prof.radii) > 0
    assert len(prof.q_profile) == len(prof.radii)
    assert np.all(np.isfinite(prof.q_profile))
    assert np.all(np.isfinite(prof.rho_RA_profile))
    assert prof.q_global > 0
    assert prof.structure_type in ["tube", "sheet", "mixed"]


def test_gaussian_kernel_robustness():
    """Verify that Gaussian kernel produces valid profiles."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    center = np.array([np.pi, np.pi, np.pi])
    prof_g = compute_multiscale_averages_at_center(
        center_pt=center,
        center_type="control",
        velocity=vel,
        mesh=mesh,
        kernel="gaussian",
        nu=0.01,
    )

    assert np.all(np.isfinite(prof_g.q_profile))
    assert np.all(np.isfinite(prof_g.rho_RA_profile))
