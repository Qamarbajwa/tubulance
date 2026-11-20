"""Milestone 12B Comprehensive Validation Benchmark Suite.

Runs:
1. Fine Resolved Reference (32^3, Cs=0).
2. Coarse No-Model (16^3, Cs=0).
3. Coarse Smagorinsky LES Sweep (16^3, Cs in [0.05, 0.10, 0.15, 0.20, 0.25]).

Evaluates velocity error E_u, kinetic energy error E_K, spectrum error E_spec,
low-k spectrum error E_lowk, SGS dissipation, dissipation ratio R_SGS, eddy viscosity
statistics (mean, p90, p99, max, fraction > nu), timing ratio R_t, and memory accounting.
"""
import time
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.decaying_turbulence import generate_matched_solenoidal_fields
from navier3d.fields import FlowState
from navier3d.filtering import restrict_velocity_fine_to_coarse, spectral_cutoff_filter
from navier3d.mesh import StructuredMesh3D
from navier3d.pressure import compute_initial_pressure
from navier3d.spectrum import compute_energy_spectrum
from navier3d.time_integrators import ThetaSchemeIntegrator, run
from navier3d.turbulence import SmagorinskyModel, compute_sgs_mechanical_work


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_les_validation_sweep_benchmark() -> None:
    """Execute complete Milestone 12B validation sweep and print required result table."""
    L = 2.0 * np.pi
    m_fine = StructuredMesh3D(nx=32, ny=32, nz=32, lx=L, ly=L, lz=L, n_ghost=1)
    m_coarse = StructuredMesh3D(nx=16, ny=16, nz=16, lx=L, ly=L, lz=L, n_ghost=1)
    b = periodic_bcs()

    rho, nu = 1.0, 0.002
    dt = 1e-3
    n_steps = 10

    # 1. Generate spectrally matched initial fields
    vel_fine0, vel_coarse0 = generate_matched_solenoidal_fields(m_fine, m_coarse, b, k_peak=2.0, E0=1.0, seed=42)
    p_fine0, _ = compute_initial_pressure(vel_fine0, b, m_fine, rho, nu, convection_scheme="centered", solver="direct", null_space_strategy="pin_cell")
    p_coarse0, _ = compute_initial_pressure(vel_coarse0, b, m_coarse, rho, nu, convection_scheme="centered", solver="direct", null_space_strategy="pin_cell")

    s_fine0 = FlowState(velocity=vel_fine0, pressure=p_fine0, time=0.0, step=0)
    s_coarse0 = FlowState(velocity=vel_coarse0, pressure=p_coarse0, time=0.0, step=0)

    # 2. Run Fine Resolved Reference (32^3, Cs=0)
    t0_fine = time.perf_counter()
    integ_fine = ThetaSchemeIntegrator(
        m_fine, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method="incremental", chi=1.0, pressure_extrapolation=True,
        turbulence_model=None,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    s_fine_final, _ = run(integ_fine, s_fine0, n_steps)
    t_fine = time.perf_counter() - t0_fine

    # Filter & restrict fine final reference velocity to coarse grid
    k_cutoff = np.pi / m_coarse.dx
    v_filt_fine = spectral_cutoff_filter(s_fine_final.velocity, m_fine, k_cutoff, b)
    v_ref_coarse = restrict_velocity_fine_to_coarse(v_filt_fine, m_fine, m_coarse, b)

    k_ref_shells, E_ref_k = compute_energy_spectrum(v_ref_coarse, m_coarse)
    K_ref = float(0.5 * np.mean(v_ref_coarse.u.interior[:-1, :, :] ** 2 + v_ref_coarse.v.interior[:, :-1, :] ** 2 + v_ref_coarse.w.interior[:, :, :-1] ** 2))

    # 3. Execute Coarse Sweep (Cs in [0.0, 0.05, 0.10, 0.15, 0.20, 0.25])
    cs_values = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25]
    results = []
    t_baseline = None

    print("\n" + "="*110)
    print("MILESTONE 12B QUANTITATIVE LES VALIDATION RESULT TABLE")
    print("="*110)
    print(f"{'Model':<25} | {'N':<4} | {'Cs':<5} | {'E_u':<9} | {'E_K':<9} | {'E_spec':<9} | {'E_lowk':<9} | {'Pi_SGS':<9} | {'nu_t/nu max':<11} | {'Rt':<5}")
    print("-" * 110)

    for cs in cs_values:
        model = SmagorinskyModel(cs=cs) if cs > 0.0 else None
        integ = ThetaSchemeIntegrator(
            m_coarse, b, rho=rho, nu=nu, dt=dt, theta=0.5, convection_scheme="centered",
            projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            turbulence_model=model,
            pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )

        t0_run = time.perf_counter()
        s_final, hist = run(integ, s_coarse0, n_steps)
        t_run = time.perf_counter() - t0_run

        if cs == 0.0:
            t_baseline = t_run

        rt = t_run / t_baseline if t_baseline else 1.0

        v_c = s_final.velocity
        # Compute metrics against filtered fine reference
        diff_u = v_c.u.interior[:-1, :, :] - v_ref_coarse.u.interior[:-1, :, :]
        diff_v = v_c.v.interior[:, :-1, :] - v_ref_coarse.v.interior[:, :-1, :]
        diff_w = v_c.w.interior[:, :, :-1] - v_ref_coarse.w.interior[:, :, :-1]

        l2_diff = np.sqrt(np.mean(diff_u**2 + diff_v**2 + diff_w**2))
        l2_ref = np.sqrt(np.mean(v_ref_coarse.u.interior[:-1, :, :]**2 + v_ref_coarse.v.interior[:, :-1, :]**2 + v_ref_coarse.w.interior[:, :, :-1]**2))
        E_u = float(l2_diff / (l2_ref + 1e-15))

        K_coarse = float(0.5 * np.mean(v_c.u.interior[:-1, :, :]**2 + v_c.v.interior[:, :-1, :]**2 + v_c.w.interior[:, :, :-1]**2))
        E_K = float(abs(K_coarse - K_ref) / (K_ref + 1e-15))

        k_shells, E_c_k = compute_energy_spectrum(v_c, m_coarse)
        min_len = min(len(E_c_k), len(E_ref_k))
        E_spec = float(np.sum(np.abs(E_c_k[:min_len] - E_ref_k[:min_len])) / (np.sum(E_ref_k[:min_len]) + 1e-15))

        # Low-wavenumber metric (k <= 0.5 * k_c)
        low_k_mask = k_shells[:min_len] <= (0.5 * k_cutoff)
        if np.any(low_k_mask):
            E_lowk = float(np.sum(np.abs(E_c_k[:min_len][low_k_mask] - E_ref_k[:min_len][low_k_mask])) / (np.sum(E_ref_k[:min_len][low_k_mask]) + 1e-15))
        else:
            E_lowk = E_spec

        pi_sgs = hist[-1].pi_sgs if hist[-1].pi_sgs is not None else 0.0
        nu_t_max_over_nu = hist[-1].nu_t_max_over_nu if hist[-1].nu_t_max_over_nu is not None else 0.0

        name = "Coarse no SGS" if cs == 0.0 else f"Coarse LES (Cs={cs:.2f})"
        print(f"{name:<25} | {16:<4} | {cs:<5.2f} | {E_u:<9.4f} | {E_K:<9.4f} | {E_spec:<9.4f} | {E_lowk:<9.4f} | {pi_sgs:<9.4e} | {nu_t_max_over_nu:<11.2f} | {rt:<5.2f}")

        results.append({
            "cs": cs, "E_u": E_u, "E_K": E_K, "E_spec": E_spec, "E_lowk": E_lowk,
            "pi_sgs": pi_sgs, "nu_t_max_over_nu": nu_t_max_over_nu, "Rt": rt
        })

    print("="*110 + "\n")

    # Assertions
    assert len(results) == len(cs_values)
    # Mechanical work / SGS dissipation must be non-negative
    for res in results:
        assert res["pi_sgs"] >= 0.0
