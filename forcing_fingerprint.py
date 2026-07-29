"""
Forcing case fingerprinting and collision detection (Milestone 5.7a audit)
===============================================================================

Item 5 of the Milestone 5.7a audit: "if two preregistered cases produce
identical effective forcing, they cannot count as separate stress-test
conditions." This module computes a deterministic fingerprint of each
forcing case's RESOLVED configuration (after `forcing_test_matrix.
resolve_forcing_case` has turned symbolic k_f_mode/power/etc. into actual
numbers against a specific grid's terminal layer) and flags collisions.

Confirmed root causes from the original Milestone 5.7 campaign, both now
fixed and covered by tests here:

1. `moderate_steady_isotropic` and `forcing_far_below_ks` were literal
   duplicate case definitions (same forcing_type/power/k_f_mode/tau_f) --
   a genuine matrix-design bug, fixed in forcing_test_matrix.py by giving
   general-purpose cases their own `k_f_mode="moderate_below_ks"` distinct
   from the scale-separation test's `k_f_mode="far_below_ks"`.
2. At grid_n=32, `compute_terminal_layer` degenerates to `ks=0`, which
   collapses `k_f_mode="far_below_ks"` and `k_f_mode="near_ks"` onto the
   same resolved k_f (`max(0.3*0, delta_k) == max(0.9*0, delta_k)`) --
   this is a genuine resolution-driven collision, not a matrix bug, and is
   handled by excluding 32^3 from k_f/k_s-based applicability conclusions
   (see stress_test_classification.py's resolution_status field) rather
   than by trying to make 32^3 resolve distinct k_f values it structurally
   cannot.

This module only fingerprints the REQUESTED/resolved configuration (mask
center, bandwidth, type, direction, power, timescale). It does not hash the
full per-step applied spectral array or temporal waveform -- that level of
instrumentation is tracked separately via
`pseudo_spectral_solver.EnergyBudgetSample.forcing_requested_amplitude` /
`forcing_applied_amplitude` / `forcing_clip_active` and
`energy_budget.summarize_energy_budget`'s `forcing_clip_*` fields, which
answer "did the clip alter what was requested" for an executed run. This
module answers the earlier, cheaper question: "are these two cases even
asking for different forcing in the first place."
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from forcing import ForcingState
from forcing_test_matrix import ForcingTestCase, resolve_forcing_case
from jhtdb_terminal_benchmark import TerminalLayer

_ROUND_DIGITS = 6


def resolved_forcing_fingerprint(forcing: ForcingState) -> tuple:
    """A hashable tuple summarizing the physically-meaningful, resolved
    forcing configuration -- independent of anything RNG-seed-dependent
    (the actual random phases are never part of the fingerprint; two
    isotropic_random cases with the same k_f/bandwidth/power are
    considered the same forcing condition regardless of seed, which is the
    correct notion of "distinct stress-test condition")."""
    return (
        forcing.forcing_type,
        round(forcing.injection_wavenumber, _ROUND_DIGITS),
        tuple(round(k, _ROUND_DIGITS) for k in forcing.extra_wavenumbers),
        round(forcing.bandwidth, _ROUND_DIGITS),
        round(forcing.power_input, _ROUND_DIGITS),
        round(forcing.timescale, _ROUND_DIGITS),
        None if forcing.direction is None else tuple(round(d, _ROUND_DIGITS) for d in forcing.direction),
        round(forcing.spatial_coherence, _ROUND_DIGITS),
        round(forcing.temporal_coherence, _ROUND_DIGITS),
    )


def forcing_fingerprint_hash(forcing: ForcingState) -> str:
    return hashlib.sha256(repr(resolved_forcing_fingerprint(forcing)).encode()).hexdigest()[:16]


@dataclass(frozen=True)
class FingerprintCollision:
    fingerprint_hash: str
    case_names: tuple[str, ...]
    fingerprint: tuple


def detect_forcing_collisions(
    cases: list[ForcingTestCase], layer: TerminalLayer, nyquist: float, delta_k: float
) -> list[FingerprintCollision]:
    """Resolves every case against the given (grid-specific) terminal
    layer and returns every group of >=2 cases that collapse onto the
    same resolved fingerprint -- i.e. cases that CANNOT be treated as
    distinct stress-test conditions at this grid_n."""
    by_fp: dict[str, list[str]] = {}
    fp_by_hash: dict[str, tuple] = {}
    for case in cases:
        resolved = resolve_forcing_case(case, layer, nyquist, delta_k)
        fp = resolved_forcing_fingerprint(resolved)
        h = forcing_fingerprint_hash(resolved)
        by_fp.setdefault(h, []).append(case.name)
        fp_by_hash[h] = fp

    return [
        FingerprintCollision(fingerprint_hash=h, case_names=tuple(names), fingerprint=fp_by_hash[h])
        for h, names in by_fp.items()
        if len(names) >= 2
    ]


def assert_no_unexpected_collisions(
    cases: list[ForcingTestCase], layer: TerminalLayer, nyquist: float, delta_k: float, *, allowed_collisions: frozenset[frozenset[str]] = frozenset()
) -> list[FingerprintCollision]:
    """Raises if any collision is found whose case-name set is not in
    `allowed_collisions` (each entry a frozenset of case names that are
    KNOWN and DOCUMENTED to collide at this resolution -- e.g. the 32^3
    ks=0 degeneracy). Returns the full collision list (including allowed
    ones) for reporting."""
    collisions = detect_forcing_collisions(cases, layer, nyquist, delta_k)
    unexpected = [c for c in collisions if frozenset(c.case_names) not in allowed_collisions]
    if unexpected:
        details = "; ".join(f"{c.case_names} -> {c.fingerprint}" for c in unexpected)
        raise AssertionError(
            f"Unexpected forcing-case fingerprint collision(s) at this resolution: {details}. "
            "Two preregistered cases resolved to identical forcing and cannot be treated as "
            "separate stress-test conditions -- either fix the case definitions or add this "
            "collision to allowed_collisions with a documented reason."
        )
    return collisions
