# TP2-G3: INDEPENDENT MATHEMATICAL VERIFICATION REPORT

**Authority:** Independent E4 Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3 (Exact Stochastic Cauchy Covariance / Variance Evolution)`  
**Governance Standard:** Mid-Project Autonomous Governance v2.9 (Tier T4)  
**Candidate Base SHA:** `2e9a4fb5dd6ddc5ec377328f9387c16acab1fe5f`  
**Status:** Authoritative Independent Verification  

---

## 1. Governance Pre-Flight & Independence Disclosure

- **Base Commit SHA**: `2e9a4fb5dd6ddc5ec377328f9387c16acab1fe5f`.
- **Candidate Artifacts Audited**:
  - `TP2_G3_BACKWARD_ITO_DERIVATION.md` (`8f5914386955e2fece715ab4af2760d74c2bd7e92b9cef20e307b8d52a947ae5`)
  - `TP2_G3_FORWARDIZED_MARTINGALE_CONTRACT.md` (`e55bfbb48fe2b9555e38ed4b7004e32fafb26eaa0fde6f7e9a6794c6c384c0c0`)
  - `TP2_G3_COVARIANCE_TENSOR_IDENTITY.md` (`c1d2504fe437c7569bc37383b90f1e201481a7b34583a008d84a5c407336b8bb`)
  - `TP2_G3_VARIANCE_BUDGET.md` (`06d41758a0282f29ecf67e6e7b8a2e595f6ac7c49780c7209aa9180b5cdcd7dc`)
  - `TP2_G3_CHI_EVOLUTION.md` (`73985f56b2d63a84f9ad744346d221a92a288cce985d65b24aa87f90836f4e17`)
  - `TP2_G3_SCALING_AUDIT.md` (`2098362f4472bb9ada49bdc177cc5757f84b122ec3b5507d486c995adbe3a564`)
  - `TP2_G3_COUNTEREXAMPLE_LEDGER.md` (`543b976129664f5b4e836a7f0891fec372b804092237568447b3c614b98a53c4`)
  - `TP2_G3_LITERATURE_NOVELTY_AUDIT.md` (`508b644a8ca0e0ff796efcd594116d157890ed82c049a04a9f3bab0350a7efbd`)
  - `TP2_G3_CLAIM_EVIDENCE_MATRIX.md` (`c30c56476939abb66fbe450b3fb34b5b143fcad305362b0ad30a7e6f05511add`)
  - `TP2_G3_NEGATIVE_EVIDENCE.md` (`113ffac24cbf8fe3aea4f2312bb7d94ce1684c625e25504a5fe71a81b39bf1c4`)
  - `TP2_G3_FINAL_REVIEW_PACKET.md` (`2b8921a5ab5e8b71bef870b5676c29794477a3e09c80d43e47ae891318f6268d`)
  - `tests/test_tp2_g3_suite.py` (`90c83244e4cc7c1d55de846fe7fae58c58efb8d3e6bc48a41d36058241faa78e`)
- **Independence Disclosure**:
  $$\boxed{\textbf{E4\_INDEPENDENCE\_LIMITATION}}$$
  *(Verification is executed with strict adversarial role separation in the governed environment; all mathematical claims have been reconstructed from first principles).*

---

## 2. Independent Mathematical Reconstruction & Verification

### 2.1 Primary Source Oracle & Forward-Time Martingale
- The stochastic Cauchy contribution $Z_s = D_T^s(x) \omega(A_T^s(x), s)$ on $s \in [0, T]$ is a backward local martingale (and true martingale for smooth fields).
- Forwardizing time $\tau = T - s \in [0, T]$, $Y_\tau = Z_{T-\tau}$, and $B_\tau = W_T - W_{T-\tau}$ establishes the standard forward Itô SDE:
  $$d Y_\tau = \Sigma_\tau \, dB_\tau, \quad Y_0 = \omega(x, T),$$
  where in project **Convention M** ($[J]_{ij} = \partial_j f_i$):
  $$\boxed{ \Sigma_\tau = \sqrt{2\nu} \, D_{T-\tau} \, J_\omega(A_{T-\tau}, T-\tau) }$$
- Componentwise oracle: $[\Sigma]_{ik} = \sqrt{2\nu} D_{ij} \partial_k \omega_j$. Alternative operator orderings ($J_\omega D$, $D^T J_\omega$, $D J_\omega^T$) are rigorously rejected by non-commutation.

### 2.2 Covariance and Variance Identities Verified
- Mean conservation: $m = \mathbb{E}[Z_s] = \omega(x, T)$ for all $s \in [0, T] \implies \partial_s m = 0$.
- Covariance tensor:
  $$\boxed{ C_s = \operatorname{Cov}(Z_s) = 2\nu \int_s^T \mathbb{E}\left[ D_r (J_\omega J_\omega^T)(A_r, r) D_r^T \right] dr \succeq 0 }$$
  $$\boxed{ \frac{\partial}{\partial s} C_s = - \mathbb{E}[ \Sigma_s \Sigma_s^T ] \preceq 0, \quad C_T = 0 }$$
- Trace variance budget:
  $$\boxed{ V_s = \operatorname{tr}(C_s) = 2\nu \int_s^T \mathbb{E}\left[ \| D_r J_\omega(A_r, r) \|_F^2 \right] dr }$$
  $$\boxed{ \frac{\partial}{\partial s} V_s = - 2\nu \, \mathbb{E}\left[ \| D_s J_\omega(A_s, s) \|_F^2 \right] \le 0 }$$
- Second-moment decomposition: $\mathbb{E}|Z_s|^2 = |\omega(x, T)|^2 + V_s$.

---

## 3. Discovered Corrections & Necessary Revisions

1. **Mandatory $\chi$ Zero-Mean Correction**:
   The worker report erroneously stated that whenever $|\omega(x, T)| = 0$, $\chi_s$ is `CHI_UNDEFINED_DEGENERATE_ZERO_STATE`.
   **Correction**: When $\mathbb{E} Z_s = 0$ but $\mathbb{E}|Z_s|^2 > 0$ ($V_s > 0$), $\chi_s = \frac{0}{V_s} = \mathbf{0.0}$. This is the **non-degenerate perfect-cancellation state**. Only when $\mathbb{E}|Z_s|^2 = 0$ ($0/0$) is the state undefined.
2. **Couette Counterexample Domain Scope**:
   Plane Couette flow is an exact affine Navier–Stokes solution with $J_\omega \equiv 0$, but is unbounded on $\mathbb{R}^3$ and non-periodic on $\mathbb{T}^3$.
   **Correction**: The counterexample is classified as `EXACT_SMOOTH_AFFINE_NS_SANITY_COUNTEREXAMPLE_OUTSIDE_DECLARED_ENERGY_DOMAIN`. The resulting no-go theorem is formulated rigorously as:
   $$\boxed{\textbf{VISCOSITY\_ALONE\_DOES\_NOT\_ALGEBRAICALLY\_FORCE\_POSITIVE\_QUADRATIC\_VARIATION}}$$
3. **Monotonicity Qualification**:
   $\partial_s \chi_s \ge 0$ is non-strict in regions/intervals where $J_\omega = 0$. Strict monotonicity requires the non-degeneracy hypothesis $\mathbb{E}[\|D_s J_\omega\|_F^2] > 0$.

---

## 4. Machine Verification Audit

- All 9 worker tests in `tests/test_tp2_g3_suite.py` executed and passed.
- 5 new independent verification tests in `tests/test_tp2_g3_independent_verification.py` passed, confirming the 3 cases of $\chi$, PSD vs PD rank structure, sign mutation rejection, tensor ordering mutation rejection, and non-strict monotonicity.
- Total repository test count: **28/28 tests passed**.
