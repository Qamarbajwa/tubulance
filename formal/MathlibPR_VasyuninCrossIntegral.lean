/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Stirling
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Cotangent
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.NumberTheory.Harmonic.EulerMascheroni
import RiemannBlueprint.MathlibPR_NymanBeurling
import RiemannBlueprint.MathlibPR_VasyuninIntegral
import RiemannBlueprint.Section8_VasyuninBDR

/-!
# Vasyunin Cross-Integrals, Off-Diagonal Cotangent Sums, and L² BDR Bridge

This file formalizes the analytic cross-integrals and the exact bridge between the continuous
Lebesgue $L^2(0, 1)$ Hilbert space distance and the discrete Rank-4 Boundary-Dirichlet
Reduction (BDR) matrix algebra:
1. Product integrability: `intervalIntegrable_recipFractScaled_mul` proves that
   `recipFractScaled j x * recipFractScaled k x` is interval integrable on any compact interval.
2. Upper sub-interval evaluation: on `(max(1/j, 1/k), 1)`, both `{1/(jx)}` and `{1/(kx)}` have
   zero integer part, yielding `1 / (j * k * max(1/j, 1/k)) - 1 / (j * k)`.
3. Vasyunin cotangent sums: `vasyuninCotSum` and `vasyuninGCot`, proving diagonal vanishing
   `vasyuninGCot k k = 0` and symmetry `vasyuninGCot j k = vasyuninGCot k j`.
4. Smooth kernel properties: `GSmooth_comm` and diagonal reduction `GSmooth_diag`.
5. Full quadratic expansion: `intervalIntegral_sq_sub_sum` expands the Lebesgue $L^2$ norm
   of `1 - ∑ c_k {1/(kx)}` into linear target projections and cross-Gram inner products.
6. Affine $L^2$ pure cotangent bridge: `affine_l2_pure_cotangent_bridge` proves that for any
   $c \in \mathcal{A}_N$ (satisfying $D_1(c, N) = 0$ and $D_0(c, N) = 2$), all smooth and
   logarithmic terms cancel identically, leaving exact pure cotangent residual `1 + Q_cot(c, N)`.
-/

open MeasureTheory Set Filter Finset
open RiemannBlueprint.Section8_VasyuninBDR

/-- Product of two dilated fractional parts is interval integrable on any compact interval. -/
theorem intervalIntegrable_recipFractScaled_mul (j k : ℕ) (a b : ℝ) :
    IntervalIntegrable (fun x => recipFractScaled j x * recipFractScaled k x) volume a b := by
  have hmeas : Measurable (fun x => recipFractScaled j x * recipFractScaled k x) := by
    have hmj : Measurable (recipFractScaled j) :=
      measurable_fract.comp (measurable_const.div (measurable_const.mul measurable_id))
    have hmk : Measurable (recipFractScaled k) :=
      measurable_fract.comp (measurable_const.div (measurable_const.mul measurable_id))
    exact hmj.mul hmk
  have hbd : ∀ x, ‖recipFractScaled j x * recipFractScaled k x‖ ≤ (1 : ℝ) := by
    intro x
    unfold recipFractScaled
    have hj_nonneg : 0 ≤ Int.fract (1 / ((j : ℝ) * x)) := Int.fract_nonneg _
    have hk_nonneg : 0 ≤ Int.fract (1 / ((k : ℝ) * x)) := Int.fract_nonneg _
    have hj_lt : Int.fract (1 / ((j : ℝ) * x)) < 1 := Int.fract_lt_one _
    have hk_lt : Int.fract (1 / ((k : ℝ) * x)) < 1 := Int.fract_lt_one _
    rw [Real.norm_of_nonneg (mul_nonneg hj_nonneg hk_nonneg)]
    nlinarith
  exact (intervalIntegrable_const (c := (1 : ℝ))).mono_fun' hmeas.aestronglyMeasurable
    (ae_of_all _ fun x => hbd x)

/-- On the upper sub-interval `uIoc (max(1/j, 1/k)) 1`, both fractional parts reduce to hyperbolas:
`recipFractScaled j x * recipFractScaled k x = 1 / (j * k * x^2)`. -/
theorem recipFractScaled_mul_eq_on_uIoc {j k : ℕ} (hj : 1 ≤ j) (hk : 1 ≤ k) {x : ℝ}
    (hx : x ∈ uIoc (max (1 / (j : ℝ)) (1 / (k : ℝ))) 1) :
    recipFractScaled j x * recipFractScaled k x = 1 / ((j : ℝ) * (k : ℝ) * x ^ 2) := by
  let M := max (1 / (j : ℝ)) (1 / (k : ℝ))
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hj_le_one : 1 / (j : ℝ) ≤ 1 := div_le_one_of_le₀ (by exact_mod_cast hj) hj_pos.le
  have hk_le_one : 1 / (k : ℝ) ≤ 1 := div_le_one_of_le₀ (by exact_mod_cast hk) hk_pos.le
  have hM_le : M ≤ 1 := max_le hj_le_one hk_le_one
  rw [uIoc_of_le hM_le] at hx
  have hx_j : x ∈ uIoc (1 / (j : ℝ)) 1 := by
    rw [uIoc_of_le hj_le_one]
    exact ⟨(le_max_left (1 / (j : ℝ)) (1 / (k : ℝ))).trans_lt hx.1, hx.2⟩
  have hx_k : x ∈ uIoc (1 / (k : ℝ)) 1 := by
    rw [uIoc_of_le hk_le_one]
    exact ⟨(le_max_right (1 / (j : ℝ)) (1 / (k : ℝ))).trans_lt hx.1, hx.2⟩
  rw [recipFractScaled_eq_one_div_of_mem_uIoc hj hx_j,
      recipFractScaled_eq_one_div_of_mem_uIoc hk hx_k]
  ring

/-- Exact integral of `1 / (j * k * x^2)` on `M..1`. -/
theorem intervalIntegral_inv_prod_x_sq {j k : ℕ} (hj : 1 ≤ j) (hk : 1 ≤ k) {M : ℝ}
    (hM_pos : 0 < M) (hM_le : M ≤ 1) :
    ∫ x in M..1, (1 : ℝ) / ((j : ℝ) * (k : ℝ) * x ^ 2) =
      1 / ((j : ℝ) * (k : ℝ) * M) - 1 / ((j : ℝ) * (k : ℝ)) := by
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hjk_pos : (0 : ℝ) < (j : ℝ) * (k : ℝ) := mul_pos hj_pos hk_pos
  have h_deriv : ∀ x ∈ Set.uIcc M 1,
      HasDerivAt (fun y : ℝ => -(1 : ℝ) / ((j : ℝ) * (k : ℝ) * y))
        ((1 : ℝ) / ((j : ℝ) * (k : ℝ) * x ^ 2)) x := by
    intro x hx
    rw [Set.uIcc_of_le hM_le] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le hM_pos hx.1
    have hinv : HasDerivAt (fun y : ℝ => y⁻¹) (-(x ^ 2)⁻¹) x := hasDerivAt_inv hx_pos.ne'
    have hconst := hinv.const_mul (-(1 : ℝ) / ((j : ℝ) * (k : ℝ)))
    have hEq : (fun y : ℝ => (-(1 : ℝ) / ((j : ℝ) * (k : ℝ))) * y⁻¹) =
        (fun y : ℝ => -(1 : ℝ) / ((j : ℝ) * (k : ℝ) * y)) := by
      funext y; ring
    rw [hEq] at hconst
    convert hconst using 1
    field_simp [hj_pos.ne', hk_pos.ne', hx_pos.ne']
  have h_cont : ContinuousOn (fun x : ℝ => (1 : ℝ) / ((j : ℝ) * (k : ℝ) * x ^ 2))
      (Set.uIcc M 1) := by
    intro x hx
    rw [Set.uIcc_of_le hM_le] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le hM_pos hx.1
    have hdenom : (j : ℝ) * (k : ℝ) * x ^ 2 ≠ 0 :=
      mul_ne_zero hjk_pos.ne' (pow_ne_zero 2 hx_pos.ne')
    exact ((continuousAt_const.div
      (continuousAt_const.mul (continuousAt_id.pow 2)) hdenom)).continuousWithinAt
  have hftc := intervalIntegral.integral_eq_sub_of_hasDerivAt h_deriv h_cont.intervalIntegrable
  rw [hftc]
  ring

/-- Upper sub-interval contribution to the cross inner product on `(max(1/j, 1/k), 1)`. -/
theorem intervalIntegral_recipFractScaled_mul_upper {j k : ℕ} (hj : 1 ≤ j) (hk : 1 ≤ k) :
    let M := max (1 / (j : ℝ)) (1 / (k : ℝ))
    ∫ x in M..1, recipFractScaled j x * recipFractScaled k x =
      1 / ((j : ℝ) * (k : ℝ) * M) - 1 / ((j : ℝ) * (k : ℝ)) := by
  intro M
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hM_pos : 0 < M := lt_max_of_lt_left (div_pos one_pos hj_pos)
  have hj_le_one : 1 / (j : ℝ) ≤ 1 := div_le_one_of_le₀ (by exact_mod_cast hj) hj_pos.le
  have hk_le_one : 1 / (k : ℝ) ≤ 1 := div_le_one_of_le₀ (by exact_mod_cast hk) hk_pos.le
  have hM_le : M ≤ 1 := max_le hj_le_one hk_le_one
  have h_eq : (∫ x in M..1, recipFractScaled j x * recipFractScaled k x) =
      ∫ x in M..1, (1 : ℝ) / ((j : ℝ) * (k : ℝ) * x ^ 2) := by
    apply intervalIntegral.integral_congr_ae
    exact ae_of_all _ (fun x hx => recipFractScaled_mul_eq_on_uIoc hj hk hx)
  rw [h_eq]
  exact intervalIntegral_inv_prod_x_sq hj hk hM_pos hM_le

/-- Vasyunin's cotangent sum V(a, b) for coprime pairs or general positive integers:
  V(a, b) = ∑_{m=1}^{a-1} {m * b / a} * cot(π * m / a). -/
noncomputable def vasyuninCotSum (a b : ℕ) : ℝ :=
  ∑ m ∈ Finset.Ico 1 a,
    Int.fract ((m : ℝ) * (b : ℝ) / (a : ℝ)) *
      (Real.cos (Real.pi * (m : ℝ) / (a : ℝ)) / Real.sin (Real.pi * (m : ℝ) / (a : ℝ)))

/-- Cotangent component of Vasyunin's cross Gram matrix entry:
  g_{j,k}^{(cot)} = - (π / (2 * j * k)) * (V(j, k) + V(k, j)). -/
noncomputable def vasyuninGCot (j k : ℕ) : ℝ :=
  - (Real.pi / (2 * (j : ℝ) * (k : ℝ))) * (vasyuninCotSum j k + vasyuninCotSum k j)

/-- vasyuninCotSum vanishes on the diagonal: V(k, k) = 0 for any k. -/
theorem vasyuninCotSum_diag (k : ℕ) : vasyuninCotSum k k = 0 := by
  unfold vasyuninCotSum
  by_cases hk : k = 0
  · subst hk
    rfl
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr (Nat.pos_of_ne_zero hk)
  refine Finset.sum_eq_zero ?_
  intro m _hm
  have hmk : (m : ℝ) * (k : ℝ) / (k : ℝ) = (m : ℝ) := mul_div_cancel_right₀ (m : ℝ) hk_pos.ne'
  rw [hmk, Int.fract_natCast, zero_mul]

/-- The cotangent Gram component vanishes on the diagonal. -/
theorem vasyuninGCot_diag (k : ℕ) : vasyuninGCot k k = 0 := by
  unfold vasyuninGCot
  rw [vasyuninCotSum_diag k, add_zero, mul_zero]

/-- Symmetry of the cotangent Gram component: g_{j,k}^{(cot)} = g_{k,j}^{(cot)}. -/
theorem vasyuninGCot_comm (j k : ℕ) : vasyuninGCot j k = vasyuninGCot k j := by
  dsimp [vasyuninGCot]
  have hdenom : 2 * (j : ℝ) * (k : ℝ) = 2 * (k : ℝ) * (j : ℝ) := by ring
  rw [hdenom, add_comm (vasyuninCotSum j k)]

/-- GSmooth is symmetric in j and k. -/
theorem GSmooth_comm (gamma_E : ℝ) {j k : ℕ} (hj : 0 < j) (hk : 0 < k) :
    GSmooth gamma_E j k = GSmooth gamma_E k j := by
  have hj_ne : (j : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hj.ne'
  have hk_ne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hk.ne'
  dsimp [GSmooth]
  have hlog_inv : Real.log ((j : ℝ) / (k : ℝ)) = - Real.log ((k : ℝ) / (j : ℝ)) := by
    rw [Real.log_div hj_ne hk_ne, Real.log_div hk_ne hj_ne]
    ring
  rw [hlog_inv]
  ring

/-- On the diagonal, GSmooth evaluates to the smooth Vasyunin diagonal value. -/
theorem GSmooth_diag (gamma_E : ℝ) {k : ℕ} (hk : 0 < k) :
    GSmooth gamma_E k k = (Real.log (2 * Real.pi) - gamma_E) / (k : ℝ) - 1 / ((k : ℝ) ^ 2) := by
  have hk_ne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hk.ne'
  dsimp [GSmooth]
  rw [div_self hk_ne, Real.log_one, mul_zero, add_zero]
  field_simp [hk_ne]
  ring

/-- The total Vasyunin Gram entry GSmooth + vasyuninGCot evaluates to the exact diagonal energy. -/
theorem vasyuninGram_diag (gamma_E : ℝ) {k : ℕ} (hk : 0 < k) :
    GSmooth gamma_E k k + vasyuninGCot k k =
      (Real.log (2 * Real.pi) - gamma_E) / (k : ℝ) - 1 / ((k : ℝ) ^ 2) := by
  rw [vasyuninGCot_diag k, add_zero]
  exact GSmooth_diag gamma_E hk

/-! ### Unconditional Base and Cross Integrals -/

private lemma recipFractScaled_eq_of_mem_Ioo {j n : ℕ} (hj : 1 ≤ j) (hn : 1 ≤ n) {x : ℝ}
    (hx : x ∈ Set.Ioo (1 / ((n : ℝ) + 1)) (1 / (n : ℝ))) :
    recipFractScaled j x = 1 / ((j : ℝ) * x) - ((n / j : ℕ) : ℝ) := by
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hn_pos : (0 : ℝ) < (n : ℝ) := Nat.cast_pos.mpr hn
  have hx_pos : 0 < x := lt_trans (by positivity) hx.1
  have hjx_pos : 0 < (j : ℝ) * x := mul_pos hj_pos hx_pos
  have h_inv_gt : (n : ℝ) < 1 / x := (lt_one_div hx_pos hn_pos).mp hx.2
  have h_inv_lt : 1 / x < (n : ℝ) + 1 := (one_div_lt (by positivity) hx_pos).mp hx.1
  have hmod := Nat.div_add_mod n j
  have hrem : n % j < j := Nat.mod_lt n hj
  let q : ℕ := n / j
  have hq_lo : (q : ℝ) ≤ 1 / ((j : ℝ) * x) := by
    have h1 : (j : ℝ) * (q : ℝ) ≤ (n : ℝ) := by exact_mod_cast (by omega : j * (n / j) ≤ n)
    rw [le_div_iff₀ hjx_pos]
    nlinarith [(lt_div_iff₀ hx_pos).mp h_inv_gt]
  have hq_hi : 1 / ((j : ℝ) * x) < (q : ℝ) + 1 := by
    have h2nat : n + 1 ≤ j * (n / j + 1) := by
      have h1 : n < j * (n / j) + j := by
        calc n = j * (n / j) + n % j := (Nat.div_add_mod n j).symm
          _ < j * (n / j) + j := Nat.add_lt_add_left hrem _
      linarith [show j * (n / j + 1) = j * (n / j) + j by ring]
    have h2 : (n : ℝ) + 1 ≤ (j : ℝ) * ((q : ℝ) + 1) := by exact_mod_cast h2nat
    rw [div_lt_iff₀ hjx_pos]
    have h3 : 1 < ((n : ℝ) + 1) * x := (div_lt_iff₀ hx_pos).mp h_inv_lt
    nlinarith
  have hfl : ⌊1 / ((j : ℝ) * x)⌋ = (q : ℤ) := by
    rw [Int.floor_eq_iff]
    exact ⟨by exact_mod_cast hq_lo, by exact_mod_cast hq_hi⟩
  change Int.fract (1 / ((j : ℝ) * x)) = 1 / ((j : ℝ) * x) - (q : ℝ)
  rw [Int.fract, hfl]
  simp

private lemma intervalIntegral_recipFract_unit {n : ℕ} (hn : 1 ≤ n) :
    (∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)), recipFract x) =
      Real.log ((n : ℝ) + 1) - Real.log (n : ℝ) - 1 / ((n : ℝ) + 1) := by
  have hn_pos : (0 : ℝ) < (n : ℝ) := Nat.cast_pos.mpr hn
  have hle : 1 / ((n : ℝ) + 1) ≤ 1 / (n : ℝ) :=
    one_div_le_one_div_of_le hn_pos (by linarith)
  have h_ae : (∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)), recipFract x) =
      ∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)), (1 / x - (n : ℝ)) := by
    rw [intervalIntegral.integral_of_le hle, intervalIntegral.integral_of_le hle,
      MeasureTheory.integral_Ioc_eq_integral_Ioo, MeasureTheory.integral_Ioc_eq_integral_Ioo]
    refine setIntegral_congr_fun measurableSet_Ioo fun x hx => ?_
    simpa [recipFract, recipFractScaled, one_mul, Nat.div_one] using
      recipFractScaled_eq_of_mem_Ioo le_rfl hn hx
  have h_deriv : ∀ x ∈ Set.uIcc (1 / ((n : ℝ) + 1)) (1 / (n : ℝ)),
      HasDerivAt (fun y : ℝ => Real.log y - (n : ℝ) * y) (1 / x - (n : ℝ)) x := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le (by positivity) hx.1
    convert (Real.hasDerivAt_log hx_pos.ne').sub ((hasDerivAt_id' x).const_mul (n : ℝ)) using 1
    simp [one_div]
  have h_cont : ContinuousOn (fun x : ℝ => 1 / x - (n : ℝ))
      (Set.uIcc (1 / ((n : ℝ) + 1)) (1 / (n : ℝ))) := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le (by positivity) hx.1
    exact ((continuousAt_const.div continuousAt_id hx_pos.ne').sub continuousAt_const)
      |>.continuousWithinAt
  rw [h_ae, intervalIntegral.integral_eq_sub_of_hasDerivAt h_deriv h_cont.intervalIntegrable]
  rw [one_div, Real.log_inv, one_div, Real.log_inv]
  have hne : (n : ℝ) ≠ 0 := hn_pos.ne'
  have hne1 : (n : ℝ) + 1 ≠ 0 := by positivity
  field_simp [hne, hne1]
  ring

private lemma intervalIntegral_split_recip (f : ℝ → ℝ)
    (hf : ∀ a b : ℝ, IntervalIntegrable f volume a b) (L : ℕ) (hL : 1 ≤ L) :
    (∫ x in (1 / (L : ℝ))..1, f x) =
      ∑ n ∈ Finset.Ico 1 L, ∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)), f x := by
  induction L, hL using Nat.le_induction with
  | base => simp
  | succ k hk ih =>
    have hsplit := (intervalIntegral.integral_add_adjacent_intervals
      (hf (1 / ((k : ℝ) + 1)) (1 / (k : ℝ)))
      (hf (1 / (k : ℝ)) 1)).symm
    push_cast
    rw [hsplit, ih, Finset.sum_Ico_succ_top hk, add_comm]

private lemma harmonic_eq_sum_Icc (N : ℕ) :
    (harmonic N : ℝ) = ∑ m ∈ Finset.Icc 1 N, (1 : ℝ) / (m : ℝ) := by
  induction N with
  | zero => simp [harmonic_zero]
  | succ n ih =>
    rw [Finset.sum_Icc_succ_top (Nat.succ_pos n), harmonic_succ, Rat.cast_add, ih]
    simp [one_div]

/-- Exact value of the unscaled base integral `∫₀¹ {1/x} dx = 1 - γ`. -/
theorem intervalIntegral_recipFract_zero_to_one :
    (∫ x in (0 : ℝ)..1, recipFract x) = 1 - Real.eulerMascheroniConstant := by
  have hint_rf : ∀ a b : ℝ, IntervalIntegrable recipFract volume a b := by
    intro a b
    have h_eq : recipFract = recipFractScaled 1 := by
      funext x; simp [recipFract, recipFractScaled]
    rw [h_eq]
    exact intervalIntegrable_recipFractScaled 1 a b
  have h_partial : ∀ M : ℕ,
      (∫ x in (1 / ((M : ℝ) + 1))..1, recipFract x) =
        1 - ((harmonic (M + 1) : ℝ) - Real.log ((M + 1 : ℕ) : ℝ)) := by
    intro M
    have h_split := intervalIntegral_split_recip recipFract hint_rf (M + 1) (Nat.succ_pos M)
    push_cast at h_split ⊢
    rw [h_split]
    have h_congr : ∑ n ∈ Finset.Ico 1 (M + 1),
        (∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)), recipFract x) =
        ∑ n ∈ Finset.Ico 1 (M + 1),
          (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ) - 1 / ((n : ℝ) + 1)) := by
      refine Finset.sum_congr rfl fun n hn => ?_
      exact intervalIntegral_recipFract_unit (Finset.mem_Ico.mp hn).1
    rw [h_congr, Finset.sum_sub_distrib]
    have h_log_sum : ∑ n ∈ Finset.Ico 1 (M + 1), (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) =
        Real.log ((M : ℝ) + 1) := by
      have htel : ∑ n ∈ Finset.Ico 1 (M + 1), (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) =
          Real.log (((M + 1 : ℕ) : ℝ)) - Real.log ((1 : ℕ) : ℝ) := by
        simpa [Nat.cast_add, Nat.cast_one] using
          Finset.sum_Ico_sub (fun n : ℕ => Real.log (n : ℝ)) (Nat.succ_pos M)
      rw [htel, Nat.cast_one, Real.log_one, sub_zero, Nat.cast_add, Nat.cast_one]
    have h_harm : ∑ n ∈ Finset.Ico 1 (M + 1), (1 : ℝ) / ((n : ℝ) + 1) =
        (harmonic (M + 1) : ℝ) - 1 := by
      rw [harmonic_eq_sum_Icc (M + 1), ← Finset.Ico_succ_right_eq_Icc]
      have hshift : ∑ n ∈ Finset.Ico 1 (M + 1), (1 : ℝ) / ((n : ℝ) + 1) =
          ∑ m ∈ Finset.Ico 2 (M + 2), (1 : ℝ) / (m : ℝ) := by
        rw [Finset.sum_Ico_eq_sum_range, Finset.sum_Ico_eq_sum_range]
        simp only [Nat.add_sub_cancel]
        refine Finset.sum_congr rfl fun i _ => ?_
        push_cast; ring_nf
      rw [hshift]
      have h12 : Finset.Ico 1 (Order.succ (M + 1)) = insert 1 (Finset.Ico 2 (M + 2)) := by
        ext m; simp [Finset.mem_Ico]; omega
      rw [h12, Finset.sum_insert (by simp [Finset.mem_Ico])]
      simp [one_div]
    rw [h_log_sum, h_harm]
    ring
  have h_tendsto_main : Tendsto (fun M : ℕ => ∫ x in (1 / ((M : ℝ) + 1))..1, recipFract x)
      atTop (nhds (1 - Real.eulerMascheroniConstant)) := by
    have h_rhs : Tendsto (fun M : ℕ => 1 - ((harmonic (M + 1) : ℝ) - Real.log ((M + 1 : ℕ) : ℝ)))
        atTop (nhds (1 - Real.eulerMascheroniConstant)) := by
      have ht := Real.tendsto_eulerMascheroniSeq'.comp (tendsto_add_atTop_nat 1)
      refine tendsto_const_nhds.sub ?_
      refine ht.congr' (Eventually.of_forall fun M => ?_)
      simp [Real.eulerMascheroniSeq', Nat.add_eq_zero_iff]
    refine h_rhs.congr' (Eventually.of_forall fun M => (h_partial M).symm)
  have h_tendsto_zero : Tendsto (fun M : ℕ => ∫ x in (0 : ℝ)..(1 / ((M : ℝ) + 1)), recipFract x)
      atTop (nhds 0) := by
    refine squeeze_zero_norm' (Eventually.of_forall fun M => ?_)
      (tendsto_one_div_add_atTop_nhds_zero_nat (𝕜 := ℝ))
    have hle : (0 : ℝ) ≤ 1 / ((M : ℝ) + 1) := by positivity
    have hbd : ∀ x ∈ Set.uIoc (0 : ℝ) (1 / ((M : ℝ) + 1)), ‖recipFract x‖ ≤ (1 : ℝ) := by
      intro x _
      rw [recipFract, Real.norm_of_nonneg (Int.fract_nonneg _)]
      exact (Int.fract_lt_one _).le
    simpa [abs_of_nonneg hle, abs_of_nonneg (by positivity : (0 : ℝ) ≤ (M : ℝ) + 1)] using
      intervalIntegral.norm_integral_le_of_norm_le_const hbd
  have h_sum : ∀ M : ℕ, (∫ x in (0 : ℝ)..1, recipFract x) =
      (∫ x in (0 : ℝ)..(1 / ((M : ℝ) + 1)), recipFract x) +
        (∫ x in (1 / ((M : ℝ) + 1))..1, recipFract x) := fun M =>
    (intervalIntegral.integral_add_adjacent_intervals (hint_rf 0 _) (hint_rf _ 1)).symm
  have h_const : Tendsto (fun _ : ℕ => ∫ x in (0 : ℝ)..1, recipFract x)
      atTop (nhds (∫ x in (0 : ℝ)..1, recipFract x)) := tendsto_const_nhds
  have h_eq : Tendsto (fun _ : ℕ => ∫ x in (0 : ℝ)..1, recipFract x)
      atTop (nhds (0 + (1 - Real.eulerMascheroniConstant))) :=
    (h_tendsto_zero.add h_tendsto_main).congr' (Eventually.of_forall fun M => (h_sum M).symm)
  simpa using tendsto_nhds_unique h_const h_eq

/-- Unconditional Báez-Duarte / Vasyunin target projection identity for all `k ≥ 1`. -/
theorem intervalIntegral_recipFractScaled_eq_bVasyunin {k : ℕ} (hk : 1 ≤ k) :
    (∫ x in (0 : ℝ)..1, recipFractScaled k x) =
      bVasyunin k Real.eulerMascheroniConstant := by
  rw [intervalIntegral_recipFractScaled_zero_to_one hk, intervalIntegral_recipFract_zero_to_one]
  dsimp [bVasyunin]
  ring

private lemma intervalIntegral_recipFractScaled_mul_unit {j k n : ℕ}
    (hj : 1 ≤ j) (hk : 1 ≤ k) (hn : 1 ≤ n) :
    let p : ℝ := ((n / j : ℕ) : ℝ)
    let q : ℝ := ((n / k : ℕ) : ℝ)
    (∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)), recipFractScaled j x * recipFractScaled k x) =
      1 / ((j : ℝ) * (k : ℝ)) -
        (p / (k : ℝ) + q / (j : ℝ)) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) +
        p * q * (1 / (n : ℝ) - 1 / ((n : ℝ) + 1)) := by
  intro p q
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hn_pos : (0 : ℝ) < (n : ℝ) := Nat.cast_pos.mpr hn
  have hle : 1 / ((n : ℝ) + 1) ≤ 1 / (n : ℝ) :=
    one_div_le_one_div_of_le hn_pos (by linarith)
  have h_ae : (∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)),
        recipFractScaled j x * recipFractScaled k x) =
      ∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)),
        (1 / ((j : ℝ) * (k : ℝ) * x ^ 2) -
          (p / (k : ℝ) + q / (j : ℝ)) * (1 / x) + p * q) := by
    rw [intervalIntegral.integral_of_le hle, intervalIntegral.integral_of_le hle,
      MeasureTheory.integral_Ioc_eq_integral_Ioo, MeasureTheory.integral_Ioc_eq_integral_Ioo]
    refine setIntegral_congr_fun measurableSet_Ioo fun x hx => ?_
    rw [recipFractScaled_eq_of_mem_Ioo hj hn hx, recipFractScaled_eq_of_mem_Ioo hk hn hx]
    have hx_ne : x ≠ 0 := (lt_trans (by positivity) hx.1).ne'
    field_simp [hj_pos.ne', hk_pos.ne', hx_ne]
    ring
  have h_deriv : ∀ x ∈ Set.uIcc (1 / ((n : ℝ) + 1)) (1 / (n : ℝ)),
      HasDerivAt
        (fun y : ℝ => -(1 : ℝ) / ((j : ℝ) * (k : ℝ) * y) -
          (p / (k : ℝ) + q / (j : ℝ)) * Real.log y + p * q * y)
        (1 / ((j : ℝ) * (k : ℝ) * x ^ 2) -
          (p / (k : ℝ) + q / (j : ℝ)) * (1 / x) + p * q) x := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le (by positivity) hx.1
    have h1 : HasDerivAt (fun y : ℝ => -(1 : ℝ) / ((j : ℝ) * (k : ℝ) * y))
        (1 / ((j : ℝ) * (k : ℝ) * x ^ 2)) x := by
      have hinv := (hasDerivAt_inv hx_pos.ne').const_mul (-(1 : ℝ) / ((j : ℝ) * (k : ℝ)))
      have hEq : (fun y : ℝ => (-(1 : ℝ) / ((j : ℝ) * (k : ℝ))) * y⁻¹) =
          (fun y : ℝ => -(1 : ℝ) / ((j : ℝ) * (k : ℝ) * y)) := by funext y; ring
      rw [hEq] at hinv
      convert hinv using 1
      field_simp [hj_pos.ne', hk_pos.ne', hx_pos.ne']
    have h2 : HasDerivAt (fun y : ℝ => (p / (k : ℝ) + q / (j : ℝ)) * Real.log y)
        ((p / (k : ℝ) + q / (j : ℝ)) * (1 / x)) x := by
      simpa [one_div] using (Real.hasDerivAt_log hx_pos.ne').const_mul (p / (k : ℝ) + q / (j : ℝ))
    have h3 : HasDerivAt (fun y : ℝ => p * q * y) (p * q) x := by
      simpa using (hasDerivAt_id' x).const_mul (p * q)
    exact (h1.sub h2).add h3
  have h_cont : ContinuousOn
      (fun x : ℝ => 1 / ((j : ℝ) * (k : ℝ) * x ^ 2) -
        (p / (k : ℝ) + q / (j : ℝ)) * (1 / x) + p * q)
      (Set.uIcc (1 / ((n : ℝ) + 1)) (1 / (n : ℝ))) := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le (by positivity) hx.1
    have hjkx : (j : ℝ) * (k : ℝ) * x ^ 2 ≠ 0 :=
      mul_ne_zero (mul_ne_zero hj_pos.ne' hk_pos.ne') (pow_ne_zero 2 hx_pos.ne')
    exact (((continuousAt_const.div (continuousAt_const.mul (continuousAt_id.pow 2)) hjkx).sub
      (continuousAt_const.mul (continuousAt_const.div continuousAt_id hx_pos.ne'))).add
      continuousAt_const).continuousWithinAt
  rw [h_ae, intervalIntegral.integral_eq_sub_of_hasDerivAt h_deriv h_cont.intervalIntegrable]
  rw [one_div, Real.log_inv, one_div, Real.log_inv]
  have hne : (n : ℝ) ≠ 0 := hn_pos.ne'
  have hne1 : (n : ℝ) + 1 ≠ 0 := by positivity
  field_simp [hj_pos.ne', hk_pos.ne', hne, hne1]
  ring

private lemma sum_Ico_abel (a b : ℕ → ℝ) (ha0 : a 0 = 0) {L : ℕ} (hL : 1 ≤ L) :
    ∑ n ∈ Finset.Ico 1 L, a n * (b (n + 1) - b n) =
      a (L - 1) * b L - ∑ n ∈ Finset.Ico 1 L, (a n - a (n - 1)) * b n := by
  induction L, hL using Nat.le_induction with
  | base => simp [ha0]
  | succ k hk ih =>
    rw [Finset.sum_Ico_succ_top hk, Finset.sum_Ico_succ_top hk, ih]
    simp only [Nat.add_sub_cancel]
    ring

private lemma nat_div_sub_pred_div {j n : ℕ} (hj : 1 ≤ j) (hn : 1 ≤ n) :
    ((n / j : ℕ) : ℝ) - (((n - 1) / j : ℕ) : ℝ) = if j ∣ n then 1 else 0 := by
  by_cases hdvd : j ∣ n
  · rcases hdvd with ⟨m, rfl⟩
    have hm : 1 ≤ m := by
      rcases m with _ | m
      · simp at hn
      · omega
    have h1 : j * m / j = m := Nat.mul_div_right m hj
    have h2 : (j * m - 1) / j = m - 1 := by
      have : j * m - 1 = j * (m - 1) + (j - 1) := by
        calc j * m - 1 = j * (m - 1 + 1) - 1 := by congr 2; omega
          _ = j * (m - 1) + j - 1 := by rw [mul_add, mul_one]
          _ = j * (m - 1) + (j - 1) := by omega
      rw [this, Nat.mul_add_div hj, Nat.div_eq_of_lt (by omega : j - 1 < j), add_zero]
    rw [h1, h2, Nat.cast_sub hm, Nat.cast_one]
    simp
  · have hmod : 1 ≤ n % j := by
      have h0 : n % j ≠ 0 := fun h0 => hdvd (Nat.dvd_of_mod_eq_zero h0)
      omega
    have hmlt : n % j < j := Nat.mod_lt n hj
    have hdiv : n = j * (n / j) + n % j := (Nat.div_add_mod n j).symm
    have hpred : n - 1 = j * (n / j) + (n % j - 1) := by
      conv_lhs => rw [hdiv]
      exact Nat.add_sub_assoc hmod (j * (n / j))
    have h2 : (n - 1) / j = n / j := by
      rw [hpred, Nat.mul_add_div hj, Nat.div_eq_of_lt (by omega : n % j - 1 < j), add_zero]
    rw [h2, sub_self]
    simp [hdvd]

private lemma sum_Ico_ite_dvd (g : ℕ → ℝ) {a B : ℕ} (ha : 1 ≤ a) (hB : 1 ≤ B) :
    ∑ n ∈ Finset.Ico 1 (a * B), (if a ∣ n then g n else 0) =
      ∑ m ∈ Finset.Ico 1 B, g (m * a) := by
  induction B, hB using Nat.le_induction with
  | base =>
    rw [mul_one, Finset.Ico_self, Finset.sum_empty]
    refine Finset.sum_eq_zero fun n hn => ?_
    have hlt : n < a := (Finset.mem_Ico.mp hn).2
    have hpos : 0 < n := (Finset.mem_Ico.mp hn).1
    have hndvd : ¬(a ∣ n) := fun h => absurd (Nat.le_of_dvd hpos h) (not_le_of_gt hlt)
    simp [hndvd]
  | succ k hk ih =>
    have hle1 : 1 ≤ a * k := Nat.mul_pos ha hk
    have hle2 : a * k ≤ a * (k + 1) := Nat.mul_le_mul_left a (Nat.le_succ k)
    rw [← Finset.sum_Ico_consecutive _ hle1 hle2, ih, Finset.sum_Ico_succ_top hk]
    congr 1
    have ha_pos : 0 < a := ha
    have hsingle : ∀ n ∈ Finset.Ico (a * k) (a * (k + 1)), n ≠ a * k →
        (if a ∣ n then g n else 0) = 0 := by
      intro n hn hne
      have hge := (Finset.mem_Ico.mp hn).1
      have hlt := (Finset.mem_Ico.mp hn).2
      have hndvd : ¬(a ∣ n) := by
        rintro ⟨t, rfl⟩
        have ht_gt : k < t := by
          rcases lt_trichotomy k t with hlt' | rfl | hgt'
          · exact hlt'
          · exact absurd rfl hne
          · exfalso; exact (Nat.mul_lt_mul_of_pos_left hgt' ha_pos).not_ge hge
        have ht_ge : k + 1 ≤ t := ht_gt
        exact (Nat.mul_le_mul_left a ht_ge).not_gt hlt
      simp [hndvd]
    rw [Finset.sum_eq_single (a * k) hsingle (fun hmem => by
      exfalso; apply hmem
      simp only [Finset.mem_Ico, Std.le_refl, true_and]
      exact Nat.mul_lt_mul_of_pos_left (Nat.lt_succ_self k) ha_pos)]
    simp [mul_comm k a]

private lemma abel_log_sum_exact {M j k : ℕ} (hM : 1 ≤ M) (hj : 1 ≤ j) (hk : 1 ≤ k) :
    (-(1 : ℝ) / (k : ℝ)) * ∑ n ∈ Finset.Ico 1 (M * j * k),
        ((n / j : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) =
      (Real.log ((Nat.factorial (M * k) : ℕ) : ℝ) -
        (M * k : ℝ) * Real.log ((M * k : ℕ) : ℝ)) / (k : ℝ) := by
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hM_pos : (0 : ℝ) < (M : ℝ) := Nat.cast_pos.mpr hM
  have hL : 1 ≤ M * j * k := Nat.mul_pos (Nat.mul_pos hM hj) hk
  have ha0 : (((0 / j : ℕ) : ℝ)) = 0 := by simp
  have h_abel := sum_Ico_abel (fun n => ((n / j : ℕ) : ℝ)) (fun n => Real.log (n : ℝ)) ha0 hL
  have h_congr1 : ∑ n ∈ Finset.Ico 1 (M * j * k),
      ((n / j : ℕ) : ℝ) * (Real.log (((n + 1 : ℕ) : ℝ)) - Real.log (n : ℝ)) =
      ∑ n ∈ Finset.Ico 1 (M * j * k),
        ((n / j : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) := by
    refine Finset.sum_congr rfl fun n _ => by push_cast; rfl
  rw [← h_congr1, h_abel]
  have h_top_div : (M * j * k - 1) / j = M * k - 1 := by
    have hmul : M * j * k = j * (M * k) := by ring
    have hMk : 1 ≤ M * k := Nat.mul_pos hM hk
    rw [hmul]
    have hdecomp : j * (M * k) - 1 = j * (M * k - 1) + (j - 1) := by
      calc j * (M * k) - 1 = j * (M * k - 1 + 1) - 1 := by congr 2; omega
        _ = j * (M * k - 1) + j - 1 := by rw [mul_add, mul_one]
        _ = j * (M * k - 1) + (j - 1) := by omega
    rw [hdecomp, Nat.mul_add_div hj, Nat.div_eq_of_lt (by omega : j - 1 < j), add_zero]
  have h_diff_congr : ∑ n ∈ Finset.Ico 1 (M * j * k),
      (((n / j : ℕ) : ℝ) - (((n - 1) / j : ℕ) : ℝ)) * Real.log (n : ℝ) =
      ∑ n ∈ Finset.Ico 1 (j * (M * k)), if j ∣ n then Real.log (n : ℝ) else 0 := by
    rw [show M * j * k = j * (M * k) by ring]
    refine Finset.sum_congr rfl fun n hn => ?_
    rw [nat_div_sub_pred_div hj (Finset.mem_Ico.mp hn).1]
    split_ifs <;> simp
  have hMk : 1 ≤ M * k := Nat.mul_pos hM hk
  rw [h_top_div, h_diff_congr, sum_Ico_ite_dvd (fun n => Real.log (n : ℝ)) hj hMk]
  have h_log_prod : ∀ A : ℕ, 1 ≤ A →
      ∑ m ∈ Finset.Ico 1 A, Real.log ((m * j : ℕ) : ℝ) =
        ((A : ℝ) - 1) * Real.log (j : ℝ) + Real.log ((Nat.factorial (A - 1) : ℕ) : ℝ) := by
    intro A hA
    induction A, hA using Nat.le_induction with
    | base => simp
    | succ t ht ih =>
      rw [Finset.sum_Ico_succ_top ht, ih]
      simp only [Nat.add_sub_cancel]
      have ht_pos : (0 : ℝ) < (t : ℝ) := Nat.cast_pos.mpr ht
      have hfact_eq : ((Nat.factorial t : ℕ) : ℝ) =
          (t : ℝ) * ((Nat.factorial (t - 1) : ℕ) : ℝ) := by
        have hmul := (Nat.mul_factorial_pred (by omega : t ≠ 0)).symm
        exact_mod_cast hmul
      rw [Nat.cast_mul, Real.log_mul ht_pos.ne' hj_pos.ne', hfact_eq,
        Real.log_mul ht_pos.ne' (Nat.cast_pos.mpr (Nat.factorial_pos (t - 1))).ne']
      push_cast
      ring
  rw [h_log_prod (M * k) hMk]
  have hMk_pos : (0 : ℝ) < ((M * k : ℕ) : ℝ) := Nat.cast_pos.mpr hMk
  have hfact_top : ((Nat.factorial (M * k) : ℕ) : ℝ) =
      ((M * k : ℕ) : ℝ) * ((Nat.factorial (M * k - 1) : ℕ) : ℝ) := by
    exact_mod_cast (Nat.mul_factorial_pred (by omega : M * k ≠ 0)).symm
  rw [hfact_top, Real.log_mul hMk_pos.ne' (Nat.cast_pos.mpr (Nat.factorial_pos _)).ne',
    Nat.cast_sub hMk, Nat.cast_one]
  push_cast
  have hlogL : Real.log ((M : ℝ) * (j : ℝ) * (k : ℝ)) =
      Real.log ((M : ℝ) * (k : ℝ)) + Real.log (j : ℝ) := by
    rw [show (M : ℝ) * (j : ℝ) * (k : ℝ) = ((M : ℝ) * (k : ℝ)) * (j : ℝ) by ring,
      Real.log_mul (mul_pos hM_pos hk_pos).ne' hj_pos.ne']
  rw [hlogL]
  ring

private lemma nat_div_add_pred_div_identity {n b : ℕ} (hn : 1 ≤ n) (hb : 1 ≤ b) :
    ((n / b : ℕ) : ℝ) + (((n - 1) / b : ℕ) : ℝ) =
      2 * ((n : ℝ) / (b : ℝ)) - 1 -
        (Int.fract ((n : ℝ) / (b : ℝ)) - Int.fract (-(n : ℝ) / (b : ℝ))) := by
  have hb_pos : (0 : ℝ) < (b : ℝ) := Nat.cast_pos.mpr hb
  by_cases hdvd : b ∣ n
  · rcases hdvd with ⟨q, rfl⟩
    have hq : 1 ≤ q := by
      rcases q with _ | q
      · simp at hn
      · omega
    have h1 : b * q / b = q := Nat.mul_div_right q hb
    have h2 : (b * q - 1) / b = q - 1 := by
      have hdecomp : b * q - 1 = b * (q - 1) + (b - 1) := by
        calc b * q - 1 = b * (q - 1 + 1) - 1 := by congr 2; omega
          _ = b * (q - 1) + b - 1 := by rw [mul_add, mul_one]
          _ = b * (q - 1) + (b - 1) := by omega
      rw [hdecomp, Nat.mul_add_div hb, Nat.div_eq_of_lt (by omega : b - 1 < b), add_zero]
    have hf1 : Int.fract (((b * q : ℕ) : ℝ) / (b : ℝ)) = 0 := by
      rw [Nat.cast_mul, mul_div_cancel_left₀ _ hb_pos.ne']
      exact Int.fract_natCast q
    have hf2 : Int.fract (-(((b * q : ℕ) : ℝ)) / (b : ℝ)) = 0 := by
      rw [Nat.cast_mul, neg_div, mul_div_cancel_left₀ _ hb_pos.ne',
        ← Int.cast_natCast q, ← Int.cast_neg]
      exact Int.fract_intCast (-(q : ℤ))
    rw [h1, h2, hf1, hf2, Nat.cast_mul, mul_div_cancel_left₀ _ hb_pos.ne', Nat.cast_sub hq]
    push_cast
    ring
  · have hmod_pos : 1 ≤ n % b := by
      have : n % b ≠ 0 := fun h => hdvd (Nat.dvd_of_mod_eq_zero h)
      omega
    have hmod_lt : n % b < b := Nat.mod_lt n hb
    let q : ℕ := n / b
    let r : ℕ := n % b
    have hdiv : n = b * q + r := (Nat.div_add_mod n b).symm
    have hpred : n - 1 = b * q + (r - 1) := by omega
    have h2 : (n - 1) / b = q := by
      rw [hpred, Nat.mul_add_div hb, Nat.div_eq_of_lt (by omega : r - 1 < b), add_zero]
    have hr_pos : (0 : ℝ) < (r : ℝ) := Nat.cast_pos.mpr hmod_pos
    have hbr_pos : (0 : ℝ) < (b : ℝ) - (r : ℝ) := by
      have : (r : ℝ) < (b : ℝ) := by exact_mod_cast hmod_lt
      linarith
    have h_pos_div : (n : ℝ) / (b : ℝ) = (q : ℝ) + (r : ℝ) / (b : ℝ) := by
      rw [hdiv]; push_cast; field_simp [hb_pos.ne']
    have hf1 : Int.fract ((n : ℝ) / (b : ℝ)) = (r : ℝ) / (b : ℝ) := by
      rw [h_pos_div, add_comm, Int.fract_add_natCast, Int.fract_eq_self]
      exact ⟨by positivity, (div_lt_one hb_pos).mpr (by exact_mod_cast hmod_lt)⟩
    have h_neg_div : -(n : ℝ) / (b : ℝ) = ((b : ℝ) - (r : ℝ)) / (b : ℝ) + (-(q + 1 : ℤ) : ℤ) := by
      rw [hdiv]; push_cast; field_simp [hb_pos.ne']; ring
    have hf2 : Int.fract (-(n : ℝ) / (b : ℝ)) = ((b : ℝ) - (r : ℝ)) / (b : ℝ) := by
      rw [h_neg_div, Int.fract_add_intCast, Int.fract_eq_self]
      refine ⟨by positivity, (div_lt_one hb_pos).mpr ?_⟩
      linarith
    rw [h2, hf1, hf2, h_pos_div]
    change (q : ℝ) + (q : ℝ) = _
    field_simp [hb_pos.ne']
    ring

private noncomputable def cotApproxSum (a b M : ℕ) : ℝ :=
  ∑ r ∈ Finset.Ico 1 b,
    Int.fract ((r : ℝ) * (a : ℝ) / (b : ℝ)) *
      ∑ q ∈ Finset.range M,
        (1 / ((q : ℝ) * (b : ℝ) + (r : ℝ)) -
          1 / (((q + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ)))

private lemma sum_Ico_eq_sum_Ico_sum_range (f : ℕ → ℝ) (b M : ℕ) (hb : 1 ≤ b)
    (hf0 : ∀ q : ℕ, f (q * b) = 0) :
    ∑ m ∈ Finset.Ico 1 (M * b), f m =
      ∑ r ∈ Finset.Ico 1 b, ∑ q ∈ Finset.range M, f (q * b + r) := by
  have h2 : ∑ m ∈ Finset.range (M * b), f m =
      ∑ q ∈ Finset.range M, ∑ r ∈ Finset.range b, f (q * b + r) := by
    induction M with
    | zero => simp
    | succ M ih =>
      rw [Nat.succ_mul, Finset.sum_range_add, ih, Finset.sum_range_succ]
  have h1 : ∑ m ∈ Finset.Ico 1 (M * b), f m = ∑ m ∈ Finset.range (M * b), f m := by
    by_cases hM : M = 0
    · subst hM; simp
    · have hMb : 1 ≤ M * b := Nat.mul_pos (Nat.pos_of_ne_zero hM) hb
      have hsplit : Finset.range (M * b) = insert 0 (Finset.Ico 1 (M * b)) := by
        ext m; simp [Finset.mem_range, Finset.mem_Ico]; omega
      rw [hsplit, Finset.sum_insert (by simp), show f 0 = 0 by simpa using hf0 0, zero_add]
  rw [h1, h2, Finset.sum_comm]
  have h0b : Finset.range b = insert 0 (Finset.Ico 1 b) := by
    ext r; simp [Finset.mem_range, Finset.mem_Ico]; omega
  rw [h0b, Finset.sum_insert (by simp)]
  have hzero : ∑ q ∈ Finset.range M, f (q * b + 0) = 0 :=
    Finset.sum_eq_zero fun q _ => by simpa using hf0 q
  rw [hzero, zero_add]

private lemma sum_Ico_fract_diff_div_eq_cotApproxSum {a b M : ℕ} (hb : 1 ≤ b) :
    ∑ m ∈ Finset.Ico 1 (M * b),
        (Int.fract ((m : ℝ) * (a : ℝ) / (b : ℝ)) -
          Int.fract (-((m : ℝ) * (a : ℝ) / (b : ℝ)))) / (m : ℝ) =
      cotApproxSum a b M := by
  have hb_pos : (0 : ℝ) < (b : ℝ) := Nat.cast_pos.mpr hb
  let f : ℕ → ℝ := fun m =>
    (Int.fract ((m : ℝ) * (a : ℝ) / (b : ℝ)) -
      Int.fract (-((m : ℝ) * (a : ℝ) / (b : ℝ)))) / (m : ℝ)
  have hf0 : ∀ q : ℕ, f (q * b) = 0 := by
    intro q
    dsimp [f]
    have hpos : Int.fract (((q * b : ℕ) : ℝ) * (a : ℝ) / (b : ℝ)) = 0 := by
      rw [Nat.cast_mul, show (q : ℝ) * (b : ℝ) * (a : ℝ) / (b : ℝ) = ((q * a : ℕ) : ℝ) by
        field_simp [hb_pos.ne']; push_cast; ring]
      exact Int.fract_natCast (q * a)
    have hneg : Int.fract (-(((q * b : ℕ) : ℝ) * (a : ℝ) / (b : ℝ))) = 0 := by
      rw [Nat.cast_mul, show -((q : ℝ) * (b : ℝ) * (a : ℝ) / (b : ℝ)) =
          ((-((q * a : ℕ) : ℤ) : ℤ) : ℝ) by
        field_simp [hb_pos.ne']; push_cast; ring]
      exact Int.fract_intCast _
    rw [hpos, hneg, sub_self, zero_div]
  change ∑ m ∈ Finset.Ico 1 (M * b), f m = cotApproxSum a b M
  rw [sum_Ico_eq_sum_Ico_sum_range f b M hb hf0]
  have hper_pos : ∀ q r : ℕ,
      Int.fract (((q * b + r : ℕ) : ℝ) * (a : ℝ) / (b : ℝ)) =
        Int.fract ((r : ℝ) * (a : ℝ) / (b : ℝ)) := by
    intro q r
    have heq : ((q * b + r : ℕ) : ℝ) * (a : ℝ) / (b : ℝ) =
        (r : ℝ) * (a : ℝ) / (b : ℝ) + ((q * a : ℕ) : ℝ) := by
      push_cast; field_simp [hb_pos.ne']; ring
    rw [heq, Int.fract_add_natCast]
  have hper_neg : ∀ q r : ℕ,
      Int.fract (-(((q * b + r : ℕ) : ℝ) * (a : ℝ) / (b : ℝ))) =
        Int.fract (-((r : ℝ) * (a : ℝ) / (b : ℝ))) := by
    intro q r
    have heq : -(((q * b + r : ℕ) : ℝ) * (a : ℝ) / (b : ℝ)) =
        -((r : ℝ) * (a : ℝ) / (b : ℝ)) + (-(q * a : ℤ) : ℤ) := by
      push_cast; field_simp [hb_pos.ne']; ring
    rw [heq, Int.fract_add_intCast]
  have hsplit_inner : ∀ r ∈ Finset.Ico 1 b,
      ∑ q ∈ Finset.range M, f (q * b + r) =
        Int.fract ((r : ℝ) * (a : ℝ) / (b : ℝ)) *
            ∑ q ∈ Finset.range M, (1 / ((q : ℝ) * (b : ℝ) + (r : ℝ))) -
          Int.fract (-((r : ℝ) * (a : ℝ) / (b : ℝ))) *
            ∑ q ∈ Finset.range M, (1 / ((q : ℝ) * (b : ℝ) + (r : ℝ))) := by
    intro r _
    have hsplit1 : ∀ q : ℕ, f (q * b + r) =
        Int.fract ((r : ℝ) * (a : ℝ) / (b : ℝ)) * (1 / ((q : ℝ) * (b : ℝ) + (r : ℝ))) -
        Int.fract (-((r : ℝ) * (a : ℝ) / (b : ℝ))) * (1 / ((q : ℝ) * (b : ℝ) + (r : ℝ))) := by
      intro q
      dsimp [f]
      rw [hper_pos, hper_neg, sub_div]
      push_cast
      ring
    simp_rw [hsplit1, Finset.sum_sub_distrib, ← Finset.mul_sum]
  rw [Finset.sum_congr rfl hsplit_inner, Finset.sum_sub_distrib]
  have hreflect :
      ∑ r ∈ Finset.Ico 1 b,
          Int.fract (-((r : ℝ) * (a : ℝ) / (b : ℝ))) *
            ∑ q ∈ Finset.range M, (1 / ((q : ℝ) * (b : ℝ) + (r : ℝ))) =
        ∑ r ∈ Finset.Ico 1 b,
          Int.fract ((r : ℝ) * (a : ℝ) / (b : ℝ)) *
            ∑ q ∈ Finset.range M, (1 / (((q + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ))) := by
    refine Finset.sum_bij (fun r _ => b - r) ?_ ?_ ?_ ?_
    · intro r hr
      rw [Finset.mem_Ico] at hr ⊢
      omega
    · intro r₁ hr₁ r₂ hr₂ heq
      rw [Finset.mem_Ico] at hr₁ hr₂
      omega
    · intro r hr
      rw [Finset.mem_Ico] at hr
      exact ⟨b - r, Finset.mem_Ico.mpr ⟨by omega, by omega⟩, by omega⟩
    · intro r hr
      rw [Finset.mem_Ico] at hr
      have hbr : ((b - r : ℕ) : ℝ) = (b : ℝ) - (r : ℝ) := Nat.cast_sub hr.2.le
      have hfrac : Int.fract (-((r : ℝ) * (a : ℝ) / (b : ℝ))) =
          Int.fract (((b - r : ℕ) : ℝ) * (a : ℝ) / (b : ℝ)) := by
        have heq : (((b - r : ℕ) : ℝ) * (a : ℝ) / (b : ℝ)) =
            -((r : ℝ) * (a : ℝ) / (b : ℝ)) + ((a : ℤ) : ℝ) := by
          rw [hbr]; push_cast; field_simp [hb_pos.ne']; ring
        rw [heq, Int.fract_add_intCast]
      rw [hfrac]
      congr 1
      refine Finset.sum_congr rfl fun q _ => ?_
      rw [hbr]
      push_cast
      ring_nf
  rw [hreflect, ← Finset.sum_sub_distrib]
  dsimp [cotApproxSum]
  refine Finset.sum_congr rfl fun r _ => ?_
  rw [← mul_sub, ← Finset.sum_sub_distrib]

private lemma halfSum_exact {a b M : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) (hM : 1 ≤ M) :
    ∑ m ∈ Finset.Ico 1 (M * b),
        (((m * a / b : ℕ) : ℝ) + (((m * a - 1) / b : ℕ) : ℝ)) /
          (2 * (m : ℝ) * (a : ℝ)) =
      (M : ℝ) - 1 / (b : ℝ) -
        (1 / (2 * (a : ℝ))) * ∑ m ∈ Finset.Ico 1 (M * b), (1 : ℝ) / (m : ℝ) -
        (1 / (2 * (a : ℝ))) * cotApproxSum a b M := by
  have ha_pos : (0 : ℝ) < (a : ℝ) := Nat.cast_pos.mpr ha
  have hb_pos : (0 : ℝ) < (b : ℝ) := Nat.cast_pos.mpr hb
  have hpt : ∀ m ∈ Finset.Ico 1 (M * b),
      (((m * a / b : ℕ) : ℝ) + (((m * a - 1) / b : ℕ) : ℝ)) /
        (2 * (m : ℝ) * (a : ℝ)) =
        (1 / (b : ℝ) - 1 / (2 * (a : ℝ)) * (1 / (m : ℝ))) -
          (1 / (2 * (a : ℝ))) *
            ((Int.fract ((m : ℝ) * (a : ℝ) / (b : ℝ)) -
              Int.fract (-((m : ℝ) * (a : ℝ) / (b : ℝ)))) / (m : ℝ)) := by
    intro m hm
    have hm_pos : 1 ≤ m := (Finset.mem_Ico.mp hm).1
    have hma_pos : 1 ≤ m * a := Nat.mul_pos hm_pos ha
    have hid := nat_div_add_pred_div_identity hma_pos hb
    push_cast at hid
    rw [hid]
    have hm_ne : (m : ℝ) ≠ 0 := (Nat.cast_pos.mpr hm_pos).ne'
    field_simp [ha_pos.ne', hb_pos.ne', hm_ne]
  rw [Finset.sum_congr rfl hpt, Finset.sum_sub_distrib, Finset.sum_sub_distrib,
    ← Finset.mul_sum, ← Finset.mul_sum, sum_Ico_fract_diff_div_eq_cotApproxSum hb]
  have hMb : 1 ≤ M * b := Nat.mul_pos hM hb
  rw [Finset.sum_const, Nat.card_Ico, nsmul_eq_mul, Nat.cast_sub hMb, Nat.cast_one]
  push_cast
  field_simp [hb_pos.ne']

private lemma tendsto_cotApproxSum_term {b r : ℕ} (hr : 1 ≤ r) (hrb : r < b) :
    Tendsto
      (fun M : ℕ => ∑ q ∈ Finset.range M,
        (1 / ((q : ℝ) * (b : ℝ) + (r : ℝ)) -
          1 / (((q + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ))))
      atTop
      (nhds ((Real.pi / (b : ℝ)) *
        (Real.cos (Real.pi * (r : ℝ) / (b : ℝ)) / Real.sin (Real.pi * (r : ℝ) / (b : ℝ))))) := by
  have hr_pos : (0 : ℝ) < (r : ℝ) := Nat.cast_pos.mpr hr
  have hb_pos : (0 : ℝ) < (b : ℝ) := Nat.cast_pos.mpr (lt_trans hr hrb)
  let x : ℂ := (r : ℂ) / (b : ℂ)
  have hx_mem : x ∈ Complex.integerComplement := by
    rintro ⟨n, hn⟩
    have hre : (n : ℝ) = (r : ℝ) / (b : ℝ) := by
      simpa [x, Complex.div_ofReal_re] using congr_arg Complex.re hn
    have hlt1 : (0 : ℝ) < (r : ℝ) / (b : ℝ) := div_pos hr_pos hb_pos
    have hlt2 : (r : ℝ) / (b : ℝ) < 1 := (div_lt_one hb_pos).mpr (by exact_mod_cast hrb)
    have hn0 : (0 : ℤ) < n := by exact_mod_cast hre ▸ hlt1
    have hn1 : n < (1 : ℤ) := by exact_mod_cast hre ▸ hlt2
    omega
  have h_sum_c := (summable_cotTerm hx_mem).hasSum.tendsto_sum_nat
  rw [← cot_series_rep' hx_mem] at h_sum_c
  have h_re_lim := Complex.reCLM.continuous.continuousAt.tendsto.comp h_sum_c
  have h_cot_re : ((Complex.reCLM : ℂ →L[ℝ] ℝ)
      ((Real.pi : ℂ) * Complex.cot ((Real.pi : ℂ) * x) - 1 / x)) / (b : ℝ) =
      (Real.pi / (b : ℝ)) *
        (Real.cos (Real.pi * (r : ℝ) / (b : ℝ)) / Real.sin (Real.pi * (r : ℝ) / (b : ℝ))) -
        1 / (r : ℝ) := by
    have hx_real : ((Real.pi : ℂ) * x) = ((Real.pi * (r : ℝ) / (b : ℝ) : ℝ) : ℂ) := by
      dsimp [x]; push_cast; ring
    have hcot_real : Complex.cot ((Real.pi * (r : ℝ) / (b : ℝ) : ℝ) : ℂ) =
        ((Real.cos (Real.pi * (r : ℝ) / (b : ℝ)) /
          Real.sin (Real.pi * (r : ℝ) / (b : ℝ)) : ℝ) : ℂ) := by
      rw [Complex.cot, ← Complex.ofReal_cos, ← Complex.ofReal_sin, Complex.ofReal_div]
    have hdiv_re : ((Complex.reCLM : ℂ →L[ℝ] ℝ) (1 / x)) = (b : ℝ) / (r : ℝ) := by
      have hx1 : 1 / x = (((b : ℝ) / (r : ℝ) : ℝ) : ℂ) := by
        dsimp [x]; rw [one_div_div]; push_cast; rfl
      rw [hx1, Complex.reCLM_apply, Complex.ofReal_re]
    rw [Complex.reCLM_apply, Complex.sub_re, hx_real, hcot_real]
    rw [← Complex.ofReal_mul, Complex.ofReal_re]
    have hre1 : (1 / x).re = (b : ℝ) / (r : ℝ) := by
      simpa [Complex.reCLM_apply] using hdiv_re
    rw [hre1]
    field_simp [hb_pos.ne', hr_pos.ne']
  have h_re_div : Tendsto
      (fun N : ℕ => ((Complex.reCLM : ℂ →L[ℝ] ℝ)
        (∑ n ∈ Finset.range N, (cotTerm x n))) / (b : ℝ))
      atTop
      (nhds ((Real.pi / (b : ℝ)) *
        (Real.cos (Real.pi * (r : ℝ) / (b : ℝ)) / Real.sin (Real.pi * (r : ℝ) / (b : ℝ))) -
          1 / (r : ℝ))) := by
    rw [← h_cot_re]
    exact h_re_lim.div_const (b : ℝ)
  have h_sum_real : ∀ N : ℕ,
      ((Complex.reCLM : ℂ →L[ℝ] ℝ) (∑ n ∈ Finset.range N, (cotTerm x n))) / (b : ℝ) =
        ∑ n ∈ Finset.range N,
          (1 / (((n + 1 : ℕ) : ℝ) * (b : ℝ) + (r : ℝ)) -
            1 / (((n + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ))) := by
    intro N
    rw [map_sum, Finset.sum_div]
    refine Finset.sum_congr rfl fun n _ => ?_
    have hnb1 : ((n + 1 : ℕ) : ℝ) * (b : ℝ) + (r : ℝ) ≠ 0 := by positivity
    have hnb2 : ((n + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ) ≠ 0 := by
      have h1 : (r : ℝ) < (b : ℝ) := by exact_mod_cast hrb
      have h2 : (1 : ℝ) ≤ ((n + 1 : ℕ) : ℝ) := by exact_mod_cast Nat.succ_pos n
      nlinarith
    have h_real_term :
        (1 / ((r : ℝ) / (b : ℝ) - ((n : ℝ) + 1)) + 1 / ((r : ℝ) / (b : ℝ) + ((n : ℝ) + 1))) =
          (1 / (((n + 1 : ℕ) : ℝ) * (b : ℝ) + (r : ℝ)) -
            1 / (((n + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ))) * (b : ℝ) := by
      have hm_eq : (r : ℝ) / (b : ℝ) - ((n : ℝ) + 1) =
          -((((n + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ)) / (b : ℝ)) := by
        push_cast; field_simp [hb_pos.ne']; ring
      have hp_eq : (r : ℝ) / (b : ℝ) + ((n : ℝ) + 1) =
          (((n + 1 : ℕ) : ℝ) * (b : ℝ) + (r : ℝ)) / (b : ℝ) := by
        push_cast; field_simp [hb_pos.ne']; ring
      rw [hm_eq, hp_eq]
      field_simp [hb_pos.ne', hnb1, hnb2]
      ring
    have hterm_c : cotTerm x n =
        ((((1 : ℝ) / (((n + 1 : ℕ) : ℝ) * (b : ℝ) + (r : ℝ)) -
          1 / (((n + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ))) * (b : ℝ) : ℝ) : ℂ) := by
      rw [← h_real_term]
      dsimp [cotTerm, x]
      push_cast
      rfl
    rw [hterm_c, Complex.reCLM_apply, Complex.ofReal_re, mul_div_cancel_right₀ _ hb_pos.ne']
  have h_shifted : Tendsto
      (fun M : ℕ => 1 / (r : ℝ) + ∑ n ∈ Finset.range (M - 1),
        (1 / (((n + 1 : ℕ) : ℝ) * (b : ℝ) + (r : ℝ)) -
          1 / (((n + 1 : ℕ) : ℝ) * (b : ℝ) - (r : ℝ))))
      atTop
      (nhds ((Real.pi / (b : ℝ)) *
        (Real.cos (Real.pi * (r : ℝ) / (b : ℝ)) / Real.sin (Real.pi * (r : ℝ) / (b : ℝ))))) := by
    have h_inner := h_re_div.congr (fun N => h_sum_real N)
    have h_comp := h_inner.comp (tendsto_sub_atTop_nat 1)
    simpa [add_sub_cancel] using h_comp.const_add (1 / (r : ℝ))
  have h_tail : Tendsto (fun M : ℕ => 1 / ((M : ℝ) * (b : ℝ) - (r : ℝ))) atTop (nhds 0) := by
    have h_top : Tendsto (fun M : ℕ => (M : ℝ) * (b : ℝ) - (r : ℝ)) atTop atTop := by
      rw [Filter.tendsto_atTop_atTop]
      intro B
      obtain ⟨M0, hM0⟩ := exists_nat_gt ((B + (r : ℝ)) / (b : ℝ))
      exact ⟨M0, fun M hM => by
        have : (M0 : ℝ) ≤ (M : ℝ) := by exact_mod_cast hM
        nlinarith [(div_lt_iff₀ hb_pos).mp hM0]⟩
    simpa [Function.comp_def, one_div] using tendsto_inv_atTop_zero.comp h_top
  simpa only [sub_zero] using (h_shifted.sub h_tail).congr' (by
    filter_upwards [eventually_ge_atTop 1] with M hM
    obtain ⟨m, rfl⟩ := Nat.exists_eq_add_of_le' hM
    simp only [Nat.add_sub_cancel]
    induction m with
    | zero => simp
    | succ k ih =>
      rw [Finset.sum_range_succ, Finset.sum_range_succ (n := k + 1), ← ih (Nat.succ_pos k)]
      push_cast
      ring)

private lemma tendsto_cotApproxSum (a b : ℕ) :
    Tendsto (cotApproxSum a b) atTop (nhds ((Real.pi / (b : ℝ)) * vasyuninCotSum b a)) := by
  dsimp [cotApproxSum, vasyuninCotSum]
  rw [Finset.mul_sum]
  refine tendsto_finsetSum (Finset.Ico 1 b) fun r hr => ?_
  have hrb := Finset.mem_Ico.mp hr
  have hlim := tendsto_cotApproxSum_term hrb.1 hrb.2
  simpa [mul_left_comm, mul_assoc, mul_comm] using hlim.const_mul
    (Int.fract ((r : ℝ) * (a : ℝ) / (b : ℝ)))

private lemma tendsto_mul_nat_atTop {k : ℕ} (hk : 1 ≤ k) :
    Tendsto (fun M : ℕ => M * k) atTop atTop :=
  Filter.tendsto_atTop_atTop.mpr fun N =>
    ⟨N, fun M hM => le_trans hM (Nat.le_mul_of_pos_right M hk)⟩

private lemma tendsto_stirling_log_term (k : ℕ) (hk : 1 ≤ k) :
    Tendsto (fun M : ℕ =>
        Real.log ((Nat.factorial (M * k) : ℕ) : ℝ) -
          (M * k : ℝ) * Real.log ((M * k : ℕ) : ℝ) + (M * k : ℝ) -
          (1 / 2 : ℝ) * Real.log ((M * k : ℕ) : ℝ))
      atTop (nhds ((1 / 2 : ℝ) * Real.log (2 * Real.pi))) := by
  have h_log_st : Tendsto (fun n : ℕ => Real.log (Stirling.stirlingSeq n))
      atTop (nhds (Real.log √Real.pi)) :=
    (Real.continuousAt_log (Real.sqrt_pos.mpr Real.pi_pos).ne').tendsto.comp
      Stirling.tendsto_stirlingSeq_sqrt_pi
  have h_comp := h_log_st.comp (tendsto_mul_nat_atTop hk)
  have h_lim_eq : Real.log √Real.pi + (1 / 2 : ℝ) * Real.log 2 =
      (1 / 2 : ℝ) * Real.log (2 * Real.pi) := by
    rw [Real.sqrt_eq_rpow, Real.log_rpow Real.pi_pos, Real.log_mul (by norm_num) Real.pi_pos.ne']
    ring
  rw [← h_lim_eq]
  refine (h_comp.add tendsto_const_nhds).congr' ?_
  filter_upwards [eventually_ge_atTop 1] with M hM
  have hMk : 1 ≤ M * k := Nat.mul_pos hM hk
  have hMk_pos : (0 : ℝ) < ((M * k : ℕ) : ℝ) := Nat.cast_pos.mpr hMk
  dsimp [Function.comp_def, Stirling.stirlingSeq]
  have hfact_pos : (0 : ℝ) < ((Nat.factorial (M * k) : ℕ) : ℝ) :=
    Nat.cast_pos.mpr (Nat.factorial_pos _)
  have hden_pos : (0 : ℝ) < √(2 * ((M * k : ℕ) : ℝ)) * (((M * k : ℕ) : ℝ) / Real.exp 1) ^ (M * k) :=
    mul_pos (Real.sqrt_pos.mpr (by positivity)) (pow_pos (div_pos hMk_pos (Real.exp_pos 1)) _)
  rw [Real.log_div hfact_pos.ne' hden_pos.ne',
    Real.log_mul (Real.sqrt_pos.mpr (by positivity)).ne'
      (pow_pos (div_pos hMk_pos (Real.exp_pos 1)) _).ne',
    Real.log_pow, Real.log_div hMk_pos.ne' (Real.exp_pos 1).ne', Real.log_exp,
    Real.sqrt_eq_rpow, Real.log_rpow (by positivity : 0 < 2 * ((M * k : ℕ) : ℝ)),
    Real.log_mul (by norm_num) hMk_pos.ne']
  push_cast
  ring

private lemma tendsto_harmonic_Ico_sub_log (b : ℕ) (hb : 1 ≤ b) :
    Tendsto (fun M : ℕ =>
        (∑ m ∈ Finset.Ico 1 (M * b), (1 : ℝ) / (m : ℝ)) - Real.log ((M * b : ℕ) : ℝ))
      atTop (nhds Real.eulerMascheroniConstant) := by
  have ht := Real.tendsto_eulerMascheroniSeq'.comp (tendsto_mul_nat_atTop hb)
  have h0 : Tendsto (fun M : ℕ => (1 : ℝ) / ((M * b : ℕ) : ℝ)) atTop (nhds 0) := by
    simpa [Function.comp_def, one_div] using
      tendsto_inv_atTop_zero.comp
        ((tendsto_natCast_atTop_atTop (R := ℝ)).comp (tendsto_mul_nat_atTop hb))
  simpa only [sub_zero] using (ht.sub h0).congr' (by
    filter_upwards [eventually_ge_atTop 1] with M hM
    have hMb : 1 ≤ M * b := Nat.mul_pos hM hb
    have hMb_ne : M * b ≠ 0 := by omega
    dsimp [Function.comp_def, Real.eulerMascheroniSeq']
    rw [harmonic_eq_sum_Icc, ← Finset.Ico_succ_right_eq_Icc]
    simp only [hMb_ne, ↓reduceIte]
    have hsplit : Finset.Ico 1 (Order.succ (M * b)) = insert (M * b) (Finset.Ico 1 (M * b)) := by
      ext m; simp [Finset.mem_Ico]; omega
    rw [hsplit, Finset.sum_insert (by simp [Finset.mem_Ico])]
    ring)

private lemma abel_cross_sum_exact {M j k : ℕ} (hM : 1 ≤ M) (hj : 1 ≤ j) (hk : 1 ≤ k) :
    ∑ n ∈ Finset.Ico 1 (M * j * k),
        ((n / j : ℕ) : ℝ) * ((n / k : ℕ) : ℝ) * (1 / (n : ℝ) - 1 / ((n : ℝ) + 1)) =
      -((M : ℝ) * (k : ℝ) - 1) * ((M : ℝ) * (j : ℝ) - 1) / ((M : ℝ) * (j : ℝ) * (k : ℝ)) +
        ((M : ℝ) - 1 / (k : ℝ) - (1 / (2 * (j : ℝ))) *
          ∑ m ∈ Finset.Ico 1 (M * k), (1 : ℝ) / (m : ℝ) -
          (1 / (2 * (j : ℝ))) * cotApproxSum j k M) +
        ((M : ℝ) - 1 / (j : ℝ) - (1 / (2 * (k : ℝ))) *
          ∑ m ∈ Finset.Ico 1 (M * j), (1 : ℝ) / (m : ℝ) -
          (1 / (2 * (k : ℝ))) * cotApproxSum k j M) := by
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hM_pos : (0 : ℝ) < (M : ℝ) := Nat.cast_pos.mpr hM
  have hL : 1 ≤ M * j * k := Nat.mul_pos (Nat.mul_pos hM hj) hk
  have ha0 : ((0 / j : ℕ) : ℝ) * ((0 / k : ℕ) : ℝ) = 0 := by simp
  have h_abel := sum_Ico_abel (fun n => ((n / j : ℕ) : ℝ) * ((n / k : ℕ) : ℝ))
    (fun n => -(1 : ℝ) / (n : ℝ)) ha0 hL
  have h_congr1 : ∑ n ∈ Finset.Ico 1 (M * j * k),
      ((n / j : ℕ) : ℝ) * ((n / k : ℕ) : ℝ) * (-(1 : ℝ) / ((n + 1 : ℕ) : ℝ) - -(1 : ℝ) / (n : ℝ)) =
      ∑ n ∈ Finset.Ico 1 (M * j * k),
        ((n / j : ℕ) : ℝ) * ((n / k : ℕ) : ℝ) * (1 / (n : ℝ) - 1 / ((n : ℝ) + 1)) := by
    refine Finset.sum_congr rfl fun n _ => by push_cast; ring
  rw [← h_congr1, h_abel]
  have h_top_j : (M * j * k - 1) / j = M * k - 1 := by
    have hMk : 1 ≤ M * k := Nat.mul_pos hM hk
    rw [show M * j * k = j * (M * k) by ring]
    have hdecomp : j * (M * k) - 1 = j * (M * k - 1) + (j - 1) := by
      calc j * (M * k) - 1 = j * (M * k - 1 + 1) - 1 := by congr 2; omega
        _ = j * (M * k - 1) + j - 1 := by rw [mul_add, mul_one]
        _ = j * (M * k - 1) + (j - 1) := by omega
    rw [hdecomp, Nat.mul_add_div hj, Nat.div_eq_of_lt (by omega : j - 1 < j), add_zero]
  have h_top_k : (M * j * k - 1) / k = M * j - 1 := by
    have hMj : 1 ≤ M * j := Nat.mul_pos hM hj
    rw [show M * j * k = k * (M * j) by ring]
    have hdecomp : k * (M * j) - 1 = k * (M * j - 1) + (k - 1) := by
      calc k * (M * j) - 1 = k * (M * j - 1 + 1) - 1 := by congr 2; omega
        _ = k * (M * j - 1) + k - 1 := by rw [mul_add, mul_one]
        _ = k * (M * j - 1) + (k - 1) := by omega
    rw [hdecomp, Nat.mul_add_div hk, Nat.div_eq_of_lt (by omega : k - 1 < k), add_zero]
  rw [h_top_j, h_top_k]
  have h_symm : -∑ n ∈ Finset.Ico 1 (M * j * k),
      (((n / j : ℕ) : ℝ) * ((n / k : ℕ) : ℝ) -
        (((n - 1) / j : ℕ) : ℝ) * (((n - 1) / k : ℕ) : ℝ)) * (-(1 : ℝ) / (n : ℝ)) =
      (∑ n ∈ Finset.Ico 1 (j * (M * k)),
        if j ∣ n then (((n / k : ℕ) : ℝ) + (((n - 1) / k : ℕ) : ℝ)) / (2 * (n : ℝ)) else 0) +
      (∑ n ∈ Finset.Ico 1 (k * (M * j)),
        if k ∣ n then (((n / j : ℕ) : ℝ) + (((n - 1) / j : ℕ) : ℝ)) / (2 * (n : ℝ)) else 0) := by
    have hL1 : M * j * k = j * (M * k) := by ring
    have hL2 : M * j * k = k * (M * j) := by ring
    rw [← hL1, ← hL2, ← Finset.sum_neg_distrib, ← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun n hn => ?_
    have hn1 : 1 ≤ n := (Finset.mem_Ico.mp hn).1
    have hdj := nat_div_sub_pred_div hj hn1
    have hdk := nat_div_sub_pred_div hk hn1
    let p := ((n / j : ℕ) : ℝ)
    let p' := (((n - 1) / j : ℕ) : ℝ)
    let q := ((n / k : ℕ) : ℝ)
    let q' := (((n - 1) / k : ℕ) : ℝ)
    change -((p * q - p' * q') * (-(1 : ℝ) / (n : ℝ))) =
      (if j ∣ n then (q + q') / (2 * (n : ℝ)) else 0) +
        (if k ∣ n then (p + p') / (2 * (n : ℝ)) else 0)
    have hid : 2 * (p * q - p' * q') = (p - p') * (q + q') + (q - q') * (p + p') := by ring
    have hdj' : p - p' = if j ∣ n then 1 else 0 := hdj
    have hdk' : q - q' = if k ∣ n then 1 else 0 := hdk
    rw [hdj', hdk'] at hid
    have hn_ne : (n : ℝ) ≠ 0 := (Nat.cast_pos.mpr hn1).ne'
    split_ifs at hid ⊢ <;> field_simp [hn_ne] at hid ⊢ <;> linarith
  rw [sub_eq_add_neg, h_symm]
  have hMk : 1 ≤ M * k := Nat.mul_pos hM hk
  have hMj : 1 ≤ M * j := Nat.mul_pos hM hj
  have hs1 := sum_Ico_ite_dvd
    (fun n => (((n / k : ℕ) : ℝ) + (((n - 1) / k : ℕ) : ℝ)) / (2 * (n : ℝ))) hj hMk
  have hs2 := sum_Ico_ite_dvd
    (fun n => (((n / j : ℕ) : ℝ) + (((n - 1) / j : ℕ) : ℝ)) / (2 * (n : ℝ))) hk hMj
  have hcon1 : ∑ m ∈ Finset.Ico 1 (M * k),
      ((((m * j) / k : ℕ) : ℝ) + (((m * j - 1) / k : ℕ) : ℝ)) / (2 * ((m * j : ℕ) : ℝ)) =
      ∑ m ∈ Finset.Ico 1 (M * k),
        (((m * j / k : ℕ) : ℝ) + (((m * j - 1) / k : ℕ) : ℝ)) / (2 * (m : ℝ) * (j : ℝ)) := by
    refine Finset.sum_congr rfl fun m _ => by push_cast; ring
  have hcon2 : ∑ m ∈ Finset.Ico 1 (M * j),
      ((((m * k) / j : ℕ) : ℝ) + (((m * k - 1) / j : ℕ) : ℝ)) / (2 * ((m * k : ℕ) : ℝ)) =
      ∑ m ∈ Finset.Ico 1 (M * j),
        (((m * k / j : ℕ) : ℝ) + (((m * k - 1) / j : ℕ) : ℝ)) / (2 * (m : ℝ) * (k : ℝ)) := by
    refine Finset.sum_congr rfl fun m _ => by push_cast; ring
  rw [hs1, hs2, hcon1, hcon2, halfSum_exact hj hk hM, halfSum_exact hk hj hM,
    Nat.cast_sub hMk, Nat.cast_sub hMj]
  push_cast
  ring

private lemma cross_partial_exact_identity {M j k : ℕ} (hM : 1 ≤ M) (hj : 1 ≤ j) (hk : 1 ≤ k) :
    (∫ x in (1 / ((M * j * k : ℕ) : ℝ))..1, recipFractScaled j x * recipFractScaled k x) =
      (1 / (k : ℝ)) * (Real.log ((Nat.factorial (M * k) : ℕ) : ℝ) -
        (M * k : ℝ) * Real.log ((M * k : ℕ) : ℝ) + (M * k : ℝ) -
        (1 / 2 : ℝ) * Real.log ((M * k : ℕ) : ℝ)) +
      (1 / (j : ℝ)) * (Real.log ((Nat.factorial (M * j) : ℕ) : ℝ) -
        (M * j : ℝ) * Real.log ((M * j : ℕ) : ℝ) + (M * j : ℝ) -
        (1 / 2 : ℝ) * Real.log ((M * j : ℕ) : ℝ)) -
      (1 / (2 * (j : ℝ))) *
        ((∑ m ∈ Finset.Ico 1 (M * k), (1 : ℝ) / (m : ℝ)) - Real.log ((M * k : ℕ) : ℝ)) -
      (1 / (2 * (k : ℝ))) *
        ((∑ m ∈ Finset.Ico 1 (M * j), (1 : ℝ) / (m : ℝ)) - Real.log ((M * j : ℕ) : ℝ)) +
      (((j : ℝ) - (k : ℝ)) * Real.log ((k : ℝ) / (j : ℝ)) - 2) / (2 * (j : ℝ) * (k : ℝ)) -
      1 / ((M : ℝ) * (j : ℝ) * (k : ℝ)) -
      (1 / (2 * (j : ℝ))) * cotApproxSum j k M -
      (1 / (2 * (k : ℝ))) * cotApproxSum k j M := by
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have hM_pos : (0 : ℝ) < (M : ℝ) := Nat.cast_pos.mpr hM
  have hL : 1 ≤ M * j * k := Nat.mul_pos (Nat.mul_pos hM hj) hk
  rw [intervalIntegral_split_recip (fun x => recipFractScaled j x * recipFractScaled k x)
    (intervalIntegrable_recipFractScaled_mul j k) (M * j * k) hL]
  have h_congr : ∑ n ∈ Finset.Ico 1 (M * j * k),
      (∫ x in (1 / ((n : ℝ) + 1))..(1 / (n : ℝ)), recipFractScaled j x * recipFractScaled k x) =
      ∑ n ∈ Finset.Ico 1 (M * j * k),
        (1 / ((j : ℝ) * (k : ℝ)) -
          (((n / j : ℕ) : ℝ) / (k : ℝ) + ((n / k : ℕ) : ℝ) / (j : ℝ)) *
            (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) +
          ((n / j : ℕ) : ℝ) * ((n / k : ℕ) : ℝ) * (1 / (n : ℝ) - 1 / ((n : ℝ) + 1))) := by
    refine Finset.sum_congr rfl fun n hn => ?_
    exact intervalIntegral_recipFractScaled_mul_unit hj hk (Finset.mem_Ico.mp hn).1
  rw [h_congr, Finset.sum_add_distrib, Finset.sum_sub_distrib]
  have hS1 : ∑ _n ∈ Finset.Ico 1 (M * j * k), (1 : ℝ) / ((j : ℝ) * (k : ℝ)) =
      (M : ℝ) - 1 / ((j : ℝ) * (k : ℝ)) := by
    rw [Finset.sum_const, Nat.card_Ico, nsmul_eq_mul, Nat.cast_sub hL, Nat.cast_one]
    push_cast
    field_simp [hj_pos.ne', hk_pos.ne']
  have hS2 : ∑ n ∈ Finset.Ico 1 (M * j * k),
      (((n / j : ℕ) : ℝ) / (k : ℝ) + ((n / k : ℕ) : ℝ) / (j : ℝ)) *
        (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) =
      (1 / (k : ℝ)) * ∑ n ∈ Finset.Ico 1 (M * j * k),
        ((n / j : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) +
      (1 / (j : ℝ)) * ∑ n ∈ Finset.Ico 1 (M * j * k),
        ((n / k : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) := by
    have hsplit_s2 : ∀ n : ℕ,
        (((n / j : ℕ) : ℝ) / (k : ℝ) + ((n / k : ℕ) : ℝ) / (j : ℝ)) *
          (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) =
        (1 / (k : ℝ)) * (((n / j : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ))) +
        (1 / (j : ℝ)) * (((n / k : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ))) := by
      intro n; ring
    simp_rw [hsplit_s2, Finset.sum_add_distrib, ← Finset.mul_sum]
  have ha1 := abel_log_sum_exact hM hj hk
  have ha2 := abel_log_sum_exact hM hk hj
  have ha2' : (-(1 : ℝ) / (j : ℝ)) * ∑ n ∈ Finset.Ico 1 (M * j * k),
      ((n / k : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) =
      (Real.log ((Nat.factorial (M * j) : ℕ) : ℝ) -
        (M * j : ℝ) * Real.log ((M * j : ℕ) : ℝ)) / (j : ℝ) := by
    rw [show M * j * k = M * k * j by ring]
    exact ha2
  have ha1_pos : (1 / (k : ℝ)) * ∑ n ∈ Finset.Ico 1 (M * j * k),
      ((n / j : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) =
      -((Real.log ((Nat.factorial (M * k) : ℕ) : ℝ) -
        (M * k : ℝ) * Real.log ((M * k : ℕ) : ℝ)) / (k : ℝ)) := by
    rw [← ha1]
    ring
  have ha2_pos : (1 / (j : ℝ)) * ∑ n ∈ Finset.Ico 1 (M * j * k),
      ((n / k : ℕ) : ℝ) * (Real.log ((n : ℝ) + 1) - Real.log (n : ℝ)) =
      -((Real.log ((Nat.factorial (M * j) : ℕ) : ℝ) -
        (M * j : ℝ) * Real.log ((M * j : ℕ) : ℝ)) / (j : ℝ)) := by
    rw [← ha2']
    ring
  rw [hS1, hS2, ha1_pos, ha2_pos, abel_cross_sum_exact hM hj hk]
  have hlogMk : Real.log ((M * k : ℕ) : ℝ) = Real.log (M : ℝ) + Real.log (k : ℝ) := by
    push_cast; exact Real.log_mul hM_pos.ne' hk_pos.ne'
  have hlogMj : Real.log ((M * j : ℕ) : ℝ) = Real.log (M : ℝ) + Real.log (j : ℝ) := by
    push_cast; exact Real.log_mul hM_pos.ne' hj_pos.ne'
  have hlogkj : Real.log ((k : ℝ) / (j : ℝ)) = Real.log (k : ℝ) - Real.log (j : ℝ) :=
    Real.log_div hk_pos.ne' hj_pos.ne'
  rw [hlogkj]
  have h_log_cancel :
      (1 / (k : ℝ)) * ((1 / 2 : ℝ) * Real.log ((M * k : ℕ) : ℝ)) +
        (1 / (j : ℝ)) * ((1 / 2 : ℝ) * Real.log ((M * j : ℕ) : ℝ)) -
        (1 / (2 * (j : ℝ))) * Real.log ((M * k : ℕ) : ℝ) -
        (1 / (2 * (k : ℝ))) * Real.log ((M * j : ℕ) : ℝ) -
        2 / (2 * (j : ℝ) * (k : ℝ)) =
      (((j : ℝ) - (k : ℝ)) * (Real.log (k : ℝ) - Real.log (j : ℝ)) - 2) /
        (2 * (j : ℝ) * (k : ℝ)) := by
    rw [hlogMk, hlogMj]
    field_simp [hj_pos.ne', hk_pos.ne']
    ring
  rw [← h_log_cancel]
  field_simp [hM_pos.ne', hj_pos.ne', hk_pos.ne']
  ring

/-- **Vasyunin (1995) Cross-Integral Theorem** (unconditional): for all `j, k ≥ 1`,
`∫₀¹ {1/(j x)} {1/(k x)} dx = GSmooth Real.eulerMascheroniConstant j k + vasyuninGCot j k`. -/
theorem intervalIntegral_recipFractScaled_cross {j k : ℕ} (hj : 1 ≤ j) (hk : 1 ≤ k) :
    (∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x) =
      GSmooth Real.eulerMascheroniConstant j k + vasyuninGCot j k := by
  have hj_pos : (0 : ℝ) < (j : ℝ) := Nat.cast_pos.mpr hj
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  let S₁ : ℕ → ℝ := fun M => Real.log ((Nat.factorial (M * k) : ℕ) : ℝ) -
    (M * k : ℝ) * Real.log ((M * k : ℕ) : ℝ) + (M * k : ℝ) -
    (1 / 2 : ℝ) * Real.log ((M * k : ℕ) : ℝ)
  let S₂ : ℕ → ℝ := fun M => Real.log ((Nat.factorial (M * j) : ℕ) : ℝ) -
    (M * j : ℝ) * Real.log ((M * j : ℕ) : ℝ) + (M * j : ℝ) -
    (1 / 2 : ℝ) * Real.log ((M * j : ℕ) : ℝ)
  let H₁ : ℕ → ℝ := fun M =>
    (∑ m ∈ Finset.Ico 1 (M * k), (1 : ℝ) / (m : ℝ)) - Real.log ((M * k : ℕ) : ℝ)
  let H₂ : ℕ → ℝ := fun M =>
    (∑ m ∈ Finset.Ico 1 (M * j), (1 : ℝ) / (m : ℝ)) - Real.log ((M * j : ℕ) : ℝ)
  have hS₁ : Tendsto S₁ atTop (nhds ((1 / 2 : ℝ) * Real.log (2 * Real.pi))) :=
    tendsto_stirling_log_term k hk
  have hS₂ : Tendsto S₂ atTop (nhds ((1 / 2 : ℝ) * Real.log (2 * Real.pi))) :=
    tendsto_stirling_log_term j hj
  have hH₁ : Tendsto H₁ atTop (nhds Real.eulerMascheroniConstant) :=
    tendsto_harmonic_Ico_sub_log k hk
  have hH₂ : Tendsto H₂ atTop (nhds Real.eulerMascheroniConstant) :=
    tendsto_harmonic_Ico_sub_log j hj
  have hC₁ : Tendsto (cotApproxSum j k) atTop (nhds ((Real.pi / (k : ℝ)) * vasyuninCotSum k j)) :=
    tendsto_cotApproxSum j k
  have hC₂ : Tendsto (cotApproxSum k j) atTop (nhds ((Real.pi / (j : ℝ)) * vasyuninCotSum j k)) :=
    tendsto_cotApproxSum k j
  have h_inv_L : Tendsto (fun M : ℕ => 1 / ((M : ℝ) * (j : ℝ) * (k : ℝ))) atTop (nhds 0) := by
    have h_top : Tendsto (fun M : ℕ => (M : ℝ) * (j : ℝ) * (k : ℝ)) atTop atTop :=
      (tendsto_natCast_atTop_atTop.atTop_mul_const hj_pos).atTop_mul_const hk_pos
    simpa [Function.comp_def, one_div, mul_inv] using tendsto_inv_atTop_zero.comp h_top
  let L_rhs : ℝ :=
    (1 / (k : ℝ)) * ((1 / 2 : ℝ) * Real.log (2 * Real.pi)) +
    (1 / (j : ℝ)) * ((1 / 2 : ℝ) * Real.log (2 * Real.pi)) -
    (1 / (2 * (j : ℝ))) * Real.eulerMascheroniConstant -
    (1 / (2 * (k : ℝ))) * Real.eulerMascheroniConstant +
    (((j : ℝ) - (k : ℝ)) * Real.log ((k : ℝ) / (j : ℝ)) - 2) / (2 * (j : ℝ) * (k : ℝ)) - 0 -
    (1 / (2 * (j : ℝ))) * ((Real.pi / (k : ℝ)) * vasyuninCotSum k j) -
    (1 / (2 * (k : ℝ))) * ((Real.pi / (j : ℝ)) * vasyuninCotSum j k)
  have h_main_lim : Tendsto
      (fun M : ℕ => ∫ x in (1 / ((M * j * k : ℕ) : ℝ))..1,
        recipFractScaled j x * recipFractScaled k x)
      atTop (nhds L_rhs) := by
    have h_comb := (((((((hS₁.const_mul (1 / (k : ℝ))).add
      (hS₂.const_mul (1 / (j : ℝ)))).sub
      (hH₁.const_mul (1 / (2 * (j : ℝ))))).sub
      (hH₂.const_mul (1 / (2 * (k : ℝ))))).add
      (tendsto_const_nhds (x := (((j : ℝ) - (k : ℝ)) * Real.log ((k : ℝ) / (j : ℝ)) - 2) /
        (2 * (j : ℝ) * (k : ℝ))))).sub h_inv_L).sub
      (hC₁.const_mul (1 / (2 * (j : ℝ))))).sub
      (hC₂.const_mul (1 / (2 * (k : ℝ))))
    refine h_comb.congr' ?_
    filter_upwards [eventually_ge_atTop 1] with M hM
    exact (cross_partial_exact_identity hM hj hk).symm
  have h_lim_tail : Tendsto (fun M : ℕ => 1 / ((M * j * k : ℕ) : ℝ)) atTop (nhds 0) := by
    push_cast
    exact h_inv_L
  have h_zero_lim : Tendsto
      (fun M : ℕ => ∫ x in (0 : ℝ)..(1 / ((M * j * k : ℕ) : ℝ)),
        recipFractScaled j x * recipFractScaled k x)
      atTop (nhds 0) := by
    refine squeeze_zero_norm' (Eventually.of_forall fun M => ?_) h_lim_tail
    have hle : (0 : ℝ) ≤ 1 / ((M * j * k : ℕ) : ℝ) := by positivity
    have hbd : ∀ x ∈ Set.uIoc (0 : ℝ) (1 / ((M * j * k : ℕ) : ℝ)),
        ‖recipFractScaled j x * recipFractScaled k x‖ ≤ (1 : ℝ) := by
      intro x _
      unfold recipFractScaled
      have h1 := Int.fract_nonneg (1 / ((j : ℝ) * x))
      have h2 := Int.fract_lt_one (1 / ((j : ℝ) * x))
      have h3 := Int.fract_nonneg (1 / ((k : ℝ) * x))
      have h4 := Int.fract_lt_one (1 / ((k : ℝ) * x))
      rw [Real.norm_of_nonneg (mul_nonneg h1 h3)]
      nlinarith
    simpa [abs_of_nonneg hle,
      abs_of_nonneg (by positivity : (0 : ℝ) ≤ ((M * j * k : ℕ) : ℝ))] using
      intervalIntegral.norm_integral_le_of_norm_le_const hbd
  have h_sum : ∀ M : ℕ,
      (∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x) =
      (∫ x in (0 : ℝ)..(1 / ((M * j * k : ℕ) : ℝ)),
        recipFractScaled j x * recipFractScaled k x) +
      (∫ x in (1 / ((M * j * k : ℕ) : ℝ))..1,
        recipFractScaled j x * recipFractScaled k x) := fun M =>
    (intervalIntegral.integral_add_adjacent_intervals
      (intervalIntegrable_recipFractScaled_mul j k 0 _)
      (intervalIntegrable_recipFractScaled_mul j k _ 1)).symm
  have h_const : Tendsto
      (fun _ : ℕ => ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x)
      atTop (nhds (∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x)) :=
    tendsto_const_nhds
  have h_tot : Tendsto
      (fun _ : ℕ => ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x)
      atTop (nhds (0 + L_rhs)) :=
    (h_zero_lim.add h_main_lim).congr' (Eventually.of_forall fun M => (h_sum M).symm)
  have h_eq : (∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x) = L_rhs := by
    simpa using tendsto_nhds_unique h_const h_tot
  rw [h_eq]
  dsimp [L_rhs, GSmooth, vasyuninGCot]
  field_simp [hj_pos.ne', hk_pos.ne']
  ring

/-- Full quadratic expansion of the Lebesgue L² distance:
  ∫_0^1 (1 - ∑ c_k {1/(kx)})² dx = 1 - 2 ∑ c_k b_k + ∑∑ c_j c_k g_{j,k}. -/
theorem intervalIntegral_sq_sub_sum {N : ℕ} (c : ℕ → ℝ) :
    (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) =
      1 - 2 * (∑ k ∈ Finset.Icc 1 N, c k * ∫ x in (0 : ℝ)..1, recipFractScaled k x) +
        ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, c j * c k *
          ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x := by
  have h_exp : ∀ x, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2 =
      1 - 2 * (∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) +
        ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          c j * c k * (recipFractScaled j x * recipFractScaled k x) := by
    intro x
    have hsq : (∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2 =
        ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          c j * c k * (recipFractScaled j x * recipFractScaled k x) := by
      rw [sq, sum_mul_sum]
      refine sum_congr rfl (fun j _ => sum_congr rfl (fun k _ => ?_))
      ring
    have hlin : (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2 =
        1 - 2 * (∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) +
          (∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2 := by ring
    rw [hlin, hsq]
  have h_eq : (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) =
      ∫ x in (0 : ℝ)..1, (1 - 2 * (∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) +
        ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          c j * c k * (recipFractScaled j x * recipFractScaled k x)) := by
    refine intervalIntegral.integral_congr (fun x _ => h_exp x)
  rw [h_eq]
  have hint1 : IntervalIntegrable (fun _ : ℝ => (1 : ℝ)) volume 0 1 := intervalIntegrable_const
  have hint2_term : ∀ k ∈ Finset.Icc 1 N,
      IntervalIntegrable (fun x => c k * recipFractScaled k x) volume 0 1 := by
    intro k _
    exact (intervalIntegrable_recipFractScaled k 0 1).const_mul (c k)
  have hint2_sum : IntervalIntegrable
      (fun x => ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) volume 0 1 := by
    have heq : (fun x => ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) =
        (∑ k ∈ Finset.Icc 1 N, fun x => c k * recipFractScaled k x) := by
      funext x; rw [Finset.sum_apply]
    rw [heq]
    exact IntervalIntegrable.sum (Finset.Icc 1 N) hint2_term
  have hint2 : IntervalIntegrable
      (fun x => 2 * ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) volume 0 1 :=
    hint2_sum.const_mul 2
  have hint3_term : ∀ j ∈ Finset.Icc 1 N, ∀ k ∈ Finset.Icc 1 N,
      IntervalIntegrable (fun x => c j * c k *
        (recipFractScaled j x * recipFractScaled k x)) volume 0 1 := by
    intro j _ k _
    exact (intervalIntegrable_recipFractScaled_mul j k 0 1).const_mul (c j * c k)
  have hint3_inner : ∀ j ∈ Finset.Icc 1 N,
      IntervalIntegrable (fun x => ∑ k ∈ Finset.Icc 1 N,
        c j * c k * (recipFractScaled j x * recipFractScaled k x)) volume 0 1 := by
    intro j hj
    have heq : (fun x => ∑ k ∈ Finset.Icc 1 N,
        c j * c k * (recipFractScaled j x * recipFractScaled k x)) =
        (∑ k ∈ Finset.Icc 1 N, fun x => c j * c k *
          (recipFractScaled j x * recipFractScaled k x)) := by
      funext x; rw [Finset.sum_apply]
    rw [heq]
    exact IntervalIntegrable.sum (Finset.Icc 1 N) (hint3_term j hj)
  have hint3 : IntervalIntegrable (fun x => ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
      c j * c k * (recipFractScaled j x * recipFractScaled k x)) volume 0 1 := by
    have heq : (fun x => ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
        c j * c k * (recipFractScaled j x * recipFractScaled k x)) =
        (∑ j ∈ Finset.Icc 1 N, fun x => ∑ k ∈ Finset.Icc 1 N,
          c j * c k * (recipFractScaled j x * recipFractScaled k x)) := by
      funext x; rw [Finset.sum_apply]
    rw [heq]
    exact IntervalIntegrable.sum (Finset.Icc 1 N) hint3_inner
  rw [intervalIntegral.integral_add (hint1.sub hint2) hint3]
  rw [intervalIntegral.integral_sub hint1 hint2]
  rw [intervalIntegral.integral_const, sub_zero, smul_eq_mul, mul_one]
  rw [intervalIntegral.integral_const_mul]
  rw [intervalIntegral.integral_finsetSum hint2_term]
  simp_rw [intervalIntegral.integral_const_mul]
  rw [intervalIntegral.integral_finsetSum hint3_inner]
  refine congr_arg₂ _ rfl ?_
  refine sum_congr rfl ?_
  intro j hj
  rw [intervalIntegral.integral_finsetSum (hint3_term j hj)]
  simp_rw [intervalIntegral.integral_const_mul]

/-- Quadratic form of the cotangent Gram matrix on `Finset.Icc 1 N`. -/
noncomputable def QCot (g_cot : ℕ → ℕ → ℝ) (c : ℕ → ℝ) (N : ℕ) : ℝ :=
  ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, c j * c k * g_cot j k

/-- Theorem: Affine L² Pure Cotangent Bridge (unconditional).
For any coefficient sequence `c` on the affine subspace `A_N` (satisfying `D1(c, N) = 0` and
`D0(c, N) = 2`), the true continuous Lebesgue L² distance collapses unconditionally
to `1 + QCot vasyuninGCot c N` with zero smooth or logarithmic residual. -/
theorem affine_l2_pure_cotangent_bridge {N : ℕ} (c : ℕ → ℝ)
    (hD1 : D1 c N = 0) (hD0 : D0 c N = 2) :
    (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) =
      1 + QCot vasyuninGCot c N := by
  rw [intervalIntegral_sq_sub_sum c]
  have hb_sum : (∑ k ∈ Finset.Icc 1 N, c k * ∫ x in (0 : ℝ)..1, recipFractScaled k x) =
      ∑ k ∈ Finset.Icc 1 N, c k * bVasyunin k Real.eulerMascheroniConstant := by
    refine sum_congr rfl (fun k hk => ?_)
    rw [intervalIntegral_recipFractScaled_eq_bVasyunin (Finset.mem_Icc.mp hk).1]
  rw [hb_sum]
  have hG_sum : (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, c j * c k *
      ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x) =
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
        c j * c k * GSmooth Real.eulerMascheroniConstant j k) +
        QCot vasyuninGCot c N := by
    unfold QCot
    have hterm : ∀ j ∈ Finset.Icc 1 N, ∀ k ∈ Finset.Icc 1 N,
        c j * c k * ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x =
        c j * c k * GSmooth Real.eulerMascheroniConstant j k +
          c j * c k * vasyuninGCot j k := by
      intro j hj k hk
      rw [intervalIntegral_recipFractScaled_cross
        (Finset.mem_Icc.mp hj).1 (Finset.mem_Icc.mp hk).1, mul_add]
    have hinner : ∀ j ∈ Finset.Icc 1 N,
        (∑ k ∈ Finset.Icc 1 N, c j * c k *
          ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x) =
        (∑ k ∈ Finset.Icc 1 N, c j * c k * GSmooth Real.eulerMascheroniConstant j k) +
          ∑ k ∈ Finset.Icc 1 N, c j * c k * vasyuninGCot j k := by
      intro j hj
      rw [← sum_add_distrib]
      exact sum_congr rfl (fun k hk => hterm j hj k hk)
    rw [sum_congr rfl (fun j hj => hinner j hj), sum_add_distrib]
  rw [hG_sum, ← add_assoc]
  exact affine_bdr_pure_cotangent_identity c N Real.eulerMascheroniConstant
    (QCot vasyuninGCot c N) hD1 hD0

/-- The symmetric normalized Vasyunin cotangent sum S_cot(c, N) = - QCot g_cot c N.
This equals (π / 2) * ∑∑ (c_j c_k / jk) (V(j, k) + V(k, j)). -/
noncomputable def SCot (g_cot : ℕ → ℕ → ℝ) (c : ℕ → ℝ) (N : ℕ) : ℝ :=
  - QCot g_cot c N

/-- Exact L² distance formula in terms of SCot (unconditional):
  ∫_0^1 (1 - ∑ c_k {1/(kx)})² dx = 1 - SCot vasyuninGCot c N. -/
theorem affine_l2_dist_eq_one_sub_scot {N : ℕ} (c : ℕ → ℝ)
    (hD1 : D1 c N = 0) (hD0 : D0 c N = 2) :
    (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) =
      1 - SCot vasyuninGCot c N := by
  have h := affine_l2_pure_cotangent_bridge c hD1 hD0
  dsimp [SCot]
  linarith

/-- Equivalence of Nyman-Beurling epsilon approximation and SCot near 1 (unconditional):
  ∫_0^1 (1 - ∑ c_k {1/(kx)})² dx < ε ↔ 1 - ε < SCot vasyuninGCot c N. -/
theorem nymanBeurling_approx_iff_scot_gt {N : ℕ} (c : ℕ → ℝ) (ε : ℝ)
    (hD1 : D1 c N = 0) (hD0 : D0 c N = 2) :
    (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) < ε ↔
      1 - ε < SCot vasyuninGCot c N := by
  rw [affine_l2_dist_eq_one_sub_scot c hD1 hD0]
  constructor <;> intro h <;> linarith

/-- Main Theorem: Cotangent Limit Implies Riemann Hypothesis (unconditional bridge).
Under the Báez-Duarte / Nyman-Beurling bridge, if the normalized cotangent double sum
satisfies the limit condition SCot → 1 on the affine manifold A_N, then the
square distance tends to 0, which implies the Riemann Hypothesis. -/
theorem riemannHypothesis_of_cotangent_limit
    (h_limit : ∀ ε > 0, ∃ (N : ℕ) (c : ℕ → ℝ),
      D1 c N = 0 ∧ D0 c N = 2 ∧ 1 - ε < SCot vasyuninGCot c N) :
    RiemannHypothesis := by
  apply RiemannHypothesis.of_nymanBeurling_approx
  intro ε hε
  rcases h_limit ε hε with ⟨N, c, hD1, hD0, hscot⟩
  refine ⟨N, fun k => (c k : ℂ), ?_, ?_⟩
  · have h_cast : (∑ k ∈ Finset.Icc 1 N, (c k : ℂ) / (k : ℂ)) =
        ((∑ k ∈ Finset.Icc 1 N, c k / (k : ℝ) : ℝ) : ℂ) := by
      push_cast; rfl
    rw [h_cast]
    change ((D1 c N : ℝ) : ℂ) = 0
    rw [hD1, Complex.ofReal_zero]
  · have h_int_eq : (∫ x in Set.Ioo (0 : ℝ) 1,
          ‖1 - ∑ k ∈ Finset.Icc 1 N, (c k : ℂ) * (recipFractScaled k x : ℂ)‖ ^ 2) =
        ∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2 := by
      rw [intervalIntegral.integral_of_le (by norm_num : (0 : ℝ) ≤ 1),
        MeasureTheory.integral_Ioc_eq_integral_Ioo]
      refine setIntegral_congr_fun measurableSet_Ioo fun x _ => ?_
      have h_sub : (1 - ∑ k ∈ Finset.Icc 1 N, (c k : ℂ) * (recipFractScaled k x : ℂ)) =
          ((1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x : ℝ) : ℂ) := by
        push_cast; rfl
      rw [h_sub, Complex.norm_real, Real.norm_eq_abs, sq_abs]
    rw [h_int_eq, nymanBeurling_approx_iff_scot_gt c ε hD1 hD0]
    exact hscot
