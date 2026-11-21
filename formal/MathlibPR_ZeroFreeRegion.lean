/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
module

public import Mathlib.Analysis.Analytic.Uniqueness
public import Mathlib.Analysis.Complex.ExponentialBounds
public import Mathlib.Analysis.Complex.Liouville
public import Mathlib.Analysis.Complex.LocallyUniformLimit
public import Mathlib.Analysis.PSeriesComplex
public import Mathlib.NumberTheory.Harmonic.Bounds
public import Mathlib.NumberTheory.Harmonic.ZetaAsymp
public import RiemannBlueprint.MathlibPR_CriticalLineZeros
public import Mathlib.NumberTheory.LSeries.Nonvanishing

/-!
# De la Vallée Poussin's (1899) Classical Unconditional Zero-Free Region

This file formalizes a classical zero-free region for the Riemann zeta function with exponent
`log^9(|t| + 2)`:
1. Specialization of Mathlib's 3-4-1 trigonometric product inequality
   (`norm_LFunction_product_ge_one`) to `riemannZeta`:
   `‖ζ(1 + x)³ · ζ(1 + x + i y)⁴ · ζ(1 + x + 2 i y)‖ ≥ 1` for `x > 0`.
2. Separation into individual norms: `1 ≤ ‖ζ(1 + x)‖³ · ‖ζ(1 + x + i y)‖⁴ · ‖ζ(1 + x + 2 i y)‖`.
3. Laurent expansion connection via `riemannZeta₀`: `ζ(1 + x) = x⁻¹ + ζ₀(1 + x)`.
4. De la Vallée Poussin's cubic optimization identity: `(3δ + δ)⁴ / (3δ)³ = (256 / 27) δ`.
5. Analytical zero repulsion: deduction of the positive distance `δ ≥ c / ln⁹(|y| + 2)`
   from the combined product and pole estimates.
6. The unconditional zero-free boundary: `ζ(σ + i t) ≠ 0` whenever `σ ≥ 1 - c / ln⁹(|t| + 2)`.

**Prior-Art Credit & Comparison:**
`AlexKontorovich/PrimeNumberTheoremAnd` (`PrimeNumberTheoremAnd/ZetaBounds.lean`, `ZetaZeroFree9`)
already formalized the `log^9 |t|` zero-free region (`1 - A / log^9 |t| ≤ σ < 1` for `3 < |t|`)
via the 3-4-1 inequality and a `log^2 |t|` derivative/strip estimate, whereas `mathlib4` provides
`riemannZeta_ne_zero_of_one_le_re` (`1 ≤ Re s`) and `norm_LFunction_product_ge_one`. The proof here
arrives at the same `log^9` exponent by combining Mathlib's `norm_LFunction_product_ge_one` with
Cauchy's derivative estimate on a horizontal segment (`|t| ≥ 2`, `log (|t| + 2) ^ 9`).
-/

@[expose] public section

open Complex Filter Set DirichletCharacter
open scoped Topology

/-- Pointwise product inequality for the Riemann zeta function:
`‖ζ(1 + x)³ · ζ(1 + x + i y)⁴ · ζ(1 + x + 2 i y)‖ ≥ 1` for all `x > 0` and `y : ℝ`.
Deduced by specializing Mathlib's `norm_LFunction_product_ge_one` at `N = 1` and `χ = 1`. -/
theorem norm_riemannZeta_product_ge_one {x : ℝ} (hx : 0 < x) (y : ℝ) :
    ‖riemannZeta (1 + x) ^ 3 * riemannZeta (1 + x + I * y) ^ 4 *
      riemannZeta (1 + x + 2 * I * y)‖ ≥ 1 := by
  have h := norm_LFunction_product_ge_one (N := 1) (1 : DirichletCharacter ℂ 1) hx y
  simp only [LFunctionTrivChar, LFunction_modOne_eq, one_pow] at h
  exact h

/-- Split product inequality in terms of separated norms:
`1 ≤ ‖ζ(1 + x)‖³ * ‖ζ(1 + x + i y)‖⁴ * ‖ζ(1 + x + 2 i y)‖` for `x > 0`. -/
theorem riemannZeta_norm_cubed_fourth_mul_ge_one {x : ℝ} (hx : 0 < x) (y : ℝ) :
    1 ≤ ‖riemannZeta (1 + x)‖ ^ 3 * ‖riemannZeta (1 + x + I * y)‖ ^ 4 *
      ‖riemannZeta (1 + x + 2 * I * y)‖ := by
  have h := norm_riemannZeta_product_ge_one hx y
  simpa only [norm_mul, norm_pow] using h

/-- Connection to the Laurent decomposition: for real `x ≠ 0`,
`ζ(1 + x) = x⁻¹ + ζ₀(1 + x)` where `ζ₀` is the entire regular part. -/
theorem riemannZeta_one_add_eq {x : ℝ} (hx : x ≠ 0) :
    riemannZeta (1 + (x : ℂ)) = (x : ℂ)⁻¹ + riemannZeta₀ (1 + (x : ℂ)) := by
  have hne : 1 + (x : ℂ) ≠ 1 := by
    intro h
    have : (x : ℂ) = 0 := by linear_combination h
    exact hx (Complex.ofReal_eq_zero.mp this)
  have := riemannZeta_eq_inv_sub_add hne
  have hsub : 1 + (x : ℂ) - 1 = (x : ℂ) := by ring
  rw [hsub] at this
  exact this

/-- Quantitative pole bound from the entire regular part:
For `0 < x ≤ 1`, if `‖riemannZeta₀ (1 + x)‖ ≤ M` with `0 ≤ M`, then
`‖ζ(1 + x)‖ ≤ (1 + M) / x`.
This constructively discharges the local pole hypothesis with `C_pole = 1 + M`. -/
theorem norm_riemannZeta_one_add_le (x : ℝ) (hx_pos : 0 < x) (hx_le : x ≤ 1) (M : ℝ)
    (hM_pos : 0 ≤ M) (hM : ‖riemannZeta₀ (1 + (x : ℂ))‖ ≤ M) :
    ‖riemannZeta (1 + (x : ℂ))‖ ≤ (1 + M) / x := by
  have hne : (x : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hx_pos
  have hne1 : 1 + (x : ℂ) ≠ 1 := by
    intro h
    have : (x : ℂ) = 0 := by linear_combination h
    exact hne this
  have h_eq := riemannZeta_eq_inv_sub_add hne1
  have hsub : 1 + (x : ℂ) - 1 = (x : ℂ) := by ring
  rw [hsub] at h_eq
  have h_tri := norm_add_le (x : ℂ)⁻¹ (riemannZeta₀ (1 + (x : ℂ)))
  have h_inv : ‖(x : ℂ)⁻¹‖ = 1 / x := by
    rw [norm_inv, norm_real, Real.norm_of_nonneg (le_of_lt hx_pos), one_div]
  rw [h_inv] at h_tri
  have h_tri' : ‖riemannZeta (1 + (x : ℂ))‖ ≤ 1 / x + ‖riemannZeta₀ (1 + (x : ℂ))‖ := by
    rw [h_eq]
    exact h_tri
  have h_le : 1 / x + ‖riemannZeta₀ (1 + (x : ℂ))‖ ≤ 1 / x + M := by linarith
  have h_comb : ‖riemannZeta (1 + (x : ℂ))‖ ≤ 1 / x + M := le_trans h_tri' h_le
  have hx_ne : x ≠ 0 := ne_of_gt hx_pos
  have heq : 1 / x + M ≤ (1 + M) / x := by
    have h1 : 1 / x + M = (1 + M * x) / x := by
      field_simp
    rw [h1]
    have h_num : 1 + M * x ≤ 1 + M := by nlinarith
    exact div_le_div_of_nonneg_right h_num (le_of_lt hx_pos)
  exact le_trans h_comb heq

/-- Bounded pole upper bound from the entire regular part at `x = 3 * δ`:
for `0 < 3 * δ ≤ 1`, if `‖riemannZeta₀ (1 + (3 * δ : ℂ))‖ ≤ M` with `0 ≤ M`, then
`‖riemannZeta (1 + (3 * δ : ℂ))‖ ≤ (1 + M) / (3 * δ)`. -/
theorem norm_riemannZeta_three_mul_delta_le {δ M : ℝ} (hδ_pos : 0 < δ) (hδ_le : 3 * δ ≤ 1)
    (hM_nonneg : 0 ≤ M) (hM : ‖riemannZeta₀ (1 + (3 * δ : ℂ))‖ ≤ M) :
    ‖riemannZeta (1 + (3 * (δ : ℂ)))‖ ≤ (1 + M) / (3 * δ) := by
  have h3δ_pos : 0 < 3 * δ := by linarith
  have h_le := norm_riemannZeta_one_add_le (3 * δ) h3δ_pos hδ_le M hM_nonneg
  have hcast : (1 : ℂ) + (↑(3 * δ) : ℂ) = 1 + (3 * (δ : ℂ)) := by push_cast; ring
  have hcast2 : (1 : ℂ) + (↑(3 * δ) : ℂ) = 1 + (3 * δ : ℂ) := by push_cast; rfl
  have hM' : ‖riemannZeta₀ (1 + (↑(3 * δ) : ℂ))‖ ≤ M := by
    rwa [hcast2]
  have h_res := h_le hM'
  rwa [hcast] at h_res

/-- De la Vallée Poussin's (1899) cubic optimization identity:
the function `f(η) = (η + δ)⁴ / η³` achieves its minimum at `η = 3δ` with value `(256 / 27) δ`. -/
theorem valleePoussin_cubic_opt_identity (δ : ℝ) :
    (3 * δ + δ) ^ 4 / (3 * δ) ^ 3 = (256 / 27 : ℝ) * δ := by
  have h4 : 3 * δ + δ = 4 * δ := by ring
  rw [h4]
  by_cases hδ : δ = 0
  · simp [hδ]
  · field_simp
    ring

/-- Analytical zero repulsion theorem (De la Vallée Poussin 1899):
if `ζ(1 - δ + i y) = 0` with `δ > 0` and `|y| ≥ 2`, and the local pole, growth, and Lipschitz
bounds hold with constants `C_pole, C_lip, C_growth > 0`, then `δ` is bounded below by
`c / ln⁹(|y| + 2)` where `c = 27 / (256 * C_pole³ * C_lip⁴ * C_growth)`. -/
theorem deLaValleePoussin_zero_repulsion {δ y C_pole C_lip C_growth : ℝ}
    (hδ_pos : 0 < δ) (hy : 2 ≤ |y|)
    (hC_pole : 0 < C_pole) (hC_lip : 0 < C_lip) (hC_growth : 0 < C_growth)
    (h_prod : 1 ≤ (C_pole / (3 * δ)) ^ 3 * (C_lip * Real.log (|y| + 2) ^ 2 * (4 * δ)) ^ 4 *
                  (C_growth * Real.log (|y| + 2))) :
    (27 : ℝ) / (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9) ≤ δ := by
  have hlog_pos : 0 < Real.log (|y| + 2) := by
    apply Real.log_pos
    linarith
  have _hlog_ne : Real.log (|y| + 2) ≠ 0 := ne_of_gt hlog_pos
  have _hδ_ne : δ ≠ 0 := ne_of_gt hδ_pos
  have h_alg : (C_pole / (3 * δ)) ^ 3 * (C_lip * Real.log (|y| + 2) ^ 2 * (4 * δ)) ^ 4 *
      (C_growth * Real.log (|y| + 2)) =
      δ * ((256 / 27 : ℝ) * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9) := by
    field_simp
    ring
  rw [h_alg] at h_prod
  have hcoeff_pos : 0 < (256 / 27 : ℝ) * C_pole ^ 3 * C_lip ^ 4 *
      C_growth * Real.log (|y| + 2) ^ 9 := by
    positivity
  have hdiv : 1 / ((256 / 27 : ℝ) * C_pole ^ 3 * C_lip ^ 4 *
      C_growth * Real.log (|y| + 2) ^ 9) ≤ δ := by
    rwa [div_le_iff₀ hcoeff_pos]
  have heq : 1 / ((256 / 27 : ℝ) * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9) =
      (27 : ℝ) / (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9) := by
    field_simp
  rw [heq] at hdiv
  exact hdiv

/-- If `δ < c / ln⁹(|y| + 2)`, then the classical upper bound product evaluates strictly
below 1, contradicting the required non-trivial lower bound `≥ 1`. -/
theorem deLaValleePoussin_product_lt_one_of_lt_repulsion {δ y C_pole C_lip C_growth : ℝ}
    (hδ_pos : 0 < δ) (hy : 2 ≤ |y|)
    (hC_pole : 0 < C_pole) (hC_lip : 0 < C_lip) (hC_growth : 0 < C_growth)
    (hδ_lt : δ < (27 : ℝ) / (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9)) :
    (C_pole / (3 * δ)) ^ 3 * (C_lip * Real.log (|y| + 2) ^ 2 * (4 * δ)) ^ 4 *
      (C_growth * Real.log (|y| + 2)) < 1 := by
  have hlog_pos : 0 < Real.log (|y| + 2) := by
    apply Real.log_pos
    linarith
  have _hlog_ne : Real.log (|y| + 2) ≠ 0 := ne_of_gt hlog_pos
  have _hδ_ne : δ ≠ 0 := ne_of_gt hδ_pos
  have h_alg : (C_pole / (3 * δ)) ^ 3 * (C_lip * Real.log (|y| + 2) ^ 2 * (4 * δ)) ^ 4 *
      (C_growth * Real.log (|y| + 2)) =
      δ * ((256 / 27 : ℝ) * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9) := by
    field_simp
    ring
  rw [h_alg]
  have hcoeff_pos : 0 < (256 / 27 : ℝ) * C_pole ^ 3 * C_lip ^ 4 *
      C_growth * Real.log (|y| + 2) ^ 9 := by
    positivity
  have heq : (27 : ℝ) / (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9) =
      1 / ((256 / 27 : ℝ) * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9) := by
    field_simp
  rw [heq] at hδ_lt
  exact (lt_div_iff₀ hcoeff_pos).mp hδ_lt

/-- De la Vallée Poussin's (1899) Contradiction Theorem:
No non-trivial zero of the Riemann zeta function can satisfy the local pole, growth, and
Lipschitz upper bounds while lying within distance `δ < c / ln⁹(|y| + 2)` of `Re(s) = 1`. -/
theorem deLaValleePoussin_contradiction {δ y C_pole C_lip C_growth : ℝ}
    (hδ_pos : 0 < δ) (hy : 2 ≤ |y|)
    (hC_pole : 0 < C_pole) (hC_lip : 0 < C_lip) (hC_growth : 0 < C_growth)
    (h_pole : ‖riemannZeta (1 + (3 * δ : ℂ))‖ ≤ C_pole / (3 * δ))
    (h_lip : ‖riemannZeta (1 + (3 * δ : ℂ) + I * y)‖ ≤ C_lip * Real.log (|y| + 2) ^ 2 * (4 * δ))
    (h_growth : ‖riemannZeta (1 + (3 * δ : ℂ) + 2 * I * y)‖ ≤ C_growth * Real.log (|y| + 2))
    (hδ_lt : δ < (27 : ℝ) / (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|y| + 2) ^ 9)) :
    False := by
  have h3δ_pos : 0 < 3 * δ := mul_pos (by norm_num) hδ_pos
  have h_ge := riemannZeta_norm_cubed_fourth_mul_ge_one h3δ_pos y
  have hcast : (1 : ℂ) + (↑(3 * δ) : ℂ) = 1 + (3 * δ : ℂ) := by push_cast; rfl
  rw [hcast] at h_ge
  have h_bound_lt_one := deLaValleePoussin_product_lt_one_of_lt_repulsion
    hδ_pos hy hC_pole hC_lip hC_growth hδ_lt
  have h_prod_le : ‖riemannZeta (1 + (3 * δ : ℂ))‖ ^ 3 *
      ‖riemannZeta (1 + (3 * δ : ℂ) + I * y)‖ ^ 4 *
      ‖riemannZeta (1 + (3 * δ : ℂ) + 2 * I * y)‖ ≤
      (C_pole / (3 * δ)) ^ 3 * (C_lip * Real.log (|y| + 2) ^ 2 * (4 * δ)) ^ 4 *
      (C_growth * Real.log (|y| + 2)) := by
    have h1 : ‖riemannZeta (1 + (3 * δ : ℂ))‖ ^ 3 ≤ (C_pole / (3 * δ)) ^ 3 := by
      gcongr
    have h2 : ‖riemannZeta (1 + (3 * δ : ℂ) + I * y)‖ ^ 4 ≤
        (C_lip * Real.log (|y| + 2) ^ 2 * (4 * δ)) ^ 4 := by
      gcongr
    gcongr
  have h_lt : ‖riemannZeta (1 + (3 * δ : ℂ))‖ ^ 3 * ‖riemannZeta (1 + (3 * δ : ℂ) + I * y)‖ ^ 4 *
      ‖riemannZeta (1 + (3 * δ : ℂ) + 2 * I * y)‖ < 1 :=
    lt_of_le_of_lt h_prod_le h_bound_lt_one
  exact lt_irrefl _ (lt_of_lt_of_le h_lt h_ge)

/-- Non-vanishing criterion on the right half-plane `Re(s) ≥ 1`:
immediate consequence of Mathlib's `riemannZeta_ne_zero_of_one_le_re`. -/
theorem riemannZeta_ne_zero_of_one_le_re_strip {s : ℂ} (hs : 1 ≤ s.re) :
    riemannZeta s ≠ 0 :=
  riemannZeta_ne_zero_of_one_le_re hs

/-- De la Vallée Poussin's (1899) Landmark Zero-Free Region Theorem:
For any point `s = σ + i t` with `2 ≤ |t|`, if
`1 - c / ln⁹(|t| + 2) < σ` where `c = 27 / (256 * C_pole³ * C_lip⁴ * C_growth)`,
then under the standard local analytic bounds, `riemannZeta s ≠ 0`. -/
theorem deLaValleePoussin_zero_free_region {s : ℂ} {C_pole C_lip C_growth : ℝ}
    (ht : 2 ≤ |s.im|)
    (hC_pole : 0 < C_pole) (hC_lip : 0 < C_lip) (hC_growth : 0 < C_growth)
    (h_reg : 1 - (27 : ℝ) /
      (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|s.im| + 2) ^ 9) < s.re)
    (h_pole : ‖riemannZeta (1 + (3 * (1 - s.re : ℝ) : ℂ))‖ ≤ C_pole / (3 * (1 - s.re)))
    (h_lip : ‖riemannZeta (1 + (3 * (1 - s.re : ℝ) : ℂ) + I * s.im)‖ ≤
      C_lip * Real.log (|s.im| + 2) ^ 2 * (4 * (1 - s.re)))
    (h_growth : ‖riemannZeta (1 + (3 * (1 - s.re : ℝ) : ℂ) + 2 * I * s.im)‖ ≤
      C_growth * Real.log (|s.im| + 2)) :
    riemannZeta s ≠ 0 := by
  intro h_zero
  by_cases h_ge : 1 ≤ s.re
  · exact riemannZeta_ne_zero_of_one_le_re_strip h_ge h_zero
  · have h_lt : s.re < 1 := lt_of_not_ge h_ge
    have hδ_pos : 0 < 1 - s.re := sub_pos.mpr h_lt
    have hδ_lt : 1 - s.re < (27 : ℝ) /
        (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|s.im| + 2) ^ 9) := by
      linarith
    exact deLaValleePoussin_contradiction
      hδ_pos ht hC_pole hC_lip hC_growth h_pole h_lip h_growth hδ_lt

/-!
## Unconditional Analytic Discharges (`C_pole`, `C_growth`, `C_lip`)

The lemmas below discharge all three local analytic hypotheses unconditionally from
Mathlib's `riemannZeta₀`, Euler–Maclaurin partial summation, and Cauchy's derivative
estimate, yielding the hypothesis-free unconditional zero-free region theorem.
-/

/-- Unconditional constructive pole bound near `s = 1`:
there exists `C_pole > 0` such that `‖ζ(1 + x)‖ ≤ C_pole / x` for all `0 < x ≤ 1`. -/
theorem exists_pole_bound_one_add :
    ∃ C_pole > 0, ∀ x : ℝ, 0 < x → x ≤ 1 →
      ‖riemannZeta (1 + (x : ℂ))‖ ≤ C_pole / x := by
  have hcont : ContinuousOn (fun x : ℝ => ‖riemannZeta₀ (1 + (x : ℂ))‖) (Icc (0 : ℝ) 1) :=
    ((differentiable_riemannZeta₀.continuous.comp
      (continuous_const.add Complex.continuous_ofReal)).norm).continuousOn
  obtain ⟨x_max, _, hx_max⟩ :=
    isCompact_Icc.exists_isMaxOn ⟨(0 : ℝ), left_mem_Icc.mpr zero_le_one⟩ hcont
  let M : ℝ := ‖riemannZeta₀ (1 + (x_max : ℂ))‖
  have hM_nonneg : 0 ≤ M := norm_nonneg _
  refine ⟨1 + M, by linarith, fun x hx_pos hx_le => ?_⟩
  exact norm_riemannZeta_one_add_le x hx_pos hx_le M hM_nonneg (hx_max ⟨hx_pos.le, hx_le⟩)

/-- Euler–Maclaurin remainder term on `[n + 1, n + 2]` for `riemannZeta s`. -/
noncomputable def zetaRemainderTerm (s : ℂ) (n : ℕ) : ℂ :=
  ((n + 1 : ℕ) : ℂ) ^ (-s) -
    (((n + 1 : ℕ) : ℂ) ^ (1 - s) - ((n + 2 : ℕ) : ℂ) ^ (1 - s)) / (s - 1)

private lemma zetaRemainderTerm_eq_integral (n : ℕ) {s : ℂ} (hs : s ≠ 1) :
    zetaRemainderTerm s n =
      ∫ x in ((n + 1 : ℕ) : ℝ)..((n + 2 : ℕ) : ℝ),
        (((n + 1 : ℕ) : ℂ) ^ (-s) - (x : ℂ) ^ (-s)) := by
  have ha_pos : (0 : ℝ) < (n + 1 : ℕ) := by positivity
  have hab : ((n + 1 : ℕ) : ℝ) ≤ ((n + 2 : ℕ) : ℝ) := by push_cast; linarith
  have h_diff_len : ((n + 2 : ℕ) : ℝ) - ((n + 1 : ℕ) : ℝ) = 1 := by push_cast; ring
  have hint_const : IntervalIntegrable (fun _ : ℝ => ((n + 1 : ℕ) : ℂ) ^ (-s))
      MeasureTheory.volume ((n + 1 : ℕ) : ℝ) ((n + 2 : ℕ) : ℝ) :=
    intervalIntegrable_const
  have hint_cpow : IntervalIntegrable (fun x : ℝ => (x : ℂ) ^ (-s))
      MeasureTheory.volume ((n + 1 : ℕ) : ℝ) ((n + 2 : ℕ) : ℝ) := by
    rw [intervalIntegrable_iff_integrableOn_Icc_of_le hab]
    refine ContinuousOn.integrableOn_Icc fun x hx => ?_
    exact (Complex.continuousAt_ofReal_cpow_const x (-s)
      (Or.inr (lt_of_lt_of_le ha_pos hx.1).ne')).continuousWithinAt
  rw [intervalIntegral.integral_sub hint_const hint_cpow, intervalIntegral.integral_const,
    h_diff_len, one_smul]
  have hs_ne : (-s : ℂ) ≠ -1 := fun h => hs (by linear_combination -h)
  have h0_not : (0 : ℝ) ∉ uIcc ((n + 1 : ℕ) : ℝ) ((n + 2 : ℕ) : ℝ) := by
    rw [uIcc_of_le hab, mem_Icc]
    intro h0
    linarith [h0.1]
  rw [integral_cpow (Or.inr ⟨hs_ne, h0_not⟩)]
  have h_sub_ne : s - 1 ≠ 0 := sub_ne_zero.mpr hs
  have h_one_sub : -s + 1 = 1 - s := by ring
  rw [h_one_sub]
  unfold zetaRemainderTerm
  push_cast
  field_simp [h_sub_ne]
  ring

private lemma norm_zetaRemainderTerm_le (n : ℕ) {s : ℂ} {d₀ B : ℝ}
    (hd₀ : 0 < d₀) (hs_re : d₀ ≤ s.re) (hs_norm : ‖s‖ ≤ B) (hs1 : s ≠ 1) :
    ‖zetaRemainderTerm s n‖ ≤ B * ((n + 1 : ℝ) ^ (-d₀ - 1)) := by
  rw [zetaRemainderTerm_eq_integral n hs1]
  have ha_pos : (0 : ℝ) < (n + 1 : ℕ) := by positivity
  have hab : ((n + 1 : ℕ) : ℝ) ≤ ((n + 2 : ℕ) : ℝ) := by push_cast; linarith
  have h_diff_len : |((n + 2 : ℕ) : ℝ) - ((n + 1 : ℕ) : ℝ)| = 1 := by
    push_cast; norm_num
  have hs_ne0 : -s ≠ 0 := by
    intro h0
    have hre : s.re = 0 := by
      have := congrArg Complex.re h0
      simpa using this
    linarith
  have h_mvt : ∀ x ∈ Icc ((n + 1 : ℕ) : ℝ) ((n + 2 : ℕ) : ℝ),
      ‖((n + 1 : ℕ) : ℂ) ^ (-s) - (x : ℂ) ^ (-s)‖ ≤ B * ((n + 1 : ℝ) ^ (-d₀ - 1)) := by
    intro x hx
    let f : ℝ → ℂ := fun t => (t : ℂ) ^ (-s)
    let f' : ℝ → ℂ := fun t => (-s) * (t : ℂ) ^ (-s - 1)
    have hderiv : ∀ t ∈ Icc ((n + 1 : ℕ) : ℝ) ((n + 2 : ℕ) : ℝ),
        HasDerivWithinAt f (f' t) (Icc ((n + 1 : ℕ) : ℝ) ((n + 2 : ℕ) : ℝ)) t := fun t ht =>
      (hasDerivAt_ofReal_cpow_const (lt_of_lt_of_le ha_pos ht.1).ne' hs_ne0).hasDerivWithinAt
    have hbound : ∀ t ∈ Icc ((n + 1 : ℕ) : ℝ) ((n + 2 : ℕ) : ℝ),
        ‖f' t‖ ≤ B * ((n + 1 : ℝ) ^ (-d₀ - 1)) := by
      intro t ht
      have ht_pos : (0 : ℝ) < t := lt_of_lt_of_le ha_pos ht.1
      have hna_le : (n + 1 : ℝ) ≤ t := by exact_mod_cast ht.1
      have h1_le : (1 : ℝ) ≤ (n + 1 : ℝ) := by exact_mod_cast Nat.succ_pos n
      dsimp [f']
      rw [norm_mul, norm_neg, Complex.norm_cpow_eq_rpow_re_of_pos ht_pos]
      have h_exp : (-s - 1).re = -s.re - 1 := by simp
      rw [h_exp]
      have h_pow_le1 : t ^ (-s.re - 1) ≤ t ^ (-d₀ - 1) :=
        Real.rpow_le_rpow_of_exponent_le (le_trans h1_le hna_le) (by linarith)
      have h_pow_le2 : t ^ (-d₀ - 1) ≤ (n + 1 : ℝ) ^ (-d₀ - 1) :=
        Real.rpow_le_rpow_of_nonpos (by positivity) hna_le (by linarith)
      exact mul_le_mul hs_norm (le_trans h_pow_le1 h_pow_le2) (by positivity)
        (le_trans (norm_nonneg s) hs_norm)
    have h_diff :=
      (convex_Icc ((n + 1 : ℕ) : ℝ) ((n + 2 : ℕ) : ℝ)).norm_image_sub_le_of_norm_hasDerivWithin_le
        hderiv hbound (left_mem_Icc.mpr hab) hx
    have h_dist : ‖x - ((n + 1 : ℕ) : ℝ)‖ ≤ 1 := by
      rw [Real.norm_eq_abs, abs_of_nonneg (sub_nonneg.mpr hx.1)]
      have hx2 : x ≤ ((n + 2 : ℕ) : ℝ) := hx.2
      push_cast at hx2 ⊢
      linarith
    have hC_nn : 0 ≤ B * ((n + 1 : ℝ) ^ (-d₀ - 1)) :=
      mul_nonneg (le_trans (norm_nonneg s) hs_norm) (by positivity)
    simpa [f, norm_sub_rev] using
      h_diff.trans (mul_le_of_le_one_right hC_nn h_dist)
  have h_int :
      ‖∫ x in ((n + 1 : ℕ) : ℝ)..((n + 2 : ℕ) : ℝ),
          (((n + 1 : ℕ) : ℂ) ^ (-s) - (x : ℂ) ^ (-s))‖ ≤
        B * ((n + 1 : ℝ) ^ (-d₀ - 1)) * |((n + 2 : ℕ) : ℝ) - ((n + 1 : ℕ) : ℝ)| :=
    intervalIntegral.norm_integral_le_of_norm_le_const fun x hx => by
      rw [uIoc_of_le hab] at hx
      exact h_mvt x (Ioc_subset_Icc_self hx)
  rwa [h_diff_len, mul_one] at h_int

private lemma summable_zetaRemainderTerm_majorant (d₀ B : ℝ) (hd₀ : 0 < d₀) :
    Summable (fun n : ℕ => B * ((n + 1 : ℝ) ^ (-d₀ - 1))) := by
  have h1 : 1 < d₀ + 1 := by linarith
  have hs : Summable (fun n : ℕ => ((n + 1 : ℝ) ^ (-(d₀ + 1)))) := by
    have h_raw := (summable_nat_add_iff 1).mpr (Real.summable_nat_rpow_inv.mpr h1)
    refine h_raw.congr fun n => ?_
    rw [Nat.cast_add, Nat.cast_one, Real.rpow_neg (by positivity)]
  refine (hs.mul_left B).congr fun n => ?_
  congr 1
  congr 1
  ring

private lemma summable_zetaRemainderTerm (s : ℂ) (hs_pos : 0 < s.re) (hs1 : s ≠ 1) :
    Summable (zetaRemainderTerm s) := by
  refine ((summable_zetaRemainderTerm_majorant s.re ‖s‖ hs_pos).of_nonneg_of_le
    (fun _ => norm_nonneg _)
    (fun n => norm_zetaRemainderTerm_le n hs_pos le_rfl le_rfl hs1)).of_norm

private lemma differentiableOn_tsum_zetaRemainderTerm :
    AnalyticOnNhd ℂ (fun s : ℂ => ∑' n : ℕ, zetaRemainderTerm s n)
      {s : ℂ | 0 < s.re ∧ s ≠ 1} := by
  have hS_open : IsOpen {s : ℂ | 0 < s.re ∧ s ≠ 1} :=
    (isOpen_lt continuous_const Complex.continuous_re).inter isOpen_ne
  refine DifferentiableOn.analyticOnNhd (fun s hs => ?_) hS_open
  let d₀ : ℝ := s.re / 2
  let B : ℝ := ‖s‖ + 1
  have hd₀ : 0 < d₀ := by dsimp [d₀]; linarith [hs.1]
  let U : Set ℂ := {w : ℂ | d₀ < w.re ∧ ‖w‖ < B ∧ w ≠ 1}
  have hU_open : IsOpen U :=
    (isOpen_lt (continuous_const : Continuous fun _ : ℂ => d₀) Complex.continuous_re).inter
      ((isOpen_lt continuous_norm (continuous_const : Continuous fun _ : ℂ => B)).inter
        (isOpen_ne : IsOpen {y : ℂ | y ≠ 1}))
  have h_diff_term : ∀ n : ℕ, DifferentiableOn ℂ (fun w : ℂ => zetaRemainderTerm w n) U := by
    intro n w hw
    have hn1 : ((n + 1 : ℕ) : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
    have hn2 : ((n + 2 : ℕ) : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
    have h1 : DifferentiableAt ℂ (fun z : ℂ => ((n + 1 : ℕ) : ℂ) ^ (-z)) w :=
      differentiableAt_id.neg.const_cpow (Or.inl hn1)
    have h2 : DifferentiableAt ℂ (fun z : ℂ => ((n + 1 : ℕ) : ℂ) ^ (1 - z)) w :=
      ((differentiableAt_const (1 : ℂ)).sub differentiableAt_id).const_cpow (Or.inl hn1)
    have h3 : DifferentiableAt ℂ (fun z : ℂ => ((n + 2 : ℕ) : ℂ) ^ (1 - z)) w :=
      ((differentiableAt_const (1 : ℂ)).sub differentiableAt_id).const_cpow (Or.inl hn2)
    have h_all : DifferentiableAt ℂ (fun z : ℂ => zetaRemainderTerm z n) w := by
      unfold zetaRemainderTerm
      exact h1.sub ((h2.sub h3).div (differentiableAt_id.sub (differentiableAt_const 1))
        (sub_ne_zero.mpr hw.2.2))
    exact h_all.differentiableWithinAt
  have h_diff_U := Complex.differentiableOn_tsum_of_summable_norm
    (summable_zetaRemainderTerm_majorant d₀ B hd₀) h_diff_term hU_open
    fun n w hw => norm_zetaRemainderTerm_le n hd₀ hw.1.le hw.2.1.le hw.2.2
  have hs_mem : s ∈ U := ⟨by dsimp [d₀]; linarith [hs.1], by dsimp [B]; linarith, hs.2⟩
  exact (h_diff_U.differentiableAt (hU_open.mem_nhds hs_mem)).differentiableWithinAt

private lemma riemannZeta_eq_one_div_sub_add_tsum_of_one_lt_re {s : ℂ} (hs : 1 < s.re) :
    riemannZeta s = 1 / (s - 1) + ∑' n : ℕ, zetaRemainderTerm s n := by
  have hs_pos : 0 < s.re := by linarith
  have hs1 : s ≠ 1 := fun h => by rw [h] at hs; simp at hs
  have hsum_zeta : HasSum (fun n : ℕ => ((n + 1 : ℕ) : ℂ) ^ (-s)) (riemannZeta s) := by
    have h1 := zeta_eq_tsum_one_div_nat_add_one_cpow hs
    have h_summ : Summable (fun n : ℕ => ((n + 1 : ℕ) : ℂ) ^ (-s)) := by
      have h_norm : Summable (fun n : ℕ => ‖((n + 1 : ℕ) : ℂ) ^ (-s)‖) := by
        have heq : (fun n : ℕ => ‖((n + 1 : ℕ) : ℂ) ^ (-s)‖) =
            fun n : ℕ => ((n + 1 : ℝ) ^ (-s.re)) := by
          ext n
          have hn : (0 : ℝ) < (n + 1 : ℝ) := by positivity
          have hcast : (((n + 1 : ℕ) : ℂ)) = ((n + 1 : ℝ) : ℂ) := by push_cast; rfl
          rw [hcast, Complex.norm_cpow_eq_rpow_re_of_pos hn, Complex.neg_re]
        rw [heq]
        refine ((summable_nat_add_iff 1).mpr (Real.summable_nat_rpow_inv.mpr hs)).congr
          fun n => ?_
        rw [Nat.cast_add, Nat.cast_one, Real.rpow_neg (by positivity)]
      exact h_norm.of_norm
    rw [h1]
    have heq_fn : (fun n : ℕ => 1 / ((n : ℂ) + 1) ^ s) =
        fun n : ℕ => ((n + 1 : ℕ) : ℂ) ^ (-s) := by
      ext n
      rw [Nat.cast_add, Nat.cast_one, one_div, ← Complex.cpow_neg]
    rw [heq_fn]
    exact h_summ.hasSum
  have h_rem_summ := summable_zetaRemainderTerm s hs_pos hs1
  have h_tele_summ : Summable (fun n : ℕ =>
      (((n + 1 : ℕ) : ℂ) ^ (1 - s) - ((n + 2 : ℕ) : ℂ) ^ (1 - s)) / (s - 1)) := by
    have h_eq : (fun n : ℕ =>
        (((n + 1 : ℕ) : ℂ) ^ (1 - s) - ((n + 2 : ℕ) : ℂ) ^ (1 - s)) / (s - 1)) =
        fun n : ℕ => ((n + 1 : ℕ) : ℂ) ^ (-s) - zetaRemainderTerm s n := by
      ext n
      unfold zetaRemainderTerm
      ring
    rw [h_eq]
    exact hsum_zeta.summable.sub h_rem_summ
  have h_tele_has : HasSum (fun n : ℕ =>
      (((n + 1 : ℕ) : ℂ) ^ (1 - s) - ((n + 2 : ℕ) : ℂ) ^ (1 - s)) / (s - 1))
      (1 / (s - 1)) := by
    rw [h_tele_summ.hasSum_iff_tendsto_nat]
    have h_sum_eq : ∀ N : ℕ,
        (∑ n ∈ Finset.range N,
          (((n + 1 : ℕ) : ℂ) ^ (1 - s) - ((n + 2 : ℕ) : ℂ) ^ (1 - s)) / (s - 1)) =
          (1 - ((N + 1 : ℕ) : ℂ) ^ (1 - s)) / (s - 1) := by
      intro N
      induction N with
      | zero => simp
      | succ N ih =>
        rw [Finset.sum_range_succ, ih]
        have hcast : ((N + 1 + 1 : ℕ) : ℂ) = ((N + 2 : ℕ) : ℂ) := by push_cast; ring
        rw [hcast]
        ring
    simp_rw [h_sum_eq]
    have h_tail : Tendsto (fun N : ℕ => ((N + 1 : ℕ) : ℂ) ^ (1 - s)) atTop (nhds 0) := by
      rw [tendsto_zero_iff_norm_tendsto_zero]
      have heq_norm : (fun N : ℕ => ‖((N + 1 : ℕ) : ℂ) ^ (1 - s)‖) =
          fun N : ℕ => ((N + 1 : ℝ) ^ (-(s.re - 1))) := by
        ext N
        have hN : (0 : ℝ) < (N + 1 : ℝ) := by positivity
        have hcast : (((N + 1 : ℕ) : ℂ)) = ((N + 1 : ℝ) : ℂ) := by push_cast; rfl
        rw [hcast, Complex.norm_cpow_eq_rpow_re_of_pos hN]
        congr 1
        simp only [Complex.sub_re, Complex.one_re]
        ring
      rw [heq_norm]
      have h_pos_exp : 0 < s.re - 1 := by linarith
      exact (tendsto_rpow_neg_atTop h_pos_exp).comp
        (tendsto_natCast_atTop_atTop.atTop_add tendsto_const_nhds)
    have h_lim := ((tendsto_const_nhds (x := (1 : ℂ))).sub h_tail).div_const (s - 1)
    simpa [sub_zero] using h_lim
  have h_diff_has := hsum_zeta.sub h_tele_has
  have h_eq_rem : (fun n : ℕ => ((n + 1 : ℕ) : ℂ) ^ (-s) -
      (((n + 1 : ℕ) : ℂ) ^ (1 - s) - ((n + 2 : ℕ) : ℂ) ^ (1 - s)) / (s - 1)) =
      zetaRemainderTerm s := rfl
  rw [h_eq_rem] at h_diff_has
  have h_tsum := h_diff_has.tsum_eq
  linear_combination -h_tsum

private lemma convex_linear_gt_zfr (f : ℂ →ₗ[ℝ] ℝ) (r : ℝ) : Convex ℝ {s : ℂ | r < f s} := by
  intro x hx y hy a b ha hb hab
  simp only [Set.mem_ofPred_eq, map_add, map_smul, smul_eq_mul] at hx hy ⊢
  by_cases ha0 : 0 < a
  · calc r = a * r + b * r := by rw [← add_mul, hab, one_mul]
      _ < a * f x + b * f y := add_lt_add_of_lt_of_le
          (mul_lt_mul_of_pos_left hx ha0) (mul_le_mul_of_nonneg_left hy.le hb)
  · have ha0' : a = 0 := le_antisymm (not_lt.mp ha0) ha
    have hb1 : b = 1 := by linarith
    rw [ha0', hb1]
    linarith

private lemma convex_linear_lt_zfr (f : ℂ →ₗ[ℝ] ℝ) (r : ℝ) : Convex ℝ {s : ℂ | f s < r} := by
  simpa [neg_lt_neg_iff] using convex_linear_gt_zfr (-f) (-r)

private lemma riemannZeta_eq_one_div_sub_add_tsum {s : ℂ} (hs_pos : 0 < s.re) (hs_im : s.im ≠ 0) :
    riemannZeta s = 1 / (s - 1) + ∑' n : ℕ, zetaRemainderTerm s n := by
  let S : Set ℂ := {z : ℂ | 0 < z.re ∧ z ≠ 1}
  let F : ℂ → ℂ := fun z => riemannZeta z - (1 / (z - 1) + ∑' n : ℕ, zetaRemainderTerm z n)
  have hS_open : IsOpen S := (isOpen_lt continuous_const Complex.continuous_re).inter isOpen_ne
  have hF_ana : AnalyticOnNhd ℂ F S := by
    have h_zeta : AnalyticOnNhd ℂ riemannZeta S := by
      refine DifferentiableOn.analyticOnNhd (fun z hz => ?_) hS_open
      exact (differentiableAt_riemannZeta hz.2).differentiableWithinAt
    have h_inv : AnalyticOnNhd ℂ (fun z : ℂ => 1 / (z - 1)) S := by
      refine DifferentiableOn.analyticOnNhd (fun z hz => ?_) hS_open
      exact ((differentiableAt_const (1 : ℂ)).div
        (differentiableAt_id.sub (differentiableAt_const 1))
        (sub_ne_zero.mpr hz.2)).differentiableWithinAt
    exact h_zeta.sub (h_inv.add differentiableOn_tsum_zetaRemainderTerm)
  let U_top : Set ℂ := {z : ℂ | 0 < z.re ∧ 0 < z.im}
  let U_bot : Set ℂ := {z : ℂ | 0 < z.re ∧ z.im < 0}
  have hU_top_sub : U_top ⊆ S := fun z ⟨hz_re, hz_im⟩ =>
    ⟨hz_re, fun h1 => by subst h1; simp at hz_im⟩
  have hU_bot_sub : U_bot ⊆ S := fun z ⟨hz_re, hz_im⟩ =>
    ⟨hz_re, fun h1 => by subst h1; simp at hz_im⟩
  have hU_top_open : IsOpen U_top :=
    (isOpen_lt continuous_const Complex.continuous_re).inter
      (isOpen_lt continuous_const Complex.continuous_im)
  have hU_bot_open : IsOpen U_bot :=
    (isOpen_lt continuous_const Complex.continuous_re).inter
      (isOpen_lt Complex.continuous_im continuous_const)
  have hF_top_ana : AnalyticOnNhd ℂ F U_top := hF_ana.mono hU_top_sub
  have hF_bot_ana : AnalyticOnNhd ℂ F U_bot := hF_ana.mono hU_bot_sub
  have h_right_open : IsOpen {z : ℂ | 1 < z.re} :=
    isOpen_lt continuous_const Complex.continuous_re
  have hF_zero_right : ∀ z : ℂ, 1 < z.re → F z = 0 := fun z hz => by
    dsimp [F]
    rw [riemannZeta_eq_one_div_sub_add_tsum_of_one_lt_re hz, sub_self]
  have hU_top_pre : IsPreconnected U_top :=
    ((convex_linear_gt_zfr Complex.reCLM 0).inter
      (convex_linear_gt_zfr Complex.imCLM 0)).isPreconnected
  have hU_bot_pre : IsPreconnected U_bot :=
    ((convex_linear_gt_zfr Complex.reCLM 0).inter
      (convex_linear_lt_zfr Complex.imCLM 0)).isPreconnected
  have hz_top_mem : (2 : ℂ) + I ∈ U_top := by simp [U_top]
  have hz_bot_mem : (2 : ℂ) - I ∈ U_bot := by simp [U_bot]
  have hF_top_ev : F =ᶠ[𝓝 ((2 : ℂ) + I)] 0 := by
    refine Filter.eventually_of_mem (h_right_open.mem_nhds (by norm_num : 1 < ((2 : ℂ) + I).re)) ?_
    intro z hz; exact hF_zero_right z hz
  have hF_bot_ev : F =ᶠ[𝓝 ((2 : ℂ) - I)] 0 := by
    refine Filter.eventually_of_mem (h_right_open.mem_nhds (by norm_num : 1 < ((2 : ℂ) - I).re)) ?_
    intro z hz; exact hF_zero_right z hz
  rcases lt_or_gt_of_ne hs_im with him_neg | him_pos
  · have h_eq := hF_bot_ana.eqOn_zero_of_preconnected_of_eventuallyEq_zero
      hU_bot_pre hz_bot_mem hF_bot_ev
    have hs_mem : s ∈ U_bot := ⟨hs_pos, him_neg⟩
    have hFz := h_eq hs_mem
    dsimp [F] at hFz
    exact sub_eq_zero.mp hFz
  · have h_eq := hF_top_ana.eqOn_zero_of_preconnected_of_eventuallyEq_zero
      hU_top_pre hz_top_mem hF_top_ev
    have hs_mem : s ∈ U_top := ⟨hs_pos, him_pos⟩
    have hFz := h_eq hs_mem
    dsimp [F] at hFz
    exact sub_eq_zero.mp hFz

private lemma riemannZeta_partial_summation (M : ℕ) {s : ℂ} (hs_pos : 0 < s.re) (hs_im : s.im ≠ 0) :
    riemannZeta s =
      (∑ n ∈ Finset.range M, ((n + 1 : ℕ) : ℂ) ^ (-s)) +
        ((M + 1 : ℕ) : ℂ) ^ (1 - s) / (s - 1) +
        ∑' n : ℕ, zetaRemainderTerm s (n + M) := by
  have hs1 : s ≠ 1 := fun h => hs_im (by rw [h]; simp)
  have h_fin : 1 / (s - 1) + ∑ n ∈ Finset.range M, zetaRemainderTerm s n =
      (∑ n ∈ Finset.range M, ((n + 1 : ℕ) : ℂ) ^ (-s)) +
        ((M + 1 : ℕ) : ℂ) ^ (1 - s) / (s - 1) := by
    induction M with
    | zero => simp
    | succ M ih =>
      rw [Finset.sum_range_succ, ← add_assoc, ih, Finset.sum_range_succ]
      unfold zetaRemainderTerm
      have hcast : ((M + 1 + 1 : ℕ) : ℂ) = ((M + 2 : ℕ) : ℂ) := by push_cast; ring
      rw [hcast]
      ring
  rw [riemannZeta_eq_one_div_sub_add_tsum hs_pos hs_im]
  have h_split := (summable_zetaRemainderTerm s hs_pos hs1).sum_add_tsum_nat_add M
  rw [← h_split, ← add_assoc, h_fin]

private lemma tsum_rpow_neg_sub_one_le (M : ℕ) {σ : ℝ} (hσ : 0 < σ) :
    ∑' n : ℕ, ((n + M + 1 : ℝ) ^ (-σ - 1)) ≤
      (M + 1 : ℝ) ^ (-σ - 1) + (M + 1 : ℝ) ^ (-σ) / σ := by
  have h_summ : Summable (fun n : ℕ => ((n + M + 1 : ℝ) ^ (-σ - 1))) := by
    have h1 : 1 < σ + 1 := by linarith
    have h_raw := (summable_nat_add_iff (M + 1)).mpr (Real.summable_nat_rpow_inv.mpr h1)
    refine h_raw.congr fun n => ?_
    push_cast
    rw [← Real.rpow_neg (by positivity)]
    ring_nf
  refine h_summ.tsum_le_of_sum_range_le fun N => ?_
  cases N with
  | zero => simp only [Finset.range_zero, Finset.sum_empty]; positivity
  | succ N =>
    rw [Finset.sum_range_eq_add_Ico _ (Nat.succ_pos N)]
    simp only [Nat.cast_zero, zero_add]
    gcongr
    have h_step : ∀ k ∈ Finset.Ico 1 (N + 1),
        ((k + M + 1 : ℝ) ^ (-σ - 1)) ≤
          ∫ x in ((k + M : ℕ) : ℝ)..((k + M + 1 : ℕ) : ℝ), x ^ (-σ - 1) := by
      intro k hk
      have hk1 : 1 ≤ k := (Finset.mem_Ico.mp hk).1
      have ha_pos : (0 : ℝ) < (k + M : ℕ) := by positivity
      have hab : ((k + M : ℕ) : ℝ) ≤ ((k + M + 1 : ℕ) : ℝ) := by push_cast; linarith
      have hint : IntervalIntegrable (fun x : ℝ => x ^ (-σ - 1))
          MeasureTheory.volume ((k + M : ℕ) : ℝ) ((k + M + 1 : ℕ) : ℝ) := by
        rw [intervalIntegrable_iff_integrableOn_Icc_of_le hab]
        refine (ContinuousOn.rpow_const continuousOn_id fun x hx =>
          Or.inl (lt_of_lt_of_le ha_pos hx.1).ne').integrableOn_Icc
      have h_le : ∀ x ∈ Icc ((k + M : ℕ) : ℝ) ((k + M + 1 : ℕ) : ℝ),
          ((k + M + 1 : ℝ) ^ (-σ - 1)) ≤ x ^ (-σ - 1) := by
        intro x hx
        have hx_pos : 0 < x := lt_of_lt_of_le ha_pos hx.1
        have hx_le : x ≤ k + M + 1 := by exact_mod_cast hx.2
        exact Real.rpow_le_rpow_of_nonpos hx_pos hx_le (by linarith)
      have h_int := intervalIntegral.integral_mono_on hab intervalIntegrable_const hint fun x hx =>
        h_le x hx
      simpa [intervalIntegral.integral_const, Nat.cast_add, Nat.cast_one] using h_int
    calc ∑ k ∈ Finset.Ico 1 (N + 1), ((k + M + 1 : ℝ) ^ (-σ - 1))
        ≤ ∑ k ∈ Finset.Ico 1 (N + 1),
            ∫ x in ((k + M : ℕ) : ℝ)..((k + M + 1 : ℕ) : ℝ), x ^ (-σ - 1) :=
          Finset.sum_le_sum h_step
      _ = ∑ k ∈ Finset.Ico 1 (N + 1),
            ∫ x in (M + (k : ℕ) : ℝ)..(M + ((k + 1 : ℕ) : ℝ)), x ^ (-σ - 1) := by
          refine Finset.sum_congr rfl fun k _ => ?_
          push_cast; ring_nf
      _ = ∫ x in (M + (1 : ℕ) : ℝ)..(M + ((N + 1 : ℕ) : ℝ)), x ^ (-σ - 1) := by
          refine intervalIntegral.sum_integral_adjacent_intervals_Ico (Nat.le_add_left 1 N) ?_
          intro k _
          have ha_pos : (0 : ℝ) < (M : ℝ) + k := by
            have hk1 : 1 ≤ k := by grind
            positivity
          have hab : (M : ℝ) + k ≤ (M : ℝ) + (k + 1 : ℕ) := by push_cast; linarith
          rw [intervalIntegrable_iff_integrableOn_Icc_of_le hab]
          refine (ContinuousOn.rpow_const continuousOn_id fun x hx =>
            Or.inl (lt_of_lt_of_le ha_pos hx.1).ne').integrableOn_Icc
      _ ≤ (M + 1 : ℝ) ^ (-σ) / σ := by
          have ha_pos : (0 : ℝ) < (M : ℝ) + (1 : ℕ) := by positivity
          have hab : (M : ℝ) + (1 : ℕ) ≤ (M : ℝ) + (N + 1 : ℕ) := by push_cast; linarith
          have h0_not : (0 : ℝ) ∉ uIcc ((M : ℝ) + (1 : ℕ)) ((M : ℝ) + (N + 1 : ℕ)) := by
            rw [uIcc_of_le hab, mem_Icc]
            intro h0
            linarith [h0.1]
          rw [integral_rpow (Or.inr ⟨by linarith, h0_not⟩)]
          have h_exp : -σ - 1 + 1 = -σ := by ring
          rw [h_exp]
          have h_nn : (0 : ℝ) ≤ ((M : ℝ) + (N + 1 : ℕ)) ^ (-σ) := by positivity
          have h_eq1 : ((((M : ℝ) + (N + 1 : ℕ)) ^ (-σ) - ((M : ℝ) + (1 : ℕ)) ^ (-σ)) / (-σ)) =
              (((M + 1 : ℝ) ^ (-σ) - ((M : ℝ) + (N + 1 : ℕ)) ^ (-σ)) / σ) := by
            push_cast; field_simp; ring
          rw [h_eq1]
          exact div_le_div_of_nonneg_right (sub_le_self _ h_nn) hσ.le

/-- Unconditional logarithmic growth bound in the boundary strip
`1 - 1 / (2 * ln(|s.im| + 2)) ≤ s.re ≤ 2` for `3 / 2 ≤ |s.im|`. -/
theorem norm_riemannZeta_le_of_log_strip {s : ℂ} (ht : 3 / 2 ≤ |s.im|)
    (hre_lo : 1 - 1 / (2 * Real.log (|s.im| + 2)) ≤ s.re) (hre_hi : s.re ≤ 2) :
    ‖riemannZeta s‖ ≤ (10 * Real.exp 1 + 3) * Real.log (|s.im| + 2) := by
  have hlog_gt_one : 1 < Real.log (|s.im| + 2) := by
    rw [← Real.log_exp 1]
    exact Real.log_lt_log (Real.exp_pos 1) (lt_of_lt_of_le Real.exp_one_lt_three (by linarith))
  have hlog_pos : 0 < Real.log (|s.im| + 2) := by linarith
  have hs_re_gt_half : 1 / 2 < s.re := by
    have h1 : 1 / (2 * Real.log (|s.im| + 2)) < 1 / 2 := by
      rw [div_lt_div_iff₀ (by positivity) (by norm_num)]
      linarith
    linarith
  have hs_pos : 0 < s.re := by linarith
  have hs_im : s.im ≠ 0 := by
    intro h0
    rw [h0, abs_zero] at ht
    linarith
  have hs1 : s ≠ 1 := fun h => hs_im (by rw [h]; simp)
  let M : ℕ := Nat.floor |s.im| + 1
  have hM_ge : 1 ≤ M := by omega
  have hM_le : (M : ℝ) ≤ |s.im| + 1 := by
    dsimp [M]
    push_cast
    linarith [Nat.floor_le (abs_nonneg s.im)]
  have hM_gt : |s.im| < (M : ℝ) := by
    dsimp [M]
    push_cast
    exact Nat.lt_floor_add_one |s.im|
  have hM1_le : (M + 1 : ℝ) ≤ |s.im| + 2 := by linarith
  have h_pow_exp : ∀ x : ℝ, 1 ≤ x → x ≤ |s.im| + 2 → x ^ (1 - s.re) ≤ Real.exp 1 := by
    intro x hx1 hx_le
    by_cases hs_ge1 : 1 ≤ s.re
    · exact (Real.rpow_le_one_of_one_le_of_nonpos hx1 (by linarith)).trans
        (by exact Real.one_le_exp (by norm_num))
    · have hexp_nn : 0 ≤ 1 - s.re := by linarith
      have hx_pos : 0 < x := by linarith
      rw [Real.rpow_def_of_pos hx_pos, Real.exp_le_exp]
      have hlogx : Real.log x ≤ Real.log (|s.im| + 2) := Real.log_le_log hx_pos hx_le
      have hdiff_le : 1 - s.re ≤ 1 / Real.log (|s.im| + 2) := by
        have hhalf : 1 / (2 * Real.log (|s.im| + 2)) ≤ 1 / Real.log (|s.im| + 2) :=
          div_le_div_of_nonneg_left zero_le_one hlog_pos (by linarith)
        linarith
      calc Real.log x * (1 - s.re)
          ≤ Real.log (|s.im| + 2) * (1 - s.re) :=
            mul_le_mul_of_nonneg_right hlogx hexp_nn
        _ ≤ Real.log (|s.im| + 2) * (1 / Real.log (|s.im| + 2)) :=
            mul_le_mul_of_nonneg_left hdiff_le hlog_pos.le
        _ = 1 := mul_one_div_cancel hlog_pos.ne'
  rw [riemannZeta_partial_summation M hs_pos hs_im]
  have h_sum_bound : ‖∑ n ∈ Finset.range M, ((n + 1 : ℕ) : ℂ) ^ (-s)‖ ≤
      Real.exp 1 * (2 * Real.log (|s.im| + 2)) := by
    have h1 : ‖∑ n ∈ Finset.range M, ((n + 1 : ℕ) : ℂ) ^ (-s)‖ ≤
        ∑ n ∈ Finset.range M, ‖((n + 1 : ℕ) : ℂ) ^ (-s)‖ := norm_sum_le _ _
    have h2 : ∑ n ∈ Finset.range M, ‖((n + 1 : ℕ) : ℂ) ^ (-s)‖ ≤
        Real.exp 1 * ∑ n ∈ Finset.range M, ((n + 1 : ℝ)⁻¹) := by
      rw [Finset.mul_sum]
      refine Finset.sum_le_sum fun n hn => ?_
      have hn_lt : n < M := Finset.mem_range.mp hn
      have hn1_pos : (0 : ℝ) < (n + 1 : ℝ) := by positivity
      have hn1_ge1 : (1 : ℝ) ≤ (n + 1 : ℝ) := by exact_mod_cast Nat.succ_pos n
      have hn1_le : (n + 1 : ℝ) ≤ |s.im| + 2 := by
        have h_nat : (n + 1 : ℝ) ≤ (M : ℝ) := by exact_mod_cast hn_lt
        linarith
      rw [Nat.cast_add, Nat.cast_one, ← Complex.ofReal_natCast, ← Complex.ofReal_one,
        ← Complex.ofReal_add, Complex.norm_cpow_eq_rpow_re_of_pos hn1_pos, Complex.neg_re]
      have h_split : (n + 1 : ℝ) ^ (-s.re) = (n + 1 : ℝ) ^ (1 - s.re) * (n + 1 : ℝ)⁻¹ := by
        have heq : -s.re = (1 - s.re) + (-1) := by ring
        rw [heq, Real.rpow_add hn1_pos, Real.rpow_neg_one]
      rw [h_split]
      exact mul_le_mul_of_nonneg_right (h_pow_exp (n + 1) hn1_ge1 hn1_le) (by positivity)
    have h_harm : ∑ n ∈ Finset.range M, ((n + 1 : ℝ)⁻¹) ≤ 2 * Real.log (|s.im| + 2) := by
      have h_eq : ∑ n ∈ Finset.range M, ((n + 1 : ℝ)⁻¹) = (harmonic M : ℝ) := by
        simp [harmonic, Rat.cast_sum, Rat.cast_inv, Rat.cast_natCast]
      rw [h_eq]
      have h_le1 : (harmonic M : ℝ) ≤ 1 + Real.log M := harmonic_le_one_add_log M
      have h_le2 : Real.log (M : ℝ) ≤ Real.log (|s.im| + 2) :=
        Real.log_le_log (by exact_mod_cast hM_ge) (by linarith)
      linarith
    exact h1.trans (h2.trans (mul_le_mul_of_nonneg_left h_harm (Real.exp_pos 1).le))
  have h_bdry_bound : ‖((M + 1 : ℕ) : ℂ) ^ (1 - s) / (s - 1)‖ ≤ Real.exp 1 := by
    have hM1_pos : (0 : ℝ) < (M + 1 : ℝ) := by positivity
    have hcast : (((M + 1 : ℕ) : ℂ)) = ((M + 1 : ℝ) : ℂ) := by push_cast; rfl
    rw [norm_div, hcast, Complex.norm_cpow_eq_rpow_re_of_pos hM1_pos,
      Complex.sub_re, Complex.one_re]
    have h_num : (M + 1 : ℝ) ^ (1 - s.re) ≤ Real.exp 1 :=
      h_pow_exp (M + 1) (by linarith) hM1_le
    have h_den : 1 ≤ ‖s - 1‖ := by
      calc (1 : ℝ) ≤ 3 / 2 := by norm_num
        _ ≤ |s.im| := ht
        _ = |(s - 1).im| := by simp
        _ ≤ ‖s - 1‖ := Complex.abs_im_le_norm (s - 1)
    exact (div_le_self (by positivity) h_den).trans h_num
  have h_tail_bound : ‖∑' n : ℕ, zetaRemainderTerm s (n + M)‖ ≤ 3 + 6 * Real.exp 1 := by
    have h_summ : Summable (fun n : ℕ => zetaRemainderTerm s (n + M)) :=
      (summable_zetaRemainderTerm s hs_pos hs1).comp_injective (add_left_injective M)
    have h1 : ‖∑' n : ℕ, zetaRemainderTerm s (n + M)‖ ≤
        ∑' n : ℕ, ‖zetaRemainderTerm s (n + M)‖ := norm_tsum_le_tsum_norm h_summ.norm
    have h2 : ∑' n : ℕ, ‖zetaRemainderTerm s (n + M)‖ ≤
        ‖s‖ * ∑' n : ℕ, ((n + M + 1 : ℝ) ^ (-s.re - 1)) := by
      rw [← tsum_mul_left]
      have h_rhs_summ : Summable (fun n : ℕ => ‖s‖ * ((n + M + 1 : ℝ) ^ (-s.re - 1))) := by
        have h1' : 1 < s.re + 1 := by linarith
        have h_raw := (summable_nat_add_iff (M + 1)).mpr (Real.summable_nat_rpow_inv.mpr h1')
        refine (h_raw.congr fun n => ?_).mul_left ‖s‖
        push_cast
        rw [← Real.rpow_neg (by positivity)]
        ring_nf
      refine Summable.tsum_le_tsum (fun n => ?_) h_summ.norm h_rhs_summ
      simpa [Nat.cast_add, Nat.cast_one, add_assoc] using
        norm_zetaRemainderTerm_le (n + M) hs_pos le_rfl le_rfl hs1
    have h3 := tsum_rpow_neg_sub_one_le M hs_pos
    have h_norm_s : ‖s‖ ≤ 3 * (M + 1 : ℝ) := by
      calc ‖s‖ ≤ |s.re| + |s.im| := Complex.norm_le_abs_re_add_abs_im s
        _ = s.re + |s.im| := by rw [abs_of_pos hs_pos]
        _ ≤ 2 + |s.im| := by linarith
        _ ≤ 3 * |s.im| := by linarith
        _ ≤ 3 * (M + 1 : ℝ) := by linarith
    have hM1_pos : (0 : ℝ) < (M + 1 : ℝ) := by positivity
    have h_prod1 : ‖s‖ * ((M + 1 : ℝ) ^ (-s.re - 1)) ≤ 3 := by
      have h_step : ‖s‖ * ((M + 1 : ℝ) ^ (-s.re - 1)) ≤
          (3 * (M + 1 : ℝ)) * ((M + 1 : ℝ) ^ (-s.re - 1)) :=
        mul_le_mul_of_nonneg_right h_norm_s (by positivity)
      have h_pow_eq : (3 * (M + 1 : ℝ)) * ((M + 1 : ℝ) ^ (-s.re - 1)) =
          3 * ((M + 1 : ℝ) ^ (-s.re)) := by
        have heq : (M + 1 : ℝ) * ((M + 1 : ℝ) ^ (-s.re - 1)) = (M + 1 : ℝ) ^ (-s.re) := by
          have h1p : (M + 1 : ℝ) = (M + 1 : ℝ) ^ (1 : ℝ) := (Real.rpow_one _).symm
          calc (M + 1 : ℝ) * ((M + 1 : ℝ) ^ (-s.re - 1))
              = (M + 1 : ℝ) ^ (1 : ℝ) * ((M + 1 : ℝ) ^ (-s.re - 1)) := by rw [← h1p]
            _ = (M + 1 : ℝ) ^ (1 + (-s.re - 1)) := (Real.rpow_add hM1_pos _ _).symm
            _ = (M + 1 : ℝ) ^ (-s.re) := by ring_nf
        rw [mul_assoc, heq]
      have h_le_one : (M + 1 : ℝ) ^ (-s.re) ≤ 1 :=
        Real.rpow_le_one_of_one_le_of_nonpos (by linarith) (by linarith)
      linarith
    have h_prod2 : ‖s‖ * ((M + 1 : ℝ) ^ (-s.re) / s.re) ≤ 6 * Real.exp 1 := by
      have h_step : ‖s‖ * ((M + 1 : ℝ) ^ (-s.re) / s.re) ≤
          (3 * (M + 1 : ℝ)) * ((M + 1 : ℝ) ^ (-s.re) / (1 / 2)) := by
        refine mul_le_mul h_norm_s ?_ (by positivity) (by positivity)
        exact div_le_div_of_nonneg_left (by positivity) (by norm_num) hs_re_gt_half.le
      have h_eq : (3 * (M + 1 : ℝ)) * ((M + 1 : ℝ) ^ (-s.re) / (1 / 2)) =
          6 * ((M + 1 : ℝ) ^ (1 - s.re)) := by
        have heq : (M + 1 : ℝ) * ((M + 1 : ℝ) ^ (-s.re)) = (M + 1 : ℝ) ^ (1 - s.re) := by
          have h1p : (M + 1 : ℝ) = (M + 1 : ℝ) ^ (1 : ℝ) := (Real.rpow_one _).symm
          calc (M + 1 : ℝ) * ((M + 1 : ℝ) ^ (-s.re))
              = (M + 1 : ℝ) ^ (1 : ℝ) * ((M + 1 : ℝ) ^ (-s.re)) := by rw [← h1p]
            _ = (M + 1 : ℝ) ^ (1 + (-s.re)) := (Real.rpow_add hM1_pos _ _).symm
            _ = (M + 1 : ℝ) ^ (1 - s.re) := by ring_nf
        have hdiv : ((M + 1 : ℝ) ^ (-s.re)) / (1 / 2) = 2 * ((M + 1 : ℝ) ^ (-s.re)) := by ring
        rw [hdiv, show (3 * (M + 1 : ℝ)) * (2 * ((M + 1 : ℝ) ^ (-s.re))) =
          6 * ((M + 1 : ℝ) * ((M + 1 : ℝ) ^ (-s.re))) by ring, heq]
      have h_exp := h_pow_exp (M + 1) (by linarith) hM1_le
      linarith
    calc ‖∑' n : ℕ, zetaRemainderTerm s (n + M)‖
        ≤ ‖s‖ * ∑' n : ℕ, ((n + M + 1 : ℝ) ^ (-s.re - 1)) := h1.trans h2
      _ ≤ ‖s‖ * ((M + 1 : ℝ) ^ (-s.re - 1) + (M + 1 : ℝ) ^ (-s.re) / s.re) :=
          mul_le_mul_of_nonneg_left h3 (norm_nonneg s)
      _ = ‖s‖ * ((M + 1 : ℝ) ^ (-s.re - 1)) + ‖s‖ * ((M + 1 : ℝ) ^ (-s.re) / s.re) := mul_add _ _ _
      _ ≤ 3 + 6 * Real.exp 1 := add_le_add h_prod1 h_prod2
  have h_tri1 := norm_add_le
    ((∑ n ∈ Finset.range M, ((n + 1 : ℕ) : ℂ) ^ (-s)) + ((M + 1 : ℕ) : ℂ) ^ (1 - s) / (s - 1))
    (∑' n : ℕ, zetaRemainderTerm s (n + M))
  have h_tri2 := norm_add_le
    (∑ n ∈ Finset.range M, ((n + 1 : ℕ) : ℂ) ^ (-s))
    (((M + 1 : ℕ) : ℂ) ^ (1 - s) / (s - 1))
  have h_comb : ‖(∑ n ∈ Finset.range M, ((n + 1 : ℕ) : ℂ) ^ (-s)) +
      ((M + 1 : ℕ) : ℂ) ^ (1 - s) / (s - 1) +
      ∑' n : ℕ, zetaRemainderTerm s (n + M)‖ ≤
      2 * Real.exp 1 * Real.log (|s.im| + 2) + (7 * Real.exp 1 + 3) := by
    linarith
  have h_log_one : (7 * Real.exp 1 + 3) ≤ (8 * Real.exp 1 + 3) * Real.log (|s.im| + 2) := by
    have h1 : (7 * Real.exp 1 + 3) ≤ (7 * Real.exp 1 + 3) * Real.log (|s.im| + 2) :=
      le_mul_of_one_le_right (by positivity) hlog_gt_one.le
    have h2 : (7 * Real.exp 1 + 3) * Real.log (|s.im| + 2) ≤
        (8 * Real.exp 1 + 3) * Real.log (|s.im| + 2) :=
      mul_le_mul_of_nonneg_right (by linarith [Real.exp_pos 1]) hlog_pos.le
    exact h1.trans h2
  linarith

/-- Unconditional horizontal Lipschitz bound for `riemannZeta` from Cauchy's integral estimate
and the strip logarithmic growth bound, when `riemannZeta (1 - δ + I * y) = 0` with
`0 < δ ≤ 1 / (8 * ln(|y| + 2))` and `2 ≤ |y|`. -/
theorem riemannZeta_horizontal_lipschitz_of_zero {δ y : ℝ} (hy : 2 ≤ |y|)
    (hδ_pos : 0 < δ) (hδ_le : δ ≤ 1 / (8 * Real.log (|y| + 2)))
    (hz : riemannZeta (1 - (δ : ℂ) + I * (y : ℂ)) = 0) :
    ‖riemannZeta (1 + (3 * δ : ℂ) + I * (y : ℂ))‖ ≤
      (16 * (10 * Real.exp 1 + 3)) * Real.log (|y| + 2) ^ 2 * (4 * δ) := by
  have hlog_gt_one : 1 < Real.log (|y| + 2) := by
    rw [← Real.log_exp 1]
    exact Real.log_lt_log (Real.exp_pos 1) (lt_of_lt_of_le Real.exp_one_lt_three (by linarith))
  have hlog_pos : 0 < Real.log (|y| + 2) := by linarith
  let R : ℝ := 1 / (8 * Real.log (|y| + 2))
  have hR_pos : 0 < R := by dsimp [R]; positivity
  have hR_lt : R < 1 / 8 := by
    dsimp [R]
    rw [div_lt_div_iff₀ (by positivity) (by norm_num)]
    linarith
  let C_strip : ℝ := 10 * Real.exp 1 + 3
  let C_lip : ℝ := 16 * C_strip
  let z₁ : ℂ := 1 - (δ : ℂ) + I * (y : ℂ)
  let z₂ : ℂ := 1 + ((3 * δ : ℝ) : ℂ) + I * (y : ℂ)
  let S_seg : Set ℂ := {z : ℂ | 1 - δ ≤ z.re ∧ z.re ≤ 1 + 3 * δ ∧ z.im = y}
  have hS_conv : Convex ℝ S_seg := by
    intro a ha b hb u v hu hv huv
    simp only [S_seg, Set.mem_ofPred_eq, Complex.add_re, Complex.real_smul, Complex.mul_re,
      Complex.ofReal_re, Complex.ofReal_im, Complex.add_im, Complex.mul_im] at ha hb ⊢
    refine ⟨?_, ?_, ?_⟩
    · have h1 : u * (1 - δ) + v * (1 - δ) = 1 - δ := by rw [← add_mul, huv, one_mul]
      nlinarith [ha.1, hb.1]
    · have h2 : u * (1 + 3 * δ) + v * (1 + 3 * δ) = 1 + 3 * δ := by rw [← add_mul, huv, one_mul]
      nlinarith [ha.2.1, hb.2.1]
    · simp only [ha.2.2, hb.2.2, zero_mul, add_zero]
      calc u * y + v * y = (u + v) * y := by ring
        _ = y := by rw [huv, one_mul]
  have hw_log_bound : ∀ z ∈ S_seg, ∀ w ∈ Metric.closedBall z R,
      (3 / 2 ≤ |w.im| ∧ 1 - 1 / (2 * Real.log (|w.im| + 2)) ≤ w.re ∧ w.re ≤ 2) ∧
        Real.log (|w.im| + 2) ≤ 2 * Real.log (|y| + 2) := by
    intro z hzS w hw
    have hw_dist : ‖w - z‖ ≤ R := by rwa [Metric.mem_closedBall, dist_eq_norm] at hw
    have hw_re_diff : |w.re - z.re| ≤ R := by
      have : |w.re - z.re| = |(w - z).re| := by simp
      rw [this]
      exact (Complex.abs_re_le_norm (w - z)).trans hw_dist
    have hw_im_diff : |w.im - z.im| ≤ R := by
      have : |w.im - z.im| = |(w - z).im| := by simp
      rw [this]
      exact (Complex.abs_im_le_norm (w - z)).trans hw_dist
    have hw_im_eq : |w.im - y| ≤ R := by rwa [hzS.2.2] at hw_im_diff
    have hw_im_lo : 3 / 2 ≤ |w.im| := by
      have h1 : |y| - |w.im| ≤ |w.im - y| := by
        simpa [abs_sub_comm] using abs_sub_abs_le_abs_sub y w.im
      linarith
    have hw_im_hi : |w.im| ≤ |y| + 1 / 4 := by
      have h1 : |w.im| - |y| ≤ |w.im - y| := abs_sub_abs_le_abs_sub w.im y
      linarith
    have hlog_w_le : Real.log (|w.im| + 2) ≤ 2 * Real.log (|y| + 2) := by
      have h1 : |w.im| + 2 ≤ 2 * (|y| + 2) := by linarith
      have h2 : Real.log (|w.im| + 2) ≤ Real.log (2 * (|y| + 2)) :=
        Real.log_le_log (by positivity) h1
      have h3 : Real.log (2 * (|y| + 2)) = Real.log 2 + Real.log (|y| + 2) :=
        Real.log_mul (by norm_num) (by positivity)
      have h4 : Real.log 2 ≤ Real.log (|y| + 2) := Real.log_le_log (by norm_num) (by linarith)
      linarith
    have hlog_w_pos : 0 < Real.log (|w.im| + 2) := by
      have : 1 < |w.im| + 2 := by linarith
      exact Real.log_pos this
    have hre_lo : 1 - 1 / (2 * Real.log (|w.im| + 2)) ≤ w.re := by
      have hz_re_lo : 1 - δ ≤ z.re := hzS.1
      have hw_re_ge : z.re - R ≤ w.re := by linarith [(abs_sub_le_iff.mp hw_re_diff).2]
      have h_inv_le : 1 / (4 * Real.log (|y| + 2)) ≤ 1 / (2 * Real.log (|w.im| + 2)) := by
        rw [div_le_div_iff₀ (by positivity) (by positivity)]
        linarith
      have hR_sum : 1 / (8 * Real.log (|y| + 2)) + R = 1 / (4 * Real.log (|y| + 2)) := by
        dsimp [R]; ring
      have h_sum_R : δ + R ≤ 1 / (4 * Real.log (|y| + 2)) := by linarith
      linarith
    have hre_hi : w.re ≤ 2 := by
      have hz_re_hi : z.re ≤ 1 + 3 * δ := hzS.2.1
      have hw_re_le : w.re ≤ z.re + R := by linarith [(abs_sub_le_iff.mp hw_re_diff).1]
      have hδ_small : δ ≤ 1 / 8 := hδ_le.trans (by
        rw [div_le_div_iff₀ (by positivity) (by norm_num)]
        linarith)
      linarith
    exact ⟨⟨hw_im_lo, hre_lo, hre_hi⟩, hlog_w_le⟩
  have hz_diff : ∀ z ∈ S_seg, DifferentiableAt ℂ riemannZeta z := fun z hzS => by
    apply differentiableAt_riemannZeta
    intro h1
    have him := hzS.2.2
    rw [h1, Complex.one_im] at him
    rw [← him, abs_zero] at hy
    linarith
  have hz_deriv_bound : ∀ z ∈ S_seg, ‖deriv riemannZeta z‖ ≤ C_lip * Real.log (|y| + 2) ^ 2 := by
    intro z hzS
    have h_diff_cl : DiffContOnCl ℂ riemannZeta (Metric.ball z R) := by
      refine DifferentiableOn.diffContOnCl fun w hw => ?_
      rw [closure_ball z hR_pos.ne'] at hw
      have hw_im := (hw_log_bound z hzS w hw).1.1
      refine (differentiableAt_riemannZeta ?_).differentiableWithinAt
      intro h1
      rw [h1] at hw_im
      simp at hw_im
      linarith
    have h_sphere : ∀ w ∈ Metric.sphere z R,
        ‖riemannZeta w‖ ≤ (2 * C_strip) * Real.log (|y| + 2) := by
      intro w hw
      have hw_cb := Metric.sphere_subset_closedBall hw
      obtain ⟨⟨hw_im, hw_lo, hw_hi⟩, hlog_w_le⟩ := hw_log_bound z hzS w hw_cb
      have h_bound := norm_riemannZeta_le_of_log_strip hw_im hw_lo hw_hi
      have h_mul := mul_le_mul_of_nonneg_left hlog_w_le
        (show 0 ≤ C_strip by dsimp [C_strip]; positivity)
      dsimp [C_strip] at h_bound h_mul ⊢
      linarith
    have h_cauchy := norm_deriv_le_of_forall_mem_sphere_norm_le hR_pos h_diff_cl h_sphere
    have h_eq_rhs : (2 * C_strip) * Real.log (|y| + 2) / R =
        C_lip * Real.log (|y| + 2) ^ 2 := by
      dsimp [R, C_lip]
      field_simp [hlog_pos.ne']
      ring
    rwa [h_eq_rhs] at h_cauchy
  have hz₁_mem : z₁ ∈ S_seg := by
    simp only [S_seg, z₁, Set.mem_ofPred_eq]
    refine ⟨by simp, by simp; linarith, by simp⟩
  have hz₂_mem : z₂ ∈ S_seg := by
    simp only [S_seg, z₂, Set.mem_ofPred_eq]
    refine ⟨by simp; linarith, by simp, by simp⟩
  have h_mvt := hS_conv.norm_image_sub_le_of_norm_deriv_le hz_diff hz_deriv_bound hz₁_mem hz₂_mem
  have h_diff_eq : z₂ - z₁ = ((4 * δ : ℝ) : ℂ) := by
    dsimp [z₁, z₂]
    push_cast
    ring
  have hz_eq : riemannZeta z₁ = 0 := hz
  rw [hz_eq, sub_zero, h_diff_eq, norm_real, Real.norm_of_nonneg (by positivity)] at h_mvt
  have h_z2_eq : z₂ = 1 + (3 * δ : ℂ) + I * (y : ℂ) := by
    dsimp [z₂]; push_cast; ring
  rwa [← h_z2_eq]

/-- **De la Vallée Poussin's (1899) Unconditional Zero-Free Region Theorem**:
There exists an absolute constant `c > 0` such that `riemannZeta s ≠ 0` for all `s : ℂ` with
`2 ≤ |s.im|` and `1 - c / ln⁹(|s.im| + 2) < s.re`. -/
theorem deLaValleePoussin_zero_free_region_unconditional :
    ∃ c > 0, ∀ s : ℂ, 2 ≤ |s.im| →
      1 - c / Real.log (|s.im| + 2) ^ 9 < s.re → riemannZeta s ≠ 0 := by
  obtain ⟨C_pole, hC_pole, h_pole_all⟩ := exists_pole_bound_one_add
  let C_strip : ℝ := 10 * Real.exp 1 + 3
  let C_lip : ℝ := 16 * C_strip
  let C_growth : ℝ := 2 * C_strip
  have hC_strip : 0 < C_strip := by dsimp [C_strip]; positivity
  have hC_lip : 0 < C_lip := by dsimp [C_lip]; positivity
  have hC_growth : 0 < C_growth := by dsimp [C_growth]; positivity
  let c₀ : ℝ := 27 / (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth)
  have hc₀ : 0 < c₀ := by dsimp [c₀]; positivity
  let c : ℝ := min (1 / 8) c₀
  have hc : 0 < c := lt_min (by norm_num) hc₀
  refine ⟨c, hc, fun s ht h_reg h_zero => ?_⟩
  by_cases h_ge : 1 ≤ s.re
  · exact riemannZeta_ne_zero_of_one_le_re_strip h_ge h_zero
  · have h_lt : s.re < 1 := lt_of_not_ge h_ge
    let δ : ℝ := 1 - s.re
    have hδ_pos : 0 < δ := sub_pos.mpr h_lt
    have hlog_gt_one : 1 < Real.log (|s.im| + 2) := by
      rw [← Real.log_exp 1]
      exact Real.log_lt_log (Real.exp_pos 1) (lt_of_lt_of_le Real.exp_one_lt_three (by linarith))
    have hlog_pos : 0 < Real.log (|s.im| + 2) := by linarith
    have h_pow_ge : Real.log (|s.im| + 2) ≤ Real.log (|s.im| + 2) ^ 9 := by
      calc Real.log (|s.im| + 2)
          = Real.log (|s.im| + 2) ^ 1 := (pow_one _).symm
        _ ≤ Real.log (|s.im| + 2) ^ 9 :=
            pow_le_pow_right₀ hlog_gt_one.le (by norm_num)
    have hδ_lt_c : δ < c / Real.log (|s.im| + 2) ^ 9 := by
      dsimp [δ]; linarith
    have hδ_lt_c₀ : δ < c₀ / Real.log (|s.im| + 2) ^ 9 :=
      hδ_lt_c.trans_le (div_le_div_of_nonneg_right (min_le_right _ _) (by positivity))
    have hδ_le_log : δ ≤ 1 / (8 * Real.log (|s.im| + 2)) := by
      calc δ ≤ c / Real.log (|s.im| + 2) ^ 9 := hδ_lt_c.le
        _ ≤ (1 / 8) / Real.log (|s.im| + 2) ^ 9 :=
            div_le_div_of_nonneg_right (min_le_left _ _) (by positivity)
        _ ≤ (1 / 8) / Real.log (|s.im| + 2) :=
            div_le_div_of_nonneg_left (by norm_num) hlog_pos h_pow_ge
        _ = 1 / (8 * Real.log (|s.im| + 2)) := by ring
    have h3δ_pos : 0 < 3 * δ := by linarith
    have h3δ_le_one : 3 * δ ≤ 1 := by
      have h_le18 : δ ≤ 1 / 8 := hδ_le_log.trans (by
        rw [div_le_div_iff₀ (by positivity) (by norm_num)]; linarith)
      linarith
    have h_pole : ‖riemannZeta (1 + (3 * δ : ℂ))‖ ≤ C_pole / (3 * δ) := by
      have h_raw := h_pole_all (3 * δ) h3δ_pos h3δ_le_one
      have hcast : (1 : ℂ) + ((3 * δ : ℝ) : ℂ) = 1 + (3 * δ : ℂ) := by push_cast; rfl
      rwa [← hcast]
    have h_lip : ‖riemannZeta (1 + (3 * δ : ℂ) + I * s.im)‖ ≤
        C_lip * Real.log (|s.im| + 2) ^ 2 * (4 * δ) := by
      have hs_eq : (1 : ℂ) - (δ : ℂ) + I * (s.im : ℂ) = s := by
        apply Complex.ext <;> simp [δ]
      have hz' : riemannZeta (1 - (δ : ℂ) + I * (s.im : ℂ)) = 0 := by rwa [hs_eq]
      exact riemannZeta_horizontal_lipschitz_of_zero ht hδ_pos hδ_le_log hz'
    have h_growth : ‖riemannZeta (1 + (3 * δ : ℂ) + 2 * I * s.im)‖ ≤
        C_growth * Real.log (|s.im| + 2) := by
      let w : ℂ := 1 + (3 * δ : ℂ) + 2 * I * s.im
      have hw_im : 3 / 2 ≤ |w.im| := by
        have him : w.im = 2 * s.im := by simp [w]
        rw [him, abs_mul, abs_of_pos (by norm_num : (0 : ℝ) < 2)]
        linarith
      have hw_re_lo : 1 - 1 / (2 * Real.log (|w.im| + 2)) ≤ w.re := by
        have hre : w.re = 1 + 3 * δ := by simp [w]
        have hlogw_pos : 0 < Real.log (|w.im| + 2) :=
          Real.log_pos (by linarith)
        rw [hre]
        linarith [show 0 ≤ 1 / (2 * Real.log (|w.im| + 2)) by positivity]
      have hw_re_hi : w.re ≤ 2 := by
        have hre : w.re = 1 + 3 * δ := by simp [w]
        linarith
      have h_raw := norm_riemannZeta_le_of_log_strip hw_im hw_re_lo hw_re_hi
      have hlog_2y : Real.log (|w.im| + 2) ≤ 2 * Real.log (|s.im| + 2) := by
        have him : |w.im| = 2 * |s.im| := by
          have : w.im = 2 * s.im := by simp [w]
          rw [this, abs_mul, abs_of_pos (by norm_num : (0 : ℝ) < 2)]
        rw [him]
        have h1 : 2 * |s.im| + 2 ≤ 2 * (|s.im| + 2) := by linarith
        have h2 : Real.log (2 * |s.im| + 2) ≤ Real.log (2 * (|s.im| + 2)) :=
          Real.log_le_log (by positivity) h1
        have h3 : Real.log (2 * (|s.im| + 2)) = Real.log 2 + Real.log (|s.im| + 2) :=
          Real.log_mul (by norm_num) (by positivity)
        have h4 : Real.log 2 ≤ Real.log (|s.im| + 2) := Real.log_le_log (by norm_num) (by linarith)
        linarith
      have h_mul := mul_le_mul_of_nonneg_left hlog_2y
        (show 0 ≤ C_strip by dsimp [C_strip]; positivity)
      have h_res : ‖riemannZeta w‖ ≤ C_growth * Real.log (|s.im| + 2) := by
        dsimp [C_growth, C_strip] at h_raw h_mul ⊢
        linarith
      exact h_res
    have hδ_lt_full : δ < (27 : ℝ) /
        (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|s.im| + 2) ^ 9) := by
      have heq : c₀ / Real.log (|s.im| + 2) ^ 9 = (27 : ℝ) /
          (256 * C_pole ^ 3 * C_lip ^ 4 * C_growth * Real.log (|s.im| + 2) ^ 9) := by
        dsimp [c₀]; field_simp
      rwa [← heq]
    exact deLaValleePoussin_contradiction hδ_pos ht hC_pole hC_lip hC_growth
      h_pole h_lip h_growth hδ_lt_full
