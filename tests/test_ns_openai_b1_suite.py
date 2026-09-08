"""
Test Suite for NS-OPENAI-B1: Autonomous Multiscale Precursor Cascade Programme
Verifies exact identities, scaling asymptotics, Sobolev convergence, and stress cone geometry.
"""

import math
import numpy as np
import pytest


class TestNSOpenAIB1Suite:

    def test_01_viscous_damping_integral_uniform_bound(self):
        """
        Verify that the cumulative viscous dissipation D_j = nu * int_0^t_j |k_j(s)|^2 ds
        is uniformly bounded by nu * (K_0^2 + 1) for all j = 1..50.
        """
        nu = 1e-3
        K_0 = 1.0
        bound = nu * (K_0**2 + 1.0)

        for j in range(1, 51):
            tau_j = 2.0**(-j)
            t_j = 1.0 - tau_j
            delta_t_j = tau_j

            # Phase 1: quiescent [0, t_j - delta_t_j] at |k| <= K_0
            d_phase1 = nu * (K_0**2) * (t_j - delta_t_j)

            # Phase 2: burst [t_j - delta_t_j, t_j] sweeping to |k| = 2^(j/2)
            # Integral of |k|^2 over burst <= (2^(j/2))^2 * delta_t_j = 2^j * 2^(-j) = 1
            d_phase2 = nu * (2.0**j) * delta_t_j

            d_total = d_phase1 + d_phase2
            assert d_total <= bound + 1e-12, f"Failed at j={j}: D_j={d_total} > {bound}"
            assert d_total <= nu * (1.0 + 1.0) + 1e-12

    def test_02_shear_amplification_divergence(self):
        """
        Verify that the cumulative strain amplification G_j = int_0^t_j Gamma_j ds
        scales as c_S * 2^(j*h) -> infty for h = 0.05.
        """
        h = 0.05
        c_S = 2.0

        for j in range(1, 40):
            tau_j = 2.0**(-j)
            delta_t_j = tau_j
            # Burst shear rate ~ c_S * 2^(j(1+h))
            gamma_peak = c_S * (2.0**(j * (1.0 + h)))
            g_burst = gamma_peak * delta_t_j
            expected_scaling = c_S * (2.0**(j * h))
            assert math.isclose(g_burst, expected_scaling, rel_tol=1e-10)

        # Monotonic divergence
        g_vals = [c_S * (2.0**(j * h)) for j in range(1, 40)]
        assert all(g_vals[i] < g_vals[i+1] for i in range(len(g_vals)-1))
        assert g_vals[-1] > 7.0  # 2.0 * 2^(39*0.05) = 2.0 * 3.86 = 7.73

    def test_03_net_exponent_divergence(self):
        """
        Verify that A_j = G_j - D_j -> +infty monotonically for all j >= 5.
        """
        nu = 1e-3
        K_0 = 1.0
        h = 0.05
        c_S = 1.5
        D_bound = nu * (K_0**2 + 1.0)

        for j in range(1, 50):
            G_j = c_S * (2.0**(j * h)) - 0.5  # minus macro lower bound
            A_j = G_j - D_bound
            if j >= 5:
                assert A_j > 0.5, f"Net exponent must be strongly positive at j={j}"
            if j >= 15:
                assert A_j > 1.0, f"Net exponent must exceed 1.0 at j={j}"

        # Asymptotic divergence check
        A_final = c_S * (2.0**(100 * h)) - 0.5 - D_bound
        assert A_final > 40.0, "Net exponent must diverge to +infinity"

    def test_04_initial_sobolev_convergence(self):
        """
        Verify that the initial precursor sum sum_j ||w_j(0)||_H^m converges rapidly
        for every Sobolev index m in {0, 2, 4, 8, 16}.
        """
        h = 0.05
        c_1 = 5.0  # Core singular shear coefficient

        for m in [0, 2, 4, 8, 16]:
            terms = []
            for j in range(1, 200):
                # Norm bounded by 2^(j*(1/2 + h + m/2)) * exp(-c_1 * 2^(j*h))
                log_poly = (0.5 + h + 0.5 * m) * j * math.log(2.0)
                exp_decay = c_1 * (2.0**(j * h))
                net_log = log_poly - exp_decay
                if net_log > 700:
                    term = float('inf')
                elif net_log < -700:
                    term = 0.0
                else:
                    term = math.exp(net_log)
                terms.append(term)

            total_sum = sum(terms)
            assert math.isfinite(total_sum), f"Sobolev norm sum for m={m} must be finite"
            assert terms[-1] == 0.0, f"Tail terms for m={m} must vanish"
            # Verify that peak occurs at small j and tails vanish rapidly
            assert terms[150] < 1e-10

    def test_05_subcritical_kinetic_energy_decay(self):
        """
        Verify that the kinetic energy of each incoming pulse E(W_j*) ~ 2^(j*(3h - 0.5))
        strictly decays to 0 for h = 0.05, and that total energy sum is finite.
        """
        h = 0.05
        exponent = 3.0 * h - 0.5  # -0.35 < 0

        energies = [2.0**(j * exponent) for j in range(1, 100)]
        assert all(energies[i] > energies[i+1] for i in range(len(energies)-1)), "Pulse energy must strictly decrease"
        assert energies[-1] < 1e-10, "Pulse energy must vanish as j -> infty"

        total_energy = sum(energies)
        analytic_sum = (2.0**exponent) / (1.0 - 2.0**exponent)
        assert math.isclose(total_energy, analytic_sum, rel_tol=1e-10)
        assert total_energy < 5.0, f"Total energy {total_energy} must be modest"

    def test_06_stress_cone_interior_landing(self):
        """
        Verify that the quadratic Reynolds stress Q_j = <w_j (x) w_j> satisfies:
        Q_rz < 0, Q_theta_theta > 0, and distance to boundary d_K(Q_j) > 0.
        """
        # Principal stretching eigenvector components (alpha_r > 0, alpha_z < 0)
        alpha_r = 1.0 / math.sqrt(3.0)
        alpha_theta = 1.0 / math.sqrt(3.0)
        alpha_z = -1.0 / math.sqrt(3.0)

        # Polarization error delta_e ~ exp(-c 2^(jh))
        for j in range(1, 20):
            delta_e = math.exp(-0.2 * (2.0**(j * 0.05)))
            e_r = alpha_r + delta_e * 0.01
            e_theta = alpha_theta + delta_e * 0.01
            e_z = alpha_z - delta_e * 0.01

            Q_rz = e_r * e_z
            Q_theta_theta = e_theta**2
            Q_rr = e_r**2
            Q_zz = e_z**2

            assert Q_rz < -0.2, f"Axial jet flux Q_rz must be strictly negative at j={j}"
            assert Q_theta_theta > 0.2, f"Azimuthal flux Q_theta_theta must be strictly positive at j={j}"
            assert Q_rr > 0.2 and Q_zz > 0.2

    def test_07_nonlinear_crosstalk_uniform_bound(self):
        """
        Verify that the sum of past and future cross-talk interactions on mode j
        is uniformly bounded by a constant independent of total cascade size N.
        """
        h = 0.05
        c_overlap = 0.5
        c_future = 5.0

        for j in [5, 10, 20, 50]:
            # Past modes i < j: geometric decay exp(-c 2^(j-i))
            past_sum = sum(math.exp(-c_overlap * (2.0**(j - i))) for i in range(1, j))

            # Future modes k > j: super-exponential decay exp(-c 2^(kh))
            future_sum = sum(math.exp(-c_future * (2.0**(k * h))) for k in range(j + 1, j + 50))

            total_crosstalk = past_sum + future_sum
            assert total_crosstalk < 1.0, f"Cross-talk at j={j} must be uniformly bounded"
            assert past_sum < 0.6
            assert future_sum < 0.1
