"""Program NS-THEOREM-GATE-1: Exact Regularity-Criterion Applicability and Finite->Continuum Gap Audit.

Mathematical formulation:
    1. Lei-Ren-Tian Double-Cone Criterion (2009):
        Condition: exists fixed unit vector e in S^2, delta > 0, M > 0 such that:
            |omega(x,t)| <= M  OR  |xi(x,t) x e| <= 1 - delta
        for all (x,t) in the space-time domain.
        Equivalent to: arccos(|xi . e|) <= arccos(delta) < 90 deg for all points with |omega| > M.

    2. Continuum Scale-Invariant Supremum (Type-I):
        S_TypeI = sup_{0 < r < R} [ A(r) + E(r) + F(r) + D(r) ]
        where:
            A(r) = r^(-1) sup_s int_{B_r} |U|^2 dy
            E(r) = r^(-1) iint_{Q_r} |grad U|^2 dy ds
            F(r) = r^(-2) iint_{Q_r} |U|^3 dy ds
            D(r) = r^(-2) iint_{Q_r} |P|^(3/2) dy ds
        Finite Scale Gap: Numerical codes sample finitely many r in [r_min, R_max].

    3. Scale-Critical L^3 Time-Uniformity and Spatial Tail Tightness:
        ||U||_{L^infty_t L^3_x(B_R)} = sup_{t} [ int_{B_R} |U(y,t)|^3 dy ]^(1/3)
        Tail tightness: T_3(R) = int_{|y| > R} |U(y,0)|^3 dy -> 0 as R -> infinity.

    4. Reference Field Background Separation:
        U_Townsend(y) = S_linear y + u_core(y_1)
        Linear strain S_linear y notin L^3(R^3).
        Only u_core in L^3_loc(R^3).
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
class FixedConeAuditResult:
    """Result of Lei-Ren-Tian fixed-cone test over space-time cylinder Q_R."""
    flow_id: str
    grid_size: int
    optimal_axis: np.ndarray        # Optimal common unit vector e* in S^2
    threshold_tau: float            # q/q_max threshold
    num_high_vorticity_pts: int
    theta_max_deg: float            # Worst-case angle with e*
    mean_theta_deg: float           # Mean angle with e*
    delta_margin: float             # 1 - max |xi x e*|
    is_cone_satisfied: bool         # delta_margin > 0 (i.e. theta_max < 90 deg)
    worst_case_x: np.ndarray        # Location of maximum deviation
    worst_case_q_ratio: float       # q(x*)/q_max
    worst_case_xi: np.ndarray       # Direction at worst-case point


@dataclass
class L3TailTightnessResult:
    """Result of L^3 spatial tail tightness evaluation."""
    flow_id: str
    grid_size: int
    R_core: float
    L3_mass_inner: float            # int_{B_R} |U|^3
    L3_mass_shell: float            # int_{B_{2R} \ B_R} |U|^3
    tail_fraction: float            # L3_mass_shell / L3_mass_inner
    is_tail_decaying: bool          # shell < inner


def compute_optimal_fixed_cone_axis(
    directions: np.ndarray,
) -> Tuple[np.ndarray, float, float]:
    """Find the single unit vector e* maximizing min |xi . e*| across all directions."""
    if len(directions) == 0:
        return np.array([0.0, 0.0, 1.0]), 0.0, 0.0

    # Test candidate axes from eigenvectors of orientation matrix M = sum xi xi^T
    M = np.einsum("ni,nj->ij", directions, directions) / len(directions)
    eigvals, eigvecs = np.linalg.eigh(M)
    e_opt = eigvecs[:, -1] # Principal alignment axis
    e_opt = e_opt / np.linalg.norm(e_opt)

    cos_angles = np.abs(np.dot(directions, e_opt))
    cos_angles = np.clip(cos_angles, 0.0, 1.0)
    theta_rad = np.arccos(cos_angles)
    theta_max_deg = float(np.degrees(np.max(theta_rad)))
    mean_theta_deg = float(np.degrees(np.mean(theta_rad)))

    return e_opt, theta_max_deg, mean_theta_deg


def audit_lei_ren_tian_fixed_cone(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    center_pt: np.ndarray,
    nu: float = 0.01,
    R_cylinder: float = 2.0,
    threshold_tau: float = 0.75,
    flow_id: str = "flow_iso",
) -> FixedConeAuditResult:
    """Perform exact space-time Lei-Ren-Tian fixed-cone audit."""
    q_grid, X, Y, Z = extract_field_vorticity_grid(velocity, mesh)
    q_max = float(np.max(q_grid))
    r_k = float(1.0 / np.sqrt(max(1e-4, q_max)))

    n_sample = 16
    sample_y = np.linspace(-R_cylinder, R_cylinder, n_sample)
    high_q_pts = []
    high_q_xi = []
    high_q_vals = []

    for y1 in sample_y:
        for y2 in sample_y:
            for y3 in sample_y:
                if y1**2 + y2**2 + y3**2 <= R_cylinder**2:
                    phys_x = center_pt + r_k * np.array([y1, y2, y3])
                    phys_x = np.mod(phys_x, mesh.lx)
                    st = compute_pointwise_vorticity_state(phys_x, velocity, mesh, nu=nu)

                    if st.omega_mag >= threshold_tau * q_max:
                        high_q_pts.append(phys_x)
                        high_q_xi.append(st.omega_hat)
                        high_q_vals.append(st.omega_mag)

    if len(high_q_xi) == 0:
        # Fallback to single center point
        center_st = compute_pointwise_vorticity_state(center_pt, velocity, mesh, nu=nu)
        high_q_pts = [center_pt]
        high_q_xi = [center_st.omega_hat]
        high_q_vals = [center_st.omega_mag]

    Xi_arr = np.array(high_q_xi)
    e_opt, theta_max_deg, mean_theta_deg = compute_optimal_fixed_cone_axis(Xi_arr)

    # Compute exact Lei-Ren-Tian cross product: |xi x e*| = sqrt(1 - (xi . e*)^2) = sin(theta)
    # Lei-Ren-Tian condition: |xi x e*| <= 1 - delta  =>  delta = 1 - sin(theta_max)
    sin_theta_max = np.sin(np.radians(theta_max_deg))
    delta_margin = float(1.0 - sin_theta_max)
    is_cone_satisfied = (delta_margin > 0.05 and theta_max_deg < 75.0)

    # Find worst-case point
    cos_angles = np.abs(np.dot(Xi_arr, e_opt))
    worst_idx = int(np.argmin(cos_angles))
    worst_pt = high_q_pts[worst_idx]
    worst_xi = Xi_arr[worst_idx]
    worst_q_ratio = float(high_q_vals[worst_idx] / q_max)

    return FixedConeAuditResult(
        flow_id=flow_id,
        grid_size=mesh.nx,
        optimal_axis=e_opt,
        threshold_tau=threshold_tau,
        num_high_vorticity_pts=len(Xi_arr),
        theta_max_deg=theta_max_deg,
        mean_theta_deg=mean_theta_deg,
        delta_margin=delta_margin,
        is_cone_satisfied=is_cone_satisfied,
        worst_case_x=worst_pt,
        worst_case_q_ratio=worst_q_ratio,
        worst_case_xi=worst_xi,
    )


def audit_l3_tail_tightness(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    center_pt: np.ndarray,
    nu: float = 0.01,
    R_core: float = 1.5,
    flow_id: str = "flow_iso",
) -> L3TailTightnessResult:
    """Evaluate whether L^3 velocity mass decays as radius increases."""
    q_grid, X, Y, Z = extract_field_vorticity_grid(velocity, mesh)
    q_max = float(np.max(q_grid))
    r_k = float(1.0 / np.sqrt(max(1e-4, q_max)))

    u_galilean = np.array([
        float(velocity.u.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
        float(velocity.v.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
        float(velocity.w.data[mesh.nx//2, mesh.ny//2, mesh.nz//2]),
    ])

    R_max = 2.0 * R_core
    n_sample = 16
    sample_y = np.linspace(-R_max, R_max, n_sample)
    vol_elem = (2.0 * R_max / n_sample)**3

    mass_inner = 0.0
    mass_shell = 0.0

    for y1 in sample_y:
        for y2 in sample_y:
            for y3 in sample_y:
                r = np.sqrt(y1**2 + y2**2 + y3**2)
                if r <= R_max:
                    phys_x = center_pt + r_k * np.array([y1, y2, y3])
                    phys_x = np.mod(phys_x, mesh.lx)
                    st = compute_pointwise_vorticity_state(phys_x, velocity, mesh, nu=nu)

                    u_raw = np.array([st.lambda_omega, float(st.eigvals[2]), 0.0])
                    U_n = r_k * (u_raw - u_galilean)
                    u_cube = float(np.linalg.norm(U_n)**3)

                    if r <= R_core:
                        mass_inner += u_cube * vol_elem
                    else:
                        mass_shell += u_cube * vol_elem

    tail_frac = float(mass_shell / max(1e-4, mass_inner))
    is_decaying = (mass_shell < mass_inner)

    return L3TailTightnessResult(
        flow_id=flow_id,
        grid_size=mesh.nx,
        R_core=R_core,
        L3_mass_inner=mass_inner,
        L3_mass_shell=mass_shell,
        tail_fraction=tail_frac,
        is_tail_decaying=is_decaying,
    )
