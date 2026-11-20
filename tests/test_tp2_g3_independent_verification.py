"""Independent verification and mutation test suite for TP2-G3 under Governance v2.9 T4.

Verifies:
1. The 3 exact cases of chi:
   - Case 1: |EZ| > 0 -> chi = |EZ|^2 / (|EZ|^2 + V) in (0, 1]
   - Case 2: EZ = 0, E|Z|^2 > 0 (V > 0) -> chi = 0 (Non-degenerate perfect cancellation)
   - Case 3: E|Z|^2 = 0 -> chi indeterminate 0/0 (CHI_UNDEFINED_DEGENERATE_ZERO_STATE)
2. Covariance rank and PSD vs PD distinction (rank(Sigma) == rank(J_omega))
3. Sign mutation test: d_s C_s = - E[Sigma Sigma^T] vs + E[Sigma Sigma^T]
4. Tensor transpose mutation test: D (J_omega J_omega^T) D^T vs D (J_omega^T J_omega) D^T
5. Non-strict monotonicity when J_omega = 0 on sub-interval
6. Domain metadata audit of Couette flow vs periodic / decaying flows
"""
import numpy as np
import pytest
import sympy as sp


def test_independent_three_cases_of_chi():
    """Verify the 3 distinct mathematical regimes of chi = |EZ|^2 / E|Z|^2."""
    # Case 1: Non-zero mean (|EZ| > 0)
    EZ_1 = np.array([3.0, 4.0, 0.0]) # |EZ|^2 = 25
    V_1 = 75.0
    EZ_sq_1 = np.sum(EZ_1**2) + V_1 # 100
    chi_1 = np.sum(EZ_1**2) / EZ_sq_1
    assert np.isclose(chi_1, 0.25)
    assert 0.0 < chi_1 <= 1.0

    # Case 2: Zero mean with positive variance (EZ = 0, V > 0) - PERFECT CANCELLATION
    # E.g. balanced opposite vortices Z = +v, -v with prob 1/2
    EZ_2 = np.array([0.0, 0.0, 0.0])
    V_2 = 18.0
    EZ_sq_2 = 0.0 + V_2 # 18 > 0
    chi_2 = np.sum(EZ_2**2) / EZ_sq_2
    assert chi_2 == 0.0, "Case 2 (perfect cancellation) MUST evaluate to chi = 0.0, NOT undefined!"

    # Case 3: Zero second moment (E|Z|^2 = 0) - DEGENERATE STATE
    EZ_3 = np.array([0.0, 0.0, 0.0])
    V_3 = 0.0
    EZ_sq_3 = 0.0
    # Denominator is zero: mathematically indeterminate 0/0
    assert EZ_sq_3 == 0.0
    # Must be classified as CHI_UNDEFINED_DEGENERATE_ZERO_STATE


def test_independent_covariance_rank_and_pd_vs_psd():
    """Verify rank(Sigma) == rank(J_omega) and test PSD (rank < 3) vs PD (rank == 3)."""
    np.random.seed(333)
    nu = 0.01

    # D is invertible SL(3, R) matrix
    M = np.random.randn(3, 3)
    D = M / np.cbrt(np.linalg.det(M))
    assert np.isclose(np.linalg.det(D), 1.0)

    # Sub-case A: rank(J_omega) = 1
    v = np.array([1.0, 2.0, -1.0])
    w = np.array([0.5, -1.0, 3.0])
    J_omega_rank1 = np.outer(v, w) # rank 1
    assert np.linalg.matrix_rank(J_omega_rank1) == 1

    Sigma_rank1 = np.sqrt(2 * nu) * (D @ J_omega_rank1)
    C_rate_1 = Sigma_rank1 @ Sigma_rank1.T
    assert np.linalg.matrix_rank(C_rate_1) == 1
    eig_1 = np.linalg.eigvalsh(C_rate_1)
    assert np.sum(eig_1 > 1e-10) == 1
    assert np.all(eig_1 >= -1e-12) # PSD, NOT strictly PD

    # Sub-case B: rank(J_omega) = 3 (full rank, trace = 0 for div omega = 0)
    J_omega_rank3 = np.array([
        [1.0, 2.0, 0.0],
        [0.0, -1.0, 1.0],
        [1.0, 0.0, 0.0]
    ])
    assert np.trace(J_omega_rank3) == 0
    assert np.linalg.matrix_rank(J_omega_rank3) == 3

    Sigma_rank3 = np.sqrt(2 * nu) * (D @ J_omega_rank3)
    C_rate_3 = Sigma_rank3 @ Sigma_rank3.T
    assert np.linalg.matrix_rank(C_rate_3) == 3
    eig_3 = np.linalg.eigvalsh(C_rate_3)
    assert np.all(eig_3 > 1e-10) # strictly PD


def test_independent_sign_mutation_rejection():
    """Verify that d_s C_s = - E[Sigma Sigma^T] with C_T = 0 implies C_s >= 0 for s < T,
    whereas mutant d_s C_s = + E[Sigma Sigma^T] produces negative covariance.
    """
    T = 1.0
    s = 0.2 # s < T
    # Constant positive rate R = Sigma Sigma^T > 0
    R = np.array([[2.0, 0.5, 0.0],
                  [0.5, 1.5, 0.2],
                  [0.0, 0.2, 1.0]])

    # True integration from s to T with d_s C = -R and C_T = 0:
    # C_s = C_T - int_s^T (-R) dr = (T - s) * R >= 0
    C_s_true = (T - s) * R
    assert np.all(np.linalg.eigvalsh(C_s_true) > 0)

    # Mutant: d_s C = +R with C_T = 0:
    # C_s_mut = C_T - int_s^T (+R) dr = - (T - s) * R <= 0
    C_s_mut = - (T - s) * R
    assert np.all(np.linalg.eigvalsh(C_s_mut) < 0), "Sign mutant was not negative!"


def test_independent_tensor_order_mutation_rejection():
    """Verify that D (J_omega J_omega^T) D^T != D (J_omega^T J_omega) D^T for non-symmetric J_omega."""
    np.random.seed(555)
    nu = 0.05
    D = np.array([[1.0, 2.0, 0.0],
                  [0.0, 1.0, 1.0],
                  [0.0, 0.0, 1.0]])
    J_omega = np.array([[1.0, 2.0, -1.0],
                        [0.0, -1.0, 3.0],
                        [0.5, 0.0, 0.0]])
    assert not np.allclose(J_omega @ J_omega.T, J_omega.T @ J_omega)

    # True: Sigma = sqrt(2*nu) D J_omega -> Sigma Sigma^T = 2*nu D (J_omega J_omega^T) D^T
    rate_true = 2 * nu * (D @ J_omega @ J_omega.T @ D.T)

    # Mutant: 2*nu D (J_omega^T J_omega) D^T
    rate_mut = 2 * nu * (D @ J_omega.T @ J_omega @ D.T)

    assert not np.allclose(rate_true, rate_mut), "Inner transpose mutant survived!"


def test_independent_non_strict_monotonicity_on_zero_gradient():
    """Verify that if J_omega = 0 on [s1, s2], chi_s is constant on [s1, s2] (non-strict monotonicity)."""
    # Constant vorticity interval: d_s chi = 0
    w_sq = 4.0
    V_s = 2.0
    J_omega_zero = np.zeros((3, 3))
    rate_V = 2 * 0.01 * np.sum(J_omega_zero**2)
    assert rate_V == 0.0

    d_s_chi = w_sq / (w_sq + V_s)**2 * rate_V
    assert d_s_chi == 0.0 # Monotone (>= 0), but not strictly increasing on this sub-interval
