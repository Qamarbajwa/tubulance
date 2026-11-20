"""Adversarial and convention-reconciliation test suite for TP2-G1R.

Verifies:
1. T1: Non-symmetric linear flow (L != L^T, tr(L)=0) under Convention M
2. T2: Non-symmetric shear flow where F != F^T != F^{-1} != F^{-T}
3. T3: Exact translation between Convention M and Convention F (JFM formulas)
4. T4: Componentwise curl pullback identity with general det B
5. T5: Mutation tests killing all 3 incorrect project-convention choices (D^T, D^{-1}, D^{-T})
"""
import numpy as np
import pytest
import sympy as sp


def test_t1_non_symmetric_linear_flow():
    """T1: Verify Cauchy vorticity representation for non-symmetric linear flow.
    L != L^T, tr(L) = 0, X(a,t) = exp(tL) a, A(x,t) = exp(-tL) x.
    """
    x1, x2, x3 = sp.symbols('x1 x2 x3', real=True)
    x = sp.Matrix([x1, x2, x3])
    a1, a2, a3 = sp.symbols('a1 a2 a3', real=True)
    a = sp.Matrix([a1, a2, a3])
    
    L = sp.Matrix([
        [1, 2, 3],
        [0, -1, 4],
        [0, 0, 0]
    ])
    assert L.trace() == 0
    assert L != L.T
    
    F_M = L.exp() # J_X under Convention M
    B_M = (-L).exp() # J_A under Convention M
    
    # Check B_M == F_M^{-1}
    assert sp.simplify(F_M * B_M) == sp.eye(3)
    assert sp.simplify(B_M * F_M) == sp.eye(3)
    
    # Let omega_0 be an arbitrary initial vorticity vector
    w0 = sp.Matrix([1, -2, 5])
    
    # Exact vorticity under Convention M: omega(t) = F_M * omega_0
    w_true = F_M * w0
    
    # Cauchy backward formula using B_M^{-1}:
    w_from_B_inv = B_M.inv() * w0
    assert sp.simplify(w_true - w_from_B_inv) == sp.Matrix.zeros(3, 1)
    
    # Check that transposed choice F_M^T or B_M^T FAILS:
    w_from_transposed = F_M.T * w0
    diff_T = sp.simplify(w_true - w_from_transposed)
    assert diff_T != sp.Matrix.zeros(3, 1), "Transpose error went undetected!"


def test_t2_non_symmetric_shear_four_matrix_distinction():
    """T2: Non-symmetric shear map ensuring F != F^T != F^{-1} != F^{-T}.
    Tests all 4 candidate multipliers to prove only F_M = B_M^{-1} is valid in Convention M.
    """
    # Shear matrix with det = 1
    F_M = sp.Matrix([
        [1, 2, 0],
        [0, 1, 3],
        [0, 0, 1]
    ])
    assert F_M.det() == 1
    
    F_T = F_M.T
    F_inv = F_M.inv()
    F_inv_T = F_M.inv().T
    
    # Verify all 4 are mutually distinct
    assert F_M != F_T
    assert F_M != F_inv
    assert F_M != F_inv_T
    assert F_T != F_inv
    assert F_T != F_inv_T
    assert F_inv != F_inv_T
    
    # B_M = F_M^{-1}
    B_M = F_inv
    
    # Only B_M^{-1} equals F_M
    assert B_M.inv() == F_M
    assert B_M != F_M
    assert B_M.T != F_M
    assert B_M.inv().T != F_M


def test_t3_source_convention_translation():
    """T3: Verify translation between Convention M (Jacobian) and Convention F (Fluid Mechanics).
    In Convention F: grad_F f = (grad_M f)^T.
    Formula in JFM: D = (grad_F X)^T = (grad_F A)^{-T}.
    Prove that (grad_F X)^T == F_M and (grad_F A)^{-T} == B_M^{-1} == F_M.
    """
    # Random non-symmetric SL(3, R) matrix
    np.random.seed(777)
    M = np.random.randn(3, 3)
    F_M = M / np.cbrt(np.linalg.det(M))
    B_M = np.linalg.inv(F_M)
    
    # Convention F gradients:
    G_X = F_M.T
    G_A = B_M.T
    
    # JFM Forward formula: D_JFM_forward = G_X^T
    D_JFM_forward = G_X.T
    assert np.allclose(D_JFM_forward, F_M)
    
    # JFM Backward formula: D_JFM_backward = (G_A)^{-T}
    D_JFM_backward = np.linalg.inv(G_A).T
    assert np.allclose(D_JFM_backward, F_M)
    assert np.allclose(D_JFM_backward, np.linalg.inv(B_M))


def test_t4_componentwise_curl_pullback_general_det():
    """T4: Componentwise curl pullback identity with general det B != 1:
    [curl_x (B^T (v o A))]_i = (det B) [B^{-1}]_{ik} [curl_a v]_k(A(x))
    """
    x1, x2, x3 = sp.symbols('x1 x2 x3', real=True)
    x = sp.Matrix([x1, x2, x3])
    
    # Quadratic non-volume-preserving map
    A1 = sp.Rational(3,2)*x1 + sp.Rational(1,3)*x2**2 - sp.Rational(1,4)*x3
    A2 = sp.Rational(4,3)*x2 + sp.Rational(1,5)*x1*x3
    A3 = sp.Rational(5,4)*x3 + sp.Rational(1,2)*x1**2 - sp.Rational(1,3)*x2
    A = sp.Matrix([A1, A2, A3])
    
    # B = J_A under Convention M: B_{ij} = dA_i / dx_j
    B = A.jacobian(x)
    det_B = B.det()
    
    a1, a2, a3 = sp.symbols('a1 a2 a3', real=True)
    v1 = a2*a3 + sp.Rational(1,2)*a1**2
    v2 = sp.cos(a1) + a3**2
    v3 = a1*a2 - sp.Rational(2,3)*a3
    v = sp.Matrix([v1, v2, v3])
    
    # curl_a v in components: [curl v]_k = eps_{kmn} d v_n / d a_m
    curl_v_1 = sp.diff(v[2], a2) - sp.diff(v[1], a3)
    curl_v_2 = sp.diff(v[0], a3) - sp.diff(v[2], a1)
    curl_v_3 = sp.diff(v[1], a1) - sp.diff(v[0], a2)
    curl_v = sp.Matrix([curl_v_1, curl_v_2, curl_v_3])
    curl_v_at_A = curl_v.subs({a1: A1, a2: A2, a3: A3})
    
    # w = B^T (v o A) -> w_i = B_{ji} v_j(A(x)) = (dA_j / dx_i) v_j(A(x))
    w = B.T * v.subs({a1: A1, a2: A2, a3: A3})
    
    # [curl_x w]_i = eps_{ijk} d w_k / d x_j
    curl_w_1 = sp.diff(w[2], x2) - sp.diff(w[1], x3)
    curl_w_2 = sp.diff(w[0], x3) - sp.diff(w[2], x1)
    curl_w_3 = sp.diff(w[1], x1) - sp.diff(w[0], x2)
    curl_w = sp.Matrix([curl_w_1, curl_w_2, curl_w_3])
    
    # Expected vector: (det B) * B^{-1} * (curl_a v)(A)
    B_inv = B.inv()
    expected = det_B * B_inv * curl_v_at_A
    
    diff = sp.simplify(curl_w - expected)
    assert diff == sp.Matrix.zeros(3, 1)


def test_t5_mutation_testing_all_choices_killed():
    """T5: Deliberate mutation test ensuring that in Convention M,
    mutating D = B^{-1} to D^T, D^{-1} (= B), or D^{-T} (= B^T)
    produces nonzero error in vorticity vector transformation.
    """
    np.random.seed(888)
    for _ in range(10):
        # Generate non-symmetric SL(3, R) matrix
        M = np.random.randn(3, 3)
        F_M = M / np.cbrt(np.linalg.det(M))
        B_M = np.linalg.inv(F_M)
        
        # True Cauchy operator D_true = F_M = B_M^{-1}
        D_true = F_M
        
        w0 = np.random.randn(3)
        w_expected = D_true @ w0
        
        # Mutant 1: D -> D^T = F_M^T (transpose error)
        mut1_w = F_M.T @ w0
        assert not np.allclose(mut1_w, w_expected), "Mutant D^T was not killed!"
        
        # Mutant 2: D -> D^{-1} = B_M (inverse error)
        mut2_w = B_M @ w0
        assert not np.allclose(mut2_w, w_expected), "Mutant D^{-1} was not killed!"
        
        # Mutant 3: D -> D^{-T} = B_M^T (inverse-transpose error)
        mut3_w = B_M.T @ w0
        assert not np.allclose(mut3_w, w_expected), "Mutant D^{-T} was not killed!"
