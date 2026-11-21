/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.Real.Pi.Bounds
import RiemannBlueprint.Section8_VasyuninBDR
import RiemannBlueprint.MathlibPR_VasyuninCrossIntegral

/-!
# Constructive Candidate Sequences on the Báez-Duarte Affine Subspace

This module formalizes constructive candidate sequences $c^{(N)} \in \mathcal{A}_N$:
1. `DeltaDet`: the 2-constraint Gram determinant $\Delta(N) = N \sum 1/k^2 - (\sum 1/k)^2$.
2. `projectAffine`: closed-form Euclidean projection of any raw vector $u$ onto $\mathcal{A}_N$.
3. `projectAffine_D1` and `projectAffine_D0`: formal proof that $D_1 = 0$ and $D_0 = 2$.
4. `cCandidateMobius`: the explicit quadratic mollified Möbius candidate sequence.
5. `cCandidateMobius_mem_A_N`: proof that $c_{\mathrm{mob}}^{(N)} \in \mathcal{A}_N$.
6. `riemannHypothesis_of_cCandidateMobius_limit`: reduction of RH to the explicit candidate limit.
-/

open scoped BigOperators

namespace MathlibPR.ForwardCandidate

open RiemannBlueprint.Section8_VasyuninBDR

/-- Harmonic sum H(N) = ∑_{k=1}^N 1/k. -/
noncomputable def HSum (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, (1 : ℝ) / (k : ℝ)

/-- Square reciprocal sum S_2(N) = ∑_{k=1}^N 1/k^2. -/
noncomputable def S2Sum (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, (1 : ℝ) / ((k : ℝ) ^ 2)

/-- The constraint Gram determinant Δ(N) = N * S2Sum(N) - (HSum(N))^2. -/
noncomputable def DeltaDet (N : ℕ) : ℝ :=
  (N : ℝ) * S2Sum N - (HSum N) ^ 2

/-- Multiplier λ_1 for projecting a raw vector u onto A_N. -/
noncomputable def lambda1 (u : ℕ → ℝ) (N : ℕ) : ℝ :=
  ((N : ℝ) * (∑ k ∈ Finset.Icc 1 N, u k / (k : ℝ)) -
    HSum N * ((∑ k ∈ Finset.Icc 1 N, u k) - 2)) / DeltaDet N

/-- Multiplier λ_0 for projecting a raw vector u onto A_N. -/
noncomputable def lambda0 (u : ℕ → ℝ) (N : ℕ) : ℝ :=
  (S2Sum N * ((∑ k ∈ Finset.Icc 1 N, u k) - 2) -
    HSum N * (∑ k ∈ Finset.Icc 1 N, u k / (k : ℝ))) / DeltaDet N

/-- The exact Báez-Duarte affine projection of any raw vector u onto A_N:
  c(k) = u(k) - λ_1/k - λ_0. -/
noncomputable def projectAffine (u : ℕ → ℝ) (N : ℕ) (k : ℕ) : ℝ :=
  u k - lambda1 u N / (k : ℝ) - lambda0 u N

/-- Linear cancellation identity for D1 projection. -/
theorem projectAffine_D1 (u : ℕ → ℝ) (N : ℕ) (hΔ : DeltaDet N ≠ 0) :
    D1 (projectAffine u N) N = 0 := by
  unfold D1 projectAffine
  have h_split : (∑ k ∈ Finset.Icc 1 N, (u k - lambda1 u N / (k : ℝ) - lambda0 u N) / (k : ℝ)) =
      (∑ k ∈ Finset.Icc 1 N, u k / (k : ℝ)) -
      lambda1 u N * S2Sum N - lambda0 u N * HSum N := by
    have h1 : ∀ k ∈ Finset.Icc 1 N,
        (u k - lambda1 u N / (k : ℝ) - lambda0 u N) / (k : ℝ) =
        u k / (k : ℝ) - lambda1 u N * (1 / (k : ℝ) ^ 2) - lambda0 u N * (1 / (k : ℝ)) := by
      intro k hk
      have hkpos : (k : ℝ) ≠ 0 := by
        have hk1 : 1 ≤ k := (Finset.mem_Icc.mp hk).1
        exact Nat.cast_ne_zero.mpr (by omega)
      ring
    rw [Finset.sum_congr rfl h1]
    have h_sub_sub : ∀ k ∈ Finset.Icc 1 N,
        u k / (k : ℝ) - lambda1 u N * (1 / (k : ℝ) ^ 2) - lambda0 u N * (1 / (k : ℝ)) =
        u k / (k : ℝ) - (lambda1 u N * (1 / (k : ℝ) ^ 2) + lambda0 u N * (1 / (k : ℝ))) := by
      intro k _
      ring
    rw [Finset.sum_congr rfl h_sub_sub, Finset.sum_sub_distrib, Finset.sum_add_distrib]
    rw [← Finset.mul_sum, ← Finset.mul_sum]
    dsimp [S2Sum, HSum]
    ring
  rw [h_split]
  unfold lambda1 lambda0 DeltaDet
  set U1 := ∑ k ∈ Finset.Icc 1 N, u k / (k : ℝ)
  set U0 := ∑ k ∈ Finset.Icc 1 N, u k
  set S2 := S2Sum N
  set H := HSum N
  set n := (N : ℝ)
  have h_alg : U1 - ((n * U1 - H * (U0 - 2)) / (n * S2 - H ^ 2)) * S2 -
      ((S2 * (U0 - 2) - H * U1) / (n * S2 - H ^ 2)) * H = 0 := by
    have hD : n * S2 - H ^ 2 ≠ 0 := hΔ
    field_simp [hD]
    ring
  exact h_alg

/-- Linear cancellation identity for D0 projection. -/
theorem projectAffine_D0 (u : ℕ → ℝ) (N : ℕ) (hΔ : DeltaDet N ≠ 0) :
    D0 (projectAffine u N) N = 2 := by
  unfold D0 projectAffine
  have h_split : (∑ k ∈ Finset.Icc 1 N, (u k - lambda1 u N / (k : ℝ) - lambda0 u N)) =
      (∑ k ∈ Finset.Icc 1 N, u k) -
      lambda1 u N * HSum N - lambda0 u N * (N : ℝ) := by
    have h1 : ∀ k ∈ Finset.Icc 1 N,
        u k - lambda1 u N / (k : ℝ) - lambda0 u N =
        u k - (lambda1 u N * (1 / (k : ℝ)) + lambda0 u N) := by
      intro k _
      ring
    rw [Finset.sum_congr rfl h1, Finset.sum_sub_distrib, Finset.sum_add_distrib]
    rw [← Finset.mul_sum]
    have h_const : (∑ k ∈ Finset.Icc 1 N, lambda0 u N) = lambda0 u N * (N : ℝ) := by
      rw [Finset.sum_const, Nat.card_Icc]
      have : N + 1 - 1 = N := by omega
      rw [this, nsmul_eq_mul]
      ring
    rw [h_const]
    dsimp [HSum]
    ring
  rw [h_split]
  unfold lambda1 lambda0 DeltaDet
  set U1 := ∑ k ∈ Finset.Icc 1 N, u k / (k : ℝ)
  set U0 := ∑ k ∈ Finset.Icc 1 N, u k
  set S2 := S2Sum N
  set H := HSum N
  set n := (N : ℝ)
  have h_alg : U0 - ((n * U1 - H * (U0 - 2)) / (n * S2 - H ^ 2)) * H -
      ((S2 * (U0 - 2) - H * U1) / (n * S2 - H ^ 2)) * n = 2 := by
    have hD : n * S2 - H ^ 2 ≠ 0 := hΔ
    field_simp [hD]
    ring
  exact h_alg

/-- Any projected vector satisfies both Báez-Duarte boundary conditions. -/
theorem projectAffine_mem_A_N (u : ℕ → ℝ) (N : ℕ) (hΔ : DeltaDet N ≠ 0) :
    D1 (projectAffine u N) N = 0 ∧ D0 (projectAffine u N) N = 2 :=
  ⟨projectAffine_D1 u N hΔ, projectAffine_D0 u N hΔ⟩

/-- Lagrange Cauchy-Schwarz identity for the 2-constraint Gram determinant `DeltaDet N`. -/
theorem DeltaDet_double_sum_eq (N : ℕ) :
    2 * DeltaDet N =
      ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
        ((1 : ℝ) / (j : ℝ) - (1 : ℝ) / (k : ℝ)) ^ 2 := by
  have h_pt : ∀ j ∈ Finset.Icc 1 N, ∀ k ∈ Finset.Icc 1 N,
      ((1 : ℝ) / (j : ℝ) - (1 : ℝ) / (k : ℝ)) ^ 2 =
        (1 : ℝ) / ((j : ℝ) ^ 2) - 2 * (((1 : ℝ) / (j : ℝ)) * ((1 : ℝ) / (k : ℝ))) +
          (1 : ℝ) / ((k : ℝ) ^ 2) := by
    intro j _ k _
    ring
  have h_inner : ∀ j ∈ Finset.Icc 1 N,
      (∑ k ∈ Finset.Icc 1 N, ((1 : ℝ) / (j : ℝ) - (1 : ℝ) / (k : ℝ)) ^ 2) =
        (N : ℝ) * ((1 : ℝ) / ((j : ℝ) ^ 2)) -
          2 * ((1 : ℝ) / (j : ℝ)) * HSum N + S2Sum N := by
    intro j hj
    rw [Finset.sum_congr rfl (h_pt j hj)]
    simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.sum_const,
      Nat.card_Icc, nsmul_eq_mul, ← Finset.mul_sum]
    have hcard : ((N + 1 - 1 : ℕ) : ℝ) = (N : ℝ) := by
      have : N + 1 - 1 = N := by omega
      rw [this]
    rw [hcard]
    dsimp [HSum, S2Sum]
    ring
  rw [Finset.sum_congr rfl h_inner]
  simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.sum_const,
    Nat.card_Icc, nsmul_eq_mul, ← Finset.mul_sum, ← Finset.sum_mul]
  have hcard : ((N + 1 - 1 : ℕ) : ℝ) = (N : ℝ) := by
    have : N + 1 - 1 = N := by omega
    rw [this]
  rw [hcard]
  dsimp [DeltaDet, S2Sum, HSum]
  ring

/-- Unconditional strict positivity of the affine projection determinant `DeltaDet N > 0`
for all `N ≥ 2`. -/
theorem DeltaDet_pos {N : ℕ} (hN : 2 ≤ N) : 0 < DeltaDet N := by
  have h_eq := DeltaDet_double_sum_eq N
  have h1_mem : (1 : ℕ) ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨by omega, by omega⟩
  have h2_mem : (2 : ℕ) ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨by omega, hN⟩
  have h_inner_ge :
      ((1 : ℝ) / ((1 : ℕ) : ℝ) - (1 : ℝ) / ((2 : ℕ) : ℝ)) ^ 2 ≤
        ∑ k ∈ Finset.Icc 1 N, ((1 : ℝ) / ((1 : ℕ) : ℝ) - (1 : ℝ) / (k : ℝ)) ^ 2 :=
    Finset.single_le_sum (f := fun k : ℕ => ((1 : ℝ) / ((1 : ℕ) : ℝ) - (1 : ℝ) / (k : ℝ)) ^ 2)
      (fun k _ => sq_nonneg _) h2_mem
  have h_outer_ge :
      (∑ k ∈ Finset.Icc 1 N, ((1 : ℝ) / ((1 : ℕ) : ℝ) - (1 : ℝ) / (k : ℝ)) ^ 2) ≤
        ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          ((1 : ℝ) / (j : ℝ) - (1 : ℝ) / (k : ℝ)) ^ 2 :=
    Finset.single_le_sum
      (f := fun j : ℕ => ∑ k ∈ Finset.Icc 1 N, ((1 : ℝ) / (j : ℝ) - (1 : ℝ) / (k : ℝ)) ^ 2)
      (fun j _ => Finset.sum_nonneg (fun k _ => sq_nonneg _)) h1_mem
  have h_quarter : (0 : ℝ) < ((1 : ℝ) / ((1 : ℕ) : ℝ) - (1 : ℝ) / ((2 : ℕ) : ℝ)) ^ 2 := by
    norm_num
  linarith

/-- Non-vanishing of `DeltaDet N` for all `N ≥ 2`. -/
theorem DeltaDet_ne_zero {N : ℕ} (hN : 2 ≤ N) : DeltaDet N ≠ 0 :=
  (DeltaDet_pos hN).ne'

/-- Unconditional Báez-Duarte affine manifold membership for `projectAffine u N` (`N ≥ 2`). -/
theorem projectAffine_mem_A_N_uncond (u : ℕ → ℝ) {N : ℕ} (hN : 2 ≤ N) :
    D1 (projectAffine u N) N = 0 ∧ D0 (projectAffine u N) N = 2 :=
  projectAffine_mem_A_N u N (DeltaDet_ne_zero hN)

/-- Internal unconditional bridge from real `L^2` approximation with `D1 = 0` to Mathlib's
`RiemannHypothesis.of_nymanBeurling_approx`. -/
private theorem riemannHypothesis_of_l2_dist_approx
    (h_approx : ∀ ε > 0, ∃ (N : ℕ) (c : ℕ → ℝ), D1 c N = 0 ∧
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) < ε) :
    RiemannHypothesis := by
  apply RiemannHypothesis.of_nymanBeurling_approx
  intro ε hε
  rcases h_approx ε hε with ⟨N, c, hD1, hdist⟩
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
      refine MeasureTheory.setIntegral_congr_fun measurableSet_Ioo fun x _ => ?_
      have h_sub : (1 - ∑ k ∈ Finset.Icc 1 N, (c k : ℂ) * (recipFractScaled k x : ℂ)) =
          ((1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x : ℝ) : ℂ) := by
        push_cast; rfl
      rw [h_sub, Complex.norm_real, Real.norm_eq_abs, sq_abs]
    rwa [h_int_eq]

/-- On the Báez-Duarte affine subspace A_N (where D1 c N = 0), the linear energy
  ∑ c_k bVasyunin(k, γ) against Vasyunin's kernel is completely independent of
  the Euler-Mascheroni constant γ and equals the pure logarithmic moment ∑ c_k (ln k / k). -/
theorem affine_linear_energy_eq_log_moment (c : ℕ → ℝ) (N : ℕ) (gamma_E : ℝ)
    (hD1 : D1 c N = 0) :
    (∑ k ∈ Finset.Icc 1 N, c k * bVasyunin k gamma_E) =
      ∑ k ∈ Finset.Icc 1 N, c k * Real.log (k : ℝ) / (k : ℝ) := by
  have h_split : ∀ k ∈ Finset.Icc 1 N,
      c k * bVasyunin k gamma_E =
        c k * Real.log (k : ℝ) / (k : ℝ) + (1 - gamma_E) * (c k / (k : ℝ)) := by
    intro k _
    unfold bVasyunin
    ring
  rw [Finset.sum_congr rfl h_split, Finset.sum_add_distrib, ← Finset.mul_sum]
  unfold D1 at hD1
  rw [hD1, mul_zero, add_zero]

/-- The linear energy of any projected vector projectAffine u N against Vasyunin's kernel
  equals its pure logarithmic moment whenever DeltaDet N ≠ 0. -/
theorem projectAffine_linear_energy_eq_log_moment (u : ℕ → ℝ) (N : ℕ) (gamma_E : ℝ)
    (hΔ : DeltaDet N ≠ 0) :
    (∑ k ∈ Finset.Icc 1 N, projectAffine u N k * bVasyunin k gamma_E) =
      ∑ k ∈ Finset.Icc 1 N, projectAffine u N k * Real.log (k : ℝ) / (k : ℝ) :=
  affine_linear_energy_eq_log_moment (projectAffine u N) N gamma_E (projectAffine_D1 u N hΔ)

/-- The exact L² distance formula for any projected candidate vector (unconditional):
  ∫_0^1 (1 - ∑ c_k {1/(kx)})² dx = 1 - SCot vasyuninGCot (projectAffine u N) N. -/
theorem projectAffine_l2_dist_eq_one_sub_scot (u : ℕ → ℝ) (N : ℕ)
    (hΔ : DeltaDet N ≠ 0) :
    (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 N, projectAffine u N k * recipFractScaled k x) ^ 2) =
      1 - SCot vasyuninGCot (projectAffine u N) N :=
  affine_l2_dist_eq_one_sub_scot (projectAffine u N)
    (projectAffine_D1 u N hΔ) (projectAffine_D0 u N hΔ)

/-- The pure linear cross-term I_1(N) in the L² distance expansion on A_N:
  I_1(N) = -2 * ∑ c_k (ln k / k). -/
noncomputable def linearCrossTerm (c : ℕ → ℝ) (N : ℕ) : ℝ :=
  - 2 * ∑ k ∈ Finset.Icc 1 N, c k * Real.log (k : ℝ) / (k : ℝ)

/-- The quadratic cross-term I_2(N) in the L² distance expansion:
  I_2(N) = ∑∑ c_j c_k ∫_0^1 {1/(jx)} {1/(kx)} dx. -/
noncomputable def quadraticCrossTerm (c : ℕ → ℝ) (N : ℕ) : ℝ :=
  ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
    c j * c k * ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x

/-- Decomposition Theorem (unconditional): On the Báez-Duarte affine subspace A_N
  (where D1 c N = 0), the squared L² distance decomposes identically as:
  ∫_0^1 (1 - ∑ c_k {1/(kx)})² dx = 1 + linearCrossTerm c N + quadraticCrossTerm c N. -/
theorem l2_dist_sq_decomposition_on_A_N (c : ℕ → ℝ) (N : ℕ)
    (hD1 : D1 c N = 0) :
    (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) =
      1 + linearCrossTerm c N + quadraticCrossTerm c N := by
  rw [intervalIntegral_sq_sub_sum c]
  have h_b_sum : (∑ k ∈ Finset.Icc 1 N, c k * ∫ x in (0 : ℝ)..1, recipFractScaled k x) =
      ∑ k ∈ Finset.Icc 1 N, c k * bVasyunin k Real.eulerMascheroniConstant := by
    refine Finset.sum_congr rfl (fun k hk => ?_)
    rw [intervalIntegral_recipFractScaled_eq_bVasyunin (Finset.mem_Icc.mp hk).1]
  rw [h_b_sum, affine_linear_energy_eq_log_moment c N Real.eulerMascheroniConstant hD1]
  unfold linearCrossTerm quadraticCrossTerm
  ring

/-- The quadratic mollified Möbius weights u_mob(k, N) = - μ(k) * (1 - k/N)^2. -/
noncomputable def mollifiedMobius (N : ℕ) (k : ℕ) : ℝ :=
  - (ArithmeticFunction.moebius k : ℝ) * (1 - (k : ℝ) / (N : ℝ)) ^ 2

/-- The canonical constructive candidate vector on A_N:
  c_mob(N) = projectAffine (mollifiedMobius N) N. -/
noncomputable def cCandidateMobius (N : ℕ) : ℕ → ℝ :=
  projectAffine (mollifiedMobius N) N

/-- Main Constructive Membership Theorem:
For any N with DeltaDet N ≠ 0, the explicit mollified Möbius vector cCandidateMobius N
lies strictly on the Báez-Duarte affine subspace A_N = { c | D1 = 0, D0 = 2 }. -/
theorem cCandidateMobius_mem_A_N (N : ℕ) (hΔ : DeltaDet N ≠ 0) :
    D1 (cCandidateMobius N) N = 0 ∧ D0 (cCandidateMobius N) N = 2 :=
  projectAffine_mem_A_N (mollifiedMobius N) N hΔ

/-- Unconditional Báez-Duarte affine manifold membership for `cCandidateMobius N` (`N ≥ 2`). -/
theorem cCandidateMobius_mem_A_N_uncond {N : ℕ} (hN : 2 ≤ N) :
    D1 (cCandidateMobius N) N = 0 ∧ D0 (cCandidateMobius N) N = 2 :=
  cCandidateMobius_mem_A_N N (DeltaDet_ne_zero hN)

/-- The linear energy of the constructive mollified Möbius sequence cCandidateMobius N
  against Vasyunin's kernel equals its pure logarithmic moment whenever DeltaDet N ≠ 0. -/
theorem cCandidateMobius_linear_energy_eq_log_moment (N : ℕ) (gamma_E : ℝ)
    (hΔ : DeltaDet N ≠ 0) :
    (∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * bVasyunin k gamma_E) =
      ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * Real.log (k : ℝ) / (k : ℝ) :=
  projectAffine_linear_energy_eq_log_moment (mollifiedMobius N) N gamma_E hΔ

/-- Exact L² distance decomposition for the mollified Möbius sequence cCandidateMobius N
(unconditional for all `N ≥ 2`). -/
theorem cCandidateMobius_l2_dist_sq_decomposition (N : ℕ) (hN : 2 ≤ N) :
    (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateMobius N k * recipFractScaled k x) ^ 2) =
      1 + linearCrossTerm (cCandidateMobius N) N + quadraticCrossTerm (cCandidateMobius N) N :=
  l2_dist_sq_decomposition_on_A_N (cCandidateMobius N) N (cCandidateMobius_mem_A_N_uncond hN).1

/-- Selberg Sieve Weights: λ_k = - μ(k) * (ln(N/k) / ln N)^2 for k < N, 0 for k = N. -/
noncomputable def selbergSieveWeights (N : ℕ) (k : ℕ) : ℝ :=
  if k < N then
    - (ArithmeticFunction.moebius k : ℝ) *
      ((Real.log ((N : ℝ) / (k : ℝ)) / Real.log (N : ℝ)) ^ 2)
  else 0

/-- Constructive candidate sequence generated by Selberg sieve mollifier:
  c_sel(N) = projectAffine (selbergSieveWeights N) N. -/
noncomputable def cCandidateSelberg (N : ℕ) : ℕ → ℝ :=
  projectAffine (selbergSieveWeights N) N

/-- The Selberg sieve candidate sequence lies strictly on the Báez-Duarte subspace A_N. -/
theorem cCandidateSelberg_mem_A_N (N : ℕ) (hΔ : DeltaDet N ≠ 0) :
    D1 (cCandidateSelberg N) N = 0 ∧ D0 (cCandidateSelberg N) N = 2 :=
  projectAffine_mem_A_N (selbergSieveWeights N) N hΔ

/-- Unconditional Báez-Duarte affine manifold membership for `cCandidateSelberg N` (`N ≥ 2`). -/
theorem cCandidateSelberg_mem_A_N_uncond {N : ℕ} (hN : 2 ≤ N) :
    D1 (cCandidateSelberg N) N = 0 ∧ D0 (cCandidateSelberg N) N = 2 :=
  cCandidateSelberg_mem_A_N N (DeltaDet_ne_zero hN)

/-- The linear energy of the Selberg candidate sequence equals its pure logarithmic moment. -/
theorem cCandidateSelberg_linear_energy_eq_log_moment (N : ℕ) (gamma_E : ℝ)
    (hΔ : DeltaDet N ≠ 0) :
    (∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * bVasyunin k gamma_E) =
      ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * Real.log (k : ℝ) / (k : ℝ) :=
  projectAffine_linear_energy_eq_log_moment (selbergSieveWeights N) N gamma_E hΔ

/-- Exact L² distance decomposition for the Selberg sieve candidate sequence cCandidateSelberg N
(unconditional for all `N ≥ 2`). -/
theorem cCandidateSelberg_l2_dist_sq_decomposition (N : ℕ) (hN : 2 ≤ N) :
    (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 N, cCandidateSelberg N k * recipFractScaled k x) ^ 2) =
      1 + linearCrossTerm (cCandidateSelberg N) N + quadraticCrossTerm (cCandidateSelberg N) N :=
  l2_dist_sq_decomposition_on_A_N (cCandidateSelberg N) N (cCandidateSelberg_mem_A_N_uncond hN).1

/-- Main Reduction for Selberg Sieve Candidate (unconditional): If the Selberg cotangent sum
converges to 1, then the Riemann Hypothesis holds. -/
theorem riemannHypothesis_of_cCandidateSelberg_limit
    (h_limit : ∀ ε > 0, ∃ N : ℕ, 2 ≤ N ∧ 1 - ε < SCot vasyuninGCot (cCandidateSelberg N) N) :
    RiemannHypothesis := by
  apply riemannHypothesis_of_cotangent_limit
  intro ε hε
  rcases h_limit ε hε with ⟨N, hN, hscot⟩
  have hmem := cCandidateSelberg_mem_A_N_uncond hN
  exact ⟨N, cCandidateSelberg N, hmem.1, hmem.2, hscot⟩

/-- Main Reduction (unconditional): If the constructive mollified Möbius cotangent sum
converges to 1, then the Riemann Hypothesis holds. -/
theorem riemannHypothesis_of_cCandidateMobius_limit
    (h_limit : ∀ ε > 0, ∃ N : ℕ, 2 ≤ N ∧ 1 - ε < SCot vasyuninGCot (cCandidateMobius N) N) :
    RiemannHypothesis := by
  apply riemannHypothesis_of_cotangent_limit
  intro ε hε
  rcases h_limit ε hε with ⟨N, hN, hscot⟩
  have hmem := cCandidateMobius_mem_A_N_uncond hN
  exact ⟨N, cCandidateMobius N, hmem.1, hmem.2, hscot⟩

/-- Direct L² Distance Reduction Theorem (unconditional): If the explicit mollified Möbius sequence
  cCandidateMobius N achieves arbitrary L² approximation of 1, the Riemann Hypothesis holds. -/
theorem riemannHypothesis_of_cCandidateMobius_l2_dist
    (h_dist : ∀ ε > 0, ∃ N : ℕ, 2 ≤ N ∧
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N,
        cCandidateMobius N k * recipFractScaled k x) ^ 2) < ε) :
    RiemannHypothesis := by
  apply riemannHypothesis_of_l2_dist_approx
  intro ε hε
  rcases h_dist ε hε with ⟨N, hN, hdist⟩
  exact ⟨N, cCandidateMobius N, (cCandidateMobius_mem_A_N_uncond hN).1, hdist⟩

/-- Direct L² Distance Reduction Theorem for Selberg Sieve Candidate (unconditional):
  If the constructive Selberg sequence achieves arbitrary L² approximation of 1,
  the Riemann Hypothesis holds. -/
theorem riemannHypothesis_of_cCandidateSelberg_l2_dist
    (h_dist : ∀ ε > 0, ∃ N : ℕ, 2 ≤ N ∧
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N,
        cCandidateSelberg N k * recipFractScaled k x) ^ 2) < ε) :
    RiemannHypothesis := by
  apply riemannHypothesis_of_l2_dist_approx
  intro ε hε
  rcases h_dist ε hε with ⟨N, hN, hdist⟩
  exact ⟨N, cCandidateSelberg N, (cCandidateSelberg_mem_A_N_uncond hN).1, hdist⟩

/-- Asymptotic Sandwich Theorem (unconditional): If a constructive candidate sequence on A_N
  satisfies a logarithmic upper bound D_N^2 ≤ C / ln N for some constant C > 0,
  then the Riemann Hypothesis holds. -/
theorem riemannHypothesis_of_log_decay_bound
    (c : ℕ → ℕ → ℝ)
    (h_A_N : ∀ N ≥ 2, D1 (c N) N = 0)
    (h_dist_bound : ∃ C > 0, ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ)) :
    RiemannHypothesis := by
  apply riemannHypothesis_of_l2_dist_approx
  intro ε hε
  rcases h_dist_bound with ⟨C, hC, hbound⟩
  have h_ratio_pos : 0 < C / ε := div_pos hC hε
  have h_exp_pos : 0 < Real.exp (C / ε) := Real.exp_pos (C / ε)
  obtain ⟨M, hM⟩ := exists_nat_gt (Real.exp (C / ε) + 2)
  have hM_gt_exp : Real.exp (C / ε) < (M : ℝ) := by linarith
  have hM_ge_2 : 2 ≤ M := by
    exact_mod_cast (by linarith [h_exp_pos] : (1 : ℝ) < (M : ℝ))
  have h_log_gt : C / ε < Real.log (M : ℝ) := by
    rw [← Real.log_exp (C / ε)]
    exact Real.log_lt_log h_exp_pos hM_gt_exp
  have h_log_pos : 0 < Real.log (M : ℝ) := by
    calc 0 < C / ε := h_ratio_pos
      _ < Real.log (M : ℝ) := h_log_gt
  have h_div_lt : C / Real.log (M : ℝ) < ε := by
    rw [div_lt_iff₀ h_log_pos]
    have : C < Real.log (M : ℝ) * ε := by
      rw [← div_lt_iff₀ hε]
      exact h_log_gt
    linarith
  have h_dist_M := hbound M hM_ge_2
  have h_dist_lt : (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 M, c M k * recipFractScaled k x) ^ 2) < ε :=
    lt_of_le_of_lt h_dist_M h_div_lt
  exact ⟨M, c M, h_A_N M hM_ge_2, h_dist_lt⟩

/-- Logarithmic Decay Sandwich Theorem for mollified Möbius sequence (unconditional). -/
theorem riemannHypothesis_of_cCandidateMobius_log_decay
    (h_dist_bound : ∃ C > 0, ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N,
        cCandidateMobius N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ)) :
    RiemannHypothesis :=
  riemannHypothesis_of_log_decay_bound (fun N => cCandidateMobius N)
    (fun N hN => (cCandidateMobius_mem_A_N_uncond hN).1) h_dist_bound

/-- Logarithmic Decay Sandwich Theorem for Selberg sieve candidate sequence (unconditional). -/
theorem riemannHypothesis_of_cCandidateSelberg_log_decay
    (h_dist_bound : ∃ C > 0, ∀ N ≥ 2,
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N,
        cCandidateSelberg N k * recipFractScaled k x) ^ 2) ≤
        C / Real.log (N : ℝ)) :
    RiemannHypothesis :=
  riemannHypothesis_of_log_decay_bound (fun N => cCandidateSelberg N)
    (fun N hN => (cCandidateSelberg_mem_A_N_uncond hN).1) h_dist_bound

/-! ### Stage D.2: Determinant Positivity, Clay-Galerkin & N = 4 -/

/-- Unconditional RH reduction alias for `cCandidateMobius`. -/
theorem riemannHypothesis_of_cCandidateMobius_limit_uncond
    (h_limit : ∀ ε > 0, ∃ N : ℕ, 2 ≤ N ∧ 1 - ε < SCot vasyuninGCot (cCandidateMobius N) N) :
    RiemannHypothesis :=
  riemannHypothesis_of_cCandidateMobius_limit h_limit

/-- Unconditional RH reduction alias for `cCandidateSelberg`. -/
theorem riemannHypothesis_of_cCandidateSelberg_limit_uncond
    (h_limit : ∀ ε > 0, ∃ N : ℕ, 2 ≤ N ∧ 1 - ε < SCot vasyuninGCot (cCandidateSelberg N) N) :
    RiemannHypothesis :=
  riemannHypothesis_of_cCandidateSelberg_limit h_limit

/-- Explicit Clay-Galerkin Base-Plus-Ray candidate sequence:
`clayRank4Base + clayRank4GalerkinRay vasyuninGCot u N`. -/
noncomputable def clayGalerkinCandidate (u : ℕ → ℝ) (N k : ℕ) : ℝ :=
  clayRank4Base k + clayRank4GalerkinRay vasyuninGCot u N k

/-- `clayRank4Base` lies on `A_N` for all `N ≥ 4`. -/
theorem clayRank4Base_mem_A_N {N : ℕ} (hN : 4 ≤ N) :
    D1 clayRank4Base N = 0 ∧ D0 clayRank4Base N = 2 := by
  rcases clayRank4Base_satisfies_clay N hN with ⟨hD0, _, hD1, _⟩
  exact ⟨hD1, hD0⟩

/-- For any raw seed `u` and `N ≥ 4`, `clayGalerkinCandidate u N` lies on `A_N`. -/
theorem clayGalerkinCandidate_mem_A_N (u : ℕ → ℝ) {N : ℕ} (hN : 4 ≤ N) :
    D1 (clayGalerkinCandidate u N) N = 0 ∧ D0 (clayGalerkinCandidate u N) N = 2 := by
  have h_clay := satisfiesClayBoundaryConditions_add_of_homogeneous
    clayRank4Base (clayRank4GalerkinRay vasyuninGCot u N) N 1
    (clayRank4Base_satisfies_clay N hN)
    (clayRank4GalerkinRay_satisfies_homogeneous vasyuninGCot u N hN)
  have h_eq : (fun k => clayRank4Base k + 1 * clayRank4GalerkinRay vasyuninGCot u N k) =
      clayGalerkinCandidate u N := by
    ext k
    unfold clayGalerkinCandidate
    ring
  rw [h_eq] at h_clay
  exact ⟨h_clay.2.2.1, h_clay.1⟩

/-- Exact continuous `L^2(0, 1)` distance formula for `clayGalerkinCandidate u N` (`N ≥ 4`). -/
theorem clayGalerkinCandidate_l2_dist_eq_one_sub_scot (u : ℕ → ℝ) {N : ℕ} (hN : 4 ≤ N) :
    (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 N, clayGalerkinCandidate u N k * recipFractScaled k x) ^ 2) =
      1 - SCot vasyuninGCot (clayGalerkinCandidate u N) N := by
  have hmem := clayGalerkinCandidate_mem_A_N u hN
  exact affine_l2_dist_eq_one_sub_scot (clayGalerkinCandidate u N) hmem.1 hmem.2

/-- Unconditional RH reduction for the Clay-Galerkin Base-Plus-Ray family. -/
theorem riemannHypothesis_of_clayGalerkin_limit (u : ℕ → ℝ)
    (h_limit : ∀ ε > 0, ∃ N : ℕ, 4 ≤ N ∧ 1 - ε < SCot vasyuninGCot (clayGalerkinCandidate u N) N) :
    RiemannHypothesis := by
  apply riemannHypothesis_of_cotangent_limit
  intro ε hε
  rcases h_limit ε hε with ⟨N, hN, hscot⟩
  have hmem := clayGalerkinCandidate_mem_A_N u hN
  exact ⟨N, clayGalerkinCandidate u N, hmem.1, hmem.2, hscot⟩

private lemma sum_Icc_one_four (f : ℕ → ℝ) :
    ∑ k ∈ Finset.Icc 1 4, f k = f 1 + f 2 + f 3 + f 4 := by
  have hI : Finset.Icc 1 4 = ({1, 2, 3, 4} : Finset ℕ) := by
    ext x
    simp only [Finset.mem_Icc, Finset.mem_insert, Finset.mem_singleton]
    omega
  rw [hI]
  norm_num [Finset.sum_insert, add_assoc]

/-- Exact rational value `HSum 4 = 25 / 12`. -/
theorem HSum_four : HSum 4 = 25 / 12 := by
  unfold HSum
  rw [sum_Icc_one_four]
  norm_num

/-- Exact rational value `S2Sum 4 = 205 / 144`. -/
theorem S2Sum_four : S2Sum 4 = 205 / 144 := by
  unfold S2Sum
  rw [sum_Icc_one_four]
  norm_num

/-- Exact rational value `DeltaDet 4 = 65 / 48`. -/
theorem DeltaDet_four : DeltaDet 4 = 65 / 48 := by
  unfold DeltaDet
  rw [HSum_four, S2Sum_four]
  norm_num

/-- Exact rational evaluation of `mollifiedMobius 4` on `{1, 2, 3, 4}`. -/
theorem mollifiedMobius_four_eval :
    mollifiedMobius 4 1 = -9 / 16 ∧
    mollifiedMobius 4 2 = 1 / 4 ∧
    mollifiedMobius 4 3 = 1 / 16 ∧
    mollifiedMobius 4 4 = 0 := by
  have hm1 : ArithmeticFunction.moebius 1 = 1 := ArithmeticFunction.moebius_apply_one
  have hm2 : ArithmeticFunction.moebius 2 = -1 :=
    ArithmeticFunction.moebius_apply_prime Nat.prime_two
  have hm3 : ArithmeticFunction.moebius 3 = -1 :=
    ArithmeticFunction.moebius_apply_prime Nat.prime_three
  have hm4 : ArithmeticFunction.moebius 4 = 0 := by
    rw [show (4 : ℕ) = 2 ^ 2 by norm_num,
      ArithmeticFunction.moebius_apply_prime_pow Nat.prime_two (by norm_num)]
    simp
  refine ⟨?_, ?_, ?_, ?_⟩ <;> dsimp [mollifiedMobius]
  · rw [hm1]; norm_num
  · rw [hm2]; norm_num
  · rw [hm3]; norm_num
  · rw [hm4]; norm_num

/-- Exact rational evaluation of `cCandidateMobius 4` on `{1, 2, 3, 4}`. -/
theorem cCandidateMobius_four_eval :
    cCandidateMobius 4 1 = -667 / 624 ∧
    cCandidateMobius 4 2 = 67 / 78 ∧
    cCandidateMobius 4 3 = 217 / 208 ∧
    cCandidateMobius 4 4 = 7 / 6 := by
  rcases mollifiedMobius_four_eval with ⟨hu1, hu2, hu3, hu4⟩
  have hU1 : (∑ k ∈ Finset.Icc 1 4, mollifiedMobius 4 k / (k : ℝ)) = -5 / 12 := by
    rw [sum_Icc_one_four, hu1, hu2, hu3, hu4]
    norm_num
  have hU0 : (∑ k ∈ Finset.Icc 1 4, mollifiedMobius 4 k) = -1 / 4 := by
    rw [sum_Icc_one_four, hu1, hu2, hu3, hu4]
    norm_num
  have hlam1 : lambda1 (mollifiedMobius 4) 4 = 29 / 13 := by
    unfold lambda1
    rw [hU1, hU0, HSum_four, DeltaDet_four]
    norm_num
  have hlam0 : lambda0 (mollifiedMobius 4) 4 = -269 / 156 := by
    unfold lambda0
    rw [hU1, hU0, HSum_four, S2Sum_four, DeltaDet_four]
    norm_num
  refine ⟨?_, ?_, ?_, ?_⟩ <;> dsimp [cCandidateMobius, projectAffine]
  · rw [hu1, hlam1, hlam0]; norm_num
  · rw [hu2, hlam1, hlam0]; norm_num
  · rw [hu3, hlam1, hlam0]; norm_num
  · rw [hu4, hlam1, hlam0]; norm_num

private lemma vasyuninCotSum_one (b : ℕ) : vasyuninCotSum 1 b = 0 := by
  unfold vasyuninCotSum
  simp

private lemma vasyuninCotSum_two (b : ℕ) : vasyuninCotSum 2 b = 0 := by
  unfold vasyuninCotSum
  have hI : Finset.Ico 1 2 = ({1} : Finset ℕ) := by
    ext x; simp only [Finset.mem_Ico, Finset.mem_singleton]; omega
  rw [hI, Finset.sum_singleton]
  have harg : Real.pi * ((1 : ℕ) : ℝ) / ((2 : ℕ) : ℝ) = Real.pi / 2 := by push_cast; ring
  rw [harg, Real.cos_pi_div_two, zero_div, mul_zero]

private lemma cot_pi_div_three :
    Real.cos (Real.pi / 3) / Real.sin (Real.pi / 3) = 1 / Real.sqrt 3 := by
  rw [Real.cos_pi_div_three, Real.sin_pi_div_three]
  have hsq : Real.sqrt 3 ≠ 0 := (Real.sqrt_pos.mpr (by norm_num)).ne'
  field_simp [hsq]

private lemma cot_two_pi_div_three :
    Real.cos (2 * Real.pi / 3) / Real.sin (2 * Real.pi / 3) = -(1 / Real.sqrt 3) := by
  rw [show 2 * Real.pi / 3 = Real.pi - Real.pi / 3 by ring, Real.cos_pi_sub, Real.sin_pi_sub,
    Real.cos_pi_div_three, Real.sin_pi_div_three]
  have hsq : Real.sqrt 3 ≠ 0 := (Real.sqrt_pos.mpr (by norm_num)).ne'
  field_simp [hsq]

private lemma cot_pi_div_four :
    Real.cos (Real.pi / 4) / Real.sin (Real.pi / 4) = 1 := by
  rw [Real.cos_pi_div_four, Real.sin_pi_div_four]
  have hsq : Real.sqrt 2 ≠ 0 := (Real.sqrt_pos.mpr (by norm_num)).ne'
  field_simp [hsq]

private lemma cot_three_pi_div_four :
    Real.cos (3 * Real.pi / 4) / Real.sin (3 * Real.pi / 4) = -1 := by
  rw [show 3 * Real.pi / 4 = Real.pi - Real.pi / 4 by ring, Real.cos_pi_sub, Real.sin_pi_sub,
    Real.cos_pi_div_four, Real.sin_pi_div_four]
  have hsq : Real.sqrt 2 ≠ 0 := (Real.sqrt_pos.mpr (by norm_num)).ne'
  field_simp [hsq]

private lemma vasyuninCotSum_three_one : vasyuninCotSum 3 1 = -(1 / (3 * Real.sqrt 3)) := by
  unfold vasyuninCotSum
  have hI : Finset.Ico 1 3 = ({1, 2} : Finset ℕ) := by
    ext x; simp only [Finset.mem_Ico, Finset.mem_insert, Finset.mem_singleton]; omega
  rw [hI, Finset.sum_insert (by decide), Finset.sum_singleton]
  norm_num only
  rw [show Real.pi * 1 / 3 = Real.pi / 3 by ring,
    show Real.pi * 2 / 3 = 2 * Real.pi / 3 by ring, cot_pi_div_three, cot_two_pi_div_three]
  ring

private lemma vasyuninCotSum_three_two : vasyuninCotSum 3 2 = 1 / (3 * Real.sqrt 3) := by
  unfold vasyuninCotSum
  have hI : Finset.Ico 1 3 = ({1, 2} : Finset ℕ) := by
    ext x; simp only [Finset.mem_Ico, Finset.mem_insert, Finset.mem_singleton]; omega
  rw [hI, Finset.sum_insert (by decide), Finset.sum_singleton]
  norm_num only
  rw [show Real.pi * 1 / 3 = Real.pi / 3 by ring,
    show Real.pi * 2 / 3 = 2 * Real.pi / 3 by ring, cot_pi_div_three, cot_two_pi_div_three]
  ring

private lemma vasyuninCotSum_three_four : vasyuninCotSum 3 4 = -(1 / (3 * Real.sqrt 3)) := by
  unfold vasyuninCotSum
  have hI : Finset.Ico 1 3 = ({1, 2} : Finset ℕ) := by
    ext x; simp only [Finset.mem_Ico, Finset.mem_insert, Finset.mem_singleton]; omega
  rw [hI, Finset.sum_insert (by decide), Finset.sum_singleton]
  norm_num only
  rw [show Real.pi * 1 / 3 = Real.pi / 3 by ring,
    show Real.pi * 2 / 3 = 2 * Real.pi / 3 by ring, cot_pi_div_three, cot_two_pi_div_three]
  ring

private lemma vasyuninCotSum_four_one : vasyuninCotSum 4 1 = -(1 / 2) := by
  unfold vasyuninCotSum
  have hI : Finset.Ico 1 4 = ({1, 2, 3} : Finset ℕ) := by
    ext x; simp only [Finset.mem_Ico, Finset.mem_insert, Finset.mem_singleton]; omega
  rw [hI, Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton]
  norm_num only
  rw [show Real.pi * 1 / 4 = Real.pi / 4 by ring,
    show Real.pi * 2 / 4 = Real.pi / 2 by ring, Real.cos_pi_div_two, zero_div, mul_zero,
    show Real.pi * 3 / 4 = 3 * Real.pi / 4 by ring, cot_pi_div_four, cot_three_pi_div_four]
  ring

private lemma vasyuninCotSum_four_two : vasyuninCotSum 4 2 = 0 := by
  unfold vasyuninCotSum
  have hI : Finset.Ico 1 4 = ({1, 2, 3} : Finset ℕ) := by
    ext x; simp only [Finset.mem_Ico, Finset.mem_insert, Finset.mem_singleton]; omega
  rw [hI, Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton]
  norm_num only
  rw [show Real.pi * 1 / 4 = Real.pi / 4 by ring,
    show Real.pi * 2 / 4 = Real.pi / 2 by ring, Real.cos_pi_div_two, zero_div, mul_zero,
    show Real.pi * 3 / 4 = 3 * Real.pi / 4 by ring, cot_pi_div_four, cot_three_pi_div_four]
  ring

private lemma vasyuninCotSum_four_three : vasyuninCotSum 4 3 = 1 / 2 := by
  unfold vasyuninCotSum
  have hI : Finset.Ico 1 4 = ({1, 2, 3} : Finset ℕ) := by
    ext x; simp only [Finset.mem_Ico, Finset.mem_insert, Finset.mem_singleton]; omega
  rw [hI, Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton]
  norm_num only
  rw [show Real.pi * 1 / 4 = Real.pi / 4 by ring,
    show Real.pi * 2 / 4 = Real.pi / 2 by ring, Real.cos_pi_div_two, zero_div, mul_zero,
    show Real.pi * 3 / 4 = 3 * Real.pi / 4 by ring, cot_pi_div_four, cot_three_pi_div_four]
  ring

private lemma vasyuninGCot_one_two : vasyuninGCot 1 2 = 0 := by
  unfold vasyuninGCot
  rw [vasyuninCotSum_one, vasyuninCotSum_two]
  ring

private lemma vasyuninGCot_one_three : vasyuninGCot 1 3 = Real.pi / (18 * Real.sqrt 3) := by
  unfold vasyuninGCot
  rw [vasyuninCotSum_one, vasyuninCotSum_three_one]
  norm_num; ring

private lemma vasyuninGCot_one_four : vasyuninGCot 1 4 = Real.pi / 16 := by
  unfold vasyuninGCot
  rw [vasyuninCotSum_one, vasyuninCotSum_four_one]
  norm_num; ring

private lemma vasyuninGCot_two_three : vasyuninGCot 2 3 = -(Real.pi / (36 * Real.sqrt 3)) := by
  unfold vasyuninGCot
  rw [vasyuninCotSum_two, vasyuninCotSum_three_two]
  norm_num; ring

private lemma vasyuninGCot_two_four : vasyuninGCot 2 4 = 0 := by
  unfold vasyuninGCot
  rw [vasyuninCotSum_two, vasyuninCotSum_four_two]
  ring

private lemma vasyuninGCot_three_four :
    vasyuninGCot 3 4 = Real.pi / (72 * Real.sqrt 3) - Real.pi / 48 := by
  unfold vasyuninGCot
  rw [vasyuninCotSum_three_four, vasyuninCotSum_four_three]
  norm_num; ring

/-- Exact closed-form formula for `SCot vasyuninGCot (cCandidateMobius 4) 4`
in terms of `π` and `√3`. -/
theorem SCot_cCandidateMobius_four_eq :
    SCot vasyuninGCot (cCandidateMobius 4) 4 =
      ((119 : ℝ) / 576 + 54467 / (389376 * Real.sqrt 3)) * Real.pi := by
  rcases cCandidateMobius_four_eval with ⟨hc1, hc2, hc3, hc4⟩
  unfold SCot QCot
  simp_rw [sum_Icc_one_four]
  rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3, vasyuninGCot_diag 4]
  rw [vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 4 1,
      vasyuninGCot_comm 3 2, vasyuninGCot_comm 4 2, vasyuninGCot_comm 4 3]
  rw [vasyuninGCot_one_two, vasyuninGCot_one_three, vasyuninGCot_one_four,
      vasyuninGCot_two_three, vasyuninGCot_two_four, vasyuninGCot_three_four]
  rw [hc1, hc2, hc3, hc4]
  ring

/-- Exact continuous `L^2(0, 1)` distance formula for `cCandidateMobius 4`. -/
theorem cCandidateMobius_four_l2_dist_eq :
    (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 4, cCandidateMobius 4 k * recipFractScaled k x) ^ 2) =
      1 - ((119 : ℝ) / 576 + 54467 / (389376 * Real.sqrt 3)) * Real.pi := by
  have hmem := cCandidateMobius_mem_A_N_uncond (by decide : 2 ≤ 4)
  rw [affine_l2_dist_eq_one_sub_scot (cCandidateMobius 4) hmem.1 hmem.2,
    SCot_cCandidateMobius_four_eq]

/-- Strictly positive finite-`N` Nyman-Beurling `L^2(0, 1)` error certificate at `N = 4` for
`cCandidateMobius 4` (bounded inside `(0.09, 0.11)`). -/
theorem cCandidateMobius_four_l2_dist_pos :
    0 < (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 4, cCandidateMobius 4 k * recipFractScaled k x) ^ 2) := by
  rw [cCandidateMobius_four_l2_dist_eq]
  have hsq3_lo : (1.732 : ℝ) < Real.sqrt 3 := by
    have hnn : 0 ≤ Real.sqrt 3 := Real.sqrt_nonneg 3
    have hsq : Real.sqrt 3 * Real.sqrt 3 = 3 := Real.mul_self_sqrt (by norm_num)
    nlinarith
  have h_inv_hi : (1 : ℝ) / Real.sqrt 3 < 1 / 1.732 := by
    rw [one_div_lt_one_div (Real.sqrt_pos.mpr (by norm_num)) (by norm_num)]
    exact hsq3_lo
  have h_pi_hi : Real.pi < 3.1416 := Real.pi_lt_d4
  have h_pi_pos : 0 < Real.pi := Real.pi_pos
  have h_term : ((119 : ℝ) / 576 + 54467 / (389376 * Real.sqrt 3)) * Real.pi <
      ((119 : ℝ) / 576 + 54467 / (389376 * 1.732)) * 3.1416 := by
    have h_inner : (119 : ℝ) / 576 + 54467 / (389376 * Real.sqrt 3) <
        (119 : ℝ) / 576 + 54467 / (389376 * 1.732) := by
      have hdiv : 54467 / (389376 * Real.sqrt 3) < 54467 / (389376 * 1.732) := by
        calc 54467 / (389376 * Real.sqrt 3)
            = (54467 / 389376) * (1 / Real.sqrt 3) := by ring
          _ < (54467 / 389376) * (1 / 1.732) :=
              mul_lt_mul_of_pos_left h_inv_hi (by norm_num)
          _ = 54467 / (389376 * 1.732) := by ring
      linarith
    have h_lhs_pos : 0 < (119 : ℝ) / 576 + 54467 / (389376 * Real.sqrt 3) := by positivity
    exact mul_lt_mul h_inner (le_of_lt h_pi_hi) h_pi_pos (by positivity)
  have h_num : ((119 : ℝ) / 576 + 54467 / (389376 * 1.732)) * 3.1416 < 1 := by norm_num
  linarith

/-- Exact `L²(0, 1)` difference identity for any two vectors `c, c' ∈ A_N`. -/
theorem l2_dist_sub_eq_scot_sub {N : ℕ} (c c' : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) (hc1' : D1 c' N = 0) (hc0' : D0 c' N = 2) :
    (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c' k * recipFractScaled k x) ^ 2) -
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) =
      SCot vasyuninGCot c N - SCot vasyuninGCot c' N := by
  rw [affine_l2_dist_eq_one_sub_scot c' hc1' hc0', affine_l2_dist_eq_one_sub_scot c hc1 hc0]
  ring

/-- Strictly smaller `L²(0, 1)` distance on `A_N` holds iff `SCot` is strictly larger. -/
theorem l2_dist_lt_iff_scot_gt {N : ℕ} (c c' : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) (hc1' : D1 c' N = 0) (hc0' : D0 c' N = 2) :
    (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c' k * recipFractScaled k x) ^ 2) <
      (∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2) ↔
      SCot vasyuninGCot c N < SCot vasyuninGCot c' N := by
  rw [affine_l2_dist_eq_one_sub_scot c' hc1' hc0', affine_l2_dist_eq_one_sub_scot c hc1 hc0]
  exact sub_lt_sub_iff_left 1

/-- Explicit rational variational improvement vector on `{1, 2, 3, 4}` approximating the exact
KKT optimum on `A_4`. -/
noncomputable def cVariationalFour : ℕ → ℝ
  | 1 => -21 / 20
  | 2 => 3 / 4
  | 3 => 6 / 5
  | 4 => 11 / 10
  | _ => 0

/-- Exact rational verification that `cVariationalFour` lies in `A_4`. -/
theorem cVariationalFour_mem_A_N :
    D1 cVariationalFour 4 = 0 ∧ D0 cVariationalFour 4 = 2 := by
  unfold D1 D0
  rw [sum_Icc_one_four, sum_Icc_one_four]
  norm_num [cVariationalFour]

/-- Exact closed-form formula for `SCot vasyuninGCot cVariationalFour 4` in terms of `π` and
`√3`. -/
theorem SCot_cVariationalFour_eq :
    SCot vasyuninGCot cVariationalFour 4 =
      ((319 : ℝ) / 1600 + 23 / (150 * Real.sqrt 3)) * Real.pi := by
  unfold SCot QCot
  simp_rw [sum_Icc_one_four]
  rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3, vasyuninGCot_diag 4,
    vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 4 1,
    vasyuninGCot_comm 3 2, vasyuninGCot_comm 4 2, vasyuninGCot_comm 4 3,
    vasyuninGCot_one_two, vasyuninGCot_one_three, vasyuninGCot_one_four,
    vasyuninGCot_two_three, vasyuninGCot_two_four, vasyuninGCot_three_four]
  norm_num [cVariationalFour]
  ring

/-- Unconditional strict suboptimality of `cCandidateMobius 4`: `cVariationalFour` achieves a
strictly larger cotangent score on `A_4`. -/
theorem SCot_cCandidateMobius_four_lt_cVariationalFour :
    SCot vasyuninGCot (cCandidateMobius 4) 4 < SCot vasyuninGCot cVariationalFour 4 := by
  rw [SCot_cCandidateMobius_four_eq, SCot_cVariationalFour_eq]
  refine mul_lt_mul_of_pos_right ?_ Real.pi_pos
  have hsq : Real.sqrt 3 * Real.sqrt 3 = 3 := Real.mul_self_sqrt (by norm_num)
  have hsq3_lo : (1.732 : ℝ) < Real.sqrt 3 := by
    have hnn := Real.sqrt_nonneg 3; nlinarith
  have hsq3_hi : Real.sqrt 3 < 1.7321 := by nlinarith
  have h_inv_hi : (1 : ℝ) / Real.sqrt 3 < 1 / 1.732 :=
    (one_div_lt_one_div (Real.sqrt_pos.mpr (by norm_num)) (by norm_num)).mpr hsq3_lo
  have h_inv_lo : (1 : ℝ) / 1.7321 < 1 / Real.sqrt 3 :=
    (one_div_lt_one_div (by norm_num) (Real.sqrt_pos.mpr (by norm_num))).mpr hsq3_hi
  have h1 : (119 : ℝ) / 576 + 54467 / (389376 * Real.sqrt 3) <
      (119 : ℝ) / 576 + 54467 / (389376 * 1.732) := by
    have := mul_lt_mul_of_pos_left h_inv_hi (by norm_num : (0 : ℝ) < 54467 / 389376)
    linarith [show (54467 : ℝ) / (389376 * Real.sqrt 3) = (54467 / 389376) * (1 / Real.sqrt 3) by
      ring, show (54467 : ℝ) / (389376 * 1.732) = (54467 / 389376) * (1 / 1.732) by ring]
  have h2 : (319 : ℝ) / 1600 + 23 / (150 * 1.7321) <
      (319 : ℝ) / 1600 + 23 / (150 * Real.sqrt 3) := by
    have := mul_lt_mul_of_pos_left h_inv_lo (by norm_num : (0 : ℝ) < 23 / 150)
    linarith [show (23 : ℝ) / (150 * Real.sqrt 3) = (23 / 150) * (1 / Real.sqrt 3) by ring,
      show (23 : ℝ) / (150 * 1.7321) = (23 / 150) * (1 / 1.7321) by ring]
  have h_num : (119 : ℝ) / 576 + 54467 / (389376 * 1.732) <
      (319 : ℝ) / 1600 + 23 / (150 * 1.7321) := by norm_num
  linarith

/-- Strict `L²(0, 1)` Nyman-Beurling distance improvement of `cVariationalFour` over
`cCandidateMobius 4` on `A_4`. -/
theorem l2_dist_cVariationalFour_lt_cCandidateMobius_four :
    (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 4, cVariationalFour k * recipFractScaled k x) ^ 2) <
      (∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 4, cCandidateMobius 4 k * recipFractScaled k x) ^ 2) := by
  have hm := cCandidateMobius_mem_A_N_uncond (by decide : 2 ≤ 4)
  have hv := cVariationalFour_mem_A_N
  exact (l2_dist_lt_iff_scot_gt (cCandidateMobius 4) cVariationalFour hm.1 hm.2 hv.1 hv.2).mpr
    SCot_cCandidateMobius_four_lt_cVariationalFour

/-- Strictly positive finite-`N` `L²(0, 1)` Nyman-Beurling error certificate for
`cVariationalFour` on `A_4`. -/
theorem cVariationalFour_l2_dist_pos :
    0 < (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 4, cVariationalFour k * recipFractScaled k x) ^ 2) := by
  have hv := cVariationalFour_mem_A_N
  rw [affine_l2_dist_eq_one_sub_scot cVariationalFour hv.1 hv.2, SCot_cVariationalFour_eq]
  have hsq3_lo : (1.732 : ℝ) < Real.sqrt 3 := by
    have hnn := Real.sqrt_nonneg 3
    have hsq : Real.sqrt 3 * Real.sqrt 3 = 3 := Real.mul_self_sqrt (by norm_num)
    nlinarith
  have h_inv_hi : (1 : ℝ) / Real.sqrt 3 < 1 / 1.732 :=
    (one_div_lt_one_div (Real.sqrt_pos.mpr (by norm_num)) (by norm_num)).mpr hsq3_lo
  have h_inner : (319 : ℝ) / 1600 + 23 / (150 * Real.sqrt 3) <
      (319 : ℝ) / 1600 + 23 / (150 * 1.732) := by
    have := mul_lt_mul_of_pos_left h_inv_hi (by norm_num : (0 : ℝ) < 23 / 150)
    linarith [show (23 : ℝ) / (150 * Real.sqrt 3) = (23 / 150) * (1 / Real.sqrt 3) by ring,
      show (23 : ℝ) / (150 * 1.732) = (23 / 150) * (1 / 1.732) by ring]
  have h_term : ((319 : ℝ) / 1600 + 23 / (150 * Real.sqrt 3)) * Real.pi <
      ((319 : ℝ) / 1600 + 23 / (150 * 1.732)) * 3.1416 :=
    mul_lt_mul h_inner (le_of_lt Real.pi_lt_d4) Real.pi_pos (by positivity)
  have h_num : ((319 : ℝ) / 1600 + 23 / (150 * 1.732)) * 3.1416 < 1 := by norm_num
  linarith

/-- The minimum-`ℓ²`-norm base vector on `A_N`, projecting the zero vector via `projectAffine`. -/
noncomputable def cMinNorm (N : ℕ) : ℕ → ℝ :=
  projectAffine (fun _ => 0) N

/-- Closed-form formula `cMinNorm N k = (2 * S2Sum N - 2 * HSum N / k) / DeltaDet N`. -/
theorem cMinNorm_eq (N k : ℕ) :
    cMinNorm N k = (2 * S2Sum N - 2 * HSum N / (k : ℝ)) / DeltaDet N := by
  unfold cMinNorm projectAffine lambda1 lambda0
  simp only [zero_div, Finset.sum_const_zero, zero_sub, mul_neg, mul_zero, sub_zero]
  ring

/-- Unconditional membership of `cMinNorm N` in `A_N` for every `N ≥ 2`. -/
theorem cMinNorm_mem_A_N_uncond {N : ℕ} (hN : 2 ≤ N) :
    D1 (cMinNorm N) N = 0 ∧ D0 (cMinNorm N) N = 2 :=
  projectAffine_mem_A_N_uncond (fun _ => 0) hN

/-- Orthogonality of `cMinNorm N` to every vector `h` in the tangent hyperplane `A_N⁰`. -/
theorem cMinNorm_inner_eq_zero {N : ℕ} (h : ℕ → ℝ) (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    ∑ k ∈ Finset.Icc 1 N, cMinNorm N k * h k = 0 := by
  have hterm : ∀ k ∈ Finset.Icc 1 N,
      cMinNorm N k * h k =
        -(lambda0 (fun _ => 0) N) * h k + -(lambda1 (fun _ => 0) N) * (h k / (k : ℝ)) := by
    intro k _
    unfold cMinNorm projectAffine
    ring
  rw [Finset.sum_congr rfl hterm, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum]
  change -(lambda0 (fun _ => 0) N) * D0 h N + -(lambda1 (fun _ => 0) N) * D1 h N = 0
  rw [hh0, hh1, mul_zero, mul_zero, add_zero]

/-- Exact minimum squared `ℓ²`-norm identity `∑ k ∈ Icc 1 N, (cMinNorm N k)^2 = 4 * S2 / Δ`. -/
theorem cMinNorm_norm_sq_eq {N : ℕ} (hΔ : DeltaDet N ≠ 0) :
    ∑ k ∈ Finset.Icc 1 N, cMinNorm N k ^ 2 = 4 * S2Sum N / DeltaDet N := by
  have h1 : D1 (cMinNorm N) N = 0 := projectAffine_D1 (fun _ => 0) N hΔ
  have h0 : D0 (cMinNorm N) N = 2 := projectAffine_D0 (fun _ => 0) N hΔ
  have hterm : ∀ k ∈ Finset.Icc 1 N,
      cMinNorm N k ^ 2 =
        (2 * S2Sum N / DeltaDet N) * cMinNorm N k -
          (2 * HSum N / DeltaDet N) * (cMinNorm N k / (k : ℝ)) := by
    intro k _
    have hc := cMinNorm_eq N k
    rw [sq, hc]
    ring
  rw [Finset.sum_congr rfl hterm, Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum]
  change (2 * S2Sum N / DeltaDet N) * D0 (cMinNorm N) N -
      (2 * HSum N / DeltaDet N) * D1 (cMinNorm N) N = 4 * S2Sum N / DeltaDet N
  rw [h0, h1]
  ring

private lemma tangent_sub_mem {N : ℕ} {c : ℕ → ℝ} (hΔ : DeltaDet N ≠ 0)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) :
    D1 (fun k => c k - cMinNorm N k) N = 0 ∧ D0 (fun k => c k - cMinNorm N k) N = 0 := by
  have hm1 : D1 (cMinNorm N) N = 0 := projectAffine_D1 (fun _ => 0) N hΔ
  have hm0 : D0 (cMinNorm N) N = 2 := projectAffine_D0 (fun _ => 0) N hΔ
  constructor
  · have hsplit :
        D1 (fun k => c k - cMinNorm N k) N = D1 c N - D1 (cMinNorm N) N := by
      unfold D1
      simp_rw [sub_div, Finset.sum_sub_distrib]
    rw [hsplit, hc1, hm1, sub_self]
  · have hsplit :
        D0 (fun k => c k - cMinNorm N k) N = D0 c N - D0 (cMinNorm N) N := by
      unfold D0
      exact Finset.sum_sub_distrib (f := c) (g := cMinNorm N)
    rw [hsplit, hc0, hm0, sub_self]

/-- Exact Pythagorean decomposition on `A_N` (`N ≥ 2`):
`∑_{k=1}^N c_k^2 = 4 * S2Sum N / DeltaDet N + ∑_{k=1}^N (c_k - cMinNorm N k)^2`. -/
theorem norm_sq_eq_cMinNorm_add_sub_sq {N : ℕ} (hN : 2 ≤ N) (c : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) :
    ∑ k ∈ Finset.Icc 1 N, c k ^ 2 =
      4 * S2Sum N / DeltaDet N + ∑ k ∈ Finset.Icc 1 N, (c k - cMinNorm N k) ^ 2 := by
  have hΔ : DeltaDet N ≠ 0 := DeltaDet_ne_zero hN
  have htan := tangent_sub_mem hΔ hc1 hc0
  have horth : ∑ k ∈ Finset.Icc 1 N, cMinNorm N k * (c k - cMinNorm N k) = 0 :=
    cMinNorm_inner_eq_zero (fun k => c k - cMinNorm N k) htan.1 htan.2
  have hterm : ∀ k ∈ Finset.Icc 1 N,
      c k ^ 2 =
        cMinNorm N k ^ 2 + 2 * (cMinNorm N k * (c k - cMinNorm N k)) +
          (c k - cMinNorm N k) ^ 2 := fun _ _ => by ring
  rw [Finset.sum_congr rfl hterm, Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum,
    horth, mul_zero, add_zero, cMinNorm_norm_sq_eq hΔ]

/-- Unconditional minimum-`ℓ²`-norm lower bound on `A_N` (`N ≥ 2`):
`4 * S2Sum N / DeltaDet N ≤ ∑_{k=1}^N c_k^2`. -/
theorem cMinNorm_le_norm_sq_on_A_N {N : ℕ} (hN : 2 ≤ N) (c : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) :
    4 * S2Sum N / DeltaDet N ≤ ∑ k ∈ Finset.Icc 1 N, c k ^ 2 := by
  rw [norm_sq_eq_cMinNorm_add_sub_sq hN c hc1 hc0]
  exact le_add_of_nonneg_right (Finset.sum_nonneg fun _ _ => sq_nonneg _)

/-- Exact rational minimum squared `ℓ²`-norm benchmark at `N = 4`: `164 / 39`. -/
theorem cMinNorm_norm_sq_four :
    ∑ k ∈ Finset.Icc 1 4, cMinNorm 4 k ^ 2 = 164 / 39 := by
  rw [cMinNorm_norm_sq_eq (DeltaDet_ne_zero (by decide : 2 ≤ 4)), S2Sum_four, DeltaDet_four]
  norm_num

/-- Zero-cotangent 2-point anchor `(-2, 4, 0, 0, ...)` on `A_N` (`N ≥ 2`). -/
def cBaseAnchor : ℕ → ℝ
  | 1 => -2
  | 2 => 4
  | _ => 0

private lemma sum_Icc_of_support_two (f : ℕ → ℝ) {N : ℕ} (hN : 2 ≤ N)
    (hf : ∀ k, k ≠ 1 → k ≠ 2 → f k = 0) :
    ∑ k ∈ Finset.Icc 1 N, f k = f 1 + f 2 := by
  have h1 : (1 : ℕ) ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨by omega, by omega⟩
  have h2 : (2 : ℕ) ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨by omega, hN⟩
  have heq : ∀ k ∈ Finset.Icc 1 N,
      f k = (if k = 1 then f 1 else 0) + (if k = 2 then f 2 else 0) := by
    intro k _
    rcases eq_or_ne k 1 with rfl | hk1
    · simp
    · rcases eq_or_ne k 2 with rfl | hk2
      · simp
      · simp [hk1, hk2, hf k hk1 hk2]
  rw [Finset.sum_congr rfl heq, Finset.sum_add_distrib, Finset.sum_ite_eq', Finset.sum_ite_eq']
  simp [h1, h2]

/-- `cBaseAnchor` lies in `A_N` unconditionally for all `N ≥ 2`. -/
theorem cBaseAnchor_mem_A_N {N : ℕ} (hN : 2 ≤ N) :
    D1 cBaseAnchor N = 0 ∧ D0 cBaseAnchor N = 2 := by
  have hD1 : D1 cBaseAnchor N = cBaseAnchor 1 / (1 : ℝ) + cBaseAnchor 2 / (2 : ℝ) := by
    unfold D1
    simpa only [Nat.cast_one, Nat.cast_ofNat] using
      sum_Icc_of_support_two (fun k => cBaseAnchor k / (k : ℝ)) hN
        (fun k hk1 hk2 => by
          have hk : cBaseAnchor k = 0 := by rcases k with _ | _ | _ | k <;> simp [cBaseAnchor] at *
          rw [hk, zero_div])
  have hD0 : D0 cBaseAnchor N = cBaseAnchor 1 + cBaseAnchor 2 :=
    sum_Icc_of_support_two cBaseAnchor hN
      (fun k hk1 hk2 => by rcases k with _ | _ | _ | k <;> simp [cBaseAnchor] at *)
  constructor
  · rw [hD1]; norm_num [cBaseAnchor]
  · rw [hD0]; norm_num [cBaseAnchor]

private lemma vasyuninCotSum_two_anchor (b : ℕ) : vasyuninCotSum 2 b = 0 := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 2 = ({1} : Finset ℕ) by ext x; simp, Finset.sum_singleton,
    show Real.pi * ((1 : ℕ) : ℝ) / ((2 : ℕ) : ℝ) = Real.pi / 2 by push_cast; ring,
    Real.cos_pi_div_two, zero_div, mul_zero]

/-- All Vasyunin cotangent interactions on `{1, 2}` vanish, so `SCot` of `cBaseAnchor` is `0`. -/
theorem SCot_cBaseAnchor_eq_zero (N : ℕ) : SCot vasyuninGCot cBaseAnchor N = 0 := by
  have hV1 : ∀ b : ℕ, vasyuninCotSum 1 b = 0 := fun _ => by simp [vasyuninCotSum]
  have hG12 : vasyuninGCot 1 2 = 0 := by
    unfold vasyuninGCot
    rw [hV1, vasyuninCotSum_two_anchor]
    ring
  unfold SCot QCot
  have hzero :
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
        cBaseAnchor j * cBaseAnchor k * vasyuninGCot j k) = 0 := by
    refine Finset.sum_eq_zero fun j _ => Finset.sum_eq_zero fun k _ => ?_
    rcases j with _ | _ | _ | j <;> rcases k with _ | _ | _ | k <;>
      simp [cBaseAnchor, vasyuninGCot_diag, vasyuninGCot_comm, hG12]
  rw [hzero, neg_zero]

/-- `cBaseAnchor` achieves exact baseline `L²(0, 1)` Nyman-Beurling distance `1` for `N ≥ 2`. -/
theorem cBaseAnchor_l2_dist_eq_one {N : ℕ} (hN : 2 ≤ N) :
    (∫ x in (0 : ℝ)..1,
      (1 - ∑ k ∈ Finset.Icc 1 N, cBaseAnchor k * recipFractScaled k x) ^ 2) = 1 := by
  have ha := cBaseAnchor_mem_A_N hN
  rw [affine_l2_dist_eq_one_sub_scot cBaseAnchor ha.1 ha.2, SCot_cBaseAnchor_eq_zero N, sub_zero]

/-- Local 3-point harmonic wavelet supported on `{m, m + 1, m + 2}` with entries
`(m, -2(m + 1), m + 2)`. -/
def harmonicWavelet (m k : ℕ) : ℝ :=
  if k = m then (m : ℝ)
  else if k = m + 1 then -2 * ((m : ℝ) + 1)
  else if k = m + 2 then (m : ℝ) + 2
  else 0

private lemma sum_Icc_of_support_three (m : ℕ) (f : ℕ → ℝ) {N : ℕ} (hm : 1 ≤ m)
    (hN : m + 2 ≤ N) (hf : ∀ k, k ≠ m → k ≠ m + 1 → k ≠ m + 2 → f k = 0) :
    ∑ k ∈ Finset.Icc 1 N, f k = f m + f (m + 1) + f (m + 2) := by
  have hm0 : m ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨hm, by omega⟩
  have hm1 : m + 1 ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨by omega, by omega⟩
  have hm2 : m + 2 ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨by omega, hN⟩
  have heq : ∀ k ∈ Finset.Icc 1 N,
      f k =
        (if k = m then f m else 0) + (if k = m + 1 then f (m + 1) else 0) +
          (if k = m + 2 then f (m + 2) else 0) := by
    intro k _
    by_cases h0 : k = m
    · subst h0; simp
    · by_cases h1 : k = m + 1
      · subst h1; simp
      · by_cases h2 : k = m + 2
        · subst h2; simp
        · simp [h0, h1, h2, hf k h0 h1 h2]
  rw [Finset.sum_congr rfl heq, Finset.sum_add_distrib, Finset.sum_add_distrib,
    Finset.sum_ite_eq', Finset.sum_ite_eq', Finset.sum_ite_eq']
  simp [hm0, hm1, hm2]

/-- Every local 3-point harmonic wavelet lies unconditionally in `A_N⁰` (`m ≥ 1, m + 2 ≤ N`). -/
theorem harmonicWavelet_mem_tangent {m N : ℕ} (hm : 1 ≤ m) (hN : m + 2 ≤ N) :
    D1 (harmonicWavelet m) N = 0 ∧ D0 (harmonicWavelet m) N = 0 := by
  have hD1 :
      D1 (harmonicWavelet m) N =
        harmonicWavelet m m / (m : ℝ) +
          harmonicWavelet m (m + 1) / ((m + 1 : ℕ) : ℝ) +
            harmonicWavelet m (m + 2) / ((m + 2 : ℕ) : ℝ) :=
    sum_Icc_of_support_three m (fun k => harmonicWavelet m k / (k : ℝ)) hm hN
      (fun k h0 h1 h2 => by simp [harmonicWavelet, h0, h1, h2])
  have hD0 :
      D0 (harmonicWavelet m) N =
        harmonicWavelet m m + harmonicWavelet m (m + 1) + harmonicWavelet m (m + 2) :=
    sum_Icc_of_support_three m (harmonicWavelet m) hm hN
      (fun k h0 h1 h2 => by simp [harmonicWavelet, h0, h1, h2])
  have hw0 : harmonicWavelet m m = (m : ℝ) := by simp [harmonicWavelet]
  have hw1 : harmonicWavelet m (m + 1) = -2 * ((m : ℝ) + 1) := by simp [harmonicWavelet]
  have hw2 : harmonicWavelet m (m + 2) = (m : ℝ) + 2 := by simp [harmonicWavelet]
  have hm_ne : (m : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hm1_ne : (m : ℝ) + 1 ≠ 0 := by positivity
  have hm2_ne : (m : ℝ) + 2 ≠ 0 := by positivity
  constructor
  · rw [hD1, hw0, hw1, hw2]
    push_cast
    have h1 : (m : ℝ) / (m : ℝ) = 1 := div_self hm_ne
    have h2 : (-2 * ((m : ℝ) + 1)) / ((m : ℝ) + 1) = -2 := by field_simp [hm1_ne]
    have h3 : ((m : ℝ) + 2) / ((m : ℝ) + 2) = 1 := div_self hm2_ne
    rw [h1, h2, h3]
    ring
  · rw [hD0, hw0, hw1, hw2]
    ring

/-- Adding any finite linear combination of harmonic wavelets to `cBaseAnchor` stays in `A_N`. -/
theorem cBaseAnchor_add_smul_wavelet_mem_A_N {N : ℕ} (hN : 2 ≤ N)
    (s : Finset ℕ) (w : ℕ → ℝ) (hs : ∀ m ∈ s, 1 ≤ m ∧ m + 2 ≤ N) :
    D1 (fun k => cBaseAnchor k + ∑ m ∈ s, w m * harmonicWavelet m k) N = 0 ∧
      D0 (fun k => cBaseAnchor k + ∑ m ∈ s, w m * harmonicWavelet m k) N = 2 := by
  have ha := cBaseAnchor_mem_A_N hN
  have hsum1 :
      D1 (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N =
        ∑ m ∈ s, w m * D1 (harmonicWavelet m) N := by
    unfold D1
    simp_rw [Finset.sum_div, Finset.sum_comm (s := Finset.Icc 1 N) (t := s),
      mul_div_assoc, ← Finset.mul_sum]
  have hsum0 :
      D0 (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N =
        ∑ m ∈ s, w m * D0 (harmonicWavelet m) N := by
    unfold D0
    simp_rw [Finset.sum_comm (s := Finset.Icc 1 N) (t := s), ← Finset.mul_sum]
  have ht1 : D1 (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N = 0 := by
    rw [hsum1]
    exact Finset.sum_eq_zero fun m hm => by
      rw [(harmonicWavelet_mem_tangent (hs m hm).1 (hs m hm).2).1, mul_zero]
  have ht0 : D0 (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N = 0 := by
    rw [hsum0]
    exact Finset.sum_eq_zero fun m hm => by
      rw [(harmonicWavelet_mem_tangent (hs m hm).1 (hs m hm).2).2, mul_zero]
  constructor
  · have hsplit :
        D1 (fun k => cBaseAnchor k + ∑ m ∈ s, w m * harmonicWavelet m k) N =
          D1 cBaseAnchor N + D1 (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N := by
      unfold D1
      simp_rw [add_div, Finset.sum_add_distrib]
    rw [hsplit, ha.1, ht1, add_zero]
  · have hsplit :
        D0 (fun k => cBaseAnchor k + ∑ m ∈ s, w m * harmonicWavelet m k) N =
          D0 cBaseAnchor N + D0 (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N := by
      unfold D0
      exact Finset.sum_add_distrib
    rw [hsplit, ha.2, ht0, add_zero]

/-- Exact determinant-free wavelet coordinate decomposition of `cVariationalFour`. -/
theorem cVariationalFour_eq_wavelet_decomp (k : ℕ) :
    cVariationalFour k =
      cBaseAnchor k + (19 / 20 : ℝ) * harmonicWavelet 1 k +
        (11 / 40 : ℝ) * harmonicWavelet 2 k := by
  rcases k with _ | _ | _ | _ | _ | k <;>
    simp [cVariationalFour, cBaseAnchor, harmonicWavelet] <;> norm_num

/-- First-level Vasyunin cotangent contrast `deltaCot k = vasyuninCotSum k 2 - vasyuninCotSum k 1`.
-/
noncomputable def deltaCot (k : ℕ) : ℝ :=
  vasyuninCotSum k 2 - vasyuninCotSum k 1

/-- Denominator-free wavelet second-difference identity: multiplying `F k / k` by
`harmonicWavelet m k` cancels `1 / k` identically and yields `F m - 2 * F (m + 1) + F (m + 2)`. -/
theorem harmonicWavelet_div_sum_eq_second_diff (F : ℕ → ℝ) {m N : ℕ}
    (hm : 1 ≤ m) (hN : m + 2 ≤ N) :
    ∑ k ∈ Finset.Icc 1 N, harmonicWavelet m k * (F k / (k : ℝ)) =
      F m - 2 * F (m + 1) + F (m + 2) := by
  have hsup : ∑ k ∈ Finset.Icc 1 N, harmonicWavelet m k * (F k / (k : ℝ)) =
      harmonicWavelet m m * (F m / (m : ℝ)) +
        harmonicWavelet m (m + 1) * (F (m + 1) / ((m + 1 : ℕ) : ℝ)) +
          harmonicWavelet m (m + 2) * (F (m + 2) / ((m + 2 : ℕ) : ℝ)) :=
    sum_Icc_of_support_three m (fun k => harmonicWavelet m k * (F k / (k : ℝ))) hm hN
      (fun k h0 h1 h2 => by simp [harmonicWavelet, h0, h1, h2])
  have hw0 : harmonicWavelet m m = (m : ℝ) := by simp [harmonicWavelet]
  have hw1 : harmonicWavelet m (m + 1) = -2 * ((m : ℝ) + 1) := by simp [harmonicWavelet]
  have hw2 : harmonicWavelet m (m + 2) = (m : ℝ) + 2 := by simp [harmonicWavelet]
  have hm_ne : (m : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hm1_ne : (m : ℝ) + 1 ≠ 0 := by positivity
  have hm2_ne : (m : ℝ) + 2 ≠ 0 := by positivity
  rw [hsup, hw0, hw1, hw2]
  push_cast
  field_simp [hm_ne, hm1_ne, hm2_ne]
  ring

/-- Exact linear cross-cotangent action of the 2-point base anchor `cBaseAnchor`. -/
theorem sum_cBaseAnchor_vasyuninGCot_eq {N : ℕ} (hN : 2 ≤ N) {k : ℕ} (hk : 1 ≤ k) :
    ∑ j ∈ Finset.Icc 1 N, cBaseAnchor j * vasyuninGCot j k =
      (Real.pi / (k : ℝ)) * (vasyuninCotSum k 1 - vasyuninCotSum k 2) := by
  have hsup : ∑ j ∈ Finset.Icc 1 N, cBaseAnchor j * vasyuninGCot j k =
      cBaseAnchor 1 * vasyuninGCot 1 k + cBaseAnchor 2 * vasyuninGCot 2 k :=
    sum_Icc_of_support_two (fun j => cBaseAnchor j * vasyuninGCot j k) hN
      (fun j hj1 hj2 => by
        have hc : cBaseAnchor j = 0 := by rcases j with _ | _ | _ | j <;> simp [cBaseAnchor] at *
        rw [hc, zero_mul])
  have hV1 : vasyuninCotSum 1 k = 0 := by simp [vasyuninCotSum]
  have hk_ne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  rw [hsup]
  unfold vasyuninGCot
  rw [hV1, vasyuninCotSum_two_anchor]
  simp only [cBaseAnchor, Nat.cast_one, Nat.cast_ofNat, zero_add]
  field_simp [hk_ne]
  ring

/-- Unconstrained tangent-space shift identity for `SCot`. -/
theorem SCot_cBaseAnchor_add_eq {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ) :
    SCot vasyuninGCot (fun k => cBaseAnchor k + h k) N =
      SCot vasyuninGCot h N +
        2 * Real.pi * ∑ k ∈ Finset.Icc 1 N,
          (h k / (k : ℝ)) * (vasyuninCotSum k 2 - vasyuninCotSum k 1) := by
  have hterm : ∀ j k : ℕ,
      (cBaseAnchor j + h j) * (cBaseAnchor k + h k) * vasyuninGCot j k =
        (cBaseAnchor j * cBaseAnchor k * vasyuninGCot j k + h j * h k * vasyuninGCot j k) +
          (h k * (cBaseAnchor j * vasyuninGCot j k) +
            h j * (cBaseAnchor k * vasyuninGCot k j)) := by
    intro j k
    rw [vasyuninGCot_comm k j]
    ring
  have hcross_eq :
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, h k * (cBaseAnchor j * vasyuninGCot j k)) =
        ∑ k ∈ Finset.Icc 1 N, h k *
          ((Real.pi / (k : ℝ)) * (vasyuninCotSum k 1 - vasyuninCotSum k 2)) := by
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun k hk => ?_
    rw [← Finset.mul_sum, sum_cBaseAnchor_vasyuninGCot_eq hN (Finset.mem_Icc.mp hk).1]
  have hcross_eq2 :
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, h j * (cBaseAnchor k * vasyuninGCot k j)) =
        ∑ k ∈ Finset.Icc 1 N, h k *
          ((Real.pi / (k : ℝ)) * (vasyuninCotSum k 1 - vasyuninCotSum k 2)) := by
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [← Finset.mul_sum, sum_cBaseAnchor_vasyuninGCot_eq hN (Finset.mem_Icc.mp hj).1]
  have hQCot :
      QCot vasyuninGCot (fun k => cBaseAnchor k + h k) N =
        QCot vasyuninGCot cBaseAnchor N + QCot vasyuninGCot h N +
          2 * ∑ k ∈ Finset.Icc 1 N, h k *
            ((Real.pi / (k : ℝ)) * (vasyuninCotSum k 1 - vasyuninCotSum k 2)) := by
    unfold QCot
    simp_rw [hterm, Finset.sum_add_distrib]
    rw [hcross_eq, hcross_eq2]
    ring
  have hneg :
      -(2 * ∑ k ∈ Finset.Icc 1 N, h k *
          ((Real.pi / (k : ℝ)) * (vasyuninCotSum k 1 - vasyuninCotSum k 2))) =
        2 * Real.pi * ∑ k ∈ Finset.Icc 1 N,
          (h k / (k : ℝ)) * (vasyuninCotSum k 2 - vasyuninCotSum k 1) := by
    rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_neg_distrib]
    refine Finset.sum_congr rfl fun k _ => ?_
    ring
  have hbase : -QCot vasyuninGCot cBaseAnchor N = 0 := by
    simpa [SCot] using SCot_cBaseAnchor_eq_zero N
  unfold SCot
  rw [hQCot]
  linarith [hbase, hneg]

private lemma SCot_smul_wavelet (t : ℝ) (u : ℕ → ℝ) (N : ℕ) :
    SCot vasyuninGCot (fun k => t * u k) N = t ^ 2 * SCot vasyuninGCot u N := by
  unfold SCot QCot
  have hpt : ∀ j k : ℕ,
      (t * u j) * (t * u k) * vasyuninGCot j k = t ^ 2 * (u j * u k * vasyuninGCot j k) :=
    fun _ _ => by ring
  simp_rw [hpt, ← Finset.mul_sum]
  ring

/-- Single-wavelet ray cotangent formula along `cBaseAnchor + t • harmonicWavelet m`. -/
theorem SCot_cBaseAnchor_add_smul_wavelet_eq {m N : ℕ} (hm : 1 ≤ m) (hN : m + 2 ≤ N)
    (t : ℝ) :
    SCot vasyuninGCot (fun k => cBaseAnchor k + t * harmonicWavelet m k) N =
      t ^ 2 * SCot vasyuninGCot (harmonicWavelet m) N +
        2 * Real.pi * t * (deltaCot m - 2 * deltaCot (m + 1) + deltaCot (m + 2)) := by
  rw [SCot_cBaseAnchor_add_eq (by omega : 2 ≤ N) (fun k => t * harmonicWavelet m k),
    SCot_smul_wavelet]
  have hsum :
      (∑ k ∈ Finset.Icc 1 N,
        (t * harmonicWavelet m k / (k : ℝ)) * (vasyuninCotSum k 2 - vasyuninCotSum k 1)) =
        t * (deltaCot m - 2 * deltaCot (m + 1) + deltaCot (m + 2)) := by
    have hpt : ∀ k ∈ Finset.Icc 1 N,
        (t * harmonicWavelet m k / (k : ℝ)) * (vasyuninCotSum k 2 - vasyuninCotSum k 1) =
          t * (harmonicWavelet m k * (deltaCot k / (k : ℝ))) := fun k _ => by
      dsimp [deltaCot]
      ring
    rw [Finset.sum_congr rfl hpt, ← Finset.mul_sum,
      harmonicWavelet_div_sum_eq_second_diff deltaCot hm hN]
  rw [hsum]
  ring

/-- The smooth Vasyunin kernel `GSmooth` vanishes identically as a quadratic form on `A_N⁰`. -/
theorem sum_GSmooth_eq_zero_of_mem_tangent (N : ℕ) (gamma_E : ℝ) (h : ℕ → ℝ)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, h j * h k * GSmooth gamma_E j k = 0 := by
  have h_sum :
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, h j * h k * GSmooth gamma_E j k) =
        ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          (((Real.log (2 * Real.pi) - gamma_E) / 2) *
              (h j * (h k / (k : ℝ)) + (h j / (j : ℝ)) * h k) +
            (1 / 2) * (h j * (h k * Real.log (k : ℝ) / (k : ℝ)) +
              (h j * Real.log (j : ℝ) / (j : ℝ)) * h k) -
            (1 / 2) * ((h j * Real.log (j : ℝ)) * (h k / (k : ℝ)) +
              (h j / (j : ℝ)) * (h k * Real.log (k : ℝ))) -
            (h j / (j : ℝ)) * (h k / (k : ℝ))) := by
    refine Finset.sum_congr rfl fun j hj => Finset.sum_congr rfl fun k hk => ?_
    have hj_ne : (j : ℝ) ≠ 0 := (Nat.cast_pos.mpr (Finset.mem_Icc.mp hj).1).ne'
    have hk_ne : (k : ℝ) ≠ 0 := (Nat.cast_pos.mpr (Finset.mem_Icc.mp hk).1).ne'
    dsimp [GSmooth]
    rw [Real.log_div hk_ne hj_ne]
    field_simp [hj_ne, hk_ne]
    ring
  have hE : ∑ k ∈ Finset.Icc 1 N, h k = 0 := by simpa [D0] using hh0
  have hH : ∑ k ∈ Finset.Icc 1 N, h k / (k : ℝ) = 0 := by simpa [D1] using hh1
  have h_const : ∀ (a : ℝ) (F : ℕ → ℕ → ℝ),
      ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, a * F j k =
        a * ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, F j k := fun _ _ => by
    simp only [← Finset.mul_sum]
  have h_outer : ∀ f g : ℕ → ℝ,
      ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, f j * g k =
        (∑ j ∈ Finset.Icc 1 N, f j) * (∑ k ∈ Finset.Icc 1 N, g k) := fun _ _ => by
    simp only [← Finset.mul_sum, ← Finset.sum_mul]
  rw [h_sum]
  simp only [Finset.sum_sub_distrib, Finset.sum_add_distrib, h_const]
  simp_rw [h_outer, hE, hH]
  ring

/-- **Tangent-Space `L²`-to-Cotangent Isometry**: for any `h ∈ A_N⁰`, the `L²(0, 1)` squared norm
of `∑ k, h k * {1 / (k * x)}` equals `QCot vasyuninGCot h N`. -/
theorem tangent_l2_norm_sq_eq_qcot {N : ℕ} (h : ℕ → ℝ)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    (∫ x in (0 : ℝ)..1, (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2) =
      QCot vasyuninGCot h N := by
  have h_eq :
      (∫ x in (0 : ℝ)..1, (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2) =
        ∫ x in (0 : ℝ)..1,
          ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
            h j * h k * (recipFractScaled j x * recipFractScaled k x) := by
    refine intervalIntegral.integral_congr fun x _ => ?_
    rw [sq, Finset.sum_mul_sum]
    exact Finset.sum_congr rfl fun _ _ => Finset.sum_congr rfl fun _ _ => by ring
  have hint_term : ∀ j ∈ Finset.Icc 1 N, ∀ k ∈ Finset.Icc 1 N,
      IntervalIntegrable (fun x => h j * h k * (recipFractScaled j x * recipFractScaled k x))
        MeasureTheory.volume 0 1 := fun j _ k _ =>
    (intervalIntegrable_recipFractScaled_mul j k 0 1).const_mul _
  have hint_inner : ∀ j ∈ Finset.Icc 1 N, IntervalIntegrable
      (fun x => ∑ k ∈ Finset.Icc 1 N, h j * h k * (recipFractScaled j x * recipFractScaled k x))
      MeasureTheory.volume 0 1 := fun j hj => by
    rw [show (fun x => ∑ k ∈ Finset.Icc 1 N,
        h j * h k * (recipFractScaled j x * recipFractScaled k x)) =
      ∑ k ∈ Finset.Icc 1 N, fun x => h j * h k * (recipFractScaled j x * recipFractScaled k x) by
      funext x; rw [Finset.sum_apply]]
    exact IntervalIntegrable.sum (Finset.Icc 1 N) (hint_term j hj)
  have h_sum_int :
      (∫ x in (0 : ℝ)..1, ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          h j * h k * (recipFractScaled j x * recipFractScaled k x)) =
        ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          h j * h k * ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x := by
    rw [intervalIntegral.integral_finsetSum hint_inner]
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [intervalIntegral.integral_finsetSum (hint_term j hj)]
    simp_rw [intervalIntegral.integral_const_mul]
  rw [h_eq, h_sum_int]
  have h_cross :
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          h j * h k * ∫ x in (0 : ℝ)..1, recipFractScaled j x * recipFractScaled k x) =
        (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
            h j * h k * GSmooth Real.eulerMascheroniConstant j k) +
          QCot vasyuninGCot h N := by
    unfold QCot
    rw [Finset.sum_congr rfl fun j hj => Finset.sum_congr rfl fun k hk => by
      rw [intervalIntegral_recipFractScaled_cross
        (Finset.mem_Icc.mp hj).1 (Finset.mem_Icc.mp hk).1, mul_add]]
    simp only [Finset.sum_add_distrib]
  rw [h_cross, sum_GSmooth_eq_zero_of_mem_tangent N Real.eulerMascheroniConstant h hh1 hh0,
    zero_add]

/-- Unconditional positive semidefiniteness of `QCot vasyuninGCot` on `A_N⁰`. -/
theorem QCot_nonneg_of_mem_tangent {N : ℕ} (h : ℕ → ℝ) (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    0 ≤ QCot vasyuninGCot h N := by
  rw [← tangent_l2_norm_sq_eq_qcot h hh1 hh0]
  exact intervalIntegral.integral_nonneg (by norm_num) fun _ _ => sq_nonneg _

/-- Unconditional negative semidefiniteness of `SCot vasyuninGCot` on `A_N⁰`. -/
theorem SCot_nonpos_of_mem_tangent {N : ℕ} (h : ℕ → ℝ) (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    SCot vasyuninGCot h N ≤ 0 := by
  unfold SCot
  exact neg_nonpos.mpr (QCot_nonneg_of_mem_tangent h hh1 hh0)

private lemma cot_pi_div_three_tan : Real.cos (Real.pi / 3) / Real.sin (Real.pi / 3) = 1 / √3 := by
  rw [Real.cos_pi_div_three, Real.sin_pi_div_three]
  field_simp [(Real.sqrt_pos.mpr (by norm_num : (0 : ℝ) < 3)).ne']

private lemma cot_two_pi_div_three_tan :
    Real.cos (2 * Real.pi / 3) / Real.sin (2 * Real.pi / 3) = -(1 / √3) := by
  rw [show 2 * Real.pi / 3 = Real.pi - Real.pi / 3 by ring, Real.cos_pi_sub, Real.sin_pi_sub,
    neg_div, cot_pi_div_three_tan]

private lemma vasyuninCotSum_three_tan (b : ℕ) :
    vasyuninCotSum 3 b =
      (Int.fract ((b : ℝ) / 3) - Int.fract (2 * (b : ℝ) / 3)) * (1 / √3) := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 3 = ({1, 2} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide), Finset.sum_singleton]
  push_cast
  rw [show (1 : ℝ) * b / 3 = b / 3 by ring, show Real.pi * 1 / 3 = Real.pi / 3 by ring,
    show Real.pi * 2 / 3 = 2 * Real.pi / 3 by ring, cot_pi_div_three_tan, cot_two_pi_div_three_tan]
  ring

private lemma sum_Icc_one_three_tan (f : ℕ → ℝ) :
    ∑ k ∈ Finset.Icc 1 3, f k = f 1 + f 2 + f 3 := by
  have hI : Finset.Icc 1 3 = ({1, 2, 3} : Finset ℕ) := by
    ext x; simp only [Finset.mem_Icc, Finset.mem_insert, Finset.mem_singleton]; omega
  rw [hI]
  norm_num [Finset.sum_insert, add_assoc]

/-- Exact cotangent quadratic energy of the first harmonic wavelet `(1, -4, 3)` at `N = 3`. -/
theorem QCot_harmonicWavelet_one_eq :
    QCot vasyuninGCot (harmonicWavelet 1) 3 = Real.pi / Real.sqrt 3 := by
  unfold QCot
  simp_rw [sum_Icc_one_three_tan]
  rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3,
    vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 3 2,
    vasyuninGCot_one_two, vasyuninGCot_one_three, vasyuninGCot_two_three]
  simp [harmonicWavelet]
  ring

/-- Exact `L²(0, 1)` squared norm of the first harmonic wavelet `(1, -4, 3)`: `π / √3`. -/
theorem harmonicWavelet_one_l2_norm_sq_eq :
    (∫ x in (0 : ℝ)..1,
      (∑ k ∈ Finset.Icc 1 3, harmonicWavelet 1 k * recipFractScaled k x) ^ 2) =
      Real.pi / Real.sqrt 3 := by
  have ht := harmonicWavelet_mem_tangent (m := 1) (N := 3) (by decide) (by decide)
  rw [tangent_l2_norm_sq_eq_qcot (harmonicWavelet 1) ht.1 ht.2, QCot_harmonicWavelet_one_eq]

/-- Exact `N = 3` variational optimum `SCot` at step size `t = 2 / 3`: `4 * π / (9 * √3)`. -/
theorem SCot_cBaseAnchor_add_two_thirds_wavelet_one_eq :
    SCot vasyuninGCot (fun k => cBaseAnchor k + (2 / 3 : ℝ) * harmonicWavelet 1 k) 3 =
      4 * Real.pi / (9 * Real.sqrt 3) := by
  rw [SCot_cBaseAnchor_add_smul_wavelet_eq (m := 1) (N := 3) (by decide) (by decide) (2 / 3)]
  have hS : SCot vasyuninGCot (harmonicWavelet 1) 3 = -(Real.pi / Real.sqrt 3) := by
    unfold SCot
    rw [QCot_harmonicWavelet_one_eq]
  have hd1 : deltaCot 1 = 0 := by simp [deltaCot, vasyuninCotSum]
  have hd2 : deltaCot 2 = 0 := by
    dsimp [deltaCot]
    rw [vasyuninCotSum_two_anchor, vasyuninCotSum_two_anchor, sub_self]
  have hd3 : deltaCot 3 = 2 / (3 * Real.sqrt 3) := by
    dsimp [deltaCot]
    rw [vasyuninCotSum_three_tan, vasyuninCotSum_three_tan]
    norm_num
    ring
  rw [hS, hd1, hd2, hd3]
  ring

/-- Linear `1 / k`-weighted cotangent drive `∑ k ∈ Icc 1 N, (h k / k) * deltaCot k`. -/
noncomputable def linearCotDrive (h : ℕ → ℝ) (N : ℕ) : ℝ :=
  ∑ k ∈ Finset.Icc 1 N, (h k / (k : ℝ)) * deltaCot k

/-- Optimal scalar step size along a tangent direction `h` anchored at `cBaseAnchor`. -/
noncomputable def optTangentStep (h : ℕ → ℝ) (N : ℕ) : ℝ :=
  Real.pi * linearCotDrive h N / QCot vasyuninGCot h N

/-- Scale-invariant tangent Rayleigh quotient
`(π * linearCotDrive h N)^2 / QCot vasyuninGCot h N`. -/
noncomputable def tangentRayleighQuotient (h : ℕ → ℝ) (N : ℕ) : ℝ :=
  (Real.pi * linearCotDrive h N) ^ 2 / QCot vasyuninGCot h N

private lemma SCot_smul_rayleigh (t : ℝ) (h : ℕ → ℝ) (N : ℕ) :
    SCot vasyuninGCot (fun k => t * h k) N = -(t ^ 2 * QCot vasyuninGCot h N) := by
  unfold SCot QCot
  have hpt : ∀ j k : ℕ,
      (t * h j) * (t * h k) * vasyuninGCot j k = t ^ 2 * (h j * h k * vasyuninGCot j k) :=
    fun _ _ => by ring
  simp_rw [hpt, ← Finset.mul_sum]

private lemma SCot_cBaseAnchor_add_smul_linear {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ) (t : ℝ) :
    SCot vasyuninGCot (fun k => cBaseAnchor k + t * h k) N =
      -(t ^ 2 * QCot vasyuninGCot h N) + 2 * Real.pi * t * linearCotDrive h N := by
  rw [SCot_cBaseAnchor_add_eq hN (fun k => t * h k), SCot_smul_rayleigh]
  have hsum :
      (∑ k ∈ Finset.Icc 1 N,
        (t * h k / (k : ℝ)) * (vasyuninCotSum k 2 - vasyuninCotSum k 1)) =
        t * linearCotDrive h N := by
    have hpt : ∀ k ∈ Finset.Icc 1 N,
        (t * h k / (k : ℝ)) * (vasyuninCotSum k 2 - vasyuninCotSum k 1) =
          t * ((h k / (k : ℝ)) * deltaCot k) := fun k _ => by
      dsimp [deltaCot]
      ring
    rw [Finset.sum_congr rfl hpt, ← Finset.mul_sum]
    rfl
  rw [hsum]
  ring

/-- Exact completing-the-square identity along any tangent ray `cBaseAnchor + t • h` whenever
`QCot vasyuninGCot h N ≠ 0`. -/
theorem SCot_cBaseAnchor_add_smul_eq_rayleigh_sub_sq {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ)
    (hq : QCot vasyuninGCot h N ≠ 0) (t : ℝ) :
    SCot vasyuninGCot (fun k => cBaseAnchor k + t * h k) N =
      tangentRayleighQuotient h N -
        QCot vasyuninGCot h N * (t - optTangentStep h N) ^ 2 := by
  rw [SCot_cBaseAnchor_add_smul_linear hN h t]
  dsimp [tangentRayleighQuotient, optTangentStep]
  field_simp [hq]
  ring

/-- Optimal ray achievement at `t = optTangentStep h N`:
`SCot vasyuninGCot (cBaseAnchor + optTangentStep h N • h) N = tangentRayleighQuotient h N`. -/
theorem SCot_cBaseAnchor_add_optTangentStep_eq {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ)
    (hq : QCot vasyuninGCot h N ≠ 0) :
    SCot vasyuninGCot (fun k => cBaseAnchor k + optTangentStep h N * h k) N =
      tangentRayleighQuotient h N := by
  rw [SCot_cBaseAnchor_add_smul_eq_rayleigh_sub_sq hN h hq (optTangentStep h N), sub_self,
    zero_pow (by decide), mul_zero, sub_zero]

private lemma cBaseAnchor_add_tangent_mem_A_N {N : ℕ} (hN : 2 ≤ N) {h : ℕ → ℝ}
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) (t : ℝ) :
    D1 (fun k => cBaseAnchor k + t * h k) N = 0 ∧
      D0 (fun k => cBaseAnchor k + t * h k) N = 2 := by
  have ha := cBaseAnchor_mem_A_N hN
  constructor
  · have hsplit : D1 (fun k => cBaseAnchor k + t * h k) N = D1 cBaseAnchor N + t * D1 h N := by
      unfold D1
      have hpt : ∀ k ∈ Finset.Icc 1 N,
          (cBaseAnchor k + t * h k) / (k : ℝ) = cBaseAnchor k / (k : ℝ) + t * (h k / (k : ℝ)) :=
        fun _ _ => by ring
      rw [Finset.sum_congr rfl hpt, Finset.sum_add_distrib, ← Finset.mul_sum]
    rw [hsplit, ha.1, hh1, mul_zero, add_zero]
  · have hsplit : D0 (fun k => cBaseAnchor k + t * h k) N = D0 cBaseAnchor N + t * D0 h N := by
      unfold D0
      simp_rw [Finset.sum_add_distrib, ← Finset.mul_sum]
    rw [hsplit, ha.2, hh0, mul_zero, add_zero]

private lemma SCot_cBaseAnchor_add_smul_le_one {N : ℕ} (hN : 2 ≤ N) {h : ℕ → ℝ}
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) (t : ℝ) :
    SCot vasyuninGCot (fun k => cBaseAnchor k + t * h k) N ≤ 1 := by
  have hc := cBaseAnchor_add_tangent_mem_A_N hN hh1 hh0 t
  have hnonneg :
      0 ≤ ∫ x in (0 : ℝ)..1,
        (1 - ∑ k ∈ Finset.Icc 1 N, (cBaseAnchor k + t * h k) * recipFractScaled k x) ^ 2 :=
    intervalIntegral.integral_nonneg (by norm_num) fun _ _ => sq_nonneg _
  rw [affine_l2_dist_eq_one_sub_scot (fun k => cBaseAnchor k + t * h k) hc.1 hc.2] at hnonneg
  linarith

/-- **Unconditional Cotangent Cauchy–Schwarz Inequality on `A_N⁰`**: for every `N ≥ 2` and every
tangent vector `h ∈ A_N⁰`, `(π * linearCotDrive h N)^2 ≤ QCot vasyuninGCot h N`. -/
theorem sq_linearCotDrive_le_qcot {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    (Real.pi * linearCotDrive h N) ^ 2 ≤ QCot vasyuninGCot h N := by
  have hQ_nn : 0 ≤ QCot vasyuninGCot h N := QCot_nonneg_of_mem_tangent h hh1 hh0
  rcases lt_or_eq_of_le hQ_nn with hQ_pos | hQ_zero
  · have hle : tangentRayleighQuotient h N ≤ 1 := by
      rw [← SCot_cBaseAnchor_add_optTangentStep_eq hN h hQ_pos.ne']
      exact SCot_cBaseAnchor_add_smul_le_one hN hh1 hh0 (optTangentStep h N)
    exact (div_le_one hQ_pos).mp hle
  · rw [← hQ_zero]
    by_cases hL : Real.pi * linearCotDrive h N = 0
    · rw [hL, zero_pow (by decide)]
    · exfalso
      have hsc := SCot_cBaseAnchor_add_smul_le_one hN hh1 hh0 (1 / (Real.pi * linearCotDrive h N))
      rw [SCot_cBaseAnchor_add_smul_linear hN h (1 / (Real.pi * linearCotDrive h N)), ← hQ_zero,
        mul_zero, neg_zero, zero_add] at hsc
      have h2 : 2 * Real.pi * (1 / (Real.pi * linearCotDrive h N)) * linearCotDrive h N = 2 := by
        rw [show 2 * Real.pi * (1 / (Real.pi * linearCotDrive h N)) * linearCotDrive h N =
          2 * ((Real.pi * linearCotDrive h N) * (1 / (Real.pi * linearCotDrive h N))) by ring,
          mul_one_div_cancel hL, mul_one]
      linarith

/-- Unconditional scale-invariant ceiling `tangentRayleighQuotient h N ≤ 1` for all `N ≥ 2` and
every tangent vector `h ∈ A_N⁰`. -/
theorem tangentRayleighQuotient_le_one {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    tangentRayleighQuotient h N ≤ 1 := by
  have hQ_nn : 0 ≤ QCot vasyuninGCot h N := QCot_nonneg_of_mem_tangent h hh1 hh0
  rcases lt_or_eq_of_le hQ_nn with hQ_pos | hQ_zero
  · exact (div_le_one hQ_pos).mpr (sq_linearCotDrive_le_qcot hN h hh1 hh0)
  · dsimp [tangentRayleighQuotient]
    rw [← hQ_zero, div_zero]
    norm_num

private lemma linearCotDrive_wavelet_one_eq :
    linearCotDrive (harmonicWavelet 1) 3 = 2 / (3 * Real.sqrt 3) := by
  have hrew : linearCotDrive (harmonicWavelet 1) 3 =
      ∑ k ∈ Finset.Icc 1 3, harmonicWavelet 1 k * (deltaCot k / (k : ℝ)) :=
    Finset.sum_congr rfl fun k _ => by ring
  have hdrv : linearCotDrive (harmonicWavelet 1) 3 =
      deltaCot 1 - 2 * deltaCot 2 + deltaCot 3 := by
    rw [hrew]
    exact harmonicWavelet_div_sum_eq_second_diff deltaCot
      (by decide : 1 ≤ 1) (by decide : 1 + 2 ≤ 3)
  have hd1 : deltaCot 1 = 0 := by simp [deltaCot, vasyuninCotSum]
  have hd2 : deltaCot 2 = 0 := by
    dsimp [deltaCot]; rw [vasyuninCotSum_two_anchor, vasyuninCotSum_two_anchor, sub_self]
  have hd3 : deltaCot 3 = 2 / (3 * Real.sqrt 3) := by
    dsimp [deltaCot]; rw [vasyuninCotSum_three_tan, vasyuninCotSum_three_tan]; norm_num; ring
  rw [hdrv, hd1, hd2, hd3]
  ring

/-- Exact completing-the-square ray formula along `cBaseAnchor + t • harmonicWavelet 1` at `N = 3`.
-/
theorem SCot_cBaseAnchor_add_smul_wavelet_one_eq_completing_sq (t : ℝ) :
    SCot vasyuninGCot (fun k => cBaseAnchor k + t * harmonicWavelet 1 k) 3 =
      4 * Real.pi / (9 * Real.sqrt 3) - (Real.pi / Real.sqrt 3) * (t - 2 / 3) ^ 2 := by
  have hQ_ne : QCot vasyuninGCot (harmonicWavelet 1) 3 ≠ 0 := by
    rw [QCot_harmonicWavelet_one_eq]; positivity
  rw [SCot_cBaseAnchor_add_smul_eq_rayleigh_sub_sq (by decide : 2 ≤ 3) (harmonicWavelet 1) hQ_ne t]
  have hsq3_ne : Real.sqrt 3 ≠ 0 := (Real.sqrt_pos.mpr (by norm_num)).ne'
  have hpi_ne : Real.pi ≠ 0 := Real.pi_pos.ne'
  have hopt : optTangentStep (harmonicWavelet 1) 3 = 2 / 3 := by
    dsimp [optTangentStep]
    rw [linearCotDrive_wavelet_one_eq, QCot_harmonicWavelet_one_eq]
    field_simp [hsq3_ne, hpi_ne]
  have hray : tangentRayleighQuotient (harmonicWavelet 1) 3 = 4 * Real.pi / (9 * Real.sqrt 3) := by
    dsimp [tangentRayleighQuotient]
    rw [linearCotDrive_wavelet_one_eq, QCot_harmonicWavelet_one_eq]
    field_simp [hsq3_ne, hpi_ne]
    ring
  rw [hopt, hray, QCot_harmonicWavelet_one_eq]

/-- Global variational optimality on `A_3`: along `cBaseAnchor + t • harmonicWavelet 1`,
`SCot` is globally bounded above by `4 * π / (9 * √3)` for every `t : ℝ`. -/
theorem SCot_cBaseAnchor_add_smul_wavelet_one_le (t : ℝ) :
    SCot vasyuninGCot (fun k => cBaseAnchor k + t * harmonicWavelet 1 k) 3 ≤
      4 * Real.pi / (9 * Real.sqrt 3) := by
  rw [SCot_cBaseAnchor_add_smul_wavelet_one_eq_completing_sq t]
  have hsq_nn : 0 ≤ (Real.pi / Real.sqrt 3) * (t - 2 / 3) ^ 2 := by positivity
  linarith

private lemma sum_Icc_one_four_opt (f : ℕ → ℝ) :
    ∑ k ∈ Finset.Icc 1 4, f k = f 1 + f 2 + f 3 + f 4 := by
  rw [show Finset.Icc 1 4 = ({1, 2, 3, 4} : Finset ℕ) by
    ext x; simp only [Finset.mem_Icc, Finset.mem_insert, Finset.mem_singleton]; omega]
  norm_num [Finset.sum_insert, add_assoc]

/-- Exact 2-wavelet completeness on `A_4`: every vector `c ∈ A_4` agrees on `{1, 2, 3, 4}` with
`cBaseAnchor + (c 1 + 2) • harmonicWavelet 1 + (c 4 / 4) • harmonicWavelet 2`. -/
theorem eq_cBaseAnchor_add_wavelets_of_mem_A_four (c : ℕ → ℝ)
    (hc1 : D1 c 4 = 0) (hc0 : D0 c 4 = 2) {k : ℕ} (hk : k ∈ Finset.Icc 1 4) :
    c k = cBaseAnchor k + (c 1 + 2) * harmonicWavelet 1 k +
      (c 4 / 4) * harmonicWavelet 2 k := by
  unfold D1 at hc1
  unfold D0 at hc0
  rw [sum_Icc_one_four_opt] at hc1 hc0
  norm_num at hc1 hc0
  rcases Finset.mem_Icc.mp hk with ⟨hk1, hk4⟩
  interval_cases k <;> simp [cBaseAnchor, harmonicWavelet] <;> linarith

private lemma cot_pi_div_three_opt : Real.cos (Real.pi / 3) / Real.sin (Real.pi / 3) = 1 / √3 := by
  rw [Real.cos_pi_div_three, Real.sin_pi_div_three]
  field_simp [(Real.sqrt_pos.mpr (by norm_num : (0 : ℝ) < 3)).ne']

private lemma cot_two_pi_div_three_opt :
    Real.cos (2 * Real.pi / 3) / Real.sin (2 * Real.pi / 3) = -(1 / √3) := by
  rw [show 2 * Real.pi / 3 = Real.pi - Real.pi / 3 by ring, Real.cos_pi_sub, Real.sin_pi_sub,
    neg_div, cot_pi_div_three_opt]

private lemma cot_pi_div_four_opt : Real.cos (Real.pi / 4) / Real.sin (Real.pi / 4) = 1 := by
  rw [Real.cos_pi_div_four, Real.sin_pi_div_four]
  field_simp [(Real.sqrt_pos.mpr (by norm_num : (0 : ℝ) < 2)).ne']

private lemma vasyuninCotSum_two_opt (b : ℕ) : vasyuninCotSum 2 b = 0 := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 2 = ({1} : Finset ℕ) by ext x; simp, Finset.sum_singleton,
    show Real.pi * ((1 : ℕ) : ℝ) / ((2 : ℕ) : ℝ) = Real.pi / 2 by push_cast; ring,
    Real.cos_pi_div_two, zero_div, mul_zero]

private lemma vasyuninCotSum_three_opt (b : ℕ) :
    vasyuninCotSum 3 b =
      (Int.fract ((b : ℝ) / 3) - Int.fract (2 * (b : ℝ) / 3)) * (1 / √3) := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 3 = ({1, 2} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide), Finset.sum_singleton]
  push_cast
  rw [show (1 : ℝ) * b / 3 = b / 3 by ring, show Real.pi * 1 / 3 = Real.pi / 3 by ring,
    show Real.pi * 2 / 3 = 2 * Real.pi / 3 by ring, cot_pi_div_three_opt, cot_two_pi_div_three_opt]
  ring

private lemma vasyuninCotSum_four_opt (b : ℕ) :
    vasyuninCotSum 4 b = Int.fract ((b : ℝ) / 4) - Int.fract (3 * (b : ℝ) / 4) := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 4 = ({1, 2, 3} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton]
  push_cast
  rw [show (1 : ℝ) * b / 4 = b / 4 by ring, show Real.pi * 1 / 4 = Real.pi / 4 by ring,
    show Real.pi * 2 / 4 = Real.pi / 2 by ring, Real.cos_pi_div_two, zero_div, mul_zero,
    show Real.pi * 3 / 4 = 3 * Real.pi / 4 by ring, cot_pi_div_four_opt,
    show Real.cos (3 * Real.pi / 4) / Real.sin (3 * Real.pi / 4) = -1 by
      rw [show 3 * Real.pi / 4 = Real.pi - Real.pi / 4 by ring, Real.cos_pi_sub, Real.sin_pi_sub,
        neg_div, cot_pi_div_four_opt]]
  ring

private lemma vasyuninGCot_one_two_opt : vasyuninGCot 1 2 = 0 := by
  have hV1 : vasyuninCotSum 1 2 = 0 := by simp [vasyuninCotSum]
  unfold vasyuninGCot; rw [hV1, vasyuninCotSum_two_opt]; ring

private lemma vasyuninGCot_one_three_opt : vasyuninGCot 1 3 = Real.pi / (18 * √3) := by
  have hV1 : vasyuninCotSum 1 3 = 0 := by simp [vasyuninCotSum]
  unfold vasyuninGCot; rw [hV1, vasyuninCotSum_three_opt]; norm_num; ring

private lemma vasyuninGCot_one_four_opt : vasyuninGCot 1 4 = Real.pi / 16 := by
  have hV1 : vasyuninCotSum 1 4 = 0 := by simp [vasyuninCotSum]
  unfold vasyuninGCot; rw [hV1, vasyuninCotSum_four_opt]; norm_num; ring

private lemma vasyuninGCot_two_three_opt : vasyuninGCot 2 3 = -(Real.pi / (36 * √3)) := by
  unfold vasyuninGCot; rw [vasyuninCotSum_two_opt, vasyuninCotSum_three_opt]; norm_num; ring

private lemma vasyuninGCot_two_four_opt : vasyuninGCot 2 4 = 0 := by
  unfold vasyuninGCot; rw [vasyuninCotSum_two_opt, vasyuninCotSum_four_opt]; norm_num

private lemma vasyuninGCot_three_four_opt :
    vasyuninGCot 3 4 = Real.pi / (72 * √3) - Real.pi / 48 := by
  unfold vasyuninGCot; rw [vasyuninCotSum_three_opt, vasyuninCotSum_four_opt]; norm_num; ring

/-- Exact cotangent quadratic energy of the second harmonic wavelet `(0, 2, -6, 4)` at `N = 4`:
`QCot vasyuninGCot (harmonicWavelet 2) 4 = π`. -/
theorem QCot_harmonicWavelet_two_eq :
    QCot vasyuninGCot (harmonicWavelet 2) 4 = Real.pi := by
  unfold QCot
  simp_rw [sum_Icc_one_four_opt]
  rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3, vasyuninGCot_diag 4,
    vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 4 1,
    vasyuninGCot_comm 3 2, vasyuninGCot_comm 4 2, vasyuninGCot_comm 4 3,
    vasyuninGCot_one_two_opt, vasyuninGCot_one_three_opt, vasyuninGCot_one_four_opt,
    vasyuninGCot_two_three_opt, vasyuninGCot_two_four_opt, vasyuninGCot_three_four_opt]
  simp [harmonicWavelet]
  ring

/-- Exact 2-wavelet orthogonal diagonalization of `SCot` on `A_4`: completing the two squares in
`t₁ - t₂` and `t₂` around the global KKT optimum `((19 + √3) / 72) * π`. -/
theorem SCot_cBaseAnchor_add_two_wavelets_eq (t₁ t₂ : ℝ) :
    SCot vasyuninGCot
        (fun k => cBaseAnchor k + t₁ * harmonicWavelet 1 k + t₂ * harmonicWavelet 2 k) 4 =
      ((19 + Real.sqrt 3) / 72) * Real.pi -
        (Real.pi / Real.sqrt 3) * ((t₁ - t₂) - 2 / 3) ^ 2 -
          Real.pi * (1 - 1 / Real.sqrt 3) * (t₂ - (5 - Real.sqrt 3) / 12) ^ 2 := by
  have hsq3_ne : Real.sqrt 3 ≠ 0 := (Real.sqrt_pos.mpr (by norm_num)).ne'
  have hsq3_sq : Real.sqrt 3 ^ 2 = 3 := Real.sq_sqrt (by norm_num)
  unfold SCot QCot
  simp_rw [sum_Icc_one_four_opt]
  rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3, vasyuninGCot_diag 4,
    vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 4 1,
    vasyuninGCot_comm 3 2, vasyuninGCot_comm 4 2, vasyuninGCot_comm 4 3,
    vasyuninGCot_one_two_opt, vasyuninGCot_one_three_opt, vasyuninGCot_one_four_opt,
    vasyuninGCot_two_three_opt, vasyuninGCot_two_four_opt, vasyuninGCot_three_four_opt]
  simp [cBaseAnchor, harmonicWavelet]
  field_simp [hsq3_ne]
  ring_nf
  have hsq3_3 : Real.sqrt 3 ^ 3 = 3 * Real.sqrt 3 := by rw [pow_succ, hsq3_sq]
  simp only [hsq3_sq, hsq3_3]
  ring

/-- Exact closed-form global KKT optimizer on `A_4` in `2`-wavelet coordinates. -/
noncomputable def cGlobalOptFour (k : ℕ) : ℝ :=
  cBaseAnchor k + ((13 - Real.sqrt 3) / 12) * harmonicWavelet 1 k +
    ((5 - Real.sqrt 3) / 12) * harmonicWavelet 2 k

/-- Exact verification that the global KKT optimizer `cGlobalOptFour` lies in `A_4`. -/
theorem cGlobalOptFour_mem_A_N : D1 cGlobalOptFour 4 = 0 ∧ D0 cGlobalOptFour 4 = 2 := by
  unfold D1 D0
  rw [sum_Icc_one_four_opt, sum_Icc_one_four_opt]
  norm_num [cGlobalOptFour, cBaseAnchor, harmonicWavelet]
  constructor <;> ring

/-- Exact closed-form maximum of `SCot` on `A_4`: `((19 + √3) / 72) * π`. -/
theorem SCot_cGlobalOptFour_eq :
    SCot vasyuninGCot cGlobalOptFour 4 = ((19 + Real.sqrt 3) / 72) * Real.pi := by
  have h := SCot_cBaseAnchor_add_two_wavelets_eq
    ((13 - Real.sqrt 3) / 12) ((5 - Real.sqrt 3) / 12)
  have hfn :
      (fun k => cBaseAnchor k + ((13 - Real.sqrt 3) / 12) * harmonicWavelet 1 k +
        ((5 - Real.sqrt 3) / 12) * harmonicWavelet 2 k) = cGlobalOptFour := rfl
  rw [hfn] at h
  rw [h]
  ring

/-- Global optimality upper bound for `SCot` over all of `A_4`: every vector `c ∈ A_4` satisfies
`SCot vasyuninGCot c 4 ≤ ((19 + √3) / 72) * π`. -/
theorem SCot_le_cGlobalOptFour_of_mem_A_four (c : ℕ → ℝ)
    (hc1 : D1 c 4 = 0) (hc0 : D0 c 4 = 2) :
    SCot vasyuninGCot c 4 ≤ ((19 + Real.sqrt 3) / 72) * Real.pi := by
  let t₁ := c 1 + 2
  let t₂ := c 4 / 4
  have heq :
      SCot vasyuninGCot c 4 =
        SCot vasyuninGCot
          (fun k => cBaseAnchor k + t₁ * harmonicWavelet 1 k + t₂ * harmonicWavelet 2 k) 4 := by
    unfold SCot QCot
    congr 1
    refine Finset.sum_congr rfl fun j hj => Finset.sum_congr rfl fun k hk => ?_
    rw [eq_cBaseAnchor_add_wavelets_of_mem_A_four c hc1 hc0 hj,
      eq_cBaseAnchor_add_wavelets_of_mem_A_four c hc1 hc0 hk]
  rw [heq, SCot_cBaseAnchor_add_two_wavelets_eq t₁ t₂]
  have hsq3_gt : (1 : ℝ) < Real.sqrt 3 := by
    nlinarith [Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 3), Real.sqrt_nonneg 3]
  have h1_nn : 0 ≤ (Real.pi / Real.sqrt 3) * ((t₁ - t₂) - 2 / 3) ^ 2 := by positivity
  have h2_nn :
      0 ≤ Real.pi * (1 - 1 / Real.sqrt 3) * (t₂ - (5 - Real.sqrt 3) / 12) ^ 2 := by
    have hcoeff : 0 ≤ 1 - 1 / Real.sqrt 3 := by
      have : 1 / Real.sqrt 3 < 1 := (div_lt_one (by linarith)).mpr hsq3_gt
      linarith
    have hpi : 0 ≤ Real.pi := Real.pi_pos.le
    positivity
  linarith

/-- Global Nyman–Beurling `L²(0, 1)` lower bound over all of `A_4`: no vector in `A_4` achieves an
`L²(0, 1)` distance below `1 - ((19 + √3) / 72) * π`. -/
theorem l2_dist_cGlobalOptFour_le_of_mem_A_four (c : ℕ → ℝ)
    (hc1 : D1 c 4 = 0) (hc0 : D0 c 4 = 2) :
    1 - ((19 + Real.sqrt 3) / 72) * Real.pi ≤
      ∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 4, c k * recipFractScaled k x) ^ 2 := by
  rw [affine_l2_dist_eq_one_sub_scot c hc1 hc0]
  exact sub_le_sub_left (SCot_le_cGlobalOptFour_of_mem_A_four c hc1 hc0) 1

private lemma linearCotDrive_smul (a : ℝ) (h : ℕ → ℝ) (N : ℕ) :
    linearCotDrive (fun k => a * h k) N = a * linearCotDrive h N := by
  unfold linearCotDrive
  have hpt : ∀ k ∈ Finset.Icc 1 N,
      (a * h k / (k : ℝ)) * deltaCot k = a * ((h k / (k : ℝ)) * deltaCot k) :=
    fun _ _ => by ring
  rw [Finset.sum_congr rfl hpt, ← Finset.mul_sum]

private lemma QCot_smul (a : ℝ) (h : ℕ → ℝ) (N : ℕ) :
    QCot vasyuninGCot (fun k => a * h k) N = a ^ 2 * QCot vasyuninGCot h N := by
  unfold QCot
  have hpt : ∀ j ∈ Finset.Icc 1 N, ∀ k ∈ Finset.Icc 1 N,
      (a * h j) * (a * h k) * vasyuninGCot j k =
        a ^ 2 * (h j * h k * vasyuninGCot j k) := fun _ _ _ _ => by ring
  rw [Finset.sum_congr rfl fun j hj => Finset.sum_congr rfl fun k hk => hpt j hj k hk]
  simp_rw [← Finset.mul_sum]

/-- Exact scale invariance of the tangent Rayleigh quotient: for any `a ≠ 0`, rescaling a
direction `h` leaves `tangentRayleighQuotient` unchanged. -/
theorem tangentRayleighQuotient_smul (a : ℝ) (ha : a ≠ 0) (h : ℕ → ℝ) (N : ℕ) :
    tangentRayleighQuotient (fun k => a * h k) N = tangentRayleighQuotient h N := by
  unfold tangentRayleighQuotient
  rw [linearCotDrive_smul, QCot_smul,
    show (Real.pi * (a * linearCotDrive h N)) ^ 2 =
      a ^ 2 * (Real.pi * linearCotDrive h N) ^ 2 by ring,
    mul_div_mul_left _ _ (pow_ne_zero 2 ha)]

/-- Multi-wavelet tangent membership: any finite linear combination of 3-point harmonic wavelets
supported inside `Icc 1 N` satisfies `D1 h N = 0 ∧ D0 h N = 0`. -/
theorem sum_smul_harmonicWavelet_mem_tangent {N : ℕ} (s : Finset ℕ)
    (hs : ∀ m ∈ s, 1 ≤ m ∧ m + 2 ≤ N) (w : ℕ → ℝ) :
    D1 (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N = 0 ∧
      D0 (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N = 0 := by
  constructor
  · unfold D1
    have hpt : ∀ k ∈ Finset.Icc 1 N,
        (∑ m ∈ s, w m * harmonicWavelet m k) / (k : ℝ) =
          ∑ m ∈ s, w m * (harmonicWavelet m k / (k : ℝ)) := by
      intro k _
      rw [Finset.sum_div]
      exact Finset.sum_congr rfl fun m _ => by ring
    rw [Finset.sum_congr rfl hpt, Finset.sum_comm]
    refine Finset.sum_eq_zero fun m hm => ?_
    rw [← Finset.mul_sum]
    have hmem := (harmonicWavelet_mem_tangent (hs m hm).1 (hs m hm).2).1
    unfold D1 at hmem
    rw [hmem, mul_zero]
  · unfold D0
    rw [Finset.sum_comm]
    refine Finset.sum_eq_zero fun m hm => ?_
    rw [← Finset.mul_sum]
    have hmem := (harmonicWavelet_mem_tangent (hs m hm).1 (hs m hm).2).2
    unfold D0 at hmem
    rw [hmem, mul_zero]

/-- Linear decomposition of `linearCotDrive` on any multi-wavelet tangent vector into unweighted
second differences of `deltaCot`. -/
theorem linearCotDrive_sum_harmonicWavelet_eq {N : ℕ} (s : Finset ℕ)
    (hs : ∀ m ∈ s, 1 ≤ m ∧ m + 2 ≤ N) (w : ℕ → ℝ) :
    linearCotDrive (fun k => ∑ m ∈ s, w m * harmonicWavelet m k) N =
      ∑ m ∈ s, w m * (deltaCot m - 2 * deltaCot (m + 1) + deltaCot (m + 2)) := by
  unfold linearCotDrive
  have hpt : ∀ k ∈ Finset.Icc 1 N,
      ((∑ m ∈ s, w m * harmonicWavelet m k) / (k : ℝ)) * deltaCot k =
        ∑ m ∈ s, w m * (harmonicWavelet m k * (deltaCot k / (k : ℝ))) := by
    intro k _
    rw [Finset.sum_div, Finset.sum_mul]
    exact Finset.sum_congr rfl fun m _ => by ring
  rw [Finset.sum_congr rfl hpt, Finset.sum_comm]
  refine Finset.sum_congr rfl fun m hm => ?_
  rw [← Finset.mul_sum,
    harmonicWavelet_div_sum_eq_second_diff deltaCot (hs m hm).1 (hs m hm).2]

/-- Subtracting `cBaseAnchor` maps every affine vector `c ∈ A_N` into the homogeneous tangent
subspace `A_N⁰ = {h | D1 h N = 0 ∧ D0 h N = 0}`. -/
theorem sub_cBaseAnchor_mem_tangent {N : ℕ} (hN : 2 ≤ N) (c : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) :
    D1 (fun k => c k - cBaseAnchor k) N = 0 ∧ D0 (fun k => c k - cBaseAnchor k) N = 0 := by
  have ha := cBaseAnchor_mem_A_N hN
  constructor
  · unfold D1 at hc1 ha ⊢
    have hpt : ∀ k ∈ Finset.Icc 1 N,
        (c k - cBaseAnchor k) / (k : ℝ) = c k / (k : ℝ) - cBaseAnchor k / (k : ℝ) :=
      fun _ _ => by ring
    rw [Finset.sum_congr rfl hpt, Finset.sum_sub_distrib, hc1, ha.1, sub_self]
  · unfold D0 at hc0 ha ⊢
    rw [Finset.sum_sub_distrib, hc0, ha.2, sub_self]

/-- Universal affine-to-Rayleigh upper bound: for every `N ≥ 2` and every `c ∈ A_N`,
`SCot vasyuninGCot c N ≤ tangentRayleighQuotient (c - cBaseAnchor) N`. -/
theorem SCot_le_tangentRayleighQuotient_sub_cBaseAnchor {N : ℕ} (hN : 2 ≤ N) (c : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) :
    SCot vasyuninGCot c N ≤ tangentRayleighQuotient (fun k => c k - cBaseAnchor k) N := by
  let h : ℕ → ℝ := fun k => c k - cBaseAnchor k
  have ht := sub_cBaseAnchor_mem_tangent hN c hc1 hc0
  have hQ_nn : 0 ≤ QCot vasyuninGCot h N := QCot_nonneg_of_mem_tangent h ht.1 ht.2
  by_cases hq : QCot vasyuninGCot h N = 0
  · have hsq_le : (Real.pi * linearCotDrive h N) ^ 2 ≤ 0 := by
      rw [← hq]
      exact sq_linearCotDrive_le_qcot hN h ht.1 ht.2
    have hsq_eq : (Real.pi * linearCotDrive h N) ^ 2 = 0 := le_antisymm hsq_le (sq_nonneg _)
    have hdrv : linearCotDrive h N = 0 := by
      rcases mul_eq_zero.mp (sq_eq_zero_iff.mp hsq_eq) with hpi | hlin
      · exact False.elim (Real.pi_ne_zero hpi)
      · exact hlin
    have hc_eq : c = fun k => cBaseAnchor k + h k := funext fun k => by dsimp [h]; ring
    have hcot_add := SCot_cBaseAnchor_add_eq hN h
    have hsum_eq :
        (∑ k ∈ Finset.Icc 1 N, (h k / (k : ℝ)) * (vasyuninCotSum k 2 - vasyuninCotSum k 1)) =
          linearCotDrive h N := by
      unfold linearCotDrive deltaCot
      rfl
    have hSh : SCot vasyuninGCot h N = 0 := by simp [SCot, hq]
    have hSc : SCot vasyuninGCot c N = 0 := by
      rw [hc_eq, hcot_add, hsum_eq, hSh, hdrv, mul_zero, add_zero]
    have hR : tangentRayleighQuotient h N = 0 := by
      dsimp [tangentRayleighQuotient]
      rw [hq, div_zero]
    rw [hSc, hR]
  · have hc_eq : c = fun k => cBaseAnchor k + 1 * h k := funext fun k => by dsimp [h]; ring
    conv_lhs => rw [hc_eq]
    rw [SCot_cBaseAnchor_add_smul_eq_rayleigh_sub_sq hN h hq 1]
    have hsub_nn : 0 ≤ QCot vasyuninGCot h N * (1 - optTangentStep h N) ^ 2 :=
      mul_nonneg hQ_nn (sq_nonneg _)
    linarith

/-- Universal affine-to-Rayleigh `L²(0, 1)` lower bound over all `c ∈ A_N` for `N ≥ 2`. -/
theorem one_sub_tangentRayleighQuotient_le_l2_dist {N : ℕ} (hN : 2 ≤ N) (c : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) :
    1 - tangentRayleighQuotient (fun k => c k - cBaseAnchor k) N ≤
      ∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2 := by
  rw [affine_l2_dist_eq_one_sub_scot c hc1 hc0]
  exact sub_le_sub_left (SCot_le_tangentRayleighQuotient_sub_cBaseAnchor hN c hc1 hc0) 1

/-- Unconditional homogeneous tangent Rayleigh criterion for the Riemann Hypothesis: if tangent
vectors `h ∈ A_N⁰` make `tangentRayleighQuotient h N` arbitrarily close to `1`, then
`RiemannHypothesis` holds. -/
theorem riemannHypothesis_of_tangentRayleighQuotient_limit
    (h_rayleigh : ∀ ε : ℝ, 0 < ε → ∃ N : ℕ, 2 ≤ N ∧ ∃ h : ℕ → ℝ,
      D1 h N = 0 ∧ D0 h N = 0 ∧ 1 - ε < tangentRayleighQuotient h N) :
    RiemannHypothesis := by
  apply riemannHypothesis_of_cotangent_limit
  intro ε hε
  have hε' : 0 < min ε (1 / 2) := lt_min hε (by norm_num : (0 : ℝ) < 1 / 2)
  rcases h_rayleigh (min ε (1 / 2)) hε' with ⟨N, hN, h, hh1, hh0, hgt⟩
  have hR_pos : 0 < tangentRayleighQuotient h N := by
    have : min ε (1 / 2) ≤ 1 / 2 := min_le_right ε (1 / 2)
    linarith
  have hQ_ne : QCot vasyuninGCot h N ≠ 0 := by
    intro hQ0
    simp [tangentRayleighQuotient, hQ0] at hR_pos
  have hc := cBaseAnchor_add_tangent_mem_A_N hN hh1 hh0 (optTangentStep h N)
  have hscot : 1 - ε < SCot vasyuninGCot (fun k => cBaseAnchor k + optTangentStep h N * h k) N := by
    rw [SCot_cBaseAnchor_add_optTangentStep_eq hN h hQ_ne]
    have : min ε (1 / 2) ≤ ε := min_le_left ε (1 / 2)
    linarith
  exact ⟨N, fun k => cBaseAnchor k + optTangentStep h N * h k, hc.1, hc.2, hscot⟩

/-- Cumulative sum of the first `m` harmonic wavelets on `A_N⁰`. -/
def cumulativeDipole (m k : ℕ) : ℝ :=
  ∑ r ∈ Finset.Icc 1 m, harmonicWavelet r k

private lemma cumulativeDipole_eq_sum_one_mul (m : ℕ) :
    cumulativeDipole m = fun k => ∑ r ∈ Finset.Icc 1 m, (1 : ℝ) * harmonicWavelet r k :=
  funext fun k => by simp [cumulativeDipole]

/-- Every cumulative dipole `cumulativeDipole m` lies unconditionally in `A_N⁰` for
`1 ≤ m` and `m + 2 ≤ N`. -/
theorem cumulativeDipole_mem_tangent {m N : ℕ} (hm : 1 ≤ m) (hN : m + 2 ≤ N) :
    D1 (cumulativeDipole m) N = 0 ∧ D0 (cumulativeDipole m) N = 0 := by
  let _ := hm
  have hs : ∀ r ∈ Finset.Icc 1 m, 1 ≤ r ∧ r + 2 ≤ N := fun r hr =>
    ⟨(Finset.mem_Icc.mp hr).1, by have := (Finset.mem_Icc.mp hr).2; omega⟩
  rw [cumulativeDipole_eq_sum_one_mul]
  exact sum_smul_harmonicWavelet_mem_tangent (Finset.Icc 1 m) hs (fun _ => 1)

private lemma cot_pi_div_three_dip : Real.cos (Real.pi / 3) / Real.sin (Real.pi / 3) = 1 / √3 := by
  rw [Real.cos_pi_div_three, Real.sin_pi_div_three]
  field_simp [(Real.sqrt_pos.mpr (by norm_num : (0 : ℝ) < 3)).ne']
private lemma cot_two_pi_div_three_dip :
    Real.cos (2 * Real.pi / 3) / Real.sin (2 * Real.pi / 3) = -(1 / √3) := by
  rw [show 2 * Real.pi / 3 = Real.pi - Real.pi / 3 by ring, Real.cos_pi_sub, Real.sin_pi_sub,
    neg_div, cot_pi_div_three_dip]
private lemma cot_pi_div_four_dip : Real.cos (Real.pi / 4) / Real.sin (Real.pi / 4) = 1 := by
  rw [Real.cos_pi_div_four, Real.sin_pi_div_four]
  field_simp [(Real.sqrt_pos.mpr (by norm_num : (0 : ℝ) < 2)).ne']
private lemma vasyuninCotSum_two_dip (b : ℕ) : vasyuninCotSum 2 b = 0 := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 2 = ({1} : Finset ℕ) by ext x; simp, Finset.sum_singleton,
    show Real.pi * ((1 : ℕ) : ℝ) / ((2 : ℕ) : ℝ) = Real.pi / 2 by push_cast; ring,
    Real.cos_pi_div_two, zero_div, mul_zero]
private lemma vasyuninCotSum_three_dip (b : ℕ) :
    vasyuninCotSum 3 b =
      (Int.fract ((b : ℝ) / 3) - Int.fract (2 * (b : ℝ) / 3)) * (1 / √3) := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 3 = ({1, 2} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide), Finset.sum_singleton]
  push_cast
  rw [show (1 : ℝ) * b / 3 = b / 3 by ring, show Real.pi * 1 / 3 = Real.pi / 3 by ring,
    show Real.pi * 2 / 3 = 2 * Real.pi / 3 by ring, cot_pi_div_three_dip, cot_two_pi_div_three_dip]
  ring
private lemma vasyuninCotSum_four_dip (b : ℕ) :
    vasyuninCotSum 4 b = Int.fract ((b : ℝ) / 4) - Int.fract (3 * (b : ℝ) / 4) := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 4 = ({1, 2, 3} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton]
  push_cast
  rw [show (1 : ℝ) * b / 4 = b / 4 by ring, show Real.pi * 1 / 4 = Real.pi / 4 by ring,
    show Real.pi * 2 / 4 = Real.pi / 2 by ring, Real.cos_pi_div_two, zero_div, mul_zero,
    show Real.pi * 3 / 4 = 3 * Real.pi / 4 by ring, cot_pi_div_four_dip,
    show Real.cos (3 * Real.pi / 4) / Real.sin (3 * Real.pi / 4) = -1 by
      rw [show 3 * Real.pi / 4 = Real.pi - Real.pi / 4 by ring, Real.cos_pi_sub, Real.sin_pi_sub,
        neg_div, cot_pi_div_four_dip]]
  ring

/-- Universal telescoping first-difference law for `linearCotDrive` on cumulative dipoles:
summing the second-difference stencils over `1..m` yields `deltaCot (m + 2) - deltaCot (m + 1)`
for all `1 ≤ m` and `m + 2 ≤ N`. -/
theorem linearCotDrive_cumulativeDipole_eq {m N : ℕ} (hm : 1 ≤ m) (hN : m + 2 ≤ N) :
    linearCotDrive (cumulativeDipole m) N = deltaCot (m + 2) - deltaCot (m + 1) := by
  have hs : ∀ r ∈ Finset.Icc 1 m, 1 ≤ r ∧ r + 2 ≤ N := fun r hr =>
    ⟨(Finset.mem_Icc.mp hr).1, by have := (Finset.mem_Icc.mp hr).2; omega⟩
  rw [cumulativeDipole_eq_sum_one_mul,
    linearCotDrive_sum_harmonicWavelet_eq (Finset.Icc 1 m) hs (fun _ => 1)]
  simp_rw [one_mul]
  clear hs hN
  induction m, hm using Nat.le_induction with
  | base =>
    have hd1 : deltaCot 1 = 0 := by simp [deltaCot, vasyuninCotSum]
    have hd2 : deltaCot 2 = 0 := by
      dsimp [deltaCot]; rw [vasyuninCotSum_two_dip, vasyuninCotSum_two_dip, sub_self]
    simp [hd1, hd2]
  | succ k hk ih =>
    rw [Finset.sum_Icc_succ_top (by omega : 1 ≤ k + 1), ih]
    ring

private lemma vasyuninGCot_one_two_dip : vasyuninGCot 1 2 = 0 := by
  have hV1 : vasyuninCotSum 1 2 = 0 := by simp [vasyuninCotSum]
  unfold vasyuninGCot; rw [hV1, vasyuninCotSum_two_dip]; ring
private lemma vasyuninGCot_one_three_dip : vasyuninGCot 1 3 = Real.pi / (18 * √3) := by
  have hV1 : vasyuninCotSum 1 3 = 0 := by simp [vasyuninCotSum]
  unfold vasyuninGCot; rw [hV1, vasyuninCotSum_three_dip]; norm_num; ring
private lemma vasyuninGCot_one_four_dip : vasyuninGCot 1 4 = Real.pi / 16 := by
  have hV1 : vasyuninCotSum 1 4 = 0 := by simp [vasyuninCotSum]
  unfold vasyuninGCot; rw [hV1, vasyuninCotSum_four_dip]; norm_num; ring
private lemma vasyuninGCot_two_three_dip : vasyuninGCot 2 3 = -(Real.pi / (36 * √3)) := by
  unfold vasyuninGCot; rw [vasyuninCotSum_two_dip, vasyuninCotSum_three_dip]; norm_num; ring
private lemma vasyuninGCot_two_four_dip : vasyuninGCot 2 4 = 0 := by
  unfold vasyuninGCot; rw [vasyuninCotSum_two_dip, vasyuninCotSum_four_dip]; norm_num
private lemma vasyuninGCot_three_four_dip :
    vasyuninGCot 3 4 = Real.pi / (72 * √3) - Real.pi / 48 := by
  unfold vasyuninGCot; rw [vasyuninCotSum_three_dip, vasyuninCotSum_four_dip]; norm_num; ring

private lemma sum_Icc_one_four_dip (f : ℕ → ℝ) :
    ∑ k ∈ Finset.Icc 1 4, f k = f 1 + f 2 + f 3 + f 4 := by
  rw [show Finset.Icc 1 4 = ({1, 2, 3, 4} : Finset ℕ) by
    ext x; simp only [Finset.mem_Icc, Finset.mem_insert, Finset.mem_singleton]; omega]
  norm_num [Finset.sum_insert, add_assoc]

private lemma sum_Icc_one_five_dip (f : ℕ → ℝ) :
    ∑ k ∈ Finset.Icc 1 5, f k = f 1 + f 2 + f 3 + f 4 + f 5 := by
  rw [show Finset.Icc 1 5 = ({1, 2, 3, 4, 5} : Finset ℕ) by
    ext x; simp only [Finset.mem_Icc, Finset.mem_insert, Finset.mem_singleton]; omega]
  norm_num [Finset.sum_insert, add_assoc]

private lemma cumulativeDipole_two_eq (k : ℕ) :
    cumulativeDipole 2 k = harmonicWavelet 1 k + harmonicWavelet 2 k := by
  unfold cumulativeDipole
  rw [show Finset.Icc 1 2 = ({1, 2} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide), Finset.sum_singleton]

private lemma cumulativeDipole_three_eq (k : ℕ) :
    cumulativeDipole 3 k = harmonicWavelet 1 k + harmonicWavelet 2 k + harmonicWavelet 3 k := by
  unfold cumulativeDipole
  rw [show Finset.Icc 1 3 = ({1, 2, 3} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton, add_assoc]

/-- Exact cotangent energy of the second cumulative dipole `cumulativeDipole 2` at `N = 4`:
`(1 - 1 / √3) * π`. -/
theorem QCot_cumulativeDipole_two_eq :
    QCot vasyuninGCot (cumulativeDipole 2) 4 = (1 - 1 / Real.sqrt 3) * Real.pi := by
  unfold QCot
  simp_rw [sum_Icc_one_four_dip, cumulativeDipole_two_eq]
  rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3, vasyuninGCot_diag 4,
    vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 4 1,
    vasyuninGCot_comm 3 2, vasyuninGCot_comm 4 2, vasyuninGCot_comm 4 3,
    vasyuninGCot_one_two_dip, vasyuninGCot_one_three_dip, vasyuninGCot_one_four_dip,
    vasyuninGCot_two_three_dip, vasyuninGCot_two_four_dip, vasyuninGCot_three_four_dip]
  simp [harmonicWavelet]
  ring

/-- Exact `N = 4` `vasyuninGCot`-orthogonality of `cumulativeDipole 1` and `cumulativeDipole 2`. -/
theorem sum_cumulativeDipole_one_two_vasyuninGCot_eq_zero :
    ∑ j ∈ Finset.Icc 1 4, ∑ k ∈ Finset.Icc 1 4,
      cumulativeDipole 1 j * cumulativeDipole 2 k * vasyuninGCot j k = 0 := by
  have h1 : ∀ k, cumulativeDipole 1 k = harmonicWavelet 1 k := fun _ => by simp [cumulativeDipole]
  simp_rw [sum_Icc_one_four_dip, h1, cumulativeDipole_two_eq]
  rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3, vasyuninGCot_diag 4,
    vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 4 1,
    vasyuninGCot_comm 3 2, vasyuninGCot_comm 4 2, vasyuninGCot_comm 4 3,
    vasyuninGCot_one_two_dip, vasyuninGCot_one_three_dip, vasyuninGCot_one_four_dip,
    vasyuninGCot_two_three_dip, vasyuninGCot_two_four_dip, vasyuninGCot_three_four_dip]
  simp [harmonicWavelet]
  ring

private lemma vasyuninCotSum_five_add_eq_zero (b₁ b₂ : ℕ)
    (hb : ∀ m ∈ Finset.Ico (1 : ℕ) 5,
      Int.fract ((m : ℝ) * (b₁ : ℝ) / 5) + Int.fract ((m : ℝ) * (b₂ : ℝ) / 5) = 1) :
    vasyuninCotSum 5 b₁ + vasyuninCotSum 5 b₂ = 0 := by
  unfold vasyuninCotSum
  push_cast
  rw [← Finset.sum_add_distrib]
  have hrew :
      (∑ m ∈ Finset.Ico (1 : ℕ) 5,
        (Int.fract ((m : ℝ) * (b₁ : ℝ) / 5) *
            (Real.cos (Real.pi * (m : ℝ) / 5) / Real.sin (Real.pi * (m : ℝ) / 5)) +
          Int.fract ((m : ℝ) * (b₂ : ℝ) / 5) *
            (Real.cos (Real.pi * (m : ℝ) / 5) / Real.sin (Real.pi * (m : ℝ) / 5)))) =
        ∑ m ∈ Finset.Ico (1 : ℕ) 5,
          Real.cos (Real.pi * (m : ℝ) / 5) / Real.sin (Real.pi * (m : ℝ) / 5) :=
    Finset.sum_congr rfl fun m hm => by rw [← add_mul, hb m hm, one_mul]
  rw [hrew, show Finset.Ico 1 5 = ({1, 2, 3, 4} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide : (1 : ℕ) ∉ ({2, 3, 4} : Finset ℕ)),
    Finset.sum_insert (by decide : (2 : ℕ) ∉ ({3, 4} : Finset ℕ)),
    Finset.sum_insert (by decide : (3 : ℕ) ∉ ({4} : Finset ℕ)), Finset.sum_singleton]
  push_cast
  have h3 : Real.cos (Real.pi * 3 / 5) / Real.sin (Real.pi * 3 / 5) =
      -(Real.cos (Real.pi * 2 / 5) / Real.sin (Real.pi * 2 / 5)) := by
    rw [show Real.pi * 3 / 5 = Real.pi - Real.pi * 2 / 5 by ring,
      Real.cos_pi_sub, Real.sin_pi_sub, neg_div]
  have h4 : Real.cos (Real.pi * 4 / 5) / Real.sin (Real.pi * 4 / 5) =
      -(Real.cos (Real.pi * 1 / 5) / Real.sin (Real.pi * 1 / 5)) := by
    rw [show Real.pi * 4 / 5 = Real.pi - Real.pi * 1 / 5 by ring,
      Real.cos_pi_sub, Real.sin_pi_sub, neg_div]
  rw [h3, h4]
  ring

/-- Reciprocity cancellation on `(ℤ/5ℤ)×`: `vasyuninCotSum 5 1 + vasyuninCotSum 5 4 = 0`. -/
theorem vasyuninCotSum_five_one_add_four : vasyuninCotSum 5 1 + vasyuninCotSum 5 4 = 0 := by
  refine vasyuninCotSum_five_add_eq_zero 1 4 fun m hm => ?_
  rcases Finset.mem_Ico.mp hm with ⟨hm1, hm5⟩; interval_cases m <;> norm_num

/-- Reciprocity cancellation on `(ℤ/5ℤ)×`: `vasyuninCotSum 5 2 + vasyuninCotSum 5 3 = 0`. -/
theorem vasyuninCotSum_five_two_add_three : vasyuninCotSum 5 2 + vasyuninCotSum 5 3 = 0 := by
  refine vasyuninCotSum_five_add_eq_zero 2 3 fun m hm => ?_
  rcases Finset.mem_Ico.mp hm with ⟨hm1, hm5⟩; interval_cases m <;> norm_num

/-- Exact `N = 5` `vasyuninGCot`-orthogonality of `cumulativeDipole 2` and `cumulativeDipole 3`,
proved algebraically via reciprocity without evaluating `cot (π / 5)`. -/
theorem sum_cumulativeDipole_two_three_vasyuninGCot_five_eq_zero :
    ∑ j ∈ Finset.Icc 1 5, ∑ k ∈ Finset.Icc 1 5,
      cumulativeDipole 2 j * cumulativeDipole 3 k * vasyuninGCot j k = 0 := by
  have h15 : vasyuninGCot 1 5 = -(Real.pi / 10) * vasyuninCotSum 5 1 := by
    have hV1 : vasyuninCotSum 1 5 = 0 := by simp [vasyuninCotSum]
    unfold vasyuninGCot; rw [hV1]; norm_num
  have h25 : vasyuninGCot 2 5 = -(Real.pi / 20) * vasyuninCotSum 5 2 := by
    unfold vasyuninGCot; rw [vasyuninCotSum_two_dip]; norm_num
  have h35 :
      vasyuninGCot 3 5 = -(Real.pi / (90 * √3)) - (Real.pi / 30) * vasyuninCotSum 5 3 := by
    unfold vasyuninGCot; rw [vasyuninCotSum_three_dip]; norm_num; ring
  have h45 : vasyuninGCot 4 5 = Real.pi / 80 - (Real.pi / 40) * vasyuninCotSum 5 4 := by
    unfold vasyuninGCot; rw [vasyuninCotSum_four_dip]; norm_num; ring
  have h54 : vasyuninCotSum 5 4 = -vasyuninCotSum 5 1 := by
    linarith [vasyuninCotSum_five_one_add_four]
  have h53 : vasyuninCotSum 5 3 = -vasyuninCotSum 5 2 := by
    linarith [vasyuninCotSum_five_two_add_three]
  simp_rw [sum_Icc_one_five_dip, cumulativeDipole_two_eq, cumulativeDipole_three_eq]
  rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3, vasyuninGCot_diag 4,
    vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 4 1,
    vasyuninGCot_comm 3 2, vasyuninGCot_comm 4 2, vasyuninGCot_comm 4 3,
    vasyuninGCot_comm 5 1, vasyuninGCot_comm 5 2, vasyuninGCot_comm 5 3, vasyuninGCot_comm 5 4,
    vasyuninGCot_one_two_dip, vasyuninGCot_one_three_dip, vasyuninGCot_one_four_dip,
    vasyuninGCot_two_three_dip, vasyuninGCot_two_four_dip, vasyuninGCot_three_four_dip,
    h15, h25, h35, h45, h54, h53]
  simp [harmonicWavelet]
  ring

/-- Exact 4-point telescoping support of `cumulativeDipole`: integrating any sequence `F k / k`
against `cumulativeDipole m k` over `1..N` collapses to `F 1 - F 2 - F (m + 1) + F (m + 2)`. -/
theorem cumulativeDipole_div_sum_eq_four_point (F : ℕ → ℝ) {m N : ℕ}
    (hm : 1 ≤ m) (hN : m + 2 ≤ N) :
    ∑ k ∈ Finset.Icc 1 N, cumulativeDipole m k * (F k / (k : ℝ)) =
      F 1 - F 2 - F (m + 1) + F (m + 2) := by
  have hterm : ∀ k ∈ Finset.Icc 1 N,
      cumulativeDipole m k * (F k / (k : ℝ)) =
        ∑ r ∈ Finset.Icc 1 m, harmonicWavelet r k * (F k / (k : ℝ)) := by
    intro k _
    unfold cumulativeDipole
    rw [Finset.sum_mul]
  rw [Finset.sum_congr rfl hterm, Finset.sum_comm]
  have hinner :
      (∑ r ∈ Finset.Icc 1 m, ∑ k ∈ Finset.Icc 1 N, harmonicWavelet r k * (F k / (k : ℝ))) =
        ∑ r ∈ Finset.Icc 1 m, (F r - 2 * F (r + 1) + F (r + 2)) := by
    refine Finset.sum_congr rfl fun r hr => ?_
    have hr1 : 1 ≤ r := (Finset.mem_Icc.mp hr).1
    have hr2 : r + 2 ≤ N := by have := (Finset.mem_Icc.mp hr).2; omega
    exact harmonicWavelet_div_sum_eq_second_diff F hr1 hr2
  rw [hinner]
  clear hterm hinner hN
  induction m, hm using Nat.le_induction with
  | base =>
    simp only [Finset.Icc_self, Finset.sum_singleton]
    ring
  | succ k hk ih =>
    rw [Finset.sum_Icc_succ_top (by omega : 1 ≤ k + 1), ih]
    ring

/-- Unweighted symmetric cotangent kernel `K(j, k) = j * k * vasyuninGCot j k`. -/
noncomputable def unweightedKCot (j k : ℕ) : ℝ :=
  (j : ℝ) * (k : ℝ) * vasyuninGCot j k

/-- Symmetry of `unweightedKCot`: `unweightedKCot j k = unweightedKCot k j`. -/
theorem unweightedKCot_comm (j k : ℕ) : unweightedKCot j k = unweightedKCot k j := by
  unfold unweightedKCot
  rw [vasyuninGCot_comm j k]
  ring

/-- Vanishing of `unweightedKCot` on the diagonal: `unweightedKCot k k = 0`. -/
theorem unweightedKCot_diag (k : ℕ) : unweightedKCot k k = 0 := by
  unfold unweightedKCot
  rw [vasyuninGCot_diag k, mul_zero]

private lemma vasyuninCotSum_two_fp (b : ℕ) : vasyuninCotSum 2 b = 0 := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 2 = ({1} : Finset ℕ) by ext x; simp, Finset.sum_singleton,
    show Real.pi * ((1 : ℕ) : ℝ) / ((2 : ℕ) : ℝ) = Real.pi / 2 by push_cast; ring,
    Real.cos_pi_div_two, zero_div, mul_zero]

/-- Exact boundary contrast of `unweightedKCot`: for every `1 ≤ k`,
`unweightedKCot 1 k - unweightedKCot 2 k = (π / 2) * deltaCot k`. -/
theorem unweightedKCot_one_sub_two {k : ℕ} (hk : 1 ≤ k) :
    unweightedKCot 1 k - unweightedKCot 2 k = (Real.pi / 2) * deltaCot k := by
  have hk_ne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hV1 : vasyuninCotSum 1 k = 0 := by simp [vasyuninCotSum]
  unfold unweightedKCot vasyuninGCot deltaCot
  rw [hV1, vasyuninCotSum_two_fp]
  simp only [Nat.cast_one, Nat.cast_ofNat, zero_add]
  field_simp [hk_ne]
  ring

/-- Exact `N`-independent 4-point closed form for the cumulative dipole Gram matrix for all
`1 ≤ a`, `1 ≤ b`, `a + 2 ≤ N`, and `b + 2 ≤ N`. -/
theorem sum_cumulativeDipole_vasyuninGCot_eq_four_point {a b N : ℕ}
    (ha : 1 ≤ a) (hb : 1 ≤ b) (haN : a + 2 ≤ N) (hbN : b + 2 ≤ N) :
    ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
      cumulativeDipole a j * cumulativeDipole b k * vasyuninGCot j k =
        (Real.pi / 2) *
            (deltaCot (a + 2) - deltaCot (a + 1) + deltaCot (b + 2) - deltaCot (b + 1)) +
          (unweightedKCot (a + 1) (b + 1) - unweightedKCot (a + 1) (b + 2) -
            unweightedKCot (a + 2) (b + 1) + unweightedKCot (a + 2) (b + 2)) := by
  have hstep1 :
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
        cumulativeDipole a j * cumulativeDipole b k * vasyuninGCot j k) =
        ∑ k ∈ Finset.Icc 1 N,
          cumulativeDipole b k *
            ((∑ j ∈ Finset.Icc 1 N, cumulativeDipole a j * (unweightedKCot j k / (j : ℝ))) /
              (k : ℝ)) := by
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun k hk => ?_
    have hk_ne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by have := (Finset.mem_Icc.mp hk).1; omega)
    rw [Finset.sum_div, Finset.mul_sum]
    refine Finset.sum_congr rfl fun j hj => ?_
    have hj_ne : (j : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by have := (Finset.mem_Icc.mp hj).1; omega)
    unfold unweightedKCot
    field_simp [hj_ne, hk_ne]
  have hstep2 :
      (∑ k ∈ Finset.Icc 1 N,
        cumulativeDipole b k *
          ((∑ j ∈ Finset.Icc 1 N, cumulativeDipole a j * (unweightedKCot j k / (j : ℝ))) /
            (k : ℝ))) =
        ∑ k ∈ Finset.Icc 1 N,
          cumulativeDipole b k *
            (((Real.pi / 2) * deltaCot k - unweightedKCot (a + 1) k +
              unweightedKCot (a + 2) k) / (k : ℝ)) := by
    refine Finset.sum_congr rfl fun k hk => ?_
    have hk1 : 1 ≤ k := (Finset.mem_Icc.mp hk).1
    rw [cumulativeDipole_div_sum_eq_four_point (fun j => unweightedKCot j k) ha haN]
    have hdiff := unweightedKCot_one_sub_two hk1
    have hlin :
        unweightedKCot 1 k - unweightedKCot 2 k - unweightedKCot (a + 1) k +
            unweightedKCot (a + 2) k =
          (Real.pi / 2) * deltaCot k - unweightedKCot (a + 1) k + unweightedKCot (a + 2) k := by
      linarith
    rw [hlin]
  let F : ℕ → ℝ := fun k =>
    (Real.pi / 2) * deltaCot k - unweightedKCot (a + 1) k + unweightedKCot (a + 2) k
  have hstep3 :
      (∑ k ∈ Finset.Icc 1 N, cumulativeDipole b k * (F k / (k : ℝ))) =
        F 1 - F 2 - F (b + 1) + F (b + 2) :=
    cumulativeDipole_div_sum_eq_four_point F hb hbN
  rw [hstep1, hstep2]
  change (∑ k ∈ Finset.Icc 1 N, cumulativeDipole b k * (F k / (k : ℝ))) = _
  rw [hstep3]
  dsimp [F]
  have hd1 : deltaCot 1 = 0 := by simp [deltaCot, vasyuninCotSum]
  have hd2 : deltaCot 2 = 0 := by
    dsimp [deltaCot]; rw [vasyuninCotSum_two_fp, vasyuninCotSum_two_fp, sub_self]
  have ha1 := unweightedKCot_one_sub_two (by omega : 1 ≤ a + 1)
  have ha2 := unweightedKCot_one_sub_two (by omega : 1 ≤ a + 2)
  rw [unweightedKCot_comm (a + 1) 1, unweightedKCot_comm (a + 1) 2,
    unweightedKCot_comm (a + 2) 1, unweightedKCot_comm (a + 2) 2]
  rw [hd1, hd2]
  linear_combination ha2 - ha1

/-- Exact 4-term closed-form formula for `cumulativeDipole m k` (`1 ≤ m`). -/
theorem cumulativeDipole_eq_four_term {m : ℕ} (hm : 1 ≤ m) (k : ℕ) :
    cumulativeDipole m k =
      (if k = 1 then (1 : ℝ) else 0) + (if k = 2 then (-2 : ℝ) else 0) -
        (if k = m + 1 then ((m + 1 : ℕ) : ℝ) else 0) +
        (if k = m + 2 then ((m + 2 : ℕ) : ℝ) else 0) := by
  induction m, hm using Nat.le_induction with
  | base =>
    rcases k with _ | _ | _ | _ | k <;> simp [cumulativeDipole, harmonicWavelet] <;> ring
  | succ r hr ih =>
    unfold cumulativeDipole
    rw [Finset.sum_Icc_succ_top (by omega : 1 ≤ r + 1)]
    have hprev : (∑ j ∈ Finset.Icc 1 r, harmonicWavelet j k) = cumulativeDipole r k := rfl
    rw [hprev, ih]
    unfold harmonicWavelet
    split_ifs <;> try omega
    all_goals push_cast; ring

/-- Suffix harmonic coordinate map for the cumulative dipole basis `{cumulativeDipole m}`. -/
noncomputable def dipoleCoord (c : ℕ → ℝ) (N m : ℕ) : ℝ :=
  ∑ j ∈ Finset.Icc (m + 2) N, c j / (j : ℝ)

/-- Cumulative wavelet coordinate map for the 3-point harmonic wavelet basis
`{harmonicWavelet r}`. -/
noncomputable def waveletCoord (c : ℕ → ℝ) (N r : ℕ) : ℝ :=
  ∑ m ∈ Finset.Icc r (N - 2), dipoleCoord c N m

private lemma sum_Icc_one_split (f : ℕ → ℝ) {N : ℕ} (hN : 2 ≤ N) :
    ∑ j ∈ Finset.Icc 1 N, f j = f 1 + f 2 + ∑ j ∈ Finset.Icc 3 N, f j := by
  have hpart : Finset.Icc 1 N = insert 1 (insert 2 (Finset.Icc 3 N)) := by
    ext j; simp only [Finset.mem_Icc, Finset.mem_insert]; omega
  rw [hpart, Finset.sum_insert (by simp), Finset.sum_insert (by simp)]
  ring

private lemma sum_dipoleCoord_eq (h : ℕ → ℝ) {N : ℕ} (hN : 2 ≤ N)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    ∑ m ∈ Finset.Icc 1 (N - 2), dipoleCoord h N m = h 1 := by
  have hD1 : h 1 / (1 : ℝ) + h 2 / (2 : ℝ) + ∑ j ∈ Finset.Icc 3 N, h j / (j : ℝ) = 0 := by
    simpa [D1, sum_Icc_one_split (fun j => h j / (j : ℝ)) hN] using hh1
  have hD0 : h 1 + h 2 + ∑ j ∈ Finset.Icc 3 N, h j = 0 := by
    simpa [D0, sum_Icc_one_split h hN] using hh0
  have hswap :
      (∑ m ∈ Finset.Icc 1 (N - 2), dipoleCoord h N m) =
        ∑ j ∈ Finset.Icc 3 N, ∑ m ∈ Finset.Icc 1 (N - 2),
          if m + 2 ≤ j then h j / (j : ℝ) else 0 := by
    rw [← Finset.sum_comm]
    refine Finset.sum_congr rfl fun m hm => ?_
    have hm1 : 1 ≤ m := (Finset.mem_Icc.mp hm).1
    have hsplit : Finset.Icc (m + 2) N = (Finset.Icc 3 N).filter (fun j => m + 2 ≤ j) := by
      ext j; simp only [Finset.mem_Icc, Finset.mem_filter]; omega
    unfold dipoleCoord
    rw [hsplit, Finset.sum_filter]
  have hinner :
      (∑ j ∈ Finset.Icc 3 N, ∑ m ∈ Finset.Icc 1 (N - 2),
          if m + 2 ≤ j then h j / (j : ℝ) else 0) =
        ∑ j ∈ Finset.Icc 3 N, (h j - 2 * (h j / (j : ℝ))) := by
    refine Finset.sum_congr rfl fun j hj => ?_
    have hj3 : 3 ≤ j := (Finset.mem_Icc.mp hj).1
    have hjN : j ≤ N := (Finset.mem_Icc.mp hj).2
    have hj_ne : (j : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
    have hfilt : (Finset.Icc 1 (N - 2)).filter (fun m => m + 2 ≤ j) = Finset.Icc 1 (j - 2) := by
      ext m; simp only [Finset.mem_filter, Finset.mem_Icc]; omega
    rw [← Finset.sum_filter, hfilt, Finset.sum_const, Nat.card_Icc, nsmul_eq_mul,
      show ((j - 2 + 1 - 1 : ℕ) : ℝ) = (j : ℝ) - 2 by
        rw [show j - 2 + 1 - 1 = j - 2 by omega, Nat.cast_sub (by omega : 2 ≤ j)]; norm_num]
    field_simp [hj_ne]
  rw [hswap, hinner, Finset.sum_sub_distrib, ← Finset.mul_sum]
  norm_num at hD1
  linarith

private lemma sum_dipoleCoord_mul_ite_add (c : ℕ → ℝ) (N d k : ℕ) :
    (∑ m ∈ Finset.Icc 1 (N - 2),
        dipoleCoord c N m * (if k = m + d then ((m + d : ℕ) : ℝ) else 0)) =
      if 1 + d ≤ k ∧ k ≤ N - 2 + d then (k : ℝ) * dipoleCoord c N (k - d) else 0 := by
  split_ifs with hk
  · have hmem : k - d ∈ Finset.Icc 1 (N - 2) := Finset.mem_Icc.mpr ⟨by omega, by omega⟩
    rw [Finset.sum_eq_single (k - d)]
    · have hkd : k - d + d = k := by omega
      simp [hkd, mul_comm]
    · intro m _ hm_ne
      simp [show k ≠ m + d by omega]
    · intro habs; exact False.elim (habs hmem)
  · refine Finset.sum_eq_zero fun m hm => ?_
    have := Finset.mem_Icc.mp hm
    simp [show k ≠ m + d by omega]

/-- General-`N` completeness of the cumulative dipole basis on `A_N⁰`: for every `N ≥ 2`, every
tangent vector `h ∈ A_N⁰`, and every `k ∈ Icc 1 N`, `h k` is the exact linear combination of
`cumulativeDipole m k` with coefficients `dipoleCoord h N m`. -/
theorem eq_sum_cumulativeDipole_of_mem_tangent {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) {k : ℕ} (hk : k ∈ Finset.Icc 1 N) :
    h k = ∑ m ∈ Finset.Icc 1 (N - 2), dipoleCoord h N m * cumulativeDipole m k := by
  have hpt : ∀ m ∈ Finset.Icc 1 (N - 2),
      dipoleCoord h N m * cumulativeDipole m k =
        dipoleCoord h N m * (if k = 1 then (1 : ℝ) else 0) +
          dipoleCoord h N m * (if k = 2 then (-2 : ℝ) else 0) -
          dipoleCoord h N m * (if k = m + 1 then ((m + 1 : ℕ) : ℝ) else 0) +
          dipoleCoord h N m * (if k = m + 2 then ((m + 2 : ℕ) : ℝ) else 0) := by
    intro m hm; rw [cumulativeDipole_eq_four_term (Finset.mem_Icc.mp hm).1 k]; ring
  rw [Finset.sum_congr rfl hpt, Finset.sum_add_distrib, Finset.sum_sub_distrib,
    Finset.sum_add_distrib, ← Finset.sum_mul, ← Finset.sum_mul,
    sum_dipoleCoord_eq h hN hh1 hh0,
    sum_dipoleCoord_mul_ite_add h N 1 k,
    sum_dipoleCoord_mul_ite_add h N 2 k]
  rcases Finset.mem_Icc.mp hk with ⟨hk1, hkN⟩
  rcases eq_or_ne k 1 with rfl | hk_ne1
  · simp
  · rcases eq_or_ne k 2 with rfl | hk_ne2
    · by_cases hN3 : 3 ≤ N
      · have hD1 : h 1 / (1 : ℝ) + h 2 / (2 : ℝ) + ∑ j ∈ Finset.Icc 3 N, h j / (j : ℝ) = 0 := by
          simpa [D1, sum_Icc_one_split (fun j => h j / (j : ℝ)) hN] using hh1
        have hd1 : dipoleCoord h N 1 = ∑ j ∈ Finset.Icc 3 N, h j / (j : ℝ) := rfl
        split_ifs <;> try omega
        norm_num at hD1 hd1 ⊢; linarith
      · have hN2 : N = 2 := by omega
        subst hN2
        have hD1 : h 1 / (1 : ℝ) + h 2 / (2 : ℝ) = 0 := by
          simpa [D1, sum_Icc_one_split (fun j => h j / (j : ℝ)) le_rfl] using hh1
        have hD0 : h 1 + h 2 = 0 := by
          simpa [D0, sum_Icc_one_split h le_rfl] using hh0
        split_ifs <;> try omega
        norm_num at hD1 hD0 ⊢; linarith
    · have hk3 : 3 ≤ k := by omega
      have hk_ne : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
      have hc2 : dipoleCoord h N (k - 2) =
          h k / (k : ℝ) + ∑ j ∈ Finset.Icc (k + 1) N, h j / (j : ℝ) := by
        unfold dipoleCoord
        have hpart : Finset.Icc (k - 2 + 2) N = insert k (Finset.Icc (k + 1) N) := by
          ext j; simp only [Finset.mem_Icc, Finset.mem_insert]; omega
        rw [hpart, Finset.sum_insert (by simp)]
      have ht4 : (k : ℝ) * dipoleCoord h N (k - 2) =
          h k + (k : ℝ) * ∑ j ∈ Finset.Icc (k + 1) N, h j / (j : ℝ) := by
        rw [hc2, mul_add, mul_div_cancel₀ _ hk_ne]
      by_cases hlast : k = N
      · subst hlast
        split_ifs <;> try omega
        rw [ht4, Finset.Icc_eq_empty (by omega : ¬k + 1 ≤ k), Finset.sum_empty]
        ring
      · have hc1 : dipoleCoord h N (k - 1) = ∑ j ∈ Finset.Icc (k + 1) N, h j / (j : ℝ) := by
          unfold dipoleCoord; rw [show k - 1 + 2 = k + 1 by omega]
        split_ifs <;> try omega
        rw [ht4, hc1]
        ring

/-- General-`N` completeness of the 3-point harmonic wavelet basis on `A_N⁰`: for every `N ≥ 2`,
every `h ∈ A_N⁰`, and every `k ∈ Icc 1 N`, `h k` is the exact linear combination of
`harmonicWavelet r k` with coefficients `waveletCoord h N r`. -/
theorem eq_sum_harmonicWavelet_of_mem_tangent {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) {k : ℕ} (hk : k ∈ Finset.Icc 1 N) :
    h k = ∑ r ∈ Finset.Icc 1 (N - 2), waveletCoord h N r * harmonicWavelet r k := by
  rw [eq_sum_cumulativeDipole_of_mem_tangent hN h hh1 hh0 hk]
  have hexp :
      (∑ m ∈ Finset.Icc 1 (N - 2), dipoleCoord h N m * cumulativeDipole m k) =
        ∑ m ∈ Finset.Icc 1 (N - 2), ∑ r ∈ Finset.Icc 1 (N - 2),
          if r ≤ m then dipoleCoord h N m * harmonicWavelet r k else 0 := by
    refine Finset.sum_congr rfl fun m hm => ?_
    have hmN : m ≤ N - 2 := (Finset.mem_Icc.mp hm).2
    have hfilt : Finset.Icc 1 m = (Finset.Icc 1 (N - 2)).filter (fun r => r ≤ m) := by
      ext r; simp only [Finset.mem_Icc, Finset.mem_filter]; omega
    unfold cumulativeDipole
    rw [Finset.mul_sum, hfilt, Finset.sum_filter]
  rw [hexp, Finset.sum_comm]
  refine Finset.sum_congr rfl fun r hr => ?_
  have hr1 : 1 ≤ r := (Finset.mem_Icc.mp hr).1
  have hfilt : Finset.Icc r (N - 2) = (Finset.Icc 1 (N - 2)).filter (fun m => r ≤ m) := by
    ext m; simp only [Finset.mem_Icc, Finset.mem_filter]; omega
  unfold waveletCoord
  rw [Finset.sum_mul, hfilt, Finset.sum_filter]

private lemma dipoleCoord_sub_cBaseAnchor (c : ℕ → ℝ) {N m : ℕ} (hm : 1 ≤ m) :
    dipoleCoord (fun k => c k - cBaseAnchor k) N m = dipoleCoord c N m := by
  refine Finset.sum_congr rfl fun j hj => ?_
  have hj3 : 3 ≤ j := by have := (Finset.mem_Icc.mp hj).1; omega
  have hanch : cBaseAnchor j = 0 := by
    rcases j with _ | _ | _ | j <;> [omega; omega; omega; rfl]
  dsimp only; rw [hanch, sub_zero]

private lemma waveletCoord_sub_cBaseAnchor (c : ℕ → ℝ) {N r : ℕ} (hr : 1 ≤ r) :
    waveletCoord (fun k => c k - cBaseAnchor k) N r = waveletCoord c N r := by
  refine Finset.sum_congr rfl fun m hm => ?_
  exact dipoleCoord_sub_cBaseAnchor c (by have := (Finset.mem_Icc.mp hm).1; omega)

/-- General-`N` completeness of the cumulative dipole basis on `A_N`: for every `N ≥ 2`, every
`c ∈ A_N`, and every `k ∈ Icc 1 N`, `c k` equals `cBaseAnchor k` plus the cumulative dipole
expansion with coordinates `dipoleCoord c N m`. -/
theorem eq_cBaseAnchor_add_sum_cumulativeDipole_of_mem_A_N {N : ℕ} (hN : 2 ≤ N) (c : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) {k : ℕ} (hk : k ∈ Finset.Icc 1 N) :
    c k = cBaseAnchor k +
      ∑ m ∈ Finset.Icc 1 (N - 2), dipoleCoord c N m * cumulativeDipole m k := by
  have ht := sub_cBaseAnchor_mem_tangent hN c hc1 hc0
  have hrec := eq_sum_cumulativeDipole_of_mem_tangent hN (fun j => c j - cBaseAnchor j) ht.1 ht.2 hk
  have hsum :
      (∑ m ∈ Finset.Icc 1 (N - 2),
          dipoleCoord (fun j => c j - cBaseAnchor j) N m * cumulativeDipole m k) =
        ∑ m ∈ Finset.Icc 1 (N - 2), dipoleCoord c N m * cumulativeDipole m k := by
    refine Finset.sum_congr rfl fun m hm => ?_
    rw [dipoleCoord_sub_cBaseAnchor c (Finset.mem_Icc.mp hm).1]
  rw [hsum] at hrec; linarith

/-- General-`N` completeness of the 3-point harmonic wavelet basis on `A_N`: for every `N ≥ 2`,
every `c ∈ A_N`, and every `k ∈ Icc 1 N`, `c k` equals `cBaseAnchor k` plus the harmonic wavelet
expansion with coordinates `waveletCoord c N r`. -/
theorem eq_cBaseAnchor_add_sum_harmonicWavelet_of_mem_A_N {N : ℕ} (hN : 2 ≤ N) (c : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) {k : ℕ} (hk : k ∈ Finset.Icc 1 N) :
    c k = cBaseAnchor k +
      ∑ r ∈ Finset.Icc 1 (N - 2), waveletCoord c N r * harmonicWavelet r k := by
  have ht := sub_cBaseAnchor_mem_tangent hN c hc1 hc0
  have hrec := eq_sum_harmonicWavelet_of_mem_tangent hN (fun j => c j - cBaseAnchor j) ht.1 ht.2 hk
  have hsum :
      (∑ r ∈ Finset.Icc 1 (N - 2),
          waveletCoord (fun j => c j - cBaseAnchor j) N r * harmonicWavelet r k) =
        ∑ r ∈ Finset.Icc 1 (N - 2), waveletCoord c N r * harmonicWavelet r k := by
    refine Finset.sum_congr rfl fun r hr => ?_
    rw [waveletCoord_sub_cBaseAnchor c (Finset.mem_Icc.mp hr).1]
  rw [hsum] at hrec; linarith

/-- Wavelet formulation of the homogeneous tangent Rayleigh criterion for the Riemann Hypothesis:
if finite linear combinations of harmonic wavelets on `Icc 1 (N - 2)` achieve
`tangentRayleighQuotient` arbitrarily close to `1`, then `RiemannHypothesis` holds. -/
theorem riemannHypothesis_of_wavelet_rayleigh_limit
    (h_wavelet : ∀ ε : ℝ, 0 < ε → ∃ N : ℕ, 2 ≤ N ∧ ∃ w : ℕ → ℝ,
      1 - ε <
        tangentRayleighQuotient
          (fun k => ∑ r ∈ Finset.Icc 1 (N - 2), w r * harmonicWavelet r k) N) :
    RiemannHypothesis := by
  apply riemannHypothesis_of_tangentRayleighQuotient_limit
  intro ε hε
  rcases h_wavelet ε hε with ⟨N, hN, w, hlt⟩
  have hs : ∀ r ∈ Finset.Icc 1 (N - 2), 1 ≤ r ∧ r + 2 ≤ N := fun r hr =>
    ⟨(Finset.mem_Icc.mp hr).1, by have := (Finset.mem_Icc.mp hr).2; omega⟩
  have hmem := sum_smul_harmonicWavelet_mem_tangent (Finset.Icc 1 (N - 2)) hs w
  exact ⟨N, hN, fun k => ∑ r ∈ Finset.Icc 1 (N - 2), w r * harmonicWavelet r k,
    hmem.1, hmem.2, hlt⟩

/-- Suffix–prefix duality: on `D1 c N = 0`, the suffix coordinate `dipoleCoord c N m` equals
the negated prefix sum `-∑ j ∈ Icc 1 (m + 1), c j / j` for every `m + 1 ≤ N`. -/
theorem dipoleCoord_eq_neg_sum_Icc_of_D1_eq_zero (c : ℕ → ℝ) {N m : ℕ}
    (hc1 : D1 c N = 0) (hm : m + 1 ≤ N) :
    dipoleCoord c N m = -∑ j ∈ Finset.Icc 1 (m + 1), c j / (j : ℝ) := by
  have hunion : Finset.Icc 1 N = Finset.Icc 1 (m + 1) ∪ Finset.Icc (m + 2) N := by
    ext j; simp only [Finset.mem_Icc, Finset.mem_union]; omega
  have hdisj : Disjoint (Finset.Icc 1 (m + 1)) (Finset.Icc (m + 2) N) :=
    Finset.disjoint_left.mpr fun j h1 h2 => by simp only [Finset.mem_Icc] at h1 h2; omega
  unfold D1 at hc1
  rw [hunion, Finset.sum_union hdisj] at hc1
  unfold dipoleCoord
  linarith

/-- `N`-independent 4-point dipole Gram kernel entry `⟨dₐ, d_b⟩_G`. -/
noncomputable def dipoleGramEntry (a b : ℕ) : ℝ :=
  (Real.pi / 2) * (deltaCot (a + 2) - deltaCot (a + 1) + deltaCot (b + 2) - deltaCot (b + 1)) +
    (unweightedKCot (a + 1) (b + 1) - unweightedKCot (a + 1) (b + 2) -
      unweightedKCot (a + 2) (b + 1) + unweightedKCot (a + 2) (b + 2))

/-- Exact reduction of `linearCotDrive h N` into `dipoleCoord h N m` on `A_N⁰` for all `N ≥ 2`. -/
theorem linearCotDrive_eq_sum_dipoleCoord {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    linearCotDrive h N =
      ∑ m ∈ Finset.Icc 1 (N - 2), dipoleCoord h N m * (deltaCot (m + 2) - deltaCot (m + 1)) := by
  unfold linearCotDrive
  have hpt : ∀ k ∈ Finset.Icc 1 N,
      (h k / (k : ℝ)) * deltaCot k =
        ∑ m ∈ Finset.Icc 1 (N - 2),
          dipoleCoord h N m * ((cumulativeDipole m k / (k : ℝ)) * deltaCot k) := by
    intro k hk
    rw [eq_sum_cumulativeDipole_of_mem_tangent hN h hh1 hh0 hk, Finset.sum_div, Finset.sum_mul]
    refine Finset.sum_congr rfl fun m _ => by ring
  rw [Finset.sum_congr rfl hpt, Finset.sum_comm]
  refine Finset.sum_congr rfl fun m hm => ?_
  rw [← Finset.mul_sum]
  have hdrv := linearCotDrive_cumulativeDipole_eq (Finset.mem_Icc.mp hm).1
    (by have := (Finset.mem_Icc.mp hm).2; omega : m + 2 ≤ N)
  unfold linearCotDrive at hdrv
  rw [hdrv]

/-- Exact `N`-independent 4-point dipole Gram reduction of `QCot` on `A_N⁰` for all `N ≥ 2`. -/
theorem QCot_eq_sum_dipoleGramEntry {N : ℕ} (hN : 2 ≤ N) (h : ℕ → ℝ)
    (hh1 : D1 h N = 0) (hh0 : D0 h N = 0) :
    QCot vasyuninGCot h N =
      ∑ a ∈ Finset.Icc 1 (N - 2), ∑ b ∈ Finset.Icc 1 (N - 2),
        dipoleCoord h N a * dipoleCoord h N b * dipoleGramEntry a b := by
  unfold QCot
  have hpt : ∀ j ∈ Finset.Icc 1 N, ∀ k ∈ Finset.Icc 1 N,
      h j * h k * vasyuninGCot j k =
        ∑ a ∈ Finset.Icc 1 (N - 2), ∑ b ∈ Finset.Icc 1 (N - 2),
          dipoleCoord h N a * dipoleCoord h N b *
            (cumulativeDipole a j * cumulativeDipole b k * vasyuninGCot j k) := by
    intro j hj k hk
    rw [eq_sum_cumulativeDipole_of_mem_tangent hN h hh1 hh0 hj,
      eq_sum_cumulativeDipole_of_mem_tangent hN h hh1 hh0 hk, Finset.sum_mul, Finset.sum_mul]
    refine Finset.sum_congr rfl fun a _ => ?_
    rw [Finset.mul_sum, Finset.sum_mul]
    refine Finset.sum_congr rfl fun b _ => by ring
  have hswap1 :
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N, h j * h k * vasyuninGCot j k) =
        ∑ a ∈ Finset.Icc 1 (N - 2), ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          ∑ b ∈ Finset.Icc 1 (N - 2), dipoleCoord h N a * dipoleCoord h N b *
            (cumulativeDipole a j * cumulativeDipole b k * vasyuninGCot j k) := by
    rw [Finset.sum_congr rfl fun j hj => Finset.sum_congr rfl fun k hk => hpt j hj k hk]
    rw [Finset.sum_congr rfl fun j _ => Finset.sum_comm, Finset.sum_comm]
  have hswap2 :
      (∑ a ∈ Finset.Icc 1 (N - 2), ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
        ∑ b ∈ Finset.Icc 1 (N - 2), dipoleCoord h N a * dipoleCoord h N b *
          (cumulativeDipole a j * cumulativeDipole b k * vasyuninGCot j k)) =
        ∑ a ∈ Finset.Icc 1 (N - 2), ∑ b ∈ Finset.Icc 1 (N - 2), ∑ j ∈ Finset.Icc 1 N,
          ∑ k ∈ Finset.Icc 1 N, dipoleCoord h N a * dipoleCoord h N b *
            (cumulativeDipole a j * cumulativeDipole b k * vasyuninGCot j k) := by
    refine Finset.sum_congr rfl fun a _ => ?_
    rw [Finset.sum_congr rfl fun j _ => Finset.sum_comm, Finset.sum_comm]
  rw [hswap1, hswap2]
  refine Finset.sum_congr rfl fun a ha => Finset.sum_congr rfl fun b hb => ?_
  have hfact :
      (∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
        dipoleCoord h N a * dipoleCoord h N b *
          (cumulativeDipole a j * cumulativeDipole b k * vasyuninGCot j k)) =
        dipoleCoord h N a * dipoleCoord h N b *
          ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
            cumulativeDipole a j * cumulativeDipole b k * vasyuninGCot j k := by
    simp_rw [← Finset.mul_sum]
  rw [hfact, sum_cumulativeDipole_vasyuninGCot_eq_four_point (Finset.mem_Icc.mp ha).1
    (Finset.mem_Icc.mp hb).1 (by have := (Finset.mem_Icc.mp ha).2; omega)
    (by have := (Finset.mem_Icc.mp hb).2; omega)]
  rfl

private lemma dipoleCoord_sub_cBaseAnchor_red (c : ℕ → ℝ) {N m : ℕ} (hm : 1 ≤ m) :
    dipoleCoord (fun k => c k - cBaseAnchor k) N m = dipoleCoord c N m := by
  refine Finset.sum_congr rfl fun j hj => ?_
  have hj3 : 3 ≤ j := by have := (Finset.mem_Icc.mp hj).1; omega
  have hanch : cBaseAnchor j = 0 := by rcases j with _ | _ | _ | j <;> [omega; omega; omega; rfl]
  dsimp only; rw [hanch, sub_zero]

/-- Master `N`-independent dipole quadratic reduction of `SCot vasyuninGCot c N` on `A_N`
for every `N ≥ 2`. -/
theorem SCot_eq_dipoleCoord_quadratic_of_mem_A_N {N : ℕ} (hN : 2 ≤ N) (c : ℕ → ℝ)
    (hc1 : D1 c N = 0) (hc0 : D0 c N = 2) :
    SCot vasyuninGCot c N =
      2 * Real.pi *
          (∑ m ∈ Finset.Icc 1 (N - 2),
            dipoleCoord c N m * (deltaCot (m + 2) - deltaCot (m + 1))) -
        ∑ a ∈ Finset.Icc 1 (N - 2), ∑ b ∈ Finset.Icc 1 (N - 2),
          dipoleCoord c N a * dipoleCoord c N b * dipoleGramEntry a b := by
  let h : ℕ → ℝ := fun k => c k - cBaseAnchor k
  have ht := sub_cBaseAnchor_mem_tangent hN c hc1 hc0
  have hc_eq : c = fun k => cBaseAnchor k + h k := funext fun k => by dsimp [h]; ring
  have hcot_add := SCot_cBaseAnchor_add_eq hN h
  have hlin_eq :
      (∑ k ∈ Finset.Icc 1 N, (h k / (k : ℝ)) * (vasyuninCotSum k 2 - vasyuninCotSum k 1)) =
        linearCotDrive h N := rfl
  have hS : SCot vasyuninGCot c N = -QCot vasyuninGCot h N + 2 * Real.pi * linearCotDrive h N := by
    conv_lhs => rw [hc_eq]
    rw [hcot_add, hlin_eq]
    unfold SCot
    rfl
  rw [hS, linearCotDrive_eq_sum_dipoleCoord hN h ht.1 ht.2,
    QCot_eq_sum_dipoleGramEntry hN h ht.1 ht.2]
  have hL :
      (∑ m ∈ Finset.Icc 1 (N - 2),
          dipoleCoord h N m * (deltaCot (m + 2) - deltaCot (m + 1))) =
        ∑ m ∈ Finset.Icc 1 (N - 2),
          dipoleCoord c N m * (deltaCot (m + 2) - deltaCot (m + 1)) := by
    refine Finset.sum_congr rfl fun m hm => ?_
    rw [dipoleCoord_sub_cBaseAnchor_red c (Finset.mem_Icc.mp hm).1]
  have hQ :
      (∑ a ∈ Finset.Icc 1 (N - 2), ∑ b ∈ Finset.Icc 1 (N - 2),
          dipoleCoord h N a * dipoleCoord h N b * dipoleGramEntry a b) =
        ∑ a ∈ Finset.Icc 1 (N - 2), ∑ b ∈ Finset.Icc 1 (N - 2),
          dipoleCoord c N a * dipoleCoord c N b * dipoleGramEntry a b := by
    refine Finset.sum_congr rfl fun a ha => Finset.sum_congr rfl fun b hb => ?_
    rw [dipoleCoord_sub_cBaseAnchor_red c (Finset.mem_Icc.mp ha).1,
      dipoleCoord_sub_cBaseAnchor_red c (Finset.mem_Icc.mp hb).1]
  rw [hL, hQ]
  ring

/-- Exact `N = 4` dipole coordinates of the global KKT optimizer `cGlobalOptFour`. -/
theorem dipoleCoord_cGlobalOptFour_eval :
    dipoleCoord cGlobalOptFour 4 1 = 2 / 3 ∧
      dipoleCoord cGlobalOptFour 4 2 = (5 - Real.sqrt 3) / 12 := by
  have h34 : Finset.Icc 3 4 = ({3, 4} : Finset ℕ) := by decide
  unfold dipoleCoord
  rw [h34, Finset.sum_insert (by decide), Finset.sum_singleton, Finset.Icc_self,
    Finset.sum_singleton]
  norm_num [cGlobalOptFour, cBaseAnchor, harmonicWavelet]
  ring

/-- Exact `N = 4` dipole coordinates of `cCandidateMobius 4`. -/
theorem dipoleCoord_cCandidateMobius_four_eval :
    dipoleCoord (cCandidateMobius 4) 4 1 = 133 / 208 ∧
      dipoleCoord (cCandidateMobius 4) 4 2 = 7 / 24 := by
  rcases cCandidateMobius_four_eval with ⟨_, _, hc3, hc4⟩
  have h34 : Finset.Icc 3 4 = ({3, 4} : Finset ℕ) := by decide
  unfold dipoleCoord
  rw [h34, Finset.sum_insert (by decide), Finset.sum_singleton, Finset.Icc_self,
    Finset.sum_singleton, hc3, hc4]
  constructor <;> norm_num

/-- Strict square-index `k = 4` overshoot certificate: the 2nd dipole coordinate of
`cGlobalOptFour` is strictly smaller than that of `cCandidateMobius 4`. -/
theorem dipoleCoord_cGlobalOptFour_two_lt_cCandidateMobius_four :
    dipoleCoord cGlobalOptFour 4 2 < dipoleCoord (cCandidateMobius 4) 4 2 := by
  rw [dipoleCoord_cGlobalOptFour_eval.2, dipoleCoord_cCandidateMobius_four_eval.2]
  have hsqrt : (3 / 2 : ℝ) < Real.sqrt 3 := by
    nlinarith [Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 3), Real.sqrt_nonneg 3]
  linarith

/-- Symmetry of the 4-point dipole Gram kernel entry:
`dipoleGramEntry a b = dipoleGramEntry b a`. -/
theorem dipoleGramEntry_comm (a b : ℕ) : dipoleGramEntry a b = dipoleGramEntry b a := by
  unfold dipoleGramEntry
  rw [unweightedKCot_comm (a + 1) (b + 1), unweightedKCot_comm (a + 1) (b + 2),
    unweightedKCot_comm (a + 2) (b + 1), unweightedKCot_comm (a + 2) (b + 2)]
  ring

/-- Single-pair diagonal collapse of `dipoleGramEntry`: on the diagonal `a = b = m`, the
4-point plaque reduces to `π * (deltaCot (m + 2) - deltaCot (m + 1)) - 2 * K (m + 1) (m + 2)`. -/
theorem dipoleGramEntry_diag_eq (m : ℕ) :
    dipoleGramEntry m m =
      Real.pi * (deltaCot (m + 2) - deltaCot (m + 1)) - 2 * unweightedKCot (m + 1) (m + 2) := by
  unfold dipoleGramEntry
  rw [unweightedKCot_diag (m + 1), unweightedKCot_diag (m + 2),
    unweightedKCot_comm (m + 2) (m + 1)]
  ring

/-- Exact bridge equating the cotangent quadratic energy of `cumulativeDipole m` at any truncation
`N ≥ m + 2` to the `N`-independent diagonal entry `dipoleGramEntry m m`. -/
theorem QCot_cumulativeDipole_eq_dipoleGramEntry_diag {m N : ℕ} (hm : 1 ≤ m) (hN : m + 2 ≤ N) :
    QCot vasyuninGCot (cumulativeDipole m) N = dipoleGramEntry m m := by
  unfold QCot
  exact sum_cumulativeDipole_vasyuninGCot_eq_four_point hm hm hN hN

/-- Unconditional diagonal non-negativity of the dipole Gram kernel for every `1 ≤ m`, proved
by choosing `N = m + 2` and invoking `QCot_nonneg_of_mem_tangent`. -/
theorem dipoleGramEntry_diag_nonneg {m : ℕ} (hm : 1 ≤ m) : 0 ≤ dipoleGramEntry m m := by
  have ht := cumulativeDipole_mem_tangent hm (le_rfl : m + 2 ≤ m + 2)
  rw [← QCot_cumulativeDipole_eq_dipoleGramEntry_diag hm (le_rfl : m + 2 ≤ m + 2)]
  exact QCot_nonneg_of_mem_tangent (cumulativeDipole m) ht.1 ht.2

/-- Exact value of the first diagonal dipole Gram entry: `dipoleGramEntry 1 1 = π / √3`. -/
theorem dipoleGramEntry_one_one_eq : dipoleGramEntry 1 1 = Real.pi / Real.sqrt 3 := by
  have h1 : cumulativeDipole 1 = harmonicWavelet 1 := by
    funext k
    simp [cumulativeDipole]
  rw [← QCot_cumulativeDipole_eq_dipoleGramEntry_diag (by omega : 1 ≤ 1) (by omega : 1 + 2 ≤ 3),
    h1, QCot_harmonicWavelet_one_eq]

/-- Exact value of the second diagonal dipole Gram entry:
`dipoleGramEntry 2 2 = (1 - 1 / √3) * π`. -/
theorem dipoleGramEntry_two_two_eq :
    dipoleGramEntry 2 2 = (1 - 1 / Real.sqrt 3) * Real.pi := by
  rw [← QCot_cumulativeDipole_eq_dipoleGramEntry_diag (by omega : 1 ≤ 2) (by omega : 2 + 2 ≤ 4),
    QCot_cumulativeDipole_two_eq]

/-- Exact off-diagonal vanishing `dipoleGramEntry 1 2 = 0` reflecting `d₁ ⊥ d₂` under `G`. -/
theorem dipoleGramEntry_one_two_eq_zero : dipoleGramEntry 1 2 = 0 := by
  have h := sum_cumulativeDipole_vasyuninGCot_eq_four_point (by omega : 1 ≤ 1)
    (by omega : 1 ≤ 2) (by omega : 1 + 2 ≤ 4) (by omega : 2 + 2 ≤ 4)
  change _ = dipoleGramEntry 1 2 at h
  rw [← h, sum_cumulativeDipole_one_two_vasyuninGCot_eq_zero]

end MathlibPR.ForwardCandidate
