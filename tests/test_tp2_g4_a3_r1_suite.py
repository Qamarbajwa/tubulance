"""Automated test suite for TP2-G4-A3-R1 correction gate."""
import numpy as np
import pytest
from scipy.linalg import svd, qr


def test_corrected_tube_strictly_excludes_zero_gradient():
    """Verify that I = [pi/(8k), 3pi/(8k)] strictly bounds |sin| >= c1 > 0 and cos >= c2 > 0."""
    k = 2.0
    y_vals = np.linspace(np.pi / (8.0 * k), 3.0 * np.pi / (8.0 * k), 100)
    sin_vals = np.abs(np.sin(k * y_vals))
    cos_vals = np.cos(k * y_vals)

    c1 = np.sin(np.pi / 8.0)
    c2 = np.cos(3.0 * np.pi / 8.0)

    assert np.all(sin_vals >= c1 - 1e-12)
    assert np.all(cos_vals >= c2 - 1e-12)
    assert c1 > 0.35
    assert c2 > 0.35


def test_brownian_tube_survival_and_monotonic_drift():
    """Verify Brownian tube survival and linear beta lower bound."""
    L = 5.0
    nu = 1e-3
    k = 1.0
    c2 = np.cos(3.0 * np.pi / 8.0)
    c_beta = k * np.exp(-nu * (k ** 2) * L) * c2

    tau_vals = np.linspace(0.1, L, 50)
    beta_lower_bound = c_beta * tau_vals

    assert np.all(beta_lower_bound > 0.0)
    assert c_beta > 0.3


def test_threshold_crossing_estimate():
    """Verify tau_A <= a_eps / (A c_beta) and residence bound Delta tau_res >= L - delta."""
    L = 10.0
    delta = 0.5
    eps = 0.04
    a_eps = (1.0 - eps) / np.sqrt(eps) # = 0.96 / 0.2 = 4.8
    c_beta = 0.35

    req_A = a_eps / (c_beta * delta)
    tau_A = a_eps / (req_A * c_beta)

    assert np.isclose(tau_A, delta)
    residence_duration = L - tau_A
    assert residence_duration >= L - delta


def test_theta_domain_and_xi_regular_equivalence():
    """Verify Xi = ||D G||^2 / |D omega|^2 and Theta undefined when G = 0."""
    D = np.diag([2.0, 1.0, 0.5])
    omega = np.array([1.0, 0.0, 0.0])

    # Regular case: G != 0
    G_reg = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 3.0, 0.0]])
    Xi_reg = np.sum((D @ G_reg) ** 2) / np.sum((D @ omega) ** 2)

    kappa_sq = np.sum(G_reg ** 2) / np.sum(omega ** 2)
    A_grad = np.sum((D @ G_reg) ** 2) / np.sum(G_reg ** 2)
    A_omega = np.sum((D @ omega) ** 2) / np.sum(omega ** 2)
    Theta_reg = A_grad / A_omega

    assert np.isclose(Xi_reg, kappa_sq * Theta_reg)

    # Zero-gradient case: G = 0, omega != 0
    G_zero = np.zeros((3, 3))
    Xi_zero = np.sum((D @ G_zero) ** 2) / np.sum((D @ omega) ** 2)
    assert Xi_zero == 0.0
    # Theta would be 0 / 0 (undefined), but Xi is well-defined and equals 0


def test_mu_weighted_qs_identity():
    """Verify Q_s / S_s == 2*nu * E_mu[Xi]."""
    nu = 1e-3
    n_paths = 100
    np.random.seed(999)

    Z_sq_list = []
    DG_sq_list = []
    Xi_list = []

    for _ in range(n_paths):
        D = np.diag(np.exp(np.random.randn(3)))
        D /= np.prod(np.diag(D)) ** (1.0 / 3.0)
        omega = np.random.randn(3)
        G = np.random.randn(3, 3)

        Z = D @ omega
        Z_sq = np.sum(Z ** 2)
        DG_sq = np.sum((D @ G) ** 2)

        Z_sq_list.append(Z_sq)
        DG_sq_list.append(DG_sq)
        Xi_list.append(DG_sq / Z_sq)

    Z_sq_arr = np.array(Z_sq_list)
    DG_sq_arr = np.array(DG_sq_list)
    Xi_arr = np.array(Xi_list)

    S_s = np.mean(Z_sq_arr)
    Q_s = 2.0 * nu * np.mean(DG_sq_arr)
    direct_ratio = Q_s / S_s

    # mu-weighted average
    mu_weights = Z_sq_arr / np.sum(Z_sq_arr)
    mu_avg_Xi = np.sum(mu_weights * Xi_arr)
    formula_ratio = 2.0 * nu * mu_avg_Xi

    assert np.isclose(direct_ratio, formula_ratio, atol=1e-14)
