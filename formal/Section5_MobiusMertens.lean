import Mathlib.Analysis.SpecialFunctions.Pow.Complex
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Analysis.Complex.CauchyIntegral
import Mathlib.Analysis.PSeriesComplex
import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.NumberTheory.LSeries.Nonvanishing
import Mathlib.NumberTheory.ArithmeticFunction.Moebius
import RiemannBlueprint.Section2_PrimeAtoms
import RiemannBlueprint.Section3_CompositeTaxonomy
import RiemannBlueprint.Section4_CompositeZeta
import RiemannBlueprint.ClassicalAnalyticInterface
import RiemannBlueprint.LittlewoodForward
import RiemannBlueprint.LittlewoodConverse

/-!
# Section 5: The Multiplicative Inversion Sieve & Mertens Dual Systems
Upgraded formalization of Section 5:
- Eliminates artificial `h_recip` hypothesis via unconditional finite Möbius partition
  `finite_moebius_partition`, exact arithmetic convolution inverse `moebius_mul_zetaZ_eq_one`,
  and infinite convergent partition for `1 < s.re`.
- Proves `zeta_zero_reflection` directly from Mathlib's `riemannZeta_one_sub`!
- Uses `ClassicalAnalyticInterface` instead of global `axiom` declarations.
-/

set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.style.openClassical false
open scoped Classical

namespace RiemannBlueprint.Section5_MobiusMertens

open ArithmeticFunction
open RiemannBlueprint
open RiemannBlueprint.Section2_PrimeAtoms (Primes Composites)
open RiemannBlueprint.Section3_CompositeTaxonomy (PureComposites MixedComposites)
open RiemannBlueprint.Section4_CompositeZeta (PrimeZeta zetaZ summable_filter_cpow_neg summable_unitTerm tsum_unitTerm)

/-- Definition 5.1: The Mertens Function M(x) = ∑_{n ≤ x} μ(n). -/
noncomputable abbrev mertens (x : ℝ) : ℤ := RiemannBlueprint.mertens x

/-- Definition 5.2: The Reciprocal Riemann Zeta Function. -/
noncomputable def ReciprocalZeta (s : ℂ) : ℂ :=
  (riemannZeta s)⁻¹

/-- Definition 5.3: The Möbius Dirichlet Series ∑ μ(n) n^(-s). -/
noncomputable def MoebiusSeries (s : ℂ) : ℂ :=
  ∑' (n : ℕ), if n = 0 then 0 else ((ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s))

/-- Definition 5.4: The Möbius Composite Dirichlet Series ζ_{μ,C}(s). -/
noncomputable def MoebiusCompositeZeta (s : ℂ) : ℂ :=
  ∑' (c : ℕ), if c ∈ Composites then ((ArithmeticFunction.moebius c : ℂ) * (c : ℂ) ^ (-s)) else 0

/-- Proposition 5.5: Prime Sign Inversion of Möbius Function: μ(p) = -1. -/
theorem moebius_prime_sign (p : ℕ) (hp : Nat.Prime p) :
    ArithmeticFunction.moebius p = -1 := by
  exact ArithmeticFunction.moebius_apply_prime hp

/-- Proposition 5.6: Annihilation of Pure Prime Powers in the Inversion Sieve:
For all p prime and k ≥ 2, μ(p^k) = 0. -/
theorem moebius_pure_powers_annihilation (p k : ℕ) (hp : Nat.Prime p) (hk : k ≥ 2) :
    ArithmeticFunction.moebius (p ^ k) = 0 := by
  have hk_pos : k ≠ 0 := by omega
  have hk_ne_one : k ≠ 1 := by omega
  rw [ArithmeticFunction.moebius_apply_prime_pow hp hk_pos]
  simp [hk_ne_one]

/-- Proposition 5.7: The Inversion Sieve isolates Squarefree Mixed Composites:
Any non-zero composite summand in ζ_{μ,C}(s) must belong to MixedComposites. -/
theorem moebius_composite_support (c : ℕ) (hc : c ∈ PureComposites) :
    ArithmeticFunction.moebius c = 0 := by
  rcases hc with ⟨p, k, hp, hk, rfl⟩
  exact moebius_pure_powers_annihilation p k hp hk

/-- Lemma 5.8 (Pointwise Möbius Arithmetic Trichotomy): -/
theorem pointwise_moebius_partition (s : ℂ) (n : ℕ) :
    (if n = 0 then (0 : ℂ) else (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s)) =
    (if n = 1 then (1 : ℂ) else 0) +
    (-(if Nat.Prime n then (n : ℂ) ^ (-s) else 0)) +
    (if n ∈ Composites then (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) else 0) := by
  rcases n with _ | n
  · simp [Nat.not_prime_zero, Composites]
  · rcases n with _ | n
    · have h1 : ¬ Nat.Prime 1 := Nat.not_prime_one
      have hc1 : 1 ∉ Composites := fun h => by have := h.1; omega
      simp [h1, hc1]
    · by_cases hp : Nat.Prime (n + 2)
      · have hc : (n + 2) ∉ Composites := fun h => h.2 hp
        simp [hp, hc, ArithmeticFunction.moebius_apply_prime hp]
      · have hc : (n + 2) ∈ Composites := ⟨by omega, hp⟩
        simp [hp, hc]

/-- Theorem 5.9 (Unconditional Finite Partial-Sum Möbius Partition):
For all N ≥ 1 and all s ∈ ℂ, zero artificial assumptions! -/
theorem finite_moebius_partition (s : ℂ) (N : ℕ) (hN : 1 ≤ N) :
    ∑ n ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) =
      1 - (∑ n ∈ Finset.Icc 1 N, if n.Prime then (n : ℂ) ^ (-s) else 0) +
          (∑ n ∈ Finset.Icc 1 N, if n ∈ Composites then (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) else 0) := by
  have h_pt : ∀ n ∈ Finset.Icc 1 N,
      (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) =
      (if n = 1 then (1 : ℂ) else 0) +
      (-(if n.Prime then (n : ℂ) ^ (-s) else 0)) +
      (if n ∈ Composites then (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) else 0) := by
    intro n hn
    have hn0 : n ≠ 0 := by have := (Finset.mem_Icc.mp hn).1; omega
    simpa [hn0] using pointwise_moebius_partition s n
  rw [Finset.sum_congr rfl h_pt]
  simp only [Finset.sum_add_distrib, Finset.sum_neg_distrib]
  have h1_mem : 1 ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨le_rfl, hN⟩
  have h_unit : (∑ n ∈ Finset.Icc 1 N, if n = 1 then (1 : ℂ) else 0) = 1 := by simp [h1_mem]
  rw [h_unit]
  ring

/-- Theorem 5.10 (Exact Dirichlet Convolution Inverse Identity):
(μ * ζ : ArithmeticFunction ℤ) = 1 directly from Mathlib! -/
theorem moebius_mul_zetaZ_eq_one :
    (ArithmeticFunction.moebius : ArithmeticFunction ℤ) * zetaZ = 1 := by
  exact ArithmeticFunction.moebius_mul_coe_zeta

/-- Lemma 5.11: Bound |(μ n : ℝ)| ≤ 1 and summability of Möbius-weighted Dirichlet terms for Re(s) > 1. -/
theorem norm_moebius_le_one (n : ℕ) : ‖(ArithmeticFunction.moebius n : ℂ)‖ ≤ 1 := by
  have h : |ArithmeticFunction.moebius n| ≤ 1 := ArithmeticFunction.abs_moebius_le_one
  rw [Complex.norm_intCast]
  exact_mod_cast h

theorem summable_moebius_filter (P : ℕ → Prop) [DecidablePred P] {s : ℂ} (hs : 1 < s.re) :
    Summable (fun n : ℕ => if P n then (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) else 0) := by
  have h_abs := (Section4_CompositeZeta.summable_cpow_neg hs).norm
  refine Summable.of_norm_bounded h_abs (fun n => ?_)
  by_cases hP : P n <;> by_cases hn0 : n = 0
  · subst hn0
    simp
  · simp only [hP, hn0, ↓reduceIte, norm_mul]
    calc ‖(ArithmeticFunction.moebius n : ℂ)‖ * ‖(n : ℂ) ^ (-s)‖
        ≤ 1 * ‖(n : ℂ) ^ (-s)‖ := mul_le_mul_of_nonneg_right (norm_moebius_le_one n) (norm_nonneg _)
      _ = ‖(n : ℂ) ^ (-s)‖ := one_mul _
  · simp [hn0]
  · simp [hP, hn0]

/-- Theorem 5.12 (Unconditional Infinite Reciprocal Partition Relation):
For Re(s) > 1, ∑' μ(n) n^(-s) = 1 - P(s) + ζ_{μ,C}(s) holds unconditionally! -/
theorem reciprocal_partition_identity {s : ℂ} (hs : 1 < s.re) :
    MoebiusCompositeZeta s = MoebiusSeries s - 1 + PrimeZeta s := by
  have h_eq : MoebiusSeries s =
      ∑' n : ℕ, ((if n = 1 then (1 : ℂ) else 0) +
                 (-(if Nat.Prime n then (n : ℂ) ^ (-s) else 0)) +
                 (if n ∈ Composites then (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) else 0)) := by
    dsimp [MoebiusSeries]
    exact tsum_congr (fun n => pointwise_moebius_partition s n)
  have hU : Summable (fun n : ℕ => if n = 1 then (1 : ℂ) else 0) := summable_unitTerm
  have hP : Summable (fun n : ℕ => -(if Nat.Prime n then (n : ℂ) ^ (-s) else 0)) :=
    (summable_filter_cpow_neg Nat.Prime hs).neg
  have hC : Summable (fun n : ℕ => if n ∈ Composites then (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) else 0) :=
    summable_moebius_filter (· ∈ Composites) hs
  rw [h_eq, (hU.add hP).tsum_add hC, hU.tsum_add hP, tsum_unitTerm, tsum_neg]
  have hp_eq : (∑' n : ℕ, if Nat.Prime n then (n : ℂ) ^ (-s) else 0) = PrimeZeta s := rfl
  have hc_eq : (∑' n : ℕ, if n ∈ Composites then (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) else 0) =
      MoebiusCompositeZeta s := rfl
  rw [hp_eq, hc_eq]
  ring

/-- Definition 5.13: The Riemann Hypothesis (RH) as formalized canonically in Mathlib4. -/
abbrev RiemannHypothesis : Prop := _root_.RiemannHypothesis

/-- Definition 5.14: The Mertens Growth Bound of Order 1/2 + ε. -/
abbrev MertensBound : Prop := RiemannBlueprint.MertensBound

section AbelSummation

open intervalIntegral MeasureTheory Set Filter

/-- Real-argument Mertens summatory function `M(x) = ∑_{1 ≤ n ≤ ⌊x⌋₊} μ(n)` in `ℂ`. -/
noncomputable def mertensReal (x : ℝ) : ℂ :=
  ∑ n ∈ Finset.Icc 1 ⌊x⌋₊, (ArithmeticFunction.moebius n : ℂ)

/-- Discrete Abel summation (summation by parts) for the Möbius function on `[1, N]`. -/
lemma abel_summation_moebius_finset (N : ℕ) (hN : 1 ≤ N) (a : ℕ → ℂ) :
    ∑ n ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius n : ℂ) * a n =
      mertensReal N * a N +
        ∑ n ∈ Finset.Icc 1 (N - 1), mertensReal n * (a n - a (n + 1)) := by
  induction N, hN using Nat.le_induction with
  | base =>
    simp [mertensReal]
  | succ k hk ih =>
    rw [show Finset.Icc 1 (k + 1) = insert (k + 1) (Finset.Icc 1 k) from by
      ext m; simp only [Finset.mem_Icc, Finset.mem_insert]; constructor <;> omega]
    rw [Finset.sum_insert (by simp)]
    rw [ih]
    have h_step : (ArithmeticFunction.moebius (k + 1) : ℂ) =
        mertensReal ((k + 1 : ℕ) : ℝ) - mertensReal (k : ℝ) := by
      simp only [mertensReal, Nat.floor_natCast]
      rw [show Finset.Icc 1 (k + 1) = insert (k + 1) (Finset.Icc 1 k) from by
        ext m; simp only [Finset.mem_Icc, Finset.mem_insert]; constructor <;> omega]
      rw [Finset.sum_insert (by simp)]
      ring
    have h_k : k + 1 - 1 = k := by omega
    have hk_not : k ∉ Finset.Icc 1 (k - 1) := by simp only [Finset.mem_Icc]; omega
    rw [h_k, show Finset.Icc 1 k = insert k (Finset.Icc 1 (k - 1)) from by
      ext m; simp only [Finset.mem_Icc, Finset.mem_insert]; constructor <;> omega]
    rw [Finset.sum_insert hk_not, h_step]
    push_cast
    ring

/-- Trivial linear bound `‖M(x)‖ ≤ x` for `x ≥ 1`. -/
lemma norm_mertensReal_le (x : ℝ) (hx : 1 ≤ x) : ‖mertensReal x‖ ≤ x := by
  have h1 : ‖mertensReal x‖ ≤ (⌊x⌋₊ : ℝ) := by
    calc ‖∑ n ∈ Finset.Icc 1 ⌊x⌋₊, (ArithmeticFunction.moebius n : ℂ)‖
        ≤ ∑ n ∈ Finset.Icc 1 ⌊x⌋₊, ‖(ArithmeticFunction.moebius n : ℂ)‖ := norm_sum_le _ _
      _ ≤ ∑ _n ∈ Finset.Icc 1 ⌊x⌋₊, (1 : ℝ) := by
          refine Finset.sum_le_sum fun n _ => ?_
          rw [Complex.norm_intCast]
          exact_mod_cast ArithmeticFunction.abs_moebius_le_one (n := n)
      _ = (Finset.Icc 1 ⌊x⌋₊).card := by simp
      _ ≤ (⌊x⌋₊ : ℝ) := by norm_cast; simp [Nat.card_Icc]
  exact h1.trans (Nat.floor_le (zero_le_one.trans hx))

private lemma hasDerivAt_ofReal_cpow_neg (s : ℂ) {x : ℝ} (hx : 0 < x) :
    HasDerivAt (fun y : ℝ => (y : ℂ) ^ (-s)) (-s * (x : ℂ) ^ (-s - 1)) x := by
  have h0 : ((x : ℝ) : ℂ) ∈ Complex.slitPlane := Complex.ofReal_mem_slitPlane.mpr hx
  have hc : HasDerivAt (fun z : ℂ => z ^ (-s)) ((-s) * (x : ℂ) ^ (-s - 1) * 1) (x : ℂ) :=
    (hasDerivAt_id (x : ℂ)).cpow_const h0
  simpa using hc.comp_ofReal

private lemma unit_interval_cpow_integral (s : ℂ) (n : ℕ) (hn : 1 ≤ n) :
    s * ∫ x in (n : ℝ)..((n + 1 : ℕ) : ℝ), (x : ℂ) ^ (-s - 1) =
      (n : ℂ) ^ (-s) - ((n + 1 : ℕ) : ℂ) ^ (-s) := by
  have hle : (n : ℝ) ≤ ((n + 1 : ℕ) : ℝ) := by exact_mod_cast Nat.le_succ n
  have hn_pos : (0 : ℝ) < (n : ℝ) := Nat.cast_pos.mpr hn
  have hderiv : ∀ x ∈ Set.uIcc (n : ℝ) ((n + 1 : ℕ) : ℝ),
      HasDerivAt (fun y : ℝ => (y : ℂ) ^ (-s)) (-s * (x : ℂ) ^ (-s - 1)) x := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    exact hasDerivAt_ofReal_cpow_neg s (lt_of_lt_of_le hn_pos hx.1)
  have hcont : ContinuousOn (fun x : ℝ => -s * (x : ℂ) ^ (-s - 1))
      (Set.uIcc (n : ℝ) ((n + 1 : ℕ) : ℝ)) := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le hn_pos hx.1
    have hc : ContinuousAt (fun z : ℂ => z ^ (-s - 1)) (x : ℂ) :=
      ((hasDerivAt_id (x : ℂ)).cpow_const (Complex.ofReal_mem_slitPlane.mpr hx_pos)).continuousAt
    exact (continuousAt_const.mul (hc.comp Complex.continuous_ofReal.continuousAt)).continuousWithinAt
  have hftc := intervalIntegral.integral_eq_sub_of_hasDerivAt hderiv hcont.intervalIntegrable
  rw [intervalIntegral.integral_const_mul] at hftc
  have hrhs : (((n + 1 : ℕ) : ℝ) : ℂ) ^ (-s) - ((n : ℝ) : ℂ) ^ (-s) =
      ((n + 1 : ℕ) : ℂ) ^ (-s) - (n : ℂ) ^ (-s) := by
    simp only [Complex.ofReal_natCast]
  calc s * ∫ x in (n : ℝ)..((n + 1 : ℕ) : ℝ), (x : ℂ) ^ (-s - 1)
      = -(-s * ∫ x in (n : ℝ)..((n + 1 : ℕ) : ℝ), (x : ℂ) ^ (-s - 1)) := by ring
    _ = -(((n + 1 : ℕ) : ℂ) ^ (-s) - (n : ℂ) ^ (-s)) := by rw [hftc, hrhs]
    _ = (n : ℂ) ^ (-s) - ((n + 1 : ℕ) : ℂ) ^ (-s) := by ring

private lemma intervalIntegrable_mertensReal_cpow_unit (s : ℂ) (n : ℕ) (hn : 1 ≤ n) :
    IntervalIntegrable (fun x : ℝ => mertensReal x * (x : ℂ) ^ (-s - 1)) volume
      (n : ℝ) ((n + 1 : ℕ) : ℝ) := by
  have hle : (n : ℝ) ≤ ((n + 1 : ℕ) : ℝ) := by exact_mod_cast Nat.le_succ n
  have hn_pos : (0 : ℝ) < (n : ℝ) := Nat.cast_pos.mpr hn
  have hcont : ContinuousOn (fun x : ℝ => mertensReal (n : ℝ) * (x : ℂ) ^ (-s - 1))
      (Set.uIcc (n : ℝ) ((n + 1 : ℕ) : ℝ)) := by
    intro x hx
    rw [Set.uIcc_of_le hle] at hx
    have hx_pos : 0 < x := lt_of_lt_of_le hn_pos hx.1
    have hc : ContinuousAt (fun z : ℂ => z ^ (-s - 1)) (x : ℂ) :=
      ((hasDerivAt_id (x : ℂ)).cpow_const (Complex.ofReal_mem_slitPlane.mpr hx_pos)).continuousAt
    exact (continuousAt_const.mul (hc.comp Complex.continuous_ofReal.continuousAt)).continuousWithinAt
  have h_eq : Set.EqOn (fun x : ℝ => mertensReal (n : ℝ) * (x : ℂ) ^ (-s - 1))
      (fun x : ℝ => mertensReal x * (x : ℂ) ^ (-s - 1)) (Set.Ioo (n : ℝ) ((n + 1 : ℕ) : ℝ)) := by
    intro x hx
    have hfl : ⌊x⌋₊ = n := (Nat.floor_eq_iff (hn_pos.le.trans hx.1.le)).mpr
      ⟨hx.1.le, by simpa using hx.2⟩
    dsimp only
    unfold mertensReal
    rw [Nat.floor_natCast, hfl]
  have hint_oo : IntegrableOn (fun x : ℝ => mertensReal x * (x : ℂ) ^ (-s - 1))
      (Set.Ioo (n : ℝ) ((n + 1 : ℕ) : ℝ)) volume :=
    (hcont.integrableOn_uIcc.mono_set (by rw [Set.uIcc_of_le hle]; exact Set.Ioo_subset_Icc_self)).congr_fun h_eq measurableSet_Ioo
  rw [intervalIntegrable_iff_integrableOn_Ioc_of_le hle]
  exact hint_oo.congr_set_ae MeasureTheory.Ioo_ae_eq_Ioc.symm

private lemma mertensReal_unit_interval_integral (s : ℂ) (n : ℕ) (hn : 1 ≤ n) :
    s * ∫ x in (n : ℝ)..((n + 1 : ℕ) : ℝ), mertensReal x * (x : ℂ) ^ (-s - 1) =
      mertensReal n * ((n : ℂ) ^ (-s) - ((n + 1 : ℕ) : ℂ) ^ (-s)) := by
  have hle : (n : ℝ) ≤ ((n + 1 : ℕ) : ℝ) := by exact_mod_cast Nat.le_succ n
  have h_eq : Set.EqOn (fun x : ℝ => mertensReal x * (x : ℂ) ^ (-s - 1))
      (fun x : ℝ => mertensReal n * (x : ℂ) ^ (-s - 1)) (Set.Ioo (n : ℝ) ((n + 1 : ℕ) : ℝ)) := by
    intro x hx
    have hx_nonneg : 0 ≤ x := le_trans (Nat.cast_nonneg n) hx.1.le
    have hfl : ⌊x⌋₊ = n := (Nat.floor_eq_iff hx_nonneg).mpr ⟨hx.1.le, by simpa using hx.2⟩
    dsimp only
    unfold mertensReal
    rw [hfl, Nat.floor_natCast]
  rw [intervalIntegral.integral_of_le hle, MeasureTheory.integral_Ioc_eq_integral_Ioo]
  rw [MeasureTheory.setIntegral_congr_fun measurableSet_Ioo h_eq]
  rw [← MeasureTheory.integral_Ioc_eq_integral_Ioo, ← intervalIntegral.integral_of_le hle]
  rw [intervalIntegral.integral_const_mul]
  calc s * (mertensReal n * ∫ x in (n : ℝ)..((n + 1 : ℕ) : ℝ), (x : ℂ) ^ (-s - 1))
      = mertensReal n * (s * ∫ x in (n : ℝ)..((n + 1 : ℕ) : ℝ), (x : ℂ) ^ (-s - 1)) := by ring
    _ = mertensReal n * ((n : ℂ) ^ (-s) - ((n + 1 : ℕ) : ℂ) ^ (-s)) := by
        rw [unit_interval_cpow_integral s n hn]

/-- Continuous Abel summation (Stieltjes integration by parts) identity for finite Möbius Dirichlet sums. -/
theorem mertens_abel_integral_finset (N : ℕ) (hN : 1 ≤ N) (s : ℂ) :
    ∑ n ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) =
      mertensReal N * (N : ℂ) ^ (-s) +
        s * ∫ x in (1 : ℝ)..(N : ℝ), mertensReal x * (x : ℂ) ^ (-s - 1) := by
  suffices h : (∑ n ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius n : ℂ) * (n : ℂ) ^ (-s) =
      mertensReal N * (N : ℂ) ^ (-s) +
        s * ∫ x in (1 : ℝ)..(N : ℝ), mertensReal x * (x : ℂ) ^ (-s - 1)) ∧
      IntervalIntegrable (fun x : ℝ => mertensReal x * (x : ℂ) ^ (-s - 1)) volume (1 : ℝ) (N : ℝ) by
    exact h.1
  induction N, hN using Nat.le_induction with
  | base =>
    refine ⟨?_, ?_⟩
    · simp [mertensReal]
    · simp only [Nat.cast_one]
      exact IntervalIntegrable.refl
  | succ k hk ih =>
    rcases ih with ⟨ih_eq, ih_int⟩
    have hint_k : IntervalIntegrable (fun x : ℝ => mertensReal x * (x : ℂ) ^ (-s - 1)) volume
        (k : ℝ) ((k + 1 : ℕ) : ℝ) := intervalIntegrable_mertensReal_cpow_unit s k hk
    have hint_succ : IntervalIntegrable (fun x : ℝ => mertensReal x * (x : ℂ) ^ (-s - 1)) volume
        (1 : ℝ) ((k + 1 : ℕ) : ℝ) := ih_int.trans hint_k
    refine ⟨?_, hint_succ⟩
    rw [show Finset.Icc 1 (k + 1) = insert (k + 1) (Finset.Icc 1 k) from by
      ext m; simp only [Finset.mem_Icc, Finset.mem_insert]; constructor <;> omega]
    rw [Finset.sum_insert (by simp), ih_eq]
    have hsplit : ∫ x in (1 : ℝ)..((k + 1 : ℕ) : ℝ), mertensReal x * (x : ℂ) ^ (-s - 1) =
        (∫ x in (1 : ℝ)..(k : ℝ), mertensReal x * (x : ℂ) ^ (-s - 1)) +
        ∫ x in (k : ℝ)..((k + 1 : ℕ) : ℝ), mertensReal x * (x : ℂ) ^ (-s - 1) :=
      (intervalIntegral.integral_add_adjacent_intervals ih_int hint_k).symm
    have h_step : (ArithmeticFunction.moebius (k + 1) : ℂ) =
        mertensReal ((k + 1 : ℕ) : ℝ) - mertensReal (k : ℝ) := by
      unfold mertensReal
      rw [Nat.floor_natCast, Nat.floor_natCast]
      rw [show Finset.Icc 1 (k + 1) = insert (k + 1) (Finset.Icc 1 k) from by
        ext m; simp only [Finset.mem_Icc, Finset.mem_insert]; constructor <;> omega]
      rw [Finset.sum_insert (by simp)]
      ring
    have hunit := mertensReal_unit_interval_integral s k hk
    have hcomb : (mertensReal ((k + 1 : ℕ) : ℝ) - mertensReal (k : ℝ)) * ((k + 1 : ℕ) : ℂ) ^ (-s) +
          (mertensReal (k : ℝ) * (k : ℂ) ^ (-s) +
            s * (∫ x in (1 : ℝ)..(k : ℝ), mertensReal x * (x : ℂ) ^ (-s - 1))) =
        mertensReal ((k + 1 : ℕ) : ℝ) * ((k + 1 : ℕ) : ℂ) ^ (-s) +
          (s * (∫ x in (1 : ℝ)..(k : ℝ), mertensReal x * (x : ℂ) ^ (-s - 1)) +
           mertensReal (k : ℝ) * ((k : ℂ) ^ (-s) - ((k + 1 : ℕ) : ℂ) ^ (-s))) := by ring
    rw [h_step, hcomb, ← hunit, hsplit, mul_add]

/-- Vanishing of the boundary term `M(N) * N^(-s) → 0` for `Re(s) > 1`. -/
theorem mertens_boundary_decay {s : ℂ} (hs : 1 < s.re) :
    Tendsto (fun N : ℕ => mertensReal N * (N : ℂ) ^ (-s)) atTop (nhds 0) := by
  have h_tend : Tendsto (fun N : ℕ => (N : ℝ) ^ (1 - s.re)) atTop (nhds 0) := by
    have hlt : 0 < s.re - 1 := by linarith
    have h1 := (tendsto_rpow_neg_atTop hlt).comp tendsto_natCast_atTop_atTop
    exact h1.congr (fun N => by simp only [Function.comp_apply, neg_sub])
  refine squeeze_zero_norm' ?_ h_tend
  filter_upwards [eventually_ge_atTop 1] with N hN
  have hN_pos : (0 : ℝ) < (N : ℝ) := Nat.cast_pos.mpr hN
  rw [norm_mul, Complex.norm_natCast_cpow_of_pos hN]
  have hrhs : (N : ℝ) * (N : ℝ) ^ (-s.re) = (N : ℝ) ^ (1 - s.re) := by
    have h1 : (N : ℝ) * (N : ℝ) ^ (-s.re) = (N : ℝ) ^ (1 : ℝ) * (N : ℝ) ^ (-s.re) := by
      rw [Real.rpow_one]
    rw [h1, ← Real.rpow_add hN_pos]
    congr 1
  exact hrhs ▸ mul_le_mul_of_nonneg_right
    (norm_mertensReal_le N (by exact_mod_cast hN)) (Real.rpow_nonneg hN_pos.le _)

end AbelSummation

/-- Lemma 5.15: Non-vanishing of invertible reciprocal. -/
theorem ne_zero_of_reciprocal_product {s : ℂ} {I_s : ℂ} (h : riemannZeta s * I_s = 1) :
    riemannZeta s ≠ 0 := by
  intro hz
  rw [hz, zero_mul] at h
  exact zero_ne_one h

/-- Theorem 5.16 (Zero-Free Region from Reciprocal Inversion): -/
theorem zero_free_of_reciprocal_invertible (D : Set ℂ) (I : ℂ → ℂ)
    (h_inv : ∀ s ∈ D, riemannZeta s * I s = 1) :
    ∀ s ∈ D, riemannZeta s ≠ 0 := by
  intro s hs
  exact ne_zero_of_reciprocal_product (h_inv s hs)

/-- Theorem 5.17 (Zero Reflection Symmetry — PROVED DIRECTLY FROM MATHLIB!):
Non-trivial zeros of ζ(s) satisfy reflection symmetry about Re(s) = 1/2. -/
theorem zeta_zero_reflection {s : ℂ} (hz : riemannZeta s = 0)
    (h_not_triv : ¬∃ n : ℕ, s = -2 * (n + 1)) (h_not_one : s ≠ 1) (_hs_lt : s.re < 1 / 2) :
    riemannZeta (1 - s) = 0 ∧ (1 - s).re > 1 / 2 := by
  refine ⟨?_, ?_⟩
  · have h_not_neg_nat : ∀ n : ℕ, s ≠ -(n : ℂ) := by
      intro n hn
      subst hn
      rcases n with _ | n
      · simp [riemannZeta_zero] at hz
      · rcases Nat.even_or_odd (n + 1) with ⟨m, hm⟩ | ⟨m, hm⟩
        · have hm_pos : 0 < m := by omega
          have h_ex : ∃ k : ℕ, -(↑(n + 1) : ℂ) = -2 * (↑k + 1) := by
            refine ⟨m - 1, ?_⟩
            have h1 : n + 1 = 2 * ((m - 1) + 1) := by omega
            push_cast [h1]
            ring
          exact h_not_triv h_ex
        · let w : ℂ := ((2 * m + 2 : ℕ) : ℂ)
          have hw_not_neg : ∀ j : ℕ, w ≠ -(j : ℂ) := by
            intro j h_eq
            have h_re := congr_arg Complex.re h_eq
            simp [w] at h_re
            linarith
          have hw_ne_one : w ≠ 1 := by
            intro h_eq
            have h_re := congr_arg Complex.re h_eq
            simp [w] at h_re
            linarith
          have h_fe := riemannZeta_one_sub hw_not_neg hw_ne_one
          have h_1mw : 1 - w = -(↑(n + 1) : ℂ) := by
            dsimp [w]
            push_cast [hm]
            ring
          rw [h_1mw, hz] at h_fe
          have h_2pi_ne : ((2 * Real.pi : ℝ) : ℂ) ≠ 0 := by
            exact_mod_cast (mul_ne_zero two_ne_zero Real.pi_ne_zero)
          have h_cpow_ne : (2 * (Real.pi : ℂ)) ^ (-w) ≠ 0 := by
            rw [Complex.cpow_ne_zero_iff]
            left
            exact_mod_cast (mul_ne_zero two_ne_zero Real.pi_ne_zero)
          have h_gamma_ne : Complex.Gamma w ≠ 0 := Complex.Gamma_ne_zero hw_not_neg
          have h_cos_ne : Complex.cos ((Real.pi : ℂ) * w / 2) ≠ 0 := by
            intro hcos
            rw [Complex.cos_eq_zero_iff] at hcos
            rcases hcos with ⟨k, hk⟩
            have hw2 : (Real.pi : ℂ) * w / 2 = ((((m + 1 : ℕ) : ℝ) * Real.pi : ℝ) : ℂ) := by
              dsimp [w]; push_cast; ring
            have hk2 : (2 * (k : ℂ) + 1) * (Real.pi : ℂ) / 2 = ((((2 * k + 1 : ℤ) / 2 : ℝ) * Real.pi : ℝ) : ℂ) := by
              push_cast; ring
            rw [hw2, hk2] at hk
            have hk_r : ((m + 1 : ℕ) : ℝ) * Real.pi = ((2 * k + 1 : ℤ) / 2 : ℝ) * Real.pi :=
              Complex.ofReal_injective hk
            have hdiv : ((m + 1 : ℕ) : ℝ) = ((2 * k + 1 : ℤ) / 2 : ℝ) :=
              mul_right_cancel₀ Real.pi_ne_zero hk_r
            have hdiv2 : (2 : ℝ) * ((m + 1 : ℕ) : ℝ) = ((2 * k + 1 : ℤ) : ℝ) := by linarith
            have hint : (2 * ((m : ℤ) + 1)) = 2 * k + 1 := by exact_mod_cast hdiv2
            omega
          have h_zeta_ne : riemannZeta w ≠ 0 := by
            apply riemannZeta_ne_zero_of_one_le_re
            dsimp [w]
            norm_cast
            omega
          have h_rhs_ne : 2 * (2 * (Real.pi : ℂ)) ^ (-w) * Complex.Gamma w *
              Complex.cos ((Real.pi : ℂ) * w / 2) * riemannZeta w ≠ 0 := by
            refine mul_ne_zero (mul_ne_zero (mul_ne_zero (mul_ne_zero (by norm_num) h_cpow_ne) h_gamma_ne) h_cos_ne) h_zeta_ne
          exact h_rhs_ne h_fe.symm
    rw [riemannZeta_one_sub h_not_neg_nat h_not_one, hz, mul_zero]
  · rw [Complex.sub_re, Complex.one_re]
    linarith

/-- Theorem 5.18 (Zero-Free Half Plane from Mertens Bound — UNCONDITIONAL): -/
theorem zero_free_re_gt_half_of_mertens (h_mertens : MertensBound) :
    ∀ s : ℂ, s.re > 1/2 → riemannZeta s ≠ 0 := by
  rcases RiemannBlueprint.LittlewoodForward.mertens_inversion_of_bound h_mertens with ⟨I_M, h_inv⟩
  intro s hs
  exact ne_zero_of_reciprocal_product (h_inv s hs)

/-- Theorem 5.19 (Littlewood's Forward Theorem: Mertens Bound Implies Riemann Hypothesis — UNCONDITIONAL): -/
theorem mertens_implies_rh (h_mertens : MertensBound) :
    RiemannHypothesis := by
  have h_nofail : ∀ s : ℂ, s.re > 1/2 → riemannZeta s ≠ 0 :=
    zero_free_re_gt_half_of_mertens h_mertens
  intro s hs_zero hs_not_triv hs_not_one
  by_contra h_ne
  rcases lt_or_gt_of_ne h_ne with hs_lt | hs_gt
  · have ⟨h_refl_zero, h_refl_gt⟩ := zeta_zero_reflection hs_zero hs_not_triv hs_not_one hs_lt
    exact h_nofail (1 - s) h_refl_gt h_refl_zero
  · exact h_nofail s hs_gt hs_zero

/-- Theorem 5.20 (Mertens-Riemann Spectral Equivalence):
Forward direction (`MertensBound → RH`) is unconditional; converse assumes `H.rh_implies_mertens_bound`. -/
theorem mertens_riemann_equivalence :
    RiemannHypothesis ↔ MertensBound :=
  ⟨RiemannBlueprint.LittlewoodConverse.rh_implies_mertens_bound, mertens_implies_rh⟩

/-- Half-plane zero-freeness of `riemannZeta` on `Re(s) > 1/2` implies `_root_.RiemannHypothesis`
via the functional-equation reflection `zeta_zero_reflection`. -/
theorem half_plane_zero_free_implies_rh
    (h_zf : ∀ s : ℂ, 1 / 2 < s.re → riemannZeta s ≠ 0) :
    RiemannHypothesis := by
  intro s hs_zero h_not_triv h_ne_one
  by_contra h_ne
  rcases lt_or_gt_of_ne h_ne with hs_lt | hs_gt
  · obtain ⟨h_refl_zero, h_refl_gt⟩ := zeta_zero_reflection hs_zero h_not_triv h_ne_one hs_lt
    exact h_zf (1 - s) h_refl_gt h_refl_zero
  · exact h_zf s hs_gt hs_zero

/-- Unconditional 4-way Littlewood (1912) / Mellin–Mertens logical equivalence:
1. `_root_.RiemannHypothesis`
2. `MertensBound` (`|M(x)| ≤ C * x^(1/2 + ε)`)
3. Half-plane zero-freeness (`∀ s, 1/2 < s.re → riemannZeta s ≠ 0`)
4. Analytic Mellin–Mertens inversion on `Re(s) > 1/2` (`∃ I_M, ...`). -/
theorem mellin_mertens_unconditional_equivalence :
    (RiemannHypothesis ↔ MertensBound) ∧
    (MertensBound ↔ ∀ s : ℂ, 1 / 2 < s.re → riemannZeta s ≠ 0) ∧
    ((∀ s : ℂ, 1 / 2 < s.re → riemannZeta s ≠ 0) ↔
      ∃ I_M : ℂ → ℂ,
        (∀ s : ℂ, 1 / 2 < s.re → s ≠ 1 → I_M s = LittlewoodForward.mellinMertens s) ∧
        ∀ s : ℂ, 1 / 2 < s.re → riemannZeta s * I_M s = 1) := by
  refine ⟨mertens_riemann_equivalence, ?_, ?_⟩
  · exact ⟨zero_free_re_gt_half_of_mertens,
      fun h_zf => mertens_riemann_equivalence.mp (half_plane_zero_free_implies_rh h_zf)⟩
  · refine ⟨fun h_zf => ?_, fun ⟨I_M, _, h_inv⟩ s hs => ne_zero_of_reciprocal_product (h_inv s hs)⟩
    have hm : MertensBound :=
      mertens_riemann_equivalence.mp (half_plane_zero_free_implies_rh h_zf)
    refine ⟨fun s => if s = 1 then (riemannZeta 1)⁻¹ else LittlewoodForward.mellinMertens s,
      ?_, ?_⟩
    · intro s _ hs_ne1
      simp [hs_ne1]
    · intro s hs
      by_cases hs1 : s = 1
      · subst hs1
        simp [mul_inv_cancel₀ (h_zf 1 (by norm_num))]
      · simp only [hs1, ↓reduceIte]
        exact LittlewoodForward.riemannZeta_mul_mellinMertens_eq_one hm s hs hs1

open Asymptotics

lemma mertens_eq_mertensReal (x : ℝ) :
    (RiemannBlueprint.mertens x : ℂ) = mertensReal x := by
  dsimp [RiemannBlueprint.mertens, mertensReal]
  push_cast
  have hIic : Finset.Iic ⌊x⌋₊ = insert 0 (Finset.Icc 1 ⌊x⌋₊) := by
    ext k
    simp only [Finset.mem_Iic, Finset.mem_insert, Finset.mem_Icc]
    omega
  rw [hIic, Finset.sum_insert (by simp)]
  simp

lemma norm_mertens_le_self (x : ℝ) (hx : 1 ≤ x) :
    |(RiemannBlueprint.mertens x : ℝ)| ≤ x := by
  have h_eq := mertens_eq_mertensReal x
  have h_norm : |(RiemannBlueprint.mertens x : ℝ)| = ‖(RiemannBlueprint.mertens x : ℂ)‖ := by
    simp [Complex.norm_intCast]
  rw [h_norm, h_eq]
  exact norm_mertensReal_le x hx

/-- Mathlib-idiomatic `=O[atTop]` asymptotic formulation of Littlewood's (1912) converse:
`_root_.RiemannHypothesis` implies `(fun x => (mertens x : ℝ)) =O[atTop] (fun x => x ^ (1/2 + ε))`
for every `ε > 0`. -/
theorem isBigO_mertens_of_rh (hRH : _root_.RiemannHypothesis) (ε : ℝ) (hε : 0 < ε) :
    (fun x : ℝ => (RiemannBlueprint.mertens x : ℝ)) =O[Filter.atTop]
      fun x => x ^ ((1 / 2 : ℝ) + ε) := by
  have hM : RiemannBlueprint.MertensBound :=
    RiemannBlueprint.LittlewoodConverse.rh_implies_mertens_bound hRH
  obtain ⟨C, _hC_pos, hC_bd⟩ := hM ε hε
  refine Asymptotics.IsBigO.of_bound C ?_
  filter_upwards [Filter.eventually_ge_atTop (1 : ℝ)] with x hx
  have hx_pos : 0 < x := zero_lt_one.trans_le hx
  have hrpow_nn : 0 ≤ x ^ ((1 / 2 : ℝ) + ε) := Real.rpow_nonneg hx_pos.le _
  rw [Real.norm_of_nonneg hrpow_nn, Real.norm_eq_abs]
  exact hC_bd x hx

lemma mertensBound_of_isBigO
    (hO : ∀ ε : ℝ, 0 < ε →
      (fun x : ℝ => (RiemannBlueprint.mertens x : ℝ)) =O[Filter.atTop]
        fun x => x ^ ((1 / 2 : ℝ) + ε)) :
    RiemannBlueprint.MertensBound := by
  intro ε hε
  have hε2 : 0 < ε / 2 := by linarith
  obtain ⟨C0, hC0⟩ := (hO (ε / 2) hε2).bound
  obtain ⟨x0, hx0⟩ := Filter.eventually_atTop.mp hC0
  set M0 : ℝ := max 1 x0
  have hM0_ge1 : 1 ≤ M0 := le_max_left 1 x0
  have hM0_pos : 0 < M0 := zero_lt_one.trans_le hM0_ge1
  set C_final : ℝ := |C0| + M0 + 1
  have hC_pos : 0 < C_final := by dsimp [C_final]; positivity
  refine ⟨C_final, hC_pos, fun x hx => ?_⟩
  have hx_pos : 0 < x := zero_lt_one.trans_le hx
  have h_rpow_pos : 0 < x ^ ((1 / 2 : ℝ) + ε) := Real.rpow_pos_of_pos hx_pos _
  have h_rpow_ge1 : 1 ≤ x ^ ((1 / 2 : ℝ) + ε) := Real.one_le_rpow hx (by linarith)
  by_cases hxM : x ≤ M0
  · have h_lin : |(RiemannBlueprint.mertens x : ℝ)| ≤ x := norm_mertens_le_self x hx
    have h_le_M0 : x ≤ M0 * x ^ ((1 / 2 : ℝ) + ε) := by
      calc x ≤ M0 := hxM
        _ = M0 * 1 := (mul_one M0).symm
        _ ≤ M0 * x ^ ((1 / 2 : ℝ) + ε) := mul_le_mul_of_nonneg_left h_rpow_ge1 hM0_pos.le
    calc |(RiemannBlueprint.mertens x : ℝ)| ≤ x := h_lin
      _ ≤ M0 * x ^ ((1 / 2 : ℝ) + ε) := h_le_M0
      _ ≤ C_final * x ^ ((1 / 2 : ℝ) + ε) := by
          refine mul_le_mul_of_nonneg_right ?_ h_rpow_pos.le
          dsimp [C_final]; linarith [abs_nonneg C0]
  · have hxM' : M0 < x := lt_of_not_ge hxM
    have hx_ge_x0 : x0 ≤ x := (le_max_right 1 x0).trans hxM'.le
    have hbd := hx0 x hx_ge_x0
    rw [Real.norm_eq_abs, Real.norm_of_nonneg (Real.rpow_nonneg hx_pos.le _)] at hbd
    have hrpow_le : x ^ ((1 / 2 : ℝ) + ε / 2) ≤ x ^ ((1 / 2 : ℝ) + ε) :=
      Real.rpow_le_rpow_of_exponent_le hx (by linarith)
    calc |(RiemannBlueprint.mertens x : ℝ)| ≤ C0 * x ^ ((1 / 2 : ℝ) + ε / 2) := hbd
      _ ≤ |C0| * x ^ ((1 / 2 : ℝ) + ε / 2) := by
          refine mul_le_mul_of_nonneg_right (le_abs_self C0) (Real.rpow_nonneg hx_pos.le _)
      _ ≤ |C0| * x ^ ((1 / 2 : ℝ) + ε) := by
          refine mul_le_mul_of_nonneg_left hrpow_le (abs_nonneg C0)
      _ ≤ C_final * x ^ ((1 / 2 : ℝ) + ε) := by
          refine mul_le_mul_of_nonneg_right ?_ h_rpow_pos.le
          dsimp [C_final]; linarith

/-- Littlewood's (1912) Bidirectional Equivalence formulated via Mathlib's `=O[atTop]` filter:
`_root_.RiemannHypothesis` holds if and only if `M(x) = O(x^(1/2 + ε))` as `x → ∞` for every `ε > 0`. -/
theorem riemannHypothesis_iff_mertens_isBigO :
    _root_.RiemannHypothesis ↔
      ∀ ε : ℝ, 0 < ε →
        (fun x : ℝ => (RiemannBlueprint.mertens x : ℝ)) =O[Filter.atTop]
          fun x => x ^ ((1 / 2 : ℝ) + ε) :=
  ⟨fun hRH ε hε => isBigO_mertens_of_rh hRH ε hε,
   fun hO => mertens_implies_rh (mertensBound_of_isBigO hO)⟩

end RiemannBlueprint.Section5_MobiusMertens
