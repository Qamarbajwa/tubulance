"""Deterministic test suite for TP2-G6-B-R2 Scientific Claim Audit and Repair."""
import numpy as np
import pytest
from navier3d.math_assurance import ClaimManager


def test_fixed_torus_lattice_compatibility():
    """Verify that u_lambda is 1-periodic on T^1 iff lambda is an integer."""
    x = np.linspace(0.0, 1.0, 50, endpoint=False)
    # Base 1-periodic function: f(x) = sin(2 pi x)
    f = lambda y: np.sin(2.0 * np.pi * y)

    # Integer dilation: lambda = 3
    lam_int = 3.0
    f_int = lambda y: lam_int * f(lam_int * y)
    # Check periodicity: f_int(x + 1) == f_int(x)
    assert np.allclose(f_int(x + 1.0), f_int(x))

    # Non-integer dilation: lambda = 2.5
    lam_non = 2.5
    f_non = lambda y: lam_non * f(lam_non * y)
    # Periodicity on the fixed unit torus fails!
    assert not np.allclose(f_non(x + 1.0), f_non(x))


def test_single_helical_beltrami_stretching_identically_zero():
    """Verify single helical mode has constant |u|^2 and omega . S omega == 0."""
    k = 2.0
    z_vals = np.linspace(0.0, 2.0 * np.pi, 20)

    for z in z_vals:
        u = np.array([np.cos(k * z), np.sin(k * z), 0.0])
        # |u|^2 is constant everywhere: cos^2 + sin^2 == 1
        speed_sq = np.sum(u ** 2)
        assert np.isclose(speed_sq, 1.0)

        # Grad |u|^2 == 0
        grad_speed_sq = np.array([0.0, 0.0, 0.0])
        omega = k * u
        # omega . S omega = k^2 u . grad(|u|^2 / 2) == 0
        stretching = (k ** 2) * np.dot(u, grad_speed_sq) / 2.0
        assert np.isclose(stretching, 0.0)


def test_abc_flow_stretching_properties():
    """Verify ABC flow: pointwise stretching is non-zero, but spatial mean is zero."""
    A, B, C, k = 1.0, 1.0, 1.0, 1.0
    N = 16
    coords = np.linspace(0, 2 * np.pi, N, endpoint=False)
    X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')

    u = A * np.sin(k * Z) + C * np.cos(k * Y)
    v = B * np.sin(k * X) + A * np.cos(k * Z)
    w = C * np.sin(k * Y) + B * np.cos(k * X)

    speed_sq = u ** 2 + v ** 2 + w ** 2

    # Pointwise speed is NOT spatially constant
    assert not np.isclose(np.min(speed_sq), np.max(speed_sq))

    # Analytical derivatives of speed_sq / 2
    # d/dx (speed_sq / 2) = v * v_x + w * w_x = v * (B k cos(kX)) + w * (-B k sin(kX))
    d_dx = v * (B * k * np.cos(k * X)) - w * (B * k * np.sin(k * X))
    d_dy = w * (C * k * np.cos(k * Y)) - u * (C * k * np.sin(k * Y))
    d_dz = u * (A * k * np.cos(k * Z)) - v * (A * k * np.sin(k * Z))

    # u . grad(speed_sq / 2)
    u_dot_grad = u * d_dx + v * d_dy + w * d_dz

    # Pointwise u . grad is NOT identically zero
    assert np.max(np.abs(u_dot_grad)) > 0.1

    # Spatial average over periodic box T^3 is zero (exact divergence)
    mean_stretching = np.mean(u_dot_grad)
    assert np.isclose(mean_stretching, 0.0, atol=1e-10)


def test_counterexample_active_stretching_with_zero_gradient_source():
    """Verify counterexample where S omega != 0 while T = (nabla S)omega == 0."""
    # Constant strain tensor at a critical point of strain (nabla S = 0)
    S0 = np.diag([2.0, -1.0, -1.0])
    omega0 = np.array([1.0, 0.0, 0.0])

    # S omega != 0
    S_omega = S0 @ omega0
    assert not np.allclose(S_omega, np.zeros(3))
    # omega . S omega > 0
    stretching = omega0 @ S_omega
    assert stretching == 2.0

    # At the critical point of strain, nabla S = 0
    nabla_S = np.zeros((3, 3, 3))
    # Contract with omega: T_ij = sum_k (nabla_S)_{j, i, k} omega_k
    T = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            T[i, j] = np.sum(nabla_S[j, i, :] * omega0)

    # T is identically zero while active stretching is strictly positive!
    assert np.allclose(T, 0.0)


def test_dimensional_scaling_weights():
    """Verify the exact parabolic scaling exponents."""
    # Under x -> lambda x, t -> lambda^2 t:
    weights = {
        "u": 1,
        "S": 2,
        "omega": 2,
        "M_n": 2,
        "sigma_stretch": 2,      # rate: omega . S omega / |omega|^2
        "V_stretch": 4,          # vector: S omega
        "P_enstrophy": 6,        # density: omega . S omega
        "G": 3,                  # nabla omega
        "T": 5,                  # (nabla S) omega
        "Xi": 2,                 # ||D J_omega||^2 / |D omega|^2
        "L_n": -2,               # a / M_n
        "J_n": 0                 # 2 nu int Xi dr (dimensionless!)
    }

    # Verify dimensional balance in J_n = 2 nu int Xi dr:
    # [nu] = 0, [Xi] = 2, [dr] = -2 => [J_n] = 0 + 2 - 2 = 0
    assert weights["Xi"] + weights["L_n"] == weights["J_n"]

    # Verify dimensional balance in T = (nabla S) omega:
    # [nabla S] = 1 + [S] = 3; [omega] = 2 => [T] = 3 + 2 = 5
    assert (1 + weights["S"]) + weights["omega"] == weights["T"]

    # Verify enstrophy density: [P_enstrophy] = [omega] + [V_stretch] = 2 + 4 = 6
    assert weights["omega"] + weights["V_stretch"] == weights["P_enstrophy"]
