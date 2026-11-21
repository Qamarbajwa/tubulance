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
import RiemannBlueprint.MathlibPR_ForwardCandidate

/-!
# Linear Moment Limit and Asymptotic Cross-Term Bounds on $\mathcal{A}_N$

This module formalizes Pillar I of the forward Nyman--Beurling attack plan:
1. `logMoment`: the pure logarithmic moment $M(c, N) = \sum_{k=1}^N c_k \frac{\ln k}{k}$.
2. `sumLogOverKsq` and `sumLogOverK`: auxiliary harmonic log sums and their positivity.
3. `projectAffine_logMoment`: exact closed-form algebraic decomposition of the projected
   logarithmic moment into the raw moment and the projection multiplier corrections:
   $M(\Pi_{\mathcal{A}_N}(u), N) = M(u, N) - \lambda_1(u, N) S_{\ln, 2}(N) -
   \lambda_0(u, N) S_{\ln, 1}(N)$.
4. `linearCrossTerm_eq_neg_two_mul_logMoment`: exact identity relating the linear energy
   against Vasyunin's kernel to $-2$ times the logarithmic moment on $\mathcal{A}_N$.
5. Squeeze and decay theorems establishing that whenever the logarithmic moment converges
   to $1$ with rate $\mathcal{O}(1 / \ln N)$, the linear cross-term $I_1(N)$ converges to $-2$
   with rate $\mathcal{O}(2C / \ln N)$:
   $-2 - \frac{2C}{\ln N} \le I_1(c^{(N)}, N) \le -2 + \frac{2C}{\ln N}$.
6. Specialization to the constructive mollified Möbius ($c_{\mathrm{mob}}^{(N)}$) and
   Selberg sieve ($c_{\mathrm{sel}}^{(N)}$) candidate families.
-/

open scoped BigOperators

namespace MathlibPR.LinearMomentLimit

open MathlibPR.ForwardCandidate

/-- The pure logarithmic moment of a sequence `c` on `[1, N]`:
  $M(c, N) = \sum_{k=1}^N c_k \frac{\ln k}{k}$. -/
noncomputable def logMoment (c : ℕ → ℝ) (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, c k * Real.log (k : ℝ) / (k : ℝ)

/-- Auxiliary logarithmic reciprocal square sum:
  $S_{\ln, 2}(N) = \sum_{k=1}^N \frac{\ln k}{k^2}$. -/
noncomputable def sumLogOverKsq (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, Real.log (k : ℝ) / ((k : ℝ) ^ 2)

/-- Auxiliary logarithmic reciprocal harmonic sum:
  $S_{\ln, 1}(N) = \sum_{k=1}^N \frac{\ln k}{k}$. -/
noncomputable def sumLogOverK (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, Real.log (k : ℝ) / (k : ℝ)

/-- Positivity of the logarithmic reciprocal square sum: $0 \le S_{\ln, 2}(N)$. -/
theorem sumLogOverKsq_nonneg (N : ℕ) : 0 ≤ sumLogOverKsq N := by
  unfold sumLogOverKsq
  refine Finset.sum_nonneg (fun k hk => ?_)
  have hk1 : 1 ≤ k := (Finset.mem_Icc.mp hk).1
  have hk_pos : 0 < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  have hlog_nonneg : 0 ≤ Real.log (k : ℝ) := Real.log_nonneg (by exact_mod_cast hk1)
  have hsq_pos : 0 < (k : ℝ) ^ 2 := sq_pos_of_pos hk_pos
  exact div_nonneg hlog_nonneg (le_of_lt hsq_pos)

/-- Positivity of the logarithmic reciprocal harmonic sum: $0 \le S_{\ln, 1}(N)$. -/
theorem sumLogOverK_nonneg (N : ℕ) : 0 ≤ sumLogOverK N := by
  unfold sumLogOverK
  refine Finset.sum_nonneg (fun k hk => ?_)
  have hk1 : 1 ≤ k := (Finset.mem_Icc.mp hk).1
  have hk_pos : 0 < (k : ℝ) := Nat.cast_pos.mpr (by omega)
  have hlog_nonneg : 0 ≤ Real.log (k : ℝ) := Real.log_nonneg (by exact_mod_cast hk1)
  exact div_nonneg hlog_nonneg (le_of_lt hk_pos)

/-- Algebraic Decomposition Theorem for Projected Logarithmic Moments:
For any raw sequence `u`, projecting onto $\mathcal{A}_N$ yields the exact decomposition:
$M(\Pi_{\mathcal{A}_N}(u), N) = M(u, N) - \lambda_1(u, N) S_{\ln, 2}(N) -
\lambda_0(u, N) S_{\ln, 1}(N)$. -/
theorem projectAffine_logMoment (u : ℕ → ℝ) (N : ℕ) :
    logMoment (projectAffine u N) N =
      logMoment u N -
      lambda1 u N * sumLogOverKsq N -
      lambda0 u N * sumLogOverK N := by
  unfold logMoment sumLogOverKsq sumLogOverK projectAffine
  have h_term : ∀ k ∈ Finset.Icc 1 N,
      (u k - lambda1 u N / (k : ℝ) - lambda0 u N) * Real.log (k : ℝ) / (k : ℝ) =
        u k * Real.log (k : ℝ) / (k : ℝ) -
        lambda1 u N * (Real.log (k : ℝ) / ((k : ℝ) ^ 2)) -
        lambda0 u N * (Real.log (k : ℝ) / (k : ℝ)) := by
    intro k hk
    have hk_ne : (k : ℝ) ≠ 0 := by
      have hk1 : 1 ≤ k := (Finset.mem_Icc.mp hk).1
      exact Nat.cast_ne_zero.mpr (by omega)
    have hk2_ne : (k : ℝ) ^ 2 ≠ 0 := pow_ne_zero 2 hk_ne
    ring
  rw [Finset.sum_congr rfl h_term]
  rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib]
  rw [← Finset.mul_sum, ← Finset.mul_sum]

/-- Deviation of the projected logarithmic moment from 1:
$M(\Pi(u), N) - 1 = (M(u, N) - 1) - \lambda_1 S_{\ln, 2} - \lambda_0 S_{\ln, 1}$. -/
theorem projectAffine_logMoment_sub_one (u : ℕ → ℝ) (N : ℕ) :
    logMoment (projectAffine u N) N - 1 =
      (logMoment u N - 1) -
      lambda1 u N * sumLogOverKsq N -
      lambda0 u N * sumLogOverK N := by
  rw [projectAffine_logMoment]
  ring

/-- Exact connection between the linear cross-term `linearCrossTerm c N` and `logMoment c N`:
  $I_1(c, N) = -2 * M(c, N)$. -/
theorem linearCrossTerm_eq_neg_two_mul_logMoment (c : ℕ → ℝ) (N : ℕ) :
    linearCrossTerm c N = - 2 * logMoment c N := by
  unfold linearCrossTerm logMoment
  ring

/-- Distance of the linear cross-term from its asymptotic limit $-2$:
  $I_1(c, N) - (-2) = -2 * (M(c, N) - 1)$. -/
theorem linearCrossTerm_sub_neg_two_eq (c : ℕ → ℝ) (N : ℕ) :
    linearCrossTerm c N - (-2) = - 2 * (logMoment c N - 1) := by
  rw [linearCrossTerm_eq_neg_two_mul_logMoment]
  ring

/-- Absolute error bound on the linear cross-term from a logarithmic moment bound:
if $|M(c, N) - 1| \le \varepsilon$, then $|I_1(c, N) - (-2)| \le 2 \varepsilon$. -/
theorem linearCrossTerm_dist_le_of_logMoment_dist_le (c : ℕ → ℝ) (N : ℕ) {ε : ℝ}
    (h : |logMoment c N - 1| ≤ ε) :
    |linearCrossTerm c N - (-2)| ≤ 2 * ε := by
  rw [linearCrossTerm_sub_neg_two_eq]
  rw [abs_mul, abs_neg, abs_of_pos (by norm_num : (0 : ℝ) < 2)]
  exact mul_le_mul_of_nonneg_left h (by norm_num)

/-- Logarithmic decay rate theorem for the linear cross-term:
If $|M(c^{(N)}, N) - 1| \le \frac{C}{\ln N}$ for all $N \ge 2$,
then $|I_1(c^{(N)}, N) - (-2)| \le \frac{2C}{\ln N}$ for all $N \ge 2$. -/
theorem linearCrossTerm_log_decay_of_logMoment_log_decay (c : ℕ → ℕ → ℝ) {C : ℝ}
    (h : ∀ (N : ℕ), 2 ≤ N → |logMoment (c N) N - 1| ≤ C / Real.log (N : ℝ)) :
    ∀ (N : ℕ), 2 ≤ N → |linearCrossTerm (c N) N - (-2)| ≤ (2 * C) / Real.log (N : ℝ) := by
  intro N hN
  have h_bound := linearCrossTerm_dist_le_of_logMoment_dist_le (c N) N (h N hN)
  have h_eq : 2 * (C / Real.log (N : ℝ)) = (2 * C) / Real.log (N : ℝ) := by ring
  rwa [h_eq] at h_bound

/-- Asymptotic Sandwich Bounds on the linear cross-term:
If the logarithmic moment satisfies the logarithmic decay bound, then
$-2 - \frac{2C}{\ln N} \le I_1(c^{(N)}, N) \le -2 + \frac{2C}{\ln N}$. -/
theorem linearCrossTerm_sandwich_of_logMoment_bound (c : ℕ → ℕ → ℝ) {C : ℝ}
    (h : ∀ (N : ℕ), 2 ≤ N → |logMoment (c N) N - 1| ≤ C / Real.log (N : ℝ)) :
    ∀ (N : ℕ), 2 ≤ N →
      - 2 - (2 * C) / Real.log (N : ℝ) ≤ linearCrossTerm (c N) N ∧
      linearCrossTerm (c N) N ≤ - 2 + (2 * C) / Real.log (N : ℝ) := by
  intro N hN
  have h_abs := linearCrossTerm_log_decay_of_logMoment_log_decay c h N hN
  have h_le := abs_le.mp h_abs
  constructor
  · linarith [h_le.1]
  · linarith [h_le.2]

/-- Specialized Moment Decomposition for the Mollified Möbius Candidate $c_{\mathrm{mob}}^{(N)}$:
$M(c_{\mathrm{mob}}^{(N)}, N) = M(u_{\mathrm{mob}}, N) - \lambda_1(u_{\mathrm{mob}}) S_{\ln, 2} -
\lambda_0(u_{\mathrm{mob}}) S_{\ln, 1}$. -/
theorem cCandidateMobius_logMoment_decomp (N : ℕ) :
    logMoment (cCandidateMobius N) N =
      logMoment (mollifiedMobius N) N -
      lambda1 (mollifiedMobius N) N * sumLogOverKsq N -
      lambda0 (mollifiedMobius N) N * sumLogOverK N :=
  projectAffine_logMoment (mollifiedMobius N) N

/-- Specialized Linear Cross-Term Bound for the Mollified Möbius Sequence:
whenever the mollified Möbius logarithmic moment achieves logarithmic decay,
$I_1(c_{\mathrm{mob}}^{(N)}, N)$ decays to $-2$ at rate $\frac{2C}{\ln N}$. -/
theorem cCandidateMobius_linearCrossTerm_log_decay {C : ℝ}
    (h : ∀ (N : ℕ), 2 ≤ N → |logMoment (cCandidateMobius N) N - 1| ≤ C / Real.log (N : ℝ)) :
    ∀ (N : ℕ), 2 ≤ N →
      |linearCrossTerm (cCandidateMobius N) N - (-2)| ≤ (2 * C) / Real.log (N : ℝ) :=
  linearCrossTerm_log_decay_of_logMoment_log_decay cCandidateMobius h

/-- Specialized Moment Decomposition for the Selberg Sieve Candidate $c_{\mathrm{sel}}^{(N)}$:
$M(c_{\mathrm{sel}}^{(N)}, N) = M(\lambda, N) - \lambda_1(\lambda) S_{\ln, 2} -
\lambda_0(\lambda) S_{\ln, 1}$. -/
theorem cCandidateSelberg_logMoment_decomp (N : ℕ) :
    logMoment (cCandidateSelberg N) N =
      logMoment (selbergSieveWeights N) N -
      lambda1 (selbergSieveWeights N) N * sumLogOverKsq N -
      lambda0 (selbergSieveWeights N) N * sumLogOverK N :=
  projectAffine_logMoment (selbergSieveWeights N) N

/-- Specialized Linear Cross-Term Bound for the Selberg Sieve Sequence:
whenever the Selberg sieve logarithmic moment achieves logarithmic decay,
$I_1(c_{\mathrm{sel}}^{(N)}, N)$ decays to $-2$ at rate $\frac{2C}{\ln N}$. -/
theorem cCandidateSelberg_linearCrossTerm_log_decay {C : ℝ}
    (h : ∀ (N : ℕ), 2 ≤ N → |logMoment (cCandidateSelberg N) N - 1| ≤ C / Real.log (N : ℝ)) :
    ∀ (N : ℕ), 2 ≤ N →
      |linearCrossTerm (cCandidateSelberg N) N - (-2)| ≤ (2 * C) / Real.log (N : ℝ) :=
  linearCrossTerm_log_decay_of_logMoment_log_decay cCandidateSelberg h

end MathlibPR.LinearMomentLimit
