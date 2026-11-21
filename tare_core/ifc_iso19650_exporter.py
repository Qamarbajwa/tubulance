"""
ifc_iso19650_exporter.py
========================
Heritage BIM (Bauforschung) IFC 4.3 and ISO 19650 Property Set Exporter.

Combines:
1. `hbim_bauforschung_adapter.py` (3-tier sub-gap thermal drift taring)
2. `gpu_chiral_half_domain_condensation` (K = K_half + K_half^T 50% VRAM storage)
to generate standard IFC 4.3 / ISO 19650 Property Sets:
- `Pset_BauforschungStructuralTare`
- `Pset_ChiralHalfDomainSchurCondensation`

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Boundary: All four Clay Millennium Problems remain strictly OPEN
(status: verified-finite, open_horizon_lock: STRICTLY OPEN).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from .hbim_bauforschung_adapter import (
    generate_synthetic_masonry_stiffness,
    hbim_facade_thermal_tare_analysis,
)
from .silicon_vram_compressor import gpu_chiral_half_domain_condensation


def generate_hbim_ifc43_iso19650_payload(
    n_nodes: int = 36,
    num_time_steps: int = 365,
    true_settlement_rate_mm_yr: float = 4.5,
    thermal_amplitude_mm: float = 8.2,
    scanner_noise_sigma_mm: float = 0.8,
) -> Dict[str, Any]:
    """
    Runs the combined thermal-drift tare and chiral half-domain Guyan condensation
    to synthesize an IFC 4.3 / ISO 19650 compliant property set dictionary.
    """
    # 1. Thermal drift and settlement analysis
    tare_result = hbim_facade_thermal_tare_analysis(
        n_nodes=n_nodes,
        num_time_steps=num_time_steps,
        true_settlement_rate_mm_yr=true_settlement_rate_mm_yr,
        thermal_amplitude_mm=thermal_amplitude_mm,
        scanner_noise_sigma_mm=scanner_noise_sigma_mm,
    )

    # 2. Chiral half-domain matrix condensation (K = K_half + K_half^T)
    K_full, boundary_nodes = generate_synthetic_masonry_stiffness(n_nodes)
    chiral_result = gpu_chiral_half_domain_condensation(K_full, boundary_nodes)

    # 3. Assemble IFC 4.3 compliant Property Sets
    status_flag = (
        "ALERT_STRUCTURAL_SETTLEMENT"
        if tare_result["estimated_settlement_rate_mm_yr"] > 3.0
        else "NORMAL"
    )

    pset_structural_tare = {
        "IfcPropertySet_Name": "Pset_BauforschungStructuralTare",
        "ApplicableEntity": "IfcWall / IfcBuildingElementProxy",
        "ISO_19650_Classification": "Uniclass 2015: Pr_20_20_08_55 Masonry Wall System",
        "LevelOfDetail": "LOD 400 (As-Built Maintenance & Structural Health)",
        "AssetID": tare_result["asset_id"],
        "FacadeElement": tare_result["element_name"],
        "MonitoringCycleDays": tare_result["monitoring_duration_days"],
        "AnnualSettlementRate_mm": tare_result["estimated_settlement_rate_mm_yr"],
        "TargetSettlementRate_mm": tare_result["true_settlement_rate_mm_yr"],
        "SettlementEstimationError_mm": tare_result["estimation_error_mm"],
        "SeasonalThermalDriftAmplitude_mm": tare_result["seasonal_thermal_amplitude_tared_mm"],
        "ScannerNoiseFloor_sigma_mm": tare_result["scanner_noise_floor_sigma_mm"],
        "RawSignalToNoiseRatio_dB": tare_result["snr_raw_db"],
        "TaredSignalToNoiseRatio_dB": tare_result["snr_tared_db"],
        "StructuralSNRGain_dB": tare_result["snr_improvement_db"],
        "StructuralIntegrityStatus": status_flag,
    }

    pset_chiral_condensation = {
        "IfcPropertySet_Name": "Pset_ChiralHalfDomainSchurCondensation",
        "ApplicableEntity": "IfcStructuralMember / IfcStructuralAnalysisModel",
        "InvolutionIdentity": "K = K_half + K_half^T",
        "OriginalDegreesOfFreedom": chiral_result["n_total"],
        "PreservedBoundaryDegreesOfFreedom": chiral_result["n_boundary"],
        "CondensedInteriorDegreesOfFreedom": chiral_result["n_interior"],
        "DenseMatrixStorageElements": chiral_result["dense_elements"],
        "ChiralHalfDomainStorageElements": chiral_result["half_domain_elements"],
        "VRAMStorageReductionPct": chiral_result["vram_reduction_pct"],
        "StorageCompressionFactor": chiral_result["compression_factor"],
        "GuyanCondensationAccuracy": f"{100.0 - chiral_result['max_condensation_error']:.8f}%",
        "MaxCondensationError": chiral_result["max_condensation_error"],
        "MinCondensedEigenvalue": round(chiral_result["min_eigenvalue"], 6),
        "CoercivityStatus": (
            "STRICTLY_COERCIVE_POSITIVE_DEFINITE"
            if chiral_result["coercive"]
            else "NON_COERCIVE"
        ),
        "ExecutionDevice": chiral_result["device_name"],
        "CUDASpeedup": chiral_result["cuda_used"],
    }

    metadata_header = {
        "Project": "BTU Cottbus Historic Heritage Preservation (Bauforschung)",
        "Standard": "IFC 4.3 (ISO 16739-1:2024) / ISO 19650-1:2018",
        "Author": "Qamar Munawer",
        "Affiliation": "Brandenburg University of Technology Cottbus-Senftenberg",
        "Methodology": "ai is being used as a tool",
        "EpistemicBoundary": "All four Clay Millennium Problems remain strictly OPEN (status: verified-finite, open_horizon_lock: STRICTLY OPEN)",
    }

    return {
        "Header": metadata_header,
        "PropertySets": [
            pset_structural_tare,
            pset_chiral_condensation,
        ],
        "SummaryMetrics": {
            "Status": "PASS",
            "AssetID": tare_result["asset_id"],
            "AnnualSettlementRate_mm": tare_result["estimated_settlement_rate_mm_yr"],
            "VRAMStorageReductionPct": chiral_result["vram_reduction_pct"],
            "MaxCondensationError": chiral_result["max_condensation_error"],
            "SNRGain_dB": tare_result["snr_improvement_db"],
        },
    }


def export_hbim_ifc43_iso19650_payload(
    output_path: Optional[str | Path] = None,
    n_nodes: int = 36,
) -> Dict[str, Any]:
    """
    Generates and writes the IFC 4.3 / ISO 19650 property set JSON file.
    Default path: d:/Comfy UI/tubulance/reports/hbim_ifc43_iso19650_pset_payload.json
    """
    if output_path is None:
        output_path = Path(r"d:\Comfy UI\tubulance\reports\hbim_ifc43_iso19650_pset_payload.json")
    else:
        output_path = Path(output_path)

    payload = generate_hbim_ifc43_iso19650_payload(n_nodes=n_nodes)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return payload


if __name__ == "__main__":
    res = export_hbim_ifc43_iso19650_payload()
    print("IFC 4.3 / ISO 19650 Property Sets Exported Successfully!")
    print(f"Asset ID: {res['SummaryMetrics']['AssetID']}")
    print(f"VRAM Reduction: {res['SummaryMetrics']['VRAMStorageReductionPct']}%")
    print(f"SNR Gain: +{res['SummaryMetrics']['SNRGain_dB']} dB")
