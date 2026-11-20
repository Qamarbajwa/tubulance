# TP2-G3: CORRECTION REQUEST & REPAIR SPECIFICATION

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance Standard:** Autonomous Project Governance v2.9.4 (Tier T4)  
**Issuing Authority:** Independent E4 Verification Authority  
**Date:** 2026-08-24T17:05:00Z  

---

## 1. Defect 1: Three-Case Canonical Partition for $\chi$

- **Defect Description**: Candidate summary stated that $|\omega(x, T)| = 0$ is always `CHI_UNDEFINED_DEGENERATE_ZERO_STATE`.
- **Contradiction**: If $\mathbb{E} Z_s = 0$ and $V_s > 0$, the denominator $\mathbb{E}|Z_s|^2 = V_s > 0$, so $\chi_s = 0 / V_s = 0.0$ (perfect cancellation).
- **Contaminated Artifacts**: `TP2_G3_CHI_EVOLUTION.md`, `TP2_G3_FINAL_REVIEW_PACKET.md`, `TP2_G3_NEGATIVE_EVIDENCE.md`.
- **Required Repair**: Formulate and ratify the 3-state taxonomy:
  - State 1: $|\mathbb{E} Z| > 0 \implies \chi \in (0, 1]$
  - State 2: $\mathbb{E} Z = 0, V > 0 \implies \chi = 0.0$ (`CHI_ZERO_NONDEGENERATE_PERFECT_CANCELLATION`)
  - State 3: $\mathbb{E}|Z|^2 = 0 \implies 0/0$ (`CHI_UNDEFINED_DEGENERATE_ZERO_STATE`)
- **Required Regression Test**: `test_t11_state_2_zero_mean_perfect_cancellation` and `test_t17_reject_wrong_chi_degeneracy_convention`.

---

## 2. Defect 2: Couette Counterexample Domain Scope

- **Defect Description**: Worker candidate claimed plane Couette flow as a universal no-go theorem within the declared energy domain.
- **Contradiction**: Couette flow is affine unbounded $\notin L^2(\mathbb{R}^3)$ and non-periodic on $\mathbb{T}^3$.
- **Contaminated Artifacts**: `TP2_G3_COUNTEREXAMPLE_LEDGER.md`.
- **Required Repair**: Reclassify Couette flow as `EXACT_AFFINE_SANITY_COUNTEREXAMPLE_OUTSIDE_DECLARED_PERIODIC_DECAY_CLASS` and reformulate the no-go finding as:
  `VISCOSITY_ALONE_DOES_NOT_ALGEBRAICALLY_FORCE_STRICT_COVARIANCE_PRODUCTION`.
- **Required Regression Test**: `test_t15_couette_scope_metadata`.

---

## 3. Defect 3: Information Content of $\chi$

- **Required Repair**: Explicitly record that $\chi_s$ is a `NORMALIZED_VARIANCE_REPARAMETERIZATION` with zero independent dynamical degrees of freedom beyond $(|\omega(x, T)|^2, V_s)$.
