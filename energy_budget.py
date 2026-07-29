"""
Energy-budget accounting and closure checks (Milestone 5.7)
================================================================

Aggregates the per-step `pseudo_spectral_solver.EnergyBudgetSample` history
of one run into the summary statistics the Milestone 5.7 success
conditions require: energy-budget closure (H2), pile-up / above-cutoff
checks, and the overshoot/settling-time/oscillation diagnostics the spec
asks for on top of the controller's own (see controller.py).

The full extended energy split from the spec,

    E_terminal = E_heat + E_return + E_wave + E_compressive
                 + E_surface + E_internal

is threaded through as the `wave_channel`...`internal_channel` fields of
EnergyBudgetSample -- always 0.0 for the current incompressible Newtonian
solver (see terminal_operator_forcing_aware.TerminalEnergySplit), never
fabricated.

Milestone 5.7a audit fix
------------------------
The original `relative_closure_error` compared `mean(power_input)` against
`mean(viscous_dissipation + terminal_heat)` ALONE -- omitting `dK/dt`
entirely. During any spin-up transient this is not a valid closure check:
most of `power_input` legitimately goes into raising kinetic energy, not
into dissipation, and the omission produced a spuriously large "error" even
when the complete budget closed almost exactly. Confirmed on a real 128^3
run: that metric reported 0.98 while `unresolved_residual` (which DOES
include `dK/dt`, via `_step_once`'s `dk_measured`/`dk_predicted`
bookkeeping) was ~0.06% of `power_input`.

`relative_closure_error` is now derived from `full_timestep_residual`
(`EnergyBudgetSample.full_timestep_residual`, an alias for
`unresolved_residual`) -- the true left-over term in

    P_input = dK/dt + viscous_dissipation + terminal_heat + (0 channels)
              + full_timestep_residual/dt

The old (invalid) metric is still reported, renamed
`input_vs_dissipation_only_gap`, purely for transparency/debugging -- it
must never be used as a closure check; it does not account for dK/dt and
is expected to be large during any spin-up transient by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from pseudo_spectral_solver import EnergyBudgetSample


@dataclass(frozen=True)
class EnergyBudgetSummary:
    n_samples: int
    mean_power_input: float
    mean_viscous_dissipation: float
    mean_terminal_heat: float
    mean_return_power: float
    mean_wave: float
    mean_compressive: float
    mean_surface: float
    mean_internal: float
    mean_unresolved_residual: float
    total_unresolved_residual: float
    relative_closure_error: float  # mean(|full_timestep_residual|/dt) / max(mean(|P_input|), floor) -- includes dK/dt
    input_vs_dissipation_only_gap: float  # the OLD, invalid metric -- see module docstring; debugging only
    linear_channel_split_exact: bool  # always True by construction -- see EnergyBudgetSample docstring
    max_energy_above_cutoff: float
    any_pile_up: bool
    kinetic_energy_overshoot: float
    kinetic_energy_settling_time_steps: int | None
    kinetic_energy_oscillation_amplitude: float
    closes_within_tolerance: bool
    forcing_clip_active_fraction: float
    forcing_clip_materially_altered_case: bool


def summarize_energy_budget(
    samples: list[EnergyBudgetSample], *, dt: float, closure_tolerance: float = 0.25, pile_up_floor: float = 1e-8, settle_band: float = 0.1
) -> EnergyBudgetSummary:
    """`dt` is required (Milestone 5.7a audit) so the closure metric can
    convert the per-step energy residual back into a rate comparable to
    `power_input` -- see module docstring for why the previous dt-free
    metric was wrong.

    closure_tolerance is intentionally loose (25%) by default: this is a
    first-order-in-dt explicit-nonlinear scheme (see pseudo_spectral_solver
    module docstring), so the residual is expected to be nonzero, not just
    floating-point noise. It is reported numerically either way -- the
    tolerance only decides `closes_within_tolerance`; the underlying numbers
    are always available for a stricter re-check."""
    if not samples:
        raise ValueError("no samples to summarize")
    if dt <= 0:
        raise ValueError("dt must be > 0")

    p_input = np.array([s.power_input for s in samples])
    visc = np.array([s.viscous_dissipation for s in samples])
    heat = np.array([s.terminal_heat for s in samples])
    ret = np.array([s.return_power for s in samples])
    wave = np.array([s.wave_channel for s in samples])
    comp = np.array([s.compressive_channel for s in samples])
    surf = np.array([s.surface_channel for s in samples])
    internal = np.array([s.internal_channel for s in samples])
    residual = np.array([s.unresolved_residual for s in samples])
    above_cutoff = np.array([s.energy_above_cutoff for s in samples])
    ke = np.array([s.kinetic_energy for s in samples])
    clip_active = np.array([s.forcing_clip_active for s in samples])
    requested_amp = np.array([s.forcing_requested_amplitude for s in samples])
    applied_amp = np.array([s.forcing_applied_amplitude for s in samples])

    mean_p_input = float(np.mean(p_input))
    mean_visc = float(np.mean(visc))
    mean_heat = float(np.mean(heat))

    input_scale = max(mean_p_input, 1e-12)
    # OLD, INVALID metric -- kept only for transparency/debugging. Does not
    # include dK/dt; expected to be large during spin-up. Never use this to
    # judge whether the complete budget closes.
    input_vs_dissipation_only_gap = abs(mean_p_input - (mean_visc + mean_heat)) / input_scale

    # CORRECT closure metric: full_timestep_residual already has dK/dt
    # folded in (see EnergyBudgetSample / pseudo_spectral_solver module
    # docstrings). Convert the per-step energy residual to a rate (/dt) so
    # it is comparable to the budget's other rate terms, then normalize by
    # the DOMINANT rate in the budget, not power_input alone -- a run whose
    # kinetic energy is decaying from a large warm-start (viscous
    # dissipation >> power_input) makes power_input a meaningless
    # normalization scale (a tiny denominator inflates a genuinely small
    # residual into a huge "relative error"); normalizing by
    # max(power_input, viscous+heat) uses whichever term actually carries
    # the budget's energy traffic.
    residual_rate = residual / dt
    scale = max(mean_p_input, mean_visc + mean_heat, 1e-12)
    relative_closure_error = float(np.mean(np.abs(residual_rate))) / scale

    clip_active_fraction = float(np.mean(clip_active)) if len(clip_active) else 0.0
    mean_requested = float(np.mean(requested_amp))
    mean_applied = float(np.mean(applied_amp))
    amplitude_alteration = (
        abs(mean_requested - mean_applied) / max(mean_requested, 1e-30) if mean_requested > 1e-30 else 0.0
    )
    # A case counts as "materially altered by the clip" if the clip fired on
    # a substantial fraction of steps AND meaningfully changed the mean
    # applied amplitude relative to what was requested -- both configurable,
    # documented thresholds, not universal physical constants.
    forcing_clip_materially_altered_case = bool(clip_active_fraction > 0.1 and amplitude_alteration > 0.1)

    max_above_cutoff = float(np.max(above_cutoff))
    any_pile_up = bool(max_above_cutoff > pile_up_floor)

    final_ke = ke[-1]
    start_ke = ke[0]
    travel = abs(final_ke - start_ke)
    overshoot = float(np.max(np.abs(ke - final_ke)) / travel) if travel > 1e-12 else 0.0

    band = settle_band * max(abs(final_ke), 1e-12)
    settled_idx = None
    for i in range(len(ke)):
        if np.all(np.abs(ke[i:] - final_ke) <= band):
            settled_idx = i
            break

    tail = ke[len(ke) // 2 :] if len(ke) >= 4 else ke
    oscillation_amplitude = float((np.max(tail) - np.min(tail)) / 2.0)

    return EnergyBudgetSummary(
        n_samples=len(samples),
        mean_power_input=mean_p_input,
        mean_viscous_dissipation=mean_visc,
        mean_terminal_heat=mean_heat,
        mean_return_power=float(np.mean(ret)),
        mean_wave=float(np.mean(wave)),
        mean_compressive=float(np.mean(comp)),
        mean_surface=float(np.mean(surf)),
        mean_internal=float(np.mean(internal)),
        mean_unresolved_residual=float(np.mean(residual)),
        total_unresolved_residual=float(np.sum(residual)),
        relative_closure_error=relative_closure_error,
        input_vs_dissipation_only_gap=input_vs_dissipation_only_gap,
        linear_channel_split_exact=True,
        max_energy_above_cutoff=max_above_cutoff,
        any_pile_up=any_pile_up,
        kinetic_energy_overshoot=overshoot,
        kinetic_energy_settling_time_steps=settled_idx,
        kinetic_energy_oscillation_amplitude=oscillation_amplitude,
        closes_within_tolerance=bool(relative_closure_error <= closure_tolerance),
        forcing_clip_active_fraction=clip_active_fraction,
        forcing_clip_materially_altered_case=forcing_clip_materially_altered_case,
    )


def detect_terminal_pile_up(samples: list[EnergyBudgetSample], *, floor: float = 1e-8) -> dict:
    above = np.array([s.energy_above_cutoff for s in samples])
    growing = bool(above[-1] > above[0] * 2.0 + floor) if len(above) > 1 else False
    return {
        "max_energy_above_cutoff": float(np.max(above)),
        "final_energy_above_cutoff": float(above[-1]),
        "monotonically_growing": growing,
        "pile_up_detected": bool(np.max(above) > floor),
    }
