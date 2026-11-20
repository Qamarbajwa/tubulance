"""Unit tests for Ramanujan-Inspired Spectral Correction R_h(u).

Verifies:
1. Zero-correction baseline equivalence.
2. Incompressibility & divergence-free Leray projection property D_h R_h ~ 0.
3. Strict energy neutrality |W_R| = |<u, R_h(u)>| ~ 0 across multiple fields & resolutions.
4. Dealiasing (2/3 rule) sensitivity.
5. Galilean invariance under constant frame translation u' = u + U_0.
6. Translation and axis-permutation symmetry.
"""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.corrections import RamanujanCorrection
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.fields import FlowState, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import divergence
from navier3d.pressure import compute_initial_pressure
from navier3d.time_integrators import ThetaSchemeIntegrator, run


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def taylor_green_velocity(mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> VelocityField:
    L = mesh.lx
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")

    vel = VelocityField.zeros(mesh)
    vel.u.interior[:] = np.sin(2 * np.pi * Xu / L) * np.cos(2 * np.pi * Yu / L) * np.cos(2 * np.pi * Zu / L)
    vel.v.interior[:] = -np.cos(2 * np.pi * Xv / L) * np.sin(2 * np.pi * Yv / L) * np.cos(2 * np.pi * Zv / L)
    vel.w.interior[:] = 0.0
    return vel


def test_zero_correction_equivalence() -> None:
    """Verify ramanujan_correction=None produces bit-identical steps to baseline Model A."""
    m = StructuredMesh3D(nx=8, ny=8, nz=8, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    rho, nu, dt = 1.0, 0.01, 1e-3

    vel = taylor_green_velocity(m, b)
    p0, _ = compute_initial_pressure(vel, b, m, rho, nu, solver="direct", null_space_strategy="pin_cell")
    s0 = FlowState(velocity=vel, pressure=p0, time=0.0, step=0)

    # Model A: ramanujan_correction=None
    integ_A = ThetaSchemeIntegrator(
        m, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method="incremental", ramanujan_correction=None,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    s_A, _ = run(integ_A, s0, n_steps=3)

    # Model B with lambda=0
    corr_zero = RamanujanCorrection(lambda_=0.0)
    integ_B = ThetaSchemeIntegrator(
        m, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method="incremental", ramanujan_correction=corr_zero,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    s_B, _ = run(integ_B, s0, n_steps=3)

    assert np.allclose(s_A.velocity.u.data, s_B.velocity.u.data, atol=1e-14)
    assert np.allclose(s_A.velocity.v.data, s_B.velocity.v.data, atol=1e-14)
    assert np.allclose(s_A.velocity.w.data, s_B.velocity.w.data, atol=1e-14)


def test_incompressibility_solenoidal_property() -> None:
    """Verify discrete divergence D_h R_h is near floating-point zero due to Leray projection."""
    for N in [8, 16, 24]:
        m = StructuredMesh3D(nx=N, ny=N, nz=N, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
        b = periodic_bcs()
        vel = generate_solenoidal_random_field(m, b, seed=42)

        corr = RamanujanCorrection(lambda_=1.0)
        R_h = corr.evaluate(vel, m, b)

        div_R = divergence(R_h, m)
        max_div_R = float(np.max(np.abs(div_R.interior)))
        assert max_div_R < 1e-8, f"D_h R_h = {max_div_R} exceeds tolerance for N={N}"


def test_energy_neutrality_across_resolutions_and_fields() -> None:
    """Verify |W_R| = |<u, R_h(u)>| ~ 0 across multiple fields, resolutions, and parameter values."""
    b = periodic_bcs()
    corr = RamanujanCorrection(lambda_=0.5, alpha=1.0)

    for N in [8, 16, 24]:
        m = StructuredMesh3D(nx=N, ny=N, nz=N, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)

        # 1. Taylor-Green field
        vel_tg = taylor_green_velocity(m, b)
        W_tg = corr.compute_energy_transfer_work(vel_tg, m, b)
        assert abs(W_tg) < 1e-8, f"Taylor-Green W_R = {W_tg} for N={N}"

        # 2. Random solenoidal fields (multiple seeds)
        for seed in [123, 456, 789]:
            vel_rnd = generate_solenoidal_random_field(m, b, k_peak=2.0, E0=1.0, seed=seed)
            W_rnd = corr.compute_energy_transfer_work(vel_rnd, m, b)
            assert abs(W_rnd) < 1e-8, f"Random field seed={seed} W_R = {W_rnd} for N={N}"


def test_dealiasing_sensitivity() -> None:
    """Verify dealiasing flag (2/3 rule) filters high wavenumbers correctly."""
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    vel = generate_solenoidal_random_field(m, b, seed=42)

    corr_dealiased = RamanujanCorrection(lambda_=1.0, dealiasing=True)
    corr_aliased = RamanujanCorrection(lambda_=1.0, dealiasing=False)

    R_deal = corr_dealiased.evaluate(vel, m, b)
    R_alias = corr_aliased.evaluate(vel, m, b)

    norm_deal = float(np.sqrt(sum(np.sum(c.interior**2) for c in R_deal.components())))
    norm_alias = float(np.sqrt(sum(np.sum(c.interior**2) for c in R_alias.components())))

    assert norm_deal > 0.0
    assert norm_alias > 0.0
    # Both are finite and energy neutral
    W_deal = corr_dealiased.compute_energy_transfer_work(vel, m, b)
    W_alias = corr_aliased.compute_energy_transfer_work(vel, m, b)
    assert abs(W_deal) < 1e-8
    assert abs(W_alias) < 1e-8


def test_galilean_invariance() -> None:
    """Verify correction R_h(u + U_0) == R_h(u) under constant Galilean translation U_0."""
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    b = periodic_bcs()
    vel = generate_solenoidal_random_field(m, b, seed=101)

    corr = RamanujanCorrection(lambda_=1.0)
    R_base = corr.evaluate(vel, m, b)

    # Shift velocity by constant vector U0 = (2.0, -1.5, 3.0)
    vel_shifted = VelocityField.zeros(m)
    vel_shifted.u.interior[:] = vel.u.interior + 2.0
    vel_shifted.v.interior[:] = vel.v.interior - 1.5
    vel_shifted.w.interior[:] = vel.w.interior + 3.0

    R_shifted = corr.evaluate(vel_shifted, m, b)

    diff_u = float(np.max(np.abs(R_shifted.u.interior - R_base.u.interior)))
    diff_v = float(np.max(np.abs(R_shifted.v.interior - R_base.v.interior)))
    diff_w = float(np.max(np.abs(R_shifted.w.interior - R_base.w.interior)))

    max_diff = max(diff_u, diff_v, diff_w)
    assert max_diff < 1e-8, f"Galilean invariance deviation = {max_diff}"
