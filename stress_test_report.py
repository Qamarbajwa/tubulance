"""
Milestone 5.7 report generator
===================================

Assembles a completed stress-test campaign (a list of
milestone_5_7_stress_test.StressTestRunResult) into one JSON and one
Markdown report, following the same discipline as report_generator.py
(Milestone 5): a fixed strongest-permitted-statement, explicit supported/
not-supported lists, and a mandatory data-provenance warning.

Every Milestone 5.7 run is synthetic by construction (pseudo_spectral_
solver.py has no real-data code path at all -- there is no `data_is_real`
flag to set here because it can never be True for this module). This
report always carries the synthetic-only warning; it is not optional and
not caller-configurable, unlike Milestone 5's `data_is_real`.
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

from milestone_5_7_stress_test import (
    StressTestRunResult, applicability_map, applicability_map_from_rows, GROUP_DESCRIPTIONS,
)

SYNTHETIC_ONLY_WARNING = (
    "SYNTHETIC-ONLY REPORT -- every number below comes from the Milestone 5.7 "
    "synthetic pseudo-spectral stress-test solver (pseudo_spectral_solver.py), "
    "not from real JHTDB DNS data. This report tests the terminal-layer "
    "model's numerical and structural behavior under controlled forcing, "
    "material, and size variation. It is evidence about the MODEL'S CODE "
    "AND ASSUMPTIONS, not about real turbulence. It must never be cited "
    "alongside or in place of the real JHTDB validation campaign "
    "(jhtdb_terminal_benchmark.py / run_real_validation.py)."
)

STRONGEST_PERMITTED_STATEMENT = (
    "Under the tested synthetic forcing/material/size domain, the original "
    "terminal-layer operator's applicability boundary can be mapped: it behaves "
    "consistently with its own weak-forcing limit where Phi_l << 1 and forcing "
    "is well-separated from k_s, and its assumptions are directly challenged "
    "where forcing overlaps or exceeds k_s."
)

SUPPORTED_STATEMENTS = [
    "The forcing/material/size schema (forcing.py, material_state.py, "
    "terminal_operator_forcing_aware.py) is implemented and exercised across "
    "all 14 preregistered forcing cases without silently approximating an "
    "unimplemented material or fabricating a missing resolution tier.",
    "The first forward-in-time integrator in this repo (pseudo_spectral_"
    "solver.py) runs, conserves energy to the tolerance reported per run "
    "(unresolved_residual), and its energy-channel attribution "
    "(viscous/heat/return split) is exact by construction for the linear "
    "part of the timestep -- see module docstring.",
    "The energy-budget PI controller (controller.py) using the previously-"
    "dormant Config.gp=24/gi=8 defaults is now an actual tested control "
    "loop, with overshoot/settling-time/oscillation diagnostics reported "
    "per run rather than assumed stable.",
    "Every run is classified with an explicit (forcing case, material, "
    "grid_n) domain attached -- no run contributes to a bare supported/"
    "not-supported claim without that domain (stress_test_classification.py).",
]

NOT_SUPPORTED_STATEMENTS = [
    "Any claim about real turbulence: this entire milestone is synthetic-only "
    "(see the warning above); it cannot substitute for, and was not run "
    "against, real JHTDB data.",
    "The forcing-aware candidate model (comparison group C, "
    "terminal_operator_forcing_aware.gamma_candidate_forcing_aware): it is an "
    "explicitly preregistered, UNVALIDATED candidate functional form, not a "
    "confirmed improvement over the baseline operator -- see CANDIDATE_KAPPA "
    "and IS_CANDIDATE_MODEL in that module.",
    "Universality of the controller gains: GP=24/GI=8 was tested as a "
    "baseline hypothesis (H7), not confirmed as an optimal or universal "
    "choice -- see the group-B retuned-gains comparison for how much a "
    "calibration-only retune changes stability/overshoot.",
    "128^3 resolution results: not executed in this environment (compute-"
    "limited); any 128^3 row in this report is status='no_data', never a "
    "fabricated result.",
    "32^3 resolution results as physical evidence: this tier is diagnostic-"
    "only in this milestone's own solver (the beta-derived terminal layer "
    "degenerates to ks=0 at this resolution, see milestone_5_7_stress_test.py "
    "module docstring) -- consistent with the specification's explicit "
    "instruction not to treat 32^3 as physical.",
]

UNRESOLVED_QUESTIONS = [
    "Whether the candidate forcing-aware gamma correction (group C) actually "
    "improves agreement with anything -- there is no real-data ground truth "
    "in this milestone to compare it against; it is only compared to the "
    "unmodified baseline operator on synthetic data.",
    "Whether the return-placement kick's shell-random-phase reinjection "
    "scheme materially changes structure statistics relative to a different "
    "reinjection scheme -- only backscatter_placement.py's four preregistered "
    "strategies were exercised, at the shell level, not compared against a "
    "modal-level alternative.",
    "How the applicability map changes at 128^3 and beyond -- not executed "
    "here; compute-limited.",
    "Whether the forcing-amplitude safety clip (pseudo_spectral_solver."
    "make_forcing_hat's lam_max bound) biases the pulsed/impulsive/rotating "
    "cases' effective injected power away from their nominal target during "
    "the most transient phases -- reported per-run as power_input in the "
    "energy budget, but not separately audited against the clip's activation "
    "rate in this pass.",
]


def _safe(obj):
    if hasattr(obj, "item"):
        return obj.item()
    return str(obj)


def _result_to_dict(r: StressTestRunResult) -> dict:
    return {
        "case_name": r.case_name,
        "forcing_type": r.forcing_type,
        "split": r.split,
        "material": r.material_name,
        "grid_n": r.grid_n,
        "group": r.group,
        "phi_l": r.phi_l,
        "phi_l_regime": r.domain.phi_l_regime,
        "theta_f": r.theta_f,
        "theta_f_regime": r.domain.theta_f_regime,
        "k_f_over_ks": r.k_f_over_ks,
        "k_f_vs_ks": r.domain.k_f_vs_ks,
        "l_over_L": r.l_over_L,
        "l_over_lc": r.l_over_lc,
        "reynolds_number": r.reynolds_number,
        "pipeline_ok": r.pipeline_ok,
        "resolution_ok": r.resolution_ok,
        "populated_terminal_shells": r.populated_terminal_shells,
        "energy_budget": r.energy_budget,
        "controller": r.controller,
        "classification_labels": list(r.classification.labels),
        "classification_notes": list(r.classification.notes),
    }


def generate_stress_test_reports(
    output_dir: str, results: list[StressTestRunResult], *, grid_tiers_requested: list[int], grid_tiers_executed: list[int],
) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    skipped_tiers = sorted(set(grid_tiers_requested) - set(grid_tiers_executed))
    label_counts = Counter(l for r in results for l in r.classification.labels)
    group_counts = Counter(r.group for r in results)

    report = {
        "milestone": "5.7",
        "title": "Forcing-Material-Size Stress Test of the Terminal-Layer Model",
        "synthetic_only_warning": SYNTHETIC_ONLY_WARNING,
        "strongest_permitted_statement": STRONGEST_PERMITTED_STATEMENT,
        "statements_supported": SUPPORTED_STATEMENTS,
        "statements_not_supported": NOT_SUPPORTED_STATEMENTS,
        "unresolved_questions": UNRESOLVED_QUESTIONS,
        "comparison_groups": GROUP_DESCRIPTIONS,
        "grid_tiers_requested": grid_tiers_requested,
        "grid_tiers_executed": grid_tiers_executed,
        "grid_tiers_skipped_no_data": [
            {"grid_n": t, "status": "no_data", "reason": "compute-limited in this environment, not fabricated"} for t in skipped_tiers
        ],
        "n_runs": len(results),
        "runs_per_group": dict(group_counts),
        "classification_label_counts": dict(label_counts),
        "applicability_map": applicability_map(results),
        "runs": [_result_to_dict(r) for r in results],
    }

    json_path = output / "milestone5_7_report.json"
    json_path.write_text(json.dumps(report, indent=2, default=_safe))

    markdown_path = output / "milestone5_7_report.md"
    markdown_path.write_text(_render_markdown(report))

    return json_path, markdown_path


def generate_stress_test_reports_from_rows(
    output_dir: str, rows: list[dict], *, grid_tiers_requested: list[int], grid_tiers_executed: list[int],
    n_runs_expected: int | None = None, shards_used: list[str] | None = None,
) -> tuple[Path, Path]:
    """Same output as generate_stress_test_reports(), but assembled from
    plain dict rows (as produced by _result_to_dict() and accumulated
    across run_milestone_5_7_chunk.py shards) instead of in-memory
    StressTestRunResult objects -- used by
    assemble_milestone_5_7_report.py to finalize a chunked campaign."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    skipped_tiers = sorted(set(grid_tiers_requested) - set(grid_tiers_executed))
    label_counts = Counter(l for r in rows for l in r["classification_labels"])
    group_counts = Counter(r["group"] for r in rows)

    report = {
        "milestone": "5.7",
        "title": "Forcing-Material-Size Stress Test of the Terminal-Layer Model",
        "synthetic_only_warning": SYNTHETIC_ONLY_WARNING,
        "strongest_permitted_statement": STRONGEST_PERMITTED_STATEMENT,
        "statements_supported": SUPPORTED_STATEMENTS,
        "statements_not_supported": NOT_SUPPORTED_STATEMENTS,
        "unresolved_questions": UNRESOLVED_QUESTIONS,
        "comparison_groups": GROUP_DESCRIPTIONS,
        "grid_tiers_requested": grid_tiers_requested,
        "grid_tiers_executed": grid_tiers_executed,
        "grid_tiers_skipped_no_data": [
            {"grid_n": t, "status": "no_data", "reason": "compute-limited in this environment, not fabricated"} for t in skipped_tiers
        ],
        "shards_used": shards_used or [],
        "n_runs": len(rows),
        "n_runs_expected": n_runs_expected,
        "runs_per_group": dict(group_counts),
        "classification_label_counts": dict(label_counts),
        "applicability_map": applicability_map_from_rows(rows),
        "runs": rows,
    }

    json_path = output / "milestone5_7_report.json"
    json_path.write_text(json.dumps(report, indent=2, default=_safe))

    markdown_path = output / "milestone5_7_report.md"
    markdown_path.write_text(_render_markdown(report))

    return json_path, markdown_path


def _render_markdown(report: dict) -> str:
    lines = []
    lines.append("# Milestone 5.7 report: Forcing-Material-Size Stress Test")
    lines.append("")
    lines.append(f"> **WARNING:** {report['synthetic_only_warning']}")
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

    lines.append("## Unresolved questions")
    for q in report["unresolved_questions"]:
        lines.append(f"- {q}")
    lines.append("")

    lines.append("## Comparison groups")
    for g, desc in report["comparison_groups"].items():
        lines.append(f"- **{g}**: {desc}")
    lines.append("")

    lines.append("## Resolution tiers")
    lines.append(f"- Requested: {report['grid_tiers_requested']}")
    lines.append(f"- Executed: {report['grid_tiers_executed']}")
    for row in report["grid_tiers_skipped_no_data"]:
        lines.append(f"- grid_n={row['grid_n']}: status=no_data ({row['reason']})")
    lines.append("")

    lines.append(f"## Runs: {report['n_runs']} total")
    lines.append("")
    lines.append("Runs per comparison group:")
    for g, n in report["runs_per_group"].items():
        lines.append(f"- {g}: {n}")
    lines.append("")

    lines.append("## Classification label counts (across all runs; non-exclusive)")
    lines.append("")
    lines.append("| label | count |")
    lines.append("|---|---|")
    for label, count in sorted(report["classification_label_counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{label}` | {count} |")
    lines.append("")

    lines.append("## Applicability map (D_valid) -- by axis")
    am = report["applicability_map"]
    for axis_name, axis_key in [
        ("material", "by_material"), ("Phi_l regime", "by_phi_l_regime"),
        ("Theta_f regime", "by_theta_f_regime"), ("k_f vs k_s", "by_k_f_vs_ks"), ("grid_n", "by_grid_n"),
    ]:
        lines.append(f"### By {axis_name}")
        for key, counts in am[axis_key].items():
            counts_str = ", ".join(f"{k}={v}" for k, v in counts.items())
            lines.append(f"- **{key}**: {counts_str}")
        lines.append("")

    return "\n".join(lines)
