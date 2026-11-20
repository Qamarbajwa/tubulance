"""Unit tests for Program NS-REP-LAGRANGIAN-1."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.rep_lagrangian1_weber_math import (
    StochasticWeberScalingEntry,
    RegularityBarrierTranslationResult,
    LimitingFlowWeberProfile,
    generate_stochastic_weber_scaling_table,
    translate_regularity_criteria_to_weber,
    compute_limiting_flow_weber_profiles,
)


def test_rep_lagrangian1_weber():
    """Verify stochastic Weber scaling, regularity translations, and flow profiles."""
    # 1. Scaling classifications
    scaling_table = generate_stochastic_weber_scaling_table()
    assert len(scaling_table) >= 5
    var_names = [e.variable_name for e in scaling_table]
    assert "Deformation Covariance Tensor" in var_names
    assert "Deformation-Velocity Correlation Field" in var_names

    # Check scale invariance
    for entry in scaling_table:
        assert entry.is_scale_invariant is True

    # 2. Regularity translations
    translations = translate_regularity_criteria_to_weber()
    assert len(translations) >= 3
    crit_names = [t.criterion_name for t in translations]
    assert any("Escauriaza" in c for c in crit_names)
    assert any("Serrin" in c for c in crit_names)
    assert any("Koch-Tataru" in c for c in crit_names)

    # 3. Core flow profiles
    profiles = compute_limiting_flow_weber_profiles()
    assert len(profiles) >= 2
    flow_names = [p.flow_name for p in profiles]
    assert any("Townsend" in f for f in flow_names)
    assert any("Burgers" in f for f in flow_names)
