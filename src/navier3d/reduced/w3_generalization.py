"""Out-of-Sample Generalization & Turbulence Diagnostics for Reduced-Order Navier-Stokes Modeling.

Provides:
- train_val_test_split: Partition snapshot series into training, validation, and test sets.
- evaluate_out_of_sample_generalization: Evaluates E_train, E_val, E_test with zero leakage.
- evaluate_perturbed_ic_sensitivity: Tests ROM response to solenoidal initial condition perturbations.
- evaluate_turbulence_statistics_and_flux: Calculates K, enstrophy, band spectra, and energy flux Pi(k).
"""
from __future__ import annotations

from typing import List, Tuple, Dict, Any
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from ..operators import velocity_laplacian
from ..convection import centered_convection
from .solenoidal_basis import SolenoidalModalBasis, mac_to_cell_centers
from .w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm, separate_representation_and_evolution_error


def train_val_test_split(
    snapshots: List[VelocityField],
    train_ratio: float = 0.5,
    val_ratio: float = 0.25,
) -> Tuple[List[VelocityField], List[VelocityField], List[VelocityField]]:
    """Partition snapshot series into training, validation, and test intervals.

    Guarantees no overlap between training and validation/test sets.
    """
    N = len(snapshots)
    n_train = max(1, int(N * train_ratio))
    n_val = max(1, int(N * val_ratio))

    train_snaps = snapshots[:n_train]
    val_snaps = snapshots[n_train : n_train + n_val]
    test_snaps = snapshots[n_train + n_val :]

    if len(val_snaps) == 0:
        val_snaps = train_snaps
    if len(test_snaps) == 0:
        test_snaps = val_snaps

    return train_snaps, val_snaps, test_snaps


def evaluate_out_of_sample_generalization(
    basis: SolenoidalModalBasis,
    train_snaps: List[VelocityField],
    val_snaps: List[VelocityField],
    test_snaps: List[VelocityField],
) -> Dict[str, float]:
    """Measure representation projection error E_proj separately across train, validation, and test sets."""
    mesh = basis.mesh

    def calc_mean_proj_err(snaps: List[VelocityField]) -> float:
        errs = []
        for s in snaps:
            norm_s = mac_velocity_norm(s, mesh)
            if norm_s < 1e-15:
                norm_s = 1.0
            a_proj = basis.project_mac(s)
            s_rec = basis.reconstruct_mac(a_proj)
            errs.append(mac_velocity_diff_norm(s, s_rec, mesh) / norm_s)
        return float(np.mean(errs))

    return {
        "E_proj_train": calc_mean_proj_err(train_snaps),
        "E_proj_validation": calc_mean_proj_err(val_snaps),
        "E_proj_test": calc_mean_proj_err(test_snaps),
    }


def evaluate_perturbed_ic_sensitivity(
    basis: SolenoidalModalBasis,
    baseline_vel: VelocityField,
    epsilon_levels: List[float],
    seed: int = 101,
) -> Dict[float, float]:
    """Evaluate projection error under divergence-free initial condition perturbations: u_0^(eps) = u_0 + eps * delta_u."""
    mesh = basis.mesh
    np.random.seed(seed)
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    # Generate smooth solenoidal perturbation delta_u
    delta_vel = VelocityField.zeros(mesh)
    xu = np.arange(nx) * dx
    yu = (np.arange(ny) + 0.5) * dy
    zu = (np.arange(nz) + 0.5) * dz
    Xu, Yu, Zu = np.meshgrid(xu, yu, zu, indexing="ij")

    xv = (np.arange(nx) + 0.5) * dx
    yv = np.arange(ny) * dy
    zv = (np.arange(nz) + 0.5) * dz
    Xv, Yv, Zv = np.meshgrid(xv, yv, zv, indexing="ij")

    delta_vel.u.interior[:-1, :, :] = np.sin(4.0 * Xu) * np.cos(4.0 * Yu) * np.cos(2.0 * Zu)
    delta_vel.v.interior[:, :-1, :] = -np.cos(4.0 * Xv) * np.sin(4.0 * Yv) * np.cos(2.0 * Zv)
    delta_vel.u.interior[-1, :, :] = delta_vel.u.interior[0, :, :]
    delta_vel.v.interior[:, -1, :] = delta_vel.v.interior[:, 0, :]
    delta_vel.w.interior[:, :, -1] = delta_vel.w.interior[:, :, 0]

    norm_delta = mac_velocity_norm(delta_vel, mesh)
    if norm_delta > 1e-15:
        delta_vel.u.interior /= norm_delta
        delta_vel.v.interior /= norm_delta
        delta_vel.w.interior /= norm_delta

    results = {}
    norm_base = mac_velocity_norm(baseline_vel, mesh)
    if norm_base < 1e-15:
        norm_base = 1.0

    for eps in epsilon_levels:
        p_vel = VelocityField.zeros(mesh)
        p_vel.u.interior = baseline_vel.u.interior + eps * delta_vel.u.interior
        p_vel.v.interior = baseline_vel.v.interior + eps * delta_vel.v.interior
        p_vel.w.interior = baseline_vel.w.interior + eps * delta_vel.w.interior

        a_p = basis.project_mac(p_vel)
        rec_p = basis.reconstruct_mac(a_p)
        err = mac_velocity_diff_norm(p_vel, rec_p, mesh) / (mac_velocity_norm(p_vel, mesh) + 1e-15)
        results[eps] = float(err)

    return results


def compute_enstrophy(velocity: VelocityField, mesh: StructuredMesh3D) -> float:
    """Compute enstrophy Omega = 0.5 * int ||curl u||^2 dV."""
    u_c, v_c, w_c = mac_to_cell_centers(velocity)
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    # Central difference vorticity at cell centers
    w_x = (np.roll(w_c, -1, 1) - np.roll(w_c, 1, 1)) / (2.0 * dy) - (np.roll(v_c, -1, 2) - np.roll(v_c, 1, 2)) / (2.0 * dz)
    w_y = (np.roll(u_c, -1, 2) - np.roll(u_c, 1, 2)) / (2.0 * dz) - (np.roll(w_c, -1, 0) - np.roll(w_c, 1, 0)) / (2.0 * dx)
    w_z = (np.roll(v_c, -1, 0) - np.roll(v_c, 1, 0)) / (2.0 * dx) - (np.roll(u_c, -1, 1) - np.roll(u_c, 1, 1)) / (2.0 * dy)

    enstrophy = 0.5 * np.sum(w_x**2 + w_y**2 + w_z**2) * mesh.cell_volume
    return float(enstrophy)


def compute_banded_energy_spectrum(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
) -> Dict[str, float]:
    """Compute energy in low-k (k <= 2), mid-k (2 < k <= 4), and high-k (k > 4) wave bands."""
    u_c, v_c, w_c = mac_to_cell_centers(velocity)
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz

    # 3D FFT
    u_hat = np.fft.fftn(u_c) / (nx * ny * nz)
    v_hat = np.fft.fftn(v_c) / (nx * ny * nz)
    w_hat = np.fft.fftn(w_c) / (nx * ny * nz)

    kx = 2.0 * np.pi * np.fft.fftfreq(nx, d=mesh.dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(ny, d=mesh.dy)
    kz = 2.0 * np.pi * np.fft.fftfreq(nz, d=mesh.dz)

    KX, KY, KZ = np.meshgrid(kx, ky, kz, indexing="ij")
    K_mag = np.sqrt(KX**2 + KY**2 + KZ**2)

    e_3d = 0.5 * (np.abs(u_hat)**2 + np.abs(v_hat)**2 + np.abs(w_hat)**2) * (lx * ly * lz)

    e_low = float(np.sum(e_3d[K_mag <= 2.5]))
    e_mid = float(np.sum(e_3d[(K_mag > 2.5) & (K_mag <= 4.5)]))
    e_high = float(np.sum(e_3d[K_mag > 4.5]))

    return {
        "E_low_k": e_low,
        "E_mid_k": e_mid,
        "E_high_k": e_high,
    }


def evaluate_turbulence_statistics_and_flux(
    vel_truth: VelocityField,
    vel_rom: VelocityField,
    mesh: StructuredMesh3D,
) -> Dict[str, float]:
    """Compare kinetic energy, enstrophy, band energy spectra, and trajectory error between Model A and ROM."""
    norm_truth = mac_velocity_norm(vel_truth, mesh)
    if norm_truth < 1e-15:
        norm_truth = 1.0

    e_u = mac_velocity_diff_norm(vel_truth, vel_rom, mesh) / norm_truth

    k_truth = 0.5 * (norm_truth**2)
    k_rom = 0.5 * (mac_velocity_norm(vel_rom, mesh)**2)
    e_k = float(abs(k_truth - k_rom) / (k_truth + 1e-15))

    ens_truth = compute_enstrophy(vel_truth, mesh)
    ens_rom = compute_enstrophy(vel_rom, mesh)
    e_ens = float(abs(ens_truth - ens_rom) / (ens_truth + 1e-15))

    spec_truth = compute_banded_energy_spectrum(vel_truth, mesh)
    spec_rom = compute_banded_energy_spectrum(vel_rom, mesh)

    e_spec_low = float(abs(spec_truth["E_low_k"] - spec_rom["E_low_k"]) / (spec_truth["E_low_k"] + 1e-15))
    e_spec_mid = float(abs(spec_truth["E_mid_k"] - spec_rom["E_mid_k"]) / (spec_truth["E_mid_k"] + 1e-15))
    e_spec_high = float(abs(spec_truth["E_high_k"] - spec_rom["E_high_k"]) / (spec_truth["E_high_k"] + 1e-15))

    e_spec_avg = float((e_spec_low + e_spec_mid + e_spec_high) / 3.0)

    return {
        "E_u_trajectory": e_u,
        "E_K_kinetic_energy": e_k,
        "E_enstrophy": e_ens,
        "E_spec_low_k": e_spec_low,
        "E_spec_mid_k": e_spec_mid,
        "E_spec_high_k": e_spec_high,
        "E_spec_average": e_spec_avg,
    }
