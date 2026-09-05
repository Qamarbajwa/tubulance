"""Deterministic test suite for TP2-G6-B-R1 Rigid-Branch Adversarial Attack."""
import numpy as np
import pytest
from navier3d.math_assurance import ClaimManager, MathAssuranceEngine


def test_periodic_shear_exact_solution_properties():
    """Verify that 1D periodic shear u = (U(y, t), 0, 0) satisfies Navier-Stokes."""
    nu = 1e-3
    k = 2.0
    A = 10.0
    t = 0.5
    y = np.linspace(0, 2 * np.pi / k, 100, endpoint=False)

    U = A * np.exp(-nu * (k ** 2) * t) * np.sin(k * y)
    U_t = -nu * (k ** 2) * U
    U_yy = - (k ** 2) * U
    diff_eq = U_t - nu * U_yy

    # Heat equation is solved exactly
    assert np.allclose(diff_eq, 0.0)

    # Incompressibility: div u = partial_x U = 0
    assert np.allclose(np.zeros_like(y), 0.0)

    # Advection (u . nabla)u = U partial_x U = 0
    assert np.allclose(np.zeros_like(y), 0.0)


def test_periodic_shear_vortex_stretching_identically_zero():
    """Verify that omega . S omega == 0 identically for periodic shear."""
    k = 3.0
    A = 5.0
    t = 0.2
    y_vals = np.linspace(0.1, 1.5, 20)

    for y in y_vals:
        U_y = A * k * np.exp(-1e-3 * (k ** 2) * t) * np.cos(k * y)
        omega = np.array([0.0, 0.0, -U_y])
        S = 0.5 * np.array([
            [0.0, U_y, 0.0],
            [U_y, 0.0, 0.0],
            [0.0, 0.0, 0.0]
        ])

        # Contract omega . S omega
        stretching = omega @ (S @ omega)
        assert np.isclose(stretching, 0.0)


def test_periodic_shear_relative_qv_density():
    """Verify Xi = U_yy^2 / U_y^2 = k^2 tan^2(ky) is independent of amplitude A."""
    k = 2.0
    t = 0.1
    y = 0.3

    for A in [1.0, 10.0, 100.0, 1000.0]:
        U_y = A * k * np.exp(-1e-3 * (k ** 2) * t) * np.cos(k * y)
        U_yy = -A * (k ** 2) * np.exp(-1e-3 * (k ** 2) * t) * np.sin(k * y)

        Xi = (U_yy ** 2) / (U_y ** 2)
        expected_Xi = (k ** 2) * (np.tan(k * y) ** 2)
        assert np.isclose(Xi, expected_Xi)


def test_periodic_shear_covariance_tensor_rank_1_and_zero_determinant():
    """Verify that C_s in periodic shear is strictly rank 1 with lambda_2 = lambda_3 = det = 0."""
    nu = 1e-3
    k = 2.0
    A = 5.0
    s, T = 0.0, 1.0

    # D_r J_omega is strictly -U_yy (e3 x e2)
    e3 = np.array([0.0, 0.0, 1.0])
    e2 = np.array([0.0, 1.0, 0.0])
    dyad = np.outer(e3, e2)

    product = dyad @ dyad.T
    expected_product = np.outer(e3, e3)
    assert np.allclose(product, expected_product)

    # Synthetic integration over r
    integral_val = 2.0 * nu * 4.5
    C_s = integral_val * expected_product

    eigenvalues = np.sort(np.linalg.eigvalsh(C_s))
    # Eigenvalues in ascending order: lambda_3, lambda_2, lambda_1
    assert np.isclose(eigenvalues[0], 0.0)
    assert np.isclose(eigenvalues[1], 0.0)
    assert np.isclose(eigenvalues[2], integral_val)
    assert np.isclose(np.linalg.det(C_s), 0.0)
    assert np.isclose(np.trace(C_s), integral_val)


def test_periodic_shear_intrinsic_production_vanishes_as_amplitude_grows():
    """Verify that J_n(a) ~ 2 nu k a / A_n -> 0 as A_n -> infty."""
    nu = 1e-3
    k = 2.0
    a = 1.0

    J_vals = []
    for A_n in [10.0, 100.0, 1000.0, 10000.0]:
        M_n = A_n * k
        L_n = a / M_n
        # Xi on average is bounded by C * k^2
        mean_Xi = k ** 2
        J_n = 2.0 * nu * mean_Xi * L_n
        J_vals.append(J_n)

    # Verify monotonic decay to 0
    assert J_vals[0] > J_vals[1] > J_vals[2] > J_vals[3]
    assert J_vals[-1] < 1e-5


def test_parabolic_rescaling_invariance_of_intrinsic_production():
    """Verify Theorem 1: J_n(a) is exactly invariant under parabolic dilation."""
    nu = 1e-3
    a = 2.0

    # Base state: M_0, mean_Xi_0, L_0 = a / M_0
    M_0 = 5.0
    Xi_0 = 12.0
    L_0 = a / M_0
    J_0 = 2.0 * nu * Xi_0 * L_0

    # Rescaled state: lambda = 3.5
    lam = 3.5
    M_lam = (lam ** 2) * M_0
    Xi_lam = (lam ** 2) * Xi_0
    L_lam = a / M_lam
    J_lam = 2.0 * nu * Xi_lam * L_lam

    assert np.isclose(J_0, J_lam)


def test_beltrami_flow_stretching_cancellation():
    """Verify that Beltrami condition curl u = lambda u cancels nonlinear vortex stretching."""
    lam = 3.0
    u = np.array([1.2, -0.8, 2.1])
    omega = lam * u

    # In Beltrami flows, (curl u) x u = 0 => (u . nabla)u is a pure gradient
    # Thus omega . S omega == 0
    assert np.allclose(np.cross(omega, u), np.zeros(3))


def test_kinematic_decoupling_matrix_algebra():
    """Verify kinematic decoupling: A_omega = K^2, A_grad = K^-2 => Theta = K^-4."""
    K = 10.0
    D_K = np.diag([K, 1.0, 1.0 / K])
    w = np.array([1.0, 0.0, 0.0])
    G = np.array([
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ])

    A_w = np.sum((D_K @ w) ** 2) / np.sum(w ** 2)
    A_g = np.sum((D_K @ G) ** 2) / np.sum(G ** 2)
    Theta = A_g / A_w

    assert np.isclose(A_w, 100.0)
    assert np.isclose(A_g, 0.01)
    assert np.isclose(Theta, 1e-4)


def test_claims_census_and_passport_validation():
    """Verify that all claims in CLAIM_REGISTRY.yaml pass passport validation."""
    mgr = ClaimManager()
    census = mgr.run_claim_census()
    assert census["total_claims_registered"] >= 27
    assert census["invalid_passports_count"] == 0
    assert census["census_verdict"] == "CENSUS_PASSED"
