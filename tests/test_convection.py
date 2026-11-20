"""Tests for navier3d.convection: centered_convection, upwind_convection.

Grids are nonsymmetric (nx != ny != nz) throughout. Sections map to the
Milestone 6 review's 9 required operator-level tests.
"""
import numpy as np
import pytest

from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_velocity_bc,
)
from navier3d.convection import ConvectionError, centered_convection, upwind_convection
from navier3d.fields import FaceField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.projection import project

NX, NY, NZ = 4, 5, 6


def mesh(n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=n_ghost)


def fbc(velocity, pressure="neumann", velocity_value=None, pressure_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
    )


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def wall_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def _padded_coords_cell(n: int, d: float, ng: int) -> np.ndarray:
    i = np.arange(-ng, n + ng)
    return (i + 0.5) * d


def _padded_coords_face(n: int, d: float, ng: int) -> np.ndarray:
    i = np.arange(-ng, n + ng + 1)
    return i * d


def _fill_face_exact(field: FaceField, m: StructuredMesh3D, func) -> None:
    """Sample `func` at every stored grid point (interior AND ghosts),
    bypassing apply_velocity_bc entirely -- isolates the operator formula
    from boundary-condition ghost-fill correctness (a non-periodic
    manufactured field like u=x is not compatible with periodic ghost
    wrap, which would corrupt a BC-filled test near the boundary; direct
    sampling sidesteps that and tests convection.py in pure isolation,
    the same technique used for operators.py in Milestone 2)."""
    ng = field.n_ghost
    cell_specs = ((m.nx, m.dx), (m.ny, m.dy), (m.nz, m.dz))
    coords = []
    for axis, (n, d) in enumerate(cell_specs):
        coords.append(_padded_coords_face(n, d, ng) if axis == field.normal_axis else _padded_coords_cell(n, d, ng))
    X, Y, Z = np.meshgrid(*coords, indexing="ij")
    field.data[:] = func(X, Y, Z)


def random_full_velocity(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> VelocityField:
    rng = np.random.default_rng(seed)
    velocity = VelocityField.zeros(m)
    for comp in velocity.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(velocity, bcs)
    return velocity


def _inner_product(a: VelocityField, b: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> float:
    dV = mesh.cell_volume
    total = 0.0
    for axis, (ca, cb) in enumerate(zip(a.components(), b.components())):
        ia, ib = ca.interior, cb.interior
        if bcs.is_periodic_axis(axis):
            sl = [slice(None)] * 3
            sl[axis] = slice(0, -1)
            ia, ib = ia[tuple(sl)], ib[tuple(sl)]
        total += np.sum(ia * ib)
    return float(total * dV)


# --------------------------------------------------------------------------
# 1. Zero velocity
# --------------------------------------------------------------------------

@pytest.mark.parametrize("scheme", [centered_convection, upwind_convection])
@pytest.mark.parametrize("bcs_factory", [periodic_bcs, wall_bcs])
def test_1_zero_velocity(scheme, bcs_factory) -> None:
    m = mesh(1)
    v0 = VelocityField.zeros(m)
    apply_velocity_bc(v0, bcs_factory())
    N = scheme(v0, m)
    for comp in N.components():
        assert np.max(np.abs(comp.interior)) == 0.0


# --------------------------------------------------------------------------
# 2. Uniform velocity on periodic domains
# --------------------------------------------------------------------------

@pytest.mark.parametrize("scheme", [centered_convection, upwind_convection])
def test_2_uniform_velocity_periodic(scheme) -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    v = VelocityField.zeros(m)
    v.u.data[:] = 2.0
    v.v.data[:] = -1.0
    v.w.data[:] = 0.5
    apply_velocity_bc(v, bcs)
    N = scheme(v, m)
    for comp in N.components():
        np.testing.assert_allclose(comp.interior, 0.0, atol=1e-12)


# --------------------------------------------------------------------------
# 3 & 8. Manufactured polynomial fields with analytically known convection;
# independently verifies the self-term AND cross-term interpolations (not
# merely "does convection look plausible")
# --------------------------------------------------------------------------

def test_3_polynomial_self_term_exact() -> None:
    """u=x (v=w=0): N_u = d(x^2)/dx = 2x exactly (finite-difference of a
    quadratic is exact); N_v=N_w=0 since v=w=0 identically."""
    m = mesh(1)
    v = VelocityField.zeros(m)
    _fill_face_exact(v.u, m, lambda x, y, z: x)
    N = centered_convection(v, m)
    Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    np.testing.assert_allclose(N.u.interior, 2.0 * Xu, atol=1e-12)
    np.testing.assert_allclose(N.v.interior, 0.0, atol=1e-12)
    np.testing.assert_allclose(N.w.interior, 0.0, atol=1e-12)


def test_8_polynomial_cross_term_exact_independent_of_self_term() -> None:
    """u=y, v=x (w=0): self terms vanish identically (u^2, v^2 each
    independent of their own normal axis), isolating the cross-term
    interpolation exactly: N_u = d(xy)/dy = x, N_v = d(xy)/dx = y, N_w=0.
    This independently verifies the edge-interpolation formula (not just
    "convection looks self-consistent") since the expected values are
    derived by hand from the interpolation definitions in the module
    docstring, not from convection.py's own code."""
    m = mesh(1)
    v = VelocityField.zeros(m)
    _fill_face_exact(v.u, m, lambda x, y, z: y)
    _fill_face_exact(v.v, m, lambda x, y, z: x)
    N = centered_convection(v, m)
    Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(m.cell_centers_x(), m.face_coords_y(), m.cell_centers_z(), indexing="ij")
    np.testing.assert_allclose(N.u.interior, Xu, atol=1e-12)
    np.testing.assert_allclose(N.v.interior, Yv, atol=1e-12)
    np.testing.assert_allclose(N.w.interior, 0.0, atol=1e-12)


def test_polynomial_z_cross_terms_exact() -> None:
    """u=z, w=x (v=0): isolates the d(uw)/dz and d(uw)/dx cross terms
    specifically (distinct axis pairing from the x/y test above)."""
    m = mesh(1)
    v = VelocityField.zeros(m)
    _fill_face_exact(v.u, m, lambda x, y, z: z)
    _fill_face_exact(v.w, m, lambda x, y, z: x)
    N = centered_convection(v, m)
    Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.face_coords_z(), indexing="ij")
    np.testing.assert_allclose(N.u.interior, Xu, atol=1e-12)  # d(xz)/dz = x
    np.testing.assert_allclose(N.v.interior, 0.0, atol=1e-12)
    np.testing.assert_allclose(N.w.interior, Zw, atol=1e-12)  # d(xz)/dx = z


# --------------------------------------------------------------------------
# 4. Axis permutation and nonsymmetric grids
# --------------------------------------------------------------------------

def test_4_axis_permutation_distinct_linear_fields() -> None:
    """u=y, v=z, w=x (a genuine 3-cycle, distinct from the x/y-only test
    above): catches a copy-pasted axis index in any of the three
    permuted convective-term computations. Self terms vanish (u^2 indep.
    of x, v^2 indep. of y, w^2 indep. of z); cross terms: N_u=d(uw)/dz
    [uw=xy... wait: u=y,w=x -> uw=xy, d(xy)/dz=0] etc. -- computed by
    hand below via the same interpolation definitions."""
    m = mesh(1)
    v = VelocityField.zeros(m)
    _fill_face_exact(v.u, m, lambda x, y, z: y)
    _fill_face_exact(v.v, m, lambda x, y, z: z)
    _fill_face_exact(v.w, m, lambda x, y, z: x)
    N = centered_convection(v, m)
    # N_u = d(u^2)/dx + d(uv)/dy + d(uw)/dz = d(y^2)/dx[=0] + d(yz)/dy[=z] + d(yx)/dz[=0] = z
    # N_v = d(v^2)/dy + d(uv)/dx + d(vw)/dz = d(z^2)/dy[=0] + d(yz)/dx[=0] + d(zx)/dz[=x] = x
    # N_w = d(w^2)/dz + d(uw)/dx + d(vw)/dy = d(x^2)/dz[=0] + d(yx)/dx[=y] + d(zx)/dy[=0] = y
    Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(m.cell_centers_x(), m.face_coords_y(), m.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.face_coords_z(), indexing="ij")
    np.testing.assert_allclose(N.u.interior, Zu, atol=1e-12)
    np.testing.assert_allclose(N.v.interior, Xv, atol=1e-12)
    np.testing.assert_allclose(N.w.interior, Yw, atol=1e-12)


# --------------------------------------------------------------------------
# 5. ng=1 and ng=2
# --------------------------------------------------------------------------

@pytest.mark.parametrize("n_ghost", [1, 2])
@pytest.mark.parametrize("scheme", [centered_convection, upwind_convection])
def test_5_works_at_ng1_and_ng2(scheme, n_ghost: int) -> None:
    m = mesh(n_ghost)
    v = random_full_velocity(m, wall_bcs(), seed=3)
    N = scheme(v, m)
    for comp in N.components():
        assert np.all(np.isfinite(comp.interior))
        assert comp.n_ghost == n_ghost


# --------------------------------------------------------------------------
# 6. Conservative global momentum test (periodic)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("scheme", [centered_convection, upwind_convection])
def test_6_global_momentum_conservation_periodic(scheme) -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    v = random_full_velocity(m, bcs, seed=4)
    N = scheme(v, m)
    dV = m.cell_volume
    # exclude each component's own periodic duplicate face (Milestone 2's
    # established "periodic duplicate normal faces" convention) -- without
    # this, the sum is polluted by double-counting the shared boundary
    # face and is NOT near roundoff (verified during development).
    for axis, comp in enumerate(N.components()):
        sl = [slice(None)] * 3
        sl[axis] = slice(0, -1)
        total = float(np.sum(comp.interior[tuple(sl)]) * dV)
        assert abs(total) < 1e-9


def test_6_naive_sum_including_duplicate_is_not_conserved() -> None:
    """Companion check proving the exclusion above is load-bearing, not
    cargo-culted: including the duplicate face breaks conservation."""
    m = mesh(1)
    bcs = periodic_bcs()
    v = random_full_velocity(m, bcs, seed=4)
    N = centered_convection(v, m)
    dV = m.cell_volume
    naive_total = float(np.sum(N.u.interior) * dV)
    assert abs(naive_total) > 1e-6


# --------------------------------------------------------------------------
# 7. Semi-discrete kinetic-energy production (centered/skew form)
# --------------------------------------------------------------------------

def test_7_centered_energy_production_near_roundoff_on_divergence_free_field() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_full_velocity(m, bcs, seed=5)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")
    assert result.max_divergence_after < 1e-9

    N = centered_convection(result.velocity, m)
    energy_production = _inner_product(result.velocity, N, m, bcs)
    scale = _inner_product(result.velocity, result.velocity, m, bcs)
    assert abs(energy_production) < 1e-8 * max(scale, 1.0)


# --------------------------------------------------------------------------
# 9. Compare conservative centered vs. upwind on a discrete divergence-free field
# --------------------------------------------------------------------------

def test_9_upwind_dissipates_relative_to_centered() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    u_star = random_full_velocity(m, bcs, seed=6)
    result = project(u_star, bcs, m, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")

    N_centered = centered_convection(result.velocity, m)
    N_upwind = upwind_convection(result.velocity, m)

    e_centered = _inner_product(result.velocity, N_centered, m, bcs)
    e_upwind = _inner_product(result.velocity, N_upwind, m, bcs)

    assert abs(e_centered) < 1e-8
    # upwind's energy production is strictly positive (net dissipative,
    # since dK/dt from convection = -<u,N(u)>) and much larger in
    # magnitude than centered's roundoff-level value
    assert e_upwind > 1e-6
    assert e_upwind > abs(e_centered) * 1e3

    # the two schemes give genuinely different results (not aliased/equal)
    diff = np.max(np.abs(N_centered.u.interior - N_upwind.u.interior))
    assert diff > 1e-6


# --------------------------------------------------------------------------
# Validation / error handling
# --------------------------------------------------------------------------

def test_rejects_wrong_normal_axis() -> None:
    m = mesh(1)
    v = VelocityField.zeros(m)
    v.u.normal_axis = 1  # corrupt it directly (bypassing the constructor)
    with pytest.raises(ConvectionError):
        centered_convection(v, m)


def test_rejects_mismatched_n_ghost() -> None:
    m1 = mesh(1)
    m2 = mesh(2)
    v = VelocityField.zeros(m1)
    with pytest.raises(ConvectionError):
        centered_convection(v, m2)


def test_rejects_mismatched_shape() -> None:
    m1 = mesh(1)
    m2 = StructuredMesh3D(nx=NX + 1, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    v = VelocityField.zeros(m1)
    with pytest.raises(ConvectionError):
        centered_convection(v, m2)
