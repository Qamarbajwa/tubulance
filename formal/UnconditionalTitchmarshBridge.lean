/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import RiemannBlueprint.MellinFracPart
import RiemannBlueprint.Modules.LogarithmicPlaqueDecayCriterion

/-!
# Unconditional Titchmarsh Mellin Property Discharge Bridge

Discharges `TitchmarshMellinProperty` (from `MellinNymanBeurlingIff`)
unconditionally using `mellin_recipFract_unit_interval_of_pos_re` (from `MellinFracPart`),
yielding hypothesis-free versions of the Mellin Nyman–Beurling, pure-plaque, and
BBLR logarithmic plaque decay criteria across `Module 5C`, `Module 8D`, and `Module 8I`.
-/

open MeasureTheory Set Filter

/-- Unconditional proof of `TitchmarshMellinProperty` on `0 < Re(s) < 1`, discharged directly
from `mellin_recipFract_unit_interval_of_pos_re` in `MellinFracPart`. -/
theorem titchmarshMellinProperty_unconditional : TitchmarshMellinProperty := by
  intro s hs_pos hs_lt_one
  have hs_ne_one : s ≠ 1 := by
    intro h
    rw [h] at hs_lt_one
    simp at hs_lt_one
  exact NumberTheory.MellinFracPart.mellin_recipFract_unit_interval_of_pos_re s hs_pos hs_ne_one

/-- Unconditional Mellin-space Möbius fractional-part integral identity on `0 < Re(s) < 1`. -/
theorem integral_Ioo_moebius_recipFract_eq_unconditional
    (s : ℂ) (hs : 0 < s.re ∧ s.re < 1) (N : ℕ) :
    ∫ x : ℝ in Ioo 0 1, (1 + ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) *
        (recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1) =
      (1 / s) * (1 - riemannZeta s * ∑ k ∈ Finset.Icc 1 N,
        (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) ^ s) +
      (1 / (s - 1)) * ∑ k ∈ Finset.Icc 1 N, (ArithmeticFunction.moebius k : ℂ) / (k : ℂ) :=
  integral_Ioo_moebius_recipFract_eq titchmarshMellinProperty_unconditional s hs N

/-- Unconditional off-line zero `L^2` floor for `D_1 = 0` Báez–Duarte residuals. -/
theorem mellin_l2_floor_of_zeta_zero_unconditional (c : ℕ → ℝ) (N : ℕ)
    (hc1 : D1 c N = 0) {s : ℂ} (hs_lo : 1 / 2 < s.re) (hs_hi : s.re < 1)
    (hz : riemannZeta s = 0) :
    (2 * s.re - 1) / ‖s‖ ^ 2 ≤
      ∫ x in (0 : ℝ)..1, (1 - ∑ k ∈ Finset.Icc 1 N, c k * recipFractScaled k x) ^ 2 :=
  mellin_l2_floor_of_zeta_zero titchmarshMellinProperty_unconditional c N hc1 hs_lo hs_hi hz

/-- Unconditional pure-plaque lower bound for any off-line zero `riemannZeta s = 0`. -/
theorem purePlaque_floor_of_zeta_zero_unconditional {N : ℕ} (hN : 2 ≤ N)
    {c : ℕ → ℝ} (hc : IsDirichletAnchored c N)
    (hd : Real.pi * linearCotDrive (fun k => c k - cBaseAnchor k) N = 1)
    {s : ℂ} (hs_lo : 1 / 2 < s.re) (hs_hi : s.re < 1) (hz : riemannZeta s = 0) :
    (2 * s.re - 1) / ‖s‖ ^ 2 ≤ dipolePlaqueForm (fun k => c k - cBaseAnchor k) N :=
  purePlaque_floor_of_zeta_zero titchmarshMellinProperty_unconditional hN hc hd hs_lo hs_hi hz

/-- Unconditional pure-plaque vanishing criterion for `_root_.RiemannHypothesis`. -/
theorem riemannHypothesis_of_purePlaque_vanishing_unconditional
    (h_plaque : PurePlaqueVanishingCriterion) : _root_.RiemannHypothesis :=
  riemannHypothesis_of_purePlaque_vanishing titchmarshMellinProperty_unconditional h_plaque

/-- Unconditional telescoped-plaque vanishing criterion for `_root_.RiemannHypothesis`. -/
theorem riemannHypothesis_of_telescoped_plaque_vanishing_unconditional
    (h_tel : TelescopedPlaqueVanishingCriterion) : _root_.RiemannHypothesis :=
  riemannHypothesis_of_telescoped_plaque_vanishing titchmarshMellinProperty_unconditional h_tel

/-- Unconditional BBLR logarithmic plaque decay criterion for `_root_.RiemannHypothesis`. -/
theorem riemannHypothesis_of_logarithmic_plaque_bound_unconditional
    (h : ℕ → ℕ → ℝ) (C : ℝ)
    (h_ev : ∀ᶠ N in atTop,
      2 ≤ N ∧ D1 (h N) N = 0 ∧ D0 (h N) N = 0 ∧ h N 1 = 1 ∧
        Real.pi * linearCotDrive (h N) N = 1 ∧
        dipolePlaqueForm (h N) N ≤ C / Real.log (N : ℝ)) :
    _root_.RiemannHypothesis :=
  riemannHypothesis_of_logarithmic_plaque_bound titchmarshMellinProperty_unconditional h C h_ev
