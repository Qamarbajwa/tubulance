"""Unit tests for periodic 3D kinetic energy spectrum E(k) and Parseval consistency."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.fields import VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.spectrum import compute_energy_spectrum, verify_parseval_identity


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_parseval_identity_random_field() -> None:
    """Verify sum_k E(k) == K_physical to high precision (< 1e-12 relative error)."""
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()

    np.random.seed(123)
    vel = VelocityField.zeros(m)
    vel.u.interior[:] = np.random.normal(0.0, 1.0, (17, 16, 16))
    vel.v.interior[:] = np.random.normal(0.0, 1.0, (16, 17, 16))
    vel.w.interior[:] = np.random.normal(0.0, 1.0, (16, 16, 17))
    apply_velocity_bc(vel, b)

    K_phys, K_spec, rel_err = verify_parseval_identity(vel, m, remove_mean=True)
    assert rel_err < 1e-12, f"Parseval relative error {rel_err:.4e}"


def test_single_fourier_mode_spectrum_binning() -> None:
    """For a single Fourier mode u = A * sin(k_target * x), energy must appear in shell k_target."""
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()

    k_target = 3.0
    A = 2.0
    Xu, _, _ = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")

    vel = VelocityField.zeros(m)
    vel.u.interior[:] = A * np.sin(k_target * Xu)
    apply_velocity_bc(vel, b)

    k_shells, E_k = compute_energy_spectrum(vel, m, remove_mean=True)

    # Shell index corresponding to k_target = 3.0
    idx_target = int(np.round(k_target))
    peak_idx = int(np.argmax(E_k))

    assert peak_idx == idx_target, f"Peak shell {peak_idx} != expected {idx_target}"
    assert E_k[peak_idx] > 0.9 * np.sum(E_k)  # Nearly all energy in peak mode
