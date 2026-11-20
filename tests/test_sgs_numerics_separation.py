"""Unit tests for truncation residual analysis and kinetic energy budget decomposition."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.decaying_turbulence import generate_matched_solenoidal_fields
from navier3d.fields import ScalarField
from navier3d.mesh import StructuredMesh3D
from navier3d.sgs_apriori import compute_energy_budget, compute_truncation_residuals


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_truncation_residual_calculation() -> None:
    """Verify compute_truncation_residuals outputs finite ratios for fine vs coarse grids."""
    L = 2.0 * np.pi
    m_fine = StructuredMesh3D(nx=16, ny=16, nz=16, lx=L, ly=L, lz=L, n_ghost=1)
    m_coarse = StructuredMesh3D(nx=8, ny=8, nz=8, lx=L, ly=L, lz=L, n_ghost=1)
    b = periodic_bcs()

    vel_fine, _ = generate_matched_solenoidal_fields(m_fine, m_coarse, b, k_peak=2.0, E0=1.0, seed=42)

    res = compute_truncation_residuals(vel_fine, m_fine, m_coarse, b)

    assert "norm_f_num" in res
    assert "norm_f_sgs" in res
    assert "ratio_num_sgs" in res
    assert np.isfinite(res["ratio_num_sgs"])
    assert res["ratio_num_sgs"] >= 0.0


def test_energy_budget_calculation() -> None:
    """Verify compute_energy_budget calculates kinetic energy change and inferred numerical viscosity."""
    L = 2.0 * np.pi
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=L, ly=L, lz=L, n_ghost=1)
    b = periodic_bcs()

    v_n, _ = generate_matched_solenoidal_fields(m, m, b, k_peak=2.0, E0=1.0, seed=42)
    v_np1, _ = generate_matched_solenoidal_fields(m, m, b, k_peak=2.0, E0=0.99, seed=43)

    nu_t = ScalarField.zeros(m)
    nu_t.interior[:] = 0.001

    budget = compute_energy_budget(v_n, v_np1, dt=1e-3, mesh=m, bcs=b, nu=0.002, nu_t=nu_t)

    assert "delta_K" in budget
    assert "delta_K_visc" in budget
    assert "delta_K_sgs" in budget
    assert "nu_num" in budget
    assert np.isfinite(budget["nu_num"])
