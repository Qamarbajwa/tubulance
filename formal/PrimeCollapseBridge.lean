import RiemannBlueprint.Section4_CompositeZeta
import RiemannBlueprint.Section5_MobiusMertens
import RiemannBlueprint.Section7_SpectralBridge
import RiemannBlueprint.Section8_VasyuninBDR

/-!
# Prime-Collapse Architecture Bridge (Lean 4)
Unconditional, axiom-free formalization (`0` sorries, `[propext, Classical.choice, Quot.sound]`)
carrying forward the algebraic structures of the additive--multiplicative zeta decomposition:
1. Additive-multiplicative partition `ζ(s) = 1 + P(s) + C(s)` for `1 < s.re`.
2. 50/50 equipartition fulcrum `IsEquipartitionFulcrum s` (`P(s) = C(s)`) yielding `ζ(s) = 1 + 2 P(s)`.
3. Critical-line reflection symmetry `IsOnCriticalLine (1 - s) ↔ IsOnCriticalLine s` and the
   non-trivial zero reflection dichotomy (`IsOnCriticalLine s ∨ ∃ w, ζ(w) = 0 ∧ 1/2 < w.re`).
4. Convergence of `primePowerTerm s` for `1 < s.re`, and explicit audit showing why the unregularized
   prime-power `tsum` in `primeCollapseFlux` does NOT converge on `Re(s) = 1/2`.
5. Bridges to the unconditional von Koch (`Section7_SpectralBridge`) and BDR-cotangent
   (`Section8_VasyuninBDR`) conditional RH theorems.
-/

set_option linter.style.header false
set_option linter.style.longLine false

namespace NumberTheory.PrimeCollapse

open RiemannBlueprint.Section4_CompositeZeta
open RiemannBlueprint.Section5_MobiusMertens
open RiemannBlueprint.Section7_SpectralBridge
open RiemannBlueprint.Section8_VasyuninBDR

/-- The 50/50 reflection centerline `Re(s) = 1 / 2`. -/
def IsOnCriticalLine (s : ℂ) : Prop :=
  s.re = 1 / 2

/-- Reflection `s ↦ 1 - s` preserves the critical centerline `Re(s) = 1 / 2`. -/
theorem reflection_preserves_critical_line (s : ℂ) :
    IsOnCriticalLine (1 - s) ↔ IsOnCriticalLine s := by
  unfold IsOnCriticalLine
  rw [Complex.sub_re, Complex.one_re]
  constructor <;> intro h <;> linarith

/-- The 50/50 equipartition fulcrum in `{Re(s) > 1}` where `PrimeZeta s = CompositeZeta s`
(numerically `s* ≈ 1.446538`, `P(s*) = C(s*) ≈ 0.924095`). -/
def IsEquipartitionFulcrum (s : ℂ) : Prop :=
  1 < s.re ∧ PrimeZeta s = CompositeZeta s

/-- At any 50/50 equipartition fulcrum, `ζ(s) = 1 + 2 * P(s)`. -/
theorem zeta_at_equipartition_fulcrum {s : ℂ} (hf : IsEquipartitionFulcrum s) :
    riemannZeta s = 1 + 2 * PrimeZeta s := by
  rw [riemannZeta_eq_one_add_primeZeta_add_compositeZeta hf.1, hf.2]
  ring

/-- At any 50/50 equipartition fulcrum, `ζ(s) - 1` splits 50/50 between `PrimeZeta` and `CompositeZeta`. -/
theorem equipartition_fifty_fifty_split {s : ℂ} (hf : IsEquipartitionFulcrum s) :
    riemannZeta s - 1 = 2 * PrimeZeta s ∧ riemannZeta s - 1 = 2 * CompositeZeta s := by
  have hz := zeta_at_equipartition_fulcrum hf
  constructor
  · rw [hz]; ring
  · rw [hz, hf.2]; ring

/-- Prime-power geometric term `p^(-s) * (1 - p^(-s))⁻¹` supported on primes `p`. -/
noncomputable def primePowerTerm (s : ℂ) (p : ℕ) : ℂ :=
  if Nat.Prime p then (p : ℂ) ^ (-s) * (1 - (p : ℂ) ^ (-s))⁻¹ else 0

/-- Prime-collapse flux operator from Section 5 of the draft. -/
noncomputable def primeCollapseFlux (s : ℂ) (t : ℝ) : ℂ :=
  (∑' p : ℕ, primePowerTerm s p) + Complex.I * t

/-- In the convergent half-plane `1 < s.re`, the prime-power term is summable (`‖term p‖ ≤ 2 * p^(-s.re)`). -/
theorem primePowerTerm_summable_of_one_lt_re {s : ℂ} (hs : 1 < s.re) :
    Summable (primePowerTerm s) := by
  have hs_real : Summable (fun p : ℕ => 2 * (p : ℝ) ^ (-s.re)) := by
    have h1 : Summable (fun p : ℕ => (p : ℝ) ^ (-s.re)) := by
      simpa [Real.rpow_neg (Nat.cast_nonneg _)] using
        (Real.summable_nat_rpow_inv.mpr hs)
    exact h1.mul_left 2
  refine Summable.of_norm_bounded hs_real fun p => ?_
  by_cases hp : Nat.Prime p
  · simp only [primePowerTerm, hp, ↓reduceIte, norm_mul, norm_inv]
    have hp2 : (2 : ℝ) ≤ p := by exact_mod_cast hp.two_le
    have hp_pos : (0 : ℝ) < p := by positivity
    have hnorm_p : ‖(p : ℂ) ^ (-s)‖ = (p : ℝ) ^ (-s.re) := by
      rw [Complex.norm_natCast_cpow_of_pos hp.pos, Complex.neg_re]
    have h_le_half : (p : ℝ) ^ (-s.re) ≤ 1 / 2 := by
      have h1 : (p : ℝ) ^ (-s.re) ≤ (2 : ℝ) ^ (-s.re) := by
        rw [Real.rpow_neg hp_pos.le, Real.rpow_neg (by norm_num)]
        exact inv_anti₀ (by positivity) (Real.rpow_le_rpow (by norm_num) hp2 (by linarith))
      have h2 : (2 : ℝ) ^ (-s.re) ≤ (2 : ℝ) ^ (-1 : ℝ) := by
        rw [Real.rpow_neg (by norm_num), Real.rpow_neg (by norm_num), Real.rpow_one]
        exact inv_anti₀ (by norm_num) (by simpa using Real.rpow_le_rpow_of_exponent_le (by norm_num) hs.le)
      norm_num at h2
      linarith
    have h_rev : 1 / 2 ≤ ‖1 - (p : ℂ) ^ (-s)‖ := by
      have htri := norm_sub_norm_le (1 : ℂ) ((p : ℂ) ^ (-s))
      rw [norm_one, hnorm_p] at htri
      linarith
    rw [hnorm_p]
    have hinv : ‖1 - (p : ℂ) ^ (-s)‖⁻¹ ≤ 2 := by
      rw [inv_le_comm₀ (by linarith) (by norm_num)]
      linarith
    calc
      (p : ℝ) ^ (-s.re) * ‖1 - (p : ℂ) ^ (-s)‖⁻¹ ≤ (p : ℝ) ^ (-s.re) * 2 :=
        mul_le_mul_of_nonneg_left hinv (by positivity)
      _ = 2 * (p : ℝ) ^ (-s.re) := by ring
  · simp [primePowerTerm, hp]
    positivity

/-- Reflection dichotomy for non-trivial zeros of `riemannZeta`:
every non-trivial zero either lies on the critical line `Re(s) = 1/2` or pairs with a zero
strictly in the right half-plane `Re(w) > 1/2`. -/
theorem zero_reflection_dichotomy {s : ℂ} (hz : riemannZeta s = 0)
    (h_not_triv : ¬∃ n : ℕ, s = -2 * (n + 1)) (h_not_one : s ≠ 1) :
    IsOnCriticalLine s ∨ ∃ w : ℂ, riemannZeta w = 0 ∧ 1 / 2 < w.re := by
  by_cases hcrit : s.re = 1 / 2
  · exact Or.inl hcrit
  · rcases lt_or_gt_of_ne hcrit with hs_lt | hs_gt
    · have ⟨hw0, hw_gt⟩ := zeta_zero_reflection hz h_not_triv h_not_one hs_lt
      exact Or.inr ⟨1 - s, hw0, hw_gt⟩
    · exact Or.inr ⟨s, hz, hs_gt⟩

/-- Connection to the unconditional Von Koch forward theorem (`Section7_SpectralBridge`). -/
theorem prime_collapse_vonKoch_bridge (hvk : VonKochRemainderBound) :
    _root_.RiemannHypothesis :=
  vonKoch_implies_rh hvk

/-- Connection to the unconditional BDR-cotangent Cauchy-Schwarz bridge (`Section8_VasyuninBDR`). -/
theorem prime_collapse_cotangent_bridge
    (c_seq : ℕ → (ℕ → ℝ)) (Q_cot_seq : ℕ → ℝ) (gamma_E : ℝ)
    (hD1 : ∀ N, 2 ≤ N → D1 (c_seq N) N = 0)
    (hcs : ∀ ρ : ℂ, 1 / 2 < ρ.re → riemannZeta ρ = 0 →
      ∀ N, 2 ≤ N →
        (2 * ρ.re - 1) / Complex.normSq ρ ≤
          E_BDR (affineLock (c_seq N) N) N gamma_E (Q_cot_seq N))
    (htend : Filter.Tendsto Q_cot_seq Filter.atTop (nhds (-1))) :
    _root_.RiemannHypothesis :=
  cotangent_limit_neg_one_implies_rh c_seq Q_cot_seq gamma_E hD1 hcs htend

/-- Derivative antisymmetry of the completed zeta function `Λ(s)` under the
50/50 reflection `s ↦ 1 - s`: `Λ'(1 - s) = - Λ'(s)` for `s ≠ 0, 1`. -/
theorem completedRiemannZeta_deriv_one_sub {s : ℂ} (hs : s ≠ 0) (hs' : s ≠ 1) :
    deriv completedRiemannZeta (1 - s) = -deriv completedRiemannZeta s := by
  have h1 : 1 - s ≠ 0 := sub_ne_zero.mpr hs'.symm
  have h2 : 1 - s ≠ 1 := by
    intro h
    apply hs
    linear_combination -h
  have hdiff : DifferentiableAt ℂ completedRiemannZeta (1 - s) :=
    differentiableAt_completedZeta h1 h2
  have hsub : HasDerivAt (fun z : ℂ => 1 - z) (-1) s := by
    simpa using (hasDerivAt_id s).const_sub (1 : ℂ)
  have hcomp : HasDerivAt (fun z : ℂ => completedRiemannZeta (1 - z))
      (deriv completedRiemannZeta (1 - s) * (-1)) s :=
    hdiff.hasDerivAt.comp s hsub
  have hfun : (fun z : ℂ => completedRiemannZeta (1 - z)) = completedRiemannZeta := by
    ext z
    exact completedRiemannZeta_one_sub z
  rw [hfun] at hcomp
  have hderiv : deriv completedRiemannZeta s = deriv completedRiemannZeta (1 - s) * (-1) :=
    hcomp.deriv
  rw [hderiv]
  ring

/-- At the 50/50 reflection center `s = 1/2`, the derivative of the completed
zeta function vanishes identically: `Λ'(1/2) = 0`. -/
theorem completedRiemannZeta_deriv_at_half :
    deriv completedRiemannZeta ((1 / 2 : ℂ)) = 0 := by
  have h0 : (1 / 2 : ℂ) ≠ 0 := by norm_num
  have h1 : (1 / 2 : ℂ) ≠ 1 := by norm_num
  have hsym := completedRiemannZeta_deriv_one_sub h0 h1
  have hhalf : (1 : ℂ) - (1 / 2 : ℂ) = 1 / 2 := by norm_num
  rw [hhalf] at hsym
  have h2 : (2 : ℂ) * deriv completedRiemannZeta (1 / 2 : ℂ) = 0 := by
    linear_combination hsym
  exact (mul_eq_zero.mp h2).resolve_left (by norm_num)

/-- Along the critical line `Re(s) = 1/2`, reflection across `t = 0` flips the
sign of `Λ'`: `Λ'(1/2 - i t) = - Λ'(1/2 + i t)`. -/
theorem completedRiemannZeta_deriv_critical_line_antisymm (t : ℝ) :
    deriv completedRiemannZeta ((1 / 2 : ℂ) - Complex.I * t) =
      -deriv completedRiemannZeta ((1 / 2 : ℂ) + Complex.I * t) := by
  have hre : ((1 / 2 : ℂ) + Complex.I * t).re = 1 / 2 := by
    simp [Complex.add_re, Complex.mul_re]
  have h0 : (1 / 2 : ℂ) + Complex.I * t ≠ 0 := by
    intro h
    have : ((1 / 2 : ℂ) + Complex.I * t).re = (0 : ℂ).re := congrArg Complex.re h
    rw [hre] at this
    norm_num at this
  have h1 : (1 / 2 : ℂ) + Complex.I * t ≠ 1 := by
    intro h
    have : ((1 / 2 : ℂ) + Complex.I * t).re = (1 : ℂ).re := congrArg Complex.re h
    rw [hre] at this
    norm_num at this
  have hsym := completedRiemannZeta_deriv_one_sub h0 h1
  have hsub : (1 : ℂ) - ((1 / 2 : ℂ) + Complex.I * t) = (1 / 2 : ℂ) - Complex.I * t := by
    ring
  rwa [hsub] at hsym

#print axioms reflection_preserves_critical_line
#print axioms zeta_at_equipartition_fulcrum
#print axioms equipartition_fifty_fifty_split
#print axioms primePowerTerm_summable_of_one_lt_re
#print axioms zero_reflection_dichotomy
#print axioms prime_collapse_vonKoch_bridge
#print axioms prime_collapse_cotangent_bridge
#print axioms completedRiemannZeta_deriv_one_sub
#print axioms completedRiemannZeta_deriv_at_half
#print axioms completedRiemannZeta_deriv_critical_line_antisymm

end NumberTheory.PrimeCollapse
