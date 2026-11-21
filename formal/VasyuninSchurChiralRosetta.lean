/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import Mathlib.Data.Matrix.Mul
import Mathlib.LinearAlgebra.Matrix.Symmetric
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Tactic

/-!
# Vasyunin Schur–Chiral Rosetta ("Seeing Negatively" Operator Certificates)

`NO_RH_PROOF = TRUE`:
The Clay Riemann Hypothesis remains strictly OPEN. Every theorem in this file is a
finite-dimensional algebraic audit identity in the Beurling–Nyman–Báez-Duarte setup,
compiled strictly within Lean's standard axioms `[propext, Classical.choice, Quot.sound]`.
-/

namespace RiemannBlueprint.VasyuninSchurChiralRosetta

open Matrix

/-- **Test 1a (Dirichlet Anchor Subtraction):**
Subtracting the rank-1 Dirichlet boundary baseline `b ⬝ᵥ 1ᵀ` from `Ω = b 1ᵀ + Ψ`
isolates the interior fluctuation `Ψ` and its Gram matrix `Ψᵀ Ψ`. -/
theorem dirichlet_anchor_subtraction_gram {M K : ℕ}
    (Ω Ψ : Matrix (Fin M) (Fin K) ℝ) (b : Fin M → ℝ)
    (hΩ : Ω = Matrix.of (fun i _ => b i) + Ψ) :
    Ω - Matrix.of (fun i _ => b i) = Ψ ∧
    (Ω - Matrix.of (fun i _ => b i))ᵀ * (Ω - Matrix.of (fun i _ => b i)) = Ψᵀ * Ψ := by
  have hsub : Ω - Matrix.of (fun i _ => b i) = Ψ := by
    rw [hΩ, add_sub_cancel_left]
  exact ⟨hsub, by rw [hsub]⟩

/-- **Test 1b (Superdiagonal Orthogonal Triple Diagonal Gram):**
Any `3 × 3` symmetric matrix whose off-diagonal entries `(0,1)`, `(1,2)`, `(0,2)` vanish
equals `Matrix.diagonal ![G 0 0, G 1 1, G 2 2]`, mirroring Hodge's `diag(16, 432, 1152)`. -/
theorem superdiagonal_triple_diagonal_gram (G : Matrix (Fin 3) (Fin 3) ℝ)
    (hsym : G.IsSymm) (h01 : G 0 1 = 0) (h12 : G 1 2 = 0) (h02 : G 0 2 = 0) :
    G = Matrix.diagonal ![G 0 0, G 1 1, G 2 2] := by
  have h10 : G 1 0 = 0 := by simpa [hsym.apply 0 1] using h01
  have h21 : G 2 1 = 0 := by simpa [hsym.apply 1 2] using h12
  have h20 : G 2 0 = 0 := by simpa [hsym.apply 0 2] using h02
  ext i j
  fin_cases i <;> fin_cases j <;> simp [h01, h10, h12, h21, h02, h20]

/-- **Test 2a (Palindromic Chirality Split & Squared Parity Blindness):**
For any involution `J` (`J * J = 1`), `P_+ = (1/2)•(1 + J)`, `P_- = (1/2)•(1 - J)`, and
`T_pal = P_+ - P_- = J` satisfy `P_+ + P_- = 1`, `P_+ * P_- = 0`, `T_pal^2 = 1`, and
`P_+ * (T_pal * T_pal) * P_- = 0`. -/
theorem palindromic_chirality_split_and_blindness {M : ℕ}
    (J : Matrix (Fin M) (Fin M) ℝ) (hJ : J * J = 1) :
    let Pplus : Matrix (Fin M) (Fin M) ℝ := (1 / 2 : ℝ) • (1 + J)
    let Pminus : Matrix (Fin M) (Fin M) ℝ := (1 / 2 : ℝ) • (1 - J)
    let Tpal : Matrix (Fin M) (Fin M) ℝ := Pplus - Pminus
    Pplus + Pminus = 1 ∧
    Pplus * Pminus = 0 ∧
    Tpal = J ∧
    Tpal * Tpal = 1 ∧
    Pplus * (Tpal * Tpal) * Pminus = 0 := by
  intro Pplus Pminus Tpal
  have hsum : Pplus + Pminus = 1 := by
    ext i j
    simp [Pplus, Pminus]
    ring
  have hprod : Pplus * Pminus = 0 := by
    dsimp [Pplus, Pminus]
    rw [Matrix.smul_mul, Matrix.mul_smul, smul_smul]
    have hmul : (1 + J) * (1 - J) = (0 : Matrix (Fin M) (Fin M) ℝ) := by
      rw [Matrix.add_mul, Matrix.mul_sub, Matrix.mul_sub, Matrix.one_mul, Matrix.mul_one, hJ]
      simp
    rw [hmul, smul_zero]
  have hT : Tpal = J := by
    ext i j
    simp [Tpal, Pplus, Pminus]
    ring
  have hT2 : Tpal * Tpal = 1 := by rw [hT, hJ]
  have hblind : Pplus * (Tpal * Tpal) * Pminus = 0 := by
    rw [hT2, Matrix.mul_one, hprod]
  exact ⟨hsum, hprod, hT, hT2, hblind⟩

/-- **Test 2b (Chiral Commutator Zero Projection onto `End^+`):**
For `T_pal = J` (`J^2 = 1`), the `End^+` projection `P_+ [J, H] P_+ + P_- [J, H] P_-`
vanishes identically for every operator `H`. -/
theorem palindromic_commutator_even_projection_zero {M : ℕ}
    (J H : Matrix (Fin M) (Fin M) ℝ) (hJ : J * J = 1) :
    let Pplus : Matrix (Fin M) (Fin M) ℝ := (1 / 2 : ℝ) • (1 + J)
    let Pminus : Matrix (Fin M) (Fin M) ℝ := (1 / 2 : ℝ) • (1 - J)
    let comm : Matrix (Fin M) (Fin M) ℝ := J * H - H * J
    Pplus * comm * Pplus + Pminus * comm * Pminus = 0 := by
  intro Pplus Pminus comm
  have hpJ : Pplus * J = Pplus := by
    dsimp [Pplus]
    rw [Matrix.smul_mul, Matrix.add_mul, Matrix.one_mul, hJ, add_comm]
  have hJp : J * Pplus = Pplus := by
    dsimp [Pplus]
    rw [Matrix.mul_smul, Matrix.mul_add, Matrix.mul_one, hJ, add_comm]
  have hmJ : Pminus * J = -Pminus := by
    dsimp [Pminus]
    rw [Matrix.smul_mul, Matrix.sub_mul, Matrix.one_mul, hJ, ← smul_neg]
    congr 1; abel
  have hJm : J * Pminus = -Pminus := by
    dsimp [Pminus]
    rw [Matrix.mul_smul, Matrix.mul_sub, Matrix.mul_one, hJ, ← smul_neg]
    congr 1; abel
  have h1 : Pplus * comm * Pplus = 0 := by
    dsimp [comm]
    rw [Matrix.mul_sub, Matrix.sub_mul, ← Matrix.mul_assoc, hpJ,
      Matrix.mul_assoc Pplus (H * J) Pplus, Matrix.mul_assoc H J Pplus, hJp,
      ← Matrix.mul_assoc, sub_self]
  have h2 : Pminus * comm * Pminus = 0 := by
    dsimp [comm]
    rw [Matrix.mul_sub, Matrix.sub_mul, ← Matrix.mul_assoc, hmJ,
      Matrix.mul_assoc Pminus (H * J) Pminus, Matrix.mul_assoc H J Pminus, hJm]
    simp [Matrix.mul_assoc]
  rw [h1, h2, add_zero]

/-- **Test 2c (Spatial Half-Projector Reconstruction `K_half + K_halfᵀ = 4 T_pal`):**
If `P_half` is symmetric and `P_half + J * P_half * J = 1` with `Jᵀ = J` and `J^2 = 1`,
then `K_half = 4 • (P_half * J)` reconstructs `K_half + K_halfᵀ = 4 • J`. -/
theorem spatial_half_projector_reconstruction {M : ℕ}
    (J P_half : Matrix (Fin M) (Fin M) ℝ)
    (hJ_sym : Jᵀ = J) (hJ_sq : J * J = 1)
    (hP_sym : P_halfᵀ = P_half) (hcover : P_half + J * P_half * J = 1) :
    let K_half : Matrix (Fin M) (Fin M) ℝ := (4 : ℝ) • (P_half * J)
    K_half + K_halfᵀ = (4 : ℝ) • J := by
  intro K_half
  have hKT : K_halfᵀ = (4 : ℝ) • (J * P_half) := by
    dsimp [K_half]
    rw [Matrix.transpose_mul, hJ_sym, hP_sym]
  rw [hKT, ← smul_add]
  congr 1
  calc
    P_half * J + J * P_half
        = P_half * J + J * P_half * (J * J) := by rw [hJ_sq, Matrix.mul_one]
    _ = (P_half + J * P_half * J) * J := by
        rw [Matrix.add_mul, Matrix.mul_assoc (J * P_half) J J]
    _ = 1 * J := by rw [hcover]
    _ = J := Matrix.one_mul J

/-- **Test 3 (Prime–Composite Block Schur Complement Symmetry):**
For symmetric `Q_CC` and `Q_PP⁻¹`, `Σ_Schur(C | P) = Q_CC - Q_CP * Q_PP⁻¹ * Q_CPᵀ`
is symmetric. -/
theorem block_schur_complement_symmetric {p c : ℕ}
    (Q_CC : Matrix (Fin c) (Fin c) ℝ) (Q_CP : Matrix (Fin c) (Fin p) ℝ)
    (Q_PP_inv : Matrix (Fin p) (Fin p) ℝ)
    (hCC : Q_CCᵀ = Q_CC) (hPP : Q_PP_invᵀ = Q_PP_inv) :
    let Sigma_Schur := Q_CC - Q_CP * Q_PP_inv * Q_CPᵀ
    Sigma_Schurᵀ = Sigma_Schur := by
  intro Sigma_Schur
  dsimp [Sigma_Schur]
  rw [Matrix.transpose_sub, hCC, Matrix.transpose_mul, Matrix.transpose_mul,
    Matrix.transpose_transpose, hPP, Matrix.mul_assoc]

end RiemannBlueprint.VasyuninSchurChiralRosetta
