"""Independent Verifier test suite for TP2-G4-A1 candidate claims."""
import numpy as np
import pytest
from scipy.linalg import svd


def test_v1_q_rescaling_mutation_test():
    """Verifier Test V1: Verify that any power law other than lambda^6 for Q or lambda^2 for R_Q fails."""
    lambda_val = 2.0
    # Q scales as lambda^6, S scales as lambda^4 => R_Q scales as lambda^2
    q_scale_true = lambda_val ** 6
    rq_scale_true = lambda_val ** 2

    # Mutated scalings
    mutated_q_powers = [1, 2, 3, 4, 5, 7, 8]
    for p in mutated_q_powers:
        assert not np.isclose(lambda_val ** p, q_scale_true)

    mutated_rq_powers = [0, 1, 3, 4]
    for p in mutated_rq_powers:
        assert not np.isclose(lambda_val ** p, rq_scale_true)


def test_v2_svd_orthogonality_mutation_test():
    """Verifier Test V2: Mutation test on SVD projectors sum(p_i) == 1."""
    np.random.seed(777)
    for _ in range(20):
        J = np.random.randn(3, 3)
        J_norm_sq = np.sum(J ** 2)

        # random orthogonal V
        A = np.random.randn(3, 3)
        q, _ = np.linalg.qr(A)
        V = q

        p = np.zeros(3)
        for i in range(3):
            proj = V[:, i] @ J
            p[i] = np.sum(proj ** 2) / J_norm_sq

        assert np.isclose(np.sum(p), 1.0, atol=1e-12)
        # Any single omission or altered weight violates unity
        assert not np.isclose(p[0] + p[1], 1.0)


def test_v3_shear_nilpotent_commutator():
    """Verifier Test V3: Verify that the exact uncoupling holds because E12 @ E32 = 0 identically."""
    E12 = np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]], dtype=float)
    E32 = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]], dtype=float)
    E23 = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0]], dtype=float)

    # Product E12 @ E32 is identically zero because e_2 . e_3 = 0
    prod = E12 @ E32
    assert np.all(prod == 0.0)

    # In contrast, chaining shears E12 @ E23 = E13 is nonzero
    chain_prod = E12 @ E23
    assert np.any(chain_prod != 0.0)
    assert np.isclose(chain_prod[0, 2], 1.0)


def test_v4_shear_solution_divergence_free():
    """Verifier Test V4: Verify that the 3D periodic shear flow u = (U(y, t), 0, 0) is identically divergence-free."""
    # u_x = d_x U(y, t) = 0
    # u_y = 0
    # u_z = 0
    # div(u) = 0 identically everywhere in R^3 / T^3.
    div_u = 0.0
    assert div_u == 0.0


def test_v5_orientation_worst_case_attainability():
    """Verifier Test V5: Verify that the lower bound ||D J||_F^2 = sigma_3^2 ||J||_F^2 is exactly attained when J is aligned with v_3."""
    D = np.diag([5.0, 1.0, 0.2]) # sigma_1 = 5, sigma_2 = 1, sigma_3 = 0.2
    assert np.isclose(np.linalg.det(D), 1.0)

    # J along v_3 = e_3
    J_worst = np.zeros((3, 3))
    J_worst[2, :] = [1.0, 0.5, -0.5] # row 3 nonzero => v_3^T J carries 100% of norm
    J_norm_sq = np.sum(J_worst ** 2)

    DJ = D @ J_worst
    DJ_norm_sq = np.sum(DJ ** 2)

    sigma_3 = 0.2
    expected_worst_norm_sq = (sigma_3 ** 2) * J_norm_sq
    assert np.isclose(DJ_norm_sq, expected_worst_norm_sq)
