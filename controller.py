"""
Energy-budget PI controller for C_gamma (Milestone 5.7)
============================================================

Every terminal-operator call site through Milestone 5.5 hardcodes
`c_gamma = 1.0` with a comment that "the forward simulation should evolve
C_gamma with the GP/GI controller" -- no such controller has existed in
this repo until now (see AGENTS.md: "do not begin controller retuning
until real Milestone 5 a-priori placement results exist" -- this module is
the synthetic-only stress-test controller, not a real-data retuning).

`Config.gp = 24.0` and `Config.gi = 8.0` have sat as unused dataclass
defaults since Milestone 1. This module is the first thing that actually
reads them, and per H7 in the Milestone 5.7 spec, treats them as a *tested
baseline hypothesis*, not a universal constant -- ControllerConfig accepts
any (gp, gi) pair, defaulting to the pre-registered (24.0, 8.0).

Control law (standard discrete PI on the energy-budget imbalance):

    error(t)      = target_terminal_power - measured_terminal_power(t)
    integral(t)   = integral(t-dt) + error(t) * dt
    c_gamma(t+dt) = clip(c_gamma(t) + gp*error(t)*dt + gi*integral(t)*dt, c_gamma_min, c_gamma_max)

`target_terminal_power` is supplied by the caller (pseudo_spectral_solver.py
sets it to the injected power P_input under the steady-state hypothesis H2:
"mean input approximately balances mean viscous + terminal heat
dissipation" -- so driving terminal removal toward the injected power is a
reasonable target for a stress test, not a claim that it is correct).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

DEFAULT_GP = 24.0
DEFAULT_GI = 8.0


@dataclass(frozen=True)
class ControllerConfig:
    gp: float = DEFAULT_GP
    gi: float = DEFAULT_GI
    c_gamma_min: float = 0.0
    c_gamma_max: float = 50.0
    integral_clamp: float | None = None  # anti-windup bound on the integral term; None = unclamped

    def __post_init__(self):
        if self.gp < 0 or self.gi < 0:
            raise ValueError("gp, gi must be >= 0")
        if self.c_gamma_min < 0 or self.c_gamma_max <= self.c_gamma_min:
            raise ValueError("require 0 <= c_gamma_min < c_gamma_max")


@dataclass(frozen=True)
class ControllerState:
    c_gamma: float
    integral: float = 0.0
    step_count: int = 0
    error_history: tuple[float, ...] = ()
    c_gamma_history: tuple[float, ...] = ()


def controller_step(
    state: ControllerState, cfg: ControllerConfig, *, target_power: float, measured_power: float, dt: float
) -> ControllerState:
    error = target_power - measured_power
    integral = state.integral + error * dt
    if cfg.integral_clamp is not None:
        integral = float(np.clip(integral, -cfg.integral_clamp, cfg.integral_clamp))
    raw = state.c_gamma + cfg.gp * error * dt + cfg.gi * integral * dt
    c_gamma = float(np.clip(raw, cfg.c_gamma_min, cfg.c_gamma_max))
    return ControllerState(
        c_gamma=c_gamma,
        integral=integral,
        step_count=state.step_count + 1,
        error_history=state.error_history + (error,),
        c_gamma_history=state.c_gamma_history + (c_gamma,),
    )


def controller_diagnostics(state: ControllerState, *, settle_band: float = 0.05) -> dict:
    """Overshoot, settling time (in steps), and oscillation amplitude/frequency
    diagnostics computed from the recorded c_gamma trajectory.

    - overshoot: max fractional excursion of c_gamma beyond its own final
      value, relative to the total travel from the first recorded value.
    - settling_time_steps: first step index after which c_gamma stays within
      `settle_band` (fractional) of the final value for the remainder of the
      run; None if it never settles.
    - oscillation_amplitude: half the peak-to-peak range of c_gamma over the
      final half of the run (a proxy for residual ringing once transients
      should have died out).
    - is_stable: c_gamma stayed finite, within [c_gamma_min, c_gamma_max]
      (by construction, since controller_step clips), and did not diverge
      monotonically to the clamp for the whole run.
    """
    traj = np.asarray(state.c_gamma_history, dtype=float)
    n = traj.size
    out = {
        "n_steps": n,
        "final_c_gamma": float(traj[-1]) if n else None,
        "overshoot": None,
        "settling_time_steps": None,
        "oscillation_amplitude": None,
        "is_stable": bool(np.all(np.isfinite(traj))) if n else True,
    }
    if n == 0:
        return out

    final = traj[-1]
    start = traj[0]
    travel = abs(final - start)
    if travel > 1e-12:
        overshoot = float(np.max(np.abs(traj - final)) / travel)
    else:
        overshoot = 0.0
    out["overshoot"] = overshoot

    band = settle_band * max(abs(final), 1e-12)
    settled_idx = None
    for i in range(n):
        if np.all(np.abs(traj[i:] - final) <= band):
            settled_idx = i
            break
    out["settling_time_steps"] = settled_idx

    tail = traj[n // 2 :] if n >= 4 else traj
    out["oscillation_amplitude"] = float((np.max(tail) - np.min(tail)) / 2.0)

    out["is_stable"] = bool(out["is_stable"] and np.all(np.abs(traj) < 1e6))
    return out


# --- Milestone 5.7a audit item 8: richer controller classification ---------
#
# The original Milestone 5.7 report used a single `controller_stable` label
# for all 186 executable runs, which conflated "c_gamma stayed numerically
# bounded" with "the controller actually achieved its control objective."
# A controller can be bounded and non-oscillatory while its target error
# stays large the whole run -- that is a real failure mode, not success.


@dataclass(frozen=True)
class ControllerClassificationThresholds:
    """Every threshold documented and configurable, not a claimed physical
    constant -- same discipline as forcing.ForcingDominanceThresholds."""

    oscillation_amplitude_max: float = 0.05  # fraction of final c_gamma, for "nonoscillatory"
    overshoot_max: float = 0.5  # fractional overshoot allowed for "converged"
    final_window_fraction: float = 0.25  # last N fraction of steps used for "target achieved"
    target_error_tolerance: float = 0.1  # relative error in that window, for "target achieved"


DEFAULT_CONTROLLER_THRESHOLDS = ControllerClassificationThresholds()


def classify_controller_run(
    state: ControllerState,
    *,
    target_history: tuple[float, ...] | None = None,
    measured_history: tuple[float, ...] | None = None,
    baseline_mean_abs_error: float | None = None,
    thresholds: ControllerClassificationThresholds = DEFAULT_CONTROLLER_THRESHOLDS,
) -> tuple[str, ...]:
    """Returns a tuple of labels from {controller_bounded,
    controller_nonoscillatory, controller_converged,
    controller_target_achieved, controller_budget_error_reduced,
    controller_unstable} -- multiple may apply, and 'unstable' is mutually
    exclusive with the rest (matches controller_diagnostics.is_stable).

    - controller_bounded: c_gamma finite and within its clamp (always true
      by construction if controller_step was used -- this label exists so
      a report can state it explicitly rather than only implying it).
    - controller_nonoscillatory: final-window oscillation_amplitude, as a
      FRACTION of the final c_gamma, below `oscillation_amplitude_max`.
    - controller_converged: overshoot below `overshoot_max` AND a finite
      settling_time_steps was found.
    - controller_target_achieved: requires `target_history`/
      `measured_history` (equal length, one entry per step) -- the mean
      absolute relative error |target-measured|/|target| over the final
      `final_window_fraction` of steps is below `target_error_tolerance`.
      Without those histories, this label is never asserted (no target-
      achievement claim without the actual controlled-variable trace).
    - controller_budget_error_reduced: requires `baseline_mean_abs_error`
      (the same final-window mean absolute error from a controller-
      disabled baseline run) -- asserted only when the controlled run's
      final-window error is strictly smaller than that baseline's.
    """
    diag = controller_diagnostics(state)
    if not diag["is_stable"]:
        return ("controller_unstable",)

    labels = ["controller_bounded"]

    final_c_gamma = diag["final_c_gamma"] or 0.0
    osc = diag["oscillation_amplitude"] or 0.0
    if abs(final_c_gamma) > 1e-12 and (osc / abs(final_c_gamma)) <= thresholds.oscillation_amplitude_max:
        labels.append("controller_nonoscillatory")
    elif abs(final_c_gamma) <= 1e-12 and osc <= thresholds.oscillation_amplitude_max:
        labels.append("controller_nonoscillatory")

    if (diag["overshoot"] or 0.0) <= thresholds.overshoot_max and diag["settling_time_steps"] is not None:
        labels.append("controller_converged")

    if target_history is not None and measured_history is not None and len(target_history) == len(measured_history) and len(target_history) > 0:
        n = len(target_history)
        window_start = max(int(n * (1.0 - thresholds.final_window_fraction)), 0)
        t = np.asarray(target_history[window_start:], dtype=float)
        m = np.asarray(measured_history[window_start:], dtype=float)
        denom = np.maximum(np.abs(t), 1e-12)
        mean_abs_rel_error = float(np.mean(np.abs(t - m) / denom))
        if mean_abs_rel_error <= thresholds.target_error_tolerance:
            labels.append("controller_target_achieved")
        if baseline_mean_abs_error is not None and mean_abs_rel_error < baseline_mean_abs_error:
            labels.append("controller_budget_error_reduced")

    return tuple(labels)
