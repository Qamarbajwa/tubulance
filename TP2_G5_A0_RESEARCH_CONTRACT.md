# TP2-G5-A0 — Research Contract for G5-A1

**Decision:** `XI_CONFIRMED_AS_PRIMARY_G5_OBJECT`  
**Authorization:** only the contract below; A1 is not executed in A0.

## Frozen A1 question

Derive the exact stochastic dynamics, on the valid state space, of

\[
 N_s=\|D_sJ_\omega(A_s,s)\|_F^2,\qquad
 R_s=|D_s\omega(A_s,s)|^2,qquad
 \Xi_s=N_s/R_s.
\]

The first scientific objective is an exact, convention-consistent dynamics
and a domain-safe representation. It is not a request to prove positivity,
coercivity, or regularity.

## Permitted conclusions

A1 must classify its result as exactly one or more of:

* `COERCIVE_CONTROL_FOUND` — only with a proved non-circular, scale-compatible
  estimate and complete hypotheses;
* `COMPENSATED_OR_INTEGRATED_CONTROL_FOUND` — for a history, spacetime, or
  weighted control that is not a pointwise lower bound;
* `NEW_STRUCTURAL_OBJECT_FOUND` — if the exact dynamics expose an object more
  fundamental than Xi;
* `NO_GO_OR_INSUFFICIENT_EVIDENCE` — if no valid closure follows.

## Hard exclusions

Do not:

* derive A1 from `Xi >= c` unless separately motivated and proved;
* call stochastic Cauchy transport novel;
* transfer a vorticity-direction theorem into Xi without a deformation proof;
* equate Xi with an Eulerian inverse length without proving the deformation and
  `mu_s` bridge;
* use the Huang D-only realization as joint `(D,omega,J_omega)` realization;
* use `log Xi` on X2/X3 or before checking `R>0`;
* insert BKM, Serrin, critical-strain, or equivalent control as an a-priori
  hypothesis and call the result unconditional;
* promote internal N2 absence to N3/N4.

## State and stopping requirements

Before quotient operations A1 must define stopping/restriction for

\[
 \tau_\omega=\inf\{|\omega|=0\},\quad
 \tau_N=\inf\{N=0\},\quad
 \tau_R=\inf\{R=0\},
\]

and for loss of isolated spectral/projector clusters. Since D is invertible,
`R=0 iff omega=0`. X2 is allowed and has Xi exactly zero; `log Xi` is not.
For X3, use the zero `mu_s` weight and introduce an extension only if it is
explicitly measurable and proved irrelevant. For X4, do not define `mu_s`.

## Required A1 benchmark set

At minimum: periodic shear, Beltrami/single-shell curl eigenfields, ABC-type
families, strained-sheet and Burgers-tube benchmarks, and any joint-jet
construction found. Each benchmark must record `omega`, `J_omega`, `D`, `N`,
`R`, Xi, degeneracies, and stochastic-history variation.

## Acceptance bar

An A1 candidate requires: exact derivation; domain audit; scaling audit;
comparison against this literature boundary and local memory; worker tests;
independent verifier tests; and a reviewer statement that actively checks
literature collision, denominator errors, circularity, Euler/NS transfer, and
joint-realizability overclaim. No A1 artifact may change Clay Statement B from
`UNRESOLVED`.
