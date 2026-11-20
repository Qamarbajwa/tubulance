"""Local flow-topology feature extraction for Navier-Stokes and Lagrangian tracers.

Computes local, scale-invariant, and dimensional velocity-gradient invariants,
strain-tensor eigensystems, and Q-R topological classification without any
flow-ID, seed, or global coordinate leakage.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from .lagrangian_tracking import interpolate_mac_velocity


def compute_local_velocity_gradient(
    x_pts: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    eps: float = 1e-4,
) -> np.ndarray:
    """Compute local velocity-gradient tensor grad(u)_ij = du_i / dx_j at continuous points.
    
    Parameters
    ----------
    x_pts : np.ndarray, shape (N, 3)
        Continuous spatial coordinates [x, y, z].
    velocity : VelocityField
        MAC velocity field.
    mesh : StructuredMesh3D
        Mesh specification.
    eps : float, default=1e-4
        Finite difference displacement distance.
        
    Returns
    -------
    np.ndarray, shape (N, 3, 3)
        Velocity gradient tensor A[n, i, j] = du_i / dx_j at point n.
    """
    pts = np.atleast_2d(x_pts)
    N = len(pts)
    A = np.zeros((N, 3, 3), dtype=np.float64)

    for j in range(3):
        dx_vec = np.zeros((1, 3))
        dx_vec[0, j] = eps
        v_plus = interpolate_mac_velocity(pts + dx_vec, velocity, mesh)
        v_minus = interpolate_mac_velocity(pts - dx_vec, velocity, mesh)
        # du_i / dx_j
        A[:, :, j] = (v_plus - v_minus) / (2.0 * eps)

    return A.reshape(x_pts.shape[:-1] + (3, 3)) if x_pts.ndim > 2 else A


def extract_local_topology_features(
    centroids: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    eps: float = 1e-4,
) -> np.ndarray:
    """Extract local flow-topology feature matrix at continuous object centroids.
    
    Features extracted per centroid (14 physical & dimensionless invariants):
    0.  Q-invariant: Q = 0.5 * (||Omega||^2 - ||S||^2)
    1.  R-invariant: R = -det(grad u) = -1/3 tr(S^3) - 1/4 omega^T S omega
    2.  Vieillefosse discriminant: Delta = 27 R^2 + 4 Q^3
    3.  Strain-rate magnitude: ||S||_F = sqrt(tr(S^2))
    4.  Vorticity magnitude: |omega|
    5.  Local enstrophy: 0.5 * |omega|^2
    6.  Max strain eigenvalue alpha (most extensional)
    7.  Intermediate strain eigenvalue beta
    8.  Min strain eigenvalue gamma (most compressive)
    9.  Strain anisotropy parameter s* = -3*sqrt(6)*alpha*beta*gamma / (alpha^2+beta^2+gamma^2)^1.5
    10. Vortex-strain stretching rate: lambda_omega = omega_hat^T S omega_hat
    11. Dimensionless rotation-to-strain ratio: |omega| / (sqrt(2)*||S||_F + 1e-6)
    12. Dimensionless Q: Q / (||S||_F^2 + 0.5*|omega|^2 + 1e-6)
    13. Dimensionless vortex stretching: lambda_omega / (||S||_F + 1e-6)
    
    Parameters
    ----------
    centroids : np.ndarray, shape (N, 3)
        Tracer centroids.
    velocity : VelocityField
        MAC velocity field.
    mesh : StructuredMesh3D
        Mesh specification.
        
    Returns
    -------
    np.ndarray, shape (N, 14)
        Local topology feature matrix.
    """
    pts = np.atleast_2d(centroids)
    N = len(pts)
    grad_u = compute_local_velocity_gradient(pts, velocity, mesh, eps=eps)

    feats = np.zeros((N, 14), dtype=np.float64)

    for n in range(N):
        A = grad_u[n]
        # Symmetric strain-rate tensor with exact zero-trace projection
        S_raw = 0.5 * (A + A.T)
        tr_S = np.trace(S_raw)
        S = S_raw - (tr_S / 3.0) * np.eye(3)

        # Antisymmetric rotation-rate tensor
        Omega = 0.5 * (A - A.T)

        # Vorticity vector omega = curl(u)
        omega = np.array([
            2.0 * Omega[2, 1],  # dw/dy - dv/dz
            2.0 * Omega[0, 2],  # du/dz - dw/dx
            2.0 * Omega[1, 0],  # dv/dx - du/dy
        ])
        vort_mag = float(np.linalg.norm(omega))
        enstrophy = 0.5 * vort_mag**2

        tr_S2 = float(np.trace(S @ S))
        strain_mag = float(np.sqrt(max(0.0, tr_S2)))

        # Invariants Q and R
        # Q = 0.5 * (tr(Omega^T Omega) - tr(S^2)) = 0.25 * |omega|^2 - 0.5 * tr(S^2)
        Q = 0.25 * vort_mag**2 - 0.5 * tr_S2
        
        # R = -det(A) = -1/3 tr(S^3) - 1/4 omega^T S omega
        tr_S3 = float(np.trace(S @ S @ S))
        if vort_mag > 1e-7:
            omega_hat = omega / vort_mag
            vort_stretch = float(omega_hat @ S @ omega_hat)
        else:
            omega_hat = np.zeros(3)
            vort_stretch = 0.0

        R = - (1.0 / 3.0) * tr_S3 - 0.25 * (vort_mag**2) * vort_stretch
        Delta = 27.0 * (R**2) + 4.0 * (Q**3)

        # Strain eigenvalues (sorted descending alpha >= beta >= gamma)
        eigvals = np.sort(np.linalg.eigvalsh(S))[::-1]
        alpha, beta, gamma = float(eigvals[0]), float(eigvals[1]), float(eigvals[2])

        denom_aniso = (alpha**2 + beta**2 + gamma**2)**1.5
        if denom_aniso > 1e-7:
            s_star = float(-3.0 * np.sqrt(6.0) * alpha * beta * gamma / denom_aniso)
        else:
            s_star = 0.0

        # Dimensionless ratios
        rot_strain_ratio = vort_mag / (np.sqrt(2.0) * strain_mag + 1e-6)
        dimless_Q = Q / (strain_mag**2 + 0.5 * vort_mag**2 + 1e-6)
        dimless_stretch = vort_stretch / (strain_mag + 1e-6)

        feats[n, :] = [
            Q,
            R,
            Delta,
            strain_mag,
            vort_mag,
            enstrophy,
            alpha,
            beta,
            gamma,
            s_star,
            vort_stretch,
            rot_strain_ratio,
            dimless_Q,
            dimless_stretch,
        ]

    return feats


TOPOLOGY_FEATURE_NAMES = [
    "Q_invariant",
    "R_invariant",
    "Vieillefosse_Delta",
    "strain_magnitude",
    "vorticity_magnitude",
    "local_enstrophy",
    "strain_alpha",
    "strain_beta",
    "strain_gamma",
    "anisotropy_s_star",
    "vortex_stretching_lambda_omega",
    "rotation_to_strain_ratio",
    "dimensionless_Q",
    "dimensionless_vortex_stretching",
]
