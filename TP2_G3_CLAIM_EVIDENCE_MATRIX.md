# TP2-G3: CLAIM–EVIDENCE MATRIX & MATHEMATICAL VERIFICATION

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Verification Matrix  

---

## 1. Claim-by-Claim Verification Table

| Claim | Mathematical Statement | Verification Method | Automated Test ID | Classification |
|---|---|---|---|---|
| **Claim 1: Mean Conservation** | $m = \mathbb{E} Z_s = \omega(x,T) \implies \partial_s m = 0$ | Martingale property of forwardized SDE $dY_\tau = \Sigma_\tau dB_\tau$ | `test_t1_forwardized_martingale_orientation` | `EXACT_IDENTITY` |
| **Claim 2: Noise Matrix** | $[\Sigma_\tau]_{ik} = \sqrt{2\nu} [D_{T-\tau}]_{ij} \frac{\partial \omega_j}{\partial x_k}(A, T-\tau)$ | Itô differentiation under Convention M | `test_t1`, `test_t9` | `EXACT_IDENTITY` |
| **Claim 3: Covariance Formula** | $C_s = 2\nu \int_s^T \mathbb{E}[ D_r (J_\omega J_\omega^T) D_r^T ] dr$ | Itô product rule on $M_\tau M_\tau^T$ | `test_t2_symbolic_ito_product_rule_covariance`, `test_t3_covariance_psd` | `EXACT_IDENTITY` |
| **Claim 4: Variance Budget** | $V_s = 2\nu \int_s^T \mathbb{E}[ \| D_r J_\omega \|_F^2 ] dr$ | Trace of matrix quadratic variation | `test_t4_trace_variance_identity` | `EXACT_IDENTITY` |
| **Claim 5: $\chi$ Monotonicity** | $\frac{\partial}{\partial s} \chi_s \ge 0$ | Calculus on $\chi_s = \frac{|\omega|^2}{|\omega|^2 + V_s}$ | `test_t5_chi_algebra_and_derivative_sign` | `EXACT_IDENTITY` |
| **Claim 6: Universal Decoherence Falsification** | $\nu > 0 \not\implies \chi < 1$ (fails if $J_\omega = 0$) | Exact Couette shear flow solution | `test_t7_constant_vorticity_zero_covariance` | `FALSIFIED_UNIVERSAL_CLAIM` |
| **Claim 7: Scaling Consistency** | $[C] = 4, [V] = 4, [\Sigma] = 3, [\chi] = 0$ | Parabolic Navier–Stokes scaling derivation | `test_t6_scaling_exponents_complete` | `EXACT_SCALE_INVARIANT_QUANTITY` |
| **Claim 8: Operator Ordering Sensitivity** | $\Sigma \neq \sqrt{2\nu} J_\omega D$ | Matrix multiplication non-commutation | `test_t9_matrix_order_mutation_discrimination` | `EXACT_IDENTITY` |

---

## 2. Non-Circularity Declaration

All identities derived in TP2-G3 are valid for any classical Navier–Stokes solution on its existence interval $[0, T^*)$.
No assumption of BKM boundedness, Serrin integrability, or global continuation was made in deriving these formulas.
