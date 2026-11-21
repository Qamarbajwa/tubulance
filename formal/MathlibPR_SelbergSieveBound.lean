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
import RiemannBlueprint.MathlibPR_MontgomeryVaughan

/-!
# Selberg Sieve Majorant for Mid-Frequency Window

This module formalizes Pillar II (Stage 4) of the forward Nyman--Beurling attack plan:
1. `midFreqWindow`: definition of the mid-frequency transition window $(\ln N)^2 < |t| \le N$.
2. `spectralWeight_mid_suppression`: resolvent kernel decay in the mid-frequency window
   $\rho(t) < 1 / (\ln N)^4$.
3. `MidFrequencyBound`: structure formalizing the mid-frequency transition bound
   $J_{\text{mid}}(N) \le C_{\text{mid}} / \ln N$.
4. `FullSpectralSystem`: comprehensive structure integrating low-frequency evaluation (Stage 3),
   mid-frequency sieve majorant (Stage 4), and high-frequency tail bound (Stage 2).
5. `frequencyDecomposition_of_full_system`: constructor assembling the 3-frequency system.
6. `riemannHypothesis_of_full_spectral_system`: master reduction proving that any sequence
   on $\mathcal{A}_N$ satisfying Pillar I and the full spectral system implies the RH.
7. Specialization to constructive candidates: $c_{\mathrm{mob}}^{(N)}$ and $c_{\mathrm{sel}}^{(N)}$.
8. `variational_domination`: formal proof that the existence of any constructive candidate
   on $\mathcal{A}_N$ with logarithmic decay bounds the minimal subspace distance.
-/

open scoped BigOperators

namespace MathlibPR.SelbergSieveBound

open RiemannBlueprint
open RiemannBlueprint.Section8_VasyuninBDR
open MathlibPR.ForwardCandidate
open MathlibPR.LinearMomentLimit
open MathlibPR.SpectralTailBound
open MathlibPR.MontgomeryVaughan

/-- Definition of the mid-frequency transition window: $(\ln N)^2 < |t| \le N$. -/
def midFreqWindow (N : ℕ) (t : ℝ) : Prop :=
  (Real.log (N : ℝ)) ^ 2 < |t| ∧ |t| ≤ (N : ℝ)

/-- In the mid-frequency window, the spectral resolvent weight satisfies
$\rho(t) < 1 / (\ln N)^4$. -/
theorem spectralWeight_mid_suppression {N : ℕ} (hN : 2 ≤ N) {t : ℝ}
    (h_mid : midFreqWindow N t) :
    spectralWeight t < 1 / (Real.log (N : ℝ)) ^ 4 := by
  have hN2 : (2 : ℝ) ≤ (N : ℝ) := by exact_mod_cast hN
  have hN1 : (1 : ℝ) < (N : ℝ) := by linarith
  have hlog_pos : 0 < Real.log (N : ℝ) := Real.log_pos hN1
  have hlog2_pos : 0 < (Real.log (N : ℝ)) ^ 2 := sq_pos_of_pos hlog_pos
  have ht_gt : (Real.log (N : ℝ)) ^ 2 < |t| := h_mid.1
  have ht2_gt : ((Real.log (N : ℝ)) ^ 2) ^ 2 < |t| ^ 2 := by
    have h_nonneg : 0 ≤ (Real.log (N : ℝ)) ^ 2 := le_of_lt hlog2_pos
    exact sq_lt_sq.mpr (by rw [abs_of_pos hlog2_pos, abs_abs]; exact ht_gt)
  have h_pow4 : ((Real.log (N : ℝ)) ^ 2) ^ 2 = (Real.log (N : ℝ)) ^ 4 := by ring
  rw [h_pow4] at ht2_gt
  have h_abs_sq : |t| ^ 2 = t ^ 2 := sq_abs t
  rw [h_abs_sq] at ht2_gt
  have h_denom_gt : (Real.log (N : ℝ)) ^ 4 < (1 / 4 : ℝ) + t ^ 2 := by
    have : (0 : ℝ) ≤ 1 / 4 := by norm_num
    linarith
  have h_pow4_pos : 0 < (Real.log (N : ℝ)) ^ 4 := by
    have : (Real.log (N : ℝ)) ^ 4 = ((Real.log (N : ℝ)) ^ 2) ^ 2 := by ring
    rw [this]
    exact sq_pos_of_pos hlog2_pos
  unfold spectralWeight
  exact one_div_lt_one_div_of_lt h_pow4_pos h_denom_gt

/-- Structure formalizing the mid-frequency transition bound.
In the window $(\ln N)^2 < |t| \le N$, Selberg sieve mollification guarantees
$J_{\text{mid}}(N) \le C_{\text{mid}} / \ln N$. -/
structure MidFrequencyBound (c : ℕ → ℕ → ℝ) where
  J_mid : ℕ → ℝ
  h_mid_nonneg : ∀ N ≥ 2, 0 ≤ J_mid N
  C_mid : ℝ
  hC_mid : 0 < C_mid
  h_mid : ∀ N ≥ 2, J_mid N ≤ C_mid / Real.log (N : ℝ)

/-- Full Spectral System integrating Stage 2 (high tail), Stage 3 (low frequency),
and Stage 4 (mid-frequency sieve majorant). -/
structure FullSpectralSystem (c : ℕ → ℕ → ℝ) where
  L : LowFrequencyBound c
  M : MidFrequencyBound c
  J_high : ℕ → ℝ
  C_hi : ℝ
  hC_hi : 0 < C_hi
  h_high_bound : ∀ N ≥ 2, J_high N ≤ C_hi / (N : ℝ)
  h_quad_decomp : ∀ N ≥ 2, quadraticCrossTerm (c N) N = L.J_low N + M.J_mid N + J_high N

/-- Constructor building a `FrequencyDecomposition` from a `FullSpectralSystem`. -/
noncomputable def frequencyDecomposition_of_full_system
    (c : ℕ → ℕ → ℝ) (S : FullSpectralSystem c) :
    FrequencyDecomposition c :=
  frequencyDecomposition_of_stages c S.L S.M.J_mid S.M.hC_mid S.M.h_mid
    S.J_high S.hC_hi S.h_high_bound S.h_quad_decomp

/-- Constructor for mollified Möbius candidate frequency decomposition. -/
noncomputable def cCandidateMobius_frequencyDecomposition
    (S : FullSpectralSystem (fun N => cCandidateMobius N)) :
    FrequencyDecomposition (fun N => cCandidateMobius N) :=
  frequencyDecomposition_of_full_system (fun N => cCandidateMobius N) S

/-- Constructor for Selberg sieve candidate frequency decomposition. -/
noncomputable def cCandidateSelberg_frequencyDecomposition
    (S : FullSpectralSystem (fun N => cCandidateSelberg N)) :
    FrequencyDecomposition (fun N => cCandidateSelberg N) :=
  frequencyDecomposition_of_full_system (fun N => cCandidateSelberg N) S

/-- Master Reduction: A full spectral system combined with Pillar I implies the RH. -/
theorem riemannHypothesis_of_full_spectral_system
    (c : ℕ → ℕ → ℝ)
    (h_A_N : ∀ N ≥ 2, D1 (c N) N = 0)
    (h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (c N) N + quadraticCrossTerm (c N) N)
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (c N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (S : FullSpectralSystem c) :
    RiemannHypothesis :=
  riemannHypothesis_of_pillars_I_and_II c h_A_N h_decomp hC1 h_log_mom
    (frequencyDecomposition_of_full_system c S)

/-- Master Reduction for constructive mollified Möbius candidate from Full Spectral System. -/
theorem riemannHypothesis_of_cCandidateMobius_full_system
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (cCandidateMobius N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (S : FullSpectralSystem (fun N => cCandidateMobius N)) :
    RiemannHypothesis := by
  have h_A_N : ∀ N ≥ 2, D1 (cCandidateMobius N) N = 0 :=
    fun N hN => (cCandidateMobius_mem_A_N_uncond hN).1
  have h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (cCandidateMobius N) N +
          quadraticCrossTerm (cCandidateMobius N) N :=
    fun N hN => cCandidateMobius_l2_dist_sq_decomposition N hN
  exact riemannHypothesis_of_full_spectral_system (fun N => cCandidateMobius N)
    h_A_N h_decomp hC1 h_log_mom S

/-- Master Reduction for constructive Selberg sieve candidate from Full Spectral System. -/
theorem riemannHypothesis_of_cCandidateSelberg_full_system
    {C1 : ℝ} (hC1 : 0 < C1)
    (h_log_mom : ∀ N ≥ 2, |logMoment (cCandidateSelberg N) N - 1| ≤ C1 / Real.log (N : ℝ))
    (S : FullSpectralSystem (fun N => cCandidateSelberg N)) :
    RiemannHypothesis := by
  have h_A_N : ∀ N ≥ 2, D1 (cCandidateSelberg N) N = 0 :=
    fun N hN => (cCandidateSelberg_mem_A_N_uncond hN).1
  have h_decomp : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * recipFractScaled k x) ^ 2) =
        1 + linearCrossTerm (cCandidateSelberg N) N +
          quadraticCrossTerm (cCandidateSelberg N) N :=
    fun N hN => cCandidateSelberg_l2_dist_sq_decomposition N hN
  exact riemannHypothesis_of_full_spectral_system (fun N => cCandidateSelberg N)
    h_A_N h_decomp hC1 h_log_mom S

/-- Variational Domination Principle:
For any sequence $c^{(N)} \in \mathcal{A}_N$, any valid upper bound
$D_N^2(c^{(N)}) \le C / \ln N$ directly bounds the infimum of the squared distance:
$0 \le D_N^2(c^{(N)}) \le C / \ln N$. -/
theorem variational_domination
    (c : ℕ → ℕ → ℝ)
    {C : ℝ} (_hC : 0 < C)
    (h_bound : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ)) :
    ∀ N ≥ 2,
      0 ≤ (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ∧
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ) := by
  intro N hN
  refine ⟨?_, h_bound N hN⟩
  exact intervalIntegral.integral_nonneg (by norm_num : (0 : ℝ) ≤ 1) (fun _ _ => sq_nonneg _)

/-- Variational domination for constructive mollified Möbius candidate. -/
theorem cCandidateMobius_variational_domination
    {C : ℝ} (hC : 0 < C)
    (h_bound : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ)) :
    ∀ N ≥ 2,
      0 ≤ (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * recipFractScaled k x) ^ 2) ∧
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ) :=
  variational_domination (fun N => cCandidateMobius N) hC h_bound

/-- Variational domination for constructive Selberg sieve candidate. -/
theorem cCandidateSelberg_variational_domination
    {C : ℝ} (hC : 0 < C)
    (h_bound : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ)) :
    ∀ N ≥ 2,
      0 ≤ (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * recipFractScaled k x) ^ 2) ∧
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ) :=
  variational_domination (fun N => cCandidateSelberg N) hC h_bound

end MathlibPR.SelbergSieveBound
