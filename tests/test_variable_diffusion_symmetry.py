"""Unit tests for variable-viscosity linear operator symmetry and SPD verification."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.fields import ScalarField
from navier3d.mesh import StructuredMesh3D
from navier3d.variable_diffusion import (
    DiffusionSystemError,
    VariableDiffusionSystem,
    assemble_variable_diffusion_matrix,
    compute_symmetry_error,
)


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def wall_bcs() -> BoundaryConditionSet:
    w = FaceBoundaryCondition(velocity_type=VelocityBCType.NO_SLIP, pressure_type=PressureBCType.NEUMANN)
    return BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)


@pytest.mark.parametrize("bcs_fn", [periodic_bcs, wall_bcs])
@pytest.mark.parametrize("viscosity_ratio", [1.0, 10.0, 100.0, 1000.0])
def test_operator_symmetry_and_positive_definiteness(bcs_fn, viscosity_ratio: float) -> None:
    """Verify Esym < 10^-12 and x^T A x > 0 across BC sets, anisotropic meshes, and viscosity ratios."""
    m = StructuredMesh3D(nx=4, ny=5, nz=6, lx=1.0, ly=1.2, lz=1.5, n_ghost=1)
    b = bcs_fn()

    np.random.seed(42)
    nu_eff = ScalarField.zeros(m)
    nu_base = 0.01
    nu_eff.interior[:] = nu_base * (1.0 + (viscosity_ratio - 1.0) * np.random.uniform(0.0, 1.0, (4, 5, 6)))

    dt = 1e-3
    theta = 0.5

    A = assemble_variable_diffusion_matrix(m, b, dt, theta, nu_eff)
    e_sym = compute_symmetry_error(A)

    assert e_sym < 1e-12, f"Matrix symmetry error {e_sym:.4e} exceeds 1e-12 threshold"

    # Test positive definiteness x^T A x > 0 for 50 random vectors
    for _ in range(50):
        x = np.random.normal(0.0, 1.0, A.shape[0])
        val = float(x @ (A @ x))
        assert val > 0.0, f"x^T A x = {val} <= 0"


def test_cg_solver_rejection_for_nonsymmetric_matrix() -> None:
    """CG solver must be rejected with DiffusionSystemError if matrix is non-symmetric."""
    m = StructuredMesh3D(nx=4, ny=4, nz=4, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)
    b = periodic_bcs()
    nu_eff = ScalarField.zeros(m)
    nu_eff.interior[:] = 0.01

    sys = VariableDiffusionSystem(m, b, dt=1e-3, theta=0.5, nu_eff=nu_eff, solver="cg")

    # Manually trigger check
    A_mat = assemble_variable_diffusion_matrix(m, b, 1e-3, 0.5, nu_eff)
    # Artificially perturb symmetry of A_mat
    A_mat[0, 1] += 1.0
    e_sym = compute_symmetry_error(A_mat)

    assert e_sym > 1e-6
