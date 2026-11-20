"""Unit tests for Program NS-CONE-TERMINAL-OSCILLATION-1."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.cone_terminal_oscillation_math import (
    TerminalOscillationGeometricConstants,
    ChebyshevRadiusComparisonResult,
    IntegralSpikeCounterexampleResult,
    compute_geometric_margin_constants,
    compute_cluster_chebyshev_geometry,
    audit_weighted_integral_spike_counterexample,
)


def test_cone_terminal_oscillation_math():
    """Verify geometric margin, Chebyshev radius/diameter, and spike counterexamples."""
    # 1. Geometric margin constants
    c = compute_geometric_margin_constants(delta=0.42)
    assert np.isclose(c.alpha_deg + c.beta_deg, 90.0)
    assert 0.0 < c.alpha_deg < 90.0
    assert 0.0 < c.beta_deg < 90.0

    # 2. Chebyshev radius vs diameter
    # Suppose cluster has radius 25 deg, beta is 35 deg -> diameter is 50 deg.
    # Radius (25 deg) < beta (35 deg), but diameter (50 deg) > beta (35 deg).
    res = compute_cluster_chebyshev_geometry(radius_deg=25.0, beta_deg=35.0)
    assert res.fits_within_beta_radius is True
    assert res.fits_within_beta_diameter is False
    assert res.is_radius_smaller_than_diameter is True

    # 3. Weighted integral spike counterexample
    spike = audit_weighted_integral_spike_counterexample(gamma=2.0, beta_deg=c.beta_deg)
    assert spike.is_integral_finite is True
    assert spike.exceeds_beta_margin is True
    assert np.isclose(spike.essential_sup_radius, np.pi / 2.0)
