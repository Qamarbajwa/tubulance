"""
Resolution-convergence scaffold
==================================

Infrastructure for running the same benchmark at multiple grid sizes
(64^3 diagnostic-only, 128^3 minimum physical test, 256^3 preferred, and
above) and producing a convergence table: grid size, kc, ks, effective
beta, terminal shell count, populated terminal shell count, spectrum
error, transfer error, flux error, bottleneck ratio, runtime, and peak
memory use.

As of 2026-07-24 this project only has a real 16^3 JHTDB cutout cached
locally (see README.md "Open validation blockers" #1) -- far below even
the 64^3 diagnostic tier. Rather than fabricate data for the missing
resolutions (see AGENTS.md), each resolution here takes an explicit
`fetch` callable; when none is supplied the row is reported with
status="no_data" instead of being silently omitted or filled in with a
guess. Wire in a real `fetch` (a SciServer/Giverny call, or a path to a
larger cached HDF5 export) per resolution as real data becomes available.
"""

from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from jhtdb_terminal_benchmark import Config, compute_terminal_layer, validate_terminal_layer
from nonlinear_transfer_validation import validate as validate_nonlinear_transfer
from spectral_fields import dns_and_filtered_shells

# The tiers requested for this milestone. 64^3 is diagnostic-only (below
# the resolution needed for a trustworthy physical result), 128^3 is the
# minimum physical test, 256^3 is preferred.
DEFAULT_TIERS = (64, 128, 256)


@dataclass(frozen=True)
class ResolutionSpec:
    grid_n: int
    fetch: Callable[[], np.ndarray] | None = None
    label: str = ""


def run_at_resolution(spec: ResolutionSpec, cfg: Config) -> dict:
    if spec.fetch is None:
        return {
            "grid_n": spec.grid_n,
            "label": spec.label,
            "status": "no_data",
            "note": "No fetch function supplied for this resolution -- not fabricated.",
        }

    tracemalloc.start()
    t0 = time.perf_counter()
    row: dict = {"grid_n": spec.grid_n, "label": spec.label}
    try:
        velocity = spec.fetch()
        _, _, _, _, _, kmag, shells, e_dns, e_ref, kc, nyquist = dns_and_filtered_shells(velocity, cfg)
        delta_k = 2.0 * np.pi / cfg.domain_length
        layer = compute_terminal_layer(kc, delta_k, cfg)
        failures = validate_terminal_layer(layer, nyquist, shells, e_dns, cfg)
        terminal_region = (shells >= layer.ks) & (shells <= kc)
        populated_terminal = int(np.sum(e_dns[terminal_region] > cfg.energy_floor))

        row.update(
            {
                "kc": kc,
                "ks": layer.ks,
                "beta_effective": layer.beta_effective,
                "terminal_shell_count": layer.n_t,
                "populated_terminal_shells": populated_terminal,
                "status": "blocked" if failures else "ok",
                "failures": "; ".join(failures) if failures else "",
            }
        )

        if not failures:
            nt_result = validate_nonlinear_transfer(
                velocity, cfg, output_dir=f"jhtdb_terminal_benchmark/convergence_n{spec.grid_n}"
            )
            row.update(
                {
                    "spectrum_error": nt_result["spectrum_relative_l2_terminal_region"],
                    "transfer_error": nt_result["regions"]["terminal_region"]["relative_l2_error"],
                    "flux_error": nt_result["flux_relative_l2_error"],
                    "bottleneck_ratio": nt_result["bottleneck_ratio_relative_to_filtered_dns"],
                    "classification": nt_result["classification"],
                }
            )
    finally:
        elapsed = time.perf_counter() - t0
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    row["runtime_seconds"] = elapsed
    row["peak_memory_mb"] = peak / (1024 * 1024)
    return row


def run_convergence_table(specs: list[ResolutionSpec], cfg: Config, output_dir: str) -> pd.DataFrame:
    rows = [run_at_resolution(spec, cfg) for spec in specs]
    df = pd.DataFrame(rows)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    df.to_csv(output / "convergence_table.csv", index=False)
    if (df.get("status") == "ok").any():
        _plot_convergence(df, output / "convergence_vs_resolution.png")
    return df


def _plot_convergence(df: pd.DataFrame, path: Path) -> None:
    ok = df[df["status"] == "ok"].sort_values("grid_n")
    if ok.empty:
        return

    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    panels = [
        ("spectrum_error", "Spectrum relative L2 error"),
        ("transfer_error", "Transfer relative L2 error"),
        ("flux_error", "Flux relative L2 error"),
        ("bottleneck_ratio", "Bottleneck ratio"),
    ]
    for ax, (col, title) in zip(axes.flat, panels):
        if col in ok:
            ax.plot(ok["grid_n"], ok[col], marker="o")
        if col == "bottleneck_ratio":
            ax.axhline(1.0, color="gray", linestyle="--")
        ax.set_xlabel("Grid size (n^3)")
        ax.set_title(title)

    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    """As of 2026-07-24 only the local 16^3 cutout is real data; every
    other tier reports no_data rather than a fabricated row. Wire in real
    fetch callables (SciServer/Giverny, or larger cached HDF5 exports) as
    they become available -- see README.md "Open validation blockers".
    """
    from measure_transfer import load_local_timestep

    cfg = Config(cutoff_fraction=0.50)
    specs = [
        ResolutionSpec(16, fetch=lambda: load_local_timestep("isotropic1024coarse.h5", 1), label="local cache"),
        ResolutionSpec(64, fetch=None, label="diagnostic tier -- no real data yet"),
        ResolutionSpec(128, fetch=None, label="minimum physical test -- no real data yet"),
        ResolutionSpec(256, fetch=None, label="preferred -- no real data yet"),
    ]
    df = run_convergence_table(specs, cfg, output_dir="jhtdb_terminal_benchmark")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
