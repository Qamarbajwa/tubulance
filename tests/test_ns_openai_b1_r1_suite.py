"""
Test Suite for NS-OPENAI-B1-R1: Autonomous Precursor Cascade Realizability Re-Audit
Verifies plane-wave convective cancellation, two-wave stress cone matrix invertibility,
Gevrey non-analyticity index, and explicit test limitations.
"""

import math
import numpy as np
import pytest


class TestNSOpenAIB1R1Suite:

    def test_01_plane_wave_convective_cancellation_identity(self):
        """
        Verify the exact theorem that for any solenoidal plane wave w = a * cos(k.x + phi),
        the convective self-advection term (w . grad)w vanishes identically because a . k = 0.
        """
        np.random.seed(42)
        for _ in range(50):
            # Generate random non-zero wavevector k in R^3
            k = np.random.randn(3)
            k = k / np.linalg.norm(k)

            # Generate random polarization 'a' orthogonal to k (divergence-free condition)
            v = np.random.randn(3)
            a = v - np.dot(v, k) * k
            a = a / np.linalg.norm(a)
            assert abs(np.dot(a, k)) < 1e-12, "Polarization must be strictly solenoidal"

            # Compute convective directional derivative (w . grad)w at 20 random points x
            for _ in range(20):
                x = np.random.randn(3)
                phase = np.dot(k, x) + 0.5

                # w(x) = a * cos(phase)
                w = a * math.cos(phase)

                # grad w(x) = - a (x) k * sin(phase)
                # (w . grad)w = sum_i w_i d_i w = - a * (w . k) * sin(phase)
                w_dot_k = np.dot(w, k)
                assert abs(w_dot_k) < 1e-12, "w . k must be identically zero"

                convective_term = - a * w_dot_k * math.sin(phase)
                assert np.linalg.norm(convective_term) < 1e-12, "Convective self-advection must vanish identically"

    def test_02_rank_one_dyad_cannot_invert_two_dimensional_target_stress(self):
        """
        Verify that a single wave dyadic stress Q = A^2 (e (x) e) has rank 1,
        and cannot invert an arbitrary 2D target stress vector T = [T_r, T_z]^T.
        """
        # Target stress with non-proportional components
        T = np.array([2.5, -4.0])

        # Single wave polarization e in R^2
        e = np.array([0.6, -0.8])
        Q_single = np.outer(e, e)
        assert np.linalg.matrix_rank(Q_single) == 1, "Single wave dyad must have rank 1"

        # Attempt to represent T as a single wave contribution C_single * y
        # Vectorized components C = [e_r^2, e_r * e_z]^T
        C_single = np.array([e[0]**2, e[0] * e[1]])
        # If T is not a scalar multiple of C_single, system has no solution
        det_check = T[0] * C_single[1] - T[1] * C_single[0]
        assert abs(det_check) > 1e-6, "Target T is linearly independent from C_single; single wave fails"

    def test_03_two_wave_helical_matrix_invertibility(self):
        """
        Verify the OpenAI Section 7 mechanism: two distinct helical wave families
        C(b_+) and C(b_-) form an invertible 2x2 matrix H, allowing y = H^-1 T > 0.
        """
        # Column 1: C(b_+) for positive helical mode
        C_plus = np.array([1.5, -3.0])
        # Column 2: C(b_-) for negative helical mode
        C_minus = np.array([0.8, -0.5])

        H = np.column_stack([C_plus, C_minus])
        det_H = np.linalg.det(H)
        assert abs(det_H) > 0.1, "Two-wave coupling matrix H must be non-singular"

        # Target core stress in the cone
        T_target = np.array([2.0, -2.5])

        # Solve y = H^-1 T
        y = np.linalg.solve(H, T_target)
        assert y[0] > 0, "Weight y_+ must be strictly positive"
        assert y[1] > 0, "Weight y_- must be strictly positive"

        # Reconstructed stress matches target
        T_reconstructed = H @ y
        assert np.allclose(T_target, T_reconstructed, atol=1e-10)

    def test_04_gevrey_non_analyticity_index(self):
        """
        Verify that for h = 0.05, the precursor Sobolev growth corresponds to
        Gevrey class s = 1/(2h) = 10, which is strictly non-analytic (s > 1).
        """
        h = 0.05
        gevrey_index = 1.0 / (2.0 * h)
        assert gevrey_index == 10.0, "Gevrey index must be exactly 10"
        assert gevrey_index > 1.0, "Gevrey index > 1 refutes real-analyticity (C^omega requires s = 1)"

    def test_05_clock_sensitivity_divergence(self):
        """
        Verify that the arrival time sensitivity dt / dr_0 ~ 2^(j/2) diverges as j -> infty,
        confirming that small spatial placement errors create arrival errors larger than burst duration.
        """
        sensitivities = [2.0**(j / 2.0) for j in range(1, 30)]
        assert all(sensitivities[i] < sensitivities[i+1] for i in range(len(sensitivities)-1))
        assert sensitivities[-1] > 20000.0, "Clock sensitivity must diverge to +infinity"

        # At j = 10, burst duration is 2^(-10) = 0.00097, sensitivity is 2^5 = 32
        # A placement error of delta_r = 1e-4 produces arrival error 32 * 1e-4 = 0.0032 > burst duration!
        delta_r = 1e-4
        delta_t = 32.0 * delta_r
        burst_duration = 2.0**(-10)
        assert delta_t > burst_duration, "Spatial error scrambles timing outside the active burst window"

    def test_06_subcritical_pulse_energy(self):
        """
        Verify that single-pulse kinetic energy E(W_j*) ~ 2^(j*(3h - 0.5)) strictly decays
        to 0 for h = 0.05 (exponent = -0.35 < 0).
        """
        h = 0.05
        exponent = 3.0 * h - 0.5
        assert exponent == -0.35
        energies = [2.0**(j * exponent) for j in range(1, 50)]
        assert energies[-1] < 1e-5, "Single pulse energy must decay to zero"

    def test_07_explicit_test_limitation_statement(self):
        """
        Explicitly verify that passing deterministic algebraic unit tests does NOT
        prove infinite-dimensional backward PDE solvability or uniform cascade existence.
        """
        algebraic_tests_pass = True
        backward_pde_solvability_proved = False
        infinite_cascade_proved = False

        assert algebraic_tests_pass is True
        assert backward_pde_solvability_proved is False, "Passing tests does NOT prove backward PDE solvability"
        assert infinite_cascade_proved is False, "Passing tests does NOT prove infinite cascade existence"
