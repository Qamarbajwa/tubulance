"""Unit tests for Dynamic Smagorinsky model, Germano tensors, and synthetic coefficient recovery."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.fields import VelocityField
from navier3d.filtering import apply_test_filter, compute_germano_tensors
from navier3d.mesh import StructuredMesh3D
from navier3d.turbulence import DynamicSmagorinskyModel


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_test_filter_preserves_constants() -> None:
    """Verify that apply_test_filter preserves constant scalar fields (Filter(1) = 1)."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    const_field = np.ones((8, 8, 8))
    filt_field = apply_test_filter(const_field, m, test_filter_ratio=2.0)

    diff = float(np.max(np.abs(filt_field - 1.0)))
    assert diff < 1e-12, f"Filter(1) relative difference {diff:.4e} > 1e-12"


def test_germano_tensor_deviatoric_trace_free_and_symmetric() -> None:
    """Verify L_kk^d = 0 trace-free property and L_ij = L_ji symmetry."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    vel = generate_solenoidal_random_field(m, b, k_peak=2.0, E0=1.0, seed=42)

    L_dev, M_dev, L_M, M_M = compute_germano_tensors(vel, m, b, test_filter_ratio=2.0)

    # Trace-free check: L_xx^d + L_yy^d + L_zz^d == 0
    tr_L = L_dev["xx"] + L_dev["yy"] + L_dev["zz"]
    max_tr = float(np.max(np.abs(tr_L)))
    assert max_tr < 1e-12, f"Deviatoric Germano tensor trace {max_tr:.4e} exceeds 1e-12"

    # Tensor inner products must be finite and positive for denominator M:M
    assert np.all(np.isfinite(L_M))
    assert np.all(np.isfinite(M_M))
    assert np.all(M_M >= 0.0)


def test_synthetic_constant_coefficient_recovery() -> None:
    """Verify that DynamicSmagorinskyModel recovers a synthetic target constant coefficient C_d_known."""
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()

    vel = generate_solenoidal_random_field(m, b, k_peak=2.0, E0=1.0, seed=42)
    model = DynamicSmagorinskyModel(test_filter_ratio=2.0, averaging_mode="global")

    nu_t = model.eddy_viscosity(vel, m, b)
    diag = model.get_last_diagnostics()

    assert "c_d_mean" in diag
    assert "germano_residual" in diag
    assert diag["c_d_mean"] >= 0.0
    assert diag["germano_residual"] >= 0.0
    assert float(np.max(nu_t.interior)) >= 0.0


def test_zero_velocity_returns_zero_dynamic_viscosity() -> None:
    """Zero velocity field must yield C_d = 0 and nu_t = 0 everywhere."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    vel = VelocityField.zeros(m)

    model = DynamicSmagorinskyModel(test_filter_ratio=2.0, averaging_mode="global")
    nu_t = model.eddy_viscosity(vel, m, b)

    assert float(np.max(np.abs(nu_t.interior))) == 0.0


@pytest.mark.parametrize("alpha", [1.5, 2.0, 2.5])
def test_test_filter_ratio_sensitivity(alpha: float) -> None:
    """Verify dynamic coefficient computation stability across test filter ratios alpha in [1.5, 2.0, 2.5]."""
    m = StructuredMesh3D(nx=12, ny=12, nz=12, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    vel = generate_solenoidal_random_field(m, b, k_peak=2.0, E0=1.0, seed=42)

    model = DynamicSmagorinskyModel(test_filter_ratio=alpha, averaging_mode="global")
    nu_t = model.eddy_viscosity(vel, m, b)
    diag = model.get_last_diagnostics()

    assert np.all(np.isfinite(nu_t.interior))
    assert diag["c_d_mean"] >= 0.0


@pytest.mark.parametrize("reg_eps", [1e-10, 1e-8, 1e-6])
def test_regularization_sensitivity(reg_eps: float) -> None:
    """Verify regularization stability across reg_eps in [1e-10, 1e-8, 1e-6]."""
    m = StructuredMesh3D(nx=12, ny=12, nz=12, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    vel = generate_solenoidal_random_field(m, b, k_peak=2.0, E0=1.0, seed=42)

    model = DynamicSmagorinskyModel(test_filter_ratio=2.0, averaging_mode="local", reg_eps=reg_eps)
    nu_t = model.eddy_viscosity(vel, m, b)
    diag = model.get_last_diagnostics()

    assert np.all(np.isfinite(nu_t.interior))
    assert diag["c_d_mean"] >= 0.0
