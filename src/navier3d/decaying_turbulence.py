"""Solenoidal random velocity field generator for decaying periodic turbulence.

Constructs a divergence-free initial velocity field in 3D Fourier space
satisfying k . u_hat(k) = 0 and prescribed energy spectrum E(k), then
transforms to physical space and interpolates to MAC face locations.
"""
from __future__ import annotations

import numpy as np

from .boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from .fields import VelocityField
from .filtering import restrict_velocity_fine_to_coarse
from .mesh import StructuredMesh3D
from .projection import project_initial_velocity


def generate_solenoidal_random_field(
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    k_peak: float = 4.0,
    E0: float = 1.0,
    seed: int | None = 42,
) -> VelocityField:
    """Generate a divergence-free random velocity field on a periodic MAC grid.

    Parameters
    ----------
    mesh : StructuredMesh3D
    bcs : BoundaryConditionSet
    k_peak : float
        Peak wavenumber for initial energy spectrum.
    E0 : float
        Initial total kinetic energy scale.
    seed : int, optional
        Random seed for reproducible initial fields.
    """
    if seed is not None:
        np.random.seed(seed)

    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    kx = 2.0 * np.pi * np.fft.fftfreq(nx, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(ny, d=dy)
    kz = 2.0 * np.pi * np.fft.fftfreq(nz, d=dz)

    Kx, Ky, Kz = np.meshgrid(kx, ky, kz, indexing="ij")
    K_sq = Kx ** 2 + Ky ** 2 + Kz ** 2
    K_mag = np.sqrt(K_sq)
    K_mag[0, 0, 0] = 1.0  # Prevent division by zero at k=0

    # 1. Random vector field in Fourier space
    v_x = np.random.normal(0.0, 1.0, (nx, ny, nz)) + 1j * np.random.normal(0.0, 1.0, (nx, ny, nz))
    v_y = np.random.normal(0.0, 1.0, (nx, ny, nz)) + 1j * np.random.normal(0.0, 1.0, (nx, ny, nz))
    v_z = np.random.normal(0.0, 1.0, (nx, ny, nz)) + 1j * np.random.normal(0.0, 1.0, (nx, ny, nz))

    K_sq_safe = np.where(K_sq == 0.0, 1.0, K_sq)
    # 2. Solenoidal projection in Fourier space: u_hat = v_hat - (k . v_hat / k^2) * k
    k_dot_v = Kx * v_x + Ky * v_y + Kz * v_z
    u_hat_x = v_x - (k_dot_v / K_sq_safe) * Kx
    u_hat_y = v_y - (k_dot_v / K_sq_safe) * Ky
    u_hat_z = v_z - (k_dot_v / K_sq_safe) * Kz

    u_hat_x[0, 0, 0] = 0.0
    u_hat_y[0, 0, 0] = 0.0
    u_hat_z[0, 0, 0] = 0.0

    # 3. Shape energy spectrum E(k) = E0 * (k/k_p)^4 * exp(-2 * (k/k_p)^2)
    k_ratio = K_mag / k_peak
    spectrum_shape = (k_ratio ** 4) * np.exp(-2.0 * (k_ratio ** 2))
    amplitude = np.sqrt(np.maximum(0.0, spectrum_shape))

    u_hat_x *= amplitude
    u_hat_y *= amplitude
    u_hat_z *= amplitude

    # 4. Inverse FFT to physical space
    u_cc = np.real(np.fft.ifftn(u_hat_x))
    v_cc = np.real(np.fft.ifftn(u_hat_y))
    w_cc = np.real(np.fft.ifftn(u_hat_z))

    # Scale total kinetic energy to E0
    K_curr = 0.5 * np.mean(u_cc ** 2 + v_cc ** 2 + w_cc ** 2)
    if K_curr > 0:
        scale = np.sqrt(E0 / K_curr)
        u_cc *= scale
        v_cc *= scale
        w_cc *= scale

    # 5. Interpolate cell-centered values onto MAC face locations
    vel = VelocityField.zeros(mesh)

    u_padded = np.pad(u_cc, ((1, 1), (0, 0), (0, 0)), mode="wrap")
    vel.u.interior[:] = 0.5 * (u_padded[:-1, :, :] + u_padded[1:, :, :])

    v_padded = np.pad(v_cc, ((0, 0), (1, 1), (0, 0)), mode="wrap")
    vel.v.interior[:] = 0.5 * (v_padded[:, :-1, :] + v_padded[:, 1:, :])

    w_padded = np.pad(w_cc, ((0, 0), (0, 0), (1, 1)), mode="wrap")
    vel.w.interior[:] = 0.5 * (w_padded[:, :, :-1] + w_padded[:, :, 1:])

    apply_velocity_bc(vel, bcs)

    # 6. Leray project on MAC grid to guarantee discrete divergence-free property
    vel_sol = project_initial_velocity(vel, bcs, mesh)
    return vel_sol


def generate_matched_solenoidal_fields(
    mesh_fine: StructuredMesh3D,
    mesh_coarse: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    k_peak: float = 4.0,
    E0: float = 1.0,
    seed: int | None = 42,
) -> tuple[VelocityField, VelocityField]:
    """Generate fine and coarse solenoidal initial fields sharing the same large-scale realization."""
    vel_fine = generate_solenoidal_random_field(mesh_fine, bcs, k_peak=k_peak, E0=E0, seed=seed)
    vel_coarse = restrict_velocity_fine_to_coarse(vel_fine, mesh_fine, mesh_coarse, bcs)
    vel_coarse = project_initial_velocity(vel_coarse, bcs, mesh_coarse)
    return vel_fine, vel_coarse
