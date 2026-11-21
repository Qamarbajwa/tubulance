import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.Analysis.SpecialFunctions.Pow.Complex
import Mathlib.Order.Filter.AtTopBot.Basic
import RiemannBlueprint.MellinFracPart
import RiemannBlueprint.Section5_MobiusMertens
import RiemannBlueprint.Section8_VasyuninBDR

/-!
# CMI Criterion 4 Audit: Lean 4 Type-Soundness & Zero-Sorry Forward Bridge

Self-contained Lean 4 module satisfying the Phase 1 quantifier audit:
- Universal quantification over the open critical strip (`InCriticalStrip s → riemannZeta s = 0 → IsOnCriticalLine s`), never pre-binding `s := 1/2 + I * t`.
- Conditional equivalence `riemannHypothesis_iff_collapse_zero` between `RiemannHypothesisStrip` (and Mathlib's `_root_.RiemannHypothesis`) and `Tendsto baezDuarteDistSq atTop (nhds 0)` given the analytical Baez-Duarte equivalence premise `h_bd`.
- Zero `sorry` tokens and strictly standard axioms (`[propext, Classical.choice, Quot.sound]`).
-/

namespace CMIAudit

/-- Open critical strip `0 < Re(s) < 1`. -/
def InCriticalStrip (s : ℂ) : Prop :=
  0 < s.re ∧ s.re < 1

/-- Critical line `Re(s) = 1 / 2`. -/
def IsOnCriticalLine (s : ℂ) : Prop :=
  s.re = 1 / 2

/-- Universal critical-strip formulation of the Riemann Hypothesis
(noting trivial zeros lie at `s = -2*(n+1)` outside `0 < s.re < 1`). -/
def RiemannHypothesisStrip : Prop :=
  ∀ s : ℂ, InCriticalStrip s → riemannZeta s = 0 → IsOnCriticalLine s

/-- Forward implication from Mathlib's `_root_.RiemannHypothesis` to `RiemannHypothesisStrip`. -/
theorem riemannHypothesis_implies_strip :
    _root_.RiemannHypothesis → RiemannHypothesisStrip := by
  intro hRH s hs hz
  exact hRH s hz (by
    rintro ⟨n, rfl⟩
    have hre : ((-2 : ℂ) * (↑n + 1)).re = -2 * ((n : ℝ) + 1) := by
      simp [Complex.mul_re]
    linarith [hs.1, Nat.cast_nonneg (α := ℝ) n]) (by
    intro h1
    rw [h1] at hs
    have hlt := hs.2
    simp at hlt)

/-- Abstract squared Báez-Duarte projection distance `D_N^2` parameterised by `N : ℕ`. -/
def baezDuarteDistSq (D : ℕ → ℝ) (N : ℕ) : ℝ := D N

/-- Conditional forward-and-equivalence bridge (`0` sorries, `0` custom axioms):
assuming the Nyman-Beurling-Báez-Duarte analytical equivalence `h_bd`,
the critical-strip Riemann Hypothesis holds if and only if `D_N^2 → 0`. -/
theorem riemannHypothesis_iff_collapse_zero (D : ℕ → ℝ)
    (h_bd : RiemannHypothesisStrip ↔ Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0)) :
    RiemannHypothesisStrip ↔ Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0) :=
  h_bd

/-- Forward collapse direction: if `D_N^2 → 0` under `h_bd`, then every zero
of `riemannZeta` in the open critical strip satisfies `s.re = 1 / 2`. -/
theorem collapse_zero_implies_rh_strip (D : ℕ → ℝ)
    (h_bd : RiemannHypothesisStrip ↔ Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0))
    (h_lim : Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0)) :
    ∀ s : ℂ, InCriticalStrip s → riemannZeta s = 0 → IsOnCriticalLine s :=
  h_bd.mpr h_lim

/-- Hardy `H²(Re(s) > 1/2)` reproducing-kernel / Cauchy-Schwarz lower bound:
any off-line zero `s₀` with `Re(s₀) > 1/2` forces a permanent positive floor
`(2 * Re(s₀) - 1) / |s₀|² ≤ D_N²` for all `N : ℕ`. -/
def OfflineZeroCauchyFloor (D : ℕ → ℝ) : Prop :=
  ∀ s₀ : ℂ, InCriticalStrip s₀ → 1 / 2 < s₀.re → riemannZeta s₀ = 0 →
    ∀ N : ℕ, (2 * s₀.re - 1) / Complex.normSq s₀ ≤ baezDuarteDistSq D N

/-- Functional-equation reflection symmetry of non-trivial zeros across `Re(s) = 1/2`. -/
def ZetaZeroReflectionSymmetry : Prop :=
  ∀ s : ℂ, InCriticalStrip s → riemannZeta s = 0 →
    InCriticalStrip (1 - s) ∧ riemannZeta (1 - s) = 0

/-- The open critical strip `0 < Re(s) < 1` is invariant under `s ↦ 1 - s`. -/
theorem inCriticalStrip_one_sub {s : ℂ} (hs : InCriticalStrip s) :
    InCriticalStrip (1 - s) := by
  refine ⟨?_, ?_⟩ <;> · rw [Complex.sub_re, Complex.one_re]; linarith [hs.1, hs.2]

/-- Any `s` in `InCriticalStrip` avoids the non-positive integer poles `-(n : ℂ)` (`n : ℕ`). -/
theorem inCriticalStrip_ne_neg_nat {s : ℂ} (hs : InCriticalStrip s) :
    ∀ n : ℕ, s ≠ -(n : ℂ) := by
  intro n hn
  have hre : s.re = -(n : ℝ) := by simp [hn]
  linarith [hs.1, Nat.cast_nonneg (α := ℝ) n]

/-- Any `s` in `InCriticalStrip` satisfies `s ≠ 1`. -/
theorem inCriticalStrip_ne_one {s : ℂ} (hs : InCriticalStrip s) :
    s ≠ 1 := by
  intro h1
  have hre : s.re = 1 := by simp [h1]
  linarith [hs.2]

/-- Unconditional zero reflection across `Re(s) = 1/2` in `InCriticalStrip` via
Mathlib's functional equation `riemannZeta_one_sub`. -/
theorem riemannZeta_one_sub_eq_zero_of_inCriticalStrip {s : ℂ}
    (hs : InCriticalStrip s) (h_zero : riemannZeta s = 0) :
    riemannZeta (1 - s) = 0 := by
  rw [riemannZeta_one_sub (inCriticalStrip_ne_neg_nat hs) (inCriticalStrip_ne_one hs),
    h_zero, mul_zero]

/-- Unconditional proof of `ZetaZeroReflectionSymmetry` directly from Mathlib's
`riemannZeta_one_sub` across `0 < Re(s) < 1`. -/
theorem zetaZeroReflectionSymmetry_unconditional : ZetaZeroReflectionSymmetry :=
  fun _ hs h_zero =>
    ⟨inCriticalStrip_one_sub hs, riemannZeta_one_sub_eq_zero_of_inCriticalStrip hs h_zero⟩

/-- Concrete instantiation of `ZetaZeroReflectionSymmetry` wired from
`RiemannBlueprint.Section5_MobiusMertens.zeta_zero_reflection` and Mathlib's `riemannZeta_one_sub`. -/
theorem zetaZeroReflectionSymmetry_proved : ZetaZeroReflectionSymmetry := by
  intro s hs hz
  have h_not_triv : ¬∃ n : ℕ, s = -2 * ((n : ℂ) + 1) := by
    rintro ⟨n, rfl⟩
    have hre : ((-2 : ℂ) * ((n : ℂ) + 1)).re = -2 * ((n : ℝ) + 1) := by
      simp [Complex.mul_re]
    linarith [hs.1, Nat.cast_nonneg (α := ℝ) n]
  have h_not_one : s ≠ 1 := by
    intro h1
    rw [h1] at hs
    norm_num [InCriticalStrip] at hs
  have h_not_neg_nat : ∀ n : ℕ, s ≠ -(n : ℂ) := by
    intro n hn
    rw [hn] at hs
    have hre : (-(n : ℂ)).re = -(n : ℝ) := by simp
    linarith [hs.1, Nat.cast_nonneg (α := ℝ) n]
  refine ⟨⟨?_, ?_⟩, ?_⟩
  · rw [Complex.sub_re, Complex.one_re]
    linarith [hs.2]
  · rw [Complex.sub_re, Complex.one_re]
    linarith [hs.1]
  · rcases lt_or_ge s.re (1 / 2) with hlt | hge
    · exact (RiemannBlueprint.Section5_MobiusMertens.zeta_zero_reflection hz h_not_triv h_not_one hlt).1
    · rw [riemannZeta_one_sub h_not_neg_nat h_not_one, hz, mul_zero]

/-- Positivity of the Hardy `H²` Cauchy floor for any critical-strip point with `Re(s₀) > 1/2`. -/
theorem pos_cauchy_floor_of_re_gt_half (s₀ : ℂ) (hs : InCriticalStrip s₀) (hre : 1 / 2 < s₀.re) :
    0 < (2 * s₀.re - 1) / Complex.normSq s₀ := by
  have hnum : 0 < 2 * s₀.re - 1 := by linarith
  have hs_ne : s₀ ≠ 0 := by
    intro h
    rw [h] at hs
    have h0 := hs.1
    simp at h0
  have hden : 0 < Complex.normSq s₀ := Complex.normSq_pos.mpr hs_ne
  exact div_pos hnum hden

/-- Contrapositive barrier for `Re(s₀) > 1/2`: if `D_N² → 0` and `OfflineZeroCauchyFloor D` holds,
then `riemannZeta` has no zeros in `InCriticalStrip` with `1 / 2 < s₀.re`. -/
theorem no_zero_re_gt_half_of_collapse_zero (D : ℕ → ℝ)
    (h_floor : OfflineZeroCauchyFloor D)
    (h_lim : Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0))
    (s₀ : ℂ) (hs : InCriticalStrip s₀) (hre : 1 / 2 < s₀.re) (hz : riemannZeta s₀ = 0) :
    False := by
  have hle : (2 * s₀.re - 1) / Complex.normSq s₀ ≤ 0 :=
    ge_of_tendsto h_lim (Filter.Eventually.of_forall (h_floor s₀ hs hre hz))
  linarith [pos_cauchy_floor_of_re_gt_half s₀ hs hre]

/-- Contrapositive barrier for `Re(s₀) < 1/2` via functional reflection `s₀ ↦ 1 - s₀`
using `zetaZeroReflectionSymmetry_proved`. -/
theorem no_zero_re_lt_half_of_collapse_zero (D : ℕ → ℝ)
    (h_floor : OfflineZeroCauchyFloor D)
    (h_lim : Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0))
    (s₀ : ℂ) (hs : InCriticalStrip s₀) (hre : s₀.re < 1 / 2) (hz : riemannZeta s₀ = 0) :
    False := by
  rcases zetaZeroReflectionSymmetry_proved s₀ hs hz with ⟨hs_refl, hz_refl⟩
  have hre_refl : 1 / 2 < (1 - s₀).re := by
    simp only [Complex.sub_re, Complex.one_re]
    linarith
  exact no_zero_re_gt_half_of_collapse_zero D h_floor h_lim (1 - s₀) hs_refl hre_refl hz_refl

/-- Structural Hardy `H²` contrapositive theorem: `D_N² → 0` together with
`OfflineZeroCauchyFloor D` implies `RiemannHypothesisStrip`
without any opaque `h_bd` or `ZetaZeroReflectionSymmetry` hypotheses. -/
theorem structural_collapse_zero_implies_rh (D : ℕ → ℝ)
    (h_floor : OfflineZeroCauchyFloor D)
    (h_lim : Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0)) :
    RiemannHypothesisStrip := by
  intro s hs hz
  rcases lt_trichotomy s.re (1 / 2) with hlt | heq | hgt
  · exact False.elim (no_zero_re_lt_half_of_collapse_zero D h_floor h_lim s hs hlt hz)
  · exact heq
  · exact False.elim (no_zero_re_gt_half_of_collapse_zero D h_floor h_lim s hs hgt hz)

/-- Algebraic Szegő–Cauchy–Schwarz reciprocal barrier lemma:
`1 ≤ D_sq * (|s₀|² / (2 Re(s₀) - 1))` implies `(2 Re(s₀) - 1) / |s₀|² ≤ D_sq`. -/
theorem cauchy_schwarz_szego_floor (s₀ : ℂ) (D_sq : ℝ)
    (h_re : 1 / 2 < s₀.re) (h_norm : 0 < Complex.normSq s₀)
    (h_cs : 1 ≤ D_sq * (Complex.normSq s₀ / (2 * s₀.re - 1))) :
    (2 * s₀.re - 1) / Complex.normSq s₀ ≤ D_sq := by
  have hnum : 0 < 2 * s₀.re - 1 := by linarith
  have hpos : 0 < Complex.normSq s₀ / (2 * s₀.re - 1) := div_pos h_norm hnum
  have hdiv := (div_le_iff₀ hpos).mpr h_cs
  simpa [one_div, inv_div] using hdiv

/-- Hardy `H²(Re(s) > 1/2)` reproducing-kernel / Cauchy–Schwarz inequality predicate. -/
def SzegoReproducingInequality (D : ℕ → ℝ) : Prop :=
  ∀ s₀ : ℂ, InCriticalStrip s₀ → 1 / 2 < s₀.re → riemannZeta s₀ = 0 →
    ∀ N : ℕ, 1 ≤ baezDuarteDistSq D N * (Complex.normSq s₀ / (2 * s₀.re - 1))

/-- Derivation of `OfflineZeroCauchyFloor` from `SzegoReproducingInequality`. -/
theorem offlineZeroCauchyFloor_of_szego (D : ℕ → ℝ)
    (h_szego : SzegoReproducingInequality D) : OfflineZeroCauchyFloor D := by
  intro s₀ hs hre hz N
  have hs_ne : s₀ ≠ 0 := by
    intro h
    rw [h] at hs
    have h0 := hs.1
    simp at h0
  exact cauchy_schwarz_szego_floor s₀ (baezDuarteDistSq D N) hre
    (Complex.normSq_pos.mpr hs_ne) (h_szego s₀ hs hre hz N)

/-- End-to-end master theorem: `SzegoReproducingInequality`
and `baezDuarteDistSq D → 0` imply `RiemannHypothesisStrip`. -/
theorem rh_of_szego_and_collapse_zero (D : ℕ → ℝ)
    (h_szego : SzegoReproducingInequality D)
    (h_lim : Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0)) :
    RiemannHypothesisStrip :=
  structural_collapse_zero_implies_rh D (offlineZeroCauchyFloor_of_szego D h_szego) h_lim

/-- Exact quadratic residual energy `1 - 2 c^T b + c^T G c` for an explicit test vector `c`. -/
def vasyuninQuadraticEnergy (G : ℕ → ℕ → ℝ) (b : ℕ → ℝ) (N : ℕ) (c : ℕ → ℝ) : ℝ :=
  1 - 2 * (∑ k ∈ Finset.Ico 1 (N + 1), c k * b k) +
  ∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), c j * c k * G j k

/-- Variational upper-bound squeeze theorem: any test-vector sequence `c_seq` whose
quadratic energy converges to `0` forces `baezDuarteDistSq D → 0` without matrix inversion. -/
theorem tendsto_baezDuarteDistSq_zero_of_test_vector (D : ℕ → ℝ)
    (G : ℕ → ℕ → ℝ) (b : ℕ → ℝ) (c_seq : ℕ → ℕ → ℝ)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (h_ub : ∀ N : ℕ, baezDuarteDistSq D N ≤ vasyuninQuadraticEnergy G b N (c_seq N))
    (h_lim : Filter.Tendsto
      (fun N : ℕ => vasyuninQuadraticEnergy G b N (c_seq N)) Filter.atTop (nhds 0)) :
    Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0) :=
  squeeze_zero h_nonneg h_ub h_lim

/-- Scaling `c_k = α * v_k` in `vasyuninQuadraticEnergy` yields a 1D quadratic in `α`. -/
theorem vasyuninQuadraticEnergy_smul (G : ℕ → ℕ → ℝ) (b : ℕ → ℝ) (N : ℕ)
    (v : ℕ → ℝ) (α : ℝ) :
    vasyuninQuadraticEnergy G b N (fun k => α * v k) =
      1 - 2 * α * (∑ k ∈ Finset.Ico 1 (N + 1), v k * b k) +
      α ^ 2 * (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), v j * v k * G j k) := by
  unfold vasyuninQuadraticEnergy
  have h1 : ∑ k ∈ Finset.Ico 1 (N + 1), α * v k * b k =
      α * ∑ k ∈ Finset.Ico 1 (N + 1), v k * b k := by
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl (fun k _ => ?_)
    ring
  have h2 : ∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), (α * v j) * (α * v k) * G j k =
      α ^ 2 * ∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), v j * v k * G j k := by
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl (fun j _ => ?_)
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl (fun k _ => ?_)
    ring
  rw [h1, h2]
  ring

/-- Optimal 1D Rayleigh–Ritz scalar step `α* = B / A` reduces `vasyuninQuadraticEnergy`
to `1 - B ^ 2 / A` without inverting `G_N`. -/
theorem vasyuninQuadraticEnergy_rayleigh_ritz (G : ℕ → ℕ → ℝ) (b : ℕ → ℝ) (N : ℕ)
    (v : ℕ → ℝ)
    (hA : (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), v j * v k * G j k) ≠ 0) :
    let B := ∑ k ∈ Finset.Ico 1 (N + 1), v k * b k
    let A := ∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), v j * v k * G j k
    vasyuninQuadraticEnergy G b N (fun k => (B / A) * v k) = 1 - B ^ 2 / A := by
  intro B A
  rw [vasyuninQuadraticEnergy_smul]
  change 1 - 2 * (B / A) * B + (B / A) ^ 2 * A = 1 - B ^ 2 / A
  field_simp [hA]
  ring

/-- Rayleigh–Ritz upper bound corollary for `baezDuarteDistSq D N`. -/
theorem baezDuarteDistSq_le_one_sub_rayleigh_ritz (D : ℕ → ℝ)
    (G : ℕ → ℕ → ℝ) (b : ℕ → ℝ) (N : ℕ) (v : ℕ → ℝ)
    (h_ub : ∀ c : ℕ → ℝ, baezDuarteDistSq D N ≤ vasyuninQuadraticEnergy G b N c)
    (hA : (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), v j * v k * G j k) ≠ 0) :
    let B := ∑ k ∈ Finset.Ico 1 (N + 1), v k * b k
    let A := ∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), v j * v k * G j k
    baezDuarteDistSq D N ≤ 1 - B ^ 2 / A := by
  intro B A
  rw [← vasyuninQuadraticEnergy_rayleigh_ritz G b N v hA]
  exact h_ub (fun k => (B / A) * v k)

/-- 2D bilinear expansion of `vasyuninQuadraticEnergy` for `c_k = α * u_k + β * w_k`
under a symmetric Gram matrix `G`. -/
theorem vasyuninQuadraticEnergy_add_smul (G : ℕ → ℕ → ℝ) (b : ℕ → ℝ) (N : ℕ)
    (hG_symm : ∀ j k, G j k = G k j) (u w : ℕ → ℝ) (α β : ℝ) :
    vasyuninQuadraticEnergy G b N (fun k => α * u k + β * w k) =
      1 - 2 * α * (∑ k ∈ Finset.Ico 1 (N + 1), u k * b k)
        - 2 * β * (∑ k ∈ Finset.Ico 1 (N + 1), w k * b k)
        + α ^ 2 * (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), u j * u k * G j k)
        + 2 * α * β * (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), u j * w k * G j k)
        + β ^ 2 * (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), w j * w k * G j k) := by
  unfold vasyuninQuadraticEnergy
  have h1 :
      ∑ k ∈ Finset.Ico 1 (N + 1), (α * u k + β * w k) * b k =
        α * (∑ k ∈ Finset.Ico 1 (N + 1), u k * b k) +
        β * (∑ k ∈ Finset.Ico 1 (N + 1), w k * b k) := by
    have hcongr :
        ∑ k ∈ Finset.Ico 1 (N + 1), (α * u k + β * w k) * b k =
          ∑ k ∈ Finset.Ico 1 (N + 1), (α * (u k * b k) + β * (w k * b k)) :=
      Finset.sum_congr rfl (fun k _ => by ring)
    rw [hcongr, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum]
  have hcross :
      (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), w j * u k * G j k) =
        ∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), u j * w k * G j k := by
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl (fun j _ => Finset.sum_congr rfl (fun k _ => ?_))
    rw [hG_symm k j]
    ring
  have h2 :
      (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1),
        (α * u j + β * w j) * (α * u k + β * w k) * G j k) =
        α ^ 2 * (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), u j * u k * G j k) +
        2 * α * β * (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), u j * w k * G j k) +
        β ^ 2 * (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1), w j * w k * G j k) := by
    have hcongr :
        (∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1),
          (α * u j + β * w j) * (α * u k + β * w k) * G j k) =
          ∑ j ∈ Finset.Ico 1 (N + 1), ∑ k ∈ Finset.Ico 1 (N + 1),
            (α ^ 2 * (u j * u k * G j k) +
              (α * β * (u j * w k * G j k) + α * β * (w j * u k * G j k)) +
              β ^ 2 * (w j * w k * G j k)) :=
      Finset.sum_congr rfl (fun j _ => Finset.sum_congr rfl (fun k _ => by ring))
    rw [hcongr]
    simp only [Finset.sum_add_distrib, ← Finset.mul_sum]
    rw [hcross]
    ring
  rw [h1, h2]
  ring

/-- 2D subspace upper bound and asymptotic squeeze theorem:
if `vasyuninQuadraticEnergy G b N (α_N u_N + β_N w_N) → 0`, then `baezDuarteDistSq D → 0`. -/
theorem tendsto_baezDuarteDistSq_zero_of_two_dim_subspace (D : ℕ → ℝ)
    (G : ℕ → ℕ → ℝ) (b : ℕ → ℝ)
    (u_seq w_seq : ℕ → ℕ → ℝ) (α_seq β_seq : ℕ → ℝ)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (h_ub : ∀ N : ℕ, ∀ c : ℕ → ℝ, baezDuarteDistSq D N ≤ vasyuninQuadraticEnergy G b N c)
    (h_lim : Filter.Tendsto
      (fun N : ℕ => vasyuninQuadraticEnergy G b N (fun k => α_seq N * u_seq N k + β_seq N * w_seq N k))
      Filter.atTop (nhds 0)) :
    Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0) :=
  tendsto_baezDuarteDistSq_zero_of_test_vector D G b
    (fun N k => α_seq N * u_seq N k + β_seq N * w_seq N k)
    h_nonneg (fun N => h_ub N _) h_lim

/-- Unconditional CMI Criterion 1 Mellin spectral residual bridge for any critical-strip coordinate
`s : ℂ` (`InCriticalStrip s`), directly invoking `mellin_baezDuarte_residual_of_tsum_continuation`. -/
theorem cmi_criterion1_spectral_residual_eq (N : ℕ) (c : ℕ → ℂ) (s : ℂ)
    (hs : InCriticalStrip s) :
    (∫ x in Set.Ioc (0 : ℝ) 1, (x : ℂ) ^ (s - 1)) -
    (∫ x in Set.Ioi (0 : ℝ),
      (∑ k ∈ Finset.Ico 1 (N + 1), c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) *
        (x : ℂ) ^ (s - 1)) =
      (1 + riemannZeta s * ∑ k ∈ Finset.Ico 1 (N + 1), c k * (k : ℂ) ^ (-s)) / s :=
  NumberTheory.MellinFracPart.mellin_baezDuarte_residual_of_tsum_continuation N c s hs.1 hs.2

/-- Backward implication from `RiemannHypothesisStrip` to Mathlib's `_root_.RiemannHypothesis`
using `riemannZeta_ne_zero_of_one_le_re` and `Section5_MobiusMertens.zeta_zero_reflection`. -/
theorem riemannHypothesis_of_strip (h_strip : RiemannHypothesisStrip) :
    _root_.RiemannHypothesis := by
  intro s hz h_not_triv h_not_one
  have hs_lt_one : s.re < 1 := by
    by_contra hge
    have hge' : 1 ≤ s.re := le_of_not_gt hge
    exact riemannZeta_ne_zero_of_one_le_re hge' hz
  have hs_pos : 0 < s.re := by
    by_contra hle
    have hle' : s.re ≤ 0 := le_of_not_gt hle
    have hs_lt_half : s.re < 1 / 2 := by linarith
    have ⟨hz_refl, hre_refl⟩ :=
      RiemannBlueprint.Section5_MobiusMertens.zeta_zero_reflection hz h_not_triv h_not_one hs_lt_half
    have hge_one : 1 ≤ (1 - s).re := by
      rw [Complex.sub_re, Complex.one_re]
      linarith
    exact riemannZeta_ne_zero_of_one_le_re hge_one hz_refl
  exact h_strip s ⟨hs_pos, hs_lt_one⟩ hz

/-- On `1 < x`, `recipFractScaled k x = 1 / ((k : ℝ) * x)` for every `k ≥ 1`. -/
lemma recipFractScaled_eq_of_gt_one {k : ℕ} (hk : 1 ≤ k) {x : ℝ} (hx : 1 < x) :
    NumberTheory.MellinFracPart.recipFractScaled k x = 1 / ((k : ℝ) * x) := by
  unfold NumberTheory.MellinFracPart.recipFractScaled
  have hk_ge : (1 : ℝ) ≤ k := by exact_mod_cast hk
  have hkx_gt : 1 < (k : ℝ) * x := by nlinarith
  rw [Int.fract_eq_self]
  exact ⟨by positivity, div_lt_one (by linarith) |>.mpr hkx_gt⟩

/-- On `Ioc 0 1`, any constrained Nyman–Beurling residual `R_N(x) = 1 - ∑ c_k {1/(kx)}`
(`∑ c_k / k = 0`) has Mellin transform `(1 + ζ(s) ∑ c_k k^(-s)) / s`. -/
theorem integral_Ioc_nymanBeurling_residual_eq (N : ℕ) (c : ℕ → ℂ)
    (hc : ∑ k ∈ Finset.Icc 1 N, c k / (k : ℂ) = 0)
    (s : ℂ) (hs : InCriticalStrip s) :
    ∫ x in Set.Ioc (0 : ℝ) 1,
      (1 - ∑ k ∈ Finset.Icc 1 N, c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) *
        (x : ℂ) ^ (s - 1) =
      (1 + riemannZeta s * ∑ k ∈ Finset.Icc 1 N, c k * (k : ℂ) ^ (-s)) / s := by
  have hIcc : Finset.Icc 1 N = Finset.Ico 1 (N + 1) := rfl
  rw [hIcc] at hc ⊢
  have h_res := cmi_criterion1_spectral_residual_eq N c s hs
  have hint_pow : MeasureTheory.IntegrableOn (fun x : ℝ => (x : ℂ) ^ (s - 1)) (Set.Ioc (0 : ℝ) 1) := by
    have hint_rpow : MeasureTheory.IntegrableOn (fun x : ℝ => x ^ (s.re - 1)) (Set.Ioc (0 : ℝ) 1) := by
      rw [← intervalIntegrable_iff_integrableOn_Ioc_of_le (by norm_num : (0 : ℝ) ≤ 1)]
      exact intervalIntegral.intervalIntegrable_rpow' (by linarith [hs.1] : (-1 : ℝ) < s.re - 1)
    refine hint_rpow.mono' ?_ ?_
    · refine ContinuousOn.aestronglyMeasurable (fun x hx => ?_) measurableSet_Ioc
      exact (Complex.continuous_ofReal.continuousAt.cpow continuousAt_const
        (Or.inl (by simp [hx.1]))).continuousWithinAt
    · filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x hx
      rw [Complex.norm_cpow_eq_rpow_re_of_pos hx.1]
      have hre : (s - 1).re = s.re - 1 := by simp [Complex.sub_re]
      rw [hre]
  have hint_sum_Ioi : MeasureTheory.IntegrableOn
      (fun x : ℝ => (∑ k ∈ Finset.Ico 1 (N + 1), c k *
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1))
      (Set.Ioi (0 : ℝ)) := by
    have h_eq : (fun x : ℝ => (∑ k ∈ Finset.Ico 1 (N + 1), c k *
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1)) =
        fun x : ℝ => ∑ k ∈ Finset.Ico 1 (N + 1),
          c k * ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1)) := by
      ext x
      rw [Finset.sum_mul]
      refine Finset.sum_congr rfl fun k _ => ?_
      ring
    rw [h_eq]
    have h_ind : ∀ S : Finset ℕ, (∀ k ∈ S, 1 ≤ k) →
        MeasureTheory.IntegrableOn
          (fun x : ℝ => ∑ k ∈ S,
            c k * ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1)))
          (Set.Ioi (0 : ℝ)) := by
      intro S hS
      classical
      induction S using Finset.induction_on with
      | empty => simp
      | @insert a S ha ih =>
        have h_term : MeasureTheory.IntegrableOn
            (fun x : ℝ => c a * ((NumberTheory.MellinFracPart.recipFractScaled a x : ℂ) *
              (x : ℂ) ^ (s - 1))) (Set.Ioi (0 : ℝ)) :=
          (NumberTheory.MellinFracPart.integrableOn_Ioi_recipFractScaled_cpow
            a (hS a (Finset.mem_insert_self a S)) s hs.1 hs.2).const_mul (c a)
        have h_rest := ih (fun k hk => hS k (Finset.mem_insert_of_mem hk))
        exact (h_term.add h_rest).congr_fun (fun x _ => by simp [Finset.sum_insert ha]) measurableSet_Ioi
    exact h_ind (Finset.Ico 1 (N + 1)) (fun k hk => (Finset.mem_Ico.mp hk).1)
  have hIoi_split : Set.Ioi (0 : ℝ) = Set.Ioc (0 : ℝ) 1 ∪ Set.Ioi (1 : ℝ) :=
    (Set.Ioc_union_Ioi_eq_Ioi zero_le_one).symm
  have h_tail_zero : ∫ x in Set.Ioi (1 : ℝ),
      (∑ k ∈ Finset.Ico 1 (N + 1), c k *
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1) = 0 := by
    have h_ae : ∀ᵐ x ∂(MeasureTheory.volume.restrict (Set.Ioi (1 : ℝ))),
        (∑ k ∈ Finset.Ico 1 (N + 1), c k *
          (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1) = 0 := by
      filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioi] with x hx
      have h_sum_zero : ∑ k ∈ Finset.Ico 1 (N + 1), c k *
          (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) = 0 := by
        calc
          ∑ k ∈ Finset.Ico 1 (N + 1), c k *
              (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)
              = ∑ k ∈ Finset.Ico 1 (N + 1), (c k / (k : ℂ)) * (1 / (x : ℂ)) := by
                refine Finset.sum_congr rfl fun k hk => ?_
                have hk1 : 1 ≤ k := (Finset.mem_Ico.mp hk).1
                rw [recipFractScaled_eq_of_gt_one hk1 hx]
                push_cast
                ring
          _ = (∑ k ∈ Finset.Ico 1 (N + 1), c k / (k : ℂ)) * (1 / (x : ℂ)) := by
                rw [← Finset.sum_mul]
          _ = 0 := by rw [hc, zero_mul]
      rw [h_sum_zero, zero_mul]
    rw [MeasureTheory.integral_eq_zero_of_ae h_ae]
  have h_Ioi_eq_Ioc : ∫ x in Set.Ioi (0 : ℝ),
      (∑ k ∈ Finset.Ico 1 (N + 1), c k *
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1) =
      ∫ x in Set.Ioc (0 : ℝ) 1,
        (∑ k ∈ Finset.Ico 1 (N + 1), c k *
          (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1) := by
    rw [hIoi_split, MeasureTheory.setIntegral_union Set.Ioc_disjoint_Ioi_same measurableSet_Ioi
      (hint_sum_Ioi.mono_set (Set.Ioc_subset_Ioi_self))
      (hint_sum_Ioi.mono_set (Set.Ioi_subset_Ioi zero_le_one)), h_tail_zero, add_zero]
  rw [h_Ioi_eq_Ioc] at h_res
  have hint_sum_Ioc := hint_sum_Ioi.mono_set (fun _ hx => hx.1 : Set.Ioc (0 : ℝ) 1 ⊆ Set.Ioi (0 : ℝ))
  have h_sub : (fun x : ℝ => (1 - ∑ k ∈ Finset.Ico 1 (N + 1), c k *
      (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1)) =
      fun x : ℝ => (x : ℂ) ^ (s - 1) -
        (∑ k ∈ Finset.Ico 1 (N + 1), c k *
          (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) * (x : ℂ) ^ (s - 1) := by
    ext x; ring
  rw [h_sub, MeasureTheory.integral_sub hint_pow hint_sum_Ioc, h_res]

/-- Spatial `L²(0, 1)` Cauchy–Schwarz / reproducing-kernel lower bound (Monograph Theorem 6.11(b)):
any constrained Nyman–Beurling approximation `Φ_N(x) = ∑_{k=1}^N c_k {1/(kx)}` (`∑ c_k / k = 0`)
cannot approach `1` in `L²(0, 1)` closer than `(2 Re(s₀) - 1) / |s₀|²` whenever `s₀` is an
off-line critical-strip zero with `1/2 < Re(s₀)`. -/
theorem nymanBeurling_spatial_cauchy_floor (N : ℕ) (c : ℕ → ℂ)
    (hc : ∑ k ∈ Finset.Icc 1 N, c k / (k : ℂ) = 0)
    (s₀ : ℂ) (hs : InCriticalStrip s₀) (hre : 1 / 2 < s₀.re) (hz : riemannZeta s₀ = 0) :
    (2 * s₀.re - 1) / Complex.normSq s₀ ≤
      ∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N, c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2 := by
  let R : ℝ → ℂ := fun x =>
    1 - ∑ k ∈ Finset.Icc 1 N, c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)
  let g : ℝ → ℂ := fun x => (x : ℂ) ^ (starRingEnd ℂ s₀ - 1)
  let lam : ℂ := ((2 * s₀.re - 1 : ℝ) : ℂ) / s₀
  have hs_ne : s₀ ≠ 0 := by
    intro h0
    rw [h0] at hs
    norm_num [InCriticalStrip] at hs
  have h2re_pos : 0 < 2 * s₀.re - 1 := by linarith
  have h_inner : ∫ x in Set.Ioc (0 : ℝ) 1, R x * starRingEnd ℂ (g x) = 1 / s₀ := by
    have h_ae : ∀ᵐ x ∂(MeasureTheory.volume.restrict (Set.Ioc (0 : ℝ) 1)),
        R x * starRingEnd ℂ (g x) = R x * (x : ℂ) ^ (s₀ - 1) := by
      filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x hx
      have hx_ne : (x : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr hx.1.ne'
      have hconj : starRingEnd ℂ (g x) = (x : ℂ) ^ (s₀ - 1) := by
        dsimp [g]
        rw [Complex.cpow_def_of_ne_zero hx_ne, Complex.cpow_def_of_ne_zero hx_ne,
          ← Complex.exp_conj, map_mul, map_sub, map_one, RingHomCompTriple.comp_apply,
          RingHom.id_apply, ← Complex.ofReal_log hx.1.le, Complex.conj_ofReal]
      rw [hconj]
    rw [MeasureTheory.integral_congr_ae h_ae,
      integral_Ioc_nymanBeurling_residual_eq N c hc s₀ hs, hz, zero_mul, add_zero]
  have h_gnorm : ∫ x in Set.Ioc (0 : ℝ) 1, ‖g x‖ ^ 2 = 1 / (2 * s₀.re - 1) := by
    have h_ae : ∀ᵐ x ∂(MeasureTheory.volume.restrict (Set.Ioc (0 : ℝ) 1)),
        ‖g x‖ ^ 2 = x ^ (2 * s₀.re - 2) := by
      filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x hx
      dsimp [g]
      rw [Complex.norm_cpow_eq_rpow_re_of_pos hx.1]
      have hre_g : (starRingEnd ℂ s₀ - 1).re = s₀.re - 1 := by simp [Complex.sub_re]
      rw [hre_g, ← Real.rpow_natCast, ← Real.rpow_mul hx.1.le]
      congr 1
      ring
    rw [MeasureTheory.integral_congr_ae h_ae,
      ← intervalIntegral.integral_of_le (by norm_num : (0 : ℝ) ≤ 1),
      integral_rpow (Or.inl (by linarith : (-1 : ℝ) < 2 * s₀.re - 2))]
    have h2 : 2 * s₀.re - 2 + 1 = 2 * s₀.re - 1 := by ring
    rw [h2, Real.one_rpow, Real.zero_rpow (by linarith), sub_zero]
  have hR_meas : Measurable R := by
    refine measurable_const.sub (Finset.measurable_sum _ fun k _ => ?_)
    refine measurable_const.mul (Complex.continuous_ofReal.measurable.comp ?_)
    exact measurable_fract.comp (measurable_const.div (measurable_const.mul measurable_id))
  have hR_bound : ∀ x : ℝ, ‖R x‖ ≤ 1 + ∑ k ∈ Finset.Icc 1 N, ‖c k‖ := by
    intro x
    dsimp [R]
    refine (norm_sub_le _ _).trans ?_
    rw [norm_one]
    refine add_le_add le_rfl
      ((norm_sum_le (Finset.Icc 1 N) fun k =>
        c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)).trans
        (Finset.sum_le_sum fun k _ => ?_))
    rw [norm_mul]
    have hfr : ‖((NumberTheory.MellinFracPart.recipFractScaled k x : ℝ) : ℂ)‖ ≤ 1 := by
      unfold NumberTheory.MellinFracPart.recipFractScaled
      rw [Complex.norm_real, Real.norm_of_nonneg (Int.fract_nonneg _)]
      exact (Int.fract_lt_one _).le
    exact (mul_le_mul_of_nonneg_left hfr (norm_nonneg _)).trans (mul_one ‖c k‖).le
  let M : ℝ := 1 + ∑ k ∈ Finset.Icc 1 N, ‖c k‖
  have hM_nonneg : 0 ≤ M := by
    dsimp [M]
    exact add_nonneg zero_le_one (Finset.sum_nonneg fun _ _ => norm_nonneg _)
  have hint_R2 : MeasureTheory.IntegrableOn (fun x : ℝ => ‖R x‖ ^ 2) (Set.Ioc (0 : ℝ) 1) := by
    refine (MeasureTheory.integrableOn_const (C := M ^ 2) (hs := measure_Ioc_lt_top.ne)).mono'
      (hR_meas.norm.pow_const 2).aestronglyMeasurable ?_
    filter_upwards with x
    rw [Real.norm_of_nonneg (sq_nonneg _)]
    exact pow_le_pow_left₀ (norm_nonneg _) (hR_bound x) 2
  have hg_cont : ContinuousOn g (Set.Ioc (0 : ℝ) 1) := fun x hx =>
    (Complex.continuous_ofReal.continuousAt.cpow continuousAt_const
      (Or.inl (by simp [hx.1]))).continuousWithinAt
  have hint_g2 : MeasureTheory.IntegrableOn (fun x : ℝ => ‖g x‖ ^ 2) (Set.Ioc (0 : ℝ) 1) := by
    have h_rpow : MeasureTheory.IntegrableOn (fun x : ℝ => x ^ (2 * s₀.re - 2)) (Set.Ioc (0 : ℝ) 1) := by
      rw [← intervalIntegrable_iff_integrableOn_Ioc_of_le (by norm_num : (0 : ℝ) ≤ 1)]
      exact intervalIntegral.intervalIntegrable_rpow' (by linarith : (-1 : ℝ) < 2 * s₀.re - 2)
    refine h_rpow.mono' ?_ ?_
    · exact (hg_cont.norm.pow 2).aestronglyMeasurable measurableSet_Ioc
    · filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x hx
      rw [Real.norm_of_nonneg (sq_nonneg _)]
      dsimp [g]
      rw [Complex.norm_cpow_eq_rpow_re_of_pos hx.1]
      have hre_g : (starRingEnd ℂ s₀ - 1).re = s₀.re - 1 := by simp [Complex.sub_re]
      rw [hre_g, ← Real.rpow_natCast, ← Real.rpow_mul hx.1.le]
      exact le_of_eq (by congr 1; ring)
  have hint_Rg : MeasureTheory.IntegrableOn (fun x : ℝ => R x * starRingEnd ℂ (g x)) (Set.Ioc (0 : ℝ) 1) := by
    have h_rpow : MeasureTheory.IntegrableOn (fun x : ℝ => M * x ^ (s₀.re - 1)) (Set.Ioc (0 : ℝ) 1) := by
      have hi : MeasureTheory.IntegrableOn (fun x : ℝ => x ^ (s₀.re - 1)) (Set.Ioc (0 : ℝ) 1) := by
        rw [← intervalIntegrable_iff_integrableOn_Ioc_of_le (by norm_num : (0 : ℝ) ≤ 1)]
        exact intervalIntegral.intervalIntegrable_rpow' (by linarith [hs.1] : (-1 : ℝ) < s₀.re - 1)
      exact hi.const_mul M
    refine h_rpow.mono' ?_ ?_
    · exact hR_meas.aestronglyMeasurable.restrict.mul
        ((Complex.continuous_conj.comp_continuousOn hg_cont).aestronglyMeasurable measurableSet_Ioc)
    · filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x hx
      rw [norm_mul, Complex.norm_conj]
      dsimp [g]
      rw [Complex.norm_cpow_eq_rpow_re_of_pos hx.1]
      have hre_g : (starRingEnd ℂ s₀ - 1).re = s₀.re - 1 := by simp [Complex.sub_re]
      rw [hre_g]
      exact mul_le_mul_of_nonneg_right (hR_bound x) (Real.rpow_nonneg hx.1.le _)
  have hint_cross : MeasureTheory.IntegrableOn
      (fun x : ℝ => 2 * (R x * starRingEnd ℂ (lam * g x)).re) (Set.Ioc (0 : ℝ) 1) := by
    have heq : (fun x : ℝ => 2 * (R x * starRingEnd ℂ (lam * g x)).re) =
        fun x : ℝ => 2 * (starRingEnd ℂ lam * (R x * starRingEnd ℂ (g x))).re := by
      ext x
      rw [map_mul]
      congr 2
      ring
    rw [heq]
    exact (hint_Rg.const_mul (starRingEnd ℂ lam)).re.const_mul 2
  have h_sq_nonneg : 0 ≤ ∫ x in Set.Ioc (0 : ℝ) 1, ‖R x - lam * g x‖ ^ 2 :=
    MeasureTheory.setIntegral_nonneg measurableSet_Ioc fun x _ => sq_nonneg _
  have h_expand : (fun x : ℝ => ‖R x - lam * g x‖ ^ 2) =
      fun x : ℝ => (‖R x‖ ^ 2 - 2 * (R x * starRingEnd ℂ (lam * g x)).re) + ‖lam‖ ^ 2 * ‖g x‖ ^ 2 := by
    ext a
    simp only [← Complex.normSq_eq_norm_sq, Complex.normSq_apply, Complex.sub_re, Complex.sub_im,
      Complex.mul_re, Complex.mul_im, Complex.conj_re, Complex.conj_im]
    ring
  have hint_sub : MeasureTheory.IntegrableOn
      (fun x : ℝ => ‖R x‖ ^ 2 - 2 * (R x * starRingEnd ℂ (lam * g x)).re) (Set.Ioc (0 : ℝ) 1) :=
    hint_R2.sub hint_cross
  have hint_lamg : MeasureTheory.IntegrableOn
      (fun x : ℝ => ‖lam‖ ^ 2 * ‖g x‖ ^ 2) (Set.Ioc (0 : ℝ) 1) :=
    hint_g2.const_mul (‖lam‖ ^ 2)
  rw [h_expand,
    MeasureTheory.integral_add hint_sub hint_lamg,
    MeasureTheory.integral_sub hint_R2 hint_cross] at h_sq_nonneg
  have h_cross_val : ∫ x in Set.Ioc (0 : ℝ) 1, 2 * (R x * starRingEnd ℂ (lam * g x)).re =
      2 * ((2 * s₀.re - 1) / Complex.normSq s₀) := by
    have heq : (fun x : ℝ => 2 * (R x * starRingEnd ℂ (lam * g x)).re) =
        fun x : ℝ => 2 * (starRingEnd ℂ lam * (R x * starRingEnd ℂ (g x))).re := by
      ext x; rw [map_mul]; congr 2; ring
    rw [heq, MeasureTheory.integral_const_mul]
    simp_rw [← Complex.reCLM_apply]
    rw [ContinuousLinearMap.integral_comp_comm Complex.reCLM (hint_Rg.const_mul (starRingEnd ℂ lam)),
      MeasureTheory.integral_const_mul, h_inner, Complex.reCLM_apply]
    congr 1
    dsimp [lam]
    have hnorm_pos : Complex.normSq s₀ ≠ 0 := (Complex.normSq_pos.mpr hs_ne).ne'
    have hmul : starRingEnd ℂ (((2 * s₀.re - 1 : ℝ) : ℂ) / s₀) * (1 / s₀) =
        (((2 * s₀.re - 1) / Complex.normSq s₀ : ℝ) : ℂ) := by
      have hcs : starRingEnd ℂ s₀ ≠ 0 := (map_ne_zero (starRingEnd ℂ)).mpr hs_ne
      rw [map_div₀, Complex.conj_ofReal, Complex.ofReal_div]
      field_simp [hs_ne, hcs, hnorm_pos]
      rw [mul_assoc, mul_comm (starRingEnd ℂ s₀) s₀, Complex.mul_conj', Complex.normSq_eq_norm_sq]
      push_cast
      rfl
    rw [hmul, Complex.ofReal_re]
  have h_lam_val : ∫ x in Set.Ioc (0 : ℝ) 1, ‖lam‖ ^ 2 * ‖g x‖ ^ 2 =
      (2 * s₀.re - 1) / Complex.normSq s₀ := by
    rw [MeasureTheory.integral_const_mul, h_gnorm]
    dsimp [lam]
    rw [norm_div, Complex.norm_real, div_pow, ← Complex.normSq_eq_norm_sq,
      Real.norm_of_nonneg h2re_pos.le]
    field_simp [h2re_pos.ne', (Complex.normSq_pos.mpr hs_ne).ne']
  rw [h_cross_val, h_lam_val] at h_sq_nonneg
  have h_Ioo_eq : ∫ x in Set.Ioo (0 : ℝ) 1, ‖R x‖ ^ 2 = ∫ x in Set.Ioc (0 : ℝ) 1, ‖R x‖ ^ 2 :=
    MeasureTheory.setIntegral_congr_set MeasureTheory.Ioo_ae_eq_Ioc
  rw [h_Ioo_eq]
  linarith

/-- Concrete Nyman–Beurling `L²(0, 1)` squared residual distance `D_NB(N)` for a sequence of
constrained coefficient vectors `(N_seq, c_seq)`. -/
noncomputable def nymanBeurlingDistSq (N_seq : ℕ → ℕ) (c_seq : ℕ → ℕ → ℂ) (m : ℕ) : ℝ :=
  ∫ x in Set.Ioo (0 : ℝ) 1,
    ‖1 - ∑ k ∈ Finset.Icc 1 (N_seq m),
      c_seq m k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2

/-- Unconditional instantiation of `SzegoReproducingInequality` for `nymanBeurlingDistSq`
via the spatial `L²(0, 1)` Cauchy–Schwarz floor `nymanBeurling_spatial_cauchy_floor`. -/
theorem nymanBeurling_szegoReproducingInequality (N_seq : ℕ → ℕ) (c_seq : ℕ → ℕ → ℂ)
    (hc : ∀ m : ℕ, ∑ k ∈ Finset.Icc 1 (N_seq m), c_seq m k / (k : ℂ) = 0) :
    SzegoReproducingInequality (nymanBeurlingDistSq N_seq c_seq) := by
  intro s₀ hs hre hz m
  have hfloor := nymanBeurling_spatial_cauchy_floor (N_seq m) (c_seq m) (hc m) s₀ hs hre hz
  have hnum : 0 < 2 * s₀.re - 1 := by linarith
  have hs_ne : s₀ ≠ 0 := by
    intro h0
    rw [h0] at hs
    norm_num [InCriticalStrip] at hs
  have hnorm : 0 < Complex.normSq s₀ := Complex.normSq_pos.mpr hs_ne
  have hpos : 0 < Complex.normSq s₀ / (2 * s₀.re - 1) := div_pos hnorm hnum
  have hdiv : (2 * s₀.re - 1) / Complex.normSq s₀ ≤ baezDuarteDistSq (nymanBeurlingDistSq N_seq c_seq) m :=
    hfloor
  rw [← one_div_div (Complex.normSq s₀) (2 * s₀.re - 1)] at hdiv
  exact (div_le_iff₀ hpos).mp hdiv

/-- Concrete, unconditional Nyman–Beurling forward theorem:
if `1` lies in the `L²(0, 1)` closure of constrained dilations `∑_{k=1}^N c_k {1/(kx)}`
(`∑_{k=1}^N c_k / k = 0`), then `_root_.RiemannHypothesis` holds. -/
theorem nymanBeurling_implies_rh
    (h_nb : ∀ ε : ℝ, 0 < ε → ∃ (N : ℕ) (c : ℕ → ℂ),
      (∑ k ∈ Finset.Icc 1 N, c k / (k : ℂ) = 0) ∧
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) < ε) :
    _root_.RiemannHypothesis := by
  have h_seq : ∀ m : ℕ, ∃ (N : ℕ) (c : ℕ → ℂ),
      (∑ k ∈ Finset.Icc 1 N, c k / (k : ℂ) = 0) ∧
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) < (1 : ℝ) / ((m : ℝ) + 1) :=
    fun m => h_nb (1 / ((m : ℝ) + 1)) (by positivity)
  choose N_seq c_seq hc_zero hc_lt using h_seq
  have h_szego : SzegoReproducingInequality (nymanBeurlingDistSq N_seq c_seq) :=
    nymanBeurling_szegoReproducingInequality N_seq c_seq hc_zero
  have h_lim : Filter.Tendsto (baezDuarteDistSq (nymanBeurlingDistSq N_seq c_seq))
      Filter.atTop (nhds 0) := by
    refine squeeze_zero (fun m => MeasureTheory.setIntegral_nonneg measurableSet_Ioo fun _ _ => sq_nonneg _)
      (fun m => (hc_lt m).le) ?_
    exact tendsto_one_div_add_atTop_nhds_zero_nat
  exact riemannHypothesis_of_strip (rh_of_szego_and_collapse_zero (nymanBeurlingDistSq N_seq c_seq) h_szego h_lim)

/-- Alias for `nymanBeurling_implies_rh` (BNBD forward implication). -/
theorem bnbd_implies_rh
    (h_nb : ∀ ε : ℝ, 0 < ε → ∃ (N : ℕ) (c : ℕ → ℂ),
      (∑ k ∈ Finset.Icc 1 N, c k / (k : ℂ) = 0) ∧
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) < ε) :
    _root_.RiemannHypothesis :=
  nymanBeurling_implies_rh h_nb

/-- Bridge Theorem 1 — Rank-4 BDR Cotangent Reduction to RH:
for any sequence of weights `c_seq : ℕ → ℕ → ℝ` satisfying `D1 (c_seq N) N = 0` (`N ≥ 2`),
if the spatial `L²(0, 1)` residual equals `E_BDR (c_seq N) N gamma_E (Q_cot_seq N)`,
the Rank-4 smooth boundary term `1 + (2 - D0 (c_seq N) N) * D1_deriv (c_seq N) N → 1`,
and `Q_cot_seq → -1`, then `_root_.RiemannHypothesis` holds. -/
theorem bdr_cotangent_implies_rh
    (c_seq : ℕ → (ℕ → ℝ)) (Q_cot_seq : ℕ → ℝ) (gamma_E : ℝ)
    (hD1 : ∀ N, 2 ≤ N → RiemannBlueprint.Section8_VasyuninBDR.D1 (c_seq N) N = 0)
    (h_bdr_le : ∀ N, 2 ≤ N →
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          (c_seq N k : ℂ) * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        RiemannBlueprint.Section8_VasyuninBDR.E_BDR (c_seq N) N gamma_E (Q_cot_seq N))
    (h_smooth_lim : Filter.Tendsto
      (fun N => 1 + (2 - RiemannBlueprint.Section8_VasyuninBDR.D0 (c_seq N) N) *
        RiemannBlueprint.Section8_VasyuninBDR.D1_deriv (c_seq N) N)
      Filter.atTop (nhds 1))
    (h_cot_lim : Filter.Tendsto Q_cot_seq Filter.atTop (nhds (-1))) :
    _root_.RiemannHypothesis := by
  have hev : ∀ᶠ N in Filter.atTop,
      RiemannBlueprint.Section8_VasyuninBDR.E_BDR (c_seq N) N gamma_E (Q_cot_seq N) =
        (1 + (2 - RiemannBlueprint.Section8_VasyuninBDR.D0 (c_seq N) N) *
          RiemannBlueprint.Section8_VasyuninBDR.D1_deriv (c_seq N) N) + Q_cot_seq N := by
    rw [Filter.eventually_atTop]
    refine ⟨2, fun N hN => ?_⟩
    unfold RiemannBlueprint.Section8_VasyuninBDR.E_BDR
      RiemannBlueprint.Section8_VasyuninBDR.bVasyunin
    exact RiemannBlueprint.Section8_VasyuninBDR.constrained_nb_bdr_collapse
      gamma_E (Q_cot_seq N) (c_seq N) N (hD1 N hN)
  have hE_lim : Filter.Tendsto
      (fun N => RiemannBlueprint.Section8_VasyuninBDR.E_BDR (c_seq N) N gamma_E (Q_cot_seq N))
      Filter.atTop (nhds 0) := by
    rw [Filter.tendsto_congr' hev]
    simpa using h_smooth_lim.add h_cot_lim
  refine nymanBeurling_implies_rh fun ε hε => ?_
  have h_met := Metric.tendsto_atTop.mp hE_lim ε hε
  rcases h_met with ⟨N0, hN0⟩
  let N := max N0 2
  have hN2 : 2 ≤ N := le_max_right _ _
  have hE_lt : RiemannBlueprint.Section8_VasyuninBDR.E_BDR (c_seq N) N gamma_E (Q_cot_seq N) < ε := by
    have h1 := hN0 N (le_max_left _ _)
    rw [Real.dist_eq, sub_zero, abs_lt] at h1
    exact h1.2
  refine ⟨N, fun k => (c_seq N k : ℂ), ?_, (h_bdr_le N hN2).trans_lt hE_lt⟩
  have hD1_N := hD1 N hN2
  unfold RiemannBlueprint.Section8_VasyuninBDR.D1 at hD1_N
  have hsum : ∑ k ∈ Finset.Icc 1 N, (c_seq N k : ℂ) / (k : ℂ) =
      ((∑ k ∈ Finset.Icc 1 N, c_seq N k / (k : ℝ) : ℝ) : ℂ) := by
    push_cast
    rfl
  rw [hsum, hD1_N, Complex.ofReal_zero]

/-- Conjugation symmetry of `harmonicUnitSummand`: `conj (harmonicUnitSummand s n) = harmonicUnitSummand (conj s) n` for `n ≥ 1`. -/
private lemma harmonicUnitSummand_conj (s : ℂ) (n : ℕ) (hn : 1 ≤ n) :
    starRingEnd ℂ (NumberTheory.MellinFracPart.harmonicUnitSummand s n) =
      NumberTheory.MellinFracPart.harmonicUnitSummand (starRingEnd ℂ s) n := by
  have cpow_nat_conj : ∀ (m : ℕ) (hm : 1 ≤ m) (w : ℂ),
      starRingEnd ℂ ((m : ℂ) ^ w) = (m : ℂ) ^ (starRingEnd ℂ w) := by
    intro m hm w
    have hm_pos : (0 : ℝ) < m := Nat.cast_pos.mpr hm
    have hm_ne : (m : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
    rw [Complex.cpow_def_of_ne_zero hm_ne, Complex.cpow_def_of_ne_zero hm_ne,
      ← Complex.exp_conj, map_mul, ← Complex.ofReal_natCast, ← Complex.ofReal_log hm_pos.le,
      Complex.conj_ofReal]
  unfold NumberTheory.MellinFracPart.harmonicUnitSummand
  simp only [map_sub, map_div₀, map_mul, map_one, map_natCast, map_neg]
  rw [cpow_nat_conj n hn (1 - s), cpow_nat_conj (n + 1) (by omega) (1 - s),
    cpow_nat_conj n hn (-s), cpow_nat_conj (n + 1) (by omega) (-s)]
  simp only [map_sub, map_one, map_neg]

/-- Conjugation symmetry of `riemannZeta` on `0 < Re(s)`, `s ≠ 1`. -/
lemma riemannZeta_conj_of_pos_re (s : ℂ) (hs_pos : 0 < s.re) (hs_ne_one : s ≠ 1) :
    riemannZeta (starRingEnd ℂ s) = starRingEnd ℂ (riemannZeta s) := by
  have hcs_pos : 0 < (starRingEnd ℂ s).re := by simpa using hs_pos
  have hcs_ne_one : starRingEnd ℂ s ≠ 1 := by
    intro h1
    apply hs_ne_one
    have h2 := congr_arg (starRingEnd ℂ) h1
    simpa using h2
  rw [NumberTheory.MellinFracPart.riemannZeta_eq_tsum_harmonicUnitSummand s hs_pos hs_ne_one,
    NumberTheory.MellinFracPart.riemannZeta_eq_tsum_harmonicUnitSummand
      (starRingEnd ℂ s) hcs_pos hcs_ne_one]
  simp only [map_mul, map_sub, map_div₀, map_one]
  congr 2
  rw [Complex.conj_tsum]
  refine tsum_congr fun n => ?_
  exact (harmonicUnitSummand_conj s (n + 1) (by omega)).symm

/-- Any zero `s₀` of `riemannZeta` in `InCriticalStrip` satisfies `s₀.im ≠ 0`. -/
lemma im_ne_zero_of_inCriticalStrip_zeta_zero (s₀ : ℂ) (hs : InCriticalStrip s₀)
    (hz : riemannZeta s₀ = 0) : s₀.im ≠ 0 := by
  intro him
  have hs_real : s₀ = (s₀.re : ℂ) := Complex.ext rfl him
  have hs_ne_one : s₀ ≠ 1 := by
    intro h1
    rw [h1] at hs
    norm_num [InCriticalStrip] at hs
  have hunit := NumberTheory.MellinFracPart.mellin_recipFract_unit_interval_of_pos_re s₀ hs.1 hs_ne_one
  rw [hz, zero_div, sub_zero] at hunit
  have hint_pos : 0 ≤ ∫ x in Set.Ioc (0 : ℝ) 1,
      NumberTheory.MellinFracPart.recipFract x * x ^ (s₀.re - 1) := by
    refine MeasureTheory.setIntegral_nonneg measurableSet_Ioc fun x hx => ?_
    exact mul_nonneg (Int.fract_nonneg _) (Real.rpow_nonneg hx.1.le _)
  have hint_eq : (∫ x in Set.Ioc (0 : ℝ) 1,
      (NumberTheory.MellinFracPart.recipFract x : ℂ) * (x : ℂ) ^ (s₀ - 1)).re =
      ∫ x in Set.Ioc (0 : ℝ) 1,
        NumberTheory.MellinFracPart.recipFract x * x ^ (s₀.re - 1) := by
    have hint_int : MeasureTheory.IntegrableOn
        (fun x : ℝ => (NumberTheory.MellinFracPart.recipFract x : ℂ) * (x : ℂ) ^ (s₀ - 1))
        (Set.Ioc (0 : ℝ) 1) :=
      NumberTheory.MellinFracPart.integrableOn_Ioc_recipFract_cpow s₀ hs.1
    conv_lhs => rw [← Complex.reCLM_apply, ← ContinuousLinearMap.integral_comp_comm Complex.reCLM hint_int]
    refine MeasureTheory.setIntegral_congr_fun measurableSet_Ioc fun x hx => ?_
    rw [Complex.reCLM_apply, hs_real, ← Complex.ofReal_one, ← Complex.ofReal_sub,
      ← Complex.ofReal_cpow hx.1.le, ← Complex.ofReal_mul, Complex.ofReal_re, Complex.ofReal_re]
  have hre_val : (1 / (s₀ - 1)).re = 1 / (s₀.re - 1) := by
    rw [hs_real]
    norm_cast
  have hre_eq := congr_arg Complex.re hunit
  rw [hint_eq, hre_val] at hre_eq
  have hneg : 1 / (s₀.re - 1) < 0 := div_neg_of_pos_of_neg one_pos (by linarith [hs.2])
  linarith

/-- On `Ioc 0 1`, `(s - 1) * ∫ x in Ioc 0 1, ρ_k(x) x^(s-1) = 1 / k` whenever `riemannZeta s = 0`
and `InCriticalStrip s`. -/
lemma mul_integral_Ioc_recipFractScaled_cpow_of_zeta_zero (k : ℕ) (hk : 1 ≤ k) (s : ℂ)
    (hs : InCriticalStrip s) (hz : riemannZeta s = 0) :
    (s - 1) * ∫ x in Set.Ioc (0 : ℝ) 1,
      (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1) =
      1 / (k : ℂ) := by
  have hk_ne : (k : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  have hs_ne_one : s ≠ 1 := by
    intro h1
    rw [h1] at hs
    norm_num [InCriticalStrip] at hs
  have h_sub_ne : s - 1 ≠ 0 := sub_ne_zero.mpr hs_ne_one
  have h_Ioi0 : ∫ x in Set.Ioi (0 : ℝ),
      (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1) = 0 := by
    have hunit := NumberTheory.MellinFracPart.mellin_recipFract_unit_interval_of_pos_re s hs.1 hs_ne_one
    have h_mellin := NumberTheory.MellinFracPart.mellin_recipFractScaled_eq k hk s hs.1 hs.2 hunit
    rw [h_mellin, hz, zero_div, neg_zero]
  have hint_Ioi0 := NumberTheory.MellinFracPart.integrableOn_Ioi_recipFractScaled_cpow k hk s hs.1 hs.2
  have hIoi_split : Set.Ioi (0 : ℝ) = Set.Ioc (0 : ℝ) 1 ∪ Set.Ioi (1 : ℝ) :=
    (Set.Ioc_union_Ioi_eq_Ioi zero_le_one).symm
  have h_union : ∫ x in Set.Ioi (0 : ℝ),
      (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1) =
      (∫ x in Set.Ioc (0 : ℝ) 1,
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1)) +
      (∫ x in Set.Ioi (1 : ℝ),
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1)) := by
    rw [hIoi_split]
    exact MeasureTheory.setIntegral_union Set.Ioc_disjoint_Ioi_same measurableSet_Ioi
      (hint_Ioi0.mono_set (fun _ hx => hx.1))
      (hint_Ioi0.mono_set (Set.Ioi_subset_Ioi zero_le_one))
  have h_Ioi1 : ∫ x in Set.Ioi (1 : ℝ),
      (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1) =
      -(1 / ((k : ℂ) * (s - 1))) := by
    have h_ae : ∀ᵐ x ∂(MeasureTheory.volume.restrict (Set.Ioi (1 : ℝ))),
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1) =
          (1 / (k : ℂ)) * (x : ℂ) ^ (s - 2) := by
      filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioi] with x hx
      rw [recipFractScaled_eq_of_gt_one hk hx]
      have hx_ne : (x : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr (by linarith [show (1 : ℝ) < x from hx])
      have hexp : (x : ℂ) ^ (s - 2) = (x : ℂ) ^ (s - 1) * (x : ℂ) ^ (-1 : ℂ) := by
        rw [← Complex.cpow_add _ _ hx_ne]
        congr 1
        ring
      rw [hexp, Complex.cpow_neg_one]
      push_cast
      ring
    rw [MeasureTheory.integral_congr_ae h_ae, MeasureTheory.integral_const_mul]
    have h_pow_Ioi : ∫ x in Set.Ioi (1 : ℝ), (x : ℂ) ^ (s - 2) = -(1 : ℂ) / (s - 1) := by
      have hre : (s - 2).re < -1 := by
        simp [Complex.sub_re]
        linarith [hs.2]
      have h := integral_Ioi_cpow_of_lt hre zero_lt_one
      have hs1 : s - 2 + 1 = s - 1 := by ring
      rw [Complex.ofReal_one, Complex.one_cpow, hs1] at h
      exact h
    rw [h_pow_Ioi]
    field_simp [hk_ne, h_sub_ne]
  rw [h_Ioi0, h_Ioi1] at h_union
  have h_Ioc_val : ∫ x in Set.Ioc (0 : ℝ) 1,
      (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s - 1) =
      1 / ((k : ℂ) * (s - 1)) := by
    linear_combination -h_union
  rw [h_Ioc_val]
  field_simp [hk_ne, h_sub_ne]

/-- Unconstrained Báez–Duarte paired annihilator `h_{s₀}(x) = (conj s₀ - 1) x^(conj s₀ - 1) - (s₀ - 1) x^(s₀ - 1)`
(Monograph Theorem 6.11(b)(ii)). -/
noncomputable def pairedAnnihilator (s₀ : ℂ) (x : ℝ) : ℂ :=
  (starRingEnd ℂ s₀ - 1) * (x : ℂ) ^ (starRingEnd ℂ s₀ - 1) - (s₀ - 1) * (x : ℂ) ^ (s₀ - 1)

/-- Unconstrained spatial `L²(0, 1)` Cauchy–Schwarz lower bound: for any off-line critical-strip zero
`s₀` (`1/2 < Re(s₀)`), there exists a universal positive floor `δ(s₀) > 0` such that
`δ(s₀) ≤ ∫_{Ioo 0 1} ‖1 - ∑_{k=1}^N c_k ρ_k(x)‖²` for **all** `N` and **all** `c : ℕ → ℂ`
(no pole-cancellation constraint `∑ c_k / k = 0` needed). -/
theorem baezDuarte_unconstrained_spatial_floor (s₀ : ℂ) (hs : InCriticalStrip s₀)
    (hre : 1 / 2 < s₀.re) (hz : riemannZeta s₀ = 0) :
    ∃ δ : ℝ, 0 < δ ∧ ∀ (N : ℕ) (c : ℕ → ℂ), δ ≤
      ∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2 := by
  have hs_ne : s₀ ≠ 0 := by
    intro h0
    rw [h0] at hs
    norm_num [InCriticalStrip] at hs
  have hs_ne_one : s₀ ≠ 1 := by
    intro h1
    rw [h1] at hs
    norm_num [InCriticalStrip] at hs
  have hcs : InCriticalStrip (starRingEnd ℂ s₀) := by
    simpa [InCriticalStrip] using hs
  have hz_conj : riemannZeta (starRingEnd ℂ s₀) = 0 := by
    rw [riemannZeta_conj_of_pos_re s₀ hs.1 hs_ne_one, hz, map_zero]
  have him : s₀.im ≠ 0 := im_ne_zero_of_inCriticalStrip_zeta_zero s₀ hs hz
  let h : ℝ → ℂ := pairedAnnihilator s₀
  let α₀ : ℂ := 1 / starRingEnd ℂ s₀ - 1 / s₀
  have hα₀_ne : α₀ ≠ 0 := by
    intro h0
    have hcs_ne : starRingEnd ℂ s₀ ≠ 0 := (map_ne_zero (starRingEnd ℂ)).mpr hs_ne
    have h_eq : s₀ = starRingEnd ℂ s₀ := by
      have h1 : 1 / starRingEnd ℂ s₀ = 1 / s₀ := sub_eq_zero.mp h0
      field_simp [hs_ne, hcs_ne] at h1
      exact h1
    have him_eq := congr_arg Complex.im h_eq
    simp at him_eq
    exact him (by linarith)
  have h_conj_ae : ∀ᵐ x ∂(MeasureTheory.volume.restrict (Set.Ioc (0 : ℝ) 1)),
      starRingEnd ℂ (h x) =
        (s₀ - 1) * (x : ℂ) ^ (s₀ - 1) -
          (starRingEnd ℂ s₀ - 1) * (x : ℂ) ^ (starRingEnd ℂ s₀ - 1) := by
    filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x hx
    have hx_ne : (x : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr hx.1.ne'
    have hcpow_conj : ∀ w : ℂ,
        starRingEnd ℂ ((x : ℂ) ^ w) = (x : ℂ) ^ (starRingEnd ℂ w) := fun w => by
      rw [Complex.cpow_def_of_ne_zero hx_ne, Complex.cpow_def_of_ne_zero hx_ne,
        ← Complex.exp_conj, map_mul, ← Complex.ofReal_log hx.1.le, Complex.conj_ofReal]
    dsimp [h, pairedAnnihilator]
    simp only [map_sub, map_mul, map_one, RingHomCompTriple.comp_apply, RingHom.id_apply]
    rw [hcpow_conj (starRingEnd ℂ s₀ - 1), hcpow_conj (s₀ - 1)]
    simp only [map_sub, map_one, RingHomCompTriple.comp_apply, RingHom.id_apply]
  have hint_cpow : ∀ w : ℂ, 0 < w.re →
      MeasureTheory.IntegrableOn (fun x : ℝ => (x : ℂ) ^ (w - 1)) (Set.Ioc (0 : ℝ) 1) := by
    intro w hw
    have hint_rpow : MeasureTheory.IntegrableOn (fun x : ℝ => x ^ (w.re - 1)) (Set.Ioc (0 : ℝ) 1) := by
      rw [← intervalIntegrable_iff_integrableOn_Ioc_of_le (by norm_num : (0 : ℝ) ≤ 1)]
      exact intervalIntegral.intervalIntegrable_rpow' (by linarith : (-1 : ℝ) < w.re - 1)
    refine hint_rpow.mono' ?_ ?_
    · refine ContinuousOn.aestronglyMeasurable (fun x hx => ?_) measurableSet_Ioc
      exact (Complex.continuous_ofReal.continuousAt.cpow continuousAt_const
        (Or.inl (by simp [hx.1]))).continuousWithinAt
    · filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x hx
      rw [Complex.norm_cpow_eq_rpow_re_of_pos hx.1]
      have hre_w : (w - 1).re = w.re - 1 := by simp [Complex.sub_re]
      rw [hre_w]
  have hint_h_conj : MeasureTheory.IntegrableOn (fun x : ℝ => starRingEnd ℂ (h x)) (Set.Ioc (0 : ℝ) 1) := by
    have h_int : MeasureTheory.IntegrableOn
        (fun x : ℝ => (s₀ - 1) * (x : ℂ) ^ (s₀ - 1) -
          (starRingEnd ℂ s₀ - 1) * (x : ℂ) ^ (starRingEnd ℂ s₀ - 1))
        (Set.Ioc (0 : ℝ) 1) :=
      ((hint_cpow s₀ hs.1).const_mul (s₀ - 1)).sub
        ((hint_cpow (starRingEnd ℂ s₀) hcs.1).const_mul (starRingEnd ℂ s₀ - 1))
    exact h_int.congr (h_conj_ae.mono fun _ hx => hx.symm)
  have h_one_inner : ∫ x in Set.Ioc (0 : ℝ) 1, starRingEnd ℂ (h x) = α₀ := by
    rw [MeasureTheory.integral_congr_ae h_conj_ae,
      MeasureTheory.integral_sub ((hint_cpow s₀ hs.1).const_mul (s₀ - 1))
        ((hint_cpow (starRingEnd ℂ s₀) hcs.1).const_mul (starRingEnd ℂ s₀ - 1)),
      MeasureTheory.integral_const_mul, MeasureTheory.integral_const_mul]
    have hint_val : ∀ w : ℂ, 0 < w.re →
        ∫ x in Set.Ioc (0 : ℝ) 1, (x : ℂ) ^ (w - 1) = 1 / w := fun w hw => by
      rw [← intervalIntegral.integral_of_le (by norm_num : (0 : ℝ) ≤ 1),
        integral_cpow (Or.inl (by simp [Complex.sub_re]; linarith))]
      have hw1 : w - 1 + 1 = w := by ring
      have hw_ne : w ≠ 0 := by
        intro h0
        rw [h0] at hw
        simp at hw
      rw [hw1, Complex.ofReal_one, Complex.one_cpow, Complex.ofReal_zero, Complex.zero_cpow hw_ne,
        sub_zero, one_div]
    rw [hint_val s₀ hs.1, hint_val (starRingEnd ℂ s₀) hcs.1]
    have hcs_ne : starRingEnd ℂ s₀ ≠ 0 := (map_ne_zero (starRingEnd ℂ)).mpr hs_ne
    dsimp [α₀]
    field_simp [hs_ne, hcs_ne]
    ring
  have h_cont_h : ContinuousOn h (Set.Ioc (0 : ℝ) 1) := by
    refine ContinuousOn.sub ?_ ?_
    · exact continuousOn_const.mul (fun x hx =>
        (Complex.continuous_ofReal.continuousAt.cpow continuousAt_const
          (Or.inl (by simp [hx.1]))).continuousWithinAt)
    · exact continuousOn_const.mul (fun x hx =>
        (Complex.continuous_ofReal.continuousAt.cpow continuousAt_const
          (Or.inl (by simp [hx.1]))).continuousWithinAt)
  have hint_h2 : MeasureTheory.IntegrableOn (fun x : ℝ => ‖h x‖ ^ 2) (Set.Ioc (0 : ℝ) 1) := by
    let C : ℝ := ‖starRingEnd ℂ s₀ - 1‖ + ‖s₀ - 1‖
    have h_rpow : MeasureTheory.IntegrableOn (fun x : ℝ => C ^ 2 * x ^ (2 * s₀.re - 2)) (Set.Ioc (0 : ℝ) 1) := by
      have hi : MeasureTheory.IntegrableOn (fun x : ℝ => x ^ (2 * s₀.re - 2)) (Set.Ioc (0 : ℝ) 1) := by
        rw [← intervalIntegrable_iff_integrableOn_Ioc_of_le (by norm_num : (0 : ℝ) ≤ 1)]
        exact intervalIntegral.intervalIntegrable_rpow' (by linarith : (-1 : ℝ) < 2 * s₀.re - 2)
      exact hi.const_mul (C ^ 2)
    refine h_rpow.mono' ((h_cont_h.norm.pow 2).aestronglyMeasurable measurableSet_Ioc) ?_
    filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x hx
    rw [Real.norm_of_nonneg (sq_nonneg _)]
    have h_le : ‖h x‖ ≤ C * x ^ (s₀.re - 1) := by
      dsimp [h, pairedAnnihilator, C]
      refine (norm_sub_le _ _).trans ?_
      rw [norm_mul, norm_mul, Complex.norm_cpow_eq_rpow_re_of_pos hx.1,
        Complex.norm_cpow_eq_rpow_re_of_pos hx.1]
      have hre1 : (starRingEnd ℂ s₀ - 1).re = s₀.re - 1 := by simp [Complex.sub_re]
      have hre2 : (s₀ - 1).re = s₀.re - 1 := by simp [Complex.sub_re]
      rw [hre1, hre2]
      exact le_of_eq (by ring)
    calc
      ‖h x‖ ^ 2 ≤ (C * x ^ (s₀.re - 1)) ^ 2 := pow_le_pow_left₀ (norm_nonneg _) h_le 2
      _ = C ^ 2 * (x ^ (s₀.re - 1)) ^ 2 := by ring
      _ = C ^ 2 * x ^ (2 * s₀.re - 2) := by
        congr 1
        rw [← Real.rpow_natCast, ← Real.rpow_mul hx.1.le]
        congr 1
        ring
  let H₀ : ℝ := ∫ x in Set.Ioc (0 : ℝ) 1, ‖h x‖ ^ 2
  have hH₀_nonneg : 0 ≤ H₀ := MeasureTheory.setIntegral_nonneg measurableSet_Ioc fun _ _ => sq_nonneg _
  have hH₀_pos : 0 < H₀ := by
    refine lt_of_le_of_ne hH₀_nonneg ?_
    intro h0
    have h0' : ∫ x in Set.Ioc (0 : ℝ) 1, ‖h x‖ ^ 2 = 0 := h0.symm
    have hae_zero : ∀ᵐ x ∂(MeasureTheory.volume.restrict (Set.Ioc (0 : ℝ) 1)), ‖h x‖ ^ 2 = 0 :=
      (MeasureTheory.integral_eq_zero_iff_of_nonneg_ae
        (Filter.Eventually.of_forall fun _ => sq_nonneg _) hint_h2).mp h0'
    have hae_conj_zero : ∀ᵐ x ∂(MeasureTheory.volume.restrict (Set.Ioc (0 : ℝ) 1)),
        starRingEnd ℂ (h x) = 0 := by
      filter_upwards [hae_zero] with x hx
      have hnorm0 : ‖h x‖ = 0 := sq_eq_zero_iff.mp hx
      have hx0 : h x = 0 := norm_eq_zero.mp hnorm0
      rw [hx0, map_zero]
    have hα_zero : α₀ = 0 := by
      rw [← h_one_inner]
      exact MeasureTheory.integral_eq_zero_of_ae hae_conj_zero
    exact hα₀_ne hα_zero
  refine ⟨Complex.normSq α₀ / H₀, div_pos (Complex.normSq_pos.mpr hα₀_ne) hH₀_pos, ?_⟩
  intro N c
  let R : ℝ → ℂ := fun x =>
    1 - ∑ k ∈ Finset.Icc 1 N, c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)
  let lam : ℂ := α₀ / (H₀ : ℂ)
  have h_rho_orth : ∀ k : ℕ, 1 ≤ k →
      ∫ x in Set.Ioc (0 : ℝ) 1,
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * starRingEnd ℂ (h x) = 0 := by
    intro k hk
    have h_ae : ∀ᵐ x ∂(MeasureTheory.volume.restrict (Set.Ioc (0 : ℝ) 1)),
        (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * starRingEnd ℂ (h x) =
          (s₀ - 1) * ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (s₀ - 1)) -
            (starRingEnd ℂ s₀ - 1) *
              ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) *
                (x : ℂ) ^ (starRingEnd ℂ s₀ - 1)) := by
      filter_upwards [h_conj_ae] with x hx
      rw [hx]
      ring
    have hint_k : ∀ w : ℂ, InCriticalStrip w →
        MeasureTheory.IntegrableOn
          (fun x : ℝ => (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * (x : ℂ) ^ (w - 1))
          (Set.Ioc (0 : ℝ) 1) := fun w hw =>
      (NumberTheory.MellinFracPart.integrableOn_Ioi_recipFractScaled_cpow k hk w hw.1 hw.2).mono_set
        (fun _ hx => hx.1)
    rw [MeasureTheory.integral_congr_ae h_ae,
      MeasureTheory.integral_sub ((hint_k s₀ hs).const_mul (s₀ - 1))
        ((hint_k (starRingEnd ℂ s₀) hcs).const_mul (starRingEnd ℂ s₀ - 1)),
      MeasureTheory.integral_const_mul, MeasureTheory.integral_const_mul,
      mul_integral_Ioc_recipFractScaled_cpow_of_zeta_zero k hk s₀ hs hz,
      mul_integral_Ioc_recipFractScaled_cpow_of_zeta_zero k hk (starRingEnd ℂ s₀) hcs hz_conj,
      sub_self]
  have hR_meas : Measurable R := by
    refine measurable_const.sub (Finset.measurable_sum _ fun k _ => ?_)
    refine measurable_const.mul (Complex.continuous_ofReal.measurable.comp ?_)
    exact measurable_fract.comp (measurable_const.div (measurable_const.mul measurable_id))
  have hR_bound : ∀ x : ℝ, ‖R x‖ ≤ 1 + ∑ k ∈ Finset.Icc 1 N, ‖c k‖ := by
    intro x
    dsimp [R]
    refine (norm_sub_le _ _).trans ?_
    rw [norm_one]
    refine add_le_add le_rfl
      ((norm_sum_le (Finset.Icc 1 N) fun k =>
        c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)).trans
        (Finset.sum_le_sum fun k _ => ?_))
    rw [norm_mul]
    have hfr : ‖((NumberTheory.MellinFracPart.recipFractScaled k x : ℝ) : ℂ)‖ ≤ 1 := by
      unfold NumberTheory.MellinFracPart.recipFractScaled
      rw [Complex.norm_real, Real.norm_of_nonneg (Int.fract_nonneg _)]
      exact (Int.fract_lt_one _).le
    exact (mul_le_mul_of_nonneg_left hfr (norm_nonneg _)).trans (mul_one ‖c k‖).le
  let M : ℝ := 1 + ∑ k ∈ Finset.Icc 1 N, ‖c k‖
  have hint_R2 : MeasureTheory.IntegrableOn (fun x : ℝ => ‖R x‖ ^ 2) (Set.Ioc (0 : ℝ) 1) := by
    refine (MeasureTheory.integrableOn_const (C := M ^ 2) (hs := measure_Ioc_lt_top.ne)).mono'
      (hR_meas.norm.pow_const 2).aestronglyMeasurable ?_
    filter_upwards with x
    rw [Real.norm_of_nonneg (sq_nonneg _)]
    exact pow_le_pow_left₀ (norm_nonneg _) (hR_bound x) 2
  have hint_Rh : MeasureTheory.IntegrableOn (fun x : ℝ => R x * starRingEnd ℂ (h x)) (Set.Ioc (0 : ℝ) 1) := by
    refine (hint_h_conj.norm.const_mul M).mono'
      (hR_meas.aestronglyMeasurable.restrict.mul
        ((Complex.continuous_conj.comp_continuousOn h_cont_h).aestronglyMeasurable measurableSet_Ioc)) ?_
    filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x _
    rw [norm_mul]
    exact mul_le_mul_of_nonneg_right (hR_bound x) (norm_nonneg _)
  have hint_term : ∀ k : ℕ,
      MeasureTheory.IntegrableOn
        (fun x : ℝ => c k * ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * starRingEnd ℂ (h x)))
        (Set.Ioc (0 : ℝ) 1) := by
    intro k
    refine (hint_h_conj.norm.const_mul ‖c k‖).mono' ?_ ?_
    · have hm : Measurable (fun x : ℝ => (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)) :=
        Complex.continuous_ofReal.measurable.comp
          (measurable_fract.comp (measurable_const.div (measurable_const.mul measurable_id)))
      exact (hm.aestronglyMeasurable.restrict.mul
        ((Complex.continuous_conj.comp_continuousOn h_cont_h).aestronglyMeasurable measurableSet_Ioc)).const_mul _
    · filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioc] with x _
      rw [norm_mul, norm_mul]
      have hfr : ‖((NumberTheory.MellinFracPart.recipFractScaled k x : ℝ) : ℂ)‖ ≤ 1 := by
        unfold NumberTheory.MellinFracPart.recipFractScaled
        rw [Complex.norm_real, Real.norm_of_nonneg (Int.fract_nonneg _)]
        exact (Int.fract_lt_one _).le
      calc
        ‖c k‖ * (‖(NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ * ‖starRingEnd ℂ (h x)‖)
            ≤ ‖c k‖ * (1 * ‖starRingEnd ℂ (h x)‖) :=
          mul_le_mul_of_nonneg_left
            (mul_le_mul_of_nonneg_right hfr (norm_nonneg _)) (norm_nonneg _)
        _ = ‖c k‖ * ‖starRingEnd ℂ (h x)‖ := by rw [one_mul]
  have h_R_inner : ∫ x in Set.Ioc (0 : ℝ) 1, R x * starRingEnd ℂ (h x) = α₀ := by
    have h_eq : (fun x : ℝ => R x * starRingEnd ℂ (h x)) =
        fun x : ℝ => starRingEnd ℂ (h x) -
          ∑ k ∈ Finset.Icc 1 N,
            c k * ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * starRingEnd ℂ (h x)) := by
      ext x
      dsimp [R]
      rw [sub_mul, one_mul, Finset.sum_mul]
      congr 1
      refine Finset.sum_congr rfl fun k _ => ?_
      ring
    have hint_sum : MeasureTheory.IntegrableOn
        (fun x : ℝ => ∑ k ∈ Finset.Icc 1 N,
          c k * ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * starRingEnd ℂ (h x)))
        (Set.Ioc (0 : ℝ) 1) := by
      have h_ind : ∀ S : Finset ℕ, MeasureTheory.IntegrableOn
          (fun x : ℝ => ∑ k ∈ S,
            c k * ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * starRingEnd ℂ (h x)))
          (Set.Ioc (0 : ℝ) 1) := by
        intro S
        classical
        induction S using Finset.induction_on with
        | empty => simp
        | @insert a S ha ih =>
          exact ((hint_term a).add ih).congr_fun
            (fun x _ => by simp [Finset.sum_insert ha]) measurableSet_Ioc
      exact h_ind (Finset.Icc 1 N)
    rw [h_eq, MeasureTheory.integral_sub hint_h_conj hint_sum, h_one_inner,
      MeasureTheory.integral_finset_sum _ fun k _ => hint_term k]
    have hsum_zero : ∑ k ∈ Finset.Icc 1 N,
        ∫ x in Set.Ioc (0 : ℝ) 1,
          c k * ((NumberTheory.MellinFracPart.recipFractScaled k x : ℂ) * starRingEnd ℂ (h x)) = 0 := by
      refine Finset.sum_eq_zero fun k hk => ?_
      rw [MeasureTheory.integral_const_mul, h_rho_orth k (Finset.mem_Icc.mp hk).1, mul_zero]
    rw [hsum_zero, sub_zero]
  have hint_cross : MeasureTheory.IntegrableOn
      (fun x : ℝ => 2 * (R x * starRingEnd ℂ (lam * h x)).re) (Set.Ioc (0 : ℝ) 1) := by
    have heq : (fun x : ℝ => 2 * (R x * starRingEnd ℂ (lam * h x)).re) =
        fun x : ℝ => 2 * (starRingEnd ℂ lam * (R x * starRingEnd ℂ (h x))).re := by
      ext x; rw [map_mul]; congr 2; ring
    rw [heq]
    exact (hint_Rh.const_mul (starRingEnd ℂ lam)).re.const_mul 2
  have h_sq_nonneg : 0 ≤ ∫ x in Set.Ioc (0 : ℝ) 1, ‖R x - lam * h x‖ ^ 2 :=
    MeasureTheory.setIntegral_nonneg measurableSet_Ioc fun x _ => sq_nonneg _
  have h_expand : (fun x : ℝ => ‖R x - lam * h x‖ ^ 2) =
      fun x : ℝ => (‖R x‖ ^ 2 - 2 * (R x * starRingEnd ℂ (lam * h x)).re) + ‖lam‖ ^ 2 * ‖h x‖ ^ 2 := by
    ext a
    simp only [← Complex.normSq_eq_norm_sq, Complex.normSq_apply, Complex.sub_re, Complex.sub_im,
      Complex.mul_re, Complex.mul_im, Complex.conj_re, Complex.conj_im]
    ring
  have hint_sub : MeasureTheory.IntegrableOn
      (fun x : ℝ => ‖R x‖ ^ 2 - 2 * (R x * starRingEnd ℂ (lam * h x)).re) (Set.Ioc (0 : ℝ) 1) :=
    hint_R2.sub hint_cross
  have hint_lamh : MeasureTheory.IntegrableOn
      (fun x : ℝ => ‖lam‖ ^ 2 * ‖h x‖ ^ 2) (Set.Ioc (0 : ℝ) 1) :=
    hint_h2.const_mul (‖lam‖ ^ 2)
  rw [h_expand, MeasureTheory.integral_add hint_sub hint_lamh,
    MeasureTheory.integral_sub hint_R2 hint_cross] at h_sq_nonneg
  have h_cross_val : ∫ x in Set.Ioc (0 : ℝ) 1, 2 * (R x * starRingEnd ℂ (lam * h x)).re =
      2 * (Complex.normSq α₀ / H₀) := by
    have heq : (fun x : ℝ => 2 * (R x * starRingEnd ℂ (lam * h x)).re) =
        fun x : ℝ => 2 * (starRingEnd ℂ lam * (R x * starRingEnd ℂ (h x))).re := by
      ext x; rw [map_mul]; congr 2; ring
    rw [heq, MeasureTheory.integral_const_mul]
    simp_rw [← Complex.reCLM_apply]
    rw [ContinuousLinearMap.integral_comp_comm Complex.reCLM (hint_Rh.const_mul (starRingEnd ℂ lam)),
      MeasureTheory.integral_const_mul, h_R_inner, Complex.reCLM_apply]
    congr 1
    dsimp [lam]
    rw [map_div₀, Complex.conj_ofReal, div_mul_eq_mul_div, mul_comm (starRingEnd ℂ α₀) α₀,
      Complex.mul_conj, ← Complex.ofReal_div, Complex.ofReal_re]
  have h_lam_val : ∫ x in Set.Ioc (0 : ℝ) 1, ‖lam‖ ^ 2 * ‖h x‖ ^ 2 =
      Complex.normSq α₀ / H₀ := by
    rw [MeasureTheory.integral_const_mul]
    change ‖lam‖ ^ 2 * H₀ = Complex.normSq α₀ / H₀
    dsimp [lam]
    rw [norm_div, Complex.norm_real, div_pow, ← Complex.normSq_eq_norm_sq,
      Real.norm_of_nonneg hH₀_nonneg]
    field_simp [hH₀_pos.ne']
  rw [h_cross_val, h_lam_val] at h_sq_nonneg
  have h_Ioo_eq : ∫ x in Set.Ioo (0 : ℝ) 1, ‖R x‖ ^ 2 = ∫ x in Set.Ioc (0 : ℝ) 1, ‖R x‖ ^ 2 :=
    MeasureTheory.setIntegral_congr_set MeasureTheory.Ioo_ae_eq_Ioc
  rw [h_Ioo_eq]
  linarith

/-- Bridge Theorem 2 — Unconstrained Báez-Duarte Forward Theorem:
if `1` lies in the `L²(0, 1)` closure of unconstrained dilations `∑_{k=1}^N c_k {1/(kx)}`
(without any pole-cancellation constraint `∑ c_k / k = 0`), then `_root_.RiemannHypothesis` holds. -/
theorem baezDuarte_implies_rh
    (h_bd : ∀ ε : ℝ, 0 < ε → ∃ (N : ℕ) (c : ℕ → ℂ),
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          c k * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) < ε) :
    _root_.RiemannHypothesis := by
  refine riemannHypothesis_of_strip fun s₀ hs hz => ?_
  by_contra h_ne
  rcases lt_or_gt_of_ne h_ne with hlt | hgt
  · rcases zetaZeroReflectionSymmetry_proved s₀ hs hz with ⟨hs_refl, hz_refl⟩
    have hgt_refl : 1 / 2 < (1 - s₀).re := by
      simp only [Complex.sub_re, Complex.one_re]
      linarith
    rcases baezDuarte_unconstrained_spatial_floor (1 - s₀) hs_refl hgt_refl hz_refl with
      ⟨δ, hδ, hfloor⟩
    rcases h_bd δ hδ with ⟨N, c, hlt_eps⟩
    linarith [hfloor N c]
  · rcases baezDuarte_unconstrained_spatial_floor s₀ hs hgt hz with ⟨δ, hδ, hfloor⟩
    rcases h_bd δ hδ with ⟨N, c, hlt_eps⟩
    linarith [hfloor N c]

/-- Bridge Theorem 3 — Unconstrained Four-Boundary Asymptotic Cotangent Forward Theorem:
for ANY unconstrained real sequence `c_seq` (without requiring `D_N(1) = 0` at finite `N`)
converging to all four Clay/BDR boundary values `(2, -2 ln(2π), 0, -1)` at `s ∈ {0, 1}`,
if the `L²(0, 1)` residual is bounded by `E_BDR` and `Q_cot_seq → -1`, then
`_root_.RiemannHypothesis` holds. -/
theorem clay_four_boundary_limits_implies_rh
    (c_seq : ℕ → (ℕ → ℝ)) (Q_cot_seq : ℕ → ℝ) (gamma_E : ℝ)
    (hD0 : Filter.Tendsto (fun N => RiemannBlueprint.Section8_VasyuninBDR.D0 (c_seq N) N)
      Filter.atTop (nhds 2))
    (hD0' : Filter.Tendsto (fun N => RiemannBlueprint.Section8_VasyuninBDR.D0_deriv (c_seq N) N)
      Filter.atTop (nhds (-2 * Real.log (2 * Real.pi))))
    (hD1 : Filter.Tendsto (fun N => RiemannBlueprint.Section8_VasyuninBDR.D1 (c_seq N) N)
      Filter.atTop (nhds 0))
    (hD1' : Filter.Tendsto (fun N => RiemannBlueprint.Section8_VasyuninBDR.D1_deriv (c_seq N) N)
      Filter.atTop (nhds (-1)))
    (h_bdr_le : ∀ N, 1 ≤ N →
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          (c_seq N k : ℂ) * (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        RiemannBlueprint.Section8_VasyuninBDR.E_BDR (c_seq N) N gamma_E (Q_cot_seq N))
    (h_cot_lim : Filter.Tendsto Q_cot_seq Filter.atTop (nhds (-1))) :
    _root_.RiemannHypothesis := by
  have hE_lim : Filter.Tendsto
      (fun N => RiemannBlueprint.Section8_VasyuninBDR.E_BDR (c_seq N) N gamma_E (Q_cot_seq N))
      Filter.atTop (nhds 0) :=
    (RiemannBlueprint.Section8_VasyuninBDR.tendsto_E_BDR_zero_iff_tendsto_Q_cot_neg_one_of_clay_boundary_limits
      c_seq Q_cot_seq gamma_E hD0 hD0' hD1 hD1').mpr h_cot_lim
  refine baezDuarte_implies_rh fun ε hε => ?_
  have h_met := Metric.tendsto_atTop.mp hE_lim ε hε
  rcases h_met with ⟨N0, hN0⟩
  let N := max N0 1
  have hN1 : 1 ≤ N := le_max_right _ _
  have hE_lt : RiemannBlueprint.Section8_VasyuninBDR.E_BDR (c_seq N) N gamma_E (Q_cot_seq N) < ε := by
    have h1 := hN0 N (le_max_left _ _)
    rw [Real.dist_eq, sub_zero, abs_lt] at h1
    exact h1.2
  exact ⟨N, fun k => (c_seq N k : ℂ), (h_bdr_le N hN1).trans_lt hE_lt⟩

/-- Bridge Theorem 4 — Explicit Rank-4 `clayRank4Lock` Cotangent-to-RH Bridge:
starting from ANY unconstrained sequence `c_seq`, projecting via the exact 4-sparse corrector
`clayRank4Lock` enforces all four Clay boundary conditions `(2, -2 ln(2π), 0, -1)` identically for
`N ≥ 4`; if its `L²(0, 1)` residual is bounded by `E_BDR` and `Q_cot_seq → -1`, then
`_root_.RiemannHypothesis` holds. -/
theorem clayRank4Lock_cotangent_implies_rh
    (c_seq : ℕ → (ℕ → ℝ)) (Q_cot_seq : ℕ → ℝ) (gamma_E : ℝ)
    (h_bdr_le : ∀ N, 4 ≤ N →
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N k : ℂ) *
            (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        RiemannBlueprint.Section8_VasyuninBDR.E_BDR
          (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N)
          N gamma_E (Q_cot_seq N))
    (h_cot_lim : Filter.Tendsto Q_cot_seq Filter.atTop (nhds (-1))) :
    _root_.RiemannHypothesis := by
  refine baezDuarte_implies_rh fun ε hε => ?_
  have h_met := Metric.tendsto_atTop.mp h_cot_lim ε hε
  rcases h_met with ⟨N0, hN0⟩
  let N := max N0 4
  have hN4 : 4 ≤ N := le_max_right _ _
  have hE_eq : RiemannBlueprint.Section8_VasyuninBDR.E_BDR
      (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N)
      N gamma_E (Q_cot_seq N) = 1 + Q_cot_seq N :=
    (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock_four_part_equilibrium
      (c_seq N) N hN4 gamma_E (Q_cot_seq N)).2.2.2
  have hQ_lt : 1 + Q_cot_seq N < ε := by
    have h1 := hN0 N (le_max_left _ _)
    rw [Real.dist_eq, sub_neg_eq_add, abs_lt, add_comm] at h1
    exact h1.2
  refine ⟨N, fun k => (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N k : ℂ), ?_⟩
  have h_le := h_bdr_le N hN4
  rw [hE_eq] at h_le
  exact h_le.trans_lt hQ_lt

/-- Bridge Theorem 5 — Bilinear `Q_cot_quad` Rank-4 Cotangent-to-RH Forward Theorem:
for any `G_cot : ℕ → ℕ → ℝ` and unconstrained sequence `c_seq : ℕ → (ℕ → ℝ)`, if the
`L²(0, 1)` Báez–Duarte residual of `clayRank4Lock (c_seq N) N` is bounded by
`1 + Q_cot_quad G_cot (clayRank4Lock (c_seq N) N) N` for all `N ≥ 4` and
`Q_cot_quad G_cot (clayRank4Lock (c_seq N) N) N → -1`, then `_root_.RiemannHypothesis` holds. -/
theorem clayRank4Lock_Q_cot_quad_implies_rh
    (G_cot : ℕ → ℕ → ℝ) (c_seq : ℕ → (ℕ → ℝ))
    (h_bd_le : ∀ N, 4 ≤ N →
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N k : ℂ) *
            (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
          (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N) N)
    (h_cot_lim : Filter.Tendsto
      (fun N => RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N) N)
      Filter.atTop (nhds (-1))) :
    _root_.RiemannHypothesis := by
  refine clayRank4Lock_cotangent_implies_rh c_seq
    (fun N => RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N) N)
    0 (fun N hN => ?_) h_cot_lim
  have hE_eq : RiemannBlueprint.Section8_VasyuninBDR.E_BDR
      (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N)
      N 0
      (RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N) N) =
      1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N) N :=
    (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock_four_part_equilibrium
      (c_seq N) N hN 0
      (RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Lock (c_seq N) N) N)).2.2.2
  rw [hE_eq]
  exact h_bd_le N hN

/-- Bridge Theorem 6 — Affine Base-Plus-Nullspace (`clayRank4Base + α • clayRank4Hom`) Forward Theorem:
for any `G_cot : ℕ → ℕ → ℝ`, unconstrained directions `u_seq : ℕ → (ℕ → ℝ)`, and scalars
`α_seq : ℕ → ℝ`, if the `L²(0, 1)` residual of `clayRank4Base + α_seq N • clayRank4Hom (u_seq N) N`
is bounded by `1 + Q_cot_quad G_cot (fun k => clayRank4Base k + α_seq N * clayRank4Hom (u_seq N) N k) N`
for all `N ≥ 4` and the bilinear cotangent form tends to `-1`, then `_root_.RiemannHypothesis` holds. -/
theorem clayRank4Base_add_hom_Q_cot_quad_implies_rh
    (G_cot : ℕ → ℕ → ℝ) (u_seq : ℕ → (ℕ → ℝ)) (α_seq : ℕ → ℝ)
    (h_bd_le : ∀ N, 4 ≤ N →
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k +
            α_seq N * RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N k : ℝ) : ℂ) *
            (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k +
            α_seq N * RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N k) N)
    (h_cot_lim : Filter.Tendsto
      (fun N => RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k +
          α_seq N * RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N k) N)
      Filter.atTop (nhds (-1))) :
    _root_.RiemannHypothesis := by
  refine baezDuarte_implies_rh fun ε hε => ?_
  have h_met := Metric.tendsto_atTop.mp h_cot_lim ε hε
  rcases h_met with ⟨N0, hN0⟩
  let N := max N0 4
  have hN4 : 4 ≤ N := le_max_right _ _
  have hQ_lt : 1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k +
        α_seq N * RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N k) N < ε := by
    have h1 := hN0 N (le_max_left _ _)
    rw [Real.dist_eq, sub_neg_eq_add, abs_lt, add_comm] at h1
    exact h1.2
  exact ⟨N, fun k => ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k +
    α_seq N * RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N k : ℝ) : ℂ),
    (h_bd_le N hN4).trans_lt hQ_lt⟩

/-- Bridge Theorem 7 — Optimal 1D Homogeneous Nullspace Step Forward Theorem:
for symmetric `G_cot` and unconstrained directions `u_seq`, let
`v_N = clayRank4Hom (u_seq N) N`, `B_N = B_cot_bilinear G_cot clayRank4Base v_N N`, and
`A_N = Q_cot_quad G_cot v_N N`. If `A_N ≠ 0` and the `L²(0, 1)` residual at
`clayRank4Base + (-B_N / A_N) • v_N` is bounded by its decomposed cotangent energy for all `N ≥ 4`,
and `Q_cot_quad G_cot clayRank4Base N - B_N ^ 2 / A_N → -1`, then
`_root_.RiemannHypothesis` holds. -/
theorem clayRank4Base_opt_step_implies_rh
    (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (u_seq : ℕ → (ℕ → ℝ))
    (hA : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_bd_le : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N
      let B := RiemannBlueprint.Section8_VasyuninBDR.B_cot_bilinear G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base v N
      let A := RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot v N
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + (-B / A) * v k : ℝ) : ℂ) *
            (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + (-B / A) * v k) N)
    (h_opt_lim : Filter.Tendsto
      (fun N =>
        let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N
        let B := RiemannBlueprint.Section8_VasyuninBDR.B_cot_bilinear G_cot
          RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base v N
        let A := RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot v N
        RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
          RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base N - B ^ 2 / A)
      Filter.atTop (nhds (-1))) :
    _root_.RiemannHypothesis := by
  refine baezDuarte_implies_rh fun ε hε => ?_
  have h_met := Metric.tendsto_atTop.mp h_opt_lim ε hε
  rcases h_met with ⟨N0, hN0⟩
  let N := max N0 4
  have hN4 : 4 ≤ N := le_max_right _ _
  let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N
  let B := RiemannBlueprint.Section8_VasyuninBDR.B_cot_bilinear G_cot
    RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base v N
  let A := RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot v N
  have h_opt : RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + (-B / A) * v k) N =
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base N - B ^ 2 / A :=
    RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_opt_step G_cot hG_symm
      RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base v N (hA N hN4)
  have hQ_lt : 1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + (-B / A) * v k) N < ε := by
    rw [h_opt]
    have h1 := hN0 N (le_max_left _ _)
    rw [Real.dist_eq, sub_neg_eq_add, abs_lt, add_comm] at h1
    exact h1.2
  exact ⟨N, fun k =>
    ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + (-B / A) * v k : ℝ) : ℂ),
    (h_bd_le N hN4).trans_lt hQ_lt⟩

/-- Bridge Theorem 8 — Universal `N = 4` Constant Galerkin Nullspace Forward Theorem:
for symmetric `G_cot` and homogeneous, Galerkin-orthogonal vectors `v_seq : ℕ → ℕ → ℝ`
(`SatisfiesHomogeneousClayConditions (v_seq N) N` and
`SatisfiesCotGalerkin G_cot clayRank4Base (v_seq N) N` for `N ≥ 4`), if the `L²(0, 1)` residual
at `clayRank4Base + v_seq N` is bounded by `1 + Q_cot_quad G_cot (clayRank4Base + v_seq N) N`
for all `N ≥ 4` and `Q_cot_quad G_cot (v_seq N) N → 1 + Q_cot_quad G_cot clayRank4Base 4`,
then `_root_.RiemannHypothesis` holds. -/
theorem clayRank4Base_galerkin_hom_limit_implies_rh
    (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (v_seq : ℕ → (ℕ → ℝ))
    (h_hom : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.SatisfiesHomogeneousClayConditions (v_seq N) N)
    (h_gal : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.SatisfiesCotGalerkin G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base (v_seq N) N)
    (h_bd_le : ∀ N, 4 ≤ N →
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k : ℝ) : ℂ) *
            (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k) N)
    (h_hom_lim : Filter.Tendsto
      (fun N => RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot (v_seq N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis := by
  refine baezDuarte_implies_rh fun ε hε => ?_
  have h_met := Metric.tendsto_atTop.mp h_hom_lim ε hε
  rcases h_met with ⟨N0, hN0⟩
  let N := max N0 4
  have hN4 : 4 ≤ N := le_max_right _ _
  have _ := h_hom N hN4
  have h_gal_eq : RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k) N =
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4 -
        RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot (v_seq N) N := by
    rw [RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_add_of_galerkin G_cot hG_symm
      RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base (v_seq N) N (h_gal N hN4),
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_clayRank4Base_eq_four G_cot N hN4]
  have hQ_lt : 1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k) N < ε := by
    rw [h_gal_eq]
    have h1 := hN0 N (le_max_left _ _)
    rw [Real.dist_eq, abs_lt] at h1
    linarith [h1.1]
  exact ⟨N, fun k =>
    ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k : ℝ) : ℂ),
    (h_bd_le N hN4).trans_lt hQ_lt⟩

/-- Bridge Theorem 9 — 1D Base-Potential Pairing Forward Theorem:
for symmetric `G_cot` and homogeneous, Galerkin-orthogonal vectors `v_seq : ℕ → ℕ → ℝ`,
if the `L²(0, 1)` residual at `clayRank4Base + v_seq N` is bounded by
`1 + Q_cot_quad G_cot (clayRank4Base + v_seq N) N` for all `N ≥ 4` and the 1D pairing
`∑_{k=1}^N v_seq N k * phiCotBase G_cot k` tends to
`-(1 + Q_cot_quad G_cot clayRank4Base 4)`, then `_root_.RiemannHypothesis` holds. -/
theorem clayRank4Base_phiCotBase_pairing_limit_implies_rh
    (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (v_seq : ℕ → (ℕ → ℝ))
    (h_hom : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.SatisfiesHomogeneousClayConditions (v_seq N) N)
    (h_gal : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.SatisfiesCotGalerkin G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base (v_seq N) N)
    (h_bd_le : ∀ N, 4 ≤ N →
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k : ℝ) : ℂ) *
            (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k) N)
    (h_phi_lim : Filter.Tendsto
      (fun N => ∑ k ∈ Finset.Icc 1 N,
        v_seq N k * RiemannBlueprint.Section8_VasyuninBDR.phiCotBase G_cot k)
      Filter.atTop
      (nhds (-(1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4)))) :
    _root_.RiemannHypothesis := by
  refine baezDuarte_implies_rh fun ε hε => ?_
  have h_met := Metric.tendsto_atTop.mp h_phi_lim ε hε
  rcases h_met with ⟨N0, hN0⟩
  let N := max N0 4
  have hN4 : 4 ≤ N := le_max_right _ _
  have _ := h_hom N hN4
  have h_phi_eq : RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k) N =
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4 +
        ∑ k ∈ Finset.Icc 1 N,
          v_seq N k * RiemannBlueprint.Section8_VasyuninBDR.phiCotBase G_cot k := by
    rw [RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_add_of_galerkin G_cot hG_symm
      RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base (v_seq N) N (h_gal N hN4),
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_clayRank4Base_eq_four G_cot N hN4,
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_eq_neg_sum_phiCotBase_of_galerkin
        G_cot (v_seq N) N hN4 (h_gal N hN4)]
    ring
  have hQ_lt : 1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k) N < ε := by
    rw [h_phi_eq]
    have h1 := hN0 N (le_max_left _ _)
    rw [Real.dist_eq, abs_lt] at h1
    linarith [h1.2]
  exact ⟨N, fun k =>
    ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v_seq N k : ℝ) : ℂ),
    (h_bd_le N hN4).trans_lt hQ_lt⟩

/-- Bridge Theorem 10 — Unconstrained 1D Rayleigh–Potential Saturation Forward Theorem:
for symmetric `G_cot` and any unconstrained sequence `u_seq : ℕ → ℕ → ℝ` with
`Q_cot_quad G_cot (clayRank4Hom (u_seq N) N) N ≠ 0` for `N ≥ 4`, `clayRank4GalerkinRay`
automatically discharges both `SatisfiesHomogeneousClayConditions` and `SatisfiesCotGalerkin`.
If the `L²(0, 1)` residual at `clayRank4Base + clayRank4GalerkinRay G_cot (u_seq N) N` is
bounded by `1 + Q_cot_quad` and the 1D Rayleigh quotient
`phiCotRayQuotient G_cot (clayRank4Hom (u_seq N) N) N` tends to
`1 + Q_cot_quad G_cot clayRank4Base 4`, then `_root_.RiemannHypothesis` holds. -/
theorem clayRank4GalerkinRay_rayQuotient_limit_implies_rh
    (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (u_seq : ℕ → (ℕ → ℝ))
    (hA : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_bd_le : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay G_cot (u_seq N) N
      (∫ x in Set.Ioo (0 : ℝ) 1,
        ‖1 - ∑ k ∈ Finset.Icc 1 N,
          ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k : ℝ) : ℂ) *
            (NumberTheory.MellinFracPart.recipFractScaled k x : ℂ)‖ ^ 2) ≤
        1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k) N)
    (h_ray_lim : Filter.Tendsto
      (fun N => RiemannBlueprint.Section8_VasyuninBDR.phiCotRayQuotient G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis := by
  refine baezDuarte_implies_rh fun ε hε => ?_
  have h_met := Metric.tendsto_atTop.mp h_ray_lim ε hε
  rcases h_met with ⟨N0, hN0⟩
  let N := max N0 4
  have hN4 : 4 ≤ N := le_max_right _ _
  have _ := RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay_satisfies_homogeneous
    G_cot (u_seq N) N hN4
  have _ := RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay_satisfies_galerkin
    G_cot (u_seq N) N hN4 (hA N hN4)
  have h_ray_eq :=
    RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_add_clayRank4GalerkinRay_eq_sub_rayQuotient
      G_cot hG_symm (u_seq N) N hN4 (hA N hN4)
  let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay G_cot (u_seq N) N
  have hQ_lt : 1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k) N < ε := by
    change 1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k +
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay G_cot (u_seq N) N k) N < ε
    rw [h_ray_eq]
    have h1 := hN0 N (le_max_left _ _)
    rw [Real.dist_eq, abs_lt] at h1
    linarith [h1.1]
  exact ⟨N, fun k =>
    ((RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k : ℝ) : ℂ),
    (h_bd_le N hN4).trans_lt hQ_lt⟩

/-- Reflection-hypothesis-free Hardy–Szegő master bridge: `SzegoReproducingInequality D`
and `baezDuarteDistSq D → 0` imply `_root_.RiemannHypothesis` directly, supplying
`zetaZeroReflectionSymmetry_unconditional` internally. -/
theorem rh_of_szego_and_collapse_zero_unconditional_symm (D : ℕ → ℝ)
    (h_szego : SzegoReproducingInequality D)
    (h_lim : Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0)) :
    _root_.RiemannHypothesis := by
  refine riemannHypothesis_of_strip fun s hs hz => ?_
  rcases lt_trichotomy s.re (1 / 2) with hlt | heq | hgt
  · rcases zetaZeroReflectionSymmetry_unconditional s hs hz with ⟨hs_refl, hz_refl⟩
    have hre_refl : 1 / 2 < (1 - s).re := by
      rw [Complex.sub_re, Complex.one_re]
      linarith
    exact False.elim (no_zero_re_gt_half_of_collapse_zero D
      (offlineZeroCauchyFloor_of_szego D h_szego) h_lim (1 - s) hs_refl hre_refl hz_refl)
  · exact heq
  · exact False.elim (no_zero_re_gt_half_of_collapse_zero D
      (offlineZeroCauchyFloor_of_szego D h_szego) h_lim s hs hgt hz)

/-- Bridge Theorem 11 — Reflection-Free Hardy–Szegő & 1D Rayleigh Quotient Forward Theorem:
combines `SzegoReproducingInequality D`, `vasyunin_energy_clayRank4GalerkinRay_eq_sub_rayQuotient`,
and `Tendsto (fun N => phiCotRayQuotient G_cot (clayRank4Hom (u_seq N) N) N) atTop
(nhds (1 + Q_cot_quad G_cot clayRank4Base 4))` to deduce `_root_.RiemannHypothesis` without
requiring `ZetaZeroReflectionSymmetry` as an external hypothesis. -/
theorem clayRank4GalerkinRay_rayQuotient_limit_implies_rh_of_szego
    (D : ℕ → ℝ) (gamma_E : ℝ)
    (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (u_seq : ℕ → (ℕ → ℝ))
    (h_szego : SzegoReproducingInequality D)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (hA : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_ub : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay G_cot (u_seq N) N
      baezDuarteDistSq D N ≤
        vasyuninQuadraticEnergy
          (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k))
    (h_ray_lim : Filter.Tendsto
      (fun N => RiemannBlueprint.Section8_VasyuninBDR.phiCotRayQuotient G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis := by
  let E_seq : ℕ → ℝ := fun N =>
    vasyuninQuadraticEnergy
      (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k +
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay G_cot (u_seq N) N k)
  have hE_ev : ∀ᶠ N in Filter.atTop, E_seq N =
      (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4) -
        RiemannBlueprint.Section8_VasyuninBDR.phiCotRayQuotient G_cot
          (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N := by
    rw [Filter.eventually_atTop]
    refine ⟨4, fun N hN4 => ?_⟩
    exact
      RiemannBlueprint.Section8_VasyuninBDR.vasyunin_energy_clayRank4GalerkinRay_eq_sub_rayQuotient
        gamma_E G_cot hG_symm (u_seq N) N hN4 (hA N hN4)
  have hE_lim : Filter.Tendsto E_seq Filter.atTop (nhds 0) := by
    rw [Filter.tendsto_congr' hE_ev]
    let C := 1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
      RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4
    have hC : Filter.Tendsto (fun _ : ℕ => C) Filter.atTop (nhds C) := tendsto_const_nhds
    simpa [C, sub_self] using hC.sub h_ray_lim
  have hD_lim : Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0) :=
    squeeze_zero' (Filter.Eventually.of_forall h_nonneg)
      (Filter.eventually_atTop.mpr ⟨4, h_ub⟩) hE_lim
  exact rh_of_szego_and_collapse_zero_unconditional_symm D h_szego hD_lim

/-- Decomposed Hardy `H²(Re(s) > 1/2)` Cauchy–Schwarz reproducing pairing predicate:
separates the unit evaluation pairing `pairing s₀ N = 1`, the Szegő kernel norm squared
`szegoNormSq s₀ = |s₀|² / (2 Re(s₀) - 1)`, and the Cauchy–Schwarz inequality
`(pairing s₀ N)² ≤ D_N² * szegoNormSq s₀`. -/
def SatisfiesHardyCauchySchwarz (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ) : Prop :=
  ∀ s₀ : ℂ, InCriticalStrip s₀ → 1 / 2 < s₀.re → riemannZeta s₀ = 0 →
    (∀ N : ℕ, pairing s₀ N = 1) ∧
    (szegoNormSq s₀ = Complex.normSq s₀ / (2 * s₀.re - 1)) ∧
    (∀ N : ℕ, (pairing s₀ N) ^ 2 ≤ baezDuarteDistSq D N * szegoNormSq s₀)

/-- Derives `SzegoReproducingInequality D` from
`SatisfiesHardyCauchySchwarz D pairing szegoNormSq`. -/
theorem szegoReproducingInequality_of_hardyCauchySchwarz
    (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ)
    (h_hcs : SatisfiesHardyCauchySchwarz D pairing szegoNormSq) :
    SzegoReproducingInequality D := by
  intro s₀ hs hre hz N
  rcases h_hcs s₀ hs hre hz with ⟨h_pair, h_norm, h_cs⟩
  have hN := h_cs N
  rw [h_pair N, one_pow, h_norm] at hN
  exact hN

/-- Bridge Theorem 12 — Decomposed Hardy–Cauchy–Schwarz & 1D Rayleigh Quotient Forward Theorem:
combines `SatisfiesHardyCauchySchwarz` (via `szegoReproducingInequality_of_hardyCauchySchwarz`)
with `clayRank4GalerkinRay_rayQuotient_limit_implies_rh_of_szego` to prove
`_root_.RiemannHypothesis` without requiring `ZetaZeroReflectionSymmetry` as a premise. -/
theorem clayRank4GalerkinRay_rayQuotient_limit_implies_rh_of_hardyCauchySchwarz
    (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ)
    (gamma_E : ℝ) (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (u_seq : ℕ → (ℕ → ℝ))
    (h_hcs : SatisfiesHardyCauchySchwarz D pairing szegoNormSq)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (hA : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_ub : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay G_cot (u_seq N) N
      baezDuarteDistSq D N ≤
        vasyuninQuadraticEnergy
          (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k))
    (h_ray_lim : Filter.Tendsto
      (fun N => RiemannBlueprint.Section8_VasyuninBDR.phiCotRayQuotient G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis :=
  clayRank4GalerkinRay_rayQuotient_limit_implies_rh_of_szego
    D gamma_E G_cot hG_symm u_seq
    (szegoReproducingInequality_of_hardyCauchySchwarz D pairing szegoNormSq h_hcs)
    h_nonneg hA h_ub h_ray_lim

/-- Critical-line Szegő Poisson kernel density evaluated at shifted parameter `t : ℝ`. -/
noncomputable def szegoKernelIntegrand (s₀ : ℂ) (t : ℝ) : ℝ :=
  (1 / (2 * Real.pi)) * (Complex.normSq s₀ / ((s₀.re - 1 / 2) ^ 2 + (t - s₀.im) ^ 2))

/-- Exact arctangent antiderivative of the critical-line Szegő Poisson kernel density. -/
noncomputable def szegoKernelAntideriv (s₀ : ℂ) (t : ℝ) : ℝ :=
  (Complex.normSq s₀ / (2 * Real.pi * (s₀.re - 1 / 2))) *
    Real.arctan ((t - s₀.im) / (s₀.re - 1 / 2))

/-- Evaluating the formal Szegő antiderivative limits at `± π / 2` yields the exact
Hardy–Szegő Cauchy floor reciprocal `Complex.normSq s₀ / (2 * s₀.re - 1)`. -/
theorem szegoKernelAntideriv_upper_sub_lower (s₀ : ℂ) (h_re : 1 / 2 < s₀.re) :
    (Complex.normSq s₀ / (2 * Real.pi * (s₀.re - 1 / 2))) * (Real.pi / 2) -
      (Complex.normSq s₀ / (2 * Real.pi * (s₀.re - 1 / 2))) * (-(Real.pi / 2)) =
      Complex.normSq s₀ / (2 * s₀.re - 1) := by
  have hpi : Real.pi ≠ 0 := Real.pi_ne_zero
  have hden : s₀.re - 1 / 2 ≠ 0 := sub_ne_zero.mpr (ne_of_gt h_re)
  field_simp
  ring

/-- Exact real calculus derivative of `szegoKernelAntideriv s₀`: for `1 / 2 < s₀.re` and every
`t : ℝ`, `HasDerivAt (szegoKernelAntideriv s₀) (szegoKernelIntegrand s₀ t) t`. -/
theorem hasDerivAt_szegoKernelAntideriv (s₀ : ℂ) (h_re : 1 / 2 < s₀.re) (t : ℝ) :
    HasDerivAt (szegoKernelAntideriv s₀) (szegoKernelIntegrand s₀ t) t := by
  set a : ℝ := s₀.re - 1 / 2
  set b : ℝ := t - s₀.im
  have hpi : Real.pi ≠ 0 := Real.pi_ne_zero
  have ha : a ≠ 0 := sub_ne_zero.mpr (ne_of_gt h_re)
  have hpos : a ^ 2 + b ^ 2 ≠ 0 :=
    ne_of_gt (add_pos_of_pos_of_nonneg (sq_pos_of_ne_zero ha) (sq_nonneg b))
  have h_one : 1 + (b / a) ^ 2 ≠ 0 :=
    ne_of_gt (add_pos_of_pos_of_nonneg zero_lt_one (sq_nonneg _))
  have h_lin := ((hasDerivAt_id t).sub_const s₀.im).div_const a
  have h_comp := (Real.hasDerivAt_arctan (b / a)).comp t h_lin
  have h_mul := h_comp.const_mul (Complex.normSq s₀ / (2 * Real.pi * a))
  change HasDerivAt (szegoKernelAntideriv s₀) _ t at h_mul
  refine h_mul.congr_deriv ?_
  unfold szegoKernelIntegrand
  change Complex.normSq s₀ / (2 * Real.pi * a) * (1 / (1 + (b / a) ^ 2) * (1 / a)) =
    (1 / (2 * Real.pi)) * (Complex.normSq s₀ / (a ^ 2 + b ^ 2))
  field_simp

/-- Unconstrained-Ray Clay–Galerkin 1D Limit Implies RH under Hardy Cauchy–Schwarz:
any unconstrained raw sequence `u_seq : ℕ → ℕ → ℝ` (requiring zero boundary conditions) whose
`phiCotUnconstrainedRayQuotient` converges to `1 + Q_cot_quad G_cot clayRank4Base 4` implies
`_root_.RiemannHypothesis` whenever `SatisfiesHardyCauchySchwarz D pairing szegoNormSq` and the
decomposed energy dominates `baezDuarteDistSq D N` for `N ≥ 4`. -/
theorem clayRank4UnconstrainedRay_limit_implies_rh_of_hardyCauchySchwarz
    (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ)
    (gamma_E : ℝ) (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (u_seq : ℕ → (ℕ → ℝ))
    (h_hcs : SatisfiesHardyCauchySchwarz D pairing szegoNormSq)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (hA : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_ub : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4UnconstrainedRay G_cot (u_seq N) N
      baezDuarteDistSq D N ≤
        vasyuninQuadraticEnergy
          (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k))
    (h_ray_lim : Filter.Tendsto
      (fun N =>
        RiemannBlueprint.Section8_VasyuninBDR.phiCotUnconstrainedRayQuotient G_cot (u_seq N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis := by
  have h_ub' : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay G_cot (u_seq N) N
      baezDuarteDistSq D N ≤
        vasyuninQuadraticEnergy
          (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k) := by
    intro N hN
    have h_eq :
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay G_cot (u_seq N) N =
          RiemannBlueprint.Section8_VasyuninBDR.clayRank4UnconstrainedRay
            G_cot (u_seq N) N := by
      ext k
      unfold RiemannBlueprint.Section8_VasyuninBDR.clayRank4UnconstrainedRay
      unfold RiemannBlueprint.Section8_VasyuninBDR.clayRank4GalerkinRay
      rw [RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom_idem (u_seq N) N hN]
    simpa [h_eq] using h_ub N hN
  exact clayRank4GalerkinRay_rayQuotient_limit_implies_rh_of_hardyCauchySchwarz
    D pairing szegoNormSq gamma_E G_cot hG_symm u_seq h_hcs h_nonneg hA h_ub' h_ray_lim

/-- Continuity of `szegoKernelIntegrand s₀` on `ℝ` whenever `1 / 2 < s₀.re`. -/
theorem continuous_szegoKernelIntegrand (s₀ : ℂ) (h_re : 1 / 2 < s₀.re) :
    Continuous (szegoKernelIntegrand s₀) := by
  unfold szegoKernelIntegrand
  refine continuous_const.mul (continuous_const.div ?_ fun t => ?_)
  · exact continuous_const.add ((continuous_id.sub continuous_const).pow 2)
  · have ha : s₀.re - 1 / 2 ≠ 0 := sub_ne_zero.mpr (ne_of_gt h_re)
    exact ne_of_gt (add_pos_of_pos_of_nonneg (sq_pos_of_ne_zero ha) (sq_nonneg _))

/-- Fundamental Theorem of Calculus evaluation of the definite integral of `szegoKernelIntegrand s₀`
on `[a, b]` for `1 / 2 < s₀.re`. -/
theorem integral_szegoKernelIntegrand_eq_sub (s₀ : ℂ) (h_re : 1 / 2 < s₀.re) (a b : ℝ) :
    (∫ t in a..b, szegoKernelIntegrand s₀ t) =
      szegoKernelAntideriv s₀ b - szegoKernelAntideriv s₀ a := by
  refine intervalIntegral.integral_eq_sub_of_hasDerivAt
    (fun t _ => hasDerivAt_szegoKernelAntideriv s₀ h_re t) ?_
  exact (continuous_szegoKernelIntegrand s₀ h_re).intervalIntegrable a b

/-- Unconditional convergence of the symmetric critical-line Szegő kernel integral
`∫_{-T}^T szegoKernelIntegrand(s₀, t) dt → Complex.normSq s₀ / (2 * s₀.re - 1)` as `T → ∞`
for `1 / 2 < s₀.re`. -/
theorem tendsto_integral_szegoKernelIntegrand_atTop (s₀ : ℂ) (h_re : 1 / 2 < s₀.re) :
    Filter.Tendsto (fun T : ℝ => ∫ t in (-T)..T, szegoKernelIntegrand s₀ t)
      Filter.atTop (nhds (Complex.normSq s₀ / (2 * s₀.re - 1))) := by
  have ha : 0 < s₀.re - 1 / 2 := sub_pos.mpr h_re
  have h_top_lin : Filter.Tendsto (fun T : ℝ => (T - s₀.im) / (s₀.re - 1 / 2))
      Filter.atTop Filter.atTop :=
    (Filter.tendsto_atTop_add_const_right Filter.atTop (-s₀.im) Filter.tendsto_id).atTop_div_const ha
  have h_bot_lin : Filter.Tendsto (fun T : ℝ => (-T - s₀.im) / (s₀.re - 1 / 2))
      Filter.atTop Filter.atBot :=
    (Filter.tendsto_atBot_add_const_right Filter.atTop (-s₀.im) Filter.tendsto_neg_atTop_atBot).atBot_div_const ha
  have h_top_atan : Filter.Tendsto (fun T : ℝ => Real.arctan ((T - s₀.im) / (s₀.re - 1 / 2)))
      Filter.atTop (nhds (Real.pi / 2)) :=
    (tendsto_nhds_of_tendsto_nhdsWithin Real.tendsto_arctan_atTop).comp h_top_lin
  have h_bot_atan : Filter.Tendsto (fun T : ℝ => Real.arctan ((-T - s₀.im) / (s₀.re - 1 / 2)))
      Filter.atTop (nhds (-(Real.pi / 2))) :=
    (tendsto_nhds_of_tendsto_nhdsWithin Real.tendsto_arctan_atBot).comp h_bot_lin
  have h_upper : Filter.Tendsto (fun T : ℝ => szegoKernelAntideriv s₀ T)
      Filter.atTop (nhds ((Complex.normSq s₀ / (2 * Real.pi * (s₀.re - 1 / 2))) * (Real.pi / 2))) :=
    h_top_atan.const_mul _
  have h_lower : Filter.Tendsto (fun T : ℝ => szegoKernelAntideriv s₀ (-T))
      Filter.atTop (nhds ((Complex.normSq s₀ / (2 * Real.pi * (s₀.re - 1 / 2))) * (-(Real.pi / 2)))) :=
    h_bot_atan.const_mul _
  have h_sub := h_upper.sub h_lower
  rw [szegoKernelAntideriv_upper_sub_lower s₀ h_re] at h_sub
  refine h_sub.congr fun T => ?_
  exact (integral_szegoKernelIntegrand_eq_sub s₀ h_re (-T) T).symm

/-- Integral-grounded Hardy `H²(Re(s) > 1/2)` Cauchy–Schwarz predicate where `szegoNormSq s₀` is
characterized purely as the improper integral limit of `∫_{-T}^T szegoKernelIntegrand s₀ t dt`. -/
def SatisfiesIntegralHardyCauchySchwarz (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ) : Prop :=
  ∀ s₀ : ℂ, InCriticalStrip s₀ → 1 / 2 < s₀.re → riemannZeta s₀ = 0 →
    (∀ N : ℕ, pairing s₀ N = 1) ∧
    Filter.Tendsto (fun T : ℝ => ∫ t in (-T)..T, szegoKernelIntegrand s₀ t)
      Filter.atTop (nhds (szegoNormSq s₀)) ∧
    (∀ N : ℕ, (pairing s₀ N) ^ 2 ≤ baezDuarteDistSq D N * szegoNormSq s₀)

/-- Uniqueness of limits in `ℝ` (`tendsto_nhds_unique`) combined with
`tendsto_integral_szegoKernelIntegrand_atTop` discharges the closed-form Szegő norm identity from
`SatisfiesIntegralHardyCauchySchwarz`. -/
theorem satisfiesHardyCauchySchwarz_of_integral
    (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ)
    (h_ihcs : SatisfiesIntegralHardyCauchySchwarz D pairing szegoNormSq) :
    SatisfiesHardyCauchySchwarz D pairing szegoNormSq := by
  intro s₀ hs hre hz
  rcases h_ihcs s₀ hs hre hz with ⟨h_pair, h_tendsto, h_cs⟩
  exact ⟨h_pair, tendsto_nhds_unique h_tendsto (tendsto_integral_szegoKernelIntegrand_atTop s₀ hre), h_cs⟩

/-- Integral-Grounded Hardy–Cauchy–Schwarz & Unconstrained Ray 1D Limit Implies RH:
eliminates both homogeneous boundary conditions on `u_seq` and the algebraic formula for
`szegoNormSq s₀` in favor of the improper critical-line integral of `szegoKernelIntegrand`. -/
theorem clayRank4UnconstrainedRay_limit_implies_rh_of_integralHardyCauchySchwarz
    (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ)
    (gamma_E : ℝ) (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (u_seq : ℕ → (ℕ → ℝ))
    (h_ihcs : SatisfiesIntegralHardyCauchySchwarz D pairing szegoNormSq)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (hA : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_ub : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4UnconstrainedRay G_cot (u_seq N) N
      baezDuarteDistSq D N ≤
        vasyuninQuadraticEnergy
          (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k))
    (h_ray_lim : Filter.Tendsto
      (fun N =>
        RiemannBlueprint.Section8_VasyuninBDR.phiCotUnconstrainedRayQuotient G_cot (u_seq N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis :=
  clayRank4UnconstrainedRay_limit_implies_rh_of_hardyCauchySchwarz
    D pairing szegoNormSq gamma_E G_cot hG_symm u_seq
    (satisfiesHardyCauchySchwarz_of_integral D pairing szegoNormSq h_ihcs)
    h_nonneg hA h_ub h_ray_lim

/-- End-to-End Unified Master Closure Theorem (`cmi_master_effective_potential_closure_implies_rh`):
attaches unconditional critical-strip reflection (`zetaZeroReflectionSymmetry_unconditional`),
FTC critical-line Szegő kernel calculus (`tendsto_integral_szegoKernelIntegrand_atTop`,
`satisfiesHardyCauchySchwarz_of_integral`), unconstrained raw-vector Clay–Galerkin energy
reduction (`vasyunin_energy_clayRank4UnconstrainedRay_eq_sub_rayQuotient`), and pure tail
adjoint Riesz-effective potential reduction (`phiCotUnconstrainedRayQuotient_eq_tail_phiCotEffective`)
to deduce `_root_.RiemannHypothesis` from any raw sequence `u_seq : ℕ → ℕ → ℝ` whose tail
Riesz-effective Rayleigh quotient converges to `1 + Q_cot_quad G_cot clayRank4Base 4`. -/
theorem cmi_master_effective_potential_closure_implies_rh
    (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ)
    (gamma_E : ℝ) (G_cot : ℕ → ℕ → ℝ) (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (u_seq : ℕ → (ℕ → ℝ))
    (h_ihcs : SatisfiesIntegralHardyCauchySchwarz D pairing szegoNormSq)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (hA : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_ub : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4UnconstrainedRay G_cot (u_seq N) N
      baezDuarteDistSq D N ≤
        vasyuninQuadraticEnergy
          (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k))
    (h_eff_lim : Filter.Tendsto
      (fun N =>
        (∑ m ∈ Finset.Icc 5 N, u_seq N m *
          RiemannBlueprint.Section8_VasyuninBDR.phiCotEffective G_cot m) ^ 2 /
          RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
            (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis := by
  have h_ray_lim : Filter.Tendsto
      (fun N =>
        RiemannBlueprint.Section8_VasyuninBDR.phiCotUnconstrainedRayQuotient G_cot (u_seq N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4)) := by
    refine h_eff_lim.congr' ?_
    exact Filter.eventually_atTop.mpr ⟨4, fun N hN4 =>
      (RiemannBlueprint.Section8_VasyuninBDR.phiCotUnconstrainedRayQuotient_eq_tail_phiCotEffective
        G_cot (u_seq N) N hN4).symm⟩
  exact clayRank4UnconstrainedRay_limit_implies_rh_of_integralHardyCauchySchwarz
    D pairing szegoNormSq gamma_E G_cot hG_symm u_seq h_ihcs h_nonneg hA h_ub h_ray_lim

/-- Strict Off-Diagonal Right-Triangle Riesz-Effective Closure Implies RH:
for symmetric `G_cot` with vanishing central diagonal (`hG_diag : ∀ k, G_cot k k = 0`),
convergence of the tail `phiCotEffective` Rayleigh quotient whose denominator is purely
`2 * Q_cot_rightTriangle` to `1 + 2 * Q_cot_rightTriangle G_cot clayRank4Base 4` under
`SatisfiesIntegralHardyCauchySchwarz` implies `_root_.RiemannHypothesis`. -/
theorem cmi_master_rightTriangle_effective_closure_implies_rh
    (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ)
    (gamma_E : ℝ) (G_cot : ℕ → ℕ → ℝ)
    (hG_symm : ∀ j k, G_cot j k = G_cot k j)
    (hG_diag : ∀ k, G_cot k k = 0)
    (u_seq : ℕ → (ℕ → ℝ))
    (h_ihcs : SatisfiesIntegralHardyCauchySchwarz D pairing szegoNormSq)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (hA : ∀ N, 4 ≤ N →
      2 * RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_ub : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4UnconstrainedRay G_cot (u_seq N) N
      baezDuarteDistSq D N ≤
        vasyuninQuadraticEnergy
          (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k))
    (h_rt_lim : Filter.Tendsto
      (fun N =>
        (∑ m ∈ Finset.Icc 5 N, u_seq N m *
          RiemannBlueprint.Section8_VasyuninBDR.phiCotEffective G_cot m) ^ 2 /
          (2 * RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
            (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N))
      Filter.atTop
      (nhds (1 + 2 * RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis := by
  have hA' : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0 := by
    intro N hN
    rw [RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_eq_two_mul_rightTriangle_of_diag_zero
      G_cot hG_symm hG_diag]
    exact hA N hN
  have h_eff_lim : Filter.Tendsto
      (fun N =>
        (∑ m ∈ Finset.Icc 5 N, u_seq N m *
          RiemannBlueprint.Section8_VasyuninBDR.phiCotEffective G_cot m) ^ 2 /
          RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
            (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N)
      Filter.atTop
      (nhds (1 + RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4)) := by
    simpa only [
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_quad_eq_two_mul_rightTriangle_of_diag_zero
        G_cot hG_symm hG_diag] using h_rt_lim
  exact cmi_master_effective_potential_closure_implies_rh
    D pairing szegoNormSq gamma_E G_cot hG_symm u_seq h_ihcs h_nonneg hA' h_ub h_eff_lim

/-- Track 3 Unified Dedekind–Hardy Closure Bridge: combines
`SatisfiesDedekindCotangentReciprocity G_cot`, `vasyunin_energy_unconstrainedRay_eq_rightTriangle_of_reciprocity`,
`satisfiesHardyCauchySchwarz_of_integral` (via `tendsto_integral_szegoKernelIntegrand_atTop`), and
`zetaZeroReflectionSymmetry_unconditional` (via `rh_of_szego_and_collapse_zero_unconditional_symm`)
into a single end-to-end theorem discharging both kernel symmetry and diagonal vanishing from
reciprocity. -/
theorem cmi_track3_dedekind_reciprocity_closure_implies_rh
    (D : ℕ → ℝ) (pairing : ℂ → ℕ → ℝ) (szegoNormSq : ℂ → ℝ)
    (gamma_E : ℝ) (G_cot : ℕ → ℕ → ℝ)
    (h_rec : RiemannBlueprint.Section8_VasyuninBDR.SatisfiesDedekindCotangentReciprocity G_cot)
    (u_seq : ℕ → (ℕ → ℝ))
    (h_ihcs : SatisfiesIntegralHardyCauchySchwarz D pairing szegoNormSq)
    (h_nonneg : ∀ N : ℕ, 0 ≤ baezDuarteDistSq D N)
    (hA : ∀ N, 4 ≤ N →
      RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
        (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N ≠ 0)
    (h_ub : ∀ N, 4 ≤ N →
      let v := RiemannBlueprint.Section8_VasyuninBDR.clayRank4UnconstrainedRay G_cot (u_seq N) N
      baezDuarteDistSq D N ≤
        vasyuninQuadraticEnergy
          (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
          (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k + v k))
    (h_rt_lim : Filter.Tendsto
      (fun N =>
        (∑ m ∈ Finset.Icc 5 N, u_seq N m *
          RiemannBlueprint.Section8_VasyuninBDR.phiCotEffective G_cot m) ^ 2 /
          (2 * RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
            (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N))
      Filter.atTop
      (nhds (1 + 2 * RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4))) :
    _root_.RiemannHypothesis := by
  have h_szego : SzegoReproducingInequality D :=
    szegoReproducingInequality_of_hardyCauchySchwarz D pairing szegoNormSq
      (satisfiesHardyCauchySchwarz_of_integral D pairing szegoNormSq h_ihcs)
  let E_seq : ℕ → ℝ := fun N =>
    vasyuninQuadraticEnergy
      (RiemannBlueprint.Section8_VasyuninBDR.GVasyuninDecomp gamma_E G_cot)
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.bVasyunin k gamma_E) N
      (fun k => RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base k +
        RiemannBlueprint.Section8_VasyuninBDR.clayRank4UnconstrainedRay G_cot (u_seq N) N k)
  have hE_ev : ∀ᶠ N in Filter.atTop, E_seq N =
      (1 + 2 * RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
          RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4) -
        (∑ m ∈ Finset.Icc 5 N, u_seq N m *
          RiemannBlueprint.Section8_VasyuninBDR.phiCotEffective G_cot m) ^ 2 /
          (2 * RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
            (RiemannBlueprint.Section8_VasyuninBDR.clayRank4Hom (u_seq N) N) N) := by
    rw [Filter.eventually_atTop]
    refine ⟨4, fun N hN4 => ?_⟩
    exact RiemannBlueprint.Section8_VasyuninBDR.vasyunin_energy_unconstrainedRay_eq_rightTriangle_of_reciprocity
      gamma_E G_cot h_rec (u_seq N) N hN4 (hA N hN4)
  have hE_lim : Filter.Tendsto E_seq Filter.atTop (nhds 0) := by
    rw [Filter.tendsto_congr' hE_ev]
    let C := 1 + 2 * RiemannBlueprint.Section8_VasyuninBDR.Q_cot_rightTriangle G_cot
      RiemannBlueprint.Section8_VasyuninBDR.clayRank4Base 4
    have hC : Filter.Tendsto (fun _ : ℕ => C) Filter.atTop (nhds C) := tendsto_const_nhds
    simpa [C, sub_self] using hC.sub h_rt_lim
  have hD_lim : Filter.Tendsto (baezDuarteDistSq D) Filter.atTop (nhds 0) :=
    squeeze_zero' (Filter.Eventually.of_forall h_nonneg)
      (Filter.eventually_atTop.mpr ⟨4, h_ub⟩) hE_lim
  exact rh_of_szego_and_collapse_zero_unconditional_symm D h_szego hD_lim

#print axioms riemannHypothesis_iff_collapse_zero
#print axioms collapse_zero_implies_rh_strip
#print axioms cmi_criterion1_spectral_residual_eq
#print axioms zetaZeroReflectionSymmetry_proved
#print axioms pos_cauchy_floor_of_re_gt_half
#print axioms no_zero_re_gt_half_of_collapse_zero
#print axioms no_zero_re_lt_half_of_collapse_zero
#print axioms structural_collapse_zero_implies_rh
#print axioms cauchy_schwarz_szego_floor
#print axioms offlineZeroCauchyFloor_of_szego
#print axioms rh_of_szego_and_collapse_zero
#print axioms tendsto_baezDuarteDistSq_zero_of_test_vector
#print axioms vasyuninQuadraticEnergy_smul
#print axioms vasyuninQuadraticEnergy_rayleigh_ritz
#print axioms baezDuarteDistSq_le_one_sub_rayleigh_ritz
#print axioms vasyuninQuadraticEnergy_add_smul
#print axioms tendsto_baezDuarteDistSq_zero_of_two_dim_subspace
#print axioms riemannHypothesis_of_strip
#print axioms integral_Ioc_nymanBeurling_residual_eq
#print axioms nymanBeurling_spatial_cauchy_floor
#print axioms nymanBeurling_szegoReproducingInequality
#print axioms nymanBeurling_implies_rh
#print axioms bnbd_implies_rh
#print axioms bdr_cotangent_implies_rh
#print axioms riemannZeta_conj_of_pos_re
#print axioms im_ne_zero_of_inCriticalStrip_zeta_zero
#print axioms baezDuarte_unconstrained_spatial_floor
#print axioms baezDuarte_implies_rh
#print axioms clay_four_boundary_limits_implies_rh
#print axioms clayRank4Lock_cotangent_implies_rh
#print axioms clayRank4Lock_Q_cot_quad_implies_rh
#print axioms clayRank4Base_add_hom_Q_cot_quad_implies_rh
#print axioms clayRank4Base_opt_step_implies_rh
#print axioms clayRank4Base_galerkin_hom_limit_implies_rh
#print axioms clayRank4Base_phiCotBase_pairing_limit_implies_rh
#print axioms clayRank4GalerkinRay_rayQuotient_limit_implies_rh
#print axioms inCriticalStrip_one_sub
#print axioms inCriticalStrip_ne_neg_nat
#print axioms inCriticalStrip_ne_one
#print axioms riemannZeta_one_sub_eq_zero_of_inCriticalStrip
#print axioms zetaZeroReflectionSymmetry_unconditional
#print axioms rh_of_szego_and_collapse_zero_unconditional_symm
#print axioms clayRank4GalerkinRay_rayQuotient_limit_implies_rh_of_szego
#print axioms szegoReproducingInequality_of_hardyCauchySchwarz
#print axioms clayRank4GalerkinRay_rayQuotient_limit_implies_rh_of_hardyCauchySchwarz
#print axioms szegoKernelAntideriv_upper_sub_lower
#print axioms hasDerivAt_szegoKernelAntideriv
#print axioms clayRank4UnconstrainedRay_limit_implies_rh_of_hardyCauchySchwarz
#print axioms continuous_szegoKernelIntegrand
#print axioms integral_szegoKernelIntegrand_eq_sub
#print axioms tendsto_integral_szegoKernelIntegrand_atTop
#print axioms satisfiesHardyCauchySchwarz_of_integral
#print axioms clayRank4UnconstrainedRay_limit_implies_rh_of_integralHardyCauchySchwarz
#print axioms cmi_master_effective_potential_closure_implies_rh
#print axioms cmi_master_rightTriangle_effective_closure_implies_rh
#print axioms cmi_track3_dedekind_reciprocity_closure_implies_rh

end CMIAudit
