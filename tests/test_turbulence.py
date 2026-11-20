"""Unit tests for Smagorinsky LES turbulence model and filter scaling."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.fields import VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.turbulence import SmagorinskyModel


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def wall_bcs() -> BoundaryConditionSet:
    w = FaceBoundaryCondition(velocity_type=VelocityBCType.NO_SLIP, pressure_type=PressureBCType.NEUMANN)
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=w, y_max=w, z_min=p, z_max=p)


def test_zero_cs_returns_zero_eddy_viscosity() -> None:
    """Cs = 0 must yield nu_t = 0 everywhere to exact machine precision."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)
    b = periodic_bcs()
    model = SmagorinskyModel(cs=0.0)

    vel = VelocityField.zeros(m)
    vel.u.interior[:] = 1.5

    nu_t = model.eddy_viscosity(vel, m, b)
    assert float(np.max(np.abs(nu_t.data))) == 0.0


def test_negative_cs_raises_value_error() -> None:
    """Negative Cs must raise ValueError."""
    with pytest.raises(ValueError, match="non-negative"):
        SmagorinskyModel(cs=-0.1)


def test_eddy_viscosity_positivity_and_scaling() -> None:
    """Verify nu_t >= 0 and geometric-mean filter width scaling Delta^2."""
    m1 = StructuredMesh3D(nx=8, ny=8, nz=8, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)
    m2 = StructuredMesh3D(nx=16, ny=16, nz=16, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)
    b = periodic_bcs()

    cs = 0.17
    model = SmagorinskyModel(cs=cs)

    # Simple shear u = g*y
    g = 2.0
    _, Yu1, _ = np.meshgrid(m1.face_coords_x(), m1.cell_centers_y(), m1.cell_centers_z(), indexing="ij")
    vel1 = VelocityField.zeros(m1)
    vel1.u.interior[:] = g * Yu1

    _, Yu2, _ = np.meshgrid(m2.face_coords_x(), m2.cell_centers_y(), m2.cell_centers_z(), indexing="ij")
    vel2 = VelocityField.zeros(m2)
    vel2.u.interior[:] = g * Yu2

    nu_t1 = model.eddy_viscosity(vel1, m1, b)
    nu_t2 = model.eddy_viscosity(vel2, m2, b)

    assert float(np.min(nu_t1.interior)) >= 0.0
    assert float(np.min(nu_t2.interior)) >= 0.0

    # Since Delta2 = Delta1 / 2, nu_t2 / nu_t1 = (1/2)^2 = 0.25
    val1 = float(np.mean(nu_t1.interior[:, 1:-1, :]))
    val2 = float(np.mean(nu_t2.interior[:, 2:-2, :]))
    ratio = val2 / val1
    assert abs(ratio - 0.25) < 1e-10


def test_filter_width_anisotropy() -> None:
    """Filter width Delta = (dx * dy * dz)^(1/3) on anisotropic grid."""
    m = StructuredMesh3D(nx=10, ny=20, nz=40, lx=1.0, ly=2.0, lz=4.0, n_ghost=1)
    model = SmagorinskyModel(cs=0.1)

    delta = model.filter_width(m)
    expected_delta = (0.1 * 0.1 * 0.1) ** (1.0 / 3.0)
    assert abs(delta - expected_delta) < 1e-12


def test_wall_damping_reduces_nu_t_near_wall() -> None:
    """Wall damping must reduce nu_t near no-slip physical walls."""
    m = StructuredMesh3D(nx=8, ny=16, nz=8, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)
    b = wall_bcs()

    model_undamped = SmagorinskyModel(cs=0.17, wall_damping=False)
    model_damped = SmagorinskyModel(cs=0.17, wall_damping=True)

    _, Yu, _ = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    vel = VelocityField.zeros(m)
    vel.u.interior[:] = np.sin(np.pi * Yu)

    nu_t_un = model_undamped.eddy_viscosity(vel, m, b)
    nu_t_damped = model_damped.eddy_viscosity(vel, m, b)

    # Near wall (y=0, index j=0) nu_t_damped < nu_t_un
    wall_layer_un = float(np.mean(nu_t_un.interior[:, 0, :]))
    wall_layer_damped = float(np.mean(nu_t_damped.interior[:, 0, :]))
    assert wall_layer_damped < wall_layer_un
