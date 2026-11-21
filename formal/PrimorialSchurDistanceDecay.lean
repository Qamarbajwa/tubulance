/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.Symmetric
import Mathlib.Tactic

/-!
# Primorial Schur Distance Decay & Block-Banachiewicz Identity

`NO_RH_PROOF = TRUE`:
The Clay Riemann Hypothesis remains strictly OPEN. This module proves the exact
finite-dimensional Block-Banachiewicz Schur distance split
`d_N^2 = d_{N,Prime}^2 - Δ_Schur(C | P)` and nonnegativity of `Δ_Schur(C | P)`
strictly within Lean's foundational axioms `[propext, Classical.choice, Quot.sound]`.
-/

namespace RiemannBlueprint.PrimorialSchurDistanceDecay

open Matrix

/-- **Block-Banachiewicz Right Inverse:**
For block matrix `Q = fromBlocks Q_PP Q_PC Q_CP Q_CC`, if `Q_PP_inv` is the inverse of `Q_PP`
and `Sigma_inv` is the inverse of the Schur complement `Sigma = Q_CC - Q_CP * Q_PP_inv * Q_PC`,
then the Banachiewicz block matrix is the exact right inverse of `Q`. -/
theorem block_banachiewicz_mul_eq_one {p c : ℕ}
    (Q_PP : Matrix (Fin p) (Fin p) ℝ)
    (Q_PC : Matrix (Fin p) (Fin c) ℝ)
    (Q_CP : Matrix (Fin c) (Fin p) ℝ)
    (Q_CC : Matrix (Fin c) (Fin c) ℝ)
    (Q_PP_inv : Matrix (Fin p) (Fin p) ℝ)
    (Sigma_inv : Matrix (Fin c) (Fin c) ℝ)
    (hPP_r : Q_PP * Q_PP_inv = 1)
    (hS_r : (Q_CC - Q_CP * Q_PP_inv * Q_PC) * Sigma_inv = 1) :
    let Q := fromBlocks Q_PP Q_PC Q_CP Q_CC
    let B11 := Q_PP_inv + Q_PP_inv * Q_PC * Sigma_inv * Q_CP * Q_PP_inv
    let B12 := -(Q_PP_inv * Q_PC * Sigma_inv)
    let B21 := -(Sigma_inv * Q_CP * Q_PP_inv)
    let B22 := Sigma_inv
    Q * fromBlocks B11 B12 B21 B22 = 1 := by
  intro Q B11 B12 B21 B22
  dsimp [Q, B11, B12, B21, B22]
  rw [fromBlocks_multiply, ← fromBlocks_one]
  congr 1
  · -- Top-left block:
    have h1 : Q_PP * (Q_PP_inv + Q_PP_inv * Q_PC * Sigma_inv * Q_CP * Q_PP_inv) +
        Q_PC * -(Sigma_inv * Q_CP * Q_PP_inv) = 1 := by
      rw [Matrix.mul_add, hPP_r, Matrix.mul_neg]
      have hassoc : Q_PP * (Q_PP_inv * Q_PC * Sigma_inv * Q_CP * Q_PP_inv) =
          (Q_PP * Q_PP_inv) * (Q_PC * Sigma_inv * Q_CP * Q_PP_inv) := by
        simp only [Matrix.mul_assoc]
      rw [hassoc, hPP_r, Matrix.one_mul]
      have hneg : Q_PC * (Sigma_inv * Q_CP * Q_PP_inv) =
          Q_PC * Sigma_inv * Q_CP * Q_PP_inv := by
        simp only [Matrix.mul_assoc]
      rw [hneg]
      abel
    exact h1
  · -- Top-right block:
    have h2 : Q_PP * -(Q_PP_inv * Q_PC * Sigma_inv) + Q_PC * Sigma_inv = 0 := by
      rw [Matrix.mul_neg]
      have hassoc : Q_PP * (Q_PP_inv * Q_PC * Sigma_inv) =
          (Q_PP * Q_PP_inv) * (Q_PC * Sigma_inv) := by
        simp only [Matrix.mul_assoc]
      rw [hassoc, hPP_r, Matrix.one_mul, neg_add_cancel]
    exact h2
  · -- Bottom-left block:
    have h3 : Q_CP * (Q_PP_inv + Q_PP_inv * Q_PC * Sigma_inv * Q_CP * Q_PP_inv) +
        Q_CC * -(Sigma_inv * Q_CP * Q_PP_inv) = 0 := by
      rw [Matrix.mul_add, Matrix.mul_neg]
      have hassoc1 : Q_CP * (Q_PP_inv * Q_PC * Sigma_inv * Q_CP * Q_PP_inv) =
          (Q_CP * Q_PP_inv * Q_PC) * Sigma_inv * (Q_CP * Q_PP_inv) := by
        simp only [Matrix.mul_assoc]
      have hassoc2 : Q_CC * (Sigma_inv * Q_CP * Q_PP_inv) =
          Q_CC * Sigma_inv * (Q_CP * Q_PP_inv) := by
        simp only [Matrix.mul_assoc]
      rw [hassoc1, hassoc2]
      calc
        Q_CP * Q_PP_inv + Q_CP * Q_PP_inv * Q_PC * Sigma_inv * (Q_CP * Q_PP_inv) +
            -(Q_CC * Sigma_inv * (Q_CP * Q_PP_inv))
            = Q_CP * Q_PP_inv -
                ((Q_CC - Q_CP * Q_PP_inv * Q_PC) * Sigma_inv) * (Q_CP * Q_PP_inv) := by
                rw [Matrix.sub_mul, Matrix.sub_mul]
                abel
        _ = Q_CP * Q_PP_inv - (1 : Matrix (Fin c) (Fin c) ℝ) * (Q_CP * Q_PP_inv) := by
                rw [hS_r]
        _ = 0 := by rw [Matrix.one_mul, sub_self]
    exact h3
  · -- Bottom-right block:
    have h4 : Q_CP * -(Q_PP_inv * Q_PC * Sigma_inv) + Q_CC * Sigma_inv = 1 := by
      rw [Matrix.mul_neg]
      have hassoc : Q_CP * (Q_PP_inv * Q_PC * Sigma_inv) =
          (Q_CP * Q_PP_inv * Q_PC) * Sigma_inv := by
        simp only [Matrix.mul_assoc]
      rw [hassoc, neg_add_eq_sub, ← Matrix.sub_mul, hS_r]
    exact h4

/-- **Block-Banachiewicz Schur Distance Identity (`d_N^2 = d_{N,Prime}^2 - Δ_Schur(C | P)`):**
For symmetric `Q_PP_inv`, `Q_PC = Q_CPᵀ`, and partitioned target vector `(ρ_P, ρ_C)`,
the quadratic form of the Banachiewicz inverse block matrix splits `1 - ρᵀ Q⁻¹ ρ` into
`(1 - ρ_Pᵀ Q_PP⁻¹ ρ_P) - (ρ_C - Q_CP Q_PP⁻¹ ρ_P)ᵀ Σ_N⁻¹ (ρ_C - Q_CP Q_PP⁻¹ ρ_P)`. -/
theorem block_banachiewicz_schur_distance_split {p c : ℕ}
    (Q_CP : Matrix (Fin c) (Fin p) ℝ)
    (Q_PP_inv : Matrix (Fin p) (Fin p) ℝ)
    (Sigma_inv : Matrix (Fin c) (Fin c) ℝ)
    (hPP_sym : Q_PP_invᵀ = Q_PP_inv)
    (ρ_P : Fin p → ℝ) (ρ_C : Fin c → ℝ) :
    let Q_PC := Q_CPᵀ
    let B11 := Q_PP_inv + Q_PP_inv * Q_PC * Sigma_inv * Q_CP * Q_PP_inv
    let B12 := -(Q_PP_inv * Q_PC * Sigma_inv)
    let B21 := -(Sigma_inv * Q_CP * Q_PP_inv)
    let B22 := Sigma_inv
    let Q_inv := fromBlocks B11 B12 B21 B22
    let ρ : Fin p ⊕ Fin c → ℝ := Sum.elim ρ_P ρ_C
    let δ : Fin c → ℝ := ρ_C - Q_CP.mulVec (Q_PP_inv.mulVec ρ_P)
    1 - dotProduct ρ (Q_inv.mulVec ρ) =
      (1 - dotProduct ρ_P (Q_PP_inv.mulVec ρ_P)) -
        dotProduct δ (Sigma_inv.mulVec δ) := by
  intro Q_PC B11 B12 B21 B22 Q_inv ρ δ
  have hQinv_mul : Q_inv.mulVec ρ =
      Sum.elim (B11.mulVec ρ_P + B12.mulVec ρ_C)
               (B21.mulVec ρ_P + B22.mulVec ρ_C) := by
    ext x
    rcases x with i | j <;>
      simp [Q_inv, ρ, Matrix.mulVec, dotProduct, Fintype.sum_sum_type]
  have hdot : dotProduct ρ (Q_inv.mulVec ρ) =
      dotProduct ρ_P (B11.mulVec ρ_P + B12.mulVec ρ_C) +
      dotProduct ρ_C (B21.mulVec ρ_P + B22.mulVec ρ_C) := by
    rw [hQinv_mul]
    dsimp [ρ]
    simp [dotProduct, Fintype.sum_sum_type]
  -- Let w = Q_CP *ᵥ (Q_PP_inv *ᵥ ρ_P) and u = Q_PP_inv *ᵥ ρ_P
  set u : Fin p → ℝ := Q_PP_inv.mulVec ρ_P
  set w : Fin c → ℝ := Q_CP.mulVec u
  have hu_dot : ∀ z : Fin c → ℝ,
      dotProduct ρ_P ((Q_PP_inv * Q_PC).mulVec z) = dotProduct w z := by
    intro z
    rw [← Matrix.mulVec_mulVec]
    have : dotProduct ρ_P (Q_PP_inv.mulVec (Q_PC.mulVec z)) =
        dotProduct (Q_PP_invᵀ.mulVec ρ_P) (Q_PC.mulVec z) := by
      rw [Matrix.dotProduct_mulVec, ← Matrix.mulVec_transpose]
    rw [this, hPP_sym]
    change dotProduct u (Q_CPᵀ.mulVec z) = dotProduct (Q_CP.mulVec u) z
    rw [Matrix.dotProduct_mulVec, ← Matrix.mulVec_transpose, Matrix.transpose_transpose,
      dotProduct_comm]
  -- Expand B11 *ᵥ ρ_P, B12 *ᵥ ρ_C, B21 *ᵥ ρ_P, B22 *ᵥ ρ_C
  have hB11 : B11.mulVec ρ_P =
      u + (Q_PP_inv * Q_PC).mulVec (Sigma_inv.mulVec w) := by
    dsimp [B11]
    rw [Matrix.add_mulVec]
    congr 1
    simp only [Matrix.mul_assoc, ← Matrix.mulVec_mulVec]
    rfl
  have hB12 : B12.mulVec ρ_C =
      -((Q_PP_inv * Q_PC).mulVec (Sigma_inv.mulVec ρ_C)) := by
    dsimp [B12]
    rw [Matrix.neg_mulVec, ← Matrix.mulVec_mulVec]
  have hB21 : B21.mulVec ρ_P = -(Sigma_inv.mulVec w) := by
    dsimp [B21]
    rw [Matrix.neg_mulVec, Matrix.mul_assoc, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec]
  rw [hdot, hB11, hB12, hB21]
  dsimp [B22]
  simp only [dotProduct_add, dotProduct_neg, add_assoc]
  rw [hu_dot (Sigma_inv.mulVec w), hu_dot (Sigma_inv.mulVec ρ_C)]
  have hδ : dotProduct δ (Sigma_inv.mulVec δ) =
      dotProduct ρ_C (Sigma_inv.mulVec ρ_C) - dotProduct ρ_C (Sigma_inv.mulVec w) -
      dotProduct w (Sigma_inv.mulVec ρ_C) + dotProduct w (Sigma_inv.mulVec w) := by
    dsimp [δ]
    change dotProduct (ρ_C - w) (Sigma_inv.mulVec (ρ_C - w)) = _
    rw [Matrix.mulVec_sub, dotProduct_sub, sub_dotProduct, sub_dotProduct]
    ring
  rw [hδ]
  ring

/-- **Nonnegativity of the Composite Schur Reduction (`Δ_Schur(C | P) >= 0`) & Prime Baseline Bound:**
Whenever `Σ_N⁻¹` is positive semidefinite, subtracting the Composite Schur reduction
never increases the squared approximation distance: `d_N^2 ≤ d_{N,Prime}^2`. -/
theorem schur_distance_le_prime_baseline {p c : ℕ}
    (Q_CP : Matrix (Fin c) (Fin p) ℝ)
    (Q_PP_inv : Matrix (Fin p) (Fin p) ℝ)
    (Sigma_inv : Matrix (Fin c) (Fin c) ℝ)
    (hPP_sym : Q_PP_invᵀ = Q_PP_inv)
    (hS_psd : ∀ x : Fin c → ℝ, 0 ≤ dotProduct x (Sigma_inv.mulVec x))
    (ρ_P : Fin p → ℝ) (ρ_C : Fin c → ℝ) :
    let Q_PC := Q_CPᵀ
    let B11 := Q_PP_inv + Q_PP_inv * Q_PC * Sigma_inv * Q_CP * Q_PP_inv
    let B12 := -(Q_PP_inv * Q_PC * Sigma_inv)
    let B21 := -(Sigma_inv * Q_CP * Q_PP_inv)
    let Q_inv := fromBlocks B11 B12 B21 Sigma_inv
    let ρ : Fin p ⊕ Fin c → ℝ := Sum.elim ρ_P ρ_C
    let δ : Fin c → ℝ := ρ_C - Q_CP.mulVec (Q_PP_inv.mulVec ρ_P)
    0 ≤ dotProduct δ (Sigma_inv.mulVec δ) ∧
    1 - dotProduct ρ (Q_inv.mulVec ρ) ≤ 1 - dotProduct ρ_P (Q_PP_inv.mulVec ρ_P) := by
  intro Q_PC B11 B12 B21 Q_inv ρ δ
  have hnonneg : 0 ≤ dotProduct δ (Sigma_inv.mulVec δ) := hS_psd δ
  have hsplit :=
    block_banachiewicz_schur_distance_split Q_CP Q_PP_inv Sigma_inv hPP_sym ρ_P ρ_C
  refine ⟨hnonneg, ?_⟩
  linarith

/-- **Schur-Complement Resolvent One-Step Growth:**
Bordering a symmetric matrix `M_N` (with inverse `M_inv`) by `(v, d)` with scalar Schur
complement `s > 0` increases `1ᵀ M⁻¹ 1` by the nonnegative Schur step `(1 - vᵀ M⁻¹ 1)^2 / s`. -/
theorem schur_resolvent_one_step_growth {n : ℕ}
    (M_inv : Matrix (Fin n) (Fin n) ℝ) (hM_sym : M_invᵀ = M_inv)
    (v : Fin n → ℝ) (s : ℝ) (hs : 0 < s) :
    let ones_n : Fin n → ℝ := fun _ => 1
    let ones_next : Fin n ⊕ Fin 1 → ℝ := Sum.elim ones_n (fun _ => 1)
    let v_col : Matrix (Fin n) (Fin 1) ℝ := Matrix.of (fun i _ => v i)
    let v_row : Matrix (Fin 1) (Fin n) ℝ := v_colᵀ
    let s_inv : Matrix (Fin 1) (Fin 1) ℝ := Matrix.of (fun _ _ => s⁻¹)
    let B11 := M_inv + M_inv * v_col * s_inv * v_row * M_inv
    let B12 := -(M_inv * v_col * s_inv)
    let B21 := -(s_inv * v_row * M_inv)
    let M_next_inv := fromBlocks B11 B12 B21 s_inv
    dotProduct ones_next (M_next_inv.mulVec ones_next) =
      dotProduct ones_n (M_inv.mulVec ones_n) +
        (1 - dotProduct v (M_inv.mulVec ones_n)) ^ 2 / s ∧
    dotProduct ones_n (M_inv.mulVec ones_n) ≤
      dotProduct ones_next (M_next_inv.mulVec ones_next) := by
  intro ones_n ones_next v_col v_row s_inv B11 B12 B21 M_next_inv
  have hsplit := block_banachiewicz_schur_distance_split v_row M_inv s_inv hM_sym ones_n (fun _ => 1)
  have hδ : (fun _ : Fin 1 => (1 : ℝ)) - v_row.mulVec (M_inv.mulVec ones_n) =
      fun _ => 1 - dotProduct v (M_inv.mulVec ones_n) := by
    ext i
    fin_cases i
    simp only [Pi.sub_apply, v_row, v_col, Matrix.mulVec, Matrix.transpose_apply,
      Matrix.of_apply, dotProduct]
  have hS : dotProduct (fun _ : Fin 1 => 1 - dotProduct v (M_inv.mulVec ones_n))
      (s_inv.mulVec (fun _ : Fin 1 => 1 - dotProduct v (M_inv.mulVec ones_n))) =
      (1 - dotProduct v (M_inv.mulVec ones_n)) ^ 2 / s := by
    simp [s_inv, Matrix.mulVec, dotProduct, div_eq_mul_inv, sq]
    ring
  have hdot : dotProduct ones_next (M_next_inv.mulVec ones_next) =
      dotProduct ones_n (M_inv.mulVec ones_n) +
        (1 - dotProduct v (M_inv.mulVec ones_n)) ^ 2 / s := by
    dsimp [ones_next, v_col, v_row, s_inv, B11, B12, B21, M_next_inv] at hsplit ⊢
    rw [hδ, hS, Matrix.transpose_transpose] at hsplit
    linarith
  have hstep_nonneg : 0 ≤ (1 - dotProduct v (M_inv.mulVec ones_n)) ^ 2 / s :=
    div_nonneg (sq_nonneg _) hs.le
  exact ⟨hdot, by linarith⟩

/-- **Telescoping Resolvent Sum:**
Iterating a nonnegative Schur-step recursion `R (k + 1) = R k + step k` yields
`R N = R N0 + ∑ k ∈ Finset.Ico N0 N, step k`. -/
theorem resolvent_eq_base_add_sum_schur_steps (R step : ℕ → ℝ) (N0 N : ℕ) (hN : N0 ≤ N)
    (hrec : ∀ k, N0 ≤ k → R (k + 1) = R k + step k) :
    R N = R N0 + ∑ k ∈ Finset.Ico N0 N, step k := by
  induction N, hN using Nat.le_induction with
  | base => simp
  | succ m hm ih =>
    rw [hrec m hm, ih, Finset.sum_Ico_succ_top hm]
    ring

/-- **Conditional Barrier-Breaking Reduction:**
If `R N0 ≥ 0` and the cumulative Schur-step series `∑ k ∈ Ico N0 N, step k` grows
unboundedly, then `E_dir(N) = (R N)⁻¹ → 0` (the exact open Clay RH threshold). -/
theorem inv_resolvent_lt_eps_of_schur_steps_unbounded (R step : ℕ → ℝ) (N0 : ℕ)
    (hR0 : 0 ≤ R N0)
    (hrec : ∀ k, N0 ≤ k → R (k + 1) = R k + step k)
    (_hstep_nonneg : ∀ k, N0 ≤ k → 0 ≤ step k)
    (hunbounded : ∀ B : ℝ, ∃ N ≥ N0, B < ∑ k ∈ Finset.Ico N0 N, step k) :
    ∀ ε > 0, ∃ N ≥ N0, (R N)⁻¹ < ε := by
  intro ε hε
  obtain ⟨N, hN, hB⟩ := hunbounded ε⁻¹
  have hsum_eq := resolvent_eq_base_add_sum_schur_steps R step N0 N hN hrec
  have hR_gt : ε⁻¹ < R N := by linarith
  have hR_pos : 0 < R N := lt_trans (inv_pos.mpr hε) hR_gt
  refine ⟨N, hN, ?_⟩
  rw [inv_lt_iff_one_lt_mul₀ hR_pos]
  have := mul_lt_mul_of_pos_right hR_gt hε
  rwa [inv_mul_cancel₀ hε.ne', mul_comm] at this

end RiemannBlueprint.PrimorialSchurDistanceDecay
