"""
Milestone 5.7: explicit forcing state and forcing-dominance diagnostics
=========================================================================

The terminal-layer model through Milestone 5.5 treats forcing only as an
unconfirmed wavenumber ceiling (`Config.forcing_kmax`) used solely to check
scale separation from the terminal layer. This module adds the explicit
forcing state

    F = {P_f, k_f, tau_f, d_f, C_f, B_f}

described in the Milestone 5.7 specification, plus the three central
dimensionless diagnostics used throughout the stress test:

    Phi_l   = P_f(l) / (u_l^3 / l)      forcing-dominance ratio
    Theta_f = tau_f / tau_l             forcing/structure timescale ratio
    A_f     = (u . f) / (|u| |f|)       local forcing alignment

This module does not run anything -- it only defines the forcing state and
the diagnostics computed from it. See pseudo_spectral_solver.py for how a
ForcingState is turned into an actual spectral source term, and
forcing_test_matrix.py for the preregistered set of ForcingState instances
used by the stress test.

Phi_l classification thresholds are configurable, not hard-coded, per the
"never set a threshold before seeing the distribution" discipline in
AGENTS.md. The defaults below (0.1, 10) are a reasonable diagnostic
starting point for separating nonlinear_dominated / competing /
forcing_dominated regimes -- not a claim about where the true crossover
lies for this model.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

FORCING_TYPES = (
    "isotropic_random",
    "fixed_direction",
    "rotating_direction",
    "periodic",
    "pulsed",
    "impulsive",
    "narrow_band",
    "broad_band",
    "small_scale",
    "multi_scale",
)

# Forcing types whose spectral support is meant to span more than one
# injection wavenumber (multi_scale forces at several k_f simultaneously;
# broad_band widens the shell band around a single k_f). Everything else is
# treated as single-scale for the purposes of Phi_l/Theta_f bookkeeping.
MULTI_SCALE_TYPES = frozenset({"multi_scale"})


class ForcingConfigError(ValueError):
    """Raised when a ForcingState is constructed with an invalid or
    incomplete parameter combination."""


@dataclass(frozen=True)
class ForcingState:
    """F = {P_f, k_f, tau_f, d_f, C_f, B_f, forcing_type}.

    power_input           P_f     target injected power (mean <u.f>), >= 0
    injection_wavenumber  k_f     center wavenumber of the forcing band, > 0
    timescale             tau_f   forcing correlation/oscillation timescale, > 0
    direction             d_f     preferred unit direction; None => isotropic
    spatial_coherence     C_f     in [0,1]; 0 = fully isotropic random phase,
                                   1 = fully aligned with `direction`
    temporal_coherence           in [0,1]; 0 = phase re-randomized every
                                   step, 1 = phase frozen across steps
    bandwidth              B_f    shell half-width (in wavenumber units)
                                   around k_f (or around each entry of
                                   extra_wavenumbers for multi_scale)
    forcing_type                  one of FORCING_TYPES
    extra_wavenumbers             additional injection wavenumbers, used
                                   only by forcing_type="multi_scale"
    """

    power_input: float
    injection_wavenumber: float
    timescale: float
    direction: tuple[float, float, float] | None = None
    spatial_coherence: float = 1.0
    temporal_coherence: float = 1.0
    bandwidth: float = 1.0
    forcing_type: str = "isotropic_random"
    extra_wavenumbers: tuple[float, ...] = ()

    def __post_init__(self):
        if self.forcing_type not in FORCING_TYPES:
            raise ForcingConfigError(
                f"unknown forcing_type {self.forcing_type!r}; must be one of {FORCING_TYPES}"
            )
        if self.power_input < 0:
            raise ForcingConfigError("power_input must be >= 0")
        if self.injection_wavenumber <= 0:
            raise ForcingConfigError("injection_wavenumber must be > 0")
        if self.timescale <= 0:
            raise ForcingConfigError("timescale must be > 0")
        if self.bandwidth <= 0:
            raise ForcingConfigError("bandwidth must be > 0")
        if not (0.0 <= self.spatial_coherence <= 1.0):
            raise ForcingConfigError("spatial_coherence must be in [0,1]")
        if not (0.0 <= self.temporal_coherence <= 1.0):
            raise ForcingConfigError("temporal_coherence must be in [0,1]")
        if self.forcing_type in ("fixed_direction", "rotating_direction") and self.direction is None:
            raise ForcingConfigError(f"forcing_type={self.forcing_type!r} requires `direction` to be set")
        if self.forcing_type == "multi_scale" and len(self.extra_wavenumbers) == 0:
            raise ForcingConfigError("forcing_type='multi_scale' requires extra_wavenumbers")
        for k in self.extra_wavenumbers:
            if k <= 0:
                raise ForcingConfigError("extra_wavenumbers entries must be > 0")

    @property
    def injection_wavenumbers(self) -> tuple[float, ...]:
        """All wavenumbers this forcing injects at (single-entry unless multi_scale)."""
        return (self.injection_wavenumber,) + tuple(self.extra_wavenumbers)


@dataclass(frozen=True)
class ForcingDominanceThresholds:
    """Configurable Phi_l regime-classification boundaries -- see module
    docstring. Never hard-code a different pair inline; extend this
    dataclass if a run needs a different boundary."""

    nonlinear_dominated_below: float = 0.1
    forcing_dominated_above: float = 10.0

    def __post_init__(self):
        if not (0 < self.nonlinear_dominated_below < self.forcing_dominated_above):
            raise ValueError("require 0 < nonlinear_dominated_below < forcing_dominated_above")


DEFAULT_THRESHOLDS = ForcingDominanceThresholds()


def forcing_dominance_ratio(p_forcing_l: float, u_l: float, l: float) -> float:
    """Phi_l = P_f(l) / (u_l^3 / l).

    Requires u_l > 0 and l > 0 -- raises rather than silently returning
    inf/nan when there is no local velocity scale to compare the forcing
    power against (e.g. a not-yet-spun-up field).
    """
    if l <= 0:
        raise ValueError("l must be > 0")
    if u_l <= 0:
        raise ValueError("u_l must be > 0 (no local velocity scale to compare forcing power against)")
    denom = u_l**3 / l
    return float(p_forcing_l / denom)


def classify_forcing_regime(
    phi_l: float, thresholds: ForcingDominanceThresholds = DEFAULT_THRESHOLDS
) -> str:
    """nonlinear_dominated (Phi<<1) / competing (Phi~1) / forcing_dominated (Phi>>1)."""
    if not np.isfinite(phi_l):
        return "undefined"
    if phi_l < thresholds.nonlinear_dominated_below:
        return "nonlinear_dominated"
    if phi_l > thresholds.forcing_dominated_above:
        return "forcing_dominated"
    return "competing"


def forcing_timescale_ratio(tau_f: float, tau_l: float) -> float:
    """Theta_f = tau_f / tau_l."""
    if tau_l <= 0:
        raise ValueError("tau_l must be > 0")
    return float(tau_f / tau_l)


def classify_timescale_regime(theta_f: float, *, slow_above: float = 3.0, fast_below: float = 1.0 / 3.0) -> str:
    """quasi_steady (tau_f >> tau_l), resonant_or_competing (~1), rapid (tau_f << tau_l).
    Boundaries configurable, defaulting to a factor of 3 either side of unity."""
    if not np.isfinite(theta_f):
        return "undefined"
    if theta_f > slow_above:
        return "quasi_steady"
    if theta_f < fast_below:
        return "rapid"
    return "resonant_or_competing"


def forcing_alignment(u: np.ndarray, f: np.ndarray, *, floor: float = 1e-30) -> float:
    """A_f = (u.f)/(|u||f|), volume-averaged over real-space fields
    u, f with shape (3, nz, ny, nx). Returns NaN (not 0) when either field
    has negligible norm, since alignment is undefined there, not zero."""
    num = float(np.sum(u * f))
    nu = float(np.sqrt(np.sum(u * u)))
    nf = float(np.sqrt(np.sum(f * f)))
    if nu < floor or nf < floor:
        return float("nan")
    return num / (nu * nf)


def eddy_turnover_time(u_rms: float, l: float) -> float:
    """tau_l = l / u_rms, the local structure/turnover timescale Theta_f is compared against."""
    if u_rms <= 0:
        raise ValueError("u_rms must be > 0")
    if l <= 0:
        raise ValueError("l must be > 0")
    return float(l / u_rms)


def initial_kinetic_energy_for_target_phi_l(power_input: float, l: float, target_phi_l: float) -> float:
    """Inverts Phi_l = P_f/(u_l^3/l) for u_l, then returns the isotropic
    3-component kinetic energy 1.5*u_l^2 a solver's `SolverConfig.
    initial_kinetic_energy` should be set to so a run starting from that
    warm-started velocity scale measures approximately `target_phi_l` at
    t=0 (Milestone 5.7a audit item 2 -- the fix for the confirmed
    cold-start bias where Phi_l could not be brought below O(100) for any
    forcing power because u_l started near zero).

    This is a t=0 ESTIMATE, not a guarantee the run stays near
    `target_phi_l` throughout -- nonlinear evolution, viscosity, and the
    controller all change u_l afterward, which is exactly why every run
    still reports its own MEASURED (time-averaged) Phi_l rather than
    trusting this target value after the fact.
    """
    if power_input <= 0:
        raise ValueError("power_input must be > 0")
    if l <= 0:
        raise ValueError("l must be > 0")
    if target_phi_l <= 0:
        raise ValueError("target_phi_l must be > 0")
    u_l = (power_input * l / target_phi_l) ** (1.0 / 3.0)
    return float(1.5 * u_l**2)
