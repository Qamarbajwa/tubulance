"""Autonomous Branch NS-BLOWUP-1: Parabolic Rescaling of Extreme Events and Limiting Geometry Analysis.

Mathematical formulation:
    For an extreme space-time event at (x*, t*) with peak vorticity Omega_M = ||omega(., t*)||_infty:
    
    1. Parabolic Rescaling Parameter:
        lambda = Omega_M^(-1/2)
        
    2. Rescaled Coordinates:
        y = (x - x*) / lambda
        s = (t - t*) / lambda^2
        
    3. Rescaled Fields (preserving Navier-Stokes scale invariance):
        u^(lambda)(y, s)     = lambda * u(x* + lambda * y, t* + lambda^2 * s)
        omega^(lambda)(y, s) = lambda^2 * omega(x* + lambda * y, t* + lambda^2 * s)
        S^(lambda)(y, s)     = lambda^2 * S(x* + lambda * y, t* + lambda^2 * s)
        
    4. Normalization Property:
        ||omega^(lambda)(., 0)||_infty = 1.0 (by construction)
        
    5. Limiting Geometry Metric:
        Compare normalized vorticity profile omega^(lambda)(y) against canonical profiles:
        - 1D Gaussian Burgers Sheet: W_sheet(y) = exp(- k * y_perp^2)
        - 2D Axisymmetric Burgers Tube: W_tube(r) = exp(- k * r^2)
        Fit correlation / L2 discrepancy against limiting profiles.
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
class NSBlowup1RescaledProfile:
    """Normalized rescaled space profile at t*."""
    event_id: str
    q_max_raw: float
    rescaling_lambda: float
    rescaled_radii: np.ndarray      # y = r / lambda
    normalized_q_profile: np.ndarray # q^(lambda)(y) / q^(lambda)(0)
    normalized_l3_profile: np.ndarray
    normalized_lw_profile: np.ndarray
    rescaled_rho_profile: np.ndarray
    burgers_sheet_l2_error: float
    burgers_tube_l2_error: float
    best_fit_geometry: str          # "BURGERS_SHEET", "BURGERS_TUBE", "ASYMMETRIC"
    normalized_core_thickness_y: float


def compute_parabolic_rescaled_profile(
    center_pt: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    n_sample_radii: int = 15,
) -> NSBlowup1RescaledProfile:
    """Compute exact parabolic blow-up rescaled spatial profile around peak vorticity."""
    center_pt = np.asarray(center_pt, dtype=np.float64).reshape(3)
    
    # Extract raw vorticity grid
    q_grid, X, Y, Z = extract_field_vorticity_grid(velocity, mesh)
    q_max = float(np.max(q_grid))
    
    # Parabolic scale parameter
    lam = 1.0 / np.sqrt(max(1e-4, q_max))
    
    # Rescaled radial coordinates y in [0, 5.0]
    y_max = 5.0
    r_phys_max = y_max * lam
    radii_phys = np.linspace(0.0, min(r_phys_max, mesh.lx * 0.45), n_sample_radii)
    y_coords = radii_phys / lam
    
    # Compute isotropic radial profiles
    def _dist_periodic(c, X_arr, L):
        d = np.abs(X_arr - c)
        return np.minimum(d, L - d)

    dist_x = _dist_periodic(center_pt[0], X, mesh.lx)
    dist_y = _dist_periodic(center_pt[1], Y, mesh.ly)
    dist_z = _dist_periodic(center_pt[2], Z, mesh.lz)
    r_dist = np.sqrt(dist_x**2 + dist_y**2 + dist_z**2)

    q_prof = []
    l3_prof = []
    lw_prof = []
    rho_prof = []

    for r_val in radii_phys:
        mask = r_dist <= (r_val + 0.5 * mesh.dx)
        if not np.any(mask):
            min_idx = np.unravel_index(np.argmin(r_dist), r_dist.shape)
            mask = np.zeros_like(r_dist, dtype=bool)
            mask[min_idx] = True

        avg_q = float(np.mean(q_grid[mask]))
        
        # Pointwise state at sample point on sphere
        sample_pt = center_pt + np.array([r_val, 0.0, 0.0])
        v_st = compute_pointwise_vorticity_state(sample_pt, velocity, mesh, nu=nu)
        
        # Rescale by lambda^2
        q_rescaled = (lam**2) * avg_q
        l3_rescaled = (lam**2) * v_st.eigvals[2]
        lw_rescaled = (lam**2) * v_st.lambda_omega
        safe_l3 = l3_rescaled if abs(l3_rescaled) > 1e-6 else 1e-6
        rho = lw_rescaled / safe_l3

        q_prof.append(q_rescaled)
        l3_prof.append(l3_rescaled)
        lw_prof.append(lw_rescaled)
        rho_prof.append(rho)

    q_arr = np.array(q_prof)
    norm_q = q_arr / max(1e-6, q_arr[0])

    # Fit against Canonical Burgers Sheet: exp(-k y^2)
    # Fit k from half-width y_half
    half_mask = norm_q <= 0.50
    if np.any(half_mask):
        y_half = float(y_coords[np.argmax(half_mask)])
        k_fit = np.log(2.0) / max(1e-4, y_half**2)
    else:
        y_half = 5.0
        k_fit = 0.1

    ideal_sheet = np.exp(-k_fit * y_coords**2)
    ideal_tube = np.exp(-2.0 * k_fit * y_coords**2)

    err_sheet = float(np.mean((norm_q - ideal_sheet)**2))
    err_tube = float(np.mean((norm_q - ideal_tube)**2))

    best_geom = "BURGERS_SHEET" if err_sheet <= err_tube else "BURGERS_TUBE"

    return NSBlowup1RescaledProfile(
        event_id=f"event_q{q_max:.1f}",
        q_max_raw=q_max,
        rescaling_lambda=float(lam),
        rescaled_radii=y_coords,
        normalized_q_profile=norm_q,
        normalized_l3_profile=np.array(l3_prof),
        normalized_lw_profile=np.array(lw_prof),
        rescaled_rho_profile=np.array(rho_prof),
        burgers_sheet_l2_error=err_sheet,
        burgers_tube_l2_error=err_tube,
        best_fit_geometry=best_geom,
        normalized_core_thickness_y=y_half,
    )
