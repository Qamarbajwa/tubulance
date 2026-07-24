import numpy as np
import pytest

from comparison_metrics import extended_region_metrics, region_metrics


def test_region_metrics_perfect_agreement():
    dns = np.array([1.0, -2.0, 3.0, -4.0])
    mask = np.ones(4, dtype=bool)
    result = region_metrics(dns, dns.copy(), mask)
    assert result["correlation"] == pytest.approx(1.0)
    assert result["relative_l2_error"] == pytest.approx(0.0)
    assert result["sign_agreement_fraction"] == pytest.approx(1.0)


def test_extended_region_metrics_correct_shape_wrong_magnitude():
    # Same shape (perfectly correlated), scaled by 10x: shape metrics should
    # be perfect, magnitude metrics should reflect the scale mismatch.
    shells = np.array([1, 2, 3, 4, 5])
    dns = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    model = dns * 10.0
    mask = np.ones(5, dtype=bool)

    result = extended_region_metrics(shells, dns, model, mask)

    assert result["correlation"] == pytest.approx(1.0)
    assert result["spearman_correlation"] == pytest.approx(1.0)
    assert result["cosine_similarity"] == pytest.approx(1.0)
    assert result["relative_l2_error"] > 1.0  # magnitude is very wrong
    assert result["normalized_mean_absolute_error"] > 1.0


def test_extended_region_metrics_correct_magnitude_wrong_shape():
    shells = np.array([1, 2, 3, 4, 5])
    dns = np.array([1.0, 5.0, 1.0, 5.0, 1.0])
    model = np.array([5.0, 1.0, 5.0, 1.0, 5.0])  # same values, reversed pattern
    mask = np.ones(5, dtype=bool)

    result = extended_region_metrics(shells, dns, model, mask)

    assert result["correlation"] < 0  # anti-correlated shape
    assert result["relative_l2_error"] > 0


def test_extended_region_metrics_peak_shell_location_error():
    shells = np.array([1, 2, 3, 4, 5])
    dns = np.array([0.0, 0.0, 10.0, 0.0, 0.0])  # peak at k=3
    model = np.array([0.0, 0.0, 0.0, 10.0, 0.0])  # peak at k=4
    mask = np.ones(5, dtype=bool)

    result = extended_region_metrics(shells, dns, model, mask)

    assert result["peak_shell_location_error"] == pytest.approx(1.0)


def test_extended_region_metrics_empty_mask_is_nan_not_error():
    shells = np.array([1, 2, 3])
    dns = np.array([1.0, 2.0, 3.0])
    model = np.array([1.0, 2.0, 3.0])
    mask = np.zeros(3, dtype=bool)

    result = extended_region_metrics(shells, dns, model, mask)

    assert np.isnan(result["correlation"])
    assert np.isnan(result["peak_shell_location_error"])
