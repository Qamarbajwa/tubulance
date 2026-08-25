# TP2-G4-A2-R1: LOCAL TECHNICAL ACCEPTANCE DECISION

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2-R1 (Spectral-Degeneracy, Zero-Gradient, and Stochastic-Orientation Pre-A3 Correction)`  
**Governance Standard:** Autonomous Project Runtime Governance Kernel v2.10.0  
**Local Environment Authority:** Antigravity (Gemini Technical Authority)  
**Date:** 2026-08-25T20:57:00Z  

---

## 1. Acceptance Verdict

$$\boxed{ \text{TP2-G4-A2-R1 = CONTRACT\_ACCEPTED\_WITH\_CORRECTIONS} }$$

---

## 2. Ratified Canonical Corrections

1. **Riesz Projector Differentiability Scope**: Formally ratified that gauge-invariant cluster projectors $\mathcal{P}_\alpha$ are smooth/differentiable while the relevant spectral cluster remains isolated from its complement by a positive spectral gap.
2. **Global Definition of Unnormalized Weights $q_i$**: Formally ratified $q_i := \operatorname{tr}(P_i H) = \|v_i^T G\|^2 \ge 0$ as globally well-defined on all trajectories, with $p_i = q_i/h$ and $\eta$ defined only on the non-empty set $h = \operatorname{tr}(H) > 0$.
3. **Basis-Invariant Orientation Efficiency**: Formally ratified $\eta = \frac{\operatorname{tr}(\Gamma H)}{\lambda_{\max}(\Gamma) \operatorname{tr}(H)}$ as the canonical basis-independent representation of orientation efficiency.
4. **Backward Itô Tensor SDEs**: Formally ratified the backward Itô SDEs for $\widehat{d} H_s, \widehat{d} q_i, \widehat{d} p_i$, establishing that orientation weights are stochastic semimartingales driven by non-vanishing spatial diffusion noise.
5. **Formalized Persistence Taxonomy**: Formally ratified the definitions of occupation time $\mathcal{O}_\varepsilon(L)$, entrance time $\tau_{\text{enter}}$, exit time $\tau_{\text{exit}}$, and residence duration $\Delta \tau_{\text{res}}$ on the forwardized time parameter $\tau = T - s$.
6. **Milestone A3 Retitling**: Ratified the new title and research question for `TP2-G4-A3`:
   - **Title**: `TP2-G4-A3 — STOCHASTIC ORIENTATION-WEIGHT DYNAMICS AND LOW-ETA OCCUPATION / EXIT-TIME ANALYSIS`.

---

## 3. Evidence & Test Manifest

- `tests/test_tp2_g4_a2_r1_suite.py`: 6/6 passed.
- Scoped Regression Test Suite: **107/107 passed** across 12 test files.

---

## 4. Next Governed Increment

**`TP2-G4-A3 — STOCHASTIC ORIENTATION-WEIGHT DYNAMICS AND LOW-ETA OCCUPATION / EXIT-TIME ANALYSIS`**
