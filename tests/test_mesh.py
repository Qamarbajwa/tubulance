"""Tests for navier3d.mesh.StructuredMesh3D.

Uses a nonsymmetric grid (nx != ny != nz, lx != ly != lz) throughout so
that an accidental axis swap (e.g. dy computed from lx) would be caught;
a cubic grid would hide such bugs.
"""
import numpy as np
import pytest

from navier3d.config import SimulationConfig
from navier3d.mesh import StructuredMesh3D

NX, NY, NZ = 3, 4, 5
LX, LY, LZ = 2.0, 3.0, 5.0


@pytest.fixture
def mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=LX, ly=LY, lz=LZ, n_ghost=1)


def test_spacing_is_axis_correct(mesh: StructuredMesh3D) -> None:
    assert mesh.dx == pytest.approx(LX / NX)
    assert mesh.dy == pytest.approx(LY / NY)
    assert mesh.dz == pytest.approx(LZ / NZ)
    assert mesh.spacing == pytest.approx((LX / NX, LY / NY, LZ / NZ))


def test_cell_volume_and_face_areas(mesh: StructuredMesh3D) -> None:
    assert mesh.cell_volume == pytest.approx(mesh.dx * mesh.dy * mesh.dz)
    assert mesh.face_area_x == pytest.approx(mesh.dy * mesh.dz)
    assert mesh.face_area_y == pytest.approx(mesh.dx * mesh.dz)
    assert mesh.face_area_z == pytest.approx(mesh.dx * mesh.dy)


def test_cell_centers_shape_and_endpoints(mesh: StructuredMesh3D) -> None:
    cx, cy, cz = mesh.cell_centers_x(), mesh.cell_centers_y(), mesh.cell_centers_z()
    assert cx.shape == (NX,)
    assert cy.shape == (NY,)
    assert cz.shape == (NZ,)
    assert cx[0] == pytest.approx(0.5 * mesh.dx)
    assert cx[-1] == pytest.approx(LX - 0.5 * mesh.dx)
    assert cy[-1] == pytest.approx(LY - 0.5 * mesh.dy)
    assert cz[-1] == pytest.approx(LZ - 0.5 * mesh.dz)


def test_face_coords_shape_and_endpoints(mesh: StructuredMesh3D) -> None:
    fx, fy, fz = mesh.face_coords_x(), mesh.face_coords_y(), mesh.face_coords_z()
    assert fx.shape == (NX + 1,)
    assert fy.shape == (NY + 1,)
    assert fz.shape == (NZ + 1,)
    assert fx[0] == pytest.approx(0.0)
    assert fx[-1] == pytest.approx(LX)
    assert fy[-1] == pytest.approx(LY)
    assert fz[-1] == pytest.approx(LZ)


def test_meshgrid_centers_shapes_match_axes(mesh: StructuredMesh3D) -> None:
    X, Y, Z = mesh.meshgrid_centers()
    assert X.shape == (NX, NY, NZ)
    assert Y.shape == (NX, NY, NZ)
    assert Z.shape == (NX, NY, NZ)
    np.testing.assert_allclose(X[:, 0, 0], mesh.cell_centers_x())
    np.testing.assert_allclose(Y[0, :, 0], mesh.cell_centers_y())
    np.testing.assert_allclose(Z[0, 0, :], mesh.cell_centers_z())


@pytest.mark.parametrize("kwargs", [
    dict(nx=0), dict(ny=0), dict(nz=0), dict(nx=-1),
])
def test_invalid_cell_counts_raise(kwargs: dict) -> None:
    base = dict(nx=NX, ny=NY, nz=NZ, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    base.update(kwargs)
    with pytest.raises(ValueError):
        StructuredMesh3D(**base)


@pytest.mark.parametrize("kwargs", [
    dict(lx=0.0), dict(ly=-1.0), dict(lz=0.0),
])
def test_invalid_domain_lengths_raise(kwargs: dict) -> None:
    base = dict(nx=NX, ny=NY, nz=NZ, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    base.update(kwargs)
    with pytest.raises(ValueError):
        StructuredMesh3D(**base)


def test_invalid_n_ghost_raises() -> None:
    with pytest.raises(ValueError):
        StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=LX, ly=LY, lz=LZ, n_ghost=0)


def _bc_face(velocity="periodic", pressure="periodic"):
    return dict(velocity=velocity, pressure=pressure)


def test_from_config_matches_config_values() -> None:
    raw = {
        "domain": {"length_x": LX, "length_y": LY, "length_z": LZ},
        "mesh": {"nx": NX, "ny": NY, "nz": NZ},
        "fluid": {"density": 1.0, "kinematic_viscosity": 0.01},
        "time": {"dt": 0.001, "end_time": 1.0},
        "boundary_conditions": {name: _bc_face() for name in
                                 ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max")},
    }
    config = SimulationConfig.from_dict(raw)
    mesh = StructuredMesh3D.from_config(config, n_ghost=2)
    assert (mesh.nx, mesh.ny, mesh.nz) == (NX, NY, NZ)
    assert (mesh.lx, mesh.ly, mesh.lz) == (LX, LY, LZ)
    assert mesh.n_ghost == 2
