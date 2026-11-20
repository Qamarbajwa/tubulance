"""Tests for navier3d.profiling: StepProfiler."""
from navier3d.profiling import StepProfiler


def test_report_percentages_sum_to_100() -> None:
    p = StepProfiler()
    p.add("convection", 1.0)
    p.add("pressure_solve", 5.0)
    p.add("diffusion_solve", 2.0)
    rows = p.report(total_category="total")  # no explicit 'total' -> falls back to sum
    assert abs(sum(r.percent for r in rows) - 100.0) < 1e-9
    assert rows[0].category == "pressure_solve"  # sorted, most expensive first


def test_add_accumulates_across_multiple_calls() -> None:
    p = StepProfiler()
    p.add("x", 1.0)
    p.add("x", 2.0)
    assert p.totals["x"] == 3.0


def test_negative_durations_clamped_to_zero() -> None:
    p = StepProfiler()
    p.add("x", -5.0)
    assert p.totals["x"] == 0.0


def test_explicit_total_category_used_for_percentages() -> None:
    p = StepProfiler()
    p.add("a", 1.0)
    p.add("b", 1.0)
    p.add("total", 10.0)  # explicit total larger than sum of sub-categories (e.g. untracked overhead)
    rows = {r.category: r.percent for r in p.report(total_category="total")}
    assert abs(rows["a"] - 10.0) < 1e-9
    assert abs(rows["b"] - 10.0) < 1e-9
    assert abs(rows["total"] - 100.0) < 1e-9


def test_empty_profiler_report_is_empty() -> None:
    p = StepProfiler()
    assert p.report() == []
    assert "no profiling data" in p.format_report()


def test_format_report_is_human_readable() -> None:
    p = StepProfiler()
    p.add("pressure_solve", 5.0)
    p.add("convection", 1.0)
    p.add("total", 6.0)
    text = p.format_report()
    assert "pressure_solve" in text
    assert "%" in text
    assert "total" not in text  # total_category itself excluded from the printed rows


def test_reset_clears_totals() -> None:
    p = StepProfiler()
    p.add("x", 1.0)
    p.reset()
    assert p.totals == {}
