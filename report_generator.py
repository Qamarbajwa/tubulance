"""
First real-data report (Milestone 5, Part F)
================================================

Assembles the outputs of snapshot_ensemble.py, convergence_table.py, and
placement_comparison.py into one machine-readable JSON report and one
human-readable Markdown report. Does not run anything itself -- pass in
the already-computed result dicts/DataFrames from those modules.

The strongest permitted successful statement is fixed here, not
reworded per-run:

    "Real-DNS a-priori results show instantaneous consistency under the
    tested filtering, cutoff, and placement assumptions."

Never predictive validity, never universality, never "proof". See
`SUPPORTED_STATEMENTS` / `NOT_SUPPORTED_STATEMENTS` for the exact
boundary, and `UNRESOLVED_THEORY_GAPS` for what's still open as of
2026-07-24.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

STRONGEST_PERMITTED_STATEMENT = (
    "Real-DNS a-priori results show instantaneous consistency under the "
    "tested filtering, cutoff, and placement assumptions."
)

SUPPORTED_STATEMENTS = [
    "The nonlinear-transfer and spectral-flux mathematics are correct and "
    "globally conservative to numerical tolerance (see nonlinear_transfer.py "
    "analytic tests).",
    "The terminal operator's heat/return accounting is internally consistent "
    "and conserves total energy exactly under every implemented backscatter "
    "placement strategy (see model_transfer_conservation residuals).",
    "Run provenance, resolution requirements, and classification are enforced "
    "automatically; a run cannot silently report physics metrics from "
    "inadequate resolution or an unconfirmed time interval.",
    STRONGEST_PERMITTED_STATEMENT + " (only applies when data_is_real=True for "
    "this report -- see the data-provenance warning above if not)",
]

NOT_SUPPORTED_STATEMENTS = [
    "Predictive accuracy: no forward-in-time integration has been run "
    "(Milestone 6, not yet implemented).",
    "Universality across Reynolds numbers or flow types: only "
    "isotropic1024coarse has been considered at all, and only at 16^3 "
    "resolution as of 2026-07-24 (see UNRESOLVED_THEORY_GAPS).",
    "The physical correctness of any backscatter-placement rule: "
    "'local_cancellation' is an algebraic control case, not a claim about "
    "where energy actually returns to the spectrum; the other rules are "
    "preregistered hypotheses, not confirmed mechanisms.",
    "That a placement strategy 'wins': see the identifiability report -- "
    "a small score difference between placements is not evidence of a "
    "physical mechanism unless it exceeds snapshot-to-snapshot variability.",
]

UNRESOLVED_THEORY_GAPS = [
    "Real spatial resolution: only a 16^3 JHTDB cutout is cached locally as "
    "of 2026-07-24; 128^3+ via SciServer/Giverny has not been executed.",
    "Confirmed temporal separation: no confirmed Delta-t for "
    "isotropic1024coarse frames exists in this project.",
    "Backscatter-placement identifiability: whether any placement strategy "
    "is even distinguishable from local_cancellation given real-DNS "
    "snapshot-to-snapshot variability is unresolved pending real data.",
    "Forward-in-time validation: not implemented (Milestone 6 interface "
    "only, see forward_validation_interface.py).",
]


def _safe(obj):
    """json.dumps default= hook for numpy/pandas leftovers."""
    if hasattr(obj, "item"):
        return obj.item()
    return str(obj)


def generate_reports(
    output_dir: str,
    *,
    data_is_real: bool = False,
    ensemble_result: dict | None = None,
    convergence_df: pd.DataFrame | None = None,
    placement_selection: dict | None = None,
    placement_validation_df: pd.DataFrame | None = None,
    identifiability: dict | None = None,
    plot_paths: list[str] | None = None,
) -> tuple[Path, Path]:
    """`data_is_real` must be asserted explicitly by the caller -- it is
    NOT inferred from whether snapshots ran "ok", because a fully
    synthetic run (random-noise test data) can produce a structurally
    valid-looking ensemble result. Defaults to False so a report is
    conservative unless someone deliberately marks it as real JHTDB data.
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    report = {
        "strongest_permitted_statement": STRONGEST_PERMITTED_STATEMENT,
        "data_is_real": data_is_real,
        "data_provenance_warning": (
            None
            if data_is_real
            else (
                "SYNTHETIC/TEST DATA -- this report does NOT represent real JHTDB "
                "validation. Every number below was produced from synthetic velocity "
                "fields for code-correctness testing only. Do not cite this report as "
                "evidence about the terminal-layer theory."
            )
        ),
        "structural_validation": (
            ensemble_result.get("dataset_level_classification") if ensemble_result else None
        ),
        "ensemble_statistics": ensemble_result.get("aggregate") if ensemble_result else None,
        "resolution_convergence": (
            convergence_df.to_dict(orient="records") if convergence_df is not None else None
        ),
        "placement_selection": placement_selection,
        "placement_validation_comparison": (
            placement_validation_df.to_dict(orient="records") if placement_validation_df is not None else None
        ),
        "identifiability": identifiability,
        "classification_outcome": (
            ensemble_result.get("dataset_level_classification", {}).get("label")
            if ensemble_result
            else "no ensemble run supplied"
        ),
        "unresolved_theory_gaps": UNRESOLVED_THEORY_GAPS,
        "statements_supported": SUPPORTED_STATEMENTS,
        "statements_not_supported": NOT_SUPPORTED_STATEMENTS,
        "plot_paths": plot_paths or [],
    }

    json_path = output / "milestone5_report.json"
    json_path.write_text(json.dumps(report, indent=2, default=_safe))

    markdown_path = output / "milestone5_report.md"
    markdown_path.write_text(_render_markdown(report))

    return json_path, markdown_path


def _render_markdown(report: dict) -> str:
    lines = []
    lines.append("# Milestone 5 real-data report")
    lines.append("")
    if report["data_provenance_warning"]:
        lines.append(f"> **WARNING:** {report['data_provenance_warning']}")
        lines.append("")
    lines.append(f"**Data is real JHTDB data:** {report['data_is_real']}")
    lines.append("")
    lines.append("## Strongest permitted statement")
    lines.append("")
    lines.append(f"> {report['strongest_permitted_statement']}")
    lines.append("")

    lines.append("## What is supported")
    for s in report["statements_supported"]:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## What is NOT supported")
    for s in report["statements_not_supported"]:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## Unresolved theory gaps")
    for g in report["unresolved_theory_gaps"]:
        lines.append(f"- {g}")
    lines.append("")

    lines.append("## Structural validation (dataset-level classification)")
    sv = report["structural_validation"]
    if sv:
        lines.append(f"- Label: **{sv.get('label')}**")
        lines.append(f"- Snapshots: {sv.get('n_snapshots_ok')} ok / {sv.get('n_snapshots_total')} total")
        for check, passed in sv.get("checks", {}).items():
            lines.append(f"  - `{check}`: {'PASS' if passed else 'FAIL'}")
    else:
        lines.append("- No ensemble run supplied.")
    lines.append("")

    lines.append("## Resolution convergence")
    conv = report["resolution_convergence"]
    if conv:
        lines.append("| grid_n | status | spectrum_error | transfer_error | flux_error | bottleneck_ratio |")
        lines.append("|---|---|---|---|---|---|")
        for row in conv:
            lines.append(
                f"| {row.get('grid_n')} | {row.get('status')} | {row.get('spectrum_error', '')} | "
                f"{row.get('transfer_error', '')} | {row.get('flux_error', '')} | {row.get('bottleneck_ratio', '')} |"
            )
    else:
        lines.append("- No convergence table supplied.")
    lines.append("")

    lines.append("## Backscatter-placement selection and identifiability")
    sel = report["placement_selection"]
    if sel:
        lines.append(f"- Selection metric: `{sel.get('selection_metric')}`")
        lines.append(f"- Selected placement (calibration set only): **{sel.get('selected_placement')}**")
    ident = report["identifiability"]
    if ident:
        lines.append(f"- Overall: **{ident.get('overall_classification')}**")
        lines.append(f"- {ident.get('interpretation')}")
    lines.append("")

    lines.append("## Classification outcome")
    lines.append(f"**{report['classification_outcome']}**")
    lines.append("")

    if report["plot_paths"]:
        lines.append("## Plots")
        for p in report["plot_paths"]:
            lines.append(f"- {p}")
        lines.append("")

    return "\n".join(lines)
