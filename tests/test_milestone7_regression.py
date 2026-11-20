"""Milestone 7 Part L: correctness regression -- optimized (iterative
solver / SPD diffusion / warm-start) configurations must reproduce the
existing direct/reference solution within solver tolerance + floating
point, for every physics case this project has previously verified.
"""
import math

import numpy as np
import pytest

from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
)
from navier3d.fields import FlowState, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import ThetaSchemeIntegrator, run

REFERENCE_KWARGS = dict(
    pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    diffusion_kwargs=dict(formulation="pinned", solver="direct"),
)
OPTIMIZED_KWARGS = dict(
    pressure_kwargs=dict(solver="cg", null_space_strategy="pin_cell", tol=1e-12),
    diffusion_kwargs=dict(formulation="spd", solver="cg", rtol=1e-12),
    warm_start=True,
)


def _rel_l2(a: np.ndarray, b: np.ndarray, eps: float = 1e-12) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + eps))


def fbc(velocity, pressure="neumann", velocity_value=None, pressure_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
    )


# ==========================================================================
# Plane Poiseuille flow (pure Stokes, forced channel)
# ==========================================================================

RHO_P, NU_P, H_P, G_P = 1.0, 0.05, 0.5, 0.3


def _poiseuille_mesh(ny: int) -> StructuredMesh3D:
    return StructuredMesh3D(nx=3, ny=ny, nz=3, lx=0.3, ly=2.0 * H_P, lz=0.3, n_ghost=1)


def _poiseuille_bcs() -> BoundaryConditionSet:
    w = fbc("no_slip")
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=w, y_max=w, z_min=p, z_max=p)


def _poiseuille_forcing(mesh: StructuredMesh3D):
    def forcing(t: float) -> VelocityField:
        f = VelocityField.zeros(mesh)
        f.u.interior[:] = G_P / RHO_P
        return f
    return forcing


def _run_poiseuille(kwargs: dict, ny: int = 12, dt: float = 0.05, n_steps: int = 250):
    mesh = _poiseuille_mesh(ny)
    integrator = ThetaSchemeIntegrator(
        mesh, _poiseuille_bcs(), rho=RHO_P, nu=NU_P, dt=dt, theta=1.0, forcing=_poiseuille_forcing(mesh),
        **kwargs,
    )
    state = FlowState.zeros(mesh)
    final_state, history = run(integrator, state, n_steps)
    return mesh, final_state, history


def test_poiseuille_optimized_matches_direct_reference() -> None:
    mesh_ref, state_ref, hist_ref = _run_poiseuille(REFERENCE_KWARGS)
    mesh_opt, state_opt, hist_opt = _run_poiseuille(OPTIMIZED_KWARGS)

    assert hist_ref[-1].pressure_diagnostics.converged
    assert hist_opt[-1].pressure_diagnostics.converged
    rel_err = _rel_l2(state_opt.velocity.u.interior, state_ref.velocity.u.interior)
    assert rel_err < 1e-6, f"Poiseuille optimized-vs-reference relative L2 error {rel_err}"


# ==========================================================================
# Oscillatory plane-channel Stokes flow
# ==========================================================================

RHO_E, NU_E, H_E, G0_E = 1.0, 0.02, 0.5, 0.4


def _oscillatory_forcing(mesh: StructuredMesh3D, omega: float):
    def forcing(t: float) -> VelocityField:
        f = VelocityField.zeros(mesh)
        f.u.interior[:] = (G0_E / RHO_E) * math.cos(omega * t)
        return f
    return forcing


def _run_oscillatory(kwargs: dict, ny: int = 12, dt: float = 0.01, omega: float = 4.0, n_steps: int = 300):
    mesh = _poiseuille_mesh(ny)  # same channel geometry
    integrator = ThetaSchemeIntegrator(
        mesh, _poiseuille_bcs(), rho=RHO_E, nu=NU_E, dt=dt, theta=0.5, forcing=_oscillatory_forcing(mesh, omega),
        **kwargs,
    )
    state = FlowState.zeros(mesh)
    final_state, history = run(integrator, state, n_steps)
    return mesh, final_state, history


def test_oscillatory_channel_optimized_matches_direct_reference() -> None:
    mesh_ref, state_ref, hist_ref = _run_oscillatory(REFERENCE_KWARGS)
    mesh_opt, state_opt, hist_opt = _run_oscillatory(OPTIMIZED_KWARGS)

    assert hist_ref[-1].pressure_diagnostics.converged
    assert hist_opt[-1].pressure_diagnostics.converged
    rel_err = _rel_l2(state_opt.velocity.u.interior, state_ref.velocity.u.interior)
    assert rel_err < 1e-6, f"oscillatory-channel optimized-vs-reference relative L2 error {rel_err}"


# ==========================================================================
# Taylor-Green vortex (nonlinear)
# ==========================================================================

LX_A, LY_A, LZ_A = 1.0, 1.25, 0.5
NU_A, RHO_A, U0_A = 0.02, 1.0, 1.0
MX_A, MY_A = 2, 1
KX_A, KY_A = 2 * math.pi * MX_A / LX_A, 2 * math.pi * MY_A / LY_A


def _tg_u(x, y, z, t):
    return U0_A * np.sin(KX_A * x) * np.cos(KY_A * y) * np.exp(-NU_A * (KX_A ** 2 + KY_A ** 2) * t)


def _tg_v(x, y, z, t):
    return -U0_A * (KX_A / KY_A) * np.cos(KX_A * x) * np.sin(KY_A * y) * np.exp(-NU_A * (KX_A ** 2 + KY_A ** 2) * t)


def _tg_periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def _tg_state(mesh: StructuredMesh3D) -> FlowState:
    state = FlowState.zeros(mesh)
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    state.velocity.u.interior[:] = _tg_u(Xu, Yu, Zu, 0.0)
    state.velocity.v.interior[:] = _tg_v(Xv, Yv, Zv, 0.0)
    return state


def _run_tg(kwargs: dict, n: int = 20, dt: float = 0.0005, n_steps: int = 20):
    mesh = StructuredMesh3D(nx=n, ny=n, nz=4, lx=LX_A, ly=LY_A, lz=LZ_A, n_ghost=1)
    integrator = ThetaSchemeIntegrator(
        mesh, _tg_periodic_bcs(), rho=RHO_A, nu=NU_A, dt=dt, theta=0.5, convection_scheme="centered",
        **kwargs,
    )
    state = _tg_state(mesh)
    final_state, history = run(integrator, state, n_steps)
    return mesh, final_state, history


def test_taylor_green_optimized_matches_direct_reference() -> None:
    ref_kwargs = dict(REFERENCE_KWARGS, pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"))
    opt_kwargs = dict(OPTIMIZED_KWARGS, pressure_kwargs=dict(solver="cg", null_space_strategy="zero_mean", rhs_compatibility="mean_removal", tol=1e-12))

    mesh_ref, state_ref, hist_ref = _run_tg(ref_kwargs)
    mesh_opt, state_opt, hist_opt = _run_tg(opt_kwargs)

    assert max(h.max_divergence for h in hist_ref) < 1e-8
    assert max(h.max_divergence for h in hist_opt) < 1e-8

    err_u = _rel_l2(state_opt.velocity.u.interior, state_ref.velocity.u.interior)
    err_v = _rel_l2(state_opt.velocity.v.interior, state_ref.velocity.v.interior)
    assert err_u < 1e-6 and err_v < 1e-6

    p_ref = state_ref.pressure.interior - np.mean(state_ref.pressure.interior)
    p_opt = state_opt.pressure.interior - np.mean(state_opt.pressure.interior)
    assert _rel_l2(p_opt, p_ref) < 1e-6  # pressure modulo an additive constant

    ke_ref, ke_opt = hist_ref[-1].kinetic_energy, hist_opt[-1].kinetic_energy
    assert abs(ke_opt - ke_ref) / (abs(ke_ref) + 1e-12) < 1e-6


# ==========================================================================
# Manufactured nonlinear Navier-Stokes (TG base + extra pressure forcing)
# ==========================================================================

P0_B = 0.3
KPX_B, KPY_B, KPZ_B = KX_A, KY_A, 2 * math.pi / LZ_A


def _b_forcing(mesh: StructuredMesh3D):
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(mesh.cell_centers_x(), mesh.cell_centers_y(), mesh.face_coords_z(), indexing="ij")
    fx = P0_B * KPX_B * np.cos(KPX_B * Xu) * np.sin(KPY_B * Yu) * np.sin(KPZ_B * Zu) / RHO_A
    fy = P0_B * KPY_B * np.sin(KPX_B * Xv) * np.cos(KPY_B * Yv) * np.sin(KPZ_B * Zv) / RHO_A
    fz = P0_B * KPZ_B * np.sin(KPX_B * Xw) * np.sin(KPY_B * Yw) * np.cos(KPZ_B * Zw) / RHO_A

    def forcing(t: float) -> VelocityField:
        f = VelocityField.zeros(mesh)
        f.u.interior[:] = fx
        f.v.interior[:] = fy
        f.w.interior[:] = fz
        return f
    return forcing


def _run_manufactured(kwargs: dict, n: int = 16, dt: float = 0.0005, n_steps: int = 10):
    mesh = StructuredMesh3D(nx=n, ny=n, nz=4, lx=LX_A, ly=LY_A, lz=LZ_A, n_ghost=1)
    integrator = ThetaSchemeIntegrator(
        mesh, _tg_periodic_bcs(), rho=RHO_A, nu=NU_A, dt=dt, theta=0.5, convection_scheme="centered",
        forcing=_b_forcing(mesh), **kwargs,
    )
    state = _tg_state(mesh)
    final_state, history = run(integrator, state, n_steps)
    return mesh, final_state, history


def test_manufactured_nonlinear_ns_optimized_matches_direct_reference() -> None:
    ref_kwargs = dict(REFERENCE_KWARGS)
    opt_kwargs = dict(OPTIMIZED_KWARGS)

    mesh_ref, state_ref, hist_ref = _run_manufactured(ref_kwargs)
    mesh_opt, state_opt, hist_opt = _run_manufactured(opt_kwargs)

    assert max(h.max_divergence for h in hist_ref) < 1e-8
    assert max(h.max_divergence for h in hist_opt) < 1e-8

    err_u = _rel_l2(state_opt.velocity.u.interior, state_ref.velocity.u.interior)
    err_v = _rel_l2(state_opt.velocity.v.interior, state_ref.velocity.v.interior)
    err_w = _rel_l2(state_opt.velocity.w.interior, state_ref.velocity.w.interior)
    assert max(err_u, err_v, err_w) < 1e-6
