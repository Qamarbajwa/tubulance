import pytest

from pseudo_spectral_solver import EnergyBudgetSample
from energy_budget import summarize_energy_budget, detect_terminal_pile_up


def _sample(t, ke, p_in, visc, heat, above_cutoff=0.0, ret=0.0, resid=0.0):
    return EnergyBudgetSample(
        time=t, kinetic_energy=ke, power_input=p_in, viscous_dissipation=visc, terminal_heat=heat,
        return_power=ret, unresolved_residual=resid, energy_above_cutoff=above_cutoff,
    )


def test_summarize_requires_samples():
    with pytest.raises(ValueError):
        summarize_energy_budget([], dt=0.1)


def test_summarize_requires_dt():
    # Milestone 5.7a audit fix: dt is a required keyword-only argument
    # because the closure metric now converts the per-step residual to a
    # rate (residual/dt) -- see module docstring on why the old dt-free
    # metric was invalid.
    samples = [_sample(i * 0.1, 1.0, 1.0, 0.6, 0.4) for i in range(3)]
    with pytest.raises(TypeError):
        summarize_energy_budget(samples)
    with pytest.raises(ValueError):
        summarize_energy_budget(samples, dt=0.0)


def test_closure_within_tolerance_when_budget_balances():
    # zero residual at every step -> the corrected (dK/dt-inclusive) metric
    # is exactly zero regardless of how power_input splits between
    # viscous_dissipation and terminal_heat.
    samples = [_sample(i * 0.1, 1.0, 1.0, 0.6, 0.4) for i in range(10)]
    summary = summarize_energy_budget(samples, dt=0.1)
    assert summary.relative_closure_error == pytest.approx(0.0, abs=1e-9)
    assert summary.closes_within_tolerance is True


def test_closure_fails_when_budget_imbalanced():
    # Milestone 5.7a audit fix: "imbalanced" must now be expressed via a
    # genuine nonzero unresolved_residual, since the corrected metric is
    # derived from full_timestep_residual (which already includes dK/dt) --
    # comparing power_input to viscous+heat directly (the OLD, invalid
    # metric) is no longer what closes_within_tolerance is based on.
    dt = 0.1
    samples = [_sample(i * dt, 1.0, 1.0, 0.5, 0.5, resid=0.15) for i in range(10)]
    summary = summarize_energy_budget(samples, dt=dt, closure_tolerance=0.1)
    assert summary.relative_closure_error > 0.1
    assert summary.closes_within_tolerance is False


def test_old_invalid_metric_reported_separately_and_can_diverge_from_corrected_one():
    # A pure warm-start decay case: power_input is small, viscous_dissipation
    # dominates, and the residual is genuinely tiny (the budget DOES close).
    # The OLD metric (input_vs_dissipation_only_gap, normalized by
    # power_input alone) is large and would have wrongly flagged this as not
    # closing; the CORRECTED metric (normalized by the dominant rate) is
    # small and correctly reports closure.
    dt = 0.1
    samples = [_sample(i * dt, 1.0, 0.0025, 8.27, 0.0, resid=0.002) for i in range(10)]
    summary = summarize_energy_budget(samples, dt=dt)
    assert summary.input_vs_dissipation_only_gap > 1.0  # old metric: huge, misleading
    assert summary.relative_closure_error < 0.25  # corrected metric: small, closes
    assert summary.closes_within_tolerance is True


def test_pile_up_detection_flags_growth_above_cutoff():
    samples = [_sample(i * 0.1, 1.0, 1.0, 0.5, 0.5, above_cutoff=i * 0.01) for i in range(10)]
    pile = detect_terminal_pile_up(samples, floor=1e-8)
    assert pile["pile_up_detected"] is True
    assert pile["monotonically_growing"] is True


def test_no_pile_up_when_above_cutoff_stays_zero():
    samples = [_sample(i * 0.1, 1.0, 1.0, 0.5, 0.5, above_cutoff=0.0) for i in range(10)]
    pile = detect_terminal_pile_up(samples)
    assert pile["pile_up_detected"] is False


def test_overshoot_and_settling_time_on_converging_trajectory():
    ke_traj = [10.0, 15.0, 8.0, 6.5, 6.05, 6.0, 6.0, 6.0]
    samples = [_sample(i, ke, 1.0, 0.5, 0.5) for i, ke in enumerate(ke_traj)]
    summary = summarize_energy_budget(samples, dt=1.0, settle_band=0.02)
    assert summary.kinetic_energy_overshoot > 0.5  # significant overshoot at index 1
    assert summary.kinetic_energy_settling_time_steps is not None
