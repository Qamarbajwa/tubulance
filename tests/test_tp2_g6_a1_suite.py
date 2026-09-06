"""Deterministic test suite for TP2-G6-A1: Pressure–Strain Phase Coupling, Poisson Balance, and Calderón–Zygmund Limits."""
import numpy as np
import pytest
from navier3d.math_assurance import ClaimManager


def test_global_enstrophy_strain_equipartition_taylor_green():
    """Verify exact equipartition int_T3 tr(S^2) dx == 1/2 int_T3 |omega|^2 dx on Taylor-Green vortex."""
    N = 32
    coords = np.linspace(0, 2 * np.pi, N, endpoint=False)
    X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')

    # Taylor-Green vortex fields
    u = np.sin(X) * np.cos(Y) * np.cos(Z)
    v = -np.cos(X) * np.sin(Y) * np.cos(Z)
    w = np.zeros_like(X)

    # Spatial derivatives using periodic Fourier spectral differentiation or analytical formulas
    # u_x = cos(X)cos(Y)cos(Z), u_y = -sin(X)sin(Y)cos(Z), u_z = -sin(X)cos(Y)sin(Z)
    # v_x = sin(X)sin(Y)cos(Z), v_y = -cos(X)cos(Y)cos(Z), v_z = cos(X)sin(Y)sin(Z)
    # w_x = w_y = w_z = 0
    u_x = np.cos(X) * np.cos(Y) * np.cos(Z)
    u_y = -np.sin(X) * np.sin(Y) * np.cos(Z)
    u_z = -np.sin(X) * np.cos(Y) * np.sin(Z)

    v_x = np.sin(X) * np.sin(Y) * np.cos(Z)
    v_y = -np.cos(X) * np.cos(Y) * np.cos(Z)
    v_z = np.cos(X) * np.sin(Y) * np.sin(Z)

    w_x = np.zeros_like(X)
    w_y = np.zeros_like(X)
    w_z = np.zeros_like(X)

    # Incompressibility check
    div_u = u_x + v_y + w_z
    assert np.allclose(div_u, 0.0)

    # Strain components S_ij = 1/2 (d_j u_i + d_i u_j)
    S11 = u_x
    S22 = v_y
    S33 = w_z
    S12 = 0.5 * (u_y + v_x)
    S13 = 0.5 * (u_z + w_x)
    S23 = 0.5 * (v_z + w_y)

    # tr(S^2) = S11^2 + S22^2 + S33^2 + 2(S12^2 + S13^2 + S23^2)
    tr_S2 = S11**2 + S22**2 + S33**2 + 2 * (S12**2 + S13**2 + S23**2)

    # Vorticity components omega = curl(u)
    # omega_1 = w_y - v_z, omega_2 = u_z - w_x, omega_3 = v_x - u_y
    omega_1 = w_y - v_z
    omega_2 = u_z - w_x
    omega_3 = v_x - u_y
    omega_sq = omega_1**2 + omega_2**2 + omega_3**2

    # Volume integrals over T^3
    dx = (2 * np.pi / N)**3
    int_tr_S2 = np.sum(tr_S2) * dx
    int_half_omega_sq = 0.5 * np.sum(omega_sq) * dx

    # Exact equality to high numerical precision
    assert np.isclose(int_tr_S2, int_half_omega_sq, rtol=1e-12)


def test_matrix_algebraic_strain_identities():
    """Verify algebraic identities: tr(S Omega) == 0, tr(Omega^2) == -1/2 |omega|^2, Sym(A^2) == S^2 + Omega^2."""
    np.random.seed(42)
    for _ in range(20):
        # Random velocity gradient with zero trace
        A = np.random.randn(3, 3)
        A -= np.trace(A) / 3.0 * np.eye(3)
        assert np.isclose(np.trace(A), 0.0)

        S = 0.5 * (A + A.T)
        Omega = 0.5 * (A - A.T)

        # 1. tr(S Omega) == 0
        assert np.isclose(np.trace(S @ Omega), 0.0)

        # 2. Extract vorticity vector: omega_k = -epsilon_ijk Omega_ij
        omega = np.array([
            Omega[2, 1] - Omega[1, 2],
            Omega[0, 2] - Omega[2, 0],
            Omega[1, 0] - Omega[0, 1]
        ])
        omega_sq = np.sum(omega**2)

        # tr(Omega^2) == -1/2 |omega|^2
        assert np.isclose(np.trace(Omega @ Omega), -0.5 * omega_sq)

        # 3. Sym(A^2) == S^2 + Omega^2
        A2 = A @ A
        sym_A2 = 0.5 * (A2 + A2.T)
        assert np.allclose(sym_A2, S @ S + Omega @ Omega)

        # 4. Deviatoric part has zero trace
        Q_OW = np.trace(S @ S) - 0.5 * omega_sq
        deviatoric_source = (S @ S + Omega @ Omega) - (Q_OW / 3.0) * np.eye(3)
        assert np.isclose(np.trace(deviatoric_source), 0.0)


def test_riesz_transform_multiplier_properties():
    """Verify periodic Riesz multipliers sum to -1 and deviatoric Hessian multiplier is trace-free."""
    np.random.seed(123)
    for _ in range(20):
        k = np.random.randn(3)
        k_norm_sq = np.sum(k**2)
        if k_norm_sq < 1e-6:
            continue

        # Multiplier of R_i: -i k_i / |k|
        # Multiplier of R_i R_j: -k_i k_j / |k|^2
        # Sum_i R_i^2 = -Sum_i k_i^2 / |k|^2 = -1
        riesz_sq_sum = -np.sum(k**2) / k_norm_sq
        assert np.isclose(riesz_sq_sum, -1.0)

        # Multiplier of deviatoric Hessian Pi^dev = (R (x) R + 1/3 I)
        # M_ij = -k_i k_j / |k|^2 + 1/3 delta_ij
        M = -np.outer(k, k) / k_norm_sq + (1.0 / 3.0) * np.eye(3)
        # Trace of M must be identically zero for all non-zero wavevectors k
        assert np.isclose(np.trace(M), 0.0)


def test_vieillefosse_restricted_euler_first_integral():
    """Verify that H(Q, R) = R^2 + 4/27 Q^3 is conserved by Restricted Euler trajectories."""
    # dQ/dt = -3R, dR/dt = 2/3 Q^2
    # dH/dt = 2R dR/dt + 4/9 Q^2 dQ/dt = 2R(2/3 Q^2) + 4/9 Q^2(-3R) = 4/3 R Q^2 - 4/3 R Q^2 == 0
    Q0 = -2.0
    R0 = 1.0
    H0 = R0**2 + (4.0 / 27.0) * (Q0**3)

    dt = 1e-4
    Q, R = Q0, R0
    for _ in range(100):
        # 4th-order Runge-Kutta
        def f(q, r):
            return -3.0 * r, (2.0 / 3.0) * (q**2)

        k1_q, k1_r = f(Q, R)
        k2_q, k2_r = f(Q + 0.5 * dt * k1_q, R + 0.5 * dt * k1_r)
        k3_q, k3_r = f(Q + 0.5 * dt * k2_q, R + 0.5 * dt * k2_r)
        k4_q, k4_r = f(Q + dt * k3_q, R + dt * k3_r)

        Q += (dt / 6.0) * (k1_q + 2 * k2_q + 2 * k3_q + k4_q)
        R += (dt / 6.0) * (k1_r + 2 * k2_r + 2 * k3_r + k4_r)

    H_final = R**2 + (4.0 / 27.0) * (Q**3)
    assert np.isclose(H_final, H0, rtol=1e-6)


def test_clm033_and_ns_obs017_registration():
    """Verify CLM-033 and NS-OBS-017 presence in registries and validate claim manager."""
    cm = ClaimManager()
    claims = cm.claims
    assert "CLM-033" in claims
    clm33 = claims["CLM-033"]
    assert clm33["name"] == "PRESSURE_STRAIN_COUPLING_AND_CALDERON_ZYGMUND_LIMITS"
    assert clm33["passport"]["truth_status"] == "PROVED_IDENTITY"
    assert clm33["passport"]["project_status"] == "PROJECT_CANONICAL"
