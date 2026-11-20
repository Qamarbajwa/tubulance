"""Verifier-Owned Analytical Golden Test Fixtures.

Implements Sections 24, 25, 26 of Milestone V2.
"""
from __future__ import annotations

import math
from typing import Dict, Any, Tuple

import numpy as np

from .metric_oracle import oracle_velocity_relative_l2, oracle_subspace_overlap


def get_golden_zero_error_fixture() -> Tuple[np.ndarray, np.ndarray, float]:
    """Analytical zero-error fixture: u_c = u_r -> E_u = 0.0."""
    ref = np.ones((10, 10, 10), dtype=np.float64)
    cand = np.ones((10, 10, 10), dtype=np.float64)
    expected_error = 0.0
    return ref, cand, expected_error


def get_golden_scaling_fixture() -> Tuple[np.ndarray, np.ndarray, float]:
    """Analytical scaling fixture: u_c = 2 * u_r -> ||u_r - 2 u_r|| / ||u_r|| = 1.0."""
    ref = np.ones((10, 10, 10), dtype=np.float64)
    cand = np.ones((10, 10, 10), dtype=np.float64) * 2.0
    expected_error = 1.0
    return ref, cand, expected_error


def get_golden_orthogonal_bases_fixture() -> Tuple[np.ndarray, np.ndarray, float]:
    """Analytical orthogonal bases fixture: Phi_B = [1,0], Phi_W = [0,1] -> theta = 90.0 degrees."""
    Phi_B = np.array([[1.0], [0.0]], dtype=np.float64)
    Phi_W = np.array([[0.0], [1.0]], dtype=np.float64)
    expected_min_angle = 90.0
    return Phi_B, Phi_W, expected_min_angle


def get_golden_identical_bases_fixture() -> Tuple[np.ndarray, np.ndarray, float]:
    """Analytical identical bases fixture: Phi_B = [1,0], Phi_W = [1,0] -> theta = 0.0 degrees."""
    Phi_B = np.array([[1.0], [0.0]], dtype=np.float64)
    Phi_W = np.array([[1.0], [0.0]], dtype=np.float64)
    expected_min_angle = 0.0
    return Phi_B, Phi_W, expected_min_angle


def verify_golden_fixtures() -> bool:
    """Execute verifier property-based verification on golden fixtures."""
    ref0, cand0, exp0 = get_golden_zero_error_fixture()
    err0 = oracle_velocity_relative_l2(ref0, cand0)
    assert abs(err0 - exp0) < 1e-12, f"Golden zero error test failed: {err0} vs {exp0}"

    ref2, cand2, exp2 = get_golden_scaling_fixture()
    err2 = oracle_velocity_relative_l2(ref2, cand2)
    assert abs(err2 - exp2) < 1e-12, f"Golden scaling error test failed: {err2} vs {exp2}"

    Phi_B90, Phi_W90, exp90 = get_golden_orthogonal_bases_fixture()
    _, _, angle90 = oracle_subspace_overlap(Phi_B90, Phi_W90)
    assert abs(angle90 - exp90) < 1e-6, f"Golden orthogonal angle test failed: {angle90} vs {exp90}"

    Phi_B0, Phi_W0, exp0_deg = get_golden_identical_bases_fixture()
    _, _, angle0 = oracle_subspace_overlap(Phi_B0, Phi_W0)
    assert abs(angle0 - exp0_deg) < 1e-6, f"Golden identical angle test failed: {angle0} vs {exp0_deg}"

    return True
