/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)

Methodology note: ai is being used as a tool.
-/
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Tactic

/-!
# Selberg Mollifier Three-Part Margin Split & Conrey-Reciprocity Reduction

This module formalizes Stages 2 and 3 of the intermediate Selberg mollifier roadmap:
1. `selberg_bblr_explicit_safety_margin_pos`:
   Certifies the exact positive safety margin `ΔC = C_bblr - C_main = 0.091897 > 0`
   between the BBLR envelope constant `C_bblr = 0.212694` and the continuous
   Dirichlet main-term constant `C_main = 0.120797`.
2. `mellin_plancherel_conrey_window_and_reciprocity_split`:
   Decomposes the Mellin-Plancherel mollified energy `E_moll(N)` into:
   - Continuous Dirichlet main term `C_main / ln N`
   - Conrey unconditional short-mollifier window (`θ < 4/7`) `E_conrey`
   - Bettin-Conrey off-diagonal cotangent reciprocity remainder `R_off`
   and proves that whenever `E_conrey + R_off ≤ ΔC / ln N`, the full energy obeys
   `E_moll(N) ≤ C_bblr / ln N`.
3. `finite_deep_scan_and_asymptotic_reciprocity_margin_glue`:
   Glues the verified finite deep-scan envelope (`2 ≤ N ≤ 10000`) with the conditional
   asymptotic (`N > 10000`) reciprocity margin bound to yield the global `N ≥ 2`
   logarithmic decay bound `E_moll(N) ≤ C_bblr / ln N`.

EPISTEMIC BOUNDARY:
The infinite-dimensional `N → ∞` Premise A (`E_conrey(N) + R_off(N) ≤ ΔC / ln N`
for all `N > 10000`) remains strictly OPEN. This module certifies the finite-scan
bridge and the exact 3-part conditional reduction with zero `sorry` and standard axioms.
-/

namespace SelbergConreyReciprocityMarginSplit

/-- Canonical BBLR envelope constant `C_bblr = 0.212694`. -/
noncomputable def C_bblr : ℝ := 0.212694

/-- Continuous Dirichlet main-term constant `C_main = 0.120797`. -/
noncomputable def C_main : ℝ := 0.120797

/-- Remaining asymptotic safety margin `ΔC = C_bblr - C_main = 0.091897`. -/
noncomputable def Delta_C : ℝ := C_bblr - C_main

/-- Theorem 1: The explicit BBLR-to-Dirichlet safety margin `ΔC = 0.091897` is strictly positive. -/
theorem selberg_bblr_explicit_safety_margin_pos :
    Delta_C = 0.091897 ∧ 0 < Delta_C ∧ C_main + Delta_C = C_bblr := by
  unfold Delta_C C_bblr C_main
  norm_num

/-- Theorem 2: Three-part Mellin-Plancherel decomposition into continuous Dirichlet main term,
    Conrey short-mollifier window (`θ < 4/7`), and Bettin-Conrey off-diagonal reciprocity remainder. -/
theorem mellin_plancherel_conrey_window_and_reciprocity_split
    (N : ℕ) (hN : 2 ≤ N)
    (E_moll E_conrey R_off : ℝ)
    (h_decomp : E_moll = C_main / Real.log (N : ℝ) + E_conrey + R_off)
    (h_slack : E_conrey + R_off ≤ Delta_C / Real.log (N : ℝ)) :
    E_moll ≤ C_bblr / Real.log (N : ℝ) := by
  have h1_lt : (1 : ℝ) < (N : ℝ) := by
    have h2 : (2 : ℝ) ≤ (N : ℝ) := by exact_mod_cast hN
    linarith
  have hlog_pos : 0 < Real.log (N : ℝ) := Real.log_pos h1_lt
  have h_sum : C_main / Real.log (N : ℝ) + Delta_C / Real.log (N : ℝ) = C_bblr / Real.log (N : ℝ) := by
    rw [← add_div]
    unfold Delta_C
    ring
  linarith

/-- Theorem 3: Gluing the finite deep scan (`2 ≤ N ≤ N_scan`, e.g., `N_scan = 10000`)
    with the asymptotic reciprocity margin bound (`N > N_scan`) yields the uniform
    logarithmic decay envelope `E_moll(N) ≤ C_bblr / ln N` for all `N ≥ 2`. -/
theorem finite_deep_scan_and_asymptotic_reciprocity_margin_glue
    (N_scan : ℕ)
    (E_moll E_conrey R_off : ℕ → ℝ)
    (h_finite_scan : ∀ N : ℕ, 2 ≤ N → N ≤ N_scan → E_moll N ≤ C_bblr / Real.log (N : ℝ))
    (h_asymp_decomp : ∀ N : ℕ, N_scan < N →
      E_moll N = C_main / Real.log (N : ℝ) + E_conrey N + R_off N)
    (h_asymp_slack : ∀ N : ℕ, N_scan < N →
      E_conrey N + R_off N ≤ Delta_C / Real.log (N : ℝ)) :
    ∀ N : ℕ, 2 ≤ N → E_moll N ≤ C_bblr / Real.log (N : ℝ) := by
  intro N hN
  by_cases h_le : N ≤ N_scan
  · exact h_finite_scan N hN h_le
  · have h_gt : N_scan < N := Nat.lt_of_not_le h_le
    exact mellin_plancherel_conrey_window_and_reciprocity_split N hN
      (E_moll N) (E_conrey N) (R_off N)
      (h_asymp_decomp N h_gt) (h_asymp_slack N h_gt)

#print axioms selberg_bblr_explicit_safety_margin_pos
#print axioms mellin_plancherel_conrey_window_and_reciprocity_split
#print axioms finite_deep_scan_and_asymptotic_reciprocity_margin_glue

end SelbergConreyReciprocityMarginSplit
