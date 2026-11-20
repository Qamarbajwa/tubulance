"""Unit tests for Program NS-REP-SYNTHESIS-1."""
from __future__ import annotations

import pytest

from navier3d.experimental.rep_synthesis1_audit_math import (
    build_representation_dictionary,
    audit_common_stretching_source,
    audit_pressure_response_adversarial,
    audit_frame_rotation_hypothesis,
    audit_critical_space_translations,
    audit_missing_ingredients,
)


def test_rep_synthesis1_suite():
    """Verify cross-representation dictionary, stretching source, falsifications, and missing ingredients."""
    # 1. Dictionary completeness
    dict_entries = build_representation_dictionary()
    assert len(dict_entries) >= 12
    reps = {e.representation for e in dict_entries}
    assert "Eulerian" in reps
    assert "Pressure" in reps
    assert "Stochastic Lagrangian" in reps
    assert "Multiscale" in reps

    # 2. Common stretching source
    stretching = audit_common_stretching_source()
    assert stretching["classification"] == "PROVED_IMPLICATION"
    assert "S" in stretching["underlying_common_tensor"]

    # 3. Adversarial pressure response
    press_adv = audit_pressure_response_adversarial()
    assert press_adv["is_automatic_stabilization_falsified"] is True
    assert press_adv["status"] == "FALSIFIED"

    # 4. Frame rotation hypothesis
    frame_audit = audit_frame_rotation_hypothesis()
    assert frame_audit.is_dimensionally_consistent is True
    assert frame_audit.is_scale_invariant is True
    assert frame_audit.smooth_solution_can_violate is True
    assert "FALSIFIED" in frame_audit.general_regularity_equivalence_status

    # 5. Critical space translations
    translations = audit_critical_space_translations()
    assert len(translations) >= 5
    quantities = [t["quantity"] for t in translations]
    assert any("Deformation Covariance" in q for q in quantities)
    assert any("Correlation Field" in q for q in quantities)

    # 6. Missing ingredients
    missing = audit_missing_ingredients()
    assert len(missing) == 9
