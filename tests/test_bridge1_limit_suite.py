"""Unit tests for Program NS-BRIDGE1: Blow-Up Rescaling, Limit-Class Identification, and Rigidity Eligibility."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.bridge1_limit_rigidity_math import (
    Bridge1RescaledEvent,
    evaluate_bridge1_rescaled_event,
)


def test_bridge1_rescaled_event_evaluation():
    """Verify Bridge-1 parabolic dilation, scale-invariant quantities, model distances, and cone containment."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    v0 = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)
    v1 = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=43)

    history = [v0, v1]
    times = [0.0, 0.02]
    center = np.array([np.pi, np.pi, np.pi])

    event = evaluate_bridge1_rescaled_event(
        velocity_history=history,
        times=times,
        snap_idx=1,
        center_pt=center,
        mesh=mesh,
        nu=0.01,
        R_cylinder=2.0,
        sequence_type="GLOBAL_QMAX",
        flow_id="flow_test",
    )

    assert event.r_k > 0.0
    assert event.is_nontrivial is True
    assert event.A_R >= 0.0
    assert event.norm_U_L3_critical >= 0.0
    assert event.d_Townsend >= 0.0
    assert event.d_Burgers >= 0.0
    assert event.classified_limit_class in ["TOWNSEND_SHEET", "BURGERS_TUBE", "UNKNOWN_CLASS"]
    assert 0.0 <= event.f_strain_self_generated <= 1.0
    assert event.theta_cone_deg >= 0.0
