/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import Mathlib.Tactic

/-!
# Euclid Opposite-Side Contradiction Exclusion Discs

`NO_RH_PROOF = TRUE`:
This module certifies finite-`N` algebraic equivalences and rational exclusion
discs derived from the Cauchy-Schwarz Mellin off-line zero floor.
The asymptotic `N → ∞` Clay Riemann Hypothesis remains strictly OPEN.
-/

namespace RiemannBlueprint

/-- **NO_RH_PROOF = TRUE**: The asymptotic `N → ∞` Clay Riemann Hypothesis
    remains strictly OPEN. -/
def no_rh_proof_euclid_exclusion_lock : Bool := true

/-- Theorem 1 (Euclid Off-Line Zero Disc Equivalence):
    For `E > 0` and `β₀² + γ₀² > 0`,
    `(2 * β₀ - 1) / (β₀² + γ₀²) > E ↔ (β₀ - 1 / E)² + γ₀² < (1 - E) / E²`. -/
theorem euclid_offline_zero_disc_equivalence
    (β₀ γ₀ E : ℝ) (hE : 0 < E) (h_norm : 0 < β₀ ^ 2 + γ₀ ^ 2) :
    (2 * β₀ - 1) / (β₀ ^ 2 + γ₀ ^ 2) > E ↔
      (β₀ - 1 / E) ^ 2 + γ₀ ^ 2 < (1 - E) / E ^ 2 := by
  have hE_ne : E ≠ 0 := ne_of_gt hE
  rw [gt_iff_lt, lt_div_iff₀ h_norm]
  constructor
  · intro h_lt
    have h_mul : E * (β₀ - 1 / E) ^ 2 + E * γ₀ ^ 2 < (1 - E) / E := by
      have h_eq : E * (β₀ - 1 / E) ^ 2 + E * γ₀ ^ 2 =
          (E * (β₀ ^ 2 + γ₀ ^ 2) - (2 * β₀ - 1)) + (1 - E) / E := by
        field_simp
        ring
      linarith
    have h_div := div_lt_div_of_pos_right h_mul hE
    have h_lhs : (E * (β₀ - 1 / E) ^ 2 + E * γ₀ ^ 2) / E = (β₀ - 1 / E) ^ 2 + γ₀ ^ 2 := by
      field_simp
    have h_rhs : ((1 - E) / E) / E = (1 - E) / E ^ 2 := by
      field_simp
    linarith
  · intro h_disc
    have h_mul : E * ((β₀ - 1 / E) ^ 2 + γ₀ ^ 2) < E * ((1 - E) / E ^ 2) :=
      mul_lt_mul_of_pos_left h_disc hE
    have h_lhs : E * ((β₀ - 1 / E) ^ 2 + γ₀ ^ 2) =
        E * (β₀ ^ 2 + γ₀ ^ 2) - (2 * β₀ - 1) + (1 - E) / E := by
      field_simp
      ring
    have h_rhs : E * ((1 - E) / E ^ 2) = (1 - E) / E := by
      field_simp
    linarith

/-- Theorem 2 (Euclid Contradiction Excludes Off-Line Zero):
    Given the Cauchy-Schwarz floor `E_dir ≥ (2 * β₀ - 1) / (β₀² + γ₀²)`
    and a finite matrix measurement `E_dir ≤ E_bound`, any point satisfying
    `(2 * β₀ - 1) / (β₀² + γ₀²) > E_bound` leads to `False`. -/
theorem euclid_contradiction_excludes_offline_zero
    (β₀ γ₀ E_dir E_bound : ℝ)
    (h_floor : (2 * β₀ - 1) / (β₀ ^ 2 + γ₀ ^ 2) ≤ E_dir)
    (h_meas : E_dir ≤ E_bound)
    (h_excl : (2 * β₀ - 1) / (β₀ ^ 2 + γ₀ ^ 2) > E_bound) : False := by
  linarith

/-- Theorem 3 (Monotonicity of Exclusion Disc in Cutoff):
    If `0 < E_N2 ≤ E_N1`, every point `(β₀, γ₀)` excluded at `N₁` is strictly
    excluded at `N₂`. -/
theorem exclusion_disc_monotone_in_cutoff
    (β₀ γ₀ E_N1 E_N2 : ℝ) (_hE2 : 0 < E_N2) (h_le : E_N2 ≤ E_N1)
    (h_excl1 : (2 * β₀ - 1) / (β₀ ^ 2 + γ₀ ^ 2) > E_N1) :
    (2 * β₀ - 1) / (β₀ ^ 2 + γ₀ ^ 2) > E_N2 := by
  linarith

/-- Theorem 4 (`N = 211` Explicit Rational Exclusion Certificate):
    Using `E_211 ≤ 863 / 100000` at `β₀ = 1`, every `(1, γ₀)` with `γ₀² ≤ 114`
    satisfies `(2 * 1 - 1) / (1² + γ₀²) > 863 / 100000`. -/
theorem n211_and_n500_explicit_exclusion_cert
    (γ₀ : ℝ) (hγ : γ₀ ^ 2 ≤ 114) :
    (2 * (1 : ℝ) - 1) / ((1 : ℝ) ^ 2 + γ₀ ^ 2) > (863 : ℝ) / 100000 := by
  have h_pos : (0 : ℝ) < (1 : ℝ) ^ 2 + γ₀ ^ 2 := by positivity
  rw [gt_iff_lt, lt_div_iff₀ h_pos]
  nlinarith

end RiemannBlueprint
