"""Program TH10-R: Strict Dangerous-Burst Recurrence and True Vorticity Growth Math Module.

Mathematical formulation:
    1. Instantaneous Logarithmic Growth Rate:
        g(t) = D ln(q)/Dt = lambda_omega(t) + Vlog(t)
        where lambda_omega = xi^T S xi, Vlog = nu (xi . Delta omega) / q.

    2. Strict Dangerous Core Criteria:
        A. q / q_max >= alpha  (primary alpha = 0.95; robustness 0.90, 0.95, 0.99)
        B. lambda_3 > epsilon  (epsilon = 1e-4)
        C. rho = lambda_omega / lambda_3 >= rho_0  (primary rho_0 = 0.80; robustness 0.80, 0.90, 0.95, 0.99)
        D. g(t) > 0

    3. Finite-Window Confirmation:
        G_Delta(t) = ln[ q(t + Delta) / q(t) ] > tol (tol = 1e-4)

    4. Episode Reclassification Classes:
        - TRUE_POSITIVE_GROWTH_BURST
        - HIGH_ALIGNMENT_BUT_DECAYING
        - VISCOUSLY_DOMINATED
        - LOW_Q_NON_REGULARITY_RELEVANT
        - NUMERICALLY_AMBIGUOUS

    5. Episode Integrals & Balance:
        A_k  = int_{I_k} lambda_omega^+ dt
        V_k  = int_{I_k} Vlog dt
        G_k  = int_{I_k} g(t) dt = ln(q_end / q_start)
        H3_k = int_{I_k} lambda_3^+ dt
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, ScalarField
from .th5_vorticity_math import compute_pointwise_vorticity_state
from .th7_viscous_influx_math import compute_pointwise_viscous_decomposition
from .th8_depletion_math import extract_field_vorticity_grid


@dataclass
class TH10RPointState:
    """Evaluated state along a trajectory at time t."""
    t: float
    x: np.ndarray
    q: float
    q_max_field: float
    q_ratio: float           # q / q_max_field
    lambda_1: float
    lambda_2: float
    lambda_3: float
    lambda_omega: float
    rho: float               # lambda_omega / lambda_3
    a3: float
    Vlog: float
    g: float                 # lambda_omega + Vlog = D ln(q)/Dt
    Q: float
    structure_id: int        # Connected component / tracking ID
    is_dangerous_core: bool  # q_ratio >= alpha and rho >= rho_0 and g > 0
    xi: np.ndarray
    e3: np.ndarray


@dataclass
class TH10RConfirmedBurst:
    """Strictly confirmed dangerous growth burst."""
    burst_id: int
    t_start: float
    t_end: float
    duration: float
    q_start: float
    q_end: float
    q_peak: float
    max_q_ratio: float
    A_k: float               # int lambda_omega^+ dt
    V_k: float               # int Vlog dt
    G_k: float               # int g(t) dt = ln(q_end / q_start)
    H3_k: float              # int lambda_3^+ dt
    structure_id: int
    refractory_time: float   # W_k = start(next) - end(this)
    inter_delta_ln_q: float  # D_k = ln(q(next_start) / q(this_end))
    is_same_structure_next: bool


def evaluate_th10r_point(
    x_pt: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    t_cur: float = 0.0,
    q_max_field: Optional[float] = None,
    alpha: float = 0.95,
    rho_0: float = 0.80,
    structure_id: int = 0,
) -> TH10RPointState:
    """Compute exact instantaneous growth rate g(t) and strict dangerous core status."""
    x_pt = np.asarray(x_pt, dtype=np.float64).reshape(3)

    v_st = compute_pointwise_vorticity_state(x_pt, velocity, mesh, nu=nu)
    decomp = compute_pointwise_viscous_decomposition(x_pt, velocity, mesh, nu=nu)

    l1, l2, l3 = v_st.eigvals
    lw = float(v_st.lambda_omega)
    safe_l3 = l3 if abs(l3) > 1e-6 else 1e-6
    rho = float(lw / safe_l3)
    a3 = float(v_st.alignments[2]**2)

    q = float(v_st.omega_mag)
    if q_max_field is None:
        q_grid, _, _, _ = extract_field_vorticity_grid(velocity, mesh)
        q_max_field = float(np.max(q_grid))

    q_ratio = q / max(1e-6, q_max_field)

    # Vlog = nu (xi . Delta omega) / q
    xi = v_st.omega_hat
    lap_w = decomp.lap_omega
    Vlog = float(nu * np.dot(xi, lap_w) / max(1e-6, q))

    # Exact growth rate g(t)
    g = lw + Vlog

    is_danger = (q_ratio >= alpha) and (l3 > 1e-4) and (rho >= rho_0) and (g > 0.0)

    return TH10RPointState(
        t=t_cur,
        x=x_pt,
        q=q,
        q_max_field=q_max_field,
        q_ratio=q_ratio,
        lambda_1=l1,
        lambda_2=l2,
        lambda_3=l3,
        lambda_omega=lw,
        rho=rho,
        a3=a3,
        Vlog=Vlog,
        g=g,
        Q=float(v_st.Q),
        structure_id=structure_id,
        is_dangerous_core=is_danger,
        xi=xi,
        e3=v_st.eigvecs[:, 2],
    )


def reclassify_original_episode(
    pts_in_episode: List[TH10RPointState],
    alpha: float = 0.90,
    rho_0: float = 0.80,
) -> str:
    """Classify an original TH10 episode into exact physical categories."""
    if not pts_in_episode:
        return "NUMERICALLY_AMBIGUOUS"

    mean_q_ratio = np.mean([p.q_ratio for p in pts_in_episode])
    mean_g = np.mean([p.g for p in pts_in_episode])
    mean_lw = np.mean([p.lambda_omega for p in pts_in_episode])
    mean_vlog = np.mean([p.Vlog for p in pts_in_episode])

    if mean_q_ratio < alpha:
        return "LOW_Q_NON_REGULARITY_RELEVANT"

    if mean_g > 1e-4:
        return "TRUE_POSITIVE_GROWTH_BURST"
    elif mean_vlog < -abs(mean_lw):
        return "VISCOUSLY_DOMINATED"
    else:
        return "HIGH_ALIGNMENT_BUT_DECAYING"


def identify_th10r_true_bursts(
    traj_points: List[TH10RPointState],
    alpha: float = 0.95,
    rho_0: float = 0.80,
    min_window_steps: int = 1,
) -> List[TH10RConfirmedBurst]:
    """Identify strictly confirmed dangerous growth bursts along a trajectory."""
    bursts: List[TH10RConfirmedBurst] = []
    in_burst = False
    start_idx = 0
    burst_count = 0

    n_pts = len(traj_points)
    if n_pts < 2:
        return bursts

    burst_intervals: List[Tuple[int, int]] = []
    for i, pt in enumerate(traj_points):
        # Strict condition: q/qmax >= alpha, rho >= rho_0, g > 0
        cond = (pt.q_ratio >= alpha) and (pt.rho >= rho_0) and (pt.g > 0.0)
        if cond:
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
        t_s = traj_points[s_idx].t
        t_e = traj_points[e_idx].t
        dur = max(1e-6, t_e - t_s)

        q_s = traj_points[s_idx].q
        q_e = traj_points[e_idx].q
        q_pk = max([traj_points[k].q for k in range(s_idx, e_idx + 1)])
        max_ratio = max([traj_points[k].q_ratio for k in range(s_idx, e_idx + 1)])
        struct_id = traj_points[s_idx].structure_id

        # Integrate A_k, V_k, G_k, H3_k
        A_k = 0.0
        V_k = 0.0
        G_k = 0.0
        H3_k = 0.0

        for off in range(e_idx - s_idx):
            k = s_idx + off
            dt = traj_points[k + 1].t - traj_points[k].t
            lw_pos_0 = max(0.0, traj_points[k].lambda_omega)
            lw_pos_1 = max(0.0, traj_points[k + 1].lambda_omega)
            l3_pos_0 = max(0.0, traj_points[k].lambda_3)
            l3_pos_1 = max(0.0, traj_points[k + 1].lambda_3)

            A_k += 0.5 * (lw_pos_0 + lw_pos_1) * dt
            V_k += 0.5 * (traj_points[k].Vlog + traj_points[k + 1].Vlog) * dt
            G_k += 0.5 * (traj_points[k].g + traj_points[k + 1].g) * dt
            H3_k += 0.5 * (l3_pos_0 + l3_pos_1) * dt

        # Inter-burst interval
        if idx < len(burst_intervals) - 1:
            next_s = burst_intervals[idx + 1][0]
            refractory_t = traj_points[next_s].t - t_e
            d_k = float(np.log(max(1e-6, traj_points[next_s].q) / max(1e-6, q_e)))
            same_struct = (struct_id == traj_points[next_s].structure_id)
        else:
            refractory_t = 0.0
            d_k = 0.0
            same_struct = False

        burst_count += 1
        bursts.append(TH10RConfirmedBurst(
            burst_id=burst_count,
            t_start=t_s,
            t_end=t_e,
            duration=dur,
            q_start=q_s,
            q_end=q_e,
            q_peak=q_pk,
            max_q_ratio=max_ratio,
            A_k=float(A_k),
            V_k=float(V_k),
            G_k=float(G_k),
            H3_k=float(H3_k),
            structure_id=struct_id,
            refractory_time=float(refractory_t),
            inter_delta_ln_q=float(d_k),
            is_same_structure_next=same_struct,
        ))

    return bursts
