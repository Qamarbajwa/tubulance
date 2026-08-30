# TP2-G5-A3 — Amplitude–Direction Decomposition

## Scope

This artifact records the Convention-M algebra for a smooth vorticity field on the nonzero-vorticity domain

`q = |omega| > 0`, `xi = omega/q`, and `[J_f]_{ij} = partial_j f_i`.

It is a pointwise identity package. It does not assert a global continuation criterion, a BKM bound, or a regularity theorem.

## Exact identities

Since `omega = q xi`, differentiation gives

`J_omega = xi (grad q)^T + q J_xi`.

The unit-vector constraint gives `xi dot partial_j xi = 0` for each spatial index `j`. Consequently the cross term vanishes and

`||J_omega||_F^2 = |grad q|^2 + q^2 ||J_xi||_F^2`.

Therefore, on `q > 0`,

`kappa_omega^2 = ||J_omega||_F^2/q^2 = |grad log q|^2 + ||J_xi||_F^2`.

The first summand is amplitude variation and the second is directional variation. The decomposition is exact and local.

## Domain and state guards

At `omega = 0`, `xi`, `J_xi`, and `kappa_omega` are not defined by this factorization. Any use of the identities must retain the nonzero-vorticity domain or an explicitly regularized extension. A zero-gradient state is not the same as a zero-vorticity state.

## Evidence classification

- Result: `PROVED_IDENTITY` by direct differentiation and the unit-vector constraint.
- Evidence: reproducible numerical checks plus a fresh-context algebra audit.
- Limit: project-level derivation, not external formal verification.
- Forbidden promotion: no implication from this decomposition to bounded `Xi`, `E_mu[Xi]`, or Clay Statement B.
