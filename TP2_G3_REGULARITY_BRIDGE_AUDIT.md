# TP2-G3: REGULARITY-BRIDGE & NON-CIRCULARITY AUDIT

**Authority:** Independent E4 Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance Standard:** Autonomous Project Governance v2.9.3 (Tier T4)  
**Status:** Authoritative Regularity-Bridge Audit  

---

## 1. What Is Exactly Established vs What Remains Open

### Exactly Established in TP2-G3:
1. Exact backward stochastic Cauchy martingale differential $d_s Z_s = \sqrt{2\nu} D_s [(\widehat{d}W_s \cdot \nabla_M)\omega](A_s, s)$.
2. Forwardized Itô SDE $dY_\tau = \Sigma_\tau dB_\tau$ with $\Sigma = \sqrt{2\nu} D J_\omega$.
3. Exact mean conservation: $\mathbb{E}[Z_s] = \omega(x, T)$ for all $s \in [0, T]$.
4. Exact covariance matrix quadratic variation: $C_s = 2\nu \int_s^T \mathbb{E}[ D_r J_\omega J_\omega^T D_r^T ] dr \succeq 0$.
5. Exact scalar variance budget: $V_s = 2\nu \int_s^T \mathbb{E}[ \| D_r J_\omega \|_F^2 ] dr$.
6. Monotone reparameterization: $\chi_s = \frac{|\omega(x,T)|^2}{|\omega(x,T)|^2 + V_s}$ with $\partial_s \chi_s \ge 0$.

### NOT Established (The Regularity Gap):
1. **No Lower Bound on Covariance Production**:
   The quadratic variation rate $Q_s := 2\nu \mathbb{E}[ \| D_s J_\omega(A_s, s) \|_F^2 ]$ is non-negative ($Q_s \ge 0$), but Navier–Stokes a-priori energy estimates provide **no lower bound** forcing $Q_s > 0$ or forcing $V_s$ to outgrow pathwise stretching $\mathbb{E}[\|D_s\|^2]$.
2. **No Blow-up Exclusion**:
   Monotonicity $\partial_s \chi_s \ge 0$ does not imply that $\chi_s \to 0$ or that $\omega(x, T)$ remains bounded near a candidate singular time.
3. **No Closure of BKM / Serrin Criteria**:
   Deriving continuation from $V_s$ would require a-priori control of $\int_0^T \|\omega\|_{L^\infty} dt$ or critical norms, which is circular.

---

## 2. Formal Status of the Regularity Bridge

$$\boxed{\textbf{TP2\_G3\_REGULARITY\_BRIDGE = OPEN}}$$

**Scientific Finding**:
The stochastic Cauchy covariance identities provide an exact representation of viscous dispersion along Lagrangian histories, but **do not constitute a regularity theorem**. Connecting quadratic variation production to a non-circular continuation criterion is the central open problem assigned to Gate TP2-G4.
