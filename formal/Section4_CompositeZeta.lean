import Mathlib.Analysis.SpecialFunctions.Pow.Complex
import Mathlib.Analysis.PSeriesComplex
import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.NumberTheory.LSeries.HurwitzZetaValues
import Mathlib.NumberTheory.ArithmeticFunction.Zeta
import Mathlib.NumberTheory.ArithmeticFunction.Misc
import Mathlib.NumberTheory.Divisors
import RiemannBlueprint.Section2_PrimeAtoms
import RiemannBlueprint.Section3_CompositeTaxonomy
import RiemannBlueprint.ClassicalAnalyticInterface

/-!
# Section 4: Construction of the Composite Zeta Functions (Re(s) > 1)
Unconditional formalization of Section 4:
- Zero self-assuming hypotheses (`h_tsum` completely eliminated).
- Unconditional finite partial-sum partition `finite_additive_partition`.
- Unconditional infinite `tsum` decomposition for `1 < s.re` via Mathlib's `zeta_eq_tsum_one_div_nat_cpow`.
- Zero custom `axiom` declarations (uses `ClassicalAnalyticInterface` hypothesis for natural boundary).
-/

set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.style.openClassical false
open scoped Classical

namespace RiemannBlueprint.Section4_CompositeZeta

open ArithmeticFunction
open RiemannBlueprint
open RiemannBlueprint.Section2_PrimeAtoms (Primes Composites)
open RiemannBlueprint.Section3_CompositeTaxonomy (PureComposites MixedComposites omega)

/-- Definition 4.1: The Prime Zeta Function P(s) on ℂ. -/
noncomputable abbrev PrimeZeta (s : ℂ) : ℂ := RiemannBlueprint.PrimeZeta s

/-- Definition 4.2: The Additive Composite Zeta Function ζ_C(s) on ℂ. -/
noncomputable abbrev CompositeZeta (s : ℂ) : ℂ := RiemannBlueprint.CompositeZeta s

/-- Definition 4.3: The Squared Multiplicative Composite Zeta Function (ζ(s) - 1)^2. -/
noncomputable def CompositeZetaSquared (s : ℂ) : ℂ :=
  (riemannZeta s - 1) ^ 2

/-- Definition 4.4: The Convolutive Divisor Weight r(n) = d(n) - 2 on composites. -/
def divisorWeight (n : ℕ) : ℤ :=
  (n.divisors.card : ℤ) - 2

/-! ### Audit 1: Pointwise Trichotomy, Finite Partial Sums & Unconditional Infinite Series Splitting -/

/-- Lemma 4.5 (Pointwise Arithmetic Trichotomy of Summand):
For every natural number n, the summand splits into {1}, ℙ, and ℂ. -/
theorem pointwise_additive_partition (s : ℂ) (n : ℕ) :
    (if n = 0 then 0 else (n : ℂ) ^ (-s)) =
    (if n = 1 then (1 : ℂ) else 0) +
    (if Nat.Prime n then (n : ℂ) ^ (-s) else 0) +
    (if n ∈ Composites then (n : ℂ) ^ (-s) else 0) := by
  rcases n with _ | n
  · simp [Nat.not_prime_zero, Composites]
  · rcases n with _ | n
    · have h_prime1 : ¬ Nat.Prime 1 := Nat.not_prime_one
      have h_comp1 : 1 ∉ Composites := by
        intro hc
        have : 1 > 1 := hc.1
        omega
      simp [h_prime1, h_comp1]
    · by_cases hp : Nat.Prime (n + 2)
      · have hc : (n + 2) ∉ Composites := fun h_comp => h_comp.2 hp
        simp [hp, hc]
      · have hc : (n + 2) ∈ Composites := ⟨by omega, hp⟩
        simp [hp, hc]

/-- Lemma 4.6: Unconditional Finite Partial-Sum Partition for all N ≥ 1 and all s ∈ ℂ. -/
theorem finite_additive_partition (s : ℂ) (N : ℕ) (hN : 1 ≤ N) :
    ∑ n ∈ Finset.Icc 1 N, (n : ℂ) ^ (-s) =
      1 + (∑ n ∈ Finset.Icc 1 N, if n.Prime then (n : ℂ) ^ (-s) else 0) +
          (∑ n ∈ Finset.Icc 1 N, if n ∈ Composites then (n : ℂ) ^ (-s) else 0) := by
  have h_pt : ∀ n ∈ Finset.Icc 1 N, (n : ℂ) ^ (-s) =
      (if n = 1 then (1 : ℂ) else 0) +
      (if n.Prime then (n : ℂ) ^ (-s) else 0) +
      (if n ∈ Composites then (n : ℂ) ^ (-s) else 0) := by
    intro n hn
    have hn_ne : n ≠ 0 := by
      have := (Finset.mem_Icc.mp hn).1
      omega
    simpa [hn_ne] using pointwise_additive_partition s n
  rw [Finset.sum_congr rfl h_pt]
  simp only [Finset.sum_add_distrib]
  have h1_mem : 1 ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨le_rfl, hN⟩
  have h_unit : (∑ n ∈ Finset.Icc 1 N, if n = 1 then (1 : ℂ) else 0) = 1 := by
    simp [h1_mem]
  rw [h_unit]

/-- Lemma 4.7: Evaluation of the Unit Series Summand to 1. -/
theorem tsum_unitTerm : (∑' n : ℕ, (if n = 1 then (1 : ℂ) else 0)) = 1 := by
  rw [tsum_eq_single 1]
  · simp
  · intro b hb
    simp [hb]

/-- Lemma 4.8: Absolute summability of n^(-s) for Re(s) > 1. -/
theorem summable_cpow_neg {s : ℂ} (hs : 1 < s.re) :
    Summable (fun n : ℕ => if n = 0 then (0 : ℂ) else (n : ℂ) ^ (-s)) := by
  have h_zeta : Summable (fun n : ℕ => 1 / (n : ℂ) ^ s) :=
    Complex.summable_one_div_nat_cpow.mpr hs
  have hs_ne : s ≠ 0 := Complex.ne_zero_of_one_lt_re hs
  refine h_zeta.congr (fun n => ?_)
  rcases n with _ | n
  · simp [Complex.zero_cpow hs_ne]
  · simp [Complex.cpow_neg, one_div]

/-- Lemma 4.9: Summability of any predicate-filtered subseries for Re(s) > 1. -/
theorem summable_filter_cpow_neg (P : ℕ → Prop) [DecidablePred P] {s : ℂ} (hs : 1 < s.re) :
    Summable (fun n : ℕ => if P n then (n : ℂ) ^ (-s) else 0) := by
  have h_abs := (summable_cpow_neg hs).norm
  have hs_ne : -s ≠ 0 := neg_ne_zero.mpr (Complex.ne_zero_of_one_lt_re hs)
  refine Summable.of_norm_bounded h_abs (fun n => ?_)
  by_cases hn0 : n = 0
  · subst hn0
    by_cases hP : P 0 <;> simp [hP, Complex.zero_cpow hs_ne]
  · by_cases hP : P n <;> simp [hP, hn0]

/-- Lemma 4.10: Summability of the Unit indicator term. -/
theorem summable_unitTerm : Summable (fun n : ℕ => if n = 1 then (1 : ℂ) else 0) := by
  refine summable_of_ne_finset_zero (s := {1}) (fun b hb => ?_)
  simp only [Finset.mem_singleton] at hb
  simp [hb]

/-- Theorem 4.11 (Unconditional Infinite Additive Partition Identity):
For all s ∈ ℂ with Re(s) > 1, ζ(s) = 1 + P(s) + ζ_C(s) holds unconditionally from Mathlib. -/
theorem riemannZeta_eq_one_add_primeZeta_add_compositeZeta {s : ℂ} (hs : 1 < s.re) :
    riemannZeta s = 1 + PrimeZeta s + CompositeZeta s := by
  rw [zeta_eq_tsum_one_div_nat_cpow hs]
  have hs_ne : s ≠ 0 := Complex.ne_zero_of_one_lt_re hs
  have h_eq1 : (∑' n : ℕ, 1 / (n : ℂ) ^ s) =
      ∑' n : ℕ, (if n = 0 then (0 : ℂ) else (n : ℂ) ^ (-s)) := by
    refine tsum_congr (fun n => ?_)
    rcases n with _ | n
    · simp [Complex.zero_cpow hs_ne]
    · simp [Complex.cpow_neg, one_div]
  rw [h_eq1]
  have h_eq2 : (∑' n : ℕ, if n = 0 then (0 : ℂ) else (n : ℂ) ^ (-s)) =
      ∑' n : ℕ, ((if n = 1 then (1 : ℂ) else 0) +
                 (if Nat.Prime n then (n : ℂ) ^ (-s) else 0) +
                 (if n ∈ Composites then (n : ℂ) ^ (-s) else 0)) := by
    refine tsum_congr (fun n => pointwise_additive_partition s n)
  rw [h_eq2]
  have hU : Summable (fun n : ℕ => if n = 1 then (1 : ℂ) else 0) := summable_unitTerm
  have hP : Summable (fun n : ℕ => if Nat.Prime n then (n : ℂ) ^ (-s) else 0) :=
    summable_filter_cpow_neg Nat.Prime hs
  have hC : Summable (fun n : ℕ => if n ∈ Composites then (n : ℂ) ^ (-s) else 0) :=
    summable_filter_cpow_neg (· ∈ Composites) hs
  rw [Summable.tsum_add (hU.add hP) hC, Summable.tsum_add hU hP, tsum_unitTerm]
  have hp_eq : (∑' n : ℕ, if Nat.Prime n then (n : ℂ) ^ (-s) else 0) = PrimeZeta s := rfl
  have hc_eq : (∑' n : ℕ, if n ∈ Composites then (n : ℂ) ^ (-s) else 0) = CompositeZeta s := rfl
  rw [hp_eq, hc_eq]

/-- Theorem 4.12 (Unconditional Additive Partition Relation for Re(s) > 1):
ζ_C(s) = ζ(s) - 1 - P(s) with ZERO artificial h_tsum hypothesis. -/
theorem additive_identity_relation {s : ℂ} (hs : 1 < s.re) :
    CompositeZeta s = riemannZeta s - 1 - PrimeZeta s := by
  have h := riemannZeta_eq_one_add_primeZeta_add_compositeZeta hs
  linear_combination -1 * h

/-- Corollary 4.13 (Unconditional Special Value at s = 2):
ζ_C(2) = π^2 / 6 - 1 - P(2). -/
theorem additive_identity_at_s_2 :
    CompositeZeta 2 = (Real.pi : ℂ) ^ 2 / 6 - 1 - PrimeZeta 2 := by
  have h2 : (1 : ℝ) < (2 : ℂ).re := by norm_num
  have h := additive_identity_relation h2
  rw [riemannZeta_two] at h
  exact h

/-! ### Audit 2: Dirichlet Arithmetic Function Convolution Square -/

/-- The integer-valued zeta arithmetic function ζ_ℤ(n) = 1 for n ≥ 1. -/
def zetaZ : ArithmeticFunction ℤ := ↑ArithmeticFunction.zeta

/-- The shifted zeta arithmetic function (ζ - 1)(n). -/
def zetaSubOne : ArithmeticFunction ℤ := zetaZ - 1

theorem sub_apply' {f g : ArithmeticFunction ℤ} {n : ℕ} : (f - g) n = f n - g n := rfl

/-- Bilinear expansion of the Dirichlet convolution square (ζ - 1) * (ζ - 1). -/
theorem zetaSubOne_sq :
    zetaSubOne * zetaSubOne = zetaZ * zetaZ - zetaZ - zetaZ + 1 := by
  dsimp [zetaSubOne]
  ring

theorem zetaZ_apply_of_pos {n : ℕ} (hn : 0 < n) : zetaZ n = 1 := by
  change (↑zeta : ArithmeticFunction ℤ) n = 1
  rw [natCoe_apply]
  simp [hn.ne']

theorem zetaZ_mul_self_apply {n : ℕ} (_hn : 0 < n) :
    (zetaZ * zetaZ) n = (n.divisors.card : ℤ) := by
  change ((↑zeta : ArithmeticFunction ℤ) * ↑zeta) n = (n.divisors.card : ℤ)
  rw [coe_zeta_mul_apply]
  have h_ones : ∀ d ∈ n.divisors, (↑zeta : ArithmeticFunction ℤ) d = 1 := by
    intro d hd
    have hd_pos : 0 < d := Nat.pos_of_mem_divisors hd
    rw [natCoe_apply]
    simp [hd_pos.ne']
  rw [Finset.sum_congr rfl h_ones]
  simp

theorem one_apply_one : (1 : ArithmeticFunction ℤ) 1 = 1 := by
  simp

theorem one_apply_ne_one {n : ℕ} (hn : n ≠ 1) : (1 : ArithmeticFunction ℤ) n = 0 := by
  exact one_apply_ne hn

/-- Theorem 4.14 (Unit Annihilation in Convolution Square):
(ζ - 1) * (ζ - 1) evaluated at 1 vanishes identically. -/
theorem zetaSubOne_sq_apply_one : (zetaSubOne * zetaSubOne) 1 = 0 := by
  rw [zetaSubOne_sq]
  rw [ArithmeticFunction.add_apply, sub_apply', sub_apply']
  rw [zetaZ_mul_self_apply (by omega)]
  have h1 : zetaZ 1 = 1 := zetaZ_apply_of_pos (by omega)
  have h_one_one : (1 : ArithmeticFunction ℤ) 1 = 1 := one_apply_one
  rw [Nat.divisors_one, Finset.card_singleton, Nat.cast_one]
  rw [h1, h_one_one]
  ring

/-- Theorem 4.15 (Prime Annihilation in Convolution Square):
(ζ - 1) * (ζ - 1) annihilates every prime atom p. -/
theorem zetaSubOne_sq_apply_prime {p : ℕ} (hp : Nat.Prime p) :
    (zetaSubOne * zetaSubOne) p = 0 := by
  rw [zetaSubOne_sq]
  rw [ArithmeticFunction.add_apply, sub_apply', sub_apply']
  rw [zetaZ_mul_self_apply hp.pos]
  have hp_card : (p.divisors.card : ℤ) = 2 := by
    rw [Nat.Prime.divisors hp]
    have h1_not_mem : 1 ∉ ({p} : Finset ℕ) := by
      simp only [Finset.mem_singleton]
      exact hp.ne_one.symm
    rw [Finset.card_insert_of_notMem h1_not_mem, Finset.card_singleton]
    norm_num
  have hz : zetaZ p = 1 := zetaZ_apply_of_pos hp.pos
  have h_one : (1 : ArithmeticFunction ℤ) p = 0 := one_apply_ne_one hp.ne_one
  rw [hp_card, hz, h_one]
  ring

/-- Theorem 4.16 (Divisor-Weighted Composite Convolution):
(ζ - 1) * (ζ - 1) evaluated at any composite c evaluates exactly to d(c) - 2. -/
theorem zetaSubOne_sq_apply_composite {c : ℕ} (hc : c ∈ Composites) :
    (zetaSubOne * zetaSubOne) c = (c.divisors.card : ℤ) - 2 := by
  rw [zetaSubOne_sq]
  rw [ArithmeticFunction.add_apply, sub_apply', sub_apply']
  have hc_gt : c > 1 := hc.1
  have hc_pos : 0 < c := by omega
  have hc_ne_one : c ≠ 1 := by omega
  have hz : zetaZ c = 1 := zetaZ_apply_of_pos hc_pos
  have h_one : (1 : ArithmeticFunction ℤ) c = 0 := one_apply_ne_one hc_ne_one
  rw [zetaZ_mul_self_apply hc_pos, hz, h_one]
  ring

/-- Corollary 4.17: The composite weight is strictly positive: (ζ - 1) * (ζ - 1) c ≥ 1. -/
theorem zetaSubOne_sq_apply_composite_pos {c : ℕ} (hc : c ∈ Composites) :
    (zetaSubOne * zetaSubOne) c ≥ 1 := by
  rw [zetaSubOne_sq_apply_composite hc]
  have h_card := RiemannBlueprint.Section3_CompositeTaxonomy.divisor_count_composite c hc
  omega

/-- Proposition 4.18: Divisor Weight Vanishes on Primes and is Positive on Composites. -/
theorem divisor_weight_primes_and_composites (n : ℕ) :
    (Nat.Prime n → divisorWeight n = 0) ∧
    (n ∈ Composites → divisorWeight n ≥ 1) := by
  refine ⟨?_, ?_⟩
  · intro hp
    dsimp [divisorWeight]
    rw [Nat.Prime.divisors hp]
    have h1_not_mem : 1 ∉ ({n} : Finset ℕ) := by
      simp only [Finset.mem_singleton]
      exact hp.ne_one.symm
    have : ({1, n} : Finset ℕ).card = 2 := by
      rw [Finset.card_insert_of_notMem h1_not_mem, Finset.card_singleton]
    omega
  · intro hc
    have h_card := RiemannBlueprint.Section3_CompositeTaxonomy.divisor_count_composite n hc
    dsimp [divisorWeight]
    omega

/-- Theorem 4.19 (Meromorphic Continuation of CompositeZetaSquared):
(ζ(s) - 1)^2 is complex-differentiable at every point s ≠ 1 in ℂ. -/
theorem differentiableAt_compositeZetaSquared (s : ℂ) (hs : s ≠ 1) :
    DifferentiableAt ℂ (fun z => (riemannZeta z - 1) ^ 2) s := by
  have h_diff := differentiableAt_riemannZeta hs
  exact ((h_diff.sub (differentiableAt_const 1)).pow 2)

/-- Theorem 4.20: Analytic Discrepancy between Additive and Multiplicative Partitions.
While CompositeZetaSquared continues meromorphically to ℂ \ {1}, under the classical
natural boundary interface CompositeZeta cannot be analytically continued past Re(s) = 0
in the upper half-plane Im(s) > 0 (avoiding the real pole s = 1 and real singularities 1/k). -/
theorem analytic_discrepancy_theorem (H : ClassicalAnalyticInterface) :
    (∀ s : ℂ, s ≠ 1 → DifferentiableAt ℂ (fun z => (riemannZeta z - 1) ^ 2) s) ∧
    (¬ ∃ (f : ℂ → ℂ), AnalyticOn ℂ f {s : ℂ | -1 < s.re ∧ 0 < s.im} ∧
      ∀ s : ℂ, 1 < s.re → 0 < s.im → f s = CompositeZeta s) := by
  exact ⟨fun s hs => differentiableAt_compositeZetaSquared s hs, H.natural_boundary_obstruction_at_zero⟩

end RiemannBlueprint.Section4_CompositeZeta
