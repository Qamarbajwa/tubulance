"""Periodic 3D kinetic energy spectrum E(k) and Parseval consistency.

Provides 3D Fast Fourier Transform (FFT) energy spectrum analysis:
1. Interpolates MAC velocity components (u, v, w) onto cell centers.
2. Computes 3D discrete Fourier transform for each component.
3. Evaluates mode energy e(k) = 0.5 * (|u_hat|^2 + |v_hat|^2 + |w_hat|^2).
4. Bins mode energies into spherical wavenumber shells k = sqrt(kx^2 + ky^2 + kz^2).
5. Verifies Parseval identity: sum_k E(k) == K_cell_center to high precision.
"""
from __future__ import annotations

import numpy as np

from .fields import VelocityField
from .mesh import StructuredMesh3D


def compute_energy_spectrum(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    remove_mean: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute 3D kinetic energy spectrum E(k) for a periodic domain.

    Returns (k_shells, E_k):
    - k_shells: 1D array of wavenumber magnitudes k.
    - E_k: 1D array of kinetic energy assigned to each shell k.
    """
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz

    # 1. Interpolate MAC velocities onto cell centers
    u_data = velocity.u.interior
    v_data = velocity.v.interior
    w_data = velocity.w.interior

    u_cc = 0.5 * (u_data[:-1, :, :] + u_data[1:, :, :])
    v_cc = 0.5 * (v_data[:, :-1, :] + v_data[:, 1:, :])
    w_cc = 0.5 * (w_data[:, :, :-1] + w_data[:, :, 1:])

    if remove_mean:
        u_cc = u_cc - np.mean(u_cc)
        v_cc = v_cc - np.mean(v_cc)
        w_cc = w_cc - np.mean(w_cc)

    # 2. 3D FFT (scaled by 1/N for Parseval equality)
    u_hat = np.fft.fftn(u_cc) / (nx * ny * nz)
    v_hat = np.fft.fftn(v_cc) / (nx * ny * nz)
    w_hat = np.fft.fftn(w_cc) / (nx * ny * nz)

    # Mode kinetic energy: 0.5 * (|u_hat|^2 + |v_hat|^2 + |w_hat|^2)
    e_mode = 0.5 * (np.abs(u_hat) ** 2 + np.abs(v_hat) ** 2 + np.abs(w_hat) ** 2)

    # 3. Compute wavenumber grid kx, ky, kz
    kx_1d = 2.0 * np.pi * np.fft.fftfreq(nx, d=mesh.dx)
    ky_1d = 2.0 * np.pi * np.fft.fftfreq(ny, d=mesh.dy)
    kz_1d = 2.0 * np.pi * np.fft.fftfreq(nz, d=mesh.dz)

    Kx, Ky, Kz = np.meshgrid(kx_1d, ky_1d, kz_1d, indexing="ij")
    K_mag = np.sqrt(Kx ** 2 + Ky ** 2 + Kz ** 2)

    # 4. Spherical shell binning
    dk = min(2.0 * np.pi / lx, 2.0 * np.pi / ly, 2.0 * np.pi / lz)
    k_max = np.max(K_mag)

    nbins = int(np.ceil(k_max / dk)) + 1
    k_shells = np.arange(nbins) * dk
    E_k = np.zeros(nbins)

    k_indices = np.clip(np.round(K_mag / dk).astype(int), 0, nbins - 1)
    np.add.at(E_k, k_indices, e_mode)

    return k_shells, E_k


def verify_parseval_identity(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    remove_mean: bool = True,
) -> tuple[float, float, float]:
    """Verify Parseval's identity: sum_k E(k) == K_physical.

    Returns (K_physical, K_spectral, rel_error).
    """
    u_data = velocity.u.interior
    v_data = velocity.v.interior
    w_data = velocity.w.interior

    u_cc = 0.5 * (u_data[:-1, :, :] + u_data[1:, :, :])
    v_cc = 0.5 * (v_data[:, :-1, :] + v_data[:, 1:, :])
    w_cc = 0.5 * (w_data[:, :, :-1] + w_data[:, :, 1:])

    if remove_mean:
        u_cc = u_cc - np.mean(u_cc)
        v_cc = v_cc - np.mean(v_cc)
        w_cc = w_cc - np.mean(w_cc)

    K_physical = float(0.5 * np.mean(u_cc ** 2 + v_cc ** 2 + w_cc ** 2))

    k_shells, E_k = compute_energy_spectrum(velocity, mesh, remove_mean=remove_mean)
    K_spectral = float(np.sum(E_k))

    rel_err = abs(K_physical - K_spectral) / (K_physical + 1e-15)
    return K_physical, K_spectral, rel_err
