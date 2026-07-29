"""
Tests for Milestone 5.7a audit additions.

Covers the functions introduced or structurally changed by the 5.7a audit
that were not yet exercised by any existing test file: warm-start Phi_l
targeting (forcing.py), richer controller classification (controller.py),
isotropic-control-ensemble significance testing (structure_metrics.py),
orthogonal AuditedStatus (stress_test_classification.py), forcing-case
fingerprinting/collision detection (forcing_fingerprint.py), deterministic
run identity (milestone_5_7_stress_test.py), and the forcing-amplitude clip
instrumentation (pseudo_spectral_solver.py).
"""
import numpy as np
import pytest

from forcing import ForcingState, forcing_dominance_ratio, initial_kinetic_energy_for_target_phi_l
from controller import (
    ControllerConfig, ControllerState, controller_step, classify_controller_run,
    ControllerClassificationThresholds,
)
from structure_metrics import isotropic_control_baseline, is_anisotropic_response_significant
from stress_test_classification import AuditedStatus, compute_audited_status
from forcing_test_matrix import ForcingTestCase
from forcing_fingerprint import (
    resolved_forcing_fingerprint, forcing_fingerprint_hash, detect_forcing_collisions,
    assert_no_unexpected_collisions,
)
from jhtdb_terminal_benchmark import compute_terminal_layer, wavenumbers, Config as TerminalConfig
from milestone_5_7_stress_test import compute_run_identity
from material_state import get_material
from pseudo_spectral_solver import SolverConfig, run_solver

NEWTONIAN = get_material("incompressible_newtonian_liquid")


# --- forcing.py: warm-start Phi_l targeting ---------------------------------

def test_initial_kinetic_energy_for_target_phi_l_round_trips():
    power = 0.05
    l = 2.0
    target = 3.0
    ke = initial_kinetic_energy_for_target_phi_l(power, l, target)
    assert ke > 0
    u_l = np.sqrt(2.0 * ke / 3.0)
    phi = forcing_dominance_ratio(power, u_l, l)
    assert phi == pytest.approx(target, rel=1e-9)


@pytest.mark.parametrize("power,l,target", [(-1.0, 1.0, 1.0), (1.0, -1.0, 1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 0.0)])
def test_initial_kinetic_energy_for_target_phi_l_rejects_invalid_inputs(power, l, target):
    with pytest.raises(ValueError):
        initial_kinetic_energy_for_target_phi_l(power, l, target)


# --- controller.py: richer classification -----------------------------------

def _run_controller(target_power: float, measured_power_fn, n_steps: int, *, gp=24.0, gi=8.0, dt=0.05, c_gamma0=1.0):
    cfg = ControllerConfig(gp=gp, gi=gi)
    state = ControllerState(c_gamma=c_gamma0)
    measured_history = []
    target_history = []
    for i in range(n_steps):
        measured = measured_power_fn(state.c_gamma)
        state = controller_step(state, cfg, target_power=target_power, measured_power=measured, dt=dt)
        measured_history.append(measured)
        target_history.append(target_power)
    return state, tuple(target_history), tuple(measured_history)


def test_classify_controller_run_converging_controller_is_bounded_and_nonoscillatory():
    # measured power tracks c_gamma directly (a simple negative-feedback
    # loop) so the controller should settle.
    state, targets, measured = _run_controller(1.0, lambda c: 0.1 * c, 60)
    labels = classify_controller_run(state, target_history=targets, measured_history=measured)
    assert "controller_bounded" in labels
    assert "controller_unstable" not in labels


def test_classify_controller_run_unstable_short_circuits_to_single_label():
    # A trajectory containing a non-finite value is exactly what
    # controller_diagnostics.is_stable is designed to catch.
    bad_state = ControllerState(c_gamma=float("nan"), c_gamma_history=(1.0, 5.0, float("nan")))
    labels = classify_controller_run(bad_state)
    assert labels == ("controller_unstable",)


def test_classify_controller_run_target_achieved_requires_matching_histories():
    state, targets, measured = _run_controller(1.0, lambda c: 0.1 * c, 60)
    # Without histories, controller_target_achieved must never be asserted.
    labels_no_history = classify_controller_run(state)
    assert "controller_target_achieved" not in labels_no_history

    # A measured trace that matches target almost exactly in the final
    # window should earn controller_target_achieved.
    close_measured = tuple(0.99 * t for t in targets)
    labels_close = classify_controller_run(state, target_history=targets, measured_history=close_measured)
    assert "controller_target_achieved" in labels_close

    # A measured trace far from target in the final window should not.
    far_measured = tuple(5.0 * t for t in targets)
    labels_far = classify_controller_run(state, target_history=targets, measured_history=far_measured)
    assert "controller_target_achieved" not in labels_far


def test_classify_controller_run_budget_error_reduced_only_when_better_than_baseline():
    state, targets, measured = _run_controller(1.0, lambda c: 0.1 * c, 60)
    close_measured = tuple(0.99 * t for t in targets)
    # A generous baseline error -> controlled run beats it.
    labels_better = classify_controller_run(
        state, target_history=targets, measured_history=close_measured, baseline_mean_abs_error=0.5,
    )
    assert "controller_budget_error_reduced" in labels_better
    # An impossibly tight baseline -> controlled run cannot beat it.
    labels_worse = classify_controller_run(
        state, target_history=targets, measured_history=close_measured, baseline_mean_abs_error=1e-9,
    )
    assert "controller_budget_error_reduced" not in labels_worse


def test_classify_controller_run_thresholds_are_configurable():
    state, targets, measured = _run_controller(1.0, lambda c: 0.1 * c, 60)
    strict = ControllerClassificationThresholds(target_error_tolerance=1e-12)
    close_measured = tuple(0.99 * t for t in targets)
    labels = classify_controller_run(state, target_history=targets, measured_history=close_measured, thresholds=strict)
    assert "controller_target_achieved" not in labels  # 1% error fails an impossibly strict tolerance


# --- structure_metrics.py: isotropic-control-ensemble significance ---------

def test_isotropic_control_baseline_basic_stats():
    baseline = isotropic_control_baseline([0.01, 0.02, 0.03])
    assert baseline.n_seeds == 3
    assert baseline.mean_anisotropy_magnitude == pytest.approx(0.02)
    assert baseline.samples == (0.01, 0.02, 0.03)


def test_isotropic_control_baseline_rejects_empty():
    with pytest.raises(ValueError):
        isotropic_control_baseline([])


def test_is_anisotropic_response_significant_distinguishes_noise_from_signal():
    baseline = isotropic_control_baseline([0.01, 0.015, 0.02, 0.012])
    noise_level_case = baseline.mean_anisotropy_magnitude + 0.5 * baseline.std_anisotropy_magnitude
    strong_signal_case = baseline.mean_anisotropy_magnitude + 10.0 * baseline.std_anisotropy_magnitude
    assert is_anisotropic_response_significant(noise_level_case, baseline) is False
    assert is_anisotropic_response_significant(strong_signal_case, baseline) is True


# --- stress_test_classification.py: orthogonal AuditedStatus ---------------

def test_audited_status_rejects_invalid_field_value():
    with pytest.raises(ValueError):
        AuditedStatus(
            pipeline_status="not_a_real_status", resolution_status="resolved",
            energy_budget_status="closed", forcing_regime_status="measured",
            scientific_status="not_testable", spectral_status="no_detected_pileup",
        )


def test_compute_audited_status_failed_pipeline_forces_not_testable():
    status = compute_audited_status(
        pipeline_ok=False, material_implemented=True, resolution_ok=True, is_diagnostic_tier=False,
        energy_budget_closes=True, energy_budget_partial=False, forcing_clip_materially_altered=False,
        forcing_overlaps_terminal_layer=False, weak_forcing_case=False, weak_forcing_matches_baseline=None,
        group="A",
    )
    assert status.pipeline_status == "failed"
    assert status.scientific_status == "not_testable"
    assert status.resolution_status == "insufficient"
    assert status.spectral_status == "unresolved"


def test_compute_audited_status_diagnostic_tier_cannot_claim_scientific_result():
    status = compute_audited_status(
        pipeline_ok=True, material_implemented=True, resolution_ok=True, is_diagnostic_tier=True,
        energy_budget_closes=True, energy_budget_partial=False, forcing_clip_materially_altered=False,
        forcing_overlaps_terminal_layer=True,  # even a strong physical signal...
        weak_forcing_case=False, weak_forcing_matches_baseline=None, group="C",
    )
    assert status.resolution_status == "diagnostic_only"
    assert status.scientific_status == "not_testable"  # ...is overridden by the diagnostic-tier gate
    assert status.spectral_status == "unresolved"  # diagnostic tier -> no spectral claim either


def test_compute_audited_status_overlap_case_is_assumption_challenged():
    status = compute_audited_status(
        pipeline_ok=True, material_implemented=True, resolution_ok=True, is_diagnostic_tier=False,
        energy_budget_closes=False, energy_budget_partial=True, forcing_clip_materially_altered=False,
        forcing_overlaps_terminal_layer=True, weak_forcing_case=False, weak_forcing_matches_baseline=None,
        group="A",
    )
    assert status.energy_budget_status == "partial"
    assert status.scientific_status == "assumption_challenged"


def test_compute_audited_status_baseline_group_never_gets_a_candidate_label():
    # Milestone 5.7a re-audit: a group A (or B/D/E/F) run never ran the
    # candidate operator at all -- it must never receive a
    # candidate_*/synthetic_support-style label implying otherwise.
    for group in ("A", "B", "D", "E", "F"):
        status = compute_audited_status(
            pipeline_ok=True, material_implemented=True, resolution_ok=True, is_diagnostic_tier=False,
            energy_budget_closes=True, energy_budget_partial=False, forcing_clip_materially_altered=False,
            forcing_overlaps_terminal_layer=False, weak_forcing_case=True, weak_forcing_matches_baseline=True,
            group=group,
        )
        assert status.scientific_status == "synthetic_run_valid"


def test_compute_audited_status_candidate_limit_consistency_requires_group_c_and_match():
    matches = compute_audited_status(
        pipeline_ok=True, material_implemented=True, resolution_ok=True, is_diagnostic_tier=False,
        energy_budget_closes=True, energy_budget_partial=False, forcing_clip_materially_altered=False,
        forcing_overlaps_terminal_layer=False, weak_forcing_case=True, weak_forcing_matches_baseline=True,
        group="C",
    )
    assert matches.scientific_status == "candidate_limit_consistency_observed"

    # group C but NOT the weak-limit match -> conservative "not testable for
    # improvement", never a positive candidate claim.
    not_weak = compute_audited_status(
        pipeline_ok=True, material_implemented=True, resolution_ok=True, is_diagnostic_tier=False,
        energy_budget_closes=True, energy_budget_partial=False, forcing_clip_materially_altered=False,
        forcing_overlaps_terminal_layer=False, weak_forcing_case=False, weak_forcing_matches_baseline=None,
        group="C",
    )
    assert not_weak.scientific_status == "candidate_improvement_not_testable"

    # group C, weak-forcing case, but did NOT match baseline -> still no
    # positive consistency claim.
    mismatched = compute_audited_status(
        pipeline_ok=True, material_implemented=True, resolution_ok=True, is_diagnostic_tier=False,
        energy_budget_closes=True, energy_budget_partial=False, forcing_clip_materially_altered=False,
        forcing_overlaps_terminal_layer=False, weak_forcing_case=True, weak_forcing_matches_baseline=False,
        group="C",
    )
    assert mismatched.scientific_status == "candidate_improvement_not_testable"


def test_compute_audited_status_no_run_ever_claims_improvement():
    # "candidate improvement" is not in the vocabulary at all -- there is no
    # real-data ground truth anywhere in this synthetic milestone to improve
    # against.
    from stress_test_classification import SCIENTIFIC_STATUSES
    assert not any("improvement" in s and "not_testable" not in s for s in SCIENTIFIC_STATUSES)


def test_classify_spectral_status_orthogonal_to_energy_budget():
    from stress_test_classification import classify_spectral_status
    assert classify_spectral_status(is_diagnostic_tier=True, forcing_above_cutoff=False, pile_up_detected=True, monotonically_growing=True) == "unresolved"
    assert classify_spectral_status(is_diagnostic_tier=False, forcing_above_cutoff=True, pile_up_detected=True, monotonically_growing=True) == "forcing_above_cutoff"
    assert classify_spectral_status(is_diagnostic_tier=False, forcing_above_cutoff=False, pile_up_detected=False, monotonically_growing=False) == "no_detected_pileup"
    assert classify_spectral_status(is_diagnostic_tier=False, forcing_above_cutoff=False, pile_up_detected=True, monotonically_growing=True) == "persistent_pileup"
    assert classify_spectral_status(is_diagnostic_tier=False, forcing_above_cutoff=False, pile_up_detected=True, monotonically_growing=False) == "transient_pileup"


def test_compute_audited_status_closed_budget_can_still_have_persistent_pileup():
    # The key re-audit finding this field exists to prevent hiding: a run
    # can close its energy budget while persistently piling up energy above
    # the cutoff -- these are orthogonal, and a caller must check both.
    status = compute_audited_status(
        pipeline_ok=True, material_implemented=True, resolution_ok=True, is_diagnostic_tier=False,
        energy_budget_closes=True, energy_budget_partial=False, forcing_clip_materially_altered=False,
        forcing_overlaps_terminal_layer=False, weak_forcing_case=False, weak_forcing_matches_baseline=None,
        group="A", pile_up_detected=True, monotonically_growing=True,
    )
    assert status.energy_budget_status == "closed"
    assert status.spectral_status == "persistent_pileup"


# --- forcing_fingerprint.py: fingerprinting and collision detection --------

def test_resolved_forcing_fingerprint_is_deterministic_and_seed_independent():
    f1 = ForcingState(power_input=0.05, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    f2 = ForcingState(power_input=0.05, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    assert resolved_forcing_fingerprint(f1) == resolved_forcing_fingerprint(f2)
    assert forcing_fingerprint_hash(f1) == forcing_fingerprint_hash(f2)


def test_resolved_forcing_fingerprint_distinguishes_different_configs():
    f1 = ForcingState(power_input=0.05, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    f2 = ForcingState(power_input=0.5, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    assert resolved_forcing_fingerprint(f1) != resolved_forcing_fingerprint(f2)


def test_detect_forcing_collisions_flags_duplicate_case_definitions():
    dup_a = ForcingTestCase(
        name="dup_a", letter="", description="", expected_response="",
        forcing_type="isotropic_random", power=0.05, k_f_mode="fixed_absolute", k_f_absolute=3.0, tau_f=1.0,
    )
    dup_b = ForcingTestCase(
        name="dup_b", letter="", description="", expected_response="",
        forcing_type="isotropic_random", power=0.05, k_f_mode="fixed_absolute", k_f_absolute=3.0, tau_f=1.0,
    )
    distinct = ForcingTestCase(
        name="distinct", letter="", description="", expected_response="",
        forcing_type="isotropic_random", power=1.0, k_f_mode="fixed_absolute", k_f_absolute=3.0, tau_f=1.0,
    )
    domain_length = 2.0 * np.pi
    kx, ky, kz = wavenumbers(64, domain_length)
    nyquist = float(np.max(np.abs(kx[:, 0, 0])))
    delta_k = 2.0 * np.pi / domain_length
    layer = compute_terminal_layer(0.5 * nyquist, delta_k, TerminalConfig())

    collisions = detect_forcing_collisions([dup_a, dup_b, distinct], layer, nyquist, delta_k)
    assert len(collisions) == 1
    assert set(collisions[0].case_names) == {"dup_a", "dup_b"}

    with pytest.raises(AssertionError):
        assert_no_unexpected_collisions([dup_a, dup_b, distinct], layer, nyquist, delta_k)

    # Declaring the collision as allowed/documented should silence the raise.
    allowed = frozenset({frozenset({"dup_a", "dup_b"})})
    result = assert_no_unexpected_collisions([dup_a, dup_b, distinct], layer, nyquist, delta_k, allowed_collisions=allowed)
    assert len(result) == 1


# --- milestone_5_7_stress_test.py: deterministic run identity --------------

def _identity_kwargs(**overrides):
    defaults = dict(
        case_name="weak_isotropic", split="calibration", material_name="incompressible_newtonian_liquid",
        grid_n=64, domain_length=2.0 * np.pi, viscosity=0.02, group="A", controller_gains=(24.0, 8.0), seed=0,
        forcing=ForcingState(power_input=0.05, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random"),
    )
    defaults.update(overrides)
    return defaults


def test_compute_run_identity_is_deterministic():
    id1 = compute_run_identity(**_identity_kwargs())
    id2 = compute_run_identity(**_identity_kwargs())
    assert id1 == id2


def test_compute_run_identity_changes_with_outcome_determining_fields():
    base = compute_run_identity(**_identity_kwargs())
    assert base != compute_run_identity(**_identity_kwargs(seed=1))
    assert base != compute_run_identity(**_identity_kwargs(group="C"))
    assert base != compute_run_identity(**_identity_kwargs(grid_n=128))
    assert base != compute_run_identity(**_identity_kwargs(
        forcing=ForcingState(power_input=1.0, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    ))


def test_compute_run_identity_handles_none_forcing():
    # Blocked-result rows (material not implemented) may have no resolved
    # forcing at all -- must not raise.
    rid = compute_run_identity(**_identity_kwargs(forcing=None))
    assert isinstance(rid, str) and len(rid) == 24


# --- pseudo_spectral_solver.py: forcing-amplitude clip instrumentation ------

def test_energy_budget_samples_report_clip_diagnostics_consistently():
    force = ForcingState(power_input=5.0, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    cfg = SolverConfig(
        grid_n=16, domain_length=2 * np.pi, viscosity=0.05, forcing=force, material=NEWTONIAN, dt=0.01, seed=0,
        forcing_amplitude_safety_factor=0.05,  # deliberately tiny -> clip should fire
    )
    _state, samples, _layer = run_solver(cfg, 5)
    assert any(s.forcing_clip_active for s in samples)
    for s in samples:
        assert s.forcing_applied_amplitude <= s.forcing_requested_amplitude + 1e-9
        assert isinstance(s.forcing_clip_active, bool)


def test_energy_budget_samples_report_no_clip_for_zero_power_forcing():
    force = ForcingState(power_input=0.0, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    cfg = SolverConfig(grid_n=16, domain_length=2 * np.pi, viscosity=0.05, forcing=force, material=NEWTONIAN, dt=0.01, seed=0)
    _state, samples, _layer = run_solver(cfg, 3)
    assert all(not s.forcing_clip_active for s in samples)
    assert all(s.forcing_requested_amplitude == 0.0 for s in samples)
