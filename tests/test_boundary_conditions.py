"""Tests for navier3d.boundary_conditions.

Uses a nonsymmetric grid (nx != ny != nz) and, for several checks, an
asymmetric BC configuration (different type on the lo/hi face of an
axis) so that a coupling or axis-swap bug cannot hide behind symmetry.
Ghost/boundary values are checked against numbers derived by hand from
the formulas documented in boundary_conditions.py and docs/architecture.md,
not merely "did it run."
"""
import numpy as np
import pytest

from navier3d.boundary_conditions import (
    BoundaryConditionError,
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_boundary_conditions,
    apply_pressure_bc,
    apply_velocity_bc,
)
from navier3d.fields import FaceField, FlowState, ScalarField
from navier3d.mesh import StructuredMesh3D

NX, NY, NZ = 3, 4, 5


def mesh(n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=2.0, ly=3.0, lz=5.0, n_ghost=n_ghost)


def fbc(velocity, pressure, velocity_value=None, pressure_value=None, pressure_gradient_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
        pressure_gradient_value=pressure_gradient_value,
    )


def periodic_box_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def all_walls_bcs(**overrides) -> BoundaryConditionSet:
    """No-slip walls on every face by default; override individual faces."""
    w = fbc("no_slip", "neumann")
    kwargs = dict(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)
    kwargs.update(overrides)
    return BoundaryConditionSet(**kwargs)


# --------------------------------------------------------------------------
# FaceBoundaryCondition / BoundaryConditionSet construction and validation
# --------------------------------------------------------------------------

def test_incompatible_velocity_pressure_pair_raises() -> None:
    with pytest.raises(BoundaryConditionError):
        fbc("no_slip", "dirichlet", pressure_value=0.0)


def test_velocity_inlet_without_value_raises() -> None:
    with pytest.raises(BoundaryConditionError):
        fbc("velocity_inlet", "neumann")


def test_dirichlet_pressure_without_value_raises() -> None:
    with pytest.raises(BoundaryConditionError):
        fbc("pressure_outlet", "dirichlet")


def test_periodic_must_be_paired_raises() -> None:
    periodic = fbc("periodic", "periodic")
    wall = fbc("no_slip", "neumann")
    with pytest.raises(BoundaryConditionError):
        BoundaryConditionSet(x_min=periodic, x_max=wall, y_min=wall, y_max=wall, z_min=wall, z_max=wall)


def test_is_periodic_axis() -> None:
    bcs = periodic_box_bcs()
    assert bcs.is_periodic_axis(0) and bcs.is_periodic_axis(1) and bcs.is_periodic_axis(2)
    bcs2 = all_walls_bcs()
    assert not bcs2.is_periodic_axis(0)


def test_getitem_unknown_face_raises_key_error() -> None:
    bcs = periodic_box_bcs()
    with pytest.raises(KeyError):
        bcs["not_a_face"]


def test_boundary_condition_set_from_config_round_trips_lid_driven_cavity() -> None:
    from navier3d.config import SimulationConfig

    raw = {
        "domain": {"length_x": 1.0, "length_y": 1.0, "length_z": 1.0},
        "mesh": {"nx": 4, "ny": 4, "nz": 4},
        "fluid": {"density": 1.0, "kinematic_viscosity": 0.01},
        "time": {"dt": 0.001, "end_time": 1.0},
        "boundary_conditions": {
            "x_min": {"velocity": "no_slip", "pressure": "neumann"},
            "x_max": {"velocity": "no_slip", "pressure": "neumann"},
            "y_min": {"velocity": "no_slip", "pressure": "neumann"},
            "y_max": {"velocity": "velocity_inlet", "pressure": "neumann", "velocity_value": [1.0, 0.0, 0.0]},
            "z_min": {"velocity": "no_slip", "pressure": "neumann"},
            "z_max": {"velocity": "no_slip", "pressure": "neumann"},
        },
    }
    config = SimulationConfig.from_dict(raw)
    bcs = BoundaryConditionSet.from_config(config.boundary_conditions)
    assert bcs.y_max.velocity_type is VelocityBCType.VELOCITY_INLET
    assert bcs.y_max.velocity_value == (1.0, 0.0, 0.0)
    assert bcs.x_min.velocity_type is VelocityBCType.NO_SLIP


# --------------------------------------------------------------------------
# Pressure ghost fill
# --------------------------------------------------------------------------

def test_pressure_periodic_ghost_wrap() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    field.data[:, 2, 2] = np.arange(field.data.shape[0], dtype=np.float64)
    apply_pressure_bc(field, periodic_box_bcs())
    n = field.data.shape[0]
    ng = m.n_ghost
    np.testing.assert_allclose(field.data[0:ng, 2, 2], field.data[n - 2 * ng:n - ng, 2, 2])
    np.testing.assert_allclose(field.data[n - ng:n, 2, 2], field.data[ng:2 * ng, 2, 2])


def test_pressure_neumann_ghost_equals_interior() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    field.interior = 5.0
    field.data[0, :, :] = -999.0  # will be overwritten
    apply_pressure_bc(field, all_walls_bcs())
    assert field.data[0, 2, 2] == pytest.approx(5.0)
    assert field.data[-1, 2, 2] == pytest.approx(5.0)


def test_pressure_inhomogeneous_neumann_ghost() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    field.interior = 0.0
    field.data[1, 2, 2] = 5.0  # interior cell adjacent to the x_min ghost
    grad_bc = fbc("no_slip", "neumann", pressure_gradient_value=2.0)
    bcs = all_walls_bcs(x_min=grad_bc)
    apply_pressure_bc(field, bcs, spacing=m.spacing)
    # ghost(k=0) = interior + (2*0+1)*dx*g = 5 + dx*2
    assert field.data[0, 2, 2] == pytest.approx(5.0 + m.dx * 2.0)


def test_pressure_inhomogeneous_neumann_ghost_hi_side() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    field.interior = 0.0
    field.data[-2, 2, 2] = 7.0  # interior cell adjacent to the x_max ghost
    grad_bc = fbc("no_slip", "neumann", pressure_gradient_value=3.0)
    bcs = all_walls_bcs(x_max=grad_bc)
    apply_pressure_bc(field, bcs, spacing=m.spacing)
    assert field.data[-1, 2, 2] == pytest.approx(7.0 + m.dx * 3.0)


def test_pressure_inhomogeneous_neumann_without_spacing_raises() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    grad_bc = fbc("no_slip", "neumann", pressure_gradient_value=2.0)
    bcs = all_walls_bcs(x_min=grad_bc)
    with pytest.raises(ValueError):
        apply_pressure_bc(field, bcs)  # no spacing provided


def test_pressure_inhomogeneous_neumann_hi_side_without_spacing_raises() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    grad_bc = fbc("no_slip", "neumann", pressure_gradient_value=3.0)
    bcs = all_walls_bcs(x_max=grad_bc)
    with pytest.raises(ValueError):
        apply_pressure_bc(field, bcs)  # no spacing provided


def test_pressure_gradient_value_on_non_neumann_raises() -> None:
    with pytest.raises(BoundaryConditionError):
        fbc("pressure_outlet", "dirichlet", pressure_value=0.0, pressure_gradient_value=1.0)


def test_pressure_dirichlet_ghost_reflection() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    field.interior = 0.0
    field.data[1, 2, 2] = 4.0  # interior cell adjacent to the x_min ghost
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=10.0)
    bcs = all_walls_bcs(x_min=outlet)
    apply_pressure_bc(field, bcs)
    # ghost = 2*value - interior = 2*10 - 4 = 16
    assert field.data[0, 2, 2] == pytest.approx(16.0)


def test_pressure_dirichlet_ghost_reflection_hi_side() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    field.interior = 0.0
    field.data[-2, 2, 2] = 6.0  # interior cell adjacent to the x_max ghost
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=1.0)
    bcs = all_walls_bcs(x_max=outlet)
    apply_pressure_bc(field, bcs)
    # ghost = 2*value - interior = 2*1 - 6 = -4
    assert field.data[-1, 2, 2] == pytest.approx(-4.0)


def test_pressure_constant_field_preserved_neumann() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    field.interior = 3.5
    apply_pressure_bc(field, all_walls_bcs())
    assert np.all(field.data == pytest.approx(3.5))


def test_pressure_constant_field_preserved_periodic() -> None:
    m = mesh(1)
    field = ScalarField.zeros(m)
    field.interior = -2.0
    apply_pressure_bc(field, periodic_box_bcs())
    assert np.all(field.data == pytest.approx(-2.0))


# --------------------------------------------------------------------------
# Velocity: face-normal axis, direct boundary assignment
# --------------------------------------------------------------------------

def test_normal_no_slip_boundary_is_zero() -> None:
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)
    field.interior = 7.0
    apply_velocity_bc(_velocity_field_with(m, u=field), all_walls_bcs())
    assert field.data[1, 2, 2] == pytest.approx(0.0)  # x_min boundary face
    assert field.data[-2, 2, 2] == pytest.approx(0.0)  # x_max boundary face


def test_normal_velocity_inlet_boundary_takes_prescribed_value() -> None:
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)
    field.interior = 0.0
    inlet = fbc("velocity_inlet", "neumann", velocity_value=(2.5, 0.0, 0.0))
    bcs = all_walls_bcs(x_min=inlet)
    apply_velocity_bc(_velocity_field_with(m, u=field), bcs)
    assert field.data[1, 2, 2] == pytest.approx(2.5)


def test_normal_pressure_outlet_boundary_is_zero_gradient() -> None:
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)
    field.data[:] = 0.0
    field.data[2, 2, 2] = 9.0  # interior adjacent to x_min boundary face (index 1)
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    bcs = all_walls_bcs(x_min=outlet)
    apply_velocity_bc(_velocity_field_with(m, u=field), bcs)
    assert field.data[1, 2, 2] == pytest.approx(9.0)


def test_normal_periodic_boundary_faces_are_averaged() -> None:
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)
    field.data[:] = 0.0
    field.data[1, 2, 2] = 10.0  # x_min boundary face (raw, pre-BC)
    field.data[4, 2, 2] = 40.0  # x_max boundary face (raw, pre-BC); nx=3 -> hi index = ng+nx = 4
    apply_velocity_bc(_velocity_field_with(m, u=field), periodic_box_bcs())
    assert field.data[1, 2, 2] == pytest.approx(25.0)
    assert field.data[4, 2, 2] == pytest.approx(25.0)


def test_normal_axis_ghost_dirichlet_reflection_and_boundaries_independent() -> None:
    """no_slip at x_min, velocity_inlet at x_max: verifies each side is
    handled independently and checks the node-reflection ghost formula
    ghost = 2*boundary_value - mirror_interior beyond both boundary faces."""
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)
    field.data[:] = 0.0
    field.data[2, 2, 2] = 5.0  # interior adjacent to x_min boundary (index 1)
    field.data[3, 2, 2] = 7.0  # interior adjacent to x_max boundary (index 4)
    inlet = fbc("velocity_inlet", "neumann", velocity_value=(2.0, 0.0, 0.0))
    bcs = all_walls_bcs(x_min=fbc("no_slip", "neumann"), x_max=inlet)
    apply_velocity_bc(_velocity_field_with(m, u=field), bcs)

    assert field.data[1, 2, 2] == pytest.approx(0.0)     # x_min boundary: no_slip -> 0
    assert field.data[4, 2, 2] == pytest.approx(2.0)     # x_max boundary: inlet -> 2.0
    assert field.data[0, 2, 2] == pytest.approx(-5.0)    # ghost = 2*0 - 5
    assert field.data[5, 2, 2] == pytest.approx(-3.0)    # ghost = 2*2 - 7


def test_normal_axis_periodic_wrap_skips_duplicated_boundary_point() -> None:
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)  # shape[0] = nx+1+2ng = 6
    field.data[:, 2, 2] = [0.0, 10.0, 20.0, 30.0, 40.0, 0.0]
    apply_velocity_bc(_velocity_field_with(m, u=field), periodic_box_bcs())
    expected = [30.0, 25.0, 20.0, 30.0, 25.0, 20.0]
    np.testing.assert_allclose(field.data[:, 2, 2], expected)


def test_normal_axis_periodic_wrap_two_ghost_layers() -> None:
    m = mesh(2)
    field = FaceField.zeros(m, normal_axis=0)  # shape[0] = nx+1+2ng = 8
    field.data[:, 3, 3] = [0.0, 0.0, 10.0, 20.0, 30.0, 40.0, 0.0, 0.0]
    apply_velocity_bc(_velocity_field_with(m, u=field), periodic_box_bcs())
    expected = [20.0, 30.0, 25.0, 20.0, 30.0, 25.0, 20.0, 30.0]
    np.testing.assert_allclose(field.data[:, 3, 3], expected)


def test_normal_axis_dirichlet_ghost_two_ghost_layers() -> None:
    m = mesh(2)
    field = FaceField.zeros(m, normal_axis=0)  # shape[0] = nx+1+2ng = 8
    field.data[:] = 0.0
    field.data[3, 3, 3] = 100.0
    field.data[4, 3, 3] = 200.0
    apply_velocity_bc(_velocity_field_with(m, u=field), all_walls_bcs())
    expected = [-200.0, -100.0, 0.0, 100.0, 200.0, 0.0, -200.0, -100.0]
    np.testing.assert_allclose(field.data[:, 3, 3], expected)


# --------------------------------------------------------------------------
# Velocity: tangential axis ghosts
# --------------------------------------------------------------------------

def test_tangential_stationary_no_slip_reflection() -> None:
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)
    field.data[:] = 0.0
    field.data[2, 1, 3] = 7.0  # interior adjacent to y_min ghost, x/z interior locations
    apply_velocity_bc(_velocity_field_with(m, u=field), all_walls_bcs())
    assert field.data[2, 0, 3] == pytest.approx(-7.0)


def test_tangential_moving_wall_reflection() -> None:
    """Lid-driven-cavity-style moving wall: y_max moves with u-component speed 3.0."""
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)
    field.data[:] = 0.0
    field.data[2, 4, 3] = 9.0  # interior adjacent to y_max ghost
    lid = fbc("velocity_inlet", "neumann", velocity_value=(3.0, 0.0, 0.0))
    bcs = all_walls_bcs(y_max=lid)
    apply_velocity_bc(_velocity_field_with(m, u=field), bcs)
    assert field.data[2, 5, 3] == pytest.approx(2.0 * 3.0 - 9.0)


def test_tangential_free_slip_reflection() -> None:
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)
    field.data[:] = 0.0
    field.data[2, 1, 3] = 6.0
    slip = fbc("free_slip", "neumann")
    bcs = all_walls_bcs(y_min=slip)
    apply_velocity_bc(_velocity_field_with(m, u=field), bcs)
    assert field.data[2, 0, 3] == pytest.approx(6.0)


def test_tangential_periodic_wrap() -> None:
    m = mesh(1)
    field = FaceField.zeros(m, normal_axis=0)  # tangential axis y has ny+2ng = 6 entries
    field.data[2, :, 3] = [0.0, 10.0, 20.0, 30.0, 40.0, 0.0]
    bcs = periodic_box_bcs()
    apply_velocity_bc(_velocity_field_with(m, u=field), bcs)
    assert field.data[2, 0, 3] == pytest.approx(40.0)
    assert field.data[2, 5, 3] == pytest.approx(10.0)


# --------------------------------------------------------------------------
# Constant-field preservation (regression / sanity)
# --------------------------------------------------------------------------

def test_full_state_constant_field_preserved_periodic_box() -> None:
    m = mesh(1)
    state = FlowState.zeros(m)
    state.pressure.interior = 1.0
    state.velocity.u.interior = 2.0
    state.velocity.v.interior = 3.0
    state.velocity.w.interior = 4.0
    apply_boundary_conditions(state, periodic_box_bcs())
    assert np.all(state.pressure.data == pytest.approx(1.0))
    assert np.all(state.velocity.u.data == pytest.approx(2.0))
    assert np.all(state.velocity.v.data == pytest.approx(3.0))
    assert np.all(state.velocity.w.data == pytest.approx(4.0))


def test_full_state_constant_field_preserved_free_slip_box() -> None:
    """All-free-slip, zero velocity: a constant zero field must remain
    zero everywhere (impermeable normal + zero-gradient tangential)."""
    m = mesh(1)
    state = FlowState.zeros(m)
    slip = fbc("free_slip", "neumann")
    bcs = BoundaryConditionSet(x_min=slip, x_max=slip, y_min=slip, y_max=slip, z_min=slip, z_max=slip)
    apply_boundary_conditions(state, bcs)
    assert np.all(state.pressure.data == pytest.approx(0.0))
    assert np.all(state.velocity.u.data == pytest.approx(0.0))
    assert np.all(state.velocity.v.data == pytest.approx(0.0))
    assert np.all(state.velocity.w.data == pytest.approx(0.0))


def test_apply_boundary_conditions_lid_driven_cavity_style_does_not_crash() -> None:
    m = mesh(1)
    state = FlowState.zeros(m)
    wall = fbc("no_slip", "neumann")
    lid = fbc("velocity_inlet", "neumann", velocity_value=(1.0, 0.0, 0.0))
    bcs = BoundaryConditionSet(x_min=wall, x_max=wall, y_min=wall, y_max=lid, z_min=wall, z_max=wall)
    apply_boundary_conditions(state, bcs)
    # Lid drives the tangential u-ghost above y_max; interior is zero so
    # ghost = 2*1.0 - 0.0 = 2.0.
    assert state.velocity.u.data[2, -1, 3] == pytest.approx(2.0)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _velocity_field_with(m: StructuredMesh3D, u=None, v=None, w=None):
    from navier3d.fields import FaceField as _FaceField
    from navier3d.fields import VelocityField as _VelocityField

    return _VelocityField(
        u=u if u is not None else _FaceField.zeros(m, normal_axis=0),
        v=v if v is not None else _FaceField.zeros(m, normal_axis=1),
        w=w if w is not None else _FaceField.zeros(m, normal_axis=2),
    )
