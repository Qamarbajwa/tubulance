"""Milestone 7 Part B: optional PyAMG backend for the pressure Poisson
system.

Skipped entirely if pyamg is not installed (``pip install -e ".[amg]"``).
Verifies AMG-preconditioned CG does not alter the mathematical solution
relative to the existing (no-preconditioner / Jacobi) reference paths --
and, per the review's explicit emphasis, checks the **corrected
velocity** after a full projection, not merely the raw pressure field
(a pressure offset is physically irrelevant on its own).
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
from navier3d.fields import ScalarField, VelocityField
from navier3d.linear_solvers import HAS_PYAMG
from navier3d.mesh import StructuredMesh3D
from navier3d.pressure import PressurePoissonSystem
from navier3d.projection import project

pytestmark = pytest.mark.skipif(not HAS_PYAMG, reason="pyamg not installed")

NX, NY, NZ = 10, 12, 14
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


def dirichlet_bcs(value: float = 0.0) -> BoundaryConditionSet:
    d = fbc("pressure_outlet", "dirichlet", pressure_value=value)
    return BoundaryConditionSet(x_min=d, x_max=d, y_min=d, y_max=d, z_min=d, z_max=d)


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def _rel_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + EPS))


# --------------------------------------------------------------------------
# Raw pressure comparison (offset-normalized, as the review's formula asks)
# --------------------------------------------------------------------------

def test_amg_pressure_matches_reference_after_offset_normalization() -> None:
    m = mesh(1)
    bcs = dirichlet_bcs(0.0)
    rng = np.random.default_rng(1)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)

    ref = PressurePoissonSystem(m, bcs, solver="cg", tol=1e-12)
    amg = PressurePoissonSystem(m, bcs, solver="cg", preconditioner="amg", tol=1e-12)
    p_ref, d_ref = ref.solve(rhs)
    p_amg, d_amg = amg.solve(rhs)
    assert d_ref.converged and d_amg.converged

    # dirichlet system is nonsingular -- no offset ambiguity at all here,
    # but normalize anyway per the review's formula for generality
    p_ref_n = p_ref.interior - np.mean(p_ref.interior)
    p_amg_n = p_amg.interior - np.mean(p_amg.interior)
    rel_err = _rel_l2(p_amg_n, p_ref_n)
    assert rel_err < 1e-6


def test_amg_pressure_matches_reference_singular_periodic_system() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    rng = np.random.default_rng(2)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)

    ref = PressurePoissonSystem(m, bcs, solver="cg", rhs_compatibility="mean_removal", tol=1e-12)
    amg = PressurePoissonSystem(m, bcs, solver="cg", preconditioner="amg", rhs_compatibility="mean_removal", tol=1e-12)
    p_ref, d_ref = ref.solve(rhs)
    p_amg, d_amg = amg.solve(rhs)
    assert d_ref.converged and d_amg.converged

    p_ref_n = p_ref.interior - np.mean(p_ref.interior)
    p_amg_n = p_amg.interior - np.mean(p_amg.interior)
    assert _rel_l2(p_amg_n, p_ref_n) < 1e-6


# --------------------------------------------------------------------------
# Corrected velocity comparison (the more important check per the review)
# --------------------------------------------------------------------------

def test_amg_corrected_velocity_matches_reference_after_projection() -> None:
    """The pressure OFFSET is physically irrelevant; what actually matters
    is that the corrected velocity (which depends only on grad(p), not p
    itself) agrees between AMG-preconditioned and reference pressure
    solves."""
    m = mesh(1)
    bcs = periodic_bcs()
    rng = np.random.default_rng(3)
    u_star = VelocityField.zeros(m)
    for comp in u_star.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(u_star, bcs)

    result_ref = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="cg", rhs_compatibility="mean_removal", tol=1e-12)
    result_amg = project(u_star, bcs, m, rho=1.0, dt=0.01, solver="cg", preconditioner="amg", rhs_compatibility="mean_removal", tol=1e-12)

    assert result_ref.pressure_diagnostics.converged
    assert result_amg.pressure_diagnostics.converged
    assert result_ref.max_divergence_after < 1e-8
    assert result_amg.max_divergence_after < 1e-8

    for comp_ref, comp_amg in zip(result_ref.velocity.components(), result_amg.velocity.components()):
        rel_err = _rel_l2(comp_amg.interior, comp_ref.interior)
        assert rel_err < 1e-6, f"velocity component mismatch: {rel_err}"


# --------------------------------------------------------------------------
# AMG does not require the null-space handling to change
# --------------------------------------------------------------------------

def test_amg_with_pin_cell_null_space_strategy() -> None:
    m = mesh(1)
    bcs = periodic_bcs()
    rng = np.random.default_rng(4)
    rhs = ScalarField.zeros(m)
    rhs.interior = rng.uniform(-1.0, 1.0, size=rhs.interior.shape)

    system = PressurePoissonSystem(m, bcs, solver="cg", preconditioner="amg", null_space_strategy="pin_cell", tol=1e-12)
    p, diag = system.solve(rhs)
    assert diag.converged
    assert diag.preconditioner_time >= 0.0
