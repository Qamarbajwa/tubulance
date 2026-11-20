"""Cryptographically Bound Receipt Schema and Canonical Hash Generator.

Implements Section 9, 10 of Milestone V2 and Milestone V2.2.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
from typing import Dict, Any

from .crypto_signer import canonicalize_json


def build_v2_receipt_schema(
    run_id: str,
    verifier_version: str,
    verifier_manifest_sha256: str,
    source_manifest_sha256: str,
    git_commit: str,
    config_sha256: str,
    preregistration_sha256: str,
    holdout_manifest_sha256: str,
    raw_manifest_sha256: str,
    metrics_sha256: str,
    timing_sha256: str,
    environment_sha256: str,
    report_sha256: str,
    ledger_head_sha256: str,
    verification_status: str = "TECHNICALLY_VERIFIED",
    trust_level: str = "LEVEL 2 - TECHNICALLY VERIFIED",
    trust_mode: str = "DEVELOPMENT_ONLY",
    signing_public_key_fingerprint: str = "",
) -> Dict[str, Any]:
    """Construct deterministic V2/V2.2 receipt dictionary."""
    return {
        "schema_version": "2.2",
        "run_id": run_id,
        "verifier_version": verifier_version,
        "verifier_manifest_sha256": verifier_manifest_sha256,
        "source_manifest_sha256": source_manifest_sha256,
        "git_commit": git_commit,
        "config_sha256": config_sha256,
        "preregistration_sha256": preregistration_sha256,
        "holdout_manifest_sha256": holdout_manifest_sha256,
        "raw_manifest_sha256": raw_manifest_sha256,
        "metrics_sha256": metrics_sha256,
        "timing_sha256": timing_sha256,
        "environment_sha256": environment_sha256,
        "report_sha256": report_sha256,
        "ledger_head_sha256": ledger_head_sha256,
        "verification_status": verification_status,
        "trust_mode": trust_mode,
        "signing_public_key_fingerprint": signing_public_key_fingerprint,
        "trust_level": trust_level,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def compute_receipt_canonical_hash(receipt_dict: Dict[str, Any]) -> str:
    """Compute SHA256 hex digest of canonicalized receipt JSON."""
    json_bytes = canonicalize_json(receipt_dict)
    return hashlib.sha256(json_bytes).hexdigest()
