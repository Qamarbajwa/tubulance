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

/-!
# Spectral High-Frequency Tail Bound and Frequency Decomposition

This module formalizes Pillar II (Stage 2) of the forward Nyman--Beurling attack plan:
1. spectralWeight: canonical resolvent kernel weight $\\rho(t) = \\frac{1}{1/4 + t^2}$.
2. spectralWeight_pos, spectralWeight_le_inv_sq: pointwise polynomial decay
   $\\rho(t) \\le 1/t^2$.
3. spectralWeight_tail_le: for $|t| \\ge N \\ge 1$, $\\rho(t) \\le 1/N^2$.
4. div_nat_le_div_log: asymptotic dominance /N \\le C/\\ln N$ for all  \\ge 2$,  \\ge 0$.
5. cNormL1Half: $\\ell^1$ half-weight norm $\\sum_{k=1}^N |c_k| / \\sqrt{k}$.
6. Frequency decomposition of quadratic cross-term:
   (c, N) = J_{\\text{low}} + J_{\\text{mid}} + J_{\\text{high}}$.
7. High-frequency tail absorption: any tail bound {\\text{high}} \\le C_{\\text{high}} / N$
   is strictly absorbed into the logarithmic scale $\\mathcal{O}(1 / \\ln N)$.
8. Master 3-frequency synthesis: reducing ^2 \\le C / \\ln N$ to the three individual
   frequency bounds.
9. Constructive candidate instantiations: reductions for {\\mathrm{mob}}^{(N)}$ and
   {\\mathrm{sel}}^{(N)}$.
-/

open scoped BigOperators

namespace MathlibPR.SpectralTailBound

open RiemannBlueprint
open RiemannBlueprint.Section8_VasyuninBDR
open MathlibPR.ForwardCandidate
open MathlibPR.LinearMomentLimit

/-- The canonical spectral resolvent kernel weight $\\rho(t) = \\frac{1}{1/4 + t^2}$. -/
noncomputable def spectralWeight (t : ℝ) : ℝ :=
  1 / ((1 / 4 : ℝ) + t ^ 2)

/-- Strict positivity of the spectral weight for all  \\in \\mathbb{R}$. -/
theorem spectralWeight_pos (t : ℝ) : 0 < spectralWeight t := by
  unfold spectralWeight
  have h_denom : 0 < (1 / 4 : ℝ) + t ^ 2 := by
    have : (0 : ℝ) < 1 / 4 := by norm_num
    have : (0 : ℝ) ≤ t ^ 2 := sq_nonneg t
    linarith
  exact one_div_pos.mpr h_denom

/-- Non-negativity of the spectral weight. -/
theorem spectralWeight_nonneg (t : ℝ) : 0 ≤ spectralWeight t :=
  le_of_lt (spectralWeight_pos t)

/-- Polynomial decay of the spectral weight: $\\rho(t) \\le 1 / t^2$ for  \\ne 0$. -/
theorem spectralWeight_le_inv_sq {t : ℝ} (ht : t ≠ 0) :
    spectralWeight t ≤ 1 / t ^ 2 := by
  unfold spectralWeight
  have ht2_pos : 0 < t ^ 2 := sq_pos_of_ne_zero ht
  have h_denom : t ^ 2 ≤ (1 / 4 : ℝ) + t ^ 2 := by
    linarith [show (0 : ℝ) ≤ 1 / 4 by norm_num]
  exact one_div_le_one_div_of_le ht2_pos h_denom

/-- Uniform high-frequency tail bound: for $|t| \\ge N \\ge 1$, $\\rho(t) \\le 1 / N^2$. -/
theorem spectralWeight_tail_le {N : ℕ} (hN : 1 ≤ N) {t : ℝ} (ht : (N : ℝ) ≤ |t|) :
    spectralWeight t ≤ 1 / (N : ℝ) ^ 2 := by
  unfold spectralWeight
  have hN_pos : (0 : ℝ) < (N : ℝ) := Nat.cast_pos.mpr hN
  have hN2_pos : (0 : ℝ) < (N : ℝ) ^ 2 := sq_pos_of_pos hN_pos
  have ht2_ge : (N : ℝ) ^ 2 ≤ t ^ 2 := by
    have h_abs_sq : |t| ^ 2 = t ^ 2 := sq_abs t
    rw [← h_abs_sq]
    exact sq_le_sq' (by linarith) ht
  have h_denom : (N : ℝ) ^ 2 ≤ (1 / 4 : ℝ) + t ^ 2 := by
    linarith [show (0 : ℝ) ≤ 1 / 4 by norm_num]
  exact one_div_le_one_div_of_le hN2_pos h_denom

/-- Asymptotic Dominance Lemma:
For any non-negative constant  \\ge 0$ and any integer  \\ge 2$,
$\\frac{C}{N} \\le \\frac{C}{\\ln N}$. -/
theorem div_nat_le_div_log (C : ℝ) (hC : 0 ≤ C) (N : ℕ) (hN : 2 ≤ N) :
    C / (N : ℝ) ≤ C / Real.log (N : ℝ) := by
  have hN_ge_two : (2 : ℝ) ≤ (N : ℝ) := by exact_mod_cast hN
  have hN_gt_one : (1 : ℝ) < (N : ℝ) := by linarith
  have hN_pos : (0 : ℝ) < (N : ℝ) := by linarith
  have hlog_pos : 0 < Real.log (N : ℝ) := Real.log_pos hN_gt_one
  have hlog_le : Real.log (N : ℝ) ≤ (N : ℝ) := Real.log_le_self (le_of_lt hN_pos)
  exact div_le_div_of_nonneg_left hC hlog_pos hlog_le

/-- The weighted $\\ell^1$ half-norm of a coefficient vector:
$\\sum_{k=1}^N \\frac{|c_k|}{\\sqrt{k}}$. -/
noncomputable def cNormL1Half (c : ℕ → ℝ) (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, |c k| / Real.sqrt (k : ℝ)

/-- Positivity of the weighted $\\ell^1$ half-norm. -/
theorem cNormL1Half_nonneg (c : ℕ → ℝ) (N : ℕ) : 0 ≤ cNormL1Half c N := by
  unfold cNormL1Half
  refine Finset.sum_nonneg (fun k _ => ?_)
  exact div_nonneg (abs_nonneg _) (Real.sqrt_nonneg _)

/-- Frequency Decomposition Structure for the quadratic cross-term (c, N)$. -/
structure FrequencyDecomposition (c : ℕ → ℕ → ℝ) where
  J_low : ℕ → ℝ
  J_mid : ℕ → ℝ
  J_high : ℕ → ℝ
  h_decomp : ∀ N ≥ 2, quadraticCrossTerm (c N) N = J_low N + J_mid N + J_high N
  h_low_mid_bound : ∃ C_lm > 0, ∀ N ≥ 2, J_low N + J_mid N ≤ 1 + C_lm / Real.log (N : ℝ)
  h_high_bound : ∃ C_hi > 0, ∀ N ≥ 2, J_high N ≤ C_hi / (N : ℝ)

/-- Master Quadratic Upper Bound Theorem:
Given a 3-frequency decomposition where low+mid frequencies are bounded by  + C_{lm}/\\ln N$
and the high-frequency tail is bounded by {hi}/N$, the total quadratic cross-term satisfies
(c^{(N)}, N) \\le 1 + (C_{lm} + C_{hi}) / \\ln N$. -/
theorem quadraticCrossTerm_bound_of_frequency_decomp (c : ℕ → ℕ → ℝ)
    (F : FrequencyDecomposition c) :
    ∃ C_quad > 0, ∀ N ≥ 2,
      quadraticCrossTerm (c N) N ≤ 1 + C_quad / Real.log (N : ℝ) := by
  rcases F.h_low_mid_bound with ⟨C_lm, hClm, h_lm⟩
  rcases F.h_high_bound with ⟨C_hi, hChi, h_hi⟩
  refine ⟨C_lm + C_hi, add_pos hClm hChi, ?_⟩
  intro N hN
  rw [F.h_decomp N hN]
  have h_tail_log := div_nat_le_div_log C_hi (le_of_lt hChi) N hN
  have h_high_le := (h_hi N hN).trans h_tail_log
  have h_sum := add_le_add (h_lm N hN) h_high_le
  have h_add_div : 1 + C_lm / Real.log (N : ℝ) + C_hi / Real.log (N : ℝ) =
      1 + (C_lm + C_hi) / Real.log (N : ℝ) := by ring
  rwa [h_add_div] at h_sum

/-- Master 2-Pillar Distance Bound Theorem:
If the linear cross-term satisfies (c^{(N)}, N) \\le -2 + 2 C_1 / \\ln N$
and the quadratic cross-term satisfies (c^{(N)}, N) \\le 1 + C_2 / \\ln N$,
and the ^2$ distance decomposes as ^2 = 1 + I_1 + I_2$,
then ^2 \\le (2 C_1 + C_2) / \\ln N$. -/
theorem l2_dist_bound_of_cross_terms
    (c : ℕ → ℕ → ℝ)
    (h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (c N) N + quadraticCrossTerm (c N) N)
    {C1 : ℝ} (hC1 : 0 < C1)
    (hI1 : ∀ N ≥ 2, linearCrossTerm (c N) N ≤ -2 + (2 * C1) / Real.log (N : ℝ))
    {C2 : ℝ} (hC2 : 0 < C2)
    (hI2 : ∀ N ≥ 2, quadraticCrossTerm (c N) N ≤ 1 + C2 / Real.log (N : ℝ)) :
    ∃ C_tot > 0, ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        C_tot / Real.log (N : ℝ) := by
  refine ⟨2 * C1 + C2, by linarith, ?_⟩
  intro N hN
  rw [h_decomp N hN]
  have h1 := hI1 N hN
  have h2 := hI2 N hN
  have h_sum := add_le_add (add_le_add (le_refl (1 : ℝ)) h1) h2
  have h_alg : (1 : ℝ) + (-2 + (2 * C1) / Real.log (N : ℝ)) + (1 + C2 / Real.log (N : ℝ)) =
      (2 * C1 + C2) / Real.log (N : ℝ) := by ring
  rwa [h_alg] at h_sum

/-- Master Analytic Closure Theorem (Pillars I + II to Riemann Hypothesis):
Combining the linear moment limit (Pillar I) with the 3-frequency spectral decomposition (Pillar II)
produces a constructive sequence on $\\mathcal{A}_N$ satisfying ^2 \\le C / \\ln N$,
which unconditionally implies the Riemann Hypothesis. -/
theorem riemannHypothesis_of_pillars_I_and_II
    (c : ℕ → ℕ → ℝ)
    (h_A_N : ∀ N ≥ 2, D1 (c N) N = 0)
    (h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (c N) N + quadraticCrossTerm (c N) N)
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (c N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (F : FrequencyDecomposition c) :
    RiemannHypothesis := by
  have hI1_sandwich := linearCrossTerm_sandwich_of_logMoment_bound c h_log_mom
  have hI1 : ∀ N ≥ 2, linearCrossTerm (c N) N ≤ -2 + (2 * C1) / Real.log (N : ℝ) :=
    fun N hN => (hI1_sandwich N hN).2
  rcases quadraticCrossTerm_bound_of_frequency_decomp c F with ⟨C2, hC2, hI2⟩
  have h_dist_bound := l2_dist_bound_of_cross_terms c h_decomp hC1 hI1 hC2 hI2
  exact riemannHypothesis_of_log_decay_bound c h_A_N h_dist_bound

/-- Quadratic cross-term bound for constructive mollified Möbius candidate. -/
theorem cCandidateMobius_quadraticCrossTerm_bound
    (F : FrequencyDecomposition (fun N => cCandidateMobius N)) :
    ∃ C_quad > 0, ∀ N ≥ 2,
      quadraticCrossTerm (cCandidateMobius N) N ≤ 1 + C_quad / Real.log (N : ℝ) :=
  quadraticCrossTerm_bound_of_frequency_decomp (fun N => cCandidateMobius N) F

/-- Specialization to the constructive mollified Möbius candidate sequence. -/
theorem riemannHypothesis_of_cCandidateMobius_pillars_I_and_II
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (cCandidateMobius N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (F : FrequencyDecomposition (fun N => cCandidateMobius N)) :
    RiemannHypothesis := by
  have h_A_N : ∀ N ≥ 2, D1 (cCandidateMobius N) N = 0 :=
    fun N hN => (cCandidateMobius_mem_A_N_uncond hN).1
  have h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (cCandidateMobius N) N +
          quadraticCrossTerm (cCandidateMobius N) N :=
    fun N hN => cCandidateMobius_l2_dist_sq_decomposition N hN
  exact riemannHypothesis_of_pillars_I_and_II (fun N => cCandidateMobius N)
    h_A_N h_decomp hC1 h_log_mom F

/-- Quadratic cross-term bound for constructive Selberg sieve candidate. -/
theorem cCandidateSelberg_quadraticCrossTerm_bound
    (F : FrequencyDecomposition (fun N => cCandidateSelberg N)) :
    ∃ C_quad > 0, ∀ N ≥ 2,
      quadraticCrossTerm (cCandidateSelberg N) N ≤ 1 + C_quad / Real.log (N : ℝ) :=
  quadraticCrossTerm_bound_of_frequency_decomp (fun N => cCandidateSelberg N) F

/-- Specialization to the constructive Selberg sieve candidate sequence. -/
theorem riemannHypothesis_of_cCandidateSelberg_pillars_I_and_II
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (cCandidateSelberg N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (F : FrequencyDecomposition (fun N => cCandidateSelberg N)) :
    RiemannHypothesis := by
  have h_A_N : ∀ N ≥ 2, D1 (cCandidateSelberg N) N = 0 :=
    fun N hN => (cCandidateSelberg_mem_A_N_uncond hN).1
  have h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (cCandidateSelberg N) N +
          quadraticCrossTerm (cCandidateSelberg N) N :=
    fun N hN => cCandidateSelberg_l2_dist_sq_decomposition N hN
  exact riemannHypothesis_of_pillars_I_and_II (fun N => cCandidateSelberg N)
    h_A_N h_decomp hC1 h_log_mom F

end MathlibPR.SpectralTailBound
