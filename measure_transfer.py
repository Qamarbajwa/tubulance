"""
Two-snapshot filtered-energy transfer measurement
===================================================

Second stage referenced in README.md: use two JHTDB snapshots separated by a
known interval to measure the actual sub-filter energy transfer, ahead of
running the complete forward model over the same interval.

IMPORTANT -- what this measures:

The quantity computed here, dE(k) = E(k, t2) - E(k, t1), is a raw
finite-difference energy-evolution measurement. It is NOT an isolated
nonlinear-cascade transfer: it bundles resolved-resolved triadic transfer,
resolved/unresolved (subfilter) transfer, and whatever forcing, viscosity,
and pressure did to the resolved field over the interval. Do not interpret
it as a clean cascade measurement unless those contributions have been
separated out (see AGENTS.md).

IMPORTANT -- time coordinates:

This script requires two explicit TimeCoordinate objects (time_1, time_2)
rather than bare frame indices, and only computes a physical rate
(delta_E_per_time) when both carry dt_confirmed=True with a recorded
source. Adjacent frame numbers in a local JHTDB HDF5 export are NOT assumed
to be unit-spaced in real time -- the export's t_start/t_end/t_step attrs
record what was passed to the cutout query, not a documented physical
Delta-t. When Delta-t cannot be established, this script still reports the
dimensionless per-frame delta_E(k) but clearly marks the rate as
unavailable in both the console output and the metadata file, rather than
silently guessing a time unit.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from jhtdb_terminal_benchmark import (
    Config,
    as_component_first,
    project_divergence_free,
    shell_spectrum,
    spectral_filter,
    wavenumbers,
)


class TemporalMetadataError(RuntimeError):
    """Raised when Delta-t between two snapshots cannot be established from
    authoritative dataset metadata."""


@dataclass(frozen=True)
class TimeCoordinate:
    """One requested/returned JHTDB time coordinate.

    requested_time: what was asked for.
    returned_time: what an authoritative source (a live JHTDB/Giverny query,
        or verified dataset documentation) confirms was actually used, if
        known.
    dt_confirmed: whether it is safe to treat a difference between two
        TimeCoordinates as a physical Delta-t. False for anything derived
        only from a local export's frame index.
    """

    requested_time: float
    frame_index: int | None
    returned_time: float | None
    interpolation_method: str
    dimensional: bool
    source: str
    dt_confirmed: bool = False


def local_h5_time_coordinate(path: str, frame_index: int) -> TimeCoordinate:
    """Build an *unconfirmed* TimeCoordinate from a local JHTDB HDF5 export.

    The export's attrs (t_start/t_end/t_step) record what was passed to the
    cutout query, not a documented physical Delta-t between frames. Do not
    assume adjacent frame numbers are unit-spaced in real time.
    """
    with h5py.File(path, "r") as f:
        attrs = {k: (v.item() if hasattr(v, "item") else v) for k, v in f.attrs.items()}
        if isinstance(attrs.get("dataset"), bytes):
            attrs["dataset"] = attrs["dataset"].decode()
    return TimeCoordinate(
        requested_time=float(frame_index),
        frame_index=frame_index,
        returned_time=None,
        interpolation_method="unknown (local export; not re-queried against a live JHTDB service)",
        dimensional=False,
        source=f"local_h5_attrs:{path}:{attrs}",
        dt_confirmed=False,
    )


def resolve_dt(t1: TimeCoordinate, t2: TimeCoordinate) -> float:
    if not (t1.dt_confirmed and t2.dt_confirmed):
        raise TemporalMetadataError(
            "Delta-t between these two snapshots has not been confirmed "
            "against authoritative JHTDB/Giverny metadata (dt_confirmed is "
            "False on at least one TimeCoordinate). Do not infer spacing "
            "from frame indices -- confirm the real physical time interval "
            "first (e.g. from a live Giverny query's returned time, or "
            "official dataset documentation), then construct "
            "TimeCoordinate objects with dt_confirmed=True and a recorded "
            "source."
        )
    if t1.returned_time is not None and t2.returned_time is not None:
        return t2.returned_time - t1.returned_time
    return t2.requested_time - t1.requested_time


def load_local_timestep(path: str, timestep: int) -> np.ndarray:
    with h5py.File(path, "r") as f:
        key = f"Velocity_{timestep:04d}"
        if key not in f:
            available = [k for k in f.keys() if k.startswith("Velocity_")]
            raise KeyError(f"{key} not found in {path}; available: {available}")
        return np.asarray(f[key])


def filtered_spectrum(velocity: np.ndarray, cfg: Config):
    u = as_component_first(velocity)
    nz, ny, nx = u.shape[1:]
    if not (nx == ny == nz):
        raise ValueError("This measurement requires a cubic cutout.")

    kx, ky, kz = wavenumbers(nx, cfg.domain_length)
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    uh = np.fft.fftn(u, axes=(1, 2, 3))
    uh = project_divergence_free(uh, kx, ky, kz)

    nyquist = float(np.max(np.abs(kx[:, 0, 0])))
    kc = cfg.cutoff_fraction * nyquist
    uh_ref = spectral_filter(uh, kmag, kc)
    shells, e = shell_spectrum(uh_ref, kmag)
    return shells, e, kc


def measure(
    velocity_1: np.ndarray,
    velocity_2: np.ndarray,
    t1: TimeCoordinate,
    t2: TimeCoordinate,
    cfg: Config,
    output_dir: str,
) -> pd.DataFrame:
    shells, e1, kc = filtered_spectrum(velocity_1, cfg)
    _, e2, kc2 = filtered_spectrum(velocity_2, cfg)
    assert kc == kc2

    dt: float | None
    dt_error: str | None
    try:
        dt = resolve_dt(t1, t2)
        dt_error = None
    except TemporalMetadataError as exc:
        dt = None
        dt_error = str(exc)

    df = pd.DataFrame(
        {
            "k": shells,
            "E_t1": e1,
            "E_t2": e2,
            "delta_E_per_frame": e2 - e1,
        }
    )
    if dt is not None:
        df["delta_E_per_time"] = df["delta_E_per_frame"] / dt

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    df.to_csv(output / "transfer_measurement.csv", index=False)

    metadata = {
        "dataset": cfg.dataset,
        "t1": asdict(t1),
        "t2": asdict(t2),
        "delta_t": dt,
        "delta_t_confirmed": dt is not None,
        "delta_t_error": dt_error,
        "kc": kc,
        "measurement_label": (
            "finite-difference energy-evolution measurement -- NOT an "
            "isolated nonlinear-cascade transfer; bundles resolved-resolved "
            "transfer, subfilter transfer, forcing, viscosity, and pressure "
            "effects over the interval"
        ),
    }
    (output / "transfer_measurement_metadata.json").write_text(json.dumps(metadata, indent=2))

    plt.figure(figsize=(8, 5))
    valid = shells > 0
    plt.axhline(0.0, color="black", linewidth=0.8)
    ycol = "delta_E_per_time" if dt is not None else "delta_E_per_frame"
    plt.plot(shells[valid], df[ycol][valid], marker="o")
    plt.axvline(kc, linestyle="--", color="gray", label="cutoff")
    plt.xlabel("Wavenumber")
    plt.ylabel("dE/dt(k)" if dt is not None else "delta_E(k)  [per frame -- dt unconfirmed]")
    plt.title("Filtered-energy finite-difference tendency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "transfer_measurement.png", dpi=180)
    plt.close()

    if dt_error is not None:
        print("TRANSFER-RATE UNAVAILABLE (dimensionless delta_E(k) only):")
        print(f"  {dt_error}")

    return df


def main() -> None:
    cfg = Config(cutoff_fraction=0.50)
    path = "isotropic1024coarse (1).h5"

    v1 = load_local_timestep(path, 1)
    v2 = load_local_timestep(path, 5)
    t1 = local_h5_time_coordinate(path, 1)
    t2 = local_h5_time_coordinate(path, 5)

    df = measure(v1, v2, t1, t2, cfg, output_dir="jhtdb_terminal_benchmark")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
