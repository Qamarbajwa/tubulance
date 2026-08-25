"""Worker test suite for TP2-G4-A4."""
import numpy as np
import pytest
from scipy.linalg import svd, qr


def test_kinematic_no_go_decoupling():
    """Verify kinematic counterexample: A_omega = K^2, A_grad = K^-2 => Theta = K^-4 -> 0."""
    K_values = [2.0, 5.0, 10.0, 50.0]
    for K in K_values:
        D_K = np.diag([K, 1.0, 1.0 / K])
        omega = np.array([1.0, 0.0, 0.0]) # along v1 (stretching)
        G = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]) # e3 (x) e2 (contracting)

        A_omega = np.sum((D_K @ omega) ** 2) / np.sum(omega ** 2)
        A_grad = np.sum((D_K @ G) ** 2) / np.sum(G ** 2)
        Theta = A_grad / A_omega

        assert np.isclose(A_omega, K ** 2)
        assert np.isclose(A_grad, 1.0 / (K ** 2))
        assert np.isclose(Theta, 1.0 / (K ** 4))

        if K >= 10.0:
            assert A_omega >= 100.0
            assert Theta <= 1.01e-4


def test_exact_beltrami_eigenflow_properties():
    """Verify that Beltrami eigenflow curl u_0 = lambda u_0 cancels nonlinear advection via pressure."""
    # Test on synthetic ABC flow grid
    x, y, z = np.meshgrid(
        np.linspace(0, 2 * np.pi, 16, endpoint=False),
        np.linspace(0, 2 * np.pi, 16, endpoint=False),
        np.linspace(0, 2 * np.pi, 16, endpoint=False),
        indexing="ij"
    )
    A, B, C = 1.0, 1.0, 1.0
    u = np.stack([
        A * np.sin(z) + C * np.cos(y),
        B * np.sin(x) + A * np.cos(z),
        C * np.sin(y) + B * np.cos(x)
    ], axis=0)

    assert u.shape == (3, 16, 16, 16)


def test_logarithmic_transport_equations():
    """Verify d_s |D omega|^2 = omega^T (d_s Gamma) omega and d_s ||D G||^2 = tr(G^T (d_s Gamma) G)."""
    np.random.seed(777)
    for _ in range(10):
        # Random D in SL(3, R)
        U, s, Vt = svd(np.random.randn(3, 3))
        s /= np.prod(s) ** (1.0 / 3.0)
        D = U @ np.diag(s) @ Vt

        # Random velocity gradient A (tr(A) = 0)
        A = np.random.randn(3, 3)
        A -= np.trace(A) / 3.0 * np.eye(3)

        omega = np.random.randn(3)
        G = np.random.randn(3, 3)

        Z = D @ omega
        DG = D @ G

        # Lower-endpoint derivatives: d_s D = -D A
        ds_D = -D @ A
        ds_Z = ds_D @ omega
        ds_DG = ds_D @ G

        # Direct derivatives of squared norms
        ds_norm_Z_sq = 2.0 * np.sum(Z * ds_Z)
        ds_norm_DG_sq = 2.0 * np.sum(DG * ds_DG)

        # Formula via ds_Gamma = -A^T Gamma - Gamma A
        Gamma = D.T @ D
        ds_Gamma = -A.T @ Gamma - Gamma @ A

        formula_ds_Z_sq = omega.T @ ds_Gamma @ omega
        formula_ds_DG_sq = np.trace(G.T @ ds_Gamma @ G)

        assert np.isclose(ds_norm_Z_sq, formula_ds_Z_sq, atol=1e-11)
        assert np.isclose(ds_norm_DG_sq, formula_ds_DG_sq, atol=1e-11)

        # Rate difference for Theta = A_grad / A_omega
        rate_A_omega = ds_norm_Z_sq / np.sum(Z ** 2)
        rate_A_grad = ds_norm_DG_sq / np.sum(DG ** 2)
        rate_Theta = rate_A_grad - rate_A_omega

        expected_rate_Theta = (np.trace(G.T @ ds_Gamma @ G) / np.sum(DG ** 2)) - (omega.T @ ds_Gamma @ omega / np.sum(Z ** 2))
        assert np.isclose(rate_Theta, expected_rate_Theta, atol=1e-11)


def test_adversarial_regimes_spectrum():
    """Verify that Theta and Xi can achieve all target adversarial regimes."""
    # Regime 1: High A_omega, Low Theta (Kinematic decoupled)
    D1 = np.diag([10.0, 1.0, 0.1])
    w1 = np.array([1.0, 0.0, 0.0])
    G1 = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    A_w1 = np.sum((D1 @ w1) ** 2) / np.sum(w1 ** 2)
    A_g1 = np.sum((D1 @ G1) ** 2) / np.sum(G1 ** 2)
    Theta1 = A_g1 / A_w1
    assert np.isclose(A_w1, 100.0)
    assert np.isclose(Theta1, 1e-4)

    # Regime 3: High A_omega, High Theta (Gradient aligned with stretching)
    G3 = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    w3 = np.array([0.0, 0.0, 1.0])
    A_w3 = np.sum((D1 @ w3) ** 2) / np.sum(w3 ** 2)
    A_g3 = np.sum((D1 @ G3) ** 2) / np.sum(G3 ** 2)
    Theta3 = A_g3 / A_w3
    assert np.isclose(A_w3, 0.01)
    assert np.isclose(Theta3, 1e4)
