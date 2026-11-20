# TP2-G3: EXACT COVARIANCE TENSOR DYNAMICS

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Mathematical Identity  

---

## 1. Covariance Matrix Definitions

Let $m := \mathbb{E}[ Z_s ] = \omega(x, T)$ be the constant mean vector.
Define the full $3 \times 3$ covariance tensor of the stochastic Cauchy contribution $Z_s$:
$$C_s := \operatorname{Cov}(Z_s) = \mathbb{E}\left[ (Z_s - m)(Z_s - m)^T \right] \in \mathbb{R}^{3 \times 3}, \quad s \in [0, T].$$
In forwardized time $\tau = T - s$:
$$\widetilde{C}_\tau := C_{T-\tau} = \mathbb{E}\left[ (Y_\tau - m)(Y_\tau - m)^T \right], \quad \tau \in [0, T].$$
Terminal boundary condition:
$$\widetilde{C}_0 = C_T = 0.$$

---

## 2. Derivation via Itô's Product Rule

Let $M_\tau := Y_\tau - m = \int_0^\tau \Sigma_{\tau'} dB_{\tau'}$.
Applying the matrix Itô product rule to the outer product $M_\tau M_\tau^T$:
$$d( M_\tau M_\tau^T ) = (d M_\tau) M_\tau^T + M_\tau (d M_\tau)^T + (d M_\tau)(d M_\tau)^T.$$
The differential cross terms are:
$$(d M_\tau)(d M_\tau)^T = (\Sigma_\tau dB_\tau)(\Sigma_\tau dB_\tau)^T = \Sigma_\tau (dB_\tau dB_\tau^T) \Sigma_\tau^T = \Sigma_\tau (I_3 d\tau) \Sigma_\tau^T = (\Sigma_\tau \Sigma_\tau^T) d\tau.$$

Taking expectations on both sides:
$$\mathbb{E}[(d M_\tau) M_\tau^T] = 0 \quad \text{(martingale property of Itô stochastic integral)},$$
$$\mathbb{E}[M_\tau (d M_\tau)^T] = 0.$$
Therefore:
$$d \widetilde{C}_\tau = d \mathbb{E}[ M_\tau M_\tau^T ] = \mathbb{E}[ \Sigma_\tau \Sigma_\tau^T ] d\tau \implies \boxed{ \frac{d}{d\tau} \widetilde{C}_\tau = \mathbb{E}[ \Sigma_\tau \Sigma_\tau^T ] }$$

---

## 3. Translation to Original Time $s$ and Tensor Representation

Since $\tau = T - s$, the derivative transformation gives $\frac{d}{d\tau} = - \frac{\partial}{\partial s}$.
Therefore, in original time $s \in [0, T]$:
$$\boxed{ \frac{\partial}{\partial s} C_s = - \mathbb{E}[ \Sigma_s \Sigma_s^T ] \preceq 0 }$$

Integrating backward from $s$ to $T$ using the terminal condition $C_T = 0$:
$$C_s = C_T - \int_s^T \frac{\partial C_r}{\partial r} dr = \int_s^T \mathbb{E}[ \Sigma_r \Sigma_r^T ] dr.$$

Substituting $\Sigma_r = \sqrt{2\nu} D_r J_\omega(A_r, r)$:
$$\Sigma_r \Sigma_r^T = 2\nu \, D_r \, J_\omega(A_r, r) \, J_\omega(A_r, r)^T \, D_r^T.$$
Thus:
$$\boxed{ C_s = 2\nu \int_s^T \mathbb{E}\left[ D_r \, (J_\omega J_\omega^T)(A_r, r) \, D_r^T \right] dr }$$

In index notation under **Convention M**:
$$\boxed{ [C_s]_{ij} = 2\nu \int_s^T \mathbb{E}\left[ [D_r]_{ik} \frac{\partial \omega_k}{\partial x_m}(A_r, r) \frac{\partial \omega_l}{\partial x_m}(A_r, r) [D_r]_{jl} \right] dr }$$

---

## 4. Matrix Positivity and Loewner Order

1. For every realization and every $r \in [s, T]$, the matrix $\Sigma_r \Sigma_r^T$ is symmetric positive semi-definite ($\Sigma_r \Sigma_r^T \succeq 0$).
2. The expectation and integral preserve positive semi-definiteness:
   $$\boxed{ C_s \succeq 0 \quad \text{for all } s \in [0, T] }$$
3. As $s$ decreases (looking farther backward into the flow history), $C_s$ grows monotonically in the **Loewner partial order**:
   $$0 \le s_1 \le s_2 \le T \implies C_{s_1} \succeq C_{s_2} \succeq 0.$$
4. **Rank Control**:
   Since $D_r \in SL(3, \mathbb{R})$ is invertible ($\det D_r = 1$), the rank of $\Sigma_r = \sqrt{2\nu} D_r J_\omega$ is determined entirely by the spatial vorticity Jacobian $J_\omega$:
   $$\operatorname{rank}(\Sigma_r) = \operatorname{rank}(J_\omega(A_r, r)).$$
   Stochastic covariance production occurs exclusively in directions along which vorticity possesses spatial variation.
