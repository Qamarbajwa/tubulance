"""
Multi-snapshot ensemble validation
=====================================

Milestone 4 item 5/6: the model must not be judged from one favorable
snapshot. Runs nonlinear_transfer_validation.validate() across multiple
independent snapshots, reports per-snapshot metrics plus mean/std/median/
worst-case, and applies the dataset-level "a-priori consistency" rule from
README.md item 6 -- which is a strict AND of quantified structural checks,
NOT a single correlation threshold (no such universal threshold is defined
here; per the 2026-07-24 instruction, thresholds should be set only after
seeing the real-data distribution, so `dataset_level_classification()`
reports the bottleneck-ratio distribution rather than auto-pass/failing
it).

As of 2026-07-24 there is no real independent multi-snapshot 128^3+ JHTDB
data available in this project (see README.md "Open validation
blockers"). This module is infrastructure, ready to run once such data
exists; tests exercise it with synthetic snapshots for code correctness
only, never as evidence about the terminal-layer theory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from jhtdb_terminal_benchmark import Config, InsufficientResolutionError
from nonlinear_transfer_validation import validate

# name -> (getter, comparison spec). "higher_is_better": True/False picks the
# worst-case direction; "target" picks the value furthest from an ideal
# (e.g. a ratio of 1.0).
_METRIC_SPECS: dict[str, dict] = {
    "terminal_region_correlation": {
        "getter": lambda r: r["regions"]["terminal_region"]["correlation"],
        "higher_is_better": True,
    },
    "terminal_region_spearman": {
        "getter": lambda r: r["regions"]["terminal_region"]["spearman_correlation"],
        "higher_is_better": True,
    },
    "spectrum_relative_l2_terminal_region": {
        "getter": lambda r: r["spectrum_relative_l2_terminal_region"],
        "higher_is_better": False,
    },
    "flux_relative_l2_error": {
        "getter": lambda r: r["flux_relative_l2_error"],
        "higher_is_better": False,
    },
    "bottleneck_ratio": {
        "getter": lambda r: r["bottleneck_ratio_relative_to_filtered_dns"],
        "target": 1.0,
    },
    "terminal_processing_to_dns_flux_ratio": {
        "getter": lambda r: r["terminal_processing_to_dns_flux_ratio"],
        "target": 1.0,
    },
    "global_conservation_residual": {
        "getter": lambda r: r["global_nonlinear_conservation"]["relative_residual"],
        "higher_is_better": False,
    },
    "model_transfer_conservation_residual": {
        "getter": lambda r: abs(r["model_transfer_conservation"]["residual"]),
        "higher_is_better": False,
    },
}


def _worst_case(values: np.ndarray, spec: dict) -> float:
    if "target" in spec:
        idx = int(np.argmax(np.abs(values - spec["target"])))
    elif spec["higher_is_better"]:
        idx = int(np.argmin(values))
    else:
        idx = int(np.argmax(values))
    return float(values[idx])


def run_ensemble(
    fetchers: list[Callable[[], np.ndarray]],
    cfg: Config,
    output_dir: str,
    *,
    labels: list[str] | None = None,
    min_snapshots: int = 5,
) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    labels = labels or [f"snapshot_{i}" for i in range(len(fetchers))]

    per_snapshot: list[dict] = []
    for label, fetch in zip(labels, fetchers):
        try:
            result = validate(fetch(), cfg, output_dir=str(output / label))
            result = dict(result, _label=label, _status="ok")
        except InsufficientResolutionError as exc:
            result = {"_label": label, "_status": "blocked", "_reason": str(exc)}
        per_snapshot.append(result)

    ok_results = [r for r in per_snapshot if r["_status"] == "ok"]

    rows = []
    for r in ok_results:
        row = {"label": r["_label"], "n_t": r.get("n_t"), "grid_n": r.get("grid_n")}
        for name, spec in _METRIC_SPECS.items():
            try:
                row[name] = spec["getter"](r)
            except (KeyError, TypeError):
                row[name] = float("nan")
        rows.append(row)
    per_snapshot_df = pd.DataFrame(rows)
    per_snapshot_df.to_csv(output / "ensemble_per_snapshot.csv", index=False)

    aggregate = {}
    for name, spec in _METRIC_SPECS.items():
        if name not in per_snapshot_df:
            continue
        values = per_snapshot_df[name].dropna().to_numpy()
        if values.size == 0:
            continue
        aggregate[name] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "median": float(np.median(values)),
            "worst_case": _worst_case(values, spec),
            "n": int(values.size),
        }

    classification = dataset_level_classification(per_snapshot, cfg, min_snapshots=min_snapshots)

    result = {
        "n_snapshots_requested": len(fetchers),
        "labels": labels,
        "per_snapshot_status": {r["_label"]: r["_status"] for r in per_snapshot},
        "aggregate": aggregate,
        "dataset_level_classification": classification,
    }
    (output / "ensemble_summary.json").write_text(json.dumps(result, indent=2, default=str))

    if not per_snapshot_df.empty:
        _plot_ensemble_summary(per_snapshot_df, output / "ensemble_summary.png")

    return result


def dataset_level_classification(
    per_snapshot: list[dict],
    cfg: Config,
    *,
    min_snapshots: int = 5,
    conservation_tolerance: float = 1e-6,
) -> dict:
    """The item-6 "positive-result rule": a dataset may be described as
    showing a-priori consistency only when ALL of the quantified criteria
    below hold. `no_severe_bottleneck` is deliberately left undetermined --
    no numerical severity threshold has been set from a real-data
    distribution yet, so this reports the distribution instead of guessing
    a cutoff (see module docstring).
    """
    ok_results = [r for r in per_snapshot if r.get("_status") == "ok"]
    structural_pass = [r for r in ok_results if r.get("classification") not in ("pipeline_only", "blocked")]
    n_structural = len(structural_pass)

    def _all(predicate) -> bool:
        return n_structural > 0 and all(predicate(r) for r in structural_pass)

    checks = {
        "at_least_five_snapshots_pass_structural_checks": n_structural >= min_snapshots,
        "nonlinear_conservation_within_tolerance": _all(
            lambda r: r["global_nonlinear_conservation"]["relative_residual"] <= conservation_tolerance
        ),
        "model_transfer_conservation_within_tolerance": _all(
            lambda r: abs(r["model_transfer_conservation"]["residual"]) <= conservation_tolerance
        ),
        "no_energy_above_cutoff": _all(
            lambda r: r["energy_above_cutoff_filtered"] == 0.0 and r["energy_above_cutoff_terminal"] == 0.0
        ),
        "terminal_shell_count_at_least_six": _all(lambda r: r["n_t"] >= cfg.min_terminal_shells),
        "populated_terminal_shells_at_least_four": _all(
            lambda r: r["populated_terminal_shells"] >= cfg.min_populated_terminal_shells
        ),
        "transfer_agreement_positive_in_majority_of_snapshots": (
            n_structural > 0
            and float(
                np.mean([r["regions"]["terminal_region"]["correlation"] > 0 for r in structural_pass])
            )
            > 0.5
        ),
    }

    bottleneck_ratios = [
        r["bottleneck_ratio_relative_to_filtered_dns"] for r in structural_pass if np.isfinite(r["bottleneck_ratio_relative_to_filtered_dns"])
    ]

    all_quantified_pass = all(checks.values())

    return {
        "n_snapshots_total": len(per_snapshot),
        "n_snapshots_ok": len(ok_results),
        "n_snapshots_structural_pass": n_structural,
        "checks": checks,
        "bottleneck_ratio_distribution": bottleneck_ratios,
        "no_severe_bottleneck_determination": (
            "not auto-determined -- no numerical bottleneck-severity threshold has been "
            "set from a real-data distribution yet; review bottleneck_ratio_distribution "
            "manually before making this call"
        ),
        "dataset_shows_a_priori_consistency": all_quantified_pass,
        "label": (
            "a-priori consistency (NOT full validation -- see run_classification.py)"
            if all_quantified_pass
            else "criteria not met -- see `checks` for which ones failed"
        ),
    }


def _plot_ensemble_summary(df: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    ax = axes[0, 0]
    metric_cols = ["terminal_region_correlation", "spectrum_relative_l2_terminal_region", "flux_relative_l2_error"]
    available = [c for c in metric_cols if c in df]
    if available:
        ax.boxplot([df[c].dropna() for c in available], tick_labels=available)
        ax.tick_params(axis="x", rotation=30)
    ax.set_title("Metric distributions across snapshots")

    ax = axes[0, 1]
    if "n_t" in df and "bottleneck_ratio" in df:
        ax.scatter(df["n_t"], df["bottleneck_ratio"])
        ax.axhline(1.0, color="gray", linestyle="--")
    ax.set_xlabel("Terminal shell count N_T")
    ax.set_ylabel("Bottleneck ratio")
    ax.set_title("Bottleneck ratio vs. terminal shell count")

    ax = axes[1, 0]
    if "terminal_region_correlation" in df:
        ax.plot(range(len(df)), df["terminal_region_correlation"], marker="o")
        ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel("Snapshot index")
    ax.set_ylabel("Terminal-region correlation")
    ax.set_title("Metric variation across snapshots")

    ax = axes[1, 1]
    if "flux_relative_l2_error" in df:
        ax.plot(range(len(df)), df["flux_relative_l2_error"], marker="o", color="tab:red")
    ax.set_xlabel("Snapshot index")
    ax.set_ylabel("Flux relative L2 error")
    ax.set_title("Flux error across snapshots")

    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close(fig)
