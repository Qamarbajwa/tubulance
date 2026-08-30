# TP2-G5-A3 — Understanding Gate

## Level 1: mechanism

`omega = q xi` separates amplitude variation from direction variation. A deformation matrix changes both through a metric-weighted projection.

## Level 2: architecture

`Xi` splits into a deformation-parallel term `M_D` and a deformation-transverse term `C_D`. The beta coupling is the longitudinal deformation correction. `Gamma = D^T D` exposes the metric, while condition number bounds compare `Xi` to `kappa_omega^2` only conditionally.

## Level 3: rigorous Q&A

- What is proved? The pointwise identities on `q > 0` and invertible `D`.
- What is not proved? A uniform condition-number bound, an evolution closure, an Eulerian expectation identity, or a regularity result.
- What fails at zero states? `xi`, `J_xi`, and the quotient definition require explicit domain guards.
- What remains open? A non-circular bridge from the A3 geometry to the accepted stochastic dynamics.

Verdict: `U3_COMPLETE_PACKAGE` for the bounded A3 derivation, with open research questions preserved.
