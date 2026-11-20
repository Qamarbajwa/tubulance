# TP2-G3: FORWARDIZED MARTINGALE CONTRACT & TIME REVERSAL

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Mathematical Contract  

---

## 1. Time-Reversal Transformation

To eliminate any potential sign ambiguity inherent in backward-Itô calculus, we map the backward history parameter $s \in [0, T]$ to an ordinary forward history parameter $\tau \in [0, T]$.

### Definition (Forwardized Time Variable):
$$\tau := T - s \in [0, T].$$
- At $\tau = 0$: $s = T$ (terminal observation state).
- At $\tau = T$: $s = 0$ (initial data state).
- Differential relation: $d\tau = -ds$.

### Definition (Forwardized Cauchy Process):
$$Y_\tau := Z_{T-\tau} = D_{T-\tau} \, \omega(A_{T-\tau}, T-\tau).$$
- Initial state at $\tau = 0$: $Y_0 = Z_T = \omega(x, T)$.

### Definition (Forwardized Brownian Motion):
Define the time-reversed Brownian motion $B_\tau$ on $[0, T]$:
$$B_\tau := - (W_{T-\tau} - W_T) = W_T - W_{T-\tau}.$$
- $B_0 = 0$.
- For any $0 \le \tau_1 \le \tau_2 \le T$:
  $$B_{\tau_2} - B_{\tau_1} = W_{T-\tau_1} - W_{T-\tau_2} \sim \mathcal{N}(0, (\tau_2 - \tau_1) I_3).$$
- $B_\tau$ is a standard 3D Brownian motion with respect to the forward filtration $\mathcal{G}_\tau := \mathcal{F}_T^{T-\tau}$.
- Increment relation: $dB_\tau = - \widehat{d}W_{T-\tau}$.

---

## 2. Forwardized Itô SDE and Noise Matrix

Under forwardized time $\tau$, the process $Y_\tau$ solves the standard forward Itô stochastic differential equation:
$$\boxed{ d Y_\tau = \Sigma_\tau \, dB_\tau, \quad Y_0 = \omega(x, T) }$$
where the $3 \times 3$ stochastic noise matrix $\Sigma_\tau$ is:
$$\boxed{ \Sigma_\tau := \sqrt{2\nu} \, D_{T-\tau} \, J_\omega(A_{T-\tau}, T-\tau) }$$

In index notation under **Convention M**:
$$\boxed{ [\Sigma_\tau]_{ik} = \sqrt{2\nu} \, [D_{T-\tau}]_{ij} \, \frac{\partial \omega_j}{\partial x_k}(A_{T-\tau}, T-\tau) = \sqrt{2\nu} \, [D_{T-\tau}]_{ij} \, [J_\omega]_{jk}(A_{T-\tau}, T-\tau) }$$

---

## 3. Forward Martingale Properties

1. **Integral Representation**:
   $$Y_\tau = \omega(x, T) + \int_0^\tau \Sigma_{\tau'} \, dB_{\tau'}.$$
2. **Exact Mean Invariance**:
   $$\mathbb{E}[ Y_\tau ] = \mathbb{E}[ Y_0 ] = \omega(x, T) \quad \text{for all } \tau \in [0, T].$$
3. **Zero-Drift Property**:
   $Y_\tau$ is a continuous $L^2$ martingale on $[0, T]$ with respect to filtration $\mathcal{G}_\tau$.
