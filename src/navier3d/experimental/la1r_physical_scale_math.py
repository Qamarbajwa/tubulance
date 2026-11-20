"""Physical-Scale Localization and Enstrophy-Weighted Concentration Math Module for Program LA1-R.

Mathematical formulation:
    1. Enstrophy-weighted realized stretching:
        Lambda_omega(r) = int phi_r |omega|^2 lambda_omega dx / int phi_r |omega|^2 dx
        Lambda_3(r)     = int phi_r |omega|^2 lambda_3 dx / int phi_r |omega|^2 dx
        D_weighted(r)   = Lambda_omega(r) / Lambda_3(r)

    2. Localized vortex stretching production:
        P_stretch(r) = int phi_r |omega|^2 lambda_omega dx

    3. Localized enstrophy:
        E(r) = 1/2 int phi_r |omega|^2 dx

    4. Superlevel sets:
        Omega_alpha = { x : |omega(x)| >= alpha * q_max }
        Volume fraction, transverse thickness, aspect ratio.

    5. Resolution classification:
        PHYSICALLY CONVERGED: R_coh(phys) converges to a constant physical length independent of dx.
        GRID-LOCKED: R_coh(phys) ~ C * dx (shrinks strictly proportionally to grid spacing).
        UNDER-RESOLVED: No systematic scaling.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, ScalarField
from .th5_vorticity_math import compute_pointwise_vorticity_state


@dataclass
class LA1RPhysicalProfile:
    """Physical scale and enstrophy-weighted profile record."""
    center_pt: np.ndarray
    q_max: float
    radii_phys: np.ndarray
    radii_dx: np.ndarray
    radii_norm: np.ndarray
    q_profile: np.ndarray
    Lambda_omega_profile: np.ndarray
    Lambda_3_profile: np.ndarray
    D_weighted_profile: np.ndarray
    P_stretch_profile: np.ndarray
    E_profile: np.ndarray
    superlevel_vol_frac_90: float
    superlevel_vol_frac_80: float
    sheet_thickness_phys: float
    sheet_thickness_dx: float
    R_coh_phys_80: float
    R_coh_dx_80: float


def evaluate_la1r_physical_profile(
    center_pt: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    radii_phys: Optional[List[float]] = None,
    nu: float = 0.01,
) -> LA1RPhysicalProfile:
    """Compute exact enstrophy-weighted stretching, production, and physical thickness."""
    center_pt = np.asarray(center_pt, dtype=np.float64).reshape(3)
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    lx = mesh.lx

    if radii_phys is None:
        # Standard physical radii spanning 0.1 to 1.5
        radii_phys = [0.05 * lx, 0.10 * lx, 0.15 * lx, 0.25 * lx, 0.40 * lx]

    radii_arr = np.array(radii_phys, dtype=np.float64)
    radii_dx = radii_arr / dx
    radii_norm = radii_arr / lx

    xs = (np.arange(nx) + 0.5) * dx
    ys = (np.arange(ny) + 0.5) * dy
    zs = (np.arange(nz) + 0.5) * dz
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")

    # Grid quantities
    q_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    l3_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    lw_grid = np.zeros((nx, ny, nz), dtype=np.float64)

    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                pt = np.array([xs[i], ys[j], zs[k]])
                v_st = compute_pointwise_vorticity_state(pt, velocity, mesh, nu=nu)
                q_grid[i, j, k] = v_st.omega_mag
                l3_grid[i, j, k] = v_st.eigvals[2]
                lw_grid[i, j, k] = v_st.lambda_omega

    q_max = float(np.max(q_grid))
    enstrophy_grid = q_grid**2

    # Periodic distance
    def _dist_periodic(c, X_arr, L):
        d = np.abs(X_arr - c)
        return np.minimum(d, L - d)

    dist_x = _dist_periodic(center_pt[0], X, mesh.lx)
    dist_y = _dist_periodic(center_pt[1], Y, mesh.ly)
    dist_z = _dist_periodic(center_pt[2], Z, mesh.lz)
    r_dist = np.sqrt(dist_x**2 + dist_y**2 + dist_z**2)

    q_prof = []
    Lw_prof = []
    L3_prof = []
    Dw_prof = []
    P_prof = []
    E_prof = []

    for r in radii_phys:
        mask = r_dist <= r
        if not np.any(mask):
            min_idx = np.unravel_index(np.argmin(r_dist), r_dist.shape)
            mask = np.zeros_like(r_dist, dtype=bool)
            mask[min_idx] = True

        local_ens = enstrophy_grid[mask]
        ens_sum = np.sum(local_ens)
        if ens_sum < 1e-12:
            ens_sum = 1.0

        avg_q = float(np.mean(q_grid[mask]))
        Lw = float(np.sum(local_ens * lw_grid[mask]) / ens_sum)
        L3 = float(np.sum(local_ens * l3_grid[mask]) / ens_sum)
        Dw = float(Lw / max(1e-6, L3))
        P_str = float(np.sum(local_ens * lw_grid[mask]) * (dx * dy * dz))
        E_val = float(0.5 * np.sum(local_ens) * (dx * dy * dz))

        q_prof.append(avg_q)
        Lw_prof.append(Lw)
        L3_prof.append(L3)
        Dw_prof.append(Dw)
        P_prof.append(P_str)
        E_prof.append(E_val)

    # Superlevel sets
    vol_90 = float(np.mean(q_grid >= 0.90 * q_max))
    vol_80 = float(np.mean(q_grid >= 0.80 * q_max))

    # Transverse thickness (number of cells across which q >= 0.80 q_max along normal)
    # Estimate equivalent sphere/slab thickness: t ~ vol^(1/3) * L
    sheet_thickness_phys = float(vol_80**(1.0 / 3.0) * lx)
    sheet_thickness_dx = sheet_thickness_phys / dx

    Dw_arr = np.array(Dw_prof)
    valid_80 = radii_arr[Dw_arr >= 0.80]
    R_coh_phys_80 = float(np.max(valid_80)) if len(valid_80) > 0 else 0.0
    R_coh_dx_80 = R_coh_phys_80 / dx

    return LA1RPhysicalProfile(
        center_pt=center_pt,
        q_max=q_max,
        radii_phys=radii_arr,
        radii_dx=radii_dx,
        radii_norm=radii_norm,
        q_profile=np.array(q_prof),
        Lambda_omega_profile=np.array(Lw_prof),
        Lambda_3_profile=np.array(L3_prof),
        D_weighted_profile=Dw_arr,
        P_stretch_profile=np.array(P_prof),
        E_profile=np.array(E_prof),
        superlevel_vol_frac_90=vol_90,
        superlevel_vol_frac_80=vol_80,
        sheet_thickness_phys=sheet_thickness_phys,
        sheet_thickness_dx=sheet_thickness_dx,
        R_coh_phys_80=R_coh_phys_80,
        R_coh_dx_80=R_coh_dx_80,
    )
