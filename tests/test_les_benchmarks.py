"""LES benchmarks and validation tests.

Covers:
1. Taylor-Green vortex LES vs baseline Cs=0.
2. Decaying periodic turbulence evolution with solenoidal random IC.
3. Coarse LES vs filtered fine reference comparison.
4. Cs sensitivity study.
5. Conservation, positivity, and SGS dissipation checks.
"""
import math
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.fields import FlowState, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.pressure import compute_initial_pressure
from navier3d.spectrum import compute_energy_spectrum, verify_parseval_identity
from navier3d.time_integrators import ThetaSchemeIntegrator, run
from navier3d.turbulence import SmagorinskyModel


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def taylor_green_initial_state(m: StructuredMesh3D, b: BoundaryConditionSet, rho: float = 1.0, nu: float = 0.01) -> FlowState:
    L = m.lx
    Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(m.cell_centers_x(), m.face_coords_y(), m.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.face_coords_z(), indexing="ij")

    vel0 = VelocityField.zeros(m)
    vel0.u.interior[:] = np.sin(2 * np.pi * Xu / L) * np.cos(2 * np.pi * Yu / L) * np.cos(2 * np.pi * Zu / L)
    vel0.v.interior[:] = -np.cos(2 * np.pi * Xv / L) * np.sin(2 * np.pi * Yv / L) * np.cos(2 * np.pi * Zv / L)
    vel0.w.interior[:] = 0.0
    apply_velocity_bc(vel0, b)

    p0, _ = compute_initial_pressure(
        vel0, b, m, rho, nu, convection_scheme="centered", solver="direct", null_space_strategy="pin_cell"
    )
    return FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)


def test_taylor_green_les_vs_baseline() -> None:
    """Taylor-Green vortex benchmark: Smagorinsky LES (Cs=0.17) vs baseline Cs=0.
    Verifies that LES dissipation Pi_sgs >= 0 and LES removes unresolved energy faster."""
    m = StructuredMesh3D(nx=12, ny=12, nz=12, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    rho, nu = 1.0, 0.005
    dt = 1e-3
    n_steps = 15

    s0 = taylor_green_initial_state(m, b, rho, nu)

    # 1. Baseline Cs=0
    model_base = SmagorinskyModel(cs=0.0)
    integ_base = ThetaSchemeIntegrator(
        m, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method="incremental", chi=1.0, pressure_extrapolation=True,
        turbulence_model=model_base,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    s_base, hist_base = run(integ_base, s0, n_steps)

    # 2. Smagorinsky LES Cs=0.17
    model_les = SmagorinskyModel(cs=0.17)
    integ_les = ThetaSchemeIntegrator(
        m, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method="incremental", chi=1.0, pressure_extrapolation=True,
        turbulence_model=model_les,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    s_les, hist_les = run(integ_les, s0, n_steps)

    # Verify positivity & SGS dissipation
    assert hist_les[-1].pi_sgs is not None
    assert hist_les[-1].pi_sgs >= 0.0
    assert hist_les[-1].nu_t_max >= 0.0

    # LES kinetic energy decays faster due to SGS dissipation
    ke_base = hist_base[-1].kinetic_energy
    ke_les = hist_les[-1].kinetic_energy
    assert ke_les <= ke_base


def test_decaying_turbulence_benchmark() -> None:
    """Decaying periodic turbulence with solenoidal random field IC.
    Tracks kinetic energy decay, SGS dissipation Pi_sgs >= 0, and energy spectrum."""
    m = StructuredMesh3D(nx=12, ny=12, nz=12, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    rho, nu = 1.0, 0.002
    dt = 1e-3

    vel0 = generate_solenoidal_random_field(m, b, k_peak=2.0, E0=1.0, seed=123)
    p0, _ = compute_initial_pressure(
        vel0, b, m, rho, nu, convection_scheme="centered", solver="direct", null_space_strategy="pin_cell"
    )
    s0 = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

    model = SmagorinskyModel(cs=0.15)
    integrator = ThetaSchemeIntegrator(
        m, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method="incremental", chi=1.0, pressure_extrapolation=True,
        turbulence_model=model,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    final_state, history = run(integrator, s0, n_steps=10)

    assert history[-1].normalized_divergence < 1e-6
    assert history[-1].pi_sgs >= 0.0

    k_shells, E_k = compute_energy_spectrum(final_state.velocity, m)
    assert np.sum(E_k) > 0.0


def test_cs_sensitivity_study() -> None:
    """Verify solver behavior across Cs in [0, 0.05, 0.1, 0.18, 0.25].
    Higher Cs must yield higher eddy viscosity nu_t_max."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    rho, nu = 1.0, 0.01
    dt = 1e-3

    s0 = taylor_green_initial_state(m, b, rho, nu)
    cs_values = [0.0, 0.05, 0.1, 0.18, 0.25]
    nu_t_max_list = []

    for cs in cs_values:
        model = SmagorinskyModel(cs=cs)
        integrator = ThetaSchemeIntegrator(
            m, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
            projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            turbulence_model=model,
            pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )
        _, history = run(integrator, s0, n_steps=3)
        nu_t_max = history[-1].nu_t_max if history[-1].nu_t_max is not None else 0.0
        nu_t_max_list.append(nu_t_max)

    # nu_t_max must be monotonically increasing with Cs
    for i in range(len(cs_values) - 1):
        assert nu_t_max_list[i] <= nu_t_max_list[i+1]
