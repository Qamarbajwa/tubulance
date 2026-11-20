"""Forensic Recheck of Vorticity-Direction and Eigenframe Dynamics for Program TH9-R.

Mathematical formulation:
    Vorticity: omega = q * xi  with q = |omega|, xi = omega / q
    D omega / D t = S omega + nu Delta omega

    Direction Evolution:
        D xi / D t = R_strain + R_visc
    where:
        R_strain = (I - xi xi^T) S xi = S xi - lambda_omega xi
        R_visc = (nu / q) (I - xi xi^T) Delta omega = (nu / q) [ Delta omega - (xi . Delta omega) xi ]
        lambda_omega = xi^T S xi

    Orthogonality properties (exact):
        xi . R_strain = 0
        xi . R_visc = 0
        xi . (D xi / D t) = 0

    Alignment weight a_3 = (xi . e_3)^2 Evolution:
        D a_3 / D t = T_xi_strain + T_xi_visc + T_frame
    where:
        T_xi_strain = 2 (xi . e_3) (R_strain . e_3)
        T_xi_visc   = 2 (xi . e_3) (R_visc . e_3)
        T_frame     = 2 (xi . e_3) (xi . D e_3 / D t)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, ScalarField
from .th3_topology_features import compute_local_velocity_gradient
from .th5_vorticity_math import compute_pointwise_vorticity_state
from .th7_viscous_influx_math import compute_pointwise_viscous_decomposition
from .th9_persistence_math import compute_pressure_hessian_at_point


@dataclass
class TH9RDirectionForensicState:
    """Forensic evaluation record for a single space-time point."""
    x: np.ndarray             # (3,)
    q: float                  # |omega|
    xi: np.ndarray            # unit vorticity (3,)
    lambda_1: float           # smallest eigenvalue
    lambda_2: float           # intermediate eigenvalue
    lambda_3: float           # largest eigenvalue
    lambda_omega: float       # xi^T S xi
    rho: float                # lambda_omega / lambda_3
    a1: float                 # (xi . e1)^2
    a2: float                 # (xi . e2)^2
    a3: float                 # (xi . e3)^2
    R_strain: np.ndarray      # S xi - lambda_omega xi (3,)
    R_visc: np.ndarray        # (nu/q) (Delta omega - (xi . Delta omega) xi) (3,)
    D_xi_Dt: np.ndarray       # R_strain + R_visc (3,)
    D_e3_Dt: np.ndarray       # D e3 / D t (3,)
    ortho_xi_Dxi: float       # |xi . D_xi_Dt|
    ortho_xi_Rstrain: float   # |xi . R_strain|
    ortho_xi_Rvisc: float     # |xi . R_visc|
    T_xi_strain: float        # 2 (xi . e3) (R_strain . e3)
    T_xi_visc: float          # 2 (xi . e3) (R_visc . e3)
    T_xi_total: float         # T_xi_strain + T_xi_visc
    T_frame: float            # 2 (xi . e3) (xi . D e3 / D t)
    Da3_Dt: float             # T_xi_total + T_frame
    closure_error: float      # |Da3_Dt - (T_xi_strain + T_xi_visc + T_frame)|
    norm_R_strain: float      # ||R_strain||
    norm_R_visc: float        # ||R_visc||
    norm_De3_Dt: float        # ||D e3 / D t||
    Pi_13: float              # e1^T H_p e3
    Pi_23: float              # e2^T H_p e3
    Pi_33: float              # e3^T H_p e3
    frame_rot_rate: float     # ||W_ij||_F
    h_xi: float               # xi . curl(xi)


def evaluate_th9r_forensic_state(
    x_pt: np.ndarray,
    velocity: VelocityField,
    pressure: Optional[ScalarField],
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    eps: Optional[float] = None,
) -> TH9RDirectionForensicState:
    """Evaluate exact 3-way alignment torque decomposition and orthogonality properties."""
    x_pt = np.asarray(x_pt, dtype=np.float64).reshape(3)

    v_state = compute_pointwise_vorticity_state(x_pt, velocity, mesh, nu=nu)
    decomp = compute_pointwise_viscous_decomposition(x_pt, velocity, mesh, nu=nu)

    l1, l2, l3 = v_state.eigvals
    e1, e2, e3 = v_state.eigvecs.T
    xi = v_state.omega_hat
    q = v_state.omega_mag
    S = v_state.S

    a1 = float(v_state.alignments[0]**2)
    a2 = float(v_state.alignments[1]**2)
    a3 = float(v_state.alignments[2]**2)
    l_w = float(v_state.lambda_omega)
    safe_l3 = l3 if abs(l3) > 1e-6 else 1e-6
    rho = float(l_w / safe_l3)

    # 1. R_strain and R_visc
    S_xi = S @ xi
    R_strain = S_xi - l_w * xi

    lap_w = decomp.lap_omega
    xi_dot_lap = float(np.dot(xi, lap_w))
    visc_perp = (lap_w - xi_dot_lap * xi) / max(1e-6, q)
    R_visc = nu * visc_perp

    D_xi_Dt = R_strain + R_visc

    # Orthogonality checks
    ortho_xi_Dxi = float(abs(np.dot(xi, D_xi_Dt)))
    ortho_xi_Rstrain = float(abs(np.dot(xi, R_strain)))
    ortho_xi_Rvisc = float(abs(np.dot(xi, R_visc)))

    # 2. Pressure Hessian H_p
    if pressure is not None:
        Hp, tr_Hp = compute_pressure_hessian_at_point(x_pt, pressure, mesh, eps=eps)
    else:
        Hp = - (S @ S) + np.eye(3) * (2.0 * v_state.Q / 3.0)
        tr_Hp = 2.0 * v_state.Q

    # 3. Eigenframe rotation
    A = compute_local_velocity_gradient(x_pt.reshape(1, 3), velocity, mesh, eps=1e-4)[0]
    Omega_mat = 0.5 * (A - A.T)
    DS_Dt = - (S @ S + Omega_mat @ Omega_mat) - Hp

    gap_31 = max(1e-4, l3 - l1)
    gap_32 = max(1e-4, l3 - l2)
    gap_21 = max(1e-4, l2 - l1)

    m_13 = float(e1 @ DS_Dt @ e3)
    m_23 = float(e2 @ DS_Dt @ e3)
    m_12 = float(e1 @ DS_Dt @ e2)

    D_e3_Dt = (m_13 / gap_31) * e1 + (m_23 / gap_32) * e2

    # Torques
    xi_dot_e3 = float(np.dot(xi, e3))
    T_xi_strain = float(2.0 * xi_dot_e3 * np.dot(R_strain, e3))
    T_xi_visc   = float(2.0 * xi_dot_e3 * np.dot(R_visc, e3))
    T_xi_total  = T_xi_strain + T_xi_visc
    T_frame     = float(2.0 * xi_dot_e3 * np.dot(xi, D_e3_Dt))
    Da3_Dt      = T_xi_total + T_frame
    closure_err = float(abs(Da3_Dt - (T_xi_strain + T_xi_visc + T_frame)))

    # Norms
    norm_R_strain = float(np.linalg.norm(R_strain))
    norm_R_visc   = float(np.linalg.norm(R_visc))
    norm_De3_Dt   = float(np.linalg.norm(D_e3_Dt))

    # Pressure Hessian in eigenframe
    Pi_13 = float(e1 @ Hp @ e3)
    Pi_23 = float(e2 @ Hp @ e3)
    Pi_33 = float(e3 @ Hp @ e3)

    W_12 = m_12 / gap_21
    W_13 = m_13 / gap_31
    W_23 = m_23 / gap_32
    frame_rot_rate = float(np.sqrt(W_12**2 + W_13**2 + W_23**2))

    # Twist density h_xi = xi . curl(xi)
    grad_xi = decomp.grad_xi
    curl_xi = np.array([
        grad_xi[2, 1] - grad_xi[1, 2],
        grad_xi[0, 2] - grad_xi[2, 0],
        grad_xi[1, 0] - grad_xi[0, 1]
    ], dtype=np.float64)
    h_xi = float(np.dot(xi, curl_xi))

    return TH9RDirectionForensicState(
        x=x_pt,
        q=q,
        xi=xi,
        lambda_1=l1,
        lambda_2=l2,
        lambda_3=l3,
        lambda_omega=l_w,
        rho=rho,
        a1=a1,
        a2=a2,
        a3=a3,
        R_strain=R_strain,
        R_visc=R_visc,
        D_xi_Dt=D_xi_Dt,
        D_e3_Dt=D_e3_Dt,
        ortho_xi_Dxi=ortho_xi_Dxi,
        ortho_xi_Rstrain=ortho_xi_Rstrain,
        ortho_xi_Rvisc=ortho_xi_Rvisc,
        T_xi_strain=T_xi_strain,
        T_xi_visc=T_xi_visc,
        T_xi_total=T_xi_total,
        T_frame=T_frame,
        Da3_Dt=Da3_Dt,
        closure_error=closure_err,
        norm_R_strain=norm_R_strain,
        norm_R_visc=norm_R_visc,
        norm_De3_Dt=norm_De3_Dt,
        Pi_13=Pi_13,
        Pi_23=Pi_23,
        Pi_33=Pi_33,
        frame_rot_rate=frame_rot_rate,
        h_xi=h_xi,
    )
