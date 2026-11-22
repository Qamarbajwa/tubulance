"""
Unit tests for Genuine Finite-Continuum su(2) Fuzzy Sphere, DEC, 4D Chiral Product Manifold,
Dimensional Homogeneity, and 4D Ornstein-Zernike Drift Tare.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Date: 2026-11-22
Methodology Note: ai is being used as a tool
Epistemic Boundary: status: verified-finite, open_horizon_lock: STRICTLY OPEN

Validates:
1. Exact su(2) Fuzzy Sphere Casimir preservation (machine-precision zero).
2. Exact Lie algebra commutation relations [X_a, X_b] = i*theta*eps_abc*X_c.
3. Analytical action matching Tr([X,X]^2) == 2*N*R^4 / (g^2*(N^2 - 1)).
4. Monotonic convergence of the non-commutativity parameter theta -> 0 as N -> infty.
5. DEC plaquette vacuum action S=0 and non-trivial excitation S > 0.
6. 4D chiral product fuzzy manifold S^2_L x S^2_R scaling: Delta_phys = 1 / R^2 independent of N.
7. Dimensionally homogeneous crossover m_gap(R) = sqrt(lambda_geom + Delta_dyn^2) in L^-1.
8. 4D Euclidean correlator scaling (r^-2 scalar, r^-8 glueball) and exact 3/(2r) drift tare.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math
import numpy as np
import pytest

from scripts.probe_finite_continuum_models import (
    get_su2_generators,
    analyze_fuzzy_sphere,
    analyze_dec_simplicial_model
)
from scripts.probe_4d_matrix_gauge_continuum import (
    run_phase3_scaling,
    construct_4d_fuzzy_geometry,
    compute_fluctuation_spectrum
)
from scripts.probe_infinite_volume_r4_transition import compute_crossover_spectrum
from scripts.probe_osterwalder_schrader_os4_correlator import simulate_glueball_correlator
from scripts.probe_nonabelian_commutator_schur_gap import (
    construct_spherical_multiplet_basis,
    compute_quartic_stiffness_tensor,
    compute_berezin_toeplitz_scaling,
    compute_mixed_parity_schur_spectrum,
    compute_schur_spectrum_at_radius,
    compute_closed_form_rational_predictions
)
from scripts.probe_dynamical_chamber_and_markov_seams import (
    compute_vacuum_chamber_profile,
    verify_universal_trophic_sum_of_squares,
    verify_trophic_sum_of_squares_and_tridiagonal_markov
)


def test_fuzzy_sphere_casimir_and_commutation():
    """Verify Casimir invariant and commutation relations for N=2..16."""
    N_list = [2, 3, 4, 5, 8, 16]
    results = analyze_fuzzy_sphere(N_list, R=1.0, g=1.0)
    
    for r in results:
        assert r["casimir_err"] < 1e-14
        assert r["comm_err"] < 1e-14
        assert math.isclose(r["action_val"], r["action_th"], rel_tol=1e-12)
        assert r["spectral_gap"] == 2.0


def test_fuzzy_sphere_continuum_limit_theta():
    """Verify that the non-commutative parameter theta -> 0 monotonically as N -> infty."""
    N_list = [2, 4, 8, 16, 32, 64]
    thetas = []
    for N in N_list:
        j = (N - 1) / 2.0
        theta = 1.0 / math.sqrt(j * (j + 1))
        thetas.append(theta)
        
    for i in range(len(thetas) - 1):
        assert thetas[i] > thetas[i+1]
        
    assert thetas[-1] < 0.04


def test_dec_plaquette_vacuum_and_excitations():
    """Verify DEC plaquette vacuum action is 0 and perturbed action is strictly positive."""
    betas = [0.1, 0.5, 1.0, 2.0, 3.0]
    results = analyze_dec_simplicial_model(betas)
    
    for r in results:
        assert r["S_vac"] == 0.0
        assert r["S_exc"] > 0.0
        assert r["M_gap"] > 0.0


def test_4d_chiral_product_fuzzy_manifold_scaling():
    """Verify 4D chiral product fuzzy manifold S^2_L x S^2_R gap cancellation to 1 / R^2."""
    res = run_phase3_scaling()
    R = 1.0
    for entry in res:
        N = entry["N"]
        theta = entry["theta"]
        gap = entry["spectral_gap"]
        
        # Metric factor theta^-2 = (N - 1) / (4 * R^2)
        theta_inv_sq = 1.0 / (theta ** 2)
        expected_metric = (N - 1.0) / (4.0 * (R ** 2))
        assert math.isclose(theta_inv_sq, expected_metric, rel_tol=1e-12)
        
        # Unscaled matrix gap Delta_N = 4 / (N - 1)
        expected_gap = 4.0 / (N - 1.0)
        assert math.isclose(gap, expected_gap, rel_tol=1e-12)
        
        # Physical gap Delta_phys = theta^-2 * Delta_N == 1 / R^2
        phys_gap = theta_inv_sq * gap
        assert math.isclose(phys_gap, 1.0 / (R ** 2), rel_tol=1e-12)
        
        # Vacuum uniqueness: exactly 1 zero mode
        assert entry["zero_modes"] == 1


def test_dimensional_homogeneity_and_infinite_volume_transition():
    """Verify dimensional homogeneity of lambda_geom, Delta_dyn, m_gap, and lambda_total."""
    R_vals = [0.1, 0.5, 1.0, 5.0, 20.0, 50.0]
    Lambda_QCD = 1.2000
    res = compute_crossover_spectrum(R_vals, Lambda_QCD=Lambda_QCD)
    
    for entry in res:
        R = entry["R"]
        lam_geom = entry["lambda_geom"]
        delta_dyn = entry["delta_dyn"]
        m_gap = entry["m_gap"]
        lam_total = entry["lambda_total"]
        
        # Check geometric Laplacian eigenvalue is exactly 1 / R^2 (L^-2)
        assert math.isclose(lam_geom, 1.0 / (R ** 2), rel_tol=1e-12)
        
        # Check linear mass gap m_gap = sqrt(lambda_geom + Delta_dyn^2) (L^-1)
        expected_m_gap = math.sqrt(lam_geom + delta_dyn ** 2)
        assert math.isclose(m_gap, expected_m_gap, rel_tol=1e-12)
        
        # Check squared total gap lambda_total = lambda_geom + Delta_dyn^2 (L^-2)
        expected_lam_total = lam_geom + delta_dyn ** 2
        assert math.isclose(lam_total, expected_lam_total, rel_tol=1e-12)
        assert math.isclose(lam_total, m_gap ** 2, rel_tol=1e-12)
        
    # UV dominance: at R = 0.1, m_gap is dominated by 1 / R = 10
    assert res[0]["m_gap"] > 10.0
    
    # IR saturation: at R = 50.0, Delta_dyn saturates to Lambda_QCD
    assert math.isclose(res[-1]["delta_dyn"], Lambda_QCD, rel_tol=1e-6)
    assert math.isclose(res[-1]["m_gap"], Lambda_QCD, rel_tol=1e-3)


def test_4d_ornstein_zernike_drift_tare_and_correlator_scaling():
    """Verify 4D scalar and glueball scaling and exact 3/(2r) spherical drift tare."""
    r_vals = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
    m_true = 1.2000
    A = 2.5
    res = simulate_glueball_correlator(r_vals, m_gap=m_true, A=A)
    
    for entry in res:
        r = entry["r"]
        c_massive = entry["c_massive"]
        c_dim4 = entry["c_massless_dim4"]
        c_scalar = entry["c_massless_scalar"]
        m_eff_raw = entry["m_eff_raw"]
        drift = entry["drift_term"]
        m_eff_tared = entry["m_eff_tared"]
        tare_err = entry["tare_error"]
        
        # Check 4D massless scalar scaling: A / r^2
        assert math.isclose(c_scalar, A / (r ** 2), rel_tol=1e-12)
        
        # Check 4D massless dimension-4 glueball scaling: A / r^8
        assert math.isclose(c_dim4, A / (r ** 8), rel_tol=1e-12)
        
        # Check drift term is exactly 3 / (2 * r)
        assert math.isclose(drift, 1.5 / r, rel_tol=1e-12)
        
        # Check raw effective mass is m_true + 3 / (2 * r)
        assert math.isclose(m_eff_raw, m_true + 1.5 / r, rel_tol=1e-12)
        
        # Check tared effective mass exactly recovers m_true = 1.2000
        assert math.isclose(m_eff_tared, m_true, rel_tol=1e-14)
        assert tare_err < 1e-14


def test_nonabelian_commutator_stiffness_and_schur_gap():
    """Verify non-abelian quartic commutator stiffness, B=0 selection rule, and mass plateau."""
    for N, expected_stiff in [(3, 5.0), (4, 2.0), (5, 1.0)]:
        T_l1, ortho_l2, j = construct_spherical_multiplet_basis(N)
        M_stiff = compute_quartic_stiffness_tensor(T_l1, ortho_l2)
        
        # Exact isotropic diagonal stiffness: M_stiff == C_stiff * I_3
        for a in range(3):
            for b in range(3):
                if a == b:
                    assert math.isclose(M_stiff[a, b], expected_stiff, rel_tol=1e-12)
                else:
                    assert abs(M_stiff[a, b]) < 1e-12
                    
        # Tree-level gap vanishes as R -> infty
        r_tree_small = compute_schur_spectrum_at_radius(1.0, N, v_cond=0.0, is_isotropic=True)
        r_tree_large = compute_schur_spectrum_at_radius(100.0, N, v_cond=0.0, is_isotropic=True)
        assert r_tree_small["min_eval_Seff"] == 2.0
        assert math.isclose(r_tree_large["min_eval_Seff"], 0.0002, rel_tol=1e-6)
        
        # Non-abelian condensate provides exact mass plateau Delta = C_stiff * v^2
        v = 0.5
        expected_plateau = expected_stiff * (v ** 2)
        r_cond_large = compute_schur_spectrum_at_radius(1000.0, N, v_cond=v, is_isotropic=True)
        assert math.isclose(r_cond_large["min_eval_Seff"], expected_plateau, rel_tol=1e-4)
        assert r_cond_large["norm_B"] < 1e-15


def test_berezin_toeplitz_continuum_convergence():
    """Verify Berezin-Toeplitz grain scaling C_stiff(N) = 120/(N(N^2-1)) and invariant C_phys == 1."""
    for N in [3, 4, 5, 6, 8, 10, 12]:
        res = compute_berezin_toeplitz_scaling(N)
        expected_raw = 120.0 / (N * (N ** 2 - 1))
        assert math.isclose(res["c_raw"], expected_raw, rel_tol=1e-12)
        assert math.isclose(res["c_phys_canonical"], 1.0, rel_tol=1e-12)
        assert math.isclose(res["c_phys_baseline"], 5.0, rel_tol=1e-12)


def test_mixed_parity_active_schur_tare_positivity():
    """Verify active off-diagonal friction B != 0 and Schur complement positivity at R = 1000."""
    prev_seff = 0.0
    for N in [3, 4, 5, 6, 8, 10, 12]:
        r = compute_mixed_parity_schur_spectrum(N, v1=0.2, v2=0.5, R=1000.0, use_grain_norm=True)
        
        # Friction is active and strictly non-zero
        assert math.isclose(r["norm_B"], 0.5189, rel_tol=1e-3)
        assert r["norm_B"] > 0.5
        
        # Quadrupole block A is strictly positive
        assert r["min_A"] > 0.35
        
        # Diagonal stiffness D strictly dominates Schur tare loss
        assert r["min_D"] > r["norm_tare"]
        
        # Schur complement is strictly positive
        assert r["min_Seff"] > 0.15
        assert r["stable"] is True
        
        # Monotonic convergence as N -> infty
        assert r["min_Seff"] >= prev_seff
        prev_seff = r["min_Seff"]


def test_exact_representation_theoretic_closed_form_limits():
    """Verify closed-form rational formulas for min(A(N)), tare_e2(N), min(S_eff(N)), and N -> infty limits."""
    for N in [4, 5, 6, 8, 10, 12]:
        # At large R=1e7, the 2/R^2 free kinetic term vanishes to machine precision
        r = compute_mixed_parity_schur_spectrum(N, v1=0.2, v2=0.5, R=1e7, use_grain_norm=True)
        pred = compute_closed_form_rational_predictions(N, v1=0.2, v2=0.5)
        
        # Machine-precision agreement between numeric matrix diagonalisation and closed-form rational formula
        assert math.isclose(r["min_A"], pred["min_A"], rel_tol=1e-10)
        assert math.isclose(r["min_Seff"], pred["min_Seff"], rel_tol=1e-10)
        assert pred["min_A"] >= 1.36999
        assert pred["min_Seff"] >= 0.20240
        
    # Check asymptotic limits
    pred_inf = compute_closed_form_rational_predictions(100, v1=0.2, v2=0.5)
    assert math.isclose(pred_inf["min_A_inf"], 1209.0 / 700.0, rel_tol=1e-12)
    assert math.isclose(pred_inf["tare_e2_inf"], 28.0 / 403.0, rel_tol=1e-12)
    assert math.isclose(pred_inf["min_Seff_inf"], 8887.0 / 40300.0, rel_tol=1e-12)
    assert pred_inf["min_Seff_inf"] > 0.2205


def test_seam1_vacuum_chamber_self_selection():
    """
    Verify Seam 1:
    1. At N=3, phi=pi/4 (v1=v2) yields min_S == 0 and singular Tr(S^-1) == inf.
    2. For all N >= 4, Chamber II (v2 > v1 > 0, phi=75 deg) strictly dominates
       Chamber I (v1 > v2 > 0, phi=15 deg) in Tr(H), min(A), min(S_eff),
       1-loop spectral stability (smaller Tr(S^-1)), and log det(H).
    """
    r_n3_wall = compute_vacuum_chamber_profile(3, math.pi / 4.0, R=1e15)
    assert abs(r_n3_wall["min_S"]) < 1e-12
    assert math.isinf(r_n3_wall["tr_inv_S"])
    
    for N in [4, 6, 8, 12, 100]:
        r_ch1 = compute_vacuum_chamber_profile(N, math.radians(15.0), R=1e15)
        r_ch2 = compute_vacuum_chamber_profile(N, math.radians(75.0), R=1e15)
        
        assert r_ch2["tr_H"] > r_ch1["tr_H"]
        assert r_ch2["min_A"] > r_ch1["min_A"]
        assert r_ch2["min_S"] > r_ch1["min_S"]
        assert r_ch2["tr_inv_S"] < r_ch1["tr_inv_S"]
        assert r_ch2["log_det_H"] > r_ch1["log_det_H"]


def test_universal_trophic_sum_of_squares_identity():
    """
    Verify universal Trophic Sum-of-Squares Decomposition across N in {3..100}
    and angles phi in (0, pi/2), plus exact canonical landmarks:
    441/2900 at N=3 (0.2, 0.5), 29/400 at N=4 (45 deg), and 29/275 continuum limit.
    """
    sos = verify_universal_trophic_sum_of_squares(rho_sq=0.29)
    assert sos["max_err"] <= 1e-13
    assert sos["err_n3_landmark"] <= 1e-14
    assert sos["err_n4_45"] <= 1e-14
    assert sos["err_inf_exact"] <= 1e-15
    assert math.isclose(sos["barrier_inf"], 29.0 / 275.0, rel_tol=1e-14)


def test_trophic_four_elevenths_ratio_and_tridiagonal_markov():
    """
    Verify:
    1. Asymptotic symmetric-ray 4/11 ratio and barrier 29/275.
    2. Exact tridiagonal inverse K_N = Q_N^-1 across N=2..25, zero |j-k|>=2 entries,
       corner entry J_Markov(p_{N-1}, p_N), and Markov Sum-of-Squares quadratic form.
    """
    tm = verify_trophic_sum_of_squares_and_tridiagonal_markov(rho_sq=0.29, seed=42)
    assert tm["trophic_max_err"] <= 1e-15
    assert tm["err_4_11"] <= 1e-15
    assert tm["err_29_275"] <= 1e-15
    assert tm["max_inv_err"] <= 2e-13
    assert tm["max_residual_err"] <= 1e-14
    assert tm["max_off_tridiag"] <= 2e-13
    assert tm["max_corner_err"] <= 1e-13
    assert tm["max_quad_err"] <= 1e-12






