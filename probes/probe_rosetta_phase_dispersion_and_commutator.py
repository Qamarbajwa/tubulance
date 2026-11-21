"""
probe_rosetta_phase_dispersion_and_commutator.py
================================================
Production audit probe for Phase Dispersion Energy, Robertson-Schroedinger Commutator
Uncertainty Floor, and Cross-Prime Gram Matrix Positive Definiteness.

Evaluates the exact decomposition across L in {1.0, 2.0, 4.0, 6.0} and K = 32:
    Q_W(Psi_m) = <A_arch>_m - M_prime(L) + Delta E_disp(Psi_m)
demonstrating that the strictly positive dispersive phase energy Delta E_disp > 0
rescues the margin beyond the classical triangle-inequality wall (where naive <A> - M < 0),
verifies operator non-commutativity ||[A_arch, P_prime]||_F > 0, and confirms
positive-definiteness of the 25x25 Cross-Prime Gram matrix.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Status: Verified-Finite Probe (status: verified-finite).
All Clay Millennium Problems remain strictly OPEN.
"""

import os
import sys
import json
import time
import numpy as np

# Ensure rosetta_core is importable
probe_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.dirname(probe_dir)
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from rosetta_core.quantum_entanglement import (
    wavefunction_phase_dispersion_and_commutator_audit,
)


def run_probe():
    t0 = time.time()
    L_values = [1.0, 2.0, 4.0, 6.0]
    K = 32
    
    sweep_results = []
    all_passed = True
    
    print("=" * 84)
    print("PROBE: PHASE DISPERSION, COMMUTATOR UNCERTAINTY & CROSS-PRIME GRAM AUDIT (K = 32)")
    print("Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg")
    print("Methodology: ai is being used as a tool")
    print("=" * 84)
    
    for L in L_values:
        audit = wavefunction_phase_dispersion_and_commutator_audit(L=L, K=K)
        
        M_prime = audit["M_prime"]
        modes = audit["modes"]
        comm = audit["commutator"]
        gram = audit["cross_prime_gram"]
        
        # Verify exact decomposition on every mode
        max_residual = max(m["sum_identity_residual"] for m in modes)
        assert max_residual < 1e-10, f"Decomposition residual exceeded threshold at L={L}: {max_residual}"
        
        # Verify commutator non-vanishing
        assert comm["is_non_commuting"], f"Commutator vanished at L={L}"
        assert comm["frobenius_norm"] > 0.5, f"Frobenius norm too small at L={L}: {comm['frobenius_norm']}"
        
        # Verify cross-prime Gram strict positive definiteness
        assert gram["is_strictly_positive_definite"], f"Cross-prime Gram not positive definite at L={L}"
        assert gram["min_eigenvalue"] > 0.0, f"Gram min eigenvalue <= 0 at L={L}"
        
        # Check concrete pair values matching Lean 4
        assert abs(gram["concrete_G22"] - 5.0 / 8.0) < 1e-12
        assert abs(gram["concrete_G33"] - 5.0 / 9.0) < 1e-12
        assert abs(gram["concrete_G23"] - 5.0 / 12.0) < 1e-12
        assert abs(gram["concrete_det_2x2"] - 25.0 / 144.0) < 1e-12
        assert gram["concrete_det_2x2"] > 0.0
        
        # Check triangle wall rescue for L >= 4.0
        mode0 = modes[0]
        if L >= 4.0:
            assert mode0["naive_triangle_margin"] < 0.0, f"Expected naive margin < 0 at L={L}"
            assert mode0["delta_E_disp"] > 0.0, f"Expected DeltaE_disp > 0 at L={L}"
            assert mode0["dispersion_rescues_positivity"], f"Dispersion did not rescue positivity at L={L}"
            assert mode0["eigenvalue"] >= -1e-11, f"Negative eigenvalue beyond tolerance at L={L}: {mode0['eigenvalue']}"
            
        print(
            f"L={L:3.1f} | M_prime={M_prime:6.2f} | Naive(m=0)={mode0['naive_triangle_margin']:7.2f} | "
            f"DeltaE_disp(m=0)={mode0['delta_E_disp']:7.2f} | Q_W(m=0)={mode0['eigenvalue']:9.6f} | "
            f"||[A,P]||_F={comm['frobenius_norm']:6.2f} | Gram lam_min={gram['min_eigenvalue']:.4e}"
        )
        
        # Record summary for receipt
        sweep_results.append({
            "L": L,
            "K": K,
            "M_prime": round(M_prime, 4),
            "commutator_frobenius_norm": round(comm["frobenius_norm"], 4),
            "commutator_spectral_norm": round(comm["spectral_norm"], 4),
            "cross_prime_gram_min_eigenvalue": gram["min_eigenvalue"],
            "cross_prime_gram_max_eigenvalue": gram["max_eigenvalue"],
            "max_decomposition_residual": max_residual,
            "ground_mode": {
                "eigenvalue": mode0["eigenvalue"],
                "A_arch_expectation": round(mode0["A_arch_expectation"], 4),
                "naive_triangle_margin": round(mode0["naive_triangle_margin"], 4),
                "delta_E_disp": round(mode0["delta_E_disp"], 4),
                "dispersion_rescues_positivity": mode0["dispersion_rescues_positivity"],
                "delta_A": round(mode0["delta_A"], 4),
                "delta_P": round(mode0["delta_P"], 4),
                "uncertainty_product": round(mode0["uncertainty_product"], 4)
            },
            "first_excited_mode": {
                "eigenvalue": modes[1]["eigenvalue"],
                "naive_triangle_margin": round(modes[1]["naive_triangle_margin"], 4),
                "delta_E_disp": round(modes[1]["delta_E_disp"], 4),
                "uncertainty_product": round(modes[1]["uncertainty_product"], 4)
            }
        })
        
    elapsed = time.time() - t0
    
    receipt_data = {
        "probe_id": "PROBE-ROSETTA-PHASE-DISPERSION-AND-COMMUTATOR-001",
        "author": "Qamar Munawer",
        "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg",
        "methodology": "ai is being used as a tool",
        "epistemic_status": "verified-finite",
        "all_four_clay_millennium_problems_open": True,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": elapsed,
        "verified": True,
        "status": "PASS",
        "parameters": {
            "L_values": L_values,
            "K": K,
            "prime_count": 25,
            "lambda_exponent": 0.5
        },
        "lean4_matched_theorems": [
            "RosettaPhaseDispersionAndUncertainty.phase_dispersion_restores_positivity_beyond_triangle_wall",
            "RosettaPhaseDispersionAndUncertainty.commutator_uncertainty_sum_floor",
            "RosettaPhaseDispersionAndUncertainty.cross_prime_gram_matrix_strict_positivity",
            "RosettaPhaseDispersionAndUncertainty.concrete_first_prime_pair_gram_floor"
        ],
        "sweep_results": sweep_results
    }
    
    # Save receipt in probes/ and reports/
    receipt_path_probe = os.path.join(probe_dir, "probe_rosetta_phase_dispersion_and_commutator_receipt.json")
    with open(receipt_path_probe, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2)
        
    receipt_dir_reports = os.path.join(workspace_dir, "reports")
    os.makedirs(receipt_dir_reports, exist_ok=True)
    receipt_path_report = os.path.join(receipt_dir_reports, "probe_rosetta_phase_dispersion_and_commutator_receipt.json")
    with open(receipt_path_report, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2)
        
    print(f"\n[RECEIPT SAVED] {receipt_path_probe}")
    print(f"[RECEIPT SAVED] {receipt_path_report}")
    print(f"Elapsed: {elapsed:.4f} s | Status: PASS | Verified: True")


if __name__ == "__main__":
    run_probe()
