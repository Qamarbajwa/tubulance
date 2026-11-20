"""Milestone TH10: Temporal Burst Recurrence, Inter-Burst Damping, Structure Switching, and Cumulative Growth.

Mathematical formulation:
    1. Burst Identification:
        A continuous interval [t_start, t_end] where realized stretching ratio
        rho(t) = lambda_omega(t) / lambda_3(t) >= rho_thresh (default 0.80).
        Duration: Delta t_burst = t_end - t_start.

    2. Refractory Time:
        t_refractory = t_{next_start} - t_end
        Measures the minimum quiescent interval before another dangerous burst can occur.

    3. Structure Switching Dynamics:
        Q = 1/2 ( ||Omega||_F^2 - ||S||_F^2 )
        Topology:
            "SHEET": Q < -eps_Q (strain-dominated layer)
            "TUBE":  Q > +eps_Q (vorticity-dominated core)
            "INTERMEDIATE": |Q| <= eps_Q

    4. Logarithmic Vorticity Gains and Inter-Burst Damping:
        Burst Gain:
            Delta_ln_q_burst = int_{t_start}^{t_end} (lambda_omega(s) + Vlog(s)) ds
        Inter-Burst Damping:
            Delta_ln_q_inter = int_{t_end}^{t_{next_start}} (lambda_omega(s) + Vlog(s)) ds
        Net Cycle Gain:
            Delta_ln_q_cycle = Delta_ln_q_burst + Delta_ln_q_inter

    5. Cumulative Stretching Functionals:
        I_lambda_omega(t) = int_0^t lambda_omega(s) ds
        I_lambda_3(t)     = int_0^t lambda_3(s) ds
        Cumulative Depletion Fraction = 1 - I_lambda_omega(T) / I_lambda_3(T)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, ScalarField
from .th5_vorticity_math import compute_pointwise_vorticity_state
from .th7_viscous_influx_math import compute_pointwise_viscous_decomposition
from .th9_persistence_math import compute_pressure_hessian_at_point


@dataclass
class TH10TrajectoryPoint:
    """State record along a trajectory at time t."""
    t: float
    x: np.ndarray
    q: float
    lambda_3: float
    lambda_omega: float
    rho: float
    a3: float
    Vlog: float
    Q: float
    structure_type: str  # "SHEET", "TUBE", "INTERMEDIATE"
    xi: np.ndarray
    e3: np.ndarray


@dataclass
class TH10BurstEpisode:
    """Quantified stretching burst episode with structure switching and refractory timing."""
    episode_id: int
    t_start: float
    t_end: float
    duration: float
    duration_strain_units: float
    q_start: float
    q_peak: float
    q_end: float
    delta_ln_q_burst: float
    mean_rho: float
    max_rho: float
    burst_structure: str
    refractory_time: float
    post_inter_delta_ln_q: float
    net_cycle_gain: float
    post_burst_structure: str
    structure_switched: bool
    phase_scrambling_orient: float
    phase_scrambling_frame: float


def classify_structure_type(Q: float, eps_Q: float = 0.05) -> str:
    """Classify local topology from the second velocity gradient invariant Q."""
    if Q < -eps_Q:
        return "SHEET"
    elif Q > eps_Q:
        return "TUBE"
    else:
        return "INTERMEDIATE"


def identify_burst_episodes(
    traj_points: List[TH10TrajectoryPoint],
    rho_thresh: float = 0.80,
) -> List[TH10BurstEpisode]:
    """Identify discrete near-maximal stretching burst episodes and inter-burst damping intervals."""
    episodes: List[TH10BurstEpisode] = []
    in_burst = False
    start_idx = 0
    ep_count = 0

    n_pts = len(traj_points)
    if n_pts < 2:
        return episodes

    # Find burst segments
    burst_intervals: List[Tuple[int, int]] = []
    for i, pt in enumerate(traj_points):
        if pt.rho >= rho_thresh:
            if not in_burst:
                in_burst = True
                start_idx = i
        else:
            if in_burst:
                in_burst = False
                burst_intervals.append((start_idx, i - 1))
    if in_burst:
        burst_intervals.append((start_idx, n_pts - 1))

    for idx, (s_idx, e_idx) in enumerate(burst_intervals):
        ep_count += 1
        t_s = traj_points[s_idx].t
        t_e = traj_points[e_idx].t
        dur = max(1e-6, t_e - t_s)

        mean_l3 = np.mean([traj_points[k].lambda_3 for k in range(s_idx, e_idx + 1)])
        dur_strain = dur * max(1e-4, mean_l3)

        q_s = traj_points[s_idx].q
        q_e = traj_points[e_idx].q
        q_pk = max([traj_points[k].q for k in range(s_idx, e_idx + 1)])

        # Integrate burst gain
        burst_dt = [(traj_points[s_idx + off + 1].t - traj_points[s_idx + off].t) for off in range(e_idx - s_idx)]
        if burst_dt:
            int_gain = sum(
                0.5 * (traj_points[s_idx + off].lambda_omega + traj_points[s_idx + off].Vlog + traj_points[s_idx + off + 1].lambda_omega + traj_points[s_idx + off + 1].Vlog) * dt
                for off, dt in enumerate(burst_dt)
            )
        else:
            int_gain = 0.0

        mean_rho = float(np.mean([traj_points[k].rho for k in range(s_idx, e_idx + 1)]))
        max_rho = float(np.max([traj_points[k].rho for k in range(s_idx, e_idx + 1)]))
        burst_struct = traj_points[s_idx].structure_type

        # Inter-burst interval to next burst
        if idx < len(burst_intervals) - 1:
            next_s_idx = burst_intervals[idx + 1][0]
            refractory_dur = traj_points[next_s_idx].t - t_e
            inter_dt = [(traj_points[e_idx + off + 1].t - traj_points[e_idx + off].t) for off in range(next_s_idx - e_idx)]
            inter_gain = sum(
                0.5 * (traj_points[e_idx + off].lambda_omega + traj_points[e_idx + off].Vlog + traj_points[e_idx + off + 1].lambda_omega + traj_points[e_idx + off + 1].Vlog) * dt
                for off, dt in enumerate(inter_dt)
            )
            scramble_orient = float(np.dot(traj_points[e_idx].xi, traj_points[next_s_idx].xi)**2)
            scramble_frame = float(np.dot(traj_points[e_idx].e3, traj_points[next_s_idx].e3)**2)
            post_struct = traj_points[min(e_idx + 1, n_pts - 1)].structure_type
            switched = (burst_struct != post_struct)
        else:
            refractory_dur = 0.0
            inter_gain = 0.0
            scramble_orient = 1.0
            scramble_frame = 1.0
            post_struct = burst_struct
            switched = False

        episodes.append(TH10BurstEpisode(
            episode_id=ep_count,
            t_start=t_s,
            t_end=t_e,
            duration=dur,
            duration_strain_units=dur_strain,
            q_start=q_s,
            q_peak=q_pk,
            q_end=q_e,
            delta_ln_q_burst=float(int_gain),
            mean_rho=mean_rho,
            max_rho=max_rho,
            burst_structure=burst_struct,
            refractory_time=float(refractory_dur),
            post_inter_delta_ln_q=float(inter_gain),
            net_cycle_gain=float(int_gain + inter_gain),
            post_burst_structure=post_struct,
            structure_switched=switched,
            phase_scrambling_orient=scramble_orient,
            phase_scrambling_frame=scramble_frame,
        ))

    return episodes
