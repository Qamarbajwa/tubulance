"""verifier: Independent Read-Only Verifier Package for Milestone V2 & V2.2.

Enforces absolute separation between experimental research code, verification logic,
and external cryptographic roots of trust.
"""

from .lock_manager import LockManager, VerifierLockError
from .metric_oracle import (
    oracle_velocity_relative_l2,
    oracle_wall_shear_relative_error,
    oracle_subspace_overlap,
)
from .config_validator import validate_config_comparability
from .timing_validator import validate_timing_and_resources
from .claim_validator import validate_report_claims
from .ledger_validator import validate_hash_chained_ledger
from .static_dep_checker import assert_no_verifier_imports_in_experiment, assert_no_project_scripts_write_external_root
from .crypto_signer import (
    generate_ed25519_keypair,
    compute_public_key_fingerprint,
    sign_data,
    verify_data_signature,
    canonicalize_json,
    InvalidSignatureError,
)
from .trusted_roots import (
    LockManagerV2,
    UntrustedVerifierRootError,
    UntrustedPublicKeyError,
    RevokedVerifierError,
    TrustMode,
    TrustModeManager,
    TrustLevel,
    DevelopmentIdentityError,
    ExternalRootUnavailableError,
    ExternalRootMismatchError,
    ExternalRootWriteForbiddenError,
    load_revoked_identities,
)
from .receipt_schema import build_v2_receipt_schema, compute_receipt_canonical_hash
from .golden_fixtures import verify_golden_fixtures
from .status_machine import StatusMachine, TRUST_LEVEL_MAP
from .secret_scanner import scan_repository_for_secrets, SecretLeakError
from .verify_receipt import verify_receipt

__all__ = [
    "LockManager",
    "LockManagerV2",
    "VerifierLockError",
    "UntrustedVerifierRootError",
    "UntrustedPublicKeyError",
    "RevokedVerifierError",
    "TrustMode",
    "TrustModeManager",
    "TrustLevel",
    "DevelopmentIdentityError",
    "ExternalRootUnavailableError",
    "ExternalRootMismatchError",
    "ExternalRootWriteForbiddenError",
    "load_revoked_identities",
    "InvalidSignatureError",
    "SecretLeakError",
    "oracle_velocity_relative_l2",
    "oracle_wall_shear_relative_error",
    "oracle_subspace_overlap",
    "validate_config_comparability",
    "validate_timing_and_resources",
    "validate_report_claims",
    "validate_hash_chained_ledger",
    "assert_no_verifier_imports_in_experiment",
    "assert_no_project_scripts_write_external_root",
    "generate_ed25519_keypair",
    "compute_public_key_fingerprint",
    "sign_data",
    "verify_data_signature",
    "canonicalize_json",
    "build_v2_receipt_schema",
    "compute_receipt_canonical_hash",
    "verify_golden_fixtures",
    "StatusMachine",
    "TRUST_LEVEL_MAP",
    "scan_repository_for_secrets",
    "verify_receipt",
]
