"""Unit tests for Program TH10-R: Strict Dangerous-Burst Recurrence."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.th10r_true_burst_math import (
    TH10RPointState,
    evaluate_th10r_point,
    identify_th10r_true_bursts,
    reclassify_original_episode,
)


def test_th10r_growth_rate_and_reclassification():
    """Verify exact logarithmic growth rate g = lambda_omega + Vlog and reclassification logic."""
    pts = []
    for t in [0.0, 0.1, 0.2, 0.3, 0.4]:
        # Case A: High rho (0.95), High q_ratio (0.98), but Negative growth (g = -0.5)
        pt = TH10RPointState(
            t=t,
            x=np.zeros(3),
            q=10.0 - t,
            q_max_field=10.0,
            q_ratio=0.98,
            lambda_1=-1.0,
            lambda_2=0.0,
            lambda_3=2.0,
            lambda_omega=1.9,
            rho=0.95,
            a3=0.90,
            Vlog=-2.4, # Overwhelms stretching
            g=1.9 - 2.4, # = -0.5
            Q=-1.0,
            structure_id=1,
            is_dangerous_core=False,
            xi=np.array([1.0, 0.0, 0.0]),
            e3=np.array([1.0, 0.0, 0.0]),
        )
        pts.append(pt)

    # Must be reclassified as VISCOUSLY_DOMINATED or HIGH_ALIGNMENT_BUT_DECAYING, NOT true growth
    reclass = reclassify_original_episode(pts, alpha=0.90, rho_0=0.80)
    assert reclass in ["VISCOUSLY_DOMINATED", "HIGH_ALIGNMENT_BUT_DECAYING"]
    assert reclass != "TRUE_POSITIVE_GROWTH_BURST"


def test_th10r_true_growth_burst_detection():
    """Verify detection of genuine positive-growth bursts."""
    pts = []
    for i, t in enumerate(np.linspace(0.0, 0.5, 6)):
        is_burst = (0.1 <= t <= 0.3)
        lw = 2.0 if is_burst else -1.0
        vlog = -0.2 if is_burst else -0.5
        g = lw + vlog # 1.8 during burst (>0), -1.5 outside

        pt = TH10RPointState(
            t=float(t),
            x=np.zeros(3),
            q=float(9.5 + (t if is_burst else -t)),
            q_max_field=10.0,
            q_ratio=0.96,
            lambda_1=-1.0,
            lambda_2=0.0,
            lambda_3=2.1,
            lambda_omega=float(lw),
            rho=float(lw / 2.1),
            a3=0.90,
            Vlog=float(vlog),
            g=float(g),
            Q=-1.0,
            structure_id=1,
            is_dangerous_core=(is_burst and g > 0),
            xi=np.array([1.0, 0.0, 0.0]),
            e3=np.array([1.0, 0.0, 0.0]),
        )
        pts.append(pt)

    bursts = identify_th10r_true_bursts(pts, alpha=0.95, rho_0=0.80)
    assert len(bursts) == 1
    assert bursts[0].G_k > 0.0
    assert bursts[0].A_k > 0.0
