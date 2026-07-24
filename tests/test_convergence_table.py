import numpy as np

from convergence_table import ResolutionSpec, run_at_resolution, run_convergence_table
from jhtdb_terminal_benchmark import Config


def _synthetic_velocity(n, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, n, n, 3))


def test_run_at_resolution_reports_no_data_without_fetch():
    row = run_at_resolution(ResolutionSpec(grid_n=128, fetch=None), Config())
    assert row["status"] == "no_data"
    assert row["grid_n"] == 128
    assert "note" in row


def test_run_at_resolution_reports_blocked_for_small_grid():
    row = run_at_resolution(
        ResolutionSpec(grid_n=16, fetch=lambda: _synthetic_velocity(16, seed=1)), Config()
    )
    assert row["status"] == "blocked"
    assert "N_T" in row["failures"]
    assert row["runtime_seconds"] >= 0


def test_run_at_resolution_reports_ok_and_metrics_for_adequate_grid():
    row = run_at_resolution(
        ResolutionSpec(grid_n=64, fetch=lambda: _synthetic_velocity(64, seed=2)), Config()
    )
    assert row["status"] == "ok"
    for key in ("spectrum_error", "transfer_error", "flux_error", "bottleneck_ratio", "classification"):
        assert key in row


def test_run_convergence_table_writes_csv(tmp_path):
    specs = [
        ResolutionSpec(grid_n=16, fetch=lambda: _synthetic_velocity(16, seed=1)),
        ResolutionSpec(grid_n=128, fetch=None),
    ]
    df = run_convergence_table(specs, Config(), output_dir=str(tmp_path))
    assert len(df) == 2
    assert (tmp_path / "convergence_table.csv").exists()
