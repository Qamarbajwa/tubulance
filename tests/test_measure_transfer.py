import pytest

from measure_transfer import TemporalMetadataError, TimeCoordinate, resolve_dt


def _tc(requested, dt_confirmed, returned=None):
    return TimeCoordinate(
        requested_time=requested,
        frame_index=None,
        returned_time=returned,
        interpolation_method="test",
        dimensional=True,
        source="test",
        dt_confirmed=dt_confirmed,
    )


def test_resolve_dt_raises_when_unconfirmed():
    t1 = _tc(1.0, dt_confirmed=False)
    t2 = _tc(2.0, dt_confirmed=True)
    with pytest.raises(TemporalMetadataError):
        resolve_dt(t1, t2)


def test_resolve_dt_uses_returned_time_when_available():
    t1 = _tc(1.0, dt_confirmed=True, returned=1.002)
    t2 = _tc(2.0, dt_confirmed=True, returned=2.004)
    assert resolve_dt(t1, t2) == pytest.approx(1.002)


def test_resolve_dt_uses_requested_time_when_returned_time_missing():
    t1 = _tc(0.0, dt_confirmed=True)
    t2 = _tc(0.5, dt_confirmed=True)
    assert resolve_dt(t1, t2) == pytest.approx(0.5)
