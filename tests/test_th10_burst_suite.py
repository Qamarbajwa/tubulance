"""Unit tests for Milestone TH10: Temporal Burst Recurrence, Refractory Time, and Structure Switching."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.th10_burst_math import (
    TH10TrajectoryPoint,
    identify_burst_episodes,
    classify_structure_type,
)


def test_th10_structure_classification():
    """Verify Q-criterion structure classification."""
    assert classify_structure_type(-0.5) == "SHEET"
    assert classify_structure_type(+0.5) == "TUBE"
    assert classify_structure_type(0.0) == "INTERMEDIATE"


def test_th10_burst_identification_and_refractory_dynamics():
    """Verify burst identification, refractory interval segmentation, structure switching, and net gain computation."""
    times = np.linspace(0.0, 1.0, 51)
    pts = []

    # Construct synthetic trajectory with two bursts (rho >= 0.80) separated by a relaxation interval
    for t in times:
        if (0.1 <= t <= 0.3) or (0.6 <= t <= 0.8):
            rho = 0.95
            l_w = 2.0
            l3 = 2.1
            v_log = -0.1
            Q = -0.8  # Strain-dominated sheet during burst
        else:
            rho = 0.20
            l_w = -1.0
            l3 = 1.5
            v_log = -0.5
            Q = +0.8  # Vorticity-dominated tube / intermediate post-burst

        pts.append(TH10TrajectoryPoint(
            t=float(t),
            x=np.array([1.0, 2.0, 3.0]),
            q=float(1.0 + t),
            lambda_3=float(l3),
            lambda_omega=float(l_w),
            rho=float(rho),
            a3=float(rho**2),
            Vlog=float(v_log),
            Q=float(Q),
            structure_type=classify_structure_type(Q),
            xi=np.array([1.0, 0.0, 0.0]),
            e3=np.array([np.cos(t), np.sin(t), 0.0]),
        ))

    episodes = identify_burst_episodes(pts, rho_thresh=0.80)

    assert len(episodes) == 2
    assert episodes[0].t_start == pytest.approx(0.1, abs=0.03)
    assert episodes[0].t_end == pytest.approx(0.3, abs=0.03)
    assert episodes[0].delta_ln_q_burst > 0.0
    assert episodes[0].post_inter_delta_ln_q < 0.0
    assert episodes[0].net_cycle_gain < episodes[0].delta_ln_q_burst
    assert episodes[0].burst_structure == "SHEET"
    assert episodes[0].post_burst_structure == "TUBE"
    assert episodes[0].structure_switched is True
    assert episodes[0].refractory_time == pytest.approx(0.3, abs=0.03)
