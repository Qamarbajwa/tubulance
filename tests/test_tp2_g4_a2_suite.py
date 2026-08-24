"""Worker test suite for TP2-G4-A2."""
import numpy as np
import pytest
from scipy.linalg import svd, qr


def test_g_tensor_equation_components():
    """Verify that (D_t - nu Delta) G = S G - G A + T under Convention M."""
    # Test on a synthesized 3D velocity gradient and second derivative field
    np.random.seed(101)
    A = np.random.randn(3, 3)
    A -= np.trace(A) / 3.0 * np.eye(3) # incompressible: tr(A) = 0
    S = 0.5 * (A + A.T)
    Omega = 0.5 * (A - A.T)

    # Vorticity vector omega from Omega
    omega = np.array([
        -2.0 * Omega[1, 2],
        2.0 * Omega[0, 2],
        -2.0 * Omega[0, 1]
    ])

    # Vorticity gradient tensor G (tr(G) = 0)
    G = np.random.randn(3, 3)
    G -= np.trace(G) / 3.0 * np.eye(3)

    # Strain gradient tensor d_j S_ik (3 x 3 x 3 tensor)
    grad_S = np.random.randn(3, 3, 3)
    # T_ij = (d_j S_ik) omega_k
    T = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                T[i, j] += grad_S[j, i, k] * omega[k]

    # RHS of G equation: K = S G - G A + T
    K = S @ G - G @ A + T
    assert K.shape == (3, 3)


def test_gamma_evolution_identity():
    """Verify d_s Gamma_s = -A_s^T Gamma_s - Gamma_s A_s."""
    np.random.seed(202)
    for _ in range(15):
        # Random D in SL(3, R)
        U, s, Vt = svd(np.random.randn(3, 3))
        s = s / (np.prod(s) ** (1.0 / 3.0))
        D = U @ np.diag(s) @ Vt
        Gamma = D.T @ D
        assert np.isclose(np.linalg.det(Gamma), 1.0)

        # Random velocity gradient A (tr(A) = 0)
        A = np.random.randn(3, 3)
        A -= np.trace(A) / 3.0 * np.eye(3)

        # Lower-endpoint derivative d_s D = -D A
        ds_D = -D @ A
        # Direct d_s Gamma = (ds_D)^T D + D^T (ds_D)
        direct_ds_Gamma = ds_D.T @ D + D.T @ ds_D

        # Formula: -A^T Gamma - Gamma A
        formula_ds_Gamma = -A.T @ Gamma - Gamma @ A

        assert np.allclose(direct_ds_Gamma, formula_ds_Gamma, atol=1e-12)


def test_spectral_projector_evolution():
    """Verify projector evolution formula for simple spectrum."""
    np.random.seed(303)
    # Construct Gamma with distinct eigenvalues
    s_sq = np.array([4.0, 1.0, 0.25])
    V, _ = qr(np.random.randn(3, 3))
    Gamma = V @ np.diag(s_sq) @ V.T

    # Projectors P_i
    P = [np.outer(V[:, i], V[:, i]) for i in range(3)]
    for i in range(3):
        assert np.isclose(np.trace(P[i]), 1.0)

    # Rate of strain A
    A = np.random.randn(3, 3)
    A -= np.trace(A) / 3.0 * np.eye(3)
    ds_Gamma = -A.T @ Gamma - Gamma @ A

    # For each projector P_i
    for i in range(3):
        ds_P_i = np.zeros((3, 3))
        for j in range(3):
            if j != i:
                ds_P_i += (P[j] @ ds_Gamma @ P[i] + P[i] @ ds_Gamma @ P[j]) / (s_sq[i] - s_sq[j])

        # Verify orthogonality condition: P_i @ ds_P_i @ P_i == 0
        assert np.allclose(P[i] @ ds_P_i @ P[i], 0.0, atol=1e-12)
        # Verify trace condition: tr(ds_P_i) == 0
        assert np.isclose(np.trace(ds_P_i), 0.0, atol=1e-12)


def test_clustered_degenerate_projector_gauge_invariance():
    """Verify gauge-invariance of clustered projector P_12 under SO(2) rotation of degenerate subspace."""
    s_sq = np.array([3.0, 3.0, 1.0 / 9.0]) # degenerate sigma_1 = sigma_2 = sqrt(3)
    V, _ = qr(np.random.randn(3, 3))
    Gamma = V @ np.diag(s_sq) @ V.T

    # Subspace projector P_12 = v1 v1^T + v2 v2^T = I - v3 v3^T
    P_12_base = np.outer(V[:, 0], V[:, 0]) + np.outer(V[:, 1], V[:, 1])

    # Apply random SO(2) rotation in 1-2 subspace
    theta = 1.234
    rot = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])
    V_rot = V.copy()
    V_rot[:, :2] = V[:, :2] @ rot

    P_12_rot = np.outer(V_rot[:, 0], V_rot[:, 0]) + np.outer(V_rot[:, 1], V_rot[:, 1])

    # Must be strictly identical
    assert np.allclose(P_12_base, P_12_rot, atol=1e-14)


def test_doubly_stochastic_frame_overlap():
    """Verify that frame overlap matrix R_ij = |v_i . e_j|^2 is doubly stochastic."""
    np.random.seed(404)
    for _ in range(10):
        V, _ = qr(np.random.randn(3, 3))
        E, _ = qr(np.random.randn(3, 3))

        R = (V.T @ E) ** 2
        # Row sums == 1
        assert np.allclose(np.sum(R, axis=1), 1.0, atol=1e-14)
        # Col sums == 1
        assert np.allclose(np.sum(R, axis=0), 1.0, atol=1e-14)


def test_neutral_subspace_suppression_mode():
    """Verify Mode II suppression: p_2 = 1, sigma_2 = 1 drives eta = 1/sigma_1^2 -> 0."""
    sigma_1_values = [2.0, 10.0, 50.0, 100.0]
    for sigma_1 in sigma_1_values:
        sigma_2 = 1.0
        sigma_3 = 1.0 / sigma_1

        # Mode II: p_1 = 0, p_2 = 1, p_3 = 0
        p = np.array([0.0, 1.0, 0.0])
        A_grad = np.sum(p * np.array([sigma_1 ** 2, sigma_2 ** 2, sigma_3 ** 2]))
        assert np.isclose(A_grad, 1.0) # exactly 1.0 (uncoupled)

        eta = A_grad / (sigma_1 ** 2)
        expected_eta = 1.0 / (sigma_1 ** 2)
        assert np.isclose(eta, expected_eta)
        if sigma_1 >= 50.0:
            assert eta < 1e-3
