"""Subspace Distance, Representation Diagnosis, Phase Normalization, and Translation Alignment Diagnostics.

Provides:
- diagnose_representation_vs_evolution: Separates projection error E_proj from ROM dynamics error E_ROM.
- subspace_distance_metric: Calculates principal angles theta_i and subspace distance d_subspace = sqrt(sum sin^2 theta_i).
- optimal_translation_alignment: Finds spatial shift (di, dj, dk) to minimize projection error under translation symmetry.
- fourier_phase_amplitude_decomposition: Separates magnitude |u_hat(k)| from phase arg u_hat(k) across seeds.
"""
from __future__ import annotations

from typing import Tuple, Dict, Any, List
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from .solenoidal_basis import SolenoidalModalBasis, mac_to_cell_centers
from .w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm


def diagnose_representation_vs_evolution(
    basis: SolenoidalModalBasis,
    vel_truth: VelocityField,
    vel_rom: VelocityField,
) -> Dict[str, float]:
    """Separate representation error E_proj from evolution error E_ROM for an unseen flow state."""
    mesh = basis.mesh
    norm_truth = mac_velocity_norm(vel_truth, mesh)
    if norm_truth < 1e-15:
        norm_truth = 1.0

    a_proj = basis.project_mac(vel_truth)
    vel_proj = basis.reconstruct_mac(a_proj)

    e_proj = mac_velocity_diff_norm(vel_truth, vel_proj, mesh) / norm_truth
    e_rom = mac_velocity_diff_norm(vel_truth, vel_rom, mesh) / norm_truth

    return {
        "E_projection": float(e_proj),
        "E_ROM_evolution": float(e_rom),
        "representation_failure": bool(e_proj > 0.5),
        "evolution_failure": bool(e_rom > e_proj + 0.1),
    }


def subspace_distance_metric(
    basis_A: SolenoidalModalBasis,
    basis_B: SolenoidalModalBasis,
) -> Dict[str, Any]:
    """Compute principal angles theta_i and subspace distance d_subspace = sqrt(sum sin^2 theta_i) between two bases."""
    r_A = basis_A.num_modes
    r_B = basis_B.num_modes
    r = min(r_A, r_B)

    dV = basis_A.mesh.cell_volume

    # Compute MAC inner product matrix S_ij = < phi_i^A, phi_j^B >_MAC
    S = np.zeros((r_A, r_B), dtype=np.float64)
    for i in range(r_A):
        ui, vi, wi = basis_A.get_mode_mac(i)
        for j in range(r_B):
            uj, vj, wj = basis_B.get_mode_mac(j)
            S[i, j] = np.sum(ui * uj + vi * vj + wi * wj) * dV

    # Singular values of S are cos(theta_i)
    U, sigmas, Vt = np.linalg.svd(S)
    sigmas = np.clip(sigmas[:r], 0.0, 1.0)

    theta_rad = np.arccos(sigmas)
    sin_sq = 1.0 - sigmas**2
    d_subspace = float(np.sqrt(np.sum(sin_sq)))

    return {
        "singular_values_cos_theta": sigmas.tolist(),
        "principal_angles_deg": np.degrees(theta_rad).tolist(),
        "subspace_distance": d_subspace,
        "mean_principal_angle_deg": float(np.mean(np.degrees(theta_rad))),
    }


def optimal_translation_alignment(
    basis: SolenoidalModalBasis,
    velocity: VelocityField,
) -> Dict[str, Any]:
    """Find spatial shift (di, dj, dk) maximizing projection correlation and return before/after projection error."""
    mesh = basis.mesh
    norm_orig = mac_velocity_norm(velocity, mesh)
    if norm_orig < 1e-15:
        norm_orig = 1.0

    a_orig = basis.project_mac(velocity)
    rec_orig = basis.reconstruct_mac(a_orig)
    err_before = mac_velocity_diff_norm(velocity, rec_orig, mesh) / norm_orig

    best_err = err_before
    best_shift = (0, 0, 0)

    # Search small spatial grid shifts
    u_data = velocity.u.interior
    v_data = velocity.v.interior
    w_data = velocity.w.interior

    for di in [-2, -1, 0, 1, 2]:
        for dj in [-2, -1, 0, 1, 2]:
            for dk in [-2, -1, 0, 1, 2]:
                if di == 0 and dj == 0 and dk == 0:
                    continue
                shifted_vel = VelocityField.zeros(mesh)
                shifted_vel.u.interior[:-1, :, :] = np.roll(u_data[:-1, :, :], (di, dj, dk), axis=(0, 1, 2))
                shifted_vel.v.interior[:, :-1, :] = np.roll(v_data[:, :-1, :], (di, dj, dk), axis=(0, 1, 2))
                shifted_vel.w.interior[:, :, :-1] = np.roll(w_data[:, :, :-1], (di, dj, dk), axis=(0, 1, 2))

                a_shift = basis.project_mac(shifted_vel)
                rec_shift = basis.reconstruct_mac(a_shift)
                err_shift = mac_velocity_diff_norm(shifted_vel, rec_shift, mesh) / norm_orig

                if err_shift < best_err:
                    best_err = err_shift
                    best_shift = (di, dj, dk)

    return {
        "E_proj_before_alignment": float(err_before),
        "E_proj_after_alignment": float(best_err),
        "optimal_shift_grid_nodes": best_shift,
        "alignment_improvement_factor": float(err_before / (best_err + 1e-15)),
    }


def fourier_phase_amplitude_decomposition(
    vel_A: VelocityField,
    vel_B: VelocityField,
    mesh: StructuredMesh3D,
) -> Dict[str, float]:
    """Separate Fourier magnitude spectrum |u_hat(k)| from phase spectrum arg u_hat(k) between two fields."""
    uA, vA, wA = mac_to_cell_centers(vel_A)
    uB, vB, wB = mac_to_cell_centers(vel_B)

    uA_hat = np.fft.fftn(uA)
    vA_hat = np.fft.fftn(vA)
    wA_hat = np.fft.fftn(wA)

    uB_hat = np.fft.fftn(uB)
    vB_hat = np.fft.fftn(vB)
    wB_hat = np.fft.fftn(wB)

    ampA = np.sqrt(np.abs(uA_hat)**2 + np.abs(vA_hat)**2 + np.abs(wA_hat)**2)
    ampB = np.sqrt(np.abs(uB_hat)**2 + np.abs(vB_hat)**2 + np.abs(wB_hat)**2)

    # Correlation of amplitude spectra
    amp_corr = np.corrcoef(ampA.ravel(), ampB.ravel())[0, 1]

    # Correlation of physical fields
    fieldA = np.concatenate([uA.ravel(), vA.ravel(), wA.ravel()])
    fieldB = np.concatenate([uB.ravel(), vB.ravel(), wB.ravel()])
    field_corr = np.corrcoef(fieldA, fieldB)[0, 1]

    return {
        "amplitude_spectrum_correlation": float(amp_corr),
        "physical_field_correlation": float(field_corr),
        "phase_mismatch_factor": float(amp_corr - field_corr),
    }
