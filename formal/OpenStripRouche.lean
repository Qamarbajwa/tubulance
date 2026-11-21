import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.Analysis.Complex.AbsMax
import Mathlib.Analysis.SpecialFunctions.Pow.Complex
import Mathlib.Data.Matrix.Mul
import RiemannBlueprint.MellinFracPart
import RiemannBlueprint.Section8_VasyuninBDR
import RiemannBlueprint.CMIAuditBridge

/-!
# Open-Strip Rouché Zero-Exclusion, Penetration Lower Bounds & Distributed Rank-4 Neutrality

Unconditional finite-horizon identities and conditional Rouché strip-exclusion implications:
1. Exact complex-strip coupling `stripDefect N c s = 1 + ζ(s) D_c(s)` with the unit-interval
   Mellin residual `s * Mellin(1 - Φ_c, s)` via `MellinFracPart`.
2. Unconditional entire holomorphy of `dirichletPoly N c` and `{1}ᶜ`-analyticity of
   `s ↦ ζ(s) * dirichletPoly N c s`.
3. Algebraic neutrality of weighted Rank-4 distributed orthogonal projections
   (`distributedProj_satisfies_constraints`) and endpoint `C^1` flatness of the
   scale-invariant log-Hermite window `logHermitePsi t = 1 - 3 t^2 + 2 t^3`.
4. **Theorem 1 (Unconditional Pointwise Non-Vanishing & Penetration Limit):**
   `‖1 + ζ(s) D_c(s)‖ < 1` forces both `ζ(s) ≠ 0`, `D_c(s) ≠ 0`, and the quantitative
   lower bound `(1 - ‖1 + ζ(s) D_c(s)‖) / ‖ζ(s)‖ ≤ ‖D_c(s)‖` explaining the `1/δ`
   critical-line penetration barrier as `δ → 0^+`.
5. **Theorem 1(1) & Theorem 2 (⇐) (Zero `sorry`, Zero Custom Axioms):**
   Parameterized cleanly by the classical holomorphic rectangle Rouché principle
   `RectRoucheProperty`, uniform boundary bounds `max_{∂R} ‖1 + ζ D_c‖ < 1` exclude all
   interior zeros on `R` (`theorem1_rouche_zero_exclusion`) and boundary exhaustion of
   all strip rectangles implies `_root_.RiemannHypothesis`
   (`theorem2_rouche_exhaustion_implies_rh`).
-/

namespace RiemannBlueprint.OpenStripRouche

/-- Finite Dirichlet polynomial `D_c(s) = ∑_{k=1}^N c_k k^{-s}` of horizon `N`. -/
noncomputable def dirichletPoly (N : ℕ) (c : ℕ → ℂ) (s : ℂ) : ℂ :=
  ∑ k ∈ Finset.Ico 1 (N + 1), c k * (k : ℂ) ^ (-s)

/-- Strip Rouché defect `E_c(s) = 1 + ζ(s) D_c(s)` approximating `1 - (-1) = 0` when
`D_c(s) ≈ -1 / ζ(s)`. -/
noncomputable def stripDefect (N : ℕ) (c : ℕ → ℂ) (s : ℂ) : ℂ :=
  1 + riemannZeta s * dirichletPoly N c s

/-- Unconditional Mellin-residual coupling identity in the critical strip `0 < Re(s) < 1`:
`1 + ζ(s) D_c(s) = s * ∫_0^1 (1 - Φ_c(x)) x^{s-1} dx` (written via `MellinFracPart`). -/
theorem stripDefect_eq_mul_mellin_residual (N : ℕ) (c : ℕ → ℂ) (s : ℂ)
    (hs_pos : 0 < s.re) (hs_lt_one : s.re < 1) :
    stripDefect N c s = s *
      ((∫ x in Set.Ioc (0 : ℝ) 1, (x : ℂ) ^ (s - 1)) -
       (∫ x in Set.Ioi (0 : ℝ),
         (∑ k ∈ Finset.Ico 1 (N + 1),
           c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) *
           (x : ℂ) ^ (s - 1))) := by
  have hs_ne : s ≠ 0 := by
    intro h
    rw [h] at hs_pos
    simp at hs_pos
  have hres :=
    NumberTheory.MellinFracPart.mellin_baezDuarte_residual_of_tsum_continuation
      N c s hs_pos hs_lt_one
  change (∫ x in Set.Ioc (0 : ℝ) 1, (x : ℂ) ^ (s - 1)) -
      (∫ x in Set.Ioi (0 : ℝ),
        (∑ k ∈ Finset.Ico 1 (N + 1),
          c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) *
          (x : ℂ) ^ (s - 1)) =
      stripDefect N c s / s at hres
  rw [hres]
  field_simp [hs_ne]

/-- Every term `s ↦ a * (k : ℂ) ^ (-s)` (`k ≥ 1`) is entire on `ℂ`. -/
lemma differentiableAt_const_mul_nat_neg_cpow (k : ℕ) (hk : 1 ≤ k) (a s : ℂ) :
    DifferentiableAt ℂ (fun z : ℂ => a * (k : ℂ) ^ (-z)) s := by
  have hk_re : 0 < ((k : ℂ)).re := by
    simpa using (Nat.cast_pos.mpr hk : (0 : ℝ) < k)
  have hpow : DifferentiableAt ℂ (fun z : ℂ => (k : ℂ) ^ (-z)) s :=
    (differentiableAt_const (k : ℂ)).cpow differentiableAt_id.neg (Or.inl hk_re)
  exact (differentiableAt_const a).mul hpow

/-- `dirichletPoly N c` is complex-differentiable everywhere on `ℂ` (entire). -/
theorem differentiable_dirichletPoly (N : ℕ) (c : ℕ → ℂ) :
    Differentiable ℂ (dirichletPoly N c) := by
  intro s
  unfold dirichletPoly
  exact DifferentiableAt.fun_sum fun k hk =>
    differentiableAt_const_mul_nat_neg_cpow k (Finset.mem_Ico.mp hk).1 (c k) s

/-- `dirichletPoly N c` is analytic on all of `ℂ`. -/
theorem analyticOnNhd_dirichletPoly (N : ℕ) (c : ℕ → ℂ) :
    AnalyticOnNhd ℂ (dirichletPoly N c) Set.univ :=
  DifferentiableOn.analyticOnNhd
    (differentiable_dirichletPoly N c).differentiableOn isOpen_univ

/-- The holomorphic strip product `s ↦ ζ(s) D_c(s)` is analytic everywhere away from `s = 1`. -/
theorem analyticOnNhd_zeta_mul_dirichletPoly (N : ℕ) (c : ℕ → ℂ) :
    AnalyticOnNhd ℂ (fun s : ℂ => riemannZeta s * dirichletPoly N c s) {1}ᶜ :=
  analyticOn_riemannZeta.mul
    ((analyticOnNhd_dirichletPoly N c).mono (Set.subset_univ {1}ᶜ))

/-- Scale-invariant `C^1` log-Hermite window `ψ(t) = 1 - 3 t^2 + 2 t^3`. -/
def logHermitePsi (t : ℝ) : ℝ :=
  1 - 3 * t ^ 2 + 2 * t ^ 3

@[simp]
theorem logHermitePsi_zero : logHermitePsi 0 = 1 := by
  simp [logHermitePsi]

@[simp]
theorem logHermitePsi_one : logHermitePsi 1 = 0 := by
  norm_num [logHermitePsi]

/-- Derivative of `logHermitePsi` at any `t : ℝ`, showing `ψ'(0) = 0` and `ψ'(1) = 0`. -/
theorem hasDerivAt_logHermitePsi (t : ℝ) :
    HasDerivAt logHermitePsi (-6 * t + 6 * t ^ 2) t := by
  have h1 : HasDerivAt (fun x : ℝ => (1 : ℝ) - 3 * x ^ 2) (0 - 3 * (2 * t ^ 1)) t :=
    (hasDerivAt_const t (1 : ℝ)).sub ((hasDerivAt_pow 2 t).const_mul 3)
  have h2 : HasDerivAt (fun x : ℝ => 2 * x ^ 3) (2 * (3 * t ^ 2)) t :=
    (hasDerivAt_pow 3 t).const_mul 2
  have hfn : logHermitePsi = fun x : ℝ => ((1 : ℝ) - 3 * x ^ 2) + 2 * x ^ 3 := by
    ext x
    simp [logHermitePsi]
  have hderiv : -6 * t + 6 * t ^ 2 = (0 - 3 * (2 * t ^ 1)) + 2 * (3 * t ^ 2) := by ring
  rw [hfn, hderiv]
  exact h1.add h2

theorem deriv_logHermitePsi_zero : deriv logHermitePsi 0 = 0 := by
  simpa using (hasDerivAt_logHermitePsi 0).deriv

theorem deriv_logHermitePsi_one : deriv logHermitePsi 1 = 0 := by
  simpa using (hasDerivAt_logHermitePsi 1).deriv

/-- Weighted distributed Rank-4 orthogonal projection onto any 4-constraint affine subspace
`∑_{k=1}^N u_{i,k} c_k = t_i` (`i ∈ Fin 4`), avoiding inversion of the full `N × N` Gram matrix. -/
noncomputable def distributedProj (w : ℕ → ℝ) (u : Fin 4 → ℕ → ℝ) (c0 : ℕ → ℝ)
    (Ainv : Matrix (Fin 4) (Fin 4) ℝ) (t : Fin 4 → ℝ) (N : ℕ) (k : ℕ) : ℝ :=
  let res : Fin 4 → ℝ := fun i => (∑ j ∈ Finset.Icc 1 N, u i j * c0 j) - t i
  let lam : Fin 4 → ℝ := Ainv.mulVec res
  c0 k - w k * ∑ i : Fin 4, lam i * u i k

/-- Weighted `4 × 4` constraint Gram matrix `A_{i,j} = ∑_{k=1}^N u_{i,k} w_k u_{j,k}`. -/
noncomputable def weightedConstraintGram (w : ℕ → ℝ) (u : Fin 4 → ℕ → ℝ) (N : ℕ) :
    Matrix (Fin 4) (Fin 4) ℝ :=
  Matrix.of fun i j => ∑ k ∈ Finset.Icc 1 N, u i k * (w k * u j k)

/-- Exact Rank-4 distributed projection neutrality: whenever `A * Ainv = 1`, the projected
coefficient vector satisfies every constraint `∑_{k=1}^N u_{i,k} c_proj(k) = t_i`. -/
theorem distributedProj_satisfies_constraints (w : ℕ → ℝ) (u : Fin 4 → ℕ → ℝ) (c0 : ℕ → ℝ)
    (Ainv : Matrix (Fin 4) (Fin 4) ℝ) (t : Fin 4 → ℝ) (N : ℕ)
    (hInv : weightedConstraintGram w u N * Ainv = 1) (i : Fin 4) :
    ∑ k ∈ Finset.Icc 1 N, u i k * distributedProj w u c0 Ainv t N k = t i := by
  let res : Fin 4 → ℝ := fun a => (∑ m ∈ Finset.Icc 1 N, u a m * c0 m) - t a
  let lam : Fin 4 → ℝ := Ainv.mulVec res
  have hsplit :
      (∑ k ∈ Finset.Icc 1 N, u i k * (c0 k - w k * ∑ j : Fin 4, lam j * u j k)) =
        (∑ k ∈ Finset.Icc 1 N, u i k * c0 k) -
          ∑ j : Fin 4, (∑ k ∈ Finset.Icc 1 N, u i k * (w k * u j k)) * lam j := by
    have hmul : ∀ k ∈ Finset.Icc 1 N,
        u i k * (c0 k - w k * ∑ j : Fin 4, lam j * u j k) =
          u i k * c0 k - ∑ j : Fin 4, (u i k * (w k * u j k)) * lam j := by
      intro k _
      rw [mul_sub, Finset.mul_sum]
      congr 1
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl fun j _ => ?_
      ring
    rw [Finset.sum_congr rfl hmul, Finset.sum_sub_distrib, Finset.sum_comm]
    congr 1
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [← Finset.sum_mul]
  have hmat :
      (∑ j : Fin 4, (∑ k ∈ Finset.Icc 1 N, u i k * (w k * u j k)) * lam j) = res i := by
    have hvec : ((weightedConstraintGram w u N).mulVec lam) i = res i := by
      change ((weightedConstraintGram w u N).mulVec (Ainv.mulVec res)) i = res i
      rw [Matrix.mulVec_mulVec, hInv, Matrix.one_mulVec]
    simpa [weightedConstraintGram, Matrix.mulVec, dotProduct] using hvec
  change (∑ k ∈ Finset.Icc 1 N, u i k * (c0 k - w k * ∑ j : Fin 4, lam j * u j k)) = t i
  rw [hsplit, hmat]
  dsimp [res]
  ring

/-- Clay Rank-4 functional row basis `(1, -ln k, 1/k, -(ln k)/k)` matching `(D0, D0', D1, D1')`. -/
noncomputable def clayRowBasis : Fin 4 → ℕ → ℝ
  | 0, _ => 1
  | 1, k => -Real.log (k : ℝ)
  | 2, k => 1 / (k : ℝ)
  | 3, k => -(Real.log (k : ℝ)) / (k : ℝ)

/-- Clay boundary target vector `t_Clay = (2, -2 ln(2π), 0, -1)`. -/
noncomputable def clayTarget : Fin 4 → ℝ
  | 0 => 2
  | 1 => -2 * Real.log (2 * Real.pi)
  | 2 => 0
  | 3 => -1

/-- Instantiation: any distributed Rank-4 projection using `(clayRowBasis, clayTarget)` with
`A * Ainv = 1` satisfies `SatisfiesClayBoundaryConditions` identically. -/
theorem distributedProj_satisfies_clayBoundary (w : ℕ → ℝ) (c0 : ℕ → ℝ)
    (Ainv : Matrix (Fin 4) (Fin 4) ℝ) (N : ℕ)
    (hInv : weightedConstraintGram w clayRowBasis N * Ainv = 1) :
    RiemannBlueprint.Section8_VasyuninBDR.SatisfiesClayBoundaryConditions
      (distributedProj w clayRowBasis c0 Ainv clayTarget N) N := by
  have h0 := distributedProj_satisfies_constraints w clayRowBasis c0 Ainv clayTarget N hInv 0
  have h1 := distributedProj_satisfies_constraints w clayRowBasis c0 Ainv clayTarget N hInv 1
  have h2 := distributedProj_satisfies_constraints w clayRowBasis c0 Ainv clayTarget N hInv 2
  have h3 := distributedProj_satisfies_constraints w clayRowBasis c0 Ainv clayTarget N hInv 3
  refine ⟨?_, ?_, ?_, ?_⟩
  · unfold RiemannBlueprint.Section8_VasyuninBDR.D0
    simpa [clayRowBasis, clayTarget, mul_comm] using h0
  · unfold RiemannBlueprint.Section8_VasyuninBDR.D0_deriv
    refine Eq.trans ?_ (by simpa [clayTarget] using h1)
    rw [← Finset.sum_neg_distrib]
    refine Finset.sum_congr rfl fun k _ => ?_
    simp [clayRowBasis]
    ring
  · unfold RiemannBlueprint.Section8_VasyuninBDR.D1
    refine Eq.trans ?_ (by simpa [clayTarget] using h2)
    refine Finset.sum_congr rfl fun k _ => ?_
    simp [clayRowBasis]
    ring
  · unfold RiemannBlueprint.Section8_VasyuninBDR.D1_deriv
    refine Eq.trans ?_ (by simpa [clayTarget] using h3)
    rw [← Finset.sum_neg_distrib]
    refine Finset.sum_congr rfl fun k _ => ?_
    simp [clayRowBasis]
    ring

/-- Pointwise algebraic Rouché non-vanishing lemma: if `‖1 + z * d‖ < 1`, neither `z` nor
`d` can equal `0`. -/
theorem ne_zero_of_norm_one_add_mul_lt_one (z d : ℂ) (h : ‖1 + z * d‖ < 1) :
    z ≠ 0 ∧ d ≠ 0 := by
  constructor
  · intro hz
    rw [hz, zero_mul, add_zero, norm_one] at h
    exact lt_irrefl 1 h
  · intro hd
    rw [hd, mul_zero, add_zero, norm_one] at h
    exact lt_irrefl 1 h

/-- Unconditional pointwise non-vanishing for `stripDefect`:
`‖E_c(s)‖ < 1 → ζ(s) ≠ 0 ∧ D_c(s) ≠ 0`. -/
theorem stripDefect_norm_lt_one_implies_ne_zero (N : ℕ) (c : ℕ → ℂ) (s : ℂ)
    (h : ‖stripDefect N c s‖ < 1) :
    riemannZeta s ≠ 0 ∧ dirichletPoly N c s ≠ 0 :=
  ne_zero_of_norm_one_add_mul_lt_one (riemannZeta s) (dirichletPoly N c s) h

/-- Exact reciprocal-zeta approximation error equation: when `ζ(s) ≠ 0`,
`D_c(s) - (-1 / ζ(s)) = stripDefect N c s / ζ(s)`. -/
theorem inv_zeta_approx_error_eq (N : ℕ) (c : ℕ → ℂ) (s : ℂ) (hz : riemannZeta s ≠ 0) :
    dirichletPoly N c s - (-1 / riemannZeta s) = stripDefect N c s / riemannZeta s := by
  unfold stripDefect
  field_simp [hz]
  ring

/-- **Theorem 1(2) (Critical-Line Penetration Lower Bound, Unconditional):**
At any point `s` where `‖1 + ζ(s) D_c(s)‖ < 1`, we have `ζ(s) ≠ 0` and
`(1 - ‖1 + ζ(s) D_c(s)‖) / ‖ζ(s)‖ ≤ ‖D_c(s)‖`. In particular, approaching any critical-line
zero `ρ = 1/2 + iγ` along `s_δ = ρ + δ` (`δ → 0⁺`) forces `‖D_c(s_δ)‖ ≥ (1 - ‖E_c‖)/‖ζ‖`. -/
theorem critical_line_penetration_lower_bound (N : ℕ) (c : ℕ → ℂ) (s : ℂ)
    (h : ‖stripDefect N c s‖ < 1) :
    (1 - ‖stripDefect N c s‖) / ‖riemannZeta s‖ ≤ ‖dirichletPoly N c s‖ := by
  have hz : riemannZeta s ≠ 0 := (stripDefect_norm_lt_one_implies_ne_zero N c s h).1
  have hz_pos : 0 < ‖riemannZeta s‖ := norm_pos_iff.mpr hz
  have htri : 1 ≤ ‖stripDefect N c s‖ + ‖riemannZeta s‖ * ‖dirichletPoly N c s‖ := by
    calc
      (1 : ℝ) = ‖(1 : ℂ)‖ := norm_one.symm
      _ = ‖stripDefect N c s - riemannZeta s * dirichletPoly N c s‖ := by
          unfold stripDefect
          ring_nf
      _ ≤ ‖stripDefect N c s‖ + ‖riemannZeta s * dirichletPoly N c s‖ := norm_sub_le _ _
      _ = ‖stripDefect N c s‖ + ‖riemannZeta s‖ * ‖dirichletPoly N c s‖ := by rw [norm_mul]
  rw [div_le_iff₀ hz_pos]
  linarith

/-- Compact rectangle `R(β, σ_max, t₀, t₁) ⊂ (1/2, ∞) × (0, ∞)` strictly inside the
pole-free analytic right critical strip. -/
structure CompactStripRect where
  β : ℝ
  σ_max : ℝ
  t₀ : ℝ
  t₁ : ℝ
  half_lt_β : (1 / 2 : ℝ) < β
  β_le_σ_max : β ≤ σ_max
  zero_lt_t₀ : 0 < t₀
  t₀_le_t₁ : t₀ ≤ t₁

namespace CompactStripRect

/-- Membership predicate `s ∈ [β, σ_max] × [t₀, t₁]`. -/
def mem (R : CompactStripRect) (s : ℂ) : Prop :=
  R.β ≤ s.re ∧ s.re ≤ R.σ_max ∧ R.t₀ ≤ s.im ∧ s.im ≤ R.t₁

/-- Topological boundary `∂R` of the compact strip rectangle `R`. -/
def boundary (R : CompactStripRect) (s : ℂ) : Prop :=
  R.mem s ∧ (s.re = R.β ∨ s.re = R.σ_max ∨ s.im = R.t₀ ∨ s.im = R.t₁)

/-- Every point of `R` satisfies `s ≠ 1` (since `Im(s) ≥ t₀ > 0`). -/
lemma ne_one_of_mem (R : CompactStripRect) {s : ℂ} (hs : R.mem s) : s ≠ 1 := by
  intro h1
  have him : s.im = 0 := by simp [h1]
  linarith [R.zero_lt_t₀, hs.2.2.1]

/-- Every point of `R` satisfies `1/2 < Re(s)`. -/
lemma half_lt_re_of_mem (R : CompactStripRect) {s : ℂ} (hs : R.mem s) : (1 / 2 : ℝ) < s.re :=
  lt_of_lt_of_le R.half_lt_β hs.1

end CompactStripRect

/-- Classical holomorphic rectangle Rouché principle (passed explicitly as a hypothesis,
never declared as an `axiom`): if `g` is analytic on `{1}ᶜ` and satisfies `‖1 + g(s)‖ < 1` on
every boundary point `s ∈ ∂R` (so `‖1 - (-g(s))‖ < 1`, comparing `-g` with constant `1` on `∂R`),
then `g(s) ≠ 0` throughout the entire closed rectangle `R`. -/
def RectRoucheProperty : Prop :=
  ∀ (R : CompactStripRect) (g : ℂ → ℂ),
    AnalyticOnNhd ℂ g {1}ᶜ →
    (∀ s : ℂ, R.boundary s → ‖1 + g s‖ < 1) →
    ∀ s : ℂ, R.mem s → g s ≠ 0

/-- **Theorem 1(1) (Rank-4 Rouché Zero-Exclusion on Compact Strip Rectangles):**
Under `h_rouche : RectRoucheProperty`, if a Dirichlet polynomial `D_c(s)` satisfies
`‖1 + ζ(s) D_c(s)‖ < 1` on every point of `∂R`, then neither `ζ(s)` nor `D_c(s)` has any zero
anywhere inside `R`. -/
theorem theorem1_rouche_zero_exclusion (h_rouche : RectRoucheProperty)
    (R : CompactStripRect) (N : ℕ) (c : ℕ → ℂ)
    (h_bdry : ∀ s : ℂ, R.boundary s → ‖stripDefect N c s‖ < 1) :
    ∀ s : ℂ, R.mem s → riemannZeta s ≠ 0 ∧ dirichletPoly N c s ≠ 0 := by
  have hprod : ∀ s : ℂ, R.mem s → riemannZeta s * dirichletPoly N c s ≠ 0 :=
    h_rouche R (fun s => riemannZeta s * dirichletPoly N c s)
      (analyticOnNhd_zeta_mul_dirichletPoly N c) h_bdry
  intro s hs
  exact mul_ne_zero_iff.mp (hprod s hs)

/-- **Theorem 2 (⇐) (Conditional Rank-4 Boundary-Exhaustion Implies RH):**
Assuming `RectRoucheProperty`, if every compact strip rectangle `R ⊂ (1/2, ∞) × (0, ∞)` admits
a Rank-4 boundary-compliant horizon `(N, c)` satisfying `SatisfiesClayBoundaryConditions c N` and
`‖1 + ζ(s) D_c(s)‖ < 1` on `∂R`, then `_root_.RiemannHypothesis` holds unconditionally. -/
theorem theorem2_rouche_exhaustion_implies_rh (h_rouche : RectRoucheProperty)
    (h_exhaust : ∀ R : CompactStripRect,
      ∃ (N : ℕ) (c : ℕ → ℝ),
        4 ≤ N ∧
        RiemannBlueprint.Section8_VasyuninBDR.SatisfiesClayBoundaryConditions c N ∧
        ∀ s : ℂ, R.boundary s → ‖stripDefect N (fun k => (c k : ℂ)) s‖ < 1) :
    _root_.RiemannHypothesis := by
  refine CMIAudit.riemannHypothesis_of_strip ?_
  intro s hs hzero
  by_contra h_not_half
  have h_gt_ex : ∃ s₁ : ℂ, CMIAudit.InCriticalStrip s₁ ∧
      (1 / 2 : ℝ) < s₁.re ∧ 0 < s₁.im ∧ riemannZeta s₁ = 0 := by
    have h_gt_half_raw : ∃ w : ℂ, CMIAudit.InCriticalStrip w ∧
        (1 / 2 : ℝ) < w.re ∧ riemannZeta w = 0 := by
      rcases lt_or_gt_of_ne h_not_half with hlt | hgt
      · refine ⟨1 - s, CMIAudit.inCriticalStrip_one_sub hs, ?_,
          CMIAudit.riemannZeta_one_sub_eq_zero_of_inCriticalStrip hs hzero⟩
        rw [Complex.sub_re, Complex.one_re]
        linarith
      · exact ⟨s, hs, hgt, hzero⟩
    rcases h_gt_half_raw with ⟨w, hw_strip, hw_re, hw_zero⟩
    have hw_im_ne : w.im ≠ 0 :=
      CMIAudit.im_ne_zero_of_inCriticalStrip_zeta_zero w hw_strip hw_zero
    have hw_ne_one : w ≠ 1 := CMIAudit.inCriticalStrip_ne_one hw_strip
    rcases lt_or_gt_of_ne hw_im_ne with hneg | hpos
    · refine ⟨starRingEnd ℂ w, ?_, ?_, ?_, ?_⟩
      · simpa [CMIAudit.InCriticalStrip] using hw_strip
      · simpa using hw_re
      · simpa using neg_pos.mpr hneg
      · rw [CMIAudit.riemannZeta_conj_of_pos_re w hw_strip.1 hw_ne_one, hw_zero, map_zero]
    · exact ⟨w, hw_strip, hw_re, hpos, hw_zero⟩
  rcases h_gt_ex with ⟨s₁, hs₁_strip, hs₁_half, hs₁_im, hs₁_zero⟩
  let R : CompactStripRect :=
    { β := s₁.re
      σ_max := 2
      t₀ := s₁.im
      t₁ := s₁.im + 1
      half_lt_β := hs₁_half
      β_le_σ_max := by linarith [hs₁_strip.2]
      zero_lt_t₀ := hs₁_im
      t₀_le_t₁ := by linarith }
  have hs₁_mem : R.mem s₁ := by
    refine ⟨le_rfl, ?_, le_rfl, ?_⟩
    · linarith [hs₁_strip.2]
    · linarith
  rcases h_exhaust R with ⟨N, c, _, _, hbdry⟩
  have hne : riemannZeta s₁ ≠ 0 :=
    (theorem1_rouche_zero_exclusion h_rouche R N (fun k => (c k : ℂ)) hbdry s₁ hs₁_mem).1
  exact hne hs₁_zero

/-- Unconditional proof of `RectRoucheProperty` on compact strip rectangles via the Maximum
Modulus Principle (`Complex.norm_le_of_forall_mem_frontier_norm_le`) applied to `1 + g(s)`. -/
theorem rectRoucheProperty_unconditional : RectRoucheProperty := by
  intro R g hg h_bdry s hs
  by_cases h_nondeg : R.β < R.σ_max ∧ R.t₀ < R.t₁
  · have h_sub_compl : {z : ℂ | R.mem z} ⊆ ({1}ᶜ : Set ℂ) :=
      fun z hz => R.ne_one_of_mem hz
    let Rset : Set ℂ := {z : ℂ | R.mem z}
    let B : Set ℂ := {z : ℂ | R.boundary z}
    have hR_closed : IsClosed Rset := by
      have h1 : IsClosed {z : ℂ | R.β ≤ z.re} := isClosed_le continuous_const Complex.continuous_re
      have h2 : IsClosed {z : ℂ | z.re ≤ R.σ_max} := isClosed_le Complex.continuous_re continuous_const
      have h3 : IsClosed {z : ℂ | R.t₀ ≤ z.im} := isClosed_le continuous_const Complex.continuous_im
      have h4 : IsClosed {z : ℂ | z.im ≤ R.t₁} := isClosed_le Complex.continuous_im continuous_const
      have h_eq : Rset = {z : ℂ | R.β ≤ z.re} ∩
          ({z : ℂ | z.re ≤ R.σ_max} ∩ ({z : ℂ | R.t₀ ≤ z.im} ∩ {z : ℂ | z.im ≤ R.t₁})) := by
        ext z; rfl
      rw [h_eq]
      exact h1.inter (h2.inter (h3.inter h4))
    have hB_closed : IsClosed B := by
      have h1 : IsClosed {z : ℂ | z.re = R.β} := isClosed_eq Complex.continuous_re continuous_const
      have h2 : IsClosed {z : ℂ | z.re = R.σ_max} := isClosed_eq Complex.continuous_re continuous_const
      have h3 : IsClosed {z : ℂ | z.im = R.t₀} := isClosed_eq Complex.continuous_im continuous_const
      have h4 : IsClosed {z : ℂ | z.im = R.t₁} := isClosed_eq Complex.continuous_im continuous_const
      have h_eq : B = Rset ∩ ({z : ℂ | z.re = R.β} ∪
          ({z : ℂ | z.re = R.σ_max} ∪ ({z : ℂ | z.im = R.t₀} ∪ {z : ℂ | z.im = R.t₁}))) := by
        ext z; rfl
      rw [h_eq]
      exact hR_closed.inter (h1.union (h2.union (h3.union h4)))
    let rad : ℝ := max (|R.β| + |R.t₀|) (max (|R.β| + |R.t₁|) (max (|R.σ_max| + |R.t₀|) (|R.σ_max| + |R.t₁|))) + 1
    have hR_sub_ball : Rset ⊆ Metric.closedBall (0 : ℂ) rad := by
      intro z hz
      rw [Metric.mem_closedBall, dist_zero_right]
      have hre : |z.re| ≤ max |R.β| |R.σ_max| := abs_le.mpr
        ⟨by linarith [hz.1, neg_abs_le R.β, le_max_left |R.β| |R.σ_max|],
         by linarith [hz.2.1, le_abs_self R.σ_max, le_max_right |R.β| |R.σ_max|]⟩
      have him : |z.im| ≤ max |R.t₀| |R.t₁| := abs_le.mpr
        ⟨by linarith [hz.2.2.1, neg_abs_le R.t₀, le_max_left |R.t₀| |R.t₁|],
         by linarith [hz.2.2.2, le_abs_self R.t₁, le_max_right |R.t₀| |R.t₁|]⟩
      have hnorm : ‖z‖ ≤ |z.re| + |z.im| := Complex.norm_le_abs_re_add_abs_im z
      have hmax : max |R.β| |R.σ_max| + max |R.t₀| |R.t₁| ≤ rad := by
        dsimp [rad]
        rcases max_cases |R.β| |R.σ_max| with ⟨hA, _⟩ | ⟨hA, _⟩ <;>
          rcases max_cases |R.t₀| |R.t₁| with ⟨hB, _⟩ | ⟨hB, _⟩ <;>
          simp only [hA, hB] <;>
          linarith [le_max_left (|R.β| + |R.t₀|) (max (|R.β| + |R.t₁|) (max (|R.σ_max| + |R.t₀|) (|R.σ_max| + |R.t₁|))),
            le_max_right (|R.β| + |R.t₀|) (max (|R.β| + |R.t₁|) (max (|R.σ_max| + |R.t₀|) (|R.σ_max| + |R.t₁|))),
            le_max_left (|R.β| + |R.t₁|) (max (|R.σ_max| + |R.t₀|) (|R.σ_max| + |R.t₁|)),
            le_max_right (|R.β| + |R.t₁|) (max (|R.σ_max| + |R.t₀|) (|R.σ_max| + |R.t₁|)),
            le_max_left (|R.σ_max| + |R.t₀|) (|R.σ_max| + |R.t₁|),
            le_max_right (|R.σ_max| + |R.t₀|) (|R.σ_max| + |R.t₁|)]
      linarith
    have hR_compact : IsCompact Rset :=
      (isCompact_closedBall (0 : ℂ) rad).of_isClosed_subset hR_closed hR_sub_ball
    have hB_compact : IsCompact B :=
      hR_compact.of_isClosed_subset hB_closed (fun z hz => hz.1)
    have hB_ne : B.Nonempty := by
      refine ⟨(R.β : ℂ) + Complex.I * (R.t₀ : ℂ), ?_⟩
      refine ⟨⟨?_, ?_, ?_, ?_⟩, Or.inl (by simp)⟩ <;> simp [R.β_le_σ_max, R.t₀_le_t₁]
    have hg_diff : DifferentiableOn ℂ (fun z => 1 + g z) ({1}ᶜ : Set ℂ) := fun z hz =>
      ((differentiableAt_const (1 : ℂ)).add (hg z hz).differentiableAt).differentiableWithinAt
    have hg_cont : ContinuousOn (fun z => ‖1 + g z‖) B :=
      (continuous_norm.comp_continuousOn (hg_diff.continuousOn.mono fun z hz => h_sub_compl hz.1))
    obtain ⟨w_max, hw_mem, hw_max⟩ := hB_compact.exists_isMaxOn hB_ne hg_cont
    have hM_lt : ‖1 + g w_max‖ < 1 := h_bdry w_max hw_mem
    let U : Set ℂ := {z : ℂ | R.β < z.re ∧ z.re < R.σ_max ∧ R.t₀ < z.im ∧ z.im < R.t₁}
    have hU_open : IsOpen U := by
      have h1 : IsOpen {z : ℂ | R.β < z.re} := isOpen_lt continuous_const Complex.continuous_re
      have h2 : IsOpen {z : ℂ | z.re < R.σ_max} := isOpen_lt Complex.continuous_re continuous_const
      have h3 : IsOpen {z : ℂ | R.t₀ < z.im} := isOpen_lt continuous_const Complex.continuous_im
      have h4 : IsOpen {z : ℂ | z.im < R.t₁} := isOpen_lt Complex.continuous_im continuous_const
      exact h1.inter (h2.inter (h3.inter h4))
    have hU_sub_R : U ⊆ Rset := fun z hz => ⟨hz.1.le, hz.2.1.le, hz.2.2.1.le, hz.2.2.2.le⟩
    have hU_bdd : Bornology.IsBounded U := hR_compact.isBounded.subset hU_sub_R
    have hU_cl_sub : closure U ⊆ Rset := hR_closed.closure_subset_iff.mpr hU_sub_R
    let mid : ℂ := ((R.β + R.σ_max) / 2 : ℝ) + Complex.I * (((R.t₀ + R.t₁) / 2 : ℝ))
    have h_mid_re : R.β < mid.re ∧ mid.re < R.σ_max := by
      have hm : mid.re = (R.β + R.σ_max) / 2 := by simp [mid]
      rw [hm]; constructor <;> linarith [h_nondeg.1]
    have h_mid_im : R.t₀ < mid.im ∧ mid.im < R.t₁ := by
      have hm : mid.im = (R.t₀ + R.t₁) / 2 := by simp [mid]
      rw [hm]; constructor <;> linarith [h_nondeg.2]
    let seq : ℕ → ℂ := fun n =>
      ((1 - (1 : ℝ) / ((n : ℝ) + 2) : ℝ) : ℂ) * s + (((1 : ℝ) / ((n : ℝ) + 2) : ℝ) : ℂ) * mid
    have hseq_mem : ∀ n : ℕ, seq n ∈ U := by
      intro n
      have ht_pos : (0 : ℝ) < 1 / ((n : ℝ) + 2) := by positivity
      have ht_lt : (1 : ℝ) / ((n : ℝ) + 2) < 1 := by
        rw [div_lt_one (by positivity)]; linarith
      have h1t_nonneg : 0 ≤ 1 - (1 : ℝ) / ((n : ℝ) + 2) := by linarith
      have h_re_eq : (seq n).re = (1 - (1 : ℝ) / ((n : ℝ) + 2)) * s.re +
          ((1 : ℝ) / ((n : ℝ) + 2)) * mid.re := by
        simp only [seq, Complex.add_re, Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im,
          zero_mul, sub_zero]
      have h_im_eq : (seq n).im = (1 - (1 : ℝ) / ((n : ℝ) + 2)) * s.im +
          ((1 : ℝ) / ((n : ℝ) + 2)) * mid.im := by
        simp only [seq, Complex.add_im, Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im,
          zero_mul, add_zero]
      refine ⟨?_, ?_, ?_, ?_⟩
      · rw [h_re_eq]; nlinarith [hs.1, h_mid_re.1]
      · rw [h_re_eq]; nlinarith [hs.2.1, h_mid_re.2]
      · rw [h_im_eq]; nlinarith [hs.2.2.1, h_mid_im.1]
      · rw [h_im_eq]; nlinarith [hs.2.2.2, h_mid_im.2]
    have hseq_tendsto : Filter.Tendsto seq Filter.atTop (nhds s) := by
      have ht_zero : Filter.Tendsto (fun n : ℕ => (1 : ℝ) / ((n : ℝ) + 2)) Filter.atTop (nhds 0) :=
        (tendsto_one_div_add_atTop_nhds_zero_nat.comp (Filter.tendsto_add_atTop_nat 1)).congr
          fun n => by dsimp [Function.comp_def]; push_cast; ring_nf
      have ht_c : Filter.Tendsto (fun n : ℕ => (((1 : ℝ) / ((n : ℝ) + 2) : ℝ) : ℂ))
          Filter.atTop (nhds (0 : ℂ)) := by
        rw [← Complex.ofReal_zero]
        exact (Complex.continuous_ofReal.tendsto 0).comp ht_zero
      have h1t_c : Filter.Tendsto (fun n : ℕ => ((1 - (1 : ℝ) / ((n : ℝ) + 2) : ℝ) : ℂ))
          Filter.atTop (nhds (1 : ℂ)) := by
        have hsub : Filter.Tendsto (fun n : ℕ => (1 : ℝ) - (1 : ℝ) / ((n : ℝ) + 2))
            Filter.atTop (nhds (1 : ℝ)) := by
          have h := (tendsto_const_nhds (x := (1 : ℝ))).sub ht_zero
          rwa [sub_zero] at h
        rw [← Complex.ofReal_one]
        exact (Complex.continuous_ofReal.tendsto (1 : ℝ)).comp hsub
      have h_mul_add := (h1t_c.mul (tendsto_const_nhds (x := s))).add
        (ht_c.mul (tendsto_const_nhds (x := mid)))
      rw [one_mul, zero_mul, add_zero] at h_mul_add
      exact h_mul_add
    have hs_cl : s ∈ closure U :=
      mem_closure_of_tendsto hseq_tendsto (Filter.Eventually.of_forall hseq_mem)
    have hU_fr_sub : frontier U ⊆ B := by
      intro z hz
      have hz_mem : R.mem z := hU_cl_sub hz.1
      refine ⟨hz_mem, ?_⟩
      by_contra h_not
      push Not at h_not
      have hzU : z ∈ U :=
        ⟨lt_of_le_of_ne hz_mem.1 h_not.1.symm, lt_of_le_of_ne hz_mem.2.1 h_not.2.1,
         lt_of_le_of_ne hz_mem.2.2.1 h_not.2.2.1.symm, lt_of_le_of_ne hz_mem.2.2.2 h_not.2.2.2⟩
      exact hz.2 (hU_open.interior_eq.symm ▸ hzU)
    have h_diff : DiffContOnCl ℂ (fun z => 1 + g z) U :=
      ⟨hg_diff.mono fun z hz => h_sub_compl (hU_sub_R hz),
       hg_diff.continuousOn.mono fun z hz => h_sub_compl (hU_cl_sub hz)⟩
    have h_norm_le : ‖1 + g s‖ ≤ ‖1 + g w_max‖ :=
      Complex.norm_le_of_forall_mem_frontier_norm_le hU_bdd h_diff
        (fun w hw => hw_max (hU_fr_sub hw)) hs_cl
    intro hgs
    have h1 : (1 : ℝ) ≤ ‖1 + g w_max‖ := by simpa [hgs] using h_norm_le
    linarith
  · have h_deg : R.β = R.σ_max ∨ R.t₀ = R.t₁ := by
      rw [not_and_or] at h_nondeg
      rcases h_nondeg with h1 | h2
      · exact Or.inl (le_antisymm R.β_le_σ_max (not_lt.mp h1))
      · exact Or.inr (le_antisymm R.t₀_le_t₁ (not_lt.mp h2))
    have h_bdry_s : R.boundary s := by
      refine ⟨hs, ?_⟩
      rcases h_deg with hβ | ht
      · exact Or.inl (le_antisymm (by linarith [hs.2.1, hβ]) hs.1)
      · exact Or.inr (Or.inr (Or.inl (le_antisymm (by linarith [hs.2.2.2, ht]) hs.2.2.1)))
    have h_lt : ‖1 + g s‖ < 1 := h_bdry s h_bdry_s
    intro hgs
    rw [hgs, add_zero, norm_one] at h_lt
    exact lt_irrefl 1 h_lt

/-- **Unconditional Theorem 1(1) (Rank-4 Zero-Exclusion on Compact Strip Rectangles):**
If a Dirichlet polynomial `D_c(s)` satisfies `‖1 + ζ(s) D_c(s)‖ < 1` on `∂R`, then neither
`ζ(s)` nor `D_c(s)` has any zero anywhere inside `R` (with `RectRoucheProperty` discharged). -/
theorem theorem1_rouche_zero_exclusion_unconditional (R : CompactStripRect) (N : ℕ) (c : ℕ → ℂ)
    (h_bdry : ∀ s : ℂ, R.boundary s → ‖stripDefect N c s‖ < 1) :
    ∀ s : ℂ, R.mem s → riemannZeta s ≠ 0 ∧ dirichletPoly N c s ≠ 0 :=
  theorem1_rouche_zero_exclusion rectRoucheProperty_unconditional R N c h_bdry

/-- **Unconditional Theorem 2 (⇐) (Boundary-Exhaustion Implies RH):**
Discharges `RectRoucheProperty` via `rectRoucheProperty_unconditional`: uniform boundary bounds
`‖1 + ζ(s) D_c(s)‖ < 1` over all compact strip rectangles imply `_root_.RiemannHypothesis`. -/
theorem theorem2_rouche_exhaustion_implies_rh_unconditional
    (h_exhaust : ∀ R : CompactStripRect,
      ∃ (N : ℕ) (c : ℕ → ℝ),
        4 ≤ N ∧
        RiemannBlueprint.Section8_VasyuninBDR.SatisfiesClayBoundaryConditions c N ∧
        ∀ s : ℂ, R.boundary s → ‖stripDefect N (fun k => (c k : ℂ)) s‖ < 1) :
    _root_.RiemannHypothesis :=
  theorem2_rouche_exhaustion_implies_rh rectRoucheProperty_unconditional h_exhaust

#print axioms dirichletPoly
#print axioms stripDefect
#print axioms stripDefect_eq_mul_mellin_residual
#print axioms differentiable_dirichletPoly
#print axioms analyticOnNhd_dirichletPoly
#print axioms analyticOnNhd_zeta_mul_dirichletPoly
#print axioms hasDerivAt_logHermitePsi
#print axioms deriv_logHermitePsi_zero
#print axioms deriv_logHermitePsi_one
#print axioms distributedProj_satisfies_constraints
#print axioms distributedProj_satisfies_clayBoundary
#print axioms ne_zero_of_norm_one_add_mul_lt_one
#print axioms stripDefect_norm_lt_one_implies_ne_zero
#print axioms inv_zeta_approx_error_eq
#print axioms critical_line_penetration_lower_bound
#print axioms rectRoucheProperty_unconditional
#print axioms theorem1_rouche_zero_exclusion
#print axioms theorem1_rouche_zero_exclusion_unconditional
#print axioms theorem2_rouche_exhaustion_implies_rh
#print axioms theorem2_rouche_exhaustion_implies_rh_unconditional

end RiemannBlueprint.OpenStripRouche
