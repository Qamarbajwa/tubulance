"""Unit tests for discrete SGS energy work-dissipation identity W_sgs == -Pi_sgs <= 0."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.fields import ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.strain import compute_strain_magnitude
from navier3d.turbulence import SmagorinskyModel, compute_sgs_mechanical_work


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_sgs_mechanical_work_equals_negative_dissipation() -> None:
    """Verify discrete MAC identity W_sgs = <u, div tau_sgs>_MAC == -Pi_sgs <= 0 on periodic domain."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()

    vel = generate_solenoidal_random_field(m, b, k_peak=2.0, E0=1.0, seed=42)
    model = SmagorinskyModel(cs=0.17)
    nu_t = model.eddy_viscosity(vel, m, b)

    W_sgs, Pi_sgs, rel_err = compute_sgs_mechanical_work(vel, nu_t, m, b)

    # Mechanical work must be negative (dissipative)
    assert W_sgs <= 0.0
    assert Pi_sgs >= 0.0
    assert rel_err < 1e-10, f"Mechanical work W_sgs ({W_sgs:.6e}) vs -Pi_sgs ({-Pi_sgs:.6e}) relative error {rel_err:.4e}"
