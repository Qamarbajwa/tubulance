# TP2-G3: TRACE VARIANCE BUDGET & SECOND MOMENT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Mathematical Identity  

---

## 1. Scalar Variance Evolution

Define the scalar total variance of the stochastic Cauchy vector $Z_s$:
$$V_s := \operatorname{Var}(Z_s) = \mathbb{E}\left[ |Z_s - m|^2 \right] = \operatorname{tr}(C_s), \quad s \in [0, T].$$
Taking the trace of the covariance differential $\frac{\partial}{\partial s} C_s = - \mathbb{E}[\Sigma_s \Sigma_s^T]$:
$$\frac{\partial}{\partial s} V_s = \operatorname{tr}\left( \frac{\partial}{\partial s} C_s \right) = - \mathbb{E}\left[ \operatorname{tr}(\Sigma_s \Sigma_s^T) \right].$$

Using the cyclic property of the trace:
$$\operatorname{tr}(\Sigma_s \Sigma_s^T) = \operatorname{tr}\left( 2\nu D_s J_\omega J_\omega^T D_s^T \right) = 2\nu \operatorname{tr}\left( (D_s J_\omega)(D_s J_\omega)^T \right) = 2\nu \| D_s J_\omega(A_s, s) \|_F^2,$$
where $\| \cdot \|_F$ denotes the matrix Frobenius norm ($\|M\|_F^2 = \sum_{i,j} M_{ij}^2$).

Therefore, the exact rate of change of scalar variance is:
$$\boxed{ \frac{\partial}{\partial s} V_s = - 2\nu \, \mathbb{E}\left[ \| D_s J_\omega(A_s, s) \|_F^2 \right] \le 0 }$$

Integrating backward from $s$ to $T$ with terminal condition $V_T = 0$:
$$\boxed{ V_s = 2\nu \int_s^T \mathbb{E}\left[ \| D_r J_\omega(A_r, r) \|_F^2 \right] dr }$$

---

## 2. Second-Moment Variance Identity

Because the mean vector $m = \mathbb{E} Z_s = \omega(x, T)$ is constant for all $s \in [0, T]$, the second-moment identity in Hilbert space:
$$\mathbb{E}|Z_s|^2 = |\mathbb{E} Z_s|^2 + \mathbb{E}|Z_s - \mathbb{E} Z_s|^2$$
becomes the exact representation:
$$\boxed{ \mathbb{E}|Z_s|^2 = |\omega(x, T)|^2 + V_s = |\omega(x, T)|^2 + 2\nu \int_s^T \mathbb{E}\left[ \| D_r J_\omega(A_r, r) \|_F^2 \right] dr }$$

---

## 3. Mathematical Classification

- **Identity Nature**:
  $$\boxed{ \text{EXACT\_MARTINGALE\_QUADRATIC\_VARIATION\_IDENTITY} }$$
- **Rigorous Grounding**:
  This identity is the exact continuous-time Itô isometry for the stochastic Cauchy vector process. It holds on any interval $[0, T]$ where the underlying Navier–Stokes solution $u$ is classical ($u \in C([0, T]; C^2)$).
