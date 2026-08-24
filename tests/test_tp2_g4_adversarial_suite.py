"""Adversarial and analytical test suite for TP2-G4-A1."""
import numpy as np
import pytest
from scipy.linalg import svd, expm


def test_q_scaling_invariance_and_inhomogeneity():
    """Verify that Q_s scales as lambda^6, ||D||^2 as lambda^0, and R_Q = Q_s / S_s as lambda^2."""
    nu = 1e-3
    lambda_scale = 3.5

    # Base quantities
    J_omega = np.array([
        [0.1, -0.2, 0.5],
        [0.3, 0.4, -0.1],
        [-0.4, 0.2, 0.7]
    ])
    D = np.array([
        [1.2, 0.3, 0.0],
        [0.1, 0.9, 0.2],
        [0.0, 0.1, 1.0 / (1.2 * 0.9 - 0.3 * 0.1)] # det ~ 1
    ])
    D = D / (np.linalg.det(D) ** (1.0 / 3.0)) # exactly in SL(3, R)
    assert np.isclose(np.linalg.det(D), 1.0)

    # Base integrand
    base_Q_integrand = 2.0 * nu * np.sum((D @ J_omega) ** 2)
    base_D_norm_sq = np.sum(D ** 2)
    base_omega_norm_sq = 2.5
    base_V = 1.2
    base_S = base_omega_norm_sq + base_V
    base_RQ = base_Q_integrand / base_S

    # Rescaled quantities under Navier-Stokes parabolic zoom: J_omega -> lambda^3 J_omega, D -> D, S -> lambda^4 S
    rescaled_J_omega = (lambda_scale ** 3) * J_omega
    rescaled_D = D # lambda^0
    rescaled_Q_integrand = 2.0 * nu * np.sum((rescaled_D @ rescaled_J_omega) ** 2)
    rescaled_D_norm_sq = np.sum(rescaled_D ** 2)
    rescaled_S = (lambda_scale ** 4) * base_S
    rescaled_RQ = rescaled_Q_integrand / rescaled_S

    # Assert scaling properties
    assert np.isclose(rescaled_Q_integrand, base_Q_integrand * (lambda_scale ** 6))
    assert np.isclose(rescaled_D_norm_sq, base_D_norm_sq * (lambda_scale ** 0))
    assert np.isclose(rescaled_RQ, base_RQ * (lambda_scale ** 2))


def test_svd_decomposition_identity():
    """Verify exact SVD orientation decomposition ||D J||_F^2 == ||J||_F^2 * sum(p_i * sigma_i^2)."""
    np.random.seed(42)
    for _ in range(25):
        # Generate random SL(3, R) matrix
        A = np.random.randn(3, 3)
        # SVD of A
        U, s, Vt = svd(A)
        # normalize to SL(3, R)
        s = s / (np.prod(s) ** (1.0 / 3.0))
        if np.linalg.det(U) < 0:
            U[:, 0] *= -1.0
        if np.linalg.det(Vt) < 0:
            Vt[0, :] *= -1.0
        D = U @ np.diag(s) @ Vt
        assert np.isclose(np.linalg.det(D), 1.0)

        # Random Jacobian J
        J = np.random.randn(3, 3)
        J_norm_sq = np.sum(J ** 2)

        # Direct Frobenius norm
        direct_norm_sq = np.sum((D @ J) ** 2)

        # SVD formula components
        V = Vt.T
        sigma_sq = s ** 2
        p = np.zeros(3)
        for i in range(3):
            v_i = V[:, i]
            # |v_i^T J|^2 = sum_k (v_i^T J_{:, k})^2
            proj = v_i @ J
            p[i] = np.sum(proj ** 2) / J_norm_sq

        assert np.isclose(np.sum(p), 1.0)
        svd_norm_sq = J_norm_sq * np.sum(p * sigma_sq)

        assert np.isclose(direct_norm_sq, svd_norm_sq, rtol=1e-12, atol=1e-12)


def test_kinematic_counterexample_decay():
    """Verify that D_K = diag(K, 1, 1/K) with J = e_3 (x) e_1 drives ||D_K|| -> infty while ||D_K J|| -> 0."""
    J = np.zeros((3, 3))
    J[2, 0] = 1.0 # e_3 (x) e_1
    assert np.trace(J) == 0.0
    J_norm = np.linalg.norm(J, 'fro')

    K_values = [1.0, 10.0, 100.0, 1000.0]
    prev_DJ_norm = float('inf')

    for K in K_values:
        D_K = np.diag([K, 1.0, 1.0 / K])
        assert np.isclose(np.linalg.det(D_K), 1.0)

        D_norm = np.linalg.norm(D_K, 'fro')
        DJ = D_K @ J
        DJ_norm_sq = np.sum(DJ ** 2)

        # Analytical expectation: ||D_K J||_F^2 = K^-2 * ||J||_F^2
        expected_DJ_norm_sq = (1.0 / (K ** 2)) * (J_norm ** 2)
        assert np.isclose(DJ_norm_sq, expected_DJ_norm_sq)

        # As K grows, deformation grows but DJ collapses
        if K > 1.0:
            assert D_norm > 1.0
            assert DJ_norm_sq < prev_DJ_norm
        prev_DJ_norm = DJ_norm_sq


def test_incompressibility_worst_case_bound():
    """Verify that incompressibility yields ||D J||_F^2 >= sigma_1^-4 ||J||_F^2."""
    np.random.seed(123)
    for _ in range(50):
        # Generate random SL(3, R) matrix
        A = np.random.randn(3, 3)
        U, s, Vt = svd(A)
        s = np.sort(s / (np.prod(s) ** (1.0 / 3.0)))[::-1] # sigma_1 >= sigma_2 >= sigma_3 > 0
        D = U @ np.diag(s) @ Vt

        J = np.random.randn(3, 3)
        J_norm_sq = np.sum(J ** 2)

        direct_norm_sq = np.sum((D @ J) ** 2)
        sigma_1 = s[0]
        worst_case_lower_bound = (sigma_1 ** -4) * J_norm_sq

        assert direct_norm_sq >= worst_case_lower_bound - 1e-12


def test_periodic_shear_exact_identity():
    """Verify exact algebraic decoupling D_s J_omega == J_omega for 3D periodic shear family."""
    # E_12 and E_32 definitions
    E12 = np.zeros((3, 3))
    E12[0, 1] = 1.0

    E32 = np.zeros((3, 3))
    E32[2, 1] = 1.0

    # Orthogonality of matrix products
    assert np.allclose(E12 @ E32, 0.0)

    # For any shear parameter alpha
    alpha_values = [-100.0, -1.5, 0.0, 2.7, 50.0, 1000.0]
    for alpha in alpha_values:
        D = np.eye(3) + alpha * E12
        assert np.isclose(np.linalg.det(D), 1.0) # det(I + alpha E12) = 1

        U_yy = -3.42 # arbitrary curvature
        J_omega = -U_yy * E32

        # Compute D @ J_omega
        DJ_omega = D @ J_omega

        # Must be IDENTICALLY J_omega, with ZERO dependence on alpha
        assert np.allclose(DJ_omega, J_omega)
        assert np.isclose(np.sum(DJ_omega ** 2), np.sum(J_omega ** 2))
        assert np.isclose(np.sum(DJ_omega ** 2), U_yy ** 2)


def test_high_wavenumber_shear_reverse_independence():
    """Verify that large Q_s can occur with infinitesimal deformation (reverse implication failure)."""
    nu = 1e-3
    A = 2.0
    k_values = [1, 5, 10, 50, 100]

    for k in k_values:
        # short lookback horizon h = k^-1.5
        h = k ** -1.5
        # shear accumulation alpha ~ A * k * h = A * k^-0.5 -> 0
        alpha = A * k * h
        D = np.eye(3) + alpha * np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]])
        D_norm_sq = np.sum(D ** 2) # = 3 + alpha^2 -> 3

        # Vorticity Hessian/gradient ~ A * k^2
        U_yy_max = A * (k ** 2)
        # Q_s ~ 2 * nu * (U_yy_max)^2 = 2 * nu * A^2 * k^4
        Q_s = 2.0 * nu * (U_yy_max ** 2)

        if k >= 50:
            # D is arbitrarily close to Identity
            assert np.isclose(D_norm_sq, 3.0, atol=1e-1)
            # Q_s is massive
            assert Q_s > 100.0


def test_rq_log_chi_rate_identity():
    """Verify that R_Q(s) = Q_s / S_s == d_s ln(chi_s)."""
    omega_T_sq = 4.0
    V_s = 1.5 # scalar variance budget
    Q_s = 0.8 # production rate = -d_s V_s

    S_s = omega_T_sq + V_s
    chi_s = omega_T_sq / (omega_T_sq + V_s)

    # R_Q definition
    R_Q = Q_s / S_s

    # d_s chi_s = (omega_T_sq / (omega_T_sq + V_s)^2) * Q_s
    d_s_chi_s = (omega_T_sq / (S_s ** 2)) * Q_s
    # d_s ln(chi_s) = (1 / chi_s) * d_s chi_s
    d_s_ln_chi = (1.0 / chi_s) * d_s_chi_s

    assert np.isclose(R_Q, d_s_ln_chi)


def test_orientation_factor_bounds():
    """Verify 0 <= A_nabla_omega <= sigma_1^2 and normalized ratio eta_s in (0, 1]."""
    np.random.seed(999)
    for _ in range(20):
        A = np.random.randn(3, 3)
        U, s, Vt = svd(A)
        s = np.sort(s / (np.prod(s) ** (1.0 / 3.0)))[::-1]
        D = U @ np.diag(s) @ Vt

        J = np.random.randn(3, 3)
        J_norm_sq = np.sum(J ** 2)

        direct_norm_sq = np.sum((D @ J) ** 2)
        A_nabla = direct_norm_sq / J_norm_sq
        sigma_1_sq = s[0] ** 2

        # 0 < A_nabla <= sigma_1^2
        assert A_nabla > 0.0
        assert A_nabla <= sigma_1_sq + 1e-12

        eta_s = direct_norm_sq / (sigma_1_sq * J_norm_sq)
        assert eta_s > 0.0
        assert eta_s <= 1.0 + 1e-12
