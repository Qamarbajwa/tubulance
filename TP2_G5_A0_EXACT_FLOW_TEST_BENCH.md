# TP2-G5-A0 — Exact-Flow Test-Bench Registry

This registry is a calibration library for A1. It is not evidence of a
universal theorem.

| Family | Exact status | Xi-relevant behavior | A0 classification |
|---|---|---|---|
| Periodic shear `u=(U(y,t),0,0)` | exact smooth periodic NS | `J_omega` can be nonzero while `D J_omega=J_omega`; large shear deformation need not enlarge `Q`; X2 is available in constant-vorticity subcases | adversarial decoupling |
| Beltrami/curl eigenfield `curl u=lambda u` with decay | exact smooth periodic unforced NS | vortex stretching is pressure-cancelled, `A_omega=1`; deformation may still be nontrivial; tests Xi against pressure-depletion intuition | pressure-depletion benchmark |
| ABC-type single-shell Beltrami | exact analytic Euler/NS family | 3D geometry and deformation richness, but not a universal Xi sign or size theorem | exact 3D benchmark |
| Single-shell curl eigenfields | exact analytic periodic family | includes the 2026 Huang deformation-realization construction; deformation can be prescribed, joint jets not established | realizability stress test |
| Strained sheet / Burgers-tube local models | classical exact/benchmark families | test large `A_omega`, small/large orientation factors and profile degeneracies; periodic embedding requires care | adversarial calibration |

## Required questions per family

For every analytic benchmark A1 must record whether it realizes `A_omega >> 1`,
`Theta << 1`, Xi small/large, `J_omega=0` with `omega != 0`, and nontrivial
stochastic-history variation. A failure to realize a state is not a theorem
that the state is impossible in general.

## Current safe conclusions

The periodic shear and Beltrami families already prevent a preselected
coercive answer. They do not determine whether a compensated or integrated
control exists on the full class. A1 must test all four permitted outcomes:
`COERCIVE_CONTROL_FOUND`, `COMPENSATED_OR_INTEGRATED_CONTROL_FOUND`,
`NEW_STRUCTURAL_OBJECT_FOUND`, and `NO_GO_OR_INSUFFICIENT_EVIDENCE`.
