"""Tests for navier3d.fields: ScalarField, FaceField, VelocityField, FlowState.

Uses a nonsymmetric grid (nx != ny != nz) so an axis swap in shape
construction (e.g. padding the wrong axis for a given normal_axis) would
be caught by a shape-length mismatch rather than hidden by symmetry.
"""
import numpy as np
import pytest

from navier3d.fields import FaceField, FlowState, ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D

NX, NY, NZ = 3, 4, 5


@pytest.fixture(params=[1, 2])
def mesh(request) -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=2.0, ly=3.0, lz=5.0, n_ghost=request.param)


def test_scalar_field_shapes(mesh: StructuredMesh3D) -> None:
    ng = mesh.n_ghost
    field = ScalarField.zeros(mesh)
    assert field.data.shape == (NX + 2 * ng, NY + 2 * ng, NZ + 2 * ng)
    assert field.interior.shape == (NX, NY, NZ)


def test_scalar_field_interior_round_trip(mesh: StructuredMesh3D) -> None:
    field = ScalarField.zeros(mesh)
    values = np.arange(NX * NY * NZ, dtype=np.float64).reshape(NX, NY, NZ)
    field.interior = values
    np.testing.assert_array_equal(field.interior, values)
    # Ghosts remain untouched (still zero) by the interior setter.
    assert field.data[0, 0, 0] == 0.0


@pytest.mark.parametrize(
    "normal_axis, expected_shape_fn",
    [
        (0, lambda ng: (NX + 1 + 2 * ng, NY + 2 * ng, NZ + 2 * ng)),
        (1, lambda ng: (NX + 2 * ng, NY + 1 + 2 * ng, NZ + 2 * ng)),
        (2, lambda ng: (NX + 2 * ng, NY + 2 * ng, NZ + 1 + 2 * ng)),
    ],
)
def test_face_field_shapes_per_axis(mesh: StructuredMesh3D, normal_axis: int, expected_shape_fn) -> None:
    ng = mesh.n_ghost
    field = FaceField.zeros(mesh, normal_axis=normal_axis)
    assert field.data.shape == expected_shape_fn(ng)


@pytest.mark.parametrize(
    "normal_axis, expected_interior_shape",
    [
        (0, (NX + 1, NY, NZ)),
        (1, (NX, NY + 1, NZ)),
        (2, (NX, NY, NZ + 1)),
    ],
)
def test_face_field_interior_shape_per_axis(mesh: StructuredMesh3D, normal_axis: int, expected_interior_shape) -> None:
    field = FaceField.zeros(mesh, normal_axis=normal_axis)
    assert field.interior.shape == expected_interior_shape


def test_face_field_invalid_normal_axis_raises(mesh: StructuredMesh3D) -> None:
    with pytest.raises(ValueError):
        FaceField.zeros(mesh, normal_axis=3)


def test_velocity_field_components_have_correct_normal_axes(mesh: StructuredMesh3D) -> None:
    velocity = VelocityField.zeros(mesh)
    assert velocity.u.normal_axis == 0
    assert velocity.v.normal_axis == 1
    assert velocity.w.normal_axis == 2
    assert velocity.u.interior.shape == (NX + 1, NY, NZ)
    assert velocity.v.interior.shape == (NX, NY + 1, NZ)
    assert velocity.w.interior.shape == (NX, NY, NZ + 1)
    assert velocity.components() == (velocity.u, velocity.v, velocity.w)


def test_interior_range_matches_interior_shape(mesh: StructuredMesh3D) -> None:
    field = ScalarField.zeros(mesh)
    ranges = [field.interior_range(a) for a in range(3)]
    lengths = tuple(r.stop - r.start for r in ranges)
    assert lengths == field.interior.shape


def test_shifted_range_offsets_by_one(mesh: StructuredMesh3D) -> None:
    ng = mesh.n_ghost
    field = ScalarField.zeros(mesh)
    base = field.interior_range(0)
    plus = field.shifted_range(0, +1)
    minus = field.shifted_range(0, -1)
    assert plus.start == base.start + 1 and plus.stop == base.stop + 1
    assert minus.start == base.start - 1 and minus.stop == base.stop - 1
    assert minus.start == ng - 1  # reaches exactly one ghost layer in


def test_first_interior_layer_matches_interior_edges(mesh: StructuredMesh3D) -> None:
    # first_interior_layer spans the FULL padded width of the other two
    # axes (including their own ghosts), matching ghost_layer's convention.
    ng = mesh.n_ghost
    field = ScalarField.zeros(mesh)
    field.interior = np.arange(NX * NY * NZ, dtype=np.float64).reshape(NX, NY, NZ)
    np.testing.assert_array_equal(
        field.first_interior_layer(0, "lo")[ng:-ng, ng:-ng], field.interior[0, :, :]
    )
    np.testing.assert_array_equal(
        field.first_interior_layer(0, "hi")[ng:-ng, ng:-ng], field.interior[-1, :, :]
    )


def test_first_interior_layer_invalid_side_raises(mesh: StructuredMesh3D) -> None:
    field = ScalarField.zeros(mesh)
    with pytest.raises(ValueError):
        field.first_interior_layer(0, "middle")


def test_ghost_layer_nearest_and_farthest(mesh: StructuredMesh3D) -> None:
    ng = mesh.n_ghost
    field = ScalarField.zeros(mesh)
    field.data[:] = np.arange(field.data.shape[0]).reshape(-1, 1, 1)
    nearest_lo = field.ghost_layer(0, "lo", g=0)
    np.testing.assert_array_equal(nearest_lo, field.data[ng - 1, :, :])
    nearest_hi = field.ghost_layer(0, "hi", g=0)
    np.testing.assert_array_equal(nearest_hi, field.data[-ng, :, :])
    if ng > 1:
        farthest_lo = field.ghost_layer(0, "lo", g=ng - 1)
        np.testing.assert_array_equal(farthest_lo, field.data[0, :, :])


def test_ghost_layer_out_of_range_raises(mesh: StructuredMesh3D) -> None:
    field = ScalarField.zeros(mesh)
    with pytest.raises(ValueError):
        field.ghost_layer(0, "lo", g=mesh.n_ghost)
    with pytest.raises(ValueError):
        field.ghost_layer(0, "sideways", g=0)


def test_face_field_boundary_layer_is_first_interior_layer_on_normal_axis(mesh: StructuredMesh3D) -> None:
    ng = mesh.n_ghost
    field = FaceField.zeros(mesh, normal_axis=0)
    field.interior = np.arange((NX + 1) * NY * NZ, dtype=np.float64).reshape(NX + 1, NY, NZ)
    np.testing.assert_array_equal(field.boundary_layer("lo")[ng:-ng, ng:-ng], field.interior[0, :, :])
    np.testing.assert_array_equal(field.boundary_layer("hi")[ng:-ng, ng:-ng], field.interior[-1, :, :])


def test_flow_state_zeros(mesh: StructuredMesh3D) -> None:
    state = FlowState.zeros(mesh)
    assert state.time == 0.0
    assert state.step == 0
    assert state.pressure.interior.shape == (NX, NY, NZ)
    assert state.velocity.u.interior.shape == (NX + 1, NY, NZ)
    assert state.velocity.v.interior.shape == (NX, NY + 1, NZ)
    assert state.velocity.w.interior.shape == (NX, NY, NZ + 1)
