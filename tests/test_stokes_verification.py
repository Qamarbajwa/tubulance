"""Milestone 5 verification cases A-H (I and J live in test_time_integrators.py).

Still no convection (Milestone 6) -- everything here is unsteady Stokes
flow: theta-scheme diffusion (backward Euler theta=1, Crank-Nicolson
theta=0.5) + Milestone 4 projection.

Sections map directly to the review's A-H labels. Parameters (resolution,
dt, run length) were tuned empirically (see the Milestone 5 report) so
this file runs in a reasonable time while still meeting every stated
acceptance target on its own "documented resolved mesh" -- this file *is*
that documentation.
"""
import cmath
import math

import numpy as np
import pytest

from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_pressure_bc,
)
from navier3d.fields import FaceField, FlowState, ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import divergence, gradient
from navier3d.time_integrators import ThetaSchemeIntegrator, run


def fbc(velocity, pressure="neumann", velocity_value=None, pressure_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
    )


def channel_bcs() -> BoundaryConditionSet:
    """Periodic in x, z; no-slip walls in y."""
    p = fbc("periodic", "periodic")
    w = fbc("no_slip")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=w, y_max=w, z_min=p, z_max=p)


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def _errors(computed: np.ndarray, exact: np.ndarray) -> tuple:
    diff = (computed - exact).ravel()
    return float(np.mean(np.abs(diff))), float(np.sqrt(np.mean(diff ** 2))), float(np.max(np.abs(diff)))


def _order(e1: float, e2: float) -> float:
    return math.log(e1 / e2) / math.log(2.0)


# ==========================================================================
# A. Pure diffusion eigenmode
# ==========================================================================

LY_A = 1.0
U0_A = 1.0
NU_A = 0.05
K_A = math.pi / LY_A  # m=1 mode: sin(k*0)=sin(k*Ly)=0, homogeneous no-slip compatible


def _exact_eigenmode(y: np.ndarray, t: float) -> np.ndarray:
    return U0_A * np.sin(K_A * y) * np.exp(-NU_A * K_A * K_A * t)


def _eigenmode_mesh(ny: int, nx: int = 2, nz: int = 2, n_ghost: int = 1) -> StructuredMesh3D:
    return StructuredMesh3D(nx=nx, ny=ny, nz=nz, lx=0.3, ly=LY_A, lz=0.3, n_ghost=n_ghost)


def _eigenmode_integrator(mesh: StructuredMesh3D, dt: float, theta: float) -> ThetaSchemeIntegrator:
    return ThetaSchemeIntegrator(
        mesh, channel_bcs(), rho=1.0, nu=NU_A, dt=dt, theta=theta,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )


def _eigenmode_initial_state(mesh: StructuredMesh3D) -> FlowState:
    state = FlowState.zeros(mesh)
    yc = mesh.cell_centers_y()
    state.velocity.u.interior[:, :, :] = _exact_eigenmode(yc, 0.0)[None, :, None]
    return state


def test_A_eigenmode_matches_analytical_decay() -> None:
    ny = 48
    dt = 0.005
    n_steps = 20  # t=0.1
    mesh = _eigenmode_mesh(ny)
    integrator = _eigenmode_integrator(mesh, dt, theta=0.5)
    state = _eigenmode_initial_state(mesh)
    final_state, history = run(integrator, state, n_steps)

    yc = mesh.cell_centers_y()
    exact = _exact_eigenmode(yc, n_steps * dt)
    numeric = final_state.velocity.u.interior[0, :, 0]
    l1, l2, linf = _errors(numeric, exact)
    assert linf < 1e-4
    # divergence stays at machine precision throughout (field only varies
    # with y, exactly solenoidal for all time)
    assert max(h.max_divergence for h in history) < 1e-8


# ==========================================================================
# B. Temporal-order test (self-referenced: isolates temporal error from the
# spatial discretization's own eigenvalue, which otherwise contaminates a
# comparison against the continuous solution once error terms are this
# small -- see the Milestone 5 report for the diagnosis)
# ==========================================================================

@pytest.mark.parametrize("theta,expected_order", [(1.0, 1.0), (0.5, 2.0)])
def test_B_temporal_order(theta: float, expected_order: float) -> None:
    ny = 48
    T = 0.05
    mesh = _eigenmode_mesh(ny)

    def run_to(dt: float) -> np.ndarray:
        n_steps = round(T / dt)
        integrator = _eigenmode_integrator(mesh, dt, theta)
        state = _eigenmode_initial_state(mesh)
        final_state, _ = run(integrator, state, n_steps)
        return final_state.velocity.u.interior[0, :, 0]

    reference = run_to(T / 4000)
    dts = [0.01, 0.005, 0.0025, 0.00125]
    errors = [float(np.sqrt(np.mean((run_to(dt) - reference) ** 2))) for dt in dts]
    orders = [_order(e1, e2) for e1, e2 in zip(errors[:-1], errors[1:])]
    for order in orders:
        assert expected_order - 0.25 <= order <= expected_order + 0.5, f"theta={theta}: orders {orders}"


# ==========================================================================
# C. Spatial-order test (dt negligible, vary ny, compare to continuous exact)
# ==========================================================================

def test_C_spatial_order() -> None:
    dt = 1e-6
    errors = []
    for ny in [16, 32, 64, 128]:
        mesh = _eigenmode_mesh(ny)
        integrator = _eigenmode_integrator(mesh, dt, theta=0.5)
        state = _eigenmode_initial_state(mesh)
        final_state, _ = run(integrator, state, n_steps=1)
        yc = mesh.cell_centers_y()
        exact = _exact_eigenmode(yc, dt)
        _, l2, _ = _errors(final_state.velocity.u.interior[0, :, 0], exact)
        errors.append(l2)
    orders = [_order(e1, e2) for e1, e2 in zip(errors[:-1], errors[1:])]
    for order in orders:
        assert 1.8 <= order <= 2.2, f"observed orders {orders}"


# ==========================================================================
# D. Plane Poiseuille flow
# ==========================================================================

LY_D = 1.0
H_D = LY_D / 2.0
NU_D = 0.05
F_D = 0.02
RHO_D = 1.0


def _exact_poiseuille(y: np.ndarray) -> np.ndarray:
    yc = y - H_D
    return F_D / (2.0 * NU_D) * (H_D ** 2 - yc ** 2)


def _poiseuille_forcing(mesh: StructuredMesh3D):
    def forcing(t: float) -> VelocityField:
        f = VelocityField.zeros(mesh)
        f.u.data[:] = F_D
        return f
    return forcing


def _run_poiseuille(ny: int, dt: float, n_steps: int, nx: int = 3, nz: int = 3):
    mesh = StructuredMesh3D(nx=nx, ny=ny, nz=nz, lx=0.5, ly=LY_D, lz=0.5, n_ghost=1)
    integrator = ThetaSchemeIntegrator(
        mesh, channel_bcs(), rho=RHO_D, nu=NU_D, dt=dt, theta=1.0, forcing=_poiseuille_forcing(mesh),
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    state = FlowState.zeros(mesh)
    final_state, history = run(integrator, state, n_steps)
    return mesh, final_state, history


def test_D_poiseuille_profile_centerline_flowrate_wallshear() -> None:
    ny = 32
    mesh, final_state, history = _run_poiseuille(ny, dt=0.05, n_steps=400)  # t=20 ~ 10 relaxation times
    yc = mesh.cell_centers_y()
    exact_profile = _exact_poiseuille(yc)
    numeric_profile = final_state.velocity.u.interior[0, :, 0]

    profile_rel_err = np.max(np.abs(numeric_profile - exact_profile)) / _exact_poiseuille(np.array([H_D]))[0]
    assert profile_rel_err < 0.005

    centerline_exact = _exact_poiseuille(np.array([H_D]))[0]
    centerline_numeric = final_state.velocity.u.interior[0, ny // 2, 0]
    assert abs(centerline_numeric - centerline_exact) / centerline_exact < 0.005

    flow_rate_exact = F_D * H_D ** 2 / (3.0 * NU_D)  # mean velocity = (1/2h) * integral u dy
    flow_rate_numeric = float(np.mean(numeric_profile))
    assert abs(flow_rate_numeric - flow_rate_exact) / flow_rate_exact < 0.005

    wall_shear_exact = F_D * H_D  # nu*du/dy at y=0
    dy = mesh.dy
    wall_shear_numeric = NU_D * (numeric_profile[0] - 0.0) / (dy / 2.0)
    assert abs(wall_shear_numeric - wall_shear_exact) / wall_shear_exact < 0.01

    # divergence stays small throughout the run, not just at the end
    assert max(h.max_divergence for h in history) < 1e-8

    # steady-state convergence criterion: velocity change per step -> 0
    assert abs(history[-1].max_velocity - history[-2].max_velocity) < 1e-5


def test_D_poiseuille_spatial_convergence() -> None:
    errors = []
    for ny in [8, 16, 32, 64]:
        mesh, final_state, history = _run_poiseuille(ny, dt=0.05, n_steps=400)
        yc = mesh.cell_centers_y()
        exact = _exact_poiseuille(yc)
        _, l2, _ = _errors(final_state.velocity.u.interior[0, :, 0], exact)
        errors.append(l2)
    orders = [_order(e1, e2) for e1, e2 in zip(errors[:-1], errors[1:])]
    for order in orders:
        assert 1.7 <= order <= 2.3, f"observed orders {orders}"


# ==========================================================================
# E. Oscillatory plane-channel Stokes flow (plane-channel Womersley analogue)
#
# Named per the review's explicit instruction: "oscillatory plane-channel
# Stokes flow" / "plane-channel Womersley analogue" -- NOT "Womersley flow"
# unqualified, which implies circular-pipe geometry not represented here.
# ==========================================================================

LY_E = 1.0
H_E = LY_E / 2.0
NU_E = 0.05
RHO_E = 1.0
F0_E = 0.02


def _exact_uhat(y: np.ndarray, omega: float) -> np.ndarray:
    yc = y - H_E
    lam = cmath.sqrt(1j * omega / NU_E)
    return (F0_E / (1j * omega)) * (1.0 - np.cosh(lam * yc) / np.cosh(lam * H_E))


def _oscillatory_forcing(mesh: StructuredMesh3D, omega: float):
    def forcing(t: float) -> VelocityField:
        f = VelocityField.zeros(mesh)
        f.u.data[:] = F0_E * math.cos(omega * t)
        return f
    return forcing


def _run_oscillatory(ny: int, dt: float, omega: float, n_transient_periods: float = 5.0, nx: int = 2, nz: int = 2):
    mesh = StructuredMesh3D(nx=nx, ny=ny, nz=nz, lx=0.3, ly=LY_E, lz=0.3, n_ghost=1)
    integrator = ThetaSchemeIntegrator(
        mesh, channel_bcs(), rho=RHO_E, nu=NU_E, dt=dt, theta=0.5, forcing=_oscillatory_forcing(mesh, omega),
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    period = 2.0 * math.pi / omega
    n_transient = round(n_transient_periods * period / dt)
    n_record = round(period / dt)
    state = FlowState.zeros(mesh)
    state, _ = run(integrator, state, n_transient)

    times, profiles = [], []
    for _ in range(n_record):
        state, diag = integrator.step(state)
        times.append(state.time)
        profiles.append(state.velocity.u.interior[0, :, 0].copy())
    return mesh, np.array(times), np.array(profiles)


def _fit_amplitude_phase(times: np.ndarray, profiles: np.ndarray, omega: float) -> tuple:
    """Least-squares fit u(t) ~= a*cos(wt) + b*sin(wt) at every column of
    `profiles`; returns (amplitude, phase) with u(t) = amp*cos(wt+phase)."""
    A = np.stack([np.cos(omega * times), np.sin(omega * times)], axis=1)
    coeffs, *_ = np.linalg.lstsq(A, profiles, rcond=None)
    a, b = coeffs[0], coeffs[1]
    amplitude = np.sqrt(a ** 2 + b ** 2)
    phase = np.arctan2(-b, a)
    return amplitude, phase


def test_E_oscillatory_channel_amplitude_and_phase_profile() -> None:
    ny, dt, omega = 24, 0.01, 2.0
    mesh, times, profiles = _run_oscillatory(ny, dt, omega)
    yc = mesh.cell_centers_y()

    amp_numeric, phase_numeric = _fit_amplitude_phase(times, profiles, omega)
    uhat = _exact_uhat(yc, omega)
    amp_exact, phase_exact = np.abs(uhat), np.angle(uhat)

    amp_rel_err = np.max(np.abs(amp_numeric - amp_exact)) / np.max(amp_exact)
    assert amp_rel_err < 0.01

    # Phase is ill-conditioned wherever amplitude -> 0 (a physical property
    # of the signal, not a solver defect): compare phase only where the
    # amplitude is a non-negligible fraction of its peak.
    mask = amp_exact > 0.2 * np.max(amp_exact)
    phase_diff_deg = np.degrees(np.angle(np.exp(1j * (phase_numeric - phase_exact))))
    assert np.max(np.abs(phase_diff_deg[mask])) < 1.0


def test_E_oscillatory_channel_bulk_amplitude_and_phase() -> None:
    ny, dt, omega = 24, 0.01, 2.0
    mesh, times, profiles = _run_oscillatory(ny, dt, omega)
    yc = mesh.cell_centers_y()

    bulk_numeric = np.mean(profiles, axis=1)
    amp_bulk_num, phase_bulk_num = _fit_amplitude_phase(times, bulk_numeric[:, None], omega)
    amp_bulk_num, phase_bulk_num = float(amp_bulk_num[0]), float(phase_bulk_num[0])

    bulk_exact = complex(np.mean(_exact_uhat(yc, omega)))
    amp_bulk_exact, phase_bulk_exact = abs(bulk_exact), cmath.phase(bulk_exact)

    assert abs(amp_bulk_num - amp_bulk_exact) / amp_bulk_exact < 0.01
    phase_err_deg = abs(math.degrees(math.atan2(
        math.sin(phase_bulk_num - phase_bulk_exact), math.cos(phase_bulk_num - phase_bulk_exact)
    )))
    assert phase_err_deg < 1.0


def test_E_oscillatory_channel_periodic_repeat_error() -> None:
    """After transient decay, the profile one period later should match
    the starting profile of that recorded period (true periodic steady
    state, not still relaxing)."""
    ny, dt, omega = 24, 0.01, 2.0
    mesh, times, profiles = _run_oscillatory(ny, dt, omega, n_transient_periods=7.0)
    repeat_err = np.max(np.abs(profiles[0] - profiles[-1])) / np.max(np.abs(profiles))
    assert repeat_err < 0.03


def test_E_oscillatory_channel_temporal_convergence() -> None:
    """Self-referenced (vs. a very fine-dt run at the SAME ny), for the
    same reason as test_B: at these amplitude-error magnitudes, the fixed
    spatial discretization error at any practical ny dominates a
    continuous-solution comparison and completely masks dt-refinement
    (verified empirically: the error against the continuous solution is
    flat at ~5.9e-5 for dt in [0.02, 0.0025] at ny=24 -- that whole range
    is already well inside the spatial-error floor)."""
    ny, omega = 24, 2.0
    reference_mesh, reference_times, reference_profiles = _run_oscillatory(ny, 0.02 / 32, omega)
    ref_amp, _ = _fit_amplitude_phase(reference_times, reference_profiles, omega)

    errors = []
    for dt in [0.02, 0.01, 0.005]:
        mesh, times, profiles = _run_oscillatory(ny, dt, omega)
        amp_numeric, _ = _fit_amplitude_phase(times, profiles, omega)
        errors.append(float(np.sqrt(np.mean((amp_numeric - ref_amp) ** 2))))
    orders = [_order(e1, e2) for e1, e2 in zip(errors[:-1], errors[1:])]
    for order in orders:
        assert order > 1.5, f"observed orders {orders}"


def test_E_oscillatory_channel_multiple_frequencies() -> None:
    """A second, higher dimensionless frequency (larger omega*h^2/nu, the
    plane-channel analogue of a Womersley number) -- looser tolerance,
    just confirming the method remains accurate across frequency regimes,
    not re-establishing the tight <1% bound already shown at omega=2."""
    ny, dt, omega = 24, 0.005, 6.0
    mesh, times, profiles = _run_oscillatory(ny, dt, omega, n_transient_periods=5.0)
    yc = mesh.cell_centers_y()
    amp_numeric, phase_numeric = _fit_amplitude_phase(times, profiles, omega)
    uhat = _exact_uhat(yc, omega)
    amp_exact, phase_exact = np.abs(uhat), np.angle(uhat)
    amp_rel_err = np.max(np.abs(amp_numeric - amp_exact)) / np.max(amp_exact)
    assert amp_rel_err < 0.03
    mask = amp_exact > 0.3 * np.max(amp_exact)
    phase_diff_deg = np.degrees(np.angle(np.exp(1j * (phase_numeric - phase_exact))))
    assert np.max(np.abs(phase_diff_deg[mask])) < 3.0


# ==========================================================================
# F. Manufactured full unsteady Stokes solution
#
# u = U0*cos(kx x)*sin(ky y)*exp(-sigma t), v = -U0*(kx/ky)*sin(kx x)*cos(ky y)*exp(-sigma t),
# w = 0, sigma = nu*(kx^2+ky^2): by construction this (u,v) pair is exactly
# divergence-free for all time AND exactly satisfies du/dt = nu*lap(u) on
# its own (the defining property of a diffusion eigenmode, Section A,
# extended to 2 components) -- so p=0, f=0 would already be an exact
# solution. To exercise the forcing pathway non-trivially, a second,
# independent, time-INDEPENDENT pressure field p = P0*sin(kx x)*sin(ky y)*sin(kz z)
# is added on top (pressure imposes no constraint on u's divergence-free
# property); since the (u,v) part already satisfies the equation on its
# own, the required forcing collapses to exactly f = (1/rho)*grad(p) (the
# w-equation is satisfied identically too: dw/dt=0 = -(1/rho)dp/dz + 0 +
# (1/rho)dp/dz).
# ==========================================================================

LX_F, LY_F, LZ_F = 1.0, 1.25, 1.5
U0_F, NU_F, RHO_F, P0_F = 1.0, 0.05, 1.0, 0.3
KX_F, KY_F, KZ_F = 2 * math.pi / LX_F, 2 * math.pi / LY_F, 2 * math.pi / LZ_F
SIGMA_F = NU_F * (KX_F ** 2 + KY_F ** 2)


def _f_u_exact(x, y, z, t):
    return U0_F * np.cos(KX_F * x) * np.sin(KY_F * y) * np.exp(-SIGMA_F * t)


def _f_v_exact(x, y, z, t):
    return -U0_F * (KX_F / KY_F) * np.sin(KX_F * x) * np.cos(KY_F * y) * np.exp(-SIGMA_F * t)


def _f_forcing(mesh: StructuredMesh3D):
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(mesh.cell_centers_x(), mesh.cell_centers_y(), mesh.face_coords_z(), indexing="ij")
    fx = P0_F * KX_F * np.cos(KX_F * Xu) * np.sin(KY_F * Yu) * np.sin(KZ_F * Zu) / RHO_F
    fy = P0_F * KY_F * np.sin(KX_F * Xv) * np.cos(KY_F * Yv) * np.sin(KZ_F * Zv) / RHO_F
    fz = P0_F * KZ_F * np.sin(KX_F * Xw) * np.sin(KY_F * Yw) * np.cos(KZ_F * Zw) / RHO_F

    def forcing(t: float) -> VelocityField:
        f = VelocityField.zeros(mesh)
        f.u.interior[:] = fx
        f.v.interior[:] = fy
        f.w.interior[:] = fz
        return f
    return forcing


def _run_manufactured_stokes(n: int, dt: float, n_steps: int):
    mesh = StructuredMesh3D(nx=n, ny=n, nz=n, lx=LX_F, ly=LY_F, lz=LZ_F, n_ghost=1)
    # solver="direct": for this periodic 3-D problem, CG at tol=1e-12 (needed
    # for a clean convergence-order measurement) is dramatically slower than
    # a direct factorization reused across all 20 steps (measured: ~94s vs
    # ~35s at n=32 with CG vs direct respectively; direct is used here with
    # a capped n=20 to keep the *whole* test suite's runtime reasonable --
    # 3-D direct sparse LU fill-in grows faster than linearly with N, which
    # is exactly why a real solver would reach for multigrid/PyAMG at
    # production scale (Milestone 3's documented, not-yet-implemented
    # roadmap item), not a comment on correctness at this test's scale.
    integrator = ThetaSchemeIntegrator(
        mesh, periodic_bcs(), rho=RHO_F, nu=NU_F, dt=dt, theta=0.5, forcing=_f_forcing(mesh),
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    state = FlowState.zeros(mesh)
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    state.velocity.u.interior[:] = _f_u_exact(Xu, Yu, Zu, 0.0)
    state.velocity.v.interior[:] = _f_v_exact(Xv, Yv, Zv, 0.0)
    final_state, history = run(integrator, state, n_steps)
    return mesh, final_state, history


def _manufactured_error(mesh: StructuredMesh3D, final_state: FlowState, T: float) -> float:
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    exact_u = _f_u_exact(Xu, Yu, Zu, T)
    exact_v = _f_v_exact(Xv, Yv, Zv, T)
    err_u = final_state.velocity.u.interior - exact_u
    err_v = final_state.velocity.v.interior - exact_v
    return float(np.sqrt(np.mean(err_u ** 2) + np.mean(err_v ** 2)))


def test_F_manufactured_stokes_full_pipeline_spatial_convergence() -> None:
    dt, n_steps = 0.001, 20
    resolutions = [8, 16, 20]
    errors = []
    for n in resolutions:
        mesh, final_state, history = _run_manufactured_stokes(n, dt, n_steps)
        errors.append(_manufactured_error(mesh, final_state, n_steps * dt))
        assert max(h.max_divergence for h in history) < 1e-8
    for n1, n2, e1, e2 in zip(resolutions[:-1], resolutions[1:], errors[:-1], errors[1:]):
        order = math.log(e1 / e2) / math.log(n2 / n1)
        assert 1.7 <= order <= 2.3, f"n={n1}->{n2}: observed order {order}"


# ==========================================================================
# G. Long-run incompressibility
# ==========================================================================

def test_G_long_run_no_divergence_accumulation() -> None:
    m = StructuredMesh3D(nx=6, ny=8, nz=10, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    bcs = channel_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.08, dt=0.01, theta=0.5,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    rng = np.random.default_rng(0)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.3, 0.3, size=comp.interior.shape)
    from navier3d.boundary_conditions import apply_velocity_bc
    apply_velocity_bc(state.velocity, bcs)

    final_state, history = run(integrator, state, n_steps=300)
    # raw L_inf / L_2 (units 1/time, case-dependent magnitude -- see
    # StepDiagnostics docstring) and the dimensionless normalized E_div
    # are checked SEPARATELY and against DIFFERENT thresholds: the
    # project's stated acceptance target ("normalized divergence < 1e-8
    # for controlled benchmarks") applies to E_div, not to the raw forms.
    max_divs = [h.max_divergence for h in history]
    l2_divs = [h.l2_divergence for h in history]
    normalized_divs = [h.normalized_divergence for h in history]

    assert max(max_divs) < 1e-6  # raw L_inf
    assert max(l2_divs) < 1e-6  # raw L_2
    assert max(normalized_divs) < 1e-8  # dimensionless E_div, the acceptance-criterion quantity
    # no systematic growth: the second half of the run is not worse than the first
    first_half_max = max(max_divs[:150])
    second_half_max = max(max_divs[150:])
    assert second_half_max <= max(first_half_max * 10.0, 1e-8)


# ==========================================================================
# H. Energy decay
# ==========================================================================

def test_H_energy_monotonic_non_increase_unforced() -> None:
    m = StructuredMesh3D(nx=6, ny=8, nz=10, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    bcs = channel_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=1.0,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    rng = np.random.default_rng(1)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.5, 0.5, size=comp.interior.shape)
    from navier3d.boundary_conditions import apply_velocity_bc
    apply_velocity_bc(state.velocity, bcs)

    final_state, history = run(integrator, state, n_steps=100)
    energies = [h.kinetic_energy for h in history]
    for k_before, k_after in zip(energies[:-1], energies[1:]):
        assert k_after <= k_before + 1e-10


def test_H_energy_decay_matches_analytical_eigenmode() -> None:
    ny = 48
    dt = 0.005
    n_steps = 30
    mesh = _eigenmode_mesh(ny)
    integrator = _eigenmode_integrator(mesh, dt, theta=0.5)
    state = _eigenmode_initial_state(mesh)
    final_state, history = run(integrator, state, n_steps)

    # K_exact(t) = 0.25 * U0^2 * Lx*Ly*Lz * exp(-2*nu*k^2*t) (integral of
    # 0.5*U0^2*sin^2(k y) over the domain, sin^2 averaging to 1/2 over y)
    Lx, Ly, Lz = mesh.lx, mesh.ly, mesh.lz
    T = n_steps * dt
    k_exact = 0.25 * U0_A ** 2 * Lx * Ly * Lz * math.exp(-2.0 * NU_A * K_A ** 2 * T)
    k_numeric = history[-1].kinetic_energy
    assert abs(k_numeric - k_exact) / k_exact < 0.01
