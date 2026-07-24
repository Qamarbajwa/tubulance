"""
Backscatter-placement comparison and identifiability (Milestone 5, Parts D-E)
=================================================================================

For a given DNS snapshot, runs nonlinear_transfer_validation.validate()
once per preregistered backscatter-placement strategy (see
backscatter_placement.py) and reports removal-only, full-transfer, and
flux agreement, plus shape/magnitude/sign/peak-location metrics, for each.

A placement must never be *selected* as "best" using the same snapshots
later reported as the validation result (Part D). `select_placement`
picks a winner using only a calibration snapshot set; `run_study`
reports full per-placement, per-snapshot metrics on validation snapshots
(and calibration snapshots, for transparency) without letting validation
outcomes influence the selection.

`identifiability_report` (Part E) asks whether the non-oracle placements
produce meaningfully different results at all, given how much a single
metric already varies snapshot-to-snapshot -- if placement-induced spread
is smaller than snapshot-to-snapshot spread, the placement rule cannot be
usefully discriminated by these metrics and the honest answer is
`backscatter_placement_not_identifiable`, not a false "winner."
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from backscatter_placement import DIAGNOSTIC_ONLY, PlacementConfigError, PlacementConservationError
from jhtdb_terminal_benchmark import Config, InsufficientResolutionError
from nonlinear_transfer_validation import validate

ALL_PLACEMENTS = (
    "local_cancellation",
    "parent_band_energy_weighted",
    "turnover_weighted",
    "dns_oracle_diagnostic",
)
DEPLOYABLE_PLACEMENTS = tuple(p for p in ALL_PLACEMENTS if p not in DIAGNOSTIC_ONLY)

# Metrics tracked for comparison and identifiability, pulled out of a
# validate() result dict.
#
# IMPORTANT: local_cancellation is the only strategy that changes T_model
# WITHIN the terminal region (it reduces to heat-only there); the other
# three all reinject strictly below ks, so they are IDENTICAL to each
# other -- and to plain T_remove -- when measured only inside
# terminal_region. A metric restricted to terminal_region therefore
# cannot discriminate parent_band/turnover/oracle from one another.
# inertial_transfer_* (T_dns vs T_model below ks, where the reinjected
# energy actually lands) and the flux metrics (which accumulate
# contributions from below ks upward via Pi(k) = -cumsum(T)) are the
# metrics that can actually tell these placements apart -- prefer them
# for selection, not terminal-region-only metrics.
_METRIC_GETTERS = {
    "removal_correlation": lambda r: r["removal_only_comparison"]["correlation"],
    "removal_relative_l2_error": lambda r: r["removal_only_comparison"]["relative_l2_error"],
    "removal_sign_agreement": lambda r: r["removal_only_comparison"]["sign_agreement_fraction"],
    "full_transfer_correlation": lambda r: r["regions"]["terminal_region"]["correlation"],
    "full_transfer_spearman": lambda r: r["regions"]["terminal_region"]["spearman_correlation"],
    "full_transfer_relative_l2_error": lambda r: r["regions"]["terminal_region"]["relative_l2_error"],
    "full_transfer_cosine_similarity": lambda r: r["regions"]["terminal_region"]["cosine_similarity"],
    "full_transfer_normalized_mae": lambda r: r["regions"]["terminal_region"]["normalized_mean_absolute_error"],
    "full_transfer_peak_shell_location_error": lambda r: r["regions"]["terminal_region"]["peak_shell_location_error"],
    "inertial_transfer_correlation": lambda r: r["regions"]["inertial_resolved_region"]["correlation"],
    "inertial_transfer_relative_l2_error": lambda r: r["regions"]["inertial_resolved_region"]["relative_l2_error"],
    "flux_correlation": lambda r: r["flux_comparison"]["correlation"],
    "flux_relative_l2_error": lambda r: r["flux_comparison"]["relative_l2_error"],
    "flux_plateau_error_below_ks": lambda r: r["flux_plateau_error_below_ks"],
    "terminal_processing_to_dns_flux_ratio": lambda r: r["terminal_processing_to_dns_flux_ratio"],
    "bottleneck_ratio": lambda r: r["bottleneck_ratio_relative_to_filtered_dns"],
    "model_transfer_conservation_residual": lambda r: abs(r["model_transfer_conservation"]["residual"]),
    "total_reinjection": lambda r: r["model_transfer_conservation"]["total_reinjection"],
    "total_removal": lambda r: abs(r["model_transfer_conservation"]["total_removal"]),
}

# Higher is better ("shape/agreement") vs lower is better ("error") --
# used only by select_placement()'s ranking, not by the identifiability
# report (which is symmetric in direction).
_HIGHER_IS_BETTER = {
    "removal_correlation": True,
    "full_transfer_correlation": True,
    "full_transfer_spearman": True,
    "full_transfer_cosine_similarity": True,
    "inertial_transfer_correlation": True,
    "inertial_transfer_relative_l2_error": False,
    "flux_correlation": True,
    "removal_relative_l2_error": False,
    "full_transfer_relative_l2_error": False,
    "flux_relative_l2_error": False,
    "flux_plateau_error_below_ks": False,
    "full_transfer_normalized_mae": False,
}


def _extract_metrics(result: dict) -> dict:
    row = {}
    for name, getter in _METRIC_GETTERS.items():
        try:
            row[name] = getter(result)
        except (KeyError, TypeError):
            row[name] = float("nan")
    return row


def compare_placements_on_snapshot(
    velocity: np.ndarray,
    cfg: Config,
    output_dir: str,
    *,
    c1: float | None = None,
    c2: float | None = None,
    placements: tuple[str, ...] = ALL_PLACEMENTS,
) -> dict:
    """Run every requested placement strategy on one DNS snapshot. Returns
    {"per_placement": {name: {"status": ..., "metrics": {...} or "reason": ...}}}.

    c1/c2 fall back to cfg.parent_band_c1/c2 when not passed explicitly --
    they only need to be given here to override cfg for this call.
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    c1 = cfg.parent_band_c1 if c1 is None else c1
    c2 = cfg.parent_band_c2 if c2 is None else c2

    per_placement: dict[str, dict] = {}
    for name in placements:
        placement_cfg = dataclasses.replace(
            cfg, backscatter_placement=name, parent_band_c1=c1, parent_band_c2=c2
        )
        try:
            result = validate(velocity, placement_cfg, output_dir=str(output / name))
            per_placement[name] = {
                "status": "ok",
                "diagnostic_only": name in DIAGNOSTIC_ONLY,
                "metrics": _extract_metrics(result),
            }
        except (PlacementConfigError, PlacementConservationError, InsufficientResolutionError) as exc:
            per_placement[name] = {
                "status": "blocked",
                "diagnostic_only": name in DIAGNOSTIC_ONLY,
                "reason": str(exc),
            }

    return {"per_placement": per_placement}


def select_placement(
    calibration_fetchers: list[Callable[[], np.ndarray]],
    cfg: Config,
    output_dir: str,
    *,
    c1: float | None = None,
    c2: float | None = None,
    selection_metric: str = "flux_relative_l2_error",
) -> dict:
    """Pick a winning DEPLOYABLE placement using ONLY calibration
    snapshots -- never the snapshots later reported as validation. The
    oracle is excluded from selection (it is diagnostic-only) but its
    calibration-set performance is still reported for context.

    Default metric is flux-based, not terminal-region-only: placements
    that reinject below ks are indistinguishable from each other and from
    plain T_remove when measured only inside the terminal region (see
    _METRIC_GETTERS docstring above) -- flux and inertial-region metrics
    are sensitive to where the reinjected energy actually lands.
    """
    higher_is_better = _HIGHER_IS_BETTER.get(selection_metric, True)

    per_snapshot_rows = []
    for i, fetch in enumerate(calibration_fetchers):
        comparison = compare_placements_on_snapshot(
            fetch(), cfg, f"{output_dir}/calibration_{i}", c1=c1, c2=c2
        )
        for name, entry in comparison["per_placement"].items():
            row = {"snapshot": i, "placement": name, "status": entry["status"]}
            if entry["status"] == "ok":
                row[selection_metric] = entry["metrics"].get(selection_metric, float("nan"))
            per_snapshot_rows.append(row)

    df = pd.DataFrame(per_snapshot_rows)
    means = (
        df[df["status"] == "ok"]
        .groupby("placement")[selection_metric]
        .mean()
        .dropna()
    )
    deployable_means = means[means.index.isin(DEPLOYABLE_PLACEMENTS)]

    selected = None
    if not deployable_means.empty:
        selected = (
            deployable_means.idxmax() if higher_is_better else deployable_means.idxmin()
        )

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    result = {
        "selection_metric": selection_metric,
        "higher_is_better": higher_is_better,
        "n_calibration_snapshots": len(calibration_fetchers),
        "calibration_means": means.to_dict(),
        "selected_placement": selected,
    }
    (output / "placement_selection.json").write_text(json.dumps(result, indent=2, default=str))
    return result


def run_validation_comparison(
    validation_fetchers: list[Callable[[], np.ndarray]],
    cfg: Config,
    output_dir: str,
    *,
    c1: float | None = None,
    c2: float | None = None,
) -> pd.DataFrame:
    """Report ALL placements' metrics on the validation snapshots (Part D:
    compare all four for every real snapshot). Does not select anything --
    selection must come only from select_placement() on a disjoint
    calibration set."""
    rows = []
    for i, fetch in enumerate(validation_fetchers):
        comparison = compare_placements_on_snapshot(
            fetch(), cfg, f"{output_dir}/validation_{i}", c1=c1, c2=c2
        )
        for name, entry in comparison["per_placement"].items():
            row = {"snapshot": i, "placement": name, "status": entry["status"]}
            if entry["status"] == "ok":
                row.update(entry["metrics"])
            rows.append(row)

    df = pd.DataFrame(rows)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    df.to_csv(output / "placement_validation_comparison.csv", index=False)
    return df


def identifiability_report(validation_df: pd.DataFrame) -> dict:
    """Part E: is backscatter placement identifiable at all from these
    metrics/snapshots? Compares, per metric, the spread INDUCED BY
    PLACEMENT (across placements, per snapshot, then averaged) against
    the spread INDUCED BY SNAPSHOT (across snapshots, for a fixed
    placement). If placement-induced spread is not larger, the metric
    cannot discriminate placement strategies given this much
    snapshot-to-snapshot variability.
    """
    ok = validation_df[validation_df["status"] == "ok"]
    metrics = [m for m in _METRIC_GETTERS if m in ok.columns]

    deployable = ok[ok["placement"].isin(DEPLOYABLE_PLACEMENTS)]
    oracle = ok[ok["placement"] == "dns_oracle_diagnostic"]

    per_metric = {}
    identifiable_count = 0
    evaluated_count = 0
    for metric in metrics:
        # Spread across placements, for each snapshot, then averaged.
        by_snapshot = deployable.groupby("snapshot")[metric]
        placement_spread = by_snapshot.std(ddof=0).mean()

        # Spread across snapshots, for each placement, then averaged.
        by_placement = deployable.groupby("placement")[metric]
        snapshot_spread = by_placement.std(ddof=0).mean()

        if pd.isna(placement_spread) or pd.isna(snapshot_spread):
            continue
        evaluated_count += 1
        ratio = placement_spread / snapshot_spread if snapshot_spread > 0 else float("inf")
        is_identifiable = ratio > 1.0
        identifiable_count += int(is_identifiable)

        local_mean = deployable[deployable["placement"] == "local_cancellation"][metric].mean()
        best_deployable_mean = (
            by_placement.mean().drop("local_cancellation", errors="ignore").agg(
                "max" if _HIGHER_IS_BETTER.get(metric, True) else "min"
            )
            if len(by_placement.mean().drop("local_cancellation", errors="ignore")) > 0
            else float("nan")
        )
        oracle_mean = oracle[metric].mean() if not oracle.empty else float("nan")

        per_metric[metric] = {
            "placement_induced_spread": float(placement_spread),
            "snapshot_induced_spread": float(snapshot_spread),
            "identifiability_ratio": float(ratio),
            "identifiable": bool(is_identifiable),
            "local_cancellation_mean": float(local_mean) if pd.notna(local_mean) else None,
            "best_deployable_alternative_mean": (
                float(best_deployable_mean) if pd.notna(best_deployable_mean) else None
            ),
            "oracle_mean": float(oracle_mean) if pd.notna(oracle_mean) else None,
        }

    overall_identifiable = evaluated_count > 0 and identifiable_count > evaluated_count / 2.0

    return {
        "n_metrics_evaluated": evaluated_count,
        "n_metrics_identifiable": identifiable_count,
        "per_metric": per_metric,
        "overall_classification": (
            "backscatter_placement_identifiable"
            if overall_identifiable
            else "backscatter_placement_not_identifiable"
        ),
        "interpretation": (
            "Majority of tracked metrics show placement-induced spread exceeding "
            "snapshot-to-snapshot spread -- placement choice appears to matter more "
            "than which snapshot was used."
            if overall_identifiable
            else "Placement-induced spread does not exceed snapshot-to-snapshot spread "
            "for a majority of tracked metrics -- do not overinterpret small score "
            "differences between placement strategies as a physical discovery."
        ),
    }
