"""Milestone 7 Part C: SPD-reduced diffusion formulation vs. the original
pinned-row formulation.

Verifies mathematical equivalence (same PDE, same BCs, same
discretization -- only the boundary-DOF elimination strategy differs)
across every velocity BC type this project supports, using the review's
required relative-L2-error metric:
``|u_iter - u_direct|_2 / (|u_direct|_2 + eps)``.
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
from navier3d.diffusion import DiffusionSystemError, VelocityDiffusionSystem
from navier3d.fields import FaceField, VelocityField
from navier3d.linear_solvers import HAS_PYAMG
from navier3d.mesh import StructuredMesh3D

NX, NY, NZ = 5, 6, 7
EPS = 1e-12


def mesh(n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=n_ghost)


def fbc(velocity, pressure="neumann", velocity_value=None, pressure_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
    )


def wall_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def channel_bcs() -> BoundaryConditionSet:
    inlet = fbc("velocity_inlet", velocity_value=(1.5, 0.2, -0.3))
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=inlet, x_max=outlet, y_min=w, y_max=w, z_min=w, z_max=w)


def free_slip_bcs() -> BoundaryConditionSet:
    f = fbc("free_slip")
    return BoundaryConditionSet(x_min=f, x_max=f, y_min=f, y_max=f, z_min=f, z_max=f)


def reverse_channel_bcs() -> BoundaryConditionSet:
    """Same as channel_bcs but with outlet/inlet swapped -- exercises the
    LO-side pressure_outlet elimination branch of
    _normal_matrix_reduced, which channel_bcs (outlet on HI only) never
    reaches."""
    outlet = fbc("pressure_outlet", "dirichlet", pressure_value=0.0)
    inlet = fbc("velocity_inlet", velocity_value=(1.5, 0.2, -0.3))
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=outlet, x_max=inlet, y_min=w, y_max=w, z_min=w, z_max=w)


def random_full_velocity(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> VelocityField:
    rng = np.random.default_rng(seed)
    velocity = VelocityField.zeros(m)
    for comp in velocity.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(velocity, bcs)
    return velocity


def _rel_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + EPS))


# --------------------------------------------------------------------------
# Matrix structure: spd formulation really is symmetric
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bcs_factory", [wall_bcs, periodic_bcs, channel_bcs, free_slip_bcs])
@pytest.mark.parametrize("axis", [0, 1, 2])
def test_spd_matrix_is_symmetric(bcs_factory, axis: int) -> None:
    m = mesh(1)
    system = VelocityDiffusionSystem(m, bcs_factory(), axis, nu=0.2, dt=0.02, theta=0.5, formulation="spd")
    diff = (system.matrix - system.matrix.T)
    assert np.max(np.abs(diff.toarray())) < 1e-12


def test_pinned_matrix_is_not_symmetric_for_dirichlet_like_bcs() -> None:
    """Sanity check that the comparison above is meaningful: the ORIGINAL
    formulation genuinely is asymmetric for a non-periodic axis (proving
    the "spd" formulation is a real change, not a no-op)."""
    m = mesh(1)
    system = VelocityDiffusionSystem(m, wall_bcs(), 0, nu=0.2, dt=0.02, theta=0.5, formulation="pinned")
    diff = (system.matrix - system.matrix.T)
    assert np.max(np.abs(diff.toarray())) > 1e-6


# --------------------------------------------------------------------------
# CG rejected on pinned (general) matrix; allowed on spd
# --------------------------------------------------------------------------

def test_cg_rejected_on_pinned_formulation() -> None:
    m = mesh(1)
    with pytest.raises(DiffusionSystemError):
        VelocityDiffusionSystem(m, wall_bcs(), 0, nu=0.1, dt=0.01, theta=1.0, formulation="pinned", solver="cg")


def test_cg_default_and_accepted_on_spd_formulation() -> None:
    m = mesh(1)
    system = VelocityDiffusionSystem(m, wall_bcs(), 0, nu=0.1, dt=0.01, theta=1.0, formulation="spd")
    assert system._linear_solver.method.value == "cg"


# --------------------------------------------------------------------------
# Equivalence: spd/cg vs pinned/direct, across BC types and all 3 components
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bcs_factory", [wall_bcs, periodic_bcs, channel_bcs, reverse_channel_bcs, free_slip_bcs])
@pytest.mark.parametrize("axis", [0, 1, 2])
def test_spd_cg_matches_pinned_direct(bcs_factory, axis: int) -> None:
    m = mesh(1)
    bcs = bcs_factory()
    u_n = random_full_velocity(m, bcs, seed=42 + axis).components()[axis]

    direct_system = VelocityDiffusionSystem(m, bcs, axis, nu=0.15, dt=0.02, theta=0.5, formulation="pinned", solver="direct")
    spd_system = VelocityDiffusionSystem(m, bcs, axis, nu=0.15, dt=0.02, theta=0.5, formulation="spd", solver="cg", rtol=1e-12)

    u_direct, diag_direct = direct_system.solve(u_n)
    u_spd, diag_spd = spd_system.solve(u_n)

    assert diag_direct.converged and diag_spd.converged
    rel_err = _rel_l2(u_spd.interior, u_direct.interior)
    assert rel_err < 1e-8, f"bcs={bcs_factory.__name__} axis={axis}: relative L2 error {rel_err}"


@pytest.mark.parametrize("bcs_factory", [wall_bcs, channel_bcs])
def test_spd_bicgstab_matches_pinned_direct(bcs_factory) -> None:
    """Also check the general-matrix bicgstab/gmres fallback path (still
    on the ORIGINAL pinned formulation, matrix_kind='general') agrees
    with the direct reference -- the review's "otherwise use GMRES or
    BiCGSTAB" option, independent of the spd reformulation."""
    m = mesh(1)
    bcs = bcs_factory()
    u_n = random_full_velocity(m, bcs, seed=99).components()[0]

    direct_system = VelocityDiffusionSystem(m, bcs, 0, nu=0.2, dt=0.02, theta=1.0, formulation="pinned", solver="direct")
    iter_system = VelocityDiffusionSystem(m, bcs, 0, nu=0.2, dt=0.02, theta=1.0, formulation="pinned", solver="bicgstab", rtol=1e-12)

    u_direct, diag_direct = direct_system.solve(u_n)
    u_iter, diag_iter = iter_system.solve(u_n)
    assert diag_direct.converged and diag_iter.converged
    assert _rel_l2(u_iter.interior, u_direct.interior) < 1e-8


# --------------------------------------------------------------------------
# Warm starts for the SPD/iterative path (Part D)
# --------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_PYAMG, reason="pyamg not installed")
def test_spd_amg_preconditioner_matches_direct_reference() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    u_n = random_full_velocity(m, bcs, seed=77).components()[0]

    direct_system = VelocityDiffusionSystem(m, bcs, 0, nu=0.15, dt=0.02, theta=0.5, formulation="pinned", solver="direct")
    amg_system = VelocityDiffusionSystem(m, bcs, 0, nu=0.15, dt=0.02, theta=0.5, formulation="spd", solver="cg", preconditioner="amg", rtol=1e-12)

    u_direct, diag_direct = direct_system.solve(u_n)
    u_amg, diag_amg = amg_system.solve(u_n)
    assert diag_direct.converged and diag_amg.converged
    assert _rel_l2(u_amg.interior, u_direct.interior) < 1e-6


def test_spd_warm_start_reduces_iterations() -> None:
    m = mesh(1)
    bcs = wall_bcs()
    system = VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=0.5, formulation="spd", solver="cg", rtol=1e-10)
    u_n = random_full_velocity(m, bcs, seed=5).components()[0]

    u_cold, diag_cold = system.solve(u_n)
    u_warm, diag_warm = system.solve(u_n, x0=u_cold)
    assert diag_warm.converged
    np.testing.assert_allclose(u_warm.interior, u_cold.interior, atol=1e-8)
    assert diag_warm.iterations <= diag_cold.iterations
