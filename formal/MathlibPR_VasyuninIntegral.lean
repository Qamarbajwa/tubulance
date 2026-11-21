/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
module

public import RiemannBlueprint.MathlibPR_NymanBeurling
public import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
public import Mathlib.Analysis.SpecialFunctions.Log.Deriv

/-!
# Vasyunin Diagonal and Báez-Duarte Projection Integrals

This file formalizes the exact piecewise behavior and Lebesgue integrals connecting
the dilated reciprocal fractional part `recipFractScaled k x = {1 / (k * x)}` to the
Báez-Duarte target projection `b_k` and the Vasyunin diagonal Gram matrix entry `g_{k,k}`:
1. Exact formula on the upper sub-interval `(1 / k, 1)`: `{1 / (k * x)} = 1 / (k * x)`.
2. Upper sub-interval target integral: `∫_{1/k}^1 {1 / (k * x)} dx = (ln k) / k`.
3. Upper sub-interval diagonal integral: `∫_{1/k}^1 {1 / (k * x)}² dx = 1/k - 1/k²`.
4. Full decompositions on `(0, 1)` into the rescaled base integral and upper remainder.
-/

@[expose] public section

open MeasureTheory Set Filter

/-- On the upper sub-interval `(1 / k, 1)`, `{1 / (k x)}` has zero integer part and equals
the smooth hyperbola `1 / (k x)` identically. -/
theorem recipFractScaled_eq_one_div_of_mem_Ioo {k : ℕ} (hk : 1 ≤ k) {x : ℝ}
    (hx_lo : 1 / (k : ℝ) < x) (_hx_hi : x < 1) :
    recipFractScaled k x = 1 / ((k : ℝ) * x) := by
  unfold recipFractScaled
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hkx : 1 < (k : ℝ) * x := by
    have h1 : (k : ℝ) * (1 / (k : ℝ)) < (k : ℝ) * x := mul_lt_mul_of_pos_left hx_lo hk_pos
    rwa [mul_one_div_cancel (ne_of_gt hk_pos)] at h1
  rw [Int.fract_eq_self]
  exact ⟨by positivity, (div_lt_one (by positivity)).mpr hkx⟩

/-- On the unoriented interval `uIoc (1 / k) 1`, `{1 / (k x)}` equals `1 / (k x)`. -/
theorem recipFractScaled_eq_one_div_of_mem_uIoc {k : ℕ} (hk : 1 ≤ k) {x : ℝ}
    (hx : x ∈ uIoc (1 / (k : ℝ)) 1) :
    recipFractScaled k x = 1 / ((k : ℝ) * x) := by
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hle : 1 / (k : ℝ) ≤ 1 := by
    rw [div_le_one₀ hk_pos]
    exact_mod_cast hk
  rw [uIoc_of_le hle] at hx
  unfold recipFractScaled
  have hkx : 1 < (k : ℝ) * x := by
    have h1 : (k : ℝ) * (1 / (k : ℝ)) < (k : ℝ) * x := mul_lt_mul_of_pos_left hx.1 hk_pos
    rwa [mul_one_div_cancel (ne_of_gt hk_pos)] at h1
  rw [Int.fract_eq_self]
  exact ⟨by positivity, (div_lt_one (by positivity)).mpr hkx⟩

/-- Exact `L²(0, 1)` dilation integral `∫_{1/k}^1 (1 / (kx)) dx = (ln k) / k`. -/
theorem intervalIntegral_linear_dilation (k : ℕ) (hk : 1 ≤ k) :
    ∫ x in ((1 : ℝ) / (k : ℝ))..(1 : ℝ), (1 : ℝ) / ((k : ℝ) * x) =
      Real.log (k : ℝ) / (k : ℝ) := by
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hle : (1 : ℝ) / (k : ℝ) ≤ 1 := div_le_one_of_le₀ (by exact_mod_cast hk) hk_pos.le
  have h_deriv : ∀ x ∈ Set.uIcc ((1 : ℝ) / (k : ℝ)) (1 : ℝ),
      HasDerivAt (fun y : ℝ => Real.log y / (k : ℝ)) ((1 : ℝ) / ((k : ℝ) * x)) x := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le (div_pos one_pos hk_pos) hx.1
    simpa [div_eq_mul_inv, mul_comm, mul_left_comm, mul_assoc] using
      (Real.hasDerivAt_log hx_pos.ne').div_const (k : ℝ)
  have h_cont : ContinuousOn (fun x : ℝ => (1 : ℝ) / ((k : ℝ) * x))
      (Set.uIcc ((1 : ℝ) / (k : ℝ)) (1 : ℝ)) := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le (div_pos one_pos hk_pos) hx.1
    exact (continuousAt_const.div (continuousAt_const.mul continuousAt_id)
      (mul_ne_zero hk_pos.ne' hx_pos.ne')).continuousWithinAt
  have hftc := intervalIntegral.integral_eq_sub_of_hasDerivAt h_deriv h_cont.intervalIntegrable
  rw [hftc, Real.log_one, zero_div, zero_sub, one_div, Real.log_inv]
  ring

/-- Exact `L²(0, 1)` dilation energy `∫_{1/k}^1 (1 / (kx))² dx = 1/k - 1/k²`. -/
theorem intervalIntegral_sq_dilation (k : ℕ) (hk : 1 ≤ k) :
    ∫ x in ((1 : ℝ) / (k : ℝ))..(1 : ℝ), ((1 : ℝ) / ((k : ℝ) * x)) ^ 2 =
      1 / (k : ℝ) - 1 / ((k : ℝ) ^ 2) := by
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hle : (1 : ℝ) / (k : ℝ) ≤ 1 := div_le_one_of_le₀ (by exact_mod_cast hk) hk_pos.le
  have h_deriv : ∀ x ∈ Set.uIcc ((1 : ℝ) / (k : ℝ)) (1 : ℝ),
      HasDerivAt (fun y : ℝ => -(1 : ℝ) / ((k : ℝ) ^ 2 * y))
        (((1 : ℝ) / ((k : ℝ) * x)) ^ 2) x := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le (div_pos one_pos hk_pos) hx.1
    have hinv : HasDerivAt (fun y : ℝ => y⁻¹) (-(x ^ 2)⁻¹) x := hasDerivAt_inv hx_pos.ne'
    have hconst := hinv.const_mul (-(1 : ℝ) / (k : ℝ) ^ 2)
    have hEq : (fun y : ℝ => (-(1 : ℝ) / (k : ℝ) ^ 2) * y⁻¹) =
        (fun y : ℝ => -(1 : ℝ) / ((k : ℝ) ^ 2 * y)) := by
      funext y; ring
    rw [hEq] at hconst
    convert hconst using 1
    field_simp [hk_pos.ne', hx_pos.ne']
  have h_cont : ContinuousOn (fun x : ℝ => ((1 : ℝ) / ((k : ℝ) * x)) ^ 2)
      (Set.uIcc ((1 : ℝ) / (k : ℝ)) (1 : ℝ)) := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le (div_pos one_pos hk_pos) hx.1
    exact ((continuousAt_const.div (continuousAt_const.mul continuousAt_id)
      (mul_ne_zero hk_pos.ne' hx_pos.ne')).pow 2).continuousWithinAt
  have hftc := intervalIntegral.integral_eq_sub_of_hasDerivAt h_deriv h_cont.intervalIntegrable
  rw [hftc]
  field_simp [hk_pos.ne']
  ring

/-- `recipFractScaled k` is interval integrable on any compact interval. -/
theorem intervalIntegrable_recipFractScaled (k : ℕ) (a b : ℝ) :
    IntervalIntegrable (recipFractScaled k) volume a b := by
  have hmeas : Measurable (recipFractScaled k) :=
    measurable_fract.comp (measurable_const.div (measurable_const.mul measurable_id))
  have hbd : ∀ x, ‖recipFractScaled k x‖ ≤ (1 : ℝ) := by
    intro x
    unfold recipFractScaled
    rw [Real.norm_of_nonneg (Int.fract_nonneg _)]
    exact (Int.fract_lt_one _).le
  exact (intervalIntegrable_const (c := (1 : ℝ))).mono_fun' hmeas.aestronglyMeasurable
    (ae_of_all _ fun x => hbd x)

/-- `(recipFractScaled k x) ^ 2` is interval integrable on any compact interval. -/
theorem intervalIntegrable_sq_recipFractScaled (k : ℕ) (a b : ℝ) :
    IntervalIntegrable (fun x => (recipFractScaled k x) ^ 2) volume a b := by
  have hmeas : Measurable (fun x => (recipFractScaled k x) ^ 2) := by
    have hm : Measurable (recipFractScaled k) :=
      measurable_fract.comp (measurable_const.div (measurable_const.mul measurable_id))
    exact hm.pow_const 2
  have hbd : ∀ x, ‖(recipFractScaled k x) ^ 2‖ ≤ (1 : ℝ) := by
    intro x
    unfold recipFractScaled
    rw [Real.norm_of_nonneg (sq_nonneg _)]
    have h1 : 0 ≤ Int.fract (1 / ((k : ℝ) * x)) := Int.fract_nonneg _
    have h2 : Int.fract (1 / ((k : ℝ) * x)) < 1 := Int.fract_lt_one _
    nlinarith
  exact (intervalIntegrable_const (c := (1 : ℝ))).mono_fun' hmeas.aestronglyMeasurable
    (ae_of_all _ fun x => hbd x)

/-- The upper sub-interval `(1 / k, 1]` contributes the exact logarithmic term `(ln k) / k`
to the Báez-Duarte target projection `b_k = ∫_0^1 {1 / (k x)} dx`. -/
theorem intervalIntegral_recipFractScaled_inv_to_one {k : ℕ} (hk : 1 ≤ k) :
    (∫ x in (1 / (k : ℝ))..1, recipFractScaled k x) = Real.log (k : ℝ) / (k : ℝ) := by
  have h_eq : (∫ x in (1 / (k : ℝ))..1, recipFractScaled k x) =
      ∫ x in (1 / (k : ℝ))..1, 1 / ((k : ℝ) * x) := by
    apply intervalIntegral.integral_congr_ae
    exact ae_of_all _ (fun x hx => recipFractScaled_eq_one_div_of_mem_uIoc hk hx)
  rw [h_eq]
  exact intervalIntegral_linear_dilation k hk

/-- The upper sub-interval `(1 / k, 1]` contributes `1 / k - 1 / k^2` to the Vasyunin
diagonal Gram inner product `g_{k,k} = ∫_0^1 {1 / (k x)}^2 dx`. -/
theorem intervalIntegral_sq_recipFractScaled_inv_to_one {k : ℕ} (hk : 1 ≤ k) :
    (∫ x in (1 / (k : ℝ))..1, (recipFractScaled k x) ^ 2) =
      1 / (k : ℝ) - 1 / (k : ℝ) ^ 2 := by
  have h_eq : (∫ x in (1 / (k : ℝ))..1, (recipFractScaled k x) ^ 2) =
      ∫ x in (1 / (k : ℝ))..1, (1 / ((k : ℝ) * x)) ^ 2 := by
    apply intervalIntegral.integral_congr_ae
    exact ae_of_all _ (fun x hx => by rw [recipFractScaled_eq_one_div_of_mem_uIoc hk hx])
  rw [h_eq]
  exact intervalIntegral_sq_dilation k hk

/-- Full Báez-Duarte target decomposition on `(0, 1)` into base integral and log remainder. -/
theorem intervalIntegral_recipFractScaled_zero_to_one {k : ℕ} (hk : 1 ≤ k) :
    (∫ x in (0 : ℝ)..1, recipFractScaled k x) =
      (Real.log (k : ℝ) + ∫ y in (0 : ℝ)..1, recipFract y) / (k : ℝ) := by
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have h_split := (intervalIntegral.integral_add_adjacent_intervals
    (intervalIntegrable_recipFractScaled k 0 (1 / (k : ℝ)))
    (intervalIntegrable_recipFractScaled k (1 / (k : ℝ)) 1)).symm
  rw [h_split]
  have h_lower : (∫ x in (0 : ℝ)..(1 / (k : ℝ)), recipFractScaled k x) =
      (∫ y in (0 : ℝ)..1, recipFract y) / (k : ℝ) := by
    have hcomp := intervalIntegral.integral_comp_mul_left recipFract (ne_of_gt hk_pos)
      (a := 0) (b := 1 / (k : ℝ))
    rw [mul_zero, mul_one_div_cancel (ne_of_gt hk_pos)] at hcomp
    have hdef : (fun x => recipFract ((k : ℝ) * x)) = recipFractScaled k := by
      funext x; rfl
    rw [hdef] at hcomp
    rw [hcomp, smul_eq_mul, div_eq_inv_mul]
  rw [h_lower, intervalIntegral_recipFractScaled_inv_to_one hk]
  ring

/-- Full Vasyunin diagonal decomposition on `(0, 1)` into base energy and remainder. -/
theorem intervalIntegral_sq_recipFractScaled_zero_to_one {k : ℕ} (hk : 1 ≤ k) :
    (∫ x in (0 : ℝ)..1, (recipFractScaled k x) ^ 2) =
      (1 + ∫ y in (0 : ℝ)..1, (recipFract y) ^ 2) / (k : ℝ) - 1 / (k : ℝ) ^ 2 := by
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have h_split := (intervalIntegral.integral_add_adjacent_intervals
    (intervalIntegrable_sq_recipFractScaled k 0 (1 / (k : ℝ)))
    (intervalIntegrable_sq_recipFractScaled k (1 / (k : ℝ)) 1)).symm
  rw [h_split]
  have h_lower : (∫ x in (0 : ℝ)..(1 / (k : ℝ)), (recipFractScaled k x) ^ 2) =
      (∫ y in (0 : ℝ)..1, (recipFract y) ^ 2) / (k : ℝ) := by
    have hcomp := intervalIntegral.integral_comp_mul_left
      (fun y => (recipFract y) ^ 2) (ne_of_gt hk_pos) (a := 0) (b := 1 / (k : ℝ))
    rw [mul_zero, mul_one_div_cancel (ne_of_gt hk_pos)] at hcomp
    have hdef : (fun x => (recipFract ((k : ℝ) * x)) ^ 2) =
        (fun x => (recipFractScaled k x) ^ 2) := by
      funext x; rfl
    rw [hdef] at hcomp
    rw [hcomp, smul_eq_mul, div_eq_inv_mul]
  rw [h_lower, intervalIntegral_sq_recipFractScaled_inv_to_one hk]
  ring
