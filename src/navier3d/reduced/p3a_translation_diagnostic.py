"""Milestone P3-A: Cross-Seed Phase / Translation Alignment Causal Diagnostic.

This module implements the diagnostic algorithms to determine whether
unseen-seed POD generalization failure is caused by spatial phase / translational
misalignment in the homogeneous periodic channel directions (x, z).

Constraints:
- Only translates in homogeneous directions x, z (Delta_y = 0 strictly).
- Preserves discrete solenoidality under periodic Fourier phase shifts.
- Computes canonical MAC energy inner products and Grassmannian chordal/geodesic/spectral distances.
- Performs both integer-grid FFT cross-correlation and continuous subgrid optimization.
"""
from __future__ import annotations

from typing import Tuple, Dict, Any, List, Optional
import numpy as np
from scipy.optimize import minimize

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from .solenoidal_basis import PODSolenoidalBasis, mac_to_cell_centers
from .w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm


# ============================================================================
# 1. Continuous Periodic Shift via 2D Fourier Phase Shifting (x, z)
# ============================================================================

def fourier_shift_2d_xz(
    field_3d: np.ndarray,
    dx_shift: float,
    dz_shift: float,
    lx: float,
    lz: float,
) -> np.ndarray:
    """Apply a continuous periodic translation in (x, z) to a 3D field array of shape (nx, ny, nz).

    Uses 2D FFT along axes 0 and 2. The wall-normal axis 1 (y) is untouched (Delta_y = 0).
    """
    nx, ny, nz = field_3d.shape
    kx = 2.0 * np.pi * np.fft.fftfreq(nx, d=lx / nx)
    kz = 2.0 * np.pi * np.fft.fftfreq(nz, d=lz / nz)

    Kx, Kz = np.meshgrid(kx, kz, indexing="ij")
    phase_factor_2d = np.exp(-1j * (Kx * dx_shift + Kz * dz_shift))  # (nx, nz)
    phase_factor_3d = phase_factor_2d[:, np.newaxis, :]  # (nx, 1, nz)

    # 2D FFT along (0, 2)
    fft_xz = np.fft.fftn(field_3d, axes=(0, 2))
    shifted_fft = fft_xz * phase_factor_3d
    shifted_field = np.fft.ifftn(shifted_fft, axes=(0, 2)).real

    return shifted_field


def shift_velocity_field_xz(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    dx_shift: float,
    dz_shift: float,
) -> VelocityField:
    """Shift a MAC VelocityField in the periodic homogeneous directions (x, z).

    Strictly enforces Delta_y = 0.
    Preserves exact discrete solenoidality and boundary conditions.
    """
    shifted = VelocityField.zeros(mesh)

    # Interior shapes:
    # u.interior: (nx + 1, ny, nz) - periodic in x: interior[:-1, :, :] has shape (nx, ny, nz)
    # v.interior: (nx, ny + 1, nz) - periodic in x, z: interior[:, :, :] has shape (nx, ny+1, nz)
    # w.interior: (nx, ny, nz + 1) - periodic in z: interior[:, :, :-1] has shape (nx, ny, nz)

    u_data = velocity.u.interior[:-1, :, :]
    v_data = velocity.v.interior[:, :, :]
    w_data = velocity.w.interior[:, :, :-1]

    u_shifted = fourier_shift_2d_xz(u_data, dx_shift, dz_shift, mesh.lx, mesh.lz)
    v_shifted = fourier_shift_2d_xz(v_data, dx_shift, dz_shift, mesh.lx, mesh.lz)
    w_shifted = fourier_shift_2d_xz(w_data, dx_shift, dz_shift, mesh.lx, mesh.lz)

    shifted.u.interior[:-1, :, :] = u_shifted
    shifted.u.interior[-1, :, :] = u_shifted[0, :, :]

    shifted.v.interior[:, :, :] = v_shifted

    shifted.w.interior[:, :, :-1] = w_shifted
    shifted.w.interior[:, :, -1] = w_shifted[:, :, 0]

    return shifted


# ============================================================================
# 2. Optimal Alignment Solver: FFT Correlation + Subgrid Refinement
# ============================================================================

def compute_cross_correlation_map_xz(
    vel_A: VelocityField,
    vel_B: VelocityField,
    mesh: StructuredMesh3D,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute 2D cross-correlation map C(dx, dz) = <u_A, T(dx, dz) u_B>_MAC across all grid shifts."""
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    dV = mesh.cell_volume

    uA = vel_A.u.interior[:-1, :, :]
    vA = vel_A.v.interior[:, :-1, :]
    wA = vel_A.w.interior[:, :, :-1]

    uB = vel_B.u.interior[:-1, :, :]
    vB = vel_B.v.interior[:, :-1, :]
    wB = vel_B.w.interior[:, :, :-1]

    # FFT2 across (0, 2)
    uA_hat = np.fft.fftn(uA, axes=(0, 2))
    vA_hat = np.fft.fftn(vA, axes=(0, 2))
    wA_hat = np.fft.fftn(wA, axes=(0, 2))

    uB_hat = np.fft.fftn(uB, axes=(0, 2))
    vB_hat = np.fft.fftn(vB, axes=(0, 2))
    wB_hat = np.fft.fftn(wB, axes=(0, 2))

    # Cross spectrum for <uA, T(dx, dz) uB> = sum uA_hat * conj(uB_hat)
    cross_spec = np.sum(
        uA_hat * np.conj(uB_hat) + vA_hat * np.conj(vB_hat) + wA_hat * np.conj(wB_hat),
        axis=1,
    )  # shape (nx, nz)

    # IFFT gives correlation for positive shifts
    corr_map = np.fft.ifftn(cross_spec, axes=(0, 1)).real * dV

    x_shifts_grid = np.arange(nx) * mesh.dx
    z_shifts_grid = np.arange(nz) * mesh.dz

    return corr_map, x_shifts_grid, z_shifts_grid


def find_optimal_periodic_alignment(
    vel_A: VelocityField,
    vel_B: VelocityField,
    mesh: StructuredMesh3D,
    subgrid: bool = True,
) -> Dict[str, Any]:
    """Find optimal periodic shift (dx*, dz*) applied to vel_B that minimizes MAC distance ||u_A - T(dx, dz) u_B||_MAC."""
    norm_A = mac_velocity_norm(vel_A, mesh)
    norm_B = mac_velocity_norm(vel_B, mesh)
    raw_diff = mac_velocity_diff_norm(vel_A, vel_B, mesh)

    # 1. Integer grid search via FFT cross-correlation
    corr_map, x_shifts, z_shifts = compute_cross_correlation_map_xz(vel_A, vel_B, mesh)
    max_idx = np.unravel_index(np.argmax(corr_map), corr_map.shape)
    dx_int = float(x_shifts[max_idx[0]])
    dz_int = float(z_shifts[max_idx[1]])

    vel_B_int = shift_velocity_field_xz(vel_B, mesh, dx_int, dz_int)
    err_int = mac_velocity_diff_norm(vel_A, vel_B_int, mesh)

    dx_opt = dx_int
    dz_opt = dz_int
    err_opt = err_int

    # 2. Continuous subgrid optimization
    if subgrid:
        def obj(params: np.ndarray) -> float:
            dx, dz = params
            shifted = shift_velocity_field_xz(vel_B, mesh, dx, dz)
            return float(mac_velocity_diff_norm(vel_A, shifted, mesh))

        res = minimize(
            obj,
            x0=np.array([dx_int, dz_int]),
            method="Nelder-Mead",
            options={"xatol": 1e-4 * mesh.dx, "fatol": 1e-6, "maxiter": 100},
        )
        if res.fun < err_opt:
            dx_opt = float(res.x[0] % mesh.lx)
            dz_opt = float(res.x[1] % mesh.lz)
            err_opt = float(res.fun)

    r_field = float(err_opt / (raw_diff + 1e-15))

    return {
        "dx_optimal": dx_opt,
        "dz_optimal": dz_opt,
        "dx_integer": dx_int,
        "dz_integer": dz_int,
        "d_field_raw": float(raw_diff),
        "d_field_aligned": float(err_opt),
        "d_field_aligned_integer": float(err_int),
        "R_field": r_field,
        "norm_A": float(norm_A),
        "norm_B": float(norm_B),
    }


# ============================================================================
# 3. Exact Subspace Metrics (Grassmannian Chordal, Geodesic, Spectral)
# ============================================================================

def compute_subspace_metrics(
    basis_A: PODSolenoidalBasis,
    basis_B: PODSolenoidalBasis,
    rank: int,
) -> Dict[str, Any]:
    """Compute rigorous Grassmannian subspace distances between two modal bases at matched rank.

    Definitions:
    - Cross-Gramian S_ij = < phi_i^A, phi_j^B >_MAC
    - Singular values of S: sigma_1 >= ... >= sigma_r in [0, 1] (cos theta_i)
    - Principal angles: theta_i = arccos(sigma_i)
    - Chordal distance: d_chordal = sqrt(sum_i sin^2 theta_i) = sqrt(r - sum_i sigma_i^2)
    - Geodesic distance: d_geodesic = sqrt(sum_i theta_i^2)
    - Spectral distance: d_spectral = max_i theta_i = theta_max
    """
    r_A = basis_A.num_modes
    r_B = basis_B.num_modes
    r = min(rank, r_A, r_B)

    dV = basis_A.mesh.cell_volume
    S = np.zeros((r, r), dtype=np.float64)

    for i in range(r):
        ui, vi, wi = basis_A.get_mode_mac(i)
        for j in range(r):
            uj, vj, wj = basis_B.get_mode_mac(j)
            S[i, j] = np.sum(ui * uj + vi * vj + wi * wj) * dV

    U, sigmas, Vt = np.linalg.svd(S)
    sigmas = np.clip(sigmas[:r], 0.0, 1.0)

    theta_rad = np.arccos(sigmas)
    theta_deg = np.degrees(theta_rad)

    sin_sq = np.maximum(0.0, 1.0 - sigmas**2)
    d_chordal = float(np.sqrt(np.sum(sin_sq)))
    d_geodesic = float(np.sqrt(np.sum(theta_rad**2)))
    d_spectral_rad = float(np.max(theta_rad)) if len(theta_rad) > 0 else 0.0
    d_spectral_deg = float(np.max(theta_deg)) if len(theta_deg) > 0 else 0.0

    return {
        "rank": int(r),
        "singular_values_cos_theta": sigmas.tolist(),
        "principal_angles_rad": theta_rad.tolist(),
        "principal_angles_deg": theta_deg.tolist(),
        "d_chordal": d_chordal,
        "d_geodesic": d_geodesic,
        "d_spectral_deg": d_spectral_deg,
        "d_spectral_rad": d_spectral_rad,
        "mean_principal_angle_deg": float(np.mean(theta_deg)),
    }


# ============================================================================
# 4. Fourier Phase vs. Amplitude Decomposition
# ============================================================================

def fourier_phase_amplitude_analysis(
    vel_A: VelocityField,
    vel_B: VelocityField,
    mesh: StructuredMesh3D,
) -> Dict[str, float]:
    """Decompose cross-field mismatch into pure Fourier phase error and pure amplitude error."""
    uA, vA, wA = mac_to_cell_centers(vel_A)
    uB, vB, wB = mac_to_cell_centers(vel_B)

    uA_hat = np.fft.fftn(uA)
    vA_hat = np.fft.fftn(vA)
    wA_hat = np.fft.fftn(wA)

    uB_hat = np.fft.fftn(uB)
    vB_hat = np.fft.fftn(vB)
    wB_hat = np.fft.fftn(wB)

    # Amplitudes
    ampA = np.sqrt(np.abs(uA_hat)**2 + np.abs(vA_hat)**2 + np.abs(wA_hat)**2)
    ampB = np.sqrt(np.abs(uB_hat)**2 + np.abs(vB_hat)**2 + np.abs(wB_hat)**2)

    # Relative amplitude discrepancy
    amp_denom = 0.5 * (ampA + ampB) + 1e-12
    rel_amp_err = float(np.mean(np.abs(ampA - ampB) / amp_denom))

    # Phase angles for energetic modes (where amplitude > 1% of max)
    mask = (ampA > 0.01 * np.max(ampA)) | (ampB > 0.01 * np.max(ampB))

    # Circular phase difference across u, v, w components
    phase_diffs = []
    for fA, fB in [(uA_hat, uB_hat), (vA_hat, vB_hat), (wA_hat, wB_hat)]:
        diff = np.angle(fA * np.conj(fB))  # circular difference in [-pi, pi]
        phase_diffs.append(np.abs(diff[mask]))

    mean_phase_err_rad = float(np.mean(np.concatenate(phase_diffs)))
    mean_phase_err_deg = float(np.degrees(mean_phase_err_rad))

    return {
        "mean_phase_error_deg": mean_phase_err_deg,
        "mean_phase_error_rad": mean_phase_err_rad,
        "relative_amplitude_error": rel_amp_err,
    }
