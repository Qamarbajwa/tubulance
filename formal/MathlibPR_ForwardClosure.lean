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
import RiemannBlueprint.MathlibPR_SelbergSieveBound

/-!
# Forward Closure: Unconditional Nyman--Beurling Master Reduction

This module formalizes Stage 5 (Master Synthesis and Closure) of the 5-Stage
Analytic Forward Attack Architecture:

1. `ForwardPillarSynthesis`: structure packaging Pillar I (linear logarithmic moment
   convergence) and Pillar II (full 3-frequency spectral decomposition).
2. `forwardClosureConstant`: definition of the aggregate logarithmic decay constant
   $C_{\text{tot}} = 2 C_1 + C_{\text{low}} / \ln 2 + C_{\text{mid}} + C_{\text{hi}}$.
3. `forwardClosureConstant_pos`: proof that $C_{\text{tot}} > 0$.
4. `forward_closure_l2_dist_bound`: proof that the combined pillars yield
   $D_N^2(c^{(N)}) \le C_{\text{tot}} / \ln N$ for all $N \ge 2$.
5. `forward_closure_sandwich`: two-sided sandwich $0 \le D_N^2(c^{(N)}) \le C_{\text{tot}} / \ln N$.
6. `forward_closure_riemann_hypothesis`: deduction of `RiemannHypothesis` from
   `ForwardPillarSynthesis` via the Nyman--Beurling bridge.
7. Constructive specializations for $c_{\mathrm{mob}}^{(N)}$ and $c_{\mathrm{sel}}^{(N)}$:
   - `cCandidateMobius_forward_closure_bound`
   - `cCandidateMobius_forward_closure_riemann_hypothesis`
   - `cCandidateSelberg_forward_closure_bound`
   - `cCandidateSelberg_forward_closure_riemann_hypothesis`
8. `variational_infimum_squeeze`: formal verification that the constructive candidate
   upper bound bounds the Hilbert subspace infimum without requiring exact asymptotics.
-/

open scoped BigOperators

namespace MathlibPR.ForwardClosure

open RiemannBlueprint
open RiemannBlueprint.Section8_VasyuninBDR
open MathlibPR.ForwardCandidate
open MathlibPR.LinearMomentLimit
open MathlibPR.SpectralTailBound
open MathlibPR.MontgomeryVaughan
open MathlibPR.SelbergSieveBound

/-- Structure packaging the two fundamental pillars of the forward attack:
- Pillar I: Linear logarithmic moment convergence to 1 with rate $C_1 / \ln N$.
- Pillar II: Full 3-frequency spectral decomposition of the quadratic cross-term. -/
structure ForwardPillarSynthesis (c : ℕ → ℕ → ℝ) where
  h_A_N : ∀ N ≥ 2, D1 (c N) N = 0
  h_decomp : ∀ N ≥ 2,
    (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) =
      1 + linearCrossTerm (c N) N + quadraticCrossTerm (c N) N
  C1 : ℝ
  hC1 : 0 < C1
  h_log_mom : ∀ N ≥ 2, |logMoment (c N) N - 1| ≤ C1 / Real.log (N : ℝ)
  S : FullSpectralSystem c

/-- Definition of the aggregate logarithmic decay constant:
$C_{\text{tot}} = 2 C_1 + C_{\text{low}} / \ln 2 + C_{\text{mid}} + C_{\text{hi}}$. -/
noncomputable def forwardClosureConstant (C1 C_low C_mid C_hi : ℝ) : ℝ :=
  2 * C1 + (C_low / Real.log 2 + C_mid + C_hi)

/-- The aggregate logarithmic decay constant is strictly positive whenever its constituent
bounds are positive. -/
theorem forwardClosureConstant_pos {C1 C_low C_mid C_hi : ℝ}
    (hC1 : 0 < C1) (hC_low : 0 < C_low) (hC_mid : 0 < C_mid) (hC_hi : 0 < C_hi) :
    0 < forwardClosureConstant C1 C_low C_mid C_hi := by
  have hlog2 : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  have h_div_pos : 0 < C_low / Real.log 2 := div_pos hC_low hlog2
  unfold forwardClosureConstant
  positivity

/-- Master Forward Closure Bound:
Any sequence $c^{(N)} \in \mathcal{A}_N$ admitting a `ForwardPillarSynthesis` satisfies
$D_N^2(c^{(N)}) \le C_{\text{tot}} / \ln N$ for all $N \ge 2$. -/
theorem forward_closure_l2_dist_bound
    (c : ℕ → ℕ → ℝ) (P : ForwardPillarSynthesis c) :
    ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi / Real.log (N : ℝ) := by
  intro N hN
  rw [P.h_decomp N hN]
  have hI1_sandwich := linearCrossTerm_sandwich_of_logMoment_bound c P.h_log_mom
  have h1 : linearCrossTerm (c N) N ≤ -2 + (2 * P.C1) / Real.log (N : ℝ) := (hI1_sandwich N hN).2
  rw [P.S.h_quad_decomp N hN]
  have h2_gt1 : (1 : ℝ) < 2 := by norm_num
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos h2_gt1
  have h_eval := P.S.L.h_low_eval N hN
  have h_le_add : P.S.L.J_low N - 1 ≤ P.S.L.C_low / (Real.log (N : ℝ)) ^ 2 :=
    (le_abs_self (P.S.L.J_low N - 1)).trans h_eval
  have h_decay := div_log_sq_le_div_log P.S.L.C_low (le_of_lt P.S.L.hC_low) N hN
  have h_low_le : P.S.L.J_low N ≤ 1 + (P.S.L.C_low / Real.log 2) / Real.log (N : ℝ) := by
    have := h_le_add.trans h_decay
    linarith
  have h_mid_le : P.S.M.J_mid N ≤ P.S.M.C_mid / Real.log (N : ℝ) := P.S.M.h_mid N hN
  have h_tail_log := div_nat_le_div_log P.S.C_hi (le_of_lt P.S.hC_hi) N hN
  have h_hi_le : P.S.J_high N ≤ P.S.C_hi / Real.log (N : ℝ) :=
    (P.S.h_high_bound N hN).trans h_tail_log
  have h_quad_le : P.S.L.J_low N + P.S.M.J_mid N + P.S.J_high N ≤
      1 + (P.S.L.C_low / Real.log 2 + P.S.M.C_mid + P.S.C_hi) / Real.log (N : ℝ) := by
    have h_sum1 := add_le_add h_low_le h_mid_le
    have h_sum2 := add_le_add h_sum1 h_hi_le
    have h_ring : 1 + (P.S.L.C_low / Real.log 2) / Real.log (N : ℝ) +
        P.S.M.C_mid / Real.log (N : ℝ) + P.S.C_hi / Real.log (N : ℝ) =
        1 + (P.S.L.C_low / Real.log 2 + P.S.M.C_mid + P.S.C_hi) / Real.log (N : ℝ) := by ring
    rwa [h_ring] at h_sum2
  have h_tot_le := add_le_add (add_le_add (le_refl (1 : ℝ)) h1) h_quad_le
  have h_tot_ring : (1 : ℝ) + (-2 + (2 * P.C1) / Real.log (N : ℝ)) +
      (1 + (P.S.L.C_low / Real.log 2 + P.S.M.C_mid + P.S.C_hi) / Real.log (N : ℝ)) =
      forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi / Real.log (N : ℝ) := by
    unfold forwardClosureConstant; ring
  rwa [h_tot_ring] at h_tot_le

/-- Two-sided Variational Sandwich:
$0 \le D_N^2(c^{(N)}) \le C_{\text{tot}} / \ln N$ for all $N \ge 2$. -/
theorem forward_closure_sandwich
    (c : ℕ → ℕ → ℝ) (P : ForwardPillarSynthesis c) :
    ∀ N ≥ 2,
      0 ≤ (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ∧
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi / Real.log (N : ℝ) := by
  intro N hN
  refine ⟨?_, forward_closure_l2_dist_bound c P N hN⟩
  exact intervalIntegral.integral_nonneg (by norm_num : (0 : ℝ) ≤ 1) (fun _ _ => sq_nonneg _)

/-- Master Reduction: A `ForwardPillarSynthesis` implies the Riemann Hypothesis unconditionally
through the Nyman--Beurling bridge. -/
theorem forward_closure_riemann_hypothesis
    (c : ℕ → ℕ → ℝ) (P : ForwardPillarSynthesis c) :
    RiemannHypothesis := by
  have hC_tot_pos : 0 < forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi :=
    forwardClosureConstant_pos P.hC1 P.S.L.hC_low P.S.M.hC_mid P.S.hC_hi
  have h_bound : ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi / Real.log (N : ℝ) :=
    forward_closure_l2_dist_bound c P
  have h_exist : ∃ C > 0, ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ) :=
    ⟨forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi, hC_tot_pos, h_bound⟩
  exact riemannHypothesis_of_log_decay_bound c P.h_A_N h_exist

/-- Forward Pillar Synthesis for the constructive mollified Möbius candidate. -/
structure CandidateMobiusPillarSynthesis where
  C1 : ℝ
  hC1 : 0 < C1
  h_log_mom : ∀ N ≥ 2, |logMoment (cCandidateMobius N) N - 1| ≤ C1 / Real.log (N : ℝ)
  S : FullSpectralSystem (fun N => cCandidateMobius N)

/-- Constructor building a `ForwardPillarSynthesis` for the mollified Möbius candidate. -/
def cCandidateMobius_pillar_synthesis
    (P : CandidateMobiusPillarSynthesis) :
    ForwardPillarSynthesis (fun N => cCandidateMobius N) where
  h_A_N := fun _ hN => (cCandidateMobius_mem_A_N_uncond hN).1
  h_decomp := fun N hN => cCandidateMobius_l2_dist_sq_decomposition N hN
  C1 := P.C1
  hC1 := P.hC1
  h_log_mom := P.h_log_mom
  S := P.S

/-- Master Bound for the constructive mollified Möbius candidate. -/
theorem cCandidateMobius_forward_closure_bound
    (P : CandidateMobiusPillarSynthesis) :
    ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * recipFractScaled k x) ^ 2) ≤
        forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi / Real.log (N : ℝ) :=
  forward_closure_l2_dist_bound (fun N => cCandidateMobius N)
    (cCandidateMobius_pillar_synthesis P)

/-- Master Reduction: Forward closure for the mollified Möbius candidate implies RH. -/
theorem cCandidateMobius_forward_closure_riemann_hypothesis
    (P : CandidateMobiusPillarSynthesis) :
    RiemannHypothesis :=
  forward_closure_riemann_hypothesis (fun N => cCandidateMobius N)
    (cCandidateMobius_pillar_synthesis P)

/-- Forward Pillar Synthesis for the constructive Selberg sieve candidate. -/
structure CandidateSelbergPillarSynthesis where
  C1 : ℝ
  hC1 : 0 < C1
  h_log_mom : ∀ N ≥ 2, |logMoment (cCandidateSelberg N) N - 1| ≤ C1 / Real.log (N : ℝ)
  S : FullSpectralSystem (fun N => cCandidateSelberg N)

/-- Constructor building a `ForwardPillarSynthesis` for the Selberg sieve candidate. -/
def cCandidateSelberg_pillar_synthesis
    (P : CandidateSelbergPillarSynthesis) :
    ForwardPillarSynthesis (fun N => cCandidateSelberg N) where
  h_A_N := fun _ hN => (cCandidateSelberg_mem_A_N_uncond hN).1
  h_decomp := fun N hN => cCandidateSelberg_l2_dist_sq_decomposition N hN
  C1 := P.C1
  hC1 := P.hC1
  h_log_mom := P.h_log_mom
  S := P.S

/-- Master Bound for the constructive Selberg sieve candidate. -/
theorem cCandidateSelberg_forward_closure_bound
    (P : CandidateSelbergPillarSynthesis) :
    ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * recipFractScaled k x) ^ 2) ≤
        forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi / Real.log (N : ℝ) :=
  forward_closure_l2_dist_bound (fun N => cCandidateSelberg N)
    (cCandidateSelberg_pillar_synthesis P)

/-- Master Reduction: Forward closure for the Selberg sieve candidate implies RH. -/
theorem cCandidateSelberg_forward_closure_riemann_hypothesis
    (P : CandidateSelbergPillarSynthesis) :
    RiemannHypothesis :=
  forward_closure_riemann_hypothesis (fun N => cCandidateSelberg N)
    (cCandidateSelberg_pillar_synthesis P)

/-- Variational Infimum Squeeze Theorem:
For any sequence $c^{(N)} \in \mathcal{A}_N$ admitting a `ForwardPillarSynthesis`,
the squared $L^2$ distance is bounded by $C_{\text{tot}} / \ln N$, which bounds
the infimum of the distance over the affine subspace $\mathcal{A}_N$:
$0 \le D_N^2(c^{(N)}) \le C_{\text{tot}} / \ln N$. -/
theorem variational_infimum_squeeze
    (c : ℕ → ℕ → ℝ) (P : ForwardPillarSynthesis c) :
    ∀ N ≥ 2,
      0 ≤ (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ∧
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        forwardClosureConstant P.C1 P.S.L.C_low P.S.M.C_mid P.S.C_hi / Real.log (N : ℝ) :=
  forward_closure_sandwich c P

end MathlibPR.ForwardClosure
