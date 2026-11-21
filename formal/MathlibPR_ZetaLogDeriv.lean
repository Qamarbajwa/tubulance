/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
module

public import Mathlib.Analysis.Calculus.Deriv.Basic
public import Mathlib.Analysis.Calculus.Deriv.Inv
public import Mathlib.Analysis.Analytic.Basic
public import Mathlib.NumberTheory.LSeries.RiemannZeta
public import RiemannBlueprint.MathlibPR_LittlewoodMertens
public import RiemannBlueprint.MathlibPR_LittlewoodConverse

/-!
# Logarithmic Derivative and Inverse Zeta Holomorphy

This file formalizes the holomorphic regularity of the logarithmic derivative
`s ↦ ζ'(s) / ζ(s)` and the disjointness of non-trivial zeros off the critical line
under `RiemannHypothesis`:
1. The logarithmic derivative is holomorphic on `{s : ℂ | 1 / 2 < s.re ∧ s ≠ 1}`.
2. In particular, `riemannZeta` has no zeros (and no multiple zeros `ζ(s) = 0 ∧ ζ'(s) = 0`)
   anywhere in `{s : ℂ | 1 / 2 < s.re ∧ s ≠ 1}` or in the reflected strip
   `{s : ℂ | 0 < s.re ∧ s.re < 1 / 2}`.
3. The equivalence `riemannHypothesis_iff_analyticAt_inv_riemannZeta`.

## Main Results
* `differentiableOn_logDeriv_riemannZeta_of_riemannHypothesis`: Holomorphy of `ζ' / ζ`.
* `riemannZeta_Or_deriv_ne_zero_of_riemannHypothesis`: Nonvanishing off `Re(s) = 1/2`.
* `riemannHypothesis_iff_analyticAt_inv_riemannZeta`: Bidirectional reciprocal holomorphy.
-/

@[expose] public section

open scoped Topology
open Complex Filter Set

private lemma isOpen_re_gt (r : ℝ) : IsOpen {s : ℂ | r < s.re} :=
  isOpen_lt continuous_const Complex.continuous_re

private lemma riemannZeta_ne_zero_of_rh (hRH : _root_.RiemannHypothesis) {s : ℂ}
    (hs : 1 / 2 < s.re) (hs1 : s ≠ 1) : riemannZeta s ≠ 0 := by
  have hM := isBigO_mertens_of_riemannHypothesis hRH
  have h_inv := riemannZeta_mul_mellinMertens_eq_one_of_isBigO hM s hs hs1
  intro hz
  rw [hz, zero_mul] at h_inv
  exact zero_ne_one h_inv

/-- Under `_root_.RiemannHypothesis`, the logarithmic derivative `s ↦ ζ'(s) / ζ(s)` is
holomorphic (`DifferentiableOn ℂ`) on the punctured half-plane `{s : ℂ | 1 / 2 < s.re ∧ s ≠ 1}`. -/
theorem differentiableOn_logDeriv_riemannZeta_of_riemannHypothesis
    (hRH : _root_.RiemannHypothesis) :
    DifferentiableOn ℂ (fun s => deriv riemannZeta s / riemannZeta s)
      {s : ℂ | 1 / 2 < s.re ∧ s ≠ 1} := by
  let U : Set ℂ := {s : ℂ | 1 / 2 < s.re ∧ s ≠ 1}
  have hU_open : IsOpen U := (isOpen_re_gt (1 / 2)).inter isOpen_ne
  have h_diff : DifferentiableOn ℂ riemannZeta U := fun s hs =>
    (differentiableAt_riemannZeta hs.2).differentiableWithinAt
  have h_deriv_diff : DifferentiableOn ℂ (deriv riemannZeta) U :=
    h_diff.deriv hU_open
  refine h_deriv_diff.div h_diff fun s hs => ?_
  exact riemannZeta_ne_zero_of_rh hRH hs.1 hs.2

/-- Under `_root_.RiemannHypothesis`, `riemannZeta` has no zeros in `{s : ℂ | 1 / 2 < s.re ∧ s ≠ 1}`
nor in the reflected strip `{s : ℂ | 0 < s.re ∧ s.re < 1 / 2}`. In particular, at any such point
`s`, `riemannZeta s ≠ 0` (and hence `riemannZeta s ≠ 0 ∨ deriv riemannZeta s ≠ 0`). -/
theorem riemannZeta_Or_deriv_ne_zero_of_riemannHypothesis
    (hRH : _root_.RiemannHypothesis) {s : ℂ}
    (hs : (1 / 2 < s.re ∧ s ≠ 1) ∨ (0 < s.re ∧ s.re < 1 / 2)) :
    riemannZeta s ≠ 0 ∧ (riemannZeta s ≠ 0 ∨ deriv riemannZeta s ≠ 0) := by
  have h_ne : riemannZeta s ≠ 0 := by
    rcases hs with ⟨hs_gt, hs_ne1⟩ | ⟨hs_pos, hs_lt⟩
    · exact riemannZeta_ne_zero_of_rh hRH hs_gt hs_ne1
    · intro hz
      have hs_not_triv : ¬∃ n : ℕ, s = -2 * (n + 1) := fun ⟨n, hn⟩ => by
        have := congr_arg Complex.re hn
        simp at this
        linarith
      have hs_ne1 : s ≠ 1 := fun h1 => by
        subst h1
        norm_num at hs_lt
      have hz_refl := riemannZeta_zero_reflection hz hs_not_triv hs_ne1 hs_lt
      have h1ms_ne : 1 - s ≠ 1 := fun h1 => by
        have : s = 0 := by linear_combination -h1
        subst this
        simp only [Complex.zero_re] at hs_pos
        linarith
      exact riemannZeta_ne_zero_of_rh hRH hz_refl.2 h1ms_ne hz_refl.1
  exact ⟨h_ne, Or.inl h_ne⟩

/-- `_root_.RiemannHypothesis` holds if and only if `(riemannZeta ·)⁻¹` is differentiable at
every point `s : ℂ` with `1 / 2 < s.re` and `s ≠ 1`. -/
theorem riemannHypothesis_iff_analyticAt_inv_riemannZeta :
    _root_.RiemannHypothesis ↔
      ∀ s : ℂ, 1 / 2 < s.re → s ≠ 1 →
        DifferentiableAt ℂ (fun z => (riemannZeta z)⁻¹) s ∧ riemannZeta s ≠ 0 := by
  constructor
  · intro hRH s hs hs1
    have h_diff : DifferentiableAt ℂ riemannZeta s := differentiableAt_riemannZeta hs1
    have h_nz : riemannZeta s ≠ 0 := riemannZeta_ne_zero_of_rh hRH hs hs1
    exact ⟨h_diff.inv h_nz, h_nz⟩
  · intro h s hz h_not_triv h_not_one
    by_contra h_ne
    rcases lt_or_gt_of_ne h_ne with hlt | hgt
    · have hre_refl : 1 / 2 < (1 - s).re := by rw [Complex.sub_re, Complex.one_re]; linarith
      have hz_refl := riemannZeta_zero_reflection hz h_not_triv h_not_one hlt
      have h1ms_ne : 1 - s ≠ 1 := fun h1 => by
        have : s = 0 := by linear_combination -h1
        subst this
        simp [riemannZeta_zero] at hz
      exact (h (1 - s) hre_refl h1ms_ne).2 hz_refl.1
    · exact (h s hgt h_not_one).2 hz
