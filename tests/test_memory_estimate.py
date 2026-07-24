import pytest

from memory_estimate import estimate_disk_usage_mb, estimate_peak_memory


def test_estimate_peak_memory_scales_with_n_cubed():
    small = estimate_peak_memory(64)
    large = estimate_peak_memory(128)
    # 128^3 / 64^3 == 8
    assert large.subtotal_mb == pytest.approx(small.subtotal_mb * 8, rel=1e-6)


def test_estimate_peak_memory_breakdown_sums_to_subtotal():
    est = estimate_peak_memory(64)
    assert sum(est.breakdown_mb.values()) == pytest.approx(est.subtotal_mb)
    assert est.peak_estimate_mb == pytest.approx(est.subtotal_mb * est.safety_factor)


def test_estimate_peak_memory_256_cubed_is_multiple_gb():
    est = estimate_peak_memory(256)
    assert est.peak_estimate_mb > 1000  # sanity: not trivially small


def test_estimate_disk_usage_scales_linearly():
    small = estimate_disk_usage_mb(5, 4)
    large = estimate_disk_usage_mb(10, 4)
    assert large == pytest.approx(small * 2)
