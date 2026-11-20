# TP2-G3: BACKWARD-ITÔ DIFFERENTIAL DERIVATION

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3 (Exact Stochastic Cauchy Covariance Evolution)`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Risk Tier:** `T4`  
**Status:** Authoritative Candidate Derivation  

---

## 1. Domain, Solution Setting, and Trajectory Framework

Let $\Omega = \mathbb{T}^3$ or $\mathbb{R}^3$ with smooth decaying velocity $u \in C([0, T]; H^s(\Omega))$ ($s > 5/2$) and vorticity $\omega = \nabla \times u$.
There are no physical boundaries; boundary local-time and boundary vorticity flux terms are identically zero.

Fix a terminal space-time point $(x, T)$.
For $s \in [0, T]$:
- Let $A_s \equiv A_T^s(x) = X_{s,T}^{-1}(x)$ denote the backward trajectory originating from $x$ at time $T$.
- Let $D_s \equiv D_T^s(x) = [J_{A_T^s}(x)]^{-1} = J_{X_{s,T}}(A_T^s(x)) \in SL(3, \mathbb{R})$.
- The stochastic Cauchy contribution vector is:
  $$Z_s := D_s \, \omega(A_s, s), \quad Z_{s, i} = [D_s]_{ij} \, \omega_j(A_s, s).$$
- Terminal boundary condition: at $s = T$, $A_T = x$, $D_T = I_3$, $Z_T = \omega(x, T)$.

---

## 2. Backward-Itô Differential of the Cauchy Vector

Under the backward stochastic flow, $A_s$ satisfies the backward Itô SDE running backward from $T$ to $s$:
$$d_s A_s = u(A_s, s) ds + \sqrt{2\nu} \, \widehat{d}W_s, \quad A_T = x,$$
where $\widehat{d}W_s$ represents the backward Brownian increment with backward filtration $\mathcal{F}_T^s = \sigma(W_\tau - W_s : s \le \tau \le T)$.

Applying the stochastic Leibniz rule / chain rule to $Z_s = D_s \omega(A_s, s)$:
$$d_s Z_s = (d_s D_s) \omega(A_s, s) + D_s (d_s \omega(A_s, s)) + d_s D_s \cdot d_s \omega.$$

By the fundamental Constantin–Iyer / Eyink–Gupta–Zaki representation:
1. The deterministic drift terms in the vorticity equation $\partial_s \omega + (u \cdot \nabla)\omega = (\omega \cdot \nabla)u + \nu \Delta \omega$ are exactly cancelled by the stochastic deformation transport and diffusion of $D_s$.
2. The drift of $Z_s$ vanishes identically along backward stochastic paths:
   $$\mathbb{E}[ d_s Z_s \mid \mathcal{F}_T^s ] = 0.$$
3. The remaining stochastic dispersion arises purely from the spatial gradient of vorticity $J_\omega$ contracted with the Brownian increment $\widehat{d}W_s$:
   $$\boxed{ d_s Z_s = \sqrt{2\nu} \, D_s \left[ (\widehat{d}W_s \cdot \nabla_M) \omega \right](A_s, s) }$$

In index notation under **Convention M** ($[J_\omega]_{jk} = \frac{\partial \omega_j}{\partial x_k}$):
$$\boxed{ d_s Z_{s, i} = \sqrt{2\nu} \, [D_s]_{ij} \, \frac{\partial \omega_j}{\partial x_k}(A_s, s) \, \widehat{d}W_s^k = \sqrt{2\nu} \, [D_s]_{ij} \, [J_\omega]_{jk}(A_s, s) \, \widehat{d}W_s^k }$$

---

## 3. Backward Martingale Property

Because the drift is identically zero, the process $s \mapsto Z_s$ is a **backward martingale** with respect to the backward filtration $\mathcal{F}_T^s$:
$$\mathbb{E}[ Z_s \mid \mathcal{F}_T^t ] = Z_t \quad \text{for all } 0 \le s \le t \le T.$$
In particular, taking expectations conditioned on $s=T$:
$$\mathbb{E}[ Z_s ] = Z_T = \omega(x, T) \quad \text{for all } s \in [0, T].$$
