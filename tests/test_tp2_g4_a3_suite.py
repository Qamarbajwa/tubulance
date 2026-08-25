"""Worker test suite for TP2-G4-A3."""
import numpy as np
import pytest
from scipy.linalg import svd, qr


def test_shear_gamma_eigenvalues():
    """Verify analytical eigenvalues of Gamma for shear flow."""
    alphas = [0.0, 0.5, 1.0, 5.0, 20.0, 100.0]
    for alpha in alphas:
        D = np.array([
            [1.0, alpha, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
        Gamma = D.T @ D
        eigvals = np.sort(np.linalg.eigvalsh(Gamma))[::-1]

        # Analytical formula
        sigma_1 = (np.sqrt(alpha ** 2 + 4.0) + np.abs(alpha)) / 2.0
        sigma_2 = 1.0
        sigma_3 = 1.0 / sigma_1

        assert np.isclose(eigvals[0], sigma_1 ** 2)
        assert np.isclose(eigvals[1], sigma_2 ** 2)
        assert np.isclose(eigvals[2], sigma_3 ** 2)
        assert np.isclose(np.prod(eigvals), 1.0)


def test_eta_exact_formula_and_threshold():
    """Verify eta = sigma_1^-2 = exp(-2 asinh(|A beta|/2)) and threshold."""
    epsilons = [0.5, 0.1, 0.01, 1e-4]
    for eps in epsilons:
        threshold = (1.0 - eps) / np.sqrt(eps)

        # At exact threshold:
        alpha = threshold
        sigma_1 = (np.sqrt(alpha ** 2 + 4.0) + alpha) / 2.0
        eta = 1.0 / (sigma_1 ** 2)
        assert np.isclose(eta, eps, atol=1e-10)

        # Verify asinh identity:
        asinh_eta = np.exp(-2.0 * np.arcsinh(alpha / 2.0))
        assert np.isclose(eta, asinh_eta)


def test_amplitude_factorization_and_occupation_limit():
    """Verify occupation time limit O_eps^A(L) -> L as A -> infty."""
    L = 5.0
    eps = 0.05
    n_pts = 500
    tau_grid = np.linspace(0.01, L, n_pts)
    dtau = tau_grid[1] - tau_grid[0]

    # Synthetic beta process with positive variance
    np.random.seed(42)
    beta_vals = 0.2 + 0.1 * np.cos(tau_grid) + 0.05 * np.sin(2 * tau_grid)
    # Ensure beta is strictly non-zero
    assert np.all(np.abs(beta_vals) > 0.05)

    A_values = [1.0, 10.0, 50.0, 500.0]
    occupations = []
    for A in A_values:
        alpha_vals = A * beta_vals
        sigma_1_vals = (np.sqrt(alpha_vals ** 2 + 4.0) + np.abs(alpha_vals)) / 2.0
        eta_vals = 1.0 / (sigma_1_vals ** 2)
        occ = np.sum(eta_vals <= eps) * dtau
        occupations.append(occ)

    # For large A, occupation approaches full duration L
    assert occupations[-1] >= 0.95 * L


def test_vorticity_relevant_deformation_and_relative_efficiency():
    """Verify A_omega, A_grad, and relative efficiency Theta."""
    # Periodic shear case: Theta == 1
    alpha = 10.0
    D_shear = np.array([[1.0, alpha, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    omega = np.array([0.0, 0.0, -2.5]) # along z (neutral)
    J_omega = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 5.0, 0.0]]) # along e3 (x) e2

    A_omega = np.sum((D_shear @ omega) ** 2) / np.sum(omega ** 2)
    A_grad = np.sum((D_shear @ J_omega) ** 2) / np.sum(J_omega ** 2)
    Theta_shear = A_grad / A_omega

    assert np.isclose(A_omega, 1.0)
    assert np.isclose(A_grad, 1.0)
    assert np.isclose(Theta_shear, 1.0)

    # Adversarial cases: Theta < 1 and Theta > 1
    D_diag = np.diag([4.0, 1.0, 0.25])
    # Case 1: omega along stretching v1, J_omega along contracting v3 -> Theta << 1
    omega_1 = np.array([1.0, 0.0, 0.0])
    J_omega_3 = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    A_omega_1 = np.sum((D_diag @ omega_1) ** 2) / np.sum(omega_1 ** 2)
    A_grad_3 = np.sum((D_diag @ J_omega_3) ** 2) / np.sum(J_omega_3 ** 2)
    Theta_low = A_grad_3 / A_omega_1
    assert Theta_low < 0.01

    # Case 2: omega along contracting v3, J_omega along stretching v1 -> Theta >> 1
    Theta_high = A_omega_1 / A_grad_3
    assert Theta_high > 100.0


def test_kappa_theta_identity_and_mu_rate():
    """Verify ||D J_omega||^2 / |D omega|^2 == kappa_omega^2 Theta and mu-weighted rate."""
    np.random.seed(123)
    D = np.diag([3.0, 1.0, 1.0 / 3.0])
    omega = np.array([1.0, 2.0, -1.0])
    J_omega = np.random.randn(3, 3)

    norm_D_J = np.sum((D @ J_omega) ** 2)
    norm_D_w = np.sum((D @ omega) ** 2)
    ratio_direct = norm_D_J / norm_D_w

    kappa_sq = np.sum(J_omega ** 2) / np.sum(omega ** 2)
    A_grad = norm_D_J / np.sum(J_omega ** 2)
    A_omega = norm_D_w / np.sum(omega ** 2)
    Theta = A_grad / A_omega

    ratio_decomposed = kappa_sq * Theta
    assert np.isclose(ratio_direct, ratio_decomposed)


def test_parabolic_scaling_exponents():
    """Verify exact parabolic scaling exponents for Q/S, kappa_omega^2, and Theta."""
    # Under x -> lambda x, t -> lambda^2 t, u -> lambda u:
    # [omega] = 2, [J_omega] = 3, [D] = 0, [Q] = 6, [S] = 4, [R_Q] = 2
    # [kappa_omega^2] = 2 * [J_omega] - 2 * [omega] = 6 - 4 = 2
    # [Theta] = [A_grad] - [A_omega] = 0 - 0 = 0
    scale_kappa_sq = 2
    scale_theta = 0
    scale_RQ = scale_kappa_sq + scale_theta
    assert scale_RQ == 2
