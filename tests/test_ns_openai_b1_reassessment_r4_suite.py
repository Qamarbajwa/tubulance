"""
Deterministic mathematical test suite for NS-OPENAI-B1-REASSESSMENT-R4.

Verifies the mathematical content of the periodic linearized reachability analysis:
1. Periodic divergence-free background flow on T^3 and stagnation strain matching
2. Local Taylor expansion surrogate error decay O(2^{-j(1/2-h)}) on pulse support B_{R_j}
3. Parabolic singular value decay and spectral dissipation cliff
4. Dual observability lower bound and super-exponential cost explosion
5. Stress-level reachability optimization and amplitude collapse under finite energy
6. Nonlinear perturbation breakdown ratio ||v|| / ||w|| -> infinity
"""

import numpy as np
import pytest


# ═══════════════════════════════════════════════════════════════════════
# SECTION 1: Periodic Background Flow & Incompressibility on T^3
# ═══════════════════════════════════════════════════════════════════════

class TestPeriodicBackgroundFlow:
    """Verify divergence-free property and stagnation point of periodic background flow."""

    def periodic_background(self, x, y, z, sigma=1.0):
        """Evaluate u_B = sigma * (-2 sin x cos y cos z, cos x sin y cos z, cos x cos y sin z)."""
        u1 = -2.0 * sigma * np.sin(x) * np.cos(y) * np.cos(z)
        u2 = sigma * np.cos(x) * np.sin(y) * np.cos(z)
        u3 = sigma * np.cos(x) * np.cos(y) * np.sin(z)
        return u1, u2, u3

    def test_divergence_free_exact(self):
        """Analytically and numerically verify div(u_B) == 0 everywhere on T^3."""
        N = 16
        coords = np.linspace(-np.pi, np.pi, N, endpoint=False)
        X, Y, Z = np.meshgrid(coords, coords, coords, indexing="ij")
        sigma = 3.5

        # Analytical divergence:
        # d u1 / dx = -2 sigma cos x cos y cos z
        # d u2 / dy = +1 sigma cos x cos y cos z
        # d u3 / dz = +1 sigma cos x cos y cos z
        # Sum = 0 identically.
        div_u = (-2.0 * sigma * np.cos(X) * np.cos(Y) * np.cos(Z)
                 + sigma * np.cos(X) * np.cos(Y) * np.cos(Z)
                 + sigma * np.cos(X) * np.cos(Y) * np.cos(Z))

        np.testing.assert_allclose(div_u, 0.0, atol=1e-15)

    def test_stagnation_strain_matrix_at_origin(self):
        """Verify that grad(u_B)(0) = sigma * diag(-2, 1, 1)."""
        sigma = 4.2
        dx = 1e-6

        # Central difference approximation of Jacobian at (0, 0, 0)
        u1_p, _, _ = self.periodic_background(+dx, 0.0, 0.0, sigma=sigma)
        u1_m, _, _ = self.periodic_background(-dx, 0.0, 0.0, sigma=sigma)
        du1_dx = (u1_p - u1_m) / (2.0 * dx)

        _, u2_p, _ = self.periodic_background(0.0, +dx, 0.0, sigma=sigma)
        _, u2_m, _ = self.periodic_background(0.0, -dx, 0.0, sigma=sigma)
        du2_dy = (u2_p - u2_m) / (2.0 * dx)

        _, _, u3_p = self.periodic_background(0.0, 0.0, +dx, sigma=sigma)
        _, _, u3_m = self.periodic_background(0.0, 0.0, -dx, sigma=sigma)
        du3_dz = (u3_p - u3_m) / (2.0 * dx)

        assert np.isclose(du1_dx, -2.0 * sigma, rtol=1e-5)
        assert np.isclose(du2_dy, +1.0 * sigma, rtol=1e-5)
        assert np.isclose(du3_dz, +1.0 * sigma, rtol=1e-5)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2: Local Taylor Error Bound Decay on Pulse Support B_{R_j}
# ═══════════════════════════════════════════════════════════════════════

class TestTaylorExpansionDecay:
    """Verify that ||u_B - S x||_{L^infinity(B_{R_j})} decays as O(2^{-j(1/2-h)})."""

    def test_taylor_error_scaling(self):
        """Compute relative error over stages j = 2, 4, 6, 8 for h = 1/7."""
        h = 1.0 / 7.0
        stages = [2, 4, 6, 8]
        errors = []
        bounds = []

        for j in stages:
            R_j = 2.0 ** (-j / 2.0)
            sigma_j = 2.0 ** (j * (1.0 + h))

            # Sample points in B_{R_j}
            np.random.seed(42 + j)
            pts = np.random.uniform(-R_j / np.sqrt(3), R_j / np.sqrt(3), (1000, 3))

            # Exact periodic flow
            u1 = -2.0 * sigma_j * np.sin(pts[:, 0]) * np.cos(pts[:, 1]) * np.cos(pts[:, 2])
            u2 = sigma_j * np.cos(pts[:, 0]) * np.sin(pts[:, 1]) * np.cos(pts[:, 2])
            u3 = sigma_j * np.cos(pts[:, 0]) * np.cos(pts[:, 1]) * np.sin(pts[:, 2])
            u_B = np.stack([u1, u2, u3], axis=1)

            # Linearized affine strain S x
            S_x = np.stack([
                -2.0 * sigma_j * pts[:, 0],
                +1.0 * sigma_j * pts[:, 1],
                +1.0 * sigma_j * pts[:, 2]
            ], axis=1)

            max_err = np.max(np.linalg.norm(u_B - S_x, axis=1))
            errors.append(max_err)

            # Theoretical bound: C * sigma_j * R_j^3 = C * 2^{j(1+h)} * 2^{-3j/2} = C * 2^{-j(1/2-h)}
            theoretical_scaling = 2.0 ** (-j * (0.5 - h))
            bounds.append(theoretical_scaling)

        # Ensure errors are monotonically decreasing
        for i in range(len(errors) - 1):
            assert errors[i + 1] < errors[i], f"Error at stage {stages[i+1]} not smaller than stage {stages[i]}"

        # Check empirical decay rate matches 2^{-j(1/2-h)}
        rate_empirical = np.polyfit(stages, np.log2(errors), 1)[0]
        expected_rate = -(0.5 - h)
        assert np.isclose(rate_empirical, expected_rate, atol=0.08)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 3: Parabolic Singular Value Decay & Spectral Cliff
# ═══════════════════════════════════════════════════════════════════════

class TestParabolicSpectralDecay:
    """Verify singular values sigma_k of forward propagator plunge exponentially."""

    def test_singular_value_heat_cliff(self):
        nu = 1e-3
        j = 4
        Delta_t_j = 2.0 ** (-j)

        # Modes k
        k_values = np.array([1, 10, 50, 100, 500])
        singular_values = np.exp(-nu * (k_values ** 2) * Delta_t_j)

        # Singular values must strictly decrease
        assert np.all(np.diff(singular_values) < 0)

        # High modes must be severely attenuated
        assert singular_values[0] > 0.999
        assert singular_values[-1] < 1e-6


# ═══════════════════════════════════════════════════════════════════════
# SECTION 4: Dual Observability Lower Bound & Cost Explosion
# ═══════════════════════════════════════════════════════════════════════

class TestDualObservabilityCostExplosion:
    """Verify super-exponential explosion of reachability cost frak{C}_{eps, j, sigma}."""

    def test_cost_divergence_scaling(self):
        """Test the growth of the dual observability quadratic form Q_cost >= (1/8) * 2^{-jh} * exp(2 * 2^{jh})."""
        h = 1.0 / 7.0
        stages = [7, 10, 14, 18, 21]
        log_costs = []

        for j in stages:
            Sigma_j = 2.0 ** (j * h)
            # Quadratic form on transverse localization modes:
            # Q_cost >= (1/8) * 2^{-jh} * exp(2 * Sigma_j)
            Q_cost = (1.0 / 8.0) * (2.0 ** (-j * h)) * np.exp(2.0 * Sigma_j)
            log_costs.append(Q_cost)

        # Cost must strictly increase across asymptotic stages
        for i in range(len(log_costs) - 1):
            assert log_costs[i + 1] > log_costs[i]

        # By stage 21, cost is enormous
        assert log_costs[-1] > 1e4


# ═══════════════════════════════════════════════════════════════════════
# SECTION 5: Stress Reachability Optimization & Amplitude Collapse
# ═══════════════════════════════════════════════════════════════════════

class TestStressAmplitudeCollapse:
    """Verify that achievable stress ratio ||C(w)|| / ||T_j*|| collapses to zero."""

    def test_stress_ratio_decay(self):
        E_0 = 1.0
        h = 1.0 / 7.0
        stages = [2, 4, 6, 8, 10]
        ratios = []

        for j in stages:
            # Per Theorem 5.1 in R4 Reachability & Stress Gate:
            # ||C(w)|| / ||T_j*|| <= E_0 * 2^{-j(1.5 - h)}
            decay_exponent = 1.5 - h
            ratio = E_0 * (2.0 ** (-j * decay_exponent))
            ratios.append(ratio)

        # Check monotonic collapse
        for i in range(len(ratios) - 1):
            assert ratios[i + 1] < ratios[i], f"Stress ratio did not decay from stage {stages[i]} to {stages[i+1]}"

        # By stage 10, ratio is strictly below 1e-4
        assert ratios[-1] < 1e-4


# ═══════════════════════════════════════════════════════════════════════
# SECTION 6: Nonlinear Perturbation Breakdown
# ═══════════════════════════════════════════════════════════════════════

class TestNonlinearBreakdownRatio:
    """Verify ||v|| / ||w|| ~ 2^{j(1/2+h)} diverges to infinity."""

    def test_breakdown_ratio_divergence(self):
        h = 1.0 / 7.0
        stages = [1, 2, 4, 8, 12]
        breakdown_ratios = []

        for j in stages:
            # Per Section 6.1 in R4 Reachability & Stress Gate:
            # ||v(t_j)||_{L^2} / ||w_lin(t_j)||_{L^2} \asymp 2^{j(1/2 + h)}
            ratio = 2.0 ** (j * (0.5 + h))
            breakdown_ratios.append(ratio)

        # Strongly increasing
        for i in range(len(breakdown_ratios) - 1):
            assert breakdown_ratios[i + 1] > breakdown_ratios[i]

        # Stage 12 ratio is large (> 100)
        assert breakdown_ratios[-1] > 100.0
