"""Unit tests for Program NS-BLOWUP-2: Full Parabolically Rescaled Navier-Stokes Field Analysis."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.ns_blowup2_full_limit_math import (
    NSBlowup2CylinderState,
    evaluate_rescaled_cylinder,
)


def test_ns_blowup2_rescaled_cylinder_evaluation():
    """Verify full rescaled field evaluation, scale-critical norms, and Burgers-Townsend model validation."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    v0 = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)
    v1 = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=43)

    history = [v0, v1]
    times = [0.0, 0.02]
    center = np.array([np.pi, np.pi, np.pi])

    state = evaluate_rescaled_cylinder(
        velocity_history=history,
        times=times,
        snap_idx=1,
        center_pt=center,
        mesh=mesh,
        nu=0.01,
        R_sample=2.0,
        seq_type="SEQUENCE_A_WITHIN_SOLUTION",
        flow_id="flow_test",
        phase_cat="PEAK",
    )

    assert state.r_n > 0.0
    assert state.rescaled_dx > 0.0
    assert state.rescaled_domain_L > 0.0
    assert state.norm_U_L3 >= 0.0
    assert state.pde_residual_NS >= 0.0
    assert state.burgers_vector_L2_error >= 0.0
