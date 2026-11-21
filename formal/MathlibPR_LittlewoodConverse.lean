/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
module

public import Mathlib.Analysis.Analytic.Uniqueness
public import Mathlib.Analysis.Complex.CauchyIntegral
public import Mathlib.Analysis.Complex.HasPrimitives
public import Mathlib.Analysis.MellinInversion
public import Mathlib.Analysis.MellinTransform
public import Mathlib.Analysis.Asymptotics.SpecificAsymptotics
public import Mathlib.Analysis.PSeriesComplex
public import Mathlib.MeasureTheory.Function.Floor
public import Mathlib.NumberTheory.LSeries.Dirichlet
public import Mathlib.NumberTheory.LSeries.Nonvanishing
public import Mathlib.NumberTheory.LSeries.RiemannZeta
public import Mathlib.NumberTheory.AbelSummation
public import Mathlib.NumberTheory.LSeries.SumCoeff
public import RiemannBlueprint.MathlibPR_LittlewoodMertens
public import RiemannBlueprint.MathlibPR_ZetaInvSubpolynomial

/-!
# Littlewood's (1912) Converse & Unconditional Mellin–Mertens Equivalence

This file formalizes Stages 4–5 of Littlewood's (1912) converse theorem:
using the conditional reciprocal zeta bound from MathlibPR_ZetaInvSubpolynomial
and the trapezoidal Mellin inversion formula, we establish that RiemannHypothesis
implies the pointwise asymptotic Mertens bound M(x) = O(x ^ (1 / 2 + ε)).
Combining this with Littlewood's forward theorem (RiemannHypothesis.of_mertens_isBigO
from MathlibPR_LittlewoodMertens), we conclude the full bidirectional equivalence
RiemannHypothesis ↔ ∀ ε > 0, M(x) = O(x ^ (1 / 2 + ε)).

## Main Results
* isBigO_mertens_of_riemannHypothesis: Littlewood's (1912) converse in Mathlib's =O[atTop].
* 
iemannHypothesis_iff_mertens_isBigO: Littlewood's bidirectional equivalence.
-/

set_option linter.style.openClassical false

@[expose] public section

open scoped LSeries.notation Topology
open Asymptotics Complex Filter MeasureTheory Metric Set Real

/-! ### Stage 4: Compactly Supported Trapezoidal Cutoff & Mellin–Mertens Inversion at Re(s) = 2 -/

/-- Continuous compactly supported trapezoidal cutoff matching `1` on `[1, X]`, linear on `[1/2, 1]`
and `[X, X + H]`, and `0` outside `(1/2, X + H)`. -/
private noncomputable def cutoffPhi (X H t : ℝ) : ℂ :=
  ((min (max 0 (min 1 (2 * t - 1))) (max 0 (min 1 ((X + H - t) / H))) : ℝ) : ℂ)

private lemma continuous_cutoffPhi (X H : ℝ) : Continuous (cutoffPhi X H) := by
  unfold cutoffPhi
  fun_prop

private lemma cutoffPhi_eq_zero_of_le_half (X H : ℝ) {t : ℝ} (ht : t ≤ 1 / 2) :
    cutoffPhi X H t = 0 := by
  have h1 : 2 * t - 1 ≤ 0 := by linarith
  have h2 : min 1 (2 * t - 1) ≤ 0 := min_le_of_right_le h1
  have h3 : max (0 : ℝ) (min 1 (2 * t - 1)) = 0 := max_eq_left h2
  have _h4 : (0 : ℝ) ≤ max 0 (min 1 ((X + H - t) / H)) := le_max_left _ _
  simp [cutoffPhi, h3]

private lemma cutoffPhi_eq_zero_of_ge (X : ℝ) {H t : ℝ} (hH : 0 < H) (ht : X + H ≤ t) :
    cutoffPhi X H t = 0 := by
  have h1 : (X + H - t) / H ≤ 0 := div_nonpos_of_nonpos_of_nonneg (by linarith) hH.le
  have h2 : min 1 ((X + H - t) / H) ≤ 0 := min_le_of_right_le h1
  have h3 : max (0 : ℝ) (min 1 ((X + H - t) / H)) = 0 := max_eq_left h2
  have _h4 : (0 : ℝ) ≤ max 0 (min 1 (2 * t - 1)) := le_max_left _ _
  simp [cutoffPhi, h3]

private lemma cutoffPhi_eq_left {X H t : ℝ} (hX : 1 ≤ X) (hH : 0 < H)
    (ht1 : 1 / 2 ≤ t) (ht2 : t ≤ 1) :
    cutoffPhi X H t = ((2 * t - 1 : ℝ) : ℂ) := by
  have hA1 : 2 * t - 1 ≤ 1 := by linarith
  have hA0 : 0 ≤ 2 * t - 1 := by linarith
  have hA : max (0 : ℝ) (min 1 (2 * t - 1)) = 2 * t - 1 := by
    rw [min_eq_right hA1, max_eq_right hA0]
  have hB1 : 1 ≤ (X + H - t) / H := (one_le_div hH).2 (by linarith)
  have hB : max (0 : ℝ) (min 1 ((X + H - t) / H)) = 1 := by
    rw [min_eq_left hB1, max_eq_right zero_le_one]
  simp [cutoffPhi, hA, hB, min_eq_left hA1]

private lemma cutoffPhi_eq_one_of_Icc {X H t : ℝ} (_hX : 1 ≤ X) (hH : 0 < H)
    (ht1 : 1 ≤ t) (ht2 : t ≤ X) :
    cutoffPhi X H t = 1 := by
  have hA1 : 1 ≤ 2 * t - 1 := by linarith
  have hA : max (0 : ℝ) (min 1 (2 * t - 1)) = 1 := by
    rw [min_eq_left hA1, max_eq_right zero_le_one]
  have hB1 : 1 ≤ (X + H - t) / H := (one_le_div hH).2 (by linarith)
  have hB : max (0 : ℝ) (min 1 ((X + H - t) / H)) = 1 := by
    rw [min_eq_left hB1, max_eq_right zero_le_one]
  simp [cutoffPhi, hA, hB]

private lemma cutoffPhi_eq_right {X H t : ℝ} (_hX : 1 ≤ X) (hH : 0 < H)
    (ht1 : X ≤ t) (ht2 : t ≤ X + H) :
    cutoffPhi X H t = (((X + H - t) / H : ℝ) : ℂ) := by
  have hA1 : 1 ≤ 2 * t - 1 := by linarith
  have hA : max (0 : ℝ) (min 1 (2 * t - 1)) = 1 := by
    rw [min_eq_left hA1, max_eq_right zero_le_one]
  have hB1 : (X + H - t) / H ≤ 1 := (div_le_one hH).2 (by linarith)
  have hB0 : 0 ≤ (X + H - t) / H := div_nonneg (by linarith) hH.le
  have hB : max (0 : ℝ) (min 1 ((X + H - t) / H)) = (X + H - t) / H := by
    rw [min_eq_right hB1, max_eq_right hB0]
  rw [cutoffPhi, hA, hB, min_eq_right hB1]

private lemma norm_cutoffPhi_le_one (X H t : ℝ) : ‖cutoffPhi X H t‖ ≤ 1 := by
  unfold cutoffPhi
  set a : ℝ := max 0 (min 1 (2 * t - 1))
  set b : ℝ := max 0 (min 1 ((X + H - t) / H))
  have ha0 : 0 ≤ a := le_max_left _ _
  have ha1 : a ≤ 1 := max_le zero_le_one (min_le_left _ _)
  have hb0 : 0 ≤ b := le_max_left _ _
  have hm0 : 0 ≤ min a b := le_min ha0 hb0
  have hm1 : min a b ≤ 1 := (min_le_left a b).trans ha1
  rw [Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg hm0]
  exact hm1

private lemma summable_moebius_mul_cutoffPhi {X H : ℝ} (hH : 0 < H) :
    Summable (fun n : ℕ => (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) := by
  refine summable_of_ne_finset_zero (s := Finset.Iic (Nat.floor (X + H))) ?_
  intro n hn
  simp only [Finset.mem_Iic, not_le] at hn
  have hXHn : X + H < (n : ℝ) := by
    have hfloor : X + H < ((Nat.floor (X + H) : ℕ) : ℝ) + 1 := Nat.lt_floor_add_one _
    have hn_ge : ((Nat.floor (X + H) : ℕ) : ℝ) + 1 ≤ (n : ℝ) := by exact_mod_cast hn
    linarith
  rw [cutoffPhi_eq_zero_of_ge X hH hXHn.le, mul_zero]

private lemma tsum_moebius_mul_cutoffPhi_sub_mertens_norm_le {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H) :
    ‖(∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) - (mertens X : ℂ)‖ ≤
      H + 1 := by
  set N : ℕ := Nat.floor (X + H)
  set M : ℕ := Nat.floor X
  have hMN : M ≤ N := Nat.floor_mono (by linarith)
  have h_tsum :
      (∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) =
        ∑ n ∈ Finset.Iic N, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n := by
    refine tsum_eq_sum ?_
    intro n hn
    simp only [Finset.mem_Iic, not_le] at hn
    have hXHn : X + H < (n : ℝ) := by
      have hfloor : X + H < (N : ℝ) + 1 := Nat.lt_floor_add_one _
      have hn_ge : (N : ℝ) + 1 ≤ (n : ℝ) := by exact_mod_cast hn
      linarith
    rw [cutoffPhi_eq_zero_of_ge X hH hXHn.le, mul_zero]
  have h_mertens_cast :
      (mertens X : ℂ) =
        ∑ n ∈ Finset.Iic M, (ArithmeticFunction.moebius n : ℂ) := by
    simp [mertens, M]
  have h_split :
      (∑ n ∈ Finset.Iic N, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) =
        (∑ n ∈ Finset.Iic M, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) +
        ∑ n ∈ Finset.Ioc M N, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n := by
    have hIic : Finset.Iic N = Finset.Iic M ∪ Finset.Ioc M N := by
      ext n
      simp only [Finset.mem_union, Finset.mem_Iic, Finset.mem_Ioc]
      omega
    have hdisj : Disjoint (Finset.Iic M) (Finset.Ioc M N) := by
      rw [Finset.disjoint_left]
      intro n hn1 hn2
      simp only [Finset.mem_Iic] at hn1
      simp only [Finset.mem_Ioc] at hn2
      omega
    rw [hIic, Finset.sum_union hdisj]
  have h_main :
      (∑ n ∈ Finset.Iic M, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) =
        ∑ n ∈ Finset.Iic M, (ArithmeticFunction.moebius n : ℂ) := by
    refine Finset.sum_congr rfl fun n hn => ?_
    rcases Nat.eq_zero_or_pos n with rfl | hn_pos
    · simp
    · have hn1 : (1 : ℝ) ≤ n := by exact_mod_cast hn_pos
      have hnX : (n : ℝ) ≤ X :=
        (Nat.le_floor_iff (by linarith : 0 ≤ X)).mp (Finset.mem_Iic.mp hn)
      rw [cutoffPhi_eq_one_of_Icc hX hH hn1 hnX, mul_one]
  rw [h_tsum, h_mertens_cast, h_split, h_main, add_sub_cancel_left]
  calc ‖∑ n ∈ Finset.Ioc M N, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖
      ≤ ∑ n ∈ Finset.Ioc M N, ‖(ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ :=
        norm_sum_le _ _
    _ ≤ ∑ _n ∈ Finset.Ioc M N, (1 : ℝ) := by
        refine Finset.sum_le_sum fun n _ => ?_
        rw [norm_mul]
        have hmu : ‖(ArithmeticFunction.moebius n : ℂ)‖ ≤ 1 := by
          simpa [Complex.norm_intCast] using
            (show |(ArithmeticFunction.moebius n : ℝ)| ≤ 1 by
              exact_mod_cast ArithmeticFunction.abs_moebius_le_one (n := n))
        exact (mul_le_mul hmu (norm_cutoffPhi_le_one X H n) (norm_nonneg _) zero_le_one).trans_eq
          (one_mul 1)
    _ = ((Finset.Ioc M N).card : ℝ) := by simp
    _ = (N - M : ℝ) := by
        rw [Nat.card_Ioc, Nat.cast_sub hMN]
    _ ≤ H + 1 := by
        have hN_le : (N : ℝ) ≤ X + H := Nat.floor_le (by linarith)
        have hM_gt : X - 1 < (M : ℝ) := by linarith [Nat.lt_floor_add_one X]
        linarith

private lemma indicator_Ioi_cutoffPhi (X H : ℝ) (hH : 0 < H) (g : ℝ → ℂ) :
    Set.indicator (Set.Ioi (0 : ℝ)) (fun t => g t * cutoffPhi X H t) =
      Set.indicator (Set.Ioc (1 / 2 : ℝ) (X + H)) (fun t => g t * cutoffPhi X H t) := by
  ext t
  by_cases h1 : 1 / 2 < t <;> by_cases h2 : t ≤ X + H
  · have h0 : 0 < t := by linarith
    rw [Set.indicator_of_mem (show t ∈ Set.Ioi (0 : ℝ) from h0),
      Set.indicator_of_mem (show t ∈ Set.Ioc (1 / 2 : ℝ) (X + H) from ⟨h1, h2⟩)]
  · have h0 : 0 < t := by linarith
    rw [Set.indicator_of_mem (show t ∈ Set.Ioi (0 : ℝ) from h0),
      Set.indicator_of_notMem (show t ∉ Set.Ioc (1 / 2 : ℝ) (X + H) from fun h => h2 h.2),
      cutoffPhi_eq_zero_of_ge X hH (le_of_not_ge h2), mul_zero]
  · rw [Set.indicator_of_notMem (show t ∉ Set.Ioc (1 / 2 : ℝ) (X + H) from fun h => h1 h.1)]
    by_cases h0 : 0 < t
    · rw [Set.indicator_of_mem (show t ∈ Set.Ioi (0 : ℝ) from h0),
        cutoffPhi_eq_zero_of_le_half X H (le_of_not_gt h1), mul_zero]
    · rw [Set.indicator_of_notMem (show t ∉ Set.Ioi (0 : ℝ) from h0)]
  · rw [Set.indicator_of_notMem (show t ∉ Set.Ioc (1 / 2 : ℝ) (X + H) from fun h => h1 h.1)]
    by_cases h0 : 0 < t
    · rw [Set.indicator_of_mem (show t ∈ Set.Ioi (0 : ℝ) from h0),
        cutoffPhi_eq_zero_of_le_half X H (le_of_not_gt h1), mul_zero]
    · rw [Set.indicator_of_notMem (show t ∉ Set.Ioi (0 : ℝ) from h0)]

/-- Closed form of the Mellin transform of `cutoffPhi X H` for `0 < s.re`. -/
private theorem mellin_cutoffPhi_eq {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H) {s : ℂ} (hs : 0 < s.re) :
    mellin (cutoffPhi X H) s =
      (((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-s)) /
        (s * (s + 1)) := by
  have hs0 : s ≠ 0 := by intro h; rw [h] at hs; simp at hs
  have hs1 : s + 1 ≠ 0 := by
    intro h
    have := congrArg Complex.re h
    simp at this
    linarith
  have hH0 : (H : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr hH.ne'
  let F : ℝ → ℂ := fun t => (t : ℂ) ^ (s - 1) * cutoffPhi X H t
  have h_mellin : mellin (cutoffPhi X H) s = ∫ t in (1 / 2 : ℝ)..(X + H), F t := by
    rw [mellin]
    have h_smul : (fun t : ℝ => (t : ℂ) ^ (s - 1) • cutoffPhi X H t) = F := by
      ext t; simp [F, smul_eq_mul]
    rw [h_smul, ← MeasureTheory.integral_indicator measurableSet_Ioi,
      indicator_Ioi_cutoffPhi X H hH (fun t : ℝ => (t : ℂ) ^ (s - 1)),
      MeasureTheory.integral_indicator measurableSet_Ioc,
      intervalIntegral.integral_of_le (by linarith : (1 / 2 : ℝ) ≤ X + H)]
  have h_cont_F : ContinuousOn F (Set.Icc (1 / 2 : ℝ) (X + H)) := by
    refine ContinuousOn.mul ?_ (continuous_cutoffPhi X H).continuousOn
    refine ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const ?_
    intro t ht
    have ht_pos : 0 < t := by linarith [ht.1]
    exact Complex.ofReal_mem_slitPlane.mpr ht_pos
  have hI₁ : IntervalIntegrable F MeasureTheory.volume (1 / 2 : ℝ) 1 :=
    (h_cont_F.mono (Set.Icc_subset_Icc le_rfl (by linarith))).intervalIntegrable_of_Icc
      (by norm_num)
  have hI₂ : IntervalIntegrable F MeasureTheory.volume 1 X :=
    (h_cont_F.mono (Set.Icc_subset_Icc (by linarith) (by linarith))).intervalIntegrable_of_Icc
      hX
  have hI₃ : IntervalIntegrable F MeasureTheory.volume X (X + H) :=
    (h_cont_F.mono (Set.Icc_subset_Icc (by linarith) le_rfl)).intervalIntegrable_of_Icc
      (by linarith)
  have h_split : (∫ t in (1 / 2 : ℝ)..(X + H), F t) =
      (∫ t in (1 / 2 : ℝ)..1, F t) + (∫ t in (1 : ℝ)..X, F t) + (∫ t in X..(X + H), F t) := by
    have h12 : (∫ t in (1 / 2 : ℝ)..X, F t) =
        (∫ t in (1 / 2 : ℝ)..1, F t) + (∫ t in (1 : ℝ)..X, F t) :=
      (intervalIntegral.integral_add_adjacent_intervals hI₁ hI₂).symm
    have hI12 : IntervalIntegrable F MeasureTheory.volume (1 / 2 : ℝ) X := hI₁.trans hI₂
    rw [← intervalIntegral.integral_add_adjacent_intervals hI12 hI₃, h12]
  -- Evaluate piece 1: ∫ (1/2)..1 F
  have h_p1 : (∫ t in (1 / 2 : ℝ)..1, F t) =
      (s - 1 + (2 : ℂ) ^ (-s)) / (s * (s + 1)) := by
    have h_eq : Set.EqOn F (fun t : ℝ => (2 : ℂ) * (t : ℂ) ^ s - (t : ℂ) ^ (s - 1))
        (Set.uIcc (1 / 2 : ℝ) 1) := by
      intro t ht
      have ht' : t ∈ Set.Icc (1 / 2 : ℝ) 1 := by
        rw [Set.uIcc_of_le (by norm_num : (1 / 2 : ℝ) ≤ 1)] at ht
        exact ht
      have ht_pos : 0 < t := by linarith [ht'.1]
      dsimp [F]
      rw [cutoffPhi_eq_left hX hH ht'.1 ht'.2]
      push_cast
      have hpow : (t : ℂ) ^ (s - 1) * (t : ℂ) = (t : ℂ) ^ s := by
        have ht0 : (t : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr ht_pos.ne'
        calc (t : ℂ) ^ (s - 1) * (t : ℂ)
            = (t : ℂ) ^ (s - 1) * (t : ℂ) ^ (1 : ℂ) := by rw [Complex.cpow_one]
          _ = (t : ℂ) ^ ((s - 1) + 1) := (Complex.cpow_add _ _ ht0).symm
          _ = (t : ℂ) ^ s := by ring_nf
      calc (t : ℂ) ^ (s - 1) * (2 * (t : ℂ) - 1)
          = 2 * ((t : ℂ) ^ (s - 1) * (t : ℂ)) - (t : ℂ) ^ (s - 1) := by ring
        _ = 2 * (t : ℂ) ^ s - (t : ℂ) ^ (s - 1) := by rw [hpow]
    have hc1 : ContinuousOn (fun t : ℝ => (2 : ℂ) * (t : ℂ) ^ s) (Set.Icc (1 / 2 : ℝ) 1) := by
      refine ContinuousOn.mul continuousOn_const ?_
      exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
        fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
    have hc2 : ContinuousOn (fun t : ℝ => (t : ℂ) ^ (s - 1)) (Set.Icc (1 / 2 : ℝ) 1) := by
      exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
        fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
    rw [intervalIntegral.integral_congr h_eq,
      intervalIntegral.integral_sub (hc1.intervalIntegrable_of_Icc (by norm_num))
        (hc2.intervalIntegrable_of_Icc (by norm_num)),
      intervalIntegral.integral_const_mul]
    have h_int_s : (∫ t in (1 / 2 : ℝ)..1, (t : ℂ) ^ s) =
        ((1 : ℂ) ^ (s + 1) - ((1 / 2 : ℝ) : ℂ) ^ (s + 1)) / (s + 1) :=
      integral_cpow (Or.inl (by linarith))
    have h_int_s1 : (∫ t in (1 / 2 : ℝ)..1, (t : ℂ) ^ (s - 1)) =
        ((1 : ℂ) ^ s - ((1 / 2 : ℝ) : ℂ) ^ s) / s := by
      simpa [sub_add_cancel] using
        (integral_cpow (a := (1 / 2 : ℝ)) (b := 1) (r := s - 1)
          (Or.inl (by simp; linarith)))
    have h_half_s : ((1 / 2 : ℝ) : ℂ) ^ s = (2 : ℂ) ^ (-s) := by
      have h2r : (2 : ℂ) = ((2 : ℝ) : ℂ) := by norm_cast
      have h2ne : (2 : ℂ) ^ s ≠ 0 := Complex.cpow_ne_zero_iff.mpr (Or.inl (by norm_num))
      apply mul_right_cancel₀ h2ne
      calc ((1 / 2 : ℝ) : ℂ) ^ s * (2 : ℂ) ^ s
          = ((1 / 2 : ℝ) : ℂ) ^ s * ((2 : ℝ) : ℂ) ^ s := by rw [← h2r]
        _ = (((1 / 2 : ℝ) * (2 : ℝ) : ℝ) : ℂ) ^ s := by
            rw [← Complex.mul_cpow_ofReal_nonneg (by norm_num) (by norm_num)]
            norm_cast
        _ = (1 : ℂ) ^ s := by norm_num
        _ = 1 := Complex.one_cpow s
        _ = (2 : ℂ) ^ (-s + s) := by simp
        _ = (2 : ℂ) ^ (-s) * (2 : ℂ) ^ s := Complex.cpow_add _ _ (by norm_num)
    have h_half_s1 : ((1 / 2 : ℝ) : ℂ) ^ (s + 1) = (2 : ℂ) ^ (-s) * (2 : ℂ)⁻¹ := by
      have h_half_c : ((1 / 2 : ℝ) : ℂ) = (2 : ℂ)⁻¹ := by norm_num
      rw [Complex.cpow_add _ _ (by norm_num), Complex.cpow_one, h_half_s, h_half_c]
    rw [h_int_s, h_int_s1, Complex.one_cpow, Complex.one_cpow, h_half_s, h_half_s1]
    field_simp [hs0, hs1]
    ring
  -- Evaluate piece 2: ∫ 1..X F
  have h_p2 : (∫ t in (1 : ℝ)..X, F t) = ((X : ℂ) ^ s - 1) / s := by
    have h_eq : Set.EqOn F (fun t : ℝ => (t : ℂ) ^ (s - 1)) (Set.uIcc (1 : ℝ) X) := by
      intro t ht
      have ht' : t ∈ Set.Icc (1 : ℝ) X := by simpa [Set.uIcc_of_le hX] using ht
      simp [F, cutoffPhi_eq_one_of_Icc hX hH ht'.1 ht'.2]
    rw [intervalIntegral.integral_congr h_eq]
    simpa [sub_add_cancel, Complex.one_cpow] using
      (integral_cpow (a := (1 : ℝ)) (b := X) (r := s - 1)
        (Or.inl (by simp; linarith)))
  -- Evaluate piece 3: ∫ X..(X+H) F
  have h_p3 : (∫ t in X..(X + H), F t) =
      ((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ) - (s + 1) * (X : ℂ) ^ s) /
        (s * (s + 1)) := by
    have h_eq : Set.EqOn F
        (fun t : ℝ => ((((X + H : ℝ) : ℂ) / (H : ℂ)) * (t : ℂ) ^ (s - 1)) -
          ((H : ℂ)⁻¹ * (t : ℂ) ^ s)) (Set.uIcc X (X + H)) := by
      intro t ht
      have ht' : t ∈ Set.Icc X (X + H) := by
        simpa [Set.uIcc_of_le (by linarith : X ≤ X + H)] using ht
      have ht_pos : 0 < t := by linarith [ht'.1]
      dsimp [F]
      rw [cutoffPhi_eq_right hX hH ht'.1 ht'.2]
      push_cast
      have hpow : (t : ℂ) ^ (s - 1) * (t : ℂ) = (t : ℂ) ^ s := by
        have ht0 : (t : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr ht_pos.ne'
        calc (t : ℂ) ^ (s - 1) * (t : ℂ)
            = (t : ℂ) ^ (s - 1) * (t : ℂ) ^ (1 : ℂ) := by rw [Complex.cpow_one]
          _ = (t : ℂ) ^ ((s - 1) + 1) := (Complex.cpow_add _ _ ht0).symm
          _ = (t : ℂ) ^ s := by ring_nf
      calc (t : ℂ) ^ (s - 1) * (((X : ℂ) + (H : ℂ) - (t : ℂ)) / (H : ℂ))
          = ((((X : ℂ) + (H : ℂ)) / (H : ℂ)) * (t : ℂ) ^ (s - 1)) -
              ((H : ℂ)⁻¹ * ((t : ℂ) ^ (s - 1) * (t : ℂ))) := by ring
        _ = ((((X : ℂ) + (H : ℂ)) / (H : ℂ)) * (t : ℂ) ^ (s - 1)) -
              ((H : ℂ)⁻¹ * (t : ℂ) ^ s) := by
              rw [hpow]
    have hc1 : ContinuousOn
        (fun t : ℝ => (((X + H : ℝ) : ℂ) / (H : ℂ)) * (t : ℂ) ^ (s - 1)) (Set.Icc X (X + H)) := by
      refine ContinuousOn.mul continuousOn_const ?_
      exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
        fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
    have hc2 : ContinuousOn
        (fun t : ℝ => (H : ℂ)⁻¹ * (t : ℂ) ^ s) (Set.Icc X (X + H)) := by
      refine ContinuousOn.mul continuousOn_const ?_
      exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
        fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
    rw [intervalIntegral.integral_congr h_eq,
      intervalIntegral.integral_sub (hc1.intervalIntegrable_of_Icc (by linarith))
        (hc2.intervalIntegrable_of_Icc (by linarith)),
      intervalIntegral.integral_const_mul, intervalIntegral.integral_const_mul]
    have h_int_s1 : (∫ t in X..(X + H), (t : ℂ) ^ (s - 1)) =
        (((X + H : ℝ) : ℂ) ^ s - (X : ℂ) ^ s) / s := by
      simpa [sub_add_cancel] using
        (integral_cpow (a := X) (b := X + H) (r := s - 1)
          (Or.inl (by simp; linarith)))
    have h_int_s : (∫ t in X..(X + H), (t : ℂ) ^ s) =
        (((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (s + 1) :=
      integral_cpow (Or.inl (by linarith))
    have hpow_XH : ((X + H : ℝ) : ℂ) ^ (s + 1) = ((X + H : ℝ) : ℂ) ^ s * ((X + H : ℝ) : ℂ) := by
      rw [Complex.cpow_add _ _ (Complex.ofReal_ne_zero.mpr (by linarith)), Complex.cpow_one]
    have hpow_X : (X : ℂ) ^ (s + 1) = (X : ℂ) ^ s * (X : ℂ) := by
      rw [Complex.cpow_add _ _ (Complex.ofReal_ne_zero.mpr (by linarith)), Complex.cpow_one]
    rw [h_int_s1, h_int_s, hpow_XH, hpow_X]
    push_cast
    field_simp [hs0, hs1, hH0]
    ring
  rw [h_mellin, h_split, h_p1, h_p2, h_p3]
  field_simp [hs0, hs1, hH0]
  ring

/-- Quadratic vertical decay of `mellin (cutoffPhi X H)` on `{s : ℂ | 0 < s.re}`. -/
private lemma norm_mellin_cutoffPhi_le_div_sq {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H)
    {s : ℂ} (hs : 0 < s.re) :
    ‖mellin (cutoffPhi X H) s‖ ≤
      (2 * (X + H) ^ (s.re + 1) / H + 3) / (s.re ^ 2 + s.im ^ 2) := by
  rw [mellin_cutoffPhi_eq hX hH hs]
  have hXH_pos : 0 < X + H := by linarith
  have hX_pos : 0 < X := by linarith
  have h_num1 : ‖((X + H : ℝ) : ℂ) ^ (s + 1)‖ = (X + H) ^ (s.re + 1) := by
    simpa [Complex.add_re, Complex.one_re] using
      Complex.norm_cpow_eq_rpow_re_of_pos hXH_pos (s + 1)
  have h_num2 : ‖(X : ℂ) ^ (s + 1)‖ = X ^ (s.re + 1) := by
    simpa [Complex.add_re, Complex.one_re] using
      Complex.norm_cpow_eq_rpow_re_of_pos hX_pos (s + 1)
  have h_pow_le : X ^ (s.re + 1) ≤ (X + H) ^ (s.re + 1) :=
    Real.rpow_le_rpow hX_pos.le (by linarith) (by linarith)
  have h_two_pow : ‖(2 : ℂ) ^ (-s)‖ ≤ 1 := by
    have h2 : (2 : ℂ) = ((2 : ℝ) : ℂ) := by norm_cast
    rw [h2, Complex.norm_cpow_eq_rpow_re_of_pos (by norm_num : (0 : ℝ) < 2) (-s), Complex.neg_re]
    exact Real.rpow_le_one_of_one_le_of_nonpos (by norm_num) (by linarith)
  have h_num :
      ‖((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-s)‖ ≤
        2 * (X + H) ^ (s.re + 1) / H + 3 := by
    have hdiv : ((X + H) ^ (s.re + 1) + X ^ (s.re + 1)) / H ≤
        2 * (X + H) ^ (s.re + 1) / H := by
      rw [two_mul]
      exact div_le_div_of_nonneg_right (add_le_add (le_refl _) h_pow_le) hH.le
    calc ‖((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-s)‖
        ≤ ‖(((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ) - 2‖ + ‖(2 : ℂ) ^ (-s)‖ :=
          norm_add_le _ _
      _ ≤ (‖(((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)‖ + ‖(2 : ℂ)‖) + 1 :=
          add_le_add (norm_sub_le _ _) h_two_pow
      _ = ((‖((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)‖ / H) + 2) + 1 := by
          rw [norm_div, Complex.norm_real, Real.norm_eq_abs, abs_of_pos hH,
            Complex.norm_ofNat]
      _ ≤ (((‖((X + H : ℝ) : ℂ) ^ (s + 1)‖ + ‖(X : ℂ) ^ (s + 1)‖) / H) + 2) + 1 := by
          gcongr
          exact norm_sub_le _ _
      _ = ((X + H) ^ (s.re + 1) + X ^ (s.re + 1)) / H + 3 := by
          rw [h_num1, h_num2]; ring
      _ ≤ 2 * (X + H) ^ (s.re + 1) / H + 3 := by linarith
  have h_den : s.re ^ 2 + s.im ^ 2 ≤ ‖s * (s + 1)‖ := by
    rw [norm_mul]
    have h_norm_sq : s.re ^ 2 + s.im ^ 2 = ‖s‖ ^ 2 := by
      rw [Complex.sq_norm, Complex.normSq_apply]
      ring
    have h_s_le_s1 : ‖s‖ ≤ ‖s + 1‖ := by
      rw [← sq_le_sq₀ (norm_nonneg _) (norm_nonneg _), Complex.sq_norm, Complex.sq_norm,
        Complex.normSq_apply, Complex.normSq_apply]
      simp only [Complex.add_re, Complex.one_re, Complex.add_im, Complex.one_im, add_zero]
      nlinarith
    rw [h_norm_sq, sq]
    exact mul_le_mul_of_nonneg_left h_s_le_s1 (norm_nonneg _)
  have h_pos_den : 0 < s.re ^ 2 + s.im ^ 2 := by positivity
  rw [norm_div]
  exact div_le_div₀ (by positivity) h_num h_pos_den h_den

/-- Linear `1 / ‖s‖` bound for `mellin (cutoffPhi X H)` independent of `H`. -/
private lemma norm_mellin_cutoffPhi_le_div_norm {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H)
    {s : ℂ} (hs : 0 < s.re) :
    ‖mellin (cutoffPhi X H) s‖ ≤ 4 * (X + H) ^ s.re / ‖s‖ := by
  have hs0 : s ≠ 0 := by intro h; rw [h] at hs; simp at hs
  have hs1 : s + 1 ≠ 0 := by
    intro h
    have := congrArg Complex.re h
    simp at this
    linarith
  have hH0 : (H : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr hH.ne'
  have h_int_eq :
      mellin (cutoffPhi X H) s =
        (((H : ℂ)⁻¹ * (∫ t : ℝ in X..(X + H), (t : ℂ) ^ s)) +
          (-2 + (2 : ℂ) ^ (-s)) / (s + 1)) / s := by
    rw [mellin_cutoffPhi_eq hX hH hs,
      integral_cpow (Or.inl (by linarith))]
    field_simp [hs0, hs1, hH0]
    ring
  rw [h_int_eq, norm_div]
  have hXH_pos : 0 < X + H := by linarith
  have hXH_ge1 : 1 ≤ (X + H) ^ s.re := Real.one_le_rpow (by linarith) hs.le
  have h_int_bd : ‖(H : ℂ)⁻¹ * (∫ t : ℝ in X..(X + H), (t : ℂ) ^ s)‖ ≤ (X + H) ^ s.re := by
    rw [norm_mul, norm_inv, Complex.norm_real, Real.norm_eq_abs, abs_of_pos hH]
    have h_norm_c : ∀ t ∈ Set.uIoc X (X + H), ‖(t : ℂ) ^ s‖ ≤ (X + H) ^ s.re := by
      intro t ht
      rw [Set.uIoc_of_le (by linarith : X ≤ X + H)] at ht
      have ht_pos : 0 < t := by linarith [ht.1]
      rw [Complex.norm_cpow_eq_rpow_re_of_pos ht_pos s]
      exact Real.rpow_le_rpow ht_pos.le ht.2 hs.le
    have h_le := intervalIntegral.norm_integral_le_of_norm_le_const h_norm_c
    rw [abs_of_nonneg (by linarith : 0 ≤ X + H - X), show X + H - X = H by ring] at h_le
    calc H⁻¹ * ‖∫ t in X..(X + H), (t : ℂ) ^ s‖
        ≤ H⁻¹ * ((X + H) ^ s.re * H) := mul_le_mul_of_nonneg_left h_le (by positivity)
      _ = (X + H) ^ s.re := by field_simp [hH.ne']
  have h_s1_ge1 : 1 ≤ ‖s + 1‖ := by
    have h_re : 1 ≤ (s + 1).re := by simp; linarith
    exact h_re.trans (Complex.re_le_norm _)
  have h_two_pow : ‖(2 : ℂ) ^ (-s)‖ ≤ 1 := by
    have h2 : (2 : ℂ) = ((2 : ℝ) : ℂ) := by norm_cast
    rw [h2, Complex.norm_cpow_eq_rpow_re_of_pos (by norm_num : (0 : ℝ) < 2) (-s), Complex.neg_re]
    exact Real.rpow_le_one_of_one_le_of_nonpos (by norm_num) (by linarith)
  have h_tail_bd : ‖(-2 + (2 : ℂ) ^ (-s)) / (s + 1)‖ ≤ 3 := by
    rw [norm_div]
    have hnum : ‖(-2 : ℂ) + (2 : ℂ) ^ (-s)‖ ≤ 3 := by
      calc ‖(-2 : ℂ) + (2 : ℂ) ^ (-s)‖
          ≤ ‖(-2 : ℂ)‖ + ‖(2 : ℂ) ^ (-s)‖ := norm_add_le _ _
        _ ≤ 2 + 1 := by
            have h2 : ‖(-2 : ℂ)‖ = 2 := by simp
            linarith
        _ = 3 := by norm_num
    exact div_le_of_le_mul₀ (by positivity) (by norm_num) (hnum.trans (by linarith))
  have h_tot_num :
      ‖((H : ℂ)⁻¹ * (∫ t : ℝ in X..(X + H), (t : ℂ) ^ s)) + (-2 + (2 : ℂ) ^ (-s)) / (s + 1)‖ ≤
        4 * (X + H) ^ s.re := by
    calc ‖_‖ ≤ ‖(H : ℂ)⁻¹ * (∫ t : ℝ in X..(X + H), (t : ℂ) ^ s)‖ +
              ‖(-2 + (2 : ℂ) ^ (-s)) / (s + 1)‖ := norm_add_le _ _
      _ ≤ (X + H) ^ s.re + 3 := add_le_add h_int_bd h_tail_bd
      _ ≤ (X + H) ^ s.re + 3 * (X + H) ^ s.re := by linarith
      _ = 4 * (X + H) ^ s.re := by ring
  exact div_le_div_of_nonneg_right h_tot_num (norm_nonneg s)

private lemma differentiableOn_mellin_cutoffPhi {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H) :
    DifferentiableOn ℂ (mellin (cutoffPhi X H)) {s : ℂ | 0 < s.re} := by
  let g : ℂ → ℂ := fun s =>
    (((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-s)) /
      (s * (s + 1))
  have hg_diff : DifferentiableOn ℂ g {s : ℂ | 0 < s.re} := by
    intro s hs
    simp only [Set.mem_ofPred_eq] at hs
    have hs0 : s ≠ 0 := by intro h; rw [h] at hs; simp at hs
    have hs1 : s + 1 ≠ 0 := by
      intro h; have := congrArg Complex.re h; simp at this; linarith
    have hd_XH : DifferentiableAt ℂ (fun z : ℂ => ((X + H : ℝ) : ℂ) ^ (z + 1)) s :=
      DifferentiableAt.const_cpow (differentiableAt_id.add (differentiableAt_const _))
        (Or.inl (Complex.ofReal_ne_zero.mpr (by linarith)))
    have hd_X : DifferentiableAt ℂ (fun z : ℂ => (X : ℂ) ^ (z + 1)) s :=
      DifferentiableAt.const_cpow (differentiableAt_id.add (differentiableAt_const _))
        (Or.inl (Complex.ofReal_ne_zero.mpr (by linarith)))
    have hd_2 : DifferentiableAt ℂ (fun z : ℂ => (2 : ℂ) ^ (-z)) s :=
      DifferentiableAt.const_cpow differentiableAt_id.neg (Or.inl (by norm_num))
    have hd_num : DifferentiableAt ℂ (fun z : ℂ =>
        (((((X + H : ℝ) : ℂ) ^ (z + 1) - (X : ℂ) ^ (z + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-z))) s :=
      (((hd_XH.sub hd_X).div_const _).sub (differentiableAt_const _)).add hd_2
    have hd_den : DifferentiableAt ℂ (fun z : ℂ => z * (z + 1)) s :=
      differentiableAt_id.mul (differentiableAt_id.add (differentiableAt_const _))
    exact (hd_num.div hd_den (mul_ne_zero hs0 hs1)).differentiableWithinAt
  exact hg_diff.congr (fun s hs => mellin_cutoffPhi_eq hX hH hs)

private lemma mellinConvergent_cutoffPhi {X H : ℝ} (_hX : 1 ≤ X) (hH : 0 < H) (σ : ℝ) :
    MellinConvergent (cutoffPhi X H) (σ : ℂ) := by
  let F : ℝ → ℂ := fun t => (t : ℂ) ^ ((σ : ℂ) - 1) * cutoffPhi X H t
  have h_cont : ContinuousOn F (Set.Icc (1 / 2 : ℝ) (X + H)) := by
    refine ContinuousOn.mul ?_ (continuous_cutoffPhi X H).continuousOn
    exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
      fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
  have h_int_Ioc : MeasureTheory.IntegrableOn F (Set.Ioc (1 / 2 : ℝ) (X + H)) :=
    h_cont.integrableOn_Icc.mono_set Set.Ioc_subset_Icc_self
  rw [MellinConvergent]
  have h_smul : (fun t : ℝ => (t : ℂ) ^ ((σ : ℂ) - 1) • cutoffPhi X H t) = F := by
    ext t; simp [F, smul_eq_mul]
  rw [h_smul, ← MeasureTheory.integrable_indicator_iff measurableSet_Ioi,
    indicator_Ioi_cutoffPhi X H hH (fun t : ℝ => (t : ℂ) ^ ((σ : ℂ) - 1)),
    MeasureTheory.integrable_indicator_iff measurableSet_Ioc]
  exact h_int_Ioc

private lemma integrable_inv_sq_add_sq {σ : ℝ} (hσ : 0 < σ) :
    MeasureTheory.Integrable (fun y : ℝ => (σ ^ 2 + y ^ 2)⁻¹) := by
  have h1 : MeasureTheory.Integrable (fun u : ℝ => (1 + u ^ 2)⁻¹) := integrable_inv_one_add_sq
  have h2 := h1.comp_mul_left' (inv_ne_zero hσ.ne')
  refine (h2.const_mul (σ ^ 2)⁻¹).congr (Filter.Eventually.of_forall fun y => ?_)
  field_simp [hσ.ne']

private lemma verticalIntegrable_mellin_cutoffPhi {X H σ : ℝ}
    (hX : 1 ≤ X) (hH : 0 < H) (hσ : 0 < σ) :
    Complex.VerticalIntegrable (mellin (cutoffPhi X H)) σ := by
  rw [Complex.VerticalIntegrable]
  have h_cont : Continuous (fun y : ℝ => mellin (cutoffPhi X H) (σ + y * Complex.I)) := by
    have hc : Continuous (fun y : ℝ => (σ : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
    refine (differentiableOn_mellin_cutoffPhi hX hH).continuousOn.comp_continuous hc fun y => ?_
    simp [hσ]
  set K : ℝ := 2 * (X + H) ^ (σ + 1) / H + 3
  refine (integrable_inv_sq_add_sq hσ |>.const_mul K).mono' h_cont.aestronglyMeasurable
    (Filter.Eventually.of_forall fun y => ?_)
  have hs_re : (σ + y * Complex.I).re = σ := by simp
  have hbd := norm_mellin_cutoffPhi_le_div_sq hX hH (s := σ + y * Complex.I) (by simpa using hσ)
  rw [hs_re] at hbd
  simpa [K, div_eq_mul_inv, mul_comm] using hbd

/-- Exact Mellin–Mertens identity for the trapezoidal cutoff at `Re(s) = 2`. -/
private theorem sum_moebius_cutoffPhi_eq_mellinInv_two {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H) :
    (∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) =
      ((1 / (2 * Real.pi) : ℝ) : ℂ) *
        ∫ y : ℝ, zetaInv (2 + y * Complex.I) * mellin (cutoffPhi X H) (2 + y * Complex.I) := by
  set phi := cutoffPhi X H
  have h_mc2 : MellinConvergent phi 2 := by
    simpa using mellinConvergent_cutoffPhi hX hH 2
  have h_vi2 : Complex.VerticalIntegrable (mellin phi) 2 :=
    verticalIntegrable_mellin_cutoffPhi hX hH (by norm_num)
  let F : ℕ → ℝ → ℂ := fun n y =>
    if n = 0 then 0
    else (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I)) *
      mellin phi (2 + y * Complex.I)
  have h_term : ∀ n : ℕ,
      (ArithmeticFunction.moebius n : ℂ) * phi n =
        ((1 / (2 * Real.pi) : ℝ) : ℂ) * ∫ y : ℝ, F n y := by
    intro n
    rcases Nat.eq_zero_or_pos n with rfl | hn_pos
    · simp [F]
    · have hn_real_pos : (0 : ℝ) < n := Nat.cast_pos.mpr hn_pos
      have h_inv := mellinInv_mellin_eq 2 phi hn_real_pos h_mc2 h_vi2
        ((continuous_cutoffPhi X H).continuousAt)
      rw [mellinInv] at h_inv
      simp only [smul_eq_mul, Complex.real_smul] at h_inv
      have h_inv' :
          ((1 / (2 * Real.pi) : ℝ) : ℂ) *
            ∫ y : ℝ, (n : ℂ) ^ (-(2 + y * Complex.I)) * mellin phi (2 + y * Complex.I) = phi n := by
        simpa using h_inv
      rw [← h_inv']
      have hn0 : n ≠ 0 := hn_pos.ne'
      calc (ArithmeticFunction.moebius n : ℂ) *
            (((1 / (2 * Real.pi) : ℝ) : ℂ) *
              ∫ y : ℝ, (n : ℂ) ^ (-(2 + y * Complex.I)) * mellin phi (2 + y * Complex.I))
          = ((1 / (2 * Real.pi) : ℝ) : ℂ) *
            ((ArithmeticFunction.moebius n : ℂ) *
              ∫ y : ℝ, (n : ℂ) ^ (-(2 + y * Complex.I)) * mellin phi (2 + y * Complex.I)) := by ring
        _ = ((1 / (2 * Real.pi) : ℝ) : ℂ) * ∫ y : ℝ, F n y := by
            congr 1
            rw [← MeasureTheory.integral_const_mul]
            refine MeasureTheory.integral_congr_ae (Filter.Eventually.of_forall fun y => ?_)
            simp [F, hn0, mul_assoc]
  have h_aesm : ∀ n : ℕ, MeasureTheory.AEStronglyMeasurable (F n) MeasureTheory.volume := by
    intro n
    rcases Nat.eq_zero_or_pos n with rfl | hn_pos
    · simpa [F] using MeasureTheory.aestronglyMeasurable_const
    · have hc_m : Continuous (fun y : ℝ => mellin phi (2 + y * Complex.I)) := by
        have hc : Continuous (fun y : ℝ => (2 : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
        exact (differentiableOn_mellin_cutoffPhi hX hH).continuousOn.comp_continuous hc
          fun y => by norm_num
      have hc_p : Continuous (fun y : ℝ => (n : ℂ) ^ (-(2 + y * Complex.I))) := by
        refine Continuous.const_cpow ?_
          (Or.inl (Complex.ofReal_ne_zero.mpr (Nat.cast_pos.mpr hn_pos).ne'))
        fun_prop
      have hF_eq : F n = fun y : ℝ =>
          (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I)) *
            mellin phi (2 + y * Complex.I) := by
        ext y; simp [F, hn_pos.ne']
      rw [hF_eq]
      exact ((continuous_const.mul hc_p).mul hc_m).aestronglyMeasurable
  set K : ℝ := 2 * (X + H) ^ ((2 : ℝ) + 1) / H + 3
  have hK_nn : 0 ≤ K := by positivity
  have h_lintegral_bound :
      (∑' n : ℕ, ∫⁻ y : ℝ, ‖F n y‖ₑ ∂MeasureTheory.volume) ≠ ⊤ := by
    have h_base : MeasureTheory.Integrable (fun y : ℝ => K * (2 ^ 2 + y ^ 2)⁻¹) :=
      (integrable_inv_sq_add_sq (by norm_num)).const_mul K
    have h_base_lt : ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume < ⊤ :=
      h_base.hasFiniteIntegral
    let a : ℕ → ENNReal := fun n => ENNReal.ofReal (((n : ℝ) ^ (2 : ℝ))⁻¹)
    have h_each : ∀ n : ℕ,
        ∫⁻ y : ℝ, ‖F n y‖ₑ ∂MeasureTheory.volume ≤
          a n * ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume := by
      intro n
      rcases Nat.eq_zero_or_pos n with rfl | hn_pos
      · simp [F, a]
      · have hn0 : n ≠ 0 := hn_pos.ne'
        have hn_pos_r : (0 : ℝ) < n := Nat.cast_pos.mpr hn_pos
        rw [← MeasureTheory.lintegral_const_mul'' _ h_base.aestronglyMeasurable.enorm]
        refine MeasureTheory.lintegral_mono fun y => ?_
        have h_mu : ‖(ArithmeticFunction.moebius n : ℂ)‖ ≤ 1 := by
          simpa [Complex.norm_intCast] using
            (show |(ArithmeticFunction.moebius n : ℝ)| ≤ 1 by
              exact_mod_cast ArithmeticFunction.abs_moebius_le_one (n := n))
        have h_cpow : ‖(n : ℂ) ^ (-(2 + y * Complex.I))‖ = ((n : ℝ) ^ (2 : ℝ))⁻¹ := by
          have hn_c : (n : ℂ) = ((n : ℝ) : ℂ) := by norm_cast
          rw [hn_c, Complex.norm_cpow_eq_rpow_re_of_pos hn_pos_r]
          simp [Real.rpow_neg hn_pos_r.le]
        have h_mbd := norm_mellin_cutoffPhi_le_div_sq hX hH (s := 2 + y * Complex.I) (by norm_num)
        have hre2 : (2 + y * Complex.I).re = 2 := by simp
        rw [hre2] at h_mbd
        have h_norm : ‖F n y‖ ≤ ((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹) := by
          dsimp [F]
          simp only [hn0, ↓reduceIte, norm_mul, h_cpow]
          calc ‖(ArithmeticFunction.moebius n : ℂ)‖ * ((n : ℝ) ^ (2 : ℝ))⁻¹ *
                ‖mellin phi (2 + y * Complex.I)‖
              ≤ 1 * ((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹) := by
                refine mul_le_mul (mul_le_mul_of_nonneg_right h_mu (by positivity)) ?_
                  (norm_nonneg _) (by positivity)
                simpa [K, div_eq_mul_inv] using h_mbd
            _ = ((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹) := by ring
        have h_prod : ENNReal.ofReal (((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹)) =
            a n * ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ := by
          rw [ENNReal.ofReal_mul (by positivity)]
          congr 1
          rw [Real.enorm_eq_ofReal_abs, abs_of_nonneg (mul_nonneg hK_nn (by positivity))]
        have h_en : ‖F n y‖ₑ ≤
            ENNReal.ofReal (((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹)) := by
          rw [← ofReal_norm (F n y)]
          exact ENNReal.ofReal_le_ofReal h_norm
        exact h_en.trans_eq h_prod
    have ha_sum : (∑' n : ℕ, a n) < ⊤ :=
      (Real.summable_nat_rpow_inv.mpr one_lt_two).tsum_ofReal_lt_top
    have h_sum_le : (∑' n : ℕ, ∫⁻ y : ℝ, ‖F n y‖ₑ ∂MeasureTheory.volume) ≤
        (∑' n : ℕ, a n) * ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume := by
      calc (∑' n : ℕ, ∫⁻ y : ℝ, ‖F n y‖ₑ ∂MeasureTheory.volume)
          ≤ ∑' n : ℕ, a n * ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume :=
            ENNReal.tsum_le_tsum h_each
        _ = (∑' n : ℕ, a n) * ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume :=
            ENNReal.tsum_mul_right
    exact (h_sum_le.trans_lt (ENNReal.mul_lt_top ha_sum h_base_lt)).ne
  have h_int_tsum := MeasureTheory.integral_tsum h_aesm h_lintegral_bound
  have h_sum_term :
      (∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * phi n) =
        ((1 / (2 * Real.pi) : ℝ) : ℂ) * ∑' n : ℕ, ∫ y : ℝ, F n y := by
    have h_fun : (fun n : ℕ => (ArithmeticFunction.moebius n : ℂ) * phi n) =
        fun n : ℕ => ((1 / (2 * Real.pi) : ℝ) : ℂ) * ∫ y : ℝ, F n y :=
      funext h_term
    rw [h_fun, tsum_mul_left]
  rw [h_sum_term, ← h_int_tsum]
  congr 1
  refine MeasureTheory.integral_congr_ae (Filter.Eventually.of_forall fun y => ?_)
  have hs2 : 1 < (2 + y * Complex.I).re := by simp
  have hs_ne1 : 2 + y * Complex.I ≠ 1 := by
    intro h
    have := congrArg Complex.re h
    simp at this
  have h_lseries_eq :
      (∑' n : ℕ, if n = 0 then (0 : ℂ) else
        (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I))) =
        zetaInv (2 + y * Complex.I) := by
    have hmul := LSeries_one_mul_Lseries_moebius hs2
    rw [LSeries_one_eq_riemannZeta hs2] at hmul
    have hL_eq : LSeries (↗ArithmeticFunction.moebius) (2 + y * Complex.I) =
        ∑' n : ℕ, if n = 0 then (0 : ℂ) else
          (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I)) := by
      simp only [LSeries, LSeries.term]
      congr 1
      ext n
      split_ifs with hn
      · rfl
      · simp only [div_eq_mul_inv, ← Complex.cpow_neg]
    rw [← hL_eq]
    have hinv : LSeries (↗ArithmeticFunction.moebius) (2 + y * Complex.I) =
        (riemannZeta (2 + y * Complex.I))⁻¹ :=
      eq_inv_of_mul_eq_one_right hmul
    simp [zetaInv, hs_ne1, hinv]
  have hF_rw : (fun n : ℕ => F n y) = fun n : ℕ =>
      (if n = 0 then (0 : ℂ) else
        (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I))) *
        mellin phi (2 + y * Complex.I) := by
    ext n
    by_cases hn : n = 0 <;> simp [F, hn]
  dsimp only
  rw [hF_rw, tsum_mul_right, h_lseries_eq]

/-! ### Stage 5: Cauchy Rectangle Contour Shift & Unconditional `RH → MertensBound` -/

/-- Exact value of the improper real power tail integral `∫ t in Ioi c, t ^ p`
for `c > 0`, `p < -1`. -/
private lemma setIntegral_Ioi_rpow_of_lt {c p : ℝ} (hc : 0 < c) (hp : p < -1) :
    ∫ t : ℝ in Set.Ioi c, t ^ p = c ^ (p + 1) / (-(p + 1)) := by
  have h1 :
      ((∫ t : ℝ in Set.Ioi c, t ^ p : ℝ) : ℂ) =
        ∫ t : ℝ in Set.Ioi c, ((t ^ p : ℝ) : ℂ) :=
    integral_ofReal.symm
  have h2 :
      (∫ t : ℝ in Set.Ioi c, ((t ^ p : ℝ) : ℂ)) =
        ∫ t : ℝ in Set.Ioi c, (t : ℂ) ^ (p : ℂ) := by
    refine MeasureTheory.setIntegral_congr_fun measurableSet_Ioi fun t ht => ?_
    exact Complex.ofReal_cpow (hc.le.trans ht.le) p
  have h3 : (∫ t : ℝ in Set.Ioi c, (t : ℂ) ^ (p : ℂ)) =
      -(c : ℂ) ^ ((p : ℂ) + 1) / ((p : ℂ) + 1) :=
    integral_Ioi_cpow_of_lt (by simpa using hp) hc
  have h4 : -(c : ℂ) ^ ((p : ℂ) + 1) / ((p : ℂ) + 1) = ((c ^ (p + 1) / (-(p + 1)) : ℝ) : ℂ) := by
    have hcp : (c : ℂ) ^ ((p : ℂ) + 1) = ((c ^ (p + 1) : ℝ) : ℂ) := by
      have hre : (p : ℂ) + 1 = ((p + 1 : ℝ) : ℂ) := by push_cast; rfl
      rw [hre, ← Complex.ofReal_cpow hc.le (p + 1)]
    rw [hcp]
    push_cast
    have hp1 : (p : ℂ) + 1 ≠ 0 := by
      intro h
      have := congrArg Complex.re h
      simp at this
      linarith
    field_simp [hp1]
  exact Complex.ofReal_injective (h1.trans (h2.trans (h3.trans h4)))

/-- Integrability of `(1 + |y|) ^ eps / (σ ^ 2 + y ^ 2)` on `ℝ` for `0 < σ` and `0 ≤ eps < 1`. -/
private lemma integrable_one_add_abs_rpow_div {σ eps : ℝ}
    (hσ : 0 < σ) (heps0 : 0 ≤ eps) (heps1 : eps < 1) :
    MeasureTheory.Integrable (fun y : ℝ => (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2)) := by
  let g₁ : ℝ → ℝ := Set.indicator (Set.Icc (-1 : ℝ) 1) (fun _ => (2 : ℝ) ^ eps / σ ^ 2)
  let g₂ : ℝ → ℝ := Set.indicator (Set.Ioi (1 : ℝ)) (fun y => (2 : ℝ) ^ eps * y ^ (eps - 2))
  let g₃ : ℝ → ℝ := fun y =>
    Set.indicator (Set.Ioi (1 : ℝ)) (fun t => (2 : ℝ) ^ eps * t ^ (eps - 2)) (-y)
  have hg₁ : MeasureTheory.Integrable g₁ :=
    (MeasureTheory.integrable_indicator_iff measurableSet_Icc).mpr
      (continuousOn_const.integrableOn_Icc (a := (-1 : ℝ)) (b := 1))
  have hg₂ : MeasureTheory.Integrable g₂ :=
    (MeasureTheory.integrable_indicator_iff measurableSet_Ioi).mpr
      (MeasureTheory.Integrable.const_mul
        (integrableOn_Ioi_rpow_of_lt (by linarith : eps - 2 < -1) zero_lt_one) ((2 : ℝ) ^ eps))
  have hg₃ : MeasureTheory.Integrable g₃ := hg₂.comp_neg
  have hf_meas : MeasureTheory.AEStronglyMeasurable
      (fun y : ℝ => (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2)) MeasureTheory.volume :=
    ((Continuous.rpow (by fun_prop : Continuous fun y : ℝ => 1 + |y|) continuous_const
      (fun y => Or.inl (by linarith [abs_nonneg y]))).div
      (by fun_prop : Continuous fun y : ℝ => σ ^ 2 + y ^ 2)
      (fun y => ne_of_gt (by positivity))).aestronglyMeasurable
  refine ((hg₁.add hg₂).add hg₃).mono' hf_meas (Filter.Eventually.of_forall fun y => ?_)
  have hf_nn : 0 ≤ (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2) := by positivity
  rw [Real.norm_of_nonneg hf_nn]
  have h2_nn : 0 ≤ (2 : ℝ) ^ eps := by positivity
  have hg₁_nn : 0 ≤ g₁ y := by
    by_cases h : y ∈ Set.Icc (-1 : ℝ) 1
    · simp only [g₁, Set.indicator_of_mem h]; positivity
    · simp [g₁, h]
  have hg₂_nn : 0 ≤ g₂ y := by
    by_cases h : 1 < y
    · have hpos : 0 ≤ (2 : ℝ) ^ eps * y ^ (eps - 2) := by positivity
      simpa [g₂, h] using hpos
    · simp [g₂, h]
  have hg₃_nn : 0 ≤ g₃ y := by
    by_cases h : 1 < -y
    · have hpos : 0 ≤ (2 : ℝ) ^ eps * (-y) ^ (eps - 2) := by positivity
      simpa [g₃, h] using hpos
    · simp [g₃, h]
  by_cases hy1 : |y| ≤ 1
  · have h_mem : y ∈ Set.Icc (-1 : ℝ) 1 := abs_le.mp hy1
    have hg₁_val : g₁ y = (2 : ℝ) ^ eps / σ ^ 2 := by simp [g₁, h_mem]
    have h_bd : (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2) ≤ (2 : ℝ) ^ eps / σ ^ 2 := by
      have hnum : (1 + |y|) ^ eps ≤ (2 : ℝ) ^ eps :=
        Real.rpow_le_rpow (by linarith [abs_nonneg y]) (by linarith) heps0
      have hden : σ ^ 2 ≤ σ ^ 2 + y ^ 2 := le_add_of_nonneg_right (sq_nonneg y)
      exact div_le_div₀ (by positivity) hnum (by positivity) hden
    simp only [Pi.add_apply]; linarith
  · have hy_gt : 1 < |y| := lt_of_not_ge hy1
    rcases le_or_gt 0 y with hy0 | hy0
    · have h1y : 1 < y := by rwa [abs_of_nonneg hy0] at hy_gt
      have h1y_le : 1 + |y| ≤ 2 * y := by
        rw [abs_of_nonneg hy0]; linarith
      have hnum : (1 + |y|) ^ eps ≤ (2 : ℝ) ^ eps * y ^ eps := by
        calc (1 + |y|) ^ eps ≤ (2 * y) ^ eps :=
              Real.rpow_le_rpow (by positivity) h1y_le heps0
          _ = (2 : ℝ) ^ eps * y ^ eps := Real.mul_rpow (by norm_num) (by linarith)
      have hden : y ^ 2 ≤ σ ^ 2 + y ^ 2 := le_add_of_nonneg_left (sq_nonneg σ)
      have hrpow_div : y ^ eps / y ^ 2 = y ^ (eps - 2) := by
        rw [← Real.rpow_two y, ← Real.rpow_sub (by linarith : 0 < y)]
      have hg₂_val : g₂ y = (2 : ℝ) ^ eps * y ^ (eps - 2) := by
        simp [g₂, h1y]
      have h_bd : (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2) ≤ g₂ y := by
        rw [hg₂_val, ← hrpow_div, mul_div_assoc']
        exact div_le_div₀ (by positivity) hnum (by positivity) hden
      simp only [Pi.add_apply]; linarith
    · have h1ny : 1 < -y := by rwa [abs_of_neg hy0] at hy_gt
      have h1y_le : 1 + |y| ≤ 2 * (-y) := by
        rw [abs_of_neg hy0]; linarith
      have hnum : (1 + |y|) ^ eps ≤ (2 : ℝ) ^ eps * (-y) ^ eps := by
        calc (1 + |y|) ^ eps ≤ (2 * (-y)) ^ eps :=
              Real.rpow_le_rpow (by positivity) h1y_le heps0
          _ = (2 : ℝ) ^ eps * (-y) ^ eps := Real.mul_rpow (by norm_num) (by linarith)
      have hden : (-y) ^ 2 ≤ σ ^ 2 + y ^ 2 := by
        rw [neg_sq]
        exact le_add_of_nonneg_left (sq_nonneg σ)
      have hrpow_div : (-y) ^ eps / (-y) ^ 2 = (-y) ^ (eps - 2) := by
        rw [← Real.rpow_two (-y), ← Real.rpow_sub (by linarith : 0 < -y)]
      have hg₃_val : g₃ y = (2 : ℝ) ^ eps * (-y) ^ (eps - 2) := by
        simp [g₃, h1ny]
      have h_bd : (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2) ≤ g₃ y := by
        rw [hg₃_val, ← hrpow_div, mul_div_assoc']
        exact div_le_div₀ (by positivity) hnum (by positivity) hden
      simp only [Pi.add_apply]; linarith

/-- Contour shift under `_root_.RiemannHypothesis` from `Re(s) = 2` to any `σ₀ ∈ (1/2, 2)`. -/
private theorem mellin_cutoffPhi_two_eq_sigma (h_rh : _root_.RiemannHypothesis)
    {X H σ₀ : ℝ} (hX : 1 ≤ X) (hH : 0 < H) (hσ₀_lo : 1 / 2 < σ₀) (hσ₀_hi : σ₀ < 2) :
    ∫ y : ℝ, zetaInv (2 + y * Complex.I) * mellin (cutoffPhi X H) (2 + y * Complex.I) =
      ∫ y : ℝ, zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I) := by
  let G : ℂ → ℂ := fun s => zetaInv s * mellin (cutoffPhi X H) s
  let eps : ℝ := 1 / 4
  obtain ⟨Cζ, hCζ_pos, hCζ⟩ :=
    inv_zeta_isBigO_im_of_rh h_rh hσ₀_lo (by norm_num : (0 : ℝ) < eps)
  let K : ℝ := 2 * (X + H) ^ (3 : ℝ) / H + 3
  have hK_nn : 0 ≤ K := by positivity
  have hXH_ge1 : 1 ≤ X + H := by linarith
  have hG_bd : ∀ s : ℂ, σ₀ ≤ s.re → s.re ≤ 2 →
      ‖G s‖ ≤ (Cζ * K) * ((1 + |s.im|) ^ eps / (σ₀ ^ 2 + s.im ^ 2)) := by
    intro s hs_lo hs_hi
    have hs_pos : 0 < s.re := by linarith
    have hz := hCζ s hs_lo
    have hm := norm_mellin_cutoffPhi_le_div_sq hX hH hs_pos
    have hpow_XH : (X + H) ^ (s.re + 1) ≤ (X + H) ^ (3 : ℝ) :=
      Real.rpow_le_rpow_of_exponent_le hXH_ge1 (by linarith)
    have hm_K : ‖mellin (cutoffPhi X H) s‖ ≤ K / (σ₀ ^ 2 + s.im ^ 2) := by
      have hnum : 2 * (X + H) ^ (s.re + 1) / H + 3 ≤ K := by
        dsimp [K]
        gcongr
      have hden : σ₀ ^ 2 + s.im ^ 2 ≤ s.re ^ 2 + s.im ^ 2 := by
        have hsq : σ₀ ^ 2 ≤ s.re ^ 2 := sq_le_sq' (by linarith) hs_lo
        linarith
      exact hm.trans (div_le_div₀ hK_nn hnum (by positivity) hden)
    have hg_prod : ‖G s‖ ≤ (Cζ * (1 + |s.im|) ^ eps) * (K / (σ₀ ^ 2 + s.im ^ 2)) := by
      dsimp [G]
      rw [norm_mul]
      exact mul_le_mul hz hm_K (norm_nonneg _) (by positivity)
    calc ‖G s‖ ≤ (Cζ * (1 + |s.im|) ^ eps) * (K / (σ₀ ^ 2 + s.im ^ 2)) := hg_prod
      _ = (Cζ * K) * ((1 + |s.im|) ^ eps / (σ₀ ^ 2 + s.im ^ 2)) := by ring
  have hG_diff : DifferentiableOn ℂ G {s : ℂ | 1 / 2 < s.re} := by
    intro s hs
    simp only [Set.mem_ofPred_eq] at hs
    have hd1 : DifferentiableAt ℂ zetaInv s :=
      (differentiableOn_zetaInv_of_rh h_rh s hs).differentiableAt
        (IsOpen.mem_nhds (isOpen_lt continuous_const Complex.continuous_re) hs)
    have hd2 : DifferentiableAt ℂ (mellin (cutoffPhi X H)) s :=
      (differentiableOn_mellin_cutoffPhi hX hH s (by linarith : (0 : ℝ) < s.re)).differentiableAt
        (IsOpen.mem_nhds (isOpen_lt continuous_const Complex.continuous_re)
          (show (0 : ℝ) < s.re by linarith))
    exact (hd1.mul hd2).differentiableWithinAt
  have h_vert_int : ∀ σ : ℝ, σ₀ ≤ σ → σ ≤ 2 →
      MeasureTheory.Integrable (fun y : ℝ => G (σ + y * Complex.I)) := by
    intro σ hσ_lo hσ_hi
    have hc : Continuous (fun y : ℝ => G (σ + y * Complex.I)) := by
      have hline : Continuous (fun y : ℝ => (σ : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
      exact hG_diff.continuousOn.comp_continuous hline fun y => by simp; linarith
    refine ((integrable_one_add_abs_rpow_div (by linarith : 0 < σ₀) (by norm_num : 0 ≤ eps)
      (by norm_num : eps < 1)).const_mul (Cζ * K)).mono' hc.aestronglyMeasurable
      (Filter.Eventually.of_forall fun y => ?_)
    have hs_re : (σ + y * Complex.I).re = σ := by simp
    have hs_im : (σ + y * Complex.I).im = y := by simp
    simpa [hs_re, hs_im] using
      hG_bd (σ + y * Complex.I) (by simpa using hσ_lo) (by simpa using hσ_hi)
  have h_int2 : MeasureTheory.Integrable (fun y : ℝ => G (2 + y * Complex.I)) :=
    h_vert_int 2 hσ₀_hi.le le_rfl
  have h_intσ : MeasureTheory.Integrable (fun y : ℝ => G (σ₀ + y * Complex.I)) :=
    h_vert_int σ₀ le_rfl hσ₀_hi.le
  have h_rect : ∀ T : ℝ, 0 ≤ T →
      (∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I)) -
      (∫ x : ℝ in σ₀..2, G (x + T * Complex.I)) +
      Complex.I • (∫ y : ℝ in (-T)..T, G (2 + y * Complex.I)) -
      Complex.I • (∫ y : ℝ in (-T)..T, G (σ₀ + y * Complex.I)) = 0 := by
    intro T _hT
    have h_sub : Set.uIcc σ₀ 2 ×ℂ Set.uIcc (-T) T ⊆ {s : ℂ | 1 / 2 < s.re} := by
      intro s hs
      rcases hs with ⟨hs_re, _⟩
      rw [Set.uIcc_of_le hσ₀_hi.le] at hs_re
      exact hσ₀_lo.trans_le hs_re.1
    have h_cauchy := Complex.integral_boundary_rect_eq_zero_of_differentiableOn G
      (σ₀ + (-T) * Complex.I) (2 + T * Complex.I) (hG_diff.mono (by simpa using h_sub))
    simpa using h_cauchy
  let C_horiz : ℝ := (2 - σ₀) * (Cζ * K) * (2 : ℝ) ^ eps
  have h_top_lim : Filter.Tendsto (fun T : ℝ => ∫ x : ℝ in σ₀..2, G (x + T * Complex.I))
      Filter.atTop (𝓝 0) := by
    have h_bound_lim : Filter.Tendsto (fun T : ℝ => C_horiz * T ^ (eps - 2))
        Filter.atTop (𝓝 0) := by
      have ht := tendsto_rpow_neg_atTop (by norm_num : (0 : ℝ) < 2 - eps)
      simpa [mul_zero, show -(2 - eps) = eps - 2 by ring] using ht.const_mul C_horiz
    rw [tendsto_zero_iff_norm_tendsto_zero]
    refine squeeze_zero' (Filter.Eventually.of_forall fun T => norm_nonneg _) ?_ h_bound_lim
    filter_upwards [Filter.eventually_ge_atTop (1 : ℝ)] with T hT
    have h_norm_x : ∀ x ∈ Set.uIoc σ₀ 2,
        ‖G (x + T * Complex.I)‖ ≤ (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) := by
      intro x hx
      rw [Set.uIoc_of_le hσ₀_hi.le] at hx
      have him : (x + T * Complex.I).im = T := by simp
      have hbd := hG_bd (x + T * Complex.I) (by simpa using hx.1.le) (by simpa using hx.2)
      rw [him, abs_of_pos (by linarith)] at hbd
      have h1T : (1 + T) ^ eps ≤ (2 * T) ^ eps :=
        Real.rpow_le_rpow (by linarith) (by linarith) (by norm_num)
      have h2T : (2 * T) ^ eps = (2 : ℝ) ^ eps * T ^ eps :=
        Real.mul_rpow (by norm_num) (by linarith)
      have hden : T ^ 2 ≤ σ₀ ^ 2 + T ^ 2 := le_add_of_nonneg_left (sq_nonneg _)
      have hpow : T ^ eps / T ^ 2 = T ^ (eps - 2) := by
        rw [← Real.rpow_two T, ← Real.rpow_sub (by linarith)]
      calc ‖G (x + T * Complex.I)‖
          ≤ (Cζ * K) * ((1 + T) ^ eps / (σ₀ ^ 2 + T ^ 2)) := hbd
        _ ≤ (Cζ * K) * (((2 : ℝ) ^ eps * T ^ eps) / T ^ 2) := by
            gcongr; linarith [h1T, h2T]
        _ = (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) := by
            rw [mul_div_assoc, hpow]; ring
    have hi := intervalIntegral.norm_integral_le_of_norm_le_const h_norm_x
    rw [abs_of_nonneg (by linarith)] at hi
    calc ‖∫ x : ℝ in σ₀..2, G (x + T * Complex.I)‖
        ≤ (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) * (2 - σ₀) := hi
      _ = C_horiz * T ^ (eps - 2) := by dsimp [C_horiz]; ring
  have h_bot_lim : Filter.Tendsto (fun T : ℝ => ∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I))
      Filter.atTop (𝓝 0) := by
    have h_bound_lim : Filter.Tendsto (fun T : ℝ => C_horiz * T ^ (eps - 2))
        Filter.atTop (𝓝 0) := by
      have ht := tendsto_rpow_neg_atTop (by norm_num : (0 : ℝ) < 2 - eps)
      simpa [mul_zero, show -(2 - eps) = eps - 2 by ring] using ht.const_mul C_horiz
    rw [tendsto_zero_iff_norm_tendsto_zero]
    refine squeeze_zero' (Filter.Eventually.of_forall fun T => norm_nonneg _) ?_ h_bound_lim
    filter_upwards [Filter.eventually_ge_atTop (1 : ℝ)] with T hT
    have h_norm_x : ∀ x ∈ Set.uIoc σ₀ 2,
        ‖G (x + (-T) * Complex.I)‖ ≤ (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) := by
      intro x hx
      rw [Set.uIoc_of_le hσ₀_hi.le] at hx
      have him : (x + (-T) * Complex.I).im = -T := by simp
      have hbd := hG_bd (x + (-T) * Complex.I) (by simpa using hx.1.le) (by simpa using hx.2)
      rw [him, abs_neg, abs_of_pos (by linarith), neg_sq] at hbd
      have h1T : (1 + T) ^ eps ≤ (2 * T) ^ eps :=
        Real.rpow_le_rpow (by linarith) (by linarith) (by norm_num)
      have h2T : (2 * T) ^ eps = (2 : ℝ) ^ eps * T ^ eps :=
        Real.mul_rpow (by norm_num) (by linarith)
      have hden : T ^ 2 ≤ σ₀ ^ 2 + T ^ 2 := le_add_of_nonneg_left (sq_nonneg _)
      have hpow : T ^ eps / T ^ 2 = T ^ (eps - 2) := by
        rw [← Real.rpow_two T, ← Real.rpow_sub (by linarith)]
      calc ‖G (x + (-T) * Complex.I)‖
          ≤ (Cζ * K) * ((1 + T) ^ eps / (σ₀ ^ 2 + T ^ 2)) := hbd
        _ ≤ (Cζ * K) * (((2 : ℝ) ^ eps * T ^ eps) / T ^ 2) := by
            gcongr; linarith [h1T, h2T]
        _ = (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) := by
            rw [mul_div_assoc, hpow]; ring
    have hi := intervalIntegral.norm_integral_le_of_norm_le_const h_norm_x
    rw [abs_of_nonneg (by linarith)] at hi
    calc ‖∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I)‖
        ≤ (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) * (2 - σ₀) := hi
      _ = C_horiz * T ^ (eps - 2) := by dsimp [C_horiz]; ring
  have h_vright_lim :
      Filter.Tendsto (fun T : ℝ => ∫ y : ℝ in (-T)..T, G (2 + y * Complex.I))
        Filter.atTop (𝓝 (∫ y : ℝ, G (2 + y * Complex.I))) :=
    MeasureTheory.intervalIntegral_tendsto_integral h_int2
      Filter.tendsto_neg_atTop_atBot Filter.tendsto_id
  have h_vleft_lim :
      Filter.Tendsto (fun T : ℝ => ∫ y : ℝ in (-T)..T, G (σ₀ + y * Complex.I))
        Filter.atTop (𝓝 (∫ y : ℝ, G (σ₀ + y * Complex.I))) :=
    MeasureTheory.intervalIntegral_tendsto_integral h_intσ
      Filter.tendsto_neg_atTop_atBot Filter.tendsto_id
  have h_comb_lim :
      Filter.Tendsto
        (fun T : ℝ =>
          (∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I)) -
          (∫ x : ℝ in σ₀..2, G (x + T * Complex.I)) +
          Complex.I • (∫ y : ℝ in (-T)..T, G (2 + y * Complex.I)) -
          Complex.I • (∫ y : ℝ in (-T)..T, G (σ₀ + y * Complex.I)))
        Filter.atTop
        (𝓝 (0 - 0 + Complex.I • (∫ y : ℝ, G (2 + y * Complex.I)) -
          Complex.I • (∫ y : ℝ, G (σ₀ + y * Complex.I)))) :=
    (((h_bot_lim.sub h_top_lim).add (h_vright_lim.const_smul Complex.I)).sub
      (h_vleft_lim.const_smul Complex.I))
  have h_zero_lim :
      Filter.Tendsto
        (fun T : ℝ =>
          (∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I)) -
          (∫ x : ℝ in σ₀..2, G (x + T * Complex.I)) +
          Complex.I • (∫ y : ℝ in (-T)..T, G (2 + y * Complex.I)) -
          Complex.I • (∫ y : ℝ in (-T)..T, G (σ₀ + y * Complex.I)))
        Filter.atTop (𝓝 0) :=
    tendsto_const_nhds.congr' (by
      filter_upwards [Filter.eventually_ge_atTop (0 : ℝ)] with T hT
      exact (h_rect T hT).symm)
  have h_eq0 := tendsto_nhds_unique h_comb_lim h_zero_lim
  simp only [sub_zero, zero_add, smul_eq_mul] at h_eq0
  have h_mul_eq : Complex.I * (∫ y : ℝ, G (2 + y * Complex.I)) =
      Complex.I * (∫ y : ℝ, G (σ₀ + y * Complex.I)) := sub_eq_zero.mp h_eq0
  exact mul_left_cancel₀ Complex.I_ne_zero h_mul_eq

/-- The pointwise asymptotic Mertens bound `M(x) = O(x^(1/2 + ε))`. -/
private def MertensBound : Prop :=
  ∀ ε > 0, ∃ C > 0, ∀ x ≥ 1, |(mertens x : ℝ)| ≤ C * x ^ ((1 / 2 : ℝ) + ε)

/-- Littlewood (1912) converse: `_root_.RiemannHypothesis` implies `MertensBound`
unconditionally via Perron/Mellin–Mertens contour shift to `Re(s) = 1/2 + ε/4`. -/
private theorem rh_implies_mertens_bound : _root_.RiemannHypothesis → MertensBound := by
  intro h_rh ε hε
  set δ₀ : ℝ := min (ε / 4) (1 / 4)
  have hδ_pos : 0 < δ₀ := lt_min (by linarith) (by norm_num)
  have hδ_le_quarter : δ₀ ≤ 1 / 4 := min_le_right _ _
  have h4δ_le : 4 * δ₀ ≤ ε := by linarith [min_le_left (ε / 4) (1 / 4)]
  set σ₀ : ℝ := 1 / 2 + δ₀
  have hσ₀_lo : 1 / 2 < σ₀ := by dsimp [σ₀]; linarith
  have hσ₀_hi : σ₀ < 2 := by dsimp [σ₀]; linarith
  have hσ₀_le1 : σ₀ ≤ 1 := by dsimp [σ₀]; linarith
  obtain ⟨Cζ, hCζ_pos, hCζ⟩ := inv_zeta_isBigO_im_of_rh h_rh hσ₀_lo hδ_pos
  have hlog_bd : ∀ y : ℝ, 1 ≤ y → Real.log y ≤ y ^ δ₀ / δ₀ := by
    intro y hy
    have hyδ : 0 < y ^ δ₀ := Real.rpow_pos_of_pos (by linarith) δ₀
    have h1 := Real.log_le_sub_one_of_pos hyδ
    rw [Real.log_rpow (by linarith)] at h1
    have h2 : δ₀ * Real.log y ≤ y ^ δ₀ := by linarith
    exact (le_div_iff₀ hδ_pos).2 (by linarith)
  set C_mid_const : ℝ :=
    (1 / (2 * Real.pi)) * (4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * (2 * σ₀⁻¹ + 2 * δ₀⁻¹))
  set C_tail_const : ℝ :=
    (1 / (2 * Real.pi)) * (2 * Cζ * (2 : ℝ) ^ δ₀ * (2 * (2 : ℝ) ^ (σ₀ + 1) + 3) / (1 - δ₀))
  set C_final : ℝ := 3 + C_mid_const + C_tail_const
  have h1_sub_δ : 0 < 1 - δ₀ := by linarith
  have hC_mid_nn : 0 ≤ C_mid_const := by dsimp [C_mid_const]; positivity
  have hC_tail_nn : 0 ≤ C_tail_const := by
    dsimp [C_tail_const]
    exact mul_nonneg (by positivity) (div_nonneg (by positivity) h1_sub_δ.le)
  have hC_final_pos : 0 < C_final := by dsimp [C_final]; linarith
  refine ⟨C_final, hC_final_pos, fun X hX => ?_⟩
  set H : ℝ := Real.sqrt X
  have hH_ge1 : 1 ≤ H := Real.one_le_sqrt.mpr hX
  have hH_pos : 0 < H := by linarith
  have hXH_le : X + H ≤ 2 * X := by
    have hsqrt_le : H ≤ X := by
      calc H = Real.sqrt X := rfl
        _ ≤ Real.sqrt (X * X) := Real.sqrt_le_sqrt (le_mul_of_one_le_right (by linarith) hX)
        _ = X := Real.sqrt_mul_self (by linarith)
    linarith
  have hXH_pos : 0 < X + H := by linarith
  have hXH_ge1 : 1 ≤ X + H := by linarith
  have h_diff := tsum_moebius_mul_cutoffPhi_sub_mertens_norm_le hX hH_pos
  have h_inv2 := sum_moebius_cutoffPhi_eq_mellinInv_two hX hH_pos
  have h_shift := mellin_cutoffPhi_two_eq_sigma h_rh hX hH_pos hσ₀_lo hσ₀_hi
  set S_shifted : ℂ :=
    ∫ y : ℝ, zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)
  have h_mert_bd :
      |(mertens X : ℝ)| ≤ (H + 1) + (1 / (2 * Real.pi)) * ‖S_shifted‖ := by
    have h_cast_abs : |(mertens X : ℝ)| = ‖(mertens X : ℂ)‖ := by
      simp [Complex.norm_intCast]
    rw [h_cast_abs]
    have h_tri : ‖(mertens X : ℂ)‖ ≤
        ‖(mertens X : ℂ) -
          ∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ +
        ‖∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ := by
      calc ‖(mertens X : ℂ)‖
          = ‖((mertens X : ℂ) -
              ∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) +
              ∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ := by ring_nf
        _ ≤ _ := norm_add_le _ _
    have h_diff' :
        ‖(mertens X : ℂ) -
          ∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ ≤
          H + 1 := by
      simpa [norm_sub_rev] using h_diff
    have h_sum_norm :
        ‖∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ =
          (1 / (2 * Real.pi)) * ‖S_shifted‖ := by
      rw [h_inv2, h_shift, norm_mul, Complex.norm_real, Real.norm_eq_abs,
        abs_of_pos (by positivity)]
    linarith
  -- Bound ‖S_shifted‖ ≤ ∫ y, ‖G (σ₀ + y * I)‖ via middle |y| ≤ H and tails |y| > H
  let K : ℝ := 2 * (X + H) ^ (σ₀ + 1) / H + 3
  let M_mid : ℝ := 4 * Cζ * (X + H) ^ σ₀ * (1 + H) ^ δ₀
  let M_tail : ℝ := Cζ * K * (2 : ℝ) ^ δ₀
  let dom_rec : ℝ → ℝ := fun y => if |y| < 1 then σ₀⁻¹ else |y|⁻¹
  let B : ℝ → ℝ := fun y =>
    Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y +
    Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y +
    Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y)
  have h_dom_intOn : MeasureTheory.IntegrableOn dom_rec (Set.Icc (-H) H) := by
    have h_dom_meas : Measurable dom_rec :=
      Measurable.ite (measurableSet_lt continuous_abs.measurable measurable_const)
        measurable_const continuous_abs.measurable.inv
    have h_mem_bd : ∀ y : ℝ, ‖dom_rec y‖ ≤ σ₀⁻¹ := by
      intro y
      have hdr : 0 ≤ dom_rec y := by
        dsimp [dom_rec]; split_ifs <;> positivity
      have hdr_le : dom_rec y ≤ σ₀⁻¹ := by
        dsimp [dom_rec]
        split_ifs with hy
        · exact le_rfl
        · have hy1 : 1 ≤ |y| := le_of_not_gt hy
          exact (inv_le_inv₀ (by linarith [hσ₀_le1]) (by linarith)).mpr (by linarith [hσ₀_le1])
      rwa [Real.norm_of_nonneg hdr]
    exact MeasureTheory.IntegrableOn.of_bound measure_Icc_lt_top
      h_dom_meas.aestronglyMeasurable σ₀⁻¹
      (Filter.Eventually.of_forall h_mem_bd)
  have hB1_int : MeasureTheory.Integrable
      (Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y)) :=
    (MeasureTheory.integrable_indicator_iff measurableSet_Icc).mpr
      (h_dom_intOn.const_mul M_mid)
  have hB2_int : MeasureTheory.Integrable
      (Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2))) :=
    (MeasureTheory.integrable_indicator_iff measurableSet_Ioi).mpr
      (MeasureTheory.Integrable.const_mul
        (integrableOn_Ioi_rpow_of_lt (by linarith : δ₀ - 2 < -1) hH_pos) M_tail)
  have hB3_int : MeasureTheory.Integrable
      (fun y => Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y)) :=
    hB2_int.comp_neg
  have h_S_norm_le : ‖S_shifted‖ ≤ ∫ y : ℝ, B y := by
    have h_norm_int :
        ‖S_shifted‖ ≤
          ∫ y : ℝ, ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ :=
      MeasureTheory.norm_integral_le_integral_norm _
    have h_ptwise : ∀ y : ℝ,
        ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ ≤ B y := by
      intro y
      have hre : (σ₀ + y * Complex.I).re = σ₀ := by simp
      have him : (σ₀ + y * Complex.I).im = y := by simp
      have hz := hCζ (σ₀ + y * Complex.I) (by simp)
      rw [him] at hz
      have hK_nn : 0 ≤ K := by dsimp [K]; positivity
      have hM_tail_nn : 0 ≤ M_tail := by dsimp [M_tail]; positivity
      have hb_nn1 : 0 ≤ Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y := by
        by_cases h : y ∈ Set.Icc (-H) H
        · rw [Set.indicator_of_mem h]
          dsimp [dom_rec]; split_ifs <;> positivity
        · simp [h]
      have hb_nn2 : 0 ≤ Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y := by
        by_cases h : H < y
        · have hy_nn : 0 ≤ y := by linarith
          have : 0 ≤ M_tail * y ^ (δ₀ - 2) := mul_nonneg hM_tail_nn (by positivity)
          simpa [h] using this
        · simp [h]
      have hb_nn3 : 0 ≤ Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y) := by
        by_cases h : H < -y
        · have hny_nn : 0 ≤ -y := by linarith
          have : 0 ≤ M_tail * (-y) ^ (δ₀ - 2) := mul_nonneg hM_tail_nn (by positivity)
          simpa [h] using this
        · simp [h]
      by_cases hyH : |y| ≤ H
      · have h_mem : y ∈ Set.Icc (-H) H := abs_le.mp hyH
        have hm := norm_mellin_cutoffPhi_le_div_norm hX hH_pos
          (s := σ₀ + y * Complex.I) (by simp; linarith)
        rw [hre] at hm
        have h1y : (1 + |y|) ^ δ₀ ≤ (1 + H) ^ δ₀ :=
          Real.rpow_le_rpow (by positivity) (by linarith) hδ_pos.le
        have h_inv_s : (‖σ₀ + y * Complex.I‖)⁻¹ ≤ dom_rec y := by
          have hs_re_le : σ₀ ≤ ‖σ₀ + y * Complex.I‖ := by
            simpa [hre] using Complex.re_le_norm (σ₀ + y * Complex.I)
          have hs_norm_pos : 0 < ‖σ₀ + y * Complex.I‖ := by linarith
          have hs_im_le : |y| ≤ ‖σ₀ + y * Complex.I‖ := by
            simpa [him] using Complex.abs_im_le_norm (σ₀ + y * Complex.I)
          dsimp [dom_rec]
          split_ifs with hy1
          · exact (inv_le_inv₀ hs_norm_pos (by linarith)).mpr hs_re_le
          · have hy1' : 1 ≤ |y| := le_of_not_gt hy1
            exact (inv_le_inv₀ hs_norm_pos (by linarith)).mpr hs_im_le
        have h_mid :
            ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ ≤
              M_mid * dom_rec y := by
          rw [norm_mul]
          calc ‖zetaInv (σ₀ + y * Complex.I)‖ * ‖mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖
              ≤ (Cζ * (1 + |y|) ^ δ₀) * (4 * (X + H) ^ σ₀ / ‖σ₀ + y * Complex.I‖) :=
                mul_le_mul hz hm (norm_nonneg _) (by positivity)
            _ ≤ (Cζ * (1 + H) ^ δ₀) * (4 * (X + H) ^ σ₀ * dom_rec y) := by
                refine mul_le_mul (mul_le_mul_of_nonneg_left h1y hCζ_pos.le)
                  ?_ (by positivity) (by positivity)
                rw [div_eq_mul_inv]
                exact mul_le_mul_of_nonneg_left h_inv_s (by positivity)
            _ = M_mid * dom_rec y := by dsimp [M_mid]; ring
        have hB_mem : Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y =
            M_mid * dom_rec y :=
          Set.indicator_of_mem h_mem _
        dsimp [B]
        linarith
      · have hy_gt : H < |y| := lt_of_not_ge hyH
        have hm := norm_mellin_cutoffPhi_le_div_sq hX hH_pos
          (s := σ₀ + y * Complex.I) (by simp; linarith)
        rw [hre, him] at hm
        rcases le_or_gt 0 y with hy0 | hy0
        · have hy_pos_H : H < y := by rwa [abs_of_nonneg hy0] at hy_gt
          have h1y_le : 1 + |y| ≤ 2 * y := by rw [abs_of_nonneg hy0]; linarith
          have hnum : (1 + |y|) ^ δ₀ ≤ (2 : ℝ) ^ δ₀ * y ^ δ₀ := by
            calc (1 + |y|) ^ δ₀ ≤ (2 * y) ^ δ₀ := Real.rpow_le_rpow (by positivity) h1y_le hδ_pos.le
              _ = (2 : ℝ) ^ δ₀ * y ^ δ₀ := Real.mul_rpow (by norm_num) (by linarith)
          have hden : y ^ 2 ≤ σ₀ ^ 2 + y ^ 2 := le_add_of_nonneg_left (sq_nonneg _)
          have hrpow_div : y ^ δ₀ / y ^ 2 = y ^ (δ₀ - 2) := by
            rw [← Real.rpow_two y, ← Real.rpow_sub (by linarith)]
          have h_bd : ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ ≤
              M_tail * y ^ (δ₀ - 2) := by
            rw [norm_mul]
            calc ‖zetaInv (σ₀ + y * Complex.I)‖ * ‖mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖
                ≤ (Cζ * (1 + |y|) ^ δ₀) * (K / (σ₀ ^ 2 + y ^ 2)) :=
                  mul_le_mul hz hm (norm_nonneg _) (by positivity)
              _ ≤ (Cζ * ((2 : ℝ) ^ δ₀ * y ^ δ₀)) * (K / y ^ 2) := by
                  refine mul_le_mul (mul_le_mul_of_nonneg_left hnum hCζ_pos.le)
                    (div_le_div_of_nonneg_left hK_nn (sq_pos_of_pos (by linarith : 0 < y)) hden)
                    (div_nonneg hK_nn (by positivity)) (by positivity)
              _ = M_tail * (y ^ δ₀ / y ^ 2) := by dsimp [M_tail]; ring
              _ = M_tail * y ^ (δ₀ - 2) := by rw [hrpow_div]
          have hB_mem : Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y =
              M_tail * y ^ (δ₀ - 2) :=
            Set.indicator_of_mem hy_pos_H _
          dsimp [B]
          linarith
        · have hy_neg_H : H < -y := by rwa [abs_of_neg hy0] at hy_gt
          have hny_pos : 0 < -y := by linarith
          have h1y_le : 1 + |y| ≤ 2 * (-y) := by rw [abs_of_neg hy0]; linarith
          have hnum : (1 + |y|) ^ δ₀ ≤ (2 : ℝ) ^ δ₀ * (-y) ^ δ₀ := by
            calc (1 + |y|) ^ δ₀ ≤ (2 * (-y)) ^ δ₀ :=
                  Real.rpow_le_rpow (by positivity) h1y_le hδ_pos.le
              _ = (2 : ℝ) ^ δ₀ * (-y) ^ δ₀ := Real.mul_rpow (by norm_num) (by linarith)
          have hden : (-y) ^ 2 ≤ σ₀ ^ 2 + y ^ 2 := by
            rw [neg_sq]; exact le_add_of_nonneg_left (sq_nonneg _)
          have hrpow_div : (-y) ^ δ₀ / (-y) ^ 2 = (-y) ^ (δ₀ - 2) := by
            rw [← Real.rpow_two (-y), ← Real.rpow_sub (by linarith)]
          have h_bd : ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ ≤
              M_tail * (-y) ^ (δ₀ - 2) := by
            rw [norm_mul]
            calc ‖zetaInv (σ₀ + y * Complex.I)‖ * ‖mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖
                ≤ (Cζ * (1 + |y|) ^ δ₀) * (K / (σ₀ ^ 2 + y ^ 2)) :=
                  mul_le_mul hz hm (norm_nonneg _) (by positivity)
              _ ≤ (Cζ * ((2 : ℝ) ^ δ₀ * (-y) ^ δ₀)) * (K / (-y) ^ 2) := by
                  refine mul_le_mul (mul_le_mul_of_nonneg_left hnum hCζ_pos.le)
                    (div_le_div_of_nonneg_left hK_nn (sq_pos_of_pos hny_pos) hden)
                    (div_nonneg hK_nn (by positivity)) (by positivity)
              _ = M_tail * ((-y) ^ δ₀ / (-y) ^ 2) := by dsimp [M_tail]; ring
              _ = M_tail * (-y) ^ (δ₀ - 2) := by rw [hrpow_div]
          have hB_mem : Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y) =
              M_tail * (-y) ^ (δ₀ - 2) :=
            Set.indicator_of_mem hy_neg_H _
          dsimp [B]
          linarith
    have hG_int_norm : MeasureTheory.Integrable
        (fun y : ℝ =>
          ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖) := by
      have hG_cont : Continuous
          (fun y : ℝ =>
          ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖) := by
        refine Continuous.norm (Continuous.mul ?_ ?_)
        · have hc : Continuous (fun y : ℝ => (σ₀ : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
          exact (differentiableOn_zetaInv_of_rh h_rh).continuousOn.comp_continuous
            hc fun y => by simp; linarith
        · have hc : Continuous (fun y : ℝ => (σ₀ : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
          exact (differentiableOn_mellin_cutoffPhi hX hH_pos).continuousOn.comp_continuous
            hc fun y => by simp; linarith
      refine (hB1_int.add hB2_int |>.add hB3_int).mono' hG_cont.aestronglyMeasurable
        (Filter.Eventually.of_forall fun y => ?_)
      rw [Real.norm_of_nonneg (norm_nonneg _)]
      exact h_ptwise y
    have h_int_mono := MeasureTheory.integral_mono hG_int_norm
      ((hB1_int.add hB2_int).add hB3_int) h_ptwise
    exact h_norm_int.trans h_int_mono
  -- Evaluate the three pieces of ∫ B y
  have hB1_eval :
      ∫ y : ℝ, Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y ≤
        M_mid * (2 * σ₀⁻¹ + 2 * Real.log H) := by
    rw [MeasureTheory.integral_indicator measurableSet_Icc,
      MeasureTheory.setIntegral_congr_set MeasureTheory.Ioc_ae_eq_Icc.symm,
      ← intervalIntegral.integral_of_le (by linarith : -H ≤ H),
      intervalIntegral.integral_const_mul]
    refine mul_le_mul_of_nonneg_left ?_ (by positivity)
    have hI_neg : IntervalIntegrable dom_rec MeasureTheory.volume (-H) (-1) :=
      (intervalIntegrable_iff_integrableOn_Ioc_of_le (by linarith)).mpr
        (h_dom_intOn.mono_set (Set.Ioc_subset_Icc_self.trans
          (Set.Icc_subset_Icc le_rfl (by linarith))))
    have hI_mid : IntervalIntegrable dom_rec MeasureTheory.volume (-1) 1 :=
      (intervalIntegrable_iff_integrableOn_Ioc_of_le (by norm_num)).mpr
        (h_dom_intOn.mono_set (Set.Ioc_subset_Icc_self.trans
          (Set.Icc_subset_Icc (by linarith) hH_ge1)))
    have hI_pos : IntervalIntegrable dom_rec MeasureTheory.volume 1 H :=
      (intervalIntegrable_iff_integrableOn_Ioc_of_le hH_ge1).mpr
        (h_dom_intOn.mono_set (Set.Ioc_subset_Icc_self.trans
          (Set.Icc_subset_Icc (by linarith) le_rfl)))
    have h_split :
        (∫ y : ℝ in (-H)..H, dom_rec y) =
          (∫ y : ℝ in (-H)..(-1), dom_rec y) + (∫ y : ℝ in (-1)..1, dom_rec y) +
            (∫ y : ℝ in 1..H, dom_rec y) := by
      have h12 : (∫ y : ℝ in (-H)..1, dom_rec y) =
          (∫ y : ℝ in (-H)..(-1), dom_rec y) + (∫ y : ℝ in (-1)..1, dom_rec y) :=
        (intervalIntegral.integral_add_adjacent_intervals hI_neg hI_mid).symm
      rw [← intervalIntegral.integral_add_adjacent_intervals (hI_neg.trans hI_mid) hI_pos, h12]
    have h_neg_val : (∫ y : ℝ in (-H)..(-1), dom_rec y) = Real.log H := by
      have h_eq : Set.EqOn dom_rec (fun y : ℝ => -(y⁻¹)) (Set.uIcc (-H) (-1)) := by
        intro y hy
        rw [Set.uIcc_of_le (by linarith : -H ≤ -1)] at hy
        have hy_neg : y < 0 := by linarith [hy.2]
        dsimp [dom_rec]
        split_ifs with h
        · exfalso; rw [abs_of_neg hy_neg] at h; linarith [hy.2]
        · simp [abs_of_neg hy_neg]
      rw [intervalIntegral.integral_congr h_eq, intervalIntegral.integral_neg,
        integral_inv_of_neg (by linarith) (by norm_num)]
      have hdiv : (-1 : ℝ) / (-H) = H⁻¹ := by field_simp
      rw [hdiv, Real.log_inv, neg_neg]
    have h_mid_val : (∫ y : ℝ in (-1)..1, dom_rec y) ≤ 2 * σ₀⁻¹ := by
      have h_le : ∀ y ∈ Set.Icc (-1 : ℝ) 1, dom_rec y ≤ σ₀⁻¹ := by
        intro y _
        dsimp [dom_rec]
        split_ifs with hy
        · exact le_rfl
        · exact (inv_le_inv₀ (by linarith [hσ₀_le1]) (by linarith [le_of_not_gt hy])).mpr
            (by linarith [le_of_not_gt hy, hσ₀_le1])
      calc (∫ y : ℝ in (-1)..1, dom_rec y)
          ≤ ∫ _y : ℝ in (-1 : ℝ)..1, σ₀⁻¹ :=
            intervalIntegral.integral_mono_on (by norm_num) hI_mid intervalIntegrable_const h_le
        _ = 2 * σ₀⁻¹ := by
            rw [intervalIntegral.integral_const, smul_eq_mul]; ring
    have h_pos_val : (∫ y : ℝ in 1..H, dom_rec y) = Real.log H := by
      have h_eq : Set.EqOn dom_rec (fun y : ℝ => y⁻¹) (Set.uIcc 1 H) := by
        intro y hy
        rw [Set.uIcc_of_le hH_ge1] at hy
        have hy_pos : 0 < y := by linarith [hy.1]
        dsimp [dom_rec]
        split_ifs with h
        · exfalso; rw [abs_of_pos hy_pos] at h; linarith [hy.1]
        · rw [abs_of_pos hy_pos]
      rw [intervalIntegral.integral_congr h_eq, integral_inv_of_pos zero_lt_one hH_pos, div_one]
    linarith [h_split, h_neg_val, h_mid_val, h_pos_val]
  have hB2_eval :
      ∫ y : ℝ, Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y =
        M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)) := by
    rw [MeasureTheory.integral_indicator measurableSet_Ioi,
      MeasureTheory.integral_const_mul,
      setIntegral_Ioi_rpow_of_lt hH_pos (by linarith)]
    ring_nf
  have hB3_eval :
      (∫ y : ℝ, Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y)) =
        M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)) := by
    rw [MeasureTheory.integral_neg_eq_self
      (fun y => Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) y)]
    exact hB2_eval
  have hB_sum_eval : ∫ y : ℝ, B y =
      (∫ y : ℝ, Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y) +
      (∫ y : ℝ, Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y) +
      (∫ y : ℝ, Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y)) := by
    dsimp [B]
    have hB12_int : MeasureTheory.Integrable
        (fun y : ℝ => Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y +
          Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y) :=
      hB1_int.add hB2_int
    rw [MeasureTheory.integral_add hB12_int hB3_int,
      MeasureTheory.integral_add hB1_int hB2_int]
  have h_inv_norm : (1 / (2 * Real.pi)) * ‖S_shifted‖ ≤
      (C_mid_const + C_tail_const) * X ^ ((1 / 2 : ℝ) + ε) := by
    have hX_pos : 0 < X := by linarith
    have hH_rpow : H = X ^ ((1 / 2 : ℝ)) := by simp [H, Real.sqrt_eq_rpow]
    have hHδ_rpow : H ^ δ₀ = X ^ (δ₀ / 2) := by
      rw [hH_rpow, ← Real.rpow_mul hX_pos.le]; ring_nf
    have h_mid_bd :
        (1 / (2 * Real.pi)) * (M_mid * (2 * σ₀⁻¹ + 2 * Real.log H)) ≤
          C_mid_const * X ^ ((1 / 2 : ℝ) + ε) := by
      have h1H_le : 1 + H ≤ 2 * H := by linarith
      have h1H_pow : (1 + H) ^ δ₀ ≤ (2 : ℝ) ^ δ₀ * X ^ (δ₀ / 2) := by
        calc (1 + H) ^ δ₀ ≤ (2 * H) ^ δ₀ := Real.rpow_le_rpow (by positivity) h1H_le hδ_pos.le
          _ = (2 : ℝ) ^ δ₀ * H ^ δ₀ := Real.mul_rpow (by norm_num) hH_pos.le
          _ = (2 : ℝ) ^ δ₀ * X ^ (δ₀ / 2) := by rw [hHδ_rpow]
      have hXH_pow : (X + H) ^ σ₀ ≤ (2 : ℝ) ^ σ₀ * X ^ σ₀ := by
        calc (X + H) ^ σ₀ ≤ (2 * X) ^ σ₀ := Real.rpow_le_rpow (by positivity) hXH_le (by linarith)
          _ = (2 : ℝ) ^ σ₀ * X ^ σ₀ := Real.mul_rpow (by norm_num) hX_pos.le
      have hM_mid_bd : M_mid ≤ 4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * X ^ (σ₀ + δ₀ / 2) := by
        have hx_mul : X ^ σ₀ * X ^ (δ₀ / 2) = X ^ (σ₀ + δ₀ / 2) :=
          (Real.rpow_add hX_pos _ _).symm
        calc M_mid = 4 * Cζ * (X + H) ^ σ₀ * (1 + H) ^ δ₀ := rfl
          _ ≤ 4 * Cζ * ((2 : ℝ) ^ σ₀ * X ^ σ₀) * ((2 : ℝ) ^ δ₀ * X ^ (δ₀ / 2)) := by
              refine mul_le_mul (mul_le_mul_of_nonneg_left hXH_pow (by positivity)) h1H_pow
                (by positivity) (by positivity)
          _ = 4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * (X ^ σ₀ * X ^ (δ₀ / 2)) := by ring
          _ = 4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * X ^ (σ₀ + δ₀ / 2) := by rw [hx_mul]
      have hlog_H : 2 * σ₀⁻¹ + 2 * Real.log H ≤ (2 * σ₀⁻¹ + 2 * δ₀⁻¹) * X ^ (δ₀ / 2) := by
        have hHδ_ge1 : 1 ≤ H ^ δ₀ := Real.one_le_rpow hH_ge1 hδ_pos.le
        have hl := hlog_bd H hH_ge1
        rw [hHδ_rpow] at hl hHδ_ge1
        have h_term1 : 2 * σ₀⁻¹ ≤ 2 * σ₀⁻¹ * X ^ (δ₀ / 2) :=
          le_mul_of_one_le_right (by positivity) hHδ_ge1
        calc 2 * σ₀⁻¹ + 2 * Real.log H
            ≤ 2 * σ₀⁻¹ * X ^ (δ₀ / 2) + 2 * (X ^ (δ₀ / 2) / δ₀) := by linarith
          _ = (2 * σ₀⁻¹ + 2 * δ₀⁻¹) * X ^ (δ₀ / 2) := by ring
      have hx_exp : X ^ (σ₀ + δ₀ / 2) * X ^ (δ₀ / 2) = X ^ (σ₀ + δ₀) := by
        rw [← Real.rpow_add hX_pos]; ring_nf
      have hx_le : X ^ (σ₀ + δ₀) ≤ X ^ ((1 / 2 : ℝ) + ε) :=
        Real.rpow_le_rpow_of_exponent_le hX (by dsimp [σ₀]; linarith)
      have hlogH_nn : 0 ≤ Real.log H := Real.log_nonneg hH_ge1
      calc (1 / (2 * Real.pi)) * (M_mid * (2 * σ₀⁻¹ + 2 * Real.log H))
          ≤ (1 / (2 * Real.pi)) * ((4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * X ^ (σ₀ + δ₀ / 2)) *
              ((2 * σ₀⁻¹ + 2 * δ₀⁻¹) * X ^ (δ₀ / 2))) := by
              refine mul_le_mul_of_nonneg_left
                (mul_le_mul hM_mid_bd hlog_H (by positivity) (by positivity))
                (by positivity)
        _ = C_mid_const * (X ^ (σ₀ + δ₀ / 2) * X ^ (δ₀ / 2)) := by
              dsimp [C_mid_const]; ring
        _ = C_mid_const * X ^ (σ₀ + δ₀) := by rw [hx_exp]
        _ ≤ C_mid_const * X ^ ((1 / 2 : ℝ) + ε) :=
              mul_le_mul_of_nonneg_left hx_le hC_mid_nn
    have h_tail_bd :
        (1 / (2 * Real.pi)) * (2 * (M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)))) ≤
          C_tail_const * X ^ ((1 / 2 : ℝ) + ε) := by
      have hXH_pow1 : (X + H) ^ (σ₀ + 1) ≤ (2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1) := by
        calc (X + H) ^ (σ₀ + 1) ≤ (2 * X) ^ (σ₀ + 1) :=
              Real.rpow_le_rpow (by positivity) hXH_le (by positivity)
          _ = (2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1) := Real.mul_rpow (by norm_num) hX_pos.le
      have hX_div : X ^ (σ₀ + 1) / H = X ^ (σ₀ + 1 / 2) := by
        rw [hH_rpow, ← Real.rpow_sub hX_pos]; ring_nf
      have hX_ge1' : 1 ≤ X ^ (σ₀ + 1 / 2) := Real.one_le_rpow hX (by positivity)
      have hK_bd : K ≤ (2 * (2 : ℝ) ^ (σ₀ + 1) + 3) * X ^ (σ₀ + 1 / 2) := by
        calc K = 2 * (X + H) ^ (σ₀ + 1) / H + 3 := rfl
          _ ≤ 2 * ((2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1)) / H + 3 := by gcongr
          _ = 2 * (2 : ℝ) ^ (σ₀ + 1) * (X ^ (σ₀ + 1) / H) + 3 := by ring
          _ = 2 * (2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1 / 2) + 3 := by rw [hX_div]
          _ ≤ 2 * (2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1 / 2) + 3 * X ^ (σ₀ + 1 / 2) := by linarith
          _ = (2 * (2 : ℝ) ^ (σ₀ + 1) + 3) * X ^ (σ₀ + 1 / 2) := by ring
      have hH_tail_pow : H ^ (δ₀ - 1) = X ^ ((δ₀ - 1) / 2) := by
        rw [hH_rpow, ← Real.rpow_mul hX_pos.le]; ring_nf
      have hx_tail_exp : X ^ (σ₀ + 1 / 2) * X ^ ((δ₀ - 1) / 2) = X ^ (σ₀ + δ₀ / 2) := by
        rw [← Real.rpow_add hX_pos]; ring_nf
      have hx_tail_le : X ^ (σ₀ + δ₀ / 2) ≤ X ^ ((1 / 2 : ℝ) + ε) :=
        Real.rpow_le_rpow_of_exponent_le hX (by dsimp [σ₀]; linarith)
      calc (1 / (2 * Real.pi)) * (2 * (M_tail * (H ^ (δ₀ - 1) / (1 - δ₀))))
          = (1 / (2 * Real.pi)) * (2 * Cζ * (2 : ℝ) ^ δ₀ * K * H ^ (δ₀ - 1) / (1 - δ₀)) := by
              dsimp [M_tail]; ring
        _ ≤ (1 / (2 * Real.pi)) * (2 * Cζ * (2 : ℝ) ^ δ₀ *
              ((2 * (2 : ℝ) ^ (σ₀ + 1) + 3) * X ^ (σ₀ + 1 / 2)) *
                X ^ ((δ₀ - 1) / 2) / (1 - δ₀)) := by
              rw [hH_tail_pow]
              refine mul_le_mul_of_nonneg_left
                (div_le_div_of_nonneg_right
                  (mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hK_bd (by positivity))
                    (by positivity))
                  h1_sub_δ.le)
                (by positivity)
        _ = C_tail_const * (X ^ (σ₀ + 1 / 2) * X ^ ((δ₀ - 1) / 2)) := by
              dsimp [C_tail_const]; ring
        _ = C_tail_const * X ^ (σ₀ + δ₀ / 2) := by rw [hx_tail_exp]
        _ ≤ C_tail_const * X ^ ((1 / 2 : ℝ) + ε) :=
              mul_le_mul_of_nonneg_left hx_tail_le hC_tail_nn
    calc (1 / (2 * Real.pi)) * ‖S_shifted‖
        ≤ (1 / (2 * Real.pi)) * ∫ y : ℝ, B y :=
          mul_le_mul_of_nonneg_left h_S_norm_le (by positivity)
      _ ≤ (1 / (2 * Real.pi)) * (M_mid * (2 * σ₀⁻¹ + 2 * Real.log H) +
            2 * (M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)))) := by
          refine mul_le_mul_of_nonneg_left ?_ (by positivity)
          linarith [hB_sum_eval, hB1_eval, hB2_eval, hB3_eval]
      _ = (1 / (2 * Real.pi)) * (M_mid * (2 * σ₀⁻¹ + 2 * Real.log H)) +
            (1 / (2 * Real.pi)) * (2 * (M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)))) := by ring
      _ ≤ C_mid_const * X ^ ((1 / 2 : ℝ) + ε) + C_tail_const * X ^ ((1 / 2 : ℝ) + ε) :=
          add_le_add h_mid_bd h_tail_bd
      _ = (C_mid_const + C_tail_const) * X ^ ((1 / 2 : ℝ) + ε) := by ring
  have hH1_le : H + 1 ≤ 3 * X ^ ((1 / 2 : ℝ) + ε) := by
    have hH_le_rpow : H ≤ X ^ ((1 / 2 : ℝ) + ε) := by
      have hH_rpow : H = X ^ ((1 / 2 : ℝ)) := by simp [H, Real.sqrt_eq_rpow]
      rw [hH_rpow]
      exact Real.rpow_le_rpow_of_exponent_le hX (by linarith)
    have h1_le_rpow : 1 ≤ X ^ ((1 / 2 : ℝ) + ε) := Real.one_le_rpow hX (by linarith)
    linarith
  calc |(mertens X : ℝ)|
      ≤ (H + 1) + (1 / (2 * Real.pi)) * ‖S_shifted‖ := h_mert_bd
    _ ≤ 3 * X ^ ((1 / 2 : ℝ) + ε) + (C_mid_const + C_tail_const) * X ^ ((1 / 2 : ℝ) + ε) :=
        add_le_add hH1_le h_inv_norm
    _ = C_final * X ^ ((1 / 2 : ℝ) + ε) := by dsimp [C_final]; ring



/-- Mathlib-idiomatic `=O[atTop]` asymptotic formulation of Littlewood's (1912) converse:
`RiemannHypothesis` implies `(fun x => (mertens x : ℝ)) =O[atTop] (fun x => x ^ (1/2 + ε))`
for every `ε > 0`. -/
theorem isBigO_mertens_of_riemannHypothesis (hRH : _root_.RiemannHypothesis) (ε : ℝ) (hε : 0 < ε) :
    (fun x : ℝ => (mertens x : ℝ)) =O[Filter.atTop]
      fun x => x ^ ((1 / 2 : ℝ) + ε) := by
  have hM := rh_implies_mertens_bound hRH
  obtain ⟨C, _hC_pos, hC_bd⟩ := hM ε hε
  refine Asymptotics.IsBigO.of_bound C ?_
  filter_upwards [Filter.eventually_ge_atTop (1 : ℝ)] with x hx
  have hx_pos : 0 < x := zero_lt_one.trans_le hx
  have hrpow_nn : 0 ≤ x ^ ((1 / 2 : ℝ) + ε) := Real.rpow_nonneg hx_pos.le _
  rw [Real.norm_of_nonneg hrpow_nn, Real.norm_eq_abs]
  exact hC_bd x hx

/-- Littlewood's (1912) Bidirectional Equivalence formulated via Mathlib's `=O[atTop]` filter:
`RiemannHypothesis` holds if and only if `M(x) = O(x^(1/2 + ε))` as `x → ∞` for every `ε > 0`. -/
theorem riemannHypothesis_iff_mertens_isBigO :
    _root_.RiemannHypothesis ↔
      ∀ ε : ℝ, 0 < ε →
        (fun x : ℝ => (mertens x : ℝ)) =O[Filter.atTop]
          fun x => x ^ ((1 / 2 : ℝ) + ε) :=
  ⟨fun hRH ε hε => isBigO_mertens_of_riemannHypothesis hRH ε hε,
   fun hO => RiemannHypothesis.of_mertens_isBigO hO⟩


/-! ### Stage 6: Titchmarsh §14.25(A) Möbius Dirichlet Series Convergence & Equivalence -/

private lemma isOpen_re_gt (r : ℝ) : IsOpen {s : ℂ | r < s.re} :=
  isOpen_lt continuous_const Complex.continuous_re

private noncomputable def moebC : ℕ → ℂ := fun n => (ArithmeticFunction.moebius n : ℂ)

private lemma mertens_nat_cast (n : ℕ) :
    (mertens (n : ℝ) : ℂ) = ∑ k ∈ Finset.Icc 0 n, moebC k := by
  dsimp [mertens, moebC]
  rw [Nat.floor_natCast]
  push_cast
  exact rfl

private lemma cpow_neg_mul_eq_div (s : ℂ) {k : ℕ} (hk : 1 ≤ k) (c : ℂ) :
    (k : ℂ) ^ (-s) * c = c / (k : ℂ) ^ s := by
  have hk0 : (k : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  rw [cpow_neg, inv_mul_eq_div]

private lemma sum_Icc_zero_moebC_mul {N : ℕ} (hN : 1 ≤ N) (g : ℕ → ℂ) :
    ∑ k ∈ Finset.Icc 0 N, g k * moebC k = ∑ k ∈ Finset.Icc 1 N, g k * moebC k := by
  have h_split : Finset.Icc 0 N = insert 0 (Finset.Icc 1 N) := by
    ext x
    simp only [Finset.mem_Icc, Finset.mem_insert]
    omega
  rw [h_split, Finset.sum_insert (by simp)]
  have h0 : moebC 0 = 0 := by simp [moebC]
  rw [h0, mul_zero, zero_add]

private lemma integral_deriv_eq_mellinMertens (s : ℂ) (hs : 1 / 2 < s.re) :
    -(∫ (t : ℝ) in Ioi 1, (deriv (fun x : ℝ => (x : ℂ) ^ (-s)) t) *
        ∑ k ∈ Finset.Icc 0 ⌊t⌋₊, moebC k) = mellinMertens s := by
  have hs_pos : 0 < s.re := by linarith
  have hs_ne0 : s ≠ 0 := ne_zero_of_re_pos hs_pos
  have h_deriv : ∀ᵐ (t : ℝ) ∂(volume.restrict (Ioi 1)),
      (deriv (fun x : ℝ => (x : ℂ) ^ (-s)) t) * ∑ k ∈ Finset.Icc 0 ⌊t⌋₊, moebC k =
        - (s * ((mertens t : ℂ) * (t : ℂ) ^ (-(s + 1)))) := by
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
    have ht_pos : (0 : ℝ) < t := zero_lt_one.trans ht
    have hd := deriv_ofReal_cpow_const ht_pos.ne' (neg_ne_zero.mpr hs_ne0)
    have hm : ∑ k ∈ Finset.Icc 0 ⌊t⌋₊, moebC k = (mertens t : ℂ) := by
      dsimp [mertens, moebC]
      push_cast
      exact rfl
    rw [hd, hm]
    have hexp : -s - 1 = -(s + 1) := by ring
    rw [hexp]
    ring
  rw [integral_congr_ae h_deriv, integral_neg, neg_neg]
  rw [integral_const_mul]
  rfl

/-- Value of mellinMertens 1 = 0 derived from the simple pole residue (s - 1) * ζ(s) → 1. -/
lemma mellinMertens_one_eq_zero
    (hM : ∀ ε : ℝ, 0 < ε →
      (fun x : ℝ => (mertens x : ℝ)) =O[atTop] fun x => x ^ ((1 / 2 : ℝ) + ε)) :
    mellinMertens 1 = 0 := by
  have h_cont : ContinuousAt mellinMertens 1 :=
    (mellinMertens_differentiableAt_of_isBigO hM (s := 1) (by norm_num)).continuousAt
  have h_res := riemannZeta_residue_one
  have h_prod : Tendsto (fun s => (s - 1) * riemannZeta s * mellinMertens s) (𝓝[≠] 1)
      (𝓝 (1 * mellinMertens 1)) :=
    h_res.mul (h_cont.tendsto.mono_left nhdsWithin_le_nhds)
  have h_ev : ∀ᶠ s in 𝓝[≠] 1, (s - 1) * riemannZeta s * mellinMertens s = s - 1 := by
    have h_nhds : {s : ℂ | 1 / 2 < s.re} ∈ 𝓝[≠] (1 : ℂ) :=
      mem_nhdsWithin_of_mem_nhds
        ((isOpen_re_gt (1 / 2)).mem_nhds (by norm_num : (1 / 2 : ℝ) < (1 : ℂ).re))
    filter_upwards [h_nhds, self_mem_nhdsWithin] with s hs hne
    rw [mul_assoc, riemannZeta_mul_mellinMertens_eq_one_of_isBigO hM s hs hne, mul_one]
  have h_sub_lim : Tendsto (fun s : ℂ => s - 1) (𝓝[≠] 1) (𝓝 0) := by
    have h1 : Tendsto (fun s : ℂ => s - 1) (𝓝 1) (𝓝 (1 - 1)) :=
      (continuous_id.sub continuous_const).tendsto 1
    rw [sub_self] at h1
    exact h1.mono_left nhdsWithin_le_nhds
  have h_prod_lim : Tendsto (fun s => (s - 1) * riemannZeta s * mellinMertens s) (𝓝[≠] 1) (𝓝 0) :=
    (tendsto_congr' h_ev).mpr h_sub_lim
  have h_eq := tendsto_nhds_unique h_prod h_prod_lim
  rw [one_mul] at h_eq
  exact h_eq

/-- Under `RiemannHypothesis`, the reciprocal sum `∑_{k=1}^N μ(k) / k` converges to `0` as
`N → ∞` via Abel summation and the residue value `mellinMertens 1 = 0`. -/
theorem tendsto_sum_moebius_div_self_of_riemannHypothesis (hRH : _root_.RiemannHypothesis) :
    Filter.Tendsto
      (fun N : ℕ => ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ))
      Filter.atTop (nhds 0) := by
  let s : ℂ := 1
  have hs : (1 / 2 : ℝ) < s.re := by norm_num [s]
  let ε : ℝ := (s.re - 1 / 2) / 2
  have hε : 0 < ε := by dsimp [ε, s]; norm_num
  have hr_pos : 0 ≤ (1 / 2 : ℝ) + ε := by dsimp [ε, s]; norm_num
  have hs_pos : 0 < s.re := by norm_num [s]
  have hs_ne0 : s ≠ 0 := by norm_num [s]
  have hO := isBigO_mertens_of_riemannHypothesis hRH ε hε
  have hf_diff : ∀ t ∈ Ici 1, DifferentiableAt ℝ (fun x : ℝ => (x : ℂ) ^ (-s)) t := fun t ht =>
    differentiableAt_id.ofReal_cpow_const (zero_lt_one.trans_le ht).ne' (neg_ne_zero.mpr hs_ne0)
  have hf_int : LocallyIntegrableOn (deriv (fun x : ℝ => (x : ℂ) ^ (-s))) (Ici 1) :=
    (Iff.mpr integrableOn_Ici_iff_integrableOn_Ioi <|
      integrableOn_Ioi_deriv_ofReal_cpow zero_lt_one
        (by simp [Complex.neg_re, s])).locallyIntegrableOn
  have h_sum_O : (fun n : ℕ => ∑ k ∈ Finset.Icc 0 n, moebC k) =O[atTop]
      fun n : ℕ => (n : ℝ) ^ ((1 / 2 : ℝ) + ε) := by
    have h_nat : (fun n : ℕ => (mertens (n : ℝ) : ℝ)) =O[atTop]
        fun n : ℕ => (n : ℝ) ^ ((1 / 2 : ℝ) + ε) :=
      hO.comp_tendsto tendsto_natCast_atTop_atTop
    have h_m_c : (fun n : ℕ => (mertens (n : ℝ) : ℂ)) =O[atTop]
        fun n : ℕ => (n : ℝ) ^ ((1 / 2 : ℝ) + ε) :=
      isBigO_ofReal_left.mpr h_nat
    simpa only [mertens_nat_cast] using h_m_c
  have hlim : Tendsto (fun n : ℕ ↦ (n : ℝ) ^ (-(s.re - ((1 / 2 : ℝ) + ε)))) atTop (𝓝 0) :=
    (tendsto_rpow_neg_atTop (by dsimp [ε, s]; norm_num)).comp tendsto_natCast_atTop_atTop
  have h_lim : Tendsto (fun n : ℕ => (n : ℂ) ^ (-s) * ∑ k ∈ Finset.Icc 0 n, moebC k) atTop (𝓝 0) :=
    (IsBigO.mul_atTop_rpow_natCast_of_isBigO_rpow (-s.re) _ _
      (isBigO_norm_left.mp (norm_ofReal_cpow_eventually_eq_atTop _).isBigO.natCast_atTop)
      h_sum_O (by dsimp [s, ε]; norm_num)).trans_tendsto hlim
  let g : ℝ → ℝ := fun t => t ^ (-(s.re + 1) + ((1 / 2 : ℝ) + ε))
  have h_int : IntegrableAtFilter g atTop := by
    refine integrableAtFilter_rpow_atTop_iff.mpr ?_
    show -(s.re + 1) + (1 / 2 + ε) < -1
    dsimp [ε, s]
    norm_num
  have hg_dom : (fun t => deriv (fun x : ℝ => (x : ℂ) ^ (-s)) t *
      ∑ k ∈ Finset.Icc 0 ⌊t⌋₊, moebC k) =O[atTop] g := by
    refine .mul_atTop_rpow_of_isBigO_rpow (-(s + 1).re) ((1 / 2 : ℝ) + ε) _ ?_ ?_ ?_
    · simpa [-neg_add_rev, neg_add'] using! isBigO_deriv_ofReal_cpow_const_atTop (-s)
    · exact (h_sum_O.comp_tendsto tendsto_nat_floor_atTop).trans <|
        isEquivalent_nat_floor.isBigO.rpow hr_pos (eventually_ge_atTop 0)
    · have : (-s - 1).re = -(s.re + 1) := by rw [sub_re, neg_re, one_re]; ring
      dsimp [g]
      linarith
  have h_abel := tendsto_sum_mul_atTop_nhds_one_sub_integral₀ (c := moebC)
    (f := fun x : ℝ => (x : ℂ) ^ (-s)) (l := 0) (by simp [moebC]) hf_diff hf_int h_lim hg_dom h_int
  have h_int_val : (0 : ℂ) - ∫ (t : ℝ) in Ioi 1, deriv (fun x : ℝ => (x : ℂ) ^ (-s)) t *
      ∑ k ∈ Finset.Icc 0 ⌊t⌋₊, moebC k = mellinMertens s := by
    rw [zero_sub, integral_deriv_eq_mellinMertens s hs]
  rw [h_int_val] at h_abel
  have h_m1 : mellinMertens s = 0 := by
    change mellinMertens 1 = 0
    exact mellinMertens_one_eq_zero (isBigO_mertens_of_riemannHypothesis hRH)
  rw [h_m1] at h_abel
  refine h_abel.congr' ?_
  filter_upwards [eventually_ge_atTop 1] with N hN
  rw [sum_Icc_zero_moebC_mul hN]
  refine Finset.sum_congr rfl fun k hk => ?_
  have hk_pos : 1 ≤ k := (Finset.mem_Icc.mp hk).1
  have hk0 : (k : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  dsimp [moebC, s]
  rw [cpow_neg, cpow_one, inv_mul_eq_div]

/-- Titchmarsh §14.25(A): Under `RiemannHypothesis`, the Möbius Dirichlet series
∑_{n=1}^N μ(n) n^{-s} converges to (riemannZeta s)⁻¹ at every point in the half-plane
1 / 2 < s.re with s ≠ 1. -/
theorem tendsto_sum_moebius_cpow_of_riemannHypothesis (hRH : _root_.RiemannHypothesis)
    {s : ℂ} (hs : 1 / 2 < s.re) (hs1 : s ≠ 1) :
    Filter.Tendsto
      (fun N : ℕ => ∑ n ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius n : ℂ) / (n : ℂ) ^ s)
      Filter.atTop (nhds (riemannZeta s)⁻¹) := by
  let ε : ℝ := (s.re - 1 / 2) / 2
  have hε : 0 < ε := by dsimp [ε]; linarith
  have hr : (1 / 2 : ℝ) + ε < s.re := by dsimp [ε]; linarith
  have hr_pos : 0 ≤ (1 / 2 : ℝ) + ε := by linarith
  have hs_pos : 0 < s.re := by linarith
  have hs_ne0 : s ≠ 0 := ne_zero_of_re_pos hs_pos
  have hO := isBigO_mertens_of_riemannHypothesis hRH ε hε
  have hf_diff : ∀ t ∈ Ici 1, DifferentiableAt ℝ (fun x : ℝ => (x : ℂ) ^ (-s)) t := fun t ht =>
    differentiableAt_id.ofReal_cpow_const (zero_lt_one.trans_le ht).ne' (neg_ne_zero.mpr hs_ne0)
  have hf_int : LocallyIntegrableOn (deriv (fun x : ℝ => (x : ℂ) ^ (-s))) (Ici 1) :=
    (Iff.mpr integrableOn_Ici_iff_integrableOn_Ioi <|
      integrableOn_Ioi_deriv_ofReal_cpow zero_lt_one
        (by simp [Complex.neg_re]; linarith)).locallyIntegrableOn
  have h_sum_O : (fun n : ℕ => ∑ k ∈ Finset.Icc 0 n, moebC k) =O[atTop]
      fun n : ℕ => (n : ℝ) ^ ((1 / 2 : ℝ) + ε) := by
    have h_nat : (fun n : ℕ => (mertens (n : ℝ) : ℝ)) =O[atTop]
        fun n : ℕ => (n : ℝ) ^ ((1 / 2 : ℝ) + ε) :=
      hO.comp_tendsto tendsto_natCast_atTop_atTop
    have h_m_c : (fun n : ℕ => (mertens (n : ℝ) : ℂ)) =O[atTop]
        fun n : ℕ => (n : ℝ) ^ ((1 / 2 : ℝ) + ε) :=
      isBigO_ofReal_left.mpr h_nat
    simpa only [mertens_nat_cast] using h_m_c
  have hlim : Tendsto (fun n : ℕ ↦ (n : ℝ) ^ (-(s.re - ((1 / 2 : ℝ) + ε)))) atTop (𝓝 0) :=
    (tendsto_rpow_neg_atTop (by dsimp [ε]; linarith)).comp tendsto_natCast_atTop_atTop
  have h_lim : Tendsto (fun n : ℕ => (n : ℂ) ^ (-s) * ∑ k ∈ Finset.Icc 0 n, moebC k) atTop (𝓝 0) :=
    (IsBigO.mul_atTop_rpow_natCast_of_isBigO_rpow (-s.re) _ _
      (isBigO_norm_left.mp (norm_ofReal_cpow_eventually_eq_atTop _).isBigO.natCast_atTop)
      h_sum_O (by linarith)).trans_tendsto hlim
  let g : ℝ → ℝ := fun t => t ^ (-(s.re + 1) + ((1 / 2 : ℝ) + ε))
  have h_int : IntegrableAtFilter g atTop := by
    refine integrableAtFilter_rpow_atTop_iff.mpr ?_
    show -(s.re + 1) + (1 / 2 + ε) < -1
    dsimp [ε]
    linarith
  have hg_dom : (fun t => deriv (fun x : ℝ => (x : ℂ) ^ (-s)) t *
      ∑ k ∈ Finset.Icc 0 ⌊t⌋₊, moebC k) =O[atTop] g := by
    refine .mul_atTop_rpow_of_isBigO_rpow (-(s + 1).re) ((1 / 2 : ℝ) + ε) _ ?_ ?_ ?_
    · simpa [-neg_add_rev, neg_add'] using! isBigO_deriv_ofReal_cpow_const_atTop (-s)
    · exact (h_sum_O.comp_tendsto tendsto_nat_floor_atTop).trans <|
        isEquivalent_nat_floor.isBigO.rpow hr_pos (eventually_ge_atTop 0)
    · have : (-s - 1).re = -(s.re + 1) := by rw [sub_re, neg_re, one_re]; ring
      dsimp [g]
      linarith
  have h_abel := tendsto_sum_mul_atTop_nhds_one_sub_integral₀ (c := moebC)
    (f := fun x : ℝ => (x : ℂ) ^ (-s)) (l := 0) (by simp [moebC]) hf_diff hf_int h_lim hg_dom h_int
  have h_int_val : (0 : ℂ) - ∫ (t : ℝ) in Ioi 1, deriv (fun x : ℝ => (x : ℂ) ^ (-s)) t *
      ∑ k ∈ Finset.Icc 0 ⌊t⌋₊, moebC k = mellinMertens s := by
    rw [zero_sub, integral_deriv_eq_mellinMertens s hs]
  rw [h_int_val] at h_abel
  have h_zeta_mul := riemannZeta_mul_mellinMertens_eq_one_of_isBigO
    (isBigO_mertens_of_riemannHypothesis hRH) s hs hs1
  have h_mellin_eq : mellinMertens s = (riemannZeta s)⁻¹ :=
    eq_inv_of_mul_eq_one_right h_zeta_mul
  rw [h_mellin_eq] at h_abel
  refine h_abel.congr' ?_
  filter_upwards [eventually_ge_atTop 1] with N hN
  rw [sum_Icc_zero_moebC_mul hN]
  refine Finset.sum_congr rfl fun k hk => ?_
  exact cpow_neg_mul_eq_div s (Finset.mem_Icc.mp hk).1 _

/-- _root_.RiemannHypothesis holds if and only if for every s : ℂ with 1 / 2 < s.re
and s ≠ 1, the Möbius Dirichlet series partial sums converge to (riemannZeta s)⁻¹
and 
iemannZeta s ≠ 0. -/
theorem riemannHypothesis_iff_tendsto_sum_moebius :
    _root_.RiemannHypothesis ↔
      ∀ s : ℂ, 1 / 2 < s.re → s ≠ 1 →
        Filter.Tendsto
          (fun N : ℕ => ∑ n ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius n : ℂ) / (n : ℂ) ^ s)
          Filter.atTop (nhds (riemannZeta s)⁻¹) ∧ riemannZeta s ≠ 0 := by
  constructor
  · intro hRH s hs hs1
    refine ⟨tendsto_sum_moebius_cpow_of_riemannHypothesis hRH hs hs1, ?_⟩
    have hM := isBigO_mertens_of_riemannHypothesis hRH
    have h_inv := riemannZeta_mul_mellinMertens_eq_one_of_isBigO hM s hs hs1
    intro hz
    rw [hz, zero_mul] at h_inv
    exact zero_ne_one h_inv
  · intro h s hz h_not_triv h_not_one
    by_contra h_ne
    rcases lt_or_gt_of_ne h_ne with hlt | hgt
    · have hre_refl : 1 / 2 < (1 - s).re := by rw [Complex.sub_re, Complex.one_re]; linarith
      have hz_refl := riemannZeta_zero_reflection hz h_not_triv h_not_one hlt
      have h1ms_ne : 1 - s ≠ 1 := fun h1 => by
        have : s = 0 := by linear_combination -h1
        subst this
        simp [riemannZeta_zero] at hz
      exact (h (1 - s) hre_refl h1ms_ne).2 hz_refl.1
    · exact (h s hgt h_not_one).2 hz
