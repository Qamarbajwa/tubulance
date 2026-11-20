"""Unit tests for Program NS-CONE-BV-FIXED-REDUCTION-1."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.cone_bv_fixed_reduction_math import (
    TerminalConeMarginResult,
    RescaledThresholdResult,
    compute_terminal_fixed_cone_margin,
    compute_rescaled_theorem11_parameters,
)


def test_terminal_fixed_cone_reduction():
    """Verify quantitative margin delta_* and parabolic rescaling calculations."""
    # Test for various initial cone margins
    for delta in [0.10, 0.25, 0.42, 0.75, 0.95]:
        res = compute_terminal_fixed_cone_margin(delta=delta, slack_fraction=0.5)
        assert res.is_terminal_cone_valid is True
        assert res.delta_star > 0.0
        assert res.combined_angle_deg < 90.0
        assert res.alpha_deg < res.combined_angle_deg

    # Test parabolic rescaling
    rescale_res = compute_rescaled_theorem11_parameters(M=10.0, horizon_h=0.04)
    assert rescale_res.is_theorem_1_1_applicable is True
    assert 0.0 < rescale_res.rescaling_radius_r <= 1.0
    assert 0.0 < rescale_res.rescaled_threshold_M_r <= rescale_res.original_M
