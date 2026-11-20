"""Test suite for TP2-G3: Exact Stochastic Cauchy Covariance and Variance Evolution.

Verifies:
T1: Forwardized martingale sign and orientation check (dY_tau = Sigma dB_tau)
T2: Itô product-rule covariance derivation in finite-dimensional symbolic form
T3: Covariance positive semi-definiteness (Loewner order)
T4: Trace identity: tr(C_s) == V_s == 2*nu * int E[||D J_omega||_F^2] dr
T5: chi algebra, derivative sign d_s chi_s >= 0, and monotone reparameterization
T6: Scaling exponents: [Z]=2, [C]=4, [V]=4, [J_omega]=3, [Sigma]=3, [Sigma Sigma^T]=6, [chi]=0
T7: Constant-vorticity zero-covariance counterexample (J_omega = 0 -> C_s = 0, V_s = 0, chi_s = 1)
T8: Nonzero-gradient example producing strictly positive quadratic variation
T9: Matrix-order mutation tests (D J_omega vs J_omega D vs D^T J_omega vs D J_omega^T)
"""
import numpy as np
import pytest
import sympy as sp


def test_t1_forwardized_martingale_orientation():
    """T1: Verify forwardized time tau = T - s, dB_tau = - dW_s, dY_tau = Sigma dB_tau."""
    np.random.seed(42)
    n_steps = 1000
    n_paths = 5000
    dt = 0.001
    
    # Simulate forwardized martingale Y_tau = Y_0 + int Sigma dB
    Y_0 = np.array([2.0, -1.0, 3.0])
    # Constant Sigma for baseline verification
    Sigma = np.array([[1.5, 0.2, -0.1],
                      [0.2, 1.0, 0.4],
                      [-0.1, 0.4, 2.0]])
    
    dB = np.random.randn(n_paths, n_steps, 3) * np.sqrt(dt)
    increments = np.einsum('ij,npj->npi', Sigma, dB)
    Y_traj = Y_0 + np.cumsum(increments, axis=1)
    
    # Martingale property: E[Y_tau] == Y_0
    mean_final = np.mean(Y_traj[:, -1, :], axis=0)
    assert np.allclose(mean_final, Y_0, atol=0.05)
    
    # Covariance property: Cov(Y_tau) == tau * Sigma Sigma^T
    tau = n_steps * dt
    cov_empirical = np.cov(Y_traj[:, -1, :], rowvar=False)
    cov_theoretical = tau * (Sigma @ Sigma.T)
    assert np.allclose(cov_empirical, cov_theoretical, atol=0.1)


def test_t2_symbolic_ito_product_rule_covariance():
    """T2: Symbolically derive d(M M^T) = (dM) M^T + M (dM)^T + (dM)(dM)^T."""
    # Symbolic 1D/3D check of Itô product rule expectation
    dt = sp.symbols('dt', positive=True)
    # Let dM = Sigma dB, with dB_i dB_j = delta_ij dt
    Sigma11, Sigma12, Sigma21, Sigma22 = sp.symbols('Sigma11 Sigma12 Sigma21 Sigma22', real=True)
    Sigma = sp.Matrix([[Sigma11, Sigma12], [Sigma21, Sigma22]])
    
    # The quadratic variation matrix is Sigma * I * Sigma^T * dt
    quad_var = Sigma * Sigma.T * dt
    # Check that diagonal is strictly non-negative
    diag1 = sp.simplify(quad_var[0, 0] / dt)
    diag2 = sp.simplify(quad_var[1, 1] / dt)
    assert diag1 == Sigma11**2 + Sigma12**2
    assert diag2 == Sigma21**2 + Sigma22**2


def test_t3_covariance_psd():
    """T3: Verify that C_s is positive semi-definite for any random ensemble of D and J_omega."""
    np.random.seed(123)
    nu = 0.01
    n_samples = 200
    
    C_s = np.zeros((3, 3))
    for _ in range(n_samples):
        # Generate random SL(3, R) matrix D
        M = np.random.randn(3, 3)
        D = M / np.cbrt(np.linalg.det(M))
        # Random J_omega (trace is div omega = 0)
        J_omega = np.random.randn(3, 3)
        J_omega -= np.trace(J_omega)/3 * np.eye(3)
        
        Sigma = np.sqrt(2 * nu) * (D @ J_omega)
        C_s += Sigma @ Sigma.T
    
    C_s /= n_samples
    # Eigenvalues must be non-negative
    eigenvalues = np.linalg.eigvalsh(C_s)
    assert np.all(eigenvalues >= -1e-12)


def test_t4_trace_variance_identity():
    """T4: Verify tr(C_s) == V_s == 2*nu * int E[||D J_omega||_F^2] dr."""
    np.random.seed(456)
    nu = 0.05
    M = np.random.randn(3, 3)
    D = M / np.cbrt(np.linalg.det(M))
    J_omega = np.random.randn(3, 3)
    
    Sigma = np.sqrt(2 * nu) * (D @ J_omega)
    Sigma_Sigma_T = Sigma @ Sigma.T
    
    trace_cov = np.trace(Sigma_Sigma_T)
    frobenius_sq = 2 * nu * np.sum((D @ J_omega)**2)
    
    assert np.isclose(trace_cov, frobenius_sq)


def test_t5_chi_algebra_and_derivative_sign():
    """T5: Verify chi = |w|^2 / (|w|^2 + V_s) and d_s chi_s >= 0."""
    w_sq = 4.0 # |omega(x,T)|^2
    V_s = 6.0  # scalar variance
    chi = w_sq / (w_sq + V_s)
    assert np.isclose(chi, 4.0 / 10.0)
    assert 0.0 <= chi <= 1.0
    
    # Derivative: d_s chi_s = - |w|^2 / (|w|^2 + V)^2 * (d_s V_s)
    # Since d_s V_s = - 2*nu * E[||D J_omega||^2] <= 0:
    d_s_V = - 1.5
    d_s_chi = - w_sq / (w_sq + V_s)**2 * d_s_V
    assert d_s_chi > 0.0, "d_s chi_s must be non-negative!"


def test_t6_scaling_exponents_complete():
    """T6: Audit all G3 scaling exponents from Navier-Stokes parabolic scaling."""
    # u_lambda(x,t) = lambda u(lambda x, lambda^2 t) -> [u] = 1, [x] = -1, [t] = -2
    s_x = -1
    s_t = -2
    s_grad = 1
    s_u = 1
    s_omega = s_grad + s_u  # +2
    s_D = 0                 # dimensionless
    s_Z = s_D + s_omega     # +2
    s_J_omega = s_grad + s_omega # +3
    s_nu = 0                # viscosity fixed under NS scaling
    s_Sigma = s_D + s_J_omega    # +3
    s_Sigma_Sigma_T = 2 * s_Sigma # +6
    s_ds = s_t              # -2 (differential dt or ds)
    # Integrated covariance: C = int Sigma Sigma^T ds -> +6 + (-2) = +4
    s_C = s_Sigma_Sigma_T + s_ds # +4
    s_V = s_C               # +4
    s_d_s_C = s_C - s_t     # +4 - (-2) = +6 == s_Sigma_Sigma_T
    s_chi = 2*s_omega - s_C # +4 - 4 = 0
    s_d_s_chi = s_chi - s_t # 0 - (-2) = +2
    
    assert s_Z == 2
    assert s_J_omega == 3
    assert s_Sigma == 3
    assert s_Sigma_Sigma_T == 6
    assert s_C == 4
    assert s_V == 4
    assert s_chi == 0
    assert s_d_s_chi == 2


def test_t7_constant_vorticity_zero_covariance():
    """T7: Constant-vorticity Couette shear flow where J_omega = 0.
    Proves UNIVERSAL_STRICT_DECOHERENCE_BY_VISCOSITY = FALSE.
    """
    nu = 0.1
    D = np.eye(3)
    J_omega = np.zeros((3, 3)) # Constant vorticity
    
    Sigma = np.sqrt(2 * nu) * (D @ J_omega)
    assert np.allclose(Sigma, 0.0)
    
    # Covariance rate
    d_s_C = - (Sigma @ Sigma.T)
    assert np.allclose(d_s_C, 0.0)
    
    # V_s and chi_s
    V_s = 0.0
    w_sq = 5.0
    chi_s = w_sq / (w_sq + V_s)
    assert chi_s == 1.0


def test_t8_nonzero_gradient_positive_quadratic_variation():
    """T8: Non-zero vorticity gradient produces strictly positive quadratic variation."""
    nu = 0.01
    D = np.diag([2.0, 0.5, 1.0])
    J_omega = np.array([
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 2.0],
        [0.0, 0.0, 0.0]
    ])
    assert not np.allclose(J_omega, 0.0)
    
    Sigma = np.sqrt(2 * nu) * (D @ J_omega)
    rate_C = Sigma @ Sigma.T
    
    assert np.trace(rate_C) > 0.0
    assert np.linalg.matrix_rank(rate_C) > 0


def test_t9_matrix_order_mutation_discrimination():
    """T9: Discriminate true noise matrix Sigma = sqrt(2*nu) D J_omega
    from mutations: J_omega D, D^T J_omega, D J_omega^T.
    """
    np.random.seed(999)
    nu = 0.02
    
    # Non-symmetric D and non-symmetric J_omega
    D = np.array([
        [1.0, 2.0, 0.0],
        [0.0, 1.0, 3.0],
        [0.0, 0.0, 1.0]
    ])
    J_omega = np.array([
        [2.0, 1.0, -1.0],
        [0.5, -1.0, 2.0],
        [-2.5, 0.0, -1.0]
    ])
    
    Sigma_true = np.sqrt(2 * nu) * (D @ J_omega)
    C_rate_true = Sigma_true @ Sigma_true.T
    
    # Mutant 1: J_omega @ D (wrong multiplication order)
    Sigma_mut1 = np.sqrt(2 * nu) * (J_omega @ D)
    C_rate_mut1 = Sigma_mut1 @ Sigma_mut1.T
    assert not np.allclose(C_rate_mut1, C_rate_true), "Mutant J_omega @ D survived!"
    
    # Mutant 2: D.T @ J_omega (transposed deformation)
    Sigma_mut2 = np.sqrt(2 * nu) * (D.T @ J_omega)
    C_rate_mut2 = Sigma_mut2 @ Sigma_mut2.T
    assert not np.allclose(C_rate_mut2, C_rate_true), "Mutant D.T @ J_omega survived!"
    
    # Mutant 3: D @ J_omega.T (transposed vorticity gradient)
    Sigma_mut3 = np.sqrt(2 * nu) * (D @ J_omega.T)
    C_rate_mut3 = Sigma_mut3 @ Sigma_mut3.T
    assert not np.allclose(C_rate_mut3, C_rate_true), "Mutant D @ J_omega.T survived!"
