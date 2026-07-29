"""
Milestone 5.7 run/case classification
=========================================

Extends run_classification.py's ladder discipline to the forcing/material/
size stress test. This is deliberately a *richer* vocabulary than a binary
supported/not-supported flag -- per the Milestone 5.7 spec's success
condition #8 ("failures are correctly classified rather than hidden") and
its explicit instruction not to use a binary result "without specifying the
tested forcing, material and size domain."

Every classification below must be attached to the specific (forcing case,
material, grid_n) tuple it was computed for -- see
`StressTestClassification.domain`. There is no dataset-level or milestone-
level single verdict; `milestone_5_7_stress_test.py`'s applicability map is
an aggregation of these per-domain classifications, not a replacement for
them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

VALID_LABELS = (
    "pipeline_only",
    "insufficient_resolution",
    "energy_budget_valid",
    "weak_forcing_consistent",
    "forcing_sensitive",
    "forcing_overlap_invalidates_assumption",
    "controller_stable",
    "controller_unstable",
    "anisotropic_response_identified",
    "size_effect_identified",
    "material_interface_only",
    "terminal_model_supported_in_domain",
    "terminal_model_requires_extension",
    "terminal_model_not_supported",
    "blocked",
)


@dataclass(frozen=True)
class RunDomain:
    """Exactly what was tested -- required alongside every classification."""

    forcing_case: str
    material: str
    grid_n: int
    forcing_type: str
    phi_l_regime: str  # "nonlinear_dominated" | "competing" | "forcing_dominated" | "undefined"
    theta_f_regime: str  # "quasi_steady" | "resonant_or_competing" | "rapid" | "undefined"
    k_f_vs_ks: str  # "below" | "near" | "overlap_or_above"


@dataclass(frozen=True)
class StressTestClassification:
    domain: RunDomain
    labels: tuple[str, ...]  # non-exclusive; a run can carry several
    notes: tuple[str, ...] = ()

    def __post_init__(self):
        bad = [l for l in self.labels if l not in VALID_LABELS]
        if bad:
            raise ValueError(f"invalid classification label(s) {bad}; must be from {VALID_LABELS}")
        if not self.labels:
            raise ValueError("a run must carry at least one classification label")


PIPELINE_STATUSES = ("failed", "passed")
RESOLUTION_STATUSES = ("diagnostic_only", "insufficient", "resolved")
ENERGY_BUDGET_STATUSES = ("invalid", "partial", "closed")
FORCING_REGIME_STATUSES = ("requested_only", "measured", "altered_by_clip")

# Milestone 5.7a re-audit (second pass): the first-pass vocabulary's
# "candidate_behavior_observed" was too permissive -- it fired on 17/19
# minimal-matrix rows, including baseline (group A, no candidate operator
# involved at all) runs, runs with persistent spectral pile-up, and runs
# where the controller was only ever shown to be bounded, never converged
# or on-target. Replaced with a vocabulary that cannot imply a candidate
# finding for a baseline run, and that never claims "improvement" (there is
# no real-data ground truth anywhere in this synthetic milestone to improve
# against):
#   synthetic_run_valid              -- ran correctly, resolved, budget
#                                        closed; no candidate-operator claim.
#   candidate_limit_consistency_observed -- group C, weak-forcing case,
#                                        matches its group-A counterpart
#                                        (the ONLY thing H1 was ever meant
#                                        to check).
#   candidate_difference_observed    -- group C, NOT the weak-limit check,
#                                        and a measured difference from a
#                                        baseline counterpart exists.
#                                        Reserved: nothing in the current
#                                        pipeline computes this difference
#                                        yet, so no run is assigned it --
#                                        it must never be inferred without
#                                        an actual A/C comparison.
#   candidate_improvement_not_testable -- group C, not the weak-limit
#                                        check: this run cannot support any
#                                        "better than baseline" claim,
#                                        stated explicitly rather than left
#                                        implicit.
#   assumption_challenged            -- forcing overlaps/exceeds k_s.
#   not_testable                     -- pipeline failed or resolution is
#                                        diagnostic-only/insufficient.
SCIENTIFIC_STATUSES = (
    "not_testable", "assumption_challenged", "synthetic_run_valid",
    "candidate_limit_consistency_observed", "candidate_difference_observed",
    "candidate_improvement_not_testable",
)

# Milestone 5.7a re-audit: energy-budget CLOSURE (does P_input balance
# dK/dt + dissipation + heat + residual) and spectral PLACEMENT (is energy
# piling up above the terminal cutoff instead of being removed) are
# different questions -- a run can close its budget while persistently
# accumulating energy above kc, and reporting only energy_budget_status
# would hide that. spectral_status is therefore a separate, orthogonal
# dimension, not a sub-case of energy_budget_status.
#   no_detected_pileup   -- energy_above_cutoff stayed at/near the noise
#                            floor for the whole run.
#   transient_pileup      -- pile-up detected but did not grow across the
#                            run (detect_terminal_pile_up.monotonically_
#                            growing is False) -- may just be a spin-up
#                            transient in a short run.
#   persistent_pileup      -- pile-up detected AND grew across the run --
#                            the strongest spectral-placement warning this
#                            pipeline can currently issue.
#   forcing_above_cutoff   -- the case's own forcing injects above k_c
#                            (l_over_lc < 1) -- pile-up here is an expected
#                            consequence of the forcing placement itself,
#                            not necessarily a terminal-operator failure.
#   unresolved             -- diagnostic-tier resolution; no spectral claim
#                            is supportable.
SPECTRAL_STATUSES = ("no_detected_pileup", "transient_pileup", "persistent_pileup", "forcing_above_cutoff", "unresolved")


@dataclass(frozen=True)
class AuditedStatus:
    """Milestone 5.7a audit item 10 (extended in the re-audit): six
    ORTHOGONAL status dimensions, replacing the previous practice of
    folding `pipeline_only` and `terminal_model_not_supported` into the
    same flat label list as if they were peer conclusions. A run's
    scientific_status is only meaningful when read together with its
    resolution_status, energy_budget_status, AND spectral_status -- e.g.
    `assumption_challenged` at resolution_status='diagnostic_only' is a
    hint, not evidence, and a `closed` energy budget with a `persistent_
    pileup` spectral_status is NOT terminal-model support."""

    pipeline_status: str
    resolution_status: str
    energy_budget_status: str
    forcing_regime_status: str
    scientific_status: str
    spectral_status: str

    def __post_init__(self):
        checks = [
            (self.pipeline_status, PIPELINE_STATUSES, "pipeline_status"),
            (self.resolution_status, RESOLUTION_STATUSES, "resolution_status"),
            (self.energy_budget_status, ENERGY_BUDGET_STATUSES, "energy_budget_status"),
            (self.forcing_regime_status, FORCING_REGIME_STATUSES, "forcing_regime_status"),
            (self.scientific_status, SCIENTIFIC_STATUSES, "scientific_status"),
            (self.spectral_status, SPECTRAL_STATUSES, "spectral_status"),
        ]
        for value, valid, name in checks:
            if value not in valid:
                raise ValueError(f"{name}={value!r} must be one of {valid}")


def classify_spectral_status(
    *, is_diagnostic_tier: bool, forcing_above_cutoff: bool, pile_up_detected: bool, monotonically_growing: bool,
) -> str:
    """See SPECTRAL_STATUSES above for the meaning of each value. Computed
    independently of energy_budget_status -- closure and spectral placement
    are different questions (Milestone 5.7a re-audit)."""
    if is_diagnostic_tier:
        return "unresolved"
    if forcing_above_cutoff:
        return "forcing_above_cutoff"
    if not pile_up_detected:
        return "no_detected_pileup"
    return "persistent_pileup" if monotonically_growing else "transient_pileup"


def compute_audited_status(
    *,
    pipeline_ok: bool,
    material_implemented: bool,
    resolution_ok: bool,
    is_diagnostic_tier: bool,
    energy_budget_closes: bool,
    energy_budget_partial: bool,
    forcing_clip_materially_altered: bool,
    forcing_overlaps_terminal_layer: bool,
    weak_forcing_case: bool,
    weak_forcing_matches_baseline: bool | None,
    group: str,
    forcing_above_cutoff: bool = False,
    pile_up_detected: bool = False,
    monotonically_growing: bool = False,
) -> AuditedStatus:
    """Computes the six orthogonal statuses independently -- no status here
    short-circuits or implies another; a caller must check
    resolution_status/energy_budget_status/spectral_status before trusting
    scientific_status, exactly the discipline the 5.7a audit requires.

    `group` replaces the first audit pass's `anisotropy_significant` input
    to scientific_status (re-audit finding: anisotropy is reported via
    classification_labels/the isotropic-control baseline, not folded into
    scientific_status -- a baseline (group A) run showing anisotropy is not
    a "candidate" finding at all, since group A never runs the candidate
    operator)."""
    if not material_implemented:
        pipeline_status = "failed"
    elif not pipeline_ok:
        pipeline_status = "failed"
    else:
        pipeline_status = "passed"

    if pipeline_status == "failed":
        resolution_status = "insufficient"
        energy_budget_status = "invalid"
        forcing_regime_status = "requested_only"
        scientific_status = "not_testable"
        spectral_status = "unresolved"
        return AuditedStatus(pipeline_status, resolution_status, energy_budget_status, forcing_regime_status, scientific_status, spectral_status)

    if is_diagnostic_tier:
        resolution_status = "diagnostic_only"
    elif not resolution_ok:
        resolution_status = "insufficient"
    else:
        resolution_status = "resolved"

    if energy_budget_closes:
        energy_budget_status = "closed"
    elif energy_budget_partial:
        energy_budget_status = "partial"
    else:
        energy_budget_status = "invalid"

    forcing_regime_status = "altered_by_clip" if forcing_clip_materially_altered else "measured"

    spectral_status = classify_spectral_status(
        is_diagnostic_tier=is_diagnostic_tier, forcing_above_cutoff=forcing_above_cutoff,
        pile_up_detected=pile_up_detected, monotonically_growing=monotonically_growing,
    )

    # scientific_status is deliberately conservative: it can only claim
    # anything beyond "not_testable" when resolution_status == "resolved"
    # (a diagnostic-only or insufficient tier cannot speak to the model's
    # physics, only to code-path correctness), and it can never claim a
    # candidate finding for a run that did not run the candidate operator
    # (group != "C").
    if resolution_status != "resolved":
        scientific_status = "not_testable"
    elif forcing_overlaps_terminal_layer:
        scientific_status = "assumption_challenged"
    elif group == "C" and weak_forcing_case and weak_forcing_matches_baseline:
        scientific_status = "candidate_limit_consistency_observed"
    elif group == "C":
        scientific_status = "candidate_improvement_not_testable"
    else:
        scientific_status = "synthetic_run_valid"

    return AuditedStatus(pipeline_status, resolution_status, energy_budget_status, forcing_regime_status, scientific_status, spectral_status)


def classify_stress_test_run(
    domain: RunDomain,
    *,
    pipeline_ok: bool,
    resolution_ok: bool,
    material_implemented: bool,
    energy_budget_closes: bool,
    pile_up_detected: bool,
    controller_is_stable: bool,
    weak_forcing_case: bool,
    weak_forcing_matches_baseline: bool | None,
    forcing_overlaps_terminal_layer: bool,
    anisotropy_significant: bool,
    size_effect_significant: bool,
) -> StressTestClassification:
    """Builds the (possibly multi-label) classification for one (forcing
    case, material, grid_n) run. This is NOT a single ladder -- several
    labels can and usually do apply simultaneously (e.g. a run can be both
    `energy_budget_valid` and `anisotropic_response_identified`)."""
    labels: list[str] = []
    notes: list[str] = []

    if not material_implemented:
        return StressTestClassification(domain=domain, labels=("material_interface_only",), notes=("material not implemented by this milestone's solver",))

    if not pipeline_ok:
        return StressTestClassification(domain=domain, labels=("blocked",), notes=("pipeline failed before any physical result could be computed",))

    if not resolution_ok:
        labels.append("insufficient_resolution")
        notes.append("terminal layer does not meet min_terminal_shells/min_populated_terminal_shells at this grid_n")

    labels.append("pipeline_only")

    if energy_budget_closes:
        labels.append("energy_budget_valid")
    if pile_up_detected:
        notes.append("unresolved energy pile-up detected above cutoff")

    labels.append("controller_stable" if controller_is_stable else "controller_unstable")

    if weak_forcing_case:
        if weak_forcing_matches_baseline:
            labels.append("weak_forcing_consistent")
        elif weak_forcing_matches_baseline is False:
            labels.append("forcing_sensitive")
            notes.append("weak-forcing case did not reduce to the original-model baseline within tolerance")
    else:
        labels.append("forcing_sensitive")

    if forcing_overlaps_terminal_layer:
        labels.append("forcing_overlap_invalidates_assumption")
        notes.append("forcing injects energy at or above k_s; original cascade-arrival assumption directly challenged (H3)")

    if anisotropy_significant:
        labels.append("anisotropic_response_identified")
    if size_effect_significant:
        labels.append("size_effect_identified")

    # Overall in-domain verdict, only meaningful together with `domain`.
    if not resolution_ok:
        pass  # insufficient_resolution already recorded; no supported/not-supported verdict
    elif forcing_overlaps_terminal_layer and not energy_budget_closes:
        labels.append("terminal_model_not_supported")
    elif forcing_overlaps_terminal_layer or (anisotropy_significant and not weak_forcing_case):
        labels.append("terminal_model_requires_extension")
    elif energy_budget_closes and controller_is_stable and not pile_up_detected:
        labels.append("terminal_model_supported_in_domain")
    else:
        labels.append("terminal_model_requires_extension")

    return StressTestClassification(domain=domain, labels=tuple(dict.fromkeys(labels)), notes=tuple(notes))
