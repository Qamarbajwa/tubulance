import numpy as np
import pytest

from milestone_5_7_stress_test import (
    run_one, run_campaign, applicability_map, COMPARISON_GROUPS, GROUP_DESCRIPTIONS, GRID_TIER_DIAGNOSTIC_ONLY,
)
from forcing_test_matrix import CALIBRATION_CASES


def test_all_six_comparison_groups_defined():
    assert set(COMPARISON_GROUPS) == set("ABCDEF")
    assert set(GROUP_DESCRIPTIONS) == set("ABCDEF")


def test_grid_32_is_diagnostic_only():
    assert 32 in GRID_TIER_DIAGNOSTIC_ONLY


def test_run_one_material_interface_only_short_circuits_without_solving():
    r = run_one(CALIBRATION_CASES[0], "generic_compressible_gas_placeholder", 32, "A", n_steps=3)
    assert r.classification.labels == ("material_interface_only",)
    assert r.pipeline_ok is False


@pytest.mark.parametrize("group", ["A", "C", "D", "E", "F"])
def test_run_one_each_group_runs_at_diagnostic_grid(group):
    r = run_one(CALIBRATION_CASES[0], "incompressible_newtonian_liquid", 32, group, n_steps=8)
    assert r.group == group
    assert r.pipeline_ok is True
    assert "insufficient_resolution" in r.classification.labels  # 32^3 always diagnostic-only per spec
    assert np.isfinite(r.phi_l) or r.phi_l != r.phi_l  # finite or a legitimate nan, never crashes


def test_run_one_records_full_domain_on_success():
    r = run_one(CALIBRATION_CASES[0], "incompressible_newtonian_liquid", 32, "A", n_steps=8)
    assert r.domain.forcing_case == CALIBRATION_CASES[0].name
    assert r.domain.material == "incompressible_newtonian_liquid"
    assert r.domain.grid_n == 32


def test_run_campaign_produces_one_result_per_combination():
    cases = list(CALIBRATION_CASES[:2])
    results = run_campaign(cases=cases, materials=["incompressible_newtonian_liquid"], grid_ns=[32], groups=["A", "D"], n_steps=6)
    assert len(results) == len(cases) * 1 * 2


def test_applicability_map_aggregates_by_axis():
    cases = list(CALIBRATION_CASES[:1])
    results = run_campaign(cases=cases, materials=["incompressible_newtonian_liquid"], grid_ns=[32], groups=["A"], n_steps=6)
    am = applicability_map(results)
    assert am["n_runs"] == 1
    assert 32 in am["by_grid_n"]
    assert "incompressible_newtonian_liquid" in am["by_material"]


def test_campaign_never_crashes_on_interface_only_material_mixed_in():
    cases = list(CALIBRATION_CASES[:1])
    results = run_campaign(
        cases=cases, materials=["incompressible_newtonian_liquid", "simplified_viscoelastic_candidate"],
        grid_ns=[32], groups=["A"], n_steps=6,
    )
    labels = {r.material_name: r.classification.labels for r in results}
    assert labels["simplified_viscoelastic_candidate"] == ("material_interface_only",)
    assert labels["incompressible_newtonian_liquid"] != ("material_interface_only",)
