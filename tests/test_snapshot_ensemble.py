import numpy as np

from jhtdb_terminal_benchmark import Config
from snapshot_ensemble import dataset_level_classification, run_ensemble


def _make_fetch(n, seed):
    def fetch():
        rng = np.random.default_rng(seed)
        return rng.normal(size=(n, n, n, 3))

    return fetch


def test_run_ensemble_separates_ok_and_blocked_snapshots(tmp_path):
    fetchers = [_make_fetch(64, s) for s in range(3)] + [_make_fetch(16, 99)]
    result = run_ensemble(fetchers, Config(), output_dir=str(tmp_path), min_snapshots=3)

    statuses = list(result["per_snapshot_status"].values())
    assert statuses.count("ok") == 3
    assert statuses.count("blocked") == 1
    assert (tmp_path / "ensemble_per_snapshot.csv").exists()
    assert (tmp_path / "ensemble_summary.json").exists()
    assert (tmp_path / "ensemble_summary.png").exists()


def test_run_ensemble_aggregate_has_mean_std_median_worst_case(tmp_path):
    fetchers = [_make_fetch(64, s) for s in range(4)]
    result = run_ensemble(fetchers, Config(), output_dir=str(tmp_path), min_snapshots=4)

    agg = result["aggregate"]["terminal_region_correlation"]
    assert set(agg) == {"mean", "std", "median", "worst_case", "n"}
    assert agg["n"] == 4


def _complete_snapshot(corr=0.5, classification="forward_validation_required"):
    return {
        "_status": "ok",
        "classification": classification,
        "global_nonlinear_conservation": {"relative_residual": 1e-9},
        "model_transfer_conservation": {"residual": 0.0},
        "energy_above_cutoff_filtered": 0.0,
        "energy_above_cutoff_terminal": 0.0,
        "n_t": 8.0,
        "populated_terminal_shells": 5,
        "regions": {"terminal_region": {"correlation": corr}},
        "bottleneck_ratio_relative_to_filtered_dns": 0.9,
    }


def test_dataset_level_classification_fails_below_min_snapshots():
    per_snapshot = [_complete_snapshot() for _ in range(3)]
    result = dataset_level_classification(per_snapshot, Config(), min_snapshots=5)
    assert result["checks"]["at_least_five_snapshots_pass_structural_checks"] is False
    assert result["dataset_shows_a_priori_consistency"] is False


def test_dataset_level_classification_all_pass():
    def snapshot(corr):
        return {
            "_status": "ok",
            "classification": "forward_validation_required",
            "global_nonlinear_conservation": {"relative_residual": 1e-9},
            "model_transfer_conservation": {"residual": 0.0},
            "energy_above_cutoff_filtered": 0.0,
            "energy_above_cutoff_terminal": 0.0,
            "n_t": 8.0,
            "populated_terminal_shells": 5,
            "regions": {"terminal_region": {"correlation": corr}},
            "bottleneck_ratio_relative_to_filtered_dns": 0.9,
        }

    per_snapshot = [snapshot(0.5) for _ in range(5)]
    result = dataset_level_classification(per_snapshot, Config(), min_snapshots=5)

    assert all(result["checks"].values())
    assert result["dataset_shows_a_priori_consistency"] is True
    assert result["no_severe_bottleneck_determination"].startswith("not auto-determined")


def test_dataset_level_classification_fails_when_minority_positive():
    def snapshot(corr):
        return {
            "_status": "ok",
            "classification": "forward_validation_required",
            "global_nonlinear_conservation": {"relative_residual": 1e-9},
            "model_transfer_conservation": {"residual": 0.0},
            "energy_above_cutoff_filtered": 0.0,
            "energy_above_cutoff_terminal": 0.0,
            "n_t": 8.0,
            "populated_terminal_shells": 5,
            "regions": {"terminal_region": {"correlation": corr}},
            "bottleneck_ratio_relative_to_filtered_dns": 0.9,
        }

    per_snapshot = [snapshot(0.5), snapshot(-0.2), snapshot(-0.3), snapshot(-0.1), snapshot(-0.4)]
    result = dataset_level_classification(per_snapshot, Config(), min_snapshots=5)

    assert result["checks"]["transfer_agreement_positive_in_majority_of_snapshots"] is False
    assert result["dataset_shows_a_priori_consistency"] is False
