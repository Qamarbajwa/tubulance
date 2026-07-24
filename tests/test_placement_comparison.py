import numpy as np
import pandas as pd
import pytest

from jhtdb_terminal_benchmark import Config
from placement_comparison import (
    ALL_PLACEMENTS,
    DEPLOYABLE_PLACEMENTS,
    compare_placements_on_snapshot,
    identifiability_report,
    run_validation_comparison,
    select_placement,
)


def _make_fetch(n, seed):
    def fetch():
        rng = np.random.default_rng(seed)
        return rng.normal(size=(n, n, n, 3))

    return fetch


def test_compare_placements_runs_all_four_when_configured(tmp_path):
    cfg = Config(parent_band_c1=0.3, parent_band_c2=0.8)
    result = compare_placements_on_snapshot(_make_fetch(64, 1)(), cfg, str(tmp_path))

    assert set(result["per_placement"]) == set(ALL_PLACEMENTS)
    assert all(entry["status"] == "ok" for entry in result["per_placement"].values())
    assert result["per_placement"]["dns_oracle_diagnostic"]["diagnostic_only"] is True
    assert result["per_placement"]["local_cancellation"]["diagnostic_only"] is False


def test_compare_placements_falls_back_to_cfg_parent_band_c1_c2(tmp_path):
    # Regression test: c1/c2 must come from cfg when not passed explicitly
    # to compare_placements_on_snapshot -- previously this silently
    # overwrote cfg's values with None and blocked parent_band.
    cfg = Config(parent_band_c1=0.3, parent_band_c2=0.8)
    result = compare_placements_on_snapshot(_make_fetch(64, 2)(), cfg, str(tmp_path))
    assert result["per_placement"]["parent_band_energy_weighted"]["status"] == "ok"


def test_compare_placements_blocks_parent_band_without_c1_c2(tmp_path):
    cfg = Config()  # no parent_band_c1/c2
    result = compare_placements_on_snapshot(_make_fetch(64, 3)(), cfg, str(tmp_path))
    assert result["per_placement"]["parent_band_energy_weighted"]["status"] == "blocked"


def test_select_placement_uses_only_deployable_placements(tmp_path):
    cfg = Config(parent_band_c1=0.3, parent_band_c2=0.8)
    fetchers = [_make_fetch(64, s) for s in range(3)]

    result = select_placement(fetchers, cfg, str(tmp_path))

    assert result["selected_placement"] in DEPLOYABLE_PLACEMENTS
    assert "dns_oracle_diagnostic" not in {result["selected_placement"]}
    assert (tmp_path / "placement_selection.json").exists()


def test_run_validation_comparison_writes_csv_with_all_placements(tmp_path):
    cfg = Config(parent_band_c1=0.3, parent_band_c2=0.8)
    fetchers = [_make_fetch(64, s) for s in range(4, 7)]

    df = run_validation_comparison(fetchers, cfg, str(tmp_path))

    assert (tmp_path / "placement_validation_comparison.csv").exists()
    assert set(df["placement"].unique()) == set(ALL_PLACEMENTS)
    assert set(df["snapshot"].unique()) == {0, 1, 2}


def test_identifiability_report_structure():
    # Synthetic dataframe mimicking run_validation_comparison output: two
    # snapshots, three deployable placements with a clear metric split
    # between placements that's larger than the (zero) across-snapshot
    # variability -- should be identifiable.
    rows = []
    for snap in range(2):
        for placement, value in [
            ("local_cancellation", 0.1),
            ("parent_band_energy_weighted", 0.9),
            ("turnover_weighted", 0.9),
            ("dns_oracle_diagnostic", 0.95),
        ]:
            rows.append({"snapshot": snap, "placement": placement, "status": "ok", "flux_correlation": value})
    df = pd.DataFrame(rows)

    report = identifiability_report(df)

    assert report["overall_classification"] in (
        "backscatter_placement_identifiable",
        "backscatter_placement_not_identifiable",
    )
    assert "flux_correlation" in report["per_metric"]
    metric_report = report["per_metric"]["flux_correlation"]
    assert metric_report["identifiable"] is True  # placement spread >> zero snapshot spread
    assert metric_report["oracle_mean"] == pytest.approx(0.95)


def test_identifiability_report_flags_not_identifiable_when_placement_spread_is_small():
    rows = []
    rng = np.random.default_rng(0)
    for snap in range(5):
        base = rng.normal()
        for placement in DEPLOYABLE_PLACEMENTS:
            # Same underlying value +/- tiny noise -- placement barely matters,
            # snapshot-to-snapshot variation dominates.
            rows.append(
                {
                    "snapshot": snap,
                    "placement": placement,
                    "status": "ok",
                    "flux_correlation": base + rng.normal(scale=1e-4),
                }
            )
    df = pd.DataFrame(rows)

    report = identifiability_report(df)
    assert report["per_metric"]["flux_correlation"]["identifiable"] is False
