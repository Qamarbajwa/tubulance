"""Unit tests for A-priori SGS stress extraction and diagnostic functions."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.decaying_turbulence import generate_matched_solenoidal_fields
from navier3d.mesh import StructuredMesh3D
from navier3d.sgs_apriori import compute_exact_sgs_stress, compute_sgs_apriori_diagnostics
from navier3d.turbulence import SmagorinskyModel


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_exact_sgs_stress_extraction_and_apriori_diagnostics() -> None:
    """Verify that compute_exact_sgs_stress and compute_sgs_apriori_diagnostics run cleanly and return finite values."""
    L = 2.0 * np.pi
    m_fine = StructuredMesh3D(nx=16, ny=16, nz=16, lx=L, ly=L, lz=L, n_ghost=1)
    m_coarse = StructuredMesh3D(nx=8, ny=8, nz=8, lx=L, ly=L, lz=L, n_ghost=1)
    b = periodic_bcs()

    vel_fine, vel_coarse = generate_matched_solenoidal_fields(m_fine, m_coarse, b, k_peak=2.0, E0=1.0, seed=42)

    tau_exact = compute_exact_sgs_stress(vel_fine, m_fine, m_coarse, b)

    assert "dev_xx" in tau_exact
    assert tau_exact["dev_xx"].shape == (8, 8, 8)

    model = SmagorinskyModel(cs=0.17)
    nu_t = model.eddy_viscosity(vel_coarse, m_coarse, b)

    diag = compute_sgs_apriori_diagnostics(tau_exact, vel_coarse, nu_t, m_coarse, b)

    assert "rho_Pi" in diag
    assert "rho_tau" in diag
    assert "c_d_opt" in diag
    assert "c_s_opt" in diag
    assert np.isfinite(diag["c_d_opt"])
    assert diag["c_s_opt"] >= 0.0
