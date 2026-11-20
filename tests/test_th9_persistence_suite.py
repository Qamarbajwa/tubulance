"""Test suite for Milestone TH9: Dynamical Persistence, Alignment Torques, and Pressure-Hessian Coupling."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.fields import ScalarField
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.th9_persistence_math import (
    evaluate_dynamic_stretching_state,
    compute_pressure_hessian_at_point,
)


def test_alignment_derivative_exact_decomposition():
    """Verify that Da3/Dt == T_xi + T_frame."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)
    p = ScalarField.zeros(mesh)

    pt = np.array([1.5, 2.0, 2.5])
    state = evaluate_dynamic_stretching_state(pt, vel, p, mesh, nu=0.01)

    # Check that Da3_Dt == T_xi + T_frame
    assert np.isclose(state.Da3_Dt, state.T_xi + state.T_frame, atol=1e-6)
    assert np.isfinite(state.frame_rot_rate)
    assert np.isfinite(state.h_xi)


def test_pressure_hessian_trace_evaluation():
    """Verify that pressure Hessian computation produces a symmetric matrix."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    p = ScalarField.zeros(mesh)
    # Fill synthetic pressure field
    xs = (np.arange(mesh.nx) + 0.5) * mesh.dx
    ys = (np.arange(mesh.ny) + 0.5) * mesh.dy
    zs = (np.arange(mesh.nz) + 0.5) * mesh.dz
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    p.interior[:] = np.sin(X) * np.cos(Y) * np.sin(Z)

    pt = np.array([1.0, 1.0, 1.0])
    Hp, tr_H = compute_pressure_hessian_at_point(pt, p, mesh, eps=1e-3)

    # Check symmetry: H_p == H_p^T
    assert np.allclose(Hp, Hp.T, atol=1e-3)
    # Analytic trace of sin(x)cos(y)sin(z) is -3*sin(x)cos(y)sin(z)
    expected_tr = -3.0 * np.sin(1.0) * np.cos(1.0) * np.sin(1.0)
    assert np.isclose(tr_H, expected_tr, atol=0.1)
