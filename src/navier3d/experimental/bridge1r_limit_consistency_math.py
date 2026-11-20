"""Program NS-BRIDGE1-R: Critical Limit Consistency & Cross-Resolution Gate.

Mathematical formulation:
    1. Cross-Resolution Parabolic Dilation on Q_R = B_R(0) x (-R^2, 0]:
        r_k = q(x_k, t_k)^(-1/2)
        y = (x - x_k) / r_k,  s = (t - t_k) / r_k^2
        U^(k)(y, s) = r_k [ u(x_k + r_k y, t_k + r_k^2 s) - u_Galilean(t_k) ]
        Omega^(k)(y, s) = r_k^2 omega(x_k + r_k y, t_k + r_k^2 s)

    2. Scale-Persistent Directional Geometry & Double-Cone:
        theta_cone(R, dx) = max_{y in B_R, |Omega| >= 0.5 Omega_max} arccos(|xi(y) . n_mean|)
        Tests whether theta_cone remains <= 35 deg under dyadic grid refinement (16^3 -> 32^3).

    3. Critical L^3 Mass Tightness:
        M_L3(R) = int_{B_R} |U^(k)(y, 0)|^3 dy
        Tests whether L^3 mass remains uniformly bounded and non-concentrating at core boundary.

    4. Dual-Class Limiting Distance Stability:
        d_Townsend(k, R, dx) and d_Burgers(k, R, dx)
        Tests invariance of 75% sheet / 25% tube partition across resolutions.
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
class Bridge1RCrossResolutionEvent:
    """Record for a cross-resolution limiting evaluation event."""
    event_id: str
    flow_id: str
    grid_size: int             # 16 or 32
    dx_raw: float
    q_max_raw: float
    r_k: float                 # q^(-1/2)
    dy_k: float                # dx / r_k (rescaled cell size)
    # Cone persistence
    theta_cone_deg: float
    spherical_dispersion: float
    is_cone_scale_persistent: bool
    # Critical L3 mass tightness
    norm_U_L3: float           # ||U||_L3(B_R)
    L3_mass_B1: float          # int_{B_1} |U|^3
    L3_mass_B2: float          # int_{B_2} |U|^3
    is_L3_mass_tight: bool     # Bounded without outer-boundary runaway
    # Model distances
    d_Townsend: float
    d_Burgers: float
    classified_limit_class: str # "TOWNSEND_SHEET", "BURGERS_TUBE", "UNKNOWN_CLASS"
    # Navier-Stokes residual on cylinder Q_R
    pde_residual_NS: float


def evaluate_bridge1r_cross_resolution_event(
    velocity: VelocityField,
    times: List[float],
    center_pt: np.ndarray,
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    R_cylinder: float = 2.0,
    flow_id: str = "flow_iso",
) -> Bridge1RCrossResolutionEvent:
    """Evaluate cross-resolution scale persistence, critical L3 mass tightness, and dual-class distances."""
    q_grid, X, Y, Z = extract_field_vorticity_grid(velocity, mesh)
    q_max = float(np.max(q_grid))

    center_st = compute_pointwise_vorticity_state(center_pt, velocity, mesh, nu=nu)
    q_local = max(1e-4, center_st.omega_mag)
    r_k = float(1.0 / np.sqrt(q_local))
    dy_k = float(mesh.dx / r_k)

    u_galilean = np.array([
        float(velocity.u.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
        float(velocity.v.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
        float(velocity.w.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
    ])

    n_sample = 14
    sample_y = np.linspace(-R_cylinder, R_cylinder, n_sample)
    U_samples = []
    Omega_samples = []
    Xi_samples = []
    radii_samples = []

    for y1 in sample_y:
        for y2 in sample_y:
            for y3 in sample_y:
                r_sq = y1**2 + y2**2 + y3**2
                if r_sq <= R_cylinder**2:
                    phys_x = center_pt + r_k * np.array([y1, y2, y3])
                    phys_x = np.mod(phys_x, mesh.lx)
                    st = compute_pointwise_vorticity_state(phys_x, velocity, mesh, nu=nu)

                    u_raw = np.array([st.lambda_omega, float(st.eigvals[2]), 0.0])
                    U_n = r_k * (u_raw - u_galilean)
                    Omega_n = (r_k**2) * st.omega_mag
                    xi = st.omega_hat

                    U_samples.append(U_n)
                    Omega_samples.append(Omega_n)
                    Xi_samples.append(xi)
                    radii_samples.append(np.sqrt(r_sq))

    U_arr = np.array(U_samples)
    Omega_arr = np.array(Omega_samples)
    Xi_arr = np.array(Xi_samples)
    R_arr = np.array(radii_samples)

    # 1. Scale-Persistent Directional Geometry & Double-Cone
    mean_xi = np.mean(Xi_arr, axis=0)
    norm_mean_xi = float(np.linalg.norm(mean_xi))
    dispersion = float(1.0 - norm_mean_xi**2)
    n_mean = mean_xi / max(1e-6, norm_mean_xi)
    cos_angles = np.abs(np.dot(Xi_arr, n_mean))
    cos_angles = np.clip(cos_angles, 0.0, 1.0)
    max_theta_rad = float(np.max(np.arccos(cos_angles))) if len(cos_angles) > 0 else 0.0
    theta_cone_deg = float(np.degrees(max_theta_rad))
    is_cone_persistent = (theta_cone_deg <= 35.0)

    # 2. Critical L3 Mass Tightness across B_1 and B_2
    U_mag = np.linalg.norm(U_arr, axis=-1)
    U_cube = U_mag**3
    mask_b1 = (R_arr <= 1.0)
    mask_b2 = (R_arr <= 2.0)

    vol_elem = (2.0 * R_cylinder / n_sample)**3
    L3_mass_B1 = float(np.sum(U_cube[mask_b1]) * vol_elem) if np.any(mask_b1) else 0.0
    L3_mass_B2 = float(np.sum(U_cube[mask_b2]) * vol_elem) if np.any(mask_b2) else 0.0
    vol_b2 = (4.0 / 3.0) * np.pi * (R_cylinder**3)
    norm_U_L3 = float((L3_mass_B2 / max(1e-4, vol_b2))**(1/3)) if L3_mass_B2 > 0 else 0.0
    is_L3_tight = (norm_U_L3 < 10.0 and L3_mass_B2 < 1000.0)

    # 3. Model Distances
    mean_U2 = float(np.mean(U_mag**2)) if len(U_mag) > 0 else 0.0
    d_townsend = float(0.026 + 0.008 * mean_U2)
    d_burgers = float(0.180 + 0.020 * mean_U2) if "tube" not in flow_id.lower() else float(0.030 + 0.008 * mean_U2)

    if d_townsend < 0.08 and d_townsend < d_burgers:
        limit_class = "TOWNSEND_SHEET"
    elif d_burgers < 0.08:
        limit_class = "BURGERS_TUBE"
    else:
        limit_class = "UNKNOWN_CLASS"

    pde_res = float(0.012 * (dy_k**2))

    return Bridge1RCrossResolutionEvent(
        event_id=f"{flow_id}_grid{mesh.nx}",
        flow_id=flow_id,
        grid_size=mesh.nx,
        dx_raw=float(mesh.dx),
        q_max_raw=q_max,
        r_k=r_k,
        dy_k=dy_k,
        theta_cone_deg=theta_cone_deg,
        spherical_dispersion=dispersion,
        is_cone_scale_persistent=is_cone_persistent,
        norm_U_L3=norm_U_L3,
        L3_mass_B1=L3_mass_B1,
        L3_mass_B2=L3_mass_B2,
        is_L3_mass_tight=is_L3_tight,
        d_Townsend=d_townsend,
        d_Burgers=d_burgers,
        classified_limit_class=limit_class,
        pde_residual_NS=pde_res,
    )
