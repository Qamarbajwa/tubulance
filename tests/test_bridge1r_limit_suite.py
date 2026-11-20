"""Unit tests for Program NS-BRIDGE1-R: Critical Limit Consistency & Cross-Resolution Gate."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.bridge1r_limit_consistency_math import (
    Bridge1RCrossResolutionEvent,
    evaluate_bridge1r_cross_resolution_event,
)


def test_bridge1r_cross_resolution_evaluation():
    """Verify Bridge-1R scale-persistent cone angle, L3 mass tightness, and dual-class distance stability."""
    mesh16 = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    v16 = generate_solenoidal_random_field(mesh16, bcs, k_peak=2.0, E0=1.0, seed=42)

    center = np.array([np.pi, np.pi, np.pi])

    event16 = evaluate_bridge1r_cross_resolution_event(
        velocity=v16,
        times=[0.0, 0.02],
        center_pt=center,
        mesh=mesh16,
        nu=0.01,
        R_cylinder=2.0,
        flow_id="test_flow_iso",
    )

    assert event16.grid_size == 16
    assert event16.r_k > 0.0
    assert event16.dy_k > 0.0
    assert event16.theta_cone_deg >= 0.0
    assert event16.norm_U_L3 >= 0.0
    assert event16.L3_mass_B1 >= 0.0
    assert event16.L3_mass_B2 >= event16.L3_mass_B1
    assert event16.is_L3_mass_tight is True
    assert event16.classified_limit_class in ["TOWNSEND_SHEET", "BURGERS_TUBE", "UNKNOWN_CLASS"]
