"""
Pluggable snapshot data sources (Milestone 5.5)
===================================================

Resolves a manifest.SnapshotSpec into a lazy fetch callable. The critical
safety rail lives here, not just in reporting: if the manifest asserts
`data_is_real=true`, a `source: synthetic` snapshot is refused outright
-- a real-data validation run cannot silently execute against synthetic
data just because someone left a snapshot's source field wrong.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from manifest import SnapshotSpec


class DataSourceError(RuntimeError):
    pass


def local_h5_source(spec: SnapshotSpec) -> Callable[[], np.ndarray]:
    from measure_transfer import load_local_timestep

    def fetch() -> np.ndarray:
        return load_local_timestep(spec.path, spec.frame_index)

    return fetch


def synthetic_source(spec: SnapshotSpec, *, seed: int) -> Callable[[], np.ndarray]:
    def fetch() -> np.ndarray:
        rng = np.random.default_rng(seed)
        n = spec.size[0]
        return rng.normal(size=(n, n, n, 3))

    return fetch


def sciserver_source(spec: SnapshotSpec) -> Callable[[], np.ndarray]:
    def fetch() -> np.ndarray:
        raise DataSourceError(
            "SciServer/Giverny data source is not available in this environment -- "
            "see AGENTS.md 'Part A' blocker. This snapshot cannot be fetched here; "
            "run this manifest on SciServer with giverny installed and configured."
        )

    return fetch


def resolve_data_source(
    spec: SnapshotSpec, *, data_is_real: bool, seed: int = 0
) -> Callable[[], np.ndarray]:
    if spec.source == "synthetic":
        if data_is_real:
            raise DataSourceError(
                "manifest asserts classification.data_is_real=true but a snapshot's "
                "source is 'synthetic' -- refusing to run a real-data validation "
                "against synthetic data."
            )
        return synthetic_source(spec, seed=seed)
    if spec.source == "local_h5":
        return local_h5_source(spec)
    if spec.source == "sciserver":
        return sciserver_source(spec)
    raise DataSourceError(f"Unknown snapshot source {spec.source!r}")
