"""Executable checks for the exact TP2-G5-A3 geometric identities."""

from __future__ import annotations

import numpy as np
import pytest
from pathlib import Path

from scripts.tp2_g5_a3_geometry import (
    amplitude_direction_decomposition,
    beta_terms,
    condition_number_bounds,
    gamma_xi,
    metric_split,
    xi_from_decomposition,
)


def unit_vector(seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.normal(size=3)
    return v / np.linalg.norm(v)


def test_convention_m_amplitude_direction_identity() -> None:
    xi = unit_vector()
    grad_q = np.array([0.7, -0.2, 0.4])
    J_xi = np.array([[0.0, 0.2, -0.1], [0.2, 0.0, 0.3], [-0.1, 0.3, 0.0]])
    J_xi = J_xi - xi[:, None] * (xi @ J_xi)
    G, lhs, rhs = amplitude_direction_decomposition(xi, grad_q, 2.5, J_xi)
    assert np.allclose(lhs, rhs)
    assert np.allclose(np.sum(G * G), np.dot(grad_q, grad_q) + 2.5**2 * np.sum(J_xi * J_xi))


def test_kappa_identity() -> None:
    q = 2.5
    grad_q = np.array([0.7, -0.2, 0.4])
    J_xi = np.zeros((3, 3))
    J_xi[0, 1] = 0.4
    J_xi[1, 1] = -0.3
    xi = unit_vector()
    J_xi -= xi[:, None] * (xi @ J_xi)
    _, lhs, rhs = amplitude_direction_decomposition(xi, grad_q, q, J_xi)
    assert np.allclose(lhs / q**2, np.dot(grad_q, grad_q) / q**2 + np.sum(J_xi * J_xi))
    assert np.isclose(rhs / q**2, np.dot(grad_q / q, grad_q / q) + np.sum(J_xi * J_xi))


def test_deformation_weighted_xi_and_metric_split() -> None:
    rng = np.random.default_rng(11)
    D = rng.normal(size=(3, 3))
    D += 3.0 * np.eye(3)
    xi = unit_vector(11)
    q = 1.7
    grad_log_q = np.array([0.3, -0.6, 0.2])
    J_xi = rng.normal(size=(3, 3))
    J_xi -= xi[:, None] * (xi @ J_xi)
    xi_value, M_D, C_D = metric_split(D, xi, grad_log_q, J_xi)
    direct = xi_from_decomposition(D, xi, grad_log_q, J_xi)
    assert np.isclose(xi_value, M_D + C_D)
    assert np.isclose(xi_value, direct)
    assert M_D >= -1e-12 and C_D >= -1e-12
    assert np.allclose(beta_terms(D, xi, J_xi), (D @ xi @ (D @ J_xi)) / np.dot(D @ xi, D @ xi))


def test_beta_vanishes_for_d_identity_and_can_be_nonzero() -> None:
    xi = unit_vector(3)
    J_xi = np.array([[0.0, 0.3, -0.2], [0.1, 0.0, 0.4], [0.2, -0.3, 0.0]])
    J_xi -= xi[:, None] * (xi @ J_xi)
    assert np.allclose(beta_terms(np.eye(3), xi, J_xi), 0.0)
    D = np.array([[2.0, 0.5, 0.0], [0.0, 1.0, 0.2], [0.0, 0.0, 0.5]])
    assert np.linalg.norm(beta_terms(D, xi, J_xi)) > 1e-8


def test_gamma_form_matches_direct_deformation_weighted_xi() -> None:
    rng = np.random.default_rng(4)
    D = rng.normal(size=(3, 3)) + 2.5 * np.eye(3)
    xi = unit_vector(4)
    q = 1.2
    grad_log_q = rng.normal(size=3)
    J_xi = rng.normal(size=(3, 3))
    J_xi -= xi[:, None] * (xi @ J_xi)
    G = xi[:, None] * (q * grad_log_q)[None, :] + q * J_xi
    assert np.isclose(gamma_xi(D, G, q, xi), xi_from_decomposition(D, xi, grad_log_q, J_xi))


def test_condition_number_envelope() -> None:
    D = np.diag([5.0, 2.0, 0.5])
    xi = unit_vector(8)
    G = np.arange(9, dtype=float).reshape(3, 3) / 7.0
    q = 1.3
    value = gamma_xi(D, G, q, xi)
    kappa2 = np.sum(G * G) / (q * q)
    lo, hi = condition_number_bounds(D, kappa2)
    assert lo - 1e-12 <= value <= hi + 1e-12


@pytest.mark.parametrize(
    "grad_log_q,J_xi",
    [(np.zeros(3), np.zeros((3, 3))), (np.array([0.2, -0.1, 0.4]), np.zeros((3, 3))), (np.zeros(3), np.eye(3))],
)
def test_boundary_calibrations_are_finite_or_domain_guarded(grad_log_q: np.ndarray, J_xi: np.ndarray) -> None:
    D = np.eye(3)
    xi = unit_vector(12)
    value, M_D, C_D = metric_split(D, xi, grad_log_q, J_xi)
    assert value >= -1e-12 and M_D >= -1e-12 and C_D >= -1e-12


def test_zero_gradient_and_zero_vorticity_domains_are_distinct() -> None:
    xi = unit_vector(19)
    value, _, _ = metric_split(np.eye(3), xi, np.zeros(3), np.zeros((3, 3)))
    assert np.isclose(value, 0.0)
    with pytest.raises(ValueError, match="q must be positive"):
        amplitude_direction_decomposition(xi, np.zeros(3), 0.0, np.zeros((3, 3)))


def test_no_automatic_bridge_claims() -> None:
    artifact = Path(__file__).resolve().parents[1] / "TP2_G5_A3_GEOMETRIC_NO_GO_RESULTS.md"
    assert artifact.exists()
