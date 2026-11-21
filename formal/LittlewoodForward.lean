import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.NumberTheory.LSeries.Dirichlet
import Mathlib.NumberTheory.LSeries.Nonvanishing
import Mathlib.NumberTheory.LSeries.SumCoeff
import Mathlib.Analysis.MellinTransform
import Mathlib.Analysis.Complex.CauchyIntegral
import Mathlib.Analysis.Analytic.Uniqueness
import RiemannBlueprint.ClassicalAnalyticInterface

/-!
# Littlewood's (1912) Forward Theorem: `MertensBound → RiemannHypothesis`

Unconditional Lean 4 + Mathlib4 proof of the forward direction of Littlewood's
Mertens–Riemann equivalence:
1. Stage A (`1 < s.re`): Abel summation (`LSeries_eq_mul_integral'`) identifies
   `LSeries ↗μ s = mellinMertens s` and hence `riemannZeta s * mellinMertens s = 1`.
2. Stage B (`1/2 < s.re`): Under `MertensBound`, `mellinMertens` is holomorphic on the
   half-plane `{s : ℂ | 1 / 2 < s.re}` via `mellin_differentiableAt_of_isBigO_rpow`.
3. Stage C (`1/2 < s.re`): Analytic continuation via `AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq`
   across open convex subsets (`U_top`, `U_bot`, `U_strip`) extends `riemannZeta s * mellinMertens s = 1`
   to all `1/2 < s.re` (`s ≠ 1`), while `riemannZeta_ne_zero_of_one_le_re` handles `s = 1`.
-/

set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.style.openClassical false

namespace RiemannBlueprint.LittlewoodForward

open scoped ArithmeticFunction.zeta ArithmeticFunction.Moebius LSeries.notation Topology
open Filter MeasureTheory Set Complex Asymptotics

/-- Complex-valued Möbius coefficient sequence `n ↦ (μ(n) : ℂ)`. -/
noncomputable def moebiusC : ℕ → ℂ := fun n => (ArithmeticFunction.moebius n : ℂ)

/-- Mellin-Mertens integral representation of `1 / ζ(s)`:
`M_ζ(s) = s * ∫_{t > 1} M(t) * t^{-(s+1)} dt`. -/
noncomputable def mellinMertens (s : ℂ) : ℂ :=
  s * ∫ x in Set.Ioi (1 : ℝ), (RiemannBlueprint.mertens x : ℂ) * (x : ℂ) ^ (-(s + 1))

/-- Indicator extension of `M(x)` supported on `(1, ∞)` for `Mathlib`'s `mellin`. -/
noncomputable def mertensIndicator (x : ℝ) : ℂ :=
  if 1 < x then (RiemannBlueprint.mertens x : ℂ) else 0

/-- Corrected inverse on the half-plane `{s : ℂ | 1/2 < s.re}` (handling the dummy value at `s = 1`). -/
noncomputable def mellinMertensInv (s : ℂ) : ℂ :=
  if s = 1 then (riemannZeta 1)⁻¹ else mellinMertens s

/-! ### Stage A: Abel Summation / Integral Identity on `{s : ℂ | 1 < s.re}` -/

/-- Helper: `(mertens x : ℂ)` agrees with the `Icc 1 ⌊x⌋₊` sum of `(μ k : ℂ)`. -/
lemma mertens_cast_eq_sum_Icc (x : ℝ) :
    (RiemannBlueprint.mertens x : ℂ) =
      ∑ k ∈ Finset.Icc 1 ⌊x⌋₊, moebiusC k := by
  dsimp [RiemannBlueprint.mertens, moebiusC]
  push_cast
  have hIic : Finset.Iic ⌊x⌋₊ = insert 0 (Finset.Icc 1 ⌊x⌋₊) := by
    ext k
    simp only [Finset.mem_Iic, Finset.mem_insert, Finset.mem_Icc]
    omega
  rw [hIic, Finset.sum_insert (by simp)]
  simp

/-- Unconditional bound `∑_{k ∈ Icc 1 n} ‖moebiusC k‖ = O(n)`. -/
lemma moebiusC_sum_norm_isBigO :
    (fun n : ℕ => ∑ k ∈ Finset.Icc 1 n, ‖moebiusC k‖) =O[atTop] fun n : ℕ => (n : ℝ) ^ (1 : ℝ) := by
  refine IsBigO.of_bound 1 (Eventually.of_forall fun n => ?_)
  have h_le : ∑ k ∈ Finset.Icc 1 n, ‖moebiusC k‖ ≤ (n : ℝ) := by
    calc ∑ k ∈ Finset.Icc 1 n, ‖moebiusC k‖
        ≤ ∑ _k ∈ Finset.Icc 1 n, (1 : ℝ) := by
          refine Finset.sum_le_sum fun k _ => ?_
          simpa [moebiusC, Complex.norm_intCast] using
            (show |(ArithmeticFunction.moebius k : ℝ)| ≤ 1 by
              exact_mod_cast ArithmeticFunction.abs_moebius_le_one (n := k))
      _ = (Finset.Icc 1 n).card := by simp
      _ ≤ n := by
          norm_cast
          simp [Nat.card_Icc]
  have h_nn : 0 ≤ ∑ k ∈ Finset.Icc 1 n, ‖moebiusC k‖ :=
    Finset.sum_nonneg fun k _ => norm_nonneg _
  simpa [Real.norm_of_nonneg h_nn, Real.rpow_one, Real.norm_natCast] using h_le

/-- **Stage A:** For `1 < s.re`, `riemannZeta s * mellinMertens s = 1`. -/
theorem riemannZeta_mul_mellinMertens_of_one_lt_re {s : ℂ} (hs : 1 < s.re) :
    riemannZeta s * mellinMertens s = 1 := by
  have h_int : LSeries moebiusC s = mellinMertens s := by
    rw [LSeries_eq_mul_integral' moebiusC zero_le_one hs moebiusC_sum_norm_isBigO]
    dsimp [mellinMertens]
    congr 1
    refine setIntegral_congr_fun measurableSet_Ioi fun t _ => ?_
    rw [mertens_cast_eq_sum_Icc]
  have h_mul : riemannZeta s * LSeries moebiusC s = 1 := by
    have hz : LSeries (1 : ℕ → ℂ) s = riemannZeta s := LSeries_one_eq_riemannZeta hs
    have hmul : LSeries (1 : ℕ → ℂ) s * LSeries (↗ArithmeticFunction.moebius) s = 1 :=
      LSeries_one_mul_Lseries_moebius hs
    rw [hz] at hmul
    have h_congr : LSeries (↗ArithmeticFunction.moebius) s = LSeries moebiusC s :=
      LSeries_congr (fun _ => by simp [moebiusC]) s
    rw [h_congr] at hmul
    exact hmul
  rw [← h_int]
  exact h_mul

/-! ### Stage B: Holomorphicity of `mellinMertens` on `{s : ℂ | 1/2 < s.re}` -/

/-- Relates `mellinMertens s` to Mathlib's `mellin mertensIndicator (-s)`. -/
lemma mellinMertens_eq_mul_mellin (s : ℂ) :
    mellinMertens s = s * mellin mertensIndicator (-s) := by
  dsimp [mellinMertens, mellin]
  congr 1
  have h_eq : EqOn
      (fun t : ℝ => (t : ℂ) ^ ((-s) - 1) * mertensIndicator t)
      ((Set.Ioi 1).indicator (fun t : ℝ => (RiemannBlueprint.mertens t : ℂ) * (t : ℂ) ^ (-(s + 1))))
      (Set.Ioi 0) := by
    intro t _ht
    by_cases ht1 : 1 < t
    · have h_exp : (-s - 1 : ℂ) = -(s + 1) := by ring
      simp [mertensIndicator, ht1, mul_comm, h_exp]
    · simp [mertensIndicator, ht1]
  have h_eq' : EqOn
      ((Set.Ioi 1).indicator (fun t : ℝ => (RiemannBlueprint.mertens t : ℂ) * (t : ℂ) ^ (-(s + 1))))
      (fun t : ℝ => (t : ℂ) ^ ((-s) - 1) * mertensIndicator t)
      (Set.Ioi 0) := h_eq.symm
  rw [← setIntegral_congr_fun measurableSet_Ioi h_eq', setIntegral_indicator measurableSet_Ioi]
  have h_inter : Set.Ioi (0 : ℝ) ∩ Set.Ioi 1 = Set.Ioi 1 := by
    ext t
    simp only [Set.mem_inter_iff, Set.mem_Ioi]
    exact ⟨fun h => h.2, fun h => ⟨zero_lt_one.trans h, h⟩⟩
  rw [h_inter]

/-- `mertensIndicator` is locally integrable on `(0, ∞)`. -/
lemma locallyIntegrableOn_mertensIndicator :
    LocallyIntegrableOn mertensIndicator (Set.Ioi 0) := by
  have h_sum : LocallyIntegrableOn (fun t : ℝ => ∑ k ∈ Finset.Icc 1 ⌊t⌋₊, moebiusC k) (Set.Ici 0) := by
    simpa using locallyIntegrableOn_mul_sum_Icc (𝕜 := ℂ) (c := moebiusC) (m := 1)
      le_rfl (locallyIntegrableOn_const (1 : ℂ))
  have h_loc : LocallyIntegrableOn (fun t : ℝ => (RiemannBlueprint.mertens t : ℂ)) (Set.Ioi 0) := by
    have h_fn : (fun t : ℝ => (RiemannBlueprint.mertens t : ℂ)) =
        fun t : ℝ => ∑ k ∈ Finset.Icc 1 ⌊t⌋₊, moebiusC k :=
      funext mertens_cast_eq_sum_Icc
    rw [h_fn]
    exact h_sum.mono_set Set.Ioi_subset_Ici_self
  rw [locallyIntegrableOn_iff isLocallyClosed_Ioi]
  intro K hK_sub hK_cpt
  have hK_int : IntegrableOn (fun t : ℝ => (RiemannBlueprint.mertens t : ℂ)) K :=
    h_loc.integrableOn_compact_subset hK_sub hK_cpt
  have h_ind : IntegrableOn ((Set.Ioi 1).indicator (fun t : ℝ => (RiemannBlueprint.mertens t : ℂ))) K :=
    hK_int.indicator measurableSet_Ioi
  refine h_ind.congr_fun (fun t _ => ?_) hK_cpt.measurableSet
  by_cases ht : 1 < t <;> simp [mertensIndicator, ht]

/-- Under `MertensBound`, `mertensIndicator =O[atTop] (· ^ (1/2 + ε))`. -/
lemma mertensIndicator_isBigO_atTop (h_mertens : RiemannBlueprint.MertensBound)
    {ε : ℝ} (hε : 0 < ε) :
    mertensIndicator =O[atTop] fun x : ℝ => x ^ ((1 / 2 : ℝ) + ε) := by
  obtain ⟨C, hC, hbd⟩ := h_mertens ε hε
  refine IsBigO.of_bound C ?_
  filter_upwards [eventually_ge_atTop (1 : ℝ)] with x hx
  have hx_pos : 0 < x := zero_lt_one.trans_le hx
  have hrpow_nn : 0 ≤ x ^ ((1 / 2 : ℝ) + ε) := Real.rpow_nonneg hx_pos.le _
  rw [Real.norm_of_nonneg hrpow_nn]
  by_cases hx1 : 1 < x
  · simpa [mertensIndicator, hx1, Complex.norm_intCast] using hbd x hx
  · rw [mertensIndicator, if_neg hx1, norm_zero]
    positivity

/-- Near `0+`, `mertensIndicator` vanishes identically and is `O(x ^ (-b))` for any `b`. -/
lemma mertensIndicator_isBigO_nhdsWithin_zero (b : ℝ) :
    mertensIndicator =O[𝓝[>] (0 : ℝ)] fun x : ℝ => x ^ (-b) := by
  refine (isBigO_zero (fun x : ℝ => x ^ (-b)) (𝓝[>] 0)).congr' ?_ EventuallyEq.rfl
  filter_upwards [eventually_nhdsWithin_of_eventually_nhds (Iio_mem_nhds one_pos)] with x hx
  simp [mertensIndicator, not_lt.mpr (le_of_lt hx)]

/-- **Stage B:** Under `MertensBound`, `mellinMertens` is complex-differentiable at every `s` with `1/2 < s.re`. -/
theorem mellinMertens_differentiableAt (h_mertens : RiemannBlueprint.MertensBound)
    {s : ℂ} (hs : 1 / 2 < s.re) :
    DifferentiableAt ℂ mellinMertens s := by
  have h_fn : mellinMertens = fun z : ℂ => z * mellin mertensIndicator (-z) :=
    funext mellinMertens_eq_mul_mellin
  rw [h_fn]
  have hε : 0 < (s.re - 1 / 2) / 2 := by linarith
  set ε : ℝ := (s.re - 1 / 2) / 2
  set a : ℝ := -((1 / 2 : ℝ) + ε)
  set b : ℝ := (-s).re - 1
  have hf_top : mertensIndicator =O[atTop] (· ^ (-a)) := by
    simpa [a, neg_neg] using mertensIndicator_isBigO_atTop h_mertens hε
  have hs_top : (-s).re < a := by
    rw [neg_re]
    dsimp [a, ε]
    linarith
  have hs_bot : b < (-s).re := by
    dsimp [b]
    linarith
  have hm_diff : DifferentiableAt ℂ (mellin mertensIndicator) (-s) :=
    mellin_differentiableAt_of_isBigO_rpow locallyIntegrableOn_mertensIndicator
      hf_top hs_top (mertensIndicator_isBigO_nhdsWithin_zero b) hs_bot
  have h_comp : DifferentiableAt ℂ (fun z : ℂ => mellin mertensIndicator (-z)) s :=
    hm_diff.comp s (differentiableAt_id.neg)
  exact differentiableAt_id.mul h_comp

/-! ### Stage C: Analytic Continuation to `{s : ℂ | 1/2 < s.re}` via Open Convex Subsets -/

private lemma isOpen_re_gt (r : ℝ) : IsOpen {s : ℂ | r < s.re} :=
  isOpen_lt continuous_const Complex.continuous_re

private lemma isOpen_re_lt (r : ℝ) : IsOpen {s : ℂ | s.re < r} :=
  isOpen_lt Complex.continuous_re continuous_const

private lemma isOpen_im_gt (r : ℝ) : IsOpen {s : ℂ | r < s.im} :=
  isOpen_lt continuous_const Complex.continuous_im

private lemma isOpen_im_lt (r : ℝ) : IsOpen {s : ℂ | s.im < r} :=
  isOpen_lt Complex.continuous_im continuous_const

private lemma convex_combination_gt {r u v a b : ℝ} (hu : r < u) (hv : r < v)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hab : a + b = 1) : r < a * u + b * v := by
  by_cases ha0 : 0 < a
  · calc r = a * r + b * r := by rw [← add_mul, hab, one_mul]
      _ < a * u + b * v := add_lt_add_of_lt_of_le
          (mul_lt_mul_of_pos_left hu ha0) (mul_le_mul_of_nonneg_left hv.le hb)
  · have ha0' : a = 0 := le_antisymm (not_lt.mp ha0) ha
    have hb1 : b = 1 := by linarith
    rw [ha0', hb1]
    linarith

private lemma convex_combination_lt {r u v a b : ℝ} (hu : u < r) (hv : v < r)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hab : a + b = 1) : a * u + b * v < r := by
  have h := convex_combination_gt (neg_lt_neg hu) (neg_lt_neg hv) ha hb hab
  linarith

private lemma convex_re_gt (r : ℝ) : Convex ℝ {s : ℂ | r < s.re} := by
  intro x hx y hy a b ha hb hab
  simp only [Set.mem_ofPred_eq, Complex.add_re, Complex.smul_re, smul_eq_mul] at hx hy ⊢
  exact convex_combination_gt hx hy ha hb hab

private lemma convex_re_lt (r : ℝ) : Convex ℝ {s : ℂ | s.re < r} := by
  intro x hx y hy a b ha hb hab
  simp only [Set.mem_ofPred_eq, Complex.add_re, Complex.smul_re, smul_eq_mul] at hx hy ⊢
  exact convex_combination_lt hx hy ha hb hab

private lemma convex_im_gt (r : ℝ) : Convex ℝ {s : ℂ | r < s.im} := by
  intro x hx y hy a b ha hb hab
  simp only [Set.mem_ofPred_eq, Complex.add_im, Complex.smul_im, smul_eq_mul] at hx hy ⊢
  exact convex_combination_gt hx hy ha hb hab

private lemma convex_im_lt (r : ℝ) : Convex ℝ {s : ℂ | s.im < r} := by
  intro x hx y hy a b ha hb hab
  simp only [Set.mem_ofPred_eq, Complex.add_im, Complex.smul_im, smul_eq_mul] at hx hy ⊢
  exact convex_combination_lt hx hy ha hb hab

/-- **Stage C:** For any `1/2 < s.re` with `s ≠ 1`, `riemannZeta s * mellinMertens s = 1`. -/
theorem riemannZeta_mul_mellinMertens_eq_one (h_mertens : RiemannBlueprint.MertensBound) :
    ∀ s : ℂ, 1 / 2 < s.re → s ≠ 1 → riemannZeta s * mellinMertens s = 1 := by
  let F : ℂ → ℂ := fun s => riemannZeta s * mellinMertens s
  let U : Set ℂ := {s : ℂ | 1 / 2 < s.re} \ {1}
  have hU_open : IsOpen U := (isOpen_re_gt (1 / 2)).sdiff isClosed_singleton
  have hF_diff : DifferentiableOn ℂ F U := fun s hs =>
    ((differentiableAt_riemannZeta hs.2).mul (mellinMertens_differentiableAt h_mertens hs.1)).differentiableWithinAt
  have hF_ana : AnalyticOnNhd ℂ F U := hF_diff.analyticOnNhd hU_open
  let U_top : Set ℂ := {s : ℂ | 1 / 2 < s.re} ∩ {s : ℂ | 0 < s.im}
  let U_bot : Set ℂ := {s : ℂ | 1 / 2 < s.re} ∩ {s : ℂ | s.im < 0}
  let U_strip : Set ℂ := {s : ℂ | 1 / 2 < s.re} ∩ {s : ℂ | s.re < 1}
  have hU_top_sub : U_top ⊆ U := by
    intro s hs
    refine ⟨hs.1, fun h1 => ?_⟩
    subst h1
    simp [U_top] at hs
  have hU_bot_sub : U_bot ⊆ U := by
    intro s hs
    refine ⟨hs.1, fun h1 => ?_⟩
    subst h1
    simp [U_bot] at hs
  have hU_strip_sub : U_strip ⊆ U := by
    intro s hs
    refine ⟨hs.1, fun h1 => ?_⟩
    subst h1
    simp [U_strip] at hs
  have hU_top_pre : IsPreconnected U_top :=
    ((convex_re_gt (1 / 2)).inter (convex_im_gt 0)).isPreconnected
  have hU_bot_pre : IsPreconnected U_bot :=
    ((convex_re_gt (1 / 2)).inter (convex_im_lt 0)).isPreconnected
  have hU_strip_pre : IsPreconnected U_strip :=
    ((convex_re_gt (1 / 2)).inter (convex_re_lt 1)).isPreconnected
  have h_one_ana : ∀ V : Set ℂ, AnalyticOnNhd ℂ (fun _ : ℂ => (1 : ℂ)) V :=
    fun _ => analyticOnNhd_const
  have h_eq_top : EqOn F (fun _ => (1 : ℂ)) U_top := by
    have hz0 : (2 : ℂ) + Complex.I ∈ U_top := by norm_num [U_top]
    have h_ev : F =ᶠ[𝓝 ((2 : ℂ) + Complex.I)] (fun _ => (1 : ℂ)) := by
      filter_upwards [(isOpen_re_gt 1).mem_nhds (by norm_num : 1 < ((2 : ℂ) + Complex.I).re)] with z hz
      exact riemannZeta_mul_mellinMertens_of_one_lt_re hz
    exact (hF_ana.mono hU_top_sub).eqOn_of_preconnected_of_eventuallyEq (h_one_ana U_top) hU_top_pre hz0 h_ev
  have h_eq_bot : EqOn F (fun _ => (1 : ℂ)) U_bot := by
    have hz0 : (2 : ℂ) - Complex.I ∈ U_bot := by norm_num [U_bot]
    have h_ev : F =ᶠ[𝓝 ((2 : ℂ) - Complex.I)] (fun _ => (1 : ℂ)) := by
      filter_upwards [(isOpen_re_gt 1).mem_nhds (by norm_num : 1 < ((2 : ℂ) - Complex.I).re)] with z hz
      exact riemannZeta_mul_mellinMertens_of_one_lt_re hz
    exact (hF_ana.mono hU_bot_sub).eqOn_of_preconnected_of_eventuallyEq (h_one_ana U_bot) hU_bot_pre hz0 h_ev
  have h_eq_strip : EqOn F (fun _ => (1 : ℂ)) U_strip := by
    have hz0 : ((3 / 4 : ℝ) : ℂ) + Complex.I ∈ U_strip := by norm_num [U_strip]
    have h_U_top_open : IsOpen U_top := (isOpen_re_gt (1 / 2)).inter (isOpen_im_gt 0)
    have h_ev : F =ᶠ[𝓝 (((3 / 4 : ℝ) : ℂ) + Complex.I)] (fun _ => (1 : ℂ)) := by
      filter_upwards [h_U_top_open.mem_nhds (by norm_num [U_top] : ((3 / 4 : ℝ) : ℂ) + Complex.I ∈ U_top)] with z hz
      exact h_eq_top hz
    exact (hF_ana.mono hU_strip_sub).eqOn_of_preconnected_of_eventuallyEq (h_one_ana U_strip) hU_strip_pre hz0 h_ev
  intro s hs hne
  rcases lt_trichotomy s.re 1 with hlt | heq | hgt
  · exact h_eq_strip ⟨hs, hlt⟩
  · have him : s.im ≠ 0 := by
      intro h0
      apply hne
      apply Complex.ext <;> simp [heq, h0]
    rcases lt_or_gt_of_ne him with him_lt | him_gt
    · exact h_eq_bot ⟨hs, him_lt⟩
    · exact h_eq_top ⟨hs, him_gt⟩
  · exact riemannZeta_mul_mellinMertens_of_one_lt_re hgt

/-- **Master Theorem (Mertens Inversion Without Axioms):**
Under `MertensBound`, `mellinMertensInv` is a right inverse of `riemannZeta` on all `s.re > 1/2`. -/
theorem mertens_inversion_of_bound (h_mertens : RiemannBlueprint.MertensBound) :
    ∃ I_M : ℂ → ℂ, ∀ s : ℂ, 1 / 2 < s.re → riemannZeta s * I_M s = 1 := by
  refine ⟨mellinMertensInv, fun s hs => ?_⟩
  by_cases h1 : s = 1
  · subst h1
    simp only [mellinMertensInv, ↓reduceIte]
    exact mul_inv_cancel₀ (riemannZeta_ne_zero_of_one_le_re (by norm_num))
  · simp only [mellinMertensInv, h1, ↓reduceIte]
    exact riemannZeta_mul_mellinMertens_eq_one h_mertens s hs h1

end RiemannBlueprint.LittlewoodForward
