import json

from report_generator import generate_reports


def test_generate_reports_defaults_to_synthetic_warning(tmp_path):
    json_path, md_path = generate_reports(str(tmp_path))

    assert json_path.exists()
    assert md_path.exists()

    report = json.loads(json_path.read_text())
    assert report["data_is_real"] is False
    assert "SYNTHETIC" in report["data_provenance_warning"]
    assert "WARNING" in md_path.read_text()


def test_generate_reports_no_warning_when_marked_real(tmp_path):
    json_path, md_path = generate_reports(str(tmp_path), data_is_real=True)

    report = json.loads(json_path.read_text())
    assert report["data_is_real"] is True
    assert report["data_provenance_warning"] is None
    assert "WARNING" not in md_path.read_text()


def test_generate_reports_includes_unresolved_gaps_and_statement_boundaries(tmp_path):
    json_path, _ = generate_reports(str(tmp_path))
    report = json.loads(json_path.read_text())

    assert len(report["unresolved_theory_gaps"]) > 0
    assert len(report["statements_supported"]) > 0
    assert len(report["statements_not_supported"]) > 0
    assert "predictive" in " ".join(report["statements_not_supported"]).lower()


def test_generate_reports_embeds_ensemble_and_placement_data(tmp_path):
    ensemble_result = {
        "aggregate": {"terminal_region_correlation": {"mean": 0.5}},
        "dataset_level_classification": {
            "label": "criteria not met",
            "n_snapshots_ok": 5,
            "n_snapshots_total": 5,
            "checks": {"at_least_five_snapshots_pass_structural_checks": True},
        },
    }
    identifiability = {
        "overall_classification": "backscatter_placement_not_identifiable",
        "interpretation": "test interpretation",
    }
    placement_selection = {"selection_metric": "flux_relative_l2_error", "selected_placement": "local_cancellation"}

    json_path, md_path = generate_reports(
        str(tmp_path),
        ensemble_result=ensemble_result,
        placement_selection=placement_selection,
        identifiability=identifiability,
    )

    report = json.loads(json_path.read_text())
    assert report["structural_validation"]["n_snapshots_ok"] == 5
    assert report["classification_outcome"] == "criteria not met"
    assert report["identifiability"]["overall_classification"] == "backscatter_placement_not_identifiable"

    md_text = md_path.read_text()
    assert "backscatter_placement_not_identifiable" in md_text
    assert "local_cancellation" in md_text
