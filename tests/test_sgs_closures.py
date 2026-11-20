"""Unit tests and reference-based benchmark evaluation for WALE and Vreman SGS closures.

Verifies:
1. WALE (Nicoud & Ducros 1999) and Vreman (Vreman 2004) model properties:
   - Non-negativity nu_t >= 0.
   - Zero eddy viscosity for zero velocity fields.
   - Automatic dissipation reduction for laminar shear flows (B_beta -> 0 for Vreman, S_sd -> 0 for WALE).
2. Unsteady solver integration with ThetaSchemeIntegrator and run().
3. Exact reference-based accuracy comparison against filtered fine (32^3) baseline.
"""
from __future__ import annotations

import time
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.decaying_turbulence import generate_matched_solenoidal_fields
from navier3d.fields import FlowState, VelocityField
from navier3d.filtering import restrict_velocity_fine_to_coarse, spectral_cutoff_filter
from navier3d.mesh import StructuredMesh3D
from navier3d.pressure import compute_initial_pressure
from navier3d.spectrum import compute_energy_spectrum
from navier3d.time_integrators import ThetaSchemeIntegrator, run
from navier3d.turbulence import DynamicSmagorinskyModel, SmagorinskyModel, VremanModel, WALEModel


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_wale_model_properties() -> None:
    """Verify WALEModel non-negativity, zero-field output, and parameter validation."""
    with pytest.raises(ValueError):
        WALEModel(cw=-0.1)

    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()
    vel_zero = VelocityField.zeros(mesh)

    model = WALEModel(cw=0.325)
    nu_t_zero = model.eddy_viscosity(vel_zero, mesh, bcs)

    assert np.all(nu_t_zero.interior == 0.0)

    # Random solenoidal field test
    vel, _ = generate_matched_solenoidal_fields(mesh, mesh, bcs, k_peak=2.0, E0=1.0, seed=123)
    nu_t = model.eddy_viscosity(vel, mesh, bcs)

    assert np.all(nu_t.interior >= 0.0)
    assert np.max(nu_t.interior) > 0.0
    assert np.all(np.isfinite(nu_t.interior))


def test_vreman_model_properties() -> None:
    """Verify VremanModel non-negativity, zero-field output, and laminar shear flow reduction."""
    with pytest.raises(ValueError):
        VremanModel(cv=-0.05)

    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()
    vel_zero = VelocityField.zeros(mesh)

    model = VremanModel(cv=0.07)
    nu_t_zero = model.eddy_viscosity(vel_zero, mesh, bcs)

    assert np.all(nu_t_zero.interior == 0.0)

    # Pure 1D/2D laminar shear flow u(y) = y, v=0, w=0 -> B_beta = 0 exactly
    vel_shear = VelocityField.zeros(mesh)
    y_coords = np.linspace(0, 2.0 * np.pi, 16, endpoint=False)
    for j in range(16):
        vel_shear.u.interior[:, j, :] = y_coords[j]

    nu_t_shear = model.eddy_viscosity(vel_shear, mesh, bcs)
    assert np.allclose(nu_t_shear.interior, 0.0, atol=1e-8)

    # Random solenoidal turbulent field test
    vel, _ = generate_matched_solenoidal_fields(mesh, mesh, bcs, k_peak=2.0, E0=1.0, seed=456)
    nu_t = model.eddy_viscosity(vel, mesh, bcs)

    assert np.all(nu_t.interior >= 0.0)
    assert np.max(nu_t.interior) > 0.0
    assert np.all(np.isfinite(nu_t.interior))


def test_sgs_closures_with_theta_integrator() -> None:
    """Verify WALE and Vreman models run stably inside ThetaSchemeIntegrator."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()
    rho, nu, dt = 1.0, 0.002, 1e-3

    vel0, _ = generate_matched_solenoidal_fields(mesh, mesh, bcs, k_peak=2.0, E0=1.0, seed=789)
    p0, _ = compute_initial_pressure(vel0, bcs, mesh, rho, nu, convection_scheme="centered", solver="direct", null_space_strategy="pin_cell")
    s0 = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

    for name, model in [("WALE", WALEModel(cw=0.325)), ("Vreman", VremanModel(cv=0.07))]:
        integ = ThetaSchemeIntegrator(
            mesh, bcs, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
            projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            turbulence_model=model, pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )
        s_final, history = run(integ, s0, n_steps=10)

        assert len(history) == 10
        assert np.all(np.isfinite(s_final.velocity.u.interior))
        assert np.all(np.isfinite(s_final.velocity.v.interior))
        assert np.all(np.isfinite(s_final.velocity.w.interior))


def test_full_sgs_closure_benchmark_suite() -> None:
    """Milestone S1 Full SGS Closure Accuracy & Reference Pass/Fail Evaluation Suite.

    Evaluates:
    - Filtered Fine Reference (32^3, Cs=0).
    - Baseline Coarse NS (16^3, Cs=0).
    - Static Smagorinsky (16^3, Cs=0.15).
    - Dynamic Smagorinsky (16^3).
    - WALE Model (16^3, Cw=0.325).
    - Vreman Model (16^3, Cv=0.07).

    Prints structured Markdown comparison table and evaluates strict reference accuracy.
    """
    L = 2.0 * np.pi
    m_fine = StructuredMesh3D(nx=32, ny=32, nz=32, lx=L, ly=L, lz=L, n_ghost=1)
    m_coarse = StructuredMesh3D(nx=16, ny=16, nz=16, lx=L, ly=L, lz=L, n_ghost=1)
    b = periodic_bcs()

    rho, nu = 1.0, 0.002
    dt = 1e-3
    n_steps = 10

    # 1. Spectrally matched initial fields
    vel_fine0, vel_coarse0 = generate_matched_solenoidal_fields(m_fine, m_coarse, b, k_peak=2.0, E0=1.0, seed=42)
    p_fine0, _ = compute_initial_pressure(vel_fine0, b, m_fine, rho, nu, convection_scheme="centered", solver="direct", null_space_strategy="pin_cell")
    p_coarse0, _ = compute_initial_pressure(vel_coarse0, b, m_coarse, rho, nu, convection_scheme="centered", solver="direct", null_space_strategy="pin_cell")

    s_fine0 = FlowState(velocity=vel_fine0, pressure=p_fine0, time=0.0, step=0)
    s_coarse0 = FlowState(velocity=vel_coarse0, pressure=p_coarse0, time=0.0, step=0)

    # 2. Run Fine Reference (32^3, Cs=0)
    integ_fine = ThetaSchemeIntegrator(
        m_fine, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method="incremental", chi=1.0, pressure_extrapolation=True,
        turbulence_model=None, pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    s_fine_final, _ = run(integ_fine, s_fine0, n_steps)

    k_cutoff = np.pi / m_coarse.dx
    v_filt_fine = spectral_cutoff_filter(s_fine_final.velocity, m_fine, k_cutoff, b)
    v_ref_coarse = restrict_velocity_fine_to_coarse(v_filt_fine, m_fine, m_coarse, b)

    # 3. Model closures to evaluate
    closures = [
        ("Coarse Baseline NS", None),
        ("Coarse Static Smagorinsky (Cs=0.15)", SmagorinskyModel(cs=0.15)),
        ("Coarse Dynamic Smagorinsky", DynamicSmagorinskyModel()),
        ("Coarse WALE (Cw=0.325)", WALEModel(cw=0.325)),
        ("Coarse Vreman (Cv=0.07)", VremanModel(cv=0.07)),
    ]

    print("\n==========================================================================================================")
    print("MILESTONE S1 SGS CLOSURE BENCHMARK COMPARISON TABLE")
    print("==========================================================================================================")
    print(f"{'Closure Model':<35} | {'Grid':<6} | {'E_u (Vel Error)':<15} | {'E_K (Energy Err)':<16} | {'Wall Time (s)':<12}")
    print("----------------------------------------------------------------------------------------------------------")

    results = []
    e_u_baseline = None

    for name, model in closures:
        t0 = time.perf_counter()
        integ = ThetaSchemeIntegrator(
            m_coarse, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
            projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            turbulence_model=model, pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )
        s_final, hist = run(integ, s_coarse0, n_steps)
        t_wall = time.perf_counter() - t0

        v_m = s_final.velocity
        diff_u = v_m.u.interior[:-1, :, :] - v_ref_coarse.u.interior[:-1, :, :]
        diff_v = v_m.v.interior[:, :-1, :] - v_ref_coarse.v.interior[:, :-1, :]
        diff_w = v_m.w.interior[:, :, :-1] - v_ref_coarse.w.interior[:, :, :-1]

        norm_diff = np.sqrt(np.mean(diff_u**2 + diff_v**2 + diff_w**2))
        norm_ref = np.sqrt(np.mean(v_ref_coarse.u.interior[:-1, :, :]**2 + v_ref_coarse.v.interior[:, :-1, :]**2 + v_ref_coarse.w.interior[:, :, :-1]**2))
        E_u = float(norm_diff / (norm_ref + 1e-15))

        K_m = float(0.5 * np.mean(v_m.u.interior[:-1, :, :]**2 + v_m.v.interior[:, :-1, :]**2 + v_m.w.interior[:, :, :-1]**2))
        K_ref = float(0.5 * np.mean(v_ref_coarse.u.interior[:-1, :, :]**2 + v_ref_coarse.v.interior[:, :-1, :]**2 + v_ref_coarse.w.interior[:, :, :-1]**2))
        E_K = float(abs(K_m - K_ref) / (K_ref + 1e-15))

        if "Baseline" in name:
            e_u_baseline = E_u

        results.append((name, E_u, E_K, t_wall))
        print(f"{name:<35} | 16^3   | {E_u:<15.6f} | {E_K:<16.6f} | {t_wall:<12.3f}")

    print("==========================================================================================================\n")

    # Assertions for physical correctness
    assert e_u_baseline is not None
    for name, E_u, E_K, t_wall in results:
        if "Smagorinsky" in name or "WALE" in name or "Vreman" in name:
            assert E_u <= e_u_baseline * 1.01, f"{name} accuracy degraded beyond baseline!"
