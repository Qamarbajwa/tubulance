"""Tests for navier3d.pressure: PressurePoissonSystem.

Structure:
  - matrix assembly: shape, sparsity, symmetry, CSR storage
  - assembled operator vs matrix-free scalar_laplacian (the "critical
    consistency test")
  - null space: A @ ones = 0 (periodic/Neumann), absent for Dirichlet
  - pressure-gradient invariance under an additive constant
  - RHS compatibility: strict rejection, mean-removal auto-correction
  - direct vs CG agreement; zero_mean vs pin_cell gradient agreement
  - manufactured solutions (periodic, all-Neumann, Dirichlet, mixed) with
    L1/L2/Linf convergence tables at 4 resolutions, algebraic residual
    reported separately from discretization error
  - energy property x^T A x >= 0
  - performance / matrix-reuse / no-dense-matrix checks
  - edge cases: constant/zero RHS, max-iteration failure, BC-change
    requires a new system

Grids are nonsymmetric (nx != ny != nz) throughout. Convergence studies
fix the physical domain (lx=1, ly=1.25, lz=1.5) and use nx=N, ny=1.25N,
nz=1.5N so dx=dy=dz=1/N at every resolution -- a smaller nonsymmetric
multiplier than Milestone 2's (which would make N=64 solves too slow for
a full pressure-system test suite): N in {4, 8, 16, 32} keeps the whole
suite fast while still exercising nonsymmetric cell counts and clean
Richardson doubling.
"""
import math

import numpy as np
import pytest
import scipy.sparse as sp

from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_pressure_bc,
)
from navier3d.fields import ScalarField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import scalar_laplacian
from navier3d.pressure import PressurePoissonSystem, PressureSystemError, SolveDiagnostics

NX, NY, NZ = 3, 4, 5


def mesh(n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=2.0, ly=3.0, lz=5.0, n_ghost=n_ghost)


def refinement_mesh(N: int, n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=N, ny=int(1.25 * N), nz=int(1.5 * N), lx=1.0, ly=1.25, lz=1.5, n_ghost=n_ghost)


def fbc(velocity, pressure, velocity_value=None, pressure_value=None, pressure_gradient_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
        pressure_gradient_value=pressure_gradient_value,
    )


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def neumann_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip", "neumann")
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def dirichlet_bcs(value: float = 0.0) -> BoundaryConditionSet:
    w = fbc("pressure_outlet", "dirichlet", pressure_value=value)
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def _errors(computed: np.ndarray, exact: np.ndarray) -> tuple:
    diff = (computed - exact).ravel()
    return float(np.mean(np.abs(diff))), float(np.sqrt(np.mean(diff ** 2))), float(np.max(np.abs(diff)))


def _orders(errors: list) -> list:
    return [math.log(e1 / e2) / math.log(2.0) for e1, e2 in zip(errors[:-1], errors[1:])]


RESOLUTIONS = [4, 8, 16, 32]


# --------------------------------------------------------------------------
# Matrix assembly: shape, sparsity, symmetry, storage
# --------------------------------------------------------------------------

def test_matrix_shape() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, neumann_bcs(), rhs_compatibility="mean_removal")
    n = NX * NY * NZ
    assert system.shape == (n, n)
    assert system.matrix.shape == (n, n)


def test_matrix_sparsity_seven_point() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, periodic_bcs(), rhs_compatibility="mean_removal")
    # every interior periodic cell has exactly 7 nonzeros (itself + 6 neighbors)
    nnz_per_row = np.diff(system.matrix.tocsr().indptr)
    assert np.all(nnz_per_row == 7)


def test_matrix_is_csr() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, neumann_bcs(), rhs_compatibility="mean_removal")
    assert sp.issparse(system.matrix)
    assert system.matrix.format == "csr"


def test_matrix_symmetric() -> None:
    for bcs in (periodic_bcs(), neumann_bcs(), dirichlet_bcs(1.0)):
        m = mesh(1)
        system = PressurePoissonSystem(m, bcs, rhs_compatibility="mean_removal")
        diff = (system.matrix - system.matrix.T)
        assert abs(diff).max() < 1e-12


def test_pinned_matrix_symmetric() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, periodic_bcs(), solver="direct", null_space_strategy="pin_cell")
    diff = (system.matrix - system.matrix.T)
    assert abs(diff).max() < 1e-12


# --------------------------------------------------------------------------
# Critical consistency test: assembled operator vs matrix-free Laplacian
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bcs_factory,homogeneous_kwargs", [
    (periodic_bcs, {}),
    (neumann_bcs, {}),
    (lambda: dirichlet_bcs(0.0), {}),
])
def test_assembled_matrix_matches_matrix_free_laplacian_homogeneous(bcs_factory, homogeneous_kwargs) -> None:
    """A p = -L_h p exactly, for homogeneous BCs (matches the reviewer's
    literal formula -- see module docstring; the general inhomogeneous
    case is covered by test_assembled_matrix_matches_matrix_free_laplacian_inhomogeneous)."""
    m = mesh(1)
    bcs = bcs_factory()
    rng = np.random.default_rng(0)
    p = ScalarField.zeros(m)
    p.interior = rng.uniform(-1.0, 1.0, size=p.interior.shape)
    apply_pressure_bc(p, bcs)
    lap = scalar_laplacian(p, m)

    system = PressurePoissonSystem(m, bcs, rhs_compatibility="mean_removal")
    p_vec = p.interior.ravel(order="C")
    Ap = system.matrix @ p_vec
    np.testing.assert_allclose(Ap, -lap.interior.ravel(order="C"), atol=1e-10)


def test_assembled_matrix_matches_matrix_free_laplacian_inhomogeneous() -> None:
    """General relation: L_h_matrix @ p + correction == L_h_full(p) (see
    module docstring "Boundary elimination and the correction vector"),
    for a mix of inhomogeneous Dirichlet and inhomogeneous Neumann faces."""
    m = mesh(1)
    dwall = fbc("pressure_outlet", "dirichlet", pressure_value=3.0)
    nwall = fbc("no_slip", "neumann", pressure_gradient_value=2.0)
    free = fbc("no_slip", "neumann")
    bcs = BoundaryConditionSet(x_min=dwall, x_max=free, y_min=nwall, y_max=free, z_min=free, z_max=free)
    rng = np.random.default_rng(1)
    p = ScalarField.zeros(m)
    p.interior = rng.uniform(-1.0, 1.0, size=p.interior.shape)
    apply_pressure_bc(p, bcs, spacing=m.spacing)
    lap = scalar_laplacian(p, m)

    system = PressurePoissonSystem(m, bcs, solver="direct")
    p_vec = p.interior.ravel(order="C")
    L_p = system.laplacian_matrix @ p_vec
    np.testing.assert_allclose(L_p + system._correction, lap.interior.ravel(order="C"), atol=1e-10)


def test_as_interior_tangential_accepts_already_interior_array() -> None:
    from navier3d.pressure import _as_interior_tangential

    m = mesh(1)
    arr = np.ones((NY, NZ))  # already interior-shaped for an x-axis face
    result = _as_interior_tangential(arr, m, axis=0, name="test")
    assert result is arr


def test_as_interior_tangential_rejects_wrong_shape() -> None:
    from navier3d.pressure import _as_interior_tangential

    m = mesh(1)
    arr = np.ones((NY + 5, NZ + 5))  # matches neither interior nor full-padded shape
    with pytest.raises(PressureSystemError):
        _as_interior_tangential(arr, m, axis=0, name="test")


def test_scalar_laplacian_is_independently_implemented() -> None:
    """Sanity guard for the reviewer's stated concern: scalar_laplacian must
    not be implemented as divergence(gradient(phi)), or the D_h G_h = L_h
    and this consistency test would be tautological. Confirmed by source
    inspection (operators.py: scalar_laplacian -> _centered_laplacian ->
    _interior_shifted, entirely separate from gradient's
    _face_gradient_term / divergence's _cell_divergence_term); this test
    additionally checks the two code paths give bit-identical-up-to-roundoff
    results on a case that would NOT be tautological if they were secretly
    the same function aliased under two names: a case where scalar_laplacian
    is compared against an independently hand-written 7-point stencil.
    """
    m = mesh(1)
    rng = np.random.default_rng(2)
    p = ScalarField.zeros(m)
    p.interior = rng.uniform(-1.0, 1.0, size=p.interior.shape)
    apply_pressure_bc(p, periodic_bcs())

    lap = scalar_laplacian(p, m)

    # Hand-written 7-point stencil, independent of both operators.py and
    # pressure.py's matrix assembly.
    d = p.data
    dx2, dy2, dz2 = m.dx ** 2, m.dy ** 2, m.dz ** 2
    hand = (
        (d[2:, 1:-1, 1:-1] - 2 * d[1:-1, 1:-1, 1:-1] + d[:-2, 1:-1, 1:-1]) / dx2
        + (d[1:-1, 2:, 1:-1] - 2 * d[1:-1, 1:-1, 1:-1] + d[1:-1, :-2, 1:-1]) / dy2
        + (d[1:-1, 1:-1, 2:] - 2 * d[1:-1, 1:-1, 1:-1] + d[1:-1, 1:-1, :-2]) / dz2
    )
    np.testing.assert_allclose(lap.interior, hand, atol=1e-12)


# --------------------------------------------------------------------------
# Null space
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bcs_factory", [periodic_bcs, neumann_bcs])
def test_null_space_constant_vector(bcs_factory) -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, bcs_factory(), rhs_compatibility="mean_removal")
    assert system.has_null_space
    ones = np.ones(system.shape[0])
    result = system.matrix @ ones
    np.testing.assert_allclose(result, 0.0, atol=1e-10)


def test_dirichlet_has_no_null_space() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    assert not system.has_null_space
    ones = np.ones(system.shape[0])
    result = system.matrix @ ones
    assert np.max(np.abs(result)) > 1e-6  # emphatically not zero


def test_single_dirichlet_face_removes_null_space() -> None:
    """Even one Dirichlet face (rest Neumann) should make the system nonsingular."""
    m = mesh(1)
    dwall = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    free = fbc("no_slip", "neumann")
    bcs = BoundaryConditionSet(x_min=dwall, x_max=free, y_min=free, y_max=free, z_min=free, z_max=free)
    system = PressurePoissonSystem(m, bcs, solver="direct")
    assert not system.has_null_space


def test_pinned_matrix_null_space_removed() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, periodic_bcs(), solver="direct", null_space_strategy="pin_cell")
    ones = np.ones(system.shape[0])
    result = system.matrix @ ones
    assert np.max(np.abs(result)) > 1e-6


# --------------------------------------------------------------------------
# Pressure-gradient invariance under an additive constant
# --------------------------------------------------------------------------

def test_pressure_gradient_invariant_to_additive_constant() -> None:
    from navier3d.operators import gradient

    m = mesh(1)
    bcs = periodic_bcs()
    rng = np.random.default_rng(3)
    p = ScalarField.zeros(m)
    p.interior = rng.uniform(-1.0, 1.0, size=p.interior.shape)
    apply_pressure_bc(p, bcs)
    grad1 = gradient(p, m)

    p_shifted = ScalarField.zeros(m)
    p_shifted.interior = p.interior + 7.3
    apply_pressure_bc(p_shifted, bcs)
    grad2 = gradient(p_shifted, m)

    for c1, c2 in zip(grad1.components(), grad2.components()):
        np.testing.assert_allclose(c1.interior, c2.interior, atol=1e-12)


# --------------------------------------------------------------------------
# RHS compatibility
# --------------------------------------------------------------------------

def test_incompatible_rhs_rejected_strict() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, neumann_bcs(), rhs_compatibility="strict")
    rhs = ScalarField.zeros(m)
    rhs.interior = 5.0  # sum != 0: incompatible with an all-Neumann system
    with pytest.raises(PressureSystemError):
        system.solve(rhs)


def test_compatible_rhs_accepted_strict() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, neumann_bcs(), rhs_compatibility="strict", tol=1e-8)
    rhs = ScalarField.zeros(m)
    values = np.zeros(rhs.interior.shape)
    values.flat[0] = 1.0
    values.flat[1] = -1.0  # sums to exactly zero
    rhs.interior = values
    sol, diag = system.solve(rhs)
    assert diag.compatibility_error == pytest.approx(0.0, abs=1e-10)


def test_mean_removal_auto_corrects_and_reports_compatibility_error() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, neumann_bcs(), rhs_compatibility="mean_removal", tol=1e-8)
    rhs = ScalarField.zeros(m)
    rhs.interior = 5.0  # incompatible; mean_removal should silently fix it
    sol, diag = system.solve(rhs)
    assert diag.converged
    expected_compat = 5.0 * NX * NY * NZ * m.cell_volume
    assert diag.compatibility_error == pytest.approx(expected_compat)


def test_dirichlet_system_ignores_compatibility() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct", rhs_compatibility="strict")
    rhs = ScalarField.zeros(m)
    rhs.interior = 5.0  # would be "incompatible" for a singular system, but this one isn't singular
    sol, diag = system.solve(rhs)  # must not raise
    assert diag.compatibility_error == 0.0


# --------------------------------------------------------------------------
# Direct vs CG agreement; zero_mean vs pin_cell agreement
# --------------------------------------------------------------------------

def test_direct_and_cg_agree_dirichlet() -> None:
    m = mesh(1)
    rng = np.random.default_rng(4)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)

    sys_direct = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    sys_cg = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="cg", tol=1e-12)
    p_direct, _ = sys_direct.solve(rhs)
    p_cg, diag_cg = sys_cg.solve(rhs)
    assert diag_cg.converged
    np.testing.assert_allclose(p_direct.interior, p_cg.interior, atol=1e-7)


def test_zero_mean_and_pin_cell_gradients_agree() -> None:
    from navier3d.operators import gradient

    m = mesh(1)
    bcs = neumann_bcs()
    rng = np.random.default_rng(5)
    rhs = ScalarField.zeros(m)
    values = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)
    values -= values.mean()  # ensure exact compatibility
    rhs.interior = values

    sys_zm = PressurePoissonSystem(m, bcs, solver="cg", null_space_strategy="zero_mean", tol=1e-12)
    sys_pin = PressurePoissonSystem(m, bcs, solver="direct", null_space_strategy="pin_cell")
    p_zm, _ = sys_zm.solve(rhs)
    p_pin, _ = sys_pin.solve(rhs)

    apply_pressure_bc(p_zm, bcs)
    apply_pressure_bc(p_pin, bcs)
    grad_zm = gradient(p_zm, m)
    grad_pin = gradient(p_pin, m)
    for c1, c2 in zip(grad_zm.components(), grad_pin.components()):
        np.testing.assert_allclose(c1.interior, c2.interior, atol=1e-6)

    # And the pressure fields themselves differ only by a constant.
    diff = p_zm.interior - p_pin.interior
    assert np.std(diff) < 1e-6


# --------------------------------------------------------------------------
# Manufactured solutions + convergence
# --------------------------------------------------------------------------

def _manufactured_periodic(m: StructuredMesh3D):
    mx, my, mz = 1, 1, 1
    kx, ky, kz = 2 * math.pi * mx / m.lx, 2 * math.pi * my / m.ly, 2 * math.pi * mz / m.lz
    X, Y, Z = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    phi = np.sin(kx * X) * np.cos(ky * Y) * np.sin(kz * Z)
    rhs = -(kx ** 2 + ky ** 2 + kz ** 2) * phi
    return phi, rhs


def _manufactured_neumann(m: StructuredMesh3D):
    mx, my, mz = 1, 1, 1
    kx, ky, kz = mx * math.pi / m.lx, my * math.pi / m.ly, mz * math.pi / m.lz
    X, Y, Z = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    phi = np.cos(kx * X) * np.cos(ky * Y) * np.cos(kz * Z)
    rhs = -(kx ** 2 + ky ** 2 + kz ** 2) * phi
    return phi, rhs  # dphi/dn = 0 at every face by construction


def _manufactured_dirichlet(m: StructuredMesh3D):
    mx, my, mz = 1, 1, 1
    kx, ky, kz = mx * math.pi / m.lx, my * math.pi / m.ly, mz * math.pi / m.lz
    X, Y, Z = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    phi = np.sin(kx * X) * np.sin(ky * Y) * np.sin(kz * Z)
    rhs = -(kx ** 2 + ky ** 2 + kz ** 2) * phi
    return phi, rhs  # phi = 0 on every face by construction


def _manufactured_mixed(m: StructuredMesh3D):
    """x: Dirichlet (V_lo=0, V_hi=lx^2); y, z: homogeneous Neumann.

    A Dirichlet BC here is a single scalar per *whole face*, so the
    manufactured solution's x_min/x_max values must be literally constant
    across y, z -- a purely additive f(x)+g(y)+h(z) form does NOT satisfy
    that (g(y)+h(z) still varies across the x=const face). Instead use
    phi = f(x) + q(x)*g(y)*h(z) with q(x)=sin(pi*x/lx), which vanishes at
    both x=0 and x=lx, so the second term drops out entirely on the
    Dirichlet faces and only f(x) (=x^2 here) determines the (constant)
    boundary value there.
    """
    my, mz = 1, 1
    kx_q = math.pi / m.lx
    ky, kz = my * math.pi / m.ly, mz * math.pi / m.lz
    X, Y, Z = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    q = np.sin(kx_q * X)
    gh = np.cos(ky * Y) * np.cos(kz * Z)
    phi = X ** 2 + q * gh
    rhs = 2.0 - (kx_q ** 2 + ky ** 2 + kz ** 2) * q * gh
    return phi, rhs


def _mixed_bcs(m: StructuredMesh3D) -> BoundaryConditionSet:
    d_lo = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    d_hi = fbc("pressure_outlet", "dirichlet", pressure_value=m.lx ** 2)
    free = fbc("no_slip", "neumann")
    return BoundaryConditionSet(x_min=d_lo, x_max=d_hi, y_min=free, y_max=free, z_min=free, z_max=free)


@pytest.mark.parametrize("case,bcs_factory,manufactured,solver,null_strategy,rhs_mode", [
    ("periodic", periodic_bcs, _manufactured_periodic, "cg", "zero_mean", "mean_removal"),
    ("neumann", neumann_bcs, _manufactured_neumann, "cg", "zero_mean", "mean_removal"),
    ("dirichlet", lambda: dirichlet_bcs(0.0), _manufactured_dirichlet, "direct", "zero_mean", "strict"),
])
def test_manufactured_solution_convergence(case, bcs_factory, manufactured, solver, null_strategy, rhs_mode) -> None:
    l2s = []
    for N in RESOLUTIONS:
        m = refinement_mesh(N)
        bcs = bcs_factory()
        phi_exact, rhs_exact = manufactured(m)
        rhs = ScalarField.zeros(m)
        rhs.interior = rhs_exact
        system = PressurePoissonSystem(m, bcs, solver=solver, null_space_strategy=null_strategy,
                                        rhs_compatibility=rhs_mode, tol=1e-11)
        sol, diag = system.solve(rhs)
        assert diag.converged

        p_h, p_e = sol.interior, phi_exact
        if system.has_null_space:
            p_h = p_h - np.mean(p_h)
            p_e = p_e - np.mean(p_e)
        l1, l2, linf = _errors(p_h, p_e)
        l2s.append(l2)

    orders = _orders(l2s)
    for order in orders:
        assert 1.7 <= order <= 2.3, f"{case}: observed orders {orders}, expected ~2"


def test_manufactured_mixed_dirichlet_neumann_convergence() -> None:
    l2s = []
    for N in RESOLUTIONS:
        m = refinement_mesh(N)
        bcs = _mixed_bcs(m)
        phi_exact, rhs_exact = _manufactured_mixed(m)
        rhs = ScalarField.zeros(m)
        rhs.interior = rhs_exact
        system = PressurePoissonSystem(m, bcs, solver="direct")
        assert not system.has_null_space
        sol, diag = system.solve(rhs)
        assert diag.converged
        _, l2, _ = _errors(sol.interior, phi_exact)
        l2s.append(l2)

    orders = _orders(l2s)
    for order in orders:
        assert 1.7 <= order <= 2.3, f"mixed: observed orders {orders}, expected ~2"


def test_algebraic_residual_reported_separately_from_discretization_error() -> None:
    """A small algebraic residual (||b - Ax||) must never be conflated with
    PDE discretization error (||p_h - p_exact||); this test computes both
    independently and shows the algebraic residual is many orders tighter
    (solver tolerance) than the (much larger, O(h^2)) discretization error."""
    m = refinement_mesh(8)
    bcs = periodic_bcs()
    phi_exact, rhs_exact = _manufactured_periodic(m)
    rhs = ScalarField.zeros(m)
    rhs.interior = rhs_exact
    system = PressurePoissonSystem(m, bcs, solver="cg", rhs_compatibility="mean_removal", tol=1e-12)
    sol, diag = system.solve(rhs)

    algebraic_residual = diag.final_residual  # ||b_internal - A p_vec||
    p_h = sol.interior - np.mean(sol.interior)
    p_e = phi_exact - np.mean(phi_exact)
    _, discretization_l2, _ = _errors(p_h, p_e)

    assert algebraic_residual < 1e-8
    assert discretization_l2 > 1e-3  # coarse grid (N=8): real, non-negligible truncation error
    assert algebraic_residual < discretization_l2 / 1000  # unambiguously different scales


# --------------------------------------------------------------------------
# Energy property: x^T A x >= 0
# --------------------------------------------------------------------------

def test_energy_nonnegative_and_zero_for_constants_unconstrained() -> None:
    m = mesh(1)
    rng = np.random.default_rng(6)
    for bcs in (periodic_bcs(), neumann_bcs()):
        system = PressurePoissonSystem(m, bcs, rhs_compatibility="mean_removal")
        for _ in range(5):
            x = rng.uniform(-1.0, 1.0, size=system.shape[0])
            energy = float(x @ (system.matrix @ x))
            assert energy >= -1e-10
        ones = np.ones(system.shape[0])
        assert float(ones @ (system.matrix @ ones)) == pytest.approx(0.0, abs=1e-8)


def test_energy_strictly_positive_for_admissible_nonzero_constrained() -> None:
    m = mesh(1)
    rng = np.random.default_rng(7)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    for _ in range(5):
        x = rng.uniform(-1.0, 1.0, size=system.shape[0])
        energy = float(x @ (system.matrix @ x))
        assert energy > 0.0


# --------------------------------------------------------------------------
# Performance / matrix reuse / storage
# --------------------------------------------------------------------------

def test_matrix_reused_across_multiple_rhs_without_reassembly() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    matrix_id_before = id(system.matrix)
    rng = np.random.default_rng(8)
    for _ in range(3):
        rhs = ScalarField.zeros(m)
        rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)
        sol, diag = system.solve(rhs)
        assert diag.assembly_time == system.assembly_time  # same recorded assembly, not re-timed per solve
    assert id(system.matrix) == matrix_id_before  # matrix object never rebuilt


def test_update_bcs_reuses_matrix_object_across_changing_neumann_values() -> None:
    """Milestone 5 requirement: fixed mesh + fixed BC TYPES reuse the sparse
    matrix (and, for solver='direct', its LU factorization); time-varying
    inhomogeneous Neumann VALUES update only the correction/RHS."""
    m = mesh(1)
    w = fbc("no_slip", "neumann", pressure_gradient_value=0.0)
    bcs0 = BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)
    system = PressurePoissonSystem(m, bcs0, solver="direct", null_space_strategy="pin_cell")
    matrix_id = id(system.matrix)
    lu_id = id(system._lu)
    assembly_time = system.assembly_time

    rng = np.random.default_rng(20)
    solutions = []
    for step in range(3):
        g = fbc("no_slip", "neumann", pressure_gradient_value=rng.uniform(-1.0, 1.0))
        bcs_step = BoundaryConditionSet(x_min=g, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)
        system.update_bcs(bcs_step)
        # matrix and factorization objects are byte-identical (never rebuilt)
        assert id(system.matrix) == matrix_id
        assert id(system._lu) == lu_id
        assert system.assembly_time == assembly_time  # not re-timed

        rhs = ScalarField.zeros(m)
        rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)
        sol, diag = system.solve(rhs)
        assert diag.converged
        solutions.append(sol.interior.copy())

    # different Neumann values genuinely changed the solution (not a no-op)
    assert np.max(np.abs(solutions[0] - solutions[1])) > 1e-8


def test_update_bcs_rejects_topology_change() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, neumann_bcs(), rhs_compatibility="mean_removal")
    with pytest.raises(PressureSystemError):
        system.update_bcs(dirichlet_bcs(0.0))


def test_solve_reports_independent_assembly_and_solve_times() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    rhs = ScalarField.zeros(m)
    rhs.interior = 1.0
    sol, diag = system.solve(rhs)
    assert diag.assembly_time >= 0.0
    assert diag.solve_time >= 0.0
    assert diag.assembly_time == system.assembly_time


def test_no_dense_matrix_allocated() -> None:
    """The matrix stays sparse even for solver='direct' (uses splu on CSC,
    not a dense factorization)."""
    m = refinement_mesh(16)  # 16*20*24 = 7680 unknowns; a dense matrix would be ~470 MB
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    assert sp.issparse(system.matrix)
    assert sp.issparse(system.laplacian_matrix)


# --------------------------------------------------------------------------
# Edge cases
# --------------------------------------------------------------------------

def test_zero_rhs_gives_zero_solution_dirichlet() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    rhs = ScalarField.zeros(m)
    sol, diag = system.solve(rhs)
    np.testing.assert_allclose(sol.interior, 0.0, atol=1e-10)


def test_constant_rhs_neumann_mean_removal() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, neumann_bcs(), rhs_compatibility="mean_removal", tol=1e-10)
    rhs = ScalarField.zeros(m)
    rhs.interior = 3.0  # incompatible constant; mean-removal makes it exactly zero after subtraction
    sol, diag = system.solve(rhs)
    assert diag.converged
    # rhs became exactly zero after mean removal -> zero-mean solution is exactly zero
    np.testing.assert_allclose(sol.interior, 0.0, atol=1e-8)


def test_max_iterations_failure_path() -> None:
    m = refinement_mesh(16)
    bcs = dirichlet_bcs(0.0)
    system = PressurePoissonSystem(m, bcs, solver="cg", tol=1e-14, max_iterations=2)
    rng = np.random.default_rng(9)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)
    sol, diag = system.solve(rhs)
    assert not diag.converged
    assert diag.iterations <= 2


def test_residual_tolerance_is_respected() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="cg", tol=1e-6, max_iterations=10000)
    rng = np.random.default_rng(10)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)
    sol, diag = system.solve(rhs)
    assert diag.converged
    assert diag.final_residual <= 1e-6 * max(1.0, diag.initial_residual)


def test_bc_change_requires_new_system() -> None:
    """There is no in-place BC-mutation API; changing BCs means constructing
    a new PressurePoissonSystem. This test documents that by construction
    (no setter exists) rather than by exception."""
    m = mesh(1)
    system = PressurePoissonSystem(m, neumann_bcs(), rhs_compatibility="mean_removal")
    assert not hasattr(system, "set_bcs")
    assert not hasattr(system, "rebuild")
    with pytest.raises(AttributeError):
        system.bcs = dirichlet_bcs(0.0)  # bcs is a read-only property


def test_direct_solver_rejected_with_zero_mean_null_space() -> None:
    m = mesh(1)
    with pytest.raises(PressureSystemError):
        PressurePoissonSystem(m, periodic_bcs(), solver="direct", null_space_strategy="zero_mean")


def test_invalid_pin_index_rejected() -> None:
    m = mesh(1)
    with pytest.raises(PressureSystemError):
        PressurePoissonSystem(m, periodic_bcs(), null_space_strategy="pin_cell", pin_index=(NX, 0, 0))


def test_unknown_preconditioner_rejected() -> None:
    m = mesh(1)
    with pytest.raises(PressureSystemError):
        PressurePoissonSystem(m, dirichlet_bcs(0.0), preconditioner="ilu")


def test_mesh_and_bcs_properties_readable() -> None:
    m = mesh(1)
    bcs = dirichlet_bcs(0.0)
    system = PressurePoissonSystem(m, bcs, solver="direct")
    assert system.mesh is m
    assert system.bcs is bcs


def test_solve_rejects_mismatched_shape_same_ghost_width() -> None:
    m1 = mesh(1)
    m2 = StructuredMesh3D(nx=NX + 1, ny=NY, nz=NZ, lx=2.0, ly=3.0, lz=5.0, n_ghost=1)
    system = PressurePoissonSystem(m1, dirichlet_bcs(0.0), solver="direct")
    rhs = ScalarField.zeros(m2)  # same n_ghost, different shape
    with pytest.raises(PressureSystemError):
        system.solve(rhs)


def test_solve_accepts_warm_start_x0() -> None:
    m = mesh(1)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="cg", tol=1e-10)
    rng = np.random.default_rng(13)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)
    sol_cold, diag_cold = system.solve(rhs)
    sol_warm, diag_warm = system.solve(rhs, x0=sol_cold)
    assert diag_warm.converged
    np.testing.assert_allclose(sol_warm.interior, sol_cold.interior, atol=1e-8)
    assert diag_warm.iterations <= diag_cold.iterations  # warm start from the exact solution: fast/immediate


def test_solve_rejects_mismatched_ghost_width() -> None:
    m1 = mesh(1)
    m2 = mesh(2)
    system = PressurePoissonSystem(m1, dirichlet_bcs(0.0), solver="direct")
    rhs = ScalarField.zeros(m2)
    with pytest.raises(PressureSystemError):
        system.solve(rhs)


@pytest.mark.parametrize("n_ghost", [1, 2])
def test_system_works_at_ng1_and_ng2(n_ghost: int) -> None:
    m = mesh(n_ghost)
    system = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    rng = np.random.default_rng(11)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)
    sol, diag = system.solve(rhs)
    assert diag.converged
    assert sol.n_ghost == n_ghost


def test_jacobi_preconditioner_runs_and_agrees_with_unpreconditioned() -> None:
    m = mesh(1)
    rng = np.random.default_rng(12)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)

    sys_plain = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="cg", tol=1e-12)
    sys_jacobi = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="cg", preconditioner="jacobi", tol=1e-12)
    p_plain, d_plain = sys_plain.solve(rhs)
    p_jacobi, d_jacobi = sys_jacobi.solve(rhs)
    assert d_plain.converged and d_jacobi.converged
    np.testing.assert_allclose(p_plain.interior, p_jacobi.interior, atol=1e-8)


@pytest.mark.parametrize("solver", ["bicgstab", "gmres"])
def test_bicgstab_and_gmres_solvers_agree_with_direct_reference(solver: str) -> None:
    """Milestone 7 Part A: pressure.py's matrix is always SPD, so CG is
    preferred, but BiCGSTAB/GMRES must also work correctly through the
    shared LinearSolver abstraction (general-purpose fallback methods)."""
    m = mesh(1)
    rng = np.random.default_rng(21)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)

    sys_direct = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver="direct")
    sys_iter = PressurePoissonSystem(m, dirichlet_bcs(0.0), solver=solver, tol=1e-12)
    p_direct, d_direct = sys_direct.solve(rhs)
    p_iter, d_iter = sys_iter.solve(rhs)
    assert d_direct.converged and d_iter.converged
    np.testing.assert_allclose(p_direct.interior, p_iter.interior, atol=1e-6)
