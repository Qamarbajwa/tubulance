"""
Phase-map construction (Milestone 5.7)
===========================================

Builds the applicability-map axes requested by the specification:
Phi_l vs Theta_f, k_f/k_s vs forcing power, structure-size-over-terminal-
scale vs forcing dominance, Reynolds number vs forcing dominance, and
domain size vs terminal-shell population. Each point is one executed
(forcing case, material, grid_n) run; a point's region label comes
directly from that run's `stress_test_classification.StressTestClassification`
-- this module does not invent new physics, it only projects existing
per-run classifications onto 2D axes for inspection.

Region labels used on the maps (a restriction of the classification
vocabulary to the five spatial-map categories the spec asks for):

    original_model_valid        <- terminal_model_supported_in_domain
    original_model_marginal     <- energy_budget_valid but controller_unstable,
                                    or weak_forcing_consistent only marginally
    forcing_aware_model_required<- terminal_model_requires_extension
    unresolved                  <- insufficient_resolution
    physically_unsupported      <- terminal_model_not_supported / blocked
"""

from __future__ import annotations

from dataclasses import dataclass

from stress_test_classification import StressTestClassification

MAP_REGIONS = (
    "original_model_valid",
    "original_model_marginal",
    "forcing_aware_model_required",
    "unresolved",
    "physically_unsupported",
)


@dataclass(frozen=True)
class PhaseMapPoint:
    x: float
    y: float
    region: str
    run_domain: dict
    labels: tuple[str, ...]


def region_from_classification(c: StressTestClassification) -> str:
    labels = set(c.labels)
    if "blocked" in labels or "terminal_model_not_supported" in labels:
        return "physically_unsupported"
    if "insufficient_resolution" in labels or "material_interface_only" in labels:
        return "unresolved"
    if "terminal_model_requires_extension" in labels:
        return "forcing_aware_model_required"
    if "terminal_model_supported_in_domain" in labels:
        if "controller_unstable" in labels:
            return "original_model_marginal"
        return "original_model_valid"
    return "original_model_marginal"


def build_phase_map(points: list[dict], *, x_key: str, y_key: str) -> list[PhaseMapPoint]:
    """points: list of dicts each containing x_key, y_key, and a
    'classification' StressTestClassification instance."""
    out = []
    for p in points:
        c: StressTestClassification = p["classification"]
        out.append(
            PhaseMapPoint(
                x=float(p[x_key]),
                y=float(p[y_key]),
                region=region_from_classification(c),
                run_domain={
                    "forcing_case": c.domain.forcing_case,
                    "material": c.domain.material,
                    "grid_n": c.domain.grid_n,
                },
                labels=c.labels,
            )
        )
    return out


def phi_theta_map(points: list[dict]) -> list[PhaseMapPoint]:
    return build_phase_map(points, x_key="phi_l", y_key="theta_f")


def kf_ks_vs_power_map(points: list[dict]) -> list[PhaseMapPoint]:
    return build_phase_map(points, x_key="k_f_over_ks", y_key="power_input")


def structure_scale_vs_dominance_map(points: list[dict]) -> list[PhaseMapPoint]:
    return build_phase_map(points, x_key="l_over_lc", y_key="phi_l")


def reynolds_vs_dominance_map(points: list[dict]) -> list[PhaseMapPoint]:
    return build_phase_map(points, x_key="reynolds_number", y_key="phi_l")


def size_vs_terminal_population_map(points: list[dict]) -> list[PhaseMapPoint]:
    return build_phase_map(points, x_key="grid_n", y_key="populated_terminal_shells")


def summarize_regions(points: list[PhaseMapPoint]) -> dict:
    counts = {region: 0 for region in MAP_REGIONS}
    for p in points:
        counts[p.region] += 1
    return counts
