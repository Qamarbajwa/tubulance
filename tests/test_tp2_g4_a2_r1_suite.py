"""Automated test suite for TP2-G4-A2-R1 correction gate."""
import numpy as np
import pytest
from scipy.linalg import svd, qr


def test_spectral_cluster_resolvent_gap():
    """Verify Riesz projector for isolated 2D cluster and gap condition."""
    # Isolated 2D cluster: mu_1 = 4.0, mu_2 = 3.9, mu_3 = 0.5 (spectral gap = 3.4)
    mu = np.array([4.0, 3.9, 0.5])
    V, _ = qr(np.random.randn(3, 3))
    Gamma = V @ np.diag(mu) @ V.T

    # Cluster projector P_12 = v1 v1^T + v2 v2^T
    P_12 = np.outer(V[:, 0], V[:, 0]) + np.outer(V[:, 1], V[:, 1])
    assert np.isclose(np.trace(P_12), 2.0)

    # Resolvent contour integral around cluster [3.5, 4.5] with circle radius 0.6 centered at 3.95
    z_center = 3.95
    radius = 0.6
    n_pts = 64
    angles = np.linspace(0, 2 * np.pi, n_pts, endpoint=False)
    dz = 1j * radius * np.exp(1j * angles) * (2 * np.pi / n_pts)
    z_vals = z_center + radius * np.exp(1j * angles)

    P_contour = np.zeros((3, 3), dtype=complex)
    for z, d_z in zip(z_vals, dz):
        resolvent = np.linalg.inv(z * np.eye(3) - Gamma)
        P_contour += resolvent * d_z / (2j * np.pi)

    assert np.allclose(P_contour.real, P_12, atol=1e-3)


def test_unnormalized_weights_globally_defined():
    """Verify q_i = tr(P_i H) >= 0 and sum(q_i) == h, including at G = 0."""
    # Nonzero G case
    G = np.random.randn(3, 3)
    H = G @ G.T
    h = np.trace(H)

    V, _ = qr(np.random.randn(3, 3))
    q = np.zeros(3)
    for i in range(3):
        P_i = np.outer(V[:, i], V[:, i])
        q[i] = np.trace(P_i @ H)
        assert q[i] >= 0.0

    assert np.isclose(np.sum(q), h)

    # Zero G case (h = 0)
    G_zero = np.zeros((3, 3))
    H_zero = G_zero @ G_zero.T
    h_zero = np.trace(H_zero)
    assert h_zero == 0.0

    q_zero = np.zeros(3)
    for i in range(3):
        P_i = np.outer(V[:, i], V[:, i])
        q_zero[i] = np.trace(P_i @ H_zero)
        assert q_zero[i] == 0.0

    assert np.sum(q_zero) == 0.0
    # At h = 0, p_i = q_i / h is 0/0 (undefined), but q_i and H are well-defined


def test_basis_invariant_eta_equivalence():
    """Verify eta = tr(Gamma H) / (lambda_max(Gamma) tr(H)) matches sum p_i (sigma_i/sigma_1)^2."""
    # Simple spectrum
    s = np.array([5.0, 2.0, 0.1])
    V, _ = qr(np.random.randn(3, 3))
    Gamma = V @ np.diag(s ** 2) @ V.T

    G = np.random.randn(3, 3)
    H = G @ G.T
    h = np.trace(H)

    # Basis-invariant formula
    lambda_max = np.max(s ** 2)
    eta_invariant = np.trace(Gamma @ H) / (lambda_max * h)

    # Component formula
    p = np.zeros(3)
    for i in range(3):
        p[i] = (V[:, i] @ H @ V[:, i]) / h

    eta_component = p[0] + p[1] * ((s[1] / s[0]) ** 2) + p[2] * ((s[2] / s[0]) ** 2)
    assert np.isclose(eta_invariant, eta_component)

    # Double degeneracy case (sigma_1 = sigma_2 = 4.0, sigma_3 = 1/16)
    s_deg = np.array([4.0, 4.0, 1.0 / 16.0])
    Gamma_deg = V @ np.diag(s_deg ** 2) @ V.T
    lambda_max_deg = 16.0

    eta_deg = np.trace(Gamma_deg @ H) / (lambda_max_deg * h)
    assert eta_deg > 0.0
    assert eta_deg <= 1.0


def test_backward_ito_sde_q_tensor_decomposition():
    """Verify the 3-component structure of d_hat q_i: rotation + dynamics + martingale noise."""
    P_i = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    dot_P_i = np.array([[0.0, 0.5, 0.0], [0.5, 0.0, 0.0], [0.0, 0.0, 0.0]])
    H = np.array([[2.0, 1.0, 0.0], [1.0, 3.0, 0.0], [0.0, 0.0, 1.0]])
    R_H = np.array([[0.5, 0.2, 0.0], [0.2, -0.3, 0.0], [0.0, 0.0, 0.1]])

    # Term 1: deformation rotation
    rot_term = np.trace(dot_P_i @ H)
    assert np.isclose(rot_term, 1.0) # 0.5*1 + 0.5*1

    # Term 2: dynamics
    dyn_term = np.trace(P_i @ R_H)
    assert np.isclose(dyn_term, 0.5)

    # Term 3: martingale noise (spatial derivative of H along 3 axes)
    nu = 1e-3
    grad_H = [np.random.randn(3, 3) for _ in range(3)]
    for g in grad_H:
        g += g.T # symmetric
    noise_amplitudes = [np.sqrt(2.0 * nu) * np.trace(P_i @ g) for g in grad_H]
    assert len(noise_amplitudes) == 3


def test_normalized_process_r_m_operator():
    """Verify trace-free property tr(R_M) == 0 for R_M = (R_H - M tr(R_H))/h + 2nu/h sum (d_l h)(d_l M)."""
    h = 4.5
    M = np.diag([0.6, 0.3, 0.1])
    assert np.isclose(np.trace(M), 1.0)

    R_H = np.array([[1.2, 0.4, 0.0], [0.4, -0.5, 0.1], [0.0, 0.1, 0.3]])
    tr_R_H = np.trace(R_H)

    # Part 1: (R_H - M tr(R_H)) / h
    part1 = (R_H - M * tr_R_H) / h
    assert np.isclose(np.trace(part1), 0.0)

    # Part 2: (2 nu / h) sum (d_l h)(d_l M) where tr(d_l M) = 0
    nu = 1e-3
    d_l_h = [0.2, -0.4, 0.1]
    d_l_M = []
    for _ in range(3):
        dM = np.random.randn(3, 3)
        dM -= np.trace(dM) / 3.0 * np.eye(3) # tr(dM) = 0 since tr(M) = 1
        d_l_M.append(dM)

    part2 = np.zeros((3, 3))
    for dl_h, dl_M in zip(d_l_h, d_l_M):
        part2 += (2.0 * nu / h) * dl_h * dl_M

    assert np.isclose(np.trace(part2), 0.0)

    R_M = part1 + part2
    assert np.isclose(np.trace(R_M), 0.0)


def test_persistence_definitions_consistency():
    """Verify occupation time and first exit time on a synthetic trajectory."""
    n_steps = 100
    tau_grid = np.linspace(0, 10.0, n_steps)
    dtau = tau_grid[1] - tau_grid[0]
    eps = 0.1

    # Synthetic eta trajectory starting low and exiting at tau = 3.0
    eta_traj = 0.05 + 0.02 * np.sin(tau_grid)
    eta_traj[tau_grid >= 3.0] += 0.5 # exit after tau = 3.0

    # Occupation time on [0, 10.0]
    in_low_set = (eta_traj <= eps)
    occupation_time = np.sum(in_low_set) * dtau
    assert occupation_time > 0.0
    assert occupation_time <= 10.0

    # First exit time
    exit_idx = np.where(eta_traj > eps)[0]
    assert len(exit_idx) > 0
    tau_exit = tau_grid[exit_idx[0]]
    assert np.isclose(tau_exit, 3.0, atol=0.2)
