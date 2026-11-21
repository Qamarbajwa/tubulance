/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
module

public import Mathlib.Analysis.Analytic.IsolatedZeros
public import Mathlib.Analysis.Analytic.Uniqueness
public import Mathlib.Analysis.Calculus.ParametricIntegral
public import Mathlib.Analysis.Complex.CauchyIntegral
public import Mathlib.Analysis.Complex.Liouville
public import Mathlib.Analysis.Fourier.Inversion
public import Mathlib.Basic.Real.Basic
public import Mathlib.Data.Set.Finite.Lattice
public import RiemannBlueprint.MathlibPR_CriticalLineZeros
public import Mathlib.NumberTheory.LSeries.HardyZ
public import Mathlib.NumberTheory.LSeries.RiemannZeta
public import Mathlib.NumberTheory.ModularForms.JacobiTheta.OneVariable
public import Mathlib.Order.Bounds.Basic
public import Mathlib.Tactic.Linarith

/-!
# Hardy's (1914) Critical-Line Zeros Theorem

This file formalizes the unconditional landmark theorem of Hardy (1914):
1. Specialization of the Intermediate Value Theorem sign-change detector to Hardy's real-valued
   `hardyZ` function: `hardyZ a * hardyZ b ≤ 0 → ∃ t₀ ∈ [a, b], riemannZeta (criticalLine t₀) = 0`.
2. Proof that any subset of `ℝ` unbounded above is infinite (`Set.Infinite`).
3. Deduction that existence of unbounded sign changes of `hardyZ` certifies that the set of
   non-trivial zeros of the Riemann zeta function on the critical line `Re(s) = 1 / 2` is infinite.
4. Equivalence with the infinitude of real zeros of Hardy's `Z`-function, followed by an
   unconditional proof of Hardy's theorem via Jacobi's theta transformation, Fourier inversion,
   and boundary vanishing of higher derivatives at `α → (π / 4)⁻`.
-/

@[expose] public section

open Complex Set Filter Topology

/-- Any subset of `ℝ` that contains elements arbitrarily far out is infinite. -/
theorem infinite_of_forall_exists_gt {s : Set ℝ} (h : ∀ T : ℝ, ∃ t ∈ s, T < t) :
    s.Infinite := by
  intro hfin
  have hbdd : BddAbove s := hfin.bddAbove
  rw [bddAbove_def] at hbdd
  rcases hbdd with ⟨B, hB⟩
  rcases h B with ⟨t, ht_mem, ht_gt⟩
  have hle : t ≤ B := hB t ht_mem
  linarith

/-- Intermediate value certification of non-trivial critical-line zeros via Hardy's `Z`-function:
if `hardyZ` changes sign on `[a, b]`, then `riemannZeta` has a zero on the critical line. -/
theorem exists_criticalLine_zero_of_hardyZ_sign_change {a b : ℝ} (hab : a ≤ b)
    (hsign : hardyZ a * hardyZ b ≤ 0) :
    ∃ t₀ ∈ Set.Icc a b, (criticalLine t₀).re = 1 / 2 ∧ riemannZeta (criticalLine t₀) = 0 := by
  have hzero : ∀ t ∈ Set.Icc a b, hardyZ t = 0 → riemannZeta (criticalLine t) = 0 := by
    intro t _ ht
    have heq : criticalLine t = 1 / 2 + (t : ℂ) * I := by
      simp only [criticalLine]
      ring
    rw [heq]
    exact (hardyZ_eq_zero_iff t).mp ht
  exact exists_criticalLine_zero_of_sign_change hab continuous_hardyZ.continuousOn hzero hsign

/-- Hardy's (1914) Landmark Theorem (conditional sign-change form):
if Hardy's `Z`-function has sign changes arbitrarily far out on `ℝ`, then the Riemann zeta function
has infinitely many non-trivial zeros on the critical line `Re(s) = 1 / 2`. -/
theorem infinite_criticalLine_zeros_of_sign_changes
    (h_sign : ∀ T : ℝ, ∃ a b : ℝ, T < a ∧ a ≤ b ∧ hardyZ a * hardyZ b ≤ 0) :
    {t : ℝ | riemannZeta (criticalLine t) = 0}.Infinite := by
  apply _root_.infinite_of_forall_exists_gt
  intro T
  rcases h_sign T with ⟨a, b, hTa, hab, hsign⟩
  rcases exists_criticalLine_zero_of_hardyZ_sign_change hab hsign with ⟨t₀, ht₀_mem, _, ht₀_zero⟩
  refine ⟨t₀, ht₀_zero, ?_⟩
  exact lt_of_lt_of_le hTa ht₀_mem.1

/-- The zero set of Hardy's `Z`-function on `ℝ` is infinite
whenever it has unbounded sign changes. -/
theorem infinite_hardyZ_zeros_of_sign_changes
    (h_sign : ∀ T : ℝ, ∃ a b : ℝ, T < a ∧ a ≤ b ∧ hardyZ a * hardyZ b ≤ 0) :
    {t : ℝ | hardyZ t = 0}.Infinite := by
  apply _root_.infinite_of_forall_exists_gt
  intro T
  rcases h_sign T with ⟨a, b, hTa, hab, hsign⟩
  have hz : ∃ t₀ ∈ Set.Icc a b, hardyZ t₀ = 0 := by
    rcases mul_nonpos_iff.mp hsign with ⟨h1, h2⟩ | ⟨h1, h2⟩
    · have hmem : (0 : ℝ) ∈ Set.Icc (hardyZ b) (hardyZ a) := ⟨h2, h1⟩
      have := intermediate_value_Icc' hab continuous_hardyZ.continuousOn hmem
      rcases this with ⟨t₀, ht₀, heq⟩
      exact ⟨t₀, ht₀, heq⟩
    · have hmem : (0 : ℝ) ∈ Set.Icc (hardyZ a) (hardyZ b) := ⟨h1, h2⟩
      have := intermediate_value_Icc hab continuous_hardyZ.continuousOn hmem
      rcases this with ⟨t₀, ht₀, heq⟩
      exact ⟨t₀, ht₀, heq⟩
  rcases hz with ⟨t₀, ht₀_mem, ht₀_zero⟩
  refine ⟨t₀, ht₀_zero, ?_⟩
  exact lt_of_lt_of_le hTa ht₀_mem.1

/-!
## Unconditional Infinitude of Critical-Line Zeros (Hardy 1914)

The remainder of this file formalizes Hardy's (1914) unconditional theorem proving that
`riemannZeta (criticalLine t)` and `hardyZ t` vanish at infinitely many `t : ℝ`.
-/

section UnconditionalHardy

open MeasureTheory HurwitzZeta
open scoped UpperHalfPlane FourierTransform RealInnerProductSpace

/-- Analytic strip kernel `Ψ(z) = exp(z/2) θ(i exp(2z)) - (exp(z/2) + exp(-z/2))`,
defined and holomorphic on the open strip `|z.im| < π / 4`. -/
noncomputable def hardyPsi (z : ℂ) : ℂ :=
  Complex.exp (z / 2) * jacobiTheta (I * Complex.exp (2 * z)) -
    (Complex.exp (z / 2) + Complex.exp (-z / 2))

private lemma im_I_mul_exp_two_mul_pos {z : ℂ} (hz : |z.im| < Real.pi / 4) :
    0 < (I * Complex.exp (2 * z)).im := by
  have him : (I * Complex.exp (2 * z)).im =
      Real.exp (2 * z.re) * Real.cos (2 * z.im) := by
    rw [Complex.mul_im, Complex.I_re, Complex.I_im, zero_mul, one_mul, zero_add,
      Complex.exp_re]
    simp
  rw [him]
  have hcos : 0 < Real.cos (2 * z.im) := by
    apply Real.cos_pos_of_mem_Ioo
    have h1 : -(Real.pi / 4) < z.im := (abs_lt.mp hz).1
    have h2 : z.im < Real.pi / 4 := (abs_lt.mp hz).2
    constructor <;> linarith
  exact mul_pos (Real.exp_pos _) hcos

private lemma differentiableAt_hardyPsi {z : ℂ} (hz : |z.im| < Real.pi / 4) :
    DifferentiableAt ℂ hardyPsi z := by
  have hθ := differentiableAt_jacobiTheta (im_I_mul_exp_two_mul_pos hz)
  have hτ : DifferentiableAt ℂ (fun w : ℂ => I * Complex.exp (2 * w)) z :=
    (differentiableAt_const _).mul ((differentiableAt_const (2 : ℂ)).mul differentiableAt_id).cexp
  have h1 : DifferentiableAt ℂ (fun w : ℂ => Complex.exp (w / 2)) z :=
    (differentiableAt_id.div_const 2).cexp
  have h2 : DifferentiableAt ℂ (fun w : ℂ => Complex.exp (-w / 2)) z :=
    (differentiableAt_id.neg.div_const 2).cexp
  have h3 : DifferentiableAt ℂ (jacobiTheta ∘ fun w : ℂ => I * Complex.exp (2 * w)) z :=
    hθ.comp z hτ
  change DifferentiableAt ℂ (fun w : ℂ =>
    Complex.exp (w / 2) * jacobiTheta (I * Complex.exp (2 * w)) -
      (Complex.exp (w / 2) + Complex.exp (-w / 2))) z
  exact (h1.mul h3).sub (h1.add h2)

private lemma hardyPsi_neg {z : ℂ} (hz : |z.im| < Real.pi / 4) :
    hardyPsi (-z) = hardyPsi z := by
  have him : 0 < (I * Complex.exp (2 * z)).im := im_I_mul_exp_two_mul_pos hz
  let τ : ℍ := ⟨I * Complex.exp (2 * z), him⟩
  have hS := jacobiTheta_S_smul τ
  have h_mod : ((ModularGroup.S • τ : ℍ) : ℂ) = I * Complex.exp (-2 * z) := by
    rw [UpperHalfPlane.modular_S_smul]
    change (-(τ : ℂ))⁻¹ = I * Complex.exp (-2 * z)
    rw [inv_neg]
    change -(I * Complex.exp (2 * z))⁻¹ = I * Complex.exp (-2 * z)
    rw [show -2 * z = -(2 * z) by ring, Complex.exp_neg, mul_inv,
      show -(I⁻¹ * (Complex.exp (2 * z))⁻¹) = (-I⁻¹) * (Complex.exp (2 * z))⁻¹ by ring,
      inv_I, neg_neg]
  have h_cpow : (-I * (τ : ℂ)) ^ (1 / 2 : ℂ) = Complex.exp z := by
    change (-I * (I * Complex.exp (2 * z))) ^ (1 / 2 : ℂ) = Complex.exp z
    have h_eq : -I * (I * Complex.exp (2 * z)) = Complex.exp (2 * z) := by
      rw [← mul_assoc, neg_mul, I_mul_I, neg_neg, one_mul]
    rw [h_eq, Complex.cpow_def_of_ne_zero (Complex.exp_ne_zero _)]
    have him2 : -(Real.pi) < (2 * z).im ∧ (2 * z).im ≤ Real.pi := by
      have h1 : -(Real.pi / 4) < z.im := (abs_lt.mp hz).1
      have h2 : z.im < Real.pi / 4 := (abs_lt.mp hz).2
      simp only [Complex.mul_im, Complex.re_ofNat, Complex.im_ofNat, zero_mul, add_zero]
      constructor <;> linarith [Real.pi_pos]
    rw [Complex.log_exp him2.1 him2.2]
    congr 1
    ring
  change jacobiTheta ((ModularGroup.S • τ : ℍ) : ℂ) =
    (-I * (τ : ℂ)) ^ (1 / 2 : ℂ) * jacobiTheta τ at hS
  rw [h_mod, h_cpow] at hS
  unfold hardyPsi
  rw [show 2 * -z = -2 * z by ring, hS, ← mul_assoc, ← Complex.exp_add,
    show -z / 2 + z = z / 2 by ring, neg_neg, add_comm (Complex.exp (-z / 2))]

private lemma norm_hardyPsi_le {α₀ : ℝ} (hα₀ : 0 ≤ α₀) (hα : α₀ < Real.pi / 4) :
    ∃ M > 0, ∀ z : ℂ, |z.im| ≤ α₀ → ‖hardyPsi z‖ ≤ M * Real.exp (-|z.re| / 2) := by
  have h_cos_pos : 0 < Real.cos (2 * α₀) := by
    apply Real.cos_pos_of_mem_Ioo
    constructor <;> linarith [Real.pi_pos]
  let c₀ : ℝ := Real.cos (2 * α₀)
  let c : ℝ := Real.pi * c₀
  have hc₀ : 0 < c₀ := h_cos_pos
  have hc : 0 < c := mul_pos Real.pi_pos hc₀
  have hc_lt : Real.exp (-c) < 1 := Real.exp_lt_one_iff.mpr (by linarith)
  let Cθ : ℝ := 2 / (1 - Real.exp (-c))
  have hCθ : 0 < Cθ := div_pos (by norm_num) (sub_pos.mpr hc_lt)
  let M : ℝ := Cθ * Real.exp (1 / (4 * c)) + 1
  have hM : 0 < M := by dsimp [M]; positivity
  refine ⟨M, hM, fun z hz => ?_⟩
  have h_nonneg : ∀ w : ℂ, 0 ≤ w.re → |w.im| ≤ α₀ →
      ‖hardyPsi w‖ ≤ M * Real.exp (-w.re / 2) := by
    intro w hw_re hw_im
    let τ : ℂ := I * Complex.exp (2 * w)
    have him_eq : τ.im = Real.exp (2 * w.re) * Real.cos (2 * w.im) := by
      dsimp [τ]
      rw [Complex.mul_im, Complex.I_re, Complex.I_im, zero_mul, one_mul, zero_add,
        Complex.exp_re]
      simp
    have h_cos_le : c₀ ≤ Real.cos (2 * w.im) := by
      have h_two_w : |2 * w.im| ≤ 2 * α₀ := by
        rw [abs_mul, abs_of_pos (by norm_num : (0 : ℝ) < 2)]
        linarith
      dsimp [c₀]
      rw [← Real.cos_abs (2 * w.im)]
      apply Real.strictAntiOn_cos.antitoneOn
      · exact ⟨abs_nonneg _, by linarith [Real.pi_pos, h_two_w, hα]⟩
      · exact ⟨by linarith, by linarith [Real.pi_pos, hα]⟩
      · exact h_two_w
    have hτ_im_exp : c₀ * Real.exp (2 * w.re) ≤ τ.im := by
      rw [him_eq, mul_comm]
      exact mul_le_mul_of_nonneg_left h_cos_le (Real.exp_pos _).le
    have h_exp_ge : 1 ≤ Real.exp (2 * w.re) := Real.one_le_exp (by linarith)
    have hτ_pos : 0 < τ.im := lt_of_lt_of_le (mul_pos hc₀ (Real.exp_pos _)) hτ_im_exp
    have h_pi_τ_exp : c * Real.exp (2 * w.re) ≤ Real.pi * τ.im := by
      dsimp [c]
      calc Real.pi * c₀ * Real.exp (2 * w.re)
          = Real.pi * (c₀ * Real.exp (2 * w.re)) := by ring
        _ ≤ Real.pi * τ.im := mul_le_mul_of_nonneg_left hτ_im_exp Real.pi_pos.le
    have h_pi_τ : c ≤ Real.pi * τ.im := by
      calc c = c * 1 := (mul_one c).symm
        _ ≤ c * Real.exp (2 * w.re) := mul_le_mul_of_nonneg_left h_exp_ge hc.le
        _ ≤ Real.pi * τ.im := h_pi_τ_exp
    have h_theta := norm_jacobiTheta_sub_one_le hτ_pos
    have h_exp_le : Real.exp (-Real.pi * τ.im) ≤ Real.exp (-c * Real.exp (2 * w.re)) := by
      rw [Real.exp_le_exp]
      linarith
    have h_den_le : 2 / (1 - Real.exp (-Real.pi * τ.im)) ≤ Cθ := by
      dsimp [Cθ]
      have h1 : Real.exp (-Real.pi * τ.im) ≤ Real.exp (-c) := by
        rw [Real.exp_le_exp]
        linarith
      have h_pos1 : 0 < 1 - Real.exp (-Real.pi * τ.im) :=
        sub_pos.mpr (Real.exp_lt_one_iff.mpr (by linarith [Real.pi_pos, hτ_pos]))
      gcongr
    have h_theta_bound : ‖jacobiTheta τ - 1‖ ≤ Cθ * Real.exp (-c * Real.exp (2 * w.re)) :=
      h_theta.trans (mul_le_mul h_den_le h_exp_le (Real.exp_pos _).le hCθ.le)
    have h_decomp : hardyPsi w =
        Complex.exp (w / 2) * (jacobiTheta τ - 1) - Complex.exp (-w / 2) := by
      unfold hardyPsi
      dsimp [τ]
      ring
    have h_norm1 : ‖Complex.exp (w / 2) * (jacobiTheta τ - 1)‖ ≤
        Cθ * Real.exp (1 / (4 * c)) * Real.exp (-w.re / 2) := by
      rw [norm_mul, Complex.norm_exp, show (w / 2).re = w.re / 2 by simp]
      have h_sq_exp : w.re ^ 2 ≤ Real.exp (2 * w.re) := by
        have h1 : w.re + 1 ≤ Real.exp w.re := Real.add_one_le_exp w.re
        have h2 : (w.re + 1) ^ 2 ≤ Real.exp w.re ^ 2 := by nlinarith
        have h3 : Real.exp w.re ^ 2 = Real.exp (2 * w.re) := by
          rw [sq, ← Real.exp_add, two_mul]
        nlinarith
      have h_quad : w.re - c * Real.exp (2 * w.re) ≤ 1 / (4 * c) := by
        have h_comp : c * w.re ^ 2 - w.re + 1 / (4 * c) = c * (w.re - 1 / (2 * c)) ^ 2 := by
          field_simp [hc.ne']; ring
        have h_nn : 0 ≤ c * (w.re - 1 / (2 * c)) ^ 2 := mul_nonneg hc.le (sq_nonneg _)
        have h_mul : c * w.re ^ 2 ≤ c * Real.exp (2 * w.re) :=
          mul_le_mul_of_nonneg_left h_sq_exp hc.le
        linarith
      calc Real.exp (w.re / 2) * ‖jacobiTheta τ - 1‖
          ≤ Real.exp (w.re / 2) * (Cθ * Real.exp (-c * Real.exp (2 * w.re))) :=
            mul_le_mul_of_nonneg_left h_theta_bound (Real.exp_pos _).le
        _ = Cθ * Real.exp (w.re / 2 + -c * Real.exp (2 * w.re)) := by
            rw [mul_left_comm, ← Real.exp_add]
        _ ≤ Cθ * Real.exp (1 / (4 * c) - w.re / 2) := by
            gcongr; linarith
        _ = Cθ * Real.exp (1 / (4 * c)) * Real.exp (-w.re / 2) := by
            rw [sub_eq_add_neg, show -(w.re / 2) = -w.re / 2 by ring, Real.exp_add, mul_assoc]
    have h_norm2 : ‖Complex.exp (-w / 2)‖ = Real.exp (-w.re / 2) := by
      rw [Complex.norm_exp, show (-w / 2).re = -w.re / 2 by simp]
    rw [h_decomp]
    calc ‖Complex.exp (w / 2) * (jacobiTheta τ - 1) - Complex.exp (-w / 2)‖
        ≤ ‖Complex.exp (w / 2) * (jacobiTheta τ - 1)‖ + ‖Complex.exp (-w / 2)‖ :=
          norm_sub_le _ _
      _ ≤ Cθ * Real.exp (1 / (4 * c)) * Real.exp (-w.re / 2) + Real.exp (-w.re / 2) :=
          add_le_add h_norm1 h_norm2.le
      _ = M * Real.exp (-w.re / 2) := by dsimp [M]; ring
  by_cases hre : 0 ≤ z.re
  · rw [abs_of_nonneg hre]
    exact h_nonneg z hre hz
  · have hre_neg : 0 ≤ (-z).re := by simp; linarith
    have him_neg : |(-z).im| ≤ α₀ := by simpa using hz
    have h_abs : |z.re| = (-z).re := by simp [abs_of_neg (lt_of_not_ge hre)]
    rw [← hardyPsi_neg (lt_of_le_of_lt hz hα), h_abs]
    exact h_nonneg (-z) hre_neg him_neg

private lemma integrable_hardyPsi_shift {α : ℝ} (hα : |α| < Real.pi / 4) :
    Integrable (fun u : ℝ => hardyPsi ((u : ℂ) + I * (α : ℂ))) := by
  obtain ⟨M, hM_pos, hM⟩ := norm_hardyPsi_le (abs_nonneg α) hα
  have hcont : Continuous (fun u : ℝ => hardyPsi ((u : ℂ) + I * (α : ℂ))) := by
    rw [continuous_iff_continuousAt]
    intro u
    have him : |((u : ℂ) + I * (α : ℂ)).im| < Real.pi / 4 := by simpa using hα
    have h_arg : ContinuousAt (fun v : ℝ => (v : ℂ) + I * (α : ℂ)) u :=
      (Complex.continuous_ofReal.add continuous_const).continuousAt
    have h_f : ContinuousAt hardyPsi ((fun v : ℝ => (v : ℂ) + I * (α : ℂ)) u) :=
      (differentiableAt_hardyPsi him).continuousAt
    exact h_f.comp (f := fun v : ℝ => (v : ℂ) + I * (α : ℂ)) h_arg
  have hdom : Integrable (fun u : ℝ => M * Real.exp (-|u| / 2)) := by
    have h1 : IntegrableOn (fun u : ℝ => M * Real.exp (-(1 / 2 : ℝ) * u)) (Ioi 0) :=
      (integrableOn_exp_mul_Ioi (by norm_num : -(1 / 2 : ℝ) < 0) 0).const_mul M
    have h2 : IntegrableOn (fun u : ℝ => M * Real.exp ((1 / 2 : ℝ) * u)) (Iic 0) :=
      (integrableOn_exp_mul_Iic (by norm_num : (0 : ℝ) < 1 / 2) 0).const_mul M
    rw [← integrableOn_univ, ← Iic_union_Ioi (a := (0 : ℝ)), integrableOn_union]
    refine ⟨h2.congr_fun (fun u hu => ?_) measurableSet_Iic,
        h1.congr_fun (fun u hu => ?_) measurableSet_Ioi⟩
    · simp only [abs_of_nonpos (mem_Iic.mp hu)]; ring_nf
    · simp only [abs_of_pos (mem_Ioi.mp hu)]; ring_nf
  refine hdom.mono hcont.aestronglyMeasurable (ae_of_all _ fun u => ?_)
  have him : |((u : ℂ) + I * (α : ℂ)).im| ≤ |α| := by simp
  have hre : ((u : ℂ) + I * (α : ℂ)).re = u := by simp
  calc ‖hardyPsi ((u : ℂ) + I * (α : ℂ))‖
      ≤ M * Real.exp (-|((u : ℂ) + I * (α : ℂ)).re| / 2) := hM _ him
    _ = M * Real.exp (-|u| / 2) := by rw [hre]
    _ = ‖M * Real.exp (-|u| / 2)‖ := by
        rw [Real.norm_of_nonneg (mul_nonneg hM_pos.le (Real.exp_pos _).le)]

private lemma integral_cexp_neg_half_abs_mul (t : ℝ) :
    ∫ u : ℝ, Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I) =
      1 / (1 / 2 + (t : ℂ) * I) + 1 / (1 - (1 / 2 + (t : ℂ) * I)) := by
  let c₁ : ℂ := -(1 / 2 : ℂ) + (t : ℂ) * I
  let c₂ : ℂ := -(1 / 2 : ℂ) - (t : ℂ) * I
  have hc₁_re : c₁.re < 0 := by simp [c₁]
  have hc₂_re : c₂.re < 0 := by simp [c₂]
  have hc₂_neg_re : 0 < (-c₂).re := by simp [c₂]
  have hc₁_ne : c₁ ≠ 0 := fun h => by rw [h] at hc₁_re; simp at hc₁_re
  have hc₂_ne : c₂ ≠ 0 := fun h => by rw [h] at hc₂_re; simp at hc₂_re
  have hint_Ioi : ∫ u in Ioi (0 : ℝ), Complex.exp (c₁ * u) = -1 / c₁ := by
    have h_ten := intervalIntegral_tendsto_integral_Ioi (a := (0 : ℝ))
      (f := fun u : ℝ => Complex.exp (c₁ * u))
      (integrableOn_exp_mul_complex_Ioi hc₁_re 0) tendsto_id
    simp only [id_eq] at h_ten
    have h_ev : (fun b : ℝ => ∫ u in (0 : ℝ)..b, Complex.exp (c₁ * u)) =
        fun b : ℝ => (Complex.exp (c₁ * b) - 1) / c₁ := by
      ext b
      rw [integral_exp_mul_complex hc₁_ne, Complex.ofReal_zero, mul_zero, Complex.exp_zero]
    rw [h_ev] at h_ten
    have h_lim : Tendsto (fun b : ℝ => (Complex.exp (c₁ * b) - 1) / c₁) atTop (nhds (-1 / c₁)) := by
      have ht0 : Tendsto (fun b : ℝ => Complex.exp (c₁ * b)) atTop (nhds 0) := by
        rw [tendsto_zero_iff_norm_tendsto_zero]
        simp_rw [Complex.norm_exp, show ∀ b : ℝ, (c₁ * (b : ℂ)).re = c₁.re * b by
          intro b; simp [Complex.mul_re]]
        exact Real.tendsto_exp_atBot.comp (tendsto_id.const_mul_atTop_of_neg hc₁_re)
      simpa [zero_sub] using (ht0.sub tendsto_const_nhds).div_const c₁
    exact tendsto_nhds_unique h_ten h_lim
  have hint_Iic : ∫ u in Iic (0 : ℝ), Complex.exp (-c₂ * u) = -1 / c₂ := by
    have h_fn : (fun u : ℝ => Complex.exp (-c₂ * u)) =
        fun u : ℝ => (fun x : ℝ => Complex.exp (c₂ * (x : ℂ))) (-u) := by
      ext u; push_cast; congr 1; ring
    rw [h_fn, integral_comp_neg_Iic 0 (fun x : ℝ => Complex.exp (c₂ * (x : ℂ))), neg_zero]
    have h_ten := intervalIntegral_tendsto_integral_Ioi (a := (0 : ℝ))
      (f := fun u : ℝ => Complex.exp (c₂ * u))
      (integrableOn_exp_mul_complex_Ioi hc₂_re 0) tendsto_id
    simp only [id_eq] at h_ten
    have h_ev : (fun b : ℝ => ∫ u in (0 : ℝ)..b, Complex.exp (c₂ * u)) =
        fun b : ℝ => (Complex.exp (c₂ * b) - 1) / c₂ := by
      ext b
      rw [integral_exp_mul_complex hc₂_ne, Complex.ofReal_zero, mul_zero, Complex.exp_zero]
    rw [h_ev] at h_ten
    have h_lim : Tendsto (fun b : ℝ => (Complex.exp (c₂ * b) - 1) / c₂) atTop
        (nhds (-1 / c₂)) := by
      have ht0 : Tendsto (fun b : ℝ => Complex.exp (c₂ * b)) atTop (nhds 0) := by
        rw [tendsto_zero_iff_norm_tendsto_zero]
        simp_rw [Complex.norm_exp, show ∀ b : ℝ, (c₂ * (b : ℂ)).re = c₂.re * b by
          intro b; simp [Complex.mul_re]]
        exact Real.tendsto_exp_atBot.comp (tendsto_id.const_mul_atTop_of_neg hc₂_re)
      simpa [zero_sub] using (ht0.sub tendsto_const_nhds).div_const c₂
    exact tendsto_nhds_unique h_ten h_lim
  have h_split_int :
      ∫ u : ℝ, Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I) =
      (∫ u in Iic (0 : ℝ), Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I)) +
      (∫ u in Ioi (0 : ℝ), Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I)) := by
    have h_int_Iic : IntegrableOn
        (fun u : ℝ => Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I))
        (Iic 0) := by
      refine (integrableOn_exp_mul_complex_Iic hc₂_neg_re 0).congr_fun
        (fun u hu => ?_) measurableSet_Iic
      rw [← Complex.exp_add, abs_of_nonpos (mem_Iic.mp hu)]
      dsimp [c₂]; push_cast; ring_nf
    have h_int_Ioi : IntegrableOn
        (fun u : ℝ => Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I))
        (Ioi 0) := by
      refine (integrableOn_exp_mul_complex_Ioi hc₁_re 0).congr_fun
        (fun u hu => ?_) measurableSet_Ioi
      rw [← Complex.exp_add, abs_of_pos (mem_Ioi.mp hu)]
      dsimp [c₁]; ring_nf
    rw [← MeasureTheory.setIntegral_union (Iic_disjoint_Ioi (le_refl (0 : ℝ))) measurableSet_Ioi
      h_int_Iic h_int_Ioi, Iic_union_Ioi, setIntegral_univ]
  have h1_eq :
      ∫ u in Iic (0 : ℝ), Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I) =
      ∫ u in Iic (0 : ℝ), Complex.exp (-c₂ * u) := by
    refine setIntegral_congr_fun measurableSet_Iic fun u hu => ?_
    rw [← Complex.exp_add, abs_of_nonpos (mem_Iic.mp hu)]
    congr 1; dsimp [c₂]; push_cast; ring
  have h2_eq :
      ∫ u in Ioi (0 : ℝ), Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I) =
      ∫ u in Ioi (0 : ℝ), Complex.exp (c₁ * u) := by
    refine setIntegral_congr_fun measurableSet_Ioi fun u hu => ?_
    rw [← Complex.exp_add, abs_of_pos (mem_Ioi.mp hu)]
    congr 1; dsimp [c₁]; ring
  rw [h_split_int, h1_eq, h2_eq, hint_Iic, hint_Ioi]
  have hc₂_neg : -c₂ = 1 / 2 + (t : ℂ) * I := by dsimp [c₂]; ring
  have hc₁_neg : -c₁ = 1 - (1 / 2 + (t : ℂ) * I) := by dsimp [c₁]; ring
  have h_eq1 : -1 / c₂ = 1 / (1 / 2 + (t : ℂ) * I) := by
    rw [← hc₂_neg, neg_div, div_neg]
  have h_eq2 : -1 / c₁ = 1 / (1 - (1 / 2 + (t : ℂ) * I)) := by
    rw [← hc₁_neg, neg_div, div_neg]
  rw [h_eq1, h_eq2]

private lemma completedRiemannZeta_half_add_mul_I_eq_fourier (t : ℝ) :
    completedRiemannZeta (1 / 2 + (t : ℂ) * I) =
      ∫ u : ℝ, hardyPsi (u : ℂ) * Complex.exp ((t : ℂ) * u * I) := by
  have h_zeta_eq := completedRiemannZeta_eq (1 / 2 + (t : ℂ) * I)
  have h_Λ₀ : completedRiemannZeta₀ (1 / 2 + (t : ℂ) * I) =
      (mellin (hurwitzEvenFEPair 0).f_modif ((1 / 2 + (t : ℂ) * I) / 2)) / 2 := by
    rw [completedRiemannZeta₀, HurwitzZeta.completedHurwitzZetaEven₀, WeakFEPair.Λ₀]
  have h_mellin : (mellin (hurwitzEvenFEPair 0).f_modif ((1 / 2 + (t : ℂ) * I) / 2)) / 2 =
      ∫ u : ℝ, (hardyPsi (u : ℂ) + Complex.exp (-((|u| : ℝ) : ℂ) / 2)) *
        Complex.exp ((t : ℂ) * u * I) := by
    rw [mellin]
    have h_comp : ∫ y in Ioi (0 : ℝ),
        (y : ℂ) ^ ((1 / 2 + (t : ℂ) * I) / 2 - 1) • (hurwitzEvenFEPair 0).f_modif y =
        ∫ x : ℝ, (Real.exp x : ℂ) * ((Real.exp x : ℂ) ^ ((1 / 2 + (t : ℂ) * I) / 2 - 1) •
          (hurwitzEvenFEPair 0).f_modif (Real.exp x)) := by
      symm
      simpa [Complex.real_smul] using
        integral_comp_exp (fun y : ℝ =>
          (y : ℂ) ^ ((1 / 2 + (t : ℂ) * I) / 2 - 1) • (hurwitzEvenFEPair 0).f_modif y)
    have h_scale : (∫ x : ℝ, (Real.exp x : ℂ) *
        ((Real.exp x : ℂ) ^ ((1 / 2 + (t : ℂ) * I) / 2 - 1) •
          (hurwitzEvenFEPair 0).f_modif (Real.exp x))) / 2 =
        ∫ u : ℝ, (Real.exp (2 * u) : ℂ) *
          ((Real.exp (2 * u) : ℂ) ^ ((1 / 2 + (t : ℂ) * I) / 2 - 1) •
            (hurwitzEvenFEPair 0).f_modif (Real.exp (2 * u))) := by
      rw [Measure.integral_comp_mul_left (fun x : ℝ => (Real.exp x : ℂ) *
        ((Real.exp x : ℂ) ^ ((1 / 2 + (t : ℂ) * I) / 2 - 1) •
          (hurwitzEvenFEPair 0).f_modif (Real.exp x))) (2 : ℝ),
        abs_of_pos (inv_pos.mpr (by norm_num : (0 : ℝ) < 2)), Complex.real_smul]
      push_cast
      ring
    rw [h_comp, h_scale]
    refine integral_congr_ae ?_
    filter_upwards [compl_mem_ae_iff.mpr (Subsingleton.measure_zero (s := {(0 : ℝ)}) (by simp) _)]
      with u hu
    have hu0 : u ≠ 0 := hu
    have h_exp_pos : 0 < Real.exp (2 * u) := Real.exp_pos _
    have h_pow : (Real.exp (2 * u) : ℂ) *
        ((Real.exp (2 * u) : ℂ) ^ ((1 / 2 + (t : ℂ) * I) / 2 - 1)) =
        Complex.exp ((u : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I) := by
      rw [Complex.ofReal_exp, Complex.cpow_def_of_ne_zero (Complex.exp_ne_zero _),
        Complex.log_exp (by simp [Real.pi_pos]) (by simp [Real.pi_pos.le]),
        ← Complex.exp_add, ← Complex.exp_add]
      congr 1
      push_cast
      ring
    simp only [smul_eq_mul]
    rw [← mul_assoc, h_pow]
    have h_f_modif : (hurwitzEvenFEPair 0).f_modif (Real.exp (2 * u)) =
        if 0 < u then jacobiTheta (I * Complex.exp (2 * u)) - 1
        else jacobiTheta (I * Complex.exp (2 * u)) - Complex.exp (-(u : ℂ)) := by
      dsimp [WeakFEPair.f_modif, hurwitzEvenFEPair]
      have hek : ((evenKernel 0 (Real.exp (2 * u)) : ℝ) : ℂ) =
          jacobiTheta (I * Complex.exp (2 * u)) := by
        rw [evenKernel_eq_cosKernel_of_zero, ← QuotientAddGroup.mk_zero, cosKernel_def,
          Complex.ofReal_zero, Complex.ofReal_exp, ← jacobiTheta_eq_jacobiTheta₂]
        simp
      rcases lt_or_gt_of_ne hu0 with hlt | hgt
      · have hexp_lt1 : Real.exp (2 * u) < 1 := Real.exp_lt_one_iff.mpr (by linarith)
        have h_not : Real.exp (2 * u) ∉ Ioi (1 : ℝ) := fun h => absurd h (not_lt.mpr hexp_lt1.le)
        have h_in : Real.exp (2 * u) ∈ Ioo (0 : ℝ) 1 := ⟨h_exp_pos, hexp_lt1⟩
        have h_rpow : ((Real.exp (2 * u) ^ (-(1 / 2 : ℝ)) : ℝ) : ℂ) = Complex.exp (-(u : ℂ)) := by
          rw [← Real.exp_mul, show (2 * u) * -(1 / 2 : ℝ) = -u by ring, Complex.ofReal_exp,
            Complex.ofReal_neg]
        simp only [hlt.not_gt, ite_false, indicator_of_notMem h_not,
          indicator_of_mem h_in, zero_add, one_mul, mul_one]
        rw [hek, h_rpow]
      · have hexp_gt1 : 1 < Real.exp (2 * u) := Real.one_lt_exp_iff.mpr (by linarith)
        have h_in : Real.exp (2 * u) ∈ Ioi (1 : ℝ) := hexp_gt1
        have h_not : Real.exp (2 * u) ∉ Ioo (0 : ℝ) 1 :=
          fun h => absurd h.2 (not_lt.mpr hexp_gt1.le)
        simp only [hgt, ite_true, indicator_of_mem h_in, indicator_of_notMem h_not, add_zero]
        exact congrArg (· - 1) hek
    rw [h_f_modif]
    rcases lt_or_gt_of_ne hu0 with hlt | hgt
    · simp only [hlt.not_gt, ite_false]
      rw [abs_of_neg hlt]
      unfold hardyPsi
      rw [show -(((-u : ℝ) : ℂ)) / 2 = (u : ℂ) / 2 by push_cast; ring]
      have h_id1 : Complex.exp ((u : ℂ) / 2) * Complex.exp (-(u : ℂ)) =
          Complex.exp (-(u : ℂ) / 2) := by
        rw [← Complex.exp_add]; congr 1; ring
      calc (Complex.exp ((u : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I)) *
            (jacobiTheta (I * Complex.exp (2 * (u : ℂ))) - Complex.exp (-(u : ℂ)))
          = (Complex.exp ((u : ℂ) / 2) * jacobiTheta (I * Complex.exp (2 * (u : ℂ))) -
              Complex.exp ((u : ℂ) / 2) * Complex.exp (-(u : ℂ))) *
              Complex.exp ((t : ℂ) * u * I) := by ring
        _ = (Complex.exp ((u : ℂ) / 2) * jacobiTheta (I * Complex.exp (2 * (u : ℂ))) -
              Complex.exp (-(u : ℂ) / 2)) * Complex.exp ((t : ℂ) * u * I) := by
              rw [h_id1]
        _ = _ := by ring
    · simp only [hgt, ite_true]
      rw [abs_of_pos hgt]
      unfold hardyPsi
      ring
  have hint_psi : Integrable (fun u : ℝ => hardyPsi (u : ℂ) * Complex.exp ((t : ℂ) * u * I)) := by
    have h_raw := integrable_hardyPsi_shift (α := 0) (by simpa using Real.pi_pos)
    refine h_raw.mono ?_ (ae_of_all _ fun u => ?_)
    · exact ((continuous_iff_continuousAt.mpr fun u =>
        (differentiableAt_hardyPsi (by simpa using Real.pi_pos)).continuousAt.comp
          Complex.continuous_ofReal.continuousAt).mul (by fun_prop)).aestronglyMeasurable
    · rw [norm_mul, show ‖Complex.exp ((t : ℂ) * u * I)‖ = 1 by
        rw [Complex.norm_exp]; simp [Complex.mul_re]]
      simp
  have hint_exp : Integrable
      (fun u : ℝ => Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I)) := by
    have h1 : IntegrableOn
        (fun u : ℝ => Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I))
        (Iic 0) := by
      refine (integrableOn_exp_mul_complex_Iic
          (by simp : (0 : ℝ) < (1 / 2 + (t : ℂ) * I).re) 0).congr_fun
        (fun u hu => ?_) measurableSet_Iic
      rw [← Complex.exp_add, abs_of_nonpos (mem_Iic.mp hu)]
      push_cast; ring_nf
    have h2 : IntegrableOn
        (fun u : ℝ => Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I))
        (Ioi 0) := by
      refine (integrableOn_exp_mul_complex_Ioi
          (by simp : (-(1 / 2 : ℂ) + (t : ℂ) * I).re < 0) 0).congr_fun
        (fun u hu => ?_) measurableSet_Ioi
      rw [← Complex.exp_add, abs_of_pos (mem_Ioi.mp hu)]
      ring_nf
    rw [← integrableOn_univ, ← Iic_union_Ioi (a := (0 : ℝ)), integrableOn_union]
    exact ⟨h1, h2⟩
  have h_add : ∫ u : ℝ, (hardyPsi (u : ℂ) + Complex.exp (-((|u| : ℝ) : ℂ) / 2)) *
        Complex.exp ((t : ℂ) * u * I) =
      (∫ u : ℝ, hardyPsi (u : ℂ) * Complex.exp ((t : ℂ) * u * I)) +
      (∫ u : ℝ, Complex.exp (-((|u| : ℝ) : ℂ) / 2) * Complex.exp ((t : ℂ) * u * I)) := by
    simp_rw [add_mul]
    exact integral_add hint_psi hint_exp
  rw [h_zeta_eq, h_Λ₀, h_mellin, h_add, integral_cexp_neg_half_abs_mul t]
  ring

private lemma integrable_hardyPsi_shift_mul_cexp (t : ℝ) {α : ℝ} (hα : |α| < Real.pi / 4) :
    Integrable (fun u : ℝ =>
      hardyPsi ((u : ℂ) + (α : ℂ) * I) * Complex.exp ((t : ℂ) * ((u : ℂ) + (α : ℂ) * I) * I)) := by
  have hcont : Continuous (fun u : ℝ =>
      hardyPsi ((u : ℂ) + (α : ℂ) * I) * Complex.exp ((t : ℂ) * ((u : ℂ) + (α : ℂ) * I) * I)) := by
    rw [continuous_iff_continuousAt]
    intro u
    have him : |((u : ℂ) + (α : ℂ) * I).im| < Real.pi / 4 := by simpa using hα
    have h_arg : ContinuousAt (fun v : ℝ => (v : ℂ) + (α : ℂ) * I) u :=
      (Complex.continuous_ofReal.add continuous_const).continuousAt
    have h_f : ContinuousAt hardyPsi ((fun v : ℝ => (v : ℂ) + (α : ℂ) * I) u) :=
      (differentiableAt_hardyPsi him).continuousAt
    exact (h_f.comp (f := fun v : ℝ => (v : ℂ) + (α : ℂ) * I) h_arg).mul (by fun_prop)
  have hraw := integrable_hardyPsi_shift hα
  have hdom : Integrable (fun u : ℝ => Real.exp (-t * α) * ‖hardyPsi ((u : ℂ) + I * (α : ℂ))‖) :=
    hraw.norm.const_mul (Real.exp (-t * α))
  refine hdom.mono hcont.aestronglyMeasurable (ae_of_all _ fun u => ?_)
  have hnorm : ‖Complex.exp ((t : ℂ) * ((u : ℂ) + (α : ℂ) * I) * I)‖ = Real.exp (-t * α) := by
    rw [Complex.norm_exp]
    have hre : ((t : ℂ) * ((u : ℂ) + (α : ℂ) * I) * I).re = -t * α := by
      simp [Complex.mul_re, Complex.mul_im]
    rw [hre]
  rw [norm_mul, hnorm, mul_comm (α : ℂ) I, mul_comm _ (Real.exp (-t * α))]
  exact (le_abs_self _).trans_eq (Real.norm_eq_abs _).symm

private lemma completedRiemannZeta_half_add_mul_I_eq_shift (t : ℝ) {α : ℝ}
    (hα : |α| < Real.pi / 4) :
    completedRiemannZeta (1 / 2 + (t : ℂ) * I) =
      ∫ u : ℝ,
        hardyPsi ((u : ℂ) + (α : ℂ) * I) *
          Complex.exp ((t : ℂ) * ((u : ℂ) + (α : ℂ) * I) * I) := by
  let F : ℂ → ℂ := fun z => hardyPsi z * Complex.exp ((t : ℂ) * z * I)
  have hrect : ∀ R : ℝ,
      (∫ x in (-R)..R, F (x : ℂ)) - (∫ x in (-R)..R, F ((x : ℂ) + (α : ℂ) * I)) +
        I • (∫ y in (0 : ℝ)..α, F ((R : ℂ) + (y : ℂ) * I)) -
        I • (∫ y in (0 : ℝ)..α, F ((-R : ℂ) + (y : ℂ) * I)) = 0 := by
    intro R
    have hdiff : DifferentiableOn ℂ F
        (uIcc (-(R : ℂ)).re ((R : ℂ) + (α : ℂ) * I).re ×ℂ
          uIcc (-(R : ℂ)).im ((R : ℂ) + (α : ℂ) * I).im) := by
      intro z hz
      have hzim : |z.im| < Real.pi / 4 := by
        have him : z.im ∈ uIcc 0 α := by simpa using hz.2
        have h_abs : |z.im| ≤ |α| := by
          rcases mem_uIcc.mp him with ⟨h1, h2⟩ | ⟨h1, h2⟩
          · exact abs_le.mpr ⟨by linarith [abs_nonneg α], h2.trans (le_abs_self α)⟩
          · exact abs_le.mpr ⟨by linarith [neg_le_abs α], h2.trans (abs_nonneg α)⟩
        exact lt_of_le_of_lt h_abs hα
      exact ((differentiableAt_hardyPsi hzim).mul
        (((differentiableAt_const _).mul differentiableAt_id).mul
          (differentiableAt_const _)).cexp).differentiableWithinAt
    have hcauchy := Complex.integral_boundary_rect_eq_zero_of_differentiableOn
      F (-(R : ℂ)) ((R : ℂ) + (α : ℂ) * I) hdiff
    simpa [Complex.ofReal_neg, Complex.neg_re, Complex.ofReal_re, Complex.ofReal_im,
      Complex.add_re, Complex.add_im, Complex.mul_re, Complex.mul_im] using hcauchy
  obtain ⟨M, hM_pos, hM⟩ := norm_hardyPsi_le (abs_nonneg α) hα
  have hV_bound : ∀ R : ℝ, 0 ≤ R → ∀ x : ℝ, |x| = R →
      ‖I • ∫ y in (0 : ℝ)..α, F ((x : ℂ) + (y : ℂ) * I)‖ ≤
        M * Real.exp (|t| * |α|) * |α| * Real.exp (-R / 2) := by
    intro R _ x hxR
    have h_side : ∀ y ∈ uIoc (0 : ℝ) α,
        ‖F ((x : ℂ) + (y : ℂ) * I)‖ ≤ M * Real.exp (|t| * |α|) * Real.exp (-R / 2) := by
      intro y hy
      have hy_uIcc : y ∈ uIcc 0 α := uIoc_subset_uIcc hy
      have hy_abs : |y| ≤ |α| := by
        rcases mem_uIcc.mp hy_uIcc with ⟨h1, h2⟩ | ⟨h1, h2⟩
        · exact abs_le.mpr ⟨by linarith [abs_nonneg α], h2.trans (le_abs_self α)⟩
        · exact abs_le.mpr ⟨by linarith [neg_le_abs α], h2.trans (abs_nonneg α)⟩
      have hψ := hM ((x : ℂ) + (y : ℂ) * I) (by simpa using hy_abs)
      have h_exp : ‖Complex.exp ((t : ℂ) * ((x : ℂ) + (y : ℂ) * I) * I)‖ ≤
          Real.exp (|t| * |α|) := by
        rw [Complex.norm_exp, show ((t : ℂ) * ((x : ℂ) + (y : ℂ) * I) * I).re = -t * y by
          simp [Complex.mul_re, Complex.mul_im]]
        rw [Real.exp_le_exp]
        have h1 : -t * y ≤ |t| * |y| := by
          calc -t * y ≤ |-t * y| := le_abs_self _
            _ = |t| * |y| := by rw [abs_mul, abs_neg]
        exact h1.trans (mul_le_mul_of_nonneg_left hy_abs (abs_nonneg t))
      have hre : |((x : ℂ) + (y : ℂ) * I).re| = R := by simpa using hxR
      rw [hre] at hψ
      dsimp [F]
      rw [norm_mul]
      calc ‖hardyPsi ((x : ℂ) + (y : ℂ) * I)‖ *
            ‖Complex.exp ((t : ℂ) * ((x : ℂ) + (y : ℂ) * I) * I)‖
          ≤ (M * Real.exp (-R / 2)) * Real.exp (|t| * |α|) :=
            mul_le_mul hψ h_exp (norm_nonneg _) (mul_nonneg hM_pos.le (Real.exp_pos _).le)
        _ = M * Real.exp (|t| * |α|) * Real.exp (-R / 2) := by ring
    have hint := intervalIntegral.norm_integral_le_of_norm_le_const h_side
    rw [sub_zero] at hint
    rw [norm_smul, Complex.norm_I, one_mul]
    calc ‖∫ y in (0 : ℝ)..α, F ((x : ℂ) + (y : ℂ) * I)‖
        ≤ M * Real.exp (|t| * |α|) * Real.exp (-R / 2) * |α| := hint
      _ = M * Real.exp (|t| * |α|) * |α| * Real.exp (-R / 2) := by ring
  have hVR : Tendsto (fun R : ℝ => I • ∫ y in (0 : ℝ)..α, F ((R : ℂ) + (y : ℂ) * I))
      atTop (nhds 0) := by
    rw [tendsto_zero_iff_norm_tendsto_zero]
    refine squeeze_zero'
      (g := fun R : ℝ => M * Real.exp (|t| * |α|) * |α| * Real.exp (-R / 2))
      (Eventually.of_forall fun _ => norm_nonneg _) ?_ ?_
    · filter_upwards [eventually_ge_atTop 0] with R hR
      exact hV_bound R hR R (abs_of_nonneg hR)
    · have ht : Tendsto (fun R : ℝ => Real.exp (-R / 2)) atTop (nhds 0) := by
        refine (Real.tendsto_exp_atBot.comp
          (tendsto_id.const_mul_atTop_of_neg (by norm_num : -(1 / 2 : ℝ) < 0))).congr
          (fun R => ?_)
        dsimp only [Function.comp_def, id_eq]; congr 1; ring
      simpa [mul_zero] using ht.const_mul (M * Real.exp (|t| * |α|) * |α|)
  have hVL : Tendsto (fun R : ℝ => I • ∫ y in (0 : ℝ)..α, F ((-R : ℂ) + (y : ℂ) * I))
      atTop (nhds 0) := by
    rw [tendsto_zero_iff_norm_tendsto_zero]
    refine squeeze_zero'
      (g := fun R : ℝ => M * Real.exp (|t| * |α|) * |α| * Real.exp (-R / 2))
      (Eventually.of_forall fun _ => norm_nonneg _) ?_ ?_
    · filter_upwards [eventually_ge_atTop 0] with R hR
      simpa [Complex.ofReal_neg] using hV_bound R hR (-R) (by rw [abs_neg, abs_of_nonneg hR])
    · have ht : Tendsto (fun R : ℝ => Real.exp (-R / 2)) atTop (nhds 0) := by
        refine (Real.tendsto_exp_atBot.comp
          (tendsto_id.const_mul_atTop_of_neg (by norm_num : -(1 / 2 : ℝ) < 0))).congr
          (fun R => ?_)
        dsimp only [Function.comp_def, id_eq]; congr 1; ring
      simpa [mul_zero] using ht.const_mul (M * Real.exp (|t| * |α|) * |α|)
  have hbot_int : Integrable (fun x : ℝ => F (x : ℂ)) := by
    simpa [F] using integrable_hardyPsi_shift_mul_cexp t (α := 0) (by simpa using Real.pi_pos)
  have htop_int : Integrable (fun x : ℝ => F ((x : ℂ) + (α : ℂ) * I)) :=
    integrable_hardyPsi_shift_mul_cexp t hα
  have hbot_ten := intervalIntegral_tendsto_integral hbot_int tendsto_neg_atTop_atBot tendsto_id
  have htop_ten := intervalIntegral_tendsto_integral htop_int tendsto_neg_atTop_atBot tendsto_id
  simp only [id_eq] at hbot_ten htop_ten
  have hcomb : Tendsto (fun R : ℝ =>
      (∫ x in (-R)..R, F (x : ℂ)) +
        (I • (∫ y in (0 : ℝ)..α, F ((R : ℂ) + (y : ℂ) * I)) -
          I • (∫ y in (0 : ℝ)..α, F ((-R : ℂ) + (y : ℂ) * I))))
      atTop (nhds ((∫ x : ℝ, F (x : ℂ)) + (0 - 0))) :=
    hbot_ten.add (hVR.sub hVL)
  have h_eq_fn : (fun R : ℝ => ∫ x in (-R)..R, F ((x : ℂ) + (α : ℂ) * I)) =
      fun R : ℝ =>
        (∫ x in (-R)..R, F (x : ℂ)) +
          (I • (∫ y in (0 : ℝ)..α, F ((R : ℂ) + (y : ℂ) * I)) -
            I • (∫ y in (0 : ℝ)..α, F ((-R : ℂ) + (y : ℂ) * I))) := by
    ext R
    have h0 := hrect R
    linear_combination -h0
  rw [sub_zero, add_zero, ← h_eq_fn] at hcomb
  have h_int_eq := tendsto_nhds_unique hcomb htop_ten
  rw [completedRiemannZeta_half_add_mul_I_eq_fourier t]
  exact h_int_eq

private lemma norm_completedRiemannZeta_criticalLine_le {α₀ : ℝ}
    (hα₀ : 0 ≤ α₀) (hα : α₀ < Real.pi / 4) :
    ∃ C > 0, ∀ t : ℝ,
      ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖ ≤ C * Real.exp (-α₀ * |t|) := by
  let I_int : ℝ := ∫ u : ℝ, ‖hardyPsi ((u : ℂ) + I * (α₀ : ℂ))‖
  have hI_nonneg : 0 ≤ I_int := integral_nonneg fun _ => norm_nonneg _
  refine ⟨I_int + 1, by linarith, fun t => ?_⟩
  by_cases ht : 0 ≤ t
  · have hα_abs : |α₀| < Real.pi / 4 := by rwa [abs_of_nonneg hα₀]
    rw [completedRiemannZeta_half_add_mul_I_eq_shift t hα_abs, abs_of_nonneg ht]
    have hint := norm_integral_le_integral_norm (μ := volume)
      (fun u : ℝ => hardyPsi ((u : ℂ) + (α₀ : ℂ) * I) *
        Complex.exp ((t : ℂ) * ((u : ℂ) + (α₀ : ℂ) * I) * I))
    have h_eq : ∫ u : ℝ, ‖hardyPsi ((u : ℂ) + (α₀ : ℂ) * I) *
        Complex.exp ((t : ℂ) * ((u : ℂ) + (α₀ : ℂ) * I) * I)‖ =
        Real.exp (-α₀ * t) * I_int := by
      rw [← integral_const_mul]
      refine integral_congr_ae (ae_of_all _ fun u => ?_)
      dsimp only
      rw [norm_mul, Complex.norm_exp,
        show ((t : ℂ) * ((u : ℂ) + (α₀ : ℂ) * I) * I).re = -t * α₀ by
          simp [Complex.mul_re, Complex.mul_im],
        mul_comm (α₀ : ℂ) I, mul_comm _ (Real.exp (-t * α₀)), show -t * α₀ = -α₀ * t by ring]
    calc ‖∫ u : ℝ, hardyPsi ((u : ℂ) + (α₀ : ℂ) * I) *
          Complex.exp ((t : ℂ) * ((u : ℂ) + (α₀ : ℂ) * I) * I)‖
        ≤ Real.exp (-α₀ * t) * I_int := hint.trans_eq h_eq
      _ ≤ (I_int + 1) * Real.exp (-α₀ * t) := by
          rw [mul_comm]; exact mul_le_mul_of_nonneg_right (by linarith) (Real.exp_pos _).le
  · have ht_neg : t < 0 := lt_of_not_ge ht
    have hα_abs : |-α₀| < Real.pi / 4 := by rwa [abs_neg, abs_of_nonneg hα₀]
    rw [completedRiemannZeta_half_add_mul_I_eq_shift t hα_abs, abs_of_neg ht_neg]
    have hint := norm_integral_le_integral_norm (μ := volume)
      (fun u : ℝ => hardyPsi ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) *
        Complex.exp ((t : ℂ) * ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) * I))
    have h_sym : ∫ u : ℝ, ‖hardyPsi ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I)‖ = I_int := by
      have h_pt : (fun u : ℝ => ‖hardyPsi ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I)‖) =
          fun u : ℝ => ‖hardyPsi (((-u : ℝ) : ℂ) + I * (α₀ : ℂ))‖ := by
        ext u
        have hz : |(((-u : ℝ) : ℂ) + I * (α₀ : ℂ)).im| < Real.pi / 4 := by
          simpa [abs_of_nonneg hα₀] using hα
        have heq : -(((-u : ℝ) : ℂ) + I * (α₀ : ℂ)) = (u : ℂ) + ((-α₀ : ℝ) : ℂ) * I := by
          push_cast; ring
        rw [← heq, hardyPsi_neg hz]
      rw [h_pt]
      have hcomp := Measure.integral_comp_mul_left
        (fun x : ℝ => ‖hardyPsi ((x : ℂ) + I * (α₀ : ℂ))‖) (-1 : ℝ)
      simpa using hcomp
    have h_eq : ∫ u : ℝ, ‖hardyPsi ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) *
        Complex.exp ((t : ℂ) * ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) * I)‖ =
        Real.exp (-α₀ * -t) * I_int := by
      calc ∫ u : ℝ, ‖hardyPsi ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) *
            Complex.exp ((t : ℂ) * ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) * I)‖
          = ∫ u : ℝ, Real.exp (-α₀ * -t) * ‖hardyPsi ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I)‖ := by
              refine integral_congr_ae (ae_of_all _ fun u => ?_)
              dsimp only
              rw [norm_mul, Complex.norm_exp,
                show ((t : ℂ) * ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) * I).re = -t * -α₀ by
                  simp [Complex.mul_re, Complex.mul_im],
                mul_comm]
              congr 2; ring
        _ = Real.exp (-α₀ * -t) * ∫ u : ℝ, ‖hardyPsi ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I)‖ :=
              integral_const_mul _ _
        _ = Real.exp (-α₀ * -t) * I_int := by rw [h_sym]
    calc ‖∫ u : ℝ, hardyPsi ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) *
          Complex.exp ((t : ℂ) * ((u : ℂ) + ((-α₀ : ℝ) : ℂ) * I) * I)‖
        ≤ Real.exp (-α₀ * -t) * I_int := hint.trans_eq h_eq
      _ ≤ (I_int + 1) * Real.exp (-α₀ * -t) := by
          rw [mul_comm]; exact mul_le_mul_of_nonneg_right (by linarith) (Real.exp_pos _).le

private lemma continuous_completedRiemannZeta_criticalLine :
    Continuous (fun t : ℝ => completedRiemannZeta (1 / 2 + (t : ℂ) * I)) := by
  rw [continuous_iff_continuousAt]
  intro t
  have hs0 : (1 / 2 : ℂ) + (t : ℂ) * I ≠ 0 := by
    intro h; have := congrArg Complex.re h; norm_num at this
  have hs1 : (1 / 2 : ℂ) + (t : ℂ) * I ≠ 1 := by
    intro h; have := congrArg Complex.re h; norm_num at this
  have hdiff := (differentiableAt_completedZeta hs0 hs1).continuousAt
  have h_arg : ContinuousAt (fun x : ℝ => (1 / 2 : ℂ) + (x : ℂ) * I) t :=
    (continuous_const.add (Complex.continuous_ofReal.mul continuous_const)).continuousAt
  exact hdiff.comp (f := fun x : ℝ => (1 / 2 : ℂ) + (x : ℂ) * I) h_arg

private lemma integrable_abs_pow_mul_exp_mul_completedRiemannZeta (m : ℕ) {β : ℝ}
    (hβ₀ : 0 ≤ β) (hβ : β < Real.pi / 4) :
    Integrable (fun t : ℝ =>
      |t| ^ m * Real.exp (β * |t|) * ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖) := by
  let α₁ : ℝ := (β + Real.pi / 4) / 2
  have hα₁_gt : β < α₁ := by dsimp [α₁]; linarith
  have hα₁_pos : 0 ≤ α₁ := hβ₀.trans hα₁_gt.le
  have hα₁_lt : α₁ < Real.pi / 4 := by dsimp [α₁]; linarith
  let δ : ℝ := α₁ - β
  have hδ : 0 < δ := sub_pos.mpr hα₁_gt
  obtain ⟨C, hC, hΛ⟩ := norm_completedRiemannZeta_criticalLine_le hα₁_pos hα₁_lt
  let K : ℝ := C * (m.factorial : ℝ) / (δ / 2) ^ m
  have hK : 0 ≤ K := by positivity
  have hdom : Integrable (fun t : ℝ => K * Real.exp (-(δ / 2) * |t|)) := by
    have h1 : IntegrableOn (fun t : ℝ => K * Real.exp (-(δ / 2) * t)) (Ioi 0) :=
      (integrableOn_exp_mul_Ioi (by linarith : -(δ / 2) < 0) 0).const_mul K
    have h2 : IntegrableOn (fun t : ℝ => K * Real.exp ((δ / 2) * t)) (Iic 0) :=
      (integrableOn_exp_mul_Iic (by linarith : (0 : ℝ) < δ / 2) 0).const_mul K
    rw [← integrableOn_univ, ← Iic_union_Ioi (a := (0 : ℝ)), integrableOn_union]
    refine ⟨h2.congr_fun (fun t ht => ?_) measurableSet_Iic,
        h1.congr_fun (fun t ht => ?_) measurableSet_Ioi⟩
    · simp only [abs_of_nonpos (mem_Iic.mp ht)]; ring_nf
    · simp only [abs_of_pos (mem_Ioi.mp ht)]
  have hmeas : AEStronglyMeasurable (fun t : ℝ =>
      |t| ^ m * Real.exp (β * |t|) * ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖) volume :=
    ((continuous_abs.pow m).mul
      (Real.continuous_exp.comp (continuous_const.mul continuous_abs)) |>.mul
      continuous_completedRiemannZeta_criticalLine.norm).aestronglyMeasurable
  refine hdom.mono hmeas (ae_of_all _ fun t => ?_)
  have hpow : |t| ^ m ≤ (m.factorial : ℝ) / (δ / 2) ^ m * Real.exp ((δ / 2) * |t|) := by
    have hx_nn : 0 ≤ (δ / 2) * |t| := mul_nonneg (by positivity) (abs_nonneg t)
    have h_exp := Real.pow_div_factorial_le_exp ((δ / 2) * |t|) hx_nn m
    rw [mul_pow, div_le_iff₀ (Nat.cast_pos.mpr m.factorial_pos)] at h_exp
    have hc_pos : (0 : ℝ) < (δ / 2) ^ m := pow_pos (by linarith) m
    rw [← le_div_iff₀' hc_pos] at h_exp
    calc |t| ^ m ≤ (Real.exp ((δ / 2) * |t|) * (m.factorial : ℝ)) / (δ / 2) ^ m := h_exp
      _ = (m.factorial : ℝ) / (δ / 2) ^ m * Real.exp ((δ / 2) * |t|) := by ring
  rw [Real.norm_of_nonneg (mul_nonneg (mul_nonneg (pow_nonneg (abs_nonneg t) m) (Real.exp_pos _).le)
    (norm_nonneg _)), Real.norm_of_nonneg (mul_nonneg hK (Real.exp_pos _).le)]
  calc |t| ^ m * Real.exp (β * |t|) * ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖
      ≤ ((m.factorial : ℝ) / (δ / 2) ^ m * Real.exp ((δ / 2) * |t|)) * Real.exp (β * |t|) *
          (C * Real.exp (-α₁ * |t|)) :=
        mul_le_mul (mul_le_mul_of_nonneg_right hpow (Real.exp_pos _).le) (hΛ t) (norm_nonneg _)
          (by positivity)
    _ = K * (Real.exp ((δ / 2) * |t|) * Real.exp (β * |t|) * Real.exp (-α₁ * |t|)) := by
        dsimp [K]; ring
    _ = K * Real.exp (-(δ / 2) * |t|) := by
        rw [← Real.exp_add, ← Real.exp_add]
        congr 2; dsimp [δ]; ring

/-- Analytic strip representation `G(z) = (2π)⁻¹ ∫_{-∞}^∞ exp(-i z t) Λ(1/2 + i t) dt`
on the strip `|z.im| < π / 4`. -/
noncomputable def hardyG (z : ℂ) : ℂ :=
  ((2 * Real.pi : ℝ) : ℂ)⁻¹ *
    ∫ t : ℝ, Complex.exp (-z * (t : ℂ) * I) * completedRiemannZeta (1 / 2 + (t : ℂ) * I)

private lemma hardyG_ofReal (u : ℝ) : hardyG (u : ℂ) = hardyPsi (u : ℂ) := by
  let f : ℝ → ℂ := fun v => hardyPsi (v : ℂ)
  have hf_cont : Continuous f := by
    rw [continuous_iff_continuousAt]
    intro v
    exact (differentiableAt_hardyPsi (by simpa using Real.pi_pos)).continuousAt.comp
      Complex.continuous_ofReal.continuousAt
  have hf_int : Integrable f := by
    simpa [f] using integrable_hardyPsi_shift (α := 0) (by simpa using Real.pi_pos)
  have h_four : ∀ ξ : ℝ, 𝓕 f ξ =
      completedRiemannZeta (1 / 2 + ((-(2 * Real.pi) * ξ : ℝ) : ℂ) * I) := by
    intro ξ
    rw [Real.fourier_eq', completedRiemannZeta_half_add_mul_I_eq_fourier (-(2 * Real.pi) * ξ)]
    refine integral_congr_ae (ae_of_all _ fun v => ?_)
    dsimp only [f]
    rw [smul_eq_mul, mul_comm _ (hardyPsi (v : ℂ)), RCLike.inner_apply]
    simp only [starRingEnd_apply, star_trivial]
    congr 2
    push_cast
    ring
  have h_raw_int : Integrable (fun t : ℝ => ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖) := by
    simpa using integrable_abs_pow_mul_exp_mul_completedRiemannZeta 0 le_rfl
      (by linarith [Real.pi_pos] : (0 : ℝ) < Real.pi / 4)
  have h_comp_int : Integrable (fun ξ : ℝ =>
      completedRiemannZeta (1 / 2 + ((-(2 * Real.pi) * ξ : ℝ) : ℂ) * I)) := by
    have h_meas : Integrable (fun t : ℝ => completedRiemannZeta (1 / 2 + (t : ℂ) * I)) :=
      h_raw_int.mono continuous_completedRiemannZeta_criticalLine.aestronglyMeasurable
        (ae_of_all _ fun _ => by simp)
    exact (integrable_comp_mul_left_iff
      (fun t : ℝ => completedRiemannZeta (1 / 2 + (t : ℂ) * I))
      (neg_ne_zero.mpr (by positivity : 2 * Real.pi ≠ 0))).mpr h_meas
  have hf_four_int : Integrable (𝓕 f) := by
    refine h_comp_int.congr (ae_of_all _ fun ξ => (h_four ξ).symm)
  have hinv := congrFun (hf_cont.fourierInv_fourier_eq hf_int hf_four_int) u
  dsimp [f] at hinv
  rw [← hinv, Real.fourierInv_eq']
  have h_eq : (fun ξ : ℝ =>
      Complex.exp (((2 * Real.pi * ⟪ξ, u⟫ : ℝ) : ℂ) * I) • (𝓕 f ξ)) =
      fun ξ : ℝ =>
        Complex.exp (-(u : ℂ) * ((-(2 * Real.pi) * ξ : ℝ) : ℂ) * I) *
          completedRiemannZeta (1 / 2 + ((-(2 * Real.pi) * ξ : ℝ) : ℂ) * I) := by
    ext ξ
    rw [h_four ξ, smul_eq_mul, RCLike.inner_apply]
    simp only [starRingEnd_apply, star_trivial]
    congr 1
    congr 1
    push_cast
    ring
  rw [h_eq]
  have h_chg := Measure.integral_comp_mul_left (fun t : ℝ =>
    Complex.exp (-(u : ℂ) * (t : ℂ) * I) * completedRiemannZeta (1 / 2 + (t : ℂ) * I))
    (-(2 * Real.pi))
  rw [h_chg, abs_inv, abs_neg, abs_of_pos (by positivity : (0 : ℝ) < 2 * Real.pi),
    Complex.real_smul]
  dsimp [hardyG]
  push_cast
  ring

private lemma hasDerivAt_hardyG {z : ℂ} (hz : |z.im| < Real.pi / 4) :
    HasDerivAt hardyG (((2 * Real.pi : ℝ) : ℂ)⁻¹ *
      ∫ t : ℝ, (-((t : ℂ) * I) * Complex.exp (-z * (t : ℂ) * I)) *
        completedRiemannZeta (1 / 2 + (t : ℂ) * I)) z := by
  let α₀ : ℝ := (|z.im| + Real.pi / 4) / 2
  have hα₀_gt : |z.im| < α₀ := by dsimp [α₀]; linarith
  have hα₀_pos : 0 ≤ α₀ := (abs_nonneg _).trans hα₀_gt.le
  have hα₀_lt : α₀ < Real.pi / 4 := by dsimp [α₀]; linarith
  let ε : ℝ := α₀ - |z.im|
  have hε : 0 < ε := sub_pos.mpr hα₀_gt
  let F : ℂ → ℝ → ℂ := fun w t =>
    Complex.exp (-w * (t : ℂ) * I) * completedRiemannZeta (1 / 2 + (t : ℂ) * I)
  let F' : ℂ → ℝ → ℂ := fun w t =>
    (-((t : ℂ) * I) * Complex.exp (-w * (t : ℂ) * I)) * completedRiemannZeta (1 / 2 + (t : ℂ) * I)
  let bound : ℝ → ℝ := fun t =>
    |t| * Real.exp (α₀ * |t|) * ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖
  have h_bound_int : Integrable bound :=
    integrable_abs_pow_mul_exp_mul_completedRiemannZeta 1 hα₀_pos hα₀_lt
      |> fun h => by simpa [bound] using h
  have h_meas : ∀ᶠ w in 𝓝 z, AEStronglyMeasurable (F w) volume := by
    refine Eventually.of_forall fun w => ?_
    exact (((Complex.continuous_exp.comp
      ((continuous_const.mul Complex.continuous_ofReal).mul continuous_const))).mul
      continuous_completedRiemannZeta_criticalLine).aestronglyMeasurable
  have h_int_z : Integrable (F z) := by
    have h0 := integrable_abs_pow_mul_exp_mul_completedRiemannZeta 0 hα₀_pos hα₀_lt
    have h_meas_z : AEStronglyMeasurable (F z) volume :=
      ((Complex.continuous_exp.comp
        ((continuous_const.mul Complex.continuous_ofReal).mul continuous_const)).mul
        continuous_completedRiemannZeta_criticalLine).aestronglyMeasurable
    refine h0.mono h_meas_z (ae_of_all _ fun t => ?_)
    dsimp [F]
    rw [norm_mul, Complex.norm_exp,
      show (-z * (t : ℂ) * I).re = z.im * t by simp [Complex.mul_re, Complex.mul_im]]
    rw [pow_zero, one_mul, abs_of_nonneg (mul_nonneg (Real.exp_pos _).le (norm_nonneg _))]
    refine mul_le_mul_of_nonneg_right ?_ (norm_nonneg _)
    rw [Real.exp_le_exp]
    exact (le_abs_self (z.im * t)).trans (by rw [abs_mul]; gcongr)
  have h_F'_meas : AEStronglyMeasurable (F' z) volume := by
    exact (((Complex.continuous_ofReal.mul continuous_const).neg.mul
      (Complex.continuous_exp.comp
        ((continuous_const.mul Complex.continuous_ofReal).mul continuous_const))).mul
      continuous_completedRiemannZeta_criticalLine).aestronglyMeasurable
  have h_bound : ∀ᵐ t ∂volume, ∀ w ∈ Metric.ball z ε, ‖F' w t‖ ≤ bound t := by
    refine ae_of_all _ fun t w hw => ?_
    have hw_im : |w.im| ≤ α₀ := by
      have him_diff : |w.im - z.im| ≤ ‖w - z‖ := by
        simpa [Complex.sub_im] using Complex.abs_im_le_norm (w - z)
      have hdist : ‖w - z‖ < ε := mem_ball_iff_norm.mp hw
      have htri : |w.im| ≤ |z.im| + |w.im - z.im| := by
        simpa using abs_add_le z.im (w.im - z.im)
      linarith
    dsimp [F', bound]
    rw [norm_mul, norm_mul, norm_neg, norm_mul, Complex.norm_real, Complex.norm_I, mul_one,
      Real.norm_eq_abs, Complex.norm_exp,
      show (-w * (t : ℂ) * I).re = w.im * t by simp [Complex.mul_re, Complex.mul_im]]
    refine mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left ?_ (abs_nonneg t)) (norm_nonneg _)
    rw [Real.exp_le_exp]
    exact (le_abs_self (w.im * t)).trans
      (by rw [abs_mul]; exact mul_le_mul hw_im le_rfl (abs_nonneg t) hα₀_pos)
  have h_diff : ∀ᵐ t ∂volume, ∀ w ∈ Metric.ball z ε, HasDerivAt (fun x => F x t) (F' w t) w := by
    refine ae_of_all _ fun t w _ => ?_
    have h_inner : HasDerivAt (fun x : ℂ => -x * (t : ℂ) * I) (-((t : ℂ) * I)) w := by
      have h : HasDerivAt (fun x : ℂ => (-x) * ((t : ℂ) * I)) ((-1 : ℂ) * ((t : ℂ) * I)) w :=
        (hasDerivAt_id w).neg.mul_const ((t : ℂ) * I)
      simpa [neg_mul, mul_assoc, one_mul] using h
    have h_exp : HasDerivAt (fun x : ℂ => Complex.exp (-x * (t : ℂ) * I))
        (Complex.exp (-w * (t : ℂ) * I) * -((t : ℂ) * I)) w := h_inner.cexp
    convert h_exp.mul_const (completedRiemannZeta (1 / 2 + (t : ℂ) * I)) using 1
    dsimp [F']
    ring
  have h_res := hasDerivAt_integral_of_dominated_loc_of_deriv_le (Metric.ball_mem_nhds z hε)
    h_meas h_int_z h_F'_meas h_bound h_bound_int h_diff
  exact (h_res.2.const_mul (((2 * Real.pi : ℝ) : ℂ)⁻¹))

private lemma hardyG_eq_hardyPsi {z : ℂ} (hz : |z.im| < Real.pi / 4) :
    hardyG z = hardyPsi z := by
  let S : Set ℂ := {w : ℂ | |w.im| < Real.pi / 4}
  have hS_open : IsOpen S := isOpen_lt continuous_im.abs continuous_const
  have hS_conv : Convex ℝ S := by
    intro x hx y hy a b ha hb hab
    change |((a • x + b • y : ℂ)).im| < Real.pi / 4
    have him : ((a • x + b • y : ℂ)).im = a * x.im + b * y.im := by
      simp
    rw [him]
    calc |a * x.im + b * y.im| ≤ |a * x.im| + |b * y.im| := abs_add_le _ _
      _ = a * |x.im| + b * |y.im| := by
          rw [abs_mul, abs_mul, abs_of_nonneg ha, abs_of_nonneg hb]
      _ < a * (Real.pi / 4) + b * (Real.pi / 4) := by
          rcases eq_or_lt_of_le ha with rfl | ha_pos
          · have hb1 : b = 1 := by linarith
            subst hb1; simpa [S] using hy
          · have h1 : a * |x.im| < a * (Real.pi / 4) := mul_lt_mul_of_pos_left hx ha_pos
            have h2 : b * |y.im| ≤ b * (Real.pi / 4) :=
              mul_le_mul_of_nonneg_left (le_of_lt hy) hb
            linarith
      _ = Real.pi / 4 := by rw [← add_mul, hab, one_mul]
  have hS_pre : IsPreconnected S := hS_conv.isPreconnected
  have hG_ana : AnalyticOnNhd ℂ hardyG S :=
    DifferentiableOn.analyticOnNhd
      (fun w hw => (hasDerivAt_hardyG hw).differentiableAt.differentiableWithinAt) hS_open
  have hPsi_ana : AnalyticOnNhd ℂ hardyPsi S :=
    DifferentiableOn.analyticOnNhd
      (fun w hw => (differentiableAt_hardyPsi hw).differentiableWithinAt) hS_open
  have h0_mem : (0 : ℂ) ∈ S := by simp [S, Real.pi_pos]
  have h_freq : ∃ᶠ w in 𝓝[≠] (0 : ℂ), hardyG w = hardyPsi w := by
    rw [Metric.nhdsWithin_basis_ball.frequently_iff]
    intro δ hδ
    let u : ℝ := min (δ / 2) 1
    have hu_pos : 0 < u := lt_min (half_pos hδ) one_pos
    refine ⟨(u : ℂ), ⟨?_, Complex.ofReal_ne_zero.mpr hu_pos.ne'⟩, hardyG_ofReal u⟩
    rw [Metric.mem_ball, dist_zero_right, Complex.norm_real, Real.norm_of_nonneg hu_pos.le]
    exact lt_of_le_of_lt (min_le_left _ _) (half_lt_self hδ)
  exact hG_ana.eqOn_of_preconnected_of_frequently_eq hPsi_ana hS_pre h0_mem h_freq hz

private lemma integral_exp_mul_completedRiemannZeta {α : ℝ} (hα : |α| < Real.pi / 4) :
    ((2 * Real.pi : ℝ) : ℂ)⁻¹ *
      ∫ t : ℝ, Complex.exp ((α : ℂ) * (t : ℂ)) * completedRiemannZeta (1 / 2 + (t : ℂ) * I) =
      hardyPsi (I * (α : ℂ)) := by
  have hz : |(I * (α : ℂ)).im| < Real.pi / 4 := by simpa using hα
  have h := hardyG_eq_hardyPsi hz
  dsimp [hardyG] at h
  convert h using 3
  ext t
  congr 1
  congr 1
  calc (α : ℂ) * (t : ℂ)
      = -(I * I) * (α : ℂ) * (t : ℂ) := by rw [I_mul_I]; ring
    _ = -(I * (α : ℂ)) * (t : ℂ) * I := by ring

/-- The theta component of `hardyPsi z`: `exp (z / 2) * jacobiTheta (I * exp (2 * z))`. -/
noncomputable def hardyThetaTerm (z : ℂ) : ℂ :=
  Complex.exp (z / 2) * jacobiTheta (I * Complex.exp (2 * z))

private lemma jacobiTheta_neg_one_add {η : ℂ} (hη : 0 < η.im) :
    jacobiTheta (-1 + η) = 2 * jacobiTheta (4 * η) - jacobiTheta η := by
  have hη1 : 0 < (-1 + η).im := by simpa using hη
  have hη4 : 0 < (4 * η).im := by
    have : (4 * η).im = 4 * η.im := by simp
    linarith
  rw [jacobiTheta_eq_tsum_nat hη1, jacobiTheta_eq_tsum_nat hη4, jacobiTheta_eq_tsum_nat hη]
  let f : ℕ → ℂ := fun n => Complex.exp (Real.pi * I * ((n : ℂ) + 1) ^ 2 * (-1 + η))
  let g : ℕ → ℂ := fun n => Complex.exp (Real.pi * I * ((n : ℂ) + 1) ^ 2 * η)
  let h4 : ℕ → ℂ := fun m => Complex.exp (Real.pi * I * ((m : ℂ) + 1) ^ 2 * (4 * η))
  have hf : Summable f := (hasSum_nat_jacobiTheta hη1).summable
  have hg : Summable g := (hasSum_nat_jacobiTheta hη).summable
  have hh4 : Summable h4 := (hasSum_nat_jacobiTheta hη4).summable
  have h_even_odd : ∀ m : ℕ, f (2 * m) + g (2 * m) = 0 ∧
      f (2 * m + 1) + g (2 * m + 1) = 2 * h4 m := by
    intro m
    have h_sign_even : Complex.exp (Real.pi * I * (((2 * m : ℕ) : ℂ) + 1) ^ 2 * (-1)) = -1 := by
      have hexp : Real.pi * I * (((2 * m : ℕ) : ℂ) + 1) ^ 2 * (-1) =
          (((m : ℤ) ^ 2 + m : ℤ) * (-2 : ℤ) : ℤ) * (2 * Real.pi * I) - Real.pi * I := by
        push_cast; ring
      rw [hexp, sub_eq_add_neg, Complex.exp_add, Complex.exp_int_mul_two_pi_mul_I, one_mul,
        Complex.exp_neg, Complex.exp_pi_mul_I]
      norm_num
    have h_sign_odd :
        Complex.exp (Real.pi * I * (((2 * m + 1 : ℕ) : ℂ) + 1) ^ 2 * (-1)) = 1 := by
      have hexp : Real.pi * I * (((2 * m + 1 : ℕ) : ℂ) + 1) ^ 2 * (-1) =
          (-(((m : ℤ) + 1) ^ 2 * 2 : ℤ) : ℤ) * (2 * Real.pi * I) := by
        push_cast; ring
      rw [hexp, Complex.exp_int_mul_two_pi_mul_I]
    have h_f_mul : ∀ n : ℕ,
        f n = Complex.exp (Real.pi * I * ((n : ℂ) + 1) ^ 2 * (-1)) * g n := by
      intro n
      dsimp [f, g]
      rw [← Complex.exp_add]
      congr 1; ring
    constructor
    · rw [h_f_mul (2 * m), h_sign_even]; ring
    · have hg_odd : g (2 * m + 1) = h4 m := by
        dsimp [g, h4]
        congr 1; push_cast; ring
      rw [h_f_mul (2 * m + 1), h_sign_odd, one_mul, hg_odd]; ring
  have h_sum_2N : ∀ N : ℕ,
      (∑ n ∈ Finset.range (2 * N), (f n + g n)) = 2 * ∑ m ∈ Finset.range N, h4 m := by
    intro N
    induction N with
    | zero => simp
    | succ N ih =>
      rw [show 2 * (N + 1) = (2 * N + 1) + 1 by ring, Finset.sum_range_succ,
        Finset.sum_range_succ, ih, Finset.sum_range_succ,
        (h_even_odd N).1, (h_even_odd N).2]
      ring
  have h_ten_nat : Tendsto (fun N : ℕ => 2 * N) atTop atTop :=
    Filter.tendsto_atTop_atTop.mpr fun b => ⟨b, fun n hn => by omega⟩
  have h_ten_L : Tendsto (fun N : ℕ => ∑ n ∈ Finset.range (2 * N), (f n + g n))
      atTop (nhds (∑' n : ℕ, (f n + g n))) :=
    (hf.add hg).hasSum.tendsto_sum_nat.comp h_ten_nat
  have h_ten_R : Tendsto (fun N : ℕ => 2 * ∑ m ∈ Finset.range N, h4 m)
      atTop (nhds (2 * ∑' m : ℕ, h4 m)) :=
    tendsto_const_nhds.mul hh4.hasSum.tendsto_sum_nat
  have h_tsum : ∑' n : ℕ, (f n + g n) = 2 * ∑' m : ℕ, h4 m := by
    have h_eq_fn : (fun N : ℕ => ∑ n ∈ Finset.range (2 * N), (f n + g n)) =
        fun N : ℕ => 2 * ∑ m ∈ Finset.range N, h4 m := funext h_sum_2N
    rw [h_eq_fn] at h_ten_L
    exact tendsto_nhds_unique h_ten_L h_ten_R
  rw [hf.tsum_add hg] at h_tsum
  have hf_sum : ∑' n : ℕ, f n = 2 * ∑' m : ℕ, h4 m - ∑' n : ℕ, g n :=
    eq_sub_of_add_eq h_tsum
  dsimp [f, g, h4] at hf_sum
  rw [hf_sum]
  ring

private lemma cpow_neg_half_four_mul {z : ℂ} (hz : 0 < z.re) :
    ((4 : ℂ) * z) ^ (-(1 / 2 : ℂ)) = (1 / 2 : ℂ) * z ^ (-(1 / 2 : ℂ)) := by
  have hz0 : z ≠ 0 := fun h => by rw [h] at hz; simp at hz
  have h4z0 : (4 : ℂ) * z ≠ 0 := mul_ne_zero (by norm_num) hz0
  have harg4 : (4 : ℂ).arg = 0 := Complex.arg_ofReal_of_nonneg (by norm_num)
  have hargz : |z.arg| < Real.pi / 2 := Complex.abs_arg_lt_pi_div_two_iff.mpr (Or.inl hz)
  have hlog : Complex.log ((4 : ℂ) * z) = Complex.log (4 : ℂ) + Complex.log z := by
    apply Complex.log_mul (by norm_num) hz0
    rw [harg4, zero_add]
    have h1 := (abs_lt.mp hargz).1
    have h2 := (abs_lt.mp hargz).2
    constructor <;> linarith [Real.pi_pos]
  rw [Complex.cpow_def_of_ne_zero h4z0, Complex.cpow_def_of_ne_zero hz0, hlog,
    add_mul, Complex.exp_add]
  congr 1
  have h4log : Complex.exp (Complex.log (4 : ℂ) * -(1 / 2 : ℂ)) = (1 / 2 : ℂ) := by
    rw [mul_comm, show (4 : ℂ) = ((4 : ℝ) : ℂ) by norm_num, ← Complex.ofReal_log (by norm_num),
      show -(1 / 2 : ℂ) * ((Real.log 4 : ℝ) : ℂ) = ((-(1 / 2) * Real.log 4 : ℝ) : ℂ) by
        push_cast; ring,
      ← Complex.ofReal_exp]
    have hreal : Real.exp (-(1 / 2 : ℝ) * Real.log 4) = 1 / 2 := by
      rw [mul_comm, ← Real.rpow_def_of_pos (by norm_num : (0 : ℝ) < 4),
        Real.rpow_neg (by norm_num), show (4 : ℝ) ^ (1 / 2 : ℝ) = 2 by
          rw [← Real.sqrt_eq_rpow, show (4 : ℝ) = 2 ^ 2 by norm_num, Real.sqrt_sq (by norm_num)]]
      norm_num
    rw [hreal]
    norm_num
  exact h4log

private lemma norm_cpow_neg_half {z : ℂ} (hz : z ≠ 0) :
    ‖z ^ (-(1 / 2 : ℂ))‖ = Real.sqrt (‖z‖⁻¹) := by
  rw [Complex.cpow_def_of_ne_zero hz, Complex.norm_exp,
    show (Complex.log z * -(1 / 2 : ℂ)).re = (Complex.log z).re * -(1 / 2 : ℝ) by
      simp [Complex.mul_re],
    Complex.log_re, ← Real.rpow_def_of_pos (norm_pos_iff.mpr hz),
    Real.rpow_neg (norm_nonneg z), Real.sqrt_eq_rpow, Real.inv_rpow (norm_nonneg z)]

private lemma norm_jacobiTheta_neg_one_add_le {η : ℂ} (hη_im : 0 < η.im)
    (h_big : 1 ≤ Real.pi * (η.im / (4 * ‖η‖ ^ 2))) :
    ‖jacobiTheta (-1 + η)‖ ≤
      8 * Real.sqrt (η.im⁻¹) * Real.exp (-Real.pi * (η.im / (4 * ‖η‖ ^ 2))) := by
  have hη0 : η ≠ 0 := fun h => by rw [h] at hη_im; simp at hη_im
  let σ : ℂ := -η⁻¹
  let σ₄ : ℂ := -(4 * η)⁻¹
  have hσ_im : σ.im = η.im / ‖η‖ ^ 2 := by
    dsimp [σ]
    simp [Complex.inv_im, Complex.normSq_eq_norm_sq, div_eq_mul_inv]
  have hσ₄_im : σ₄.im = η.im / (4 * ‖η‖ ^ 2) := by
    dsimp [σ₄]
    simp [Complex.inv_im, Complex.normSq_eq_norm_sq]
    ring
  have hσ_pos : 0 < σ.im := by rw [hσ_im]; positivity
  have hσ₄_pos : 0 < σ₄.im := by rw [hσ₄_im]; positivity
  have hS1 : jacobiTheta η = (-I * η) ^ (-(1 / 2 : ℂ)) * jacobiTheta σ := by
    let τ : ℍ := ⟨σ, hσ_pos⟩
    have hS := jacobiTheta_S_smul τ
    have h_mod : ((ModularGroup.S • τ : ℍ) : ℂ) = η := by
      rw [UpperHalfPlane.modular_S_smul]
      change (-(τ : ℂ))⁻¹ = η
      dsimp [τ, σ]
      simp
    have h_neg_I_re : 0 < (-I * η).re := by simp [hη_im]
    have h_arg : (-I * η).arg ≠ Real.pi := by
      have hlt := Complex.abs_arg_lt_pi_div_two_iff.mpr (Or.inl h_neg_I_re)
      intro h; rw [h, abs_of_pos Real.pi_pos] at hlt; linarith [Real.pi_pos]
    have h_eq_pow : (-I * (τ : ℂ)) ^ (1 / 2 : ℂ) = (-I * η) ^ (-(1 / 2 : ℂ)) := by
      have h_inner : (-I * (τ : ℂ)) = (-I * η)⁻¹ := by
        dsimp [τ, σ]
        rw [mul_neg, neg_mul, neg_neg, mul_inv, inv_neg, inv_I, neg_neg]
      rw [h_inner, Complex.inv_cpow (-I * η) (1 / 2 : ℂ) h_arg, Complex.cpow_neg]
    change jacobiTheta ((ModularGroup.S • τ : ℍ) : ℂ) =
      (-I * (τ : ℂ)) ^ (1 / 2 : ℂ) * jacobiTheta (τ : ℂ) at hS
    rw [h_mod, h_eq_pow] at hS
    exact hS
  have hS4 : jacobiTheta (4 * η) = (1 / 2 : ℂ) * (-I * η) ^ (-(1 / 2 : ℂ)) * jacobiTheta σ₄ := by
    let τ₄ : ℍ := ⟨σ₄, hσ₄_pos⟩
    have hS := jacobiTheta_S_smul τ₄
    have h_mod : ((ModularGroup.S • τ₄ : ℍ) : ℂ) = 4 * η := by
      rw [UpperHalfPlane.modular_S_smul]
      change (-(τ₄ : ℂ))⁻¹ = 4 * η
      dsimp [τ₄, σ₄]
      simp
    have h_neg_I4_re : 0 < (-I * (4 * η)).re := by simp [hη_im]
    have h_arg : (-I * (4 * η)).arg ≠ Real.pi := by
      have hlt := Complex.abs_arg_lt_pi_div_two_iff.mpr (Or.inl h_neg_I4_re)
      intro h; rw [h, abs_of_pos Real.pi_pos] at hlt; linarith [Real.pi_pos]
    have h_eq_pow : (-I * (τ₄ : ℂ)) ^ (1 / 2 : ℂ) =
        (1 / 2 : ℂ) * (-I * η) ^ (-(1 / 2 : ℂ)) := by
      have h_inner : (-I * (τ₄ : ℂ)) = (-I * (4 * η))⁻¹ := by
        dsimp [τ₄, σ₄]
        calc -I * -(4 * η)⁻¹ = (4 * η)⁻¹ * I := by ring
          _ = (4 * η)⁻¹ * (-I)⁻¹ := by rw [inv_neg, inv_I, neg_neg]
          _ = (-I * (4 * η))⁻¹ := by rw [← mul_inv_rev]
      rw [h_inner, Complex.inv_cpow (-I * (4 * η)) (1 / 2 : ℂ) h_arg,
        show -I * (4 * η) = (4 : ℂ) * (-I * η) by ring,
        ← Complex.cpow_neg ((4 : ℂ) * (-I * η)) (1 / 2 : ℂ),
        cpow_neg_half_four_mul (by simp [hη_im])]
    change jacobiTheta ((ModularGroup.S • τ₄ : ℍ) : ℂ) =
      (-I * (τ₄ : ℂ)) ^ (1 / 2 : ℂ) * jacobiTheta (τ₄ : ℂ) at hS
    rw [h_mod, h_eq_pow] at hS
    exact hS
  have h_diff : jacobiTheta (-1 + η) =
      (-I * η) ^ (-(1 / 2 : ℂ)) * ((jacobiTheta σ₄ - 1) - (jacobiTheta σ - 1)) := by
    rw [jacobiTheta_neg_one_add hη_im, hS4, hS1]
    ring
  have h_e1 : ‖jacobiTheta σ - 1‖ ≤ 4 * Real.exp (-Real.pi * σ₄.im) := by
    have h_raw := norm_jacobiTheta_sub_one_le hσ_pos
    have hσ_ge : σ₄.im ≤ σ.im := by
      rw [hσ_im, hσ₄_im]
      gcongr
      linarith [sq_nonneg ‖η‖]
    have hpi1 : 1 ≤ Real.pi * σ.im := by
      have : Real.pi * σ₄.im ≤ Real.pi * σ.im := mul_le_mul_of_nonneg_left hσ_ge Real.pi_pos.le
      rw [hσ₄_im] at this
      linarith [h_big]
    have h_exp_half : Real.exp (-Real.pi * σ.im) ≤ 1 / 2 := by
      calc Real.exp (-Real.pi * σ.im)
          ≤ Real.exp (-1) := Real.exp_le_exp.mpr (by linarith)
        _ ≤ 1 / 2 := by
            have := Real.add_one_le_exp (1 : ℝ)
            rw [Real.exp_neg, inv_le_iff_one_le_mul₀ (by linarith)]
            linarith
    have h_den : 2 / (1 - Real.exp (-Real.pi * σ.im)) ≤ 4 := by
      rw [div_le_iff₀ (by linarith)]
      linarith
    calc ‖jacobiTheta σ - 1‖
        ≤ 2 / (1 - Real.exp (-Real.pi * σ.im)) * Real.exp (-Real.pi * σ.im) := h_raw
      _ ≤ 4 * Real.exp (-Real.pi * σ.im) :=
          mul_le_mul_of_nonneg_right h_den (Real.exp_pos _).le
      _ ≤ 4 * Real.exp (-Real.pi * σ₄.im) :=
          mul_le_mul_of_nonneg_left
            (Real.exp_le_exp.mpr (mul_le_mul_of_nonpos_left hσ_ge (neg_nonpos.mpr Real.pi_pos.le)))
            (by norm_num)
  have h_e4 : ‖jacobiTheta σ₄ - 1‖ ≤ 4 * Real.exp (-Real.pi * σ₄.im) := by
    have h_raw := norm_jacobiTheta_sub_one_le hσ₄_pos
    have hpi1 : 1 ≤ Real.pi * σ₄.im := by rw [hσ₄_im]; exact h_big
    have h_exp_half : Real.exp (-Real.pi * σ₄.im) ≤ 1 / 2 := by
      calc Real.exp (-Real.pi * σ₄.im)
          ≤ Real.exp (-1) := Real.exp_le_exp.mpr (by linarith)
        _ ≤ 1 / 2 := by
            have := Real.add_one_le_exp (1 : ℝ)
            rw [Real.exp_neg, inv_le_iff_one_le_mul₀ (by linarith)]
            linarith
    have h_den : 2 / (1 - Real.exp (-Real.pi * σ₄.im)) ≤ 4 := by
      rw [div_le_iff₀ (by linarith)]
      linarith
    exact h_raw.trans (mul_le_mul_of_nonneg_right h_den (Real.exp_pos _).le)
  have h_pow_norm : ‖(-I * η) ^ (-(1 / 2 : ℂ))‖ ≤ Real.sqrt (η.im⁻¹) := by
    rw [norm_cpow_neg_half (mul_ne_zero (neg_ne_zero.mpr I_ne_zero) hη0),
      norm_mul, norm_neg, Complex.norm_I, one_mul]
    exact Real.sqrt_le_sqrt (inv_anti₀ hη_im (Complex.im_le_norm η))
  rw [h_diff, norm_mul]
  calc ‖(-I * η) ^ (-(1 / 2 : ℂ))‖ * ‖(jacobiTheta σ₄ - 1) - (jacobiTheta σ - 1)‖
      ≤ Real.sqrt (η.im⁻¹) * (‖jacobiTheta σ₄ - 1‖ + ‖jacobiTheta σ - 1‖) :=
        mul_le_mul h_pow_norm (norm_sub_le _ _) (norm_nonneg _) (Real.sqrt_nonneg _)
    _ ≤ Real.sqrt (η.im⁻¹) *
        (4 * Real.exp (-Real.pi * σ₄.im) + 4 * Real.exp (-Real.pi * σ₄.im)) := by
        gcongr
    _ = 8 * Real.sqrt (η.im⁻¹) * Real.exp (-Real.pi * (η.im / (4 * ‖η‖ ^ 2))) := by
        rw [hσ₄_im]; ring

private lemma tendsto_iteratedDeriv_hardyThetaTerm (k : ℕ) :
    Tendsto (fun δ : ℝ =>
      ‖iteratedDeriv (2 * k) (fun w : ℂ => hardyThetaTerm (I * w))
        ((Real.pi / 4 - δ : ℝ) : ℂ)‖)
      (𝓝[>] (0 : ℝ)) (nhds 0) := by
  let c_im : ℝ := Real.exp (-1) * (2 / Real.pi)
  have hc_im : 0 < c_im := by positivity
  let c_decay : ℝ := Real.pi * c_im / 256
  have hc_decay : 0 < c_decay := by positivity
  let δ₀ : ℝ := min (Real.pi / 16) (min (1 / 4) c_decay)
  have hδ₀ : 0 < δ₀ := by positivity
  have h_bound_ev : ∀ᶠ δ in 𝓝[>] (0 : ℝ),
      ‖iteratedDeriv (2 * k) (fun w : ℂ => hardyThetaTerm (I * w))
        ((Real.pi / 4 - δ : ℝ) : ℂ)‖ ≤
        ((2 * k).factorial : ℝ) * (Real.exp 1 * 8 * (c_im⁻¹ + 1)) * (2 : ℝ) ^ (2 * k) *
          (δ⁻¹) ^ (2 * k + 1) * Real.exp (-c_decay * δ⁻¹) := by
    filter_upwards [Ioo_mem_nhdsGT hδ₀] with δ hδ
    have hδ_pos : 0 < δ := hδ.1
    have hδ_le_pi16 : δ ≤ Real.pi / 16 := hδ.2.le.trans (min_le_left _ _)
    have hδ_le_quart : δ ≤ 1 / 4 := hδ.2.le.trans ((min_le_right _ _).trans (min_le_left _ _))
    have hδ_le_1 : δ ≤ 1 := hδ_le_quart.trans (by norm_num)
    have hδ_le_dec : δ ≤ c_decay := hδ.2.le.trans ((min_le_right _ _).trans (min_le_right _ _))
    let center : ℂ := ((Real.pi / 4 - δ : ℝ) : ℂ)
    let R : ℝ := δ / 2
    have hR : 0 < R := half_pos hδ_pos
    have hR_eq : R = δ / 2 := rfl
    have h_diff_ball : DiffContOnCl ℂ (fun w : ℂ => hardyThetaTerm (I * w))
        (Metric.ball center R) := by
      have h_sub : Metric.closedBall center R ⊆ {w : ℂ | |w.re| < Real.pi / 4} := by
        intro w hw
        have hre_diff : |w.re - center.re| ≤ ‖w - center‖ := by
          simpa [Complex.sub_re] using Complex.abs_re_le_norm (w - center)
        have hdist : ‖w - center‖ ≤ R := by
          simpa [Complex.dist_eq] using Metric.mem_closedBall.mp hw
        have h_cen_re : center.re = Real.pi / 4 - δ := by simp [center]
        rw [h_cen_re] at hre_diff
        have h1 : Real.pi / 4 - 3 * δ / 2 ≤ w.re := by
          linarith [(abs_le.mp (hre_diff.trans hdist)).1, hR_eq]
        have h2 : w.re ≤ Real.pi / 4 - δ / 2 := by
          linarith [(abs_le.mp (hre_diff.trans hdist)).2, hR_eq]
        refine abs_lt.mpr ⟨?_, h2.trans_lt (sub_lt_self _ (half_pos hδ_pos))⟩
        have h_lo : -(Real.pi / 4) < Real.pi / 4 - 3 * (Real.pi / 16) / 2 := by
          linarith [Real.pi_pos]
        have h_δpi : 3 * δ / 2 ≤ 3 * (Real.pi / 16) / 2 := by gcongr
        exact h_lo.trans_le (by linarith [h_δpi, h1])
      have h_diff_strip : DifferentiableOn ℂ (fun w : ℂ => hardyThetaTerm (I * w))
          {w : ℂ | |w.re| < Real.pi / 4} := by
        intro w hw
        have him : |(I * w).im| < Real.pi / 4 := by simpa using hw
        have hθ := differentiableAt_jacobiTheta (im_I_mul_exp_two_mul_pos him)
        have h_cexp : DifferentiableAt ℂ (fun x : ℂ => Complex.exp (2 * (I * x))) w :=
          ((differentiableAt_const (2 : ℂ)).mul
            ((differentiableAt_const I).mul differentiableAt_id)).cexp
        have h_jac : DifferentiableAt ℂ
            (jacobiTheta ∘ fun x : ℂ => I * Complex.exp (2 * (I * x))) w :=
          hθ.comp w ((differentiableAt_const I).mul h_cexp)
        have h_left : DifferentiableAt ℂ (fun x : ℂ => Complex.exp ((I * x) / 2)) w :=
          (((differentiableAt_const I).mul differentiableAt_id).div_const 2).cexp
        change DifferentiableWithinAt ℂ
          (fun x : ℂ => Complex.exp ((I * x) / 2) *
            jacobiTheta (I * Complex.exp (2 * (I * x)))) _ w
        exact (h_left.mul h_jac).differentiableWithinAt
      exact ⟨h_diff_strip.mono (Metric.ball_subset_closedBall.trans h_sub),
        (h_diff_strip.mono (Metric.closure_ball_subset_closedBall.trans h_sub)).continuousOn⟩
    have h_sphere : ∀ w ∈ Metric.sphere center R,
        ‖hardyThetaTerm (I * w)‖ ≤
          Real.exp 1 * 8 * (c_im⁻¹ + 1) * δ⁻¹ * Real.exp (-c_decay * δ⁻¹) := by
      intro w hw
      have hw_dist : ‖w - center‖ = R := mem_sphere_iff_norm.mp hw
      have h_cen_re : center.re = Real.pi / 4 - δ := by simp [center]
      have h_cen_im : center.im = 0 := by simp [center]
      have hre_diff : |w.re - (Real.pi / 4 - δ)| ≤ R := by
        simpa [Complex.sub_re, h_cen_re, hw_dist] using Complex.abs_re_le_norm (w - center)
      have him_diff : |w.im| ≤ R := by
        simpa [Complex.sub_im, h_cen_im, hw_dist] using Complex.abs_im_le_norm (w - center)
      let u : ℂ := (Real.pi / 4 : ℂ) - w
      have hu_re_lo : δ / 2 ≤ u.re := by
        have := (abs_le.mp hre_diff).2
        have hure : u.re = Real.pi / 4 - w.re := by simp [u]
        linarith [hR_eq]
      have hu_re_hi : u.re ≤ 3 * δ / 2 := by
        have := (abs_le.mp hre_diff).1
        have hure : u.re = Real.pi / 4 - w.re := by simp [u]
        linarith [hR_eq]
      have hu_im : |u.im| ≤ δ / 2 := by
        have huim : u.im = -w.im := by simp [u]
        rw [huim, abs_neg]
        linarith [him_diff, hR_eq]
      let η : ℂ := 1 - Complex.exp (-2 * I * u)
      have h_tau : I * Complex.exp (2 * (I * w)) = -1 + η := by
        have hexp : 2 * (I * w) = (Real.pi / 2 : ℂ) * I + (-2 * I * u) := by
          dsimp [u]; ring
        rw [hexp, Complex.exp_add, Complex.exp_pi_div_two_mul_I]
        dsimp [η]
        calc I * (I * Complex.exp (-2 * I * u))
            = (I * I) * Complex.exp (-2 * I * u) := by ring
          _ = -1 + (1 - Complex.exp (-2 * I * u)) := by rw [I_mul_I]; ring
      have hη_im : c_im * δ ≤ η.im := by
        have him_eq : η.im = Real.exp (2 * u.im) * Real.sin (2 * u.re) := by
          dsimp [η]
          simp only [zero_sub, Complex.exp_im]
          have hre2 : (-2 * I * u).re = 2 * u.im := by
            simp [Complex.mul_re, Complex.mul_im]
          have him2 : (-2 * I * u).im = -2 * u.re := by
            simp [Complex.mul_re, Complex.mul_im]
          rw [hre2, him2, show (-2 * u.re : ℝ) = -(2 * u.re) by ring, Real.sin_neg]
          ring
        have hsin : (2 / Real.pi) * (2 * u.re) ≤ Real.sin (2 * u.re) :=
          Real.mul_le_sin (by linarith) (by linarith [Real.pi_pos, hδ_le_pi16])
        have hexp_im : Real.exp (-1) ≤ Real.exp (2 * u.im) := by
          rw [Real.exp_le_exp]
          have := (abs_le.mp hu_im).1
          linarith
        rw [him_eq]
        calc c_im * δ
            = Real.exp (-1) * ((2 / Real.pi) * δ) := by dsimp [c_im]; ring
          _ ≤ Real.exp (-1) * ((2 / Real.pi) * (2 * u.re)) := by
              gcongr; linarith
          _ ≤ Real.exp (2 * u.im) * Real.sin (2 * u.re) :=
              mul_le_mul hexp_im hsin (mul_nonneg (by positivity) (by linarith))
                (Real.exp_pos _).le
      have hη_im_pos : 0 < η.im := lt_of_lt_of_le (mul_pos hc_im hδ_pos) hη_im
      have hη_norm : ‖η‖ ≤ 8 * δ := by
        have hu_norm : ‖u‖ ≤ 2 * δ := by
          have := Complex.norm_le_abs_re_add_abs_im u
          rw [abs_of_nonneg (by linarith)] at this
          linarith [hu_im]
        have h_arg_norm : ‖-2 * I * u‖ ≤ 1 := by
          rw [norm_mul, norm_mul, norm_neg, Complex.norm_two, Complex.norm_I, mul_one]
          linarith
        have h_sub := Complex.norm_exp_sub_one_le h_arg_norm
        rw [show η = -(Complex.exp (-2 * I * u) - 1) by dsimp [η]; ring, norm_neg]
        calc ‖Complex.exp (-2 * I * u) - 1‖
            ≤ 2 * ‖-2 * I * u‖ := h_sub
          _ = 4 * ‖u‖ := by
              rw [norm_mul, norm_mul, norm_neg, Complex.norm_two, Complex.norm_I, mul_one]; ring
          _ ≤ 8 * δ := by linarith
      have h_ratio_lo : c_decay * δ⁻¹ ≤ Real.pi * (η.im / (4 * ‖η‖ ^ 2)) := by
        have hη_norm_pos : 0 < ‖η‖ :=
          norm_pos_iff.mpr (fun h => by rw [h] at hη_im_pos; simp at hη_im_pos)
        calc c_decay * δ⁻¹
            = Real.pi * (c_im * δ / (4 * (8 * δ) ^ 2)) := by
                dsimp [c_decay]; field_simp [hδ_pos.ne']; ring
          _ ≤ Real.pi * (η.im / (4 * ‖η‖ ^ 2)) := by gcongr
      have h_big : 1 ≤ Real.pi * (η.im / (4 * ‖η‖ ^ 2)) := by
        calc (1 : ℝ) = δ * δ⁻¹ := (mul_inv_cancel₀ hδ_pos.ne').symm
          _ ≤ c_decay * δ⁻¹ := mul_le_mul_of_nonneg_right hδ_le_dec (inv_nonneg.mpr hδ_pos.le)
          _ ≤ Real.pi * (η.im / (4 * ‖η‖ ^ 2)) := h_ratio_lo
      have hθ_bd := norm_jacobiTheta_neg_one_add_le hη_im_pos h_big
      have h_sqrt_bd : Real.sqrt (η.im⁻¹) ≤ (c_im⁻¹ + 1) * δ⁻¹ := by
        have h1 : Real.sqrt (η.im⁻¹) ≤ η.im⁻¹ + 1 := by
          nlinarith [Real.sq_sqrt (inv_nonneg.mpr hη_im_pos.le)]
        have h2 : η.im⁻¹ ≤ (c_im * δ)⁻¹ := inv_anti₀ (mul_pos hc_im hδ_pos) hη_im
        have h3 : (1 : ℝ) ≤ δ⁻¹ := (one_le_inv₀ hδ_pos).mpr hδ_le_1
        calc Real.sqrt (η.im⁻¹) ≤ η.im⁻¹ + 1 := h1
          _ ≤ c_im⁻¹ * δ⁻¹ + δ⁻¹ := by
              rw [mul_inv] at h2; linarith
          _ = (c_im⁻¹ + 1) * δ⁻¹ := by ring
      have h_exp_bd :
          Real.exp (-Real.pi * (η.im / (4 * ‖η‖ ^ 2))) ≤ Real.exp (-c_decay * δ⁻¹) := by
        rw [Real.exp_le_exp]
        linarith
      have h_pref_bd : ‖Complex.exp ((I * w) / 2)‖ ≤ Real.exp 1 := by
        rw [Complex.norm_exp, show ((I * w) / 2).re = -w.im / 2 by simp [Complex.mul_re]]
        rw [Real.exp_le_exp]
        have := (abs_le.mp him_diff).1
        linarith [hR_eq]
      dsimp [hardyThetaTerm]
      rw [h_tau, norm_mul]
      calc ‖Complex.exp ((I * w) / 2)‖ * ‖jacobiTheta (-1 + η)‖
          ≤ Real.exp 1 *
              (8 * Real.sqrt (η.im⁻¹) * Real.exp (-Real.pi * (η.im / (4 * ‖η‖ ^ 2)))) :=
            mul_le_mul h_pref_bd hθ_bd (norm_nonneg _) (Real.exp_pos _).le
        _ ≤ Real.exp 1 * (8 * ((c_im⁻¹ + 1) * δ⁻¹) * Real.exp (-c_decay * δ⁻¹)) := by
            gcongr
        _ = Real.exp 1 * 8 * (c_im⁻¹ + 1) * δ⁻¹ * Real.exp (-c_decay * δ⁻¹) := by ring
    have h_cauchy := Complex.norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le
      (2 * k) hR h_diff_ball h_sphere
    calc ‖iteratedDeriv (2 * k) (fun w : ℂ => hardyThetaTerm (I * w)) center‖
        ≤ (2 * k).factorial * (Real.exp 1 * 8 * (c_im⁻¹ + 1) * δ⁻¹ * Real.exp (-c_decay * δ⁻¹)) /
            (δ / 2) ^ (2 * k) := h_cauchy
      _ = ((2 * k).factorial : ℝ) * (Real.exp 1 * 8 * (c_im⁻¹ + 1)) * (2 : ℝ) ^ (2 * k) *
            (δ⁻¹) ^ (2 * k + 1) * Real.exp (-c_decay * δ⁻¹) := by
          rw [div_pow, inv_pow, pow_succ]
          field_simp [hδ_pos.ne']
  have h_top : Tendsto (fun x : ℝ => x ^ (2 * k + 1) * Real.exp (-c_decay * x)) atTop (nhds 0) := by
    let C_k : ℝ := ((2 * k + 1).factorial : ℝ) / (c_decay / 2) ^ (2 * k + 1)
    refine squeeze_zero' (g := fun x : ℝ => C_k * Real.exp (-(c_decay / 2) * x))
      ((eventually_ge_atTop (0 : ℝ)).mono fun x hx => by positivity) ?_ ?_
    · filter_upwards [eventually_ge_atTop 0] with x hx
      have hx_nn : 0 ≤ (c_decay / 2) * x := mul_nonneg (half_pos hc_decay).le hx
      have hexp := Real.pow_div_factorial_le_exp ((c_decay / 2) * x) hx_nn (2 * k + 1)
      rw [mul_pow, div_le_iff₀ (Nat.cast_pos.mpr (2 * k + 1).factorial_pos)] at hexp
      have hc_pos : (0 : ℝ) < (c_decay / 2) ^ (2 * k + 1) :=
        pow_pos (half_pos hc_decay) (2 * k + 1)
      rw [← le_div_iff₀' hc_pos] at hexp
      calc x ^ (2 * k + 1) * Real.exp (-c_decay * x)
          ≤ ((Real.exp ((c_decay / 2) * x) * ((2 * k + 1).factorial : ℝ)) /
              (c_decay / 2) ^ (2 * k + 1)) * Real.exp (-c_decay * x) :=
            mul_le_mul_of_nonneg_right hexp (Real.exp_pos _).le
        _ = C_k * (Real.exp ((c_decay / 2) * x) * Real.exp (-c_decay * x)) := by
            dsimp [C_k]; ring
        _ = C_k * Real.exp (-(c_decay / 2) * x) := by
            rw [← Real.exp_add]; congr 2; ring
    · have ht := Real.tendsto_exp_atBot.comp
        (tendsto_id.const_mul_atTop_of_neg (by linarith : -(c_decay / 2) < 0))
      simpa [mul_zero] using ht.const_mul C_k
  have h_inv_ten : Tendsto (fun δ : ℝ => (δ⁻¹) ^ (2 * k + 1) * Real.exp (-c_decay * δ⁻¹))
      (𝓝[>] (0 : ℝ)) (nhds 0) := h_top.comp tendsto_inv_nhdsGT_zero
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le' tendsto_const_nhds ?_
    (Eventually.of_forall fun _ => norm_nonneg _) h_bound_ev
  simpa [mul_zero, mul_assoc] using h_inv_ten.const_mul
    (((2 * k).factorial : ℝ) * (Real.exp 1 * 8 * (c_im⁻¹ + 1)) * (2 : ℝ) ^ (2 * k))

private lemma iteratedDeriv_cexp_const_mul' (c : ℂ) (n : ℕ) (w : ℂ) :
    iteratedDeriv n (fun z : ℂ => Complex.exp (c * z)) w = c ^ n * Complex.exp (c * w) := by
  induction n generalizing w with
  | zero => simp
  | succ n ih =>
    rw [iteratedDeriv_succ']
    have hderiv_fn : deriv (fun x : ℂ => Complex.exp (c * x)) =
        fun z : ℂ => c * Complex.exp (c * z) := by
      ext z
      have h : HasDerivAt (fun x : ℂ => Complex.exp (c * x)) (c * Complex.exp (c * z)) z := by
        simpa [mul_comm, mul_one] using ((hasDerivAt_id' z).const_mul c).cexp
      exact h.deriv
    rw [hderiv_fn, iteratedDeriv_const_mul, ih, pow_succ]
    · ring
    · exact (contDiffAt_const.mul contDiffAt_id).cexp

private lemma norm_iteratedDeriv_hardyCoshTerm_le (n : ℕ) (α : ℝ) :
    ‖iteratedDeriv n
      (fun w : ℂ => Complex.exp ((I * w) / 2) + Complex.exp (-(I * w) / 2)) (α : ℂ)‖ ≤ 2 := by
  have h1 : ContDiffAt ℂ n (fun w : ℂ => Complex.exp ((I * w) / 2)) (α : ℂ) :=
    ((contDiffAt_const.mul contDiffAt_id).div_const 2).cexp
  have h2 : ContDiffAt ℂ n (fun w : ℂ => Complex.exp (-(I * w) / 2)) (α : ℂ) :=
    ((contDiffAt_const.mul contDiffAt_id).neg.div_const 2).cexp
  change ‖iteratedDeriv n
    ((fun w : ℂ => Complex.exp ((I * w) / 2)) + (fun w : ℂ => Complex.exp (-(I * w) / 2)))
    (α : ℂ)‖ ≤ 2
  rw [iteratedDeriv_add h1 h2]
  have hf1 : (fun w : ℂ => Complex.exp ((I * w) / 2)) =
      fun w : ℂ => Complex.exp ((I / 2) * w) := by ext w; ring_nf
  have hf2 : (fun w : ℂ => Complex.exp (-(I * w) / 2)) =
      fun w : ℂ => Complex.exp ((-I / 2) * w) := by ext w; ring_nf
  rw [hf1, hf2, iteratedDeriv_cexp_const_mul', iteratedDeriv_cexp_const_mul']
  have hn1 : ‖(I / 2) ^ n * Complex.exp ((I / 2) * (α : ℂ))‖ ≤ 1 := by
    rw [norm_mul, norm_pow, norm_div, Complex.norm_I, Complex.norm_two,
      Complex.norm_exp, show ((I / 2) * (α : ℂ)).re = 0 by simp [Complex.mul_re],
      Real.exp_zero, mul_one]
    exact pow_le_one₀ (by positivity) (by norm_num)
  have hn2 : ‖(-I / 2) ^ n * Complex.exp ((-I / 2) * (α : ℂ))‖ ≤ 1 := by
    rw [norm_mul, norm_pow, norm_div, norm_neg, Complex.norm_I, Complex.norm_two,
      Complex.norm_exp, show ((-I / 2) * (α : ℂ)).re = 0 by simp [Complex.mul_re],
      Real.exp_zero, mul_one]
    exact pow_le_one₀ (by positivity) (by norm_num)
  exact ((norm_add_le _ _).trans (add_le_add hn1 hn2)).trans_eq (by norm_num)

private noncomputable def hardyGn (n : ℕ) (w : ℂ) : ℂ :=
  ((2 * Real.pi : ℝ) : ℂ)⁻¹ *
    ∫ t : ℝ, (t : ℂ) ^ n * Complex.exp (w * (t : ℂ)) * completedRiemannZeta (1 / 2 + (t : ℂ) * I)

private lemma hasDerivAt_hardyGn (n : ℕ) {w : ℂ} (hw : |w.re| < Real.pi / 4) :
    HasDerivAt (hardyGn n) (hardyGn (n + 1) w) w := by
  let α₀ : ℝ := (|w.re| + Real.pi / 4) / 2
  have hα₀_gt : |w.re| < α₀ := by dsimp [α₀]; linarith
  have hα₀_pos : 0 ≤ α₀ := (abs_nonneg _).trans hα₀_gt.le
  have hα₀_lt : α₀ < Real.pi / 4 := by dsimp [α₀]; linarith
  let ε : ℝ := α₀ - |w.re|
  have hε : 0 < ε := sub_pos.mpr hα₀_gt
  let F : ℂ → ℝ → ℂ := fun z t =>
    (t : ℂ) ^ n * Complex.exp (z * (t : ℂ)) * completedRiemannZeta (1 / 2 + (t : ℂ) * I)
  let F' : ℂ → ℝ → ℂ := fun z t =>
    (t : ℂ) ^ (n + 1) * Complex.exp (z * (t : ℂ)) * completedRiemannZeta (1 / 2 + (t : ℂ) * I)
  let bound : ℝ → ℝ := fun t =>
    |t| ^ (n + 1) * Real.exp (α₀ * |t|) * ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖
  have h_bound_int : Integrable bound :=
    integrable_abs_pow_mul_exp_mul_completedRiemannZeta (n + 1) hα₀_pos hα₀_lt
  have h_meas : ∀ᶠ z in 𝓝 w, AEStronglyMeasurable (F z) volume := by
    refine Eventually.of_forall fun z => ?_
    exact (((Complex.continuous_ofReal.pow n).mul
      (Complex.continuous_exp.comp (continuous_const.mul Complex.continuous_ofReal))).mul
      continuous_completedRiemannZeta_criticalLine).aestronglyMeasurable
  have h_int_w : Integrable (F w) := by
    have h_n := integrable_abs_pow_mul_exp_mul_completedRiemannZeta n hα₀_pos hα₀_lt
    have h_meas_w : AEStronglyMeasurable (F w) volume :=
      (((Complex.continuous_ofReal.pow n).mul
        (Complex.continuous_exp.comp (continuous_const.mul Complex.continuous_ofReal))).mul
        continuous_completedRiemannZeta_criticalLine).aestronglyMeasurable
    refine h_n.mono h_meas_w (ae_of_all _ fun t => ?_)
    dsimp [F]
    rw [norm_mul, norm_mul, norm_pow, Complex.norm_real, Real.norm_eq_abs,
      Complex.norm_exp, show (w * (t : ℂ)).re = w.re * t by simp [Complex.mul_re],
      abs_of_nonneg (mul_nonneg (mul_nonneg (pow_nonneg (abs_nonneg t) n) (Real.exp_pos _).le)
        (norm_nonneg _))]
    refine mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left ?_ (pow_nonneg (abs_nonneg t) n))
      (norm_nonneg _)
    rw [Real.exp_le_exp]
    exact (le_abs_self (w.re * t)).trans (by rw [abs_mul]; gcongr)
  have h_F'_meas : AEStronglyMeasurable (F' w) volume :=
    (((Complex.continuous_ofReal.pow (n + 1)).mul
      (Complex.continuous_exp.comp (continuous_const.mul Complex.continuous_ofReal))).mul
      continuous_completedRiemannZeta_criticalLine).aestronglyMeasurable
  have h_bound : ∀ᵐ t ∂volume, ∀ z ∈ Metric.ball w ε, ‖F' z t‖ ≤ bound t := by
    refine ae_of_all _ fun t z hz => ?_
    have hz_re : |z.re| ≤ α₀ := by
      have hre_diff : |z.re - w.re| ≤ ‖z - w‖ := by
        simpa [Complex.sub_re] using Complex.abs_re_le_norm (z - w)
      have hdist : ‖z - w‖ < ε := mem_ball_iff_norm.mp hz
      have htri : |z.re| ≤ |w.re| + |z.re - w.re| := by
        simpa using abs_add_le w.re (z.re - w.re)
      linarith
    dsimp [F', bound]
    rw [norm_mul, norm_mul, norm_pow, Complex.norm_real, Real.norm_eq_abs,
      Complex.norm_exp, show (z * (t : ℂ)).re = z.re * t by simp [Complex.mul_re]]
    refine mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left ?_
      (pow_nonneg (abs_nonneg t) (n + 1))) (norm_nonneg _)
    rw [Real.exp_le_exp]
    exact (le_abs_self (z.re * t)).trans
      (by rw [abs_mul]; exact mul_le_mul hz_re le_rfl (abs_nonneg t) hα₀_pos)
  have h_diff : ∀ᵐ t ∂volume, ∀ z ∈ Metric.ball w ε, HasDerivAt (fun x => F x t) (F' z t) z := by
    refine ae_of_all _ fun t z _ => ?_
    have h_inner : HasDerivAt (fun x : ℂ => x * (t : ℂ)) (t : ℂ) z := by
      simpa using (hasDerivAt_id z).mul_const (t : ℂ)
    have h_exp : HasDerivAt (fun x : ℂ => Complex.exp (x * (t : ℂ)))
        (Complex.exp (z * (t : ℂ)) * (t : ℂ)) z := h_inner.cexp
    have h_all := (h_exp.const_mul ((t : ℂ) ^ n)).mul_const
      (completedRiemannZeta (1 / 2 + (t : ℂ) * I))
    convert h_all using 1
    dsimp [F']
    rw [pow_succ]
    ring
  have h_res := hasDerivAt_integral_of_dominated_loc_of_deriv_le (Metric.ball_mem_nhds w hε)
    h_meas h_int_w h_F'_meas h_bound h_bound_int h_diff
  exact h_res.2.const_mul (((2 * Real.pi : ℝ) : ℂ)⁻¹)

private lemma iteratedDeriv_hardyG_mul_I (n : ℕ) {w : ℂ} (hw : |w.re| < Real.pi / 4) :
    iteratedDeriv n (fun z : ℂ => hardyG (I * z)) w = hardyGn n w := by
  induction n generalizing w with
  | zero =>
    rw [iteratedDeriv_zero]
    dsimp [hardyG, hardyGn]
    congr 2
    ext t
    congr 1
    rw [pow_zero, one_mul]
    congr 1
    calc -(I * w) * (t : ℂ) * I = -(I * I) * w * (t : ℂ) := by ring
      _ = w * (t : ℂ) := by rw [I_mul_I]; ring
  | succ n ih =>
    rw [iteratedDeriv_succ]
    have h_ev : iteratedDeriv n (fun z : ℂ => hardyG (I * z)) =ᶠ[𝓝 w] hardyGn n := by
      have h_open : IsOpen {z : ℂ | |z.re| < Real.pi / 4} :=
        isOpen_lt continuous_re.abs continuous_const
      filter_upwards [h_open.mem_nhds hw] with z hz
      exact ih hz
    rw [h_ev.deriv_eq, (hasDerivAt_hardyGn n hw).deriv]

private lemma iteratedDeriv_hardyPsi_mul_I_eq (n : ℕ) {α : ℝ} (hα : |α| < Real.pi / 4) :
    iteratedDeriv n (fun z : ℂ => hardyPsi (I * z)) (α : ℂ) = hardyGn n (α : ℂ) := by
  have h_open : IsOpen {z : ℂ | |z.re| < Real.pi / 4} :=
    isOpen_lt continuous_re.abs continuous_const
  have h_ev : (fun z : ℂ => hardyPsi (I * z)) =ᶠ[𝓝 (α : ℂ)] fun z : ℂ => hardyG (I * z) := by
    filter_upwards [h_open.mem_nhds (by simpa using hα)] with z hz
    exact (hardyG_eq_hardyPsi (by simpa using hz)).symm
  rw [h_ev.iteratedDeriv_eq n, iteratedDeriv_hardyG_mul_I n (by simpa using hα)]

private lemma hardyGn_even_re (k : ℕ) {α : ℝ} (hα : |α| < Real.pi / 4) :
    (2 * Real.pi) * (hardyGn (2 * k) (α : ℂ)).re =
      ∫ t in Ioi (0 : ℝ),
        t ^ (2 * k) * (Real.exp (α * t) + Real.exp (-α * t)) *
          (completedRiemannZeta (1 / 2 + (t : ℂ) * I)).re := by
  let Λre : ℝ → ℝ := fun t => (completedRiemannZeta (1 / 2 + (t : ℂ) * I)).re
  have hΛ_even : ∀ t : ℝ, Λre (-t) = Λre t := by
    intro t
    dsimp [Λre]
    have h1 := completedRiemannZeta_one_sub (1 / 2 + (t : ℂ) * I)
    rw [show 1 - (1 / 2 + (t : ℂ) * I) = 1 / 2 + ((-t : ℝ) : ℂ) * I by push_cast; ring] at h1
    rw [h1]
  have h_integrand_eq : (fun t : ℝ => (t : ℂ) ^ (2 * k) * Complex.exp ((α : ℂ) * (t : ℂ)) *
      completedRiemannZeta (1 / 2 + (t : ℂ) * I)) =
      fun t : ℝ => ((t ^ (2 * k) * Real.exp (α * t) * Λre t : ℝ) : ℂ) := by
    ext t
    have h_conj : ((Λre t : ℝ) : ℂ) = completedRiemannZeta (1 / 2 + (t : ℂ) * I) :=
      Complex.conj_eq_iff_re.mp (by
        rw [Complex.conj_eq_iff_im]
        exact completedRiemannZeta_half_add_mul_I_im t)
    rw [← h_conj]
    push_cast
    ring
  have h_int_full : Integrable (fun t : ℝ => t ^ (2 * k) * Real.exp (α * t) * Λre t) := by
    have h_raw := integrable_abs_pow_mul_exp_mul_completedRiemannZeta (2 * k) (abs_nonneg α) hα
    have h_cont : Continuous (fun t : ℝ => t ^ (2 * k) * Real.exp (α * t) * Λre t) :=
      ((continuous_id.pow (2 * k)).mul
        (Real.continuous_exp.comp (continuous_const.mul continuous_id))).mul
        (Complex.continuous_re.comp continuous_completedRiemannZeta_criticalLine)
    refine h_raw.mono h_cont.aestronglyMeasurable (ae_of_all _ fun t => ?_)
    have hΛ_norm : |Λre t| = ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖ := by
      rw [Complex.norm_def, Complex.normSq_apply, completedRiemannZeta_half_add_mul_I_im t,
        mul_zero, add_zero, Real.sqrt_mul_self_eq_abs]
    rw [Real.norm_eq_abs, abs_mul, abs_mul, abs_pow, abs_of_pos (Real.exp_pos _), hΛ_norm,
      Real.norm_of_nonneg (by positivity)]
    have h_exp : Real.exp (α * t) ≤ Real.exp (|α| * |t|) :=
      Real.exp_le_exp.mpr ((le_abs_self (α * t)).trans (by rw [abs_mul]))
    exact mul_le_mul_of_nonneg_right
      (mul_le_mul_of_nonneg_left h_exp (pow_nonneg (abs_nonneg t) _)) (norm_nonneg _)
  have h_int_re : (hardyGn (2 * k) (α : ℂ)).re =
      (2 * Real.pi)⁻¹ * ∫ t : ℝ, t ^ (2 * k) * Real.exp (α * t) * Λre t := by
    dsimp [hardyGn]
    have h_int_c : Integrable (fun t : ℝ => ((t ^ (2 * k) * Real.exp (α * t) * Λre t : ℝ) : ℂ)) :=
      Complex.ofRealCLM.integrable_comp h_int_full
    have h_re_int : (∫ t : ℝ, ((t ^ (2 * k) * Real.exp (α * t) * Λre t : ℝ) : ℂ)).re =
        ∫ t : ℝ, t ^ (2 * k) * Real.exp (α * t) * Λre t := by
      change Complex.reCLM (∫ t : ℝ, ((t ^ (2 * k) * Real.exp (α * t) * Λre t : ℝ) : ℂ)) = _
      rw [← Complex.reCLM.integral_comp_comm h_int_c]
      simp only [Complex.reCLM_apply, Complex.ofReal_re]
    rw [h_integrand_eq, ← Complex.ofReal_inv (2 * Real.pi), Complex.re_ofReal_mul, h_re_int]
  rw [h_int_re, ← mul_assoc, mul_inv_cancel₀ (by positivity : 2 * Real.pi ≠ 0), one_mul]
  have h_split : ∫ t : ℝ, t ^ (2 * k) * Real.exp (α * t) * Λre t =
      (∫ t in Iic (0 : ℝ), t ^ (2 * k) * Real.exp (α * t) * Λre t) +
      (∫ t in Ioi (0 : ℝ), t ^ (2 * k) * Real.exp (α * t) * Λre t) := by
    rw [← MeasureTheory.setIntegral_union (Iic_disjoint_Ioi (le_refl (0 : ℝ))) measurableSet_Ioi
      h_int_full.integrableOn h_int_full.integrableOn, Iic_union_Ioi, setIntegral_univ]
  have h_Iic : ∫ t in Iic (0 : ℝ), t ^ (2 * k) * Real.exp (α * t) * Λre t =
      ∫ t in Ioi (0 : ℝ), t ^ (2 * k) * Real.exp (-α * t) * Λre t := by
    have h_fn : (fun t : ℝ => t ^ (2 * k) * Real.exp (α * t) * Λre t) =
        fun t : ℝ => (fun x : ℝ => x ^ (2 * k) * Real.exp (-α * x) * Λre x) (-t) := by
      ext t
      dsimp only
      have h_even_pow : (-t) ^ (2 * k) = t ^ (2 * k) := by
        rw [pow_mul, neg_sq, ← pow_mul]
      rw [h_even_pow, hΛ_even t, neg_mul]
      ring_nf
    rw [h_fn, integral_comp_neg_Iic 0 (fun x : ℝ => x ^ (2 * k) * Real.exp (-α * x) * Λre x),
      neg_zero]
  have h_Ioi_neg_int :
      IntegrableOn (fun t : ℝ => t ^ (2 * k) * Real.exp (-α * t) * Λre t) (Ioi 0) := by
    have h_raw := integrable_abs_pow_mul_exp_mul_completedRiemannZeta (2 * k) (abs_nonneg α) hα
    refine (h_raw.integrableOn (s := Ioi 0)).mono' ?_ (ae_of_all _ fun t => ?_)
    · exact (((continuous_id.pow (2 * k)).mul
        (Real.continuous_exp.comp (continuous_const.mul continuous_id))).mul
        (Complex.continuous_re.comp
          continuous_completedRiemannZeta_criticalLine)).aestronglyMeasurable
    · have hΛ_norm : |Λre t| = ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖ := by
        rw [Complex.norm_def, Complex.normSq_apply, completedRiemannZeta_half_add_mul_I_im t,
          mul_zero, add_zero, Real.sqrt_mul_self_eq_abs]
      rw [Real.norm_eq_abs, abs_mul, abs_mul, abs_pow, abs_of_pos (Real.exp_pos _), hΛ_norm]
      have h_exp : Real.exp (-α * t) ≤ Real.exp (|α| * |t|) :=
        Real.exp_le_exp.mpr ((le_abs_self (-α * t)).trans (by rw [abs_mul, abs_neg]))
      exact mul_le_mul_of_nonneg_right
        (mul_le_mul_of_nonneg_left h_exp (pow_nonneg (abs_nonneg t) _)) (norm_nonneg _)
  rw [h_split, h_Iic, ← integral_add h_Ioi_neg_int h_int_full.integrableOn]
  refine setIntegral_congr_fun measurableSet_Ioi fun t _ => ?_
  ring

private lemma hardyZ_unbounded_sign_changes :
    ∀ T : ℝ, ∃ a b : ℝ, T < a ∧ a ≤ b ∧ hardyZ a * hardyZ b ≤ 0 := by
  by_contra h_neg
  push Not at h_neg
  rcases h_neg with ⟨T₀, hT₀⟩
  let a₀ : ℝ := max T₀ 1 + 1
  have ha₀_gt_T₀ : T₀ < a₀ := lt_of_le_of_lt (le_max_left T₀ 1) (lt_add_one _)
  have ha₀_gt_one : 1 < a₀ := lt_of_le_of_lt (le_max_right T₀ 1) (lt_add_one _)
  have ha₀_pos : 0 < a₀ := by linarith
  have ha₀_ne : hardyZ a₀ ≠ 0 := by
    have h0 := hT₀ a₀ a₀ ha₀_gt_T₀ le_rfl
    intro hz
    rw [hz, zero_mul] at h0
    exact lt_irrefl 0 h0
  let sgn : ℝ := if 0 < hardyZ a₀ then 1 else -1
  have hsgn_abs : |sgn| = 1 := by
    dsimp [sgn]
    split_ifs <;> norm_num
  have h_pos_after : ∀ t : ℝ, a₀ ≤ t → 0 < sgn * hardyZ t := by
    intro t ht
    have hmul := hT₀ a₀ t ha₀_gt_T₀ ht
    dsimp [sgn]
    split_ifs with ha
    · rw [one_mul]
      exact (mul_pos_iff.mp hmul).elim (fun ⟨_, hb⟩ => hb) (fun ⟨ha_neg, _⟩ => by linarith)
    · have ha_neg : hardyZ a₀ < 0 := lt_of_le_of_ne (le_of_not_gt ha) ha₀_ne
      have ht_neg : hardyZ t < 0 :=
        (mul_pos_iff.mp hmul).elim (fun ⟨ha_pos, _⟩ => by linarith) (fun ⟨_, hb⟩ => hb)
      nlinarith
  let Λre : ℝ → ℝ := fun t => (completedRiemannZeta (1 / 2 + (t : ℂ) * I)).re
  have h_Λre_pos : ∀ t : ℝ, a₀ ≤ t → 0 < sgn * Λre t := by
    intro t ht
    have hΓ : 0 < ‖Gammaℝ (1 / 2 + (t : ℂ) * I)‖ :=
      norm_pos_iff.mpr (Gammaℝ_ne_zero_of_re_pos (by simp))
    have hZ : Λre t = hardyZ t * ‖Gammaℝ (1 / 2 + (t : ℂ) * I)‖ := by
      dsimp [hardyZ, Λre]
      rw [div_mul_cancel₀ _ hΓ.ne']
    rw [hZ, ← mul_assoc]
    exact mul_pos (h_pos_after t ht) hΓ
  have h_Λre_cont : Continuous Λre :=
    Complex.continuous_re.comp continuous_completedRiemannZeta_criticalLine
  obtain ⟨t_min, ht_min_mem, ht_min⟩ :=
    isCompact_Icc.exists_isMinOn (nonempty_Icc.mpr (by linarith : a₀ + 1 ≤ a₀ + 2))
      ((continuous_const (y := sgn)).mul h_Λre_cont).continuousOn
  let m_pos : ℝ := sgn * Λre t_min
  have hm_pos : 0 < m_pos := h_Λre_pos t_min (by linarith [ht_min_mem.1])
  obtain ⟨M_low, hM_low⟩ := isCompact_Icc.exists_bound_of_continuousOn
    (f := Λre) h_Λre_cont.continuousOn (s := Set.Icc 0 a₀)
  let M_abs : ℝ := max M_low 0
  have hM_abs_nn : 0 ≤ M_abs := le_max_right _ _
  let C_low : ℝ := a₀ * (2 * Real.exp ((Real.pi / 4) * a₀)) * M_abs
  have h_every_k : ∀ k : ℕ, m_pos * (a₀ + 1) ^ (2 * k) - C_low * a₀ ^ (2 * k) ≤ 6 * Real.pi := by
    intro k
    have h_ten_k := tendsto_iteratedDeriv_hardyThetaTerm k
    have h_ev_lt : ∀ᶠ δ in 𝓝[>] (0 : ℝ),
        ‖iteratedDeriv (2 * k) (fun w : ℂ => hardyThetaTerm (I * w))
          ((Real.pi / 4 - δ : ℝ) : ℂ)‖ < 1 :=
      h_ten_k.eventually (gt_mem_nhds one_pos)
    obtain ⟨δ, hδ_lt, hδ_gt⟩ :=
      (h_ev_lt.and (Ioo_mem_nhdsGT (by positivity : (0 : ℝ) < Real.pi / 8))).exists
    let α : ℝ := Real.pi / 4 - δ
    have hα_pos : 0 < α := by dsimp [α]; linarith [hδ_gt.2]
    have hα_lt : α < Real.pi / 4 := by dsimp [α]; linarith [hδ_gt.1]
    have hα_abs : |α| < Real.pi / 4 := by rwa [abs_of_pos hα_pos]
    have h_theta_diff : ContDiffAt ℂ (2 * k) (fun w : ℂ => hardyThetaTerm (I * w)) (α : ℂ) := by
      have h_open : IsOpen {w : ℂ | |w.re| < Real.pi / 4} :=
        isOpen_lt continuous_re.abs continuous_const
      have h_diff_strip : DifferentiableOn ℂ (fun w : ℂ => hardyThetaTerm (I * w))
          {w : ℂ | |w.re| < Real.pi / 4} := by
        intro w hw
        have hwim : |(I * w).im| < Real.pi / 4 := by simpa using hw
        have hθ := differentiableAt_jacobiTheta (im_I_mul_exp_two_mul_pos hwim)
        have h_cexp : DifferentiableAt ℂ (fun x : ℂ => Complex.exp (2 * (I * x))) w :=
          ((differentiableAt_const (2 : ℂ)).mul
            ((differentiableAt_const I).mul differentiableAt_id)).cexp
        have h_jac : DifferentiableAt ℂ
            (jacobiTheta ∘ fun x : ℂ => I * Complex.exp (2 * (I * x))) w :=
          hθ.comp w ((differentiableAt_const I).mul h_cexp)
        have h_left : DifferentiableAt ℂ (fun x : ℂ => Complex.exp ((I * x) / 2)) w :=
          (((differentiableAt_const I).mul differentiableAt_id).div_const 2).cexp
        change DifferentiableWithinAt ℂ
          (fun x : ℂ => Complex.exp ((I * x) / 2) *
            jacobiTheta (I * Complex.exp (2 * (I * x)))) _ w
        exact (h_left.mul h_jac).differentiableWithinAt
      exact ((h_diff_strip.analyticOnNhd h_open) (α : ℂ) (by simpa using hα_abs)).contDiffAt.of_le
        (by exact_mod_cast le_top)
    have h_cosh_diff : ContDiffAt ℂ (2 * k)
        (fun w : ℂ => Complex.exp ((I * w) / 2) + Complex.exp (-(I * w) / 2)) (α : ℂ) := by
      have h1 : ContDiffAt ℂ (2 * k) (fun w : ℂ => Complex.exp ((I * w) / 2)) (α : ℂ) :=
        ((contDiffAt_const.mul contDiffAt_id).div_const 2).cexp
      have h2 : ContDiffAt ℂ (2 * k) (fun w : ℂ => Complex.exp (-(I * w) / 2)) (α : ℂ) :=
        ((contDiffAt_const.mul contDiffAt_id).neg.div_const 2).cexp
      exact h1.add h2
    have h_psi_split : (fun w : ℂ => hardyPsi (I * w)) =
        (fun w : ℂ => hardyThetaTerm (I * w)) -
          (fun w : ℂ => Complex.exp ((I * w) / 2) + Complex.exp (-(I * w) / 2)) := by
      ext w; rfl
    have h_norm_Gn : ‖hardyGn (2 * k) (α : ℂ)‖ ≤ 3 := by
      rw [← iteratedDeriv_hardyPsi_mul_I_eq (2 * k) hα_abs, h_psi_split,
        iteratedDeriv_sub h_theta_diff h_cosh_diff]
      calc ‖iteratedDeriv (2 * k) (fun w : ℂ => hardyThetaTerm (I * w)) (α : ℂ) -
            iteratedDeriv (2 * k)
              (fun w : ℂ => Complex.exp ((I * w) / 2) + Complex.exp (-(I * w) / 2)) (α : ℂ)‖
          ≤ ‖iteratedDeriv (2 * k) (fun w : ℂ => hardyThetaTerm (I * w)) (α : ℂ)‖ +
            ‖iteratedDeriv (2 * k)
              (fun w : ℂ => Complex.exp ((I * w) / 2) + Complex.exp (-(I * w) / 2)) (α : ℂ)‖ :=
            norm_sub_le _ _
        _ ≤ 1 + 2 := add_le_add hδ_lt.le (norm_iteratedDeriv_hardyCoshTerm_le (2 * k) α)
        _ = 3 := by norm_num
    let F_k : ℝ → ℝ :=
      fun t => t ^ (2 * k) * (Real.exp (α * t) + Real.exp (-α * t)) * (sgn * Λre t)
    have h_Fk_int : IntegrableOn F_k (Ioi 0) := by
      have h_raw := integrable_abs_pow_mul_exp_mul_completedRiemannZeta (2 * k) hα_pos.le hα_lt
      refine ((h_raw.const_mul 2).integrableOn (s := Ioi 0)).mono' ?_ (ae_of_all _ fun t => ?_)
      · exact (((continuous_id.pow (2 * k)).mul
          ((Real.continuous_exp.comp (continuous_const.mul continuous_id)).add
            (Real.continuous_exp.comp (continuous_const.mul continuous_id)))).mul
          (continuous_const.mul h_Λre_cont)).aestronglyMeasurable
      · have hΛ_norm : |Λre t| = ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖ := by
          rw [Complex.norm_def, Complex.normSq_apply, completedRiemannZeta_half_add_mul_I_im t,
            mul_zero, add_zero, Real.sqrt_mul_self_eq_abs]
        have h_exp_sum : Real.exp (α * t) + Real.exp (-α * t) ≤ 2 * Real.exp (α * |t|) := by
          have h1 : Real.exp (α * t) ≤ Real.exp (α * |t|) :=
            Real.exp_le_exp.mpr (mul_le_mul_of_nonneg_left (le_abs_self t) hα_pos.le)
          have h2 : Real.exp (-α * t) ≤ Real.exp (α * |t|) :=
            Real.exp_le_exp.mpr
              (by rw [neg_mul, ← mul_neg]; exact mul_le_mul_of_nonneg_left (neg_le_abs t) hα_pos.le)
          linarith
        dsimp [F_k]
        rw [abs_mul, abs_mul, abs_pow,
          abs_of_pos (add_pos (Real.exp_pos _) (Real.exp_pos _)), abs_mul, hsgn_abs, one_mul,
          hΛ_norm]
        calc |t| ^ (2 * k) * (Real.exp (α * t) + Real.exp (-α * t)) *
              ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖
            ≤ |t| ^ (2 * k) * (2 * Real.exp (α * |t|)) *
                ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖ := by gcongr
          _ = 2 * (|t| ^ (2 * k) * Real.exp (α * |t|) *
                ‖completedRiemannZeta (1 / 2 + (t : ℂ) * I)‖) := by ring
    have h_upper : ∫ t in Ioi (0 : ℝ), F_k t ≤ 6 * Real.pi := by
      have h_eq : ∫ t in Ioi (0 : ℝ), F_k t =
          sgn * ((2 * Real.pi) * (hardyGn (2 * k) (α : ℂ)).re) := by
        calc ∫ t in Ioi (0 : ℝ), F_k t
            = ∫ t in Ioi (0 : ℝ), sgn * (t ^ (2 * k) *
                (Real.exp (α * t) + Real.exp (-α * t)) * Λre t) := by
                refine setIntegral_congr_fun measurableSet_Ioi fun t _ => ?_
                dsimp [F_k]; ring
          _ = sgn * ∫ t in Ioi (0 : ℝ), t ^ (2 * k) *
                (Real.exp (α * t) + Real.exp (-α * t)) * Λre t :=
                integral_const_mul _ _
          _ = sgn * ((2 * Real.pi) * (hardyGn (2 * k) (α : ℂ)).re) := by
                rw [hardyGn_even_re k hα_abs]
      calc ∫ t in Ioi (0 : ℝ), F_k t
          ≤ |∫ t in Ioi (0 : ℝ), F_k t| := le_abs_self _
        _ = |sgn * ((2 * Real.pi) * (hardyGn (2 * k) (α : ℂ)).re)| := by rw [h_eq]
        _ = 1 * (2 * Real.pi * |(hardyGn (2 * k) (α : ℂ)).re|) := by
            rw [abs_mul, hsgn_abs, abs_mul, abs_of_pos (by positivity : (0 : ℝ) < 2 * Real.pi)]
        _ ≤ 2 * Real.pi * ‖hardyGn (2 * k) (α : ℂ)‖ := by
            rw [one_mul]; gcongr; exact Complex.abs_re_le_norm _
        _ ≤ 2 * Real.pi * 3 := by gcongr
        _ = 6 * Real.pi := by ring
    have h_split_0 : ∫ t in Ioi (0 : ℝ), F_k t =
        (∫ t in Ioc 0 a₀, F_k t) + (∫ t in Ioi a₀, F_k t) := by
      have h_union : Ioc (0 : ℝ) a₀ ∪ Ioi a₀ = Ioi (0 : ℝ) := Ioc_union_Ioi_eq_Ioi ha₀_pos.le
      have h_disj : Disjoint (Ioc (0 : ℝ) a₀) (Ioi a₀) := Ioc_disjoint_Ioi_same
      have h1 : IntegrableOn F_k (Ioc 0 a₀) := h_Fk_int.mono_set Ioc_subset_Ioi_self
      have h2 : IntegrableOn F_k (Ioi a₀) := h_Fk_int.mono_set (Ioi_subset_Ioi ha₀_pos.le)
      rw [← h_union, setIntegral_union h_disj measurableSet_Ioi h1 h2]
    have h_low_bd : -C_low * a₀ ^ (2 * k) ≤ ∫ t in Ioc 0 a₀, F_k t := by
      have h_pt : ∀ t ∈ Ioc (0 : ℝ) a₀,
          ‖F_k t‖ ≤ a₀ ^ (2 * k) * (2 * Real.exp ((Real.pi / 4) * a₀)) * M_abs := by
        intro t ht
        have h_t_nn : 0 ≤ t := ht.1.le
        have h_exp1 : Real.exp (α * t) ≤ Real.exp ((Real.pi / 4) * a₀) :=
          Real.exp_le_exp.mpr (mul_le_mul hα_lt.le ht.2 h_t_nn (by positivity))
        have h_exp2 : Real.exp (-α * t) ≤ Real.exp ((Real.pi / 4) * a₀) := by
          rw [Real.exp_le_exp]
          have hneg : -α * t ≤ 0 := mul_nonpos_of_nonpos_of_nonneg (by linarith) h_t_nn
          exact hneg.trans (mul_nonneg (by positivity) ha₀_pos.le)
        have h_Λ : |Λre t| ≤ M_abs := by
          have h := hM_low t ⟨h_t_nn, ht.2⟩
          exact (le_trans (by rfl) h).trans (le_max_left _ _)
        dsimp [F_k]
        change |t ^ (2 * k) * (Real.exp (α * t) + Real.exp (-α * t)) * (sgn * Λre t)| ≤
          a₀ ^ (2 * k) * (2 * Real.exp ((Real.pi / 4) * a₀)) * M_abs
        rw [abs_mul, abs_mul, abs_pow,
          abs_of_pos (add_pos (Real.exp_pos _) (Real.exp_pos _)), abs_mul, hsgn_abs, one_mul,
          abs_of_nonneg h_t_nn]
        have h_pow : t ^ (2 * k) ≤ a₀ ^ (2 * k) := pow_le_pow_left₀ h_t_nn ht.2 (2 * k)
        have h_esum : Real.exp (α * t) + Real.exp (-α * t) ≤ 2 * Real.exp ((Real.pi / 4) * a₀) := by
          linarith
        exact mul_le_mul (mul_le_mul h_pow h_esum (by positivity) (by positivity))
          h_Λ (abs_nonneg _) (by positivity)
      have h_int_le : |∫ t in Ioc 0 a₀, F_k t| ≤
          a₀ ^ (2 * k) * (2 * Real.exp ((Real.pi / 4) * a₀)) * M_abs * a₀ := by
        simpa [Real.volume_real_Ioc_of_le ha₀_pos.le, sub_zero, Real.norm_eq_abs] using
          norm_setIntegral_le_of_norm_le_const
            (measure_Ioc_lt_top : volume (Ioc (0 : ℝ) a₀) < ⊤) h_pt
      have h_abs_le : |∫ t in Ioc 0 a₀, F_k t| ≤ C_low * a₀ ^ (2 * k) :=
        h_int_le.trans (le_of_eq (by dsimp [C_low]; ring))
      linarith [(abs_le.mp h_abs_le).1]
    have h_tail_bd : m_pos * (a₀ + 1) ^ (2 * k) ≤ ∫ t in Ioi a₀, F_k t := by
      have h_sub : Ioc (a₀ + 1) (a₀ + 2) ⊆ Ioi a₀ := fun t ht => lt_of_le_of_lt (by linarith) ht.1
      have h_nonneg_tail : ∀ t ∈ Ioi a₀, 0 ≤ F_k t := by
        intro t ht
        have ht_pos : 0 < t := lt_trans ha₀_pos ht
        have hΛ_pos := h_Λre_pos t ht.le
        dsimp [F_k]
        exact mul_nonneg (mul_nonneg (pow_nonneg ht_pos.le _)
          (add_pos (Real.exp_pos _) (Real.exp_pos _)).le) hΛ_pos.le
      have h_mono : ∫ t in Ioc (a₀ + 1) (a₀ + 2), F_k t ≤ ∫ t in Ioi a₀, F_k t :=
        setIntegral_mono_set (h_Fk_int.mono_set (Ioi_subset_Ioi ha₀_pos.le))
          (ae_restrict_of_forall_mem measurableSet_Ioi h_nonneg_tail) h_sub.eventuallyLE
      have h_const_le : ∫ t in Ioc (a₀ + 1) (a₀ + 2), (m_pos * (a₀ + 1) ^ (2 * k)) ≤
          ∫ t in Ioc (a₀ + 1) (a₀ + 2), F_k t := by
        refine setIntegral_mono_on (integrableOn_const (hs := measure_Ioc_lt_top.ne))
          (h_Fk_int.mono_set (h_sub.trans (Ioi_subset_Ioi ha₀_pos.le))) measurableSet_Ioc ?_
        intro t ht
        have h_t_ge : a₀ + 1 ≤ t := ht.1.le
        have h_pow : (a₀ + 1) ^ (2 * k) ≤ t ^ (2 * k) := by gcongr
        have h_exp_ge : 1 ≤ Real.exp (α * t) + Real.exp (-α * t) := by
          have : 1 ≤ Real.exp (α * t) := Real.one_le_exp (mul_nonneg hα_pos.le (by linarith))
          linarith [Real.exp_pos (-α * t)]
        have h_mem : t ∈ Set.Icc (a₀ + 1) (a₀ + 2) := ⟨ht.1.le, ht.2⟩
        have h_m : m_pos ≤ sgn * Λre t := ht_min h_mem
        dsimp [F_k]
        calc m_pos * (a₀ + 1) ^ (2 * k)
            ≤ (a₀ + 1) ^ (2 * k) * 1 * m_pos := by ring_nf; rfl
          _ ≤ t ^ (2 * k) * (Real.exp (α * t) + Real.exp (-α * t)) * (sgn * Λre t) :=
              mul_le_mul (mul_le_mul h_pow h_exp_ge zero_le_one (pow_nonneg (by linarith) _))
                h_m hm_pos.le (mul_nonneg (pow_nonneg (by linarith) _)
                  (add_pos (Real.exp_pos _) (Real.exp_pos _)).le)
      have h_vol : ∫ t in Ioc (a₀ + 1) (a₀ + 2), (m_pos * (a₀ + 1) ^ (2 * k)) =
          m_pos * (a₀ + 1) ^ (2 * k) := by
        rw [setIntegral_const, smul_eq_mul, Real.volume_real_Ioc_of_le (by linarith),
          show a₀ + 2 - (a₀ + 1) = 1 by ring, one_mul]
      linarith
    linarith
  have h_ratio_gt : 1 < ((a₀ + 1) / a₀) ^ 2 := by
    have h1 : 1 < (a₀ + 1) / a₀ := by
      rw [one_lt_div ha₀_pos]
      linarith
    exact one_lt_pow₀ h1 (by norm_num)
  have h_tendsto : Tendsto (fun k : ℕ => m_pos * (((a₀ + 1) / a₀) ^ 2) ^ k) atTop atTop :=
    (tendsto_pow_atTop_atTop_of_one_lt h_ratio_gt).const_mul_atTop hm_pos
  rw [Filter.tendsto_atTop] at h_tendsto
  obtain ⟨k, hk⟩ := h_tendsto (C_low + 6 * Real.pi + 1) |>.exists
  have hk_bound := h_every_k k
  have ha0_ge1 : 1 ≤ a₀ ^ (2 * k) := one_le_pow₀ ha₀_gt_one.le
  have h_div : m_pos * (((a₀ + 1) / a₀) ^ 2) ^ k =
      m_pos * (a₀ + 1) ^ (2 * k) / a₀ ^ (2 * k) := by
    rw [← pow_mul, div_pow]
    ring
  rw [h_div, le_div_iff₀ (pow_pos ha₀_pos _)] at hk
  have hk1 : (C_low + 6 * Real.pi) * a₀ ^ (2 * k) < (C_low + 6 * Real.pi + 1) * a₀ ^ (2 * k) := by
    nlinarith [pow_pos ha₀_pos (2 * k)]
  have hk2 : 6 * Real.pi ≤ 6 * Real.pi * a₀ ^ (2 * k) := by
    nlinarith [Real.pi_pos, ha0_ge1]
  linarith

end UnconditionalHardy

/-- **Hardy's (1914) Theorem** (unconditional): the Riemann zeta function has infinitely many
zeros on the critical line `Re(s) = 1 / 2`. -/
theorem infinite_criticalLine_zeros :
    {t : ℝ | riemannZeta (criticalLine t) = 0}.Infinite :=
  infinite_criticalLine_zeros_of_sign_changes hardyZ_unbounded_sign_changes

/-- **Hardy's (1914) Theorem for `hardyZ`** (unconditional): Hardy's `Z`-function has infinitely
many real zeros. -/
theorem infinite_hardyZ_zeros :
    {t : ℝ | hardyZ t = 0}.Infinite :=
  infinite_hardyZ_zeros_of_sign_changes hardyZ_unbounded_sign_changes
