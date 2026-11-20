"""Milestone 7 Part N: failure handling.

The simulation must never silently continue after: pressure failure;
diffusion solve failure; NaN/Inf; dt below dt_min; impossible CFL
target; invalid preconditioner; incompatible solver/matrix selection.
Each is exercised here as an explicit, deliberately-triggered failure.
"""
import numpy as np
import pytest

from navier3d.adaptive import AdaptiveTimestepController, AdaptiveTimestepError
from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_velocity_bc,
)
from navier3d.diffusion import DiffusionSystemError, VelocityDiffusionSystem
from navier3d.fields import FlowState, VelocityField
from navier3d.linear_solvers import LinearSolverError
from navier3d.mesh import StructuredMesh3D
from navier3d.pressure import PressurePoissonSystem, PressureSystemError
from navier3d.time_integrators import IntegrationError, ThetaSchemeIntegrator, run

NX, NY, NZ = 6, 7, 5


def mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)


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


def random_state(m: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> FlowState:
    rng = np.random.default_rng(seed)
    state = FlowState.zeros(m)
    for comp in state.velocity.components():
        comp.interior = rng.uniform(-0.5, 0.5, size=comp.interior.shape)
    apply_velocity_bc(state.velocity, bcs)
    return state


# --------------------------------------------------------------------------
# 1. Pressure solve failure (non-convergence) -> IntegrationError
# --------------------------------------------------------------------------

def test_pressure_non_convergence_raises_integration_error_with_diagnostics() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(solver="cg", rhs_compatibility="mean_removal", tol=1e-14, max_iterations=1),
    )
    state = random_state(m, bcs, seed=1)
    with pytest.raises(IntegrationError, match="projection failed"):
        integrator.step(state)


# --------------------------------------------------------------------------
# 2. Diffusion solve failure (non-convergence) -> IntegrationError
# --------------------------------------------------------------------------

def test_diffusion_non_convergence_raises_integration_error_with_diagnostics() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
        diffusion_kwargs=dict(formulation="spd", solver="cg", rtol=1e-14, max_iterations=1),
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-8),
    )
    state = random_state(m, bcs, seed=2)
    with pytest.raises(IntegrationError, match="did not converge"):
        integrator.step(state)


# --------------------------------------------------------------------------
# 3. NaN/Inf never silently continued
# --------------------------------------------------------------------------

def test_nonfinite_forcing_raises_integration_error() -> None:
    m = mesh()
    bcs = periodic_bcs()

    def bad_forcing(t):
        f = VelocityField.zeros(m)
        f.u.interior[:] = np.nan
        return f

    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, forcing=bad_forcing,
        pressure_kwargs=dict(rhs_compatibility="mean_removal", tol=1e-10),
    )
    state = FlowState.zeros(m)
    with pytest.raises(IntegrationError, match="non-finite"):
        integrator.step(state)


# --------------------------------------------------------------------------
# 4/5. dt below dt_min / impossible CFL target (strict mode)
# --------------------------------------------------------------------------

def test_impossible_cfl_target_raises_under_strict_mode() -> None:
    m = mesh()
    v = VelocityField.zeros(m)
    v.u.interior[:] = 1e6  # runaway velocity
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-4, dt_max=1.0, strict=True)
    with pytest.raises(AdaptiveTimestepError, match="impossible CFL target"):
        controller.next_dt(v, m, dt_previous=1e-4)


def test_same_scenario_without_strict_mode_clamps_instead_of_raising() -> None:
    """Confirms strict=True is opt-in -- the non-strict default still
    clamps to dt_min (Part F's baseline, documented, non-failure
    behavior), so this is a genuine behavioral distinction, not two
    tests of the same thing."""
    m = mesh()
    v = VelocityField.zeros(m)
    v.u.interior[:] = 1e6
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-4, dt_max=1.0, strict=False)
    decision = controller.next_dt(v, m, dt_previous=1e-4)
    assert decision.dt == pytest.approx(1e-4)
    assert decision.limited_by == "dt_min"


# --------------------------------------------------------------------------
# 6. Invalid preconditioner
# --------------------------------------------------------------------------

def test_invalid_preconditioner_rejected_for_pressure() -> None:
    m = mesh()
    bcs = periodic_bcs()
    with pytest.raises(PressureSystemError, match="preconditioner"):
        PressurePoissonSystem(m, bcs, solver="cg", preconditioner="not_a_real_preconditioner", rhs_compatibility="mean_removal")


def test_invalid_preconditioner_rejected_for_diffusion() -> None:
    m = mesh()
    bcs = periodic_bcs()
    with pytest.raises(DiffusionSystemError, match="preconditioner"):
        VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=0.5, formulation="spd", preconditioner="not_a_real_preconditioner")


def test_amg_preconditioner_without_pyamg_raises_clear_error(monkeypatch) -> None:
    import navier3d.linear_solvers as ls
    monkeypatch.setattr(ls, "HAS_PYAMG", False)
    m = mesh()
    bcs = periodic_bcs()
    with pytest.raises(PressureSystemError, match="pyamg"):
        PressurePoissonSystem(m, bcs, solver="cg", preconditioner="amg", rhs_compatibility="mean_removal")


# --------------------------------------------------------------------------
# 7. Incompatible solver/matrix selection
# --------------------------------------------------------------------------

def test_cg_rejected_on_nonsymmetric_pinned_diffusion_matrix() -> None:
    m = mesh()
    bcs = periodic_bcs()
    with pytest.raises(DiffusionSystemError, match="not valid"):
        VelocityDiffusionSystem(m, bcs, 0, nu=0.1, dt=0.01, theta=0.5, formulation="pinned", solver="cg")


def test_direct_solver_rejected_with_zero_mean_singular_pressure_system() -> None:
    m = mesh()
    bcs = periodic_bcs()
    with pytest.raises(PressureSystemError):
        PressurePoissonSystem(m, bcs, solver="direct", null_space_strategy="zero_mean")


def test_linear_solver_error_message_includes_valid_alternatives() -> None:
    """The exception message itself should carry enough diagnostic
    information to know what WOULD have worked (the review: "Include
    solver diagnostics in the exception where possible")."""
    from navier3d.linear_solvers import create_linear_solver
    import scipy.sparse as sp

    A = sp.identity(5, format="csr")
    with pytest.raises(LinearSolverError) as exc_info:
        create_linear_solver(A, method="cg", matrix_kind="general")
    message = str(exc_info.value)
    assert "cg" in message
    assert "general" in message
    assert "direct" in message or "bicgstab" in message or "gmres" in message  # valid alternatives listed


# --------------------------------------------------------------------------
# Full-integrator run: a failure partway through never leaves the caller
# with a partially-advanced, silently-wrong state
# --------------------------------------------------------------------------

def test_run_loop_propagates_failure_without_swallowing_it() -> None:
    m = mesh()
    bcs = periodic_bcs()
    integrator = ThetaSchemeIntegrator(
        m, bcs, rho=1.0, nu=0.1, dt=0.01, theta=0.5, convection_scheme="centered",
        pressure_kwargs=dict(solver="cg", rhs_compatibility="mean_removal", tol=1e-14, max_iterations=1),
    )
    state = random_state(m, bcs, seed=9)
    with pytest.raises(IntegrationError):
        run(integrator, state, n_steps=10)
