# TP2-G3: CORRECTION REQUEST R2 & AUDIT SPECIFICATION

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3-E4R`  
**Governance Standard:** Autonomous Project Governance v2.9.4 (Tier T4)  
**Issuing Authority:** Independent E4 Verification Authority  
**Date:** 2026-08-24T17:30:00Z  

---

## 1. Description of Identified Gaps in R1 State

1. **Strict Positivity of $Q_s$ on $\mathbb{T}^3$**:
   - The R1 state established non-negativity $Q_s \ge 0$ and the affine Couette no-go, but did not analyze whether in-class solutions on $\mathbb{T}^3$ with $|\omega(T)| > 0$ strictly force $Q_s > 0$.
   - **Audit Action**: Completed rigorous proof that full topological support of backward diffusion forces $Q_s > 0$ for all $s < T$ whenever $|\omega(T)| > 0$.
2. **Strict Lookback Monotonicity of $\chi_s$**:
   - Monotonicity $\partial_s \chi_s \ge 0$ is refined to strict monotonicity $\partial_s \chi_s > 0$ for non-trivial smooth solutions on $\mathbb{T}^3$.
3. **Disambiguation of Algebraic Integrand vs Expected QV**:
   - Formally disambiguated `VISCOSITY_ALONE_DOES_NOT_ALGEBRAICALLY_FORCE_POINTWISE_STRICT_PRODUCTION` from `SMOOTH_IN_CLASS_NONTRIVIAL_TERMINAL_VORTICITY_IMPLIES_STRICT_EXPECTED_QV_PRODUCTION`.
4. **Test Inventory Distinction**:
   - Clarified that the G3 Acceptance Suite comprises 56 tests across 6 files, whereas the total repository contains 884 tests across 111 files.

---

## 2. Mandatory Repairs Required

- Formalize `TP2_G3_STRICT_Q_POSITIVITY_AUDIT.md`.
- Expand verifier-owned test suite to 28 tests (T1–T28) covering diffusion support, continuity, periodic curl zero-integral, and uniqueness forward implications.
- Assign new candidate identifier: `TP2-G3-CANDIDATE-FINAL-REPAIRED-R2`.
