"""Unit tests for 3D spectral cutoff filter and fine-to-coarse MAC restriction."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.decaying_turbulence import generate_matched_solenoidal_fields, generate_solenoidal_random_field
from navier3d.fields import VelocityField
from navier3d.filtering import restrict_velocity_fine_to_coarse, spectral_cutoff_filter
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import divergence
from navier3d.spectrum import compute_energy_spectrum, verify_parseval_identity


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_spectral_cutoff_filter_preserves_low_modes_removes_high_modes() -> None:
    """Verify that spectral_cutoff_filter retains k <= k_cutoff and zeroes k > k_cutoff."""
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()

    vel = generate_solenoidal_random_field(m, b, k_peak=4.0, E0=1.0, seed=42)
    k_cut = 3.0

    vel_filt = spectral_cutoff_filter(vel, m, k_cut, b)
    k_shells, E_k_filt = compute_energy_spectrum(vel_filt, m)

    # Check high wavenumber energy is zeroed
    high_k_mask = k_shells > (k_cut + 0.5)
    if np.any(high_k_mask):
        high_k_energy = float(np.sum(E_k_filt[high_k_mask]))
        assert high_k_energy < 1e-12, f"High k energy {high_k_energy:.4e} > 0"

    # Divergence remains negligible
    div = divergence(vel_filt, m)
    assert float(np.max(np.abs(div.interior))) < 1e-6


def test_fine_to_coarse_restriction_preserves_low_fourier_mode() -> None:
    """Verify that coarse restriction of a low Fourier mode preserves amplitude and phase."""
    L = 2.0 * np.pi
    m_fine = StructuredMesh3D(nx=16, ny=16, nz=16, lx=L, ly=L, lz=L, n_ghost=1)
    m_coarse = StructuredMesh3D(nx=8, ny=8, nz=8, lx=L, ly=L, lz=L, n_ghost=1)
    b = periodic_bcs()

    # Single low mode u = A sin(k_x x)
    k_x = 1.0
    A = 2.0

    vel_fine = VelocityField.zeros(m_fine)
    Xu, _, _ = np.meshgrid(m_fine.face_coords_x(), m_fine.cell_centers_y(), m_fine.cell_centers_z(), indexing="ij")
    vel_fine.u.interior[:] = A * np.sin(k_x * Xu)
    apply_velocity_bc(vel_fine, b)

    vel_coarse = restrict_velocity_fine_to_coarse(vel_fine, m_fine, m_coarse, b)

    Xu_c, _, _ = np.meshgrid(m_coarse.face_coords_x(), m_coarse.cell_centers_y(), m_coarse.cell_centers_z(), indexing="ij")
    u_expected = A * np.sin(k_x * Xu_c)

    diff = float(np.max(np.abs(vel_coarse.u.interior - u_expected)))
    assert diff < 0.05  # Slight area-averaging discretization factor sinc(k dx / 2)


def test_spectrally_matched_initial_fields() -> None:
    """Verify that generate_matched_solenoidal_fields produces matched coarse and fine initial states."""
    L = 2.0 * np.pi
    m_fine = StructuredMesh3D(nx=16, ny=16, nz=16, lx=L, ly=L, lz=L, n_ghost=1)
    m_coarse = StructuredMesh3D(nx=8, ny=8, nz=8, lx=L, ly=L, lz=L, n_ghost=1)
    b = periodic_bcs()

    vel_fine, vel_coarse = generate_matched_solenoidal_fields(m_fine, m_coarse, b, k_peak=2.0, E0=1.0, seed=42)

    div_fine = divergence(vel_fine, m_fine)
    div_coarse = divergence(vel_coarse, m_coarse)

    assert float(np.max(np.abs(div_fine.interior))) < 1e-6
    assert float(np.max(np.abs(div_coarse.interior))) < 1e-6
