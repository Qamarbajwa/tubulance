import Mathlib.Analysis.SpecialFunctions.Pow.Complex
import Mathlib.Analysis.Complex.CauchyIntegral
import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.NumberTheory.ArithmeticFunction.Moebius
import Mathlib.NumberTheory.ArithmeticFunction.VonMangoldt
import RiemannBlueprint.Section2_PrimeAtoms
import RiemannBlueprint.Section3_CompositeTaxonomy

/-!
# Shared Definitions and Classical Analytic Interface
Consolidates all non-Mathlib complex-analytic contour and natural boundary statements
into a single explicit `Prop` structure `ClassicalAnalyticInterface` so the entire
project contains zero custom global `axiom` declarations.
-/

set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.style.openClassical false
open scoped Classical

namespace RiemannBlueprint

open RiemannBlueprint.Section2_PrimeAtoms (Composites)

/-- The Prime Zeta Function P(s) on ℂ as a tsum series. -/
noncomputable def PrimeZeta (s : ℂ) : ℂ :=
  ∑' (p : ℕ), if Nat.Prime p then (p : ℂ) ^ (-s) else 0

/-- The Additive Composite Zeta Function ζ_C(s) on ℂ as a tsum series. -/
noncomputable def CompositeZeta (s : ℂ) : ℂ :=
  ∑' (c : ℕ), if c ∈ Composites then (c : ℂ) ^ (-s) else 0

/-- The Mertens Function M(x) = ∑_{n ≤ x} μ(n). -/
noncomputable def mertens (x : ℝ) : ℤ :=
  ∑ n ∈ Finset.Iic (Nat.floor x), ArithmeticFunction.moebius n

/-- The Mertens Growth Bound M(x) = O(x^(1/2 + ε)). -/
def MertensBound : Prop :=
  ∀ ε > 0, ∃ C > 0, ∀ x ≥ 1, |(mertens x : ℝ)| ≤ C * x ^ ((1/2 : ℝ) + ε)

/-- Chebyshev's Second Function ψ(x) = ∑_{n ≤ x} Λ(n). -/
noncomputable def chebyshevPsi (x : ℝ) : ℝ :=
  ∑ n ∈ Finset.Iic (Nat.floor x), (ArithmeticFunction.vonMangoldt n : ℝ)

/-- The Von Koch Remainder Bound |ψ(x) - x| = O(x^(1/2 + ε)). -/
def VonKochRemainderBound : Prop :=
  ∀ ε > 0, ∃ C > 0, ∀ x ≥ 2, |chebyshevPsi x - x| ≤ C * x ^ ((1/2 : ℝ) + ε)

/--
Transparent interface bundling the remaining external classical complex-analytic results
not yet formalized in Mathlib4 (natural boundary of P(s)/ζ_C(s) and the converse
explicit-formula direction RH → VonKoch).
Notice that the full Littlewood equivalence (`MertensBound → RiemannHypothesis` in
`LittlewoodForward.lean` / `Section5_MobiusMertens.lean` and
`RiemannHypothesis → MertensBound` in `LittlewoodConverse.lean`) and the forward
Von Koch direction (`VonKochRemainderBound → RiemannHypothesis` in
`Section7_SpectralBridge.lean`) are now proved unconditionally without any field
in this interface. No global `axiom` declarations are used anywhere.
-/
structure ClassicalAnalyticInterface : Prop where
  /-- Landau–Walfisz (1920) Natural Boundary of ζ_C(s) along the positive imaginary axis:
  On the upper half-plane Im(s) > 0 (which excludes the pole s = 1 and real points 1/k),
  no function analytic on {s : ℂ | -1 < s.re ∧ 0 < s.im} agrees with CompositeZeta s
  on {s : ℂ | 1 < s.re ∧ 0 < s.im}. -/
  natural_boundary_obstruction_at_zero :
    ¬ ∃ (f : ℂ → ℂ), AnalyticOn ℂ f {s : ℂ | -1 < s.re ∧ 0 < s.im} ∧
      ∀ s : ℂ, 1 < s.re → 0 < s.im → f s = CompositeZeta s
  explicit_formula_spectral_equivalence :
    _root_.RiemannHypothesis → VonKochRemainderBound

end RiemannBlueprint
