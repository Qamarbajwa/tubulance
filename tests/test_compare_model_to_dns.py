import numpy as np
import pytest

from compare_model_to_dns import compare
from jhtdb_terminal_benchmark import Config, InsufficientResolutionError
from measure_transfer import TemporalMetadataError, TimeCoordinate


def _tc(requested, dt_confirmed):
    return TimeCoordinate(
        requested_time=requested,
        frame_index=None,
        returned_time=None,
        interpolation_method="test",
        dimensional=True,
        source="test",
        dt_confirmed=dt_confirmed,
    )


def _synthetic_velocity(n, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, n, n, 3))


def test_compare_raises_without_confirmed_dt(tmp_path):
    cfg = Config()
    v1 = _synthetic_velocity(16, seed=1)
    v2 = _synthetic_velocity(16, seed=2)
    t1 = _tc(1.0, dt_confirmed=False)
    t2 = _tc(2.0, dt_confirmed=True)
    with pytest.raises(TemporalMetadataError):
        compare(v1, v2, t1, t2, cfg, output_dir=str(tmp_path))


def test_compare_raises_on_insufficient_resolution(tmp_path):
    # 16^3 grid at default cutoff_fraction cannot host a 6-shell terminal layer.
    cfg = Config()
    v1 = _synthetic_velocity(16, seed=1)
    v2 = _synthetic_velocity(16, seed=2)
    t1 = _tc(1.0, dt_confirmed=True)
    t2 = _tc(1.002, dt_confirmed=True)
    with pytest.raises(InsufficientResolutionError):
        compare(v1, v2, t1, t2, cfg, output_dir=str(tmp_path))


def test_compare_full_synthetic_pass(tmp_path):
    # 64^3 grid is large enough for beta=0.56 to yield N_T >= 6.
    cfg = Config()
    v1 = _synthetic_velocity(64, seed=1)
    v2 = _synthetic_velocity(64, seed=2)
    t1 = _tc(1.0, dt_confirmed=True)
    t2 = _tc(1.002, dt_confirmed=True)

    result = compare(v1, v2, t1, t2, cfg, output_dir=str(tmp_path))

    assert result["terminal_layer_source"] == "beta"
    assert result["n_t"] >= cfg.min_terminal_shells
    assert set(result["regions"]) == {
        "ordinary_resolved_region",
        "terminal_region",
        "final_two_shells_before_kc",
        "all_permitted",
    }
    assert np.isfinite(result["terminal_power_ratio"])
    assert (tmp_path / "model_vs_dns_summary.json").exists()
    assert (tmp_path / "model_vs_dns_per_shell.csv").exists()
    assert (tmp_path / "model_vs_dns.png").exists()
