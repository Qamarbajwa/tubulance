"""navier3d: a modular, general-purpose 3D incompressible Navier-Stokes solver.

Through Milestone 9: package skeleton, configuration system, structured
MAC-grid mesh, staggered field containers, boundary-condition interfaces,
compatible discrete spatial operators, a sparse pressure Poisson system,
velocity projection, and a full unsteady solver for the complete
incompressible Navier-Stokes equations (nonlinear convection, implicit
diffusion, projection) -- with a shared direct/iterative (CG/BiCGSTAB/
GMRES, optional PyAMG) linear-solver backend, an SPD-reduced diffusion
formulation, matrix/preconditioner reuse and warm starts, CFL-driven
adaptive timestepping with variable-step AB2, profiling, and memory
accounting (Milestone 7); selectable non-incremental/incremental/
rotational pressure-correction projection methods with explicit, tested
pressure-vs-pressure-increment boundary condition derivations
(Milestone 8); and now (Milestone 9) a root-cause-isolated,
theta-parametrized pressure-extrapolation fix
(``pressure_extrapolation=True``, opt-in) for the incremental/rotational
predictor's own lagged-pressure temporal-order defect -- proven, not
assumed, to recover clean order-2 velocity convergence at the isolated
predictor level, with a further, honestly-reported, not-yet-fully-
resolved finding that an inconsistent initial pressure combined with a
non-flow-consistent initial condition produces a separate
startup-transient effect in the full pipeline. See docs/architecture.md
for the full design, verification history, and current limitations --
including the explicit restriction against describing any result from
this package as DNS, LES, or RANS.
"""
from __future__ import annotations

from .boundary_conditions import (
    BoundaryConditionError,
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_boundary_conditions,
    apply_pressure_bc,
    apply_velocity_bc,
)
from .config import ConfigError, SimulationConfig
from .fields import FaceField, FlowState, ScalarField, VelocityField
from .mesh import StructuredMesh3D
from .operators import (
    OperatorError,
    divergence,
    gradient,
    scalar_laplacian,
    velocity_laplacian,
)
from .pressure import (
    LinearSolverKind,
    NullSpaceStrategy,
    PressurePoissonSystem,
    PressureSystemError,
    RHSCompatibilityMode,
    SolveDiagnostics,
    compute_initial_pressure,
)
from .projection import (
    ProjectionError,
    ProjectionResult,
    derive_phi_bcs,
    derive_pressure_bcs,
    project,
    project_incremental,
    project_initial_velocity,
)
from .diffusion import DiffusionDiagnostics, DiffusionSystemError, VelocityDiffusionSystem
from .convection import ConvectionError, centered_convection, upwind_convection
from .time_integrators import (
    CFLError,
    IntegrationError,
    IntegratorHistory,
    StepDiagnostics,
    ThetaSchemeIntegrator,
    compute_cfl,
    compute_reynolds,
    run,
)
from .linear_solvers import (
    HAS_PYAMG,
    LinearSolveResult,
    LinearSolver,
    LinearSolverError,
    MatrixKind,
    SolverMethod,
    create_linear_solver,
)
from .adaptive import (
    AdaptiveTimestepController,
    AdaptiveTimestepError,
    DtDecision,
    pressure_extrapolation_coefficients,
    variable_step_ab2_coefficients,
)
from .profiling import ProfileReport, StepProfiler
from .memory import (
    MemoryReport,
    estimate_field_memory,
    estimate_matrix_memory,
    estimate_solver_matrix_memory,
    measure_direct_factorization_memory,
    measure_matrix_memory,
    measure_process_rss_delta,
)
from .decaying_turbulence import generate_matched_solenoidal_fields, generate_solenoidal_random_field
from .filtering import apply_test_filter, compute_germano_tensors, restrict_velocity_fine_to_coarse, spectral_cutoff_filter
from .sgs_apriori import compute_energy_budget, compute_exact_sgs_stress, compute_sgs_apriori_diagnostics, compute_truncation_residuals
from .spectrum import compute_energy_spectrum, verify_parseval_identity
from .strain import compute_strain_components, compute_strain_magnitude
from .turbulence import (
    DynamicSmagorinskyModel,
    LESModel,
    SmagorinskyModel,
    VremanModel,
    WALEModel,
    compute_sgs_mechanical_work,
)
from .corrections import RamanujanCorrection, SpectralCorrection
from . import experimental
from . import reduced
from .ramanujan_diagnostics import (
    compute_force_norm_ratios,
    compute_helicity_and_enstrophy_rates,
    compute_high_k_energy_ratio,
    compute_shell_transfer_matrices,
    compute_spectral_correction_flux,
)
from .variable_diffusion import (
    VariableDiffusionSystem,
    assemble_variable_diffusion_matrix,
    compute_symmetry_error,
    variable_viscosity_stress_divergence,
)

__version__ = "0.1.0.dev0"

__all__ = [
    "__version__",
    "SimulationConfig",
    "ConfigError",
    "StructuredMesh3D",
    "ScalarField",
    "FaceField",
    "VelocityField",
    "FlowState",
    "BoundaryConditionSet",
    "FaceBoundaryCondition",
    "BoundaryConditionError",
    "VelocityBCType",
    "PressureBCType",
    "apply_boundary_conditions",
    "apply_velocity_bc",
    "apply_pressure_bc",
    "OperatorError",
    "gradient",
    "divergence",
    "scalar_laplacian",
    "velocity_laplacian",
    "PressurePoissonSystem",
    "PressureSystemError",
    "SolveDiagnostics",
    "NullSpaceStrategy",
    "LinearSolverKind",
    "RHSCompatibilityMode",
    "compute_initial_pressure",
    "project",
    "project_incremental",
    "project_initial_velocity",
    "ProjectionResult",
    "ProjectionError",
    "derive_pressure_bcs",
    "derive_phi_bcs",
    "VelocityDiffusionSystem",
    "DiffusionDiagnostics",
    "DiffusionSystemError",
    "ThetaSchemeIntegrator",
    "StepDiagnostics",
    "IntegratorHistory",
    "IntegrationError",
    "CFLError",
    "compute_cfl",
    "compute_reynolds",
    "run",
    "ConvectionError",
    "centered_convection",
    "upwind_convection",
    "LinearSolver",
    "LinearSolverError",
    "LinearSolveResult",
    "SolverMethod",
    "MatrixKind",
    "create_linear_solver",
    "HAS_PYAMG",
    "AdaptiveTimestepController",
    "AdaptiveTimestepError",
    "DtDecision",
    "variable_step_ab2_coefficients",
    "pressure_extrapolation_coefficients",
    "StepProfiler",
    "ProfileReport",
    "MemoryReport",
    "estimate_field_memory",
    "estimate_matrix_memory",
    "estimate_solver_matrix_memory",
    "measure_matrix_memory",
    "measure_direct_factorization_memory",
    "measure_process_rss_delta",
    "LESModel",
    "SmagorinskyModel",
    "DynamicSmagorinskyModel",
    "WALEModel",
    "VremanModel",
    "experimental",
    "compute_strain_components",
    "compute_strain_magnitude",
    "variable_viscosity_stress_divergence",
    "VariableDiffusionSystem",
    "compute_energy_spectrum",
    "verify_parseval_identity",
    "generate_solenoidal_random_field",
    "generate_matched_solenoidal_fields",
    "compute_sgs_mechanical_work",
    "assemble_variable_diffusion_matrix",
    "compute_symmetry_error",
    "spectral_cutoff_filter",
    "apply_test_filter",
    "compute_germano_tensors",
    "restrict_velocity_fine_to_coarse",
    "compute_exact_sgs_stress",
    "compute_sgs_apriori_diagnostics",
    "compute_truncation_residuals",
    "compute_energy_budget",
    "SpectralCorrection",
    "RamanujanCorrection",
    "compute_helicity_and_enstrophy_rates",
    "compute_high_k_energy_ratio",
    "compute_force_norm_ratios",
    "compute_spectral_correction_flux",
    "compute_shell_transfer_matrices",
]
