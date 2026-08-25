# TP2-G4-A2-R1: INDEPENDENT E4 MATHEMATICAL VERIFICATION REPORT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2-R1`  
**Role:** Independent Verification Authority (Governance v2.10.0)  
**Date:** 2026-08-25T20:56:30Z  
**Verdict:** `E4_PASS — SPECTRAL_DEGENERACY_AND_STOCHASTIC_ORIENTATION_CORRECTIONS_RATIFIED`  

---

## 1. Executive Summary

The independent verification authority audited the mathematical corrections in `TP2-G4-A2-R1` prior to advancing to `TP2-G4-A3`. All three primary issues raised in the adversarial pre-flight audit have been rigorously resolved:

1. **Kato/Riesz Resolvent Gap Scope**: Projector differentiability is now properly restricted to isolated spectral clusters with positive spectral gap to their complement.
2. **Zero-Gradient Handling**: The unnormalized orientation weights $q_i := \operatorname{tr}(P_i H) = \|v_i^T G\|^2 \ge 0$ are ratified as globally well-defined observables on all sample paths, with $p_i = q_i/h$ and $\eta$ defined only on $h = \operatorname{tr}(H) > 0$.
3. **Stochastic Semimartingale SDEs**: The backward Itô SDEs for $\widehat{d} H_s, \widehat{d} q_i, \widehat{d} p_i$ and the forwardized persistence definitions on $\tau = T - s$ are verified and ratified.

---

## 2. Itemized Verification Results

| Item / Equation | Verifier Check | Mathematical Status |
|---|---|---|
| **Spectral Cluster Projector $\mathcal{P}_\alpha$** | Verified Riesz contour integral $\mathcal{P}_\alpha = \frac{1}{2\pi i} \oint_{\mathcal{C}_\alpha} (z I - \Gamma)^{-1} dz$ under positive spectral gap. | `RATIFIED_EXACT` |
| **Unnormalized Weights $q_i \ge 0, \sum q_i = h$** | Verified $q_i = \operatorname{tr}(P_i H)$ is globally well-defined even when $G = 0 \implies q_i = 0$. | `RATIFIED_EXACT` |
| **Basis-Invariant $\eta = \frac{\operatorname{tr}(\Gamma H)}{\lambda_{\max}(\Gamma) \operatorname{tr}(H)}$** | Matches $\sum p_i (\sigma_i/\sigma_1)^2$ on simple spectrum; gauge-invariant on double degeneracy. | `RATIFIED_EXACT` |
| **Backward Itô SDE for $\widehat{d} H_s$** | Verified $\widehat{d} H_s = R_H ds + \sqrt{2\nu} \sum_\ell \partial_\ell H \widehat{d}W^\ell$ with $R_H = K G^T + G K^T - 2\nu B_G$. | `RATIFIED_EXACT` |
| **Weight SDE $\widehat{d} q_i$ Decomposition** | Verified 3-component structure: deformation rotation + vorticity dynamics + martingale noise. | `RATIFIED_EXACT` |
| **Forwardized Persistence Definitions** | Verified formal definitions of $\mathcal{O}_\varepsilon(L)$, $\tau_{\text{enter}}$, $\tau_{\text{exit}}$, $\Delta \tau_{\text{res}}$. | `RATIFIED_EXACT` |

---

## 3. Test Verification Truth

- `tests/test_tp2_g4_a2_r1_suite.py`: 6/6 passed.
- `tests/test_tp2_g4_a2_suite.py` + `tests/test_tp2_g4_a2_verifier_suite.py`: 26/26 passed.
- Combined regression suite: **107/107 passed** across 12 test files.

---

## 4. Final Verifier Verdict

$$\boxed{ \text{TP2-G4-A2-R1 = FINAL\_E4\_PASS\_WITH\_CORRECTIONS\_RATIFIED} }$$
