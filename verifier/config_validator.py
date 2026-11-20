"""Independent Configuration Comparability and Parameter Consistency Validator.

Implements Sections 19, 20, 21, 23, 24 of Milestone V1.
"""
from __future__ import annotations

from typing import Dict, Any, List


class VerifierConfigError(ValueError):
    """Raised when configuration comparability or physical consistency fails."""


def validate_config_comparability(ref_cfg: Dict[str, Any], cand_cfg: Dict[str, Any]) -> bool:
    """Verify physical problem comparability between reference and candidate configs."""
    prohibited_mismatches = [
        "nx", "ny", "nz", "lx", "ly", "lz", "nu", "rho", "dt", "n_steps", "seed", "bcs", "forcing"
    ]

    for key in prohibited_mismatches:
        ref_val = ref_cfg.get(key)
        cand_val = cand_cfg.get(key)
        if ref_val != cand_val:
            raise VerifierConfigError(
                f"Prohibited config mismatch for '{key}': ref={ref_val!r}, cand={cand_val!r}"
            )

    # Derived Reynolds consistency: Re = 2.0 / nu for channel (or L*U/nu)
    nu = float(cand_cfg.get("nu", 0.05))
    if "Re_declared" in cand_cfg:
        re_decl = float(cand_cfg["Re_declared"])
        re_deriv = 2.0 / nu
        if abs(re_decl - re_deriv) > 1e-5:
            raise VerifierConfigError(
                f"Reynolds consistency FAIL: Re_declared={re_decl}, but Re_derived={re_deriv}"
            )

    return True


def validate_actual_rank(claimed_rank: int, coeffs_shape: tuple[int, ...]) -> bool:
    """Validate that actual coefficient array dimension matches claimed rank."""
    actual_rank = coeffs_shape[0] if len(coeffs_shape) > 0 else 0
    if actual_rank != claimed_rank:
        raise VerifierConfigError(
            f"Rank validation FAIL: claimed rank = {claimed_rank}, but actual coefficient dimension = {actual_rank}"
        )
    return True
