import Mathlib.Analysis.SpecialFunctions.Pow.Complex
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.MellinTransform
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics
import Mathlib.Analysis.Analytic.IsolatedZeros
import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.NumberTheory.LSeries.SumCoeff
import Mathlib.NumberTheory.LSeries.Dirichlet
import Mathlib.NumberTheory.LSeries.Nonvanishing
import Mathlib.NumberTheory.ArithmeticFunction.VonMangoldt
import RiemannBlueprint.Section2_PrimeAtoms
import RiemannBlueprint.Section3_CompositeTaxonomy
import RiemannBlueprint.Section4_CompositeZeta
import RiemannBlueprint.Section5_MobiusMertens
import RiemannBlueprint.Section6_CriticalStripAudit
import RiemannBlueprint.ClassicalAnalyticInterface

/-!
# Section 7: The Explicit Formula & Spectral Equivalences
Upgraded formalization of Section 7:
- Re-exports `chebyshevPsi` and `VonKochRemainderBound`.
- Replaces bare `axiom explicit_formula_spectral_equivalence` with explicit `(H : ClassicalAnalyticInterface)` hypothesis.
-/

set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.style.openClassical false
open scoped Classical

namespace RiemannBlueprint.Section7_SpectralBridge

open RiemannBlueprint
open RiemannBlueprint.Section2_PrimeAtoms (Primes Composites)
open RiemannBlueprint.Section3_CompositeTaxonomy (PureComposites MixedComposites omega)
open RiemannBlueprint.Section5_MobiusMertens (MertensBound mertens_riemann_equivalence)

/-- Definition 7.1: Chebyshev's First Function θ(x) = ∑_{p ≤ x} ln(p). -/
noncomputable def chebyshevTheta (x : ℝ) : ℝ :=
  ∑ p ∈ Finset.filter Nat.Prime (Finset.Iic (Nat.floor x)), Real.log (p : ℝ)

/-- Definition 7.2: Chebyshev's Second Function ψ(x) = ∑_{n ≤ x} Λ(n). -/
noncomputable abbrev chebyshevPsi (x : ℝ) : ℝ := RiemannBlueprint.chebyshevPsi x

/-- Proposition 7.3: Von Mangoldt Weight Annihilation on Mixed Composites.
Mixed composites contribute zero weight to the Chebyshev function ψ(x). -/
theorem mixed_composites_von_mangoldt_vanish (n : ℕ) (hn : n ∈ MixedComposites) :
    ArithmeticFunction.vonMangoldt n = 0 := by
  have h_omega : omega n ≥ 2 := hn.2
  exact RiemannBlueprint.Section3_CompositeTaxonomy.von_mangoldt_isolation n h_omega

/-- Definition 7.4: The Von Koch Remainder Bound of Order 1/2 + ε. -/
abbrev VonKochRemainderBound : Prop := RiemannBlueprint.VonKochRemainderBound

section VonKochMellinForward

open Complex MeasureTheory Filter Asymptotics

noncomputable def chebyshevPsiRemainder (x : ℝ) : ℂ :=
  if 1 < x then ((chebyshevPsi x - x : ℝ) : ℂ) else 0

noncomputable def mellinVonKochRemainder (s : ℂ) : ℂ :=
  s * mellin chebyshevPsiRemainder (-s)

lemma psi_monotone : Monotone chebyshevPsi := by
  intro x y hxy
  unfold chebyshevPsi
  apply Finset.sum_le_sum_of_subset_of_nonneg
  · exact Finset.Iic_subset_Iic.mpr (Nat.floor_mono hxy)
  · intro i _ _; exact ArithmeticFunction.vonMangoldt_nonneg

lemma psi_nonneg (x : ℝ) : 0 ≤ chebyshevPsi x := by
  unfold chebyshevPsi
  exact Finset.sum_nonneg fun _ _ => ArithmeticFunction.vonMangoldt_nonneg

lemma psi_measurable : Measurable chebyshevPsi := psi_monotone.measurable

lemma psi_icc_eq (t : ℝ) :
    (∑ k ∈ Finset.Icc 1 ⌊t⌋₊, ArithmeticFunction.vonMangoldt k) = chebyshevPsi t := by
  unfold chebyshevPsi RiemannBlueprint.chebyshevPsi
  have hsub : Finset.Iic ⌊t⌋₊ = insert 0 (Finset.Icc 1 ⌊t⌋₊) := by
    ext k; simp only [Finset.mem_Iic, Finset.mem_insert, Finset.mem_Icc]; omega
  rw [hsub, Finset.sum_insert (by simp)]
  simp

lemma sum_vonMangoldt_Icc_le_mul_log (n : ℕ) :
    (∑ k ∈ Finset.Icc 1 n, ArithmeticFunction.vonMangoldt k) ≤ (n : ℝ) * Real.log n := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · simp
  · have hle : ∀ k ∈ Finset.Icc 1 n, ArithmeticFunction.vonMangoldt k ≤ Real.log n := by
      intro k hk
      have hk1 : 1 ≤ k := (Finset.mem_Icc.mp hk).1
      have hkn : k ≤ n := (Finset.mem_Icc.mp hk).2
      calc
        ArithmeticFunction.vonMangoldt k ≤ Real.log k := ArithmeticFunction.vonMangoldt_le_log
        _ ≤ Real.log n := Real.log_le_log (by exact_mod_cast hk1) (by exact_mod_cast hkn)
    calc
      (∑ k ∈ Finset.Icc 1 n, ArithmeticFunction.vonMangoldt k)
          ≤ ∑ _k ∈ Finset.Icc 1 n, Real.log n := Finset.sum_le_sum hle
      _ = ((Finset.Icc 1 n).card : ℝ) * Real.log n := by rw [Finset.sum_const, nsmul_eq_mul]
      _ = (n : ℝ) * Real.log n := by simp

lemma id_mul_log_isBigO_rpow {ε : ℝ} (hε : 0 < ε) :
    (fun x : ℝ => x * Real.log x) =O[atTop] fun x : ℝ => x ^ (1 + ε) := by
  have h1 : (fun x : ℝ => x * Real.log x) =O[atTop] fun x : ℝ => x * x ^ ε :=
    (isBigO_refl _ atTop).mul (isLittleO_log_rpow_atTop hε).isBigO
  refine h1.trans (IsBigO.of_bound 1 ?_)
  filter_upwards [eventually_gt_atTop (0 : ℝ)] with x hx
  rw [one_mul, Real.rpow_add hx, Real.rpow_one]

lemma sum_vonMangoldt_Icc_isBigO_rpow {ε : ℝ} (hε : 0 < ε) :
    (fun n : ℕ => ∑ k ∈ Finset.Icc 1 n, ArithmeticFunction.vonMangoldt k) =O[atTop]
      fun n : ℕ => (n : ℝ) ^ (1 + ε) := by
  have hcast : (fun n : ℕ => (n : ℝ) * Real.log n) =O[atTop] fun n : ℕ => (n : ℝ) ^ (1 + ε) :=
    (id_mul_log_isBigO_rpow hε).comp_tendsto tendsto_natCast_atTop_atTop
  refine (IsBigO.of_bound 1 ?_).trans hcast
  filter_upwards [eventually_ge_atTop (1 : ℕ)] with n hn
  have hnonneg : 0 ≤ ∑ k ∈ Finset.Icc 1 n, ArithmeticFunction.vonMangoldt k :=
    Finset.sum_nonneg fun _ _ => ArithmeticFunction.vonMangoldt_nonneg
  have hlog_nonneg : 0 ≤ (n : ℝ) * Real.log n :=
    mul_nonneg (Nat.cast_nonneg _) (Real.log_nonneg (by exact_mod_cast hn))
  rw [one_mul, Real.norm_of_nonneg hnonneg, Real.norm_of_nonneg hlog_nonneg]
  exact sum_vonMangoldt_Icc_le_mul_log n

lemma chebyshevPsiRemainder_eq_indicator :
    chebyshevPsiRemainder = Set.indicator (Set.Ioi 1) (fun x : ℝ => ((chebyshevPsi x - x : ℝ) : ℂ)) := by
  ext x
  simp [chebyshevPsiRemainder, Set.indicator_apply]

lemma chebyshevPsiRemainder_measurable : Measurable chebyshevPsiRemainder := by
  rw [chebyshevPsiRemainder_eq_indicator]
  exact (Complex.continuous_ofReal.measurable.comp (psi_measurable.sub measurable_id)).indicator measurableSet_Ioi

lemma chebyshevPsiRemainder_locallyIntegrableOn :
    LocallyIntegrableOn chebyshevPsiRemainder (Set.Ioi 0) volume := by
  rw [MeasureTheory.locallyIntegrableOn_iff isOpen_Ioi.isLocallyClosed]
  intro k hk_sub hk_comp
  obtain ⟨M, hM⟩ := hk_comp.bddAbove
  set R : ℝ := max M 0
  refine IntegrableOn.of_bound hk_comp.measure_lt_top chebyshevPsiRemainder_measurable.aestronglyMeasurable
    (chebyshevPsi R + R) ?_
  filter_upwards [ae_restrict_mem hk_comp.measurableSet] with x hx
  have hx_pos : 0 < x := hk_sub hx
  have hx_le_R : x ≤ R := le_trans (hM hx) (le_max_left _ _)
  unfold chebyshevPsiRemainder
  split_ifs with hx1
  · calc
      ‖((chebyshevPsi x - x : ℝ) : ℂ)‖ = |chebyshevPsi x - x| := Complex.norm_real _
      _ ≤ |chebyshevPsi x| + |x| := abs_sub _ _
      _ = chebyshevPsi x + x := by rw [abs_of_nonneg (psi_nonneg x), abs_of_pos hx_pos]
      _ ≤ chebyshevPsi R + R := add_le_add (psi_monotone hx_le_R) hx_le_R
  · simp only [norm_zero]
    exact add_nonneg (psi_nonneg R) (le_max_right M 0)

lemma chebyshevPsiRemainder_isBigO_atTop_uncond {ε : ℝ} (hε : 0 < ε) :
    chebyshevPsiRemainder =O[atTop] fun x : ℝ => x ^ (1 + ε) := by
  have hlog : (fun x : ℝ => x * Real.log x) =O[atTop] fun x : ℝ => x ^ (1 + ε) :=
    id_mul_log_isBigO_rpow hε
  have hid : (fun x : ℝ => x) =O[atTop] fun x : ℝ => x ^ (1 + ε) := by
    refine IsBigO.of_bound 1 ?_
    filter_upwards [eventually_ge_atTop (1 : ℝ)] with x hx
    have hx0 : 0 ≤ x := by linarith
    have hxpow0 : 0 ≤ x ^ (1 + ε) := Real.rpow_nonneg hx0 _
    rw [Real.norm_of_nonneg hx0, one_mul, Real.norm_of_nonneg hxpow0]
    calc
      x = x ^ (1 : ℝ) := (Real.rpow_one x).symm
      _ ≤ x ^ (1 + ε) := Real.rpow_le_rpow_of_exponent_le hx (by linarith)
  have hsum : (fun x : ℝ => x * Real.log x + x) =O[atTop] fun x : ℝ => x ^ (1 + ε) := hlog.add hid
  refine (IsBigO.of_bound 1 ?_).trans hsum
  filter_upwards [eventually_ge_atTop (2 : ℝ)] with x hx
  have hx1 : 1 < x := by linarith
  have hfloor1 : 1 ≤ ⌊x⌋₊ := Nat.le_floor (by norm_num; linarith)
  have hfloor_pos : (0 : ℝ) < (⌊x⌋₊ : ℝ) := by exact_mod_cast hfloor1
  have hfloor_le : (⌊x⌋₊ : ℝ) ≤ x := Nat.floor_le (by linarith)
  have hpsi_le : chebyshevPsi x ≤ x * Real.log x := by
    rw [← psi_icc_eq]
    calc
      (∑ k ∈ Finset.Icc 1 ⌊x⌋₊, ArithmeticFunction.vonMangoldt k)
          ≤ (⌊x⌋₊ : ℝ) * Real.log (⌊x⌋₊ : ℝ) := sum_vonMangoldt_Icc_le_mul_log ⌊x⌋₊
      _ ≤ x * Real.log x := mul_le_mul hfloor_le (Real.log_le_log hfloor_pos hfloor_le)
          (Real.log_nonneg (by exact_mod_cast hfloor1)) (by linarith)
  have hxr : 0 ≤ x * Real.log x + x := by
    have : 0 ≤ Real.log x := Real.log_nonneg (by linarith)
    nlinarith
  have hval : chebyshevPsiRemainder x = ((chebyshevPsi x - x : ℝ) : ℂ) := by
    simp [chebyshevPsiRemainder, hx1]
  rw [hval, Complex.norm_real, one_mul, Real.norm_of_nonneg hxr]
  calc
    |chebyshevPsi x - x| ≤ |chebyshevPsi x| + |x| := abs_sub _ _
    _ = chebyshevPsi x + x := by rw [abs_of_nonneg (psi_nonneg x), abs_of_pos (by linarith)]
    _ ≤ x * Real.log x + x := by linarith [hpsi_le]

lemma chebyshevPsiRemainder_isBigO_atTop_of_vonKoch (hvk : VonKochRemainderBound)
    {ε : ℝ} (hε : 0 < ε) :
    chebyshevPsiRemainder =O[atTop] fun x : ℝ => x ^ (1 / 2 + ε) := by
  obtain ⟨C, hC_pos, hC⟩ := hvk ε hε
  refine IsBigO.of_bound C ?_
  filter_upwards [eventually_ge_atTop (2 : ℝ)] with x hx
  have hx1 : 1 < x := by linarith
  have hx0 : 0 ≤ x := by linarith
  have hval : chebyshevPsiRemainder x = ((chebyshevPsi x - x : ℝ) : ℂ) := by
    simp [chebyshevPsiRemainder, hx1]
  rw [hval, Complex.norm_real, Real.norm_of_nonneg (Real.rpow_nonneg hx0 _)]
  exact hC x hx

lemma chebyshevPsiRemainder_isBigO_nhdsGT (b : ℝ) :
    chebyshevPsiRemainder =O[nhdsWithin 0 (Set.Ioi 0)] fun x : ℝ => x ^ (-b) := by
  refine IsBigO.of_bound 1 ?_
  filter_upwards [Ioo_mem_nhdsGT zero_lt_one] with x hx
  have hx1 : ¬ (1 < x) := not_lt.mpr hx.2.le
  have hval : chebyshevPsiRemainder x = 0 := by
    simp [chebyshevPsiRemainder, hx1]
  rw [hval, norm_zero, one_mul]
  exact norm_nonneg _

/-- Stage B (Analytic Continuation of Mellin Remainder):
Under `VonKochRemainderBound`, `mellinVonKochRemainder s` is complex-differentiable
at every `s` with `Re(s) > 1/2`. -/
theorem mellinVonKochRemainder_differentiableAt (hvk : VonKochRemainderBound)
    {s : ℂ} (hs : 1 / 2 < s.re) :
    DifferentiableAt ℂ mellinVonKochRemainder s := by
  let ε : ℝ := (s.re - 1 / 2) / 2
  have hε : 0 < ε := by simp only [ε]; linarith
  have hm : DifferentiableAt ℂ (mellin chebyshevPsiRemainder) (-s) := by
    refine mellin_differentiableAt_of_isBigO_rpow (a := -(1 / 2 + ε)) (b := -s.re - 1)
      chebyshevPsiRemainder_locallyIntegrableOn ?_ ?_ (chebyshevPsiRemainder_isBigO_nhdsGT _) ?_
    · simpa only [neg_neg] using chebyshevPsiRemainder_isBigO_atTop_of_vonKoch hvk hε
    · simp only [neg_re, ε]; linarith
    · simp only [neg_re]; linarith
  exact differentiableAt_id.mul (hm.comp s differentiableAt_id.neg)

/-- Under `VonKochRemainderBound`, `mellinVonKochRemainder` is analytic on `{s | 1/2 < Re(s)}`. -/
theorem mellinVonKochRemainder_analyticOnNhd (hvk : VonKochRemainderBound) :
    AnalyticOnNhd ℂ mellinVonKochRemainder {s : ℂ | 1 / 2 < s.re} := by
  have hopen : IsOpen {s : ℂ | 1 / 2 < s.re} := isOpen_lt continuous_const Complex.continuous_re
  refine DifferentiableOn.analyticOnNhd ?_ hopen
  intro s hs
  exact (mellinVonKochRemainder_differentiableAt hvk hs).differentiableWithinAt

lemma mellinConvergent_psiRemainder_of_one_lt_re {s : ℂ} (hs : 1 < s.re) :
    MellinConvergent chebyshevPsiRemainder (-s) := by
  let ε : ℝ := (s.re - 1) / 2
  have hε : 0 < ε := by simp only [ε]; linarith
  refine mellinConvergent_of_isBigO_rpow (a := -(1 + ε)) (b := -s.re - 1)
    chebyshevPsiRemainder_locallyIntegrableOn ?_ ?_ (chebyshevPsiRemainder_isBigO_nhdsGT _) ?_
  · simpa only [neg_neg] using chebyshevPsiRemainder_isBigO_atTop_uncond hε
  · simp only [neg_re, ε]; linarith
  · simp only [neg_re]; linarith

lemma mellin_psiRemainder_integrableOn_Ioi_one {s : ℂ} (hs : 1 < s.re) :
    IntegrableOn (fun t : ℝ => ((chebyshevPsi t - t : ℝ) : ℂ) * (t : ℂ) ^ (-(s + 1))) (Set.Ioi 1) volume := by
  have hm : IntegrableOn (fun t : ℝ => (t : ℂ) ^ (-s - 1) * chebyshevPsiRemainder t) (Set.Ioi 0) volume := by
    simpa [MellinConvergent, smul_eq_mul] using mellinConvergent_psiRemainder_of_one_lt_re hs
  have hind : IntegrableOn (Set.indicator (Set.Ioi 1)
      (fun t : ℝ => ((chebyshevPsi t - t : ℝ) : ℂ) * (t : ℂ) ^ (-(s + 1)))) (Set.Ioi 0) volume := by
    refine hm.congr_fun (fun t _ => ?_) measurableSet_Ioi
    dsimp only
    rw [chebyshevPsiRemainder_eq_indicator, mul_comm, Set.indicator_apply]
    have hexp : (-s - 1 : ℂ) = -(s + 1) := by ring
    rw [hexp, Set.indicator_apply]
    split_ifs <;> simp
  have hiff := (integrableOn_indicator_iff (s := Set.Ioi (1 : ℝ)) (t := Set.Ioi (0 : ℝ))
    (f := fun t : ℝ => ((chebyshevPsi t - t : ℝ) : ℂ) * (t : ℂ) ^ (-(s + 1)))
    measurableSet_Ioi.nullMeasurableSet).mp hind
  have hinter : Set.Ioi (1 : ℝ) ∩ Set.Ioi (0 : ℝ) = Set.Ioi 1 :=
    Set.inter_eq_left.mpr (Set.Ioi_subset_Ioi zero_le_one)
  rwa [hinter] at hiff

lemma mellin_psiRemainder_eq_integral_Ioi_one (s : ℂ) :
    mellin chebyshevPsiRemainder (-s) =
      ∫ t in Set.Ioi (1 : ℝ), ((chebyshevPsi t - t : ℝ) : ℂ) * (t : ℂ) ^ (-(s + 1)) := by
  unfold mellin
  have hcongr : Set.EqOn
      (fun t : ℝ => (t : ℂ) ^ (-s - 1) • chebyshevPsiRemainder t)
      (Set.indicator (Set.Ioi 1) (fun t : ℝ => ((chebyshevPsi t - t : ℝ) : ℂ) * (t : ℂ) ^ (-(s + 1))))
      (Set.Ioi 0) := by
    intro t _
    simp only [smul_eq_mul, chebyshevPsiRemainder_eq_indicator, Set.indicator_apply]
    have hexp : (-s - 1 : ℂ) = -(s + 1) := by ring
    rw [hexp]
    split_ifs <;> ring
  rw [setIntegral_congr_fun measurableSet_Ioi hcongr, setIntegral_indicator measurableSet_Ioi]
  have hinter : Set.Ioi (0 : ℝ) ∩ Set.Ioi (1 : ℝ) = Set.Ioi 1 :=
    Set.inter_eq_right.mpr (Set.Ioi_subset_Ioi zero_le_one)
  rw [hinter]

lemma integrableOn_id_mul_cpow_Ioi_one {s : ℂ} (hs : 1 < s.re) :
    IntegrableOn (fun t : ℝ => (t : ℂ) * (t : ℂ) ^ (-(s + 1))) (Set.Ioi 1) volume := by
  have hcpow : IntegrableOn (fun t : ℝ => (t : ℂ) ^ (-s)) (Set.Ioi 1) volume :=
    (integrableOn_Ioi_cpow_iff zero_lt_one).mpr (by simp; linarith)
  refine hcpow.congr_fun (fun t ht => ?_) measurableSet_Ioi
  have ht0 : (t : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr (by linarith [Set.mem_Ioi.mp ht])
  calc
    (t : ℂ) ^ (-s) = (t : ℂ) ^ (1 + -(s + 1)) := by ring_nf
    _ = (t : ℂ) ^ (1 : ℂ) * (t : ℂ) ^ (-(s + 1)) := Complex.cpow_add _ _ ht0
    _ = (t : ℂ) * (t : ℂ) ^ (-(s + 1)) := by rw [Complex.cpow_one]

lemma integral_id_mul_cpow_Ioi_one {s : ℂ} (hs : 1 < s.re) :
    ∫ t in Set.Ioi (1 : ℝ), (t : ℂ) * (t : ℂ) ^ (-(s + 1)) = 1 / (s - 1) := by
  have hcongr : Set.EqOn (fun t : ℝ => (t : ℂ) * (t : ℂ) ^ (-(s + 1)))
      (fun t : ℝ => (t : ℂ) ^ (-s)) (Set.Ioi 1) := by
    intro t ht
    have ht0 : (t : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr (by linarith [Set.mem_Ioi.mp ht])
    calc
      (t : ℂ) * (t : ℂ) ^ (-(s + 1)) = (t : ℂ) ^ (1 : ℂ) * (t : ℂ) ^ (-(s + 1)) := by rw [Complex.cpow_one]
      _ = (t : ℂ) ^ (1 + -(s + 1)) := (Complex.cpow_add _ _ ht0).symm
      _ = (t : ℂ) ^ (-s) := by ring_nf
  rw [setIntegral_congr_fun measurableSet_Ioi hcongr,
    integral_Ioi_cpow_of_lt (by simp; linarith) zero_lt_one, Complex.ofReal_one, Complex.one_cpow]
  have hs1 : s - 1 ≠ 0 := sub_ne_zero.mpr (fun h => by rw [h] at hs; norm_num at hs)
  have h1s : -s + 1 ≠ 0 := fun h => hs1 (by linear_combination -h)
  field_simp [hs1, h1s]
  ring

/-- Stage A (Log-Derivative Integral Representation on `Re(s) > 1`):
Unconditionally for `1 < Re(s)`, `-ζ'(s)/ζ(s) = s/(s-1) + J_ψ(s)`. -/
theorem neg_deriv_riemannZeta_div_eq_pole_add_mellinVonKochRemainder
    {s : ℂ} (hs : 1 < s.re) :
    -deriv riemannZeta s / riemannZeta s = s / (s - 1) + mellinVonKochRemainder s := by
  let ε : ℝ := (s.re - 1) / 2
  have hε : 0 < ε := by simp only [ε]; linarith
  have hL := ArithmeticFunction.LSeries_vonMangoldt_eq_deriv_riemannZeta_div hs
  have hint := LSeries_eq_mul_integral_of_nonneg ArithmeticFunction.vonMangoldt
    (r := 1 + ε) (by linarith) (s := s) (by simp only [ε]; linarith)
    (sum_vonMangoldt_Icc_isBigO_rpow hε) (fun n => ArithmeticFunction.vonMangoldt_nonneg)
  have hsplit : (∫ t in Set.Ioi (1 : ℝ),
      (∑ k ∈ Finset.Icc 1 ⌊t⌋₊, (ArithmeticFunction.vonMangoldt k : ℂ)) * (t : ℂ) ^ (-(s + 1))) =
      mellin chebyshevPsiRemainder (-s) + 1 / (s - 1) := by
    have hcongr : ∀ t : ℝ,
        (∑ k ∈ Finset.Icc 1 ⌊t⌋₊, (ArithmeticFunction.vonMangoldt k : ℂ)) * (t : ℂ) ^ (-(s + 1)) =
        ((chebyshevPsi t - t : ℝ) : ℂ) * (t : ℂ) ^ (-(s + 1)) + (t : ℂ) * (t : ℂ) ^ (-(s + 1)) := by
      intro t
      have hpsi : (∑ k ∈ Finset.Icc 1 ⌊t⌋₊, (ArithmeticFunction.vonMangoldt k : ℂ)) =
          (chebyshevPsi t : ℂ) := by
        exact_mod_cast psi_icc_eq t
      rw [hpsi]
      push_cast
      ring
    simp_rw [hcongr]
    rw [integral_add (mellin_psiRemainder_integrableOn_Ioi_one hs) (integrableOn_id_mul_cpow_Ioi_one hs),
      mellin_psiRemainder_eq_integral_Ioi_one, integral_id_mul_cpow_Ioi_one hs]
  rw [← hL, hint, hsplit]
  unfold mellinVonKochRemainder
  ring

/-- Cleared-denominator log-derivative identity unconditionally on `1 < Re(s)`. -/
theorem zeta_deriv_cleared_eq_zero_of_one_lt_re {s : ℂ} (hs : 1 < s.re) :
    deriv riemannZeta s + (s / (s - 1) + mellinVonKochRemainder s) * riemannZeta s = 0 := by
  have hne : riemannZeta s ≠ 0 := riemannZeta_ne_zero_of_one_lt_re hs
  have h := neg_deriv_riemannZeta_div_eq_pole_add_mellinVonKochRemainder hs
  calc
    deriv riemannZeta s + (s / (s - 1) + mellinVonKochRemainder s) * riemannZeta s
        = deriv riemannZeta s + (-deriv riemannZeta s / riemannZeta s) * riemannZeta s := by rw [h]
    _ = 0 := by field_simp [hne]; ring

/-- Stage C (Analytic Continuation across `{s | 1/2 < Re(s)} \ {1}`):
Under `VonKochRemainderBound`, `ζ'(s) + (s/(s-1) + J_ψ(s))ζ(s) = 0` holds for every `s ≠ 1` with `Re(s) > 1/2`. -/
theorem zeta_deriv_cleared_eq_zero_of_half_lt_re_ne_one (hvk : VonKochRemainderBound)
    {s : ℂ} (hs_re : 1 / 2 < s.re) (hs_ne : s ≠ 1) :
    deriv riemannZeta s + (s / (s - 1) + mellinVonKochRemainder s) * riemannZeta s = 0 := by
  let F : ℂ → ℂ := fun z =>
    deriv riemannZeta z + (z / (z - 1) + mellinVonKochRemainder z) * riemannZeta z
  let U_dom : Set ℂ := {z : ℂ | 1 / 2 < z.re} \ {1}
  let U_top : Set ℂ := {z : ℂ | 1 / 2 < z.re ∧ 0 < z.im}
  let U_bot : Set ℂ := {z : ℂ | 1 / 2 < z.re ∧ z.im < 0}
  let U_left : Set ℂ := {z : ℂ | 1 / 2 < z.re ∧ z.re < 1}
  have hU_dom_open : IsOpen U_dom :=
    (isOpen_lt continuous_const Complex.continuous_re).sdiff isClosed_singleton
  have hζ_ana : AnalyticOnNhd ℂ riemannZeta U_dom := by
    refine DifferentiableOn.analyticOnNhd ?_ hU_dom_open
    intro z hz
    exact (differentiableAt_riemannZeta hz.2).differentiableWithinAt
  have hpole_ana : AnalyticOnNhd ℂ (fun z : ℂ => z / (z - 1)) U_dom := by
    refine DifferentiableOn.analyticOnNhd ?_ hU_dom_open
    intro z hz
    have hnum : DifferentiableAt ℂ (fun w : ℂ => w) z := differentiableAt_id
    have hden : DifferentiableAt ℂ (fun w : ℂ => w - 1) z :=
      differentiableAt_id.sub (differentiableAt_const (1 : ℂ))
    exact (hnum.div hden (sub_ne_zero.mpr hz.2)).differentiableWithinAt
  have hF_ana : AnalyticOnNhd ℂ F U_dom :=
    hζ_ana.deriv.add ((hpole_ana.add ((mellinVonKochRemainder_analyticOnNhd hvk).mono
      Set.sdiff_subset)).mul hζ_ana)
  have hU_top_sub : U_top ⊆ U_dom := fun z hz =>
    ⟨hz.1, fun h1 => by rcases Set.mem_singleton_iff.mp h1 with rfl; simp [U_top] at hz⟩
  have hU_bot_sub : U_bot ⊆ U_dom := fun z hz =>
    ⟨hz.1, fun h1 => by rcases Set.mem_singleton_iff.mp h1 with rfl; simp [U_bot] at hz⟩
  have hU_left_sub : U_left ⊆ U_dom := fun z hz =>
    ⟨hz.1, fun h1 => by rcases Set.mem_singleton_iff.mp h1 with rfl; simp [U_left] at hz⟩
  have hlin_gt : ∀ {a b c x y : ℝ}, 0 ≤ a → 0 ≤ b → a + b = 1 → c < x → c < y → c < a * x + b * y := by
    intro a b c x y ha hb hab hx hy
    by_cases ha0 : a = 0
    · have hb1 : b = 1 := by linarith
      rw [ha0, hb1]; linarith
    · have ha_pos : 0 < a := lt_of_le_of_ne ha (Ne.symm ha0)
      have h1 : a * c < a * x := mul_lt_mul_of_pos_left hx ha_pos
      have h2 : b * c ≤ b * y := mul_le_mul_of_nonneg_left hy.le hb
      have h3 : a * c + b * c = c := by rw [← add_mul, hab, one_mul]
      linarith
  have hlin_lt : ∀ {a b c x y : ℝ}, 0 ≤ a → 0 ≤ b → a + b = 1 → x < c → y < c → a * x + b * y < c := by
    intro a b c x y ha hb hab hx hy
    have h := hlin_gt ha hb hab (neg_lt_neg hx) (neg_lt_neg hy)
    linarith
  have hU_top_pre : IsPreconnected U_top := by
    have hconv : Convex ℝ U_top := by
      intro x hx y hy a b ha hb hab
      change 1 / 2 < (a • x + b • y).re ∧ 0 < (a • x + b • y).im
      simp only [Complex.add_re, Complex.add_im, Complex.real_smul, Complex.mul_re,
        Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im, zero_mul, sub_zero, add_zero]
      exact ⟨hlin_gt ha hb hab hx.1 hy.1, hlin_gt ha hb hab hx.2 hy.2⟩
    exact hconv.isPreconnected
  have hU_bot_pre : IsPreconnected U_bot := by
    have hconv : Convex ℝ U_bot := by
      intro x hx y hy a b ha hb hab
      change 1 / 2 < (a • x + b • y).re ∧ (a • x + b • y).im < 0
      simp only [Complex.add_re, Complex.add_im, Complex.real_smul, Complex.mul_re,
        Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im, zero_mul, sub_zero, add_zero]
      exact ⟨hlin_gt ha hb hab hx.1 hy.1, hlin_lt ha hb hab hx.2 hy.2⟩
    exact hconv.isPreconnected
  have hU_left_pre : IsPreconnected U_left := by
    have hconv : Convex ℝ U_left := by
      intro x hx y hy a b ha hb hab
      change 1 / 2 < (a • x + b • y).re ∧ (a • x + b • y).re < 1
      simp only [Complex.add_re, Complex.real_smul, Complex.mul_re, Complex.ofReal_re,
        Complex.ofReal_im, zero_mul, sub_zero]
      exact ⟨hlin_gt ha hb hab hx.1 hy.1, hlin_lt ha hb hab hx.2 hy.2⟩
    exact hconv.isPreconnected
  have hright_open : IsOpen {z : ℂ | 1 < z.re} := isOpen_lt continuous_const Complex.continuous_re
  have htop_open : IsOpen U_top :=
    (isOpen_lt continuous_const Complex.continuous_re).inter
      (isOpen_lt continuous_const Complex.continuous_im)
  have hzero_top : Set.EqOn F 0 U_top := by
    refine (hF_ana.mono hU_top_sub).eqOn_of_preconnected_of_eventuallyEq
      analyticOnNhd_const hU_top_pre (z₀ := (2 : ℂ) + I) (by simp [U_top]; norm_num) ?_
    refine Filter.eventuallyEq_iff_exists_mem.mpr ⟨{z : ℂ | 1 < z.re},
      hright_open.mem_nhds (by simp), fun z hz => zeta_deriv_cleared_eq_zero_of_one_lt_re hz⟩
  have hzero_bot : Set.EqOn F 0 U_bot := by
    refine (hF_ana.mono hU_bot_sub).eqOn_of_preconnected_of_eventuallyEq
      analyticOnNhd_const hU_bot_pre (z₀ := (2 : ℂ) - I) (by simp [U_bot]; norm_num) ?_
    refine Filter.eventuallyEq_iff_exists_mem.mpr ⟨{z : ℂ | 1 < z.re},
      hright_open.mem_nhds (by simp), fun z hz => zeta_deriv_cleared_eq_zero_of_one_lt_re hz⟩
  have hzero_left : Set.EqOn F 0 U_left := by
    refine (hF_ana.mono hU_left_sub).eqOn_of_preconnected_of_eventuallyEq
      analyticOnNhd_const hU_left_pre (z₀ := (3 / 4 : ℂ) + I) (by simp [U_left]; norm_num) ?_
    refine Filter.eventuallyEq_iff_exists_mem.mpr ⟨U_top,
      htop_open.mem_nhds (by simp [U_top]; norm_num), fun z hz => hzero_top hz⟩
  rcases lt_trichotomy s.re 1 with hlt | heq | hgt
  · exact hzero_left ⟨hs_re, hlt⟩
  · have him : s.im ≠ 0 := fun h0 => hs_ne (Complex.ext heq h0)
    rcases lt_or_gt_of_ne him with hneg | hpos
    · exact hzero_bot ⟨hs_re, hneg⟩
    · exact hzero_top ⟨hs_re, hpos⟩
  · exact zeta_deriv_cleared_eq_zero_of_one_lt_re hgt

/-- Forward Non-Simple Zero Corollary under `VonKochRemainderBound`:
Any zero `ρ` of `riemannZeta` with `Re(ρ) > 1/2` satisfies `deriv riemannZeta ρ = 0`
(i.e., `VonKochRemainderBound` unconditionally rules out simple zeros right of the critical line). -/
theorem deriv_riemannZeta_eq_zero_of_vonKoch_of_zeta_eq_zero (hvk : VonKochRemainderBound)
    {ρ : ℂ} (hre : 1 / 2 < ρ.re) (hζ : riemannZeta ρ = 0) :
    deriv riemannZeta ρ = 0 := by
  have hne : ρ ≠ 1 := by
    intro h1
    subst h1
    exact riemannZeta_ne_zero_of_one_le_re (by simp : (1 : ℝ) ≤ (1 : ℂ).re) hζ
  have h := zeta_deriv_cleared_eq_zero_of_half_lt_re_ne_one hvk hre hne
  rw [hζ, mul_zero, add_zero] at h
  exact h

/-- `riemannZeta` is analytic on `{s | s ≠ 1}`. -/
lemma riemannZeta_analyticOnNhd_ne_one : AnalyticOnNhd ℂ riemannZeta {z : ℂ | z ≠ 1} := by
  refine DifferentiableOn.analyticOnNhd ?_ isOpen_ne
  intro z hz
  exact (differentiableAt_riemannZeta hz).differentiableWithinAt

/-- Identity-theorem lemma (unconditional): `riemannZeta` does not vanish identically on any
neighbourhood of a point `ρ` with `Re(ρ) > 1/2`. -/
lemma riemannZeta_not_eventually_zero {ρ : ℂ} (hre : 1 / 2 < ρ.re) :
    ¬ ∀ᶠ z in nhds ρ, riemannZeta z = 0 := by
  intro hev
  by_cases hge : 1 ≤ ρ.re
  · exact riemannZeta_ne_zero_of_one_le_re hge hev.self_of_nhds
  push Not at hge
  let U_top : Set ℂ := {z : ℂ | 1 / 2 < z.re ∧ 0 < z.im}
  let U_left : Set ℂ := {z : ℂ | 1 / 2 < z.re ∧ z.re < 1}
  have hlin_gt : ∀ {a b c x y : ℝ}, 0 ≤ a → 0 ≤ b → a + b = 1 → c < x → c < y →
      c < a * x + b * y := by
    intro a b c x y ha hb hab hx hy
    by_cases ha0 : a = 0
    · have hb1 : b = 1 := by linarith
      rw [ha0, hb1]; linarith
    · have ha_pos : 0 < a := lt_of_le_of_ne ha (Ne.symm ha0)
      have h1 : a * c < a * x := mul_lt_mul_of_pos_left hx ha_pos
      have h2 : b * c ≤ b * y := mul_le_mul_of_nonneg_left hy.le hb
      have h3 : a * c + b * c = c := by rw [← add_mul, hab, one_mul]
      linarith
  have hlin_lt : ∀ {a b c x y : ℝ}, 0 ≤ a → 0 ≤ b → a + b = 1 → x < c → y < c →
      a * x + b * y < c := by
    intro a b c x y ha hb hab hx hy
    have h := hlin_gt ha hb hab (neg_lt_neg hx) (neg_lt_neg hy)
    linarith
  have hU_top_pre : IsPreconnected U_top := by
    have hconv : Convex ℝ U_top := by
      intro x hx y hy a b ha hb hab
      change 1 / 2 < (a • x + b • y).re ∧ 0 < (a • x + b • y).im
      simp only [Complex.add_re, Complex.add_im, Complex.real_smul, Complex.mul_re,
        Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im, zero_mul, sub_zero, add_zero]
      exact ⟨hlin_gt ha hb hab hx.1 hy.1, hlin_gt ha hb hab hx.2 hy.2⟩
    exact hconv.isPreconnected
  have hU_left_pre : IsPreconnected U_left := by
    have hconv : Convex ℝ U_left := by
      intro x hx y hy a b ha hb hab
      change 1 / 2 < (a • x + b • y).re ∧ (a • x + b • y).re < 1
      simp only [Complex.add_re, Complex.real_smul, Complex.mul_re, Complex.ofReal_re,
        Complex.ofReal_im, zero_mul, sub_zero]
      exact ⟨hlin_gt ha hb hab hx.1 hy.1, hlin_lt ha hb hab hx.2 hy.2⟩
    exact hconv.isPreconnected
  have hU_top_sub : U_top ⊆ {z : ℂ | z ≠ 1} := fun z hz h1 => by
    subst h1; simp [U_top] at hz
  have hU_left_sub : U_left ⊆ {z : ℂ | z ≠ 1} := fun z hz h1 => by
    subst h1; simp [U_left] at hz
  have hleft_open : IsOpen U_left :=
    (isOpen_lt continuous_const Complex.continuous_re).inter
      (isOpen_lt Complex.continuous_re continuous_const)
  have hzero_left : Set.EqOn riemannZeta 0 U_left :=
    (riemannZeta_analyticOnNhd_ne_one.mono hU_left_sub).eqOn_zero_of_preconnected_of_eventuallyEq_zero
      hU_left_pre ⟨hre, hge⟩ hev
  have hp : (3 / 4 : ℂ) + I ∈ U_left := by simp [U_left]; norm_num
  have hev2 : riemannZeta =ᶠ[nhds ((3 / 4 : ℂ) + I)] 0 :=
    Filter.eventually_of_mem (hleft_open.mem_nhds hp) fun z hz => hzero_left hz
  have hzero_top : Set.EqOn riemannZeta 0 U_top :=
    (riemannZeta_analyticOnNhd_ne_one.mono hU_top_sub).eqOn_zero_of_preconnected_of_eventuallyEq_zero
      hU_top_pre (by simp [U_top]; norm_num) hev2
  have h2I : riemannZeta ((2 : ℂ) + I) = 0 := hzero_top (by simp [U_top]; norm_num)
  exact riemannZeta_ne_zero_of_one_le_re (by simp) h2I

/-- Stage D (Order-of-zero obstruction, Method A): under `VonKochRemainderBound`, `riemannZeta`
has no zero `ρ` with `Re(ρ) > 1/2`. If `ζ(z) = (z - ρ)^(m+1) h(z)` locally with `h(ρ) ≠ 0`, then
the cleared logarithmic-derivative identity `ζ' + Pζ = 0` forces `(m+1) h(ρ) = 0`. -/
theorem zero_free_re_gt_half_of_vonKoch (hVK : VonKochRemainderBound) :
    ∀ s : ℂ, 1 / 2 < s.re → riemannZeta s ≠ 0 := by
  intro ρ hre hζ
  have hne : ρ ≠ 1 := by
    intro h1
    subst h1
    exact riemannZeta_ne_zero_of_one_le_re (by simp : (1 : ℝ) ≤ (1 : ℂ).re) hζ
  let P : ℂ → ℂ := fun z => z / (z - 1) + mellinVonKochRemainder z
  have hP : AnalyticAt ℂ P ρ := by
    have h1 : AnalyticAt ℂ (fun z : ℂ => z / (z - 1)) ρ :=
      analyticAt_id.div (analyticAt_id.sub analyticAt_const) (sub_ne_zero.mpr hne)
    exact h1.add (mellinVonKochRemainder_analyticOnNhd hVK ρ hre)
  have hζ_an : AnalyticAt ℂ riemannZeta ρ := riemannZeta_analyticOnNhd_ne_one ρ hne
  obtain ⟨n, h, hh_an, hh_ne, hfac⟩ :=
    hζ_an.exists_eventuallyEq_pow_smul_nonzero_iff.mpr (riemannZeta_not_eventually_zero hre)
  simp only [smul_eq_mul] at hfac
  cases n with
  | zero =>
    have := hfac.self_of_nhds
    rw [hζ, pow_zero, one_mul] at this
    exact hh_ne this.symm
  | succ m =>
    -- eventual cleared identity near `ρ`
    have hdom : ∀ᶠ z in nhds ρ, 1 / 2 < z.re ∧ z ≠ 1 :=
      ((isOpen_lt continuous_const Complex.continuous_re).inter isOpen_ne).mem_nhds ⟨hre, hne⟩
    have hcl : ∀ᶠ z in nhds ρ, deriv riemannZeta z + P z * riemannZeta z = 0 :=
      hdom.mono fun z hz => zeta_deriv_cleared_eq_zero_of_half_lt_re_ne_one hVK hz.1 hz.2
    -- eventual derivative formula
    have hd : ∀ᶠ z in nhds ρ, deriv riemannZeta z =
        ((m : ℂ) + 1) * (z - ρ) ^ m * h z + (z - ρ) ^ (m + 1) * deriv h z := by
      filter_upwards [hfac.eventually_nhds, hh_an.eventually_analyticAt] with y hy hhy
      rw [Filter.EventuallyEq.deriv_eq (f := fun z => (z - ρ) ^ (m + 1) * h z) hy]
      have hA : HasDerivAt (fun z : ℂ => (z - ρ) ^ (m + 1))
          (((m + 1 : ℕ) : ℂ) * (y - ρ) ^ (m + 1 - 1) * 1) y :=
        ((hasDerivAt_id y).sub_const ρ).pow (m + 1)
      have hB : HasDerivAt (fun z : ℂ => (z - ρ) ^ (m + 1) * h z)
          (((m + 1 : ℕ) : ℂ) * (y - ρ) ^ (m + 1 - 1) * 1 * h y + (y - ρ) ^ (m + 1) * deriv h y) y :=
        hA.mul hhy.differentiableAt.hasDerivAt
      rw [hB.deriv]
      simp only [Nat.add_sub_cancel, mul_one]
      push_cast
      ring
    -- combined identity `(z - ρ)^m * K z = 0`
    let K : ℂ → ℂ := fun z => ((m : ℂ) + 1) * h z + (z - ρ) * (deriv h z + P z * h z)
    have hmain : ∀ᶠ z in nhds ρ, (z - ρ) ^ m * K z = 0 := by
      filter_upwards [hcl, hd, hfac] with z hcz hdz hfz
      have : (z - ρ) ^ m * K z =
          deriv riemannZeta z + P z * riemannZeta z := by
        rw [hdz, hfz]; simp only [K]; ring
      rw [this, hcz]
    have hK_ev : ∀ᶠ z in nhdsWithin ρ {ρ}ᶜ, K z = 0 := by
      filter_upwards [nhdsWithin_le_nhds hmain, self_mem_nhdsWithin] with z hz hzne
      have hpow : (z - ρ) ^ m ≠ 0 := pow_ne_zero m (sub_ne_zero.mpr hzne)
      exact (mul_eq_zero.mp hz).resolve_left hpow
    have hKc : ContinuousAt K ρ := by
      have h1 : ContinuousAt h ρ := hh_an.continuousAt
      have h2 : ContinuousAt (deriv h) ρ := hh_an.deriv.continuousAt
      have h3 : ContinuousAt P ρ := hP.continuousAt
      exact (continuousAt_const.mul h1).add
        ((continuousAt_id.sub continuousAt_const).mul (h2.add (h3.mul h1)))
    have hlim1 : Filter.Tendsto K (nhdsWithin ρ {ρ}ᶜ) (nhds (K ρ)) :=
      hKc.tendsto.mono_left nhdsWithin_le_nhds
    have hlim2 : Filter.Tendsto K (nhdsWithin ρ {ρ}ᶜ) (nhds 0) :=
      tendsto_const_nhds.congr' (hK_ev.mono fun z hz => hz.symm)
    have hK0 : K ρ = 0 := tendsto_nhds_unique hlim1 hlim2
    simp only [K, sub_self, zero_mul, add_zero] at hK0
    have hm : ((m : ℂ) + 1) ≠ 0 := by exact_mod_cast Nat.succ_ne_zero m
    exact hh_ne ((mul_eq_zero.mp hK0).resolve_left hm)

/-- Von Koch's forward theorem (UNCONDITIONAL in Lean, assuming only the hypothesis
`VonKochRemainderBound`): `ψ(x) = x + O(x^{1/2+ε})` for all `ε > 0` implies RH. -/
theorem vonKoch_implies_rh (hVK : VonKochRemainderBound) :
    _root_.RiemannHypothesis := by
  have h_nofail := zero_free_re_gt_half_of_vonKoch hVK
  intro s hs_zero hs_not_triv hs_not_one
  by_contra h_ne
  rcases lt_or_gt_of_ne h_ne with hs_lt | hs_gt
  · have ⟨h_refl_zero, h_refl_gt⟩ :=
      RiemannBlueprint.Section5_MobiusMertens.zeta_zero_reflection hs_zero hs_not_triv
        hs_not_one hs_lt
    exact h_nofail (1 - s) h_refl_gt h_refl_zero
  · exact h_nofail s hs_gt hs_zero

end VonKochMellinForward

/-- Theorem 7.5 (Spectral Stability Theorem):
Forward direction (`VonKochRemainderBound → _root_.RiemannHypothesis`) is unconditional
via `vonKoch_implies_rh`; converse assumes `H.explicit_formula_spectral_equivalence`. -/
theorem spectral_stability_theorem (H : ClassicalAnalyticInterface) :
    _root_.RiemannHypothesis ↔ VonKochRemainderBound :=
  ⟨H.explicit_formula_spectral_equivalence, vonKoch_implies_rh⟩

/-- Theorem 7.6 (Master Dual-System Equivalence):
The Mertens squarefree inversion bound is equivalent to the Chebyshev prime-power
remainder bound via the spectral zeros of the Riemann zeta function. -/
theorem master_dual_system_equivalence (H : ClassicalAnalyticInterface) :
    MertensBound ↔ VonKochRemainderBound :=
  mertens_riemann_equivalence.symm.trans (spectral_stability_theorem H)

end RiemannBlueprint.Section7_SpectralBridge
