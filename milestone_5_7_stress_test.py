"""
Milestone 5.7: Forcing-Material-Size Stress Test of the Terminal-Layer Model
================================================================================

Orchestrates the synthetic pseudo-spectral stress test described in the
Milestone 5.7 specification: runs the preregistered forcing test matrix
(forcing_test_matrix.py) across materials (material_state.py) and grid
sizes, under six comparison groups (A-F below), classifies every run
(stress_test_classification.py), and aggregates the results into the
applicability map

    D_valid = {M, Re, Phi, Theta_f, k_f/k_s, l/L, l/lc}

This module never touches the real JHTDB campaign (jhtdb_terminal_
benchmark.py, run_real_validation.py, manifests/) -- it is a fully separate
synthetic/theoretical framework, as the specification requires. Every
result this module produces is synthetic-only; see stress_test_report.py
for the mandatory data-provenance warning threaded through every report.

Comparison groups
------------------
  A  original_fixed_gains          baseline operator, controller with the
                                    preregistered fixed gains (GP=24, GI=8)
  B  original_retuned_calibration  baseline operator, controller gains
                                    retuned (see tune_controller_gains) using
                                    ONLY the calibration forcing cases
  C  forcing_aware_candidate       candidate operator (terminal_operator_
                                    forcing_aware.gamma_candidate_forcing_aware)
  D  no_terminal_operator          apply_terminal_operator=False
  E  hard_cutoff                   hard spectral truncation at kc, no smooth
                                    damping, no heat/return split
  F  smooth_damping_no_backscatter alpha_s=1.0 (all heat, no return) --
                                    "ordinary smooth spectral damping"

Resolution note: at grid_n=32 with this solver's default cutoff_fraction
(kc = 0.5*Nyquist) and beta=0.56, `compute_terminal_layer` falls back to
`ks=0` (not enough shells for the beta-derived layer) -- and `estimate_tau_s`
is undefined at ks=0 (the entry-shell energy is exactly zero, since the k=0
mode is removed by the divergence-free projection), which silently zeros
`gamma` everywhere. This is exactly why the specification requires 32^3 be
treated as diagnostic-only: `resolution_ok` below additionally requires
`layer.ks > 0`, on top of the base repo's `validate_terminal_layer` shell-
count checks, specifically because of this degeneracy.
"""

from __future__ import annotations

from dataclasses import dataclass, replace, field
import hashlib
import itertools
import json
import numpy as np

from jhtdb_terminal_benchmark import (
    wavenumbers, compute_terminal_layer, validate_terminal_layer, shell_spectrum,
    Config as TerminalConfig, kinetic_energy_hat,
)
from forcing import (
    ForcingState, forcing_dominance_ratio, classify_forcing_regime, forcing_timescale_ratio,
    classify_timescale_regime, eddy_turnover_time, DEFAULT_THRESHOLDS,
)
from material_state import MaterialState, get_material, classify_material_support
from pseudo_spectral_solver import SolverConfig, run_solver
from controller import ControllerConfig, controller_diagnostics, classify_controller_run, DEFAULT_GP, DEFAULT_GI
from energy_budget import summarize_energy_budget, detect_terminal_pile_up
from structure_metrics import (
    anisotropy_tensor, anisotropy_invariants, isotropic_control_baseline, is_anisotropic_response_significant,
    IsotropicControlBaseline,
)
from forcing_test_matrix import (
    ForcingTestCase, resolve_forcing_case, CALIBRATION_CASES, VALIDATION_CASES, assert_case_separation,
    min_steps_for_forcing_case,
)
from stress_test_classification import (
    RunDomain, classify_stress_test_run, StressTestClassification, AuditedStatus, compute_audited_status,
)

# Bumped whenever the solver's numerics, energy-budget definition, or
# forcing-generation scheme changes in a way that would make an old run_id
# not comparable to a new one -- part of the deterministic run identity
# (Milestone 5.7a audit item 6).
SOLVER_VERSION = "5.7a-2026-07-29"

COMPARISON_GROUPS = ("A", "B", "C", "D", "E", "F")

GROUP_DESCRIPTIONS = {
    "A": "original_fixed_gains -- baseline terminal operator, controller with preregistered fixed gains (GP=24, GI=8)",
    "B": "original_retuned_calibration -- baseline operator, controller gains retuned on calibration cases only",
    "C": "forcing_aware_candidate -- CANDIDATE gamma modification (terminal_operator_forcing_aware), not validated",
    "D": "no_terminal_operator -- terminal operator disabled entirely",
    "E": "hard_cutoff -- hard spectral truncation at kc, no smooth damping",
    "F": "smooth_damping_no_backscatter -- smooth gamma(k), alpha_s=1.0 (all heat, no return)",
}

# Preregistered gain-tuning grid for group B -- fixed before running, per the
# same preregistration discipline as backscatter_placement.py's strategies.
GAIN_TUNING_GRID = ((DEFAULT_GP, DEFAULT_GI), (12.0, 4.0), (48.0, 16.0), (24.0, 16.0), (12.0, 8.0))

# 32^3 is diagnostic-only per the specification; 64^3 is the minimum tier a
# physical claim may be based on; 128^3 is included in the tier list but is
# not executed by default (compute-limited in this environment -- reported
# as status="no_data", never fabricated, same convention as
# convergence_table.py's ResolutionSpec.fetch=None).
GRID_TIERS_DEFAULT = (32, 64)
GRID_TIER_DIAGNOSTIC_ONLY = frozenset({32})
GRID_TIER_COMPUTE_LIMITED = frozenset({128})

DEFAULT_DOMAIN_LENGTH = 2.0 * np.pi
DEFAULT_VISCOSITY = 0.02
DEFAULT_N_STEPS = 60
DEFAULT_DT = 0.008


def compute_run_identity(
    *, case_name: str, split: str, material_name: str, grid_n: int, domain_length: float, viscosity: float,
    group: str, controller_gains: tuple[float, float], seed: int, forcing: ForcingState | None,
    solver_version: str = SOLVER_VERSION,
) -> str:
    """Milestone 5.7a audit item 6: a deterministic run identity from every
    field that can change a run's outcome. Two runs with the same identity
    MUST have produced the same result (given the same code); a shard
    aggregator can therefore safely deduplicate on this key, and a
    mismatch between `n_runs_expected` (unique identities requested) and
    `n_runs_observed` (unique identities actually present) is a real,
    checkable discrepancy instead of an eyeballed guess.

    Deliberately does NOT include the resolved forcing's random phases
    (RNG state during stepping) -- `seed` already captures that
    determinism; this identity is about WHICH condition was run, not the
    literal bytes of one run's noise realization."""
    payload = {
        "solver_version": solver_version,
        "case_name": case_name,
        "split": split,
        "material": material_name,
        "grid_n": grid_n,
        "domain_length": domain_length,
        "viscosity": viscosity,
        "comparison_group": group,
        "controller_gains": list(controller_gains),
        "seed": seed,
        "forcing": None
        if forcing is None
        else {
            "type": forcing.forcing_type,
            "power_input": forcing.power_input,
            "injection_wavenumber": forcing.injection_wavenumber,
            "extra_wavenumbers": list(forcing.extra_wavenumbers),
            "timescale": forcing.timescale,
            "bandwidth": forcing.bandwidth,
            "direction": None if forcing.direction is None else list(forcing.direction),
            "spatial_coherence": forcing.spatial_coherence,
            "temporal_coherence": forcing.temporal_coherence,
        },
    }
    blob = json.dumps(payload, sort_keys=True, default=float)
    return hashlib.sha256(blob.encode()).hexdigest()[:24]


def _group_solver_kwargs(group: str, *, gains: tuple[float, float]) -> dict:
    gp, gi = gains
    if group == "A":
        return dict(use_controller=True, controller=ControllerConfig(gp=DEFAULT_GP, gi=DEFAULT_GI), terminal_gamma_mode="baseline")
    if group == "B":
        return dict(use_controller=True, controller=ControllerConfig(gp=gp, gi=gi), terminal_gamma_mode="baseline")
    if group == "C":
        return dict(use_controller=True, controller=ControllerConfig(gp=DEFAULT_GP, gi=DEFAULT_GI), terminal_gamma_mode="candidate_forcing_aware")
    if group == "D":
        return dict(apply_terminal_operator=False, use_controller=False, c_gamma_fixed=0.0)
    if group == "E":
        return dict(apply_terminal_operator=False, hard_cutoff=True, use_controller=False, c_gamma_fixed=0.0)
    if group == "F":
        return dict(use_controller=True, controller=ControllerConfig(gp=DEFAULT_GP, gi=DEFAULT_GI), terminal_gamma_mode="baseline", alpha_s=1.0)
    raise ValueError(f"unknown comparison group {group!r}")


def _base_solver_config(
    case: ForcingTestCase, material: MaterialState, grid_n: int, *, domain_length: float, viscosity: float, dt: float, seed: int
) -> tuple[SolverConfig, object]:
    kx, ky, kz = wavenumbers(grid_n, domain_length)
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    nyquist = float(np.max(np.abs(kx[:, 0, 0])))
    delta_k = 2.0 * np.pi / domain_length
    kc = 0.5 * nyquist
    layer = compute_terminal_layer(kc, delta_k, TerminalConfig())
    forcing = resolve_forcing_case(case, layer, nyquist, delta_k)
    cfg = SolverConfig(
        grid_n=grid_n, domain_length=domain_length, viscosity=viscosity, forcing=forcing, material=material, dt=dt, seed=seed,
    )
    return cfg, layer


def tune_controller_gains(
    material: MaterialState, grid_n: int, *, domain_length: float, viscosity: float, dt: float, n_steps: int, seed: int
) -> tuple[float, float]:
    """Group B: pick (gp, gi) from GAIN_TUNING_GRID using ONLY the
    calibration forcing cases, scored by controller overshoot + oscillation
    amplitude (lower is better) -- a simple, preregistered, symmetric score.
    Never uses a validation case; see forcing_test_matrix.py for the
    calibration/validation split this depends on."""
    assert_case_separation()
    best = None
    best_score = float("inf")
    for gp, gi in GAIN_TUNING_GRID:
        total_score = 0.0
        for case in CALIBRATION_CASES:
            cfg, _layer = _base_solver_config(case, material, grid_n, domain_length=domain_length, viscosity=viscosity, dt=dt, seed=seed)
            cfg = replace(cfg, use_controller=True, controller=ControllerConfig(gp=gp, gi=gi))
            _state, samples, _layer2 = run_solver(cfg, n_steps)
            diag = controller_diagnostics(_state.controller_state)
            overshoot = diag["overshoot"] or 0.0
            osc = diag["oscillation_amplitude"] or 0.0
            total_score += overshoot + osc
        if total_score < best_score:
            best_score = total_score
            best = (gp, gi)
    return best


@dataclass(frozen=True)
class StressTestRunResult:
    run_id: str
    case_name: str
    forcing_type: str
    split: str
    material_name: str
    grid_n: int
    group: str
    domain: RunDomain
    phi_l: float
    theta_f: float
    k_f_over_ks: float
    l_over_L: float
    l_over_lc: float
    reynolds_number: float
    energy_budget: dict
    controller: dict
    controller_labels: tuple[str, ...]
    classification: StressTestClassification
    audited_status: AuditedStatus
    component_energies: dict
    is_diagnostic_tier: bool
    pipeline_ok: bool
    resolution_ok: bool
    populated_terminal_shells: int


def _blocked_result(case, material_name, grid_n, group, *, run_id, reason_labels, material_implemented, pipeline_ok, extra_energy_budget=None) -> StressTestRunResult:
    domain = RunDomain(
        forcing_case=case.name, material=material_name, grid_n=grid_n, forcing_type=case.forcing_type,
        phi_l_regime="undefined", theta_f_regime="undefined", k_f_vs_ks="undefined",
    )
    classification = classify_stress_test_run(
        domain, pipeline_ok=pipeline_ok, resolution_ok=False, material_implemented=material_implemented,
        energy_budget_closes=False, pile_up_detected=False, controller_is_stable=False,
        weak_forcing_case=False, weak_forcing_matches_baseline=None,
        forcing_overlaps_terminal_layer=False, anisotropy_significant=False, size_effect_significant=False,
    )
    audited = compute_audited_status(
        pipeline_ok=pipeline_ok, material_implemented=material_implemented, resolution_ok=False,
        is_diagnostic_tier=False, energy_budget_closes=False, energy_budget_partial=False,
        forcing_clip_materially_altered=False, forcing_overlaps_terminal_layer=False,
        weak_forcing_case=False, weak_forcing_matches_baseline=None, group=group,
    )
    return StressTestRunResult(
        run_id=run_id, case_name=case.name, forcing_type=case.forcing_type, split=case.split,
        material_name=material_name, grid_n=grid_n, group=group, domain=domain, phi_l=float("nan"),
        theta_f=float("nan"), k_f_over_ks=float("nan"), l_over_L=float("nan"), l_over_lc=float("nan"),
        reynolds_number=float("nan"), energy_budget=extra_energy_budget or {}, controller={}, controller_labels=(),
        classification=classification, audited_status=audited, component_energies={}, is_diagnostic_tier=False,
        pipeline_ok=pipeline_ok, resolution_ok=False, populated_terminal_shells=0,
    )


def run_one(
    case: ForcingTestCase, material_name: str, grid_n: int, group: str, *,
    domain_length: float = DEFAULT_DOMAIN_LENGTH, viscosity: float = DEFAULT_VISCOSITY,
    n_steps: int | None = DEFAULT_N_STEPS, dt: float = DEFAULT_DT, seed: int = 0,
    tuned_gains: tuple[float, float] | None = None, initial_kinetic_energy: float | None = None,
    min_periods_for_temporal_forcing: float = 2.0,
) -> StressTestRunResult:
    """`n_steps=None` auto-selects enough steps to span at least
    `min_periods_for_temporal_forcing` full `tau_f` cycles for temporally-
    varying forcing types (periodic/pulsed/impulsive/rotating_direction) --
    see forcing_test_matrix.min_steps_for_forcing_case and the Milestone
    5.7a audit's confirmed root cause for why the original campaign's
    `pulsed` case never actually pulsed."""
    material = get_material(material_name)
    gains = tuned_gains or (DEFAULT_GP, DEFAULT_GI)
    run_id = compute_run_identity(
        case_name=case.name, split=case.split, material_name=material_name, grid_n=grid_n,
        domain_length=domain_length, viscosity=viscosity, group=group, controller_gains=gains, seed=seed,
        forcing=None,
    )
    if not material.implemented:
        return _blocked_result(case, material_name, grid_n, group, run_id=run_id, reason_labels=(), material_implemented=False, pipeline_ok=False)

    if n_steps is None:
        n_steps = max(DEFAULT_N_STEPS, min_steps_for_forcing_case(case, dt, min_periods=min_periods_for_temporal_forcing))

    cfg, layer = _base_solver_config(case, material, grid_n, domain_length=domain_length, viscosity=viscosity, dt=dt, seed=seed)
    cfg = replace(cfg, **_group_solver_kwargs(group, gains=gains), initial_kinetic_energy=initial_kinetic_energy)
    run_id = compute_run_identity(
        case_name=case.name, split=case.split, material_name=material_name, grid_n=grid_n,
        domain_length=domain_length, viscosity=viscosity, group=group, controller_gains=gains, seed=seed,
        forcing=cfg.forcing,
    )

    try:
        state, samples, layer = run_solver(cfg, n_steps)
        pipeline_ok = True
    except Exception as exc:  # pipeline failure -- classify as blocked, don't crash the campaign
        return _blocked_result(
            case, material_name, grid_n, group, run_id=run_id, reason_labels=(), material_implemented=True,
            pipeline_ok=False, extra_energy_budget={"error": str(exc)},
        )

    is_diagnostic_tier = (grid_n in GRID_TIER_DIAGNOSTIC_ONLY) or (layer.ks <= 0)

    nyquist = float(np.max(np.abs(wavenumbers(grid_n, domain_length)[0][:, 0, 0])))
    shells, e_final = shell_spectrum(state.velocity_hat, np.sqrt(sum(w**2 for w in wavenumbers(grid_n, domain_length))))
    tcfg = cfg.to_terminal_config()
    resolution_failures = validate_terminal_layer(layer, nyquist, shells, e_final, tcfg)
    resolution_ok = (len(resolution_failures) == 0) and (layer.ks > 0)
    populated = int(np.sum(e_final[(shells >= layer.ks) & (shells <= layer.kc)] > tcfg.energy_floor))

    # Phi_l/Theta_f/Re are quasi-steady-state diagnostics -- averaging
    # kinetic energy over the second half of the run (rather than reading
    # only the final-step snapshot) avoids classifying a still-spinning-up
    # transient as if it were the run's actual regime. Even so, a cold
    # start (initial_kinetic_energy=None) can leave u_l too small for the
    # whole run for any forcing power to register as "weak" relative to it
    # -- see SolverConfig.initial_kinetic_energy docstring (Milestone 5.7a
    # audit item 2's root-cause fix).
    tail = samples[len(samples) // 2 :] if len(samples) >= 4 else samples
    ke_ref = float(np.mean([s.kinetic_energy for s in tail]))
    u_rms = float(np.sqrt(2.0 * ke_ref / 3.0)) if ke_ref > 0 else 1e-6
    ell_f = 2.0 * np.pi / cfg.forcing.injection_wavenumber
    tau_l = eddy_turnover_time(max(u_rms, 1e-6), ell_f)
    try:
        phi_l = forcing_dominance_ratio(cfg.forcing.power_input, max(u_rms, 1e-6), ell_f)
    except ValueError:
        phi_l = float("nan")
    theta_f = forcing_timescale_ratio(cfg.forcing.timescale, max(tau_l, 1e-9))
    reynolds_number = float(u_rms * ell_f / viscosity)
    k_f_over_ks = float(cfg.forcing.injection_wavenumber / layer.ks) if layer.ks > 0 else float("inf")
    l_over_L = float(ell_f / domain_length)
    l_over_lc = float(ell_f / (2.0 * np.pi / layer.kc)) if layer.kc > 0 else float("nan")

    if not np.isfinite(k_f_over_ks):
        k_f_vs_ks = "undefined"
    elif k_f_over_ks < 0.7:
        k_f_vs_ks = "below"
    elif k_f_over_ks <= 1.3:
        k_f_vs_ks = "near"
    else:
        k_f_vs_ks = "overlap_or_above"

    domain = RunDomain(
        forcing_case=case.name, material=material_name, grid_n=grid_n, forcing_type=case.forcing_type,
        phi_l_regime=classify_forcing_regime(phi_l, DEFAULT_THRESHOLDS) if np.isfinite(phi_l) else "undefined",
        theta_f_regime=classify_timescale_regime(theta_f) if np.isfinite(theta_f) else "undefined",
        k_f_vs_ks=k_f_vs_ks,
    )

    summary = summarize_energy_budget(samples, dt=cfg.dt)
    pile_up = detect_terminal_pile_up(samples)
    ctrl_diag = controller_diagnostics(state.controller_state)
    target_hist = tuple(s.power_input for s in samples)
    measured_hist = tuple(s.terminal_heat + s.return_power for s in samples)
    controller_labels = classify_controller_run(state.controller_state, target_history=target_hist, measured_history=measured_hist)

    u_real = np.fft.ifftn(state.velocity_hat, axes=(1, 2, 3)).real
    b = anisotropy_tensor(u_real)
    inv = anisotropy_invariants(b)
    anisotropy_significant = inv["anisotropy_magnitude"] > 0.02  # UNAUDITED single-run threshold -- see note below
    component_energies = {
        "Ex": float(0.5 * np.mean(u_real[0] ** 2)),
        "Ey": float(0.5 * np.mean(u_real[1] ** 2)),
        "Ez": float(0.5 * np.mean(u_real[2] ** 2)),
        "b_ij": b.tolist(),
        "anisotropy_invariants": inv,
    }
    # NOTE (Milestone 5.7a audit item 9): `anisotropy_significant` above is
    # still the single-run threshold from the original Milestone 5.7 run --
    # kept as the default so run_one() stays cheap for a full campaign
    # sweep. The audited, isotropic-control-ensemble version
    # (structure_metrics.is_anisotropic_response_significant) is applied
    # explicitly by the corrected minimal matrix
    # (run_minimal_corrected_matrix.py), which is the only context in
    # which `anisotropic_response_identified` should be treated as
    # evidence rather than an unaudited screen.

    weak_forcing_case = domain.phi_l_regime == "nonlinear_dominated"
    classification = classify_stress_test_run(
        domain, pipeline_ok=pipeline_ok, resolution_ok=resolution_ok, material_implemented=True,
        energy_budget_closes=summary.closes_within_tolerance, pile_up_detected=pile_up["pile_up_detected"],
        controller_is_stable=bool(ctrl_diag["is_stable"]) if cfg.use_controller else True,
        weak_forcing_case=weak_forcing_case, weak_forcing_matches_baseline=None,
        forcing_overlaps_terminal_layer=(k_f_vs_ks == "overlap_or_above"),
        anisotropy_significant=anisotropy_significant, size_effect_significant=False,
    )
    # "partial" energy-budget status: not within the strict closure
    # tolerance, but the residual rate is still smaller than the input
    # power itself (i.e. the budget is in the right ballpark, just not
    # tight) -- vs. "invalid", where the residual is comparable to or
    # exceeds power_input and something is actually wrong.
    energy_budget_partial = (not summary.closes_within_tolerance) and (summary.relative_closure_error < 1.0)
    # forcing_above_cutoff: this case's OWN forcing injects above k_c
    # (l_over_lc < 1), distinct from forcing overlapping [k_s, k_c] --
    # see stress_test_classification.SPECTRAL_STATUSES.
    forcing_above_cutoff = np.isfinite(l_over_lc) and l_over_lc < 1.0
    audited_status = compute_audited_status(
        pipeline_ok=pipeline_ok, material_implemented=True, resolution_ok=resolution_ok,
        is_diagnostic_tier=is_diagnostic_tier, energy_budget_closes=summary.closes_within_tolerance,
        energy_budget_partial=energy_budget_partial,
        forcing_clip_materially_altered=summary.forcing_clip_materially_altered_case,
        forcing_overlaps_terminal_layer=(k_f_vs_ks == "overlap_or_above"), weak_forcing_case=weak_forcing_case,
        weak_forcing_matches_baseline=None, group=group,
        forcing_above_cutoff=forcing_above_cutoff, pile_up_detected=pile_up["pile_up_detected"],
        monotonically_growing=pile_up["monotonically_growing"],
    )

    return StressTestRunResult(
        run_id=run_id, case_name=case.name, forcing_type=case.forcing_type, split=case.split,
        material_name=material_name, grid_n=grid_n, group=group, domain=domain, phi_l=phi_l, theta_f=theta_f,
        k_f_over_ks=k_f_over_ks, l_over_L=l_over_L, l_over_lc=l_over_lc, reynolds_number=reynolds_number,
        energy_budget=summary.__dict__ | {"pile_up": pile_up}, controller=ctrl_diag,
        controller_labels=controller_labels, classification=classification, audited_status=audited_status,
        component_energies=component_energies, is_diagnostic_tier=is_diagnostic_tier, pipeline_ok=pipeline_ok,
        resolution_ok=resolution_ok, populated_terminal_shells=populated,
    )


def run_isotropic_control_ensemble(
    case: ForcingTestCase, material_name: str, grid_n: int, group: str, *, seeds: tuple[int, ...],
    domain_length: float = DEFAULT_DOMAIN_LENGTH, viscosity: float = DEFAULT_VISCOSITY,
    n_steps: int | None = DEFAULT_N_STEPS, dt: float = DEFAULT_DT, tuned_gains: tuple[float, float] | None = None,
    initial_kinetic_energy: float | None = None,
) -> IsotropicControlBaseline:
    """Milestone 5.7a audit item 9: runs `case` with its forcing TYPE
    forced to isotropic_random (same power/k_f/bandwidth/tau_f otherwise)
    across multiple seeds, and returns the isotropic anisotropy_magnitude
    baseline (mean, std) that `structure_metrics.
    is_anisotropic_response_significant` compares an actual case against.
    Expensive (one full solver run per seed) -- used by the corrected
    minimal matrix, not by the general run_campaign() sweep."""
    from dataclasses import replace as _dc_replace

    iso_case = _dc_replace(case, forcing_type="isotropic_random", direction=None, spatial_coherence=1.0)
    magnitudes = []
    for seed in seeds:
        result = run_one(
            iso_case, material_name, grid_n, group, domain_length=domain_length, viscosity=viscosity,
            n_steps=n_steps, dt=dt, seed=seed, tuned_gains=tuned_gains, initial_kinetic_energy=initial_kinetic_energy,
        )
        inv = result.component_energies.get("anisotropy_invariants")
        if inv is not None:
            magnitudes.append(inv["anisotropy_magnitude"])
    return isotropic_control_baseline(magnitudes)


def run_campaign(
    *, cases: list[ForcingTestCase], materials: list[str], grid_ns: list[int], groups: list[str],
    n_steps: int = DEFAULT_N_STEPS, dt: float = DEFAULT_DT, viscosity: float = DEFAULT_VISCOSITY,
    domain_length: float = DEFAULT_DOMAIN_LENGTH, seed: int = 0,
) -> list[StressTestRunResult]:
    """Runs every (case, material, grid_n, group) combination. Group B first
    tunes its gains once per (material, grid_n) using only calibration
    cases, then reuses that tuning for every case in that (material, grid_n)
    -- consistent with 'retuned only on calibration cases', not per-case."""
    results: list[StressTestRunResult] = []
    tuned_cache: dict[tuple[str, int], tuple[float, float]] = {}
    for material_name in materials:
        material = get_material(material_name)
        for grid_n in grid_ns:
            if "B" in groups and material.implemented:
                key = (material_name, grid_n)
                if key not in tuned_cache:
                    tuned_cache[key] = tune_controller_gains(
                        material, grid_n, domain_length=domain_length, viscosity=viscosity, dt=dt, n_steps=max(n_steps // 2, 10), seed=seed
                    )
            for case in cases:
                for group in groups:
                    tuned = tuned_cache.get((material_name, grid_n)) if group == "B" else None
                    results.append(
                        run_one(
                            case, material_name, grid_n, group, domain_length=domain_length, viscosity=viscosity,
                            n_steps=n_steps, dt=dt, seed=seed, tuned_gains=tuned,
                        )
                    )
    return results


def applicability_map(results: list[StressTestRunResult]) -> dict:
    """D_valid = {M, Re, Phi, Theta_f, k_f/k_s, l/L, l/lc}: aggregates every
    executed run's classification into per-domain-axis breakdowns. Not a
    single verdict -- see stress_test_classification.py docstring."""
    by_material: dict[str, dict[str, int]] = {}
    by_phi_regime: dict[str, dict[str, int]] = {}
    by_theta_regime: dict[str, dict[str, int]] = {}
    by_k_f_vs_ks: dict[str, dict[str, int]] = {}
    by_grid_n: dict[int, dict[str, int]] = {}

    def _bump(bucket: dict, key, label):
        bucket.setdefault(key, {}).setdefault(label, 0)
        bucket[key][label] += 1

    for r in results:
        for label in r.classification.labels:
            _bump(by_material, r.material_name, label)
            _bump(by_phi_regime, r.domain.phi_l_regime, label)
            _bump(by_theta_regime, r.domain.theta_f_regime, label)
            _bump(by_k_f_vs_ks, r.domain.k_f_vs_ks, label)
            _bump(by_grid_n, r.grid_n, label)

    return {
        "n_runs": len(results),
        "by_material": by_material,
        "by_phi_l_regime": by_phi_regime,
        "by_theta_f_regime": by_theta_regime,
        "by_k_f_vs_ks": by_k_f_vs_ks,
        "by_grid_n": by_grid_n,
    }


def applicability_map_from_rows(rows: list[dict]) -> dict:
    """Same aggregation as applicability_map(), but operating on the plain
    dict rows produced by stress_test_report._result_to_dict() -- used when
    reassembling a campaign from JSON shards (run_milestone_5_7_chunk.py /
    assemble_milestone_5_7_report.py) rather than in-memory
    StressTestRunResult objects."""
    by_material: dict = {}
    by_phi_regime: dict = {}
    by_theta_regime: dict = {}
    by_k_f_vs_ks: dict = {}
    by_grid_n: dict = {}

    def _bump(bucket: dict, key, label):
        bucket.setdefault(key, {}).setdefault(label, 0)
        bucket[key][label] += 1

    for row in rows:
        for label in row["classification_labels"]:
            _bump(by_material, row["material"], label)
            _bump(by_phi_regime, row["phi_l_regime"], label)
            _bump(by_theta_regime, row["theta_f_regime"], label)
            _bump(by_k_f_vs_ks, row["k_f_vs_ks"], label)
            _bump(by_grid_n, row["grid_n"], label)

    return {
        "n_runs": len(rows),
        "by_material": by_material,
        "by_phi_l_regime": by_phi_regime,
        "by_theta_f_regime": by_theta_regime,
        "by_k_f_vs_ks": by_k_f_vs_ks,
        "by_grid_n": by_grid_n,
    }
