"""Unit tests for Program NS-CONE-LEMMA-PROOF-1: Proof-Only Adversarial Audit Suite."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.cone_lemma_proof1_math import (
    GeometricReductionResult,
    TemporalDiscontinuityAuditResult,
    MovingAxisScalingLedgerEntry,
    compute_geometric_reduction_constant,
    audit_temporal_selection_counterexample,
    generate_proof_gate_scaling_ledger,
)


def test_cone_lemma_proof1_gates():
    """Verify Proof Gate 1, 2, 6, and 11 mathematical calculations."""
    # Proof Gate 1: Geometric reduction
    res1 = compute_geometric_reduction_constant(delta=0.42)
    assert res1.is_axial_domination_valid is True
    assert 0.0 < res1.theta_max_deg < 90.0
    assert res1.constant_C_delta >= 1.0

    # Proof Gate 2: Temporal discontinuity counterexample
    res2 = audit_temporal_selection_counterexample()
    assert res2.is_temporal_regularity_implied_by_hypothesis is False
    assert np.isclose(res2.angular_jump_deg, 90.0)
    assert res2.hypothesis_violated is False  # Valid adversarial counterexample

    # Proof Gate 6 & 11: Scaling ledger
    ledger = generate_proof_gate_scaling_ledger()
    assert len(ledger) >= 4
    term_names = [e.term_name for e in ledger]
    assert "E1_axis_rotation" in term_names
    assert "E3_low_vorticity_2d_slice" in term_names
