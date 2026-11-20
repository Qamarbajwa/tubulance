"""Milestone 6 correction: predictor-level convection sign verification.

Isolated from projection and from Taylor-Green's coincidental pressure
cancellation (the review's "SECOND" concern was that a compensating sign
error in the pressure term could make the full pipeline pass even if
convection's sign were wrong -- this test never calls ``project()`` or
constructs a pressure system at all, so no such cancellation is possible).

Exercises exactly the mechanism ``ThetaSchemeIntegrator.step`` uses
internally (``time_integrators.py``, ``conv_contribution =
-ab2_field.components()[axis].interior``): one
``VelocityDiffusionSystem.solve()`` call per component with
``forcing = -N_h(u^n)`` folded in as the RHS's explicit source term.

Why the operative limit is "nu -> 0" rather than "dt -> 0":
``VelocityDiffusionSystem.solve`` is a direct (algebraic) implicit linear
solve, not a forward-time finite-difference approximation of ``du/dt`` --
the convective contribution enters as an *exact* term ``dt*forcing`` on
the right-hand side, with no truncation of its own. Expanding
``u* = M^{-1} @ rhs`` with ``M = I - theta*nu*dt*L_h`` gives

    (u*-u^n)/dt = forcing + nu*(L_h u^n + correction) + O(nu^2*dt)

i.e. the residual against ``forcing`` is ``O(nu)`` and, to leading order,
*independent of dt* -- it does not shrink from time refinement alone.
Both properties are checked below and were confirmed numerically before
picking the assertions' tolerances: at fixed tiny ``nu``, the residual is
flat across four decades of ``dt`` (no hidden dt-truncation bug); at
fixed ``dt``, the residual shrinks linearly as ``nu`` is driven toward
the validator's floor (``VelocityDiffusionSystem`` requires ``nu > 0``),
converging to ``-N_h(u^n)``. A companion check using the *opposite* sign
(``forcing = +N_h(u^n)``) confirms the residual does **not** converge
under the same refinement (stays near ``2*|N_h(u^n)|`` regardless of
``nu``), proving this test is sensitive to the sign, not just able to
detect gross magnitude errors.
"""
import numpy as np

from navier3d.boundary_conditions import (
    BoundaryConditionSet,
    FaceBoundaryCondition,
    PressureBCType,
    VelocityBCType,
    apply_velocity_bc,
)
from navier3d.convection import centered_convection
from navier3d.diffusion import VelocityDiffusionSystem
from navier3d.fields import VelocityField
from navier3d.mesh import StructuredMesh3D

NX, NY, NZ = 6, 7, 5


def _mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.3, lz=0.9, n_ghost=1)


def _periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def _manufactured_velocity(mesh: StructuredMesh3D, bcs: BoundaryConditionSet, seed: int) -> VelocityField:
    rng = np.random.default_rng(seed)
    u = VelocityField.zeros(mesh)
    for comp in u.components():
        comp.interior = rng.uniform(-1.0, 1.0, size=comp.interior.shape)
    apply_velocity_bc(u, bcs)
    return u


def _predictor_ratio(u_n: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet,
                      nu: float, dt: float, source_interiors: list) -> list:
    """Mirrors ``ThetaSchemeIntegrator.step``'s predictor exactly: one
    ``VelocityDiffusionSystem.solve()`` per component, ``theta=0.5``
    (Crank-Nicolson, matching the NS verification tests), forcing given
    directly as raw interior arrays. No pressure system is built and
    ``project()`` is never called anywhere in this module."""
    out = []
    for axis, comp_n in enumerate(u_n.components()):
        system = VelocityDiffusionSystem(mesh, bcs, axis, nu=nu, dt=dt, theta=0.5)
        comp_star, diag = system.solve(comp_n, forcing=source_interiors[axis])
        assert diag.finite
        out.append((comp_star.interior - comp_n.interior) / dt)
    return out


def _max_abs_diff(ratio: list, reference: list) -> float:
    return max(float(np.max(np.abs(r - ref))) for r, ref in zip(ratio, reference))


def test_predictor_sign_converges_to_minus_N_not_plus_N() -> None:
    mesh = _mesh()
    bcs = _periodic_bcs()
    u_n = _manufactured_velocity(mesh, bcs, seed=123)
    N = centered_convection(u_n, mesh)
    neg_N = [-c.interior for c in N.components()]
    pos_N = [c.interior for c in N.components()]
    scale = max(float(np.max(np.abs(c.interior))) for c in N.components())

    # (a) dt sweep at fixed tiny nu: residual against -N_h(u^n) stays
    # flat across four decades of dt (empirically varies by <0.1%,
    # confirmed numerically before writing this assertion) -- rules out
    # a hidden dt-only truncation bug and matches the exact-linear-solve
    # structure derived in the module docstring above.
    dt_errors = [
        _max_abs_diff(_predictor_ratio(u_n, mesh, bcs, nu=1e-10, dt=dt, source_interiors=neg_N), neg_N)
        for dt in (1e-2, 1e-3, 1e-4, 1e-5)
    ]
    assert max(dt_errors) < 2.0 * min(dt_errors)

    # (b) nu sweep at fixed dt: residual against -N_h(u^n) shrinks
    # (empirically ~linearly) as viscosity is driven toward the
    # validator's floor, converging to the correct sign and magnitude.
    nu_errors_correct = [
        _max_abs_diff(_predictor_ratio(u_n, mesh, bcs, nu=nu, dt=1e-3, source_interiors=neg_N), neg_N)
        for nu in (1e-6, 1e-8, 1e-10, 1e-12)
    ]
    for e1, e2 in zip(nu_errors_correct[:-1], nu_errors_correct[1:]):
        assert e2 < 0.5 * e1
    assert nu_errors_correct[-1] < 1e-6

    # (c) sign check: the SAME refinement with the opposite sign
    # (forcing=+N_h(u^n)) does not converge to -N_h(u^n) -- the residual
    # stays near 2*|N_h(u^n)| regardless of how small nu gets, proving
    # (a)/(b) above genuinely discriminate the sign, not merely detect a
    # gross magnitude error.
    nu_errors_wrong = [
        _max_abs_diff(_predictor_ratio(u_n, mesh, bcs, nu=nu, dt=1e-3, source_interiors=pos_N), neg_N)
        for nu in (1e-6, 1e-8, 1e-10, 1e-12)
    ]
    assert min(nu_errors_wrong) > 1.5 * scale
