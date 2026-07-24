"""
Run metadata capture
======================

For every real-data run, record exactly what was fetched and how it was
processed -- dataset, spatial origin, cube size, stride, time coordinate,
filtering method, FFT normalization, terminal-layer geometry, resolution
diagnostics, and resource use. Per AGENTS.md: never infer a missing value.
Fields that cannot be determined from the actual fetch call are reported
as an explicit "not recorded" note, not filled in from Config defaults
that may not reflect what was actually fetched (e.g. a local HDF5 read
does not go through Config.start_xyz/size_xyz/stride_xyz at all -- those
fields are unused for that path, so reporting them would misrepresent the
real query).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import h5py

from jhtdb_terminal_benchmark import Config, TerminalLayer

NOT_RECORDED = {"note": "not recorded -- see the fetch call site for this run"}

FILTERING_METHOD = (
    "hard spectral cutoff |k| <= kc via boolean mask multiplication, applied "
    "after divergence-free (I - kk^T/|k|^2) projection of the DNS field "
    "(jhtdb_terminal_benchmark.project_divergence_free, spectral_filter)"
)
FFT_NORMALIZATION = (
    "numpy.fft.fftn, unnormalized forward transform (no 1/N factor); "
    "energy and transfer densities are divided by n3^2 = (nx*ny*nz)^2 "
    "per jhtdb_terminal_benchmark.kinetic_energy_hat()'s convention"
)


@dataclass(frozen=True)
class SpatialOrigin:
    start_xyz: tuple[int, int, int]
    size_xyz: tuple[int, int, int]
    stride_xyz: tuple[int, int, int]
    source: str


def spatial_origin_from_local_h5(path: str) -> SpatialOrigin:
    """Real spatial origin/size/stride as recorded in a local JHTDB HDF5
    export's attrs -- NOT from Config, which is unused by the local-file
    fetch path and would misrepresent what was actually pulled."""
    with h5py.File(path, "r") as f:
        attrs = f.attrs
        start = (int(attrs["x_start"]), int(attrs["y_start"]), int(attrs["z_start"]))
        end = (int(attrs["x_end"]), int(attrs["y_end"]), int(attrs["z_end"]))
        step = (int(attrs["x_step"]), int(attrs["y_step"]), int(attrs["z_step"]))
        size = tuple((e - s) // st + 1 for s, e, st in zip(start, end, step))
    return SpatialOrigin(start_xyz=start, size_xyz=size, stride_xyz=step, source=f"local_h5_attrs:{path}")


def build_run_metadata(
    cfg: Config,
    layer: TerminalLayer,
    nyquist: float,
    *,
    runtime_seconds: float | None = None,
    peak_memory_mb: float | None = None,
    spatial_origin: SpatialOrigin | None = None,
    time_coordinate: dict | None = None,
    populated_terminal_shells: int | None = None,
) -> dict:
    return {
        "dataset": cfg.dataset,
        "spatial_origin": asdict(spatial_origin) if spatial_origin is not None else NOT_RECORDED,
        "time_coordinate": time_coordinate if time_coordinate is not None else NOT_RECORDED,
        "filtering_method": FILTERING_METHOD,
        "fft_normalization": FFT_NORMALIZATION,
        "kc": layer.kc,
        "ks": layer.ks,
        "delta_k": layer.delta_k,
        "n_t": layer.n_t,
        "beta_configured": cfg.beta,
        "beta_effective": layer.beta_effective,
        "terminal_layer_source": layer.source,
        "populated_terminal_shells": populated_terminal_shells,
        "nyquist": nyquist,
        "nyquist_separation": {
            "kc_over_nyquist": layer.kc / nyquist if nyquist else None,
            "nyquist_minus_kc": nyquist - layer.kc if nyquist else None,
        },
        "forcing_separation": (
            {"forcing_kmax": cfg.forcing_kmax, "gap_ks_minus_forcing_kmax": layer.ks - cfg.forcing_kmax}
            if cfg.forcing_kmax is not None
            else {
                "note": (
                    "Config.forcing_kmax not confirmed against official JHTDB "
                    "documentation -- not inferred, see AGENTS.md"
                )
            }
        ),
        "runtime_seconds": runtime_seconds,
        "peak_memory_mb": peak_memory_mb,
    }
