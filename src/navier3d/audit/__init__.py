"""navier3d.audit: Research Evidence Integrity, Reproducibility, and Anti-Fabrication Framework.

Implements the project-wide rule: NO CLAIM WITHOUT EVIDENCE.
"""

from .run_identity import (
    generate_run_id,
    capture_environment,
    fingerprint_config,
    FrozenConfig,
    BenchmarkComparabilityError,
    assert_comparable,
)
from .evidence_bundle import (
    EvidenceBundle,
    WriteProtectionError,
    append_to_research_ledger,
)
from .metrics import (
    calculate_velocity_l2_relative_error,
    calculate_wall_shear_relative_error,
    get_metric_function_hash,
    build_metric_entry,
)
from .preregistration import (
    preregister_experiment,
    HoldoutViolationError,
    HoldoutManager,
)
from .claim_checker import (
    ClaimChecker,
    ReportValidationError,
    validate_report_against_metrics,
)
from .static_scanner import scan_codebase_for_hardcoded_results

__all__ = [
    "generate_run_id",
    "capture_environment",
    "fingerprint_config",
    "FrozenConfig",
    "BenchmarkComparabilityError",
    "assert_comparable",
    "EvidenceBundle",
    "WriteProtectionError",
    "append_to_research_ledger",
    "calculate_velocity_l2_relative_error",
    "calculate_wall_shear_relative_error",
    "get_metric_function_hash",
    "build_metric_entry",
    "preregister_experiment",
    "HoldoutViolationError",
    "HoldoutManager",
    "ClaimChecker",
    "ReportValidationError",
    "validate_report_against_metrics",
    "scan_codebase_for_hardcoded_results",
]
