import numpy as np
import pytest

from data_sources import DataSourceError, resolve_data_source
from manifest import SnapshotSpec


def test_synthetic_source_produces_correctly_shaped_field_when_not_real():
    spec = SnapshotSpec(time=0.0, origin=(0, 0, 0), size=(32, 32, 32), source="synthetic")
    fetch = resolve_data_source(spec, data_is_real=False, seed=1)
    v = fetch()
    assert v.shape == (32, 32, 32, 3)


def test_synthetic_source_refused_when_data_is_real_true():
    spec = SnapshotSpec(time=0.0, origin=(0, 0, 0), size=(32, 32, 32), source="synthetic")
    with pytest.raises(DataSourceError, match="data_is_real"):
        resolve_data_source(spec, data_is_real=True, seed=1)


def test_local_h5_source_reads_real_cached_file():
    spec = SnapshotSpec(
        time=1.0,
        origin=(100, 100, 100),
        size=(16, 16, 16),
        source="local_h5",
        path="isotropic1024coarse.h5",
        frame_index=1,
    )
    fetch = resolve_data_source(spec, data_is_real=False)
    v = fetch()
    assert v.shape == (16, 16, 16, 3)


def test_sciserver_source_raises_clearly_when_fetched():
    spec = SnapshotSpec(time=0.0, origin=(0, 0, 0), size=(128, 128, 128), source="sciserver")
    fetch = resolve_data_source(spec, data_is_real=True)
    with pytest.raises(DataSourceError, match="SciServer"):
        fetch()


def test_unknown_source_raises():
    spec = SnapshotSpec(time=0.0, origin=(0, 0, 0), size=(32, 32, 32), source="synthetic")
    object.__setattr__(spec, "source", "made_up_source")  # bypass frozen dataclass for the test
    with pytest.raises(DataSourceError):
        resolve_data_source(spec, data_is_real=False)
