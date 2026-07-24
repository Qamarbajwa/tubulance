"""
Physical-validation run classification
========================================

A shared vocabulary used by jhtdb_terminal_benchmark.py,
compare_model_to_dns.py, and nonlinear_transfer_validation.py so every
script reports run status the same way. Six classifications, treated as a
strict ladder (each rung requires everything below it) plus one failure
mode that sits outside the ladder:

    blocked                              -- pipeline itself failed (could
                                             not fetch/filter/FFT the data
                                             at all).
    pipeline_only                        -- pipeline ran, but the terminal
                                             layer failed resolution
                                             validation (see
                                             jhtdb_terminal_benchmark.
                                             validate_terminal_layer) so no
                                             physical claim can be made.
    apriori_operator_valid               -- resolution adequate; the
                                             single-snapshot a-priori
                                             operator test ran.
    finite_difference_comparison_valid   -- additionally, a confirmed-dt
                                             two-snapshot Edot_DNS vs
                                             Edot_model comparison ran.
    nonlinear_transfer_comparison_valid  -- additionally, the true
                                             nonlinear transfer T(k)/flux
                                             Pi(k) was computed (globally
                                             conservative within tolerance)
                                             and compared against the
                                             model's predicted removal.
    forward_validation_required          -- the nonlinear-transfer
                                             comparison additionally meets
                                             the "credible early result"
                                             bar (see README.md): this is
                                             the ceiling of what an
                                             a-priori-style comparison can
                                             show. It is NOT full
                                             validation -- that requires
                                             running the model forward in
                                             time and comparing evolved
                                             statistics over several
                                             turnover times, which is not
                                             implemented.

Do not classify a run as physically supportive merely because energy is
conserved or the cutoff is enforced -- those are necessary preconditions
checked at every rung, not evidence of the theory being correct.
"""

from __future__ import annotations

from dataclasses import dataclass

VALID_CLASSIFICATIONS = (
    "blocked",
    "pipeline_only",
    "apriori_operator_valid",
    "finite_difference_comparison_valid",
    "nonlinear_transfer_comparison_valid",
    "forward_validation_required",
)


@dataclass(frozen=True)
class RunStages:
    pipeline_ok: bool = False
    resolution_ok: bool = False
    apriori_operator_ok: bool = False
    finite_difference_ok: bool = False
    nonlinear_transfer_ok: bool = False
    nonlinear_transfer_meets_positive_result_bar: bool = False


def classify_run(stages: RunStages) -> str:
    if not stages.pipeline_ok:
        return "blocked"
    if not stages.resolution_ok or not stages.apriori_operator_ok:
        return "pipeline_only"
    if not stages.nonlinear_transfer_ok:
        if stages.finite_difference_ok:
            return "finite_difference_comparison_valid"
        return "apriori_operator_valid"
    if stages.nonlinear_transfer_meets_positive_result_bar:
        return "forward_validation_required"
    return "nonlinear_transfer_comparison_valid"


def positive_result_bar(
    *,
    n_t: float,
    min_terminal_shells: int,
    populated_terminal_shells: int,
    min_populated_terminal_shells: int,
    conservation_relative_residual: float,
    conservation_tolerance: float,
    energy_above_cutoff: float,
    transfer_correlation: float,
) -> tuple[bool, list[str]]:
    """The "first real positive result" bar from README.md / the 2026-07-24
    theory addition. All conditions must hold; returns (passes, reasons)
    where reasons lists which conditions failed.
    """
    reasons = []
    if n_t < min_terminal_shells:
        reasons.append(f"N_T={n_t:.2f} < required {min_terminal_shells}")
    if populated_terminal_shells < min_populated_terminal_shells:
        reasons.append(
            f"populated terminal shells={populated_terminal_shells} < required "
            f"{min_populated_terminal_shells}"
        )
    if conservation_relative_residual > conservation_tolerance:
        reasons.append(
            f"nonlinear-transfer conservation residual "
            f"{conservation_relative_residual:.3g} exceeds tolerance "
            f"{conservation_tolerance:.3g}"
        )
    if energy_above_cutoff > 0:
        reasons.append(f"energy above cutoff is {energy_above_cutoff:.3g}, expected 0")
    if not (transfer_correlation > 0):
        reasons.append(f"transfer correlation {transfer_correlation:.3g} is not > 0")
    return (len(reasons) == 0, reasons)
