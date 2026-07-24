import numpy as np
import pandas as pd
import pytest

from backscatter_placement import PlacementConfigError
from jhtdb_terminal_benchmark import Config, InsufficientResolutionError
from nonlinear_transfer_validation import validate


def _synthetic_velocity(n, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, n, n, 3))


def test_validate_raises_on_insufficient_resolution(tmp_path):
    cfg = Config()
    v = _synthetic_velocity(16, seed=1)
    with pytest.raises(InsufficientResolutionError):
        validate(v, cfg, output_dir=str(tmp_path))


def test_validate_full_synthetic_pass_without_forcing_kmax(tmp_path):
    cfg = Config()
    v = _synthetic_velocity(64, seed=3)

    result = validate(v, cfg, output_dir=str(tmp_path))

    assert result["classification"] in (
        "nonlinear_transfer_comparison_valid",
        "forward_validation_required",
    )
    assert result["regions"]["forcing_region"] == {
        "unavailable_reason": "Config.forcing_kmax not set -- see AGENTS.md"
    }
    assert set(result["regions"]) == {
        "forcing_region",
        "inertial_resolved_region",
        "terminal_region",
        "final_two_shells_before_kc",
    }
    # Filtering must enforce exactly zero energy above the cutoff.
    assert result["energy_above_cutoff_filtered"] == pytest.approx(0.0)
    assert result["energy_above_cutoff_terminal"] == pytest.approx(0.0)
    assert np.isfinite(result["global_nonlinear_conservation"]["relative_residual"])
    assert (tmp_path / "nonlinear_transfer_summary.json").exists()
    assert (tmp_path / "nonlinear_transfer_per_shell.csv").exists()
    assert (tmp_path / "nonlinear_transfer_comparison.png").exists()


def test_validate_reports_forcing_region_when_configured(tmp_path):
    cfg = Config(forcing_kmax=2.0, min_forcing_terminal_gap_shells=0.0)
    v = _synthetic_velocity(64, seed=4)

    result = validate(v, cfg, output_dir=str(tmp_path))

    assert "unavailable_reason" not in result["regions"]["forcing_region"]
    assert "correlation" in result["regions"]["forcing_region"]


def test_validate_dealias_reduces_conservation_residual(tmp_path):
    cfg = Config()
    v = _synthetic_velocity(64, seed=5)

    result_raw = validate(v, cfg, output_dir=str(tmp_path / "raw"), dealias=False)
    result_dealiased = validate(v, cfg, output_dir=str(tmp_path / "dealiased"), dealias=True)

    residual_raw = result_raw["global_nonlinear_conservation"]["relative_residual"]
    residual_dealiased = result_dealiased["global_nonlinear_conservation"]["relative_residual"]
    assert residual_dealiased <= residual_raw + 1e-12


def test_t_model_equals_heat_only_under_local_backscatter_placement(tmp_path):
    # T_model(k) = T_remove(k) + T_return(k) = -gamma*E + (1-alpha)*gamma*E
    # = -alpha*gamma*E exactly under "local" placement -- verify the
    # per-shell CSV satisfies this identity directly, not just that the
    # code runs.
    cfg = Config()
    v = _synthetic_velocity(64, seed=6)

    validate(v, cfg, output_dir=str(tmp_path))
    df = pd.read_csv(tmp_path / "nonlinear_transfer_per_shell.csv")

    np.testing.assert_allclose(df["T_model"], df["T_model_heat"], atol=1e-12)
    np.testing.assert_allclose(
        df["T_model_remove"] + df["T_model_return"], df["T_model"], atol=1e-12
    )


def test_model_transfer_conservation_residual_is_near_zero(tmp_path):
    cfg = Config()
    v = _synthetic_velocity(64, seed=7)

    result = validate(v, cfg, output_dir=str(tmp_path))
    conservation = result["model_transfer_conservation"]

    assert conservation["backscatter_placement"] == "local_cancellation"
    assert abs(conservation["residual"]) < 1e-9
    # Total heat should be non-negative (it's a sink, reported as a
    # positive magnitude) whenever the operator actually removed energy.
    assert conservation["total_heat"] >= -1e-12


def test_removal_only_comparison_restricted_to_dns_net_loss_shells(tmp_path):
    cfg = Config()
    v = _synthetic_velocity(64, seed=8)

    result = validate(v, cfg, output_dir=str(tmp_path))
    df = pd.read_csv(tmp_path / "nonlinear_transfer_per_shell.csv")
    permitted = (df["k"] > 0) & (df["k"] <= result["kc"])
    expected_n = int((permitted & (df["T_dns"] < 0)).sum())

    assert result["removal_only_comparison"]["n_shells"] == expected_n


def test_flux_comparison_present_with_plateau_metric(tmp_path):
    cfg = Config()
    v = _synthetic_velocity(64, seed=9)

    result = validate(v, cfg, output_dir=str(tmp_path))

    assert "relative_l2_error" in result["flux_comparison"]
    assert "spearman_correlation" in result["flux_comparison"]
    assert np.isfinite(result["flux_plateau_error_below_ks"])


def test_unsupported_backscatter_placement_raises(tmp_path):
    cfg = Config(backscatter_placement="global_uniform")
    v = _synthetic_velocity(64, seed=10)

    with pytest.raises(PlacementConfigError):
        validate(v, cfg, output_dir=str(tmp_path))


def test_parent_band_placement_requires_preregistered_c1_c2(tmp_path):
    cfg = Config(backscatter_placement="parent_band_energy_weighted")
    v = _synthetic_velocity(64, seed=11)

    with pytest.raises(PlacementConfigError):
        validate(v, cfg, output_dir=str(tmp_path))


def test_parent_band_placement_runs_and_conserves_when_configured(tmp_path):
    cfg = Config(backscatter_placement="parent_band_energy_weighted", parent_band_c1=0.3, parent_band_c2=0.8)
    v = _synthetic_velocity(64, seed=11)

    result = validate(v, cfg, output_dir=str(tmp_path))

    assert result["model_transfer_conservation"]["backscatter_placement"] == "parent_band_energy_weighted"
    assert abs(result["model_transfer_conservation"]["residual"]) < 1e-6


def test_dns_oracle_placement_is_flagged_diagnostic_only(tmp_path):
    cfg = Config(backscatter_placement="dns_oracle_diagnostic")
    v = _synthetic_velocity(64, seed=12)

    result = validate(v, cfg, output_dir=str(tmp_path))

    assert result["model_transfer_conservation"]["diagnostic_only"] is True


def test_turnover_weighted_placement_runs_and_conserves(tmp_path):
    cfg = Config(backscatter_placement="turnover_weighted")
    v = _synthetic_velocity(64, seed=13)

    result = validate(v, cfg, output_dir=str(tmp_path))

    assert result["model_transfer_conservation"]["diagnostic_only"] is False
    assert abs(result["model_transfer_conservation"]["residual"]) < 1e-6
