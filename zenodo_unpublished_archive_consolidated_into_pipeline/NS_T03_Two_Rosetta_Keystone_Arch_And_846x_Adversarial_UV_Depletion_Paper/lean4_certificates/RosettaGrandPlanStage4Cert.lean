/-
RosettaGrandPlanStage4Cert.lean

Machine-verified Lean 4 certificate for Grand Plan Stage 4:
Two-sided Win-Win Arch Enclosure Theorem.
If an observable Phi satisfies both:
  1. Aligned-tube depletion bound:     Phi <= C1 * delta        (vanishes as delta -> 0)
  2. Scrambled-tangle depletion bound: Phi <= C2 * (2 - 3*delta) (vanishes as delta -> 2/3)
for C1, C2 >= 0, then (C1 + 3 * C2) * Phi <= 2 * C1 * C2 unconditionally!

NS_GLOBAL_REGULARITY_OPEN = TRUE:
This certifies the algebraic Win-Win arch enclosure; proving the uniform
PDE constants C1, C2 independent of L -> infinity remains OPEN.
-/

namespace RosettaGrandPlanStage4

def ns_global_regularity_open_lock : Bool := true

/-- Unconditional two-sided Win-Win Arch Enclosure Theorem:
    Eliminates `delta` between `Phi <= C1 * delta` and `Phi <= C2 * (2 - 3*delta)`
    with weights `3 * C2` and `C1` to yield `(C1 + 3 * C2) * Phi <= 2 * C1 * C2`. -/
theorem grand_plan_two_sided_arch_enclosure_unconditional
    (Phi delta C1 C2 : Int)
    (hC1 : 0 ≤ C1)
    (hC2 : 0 ≤ C2)
    (h_aligned : Phi ≤ C1 * delta)
    (h_scrambled : Phi ≤ C2 * (2 - 3 * delta)) :
    (C1 + 3 * C2) * Phi ≤ 2 * C1 * C2 := by
  have h1 : (3 * C2) * Phi ≤ (3 * C2) * (C1 * delta) :=
    Int.mul_le_mul_of_nonneg_left h_aligned (by omega)
  have h2 : C1 * Phi ≤ C1 * (C2 * (2 - 3 * delta)) :=
    Int.mul_le_mul_of_nonneg_left h_scrambled hC1
  have h_sum : C1 * Phi + (3 * C2) * Phi ≤
      C1 * (C2 * (2 - 3 * delta)) + (3 * C2) * (C1 * delta) :=
    Int.add_le_add h2 h1
  have h_lhs : (C1 + 3 * C2) * Phi = C1 * Phi + (3 * C2) * Phi :=
    Int.add_mul C1 (3 * C2) Phi
  have h_rhs : C1 * (C2 * (2 - 3 * delta)) + (3 * C2) * (C1 * delta) = 2 * C1 * C2 := by
    rw [Int.mul_sub, Int.mul_sub]
    have ha : C1 * (C2 * 2) = 2 * C1 * C2 := by
      rw [Int.mul_comm C2 2, ← Int.mul_assoc, Int.mul_comm C1 2]
    have hb : C1 * (C2 * (3 * delta)) = (3 * C2) * (C1 * delta) := by
      simp only [Int.mul_assoc, Int.mul_comm, Int.mul_left_comm]
    omega
  omega

#print axioms grand_plan_two_sided_arch_enclosure_unconditional

end RosettaGrandPlanStage4
