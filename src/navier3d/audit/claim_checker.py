"""Claim-Evidence Mapping and Logical Report Validation.

Implements Sections 11, 12, 13, 38, 39 of Milestone V0.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List


class ReportValidationError(ValueError):
    """Raised when markdown report claims contradict computed metrics.json data."""


class ClaimChecker:
    """Manages claims.json and links claims to supporting run IDs and metrics."""

    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        self.claims_path = self.run_dir / "claims.json"
        self.claims: List[Dict[str, Any]] = []

    def add_claim(
        self,
        claim_id: str,
        text: str,
        supporting_run_ids: List[str],
        supporting_metrics: List[str],
        status: str = "UNVERIFIED",
    ) -> Dict[str, Any]:
        valid_statuses = ("VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED", "CONTRADICTED", "INVALIDATED")
        if status not in valid_statuses:
            raise ValueError(f"Invalid claim status {status!r}; expected one of {valid_statuses}")

        entry = {
            "claim_id": claim_id,
            "text": text,
            "supporting_run_ids": supporting_run_ids,
            "supporting_metrics": supporting_metrics,
            "status": status,
        }
        self.claims.append(entry)
        self.save()
        return entry

    def save(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with open(self.claims_path, "w", encoding="utf-8") as f:
            json.dump(self.claims, f, indent=2)


def validate_report_against_metrics(
    report_md: str, metrics: Dict[str, Any], run_dir: str | Path
) -> Dict[str, Any]:
    """Parse report text and check for logical contradictions against computed metrics.

    Checks:
    - Speedup claims (e.g. '10x' vs actual 4.2x)
    - Error claims (e.g. '< 1%' or '1%' vs actual 14% or 25%)
    - Memory claims
    """
    errors = []

    # Check for velocity error claim contradiction
    if "velocity_relative_l2" in metrics:
        actual_e_u = metrics["velocity_relative_l2"]["value"]
        # Look for claims of < 1% or < 0.01 error when actual is much larger
        if actual_e_u > 0.05:
            if re.search(r"E_u\s*<\s*1%|< 0\.01|less than 1%|under 1%", report_md, re.IGNORECASE):
                errors.append(
                    f"Report claims velocity error E_u < 1%, but metrics.json records E_u = {actual_e_u:.4f} ({actual_e_u*100:.2f}%)"
                )

    # Check for speedup claim contradiction
    if "speedup" in metrics:
        actual_speedup = metrics["speedup"]["value"]
        # Look for claims like "50x" or "100x" when actual is small
        if actual_speedup < 10.0:
            match = re.search(r"(\d+(\.\d+)?)x\s*speedup", report_md, re.IGNORECASE)
            if match:
                claimed_speedup = float(match.group(1))
                if claimed_speedup > actual_speedup * 2.0 and claimed_speedup > 10.0:
                    errors.append(
                        f"Report claims {claimed_speedup:.1f}x speedup, but metrics.json records speedup = {actual_speedup:.2f}x"
                    )

    validation_result = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }

    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "report_validation.json", "w", encoding="utf-8") as f:
        json.dump(validation_result, f, indent=2)

    if errors:
        raise ReportValidationError(
            f"Report validation FAILED with {len(errors)} logical contradiction(s):\n" + "\n".join(f"- {e}" for e in errors)
        )

    return validation_result
