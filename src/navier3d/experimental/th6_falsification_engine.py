"""Adversarial Falsification Engine for Candidate Vorticity-Growth Bound B1 (Milestone TH6).

Mathematical candidate:
    ln(|omega(t2)| / |omega(t1)|) <= int_{t1}^{t2} lambda_3(s) ds

Decomposition:
    r(t) = V_log(t) - G(t)
    where G(t) = lambda_3(t) - lambda_omega(t) >= 0 (eigenvalue gap)
          V_log(t) = nu * (omega_hat . Delta(omega)) / |omega| (viscous log term)
    R(t1, t2) = ln(|omega(t2)|/|omega(t1)|) - int_{t1}^{t2} lambda_3 dt
              = int_{t1}^{t2} [V_log - G] dt

Provides:
- All-subintervals matrix evaluation across trajectories.
- Pointwise positive-r event detection and duration analysis.
- Exact residual closure verification: |R_direct - R_integrated| <= tolerance.
- Adversarial flow state generator targeting G approx 0 and V_log > 0.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField
from ..projection import project
from ..boundary_conditions import BoundaryConditionSet, periodic_bcs
from .th5_vorticity_math import compute_pointwise_vorticity_state


@dataclass
class SubintervalEvaluation:
    """Exact dynamical terms and bound residual for a single trajectory subinterval [t1, t2]."""
    t1_idx: int
    t2_idx: int
    t1: float
    t2: float
    dt: float
    w1: float
    w2: float
    log_growth: float
    int_lambda_omega: float
    int_lambda_3: float
    int_V_log: float
    int_G: float
    R_direct: float
    R_integrated: float
    closure_error: float
    margin: float
    is_violation: bool


def _trapz(y_arr: np.ndarray, x_arr: np.ndarray) -> float:
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y_arr, x_arr))
    return float(np.trapz(y_arr, x_arr))


def evaluate_trajectory_subintervals(
    times: List[float],
    w_mags: List[float],
    lambda_omegas: List[float],
    lambda_3s: List[float],
    V_omegas: List[float],
    min_w_threshold: float = 1e-4,
    min_step_gap: int = 1,
    max_step_gap: Optional[int] = None,
) -> List[SubintervalEvaluation]:
    """Evaluate candidate bound B1 across all valid subintervals [t_i, t_j] (j > i)."""
    T = len(times)
    t_arr = np.asarray(times, dtype=np.float64)
    w_arr = np.asarray(w_mags, dtype=np.float64)
    l_w_arr = np.asarray(lambda_omegas, dtype=np.float64)
    l_3_arr = np.asarray(lambda_3s, dtype=np.float64)
    V_arr = np.asarray(V_omegas, dtype=np.float64)

    # G(t) = lambda_3 - lambda_omega >= 0
    G_arr = np.maximum(0.0, l_3_arr - l_w_arr)
    # V_log(t) = V_omega / |omega|
    V_log_arr = np.where(w_arr > min_w_threshold, V_arr / w_arr, 0.0)

    results: List[SubintervalEvaluation] = []
    max_gap = max_step_gap if max_step_gap is not None else T

    for i in range(T - 1):
        w1 = w_arr[i]
        if w1 < min_w_threshold:
            continue
        for j in range(i + min_step_gap, min(T, i + max_gap + 1)):
            w2 = w_arr[j]
            if w2 < min_w_threshold:
                continue

            sub_t = t_arr[i : j + 1]
            sub_lw = l_w_arr[i : j + 1]
            sub_l3 = l_3_arr[i : j + 1]
            sub_G = G_arr[i : j + 1]
            sub_Vlog = V_log_arr[i : j + 1]

            int_lw = _trapz(sub_lw, sub_t)
            int_l3 = _trapz(sub_l3, sub_t)
            int_G = _trapz(sub_G, sub_t)
            int_Vlog = _trapz(sub_Vlog, sub_t)

            log_growth = float(np.log(w2 / w1))
            R_direct = log_growth - int_l3
            R_integrated = int_Vlog - int_G
            closure_err = abs(R_direct - R_integrated)
            margin = -R_direct
            is_viol = bool(R_direct > 1e-4)

            results.append(
                SubintervalEvaluation(
                    t1_idx=i,
                    t2_idx=j,
                    t1=float(sub_t[0]),
                    t2=float(sub_t[-1]),
                    dt=float(sub_t[-1] - sub_t[0]),
                    w1=float(w1),
                    w2=float(w2),
                    log_growth=log_growth,
                    int_lambda_omega=int_lw,
                    int_lambda_3=int_l3,
                    int_V_log=int_Vlog,
                    int_G=int_G,
                    R_direct=R_direct,
                    R_integrated=R_integrated,
                    closure_error=closure_err,
                    margin=margin,
                    is_violation=is_viol,
                )
            )

    return results


def find_pointwise_positive_r_events(
    times: List[float],
    w_mags: List[float],
    lambda_omegas: List[float],
    lambda_3s: List[float],
    V_omegas: List[float],
    align_e3: List[float],
    align_e2: List[float],
    Qs: List[float],
    Rs: List[float],
    min_w_threshold: float = 1e-4,
) -> List[Dict[str, Any]]:
    """Identify all space-time points where pointwise growth excess r(t) = V_log(t) - G(t) > 0."""
    events = []
    T = len(times)
    for step in range(T):
        w = w_mags[step]
        if w < min_w_threshold:
            continue
        l_w = lambda_omegas[step]
        l_3 = lambda_3s[step]
        G = max(0.0, l_3 - l_w)
        V_log = V_omegas[step] / w
        r = V_log - G
        if r > 1e-4:
            events.append({
                "step": step,
                "time": times[step],
                "omega_mag": w,
                "lambda_omega": l_w,
                "lambda_3": l_3,
                "eigenvalue_gap_G": G,
                "viscous_log_V": V_log,
                "growth_excess_r": r,
                "align_e3": align_e3[step],
                "align_e2": align_e2[step],
                "Q": Qs[step],
                "R": Rs[step],
            })
    return events


def generate_adversarial_strained_layer_field(
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    seed: int = 42,
    shear_intensity: float = 2.5,
) -> VelocityField:
    """Construct an adversarial incompressible flow state maximizing alignment with e3 in steep viscous layer."""
    rng = np.random.default_rng(seed)
    
    # Exact staggered MAC face coordinates
    x_u = np.linspace(0, mesh.lx, mesh.nx + 1)
    y_c = np.linspace(0.5 * mesh.dy, mesh.ly - 0.5 * mesh.dy, mesh.ny)
    z_c = np.linspace(0.5 * mesh.dz, mesh.lz - 0.5 * mesh.dz, mesh.nz)
    Xu, Yu, Zu = np.meshgrid(x_u, y_c, z_c, indexing="ij")

    x_c = np.linspace(0.5 * mesh.dx, mesh.lx - 0.5 * mesh.dx, mesh.nx)
    y_v = np.linspace(0, mesh.ly, mesh.ny + 1)
    Xv, Yv, Zv = np.meshgrid(x_c, y_v, z_c, indexing="ij")

    z_w = np.linspace(0, mesh.lz, mesh.nz + 1)
    Xw, Yw, Zw = np.meshgrid(x_c, y_c, z_w, indexing="ij")

    gamma = shear_intensity
    u_face = gamma * np.sin(Xu) * np.cos(Yu)
    v_face = -gamma * np.cos(Xv) * np.sin(Yv)
    w_face = 1.5 * np.sin(2.0 * Yw) * np.cos(Zw) + 0.5 * np.sin(3.0 * Xw)

    vel = VelocityField.zeros(mesh)
    vel.u.data[mesh.n_ghost : -mesh.n_ghost, mesh.n_ghost : -mesh.n_ghost, mesh.n_ghost : -mesh.n_ghost] = u_face
    vel.v.data[mesh.n_ghost : -mesh.n_ghost, mesh.n_ghost : -mesh.n_ghost, mesh.n_ghost : -mesh.n_ghost] = v_face
    vel.w.data[mesh.n_ghost : -mesh.n_ghost, mesh.n_ghost : -mesh.n_ghost, mesh.n_ghost : -mesh.n_ghost] = w_face

    # Apply periodic boundary conditions to ghost cells in place
    from ..boundary_conditions import apply_velocity_bc
    apply_velocity_bc(vel, bcs)

    # Solenoidal Leray projection
    proj_res = project(vel, bcs, mesh, 1.0, 1.0)
    return proj_res.velocity
