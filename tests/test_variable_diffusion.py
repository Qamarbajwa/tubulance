"""Unit tests for variable-viscosity stress divergence operator and linear solver."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.fields import ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import velocity_laplacian
from navier3d.variable_diffusion import VariableDiffusionSystem, variable_viscosity_stress_divergence


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_constant_viscosity_equivalence_with_laplacian() -> None:
    """For spatially uniform nu_eff = nu_c, variable_viscosity_stress_divergence
    must equal nu_c * velocity_laplacian(u) to machine precision for solenoidal fields."""
    m = StructuredMesh3D(nx=12, ny=12, nz=12, lx=1.0, ly=1.2, lz=1.1, n_ghost=1)
    b = periodic_bcs()

    Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(m.cell_centers_x(), m.face_coords_y(), m.cell_centers_z(), indexing="ij")

    from navier3d.projection import project_initial_velocity

    vel = VelocityField.zeros(m)
    vel.u.interior[:] = np.sin(2 * np.pi * Xu) * np.cos(2 * np.pi * Yu / 1.2)
    vel.v.interior[:] = -np.cos(2 * np.pi * Xv) * np.sin(2 * np.pi * Yv / 1.2)
    vel.w.interior[:] = 0.0
    apply_velocity_bc(vel, b)
    vel = project_initial_velocity(vel, b, m)

    nu_c = 0.05
    nu_eff = ScalarField.zeros(m)
    nu_eff.interior[:] = nu_c

    div_tau = variable_viscosity_stress_divergence(vel, nu_eff, m, b)
    lap_u = velocity_laplacian(vel, m)

    # Compare div_tau against nu_c * lap_u
    diff_u = float(np.max(np.abs(div_tau.u.interior - nu_c * lap_u.u.interior)))
    diff_v = float(np.max(np.abs(div_tau.v.interior - nu_c * lap_u.v.interior)))

    assert diff_u < 1e-12, f"u diff {diff_u}"
    assert diff_v < 1e-12, f"v diff {diff_v}"


def test_variable_diffusion_system_solve() -> None:
    """Verify that VariableDiffusionSystem solves [I - theta*dt*div(2 nu_eff S)] u* = rhs."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)
    b = periodic_bcs()

    vel = VelocityField.zeros(m)
    vel.u.interior[:] = np.sin(2 * np.pi * m.face_coords_x()[:, None, None])
    apply_velocity_bc(vel, b)

    nu_eff = ScalarField.zeros(m)
    nu_eff.interior[:] = 0.01 + 0.02 * np.random.uniform(0.0, 1.0, (m.nx, m.ny, m.nz))

    dt = 1e-3
    theta = 0.5
    system = VariableDiffusionSystem(m, b, dt, theta, nu_eff)

    # Apply operator to vel to get rhs
    rhs = system.apply(vel)

    # Solve system for rhs
    sol, info = system.solve(rhs)

    diff_u = float(np.max(np.abs(sol.u.interior - vel.u.interior)))
    assert diff_u < 1e-6, f"Variable diffusion solve error: {diff_u}"
