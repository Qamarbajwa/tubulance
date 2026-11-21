/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import Mathlib.Data.Matrix.Mul
import Mathlib.LinearAlgebra.Matrix.Symmetric
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.NumberTheory.ArithmeticFunction.Moebius
import RiemannBlueprint.UnconditionalTitchmarshBridge
import RiemannBlueprint.Modules.EuclideanExhaustionTailBound

/-!
# Matrix Factorization, Exact Möbius–Difference Inversion, and Half-Observation Laws

This module transcribes the Báez–Duarte / Vasyunin / Riemann Zeta framework into explicit
matrix relations and proves the three half-observation theorems without additional axioms:

* **Part I (Additive–Multiplicative Factorization & Exact Inversion):**
  `floorMatrix M N = cumSumMatrix M * divisorMatrix M N`,
  `firstDiffMatrix M * cumSumMatrix M = 1`,
  `mobiusMatrix M * divisorMatrix M M = 1`, and
  `(mobiusMatrix M * firstDiffMatrix M) * floorMatrix M M = 1`.
* **Part II (Three-Matrix Sandwich Energy & Lebesgue Bridge):**
  `residualVec c M N = onesVec M + (cumSumMatrix M * divisorMatrix M N).mulVec (coeffVec c N)`,
  identifying `harmonicCellL2PartialSum c N M` and `∫ x in Ioc (1/(M+1)) 1, residual^2`
  with the diagonal quadratic form `rᵀ W_M r` and proving the Book X.1 tail bound.
* **Part III (Half-Observation Laws — Spatial & Palindromic Period):**
  `upperHalf_observation_zero` (vanishing on `(1/2, 1]` under Dirichlet anchoring),
  `halfObservation_quadForm_eq_double_half` (abstract reversal involution `J` folding), and
  `harmonicCellL2PartialSum_period_eq_double_halfObservation` (exact `[1, L-2]` period folding
  onto `[1, H]` with symmetric double-cone weights `W̄_half = (1/2) • (W_L + J W_R J)`).
* **Part IV (Core `(N - 2) × (N - 2)` Matrices & Half-Plane Matrix RH Criterion):**
  `dipoleGramMatrix`, `purePlaqueMatrix`, and `unitDefectMatrix`, rank-2 boundary shifts,
  universal superdiagonal zeros `dipoleGramMatrix_superdiag_eq_zero`, unconditional
  off-line zero floor `unitDefectMatrix_offline_zero_floor_unconditional` on `Re(s) > 1/2`,
  and `riemannHypothesis_of_unitDefectMatrix_vanishing_unconditional`.
* **Part V (Basal 50/50 Clock, Observation Matrices, & Upper-Half Gram Bound):**
  `baseClockVec`, orthogonal parity observation matrix `parityObsMatrix`, transformed metric
  `parityObsMatrix_conj_slabWeightMatrix`, palindromic projectors `palindromicProjPlus` /
  `palindromicProjMinus` annihilating odd metrics, `augClockGramMatrix`, `simplexLiftMatrix`,
  and the universal upper-half Gram bound `dipoleGramMatrix_quadForm_ge_half_sq`.
* **Part VI (Wavefunction Matrix `Ω_{M,N}`, Cholesky/Schur Innovations, & Spectral RH):**
  `wavefunctionVec`, `anchoredWaveMatrix`, `foldedHalfWaveVec`, exact Born norm and finite-horizon
  Gram monotonicity `anchoredWave_gram_quadForm_le_unitDefectMatrix`, Cholesky/Schur innovation
  identities `cholesky_energy_eq_one_sub_sum_sq` and `schur_one_step_innovation`, exact `{1, 2, 4}`
  dyadic energy `one_sub_SCot_dyadicFour_eq` (`1 - π/4`), and ground-state spectral RH criterion
  `riemannHypothesis_of_unitDefectMatrix_groundState_vanishing_unconditional`.
-/

namespace RiemannBlueprint.MatrixHalfObservation

open scoped BigOperators Matrix
open MeasureTheory Set Finset

private lemma sum_fin_succ_eq_sum_Icc (n : ℕ) (f : ℕ → ℝ) :
    (∑ i : Fin n, f (i.1 + 1)) = ∑ m ∈ Finset.Icc 1 n, f m := by
  refine Finset.sum_bij (fun i _ => i.1 + 1) ?_ ?_ ?_ (fun _ _ => rfl)
  · intro i _; exact Finset.mem_Icc.mpr ⟨by omega, i.isLt⟩
  · intro i₁ _ i₂ _ h; exact Fin.ext (by omega)
  · intro m hm
    have hm' := Finset.mem_Icc.mp hm
    refine ⟨⟨m - 1, by omega⟩, Finset.mem_univ _, ?_⟩
    dsimp; omega

/-! ## Part I: Additive–Multiplicative Factorization & Exact Inversion -/

/-- Lower-triangular summation matrix `Σ` (`M × M`): `(i, m) ↦ 1` if `m ≤ i`, else `0`. -/
def cumSumMatrix (M : ℕ) : Matrix (Fin M) (Fin M) ℝ :=
  fun i m => if m.1 ≤ i.1 then 1 else 0

/-- Divisibility incidence matrix `D` (`M × N`): `(m, j) ↦ 1` if `(j + 1) ∣ (m + 1)`, else `0`. -/
def divisorMatrix (M N : ℕ) : Matrix (Fin M) (Fin N) ℝ :=
  fun m j => if j.1 + 1 ∣ m.1 + 1 then 1 else 0

/-- Integer-floor quotient matrix `F` (`M × N`): `(i, j) ↦ ⌊(i + 1) / (j + 1)⌋`. -/
def floorMatrix (M N : ℕ) : Matrix (Fin M) (Fin N) ℝ :=
  fun i j => (((i.1 + 1) / (j.1 + 1) : ℕ) : ℝ)

/-- Backward first-difference matrix `Δ` (`M × M`), the left/right inverse of `Σ`. -/
def firstDiffMatrix (M : ℕ) : Matrix (Fin M) (Fin M) ℝ :=
  fun i m => if i.1 = m.1 then 1 else if i.1 = m.1 + 1 then -1 else 0

/-- Möbius divisor-inversion matrix `M_μ` (`M × M`): `(i, m) ↦ μ((i + 1)/(m + 1))` when
`(m + 1) ∣ (i + 1)`, else `0`. -/
def mobiusMatrix (M : ℕ) : Matrix (Fin M) (Fin M) ℝ :=
  fun i m => if m.1 + 1 ∣ i.1 + 1 then (ArithmeticFunction.moebius ((i.1 + 1) / (m.1 + 1)) : ℝ)
    else 0

private lemma card_Icc_filter_dvd (n d : ℕ) (hd : 1 ≤ d) :
    ((Finset.Icc 1 n).filter (d ∣ ·)).card = n / d := by
  have hdpos : 0 < d := by omega
  have hbij : ((Finset.Icc 1 n).filter (d ∣ ·)).card = (Finset.range (n / d)).card := by
    symm
    refine Finset.card_bij (fun q _ => (q + 1) * d) ?_ ?_ ?_
    · intro q hq
      have hq' : q < n / d := Finset.mem_range.mp hq
      refine Finset.mem_filter.mpr ⟨Finset.mem_Icc.mpr ⟨Nat.mul_pos (by omega) hdpos, ?_⟩,
        dvd_mul_left d (q + 1)⟩
      exact (Nat.mul_le_mul_right d (by omega : q + 1 ≤ n / d)).trans (Nat.div_mul_le_self n d)
    · intro q₁ _ q₂ _ h
      have := Nat.mul_right_cancel hdpos h
      omega
    · intro m hm
      rcases Finset.mem_filter.mp hm with ⟨hm_icc, hdvd⟩
      rcases hdvd with ⟨q, hdq⟩
      have hm_pos : 1 ≤ d * q := by rw [← hdq]; exact (Finset.mem_Icc.mp hm_icc).1
      have hm_le : d * q ≤ n := by rw [← hdq]; exact (Finset.mem_Icc.mp hm_icc).2
      have hq1 : 1 ≤ q := by
        rcases Nat.eq_zero_or_pos q with rfl | hqpos
        · simp at hm_pos
        · exact hqpos
      have hq_le : q ≤ n / d := (Nat.le_div_iff_mul_le hdpos).mpr (by simpa [mul_comm] using hm_le)
      refine ⟨q - 1, Finset.mem_range.mpr (by omega), ?_⟩
      rw [show q - 1 + 1 = q by omega, mul_comm, hdq]
  rw [hbij, Finset.card_range]

/-- **Two-Matrix Additive–Multiplicative Factorization**: `F = Σ * D` for all dimensions `M, N`. -/
theorem floorMatrix_eq_cumSum_mul_divisor (M N : ℕ) :
    floorMatrix M N = cumSumMatrix M * divisorMatrix M N := by
  ext i j
  rw [Matrix.mul_apply]
  have hi : i.1 < M := i.isLt
  have h1 : (∑ m : Fin M, cumSumMatrix M i m * divisorMatrix M N m j) =
      ∑ m ∈ (Finset.univ : Finset (Fin M)),
        if m.1 ≤ i.1 ∧ j.1 + 1 ∣ m.1 + 1 then (1 : ℝ) else 0 := by
    refine Finset.sum_congr rfl fun m _ => ?_
    dsimp [cumSumMatrix, divisorMatrix]
    by_cases hm : m.1 ≤ i.1 <;> by_cases hd : j.1 + 1 ∣ m.1 + 1 <;> simp [hm, hd]
  have h2 : (∑ m ∈ (Finset.univ : Finset (Fin M)),
        if m.1 ≤ i.1 ∧ j.1 + 1 ∣ m.1 + 1 then (1 : ℝ) else 0) =
      ∑ n ∈ (Finset.Icc 1 (i.1 + 1)).filter (j.1 + 1 ∣ ·), (1 : ℝ) := by
    rw [← Finset.sum_filter]
    refine Finset.sum_bij (fun m _ => m.1 + 1) ?_ ?_ ?_ (fun _ _ => rfl)
    · intro m hm
      rcases Finset.mem_filter.mp hm with ⟨_, hmi, hd⟩
      exact Finset.mem_filter.mpr ⟨Finset.mem_Icc.mpr ⟨by omega, by omega⟩, hd⟩
    · intro m₁ _ m₂ _ h
      exact Fin.ext (by omega)
    · intro n hn
      rcases Finset.mem_filter.mp hn with ⟨hn_icc, hd⟩
      have hn' := Finset.mem_Icc.mp hn_icc
      refine ⟨⟨n - 1, by omega⟩, Finset.mem_filter.mpr ⟨Finset.mem_univ _, ?_, ?_⟩, ?_⟩
      · dsimp; omega
      · dsimp; rwa [show n - 1 + 1 = n by omega]
      · dsimp; omega
  rw [h1, h2, Finset.sum_const, nsmul_eq_mul, mul_one,
    card_Icc_filter_dvd (i.1 + 1) (j.1 + 1) (by omega)]
  rfl

/-- **Left Inversion of Summation**: `Δ * Σ = I` for every dimension `M`. -/
theorem firstDiffMatrix_mul_cumSumMatrix (M : ℕ) :
    firstDiffMatrix M * cumSumMatrix M = 1 := by
  ext i j
  rw [Matrix.mul_apply]
  rcases Nat.eq_zero_or_pos i.1 with hi0 | hipos
  · have hsum : (∑ m : Fin M, firstDiffMatrix M i m * cumSumMatrix M m j) =
        if j.1 ≤ 0 then 1 else 0 := by
      have hterm : ∀ m : Fin M, firstDiffMatrix M i m * cumSumMatrix M m j =
          if m = i then (if j.1 ≤ 0 then 1 else 0) else 0 := fun m => by
        dsimp [firstDiffMatrix, cumSumMatrix]
        by_cases hm : m = i
        · subst hm; simp [hi0]
        · have hne1 : i.1 ≠ m.1 := fun h => hm (Fin.ext h.symm)
          have hne2 : i.1 ≠ m.1 + 1 := by omega
          simp [hne1, hne2, hm]
      rw [Finset.sum_congr rfl fun m _ => hterm m, Finset.sum_ite_eq']
      simp
    rw [hsum]
    by_cases hji : i = j
    · subst hji; simp [hi0]
    · have hjne0 : ¬ j.1 ≤ 0 := fun hle => hji (Fin.ext (by omega))
      simp [hji, hjne0]
  · set p : Fin M := ⟨i.1 - 1, by omega⟩
    have hp_ne : p ≠ i := fun h => by
      have := congrArg Fin.val h
      dsimp [p] at this
      omega
    have hterm : ∀ m : Fin M, firstDiffMatrix M i m * cumSumMatrix M m j =
        (if m = i then (if j.1 ≤ i.1 then 1 else 0) else 0) +
          (if m = p then (if j.1 ≤ i.1 - 1 then -1 else 0) else 0) := fun m => by
      dsimp [firstDiffMatrix, cumSumMatrix]
      by_cases hmi : m = i
      · subst hmi; simp [hp_ne.symm]
      · by_cases hmp : m = p
        · subst hmp
          have hne1 : i.1 ≠ p.1 := by dsimp [p]; omega
          have heq2 : i.1 = p.1 + 1 := by dsimp [p]; omega
          simp [heq2, hp_ne]
        · have hne1 : i.1 ≠ m.1 := fun h => hmi (Fin.ext h.symm)
          have hne2 : i.1 ≠ m.1 + 1 := fun h => hmp (Fin.ext (by dsimp [p]; omega))
          simp [hne1, hne2, hmi, hmp]
    rw [Finset.sum_congr rfl fun m _ => hterm m, Finset.sum_add_distrib,
      Finset.sum_ite_eq', Finset.sum_ite_eq']
    simp only [Finset.mem_univ, ↓reduceIte]
    by_cases hji : i = j
    · subst hji
      have hnot : ¬ i.1 ≤ i.1 - 1 := by omega
      simp [hnot]
    · simp only [Matrix.one_apply, hji, ↓reduceIte]
      by_cases hle : j.1 ≤ i.1
      · have hle1 : j.1 ≤ i.1 - 1 := by
          have hne : j.1 ≠ i.1 := fun h => hji (Fin.ext h.symm)
          omega
        simp [hle, hle1]
      · have hnot : ¬ j.1 ≤ i.1 - 1 := by omega
        simp [hle, hnot]

private lemma sum_moebius_div_divisors (q : ℕ) (_hq : 1 ≤ q) :
    (∑ d ∈ q.divisors, (ArithmeticFunction.moebius (q / d) : ℝ)) = if q = 1 then 1 else 0 := by
  have hZ := congrArg (fun f : ArithmeticFunction ℝ => f q)
    (ArithmeticFunction.coe_moebius_mul_coe_zeta (R := ℝ))
  rw [ArithmeticFunction.mul_apply, ArithmeticFunction.one_apply,
    Nat.sum_divisorsAntidiagonal' (fun x₁ x₂ =>
      (↑ArithmeticFunction.moebius : ArithmeticFunction ℝ) x₁ *
        (↑ArithmeticFunction.zeta : ArithmeticFunction ℝ) x₂)] at hZ
  have hsum : (∑ d ∈ q.divisors,
      (↑ArithmeticFunction.moebius : ArithmeticFunction ℝ) (q / d) *
        (↑ArithmeticFunction.zeta : ArithmeticFunction ℝ) d) =
      ∑ d ∈ q.divisors, (ArithmeticFunction.moebius (q / d) : ℝ) := by
    refine Finset.sum_congr rfl fun d hd => ?_
    have hd0 : d ≠ 0 := (Nat.pos_of_mem_divisors hd).ne'
    simp [ArithmeticFunction.intCoe_apply, ArithmeticFunction.natCoe_apply,
      ArithmeticFunction.zeta_apply, hd0]
  rw [hsum] at hZ
  exact hZ

/-- **Left Möbius Inversion of Divisibility**: `M_μ * D = I` for every dimension `M`. -/
theorem mobiusMatrix_mul_divisorMatrix (M : ℕ) :
    mobiusMatrix M * divisorMatrix M M = 1 := by
  ext i j
  rw [Matrix.mul_apply]
  have haM : i.1 + 1 ≤ M := i.isLt
  by_cases hba : j.1 + 1 ∣ i.1 + 1
  · rcases hba with ⟨q, hq⟩
    have hq1 : 1 ≤ q := by
      rcases Nat.eq_zero_or_pos q with rfl | hqp
      · simp at hq
      · exact hqp
    have hsum : (∑ m : Fin M, mobiusMatrix M i m * divisorMatrix M M m j) =
        ∑ d ∈ q.divisors, (ArithmeticFunction.moebius (q / d) : ℝ) := by
      have hterm : ∀ m : Fin M, mobiusMatrix M i m * divisorMatrix M M m j =
          if m.1 + 1 ∣ i.1 + 1 ∧ j.1 + 1 ∣ m.1 + 1 then
            (ArithmeticFunction.moebius ((i.1 + 1) / (m.1 + 1)) : ℝ) else 0 := fun m => by
        dsimp [mobiusMatrix, divisorMatrix]
        by_cases h1 : m.1 + 1 ∣ i.1 + 1 <;> by_cases h2 : j.1 + 1 ∣ m.1 + 1 <;> simp [h1, h2]
      rw [Finset.sum_congr rfl fun m _ => hterm m, ← Finset.sum_filter]
      refine Finset.sum_bij (fun m _ => (m.1 + 1) / (j.1 + 1)) ?_ ?_ ?_ ?_
      · intro m hm
        rcases Finset.mem_filter.mp hm with ⟨_, hc_dvd_a, hb_dvd_c⟩
        rcases hb_dvd_c with ⟨d, hd_eq⟩
        have hc_div : (m.1 + 1) / (j.1 + 1) = d := by
          rw [hd_eq, Nat.mul_div_right d (by omega)]
        rw [hc_div]
        refine Nat.mem_divisors.mpr ⟨?_, by omega⟩
        rcases hc_dvd_a with ⟨r, hr⟩
        refine ⟨r, ?_⟩
        apply Nat.mul_left_cancel (by omega : 0 < j.1 + 1)
        calc (j.1 + 1) * q = i.1 + 1 := hq.symm
          _ = (m.1 + 1) * r := hr
          _ = (j.1 + 1) * (d * r) := by rw [hd_eq, mul_assoc]
      · intro m₁ hm₁ m₂ hm₂ h
        rcases Finset.mem_filter.mp hm₁ with ⟨_, _, hb₁⟩
        rcases Finset.mem_filter.mp hm₂ with ⟨_, _, hb₂⟩
        have hc : m₁.1 + 1 = m₂.1 + 1 := by
          calc m₁.1 + 1 = (j.1 + 1) * ((m₁.1 + 1) / (j.1 + 1)) := (Nat.mul_div_cancel' hb₁).symm
            _ = (j.1 + 1) * ((m₂.1 + 1) / (j.1 + 1)) := by rw [h]
            _ = m₂.1 + 1 := Nat.mul_div_cancel' hb₂
        exact Fin.ext (by omega)
      · intro d hd
        rcases Nat.mem_divisors.mp hd with ⟨⟨r, hqdr⟩, _⟩
        have hd1 : 1 ≤ d := Nat.pos_of_mem_divisors hd
        have hbd_le_a : (j.1 + 1) * d ≤ i.1 + 1 := by
          have hr1 : 1 ≤ r := by
            rcases Nat.eq_zero_or_pos r with rfl | hrp
            · simp at hqdr; omega
            · exact hrp
          calc (j.1 + 1) * d ≤ (j.1 + 1) * (d * r) :=
              Nat.mul_le_mul_left (j.1 + 1) (Nat.le_mul_of_pos_right d hr1)
            _ = (j.1 + 1) * q := by rw [hqdr]
            _ = i.1 + 1 := hq.symm
        have hbd_pos : 1 ≤ (j.1 + 1) * d := Nat.mul_pos (by omega) hd1
        refine ⟨⟨(j.1 + 1) * d - 1, by omega⟩,
          Finset.mem_filter.mpr ⟨Finset.mem_univ _, ?_, ?_⟩, ?_⟩
        · dsimp
          rw [show (j.1 + 1) * d - 1 + 1 = (j.1 + 1) * d by omega]
          exact ⟨r, by calc i.1 + 1 = (j.1 + 1) * q := hq
            _ = (j.1 + 1) * (d * r) := by rw [hqdr]
            _ = (j.1 + 1) * d * r := by ring⟩
        · dsimp
          rw [show (j.1 + 1) * d - 1 + 1 = (j.1 + 1) * d by omega]
          exact dvd_mul_right (j.1 + 1) d
        · dsimp
          rw [show (j.1 + 1) * d - 1 + 1 = (j.1 + 1) * d by omega,
            Nat.mul_div_right d (by omega)]
      · intro m hm
        rcases Finset.mem_filter.mp hm with ⟨_, _, hb_dvd_c⟩
        rcases hb_dvd_c with ⟨d, hd_eq⟩
        have hc_div : (m.1 + 1) / (j.1 + 1) = d := by
          rw [hd_eq, Nat.mul_div_right d (by omega)]
        rw [hc_div, hq, hd_eq, Nat.mul_div_mul_left q d (by omega)]
    rw [hsum, sum_moebius_div_divisors q hq1]
    by_cases hij : i = j
    · have hq_one : q = 1 := by
        have hab : i.1 + 1 = j.1 + 1 := by rw [hij]
        apply Nat.mul_left_cancel (by omega : 0 < j.1 + 1)
        linarith [hq]
      simp [Matrix.one_apply, hij, hq_one]
    · have hq_ne : q ≠ 1 := by
        intro hq1'
        apply hij
        apply Fin.ext
        have : i.1 + 1 = j.1 + 1 := by rw [hq, hq1', mul_one]
        omega
      simp [hij, hq_ne]
  · have hzero : ∀ m : Fin M, mobiusMatrix M i m * divisorMatrix M M m j = 0 := fun m => by
      dsimp [mobiusMatrix, divisorMatrix]
      by_cases h1 : m.1 + 1 ∣ i.1 + 1
      · have h2 : ¬ j.1 + 1 ∣ m.1 + 1 := fun h => hba (dvd_trans h h1)
        simp [h1, h2]
      · simp [h1]
    have hij : i ≠ j := fun h => hba (by simp [h])
    simp [Finset.sum_congr rfl fun m _ => hzero m, hij]

/-- **Exact Additive–Multiplicative Left Inverse of `floorMatrix`**:
`(M_μ * Δ) * F = I` for every dimension `M`. -/
theorem inverse_floorMatrix_mul (M : ℕ) :
    (mobiusMatrix M * firstDiffMatrix M) * floorMatrix M M = 1 := by
  rw [floorMatrix_eq_cumSum_mul_divisor, Matrix.mul_assoc,
    ← Matrix.mul_assoc (firstDiffMatrix M) (cumSumMatrix M) (divisorMatrix M M),
    firstDiffMatrix_mul_cumSumMatrix, Matrix.one_mul, mobiusMatrix_mul_divisorMatrix]

/-! ## Part II: Three-Matrix Sandwich Energy Form & Lebesgue Bridge -/

/-- Diagonal harmonic slab-width matrix `W_M = diag(1 / (n * (n + 1)))`. -/
noncomputable def slabWeightMatrix (M : ℕ) : Matrix (Fin M) (Fin M) ℝ :=
  Matrix.diagonal fun i => harmonicCellWidth (i.1 + 1)

/-- Constant all-ones vector `1_n : Fin n → ℝ`. -/
def onesVec (n : ℕ) : Fin n → ℝ := fun _ => 1

/-- Finite coefficient vector `cVec = (c 1, ..., c N)`. -/
def coeffVec (c : ℕ → ℝ) (N : ℕ) : Fin N → ℝ := fun j => c (j.1 + 1)

/-- Discrete cell residual vector `r_M(n) = discreteCellResidual c N n` for `1 ≤ n ≤ M`. -/
noncomputable def residualVec (c : ℕ → ℝ) (M N : ℕ) : Fin M → ℝ :=
  fun i => discreteCellResidual c N (i.1 + 1)

/-- **Factorized Matrix-Vector Residual Law**: `r_M = 1_M + (Σ_M * D_{M,N}) *ᵥ c_N`. -/
theorem residualVec_eq_ones_add_factorized (c : ℕ → ℝ) (M N : ℕ) :
    residualVec c M N = onesVec M + (cumSumMatrix M * divisorMatrix M N).mulVec (coeffVec c N) := by
  rw [← floorMatrix_eq_cumSum_mul_divisor]
  ext i
  simp only [Pi.add_apply, residualVec, onesVec, Matrix.mulVec, dotProduct,
    floorMatrix, coeffVec, discreteCellResidual]
  congr 1
  rw [← sum_fin_succ_eq_sum_Icc N (fun k => c k * (((i.1 + 1) / k : ℕ) : ℝ))]
  refine Finset.sum_congr rfl fun j _ => by ring

/-- **Discrete L² Quadratic Form Identity**: `harmonicCellL2PartialSum c N M = r_Mᵀ W_M r_M`. -/
theorem harmonicCellL2PartialSum_eq_quadForm (c : ℕ → ℝ) (M N : ℕ) :
    harmonicCellL2PartialSum c N M =
      dotProduct (residualVec c M N) ((slabWeightMatrix M).mulVec (residualVec c M N)) := by
  unfold harmonicCellL2PartialSum slabWeightMatrix
  simp only [Matrix.mulVec_diagonal, dotProduct, residualVec]
  rw [← sum_fin_succ_eq_sum_Icc M (fun n => (discreteCellResidual c N n) ^ 2 * harmonicCellWidth n)]
  refine Finset.sum_congr rfl fun i _ => by ring

/-- **Three-Matrix Sandwich Identity on `L²(1/(M+1), 1]`**: on `D1 c N = 0` (`1 ≤ M`),
the Lebesgue set integral equals `(1 + Σ D c)ᵀ W_M (1 + Σ D c) = r_Mᵀ W_M r_M`. -/
theorem setIntegral_Ioc_eq_matrix_quadForm (c : ℕ → ℝ) (N M : ℕ) (hM : 1 ≤ M)
    (hD1 : D1 c N = 0) :
    ∫ x in Set.Ioc (1 / ((M : ℝ) + 1)) 1, (continuousNymanResidual c N x) ^ 2 =
      dotProduct (residualVec c M N) ((slabWeightMatrix M).mulVec (residualVec c M N)) := by
  rw [harmonicCellL2PartialSum_eq_setIntegral_Ioc c N hM hD1,
    harmonicCellL2PartialSum_eq_quadForm]

/-- **Matrix Quadratic-Form Book X.1 Tail Bound**: on `D1 c N = 0`, for `1 ≤ M ≤ M'`,
increasing dimension from `M` to `M'` changes `rᵀ W r` by at most `B(c, N)² / (M + 1)`. -/
theorem matrix_quadForm_tail_bound (c : ℕ → ℝ) (N M M' : ℕ) (hD1 : D1 c N = 0)
    (hM : 1 ≤ M) (hMM' : M ≤ M') :
    dotProduct (residualVec c M' N) ((slabWeightMatrix M').mulVec (residualVec c M' N)) -
        dotProduct (residualVec c M N) ((slabWeightMatrix M).mulVec (residualVec c M N)) ≤
      (uniformCellBound c N) ^ 2 / ((M : ℝ) + 1) := by
  rw [← harmonicCellL2PartialSum_eq_quadForm, ← harmonicCellL2PartialSum_eq_quadForm,
    harmonicCellL2PartialSum_sub_eq_tailSum c N hM hMM']
  exact harmonicCellL2TailSum_le_uniformCellBound_sq_div_succ hD1 hM hMM'

/-! ## Part III: Half-Observation Laws (Spatial Upper-Half & Palindromic Period Folding) -/

/-- **Spatial Upper-Half Annihilation Law (`(1/2, 1]`)**: under Dirichlet anchoring
`IsDirichletAnchored c N` (`2 ≤ N`), the upper-half interval `(1/2, 1]` carries zero `L²` residual,
so the full `L²(0, 1]` energy concentrates strictly inside the lower half `(0, 1/2]`. -/
theorem upperHalf_observation_zero {c : ℕ → ℝ} {N : ℕ} (hN : 2 ≤ N)
    (hc : IsDirichletAnchored c N) :
    (∫ x in Set.Ioc (1 / 2 : ℝ) 1, (continuousNymanResidual c N x) ^ 2 = 0) ∧
      (∫ x in Set.Ioc (0 : ℝ) 1, (continuousNymanResidual c N x) ^ 2 =
        ∫ x in Set.Ioc (0 : ℝ) (1 / 2 : ℝ), (continuousNymanResidual c N x) ^ 2) := by
  have hcell : ∫ x in Set.Ioc (1 / 2 : ℝ) 1, (continuousNymanResidual c N x) ^ 2 = 0 := by
    have h1 := setIntegral_Ioc_harmonicCell_eq c N le_rfl hc.1
    simp only [Nat.cast_one, div_one] at h1
    rw [discreteCellResidual_one_eq c (by omega : 1 ≤ N), hc.2.2] at h1
    norm_num at h1
    simpa [one_div] using h1
  have hf := continuousNymanResidual_sq_integrableOn_Ioc c N
  have hunion : Set.Ioc (0 : ℝ) 1 = Set.Ioc (0 : ℝ) (1 / 2) ∪ Set.Ioc (1 / 2) 1 := by
    ext x; simp only [Set.mem_Ioc, Set.mem_union]
    constructor
    · intro ⟨h0, h1⟩
      by_cases hx : x ≤ 1 / 2
      · exact Or.inl ⟨h0, hx⟩
      · exact Or.inr ⟨lt_of_not_ge hx, h1⟩
    · intro h
      rcases h with ⟨h0, hx⟩ | ⟨hx, h1⟩
      · exact ⟨h0, hx.trans (by norm_num)⟩
      · exact ⟨lt_trans (by norm_num) hx, h1⟩
  have hdisj : Disjoint (Set.Ioc (0 : ℝ) (1 / 2)) (Set.Ioc (1 / 2) 1) :=
    Set.disjoint_left.mpr fun x h1 h2 => by linarith [h1.2, h2.1]
  have hsub1 : Set.Ioc (0 : ℝ) (1 / 2) ⊆ Set.Ioc (0 : ℝ) 1 :=
    Set.Ioc_subset_Ioc le_rfl (by norm_num)
  have hsub2 : Set.Ioc (1 / 2 : ℝ) 1 ⊆ Set.Ioc (0 : ℝ) 1 :=
    Set.Ioc_subset_Ioc (by norm_num) le_rfl
  refine ⟨hcell, ?_⟩
  rw [hunion, MeasureTheory.setIntegral_union hdisj measurableSet_Ioc
    (hf.mono_set hsub1) (hf.mono_set hsub2), hcell, add_zero]

/-- Anti-diagonal reversal permutation matrix `J` (`H × H`): `J i j = 1` iff `i + j + 1 = H`. -/
def revPermMatrix (H : ℕ) : Matrix (Fin H) (Fin H) ℝ :=
  fun i j => if i.1 + j.1 + 1 = H then 1 else 0

/-- Symmetry of the reversal involution: `Jᵀ = J`. -/
theorem revPermMatrix_transpose (H : ℕ) : (revPermMatrix H).transpose = revPermMatrix H := by
  ext i j
  simp only [Matrix.transpose_apply, revPermMatrix]
  rw [add_comm i.1 j.1]

/-- Involution identity of reversal: `J * J = I`. -/
theorem revPermMatrix_mul_self (H : ℕ) : revPermMatrix H * revPermMatrix H = 1 := by
  ext i j
  rw [Matrix.mul_apply]
  set k : Fin H := ⟨H - 1 - i.1, by omega⟩
  have hterm : ∀ m : Fin H, revPermMatrix H i m * revPermMatrix H m j =
      if m = k then (if i = j then 1 else 0) else 0 := fun m => by
    dsimp [revPermMatrix]
    by_cases hmk : m = k
    · subst hmk
      have hik : i.1 + k.1 + 1 = H := by dsimp [k]; omega
      have hki : k.1 + i.1 + 1 = H := by omega
      by_cases hij : i = j
      · subst hij; simp [hik, hki]
      · have hne : k.1 + j.1 + 1 ≠ H := by
          intro heq
          apply hij; apply Fin.ext
          dsimp [k] at heq; omega
        simp [hik, hij, hne]
    · have hne : i.1 + m.1 + 1 ≠ H := fun heq =>
        hmk (Fin.ext (by dsimp [k]; omega))
      simp [hne, hmk]
  rw [Finset.sum_congr rfl fun m _ => hterm m, Finset.sum_ite_eq']
  simp [Matrix.one_apply]

/-- **Abstract Half-Observation Folding Theorem**: whenever `a_R = -J *ᵥ a_L` with `Jᵀ = J`,
the full two-half energy reduces identically to double the half-dimensional quadratic form under
the folded kernel `W̄_half = (1/2) • (W_L + J W_R J)`. -/
theorem halfObservation_quadForm_eq_double_half (H : ℕ)
    (WL WR : Matrix (Fin H) (Fin H) ℝ) (aL aR : Fin H → ℝ)
    (hanti : aR = -((revPermMatrix H).mulVec aL)) :
    dotProduct aL (WL.mulVec aL) + dotProduct aR (WR.mulVec aR) =
      2 * dotProduct aL
        ((((1 / 2 : ℝ) • (WL + revPermMatrix H * WR * revPermMatrix H))).mulVec aL) := by
  set J := revPermMatrix H
  have hsym : ∀ x y : Fin H → ℝ,
      dotProduct (J.mulVec x) y = dotProduct x (J.mulVec y) := fun x y => by
    calc dotProduct (J.mulVec x) y
        = dotProduct (Matrix.vecMul x J.transpose) y := by rw [Matrix.vecMul_transpose]
      _ = dotProduct (Matrix.vecMul x J) y := by rw [revPermMatrix_transpose]
      _ = dotProduct x (J.mulVec y) := (Matrix.dotProduct_mulVec x J y).symm
  have hR_quad : dotProduct aR (WR.mulVec aR) =
      dotProduct aL ((J * WR * J).mulVec aL) := by
    rw [hanti]
    simp only [Matrix.mulVec_neg, dotProduct_neg, neg_dotProduct, neg_neg]
    rw [hsym aL (WR.mulVec (J.mulVec aL)), Matrix.mul_assoc,
      ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec]
  rw [hR_quad]
  simp only [Matrix.smul_mulVec, Matrix.add_mulVec, dotProduct_smul, dotProduct_add, smul_eq_mul]
  ring

/-- Left half modular residual vector on `[1, H]` for period `L = 2 * H + 2`. -/
noncomputable def leftHalfResidual (c : ℕ → ℝ) (N H : ℕ) : Fin H → ℝ :=
  fun i => modularCellResidual c N (i.1 + 1)

/-- Right half modular residual vector on `[H + 1, 2 * H]` for period `L = 2 * H + 2`. -/
noncomputable def rightHalfResidual (c : ℕ → ℝ) (N H : ℕ) : Fin H → ℝ :=
  fun i => modularCellResidual c N (H + 1 + i.1)

/-- Diagonal harmonic slab weights on the left half `[1, H]`. -/
noncomputable def leftHalfWeights (H : ℕ) : Matrix (Fin H) (Fin H) ℝ :=
  Matrix.diagonal fun i => harmonicCellWidth (i.1 + 1)

/-- Diagonal harmonic slab weights on the right half `[H + 1, 2 * H]`. -/
noncomputable def rightHalfWeights (H : ℕ) : Matrix (Fin H) (Fin H) ℝ :=
  Matrix.diagonal fun i => harmonicCellWidth (H + 1 + i.1)

/-- Symmetric half-folded double-cone diagonal matrix `W̄_half = diag(doubleConeSymmetricWidth)`. -/
noncomputable def doubleConeHalfWeights (H : ℕ) : Matrix (Fin H) (Fin H) ℝ :=
  Matrix.diagonal fun i => doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1)

/-- **Palindromic Half-Period Antisymmetry**: `a_R = -J *ᵥ a_L` on `[1, 2H]` for `L = 2H + 2`. -/
theorem rightHalfResidual_eq_neg_rev_mulVec (c : ℕ → ℝ) (N H : ℕ) (hD1 : D1 c N = 0)
    (hD0 : D0 c N = 2) (hL : ∀ k ∈ Finset.Icc 1 N, k ∣ 2 * H + 2) :
    rightHalfResidual c N H = -((revPermMatrix H).mulVec (leftHalfResidual c N H)) := by
  ext i
  simp only [Pi.neg_apply, rightHalfResidual, Matrix.mulVec, dotProduct]
  set k : Fin H := ⟨H - 1 - i.1, by omega⟩
  have hterm : ∀ j : Fin H, revPermMatrix H i j * leftHalfResidual c N H j =
      if j = k then modularCellResidual c N (k.1 + 1) else 0 := fun j => by
    dsimp [revPermMatrix, leftHalfResidual]
    by_cases hjk : j = k
    · subst hjk
      have hik : i.1 + k.1 + 1 = H := by dsimp [k]; omega
      simp [hik]
    · have hne : i.1 + j.1 + 1 ≠ H := fun heq => hjk (Fin.ext (by dsimp [k]; omega))
      simp [hne, hjk]
  rw [Finset.sum_congr rfl fun j _ => hterm j, Finset.sum_ite_eq']
  simp only [Finset.mem_univ, ↓reduceIte]
  have href : H + 1 + i.1 = (2 * H + 2) - 1 - (k.1 + 1) := by dsimp [k]; omega
  rw [href, modularCellResidual_palindromic_neg c N (2 * H + 2) (k.1 + 1) hD1 hD0 hL (by omega)]

/-- **Folded Half-Weight Identity**: `(1/2) • (W_L + J * W_R * J) = doubleConeHalfWeights H`. -/
theorem foldedHalfWeights_eq_doubleCone (H : ℕ) :
    (1 / 2 : ℝ) • (leftHalfWeights H + revPermMatrix H * rightHalfWeights H * revPermMatrix H) =
      doubleConeHalfWeights H := by
  have hconj : revPermMatrix H * rightHalfWeights H * revPermMatrix H =
      Matrix.diagonal fun i => harmonicCellWidth (2 * H + 2 - 1 - (i.1 + 1)) := by
    ext i j
    rw [Matrix.mul_apply]
    set k : Fin H := ⟨H - 1 - i.1, by omega⟩
    have hrow : ∀ m : Fin H, (revPermMatrix H * rightHalfWeights H) i m =
        if m = k then harmonicCellWidth (H + 1 + k.1) else 0 := fun m => by
      rw [Matrix.mul_apply]
      have hinner : ∀ r : Fin H, revPermMatrix H i r * rightHalfWeights H r m =
          if r = m then (if r = k then harmonicCellWidth (H + 1 + k.1) else 0) else 0 := fun r => by
        dsimp [revPermMatrix, rightHalfWeights, Matrix.diagonal]
        by_cases hrm : r = m
        · subst hrm
          by_cases hrk : r = k
          · subst hrk
            have hik : i.1 + k.1 + 1 = H := by dsimp [k]; omega
            simp [hik]
          · have hne : i.1 + r.1 + 1 ≠ H := fun heq => hrk (Fin.ext (by dsimp [k]; omega))
            simp [hne, hrk]
        · simp [hrm]
      rw [Finset.sum_congr rfl fun r _ => hinner r, Finset.sum_ite_eq']
      by_cases hmk : m = k
      · subst hmk; simp
      · have hne : ¬ k = m := fun h => hmk h.symm
        simp [hmk]
    have hterm : ∀ m : Fin H, (revPermMatrix H * rightHalfWeights H) i m * revPermMatrix H m j =
        if m = k then (if i = j then harmonicCellWidth (2 * H + 2 - 1 - (i.1 + 1)) else 0)
          else 0 := fun m => by
      rw [hrow m]
      by_cases hmk : m = k
      · subst hmk
        dsimp [revPermMatrix]
        have hidx : H + 1 + k.1 = 2 * H + 2 - 1 - (i.1 + 1) := by dsimp [k]; omega
        by_cases hij : i = j
        · subst hij
          have hki : k.1 + i.1 + 1 = H := by dsimp [k]; omega
          simp [hki, hidx]
        · have hne : k.1 + j.1 + 1 ≠ H := fun heq => hij (Fin.ext (by dsimp [k] at heq; omega))
          simp [hne, hij]
      · simp [hmk]
    rw [Finset.sum_congr rfl fun m _ => hterm m, Finset.sum_ite_eq']
    simp only [Finset.mem_univ, ↓reduceIte]
    by_cases hij : i = j
    · subst hij; simp [Matrix.diagonal_apply_eq]
    · simp [hij, Matrix.diagonal_apply_ne]
  rw [hconj]
  ext i j
  dsimp [leftHalfWeights, doubleConeHalfWeights, doubleConeSymmetricWidth, Matrix.diagonal]
  by_cases hij : i = j
  · subst hij; simp [two_mul]; ring
  · simp [hij]

/-- **Concrete Period Half-Observation Folding Theorem**: for any period `L = 2 * H + 2` divisible
by `1..N`, the interior energy across `[1, L - 2]` equals twice the half-observation quadratic form
on `[1, H]` with symmetric double-cone weights. -/
theorem harmonicCellL2PartialSum_period_eq_double_halfObservation (c : ℕ → ℝ) (N H : ℕ)
    (hD1 : D1 c N = 0) (hD0 : D0 c N = 2) (hL : ∀ k ∈ Finset.Icc 1 N, k ∣ 2 * H + 2) :
    harmonicCellL2PartialSum c N (2 * H) =
      2 * dotProduct (leftHalfResidual c N H)
        ((doubleConeHalfWeights H).mulVec (leftHalfResidual c N H)) := by
  have hsplit_sum : harmonicCellL2PartialSum c N (2 * H) =
      dotProduct (leftHalfResidual c N H) ((leftHalfWeights H).mulVec (leftHalfResidual c N H)) +
        dotProduct (rightHalfResidual c N H)
          ((rightHalfWeights H).mulVec (rightHalfResidual c N H)) := by
    unfold harmonicCellL2PartialSum
    have hmod : ∀ n ∈ Finset.Icc 1 (2 * H),
        (discreteCellResidual c N n) ^ 2 * harmonicCellWidth n =
          (modularCellResidual c N n) ^ 2 * harmonicCellWidth n := fun n _ => by
      rw [discreteCellResidual_eq_modularCellResidual_of_D1_eq_zero c N n hD1]
    rw [Finset.sum_congr rfl hmod]
    have hunion : Finset.Icc 1 (2 * H) = Finset.Icc 1 H ∪ Finset.Icc (H + 1) (2 * H) := by
      ext n; simp only [Finset.mem_Icc, Finset.mem_union]; omega
    have hdisj : Disjoint (Finset.Icc 1 H) (Finset.Icc (H + 1) (2 * H)) :=
      Finset.disjoint_left.mpr fun n h1 h2 => by simp only [Finset.mem_Icc] at h1 h2; omega
    rw [hunion, Finset.sum_union hdisj]
    congr 1
    · simp only [leftHalfWeights, Matrix.mulVec_diagonal, dotProduct, leftHalfResidual]
      rw [← sum_fin_succ_eq_sum_Icc H
        (fun n => (modularCellResidual c N n) ^ 2 * harmonicCellWidth n)]
      refine Finset.sum_congr rfl fun i _ => by ring
    · simp only [rightHalfWeights, Matrix.mulVec_diagonal, dotProduct, rightHalfResidual]
      symm
      refine Finset.sum_bij (fun i _ => H + 1 + i.1) ?_ ?_ ?_ (fun i _ => by ring)
      · intro i _; exact Finset.mem_Icc.mpr ⟨by omega, by have := i.isLt; omega⟩
      · intro i₁ _ i₂ _ h; exact Fin.ext (by omega)
      · intro n hn
        have hn' := Finset.mem_Icc.mp hn
        refine ⟨⟨n - (H + 1), by omega⟩, Finset.mem_univ _, ?_⟩
        dsimp; omega
  rw [hsplit_sum,
    halfObservation_quadForm_eq_double_half H (leftHalfWeights H) (rightHalfWeights H)
      (leftHalfResidual c N H) (rightHalfResidual c N H)
      (rightHalfResidual_eq_neg_rev_mulVec c N H hD1 hD0 hL),
    foldedHalfWeights_eq_doubleCone H]

/-! ## Part IV: Core `(N - 2) × (N - 2)` Matrices & Right Half-Plane Criterion -/

/-- The `(N - 2) × (N - 2)` cumulative-dipole Gram matrix `G̃_N`. -/
noncomputable def dipoleGramMatrix (N : ℕ) : Matrix (Fin (N - 2)) (Fin (N - 2)) ℝ :=
  fun i j => dipoleGramEntry (i.1 + 1) (j.1 + 1)

/-- The `(N - 2) × (N - 2)` pure 4-point plaque matrix `P_N`. -/
noncomputable def purePlaqueMatrix (N : ℕ) : Matrix (Fin (N - 2)) (Fin (N - 2)) ℝ :=
  fun i j => dipolePlaqueEntry (i.1 + 1) (j.1 + 1)

/-- The `(N - 2) × (N - 2)` homogeneous Dirichlet-simplex unit-defect matrix `M_N`. -/
noncomputable def unitDefectMatrix (N : ℕ) : Matrix (Fin (N - 2)) (Fin (N - 2)) ℝ :=
  fun i j => unitDefectEntry (i.1 + 1) (j.1 + 1)

/-- Boundary cotangent drive-difference vector `u_N(i) = δ(i + 3) - δ(i + 2)`. -/
noncomputable def driveDiffVec (N : ℕ) : Fin (N - 2) → ℝ :=
  fun i => deltaCot (i.1 + 3) - deltaCot (i.1 + 2)

/-- Outer product rank-1 matrix `(u ⊗ v)_{ij} = u_i * v_j`. -/
def rankOneMatrix {n : ℕ} (u v : Fin n → ℝ) : Matrix (Fin n) (Fin n) ℝ :=
  fun i j => u i * v j

/-- Symmetry of `dipoleGramMatrix N`. -/
theorem dipoleGramMatrix_isSymm (N : ℕ) : (dipoleGramMatrix N).IsSymm := by
  ext i j; exact dipoleGramEntry_comm (j.1 + 1) (i.1 + 1)

/-- Symmetry of `purePlaqueMatrix N`. -/
theorem purePlaqueMatrix_isSymm (N : ℕ) : (purePlaqueMatrix N).IsSymm := by
  ext i j; exact dipolePlaqueEntry_comm (j.1 + 1) (i.1 + 1)

/-- Symmetry of `unitDefectMatrix N`. -/
theorem unitDefectMatrix_isSymm (N : ℕ) : (unitDefectMatrix N).IsSymm := by
  ext i j; exact unitDefectEntry_comm (j.1 + 1) (i.1 + 1)

/-- **Universal Superdiagonal Orthogonality in Matrix Form**: `(G̃_N)_{i, i+1} = 0` for all `i`. -/
theorem dipoleGramMatrix_superdiag_eq_zero (N : ℕ) (i j : Fin (N - 2)) (h : j.1 = i.1 + 1) :
    dipoleGramMatrix N i j = 0 := by
  dsimp [dipoleGramMatrix]
  rw [h, show i.1 + 1 + 1 = (i.1 + 1) + 1 by omega]
  exact (dipoleGramEntry_self_succ_eq_zero (i.1 + 1)).1

/-- **Rank-2 Shift Identity (`G̃_N` vs. `P_N`)**:
`G̃_N = P_N + (π / 2) * (u 1ᵀ + 1 uᵀ)`. -/
theorem dipoleGramMatrix_eq_purePlaque_add_boundary (N : ℕ) :
    dipoleGramMatrix N =
      purePlaqueMatrix N +
        (Real.pi / 2) •
          (rankOneMatrix (driveDiffVec N) (onesVec (N - 2)) +
            rankOneMatrix (onesVec (N - 2)) (driveDiffVec N)) := by
  ext i j
  simp only [Matrix.add_apply, Matrix.smul_apply, smul_eq_mul,
    dipoleGramMatrix, purePlaqueMatrix, rankOneMatrix, driveDiffVec, onesVec,
    dipoleGramEntry_eq_boundary_add_plaque]
  rw [show i.1 + 1 + 2 = i.1 + 3 by omega, show i.1 + 1 + 1 = i.1 + 2 by omega,
    show j.1 + 1 + 2 = j.1 + 3 by omega, show j.1 + 1 + 1 = j.1 + 2 by omega]
  ring

/-- **Homogeneous Unit-Defect Matrix Identity (`M_N` vs. `P_N`)**:
`M_N = 1 1ᵀ - (π / 2) * (u 1ᵀ + 1 uᵀ) + P_N`. -/
theorem unitDefectMatrix_eq_rankOne_sub_boundary_add_plaque (N : ℕ) :
    unitDefectMatrix N =
      rankOneMatrix (onesVec (N - 2)) (onesVec (N - 2)) -
        (Real.pi / 2) •
          (rankOneMatrix (driveDiffVec N) (onesVec (N - 2)) +
            rankOneMatrix (onesVec (N - 2)) (driveDiffVec N)) +
        purePlaqueMatrix N := by
  ext i j
  simp only [Matrix.add_apply, Matrix.sub_apply, Matrix.smul_apply, smul_eq_mul,
    unitDefectMatrix, purePlaqueMatrix, rankOneMatrix, driveDiffVec, onesVec, unitDefectEntry]
  rw [show i.1 + 1 + 2 = i.1 + 3 by omega, show i.1 + 1 + 1 = i.1 + 2 by omega,
    show j.1 + 1 + 2 = j.1 + 3 by omega, show j.1 + 1 + 1 = j.1 + 2 by omega]
  ring

/-- **Homogeneous Unit-Defect Matrix Identity (`M_N` vs. `G̃_N`)**:
`M_N = 1 1ᵀ - π * (u 1ᵀ + 1 uᵀ) + G̃_N`. -/
theorem unitDefectMatrix_eq_rankOne_sub_two_boundary_add_gram (N : ℕ) :
    unitDefectMatrix N =
      rankOneMatrix (onesVec (N - 2)) (onesVec (N - 2)) -
        Real.pi •
          (rankOneMatrix (driveDiffVec N) (onesVec (N - 2)) +
            rankOneMatrix (onesVec (N - 2)) (driveDiffVec N)) +
        dipoleGramMatrix N := by
  ext i j
  simp only [Matrix.add_apply, Matrix.sub_apply, Matrix.smul_apply, smul_eq_mul,
    unitDefectMatrix, dipoleGramMatrix, rankOneMatrix, driveDiffVec, onesVec,
    unitDefectEntry_eq_one_sub_drive_add_gram]
  rw [show i.1 + 1 + 2 = i.1 + 3 by omega, show i.1 + 1 + 1 = i.1 + 2 by omega,
    show j.1 + 1 + 2 = j.1 + 3 by omega, show j.1 + 1 + 1 = j.1 + 2 by omega]
  ring

/-- Dipole-coordinate vector `α_N ∈ ℝ^{N - 2}` extracted from `c`. -/
noncomputable def dipoleCoordVec (c : ℕ → ℝ) (N : ℕ) : Fin (N - 2) → ℝ :=
  fun i => dipoleCoord c N (i.1 + 1)

/-- **Dirichlet Simplex Constraint in Vector Form**: `1ᵀ α_N = 1` on `IsDirichletAnchored c N`. -/
theorem dotProduct_ones_dipoleCoordVec_eq_one {N : ℕ} (hN : 2 ≤ N) {c : ℕ → ℝ}
    (hc : IsDirichletAnchored c N) :
    dotProduct (onesVec (N - 2)) (dipoleCoordVec c N) = 1 := by
  rw [← sum_dipoleCoord_eq_one_of_isDirichletAnchored hN hc]
  simp only [dotProduct, onesVec, dipoleCoordVec, one_mul]
  exact sum_fin_succ_eq_sum_Icc (N - 2) (dipoleCoord c N)

private lemma quadForm_unitDefectMatrix_eq_double_sum {N : ℕ} (α : Fin (N - 2) → ℝ)
    (α' : ℕ → ℝ) (hα : ∀ i : Fin (N - 2), α' (i.1 + 1) = α i) :
    dotProduct α ((unitDefectMatrix N).mulVec α) =
      ∑ a ∈ Finset.Icc 1 (N - 2), ∑ b ∈ Finset.Icc 1 (N - 2),
        α' a * α' b * unitDefectEntry a b := by
  simp only [dotProduct, Matrix.mulVec, unitDefectMatrix, Finset.mul_sum]
  rw [← sum_fin_succ_eq_sum_Icc (N - 2) fun a =>
    ∑ b ∈ Finset.Icc 1 (N - 2), α' a * α' b * unitDefectEntry a b]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [← sum_fin_succ_eq_sum_Icc (N - 2) fun b =>
    α' (i.1 + 1) * α' b * unitDefectEntry (i.1 + 1) b]
  refine Finset.sum_congr rfl fun j _ => ?_
  rw [hα i, hα j]
  ring

/-- **Matrix Defect Reduction**: on `IsDirichletAnchored c N`, `1 - SCot c N = αᵀ M_N α`. -/
theorem one_sub_SCot_eq_unitDefectMatrix_quadForm {N : ℕ} (hN : 2 ≤ N) {c : ℕ → ℝ}
    (hc : IsDirichletAnchored c N) :
    1 - SCot vasyuninGCot c N =
      dotProduct (dipoleCoordVec c N) ((unitDefectMatrix N).mulVec (dipoleCoordVec c N)) := by
  rw [one_sub_SCot_eq_sum_unitDefectEntry_of_isDirichletAnchored hN hc,
    quadForm_unitDefectMatrix_eq_double_sum (dipoleCoordVec c N) (dipoleCoord c N) fun _ => rfl]

private lemma exists_dirichletAnchored_of_simplex {N : ℕ} (hN : 2 ≤ N) (α : Fin (N - 2) → ℝ)
    (hα : dotProduct (onesVec (N - 2)) α = 1) :
    ∃ c : ℕ → ℝ, IsDirichletAnchored c N ∧ dipoleCoordVec c N = α := by
  let α' : ℕ → ℝ := fun m =>
    if hm : 1 ≤ m ∧ m ≤ N - 2 then α ⟨m - 1, by omega⟩ else 0
  have hα' : ∑ m ∈ Finset.Icc 1 (N - 2), α' m = 1 := by
    rw [← hα]
    simp only [dotProduct, onesVec, one_mul]
    rw [← sum_fin_succ_eq_sum_Icc (N - 2) α']
    refine Finset.sum_congr rfl fun i _ => ?_
    dsimp [α']
    have hi : 1 ≤ i.1 + 1 ∧ i.1 + 1 ≤ N - 2 := ⟨by omega, i.isLt⟩
    simp [hi]
  let c : ℕ → ℝ := fun k =>
    cBaseAnchor k + ∑ m ∈ Finset.Icc 1 (N - 2), α' m * cumulativeDipole m k
  have hbase := cBaseAnchor_mem_A_N hN
  have hs_m : ∀ m ∈ Finset.Icc 1 (N - 2), 1 ≤ m ∧ m + 2 ≤ N := fun m hm =>
    ⟨(Finset.mem_Icc.mp hm).1, by have := (Finset.mem_Icc.mp hm).2; omega⟩
  have hcD1 : D1 c N = 0 := by
    unfold D1 at hbase ⊢
    simp_rw [c, add_div, Finset.sum_add_distrib, hbase.1, zero_add, Finset.sum_div]
    rw [Finset.sum_comm]
    refine Finset.sum_eq_zero fun m hm => ?_
    have hd := (cumulativeDipole_mem_tangent (hs_m m hm).1 (hs_m m hm).2).1
    unfold D1 at hd
    simp_rw [mul_div_assoc, ← Finset.mul_sum, hd, mul_zero]
  have hcD0 : D0 c N = 2 := by
    unfold D0 at hbase ⊢
    simp_rw [c, Finset.sum_add_distrib, hbase.2, add_eq_left]
    rw [Finset.sum_comm]
    refine Finset.sum_eq_zero fun m hm => ?_
    have hd := (cumulativeDipole_mem_tangent (hs_m m hm).1 (hs_m m hm).2).2
    unfold D0 at hd
    rw [← Finset.mul_sum, hd, mul_zero]
  have hcum1 : ∀ m ∈ Finset.Icc 1 (N - 2), cumulativeDipole m 1 = 1 := fun m hm => by
    unfold cumulativeDipole
    rw [Finset.sum_eq_single 1]
    · simp [harmonicWavelet]
    · intro r hr hne
      rcases r with _ | _ | r <;> [exact absurd (Finset.mem_Icc.mp hr).1 (by decide);
        exact absurd rfl hne; simp [harmonicWavelet]]
    · intro h; exact absurd (Finset.mem_Icc.mpr ⟨le_rfl, (Finset.mem_Icc.mp hm).1⟩) h
  have hc1 : c 1 = -1 := by
    have h1 : ∑ m ∈ Finset.Icc 1 (N - 2), α' m * cumulativeDipole m 1 = 1 := by
      rw [Finset.sum_congr rfl fun m hm => by rw [hcum1 m hm, mul_one], hα']
    dsimp [c, cBaseAnchor]; rw [h1]; norm_num
  have hcoord : ∀ a ∈ Finset.Icc 1 (N - 2), dipoleCoord c N a = α' a := fun a ha => by
    rw [← dipoleCoord_sub_cBaseAnchor_eq (Finset.mem_Icc.mp ha).1 (N := N) (c := c),
      show (fun k => c k - cBaseAnchor k) = fun k =>
        ∑ m ∈ Finset.Icc 1 (N - 2), α' m * cumulativeDipole m k by ext k; dsimp [c]; ring]
    unfold dipoleCoord; simp_rw [Finset.sum_div]; rw [Finset.sum_comm]
    have ht : ∀ m ∈ Finset.Icc 1 (N - 2), ∑ j ∈ Finset.Icc (a + 2) N,
        α' m * cumulativeDipole m j / (j : ℝ) = if m = a then α' a else 0 := fun m hm => by
      let F : ℕ → ℝ := fun k => if a + 2 ≤ k then 1 else 0
      have hs := cumulativeDipole_div_sum_eq_four_point F (hs_m m hm).1 (hs_m m hm).2
      rw [Finset.sum_congr rfl fun k _ => show cumulativeDipole m k * (F k / (k : ℝ)) =
        if a + 2 ≤ k then cumulativeDipole m k / (k : ℝ) else 0 from by
          dsimp [F]; split_ifs <;> ring] at hs
      simp_rw [mul_div_assoc, ← Finset.mul_sum]
      rw [show Finset.Icc (a + 2) N = (Finset.Icc 1 N).filter (fun k => a + 2 ≤ k) by
        ext k; simp only [Finset.mem_Icc, Finset.mem_filter]; omega, Finset.sum_filter, hs]
      have ha1 := (Finset.mem_Icc.mp ha).1
      by_cases hma : m = a <;> (dsimp [F]; split_ifs <;> norm_num <;> try omega)
      subst hma; simp
    rw [Finset.sum_congr rfl ht, Finset.sum_ite_eq']; simp [ha]
  refine ⟨c, ⟨hcD1, hcD0, hc1⟩, ?_⟩
  ext i
  have hi : i.1 + 1 ∈ Finset.Icc 1 (N - 2) := Finset.mem_Icc.mpr ⟨by omega, i.isLt⟩
  rw [dipoleCoordVec, hcoord (i.1 + 1) hi]
  dsimp [α']
  have hi' : 1 ≤ i.1 + 1 ∧ i.1 + 1 ≤ N - 2 := ⟨by omega, i.isLt⟩
  simp [hi']

/-- **Matrix Positive Semi-Definiteness on the Simplex**: for any `N ≥ 2` and `1ᵀ α = 1`,
`0 ≤ αᵀ M_N α`. -/
theorem unitDefectMatrix_quadForm_nonneg_of_simplex {N : ℕ} (hN : 2 ≤ N)
    (α : Fin (N - 2) → ℝ) (hα : dotProduct (onesVec (N - 2)) α = 1) :
    0 ≤ dotProduct α ((unitDefectMatrix N).mulVec α) := by
  obtain ⟨c, hc, hvec⟩ := exists_dirichletAnchored_of_simplex hN α hα
  rw [← hvec, ← one_sub_SCot_eq_unitDefectMatrix_quadForm hN hc,
    ← affine_l2_dist_eq_one_sub_scot c hc.1 hc.2.1]
  exact intervalIntegral.integral_nonneg (by norm_num) fun _ _ => sq_nonneg _

/-- **Right Half-Plane Observational Limit (`Re(s) > 1/2`) Floor — Unconditional**:
Any nontrivial off-line zero `riemannZeta s = 0` in the right half-plane `1/2 < Re(s) < 1` forces
every simplex vector `1ᵀ α = 1` at every truncation `N ≥ 2` to satisfy the uniform lower floor
`(2 * Re(s) - 1) / ‖s‖² ≤ αᵀ M_N α`. -/
theorem unitDefectMatrix_offline_zero_floor_unconditional {N : ℕ} (hN : 2 ≤ N)
    (α : Fin (N - 2) → ℝ) (hα : dotProduct (onesVec (N - 2)) α = 1)
    {s : ℂ} (hs_lo : 1 / 2 < s.re) (hs_hi : s.re < 1) (hz : riemannZeta s = 0) :
    (2 * s.re - 1) / ‖s‖ ^ 2 ≤ dotProduct α ((unitDefectMatrix N).mulVec α) := by
  obtain ⟨c, hc, hvec⟩ := exists_dirichletAnchored_of_simplex hN α hα
  have hfloor := mellin_l2_floor_of_zeta_zero_unconditional c N hc.1 hs_lo hs_hi hz
  rwa [affine_l2_dist_eq_one_sub_scot c hc.1 hc.2.1,
    one_sub_SCot_eq_unitDefectMatrix_quadForm hN hc, hvec] at hfloor

/-- **Unconditional Matrix-Simplex RH Equivalence Criterion**:
`_root_.RiemannHypothesis` follows if `inf { αᵀ M_N α | 1ᵀ α = 1 } → 0` as `N → ∞`,
with `TitchmarshMellinProperty` discharged unconditionally via `UnconditionalTitchmarshBridge`. -/
theorem riemannHypothesis_of_unitDefectMatrix_vanishing_unconditional
    (h_vanish : ∀ ε : ℝ, 0 < ε → ∃ (N : ℕ) (α : Fin (N - 2) → ℝ),
      2 ≤ N ∧ dotProduct (onesVec (N - 2)) α = 1 ∧
        dotProduct α ((unitDefectMatrix N).mulVec α) < ε) :
    _root_.RiemannHypothesis := by
  refine riemannHypothesis_of_unitDefectEntry_simplex_vanishing
    titchmarshMellinProperty_unconditional fun ε hε => ?_
  obtain ⟨N, α, hN, hα, hlt⟩ := h_vanish ε hε
  let α' : ℕ → ℝ := fun m =>
    if hm : 1 ≤ m ∧ m ≤ N - 2 then α ⟨m - 1, by omega⟩ else 0
  have hα' : ∑ m ∈ Finset.Icc 1 (N - 2), α' m = 1 := by
    rw [← hα]
    simp only [dotProduct, onesVec, one_mul]
    rw [← sum_fin_succ_eq_sum_Icc (N - 2) α']
    refine Finset.sum_congr rfl fun i _ => ?_
    dsimp [α']
    have hi : 1 ≤ i.1 + 1 ∧ i.1 + 1 ≤ N - 2 := ⟨by omega, i.isLt⟩
    simp [hi]
  have hsum_eq : ∑ a ∈ Finset.Icc 1 (N - 2), ∑ b ∈ Finset.Icc 1 (N - 2),
      α' a * α' b * unitDefectEntry a b =
      dotProduct α ((unitDefectMatrix N).mulVec α) := by
    rw [quadForm_unitDefectMatrix_eq_double_sum α α' fun i => by
      dsimp [α']
      have hi : 1 ≤ i.1 + 1 ∧ i.1 + 1 ≤ N - 2 := ⟨by omega, i.isLt⟩
      simp [hi]]
  exact ⟨N, α', hN, hα', hsum_eq ▸ hlt⟩

/-! ## Part V: Basal 50/50 Clock, Observation Matrices, & Upper-Half Gram Bound -/

/-- Basal 50/50 alternating clock vector `b_M(i) = (-1)^{i + 1}` on `Fin M`. -/
def baseClockVec (M : ℕ) : Fin M → ℝ :=
  fun i => (-1 : ℝ) ^ (i.1 + 1)

/-- **Basal 50/50 Alternating Clock Theorem**: the anchor `cBaseAnchor = (-2, 4, 0, ...)`
generates `discreteCellResidual cBaseAnchor N n = (-1)^n` for every `n : ℕ` (`2 ≤ N`). -/
theorem discreteCellResidual_cBaseAnchor_eq_neg_one_pow {N : ℕ} (hN : 2 ≤ N) (n : ℕ) :
    discreteCellResidual cBaseAnchor N n = (-1 : ℝ) ^ n := by
  unfold discreteCellResidual
  have hterm : ∀ k ∈ Finset.Icc 1 N,
      cBaseAnchor k * ((n / k : ℕ) : ℝ) =
        (if k = 1 then -2 * (n : ℝ) else 0) +
          (if k = 2 then 4 * ((n / 2 : ℕ) : ℝ) else 0) := fun k _ => by
    rcases k with _ | _ | _ | k
    · simp [cBaseAnchor]
    · simp [cBaseAnchor]
    · simp [cBaseAnchor]
    · simp [cBaseAnchor]
  have h1 : (1 : ℕ) ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨le_rfl, by omega⟩
  have h2 : (2 : ℕ) ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨by omega, hN⟩
  rw [Finset.sum_congr rfl hterm, Finset.sum_add_distrib, Finset.sum_ite_eq',
    Finset.sum_ite_eq']
  simp only [h1, h2, ↓reduceIte]
  rcases Nat.even_or_odd n with ⟨k, rfl⟩ | ⟨k, rfl⟩
  · have hdiv : (k + k) / 2 = k := by omega
    rw [hdiv, Even.neg_one_pow (⟨k, rfl⟩ : Even (k + k))]
    push_cast; ring
  · have hdiv : (2 * k + 1) / 2 = k := by omega
    rw [hdiv, Odd.neg_one_pow (⟨k, rfl⟩ : Odd (2 * k + 1))]
    push_cast; ring

/-- Matrix-vector form of the basal 50/50 clock on `Fin M`: `residualVec cBaseAnchor M N = b_M`. -/
theorem residualVec_cBaseAnchor_eq_baseClockVec {N : ℕ} (hN : 2 ≤ N) (M : ℕ) :
    residualVec cBaseAnchor M N = baseClockVec M := by
  ext i
  exact discreteCellResidual_cBaseAnchor_eq_neg_one_pow hN (i.1 + 1)

/-- **Basal 50/50 Clock L² Norm Identity**: `b_Mᵀ W_M b_M = 1 - 1 / (M + 1)`. -/
theorem baseClockVec_quadForm_eq (M : ℕ) :
    dotProduct (baseClockVec M) ((slabWeightMatrix M).mulVec (baseClockVec M)) =
      1 - 1 / ((M : ℝ) + 1) := by
  have hdot : dotProduct (baseClockVec M) ((slabWeightMatrix M).mulVec (baseClockVec M)) =
      ∑ i : Fin M, harmonicCellWidth (i.1 + 1) := by
    simp only [dotProduct, slabWeightMatrix, Matrix.mulVec_diagonal, baseClockVec]
    refine Finset.sum_congr rfl fun i _ => ?_
    have hsq : (-1 : ℝ) ^ (i.1 + 1) * (-1 : ℝ) ^ (i.1 + 1) = 1 := by
      rw [← sq, ← pow_mul, mul_comm, pow_mul, neg_one_sq, one_pow]
    calc (-1 : ℝ) ^ (i.1 + 1) * (harmonicCellWidth (i.1 + 1) * (-1 : ℝ) ^ (i.1 + 1))
        = ((-1 : ℝ) ^ (i.1 + 1) * (-1 : ℝ) ^ (i.1 + 1)) * harmonicCellWidth (i.1 + 1) := by ring
      _ = harmonicCellWidth (i.1 + 1) := by rw [hsq, one_mul]
  have hsum : ∀ m : ℕ, ∑ i : Fin m, harmonicCellWidth (i.1 + 1) = 1 - 1 / ((m : ℝ) + 1) := by
    intro m
    induction m with
    | zero => simp
    | succ k ih =>
      rw [Fin.sum_univ_castSucc]
      simp only [Fin.val_castSucc, Fin.val_last]
      rw [ih]
      unfold harmonicCellWidth
      have hk1 : ((k : ℝ) + 1) ≠ 0 := by positivity
      have hk2 : ((k : ℝ) + 2) ≠ 0 := by positivity
      push_cast
      field_simp
      ring
  rw [hdot, hsum M]

/-- **Palindromic Clock Reversal**: `J_{2H} *ᵥ b_{2H} = -b_{2H}`. -/
theorem baseClockVec_antisym_rev (H : ℕ) :
    (revPermMatrix (2 * H)).mulVec (baseClockVec (2 * H)) = -baseClockVec (2 * H) := by
  ext i
  have hiLt : i.1 < 2 * H := i.isLt
  simp only [Matrix.mulVec, dotProduct, Pi.neg_apply]
  set k : Fin (2 * H) := ⟨2 * H - 1 - i.1, by omega⟩
  have hkval : k.1 = 2 * H - 1 - i.1 := rfl
  have hterm : ∀ j : Fin (2 * H), revPermMatrix (2 * H) i j * baseClockVec (2 * H) j =
      if j = k then baseClockVec (2 * H) k else 0 := fun j => by
    dsimp [revPermMatrix]
    by_cases hjk : j = k
    · subst hjk
      have hik : i.1 + k.1 + 1 = 2 * H := by rw [hkval]; omega
      simp [hik]
    · have hne : i.1 + j.1 + 1 ≠ 2 * H := fun heq => hjk (Fin.ext (by rw [hkval]; omega))
      simp [hne, hjk]
  rw [Finset.sum_congr rfl fun j _ => hterm j, Finset.sum_ite_eq']
  simp only [Finset.mem_univ, ↓reduceIte, baseClockVec]
  rcases Nat.even_or_odd (i.1 + 1) with hi_ev | hi_od
  · have hk_od : Odd (k.1 + 1) := by
      rcases hi_ev with ⟨r, hr⟩
      exact ⟨H - r, by rw [hkval]; omega⟩
    rw [hi_ev.neg_one_pow, hk_od.neg_one_pow]
  · have hk_ev : Even (k.1 + 1) := by
      rcases hi_od with ⟨r, hr⟩
      exact ⟨H - r, by rw [hkval]; omega⟩
    rw [hi_od.neg_one_pow, hk_ev.neg_one_pow]; ring

/-- Orthogonal basal 50/50 parity observation matrix `O_{2K} = I_K ⊗ U_2` (`2K × 2K`),
mapping each adjacent pair `(r_{2k-1}, r_{2k})` to its mean and alternating coordinates. -/
noncomputable def parityObsMatrix (K : ℕ) : Matrix (Fin (2 * K)) (Fin (2 * K)) ℝ :=
  fun i j =>
    if i.1 / 2 = j.1 / 2 then
      if Even i.1 then 1 / Real.sqrt 2
      else if Even j.1 then -(1 / Real.sqrt 2) else 1 / Real.sqrt 2
    else 0

private lemma sum_fin_block_pair {K : ℕ} (b : ℕ) (hb : 2 * b + 1 < 2 * K)
    (f : Fin (2 * K) → ℝ) (hf : ∀ k : Fin (2 * K), k.1 / 2 ≠ b → f k = 0) :
    (∑ k : Fin (2 * K), f k) = f ⟨2 * b, by omega⟩ + f ⟨2 * b + 1, hb⟩ := by
  let e : Fin (2 * K) := ⟨2 * b, by omega⟩
  let o : Fin (2 * K) := ⟨2 * b + 1, hb⟩
  have heo : e ≠ o := fun h => by
    have := congrArg Fin.val h
    dsimp [e, o] at this; omega
  have hsplit : ∀ k : Fin (2 * K),
      f k = (if k = e then f e else 0) + (if k = o then f o else 0) := fun k => by
    by_cases hke : k = e
    · subst hke; simp [heo]
    · by_cases hko : k = o
      · subst hko; simp [heo.symm]
      · have hdiv : k.1 / 2 ≠ b := fun hd => by
          have hkval : k.1 = 2 * b ∨ k.1 = 2 * b + 1 := by omega
          rcases hkval with h1 | h2
          · exact hke (Fin.ext h1)
          · exact hko (Fin.ext h2)
        simp [hf k hdiv, hke, hko]
  rw [Finset.sum_congr rfl fun k _ => hsplit k, Finset.sum_add_distrib,
    Finset.sum_ite_eq', Finset.sum_ite_eq']
  simp [e, o]

private lemma parityObsMatrix_sq_two_inv :
    (1 / Real.sqrt 2) * (1 / Real.sqrt 2) = (1 / 2 : ℝ) := by
  have h2 : Real.sqrt 2 * Real.sqrt 2 = 2 := Real.mul_self_sqrt (by norm_num)
  calc (1 / Real.sqrt 2) * (1 / Real.sqrt 2)
      = 1 / (Real.sqrt 2 * Real.sqrt 2) := by ring
    _ = 1 / 2 := by rw [h2]

private lemma parityObsMatrix_col_even {K : ℕ} (i : Fin (2 * K)) (b : ℕ) (hb : 2 * b < 2 * K) :
    parityObsMatrix K i ⟨2 * b, hb⟩ =
      if i.1 / 2 = b then
        if Even i.1 then 1 / Real.sqrt 2 else -(1 / Real.sqrt 2)
      else 0 := by
  dsimp [parityObsMatrix]
  have hev : Even (2 * b) := ⟨b, by omega⟩
  have hdiv : (2 * b) / 2 = b := by omega
  rw [hdiv]
  by_cases hi : i.1 / 2 = b <;> by_cases hie : Even i.1 <;> simp [hi, hie, hev]

private lemma parityObsMatrix_col_odd {K : ℕ} (i : Fin (2 * K)) (b : ℕ)
    (hb : 2 * b + 1 < 2 * K) :
    parityObsMatrix K i ⟨2 * b + 1, hb⟩ =
      if i.1 / 2 = b then 1 / Real.sqrt 2 else 0 := by
  dsimp [parityObsMatrix]
  have hod : ¬ Even (2 * b + 1) := Nat.not_even_iff_odd.mpr ⟨b, by omega⟩
  have hdiv : (2 * b + 1) / 2 = b := by omega
  rw [hdiv]
  by_cases hi : i.1 / 2 = b <;> by_cases hie : Even i.1 <;> simp [hi, hie, hod]

/-- **Orthogonality (`O * Oᵀ = I`)**: `parityObsMatrix K` is a row-orthogonal matrix. -/
theorem parityObsMatrix_mul_transpose (K : ℕ) :
    parityObsMatrix K * (parityObsMatrix K).transpose = 1 := by
  ext i j
  rw [Matrix.mul_apply]
  have hb : 2 * (i.1 / 2) + 1 < 2 * K := by omega
  have hzero : ∀ k : Fin (2 * K), k.1 / 2 ≠ i.1 / 2 →
      parityObsMatrix K i k * (parityObsMatrix K).transpose k j = 0 := fun k hk => by
    dsimp [parityObsMatrix, Matrix.transpose_apply]
    simp [Ne.symm hk]
  rw [sum_fin_block_pair (i.1 / 2) hb _ hzero]
  simp only [Matrix.transpose_apply]
  rw [parityObsMatrix_col_even i (i.1 / 2) (by omega),
    parityObsMatrix_col_even j (i.1 / 2) (by omega),
    parityObsMatrix_col_odd i (i.1 / 2) hb,
    parityObsMatrix_col_odd j (i.1 / 2) hb]
  by_cases hdiv : j.1 / 2 = i.1 / 2
  · have hsq := parityObsMatrix_sq_two_inv
    by_cases hi : Even i.1 <;> by_cases hj : Even j.1
    · have hij : i = j := Fin.ext (by
        rcases hi with ⟨a, ha⟩; rcases hj with ⟨b, hb'⟩; omega)
      subst hij
      simp only [↓reduceIte, hi, Matrix.one_apply_eq]
      calc (1 / Real.sqrt 2) * (1 / Real.sqrt 2) + (1 / Real.sqrt 2) * (1 / Real.sqrt 2)
          = 1 / 2 + 1 / 2 := by rw [hsq]
        _ = 1 := by norm_num
    · have hij : i ≠ j := fun h => hj (h ▸ hi)
      simp [hij, hdiv, hi, hj]
    · have hij : i ≠ j := fun h => hi (h ▸ hj)
      simp [hij, hdiv, hi, hj]
    · have hij : i = j := Fin.ext (by
        rw [Nat.not_even_iff_odd] at hi hj
        rcases hi with ⟨a, ha⟩; rcases hj with ⟨b, hb'⟩; omega)
      subst hij
      simp only [↓reduceIte, hi, Matrix.one_apply_eq]
      calc -(1 / Real.sqrt 2) * -(1 / Real.sqrt 2) + (1 / Real.sqrt 2) * (1 / Real.sqrt 2)
          = 1 / 2 + 1 / 2 := by rw [neg_mul_neg, hsq]
        _ = 1 := by norm_num
  · have hij : i ≠ j := fun h => hdiv (by rw [h])
    simp [hij, hdiv]

/-- **Orthogonality (`Oᵀ * O = I`)**: `parityObsMatrix K` is a column-orthogonal matrix. -/
theorem parityObsMatrix_transpose_mul (K : ℕ) :
    (parityObsMatrix K).transpose * parityObsMatrix K = 1 := by
  ext i j
  rw [Matrix.mul_apply]
  have hb : 2 * (i.1 / 2) + 1 < 2 * K := by omega
  have hzero : ∀ k : Fin (2 * K), k.1 / 2 ≠ i.1 / 2 →
      (parityObsMatrix K).transpose i k * parityObsMatrix K k j = 0 := fun k hk => by
    dsimp [parityObsMatrix, Matrix.transpose_apply]
    simp [hk]
  rw [sum_fin_block_pair (i.1 / 2) hb _ hzero]
  simp only [Matrix.transpose_apply]
  dsimp [parityObsMatrix]
  have he_ev : Even (2 * (i.1 / 2)) := ⟨i.1 / 2, by omega⟩
  have ho_odd : ¬ Even (2 * (i.1 / 2) + 1) := Nat.not_even_iff_odd.mpr ⟨i.1 / 2, by omega⟩
  have he_div : (2 * (i.1 / 2)) / 2 = i.1 / 2 := by omega
  have ho_div : (2 * (i.1 / 2) + 1) / 2 = i.1 / 2 := by omega
  rw [he_div, ho_div]
  by_cases hdiv : i.1 / 2 = j.1 / 2
  · have hsq := parityObsMatrix_sq_two_inv
    by_cases hi : Even i.1 <;> by_cases hj : Even j.1
    · have hij : i = j := Fin.ext (by
        rcases hi with ⟨a, ha⟩; rcases hj with ⟨b, hb'⟩; omega)
      subst hij
      simp only [↓reduceIte, he_ev, ho_odd, hi, Matrix.one_apply_eq]
      calc (1 / Real.sqrt 2) * (1 / Real.sqrt 2) + -(1 / Real.sqrt 2) * -(1 / Real.sqrt 2)
          = 1 / 2 + 1 / 2 := by rw [neg_mul_neg, hsq]
        _ = 1 := by norm_num
    · have hij : i ≠ j := fun h => hj (h ▸ hi)
      simp [hij, hdiv, hi, hj]
    · have hij : i ≠ j := fun h => hi (h ▸ hj)
      simp [hij, hdiv, hi, hj]
    · have hij : i = j := Fin.ext (by
        rw [Nat.not_even_iff_odd] at hi hj
        rcases hi with ⟨a, ha⟩; rcases hj with ⟨b, hb'⟩; omega)
      subst hij
      simp only [↓reduceIte, he_ev, ho_odd, hi, Matrix.one_apply_eq]
      calc (1 / Real.sqrt 2) * (1 / Real.sqrt 2) + (1 / Real.sqrt 2) * (1 / Real.sqrt 2)
          = 1 / 2 + 1 / 2 := by rw [hsq]
        _ = 1 := by norm_num
  · have hij : i ≠ j := fun h => hdiv (by rw [h])
    simp [hij, hdiv]

/-- **50/50 Parity Channel Separation**: `O_{2K}` maps `b_{2K}` to `0` on every even-indexed
(local-mean) row and `√2` on every odd-indexed (alternating) row. -/
theorem parityObsMatrix_mulVec_baseClockVec (K : ℕ) (i : Fin (2 * K)) :
    ((parityObsMatrix K).mulVec (baseClockVec (2 * K))) i =
      if Even i.1 then 0 else Real.sqrt 2 := by
  simp only [Matrix.mulVec, dotProduct]
  have hb : 2 * (i.1 / 2) + 1 < 2 * K := by omega
  have hbe : baseClockVec (2 * K) ⟨2 * (i.1 / 2), by omega⟩ = -1 := by
    dsimp [baseClockVec]
    exact Odd.neg_one_pow ⟨i.1 / 2, by omega⟩
  have hbo : baseClockVec (2 * K) ⟨2 * (i.1 / 2) + 1, hb⟩ = 1 := by
    dsimp [baseClockVec]
    exact Even.neg_one_pow ⟨i.1 / 2 + 1, by omega⟩
  have hzero : ∀ k : Fin (2 * K), k.1 / 2 ≠ i.1 / 2 →
      parityObsMatrix K i k * baseClockVec (2 * K) k = 0 := fun k hk => by
    dsimp [parityObsMatrix]
    simp [Ne.symm hk]
  rw [sum_fin_block_pair (i.1 / 2) hb _ hzero,
    parityObsMatrix_col_even i (i.1 / 2) (by omega),
    parityObsMatrix_col_odd i (i.1 / 2) hb, hbe, hbo]
  have h2 : 2 / Real.sqrt 2 = Real.sqrt 2 := by
    have hsq : Real.sqrt 2 * Real.sqrt 2 = 2 := Real.mul_self_sqrt (by norm_num)
    have hne : Real.sqrt 2 ≠ 0 := by positivity
    field_simp; linarith [hsq]
  by_cases hi : Even i.1
  · simp [hi]
  · simp only [↓reduceIte, hi, ↓reduceIte]
    calc -(1 / Real.sqrt 2) * -1 + 1 / Real.sqrt 2 * 1 = 2 / Real.sqrt 2 := by ring
      _ = Real.sqrt 2 := h2

/-- **Transformed Parity-Channel Slab Metric**: `O_{2K} * W_{2K} * O_{2K}ᵀ` is exact
block-diagonal with `2 × 2` blocks having diagonal `1 / (4 p² - 1)` and off-diagonal
`-1 / (2 p (4 p² - 1))` where `p = i / 2 + 1`. -/
theorem parityObsMatrix_conj_slabWeightMatrix (K : ℕ) (i j : Fin (2 * K)) :
    (parityObsMatrix K * slabWeightMatrix (2 * K) * (parityObsMatrix K).transpose) i j =
      if i.1 / 2 = j.1 / 2 then
        let p : ℝ := ((i.1 / 2 + 1 : ℕ) : ℝ)
        if i = j then 1 / (4 * p ^ 2 - 1)
        else -(1 / (2 * p * (4 * p ^ 2 - 1)))
      else 0 := by
  rw [Matrix.mul_apply]
  have hdiag : ∀ k : Fin (2 * K),
      (parityObsMatrix K * slabWeightMatrix (2 * K)) i k =
        parityObsMatrix K i k * harmonicCellWidth (k.1 + 1) := fun k => by
    rw [Matrix.mul_apply]
    have ht : ∀ m : Fin (2 * K),
        parityObsMatrix K i m * slabWeightMatrix (2 * K) m k =
          if m = k then parityObsMatrix K i k * harmonicCellWidth (k.1 + 1) else 0 := fun m => by
      dsimp [slabWeightMatrix, Matrix.diagonal]
      by_cases hmk : m = k
      · subst hmk; simp
      · simp [hmk]
    rw [Finset.sum_congr rfl fun m _ => ht m, Finset.sum_ite_eq']
    simp
  rw [Finset.sum_congr rfl fun k _ => by rw [hdiag k]]
  by_cases hij_div : i.1 / 2 = j.1 / 2
  · simp only [hij_div, ↓reduceIte]
    have hb : 2 * (i.1 / 2) + 1 < 2 * K := by omega
    have hzero : ∀ k : Fin (2 * K), k.1 / 2 ≠ i.1 / 2 →
        parityObsMatrix K i k * harmonicCellWidth (k.1 + 1) *
          (parityObsMatrix K).transpose k j = 0 := fun k hk => by
      dsimp [parityObsMatrix, Matrix.transpose_apply]
      simp [Ne.symm hk]
    rw [sum_fin_block_pair (i.1 / 2) hb _ hzero]
    simp only [Matrix.transpose_apply]
    rw [parityObsMatrix_col_even i (i.1 / 2) (by omega),
      parityObsMatrix_col_even j (i.1 / 2) (by omega),
      parityObsMatrix_col_odd i (i.1 / 2) hb,
      parityObsMatrix_col_odd j (i.1 / 2) hb]
    have hwe : harmonicCellWidth ((⟨2 * (i.1 / 2), by omega⟩ : Fin (2 * K)).1 + 1) =
        1 / ((2 * ((i.1 / 2 + 1 : ℕ) : ℝ) - 1) * (2 * ((i.1 / 2 + 1 : ℕ) : ℝ))) := by
      dsimp [harmonicCellWidth]; push_cast; ring
    have hwo : harmonicCellWidth ((⟨2 * (i.1 / 2) + 1, hb⟩ : Fin (2 * K)).1 + 1) =
        1 / ((2 * ((i.1 / 2 + 1 : ℕ) : ℝ)) * (2 * ((i.1 / 2 + 1 : ℕ) : ℝ) + 1)) := by
      dsimp [harmonicCellWidth]; push_cast; ring
    rw [hwe, hwo, ← hij_div]
    set p : ℝ := ((i.1 / 2 + 1 : ℕ) : ℝ)
    have hp1 : (1 : ℝ) ≤ p := by dsimp [p]; exact_mod_cast Nat.succ_pos _
    have hp_nz : 2 * p - 1 ≠ 0 := by linarith
    have hp_nz2 : p ≠ 0 := by linarith
    have hp_nz3 : 2 * p + 1 ≠ 0 := by linarith
    have h4p : 4 * p ^ 2 - 1 = (2 * p - 1) * (2 * p + 1) := by ring
    have hsq := parityObsMatrix_sq_two_inv
    by_cases hi : Even i.1 <;> by_cases hj : Even j.1
    · have hij : i = j := Fin.ext (by
        rcases hi with ⟨a, ha⟩; rcases hj with ⟨b, hb'⟩; omega)
      subst hij
      simp only [↓reduceIte, hi, h4p]
      calc (1 / Real.sqrt 2 * (1 / ((2 * p - 1) * (2 * p))) * (1 / Real.sqrt 2) +
            1 / Real.sqrt 2 * (1 / (2 * p * (2 * p + 1))) * (1 / Real.sqrt 2))
          = ((1 / Real.sqrt 2) * (1 / Real.sqrt 2)) *
              (1 / ((2 * p - 1) * (2 * p)) + 1 / (2 * p * (2 * p + 1))) := by ring
        _ = (1 / 2) * (1 / ((2 * p - 1) * (2 * p)) + 1 / (2 * p * (2 * p + 1))) := by rw [hsq]
        _ = 1 / ((2 * p - 1) * (2 * p + 1)) := by field_simp; ring
    · have hij : i ≠ j := fun h => hj (h ▸ hi)
      simp only [↓reduceIte, hi, hj, hij, h4p]
      calc (1 / Real.sqrt 2 * (1 / ((2 * p - 1) * (2 * p))) * -(1 / Real.sqrt 2) +
            1 / Real.sqrt 2 * (1 / (2 * p * (2 * p + 1))) * (1 / Real.sqrt 2))
          = ((1 / Real.sqrt 2) * (1 / Real.sqrt 2)) *
              (1 / (2 * p * (2 * p + 1)) - 1 / ((2 * p - 1) * (2 * p))) := by ring
        _ = (1 / 2) * (1 / (2 * p * (2 * p + 1)) - 1 / ((2 * p - 1) * (2 * p))) := by rw [hsq]
        _ = -(1 / (2 * p * ((2 * p - 1) * (2 * p + 1)))) := by field_simp; ring
    · have hij : i ≠ j := fun h => hi (h ▸ hj)
      simp only [↓reduceIte, hi, hj, hij, h4p]
      calc (-(1 / Real.sqrt 2) * (1 / ((2 * p - 1) * (2 * p))) * (1 / Real.sqrt 2) +
            1 / Real.sqrt 2 * (1 / (2 * p * (2 * p + 1))) * (1 / Real.sqrt 2))
          = ((1 / Real.sqrt 2) * (1 / Real.sqrt 2)) *
              (1 / (2 * p * (2 * p + 1)) - 1 / ((2 * p - 1) * (2 * p))) := by ring
        _ = (1 / 2) * (1 / (2 * p * (2 * p + 1)) - 1 / ((2 * p - 1) * (2 * p))) := by rw [hsq]
        _ = -(1 / (2 * p * ((2 * p - 1) * (2 * p + 1)))) := by field_simp; ring
    · have hij : i = j := Fin.ext (by
        rw [Nat.not_even_iff_odd] at hi hj
        rcases hi with ⟨a, ha⟩; rcases hj with ⟨b, hb'⟩; omega)
      subst hij
      simp only [↓reduceIte, hi, h4p]
      calc (-(1 / Real.sqrt 2) * (1 / ((2 * p - 1) * (2 * p))) * -(1 / Real.sqrt 2) +
            1 / Real.sqrt 2 * (1 / (2 * p * (2 * p + 1))) * (1 / Real.sqrt 2))
          = ((1 / Real.sqrt 2) * (1 / Real.sqrt 2)) *
              (1 / ((2 * p - 1) * (2 * p)) + 1 / (2 * p * (2 * p + 1))) := by ring
        _ = (1 / 2) * (1 / ((2 * p - 1) * (2 * p)) + 1 / (2 * p * (2 * p + 1))) := by rw [hsq]
        _ = 1 / ((2 * p - 1) * (2 * p + 1)) := by field_simp; ring
  · simp only [hij_div, ↓reduceIte]
    refine Finset.sum_eq_zero fun k _ => ?_
    dsimp [parityObsMatrix, Matrix.transpose_apply]
    by_cases h1 : i.1 / 2 = k.1 / 2
    · have h2 : j.1 / 2 ≠ k.1 / 2 := fun h => hij_div (h1.trans h.symm)
      simp [h1, h2]
    · simp [h1]

/-- **Isometric Channel Preservation**: `rᵀ W_{2K} r = (O r)ᵀ (O W_{2K} Oᵀ) (O r)`. -/
theorem parityObsMatrix_preserves_quadForm (K : ℕ) (r : Fin (2 * K) → ℝ) :
    dotProduct r ((slabWeightMatrix (2 * K)).mulVec r) =
      dotProduct ((parityObsMatrix K).mulVec r)
        ((parityObsMatrix K * slabWeightMatrix (2 * K) *
          (parityObsMatrix K).transpose).mulVec ((parityObsMatrix K).mulVec r)) := by
  set O := parityObsMatrix K
  set W := slabWeightMatrix (2 * K)
  have hOtO : O.transpose * O = 1 := parityObsMatrix_transpose_mul K
  have hadj : ∀ v w : Fin (2 * K) → ℝ,
      dotProduct (O.mulVec v) w = dotProduct v (O.transpose.mulVec w) := fun v w => by
    calc dotProduct (O.mulVec v) w
        = dotProduct (Matrix.vecMul v O.transpose) w := by rw [Matrix.vecMul_transpose]
      _ = dotProduct v (O.transpose.mulVec w) := (Matrix.dotProduct_mulVec v O.transpose w).symm
  symm
  calc dotProduct (O.mulVec r) ((O * W * O.transpose).mulVec (O.mulVec r))
      = dotProduct r (O.transpose.mulVec ((O * W * O.transpose).mulVec (O.mulVec r))) :=
          hadj r _
    _ = dotProduct r (W.mulVec r) := by
          rw [Matrix.mulVec_mulVec, Matrix.mulVec_mulVec]
          have hid : O.transpose * (O * W * O.transpose) * O = W := by
            calc O.transpose * (O * W * O.transpose) * O
                = O.transpose * (O * W * (O.transpose * O)) := by simp only [Matrix.mul_assoc]
              _ = O.transpose * (O * W) := by rw [hOtO, Matrix.mul_one]
              _ = (O.transpose * O) * W := by rw [← Matrix.mul_assoc]
              _ = W := by rw [hOtO, Matrix.one_mul]
          rw [hid]

/-- Symmetric palindromic projection matrix `P_+ = (1/2) • (I + J)`. -/
noncomputable def palindromicProjPlus (n : ℕ) : Matrix (Fin n) (Fin n) ℝ :=
  (1 / 2 : ℝ) • (1 + revPermMatrix n)

/-- Antisymmetric palindromic projection matrix `P_- = (1/2) • (I - J)`. -/
noncomputable def palindromicProjMinus (n : ℕ) : Matrix (Fin n) (Fin n) ℝ :=
  (1 / 2 : ℝ) • (1 - revPermMatrix n)

/-- Partition of unity `P_+ + P_- = I`. -/
theorem palindromicProjPlus_add_minus (n : ℕ) :
    palindromicProjPlus n + palindromicProjMinus n = 1 := by
  dsimp [palindromicProjPlus, palindromicProjMinus]
  rw [← smul_add,
    show (1 + revPermMatrix n) + (1 - revPermMatrix n) =
      (2 : ℝ) • (1 : Matrix (Fin n) (Fin n) ℝ) by ext i j; simp; ring]
  simp

/-- Orthogonal idempotence: `P_+² = P_+`, `P_-² = P_-`, `P_+ P_- = 0`, `P_- P_+ = 0`. -/
theorem palindromicProj_idempotent_and_orth (n : ℕ) :
    (palindromicProjPlus n * palindromicProjPlus n = palindromicProjPlus n) ∧
    (palindromicProjMinus n * palindromicProjMinus n = palindromicProjMinus n) ∧
    (palindromicProjPlus n * palindromicProjMinus n = 0) ∧
    (palindromicProjMinus n * palindromicProjPlus n = 0) := by
  let J := revPermMatrix n
  have hJ : J * J = 1 := revPermMatrix_mul_self n
  have hpp : (1 + J) * (1 + J) = (2 : ℝ) • (1 + J) := by
    calc (1 + J) * (1 + J) = 1 * (1 + J) + J * (1 + J) := add_mul 1 J (1 + J)
      _ = (1 + J) + (J + J * J) := by rw [Matrix.one_mul, mul_add, Matrix.mul_one]
      _ = (1 + J) + (J + 1) := by rw [hJ]
      _ = (2 : ℝ) • (1 + J) := by ext i j; simp; ring
  have hmm : (1 - J) * (1 - J) = (2 : ℝ) • (1 - J) := by
    calc (1 - J) * (1 - J) = 1 * (1 - J) - J * (1 - J) := sub_mul 1 J (1 - J)
      _ = (1 - J) - (J - J * J) := by rw [Matrix.one_mul, mul_sub, Matrix.mul_one]
      _ = (1 - J) - (J - 1) := by rw [hJ]
      _ = (2 : ℝ) • (1 - J) := by ext i j; simp; ring
  have hpm : (1 + J) * (1 - J) = 0 := by
    calc (1 + J) * (1 - J) = 1 * (1 - J) + J * (1 - J) := add_mul 1 J (1 - J)
      _ = (1 - J) + (J - J * J) := by rw [Matrix.one_mul, mul_sub, Matrix.mul_one]
      _ = (1 - J) + (J - 1) := by rw [hJ]
      _ = 0 := by ext i j; simp
  have hmp : (1 - J) * (1 + J) = 0 := by
    calc (1 - J) * (1 + J) = 1 * (1 + J) - J * (1 + J) := sub_mul 1 J (1 + J)
      _ = (1 + J) - (J + J * J) := by rw [Matrix.one_mul, mul_add, Matrix.mul_one]
      _ = (1 + J) - (J + 1) := by rw [hJ]
      _ = 0 := by ext i j; simp; ring
  dsimp [palindromicProjPlus, palindromicProjMinus]
  refine ⟨?_, ?_, ?_, ?_⟩
  · change (1 / 2 : ℝ) • (1 + J) * ((1 / 2 : ℝ) • (1 + J)) = (1 / 2 : ℝ) • (1 + J)
    rw [Matrix.smul_mul, Matrix.mul_smul, smul_smul, hpp, smul_smul]; norm_num
  · change (1 / 2 : ℝ) • (1 - J) * ((1 / 2 : ℝ) • (1 - J)) = (1 / 2 : ℝ) • (1 - J)
    rw [Matrix.smul_mul, Matrix.mul_smul, smul_smul, hmm, smul_smul]; norm_num
  · change (1 / 2 : ℝ) • (1 + J) * ((1 / 2 : ℝ) • (1 - J)) = 0
    rw [Matrix.smul_mul, Matrix.mul_smul, hpm, smul_zero, smul_zero]
  · change (1 / 2 : ℝ) • (1 - J) * ((1 / 2 : ℝ) • (1 + J)) = 0
    rw [Matrix.smul_mul, Matrix.mul_smul, hmp, smul_zero, smul_zero]

/-- **Equal 50/50 Projector Traces**: for any even dimension `2 * H`,
`trace P_+ = H` and `trace P_- = H`. -/
theorem palindromicProj_trace_half (H : ℕ) :
    Matrix.trace (palindromicProjPlus (2 * H)) = (H : ℝ) ∧
      Matrix.trace (palindromicProjMinus (2 * H)) = (H : ℝ) := by
  have htrJ : Matrix.trace (revPermMatrix (2 * H)) = 0 := by
    simp only [Matrix.trace, Matrix.diag_apply, revPermMatrix]
    refine Finset.sum_eq_zero fun i _ => ?_
    have hne : i.1 + i.1 + 1 ≠ 2 * H := by omega
    simp [hne]
  have htr1 : Matrix.trace (1 : Matrix (Fin (2 * H)) (Fin (2 * H)) ℝ) = ((2 * H : ℕ) : ℝ) := by
    simp [Matrix.trace]
  dsimp [palindromicProjPlus, palindromicProjMinus]
  rw [Matrix.trace_smul, Matrix.trace_smul, Matrix.trace_add, Matrix.trace_sub, htrJ, htr1]
  push_cast
  exact ⟨by ring, by ring⟩

/-- **Unobservability of the Antisymmetric Metric**: for any weight matrix `W`,
`P_- * ((1/2) • (W - J W J)) * P_- = 0`. -/
theorem palindromicProjMinus_annihilates_odd_metric (n : ℕ) (W : Matrix (Fin n) (Fin n) ℝ) :
    palindromicProjMinus n * ((1 / 2 : ℝ) • (W - revPermMatrix n * W * revPermMatrix n)) *
        palindromicProjMinus n = 0 := by
  let J := revPermMatrix n
  have hJ : J * J = 1 := revPermMatrix_mul_self n
  have hLJ : palindromicProjMinus n * J = -palindromicProjMinus n := by
    dsimp [palindromicProjMinus]
    calc (1 / 2 : ℝ) • (1 - J) * J
        = (1 / 2 : ℝ) • ((1 - J) * J) := Matrix.smul_mul _ _ _
      _ = (1 / 2 : ℝ) • (J - 1) := by rw [sub_mul, Matrix.one_mul, hJ]
      _ = -((1 / 2 : ℝ) • (1 - J)) := by ext i j; simp; ring
  have hRJ : J * palindromicProjMinus n = -palindromicProjMinus n := by
    dsimp [palindromicProjMinus]
    calc J * ((1 / 2 : ℝ) • (1 - J))
        = (1 / 2 : ℝ) • (J * (1 - J)) := Matrix.mul_smul _ _ _
      _ = (1 / 2 : ℝ) • (J - 1) := by rw [mul_sub, Matrix.mul_one, hJ]
      _ = -((1 / 2 : ℝ) • (1 - J)) := by ext i j; simp; ring
  change palindromicProjMinus n * ((1 / 2 : ℝ) • (W - J * W * J)) *
      palindromicProjMinus n = 0
  rw [Matrix.mul_smul, Matrix.smul_mul, mul_sub, sub_mul]
  calc (1 / 2 : ℝ) •
      (palindromicProjMinus n * W * palindromicProjMinus n -
        palindromicProjMinus n * (J * W * J) * palindromicProjMinus n)
      = (1 / 2 : ℝ) •
          (palindromicProjMinus n * W * palindromicProjMinus n -
            (palindromicProjMinus n * J) * W * (J * palindromicProjMinus n)) := by
          simp only [Matrix.mul_assoc]
    _ = 0 := by
          rw [hLJ, hRJ]
          simp only [Matrix.neg_mul, Matrix.mul_neg, neg_neg, sub_self, smul_zero]

/-- Augmented `(N - 1) × (N - 1)` 50/50-clock Gram matrix `G_aug`:
index `none` is the basal 50/50 clock `cBaseAnchor`, and `some i` is the `i`-th cumulative dipole.
-/
noncomputable def augClockGramMatrix (N : ℕ) :
    Matrix (Option (Fin (N - 2))) (Option (Fin (N - 2))) ℝ :=
  fun r s => match r, s with
  | none, none => 1
  | none, some j => -(Real.pi * driveDiffVec N j)
  | some i, none => -(Real.pi * driveDiffVec N i)
  | some i, some j => dipoleGramMatrix N i j

/-- Dirichlet simplex lift matrix `S_N` (`(N - 1) × (N - 2)`) enforcing `c 1 = -1`
(`(none, j) ↦ 1`, `(some i, j) ↦ δ_{ij}`). -/
def simplexLiftMatrix (N : ℕ) : Matrix (Option (Fin (N - 2))) (Fin (N - 2)) ℝ :=
  fun r j => match r with
  | none => 1
  | some i => if i = j then 1 else 0

/-- **Exact Augmented-Gram Factorization of `M_N`**:
`M_N = S_Nᵀ * G_aug * S_N` for every truncation `N`. -/
theorem unitDefectMatrix_eq_simplexLift_conj_augClockGram (N : ℕ) :
    unitDefectMatrix N =
      (simplexLiftMatrix N).transpose * augClockGramMatrix N * simplexLiftMatrix N := by
  rw [unitDefectMatrix_eq_rankOne_sub_two_boundary_add_gram N]
  ext i j
  rw [Matrix.mul_apply, Fintype.sum_option]
  have hrow : ∀ s : Option (Fin (N - 2)),
      ((simplexLiftMatrix N).transpose * augClockGramMatrix N) i s =
        augClockGramMatrix N none s + augClockGramMatrix N (some i) s := fun s => by
    rw [Matrix.mul_apply, Fintype.sum_option]
    simp [Matrix.transpose_apply, simplexLiftMatrix, Finset.sum_ite_eq']
  simp only [hrow, simplexLiftMatrix, augClockGramMatrix, Matrix.add_apply, Matrix.sub_apply,
    Matrix.smul_apply, smul_eq_mul, rankOneMatrix, onesVec, one_mul, mul_one]
  have htail : (∑ x : Fin (N - 2),
      (-(Real.pi * driveDiffVec N x) + dipoleGramMatrix N i x) * (if x = j then 1 else 0)) =
      -(Real.pi * driveDiffVec N j) + dipoleGramMatrix N i j := by
    have hpt : ∀ x : Fin (N - 2),
        (-(Real.pi * driveDiffVec N x) + dipoleGramMatrix N i x) * (if x = j then 1 else 0) =
          if x = j then -(Real.pi * driveDiffVec N j) + dipoleGramMatrix N i j else 0 := fun x => by
      by_cases hxj : x = j
      · subst hxj; simp
      · simp [hxj]
    rw [Finset.sum_congr rfl fun x _ => hpt x, Finset.sum_ite_eq']
    simp
  rw [htail]
  ring

/-- **Universal Upper-Half Gram Lower Bound (`(1/2) * (1ᵀ α)² ≤ αᵀ G̃_N α`)**:
because every tangent vector `h = ∑ α_m d_m` has constant value `-1ᵀ α` on the upper half
`(1/2, 1]` of measure `1/2`, its Gram quadratic energy cannot fall below `(1/2) * (1ᵀ α)²`. -/
theorem dipoleGramMatrix_quadForm_ge_half_sq {N : ℕ} (hN : 2 ≤ N) (α : Fin (N - 2) → ℝ) :
    (1 / 2 : ℝ) * (dotProduct (onesVec (N - 2)) α) ^ 2 ≤
      dotProduct α ((dipoleGramMatrix N).mulVec α) := by
  let α' : ℕ → ℝ := fun m => if hm : 1 ≤ m ∧ m ≤ N - 2 then α ⟨m - 1, by omega⟩ else 0
  let h : ℕ → ℝ := fun k => ∑ m ∈ Finset.Icc 1 (N - 2), α' m * cumulativeDipole m k
  have hs_m : ∀ m ∈ Finset.Icc 1 (N - 2), 1 ≤ m ∧ m + 2 ≤ N := fun m hm =>
    ⟨(Finset.mem_Icc.mp hm).1, by have := (Finset.mem_Icc.mp hm).2; omega⟩
  have hhD1 : D1 h N = 0 := by
    unfold D1
    simp_rw [h, Finset.sum_div]; rw [Finset.sum_comm]
    refine Finset.sum_eq_zero fun m hm => ?_
    have hd := (cumulativeDipole_mem_tangent (hs_m m hm).1 (hs_m m hm).2).1
    unfold D1 at hd
    simp_rw [mul_div_assoc, ← Finset.mul_sum, hd, mul_zero]
  have hhD0 : D0 h N = 0 := by
    unfold D0
    simp_rw [h]; rw [Finset.sum_comm]
    refine Finset.sum_eq_zero fun m hm => ?_
    have hd := (cumulativeDipole_mem_tangent (hs_m m hm).1 (hs_m m hm).2).2
    unfold D0 at hd
    rw [← Finset.mul_sum, hd, mul_zero]
  have hcum1 : ∀ m ∈ Finset.Icc 1 (N - 2), cumulativeDipole m 1 = 1 := fun m hm => by
    unfold cumulativeDipole
    rw [Finset.sum_eq_single 1]
    · simp [harmonicWavelet]
    · intro r hr hne
      rcases r with _ | _ | r <;> [exact absurd (Finset.mem_Icc.mp hr).1 (by decide);
        exact absurd rfl hne; simp [harmonicWavelet]]
    · intro hg; exact absurd (Finset.mem_Icc.mpr ⟨le_rfl, (Finset.mem_Icc.mp hm).1⟩) hg
  have hh1 : h 1 = dotProduct (onesVec (N - 2)) α := by
    dsimp [h]
    rw [Finset.sum_congr rfl fun m hm => by rw [hcum1 m hm, mul_one]]
    simp only [dotProduct, onesVec, one_mul]
    rw [← sum_fin_succ_eq_sum_Icc (N - 2) α']
    refine Finset.sum_congr rfl fun i _ => ?_
    dsimp [α']
    have hi : 1 ≤ i.1 + 1 ∧ i.1 + 1 ≤ N - 2 := ⟨by omega, i.isLt⟩
    simp [hi]
  have hcoord : ∀ a ∈ Finset.Icc 1 (N - 2), dipoleCoord h N a = α' a := fun a ha => by
    unfold dipoleCoord
    simp_rw [h, Finset.sum_div]; rw [Finset.sum_comm]
    have ht : ∀ m ∈ Finset.Icc 1 (N - 2), ∑ j ∈ Finset.Icc (a + 2) N,
        α' m * cumulativeDipole m j / (j : ℝ) = if m = a then α' a else 0 := fun m hm => by
      let F : ℕ → ℝ := fun k => if a + 2 ≤ k then 1 else 0
      have hs := cumulativeDipole_div_sum_eq_four_point F (hs_m m hm).1 (hs_m m hm).2
      rw [Finset.sum_congr rfl fun k _ => show cumulativeDipole m k * (F k / (k : ℝ)) =
        if a + 2 ≤ k then cumulativeDipole m k / (k : ℝ) else 0 from by
          dsimp [F]; split_ifs <;> ring] at hs
      simp_rw [mul_div_assoc, ← Finset.mul_sum]
      rw [show Finset.Icc (a + 2) N = (Finset.Icc 1 N).filter (fun k => a + 2 ≤ k) by
        ext k; simp only [Finset.mem_Icc, Finset.mem_filter]; omega, Finset.sum_filter, hs]
      have ha1 := (Finset.mem_Icc.mp ha).1
      by_cases hma : m = a <;> (dsimp [F]; split_ifs <;> norm_num <;> try omega)
      subst hma; simp
    rw [Finset.sum_congr rfl ht, Finset.sum_ite_eq']; simp [ha]
  have hquad_eq : dotProduct α ((dipoleGramMatrix N).mulVec α) = QCot vasyuninGCot h N := by
    rw [QCot_eq_sum_dipoleGramEntry hN h hhD1 hhD0]
    simp only [dotProduct, Matrix.mulVec, dipoleGramMatrix, Finset.mul_sum]
    rw [← sum_fin_succ_eq_sum_Icc (N - 2) fun a =>
      ∑ b ∈ Finset.Icc 1 (N - 2), dipoleCoord h N a * dipoleCoord h N b * dipoleGramEntry a b]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [← sum_fin_succ_eq_sum_Icc (N - 2) fun b =>
      dipoleCoord h N (i.1 + 1) * dipoleCoord h N b * dipoleGramEntry (i.1 + 1) b]
    refine Finset.sum_congr rfl fun j _ => ?_
    have hi : i.1 + 1 ∈ Finset.Icc 1 (N - 2) := Finset.mem_Icc.mpr ⟨by omega, i.isLt⟩
    have hj : j.1 + 1 ∈ Finset.Icc 1 (N - 2) := Finset.mem_Icc.mpr ⟨by omega, j.isLt⟩
    rw [hcoord (i.1 + 1) hi, hcoord (j.1 + 1) hj]
    have hi' : 1 ≤ i.1 + 1 ∧ i.1 + 1 ≤ N - 2 := ⟨by omega, i.isLt⟩
    have hj' : 1 ≤ j.1 + 1 ∧ j.1 + 1 ≤ N - 2 := ⟨by omega, j.isLt⟩
    have hαi : α' (i.1 + 1) = α i := by dsimp [α']; simp [hi']
    have hαj : α' (j.1 + 1) = α j := by dsimp [α']; simp [hj']
    rw [hαi, hαj]
    ring
  rw [hquad_eq, ← tangent_l2_norm_sq_eq_qcot h hhD1 hhD0, ← hh1]
  have hint_full : IntervalIntegrable
      (fun x => (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2) volume 0 1 := by
    have hsq_eq : (fun x => (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2) =
        ∑ j ∈ Finset.Icc 1 N, ∑ k ∈ Finset.Icc 1 N,
          fun x => h j * h k * (recipFractScaled j x * recipFractScaled k x) := by
      funext x
      simp only [Finset.sum_apply]
      rw [sq, Finset.sum_mul_sum]
      exact Finset.sum_congr rfl fun _ _ => Finset.sum_congr rfl fun _ _ => by ring
    rw [hsq_eq]
    exact IntervalIntegrable.sum (Finset.Icc 1 N) fun j _ =>
      IntervalIntegrable.sum (Finset.Icc 1 N) fun k _ =>
        (intervalIntegrable_recipFractScaled_mul j k 0 1).const_mul _
  have hint1 : IntervalIntegrable
      (fun x => (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2) volume 0 (1 / 2) := by
    refine hint_full.mono_set ?_
    rw [Set.uIcc_of_le (by norm_num), Set.uIcc_of_le (by norm_num)]
    exact Set.Icc_subset_Icc le_rfl (by norm_num)
  have hint2 : IntervalIntegrable
      (fun x => (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2) volume (1 / 2) 1 := by
    refine hint_full.mono_set ?_
    rw [Set.uIcc_of_le (by norm_num), Set.uIcc_of_le (by norm_num)]
    exact Set.Icc_subset_Icc (by norm_num) le_rfl
  rw [← intervalIntegral.integral_add_adjacent_intervals hint1 hint2]
  have h_lo_nonneg : 0 ≤ ∫ x in (0 : ℝ)..(1 / 2),
      (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2 :=
    intervalIntegral.integral_nonneg (by norm_num) fun _ _ => sq_nonneg _
  have h_top_congr : ∫ x in (1 / 2 : ℝ)..1,
      (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2 = (1 / 2 : ℝ) * (h 1) ^ 2 := by
    have hpt : Set.EqOn
        (fun x => (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2)
        (fun _ => (h 1) ^ 2) (Set.Ioc (1 / 2 : ℝ) 1) := fun x hx => by
      have hx_lo : (1 / 2 : ℝ) < x := hx.1
      have hx_hi : x ≤ 1 := hx.2
      have hx1 : ((1 : ℕ) : ℝ) ≤ 1 / x := by
        rw [Nat.cast_one, le_div_iff₀ (by linarith)]; linarith
      have hx2 : 1 / x < ((1 : ℕ) : ℝ) + 1 := by
        rw [Nat.cast_one, div_lt_iff₀ (by linarith)]; linarith
      have hcont := continuousNymanResidual_eq_discreteCellResidual h N le_rfl hx1 hx2 hhD1
      rw [discreteCellResidual_one_eq h (by omega : 1 ≤ N)] at hcont
      dsimp only
      unfold continuousNymanResidual at hcont
      unfold recipFractScaled
      have hS : (∑ k ∈ Finset.Icc 1 N, h k * Int.fract (1 / ((k : ℝ) * x))) = -(h 1) := by linarith
      rw [hS, neg_sq]
    have hcon : ∫ x in (1 / 2 : ℝ)..1,
        (∑ k ∈ Finset.Icc 1 N, h k * recipFractScaled k x) ^ 2 =
        ∫ _ in (1 / 2 : ℝ)..1, (h 1) ^ 2 := by
      rw [intervalIntegral.integral_of_le (by norm_num : (1 / 2 : ℝ) ≤ 1),
        intervalIntegral.integral_of_le (by norm_num : (1 / 2 : ℝ) ≤ 1)]
      exact MeasureTheory.setIntegral_congr_fun measurableSet_Ioc hpt
    rw [hcon, intervalIntegral.integral_const, smul_eq_mul]
    ring
  linarith

/-! ## Part VI: Wavefunction Matrix `Ω_{M,N}`, Cholesky Innovations, & Spectral RH -/

private lemma harmonicCellWidth_nonneg (n : ℕ) : 0 ≤ harmonicCellWidth n := by
  unfold harmonicCellWidth; positivity

private lemma doubleConeSymmetricWidth_nonneg (L m : ℕ) :
    0 ≤ doubleConeSymmetricWidth L m := by
  unfold doubleConeSymmetricWidth
  exact div_nonneg (add_nonneg (harmonicCellWidth_nonneg m) (harmonicCellWidth_nonneg (L - 1 - m)))
    (by norm_num)

private lemma cumulativeDipole_one_eq_one {m : ℕ} (hm : 1 ≤ m) : cumulativeDipole m 1 = 1 := by
  unfold cumulativeDipole
  rw [Finset.sum_eq_single 1]
  · simp [harmonicWavelet]
  · intro r hr hne
    rcases r with _ | _ | r <;>
      [exact absurd (Finset.mem_Icc.mp hr).1 (by decide); exact absurd rfl hne;
        simp [harmonicWavelet]]
  · intro h; exact absurd (Finset.mem_Icc.mpr ⟨le_rfl, hm⟩) h

private lemma cot_pi_div_four_p6 : Real.cos (Real.pi / 4) / Real.sin (Real.pi / 4) = 1 := by
  rw [Real.cos_pi_div_four, Real.sin_pi_div_four]
  field_simp [(Real.sqrt_pos.mpr (by norm_num : (0 : ℝ) < 2)).ne']

private lemma vasyuninCotSum_two_p6 (b : ℕ) : vasyuninCotSum 2 b = 0 := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 2 = ({1} : Finset ℕ) by ext x; simp, Finset.sum_singleton,
    show Real.pi * ((1 : ℕ) : ℝ) / ((2 : ℕ) : ℝ) = Real.pi / 2 by push_cast; ring,
    Real.cos_pi_div_two, zero_div, mul_zero]

private lemma vasyuninCotSum_four_p6 (b : ℕ) :
    vasyuninCotSum 4 b = Int.fract ((b : ℝ) / 4) - Int.fract (3 * (b : ℝ) / 4) := by
  unfold vasyuninCotSum
  rw [show Finset.Ico 1 4 = ({1, 2, 3} : Finset ℕ) by ext x; simp; omega,
    Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton]
  push_cast
  rw [show (1 : ℝ) * b / 4 = b / 4 by ring, show Real.pi * 1 / 4 = Real.pi / 4 by ring,
    show Real.pi * 2 / 4 = Real.pi / 2 by ring, Real.cos_pi_div_two, zero_div, mul_zero,
    show Real.pi * 3 / 4 = 3 * Real.pi / 4 by ring, cot_pi_div_four_p6,
    show Real.cos (3 * Real.pi / 4) / Real.sin (3 * Real.pi / 4) = -1 by
      rw [show 3 * Real.pi / 4 = Real.pi - Real.pi / 4 by ring, Real.cos_pi_sub, Real.sin_pi_sub,
        neg_div, cot_pi_div_four_p6]]
  ring

private lemma sum_Icc_one_four_p6 (f : ℕ → ℝ) :
    ∑ k ∈ Finset.Icc 1 4, f k = f 1 + f 2 + f 3 + f 4 := by
  rw [show Finset.Icc 1 4 = ({1, 2, 3, 4} : Finset ℕ) by
    ext x; simp only [Finset.mem_Icc, Finset.mem_insert, Finset.mem_singleton]; omega]
  norm_num [Finset.sum_insert, add_assoc]

/-- Square-root harmonic slab weight matrix `W_M^{1/2} = diag(√w_n)` on `Fin M`. -/
noncomputable def slabWeightSqrtMatrix (M : ℕ) : Matrix (Fin M) (Fin M) ℝ :=
  Matrix.diagonal fun i => Real.sqrt (harmonicCellWidth (i.1 + 1))

/-- Normalized wavefunction state vector `ψ_{M,N} = W_M^{1/2} r_M` whose Euclidean norm squared
equals the discrete `L²` cell energy. -/
noncomputable def wavefunctionVec (c : ℕ → ℝ) (M N : ℕ) : Fin M → ℝ :=
  (slabWeightSqrtMatrix M).mulVec (residualVec c M N)

/-- Exact square-root factorization of the slab weight metric: `W_M^{1/2} * W_M^{1/2} = W_M`. -/
theorem slabWeightSqrtMatrix_mul_self (M : ℕ) :
    slabWeightSqrtMatrix M * slabWeightSqrtMatrix M = slabWeightMatrix M := by
  ext i j
  dsimp [slabWeightSqrtMatrix, slabWeightMatrix]
  rw [Matrix.diagonal_mul_diagonal]
  by_cases hij : i = j
  · subst hij
    simp [Matrix.diagonal_apply_eq, Real.mul_self_sqrt (harmonicCellWidth_nonneg (i.1 + 1))]
  · simp [Matrix.diagonal_apply_ne _ hij]

/-- **Born Norm Law for `wavefunctionVec`**: `‖ψ_{M,N}‖₂² = harmonicCellL2PartialSum c N M`. -/
theorem wavefunctionVec_norm_sq_eq_partialSum (c : ℕ → ℝ) (M N : ℕ) :
    dotProduct (wavefunctionVec c M N) (wavefunctionVec c M N) =
      harmonicCellL2PartialSum c N M := by
  rw [harmonicCellL2PartialSum_eq_quadForm]
  have hsym : (slabWeightSqrtMatrix M).transpose = slabWeightSqrtMatrix M := by
    dsimp [slabWeightSqrtMatrix]; exact Matrix.diagonal_transpose _
  calc dotProduct (wavefunctionVec c M N) (wavefunctionVec c M N)
      = dotProduct ((slabWeightSqrtMatrix M).mulVec (residualVec c M N))
          ((slabWeightSqrtMatrix M).mulVec (residualVec c M N)) := rfl
    _ = dotProduct (Matrix.vecMul (residualVec c M N) (slabWeightSqrtMatrix M).transpose)
          ((slabWeightSqrtMatrix M).mulVec (residualVec c M N)) := by
          rw [Matrix.vecMul_transpose]
    _ = dotProduct (residualVec c M N)
          ((slabWeightSqrtMatrix M).transpose.mulVec
            ((slabWeightSqrtMatrix M).mulVec (residualVec c M N))) :=
          (Matrix.dotProduct_mulVec _ _ _).symm
    _ = dotProduct (residualVec c M N) ((slabWeightMatrix M).mulVec (residualVec c M N)) := by
          rw [hsym, Matrix.mulVec_mulVec, slabWeightSqrtMatrix_mul_self]

/-- **Wavefunction Lebesgue Integral Identity**: on `D1 c N = 0` (`1 ≤ M`),
`∫ x in Ioc (1/(M+1)) 1, residual^2 = ψᵀ ψ`. -/
theorem setIntegral_Ioc_eq_wavefunctionVec_norm_sq (c : ℕ → ℝ) (N M : ℕ) (hM : 1 ≤ M)
    (hD1 : D1 c N = 0) :
    ∫ x in Set.Ioc (1 / ((M : ℝ) + 1)) 1, (continuousNymanResidual c N x) ^ 2 =
      dotProduct (wavefunctionVec c M N) (wavefunctionVec c M N) := by
  rw [setIntegral_Ioc_eq_matrix_quadForm c N M hM hD1, ← harmonicCellL2PartialSum_eq_quadForm,
    wavefunctionVec_norm_sq_eq_partialSum]

/-- Basal 50/50 vacuum wavefunction `b̃_M = W_M^{1/2} b_M` generating `(-1)^n / √(n(n+1))`. -/
noncomputable def vacuumWaveVec (M : ℕ) : Fin M → ℝ :=
  (slabWeightSqrtMatrix M).mulVec (baseClockVec M)

/-- **Vacuum Wavefunction Norm Law**: `‖b̃_M‖₂² = 1 - 1 / (M + 1)`. -/
theorem vacuumWaveVec_norm_sq_eq (M : ℕ) :
    dotProduct (vacuumWaveVec M) (vacuumWaveVec M) = 1 - 1 / ((M : ℝ) + 1) := by
  rw [← baseClockVec_quadForm_eq M]
  have hsym : (slabWeightSqrtMatrix M).transpose = slabWeightSqrtMatrix M := by
    dsimp [slabWeightSqrtMatrix]; exact Matrix.diagonal_transpose _
  calc dotProduct (vacuumWaveVec M) (vacuumWaveVec M)
      = dotProduct ((slabWeightSqrtMatrix M).mulVec (baseClockVec M))
          ((slabWeightSqrtMatrix M).mulVec (baseClockVec M)) := rfl
    _ = dotProduct (Matrix.vecMul (baseClockVec M) (slabWeightSqrtMatrix M).transpose)
          ((slabWeightSqrtMatrix M).mulVec (baseClockVec M)) := by
          rw [Matrix.vecMul_transpose]
    _ = dotProduct (baseClockVec M)
          ((slabWeightSqrtMatrix M).transpose.mulVec
            ((slabWeightSqrtMatrix M).mulVec (baseClockVec M))) :=
          (Matrix.dotProduct_mulVec _ _ _).symm
    _ = dotProduct (baseClockVec M) ((slabWeightMatrix M).mulVec (baseClockVec M)) := by
          rw [hsym, Matrix.mulVec_mulVec, slabWeightSqrtMatrix_mul_self]

/-- Cumulative-dipole excitation matrix `Ψ_{M,N}` (`M × (N - 2)`): entry `(i, m)` is the
weighted dipole response `√w_{i+1} * ∑_{k=1}^N d_{m+1}(k) ⌊(i+1)/k⌋`. -/
noncomputable def dipoleExcitationMatrix (M N : ℕ) : Matrix (Fin M) (Fin (N - 2)) ℝ :=
  fun i m => Real.sqrt (harmonicCellWidth (i.1 + 1)) *
    (∑ k ∈ Finset.Icc 1 N, cumulativeDipole (m.1 + 1) k * (((i.1 + 1) / k : ℕ) : ℝ))

/-- Anchored wavefunction matrix `Ω_{M,N} = |b̃_M⟩ 1ᵀ + Ψ_{M,N}` (`M × (N - 2)`), mapping
any Dirichlet simplex vector `α` (`1ᵀ α = 1`) directly to the normalized wavefunction state. -/
noncomputable def anchoredWaveMatrix (M N : ℕ) : Matrix (Fin M) (Fin (N - 2)) ℝ :=
  fun i m => vacuumWaveVec M i + dipoleExcitationMatrix M N i m

/-- **Upper-Half Wavefunction Matrix Annihilation**: the first row (`n = 1`, interval `(1/2, 1]`)
of `anchoredWaveMatrix M N` is identically zero in every column `m`. -/
theorem anchoredWaveMatrix_topRow_zero {M N : ℕ} (hM : 1 ≤ M) (hN : 2 ≤ N)
    (m : Fin (N - 2)) :
    anchoredWaveMatrix M N ⟨0, by omega⟩ m = 0 := by
  dsimp [anchoredWaveMatrix, vacuumWaveVec, dipoleExcitationMatrix, slabWeightSqrtMatrix,
    baseClockVec]
  rw [Matrix.mulVec_diagonal]
  dsimp
  have h1 : (1 : ℕ) ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨le_rfl, by omega⟩
  have hsum : (∑ k ∈ Finset.Icc 1 N,
      cumulativeDipole (m.1 + 1) k * ((1 / k : ℕ) : ℝ)) = 1 := by
    rw [Finset.sum_eq_single 1]
    · simp [cumulativeDipole_one_eq_one (by omega : 1 ≤ m.1 + 1)]
    · intro k hk hne
      have hk1 := (Finset.mem_Icc.mp hk).1
      have hdiv : 1 / k = 0 := Nat.div_eq_of_lt (by omega)
      simp [hdiv]
    · intro hg; exact absurd h1 hg
  rw [hsum]
  simp only [baseClockVec, zero_add, pow_one]
  ring

/-- **Exact Wavefunction Superposition Law**: on `IsDirichletAnchored c N`,
`ψ_{M,N} = Ω_{M,N} *ᵥ α_N`. -/
theorem wavefunctionVec_eq_anchoredWaveMatrix_mulVec {c : ℕ → ℝ} {M N : ℕ} (hN : 2 ≤ N)
    (hc : IsDirichletAnchored c N) :
    wavefunctionVec c M N = (anchoredWaveMatrix M N).mulVec (dipoleCoordVec c N) := by
  ext i
  have hres_split : discreteCellResidual c N (i.1 + 1) =
      (-1 : ℝ) ^ (i.1 + 1) + ∑ m : Fin (N - 2), dipoleCoordVec c N m *
        (∑ k ∈ Finset.Icc 1 N, cumulativeDipole (m.1 + 1) k * (((i.1 + 1) / k : ℕ) : ℝ)) := by
    have hc_eq : ∀ k ∈ Finset.Icc 1 N, c k = cBaseAnchor k +
        ∑ m ∈ Finset.Icc 1 (N - 2), dipoleCoord c N m * cumulativeDipole m k := fun k hk =>
      eq_cBaseAnchor_add_sum_cumulativeDipole_of_mem_A_N hN c hc.1 hc.2.1 hk
    unfold discreteCellResidual
    rw [Finset.sum_congr rfl fun k hk => by
      rw [hc_eq k hk, add_mul, Finset.sum_mul]]
    rw [Finset.sum_add_distrib]
    have hbase : 1 + ∑ k ∈ Finset.Icc 1 N, cBaseAnchor k * (((i.1 + 1) / k : ℕ) : ℝ) =
        (-1 : ℝ) ^ (i.1 + 1) := by
      have hb := discreteCellResidual_cBaseAnchor_eq_neg_one_pow hN (i.1 + 1)
      unfold discreteCellResidual at hb
      exact hb
    rw [← add_assoc, hbase]
    congr 1
    rw [Finset.sum_comm]
    rw [← sum_fin_succ_eq_sum_Icc (N - 2) fun m =>
      ∑ k ∈ Finset.Icc 1 N,
        dipoleCoord c N m * cumulativeDipole m k * (((i.1 + 1) / k : ℕ) : ℝ)]
    refine Finset.sum_congr rfl fun m _ => ?_
    simp only [dipoleCoordVec, mul_assoc, ← Finset.mul_sum]
  have hsum_alpha : (∑ m : Fin (N - 2), dipoleCoordVec c N m) = 1 := by
    have hs := dotProduct_ones_dipoleCoordVec_eq_one hN hc
    simpa [dotProduct, onesVec, one_mul] using hs
  have hvac : vacuumWaveVec M i =
      Real.sqrt (harmonicCellWidth (i.1 + 1)) * (-1 : ℝ) ^ (i.1 + 1) := by
    dsimp [vacuumWaveVec, slabWeightSqrtMatrix]
    rw [Matrix.mulVec_diagonal]
    rfl
  dsimp [wavefunctionVec, slabWeightSqrtMatrix]
  rw [Matrix.mulVec_diagonal]
  dsimp [residualVec, Matrix.mulVec, dotProduct]
  rw [hres_split, mul_add, Finset.mul_sum]
  have h1 : Real.sqrt (harmonicCellWidth (i.1 + 1)) * (-1 : ℝ) ^ (i.1 + 1) =
      ∑ m : Fin (N - 2), vacuumWaveVec M i * dipoleCoordVec c N m := by
    rw [hvac, ← Finset.mul_sum, hsum_alpha, mul_one]
  rw [h1, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun m _ => ?_
  dsimp [anchoredWaveMatrix, dipoleExcitationMatrix]
  ring

/-- **Wavefunction Gram Factorization of Cell Energy**: on `IsDirichletAnchored c N`,
`harmonicCellL2PartialSum c N M = α_Nᵀ (Ω_{M,N}ᵀ Ω_{M,N}) α_N`. -/
theorem harmonicCellL2PartialSum_eq_anchoredWave_gram_quadForm {c : ℕ → ℝ} {M N : ℕ} (hN : 2 ≤ N)
    (hc : IsDirichletAnchored c N) :
    harmonicCellL2PartialSum c N M =
      dotProduct (dipoleCoordVec c N)
        (((anchoredWaveMatrix M N).transpose * anchoredWaveMatrix M N).mulVec
          (dipoleCoordVec c N)) := by
  rw [← wavefunctionVec_norm_sq_eq_partialSum, wavefunctionVec_eq_anchoredWaveMatrix_mulVec hN hc]
  calc dotProduct ((anchoredWaveMatrix M N).mulVec (dipoleCoordVec c N))
        ((anchoredWaveMatrix M N).mulVec (dipoleCoordVec c N))
      = dotProduct (Matrix.vecMul (dipoleCoordVec c N) (anchoredWaveMatrix M N).transpose)
          ((anchoredWaveMatrix M N).mulVec (dipoleCoordVec c N)) := by
          rw [Matrix.vecMul_transpose]
    _ = dotProduct (dipoleCoordVec c N)
          ((anchoredWaveMatrix M N).transpose.mulVec
            ((anchoredWaveMatrix M N).mulVec (dipoleCoordVec c N))) :=
          (Matrix.dotProduct_mulVec _ _ _).symm
    _ = dotProduct (dipoleCoordVec c N)
          (((anchoredWaveMatrix M N).transpose * anchoredWaveMatrix M N).mulVec
            (dipoleCoordVec c N)) := by
          rw [Matrix.mulVec_mulVec]

/-- **Monotonicity of Wavefunction Gram Forms**: for any `1 ≤ M ≤ M'` and `1ᵀ α = 1`,
`αᵀ (Ω_{M,N}ᵀ Ω_{M,N}) α ≤ αᵀ (Ω_{M',N}ᵀ Ω_{M',N}) α`. -/
theorem anchoredWave_gram_quadForm_monotone {M M' N : ℕ} (hN : 2 ≤ N) (hM : 1 ≤ M)
    (hMM' : M ≤ M') (α : Fin (N - 2) → ℝ) (hα : dotProduct (onesVec (N - 2)) α = 1) :
    dotProduct α (((anchoredWaveMatrix M N).transpose * anchoredWaveMatrix M N).mulVec α) ≤
      dotProduct α
        (((anchoredWaveMatrix M' N).transpose * anchoredWaveMatrix M' N).mulVec α) := by
  obtain ⟨c, hc, hvec⟩ := exists_dirichletAnchored_of_simplex hN α hα
  rw [← hvec, ← harmonicCellL2PartialSum_eq_anchoredWave_gram_quadForm hN hc,
    ← harmonicCellL2PartialSum_eq_anchoredWave_gram_quadForm hN hc]
  have hsub := harmonicCellL2PartialSum_sub_eq_tailSum c N hM hMM'
  have hnn := harmonicCellL2TailSum_nonneg c N M M'
  linarith

/-- **Finite-Horizon Wavefunction Gram Domination by `M_N`**: for every `1 ≤ M`, `2 ≤ N`,
and `1ᵀ α = 1`, `αᵀ (Ω_{M,N}ᵀ Ω_{M,N}) α ≤ αᵀ M_N α`. -/
theorem anchoredWave_gram_quadForm_le_unitDefectMatrix {M N : ℕ} (hN : 2 ≤ N) (hM : 1 ≤ M)
    (α : Fin (N - 2) → ℝ) (hα : dotProduct (onesVec (N - 2)) α = 1) :
    dotProduct α (((anchoredWaveMatrix M N).transpose * anchoredWaveMatrix M N).mulVec α) ≤
      dotProduct α ((unitDefectMatrix N).mulVec α) := by
  obtain ⟨c, hc, hvec⟩ := exists_dirichletAnchored_of_simplex hN α hα
  rw [← hvec, ← harmonicCellL2PartialSum_eq_anchoredWave_gram_quadForm hN hc,
    ← one_sub_SCot_eq_unitDefectMatrix_quadForm hN hc]
  have hle := harmonicCellL2PartialSum_le_integral_Ioc c N hM hc.1
  have hint_eq : ∫ x in Set.Ioc (0 : ℝ) 1, (continuousNymanResidual c N x) ^ 2 =
      ∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2 := by
    rw [intervalIntegral.integral_of_le (by norm_num : (0 : ℝ) ≤ 1)]
    rfl
  rw [hint_eq, affine_l2_dist_eq_one_sub_scot c hc.1 hc.2.1] at hle
  exact hle

/-- **Slab-to-Continuum `M → ∞` Wavefunction Gram Limit**: for every `2 ≤ N` and
`1ᵀ α = 1`, `αᵀ (Ω_{M,N}ᵀ Ω_{M,N}) α → αᵀ M_N α` as `M → ∞`. -/
theorem anchoredWave_gram_quadForm_tendsto_unitDefectMatrix {N : ℕ} (hN : 2 ≤ N)
    (α : Fin (N - 2) → ℝ) (hα : dotProduct (onesVec (N - 2)) α = 1) :
    Filter.Tendsto
      (fun M : ℕ =>
        dotProduct α (((anchoredWaveMatrix M N).transpose * anchoredWaveMatrix M N).mulVec α))
      Filter.atTop
      (nhds (dotProduct α ((unitDefectMatrix N).mulVec α))) := by
  obtain ⟨c, hc, hvec⟩ := exists_dirichletAnchored_of_simplex hN α hα
  let S : ℕ → Set ℝ := fun n => Set.Ioc (1 / ((n : ℝ) + 2)) 1
  have hS_mono : Monotone S := by
    intro m n hmn x hx
    refine ⟨lt_of_le_of_lt ?_ hx.1, hx.2⟩
    exact one_div_le_one_div_of_le (by positivity) (by gcongr)
  have hS_union : (⋃ n : ℕ, S n) = Set.Ioc (0 : ℝ) 1 := by
    ext x
    simp only [Set.mem_iUnion, S, Set.mem_Ioc]
    constructor
    · rintro ⟨n, hn1, hn2⟩
      exact ⟨lt_trans (by positivity) hn1, hn2⟩
    · rintro ⟨hx0, hx1⟩
      obtain ⟨n, hn⟩ := exists_nat_one_div_lt hx0
      refine ⟨n, lt_of_le_of_lt ?_ hn, hx1⟩
      exact one_div_le_one_div_of_le (by positivity) (by linarith)
  have h_int : MeasureTheory.IntegrableOn
      (fun x => (continuousNymanResidual c N x) ^ 2) (⋃ n : ℕ, S n) := by
    rw [hS_union]
    exact continuousNymanResidual_sq_integrableOn_Ioc c N
  have h_tend := MeasureTheory.tendsto_setIntegral_of_monotone
    (fun n => measurableSet_Ioc) hS_mono h_int
  rw [hS_union] at h_tend
  have hint_eq : ∫ x in Set.Ioc (0 : ℝ) 1, (continuousNymanResidual c N x) ^ 2 =
      dotProduct α ((unitDefectMatrix N).mulVec α) := by
    rw [← hvec, ← one_sub_SCot_eq_unitDefectMatrix_quadForm hN hc,
      ← affine_l2_dist_eq_one_sub_scot c hc.1 hc.2.1,
      intervalIntegral.integral_of_le (by norm_num : (0 : ℝ) ≤ 1)]
    rfl
  rw [hint_eq] at h_tend
  rw [← Filter.tendsto_add_atTop_iff_nat 1]
  refine h_tend.congr fun n => ?_
  have hM : 1 ≤ n + 1 := Nat.succ_pos n
  have hS_eq : Set.Ioc (1 / ((n : ℝ) + 2)) 1 = Set.Ioc (1 / ((n + 1 : ℕ) + 1 : ℝ)) 1 := by
    push_cast; ring_nf
  rw [hS_eq, harmonicCellL2PartialSum_eq_setIntegral_Ioc c N hM hc.1,
    harmonicCellL2PartialSum_eq_anchoredWave_gram_quadForm hN hc, hvec]

/-- Half-space folded wavefunction vector on `[1, H]` for period `L = 2 * H + 2`, weighting the
left-half modular residual by `√(2 * doubleConeSymmetricWidth (2H + 2) n)`. -/
noncomputable def foldedHalfWaveVec (c : ℕ → ℝ) (N H : ℕ) : Fin H → ℝ :=
  fun i => Real.sqrt (2 * doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1)) *
    leftHalfResidual c N H i

/-- **Half-Space Wavefunction Born-Norm Isometry**: on `D1 c N = 0`, `D0 c N = 2`, and
`∀ k ∈ Icc 1 N, k ∣ 2 * H + 2`, the `H`-dimensional folded wavefunction norm squared equals the
full `2H`-cell interior energy. -/
theorem foldedHalfWaveVec_norm_sq_eq_period (c : ℕ → ℝ) (N H : ℕ) (hD1 : D1 c N = 0)
    (hD0 : D0 c N = 2) (hL : ∀ k ∈ Finset.Icc 1 N, k ∣ 2 * H + 2) :
    dotProduct (foldedHalfWaveVec c N H) (foldedHalfWaveVec c N H) =
      harmonicCellL2PartialSum c N (2 * H) := by
  rw [harmonicCellL2PartialSum_period_eq_double_halfObservation c N H hD1 hD0 hL]
  simp only [dotProduct, foldedHalfWaveVec, doubleConeHalfWeights, Matrix.mulVec_diagonal]
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  have hw := doubleConeSymmetricWidth_nonneg (2 * H + 2) (i.1 + 1)
  have hsq : Real.sqrt (2 * doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1)) *
      Real.sqrt (2 * doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1)) =
      2 * doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1) :=
    Real.mul_self_sqrt (by linarith)
  calc (Real.sqrt (2 * doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1)) *
          leftHalfResidual c N H i) *
        (Real.sqrt (2 * doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1)) *
          leftHalfResidual c N H i)
      = (Real.sqrt (2 * doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1)) *
          Real.sqrt (2 * doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1))) *
        (leftHalfResidual c N H i * leftHalfResidual c N H i) := by ring
    _ = 2 * (leftHalfResidual c N H i *
          (doubleConeSymmetricWidth (2 * H + 2) (i.1 + 1) * leftHalfResidual c N H i)) := by
        rw [hsq]; ring

/-- **Cholesky Telescoping Innovation Identity**: if `G = L * Lᵀ` with injective factor `L`,
`L *ᵥ z = b`, and `G *ᵥ α = b`, then `1 - bᵀ α = 1 - ∑ i, zᵢ²`. -/
theorem cholesky_energy_eq_one_sub_sum_sq {n : ℕ} (G L : Matrix (Fin n) (Fin n) ℝ)
    (b α z : Fin n → ℝ) (hG : G = L * L.transpose) (hLz : L.mulVec z = b)
    (hGα : G.mulVec α = b) (hL_inj : ∀ v : Fin n → ℝ, L.mulVec v = 0 → v = 0) :
    1 - dotProduct b α = 1 - ∑ i : Fin n, (z i) ^ 2 := by
  have hLt_eq : L.transpose.mulVec α = z := by
    have hdiff : L.mulVec (L.transpose.mulVec α - z) = 0 := by
      rw [Matrix.mulVec_sub, Matrix.mulVec_mulVec, ← hG, hGα, hLz, sub_self]
    exact sub_eq_zero.mp (hL_inj _ hdiff)
  have hba : dotProduct b α = ∑ i : Fin n, (z i) ^ 2 := by
    calc dotProduct b α
        = dotProduct (L.mulVec z) α := by rw [hLz]
      _ = dotProduct (Matrix.vecMul z L.transpose) α := by rw [Matrix.vecMul_transpose]
      _ = dotProduct z (L.transpose.mulVec α) := (Matrix.dotProduct_mulVec z L.transpose α).symm
      _ = dotProduct z z := by rw [hLt_eq]
      _ = ∑ i : Fin n, (z i) ^ 2 := by
          simp only [dotProduct]
          exact Finset.sum_congr rfl fun i _ => (sq (z i)).symm
  rw [hba]

/-- Symmetric bordered block extension of `G : Matrix (Fin k) (Fin k) ℝ` by vector `g` and
diagonal entry `d`, indexed on `Option (Fin k)`. -/
def borderedBlockMatrix {k : ℕ} (G : Matrix (Fin k) (Fin k) ℝ) (g : Fin k → ℝ) (d : ℝ) :
    Matrix (Option (Fin k)) (Option (Fin k)) ℝ :=
  fun r s => match r, s with
  | none, none => d
  | none, some j => g j
  | some i, none => g i
  | some i, some j => G i j

/-- **Exact Schur One-Step Innovation Identity**: bordering a symmetric system `G α = b` with
`G v = g` and Schur complement `s = d - gᵀ v ≠ 0` adds exact innovation `ρ² / s` where
`ρ = b_new - gᵀ α`. -/
theorem schur_one_step_innovation {k : ℕ} (G : Matrix (Fin k) (Fin k) ℝ)
    (hGsym : G.IsSymm) (g b α v : Fin k → ℝ) (d b_new : ℝ) (hGα : G.mulVec α = b)
    (hGv : G.mulVec v = g) (hs : d - dotProduct g v ≠ 0) :
    let s := d - dotProduct g v
    let ρ := b_new - dotProduct g α
    let b_next : Option (Fin k) → ℝ := fun r => match r with | none => b_new | some i => b i
    let α_next : Option (Fin k) → ℝ := fun r =>
      match r with | none => ρ / s | some i => α i - (ρ / s) * v i
    (borderedBlockMatrix G g d).mulVec α_next = b_next ∧
      1 - dotProduct b_next α_next = (1 - dotProduct b α) - ρ ^ 2 / s := by
  intro s ρ b_next α_next
  have hvg : dotProduct v g = dotProduct g v := dotProduct_comm v g
  have hga : dotProduct g α = dotProduct b v := by
    have hGt : G.transpose = G := hGsym
    calc dotProduct g α
        = dotProduct (G.mulVec v) α := by rw [hGv]
      _ = dotProduct (Matrix.vecMul v G.transpose) α := by rw [Matrix.vecMul_transpose]
      _ = dotProduct v (G.mulVec α) := by
          rw [hGt]; exact (Matrix.dotProduct_mulVec v G α).symm
      _ = dotProduct v b := by rw [hGα]
      _ = dotProduct b v := dotProduct_comm v b
  constructor
  · ext r
    rw [Matrix.mulVec, dotProduct, Fintype.sum_option]
    cases r with
    | none =>
      have hdot : (∑ x : Fin k, borderedBlockMatrix G g d none (some x) * α_next (some x)) =
          dotProduct g α - (ρ / s) * dotProduct g v := by
        simp only [borderedBlockMatrix, α_next, dotProduct, mul_sub, Finset.sum_sub_distrib,
          Finset.mul_sum]
        congr 1
        refine Finset.sum_congr rfl fun x _ => by ring
      rw [hdot]
      dsimp [borderedBlockMatrix, α_next, b_next]
      change d * (ρ / s) + (dotProduct g α - (ρ / s) * dotProduct g v) = b_new
      have hs_def : s = d - dotProduct g v := rfl
      have hρ_def : ρ = b_new - dotProduct g α := rfl
      calc d * (ρ / s) + (dotProduct g α - (ρ / s) * dotProduct g v)
          = (d - dotProduct g v) * (ρ / s) + dotProduct g α := by ring
        _ = s * (ρ / s) + dotProduct g α := by rw [← hs_def]
        _ = ρ + dotProduct g α := by rw [mul_div_cancel₀ _ hs]
        _ = b_new := by rw [hρ_def]; ring
    | some i =>
      have hrow_sum : (∑ x : Fin k, borderedBlockMatrix G g d (some i) (some x) *
            α_next (some x)) = (G.mulVec α) i - (ρ / s) * (G.mulVec v) i := by
        simp only [borderedBlockMatrix, α_next, Matrix.mulVec, dotProduct, mul_sub,
          Finset.sum_sub_distrib, Finset.mul_sum]
        congr 1
        refine Finset.sum_congr rfl fun x _ => by ring
      rw [hrow_sum, hGα, hGv]
      dsimp [borderedBlockMatrix, α_next, b_next]
      ring
  · rw [dotProduct, Fintype.sum_option]
    dsimp [b_next, α_next]
    have htail : (∑ x : Fin k, b x * (α x - (ρ / s) * v x)) =
        dotProduct b α - (ρ / s) * dotProduct b v := by
      simp only [dotProduct, mul_sub, Finset.sum_sub_distrib, Finset.mul_sum]
      congr 1
      refine Finset.sum_congr rfl fun x _ => by ring
    rw [htail, ← hga]
    have hρ_def : ρ = b_new - dotProduct g α := rfl
    calc 1 - (b_new * (ρ / s) + (dotProduct b α - (ρ / s) * dotProduct g α))
        = (1 - dotProduct b α) - (b_new - dotProduct g α) * (ρ / s) := by ring
      _ = (1 - dotProduct b α) - ρ * (ρ / s) := by rw [← hρ_def]
      _ = (1 - dotProduct b α) - ρ ^ 2 / s := by ring

/-- Exact one-parameter family on the dyadic octave `{1, 2, 4}` (`c 3 = 0`) parameterized by `t`,
interpolating from `cBaseAnchor` (`t = 0`) to the exact Dirichlet-anchored optimum (`t = 1`). -/
def dyadicFourVec (t : ℝ) : ℕ → ℝ
  | 1 => -2 + t
  | 2 => 4 - 3 * t
  | 4 => 2 * t
  | _ => 0

/-- For every `t : ℝ`, `dyadicFourVec t` lies on the Báez–Duarte affine manifold `A_4`. -/
theorem dyadicFourVec_mem_A_N (t : ℝ) :
    D1 (dyadicFourVec t) 4 = 0 ∧ D0 (dyadicFourVec t) 4 = 2 := by
  unfold D1 D0
  rw [sum_Icc_one_four_p6, sum_Icc_one_four_p6]
  norm_num [dyadicFourVec]
  exact ⟨by ring, by ring⟩

/-- At `t = 1`, `dyadicFourVec 1 = (-1, 1, 0, 2)` is Dirichlet-anchored on `N = 4`. -/
theorem dyadicFourVec_one_isDirichletAnchored :
    IsDirichletAnchored (dyadicFourVec 1) 4 := by
  refine ⟨(dyadicFourVec_mem_A_N 1).1, (dyadicFourVec_mem_A_N 1).2, ?_⟩
  norm_num [dyadicFourVec]

/-- **Exact Dyadic `{1, 2, 4}` Variational Energy Formula**: for every `c ∈ A_4` supported on
`{1, 2, 4}` (`c 3 = 0`), `1 - SCot vasyuninGCot c 4 = (1 - π / 4) + (π / 4) * (c 1 + 1)²`. -/
theorem one_sub_SCot_dyadicFour_eq {c : ℕ → ℝ} (hD1 : D1 c 4 = 0) (hD0 : D0 c 4 = 2)
    (hc3 : c 3 = 0) :
    1 - SCot vasyuninGCot c 4 = (1 - Real.pi / 4) + (Real.pi / 4) * (c 1 + 1) ^ 2 := by
  have hd1' := hD1
  have hd0' := hD0
  unfold D1 at hd1'
  unfold D0 at hd0'
  rw [sum_Icc_one_four_p6, hc3] at hd1' hd0'
  have hc4 : c 4 = 2 * c 1 + 4 := by linarith
  have hV1 : ∀ b : ℕ, vasyuninCotSum 1 b = 0 := fun _ => by simp [vasyuninCotSum]
  have hG12 : vasyuninGCot 1 2 = 0 := by
    unfold vasyuninGCot; rw [hV1, vasyuninCotSum_two_p6]; ring
  have hG14 : vasyuninGCot 1 4 = Real.pi / 16 := by
    unfold vasyuninGCot; rw [hV1, vasyuninCotSum_four_p6]; norm_num; ring
  have hG24 : vasyuninGCot 2 4 = 0 := by
    unfold vasyuninGCot; rw [vasyuninCotSum_two_p6, vasyuninCotSum_four_p6]; norm_num
  have hq : QCot vasyuninGCot c 4 = c 1 * c 4 * (Real.pi / 8) := by
    unfold QCot
    simp_rw [sum_Icc_one_four_p6]
    rw [vasyuninGCot_diag 1, vasyuninGCot_diag 2, vasyuninGCot_diag 3, vasyuninGCot_diag 4,
      vasyuninGCot_comm 2 1, vasyuninGCot_comm 3 1, vasyuninGCot_comm 4 1,
      vasyuninGCot_comm 3 2, vasyuninGCot_comm 4 2, vasyuninGCot_comm 4 3,
      hG12, hG14, hG24, hc3]
    ring
  unfold SCot
  rw [hq, hc4]
  ring

/-- **Dyadic `{1, 2, 4}` Energy Lower Bound**: every vector on `A_4` supported on `{1, 2, 4}`
has energy at least `1 - π / 4`. -/
theorem one_sub_SCot_dyadicFour_ge {c : ℕ → ℝ} (hD1 : D1 c 4 = 0) (hD0 : D0 c 4 = 2)
    (hc3 : c 3 = 0) :
    1 - Real.pi / 4 ≤ 1 - SCot vasyuninGCot c 4 := by
  rw [one_sub_SCot_dyadicFour_eq hD1 hD0 hc3]
  have hsq : 0 ≤ (Real.pi / 4) * (c 1 + 1) ^ 2 :=
    mul_nonneg (div_nonneg Real.pi_pos.le (by norm_num)) (sq_nonneg _)
  linarith

/-- **Exact First-Octave `{1, 2, 4}` Optimum**: `dyadicFourVec 1 = (-1, 1, 0, 2)` achieves
`1 - SCot vasyuninGCot (dyadicFourVec 1) 4 = 1 - π / 4`. -/
theorem one_sub_SCot_dyadicFour_opt_eq :
    1 - SCot vasyuninGCot (dyadicFourVec 1) 4 = 1 - Real.pi / 4 := by
  rw [one_sub_SCot_dyadicFour_eq (dyadicFourVec_mem_A_N 1).1 (dyadicFourVec_mem_A_N 1).2
    (by simp [dyadicFourVec])]
  norm_num [dyadicFourVec]

/-- **Unit-Eigenvector Simplex Upper Bound**: any unit eigenvector `v` of `unitDefectMatrix N`
with eigenvalue `lam` and nonzero sum `1ᵀ v` normalizes onto the Dirichlet simplex with exact
energy `lam / (1ᵀ v)²`. -/
theorem unitDefectMatrix_eigenvector_simplex_energy {N : ℕ} (lam : ℝ) (v : Fin (N - 2) → ℝ)
    (heig : (unitDefectMatrix N).mulVec v = lam • v) (hunit : dotProduct v v = 1)
    (hsum : dotProduct (onesVec (N - 2)) v ≠ 0) :
    let α : Fin (N - 2) → ℝ := (1 / dotProduct (onesVec (N - 2)) v) • v
    dotProduct (onesVec (N - 2)) α = 1 ∧
      dotProduct α ((unitDefectMatrix N).mulVec α) =
        lam / (dotProduct (onesVec (N - 2)) v) ^ 2 := by
  intro α
  constructor
  · dsimp [α]
    rw [dotProduct_smul, smul_eq_mul, one_div_mul_cancel hsum]
  · dsimp [α]
    rw [Matrix.mulVec_smul, dotProduct_smul, smul_dotProduct, heig, dotProduct_smul, smul_eq_mul,
      smul_eq_mul, smul_eq_mul, hunit]
    field_simp [hsum]

/-- **Eigenvalue Nonnegativity for Overlap-Active Modes**: for `N ≥ 2`, any unit eigenvector `v`
of `unitDefectMatrix N` with `1ᵀ v ≠ 0` satisfies `0 ≤ lam`. -/
theorem unitDefectMatrix_eigenvalue_nonneg {N : ℕ} (hN : 2 ≤ N) (lam : ℝ) (v : Fin (N - 2) → ℝ)
    (heig : (unitDefectMatrix N).mulVec v = lam • v) (hunit : dotProduct v v = 1)
    (hsum : dotProduct (onesVec (N - 2)) v ≠ 0) :
    0 ≤ lam := by
  have h := unitDefectMatrix_eigenvector_simplex_energy lam v heig hunit hsum
  have hnn := unitDefectMatrix_quadForm_nonneg_of_simplex hN _ h.1
  rw [h.2] at hnn
  have hden : 0 < (dotProduct (onesVec (N - 2)) v) ^ 2 := sq_pos_of_ne_zero hsum
  exact nonneg_of_mul_nonneg_left (by simpa [div_eq_mul_inv] using hnn) (inv_pos.mpr hden)

/-- **Ground-State Spectral RH Criterion**: `_root_.RiemannHypothesis` follows if the lowest
overlap-active eigenvector ratio `lam / (1ᵀ v)²` of `unitDefectMatrix N` approaches `0`. -/
theorem riemannHypothesis_of_unitDefectMatrix_groundState_vanishing_unconditional
    (h_gs : ∀ ε : ℝ, 0 < ε → ∃ (N : ℕ) (lam : ℝ) (v : Fin (N - 2) → ℝ),
      2 ≤ N ∧ (unitDefectMatrix N).mulVec v = lam • v ∧ dotProduct v v = 1 ∧
        dotProduct (onesVec (N - 2)) v ≠ 0 ∧
        lam / (dotProduct (onesVec (N - 2)) v) ^ 2 < ε) :
    _root_.RiemannHypothesis := by
  refine riemannHypothesis_of_unitDefectMatrix_vanishing_unconditional fun ε hε => ?_
  obtain ⟨N, lam, v, hN, heig, hunit, hsum, hlt⟩ := h_gs ε hε
  have h := unitDefectMatrix_eigenvector_simplex_energy lam v heig hunit hsum
  exact ⟨N, (1 / dotProduct (onesVec (N - 2)) v) • v, hN, h.1, h.2.symm ▸ hlt⟩

/-- **Wavefunction Gram Quadratic Form Identity**: for any `α : Fin (N - 2) → ℝ`,
`αᵀ (Ω_{M,N}ᵀ Ω_{M,N}) α = ‖Ω_{M,N} α‖₂²`. -/
theorem anchoredWave_gram_quadForm_eq_norm_sq {M N : ℕ} (α : Fin (N - 2) → ℝ) :
    dotProduct α (((anchoredWaveMatrix M N).transpose * anchoredWaveMatrix M N).mulVec α) =
      dotProduct ((anchoredWaveMatrix M N).mulVec α) ((anchoredWaveMatrix M N).mulVec α) := by
  rw [← Matrix.mulVec_mulVec, Matrix.dotProduct_mulVec, Matrix.vecMul_transpose]

/-- **Wavefunction Gram Nonnegativity**: `0 ≤ αᵀ (Ω_{M,N}ᵀ Ω_{M,N}) α` for all `α`. -/
theorem anchoredWave_gram_quadForm_nonneg {M N : ℕ} (α : Fin (N - 2) → ℝ) :
    0 ≤ dotProduct α (((anchoredWaveMatrix M N).transpose * anchoredWaveMatrix M N).mulVec α) := by
  rw [anchoredWave_gram_quadForm_eq_norm_sq]
  exact Finset.sum_nonneg fun i _ => mul_self_nonneg _

/-- **Variational Inverse-Quadratic Identity**: for any symmetric matrix `M` with `M w = 1` and
`1ᵀ w ≠ 0`, every simplex weight `1ᵀ α = 1` decomposes orthogonally around `α* = w / (1ᵀ w)` as
`αᵀ M α = 1 / (1ᵀ w) + (α - α*)ᵀ M (α - α*)`. -/
theorem variational_inverse_quadForm_identity {n : ℕ} (M : Matrix (Fin n) (Fin n) ℝ)
    (hMsym : M.IsSymm) (w α : Fin n → ℝ) (hMw : M.mulVec w = onesVec n)
    (hsum : dotProduct (onesVec n) w ≠ 0) (hα : dotProduct (onesVec n) α = 1) :
    let αStar : Fin n → ℝ := (1 / dotProduct (onesVec n) w) • w
    dotProduct α (M.mulVec α) =
      1 / dotProduct (onesVec n) w + dotProduct (α - αStar) (M.mulVec (α - αStar)) := by
  intro αStar
  have hM_αStar : M.mulVec αStar = (1 / dotProduct (onesVec n) w) • onesVec n := by
    dsimp [αStar]
    rw [Matrix.mulVec_smul, hMw]
  have h_α_αStar : dotProduct α (M.mulVec αStar) = 1 / dotProduct (onesVec n) w := by
    rw [hM_αStar, dotProduct_smul, smul_eq_mul, dotProduct_comm α (onesVec n), hα, mul_one]
  have h_αStar_α : dotProduct αStar (M.mulVec α) = 1 / dotProduct (onesVec n) w := by
    have hsym_dot : dotProduct αStar (M.mulVec α) = dotProduct α (M.mulVec αStar) := by
      simp only [dotProduct, Matrix.mulVec, Finset.mul_sum]
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun j _ => ?_
      rw [hMsym.apply i j]
      ring
    rw [hsym_dot, h_α_αStar]
  have h_αStar_αStar : dotProduct αStar (M.mulVec αStar) = 1 / dotProduct (onesVec n) w := by
    rw [hM_αStar]
    dsimp [αStar]
    rw [dotProduct_smul, smul_dotProduct, smul_eq_mul, smul_eq_mul, dotProduct_comm w (onesVec n)]
    field_simp [hsum]
  have h_expand : dotProduct (α - αStar) (M.mulVec (α - αStar)) =
      dotProduct α (M.mulVec α) - dotProduct α (M.mulVec αStar) -
        dotProduct αStar (M.mulVec α) + dotProduct αStar (M.mulVec αStar) := by
    rw [Matrix.mulVec_sub, dotProduct_sub, sub_dotProduct, sub_dotProduct]
    ring
  rw [h_α_αStar, h_αStar_α, h_αStar_αStar] at h_expand
  linarith

/-- **Variational Inverse-Quadratic Lower Bound**: if `M` is additionally positive semidefinite,
then `1 / (1ᵀ w) ≤ αᵀ M α` for every simplex weight `1ᵀ α = 1`. -/
theorem variational_inverse_quadForm_ge {n : ℕ} (M : Matrix (Fin n) (Fin n) ℝ)
    (hMsym : M.IsSymm) (hM_psd : ∀ x : Fin n → ℝ, 0 ≤ dotProduct x (M.mulVec x))
    (w α : Fin n → ℝ) (hMw : M.mulVec w = onesVec n)
    (hsum : dotProduct (onesVec n) w ≠ 0) (hα : dotProduct (onesVec n) α = 1) :
    1 / dotProduct (onesVec n) w ≤ dotProduct α (M.mulVec α) := by
  have h := variational_inverse_quadForm_identity M hMsym w α hMw hsum hα
  dsimp at h
  have hnn := hM_psd (α - (1 / dotProduct (onesVec n) w) • w)
  linarith

/-- **Orthogonal Gram–Schmidt Innovation Telescoping Identity**: for any unit-norm vacuum
vector `b` (`‖b‖₂² = 1`) and orthogonal innovation sequence `{φ_k}_{k=3}^N` with couplings
`ρ_k = ⟨b, φ_k⟩` and nonzero norms `s_k = ⟨φ_k, φ_k⟩`, the residual energy equals
`1 - ∑_{k=3}^N ρ_k² / s_k`. -/
theorem orthogonal_innovation_telescoping_energy {n : ℕ} (b : Fin n → ℝ)
    (hb : dotProduct b b = 1) (φ : ℕ → (Fin n → ℝ))
    (hφ_orth : ∀ i j, i ≠ j → dotProduct (φ i) (φ j) = 0)
    (ρ s : ℕ → ℝ) (hρ : ∀ k, ρ k = dotProduct b (φ k)) (hs : ∀ k, s k = dotProduct (φ k) (φ k))
    (N : ℕ) (hs_ne : ∀ k ∈ Finset.Icc 3 N, s k ≠ 0) :
    let resid : Fin n → ℝ := b - ∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k
    dotProduct resid resid = 1 - ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k := by
  intro resid
  have h_cross : dotProduct b (∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k) =
      ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k := by
    rw [dotProduct_sum]
    refine Finset.sum_congr rfl fun k hk => ?_
    rw [dotProduct_smul, smul_eq_mul, ← hρ k]
    ring
  have h_self : dotProduct (∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k)
      (∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k) =
      ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k := by
    rw [dotProduct_sum]
    refine Finset.sum_congr rfl fun k hk => ?_
    rw [sum_dotProduct]
    have hsingle : ∑ j ∈ Finset.Icc 3 N,
        dotProduct ((ρ j / s j) • φ j) ((ρ k / s k) • φ k) =
        dotProduct ((ρ k / s k) • φ k) ((ρ k / s k) • φ k) := by
      refine Finset.sum_eq_single k (fun j _ hjk => ?_) (fun hk_abs => absurd hk hk_abs)
      rw [smul_dotProduct, dotProduct_smul, hφ_orth j k hjk]
      simp
    rw [hsingle, smul_dotProduct, dotProduct_smul, smul_eq_mul, smul_eq_mul, ← hs k]
    have hsk := hs_ne k hk
    field_simp [hsk]
  have h_expand : dotProduct resid resid =
      dotProduct b b - 2 * dotProduct b (∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k) +
        dotProduct (∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k)
          (∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k) := by
    dsimp [resid]
    rw [dotProduct_sub, sub_dotProduct, sub_dotProduct, dotProduct_comm (∑ k ∈ Finset.Icc 3 N, _) b]
    ring
  rw [h_expand, hb, h_cross, h_self]
  ring

/-- **Bessel's Inequality for Orthogonal Innovations**: `∑_{k=3}^N ρ_k² / s_k ≤ 1`. -/
theorem orthogonal_innovation_bessel_le_one {n : ℕ} (b : Fin n → ℝ)
    (hb : dotProduct b b = 1) (φ : ℕ → (Fin n → ℝ))
    (hφ_orth : ∀ i j, i ≠ j → dotProduct (φ i) (φ j) = 0)
    (ρ s : ℕ → ℝ) (hρ : ∀ k, ρ k = dotProduct b (φ k)) (hs : ∀ k, s k = dotProduct (φ k) (φ k))
    (N : ℕ) (hs_ne : ∀ k ∈ Finset.Icc 3 N, s k ≠ 0) :
    ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k ≤ 1 := by
  have h := orthogonal_innovation_telescoping_energy b hb φ hφ_orth ρ s hρ hs N hs_ne
  dsimp at h
  have hnn : 0 ≤ dotProduct (b - ∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k)
      (b - ∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k) :=
    Finset.sum_nonneg fun i _ => mul_self_nonneg _
  linarith

/-- **Unconditional Monotonicity of `E_free(N)`**: `E_free(N + 1) ≤ E_free(N)` for `N ≥ 2`. -/
theorem orthogonal_innovation_energy_monotone (ρ s : ℕ → ℝ) (N : ℕ) (hN : 2 ≤ N)
    (hs_pos : 0 < s (N + 1)) :
    1 - ∑ k ∈ Finset.Icc 3 (N + 1), ρ k ^ 2 / s k ≤
      1 - ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k := by
  have hIcc : Finset.Icc 3 (N + 1) = insert (N + 1) (Finset.Icc 3 N) := by
    ext k
    simp only [Finset.mem_Icc, Finset.mem_insert]
    omega
  rw [hIcc, Finset.sum_insert (by simp)]
  have hterm : 0 ≤ ρ (N + 1) ^ 2 / s (N + 1) := div_nonneg (sq_nonneg _) hs_pos.le
  linarith

/-- **Right Möbius Inversion of Divisibility**: `D_M * M_μ = I_M`. -/
theorem divisorMatrix_mul_mobiusMatrix (M : ℕ) :
    divisorMatrix M M * mobiusMatrix M = 1 := by
  ext i j
  rw [Matrix.mul_apply, Matrix.one_apply]
  by_cases hdvd : j.1 + 1 ∣ i.1 + 1
  · rcases hdvd with ⟨q, hq_eq⟩
    have hj_pos : 1 ≤ j.1 + 1 := Nat.succ_pos _
    have hq_pos : 1 ≤ q := by
      rcases Nat.eq_zero_or_pos q with rfl | hqp
      · simp at hq_eq
      · exact hqp
    have hsum_eq : (∑ m : Fin M, divisorMatrix M M i m * mobiusMatrix M m j) =
        ∑ d ∈ q.divisors, (ArithmeticFunction.moebius (q / d) : ℝ) := by
      have hterm : ∀ m : Fin M, divisorMatrix M M i m * mobiusMatrix M m j =
          if m.1 + 1 ∣ i.1 + 1 ∧ j.1 + 1 ∣ m.1 + 1 then
            (ArithmeticFunction.moebius ((m.1 + 1) / (j.1 + 1)) : ℝ) else 0 := by
        intro m
        dsimp [divisorMatrix, mobiusMatrix]
        by_cases h1 : m.1 + 1 ∣ i.1 + 1 <;> by_cases h2 : j.1 + 1 ∣ m.1 + 1 <;> simp [h1, h2]
      rw [Finset.sum_congr rfl fun m _ => hterm m, ← Finset.sum_filter]
      refine Finset.sum_bij (fun m _ => (i.1 + 1) / (m.1 + 1)) ?_ ?_ ?_ ?_
      · intro m hm
        rcases Finset.mem_filter.mp hm with ⟨_, hmi, hjm⟩
        rcases hjm with ⟨d, hd⟩
        rcases hmi with ⟨t, ht⟩
        have hm_pos : 1 ≤ m.1 + 1 := Nat.succ_pos _
        have hqt : (i.1 + 1) / (m.1 + 1) = t := by rw [ht, Nat.mul_div_cancel_left _ hm_pos]
        rw [hqt]
        refine Nat.mem_divisors.mpr ⟨?_, by omega⟩
        refine ⟨d, ?_⟩
        have : (j.1 + 1) * q = (j.1 + 1) * (t * d) := by
          calc (j.1 + 1) * q = i.1 + 1 := hq_eq.symm
            _ = (m.1 + 1) * t := ht
            _ = (j.1 + 1) * d * t := by rw [hd]
            _ = (j.1 + 1) * (t * d) := by ring
        exact Nat.mul_left_cancel hj_pos this
      · intro m₁ hm₁ m₂ hm₂ h
        have h1 := (Finset.mem_filter.mp hm₁).2.1
        have h2 := (Finset.mem_filter.mp hm₂).2.1
        rcases h1 with ⟨t₁, ht₁⟩
        rcases h2 with ⟨t₂, ht₂⟩
        have ht1_eq : (i.1 + 1) / (m₁.1 + 1) = t₁ := by rw [ht₁, Nat.mul_div_cancel_left _ (Nat.succ_pos _)]
        have ht2_eq : (i.1 + 1) / (m₂.1 + 1) = t₂ := by rw [ht₂, Nat.mul_div_cancel_left _ (Nat.succ_pos _)]
        have ht_eq : t₁ = t₂ := by rw [← ht1_eq, ← ht2_eq, h]
        have ht_pos : 0 < t₁ := by
          rcases Nat.eq_zero_or_pos t₁ with rfl | htp
          · simp at ht₁
          · exact htp
        have hm_eq : m₁.1 + 1 = m₂.1 + 1 :=
          Nat.mul_right_cancel ht_pos (ht₁.symm.trans (by rw [ht_eq]; exact ht₂))
        exact Fin.ext (by omega)
      · intro t ht
        have ht_dvd : t ∣ q := Nat.dvd_of_mem_divisors ht
        rcases ht_dvd with ⟨d, hd_eq⟩
        have ht_pos : 1 ≤ t := Nat.pos_of_mem_divisors ht
        have hd_pos : 1 ≤ d := by
          rcases Nat.eq_zero_or_pos d with rfl | hdp
          · simp at hd_eq; omega
          · exact hdp
        have hm_pos : 1 ≤ (j.1 + 1) * d := Nat.mul_pos hj_pos hd_pos
        have hm_le : (j.1 + 1) * d ≤ M := by
          have : (j.1 + 1) * d ≤ (j.1 + 1) * (d * t) :=
            Nat.mul_le_mul_left _ (Nat.le_mul_of_pos_right d ht_pos)
          rw [mul_comm d t, ← hd_eq, ← hq_eq] at this
          exact this.trans i.isLt
        refine ⟨⟨(j.1 + 1) * d - 1, by omega⟩, Finset.mem_filter.mpr ⟨Finset.mem_univ _, ?_, ?_⟩, ?_⟩
        · dsimp
          rw [show (j.1 + 1) * d - 1 + 1 = (j.1 + 1) * d by omega]
          exact ⟨t, by rw [hq_eq, hd_eq]; ring⟩
        · dsimp
          rw [show (j.1 + 1) * d - 1 + 1 = (j.1 + 1) * d by omega]
          exact ⟨d, rfl⟩
        · dsimp
          rw [show (j.1 + 1) * d - 1 + 1 = (j.1 + 1) * d by omega,
            show i.1 + 1 = (j.1 + 1) * d * t by rw [hq_eq, hd_eq]; ring,
            Nat.mul_div_cancel_left _ hm_pos]
      · intro m hm
        rcases Finset.mem_filter.mp hm with ⟨_, hmi, hjm⟩
        rcases hmi with ⟨t, ht⟩
        rcases hjm with ⟨d, hd⟩
        have hm_pos : 1 ≤ m.1 + 1 := Nat.succ_pos _
        have hqt : (i.1 + 1) / (m.1 + 1) = t := by rw [ht, Nat.mul_div_cancel_left _ hm_pos]
        have hmd : (m.1 + 1) / (j.1 + 1) = d := by rw [hd, Nat.mul_div_cancel_left _ hj_pos]
        have hq_dt : q = t * d := by
          have : (j.1 + 1) * q = (j.1 + 1) * (t * d) := by
            calc (j.1 + 1) * q = i.1 + 1 := hq_eq.symm
              _ = (m.1 + 1) * t := ht
              _ = (j.1 + 1) * d * t := by rw [hd]
              _ = (j.1 + 1) * (t * d) := by ring
          exact Nat.mul_left_cancel hj_pos this
        have ht_pos : 0 < t := by
          rcases Nat.eq_zero_or_pos t with rfl | htp
          · simp at ht
          · exact htp
        have hq_div : q / t = d := by rw [hq_dt, Nat.mul_div_cancel_left _ ht_pos]
        rw [hqt, hmd, hq_div]
    rw [hsum_eq, sum_moebius_div_divisors q hq_pos]
    by_cases hq1 : q = 1
    · have hij : i = j := Fin.ext (by
        have h1 : i.1 + 1 = j.1 + 1 := by rw [hq_eq, hq1, mul_one]
        omega)
      simp [hq1, hij]
    · have hij : i ≠ j := fun h => hq1 (by
        have h1 : (j.1 + 1) * q = (j.1 + 1) * 1 := by rw [← hq_eq, h, mul_one]
        exact Nat.mul_left_cancel hj_pos h1)
      simp [hq1, hij]
  · have hsum_zero : (∑ m : Fin M, divisorMatrix M M i m * mobiusMatrix M m j) = 0 := by
      refine Finset.sum_eq_zero fun m _ => ?_
      dsimp [divisorMatrix, mobiusMatrix]
      by_cases h1 : m.1 + 1 ∣ i.1 + 1 <;> by_cases h2 : j.1 + 1 ∣ m.1 + 1
      · exact absurd (h2.trans h1) hdvd
      · simp [h1, h2]
      · simp [h1, h2]
      · simp [h1, h2]
    have hij : i ≠ j := fun h => hdvd (by subst h; exact dvd_refl _)
    simp [hsum_zero, hij]

/-- **Right Inversion of Summation**: `Σ_M * Δ_M = I_M`. -/
theorem cumSumMatrix_mul_firstDiffMatrix (M : ℕ) :
    cumSumMatrix M * firstDiffMatrix M = 1 := by
  ext i j
  rw [Matrix.mul_apply, Matrix.one_apply]
  have hterm : ∀ m : Fin M, cumSumMatrix M i m * firstDiffMatrix M m j =
      (if m = j then (if j.1 ≤ i.1 then (1 : ℝ) else 0) else 0) +
        (if m.1 = j.1 + 1 then (if j.1 + 1 ≤ i.1 then (-1 : ℝ) else 0) else 0) := by
    intro m
    dsimp [cumSumMatrix, firstDiffMatrix]
    by_cases hmj : m = j
    · subst hmj
      by_cases hle : m.1 ≤ i.1 <;> simp [hle]
    · by_cases hms : m.1 = j.1 + 1
      · have hne' : m ≠ j := hmj
        by_cases hle : m.1 ≤ i.1 <;> simp [hms, hne'] <;> split_ifs <;> ring
      · have hne1 : m.1 ≠ j.1 := fun h => hmj (Fin.ext h)
        simp [hne1, hms, hmj]
  rw [Finset.sum_congr rfl fun m _ => hterm m, Finset.sum_add_distrib, Finset.sum_ite_eq']
  simp only [Finset.mem_univ, ↓reduceIte]
  by_cases hj1 : j.1 + 1 < M
  · set q : Fin M := ⟨j.1 + 1, hj1⟩
    have hq_eq : (∑ m : Fin M, if m.1 = j.1 + 1 then
        (if j.1 + 1 ≤ i.1 then (-1 : ℝ) else 0) else 0) =
        if j.1 + 1 ≤ i.1 then (-1 : ℝ) else 0 := by
      have : (∑ m : Fin M, if m.1 = j.1 + 1 then
          (if j.1 + 1 ≤ i.1 then (-1 : ℝ) else 0) else 0) =
          ∑ m : Fin M, if m = q then (if j.1 + 1 ≤ i.1 then (-1 : ℝ) else 0) else 0 := by
        refine Finset.sum_congr rfl fun m _ => ?_
        by_cases hmq : m = q
        · subst hmq; simp [q]
        · have hne : m.1 ≠ j.1 + 1 := fun h => hmq (Fin.ext h)
          simp [hmq, hne]
      rw [this, Finset.sum_ite_eq']
      simp
    rw [hq_eq]
    by_cases hij : i = j
    · subst hij; simp
    · by_cases hle : j.1 ≤ i.1
      · have hle1 : j.1 + 1 ≤ i.1 := by
          have : j.1 ≠ i.1 := fun h => hij (Fin.ext h.symm)
          omega
        simp [hij, hle, hle1]
      · have hnot : ¬ j.1 + 1 ≤ i.1 := by omega
        simp [hij, hle, hnot]
  · have hzero : (∑ m : Fin M, if m.1 = j.1 + 1 then
        (if j.1 + 1 ≤ i.1 then (-1 : ℝ) else 0) else 0) = 0 :=
      Finset.sum_eq_zero fun m _ => by
        have hm : m.1 ≠ j.1 + 1 := by omega
        simp [hm]
    rw [hzero, add_zero]
    by_cases hij : i = j
    · subst hij; simp
    · have hj_not : ¬ j.1 ≤ i.1 := by
        have : j.1 = M - 1 := by omega
        have : i.1 ≤ M - 1 := by omega
        intro hle
        exact hij (Fin.ext (by omega))
      simp [hij, hj_not]

/-- **Right Inversion of the Floor Matrix**: `F_M * (M_μ * Δ_M) = I_M`. -/
theorem floorMatrix_mul_inverse (M : ℕ) :
    floorMatrix M M * (mobiusMatrix M * firstDiffMatrix M) = 1 := by
  calc floorMatrix M M * (mobiusMatrix M * firstDiffMatrix M)
      = (cumSumMatrix M * divisorMatrix M M) * (mobiusMatrix M * firstDiffMatrix M) := by
          rw [floorMatrix_eq_cumSum_mul_divisor]
    _ = cumSumMatrix M * ((divisorMatrix M M * mobiusMatrix M) * firstDiffMatrix M) := by
          simp only [Matrix.mul_assoc]
    _ = cumSumMatrix M * firstDiffMatrix M := by
          rw [divisorMatrix_mul_mobiusMatrix, Matrix.one_mul]
    _ = 1 := cumSumMatrix_mul_firstDiffMatrix M

/-- **Forward Gaussian Elimination to `e_1`**: `D_M * μ = (1, 0, ..., 0)ᵀ`. -/
theorem divisorMatrix_mulVec_mobius_eq_e1 (M : ℕ) (i : Fin M) :
    (divisorMatrix M M).mulVec (fun j : Fin M => (ArithmeticFunction.moebius (j.1 + 1) : ℝ)) i =
      if i.1 = 0 then 1 else 0 := by
  have hcol0 : ∀ m : Fin M,
      mobiusMatrix M m ⟨0, i.pos⟩ = (ArithmeticFunction.moebius (m.1 + 1) : ℝ) := by
    intro m
    dsimp [mobiusMatrix]
    simp
  have hmul := congrArg (fun A : Matrix (Fin M) (Fin M) ℝ => A i ⟨0, i.pos⟩)
    (divisorMatrix_mul_mobiusMatrix M)
  rw [Matrix.mul_apply, Matrix.one_apply] at hmul
  have hlhs : (divisorMatrix M M).mulVec
      (fun j : Fin M => (ArithmeticFunction.moebius (j.1 + 1) : ℝ)) i =
      ∑ m : Fin M, divisorMatrix M M i m * mobiusMatrix M m ⟨0, i.pos⟩ := by
    rw [Matrix.mulVec, dotProduct]
    refine Finset.sum_congr rfl fun m _ => by rw [hcol0 m]
  rw [hlhs, hmul]
  by_cases hi0 : i.1 = 0
  · have hi_eq : i = ⟨0, i.pos⟩ := Fin.ext hi0
    simp [hi_eq]
  · have hi_ne : i ≠ ⟨0, i.pos⟩ := fun h => hi0 (congrArg Fin.val h)
    simp [hi0, hi_ne]

/-- **Pivot-Row Identity Matching**: row `n = 1` of `F_{M,N}` equals `(1, 0, ..., 0)`. -/
theorem floorMatrix_firstRow_eq_e1 {M N : ℕ} (hM : 1 ≤ M) (j : Fin N) :
    floorMatrix M N ⟨0, hM⟩ j = if j.1 = 0 then 1 else 0 := by
  dsimp [floorMatrix]
  by_cases hj0 : j.1 = 0
  · simp [hj0]
  · have hlt : (1 : ℕ) < j.1 + 1 := by omega
    simp [hj0, Nat.div_eq_of_lt hlt]

/-- **Pivot-Row Elimination Under Dirichlet Anchoring**: locking `c 1 = -1` forces
`1 + (F_{M,N} c)_1 = 0`. -/
theorem pivot_row_elimination_upperHalf_zero {M N : ℕ} (hM : 1 ≤ M) (hN : 1 ≤ N)
    {c : ℕ → ℝ} (hc1 : c 1 = -1) :
    1 + (floorMatrix M N).mulVec (coeffVec c N) ⟨0, hM⟩ = 0 := by
  rw [Matrix.mulVec, dotProduct]
  have hrow : ∑ j : Fin N, floorMatrix M N ⟨0, hM⟩ j * coeffVec c N j = coeffVec c N ⟨0, hN⟩ := by
    have hterm : ∀ j : Fin N, floorMatrix M N ⟨0, hM⟩ j * coeffVec c N j =
        if j = ⟨0, hN⟩ then coeffVec c N ⟨0, hN⟩ else 0 := by
      intro j
      rw [floorMatrix_firstRow_eq_e1 hM j]
      by_cases hj0 : j.1 = 0
      · have hj : j = ⟨0, hN⟩ := Fin.ext hj0
        simp [hj]
      · have hj : j ≠ ⟨0, hN⟩ := fun h => hj0 (congrArg Fin.val h)
        simp [hj0, hj]
    rw [Finset.sum_congr rfl fun j _ => hterm j, Finset.sum_ite_eq']
    simp
  rw [hrow]
  dsimp [coeffVec]
  linarith

/-- **Cholesky Whitening to the Identity Matrix `I`**: if `Ψᵀ Ψ = L Lᵀ` and `W L = 1`, then
`Ψ_tilde := Ψ Wᵀ` satisfies `Ψ_tildeᵀ Ψ_tilde = 1`. -/
theorem choleskyWhitening_gram_eq_one {M k : ℕ} (Ψ : Matrix (Fin M) (Fin k) ℝ)
    (L W : Matrix (Fin k) (Fin k) ℝ) (hG : Ψ.transpose * Ψ = L * L.transpose)
    (hW : W * L = 1) :
    (Ψ * W.transpose).transpose * (Ψ * W.transpose) = 1 := by
  calc (Ψ * W.transpose).transpose * (Ψ * W.transpose)
      = (W * Ψ.transpose) * (Ψ * W.transpose) := by
          rw [Matrix.transpose_mul, Matrix.transpose_transpose]
    _ = W * (Ψ.transpose * Ψ) * W.transpose := by
          simp only [Matrix.mul_assoc]
    _ = W * (L * L.transpose) * W.transpose := by rw [hG]
    _ = (W * L) * (W * L).transpose := by
          rw [Matrix.transpose_mul]
          simp only [Matrix.mul_assoc]
    _ = 1 * (1 : Matrix (Fin k) (Fin k) ℝ).transpose := by rw [hW]
    _ = 1 := by simp

/-- **Identity-Minus-Projection Operator Residual**: for orthogonal basis vectors `{φ_k}_{k=3}^N`
with norms `s_k = ⟨φ_k, φ_k⟩ ≠ 0`, the rank-`(N-2)` projector
`Π_N := ∑_{k=3}^N (1 / s_k) |φ_k⟩⟨φ_k|` satisfies
`‖(I - Π_N) b‖₂² = ⟨b, (I - Π_N) b⟩ = 1 - ∑_{k=3}^N ρ_k² / s_k ≥ 0` when `‖b‖₂² = 1`. -/
theorem identity_sub_proj_residual_eq {n : ℕ} (b : Fin n → ℝ) (hb : dotProduct b b = 1)
    (φ : ℕ → (Fin n → ℝ)) (hφ_orth : ∀ i j, i ≠ j → dotProduct (φ i) (φ j) = 0)
    (ρ s : ℕ → ℝ) (hρ : ∀ k, ρ k = dotProduct b (φ k)) (hs : ∀ k, s k = dotProduct (φ k) (φ k))
    (N : ℕ) (hs_ne : ∀ k ∈ Finset.Icc 3 N, s k ≠ 0) :
    let Pi_hat : Matrix (Fin n) (Fin n) ℝ :=
      ∑ k ∈ Finset.Icc 3 N, (1 / s k) • Matrix.vecMulVec (φ k) (φ k)
    let r : Fin n → ℝ := (1 - Pi_hat).mulVec b
    r = b - ∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k ∧
      dotProduct r r = dotProduct b r ∧
      dotProduct b r = 1 - ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k := by
  intro Pi_hat r
  have hPi_mul : Pi_hat.mulVec b = ∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k := by
    dsimp [Pi_hat]
    rw [Matrix.sum_mulVec]
    refine Finset.sum_congr rfl fun k _ => ?_
    rw [Matrix.smul_mulVec, Matrix.vecMulVec_mulVec, dotProduct_comm (φ k) b, ← hρ k,
      op_smul_eq_smul, smul_smul]
    ring_nf
  have hr_eq : r = b - ∑ k ∈ Finset.Icc 3 N, (ρ k / s k) • φ k := by
    dsimp [r]
    rw [Matrix.sub_mulVec, Matrix.one_mulVec, hPi_mul]
  have hr_norm : dotProduct r r = 1 - ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k := by
    rw [hr_eq]
    exact orthogonal_innovation_telescoping_energy b hb φ hφ_orth ρ s hρ hs N hs_ne
  have hb_dot : dotProduct b r = 1 - ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k := by
    rw [hr_eq, dotProduct_sub, hb, dotProduct_sum]
    have hcross : ∑ k ∈ Finset.Icc 3 N, dotProduct b ((ρ k / s k) • φ k) =
        ∑ k ∈ Finset.Icc 3 N, ρ k ^ 2 / s k := by
      refine Finset.sum_congr rfl fun k _ => ?_
      rw [dotProduct_smul, smul_eq_mul, ← hρ k]
      ring
    rw [hcross]
  exact ⟨hr_eq, hr_norm.trans hb_dot.symm, hb_dot⟩

end RiemannBlueprint.MatrixHalfObservation
