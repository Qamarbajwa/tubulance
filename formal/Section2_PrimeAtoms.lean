import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.Factorization.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.NumberTheory.Wilson

/-!
# Section 2: Multiplicative Atoms & Modular Sieve Structures of ℙ
Formalization of Section 2 from the monograph.
-/

namespace RiemannBlueprint.Section2_PrimeAtoms

/-- Definition 2.1: Primes, Units, and Composites in ℕ. -/
def Primes : Set ℕ := { p | Nat.Prime p }
def Units : Set ℕ := { 1 }
def Composites : Set ℕ := { c | c > 1 ∧ ¬ Nat.Prime c }

/-- Lemma 2.2: Bézout's Identity in ℤ. -/
theorem bezout_identity (a b : ℕ) : ∃ x y : ℤ, (a : ℤ) * x + (b : ℤ) * y = Nat.gcd a b := by
  use Nat.gcdA a b, Nat.gcdB a b
  exact (Nat.gcd_eq_gcd_ab a b).symm

/-- Lemma 2.3: Euclid's Lemma for prime divisibility. -/
theorem euclid_lemma {p a b : ℕ} (hp : Nat.Prime p) (h : p ∣ a * b) : p ∣ a ∨ p ∣ b := by
  exact (Nat.Prime.dvd_mul hp).mp h

/-- Theorem 2.4: Fundamental Theorem of Arithmetic (Unique Prime Factorization). -/
theorem fundamental_theorem_of_arithmetic (n : ℕ) (_hn : n ≠ 0) :
    ∀ l : List ℕ, (∀ p ∈ l, Nat.Prime p) → l.prod = n → l.Perm n.primeFactorsList := by
  intro l hl_prime hl_prod
  exact Nat.primeFactorsList_unique hl_prod hl_prime

/-- Theorem 2.5: Modulo 6 Sieve Confinement for primes p > 3. -/
theorem modulo_6_sieve_confinement (p : ℕ) (hp : Nat.Prime p) (hp3 : p > 3) :
    p % 6 = 1 ∨ p % 6 = 5 := by
  have hp_ge_2 : p ≥ 2 := Nat.Prime.two_le hp
  have h_rem : p % 6 < 6 := Nat.mod_lt p (by decide)
  have h_not_0 : p % 6 ≠ 0 := by
    intro h
    have : 6 ∣ p := Nat.dvd_of_mod_eq_zero h
    have : 2 ∣ p := dvd_trans (by decide : 2 ∣ 6) this
    have hp2 : p = 2 := (Nat.Prime.eq_one_or_self_of_dvd hp 2 this).resolve_left (by decide) |>.symm
    omega
  have h_not_2 : p % 6 ≠ 2 := by
    intro h
    have : 2 ∣ p := by
      have : 2 ∣ 6 := by decide
      have : 2 ∣ p % 6 := by rw [h]
      have hd : 2 ∣ 6 * (p / 6) + p % 6 := dvd_add (dvd_mul_of_dvd_left (by decide) (p / 6)) this
      rwa [Nat.div_add_mod p 6] at hd
    have hp2 : p = 2 := (Nat.Prime.eq_one_or_self_of_dvd hp 2 this).resolve_left (by decide) |>.symm
    omega
  have h_not_3 : p % 6 ≠ 3 := by
    intro h
    have : 3 ∣ p := by
      have : 3 ∣ 6 := by decide
      have : 3 ∣ p % 6 := by rw [h]
      have hd : 3 ∣ 6 * (p / 6) + p % 6 := dvd_add (dvd_mul_of_dvd_left (by decide) (p / 6)) this
      rwa [Nat.div_add_mod p 6] at hd
    have hp3_eq : p = 3 := (Nat.Prime.eq_one_or_self_of_dvd hp 3 this).resolve_left (by decide) |>.symm
    omega
  have h_not_4 : p % 6 ≠ 4 := by
    intro h
    have : 2 ∣ p := by
      have : 2 ∣ 6 := by decide
      have : 2 ∣ p % 6 := by rw [h]; decide
      have hd : 2 ∣ 6 * (p / 6) + p % 6 := dvd_add (dvd_mul_of_dvd_left (by decide) (p / 6)) this
      rwa [Nat.div_add_mod p 6] at hd
    have hp2 : p = 2 := (Nat.Prime.eq_one_or_self_of_dvd hp 2 this).resolve_left (by decide) |>.symm
    omega
  omega

/-- Theorem 2.6: Fermat's Little Theorem. -/
theorem fermats_little_theorem (p a : ℕ) (hp : Nat.Prime p) (h : ¬ p ∣ a) :
    ((a : ZMod p) ^ (p - 1)) = 1 := by
  have : Fact (Nat.Prime p) := ⟨hp⟩
  have ha_ne_zero : (a : ZMod p) ≠ 0 := by
    intro hzero
    have hcast : ((a : ℕ) : ZMod p) = (a : ZMod p) := rfl
    rw [← hcast, CharP.cast_eq_zero_iff (ZMod p) p a] at hzero
    exact h hzero
  exact ZMod.pow_card_sub_one_eq_one ha_ne_zero

/-- Theorem 2.7: Wilson's Theorem. -/
theorem wilsons_theorem (p : ℕ) (hp : Nat.Prime p) :
    ((Nat.factorial (p - 1) : ZMod p) = -1) := by
  have : Fact (Nat.Prime p) := ⟨hp⟩
  exact ZMod.wilsons_lemma p

/-- Definition 2.8: Multiplicative order of 10 modulo p. -/
noncomputable def ord10 (p : ℕ) : ℕ := orderOf (10 : ZMod p)

/-- Theorem 2.9: Base-10 Radix Periodicity Theorem. -/
theorem base10_radix_periodicity (p : ℕ) (hp : Nat.Prime p) (h2 : p ≠ 2) (h5 : p ≠ 5) :
    ord10 p ∣ (p - 1) := by
  have : Fact (Nat.Prime p) := ⟨hp⟩
  have h10_ne_zero : (10 : ZMod p) ≠ 0 := by
    intro hzero
    have hcast : ((10 : ℕ) : ZMod p) = (10 : ZMod p) := rfl
    rw [← hcast, CharP.cast_eq_zero_iff (ZMod p) p 10] at hzero
    have h10 : (10 : ℕ) = 2 * 5 := by decide
    rw [h10] at hzero
    rcases (Nat.Prime.dvd_mul hp).mp hzero with h_two | h_five
    · have hp2 : p = 2 := ((Nat.dvd_prime Nat.prime_two).mp h_two).resolve_left hp.ne_one
      exact h2 hp2
    · have hp5 : p = 5 := ((Nat.dvd_prime (by decide : Nat.Prime 5)).mp h_five).resolve_left hp.ne_one
      exact h5 hp5
  exact ZMod.orderOf_dvd_card_sub_one h10_ne_zero

end RiemannBlueprint.Section2_PrimeAtoms
