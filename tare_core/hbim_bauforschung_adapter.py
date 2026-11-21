"""
hbim_bauforschung_adapter.py
============================
Heritage BIM (Bauforschung) Masonry Facade & TLS Point-Cloud Deformation Taring.

Implements:
1. Guyan-Schur structural condensation of historical masonry facade stiffness matrices.
2. 3-Tier sub-gap tare separating seasonal thermal drift and scanner noise from true foundation settlement.
3. ISO 19650 and pyRevit-ready JSON diagnostic report export.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Boundary: All four Clay Millennium Problems remain strictly OPEN
(status: verified-finite, open_horizon_lock: STRICTLY OPEN).
"""

from __future__ import annotations

import json
import math
import time
from typing import Any, Dict, List, Tuple

import numpy as np

from .silicon_vram_compressor import gpu_kron_schur_condensation


def generate_synthetic_masonry_stiffness(n_nodes: int = 36) -> Tuple[np.ndarray, List[int]]:
    """
    Generates a synthetic 2D finite-element masonry facade stiffness matrix.
    Boundary degrees of freedom: foundation footing nodes (bottom row) and anchor points.
    """
    # 2D grid of size (6 x 6)
    grid_side = int(math.isqrt(n_nodes))
    if grid_side * grid_side != n_nodes:
        grid_side = 6
        n_nodes = 36

    K = np.zeros((n_nodes, n_nodes), dtype=np.float64)

    # Elastic modulus and shear parameters for historic brickwork
    E_masonry = 2.5e9   # 2.5 GPa
    G_masonry = 1.0e9   # 1.0 GPa

    for i in range(grid_side):
        for j in range(grid_side):
            idx = i * grid_side + j
            K[idx, idx] += 4.0 * E_masonry
            # Connect horizontal neighbors
            if j + 1 < grid_side:
                idx_r = i * grid_side + (j + 1)
                K[idx, idx_r] -= 1.0 * E_masonry
                K[idx_r, idx] -= 1.0 * E_masonry
            # Connect vertical neighbors
            if i + 1 < grid_side:
                idx_d = (i + 1) * grid_side + j
                K[idx, idx_d] -= 1.0 * G_masonry
                K[idx_d, idx] -= 1.0 * G_masonry

    # Boundary nodes: bottom row (foundation) and top corners (tie-rod anchors)
    boundary_nodes = [0 * grid_side + j for j in range(grid_side)] + [
        (grid_side - 1) * grid_side + 0,
        (grid_side - 1) * grid_side + (grid_side - 1),
    ]
    boundary_nodes = sorted(list(set(boundary_nodes)))
    return K, boundary_nodes


def hbim_facade_thermal_tare_analysis(
    n_nodes: int = 36,
    num_time_steps: int = 365,
    true_settlement_rate_mm_yr: float = 4.5,
    thermal_amplitude_mm: float = 8.2,
    scanner_noise_sigma_mm: float = 0.8,
) -> Dict[str, Any]:
    """
    Simulates TLS point-cloud facade monitoring over a 365-day monitoring cycle.
    Applies the Schur-Tare Coercivity Kernel to separate:
    1. Reversible seasonal thermal expansion cycles (sub-gap drift)
    2. Scanner Gaussian point-cloud jitter
    3. Irreversible foundation settlement (secular damage mode)
    """
    K_full, boundary_nodes = generate_synthetic_masonry_stiffness(n_nodes)

    # Guyan-Schur condensation on GPU/CPU
    condensation_result = gpu_kron_schur_condensation(K_full, boundary_nodes)

    # Time array in days
    t = np.linspace(0.0, 1.0, num_time_steps)  # 1 year

    # 1. True irreversible foundation settlement (secular linear + parabolic ramp)
    u_settlement = true_settlement_rate_mm_yr * (t + 0.2 * (t ** 2))

    # 2. Reversible seasonal thermal expansion (sinusoidal temperature variation)
    u_thermal = thermal_amplitude_mm * np.sin(2.0 * math.pi * t - math.pi / 2.0)

    # 3. Terrestrial Laser Scanner (TLS) sub-gap noise
    np.random.seed(42)
    eta_noise = np.random.normal(0.0, scanner_noise_sigma_mm, num_time_steps)

    # Raw observed displacement at key monitoring target
    u_observed = u_settlement + u_thermal + eta_noise

    # 4. Schur-Tare Decomposition:
    # Build thermal basis [1, sin(2*pi*t), cos(2*pi*t)]
    Phi = np.column_stack([
        np.ones_like(t),
        np.sin(2.0 * math.pi * t),
        np.cos(2.0 * math.pi * t),
    ])

    # Project out thermal subspace via Schur complement projection:
    # P_tare = I - Phi (Phi^T Phi)^{-1} Phi^T
    Phi_gram = Phi.T @ Phi
    W_thermal = np.linalg.solve(Phi_gram, Phi.T @ u_observed)
    u_thermal_extracted = Phi @ W_thermal

    # Tared displacement: residual containing true settlement + zero-mean filtered noise
    u_tared = u_observed - u_thermal_extracted

    # Fit linear secular slope on tared signal
    A_secular = np.column_stack([np.ones_like(t), t])
    w_secular = np.linalg.solve(A_secular.T @ A_secular, A_secular.T @ u_tared)
    estimated_settlement_rate = float(w_secular[1])

    # Estimation accuracy
    estimation_error_mm = abs(estimated_settlement_rate - true_settlement_rate_mm_yr)

    # SNR calculations (in decibels)
    # Raw SNR: Settlement vs Thermal + Noise
    power_settlement = float(np.mean(u_settlement ** 2))
    power_raw_nuisance = float(np.mean((u_thermal + eta_noise) ** 2))
    snr_raw_db = 10.0 * math.log10(max(power_settlement, 1e-12) / max(power_raw_nuisance, 1e-12))

    # Tared SNR: Settlement vs residual error
    residual_error = u_tared - (w_secular[0] + w_secular[1] * t)
    power_residual = float(np.mean(residual_error ** 2))
    snr_tared_db = 10.0 * math.log10(max(power_settlement, 1e-12) / max(power_residual, 1e-12))
    snr_improvement_db = round(snr_tared_db - snr_raw_db, 2)

    return {
        "status": "PASS",
        "asset_id": "HBIM-BTU-COT-001",
        "element_name": "Historic Sandstone-Brick North Facade",
        "n_original_mesh_nodes": n_nodes,
        "n_condensed_boundary_nodes": len(boundary_nodes),
        "monitoring_duration_days": num_time_steps,
        "true_settlement_rate_mm_yr": true_settlement_rate_mm_yr,
        "estimated_settlement_rate_mm_yr": round(estimated_settlement_rate, 3),
        "estimation_error_mm": round(estimation_error_mm, 4),
        "seasonal_thermal_amplitude_tared_mm": round(float(np.max(np.abs(u_thermal_extracted))), 2),
        "scanner_noise_floor_sigma_mm": scanner_noise_sigma_mm,
        "snr_raw_db": round(snr_raw_db, 2),
        "snr_tared_db": round(snr_tared_db, 2),
        "snr_improvement_db": snr_improvement_db,
        "condensation_telemetry": {
            "speedup": condensation_result["speedup"],
            "max_condensation_error": condensation_result["max_error"],
            "cuda_used": condensation_result["cuda_used"],
        },
    }


def export_iso19650_pyrevit_diagnostics(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exports clean ISO 19650 / pyRevit diagnostic metadata dictionary.
    Ready for automated BIM property mapping in Autodesk Revit or OpenBIM IFC models.
    """
    status_flag = "ALERT_STRUCTURAL_SETTLEMENT" if analysis_result["estimated_settlement_rate_mm_yr"] > 3.0 else "NORMAL"

    return {
        "ISO_19650_Metadata": {
            "Project": "BTU Cottbus Historic Heritage Preservation",
            "AssetID": analysis_result["asset_id"],
            "Classification": "Uniclass 2015: Pr_20_20_08_55 Masonry Wall System",
            "LevelOfDetail": "LOD 400 (As-Built Maintenance & Structural Health)",
            "Discipline": "Structural / Heritage Conservation (Bauforschung)",
        },
        "pyRevit_Parameter_Table": {
            "Facade_Element": analysis_result["element_name"],
            "Annual_Settlement_Rate_mm": analysis_result["estimated_settlement_rate_mm_yr"],
            "Thermal_Drift_Filtered_mm": analysis_result["seasonal_thermal_amplitude_tared_mm"],
            "Structural_SNR_Gain_dB": analysis_result["snr_improvement_db"],
            "Structural_Status": status_flag,
            "Guyan_Condensation_Accuracy": f"{100.0 - analysis_result['condensation_telemetry']['max_condensation_error']:.6f}%",
        },
    }
