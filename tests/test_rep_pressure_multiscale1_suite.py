"""Unit tests for Program NS-REP-PRESSURE-MULTISCALE-1."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.rep_pressure_multiscale1_math import (
    PressureHessianDecompositionResult,
    EigenframeTorqueDecompositionResult,
    NonlocalSurroundingContrastResult,
    decompose_pressure_hessian,
    compute_eigenframe_pressure_torque,
    audit_nonlocal_surrounding_contrast,
)


def test_rep_pressure_multiscale1_math():
    """Verify pressure Hessian decomposition, eigenframe torque, and nonlocal contrast."""
    # 1. Pressure Hessian decomposition
    S = np.diag([2.0, 1.0, -3.0])
    omega = np.array([0.0, 0.0, 4.0])
    H_dev = np.array([[1.0, 0.5, 0.0], [0.5, -1.0, 0.0], [0.0, 0.0, 0.0]])

    res = decompose_pressure_hessian(S=S, omega=omega, H_dev=H_dev)
    assert np.isclose(np.trace(res.deviatoric_hessian), 0.0)
    assert np.isclose(np.trace(res.total_pressure_hessian), res.laplacian_pressure)
    assert np.isclose(res.laplacian_pressure, -res.trace_S2 + res.enstrophy_density)

    # 2. Eigenframe torque decomposition
    torque_res = compute_eigenframe_pressure_torque(
        eigenvalues=( -3.0, 1.0, 2.0 ),
        H_dev=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 3.0], [0.0, 3.0, 0.0]]),
        Omega=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.5], [0.0, -0.5, 0.0]]),
        visc_diff=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.1], [0.0, 0.1, 0.0]]),
    )
    assert np.isfinite(torque_res.total_frame_rate)
    assert torque_res.pressure_fraction_pct > 0.0

    # 3. Nonlocal surrounding contrast
    contrast = audit_nonlocal_surrounding_contrast()
    assert contrast.is_H_dev_different is True
    assert contrast.frobenius_distance > 0.0
