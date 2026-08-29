# TP2-G5-A0 — Landscape, Literature Boundary, Object Identity, and Research Contract Input

**Base:** `TP2-G4-A5-R1`, local `HEAD=6fd830ce23b6046a0a65ad0f3432c73fdb295559`  
**Date:** 2026-08-29  
**Writer:** `codex-primary-writer`  
**Reviewer:** `codex-independent-reviewer-fallback` (same-model fresh checklist; degraded independence)  
**Acceptance authority:** environment-local project authority under Governance Kernel v2.10.1.

## Executive conclusion

`Xi` remains a viable primary G5 object, but only as a scale-critical rate
density on its valid state space. The audited literature establishes all of
its main ingredients separately: stochastic Cauchy transport, vorticity
gradient dynamics, inverse-vorticity length scales, deformation history,
directional regularity, sparseness/analyticity, pressure coupling, and recent
Weber covariance results. No audited source was found stating the exact ratio
or the exact `Q/S=2nu E_mu[Xi]` decomposition. This supports only the internal
verdicts recorded in `TP2_G5_A0_NOVELTY_AUDIT.md`, not an absolute novelty claim.

The principal A0 result is a boundary map: `Xi` is not equivalent to
`kappa_omega^2`, `Theta`, an Eulerian inverse length, a direction theorem, or a
deformation-only realizability statement. The non-circular a-priori control of
`E_mu[Xi]` remains open. G5-A1 is authorized only under the contract in
`TP2_G5_A0_RESEARCH_CONTRACT.md`.

## Question and allowed outcomes

The primary question is whether intrinsic 3D NS dynamics provide genuinely
a-priori, non-circular, scale-critical information on `E_mu[Xi]` for histories
with nonzero vorticity. A1 must keep all four outcomes live:

1. `COERCIVE_CONTROL_FOUND`
2. `COMPENSATED_OR_INTEGRATED_CONTROL_FOUND`
3. `NEW_STRUCTURAL_OBJECT_FOUND`
4. `NO_GO_OR_INSUFFICIENT_EVIDENCE`

No lower-bound target such as `Xi >= c` or `E_mu[Xi] >= c` is preselected.

## Identity, domain, and scaling

The exact definitions and state taxonomy are frozen in
`TP2_G5_A0_XI_IDENTITY_AND_DOMAIN.md`. The key safeguards are:

* X1: factorization valid;
* X2: Xi is exactly zero although Theta is undefined;
* X3: Xi is not silently defined at `omega=0`; those histories have zero
  `mu_s` weight;
* X4: `S_s=0` makes `mu_s` undefined and is handled through G3's chi taxonomy.

The formal parabolic dimensions are `omega:lambda^2`, `J_omega:lambda^3`,
`D:lambda^0`, `Xi:lambda^2`, and `Q/S:lambda^2`. The fixed unit torus is not
claimed to be invariant under the dilation; this is a local/formal scaling
statement plus the separately proved fixed-torus shear obstruction.

## Research-memory synthesis

The local memory identifies G3 covariance positivity, G4's SVD orientation
decomposition, the shear decoupling family, Beltrami pressure depletion,
nonlocal pressure coupling, and critical geometric pathways as the relevant
foundations. Shared obstructions are `NS-OBS-004`, `005`, `006`, `007`, `009`,
and `010`. The resurrection queue points to TH9-R, LA1-R, and BRIDGE1-R, but no
resurrection is promoted automatically by A0.

## Literature boundary

Constantin–Iyer (2008) proves the stochastic Lagrangian representation for
classical solutions; Eyink–Gupta–Zaki develops stochastic Cauchy invariants,
variance and cancellation in wall-bounded settings; Gibbon develops
Eulerian/time-averaged inverse length scales; Constantin–Fefferman and
Beirão da Veiga–Berselli give conditional vorticity-direction criteria;
Grujić gives conditional sparseness/analyticity criteria; Miller gives
critical strain-eigenvalue criteria; Lei–Ren–Tian (2025) gives a preprint
double-cone characterization; and Grujić (2026) is a preprint logarithmic
depletion proposal. None is an exact Xi theorem.

The 2026 Mahithitarmmatorn paper is the closest current stochastic analogue:
it derives closed mean/covariance equations for a Weber field, emphasizes
covariance obstructions, and explicitly makes no global regularity claim. It
does not identify the vorticity-gradient relative density Xi.

## Realizability boundary

Huang (2026) establishes exact periodic unforced NS realization of any
one-particle deformation gradient in `SL(3,R)` within a real-analytic
single-shell family. It does not establish arbitrary joint realization of
`(D,omega,J_omega)`. Therefore G4's algebraic configurations retain the label
`KINEMATIC_COUNTEREXAMPLE`. The joint-jet problem is open and is a possible
future structural object, not an A0 theorem.

## Landscape map

| Route | A0 status | Relation to Xi |
|---|---|---|
| stochastic Cauchy/Kelvin | known foundation | supplies `D omega` history, not gradient ratio |
| covariance production/cancellation | known foundation + project identity | motivates weighted denominator, no universal closure |
| Eulerian inverse length | known analogue | `kappa^2` only; missing relative deformation |
| direction/eigenframe criteria | conditional known results | cannot transfer to Xi without bridge |
| sparseness/analyticity/flux | conditional geometric bridges | possible future bridge, not established |
| pressure Hessian/commutator | structural coupling | candidate non-circular bridge, unproved |
| D-only realizability | exact 2026 theorem | insufficient for joint Xi state realization |
| joint jet realization | open | new candidate question |

## Decision

`XI_CONFIRMED_AS_PRIMARY_G5_OBJECT`, with a mandatory literature-collision
watch and the zero-state/stopping contract. Stop after A0.
