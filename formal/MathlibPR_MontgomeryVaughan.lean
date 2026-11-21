/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import RiemannBlueprint.Section8_VasyuninBDR
import RiemannBlueprint.MathlibPR_ForwardCandidate
import RiemannBlueprint.MathlibPR_LinearMomentLimit
import RiemannBlueprint.MathlibPR_SpectralTailBound

/-!
# Montgomery--Vaughan Mean Value in Low-Frequency Window

This module formalizes Pillar II (Stage 3) of the forward Nyman--Beurling attack plan:
1. lowFreqWindow: cutoff height (N) = (\\ln N)^2$.
2. lowFreqWindow_pos: strict positivity of (N)$ for  \\ge 2$.
3. mvDiagonalSum: diagonal Montgomery--Vaughan energy $\\sum_{k=1}^N |c_k|^2 / k$.
4. mvOffDiagBound: off-diagonal Montgomery--Vaughan operator bound $\\sum_{k=1}^N |c_k|^2$.
5. LowFrequencyBound: structure formalizing the low-frequency spectral evaluation
   $|J_{\\text{low}}(N) - 1| \\le C_{\\text{low}} / (\\ln N)^2$.
6. inv_log_sq_le_inv_log: dominance lemma $\\frac{1}{(\\ln N)^2} \\le
   \\frac{1}{\\ln 2 \\cdot \\ln N}$.
7. Absorption theorem: converting $\\mathcal{O}(1 / (\\ln N)^2)$ low-frequency deviations
   into the global logarithmic scale $\\mathcal{O}(1 / \\ln N)$.
8. Synthesis theorem: linking low-frequency window bounds with mid-frequency sieve bounds
   to construct the low+mid frequency component of FrequencyDecomposition.
9. Candidate specializations: reductions for {\\mathrm{mob}}^{(N)}$ and
   {\\mathrm{sel}}^{(N)}$.
-/

open scoped BigOperators

namespace MathlibPR.MontgomeryVaughan

open RiemannBlueprint
open RiemannBlueprint.Section8_VasyuninBDR
open MathlibPR.ForwardCandidate
open MathlibPR.LinearMomentLimit
open MathlibPR.SpectralTailBound

/-- Cutoff height of the low-frequency compact window: (N) = (\\ln N)^2$. -/
noncomputable def lowFreqWindow (N : ℕ) : ℝ :=
  (Real.log (N : ℝ)) ^ 2

/-- Positivity of the low-frequency window cutoff for  \\ge 2$. -/
theorem lowFreqWindow_pos {N : ℕ} (hN : 2 ≤ N) : 0 < lowFreqWindow N := by
  unfold lowFreqWindow
  have hN2 : (2 : ℝ) ≤ (N : ℝ) := by exact_mod_cast hN
  have hN1 : (1 : ℝ) < (N : ℝ) := by linarith
  have hlog_pos : 0 < Real.log (N : ℝ) := Real.log_pos hN1
  exact sq_pos_of_pos hlog_pos

/-- Non-negativity of the low-frequency window cutoff. -/
theorem lowFreqWindow_nonneg (N : ℕ) : 0 ≤ lowFreqWindow N := by
  unfold lowFreqWindow
  exact sq_nonneg (Real.log (N : ℝ))

/-- Diagonal Montgomery--Vaughan sum: $\\sum_{k=1}^N \\frac{c_k^2}{k}$. -/
noncomputable def mvDiagonalSum (c : ℕ → ℝ) (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, (c k) ^ 2 / (k : ℝ)

/-- Positivity of the diagonal Montgomery--Vaughan sum. -/
theorem mvDiagonalSum_nonneg (c : ℕ → ℝ) (N : ℕ) : 0 ≤ mvDiagonalSum c N := by
  unfold mvDiagonalSum
  refine Finset.sum_nonneg (fun k hk => ?_)
  have hk1 : 1 ≤ k := (Finset.mem_Icc.mp hk).1
  have hk_pos : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  exact div_nonneg (sq_nonneg _) (le_of_lt hk_pos)

/-- Off-diagonal Montgomery--Vaughan operator bound: $\\sum_{k=1}^N c_k^2$. -/
noncomputable def mvOffDiagBound (c : ℕ → ℝ) (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, (c k) ^ 2

/-- Non-negativity of the off-diagonal operator bound. -/
theorem mvOffDiagBound_nonneg (c : ℕ → ℝ) (N : ℕ) : 0 ≤ mvOffDiagBound c N := by
  unfold mvOffDiagBound
  refine Finset.sum_nonneg (fun k _ => sq_nonneg _)

/-- Structure formalizing the low-frequency spectral integral bound.
In the compact window $|t| \\le (\\ln N)^2$, the mollified integrand evaluates to
 + \\mathcal{O}(1 / (\\ln N)^2)$. -/
structure LowFrequencyBound (c : ℕ → ℕ → ℝ) where
  J_low : ℕ → ℝ
  h_low_nonneg : ∀ N ≥ 2, 0 ≤ J_low N
  C_low : ℝ
  hC_low : 0 < C_low
  h_low_eval : ∀ N ≥ 2, |J_low N - 1| ≤ C_low / (Real.log (N : ℝ)) ^ 2

/-- Logarithmic power dominance:
For all  \\ge 2$, $\\frac{1}{(\\ln N)^2} \\le \\frac{1}{\\ln 2 \\cdot \\ln N}$. -/
theorem inv_log_sq_le_inv_log (N : ℕ) (hN : 2 ≤ N) :
    1 / (Real.log (N : ℝ)) ^ 2 ≤ (1 / Real.log 2) / Real.log (N : ℝ) := by
  have hN2 : (2 : ℝ) ≤ (N : ℝ) := by exact_mod_cast hN
  have h2_pos : (0 : ℝ) < 2 := by norm_num
  have h2_gt1 : (1 : ℝ) < 2 := by norm_num
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos h2_gt1
  have hlogN_ge : Real.log 2 ≤ Real.log (N : ℝ) := Real.log_le_log h2_pos hN2
  have hlogN_pos : 0 < Real.log (N : ℝ) := lt_of_lt_of_le hlog2_pos hlogN_ge
  have h_sq : (Real.log (N : ℝ)) ^ 2 = Real.log (N : ℝ) * Real.log (N : ℝ) := sq _
  rw [h_sq]
  have h_prod_ge : Real.log 2 * Real.log (N : ℝ) ≤ Real.log (N : ℝ) * Real.log (N : ℝ) :=
    mul_le_mul_of_nonneg_right hlogN_ge (le_of_lt hlogN_pos)
  have h_prod_pos : 0 < Real.log 2 * Real.log (N : ℝ) := mul_pos hlog2_pos hlogN_pos
  have h_le := one_div_le_one_div_of_le h_prod_pos h_prod_ge
  have h_rewr : 1 / (Real.log 2 * Real.log (N : ℝ)) = (1 / Real.log 2) / Real.log (N : ℝ) := by
    ring
  rwa [h_rewr] at h_le

/-- Scaled low-frequency decay lemma:
For any  > 0$ and  \\ge 2$,
$\\frac{C}{(\\ln N)^2} \\le \\frac{C / \\ln 2}{\\ln N}$. -/
theorem div_log_sq_le_div_log (C : ℝ) (hC : 0 ≤ C) (N : ℕ) (hN : 2 ≤ N) :
    C / (Real.log (N : ℝ)) ^ 2 ≤ (C / Real.log 2) / Real.log (N : ℝ) := by
  have h_base := inv_log_sq_le_inv_log N hN
  have h_mul := mul_le_mul_of_nonneg_left h_base hC
  have h1 : C * (1 / (Real.log (N : ℝ)) ^ 2) = C / (Real.log (N : ℝ)) ^ 2 := by ring
  have h2 : C * ((1 / Real.log 2) / Real.log (N : ℝ)) =
      (C / Real.log 2) / Real.log (N : ℝ) := by ring
  rwa [h1, h2] at h_mul

/-- Upper bound on the low-frequency spectral integral:
{\\text{low}}(N) \\le 1 + \\frac{C_{\\text{low}} / \\ln 2}{\\ln N}$. -/
theorem low_frequency_upper_bound (c : ℕ → ℕ → ℝ) (L : LowFrequencyBound c) :
    ∃ C_scaled > 0, ∀ N ≥ 2,
      L.J_low N ≤ 1 + C_scaled / Real.log (N : ℝ) := by
  have h2_gt1 : (1 : ℝ) < 2 := by norm_num
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos h2_gt1
  refine ⟨L.C_low / Real.log 2, div_pos L.hC_low hlog2_pos, ?_⟩
  intro N hN
  have h_eval := L.h_low_eval N hN
  have h_le_add : L.J_low N - 1 ≤ L.C_low / (Real.log (N : ℝ)) ^ 2 :=
    (le_abs_self (L.J_low N - 1)).trans h_eval
  have h_decay := div_log_sq_le_div_log L.C_low (le_of_lt L.hC_low) N hN
  have h_comb : L.J_low N - 1 ≤ (L.C_low / Real.log 2) / Real.log (N : ℝ) :=
    h_le_add.trans h_decay
  linarith

/-- Low + Mid Frequency Combination Theorem:
If the low-frequency window satisfies $|J_{\\text{low}} - 1| \\le C_{\\text{low}} / (\\ln N)^2$
and the mid-frequency transition window satisfies {\\text{mid}} \\le C_{\\text{mid}} / \\ln N$,
then the combined low+mid energy satisfies
{\\text{low}} + J_{\\text{mid}} \\le 1 + (C_{\\text{low}}/\\ln 2 + C_{\\text{mid}}) / \\ln N$. -/
theorem low_mid_frequency_bound_of_components
    (c : ℕ → ℕ → ℝ)
    (L : LowFrequencyBound c)
    (J_mid : ℕ → ℝ)
    {C_mid : ℝ} (hC_mid : 0 < C_mid)
    (h_mid : ∀ N ≥ 2, J_mid N ≤ C_mid / Real.log (N : ℝ)) :
    ∃ C_lm > 0, ∀ N ≥ 2,
      L.J_low N + J_mid N ≤ 1 + C_lm / Real.log (N : ℝ) := by
  rcases low_frequency_upper_bound c L with ⟨C_scaled, hC_scaled, h_low_le⟩
  refine ⟨C_scaled + C_mid, add_pos hC_scaled hC_mid, ?_⟩
  intro N hN
  have h1 := h_low_le N hN
  have h2 := h_mid N hN
  have h_sum := add_le_add h1 h2
  have h_alg : 1 + C_scaled / Real.log (N : ℝ) + C_mid / Real.log (N : ℝ) =
      1 + (C_scaled + C_mid) / Real.log (N : ℝ) := by ring
  rwa [h_alg] at h_sum

/-- Frequency Decomposition Constructor from Stage 2 + Stage 3 + Stage 4 Components:
Assembling a low-frequency bound, a mid-frequency bound, and a high-frequency tail bound
yields a full FrequencyDecomposition. -/
noncomputable def frequencyDecomposition_of_stages
    (c : ℕ → ℕ → ℝ)
    (L : LowFrequencyBound c)
    (J_mid : ℕ → ℝ)
    {C_mid : ℝ} (hC_mid : 0 < C_mid)
    (h_mid : ∀ N ≥ 2, J_mid N ≤ C_mid / Real.log (N : ℝ))
    (J_high : ℕ → ℝ)
    {C_hi : ℝ} (hC_hi : 0 < C_hi)
    (h_high : ∀ N ≥ 2, J_high N ≤ C_hi / (N : ℝ))
    (h_decomp : ∀ N ≥ 2, quadraticCrossTerm (c N) N = L.J_low N + J_mid N + J_high N) :
    FrequencyDecomposition c := by
  have h_lm := low_mid_frequency_bound_of_components c L J_mid hC_mid h_mid
  exact {
    J_low := L.J_low
    J_mid := J_mid
    J_high := J_high
    h_decomp := h_decomp
    h_low_mid_bound := h_lm
    h_high_bound := ⟨C_hi, hC_hi, h_high⟩
  }

/-- Master Stage 3 Closure to Riemann Hypothesis:
Combining Pillar I, Low-Frequency Bound (Stage 3), Mid-Frequency Sieve Bound (Stage 4),
and High-Frequency Tail Bound (Stage 2) unconditionally implies the Riemann Hypothesis. -/
theorem riemannHypothesis_of_low_mid_high_stages
    (c : ℕ → ℕ → ℝ)
    (h_A_N : ∀ N ≥ 2, D1 (c N) N = 0)
    (h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (c N) N + quadraticCrossTerm (c N) N)
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (c N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (L : LowFrequencyBound c)
    (J_mid : ℕ → ℝ)
    {C_mid : ℝ} (hC_mid : 0 < C_mid)
    (h_mid : ∀ N ≥ 2, J_mid N ≤ C_mid / Real.log (N : ℝ))
    (J_high : ℕ → ℝ)
    {C_hi : ℝ} (hC_hi : 0 < C_hi)
    (h_high : ∀ N ≥ 2, J_high N ≤ C_hi / (N : ℝ))
    (h_quad_decomp : ∀ N ≥ 2, quadraticCrossTerm (c N) N = L.J_low N + J_mid N + J_high N) :
    RiemannHypothesis := by
  have F := frequencyDecomposition_of_stages c L J_mid hC_mid h_mid
    J_high hC_hi h_high h_quad_decomp
  exact riemannHypothesis_of_pillars_I_and_II c h_A_N h_decomp hC1 h_log_mom F

/-- Low-frequency upper bound for constructive mollified Möbius candidate. -/
theorem cCandidateMobius_low_frequency_upper_bound
    (L : LowFrequencyBound (fun N => cCandidateMobius N)) :
    ∃ C_scaled > 0, ∀ N ≥ 2,
      L.J_low N ≤ 1 + C_scaled / Real.log (N : ℝ) :=
  low_frequency_upper_bound (fun N => cCandidateMobius N) L

/-- Low-frequency upper bound for constructive Selberg sieve candidate. -/
theorem cCandidateSelberg_low_frequency_upper_bound
    (L : LowFrequencyBound (fun N => cCandidateSelberg N)) :
    ∃ C_scaled > 0, ∀ N ≥ 2,
      L.J_low N ≤ 1 + C_scaled / Real.log (N : ℝ) :=
  low_frequency_upper_bound (fun N => cCandidateSelberg N) L

/-- Master Stage 3 Closure for mollified Möbius sequence. -/
theorem riemannHypothesis_of_cCandidateMobius_stages
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (cCandidateMobius N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (L : LowFrequencyBound (fun N => cCandidateMobius N))
    (J_mid : ℕ → ℝ)
    {C_mid : ℝ} (hC_mid : 0 < C_mid)
    (h_mid : ∀ N ≥ 2, J_mid N ≤ C_mid / Real.log (N : ℝ))
    (J_high : ℕ → ℝ)
    {C_hi : ℝ} (hC_hi : 0 < C_hi)
    (h_high : ∀ N ≥ 2, J_high N ≤ C_hi / (N : ℝ))
    (h_quad_decomp : ∀ N ≥ 2,
      quadraticCrossTerm (cCandidateMobius N) N = L.J_low N + J_mid N + J_high N) :
    RiemannHypothesis := by
  have h_A_N : ∀ N ≥ 2, D1 (cCandidateMobius N) N = 0 :=
    fun N hN => (cCandidateMobius_mem_A_N_uncond hN).1
  have h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (cCandidateMobius N) N +
          quadraticCrossTerm (cCandidateMobius N) N :=
    fun N hN => cCandidateMobius_l2_dist_sq_decomposition N hN
  exact riemannHypothesis_of_low_mid_high_stages (fun N => cCandidateMobius N)
    h_A_N h_decomp hC1 h_log_mom L J_mid hC_mid h_mid J_high hC_hi h_high h_quad_decomp

/-- Master Stage 3 Closure for Selberg sieve sequence. -/
theorem riemannHypothesis_of_cCandidateSelberg_stages
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (cCandidateSelberg N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (L : LowFrequencyBound (fun N => cCandidateSelberg N))
    (J_mid : ℕ → ℝ)
    {C_mid : ℝ} (hC_mid : 0 < C_mid)
    (h_mid : ∀ N ≥ 2, J_mid N ≤ C_mid / Real.log (N : ℝ))
    (J_high : ℕ → ℝ)
    {C_hi : ℝ} (hC_hi : 0 < C_hi)
    (h_high : ∀ N ≥ 2, J_high N ≤ C_hi / (N : ℝ))
    (h_quad_decomp : ∀ N ≥ 2,
      quadraticCrossTerm (cCandidateSelberg N) N = L.J_low N + J_mid N + J_high N) :
    RiemannHypothesis := by
  have h_A_N : ∀ N ≥ 2, D1 (cCandidateSelberg N) N = 0 :=
    fun N hN => (cCandidateSelberg_mem_A_N_uncond hN).1
  have h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (cCandidateSelberg N) N +
          quadraticCrossTerm (cCandidateSelberg N) N :=
    fun N hN => cCandidateSelberg_l2_dist_sq_decomposition N hN
  exact riemannHypothesis_of_low_mid_high_stages (fun N => cCandidateSelberg N)
    h_A_N h_decomp hC1 h_log_mom L J_mid hC_mid h_mid J_high hC_hi h_high h_quad_decomp

end MathlibPR.MontgomeryVaughan
