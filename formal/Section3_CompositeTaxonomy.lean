import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.Factorization.Basic
import Mathlib.Data.Nat.Factorization.PrimePow
import Mathlib.Data.Nat.Totient
import Mathlib.Data.Finset.Card
import Mathlib.NumberTheory.ArithmeticFunction.VonMangoldt
import Mathlib.NumberTheory.ArithmeticFunction.Moebius
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Basic.Complex.Basic
import RiemannBlueprint.Section2_PrimeAtoms

/-!
# Section 3: Algebraic & Modular Taxonomy of the Composite System ℂ
Formalization of Section 3 from the monograph.
-/

namespace RiemannBlueprint.Section3_CompositeTaxonomy

open scoped ArithmeticFunction.zeta

open RiemannBlueprint.Section2_PrimeAtoms (Primes Composites)

/-- Definition 3.1: Arithmetic Factor Counting Functions ω(n) and Ω(n). -/
def omega (n : ℕ) : ℕ := n.primeFactors.card
def Omega (n : ℕ) : ℕ := n.primeFactorsList.length

/-- Definition 3.2: Pure and Mixed Composites. -/
def PureComposites : Set ℕ := { n | ∃ (p : ℕ) (k : ℕ), Nat.Prime p ∧ k ≥ 2 ∧ n = p ^ k }
def MixedComposites : Set ℕ := { n | n ∈ Composites ∧ omega n ≥ 2 }

/-- Proposition 3.3: Exact Arithmetic Classification of ℕ = {1} ∪ ℙ ∪ ℂ (mutually disjoint). -/
theorem arithmetic_classification_partition :
    Disjoint Section2_PrimeAtoms.Units Primes ∧
    Disjoint Section2_PrimeAtoms.Units Composites ∧
    Disjoint Primes Composites := by
  refine ⟨?_, ?_, ?_⟩
  · rw [Set.disjoint_iff]
    intro x ⟨hx1, hx2⟩
    have h1 : x = 1 := hx1
    have hp : Nat.Prime x := hx2
    rw [h1] at hp
    exact Nat.Prime.not_dvd_one hp (dvd_refl 1)
  · rw [Set.disjoint_iff]
    intro x ⟨hx1, hx2⟩
    have h1 : x = 1 := hx1
    have hc : x > 1 ∧ ¬ Nat.Prime x := hx2
    omega
  · rw [Set.disjoint_iff]
    intro x ⟨hx1, hx2⟩
    have hp : Nat.Prime x := hx1
    have hc : x > 1 ∧ ¬ Nat.Prime x := hx2
    exact hc.2 hp

/-- Proposition 3.4: Pure and Mixed Composites are Disjoint. -/
theorem pure_mixed_composite_partition : Disjoint PureComposites MixedComposites := by
  rw [Set.disjoint_iff]
  intro x ⟨hx_pure, hx_mixed⟩
  rcases hx_pure with ⟨p, k, hp, hk, rfl⟩
  have hk_pos : k ≠ 0 := by omega
  have h_factors : (p ^ k).primeFactors = {p} := Nat.primeFactors_prime_pow hk_pos hp
  have h_omega : omega (p ^ k) = 1 := by
    dsimp [omega]
    rw [h_factors, Finset.card_singleton]
  have h_mixed_omega : omega (p ^ k) ≥ 2 := hx_mixed.2
  omega

/-- Proposition 3.5: Isolation via the von Mangoldt function. -/
theorem von_mangoldt_isolation (n : ℕ) (hn : omega n ≥ 2) :
    ArithmeticFunction.vonMangoldt n = 0 := by
  rw [ArithmeticFunction.vonMangoldt_eq_zero_iff]
  intro h_pow
  rw [isPrimePow_iff_card_primeFactors_eq_one] at h_pow
  dsimp [omega] at hn
  omega

/-- Corollary 3.6: Divisor Count for Composites c: d(c) ≥ 3. -/
theorem divisor_count_composite (c : ℕ) (hc : c ∈ Composites) :
    c.divisors.card ≥ 3 := by
  rcases hc with ⟨hc_gt, hc_not_prime⟩
  have hc_two : 2 ≤ c := hc_gt
  have hc_ne_zero : c ≠ 0 := by omega
  have h_not_all : ¬(∀ m < c, m ∣ c → m = 1) := by
    intro h_all
    have hp : Nat.Prime c := Nat.prime_def_lt.mpr ⟨hc_two, h_all⟩
    exact hc_not_prime hp
  push Not at h_not_all
  rcases h_not_all with ⟨d, hd_lt, hd_dvd, hd_ne_one⟩
  have hd_pos : d ≠ 0 := by
    rintro rfl
    have : c = 0 := Nat.eq_zero_of_zero_dvd hd_dvd
    omega
  have hd_gt_one : 1 < d := by
    have : 1 ≤ d := Nat.pos_of_ne_zero hd_pos
    omega
  have h1 : 1 ∈ c.divisors := Nat.mem_divisors.mpr ⟨one_dvd c, hc_ne_zero⟩
  have hc_mem : c ∈ c.divisors := Nat.mem_divisors.mpr ⟨dvd_rfl, hc_ne_zero⟩
  have hd_mem : d ∈ c.divisors := Nat.mem_divisors.mpr ⟨hd_dvd, hc_ne_zero⟩
  have h_sub : {1, d, c} ⊆ c.divisors := by
    intro x hx
    simp only [Finset.mem_insert, Finset.mem_singleton] at hx
    rcases hx with rfl | rfl | rfl <;> assumption
  have h1_not_mem : 1 ∉ ({d, c} : Finset ℕ) := by
    simp only [Finset.mem_insert, Finset.mem_singleton, not_or]
    exact ⟨by omega, by omega⟩
  have hd_not_mem : d ∉ ({c} : Finset ℕ) := by
    simp only [Finset.mem_singleton]
    omega
  have h_card : ({1, d, c} : Finset ℕ).card = 3 := by
    rw [Finset.card_insert_of_notMem h1_not_mem]
    rw [Finset.card_insert_of_notMem hd_not_mem]
    rw [Finset.card_singleton]
  have := Finset.card_le_card h_sub
  omega

/-- Proposition 3.7: Prime vs. Composite Totient Gap. -/
theorem prime_vs_composite_totient_gap (c : ℕ) (hc : c ∈ Composites) :
    Nat.totient c < c - 1 := by
  rcases hc with ⟨hc_gt, hc_not_prime⟩
  have h_ne : Nat.totient c ≠ c - 1 := by
    intro h_eq
    have hp : Nat.Prime c := (Nat.totient_eq_iff_prime (by omega)).mp h_eq
    exact hc_not_prime hp
  have h_tot_lt : Nat.totient c ≤ c - 1 := Nat.le_sub_one_of_lt (Nat.totient_lt c hc_gt)
  exact lt_of_le_of_ne h_tot_lt h_ne

/-- Proposition 3.8: The Coprime Composite Lattice. -/
theorem coprime_composite_lattice (u v : ℕ) (hu : u > 1) (hv : v > 1) :
    u * v ∈ Composites := by
  refine ⟨by nlinarith, ?_⟩
  intro hp
  have h_dvd : u ∣ u * v := dvd_mul_right u v
  rcases (Nat.Prime.eq_one_or_self_of_dvd hp u h_dvd) with rfl | hu_eq
  · omega
  · have h_eq : u * v = u * 1 := by rw [mul_one, ← hu_eq]
    have : v = 1 := mul_left_cancel₀ (by omega) h_eq
    omega

/-- **Korselt Criterion Predicate** for composite odd Fermat-type pseudoprimes:
`n > 1`, `¬ Nat.Prime n`, and every prime factor `p ∣ n` satisfies `(p - 1) ∣ (n - 1)`. -/
def SatisfiesKorseltCriterion (n : ℕ) : Prop :=
  1 < n ∧ ¬ Nat.Prime n ∧ ∀ p : ℕ, Nat.Prime p → p ∣ n → (p - 1) ∣ (n - 1)

private lemma totient_three_distinct_primes (p q r : ℕ)
    (hp : Nat.Prime p) (hq : Nat.Prime q) (hr : Nat.Prime r)
    (hpq : p ≠ q) (hpr : p ≠ r) (hqr : q ≠ r) :
    Nat.totient (p * (q * r)) = (p - 1) * ((q - 1) * (r - 1)) := by
  have hcpq : Nat.Coprime p q := (hp.coprime_iff_not_dvd).mpr fun hdvd =>
    hpq ((Nat.prime_dvd_prime_iff_eq hp hq).mp hdvd)
  have hcpr : Nat.Coprime p r := (hp.coprime_iff_not_dvd).mpr fun hdvd =>
    hpr ((Nat.prime_dvd_prime_iff_eq hp hr).mp hdvd)
  have hcqr : Nat.Coprime q r := (hq.coprime_iff_not_dvd).mpr fun hdvd =>
    hqr ((Nat.prime_dvd_prime_iff_eq hq hr).mp hdvd)
  have hcp_qr : Nat.Coprime p (q * r) := hcpq.mul_right hcpr
  rw [Nat.totient_mul hcp_qr, Nat.totient_mul hcqr,
    Nat.totient_prime hp, Nat.totient_prime hq, Nat.totient_prime hr]

private lemma card_divisors_three_distinct_primes (p q r : ℕ)
    (hp : Nat.Prime p) (hq : Nat.Prime q) (hr : Nat.Prime r)
    (hpq : p ≠ q) (hpr : p ≠ r) (hqr : q ≠ r) :
    (p * (q * r)).divisors.card = 8 := by
  have hcpq : Nat.Coprime p q := (hp.coprime_iff_not_dvd).mpr fun hdvd =>
    hpq ((Nat.prime_dvd_prime_iff_eq hp hq).mp hdvd)
  have hcpr : Nat.Coprime p r := (hp.coprime_iff_not_dvd).mpr fun hdvd =>
    hpr ((Nat.prime_dvd_prime_iff_eq hp hr).mp hdvd)
  have hcqr : Nat.Coprime q r := (hq.coprime_iff_not_dvd).mpr fun hdvd =>
    hqr ((Nat.prime_dvd_prime_iff_eq hq hr).mp hdvd)
  have hcp_qr : Nat.Coprime p (q * r) := hcpq.mul_right hcpr
  rw [hcp_qr.card_divisors_mul, hcqr.card_divisors_mul,
    hp.divisors, hq.divisors, hr.divisors,
    Finset.card_pair hp.ne_one.symm, Finset.card_pair hq.ne_one.symm,
    Finset.card_pair hr.ne_one.symm]

private lemma korselt_of_three_primes (n p q r : ℕ) (hn : n = p * (q * r))
    (hp : Nat.Prime p) (hq : Nat.Prime q) (hr : Nat.Prime r)
    (hdp : (p - 1) ∣ (n - 1)) (hdq : (q - 1) ∣ (n - 1)) (hdr : (r - 1) ∣ (n - 1)) :
    ∀ x : ℕ, Nat.Prime x → x ∣ n → (x - 1) ∣ (n - 1) := by
  intro x hx hxd
  rw [hn] at hxd
  rcases hx.dvd_mul.mp hxd with hxp | hxqr
  · rw [(Nat.prime_dvd_prime_iff_eq hx hp).mp hxp]
    exact hdp
  · rcases hx.dvd_mul.mp hxqr with hxq | hxr
    · rw [(Nat.prime_dvd_prime_iff_eq hx hq).mp hxq]
      exact hdq
    · rw [(Nat.prime_dvd_prime_iff_eq hx hr).mp hxr]
      exact hdr

/-- **Korselt–Carmichael & Totient-Unmasking Theorem (`561`, `1105`, `1729`):**
Certifies unconditionally that the first three Carmichael numbers — `561 = 3 * 11 * 17`,
`1105 = 5 * 13 * 17`, and Hardy–Ramanujan's `1729 = 7 * 13 * 19 = 12^3 + 1^3 = 10^3 + 9^3` —
all lie in `Composites` and satisfy Korselt's Criterion `(p - 1) ∣ (n - 1)` for all primes `p ∣ n`,
yet are unmasked from primes by `n - φ(n) ∈ {241, 337, 433} > 1` and `d(n) - 2 = 6 > 0`. -/
theorem carmichael_korselt_and_totient_unmasking :
    (561 = 3 * 11 * 17 ∧ 561 ∈ Composites ∧ SatisfiesKorseltCriterion 561 ∧
      561 - Nat.totient 561 = 241 ∧ 1 < 561 - Nat.totient 561 ∧
      (561 : ℕ).divisors.card - 2 = 6) ∧
    (1105 = 5 * 13 * 17 ∧ 1105 ∈ Composites ∧ SatisfiesKorseltCriterion 1105 ∧
      1105 - Nat.totient 1105 = 337 ∧ 1 < 1105 - Nat.totient 1105 ∧
      (1105 : ℕ).divisors.card - 2 = 6) ∧
    (1729 = 7 * 13 * 19 ∧ 12 ^ 3 + 1 ^ 3 = 1729 ∧ 10 ^ 3 + 9 ^ 3 = 1729 ∧
      1729 ∈ Composites ∧ SatisfiesKorseltCriterion 1729 ∧
      1729 - Nat.totient 1729 = 433 ∧ 1 < 1729 - Nat.totient 1729 ∧
      (1729 : ℕ).divisors.card - 2 = 6) := by
  have h3 : Nat.Prime 3 := by decide
  have h5 : Nat.Prime 5 := by decide
  have h7 : Nat.Prime 7 := by decide
  have h11 : Nat.Prime 11 := by decide
  have h13 : Nat.Prime 13 := by decide
  have h17 : Nat.Prime 17 := by decide
  have h19 : Nat.Prime 19 := by decide
  have h561_comp : (561 : ℕ) ∈ Composites := by
    rw [show (561 : ℕ) = 3 * 187 by norm_num]
    exact coprime_composite_lattice 3 187 (by omega) (by omega)
  have h1105_comp : (1105 : ℕ) ∈ Composites := by
    rw [show (1105 : ℕ) = 5 * 221 by norm_num]
    exact coprime_composite_lattice 5 221 (by omega) (by omega)
  have h1729_comp : (1729 : ℕ) ∈ Composites := by
    rw [show (1729 : ℕ) = 7 * 247 by norm_num]
    exact coprime_composite_lattice 7 247 (by omega) (by omega)
  have h561_tot : Nat.totient 561 = 320 := by
    rw [show (561 : ℕ) = 3 * (11 * 17) by norm_num,
      totient_three_distinct_primes 3 11 17 h3 h11 h17 (by omega) (by omega) (by omega)]
  have h1105_tot : Nat.totient 1105 = 768 := by
    rw [show (1105 : ℕ) = 5 * (13 * 17) by norm_num,
      totient_three_distinct_primes 5 13 17 h5 h13 h17 (by omega) (by omega) (by omega)]
  have h1729_tot : Nat.totient 1729 = 1296 := by
    rw [show (1729 : ℕ) = 7 * (13 * 19) by norm_num,
      totient_three_distinct_primes 7 13 19 h7 h13 h19 (by omega) (by omega) (by omega)]
  have h561_div : (561 : ℕ).divisors.card = 8 := by
    rw [show (561 : ℕ) = 3 * (11 * 17) by norm_num]
    exact card_divisors_three_distinct_primes 3 11 17 h3 h11 h17 (by omega) (by omega) (by omega)
  have h1105_div : (1105 : ℕ).divisors.card = 8 := by
    rw [show (1105 : ℕ) = 5 * (13 * 17) by norm_num]
    exact card_divisors_three_distinct_primes 5 13 17 h5 h13 h17 (by omega) (by omega) (by omega)
  have h1729_div : (1729 : ℕ).divisors.card = 8 := by
    rw [show (1729 : ℕ) = 7 * (13 * 19) by norm_num]
    exact card_divisors_three_distinct_primes 7 13 19 h7 h13 h19 (by omega) (by omega) (by omega)
  have h561_kor : SatisfiesKorseltCriterion 561 :=
    ⟨by omega, h561_comp.2, korselt_of_three_primes 561 3 11 17 (by norm_num) h3 h11 h17
      ⟨280, by norm_num⟩ ⟨56, by norm_num⟩ ⟨35, by norm_num⟩⟩
  have h1105_kor : SatisfiesKorseltCriterion 1105 :=
    ⟨by omega, h1105_comp.2, korselt_of_three_primes 1105 5 13 17 (by norm_num) h5 h13 h17
      ⟨276, by norm_num⟩ ⟨92, by norm_num⟩ ⟨69, by norm_num⟩⟩
  have h1729_kor : SatisfiesKorseltCriterion 1729 :=
    ⟨by omega, h1729_comp.2, korselt_of_three_primes 1729 7 13 19 (by norm_num) h7 h13 h19
      ⟨288, by norm_num⟩ ⟨144, by norm_num⟩ ⟨96, by norm_num⟩⟩
  refine ⟨⟨by norm_num, h561_comp, h561_kor, ?_, ?_, ?_⟩,
    ⟨by norm_num, h1105_comp, h1105_kor, ?_, ?_, ?_⟩,
    ⟨by norm_num, by norm_num, by norm_num, h1729_comp, h1729_kor, ?_, ?_, ?_⟩⟩ <;> omega

/-! ### Truncated Möbius Divisor Sums -/

/-- The partial Möbius divisor sum `∑_{d ∣ n, d ≤ N} μ(d)` truncated at `N`. -/
def truncatedMoebiusDivisorSum (N n : ℕ) : ℤ :=
  ∑ d ∈ n.divisors.filter (· ≤ N), ArithmeticFunction.moebius d

/-- For `2 ≤ n ≤ N`, every divisor `d ∣ n` satisfies `d ≤ n ≤ N`,
so the truncated Möbius sum equals the complete Möbius divisor sum, which vanishes. -/
theorem truncatedMoebiusDivisorSum_eq_zero_of_le {N n : ℕ} (hn : 2 ≤ n) (hnN : n ≤ N) :
    truncatedMoebiusDivisorSum N n = 0 := by
  unfold truncatedMoebiusDivisorSum
  have hfilter : n.divisors.filter (· ≤ N) = n.divisors := by
    ext d
    simp only [Finset.mem_filter, Nat.mem_divisors, and_iff_left_iff_imp]
    rintro ⟨hd, _hn0⟩
    exact (Nat.le_of_dvd (by omega) hd).trans hnN
  rw [hfilter]
  have h_conv : (∑ d ∈ n.divisors, ArithmeticFunction.moebius d) =
      (ArithmeticFunction.moebius * ArithmeticFunction.zeta : ArithmeticFunction ℤ) n := by
    rw [ArithmeticFunction.coe_mul_zeta_apply]
  rw [h_conv, ArithmeticFunction.moebius_mul_coe_zeta]
  exact ArithmeticFunction.one_apply_ne (by omega)

/-- For prime `p > N` with `1 ≤ N`, the only divisor `d ∣ p` with `d ≤ N` is `d = 1`,
so the truncated sum equals `μ(1) = 1`. -/
theorem truncatedMoebiusDivisorSum_prime_of_lt {N p : ℕ} (hN : 1 ≤ N) (hp : p.Prime)
    (hNp : N < p) :
    truncatedMoebiusDivisorSum N p = 1 := by
  unfold truncatedMoebiusDivisorSum
  have hdiv : p.divisors = {1, p} := hp.divisors
  rw [hdiv]
  have hfilter : ({1, p} : Finset ℕ).filter (· ≤ N) = {1} := by
    ext d
    simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
    constructor
    · rintro ⟨rfl | rfl, hdN⟩
      · simp
      · omega
    · rintro rfl
      exact ⟨Or.inl rfl, hN⟩
  rw [hfilter, Finset.sum_singleton, ArithmeticFunction.moebius_apply_one]

/-- For prime powers `p^k` with `p ≤ N` and `1 ≤ k`, the only divisors `d ≤ N`
with non-zero Möbius value are `d = 1` and `d = p`, yielding `μ(1) + μ(p) = 0`. -/
theorem truncatedMoebiusDivisorSum_prime_pow_of_le {N p k : ℕ} (hp : p.Prime)
    (hk : 1 ≤ k) (hpN : p ≤ N) :
    truncatedMoebiusDivisorSum N (p ^ k) = 0 := by
  unfold truncatedMoebiusDivisorSum
  have h_full : ∑ d ∈ (p ^ k).divisors, ArithmeticFunction.moebius d = 0 := by
    have h_conv : (∑ d ∈ (p ^ k).divisors, ArithmeticFunction.moebius d) =
        (ArithmeticFunction.moebius * ArithmeticFunction.zeta : ArithmeticFunction ℤ) (p ^ k) := by
      rw [ArithmeticFunction.coe_mul_zeta_apply]
    rw [h_conv, ArithmeticFunction.moebius_mul_coe_zeta]
    have hpk_gt1 : 1 < p ^ k := Nat.one_lt_pow (by omega) hp.one_lt
    exact ArithmeticFunction.one_apply_ne hpk_gt1.ne'
  have h_split :=
    (Finset.sum_filter_add_sum_filter_not (p ^ k).divisors (· ≤ N) ArithmeticFunction.moebius).symm
  have h_tail_zero :
      ∑ d ∈ (p ^ k).divisors.filter (fun d => ¬(d ≤ N)), ArithmeticFunction.moebius d = 0 := by
    refine Finset.sum_eq_zero fun d hd => ?_
    simp only [Finset.mem_filter, Nat.mem_divisors_prime_pow hp] at hd
    rcases hd with ⟨⟨j, _hj_le, rfl⟩, hdN⟩
    have hj2 : 2 ≤ j := by
      by_contra hc
      have : j = 0 ∨ j = 1 := by omega
      rcases this with rfl | rfl
      · rw [pow_zero] at hdN
        have h1N : 1 ≤ N := (Nat.Prime.pos hp).trans_le hpN
        exact (hdN h1N).elim
      · rw [pow_one] at hdN
        exact (hdN hpN).elim
    rw [ArithmeticFunction.moebius_apply_prime_pow hp (by omega)]
    split_ifs with hj1
    · omega
    · rfl
  linarith [h_split, h_full, h_tail_zero]

/-- For distinct primes `p < q ≤ N < p * q`, all proper divisors `{1, p, q}` satisfy `≤ N`,
while `p * q > N` is excluded, giving `0 - μ(p * q) = -1`. -/
theorem truncatedMoebiusDivisorSum_mul_primes_of_lt {N p q : ℕ} (hp : p.Prime) (hq : q.Prime)
    (hpq_ne : p ≠ q) (hpN : p ≤ N) (hqN : q ≤ N) (hNpq : N < p * q) :
    truncatedMoebiusDivisorSum N (p * q) = -1 := by
  unfold truncatedMoebiusDivisorSum
  have hpq_pos : 1 < p * q := by
    have hp2 : 2 ≤ p := hp.two_le
    have hq2 : 2 ≤ q := hq.two_le
    nlinarith
  have h_full : ∑ d ∈ (p * q).divisors, ArithmeticFunction.moebius d = 0 := by
    have h_conv : (∑ d ∈ (p * q).divisors, ArithmeticFunction.moebius d) =
        (ArithmeticFunction.moebius * ArithmeticFunction.zeta : ArithmeticFunction ℤ) (p * q) := by
      rw [ArithmeticFunction.coe_mul_zeta_apply]
    rw [h_conv, ArithmeticFunction.moebius_mul_coe_zeta]
    exact ArithmeticFunction.one_apply_ne hpq_pos.ne'
  have h_split :=
    (Finset.sum_filter_add_sum_filter_not (p * q).divisors (· ≤ N) ArithmeticFunction.moebius).symm
  have h_tail_filter : (p * q).divisors.filter (fun d => ¬(d ≤ N)) = {p * q} := by
    ext d
    simp only [Finset.mem_filter, Nat.mem_divisors, Finset.mem_singleton]
    constructor
    · rintro ⟨⟨hd_dvd, _⟩, hdN⟩
      by_cases hd1 : d = 1
      · subst hd1
        have : 1 ≤ N := (Nat.Prime.pos hp).trans_le hpN
        exact (hdN this).elim
      obtain ⟨r, hr, hrd⟩ := Nat.exists_prime_and_dvd hd1
      have hr_pq : r ∣ p * q := hrd.trans hd_dvd
      rcases (Nat.Prime.dvd_mul hr).mp hr_pq with hrp | hrq
      · have hr_eq : r = p := (Nat.prime_dvd_prime_iff_eq hr hp).mp hrp
        rw [hr_eq] at hrd
        obtain ⟨m, rfl⟩ := hrd
        have hm_dvd : m ∣ q := (mul_dvd_mul_iff_left hp.ne_zero).mp hd_dvd
        rcases (Nat.dvd_prime hq).mp hm_dvd with rfl | rfl
        · rw [mul_one] at hdN
          exact (hdN hpN).elim
        · rfl
      · have hr_eq : r = q := (Nat.prime_dvd_prime_iff_eq hr hq).mp hrq
        rw [hr_eq] at hrd
        obtain ⟨m, rfl⟩ := hrd
        have hd_dvd' : q * m ∣ q * p := by rw [mul_comm q p]; exact hd_dvd
        have hm_dvd : m ∣ p := (mul_dvd_mul_iff_left hq.ne_zero).mp hd_dvd'
        rcases (Nat.dvd_prime hp).mp hm_dvd with rfl | rfl
        · rw [mul_one] at hdN
          exact (hdN hqN).elim
        · rw [mul_comm]
    · rintro rfl
      refine ⟨⟨dvd_rfl, by omega⟩, by omega⟩
  have h_tail :
      ∑ d ∈ (p * q).divisors.filter (fun d => ¬(d ≤ N)), ArithmeticFunction.moebius d = 1 := by
    rw [h_tail_filter, Finset.sum_singleton]
    have hcp : Nat.Coprime p q := (Nat.coprime_primes hp hq).mpr hpq_ne
    rw [ArithmeticFunction.isMultiplicative_moebius.map_mul_of_coprime hcp,
      ArithmeticFunction.moebius_apply_prime hp, ArithmeticFunction.moebius_apply_prime hq]
    rfl
  linarith [h_split, h_full, h_tail]

/-- For `n ≤ N`, filtering `n.divisors` by `· ≤ N` leaves all divisors of `n` intact,
so any sequence `c : ℕ → ℤ` with `c 1 = 1` whose truncated divisor sums vanish for all
`2 ≤ m ≤ N` satisfies the exact Möbius inversion identity `c n = μ(n)` for all `1 ≤ n ≤ N`. -/
theorem eq_moebius_of_truncated_divisor_sum_eq_zero {N : ℕ} {c : ℕ → ℤ}
    (hc1 : c 1 = 1)
    (hcz : ∀ m, 2 ≤ m → m ≤ N → ∑ d ∈ m.divisors.filter (· ≤ N), c d = 0)
    {n : ℕ} (hn1 : 1 ≤ n) (hnN : n ≤ N) :
    c n = ArithmeticFunction.moebius n := by
  revert hn1 hnN
  refine Nat.strong_induction_on n fun k ih hk1 hkN => ?_
  by_cases hk : k = 1
  · subst hk
    rw [hc1, ArithmeticFunction.moebius_apply_one]
  · have hk2 : 2 ≤ k := by omega
    have hdN : ∀ d ∈ k.divisors, d ≤ N :=
      fun d hd => (Nat.le_of_dvd (by omega) (Nat.dvd_of_mem_divisors hd)).trans hkN
    have hfilter : k.divisors.filter (· ≤ N) = k.divisors := by
      ext d
      simp only [Finset.mem_filter, and_iff_left_iff_imp]
      exact hdN d
    have hsum_c : ∑ d ∈ k.divisors, c d = 0 := by
      have h0 := hcz k hk2 hkN
      rwa [hfilter] at h0
    have hk_mem : k ∈ k.divisors := Nat.mem_divisors.mpr ⟨dvd_rfl, by omega⟩
    have hsplit_c : ∑ d ∈ k.divisors, c d = c k + ∑ d ∈ k.divisors.erase k, c d :=
      (Finset.add_sum_erase k.divisors c hk_mem).symm
    have hc_k : c k = - ∑ d ∈ k.divisors.erase k, c d := by
      rw [hsplit_c] at hsum_c
      calc c k = (c k + ∑ d ∈ k.divisors.erase k, c d) - ∑ d ∈ k.divisors.erase k, c d := by ring
        _ = 0 - ∑ d ∈ k.divisors.erase k, c d := by rw [hsum_c]
        _ = - ∑ d ∈ k.divisors.erase k, c d := by ring
    have h_conv : (∑ d ∈ k.divisors, ArithmeticFunction.moebius d) =
        (ArithmeticFunction.moebius * ArithmeticFunction.zeta : ArithmeticFunction ℤ) k := by
      rw [ArithmeticFunction.coe_mul_zeta_apply]
    have h_mu_zero : (∑ d ∈ k.divisors, ArithmeticFunction.moebius d) = 0 := by
      rw [h_conv, ArithmeticFunction.moebius_mul_coe_zeta]
      have : k ≠ 1 := by omega
      simp [this]
    have hsplit_mu : ∑ d ∈ k.divisors, ArithmeticFunction.moebius d =
        ArithmeticFunction.moebius k + ∑ d ∈ k.divisors.erase k, ArithmeticFunction.moebius d :=
      (Finset.add_sum_erase k.divisors ArithmeticFunction.moebius hk_mem).symm
    have hmu_k : ArithmeticFunction.moebius k =
        - ∑ d ∈ k.divisors.erase k, ArithmeticFunction.moebius d := by
      rw [hsplit_mu] at h_mu_zero
      calc ArithmeticFunction.moebius k =
          (ArithmeticFunction.moebius k +
            ∑ d ∈ k.divisors.erase k, ArithmeticFunction.moebius d) -
            ∑ d ∈ k.divisors.erase k, ArithmeticFunction.moebius d := by ring
        _ = 0 - ∑ d ∈ k.divisors.erase k, ArithmeticFunction.moebius d := by rw [h_mu_zero]
        _ = - ∑ d ∈ k.divisors.erase k, ArithmeticFunction.moebius d := by ring
    have h_erase_eq : ∑ d ∈ k.divisors.erase k, c d =
        ∑ d ∈ k.divisors.erase k, ArithmeticFunction.moebius d := by
      refine Finset.sum_congr rfl fun d hd => ?_
      simp only [Finset.mem_erase, Nat.mem_divisors] at hd
      rcases hd with ⟨hd_ne, hd_dvd, -⟩
      have hd_pos : 1 ≤ d := Nat.pos_of_dvd_of_pos hd_dvd (by omega)
      have hd_lt : d < k := Nat.lt_of_le_of_ne (Nat.le_of_dvd (by omega) hd_dvd) hd_ne
      have hdN_le : d ≤ N := hd_lt.le.trans hkN
      exact ih d hd_lt hd_pos hdN_le
    rw [hc_k, h_erase_eq, ← hmu_k]

/-- Pairing `k = 1` and `k = 2` (`N = 2`) annihilates the truncated Möbius divisor jump
at every positive even integer `2 * m` (`m ≥ 1`), even when `2 * m > 2`. -/
theorem truncatedMoebiusDivisorSum_two_mul {m : ℕ} (hm : 1 ≤ m) :
    truncatedMoebiusDivisorSum 2 (2 * m) = 0 := by
  unfold truncatedMoebiusDivisorSum
  have hfilt : (2 * m).divisors.filter (· ≤ 2) = {1, 2} := by
    ext d
    simp only [Finset.mem_filter, Nat.mem_divisors, Finset.mem_insert, Finset.mem_singleton]
    constructor
    · rintro ⟨⟨hd_dvd, h2m_ne⟩, hd2⟩
      have hd_pos : 1 ≤ d := Nat.pos_of_dvd_of_pos hd_dvd (by omega)
      omega
    · rintro (rfl | rfl)
      · exact ⟨⟨one_dvd _, by omega⟩, by omega⟩
      · exact ⟨⟨dvd_mul_right 2 m, by omega⟩, le_rfl⟩
  rw [hfilt, Finset.sum_pair (by decide), ArithmeticFunction.moebius_apply_one,
    ArithmeticFunction.moebius_apply_prime Nat.prime_two]
  ring

/-- For any odd integer `n` (`n % 2 = 1`), the only divisor `d ∣ n` with `d ≤ 2` is `d = 1`,
so `truncatedMoebiusDivisorSum 2 n` equals `truncatedMoebiusDivisorSum 2 1 = 1`.
In particular, once `k = 2` cancels all even jumps, the unit jump at `1` reappears
identically at `3` and every odd prime `p ≥ 3`. -/
theorem truncatedMoebiusDivisorSum_two_of_odd {n : ℕ} (hn : n % 2 = 1) :
    truncatedMoebiusDivisorSum 2 n = 1 := by
  unfold truncatedMoebiusDivisorSum
  have hfilt : n.divisors.filter (· ≤ 2) = {1} := by
    ext d
    simp only [Finset.mem_filter, Nat.mem_divisors, Finset.mem_singleton]
    constructor
    · rintro ⟨⟨hd_dvd, hn_ne⟩, hd2⟩
      have hd_pos : 1 ≤ d := Nat.pos_of_dvd_of_pos hd_dvd (Nat.pos_of_ne_zero hn_ne)
      by_cases hd_eq2 : d = 2
      · subst hd_eq2
        obtain ⟨k, rfl⟩ := hd_dvd
        omega
      · omega
    · rintro rfl
      exact ⟨⟨one_dvd _, by omega⟩, by omega⟩
  rw [hfilt, Finset.sum_singleton, ArithmeticFunction.moebius_apply_one]

/-- On the interior range `1 ≤ n ≤ N`, the truncated Möbius divisor sum equals `1` at `n = 1`
and `0` for all `2 ≤ n ≤ N`, matching the multiplicative identity of Dirichlet convolution. -/
theorem truncatedMoebiusDivisorSum_eq_ite {N n : ℕ} (hn1 : 1 ≤ n) (hnN : n ≤ N) :
    truncatedMoebiusDivisorSum N n = if n = 1 then 1 else 0 := by
  by_cases hn : n = 1
  · subst hn
    unfold truncatedMoebiusDivisorSum
    have h1 : (1 : ℕ).divisors.filter (· ≤ N) = {1} := by
      ext d
      simp only [Finset.mem_filter, Nat.divisors_one, Finset.mem_singleton]
      constructor
      · rintro ⟨rfl, -⟩; rfl
      · rintro rfl; exact ⟨rfl, hnN⟩
    rw [h1, Finset.sum_singleton, ArithmeticFunction.moebius_apply_one]
    simp only [↓reduceIte]
  · simp only [hn, ↓reduceIte]
    have hn2 : 2 ≤ n := by omega
    exact truncatedMoebiusDivisorSum_eq_zero_of_le hn2 hnN

/-- Bridge between Identity #1 and Identity #2 of Zero: for any complex weight function
`w : ℕ → ℂ` (such as `n ↦ (n : ℂ) ^ (-s)`), summing the truncated Möbius divisor jumps
weighted by `w n` across the interior regime `1 ≤ n ≤ N` collapses all terms `2 ≤ n ≤ N`
to zero and isolates `w 1`. -/
theorem sum_Icc_truncatedMoebiusDivisorSum_mul {N : ℕ} (hN : 1 ≤ N) (w : ℕ → ℂ) :
    ∑ n ∈ Finset.Icc 1 N, (truncatedMoebiusDivisorSum N n : ℂ) * w n = w 1 := by
  have h1_mem : 1 ∈ Finset.Icc 1 N := Finset.mem_Icc.mpr ⟨le_rfl, hN⟩
  have h_split := Finset.add_sum_erase (Finset.Icc 1 N)
    (fun n => (truncatedMoebiusDivisorSum N n : ℂ) * w n) h1_mem
  have h_tail_zero :
      ∑ n ∈ (Finset.Icc 1 N).erase 1, (truncatedMoebiusDivisorSum N n : ℂ) * w n = 0 := by
    refine Finset.sum_eq_zero fun n hn => ?_
    simp only [Finset.mem_erase, Finset.mem_Icc] at hn
    rcases hn with ⟨hn_ne, hn1, hnN⟩
    rw [truncatedMoebiusDivisorSum_eq_ite hn1 hnN]
    simp only [hn_ne, ↓reduceIte]
    push_cast
    ring
  rw [h_tail_zero, add_zero] at h_split
  have h1_val : (truncatedMoebiusDivisorSum N 1 : ℂ) * w 1 = w 1 := by
    rw [truncatedMoebiusDivisorSum_eq_ite le_rfl hN]
    simp only [↓reduceIte]
    push_cast
    ring
  rw [← h_split, h1_val]

/-- Bridge lemma: Local jump-zero cancellation on divisors forces the Dirichlet polynomial
coefficients to match the Möbius arithmetic function up to the truncation boundary `N`. -/
theorem truncated_dirichlet_inverse_bridge (N : ℕ) (c : ℕ → ℂ) (hc1 : c 1 = 1)
    (hc : ∀ n, 2 ≤ n → n ≤ N → ∑ d ∈ n.divisors.filter (· ≤ N), c d = 0) :
    ∀ n, 1 ≤ n → n ≤ N → c n = (ArithmeticFunction.moebius n : ℂ) := by
  intro n
  refine Nat.strong_induction_on n fun n ih => ?_
  intro hn1 hnN
  by_cases hn2 : n = 1
  · subst hn2
    rw [hc1, ArithmeticFunction.moebius_apply_one]
    push_cast
    rfl
  · have hn_ge2 : 2 ≤ n := by omega
    have hdN : ∀ d ∈ n.divisors, d ≤ N :=
      fun d hd => (Nat.le_of_dvd (by omega) (Nat.dvd_of_mem_divisors hd)).trans hnN
    have hfilter : n.divisors.filter (· ≤ N) = n.divisors := by
      ext d
      simp only [Finset.mem_filter, and_iff_left_iff_imp]
      exact hdN d
    have hsum_c : ∑ d ∈ n.divisors, c d = 0 := by
      have h0 := hc n hn_ge2 hnN
      rwa [hfilter] at h0
    have hn_mem : n ∈ n.divisors := Nat.mem_divisors.mpr ⟨dvd_rfl, by omega⟩
    have hsplit_c : ∑ d ∈ n.divisors, c d = c n + ∑ d ∈ n.divisors.erase n, c d :=
      (Finset.add_sum_erase n.divisors c hn_mem).symm
    have hc_n : c n = - ∑ d ∈ n.divisors.erase n, c d := by
      rw [hsplit_c] at hsum_c
      calc c n = (c n + ∑ d ∈ n.divisors.erase n, c d) - ∑ d ∈ n.divisors.erase n, c d := by ring
        _ = 0 - ∑ d ∈ n.divisors.erase n, c d := by rw [hsum_c]
        _ = - ∑ d ∈ n.divisors.erase n, c d := by ring
    have h_conv : (∑ d ∈ n.divisors, ArithmeticFunction.moebius d) =
        (ArithmeticFunction.moebius * ArithmeticFunction.zeta : ArithmeticFunction ℤ) n := by
      rw [ArithmeticFunction.coe_mul_zeta_apply]
    have h_mu_zero_int : (∑ d ∈ n.divisors, ArithmeticFunction.moebius d) = 0 := by
      rw [h_conv, ArithmeticFunction.moebius_mul_coe_zeta]
      have : n ≠ 1 := by omega
      simp [this]
    have h_mu_zero : (∑ d ∈ n.divisors, (ArithmeticFunction.moebius d : ℂ)) = 0 := by
      have : (∑ d ∈ n.divisors, (ArithmeticFunction.moebius d : ℂ)) =
          ↑(∑ d ∈ n.divisors, ArithmeticFunction.moebius d) := by
        push_cast
        rfl
      rw [this, h_mu_zero_int, Int.cast_zero]
    have hsplit_mu : ∑ d ∈ n.divisors, (ArithmeticFunction.moebius d : ℂ) =
        (ArithmeticFunction.moebius n : ℂ) +
          ∑ d ∈ n.divisors.erase n, (ArithmeticFunction.moebius d : ℂ) :=
      (Finset.add_sum_erase n.divisors (fun d => (ArithmeticFunction.moebius d : ℂ)) hn_mem).symm
    have hmu_n : (ArithmeticFunction.moebius n : ℂ) =
        - ∑ d ∈ n.divisors.erase n, (ArithmeticFunction.moebius d : ℂ) := by
      rw [hsplit_mu] at h_mu_zero
      calc (ArithmeticFunction.moebius n : ℂ) =
          ((ArithmeticFunction.moebius n : ℂ) +
            ∑ d ∈ n.divisors.erase n, (ArithmeticFunction.moebius d : ℂ)) -
            ∑ d ∈ n.divisors.erase n, (ArithmeticFunction.moebius d : ℂ) := by ring
        _ = 0 - ∑ d ∈ n.divisors.erase n, (ArithmeticFunction.moebius d : ℂ) := by rw [h_mu_zero]
        _ = - ∑ d ∈ n.divisors.erase n, (ArithmeticFunction.moebius d : ℂ) := by ring
    have h_erase_eq : ∑ d ∈ n.divisors.erase n, c d =
        ∑ d ∈ n.divisors.erase n, (ArithmeticFunction.moebius d : ℂ) := by
      refine Finset.sum_congr rfl fun d hd => ?_
      simp only [Finset.mem_erase, Nat.mem_divisors] at hd
      rcases hd with ⟨hd_ne, hd_dvd, -⟩
      have hd_pos : 1 ≤ d := Nat.pos_of_dvd_of_pos hd_dvd (by omega)
      have hd_lt : d < n := Nat.lt_of_le_of_ne (Nat.le_of_dvd (by omega) hd_dvd) hd_ne
      have hdN_le : d ≤ N := hd_lt.le.trans hnN
      exact ih d hd_lt hd_pos hdN_le
    rw [hc_n, h_erase_eq, ← hmu_n]

/-- Convolution bridge: Local jump-zero cancellation on divisors forces the truncated Dirichlet
product to match the identity arithmetic function `1 = μ * ζ` up to `N`. -/
theorem truncated_dirichlet_convolution_bridge (N : ℕ) (c : ℕ → ℂ) (hc1 : c 1 = 1)
    (hc : ∀ n, 2 ≤ n → n ≤ N → ∑ d ∈ n.divisors.filter (· ≤ N), c d = 0) :
    ∀ n, 1 ≤ n → n ≤ N →
      ∑ d ∈ n.divisors.filter (· ≤ N), c d =
        ((1 : ArithmeticFunction ℂ) n) := by
  intro n hn1 hnN
  by_cases hn2 : n = 1
  · subst hn2
    have h1 : (1 : ℕ).divisors.filter (· ≤ N) = {1} := by
      ext d
      simp only [Finset.mem_filter, Nat.divisors_one, Finset.mem_singleton]
      constructor
      · rintro ⟨rfl, -⟩; rfl
      · rintro rfl; exact ⟨rfl, hnN⟩
    rw [h1, Finset.sum_singleton, hc1]
    simp
  · have hn_ge2 : 2 ≤ n := by omega
    have h0 := hc n hn_ge2 hnN
    rw [h0]
    have hne : n ≠ 1 := by omega
    simp [hne]

end RiemannBlueprint.Section3_CompositeTaxonomy
