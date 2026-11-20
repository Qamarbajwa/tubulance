# TP2-G1R: EVIDENCE CONTAMINATION MAP & DOWNSTREAM AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1R`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Permanent Contamination Audit Record  

---

## 1. Classification of Discrepancy

Under Governance v2.9, any challenged finding must be audited for two distinct modes of contamination:
1. `SEMANTIC / OPERATOR CONTAMINATION`: Errors in tensor orientation, matrix transpose, or component mapping that invalidate mathematical equations.
2. `SCALING CONTAMINATION`: Errors in scaling exponents or dimensional invariants that invalidate critical classifications.

---

## 2. Artifact-by-Artifact Contamination Audit

| Artifact Under Review | Discrepancy Status | Semantic Contamination? | Scaling Contamination? | Forensic Assessment & Remediation |
|---|---|---|---|---|
| `TP2_G1_STOCHASTIC_CONVENTION_CONTRACT.md` | **CLEAN (Validated under Convention M)** | **NO** | **NO** | Uses Convention M ($[J]_{ij} = \partial_j f_i$) consistently. Augmented with explicit convention definition in `TP2_G1R_GRADIENT_CONVENTION_CONTRACT.md`. |
| `TP2_G1_FORWARD_BACKWARD_EQUIVALENCE.md` | **CLEAN (Validated under Convention M)** | **NO** | **NO** | Component derivation rigorously confirmed; cofactor identity $\nabla \times (B^T (v \circ A)) = B^{-1} (\nabla \times v)(A)$ proved exact. |
| `TP2_G2_SCALING_AUDIT.md` | **CLEAN (Invariant under Transpose)** | **NO** | **NO** | Deformation matrix scaling exponent $[F] = [D] = \lambda^0$ is identical for $F$, $F^T$, $F^{-1}$, $F^{-T}$. All 12 scaling exponents remain strictly valid. |
| `TP2_G2_CHI_INVARIANCE_TESTS.md` | **CLEAN** | **NO** | **NO** | Adversarial cases A–F and $[0, 1]$ bounds depend on Hilbert space probability norms and are completely unaffected by matrix convention. |
| `TP2_G1_G2_FINAL_REVIEW_PACKET.md` | **CLEAN** | **NO** | **NO** | Core conclusions remain 100% mathematically valid; reconciled with JFM literature. |
| `tests/test_tp2_g1_g2_suite.py` | **CLEAN** | **NO** | **NO** | All 5 tests verified under Convention M. Augmented with 5 new adversarial regression tests in `tests/test_tp2_g1r_adversarial_suite.py`. |
| `TP2-G3 (Proposed Task Scope)` | **CLEAN** | **NO** | **NO** | Will inherit the frozen componentwise definition: $Z_i = D_{ij} \omega_j(A,s) = [B_M^{-1}]_{ij} \omega_j(A,s)$. |

---

## 3. Contamination Verdict

$$\boxed{\textbf{ZERO CONTAMINATION (MATHEMATICAL CONTENT FULLY PRESERVED)}}$$

The apparent discrepancy between the project's Jacobian convention (Convention M) and the fluid-mechanics convention (Convention F) is a notation translation with zero mathematical error in the underlying tensor equations. No historical artifact requires deletion or invalidation.
