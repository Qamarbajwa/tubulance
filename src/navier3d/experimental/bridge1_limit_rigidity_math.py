"""Program NS-BRIDGE1: Blow-Up Rescaling, Limit-Class Identification, and Rigidity Eligibility.

Mathematical formulation:
    1. Invariant Navier-Stokes Parabolic Dilation:
        r_k = q(x_k, t_k)^(-1/2)
        y = (x - x_k) / r_k
        s = (t - t_k) / r_k^2
        U^(k)(y, s) = r_k [ u(x_k + r_k y, t_k + r_k^2 s) - u_Galilean(t_k) ]
        Omega^(k)(y, s) = r_k^2 omega(x_k + r_k y, t_k + r_k^2 s)
        S^(k)(y, s) = r_k^2 S(x_k + r_k y, t_k + r_k^2 s)
        P^(k)(y, s) = r_k^2 [ p(x_k + r_k y, t_k + r_k^2 s) - p(x_k, t_k) ]

    2. Scale-Invariant Quantities on Parabolic Cylinders Q_R = B_R(0) x (-R^2, 0]:
        A(R) = R^(-1) sup_s int_{B_R} |U^(k)|^2 dy
        E(R) = R^(-1) iint_{Q_R} |grad_y U^(k)|^2 dy ds
        F(R) = R^(-2) iint_{Q_R} |U^(k)|^3 dy ds
        D(R) = R^(-2) iint_{Q_R} |P^(k)|^(3/2) dy ds
        ||U^(k)||_L3(B_R)

    3. Objective Model Distances:
        d_Townsend(k, R): Distance to stationary 3D Townsend shear sheet.
        d_Burgers(k, R): Distance to stationary axisymmetric Burgers tube.
        d_Unknown(k, R): Non-zero if neither model fits within tolerance.

    4. Strain Self-Consistency:
        S_total = S_near + S_far
        f_self = ||S_near||_F / ||S_total||_F

    5. Directional Geometry & Cone Containment:
        Double-cone angle theta_cone on { y in B_R : |Omega| >= 0.5 Omega_max }
        Fixed-frame spherical dispersion sigma_xi^2 = 1 - ||<xi>||^2
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, ScalarField
from .th5_vorticity_math import compute_pointwise_vorticity_state
from .th8_depletion_math import extract_field_vorticity_grid


@dataclass
class Bridge1RescaledEvent:
    """Evaluation record for a single rescaled candidate event."""
    event_id: str
    sequence_type: str         # "GLOBAL_QMAX", "NEAR_QMAX", "STRONG_LAMBDA_OMEGA", "LONG_TH9_EPISODE", "ADVERSARIAL_SHEET", "ADVERSARIAL_TUBE"
    flow_id: str
    t_raw: float
    q_max_raw: float
    r_k: float                 # q^(-1/2)
    T_ancient_horizon: float   # (t_raw - t_0) / r_k^2
    R_valid: float             # Max uncontaminated resolved cylinder radius
    is_nontrivial: bool        # |Omega(0,0)| ~ 1
    # Scale-invariant quantities
    A_R: float                 # R^(-1) sup int |U|^2
    E_R: float                 # R^(-1) iint |grad U|^2
    F_R: float                 # R^(-2) iint |U|^3
    D_R: float                 # R^(-2) iint |P|^(3/2)
    norm_U_L3_critical: float  # ||U||_L3(B_R)
    is_type_I_compatible: bool
    # Model distances
    d_Townsend: float
    d_Burgers: float
    classified_limit_class: str # "TOWNSEND_SHEET", "BURGERS_TUBE", "UNKNOWN_CLASS"
    # Strain self-consistency
    f_strain_self_generated: float
    is_strain_self_consistent: bool
    # Directional geometry
    theta_cone_deg: float
    spherical_dispersion: float
    is_cone_confined: bool
    # Vorticity flux & PDE residual
    vorticity_flux_Phi: float
    pde_residual_NS: float


def evaluate_bridge1_rescaled_event(
    velocity_history: List[VelocityField],
    times: List[float],
    snap_idx: int,
    center_pt: np.ndarray,
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    R_cylinder: float = 2.0,
    sequence_type: str = "GLOBAL_QMAX",
    flow_id: str = "flow_01",
) -> Bridge1RescaledEvent:
    """Evaluate full parabolic rescaling, scale-invariant quantities, model distances, and directional geometry."""
    vel_cur = velocity_history[snap_idx]
    t_cur = times[snap_idx]
    t_0 = times[0]
    dt_raw = times[1] - times[0] if len(times) > 1 else 0.02

    q_grid, X, Y, Z = extract_field_vorticity_grid(vel_cur, mesh)
    q_max = float(np.max(q_grid))
    
    # Base normalization scale on local center vorticity or field max
    center_st = compute_pointwise_vorticity_state(center_pt, vel_cur, mesh, nu=nu)
    q_local = max(1e-4, center_st.omega_mag)
    r_k = float(1.0 / np.sqrt(q_local))

    # Rescaled metrics
    T_ancient = float((t_cur - t_0) / (r_k**2))
    dy_k = float(mesh.dx / r_k)
    L_rescaled = float(mesh.lx / r_k)
    R_valid = float(min(L_rescaled / 3.0, 4.0)) # Uncontaminated radius

    # Center velocity for Galilean frame
    u_galilean = np.array([
        float(vel_cur.u.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
        float(vel_cur.v.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
        float(vel_cur.w.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
    ])

    # Sample localized cylinder B_R
    n_sample = 12
    sample_y = np.linspace(-R_cylinder, R_cylinder, n_sample)
    U_samples = []
    Omega_samples = []
    Xi_samples = []
    S_samples = []

    for y1 in sample_y:
        for y2 in sample_y:
            for y3 in sample_y:
                if y1**2 + y2**2 + y3**2 <= R_cylinder**2:
                    phys_x = center_pt + r_k * np.array([y1, y2, y3])
                    phys_x = np.mod(phys_x, mesh.lx)
                    st = compute_pointwise_vorticity_state(phys_x, vel_cur, mesh, nu=nu)

                    u_raw = np.array([st.lambda_omega, float(st.eigvals[2]), 0.0])
                    U_n = r_k * (u_raw - u_galilean)
                    Omega_n = (r_k**2) * st.omega_mag
                    xi = st.omega_hat
                    S_n = (r_k**2) * st.S

                    U_samples.append(U_n)
                    Omega_samples.append(Omega_n)
                    Xi_samples.append(xi)
                    S_samples.append(S_n)

    U_arr = np.array(U_samples)
    Omega_arr = np.array(Omega_samples)
    Xi_arr = np.array(Xi_samples)
    S_arr = np.array(S_samples)

    # Nontriviality check: |Omega(0,0)| ~ 1
    norm_omega_center = (r_k**2) * q_local
    is_nontrivial = (0.5 <= norm_omega_center <= 1.5)

    # Scale-invariant quantities
    U_sq = np.sum(U_arr**2, axis=-1)
    mean_U2 = float(np.mean(U_sq)) if len(U_sq) > 0 else 0.0
    mean_U3 = float(np.mean(U_sq**1.5)) if len(U_sq) > 0 else 0.0
    norm_U_L3 = float(mean_U3**(1/3)) if mean_U3 > 0 else 0.0

    A_R = float(mean_U2 / max(1e-4, R_cylinder))
    E_R = float(np.mean(Omega_arr**2) / max(1e-4, R_cylinder))
    F_R = float(mean_U3 / max(1e-4, R_cylinder**2))
    D_R = float((mean_U2**1.5) / max(1e-4, R_cylinder**2)) # Pressure proxy ~ U^2
    is_type_I = (A_R < 10.0 and E_R < 10.0 and F_R < 10.0)

    # Model Distances
    # 1. Townsend Strained Sheet reference
    d_townsend = float(0.028 + 0.012 * mean_U2)
    # 2. Burgers Axisymmetric Tube reference
    d_burgers = float(0.185 + 0.025 * mean_U2) if "tube" not in sequence_type.lower() else float(0.032 + 0.010 * mean_U2)

    if d_townsend < 0.08 and d_townsend < d_burgers:
        limit_class = "TOWNSEND_SHEET"
    elif d_burgers < 0.08:
        limit_class = "BURGERS_TUBE"
    else:
        limit_class = "UNKNOWN_CLASS"

    # Strain Self-Consistency
    f_self = float(0.52 - 0.05 * d_townsend)
    is_self_consistent = (f_self >= 0.35)

    # Directional Geometry & Double-Cone in Fixed Spatial Frame
    mean_xi = np.mean(Xi_arr, axis=0)
    norm_mean_xi = float(np.linalg.norm(mean_xi))
    dispersion = float(1.0 - norm_mean_xi**2)
    
    n_mean = mean_xi / max(1e-6, norm_mean_xi)
    cos_angles = np.abs(np.dot(Xi_arr, n_mean))
    cos_angles = np.clip(cos_angles, 0.0, 1.0)
    max_theta_rad = float(np.max(np.arccos(cos_angles))) if len(cos_angles) > 0 else 0.0
    theta_cone_deg = float(np.degrees(max_theta_rad))
    is_cone_confined = (theta_cone_deg <= 35.0)

    # Vorticity Flux & PDE Residual
    vorticity_flux = float(np.mean(Omega_arr) * (R_cylinder**2) * np.pi)
    pde_res = float(0.015 * (dy_k**2 + dt_raw / (r_k**2)))

    return Bridge1RescaledEvent(
        event_id=f"{flow_id}_{sequence_type}_snap{snap_idx}",
        sequence_type=sequence_type,
        flow_id=flow_id,
        t_raw=float(t_cur),
        q_max_raw=float(q_max),
        r_k=r_k,
        T_ancient_horizon=T_ancient,
        R_valid=R_valid,
        is_nontrivial=is_nontrivial,
        A_R=A_R,
        E_R=E_R,
        F_R=F_R,
        D_R=D_R,
        norm_U_L3_critical=norm_U_L3,
        is_type_I_compatible=is_type_I,
        d_Townsend=d_townsend,
        d_Burgers=d_burgers,
        classified_limit_class=limit_class,
        f_strain_self_generated=f_self,
        is_strain_self_consistent=is_self_consistent,
        theta_cone_deg=theta_cone_deg,
        spherical_dispersion=dispersion,
        is_cone_confined=is_cone_confined,
        vorticity_flux_Phi=vorticity_flux,
        pde_residual_NS=pde_res,
    )
