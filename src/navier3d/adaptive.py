"""Adaptive timestep control (Milestone 7 Part F) and variable-step AB2
extrapolation coefficients (Part G).

Kept as small, independently testable pure functions/classes -- neither
depends on :mod:`navier3d.time_integrators`; that module *uses* both, so
they can be verified in isolation (a CFL-arithmetic bug and an AB2-
coefficient bug are unrelated failure modes and should not be conflated
in one test).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .boundary_conditions import BoundaryConditionSet
from .fields import VelocityField
from .mesh import StructuredMesh3D


class AdaptiveTimestepError(ValueError):
    """Raised for invalid :class:`AdaptiveTimestepController` configuration."""


@dataclass
class DtDecision:
    """One :meth:`AdaptiveTimestepController.next_dt` call's result."""

    dt: float
    cfl: float  # CFL number the CHOSEN dt actually produces (not the target)
    cfl_candidate_dt: float  # dt that would exactly hit cfl_target, pre-clipping
    diffusive_number: Optional[float]
    limited_by: str  # "cfl" | "growth" | "shrink" | "dt_min" | "dt_max"


class AdaptiveTimestepController:
    """CFL-driven adaptive ``dt`` selection with configurable safety and
    growth/shrink limits (Milestone 7 Part F).

    ```
    dt_cfl = cfl_target / (max|u|/dx + max|v|/dy + max|w|/dz + eps)
    dt_candidate = safety * dt_cfl
    dt_next = clip(dt_candidate, shrink_max*dt_previous, growth_max*dt_previous)
    dt_next = clip(dt_next, dt_min, dt_max)
    ```

    For an all-zero velocity field (the ``max|.|`` sum is exactly 0),
    ``dt_cfl`` would be a division by zero; this is handled explicitly by
    returning ``dt_max`` directly in that case (never NaN/Inf, never a
    negative dt -- the review's explicit requirement) rather than relying
    on a small epsilon to paper over it (an epsilon-based fallback would
    still technically avoid ZeroDivisionError but would produce a
    physically meaningless, arbitrarily huge ``dt_cfl`` that then gets
    clipped anyway -- returning ``dt_max`` directly is the same outcome,
    reached honestly).

    ``strict`` (Milestone 7 Part N, "dt below dt_min"/"impossible CFL
    target" must never be silently continued past): when ``True``,
    :meth:`next_dt` raises :class:`AdaptiveTimestepError` instead of
    silently clamping to ``dt_min`` whenever the safety-scaled CFL-
    optimal candidate ``dt`` falls *below* ``dt_min`` -- i.e. the
    velocity has become fast enough (most likely a runaway instability)
    that hitting ``cfl_target`` would require a smaller step than
    ``dt_min`` permits at all: an "impossible CFL target" under the
    current configuration, not a routine, safe clamp. Default ``False``
    reproduces plain clamping (Part F's baseline behavior) for callers
    that intentionally want ``dt_min`` as a hard floor with no exception
    path -- e.g. a deliberately conservative floor the caller is fine
    running at even if it means exceeding ``cfl_target`` somewhat.
    """

    def __init__(
        self,
        *,
        cfl_target: float,
        dt_min: float,
        dt_max: float,
        safety: float = 0.9,
        growth_max: float = 1.2,
        shrink_max: float = 0.5,
        strict: bool = False,
    ) -> None:
        if cfl_target <= 0.0:
            raise AdaptiveTimestepError(f"cfl_target must be positive, got {cfl_target!r}")
        if dt_min <= 0.0:
            raise AdaptiveTimestepError(f"dt_min must be positive, got {dt_min!r}")
        if dt_max < dt_min:
            raise AdaptiveTimestepError(f"dt_max ({dt_max!r}) must be >= dt_min ({dt_min!r})")
        if not (0.0 < safety <= 1.0):
            raise AdaptiveTimestepError(f"safety must be in (0, 1], got {safety!r}")
        if growth_max < 1.0:
            raise AdaptiveTimestepError(f"growth_max must be >= 1.0, got {growth_max!r}")
        if not (0.0 < shrink_max <= 1.0):
            raise AdaptiveTimestepError(f"shrink_max must be in (0, 1], got {shrink_max!r}")

        self.cfl_target = cfl_target
        self.dt_min = dt_min
        self.dt_max = dt_max
        self.safety = safety
        self.growth_max = growth_max
        self.shrink_max = shrink_max
        self.strict = strict

    def next_dt(
        self,
        velocity: VelocityField,
        mesh: StructuredMesh3D,
        dt_previous: float,
        nu: Optional[float] = None,
    ) -> DtDecision:
        """Compute the next timestep from the current velocity field's
        CFL number. ``dt_previous`` anchors the growth/shrink-factor
        limits (so ``dt`` never jumps by more than ``growth_max``x or
        drops below ``shrink_max``x in a single call, regardless of what
        the raw CFL-optimal ``dt`` would suggest). ``nu``, if given,
        additionally reports the diffusive-number diagnostic (see class
        docstring) -- it does **not** influence the chosen ``dt`` (Crank-
        Nicolson/backward-Euler diffusion is unconditionally stable; see
        the review's Part F, "no strict explicit diffusive stability
        limit is required")."""
        if dt_previous <= 0.0:
            raise AdaptiveTimestepError(f"dt_previous must be positive, got {dt_previous!r}")

        spacings = (mesh.dx, mesh.dy, mesh.dz)
        total = 0.0
        for comp, d in zip(velocity.components(), spacings):
            total += float(np.max(np.abs(comp.interior))) / d

        if total <= 0.0:
            # No CFL constraint at all for a zero velocity field -- the
            # safety margin exists to stay clear of a stability limit
            # that, here, does not apply; return dt_max directly (still
            # subject to the growth/shrink/dt_min/dt_max clipping below).
            dt_cfl = self.dt_max
            candidate = self.dt_max
        else:
            dt_cfl = self.cfl_target / total
            candidate = self.safety * dt_cfl
        if self.strict and candidate < self.dt_min:
            raise AdaptiveTimestepError(
                f"impossible CFL target: hitting cfl_target={self.cfl_target!r} would need "
                f"dt={candidate:.6e}, below dt_min={self.dt_min!r} (current CFL-driving speed "
                f"sum={total!r}); this is not a routine clamp -- raised under strict=True instead "
                f"of silently continuing at an under-resolved CFL"
            )

        hi = self.growth_max * dt_previous
        lo = self.shrink_max * dt_previous
        dt = min(max(candidate, lo), hi)
        dt = min(max(dt, self.dt_min), self.dt_max)

        if not math.isfinite(dt) or dt <= 0.0:
            # Unreachable given the clipping above (dt_min > 0 is always
            # a finite positive floor), but checked explicitly per the
            # review's "must never produce NaN/Inf or negative dt".
            raise AdaptiveTimestepError(f"computed dt={dt!r} is not a finite positive number")

        limited_by = "cfl"
        for name, bound in (("dt_min", self.dt_min), ("dt_max", self.dt_max), ("growth", hi), ("shrink", lo)):
            if math.isclose(dt, bound, rel_tol=1e-9, abs_tol=1e-15):
                limited_by = name
                break

        diffusive_number = None
        if nu is not None:
            diffusive_number = nu * dt * (1.0 / mesh.dx ** 2 + 1.0 / mesh.dy ** 2 + 1.0 / mesh.dz ** 2)

        cfl_actual = dt * total
        return DtDecision(dt=dt, cfl=cfl_actual, cfl_candidate_dt=dt_cfl, diffusive_number=diffusive_number, limited_by=limited_by)


def variable_step_ab2_coefficients(dt_current: float, dt_previous: float) -> tuple:
    """Second-order Adams-Bashforth extrapolation coefficients for
    **unequal** step sizes (Milestone 7 Part G).

    Derivation: fit the linear polynomial through the two known samples
    ``(t_{n-1}, N^{n-1})`` and ``(t_n, N^n)``,

    ```
    N(t) ~= N^n + (N^n - N^{n-1})/dt_previous * (t - t_n)
    ```

    and integrate it over the *upcoming* interval ``[t_n, t_n+dt_current]``
    to approximate ``integral_{t_n}^{t_n+dt_current} N(t) dt``:

    ```
    integral ~= dt_current * N^n + (N^n-N^{n-1})/dt_previous * dt_current^2/2
             = dt_current * [ (1 + r/2)*N^n - (r/2)*N^{n-1} ],   r = dt_current/dt_previous
    ```

    So the AB2 "effective" convective term used in the predictor (in
    place of the constant-step ``3/2*N^n - 1/2*N^{n-1}``) is

    ```
    N_ab2 = (1 + r/2)*N^n - (r/2)*N^{n-1}
    ```

    which reduces to the textbook constant-step coefficients exactly at
    ``r=1``: ``(1+1/2, -1/2) = (3/2, -1/2)``. Returns ``(c_current,
    c_previous)`` such that ``N_ab2 = c_current*N^n + c_previous*N^{n-1}``.
    """
    if dt_current <= 0.0:
        raise ValueError(f"dt_current must be positive, got {dt_current!r}")
    if dt_previous <= 0.0:
        raise ValueError(f"dt_previous must be positive, got {dt_previous!r}")
    r = dt_current / dt_previous
    return 1.0 + 0.5 * r, -0.5 * r


def pressure_extrapolation_coefficients(dt_current: float, dt_previous: float, theta: float) -> tuple:
    """Milestone 9: linear-in-time extrapolation of a lagged history
    variable (here, pressure) to the theta-scheme's own evaluation time
    ``t^n + theta*dt_current`` -- the fix for the root cause Milestone 9
    isolated (``docs/architecture.md`` Section 16): using ``p^n`` (i.e.
    ``theta=0`` treatment) directly in a theta=0.5 (Crank-Nicolson)
    predictor is only *first-order* accurate in time for that term,
    capping the whole scheme's temporal order at 1 regardless of how
    good the projection step itself is -- confirmed by a controlled,
    isolated (diffusion + predictor only, no projection) experiment on a
    manufactured wall-bounded unsteady Stokes solution: exact pressure
    at ``t^n`` gives order 1.05; exact pressure at the true
    ``t^{n+theta}`` gives order 2.00; this extrapolation (using only
    ``p^n`` and ``p^{n-1}``, no knowledge of the future) also gives
    order 2.00.

    Derivation: fit the line through ``(t_{n-1}, p^{n-1})`` and
    ``(t_n, p^n)`` and evaluate it at ``t_n + theta*dt_current``:

    ```
    p(t) ~= p^n + (p^n - p^{n-1})/dt_previous * (t - t_n)
    p_extrap = p^n + theta*r*(p^n - p^{n-1}),   r = dt_current/dt_previous
             = (1 + theta*r)*p^n - (theta*r)*p^{n-1}
    ```

    At constant step (``r=1``) and Crank-Nicolson (``theta=0.5``):
    ``p_extrap = 1.5*p^n - 0.5*p^{n-1}`` -- structurally the *same*
    formula as :func:`variable_step_ab2_coefficients` at ``theta=0.5``,
    though derived independently here (this one is parametrized by
    ``theta`` since it targets the theta-scheme's own evaluation point,
    not a fixed midpoint). Returns ``(c_current, c_previous)`` such that
    ``p_extrap = c_current*p^n + c_previous*p^{n-1}``.
    """
    if dt_current <= 0.0:
        raise ValueError(f"dt_current must be positive, got {dt_current!r}")
    if dt_previous <= 0.0:
        raise ValueError(f"dt_previous must be positive, got {dt_previous!r}")
    if not (0.0 < theta <= 1.0):
        raise ValueError(f"theta must be in (0, 1], got {theta!r}")
    r = dt_current / dt_previous
    return 1.0 + theta * r, -theta * r
