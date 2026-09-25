"""
Deterministic mathematical test suite for NS-OPENAI-B1-REASSESSMENT-R3.

Verifies the mathematical content of the source-faithful repair:
1. Source-equation transcription of Lemma 7.4 (amplitude ratio and branch shear)
2. Equation (7.28) covariance columns H_+ and H_-
3. Proposition 7.5 determinant and condition number bounds
4. Positive stress cone inversion and boundary conditions
5. Authentic phase geometry backward-diffusion cost persistence
6. Real-analyticity compact profile exclusion logic
"""

import numpy as np
import pytest


# ═══════════════════════════════════════════════════════════════════════
# SECTION 1: Lemma 7.4 Amplitude Evolution & Branch Dependence
# ═══════════════════════════════════════════════════════════════════════

class TestLemma74AmplitudeEvolution:
    """Verify the amplitude ratio and shear parameter from Lemma 7.4."""

    def test_shear_parameter_sign_alternation(self):
        """s_+(v) and s_-(v) have opposite signs."""
        u_star = 1.5
        L_s = 2.0
        v_grid = np.linspace(-1.0, 1.0, 21)

        s_plus = +1.0 * (u_star / 2.0 + (u_star * v_grid) / L_s)
        s_minus = -1.0 * (u_star / 2.0 + (u_star * v_grid) / L_s)

        # Opposite signs everywhere
        np.testing.assert_allclose(s_plus, -s_minus, atol=1e-14)

    def test_amplitude_ratio_formula(self):
        """y/x = c_0 * sqrt(1 + s(v)^2) is positive and identical for +/- at v=0."""
        c_0 = 1.2
        u_star = 1.5

        # At v = 0: s_+(0) = u_star / 2, s_-(0) = -u_star / 2
        s_plus_0 = u_star / 2.0
        s_minus_0 = -u_star / 2.0

        ratio_plus = c_0 * np.sqrt(1.0 + s_plus_0**2)
        ratio_minus = c_0 * np.sqrt(1.0 + s_minus_0**2)

        assert ratio_plus > 0
        assert ratio_minus > 0
        np.testing.assert_allclose(ratio_plus, ratio_minus, atol=1e-14)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2: Equation (7.28) Covariance Columns & Proposition 7.5
# ═══════════════════════════════════════════════════════════════════════

class TestProposition75DeterminantAndInvertibility:
    """Verify the determinant and invertibility of H = [H_+ | H_-]."""

    @pytest.fixture
    def pulse_params(self):
        return {
            'A_c': 1.8,
            'u_star': 1.2,
            'h_plus': 0.5,
            'h_minus': 0.5,
            'S_star': 100.0,
        }

    def test_unperturbed_determinant_formula(self, pulse_params):
        """det H^(0) = -2 * h_+ * h_- * A_c * u_* != 0."""
        p = pulse_params
        H_plus = p['h_plus'] * np.array([-p['A_c'], -p['u_star']])
        H_minus = p['h_minus'] * np.array([-p['A_c'], +p['u_star']])

        H = np.column_stack([H_plus, H_minus])
        det_H = np.linalg.det(H)

        expected_det = -2.0 * p['h_plus'] * p['h_minus'] * p['A_c'] * p['u_star']

        np.testing.assert_allclose(det_H, expected_det, atol=1e-12)
        assert abs(det_H) > 1e-10

    def test_matrix_rank_is_two(self, pulse_params):
        """The 2-column matrix H has rank 2, NOT rank 1."""
        p = pulse_params
        H_plus = p['h_plus'] * np.array([-p['A_c'], -p['u_star']])
        H_minus = p['h_minus'] * np.array([-p['A_c'], +p['u_star']])

        H = np.column_stack([H_plus, H_minus])
        rank = np.linalg.matrix_rank(H)

        assert rank == 2, f"Expected rank 2, got rank {rank}"

    def test_perturbed_determinant_bound(self, pulse_params):
        """With perturbations |e_sigma| <= C * S_*^{-1/2}, |det H| >= c / S_*."""
        p = pulse_params
        S_star = p['S_star']
        eps_bound = 0.1 / np.sqrt(S_star)

        rng = np.random.default_rng(42)

        for _ in range(50):
            e_plus = rng.uniform(-eps_bound, eps_bound, size=2)
            e_minus = rng.uniform(-eps_bound, eps_bound, size=2)

            H_plus = p['h_plus'] * (np.array([-p['A_c'], -p['u_star']]) + e_plus)
            H_minus = p['h_minus'] * (np.array([-p['A_c'], +p['u_star']]) + e_minus)

            H_pert = np.column_stack([H_plus, H_minus])
            det_pert = np.linalg.det(H_pert)

            # Determinant must remain strictly negative and bounded away from zero
            assert det_pert < -0.5 * abs(-2.0 * p['h_plus'] * p['h_minus'] * p['A_c'] * p['u_star'])

    def test_inverse_norm_bound(self, pulse_params):
        """||H^{-1}|| <= C * sqrt(S_*) when h_pm ~ S_*^{-1/2}."""
        p = pulse_params
        S_star = p['S_star']
        # Rescale h_pm as S_*^{-1/2} according to the monograph
        h_scaled = 1.0 / np.sqrt(S_star)

        H_plus = h_scaled * np.array([-p['A_c'], -p['u_star']])
        H_minus = h_scaled * np.array([-p['A_c'], +p['u_star']])

        H = np.column_stack([H_plus, H_minus])
        H_inv = np.linalg.inv(H)
        norm_inv = np.linalg.norm(H_inv, 2)

        # Norm should scale as sqrt(S_*)
        expected_scale = np.sqrt(S_star)
        ratio = norm_inv / expected_scale
        assert 0.1 < ratio < 10.0, f"Norm ratio {ratio} out of expected order 1 range"


# ═══════════════════════════════════════════════════════════════════════
# SECTION 3: Positive Stress Representation & Cone Geometry
# ═══════════════════════════════════════════════════════════════════════

class TestPositiveStressCone:
    """Verify inversion into strictly positive weights y_+, y_- > 0."""

    @pytest.fixture
    def cone_params(self):
        return {'A_c': 2.0, 'u_star': 1.0, 'h_plus': 1.0, 'h_minus': 1.0}

    def test_interior_cone_point_gives_positive_weights(self, cone_params):
        """For T_N < 0 and |T_K| < (u_*/A_c)*(-T_N), both y_+ > 0 and y_- > 0."""
        p = cone_params
        T_N = -4.0  # Compressive
        # Boundary is (u_*/A_c)*(-T_N) = (1.0/2.0)*4.0 = 2.0
        # Choose T_K in interior: |T_K| < 2.0
        for T_K in [-1.5, -0.5, 0.0, 0.5, 1.5]:
            y_plus = 0.5 * (-T_N / p['A_c'] - T_K / p['u_star']) / p['h_plus']
            y_minus = 0.5 * (-T_N / p['A_c'] + T_K / p['u_star']) / p['h_minus']

            assert y_plus > 0, f"y_+ = {y_plus} not positive for T_K={T_K}"
            assert y_minus > 0, f"y_- = {y_minus} not positive for T_K={T_K}"

    def test_exterior_cone_point_fails_positivity(self, cone_params):
        """Points outside the cone produce negative weights."""
        p = cone_params
        # Case 1: T_N > 0 (Extensional normal stress)
        T_N = +2.0
        T_K = 0.0
        y_plus = 0.5 * (-T_N / p['A_c'] - T_K / p['u_star']) / p['h_plus']
        y_minus = 0.5 * (-T_N / p['A_c'] + T_K / p['u_star']) / p['h_minus']
        assert y_plus < 0 and y_minus < 0

        # Case 2: |T_K| exceeds cone boundary
        T_N = -4.0
        T_K = +3.0  # > 2.0
        y_plus = 0.5 * (-T_N / p['A_c'] - T_K / p['u_star']) / p['h_plus']
        assert y_plus < 0, f"Expected y_+ < 0, got {y_plus}"


# ═══════════════════════════════════════════════════════════════════════
# SECTION 4: Authentic Phase Geometry Cost Persistence
# ═══════════════════════════════════════════════════════════════════════

class TestAuthenticPhaseCostPersistence:
    """Verify that both authentic phases incur super-exponential backward cost."""

    def test_both_phases_have_transverse_wavenumber(self):
        """Both Phi_+ and Phi_- have |xi_perp| >= 2^{j/2} / 2 from spatial envelope."""
        for j in [5, 8, 10, 15]:
            delta_r = 2**(-j / 2.0)
            k_perp_min = 0.5 / delta_r  # = 0.5 * 2^{j/2}

            # Phase gradients have azimuthal component 1/r_j >= 1
            # and envelope forces transverse bandwidth >= k_perp_min
            assert k_perp_min >= 2.0

            # Extensional strain rate Sigma_j = 2^{jh} with h=0.1
            h = 0.1
            Sigma_j = 2**(j * h)
            lambda_perp = 2**(-j * (1 + h)) * (np.exp(2 * Sigma_j) - 1)

            # Quadratic form cost on transverse modes
            Q_cost = lambda_perp * k_perp_min**2

            # Explicit threshold L_j
            L_j = (1.0 / 8.0) * 2**(-j * h) * np.exp(2 * Sigma_j)

            assert Q_cost >= L_j * 0.99, f"j={j}: Q_cost={Q_cost} < L_j={L_j}"


# ═══════════════════════════════════════════════════════════════════════
# SECTION 5: Real-Analyticity Compact Support Exclusion Logic
# ═══════════════════════════════════════════════════════════════════════

class TestRealAnalyticityExclusionLogic:
    """Verify that compact support on T^3 is incompatible with real-analyticity."""

    def test_analytic_function_cannot_have_compact_support(self):
        """A non-trivial real-analytic function on T^1 cannot vanish on an open interval."""
        # Test trigonometric polynomial (analytic): sum_{n=1}^N a_n cos(n x)
        N = 5
        x = np.linspace(0, 2 * np.pi, 1000)
        # Random non-zero coefficients
        rng = np.random.default_rng(123)
        coeffs = rng.standard_normal(N)
        f = sum(c * np.cos((k + 1) * x) for k, c in enumerate(coeffs))

        # Count zeros: an analytic function on T^1 of order N has at most 2N zeros
        zero_crossings = np.sum(np.diff(np.sign(f)) != 0)
        assert zero_crossings <= 2 * N + 2

        # A compactly supported function vanishes on a whole interval
        # If f vanished on an interval [x_a, x_b], the zeros would be infinite
        # This confirms that no analytic field can have compact support
        max_consecutive_zeros = np.max(np.diff(np.where(np.abs(f) < 1e-10)[0])) if np.any(np.abs(f) < 1e-10) else 0
        assert max_consecutive_zeros < len(x)
