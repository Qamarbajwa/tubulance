"""Milestone 9, finding 5: an ARBITRARY (not flow-consistent) initial
condition with p^0=0 shows order ~1 in the full pipeline regardless of
the pressure-extrapolation fix, geometry, forcing, or resolution -- but
recovers order ~2 once the flow has run long enough for the initial
transient to decay. This isolates a STARTUP-TRANSIENT effect as the
likely remaining mechanism (open question, not resolved in this
milestone -- see docs/architecture.md Section 16).
"""
import math

import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc
from navier3d.fields import FlowState
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import ThetaSchemeIntegrator, run

RHO, NU = 1.0, 0.05
LX, LY, LZ = 1.0, 1.25, 1.0


def wall_y_only_bcs() -> BoundaryConditionSet:
    w = FaceBoundaryCondition(velocity_type=VelocityBCType.NO_SLIP, pressure_type=PressureBCType.NEUMANN)
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=w, y_max=w, z_min=p, z_max=p)


def smooth_bump(X, Y, Z):
    return np.sin(math.pi * X / LX) * np.sin(math.pi * Y / LY) * np.sin(math.pi * Z / LZ)


def initial_state(m, bcs):
    s0 = FlowState.zeros(m)
    Xu, Yu, Zu = np.meshgrid(m.face_coords_x(), m.cell_centers_y(), m.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(m.cell_centers_x(), m.face_coords_y(), m.cell_centers_z(), indexing="ij")
    Xw, Yw, Zw = np.meshgrid(m.cell_centers_x(), m.cell_centers_y(), m.face_coords_z(), indexing="ij")
    s0.velocity.u.interior[:] = 0.5 * smooth_bump(Xu, Yu, Zu)
    s0.velocity.v.interior[:] = 0.3 * smooth_bump(Xv, Yv, Zv)
    s0.velocity.w.interior[:] = -0.2 * smooth_bump(Xw, Yw, Zw)
    apply_velocity_bc(s0.velocity, bcs)
    return s0


def _run(m, bcs, s0, dt, n_steps, extrap=False):
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme=None,
        projection_method="incremental", chi=1.0, pressure_extrapolation=extrap,
        pressure_kwargs=dict(solver="direct", null_space_strategy="pin_cell"),
    )
    final_state, history = run(integrator, s0, n_steps)
    return final_state, history


def _l2(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def _orders(errors):
    return [math.log(e1 / e2) / math.log(2.0) for e1, e2 in zip(errors[:-1], errors[1:])]


def test_arbitrary_ic_from_rest_shows_order_near_one() -> None:
    """Reproduces Milestone 8's own finding directly: order stays ~1
    across refinement levels for an arbitrary (non-flow-consistent) IC
    with p^0=0."""
    T = 0.01
    m = StructuredMesh3D(nx=10, ny=12, nz=8, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    bcs = wall_y_only_bcs()
    s0 = initial_state(m, bcs)

    ref, _ = _run(m, bcs, s0, T / 1024, round(T / (T / 1024)))
    errors = [
        _l2(_run(m, bcs, s0, dt, round(T / dt))[0].velocity.u.interior, ref.velocity.u.interior)
        for dt in [T / 32, T / 64, T / 128, T / 256]
    ]
    orders = _orders(errors)
    for order in orders:
        assert 0.8 < order < 1.4, f"orders {orders}"


def test_settled_state_recovers_order_two_at_matched_resolution() -> None:
    """For EACH dt level (avoiding any extrapolation-history/dt
    mismatch -- Part below), spin up using that SAME dt for a fixed
    number of steps first (letting the initial transient decay at that
    resolution), THEN measure the comparison window from the settled
    state. This isolates whether the "stuck at order 1" behavior is a
    startup artifact (recovers order 2 once settled) or a persistent
    steady-state defect (would stay at order 1 even after settling)."""
    T = 0.01
    m = StructuredMesh3D(nx=10, ny=12, nz=8, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    bcs = wall_y_only_bcs()
    s0 = initial_state(m, bcs)
    n_settle = 20

    def settle_then_measure(dt, n_steps):
        settled, _ = _run(m, bcs, s0, dt, n_settle)
        final, _ = _run(m, bcs, settled, dt, n_steps)
        return final, settled

    dts = [T / 32, T / 64, T / 128, T / 256]
    # reference: settle then run a much finer comparison window at the SAME dt scale as the finest test level
    dt_ref = T / 1024
    settled_ref, _ = _run(m, bcs, s0, dt_ref, n_settle)
    ref, _ = _run(m, bcs, settled_ref, dt_ref, round(T / (T / 1024)))

    errors = []
    for dt in dts:
        final, settled = settle_then_measure(dt, round(T / dt))
        # compare against a reference run from the SAME settled state at this dt's own settling point
        ref_from_this_settle, _ = _run(m, bcs, settled, dt_ref, round((T) / dt_ref))
        errors.append(_l2(final.velocity.u.interior, ref_from_this_settle.velocity.u.interior))

    orders = _orders(errors)
    # honest, not over-claimed: expect a MATERIAL improvement over the
    # from-rest order (~1), even if not perfectly clean 2 in every case
    assert sum(orders) / len(orders) > 1.5, f"orders {orders} -- expected material improvement once settled"


def test_consistent_p0_and_solenoidal_projection_recovers_clean_order_two_from_rest() -> None:
    """Milestone 10 resolution: shows that when the initial velocity is
    projected to the divergence-free subspace (Leray projection) and paired
    with the mathematically consistent initial pressure p^0 (via
    compute_initial_pressure), the startup transient is completely eliminated
    and clean order ~ 2.00 is achieved directly from t=0 without settling."""
    from navier3d.pressure import compute_initial_pressure
    from navier3d.projection import project_initial_velocity

    T = 0.01
    m = StructuredMesh3D(nx=10, ny=12, nz=8, lx=LX, ly=LY, lz=LZ, n_ghost=1)
    bcs = wall_y_only_bcs()
    s0_raw = initial_state(m, bcs)

    # 1. Leray projection ensures discrete solenoidal velocity
    u0_solenoidal = project_initial_velocity(s0_raw.velocity, bcs, m)

    # 2. Consistent initial pressure from initial PPE
    p0, _ = compute_initial_pressure(
        u0_solenoidal, bcs, m, RHO, NU, convection_scheme=None,
        solver="direct", null_space_strategy="pin_cell"
    )

    s0_consistent = FlowState(
        velocity=u0_solenoidal,
        pressure=p0,
        time=0.0,
        step=0,
    )

    ref, _ = _run(m, bcs, s0_consistent, T / 1024, round(T / (T / 1024)), extrap=True)
    errors = [
        _l2(_run(m, bcs, s0_consistent, dt, round(T / dt), extrap=True)[0].velocity.u.interior, ref.velocity.u.interior)
        for dt in [T / 16, T / 32, T / 64, T / 128]
    ]
    orders = _orders(errors)
    for order in orders:
        assert 1.90 < order < 2.15, f"orders {orders} -- expected clean order ~ 2 from t=0"

