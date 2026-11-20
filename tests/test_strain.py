"""Unit tests for MAC-grid strain tensor components S_ij and magnitude |S|."""
import math
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.fields import VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.strain import compute_strain_components, compute_strain_magnitude


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_strain_components_analytical_periodic_field() -> None:
    """Verify S_ij components against analytical derivatives for
    u = sin(2pi y), v = sin(2pi z), w = sin(2pi x)."""
    L = 1.0
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=L, ly=L, lz=L, n_ghost=1)
    b = periodic_bcs()

    Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(m.cell_centers_x(), m.face_coords_y(), m.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.face_coords_z(), indexing="ij")

    vel = VelocityField.zeros(m)
    vel.u.interior[:] = np.sin(2 * np.pi * Yu / L)
    vel.v.interior[:] = np.sin(2 * np.pi * Zv / L)
    vel.w.interior[:] = np.sin(2 * np.pi * Xw / L)
    apply_velocity_bc(vel, b)

    comp = compute_strain_components(vel, m, b)

    # Normal strains du/dx = 0, dv/dy = 0, dw/dz = 0
    assert float(np.max(np.abs(comp["s_xx"]))) < 1e-12
    assert float(np.max(np.abs(comp["s_yy"]))) < 1e-12
    assert float(np.max(np.abs(comp["s_zz"]))) < 1e-12

    # Shear strain S_xy = 0.5 * (2pi/L * cos(2pi y_edge))
    # Test interior accuracy against analytical derivative
    Xz_edge, Yz_edge, _ = np.meshgrid(m.face_coords_x(), m.face_coords_y(), m.cell_centers_z(), indexing="ij")
    s_xy_analytical = 0.5 * (2 * np.pi / L) * np.cos(2 * np.pi * Yz_edge / L)

    diff = float(np.max(np.abs(comp["s_xy"] - s_xy_analytical)))
    assert diff < 0.05  # O(dy^2) finite difference error


def test_strain_magnitude_interior_shear() -> None:
    """For simple shear u = g*y, v=0, w=0: in interior cells |S| = g."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)
    b = periodic_bcs()
    g = 2.5

    _, Yu, _ = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")

    vel = VelocityField.zeros(m)
    vel.u.interior[:] = g * Yu
    apply_velocity_bc(vel, b)

    s_mag = compute_strain_magnitude(vel, m, b)
    # Check interior cells (away from periodic boundary wrap jump)
    interior_slice = s_mag.interior[:, 1:-1, :]
    assert float(np.max(np.abs(interior_slice - g))) < 1e-10
