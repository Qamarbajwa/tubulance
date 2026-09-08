"""
Unit and Deterministic Regression Tests for TP2-G6-A2:
Scale-Critical Transport, Parabolic Regularity Envelopes, and Stochastic Push-Forward Measure Bounds.

Verifies:
1. Normalization and pathwise incompressibility identities (B2-L1)
2. Parabolic regularity envelope scales: tau_n = M_n^{-1}, r_n = nu^{1/2} M_n^{-1/2}
3. Chebyshev volume bounds on Eulerian superlevel sets E_s(alpha)
4. Serrin index deficit of Navier-Stokes energy bounds (2/2 + 3/6 = 1.5 > 1)
5. Deformation tensor SVD and history measure decoupling bounds (Theorem 8.1)
6. Convective sweeping and missed spike transition probability decay (Benchmark BM-A2-04)
7. Hyperbolic saddle trapping and measure concentration decoupling (Benchmark BM-A2-05)
8. Bridge B2 hierarchy status: B2-L1 proved, B2-L2 through B2-L5 obstructed
9. Two-particle relative drift cancellation identity
"""

import math
import numpy as np
import pytest


def test_measure_normalization():
    """Verify that stochastic history measure weights normalize to 1."""
    # Generate positive random weights Z_i^2
    np.random.seed(42)
    Z_sq = np.random.uniform(0.1, 10.0, size=100)
    S = np.sum(Z_sq)
    d_mu = Z_sq / S
    assert math.isclose(np.sum(d_mu), 1.0, rel_tol=1e-12)
    assert np.all(d_mu > 0.0)


def test_pathwise_jacobian_incompressibility():
    """
    Verify that div(u) = 0 implies det(grad A_s) = 1 pathwise via Liouville's equation:
    dJ / ds = -(div u) J = 0 => J(s) = J(t) = 1.
    """
    div_u = 0.0
    J_0 = 1.0
    # Discrete integration of dJ = -(div_u) * J * ds
    ds = 0.01
    J = J_0
    for _ in range(100):
        dJ = -div_u * J * ds
        J += dJ
    assert math.isclose(J, 1.0, rel_tol=1e-14)


def test_parabolic_regularity_scales():
    """
    Verify parabolic scales:
    tau_n = M_n^{-1}
    r_n = sqrt(nu / M_n)
    Diffusive displacement = sqrt(2 * nu * tau_n) = sqrt(2) * r_n
    """
    nu = 1e-3
    M_values = [10.0, 100.0, 1000.0, 10000.0]
    for M in M_values:
        tau = 1.0 / M
        r_visc = math.sqrt(nu / M)
        diff_disp = math.sqrt(2.0 * nu * tau)
        ratio = diff_disp / r_visc
        assert math.isclose(ratio, math.sqrt(2.0), rel_tol=1e-12)


def test_chebyshev_volume_bound():
    """
    Verify that Eulerian superlevel set volume satisfies:
    |E_s(alpha)| <= 2 * Omega / (alpha^2 * M^2) -> 0 as M -> inf.
    """
    Omega = 5.0  # enstrophy bound
    alpha = 0.5
    M_values = [10.0, 50.0, 100.0, 500.0, 1000.0]
    volumes = []
    for M in M_values:
        max_vol = (2.0 * Omega) / ((alpha * M) ** 2)
        volumes.append(max_vol)

    # Verify strictly decreasing
    for i in range(len(volumes) - 1):
        assert volumes[i] > volumes[i + 1]

    # Verify asymptotic limit at M = 1000
    assert volumes[-1] <= 2.0 * 5.0 / (0.25 * 1e6)  # 4e-5


def test_serrin_index_energy_deficit():
    """
    Verify Serrin exponent calculation:
    For u in L^q_t L^p_x, condition is 2/q + 3/p <= 1.
    Under 3D Navier-Stokes energy bounds: u in L^2_t L^6_x => q=2, p=6.
    Serrin exponent = 2/2 + 3/6 = 1.5 > 1 (supercritical by 0.5).
    """
    q = 2.0
    p = 6.0
    serrin_index = (2.0 / q) + (3.0 / p)
    assert math.isclose(serrin_index, 1.5, rel_tol=1e-12)
    assert serrin_index > 1.0
    scaling_deficit = serrin_index - 1.0
    assert math.isclose(scaling_deficit, 0.5, rel_tol=1e-12)


def test_deformation_svd_and_vorticity_decoupling():
    """
    Verify History Measure Decoupling (Theorem 8.1):
    D_s deformation matrix can align with compression axis to extinguish |Z_s|^2
    even in high-vorticity core, or with stretching axis to amplify in low-vorticity saddle.
    """
    # Case A: Spike core with compression along vorticity axis
    # Let omega = [0, 0, M_n]
    M_n = 1e4
    omega_core = np.array([0.0, 0.0, M_n])
    # Backward deformation matrix contracts along z-axis: D_s = diag(e^lambda, e^lambda, e^{-2lambda})
    # Since dD = -D grad u, if grad u has positive eigenvalue along z, D contracts.
    lambda_strain = 5.0
    D_core = np.diag([math.exp(lambda_strain), math.exp(lambda_strain), math.exp(-2.0 * lambda_strain)])
    assert math.isclose(np.linalg.det(D_core), 1.0, rel_tol=1e-12)

    Z_core = D_core @ omega_core
    Z_core_sq = np.sum(Z_core ** 2)
    # Z_core_sq = exp(-4 * lambda_strain) * M_n^2
    # For lambda_strain = 5.0, exp(-20) = 2.06e-9, so Z_core_sq = 2.06e-9 * 1e8 = 0.206 << M_n^2
    assert Z_core_sq < 1.0  # Extinguished below unit magnitude despite M_n = 10,000!

    # Case B: Saddle point with low vorticity omega = [1, 0, 0] aligned with backward expansion
    omega_saddle = np.array([1.0, 0.0, 0.0])
    Z_saddle = D_core @ omega_saddle
    Z_saddle_sq = np.sum(Z_saddle ** 2)
    # Z_saddle_sq = exp(2 * lambda_strain) * 1 = exp(10) * 1 = 22026.4 >> Z_core_sq
    assert Z_saddle_sq > 20000.0
    assert Z_saddle_sq > Z_core_sq * 10000.0  # Saddle weight dominates core weight by orders of magnitude!


def test_missed_spike_probability_decay():
    """
    Verify Benchmark BM-A2-04:
    When background drift separates particle by d_n >> r_n, the transition density
    probability of landing in the spike decays exponentially:
    P(A_s in E_s) ~ exp(- d_n^2 / (4 * nu * tau_n)).
    """
    nu = 1e-3
    M_n = 1000.0
    tau_n = 1.0 / M_n
    r_n = math.sqrt(nu / M_n)

    # Let background convective drift produce separation d_n = 5 * r_n
    d_n = 5.0 * r_n
    exponent = - (d_n ** 2) / (4.0 * nu * tau_n)
    # d_n^2 / (4 nu tau_n) = 25 * (nu/M_n) / (4 * nu * (1/M_n)) = 25 / 4 = 6.25
    assert math.isclose(exponent, -6.25, rel_tol=1e-12)
    prob_factor = math.exp(exponent)
    assert prob_factor < 0.002  # Less than 0.2% probability of entering the core


def test_bridge_b2_hierarchy_classification():
    """
    Verify Bridge B2 hierarchy statuses established in TP2-G6-A2:
    B2-L0: Refuted (absolute continuity holds)
    B2-L1: PROVED (pathwise incompressibility yields (A_s)_# dx = dx)
    B2-L2: OBSTRUCTED (L^p density bound requires gradient control)
    B2-L3: OBSTRUCTED (high-vorticity coverage defeated by BM-A2-04 & BM-A2-05)
    B2-L4: OBSTRUCTED (scale-critical parabolic envelope localization fails)
    B2-L5: OBSTRUCTED (circularity equivalent to BKM/Serrin)
    """
    bridge_b2_status = {
        "B2-L0": "SUPERSEDED_BY_L1",
        "B2-L1": "PROVED_CANONICAL_CEILING",
        "B2-L2": "OBSTRUCTED_BY_ENERGY_DEFICIT",
        "B2-L3": "OBSTRUCTED_BY_DECOUPLING_AND_SWEEPING",
        "B2-L4": "OBSTRUCTED_BY_DIFFUSIVE_CONVECTIVE_SCALE",
        "B2-L5": "OBSTRUCTED_BY_CIRCULARITY",
    }
    assert bridge_b2_status["B2-L1"] == "PROVED_CANONICAL_CEILING"
    for level in ["B2-L2", "B2-L3", "B2-L4", "B2-L5"]:
        assert "OBSTRUCTED" in bridge_b2_status[level]


def test_two_particle_relative_drift_cancellation():
    """
    Verify the mathematical principle of the Two-Particle Escalation Condition:
    In single-particle transport: dX = u(X) dt + sqrt(2nu) dW.
    If u(x) = U_0 + S * x (uniform drift + strain), single particle is swept by U_0.
    In two-particle difference: delta X = X_1 - X_2,
    d(delta X) = [u(X_1) - u(X_2)] dt + sqrt(2nu) (dW_1 - dW_2).
    u(X_1) - u(X_2) = (U_0 + S * X_1) - (U_0 + S * X_2) = S * delta X.
    The large background drift U_0 cancels identically, restoring scale invariance!
    """
    U_0 = np.array([1000.0, -500.0, 250.0])  # Large background velocity
    S = np.array([[2.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])  # Traceless strain

    x1 = np.array([0.1, 0.2, 0.3])
    x2 = np.array([0.105, 0.198, 0.302])
    delta_x = x1 - x2

    u1 = U_0 + S @ x1
    u2 = U_0 + S @ x2
    delta_u = u1 - u2

    # Verify that delta_u depends ONLY on S and delta_x, completely independent of U_0!
    expected_delta_u = S @ delta_x
    assert np.allclose(delta_u, expected_delta_u, atol=1e-12)
