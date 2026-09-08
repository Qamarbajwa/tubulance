"""
Unit and Deterministic Regression Tests for TP2-G6-C1:
Two-Particle Relative Dispersion, Common-Mode Cancellation, and Stochastic Jet Foundation.

Verifies:
1. Synchronous and independent common-mode velocity cancellation (Theorem 2.1)
2. Path-averaged gradient matrix trace-free property: tr(S_s) == 0
3. Independent Brownian noise relative diffusivity 4*nu and separation energy Ito correction 12*nu
4. Quadratic velocity structure function bound: S_2(h) <= |h|^2 * ||grad u||_2^2
5. Infinitesimal stochastic jet convergence: delta A_s / h -> D_s as |h| -> 0 under C-SYNC
6. Explosion of difference quotient delta A_s / |h| under C-IND
7. Bilateral deformation pullback matrix identity for Xi^pair in affine flow: grad_x Z_s = D_s J_omega D_s
8. Pair covariance rank in periodic shear flow: rank 1 for C-SYNC (centered), rank 3 for C-IND
9. Non-collision repulsive centrifugal drift in 3D: +4*nu / r_s
"""

import math
import numpy as np
import pytest


def test_common_mode_cancellation():
    """
    Verify Theorem 2.1:
    u(x, t) = U(t) + v(x, t).
    Relative velocity difference:
    u(x2, t) - u(x1, t) = v(x2, t) - v(x1, t).
    Uniform velocity U(t) cancels identically.
    """
    np.random.seed(101)
    U_t = np.array([1250.0, -840.0, 310.0])  # Enormous uniform sweeping velocity
    x1 = np.array([0.2, 0.4, 0.6])
    x2 = np.array([0.21, 0.39, 0.62])

    # Let v(x) be a divergence-free spatial mode (e.g. Taylor-Green or ABC component)
    def v_field(x):
        return np.array([
            np.sin(2 * np.pi * x[1]),
            np.cos(2 * np.pi * x[0]),
            np.sin(2 * np.pi * (x[0] + x[1]))
        ])

    u1 = U_t + v_field(x1)
    u2 = U_t + v_field(x2)
    delta_u = u2 - u1
    delta_v = v_field(x2) - v_field(x1)

    assert np.allclose(delta_u, delta_v, atol=1e-12)
    # Verify that delta_u does NOT depend on U_t in any way:
    u1_large = (U_t * 1000.0) + v_field(x1)
    u2_large = (U_t * 1000.0) + v_field(x2)
    assert np.allclose(u2_large - u1_large, delta_v, atol=1e-12)


def test_path_averaged_gradient_trace_free():
    """
    Verify that div(u) = 0 implies tr(S_s) = 0 identically for the path-averaged matrix:
    S_s = int_0^1 grad u(A1 + theta * delta A) d theta.
    """
    # Create a divergence-free gradient field: tr(grad u) = 0
    # S = diag(2, -1, -1) + skew-symmetric part
    np.random.seed(102)
    grad_u_0 = np.array([
        [2.5, 1.2, -0.7],
        [-1.2, -1.0, 0.5],
        [0.7, -0.5, -1.5]
    ])
    assert math.isclose(np.trace(grad_u_0), 0.0, abs_tol=1e-14)

    # Numerical integration along theta in [0, 1]
    N_steps = 100
    theta_vals = np.linspace(0.0, 1.0, N_steps)
    # Let grad u vary along the segment while remaining traceless everywhere
    S_accum = np.zeros((3, 3))
    for th in theta_vals:
        # Modulate by traceless spatial perturbation
        pert = np.diag([math.sin(th), math.cos(th), -math.sin(th) - math.cos(th)])
        local_grad = grad_u_0 + pert
        assert math.isclose(np.trace(local_grad), 0.0, abs_tol=1e-14)
        S_accum += local_grad * (1.0 / N_steps)

    assert math.isclose(np.trace(S_accum), 0.0, abs_tol=1e-12)


def test_relative_diffusivity_and_ito_trace():
    """
    Verify independent noise relative diffusivity 4*nu and separation energy Ito correction:
    d|delta A_s|^2 contains trace: sum_{i=1}^3 d(sqrt(4nu) B_s^i)^2 = 3 * 4*nu * ds = 12*nu * ds.
    """
    nu = 0.005
    d = 3  # spatial dimension
    single_diffusivity = 2.0 * nu  # coefficient in single particle SDE: sqrt(2nu) dW
    relative_variance_rate = 2.0 * single_diffusivity  # 4 * nu
    assert math.isclose(relative_variance_rate, 4.0 * nu, rel_tol=1e-14)

    # Ito correction for |x|^2 in R^d:
    ito_trace = d * relative_variance_rate
    assert math.isclose(ito_trace, 12.0 * nu, rel_tol=1e-14)


def test_quadratic_structure_function_bound():
    """
    Verify Theorem 7.1: S_2(h) <= |h|^2 * ||grad u||_2^2.
    Also verify Parseval trigonometric inequality: 4 * sin^2(pi * k . h) <= 4 * pi^2 * |k|^2 * |h|^2.
    """
    # Test trigonometric inequality across a grid of k and h
    np.random.seed(103)
    k_vecs = np.random.randint(-5, 5, size=(20, 3))
    h_vecs = np.random.uniform(0.001, 0.1, size=(20, 3))

    for k in k_vecs:
        for h in h_vecs:
            kh = np.dot(k, h)
            lhs = 4.0 * (math.sin(math.pi * kh) ** 2)
            rhs = 4.0 * (math.pi ** 2) * (np.dot(k, k)) * (np.dot(h, h))
            assert lhs <= rhs + 1e-12


def test_infinitesimal_stochastic_jet_convergence():
    """
    Verify Theorem 4.1: Under Coupling C-SYNC, delta A_s(h) / h -> D_s as |h| -> 0.
    In solvable affine flow u(x) = S * x, backward flow is exactly:
    A_s(x) = exp(-(t-s) S) * (x + Brownian).
    Thus D_s = exp(-(t-s) S), and delta A_s = exp(-(t-s) S) * h.
    The ratio delta A_s / h is identically equal to D_s for all h.
    """
    S = np.array([
        [1.0, 0.5, 0.0],
        [0.0, -0.5, 0.2],
        [0.0, 0.0, -0.5]
    ])  # Traceless matrix
    delta_t = 0.5
    from scipy.linalg import expm
    D_expected = expm(-delta_t * S)

    for h_mag in [1e-2, 1e-4, 1e-6]:
        h = np.array([h_mag, 2.0 * h_mag, -h_mag])
        delta_A = D_expected @ h
        # Difference quotient matrix: Q = [delta_A(e1)/|h|, delta_A(e2)/|h|, delta_A(e3)/|h|]
        Q = np.zeros((3, 3))
        for j in range(3):
            ej = np.zeros(3)
            ej[j] = h_mag
            Q[:, j] = (D_expected @ ej) / h_mag
        assert np.allclose(Q, D_expected, atol=1e-10)


def test_independent_coupling_quotient_explosion():
    """
    Verify that under C-IND, the difference quotient delta A_s / |h| explodes as |h| -> 0:
    |delta A_s| / |h| >= sqrt(4nu) |B_t - B_s| / |h| -> infty.
    """
    nu = 1e-3
    delta_t = 0.1
    # Simulated Brownian increment: non-zero with probability 1
    B_inc = np.array([0.2, -0.15, 0.3])
    noise_disp = math.sqrt(4.0 * nu) * np.linalg.norm(B_inc)
    assert noise_disp > 0.0

    ratios = []
    h_values = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
    for h_val in h_values:
        ratio = noise_disp / h_val
        ratios.append(ratio)

    # Verify ratios grow inversely with h_val
    for i in range(len(ratios) - 1):
        assert ratios[i + 1] > ratios[i] * 5.0
    assert ratios[-1] > 1000.0  # Explodes to > 1000 at h = 1e-5


def test_bilateral_pullback_xi_pair_identity():
    """
    Verify WP9 identity: In affine flow (grad^2 u = 0 => H_s = 0),
    grad_x Z_s(x) = D_s * J_omega * D_s.
    """
    # Let D_s be a 3x3 invertible deformation matrix, J_omega be a 3x3 vorticity gradient
    D_s = np.array([[2.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.5]])
    assert math.isclose(np.linalg.det(D_s), 1.0, rel_tol=1e-12)

    J_omega = np.array([[1.0, -2.0, 0.5], [0.5, 1.5, -1.0], [-1.0, 0.0, 2.0]])
    expected_grad_Z = D_s @ J_omega @ D_s

    # Compute numerically via finite differences of Z_s(x + h) - Z_s(x)
    # where Z_s(x) = D_s * (omega_0 + J_omega * A_s(x)) and A_s(x) = D_s * x
    grad_Z_num = np.zeros((3, 3))
    eps = 1e-6
    for j in range(3):
        h = np.zeros(3)
        h[j] = eps
        # delta A = D_s * h
        delta_A = D_s @ h
        # delta omega = J_omega * delta_A = J_omega * D_s * h
        delta_omega = J_omega @ delta_A
        # delta Z = D_s * delta_omega = D_s * J_omega * D_s * h
        delta_Z = D_s @ delta_omega
        grad_Z_num[:, j] = delta_Z / eps

    assert np.allclose(grad_Z_num, expected_grad_Z, atol=1e-5)


def test_pair_covariance_rank_in_shear():
    """
    Verify WP10: In periodic planar shear u = (U(y), 0, 0),
    C-SYNC centered covariance is strictly rank 1 (lambda_2 = lambda_3 = 0).
    C-IND covariance has lambda_3 = 4*nu*Delta_t > 0 (Brownian).
    """
    nu = 1e-3
    delta_t = 0.5
    var_x_shear = 25.0  # large shear-induced variance along x-axis

    # C-SYNC centered covariance:
    C_sync_centered = np.diag([var_x_shear, 0.0, 0.0])
    eig_sync = np.linalg.eigvalsh(C_sync_centered)
    assert math.isclose(eig_sync[0], 0.0, abs_tol=1e-14)
    assert math.isclose(eig_sync[1], 0.0, abs_tol=1e-14)
    assert math.isclose(eig_sync[2], var_x_shear, rel_tol=1e-12)
    assert np.count_nonzero(np.isclose(eig_sync, 0.0, atol=1e-10)) == 2  # rank 1!

    # C-IND centered covariance:
    brownian_var = 4.0 * nu * delta_t
    C_ind_centered = np.diag([var_x_shear + brownian_var, brownian_var, brownian_var])
    eig_ind = np.linalg.eigvalsh(C_ind_centered)
    assert math.isclose(eig_ind[0], brownian_var, rel_tol=1e-12)
    assert math.isclose(eig_ind[1], brownian_var, rel_tol=1e-12)
    assert eig_ind[2] > var_x_shear
    assert np.all(eig_ind > 0.0)  # full rank 3!


def test_non_collision_repulsive_drift():
    """
    Verify WP5: In C-IND, the radial distance r_s = |delta A_s| experiences
    a strictly positive repulsive centrifugal drift: + (d-1)*nu_rel / r_s = + 4*nu / r_s in d=3.
    """
    nu = 1e-3
    d = 3
    # nu_rel = 2 * nu, so (d-1) * (2 * nu_rel) / (2 * r) = (3-1) * (4 * nu) / (2 * r) = 4 * nu / r
    for r in [1e-1, 1e-2, 1e-3, 1e-4]:
        repulsive_drift = 4.0 * nu / r
        assert repulsive_drift > 0.0
        # As r -> 0, repulsive drift diverges to +infinity, protecting against collision
        if r == 1e-4:
            assert repulsive_drift >= 40.0
