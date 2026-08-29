# TP2-G5-A0 — Joint-Jet Realization Audit

## Primary source

Hao Huang, *Exact Lagrangian Realization and Robust Strain Sensing in
Incompressible Flow*, [arXiv:2607.26895](https://arxiv.org/abs/2607.26895),
version found 2026-08-29. The abstract and theorem text state that every
`F_* in SL(3,R)` can be realized as a one-particle endpoint deformation
gradient of a real-analytic, periodic, unforced, single-shell Euler or
Navier–Stokes flow. For Navier–Stokes the construction uses an explicitly
decaying amplitude. The paper also proves a finite material-direction sensing
classification.

## What is established

`DEFORMATION_ONLY_REALIZABILITY = DYNAMICALLY_EXACT_ON_PERIODIC_NS_CLASS`.
This is a deformation-only theorem: for a prescribed label and endpoint, the
one-point `D` (equivalently `F_*`) is exactly realized by an analytic periodic
NS solution in the stated family.

## What is not established by that theorem

The audited source is a D-only theorem and does not state a theorem jointly prescribing arbitrary
compatible values of

\[
 (D,\omega,J_\omega)
\]

at the same trajectory endpoint. Its strain-sensing results use deformation
realizability and material-direction data; they do not provide a joint jet
surjectivity result for vorticity and vorticity gradient. The G4 algebraic
counterexamples prescribe more than `D` alone and therefore remain
`KINEMATIC_COUNTEREXAMPLE`, not exact dynamical counterexamples to all NS
constraints.

## Joint-jet research question

`JOINT_JET_REALIZATION_PROBLEM`: characterize the triples `(D,omega,J_omega)`
realizable by exact periodic Navier–Stokes solutions at a prescribed
trajectory endpoint, including divergence-free, curl, pressure, periodicity,
and compatibility constraints.

**Current classification:** `OPEN` (not known from the audited source; not
claimed absent from all literature). The 2026 Huang theorem materially
strengthens the D-only side but does not close the joint problem.
