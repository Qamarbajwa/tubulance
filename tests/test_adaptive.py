"""Tests for navier3d.adaptive: AdaptiveTimestepController,
variable_step_ab2_coefficients."""
import math

import numpy as np
import pytest

from navier3d.adaptive import (
    AdaptiveTimestepController,
    AdaptiveTimestepError,
    variable_step_ab2_coefficients,
)
from navier3d.mesh import StructuredMesh3D
from navier3d.fields import VelocityField

NX, NY, NZ = 4, 5, 6


def mesh() -> StructuredMesh3D:
    return StructuredMesh3D(nx=NX, ny=NY, nz=NZ, lx=1.0, ly=1.25, lz=1.5, n_ghost=1)


def velocity_with_speed(speed: float) -> VelocityField:
    m = mesh()
    v = VelocityField.zeros(m)
    v.u.interior[:] = speed
    return v


# --------------------------------------------------------------------------
# AdaptiveTimestepController: construction validation
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kwargs", [
    dict(cfl_target=0.0), dict(cfl_target=-1.0),
    dict(dt_min=0.0), dict(dt_min=-1.0),
    dict(dt_max=0.001, dt_min=0.01),
    dict(safety=0.0), dict(safety=1.5),
    dict(growth_max=0.5),
    dict(shrink_max=0.0), dict(shrink_max=1.5),
])
def test_invalid_construction_rejected(kwargs) -> None:
    base = dict(cfl_target=0.5, dt_min=1e-6, dt_max=1.0, safety=0.9, growth_max=1.2, shrink_max=0.5)
    base.update(kwargs)
    with pytest.raises(AdaptiveTimestepError):
        AdaptiveTimestepController(**base)


# --------------------------------------------------------------------------
# Zero velocity -> dt_max, never divide by zero
# --------------------------------------------------------------------------

def test_zero_velocity_returns_dt_max() -> None:
    """With growth/shrink limits effectively disabled (huge growth_max,
    tiny shrink_max), a zero-velocity field's CFL-optimal dt is
    unconstrained -> the controller reports dt_max directly, not a
    division-by-zero artifact."""
    m = mesh()
    v = VelocityField.zeros(m)
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-5, dt_max=0.1, growth_max=1e6, shrink_max=1e-6)
    decision = controller.next_dt(v, m, dt_previous=0.01)
    assert decision.dt == pytest.approx(0.1)
    assert math.isfinite(decision.dt)
    assert decision.dt > 0.0


def test_zero_velocity_still_growth_limited() -> None:
    """dt_max is a ceiling, but the growth-factor limit still applies on
    top of it -- a single call cannot jump dt arbitrarily even toward an
    unconstrained dt_max."""
    m = mesh()
    v = VelocityField.zeros(m)
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-5, dt_max=100.0, growth_max=1.2)
    decision = controller.next_dt(v, m, dt_previous=0.01)
    assert decision.dt == pytest.approx(0.012, rel=1e-6)  # 1.2 * 0.01
    assert decision.limited_by == "growth"


# --------------------------------------------------------------------------
# Never NaN/Inf/negative
# --------------------------------------------------------------------------

def test_never_nan_inf_or_negative_across_wide_speed_range() -> None:
    m = mesh()
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-8, dt_max=10.0, growth_max=2.0, shrink_max=0.1)
    dt_prev = 0.01
    for speed in [0.0, 1e-10, 1e-3, 1.0, 1e3, 1e8]:
        v = velocity_with_speed(speed)
        decision = controller.next_dt(v, m, dt_previous=dt_prev)
        assert math.isfinite(decision.dt)
        assert decision.dt > 0.0
        dt_prev = decision.dt


# --------------------------------------------------------------------------
# Safety / growth / shrink limits
# --------------------------------------------------------------------------

def test_high_speed_shrinks_but_not_below_shrink_max() -> None:
    m = mesh()
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-8, dt_max=1.0, shrink_max=0.5)
    v = velocity_with_speed(1e6)  # huge speed -> CFL-optimal dt is tiny
    decision = controller.next_dt(v, m, dt_previous=0.01)
    assert decision.dt == pytest.approx(0.005, rel=1e-6)  # 0.5 * 0.01
    assert decision.limited_by == "shrink"


def test_low_speed_grows_but_not_above_growth_max() -> None:
    m = mesh()
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-8, dt_max=1.0, growth_max=1.2)
    v = velocity_with_speed(1e-9)  # tiny speed -> CFL-optimal dt is huge
    decision = controller.next_dt(v, m, dt_previous=0.01)
    assert decision.dt == pytest.approx(0.012, rel=1e-6)
    assert decision.limited_by == "growth"


def test_moderate_speed_hits_cfl_target_unclipped() -> None:
    m = mesh()
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-8, dt_max=10.0, safety=1.0, growth_max=1e6, shrink_max=1e-6)
    v = velocity_with_speed(1.0)
    dx = m.dx
    expected_dt = 0.5 * dx  # cfl_target / (speed/dx) = cfl_target*dx/speed
    # dt_previous set near the expected result so growth/shrink factors
    # (already set very permissive above) genuinely don't bind either
    decision = controller.next_dt(v, m, dt_previous=expected_dt)
    assert decision.dt == pytest.approx(expected_dt, rel=1e-6)
    assert decision.limited_by == "cfl"
    assert decision.cfl == pytest.approx(0.5, rel=1e-6)


def test_dt_min_and_dt_max_are_hard_floors_and_ceilings() -> None:
    m = mesh()
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=0.02, dt_max=0.03, growth_max=100.0, shrink_max=0.0001)
    v_fast = velocity_with_speed(1e6)
    decision_fast = controller.next_dt(v_fast, m, dt_previous=0.025)
    assert decision_fast.dt == pytest.approx(0.02)
    assert decision_fast.limited_by == "dt_min"

    v_slow = velocity_with_speed(1e-9)
    decision_slow = controller.next_dt(v_slow, m, dt_previous=0.025)
    assert decision_slow.dt == pytest.approx(0.03)
    assert decision_slow.limited_by == "dt_max"


# --------------------------------------------------------------------------
# Diffusive-number diagnostic
# --------------------------------------------------------------------------

def test_diffusive_number_reported_when_nu_given() -> None:
    m = mesh()
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-6, dt_max=1.0)
    v = velocity_with_speed(0.5)
    decision = controller.next_dt(v, m, dt_previous=0.01, nu=0.1)
    expected = 0.1 * decision.dt * (1.0 / m.dx ** 2 + 1.0 / m.dy ** 2 + 1.0 / m.dz ** 2)
    assert decision.diffusive_number == pytest.approx(expected)


def test_diffusive_number_none_when_nu_omitted() -> None:
    m = mesh()
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-6, dt_max=1.0)
    v = velocity_with_speed(0.5)
    decision = controller.next_dt(v, m, dt_previous=0.01)
    assert decision.diffusive_number is None


def test_invalid_dt_previous_rejected() -> None:
    m = mesh()
    controller = AdaptiveTimestepController(cfl_target=0.5, dt_min=1e-6, dt_max=1.0)
    v = velocity_with_speed(0.5)
    with pytest.raises(AdaptiveTimestepError):
        controller.next_dt(v, m, dt_previous=0.0)


# ==========================================================================
# Variable-step AB2 coefficients (Part G)
# ==========================================================================

def test_constant_step_recovers_standard_ab2_coefficients() -> None:
    c_current, c_previous = variable_step_ab2_coefficients(dt_current=0.01, dt_previous=0.01)
    assert c_current == pytest.approx(1.5)
    assert c_previous == pytest.approx(-0.5)


@pytest.mark.parametrize("r", [0.5, 2.0, 0.1, 10.0])
def test_coefficients_match_closed_form(r: float) -> None:
    c_current, c_previous = variable_step_ab2_coefficients(dt_current=r * 0.01, dt_previous=0.01)
    assert c_current == pytest.approx(1.0 + r / 2.0)
    assert c_previous == pytest.approx(-r / 2.0)


def test_rejects_nonpositive_dt() -> None:
    with pytest.raises(ValueError):
        variable_step_ab2_coefficients(dt_current=0.0, dt_previous=0.01)
    with pytest.raises(ValueError):
        variable_step_ab2_coefficients(dt_current=0.01, dt_previous=0.0)


def _quadratic_N(t: float, a: float, b: float, c: float) -> float:
    return a + b * t + c * t * t


def _exact_integral(t0: float, t1: float, a: float, b: float, c: float) -> float:
    def antideriv(t):
        return a * t + b * t * t / 2.0 + c * t ** 3 / 3.0
    return antideriv(t1) - antideriv(t0)


def test_polynomial_manufactured_linear_N_is_exact() -> None:
    """N(t) linear in t: the AB2 linear extrapolant IS N(t) exactly, so
    the approximation should match the true integral to roundoff for ANY
    step sizes (r != 1 included) -- a necessary sanity check before
    trusting the quadratic (genuine order) test below."""
    a, b, c = 2.0, -3.0, 0.0  # c=0: purely linear
    t_prev, dt_previous, dt_current = 1.3, 0.05, 0.12  # r = 2.4, deliberately != 1
    t_n = t_prev + dt_previous
    N_prev = _quadratic_N(t_prev, a, b, c)
    N_n = _quadratic_N(t_n, a, b, c)
    c_cur, c_pre = variable_step_ab2_coefficients(dt_current, dt_previous)
    approx_integral = dt_current * (c_cur * N_n + c_pre * N_prev)
    exact = _exact_integral(t_n, t_n + dt_current, a, b, c)
    assert approx_integral == pytest.approx(exact, abs=1e-12)


def test_polynomial_manufactured_quadratic_N_local_truncation_is_third_order() -> None:
    """N(t) quadratic in t (nonzero third derivative of the integral is
    absent since N itself is only degree 2 -- but the LINEAR
    extrapolant's mismatch against a genuinely quadratic N is what
    produces the expected O(h^3) local truncation error of a 2nd-order
    multistep formula). Holding r fixed and shrinking both step sizes by
    a factor `scale`, the truncation error should shrink by
    `scale^3` (confirmed empirically here, not merely asserted)."""
    a, b, c = 1.0, 0.5, 3.0
    r = 1.7  # deliberately non-constant-step
    t_prev = 0.4

    def local_error(scale: float) -> float:
        dt_previous = 0.1 * scale
        dt_current = r * dt_previous
        t_n = t_prev + dt_previous
        N_prev = _quadratic_N(t_prev, a, b, c)
        N_n = _quadratic_N(t_n, a, b, c)
        c_cur, c_pre = variable_step_ab2_coefficients(dt_current, dt_previous)
        approx_integral = dt_current * (c_cur * N_n + c_pre * N_prev)
        exact = _exact_integral(t_n, t_n + dt_current, a, b, c)
        return abs(approx_integral - exact)

    scales = [1.0, 0.5, 0.25, 0.125]
    errors = [local_error(s) for s in scales]
    for e_coarse, e_fine in zip(errors[:-1], errors[1:]):
        ratio = e_coarse / e_fine
        assert 7.0 < ratio < 9.0, f"expected ~8x (order 3 local) per halving, got {ratio}"
