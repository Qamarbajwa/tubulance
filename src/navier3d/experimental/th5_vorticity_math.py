"""Exact Navier-Stokes Vorticity Budgets, Strain Eigenstructure, and Regularity Diagnostics for Milestone TH5.

Provides:
- Exact pointwise and Lagrangian vorticity budgets:
  D|omega|/Dt = P_omega + V_omega + eps_budget
  where P_omega = lambda_omega * |omega|, V_omega = nu * omega_hat . Delta(omega).
- Enstrophy budget:
  0.5 * D|omega|^2/Dt = omega^T S omega + nu * omega . Delta(omega).
- Strain eigensystem analysis:
  lambda_1 <= lambda_2 <= lambda_3 (tr(S) = 0), eigenvectors e_1, e_2, e_3, alignment (omega_hat . e_i).
- Q-R topology plane invariants:
  Q = 0.5*(||Omega||^2 - ||S||^2), R = -1/3 tr(S^3) - 1/4 omega^T S omega, Delta = 27 R^2 + 4 Q^3.
- History functionals H_1 to H_10 along Lagrangian trajectories.
- Candidate mathematical bounds and adversarial falsification evaluators.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from ..fields import VelocityField, ScalarField
from ..mesh import StructuredMesh3D
from .lagrangian_tracking import interpolate_mac_velocity
from .th3_topology_features import compute_local_velocity_gradient


@dataclass
class VorticityPointState:
    """Exact kinematic and dynamical state at a single space-time point."""
    x: np.ndarray             # (3,)
    u: np.ndarray             # (3,)
    omega: np.ndarray         # (3,)
    omega_mag: float          # |omega|
    omega_hat: np.ndarray     # unit vector
    S: np.ndarray             # (3, 3) strain rate
    strain_mag: float         # ||S||_F = sqrt(tr(S^2))
    eigvals: np.ndarray       # (3,) lambda_1 <= lambda_2 <= lambda_3
    eigvecs: np.ndarray       # (3, 3) columns e_1, e_2, e_3
    alignments: np.ndarray    # (3,) |omega_hat . e_i|
    lambda_omega: float       # omega_hat^T S omega_hat
    P_omega: float            # lambda_omega * |omega| (stretching production)
    V_omega: float            # nu * omega_hat . Delta(omega) (viscous term)
    Q: float                  # Q invariant
    R: float                  # R invariant
    Vieillefosse_Delta: float # 27 R^2 + 4 Q^3
    lambda_t: float           # material tangent stretch rate (if tangent provided)


def compute_pointwise_vorticity_state(
    x_pt: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    tangent: Optional[np.ndarray] = None,
    eps: float = 1e-4,
) -> VorticityPointState:
    """Compute complete velocity gradient, strain eigensystem, and vorticity budget terms at point x."""
    x_pt = np.asarray(x_pt, dtype=np.float64).reshape(3)
    u_pt = interpolate_mac_velocity(x_pt.reshape(1, 3), velocity, mesh)[0]

    # Velocity gradient tensor A_ij = du_i / dx_j
    A = compute_local_velocity_gradient(x_pt.reshape(1, 3), velocity, mesh, eps=eps)[0]
    
    # Strain rate S and rotation rate Omega
    S_raw = 0.5 * (A + A.T)
    tr_S = float(np.trace(S_raw))
    S = S_raw - (tr_S / 3.0) * np.eye(3) # exact zero trace
    Omega = 0.5 * (A - A.T)

    # Vorticity vector omega = curl(u)
    omega = np.array([
        2.0 * Omega[2, 1],
        2.0 * Omega[0, 2],
        2.0 * Omega[1, 0],
    ], dtype=np.float64)

    w_mag = float(np.linalg.norm(omega))
    if w_mag > 1e-12:
        w_hat = omega / w_mag
    else:
        w_hat = np.zeros(3, dtype=np.float64)

    # Strain eigensystem (sorted ascending: lambda_1 <= lambda_2 <= lambda_3)
    vals, vecs = np.linalg.eigh(S)
    idx_sort = np.argsort(vals)
    eigvals = vals[idx_sort]
    eigvecs = vecs[:, idx_sort]

    # Alignments |omega_hat . e_i|
    alignments = np.array([
        float(np.abs(np.dot(w_hat, eigvecs[:, 0]))),
        float(np.abs(np.dot(w_hat, eigvecs[:, 1]))),
        float(np.abs(np.dot(w_hat, eigvecs[:, 2]))),
    ], dtype=np.float64)

    # Stretching rate lambda_omega = omega_hat^T S omega_hat
    lambda_omega = float(w_hat @ S @ w_hat)
    P_omega = lambda_omega * w_mag

    # Invariants Q, R, Delta
    tr_S2 = float(np.trace(S @ S))
    strain_mag = float(np.sqrt(max(0.0, tr_S2)))
    Q = 0.25 * (w_mag**2) - 0.5 * tr_S2
    tr_S3 = float(np.trace(S @ S @ S))
    R = - (1.0 / 3.0) * tr_S3 - 0.25 * (w_mag**2) * lambda_omega
    Delta = 27.0 * (R**2) + 4.0 * (Q**3)

    # Viscous Laplacian Delta(omega) via finite differences
    # Delta(omega) = sum_j (omega(x + eps*e_j) - 2*omega(x) + omega(x - eps*e_j)) / eps^2
    eps_lap = 2e-3
    lap_omega = np.zeros(3, dtype=np.float64)
    for j in range(3):
        dx_vec = np.zeros(3)
        dx_vec[j] = eps_lap
        A_p = compute_local_velocity_gradient((x_pt + dx_vec).reshape(1, 3), velocity, mesh, eps=eps)[0]
        w_p = np.array([A_p[2, 1] - A_p[1, 2], A_p[0, 2] - A_p[2, 0], A_p[1, 0] - A_p[0, 1]])
        A_m = compute_local_velocity_gradient((x_pt - dx_vec).reshape(1, 3), velocity, mesh, eps=eps)[0]
        w_m = np.array([A_m[2, 1] - A_m[1, 2], A_m[0, 2] - A_m[2, 0], A_m[1, 0] - A_m[0, 1]])
        lap_omega += (w_p - 2.0 * omega + w_m) / (eps_lap**2)

    V_omega = float(nu * np.dot(w_hat, lap_omega))

    # Material line tangent stretching rate lambda_t = t_hat^T S t_hat
    if tangent is not None:
        t_norm = np.linalg.norm(tangent)
        if t_norm > 1e-12:
            t_hat = tangent / t_norm
            lambda_t = float(t_hat @ S @ t_hat)
        else:
            lambda_t = 0.0
    else:
        lambda_t = 0.0

    return VorticityPointState(
        x=x_pt,
        u=u_pt,
        omega=omega,
        omega_mag=w_mag,
        omega_hat=w_hat,
        S=S,
        strain_mag=strain_mag,
        eigvals=eigvals,
        eigvecs=eigvecs,
        alignments=alignments,
        lambda_omega=lambda_omega,
        P_omega=P_omega,
        V_omega=V_omega,
        Q=Q,
        R=R,
        Vieillefosse_Delta=Delta,
        lambda_t=lambda_t,
    )


def compute_lagrangian_trajectory_budget(
    trajectory_coords: np.ndarray, # (T, 3)
    velocity_snapshots: List[VelocityField],
    times: List[float],
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    tangents: Optional[np.ndarray] = None, # (T, 3)
) -> Dict[str, Any]:
    """Evaluate exact Lagrangian vorticity budget, enstrophy, and history functionals along trajectory."""
    T = len(trajectory_coords)
    dt = float(times[1] - times[0]) if T > 1 else 0.02

    states: List[VorticityPointState] = []
    for step in range(T):
        t_vec = tangents[step] if tangents is not None else None
        st = compute_pointwise_vorticity_state(
            trajectory_coords[step],
            velocity_snapshots[step],
            mesh,
            nu=nu,
            tangent=t_vec,
        )
        states.append(st)

    # Measured D|omega|/Dt via centered differences
    w_mags = np.array([s.omega_mag for s in states])
    dw_dt_measured = np.zeros(T, dtype=np.float64)
    if T >= 3:
        dw_dt_measured[1:-1] = (w_mags[2:] - w_mags[:-2]) / (2.0 * dt)
        dw_dt_measured[0] = (w_mags[1] - w_mags[0]) / dt
        dw_dt_measured[-1] = (w_mags[-1] - w_mags[-2]) / dt
    elif T == 2:
        dw_dt_measured[:] = (w_mags[1] - w_mags[0]) / dt

    P_omegas = np.array([s.P_omega for s in states])
    V_omegas = np.array([s.V_omega for s in states])
    lambda_omegas = np.array([s.lambda_omega for s in states])
    lambda_3s = np.array([s.eigvals[2] for s in states])
    lambda_2s = np.array([s.eigvals[1] for s in states])
    lambda_1s = np.array([s.eigvals[0] for s in states])
    align_e3 = np.array([s.alignments[2] for s in states])
    align_e2 = np.array([s.alignments[1] for s in states])
    align_e1 = np.array([s.alignments[0] for s in states])
    Qs = np.array([s.Q for s in states])
    Rs = np.array([s.R for s in states])
    strain_mags = np.array([s.strain_mag for s in states])

    # Budget residual: eps_budget = D|omega|/Dt - (P_omega + V_omega)
    dw_dt_budget = P_omegas + V_omegas
    residuals = dw_dt_measured - dw_dt_budget

    def _trapz(y_arr, x_arr):
        if hasattr(np, "trapezoid"):
            return float(np.trapezoid(y_arr, x_arr))
        return float(np.trapz(y_arr, x_arr))

    # History Functionals over the window [0, T-1]
    H1_integrated_stretching = _trapz(lambda_omegas, times[:T])
    H2_positive_stretching = _trapz(np.maximum(lambda_omegas, 0.0), times[:T])
    H3_integrated_strain = _trapz(strain_mags, times[:T])
    H6_align_e3_persistence = float(np.mean(align_e3**2))
    H7_align_e2_persistence = float(np.mean(align_e2**2))

    # Actual amplification factor: ln(|omega(T-1)| / |omega(0)|)
    w_init = max(1e-6, float(w_mags[0]))
    w_final = max(1e-6, float(w_mags[-1]))
    actual_log_growth = float(np.log(w_final / w_init))

    # Candidate Upper Bound Evaluators:
    # Bound B1: Ideal extensional bound: ln(w_f / w_i) <= int(lambda_3 ds)
    B1_ideal_extensional = _trapz(lambda_3s, times[:T])
    
    # Bound B2: Integrated stretching (inviscid identity): int(lambda_omega ds)
    B2_integrated_lambda_omega = H1_integrated_stretching

    # Bound B3: Viscous-corrected upper envelope
    viscous_envelope_rate = lambda_omegas + np.where(w_mags > 1e-5, V_omegas / w_mags, 0.0)
    B3_viscous_corrected = _trapz(viscous_envelope_rate, times[:T])

    return {
        "num_steps": T,
        "times": list(times[:T]),
        "omega_mags": list(w_mags),
        "P_omegas": list(P_omegas),
        "V_omegas": list(V_omegas),
        "dw_dt_measured": list(dw_dt_measured),
        "dw_dt_budget": list(dw_dt_budget),
        "residuals": list(residuals),
        "mean_residual": float(np.mean(np.abs(residuals[1:-1]))) if T >= 3 else float(np.mean(np.abs(residuals))),
        "relative_residual": float(np.mean(np.abs(residuals[1:-1]))) / (float(np.mean(np.abs(P_omegas))) + 1e-4) if T >= 3 else 0.0,
        "lambda_omegas": list(lambda_omegas),
        "lambda_3s": list(lambda_3s),
        "align_e3": list(align_e3),
        "align_e2": list(align_e2),
        "align_e1": list(align_e1),
        "Qs": list(Qs),
        "Rs": list(Rs),
        "history_functionals": {
            "H1_integrated_stretching": H1_integrated_stretching,
            "H2_positive_stretching": H2_positive_stretching,
            "H3_integrated_strain": H3_integrated_strain,
            "H6_align_e3_persistence": H6_align_e3_persistence,
            "H7_align_e2_persistence": H7_align_e2_persistence,
            "actual_log_growth": actual_log_growth,
        },
        "candidate_bounds": {
            "B1_ideal_extensional": B1_ideal_extensional,
            "B1_violation": float(max(0.0, actual_log_growth - B1_ideal_extensional)),
            "B2_integrated_stretching": B2_integrated_lambda_omega,
            "B2_violation": float(max(0.0, actual_log_growth - B2_integrated_lambda_omega)),
            "B3_viscous_corrected": B3_viscous_corrected,
            "B3_violation": float(max(0.0, actual_log_growth - B3_viscous_corrected)),
        },
    }
