import numpy as np
import pytest

from forcing_test_matrix import (
    ALL_CASES, CALIBRATION_CASES, VALIDATION_CASES, assert_case_separation, CaseSeparationError,
    resolve_forcing_case, cases_by_split,
)
from jhtdb_terminal_benchmark import wavenumbers, compute_terminal_layer, Config


def test_at_least_fourteen_cases():
    assert len(ALL_CASES) >= 14


def test_calibration_and_validation_are_disjoint():
    assert_case_separation()  # should not raise
    names_cal = {c.name for c in CALIBRATION_CASES}
    names_val = {c.name for c in VALIDATION_CASES}
    assert names_cal.isdisjoint(names_val)


def test_calibration_set_matches_spec_menu():
    types = {c.forcing_type for c in CALIBRATION_CASES}
    # weak isotropic, moderate isotropic, one directional case
    assert "isotropic_random" in types
    assert any(c.direction is not None for c in CALIBRATION_CASES)


def test_validation_set_includes_required_case_kinds():
    names = {c.name for c in VALIDATION_CASES}
    assert "forcing_overlap_terminal_layer" in names  # terminal-overlap case
    assert "pulsed" in names  # pulsed case
    assert any(c.direction is not None for c in VALIDATION_CASES)  # directional case


def test_manual_separation_violation_detected():
    import forcing_test_matrix as ftm

    original = ftm.VALIDATION_CASES
    try:
        ftm.VALIDATION_CASES = ftm.CALIBRATION_CASES  # deliberately break disjointness
        with pytest.raises(CaseSeparationError):
            ftm.assert_case_separation()
    finally:
        ftm.VALIDATION_CASES = original


def test_resolve_forcing_case_respects_terminal_layer_ordering():
    kx, ky, kz = wavenumbers(64, 2 * np.pi)
    nyquist = float(np.max(np.abs(kx[:, 0, 0])))
    delta_k = 1.0
    layer = compute_terminal_layer(0.5 * nyquist, delta_k, Config())
    assert layer.ks > 0  # sanity: this grid resolves a proper layer

    far = next(c for c in ALL_CASES if c.name == "forcing_far_below_ks")
    near = next(c for c in ALL_CASES if c.name == "forcing_near_ks")
    overlap = next(c for c in ALL_CASES if c.name == "forcing_overlap_terminal_layer")
    small = next(c for c in ALL_CASES if c.name == "small_scale_forcing")

    fs_far = resolve_forcing_case(far, layer, nyquist, delta_k)
    fs_near = resolve_forcing_case(near, layer, nyquist, delta_k)
    fs_overlap = resolve_forcing_case(overlap, layer, nyquist, delta_k)
    fs_small = resolve_forcing_case(small, layer, nyquist, delta_k)

    assert fs_far.injection_wavenumber < fs_near.injection_wavenumber < layer.ks
    assert layer.ks <= fs_overlap.injection_wavenumber <= layer.kc
    assert fs_small.injection_wavenumber > layer.kc


def test_multi_scale_case_has_multiple_wavenumbers():
    kx, ky, kz = wavenumbers(64, 2 * np.pi)
    nyquist = float(np.max(np.abs(kx[:, 0, 0])))
    layer = compute_terminal_layer(0.5 * nyquist, 1.0, Config())
    multi = next(c for c in ALL_CASES if c.name == "multi_scale_forcing")
    fs = resolve_forcing_case(multi, layer, nyquist, 1.0)
    assert len(fs.injection_wavenumbers) >= 2


def test_cases_by_split():
    assert cases_by_split("calibration") == CALIBRATION_CASES
    assert cases_by_split("validation") == VALIDATION_CASES
    assert len(cases_by_split("all")) == len(ALL_CASES)
    with pytest.raises(ValueError):
        cases_by_split("bogus")
