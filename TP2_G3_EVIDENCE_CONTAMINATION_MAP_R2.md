# TP2-G3: EVIDENCE CONTAMINATION MAP R2 & LINEAGE AUDIT

**Authority:** Independent E4 Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3-E4R`  
**Governance Standard:** Autonomous Project Governance v2.9.4  
**Date:** 2026-08-24T17:30:00Z  

---

## 1. Lineage of G3 Claims and Revisions

| Claim Category | Initial Worker State (Initial) | Repaired State R1 | Authoritative Final State R2 | Status |
|---|---|---|---|---|
| **Stochastic SDE & Covariance** | $dY_\tau = \Sigma_\tau dB_\tau, C_s = 2\nu \int D J_\omega J_\omega^T D^T dr$ | Unchanged | Verified exact and mathematically sound | `ACCEPTED_CANONICAL` |
| **$\chi$ Zero-Mean Treatment** | Indeterminate $0/0$ for all $|\omega(T)| = 0$ | Partitioned into 3 cases ($\chi = 0.0$ for State 2) | Ratified with regression tests T11, T17 | `ACCEPTED_CANONICAL` |
| **Couette Flow Scope** | Claimed as universal no-go theorem | Reclassified as affine sanity check outside domain | Reclassified as affine sanity check; refined algebraic no-go | `ACCEPTED_CANONICAL` |
| **In-Class $Q_s$ Positivity** | Non-negativity $Q_s \ge 0$ only | Non-negativity $Q_s \ge 0$ only | Proved $Q_s > 0$ for all $s < T$ on $\mathbb{T}^3$ via full-support diffusion theorem | `ACCEPTED_CANONICAL` |
| **$\chi$ Monotonicity** | Non-strict monotonicity $\partial_s \chi_s \ge 0$ | Non-strict monotonicity $\partial_s \chi_s \ge 0$ | Strict monotonicity $\partial_s \chi_s > 0$ for $|\omega(T)| > 0$ on $\mathbb{T}^3$ | `ACCEPTED_CANONICAL` |
| **Regularity Bridge** | Claimed as open | Recorded as open | Formally proved: qualitative $Q_s > 0$ does not yield quantitative closure; `BRIDGE = OPEN` | `ACCEPTED_CANONICAL` |

---

## 2. Stale Evidence Disposal

All prior E3/E4 review outputs generated under `TP2-G3-CANDIDATE-INITIAL` or `TP2-G3-CANDIDATE-FINAL-REPAIRED` are marked `SUPERSEDED_BY_R2`.
Only evidence generated against `TP2-G3-CANDIDATE-FINAL-REPAIRED-R2` with 56 passing acceptance tests is valid for canonical scientific promotion.
