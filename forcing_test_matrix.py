"""
Preregistered forcing test matrix (Milestone 5.7)
======================================================

Fixed here, before running against the stress-test grid, so a later "best
case" cannot be mistaken for a physical discovery -- same preregistration
discipline as backscatter_placement.py's four placement strategies.

Implements the >=14-case matrix required by the Milestone 5.7 specification
(the lettered A-J table plus the k_f/k_s and multi-scale cases from the
"Required forcing regimes" / implementation-prompt lists), split into a
`CALIBRATION_CASES` set (weak isotropic, moderate steady isotropic, one
directional case) and a disjoint `VALIDATION_CASES` set (unseen magnitudes,
unseen timescales, unseen injection scales, a terminal-overlap case, a
pulsed case, and a directional case distinct from the calibration one).
`assert_case_separation()` enforces the disjointness structurally, the same
way `jhtdb_terminal_benchmark.assert_snapshot_separation` does for real
snapshots.

Numeric presets (power levels, timescales, bandwidths) are fixed constants
chosen to be reasonable relative to this solver's dimensionless setup (see
pseudo_spectral_solver.py smoke behavior), not tuned to any run's outcome.
k_f positions are resolved at build time against the *actual* terminal
layer of the grid/config being tested (`resolve_forcing_case`), since ks/kc
depend on grid_n -- a fixed absolute k_f would mean something different at
every resolution.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from forcing import ForcingState
from jhtdb_terminal_benchmark import TerminalLayer

# Preregistered power-level presets (absolute units, dimensionless solver).
POWER_WEAK = 0.0025
POWER_MODERATE = 0.05
POWER_STRONG = 1.0

# Preregistered timescale presets.
TAU_SLOW = 5.0
TAU_MODERATE = 1.0
TAU_RAPID = 0.1

DEFAULT_DIRECTION_A = (1.0, 0.0, 0.0)
DEFAULT_DIRECTION_B = (0.0, 1.0, 1.0)


@dataclass(frozen=True)
class ForcingTestCase:
    name: str
    letter: str  # matches the A-J table where applicable, else ""
    description: str
    expected_response: str
    forcing_type: str
    power: float
    k_f_mode: str  # "moderate_below_ks" | "far_below_ks" | "near_ks" | "overlap_terminal" | "above_kc_small_scale" | "multi_scale" | "fixed_absolute"
    k_f_absolute: float | None = None  # only for k_f_mode == "fixed_absolute"
    tau_f: float = TAU_MODERATE
    direction: tuple[float, float, float] | None = None
    spatial_coherence: float = 1.0
    temporal_coherence: float = 1.0
    bandwidth_mode: str = "narrow"  # "narrow" | "broad"
    split: str = "validation"  # "calibration" | "validation"


def _bandwidth(mode: str, delta_k: float) -> float:
    return 2.0 * delta_k if mode == "narrow" else 8.0 * delta_k


def resolve_k_f(mode: str, layer: TerminalLayer, nyquist: float, absolute: float | None = None) -> tuple[float, tuple[float, ...]]:
    """Returns (primary_k_f, extra_wavenumbers) resolved against the actual
    terminal layer for this grid/config."""
    if mode == "fixed_absolute":
        if absolute is None:
            raise ValueError("k_f_mode='fixed_absolute' requires k_f_absolute")
        return absolute, ()
    ks = max(layer.ks, layer.delta_k)
    if mode == "moderate_below_ks":
        return max(0.6 * ks, layer.delta_k), ()
    if mode == "far_below_ks":
        return max(0.3 * ks, layer.delta_k), ()
    if mode == "near_ks":
        return max(0.9 * ks, layer.delta_k), ()
    if mode == "overlap_terminal":
        return 0.5 * (layer.ks + layer.kc), ()
    if mode == "above_kc_small_scale":
        return min(1.2 * layer.kc, 0.85 * nyquist), ()
    if mode == "multi_scale":
        k1 = max(0.3 * ks, layer.delta_k)
        k2 = max(0.9 * ks, layer.delta_k)
        k3 = min(1.1 * layer.kc, 0.85 * nyquist)
        return k1, (k2, k3)
    raise ValueError(f"unknown k_f_mode {mode!r}")


def resolve_forcing_case(case: ForcingTestCase, layer: TerminalLayer, nyquist: float, delta_k: float) -> ForcingState:
    k_f, extra = resolve_k_f(case.k_f_mode, layer, nyquist, case.k_f_absolute)
    return ForcingState(
        power_input=case.power,
        injection_wavenumber=k_f,
        timescale=case.tau_f,
        direction=case.direction,
        spatial_coherence=case.spatial_coherence,
        temporal_coherence=case.temporal_coherence,
        bandwidth=_bandwidth(case.bandwidth_mode, delta_k),
        forcing_type=case.forcing_type,
        extra_wavenumbers=extra,
    )


# --- Calibration set (3 cases) ----------------------------------------------

CALIBRATION_CASES: tuple[ForcingTestCase, ...] = (
    ForcingTestCase(
        name="weak_isotropic", letter="A",
        description="weak isotropic forcing",
        expected_response="natural decay or weak cascade",
        forcing_type="isotropic_random", power=POWER_WEAK, k_f_mode="moderate_below_ks",
        tau_f=TAU_MODERATE, split="calibration",
    ),
    ForcingTestCase(
        name="moderate_steady_isotropic", letter="B",
        description="steady isotropic forcing",
        expected_response="conventional forced turbulence",
        forcing_type="isotropic_random", power=POWER_MODERATE, k_f_mode="moderate_below_ks",
        tau_f=TAU_MODERATE, split="calibration",
    ),
    ForcingTestCase(
        name="strong_directional_fixed", letter="D",
        description="strong directional forcing (fixed direction)",
        expected_response="anisotropic structures",
        forcing_type="fixed_direction", power=POWER_STRONG, k_f_mode="moderate_below_ks",
        tau_f=TAU_MODERATE, direction=DEFAULT_DIRECTION_A, spatial_coherence=1.0, split="calibration",
    ),
)

# --- Validation set (11 cases, disjoint from calibration) -------------------
#
# NOTE (Milestone 5.7a audit): all "general-purpose" cases below use
# k_f_mode="moderate_below_ks" (0.6*ks), reserving "far_below_ks" (0.3*ks)
# exclusively for the `forcing_far_below_ks` case, which specifically tests
# the scale-separation hypothesis (H3's "k_f << k_s" comparison point).
# Before this fix, `moderate_steady_isotropic` and `forcing_far_below_ks`
# were literal duplicate configurations (identical type/power/k_f_mode/
# tau_f) -- confirmed as the root cause of their identical measured
# diagnostics in the original Milestone 5.7 run, not a resolution artifact.
# See forcing_fingerprint.py for the collision check that would now catch
# a regression of this kind automatically.

VALIDATION_CASES: tuple[ForcingTestCase, ...] = (
    ForcingTestCase(
        name="strong_isotropic", letter="C",
        description="strong isotropic forcing",
        expected_response="intensified cascade",
        forcing_type="isotropic_random", power=POWER_STRONG, k_f_mode="moderate_below_ks",
        tau_f=TAU_MODERATE, split="validation",
    ),
    ForcingTestCase(
        name="rotating_directional", letter="",
        description="rotating forcing",
        expected_response="anisotropic structures with time-varying axis; synchronization/resonance possible",
        forcing_type="rotating_direction", power=POWER_STRONG, k_f_mode="moderate_below_ks",
        tau_f=TAU_SLOW, direction=DEFAULT_DIRECTION_B, spatial_coherence=1.0, split="validation",
    ),
    ForcingTestCase(
        name="slow_periodic", letter="F",
        description="slow coherent (periodic) forcing",
        expected_response="gradual organization",
        forcing_type="periodic", power=POWER_MODERATE, k_f_mode="moderate_below_ks",
        tau_f=TAU_SLOW, split="validation",
    ),
    ForcingTestCase(
        name="rapid_pulsed", letter="E",
        description="rapid pulsed forcing",
        expected_response="transient destruction/reformation",
        forcing_type="periodic", power=POWER_MODERATE, k_f_mode="moderate_below_ks",
        tau_f=TAU_RAPID, split="validation",
    ),
    ForcingTestCase(
        name="pulsed", letter="",
        description="pulsed forcing (square on/off)",
        expected_response="transient destruction/reformation",
        forcing_type="pulsed", power=POWER_MODERATE, k_f_mode="moderate_below_ks",
        tau_f=TAU_MODERATE, split="validation",
    ),
    ForcingTestCase(
        name="impulsive", letter="",
        description="impulsive (short kick) forcing",
        expected_response="transient destruction/reformation, strongest overshoot",
        forcing_type="impulsive", power=POWER_STRONG, k_f_mode="moderate_below_ks",
        tau_f=TAU_MODERATE, split="validation",
    ),
    ForcingTestCase(
        name="forcing_far_below_ks", letter="",
        description="forcing far below k_s",
        expected_response="model assumptions should hold (cascade-dominated arrival at terminal layer)",
        forcing_type="isotropic_random", power=POWER_MODERATE, k_f_mode="far_below_ks",
        tau_f=TAU_MODERATE, split="validation",
    ),
    ForcingTestCase(
        name="forcing_near_ks", letter="H",
        description="forcing near k_s",
        expected_response="direct interaction with terminal layer",
        forcing_type="narrow_band", power=POWER_MODERATE, k_f_mode="near_ks",
        tau_f=TAU_MODERATE, bandwidth_mode="narrow", split="validation",
    ),
    ForcingTestCase(
        name="forcing_overlap_terminal_layer", letter="I",
        description="forcing inside the terminal layer",
        expected_response="original assumptions challenged",
        forcing_type="narrow_band", power=POWER_MODERATE, k_f_mode="overlap_terminal",
        tau_f=TAU_MODERATE, bandwidth_mode="narrow", split="validation",
    ),
    ForcingTestCase(
        name="small_scale_forcing", letter="G",
        description="small-scale forcing above k_c",
        expected_response="possible inverse or bidirectional transfer",
        forcing_type="small_scale", power=POWER_MODERATE, k_f_mode="above_kc_small_scale",
        tau_f=TAU_MODERATE, bandwidth_mode="narrow", split="validation",
    ),
    ForcingTestCase(
        name="multi_scale_forcing", letter="",
        description="multi-scale forcing (simultaneous injection across scales)",
        expected_response="superposed cascade + direct-injection response",
        forcing_type="multi_scale", power=POWER_MODERATE, k_f_mode="multi_scale",
        tau_f=TAU_MODERATE, bandwidth_mode="narrow", split="validation",
    ),
)

# "oscillating forcing / synchronization or resonance" (case J) is covered by
# rotating_directional and slow_periodic above (both are the periodic-type
# forcing this repo implements); no separate case object is needed.

ALL_CASES: tuple[ForcingTestCase, ...] = CALIBRATION_CASES + VALIDATION_CASES


class CaseSeparationError(RuntimeError):
    pass


def assert_case_separation() -> None:
    cal_names = {c.name for c in CALIBRATION_CASES}
    val_names = {c.name for c in VALIDATION_CASES}
    overlap = cal_names & val_names
    if overlap:
        raise CaseSeparationError(f"forcing case(s) {sorted(overlap)} appear in both calibration and validation sets")


TEMPORAL_FORCING_TYPES = frozenset({"periodic", "pulsed", "impulsive", "rotating_direction"})


def min_steps_for_forcing_case(case: ForcingTestCase, dt: float, *, min_periods: float = 2.0) -> int:
    """Milestone 5.7a audit fix: a temporally-varying forcing case
    (periodic/pulsed/impulsive/rotating_direction) must be run for at least
    `min_periods` full `tau_f` cycles, or its envelope never actually
    varies within the run and it is numerically indistinguishable from
    steady forcing. Confirmed root cause: the original Milestone 5.7
    campaign ran `pulsed` (tau_f=1.0) for only 40 steps at dt=0.008 (total
    simulated time 0.32 < tau_f/2), so its on/off envelope stayed 'on' for
    the entire run. Returns the minimum step count for a case with a
    steady/non-periodic forcing_type unchanged (no periodicity requirement)."""
    if case.forcing_type not in TEMPORAL_FORCING_TYPES:
        return 1
    return int(np.ceil(min_periods * case.tau_f / dt))


def cases_by_split(split: str) -> tuple[ForcingTestCase, ...]:
    assert_case_separation()
    if split == "calibration":
        return CALIBRATION_CASES
    if split == "validation":
        return VALIDATION_CASES
    if split == "all":
        return ALL_CASES
    raise ValueError(f"unknown split {split!r}")
