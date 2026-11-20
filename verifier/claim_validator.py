"""Independent Report Claim Validator and Contradiction Engine.

Implements Sections 27, 28, 29, 30, 31, 36, 37, 41, 54, 56 of Milestone V1.
"""
from __future__ import annotations

import re
from typing import Dict, Any, List


class VerifierClaimError(ValueError):
    """Raised when report claims violate evidence limits or preregistered rules."""


FORBIDDEN_UNSUPPORTED_WORDS = ["proves", "guarantees", "exact", "solves"]


def validate_report_claims(report_text: str, verified_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Inspect report text for prohibited exaggeration or logical claim errors."""
    issues = []

    # 1. Forbidden language check
    for word in FORBIDDEN_UNSUPPORTED_WORDS:
        if re.search(r"\b" + word + r"\b", report_text, re.IGNORECASE):
            issues.append(f"Forbidden unsupported term '{word}' found in report text.")

    # 2. Logic Correction A: E_excess <= 0 does NOT imply "zero integration error"
    if re.search(r"zero\s*(integration|temporal)\s*error", report_text, re.IGNORECASE):
        if "temporal_dt_convergence_tested" not in verified_metrics:
            issues.append(
                "Report claims 'zero integration error', but no dt/2, dt/4 temporal convergence test was executed!"
            )

    # 3. Logic Correction B: Solenoidal alone does not justify KEEP verdict
    if re.search(r"KEEP\s*because\s*solenoidal", report_text, re.IGNORECASE):
        issues.append(
            "Report assigns KEEP verdict based solely on solenoidal property without demonstrating empirical metric benefit."
        )

    # 4. Logic Correction C: "Fully transferable across Re" requires multi-Re holdouts
    if re.search(r"fully\s*transferable\s*across\s*reynolds", report_text, re.IGNORECASE):
        if verified_metrics.get("multi_re_holdout_count", 0) < 3:
            issues.append(
                "Report claims 'fully transferable across Reynolds numbers', but fewer than 3 independent Re holdouts were evaluated!"
            )

    status = "VERIFIED" if not issues else "FAILED"
    return {"status": status, "issues": issues}
