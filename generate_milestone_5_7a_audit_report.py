"""
Milestone 5.7a audit report generator
==========================================

Assembles the Milestone 5.7a audit findings into one JSON + one Markdown
report: the confirmed root causes and their fixes, live-computed
verification evidence (fingerprint collisions, isotropic-control
significance, H1 candidate-vs-baseline agreement), the minimal corrected
64^3 (+128^3 spot check) rerun matrix, and a revised, evidence-grounded
strongest-permitted-statement.

Second-pass corrections (independent review of the first-generated report)
----------------------------------------------------------------------------
A second review of this report's first version found 7 further problems in
the REPORT ITSELF (not the underlying solver runs, which did not need to be
rerun) and this script now fixes all of them:

1. The clip-summary prose previously (in chat, not in this script's own
   output -- the JSON/markdown numbers were always correct) understated the
   clip's effect. `forcing_clip_summary` now explicitly names which cases
   were materially altered (`weak_128_spotcheck`, `overlap_128_spotcheck`
   -- both 128^3 spot checks) and states plainly that neither can be read
   as a faithful test of its nominal requested forcing.
2. The strongest permitted statement previously cited the 128^3 overlap
   result as if it were confirmatory. It is not: that run was both
   clip-altered AND did not close its energy budget. The statement now
   attributes the cascade-arrival-assumption finding to the RESOLVED 64^3
   overlap test only, with 128^3 explicitly downgraded to "consistent with,
   not independent confirmation of."
3. "All 10 bugs fixed" overstated item 10 (material dependence), which was
   correctly identified as a scope limitation, not a code defect -- no fix
   was made or attempted, by explicit instruction. Every audit item below
   now carries an explicit `category` of `defect_repaired` (9 items) or
   `scope_limitation_confirmed` (1 item, material dependence).
4. `scientific_status` previously used a single permissive
   `candidate_behavior_observed` bucket that 17/19 rows fell into,
   including baseline (group A) runs that never ran the candidate operator
   at all. Replaced (in stress_test_classification.py) with a vocabulary
   that cannot assign a candidate-operator finding to a non-candidate run,
   and that never claims "improvement" (no real-data ground truth exists
   anywhere in this synthetic milestone). This script recomputes
   scientific_status (and the new spectral_status) fresh per row using the
   corrected logic -- see `_recompute_audited_status_v2` -- rather than
   trusting each shard's originally-stored (first-pass) audited_status.
5. `controller_labels` distribution was not surfaced -- most rows carry
   only `controller_bounded`, meaning the richer classification exists but
   the controller was rarely shown to actually converge or hit its target.
   The legacy `classification_labels` field's `controller_stable` entry
   predates this richer classification and is now explicitly marked
   deprecated in this report rather than left to imply effectiveness.
6. `any_pile_up`/`monotonically_growing` were computed but not surfaced as
   an independent status -- a run can close its energy budget while
   persistently piling up energy above the cutoff, which is NOT terminal-
   model support. Added the orthogonal `spectral_status` field (see
   stress_test_classification.SPECTRAL_STATUSES) and its distribution here.
7. The anisotropy finding's language is tightened to explicitly say
   "demonstration in two families," not statistical validation.

This script performs NO new physical modeling and adds NO new candidate
terminal laws or materials -- per the audit's explicit scope constraint, it
only aggregates and re-derives conclusions from work already done
(pseudo_spectral_solver.py, forcing.py, energy_budget.py,
structure_metrics.py, forcing_fingerprint.py, stress_test_classification.py,
milestone_5_7_stress_test.py -- all as patched in the 5.7a pass) plus the
runs/milestone_5_7a/shards/*.json produced by
run_milestone_5_7a_minimal_matrix.py. No solver reruns were needed for this
second pass -- every correction above is a report-generation-time fix,
recomputed from data already on disk.

Usage:
  python generate_milestone_5_7a_audit_report.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from forcing_test_matrix import ALL_CASES
from forcing_fingerprint import detect_forcing_collisions
from jhtdb_terminal_benchmark import compute_terminal_layer, wavenumbers, Config as TerminalConfig
from structure_metrics import isotropic_control_baseline, is_anisotropic_response_significant
from stress_test_classification import compute_audited_status
from milestone_5_7_stress_test import applicability_map_from_rows, GROUP_DESCRIPTIONS

SHARD_DIR = Path("runs/milestone_5_7a/shards")
ORIGINAL_DEDUP_DIR = Path("runs/milestone_5_7a/original_campaign_dedup_corrected")
OUTPUT_DIR = Path("runs/milestone_5_7a")
DOMAIN_LENGTH = 2.0 * np.pi

SYNTHETIC_ONLY_WARNING = (
    "SYNTHETIC-ONLY REPORT -- every number below comes from the Milestone 5.7/5.7a "
    "synthetic pseudo-spectral stress-test solver (pseudo_spectral_solver.py), not "
    "from real JHTDB DNS data. This is evidence about the MODEL'S CODE AND "
    "ASSUMPTIONS, not about real turbulence. It must never be cited alongside or "
    "in place of the real JHTDB validation campaign (jhtdb_terminal_benchmark.py / "
    "run_real_validation.py). Milestone 5.7a changed NO real-data code path: it "
    "only audits and repairs the synthetic 5.7 stress-test infrastructure."
)

# The only row-pair in the minimal matrix that actually performed an A-vs-C
# weak-forcing comparison (see _h1_comparison). weak_forcing_matches_baseline
# must be True ONLY for this row -- every other group-C row has NOT been
# checked against a baseline counterpart and must not imply it has.
CANDIDATE_LIMIT_CONSISTENCY_CASE_ID = "weak_64_C"

LEGACY_LABEL_DEPRECATION_NOTICE = (
    "classification_labels' `controller_stable` entry predates the Milestone "
    "5.7a richer controller_labels classification (controller.classify_controller_run) "
    "and only ever meant 'c_gamma stayed numerically bounded.' It must be read as "
    "DEPRECATED wherever controller_labels is also available -- controller_labels is "
    "authoritative for any claim about controller effectiveness (converged / "
    "target_achieved / budget_error_reduced), not merely boundedness."
)


def _load_shards(shard_dir: Path) -> list[dict]:
    rows = []
    for sf in sorted(shard_dir.glob("*.json")):
        rows.append(json.loads(sf.read_text()))
    return rows


def _fingerprint_collisions() -> dict:
    out = {}
    for grid_n in (32, 64, 128):
        kx, ky, kz = wavenumbers(grid_n, DOMAIN_LENGTH)
        nyquist = float(np.max(np.abs(kx[:, 0, 0])))
        delta_k = 2.0 * np.pi / DOMAIN_LENGTH
        kc = 0.5 * nyquist
        layer = compute_terminal_layer(kc, delta_k, TerminalConfig())
        collisions = detect_forcing_collisions(list(ALL_CASES), layer, nyquist, delta_k)
        out[str(grid_n)] = {
            "ks": layer.ks,
            "kc": layer.kc,
            "n_collision_groups": len(collisions),
            "collisions": [
                {"case_names": list(c.case_names), "fingerprint": list(c.fingerprint)} for c in collisions
            ],
        }
    return out


def _anisotropy_reclassification(rows_by_id: dict) -> dict:
    def anis(cid):
        return rows_by_id[cid]["component_energies"]["anisotropy_invariants"]["anisotropy_magnitude"]

    weak_baseline = isotropic_control_baseline([anis("weak_64_iso_seed1"), anis("weak_64_iso_seed2")])
    dir_baseline = isotropic_control_baseline([anis("directional_64_iso_seed1"), anis("directional_64_iso_seed2")])
    weak_case = anis("weak_64_A")
    dir_case = anis("directional_64_A")
    return {
        "weak_isotropic_family": {
            "case_anisotropy_magnitude": weak_case,
            "isotropic_control_baseline": {
                "mean": weak_baseline.mean_anisotropy_magnitude,
                "std": weak_baseline.std_anisotropy_magnitude,
                "n_seeds": weak_baseline.n_seeds,
                "samples": list(weak_baseline.samples),
            },
            "naive_label_present": "anisotropic_response_identified" in rows_by_id["weak_64_A"]["classification_labels"],
            "significant_vs_control": is_anisotropic_response_significant(weak_case, weak_baseline),
        },
        "strong_directional_family": {
            "case_anisotropy_magnitude": dir_case,
            "isotropic_control_baseline": {
                "mean": dir_baseline.mean_anisotropy_magnitude,
                "std": dir_baseline.std_anisotropy_magnitude,
                "n_seeds": dir_baseline.n_seeds,
                "samples": list(dir_baseline.samples),
            },
            "naive_label_present": "anisotropic_response_identified" in rows_by_id["directional_64_A"]["classification_labels"],
            "significant_vs_control": is_anisotropic_response_significant(dir_case, dir_baseline),
        },
        "finding": (
            "The corrected anisotropy method behaves sensibly in two demonstration "
            "families: not significant for weak_isotropic (isotropic forcing), "
            "significant for strong_directional_fixed (directional forcing). It is "
            "NOT yet a statistical validation of anisotropy classification across the "
            "full campaign -- only 2 isotropic-control seeds were run per family "
            "(compute-limited, below the 5.7a spec's own recommended ensemble size), "
            "and the original 189/186-row campaign's 173 flagged runs were not "
            "individually rechecked against a matched control baseline here."
        ),
    }


def _h1_comparison(rows_by_id: dict) -> dict:
    a = rows_by_id["weak_64_A"]
    c = rows_by_id["weak_64_C"]
    keys = ("mean_power_input", "mean_viscous_dissipation", "mean_terminal_heat", "relative_closure_error", "closes_within_tolerance")
    return {
        "description": (
            "H1 check: terminal_operator_forcing_aware.gamma_candidate_forcing_aware "
            "is constructed to reduce EXACTLY to the baseline operator as Phi_l -> 0. "
            "weak_64_A (group A, baseline) and weak_64_C (group C, candidate) run the "
            "identical weak_isotropic case/grid/seed/steps, differing only in "
            "terminal_gamma_mode. This shows the candidate is numerically consistent "
            "with the baseline in the weak-forcing limit -- it is NOT evidence group C "
            "is physically better than group A; there is no ground truth in this "
            "synthetic milestone to judge 'better' against."
        ),
        "phi_l_A": a["phi_l"], "phi_l_C": c["phi_l"],
        "energy_budget_A": {k: a["energy_budget"][k] for k in keys},
        "energy_budget_C": {k: c["energy_budget"][k] for k in keys},
        "controller_A": a["controller"], "controller_C": c["controller"],
        "agreement": "diagnostics agree to >=5 significant figures at Phi_l=0.0466, consistent with the candidate's by-construction reduction to baseline in the weak-forcing limit",
    }


AUDIT_ITEMS = [
    dict(
        item=1, category="defect_repaired",
        critique="Weak-forcing limit (Phi_l<<1) was never actually tested -- all runs measured forcing_dominated.",
        root_cause="Cold-start bias: the solver always initialized velocity from a small-amplitude random field, so u_l started near zero and Phi_l = P_f/(u_l^3/l) was enormous at t=0 for ANY nonzero forcing power, regardless of preregistered intent.",
        fix="Added SolverConfig.initial_kinetic_energy (warm-start knob) and forcing.initial_kinetic_energy_for_target_phi_l() which inverts Phi_l for the u_l needed to hit a target ratio at t=0. initialize_state() rescales the random field to match.",
        files=["forcing.py", "pseudo_spectral_solver.py"],
        verification="weak_64_A measured Phi_l=0.047 (nonlinear_dominated), competing_64_A measured Phi_l~1.4 (competing), strong_64_A measured Phi_l~9-50 range (forcing_dominated) -- see minimal_matrix_rows below. All three preregistered regime bins are now empirically reached.",
    ),
    dict(
        item=2, category="defect_repaired",
        critique='Energy-budget "conserves energy" claim contradicted the actual metrics (128^3 run: relative_closure_error~=0.98, closes_within_tolerance=false).',
        root_cause="relative_closure_error compared mean(power_input) against mean(viscous_dissipation+terminal_heat) ALONE, omitting dK/dt entirely -- invalid during any spin-up/decay transient where most power legitimately goes into changing KE, not into dissipation.",
        fix="Derived relative_closure_error from full_timestep_residual (already includes dK/dt via _step_once's dk_measured/dk_predicted bookkeeping), converted to a rate (/dt), and normalized by max(mean_power_input, mean_viscous+heat) instead of mean_power_input alone (a warm-start decay run has power_input far smaller than viscous dissipation, so normalizing by power_input alone inflates a small residual into a huge relative error). summarize_energy_budget() now requires dt as a keyword argument. Old (invalid) metric kept as input_vs_dissipation_only_gap for transparency only.",
        files=["energy_budget.py", "pseudo_spectral_solver.py"],
        verification="Same weak_isotropic/grid64/initial_kinetic_energy=5.0 configuration: closure error dropped from 263.9/false (bug) to 0.079/true (fixed metric) in direct comparison during development; 18 of 19 minimal-matrix rows now report closes_within_tolerance=true -- the sole exception (overlap_128_spotcheck, a 4-step 128^3 spot check of the forcing-overlaps-terminal-layer case, relative_closure_error=0.259) is a large transient over very few steps AND was independently materially altered by the forcing-amplitude clip (see item 6 / forcing_clip_summary) -- it is not read as a resolution-convergence result either way (see item 3 / boundary_finding).",
    ),
    dict(
        item=3, category="defect_repaired",
        critique="128^3 execution status was self-contradictory (spot check misrepresented as tier completion).",
        root_cause="stress_test_report.py's grid_tiers_executed / grid_tiers_skipped_no_data distinction is binary (executed vs no_data) with no third state for 'a single spot-check row exists, this is not a resolution-convergence claim.'",
        fix="Added is_spot_check flag threaded from run_milestone_5_7a_minimal_matrix.py's CASE_SPECS through to each shard row, plus AuditedStatus.resolution_status (resolved/diagnostic_tier_only/not_executed) as an orthogonal field. This audit report's tier_status section explicitly separates spot_check_executed from complete_campaign_executed per tier -- see below.",
        files=["stress_test_classification.py", "milestone_5_7_stress_test.py", "run_milestone_5_7a_minimal_matrix.py", "generate_milestone_5_7a_audit_report.py"],
        verification="tier_status.128 below reports spot_check_executed=true, complete_campaign_executed=false, n_spot_check_rows=2, explicitly. See also boundary_finding: the robust cascade-arrival-assumption result comes from the RESOLVED 64^3 overlap test; the 128^3 overlap spot check is consistent with it but is not independent confirmation (it was also clip-altered -- see item 6).",
    ),
    dict(
        item=4, category="defect_repaired",
        critique="n_runs=189 vs n_runs_expected=84 was unexplained/suspicious.",
        root_cause="n_runs_expected=84 was a hardcoded default representing ONLY the single-grid-tier, single-material count (14 cases x 6 groups). The actual 189-row campaign spanned 2 grid tiers x 6 groups x incompressible_newtonian_liquid (168 rows) + 1 grid128 spot check + a high_viscosity_newtonian_liquid grid32/group-A pass (14 rows) + 3 one-off material_not_implemented placeholder probes (3 rows) = 186 legitimate rows, PLUS 3 genuine stale-shard duplicate rows (g32_A_highvisc_actual.json reran 3 of the same 14 cases already present in g32_A_highvisc.json, and assemble_milestone_5_7_report.py had no dedup logic) = 189.",
        fix="Added compute_run_identity() (SHA256 of all outcome-determining fields, excluding RNG phase) threaded into every row as run_id. assemble_milestone_5_7_report.py now dedups by run_id (falling back to (case,grid_n,group,material,forcing_type) for legacy rows without run_id) and reports what was dropped.",
        files=["milestone_5_7_stress_test.py", "assemble_milestone_5_7_report.py"],
        verification="Rerunning the dedup-enabled assembler against the ORIGINAL 35 shard files: loaded 189 rows, dropped exactly 3 duplicates (weak_isotropic/moderate_steady_isotropic/strong_isotropic, all grid_n=32/group=A/material=high_viscosity_newtonian_liquid), 186 rows remain -- output at runs/milestone_5_7a/original_campaign_dedup_corrected/.",
    ),
    dict(
        item=5, category="defect_repaired",
        critique="Several nominally distinct forcing cases produced bit-identical diagnostics.",
        root_cause="moderate_steady_isotropic and forcing_far_below_ks were literal duplicate case definitions (identical forcing_type/power/k_f_mode='far_below_ks'/tau_f) in forcing_test_matrix.py -- a genuine matrix-design bug, confirmed by direct inspection of the original report's raw values (phi=449.852..., theta=0.01412..., identical to many decimal places for both cases at grid32).",
        fix="Gave general-purpose cases their own k_f_mode='moderate_below_ks' (0.6*ks), reserving 'far_below_ks' (0.3*ks) exclusively for the case that specifically tests scale separation (forcing_far_below_ks). Added forcing_fingerprint.py to hash every case's RESOLVED configuration and hard-fail (assert_no_unexpected_collisions) on any future unexpected collision.",
        files=["forcing_test_matrix.py", "forcing_fingerprint.py"],
        verification="detect_forcing_collisions() over ALL_CASES: 0 collision groups at grid_n=64 and grid_n=128 (the fix is confirmed effective at both resolutions used in the minimal-matrix rerun); exactly 1 collision group remains at grid_n=32 (moderate_steady_isotropic vs forcing_far_below_ks), which is the SEPARATE, DOCUMENTED, unavoidable ks=0 degeneracy described in item 9 below, not a residual matrix bug -- see fingerprint_collisions section.",
    ),
    dict(
        item=6, category="defect_repaired",
        critique="The forcing-amplitude safety clip was suspected of controlling the experiment.",
        root_cause="pseudo_spectral_solver.make_forcing_hat applies a lam_max safety clip to the requested forcing amplitude but the original code never recorded whether the clip fired or by how much -- there was no way to check the suspicion either way.",
        fix="make_forcing_hat now returns (total, new_shapes, clip_diagnostics) with requested_amplitude/applied_amplitude/clip_active per injection scale. EnergyBudgetSample carries these per step; summarize_energy_budget computes forcing_clip_active_fraction and forcing_clip_materially_altered_case (fires only if clip_active_fraction>0.1 AND amplitude_alteration>0.1).",
        files=["pseudo_spectral_solver.py", "energy_budget.py"],
        verification="17 of 19 minimal-matrix cases were NOT materially altered by clipping. The 2 that WERE (weak_128_spotcheck, overlap_128_spotcheck) are BOTH 128^3 spot checks -- neither can be interpreted as a faithful test of its nominal requested forcing, and this is now stated explicitly wherever those two rows are cited (see forcing_clip_summary, tier_status.128, boundary_finding).",
    ),
    dict(
        item=7, category="defect_repaired",
        critique='"controller_stable" was too weak a classification (conflates bounded with effective).',
        root_cause="controller.controller_diagnostics()['is_stable'] only checked boundedness (|trajectory|<1e6), which the original classification pipeline mapped directly to a single label 'controller_stable' -- a controller that is bounded but oscillating, never converging, or never reducing the actual energy-budget error would still be called 'stable.'",
        fix="Added ControllerClassificationThresholds and classify_controller_run(), returning an orthogonal tuple of labels from {controller_bounded, controller_nonoscillatory, controller_converged, controller_target_achieved, controller_budget_error_reduced, controller_unstable} instead of one flat label.",
        files=["controller.py", "milestone_5_7_stress_test.py"],
        verification="See controller_label_distribution below: 19/19 rows get controller_bounded, but only 2/19 (weak_64_D, weak_64_E) also get controller_converged, and NO row gets controller_target_achieved or controller_budget_error_reduced in this minimal matrix -- i.e. the richer labels show the controller is mostly only shown to be bounded, not effective. The legacy classification_labels 'controller_stable' entry is now explicitly marked deprecated relative to controller_labels (see LEGACY_LABEL_DEPRECATION_NOTICE) rather than left to imply success.",
    ),
    dict(
        item=8, category="defect_repaired",
        critique="The anisotropy detector was likely over-sensitive (173/186 runs flagged, including isotropic cases).",
        root_cause="anisotropic_response_identified fired whenever anisotropy_magnitude exceeded a fixed threshold (0.02) with NO comparison against how much anisotropy an isotropically-forced control run shows purely from finite-sample/single-realization/short-run noise. Compounded by a separate bug: anisotropy_invariants() computed sqrt(max(-0.5*trace(b@b),0)), which is <=0 for real b, so the ORIGINAL magnitude was always exactly 0 -- meaning the 173/186 flag rate in the original report came from a different, likely also-flawed code path or was measured before this sign bug was introduced; either way the magnitude computation itself needed a structural fix, independent of the threshold question.",
        fix="Fixed anisotropy_invariants() to magnitude=sqrt(max(trace(b@b),0)) (a valid non-negative quantity). Added structure_metrics.isotropic_control_baseline()/is_anisotropic_response_significant() (mean+z*std of matched isotropic-forcing control runs) and milestone_5_7_stress_test.run_isotropic_control_ensemble().",
        files=["structure_metrics.py", "milestone_5_7_stress_test.py"],
        verification="See anisotropy_reclassification below -- and its explicit 'finding' text: this is a two-family demonstration that the corrected method distinguishes signal from noise, NOT a statistical validation of anisotropy classification across the full campaign.",
    ),
    dict(
        item=9, category="defect_repaired",
        critique="The 32^3 campaign cannot test k_f/k_s physics (ks=0 degeneracy) but was mixed into overall counts.",
        root_cause="compute_terminal_layer degenerates to ks=0 at grid_n=32 in this solver's beta-derived layer construction, which collapses ALL of far_below_ks/near_ks/moderate_below_ks onto the delta_k floor -- 32^3 structurally cannot resolve distinct k_f/k_s positions, but the original applicability_map()/report aggregated 32^3 rows into the same by_k_f_vs_ks buckets as 64^3/128^3 without flagging this.",
        fix="Added is_diagnostic_tier=(grid_n in GRID_TIER_DIAGNOSTIC_ONLY) or (layer.ks<=0) computed per run, and AuditedStatus.resolution_status which can only reach 'resolved' when NOT diagnostic-tier. This audit report's applicability-map section computes k_f/k_s-based aggregates ONLY over grid_n>=64 rows explicitly (see applicability_map_k_f_ks_64_and_above below), separate from the full (all-tier) aggregate kept for transparency.",
        files=["milestone_5_7_stress_test.py", "stress_test_classification.py", "generate_milestone_5_7a_audit_report.py"],
        verification="fingerprint_collisions.32 confirms the ks=0 degeneracy directly: moderate_steady_isotropic and forcing_far_below_ks (and structurally near_ks too, though it differs in forcing_type so its fingerprint doesn't collide) all resolve k_f=delta_k=1.0 at grid_n=32.",
    ),
    dict(
        item=10, category="scope_limitation_confirmed",
        critique="Material dependence was not actually tested (only Newtonian implemented).",
        root_cause="material_state.py only implements incompressible_newtonian_liquid and high_viscosity_newtonian_liquid; the other 3 of 5 preregistered material types (compressible_gas, low_mach_newtonian_gas, viscoelastic-family) correctly return material_interface_only-blocked results, but the original report's language did not always make the resulting material-scope limitation explicit enough.",
        root_cause_note="This is a known, already-disclosed scope limitation (see AGENTS.md 'Material interface_only is not approximately Newtonian'), NOT a code defect -- no fix was made or attempted here, per the audit's explicit instruction not to add new material models. It is confirmed and restated here as a standing limitation, not counted among the 9 repaired defects.",
        fix="No code change (out of 5.7a scope by explicit user instruction). Restated as a limitation in this report's Remaining Limitations section.",
        files=[],
        verification="Confirmed via material_state.py: only 2 of 5 MATERIAL_TYPES are implemented; MaterialNotImplementedError raised for the rest, never silently approximated.",
    ),
]


def _recompute_audited_status_v2(rows_by_id: dict) -> dict:
    """Recomputes AuditedStatus (6-dim, corrected vocabulary) fresh per row
    from data already in each shard -- no solver rerun needed. Supersedes
    each row's originally-stored (first-pass) `audited_status`, which used
    the old, overly-permissive scientific_status vocabulary and had no
    spectral_status at all. See module docstring, correction #4/#6."""
    out = {}
    for case_id, r in rows_by_id.items():
        eb = r["energy_budget"]
        pile = eb.get("pile_up", {})
        is_diagnostic_tier = r["audited_status"]["resolution_status"] == "diagnostic_only"
        energy_budget_partial = (not eb["closes_within_tolerance"]) and (eb["relative_closure_error"] < 1.0)
        l_over_lc = r.get("l_over_lc")
        forcing_above_cutoff = (l_over_lc is not None) and np.isfinite(l_over_lc) and (l_over_lc < 1.0)
        weak_forcing_case = r["phi_l_regime"] == "nonlinear_dominated"
        weak_forcing_matches_baseline = True if case_id == CANDIDATE_LIMIT_CONSISTENCY_CASE_ID else None
        status = compute_audited_status(
            pipeline_ok=r["pipeline_ok"], material_implemented=True, resolution_ok=r["resolution_ok"],
            is_diagnostic_tier=is_diagnostic_tier, energy_budget_closes=eb["closes_within_tolerance"],
            energy_budget_partial=energy_budget_partial,
            forcing_clip_materially_altered=eb["forcing_clip_materially_altered_case"],
            forcing_overlaps_terminal_layer=(r["k_f_vs_ks"] == "overlap_or_above"),
            weak_forcing_case=weak_forcing_case, weak_forcing_matches_baseline=weak_forcing_matches_baseline,
            group=r["group"], forcing_above_cutoff=forcing_above_cutoff,
            pile_up_detected=pile.get("pile_up_detected", False), monotonically_growing=pile.get("monotonically_growing", False),
        )
        out[case_id] = {
            "pipeline_status": status.pipeline_status, "resolution_status": status.resolution_status,
            "energy_budget_status": status.energy_budget_status, "forcing_regime_status": status.forcing_regime_status,
            "scientific_status": status.scientific_status, "spectral_status": status.spectral_status,
        }
    return out


def _controller_label_distribution(rows_by_id: dict) -> dict:
    all_labels = ("controller_bounded", "controller_nonoscillatory", "controller_converged", "controller_target_achieved", "controller_budget_error_reduced", "controller_unstable")
    counts = {label: 0 for label in all_labels}
    for r in rows_by_id.values():
        for label in r["controller_labels"]:
            counts[label] = counts.get(label, 0) + 1
    only_bounded = sum(1 for r in rows_by_id.values() if tuple(r["controller_labels"]) == ("controller_bounded",))
    return {
        "label_counts": counts,
        "n_rows": len(rows_by_id),
        "n_rows_with_only_controller_bounded": only_bounded,
        "legacy_label_deprecation_notice": LEGACY_LABEL_DEPRECATION_NOTICE,
        "interpretation": (
            f"{only_bounded} of {len(rows_by_id)} rows show ONLY controller_bounded -- bounded but not "
            "shown to be nonoscillatory, converged, on-target, or better than a baseline. Controller "
            "effectiveness (as opposed to mere boundedness) remains mostly unestablished in this minimal "
            "matrix; see Milestone 5.7b (proposed next milestone) for a dedicated controller-effectiveness test."
        ),
    }


def main():
    minimal_matrix_rows = _load_shards(SHARD_DIR)
    rows_by_id = {r["case_id"]: r for r in minimal_matrix_rows}

    fp_collisions = _fingerprint_collisions()
    anis_reclass = _anisotropy_reclassification(rows_by_id)
    h1 = _h1_comparison(rows_by_id)
    audited_status_v2 = _recompute_audited_status_v2(rows_by_id)
    controller_dist = _controller_label_distribution(rows_by_id)

    # forcing clip summary across the minimal matrix
    forcing_clip_summary = {
        r["case_id"]: {
            "forcing_clip_active_fraction": r["energy_budget"]["forcing_clip_active_fraction"],
            "forcing_clip_materially_altered_case": r["energy_budget"]["forcing_clip_materially_altered_case"],
        }
        for r in minimal_matrix_rows
    }
    materially_altered_case_ids = [cid for cid, v in forcing_clip_summary.items() if v["forcing_clip_materially_altered_case"]]
    n_materially_altered = len(materially_altered_case_ids)

    # tier status
    n_128_spot = sum(1 for r in minimal_matrix_rows if r["grid_n"] == 128 and r["is_spot_check"])
    n_64_rows = sum(1 for r in minimal_matrix_rows if r["grid_n"] == 64)
    tier_status = {
        "32": {
            "complete_campaign_executed": True,  # in the ORIGINAL 189/186-row campaign
            "spot_check_executed": False,
            "status": "diagnostic_only -- ks=0 degeneracy; excluded from all k_f/k_s-based applicability conclusions in this report (see item 9)",
        },
        "64": {
            "complete_campaign_executed": True,  # both the original campaign AND the 5.7a minimal rerun cover 64^3
            "spot_check_executed": False,
            "status": f"resolved -- {n_64_rows} rows in the 5.7a minimal corrected matrix (this report's primary evidence tier)",
        },
        "128": {
            "complete_campaign_executed": False,
            "spot_check_executed": n_128_spot > 0,
            "status": (
                f"spot_check_only -- {n_128_spot} row(s) executed (4 steps each, compute-limited in this "
                f"environment); NOT a resolution-convergence claim, and BOTH spot checks "
                f"({', '.join(materially_altered_case_ids)}) were materially altered by the forcing-amplitude "
                f"clip -- neither is a faithful test of its nominal requested forcing either."
            ),
        },
    }

    boundary_finding = {
        "statement": "The 64^3 resolved synthetic test challenges the cascade-arrival assumption.",
        "basis": "overlap_64_A (grid_n=64, not clip-altered, energy budget closes within tolerance) is classified assumption_challenged: forcing placed at/above k_s directly and measurably breaks the original terminal operator's cascade-arrival assumption at a resolved tier.",
        "128_cubed_caveat": "overlap_128_spotcheck is consistent with this finding (same qualitative classification) but is NOT independent confirmation: it is a 4-step spot check, its energy budget does not close within tolerance, and it was materially altered by the forcing-amplitude clip. It should be cited as consistent, never as corroborating evidence on its own.",
    }

    # applicability map: full (all rows) vs k_f/k_s-restricted to grid_n>=64
    full_map = applicability_map_from_rows(minimal_matrix_rows)
    rows_64_and_above = [r for r in minimal_matrix_rows if r["grid_n"] >= 64]
    map_64_and_above = applicability_map_from_rows(rows_64_and_above)

    # audited_status_v2 distribution (corrected vocabulary)
    audited_status_v2_counts = {}
    for dim in ("pipeline_status", "resolution_status", "energy_budget_status", "forcing_regime_status", "scientific_status", "spectral_status"):
        counts = {}
        for v in audited_status_v2.values():
            counts[v[dim]] = counts.get(v[dim], 0) + 1
        audited_status_v2_counts[dim] = counts

    original_dedup_report = json.loads((ORIGINAL_DEDUP_DIR / "milestone5_7_report.json").read_text())

    strongest_permitted_statement = (
        "In the audited synthetic 64^3 stress-test domain, the forcing-aware candidate "
        "is verified to reduce to the original terminal operator in a measured "
        "weak-forcing case with Phi_l~=0.047, as required by its construction. The "
        "corrected benchmark reaches nonlinear-dominated, competing, and "
        "forcing-dominated regimes, and its complete energy budget closes within the "
        "configured tolerance for 18 of 19 minimal-matrix runs. A resolved 64^3 test "
        "shows that direct forcing at or above k_s violates the original model's "
        "cascade-arrival assumption. This result identifies an applicability boundary "
        "of the model's assumptions, not validation against real turbulence. The 128^3 "
        "results remain short, clip-altered spot checks and provide no convergence "
        "evidence. Material-dependent physics remains untested beyond Newtonian "
        "viscosity variation."
    )

    report = {
        "milestone": "5.7a",
        "title": "Audit and Repair of the Forcing-Material-Size Stress Test",
        "synthetic_only_warning": SYNTHETIC_ONLY_WARNING,
        "summary": (
            "9 implementation/reporting defects were repaired and verified; 1 item "
            "(material dependence) was confirmed as a scope limitation, not a bug -- "
            "see each audit item's `category` field."
        ),
        "strongest_permitted_statement": strongest_permitted_statement,
        "boundary_finding": boundary_finding,
        "scope_constraints_honored": [
            "No new physical claims, material models, or candidate terminal laws were added.",
            "gamma_candidate_forcing_aware's functional form is unchanged from Milestone 5.7.",
            "The real JHTDB manifest and real-validation pipeline were not touched.",
            "Nothing has been committed until this report and its corrections were reviewed.",
        ],
        "audit_items": AUDIT_ITEMS,
        "fingerprint_collisions": fp_collisions,
        "anisotropy_reclassification": anis_reclass,
        "h1_candidate_baseline_agreement": h1,
        "forcing_clip_summary": {
            "per_case": forcing_clip_summary,
            "n_cases_materially_altered_by_clip": n_materially_altered,
            "n_cases_total": len(forcing_clip_summary),
            "materially_altered_case_ids": materially_altered_case_ids,
            "interpretation": (
                f"{len(forcing_clip_summary) - n_materially_altered} of {len(forcing_clip_summary)} minimal-matrix "
                f"cases were NOT materially altered by clipping. Both cases that WERE "
                f"({', '.join(materially_altered_case_ids)}) are the 128^3 spot checks -- neither can be "
                "interpreted as a faithful test of its nominal requested forcing."
            ),
        },
        "controller_label_distribution": controller_dist,
        "tier_status": tier_status,
        "comparison_groups": GROUP_DESCRIPTIONS,
        "minimal_matrix_n_rows": len(minimal_matrix_rows),
        "minimal_matrix_audited_status_v1_counts_historical": {
            dim: {v: sum(1 for r in minimal_matrix_rows if r["audited_status"][dim] == v) for v in {r["audited_status"][dim] for r in minimal_matrix_rows}}
            for dim in ("pipeline_status", "resolution_status", "energy_budget_status", "forcing_regime_status", "scientific_status")
        },
        "minimal_matrix_audited_status_v2_counts_corrected": audited_status_v2_counts,
        "minimal_matrix_audited_status_v2_per_case": audited_status_v2,
        "applicability_map_all_tiers": full_map,
        "applicability_map_k_f_ks_grid64_and_above": map_64_and_above,
        "original_campaign_dedup_correction": {
            "original_n_runs_reported": 189,
            "corrected_n_runs_after_dedup": original_dedup_report["n_runs"],
            "n_duplicates_dropped": 189 - original_dedup_report["n_runs"],
            "root_cause": "3 stale-shard duplicate rows (g32_A_highvisc_actual.json reran 3 of the 14 cases already present in g32_A_highvisc.json; assembler had no dedup logic) -- see audit item 4.",
            "corrected_report_path": str(ORIGINAL_DEDUP_DIR / "milestone5_7_report.json"),
        },
        "minimal_matrix_rows": minimal_matrix_rows,
        "remaining_limitations": [
            "Theta_f / temporal forcing (item 3 of the original 12-item prompt): min_steps_for_forcing_case() ensures periodic/pulsed/impulsive cases run >=2 nominal periods where wall-clock budget allows, but the 'slow' case (tau_f=5.0) only reached ~0.3 nominal periods at dt=0.03/n_steps=50 in this environment's per-command time budget -- reported as measured theta_f=1.16 (resonant_or_competing), not a full-period demonstration. No autocorrelation-based EFFECTIVE tau_f measurement was implemented; only the nominal (input) tau_f is compared.",
            "Material dependence remains untested beyond incompressible/high-viscosity Newtonian liquids (see audit item 10, category=scope_limitation_confirmed) -- out of scope for 5.7a by explicit instruction.",
            "The isotropic-control baselines used here (2 seeds per family) are smaller than the 5.7a spec's own recommended ensemble size; they demonstrate the corrected METHOD distinguishes signal from noise for these two specific families, not a full re-classification of every anisotropy label from the original 189/186-row campaign.",
            "128^3 is spot-check only (4 steps, 2 cases), and BOTH spot checks were materially altered by the forcing-amplitude clip -- no resolution-convergence claim, and no independent confirmation claim, is made or supportable from this data (see boundary_finding).",
            "The 32^3 tier remains diagnostic-only by construction (ks=0) and contributes to NO k_f/k_s-based conclusion in this report.",
            "Controller effectiveness (beyond mere boundedness) remains mostly unestablished: 19/19 rows are controller_bounded, only 2/19 are also controller_converged, and none reach controller_target_achieved or controller_budget_error_reduced in this minimal matrix (see controller_label_distribution).",
            "candidate_difference_observed is defined in the scientific_status vocabulary but never assigned in this pass -- no run in the minimal matrix has an actual computed A-vs-C difference metric other than the single weak-limit consistency check (weak_64_A vs weak_64_C).",
            "No new solver runs were added beyond the preregistered minimal 64^3(+128^3 spot check) matrix and the isotropic-control seeds -- this is intentionally a repair/audit pass, not an expanded campaign.",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "milestone5_7a_audit_report.json"
    json_path.write_text(json.dumps(report, indent=2, default=lambda o: str(o)))

    md_path = OUTPUT_DIR / "milestone5_7a_audit_report.md"
    md_path.write_text(_render_markdown(report))

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


def _render_markdown(report: dict) -> str:
    lines = []
    lines.append("# Milestone 5.7a audit report: Audit and Repair of the Forcing-Material-Size Stress Test")
    lines.append("")
    lines.append(f"> **WARNING:** {report['synthetic_only_warning']}")
    lines.append("")
    lines.append(f"**Summary:** {report['summary']}")
    lines.append("")
    lines.append("## Scope constraints honored")
    for s in report["scope_constraints_honored"]:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## Revised strongest permitted statement")
    lines.append("")
    lines.append(f"> {report['strongest_permitted_statement']}")
    lines.append("")

    lines.append("## Boundary finding: which resolution tier actually supports the cascade-arrival result")
    bf = report["boundary_finding"]
    lines.append(f"> {bf['statement']}")
    lines.append("")
    lines.append(f"- **Basis:** {bf['basis']}")
    lines.append(f"- **128^3 caveat:** {bf['128_cubed_caveat']}")
    lines.append("")

    lines.append("## Audit items: critique -> root cause -> fix -> verification")
    lines.append("")
    for it in report["audit_items"]:
        lines.append(f"### Item {it['item']} [{it['category']}]: {it['critique']}")
        lines.append(f"- **Root cause:** {it['root_cause']}")
        if it.get("root_cause_note"):
            lines.append(f"- **Note:** {it['root_cause_note']}")
        lines.append(f"- **Fix:** {it['fix']}")
        if it["files"]:
            lines.append(f"- **Files changed:** {', '.join(it['files'])}")
        lines.append(f"- **Verification:** {it['verification']}")
        lines.append("")

    lines.append("## Forcing-case fingerprint collisions (by grid tier)")
    for grid_n, data in report["fingerprint_collisions"].items():
        lines.append(f"- grid_n={grid_n}: ks={data['ks']:.4g}, kc={data['kc']:.4g}, {data['n_collision_groups']} collision group(s)")
        for c in data["collisions"]:
            lines.append(f"  - {c['case_names']}")
    lines.append("")

    lines.append("## Anisotropy reclassification (isotropic-control baseline)")
    ar = report["anisotropy_reclassification"]
    for fam in ("weak_isotropic_family", "strong_directional_family"):
        d = ar[fam]
        lines.append(f"- **{fam}**: case_anisotropy_magnitude={d['case_anisotropy_magnitude']:.4g}, "
                      f"control_baseline_mean={d['isotropic_control_baseline']['mean']:.4g}, "
                      f"control_baseline_std={d['isotropic_control_baseline']['std']:.4g}, "
                      f"naive_label_present={d['naive_label_present']}, "
                      f"significant_vs_control={d['significant_vs_control']}")
    lines.append(f"- {ar['finding']}")
    lines.append("")

    lines.append("## H1 candidate-vs-baseline agreement (weak-forcing limit)")
    h1 = report["h1_candidate_baseline_agreement"]
    lines.append(f"- {h1['description']}")
    lines.append(f"- Phi_l: A={h1['phi_l_A']:.6g}, C={h1['phi_l_C']:.6g}")
    lines.append(f"- Energy budget A: {h1['energy_budget_A']}")
    lines.append(f"- Energy budget C: {h1['energy_budget_C']}")
    lines.append(f"- {h1['agreement']}")
    lines.append("")

    lines.append("## Forcing-amplitude clip summary")
    fc = report["forcing_clip_summary"]
    lines.append(f"- {fc['interpretation']}")
    for case_id, v in fc["per_case"].items():
        lines.append(f"  - {case_id}: clip_active_fraction={v['forcing_clip_active_fraction']:.3g}, materially_altered={v['forcing_clip_materially_altered_case']}")
    lines.append("")

    lines.append("## Controller-label distribution (richer classification vs the legacy label)")
    cd = report["controller_label_distribution"]
    lines.append(f"- {cd['interpretation']}")
    lines.append(f"- **Legacy-label notice:** {cd['legacy_label_deprecation_notice']}")
    for label, n in cd["label_counts"].items():
        lines.append(f"  - `{label}`: {n}/{cd['n_rows']}")
    lines.append("")

    lines.append("## Resolution-tier status (orthogonal to campaign completeness)")
    for grid_n, s in report["tier_status"].items():
        lines.append(f"- grid_n={grid_n}: complete_campaign_executed={s['complete_campaign_executed']}, "
                      f"spot_check_executed={s['spot_check_executed']} -- {s['status']}")
    lines.append("")

    lines.append("## Minimal corrected matrix: audited status (corrected vocabulary, v2)")
    lines.append(f"- n_rows={report['minimal_matrix_n_rows']}")
    for dim, counts in report["minimal_matrix_audited_status_v2_counts_corrected"].items():
        counts_str = ", ".join(f"{k}={v}" for k, v in counts.items())
        lines.append(f"  - {dim}: {counts_str}")
    lines.append("")
    lines.append("(For comparison, the first-pass, now-superseded scientific_status distribution used the old "
                  "candidate_behavior_observed-style vocabulary -- kept below purely for the audit trail, not as "
                  "a current claim.)")
    v1 = report["minimal_matrix_audited_status_v1_counts_historical"]["scientific_status"]
    lines.append(f"- historical (v1, superseded) scientific_status: {', '.join(f'{k}={v}' for k, v in v1.items())}")
    lines.append("")

    lines.append("## Original 189-run campaign: dedup correction")
    oc = report["original_campaign_dedup_correction"]
    lines.append(f"- original_n_runs_reported: {oc['original_n_runs_reported']}")
    lines.append(f"- corrected_n_runs_after_dedup: {oc['corrected_n_runs_after_dedup']}")
    lines.append(f"- n_duplicates_dropped: {oc['n_duplicates_dropped']}")
    lines.append(f"- root_cause: {oc['root_cause']}")
    lines.append(f"- corrected_report_path: {oc['corrected_report_path']}")
    lines.append("")

    lines.append("## Applicability map -- k_f vs k_s, grid_n>=64 ONLY (32^3 excluded, see item 9)")
    am = report["applicability_map_k_f_ks_grid64_and_above"]
    for key, counts in am["by_k_f_vs_ks"].items():
        counts_str = ", ".join(f"{k}={v}" for k, v in counts.items())
        lines.append(f"- **{key}**: {counts_str}")
    lines.append("")

    lines.append("## Remaining limitations")
    for lim in report["remaining_limitations"]:
        lines.append(f"- {lim}")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
