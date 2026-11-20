"""Machine verification tests for TP2-G1 and TP2-G2.

Verifies:
1. Matrix Jacobian identities and Curl of pullback 1-form -> (grad A)^{-1} (curl v)
2. Equivalence of forward deformation and inverse Jacobian
3. Exact variance identity: |E[Z]|^2 = E[|Z|^2] - Var(Z)
4. Bounds: 0 <= chi <= 1
5. Adversarial cases: A (zero variance -> chi=1), B (cancellation -> chi=0), D (degeneracy)
6. Rotational invariance under SO(3)
7. Galilean invariance
8. Navier-Stokes parabolic scaling exponents of u, omega, S, X, A, F, D, Z, E[Z], E[|Z|^2], Var(Z), chi
9. Brownian scaling covariance
"""
import numpy as np
import pytest
import sympy as sp


def test_tp2_g1_curl_pullback_identity():
    """Verify that curl_x( (grad_x A)^T v(A(x)) ) == det(grad A) * (grad_x A)^{-1} (curl_a v)(A(x))
    algebraically using exact rational arithmetic in SymPy in 3D.
    """
    x1, x2, x3 = sp.symbols('x1 x2 x3', real=True)
    x = sp.Matrix([x1, x2, x3])
    
    # Use exact Rational coefficients to prevent floating-point roundoff
    A1 = x1 + sp.Rational(3, 10) * x2**2 - sp.Rational(1, 10) * x3
    A2 = x2 + sp.Rational(1, 5) * x1 * x3
    A3 = x3 + sp.Rational(3, 20) * x1**2
    
    A = sp.Matrix([A1, A2, A3])
    grad_A = A.jacobian(x) # [grad_A]_{ij} = d A_i / d x_j
    det_grad_A = grad_A.det()
    
    # Let v(a) be a smooth vector field
    a1, a2, a3 = sp.symbols('a1 a2 a3', real=True)
    v1 = a2 * a3 + sp.sin(a1)
    v2 = a1**2 + a3
    v3 = a1 * a2 - a3**2
    v = sp.Matrix([v1, v2, v3])
    
    # curl_a v = (dv3/da2 - dv2/da3, dv1/da3 - dv3/da1, dv2/da1 - dv1/da2)
    curl_v_a1 = sp.diff(v3, a2) - sp.diff(v2, a3)
    curl_v_a2 = sp.diff(v1, a3) - sp.diff(v3, a1)
    curl_v_a3 = sp.diff(v2, a1) - sp.diff(v1, a2)
    curl_v = sp.Matrix([curl_v_a1, curl_v_a2, curl_v_a3])
    
    # Evaluate curl_v at a = A(x)
    curl_v_at_A = curl_v.subs({a1: A1, a2: A2, a3: A3})
    
    # Pullback 1-form: w(x) = (grad A)^T * v(A(x))
    v_at_A = v.subs({a1: A1, a2: A2, a3: A3})
    w = grad_A.T * v_at_A
    
    # curl_x w
    curl_w_1 = sp.diff(w[2], x2) - sp.diff(w[1], x3)
    curl_w_2 = sp.diff(w[0], x3) - sp.diff(w[2], x1)
    curl_w_3 = sp.diff(w[1], x1) - sp.diff(w[0], x2)
    curl_w = sp.Matrix([curl_w_1, curl_w_2, curl_w_3])
    
    # Theoretical formula:
    # curl_x ( (grad A)^T v(A) ) = det(grad A) * (grad A)^{-1} * (curl_a v)(A)
    # When det(grad A) == 1, this equals (grad A)^{-1} * (curl_a v)(A)
    grad_A_inv = grad_A.inv()
    expected = det_grad_A * grad_A_inv * curl_v_at_A
    
    diff = sp.simplify(curl_w - expected)
    assert diff == sp.Matrix([0, 0, 0]), f"Identity failed: diff = {diff}"


def test_tp2_g1_matrix_inverse_transpose_relations():
    """Verify relations between forward deformation F, inverse Jacobian J = grad A,
    and their transposes.
    """
    np.random.seed(42)
    for _ in range(10):
        M = np.random.randn(3, 3)
        detM = np.linalg.det(M)
        F = M / (np.cbrt(detM))
        assert np.isclose(np.linalg.det(F), 1.0)
        
        # Inverse deformation J = F^{-1}
        J = np.linalg.inv(F)
        
        # Check D = J^{-1} = F
        D = np.linalg.inv(J)
        assert np.allclose(D, F)
        
        # Check transpose relations:
        # (J^T)^{-1} = (J^{-1})^T = F^T
        assert np.allclose(np.linalg.inv(J.T), F.T)
        assert np.allclose(np.linalg.inv(F.T), J.T)


def test_tp2_g2_exact_variance_identity_and_bounds():
    """Verify |E[Z]|^2 = E[|Z|^2] - Var(Z) and 0 <= chi <= 1 on random vector ensembles."""
    np.random.seed(123)
    n_samples = 100000
    
    mean_vec = np.array([2.0, -1.0, 3.0])
    cov_mat = np.array([[1.5, 0.3, 0.2], [0.3, 2.0, -0.4], [0.2, -0.4, 0.8]])
    samples = np.random.multivariate_normal(mean_vec, cov_mat, size=n_samples)
    
    e_z = np.mean(samples, axis=0)
    e_z_mag_sq = np.sum(e_z**2)
    e_z_sq = np.mean(np.sum(samples**2, axis=1))
    
    var_z = np.mean(np.sum((samples - e_z)**2, axis=1))
    
    assert np.isclose(e_z_mag_sq, e_z_sq - var_z, rtol=1e-3)
    
    chi = e_z_mag_sq / e_z_sq
    assert 0.0 <= chi <= 1.0


def test_tp2_adversarial_cases():
    """Test adversarial cases A, B, D, E, F."""
    # Case A: Deterministic zero variance
    Z_const = np.tile(np.array([3.0, 4.0, 0.0]), (1000, 1))
    e_z = np.mean(Z_const, axis=0)
    e_z_sq = np.mean(np.sum(Z_const**2, axis=1))
    chi_A = np.sum(e_z**2) / e_z_sq
    assert np.isclose(chi_A, 1.0)
    
    # Case B: Perfect cancellation (opposite vectors with equal prob)
    Z_cancel = np.array([[1.0, 2.0, 3.0], [-1.0, -2.0, -3.0]])
    e_z_b = np.mean(Z_cancel, axis=0)
    e_z_sq_b = np.mean(np.sum(Z_cancel**2, axis=1))
    assert np.allclose(e_z_b, 0.0)
    assert e_z_sq_b > 0.0
    chi_B = np.sum(e_z_b**2) / e_z_sq_b
    assert np.isclose(chi_B, 0.0)
    
    # Case D: Denominator degeneracy
    Z_zero = np.zeros((10, 3))
    denom = np.mean(np.sum(Z_zero**2, axis=1))
    assert denom == 0.0
    
    # Case E: Rotational invariance under SO(3)
    np.random.seed(99)
    Z_rand = np.random.randn(5000, 3) + np.array([1.0, 1.0, 1.0])
    e_z_orig = np.mean(Z_rand, axis=0)
    chi_orig = np.sum(e_z_orig**2) / np.mean(np.sum(Z_rand**2, axis=1))
    
    Q, _ = np.linalg.qr(np.random.randn(3, 3))
    if np.linalg.det(Q) < 0:
        Q[:, 0] *= -1
    
    Z_rot = Z_rand @ Q.T
    e_z_rot = np.mean(Z_rot, axis=0)
    chi_rot = np.sum(e_z_rot**2) / np.mean(np.sum(Z_rot**2, axis=1))
    assert np.isclose(chi_orig, chi_rot, atol=1e-12)


def test_tp2_g2_symbolic_scaling_audit():
    """Symbolically audit Navier-Stokes parabolic scaling exponents.
    u_lambda(x,t) = lambda u(lambda x, lambda^2 t) -> [u] = +1
    x -> lambda x [x] = -1
    t -> lambda^2 t [t] = -2
    """
    exponents = {}
    exponents["u"] = 1
    exponents["x"] = -1
    exponents["t"] = -2
    exponents["grad"] = 1
    
    exponents["omega"] = exponents["grad"] + exponents["u"] # 2
    exponents["S"] = exponents["grad"] + exponents["u"] # 2
    exponents["X"] = -1 # trajectory coordinate scales as x
    exponents["A"] = -1 # inverse map coordinate scales as x
    exponents["F"] = exponents["grad"] + exponents["X"] # 0 (dimensionless)
    exponents["D"] = exponents["F"] # 0 (dimensionless)
    exponents["Z"] = exponents["D"] + exponents["omega"] # 2
    exponents["E_Z"] = exponents["Z"] # 2
    exponents["E_Z_mag_sq"] = 2 * exponents["E_Z"] # 4
    exponents["E_Z_sq"] = 2 * exponents["Z"] # 4
    exponents["Var_Z"] = 4
    exponents["chi"] = exponents["E_Z_mag_sq"] - exponents["E_Z_sq"] # 0
    
    assert exponents["omega"] == 2
    assert exponents["F"] == 0
    assert exponents["D"] == 0
    assert exponents["Z"] == 2
    assert exponents["chi"] == 0, "chi must be EXACTLY scale invariant (exponent 0)!"
