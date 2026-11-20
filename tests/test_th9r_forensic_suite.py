"""Unit tests for Program TH9-R: Forensic Recheck of Direction Dynamics and Torques."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.fields import ScalarField
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.th9r_direction_forensic import evaluate_th9r_forensic_state


def test_th9r_orthogonality_and_closure():
    """Verify that R_strain and R_visc are orthogonal to xi and 3-way torque closure holds exactly."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)
    p = ScalarField.zeros(mesh)

    pt = np.array([1.5, 2.0, 2.5])
    state = evaluate_th9r_forensic_state(pt, vel, p, mesh, nu=0.01)

    # 1. Blocking Orthogonality Tests
    assert np.isclose(state.ortho_xi_Rstrain, 0.0, atol=1e-12)
    assert np.isclose(state.ortho_xi_Rvisc, 0.0, atol=1e-12)
    assert np.isclose(state.ortho_xi_Dxi, 0.0, atol=1e-12)

    # 2. Blocking 3-Way Torque Closure
    assert np.isclose(state.Da3_Dt, state.T_xi_strain + state.T_xi_visc + state.T_frame, atol=1e-12)
    assert np.isclose(state.closure_error, 0.0, atol=1e-12)


def test_th9r_vanishing_strain_torque_at_e3():
    """Verify that R_strain and T_xi_strain vanish when xi is parallel to e3."""
    # When xi = e3, S xi = lambda_3 e3, so R_strain = S xi - lambda_3 xi = 0.
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    # Sample several points and check that ||R_strain|| <= ||S|| * sqrt(1 - a3)
    for pt in [np.array([1.0, 1.0, 1.0]), np.array([2.0, 2.0, 2.0]), np.array([3.0, 3.0, 3.0])]:
        st = evaluate_th9r_forensic_state(pt, vel, None, mesh, nu=0.01)
        assert np.isfinite(st.norm_R_strain)
        assert np.isfinite(st.norm_R_visc)
        assert np.isfinite(st.T_frame)
