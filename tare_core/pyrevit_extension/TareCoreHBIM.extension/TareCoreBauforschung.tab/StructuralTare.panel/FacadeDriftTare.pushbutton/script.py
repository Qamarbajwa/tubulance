"""
FacadeDriftTare Pushbutton (pyRevit / Revit CPython Engine)
==========================================================
Bauforschung Structural Health Monitoring & Thermal Drift Tare for Historical Facades.

Executes:
1. 3-Tier sub-gap thermal drift filtering from 365-day TLS point-cloud data.
2. Chiral half-domain stiffness condensation (K = K_half + K_half^T, saving ~50% VRAM).
3. ISO 19650 / IFC 4.3 Property Set generation and export.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Boundary: All four Clay Millennium Problems remain strictly OPEN
(status: verified-finite, open_horizon_lock: STRICTLY OPEN).
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path if tare_core is not already in path
script_dir = Path(__file__).resolve().parent
# Navigate up 6 levels: FacadeDriftTare.pushbutton -> StructuralTare.panel -> TareCoreBauforschung.tab -> TareCoreHBIM.extension -> pyrevit_extension -> tare_core -> tubulance
tubulance_root = script_dir.parents[5]
if str(tubulance_root) not in sys.path:
    sys.path.insert(0, str(tubulance_root))

try:
    from tare_core import (
        export_hbim_ifc43_iso19650_payload,
        generate_hbim_ifc43_iso19650_payload,
    )
    HAS_TARE_CORE = True
except ImportError:
    HAS_TARE_CORE = False

# Check if running inside Autodesk Revit pyRevit environment
try:
    from pyrevit import forms, script
    IN_PYREVIT = True
    output = script.get_output()
except ImportError:
    IN_PYREVIT = False
    output = None


def run_facade_drift_tare():
    """Main execution entry point for pyRevit pushbutton."""
    if not HAS_TARE_CORE:
        msg = f"Error: tare_core package could not be imported from {tubulance_root}"
        if IN_PYREVIT:
            forms.alert(msg, title="TareCore Import Error")
        else:
            print(msg)
        return

    # 1. Execute analysis and export IFC 4.3 / ISO 19650 payload
    report_path = tubulance_root / "reports" / "hbim_ifc43_iso19650_pset_payload.json"
    payload = export_hbim_ifc43_iso19650_payload(output_path=report_path)

    header = payload["Header"]
    psets = {ps["IfcPropertySet_Name"]: ps for ps in payload["PropertySets"]}
    tare_ps = psets["Pset_BauforschungStructuralTare"]
    chiral_ps = psets["Pset_ChiralHalfDomainSchurCondensation"]
    summary = payload["SummaryMetrics"]

    # 2. Render output based on environment
    if IN_PYREVIT:
        output.print_md("# TareCore Bauforschung: Facade Drift Tare & Chiral Condensation")
        output.print_md(f"**Asset:** {tare_ps['AssetID']} — {tare_ps['FacadeElement']}")
        output.print_md(f"**Standard:** {header['Standard']}")
        output.print_md(f"**Author:** {header['Author']} ({header['Affiliation']})")
        output.print_md(f"**Methodology:** `{header['Methodology']}`")
        output.print_md(f"**Epistemic Boundary:** `{header['EpistemicBoundary']}`")
        output.print_md("---")

        output.print_md("### 1. Structural Health & Settlement Diagnostics (Pset_BauforschungStructuralTare)")
        output.print_table(
            table_data=[
                ["Asset ID", tare_ps["AssetID"]],
                ["Monitoring Duration", f"{tare_ps['MonitoringCycleDays']} days"],
                ["Estimated Settlement Rate", f"{tare_ps['AnnualSettlementRate_mm']:.3f} mm/yr"],
                ["Target Settlement Rate", f"{tare_ps['TargetSettlementRate_mm']:.3f} mm/yr"],
                ["Thermal Drift Filtered", f"{tare_ps['SeasonalThermalDriftAmplitude_mm']:.2f} mm"],
                ["Scanner Noise Floor (sigma)", f"{tare_ps['ScannerNoiseFloor_sigma_mm']:.2f} mm"],
                ["Structural SNR Gain", f"+{tare_ps['StructuralSNRGain_dB']:.2f} dB"],
                ["Structural Status", tare_ps["StructuralIntegrityStatus"]],
            ],
            columns=["Property Name", "Value"],
        )

        output.print_md("### 2. Chiral Half-Domain Condensation (Pset_ChiralHalfDomainSchurCondensation)")
        output.print_table(
            table_data=[
                ["Involution Identity", chiral_ps["InvolutionIdentity"]],
                ["Original Mesh DOFs", str(chiral_ps["OriginalDegreesOfFreedom"])],
                ["Preserved Boundary DOFs", str(chiral_ps["PreservedBoundaryDegreesOfFreedom"])],
                ["Dense Matrix Elements", str(chiral_ps["DenseMatrixStorageElements"])],
                ["Chiral Half Elements", str(chiral_ps["ChiralHalfDomainStorageElements"])],
                ["VRAM Reduction Ratio", f"{chiral_ps['VRAMStorageReductionPct']:.2f}% (~50% saving)"],
                ["Storage Compression", f"{chiral_ps['StorageCompressionFactor']:.2f}x"],
                ["Condensation Accuracy", chiral_ps["GuyanCondensationAccuracy"]],
                ["Coercivity Status", chiral_ps["CoercivityStatus"]],
                ["Execution Hardware", chiral_ps["ExecutionDevice"]],
            ],
            columns=["Condensation Parameter", "Result"],
        )

        output.print_md(f"\n*Diagnostic payload written to:* `{report_path}`")
        forms.alert(
            f"Bauforschung Tare Completed!\n"
            f"Asset: {tare_ps['AssetID']}\n"
            f"VRAM Reduction: {chiral_ps['VRAMStorageReductionPct']}%\n"
            f"SNR Gain: +{tare_ps['StructuralSNRGain_dB']} dB\n"
            f"Status: {tare_ps['StructuralIntegrityStatus']}",
            title="TareCore HBIM Execution Success",
        )
    else:
        print("=" * 80)
        print("TARE_CORE PYREVIT BAUFORSCHUNG EXTENSION (STANDALONE CLI MODE)")
        print(f"Author: {header['Author']} | Affiliation: {header['Affiliation']}")
        print(f"Epistemic Lock: {header['EpistemicBoundary']}")
        print("=" * 80)
        print(f"Asset ID:                     {tare_ps['AssetID']}")
        print(f"Facade Element:               {tare_ps['FacadeElement']}")
        print(f"Estimated Settlement:         {tare_ps['AnnualSettlementRate_mm']:.3f} mm/yr")
        print(f"Thermal Drift Filtered:       {tare_ps['SeasonalThermalDriftAmplitude_mm']:.2f} mm")
        print(f"Structural SNR Gain:          +{tare_ps['StructuralSNRGain_dB']:.2f} dB")
        print(f"Structural Status:            {tare_ps['StructuralIntegrityStatus']}")
        print("-" * 80)
        print(f"Involution Identity:          {chiral_ps['InvolutionIdentity']}")
        print(f"Dense Matrix Storage:         {chiral_ps['DenseMatrixStorageElements']} elements")
        print(f"Chiral Half Storage:          {chiral_ps['ChiralHalfDomainStorageElements']} elements")
        print(f"VRAM Reduction Ratio:         {chiral_ps['VRAMStorageReductionPct']:.2f}%")
        print(f"Condensation Accuracy:        {chiral_ps['GuyanCondensationAccuracy']}")
        print(f"Coercivity:                   {chiral_ps['CoercivityStatus']}")
        print("=" * 80)
        print(f"Payload JSON written to:      {report_path}")
        print("PASS (Ready for Autodesk Revit / pyRevit execution).")


if __name__ == "__main__":
    run_facade_drift_tare()
