"""Unit tests for Program NS-THEOREM-GATE-1: Regularity-Criterion Applicability & Gap Audit."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.theorem_gate1_audit_math import (
    FixedConeAuditResult,
    L3TailTightnessResult,
    compute_optimal_fixed_cone_axis,
    audit_lei_ren_tian_fixed_cone,
    audit_l3_tail_tightness,
)


def test_theorem_gate1_fixed_cone_and_tail_audit():
    """Verify Lei-Ren-Tian fixed-cone audit and L^3 spatial tail tightness calculations."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    v0 = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    center = np.array([np.pi, np.pi, np.pi])

    cone_res = audit_lei_ren_tian_fixed_cone(
        velocity=v0,
        mesh=mesh,
        center_pt=center,
        nu=0.01,
        R_cylinder=2.0,
        threshold_tau=0.75,
        flow_id="test_flow_iso",
    )

    assert cone_res.grid_size == 16
    assert cone_res.num_high_vorticity_pts >= 1
    assert 0.0 <= cone_res.theta_max_deg <= 180.0
    assert 0.0 <= cone_res.mean_theta_deg <= cone_res.theta_max_deg
    assert np.isclose(np.linalg.norm(cone_res.optimal_axis), 1.0)

    tail_res = audit_l3_tail_tightness(
        velocity=v0,
        mesh=mesh,
        center_pt=center,
        nu=0.01,
        R_core=1.5,
        flow_id="test_flow_iso",
    )

    assert tail_res.grid_size == 16
    assert tail_res.L3_mass_inner >= 0.0
    assert tail_res.L3_mass_shell >= 0.0
    assert tail_res.tail_fraction >= 0.0
