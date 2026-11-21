/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
module

public import Mathlib.Analysis.PSeriesComplex
public import Mathlib.MeasureTheory.Function.Floor
public import Mathlib.NumberTheory.LSeries.Nonvanishing
public import RiemannBlueprint.MathlibPR_LittlewoodConverse
public import RiemannBlueprint.MathlibPR_NymanBeurling

/-!
# Nyman–Beurling Mellin-Space Sawtooth Converse & Bidirectional Equivalence

This module formalizes the converse direction of the Nyman–Beurling theorem in the Mellin
frequency domain: under `RiemannHypothesis`, the explicit Möbius sawtooth approximations
annihilate the Mellin residual across the right critical strip `1 / 2 < Re(s) < 1`, establishing
the bidirectional equivalence `RiemannHypothesis ↔ ∀ s, 1/2 < s.re → s.re < 1 → Mellin → 0`.
-/

@[expose] public section

open MeasureTheory Set Filter

private lemma integral_Ioc_cpow_eq_one_div (s : ℂ) (hs_pos : 0 < s.re) :
    ∫ x in Ioc (0 : ℝ) 1, (x : ℂ) ^ (s - 1) = 1 / s := by
  have hs_ne : s ≠ 0 := fun h0 => by rw [h0] at hs_pos; simp at hs_pos
  rw [← intervalIntegral.integral_of_le (by norm_num : (0 : ℝ) ≤ 1),
    integral_cpow (Or.inl (by simp [Complex.sub_re]; linarith [hs_pos]))]
  have hs1 : s - 1 + 1 = s := by ring
  rw [hs1, Complex.ofReal_one, Complex.one_cpow, Complex.ofReal_zero,
    Complex.zero_cpow hs_ne, sub_zero]

lemma integral_Ioo_moebius_recipFract_eq (s : ℂ) (hs : 0 < s.re ∧ s.re < 1) (N : ℕ) :
    ∫ x : ℝ in Set.Ioo 0 1,
      (1 + ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) * (recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1) =
      (1 / s) * (1 - riemannZeta s * ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s) +
      (1 / (s - 1)) * ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) := by
  have hs_ne : s ≠ 0 := fun h0 => by rw [h0] at hs; simp at hs
  have hs_sub_ne : s - 1 ≠ 0 := sub_ne_zero.mpr fun h1 => by rw [h1] at hs; norm_num at hs
  have h_term : ∀ k ∈ Finset.Icc 1 N, IntegrableOn
      (fun x : ℝ => (ArithmeticFunction.moebius k : ℂ) *
        ((recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1))) (Ioc (0 : ℝ) 1) :=
    fun k hk => (integrableOn_Ioc_recipFractScaled_cpow k
      (Finset.mem_Icc.mp hk).1 s hs).const_mul _
  have h_sum_int : IntegrableOn (fun x : ℝ => ∑ k ∈ Finset.Icc 1 N,
      (ArithmeticFunction.moebius k : ℂ) *
        ((recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1))) (Ioc (0 : ℝ) 1) :=
    integrable_finsetSum _ fun k hk => h_term k hk
  have h_decomp : (fun x : ℝ => (1 + ∑ k ∈ Finset.Icc 1 N,
      (ArithmeticFunction.moebius k : ℂ) * (recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1)) =
      (fun x : ℝ => (x : ℂ) ^ (s - 1) + ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) *
          ((recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1))) := by
    ext x
    rw [add_mul, one_mul, Finset.sum_mul]
    congr 1
    exact Finset.sum_congr rfl fun k _ => by ring
  rw [setIntegral_congr_set Ioo_ae_eq_Ioc, h_decomp,
    integral_add (integrableOn_Ioc_cpow s hs.1) h_sum_int,
    integral_Ioc_cpow_eq_one_div s hs.1, integral_finsetSum _ fun k hk => h_term k hk]
  have h_sum_eval : ∑ k ∈ Finset.Icc 1 N, ∫ x in Ioc (0 : ℝ) 1,
      (ArithmeticFunction.moebius k : ℂ) *
        ((recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1)) =
      (1 / (s - 1)) * (∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ)) -
      (riemannZeta s / s) * (∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s) := by
    calc ∑ k ∈ Finset.Icc 1 N, ∫ x in Ioc (0 : ℝ) 1,
          (ArithmeticFunction.moebius k : ℂ) *
            ((recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1))
        = ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) *
            (1 / ((k : ℂ) * (s - 1)) - riemannZeta s / (s * (k : ℂ) ^ s)) := by
          refine Finset.sum_congr rfl fun k hk => ?_
          rw [integral_const_mul,
            integral_Ioc_recipFractScaled_cpow k (Finset.mem_Icc.mp hk).1 s hs]
      _ = ∑ k ∈ Finset.Icc 1 N,
            ((1 / (s - 1)) * ((ArithmeticFunction.moebius k : ℂ) / (k : ℂ)) -
             (riemannZeta s / s) * ((ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s)) := by
          refine Finset.sum_congr rfl fun k hk => ?_
          have hk_pos : 1 ≤ k := (Finset.mem_Icc.mp hk).1
          have hk_ne : (k : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
          have hk_pow_ne : (k : ℂ) ^ s ≠ 0 := Complex.cpow_ne_zero_iff.mpr (Or.inl hk_ne)
          field_simp [hk_ne, hs_sub_ne, hs_ne, hk_pow_ne]
      _ = (∑ k ∈ Finset.Icc 1 N,
            (1 / (s - 1)) * ((ArithmeticFunction.moebius k : ℂ) / (k : ℂ))) -
          (∑ k ∈ Finset.Icc 1 N,
            (riemannZeta s / s) * ((ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s)) := by
          rw [Finset.sum_sub_distrib]
      _ = (1 / (s - 1)) * (∑ k ∈ Finset.Icc 1 N,
            (ArithmeticFunction.moebius k : ℂ) / (k : ℂ)) -
          (riemannZeta s / s) * (∑ k ∈ Finset.Icc 1 N,
            (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s) := by
          rw [← Finset.mul_sum, ← Finset.mul_sum]
  rw [h_sum_eval]
  ring

/-- Converse of Nyman–Beurling in the Mellin frequency domain: under `RiemannHypothesis`,
for every `s : ℂ` in the right half of the critical strip (`1 / 2 < s.re` and `s.re < 1`),
the Mellin transform of the Möbius sawtooth residual
`1 + ∑_{k=1}^N μ(k) {1 / (k x)}` on `(0, 1)` converges to `0` as `N → ∞`. -/
theorem tendsto_mellin_moebius_recipFract_of_riemannHypothesis
    (hRH : _root_.RiemannHypothesis) {s : ℂ} (hs_lo : 1 / 2 < s.re) (hs_hi : s.re < 1) :
    Filter.Tendsto
      (fun N : ℕ =>
        ∫ x : ℝ in Set.Ioo 0 1,
          (1 + ∑ k ∈ Finset.Icc 1 N,
            (ArithmeticFunction.moebius k : ℂ) * (recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1))
      Filter.atTop (nhds 0) := by
  have hs_pos : 0 < s.re := by linarith
  have hs_strip : 0 < s.re ∧ s.re < 1 := ⟨hs_pos, hs_hi⟩
  have hs_ne_one : s ≠ 1 := fun h1 => by rw [h1] at hs_hi; simp at hs_hi
  have hz_ne : riemannZeta s ≠ 0 := by
    intro hz
    have h_not_triv : ¬ (∃ n : ℕ, s = -2 * (n + 1 : ℂ)) := fun ⟨n, hn⟩ => by
      have hre : s.re = -2 * (n + 1 : ℝ) := by
        rw [hn]
        simp
      linarith
    have hre_half := hRH s hz h_not_triv hs_ne_one
    linarith
  have h_cpow := tendsto_sum_moebius_cpow_of_riemannHypothesis hRH hs_lo hs_ne_one
  have h_div := tendsto_sum_moebius_div_self_of_riemannHypothesis hRH
  have h_mul_zeta : Filter.Tendsto
      (fun N : ℕ => riemannZeta s * ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s)
      Filter.atTop (nhds 1) := by
    have h := Filter.Tendsto.const_mul (riemannZeta s) h_cpow
    rw [mul_inv_cancel₀ hz_ne] at h
    exact h
  have h_sub_one : Filter.Tendsto
      (fun N : ℕ => 1 - riemannZeta s * ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s)
      Filter.atTop (nhds 0) := by
    have h := Filter.Tendsto.sub (tendsto_const_nhds (x := (1 : ℂ))) h_mul_zeta
    rw [sub_self] at h
    exact h
  have h_term1 : Filter.Tendsto
      (fun N : ℕ => (1 / s) * (1 - riemannZeta s * ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s))
      Filter.atTop (nhds 0) := by
    have h := Filter.Tendsto.const_mul (1 / s) h_sub_one
    rw [mul_zero] at h
    exact h
  have h_term2 : Filter.Tendsto
      (fun N : ℕ => (1 / (s - 1)) * ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) / (k : ℂ))
      Filter.atTop (nhds 0) := by
    have h := Filter.Tendsto.const_mul (1 / (s - 1)) h_div
    rw [mul_zero] at h
    exact h
  have h_add := Filter.Tendsto.add h_term1 h_term2
  rw [add_zero] at h_add
  refine h_add.congr fun N => ?_
  symm
  exact integral_Ioo_moebius_recipFract_eq s hs_strip N

/-- Bidirectional Mellin-space Nyman–Beurling equivalence: `_root_.RiemannHypothesis` holds
if and only if for every `s : ℂ` in the right critical strip (`1 / 2 < s.re` and `s.re < 1`),
the Mellin transform of the Möbius sawtooth residual converges to `0`. -/
theorem riemannHypothesis_iff_mellin_recipFract_approx :
    _root_.RiemannHypothesis ↔
      ∀ s : ℂ, 1 / 2 < s.re → s.re < 1 →
        Filter.Tendsto
          (fun N : ℕ =>
            ∫ x : ℝ in Set.Ioo 0 1,
              (1 + ∑ k ∈ Finset.Icc 1 N,
                (ArithmeticFunction.moebius k : ℂ) *
                  (recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1))
          Filter.atTop (nhds 0) := by
  refine ⟨fun hRH s hs_lo hs_hi =>
    tendsto_mellin_moebius_recipFract_of_riemannHypothesis hRH hs_lo hs_hi, fun h_mellin => ?_⟩
  intro s₀ hz h_not_triv h_not_one
  rcases riemannZeta_zero_strip_symm hz h_not_triv h_not_one with ⟨hs, hz_refl, hs_refl⟩
  by_contra h_ne
  have hw : ∃ w : ℂ, 1 / 2 < w.re ∧ w.re < 1 ∧ riemannZeta w = 0 := by
    rcases lt_or_gt_of_ne h_ne with hlt | hgt
    · refine ⟨1 - s₀, ?_, ?_, hz_refl⟩
      · rw [Complex.sub_re, Complex.one_re]; linarith
      · rw [Complex.sub_re, Complex.one_re]; linarith [hs.1]
    · refine ⟨s₀, hgt, hs.2, hz⟩
  rcases hw with ⟨w, hw_lo, hw_hi, hw_zero⟩
  have hw_pos : 0 < w.re := by linarith
  have hw_strip : 0 < w.re ∧ w.re < 1 := ⟨hw_pos, hw_hi⟩
  have hw_ne_zero : w ≠ 0 := fun h0 => by rw [h0] at hw_pos; simp at hw_pos
  have hw_sub_ne : w - 1 ≠ 0 := sub_ne_zero.mpr fun h1 => by rw [h1] at hw_hi; simp at hw_hi
  have hw_c_lo : 1 / 2 < (starRingEnd ℂ w).re := by simpa using hw_lo
  have hw_c_hi : (starRingEnd ℂ w).re < 1 := by simpa using hw_hi
  have hw_c_ne_one : starRingEnd ℂ w ≠ 1 :=
    fun h1 => hw_sub_ne (sub_eq_zero.mpr (by simpa using congr_arg (starRingEnd ℂ) h1))
  have hw_c_zero : riemannZeta (starRingEnd ℂ w) = 0 := by
    rw [riemannZeta_conj_of_pos_re w hw_pos (sub_ne_zero.mp hw_sub_ne), hw_zero, map_zero]
  have h_int_w := h_mellin w hw_lo hw_hi
  have h_int_wc := h_mellin (starRingEnd ℂ w) hw_c_lo hw_c_hi
  have h_sim_w : ∀ N : ℕ,
      ∫ x : ℝ in Set.Ioo 0 1,
        (1 + ∑ k ∈ Finset.Icc 1 N,
          (ArithmeticFunction.moebius k : ℂ) * (recipFractScaled k x : ℂ)) * (x : ℂ) ^ (w - 1) =
      (1 / w) + (1 / (w - 1)) *
        ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) := by
    intro N
    rw [integral_Ioo_moebius_recipFract_eq w hw_strip N, hw_zero, zero_mul, sub_zero, mul_one]
  have h_sim_wc : ∀ N : ℕ,
      ∫ x : ℝ in Set.Ioo 0 1,
        (1 + ∑ k ∈ Finset.Icc 1 N,
          (ArithmeticFunction.moebius k : ℂ) * (recipFractScaled k x : ℂ)) *
            (x : ℂ) ^ (starRingEnd ℂ w - 1) =
      (1 / starRingEnd ℂ w) + (1 / (starRingEnd ℂ w - 1)) *
        ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) := by
    intro N
    have hw_c_strip : 0 < (starRingEnd ℂ w).re ∧ (starRingEnd ℂ w).re < 1 :=
      ⟨by simpa using hw_pos, hw_c_hi⟩
    rw [integral_Ioo_moebius_recipFract_eq (starRingEnd ℂ w) hw_c_strip N,
      hw_c_zero, zero_mul, sub_zero, mul_one]
  have h_step_w : Filter.Tendsto
      (fun N : ℕ => ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ))
      Filter.atTop (nhds (1 / w - 1)) := by
    have h_sub := Filter.Tendsto.sub (h_int_w.congr h_sim_w)
      (tendsto_const_nhds (x := 1 / w))
    rw [zero_sub] at h_sub
    have h_mul := Filter.Tendsto.const_mul (w - 1) h_sub
    have h_rw : (fun N : ℕ => (w - 1) * ((1 / w + (1 / (w - 1)) *
        ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ)) - 1 / w)) =
        (fun N : ℕ => ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ)) := by
      ext N
      simp only [add_sub_cancel_left]
      rw [← mul_assoc, mul_one_div_cancel hw_sub_ne, one_mul]
    rw [h_rw] at h_mul
    have h_lim : (w - 1) * -(1 / w) = 1 / w - 1 := by
      field_simp [hw_ne_zero]
      ring
    rw [h_lim] at h_mul
    exact h_mul
  have h_step_wc : Filter.Tendsto
      (fun N : ℕ => ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ))
      Filter.atTop (nhds (1 / starRingEnd ℂ w - 1)) := by
    have hw_c_sub_ne : starRingEnd ℂ w - 1 ≠ 0 := sub_ne_zero.mpr hw_c_ne_one
    have hw_c_ne_zero : starRingEnd ℂ w ≠ 0 :=
      fun h0 => hw_ne_zero (by simpa using congr_arg (starRingEnd ℂ) h0)
    have h_sub := Filter.Tendsto.sub (h_int_wc.congr h_sim_wc)
      (tendsto_const_nhds (x := 1 / starRingEnd ℂ w))
    rw [zero_sub] at h_sub
    have h_mul := Filter.Tendsto.const_mul (starRingEnd ℂ w - 1) h_sub
    have h_rw : (fun N : ℕ => (starRingEnd ℂ w - 1) * ((1 / starRingEnd ℂ w +
        (1 / (starRingEnd ℂ w - 1)) *
          ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ)) -
        1 / starRingEnd ℂ w)) =
        (fun N : ℕ => ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ)) := by
      ext N
      simp only [add_sub_cancel_left]
      rw [← mul_assoc, mul_one_div_cancel hw_c_sub_ne, one_mul]
    rw [h_rw] at h_mul
    have h_lim : (starRingEnd ℂ w - 1) * -(1 / starRingEnd ℂ w) = 1 / starRingEnd ℂ w - 1 := by
      field_simp [hw_c_ne_zero]
      ring
    rw [h_lim] at h_mul
    exact h_mul
  have h_eq : (1 / w - 1 : ℂ) = 1 / starRingEnd ℂ w - 1 :=
    tendsto_nhds_unique h_step_w h_step_wc
  have h_inv_eq : (1 / w : ℂ) = 1 / starRingEnd ℂ w := by
    linear_combination h_eq
  have hw_eq_conj : w = starRingEnd ℂ w := by
    have h1 : (1 / w : ℂ)⁻¹ = (1 / starRingEnd ℂ w : ℂ)⁻¹ := by rw [h_inv_eq]
    simpa using h1
  have hw_im_ne := im_ne_zero_of_inCriticalStrip_zeta_zero w hw_strip hw_zero
  exact hw_im_ne (by
    have h := congr_arg Complex.im hw_eq_conj
    simp only [Complex.conj_im] at h
    linarith)
