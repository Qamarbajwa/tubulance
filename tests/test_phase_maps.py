from stress_test_classification import RunDomain, StressTestClassification
from phase_maps import region_from_classification, build_phase_map, summarize_regions, MAP_REGIONS


def _cls(labels):
    domain = RunDomain(
        forcing_case="x", material="incompressible_newtonian_liquid", grid_n=64, forcing_type="isotropic_random",
        phi_l_regime="competing", theta_f_regime="resonant_or_competing", k_f_vs_ks="below",
    )
    return StressTestClassification(domain=domain, labels=labels)


def test_region_mapping_supported():
    c = _cls(("pipeline_only", "energy_budget_valid", "controller_stable", "terminal_model_supported_in_domain"))
    assert region_from_classification(c) == "original_model_valid"


def test_region_mapping_marginal_when_controller_unstable():
    c = _cls(("pipeline_only", "controller_unstable", "terminal_model_supported_in_domain"))
    assert region_from_classification(c) == "original_model_marginal"


def test_region_mapping_requires_extension():
    c = _cls(("pipeline_only", "forcing_overlap_invalidates_assumption", "terminal_model_requires_extension"))
    assert region_from_classification(c) == "forcing_aware_model_required"


def test_region_mapping_unresolved():
    c = _cls(("insufficient_resolution",))
    assert region_from_classification(c) == "unresolved"


def test_region_mapping_blocked_and_not_supported():
    assert region_from_classification(_cls(("blocked",))) == "physically_unsupported"
    assert region_from_classification(_cls(("terminal_model_not_supported",))) == "physically_unsupported"


def test_build_phase_map_and_summary():
    points = [
        {"phi_l": 0.01, "theta_f": 5.0, "classification": _cls(("pipeline_only", "terminal_model_supported_in_domain", "controller_stable"))},
        {"phi_l": 100.0, "theta_f": 0.1, "classification": _cls(("insufficient_resolution",))},
    ]
    from phase_maps import phi_theta_map

    mapped = phi_theta_map(points)
    assert len(mapped) == 2
    assert mapped[0].region == "original_model_valid"
    assert mapped[1].region == "unresolved"

    counts = summarize_regions(mapped)
    assert set(counts.keys()) == set(MAP_REGIONS)
    assert counts["original_model_valid"] == 1
    assert counts["unresolved"] == 1
