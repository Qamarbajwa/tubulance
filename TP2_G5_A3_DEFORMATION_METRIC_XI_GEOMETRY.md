# TP2-G5-A3 — Deformation-Metric Geometry of Xi

## Definitions

Let `D` be an invertible deformation matrix, `G = J_omega`, `q = |omega|`, and `xi = omega/q` on `q > 0`. Set

`Xi = ||D G||_F^2 / |D omega|^2`.

Using `omega = q xi`, `D omega = q D xi`, and the amplitude–direction identity,

`Xi = sum_j |D(partial_j xi) + (partial_j log q) D xi|^2 / |D xi|^2`.

Define

`n_D = D xi/|D xi|`, `b_j = D(partial_j xi)/|D xi|`, and `a_j = partial_j log q`.

Then `Xi = sum_j |b_j + a_j n_D|^2`. With `P_perp = I - n_D n_D^T`, define

`beta_j = n_D dot b_j = (D xi dot D partial_j xi)/|D xi|^2`,

`M_D = sum_j (a_j + beta_j)^2`, and

`C_D = sum_j |P_perp b_j|^2`.

The exact split is

`Xi = M_D + C_D`, with `M_D >= 0` and `C_D >= 0`.

## The beta guard

`beta_j` is a deformation-metric direction coupling. It is not an ordinary spatial derivative. The equality `beta_j = partial_j log|D xi|` is not valid without differentiating the deformation field and accounting for its spatial dependence. For `D = I`, the unit-vector constraint gives `beta_j = xi dot partial_j xi = 0`. For a general non-orthogonal `D`, beta need not vanish.

## Gamma formulation

With `Gamma = D^T D`,

`Xi = tr(Gamma G G^T)/(q^2 xi^T Gamma xi)`.

This makes the metric weighting explicit. It does not turn `Xi` into an Eulerian scalar independent of the deformation history.

## Evidence classification

The split and Gamma form are exact pointwise identities on the declared domain. They are not a coercive estimate and do not control the evolution of `D`, `xi`, or `Xi`.
