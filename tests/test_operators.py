"""Tests for navier3d.operators: gradient, divergence, scalar_laplacian,
velocity_laplacian.

Structure:
  - exactness tests (constant / linear / quadratic fields, ng in {1,2})
  - manufactured periodic convergence studies (gradient, divergence, Laplacian)
  - the D_h G_h = L_h compatibility identity (periodic, Neumann, Dirichlet)
  - discrete integration by parts and global conservation (periodic)
  - boundary-condition-specific checks (Neumann/Dirichlet gradient, no-slip
    divergence, free-slip/no-slip velocity Laplacian)
  - shape/mesh-compatibility rejection

Grids are nonsymmetric (nx != ny != nz) throughout. Convergence studies use
nx=N, ny=1.5N, nz=2N with domain lengths 1, 1.5, 2 so that dx=dy=dz=1/N at
every resolution -- nonsymmetric cell counts (catches axis-swap bugs) with
a single refinement parameter N for clean Richardson extrapolation.
"""
import math

import numpy as np
import pytest

from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_pressure_bc,
    apply_velocity_bc,
)
from navier3d.fields import FaceField, ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import (
    OperatorError,
    divergence,
    gradient,
    scalar_laplacian,
    velocity_laplacian,
)

NX, NY, NZ = 3, 4, 5


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def mesh(n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=2.0, ly=3.0, lz=5.0, n_ghost=n_ghost)


def refinement_mesh(N: int, n_ghost: int = 1) -> StructuredMesh3D:
    """nx=N, ny=1.5N, nz=2N with lx=1, ly=1.5, lz=2 -> dx=dy=dz=1/N always."""
    return StructuredMesh3D(nx=N, ny=int(1.5 * N), nz=int(2 * N), lx=1.0, ly=1.5, lz=2.0, n_ghost=n_ghost)


def fbc(velocity, pressure, velocity_value=None, pressure_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
    )


def periodic_box_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def neumann_walls_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip", "neumann")
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def dirichlet_walls_bcs(value: float = 0.0) -> BoundaryConditionSet:
    w = fbc("pressure_outlet", "dirichlet", pressure_value=value)
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def _padded_coords_cell(n_cells: int, d: float, ng: int) -> np.ndarray:
    i = np.arange(-ng, n_cells + ng)
    return (i + 0.5) * d


def _padded_coords_face(n_cells: int, d: float, ng: int) -> np.ndarray:
    i = np.arange(-ng, n_cells + ng + 1)
    return i * d


def _fill_scalar_exact(field: ScalarField, m: StructuredMesh3D, func) -> None:
    """Fill the FULL padded array (interior and ghosts) by direct exact
    sampling of `func` at true physical coordinates. Bypasses BC ghost-fill
    entirely -- used to test operator stencils in isolation from BC
    formulas."""
    ng = field.n_ghost
    x = _padded_coords_cell(m.nx, m.dx, ng)
    y = _padded_coords_cell(m.ny, m.dy, ng)
    z = _padded_coords_cell(m.nz, m.dz, ng)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    field.data[:] = func(X, Y, Z)


def _fill_face_exact(field: FaceField, m: StructuredMesh3D, func) -> None:
    ng = field.n_ghost
    cell_coords = (m.nx, m.dx), (m.ny, m.dy), (m.nz, m.dz)
    coords = []
    for axis, (n_cells, d) in enumerate(cell_coords):
        if axis == field.normal_axis:
            coords.append(_padded_coords_face(n_cells, d, ng))
        else:
            coords.append(_padded_coords_cell(n_cells, d, ng))
    X, Y, Z = np.meshgrid(*coords, indexing="ij")
    field.data[:] = func(X, Y, Z)


def _fill_scalar_interior(field: ScalarField, m: StructuredMesh3D, func) -> None:
    X, Y, Z = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    field.interior = func(X, Y, Z)


def _fill_face_interior(field: FaceField, m: StructuredMesh3D, func) -> None:
    face_coords = (m.face_coords_x(), m.face_coords_y(), m.face_coords_z())
    cell_coords = (m.cell_centers_x(), m.cell_centers_y(), m.cell_centers_z())
    coords = [face_coords[a] if a == field.normal_axis else cell_coords[a] for a in range(3)]
    X, Y, Z = np.meshgrid(*coords, indexing="ij")
    field.interior = func(X, Y, Z)


def _errors(computed: np.ndarray, exact: np.ndarray) -> tuple:
    diff = (computed - exact).ravel()
    l1 = float(np.mean(np.abs(diff)))
    l2 = float(np.sqrt(np.mean(diff ** 2)))
    linf = float(np.max(np.abs(diff)))
    return l1, l2, linf


def _orders(errors: list) -> list:
    return [math.log(e1 / e2) / math.log(2.0) for e1, e2 in zip(errors[:-1], errors[1:])]


# --------------------------------------------------------------------------
# Constant-field exactness
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ng", [1, 2])
def test_gradient_of_constant_is_zero(ng: int) -> None:
    m = mesh(ng)
    p = ScalarField.zeros(m)
    p.data[:] = 7.0
    grad = gradient(p, m)
    for comp in grad.components():
        np.testing.assert_allclose(comp.interior, 0.0, atol=1e-12)


@pytest.mark.parametrize("ng", [1, 2])
def test_laplacian_of_constant_is_zero(ng: int) -> None:
    m = mesh(ng)
    p = ScalarField.zeros(m)
    p.data[:] = -3.5
    lap = scalar_laplacian(p, m)
    np.testing.assert_allclose(lap.interior, 0.0, atol=1e-12)


@pytest.mark.parametrize("ng", [1, 2])
def test_divergence_of_constant_velocity_is_zero(ng: int) -> None:
    m = mesh(ng)
    velocity = VelocityField.zeros(m)
    velocity.u.data[:] = 2.0
    velocity.v.data[:] = -1.0
    velocity.w.data[:] = 0.5
    div = divergence(velocity, m)
    np.testing.assert_allclose(div.interior, 0.0, atol=1e-12)


# --------------------------------------------------------------------------
# Linear-field exactness (also an axis-permutation check: a != b != c)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ng", [1, 2])
def test_gradient_of_linear_field_is_exact(ng: int) -> None:
    a, b, c, d = 2.0, -3.0, 5.0, 1.0
    m = mesh(ng)
    p = ScalarField.zeros(m)
    _fill_scalar_exact(p, m, lambda x, y, z: a * x + b * y + c * z + d)
    grad = gradient(p, m)
    np.testing.assert_allclose(grad.u.interior, a, atol=1e-10)
    np.testing.assert_allclose(grad.v.interior, b, atol=1e-10)
    np.testing.assert_allclose(grad.w.interior, c, atol=1e-10)


@pytest.mark.parametrize("ng", [1, 2])
def test_laplacian_of_linear_field_is_zero(ng: int) -> None:
    m = mesh(ng)
    p = ScalarField.zeros(m)
    _fill_scalar_exact(p, m, lambda x, y, z: 2.0 * x - 3.0 * y + 5.0 * z + 1.0)
    lap = scalar_laplacian(p, m)
    np.testing.assert_allclose(lap.interior, 0.0, atol=1e-10)


@pytest.mark.parametrize("ng", [1, 2])
def test_divergence_of_linear_velocity_is_exact(ng: int) -> None:
    """u=x, v=y, w=z -> div = 3 everywhere, exact for a linear field."""
    m = mesh(ng)
    velocity = VelocityField.zeros(m)
    _fill_face_exact(velocity.u, m, lambda x, y, z: x)
    _fill_face_exact(velocity.v, m, lambda x, y, z: y)
    _fill_face_exact(velocity.w, m, lambda x, y, z: z)
    div = divergence(velocity, m)
    np.testing.assert_allclose(div.interior, 3.0, atol=1e-10)


# --------------------------------------------------------------------------
# Quadratic Laplacian exactness
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ng", [1, 2])
def test_quadratic_laplacian_is_exact(ng: int) -> None:
    m = mesh(ng)
    p = ScalarField.zeros(m)
    _fill_scalar_exact(p, m, lambda x, y, z: x ** 2 + y ** 2 + z ** 2)
    lap = scalar_laplacian(p, m)
    np.testing.assert_allclose(lap.interior, 6.0, atol=1e-10)


# --------------------------------------------------------------------------
# Manufactured periodic convergence studies
# --------------------------------------------------------------------------

RESOLUTIONS = [8, 16, 32, 64]
KX, KY, KZ = 4.0 * math.pi, 4.0 * math.pi, math.pi  # periodic on lx=1, ly=1.5, lz=2


def _phi(x, y, z):
    return np.sin(KX * x) * np.cos(KY * y) * np.sin(KZ * z)


def _phi_laplacian(x, y, z):
    return -(KX ** 2 + KY ** 2 + KZ ** 2) * _phi(x, y, z)


def _phi_grad_x(x, y, z):
    return KX * np.cos(KX * x) * np.cos(KY * y) * np.sin(KZ * z)


def _phi_grad_y(x, y, z):
    return -KY * np.sin(KX * x) * np.sin(KY * y) * np.sin(KZ * z)


def _phi_grad_z(x, y, z):
    return KZ * np.sin(KX * x) * np.cos(KY * y) * np.cos(KZ * z)


def test_scalar_laplacian_periodic_convergence() -> None:
    errors = []
    for N in RESOLUTIONS:
        m = refinement_mesh(N)
        p = ScalarField.zeros(m)
        _fill_scalar_interior(p, m, _phi)
        apply_pressure_bc(p, periodic_box_bcs())
        lap = scalar_laplacian(p, m)
        X, Y, Z = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
        exact = _phi_laplacian(X, Y, Z)
        errors.append(_errors(lap.interior, exact))

    l2s = [e[1] for e in errors]
    orders = _orders(l2s)
    for order in orders:
        assert 1.8 <= order <= 2.2, f"observed orders {orders} (L2), expected ~2"


def test_gradient_periodic_convergence() -> None:
    errors = []
    for N in RESOLUTIONS:
        m = refinement_mesh(N)
        p = ScalarField.zeros(m)
        _fill_scalar_interior(p, m, _phi)
        apply_pressure_bc(p, periodic_box_bcs())
        grad = gradient(p, m)

        Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
        Xv, Yv, Zv = np.meshgrid(m.cell_centers_x(), m.face_coords_y(), m.cell_centers_z(), indexing="ij")
        Xw, Yw, Zw = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.face_coords_z(), indexing="ij")
        diff = np.concatenate([
            (grad.u.interior - _phi_grad_x(Xu, Yu, Zu)).ravel(),
            (grad.v.interior - _phi_grad_y(Xv, Yv, Zv)).ravel(),
            (grad.w.interior - _phi_grad_z(Xw, Yw, Zw)).ravel(),
        ])
        l2 = float(np.sqrt(np.mean(diff ** 2)))
        errors.append(l2)

    orders = _orders(errors)
    for order in orders:
        assert 1.8 <= order <= 2.2, f"observed orders {orders} (L2), expected ~2"


# kx != ky deliberately: with kx=ky (and dx=dy=dz on this refinement grid) a
# trig sum-to-product identity makes the *discrete* divergence exactly zero
# at every resolution (not just in the continuum limit), which would give a
# meaningless convergence order computed from pure floating-point noise.
# u = ky*sin(kx x)cos(ky y)cos(kz z), v = -kx*cos(kx x)sin(ky y)cos(kz z) is
# divergence-free (du/dx + dv/dy = kx*ky*cos(..)-kx*ky*cos(..) = 0) for any
# kx, ky, and with kx != ky the discrete truncation error is genuinely O(h^2).
KX_SOL = 4.0 * math.pi          # m=2 on lx=1
KY_SOL = 2.0 * math.pi * 4 / 1.5  # m=4 on ly=1.5
KZ_SOL = math.pi                 # m=1 on lz=2


def _u_sol(x, y, z):
    return KY_SOL * np.sin(KX_SOL * x) * np.cos(KY_SOL * y) * np.cos(KZ_SOL * z)


def _v_sol(x, y, z):
    return -KX_SOL * np.cos(KX_SOL * x) * np.sin(KY_SOL * y) * np.cos(KZ_SOL * z)


def test_divergence_of_solenoidal_periodic_field_converges_to_zero() -> None:
    """u, v analytically divergence-free (w=0); the discrete divergence is
    O(h^2) truncation error, not exactly zero -- this is the expected,
    standard behavior for a finite-difference discretization and is
    distinct from the exact-to-roundoff constant/linear tests above."""
    l2s = []
    for N in RESOLUTIONS:
        m = refinement_mesh(N)
        velocity = VelocityField.zeros(m)
        _fill_face_interior(velocity.u, m, _u_sol)
        _fill_face_interior(velocity.v, m, _v_sol)
        # w = 0 already (VelocityField.zeros)
        apply_velocity_bc(velocity, periodic_box_bcs())
        div = divergence(velocity, m)
        l2 = float(np.sqrt(np.mean(div.interior ** 2)))
        l2s.append(l2)

    orders = _orders(l2s)
    for order in orders:
        assert 1.8 <= order <= 2.2, f"observed orders {orders} (L2), expected ~2"


# --------------------------------------------------------------------------
# D_h G_h = L_h compatibility (periodic, Neumann, Dirichlet)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bcs_factory", [periodic_box_bcs, neumann_walls_bcs, lambda: dirichlet_walls_bcs(3.0)])
def test_divergence_of_gradient_equals_laplacian(bcs_factory) -> None:
    m = mesh(1)
    rng = np.random.default_rng(0)
    p = ScalarField.zeros(m)
    p.interior = rng.uniform(-1.0, 1.0, size=p.interior.shape)
    bcs = bcs_factory()
    apply_pressure_bc(p, bcs)

    lap_direct = scalar_laplacian(p, m)
    grad = gradient(p, m)
    lap_via_div_grad = divergence(grad, m)

    np.testing.assert_allclose(lap_via_div_grad.interior, lap_direct.interior, atol=1e-10, rtol=1e-10)


# --------------------------------------------------------------------------
# Discrete integration by parts and global conservation (periodic)
# --------------------------------------------------------------------------

def test_integration_by_parts_periodic() -> None:
    m = mesh(1)
    rng = np.random.default_rng(1)
    bcs = periodic_box_bcs()

    p = ScalarField.zeros(m)
    p.interior = rng.uniform(-1.0, 1.0, size=p.interior.shape)
    apply_pressure_bc(p, bcs)

    velocity = VelocityField.zeros(m)
    for comp in velocity.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(velocity, bcs)  # synchronizes each component's duplicate boundary faces

    dV = m.cell_volume
    cell_term = float(np.sum(p.interior * divergence(velocity, m).interior) * dV)

    grad = gradient(p, m)
    face_term = 0.0
    face_term_naive = 0.0
    extra_terms = []
    for axis, (g, u) in enumerate(zip(grad.components(), velocity.components())):
        sl_excl = [slice(None)] * 3
        sl_excl[axis] = slice(0, -1)
        term_excl = float(np.sum(g.interior[tuple(sl_excl)] * u.interior[tuple(sl_excl)]) * dV)
        face_term += term_excl

        term_full = float(np.sum(g.interior * u.interior) * dV)
        face_term_naive += term_full

        sl_dup = [slice(None)] * 3
        sl_dup[axis] = -1
        extra_terms.append(float(np.sum(g.interior[tuple(sl_dup)] * u.interior[tuple(sl_dup)]) * dV))

    # Correct identity: excluding the duplicated high-index boundary face.
    assert cell_term == pytest.approx(-face_term, abs=1e-9)

    # Naively including the duplicate breaks the identity by exactly the
    # sum of the duplicate boundary terms (proving the mechanism, not just
    # avoiding it).
    assert face_term_naive == pytest.approx(face_term + sum(extra_terms), abs=1e-9)
    assert cell_term != pytest.approx(-face_term_naive, abs=1e-6)


def test_global_divergence_sums_to_zero_periodic() -> None:
    m = mesh(1)
    rng = np.random.default_rng(2)
    bcs = periodic_box_bcs()
    velocity = VelocityField.zeros(m)
    for comp in velocity.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(velocity, bcs)

    total = float(np.sum(divergence(velocity, m).interior) * m.cell_volume)
    assert total == pytest.approx(0.0, abs=1e-10)


# --------------------------------------------------------------------------
# Boundary-condition-specific operator behavior
# --------------------------------------------------------------------------

def test_gradient_at_homogeneous_neumann_wall_is_zero() -> None:
    m = mesh(1)
    p = ScalarField.zeros(m)
    p.interior = 42.0  # arbitrary; homogeneous Neumann forces zero gradient regardless
    apply_pressure_bc(p, neumann_walls_bcs())
    grad = gradient(p, m)
    assert grad.u.data[1, 2, 2] == pytest.approx(0.0, abs=1e-12)  # x_min boundary face
    assert grad.u.data[-2, 2, 2] == pytest.approx(0.0, abs=1e-12)  # x_max boundary face


def test_gradient_at_dirichlet_wall_matches_ghost_node_formula() -> None:
    m = mesh(1)
    p = ScalarField.zeros(m)
    p.interior = 0.0
    p.interior[0, :, :] = 5.0  # cell adjacent to x_min boundary
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=10.0)
    bcs = neumann_walls_bcs()
    bcs = BoundaryConditionSet(x_min=outlet, x_max=bcs.x_max, y_min=bcs.y_min, y_max=bcs.y_max, z_min=bcs.z_min, z_max=bcs.z_max)
    apply_pressure_bc(p, bcs)
    grad = gradient(p, m)
    # ghost = 2*10 - 5 = 15; grad = (p_interior0 - ghost)/dx = (5 - 15)/dx
    expected = (5.0 - 15.0) / m.dx
    assert grad.u.data[1, 2, 2] == pytest.approx(expected)


def test_divergence_respects_no_slip_boundary_values() -> None:
    m = mesh(1)  # nx=3 -> u has 4 interior faces, indices 0..3
    velocity = VelocityField.zeros(m)
    velocity.u.interior[:, 2, 2] = [99.0, 7.0, 3.0, 99.0]  # boundary faces will be zeroed
    apply_velocity_bc(velocity, neumann_walls_bcs())
    assert velocity.u.interior[0, 2, 2] == pytest.approx(0.0)
    assert velocity.u.interior[3, 2, 2] == pytest.approx(0.0)

    div = divergence(velocity, m)
    dx = m.dx
    expected = [(7.0 - 0.0) / dx, (3.0 - 7.0) / dx, (0.0 - 3.0) / dx]
    np.testing.assert_allclose(div.interior[:, 2, 2], expected)


def test_velocity_laplacian_free_slip_tangential_mirror() -> None:
    m = mesh(1)
    velocity = VelocityField.zeros(m)
    x0, z0 = 1, 2  # safely interior x, z locations for the u (normal_axis=0) field
    velocity.u.interior[x0, 0, z0] = 5.0  # first interior y-layer (adjacent to y_min ghost)
    bcs = neumann_walls_bcs()  # no_slip on x/z; override y with free_slip below
    slip = fbc("free_slip", "neumann")
    bcs = BoundaryConditionSet(x_min=bcs.x_min, x_max=bcs.x_max, y_min=slip, y_max=slip, z_min=bcs.z_min, z_max=bcs.z_max)
    apply_velocity_bc(velocity, bcs)

    lap = velocity_laplacian(velocity, m)
    dx, dy, dz = m.dx, m.dy, m.dz
    # x term: neighbors (x0-1, x0+1) both 0 -> (0 - 2*5 + 0)/dx^2
    # y term: ghost (free-slip mirror) = interior = 5; plus-neighbor = 0 -> (0 - 2*5 + 5)/dy^2
    # z term: neighbors both 0 -> (0 - 2*5 + 0)/dz^2
    expected = (0.0 - 2.0 * 5.0 + 0.0) / dx ** 2 + (0.0 - 2.0 * 5.0 + 5.0) / dy ** 2 + (0.0 - 2.0 * 5.0 + 0.0) / dz ** 2
    assert lap.u.interior[x0, 0, z0] == pytest.approx(expected)


def test_velocity_laplacian_no_slip_normal_axis_ghost() -> None:
    """Exercises the normal-axis ghost layer beyond a no-slip boundary face
    (allocated in Milestone 1, first read here)."""
    m = mesh(1)
    velocity = VelocityField.zeros(m)
    y0, z0 = 2, 2
    velocity.u.interior[1, y0, z0] = 5.0  # interior face adjacent to x_min boundary
    apply_velocity_bc(velocity, neumann_walls_bcs())
    assert velocity.u.interior[0, y0, z0] == pytest.approx(0.0)  # boundary face: no_slip -> 0

    lap = velocity_laplacian(velocity, m)
    dx, dy, dz = m.dx, m.dy, m.dz
    # At the boundary face (index 0): plus-neighbor = interior[1] = 5;
    # minus-neighbor = ghost = 2*0 - interior[1] = -5 (node reflection).
    # x term: (5 - 2*0 + (-5))/dx^2 = 0
    # y, z terms: neighbors both 0 (untouched) -> (0 - 2*0 + 0)/d^2 = 0
    assert lap.u.interior[0, y0, z0] == pytest.approx(0.0)

    # At the interior face (index 1, center = 5): minus-neighbor = boundary = 0;
    # plus-neighbor = interior[2] = 0 (untouched) -> x term = (0 - 2*5 + 0)/dx^2
    expected = (0.0 - 2.0 * 5.0 + 0.0) / dx ** 2 + (0.0 - 2.0 * 5.0 + 0.0) / dy ** 2 + (0.0 - 2.0 * 5.0 + 0.0) / dz ** 2
    assert lap.u.interior[1, y0, z0] == pytest.approx(expected)


# --------------------------------------------------------------------------
# Mesh/shape compatibility rejection
# --------------------------------------------------------------------------

def test_gradient_rejects_mismatched_mesh() -> None:
    m1 = mesh(1)
    m2 = StructuredMesh3D(nx=NX + 1, ny=NY, nz=NZ, lx=2.0, ly=3.0, lz=5.0, n_ghost=1)
    p = ScalarField.zeros(m1)
    with pytest.raises(OperatorError):
        gradient(p, m2)


def test_divergence_rejects_mismatched_mesh() -> None:
    m1 = mesh(1)
    m2 = StructuredMesh3D(nx=NX, ny=NY + 1, nz=NZ, lx=2.0, ly=3.0, lz=5.0, n_ghost=1)
    velocity = VelocityField.zeros(m1)
    with pytest.raises(OperatorError):
        divergence(velocity, m2)


def test_scalar_laplacian_rejects_mismatched_ghost_width() -> None:
    m1 = mesh(1)
    m2 = mesh(2)
    p = ScalarField.zeros(m1)
    with pytest.raises(OperatorError):
        scalar_laplacian(p, m2)


def test_divergence_rejects_swapped_component_normal_axis() -> None:
    """A VelocityField whose 'u' slot actually holds a normal_axis=1 field
    (e.g. constructed by hand rather than via VelocityField.zeros)."""
    m = mesh(1)
    velocity = VelocityField(
        u=FaceField.zeros(m, normal_axis=1),  # wrong: should be normal_axis=0
        v=FaceField.zeros(m, normal_axis=1),
        w=FaceField.zeros(m, normal_axis=2),
    )
    with pytest.raises(OperatorError):
        divergence(velocity, m)


def test_divergence_rejects_mismatched_component_ghost_width() -> None:
    m1 = mesh(1)
    m2 = mesh(2)
    velocity = VelocityField(
        u=FaceField.zeros(m2, normal_axis=0),  # wrong n_ghost relative to m1
        v=FaceField.zeros(m1, normal_axis=1),
        w=FaceField.zeros(m1, normal_axis=2),
    )
    with pytest.raises(OperatorError):
        divergence(velocity, m1)


def test_velocity_laplacian_rejects_mismatched_mesh() -> None:
    m1 = mesh(1)
    m2 = StructuredMesh3D(nx=NX, ny=NY, nz=NZ + 1, lx=2.0, ly=3.0, lz=5.0, n_ghost=1)
    velocity = VelocityField.zeros(m1)
    with pytest.raises(OperatorError):
        velocity_laplacian(velocity, m2)
