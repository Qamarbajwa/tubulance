/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import RiemannBlueprint.EuclidOppositeSideExclusion
import RiemannBlueprint.PrimeBinaryCompressionBooster
import RiemannBlueprint.MathlibPR_NymanBeurling

/-!
# Phase 1: Euclid Pinch & Epsilon-Squeeze to `_root_.RiemannHypothesis`

This module executes Phase 1 of `RH_CLAY_CONDITIONS_MASTER_PLAN.md`:
it proves directly in Lean 4 (zero `sorry`, strictly `[propext, Classical.choice, Quot.sound]`)
that Condition C1 (`∀ ε > 0, ∃ N, E_dir N < ε`), paired with the Cauchy-Schwarz Mellin
off-line zero floor, implies `_root_.RiemannHypothesis` via `EuclidOppositeSideExclusion`
and `riemannZeta_zero_strip_symm`, without needing uniformity in `γ₀ = s.im`.

`NO_RH_PROOF = TRUE`: Condition C1 (`E_dir N → 0` as `N → ∞`) remains an open
analytic problem; this module certifies the exact implication `C1 → RiemannHypothesis`.
-/

namespace RiemannBlueprint

/-- **Theorem 1 (Pointwise Energy Vanishing Excludes All Right-Half Off-Line Zeros):**
    If `E_dir N → 0` as `N → ∞` (`∀ ε > 0, ∃ N, E_dir N < ε`) and every critical-strip
    zero with `1/2 < s.re < 1` satisfies the Cauchy-Schwarz Mellin floor
    `(2 * s.re - 1) / (s.re^2 + s.im^2) ≤ E_dir N` for all `N`, then no such zero exists. -/
theorem no_offline_zero_of_energy_vanishing
    (E_dir : ℕ → ℝ)
    (h_vanish : ∀ ε : ℝ, 0 < ε → ∃ N : ℕ, E_dir N < ε)
    (h_floor : ∀ s : ℂ, riemannZeta s = 0 → 1 / 2 < s.re → s.re < 1 →
      ∀ N : ℕ, (2 * s.re - 1) / (s.re ^ 2 + s.im ^ 2) ≤ E_dir N) :
    ∀ s : ℂ, riemannZeta s = 0 → 1 / 2 < s.re → s.re < 1 → False := by
  intro s hz h_half h_one
  have h_num : 0 < 2 * s.re - 1 := by linarith
  have h_den : 0 < s.re ^ 2 + s.im ^ 2 := by positivity
  have h_eps : 0 < (2 * s.re - 1) / (s.re ^ 2 + s.im ^ 2) := div_pos h_num h_den
  obtain ⟨N, hN⟩ := h_vanish ((2 * s.re - 1) / (s.re ^ 2 + s.im ^ 2)) h_eps
  exact euclid_contradiction_excludes_offline_zero s.re s.im (E_dir N) (E_dir N)
    (h_floor s hz h_half h_one N) (le_refl _) (gt_iff_lt.mpr hN)

/-- **Theorem 2 (Geometric-Trigonometric Euclid Pinch Implies `RiemannHypothesis`):**
    Combining `no_offline_zero_of_energy_vanishing` with the functional-equation
    strip symmetry `riemannZeta_zero_strip_symm` yields `_root_.RiemannHypothesis`
    directly from Condition C1 (`E_dir N → 0`) and the Cauchy-Schwarz Mellin floor. -/
theorem riemannHypothesis_of_euclid_energy_vanishing
    (E_dir : ℕ → ℝ)
    (h_vanish : ∀ ε : ℝ, 0 < ε → ∃ N : ℕ, E_dir N < ε)
    (h_floor : ∀ s : ℂ, riemannZeta s = 0 → 1 / 2 < s.re → s.re < 1 →
      ∀ N : ℕ, (2 * s.re - 1) / (s.re ^ 2 + s.im ^ 2) ≤ E_dir N) :
    RiemannHypothesis := by
  intro s hz h_not_triv h_not_one
  have h_sym := riemannZeta_zero_strip_symm hz h_not_triv h_not_one
  by_contra h_ne
  rcases lt_or_gt_of_ne h_ne with h_lt | h_gt
  · have h_refl_re : 1 / 2 < (1 - s).re := by
      rw [Complex.sub_re, Complex.one_re]
      linarith
    exact no_offline_zero_of_energy_vanishing E_dir h_vanish h_floor (1 - s)
      h_sym.2.1 h_refl_re h_sym.2.2.2
  · exact no_offline_zero_of_energy_vanishing E_dir h_vanish h_floor s
      hz h_gt h_sym.1.2

/-- **Theorem 3 (Weierstrass-Euclid Pinch Squeeze onto `1/2`):**
    If `E_dir N → 0` and `β₀` is trapped inside `[1/2 - E_dir N / 2, 1/2 + E_dir N / 2]`
    for every `N`, then `β₀ = 1/2` identically by `archimedean_epsilon_squeeze_to_critical_half`. -/
theorem weierstrass_pinch_squeeze_to_half_of_energy_vanishing
    (E_dir : ℕ → ℝ)
    (h_vanish : ∀ ε : ℝ, 0 < ε → ∃ N : ℕ, E_dir N < ε)
    (β₀ : ℝ)
    (h_trap : ∀ N : ℕ, (1 : ℝ) / 2 - E_dir N / 2 ≤ β₀ ∧ β₀ ≤ (1 : ℝ) / 2 + E_dir N / 2) :
    β₀ = (1 : ℝ) / 2 := by
  apply archimedean_epsilon_squeeze_to_critical_half β₀
  intro ε hε
  obtain ⟨N, hN⟩ := h_vanish (2 * ε) (by linarith)
  have h_t := h_trap N
  refine ⟨by linarith, by linarith⟩

end RiemannBlueprint
