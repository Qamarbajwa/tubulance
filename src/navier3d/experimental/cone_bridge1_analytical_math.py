"""Program NS-CONE-BRIDGE-1: High-Vorticity Time-Slice Cone Geometry, Local Absolute Vorticity Flux, and Moving/Structure-Wise Axis Reduction.

Mathematical Formulation & Primary Source Audit:
    Primary Source Reference Correction:
        Zhen Lei, Xiao Ren, Gang Tian
        "A geometric characterization of potential Navier-Stokes singularities"
        arXiv:2501.10939, 2025.

    1. Theorem 1.1 (Fixed-Axis Double-Cone):
        For a suitable weak solution in Q(1), if exists fixed e in S^2, delta > 0, M > 0 such that:
            |omega| <= M  OR  |xi x e| <= 1 - delta
        for all regular points in Q(1), then (0,0) is regular.

    2. Corollary 1.6 (Time-Slice Pairwise Angle Criterion):
        For all t in (-1, 0), if for all x, y in B_1 with omega(x,t) != 0, omega(y,t) != 0:
            |xi(x,t) x xi(y,t)| <= 1 - delta_0
        then (0,0) is a regular point.
        Proof mechanism: At each time slice t, e(t) is chosen from the time-slice geometry.
        Time-independence of e is NOT required for the spatial flux bound!

    3. Low-Vorticity Commutator & Truncation:
        omega_hi = chi_M(q) omega
        div(omega_hi) = grad(chi_M(q)) . omega = chi_M'(q) (grad q . omega)
        Low-vorticity mass bounded by M * Vol(B_R).

    4. Multi-Structure Internal vs External Disorder:
        Internal Disorder: sigma_int(j) = max_{x in Omega_j} arccos(|xi(x) . e_j|)
        External Disorder: Theta_ext = max_{j,k} arccos(|e_j . e_k|)
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
class TimeSlicePairwiseResult:
    """Result of time-slice pairwise direction analysis at threshold tau = q/q_max."""
    flow_id: str
    time: float
    threshold_tau: float
    num_points: int
    sup_pairwise_cross: float       # sup |xi(x) x xi(y)|
    delta_pair: float               # 1 - sup_pairwise_cross
    is_pairwise_satisfied: bool     # delta_pair > 0.05
    mean_pairwise_angle_deg: float
    max_pairwise_angle_deg: float


@dataclass
class StructureDisorderResult:
    """Segmentation of high-vorticity regions into internal vs external disorder."""
    flow_id: str
    time: float
    threshold_tau: float
    num_components: int
    mean_internal_disorder_deg: float
    max_internal_disorder_deg: float
    external_disorder_deg: float    # Max angle between component axes
    total_high_q_mass: float
    is_multi_structure_segregated: bool # High external, low internal disorder


@dataclass
class AbsoluteVorticityFluxResult:
    """Evaluation of absolute vorticity flux vs directional confinement."""
    flow_id: str
    time: float
    R_radius: float
    abs_vorticity_flux: float       # int_{B_R} |omega| dy
    axial_vorticity_flux: float     # int_{B_R} |omega . e*| dy
    flux_bound_ratio: float         # abs_flux / axial_flux
    theta_cone_deg: float
    delta_margin: float


def compute_projective_cross_product(xi1: np.ndarray, xi2: np.ndarray) -> float:
    """Compute projective cross-product |xi1 x xi2| = sqrt(1 - (xi1 . xi2)^2)."""
    dot_val = np.clip(np.abs(np.dot(xi1, xi2)), 0.0, 1.0)
    return float(np.sqrt(max(0.0, 1.0 - dot_val**2)))


def audit_time_slice_pairwise_directions(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    center_pt: np.ndarray,
    nu: float = 0.01,
    R_cylinder: float = 2.0,
    threshold_tau: float = 0.75,
    flow_id: str = "flow_iso",
    time_val: float = 0.0,
) -> TimeSlicePairwiseResult:
    """Evaluate Lei-Ren-Tian Corollary 1.6 pairwise cross-product on high-vorticity set."""
    q_grid, X, Y, Z = extract_field_vorticity_grid(velocity, mesh)
    q_max = float(np.max(q_grid))
    r_k = float(1.0 / np.sqrt(max(1e-4, q_max)))

    n_sample = 12
    sample_y = np.linspace(-R_cylinder, R_cylinder, n_sample)
    xi_list = []

    for y1 in sample_y:
        for y2 in sample_y:
            for y3 in sample_y:
                if y1**2 + y2**2 + y3**2 <= R_cylinder**2:
                    phys_x = center_pt + r_k * np.array([y1, y2, y3])
                    phys_x = np.mod(phys_x, mesh.lx)
                    st = compute_pointwise_vorticity_state(phys_x, velocity, mesh, nu=nu)

                    if st.omega_mag >= threshold_tau * q_max:
                        xi_list.append(st.omega_hat)

    if len(xi_list) <= 1:
        # Trivial single point or empty
        return TimeSlicePairwiseResult(
            flow_id=flow_id,
            time=time_val,
            threshold_tau=threshold_tau,
            num_points=len(xi_list),
            sup_pairwise_cross=0.0,
            delta_pair=1.0,
            is_pairwise_satisfied=True,
            mean_pairwise_angle_deg=0.0,
            max_pairwise_angle_deg=0.0,
        )

    # Subsample if too large for N^2 pairwise comparisons
    if len(xi_list) > 100:
        indices = np.random.choice(len(xi_list), 100, replace=False)
        xi_sub = [xi_list[i] for i in indices]
    else:
        xi_sub = xi_list

    N = len(xi_sub)
    cross_vals = []
    angle_vals = []

    for i in range(N):
        for j in range(i + 1, N):
            cp = compute_projective_cross_product(xi_sub[i], xi_sub[j])
            dot = np.clip(np.abs(np.dot(xi_sub[i], xi_sub[j])), 0.0, 1.0)
            ang = float(np.degrees(np.arccos(dot)))
            cross_vals.append(cp)
            angle_vals.append(ang)

    sup_cross = float(np.max(cross_vals))
    delta_pair = float(1.0 - sup_cross)
    mean_ang = float(np.mean(angle_vals))
    max_ang = float(np.max(angle_vals))
    is_satisfied = (delta_pair > 0.05 and max_ang < 75.0)

    return TimeSlicePairwiseResult(
        flow_id=flow_id,
        time=time_val,
        threshold_tau=threshold_tau,
        num_points=len(xi_list),
        sup_pairwise_cross=sup_cross,
        delta_pair=delta_pair,
        is_pairwise_satisfied=is_satisfied,
        mean_pairwise_angle_deg=mean_ang,
        max_pairwise_angle_deg=max_ang,
    )


def audit_internal_vs_external_disorder(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    center_pt: np.ndarray,
    nu: float = 0.01,
    R_cylinder: float = 2.0,
    threshold_tau: float = 0.50,
    flow_id: str = "flow_iso",
    time_val: float = 0.0,
) -> StructureDisorderResult:
    """Decompose directional disorder into within-structure (internal) vs between-structure (external)."""
    q_grid, X, Y, Z = extract_field_vorticity_grid(velocity, mesh)
    q_max = float(np.max(q_grid))
    r_k = float(1.0 / np.sqrt(max(1e-4, q_max)))

    n_sample = 12
    sample_y = np.linspace(-R_cylinder, R_cylinder, n_sample)
    pts = []
    directions = []
    mags = []

    for y1 in sample_y:
        for y2 in sample_y:
            for y3 in sample_y:
                if y1**2 + y2**2 + y3**2 <= R_cylinder**2:
                    phys_x = center_pt + r_k * np.array([y1, y2, y3])
                    phys_x = np.mod(phys_x, mesh.lx)
                    st = compute_pointwise_vorticity_state(phys_x, velocity, mesh, nu=nu)

                    if st.omega_mag >= threshold_tau * q_max:
                        pts.append(np.array([y1, y2, y3]))
                        directions.append(st.omega_hat)
                        mags.append(st.omega_mag)

    if len(pts) < 4:
        return StructureDisorderResult(
            flow_id=flow_id,
            time=time_val,
            threshold_tau=threshold_tau,
            num_components=1,
            mean_internal_disorder_deg=0.0,
            max_internal_disorder_deg=0.0,
            external_disorder_deg=0.0,
            total_high_q_mass=float(np.sum(mags)) if len(mags) > 0 else 0.0,
            is_multi_structure_segregated=False,
        )

    # Simple spatial clustering into 2 components based on spatial partition (e.g. y1 > 0 vs y1 <= 0)
    pts_arr = np.array(pts)
    dir_arr = np.array(directions)
    mags_arr = np.array(mags)

    # Cluster by sign of primary coordinate y1
    c1_mask = pts_arr[:, 0] >= 0.0
    c2_mask = ~c1_mask

    comp_axes = []
    internal_spreads = []

    for mask in [c1_mask, c2_mask]:
        if np.sum(mask) >= 2:
            sub_dirs = dir_arr[mask]
            M = np.einsum("ni,nj->ij", sub_dirs, sub_dirs) / len(sub_dirs)
            eigvals, eigvecs = np.linalg.eigh(M)
            axis = eigvecs[:, -1]
            axis = axis / np.linalg.norm(axis)
            comp_axes.append(axis)

            cos_ang = np.abs(np.dot(sub_dirs, axis))
            spread = float(np.degrees(np.max(np.arccos(np.clip(cos_ang, 0.0, 1.0)))))
            internal_spreads.append(spread)

    if len(comp_axes) >= 2:
        ext_cos = np.abs(np.dot(comp_axes[0], comp_axes[1]))
        ext_angle = float(np.degrees(np.arccos(np.clip(ext_cos, 0.0, 1.0))))
    else:
        ext_angle = 0.0

    mean_int = float(np.mean(internal_spreads)) if len(internal_spreads) > 0 else 0.0
    max_int = float(np.max(internal_spreads)) if len(internal_spreads) > 0 else 0.0
    is_segregated = (ext_angle > 40.0 and mean_int < 35.0)

    return StructureDisorderResult(
        flow_id=flow_id,
        time=time_val,
        threshold_tau=threshold_tau,
        num_components=len(comp_axes),
        mean_internal_disorder_deg=mean_int,
        max_internal_disorder_deg=max_int,
        external_disorder_deg=ext_angle,
        total_high_q_mass=float(np.sum(mags_arr)),
        is_multi_structure_segregated=is_segregated,
    )


def audit_absolute_vorticity_flux(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    center_pt: np.ndarray,
    nu: float = 0.01,
    R_radius: float = 1.5,
    flow_id: str = "flow_iso",
    time_val: float = 0.0,
) -> AbsoluteVorticityFluxResult:
    """Measure local absolute vorticity flux vs axial flux."""
    q_grid, X, Y, Z = extract_field_vorticity_grid(velocity, mesh)
    q_max = float(np.max(q_grid))
    r_k = float(1.0 / np.sqrt(max(1e-4, q_max)))

    n_sample = 12
    sample_y = np.linspace(-R_radius, R_radius, n_sample)
    vol_elem = (2.0 * R_radius / n_sample)**3

    abs_flux = 0.0
    xi_list = []
    mag_list = []

    for y1 in sample_y:
        for y2 in sample_y:
            for y3 in sample_y:
                if y1**2 + y2**2 + y3**2 <= R_radius**2:
                    phys_x = center_pt + r_k * np.array([y1, y2, y3])
                    phys_x = np.mod(phys_x, mesh.lx)
                    st = compute_pointwise_vorticity_state(phys_x, velocity, mesh, nu=nu)

                    abs_flux += st.omega_mag * vol_elem
                    xi_list.append(st.omega_hat)
                    mag_list.append(st.omega_mag)

    if len(xi_list) == 0:
        return AbsoluteVorticityFluxResult(
            flow_id=flow_id,
            time=time_val,
            R_radius=R_radius,
            abs_vorticity_flux=0.0,
            axial_vorticity_flux=0.0,
            flux_bound_ratio=1.0,
            theta_cone_deg=0.0,
            delta_margin=1.0,
        )

    # Compute optimal axis e*
    Xi_arr = np.array(xi_list)
    M = np.einsum("ni,nj->ij", Xi_arr, Xi_arr) / len(Xi_arr)
    eigvals, eigvecs = np.linalg.eigh(M)
    e_opt = eigvecs[:, -1]
    e_opt = e_opt / np.linalg.norm(e_opt)

    axial_flux = 0.0
    for xi, mag in zip(xi_list, mag_list):
        axial_flux += mag * np.abs(np.dot(xi, e_opt)) * vol_elem

    cos_angles = np.abs(np.dot(Xi_arr, e_opt))
    theta_cone_deg = float(np.degrees(np.max(np.arccos(np.clip(cos_angles, 0.0, 1.0)))))
    delta_margin = float(1.0 - np.sin(np.radians(theta_cone_deg)))
    bound_ratio = float(abs_flux / max(1e-4, axial_flux))

    return AbsoluteVorticityFluxResult(
        flow_id=flow_id,
        time=time_val,
        R_radius=R_radius,
        abs_vorticity_flux=abs_flux,
        axial_vorticity_flux=axial_flux,
        flux_bound_ratio=bound_ratio,
        theta_cone_deg=theta_cone_deg,
        delta_margin=delta_margin,
    )
