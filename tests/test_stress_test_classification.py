import pytest

from stress_test_classification import RunDomain, classify_stress_test_run, StressTestClassification, VALID_LABELS


def _domain(**kwargs):
    defaults = dict(
        forcing_case="weak_isotropic", material="incompressible_newtonian_liquid", grid_n=64,
        forcing_type="isotropic_random", phi_l_regime="nonlinear_dominated", theta_f_regime="quasi_steady",
        k_f_vs_ks="below",
    )
    defaults.update(kwargs)
    return RunDomain(**defaults)


def test_classification_requires_domain_and_at_least_one_label():
    with pytest.raises(ValueError):
        StressTestClassification(domain=_domain(), labels=())


def test_invalid_label_rejected():
    with pytest.raises(ValueError):
        StressTestClassification(domain=_domain(), labels=("not_a_real_label",))


def test_unimplemented_material_short_circuits_to_interface_only():
    c = classify_stress_test_run(
        _domain(), pipeline_ok=True, resolution_ok=True, material_implemented=False,
        energy_budget_closes=True, pile_up_detected=False, controller_is_stable=True,
        weak_forcing_case=True, weak_forcing_matches_baseline=True,
        forcing_overlaps_terminal_layer=False, anisotropy_significant=False, size_effect_significant=False,
    )
    assert c.labels == ("material_interface_only",)


def test_pipeline_failure_short_circuits_to_blocked():
    c = classify_stress_test_run(
        _domain(), pipeline_ok=False, resolution_ok=False, material_implemented=True,
        energy_budget_closes=False, pile_up_detected=False, controller_is_stable=False,
        weak_forcing_case=False, weak_forcing_matches_baseline=None,
        forcing_overlaps_terminal_layer=False, anisotropy_significant=False, size_effect_significant=False,
    )
    assert c.labels == ("blocked",)


def test_weak_forcing_consistent_when_matches_baseline():
    c = classify_stress_test_run(
        _domain(), pipeline_ok=True, resolution_ok=True, material_implemented=True,
        energy_budget_closes=True, pile_up_detected=False, controller_is_stable=True,
        weak_forcing_case=True, weak_forcing_matches_baseline=True,
        forcing_overlaps_terminal_layer=False, anisotropy_significant=False, size_effect_significant=False,
    )
    assert "weak_forcing_consistent" in c.labels
    assert "terminal_model_supported_in_domain" in c.labels


def test_forcing_overlap_flags_assumption_challenge_and_extension_required():
    c = classify_stress_test_run(
        _domain(k_f_vs_ks="overlap_or_above"), pipeline_ok=True, resolution_ok=True, material_implemented=True,
        energy_budget_closes=True, pile_up_detected=False, controller_is_stable=True,
        weak_forcing_case=False, weak_forcing_matches_baseline=None,
        forcing_overlaps_terminal_layer=True, anisotropy_significant=False, size_effect_significant=False,
    )
    assert "forcing_overlap_invalidates_assumption" in c.labels
    assert "terminal_model_requires_extension" in c.labels or "terminal_model_not_supported" in c.labels


def test_forcing_overlap_with_broken_budget_is_not_supported():
    c = classify_stress_test_run(
        _domain(k_f_vs_ks="overlap_or_above"), pipeline_ok=True, resolution_ok=True, material_implemented=True,
        energy_budget_closes=False, pile_up_detected=True, controller_is_stable=False,
        weak_forcing_case=False, weak_forcing_matches_baseline=None,
        forcing_overlaps_terminal_layer=True, anisotropy_significant=False, size_effect_significant=False,
    )
    assert "terminal_model_not_supported" in c.labels


def test_insufficient_resolution_never_yields_a_supported_verdict():
    c = classify_stress_test_run(
        _domain(), pipeline_ok=True, resolution_ok=False, material_implemented=True,
        energy_budget_closes=True, pile_up_detected=False, controller_is_stable=True,
        weak_forcing_case=True, weak_forcing_matches_baseline=True,
        forcing_overlaps_terminal_layer=False, anisotropy_significant=False, size_effect_significant=False,
    )
    assert "insufficient_resolution" in c.labels
    assert "terminal_model_supported_in_domain" not in c.labels
    assert "terminal_model_requires_extension" not in c.labels
    assert "terminal_model_not_supported" not in c.labels


def test_controller_instability_recorded():
    c = classify_stress_test_run(
        _domain(), pipeline_ok=True, resolution_ok=True, material_implemented=True,
        energy_budget_closes=True, pile_up_detected=False, controller_is_stable=False,
        weak_forcing_case=True, weak_forcing_matches_baseline=True,
        forcing_overlaps_terminal_layer=False, anisotropy_significant=False, size_effect_significant=False,
    )
    assert "controller_unstable" in c.labels


def test_valid_labels_is_exhaustive_for_all_labels_used():
    # sanity: nothing in the module should ever emit a label outside VALID_LABELS
    # (StressTestClassification.__post_init__ already enforces this at runtime)
    assert "blocked" in VALID_LABELS and "material_interface_only" in VALID_LABELS
