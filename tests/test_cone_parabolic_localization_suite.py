"""Unit tests for Program NS-CONE-PARABOLIC-LOCALIZATION-1."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.cone_parabolic_localization_math import (
    ParabolicLocalizationResult,
    GreatCircleEquivalenceResult,
    compute_parabolic_fixed_cone_parameters,
    map_great_circle_avoidance_to_parabolic_radius,
)


def test_cone_parabolic_localization():
    """Verify parabolic fixed cone parameters and great-circle mapping."""
    # 1. Parabolic fixed cone parameter validation
    for deg in [0.0, 15.0, 35.0, 60.0, 85.0]:
        res = compute_parabolic_fixed_cone_parameters(
            radius_r=0.25,
            threshold_M=5.0,
            chebyshev_radius_deg=deg,
        )
        assert res.is_fixed_cone_satisfied is True
        assert res.effective_cone_margin_delta_star > 0.0
        assert np.isclose(res.effective_cone_margin_delta_star, 1.0 - np.sin(np.radians(deg)))

    # 2. Great circle avoidance mapping
    gc_res = map_great_circle_avoidance_to_parabolic_radius(margin_from_great_circle_deg=10.0)
    assert gc_res.asymptotic_avoids_great_circle is True
    assert gc_res.is_R_M_strictly_less_than_90deg is True
    assert np.isclose(gc_res.corresponding_R_M_deg, 80.0)
