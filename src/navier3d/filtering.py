"""Spectral cutoff filtering, Germano tensor construction, and MAC-grid restriction.

Provides:
1. `spectral_cutoff_filter`: sharp 3D spherical Fourier cutoff filter.
2. `apply_test_filter`: sharp 3D Fourier test cutoff filter at k_test = k_c / test_filter_ratio.
3. `compute_germano_tensors`: constructs cell-centered Germano tensors L_ij^d, M_ij,
   and contraction terms (L^d:M) and (M:M).
4. `restrict_velocity_fine_to_coarse`: conservative area restriction of MAC face velocities.
"""
from __future__ import annotations

import numpy as np

from .boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from .fields import VelocityField
from .mesh import StructuredMesh3D
from .projection import project_initial_velocity


def spectral_cutoff_filter(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    k_cutoff: float,
    bcs: BoundaryConditionSet | None = None,
) -> VelocityField:
    """Apply sharp 3D Fourier spherical cutoff filter to a periodic velocity field.

    Filters all wavenumbers k = sqrt(kx^2 + ky^2 + kz^2) > k_cutoff to 0.
    """
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    # 1. Interpolate MAC face velocities to cell centers
    u_cc = 0.5 * (velocity.u.interior[:-1, :, :] + velocity.u.interior[1:, :, :])
    v_cc = 0.5 * (velocity.v.interior[:, :-1, :] + velocity.v.interior[:, 1:, :])
    w_cc = 0.5 * (velocity.w.interior[:, :, :-1] + velocity.w.interior[:, :, 1:])

    # 2. 3D FFT
    u_hat = np.fft.fftn(u_cc)
    v_hat = np.fft.fftn(v_cc)
    w_hat = np.fft.fftn(w_cc)

    # 3. Wavenumber grid
    kx = 2.0 * np.pi * np.fft.fftfreq(nx, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(ny, d=dy)
    kz = 2.0 * np.pi * np.fft.fftfreq(nz, d=dz)
    Kx, Ky, Kz = np.meshgrid(kx, ky, kz, indexing="ij")
    K_mag = np.sqrt(Kx ** 2 + Ky ** 2 + Kz ** 2)

    # Sharp cutoff mask
    mask = (K_mag <= k_cutoff).astype(float)

    u_hat_filt = u_hat * mask
    v_hat_filt = v_hat * mask
    w_hat_filt = w_hat * mask

    # 4. Inverse FFT
    u_filt_cc = np.real(np.fft.ifftn(u_hat_filt))
    v_filt_cc = np.real(np.fft.ifftn(v_hat_filt))
    w_filt_cc = np.real(np.fft.ifftn(w_hat_filt))

    # 5. Interpolate back to MAC face locations
    vel_filt = VelocityField.zeros(mesh)
    u_padded = np.pad(u_filt_cc, ((1, 1), (0, 0), (0, 0)), mode="wrap")
    v_padded = np.pad(v_filt_cc, ((0, 0), (1, 1), (0, 0)), mode="wrap")
    w_padded = np.pad(w_filt_cc, ((0, 0), (0, 0), (1, 1)), mode="wrap")

    vel_filt.u.interior[:] = 0.5 * (u_padded[:-1, :, :] + u_padded[1:, :, :])
    vel_filt.v.interior[:] = 0.5 * (v_padded[:, :-1, :] + v_padded[:, 1:, :])
    vel_filt.w.interior[:] = 0.5 * (w_padded[:, :, :-1] + w_padded[:, :, 1:])

    if bcs is not None:
        apply_velocity_bc(vel_filt, bcs)
        vel_filt = project_initial_velocity(vel_filt, bcs, mesh)

    return vel_filt


def apply_test_filter(
    field_3d: np.ndarray,
    mesh: StructuredMesh3D,
    test_filter_ratio: float = 2.0,
) -> np.ndarray:
    """Apply sharp 3D Fourier spherical cutoff test filter at wavenumber k_test = k_c / test_filter_ratio.

    Preserves constants (Filter(1) = 1).
    """
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    f_hat = np.fft.fftn(field_3d)

    kx = 2.0 * np.pi * np.fft.fftfreq(nx, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(ny, d=dy)
    kz = 2.0 * np.pi * np.fft.fftfreq(nz, d=dz)
    Kx, Ky, Kz = np.meshgrid(kx, ky, kz, indexing="ij")
    K_mag = np.sqrt(Kx ** 2 + Ky ** 2 + Kz ** 2)

    delta = (dx * dy * dz) ** (1.0 / 3.0)
    k_cutoff_grid = np.pi / delta
    k_cutoff_test = k_cutoff_grid / float(test_filter_ratio)

    mask = (K_mag <= k_cutoff_test).astype(float)

    f_hat_filt = f_hat * mask
    f_filt = np.real(np.fft.ifftn(f_hat_filt))
    return f_filt


def compute_germano_tensors(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet | None = None,
    test_filter_ratio: float = 2.0,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], np.ndarray, np.ndarray]:
    """Compute cell-centered Germano tensors L_ij^d, M_ij, and contraction terms (L^d:M) and (M:M)."""
    from .strain import compute_strain_components

    # 1. Cell-centered velocity components
    u_cc = 0.5 * (velocity.u.interior[:-1, :, :] + velocity.u.interior[1:, :, :])
    v_cc = 0.5 * (velocity.v.interior[:, :-1, :] + velocity.v.interior[:, 1:, :])
    w_cc = 0.5 * (velocity.w.interior[:, :, :-1] + velocity.w.interior[:, :, 1:])

    # Test-filtered velocity components
    u_hat = apply_test_filter(u_cc, mesh, test_filter_ratio)
    v_hat = apply_test_filter(v_cc, mesh, test_filter_ratio)
    w_hat = apply_test_filter(w_cc, mesh, test_filter_ratio)

    # Test-filtered products
    uu_hat = apply_test_filter(u_cc * u_cc, mesh, test_filter_ratio)
    vv_hat = apply_test_filter(v_cc * v_cc, mesh, test_filter_ratio)
    ww_hat = apply_test_filter(w_cc * w_cc, mesh, test_filter_ratio)

    uv_hat = apply_test_filter(u_cc * v_cc, mesh, test_filter_ratio)
    uw_hat = apply_test_filter(u_cc * w_cc, mesh, test_filter_ratio)
    vw_hat = apply_test_filter(v_cc * w_cc, mesh, test_filter_ratio)

    # Leonard / Germano tensor L_ij = <u_i u_j>_hat - u_i_hat * u_j_hat
    L_xx = uu_hat - u_hat * u_hat
    L_yy = vv_hat - v_hat * v_hat
    L_zz = ww_hat - w_hat * w_hat

    L_xy = uv_hat - u_hat * v_hat
    L_xz = uw_hat - u_hat * w_hat
    L_yz = vw_hat - v_hat * w_hat

    # Deviatoric Germano tensor L_ij^d = L_ij - (1/3) L_kk delta_ij
    L_kk = L_xx + L_yy + L_zz
    L_dev_xx = L_xx - (1.0 / 3.0) * L_kk
    L_dev_yy = L_yy - (1.0 / 3.0) * L_kk
    L_dev_zz = L_zz - (1.0 / 3.0) * L_kk
    L_dev_xy = L_xy
    L_dev_xz = L_xz
    L_dev_yz = L_yz

    # 2. Grid-scale strain tensor at cell centers
    strain_grid = compute_strain_components(velocity, mesh, bcs)
    S_xx = strain_grid["s_xx"]
    S_yy = strain_grid["s_yy"]
    S_zz = strain_grid["s_zz"]

    s_xy_edge = strain_grid["s_xy"]
    s_xz_edge = strain_grid["s_xz"]
    s_yz_edge = strain_grid["s_yz"]

    S_xy = 0.25 * (s_xy_edge[:-1, :-1, :] + s_xy_edge[1:, :-1, :] + s_xy_edge[:-1, 1:, :] + s_xy_edge[1:, 1:, :])
    S_xz = 0.25 * (s_xz_edge[:-1, :, :-1] + s_xz_edge[1:, :, :-1] + s_xz_edge[:-1, :, 1:] + s_xz_edge[1:, :, 1:])
    S_yz = 0.25 * (s_yz_edge[:, :-1, :-1] + s_yz_edge[:, 1:, :-1] + s_yz_edge[:, :-1, 1:] + s_yz_edge[:, 1:, 1:])

    S_mag = np.sqrt(2.0 * (S_xx**2 + S_yy**2 + S_zz**2 + 2.0 * S_xy**2 + 2.0 * S_xz**2 + 2.0 * S_yz**2))

    delta = (mesh.dx * mesh.dy * mesh.dz) ** (1.0 / 3.0)
    delta_sq = delta ** 2

    # Grid model tensor B_ij = Delta^2 |S| S_ij
    B_xx = delta_sq * S_mag * S_xx
    B_yy = delta_sq * S_mag * S_yy
    B_zz = delta_sq * S_mag * S_zz
    B_xy = delta_sq * S_mag * S_xy
    B_xz = delta_sq * S_mag * S_xz
    B_yz = delta_sq * S_mag * S_yz

    # Test-filtered grid model tensor Filter(B_ij)
    B_hat_xx = apply_test_filter(B_xx, mesh, test_filter_ratio)
    B_hat_yy = apply_test_filter(B_yy, mesh, test_filter_ratio)
    B_hat_zz = apply_test_filter(B_zz, mesh, test_filter_ratio)
    B_hat_xy = apply_test_filter(B_xy, mesh, test_filter_ratio)
    B_hat_xz = apply_test_filter(B_xz, mesh, test_filter_ratio)
    B_hat_yz = apply_test_filter(B_yz, mesh, test_filter_ratio)

    # 3. Test-filter strain tensor S_hat_ij from test-filtered velocity u_hat
    vel_test = VelocityField.zeros(mesh)
    u_pad = np.pad(u_hat, ((1, 1), (0, 0), (0, 0)), mode="wrap")
    v_pad = np.pad(v_hat, ((0, 0), (1, 1), (0, 0)), mode="wrap")
    w_pad = np.pad(w_hat, ((0, 0), (0, 0), (1, 1)), mode="wrap")
    vel_test.u.interior[:] = 0.5 * (u_pad[:-1, :, :] + u_pad[1:, :, :])
    vel_test.v.interior[:] = 0.5 * (v_pad[:, :-1, :] + v_pad[:, 1:, :])
    vel_test.w.interior[:] = 0.5 * (w_pad[:, :, :-1] + w_pad[:, :, 1:])

    strain_test = compute_strain_components(vel_test, mesh, bcs)
    S_hat_xx = strain_test["s_xx"]
    S_hat_yy = strain_test["s_yy"]
    S_hat_zz = strain_test["s_zz"]

    s_hat_xy_edge = strain_test["s_xy"]
    s_hat_xz_edge = strain_test["s_xz"]
    s_hat_yz_edge = strain_test["s_yz"]

    S_hat_xy = 0.25 * (s_hat_xy_edge[:-1, :-1, :] + s_hat_xy_edge[1:, :-1, :] + s_hat_xy_edge[:-1, 1:, :] + s_hat_xy_edge[1:, 1:, :])
    S_hat_xz = 0.25 * (s_hat_xz_edge[:-1, :, :-1] + s_hat_xz_edge[1:, :, :-1] + s_hat_xz_edge[:-1, :, 1:] + s_hat_xz_edge[1:, :, 1:])
    S_hat_yz = 0.25 * (s_hat_yz_edge[:, :-1, :-1] + s_hat_yz_edge[:, 1:, :-1] + s_hat_yz_edge[:, :-1, 1:] + s_hat_yz_edge[:, 1:, 1:])

    S_hat_mag = np.sqrt(2.0 * (S_hat_xx**2 + S_hat_yy**2 + S_hat_zz**2 + 2.0 * S_hat_xy**2 + 2.0 * S_hat_xz**2 + 2.0 * S_hat_yz**2))

    delta_test_sq = (float(test_filter_ratio) * delta) ** 2

    # Test-scale model tensor B_test_ij = Delta_hat^2 |S_hat| S_hat_ij
    B_test_xx = delta_test_sq * S_hat_mag * S_hat_xx
    B_test_yy = delta_test_sq * S_hat_mag * S_hat_yy
    B_test_zz = delta_test_sq * S_hat_mag * S_hat_zz
    B_test_xy = delta_test_sq * S_hat_mag * S_hat_xy
    B_test_xz = delta_test_sq * S_hat_mag * S_hat_xz
    B_test_yz = delta_test_sq * S_hat_mag * S_hat_yz

    # Germano model tensor M_ij = -2 (B_test_ij - Filter(B_ij))
    M_xx = -2.0 * (B_test_xx - B_hat_xx)
    M_yy = -2.0 * (B_test_yy - B_hat_yy)
    M_zz = -2.0 * (B_test_zz - B_hat_zz)
    M_xy = -2.0 * (B_test_xy - B_hat_xy)
    M_xz = -2.0 * (B_test_xz - B_hat_xz)
    M_yz = -2.0 * (B_test_yz - B_hat_yz)

    # Tensor inner products with shear factor of 2:
    L_M = (
        L_dev_xx * M_xx + L_dev_yy * M_yy + L_dev_zz * M_zz
        + 2.0 * L_dev_xy * M_xy + 2.0 * L_dev_xz * M_xz + 2.0 * L_dev_yz * M_yz
    )

    M_M = (
        M_xx**2 + M_yy**2 + M_zz**2
        + 2.0 * M_xy**2 + 2.0 * M_xz**2 + 2.0 * M_yz**2
    )

    L_dev_dict = {"xx": L_dev_xx, "yy": L_dev_yy, "zz": L_dev_zz, "xy": L_dev_xy, "xz": L_dev_xz, "yz": L_dev_yz}
    M_dict = {"xx": M_xx, "yy": M_yy, "zz": M_zz, "xy": M_xy, "xz": M_xz, "yz": M_yz}

    return L_dev_dict, M_dict, L_M, M_M


def restrict_velocity_fine_to_coarse(
    vel_fine: VelocityField,
    mesh_fine: StructuredMesh3D,
    mesh_coarse: StructuredMesh3D,
    bcs: BoundaryConditionSet | None = None,
) -> VelocityField:
    """Restrict fine MAC face velocities to coarse MAC face locations via area averaging.

    Assumes mesh_fine is an integer refinement of mesh_coarse (e.g. 32^3 to 16^3).
    """
    rx = mesh_fine.nx // mesh_coarse.nx
    ry = mesh_fine.ny // mesh_coarse.ny
    rz = mesh_fine.nz // mesh_coarse.nz

    if rx < 1 or ry < 1 or rz < 1:
        raise ValueError("mesh_fine must be finer than mesh_coarse")

    vel_coarse = VelocityField.zeros(mesh_coarse)

    # Component u at x-faces: shape (nx+1, ny, nz)
    u_fine = vel_fine.u.interior
    u_coarse = vel_coarse.u.interior
    for i in range(mesh_coarse.nx + 1):
        i_f = i * rx
        for j in range(mesh_coarse.ny):
            j_f = j * ry
            for k in range(mesh_coarse.nz):
                k_f = k * rz
                u_coarse[i, j, k] = np.mean(
                    u_fine[i_f, j_f : j_f + ry, k_f : k_f + rz]
                )

    # Component v at y-faces: shape (nx, ny+1, nz)
    v_fine = vel_fine.v.interior
    v_coarse = vel_coarse.v.interior
    for i in range(mesh_coarse.nx):
        i_f = i * rx
        for j in range(mesh_coarse.ny + 1):
            j_f = j * ry
            for k in range(mesh_coarse.nz):
                k_f = k * rz
                v_coarse[i, j, k] = np.mean(
                    v_fine[i_f : i_f + rx, j_f, k_f : k_f + rz]
                )

    # Component w at z-faces: shape (nx, ny, nz+1)
    w_fine = vel_fine.w.interior
    w_coarse = vel_coarse.w.interior
    for i in range(mesh_coarse.nx):
        i_f = i * rx
        for j in range(mesh_coarse.ny):
            j_f = j * ry
            for k in range(mesh_coarse.nz + 1):
                k_f = k * rz
                w_coarse[i, j, k] = np.mean(
                    w_fine[i_f : i_f + rx, j_f : j_f + ry, k_f]
                )

    if bcs is not None:
        apply_velocity_bc(vel_coarse, bcs)

    return vel_coarse
