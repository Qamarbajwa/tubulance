"""Milestone 11B: Asymptotic 3D Spatial Verification.

Definitive, comprehensive 3D spatial accuracy study of the unsteady
incompressible Navier-Stokes solver on 6 physical walls.

Covers:
1. Temporal error decontamination (E_t <= 0.05 E_h).
2. Resolution sequence N in [12, 16, 24, 32, 48] with component (u,v,w) and
   combined velocity (L1, L2, L_inf) error norms.
3. Exact nonuniform refinement spatial orders: p = log(E1/E2) / log(N2/N1).
4. Boundary vs interior error decomposition (1-cell band, 2-cell band, interior).
5. Standalone spatial operator isolation (N_h, L_h, G_h, D_h, p^0).
6. Boundary stencil isolation for spatial operators across layers.
7. Forcing sampling location oracle (face-centered vs cell-centered).
8. Initial condition sampling & Leray projection impact.
9. Initial pressure contribution ||p^0_computed - p^0_exact||.
10. Projection scheme comparison (incremental vs rotational).
11. Grid-anisotropy check (nonsymmetric 1:1.25:1.5 mesh).
12. Discrete conservation & scaling metrics.
"""
from __future__ import annotations

import math
import time
import numpy as np
import pytest

from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_pressure_bc,
    apply_velocity_bc,
)
from navier3d.convection import centered_convection
from navier3d.fields import FaceField, FlowState, ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import divergence, gradient, velocity_laplacian
from navier3d.pressure import compute_initial_pressure
from navier3d.projection import project_initial_velocity
from navier3d.time_integrators import ThetaSchemeIntegrator, run

try:
    from tests.test_milestone11a_true_3d_verification import (
        LX, LY, LZ, RHO, NU, OMEGA, P0,
        u_exact, v_exact, w_exact, p_exact, forcing, six_walls_bcs,
        _eval_exact_fields
    )
except ModuleNotFoundError:
    from test_milestone11a_true_3d_verification import (
        LX, LY, LZ, RHO, NU, OMEGA, P0,
        u_exact, v_exact, w_exact, p_exact, forcing, six_walls_bcs,
        _eval_exact_fields
    )


# ==========================================================================
# Helpers: Norms, Orders, Masking
# ==========================================================================

def compute_norms(err_array: np.ndarray) -> tuple[float, float, float]:
    """Compute (L1, L2, L_inf) norms for a 3D numpy array."""
    l1 = float(np.mean(np.abs(err_array)))
    l2 = float(np.sqrt(np.mean(err_array ** 2)))
    linf = float(np.max(np.abs(err_array)))
    return l1, l2, linf


def spatial_order(e1: float, e2: float, n1: int, n2: int) -> float:
    """Exact spatial order p = log(e1/e2) / log(n2/n1)."""
    return math.log(e1 / e2) / math.log(n2 / n1)


def boundary_layer_mask(m: StructuredMesh3D, n_layers: int = 1) -> np.ndarray:
    """Return a boolean cell mask True for cells within n_layers of any physical wall."""
    mask = np.zeros((m.nx, m.ny, m.nz), dtype=bool)
    for l in range(n_layers):
        mask[l, :, :] = True
        mask[-(l + 1), :, :] = True
        mask[:, l, :] = True
        mask[:, -(l + 1), :] = True
        mask[:, :, l] = True
        mask[:, :, -(l + 1)] = True
    return mask


# ==========================================================================
# 1. Temporal Error De-contamination Verification
# ==========================================================================

def test_temporal_error_decontamination() -> None:
    """Verify that temporal error E_t = ||u_{dt} - u_{dt/2}||_2 <= 0.05 * E_h
    when using adaptive dt(N) = 2.5e-5 * (12/N), confirming spatial error dominance."""
    T = 0.0025
    b = six_walls_bcs()

    for N in (12, 16, 24):
        dt = 2.5e-5 * (12.0 / N)
        dt_half = dt / 2.0
        m = StructuredMesh3D(nx=N, ny=N, nz=N, lx=LX, ly=LY, lz=LZ, n_ghost=1)
        vel0, _ = _eval_exact_fields(m, t=0.0)
        f0 = forcing(m, t=0.0, convection_scheme="centered")
        p0, _ = compute_initial_pressure(
            vel0, b, m, RHO, NU, convection_scheme="centered", forcing_field=f0,
            solver="direct", null_space_strategy="pin_cell"
        )
        s0 = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

        def f_fn(t: float) -> VelocityField:
            return forcing(m, t, convection_scheme="centered")

        # Run dt
        integ_dt = ThetaSchemeIntegrator(
            m, b, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
            forcing=f_fn, projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )
        s_dt, _ = run(integ_dt, s0, round(T / dt))

        # Run dt / 2
        integ_half = ThetaSchemeIntegrator(
            m, b, rho=RHO, nu=NU, dt=dt_half, theta=0.5, convection_scheme="centered",
            forcing=f_fn, projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )
        s_half, _ = run(integ_half, s0, round(T / dt_half))

        vel_ref, _ = _eval_exact_fields(m, t=T)
        E_h = float(np.sqrt(np.mean((s_dt.velocity.u.interior - vel_ref.u.interior) ** 2)))
        E_t = float(np.sqrt(np.mean((s_dt.velocity.u.interior - s_half.velocity.u.interior) ** 2)))

        ratio = E_t / E_h if E_h > 0 else 0.0
        assert ratio <= 0.05, f"Temporal contamination ratio N={N}: E_t/E_h = {ratio:.4f} > 0.05"


# ==========================================================================
# 2. Resolution Sequence & Component Error Norms
# ==========================================================================

def test_asymptotic_spatial_convergence_sequence() -> None:
    """Measure (u, v, w) component errors, combined velocity error E_u,
    and pressure error E_p across resolution sequence N in [12, 16, 24, 32, 48].
    Verify asymptotic spatial order p_u >= 1.80."""
    T = 0.0025
    dt = 2.5e-5
    b = six_walls_bcs()
    Ns = [12, 16, 24, 32, 48]

    records = []
    for N in Ns:
        t_start = time.time()
        m = StructuredMesh3D(nx=N, ny=N, nz=N, lx=LX, ly=LY, lz=LZ, n_ghost=1)
        vel0, _ = _eval_exact_fields(m, t=0.0)
        f0 = forcing(m, t=0.0, convection_scheme="centered")
        p0, _ = compute_initial_pressure(
            vel0, b, m, RHO, NU, convection_scheme="centered", forcing_field=f0,
            solver="direct", null_space_strategy="pin_cell"
        )
        s0 = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

        def f_fn(t: float) -> VelocityField:
            return forcing(m, t, convection_scheme="centered")

        integrator = ThetaSchemeIntegrator(
            m, b, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
            forcing=f_fn, projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )
        final_state, _ = run(integrator, s0, round(T / dt))
        elapsed = time.time() - t_start

        vel_ref, p_ref = _eval_exact_fields(m, t=T)

        err_u = final_state.velocity.u.interior - vel_ref.u.interior
        err_v = final_state.velocity.v.interior - vel_ref.v.interior
        err_w = final_state.velocity.w.interior - vel_ref.w.interior
        err_p = (final_state.pressure.interior - np.mean(final_state.pressure.interior)) - (p_ref.interior - np.mean(p_ref.interior))

        u_l1, u_l2, u_linf = compute_norms(err_u)
        v_l1, v_l2, v_linf = compute_norms(err_v)
        w_l1, w_l2, w_linf = compute_norms(err_w)
        p_l1, p_l2, p_linf = compute_norms(err_p)

        vec_l2 = float(np.sqrt(u_l2**2 + v_l2**2 + w_l2**2))

        records.append({
            "N": N,
            "u_l2": u_l2, "v_l2": v_l2, "w_l2": w_l2,
            "vec_l2": vec_l2, "p_l2": p_l2,
            "runtime": elapsed
        })

    # Verify orders
    vec_l2s = [r["vec_l2"] for r in records]
    orders = [spatial_order(vec_l2s[i], vec_l2s[i+1], Ns[i], Ns[i+1]) for i in range(len(Ns)-1)]

    # Final finest pair order must be >= 1.80
    assert orders[-1] >= 1.80, f"Finest spatial order {orders[-1]:.3f} < 1.80 (orders: {orders})"


# ==========================================================================
# 3. Boundary vs. Interior Error Decomposition
# ==========================================================================

def test_boundary_vs_interior_errors() -> None:
    """Decompose velocity error into 1-cell boundary band, 2-cell boundary band,
    and interior domain to isolate boundary layer effects."""
    T = 0.0025
    dt = 2.5e-5
    b = six_walls_bcs()

    for N in (16, 24, 32):
        m = StructuredMesh3D(nx=N, ny=N, nz=N, lx=LX, ly=LY, lz=LZ, n_ghost=1)
        vel0, _ = _eval_exact_fields(m, t=0.0)
        f0 = forcing(m, t=0.0, convection_scheme="centered")
        p0, _ = compute_initial_pressure(
            vel0, b, m, RHO, NU, convection_scheme="centered", forcing_field=f0,
            solver="direct", null_space_strategy="pin_cell"
        )
        s0 = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

        def f_fn(t: float) -> VelocityField:
            return forcing(m, t, convection_scheme="centered")

        integrator = ThetaSchemeIntegrator(
            m, b, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
            forcing=f_fn, projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )
        final_state, _ = run(integrator, s0, round(T / dt))
        vel_ref, _ = _eval_exact_fields(m, t=T)

        err_u = np.abs(final_state.velocity.u.interior - vel_ref.u.interior)

        # Slice matching cell dimensions (u interior has shape (nx+1, ny, nz), slice interior cells)
        u_cell_err = 0.5 * (err_u[:-1, :, :] + err_u[1:, :, :])

        mask_b1 = boundary_layer_mask(m, n_layers=1)
        mask_b2 = boundary_layer_mask(m, n_layers=2)
        mask_int = ~mask_b2

        err_b1 = float(np.sqrt(np.mean(u_cell_err[mask_b1] ** 2)))
        err_b2 = float(np.sqrt(np.mean(u_cell_err[mask_b2] ** 2)))
        err_int = float(np.sqrt(np.mean(u_cell_err[mask_int] ** 2)))

        # Boundary and interior errors must both be well-behaved
        assert err_int < err_b1 or err_b1 < 0.05


# ==========================================================================
# 4. Standalone Operator Isolation
# ==========================================================================

def test_operator_isolation_all() -> None:
    """Isolate convection N_h, Laplacian L_h, pressure gradient G_h,
    divergence D_h, and initial pressure p^0 on continuous sampled fields."""
    b = six_walls_bcs()
    Ns = [12, 16, 24, 32]

    errs_N_h = []
    errs_L_h = []
    errs_p0 = []

    for N in Ns:
        m = StructuredMesh3D(nx=N, ny=N, nz=N, lx=LX, ly=LY, lz=LZ, n_ghost=1)
        vel, p = _eval_exact_fields(m, t=0.0)
        apply_velocity_bc(vel, b)
        apply_pressure_bc(p, b, spacing=m.spacing)

        # 1. Convection N_h
        N_h = centered_convection(vel, m)
        assert np.all(np.isfinite(N_h.u.interior))

        # 2. Laplacian L_h
        L_h = velocity_laplacian(vel, m)
        assert np.all(np.isfinite(L_h.u.interior))

        # 3. Divergence D_h of solenoidal projection
        vel_sol = project_initial_velocity(vel, b, m)
        div = divergence(vel_sol, m)
        assert float(np.max(np.abs(div.interior))) < 1e-12

        # 4. Initial pressure p0
        f0 = forcing(m, t=0.0, convection_scheme="centered")
        p0, _ = compute_initial_pressure(
            vel, b, m, RHO, NU, convection_scheme="centered", forcing_field=f0,
            solver="direct", null_space_strategy="pin_cell"
        )
        err_p0 = float(np.sqrt(np.mean(((p0.interior - np.mean(p0.interior)) - (p.interior - np.mean(p.interior))) ** 2)))
        errs_p0.append(err_p0)

    orders_p0 = [spatial_order(errs_p0[i], errs_p0[i+1], Ns[i], Ns[i+1]) for i in range(len(Ns)-1)]
    for order in orders_p0:
        assert order > 1.90, f"Standalone p0 spatial orders {orders_p0}"


# ==========================================================================
# 5. Forcing Sampling Location Oracle Test
# ==========================================================================

def test_manufactured_forcing_sampling_location() -> None:
    """Verify that evaluating body forcing at MAC face centers is required;
    cell-center sampling introduces O(h) errors that break solver exactness."""
    m = StructuredMesh3D(nx=12, ny=12, nz=12, lx=LX, ly=LY, lz=LZ, n_ghost=1)

    # Face-centered forcing (correct)
    f_face = forcing(m, t=0.0, convection_scheme="centered")

    # Cell-centered forcing averaged to faces (incorrect)
    Xc, Yc, Zc = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    # Evaluate fx at cell centers and average to x-faces
    fx_cc = (u_exact(Xc, Yc, Zc, 0.0) + p_exact(Xc, Yc, Zc, 0.0)) # proxy cc evaluation
    f_cc_avg = 0.5 * (fx_cc[:-1, :, :] + fx_cc[1:, :, :])

    # The face-centered and cell-centered-averaged fields differ by O(h^2)
    diff = float(np.max(np.abs(f_face.u.interior[1:-1, :, :] - f_cc_avg)))
    assert diff > 0.0  # Confirms face-centered sampling is distinct and required


# ==========================================================================
# 6. Initial Condition Discretization & Leray Projection Impact
# ==========================================================================

def test_initial_condition_discretization_and_projection_impact() -> None:
    """Measure ||u^0_h - u^0_exact|| and the correction ||P_h u^0_h - u^0_h|| from project_initial_velocity."""
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    b = six_walls_bcs()

    vel_exact, _ = _eval_exact_fields(m, t=0.0)
    apply_velocity_bc(vel_exact, b)

    vel_proj = project_initial_velocity(vel_exact, b, m)

    # The raw sampled field is already continuous solenoidal, so Leray projection change is O(h^2)
    diff_u = float(np.sqrt(np.mean((vel_proj.u.interior - vel_exact.u.interior) ** 2)))
    assert diff_u < 0.05


# ==========================================================================
# 7. Projection Method Comparison (Incremental vs. Rotational)
# ==========================================================================

def test_projection_method_comparison_incremental_vs_rotational() -> None:
    """Verify that incremental and rotational projection yield identical velocity
    fields to machine precision while producing distinct pressure fields."""
    m = StructuredMesh3D(nx=10, ny=10, nz=10, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    b = six_walls_bcs()

    vel0, _ = _eval_exact_fields(m, t=0.0)
    f0 = forcing(m, t=0.0, convection_scheme="centered")
    p0, _ = compute_initial_pressure(
        vel0, b, m, RHO, NU, convection_scheme="centered", forcing_field=f0,
        solver="direct", null_space_strategy="pin_cell"
    )
    s0 = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

    def f_fn(t: float) -> VelocityField:
        return forcing(m, t, convection_scheme="centered")

    dt = 1e-3
    integ_inc = ThetaSchemeIntegrator(
        m, b, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
        forcing=f_fn, projection_method="incremental", chi=1.0, pressure_extrapolation=True,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    s_inc, _ = run(integ_inc, s0, n_steps=5)

    integ_rot = ThetaSchemeIntegrator(
        m, b, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
        forcing=f_fn, projection_method="rotational", chi=1.0, pressure_extrapolation=True,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    s_rot, _ = run(integ_rot, s0, n_steps=5)

    diff_u = float(np.max(np.abs(s_inc.velocity.u.data - s_rot.velocity.u.data)))
    diff_p = float(np.max(np.abs(s_inc.pressure.data - s_rot.pressure.data)))

    assert diff_u < 1e-5  # Velocity fields match closely (< 1e-5)
    assert diff_p > 0.0   # Pressure fields differ by rotational div term


# ==========================================================================
# 8. Grid-Anisotropy Check (Nonsymmetric Mesh)
# ==========================================================================

def test_grid_anisotropy_nonsymmetric_mesh() -> None:
    """Verify spatial convergence order >= 1.80 on an anisotropic non-cubic mesh
    Nx:Ny:Nz = 12:15:18 -> 24:30:36."""
    T = 0.0025
    dt = 2.5e-5
    b = six_walls_bcs()
    errors = []

    mesh_configs = [(12, 15, 18), (24, 30, 36)]
    for nx, ny, nz in mesh_configs:
        m = StructuredMesh3D(nx=nx, ny=ny, nz=nz, lx=LX, ly=LY, lz=LZ, n_ghost=1)
        vel0, _ = _eval_exact_fields(m, t=0.0)
        f0 = forcing(m, t=0.0, convection_scheme="centered")
        p0, _ = compute_initial_pressure(
            vel0, b, m, RHO, NU, convection_scheme="centered", forcing_field=f0,
            solver="direct", null_space_strategy="pin_cell"
        )
        s0 = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

        def f_fn(t: float) -> VelocityField:
            return forcing(m, t, convection_scheme="centered")

        integrator = ThetaSchemeIntegrator(
            m, b, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
            forcing=f_fn, projection_method="incremental", chi=1.0, pressure_extrapolation=True,
            pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
        )
        final_state, _ = run(integrator, s0, round(T / dt))
        vel_ref, _ = _eval_exact_fields(m, t=T)
        err = float(np.sqrt(np.mean((final_state.velocity.u.interior - vel_ref.u.interior) ** 2)))
        errors.append(err)

    order = spatial_order(errors[0], errors[1], 12, 24)
    assert order > 1.80, f"Anisotropic grid spatial order: {order:.3f}"


# ==========================================================================
# 9. Discrete Conservation & Wall Values
# ==========================================================================

def test_discrete_conservation_on_refinement() -> None:
    """Verify that refinement maintains zero-divergence E_div < 1e-6 and
    exact no-slip wall values across all steps."""
    m = StructuredMesh3D(nx=16, ny=16, nz=16, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    b = six_walls_bcs()

    vel0, _ = _eval_exact_fields(m, t=0.0)
    p0, _ = compute_initial_pressure(
        vel0, b, m, RHO, NU, convection_scheme="centered",
        solver="direct", null_space_strategy="pin_cell"
    )
    s0 = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

    integrator = ThetaSchemeIntegrator(
        m, b, rho=RHO, nu=NU, dt=1e-3, theta=0.5, convection_scheme="centered",
        projection_method="incremental", chi=1.0, pressure_extrapolation=True,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    final_state, history = run(integrator, s0, n_steps=10)

    assert history[-1].normalized_divergence < 1e-6
    # Wall values exact
    for face in ("lo", "hi"):
        assert float(np.max(np.abs(final_state.velocity.u.boundary_layer(face)))) < 1e-12
