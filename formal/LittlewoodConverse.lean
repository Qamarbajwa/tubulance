import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.NumberTheory.LSeries.Dirichlet
import Mathlib.NumberTheory.LSeries.Nonvanishing
import Mathlib.NumberTheory.LSeries.SumCoeff
import Mathlib.Analysis.MellinTransform
import Mathlib.Analysis.MellinInversion
import Mathlib.Analysis.Complex.CauchyIntegral
import Mathlib.Analysis.Complex.HasPrimitives
import Mathlib.Analysis.Complex.BorelCaratheodory
import Mathlib.Analysis.Complex.Hadamard
import Mathlib.Analysis.Analytic.Uniqueness
import RiemannBlueprint.ClassicalAnalyticInterface
import RiemannBlueprint.MellinFracPart
import RiemannBlueprint.LittlewoodForward

/-!
# Littlewood's (1912) Converse & Unconditional Mellin–Mertens Equivalence

Unconditional Lean 4 + Mathlib4 formalization of Littlewood's (1912) converse theorem
`_root_.RiemannHypothesis → MertensBound`, eliminating `rh_implies_mertens_bound` from
`ClassicalAnalyticInterface` and rendering `RiemannHypothesis ↔ MertensBound` and
Mellin–Mertens inversion fully unconditional.

## Architecture
- **Stage 1:** Unconditional polynomial strip bound `‖ζ(s)‖ ≤ 3 * ‖s‖` on
  `{1/2 ≤ Re(s), 1 ≤ |Im(s)|}` from `MellinFracPart.mellin_recipFract_unit_interval_of_pos_re`,
  together with uniform `Re(s) > 1` lower/upper bounds at `Re(s) = 2` and `‖ζ'/ζ(s)‖ ≤ C(δ)`
  on `Re(s) ≥ 1 + δ`.
- **Stage 2:** Under `_root_.RiemannHypothesis`, construction of holomorphic `L = log ζ` on
  `ball (2 + t * I) R₀` (`R₀ < 3/2`) via `DifferentiableOn.isExactOn_ball`, MVT bound on
  `closedBall (2 + t * I) (1 - η)`, and `Complex.borelCaratheodory` (`‖L z‖ ≤ M₃ * log t`).
- **Stage 3:** Hadamard three-lines (`HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'`)
  on `w ↦ L (2 + t * I + r₁ * exp w)` yielding Littlewood's conditional inverse bound
  `‖zetaInv s‖ ≤ C * (1 + |s.im|) ^ δ` uniformly on `σ₀ ≤ s.re` for every `σ₀ > 1/2, δ > 0`.
- **Stage 4:** Compactly supported trapezoidal cutoff `cutoffPhi X H` (`[1/2, X + H]`),
  closed-form Mellin transform, and exact Mellin–Mertens inversion via
  `MeasureTheory.mellinInv_mellin_eq` + `integral_tsum`.
- **Stage 5:** Cauchy rectangle contour shift (`Complex.integral_boundary_rect_eq_zero_of_differentiableOn`)
  from `σ = 2` to `σ₀ = 1/2 + ε/2` with `H = √X`, yielding `_root_.RiemannHypothesis → MertensBound`.
-/

set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.style.openClassical false
open scoped Classical ArithmeticFunction.Moebius LSeries.notation Topology

namespace RiemannBlueprint.LittlewoodConverse

open Asymptotics Complex Filter MeasureTheory Metric Set Real

/-! ### Stage 1: Unconditional `riemannZeta` Strip and Right-Half-Plane Bounds -/

/-- Removable-singularity inverse of `riemannZeta`: equals `0` at `s = 1` and `(ζ s)⁻¹` elsewhere. -/
noncomputable def zetaInv (s : ℂ) : ℂ :=
  if s = 1 then 0 else (riemannZeta s)⁻¹

/-- `zetaInv` has complex derivative `1` at `s = 1` from the residue `(s - 1) * ζ(s) → 1`. -/
theorem hasDerivAt_zetaInv_one : HasDerivAt zetaInv 1 1 := by
  rw [hasDerivAt_iff_tendsto_slope, slope_fun_def_field]
  simp only [zetaInv, ↓reduceIte, sub_zero]
  have h_res := riemannZeta_residue_one
  have h_inv : Tendsto (fun z : ℂ => ((z - 1) * riemannZeta z)⁻¹) (𝓝[≠] 1) (𝓝 (1⁻¹ : ℂ)) :=
    h_res.inv₀ one_ne_zero
  rw [inv_one] at h_inv
  refine h_inv.congr' ?_
  filter_upwards [self_mem_nhdsWithin] with z hz
  have hne : z ≠ 1 := hz
  simp only [hne, ↓reduceIte]
  have hsub : z - 1 ≠ 0 := sub_ne_zero.mpr hne
  by_cases hζ : riemannZeta z = 0
  · simp [hζ]
  · field_simp [hsub, hζ]

theorem differentiableAt_zetaInv_one : DifferentiableAt ℂ zetaInv 1 :=
  hasDerivAt_zetaInv_one.differentiableAt

/-- For any `s ≠ 1` with `riemannZeta s ≠ 0`, `zetaInv` is differentiable at `s`. -/
theorem differentiableAt_zetaInv {s : ℂ} (hs1 : s ≠ 1) (hζ : riemannZeta s ≠ 0) :
    DifferentiableAt ℂ zetaInv s := by
  have h_ev : zetaInv =ᶠ[𝓝 s] (fun z => (riemannZeta z)⁻¹) := by
    filter_upwards [isOpen_ne.mem_nhds hs1] with z hz
    simp [zetaInv, hz]
  exact ((differentiableAt_riemannZeta hs1).inv hζ).congr_of_eventuallyEq h_ev

/-- Under `_root_.RiemannHypothesis`, `riemannZeta` has no zeros in `{s : ℂ | 1/2 < s.re}`. -/
theorem riemannZeta_ne_zero_of_half_lt_re (hRH : _root_.RiemannHypothesis)
    {s : ℂ} (hs : 1 / 2 < s.re) : riemannZeta s ≠ 0 := by
  by_cases hs1 : 1 ≤ s.re
  · exact riemannZeta_ne_zero_of_one_le_re hs1
  · push Not at hs1
    intro h0
    have h_not_triv : ¬ ∃ n : ℕ, s = -2 * ((n : ℂ) + 1) := by
      rintro ⟨n, rfl⟩
      have hre : ((-2 : ℂ) * ((n : ℂ) + 1)).re = -2 * ((n : ℝ) + 1) := by simp [Complex.mul_re]
      linarith [Nat.cast_nonneg (α := ℝ) n]
    have h_ne_one : s ≠ 1 := by
      intro h
      rw [h] at hs1
      norm_num at hs1
    have hre := hRH s h0 h_not_triv h_ne_one
    linarith

/-- Under `_root_.RiemannHypothesis`, `zetaInv` is differentiable on the entire half-plane `1/2 < Re(s)`. -/
theorem differentiableOn_zetaInv_of_rh (hRH : _root_.RiemannHypothesis) :
    DifferentiableOn ℂ zetaInv {s : ℂ | 1 / 2 < s.re} := by
  intro s hs
  by_cases h1 : s = 1
  · subst h1; exact differentiableAt_zetaInv_one.differentiableWithinAt
  · exact (differentiableAt_zetaInv h1 (riemannZeta_ne_zero_of_half_lt_re hRH hs)).differentiableWithinAt

/-- Unconditional upper bound for the fractional-part integral on `0 < s.re`. -/
lemma norm_integral_Ioc_recipFract_le {s : ℂ} (hs : 0 < s.re) :
    ‖∫ x in Set.Ioc (0 : ℝ) 1,
      (NumberTheory.MellinFracPart.recipFract x : ℂ) * (x : ℂ) ^ (s - 1)‖ ≤ 1 / s.re := by
  have hint_real : IntegrableOn (fun x : ℝ => x ^ (s.re - 1)) (Set.Ioc 0 1) := by
    simpa [sub_eq_add_neg] using
      (intervalIntegral.intervalIntegrable_rpow' (show (-1 : ℝ) < s.re - 1 by linarith)).1
  have hint_cplx := NumberTheory.MellinFracPart.integrableOn_Ioc_recipFract_cpow s hs
  have hnorm :
      ‖∫ x in Set.Ioc (0 : ℝ) 1,
        (NumberTheory.MellinFracPart.recipFract x : ℂ) * (x : ℂ) ^ (s - 1)‖ ≤
        ∫ x in Set.Ioc (0 : ℝ) 1, x ^ (s.re - 1) := by
    refine norm_integral_le_of_norm_le hint_real ?_
    filter_upwards [ae_restrict_mem measurableSet_Ioc] with x hx
    rw [norm_mul, Complex.norm_cpow_eq_rpow_re_of_pos hx.1]
    simp only [Complex.sub_re, Complex.one_re]
    exact mul_le_of_le_one_left (Real.rpow_nonneg hx.1.le _)
      (NumberTheory.MellinFracPart.norm_recipFract_le_one x)
  have hval : (∫ x in Set.Ioc (0 : ℝ) 1, x ^ (s.re - 1)) = 1 / s.re := by
    rw [← intervalIntegral.integral_of_le zero_le_one,
      integral_rpow (Or.inl (show (-1 : ℝ) < s.re - 1 by linarith))]
    have h0 : (0 : ℝ) ^ s.re = 0 := Real.zero_rpow (ne_of_gt hs)
    rw [show s.re - 1 + 1 = s.re by ring, h0, Real.one_rpow, sub_zero, one_div]
  linarith

/-- **Stage 1 Strip Bound (Unconditional):** For `1/2 ≤ s.re` and `1 ≤ |s.im|`, `‖ζ(s)‖ ≤ 3 * ‖s‖`. -/
theorem norm_riemannZeta_le_three_mul_norm {s : ℂ} (hs_re : 1 / 2 ≤ s.re) (hs_im : 1 ≤ |s.im|) :
    ‖riemannZeta s‖ ≤ 3 * ‖s‖ := by
  have hs_pos : 0 < s.re := by linarith
  have hs_ne_one : s ≠ 1 := by
    intro h
    rw [h] at hs_im
    norm_num at hs_im
  have hid := NumberTheory.MellinFracPart.mellin_recipFract_unit_interval_of_pos_re s hs_pos hs_ne_one
  have hs_ne0 : s ≠ 0 := by
    intro h
    rw [h] at hs_pos
    simp at hs_pos
  have hζ : riemannZeta s =
      s / (s - 1) - s * ∫ x in Set.Ioc (0 : ℝ) 1,
        (NumberTheory.MellinFracPart.recipFract x : ℂ) * (x : ℂ) ^ (s - 1) := by
    have h1 := congrArg (s * ·) hid
    have h1' : s * ∫ x in Set.Ioc (0 : ℝ) 1,
        (NumberTheory.MellinFracPart.recipFract x : ℂ) * (x : ℂ) ^ (s - 1) =
        s / (s - 1) - riemannZeta s := by
      rw [h1, mul_sub, div_eq_mul_inv, mul_div_cancel₀ _ hs_ne0]
      ring
    rw [h1']
    ring
  rw [hζ]
  have h_sub_ge : 1 ≤ ‖s - 1‖ := by
    calc (1 : ℝ) ≤ |s.im| := hs_im
      _ = |(s - 1).im| := by simp
      _ ≤ ‖s - 1‖ := Complex.abs_im_le_norm (s - 1)
  have h1 : ‖s / (s - 1)‖ ≤ ‖s‖ := by
    rw [norm_div]
    exact div_le_self (norm_nonneg s) h_sub_ge
  have h2 : ‖s * ∫ x in Set.Ioc (0 : ℝ) 1,
      (NumberTheory.MellinFracPart.recipFract x : ℂ) * (x : ℂ) ^ (s - 1)‖ ≤ 2 * ‖s‖ := by
    rw [norm_mul]
    calc ‖s‖ * ‖∫ x in Set.Ioc (0 : ℝ) 1,
          (NumberTheory.MellinFracPart.recipFract x : ℂ) * (x : ℂ) ^ (s - 1)‖
        ≤ ‖s‖ * (1 / s.re) := mul_le_mul_of_nonneg_left (norm_integral_Ioc_recipFract_le hs_pos) (norm_nonneg s)
      _ ≤ ‖s‖ * 2 := by
          gcongr
          rw [div_le_iff₀ hs_pos]
          linarith
      _ = 2 * ‖s‖ := by ring
  calc ‖s / (s - 1) - s * ∫ x in Set.Ioc (0 : ℝ) 1, _‖
      ≤ ‖s / (s - 1)‖ + ‖s * ∫ x in Set.Ioc (0 : ℝ) 1, _‖ := norm_sub_le _ _
    _ ≤ ‖s‖ + 2 * ‖s‖ := add_le_add h1 h2
    _ = 3 * ‖s‖ := by ring

/-- Telescoping tail bound `∑_{n ≥ 2} n^{-2} ≤ 3/4 < 1`, giving uniform lower/upper bounds on `ζ(2 + it)`. -/
lemma norm_riemannZeta_sub_one_le_of_two_le_re {s : ℂ} (hs : 2 ≤ s.re) :
    ‖riemannZeta s - 1‖ ≤ 3 / 4 := by
  have hs1 : 1 < s.re := by linarith
  rw [zeta_eq_tsum_one_div_nat_add_one_cpow hs1]
  have hsum : Summable (fun n : ℕ => 1 / ((n : ℂ) + 1) ^ s) := by
    have h_norm : Summable (fun n : ℕ => ‖1 / ((n : ℂ) + 1) ^ s‖) := by
      have h_ev : (fun n : ℕ => ‖1 / ((n : ℂ) + 1) ^ s‖) = fun n : ℕ => ((n : ℝ) + 1) ^ (-s.re) := by
        ext n
        rw [norm_div, norm_one, one_div]
        have hn : (0 : ℝ) < (n : ℝ) + 1 := by positivity
        rw [← Complex.ofReal_natCast, ← Complex.ofReal_one, ← Complex.ofReal_add,
          Complex.norm_cpow_eq_rpow_re_of_pos hn, Real.rpow_neg hn.le]
      rw [h_ev]
      exact (Real.summable_nat_rpow_inv.mpr hs1).comp_injective Nat.succ_injective |>.congr fun n => by
        simp [Real.rpow_neg (by positivity : (0 : ℝ) ≤ (n : ℝ) + 1)]
    exact h_norm.of_norm
  rw [Summable.tsum_eq_zero_add hsum]
  simp only [Nat.cast_zero, zero_add, one_cpow, div_one, add_sub_cancel_left]
  have hsum1 : Summable (fun n : ℕ => 1 / (((n + 1 : ℕ) : ℂ) + 1) ^ s) :=
    hsum.comp_injective Nat.succ_injective
  rw [Summable.tsum_eq_zero_add hsum1]
  have h_zero : 1 / (((0 + 1 : ℕ) : ℂ) + 1) ^ s = 1 / (2 : ℂ) ^ s := by
    norm_num
  rw [h_zero]
  have hsum2 : Summable (fun n : ℕ => 1 / ((n : ℂ) + 3) ^ s) :=
    (hsum1.comp_injective Nat.succ_injective).congr fun n => by
      simp only [Function.comp_apply]
      congr 2
      push_cast
      ring
  have h_shift : (∑' b : ℕ, 1 / ((((b + 1) + 1 : ℕ) : ℂ) + 1) ^ s) =
      ∑' n : ℕ, 1 / ((n : ℂ) + 3) ^ s := by
    refine tsum_congr fun n => ?_
    congr 2
    push_cast
    ring
  rw [h_shift]
  have h_tele_hasSum : HasSum (fun n : ℕ => (1 : ℝ) / (((n : ℝ) + 2) * ((n : ℝ) + 3))) (1 / 2) := by
    rw [hasSum_iff_tendsto_nat_of_nonneg (fun _ => by positivity)]
    have h_part : ∀ N : ℕ, ∑ n ∈ Finset.range N, (1 : ℝ) / (((n : ℝ) + 2) * ((n : ℝ) + 3)) =
        1 / 2 - 1 / ((N : ℝ) + 2) := by
      intro N
      have hterm : ∀ n : ℕ, (1 : ℝ) / (((n : ℝ) + 2) * ((n : ℝ) + 3)) =
          1 / ((n : ℝ) + 2) - 1 / (((n + 1 : ℕ) : ℝ) + 2) := by
        intro n; push_cast
        have h2 : (n : ℝ) + 2 ≠ 0 := by positivity
        have h3 : (n : ℝ) + 3 ≠ 0 := by positivity
        field_simp [h2, h3]; ring
      simp_rw [hterm]
      rw [Finset.sum_range_sub' (fun n : ℕ => 1 / ((n : ℝ) + 2))]
      norm_num
    simp_rw [h_part]
    have h_inv_lim : Tendsto (fun N : ℕ => 1 / ((N : ℝ) + 2)) atTop (𝓝 0) :=
      tendsto_const_nhds.div_atTop (tendsto_natCast_atTop_atTop.atTop_add tendsto_const_nhds)
    simpa using tendsto_const_nhds.sub h_inv_lim
  have h_re_le : ∀ n : ℕ, ‖1 / ((n : ℂ) + 3) ^ s‖ ≤ (1 : ℝ) / (((n : ℝ) + 2) * ((n : ℝ) + 3)) := by
    intro n
    rw [norm_div, norm_one]
    have hn : (1 : ℝ) ≤ (n : ℝ) + 3 := by linarith [Nat.cast_nonneg (α := ℝ) n]
    rw [← Complex.ofReal_natCast, ← Complex.ofReal_ofNat, ← Complex.ofReal_add,
      Complex.norm_cpow_eq_rpow_re_of_pos (by positivity)]
    have hpow2 : ((n : ℝ) + 3) ^ (2 : ℝ) ≤ ((n : ℝ) + 3) ^ s.re :=
      Real.rpow_le_rpow_of_exponent_le hn hs
    have hmul : ((n : ℝ) + 2) * ((n : ℝ) + 3) ≤ ((n : ℝ) + 3) ^ (2 : ℝ) := by
      rw [Real.rpow_two]
      nlinarith
    have h_mul_pos : 0 < ((n : ℝ) + 2) * ((n : ℝ) + 3) := by positivity
    exact one_div_le_one_div_of_le h_mul_pos (hmul.trans hpow2)
  have hnorm_sum : ‖1 / (2 : ℂ) ^ s + ∑' n : ℕ, 1 / ((n : ℂ) + 3) ^ s‖ ≤ 3 / 4 := by
    have h_first : ‖1 / (2 : ℂ) ^ s‖ ≤ 1 / 4 := by
      rw [norm_div, norm_one, ← Complex.ofReal_ofNat, Complex.norm_cpow_eq_rpow_re_of_pos (by positivity)]
      have h2 : (2 : ℝ) ^ (2 : ℝ) ≤ (2 : ℝ) ^ s.re :=
        Real.rpow_le_rpow_of_exponent_le (by norm_num) hs
      calc 1 / (2 : ℝ) ^ s.re ≤ 1 / ((2 : ℝ) ^ (2 : ℝ)) := one_div_le_one_div_of_le (by positivity) h2
        _ = 1 / 4 := by norm_num
    have h_tail : ‖∑' n : ℕ, 1 / ((n : ℂ) + 3) ^ s‖ ≤ 1 / 2 := by
      have h_tri_neg : ∀ n : ℕ, 0 ≤ ‖1 / ((n : ℂ) + 3) ^ s‖ := fun _ => norm_nonneg _
      have h_le_pos : ∀ n : ℕ, 0 ≤ (1 : ℝ) / (((n : ℝ) + 2) * ((n : ℝ) + 3)) := fun _ => by positivity
      calc ‖∑' n : ℕ, 1 / ((n : ℂ) + 3) ^ s‖
          ≤ ∑' n : ℕ, ‖1 / ((n : ℂ) + 3) ^ s‖ := norm_tsum_le_tsum_norm hsum2.norm
        _ ≤ ∑' n : ℕ, (1 : ℝ) / (((n : ℝ) + 2) * ((n : ℝ) + 3)) :=
            Summable.tsum_le_tsum h_re_le hsum2.norm h_tele_hasSum.summable
        _ = 1 / 2 := h_tele_hasSum.tsum_eq
    calc ‖1 / (2 : ℂ) ^ s + ∑' n : ℕ, 1 / ((n : ℂ) + 3) ^ s‖
        ≤ ‖1 / (2 : ℂ) ^ s‖ + ‖∑' n : ℕ, 1 / ((n : ℂ) + 3) ^ s‖ := norm_add_le _ _
      _ ≤ 1 / 4 + 1 / 2 := add_le_add h_first h_tail
      _ = 3 / 4 := by norm_num
  simpa using hnorm_sum

/-- For `2 ≤ s.re`, `1 / 4 ≤ ‖ζ(s)‖`, `‖ζ(s)‖ ≤ 7 / 4`, and `‖zetaInv s‖ ≤ 4`. -/
lemma norm_zeta_lower_of_two_le_re {s : ℂ} (hs : 2 ≤ s.re) :
    1 / 4 ≤ ‖riemannZeta s‖ ∧ ‖riemannZeta s‖ ≤ 7 / 4 ∧ ‖zetaInv s‖ ≤ 4 := by
  have hsub := norm_riemannZeta_sub_one_le_of_two_le_re hs
  have h_lo : 1 / 4 ≤ ‖riemannZeta s‖ := by
    have htri := norm_sub_norm_le (1 : ℂ) (riemannZeta s)
    rw [norm_one, norm_sub_rev] at htri
    linarith
  have h_hi : ‖riemannZeta s‖ ≤ 7 / 4 := by
    have htri := norm_add_le (1 : ℂ) (riemannZeta s - 1)
    simp only [add_sub_cancel, norm_one] at htri
    linarith
  have hs_ne1 : s ≠ 1 := by
    intro h
    rw [h] at hs
    norm_num at hs
  have h_inv : ‖zetaInv s‖ ≤ 4 := by
    rw [zetaInv]
    simp [hs_ne1]
    exact inv_le_of_inv_le₀ (by norm_num) (by linarith)
  exact ⟨h_lo, h_hi, h_inv⟩

/-- Uniform logarithmic-derivative bound on `{s : ℂ | 1 + η ≤ s.re}` (`0 < η`). -/
theorem norm_logDeriv_riemannZeta_le {η : ℝ} (hη : 0 < η) :
    ∃ C > 0, ∀ s : ℂ, 1 + η ≤ s.re → ‖deriv riemannZeta s / riemannZeta s‖ ≤ C := by
  have h1 : 1 < (1 + η : ℂ).re := by simp [hη]
  have hsum_ref : LSeriesSummable (↗ArithmeticFunction.vonMangoldt) (1 + η : ℂ) :=
    ArithmeticFunction.LSeriesSummable_vonMangoldt h1
  refine ⟨(∑' n : ℕ, ‖LSeries.term (↗ArithmeticFunction.vonMangoldt) (1 + η : ℂ) n‖) + 1,
    by positivity, fun s hs => ?_⟩
  have hs1 : 1 < s.re := by linarith
  have h_eq := ArithmeticFunction.LSeries_vonMangoldt_eq_deriv_riemannZeta_div hs1
  have h_eq' : deriv riemannZeta s / riemannZeta s = -L ↗ArithmeticFunction.vonMangoldt s := by
    rw [h_eq]; ring
  rw [h_eq', norm_neg]
  have hsum_s : LSeriesSummable (↗ArithmeticFunction.vonMangoldt) s :=
    ArithmeticFunction.LSeriesSummable_vonMangoldt hs1
  calc ‖L ↗ArithmeticFunction.vonMangoldt s‖
      ≤ ∑' n : ℕ, ‖LSeries.term (↗ArithmeticFunction.vonMangoldt) s n‖ :=
        norm_tsum_le_tsum_norm hsum_s.norm
    _ ≤ ∑' n : ℕ, ‖LSeries.term (↗ArithmeticFunction.vonMangoldt) (1 + η : ℂ) n‖ := by
        refine Summable.tsum_le_tsum (fun n => ?_) hsum_s.norm hsum_ref.norm
        rcases eq_or_ne n 0 with rfl | hn
        · simp [LSeries.term]
        · simp only [LSeries.term, hn, ↓reduceIte, norm_div]
          have hn_ge1 : (1 : ℝ) ≤ n := by exact_mod_cast Nat.pos_of_ne_zero hn
          have hn_pos : (0 : ℝ) < n := by positivity
          rw [← Complex.ofReal_natCast, Complex.norm_cpow_eq_rpow_re_of_pos hn_pos,
            Complex.norm_cpow_eq_rpow_re_of_pos hn_pos]
          simp only [Complex.add_re, Complex.one_re, Complex.ofReal_re]
          exact div_le_div_of_nonneg_left (norm_nonneg _) (Real.rpow_pos_of_pos hn_pos _)
            (Real.rpow_le_rpow_of_exponent_le hn_ge1 hs)
    _ ≤ (∑' n : ℕ, ‖LSeries.term (↗ArithmeticFunction.vonMangoldt) (1 + η : ℂ) n‖) + 1 := by linarith

/-! ### Stage 2: Holomorphic Logarithm on Disks & Borel–Carathéodory Bound under RH -/

/-- Norm bound for `Complex.log w` on `1/4 ≤ ‖w‖ ≤ 7/4`: `‖Complex.log w‖ ≤ Real.log 4 + Real.pi`. -/
lemma norm_log_le_of_bounds {w : ℂ} (hlo : 1 / 4 ≤ ‖w‖) (hhi : ‖w‖ ≤ 7 / 4) :
    ‖Complex.log w‖ ≤ Real.log 4 + Real.pi := by
  have hlog : Complex.log w = (Real.log ‖w‖ : ℂ) + (Complex.arg w : ℂ) * I := rfl
  rw [hlog]
  have hre_abs : |Real.log ‖w‖| ≤ Real.log 4 := by
    rw [abs_le]
    constructor
    · have h1 := Real.log_le_log (by norm_num : (0 : ℝ) < 1 / 4) hlo
      rw [one_div, Real.log_inv] at h1
      linarith
    · have h2 := Real.log_le_log (by linarith : 0 < ‖w‖) (by linarith : ‖w‖ ≤ 4)
      linarith
  have him_abs : |Complex.arg w| ≤ Real.pi := abs_le.mpr ⟨(Complex.neg_pi_lt_arg w).le, Complex.arg_le_pi w⟩
  calc ‖(Real.log ‖w‖ : ℂ) + (Complex.arg w : ℂ) * I‖
      ≤ ‖(Real.log ‖w‖ : ℂ)‖ + ‖(Complex.arg w : ℂ) * I‖ := norm_add_le _ _
    _ = |Real.log ‖w‖| + |Complex.arg w| := by
        simp [Complex.norm_real, Complex.norm_I]
    _ ≤ Real.log 4 + Real.pi := add_le_add hre_abs him_abs

/-- Under RH, for any `t` with `6 ≤ |t|` and `0 < η < 1/4`, there exists a holomorphic branch
`logZ : ℂ → ℂ` on `B = ball (2 + t * I) (3/2 - η/2)` satisfying:
1. `exp (logZ z) = riemannZeta z` on `B`;
2. `‖logZ z‖ ≤ M₁` uniformly in `t` on `closedBall (2 + t * I) (1 - η)`;
3. `‖logZ z‖ ≤ M₃ * Real.log |t|` uniformly on `closedBall (2 + t * I) (3/2 - η)`. -/
theorem exists_logZeta_ball_bounds_of_rh (hRH : _root_.RiemannHypothesis)
    {η : ℝ} (hη0 : 0 < η) (hη1 : η < 1 / 4) :
    ∃ M₁ M₃ : ℝ, 0 < M₁ ∧ 0 < M₃ ∧
      ∀ (t : ℝ), 6 ≤ |t| →
        ∃ logZ : ℂ → ℂ,
          DifferentiableOn ℂ logZ (ball (2 + (t : ℂ) * I) (3 / 2 - η / 2)) ∧
          (∀ z ∈ ball (2 + (t : ℂ) * I) (3 / 2 - η / 2), Complex.exp (logZ z) = riemannZeta z) ∧
          (∀ z ∈ closedBall (2 + (t : ℂ) * I) (1 - η), ‖logZ z‖ ≤ M₁) ∧
          (∀ z ∈ closedBall (2 + (t : ℂ) * I) (3 / 2 - η), ‖logZ z‖ ≤ M₃ * Real.log |t|) := by
  obtain ⟨CΛ, hCΛ_pos, hCΛ⟩ := norm_logDeriv_riemannZeta_le hη0
  set R₀ : ℝ := 3 / 2 - η / 2
  set r₁ : ℝ := 1 - η
  set r₃ : ℝ := 3 / 2 - η
  have hR₀_pos : 0 < R₀ := by dsimp [R₀]; linarith
  have hr₃_lt_R₀ : r₃ < R₀ := by dsimp [r₃, R₀]; linarith
  set M₁ : ℝ := Real.log 4 + Real.pi + CΛ * r₁
  -- Choose M₃ large enough so Bore-Caratheodory gives ‖L z‖ ≤ M₃ * log |t| for |t| ≥ 6 (note log 6 > 1.7 > 1)
  set c_bc : ℝ := 2 * r₃ / (η / 2)
  set d_bc : ℝ := (2 * Real.log 6) * r₃ / (η / 2) + (Real.log 4 + Real.pi) * (R₀ + r₃) / (η / 2)
  set M₃ : ℝ := c_bc + d_bc + 1
  have hM₁_pos : 0 < M₁ := by
    have := Real.log_pos (by norm_num : (1 : ℝ) < 4)
    have := Real.pi_pos
    have : 0 < r₁ := by dsimp [r₁]; linarith
    positivity
  have h_eta_half : 0 < η / 2 := by linarith
  have hc_bc_nn : 0 ≤ c_bc := by
    have : 0 < r₃ := by dsimp [r₃]; linarith
    positivity
  have hd_bc_nn : 0 ≤ d_bc := by
    have : 0 < r₃ := by dsimp [r₃]; linarith
    have : 0 < Real.log 6 := Real.log_pos (by norm_num)
    have : 0 < Real.log 4 := Real.log_pos (by norm_num)
    have := Real.pi_pos
    positivity
  have hM₃_pos : 0 < M₃ := by dsimp [M₃]; linarith
  refine ⟨M₁, M₃, hM₁_pos, hM₃_pos, fun t ht => ?_⟩
  set s₀ : ℂ := 2 + (t : ℂ) * I
  set B : Set ℂ := ball s₀ R₀
  have hs₀_re : 2 ≤ s₀.re := by simp [s₀]
  have h_ball_prop : ∀ z ∈ B, 1 / 2 + η / 2 < z.re ∧ z.re < 7 / 2 ∧ 9 / 2 < |z.im| ∧ ‖z‖ ≤ 2 * |t| := by
    intro z hz
    have hdist : ‖z - s₀‖ < R₀ := mem_ball_iff_norm.mp hz
    have hre_sub : |z.re - 2| < R₀ := by
      have h1 : |z.re - 2| = |(z - s₀).re| := by simp [s₀]
      rw [h1]
      exact (Complex.abs_re_le_norm (z - s₀)).trans_lt hdist
    have him_sub : |z.im - t| < R₀ := by
      have h1 : |z.im - t| = |(z - s₀).im| := by simp [s₀]
      rw [h1]
      exact (Complex.abs_im_le_norm (z - s₀)).trans_lt hdist
    have hre_lo : 1 / 2 + η / 2 < z.re := by
      have := (abs_lt.mp hre_sub).1
      dsimp [R₀] at this; linarith
    have hre_hi : z.re < 7 / 2 := by
      have := (abs_lt.mp hre_sub).2
      dsimp [R₀] at this; linarith
    have him_lo : 9 / 2 < |z.im| := by
      have : |t| - |z.im| ≤ |z.im - t| := by
        simpa [abs_sub_comm] using abs_sub_abs_le_abs_sub t z.im
      dsimp [R₀] at him_sub
      linarith
    have him_hi : |z.im| < |t| + 3 / 2 := by
      have : |z.im| - |t| ≤ |z.im - t| := abs_sub_abs_le_abs_sub z.im t
      dsimp [R₀] at him_sub
      linarith
    have hnorm : ‖z‖ ≤ 2 * |t| := by
      have htri : ‖z‖ ≤ |z.re| + |z.im| := Complex.norm_le_abs_re_add_abs_im z
      have hzre_abs : |z.re| ≤ 7 / 2 := abs_le.mpr ⟨by linarith, by linarith⟩
      linarith
    exact ⟨hre_lo, hre_hi, him_lo, hnorm⟩
  have hB_nz : ∀ z ∈ B, z ≠ 1 ∧ riemannZeta z ≠ 0 := by
    intro z hz
    obtain ⟨hre, _, him, _⟩ := h_ball_prop z hz
    have hz1 : z ≠ 1 := by
      intro h; rw [h] at him; norm_num at him
    have hζ : riemannZeta z ≠ 0 := riemannZeta_ne_zero_of_half_lt_re hRH (by linarith)
    exact ⟨hz1, hζ⟩
  have hlogDeriv_diff : DifferentiableOn ℂ (fun z => deriv riemannZeta z / riemannZeta z) B := by
    have hζ_diff : DifferentiableOn ℂ riemannZeta B := fun z hz =>
      (differentiableAt_riemannZeta (hB_nz z hz).1).differentiableWithinAt
    have hζ_deriv_diff : DifferentiableOn ℂ (deriv riemannZeta) B := hζ_diff.deriv isOpen_ball
    exact hζ_deriv_diff.div hζ_diff (fun z hz => (hB_nz z hz).2)
  have hs₀_mem : s₀ ∈ B := mem_ball_self hR₀_pos
  obtain ⟨logZ, hLs₀, hL_deriv⟩ :=
    (hlogDeriv_diff.isExactOn_ball).with_val_at s₀ (Complex.log (riemannZeta s₀))
  have hL_diff : DifferentiableOn ℂ logZ B :=
    fun z hz => (hL_deriv z hz).differentiableAt.differentiableWithinAt
  have h_exp_eq : ∀ z ∈ B, Complex.exp (logZ z) = riemannZeta z := by
    let Q : ℂ → ℂ := fun z => riemannZeta z * Complex.exp (-logZ z)
    have hQ_deriv : ∀ z ∈ B, HasDerivAt Q 0 z := by
      intro z hz
      have h1 : HasDerivAt riemannZeta (deriv riemannZeta z) z :=
        (differentiableAt_riemannZeta (hB_nz z hz).1).hasDerivAt
      have h2 : HasDerivAt (fun w => Complex.exp (-logZ w))
          (Complex.exp (-logZ z) * -(deriv riemannZeta z / riemannZeta z)) z :=
        ((hL_deriv z hz).neg).cexp
      have hmul := h1.mul h2
      have hzero : deriv riemannZeta z * Complex.exp (-logZ z) +
          riemannZeta z * (Complex.exp (-logZ z) * -(deriv riemannZeta z / riemannZeta z)) = 0 := by
        have hζnz : riemannZeta z ≠ 0 := (hB_nz z hz).2
        field_simp [hζnz]; ring
      rw [hzero] at hmul
      exact hmul
    have hQ_const : ∀ z ∈ B, Q z = Q s₀ := fun z hz =>
      ((convex_ball s₀ R₀).is_const_of_fderivWithin_eq_zero
        (fun w hw => (hQ_deriv w hw).differentiableAt.differentiableWithinAt)
        (fun w hw => by
          rw [(hQ_deriv w hw).hasDerivWithinAt.hasFDerivWithinAt.fderivWithin
            (isOpen_ball.uniqueDiffOn w hw)]
          ext1; simp)
        hz hs₀_mem)
    intro z hz
    have hQs₀ : Q s₀ = 1 := by
      dsimp [Q]
      rw [hLs₀, Complex.exp_neg, Complex.exp_log (hB_nz s₀ hs₀_mem).2,
        mul_inv_cancel₀ (hB_nz s₀ hs₀_mem).2]
    have hQz : riemannZeta z * Complex.exp (-logZ z) = 1 := (hQ_const z hz).trans hQs₀
    rw [Complex.exp_neg] at hQz
    have h1 : (Complex.exp (logZ z))⁻¹ = (riemannZeta z)⁻¹ :=
      eq_inv_of_mul_eq_one_right hQz
    calc Complex.exp (logZ z) = ((Complex.exp (logZ z))⁻¹)⁻¹ := (inv_inv _).symm
      _ = ((riemannZeta z)⁻¹)⁻¹ := by rw [h1]
      _ = riemannZeta z := inv_inv _
  have h_inner_bound : ∀ z ∈ closedBall s₀ r₁, ‖logZ z‖ ≤ M₁ := by
    set S₁ : Set ℂ := closedBall s₀ r₁
    have hr₁_lt_R₀ : r₁ < R₀ := by dsimp [r₁, R₀]; linarith
    have hS₁_sub : S₁ ⊆ B := closedBall_subset_ball hr₁_lt_R₀
    have hS₁_diff : ∀ z ∈ S₁, DifferentiableAt ℂ logZ z :=
      fun z hz => (hL_deriv z (hS₁_sub hz)).differentiableAt
    have hS₁_deriv_bound : ∀ z ∈ S₁, ‖deriv logZ z‖ ≤ CΛ := by
      intro z hz
      have hre_ge : 1 + η ≤ z.re := by
        have hdist : ‖z - s₀‖ ≤ r₁ := mem_closedBall_iff_norm.mp hz
        have hre_abs : |z.re - 2| ≤ r₁ := by
          have : |z.re - 2| = |(z - s₀).re| := by simp [s₀]
          rw [this]
          exact (Complex.abs_re_le_norm (z - s₀)).trans hdist
        have := (abs_le.mp hre_abs).1
        dsimp [r₁] at this; linarith
      rw [(hL_deriv z (hS₁_sub hz)).deriv]
      exact hCΛ z hre_ge
    have hs₀_S₁ : s₀ ∈ S₁ := mem_closedBall_self (by dsimp [r₁]; linarith)
    obtain ⟨hlo_s₀, hhi_s₀, _⟩ := norm_zeta_lower_of_two_le_re hs₀_re
    have hLs₀_norm : ‖logZ s₀‖ ≤ Real.log 4 + Real.pi := by
      rw [hLs₀]
      exact norm_log_le_of_bounds hlo_s₀ hhi_s₀
    intro z hz
    have hmvt := (convex_closedBall s₀ r₁).norm_image_sub_le_of_norm_deriv_le hS₁_diff hS₁_deriv_bound hs₀_S₁ hz
    have hdist_le : ‖z - s₀‖ ≤ r₁ := mem_closedBall_iff_norm.mp hz
    calc ‖logZ z‖ ≤ ‖logZ z - logZ s₀‖ + ‖logZ s₀‖ := norm_le_norm_sub_add _ _
      _ ≤ CΛ * ‖z - s₀‖ + (Real.log 4 + Real.pi) := add_le_add hmvt hLs₀_norm
      _ ≤ CΛ * r₁ + (Real.log 4 + Real.pi) := by gcongr
      _ = M₁ := by dsimp [M₁]; ring
  have h_outer_bound : ∀ z ∈ closedBall s₀ r₃, ‖logZ z‖ ≤ M₃ * Real.log |t| := by
    let g : ℂ → ℂ := fun w => logZ (s₀ + w)
    have hg_diff : DifferentiableOn ℂ g (ball 0 R₀) := by
      refine hL_diff.comp ((differentiable_id.const_add s₀).differentiableOn) ?_
      intro w hw
      rw [mem_ball_iff_norm, add_sub_cancel_left]
      exact mem_ball_zero_iff.mp hw
    set M_re : ℝ := Real.log (6 * |t|)
    have hM_re_pos : 0 < M_re := Real.log_pos (by linarith)
    have hg_re : MapsTo g (ball 0 R₀) {z : ℂ | z.re ≤ M_re} := by
      intro w hw
      have hwB : s₀ + w ∈ B := by
        rw [mem_ball_iff_norm, add_sub_cancel_left]
        exact mem_ball_zero_iff.mp hw
      obtain ⟨hre, _, him, hnorm⟩ := h_ball_prop (s₀ + w) hwB
      have hre_ge_half : 1 / 2 ≤ (s₀ + w).re := by linarith
      have him_ge_one : 1 ≤ |(s₀ + w).im| := by linarith
      have hζ_le := norm_riemannZeta_le_three_mul_norm hre_ge_half him_ge_one
      have hζ_pos : 0 < ‖riemannZeta (s₀ + w)‖ := norm_pos_iff.mpr (hB_nz (s₀ + w) hwB).2
      have hexp_re : Real.exp (g w).re = ‖riemannZeta (s₀ + w)‖ := by
        dsimp [g]
        rw [← Complex.norm_exp, h_exp_eq (s₀ + w) hwB]
      have hre_eq : (g w).re = Real.log ‖riemannZeta (s₀ + w)‖ := by
        rw [← hexp_re, Real.log_exp]
      rw [Set.mem_ofPred_eq, hre_eq]
      exact Real.log_le_log hζ_pos (hζ_le.trans (by linarith))
    obtain ⟨hlo_s₀, hhi_s₀, _⟩ := norm_zeta_lower_of_two_le_re hs₀_re
    have hg0_norm : ‖g 0‖ ≤ Real.log 4 + Real.pi := by
      dsimp [g]; rw [add_zero, hLs₀]
      exact norm_log_le_of_bounds hlo_s₀ hhi_s₀
    have hlog6_le : 1 ≤ Real.log |t| := by
      have h_e : Real.exp 1 ≤ |t| := by
        have := Real.exp_one_lt_d9
        linarith
      calc 1 = Real.log (Real.exp 1) := (Real.log_exp 1).symm
        _ ≤ Real.log |t| := Real.log_le_log (Real.exp_pos 1) h_e
    intro z hz
    set w := z - s₀
    have hw_mem : w ∈ ball 0 R₀ := by
      rw [mem_ball_zero_iff]
      exact (mem_closedBall_iff_norm.mp hz).trans_lt hr₃_lt_R₀
    have hw_norm : ‖w‖ ≤ r₃ := mem_closedBall_iff_norm.mp hz
    have hbc := Complex.borelCaratheodory hM_re_pos hg_diff hg_re hR₀_pos hw_mem
    have hdenom : R₀ - ‖w‖ ≥ η / 2 := by dsimp [R₀, r₃] at *; linarith
    have hM_re_split : M_re = Real.log 6 + Real.log |t| :=
      Real.log_mul (by norm_num) (by linarith)
    have h_r₃_pos : 0 < r₃ := by dsimp [r₃]; linarith
    have h_term1_le : 2 * M_re * ‖w‖ / (R₀ - ‖w‖) ≤ 2 * M_re * r₃ / (η / 2) := by
      have hnum : 2 * M_re * ‖w‖ ≤ 2 * M_re * r₃ := by gcongr
      calc 2 * M_re * ‖w‖ / (R₀ - ‖w‖)
          ≤ 2 * M_re * r₃ / (R₀ - ‖w‖) := div_le_div_of_nonneg_right hnum (by linarith)
        _ ≤ 2 * M_re * r₃ / (η / 2) := by
            rw [div_eq_mul_inv, div_eq_mul_inv]
            exact mul_le_mul_of_nonneg_left (inv_anti₀ (by positivity) hdenom) (by positivity)
    have h_term2_le : ‖g 0‖ * (R₀ + ‖w‖) / (R₀ - ‖w‖) ≤
        (Real.log 4 + Real.pi) * (R₀ + r₃) / (η / 2) := by
      have h_pi_nn : 0 ≤ Real.log 4 + Real.pi := by positivity
      have hnum : ‖g 0‖ * (R₀ + ‖w‖) ≤ (Real.log 4 + Real.pi) * (R₀ + r₃) :=
        mul_le_mul hg0_norm (by linarith) (by positivity) h_pi_nn
      calc ‖g 0‖ * (R₀ + ‖w‖) / (R₀ - ‖w‖)
          ≤ (Real.log 4 + Real.pi) * (R₀ + r₃) / (R₀ - ‖w‖) :=
            div_le_div_of_nonneg_right hnum (by linarith)
        _ ≤ (Real.log 4 + Real.pi) * (R₀ + r₃) / (η / 2) := by
            rw [div_eq_mul_inv, div_eq_mul_inv]
            exact mul_le_mul_of_nonneg_left (inv_anti₀ (by positivity) hdenom) (by positivity)
    calc ‖logZ z‖ = ‖g w‖ := by simp [g, w]
      _ ≤ 2 * M_re * ‖w‖ / (R₀ - ‖w‖) + ‖g 0‖ * (R₀ + ‖w‖) / (R₀ - ‖w‖) := hbc
      _ ≤ 2 * M_re * r₃ / (η / 2) + (Real.log 4 + Real.pi) * (R₀ + r₃) / (η / 2) :=
          add_le_add h_term1_le h_term2_le
      _ = c_bc * Real.log |t| + d_bc := by
          rw [hM_re_split]
          dsimp [c_bc, d_bc]
          ring
      _ ≤ c_bc * Real.log |t| + d_bc * Real.log |t| := by
          gcongr
          exact le_mul_of_one_le_right hd_bc_nn hlog6_le
      _ ≤ M₃ * Real.log |t| := by
          dsimp [M₃]
          nlinarith [hlog6_le]
  exact ⟨logZ, hL_diff, h_exp_eq, h_inner_bound, h_outer_bound⟩

/-! ### Stage 3: Littlewood (1912) Three-Lines Bound & Inverse Zeta Growth under RH -/

/-- Elementary sublinear-vs-linear bound: if `0 < θ < 1`, `0 ≤ A`, and `0 < δ`,
then `∃ B ≥ 0, ∀ x ≥ 0, A * x ^ θ ≤ δ * x + B`. -/
lemma sublinear_rpow_le_linear {θ A eps : ℝ} (hθ0 : 0 < θ) (hθ1 : θ < 1) (hA : 0 ≤ A) (heps : 0 < eps) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ x : ℝ, 0 ≤ x → A * x ^ θ ≤ eps * x + B := by
  set X₀ : ℝ := (A / eps) ^ (1 / (1 - θ)) + 1
  have hX₀_pos : 0 < X₀ := by positivity
  refine ⟨A * X₀ ^ θ, by positivity, fun x hx => ?_⟩
  rcases le_total x X₀ with hle | hgt
  · have hxθ : x ^ θ ≤ X₀ ^ θ := Real.rpow_le_rpow hx hle hθ0.le
    calc A * x ^ θ ≤ A * X₀ ^ θ := mul_le_mul_of_nonneg_left hxθ hA
      _ ≤ eps * x + A * X₀ ^ θ := le_add_of_nonneg_left (mul_nonneg heps.le hx)
  · have h1mθ : 0 < 1 - θ := sub_pos.mpr hθ1
    have h_base_gt : (A / eps) ^ (1 / (1 - θ)) < x := by linarith
    have h_rpow : A / eps ≤ x ^ (1 - θ) := by
      have h_pow_le := Real.rpow_le_rpow (by positivity) h_base_gt.le h1mθ.le
      rw [← Real.rpow_mul (by positivity), one_div_mul_cancel h1mθ.ne', Real.rpow_one] at h_pow_le
      exact h_pow_le
    have hx_pos : 0 < x := lt_of_lt_of_le hX₀_pos hgt
    have hmul : A * x ^ θ ≤ eps * x := by
      calc A * x ^ θ = eps * ((A / eps) * x ^ θ) := by field_simp [heps.ne']
        _ ≤ eps * (x ^ (1 - θ) * x ^ θ) := by
            gcongr
        _ = eps * x := by
            rw [← Real.rpow_add hx_pos]
            simp
    linarith [show 0 ≤ A * X₀ ^ θ by positivity]

/-- **Stage 3 (Littlewood 1912 Conditional Inverse Bound):**
Under `_root_.RiemannHypothesis`, for any `σ₀ > 1/2` and `eps > 0`, `‖zetaInv s‖ = O((1 + |s.im|)^eps)`
uniformly on the half-plane `σ₀ ≤ s.re`. -/
theorem inv_zeta_isBigO_im_of_rh (hRH : _root_.RiemannHypothesis)
    {σ₀ eps : ℝ} (hσ₀ : 1 / 2 < σ₀) (heps : 0 < eps) :
    ∃ C > 0, ∀ s : ℂ, σ₀ ≤ s.re → ‖zetaInv s‖ ≤ C * (1 + |s.im|) ^ eps := by
  set σ₁ : ℝ := min σ₀ (3 / 4)
  have hσ₁_gt : 1 / 2 < σ₁ := lt_min hσ₀ (by norm_num)
  have hσ₁_le_σ₀ : σ₁ ≤ σ₀ := min_le_left _ _
  have hσ₁_le_34 : σ₁ ≤ 3 / 4 := min_le_right _ _
  set η : ℝ := (σ₁ - 1 / 2) / 4
  have hη0 : 0 < η := by dsimp [η]; linarith
  have hη1 : η < 1 / 4 := by dsimp [η]; linarith
  obtain ⟨M₁, M₃, hM₁_pos, hM₃_pos, h_ball⟩ := exists_logZeta_ball_bounds_of_rh hRH hη0 hη1
  set r₁ : ℝ := 1 - η
  set r₂_max : ℝ := 2 - σ₁
  set r₃ : ℝ := 3 / 2 - η
  have hr₁_pos : 0 < r₁ := by dsimp [r₁]; linarith
  have hr₁_lt_r₂max : r₁ < r₂_max := by dsimp [r₁, r₂_max, η]; linarith
  have hr₂max_lt_r₃ : r₂_max < r₃ := by dsimp [r₂_max, r₃, η]; linarith
  have hr₁_lt_r₃ : r₁ < r₃ := hr₁_lt_r₂max.trans hr₂max_lt_r₃
  set u_strip : ℝ := Real.log (r₃ / r₁)
  have hu_pos : 0 < u_strip := Real.log_pos ((one_lt_div hr₁_pos).mpr hr₁_lt_r₃)
  set θ : ℝ := Real.log (r₂_max / r₁) / u_strip
  have h_r2_gt1 : 1 < r₂_max / r₁ := (one_lt_div hr₁_pos).mpr hr₁_lt_r₂max
  have h_r2_lt_r3 : r₂_max / r₁ < r₃ / r₁ := div_lt_div_of_pos_right hr₂max_lt_r₃ hr₁_pos
  have hθ0 : 0 < θ := div_pos (Real.log_pos h_r2_gt1) hu_pos
  have hθ1 : θ < 1 := (div_lt_one hu_pos).mpr (Real.log_lt_log (by positivity) h_r2_lt_r3)
  set A_coef : ℝ := max M₁ 1 * (M₃ ^ θ)
  have hA_nn : 0 ≤ A_coef := by positivity
  obtain ⟨B_sub, hB_sub_nn, h_sublin⟩ := sublinear_rpow_le_linear hθ0 hθ1 hA_nn heps
  set t₀ : ℝ := max 6 (Real.exp (1 / M₃))
  have ht₀_ge6 : 6 ≤ t₀ := le_max_left _ _
  set K_box : Set ℂ := Icc σ₁ 2 ×ℂ Icc (-t₀) t₀
  have hK_compact : IsCompact K_box := isCompact_Icc.reProdIm isCompact_Icc
  have hK_sub : K_box ⊆ {s : ℂ | 1 / 2 < s.re} := fun s hs => hσ₁_gt.trans_le hs.1.1
  have hK_cont : ContinuousOn zetaInv K_box :=
    ((differentiableOn_zetaInv_of_rh hRH).mono hK_sub).continuousOn
  obtain ⟨B_box, hB_box⟩ := hK_compact.exists_bound_of_continuousOn hK_cont
  set C : ℝ := max 4 (max (max B_box 0) (max (Real.exp B_sub) (Real.exp M₁))) + 1
  have hC_pos : 0 < C := by
    have : 0 ≤ max 4 (max (max B_box 0) (max (Real.exp B_sub) (Real.exp M₁))) :=
      le_max_of_le_left (by norm_num)
    linarith
  refine ⟨C, hC_pos, fun s hs_re => ?_⟩
  have h_one_le_rpow : (1 : ℝ) ≤ (1 + |s.im|) ^ eps :=
    Real.one_le_rpow (by linarith [abs_nonneg s.im]) heps.le
  have h_base_bound : ∀ M_bnd : ℝ, M_bnd ≤ C → M_bnd ≤ C * (1 + |s.im|) ^ eps := fun M_bnd hM => by
    calc M_bnd ≤ C := hM
      _ = C * 1 := (mul_one C).symm
      _ ≤ C * (1 + |s.im|) ^ eps := mul_le_mul_of_nonneg_left h_one_le_rpow hC_pos.le
  rcases le_or_gt 2 s.re with hs_ge2 | hs_lt2
  · obtain ⟨_, _, h_inv⟩ := norm_zeta_lower_of_two_le_re hs_ge2
    exact h_inv.trans (h_base_bound 4 (by dsimp [C]; linarith [le_max_left 4 (max (max B_box 0) (max (Real.exp B_sub) (Real.exp M₁)))]))
  · rcases le_or_gt |s.im| t₀ with him_le | him_gt
    · have hs_box : s ∈ K_box := ⟨⟨hσ₁_le_σ₀.trans hs_re, hs_lt2.le⟩, abs_le.mp him_le⟩
      have h_le_B : ‖zetaInv s‖ ≤ max B_box 0 := (hB_box s hs_box).trans (le_max_left _ _)
      have h_le_C : max B_box 0 ≤ C := by
        dsimp [C]
        have h1 : max B_box 0 ≤ max (max B_box 0) (max (Real.exp B_sub) (Real.exp M₁)) := le_max_left _ _
        have h2 := h1.trans (le_max_right 4 _)
        linarith
      exact h_le_B.trans (h_base_bound (max B_box 0) h_le_C)
    · have ht6 : 6 ≤ |s.im| := ht₀_ge6.trans him_gt.le
      obtain ⟨logZ, hL_diff, h_exp_eq, h_inner, h_outer⟩ := h_ball s.im ht6
      set s₀ : ℂ := 2 + (s.im : ℂ) * I
      have hs_ne1 : s ≠ 1 := by
        intro h; rw [h] at ht6; norm_num at ht6
      rcases le_or_gt (1 + η) s.re with hs_ge1η | hs_lt1η
      · have hs_inner : s ∈ closedBall s₀ r₁ := by
          rw [mem_closedBall_iff_norm]
          have hsub : s - s₀ = ((s.re - 2 : ℝ) : ℂ) := by
            apply Complex.ext <;> simp [s₀]
          rw [hsub, Complex.norm_real, Real.norm_eq_abs, abs_le]
          dsimp [r₁]; constructor <;> linarith
        have hr₁_lt_R₀ : r₁ < 3 / 2 - η / 2 := by dsimp [r₁]; linarith
        have hexp_s : Complex.exp (logZ s) = riemannZeta s :=
          h_exp_eq s (closedBall_subset_ball hr₁_lt_R₀ hs_inner)
        have h_inv_norm : ‖zetaInv s‖ ≤ Real.exp M₁ := by
          have hz_eq : zetaInv s = (riemannZeta s)⁻¹ := by simp [zetaInv, hs_ne1]
          rw [hz_eq, norm_inv, ← hexp_s, Complex.norm_exp, ← Real.exp_neg]
          refine Real.exp_le_exp.mpr ?_
          have h_neg_le : -(logZ s).re ≤ ‖logZ s‖ := by
            linarith [neg_le_abs (logZ s).re, Complex.abs_re_le_norm (logZ s)]
          exact h_neg_le.trans (h_inner s hs_inner)
        have h_le_C : Real.exp M₁ ≤ C := by
          dsimp [C]
          have h1 := (le_max_right (Real.exp B_sub) (Real.exp M₁)).trans
            (le_max_right (max B_box 0) _) |>.trans (le_max_right 4 _)
          linarith
        exact h_inv_norm.trans (h_base_bound (Real.exp M₁) h_le_C)
      · have hs_ge_σ₁ : σ₁ ≤ s.re := hσ₁_le_σ₀.trans hs_re
        set r_s : ℝ := 2 - s.re
        have hr_lo : r₁ < r_s := by dsimp [r₁, r_s]; linarith
        have hr_hi : r_s ≤ r₂_max := by dsimp [r_s, r₂_max]; linarith
        let F : ℂ → ℂ := fun w => logZ (s₀ + (r₁ : ℂ) * Complex.exp w)
        have h_map_strip : ∀ w ∈ Complex.HadamardThreeLines.verticalClosedStrip 0 u_strip,
            s₀ + (r₁ : ℂ) * Complex.exp w ∈ closedBall s₀ r₃ := by
          intro w hw
          rw [mem_closedBall_iff_norm, add_sub_cancel_left, norm_mul, Complex.norm_real,
            Real.norm_eq_abs, abs_of_pos hr₁_pos, Complex.norm_exp]
          have hw_le : w.re ≤ u_strip := hw.2
          calc r₁ * Real.exp w.re ≤ r₁ * Real.exp u_strip :=
                mul_le_mul_of_nonneg_left (Real.exp_le_exp.mpr hw_le) hr₁_pos.le
            _ = r₁ * (r₃ / r₁) := by dsimp [u_strip]; rw [Real.exp_log (div_pos (by linarith) hr₁_pos)]
            _ = r₃ := mul_div_cancel₀ r₃ hr₁_pos.ne'
        have hr₃_lt_R₀ : r₃ < 3 / 2 - η / 2 := by dsimp [r₃]; linarith
        have hF_diff : DiffContOnCl ℂ F (Complex.HadamardThreeLines.verticalStrip 0 u_strip) := by
          have h_cl : closure (Complex.HadamardThreeLines.verticalStrip 0 u_strip) ⊆
              Complex.HadamardThreeLines.verticalClosedStrip 0 u_strip := by
            intro w hw
            have h_closed : IsClosed (Complex.HadamardThreeLines.verticalClosedStrip 0 u_strip) :=
              isClosed_Icc.preimage Complex.continuous_re
            exact h_closed.closure_subset_iff.mpr (fun z hz => ⟨hz.1.le, hz.2.le⟩) hw
          refine DifferentiableOn.diffContOnCl ?_
          intro w hw
          have hw_ball : s₀ + (r₁ : ℂ) * Complex.exp w ∈ ball s₀ (3 / 2 - η / 2) :=
            closedBall_subset_ball hr₃_lt_R₀ (h_map_strip w (h_cl hw))
          have h_inner_diff : DifferentiableAt ℂ (fun z : ℂ => s₀ + (r₁ : ℂ) * Complex.exp z) w :=
            (differentiableAt_id.cexp.const_mul _).const_add _
          exact ((hL_diff.differentiableAt (isOpen_ball.mem_nhds hw_ball)).comp w h_inner_diff).differentiableWithinAt
        have hF_bdd : BddAbove ((norm ∘ F) '' Complex.HadamardThreeLines.verticalClosedStrip 0 u_strip) := by
          refine ⟨M₃ * Real.log |s.im|, ?_⟩
          rintro y ⟨w, hw, rfl⟩
          exact h_outer _ (h_map_strip w hw)
        have hF_left : ∀ w ∈ Complex.re ⁻¹' {0}, ‖F w‖ ≤ max M₁ 1 := by
          intro w hw
          have hw_cb : s₀ + (r₁ : ℂ) * Complex.exp w ∈ closedBall s₀ r₁ := by
            rw [mem_closedBall_iff_norm, add_sub_cancel_left, norm_mul, Complex.norm_real,
              Real.norm_eq_abs, abs_of_pos hr₁_pos, Complex.norm_exp]
            simp only [Set.mem_preimage, Set.mem_singleton_iff] at hw
            rw [hw, Real.exp_zero, mul_one]
          exact (h_inner _ hw_cb).trans (le_max_left _ _)
        have h_log_tail_ge1 : 1 ≤ M₃ * Real.log |s.im| := by
          have h_ex : Real.exp (1 / M₃) ≤ |s.im| := (le_max_right 6 _).trans him_gt.le
          have h_log : 1 / M₃ ≤ Real.log |s.im| := by
            have := Real.log_le_log (Real.exp_pos _) h_ex
            rwa [Real.log_exp] at this
          calc 1 = M₃ * (1 / M₃) := (mul_div_cancel₀ 1 hM₃_pos.ne').symm
            _ ≤ M₃ * Real.log |s.im| := mul_le_mul_of_nonneg_left h_log hM₃_pos.le
        have hF_right : ∀ w ∈ Complex.re ⁻¹' {u_strip}, ‖F w‖ ≤ M₃ * Real.log |s.im| := by
          intro w hw
          have hw_re : w.re = u_strip := hw
          exact h_outer _ (h_map_strip w ⟨hw_re.symm ▸ hu_pos.le, hw_re.le⟩)
        set w_s : ℂ := (Real.log (r_s / r₁) : ℂ) + (Real.pi : ℂ) * I
        have hw_s_re : w_s.re = Real.log (r_s / r₁) := by simp [w_s]
        have h_rs_gt1 : 1 < r_s / r₁ := (one_lt_div hr₁_pos).mpr hr_lo
        have h_rs_le_r3 : r_s / r₁ ≤ r₃ / r₁ := div_le_div_of_nonneg_right (hr_hi.trans hr₂max_lt_r₃.le) hr₁_pos.le
        have hw_s_mem : w_s ∈ Complex.HadamardThreeLines.verticalClosedStrip 0 u_strip := by
          refine ⟨?_, ?_⟩
          · rw [hw_s_re]; exact (Real.log_pos h_rs_gt1).le
          · rw [hw_s_re]; exact Real.log_le_log (by positivity) h_rs_le_r3
        have hFs : F w_s = logZ s := by
          dsimp [F]
          congr 1
          have hexp_ws : Complex.exp w_s = - ((r_s / r₁ : ℝ) : ℂ) := by
            dsimp [w_s]
            rw [Complex.exp_add, Complex.exp_pi_mul_I, mul_neg_one, ← Complex.ofReal_exp,
              Real.exp_log (div_pos (by linarith) hr₁_pos)]
          rw [hexp_ws, mul_neg, ← Complex.ofReal_mul, mul_div_cancel₀ r_s hr₁_pos.ne']
          apply Complex.ext <;> simp [s₀, r_s]
        have h_htl := Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'
          hu_pos hw_s_mem hF_diff hF_bdd hF_left hF_right
        rw [hFs] at h_htl
        set β : ℝ := (w_s.re - 0) / (u_strip - 0)
        have hβ0 : 0 ≤ β := by
          dsimp [β]; rw [sub_zero, sub_zero]
          exact div_nonneg hw_s_mem.1 hu_pos.le
        have hβ_le_θ : β ≤ θ := by
          dsimp [β, θ]; rw [sub_zero, sub_zero, hw_s_re]
          exact div_le_div_of_nonneg_right
            (Real.log_le_log (by positivity) (div_le_div_of_nonneg_right hr_hi hr₁_pos.le)) hu_pos.le
        have h_one_sub_le : (max M₁ 1) ^ (1 - β) ≤ max M₁ 1 := by
          have hge1 : 1 ≤ max M₁ 1 := le_max_right _ _
          have h1mβ : 1 - β ≤ 1 := by linarith
          calc (max M₁ 1) ^ (1 - β) ≤ (max M₁ 1) ^ (1 : ℝ) :=
                Real.rpow_le_rpow_of_exponent_le hge1 h1mβ
            _ = max M₁ 1 := Real.rpow_one _
        have h_right_rpow : (M₃ * Real.log |s.im|) ^ β ≤ (M₃ * Real.log |s.im|) ^ θ :=
          Real.rpow_le_rpow_of_exponent_le h_log_tail_ge1 hβ_le_θ
        have h_logZ_le : ‖logZ s‖ ≤ A_coef * (Real.log |s.im|) ^ θ := by
          calc ‖logZ s‖
              ≤ (max M₁ 1) ^ (1 - β) * (M₃ * Real.log |s.im|) ^ β := by
                simpa [β] using h_htl
            _ ≤ max M₁ 1 * (M₃ * Real.log |s.im|) ^ θ :=
                mul_le_mul h_one_sub_le h_right_rpow (Real.rpow_nonneg (by positivity) _) (by positivity)
            _ = A_coef * (Real.log |s.im|) ^ θ := by
                have hlog_nn : 0 ≤ Real.log |s.im| := (Real.log_pos (by linarith)).le
                rw [Real.mul_rpow hM₃_pos.le hlog_nn]
                dsimp [A_coef]; ring
        have h_log_im_nn : 0 ≤ Real.log |s.im| := (Real.log_pos (by linarith)).le
        have h_lin : ‖logZ s‖ ≤ eps * Real.log |s.im| + B_sub :=
          h_logZ_le.trans (h_sublin (Real.log |s.im|) h_log_im_nn)
        have hexp_s : Complex.exp (logZ s) = riemannZeta s := by
          have hs_ball : s ∈ ball s₀ (3 / 2 - η / 2) :=
            closedBall_subset_ball hr₃_lt_R₀ (by
              rw [mem_closedBall_iff_norm]
              have hsub : s - s₀ = ((s.re - 2 : ℝ) : ℂ) := by apply Complex.ext <;> simp [s₀]
              rw [hsub, Complex.norm_real, Real.norm_eq_abs, abs_le]
              dsimp [r₃, η] at *; constructor <;> linarith)
          exact h_exp_eq s hs_ball
        have him_pos : 0 < |s.im| := by linarith
        have h_inv_norm : ‖zetaInv s‖ ≤ Real.exp B_sub * |s.im| ^ eps := by
          have hz_eq : zetaInv s = (riemannZeta s)⁻¹ := by simp [zetaInv, hs_ne1]
          rw [hz_eq, norm_inv, ← hexp_s, Complex.norm_exp, ← Real.exp_neg]
          have h_neg_le : -(logZ s).re ≤ ‖logZ s‖ := by
            linarith [neg_le_abs (logZ s).re, Complex.abs_re_le_norm (logZ s)]
          calc Real.exp (-(logZ s).re)
              ≤ Real.exp ‖logZ s‖ := Real.exp_le_exp.mpr h_neg_le
            _ ≤ Real.exp (eps * Real.log |s.im| + B_sub) := Real.exp_le_exp.mpr h_lin
            _ = Real.exp B_sub * Real.exp (eps * Real.log |s.im|) := by rw [Real.exp_add, mul_comm]
            _ = Real.exp B_sub * |s.im| ^ eps := by
                rw [mul_comm eps, Real.rpow_def_of_pos him_pos]
        have h_expB_le_C : Real.exp B_sub ≤ C := by
          dsimp [C]
          have h1 := (le_max_left (Real.exp B_sub) (Real.exp M₁)).trans
            (le_max_right (max B_box 0) _) |>.trans (le_max_right 4 _)
          linarith
        have h_im_le : |s.im| ^ eps ≤ (1 + |s.im|) ^ eps :=
          Real.rpow_le_rpow (abs_nonneg _) (by linarith) heps.le
        exact h_inv_norm.trans (mul_le_mul h_expB_le_C h_im_le (by positivity) hC_pos.le)

/-! ### Stage 4: Compactly Supported Trapezoidal Cutoff & Mellin–Mertens Inversion at Re(s) = 2 -/

/-- Continuous compactly supported trapezoidal cutoff matching `1` on `[1, X]`, linear on `[1/2, 1]`
and `[X, X + H]`, and `0` outside `(1/2, X + H)`. -/
noncomputable def cutoffPhi (X H t : ℝ) : ℂ :=
  ((min (max 0 (min 1 (2 * t - 1))) (max 0 (min 1 ((X + H - t) / H))) : ℝ) : ℂ)

lemma continuous_cutoffPhi (X H : ℝ) : Continuous (cutoffPhi X H) := by
  unfold cutoffPhi
  fun_prop

lemma cutoffPhi_eq_zero_of_le_half (X H : ℝ) {t : ℝ} (ht : t ≤ 1 / 2) :
    cutoffPhi X H t = 0 := by
  have h1 : 2 * t - 1 ≤ 0 := by linarith
  have h2 : min 1 (2 * t - 1) ≤ 0 := min_le_of_right_le h1
  have h3 : max (0 : ℝ) (min 1 (2 * t - 1)) = 0 := max_eq_left h2
  have _h4 : (0 : ℝ) ≤ max 0 (min 1 ((X + H - t) / H)) := le_max_left _ _
  simp [cutoffPhi, h3]

lemma cutoffPhi_eq_zero_of_ge (X : ℝ) {H t : ℝ} (hH : 0 < H) (ht : X + H ≤ t) :
    cutoffPhi X H t = 0 := by
  have h1 : (X + H - t) / H ≤ 0 := div_nonpos_of_nonpos_of_nonneg (by linarith) hH.le
  have h2 : min 1 ((X + H - t) / H) ≤ 0 := min_le_of_right_le h1
  have h3 : max (0 : ℝ) (min 1 ((X + H - t) / H)) = 0 := max_eq_left h2
  have _h4 : (0 : ℝ) ≤ max 0 (min 1 (2 * t - 1)) := le_max_left _ _
  simp [cutoffPhi, h3]

lemma cutoffPhi_eq_left {X H t : ℝ} (hX : 1 ≤ X) (hH : 0 < H)
    (ht1 : 1 / 2 ≤ t) (ht2 : t ≤ 1) :
    cutoffPhi X H t = ((2 * t - 1 : ℝ) : ℂ) := by
  have hA1 : 2 * t - 1 ≤ 1 := by linarith
  have hA0 : 0 ≤ 2 * t - 1 := by linarith
  have hA : max (0 : ℝ) (min 1 (2 * t - 1)) = 2 * t - 1 := by
    rw [min_eq_right hA1, max_eq_right hA0]
  have hB1 : 1 ≤ (X + H - t) / H := (one_le_div hH).2 (by linarith)
  have hB : max (0 : ℝ) (min 1 ((X + H - t) / H)) = 1 := by
    rw [min_eq_left hB1, max_eq_right zero_le_one]
  simp [cutoffPhi, hA, hB, min_eq_left hA1]

lemma cutoffPhi_eq_one_of_Icc {X H t : ℝ} (_hX : 1 ≤ X) (hH : 0 < H)
    (ht1 : 1 ≤ t) (ht2 : t ≤ X) :
    cutoffPhi X H t = 1 := by
  have hA1 : 1 ≤ 2 * t - 1 := by linarith
  have hA : max (0 : ℝ) (min 1 (2 * t - 1)) = 1 := by
    rw [min_eq_left hA1, max_eq_right zero_le_one]
  have hB1 : 1 ≤ (X + H - t) / H := (one_le_div hH).2 (by linarith)
  have hB : max (0 : ℝ) (min 1 ((X + H - t) / H)) = 1 := by
    rw [min_eq_left hB1, max_eq_right zero_le_one]
  simp [cutoffPhi, hA, hB]

lemma cutoffPhi_eq_right {X H t : ℝ} (_hX : 1 ≤ X) (hH : 0 < H)
    (ht1 : X ≤ t) (ht2 : t ≤ X + H) :
    cutoffPhi X H t = (((X + H - t) / H : ℝ) : ℂ) := by
  have hA1 : 1 ≤ 2 * t - 1 := by linarith
  have hA : max (0 : ℝ) (min 1 (2 * t - 1)) = 1 := by
    rw [min_eq_left hA1, max_eq_right zero_le_one]
  have hB1 : (X + H - t) / H ≤ 1 := (div_le_one hH).2 (by linarith)
  have hB0 : 0 ≤ (X + H - t) / H := div_nonneg (by linarith) hH.le
  have hB : max (0 : ℝ) (min 1 ((X + H - t) / H)) = (X + H - t) / H := by
    rw [min_eq_right hB1, max_eq_right hB0]
  rw [cutoffPhi, hA, hB, min_eq_right hB1]

lemma norm_cutoffPhi_le_one (X H t : ℝ) : ‖cutoffPhi X H t‖ ≤ 1 := by
  unfold cutoffPhi
  set a : ℝ := max 0 (min 1 (2 * t - 1))
  set b : ℝ := max 0 (min 1 ((X + H - t) / H))
  have ha0 : 0 ≤ a := le_max_left _ _
  have ha1 : a ≤ 1 := max_le zero_le_one (min_le_left _ _)
  have hb0 : 0 ≤ b := le_max_left _ _
  have hm0 : 0 ≤ min a b := le_min ha0 hb0
  have hm1 : min a b ≤ 1 := (min_le_left a b).trans ha1
  rw [Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg hm0]
  exact hm1

lemma summable_moebius_mul_cutoffPhi {X H : ℝ} (hH : 0 < H) :
    Summable (fun n : ℕ => (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) := by
  refine summable_of_ne_finset_zero (s := Finset.Iic (Nat.floor (X + H))) ?_
  intro n hn
  simp only [Finset.mem_Iic, not_le] at hn
  have hXHn : X + H < (n : ℝ) := by
    have hfloor : X + H < ((Nat.floor (X + H) : ℕ) : ℝ) + 1 := Nat.lt_floor_add_one _
    have hn_ge : ((Nat.floor (X + H) : ℕ) : ℝ) + 1 ≤ (n : ℝ) := by exact_mod_cast hn
    linarith
  rw [cutoffPhi_eq_zero_of_ge X hH hXHn.le, mul_zero]

lemma tsum_moebius_mul_cutoffPhi_sub_mertens_norm_le {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H) :
    ‖(∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) - (RiemannBlueprint.mertens X : ℂ)‖ ≤ H + 1 := by
  set N : ℕ := Nat.floor (X + H)
  set M : ℕ := Nat.floor X
  have hMN : M ≤ N := Nat.floor_mono (by linarith)
  have h_tsum :
      (∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) =
        ∑ n ∈ Finset.Iic N, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n := by
    refine tsum_eq_sum ?_
    intro n hn
    simp only [Finset.mem_Iic, not_le] at hn
    have hXHn : X + H < (n : ℝ) := by
      have hfloor : X + H < (N : ℝ) + 1 := Nat.lt_floor_add_one _
      have hn_ge : (N : ℝ) + 1 ≤ (n : ℝ) := by exact_mod_cast hn
      linarith
    rw [cutoffPhi_eq_zero_of_ge X hH hXHn.le, mul_zero]
  have h_mertens_cast :
      (RiemannBlueprint.mertens X : ℂ) =
        ∑ n ∈ Finset.Iic M, (ArithmeticFunction.moebius n : ℂ) := by
    simp [RiemannBlueprint.mertens, M]
  have h_split :
      (∑ n ∈ Finset.Iic N, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) =
        (∑ n ∈ Finset.Iic M, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) +
        ∑ n ∈ Finset.Ioc M N, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n := by
    have hIic : Finset.Iic N = Finset.Iic M ∪ Finset.Ioc M N := by
      ext n
      simp only [Finset.mem_union, Finset.mem_Iic, Finset.mem_Ioc]
      omega
    have hdisj : Disjoint (Finset.Iic M) (Finset.Ioc M N) := by
      rw [Finset.disjoint_left]
      intro n hn1 hn2
      simp only [Finset.mem_Iic] at hn1
      simp only [Finset.mem_Ioc] at hn2
      omega
    rw [hIic, Finset.sum_union hdisj]
  have h_main :
      (∑ n ∈ Finset.Iic M, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) =
        ∑ n ∈ Finset.Iic M, (ArithmeticFunction.moebius n : ℂ) := by
    refine Finset.sum_congr rfl fun n hn => ?_
    rcases Nat.eq_zero_or_pos n with rfl | hn_pos
    · simp
    · have hn1 : (1 : ℝ) ≤ n := by exact_mod_cast hn_pos
      have hnX : (n : ℝ) ≤ X :=
        (Nat.le_floor_iff (by linarith : 0 ≤ X)).mp (Finset.mem_Iic.mp hn)
      rw [cutoffPhi_eq_one_of_Icc hX hH hn1 hnX, mul_one]
  rw [h_tsum, h_mertens_cast, h_split, h_main, add_sub_cancel_left]
  calc ‖∑ n ∈ Finset.Ioc M N, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖
      ≤ ∑ n ∈ Finset.Ioc M N, ‖(ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ :=
        norm_sum_le _ _
    _ ≤ ∑ _n ∈ Finset.Ioc M N, (1 : ℝ) := by
        refine Finset.sum_le_sum fun n _ => ?_
        rw [norm_mul]
        have hmu : ‖(ArithmeticFunction.moebius n : ℂ)‖ ≤ 1 := by
          simpa [Complex.norm_intCast] using
            (show |(ArithmeticFunction.moebius n : ℝ)| ≤ 1 by
              exact_mod_cast ArithmeticFunction.abs_moebius_le_one (n := n))
        exact (mul_le_mul hmu (norm_cutoffPhi_le_one X H n) (norm_nonneg _) zero_le_one).trans_eq
          (one_mul 1)
    _ = ((Finset.Ioc M N).card : ℝ) := by simp
    _ = (N - M : ℝ) := by
        rw [Nat.card_Ioc, Nat.cast_sub hMN]
    _ ≤ H + 1 := by
        have hN_le : (N : ℝ) ≤ X + H := Nat.floor_le (by linarith)
        have hM_gt : X - 1 < (M : ℝ) := by linarith [Nat.lt_floor_add_one X]
        linarith

private lemma indicator_Ioi_cutoffPhi (X H : ℝ) (hH : 0 < H) (g : ℝ → ℂ) :
    Set.indicator (Set.Ioi (0 : ℝ)) (fun t => g t * cutoffPhi X H t) =
      Set.indicator (Set.Ioc (1 / 2 : ℝ) (X + H)) (fun t => g t * cutoffPhi X H t) := by
  ext t
  by_cases h1 : 1 / 2 < t <;> by_cases h2 : t ≤ X + H
  · have h0 : 0 < t := by linarith
    rw [Set.indicator_of_mem (show t ∈ Set.Ioi (0 : ℝ) from h0),
      Set.indicator_of_mem (show t ∈ Set.Ioc (1 / 2 : ℝ) (X + H) from ⟨h1, h2⟩)]
  · have h0 : 0 < t := by linarith
    rw [Set.indicator_of_mem (show t ∈ Set.Ioi (0 : ℝ) from h0),
      Set.indicator_of_notMem (show t ∉ Set.Ioc (1 / 2 : ℝ) (X + H) from fun h => h2 h.2),
      cutoffPhi_eq_zero_of_ge X hH (le_of_not_ge h2), mul_zero]
  · rw [Set.indicator_of_notMem (show t ∉ Set.Ioc (1 / 2 : ℝ) (X + H) from fun h => h1 h.1)]
    by_cases h0 : 0 < t
    · rw [Set.indicator_of_mem (show t ∈ Set.Ioi (0 : ℝ) from h0),
        cutoffPhi_eq_zero_of_le_half X H (le_of_not_gt h1), mul_zero]
    · rw [Set.indicator_of_notMem (show t ∉ Set.Ioi (0 : ℝ) from h0)]
  · rw [Set.indicator_of_notMem (show t ∉ Set.Ioc (1 / 2 : ℝ) (X + H) from fun h => h1 h.1)]
    by_cases h0 : 0 < t
    · rw [Set.indicator_of_mem (show t ∈ Set.Ioi (0 : ℝ) from h0),
        cutoffPhi_eq_zero_of_le_half X H (le_of_not_gt h1), mul_zero]
    · rw [Set.indicator_of_notMem (show t ∉ Set.Ioi (0 : ℝ) from h0)]

/-- Closed form of the Mellin transform of `cutoffPhi X H` for `0 < s.re`. -/
theorem mellin_cutoffPhi_eq {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H) {s : ℂ} (hs : 0 < s.re) :
    mellin (cutoffPhi X H) s =
      (((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-s)) /
        (s * (s + 1)) := by
  have hs0 : s ≠ 0 := by intro h; rw [h] at hs; simp at hs
  have hs1 : s + 1 ≠ 0 := by
    intro h
    have := congrArg Complex.re h
    simp at this
    linarith
  have hH0 : (H : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr hH.ne'
  let F : ℝ → ℂ := fun t => (t : ℂ) ^ (s - 1) * cutoffPhi X H t
  have h_mellin : mellin (cutoffPhi X H) s = ∫ t in (1 / 2 : ℝ)..(X + H), F t := by
    rw [mellin]
    have h_smul : (fun t : ℝ => (t : ℂ) ^ (s - 1) • cutoffPhi X H t) = F := by
      ext t; simp [F, smul_eq_mul]
    rw [h_smul, ← MeasureTheory.integral_indicator measurableSet_Ioi,
      indicator_Ioi_cutoffPhi X H hH (fun t : ℝ => (t : ℂ) ^ (s - 1)),
      MeasureTheory.integral_indicator measurableSet_Ioc,
      intervalIntegral.integral_of_le (by linarith : (1 / 2 : ℝ) ≤ X + H)]
  have h_cont_F : ContinuousOn F (Set.Icc (1 / 2 : ℝ) (X + H)) := by
    refine ContinuousOn.mul ?_ (continuous_cutoffPhi X H).continuousOn
    refine ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const ?_
    intro t ht
    have ht_pos : 0 < t := by linarith [ht.1]
    exact Complex.ofReal_mem_slitPlane.mpr ht_pos
  have hI₁ : IntervalIntegrable F MeasureTheory.volume (1 / 2 : ℝ) 1 :=
    (h_cont_F.mono (Set.Icc_subset_Icc le_rfl (by linarith))).intervalIntegrable_of_Icc
      (by norm_num)
  have hI₂ : IntervalIntegrable F MeasureTheory.volume 1 X :=
    (h_cont_F.mono (Set.Icc_subset_Icc (by linarith) (by linarith))).intervalIntegrable_of_Icc
      hX
  have hI₃ : IntervalIntegrable F MeasureTheory.volume X (X + H) :=
    (h_cont_F.mono (Set.Icc_subset_Icc (by linarith) le_rfl)).intervalIntegrable_of_Icc
      (by linarith)
  have h_split : (∫ t in (1 / 2 : ℝ)..(X + H), F t) =
      (∫ t in (1 / 2 : ℝ)..1, F t) + (∫ t in (1 : ℝ)..X, F t) + (∫ t in X..(X + H), F t) := by
    have h12 : (∫ t in (1 / 2 : ℝ)..X, F t) =
        (∫ t in (1 / 2 : ℝ)..1, F t) + (∫ t in (1 : ℝ)..X, F t) :=
      (intervalIntegral.integral_add_adjacent_intervals hI₁ hI₂).symm
    have hI12 : IntervalIntegrable F MeasureTheory.volume (1 / 2 : ℝ) X := hI₁.trans hI₂
    rw [← intervalIntegral.integral_add_adjacent_intervals hI12 hI₃, h12]
  -- Evaluate piece 1: ∫ (1/2)..1 F
  have h_p1 : (∫ t in (1 / 2 : ℝ)..1, F t) =
      (s - 1 + (2 : ℂ) ^ (-s)) / (s * (s + 1)) := by
    have h_eq : Set.EqOn F (fun t : ℝ => (2 : ℂ) * (t : ℂ) ^ s - (t : ℂ) ^ (s - 1))
        (Set.uIcc (1 / 2 : ℝ) 1) := by
      intro t ht
      have ht' : t ∈ Set.Icc (1 / 2 : ℝ) 1 := by
        rw [Set.uIcc_of_le (by norm_num : (1 / 2 : ℝ) ≤ 1)] at ht
        exact ht
      have ht_pos : 0 < t := by linarith [ht'.1]
      dsimp [F]
      rw [cutoffPhi_eq_left hX hH ht'.1 ht'.2]
      push_cast
      have hpow : (t : ℂ) ^ (s - 1) * (t : ℂ) = (t : ℂ) ^ s := by
        have ht0 : (t : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr ht_pos.ne'
        calc (t : ℂ) ^ (s - 1) * (t : ℂ)
            = (t : ℂ) ^ (s - 1) * (t : ℂ) ^ (1 : ℂ) := by rw [Complex.cpow_one]
          _ = (t : ℂ) ^ ((s - 1) + 1) := (Complex.cpow_add _ _ ht0).symm
          _ = (t : ℂ) ^ s := by ring_nf
      calc (t : ℂ) ^ (s - 1) * (2 * (t : ℂ) - 1)
          = 2 * ((t : ℂ) ^ (s - 1) * (t : ℂ)) - (t : ℂ) ^ (s - 1) := by ring
        _ = 2 * (t : ℂ) ^ s - (t : ℂ) ^ (s - 1) := by rw [hpow]
    have hc1 : ContinuousOn (fun t : ℝ => (2 : ℂ) * (t : ℂ) ^ s) (Set.Icc (1 / 2 : ℝ) 1) := by
      refine ContinuousOn.mul continuousOn_const ?_
      exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
        fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
    have hc2 : ContinuousOn (fun t : ℝ => (t : ℂ) ^ (s - 1)) (Set.Icc (1 / 2 : ℝ) 1) := by
      exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
        fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
    rw [intervalIntegral.integral_congr h_eq,
      intervalIntegral.integral_sub (hc1.intervalIntegrable_of_Icc (by norm_num))
        (hc2.intervalIntegrable_of_Icc (by norm_num)),
      intervalIntegral.integral_const_mul]
    have h_int_s : (∫ t in (1 / 2 : ℝ)..1, (t : ℂ) ^ s) =
        ((1 : ℂ) ^ (s + 1) - ((1 / 2 : ℝ) : ℂ) ^ (s + 1)) / (s + 1) :=
      integral_cpow (Or.inl (by linarith))
    have h_int_s1 : (∫ t in (1 / 2 : ℝ)..1, (t : ℂ) ^ (s - 1)) =
        ((1 : ℂ) ^ s - ((1 / 2 : ℝ) : ℂ) ^ s) / s := by
      simpa [sub_add_cancel] using
        (integral_cpow (a := (1 / 2 : ℝ)) (b := 1) (r := s - 1)
          (Or.inl (by simp; linarith)))
    have h_half_s : ((1 / 2 : ℝ) : ℂ) ^ s = (2 : ℂ) ^ (-s) := by
      have h2r : (2 : ℂ) = ((2 : ℝ) : ℂ) := by norm_cast
      have h2ne : (2 : ℂ) ^ s ≠ 0 := Complex.cpow_ne_zero_iff.mpr (Or.inl (by norm_num))
      apply mul_right_cancel₀ h2ne
      calc ((1 / 2 : ℝ) : ℂ) ^ s * (2 : ℂ) ^ s
          = ((1 / 2 : ℝ) : ℂ) ^ s * ((2 : ℝ) : ℂ) ^ s := by rw [← h2r]
        _ = (((1 / 2 : ℝ) * (2 : ℝ) : ℝ) : ℂ) ^ s := by
            rw [← Complex.mul_cpow_ofReal_nonneg (by norm_num) (by norm_num)]
            norm_cast
        _ = (1 : ℂ) ^ s := by norm_num
        _ = 1 := Complex.one_cpow s
        _ = (2 : ℂ) ^ (-s + s) := by simp
        _ = (2 : ℂ) ^ (-s) * (2 : ℂ) ^ s := Complex.cpow_add _ _ (by norm_num)
    have h_half_s1 : ((1 / 2 : ℝ) : ℂ) ^ (s + 1) = (2 : ℂ) ^ (-s) * (2 : ℂ)⁻¹ := by
      have h_half_c : ((1 / 2 : ℝ) : ℂ) = (2 : ℂ)⁻¹ := by norm_num
      rw [Complex.cpow_add _ _ (by norm_num), Complex.cpow_one, h_half_s, h_half_c]
    rw [h_int_s, h_int_s1, Complex.one_cpow, Complex.one_cpow, h_half_s, h_half_s1]
    field_simp [hs0, hs1]
    ring
  -- Evaluate piece 2: ∫ 1..X F
  have h_p2 : (∫ t in (1 : ℝ)..X, F t) = ((X : ℂ) ^ s - 1) / s := by
    have h_eq : Set.EqOn F (fun t : ℝ => (t : ℂ) ^ (s - 1)) (Set.uIcc (1 : ℝ) X) := by
      intro t ht
      have ht' : t ∈ Set.Icc (1 : ℝ) X := by simpa [Set.uIcc_of_le hX] using ht
      simp [F, cutoffPhi_eq_one_of_Icc hX hH ht'.1 ht'.2]
    rw [intervalIntegral.integral_congr h_eq]
    simpa [sub_add_cancel, Complex.one_cpow] using
      (integral_cpow (a := (1 : ℝ)) (b := X) (r := s - 1)
        (Or.inl (by simp; linarith)))
  -- Evaluate piece 3: ∫ X..(X+H) F
  have h_p3 : (∫ t in X..(X + H), F t) =
      ((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ) - (s + 1) * (X : ℂ) ^ s) /
        (s * (s + 1)) := by
    have h_eq : Set.EqOn F
        (fun t : ℝ => ((((X + H : ℝ) : ℂ) / (H : ℂ)) * (t : ℂ) ^ (s - 1)) -
          ((H : ℂ)⁻¹ * (t : ℂ) ^ s)) (Set.uIcc X (X + H)) := by
      intro t ht
      have ht' : t ∈ Set.Icc X (X + H) := by
        simpa [Set.uIcc_of_le (by linarith : X ≤ X + H)] using ht
      have ht_pos : 0 < t := by linarith [ht'.1]
      dsimp [F]
      rw [cutoffPhi_eq_right hX hH ht'.1 ht'.2]
      push_cast
      have hpow : (t : ℂ) ^ (s - 1) * (t : ℂ) = (t : ℂ) ^ s := by
        have ht0 : (t : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr ht_pos.ne'
        calc (t : ℂ) ^ (s - 1) * (t : ℂ)
            = (t : ℂ) ^ (s - 1) * (t : ℂ) ^ (1 : ℂ) := by rw [Complex.cpow_one]
          _ = (t : ℂ) ^ ((s - 1) + 1) := (Complex.cpow_add _ _ ht0).symm
          _ = (t : ℂ) ^ s := by ring_nf
      calc (t : ℂ) ^ (s - 1) * (((X : ℂ) + (H : ℂ) - (t : ℂ)) / (H : ℂ))
          = ((((X : ℂ) + (H : ℂ)) / (H : ℂ)) * (t : ℂ) ^ (s - 1)) -
              ((H : ℂ)⁻¹ * ((t : ℂ) ^ (s - 1) * (t : ℂ))) := by ring
        _ = ((((X : ℂ) + (H : ℂ)) / (H : ℂ)) * (t : ℂ) ^ (s - 1)) -
              ((H : ℂ)⁻¹ * (t : ℂ) ^ s) := by
              rw [hpow]
    have hc1 : ContinuousOn
        (fun t : ℝ => (((X + H : ℝ) : ℂ) / (H : ℂ)) * (t : ℂ) ^ (s - 1)) (Set.Icc X (X + H)) := by
      refine ContinuousOn.mul continuousOn_const ?_
      exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
        fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
    have hc2 : ContinuousOn
        (fun t : ℝ => (H : ℂ)⁻¹ * (t : ℂ) ^ s) (Set.Icc X (X + H)) := by
      refine ContinuousOn.mul continuousOn_const ?_
      exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
        fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
    rw [intervalIntegral.integral_congr h_eq,
      intervalIntegral.integral_sub (hc1.intervalIntegrable_of_Icc (by linarith))
        (hc2.intervalIntegrable_of_Icc (by linarith)),
      intervalIntegral.integral_const_mul, intervalIntegral.integral_const_mul]
    have h_int_s1 : (∫ t in X..(X + H), (t : ℂ) ^ (s - 1)) =
        (((X + H : ℝ) : ℂ) ^ s - (X : ℂ) ^ s) / s := by
      simpa [sub_add_cancel] using
        (integral_cpow (a := X) (b := X + H) (r := s - 1)
          (Or.inl (by simp; linarith)))
    have h_int_s : (∫ t in X..(X + H), (t : ℂ) ^ s) =
        (((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (s + 1) :=
      integral_cpow (Or.inl (by linarith))
    have hpow_XH : ((X + H : ℝ) : ℂ) ^ (s + 1) = ((X + H : ℝ) : ℂ) ^ s * ((X + H : ℝ) : ℂ) := by
      rw [Complex.cpow_add _ _ (Complex.ofReal_ne_zero.mpr (by linarith)), Complex.cpow_one]
    have hpow_X : (X : ℂ) ^ (s + 1) = (X : ℂ) ^ s * (X : ℂ) := by
      rw [Complex.cpow_add _ _ (Complex.ofReal_ne_zero.mpr (by linarith)), Complex.cpow_one]
    rw [h_int_s1, h_int_s, hpow_XH, hpow_X]
    push_cast
    field_simp [hs0, hs1, hH0]
    ring
  rw [h_mellin, h_split, h_p1, h_p2, h_p3]
  field_simp [hs0, hs1, hH0]
  ring

/-- Quadratic vertical decay of `mellin (cutoffPhi X H)` on `{s : ℂ | 0 < s.re}`. -/
lemma norm_mellin_cutoffPhi_le_div_sq {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H)
    {s : ℂ} (hs : 0 < s.re) :
    ‖mellin (cutoffPhi X H) s‖ ≤
      (2 * (X + H) ^ (s.re + 1) / H + 3) / (s.re ^ 2 + s.im ^ 2) := by
  rw [mellin_cutoffPhi_eq hX hH hs]
  have hXH_pos : 0 < X + H := by linarith
  have hX_pos : 0 < X := by linarith
  have h_num1 : ‖((X + H : ℝ) : ℂ) ^ (s + 1)‖ = (X + H) ^ (s.re + 1) := by
    simpa [Complex.add_re, Complex.one_re] using
      Complex.norm_cpow_eq_rpow_re_of_pos hXH_pos (s + 1)
  have h_num2 : ‖(X : ℂ) ^ (s + 1)‖ = X ^ (s.re + 1) := by
    simpa [Complex.add_re, Complex.one_re] using
      Complex.norm_cpow_eq_rpow_re_of_pos hX_pos (s + 1)
  have h_pow_le : X ^ (s.re + 1) ≤ (X + H) ^ (s.re + 1) :=
    Real.rpow_le_rpow hX_pos.le (by linarith) (by linarith)
  have h_two_pow : ‖(2 : ℂ) ^ (-s)‖ ≤ 1 := by
    have h2 : (2 : ℂ) = ((2 : ℝ) : ℂ) := by norm_cast
    rw [h2, Complex.norm_cpow_eq_rpow_re_of_pos (by norm_num : (0 : ℝ) < 2) (-s), Complex.neg_re]
    exact Real.rpow_le_one_of_one_le_of_nonpos (by norm_num) (by linarith)
  have h_num :
      ‖((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-s)‖ ≤
        2 * (X + H) ^ (s.re + 1) / H + 3 := by
    have hdiv : ((X + H) ^ (s.re + 1) + X ^ (s.re + 1)) / H ≤
        2 * (X + H) ^ (s.re + 1) / H := by
      rw [two_mul]
      exact div_le_div_of_nonneg_right (add_le_add (le_refl _) h_pow_le) hH.le
    calc ‖((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-s)‖
        ≤ ‖(((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ) - 2‖ + ‖(2 : ℂ) ^ (-s)‖ :=
          norm_add_le _ _
      _ ≤ (‖(((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)‖ + ‖(2 : ℂ)‖) + 1 :=
          add_le_add (norm_sub_le _ _) h_two_pow
      _ = ((‖((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)‖ / H) + 2) + 1 := by
          rw [norm_div, Complex.norm_real, Real.norm_eq_abs, abs_of_pos hH,
            Complex.norm_ofNat]
      _ ≤ (((‖((X + H : ℝ) : ℂ) ^ (s + 1)‖ + ‖(X : ℂ) ^ (s + 1)‖) / H) + 2) + 1 := by
          gcongr
          exact norm_sub_le _ _
      _ = ((X + H) ^ (s.re + 1) + X ^ (s.re + 1)) / H + 3 := by
          rw [h_num1, h_num2]; ring
      _ ≤ 2 * (X + H) ^ (s.re + 1) / H + 3 := by linarith
  have h_den : s.re ^ 2 + s.im ^ 2 ≤ ‖s * (s + 1)‖ := by
    rw [norm_mul]
    have h_norm_sq : s.re ^ 2 + s.im ^ 2 = ‖s‖ ^ 2 := by
      rw [Complex.sq_norm, Complex.normSq_apply]
      ring
    have h_s_le_s1 : ‖s‖ ≤ ‖s + 1‖ := by
      rw [← sq_le_sq₀ (norm_nonneg _) (norm_nonneg _), Complex.sq_norm, Complex.sq_norm,
        Complex.normSq_apply, Complex.normSq_apply]
      simp only [Complex.add_re, Complex.one_re, Complex.add_im, Complex.one_im, add_zero]
      nlinarith
    rw [h_norm_sq, sq]
    exact mul_le_mul_of_nonneg_left h_s_le_s1 (norm_nonneg _)
  have h_pos_den : 0 < s.re ^ 2 + s.im ^ 2 := by positivity
  rw [norm_div]
  exact div_le_div₀ (by positivity) h_num h_pos_den h_den

/-- Linear `1 / ‖s‖` bound for `mellin (cutoffPhi X H)` independent of `H`. -/
lemma norm_mellin_cutoffPhi_le_div_norm {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H)
    {s : ℂ} (hs : 0 < s.re) :
    ‖mellin (cutoffPhi X H) s‖ ≤ 4 * (X + H) ^ s.re / ‖s‖ := by
  have hs0 : s ≠ 0 := by intro h; rw [h] at hs; simp at hs
  have hs1 : s + 1 ≠ 0 := by
    intro h
    have := congrArg Complex.re h
    simp at this
    linarith
  have hH0 : (H : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr hH.ne'
  have h_int_eq :
      mellin (cutoffPhi X H) s =
        (((H : ℂ)⁻¹ * (∫ t : ℝ in X..(X + H), (t : ℂ) ^ s)) + (-2 + (2 : ℂ) ^ (-s)) / (s + 1)) / s := by
    rw [mellin_cutoffPhi_eq hX hH hs,
      integral_cpow (Or.inl (by linarith))]
    field_simp [hs0, hs1, hH0]
    ring
  rw [h_int_eq, norm_div]
  have hXH_pos : 0 < X + H := by linarith
  have hXH_ge1 : 1 ≤ (X + H) ^ s.re := Real.one_le_rpow (by linarith) hs.le
  have h_int_bd : ‖(H : ℂ)⁻¹ * (∫ t : ℝ in X..(X + H), (t : ℂ) ^ s)‖ ≤ (X + H) ^ s.re := by
    rw [norm_mul, norm_inv, Complex.norm_real, Real.norm_eq_abs, abs_of_pos hH]
    have h_norm_c : ∀ t ∈ Set.uIoc X (X + H), ‖(t : ℂ) ^ s‖ ≤ (X + H) ^ s.re := by
      intro t ht
      rw [Set.uIoc_of_le (by linarith : X ≤ X + H)] at ht
      have ht_pos : 0 < t := by linarith [ht.1]
      rw [Complex.norm_cpow_eq_rpow_re_of_pos ht_pos s]
      exact Real.rpow_le_rpow ht_pos.le ht.2 hs.le
    have h_le := intervalIntegral.norm_integral_le_of_norm_le_const h_norm_c
    rw [abs_of_nonneg (by linarith : 0 ≤ X + H - X), show X + H - X = H by ring] at h_le
    calc H⁻¹ * ‖∫ t in X..(X + H), (t : ℂ) ^ s‖
        ≤ H⁻¹ * ((X + H) ^ s.re * H) := mul_le_mul_of_nonneg_left h_le (by positivity)
      _ = (X + H) ^ s.re := by field_simp [hH.ne']
  have h_s1_ge1 : 1 ≤ ‖s + 1‖ := by
    have h_re : 1 ≤ (s + 1).re := by simp; linarith
    exact h_re.trans (Complex.re_le_norm _)
  have h_two_pow : ‖(2 : ℂ) ^ (-s)‖ ≤ 1 := by
    have h2 : (2 : ℂ) = ((2 : ℝ) : ℂ) := by norm_cast
    rw [h2, Complex.norm_cpow_eq_rpow_re_of_pos (by norm_num : (0 : ℝ) < 2) (-s), Complex.neg_re]
    exact Real.rpow_le_one_of_one_le_of_nonpos (by norm_num) (by linarith)
  have h_tail_bd : ‖(-2 + (2 : ℂ) ^ (-s)) / (s + 1)‖ ≤ 3 := by
    rw [norm_div]
    have hnum : ‖(-2 : ℂ) + (2 : ℂ) ^ (-s)‖ ≤ 3 := by
      calc ‖(-2 : ℂ) + (2 : ℂ) ^ (-s)‖
          ≤ ‖(-2 : ℂ)‖ + ‖(2 : ℂ) ^ (-s)‖ := norm_add_le _ _
        _ ≤ 2 + 1 := by
            have h2 : ‖(-2 : ℂ)‖ = 2 := by simp
            linarith
        _ = 3 := by norm_num
    exact div_le_of_le_mul₀ (by positivity) (by norm_num) (hnum.trans (by linarith))
  have h_tot_num :
      ‖((H : ℂ)⁻¹ * (∫ t : ℝ in X..(X + H), (t : ℂ) ^ s)) + (-2 + (2 : ℂ) ^ (-s)) / (s + 1)‖ ≤
        4 * (X + H) ^ s.re := by
    calc ‖_‖ ≤ ‖(H : ℂ)⁻¹ * (∫ t : ℝ in X..(X + H), (t : ℂ) ^ s)‖ +
              ‖(-2 + (2 : ℂ) ^ (-s)) / (s + 1)‖ := norm_add_le _ _
      _ ≤ (X + H) ^ s.re + 3 := add_le_add h_int_bd h_tail_bd
      _ ≤ (X + H) ^ s.re + 3 * (X + H) ^ s.re := by linarith
      _ = 4 * (X + H) ^ s.re := by ring
  exact div_le_div_of_nonneg_right h_tot_num (norm_nonneg s)

lemma differentiableOn_mellin_cutoffPhi {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H) :
    DifferentiableOn ℂ (mellin (cutoffPhi X H)) {s : ℂ | 0 < s.re} := by
  let g : ℂ → ℂ := fun s =>
    (((((X + H : ℝ) : ℂ) ^ (s + 1) - (X : ℂ) ^ (s + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-s)) /
      (s * (s + 1))
  have hg_diff : DifferentiableOn ℂ g {s : ℂ | 0 < s.re} := by
    intro s hs
    simp only [Set.mem_ofPred_eq] at hs
    have hs0 : s ≠ 0 := by intro h; rw [h] at hs; simp at hs
    have hs1 : s + 1 ≠ 0 := by
      intro h; have := congrArg Complex.re h; simp at this; linarith
    have hd_XH : DifferentiableAt ℂ (fun z : ℂ => ((X + H : ℝ) : ℂ) ^ (z + 1)) s :=
      DifferentiableAt.const_cpow (differentiableAt_id.add (differentiableAt_const _))
        (Or.inl (Complex.ofReal_ne_zero.mpr (by linarith)))
    have hd_X : DifferentiableAt ℂ (fun z : ℂ => (X : ℂ) ^ (z + 1)) s :=
      DifferentiableAt.const_cpow (differentiableAt_id.add (differentiableAt_const _))
        (Or.inl (Complex.ofReal_ne_zero.mpr (by linarith)))
    have hd_2 : DifferentiableAt ℂ (fun z : ℂ => (2 : ℂ) ^ (-z)) s :=
      DifferentiableAt.const_cpow differentiableAt_id.neg (Or.inl (by norm_num))
    have hd_num : DifferentiableAt ℂ (fun z : ℂ =>
        (((((X + H : ℝ) : ℂ) ^ (z + 1) - (X : ℂ) ^ (z + 1)) / (H : ℂ)) - 2 + (2 : ℂ) ^ (-z))) s :=
      (((hd_XH.sub hd_X).div_const _).sub (differentiableAt_const _)).add hd_2
    have hd_den : DifferentiableAt ℂ (fun z : ℂ => z * (z + 1)) s :=
      differentiableAt_id.mul (differentiableAt_id.add (differentiableAt_const _))
    exact (hd_num.div hd_den (mul_ne_zero hs0 hs1)).differentiableWithinAt
  exact hg_diff.congr (fun s hs => mellin_cutoffPhi_eq hX hH hs)

lemma mellinConvergent_cutoffPhi {X H : ℝ} (_hX : 1 ≤ X) (hH : 0 < H) (σ : ℝ) :
    MellinConvergent (cutoffPhi X H) (σ : ℂ) := by
  let F : ℝ → ℂ := fun t => (t : ℂ) ^ ((σ : ℂ) - 1) * cutoffPhi X H t
  have h_cont : ContinuousOn F (Set.Icc (1 / 2 : ℝ) (X + H)) := by
    refine ContinuousOn.mul ?_ (continuous_cutoffPhi X H).continuousOn
    exact ContinuousOn.cpow continuous_ofReal.continuousOn continuousOn_const
      fun t ht => Complex.ofReal_mem_slitPlane.mpr (by linarith [ht.1])
  have h_int_Ioc : MeasureTheory.IntegrableOn F (Set.Ioc (1 / 2 : ℝ) (X + H)) :=
    h_cont.integrableOn_Icc.mono_set Set.Ioc_subset_Icc_self
  rw [MellinConvergent]
  have h_smul : (fun t : ℝ => (t : ℂ) ^ ((σ : ℂ) - 1) • cutoffPhi X H t) = F := by
    ext t; simp [F, smul_eq_mul]
  rw [h_smul, ← MeasureTheory.integrable_indicator_iff measurableSet_Ioi,
    indicator_Ioi_cutoffPhi X H hH (fun t : ℝ => (t : ℂ) ^ ((σ : ℂ) - 1)),
    MeasureTheory.integrable_indicator_iff measurableSet_Ioc]
  exact h_int_Ioc

lemma integrable_inv_sq_add_sq {σ : ℝ} (hσ : 0 < σ) :
    MeasureTheory.Integrable (fun y : ℝ => (σ ^ 2 + y ^ 2)⁻¹) := by
  have h1 : MeasureTheory.Integrable (fun u : ℝ => (1 + u ^ 2)⁻¹) := integrable_inv_one_add_sq
  have h2 := h1.comp_mul_left' (inv_ne_zero hσ.ne')
  refine (h2.const_mul (σ ^ 2)⁻¹).congr (Filter.Eventually.of_forall fun y => ?_)
  field_simp [hσ.ne']

lemma verticalIntegrable_mellin_cutoffPhi {X H σ : ℝ} (hX : 1 ≤ X) (hH : 0 < H) (hσ : 0 < σ) :
    Complex.VerticalIntegrable (mellin (cutoffPhi X H)) σ := by
  rw [Complex.VerticalIntegrable]
  have h_cont : Continuous (fun y : ℝ => mellin (cutoffPhi X H) (σ + y * Complex.I)) := by
    have hc : Continuous (fun y : ℝ => (σ : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
    refine (differentiableOn_mellin_cutoffPhi hX hH).continuousOn.comp_continuous hc fun y => ?_
    simp [hσ]
  set K : ℝ := 2 * (X + H) ^ (σ + 1) / H + 3
  refine (integrable_inv_sq_add_sq hσ |>.const_mul K).mono' h_cont.aestronglyMeasurable
    (Filter.Eventually.of_forall fun y => ?_)
  have hs_re : (σ + y * Complex.I).re = σ := by simp
  have hbd := norm_mellin_cutoffPhi_le_div_sq hX hH (s := σ + y * Complex.I) (by simpa using hσ)
  rw [hs_re] at hbd
  simpa [K, div_eq_mul_inv, mul_comm] using hbd

/-- Exact Mellin–Mertens identity for the trapezoidal cutoff at `Re(s) = 2`. -/
theorem sum_moebius_cutoffPhi_eq_mellinInv_two {X H : ℝ} (hX : 1 ≤ X) (hH : 0 < H) :
    (∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) =
      ((1 / (2 * Real.pi) : ℝ) : ℂ) *
        ∫ y : ℝ, zetaInv (2 + y * Complex.I) * mellin (cutoffPhi X H) (2 + y * Complex.I) := by
  set phi := cutoffPhi X H
  have h_mc2 : MellinConvergent phi 2 := by
    simpa using mellinConvergent_cutoffPhi hX hH 2
  have h_vi2 : Complex.VerticalIntegrable (mellin phi) 2 :=
    verticalIntegrable_mellin_cutoffPhi hX hH (by norm_num)
  let F : ℕ → ℝ → ℂ := fun n y =>
    if n = 0 then 0
    else (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I)) *
      mellin phi (2 + y * Complex.I)
  have h_term : ∀ n : ℕ,
      (ArithmeticFunction.moebius n : ℂ) * phi n =
        ((1 / (2 * Real.pi) : ℝ) : ℂ) * ∫ y : ℝ, F n y := by
    intro n
    rcases Nat.eq_zero_or_pos n with rfl | hn_pos
    · simp [F]
    · have hn_real_pos : (0 : ℝ) < n := Nat.cast_pos.mpr hn_pos
      have h_inv := mellinInv_mellin_eq 2 phi hn_real_pos h_mc2 h_vi2
        ((continuous_cutoffPhi X H).continuousAt)
      rw [mellinInv] at h_inv
      simp only [smul_eq_mul, Complex.real_smul] at h_inv
      have h_inv' :
          ((1 / (2 * Real.pi) : ℝ) : ℂ) *
            ∫ y : ℝ, (n : ℂ) ^ (-(2 + y * Complex.I)) * mellin phi (2 + y * Complex.I) = phi n := by
        simpa using h_inv
      rw [← h_inv']
      have hn0 : n ≠ 0 := hn_pos.ne'
      calc (ArithmeticFunction.moebius n : ℂ) *
            (((1 / (2 * Real.pi) : ℝ) : ℂ) *
              ∫ y : ℝ, (n : ℂ) ^ (-(2 + y * Complex.I)) * mellin phi (2 + y * Complex.I))
          = ((1 / (2 * Real.pi) : ℝ) : ℂ) *
            ((ArithmeticFunction.moebius n : ℂ) *
              ∫ y : ℝ, (n : ℂ) ^ (-(2 + y * Complex.I)) * mellin phi (2 + y * Complex.I)) := by ring
        _ = ((1 / (2 * Real.pi) : ℝ) : ℂ) * ∫ y : ℝ, F n y := by
            congr 1
            rw [← MeasureTheory.integral_const_mul]
            refine MeasureTheory.integral_congr_ae (Filter.Eventually.of_forall fun y => ?_)
            simp [F, hn0, mul_assoc]
  have h_aesm : ∀ n : ℕ, MeasureTheory.AEStronglyMeasurable (F n) MeasureTheory.volume := by
    intro n
    rcases Nat.eq_zero_or_pos n with rfl | hn_pos
    · simpa [F] using MeasureTheory.aestronglyMeasurable_const
    · have hc_m : Continuous (fun y : ℝ => mellin phi (2 + y * Complex.I)) := by
        have hc : Continuous (fun y : ℝ => (2 : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
        exact (differentiableOn_mellin_cutoffPhi hX hH).continuousOn.comp_continuous hc
          fun y => by norm_num
      have hc_p : Continuous (fun y : ℝ => (n : ℂ) ^ (-(2 + y * Complex.I))) := by
        refine Continuous.const_cpow ?_ (Or.inl (Complex.ofReal_ne_zero.mpr (Nat.cast_pos.mpr hn_pos).ne'))
        fun_prop
      have hF_eq : F n = fun y : ℝ =>
          (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I)) *
            mellin phi (2 + y * Complex.I) := by
        ext y; simp [F, hn_pos.ne']
      rw [hF_eq]
      exact ((continuous_const.mul hc_p).mul hc_m).aestronglyMeasurable
  set K : ℝ := 2 * (X + H) ^ ((2 : ℝ) + 1) / H + 3
  have hK_nn : 0 ≤ K := by positivity
  have h_lintegral_bound :
      (∑' n : ℕ, ∫⁻ y : ℝ, ‖F n y‖ₑ ∂MeasureTheory.volume) ≠ ⊤ := by
    have h_base : MeasureTheory.Integrable (fun y : ℝ => K * (2 ^ 2 + y ^ 2)⁻¹) :=
      (integrable_inv_sq_add_sq (by norm_num)).const_mul K
    have h_base_lt : ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume < ⊤ :=
      h_base.hasFiniteIntegral
    let a : ℕ → ENNReal := fun n => ENNReal.ofReal (((n : ℝ) ^ (2 : ℝ))⁻¹)
    have h_each : ∀ n : ℕ,
        ∫⁻ y : ℝ, ‖F n y‖ₑ ∂MeasureTheory.volume ≤
          a n * ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume := by
      intro n
      rcases Nat.eq_zero_or_pos n with rfl | hn_pos
      · simp [F, a]
      · have hn0 : n ≠ 0 := hn_pos.ne'
        have hn_pos_r : (0 : ℝ) < n := Nat.cast_pos.mpr hn_pos
        rw [← MeasureTheory.lintegral_const_mul'' _ h_base.aestronglyMeasurable.enorm]
        refine MeasureTheory.lintegral_mono fun y => ?_
        have h_mu : ‖(ArithmeticFunction.moebius n : ℂ)‖ ≤ 1 := by
          simpa [Complex.norm_intCast] using
            (show |(ArithmeticFunction.moebius n : ℝ)| ≤ 1 by
              exact_mod_cast ArithmeticFunction.abs_moebius_le_one (n := n))
        have h_cpow : ‖(n : ℂ) ^ (-(2 + y * Complex.I))‖ = ((n : ℝ) ^ (2 : ℝ))⁻¹ := by
          have hn_c : (n : ℂ) = ((n : ℝ) : ℂ) := by norm_cast
          rw [hn_c, Complex.norm_cpow_eq_rpow_re_of_pos hn_pos_r]
          simp [Real.rpow_neg hn_pos_r.le]
        have h_mbd := norm_mellin_cutoffPhi_le_div_sq hX hH (s := 2 + y * Complex.I) (by norm_num)
        have hre2 : (2 + y * Complex.I).re = 2 := by simp
        rw [hre2] at h_mbd
        have h_norm : ‖F n y‖ ≤ ((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹) := by
          dsimp [F]
          simp only [hn0, ↓reduceIte, norm_mul, h_cpow]
          calc ‖(ArithmeticFunction.moebius n : ℂ)‖ * ((n : ℝ) ^ (2 : ℝ))⁻¹ *
                ‖mellin phi (2 + y * Complex.I)‖
              ≤ 1 * ((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹) := by
                refine mul_le_mul (mul_le_mul_of_nonneg_right h_mu (by positivity)) ?_
                  (norm_nonneg _) (by positivity)
                simpa [K, div_eq_mul_inv] using h_mbd
            _ = ((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹) := by ring
        have h_prod : ENNReal.ofReal (((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹)) =
            a n * ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ := by
          rw [ENNReal.ofReal_mul (by positivity)]
          congr 1
          rw [Real.enorm_eq_ofReal_abs, abs_of_nonneg (mul_nonneg hK_nn (by positivity))]
        have h_en : ‖F n y‖ₑ ≤ ENNReal.ofReal (((n : ℝ) ^ (2 : ℝ))⁻¹ * (K * (2 ^ 2 + y ^ 2)⁻¹)) := by
          rw [← ofReal_norm (F n y)]
          exact ENNReal.ofReal_le_ofReal h_norm
        exact h_en.trans_eq h_prod
    have ha_sum : (∑' n : ℕ, a n) < ⊤ :=
      (Real.summable_nat_rpow_inv.mpr one_lt_two).tsum_ofReal_lt_top
    have h_sum_le : (∑' n : ℕ, ∫⁻ y : ℝ, ‖F n y‖ₑ ∂MeasureTheory.volume) ≤
        (∑' n : ℕ, a n) * ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume := by
      calc (∑' n : ℕ, ∫⁻ y : ℝ, ‖F n y‖ₑ ∂MeasureTheory.volume)
          ≤ ∑' n : ℕ, a n * ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume :=
            ENNReal.tsum_le_tsum h_each
        _ = (∑' n : ℕ, a n) * ∫⁻ y : ℝ, ‖K * (2 ^ 2 + y ^ 2)⁻¹‖ₑ ∂MeasureTheory.volume :=
            ENNReal.tsum_mul_right
    exact (h_sum_le.trans_lt (ENNReal.mul_lt_top ha_sum h_base_lt)).ne
  have h_int_tsum := MeasureTheory.integral_tsum h_aesm h_lintegral_bound
  have h_sum_term :
      (∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * phi n) =
        ((1 / (2 * Real.pi) : ℝ) : ℂ) * ∑' n : ℕ, ∫ y : ℝ, F n y := by
    have h_fun : (fun n : ℕ => (ArithmeticFunction.moebius n : ℂ) * phi n) =
        fun n : ℕ => ((1 / (2 * Real.pi) : ℝ) : ℂ) * ∫ y : ℝ, F n y :=
      funext h_term
    rw [h_fun, tsum_mul_left]
  rw [h_sum_term, ← h_int_tsum]
  congr 1
  refine MeasureTheory.integral_congr_ae (Filter.Eventually.of_forall fun y => ?_)
  have hs2 : 1 < (2 + y * Complex.I).re := by simp
  have hs_ne1 : 2 + y * Complex.I ≠ 1 := by
    intro h
    have := congrArg Complex.re h
    simp at this
  have h_lseries_eq :
      (∑' n : ℕ, if n = 0 then (0 : ℂ) else (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I))) =
        zetaInv (2 + y * Complex.I) := by
    have hmul := LSeries_one_mul_Lseries_moebius hs2
    rw [LSeries_one_eq_riemannZeta hs2] at hmul
    have hL_eq : LSeries (↗ArithmeticFunction.moebius) (2 + y * Complex.I) =
        ∑' n : ℕ, if n = 0 then (0 : ℂ) else (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I)) := by
      simp only [LSeries, LSeries.term]
      congr 1
      ext n
      split_ifs with hn
      · rfl
      · simp only [div_eq_mul_inv, ← Complex.cpow_neg]
    rw [← hL_eq]
    have hinv : LSeries (↗ArithmeticFunction.moebius) (2 + y * Complex.I) =
        (riemannZeta (2 + y * Complex.I))⁻¹ :=
      eq_inv_of_mul_eq_one_right hmul
    simp [zetaInv, hs_ne1, hinv]
  have hF_rw : (fun n : ℕ => F n y) = fun n : ℕ =>
      (if n = 0 then (0 : ℂ) else (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-(2 + y * Complex.I))) *
        mellin phi (2 + y * Complex.I) := by
    ext n
    by_cases hn : n = 0 <;> simp [F, hn]
  dsimp only
  rw [hF_rw, tsum_mul_right, h_lseries_eq]

/-! ### Stage 5: Cauchy Rectangle Contour Shift & Unconditional `RH → MertensBound` -/

/-- Exact value of the improper real power tail integral `∫ t in Ioi c, t ^ p` for `c > 0`, `p < -1`. -/
lemma setIntegral_Ioi_rpow_of_lt {c p : ℝ} (hc : 0 < c) (hp : p < -1) :
    ∫ t : ℝ in Set.Ioi c, t ^ p = c ^ (p + 1) / (-(p + 1)) := by
  have h1 :
      ((∫ t : ℝ in Set.Ioi c, t ^ p : ℝ) : ℂ) =
        ∫ t : ℝ in Set.Ioi c, ((t ^ p : ℝ) : ℂ) :=
    integral_ofReal.symm
  have h2 :
      (∫ t : ℝ in Set.Ioi c, ((t ^ p : ℝ) : ℂ)) =
        ∫ t : ℝ in Set.Ioi c, (t : ℂ) ^ (p : ℂ) := by
    refine MeasureTheory.setIntegral_congr_fun measurableSet_Ioi fun t ht => ?_
    exact Complex.ofReal_cpow (hc.le.trans ht.le) p
  have h3 : (∫ t : ℝ in Set.Ioi c, (t : ℂ) ^ (p : ℂ)) =
      -(c : ℂ) ^ ((p : ℂ) + 1) / ((p : ℂ) + 1) :=
    integral_Ioi_cpow_of_lt (by simpa using hp) hc
  have h4 : -(c : ℂ) ^ ((p : ℂ) + 1) / ((p : ℂ) + 1) = ((c ^ (p + 1) / (-(p + 1)) : ℝ) : ℂ) := by
    have hcp : (c : ℂ) ^ ((p : ℂ) + 1) = ((c ^ (p + 1) : ℝ) : ℂ) := by
      have hre : (p : ℂ) + 1 = ((p + 1 : ℝ) : ℂ) := by push_cast; rfl
      rw [hre, ← Complex.ofReal_cpow hc.le (p + 1)]
    rw [hcp]
    push_cast
    have hp1 : (p : ℂ) + 1 ≠ 0 := by
      intro h
      have := congrArg Complex.re h
      simp at this
      linarith
    field_simp [hp1]
  exact Complex.ofReal_injective (h1.trans (h2.trans (h3.trans h4)))

/-- Integrability of `(1 + |y|) ^ eps / (σ ^ 2 + y ^ 2)` on `ℝ` for `0 < σ` and `0 ≤ eps < 1`. -/
lemma integrable_one_add_abs_rpow_div {σ eps : ℝ} (hσ : 0 < σ) (heps0 : 0 ≤ eps) (heps1 : eps < 1) :
    MeasureTheory.Integrable (fun y : ℝ => (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2)) := by
  let g₁ : ℝ → ℝ := Set.indicator (Set.Icc (-1 : ℝ) 1) (fun _ => (2 : ℝ) ^ eps / σ ^ 2)
  let g₂ : ℝ → ℝ := Set.indicator (Set.Ioi (1 : ℝ)) (fun y => (2 : ℝ) ^ eps * y ^ (eps - 2))
  let g₃ : ℝ → ℝ := fun y => Set.indicator (Set.Ioi (1 : ℝ)) (fun t => (2 : ℝ) ^ eps * t ^ (eps - 2)) (-y)
  have hg₁ : MeasureTheory.Integrable g₁ :=
    (MeasureTheory.integrable_indicator_iff measurableSet_Icc).mpr
      (continuousOn_const.integrableOn_Icc (a := (-1 : ℝ)) (b := 1))
  have hg₂ : MeasureTheory.Integrable g₂ :=
    (MeasureTheory.integrable_indicator_iff measurableSet_Ioi).mpr
      (MeasureTheory.Integrable.const_mul
        (integrableOn_Ioi_rpow_of_lt (by linarith : eps - 2 < -1) zero_lt_one) ((2 : ℝ) ^ eps))
  have hg₃ : MeasureTheory.Integrable g₃ := hg₂.comp_neg
  have hf_meas : MeasureTheory.AEStronglyMeasurable
      (fun y : ℝ => (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2)) MeasureTheory.volume :=
    ((Continuous.rpow (by fun_prop : Continuous fun y : ℝ => 1 + |y|) continuous_const
      (fun y => Or.inl (by linarith [abs_nonneg y]))).div
      (by fun_prop : Continuous fun y : ℝ => σ ^ 2 + y ^ 2)
      (fun y => ne_of_gt (by positivity))).aestronglyMeasurable
  refine ((hg₁.add hg₂).add hg₃).mono' hf_meas (Filter.Eventually.of_forall fun y => ?_)
  have hf_nn : 0 ≤ (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2) := by positivity
  rw [Real.norm_of_nonneg hf_nn]
  have h2_nn : 0 ≤ (2 : ℝ) ^ eps := by positivity
  have hg₁_nn : 0 ≤ g₁ y := by
    by_cases h : y ∈ Set.Icc (-1 : ℝ) 1
    · simp only [g₁, Set.indicator_of_mem h]; positivity
    · simp [g₁, h]
  have hg₂_nn : 0 ≤ g₂ y := by
    by_cases h : 1 < y
    · have hpos : 0 ≤ (2 : ℝ) ^ eps * y ^ (eps - 2) := by positivity
      simpa [g₂, h] using hpos
    · simp [g₂, h]
  have hg₃_nn : 0 ≤ g₃ y := by
    by_cases h : 1 < -y
    · have hpos : 0 ≤ (2 : ℝ) ^ eps * (-y) ^ (eps - 2) := by positivity
      simpa [g₃, h] using hpos
    · simp [g₃, h]
  by_cases hy1 : |y| ≤ 1
  · have h_mem : y ∈ Set.Icc (-1 : ℝ) 1 := abs_le.mp hy1
    have hg₁_val : g₁ y = (2 : ℝ) ^ eps / σ ^ 2 := by simp [g₁, h_mem]
    have h_bd : (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2) ≤ (2 : ℝ) ^ eps / σ ^ 2 := by
      have hnum : (1 + |y|) ^ eps ≤ (2 : ℝ) ^ eps :=
        Real.rpow_le_rpow (by linarith [abs_nonneg y]) (by linarith) heps0
      have hden : σ ^ 2 ≤ σ ^ 2 + y ^ 2 := le_add_of_nonneg_right (sq_nonneg y)
      exact div_le_div₀ (by positivity) hnum (by positivity) hden
    simp only [Pi.add_apply]; linarith
  · have hy_gt : 1 < |y| := lt_of_not_ge hy1
    rcases le_or_gt 0 y with hy0 | hy0
    · have h1y : 1 < y := by rwa [abs_of_nonneg hy0] at hy_gt
      have h1y_le : 1 + |y| ≤ 2 * y := by
        rw [abs_of_nonneg hy0]; linarith
      have hnum : (1 + |y|) ^ eps ≤ (2 : ℝ) ^ eps * y ^ eps := by
        calc (1 + |y|) ^ eps ≤ (2 * y) ^ eps :=
              Real.rpow_le_rpow (by positivity) h1y_le heps0
          _ = (2 : ℝ) ^ eps * y ^ eps := Real.mul_rpow (by norm_num) (by linarith)
      have hden : y ^ 2 ≤ σ ^ 2 + y ^ 2 := le_add_of_nonneg_left (sq_nonneg σ)
      have hrpow_div : y ^ eps / y ^ 2 = y ^ (eps - 2) := by
        rw [← Real.rpow_two y, ← Real.rpow_sub (by linarith : 0 < y)]
      have hg₂_val : g₂ y = (2 : ℝ) ^ eps * y ^ (eps - 2) := by
        simp [g₂, h1y]
      have h_bd : (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2) ≤ g₂ y := by
        rw [hg₂_val, ← hrpow_div, mul_div_assoc']
        exact div_le_div₀ (by positivity) hnum (by positivity) hden
      simp only [Pi.add_apply]; linarith
    · have h1ny : 1 < -y := by rwa [abs_of_neg hy0] at hy_gt
      have h1y_le : 1 + |y| ≤ 2 * (-y) := by
        rw [abs_of_neg hy0]; linarith
      have hnum : (1 + |y|) ^ eps ≤ (2 : ℝ) ^ eps * (-y) ^ eps := by
        calc (1 + |y|) ^ eps ≤ (2 * (-y)) ^ eps :=
              Real.rpow_le_rpow (by positivity) h1y_le heps0
          _ = (2 : ℝ) ^ eps * (-y) ^ eps := Real.mul_rpow (by norm_num) (by linarith)
      have hden : (-y) ^ 2 ≤ σ ^ 2 + y ^ 2 := by
        rw [neg_sq]
        exact le_add_of_nonneg_left (sq_nonneg σ)
      have hrpow_div : (-y) ^ eps / (-y) ^ 2 = (-y) ^ (eps - 2) := by
        rw [← Real.rpow_two (-y), ← Real.rpow_sub (by linarith : 0 < -y)]
      have hg₃_val : g₃ y = (2 : ℝ) ^ eps * (-y) ^ (eps - 2) := by
        simp [g₃, h1ny]
      have h_bd : (1 + |y|) ^ eps / (σ ^ 2 + y ^ 2) ≤ g₃ y := by
        rw [hg₃_val, ← hrpow_div, mul_div_assoc']
        exact div_le_div₀ (by positivity) hnum (by positivity) hden
      simp only [Pi.add_apply]; linarith

/-- Contour shift under `_root_.RiemannHypothesis` from `Re(s) = 2` to any `σ₀ ∈ (1/2, 2)`. -/
theorem mellin_cutoffPhi_two_eq_sigma (h_rh : _root_.RiemannHypothesis)
    {X H σ₀ : ℝ} (hX : 1 ≤ X) (hH : 0 < H) (hσ₀_lo : 1 / 2 < σ₀) (hσ₀_hi : σ₀ < 2) :
    ∫ y : ℝ, zetaInv (2 + y * Complex.I) * mellin (cutoffPhi X H) (2 + y * Complex.I) =
      ∫ y : ℝ, zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I) := by
  let G : ℂ → ℂ := fun s => zetaInv s * mellin (cutoffPhi X H) s
  let eps : ℝ := 1 / 4
  obtain ⟨Cζ, hCζ_pos, hCζ⟩ :=
    inv_zeta_isBigO_im_of_rh h_rh hσ₀_lo (by norm_num : (0 : ℝ) < eps)
  let K : ℝ := 2 * (X + H) ^ (3 : ℝ) / H + 3
  have hK_nn : 0 ≤ K := by positivity
  have hXH_ge1 : 1 ≤ X + H := by linarith
  have hG_bd : ∀ s : ℂ, σ₀ ≤ s.re → s.re ≤ 2 →
      ‖G s‖ ≤ (Cζ * K) * ((1 + |s.im|) ^ eps / (σ₀ ^ 2 + s.im ^ 2)) := by
    intro s hs_lo hs_hi
    have hs_pos : 0 < s.re := by linarith
    have hz := hCζ s hs_lo
    have hm := norm_mellin_cutoffPhi_le_div_sq hX hH hs_pos
    have hpow_XH : (X + H) ^ (s.re + 1) ≤ (X + H) ^ (3 : ℝ) :=
      Real.rpow_le_rpow_of_exponent_le hXH_ge1 (by linarith)
    have hm_K : ‖mellin (cutoffPhi X H) s‖ ≤ K / (σ₀ ^ 2 + s.im ^ 2) := by
      have hnum : 2 * (X + H) ^ (s.re + 1) / H + 3 ≤ K := by
        dsimp [K]
        gcongr
      have hden : σ₀ ^ 2 + s.im ^ 2 ≤ s.re ^ 2 + s.im ^ 2 := by
        have hsq : σ₀ ^ 2 ≤ s.re ^ 2 := sq_le_sq' (by linarith) hs_lo
        linarith
      exact hm.trans (div_le_div₀ hK_nn hnum (by positivity) hden)
    have hg_prod : ‖G s‖ ≤ (Cζ * (1 + |s.im|) ^ eps) * (K / (σ₀ ^ 2 + s.im ^ 2)) := by
      dsimp [G]
      rw [norm_mul]
      exact mul_le_mul hz hm_K (norm_nonneg _) (by positivity)
    calc ‖G s‖ ≤ (Cζ * (1 + |s.im|) ^ eps) * (K / (σ₀ ^ 2 + s.im ^ 2)) := hg_prod
      _ = (Cζ * K) * ((1 + |s.im|) ^ eps / (σ₀ ^ 2 + s.im ^ 2)) := by ring
  have hG_diff : DifferentiableOn ℂ G {s : ℂ | 1 / 2 < s.re} := by
    intro s hs
    simp only [Set.mem_ofPred_eq] at hs
    have hd1 : DifferentiableAt ℂ zetaInv s :=
      (differentiableOn_zetaInv_of_rh h_rh s hs).differentiableAt
        (IsOpen.mem_nhds (isOpen_lt continuous_const Complex.continuous_re) hs)
    have hd2 : DifferentiableAt ℂ (mellin (cutoffPhi X H)) s :=
      (differentiableOn_mellin_cutoffPhi hX hH s (by linarith : (0 : ℝ) < s.re)).differentiableAt
        (IsOpen.mem_nhds (isOpen_lt continuous_const Complex.continuous_re)
          (show (0 : ℝ) < s.re by linarith))
    exact (hd1.mul hd2).differentiableWithinAt
  have h_vert_int : ∀ σ : ℝ, σ₀ ≤ σ → σ ≤ 2 →
      MeasureTheory.Integrable (fun y : ℝ => G (σ + y * Complex.I)) := by
    intro σ hσ_lo hσ_hi
    have hc : Continuous (fun y : ℝ => G (σ + y * Complex.I)) := by
      have hline : Continuous (fun y : ℝ => (σ : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
      exact hG_diff.continuousOn.comp_continuous hline fun y => by simp; linarith
    refine ((integrable_one_add_abs_rpow_div (by linarith : 0 < σ₀) (by norm_num : 0 ≤ eps)
      (by norm_num : eps < 1)).const_mul (Cζ * K)).mono' hc.aestronglyMeasurable
      (Filter.Eventually.of_forall fun y => ?_)
    have hs_re : (σ + y * Complex.I).re = σ := by simp
    have hs_im : (σ + y * Complex.I).im = y := by simp
    simpa [hs_re, hs_im] using hG_bd (σ + y * Complex.I) (by simpa using hσ_lo) (by simpa using hσ_hi)
  have h_int2 : MeasureTheory.Integrable (fun y : ℝ => G (2 + y * Complex.I)) :=
    h_vert_int 2 hσ₀_hi.le le_rfl
  have h_intσ : MeasureTheory.Integrable (fun y : ℝ => G (σ₀ + y * Complex.I)) :=
    h_vert_int σ₀ le_rfl hσ₀_hi.le
  have h_rect : ∀ T : ℝ, 0 ≤ T →
      (∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I)) -
      (∫ x : ℝ in σ₀..2, G (x + T * Complex.I)) +
      Complex.I • (∫ y : ℝ in (-T)..T, G (2 + y * Complex.I)) -
      Complex.I • (∫ y : ℝ in (-T)..T, G (σ₀ + y * Complex.I)) = 0 := by
    intro T _hT
    have h_sub : Set.uIcc σ₀ 2 ×ℂ Set.uIcc (-T) T ⊆ {s : ℂ | 1 / 2 < s.re} := by
      intro s hs
      rcases hs with ⟨hs_re, _⟩
      rw [Set.uIcc_of_le hσ₀_hi.le] at hs_re
      exact hσ₀_lo.trans_le hs_re.1
    have h_cauchy := Complex.integral_boundary_rect_eq_zero_of_differentiableOn G
      (σ₀ + (-T) * Complex.I) (2 + T * Complex.I) (hG_diff.mono (by simpa using h_sub))
    simpa using h_cauchy
  let C_horiz : ℝ := (2 - σ₀) * (Cζ * K) * (2 : ℝ) ^ eps
  have h_top_lim : Filter.Tendsto (fun T : ℝ => ∫ x : ℝ in σ₀..2, G (x + T * Complex.I))
      Filter.atTop (𝓝 0) := by
    have h_bound_lim : Filter.Tendsto (fun T : ℝ => C_horiz * T ^ (eps - 2)) Filter.atTop (𝓝 0) := by
      have ht := tendsto_rpow_neg_atTop (by norm_num : (0 : ℝ) < 2 - eps)
      simpa [mul_zero, show -(2 - eps) = eps - 2 by ring] using ht.const_mul C_horiz
    rw [tendsto_zero_iff_norm_tendsto_zero]
    refine squeeze_zero' (Filter.Eventually.of_forall fun T => norm_nonneg _) ?_ h_bound_lim
    filter_upwards [Filter.eventually_ge_atTop (1 : ℝ)] with T hT
    have h_norm_x : ∀ x ∈ Set.uIoc σ₀ 2, ‖G (x + T * Complex.I)‖ ≤ (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) := by
      intro x hx
      rw [Set.uIoc_of_le hσ₀_hi.le] at hx
      have him : (x + T * Complex.I).im = T := by simp
      have hbd := hG_bd (x + T * Complex.I) (by simpa using hx.1.le) (by simpa using hx.2)
      rw [him, abs_of_pos (by linarith)] at hbd
      have h1T : (1 + T) ^ eps ≤ (2 * T) ^ eps :=
        Real.rpow_le_rpow (by linarith) (by linarith) (by norm_num)
      have h2T : (2 * T) ^ eps = (2 : ℝ) ^ eps * T ^ eps :=
        Real.mul_rpow (by norm_num) (by linarith)
      have hden : T ^ 2 ≤ σ₀ ^ 2 + T ^ 2 := le_add_of_nonneg_left (sq_nonneg _)
      have hpow : T ^ eps / T ^ 2 = T ^ (eps - 2) := by
        rw [← Real.rpow_two T, ← Real.rpow_sub (by linarith)]
      calc ‖G (x + T * Complex.I)‖
          ≤ (Cζ * K) * ((1 + T) ^ eps / (σ₀ ^ 2 + T ^ 2)) := hbd
        _ ≤ (Cζ * K) * (((2 : ℝ) ^ eps * T ^ eps) / T ^ 2) := by
            gcongr; linarith [h1T, h2T]
        _ = (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) := by
            rw [mul_div_assoc, hpow]; ring
    have hi := intervalIntegral.norm_integral_le_of_norm_le_const h_norm_x
    rw [abs_of_nonneg (by linarith)] at hi
    calc ‖∫ x : ℝ in σ₀..2, G (x + T * Complex.I)‖
        ≤ (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) * (2 - σ₀) := hi
      _ = C_horiz * T ^ (eps - 2) := by dsimp [C_horiz]; ring
  have h_bot_lim : Filter.Tendsto (fun T : ℝ => ∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I))
      Filter.atTop (𝓝 0) := by
    have h_bound_lim : Filter.Tendsto (fun T : ℝ => C_horiz * T ^ (eps - 2)) Filter.atTop (𝓝 0) := by
      have ht := tendsto_rpow_neg_atTop (by norm_num : (0 : ℝ) < 2 - eps)
      simpa [mul_zero, show -(2 - eps) = eps - 2 by ring] using ht.const_mul C_horiz
    rw [tendsto_zero_iff_norm_tendsto_zero]
    refine squeeze_zero' (Filter.Eventually.of_forall fun T => norm_nonneg _) ?_ h_bound_lim
    filter_upwards [Filter.eventually_ge_atTop (1 : ℝ)] with T hT
    have h_norm_x : ∀ x ∈ Set.uIoc σ₀ 2, ‖G (x + (-T) * Complex.I)‖ ≤ (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) := by
      intro x hx
      rw [Set.uIoc_of_le hσ₀_hi.le] at hx
      have him : (x + (-T) * Complex.I).im = -T := by simp
      have hbd := hG_bd (x + (-T) * Complex.I) (by simpa using hx.1.le) (by simpa using hx.2)
      rw [him, abs_neg, abs_of_pos (by linarith), neg_sq] at hbd
      have h1T : (1 + T) ^ eps ≤ (2 * T) ^ eps :=
        Real.rpow_le_rpow (by linarith) (by linarith) (by norm_num)
      have h2T : (2 * T) ^ eps = (2 : ℝ) ^ eps * T ^ eps :=
        Real.mul_rpow (by norm_num) (by linarith)
      have hden : T ^ 2 ≤ σ₀ ^ 2 + T ^ 2 := le_add_of_nonneg_left (sq_nonneg _)
      have hpow : T ^ eps / T ^ 2 = T ^ (eps - 2) := by
        rw [← Real.rpow_two T, ← Real.rpow_sub (by linarith)]
      calc ‖G (x + (-T) * Complex.I)‖
          ≤ (Cζ * K) * ((1 + T) ^ eps / (σ₀ ^ 2 + T ^ 2)) := hbd
        _ ≤ (Cζ * K) * (((2 : ℝ) ^ eps * T ^ eps) / T ^ 2) := by
            gcongr; linarith [h1T, h2T]
        _ = (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) := by
            rw [mul_div_assoc, hpow]; ring
    have hi := intervalIntegral.norm_integral_le_of_norm_le_const h_norm_x
    rw [abs_of_nonneg (by linarith)] at hi
    calc ‖∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I)‖
        ≤ (Cζ * K) * (2 : ℝ) ^ eps * T ^ (eps - 2) * (2 - σ₀) := hi
      _ = C_horiz * T ^ (eps - 2) := by dsimp [C_horiz]; ring
  have h_vright_lim :
      Filter.Tendsto (fun T : ℝ => ∫ y : ℝ in (-T)..T, G (2 + y * Complex.I))
        Filter.atTop (𝓝 (∫ y : ℝ, G (2 + y * Complex.I))) :=
    MeasureTheory.intervalIntegral_tendsto_integral h_int2 Filter.tendsto_neg_atTop_atBot Filter.tendsto_id
  have h_vleft_lim :
      Filter.Tendsto (fun T : ℝ => ∫ y : ℝ in (-T)..T, G (σ₀ + y * Complex.I))
        Filter.atTop (𝓝 (∫ y : ℝ, G (σ₀ + y * Complex.I))) :=
    MeasureTheory.intervalIntegral_tendsto_integral h_intσ Filter.tendsto_neg_atTop_atBot Filter.tendsto_id
  have h_comb_lim :
      Filter.Tendsto
        (fun T : ℝ =>
          (∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I)) -
          (∫ x : ℝ in σ₀..2, G (x + T * Complex.I)) +
          Complex.I • (∫ y : ℝ in (-T)..T, G (2 + y * Complex.I)) -
          Complex.I • (∫ y : ℝ in (-T)..T, G (σ₀ + y * Complex.I)))
        Filter.atTop
        (𝓝 (0 - 0 + Complex.I • (∫ y : ℝ, G (2 + y * Complex.I)) -
          Complex.I • (∫ y : ℝ, G (σ₀ + y * Complex.I)))) :=
    (((h_bot_lim.sub h_top_lim).add (h_vright_lim.const_smul Complex.I)).sub
      (h_vleft_lim.const_smul Complex.I))
  have h_zero_lim :
      Filter.Tendsto
        (fun T : ℝ =>
          (∫ x : ℝ in σ₀..2, G (x + (-T) * Complex.I)) -
          (∫ x : ℝ in σ₀..2, G (x + T * Complex.I)) +
          Complex.I • (∫ y : ℝ in (-T)..T, G (2 + y * Complex.I)) -
          Complex.I • (∫ y : ℝ in (-T)..T, G (σ₀ + y * Complex.I)))
        Filter.atTop (𝓝 0) :=
    tendsto_const_nhds.congr' (by
      filter_upwards [Filter.eventually_ge_atTop (0 : ℝ)] with T hT
      exact (h_rect T hT).symm)
  have h_eq0 := tendsto_nhds_unique h_comb_lim h_zero_lim
  simp only [sub_zero, zero_add, smul_eq_mul] at h_eq0
  have h_mul_eq : Complex.I * (∫ y : ℝ, G (2 + y * Complex.I)) =
      Complex.I * (∫ y : ℝ, G (σ₀ + y * Complex.I)) := sub_eq_zero.mp h_eq0
  exact mul_left_cancel₀ Complex.I_ne_zero h_mul_eq

/-- Littlewood (1912) converse: `_root_.RiemannHypothesis` implies `MertensBound`
unconditionally via Perron/Mellin–Mertens contour shift to `Re(s) = 1/2 + ε/4`. -/
theorem rh_implies_mertens_bound : _root_.RiemannHypothesis → RiemannBlueprint.MertensBound := by
  intro h_rh ε hε
  set δ₀ : ℝ := min (ε / 4) (1 / 4)
  have hδ_pos : 0 < δ₀ := lt_min (by linarith) (by norm_num)
  have hδ_le_quarter : δ₀ ≤ 1 / 4 := min_le_right _ _
  have h4δ_le : 4 * δ₀ ≤ ε := by linarith [min_le_left (ε / 4) (1 / 4)]
  set σ₀ : ℝ := 1 / 2 + δ₀
  have hσ₀_lo : 1 / 2 < σ₀ := by dsimp [σ₀]; linarith
  have hσ₀_hi : σ₀ < 2 := by dsimp [σ₀]; linarith
  have hσ₀_le1 : σ₀ ≤ 1 := by dsimp [σ₀]; linarith
  obtain ⟨Cζ, hCζ_pos, hCζ⟩ := inv_zeta_isBigO_im_of_rh h_rh hσ₀_lo hδ_pos
  have hlog_bd : ∀ y : ℝ, 1 ≤ y → Real.log y ≤ y ^ δ₀ / δ₀ := by
    intro y hy
    have hyδ : 0 < y ^ δ₀ := Real.rpow_pos_of_pos (by linarith) δ₀
    have h1 := Real.log_le_sub_one_of_pos hyδ
    rw [Real.log_rpow (by linarith)] at h1
    have h2 : δ₀ * Real.log y ≤ y ^ δ₀ := by linarith
    exact (le_div_iff₀ hδ_pos).2 (by linarith)
  set C_mid_const : ℝ :=
    (1 / (2 * Real.pi)) * (4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * (2 * σ₀⁻¹ + 2 * δ₀⁻¹))
  set C_tail_const : ℝ :=
    (1 / (2 * Real.pi)) * (2 * Cζ * (2 : ℝ) ^ δ₀ * (2 * (2 : ℝ) ^ (σ₀ + 1) + 3) / (1 - δ₀))
  set C_final : ℝ := 3 + C_mid_const + C_tail_const
  have h1_sub_δ : 0 < 1 - δ₀ := by linarith
  have hC_mid_nn : 0 ≤ C_mid_const := by dsimp [C_mid_const]; positivity
  have hC_tail_nn : 0 ≤ C_tail_const := by
    dsimp [C_tail_const]
    exact mul_nonneg (by positivity) (div_nonneg (by positivity) h1_sub_δ.le)
  have hC_final_pos : 0 < C_final := by dsimp [C_final]; linarith
  refine ⟨C_final, hC_final_pos, fun X hX => ?_⟩
  set H : ℝ := Real.sqrt X
  have hH_ge1 : 1 ≤ H := Real.one_le_sqrt.mpr hX
  have hH_pos : 0 < H := by linarith
  have hXH_le : X + H ≤ 2 * X := by
    have hsqrt_le : H ≤ X := by
      calc H = Real.sqrt X := rfl
        _ ≤ Real.sqrt (X * X) := Real.sqrt_le_sqrt (le_mul_of_one_le_right (by linarith) hX)
        _ = X := Real.sqrt_mul_self (by linarith)
    linarith
  have hXH_pos : 0 < X + H := by linarith
  have hXH_ge1 : 1 ≤ X + H := by linarith
  have h_diff := tsum_moebius_mul_cutoffPhi_sub_mertens_norm_le hX hH_pos
  have h_inv2 := sum_moebius_cutoffPhi_eq_mellinInv_two hX hH_pos
  have h_shift := mellin_cutoffPhi_two_eq_sigma h_rh hX hH_pos hσ₀_lo hσ₀_hi
  set S_shifted : ℂ :=
    ∫ y : ℝ, zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)
  have h_mert_bd :
      |(RiemannBlueprint.mertens X : ℝ)| ≤ (H + 1) + (1 / (2 * Real.pi)) * ‖S_shifted‖ := by
    have h_cast_abs : |(RiemannBlueprint.mertens X : ℝ)| = ‖(RiemannBlueprint.mertens X : ℂ)‖ := by
      simp [Complex.norm_intCast]
    rw [h_cast_abs]
    have h_tri : ‖(RiemannBlueprint.mertens X : ℂ)‖ ≤
        ‖(RiemannBlueprint.mertens X : ℂ) - ∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ +
        ‖∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ := by
      calc ‖(RiemannBlueprint.mertens X : ℂ)‖
          = ‖((RiemannBlueprint.mertens X : ℂ) - ∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n) +
              ∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ := by ring_nf
        _ ≤ _ := norm_add_le _ _
    have h_diff' :
        ‖(RiemannBlueprint.mertens X : ℂ) - ∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ ≤
          H + 1 := by
      simpa [norm_sub_rev] using h_diff
    have h_sum_norm :
        ‖∑' n : ℕ, (ArithmeticFunction.moebius n : ℂ) * cutoffPhi X H n‖ =
          (1 / (2 * Real.pi)) * ‖S_shifted‖ := by
      rw [h_inv2, h_shift, norm_mul, Complex.norm_real, Real.norm_eq_abs,
        abs_of_pos (by positivity)]
    linarith
  -- Bound ‖S_shifted‖ ≤ ∫ y, ‖G (σ₀ + y * I)‖ via middle |y| ≤ H and tails |y| > H
  let K : ℝ := 2 * (X + H) ^ (σ₀ + 1) / H + 3
  let M_mid : ℝ := 4 * Cζ * (X + H) ^ σ₀ * (1 + H) ^ δ₀
  let M_tail : ℝ := Cζ * K * (2 : ℝ) ^ δ₀
  let dom_rec : ℝ → ℝ := fun y => if |y| < 1 then σ₀⁻¹ else |y|⁻¹
  let B : ℝ → ℝ := fun y =>
    Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y +
    Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y +
    Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y)
  have h_dom_intOn : MeasureTheory.IntegrableOn dom_rec (Set.Icc (-H) H) := by
    have h_dom_meas : Measurable dom_rec :=
      Measurable.ite (measurableSet_lt continuous_abs.measurable measurable_const)
        measurable_const continuous_abs.measurable.inv
    have h_mem_bd : ∀ y : ℝ, ‖dom_rec y‖ ≤ σ₀⁻¹ := by
      intro y
      have hdr : 0 ≤ dom_rec y := by
        dsimp [dom_rec]; split_ifs <;> positivity
      have hdr_le : dom_rec y ≤ σ₀⁻¹ := by
        dsimp [dom_rec]
        split_ifs with hy
        · exact le_rfl
        · have hy1 : 1 ≤ |y| := le_of_not_gt hy
          exact (inv_le_inv₀ (by linarith [hσ₀_le1]) (by linarith)).mpr (by linarith [hσ₀_le1])
      rwa [Real.norm_of_nonneg hdr]
    exact MeasureTheory.IntegrableOn.of_bound measure_Icc_lt_top
      h_dom_meas.aestronglyMeasurable σ₀⁻¹
      (Filter.Eventually.of_forall h_mem_bd)
  have hB1_int : MeasureTheory.Integrable
      (Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y)) :=
    (MeasureTheory.integrable_indicator_iff measurableSet_Icc).mpr
      (h_dom_intOn.const_mul M_mid)
  have hB2_int : MeasureTheory.Integrable
      (Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2))) :=
    (MeasureTheory.integrable_indicator_iff measurableSet_Ioi).mpr
      (MeasureTheory.Integrable.const_mul
        (integrableOn_Ioi_rpow_of_lt (by linarith : δ₀ - 2 < -1) hH_pos) M_tail)
  have hB3_int : MeasureTheory.Integrable
      (fun y => Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y)) :=
    hB2_int.comp_neg
  have h_S_norm_le : ‖S_shifted‖ ≤ ∫ y : ℝ, B y := by
    have h_norm_int :
        ‖S_shifted‖ ≤
          ∫ y : ℝ, ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ :=
      MeasureTheory.norm_integral_le_integral_norm _
    have h_ptwise : ∀ y : ℝ,
        ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ ≤ B y := by
      intro y
      have hre : (σ₀ + y * Complex.I).re = σ₀ := by simp
      have him : (σ₀ + y * Complex.I).im = y := by simp
      have hz := hCζ (σ₀ + y * Complex.I) (by simp)
      rw [him] at hz
      have hK_nn : 0 ≤ K := by dsimp [K]; positivity
      have hM_tail_nn : 0 ≤ M_tail := by dsimp [M_tail]; positivity
      have hb_nn1 : 0 ≤ Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y := by
        by_cases h : y ∈ Set.Icc (-H) H
        · rw [Set.indicator_of_mem h]
          dsimp [dom_rec]; split_ifs <;> positivity
        · simp [h]
      have hb_nn2 : 0 ≤ Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y := by
        by_cases h : H < y
        · have hy_nn : 0 ≤ y := by linarith
          have : 0 ≤ M_tail * y ^ (δ₀ - 2) := mul_nonneg hM_tail_nn (by positivity)
          simpa [h] using this
        · simp [h]
      have hb_nn3 : 0 ≤ Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y) := by
        by_cases h : H < -y
        · have hny_nn : 0 ≤ -y := by linarith
          have : 0 ≤ M_tail * (-y) ^ (δ₀ - 2) := mul_nonneg hM_tail_nn (by positivity)
          simpa [h] using this
        · simp [h]
      by_cases hyH : |y| ≤ H
      · have h_mem : y ∈ Set.Icc (-H) H := abs_le.mp hyH
        have hm := norm_mellin_cutoffPhi_le_div_norm hX hH_pos (s := σ₀ + y * Complex.I) (by simp; linarith)
        rw [hre] at hm
        have h1y : (1 + |y|) ^ δ₀ ≤ (1 + H) ^ δ₀ :=
          Real.rpow_le_rpow (by positivity) (by linarith) hδ_pos.le
        have h_inv_s : (‖σ₀ + y * Complex.I‖)⁻¹ ≤ dom_rec y := by
          have hs_re_le : σ₀ ≤ ‖σ₀ + y * Complex.I‖ := by
            simpa [hre] using Complex.re_le_norm (σ₀ + y * Complex.I)
          have hs_norm_pos : 0 < ‖σ₀ + y * Complex.I‖ := by linarith
          have hs_im_le : |y| ≤ ‖σ₀ + y * Complex.I‖ := by
            simpa [him] using Complex.abs_im_le_norm (σ₀ + y * Complex.I)
          dsimp [dom_rec]
          split_ifs with hy1
          · exact (inv_le_inv₀ hs_norm_pos (by linarith)).mpr hs_re_le
          · have hy1' : 1 ≤ |y| := le_of_not_gt hy1
            exact (inv_le_inv₀ hs_norm_pos (by linarith)).mpr hs_im_le
        have h_mid :
            ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ ≤
              M_mid * dom_rec y := by
          rw [norm_mul]
          calc ‖zetaInv (σ₀ + y * Complex.I)‖ * ‖mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖
              ≤ (Cζ * (1 + |y|) ^ δ₀) * (4 * (X + H) ^ σ₀ / ‖σ₀ + y * Complex.I‖) :=
                mul_le_mul hz hm (norm_nonneg _) (by positivity)
            _ ≤ (Cζ * (1 + H) ^ δ₀) * (4 * (X + H) ^ σ₀ * dom_rec y) := by
                refine mul_le_mul (mul_le_mul_of_nonneg_left h1y hCζ_pos.le) ?_ (by positivity) (by positivity)
                rw [div_eq_mul_inv]
                exact mul_le_mul_of_nonneg_left h_inv_s (by positivity)
            _ = M_mid * dom_rec y := by dsimp [M_mid]; ring
        have hB_mem : Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y = M_mid * dom_rec y :=
          Set.indicator_of_mem h_mem _
        dsimp [B]
        linarith
      · have hy_gt : H < |y| := lt_of_not_ge hyH
        have hm := norm_mellin_cutoffPhi_le_div_sq hX hH_pos (s := σ₀ + y * Complex.I) (by simp; linarith)
        rw [hre, him] at hm
        rcases le_or_gt 0 y with hy0 | hy0
        · have hy_pos_H : H < y := by rwa [abs_of_nonneg hy0] at hy_gt
          have h1y_le : 1 + |y| ≤ 2 * y := by rw [abs_of_nonneg hy0]; linarith
          have hnum : (1 + |y|) ^ δ₀ ≤ (2 : ℝ) ^ δ₀ * y ^ δ₀ := by
            calc (1 + |y|) ^ δ₀ ≤ (2 * y) ^ δ₀ := Real.rpow_le_rpow (by positivity) h1y_le hδ_pos.le
              _ = (2 : ℝ) ^ δ₀ * y ^ δ₀ := Real.mul_rpow (by norm_num) (by linarith)
          have hden : y ^ 2 ≤ σ₀ ^ 2 + y ^ 2 := le_add_of_nonneg_left (sq_nonneg _)
          have hrpow_div : y ^ δ₀ / y ^ 2 = y ^ (δ₀ - 2) := by
            rw [← Real.rpow_two y, ← Real.rpow_sub (by linarith)]
          have h_bd : ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ ≤
              M_tail * y ^ (δ₀ - 2) := by
            rw [norm_mul]
            calc ‖zetaInv (σ₀ + y * Complex.I)‖ * ‖mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖
                ≤ (Cζ * (1 + |y|) ^ δ₀) * (K / (σ₀ ^ 2 + y ^ 2)) :=
                  mul_le_mul hz hm (norm_nonneg _) (by positivity)
              _ ≤ (Cζ * ((2 : ℝ) ^ δ₀ * y ^ δ₀)) * (K / y ^ 2) := by
                  refine mul_le_mul (mul_le_mul_of_nonneg_left hnum hCζ_pos.le)
                    (div_le_div_of_nonneg_left hK_nn (sq_pos_of_pos (by linarith : 0 < y)) hden)
                    (div_nonneg hK_nn (by positivity)) (by positivity)
              _ = M_tail * (y ^ δ₀ / y ^ 2) := by dsimp [M_tail]; ring
              _ = M_tail * y ^ (δ₀ - 2) := by rw [hrpow_div]
          have hB_mem : Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y = M_tail * y ^ (δ₀ - 2) :=
            Set.indicator_of_mem hy_pos_H _
          dsimp [B]
          linarith
        · have hy_neg_H : H < -y := by rwa [abs_of_neg hy0] at hy_gt
          have hny_pos : 0 < -y := by linarith
          have h1y_le : 1 + |y| ≤ 2 * (-y) := by rw [abs_of_neg hy0]; linarith
          have hnum : (1 + |y|) ^ δ₀ ≤ (2 : ℝ) ^ δ₀ * (-y) ^ δ₀ := by
            calc (1 + |y|) ^ δ₀ ≤ (2 * (-y)) ^ δ₀ := Real.rpow_le_rpow (by positivity) h1y_le hδ_pos.le
              _ = (2 : ℝ) ^ δ₀ * (-y) ^ δ₀ := Real.mul_rpow (by norm_num) (by linarith)
          have hden : (-y) ^ 2 ≤ σ₀ ^ 2 + y ^ 2 := by
            rw [neg_sq]; exact le_add_of_nonneg_left (sq_nonneg _)
          have hrpow_div : (-y) ^ δ₀ / (-y) ^ 2 = (-y) ^ (δ₀ - 2) := by
            rw [← Real.rpow_two (-y), ← Real.rpow_sub (by linarith)]
          have h_bd : ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖ ≤
              M_tail * (-y) ^ (δ₀ - 2) := by
            rw [norm_mul]
            calc ‖zetaInv (σ₀ + y * Complex.I)‖ * ‖mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖
                ≤ (Cζ * (1 + |y|) ^ δ₀) * (K / (σ₀ ^ 2 + y ^ 2)) :=
                  mul_le_mul hz hm (norm_nonneg _) (by positivity)
              _ ≤ (Cζ * ((2 : ℝ) ^ δ₀ * (-y) ^ δ₀)) * (K / (-y) ^ 2) := by
                  refine mul_le_mul (mul_le_mul_of_nonneg_left hnum hCζ_pos.le)
                    (div_le_div_of_nonneg_left hK_nn (sq_pos_of_pos hny_pos) hden)
                    (div_nonneg hK_nn (by positivity)) (by positivity)
              _ = M_tail * ((-y) ^ δ₀ / (-y) ^ 2) := by dsimp [M_tail]; ring
              _ = M_tail * (-y) ^ (δ₀ - 2) := by rw [hrpow_div]
          have hB_mem : Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y) = M_tail * (-y) ^ (δ₀ - 2) :=
            Set.indicator_of_mem hy_neg_H _
          dsimp [B]
          linarith
    have hG_int_norm : MeasureTheory.Integrable
        (fun y : ℝ => ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖) := by
      have hG_cont : Continuous
          (fun y : ℝ => ‖zetaInv (σ₀ + y * Complex.I) * mellin (cutoffPhi X H) (σ₀ + y * Complex.I)‖) := by
        refine Continuous.norm (Continuous.mul ?_ ?_)
        · have hc : Continuous (fun y : ℝ => (σ₀ : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
          exact (differentiableOn_zetaInv_of_rh h_rh).continuousOn.comp_continuous hc fun y => by simp; linarith
        · have hc : Continuous (fun y : ℝ => (σ₀ : ℂ) + (y : ℂ) * Complex.I) := by fun_prop
          exact (differentiableOn_mellin_cutoffPhi hX hH_pos).continuousOn.comp_continuous hc fun y => by simp; linarith
      refine (hB1_int.add hB2_int |>.add hB3_int).mono' hG_cont.aestronglyMeasurable
        (Filter.Eventually.of_forall fun y => ?_)
      rw [Real.norm_of_nonneg (norm_nonneg _)]
      exact h_ptwise y
    have h_int_mono := MeasureTheory.integral_mono hG_int_norm ((hB1_int.add hB2_int).add hB3_int) h_ptwise
    exact h_norm_int.trans h_int_mono
  -- Evaluate the three pieces of ∫ B y
  have hB1_eval :
      ∫ y : ℝ, Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y ≤
        M_mid * (2 * σ₀⁻¹ + 2 * Real.log H) := by
    rw [MeasureTheory.integral_indicator measurableSet_Icc,
      MeasureTheory.setIntegral_congr_set MeasureTheory.Ioc_ae_eq_Icc.symm,
      ← intervalIntegral.integral_of_le (by linarith : -H ≤ H),
      intervalIntegral.integral_const_mul]
    refine mul_le_mul_of_nonneg_left ?_ (by positivity)
    have hI_neg : IntervalIntegrable dom_rec MeasureTheory.volume (-H) (-1) :=
      (intervalIntegrable_iff_integrableOn_Ioc_of_le (by linarith)).mpr
        (h_dom_intOn.mono_set (Set.Ioc_subset_Icc_self.trans
          (Set.Icc_subset_Icc le_rfl (by linarith))))
    have hI_mid : IntervalIntegrable dom_rec MeasureTheory.volume (-1) 1 :=
      (intervalIntegrable_iff_integrableOn_Ioc_of_le (by norm_num)).mpr
        (h_dom_intOn.mono_set (Set.Ioc_subset_Icc_self.trans
          (Set.Icc_subset_Icc (by linarith) hH_ge1)))
    have hI_pos : IntervalIntegrable dom_rec MeasureTheory.volume 1 H :=
      (intervalIntegrable_iff_integrableOn_Ioc_of_le hH_ge1).mpr
        (h_dom_intOn.mono_set (Set.Ioc_subset_Icc_self.trans
          (Set.Icc_subset_Icc (by linarith) le_rfl)))
    have h_split :
        (∫ y : ℝ in (-H)..H, dom_rec y) =
          (∫ y : ℝ in (-H)..(-1), dom_rec y) + (∫ y : ℝ in (-1)..1, dom_rec y) +
            (∫ y : ℝ in 1..H, dom_rec y) := by
      have h12 : (∫ y : ℝ in (-H)..1, dom_rec y) =
          (∫ y : ℝ in (-H)..(-1), dom_rec y) + (∫ y : ℝ in (-1)..1, dom_rec y) :=
        (intervalIntegral.integral_add_adjacent_intervals hI_neg hI_mid).symm
      rw [← intervalIntegral.integral_add_adjacent_intervals (hI_neg.trans hI_mid) hI_pos, h12]
    have h_neg_val : (∫ y : ℝ in (-H)..(-1), dom_rec y) = Real.log H := by
      have h_eq : Set.EqOn dom_rec (fun y : ℝ => -(y⁻¹)) (Set.uIcc (-H) (-1)) := by
        intro y hy
        rw [Set.uIcc_of_le (by linarith : -H ≤ -1)] at hy
        have hy_neg : y < 0 := by linarith [hy.2]
        dsimp [dom_rec]
        split_ifs with h
        · exfalso; rw [abs_of_neg hy_neg] at h; linarith [hy.2]
        · simp [abs_of_neg hy_neg]
      rw [intervalIntegral.integral_congr h_eq, intervalIntegral.integral_neg,
        integral_inv_of_neg (by linarith) (by norm_num)]
      have hdiv : (-1 : ℝ) / (-H) = H⁻¹ := by field_simp
      rw [hdiv, Real.log_inv, neg_neg]
    have h_mid_val : (∫ y : ℝ in (-1)..1, dom_rec y) ≤ 2 * σ₀⁻¹ := by
      have h_le : ∀ y ∈ Set.Icc (-1 : ℝ) 1, dom_rec y ≤ σ₀⁻¹ := by
        intro y _
        dsimp [dom_rec]
        split_ifs with hy
        · exact le_rfl
        · exact (inv_le_inv₀ (by linarith [hσ₀_le1]) (by linarith [le_of_not_gt hy])).mpr
            (by linarith [le_of_not_gt hy, hσ₀_le1])
      calc (∫ y : ℝ in (-1)..1, dom_rec y)
          ≤ ∫ _y : ℝ in (-1 : ℝ)..1, σ₀⁻¹ :=
            intervalIntegral.integral_mono_on (by norm_num) hI_mid intervalIntegrable_const h_le
        _ = 2 * σ₀⁻¹ := by
            rw [intervalIntegral.integral_const, smul_eq_mul]; ring
    have h_pos_val : (∫ y : ℝ in 1..H, dom_rec y) = Real.log H := by
      have h_eq : Set.EqOn dom_rec (fun y : ℝ => y⁻¹) (Set.uIcc 1 H) := by
        intro y hy
        rw [Set.uIcc_of_le hH_ge1] at hy
        have hy_pos : 0 < y := by linarith [hy.1]
        dsimp [dom_rec]
        split_ifs with h
        · exfalso; rw [abs_of_pos hy_pos] at h; linarith [hy.1]
        · rw [abs_of_pos hy_pos]
      rw [intervalIntegral.integral_congr h_eq, integral_inv_of_pos zero_lt_one hH_pos, div_one]
    linarith [h_split, h_neg_val, h_mid_val, h_pos_val]
  have hB2_eval :
      ∫ y : ℝ, Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y =
        M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)) := by
    rw [MeasureTheory.integral_indicator measurableSet_Ioi,
      MeasureTheory.integral_const_mul,
      setIntegral_Ioi_rpow_of_lt hH_pos (by linarith)]
    ring_nf
  have hB3_eval :
      (∫ y : ℝ, Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y)) =
        M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)) := by
    rw [MeasureTheory.integral_neg_eq_self (fun y => Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) y)]
    exact hB2_eval
  have hB_sum_eval : ∫ y : ℝ, B y =
      (∫ y : ℝ, Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y) +
      (∫ y : ℝ, Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y) +
      (∫ y : ℝ, Set.indicator (Set.Ioi H) (fun t => M_tail * t ^ (δ₀ - 2)) (-y)) := by
    dsimp [B]
    have hB12_int : MeasureTheory.Integrable
        (fun y : ℝ => Set.indicator (Set.Icc (-H) H) (fun y => M_mid * dom_rec y) y +
          Set.indicator (Set.Ioi H) (fun y => M_tail * y ^ (δ₀ - 2)) y) :=
      hB1_int.add hB2_int
    rw [MeasureTheory.integral_add hB12_int hB3_int,
      MeasureTheory.integral_add hB1_int hB2_int]
  have h_inv_norm : (1 / (2 * Real.pi)) * ‖S_shifted‖ ≤
      (C_mid_const + C_tail_const) * X ^ ((1 / 2 : ℝ) + ε) := by
    have hX_pos : 0 < X := by linarith
    have hH_rpow : H = X ^ ((1 / 2 : ℝ)) := by simp [H, Real.sqrt_eq_rpow]
    have hHδ_rpow : H ^ δ₀ = X ^ (δ₀ / 2) := by
      rw [hH_rpow, ← Real.rpow_mul hX_pos.le]; ring_nf
    have h_mid_bd :
        (1 / (2 * Real.pi)) * (M_mid * (2 * σ₀⁻¹ + 2 * Real.log H)) ≤
          C_mid_const * X ^ ((1 / 2 : ℝ) + ε) := by
      have h1H_le : 1 + H ≤ 2 * H := by linarith
      have h1H_pow : (1 + H) ^ δ₀ ≤ (2 : ℝ) ^ δ₀ * X ^ (δ₀ / 2) := by
        calc (1 + H) ^ δ₀ ≤ (2 * H) ^ δ₀ := Real.rpow_le_rpow (by positivity) h1H_le hδ_pos.le
          _ = (2 : ℝ) ^ δ₀ * H ^ δ₀ := Real.mul_rpow (by norm_num) hH_pos.le
          _ = (2 : ℝ) ^ δ₀ * X ^ (δ₀ / 2) := by rw [hHδ_rpow]
      have hXH_pow : (X + H) ^ σ₀ ≤ (2 : ℝ) ^ σ₀ * X ^ σ₀ := by
        calc (X + H) ^ σ₀ ≤ (2 * X) ^ σ₀ := Real.rpow_le_rpow (by positivity) hXH_le (by linarith)
          _ = (2 : ℝ) ^ σ₀ * X ^ σ₀ := Real.mul_rpow (by norm_num) hX_pos.le
      have hM_mid_bd : M_mid ≤ 4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * X ^ (σ₀ + δ₀ / 2) := by
        have hx_mul : X ^ σ₀ * X ^ (δ₀ / 2) = X ^ (σ₀ + δ₀ / 2) :=
          (Real.rpow_add hX_pos _ _).symm
        calc M_mid = 4 * Cζ * (X + H) ^ σ₀ * (1 + H) ^ δ₀ := rfl
          _ ≤ 4 * Cζ * ((2 : ℝ) ^ σ₀ * X ^ σ₀) * ((2 : ℝ) ^ δ₀ * X ^ (δ₀ / 2)) := by
              refine mul_le_mul (mul_le_mul_of_nonneg_left hXH_pow (by positivity)) h1H_pow
                (by positivity) (by positivity)
          _ = 4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * (X ^ σ₀ * X ^ (δ₀ / 2)) := by ring
          _ = 4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * X ^ (σ₀ + δ₀ / 2) := by rw [hx_mul]
      have hlog_H : 2 * σ₀⁻¹ + 2 * Real.log H ≤ (2 * σ₀⁻¹ + 2 * δ₀⁻¹) * X ^ (δ₀ / 2) := by
        have hHδ_ge1 : 1 ≤ H ^ δ₀ := Real.one_le_rpow hH_ge1 hδ_pos.le
        have hl := hlog_bd H hH_ge1
        rw [hHδ_rpow] at hl hHδ_ge1
        have h_term1 : 2 * σ₀⁻¹ ≤ 2 * σ₀⁻¹ * X ^ (δ₀ / 2) :=
          le_mul_of_one_le_right (by positivity) hHδ_ge1
        calc 2 * σ₀⁻¹ + 2 * Real.log H
            ≤ 2 * σ₀⁻¹ * X ^ (δ₀ / 2) + 2 * (X ^ (δ₀ / 2) / δ₀) := by linarith
          _ = (2 * σ₀⁻¹ + 2 * δ₀⁻¹) * X ^ (δ₀ / 2) := by ring
      have hx_exp : X ^ (σ₀ + δ₀ / 2) * X ^ (δ₀ / 2) = X ^ (σ₀ + δ₀) := by
        rw [← Real.rpow_add hX_pos]; ring_nf
      have hx_le : X ^ (σ₀ + δ₀) ≤ X ^ ((1 / 2 : ℝ) + ε) :=
        Real.rpow_le_rpow_of_exponent_le hX (by dsimp [σ₀]; linarith)
      have hlogH_nn : 0 ≤ Real.log H := Real.log_nonneg hH_ge1
      calc (1 / (2 * Real.pi)) * (M_mid * (2 * σ₀⁻¹ + 2 * Real.log H))
          ≤ (1 / (2 * Real.pi)) * ((4 * Cζ * (2 : ℝ) ^ σ₀ * (2 : ℝ) ^ δ₀ * X ^ (σ₀ + δ₀ / 2)) *
              ((2 * σ₀⁻¹ + 2 * δ₀⁻¹) * X ^ (δ₀ / 2))) := by
              refine mul_le_mul_of_nonneg_left
                (mul_le_mul hM_mid_bd hlog_H (by positivity) (by positivity))
                (by positivity)
        _ = C_mid_const * (X ^ (σ₀ + δ₀ / 2) * X ^ (δ₀ / 2)) := by
              dsimp [C_mid_const]; ring
        _ = C_mid_const * X ^ (σ₀ + δ₀) := by rw [hx_exp]
        _ ≤ C_mid_const * X ^ ((1 / 2 : ℝ) + ε) :=
              mul_le_mul_of_nonneg_left hx_le hC_mid_nn
    have h_tail_bd :
        (1 / (2 * Real.pi)) * (2 * (M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)))) ≤
          C_tail_const * X ^ ((1 / 2 : ℝ) + ε) := by
      have hXH_pow1 : (X + H) ^ (σ₀ + 1) ≤ (2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1) := by
        calc (X + H) ^ (σ₀ + 1) ≤ (2 * X) ^ (σ₀ + 1) :=
              Real.rpow_le_rpow (by positivity) hXH_le (by positivity)
          _ = (2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1) := Real.mul_rpow (by norm_num) hX_pos.le
      have hX_div : X ^ (σ₀ + 1) / H = X ^ (σ₀ + 1 / 2) := by
        rw [hH_rpow, ← Real.rpow_sub hX_pos]; ring_nf
      have hX_ge1' : 1 ≤ X ^ (σ₀ + 1 / 2) := Real.one_le_rpow hX (by positivity)
      have hK_bd : K ≤ (2 * (2 : ℝ) ^ (σ₀ + 1) + 3) * X ^ (σ₀ + 1 / 2) := by
        calc K = 2 * (X + H) ^ (σ₀ + 1) / H + 3 := rfl
          _ ≤ 2 * ((2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1)) / H + 3 := by gcongr
          _ = 2 * (2 : ℝ) ^ (σ₀ + 1) * (X ^ (σ₀ + 1) / H) + 3 := by ring
          _ = 2 * (2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1 / 2) + 3 := by rw [hX_div]
          _ ≤ 2 * (2 : ℝ) ^ (σ₀ + 1) * X ^ (σ₀ + 1 / 2) + 3 * X ^ (σ₀ + 1 / 2) := by linarith
          _ = (2 * (2 : ℝ) ^ (σ₀ + 1) + 3) * X ^ (σ₀ + 1 / 2) := by ring
      have hH_tail_pow : H ^ (δ₀ - 1) = X ^ ((δ₀ - 1) / 2) := by
        rw [hH_rpow, ← Real.rpow_mul hX_pos.le]; ring_nf
      have hx_tail_exp : X ^ (σ₀ + 1 / 2) * X ^ ((δ₀ - 1) / 2) = X ^ (σ₀ + δ₀ / 2) := by
        rw [← Real.rpow_add hX_pos]; ring_nf
      have hx_tail_le : X ^ (σ₀ + δ₀ / 2) ≤ X ^ ((1 / 2 : ℝ) + ε) :=
        Real.rpow_le_rpow_of_exponent_le hX (by dsimp [σ₀]; linarith)
      calc (1 / (2 * Real.pi)) * (2 * (M_tail * (H ^ (δ₀ - 1) / (1 - δ₀))))
          = (1 / (2 * Real.pi)) * (2 * Cζ * (2 : ℝ) ^ δ₀ * K * H ^ (δ₀ - 1) / (1 - δ₀)) := by
              dsimp [M_tail]; ring
        _ ≤ (1 / (2 * Real.pi)) * (2 * Cζ * (2 : ℝ) ^ δ₀ *
              ((2 * (2 : ℝ) ^ (σ₀ + 1) + 3) * X ^ (σ₀ + 1 / 2)) * X ^ ((δ₀ - 1) / 2) / (1 - δ₀)) := by
              rw [hH_tail_pow]
              refine mul_le_mul_of_nonneg_left
                (div_le_div_of_nonneg_right
                  (mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hK_bd (by positivity))
                    (by positivity))
                  h1_sub_δ.le)
                (by positivity)
        _ = C_tail_const * (X ^ (σ₀ + 1 / 2) * X ^ ((δ₀ - 1) / 2)) := by
              dsimp [C_tail_const]; ring
        _ = C_tail_const * X ^ (σ₀ + δ₀ / 2) := by rw [hx_tail_exp]
        _ ≤ C_tail_const * X ^ ((1 / 2 : ℝ) + ε) :=
              mul_le_mul_of_nonneg_left hx_tail_le hC_tail_nn
    calc (1 / (2 * Real.pi)) * ‖S_shifted‖
        ≤ (1 / (2 * Real.pi)) * ∫ y : ℝ, B y :=
          mul_le_mul_of_nonneg_left h_S_norm_le (by positivity)
      _ ≤ (1 / (2 * Real.pi)) * (M_mid * (2 * σ₀⁻¹ + 2 * Real.log H) +
            2 * (M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)))) := by
          refine mul_le_mul_of_nonneg_left ?_ (by positivity)
          linarith [hB_sum_eval, hB1_eval, hB2_eval, hB3_eval]
      _ = (1 / (2 * Real.pi)) * (M_mid * (2 * σ₀⁻¹ + 2 * Real.log H)) +
            (1 / (2 * Real.pi)) * (2 * (M_tail * (H ^ (δ₀ - 1) / (1 - δ₀)))) := by ring
      _ ≤ C_mid_const * X ^ ((1 / 2 : ℝ) + ε) + C_tail_const * X ^ ((1 / 2 : ℝ) + ε) :=
          add_le_add h_mid_bd h_tail_bd
      _ = (C_mid_const + C_tail_const) * X ^ ((1 / 2 : ℝ) + ε) := by ring
  have hH1_le : H + 1 ≤ 3 * X ^ ((1 / 2 : ℝ) + ε) := by
    have hH_le_rpow : H ≤ X ^ ((1 / 2 : ℝ) + ε) := by
      have hH_rpow : H = X ^ ((1 / 2 : ℝ)) := by simp [H, Real.sqrt_eq_rpow]
      rw [hH_rpow]
      exact Real.rpow_le_rpow_of_exponent_le hX (by linarith)
    have h1_le_rpow : 1 ≤ X ^ ((1 / 2 : ℝ) + ε) := Real.one_le_rpow hX (by linarith)
    linarith
  calc |(RiemannBlueprint.mertens X : ℝ)|
      ≤ (H + 1) + (1 / (2 * Real.pi)) * ‖S_shifted‖ := h_mert_bd
    _ ≤ 3 * X ^ ((1 / 2 : ℝ) + ε) + (C_mid_const + C_tail_const) * X ^ ((1 / 2 : ℝ) + ε) :=
        add_le_add hH1_le h_inv_norm
    _ = C_final * X ^ ((1 / 2 : ℝ) + ε) := by dsimp [C_final]; ring

end RiemannBlueprint.LittlewoodConverse
