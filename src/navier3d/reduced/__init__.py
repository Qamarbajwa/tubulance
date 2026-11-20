"""Reduced-Order Model (ROM) Sub-Package for navier3d.

Provides:
- SolenoidalModalBasis: Abstract base class for divergence-free vector bases.
- FourierSolenoidalBasis: Fourier standing-wave solenoidal basis on 3D periodic domains.
- PODSolenoidalBasis: Snapshot Proper Orthogonal Decomposition (POD) solenoidal basis.
- SparseModalTensor: Sparse quadratic mode interaction tensor Q_kij.
- evaluate_pseudospectral_convection: Grid-based non-linear modal evaluation.
- ModalODEIntegrator: Time-stepping integrator in modal coefficient space.
- ModalStepDiagnostics: Step diagnostic container for modal simulations.
"""
from __future__ import annotations

from .solenoidal_basis import SolenoidalModalBasis, FourierSolenoidalBasis, PODSolenoidalBasis, mac_to_cell_centers, cell_centers_to_mac
from .modal_tensor import SparseModalTensor, evaluate_pseudospectral_convection, compute_mode_gradient
from .modal_integrator import ModalODEIntegrator, ModalStepDiagnostics
from .w2_diagnostics import (
    separate_representation_and_evolution_error,
    taylor_green_analytical_projection_test,
    mac_phase_shift_audit,
    round_trip_reconstruction_test,
    convection_operator_comparison,
    triad_completeness_metric,
    exact_closure_residual,
    energy_flux_discarded_modes,
    mac_velocity_norm,
    mac_velocity_diff_norm,
)
from .discrete_galerkin import DiscreteOperatorGalerkinROM
from .modal_closure import fit_modal_eddy_viscosity, ClosedModalODEIntegrator
from .pod_ensemble import EnsemblePODSolenoidalBasis, HybridSolenoidalBasis
from .w3_generalization import (
    train_val_test_split,
    evaluate_out_of_sample_generalization,
    evaluate_perturbed_ic_sensitivity,
    evaluate_turbulence_statistics_and_flux,
)
from .adaptive_rom import AdaptiveSolenoidalROM, OnlineClosureErrorEstimator, AdaptiveEnrichedROM
from .spectral_analysis import effective_pod_eigenvalues, mode_frequency_analysis
from .w4_diagnostics import (
    diagnose_representation_vs_evolution,
    subspace_distance_metric,
    optimal_translation_alignment,
    fourier_phase_amplitude_decomposition,
)
from .adaptive_fourier_basis import AdaptiveFourierSolenoidalBasis
from .clustered_pod_basis import ClusteredLocalPODBasis
from .sparse_triad_engine import MinimalSpectralGridEvaluator, SparseTriadGraph, VectorizedTriadEvaluator
from .integrating_factor_integrator import IntegratingFactorModalODEIntegrator
from .w5_optimization import profile_rom_components, measure_triad_interaction_counts, build_pareto_frontier
from .w6_validation import (
    audit_working_set_memory,
    evaluate_enstrophy_and_flux_cascade,
    run_unified_accuracy_speed_benchmark,
    run_multi_seed_robustness_suite,
)
from .w7_hybrid_ablation import (
    OntheFlyFFTEvaluator,
    run_w6_reconciliation_sweep_24,
    EulerianLagrangianWaveHybridSolver,
    evaluate_ablation_candidate,
)
from .stokes_eigenbasis import StokesEigenbasis3D
from .w8_stokes_rom import (
    MatrixFreeStokesConvectionEvaluator,
    StokesEigenmodeODEIntegrator,
    evaluate_wall_shear_and_boundary_error,
    run_stokes_vs_pod_generalization_benchmark,
)
from .w13_multiscale_capacity import ExtendedAnisotropicEigenwaveBasis, run_w13_primary_rank_sweep, run_w13_candidate_scorecard
from .w13r_reconciliation import (
    NonorthogonalProjectionSolver,
    ExtendedGlobalOracleEngine,
    W13GDenseSamplingEngine,
    CandidateG4EnsembleEngine,
    SparsificationEngine,
    SeparateHoldoutEvaluator,
    run_w13r_full_reconciliation,
)

__all__ = [
    "SolenoidalModalBasis",
    "FourierSolenoidalBasis",
    "PODSolenoidalBasis",
    "mac_to_cell_centers",
    "cell_centers_to_mac",
    "SparseModalTensor",
    "evaluate_pseudospectral_convection",
    "compute_mode_gradient",
    "ModalODEIntegrator",
    "ModalStepDiagnostics",
    "separate_representation_and_evolution_error",
    "taylor_green_analytical_projection_test",
    "mac_phase_shift_audit",
    "round_trip_reconstruction_test",
    "convection_operator_comparison",
    "triad_completeness_metric",
    "exact_closure_residual",
    "energy_flux_discarded_modes",
    "DiscreteOperatorGalerkinROM",
    "fit_modal_eddy_viscosity",
    "ClosedModalODEIntegrator",
    "EnsemblePODSolenoidalBasis",
    "HybridSolenoidalBasis",
    "train_val_test_split",
    "evaluate_out_of_sample_generalization",
    "evaluate_perturbed_ic_sensitivity",
    "evaluate_turbulence_statistics_and_flux",
    "AdaptiveSolenoidalROM",
    "OnlineClosureErrorEstimator",
    "AdaptiveEnrichedROM",
    "effective_pod_eigenvalues",
    "mode_frequency_analysis",
    "diagnose_representation_vs_evolution",
    "subspace_distance_metric",
    "optimal_translation_alignment",
    "fourier_phase_amplitude_decomposition",
    "AdaptiveFourierSolenoidalBasis",
    "ClusteredLocalPODBasis",
    "MinimalSpectralGridEvaluator",
    "SparseTriadGraph",
    "VectorizedTriadEvaluator",
    "IntegratingFactorModalODEIntegrator",
    "profile_rom_components",
    "measure_triad_interaction_counts",
    "build_pareto_frontier",
    "audit_working_set_memory",
    "evaluate_enstrophy_and_flux_cascade",
    "run_unified_accuracy_speed_benchmark",
    "run_multi_seed_robustness_suite",
    "OntheFlyFFTEvaluator",
    "run_w6_reconciliation_sweep_24",
    "EulerianLagrangianWaveHybridSolver",
    "evaluate_ablation_candidate",
    "StokesEigenbasis3D",
    "MatrixFreeStokesConvectionEvaluator",
    "StokesEigenmodeODEIntegrator",
    "evaluate_wall_shear_and_boundary_error",
    "run_stokes_vs_pod_generalization_benchmark",
    "BoundaryLayerDiagnostics",
    "DerivativeWeightedStokesBasis",
    "SeparableChannelEigenbasis",
    "ResolventResponseBasis",
    "evaluate_w9_candidate_gate",
    "ExtendedAnisotropicEigenwaveBasis",
    "run_w13_primary_rank_sweep",
    "run_w13_candidate_scorecard",
    "NonorthogonalProjectionSolver",
    "ExtendedGlobalOracleEngine",
    "W13GDenseSamplingEngine",
    "CandidateG4EnsembleEngine",
    "SparsificationEngine",
    "SeparateHoldoutEvaluator",
    "run_w13r_full_reconciliation",
]
