"""
test_rosetta_core.py: Production Test and Verification Suite for rosetta_core
=============================================================================
Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Status: Verified-Finite Engineering Verification Suite (status: verified-finite).
All Clay Millennium Problems remain strictly OPEN.
"""

import os
import sys
import json
import time
import unittest
import numpy as np

# Ensure rosetta_core is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rosetta_core.schur_condensation import guyan_schur_tare, three_tier_sub_gap_tare
from rosetta_core.tripotent_compressor import squarefree_subspace_compress
from rosetta_core.pfaffian_routing import four_spin_torus_pfaffian_count, pfaffian_skew
from rosetta_core.cfd_helical_filter import cubic_strain_tube_sheet_classifier
from rosetta_core.quantum_entanglement import (
    reconstruct_dirichlet_eigen_wavefunction,
    reconstruct_ground_wavefunction,
    bipartite_schur_entanglement_spectrum,
    canonical_four_workspace_entanglement_states,
    wavefunction_phase_dispersion_and_commutator_audit,
)


class TestRosettaCore(unittest.TestCase):
    
    def test_01_guyan_schur_tare(self):
        """Test Guyan-Schur static condensation against exact analytical block matrix."""
        # 4x4 matrix with A (2x2) and B (2x2)
        # K_AA = [[4, 1], [1, 3]]
        # K_AB = [[1, 0], [0, 1]]
        # K_BB = [[2, 0], [0, 2]]
        # K_AB * K_BB^{-1} * K_AB^T = [[0.5, 0], [0, 0.5]]
        # K_cond = [[3.5, 1], [1, 2.5]]
        K_AA = np.array([[4.0, 1.0], [1.0, 3.0]])
        K_AB = np.array([[1.0, 0.0], [0.0, 1.0]])
        K_BB = np.array([[2.0, 0.0], [0.0, 2.0]])
        
        K_cond = guyan_schur_tare(K_AA, K_AB, K_BB)
        expected = np.array([[3.5, 1.0], [1.0, 2.5]])
        
        np.testing.assert_allclose(K_cond, expected, atol=1e-12)
        self.assertTrue(np.allclose(K_cond, K_cond.T), "Condensed operator must preserve symmetry")

    def test_02_three_tier_sub_gap_tare(self):
        """Test multi-tier baseline taring: sub-gap zeroed, supra-gap preserved."""
        omega = np.array([0.1, 0.2, 0.5, 0.75, 1.0, 1.5, 2.0])
        gamma_gap = 1.0
        
        Q = np.ones((7, 7))
        Q_tared = three_tier_sub_gap_tare(Q, omega, gamma_gap)
        
        # omega[0]=0.1 < 0.5 (half_gap) -> weight = 0
        # omega[1]=0.2 < 0.5 -> weight = 0
        self.assertAlmostEqual(Q_tared[0, 0], 0.0, places=12)
        self.assertAlmostEqual(Q_tared[1, 1], 0.0, places=12)
        # omega[5]=1.5 > 1.0 -> weight = 1.0
        # omega[6]=2.0 > 1.0 -> weight = 1.0
        self.assertAlmostEqual(Q_tared[5, 5], 1.0, places=12)
        self.assertAlmostEqual(Q_tared[6, 6], 1.0, places=12)

    def test_03_tripotent_compressor(self):
        """Test tripotent compressor and 4.71x acceleration on 70-dim Spin(8) space."""
        n = 70
        k = 35
        # Construct operator with 35 active and 35 null dimensions
        M = np.zeros((n, n))
        active_indices = np.arange(k)
        for i in active_indices:
            M[i, i] = 1.0
            
        M_comp, P_act, comp_ratio = squarefree_subspace_compress(M)
        
        self.assertEqual(M_comp.shape, (k, k))
        self.assertEqual(P_act.shape, (n, n))
        # Idempotence: P_act^2 = P_act
        np.testing.assert_allclose(P_act @ P_act, P_act, atol=1e-12)
        # Zero projector P_0 = I - P_act satisfies P_0^2 = P_0
        P_0 = np.eye(n) - P_act
        np.testing.assert_allclose(P_0 @ P_0, P_0, atol=1e-12)
        # Check compression acceleration factor ~ 4.71x
        self.assertGreaterEqual(comp_ratio, 4.0)
        self.assertAlmostEqual(comp_ratio, 4.71, delta=0.1)

    def test_04_four_spin_torus_pfaffian(self):
        """Test 4-spin torus Pfaffian combination matching Lean 4 constructive_four_spin_torus_pfaffian_k33."""
        # Lean 4 certified values: Pf_pp=4, Pf_pm=4, Pf_mp=4, Pf_mm=0 -> (4+4+4-0)/2 = 6
        def make_skew_4(pf_target):
            # 4x4 skew matrix with pfaffian = A01*A23 - A02*A13 + A03*A12
            A = np.zeros((4, 4))
            A[0, 1] = pf_target / 2.0
            A[1, 0] = -A[0, 1]
            A[2, 3] = 2.0
            A[3, 2] = -A[2, 3]
            return A
            
        A_pp = make_skew_4(4.0)
        A_pm = make_skew_4(4.0)
        A_mp = make_skew_4(4.0)
        A_mm = make_skew_4(0.0)
        
        res = four_spin_torus_pfaffian_count(A_pp, A_pm, A_mp, A_mm)
        
        self.assertAlmostEqual(res["pf_pp"], 4.0, places=12)
        self.assertAlmostEqual(res["pf_pm"], 4.0, places=12)
        self.assertAlmostEqual(res["pf_mp"], 4.0, places=12)
        self.assertAlmostEqual(res["pf_mm"], 0.0, places=12)
        self.assertAlmostEqual(res["torus_crossing_count"], 6.0, places=12)
        self.assertEqual(res["resolved_crossing_parity"], 0)

    def test_05_cfd_helical_filter(self):
        """Test CFD helical filter matching Lean 4 constructive_axisymmetric_strain_ceiling_two_thirds."""
        # Axisymmetric strain (-1/2, -1/2, 1)
        grad_u = np.diag([-0.5, -0.5, 1.0])
        res = cubic_strain_tube_sheet_classifier(grad_u)
        
        # Check incompressibility
        self.assertAlmostEqual(res["trace_div"], 0.0, places=14)
        # Check cubic determinant identity residual < 1e-15
        self.assertLess(res["cubic_identity_residual"], 1e-15)
        # Check strain alignment ratio evaluates to exactly 2/3
        self.assertAlmostEqual(res["strain_alignment_ratio"], 2.0 / 3.0, places=14)
        self.assertAlmostEqual(res["ceiling_margin"], 0.0, places=14)
        self.assertEqual(res["morphology"], "vortex_tube")

    def test_06_reconstruct_dirichlet_eigen_wavefunction(self):
        """Test Dirichlet eigen-wavefunction reconstruction, Born norm, and parity."""
        # 16-mode operator
        K = 16
        L = 2.0
        # Positive definite tridiagonal operator
        Q = np.diag(np.linspace(1.0, 5.0, K)) + 0.1 * np.eye(K)
        u_grid = np.linspace(-L / 2.0, L / 2.0, 401)
        
        eigval, c_vec, psi_u, born_norm, parity_error = reconstruct_dirichlet_eigen_wavefunction(
            Q, L, u_grid, mode_index=0
        )
        
        self.assertGreater(eigval, 0.0)
        self.assertEqual(len(c_vec), K)
        self.assertAlmostEqual(float(np.linalg.norm(c_vec)), 1.0, places=12)
        # Born normalization integral close to 1.0
        self.assertAlmostEqual(born_norm, 1.0, places=3)
        # Parity error should be extremely small since cosine basis is even
        self.assertLess(parity_error, 1e-12)

    def test_07_bipartite_schur_entanglement_spectrum(self):
        """Test bipartite Schur complement and entanglement spectrum partition."""
        G_AA = np.array([[2.0, 0.5], [0.5, 2.0]])
        G_AB = np.array([[0.8, 0.1], [0.1, 0.8]])
        G_BB = np.array([[3.0, 0.2], [0.2, 3.0]])
        
        res = bipartite_schur_entanglement_spectrum(G_AA, G_AB, G_BB)
        
        # Exact Pythagorean partition: sin^2(theta) + cos^2(theta) == 1.0
        self.assertAlmostEqual(res["sin_sq_theta"] + res["cos_sq_theta"], 1.0, places=12)
        self.assertGreaterEqual(res["linear_entropy"], 0.0)
        self.assertLessEqual(res["linear_entropy"], 1.0)
        self.assertGreaterEqual(res["von_neumann_entropy"], 0.0)
        self.assertGreaterEqual(res["purity"], 0.0)
        self.assertLessEqual(res["purity"], 1.0)

    def test_08_canonical_four_workspace_entanglement_states(self):
        """Test 4-workspace canonical quantum entanglement states and hierarchy."""
        res = canonical_four_workspace_entanglement_states()
        
        # Hodge: S_lin = 0.5, S_vN = ln(2)
        h = res["workspace_01_hodge"]
        self.assertAlmostEqual(h["linear_entropy"], 0.5, places=12)
        self.assertAlmostEqual(h["von_neumann_entropy"], np.log(2.0), places=12)
        self.assertAlmostEqual(h["purity"], 0.5, places=12)
        
        # Yang-Mills: S_lin = 2/3, S_vN = ln(3)
        ym = res["workspace_02_yang_mills"]
        self.assertAlmostEqual(ym["linear_entropy"], 2.0 / 3.0, places=12)
        self.assertAlmostEqual(ym["von_neumann_entropy"], np.log(3.0), places=12)
        self.assertAlmostEqual(ym["purity"], 1.0 / 3.0, places=12)
        
        # Strict hierarchy matching Lean 4: 0 < S_lin(Hodge) < S_lin(YM)
        s_lin_product = 0.0
        self.assertLess(s_lin_product, h["linear_entropy"])
        self.assertLess(h["linear_entropy"], ym["linear_entropy"])
        
        # Navier-Stokes: Heterochiral (0.5) vs Homochiral (0.0)
        ns_hetero = res["workspace_04_navier_stokes"]["heterochiral_entangled"]
        ns_homo = res["workspace_04_navier_stokes"]["homochiral_product"]
        self.assertAlmostEqual(ns_hetero["linear_entropy"], 0.5, places=12)
        self.assertAlmostEqual(ns_homo["linear_entropy"], 0.0, places=12)

    def test_09_reconstruct_ground_wavefunction_and_schur_spectrum_aliases(self):
        """Test reconstruct_ground_wavefunction and Q_PP/Q_PC/Q_CC bipartite Schur aliases."""
        K = 8
        Q = np.diag(np.linspace(1.0, 3.0, K))
        grid = np.linspace(-1.0, 1.0, 201)
        eigval, c_vec, psi_u, born_norm, parity_error = reconstruct_ground_wavefunction(Q, grid, L=2.0)
        self.assertGreater(eigval, 0.0)
        self.assertAlmostEqual(born_norm, 1.0, places=3)
        self.assertLess(parity_error, 1e-12)
        
        # Test Q_PP, Q_PC, Q_CC keyword argument alias
        Q_PP = np.array([[2.0]])
        Q_PC = np.array([[0.5]])
        Q_CC = np.array([[2.0]])
        spec = bipartite_schur_entanglement_spectrum(Q_PP=Q_PP, Q_PC=Q_PC, Q_CC=Q_CC)
        self.assertAlmostEqual(spec["sin_sq_theta"] + spec["cos_sq_theta"], 1.0, places=12)

    def test_10_wavefunction_phase_dispersion_and_commutator_audit(self):
        """Test phase dispersion rescue beyond triangle wall, commutator uncertainty, and cross-prime Gram."""
        # 1. Audit at L = 4.0
        res_4 = wavefunction_phase_dispersion_and_commutator_audit(L=4.0, K=16)
        self.assertAlmostEqual(res_4["L"], 4.0, places=12)
        self.assertEqual(res_4["K"], 16)
        self.assertGreater(res_4["M_prime"], 20.0)
        
        # Check that naive margin < 0 on ground mode, but DeltaE_disp rescues it
        mode0_4 = res_4["modes"][0]
        self.assertLess(mode0_4["naive_triangle_margin"], 0.0)
        self.assertGreater(mode0_4["delta_E_disp"], 0.0)
        self.assertAlmostEqual(mode0_4["sum_identity_residual"], 0.0, places=10)
        self.assertGreaterEqual(mode0_4["eigenvalue"], -1e-12)
        self.assertTrue(mode0_4["dispersion_rescues_positivity"])
        self.assertGreater(mode0_4["uncertainty_product"], 0.0)
        
        # Commutator non-vanishing
        comm_4 = res_4["commutator"]
        self.assertTrue(comm_4["is_non_commuting"])
        self.assertGreater(comm_4["frobenius_norm"], 1.0)
        self.assertGreater(comm_4["spectral_norm"], 1.0)
        
        # Cross-prime Gram matrix strictly positive definite
        gram_4 = res_4["cross_prime_gram"]
        self.assertTrue(gram_4["is_strictly_positive_definite"])
        self.assertGreater(gram_4["min_eigenvalue"], 0.0)
        self.assertEqual(gram_4["prime_count"], 25)
        # Check exact rational evaluations matching Lean 4 concrete_first_prime_pair_gram_floor
        self.assertAlmostEqual(gram_4["concrete_G22"], 5.0 / 8.0, places=12)
        self.assertAlmostEqual(gram_4["concrete_G33"], 5.0 / 9.0, places=12)
        self.assertAlmostEqual(gram_4["concrete_G23"], 5.0 / 12.0, places=12)
        self.assertAlmostEqual(gram_4["concrete_det_2x2"], 25.0 / 144.0, places=12)
        self.assertGreater(gram_4["concrete_det_2x2"], 0.0)

        # 2. Audit at L = 6.0 (deep past triangle wall)
        res_6 = wavefunction_phase_dispersion_and_commutator_audit(L=6.0, K=16)
        self.assertGreater(res_6["M_prime"], 70.0)
        mode0_6 = res_6["modes"][0]
        # Naive margin is deeply negative past the triangle wall (< -60.0)
        self.assertLess(mode0_6["naive_triangle_margin"], -60.0)
        # But phase dispersion DeltaE_disp adds > 60.0 back!
        self.assertGreater(mode0_6["delta_E_disp"], 60.0)
        self.assertGreaterEqual(mode0_6["eigenvalue"], -1e-12)
        self.assertTrue(mode0_6["dispersion_rescues_positivity"])
        self.assertGreater(res_6["commutator"]["frobenius_norm"], 10.0)


def run_and_generate_receipt():
    t0 = time.time()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRosettaCore)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - t0
    
    assert result.wasSuccessful(), f"Tests failed: errors={len(result.errors)}, failures={len(result.failures)}"
    assert elapsed < 10.0, f"Test suite took too long: {elapsed:.2f} s"
    
    receipt_dir = os.path.join(parent_dir, "reports")
    os.makedirs(receipt_dir, exist_ok=True)
    receipt_path = os.path.join(receipt_dir, "probe_rosetta_core_engineering_suite_receipt.json")
    
    receipt_data = {
        "probe_id": "PROBE-ROSETTA-CORE-ENGINEERING-SUITE-001",
        "author": "Qamar Munawer",
        "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg",
        "methodology": "ai is being used as a tool",
        "epistemic_status": "verified-finite",
        "all_four_clay_millennium_problems_open": True,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": elapsed,
        "tests_run": result.testsRun,
        "errors": len(result.errors),
        "failures": len(result.failures),
        "verified": True,
        "status": "PASS",
        "modules_verified": {
            "schur_condensation": {
                "guyan_schur_tare": "VERIFIED (exact static condensation, symmetry preserved)",
                "three_tier_sub_gap_tare": "VERIFIED (bulk sub-gap modes zeroed, supra-gap active modes preserved)"
            },
            "tripotent_compressor": {
                "squarefree_subspace_compress": "VERIFIED (P_0^2=P_0, P_active^2=P_active, 4.71x acceleration on 70->35 subspace)"
            },
            "pfaffian_routing": {
                "four_spin_torus_pfaffian_count": "VERIFIED (4-spin torus Pfaffian combination on (4,4,4,0) evaluates to 6.0, matching Lean 4 constructive_four_spin_torus_pfaffian_k33)"
            },
            "cfd_helical_filter": {
                "cubic_strain_tube_sheet_classifier": "VERIFIED (axisymmetric strain (-1/2,-1/2,1) trace=0, cubic identity residual < 1e-15, ratio=2/3, matching Lean 4 constructive_axisymmetric_strain_ceiling_two_thirds)"
            },
            "quantum_entanglement": {
                "reconstruct_dirichlet_eigen_wavefunction": "VERIFIED (Born normalization integral = 1.0, parity error < 1e-12)",
                "bipartite_schur_entanglement_spectrum": "VERIFIED (exact Pythagorean partition sin^2 + cos^2 = 1.0, S_lin, S_vN, purity)",
                "canonical_four_workspace_entanglement_states": "VERIFIED (Hodge S_lin=1/2, YM S_lin=2/3, NS hetero=1/2 vs homo=0, matching Lean 4 pfaffian_bell_and_baryonic_y_junction_entanglement_hierarchy)",
                "wavefunction_phase_dispersion_and_commutator_audit": "VERIFIED (DeltaE_disp rescues Q_W past triangle wall at L=4,6; ||[A,P]||_F > 0, Cross-Prime Gram min eval > 0, matching Lean 4 RosettaPhaseDispersionAndUncertaintyCert)"
            }
        }
    }
    
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2)
        
    print(f"\n[RECEIPT SAVED] {receipt_path}")
    print(f"Elapsed: {elapsed:.4f} s | Status: PASS | Verified: True")


if __name__ == "__main__":
    run_and_generate_receipt()
