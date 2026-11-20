"""Multiscale Localized vs Global Averaging Math Module for Side Branch LA1.

Mathematical formulation:
    For a center x* and radius r:
    1. Spherical localized average:
        <f>_r(x*) = (1 / |B_r|) int_{B_r(x*)} f(x) dx
    2. Gaussian localized average:
        <f>_G,r(x*) = int f(x) * (2*pi*sigma^2)^(-3/2) exp(-|x-x*|^2 / (2*sigma^2)) dx  with sigma = r / 2
    3. Global domain average:
        <f>_Omega = (1 / |Omega|) int_Omega f(x) dx
    4. Primary ratios:
        rho_point = lambda_omega(x*) / lambda_3(x*)
        rho_RA(r) = <lambda_omega>_r / <lambda_3>_r
        rho_AR(r) = <lambda_omega / lambda_3>_r
        D_gap(r) = <lambda_3 - lambda_omega>_r
    5. Coherence radius:
        R_coh(rho0) = sup { r : rho_RA(r) >= rho0 }
    6. Local/Global contrast:
        K_f(r) = <f>_r / <f>_Omega
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, ScalarField
from .th3_topology_features import compute_local_velocity_gradient
from .th5_vorticity_math import compute_pointwise_vorticity_state


@dataclass
class MultiscaleProfile:
    """Scale profile of physical quantities around a specified center point."""
    center_pt: np.ndarray          # (3,)
    center_type: str               # 'exact_qmax', 'near_qmax', 'near_e3', 'control'
    radii: np.ndarray              # array of physical radii [r0, r1, ...]
    radii_norm: np.ndarray         # r / L_domain
    q_profile: np.ndarray          # <q>_r
    l3_profile: np.ndarray         # <lambda_3>_r
    lw_profile: np.ndarray         # <lambda_omega>_r
    rho_RA_profile: np.ndarray     # <lambda_omega>_r / <lambda_3>_r
    rho_AR_profile: np.ndarray     # <lambda_omega / lambda_3>_r
    D_gap_profile: np.ndarray      # <lambda_3 - lambda_omega>_r
    S_profile: np.ndarray          # <|S|>_r
    Q_profile: np.ndarray          # <Q>_r
    R_profile: np.ndarray          # <R>_r
    Vlog_profile: np.ndarray       # <V_log>_r
    q_global: float
    l3_global: float
    lw_global: float
    rho_global: float
    R_coh_90: float
    R_coh_80: float
    R_coh_70: float
    structure_type: str            # 'sheet', 'tube', 'mixed'


def compute_multiscale_averages_at_center(
    center_pt: np.ndarray,
    center_type: str,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    radii: Optional[List[float]] = None,
    kernel: str = "spherical",
    nu: float = 0.01,
) -> MultiscaleProfile:
    """Compute exact localized spatial averages across discrete radii r around center_pt."""
    center_pt = np.asarray(center_pt, dtype=np.float64).reshape(3)
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    lx = mesh.lx

    if radii is None:
        radii = [0.5 * dx, 1.0 * dx, 2.0 * dx, 4.0 * dx, 8.0 * dx, 0.25 * lx]

    radii_arr = np.array(radii, dtype=np.float64)
    radii_norm = radii_arr / lx

    # Coordinate grids
    xs = (np.arange(nx) + 0.5) * dx
    ys = (np.arange(ny) + 0.5) * dy
    zs = (np.arange(nz) + 0.5) * dz
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")

    # Sample grid fields
    q_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    l3_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    lw_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    Q_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    R_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    S_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    Vlog_grid = np.zeros((nx, ny, nz), dtype=np.float64)

    # Periodic minimum distance
    def _dist_periodic(c, X_arr, L):
        d = np.abs(X_arr - c)
        return np.minimum(d, L - d)

    dist_x = _dist_periodic(center_pt[0], X, mesh.lx)
    dist_y = _dist_periodic(center_pt[1], Y, mesh.ly)
    dist_z = _dist_periodic(center_pt[2], Z, mesh.lz)
    r_dist = np.sqrt(dist_x**2 + dist_y**2 + dist_z**2)

    # Sample all grid points
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                pt = np.array([xs[i], ys[j], zs[k]])
                v_st = compute_pointwise_vorticity_state(pt, velocity, mesh, nu=nu)
                q_grid[i, j, k] = v_st.omega_mag
                l3_grid[i, j, k] = v_st.eigvals[2]
                lw_grid[i, j, k] = v_st.lambda_omega
                Q_grid[i, j, k] = v_st.Q
                R_grid[i, j, k] = v_st.R
                S_grid[i, j, k] = np.sqrt(2.0 * np.sum(v_st.eigvals**2))
                Vlog_grid[i, j, k] = 0.0

    safe_l3 = np.where(np.abs(l3_grid) > 1e-6, l3_grid, 1e-6)
    rho_grid = lw_grid / safe_l3
    Dgap_grid = l3_grid - lw_grid

    # Global means
    q_global = float(np.mean(q_grid))
    l3_global = float(np.mean(l3_grid))
    lw_global = float(np.mean(lw_grid))
    rho_global = float(lw_global / max(1e-6, l3_global))

    q_prof = []
    l3_prof = []
    lw_prof = []
    rho_RA_prof = []
    rho_AR_prof = []
    D_gap_prof = []
    S_prof = []
    Q_prof = []
    R_prof = []
    Vlog_prof = []

    for r in radii:
        if kernel == "gaussian":
            sigma = max(0.5 * dx, 0.5 * r)
            w = np.exp(-0.5 * (r_dist / sigma)**2)
            w_sum = np.sum(w)
            if w_sum < 1e-12:
                w_sum = 1.0
            avg_q = float(np.sum(q_grid * w) / w_sum)
            avg_l3 = float(np.sum(l3_grid * w) / w_sum)
            avg_lw = float(np.sum(lw_grid * w) / w_sum)
            avg_rho_AR = float(np.sum(rho_grid * w) / w_sum)
            avg_Dgap = float(np.sum(Dgap_grid * w) / w_sum)
            avg_S = float(np.sum(S_grid * w) / w_sum)
            avg_Q = float(np.sum(Q_grid * w) / w_sum)
            avg_R = float(np.sum(R_grid * w) / w_sum)
            avg_Vlog = float(np.sum(Vlog_grid * w) / w_sum)
        else: # spherical top-hat
            mask = r_dist <= r
            if not np.any(mask):
                min_idx = np.unravel_index(np.argmin(r_dist), r_dist.shape)
                mask = np.zeros_like(r_dist, dtype=bool)
                mask[min_idx] = True

            avg_q = float(np.mean(q_grid[mask]))
            avg_l3 = float(np.mean(l3_grid[mask]))
            avg_lw = float(np.mean(lw_grid[mask]))
            avg_rho_AR = float(np.mean(rho_grid[mask]))
            avg_Dgap = float(np.mean(Dgap_grid[mask]))
            avg_S = float(np.mean(S_grid[mask]))
            avg_Q = float(np.mean(Q_grid[mask]))
            avg_R = float(np.mean(R_grid[mask]))
            avg_Vlog = float(np.mean(Vlog_grid[mask]))

        avg_rho_RA = float(avg_lw / max(1e-6, avg_l3))

        q_prof.append(avg_q)
        l3_prof.append(avg_l3)
        lw_prof.append(avg_lw)
        rho_RA_prof.append(avg_rho_RA)
        rho_AR_prof.append(avg_rho_AR)
        D_gap_prof.append(avg_Dgap)
        S_prof.append(avg_S)
        Q_prof.append(avg_Q)
        R_prof.append(avg_R)
        Vlog_prof.append(avg_Vlog)

    rho_RA_arr = np.array(rho_RA_prof)

    # Compute coherence radii
    def _find_r_coh(thresh):
        valid = radii_arr[rho_RA_arr >= thresh]
        return float(np.max(valid)) if len(valid) > 0 else 0.0

    R_coh_90 = _find_r_coh(0.90)
    R_coh_80 = _find_r_coh(0.80)
    R_coh_70 = _find_r_coh(0.70)

    # Structure type from local Hessian / invariants at center
    center_state = compute_pointwise_vorticity_state(center_pt, velocity, mesh, nu=nu)
    if center_state.Q > 0 and center_state.R < 0:
        struct_type = "tube"
    elif center_state.Q < 0:
        struct_type = "sheet"
    else:
        struct_type = "mixed"

    return MultiscaleProfile(
        center_pt=center_pt,
        center_type=center_type,
        radii=radii_arr,
        radii_norm=radii_norm,
        q_profile=np.array(q_prof),
        l3_profile=np.array(l3_prof),
        lw_profile=np.array(lw_prof),
        rho_RA_profile=rho_RA_arr,
        rho_AR_profile=np.array(rho_AR_prof),
        D_gap_profile=np.array(D_gap_prof),
        S_profile=np.array(S_prof),
        Q_profile=np.array(Q_prof),
        R_profile=np.array(R_prof),
        Vlog_profile=np.array(Vlog_prof),
        q_global=q_global,
        l3_global=l3_global,
        lw_global=lw_global,
        rho_global=rho_global,
        R_coh_90=R_coh_90,
        R_coh_80=R_coh_80,
        R_coh_70=R_coh_70,
        structure_type=struct_type,
    )
