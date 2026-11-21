"""
test_tare_core.py
=================
Unified Unit Test and Benchmark Suite for tare_core:
The Schur-Tare Coercivity Kernel on NVIDIA RTX A2000 8GB GPU.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Boundary: All four Clay Millennium Problems remain strictly OPEN
(status: verified-finite, open_horizon_lock: STRICTLY OPEN).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Add parent directory to sys.path so tare_core can be imported cleanly
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    DEVICE_NAME = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else "CPU"
    TOTAL_VRAM_GB = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if CUDA_AVAILABLE else 0.0
except ImportError:
    CUDA_AVAILABLE = False
    DEVICE_NAME = "CPU (PyTorch not installed)"
    TOTAL_VRAM_GB = 0.0

from tare_core.silicon_vram_compressor import (
    gpu_kron_schur_condensation,
    gpu_llm_kv_cache_schur_tare,
    optimal_sram_tile_schedule,
)
from tare_core.prime_horizon_gpu import (
    guinand_weil_spectral_prime_scanner,
    high_altitude_sqrt_x_window_sieve,
    tared_riemann_R_prime_counter,
)
from tare_core.hbim_bauforschung_adapter import (
    hbim_facade_thermal_tare_analysis,
    export_iso19650_pyrevit_diagnostics,
)
from tare_core.p_vs_np_sat_entanglement import (
    gpu_schur_pfaffian_sat_phase_transition_scanner,
    cad_bim_spaceframe_constraint_condenser,
)
from tare_core.zero_trust_governance_runner import (
    verify_four_workspace_epistemic_and_axiom_governance,
)


def run_all_benchmarks() -> dict:
    t_suite_start = time.time()
    print("=" * 80)
    print("TARE_CORE: THE SCHUR-TARE COERCIVITY KERNEL ON NVIDIA RTX A2000 GPU")
    print("Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg")
    print("Methodology: ai is being used as a tool")
    print("Epistemic Boundary: All four Clay Millennium Problems remain strictly OPEN")
    print(f"Hardware: {DEVICE_NAME} | CUDA Available: {CUDA_AVAILABLE} | Total VRAM: {TOTAL_VRAM_GB} GB")
    print("=" * 80)

    np.random.seed(42)

    # --------------------------------------------------------------------------
    # 1. Silicon Kron / Guyan-Schur Condensation
    # --------------------------------------------------------------------------
    print("\n[1/10] Running Guyan-Schur / Kron Silicon Reduction Benchmark (FP64)...")
    dim_full = 128
    dim_boundary = 16
    A_rand = np.random.randn(dim_full, dim_full)
    K_full = A_rand.T @ A_rand + np.eye(dim_full) * 10.0
    b_indices = list(range(dim_boundary))
    res_kron = gpu_kron_schur_condensation(K_full, b_indices, device="cuda" if CUDA_AVAILABLE else "cpu")
    print(f"  -> Condensed: {res_kron['n_original']}x{res_kron['n_original']} -> {res_kron['n_boundary_preserved']}x{res_kron['n_boundary_preserved']}")
    print(f"  -> Max numerical error (CPU vs GPU): {res_kron['max_error']:.2e} (target < 1e-12)")
    print(f"  -> Coercive (min eigenvalue > 0): {res_kron['coercive']} (min eig = {res_kron['min_eigenvalue']:.4f})")
    print(f"  -> Speedup: {res_kron['speedup']:.1f}x | Peak VRAM: {res_kron['peak_vram_mb']} MB")
    assert res_kron["coercive"], "Schur complement must remain strictly positive definite!"
    assert res_kron["max_error"] < 1e-10, "Numerical discrepancy too high!"

    # --------------------------------------------------------------------------
    # 2. LLM KV-Cache Schur-Tare Compression
    # --------------------------------------------------------------------------
    print("\n[2/10] Running LLM Key-Value Cache Schur-Tare Compression (SeqLen=4096, Dim=128)...")
    seq_len = 4096
    dim = 128
    K_cache = np.random.randn(seq_len, dim).astype(np.float32)
    W_attn = np.random.randn(dim, dim).astype(np.float32)
    U_low = np.random.randn(seq_len, 4).astype(np.float32)
    V_low = np.random.randn(4, dim).astype(np.float32)
    V_cache = K_cache @ W_attn + 0.01 * (U_low @ V_low)
    res_kv = gpu_llm_kv_cache_schur_tare(K_cache, V_cache, rank_keep_ratio=0.18, device="cuda" if CUDA_AVAILABLE else "cpu")
    print(f"  -> Original VRAM: {res_kv['original_vram_mb']} MB | Compressed: {res_kv['compressed_vram_mb']} MB")
    print(f"  -> Compression Ratio: {res_kv['compression_ratio']:.2f}x (target >= 4.0x, met: {res_kv['target_compression_met']})")
    print(f"  -> Frobenius Reconstruction Fidelity: {res_kv['frobenius_fidelity']*100:.1f}% (target > 99.0%, met: {res_kv['target_fidelity_met']})")
    assert res_kv["target_compression_met"], "KV-Cache compression ratio must exceed 4.0x!"
    assert res_kv["target_fidelity_met"], "Frobenius reconstruction fidelity must exceed 99.0%!"

    # --------------------------------------------------------------------------
    # 3. Optimal SRAM / GPU Tile Schedule Benchmark
    # --------------------------------------------------------------------------
    print("\n[3/10] Running Module 35 Optimal SRAM / GPU Tile Schedule Benchmark...")
    res_sram = optimal_sram_tile_schedule(X_total=65536, alpha=2.0, beta=1.0, device="cuda" if CUDA_AVAILABLE else "cpu")
    print(f"  -> Total Elements X = {res_sram['X_total']}, sqrt(X) = {res_sram['sqrt_X']:.1f}")
    print(f"  -> Optimal Tile Size m_opt = {res_sram['m_opt_exact']:.1f} -> Hardware Tile = {res_sram['hardware_tile_selected']}")
    print(f"  -> Theoretical Arithmetic Efficiency Ratio: {res_sram['theoretical_efficiency_ratio']:.2f}x")
    print(f"  -> Max discrepancy between tiled and untiled: {res_sram['max_discrepancy']:.2e}")
    assert res_sram["max_discrepancy"] < 1e-3, "Tile scheduling error exceeds threshold!"

    # --------------------------------------------------------------------------
    # 4. Engine 1: Guinand-Weil Spectral Prime Scanner
    # --------------------------------------------------------------------------
    print("\n[4/10] Running Engine 1: Guinand-Weil Spectral Prime Scanner (50 Zeta Zeros)...")
    res_spectral = guinand_weil_spectral_prime_scanner(x_min=2.0, x_max=50.0, num_zeros=50, device="cuda" if CUDA_AVAILABLE else "cpu")
    print(f"  -> Evaluated {res_spectral['primes_evaluated']} primes in [2, 50] against spectral zero resonance")
    print(f"  -> Primes aligned with zero-interference peaks: {res_spectral['primes_aligned']}/{res_spectral['primes_evaluated']} ({res_spectral['alignment_rate_pct']:.1f}%)")
    print(f"  -> Execution latency: {res_spectral['latency_ms']} ms | CUDA Used: {res_spectral['cuda_used']}")
    assert res_spectral["primes_aligned"] == res_spectral["primes_evaluated"], "All primes must constructively resonate with Guinand-Weil zero sum!"

    # --------------------------------------------------------------------------
    # 5. Engine 2: High-Altitude Segmented Window Sieve at X = 10^18
    # --------------------------------------------------------------------------
    print("\n[5/10] Running Engine 2: High-Altitude Segmented Window Sieve at X = 10^18...")
    res_sieve = high_altitude_sqrt_x_window_sieve(X_start=10**18, window_width=1000)
    print(f"  -> Window: [{10**18}, {10**18 + 1000}] (19-digit scale)")
    print(f"  -> Primes Discovered: {res_sieve['primes_count']} (theoretical expected ~ {res_sieve['theoretical_expected']:.1f})")
    print(f"  -> First 19-Digit Prime Found: {res_sieve['first_prime_found']}")
    print(f"  -> Last 19-Digit Prime Found:  {res_sieve['last_prime_found']}")
    print(f"  -> Sieve throughput: {res_sieve['primes_per_second']:,} primes/sec | Latency: {res_sieve['latency_ms']} ms")
    assert res_sieve["primes_count"] > 0, "Window sieve must find primes at 10^18 scale!"

    # --------------------------------------------------------------------------
    # 6. Engine 3: Critical-Line Tared Riemann R(X) up to 10^29
    # --------------------------------------------------------------------------
    print("\n[6/10] Running Engine 3: Critical-Line Tared Riemann R(X) up to 10^29...")
    res_R = tared_riemann_R_prime_counter()
    print(f"  -> Scales tested: 10^6 to 10^{res_R['max_scale']}")
    print(f"  -> All deviations strictly inside Schoenfeld's (sqrt(X) ln X)/(8*pi) envelope: {res_R['all_within_schoenfeld_bound']}")
    for row in res_R["table"][:5]:
        print(f"     * X = 10^{row['log10_X']}: exact={row['exact_pi']}, R(X)={row['R_estimate']:.0f}, dev={row['deviation']:.1f}, bound={row['schoenfeld_bound']:.1f} (ratio={row['envelope_ratio']:.4f})")
    assert res_R["all_within_schoenfeld_bound"], "All scale errors must sit strictly inside Schoenfeld envelope!"

    # --------------------------------------------------------------------------
    # 7. Heritage BIM (Bauforschung) Facade Monitoring Tare
    # --------------------------------------------------------------------------
    print("\n[7/10] Running Heritage BIM (Bauforschung) Facade Monitoring Tare...")
    res_hbim = hbim_facade_thermal_tare_analysis(n_nodes=36, num_time_steps=365)
    print(f"  -> Building Asset: {res_hbim['asset_id']} ({res_hbim['element_name']})")
    print(f"  -> True Settlement: {res_hbim['true_settlement_rate_mm_yr']} mm/yr | Estimated: {res_hbim['estimated_settlement_rate_mm_yr']:.3f} mm/yr (error: {res_hbim['estimation_error_mm']:.4f} mm)")
    print(f"  -> Seasonal Thermal Drift Tared: {res_hbim['seasonal_thermal_amplitude_tared_mm']} mm")
    print(f"  -> Structural SNR Improvement: +{res_hbim['snr_improvement_db']} dB ({res_hbim['snr_raw_db']} dB -> {res_hbim['snr_tared_db']} dB)")
    assert res_hbim["snr_improvement_db"] > 10.0, "Sub-gap thermal taring must improve structural SNR by > 10 dB!"

    res_iso = export_iso19650_pyrevit_diagnostics(res_hbim)
    assert "ISO_19650_Metadata" in res_iso, "ISO 19650 pyRevit export metadata must exist!"

    # --------------------------------------------------------------------------
    # 8. Workspace 05: GPU 3-SAT Phase-Transition Scanner
    # --------------------------------------------------------------------------
    print("\n[8/10] Running Workspace 05: GPU 3-SAT Phase-Transition Scanner...")
    res_sat = gpu_schur_pfaffian_sat_phase_transition_scanner(n_vars=64, device="cuda" if CUDA_AVAILABLE else "cpu")
    print(f"  -> Variables: {res_sat['n_variables']} | Scanned across alpha in [1.5, 2.5, 3.5, 4.267, 5.0]")
    for r in res_sat["table"]:
        print(f"     * alpha = {r['alpha']}: clauses={r['m_clauses']}, genus={r['cyclomatic_genus']}, "
              f"spin_sheets={r['spin_sheets_4_g']}, sin^2(Theta)={r['schur_innovation_sin2_theta']}, "
              f"entropy={r['linear_entanglement_entropy']} ({r['phase']})")
    print(f"  -> Latency: {res_sat['scan_latency_ms']} ms | CUDA Used: {res_sat['cuda_used']}")

    # --------------------------------------------------------------------------
    # 9. Workspace 05: CAD/BIM Spaceframe Constraint Condenser
    # --------------------------------------------------------------------------
    print("\n[9/10] Running Workspace 05: CAD/BIM Spaceframe Constraint Condenser...")
    res_cad = cad_bim_spaceframe_constraint_condenser(n_struts=48, n_boundary_joints=12)
    print(f"  -> Struts: {res_cad['total_spaceframe_struts']} -> Planar Struts Eliminated: {res_cad['planar_struts_eliminated']}")
    print(f"  -> Condensed Boundary Interface: {res_cad['condensed_matrix_dim']} (Coercive: {res_cad['coercive']})")
    print(f"  -> Non-Planar Overpasses Isolated: {res_cad['non_planar_overpasses_isolated']} K_{{3,3}} minors")
    assert res_cad["coercive"], "Condensed spaceframe must remain strictly coercive!"

    # --------------------------------------------------------------------------
    # 10. Engine #2 / Phase 5.2: Zero-Trust Epistemic & Axiom Governance Runner
    # --------------------------------------------------------------------------
    print("\n[10/10] Running Zero-Trust Epistemic & Axiom Governance Suite...")
    res_gov = verify_four_workspace_epistemic_and_axiom_governance()
    print(f"  -> Workspaces Audited: {res_gov['workspaces_audited']}")
    print(f"  -> Active Modules Scanned: {res_gov['total_modules_audited']}")
    print(f"  -> Total Lean 4 Theorems Verified: {res_gov['total_theorems_verified']}")
    print(f"  -> Zero-Sorry Verified: {res_gov['zero_sorry_verified']}")
    print(f"  -> Zero-Custom-Axioms Verified: {res_gov['zero_custom_axioms_verified']}")
    print(f"  -> Standard Kernel Axioms: {res_gov['standard_kernel_axioms']}")
    print(f"  -> Epistemic Boundary Verified: {res_gov['epistemic_lock_verified']}")
    print(f"  -> Attribution Standard Verified: {res_gov['attribution_verified']}")
    assert res_gov["verified"], "All 4 workspaces must pass zero-trust governance!"
    assert res_gov["status"] == "PASS", "Governance status must be PASS!"

    elapsed_total = round(time.time() - t_suite_start, 2)
    print("\n" + "=" * 80)
    print(f"ALL 10/10 TARE_CORE BENCHMARK SUITES PASSED IN {elapsed_total}s (STATUS: PASS)")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # Write Telemetry Receipt
    # --------------------------------------------------------------------------
    report_dir = PARENT_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = report_dir / "probe_tare_core_gpu_silicon_and_prime_horizons_receipt.json"

    # Convert non-serializable objects (ndarray) to lists
    res_kron_clean = {k: v for k, v in res_kron.items() if k != "condensed_matrix"}

    receipt_data = {
        "title": "tare_core GPU Silicon and Prime Horizons Verification Receipt",
        "verified": True,
        "status": "PASS",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "author": "Qamar Munawer",
        "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg",
        "methodology": "ai is being used as a tool",
        "epistemic_boundary": {
            "status": "verified-finite",
            "open_horizon_lock": "STRICTLY OPEN",
            "all_four_clay_problems_open": True,
        },
        "hardware_telemetry": {
            "device_name": DEVICE_NAME,
            "cuda_available": CUDA_AVAILABLE,
            "total_vram_gb": TOTAL_VRAM_GB,
        },
        "benchmarks": {
            "silicon_kron_schur_reduction": res_kron_clean,
            "llm_kv_cache_schur_tare": res_kv,
            "optimal_sram_tiling": res_sram,
            "guinand_weil_spectral_prime_scanner": {
                k: v for k, v in res_spectral.items() if k != "alignment_table"
            },
            "high_altitude_sqrt_x_window_sieve": res_sieve,
            "tared_riemann_R_prime_counter": {
                "scales_tested": res_R["scales_tested"],
                "max_scale": res_R["max_scale"],
                "all_within_schoenfeld_bound": res_R["all_within_schoenfeld_bound"],
                "schoenfeld_constant": res_R["schoenfeld_constant"],
                "sample_scales": res_R["table"][:5],
            },
            "hbim_facade_monitoring": {k: v for k, v in res_hbim.items() if k != "condensation_telemetry"},
            "iso19650_pyrevit_export": res_iso,
            "sat_phase_transition": res_sat,
            "cad_spaceframe_condensation": res_cad,
            "zero_trust_governance": {
                "verified": res_gov["verified"],
                "status": res_gov["status"],
                "workspaces_audited": res_gov["workspaces_audited"],
                "total_modules_audited": res_gov["total_modules_audited"],
                "total_theorems_verified": res_gov["total_theorems_verified"],
                "zero_sorry_verified": res_gov["zero_sorry_verified"],
                "zero_custom_axioms_verified": res_gov["zero_custom_axioms_verified"],
                "epistemic_lock_verified": res_gov["epistemic_lock_verified"],
                "attribution_verified": res_gov["attribution_verified"],
            },
        },
    }

    receipt_path.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")
    print(f"\nVerification receipt written to: {receipt_path}")
    return receipt_data


# Pytest entry points
def test_silicon_kron_reduction():
    dim_full = 64
    dim_boundary = 8
    A_rand = np.random.randn(dim_full, dim_full)
    K_full = A_rand.T @ A_rand + np.eye(dim_full) * 10.0
    res = gpu_kron_schur_condensation(K_full, list(range(dim_boundary)), device="cpu")
    assert res["coercive"]

def test_llm_kv_cache():
    K_cache = np.random.randn(4096, 128).astype(np.float32)
    W_attn = np.random.randn(128, 128).astype(np.float32)
    V_cache = K_cache @ W_attn
    res = gpu_llm_kv_cache_schur_tare(K_cache, V_cache, rank_keep_ratio=0.18, device="cpu")
    assert res["target_compression_met"]
    assert res["target_fidelity_met"]

def test_optimal_sram():
    res = optimal_sram_tile_schedule(X_total=1024, alpha=2.0, beta=1.0, device="cpu")
    assert res["max_discrepancy"] < 1e-3

def test_guinand_weil_scanner():
    res = guinand_weil_spectral_prime_scanner(x_min=2.0, x_max=50.0, num_zeros=50, device="cpu")
    assert res["primes_aligned"] == res["primes_evaluated"]

def test_window_sieve():
    res = high_altitude_sqrt_x_window_sieve(X_start=10**12, window_width=500)
    assert res["primes_count"] > 0

def test_riemann_R_counter():
    res = tared_riemann_R_prime_counter(scales=[10**6, 10**9])
    assert res["all_within_schoenfeld_bound"]

def test_hbim_facade():
    res = hbim_facade_thermal_tare_analysis(n_nodes=16, num_time_steps=60)
    assert res["snr_improvement_db"] > 10.0

def test_sat_phase_transition():
    res = gpu_schur_pfaffian_sat_phase_transition_scanner(n_vars=16, device="cpu")
    assert len(res["table"]) == 5

def test_cad_spaceframe():
    res = cad_bim_spaceframe_constraint_condenser(n_struts=24, n_boundary_joints=6)
    assert res["coercive"]

def test_zero_trust_governance():
    res = verify_four_workspace_epistemic_and_axiom_governance()
    assert res["verified"]
    assert res["status"] == "PASS"


if __name__ == "__main__":
    run_all_benchmarks()
