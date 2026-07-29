import numpy as np
import pytest

from forcing import (
    ForcingState, ForcingConfigError, ForcingDominanceThresholds,
    forcing_dominance_ratio, classify_forcing_regime, forcing_timescale_ratio,
    classify_timescale_regime, forcing_alignment, eddy_turnover_time,
)


def test_forcing_state_validates_forcing_type():
    with pytest.raises(ForcingConfigError):
        ForcingState(power_input=1.0, injection_wavenumber=2.0, timescale=1.0, forcing_type="not_a_type")


def test_forcing_state_requires_direction_for_directional_types():
    with pytest.raises(ForcingConfigError):
        ForcingState(power_input=1.0, injection_wavenumber=2.0, timescale=1.0, forcing_type="fixed_direction")
    # ok with direction supplied
    ForcingState(power_input=1.0, injection_wavenumber=2.0, timescale=1.0, forcing_type="fixed_direction", direction=(1, 0, 0))


def test_forcing_state_requires_extra_wavenumbers_for_multi_scale():
    with pytest.raises(ForcingConfigError):
        ForcingState(power_input=1.0, injection_wavenumber=2.0, timescale=1.0, forcing_type="multi_scale")
    fs = ForcingState(power_input=1.0, injection_wavenumber=2.0, timescale=1.0, forcing_type="multi_scale", extra_wavenumbers=(5.0,))
    assert fs.injection_wavenumbers == (2.0, 5.0)


def test_phi_l_regime_classification_boundaries():
    thresholds = ForcingDominanceThresholds(nonlinear_dominated_below=0.1, forcing_dominated_above=10.0)
    assert classify_forcing_regime(0.01, thresholds) == "nonlinear_dominated"
    assert classify_forcing_regime(1.0, thresholds) == "competing"
    assert classify_forcing_regime(100.0, thresholds) == "forcing_dominated"


def test_phi_l_is_scale_correct():
    # doubling forcing power doubles Phi_l; doubling u_l divides Phi_l by 8
    phi1 = forcing_dominance_ratio(1.0, 1.0, 1.0)
    phi2 = forcing_dominance_ratio(2.0, 1.0, 1.0)
    assert phi2 == pytest.approx(2.0 * phi1)
    phi3 = forcing_dominance_ratio(1.0, 2.0, 1.0)
    assert phi3 == pytest.approx(phi1 / 8.0)


def test_phi_l_requires_positive_scales():
    with pytest.raises(ValueError):
        forcing_dominance_ratio(1.0, 0.0, 1.0)
    with pytest.raises(ValueError):
        forcing_dominance_ratio(1.0, 1.0, 0.0)


def test_theta_f_ratio_and_classification():
    assert forcing_timescale_ratio(10.0, 1.0) == pytest.approx(10.0)
    assert classify_timescale_regime(10.0) == "quasi_steady"
    assert classify_timescale_regime(1.0) == "resonant_or_competing"
    assert classify_timescale_regime(0.01) == "rapid"


def test_forcing_alignment_perfectly_aligned_and_orthogonal():
    rng = np.random.default_rng(0)
    shape = (3, 4, 4, 4)
    base = rng.normal(size=shape)
    aligned = forcing_alignment(base, base)
    assert aligned == pytest.approx(1.0)

    # Construct an exactly-orthogonal pair via a per-voxel rotation in the
    # (u1,u2) plane: f = u2, u = u1, with u1.u2 summed to zero by
    # construction (checkerboard sign flip on one component).
    u = np.zeros(shape)
    f = np.zeros(shape)
    u[0] = 1.0
    f[1] = 1.0
    orth = forcing_alignment(u, f)
    assert orth == pytest.approx(0.0, abs=1e-10)


def test_forcing_alignment_undefined_for_zero_field():
    zeros = np.zeros((3, 4, 4, 4))
    ones = np.ones((3, 4, 4, 4))
    assert np.isnan(forcing_alignment(zeros, ones))


def test_eddy_turnover_time_positive_inputs_required():
    assert eddy_turnover_time(2.0, 4.0) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        eddy_turnover_time(0.0, 1.0)
    with pytest.raises(ValueError):
        eddy_turnover_time(1.0, 0.0)
