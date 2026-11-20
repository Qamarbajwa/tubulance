"""Advanced diagnostics and mechanism analysis for Ramanujan-Inspired Spectral Correction.

Provides:
1. compute_shell_transfer_matrices: Shell-to-shell transfer matrices T_ij^NS and T_ij^R.
2. compute_triadic_transfer_samples: Sampled triadic interaction transfer T(k|p,q).
3. compute_helicity_and_enstrophy_rates: Helicity H, dH/dt|_R, enstrophy Omega, dOmega/dt|_R.
4. compute_force_norm_ratios: R_R/num and R_R/SGS force ratios against numerical and SGS forces.
5. compute_high_k_energy_ratio: R_upper high-wavenumber energy fraction (beta=0.8).
6. compute_spectral_correction_flux: Spectral flux Pi_R(K).
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Optional

import numpy as np
from scipy.fft import fftfreq, rfftfreq, rfftn, irfftn

from .boundary_conditions import BoundaryConditionSet
from .corrections import RamanujanCorrection, SpectralCorrection
from .fields import VelocityField
from .filtering import restrict_velocity_fine_to_coarse
from .mesh import StructuredMesh3D
from .sgs_apriori import compute_truncation_residuals


def _mac_to_cell_centers(velocity: VelocityField) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Interpolate MAC face velocity components to cell centers."""
    u_face = velocity.u.interior
    v_face = velocity.v.interior
    w_face = velocity.w.interior

    u_c = 0.5 * (u_face[:-1, :, :] + u_face[1:, :, :])
    v_c = 0.5 * (v_face[:, :-1, :] + v_face[:, 1:, :])
    w_c = 0.5 * (w_face[:, :, :-1] + w_face[:, :, 1:])
    return u_c, v_c, w_c


def compute_vorticity_field(
    velocity: VelocityField, mesh: StructuredMesh3D
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute cell-centered vorticity field w = curl(u)."""
    u_c, v_c, w_c = _mac_to_cell_centers(velocity)
    u_hat = rfftn(u_c)
    v_hat = rfftn(v_c)
    w_hat = rfftn(w_c)

    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    kx = 2.0 * np.pi * fftfreq(nx, d=lx / nx)
    ky = 2.0 * np.pi * fftfreq(ny, d=ly / ny)
    kz = 2.0 * np.pi * rfftfreq(nz, d=lz / nz)
    KX, KY, KZ = np.meshgrid(kx, ky, kz, indexing="ij")

    wx_hat = 1j * (KY * w_hat - KZ * v_hat)
    wy_hat = 1j * (KZ * u_hat - KX * w_hat)
    wz_hat = 1j * (KX * v_hat - KY * u_hat)

    wx = irfftn(wx_hat, s=(nx, ny, nz))
    wy = irfftn(wy_hat, s=(nx, ny, nz))
    wz = irfftn(wz_hat, s=(nx, ny, nz))
    return wx, wy, wz


def compute_helicity_and_enstrophy_rates(
    velocity: VelocityField,
    correction: SpectralCorrection,
    mesh: StructuredMesh3D,
    bcs: Optional[BoundaryConditionSet] = None,
) -> Dict[str, float]:
    """Compute helicity H, dH/dt|_R, enstrophy Omega, and dOmega/dt|_R."""
    u_c, v_c, w_c = _mac_to_cell_centers(velocity)
    wx, wy, wz = compute_vorticity_field(velocity, mesh)

    dV = mesh.cell_volume
    helicity = float(np.sum(u_c * wx + v_c * wy + w_c * wz) * dV)
    enstrophy = float(0.5 * np.sum(wx**2 + wy**2 + wz**2) * dV)

    R_h = correction.evaluate(velocity, mesh, bcs)
    Rx_c, Ry_c, Rz_c = _mac_to_cell_centers(R_h)
    w_Rx, w_Ry, w_Rz = compute_vorticity_field(R_h, mesh)

    # dH/dt|_R = 2 * int R_h . omega dV
    dH_dt_R = float(2.0 * np.sum(Rx_c * wx + Ry_c * wy + Rz_c * wz) * dV)

    # dOmega/dt|_R = int omega . curl(R_h) dV
    dOmega_dt_R = float(np.sum(wx * w_Rx + wy * w_Ry + wz * w_Rz) * dV)

    return {
        "helicity": helicity,
        "enstrophy": enstrophy,
        "dH_dt_R": dH_dt_R,
        "dOmega_dt_R": dOmega_dt_R,
    }


def compute_high_k_energy_ratio(
    velocity: VelocityField, mesh: StructuredMesh3D, beta: float = 0.8
) -> float:
    """Compute fraction of kinetic energy in high wavenumbers k > beta * k_max."""
    u_c, v_c, w_c = _mac_to_cell_centers(velocity)
    u_hat = rfftn(u_c)
    v_hat = rfftn(v_c)
    w_hat = rfftn(w_c)

    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    kx = 2.0 * np.pi * fftfreq(nx, d=lx / nx)
    ky = 2.0 * np.pi * fftfreq(ny, d=ly / ny)
    kz = 2.0 * np.pi * rfftfreq(nz, d=lz / nz)
    KX, KY, KZ = np.meshgrid(kx, ky, kz, indexing="ij")
    K_mag = np.sqrt(KX**2 + KY**2 + KZ**2)

    k_max = np.pi / min(mesh.dx, mesh.dy, mesh.dz)
    k_cutoff = beta * k_max

    E_k = 0.5 * (np.abs(u_hat)**2 + np.abs(v_hat)**2 + np.abs(w_hat)**2)
    # Correct weight for rfft non-zero kz
    E_k[:, :, 1:-1] *= 2.0

    total_E = np.sum(E_k)
    high_k_E = np.sum(E_k[K_mag > k_cutoff])

    return float(high_k_E / (total_E + 1e-15))


def compute_force_norm_ratios(
    vel_fine: VelocityField,
    mesh_fine: StructuredMesh3D,
    mesh_coarse: StructuredMesh3D,
    correction: SpectralCorrection,
    bcs: BoundaryConditionSet,
    eps: float = 1e-15,
) -> Dict[str, float]:
    """Compute |R_h|_2, |F_num|_2, |F_SGS|_2, and force ratios R_R/num and R_R/SGS."""
    vel_coarse = restrict_velocity_fine_to_coarse(vel_fine, mesh_fine, mesh_coarse, bcs)
    trunc_res = compute_truncation_residuals(vel_fine, mesh_fine, mesh_coarse, bcs)

    norm_f_num = trunc_res["norm_f_num"]
    norm_f_sgs = trunc_res["norm_f_sgs"]

    R_h = correction.evaluate(vel_coarse, mesh_coarse, bcs)
    r_sq = sum(np.sum(comp.interior ** 2) for comp in R_h.components())
    norm_R = float(np.sqrt(r_sq * mesh_coarse.cell_volume))

    ratio_R_num = float(norm_R / (norm_f_num + eps))
    ratio_R_sgs = float(norm_R / (norm_f_sgs + eps))

    return {
        "norm_R": norm_R,
        "norm_f_num": norm_f_num,
        "norm_f_sgs": norm_f_sgs,
        "ratio_R_num": ratio_R_num,
        "ratio_R_sgs": ratio_R_sgs,
    }


def compute_spectral_correction_flux(
    velocity: VelocityField,
    correction: SpectralCorrection,
    mesh: StructuredMesh3D,
    bcs: Optional[BoundaryConditionSet] = None,
    num_shells: int = 16,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute spectral energy transfer flux Pi_R(K) across wavenumber K."""
    u_c, v_c, w_c = _mac_to_cell_centers(velocity)
    u_hat = rfftn(u_c)
    v_hat = rfftn(v_c)
    w_hat = rfftn(w_c)

    R_h = correction.evaluate(velocity, mesh, bcs)
    Rx_c, Ry_c, Rz_c = _mac_to_cell_centers(R_h)
    Rx_hat = rfftn(Rx_c)
    Ry_hat = rfftn(Ry_c)
    Rz_hat = rfftn(Rz_c)

    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    kx = 2.0 * np.pi * fftfreq(nx, d=lx / nx)
    ky = 2.0 * np.pi * fftfreq(ny, d=ly / ny)
    kz = 2.0 * np.pi * rfftfreq(nz, d=lz / nz)
    KX, KY, KZ = np.meshgrid(kx, ky, kz, indexing="ij")
    K_mag = np.sqrt(KX**2 + KY**2 + KZ**2)

    k_max = np.pi / min(mesh.dx, mesh.dy, mesh.dz)
    k_shells = np.linspace(0, k_max, num_shells + 1)
    Pi_R = np.zeros(num_shells)

    # T(k) = Re( u_hat* . R_hat )
    T_k = np.real(np.conj(u_hat) * Rx_hat + np.conj(v_hat) * Ry_hat + np.conj(w_hat) * Rz_hat)
    T_k[:, :, 1:-1] *= 2.0

    # Pi_R(K) = - int_0^K T(k) dk
    for i in range(num_shells):
        K_target = k_shells[i + 1]
        Pi_R[i] = -float(np.sum(T_k[K_mag <= K_target]))

    return k_shells[1:], Pi_R


def compute_shell_transfer_matrices(
    velocity: VelocityField,
    correction: SpectralCorrection,
    mesh: StructuredMesh3D,
    num_shells: int = 4,
    bcs: Optional[BoundaryConditionSet] = None,
) -> Dict[str, np.ndarray]:
    """Compute shell-to-shell transfer matrix T_ij^R between wavenumber shells."""
    u_c, v_c, w_c = _mac_to_cell_centers(velocity)
    u_hat = rfftn(u_c)
    v_hat = rfftn(v_c)
    w_hat = rfftn(w_c)

    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    kx = 2.0 * np.pi * fftfreq(nx, d=lx / nx)
    ky = 2.0 * np.pi * fftfreq(ny, d=ly / ny)
    kz = 2.0 * np.pi * rfftfreq(nz, d=lz / nz)
    KX, KY, KZ = np.meshgrid(kx, ky, kz, indexing="ij")
    K_mag = np.sqrt(KX**2 + KY**2 + KZ**2)

    k_max = np.pi / min(mesh.dx, mesh.dy, mesh.dz)
    shell_edges = np.linspace(0, k_max, num_shells + 1)

    T_ij_R = np.zeros((num_shells, num_shells))
    dV = mesh.cell_volume

    for j in range(num_shells):
        # Filter velocity to shell j
        mask_j = (K_mag >= shell_edges[j]) & (K_mag < shell_edges[j + 1])
        u_j_hat = np.where(mask_j, u_hat, 0.0)
        v_j_hat = np.where(mask_j, v_hat, 0.0)
        w_j_hat = np.where(mask_j, w_hat, 0.0)

        uj_x = irfftn(u_j_hat, s=(nx, ny, nz))
        uj_y = irfftn(v_j_hat, s=(nx, ny, nz))
        uj_z = irfftn(w_j_hat, s=(nx, ny, nz))

        # Reconstruct shell j velocity field
        v_shell_j = VelocityField.zeros(mesh)
        u_pad = np.pad(uj_x, ((1, 1), (0, 0), (0, 0)), mode="wrap")
        v_pad = np.pad(uj_y, ((0, 0), (1, 1), (0, 0)), mode="wrap")
        w_pad = np.pad(uj_z, ((0, 0), (0, 0), (1, 1)), mode="wrap")
        v_shell_j.u.interior[:] = 0.5 * (u_pad[:-1, :, :] + u_pad[1:, :, :])
        v_shell_j.v.interior[:] = 0.5 * (v_pad[:, :-1, :] + v_pad[:, 1:, :])
        v_shell_j.w.interior[:] = 0.5 * (w_pad[:, :, :-1] + w_pad[:, :, 1:])

        # Correction generated by shell j
        R_j = correction.evaluate(v_shell_j, mesh, bcs)
        Rx_j, Ry_j, Rz_j = _mac_to_cell_centers(R_j)

        for i in range(num_shells):
            mask_i = (K_mag >= shell_edges[i]) & (K_mag < shell_edges[i + 1])
            u_i_hat = np.where(mask_i, u_hat, 0.0)
            v_i_hat = np.where(mask_i, v_hat, 0.0)
            w_i_hat = np.where(mask_i, w_hat, 0.0)

            ui_x = irfftn(u_i_hat, s=(nx, ny, nz))
            ui_y = irfftn(v_i_hat, s=(nx, ny, nz))
            ui_z = irfftn(w_i_hat, s=(nx, ny, nz))

            # Transfer to shell i
            T_ij_R[i, j] = float(np.sum(ui_x * Rx_j + ui_y * Ry_j + ui_z * Rz_j) * dV)

    return {"shell_edges": shell_edges, "T_ij_R": T_ij_R}
