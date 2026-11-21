"""
tare_core: The Schur-Tare Coercivity Kernel
===========================================
PyTorch CUDA and high-performance numerical kernel for:
1. Guyan-Schur / Kron structural condensation and LLM KV-cache VRAM compression
2. Guinand-Weil spectral prime scanning and high-altitude prime sieving up to 10^18 - 10^29
3. Heritage BIM (Bauforschung) masonry facade deformation and sub-gap thermal drift taring
4. Zero-Trust neuro-symbolic multi-agent Lean 4 epistemic and axiom governance runner

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Boundary: All four Clay Millennium Problems remain strictly OPEN
(status: verified-finite, open_horizon_lock: STRICTLY OPEN).
"""

from .silicon_vram_compressor import (
    gpu_kron_schur_condensation,
    gpu_chiral_half_domain_condensation,
    gpu_yang_mills_chiral_two_halves_orthogonality_probe,
    gpu_llm_kv_cache_schur_tare,
    optimal_sram_tile_schedule,
)
from .prime_horizon_gpu import (
    guinand_weil_spectral_prime_scanner,
    high_altitude_sqrt_x_window_sieve,
    tared_riemann_R_prime_counter,
)
from .hbim_bauforschung_adapter import (
    hbim_facade_thermal_tare_analysis,
    export_iso19650_pyrevit_diagnostics,
)
from .ifc_iso19650_exporter import (
    generate_hbim_ifc43_iso19650_payload,
    export_hbim_ifc43_iso19650_payload,
)
from .p_vs_np_sat_entanglement import (
    gpu_schur_pfaffian_sat_phase_transition_scanner,
    cad_bim_spaceframe_constraint_condenser,
)
from .zero_trust_governance_runner import (
    verify_four_workspace_epistemic_and_axiom_governance,
)

__version__ = "2.0.0-gpu"
__all__ = [
    "gpu_kron_schur_condensation",
    "gpu_chiral_half_domain_condensation",
    "gpu_yang_mills_chiral_two_halves_orthogonality_probe",
    "gpu_llm_kv_cache_schur_tare",
    "optimal_sram_tile_schedule",
    "guinand_weil_spectral_prime_scanner",
    "high_altitude_sqrt_x_window_sieve",
    "tared_riemann_R_prime_counter",
    "hbim_facade_thermal_tare_analysis",
    "export_iso19650_pyrevit_diagnostics",
    "generate_hbim_ifc43_iso19650_payload",
    "export_hbim_ifc43_iso19650_payload",
    "gpu_schur_pfaffian_sat_phase_transition_scanner",
    "cad_bim_spaceframe_constraint_condenser",
    "verify_four_workspace_epistemic_and_axiom_governance",
]
