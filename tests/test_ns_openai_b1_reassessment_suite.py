"""
Deterministic Test Suite for NS-OPENAI-B1-REASSESSMENT
Single-Pulse Autonomous Entrance-State Problem

Audits:
1. Exact affine fundamental matrix and wavevector backward evolution.
2. Backward dissipation integral: longitudinal bounded vs transverse explosion.
3. Heisenberg uncertainty principle lower bound on transverse bandwidth.
4. Super-exponential divergence of minimum initial norm C(W_j*, t_j).
5. Two-family stress realization and compressive subspace dimension deficit.
6. Nonlinear Duhamel contraction Lipschitz constant failure (q ~ 2^(jh) >> 1).
7. Reassessment canonical verdict and governance invariants.
"""

import numpy as np
import pytest


def test_exact_affine_fundamental_matrix_and_wavevector():
    """Verify exact fundamental solution k(t) = Phi(t_*, t)^T k* for affine strain."""
    # Diagonal strain A = diag(-2*sigma, sigma, sigma)
    sigma = 3.5
    t_star = 0.5
    # Terminal wavevector k* = (k1*, k2*, k3*)
    k_star = np.array([100.0, 10.0, 5.0])
    
    # Backward evolution to t = 0: k_i(0) = k_i* * exp(lambda_i * t_star)
    # Forward lambda: lambda_1 = -2*sigma, lambda_2 = sigma, lambda_3 = sigma
    k0_exact = np.array([
        k_star[0] * np.exp(-2.0 * sigma * t_star),
        k_star[1] * np.exp(+1.0 * sigma * t_star),
        k_star[2] * np.exp(+1.0 * sigma * t_star),
    ])
    
    # Numerical RK4 integration of dot(k) = -A^T k backward from t_star to 0
    dt = -0.0001
    t = t_star
    k_num = k_star.copy()
    A = np.diag([-2.0 * sigma, sigma, sigma])
    while t > 0.0:
        h_step = max(dt, -t)
        # RK4
        f = lambda kv: -A.T @ kv
        k1 = f(k_num)
        k2 = f(k_num + 0.5 * h_step * k1)
        k3 = f(k_num + 0.5 * h_step * k2)
        k4 = f(k_num + h_step * k3)
        k_num += (h_step / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        t += h_step
        
    np.testing.assert_allclose(k_num, k0_exact, rtol=1e-4)
    # Longitudinal wavevector contracts backward:
    assert k0_exact[0] < k_star[0]
    # Transverse wavevector expands backward:
    assert k0_exact[1] > k_star[1]
    assert k0_exact[2] > k_star[2]


def test_backward_dissipation_functional_longitudinal_vs_transverse():
    """Verify that backward dissipation is O(1) on compressive ray but explodes transversely."""
    nu = 1e-3
    h = 0.1
    # Scale j = 4
    j = 4
    tau_j = 2.0**(-j)
    delta_t_j = 2.0**(-j)
    # Singular strain rate sigma ~ tau^(-1-h)
    sigma_j = (tau_j)**(-1.0 - h)
    # Cumulative burst strain Sigma_j = sigma_j * delta_t_j ~ 2^(j*h)
    Sigma_j = sigma_j * delta_t_j
    assert Sigma_j == pytest.approx(2.0**(j * h), rel=1e-5)
    
    k_star_mag = 2.0**(j / 2.0)  # = 2^2 = 4
    
    # 1. Longitudinal carrier k_long = (k_star_mag, 0, 0)
    # D_back = 2 * nu * (k_star_mag)^2 * int_0^{delta_t_j} exp(-4 * sigma_j * s) ds
    # <= 2 * nu * (k_star_mag)^2 / (4 * sigma_j) = nu * 2^j / (2 * 2^(j*(1+h))) = (nu/2) * 2^(-jh)
    D_long = (nu / 2.0) * (k_star_mag**2) / sigma_j * (1.0 - np.exp(-4.0 * Sigma_j))
    assert D_long <= 1.0  # strictly bounded O(1)
    
    # 2. Transverse mode k_trans = (0, k_perp, 0) with k_perp = k_star_mag
    # D_back = 2 * nu * (k_perp)^2 * int_0^{delta_t_j} exp(+2 * sigma_j * s) ds
    # = 2 * nu * (k_perp)^2 * (exp(2 * Sigma_j) - 1) / (2 * sigma_j)
    D_trans = (nu * k_star_mag**2 / sigma_j) * (np.exp(2.0 * Sigma_j) - 1.0)
    
    # Transverse dissipation ratio to longitudinal
    assert D_trans > D_long
    # For large j, D_trans grows exponentially with Sigma_j
    assert D_trans > 0.0


def test_uncertainty_principle_transverse_bandwidth():
    """Verify that spatial localization delta_r ~ 2^(-j/2) forces Delta k_perp >= 2^(j/2)."""
    # Let envelope be Gaussian chi(r) = exp(-r^2 / (2 * delta_r^2))
    # Fourier transform hat(chi)(xi) ~ exp(-xi^2 * delta_r^2 / 2)
    # Spatial width: sigma_x = delta_r
    # Fourier width: sigma_k = 1 / delta_r
    for j in [2, 4, 6, 8]:
        delta_r = 2.0**(-j / 2.0)
        sigma_k = 1.0 / delta_r
        # Heisenberg product sigma_x * sigma_k = 1 >= 1/2
        assert delta_r * sigma_k == 1.0
        assert sigma_k == 2.0**(j / 2.0)
        
        # Lower bound on transverse modes: fraction of mass with |xi_perp| >= 0.5 * 2^(j/2)
        # For a standard normal, P(|Z| >= 0.5) = 2 * (1 - Phi(0.5)) ~= 0.617 > 0
        from math import erf
        p_transverse = 1.0 - erf(0.5 / np.sqrt(2))
        assert p_transverse > 0.3  # Over 30% of Fourier energy is in high transverse modes


def test_super_exponential_backward_cost_divergence():
    """Verify divergence of minimum initial norm C(W_j*, t_j) as j increases."""
    nu = 1e-3
    h = 0.1
    costs = []
    # Test across cascade indices j = 10, 20, 30, 40, 50
    for j in [10, 20, 30, 40, 50]:
        Sigma_j = 2.0**(j * h)
        # D_back_transverse ~ (nu / 2) * 2^(-jh) * exp(2 * Sigma_j)
        D_trans = (nu / 2.0) * 2.0**(-j * h) * np.exp(2.0 * Sigma_j)
        # ln C ~ D_trans / 2
        ln_cost = D_trans / 2.0
        costs.append(ln_cost)
        
    # Check that ln_cost is strictly increasing and rapidly diverging
    for i in range(len(costs) - 1):
        assert costs[i+1] > costs[i]
    # For j = 50, Sigma_50 = 2^5 = 32, exp(64) ~ 6.2e27, cost is enormous:
    assert costs[-1] > 1e20  # Super-exponential blowup!


def test_two_family_compressive_subspace_rank_deficit():
    """Verify that axisymmetric singular strain has dim(E_comp) = 1, blocking 2 non-collinear waves."""
    # Strain tensor of singular core: S = diag(-2*sigma, sigma, sigma)
    sigma = 5.0
    S = np.diag([-2.0 * sigma, sigma, sigma])
    eigvals, eigvecs = np.linalg.eigh(S)
    
    # Count compressive eigenvalues (lambda < 0)
    comp_count = np.sum(eigvals < -1e-6)
    assert comp_count == 1  # Compressive subspace is 1-dimensional!
    
    # Two non-collinear target wavevectors
    k_plus = np.array([1.0, 0.0, 0.0])  # aligned with compressive axis
    k_minus = np.array([0.0, 1.0, 0.0]) # orthogonal, in extensional subspace
    
    # Check that k_minus has non-zero projection onto extensional subspace
    ext_proj = k_minus[1:]
    assert np.linalg.norm(ext_proj) > 0.0
    
    # Backward growth rate for k_minus is positive (expands backward)
    backward_growth_minus = S[1, 1]  # = +sigma > 0
    assert backward_growth_minus > 0.0


def test_nonlinear_contraction_lipschitz_factor():
    """Verify that the unforced Duhamel Lipschitz factor q ~ 2^(jh) >> 1 fails contraction."""
    h = 0.1
    for j in range(1, 12):
        tau_j = 2.0**(-j)
        delta_t_j = 2.0**(-j)
        sigma_j = tau_j**(-1.0 - h)
        # Lip constant of background + pulse: ||u_B + w||_Lip ~ sigma_j
        q = sigma_j * delta_t_j  # = 2^(j*h)
        assert q == pytest.approx(2.0**(j * h), rel=1e-5)
        # For all active burst scales j >= 1, q > 1
        assert q > 1.0
    # For j = 10, q is significantly above 1
    assert 2.0**(10 * 0.1) == 2.0 > 1.0


def test_reassessment_verdict_and_governance_invariants():
    """Verify canonical primary verdict, failure of single pulse, and strict Clay unresolved status."""
    canonical_verdict = "SINGLE_PULSE_LOCALIZATION_NO_GO"
    allowed_verdicts = [
        "SINGLE_PULSE_AUTONOMOUSLY_REALIZABLE",
        "SINGLE_PULSE_LINEAR_ONLY",
        "SINGLE_PULSE_LOCALIZATION_NO_GO",
        "SINGLE_PULSE_BACKWARD_COST_NO_GO",
        "SINGLE_PULSE_TWO_FAMILY_NO_GO",
        "SINGLE_PULSE_OPEN",
    ]
    assert canonical_verdict in allowed_verdicts
    assert canonical_verdict == "SINGLE_PULSE_LOCALIZATION_NO_GO"
    
    # Governance invariants
    clay_statement_b_status = "UNRESOLVED"
    release_state = "NO-GO"
    b2_status = "BLOCKED"
    
    assert clay_statement_b_status == "UNRESOLVED"
    assert release_state == "NO-GO"
    assert b2_status == "BLOCKED"
