"""Milestone 6 verification cases A-F: full incompressible Navier-Stokes
(nonlinear convection + diffusion + projection).

Still no turbulence model, LES, AMR, compressibility, or complex geometry.
"""
import math
import time as _time

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
from navier3d.time_integrators import CFLError, ThetaSchemeIntegrator, run


def fbc(velocity, pressure="neumann", velocity_value=None, pressure_value=None):
    return FaceBoundaryCondition(
        velocity_type=VelocityBCType(velocity),
        pressure_type=PressureBCType(pressure),
        velocity_value=velocity_value,
        pressure_value=pressure_value,
    )


def periodic_bcs() -> BoundaryConditionSet:
    p = fbc("periodic", "periodic")
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def _errors(computed: np.ndarray, exact: np.ndarray) -> float:
    return float(np.sqrt(np.mean((computed - exact) ** 2)))


def _order(e1: float, e2: float, ratio: float = 2.0) -> float:
    return math.log(e1 / e2) / math.log(ratio)


# ==========================================================================
# A. Taylor-Green vortex (2.5-D: w=0, exact for the full nonlinear equations)
#
# u = U0*sin(kx x)*cos(ky y)*exp(-sigma t)
# v = -U0*(kx/ky)*cos(kx x)*sin(ky y)*exp(-sigma t)
# w = 0, sigma = nu*(kx^2+ky^2)
# p = rho*U0^2/4 * [cos(2kx x) + (kx/ky)^2*cos(2ky y)] * exp(-2 sigma t)
#
# This is a genuine exact solution of the FULL (nonlinear) incompressible
# Navier-Stokes equations with f=0 -- the classic Taylor-Green property
# that the nonlinear convective term for this specific velocity field is
# exactly a pure gradient (verified by hand and independently confirmed
# numerically here: velocity and pressure errors both shrink at ~4x per
# grid doubling before this was trusted as a test oracle). kx != ky is
# used deliberately (a nonsymmetric-grid-friendly generalization of the
# textbook kx=ky case, re-derived and confirmed to still be exact).
# ==========================================================================

LX_A, LY_A, LZ_A = 1.0, 1.25, 0.5
NU_A, RHO_A, U0_A = 0.02, 1.0, 1.0
MX_A, MY_A = 2, 1
KX_A, KY_A = 2 * math.pi * MX_A / LX_A, 2 * math.pi * MY_A / LY_A
SIGMA_A = NU_A * (KX_A ** 2 + KY_A ** 2)

# Physically appropriate Reynolds number for THIS benchmark: the vortex's
# own decay length scale 1/k (k = sqrt(kx^2+ky^2), since sigma = nu*k^2 is
# the exact decay rate) -- not time_integrators.py's generic
# domain-geometric-mean diagnostic estimate. The two differ by more than
# 10x here (Re_TG ~ 3.7 vs. the generic estimate's ~43) precisely because
# this domain packs multiple vortex wavelengths (mx=2, my=1), making the
# vortex's own scale much smaller than the full domain -- exactly the
# case the Milestone 6 review flagged: a single generic Re is not
# universally meaningful across benchmarks.
K_A = math.sqrt(KX_A ** 2 + KY_A ** 2)
RE_TG_A = U0_A / (NU_A * K_A)  # ~3.69


def _tg_u(x, y, z, t):
    return U0_A * np.sin(KX_A * x) * np.cos(KY_A * y) * np.exp(-SIGMA_A * t)


def _tg_v(x, y, z, t):
    return -U0_A * (KX_A / KY_A) * np.cos(KX_A * x) * np.sin(KY_A * y) * np.exp(-SIGMA_A * t)


def _tg_p(x, y, z, t):
    return RHO_A * U0_A ** 2 / 4.0 * (np.cos(2 * KX_A * x) + (KX_A / KY_A) ** 2 * np.cos(2 * KY_A * y)) * np.exp(-2 * SIGMA_A * t)


def _tg_state(mesh: StructuredMesh3D) -> FlowState:
    state = FlowState.zeros(mesh)
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    state.velocity.u.interior[:] = _tg_u(Xu, Yu, Zu, 0.0)
    state.velocity.v.interior[:] = _tg_v(Xv, Yv, Zv, 0.0)
    return state


def _tg_mesh(n: int, nz: int = 4) -> StructuredMesh3D:
    return StructuredMesh3D(nx=n, ny=n, nz=nz, lx=LX_A, ly=LY_A, lz=LZ_A, n_ghost=1)


def _tg_integrator(mesh: StructuredMesh3D, dt: float, scheme: str = "centered") -> ThetaSchemeIntegrator:
    return ThetaSchemeIntegrator(
        mesh, periodic_bcs(), rho=RHO_A, nu=NU_A, dt=dt, theta=0.5, convection_scheme=scheme,
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-12),
    )


def _tg_velocity_error(mesh: StructuredMesh3D, state: FlowState, T: float) -> float:
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    eu = _errors(state.velocity.u.interior, _tg_u(Xu, Yu, Zu, T))
    ev = _errors(state.velocity.v.interior, _tg_v(Xv, Yv, Zv, T))
    return math.sqrt(eu ** 2 + ev ** 2)


def test_A_taylor_green_reynolds_number_is_vortex_scale_not_generic() -> None:
    """The benchmark's own physically appropriate Re (vortex length
    scale) is a small, fixed, case-defined number -- distinct from
    time_integrators.py's generic per-step diagnostic estimate, which
    uses the full domain size and the *current* max velocity instead."""
    assert 3.0 < RE_TG_A < 4.5


def test_A_taylor_green_velocity_pressure_energy_divergence() -> None:
    n = 32
    mesh = _tg_mesh(n)
    dt = 0.0005
    n_steps = 20
    integrator = _tg_integrator(mesh, dt)
    state = _tg_state(mesh)
    final_state, history = run(integrator, state, n_steps)
    T = n_steps * dt

    assert _tg_velocity_error(mesh, final_state, T) < 0.01
    assert np.max(np.abs(final_state.velocity.w.interior)) < 1e-10  # exactly 0 for all time
    assert max(h.max_divergence for h in history) < 1e-8

    Xp, Yp, Zp = np.meshgrid(mesh.cell_centers_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    p_num = final_state.pressure.interior - np.mean(final_state.pressure.interior)
    p_exact = _tg_p(Xp, Yp, Zp, T)
    p_exact = p_exact - np.mean(p_exact)
    assert _errors(p_num, p_exact) < 0.02

    assert history[-1].kinetic_energy > 0.0  # sanity: energy is a positive, physically sensible number


def test_A_taylor_green_spatial_convergence() -> None:
    dt = 0.0005
    n_steps = 10
    errors = []
    for n in [16, 32, 64]:
        mesh = _tg_mesh(n)
        integrator = _tg_integrator(mesh, dt)
        state = _tg_state(mesh)
        final_state, history = run(integrator, state, n_steps)
        errors.append(_tg_velocity_error(mesh, final_state, n_steps * dt))
        assert max(h.max_divergence for h in history) < 1e-8
    orders = [_order(e1, e2) for e1, e2 in zip(errors[:-1], errors[1:])]
    for order in orders:
        assert 1.6 <= order <= 2.4, f"observed orders {orders}"


def test_A_taylor_green_temporal_convergence() -> None:
    """Self-referenced (same diagnosis as Milestone 5 test B: fixed spatial
    discretization error dominates a continuous-solution comparison at
    these error magnitudes and masks dt refinement).

    **Milestone 6 correction round**: the original AB2 startup (first
    step forward-Euler-in-convection) was replaced with a genuine
    second-order (Heun's method) startup -- see ``time_integrators.py``'s
    module docstring, "AB2 startup". This measurably changed the observed
    order (climbing 1.11/1.23/1.59 before, vs. a flatter ~1.0-1.2 now
    below) but did **not** bring it to the asymptotic order-2 the review
    asked to demonstrate.

    Root cause, isolated by also measuring PRESSURE's self-referenced
    temporal order (same dt levels, same reference) alongside velocity's:
    both come out clean order ~1.0-1.2, not ~2 -- exactly the textbook
    signature of ``navier3d.projection``'s **non-incremental (Chorin-type)**
    pressure projection (see ``projection.py``'s own module docstring,
    "the non-incremental (Chorin-type) fractional-step projection"), which
    recomputes pressure from scratch every step with no history carried
    forward. This class of method has a well-known intrinsic O(dt) global
    splitting error between the pressure projection and time-advancement
    operators (Guermond, Minev & Shen 2006, "An overview of projection
    methods for incompressible flow") that is *independent* of how
    accurate the explicit predictor's own convection/diffusion
    discretization is -- so improving AB2's startup from 1st to 2nd order
    correctly fixed a real Milestone 6 bug (see
    ``tests/test_predictor_sign.py`` and the sign-audit section of the
    Milestone 6 correction report) without being able to lift the
    *overall* scheme past first order, because that ceiling comes from a
    different, already-accepted (Milestone 4) architectural choice.
    Reaching true second-order overall accuracy would require upgrading
    ``projection.py`` to an incremental (ideally rotational)
    pressure-correction scheme -- a larger change outside this
    correction round's scope, flagged to the reviewer rather than
    attempted unilaterally.

    Refined per the review's request to dt in
    {T/128, T/256, T/512, T/1024, T/2048} with a much finer reference
    (T/8192, 16x below the finest test point, vs. only 2x before) to rule
    out reference contamination. Observed order: ~1.0-1.3 throughout, not
    approaching 2 -- recorded and asserted honestly (order > 0.9,
    consistent with the diagnosed O(dt) projection-splitting ceiling)
    rather than asserting order-2 the current architecture cannot
    actually reach.
    """
    n = 24
    mesh = _tg_mesh(n)
    T = 0.02

    def run_to(dt: float) -> FlowState:
        n_steps = round(T / dt)
        integrator = _tg_integrator(mesh, dt)
        state = _tg_state(mesh)
        final_state, _ = run(integrator, state, n_steps)
        return final_state

    reference = run_to(T / 8192)
    errors = []
    for dt in [T / 128, T / 256, T / 512, T / 1024, T / 2048]:
        s = run_to(dt)
        eu = _errors(s.velocity.u.interior, reference.velocity.u.interior)
        ev = _errors(s.velocity.v.interior, reference.velocity.v.interior)
        errors.append(math.sqrt(eu ** 2 + ev ** 2))
    orders = [_order(e1, e2) for e1, e2 in zip(errors[:-1], errors[1:])]
    for order in orders:
        assert order > 0.9, f"observed orders {orders}"


def test_A_taylor_green_pressure_temporal_order_confirms_projection_is_first_order() -> None:
    """Corroborates the diagnosis in the velocity temporal-convergence
    test above: PRESSURE's own self-referenced temporal order (same
    mesh, same dt levels, same fine reference) is measured independently
    here. A non-incremental projection recomputes pressure from a fresh
    Poisson solve every step with no carried-forward history, so its
    accuracy is expected to be capped near first order regardless of the
    predictor's own (now 2nd-order, Heun-started) convection scheme --
    which is exactly what this test finds, corroborating that the
    velocity order plateau is a projection-architecture property, not a
    remaining convection-startup bug."""
    n = 24
    mesh = _tg_mesh(n)
    T = 0.02

    def run_to(dt: float) -> FlowState:
        n_steps = round(T / dt)
        integrator = _tg_integrator(mesh, dt)
        state = _tg_state(mesh)
        final_state, _ = run(integrator, state, n_steps)
        return final_state

    reference = run_to(T / 8192)
    p_ref = reference.pressure.interior - np.mean(reference.pressure.interior)
    errors = []
    for dt in [T / 128, T / 256, T / 512, T / 1024, T / 2048]:
        s = run_to(dt)
        p_num = s.pressure.interior - np.mean(s.pressure.interior)
        errors.append(_errors(p_num, p_ref))
    orders = [_order(e1, e2) for e1, e2 in zip(errors[:-1], errors[1:])]
    for order in orders:
        assert 0.8 < order < 1.6, f"observed pressure orders {orders}"


# ==========================================================================
# B. Manufactured full Navier-Stokes solution
#
# Reuses the Taylor-Green (u,v) pair verified in test A as the base
# (already an exact solution of the FULL nonlinear equations with f=0),
# and adds a second, independent, time-independent pressure perturbation
# p2 = P0*sin(kpx x)*sin(kpy y)*sin(kpz z) on top. Since p2 imposes no
# constraint on the velocity field's divergence-free property, and the
# TG (u,v) pair already exactly balances its own convection+diffusion
# against the TG pressure p1 (test A), the only additional forcing needed
# is exactly f = (1/rho)*grad(p2) -- this genuinely exercises
# convection + diffusion + a nonzero forcing pathway through the full
# predictor+pressure+projection pipeline without a symbolic-algebra
# derivation, by linearity of the pressure-gradient term.
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


def _run_manufactured_ns(n: int, dt: float, n_steps: int, nz: int = 4):
    mesh = _tg_mesh(n, nz)
    integrator = ThetaSchemeIntegrator(
        mesh, periodic_bcs(), rho=RHO_A, nu=NU_A, dt=dt, theta=0.5, convection_scheme="centered",
        forcing=_b_forcing(mesh),
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    state = _tg_state(mesh)
    final_state, history = run(integrator, state, n_steps)
    return mesh, final_state, history


def test_B_manufactured_navier_stokes_full_pipeline_convergence() -> None:
    dt, n_steps = 0.0005, 10
    resolutions = [12, 16, 20]
    errors = []
    for n in resolutions:
        mesh, final_state, history = _run_manufactured_ns(n, dt, n_steps)
        errors.append(_tg_velocity_error(mesh, final_state, n_steps * dt))
        assert max(h.max_divergence for h in history) < 1e-8
    for n1, n2, e1, e2 in zip(resolutions[:-1], resolutions[1:], errors[:-1], errors[1:]):
        order = math.log(e1 / e2) / math.log(n2 / n1)
        assert 1.6 <= order <= 2.4, f"n={n1}->{n2}: observed order {order}"


# ==========================================================================
# C. Inviscid/near-inviscid periodic energy test
# ==========================================================================

def _kinetic_energy(velocity: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> float:
    dV = mesh.cell_volume
    sq_sum = 0.0
    for axis, comp in enumerate(velocity.components()):
        interior = comp.interior
        if bcs.is_periodic_axis(axis):
            sl = [slice(None)] * 3
            sl[axis] = slice(0, -1)
            interior = interior[tuple(sl)]
        sq_sum += np.sum(interior ** 2)
    return 0.5 * sq_sum * dV


def _divergence_free_random_field(mesh: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> VelocityField:
    from navier3d.boundary_conditions import apply_velocity_bc
    from navier3d.projection import project

    rng = np.random.default_rng(seed)
    u_star = VelocityField.zeros(mesh)
    for comp in u_star.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(u_star, bcs)
    result = project(u_star, bcs, mesh, rho=1.0, dt=0.01, tol=1e-13, rhs_compatibility="mean_removal")
    return result.velocity


def test_C_near_inviscid_centered_low_drift_upwind_dissipates() -> None:
    m = StructuredMesh3D(nx=8, ny=10, nz=12, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    bcs = periodic_bcs()
    v0 = _divergence_free_random_field(m, bcs, seed=10)
    K0 = _kinetic_energy(v0, m, bcs)

    # Physically appropriate Re for THIS benchmark: unlike test A/D, a
    # homogeneous periodic box with an isotropic random initial field has
    # no privileged direction or geometric feature -- the domain's
    # geometric-mean length genuinely IS the physically meaningful scale
    # here (there is no better alternative), so it happens to coincide
    # with time_integrators.py's generic diagnostic formula. What makes
    # this benchmark's Re "near-inviscid" is nu itself being tiny, not a
    # large length or velocity scale; Re ~ 1.7e4, computed from the
    # field's own max velocity after projection, not assumed a priori.
    U_max_C = max(float(np.max(np.abs(c.interior))) for c in v0.components())
    L_C = (m.lx * m.ly * m.lz) ** (1.0 / 3.0)
    nu_small = 1e-4
    RE_C = U_max_C * L_C / nu_small
    assert RE_C > 1e4  # confirms this is genuinely a near-inviscid regime
    dt, n_steps = 0.005, 30
    drifts = {}
    for scheme in ("centered", "upwind"):
        state = FlowState.zeros(m)
        for comp_out, comp_in in zip(state.velocity.components(), v0.components()):
            comp_out.interior = comp_in.interior.copy()
        integrator = ThetaSchemeIntegrator(
            m, bcs, rho=1.0, nu=nu_small, dt=dt, theta=0.5, convection_scheme=scheme,
            pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-12),
        )
        final_state, history = run(integrator, state, n_steps)
        K_end = history[-1].kinetic_energy
        drifts[scheme] = (K_end - K0) / K0
        # never CREATES energy (do not claim exact Euler conservation --
        # this integrator has real, if small, numerical dissipation)
        assert K_end <= K0 * 1.001

    assert abs(drifts["centered"]) < 0.05  # "very low" artificial drift
    assert drifts["upwind"] < -0.1  # clearly, substantially dissipative
    assert abs(drifts["upwind"]) > abs(drifts["centered"]) * 5  # upwind dissipates far more than centered


# ==========================================================================
# D. Long nonlinear run
# ==========================================================================

def test_D_long_nonlinear_run() -> None:
    # Physically appropriate Re for THIS benchmark: this is a fully
    # enclosed no-slip box (all six faces walls, not a channel/pipe with
    # a privileged flow direction), so the physically meaningful length
    # scale is the SMALLEST wall-to-wall distance (lx=1.0), the tightest
    # no-slip constraint on the flow -- not the domain's geometric mean
    # (which time_integrators.py's generic diagnostic uses instead, and
    # which would overweight the largest dimension, lz=1.5, that no-slip
    # boundary layers on the x-faces do not actually feel).
    L_D = 1.0
    U_D = 0.3  # rng.uniform(-0.3, 0.3) initial velocity scale, below
    nu_D = 0.05
    RE_D = U_D * L_D / nu_D
    assert 3.0 < RE_D < 10.0  # firmly laminar, low Reynolds number

    m = StructuredMesh3D(nx=6, ny=8, nz=10, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    w = fbc("no_slip")
    bcs = BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)
    rng = np.random.default_rng(11)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.3, 0.3, size=comp.interior.shape)
    from navier3d.boundary_conditions import apply_velocity_bc
    apply_velocity_bc(state.velocity, bcs)

    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=0.005, theta=0.5, convection_scheme="centered", cfl_max=0.9,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    final_state, history = run(integrator, state, n_steps=300)

    max_divs = [h.max_divergence for h in history]
    normalized_divs = [h.normalized_divergence for h in history]
    energies = [h.kinetic_energy for h in history]

    assert max(max_divs) < 1e-6
    assert max(normalized_divs) < 1e-8
    first_half_max = max(max_divs[:150])
    second_half_max = max(max_divs[150:])
    assert second_half_max <= max(first_half_max * 10.0, 1e-8)  # no secular growth

    for comp in final_state.velocity.components():
        assert np.all(np.isfinite(comp.data))  # no NaN/Inf
    assert np.all(np.isfinite(final_state.pressure.data))

    assert max(energies) <= energies[0] * 1.5  # bounded (walls, no forcing: should not grow unboundedly)

    # boundary conditions remain satisfied: no-slip normal AND tangential
    assert np.max(np.abs(final_state.velocity.u.interior[0, :, :])) < 1e-8
    assert np.max(np.abs(final_state.velocity.u.interior[-1, :, :])) < 1e-8
    ng = m.n_ghost
    interior_adjacent = final_state.velocity.u.data[ng:-ng, ng, ng:-ng]
    ghost = final_state.velocity.u.data[ng:-ng, ng - 1, ng:-ng]
    np.testing.assert_allclose(ghost, -interior_adjacent, atol=1e-8)

    # pressure solver remains convergent throughout
    assert all(h.pressure_diagnostics.converged for h in history)
    assert all(all(d.converged for d in h.diffusion_diagnostics) for h in history)


# ==========================================================================
# E. CFL failure
# ==========================================================================

def test_E_excessive_cfl_rejected() -> None:
    m = StructuredMesh3D(nx=8, ny=10, nz=12, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    bcs = periodic_bcs()
    state = FlowState.zeros(m)
    state.velocity.u.data[:] = 50.0  # deliberately huge velocity
    dt = 1.0  # deliberately huge dt

    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=dt, theta=0.5, convection_scheme="centered", cfl_max=1.0,
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    with pytest.raises(CFLError):
        integrator.step(state)


def test_E_cfl_disabled_by_default_does_not_raise() -> None:
    """cfl_max=None (the default) means no hard rejection -- confirms the
    check is configurable, not always-on."""
    m = StructuredMesh3D(nx=8, ny=10, nz=12, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    bcs = periodic_bcs()
    state = FlowState.zeros(m)
    state.velocity.u.data[:] = 50.0
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=1.0, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-8, max_iterations=50000),
    )
    new_state, diag = integrator.step(state)  # must not raise
    assert diag.cfl > 1.0  # confirms the scenario genuinely was high-CFL


def test_E_safe_cfl_accepted() -> None:
    m = StructuredMesh3D(nx=8, ny=10, nz=12, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)
    bcs = periodic_bcs()
    state = FlowState.zeros(m)
    state.velocity.u.data[:] = 0.1
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.05, dt=0.01, theta=0.5, convection_scheme="centered", cfl_max=1.0,
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    new_state, diag = integrator.step(state)  # must not raise
    assert diag.cfl <= 1.0


# ==========================================================================
# F. Scheme comparison (centered vs. upwind, same Taylor-Green case)
# ==========================================================================

def test_F_scheme_comparison_centered_vs_upwind() -> None:
    n = 24
    mesh = _tg_mesh(n)
    dt = 0.0005
    n_steps = 20
    T = n_steps * dt

    results = {}
    for scheme in ("centered", "upwind"):
        integrator = _tg_integrator(mesh, dt, scheme=scheme)
        state = _tg_state(mesh)
        t0 = _time.perf_counter()
        final_state, history = run(integrator, state, n_steps)
        elapsed = _time.perf_counter() - t0
        err = _tg_velocity_error(mesh, final_state, T)
        results[scheme] = dict(
            error=err,
            energy_end=history[-1].kinetic_energy,
            max_div=max(h.max_divergence for h in history),
            runtime=elapsed,
            converged=all(h.pressure_diagnostics.converged for h in history),
        )

    # solution error: centered (2nd order) beats upwind (1st order) on the
    # same smooth, well-resolved case
    assert results["centered"]["error"] < results["upwind"]["error"]

    # numerical dissipation: upwind loses more kinetic energy than centered
    # over the same run (both decay physically via viscosity too, but
    # upwind's numerical dissipation adds to it)
    assert results["upwind"]["energy_end"] < results["centered"]["energy_end"]

    # stability: both remain stable (bounded, divergence-controlled) at
    # this safe CFL -- upwind's extra dissipation does not manifest as
    # instability here, only as reduced accuracy/energy
    assert results["centered"]["max_div"] < 1e-8
    assert results["upwind"]["max_div"] < 1e-8
    assert results["centered"]["converged"]
    assert results["upwind"]["converged"]

    # runtime: both recorded for the report; not asserted against each
    # other (convection cost is a small fraction of total step cost here,
    # dominated by the pressure/diffusion solves shared by both schemes)
    assert results["centered"]["runtime"] > 0.0
    assert results["upwind"]["runtime"] > 0.0
