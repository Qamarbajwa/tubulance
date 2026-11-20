"""Milestone 8 Part 8: Taylor-Green vortex re-run with all three
projection methods.

**Documents and verifies a real, provable mathematical property**: on a
*periodic*, uniform-spacing domain, the incremental/rotational
predictor's added term ``-(1/rho)*G_h(p^n)`` is itself always a pure
discrete gradient (because the per-component theta-scheme diffusion
operator and the discrete gradient commute in the periodic Fourier
basis -- same eigenvalue at each physical wavenumber for every velocity
component, since the finite-difference stencil is identical up to a
staggered-grid phase shift). A pure-gradient contamination of the
predictor is *exactly* removed by the projection step regardless of its
magnitude, so the FINAL CORRECTED VELOCITY is bit-for-bit-approximately
identical across all three projection methods on any periodic case,
including Taylor-Green -- verified directly below. This is not a defect
or a missed opportunity for improvement; it is why the boundary-sensitive
tests (``test_milestone8_temporal_convergence.py``,
``test_milestone8_boundary_sensitive.py``) use wall-bounded domains
instead, where this commutation argument does not hold.
"""
import math

import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.fields import FlowState
from navier3d.mesh import StructuredMesh3D
from navier3d.time_integrators import ThetaSchemeIntegrator, run

LX, LY, LZ = 1.0, 1.25, 0.5
NU, RHO, U0 = 0.02, 1.0, 1.0
MX, MY = 2, 1
KX, KY = 2 * math.pi * MX / LX, 2 * math.pi * MY / LY
SIGMA = NU * (KX ** 2 + KY ** 2)
METHODS = ["non_incremental", "incremental", "rotational"]


def _tg_u(x, y, z, t):
    return U0 * np.sin(KX * x) * np.cos(KY * y) * np.exp(-SIGMA * t)


def _tg_v(x, y, z, t):
    return -U0 * (KX / KY) * np.cos(KX * x) * np.sin(KY * y) * np.exp(-SIGMA * t)


def _tg_p(x, y, z, t):
    return RHO * U0 ** 2 / 4.0 * (np.cos(2 * KX * x) + (KX / KY) ** 2 * np.cos(2 * KY * y)) * np.exp(-2 * SIGMA * t)


def _mesh(n: int = 20, nz: int = 4) -> StructuredMesh3D:
    return StructuredMesh3D(nx=n, ny=n, nz=nz, lx=LX, ly=LY, lz=LZ, n_ghost=1)


def _periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def _state(mesh: StructuredMesh3D) -> FlowState:
    state = FlowState.zeros(mesh)
    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    state.velocity.u.interior[:] = _tg_u(Xu, Yu, Zu, 0.0)
    state.velocity.v.interior[:] = _tg_v(Xv, Yv, Zv, 0.0)
    return state


def _run(method: str, mesh: StructuredMesh3D, dt: float, n_steps: int):
    bcs = _periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        mesh, bcs, rho=RHO, nu=NU, dt=dt, theta=0.5, convection_scheme="centered",
        projection_method=method, chi=1.0,
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-12),
    )
    state = _state(mesh)
    final_state, history = run(integrator, state, n_steps)
    return final_state, history


@pytest.mark.parametrize("method", METHODS)
def test_taylor_green_accuracy_unchanged_by_projection_method(method: str) -> None:
    """The already-verified Milestone 6 spatial/temporal behavior is not
    degraded by any projection method."""
    mesh = _mesh(24)
    dt = 0.0005
    n_steps = 20
    T = n_steps * dt
    final_state, history = _run(method, mesh, dt, n_steps)

    Xu, Yu, Zu = np.meshgrid(mesh.face_coords_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij")
    Xv, Yv, Zv = np.meshgrid(mesh.cell_centers_x(), mesh.face_coords_y(), mesh.cell_centers_z(), indexing="ij")
    eu = np.sqrt(np.mean((final_state.velocity.u.interior - _tg_u(Xu, Yu, Zu, T)) ** 2))
    ev = np.sqrt(np.mean((final_state.velocity.v.interior - _tg_v(Xv, Yv, Zv, T)) ** 2))
    assert math.sqrt(eu ** 2 + ev ** 2) < 0.01
    assert max(h.max_divergence for h in history) < 1e-8
    assert np.max(np.abs(final_state.velocity.w.interior)) < 1e-10


def test_velocity_identical_across_all_three_methods_on_periodic_domain() -> None:
    """The key documented finding: periodic domains cannot distinguish
    the three projection methods at the velocity level."""
    mesh = _mesh(20)
    dt = 0.0005
    n_steps = 15
    results = {method: _run(method, mesh, dt, n_steps)[0] for method in METHODS}

    ref = results["non_incremental"]
    for method in ("incremental", "rotational"):
        for c_ref, c_other in zip(ref.velocity.components(), results[method].velocity.components()):
            np.testing.assert_allclose(c_other.interior, c_ref.interior, atol=1e-9)


def test_kinetic_energy_identical_across_methods_on_periodic_domain() -> None:
    mesh = _mesh(20)
    dt = 0.0005
    n_steps = 15
    energies = {}
    for method in METHODS:
        _, history = _run(method, mesh, dt, n_steps)
        energies[method] = history[-1].kinetic_energy
    assert energies["incremental"] == pytest.approx(energies["non_incremental"], rel=1e-8)
    assert energies["rotational"] == pytest.approx(energies["non_incremental"], rel=1e-8)


def test_pressure_differs_between_methods_even_though_velocity_matches() -> None:
    """Pressure (unlike velocity) is NOT invariant across methods on a
    periodic domain -- only its GRADIENT contribution to the predictor
    is a pure-gradient artifact that gets projected away; the returned
    pressure FIELD itself is a genuinely different quantity (full field
    vs. accumulated increments) between non_incremental and
    incremental/rotational."""
    mesh = _mesh(20)
    dt = 0.0005
    n_steps = 15
    results = {}
    for method in METHODS:
        final, _ = _run(method, mesh, dt, n_steps)
        results[method] = final.pressure.interior - np.mean(final.pressure.interior)
    assert not np.allclose(results["non_incremental"], results["incremental"], atol=1e-6)


def test_runtime_recorded_for_all_three_methods() -> None:
    """Not asserted against each other (see performance comparison test
    module for that) -- just confirms all three run and report timing."""
    mesh = _mesh(16)
    dt = 0.0005
    n_steps = 10
    for method in METHODS:
        _, history = _run(method, mesh, dt, n_steps)
        assert history[-1].elapsed_time > 0.0
        assert history[-1].pressure_diagnostics.solve_time >= 0.0
