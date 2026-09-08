# TP2-G6-A2: Parabolic Regularity Envelopes and Scale-Critical Scaling

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A2 (Work Package 4)`  
**Target Bridge:** `B2 — History-to-Eulerian Coverage`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Dimensional Weights and Scale Derivation

Let $t_n$ be a sequence of times approaching a hypothetical finite-time singularity $T^*$, with peak vorticity amplitude:
\[
M_n := \|\omega(\cdot, t_n)\|_{L^\infty(\mathbb{T}^3)} \to \infty.
\]

From the dimensional reconciliation in `TP2-G6-B-R2`:
* Vorticity: $[\omega] = T^{-1}$, so $[M_n] = T^{-1}$.
* Viscosity: $[\nu] = L^2 T^{-1}$.
* Velocity: $[u] = L T^{-1}$.

To formulate scale-critical envelopes under the heat operator $\partial_t - \nu \Delta$, spatial length scales $\ell$ and time scales $\tau$ must balance diffusion:
\[
\frac{\ell^2}{\nu \tau} \sim 1 \implies \ell \sim \sqrt{\nu \tau}.
\]

### Scale Classification:
1. **Local Turnover Time Scale:**
   \[
   \tau_n := M_n^{-1} \quad (\text{Classification: Exact Dimensional Normalization}).
   \]
   On this time interval, the peak vorticity rotates fluid by $\mathcal{O}(1)$ radians.
2. **Viscous Parabolic Diffusion Length Scale:**
   \[
   r_n := \sqrt{\nu \tau_n} = \nu^{1/2} M_n^{-1/2} \quad (\text{Classification: Canonical Viscous Microscale}).
   \]
   This is the scale on which viscous dissipation balances the vorticity timescale.
3. **Convective Advection Length Scale:**
   Let $U_n := \|u(t_n)\|_{L^\infty}$. The convective displacement scale is $\ell_{\text{conv}} \sim U_n \tau_n = U_n M_n^{-1}$.
   Unlike $r_n$, $U_n$ is not scale-invariant (it scales as $L^3$ critical norm only when integrated or rescaled).

---

## 2. Parabolic Regularity Envelope Around Peak Vorticity

Consider a space-time parabolic cylinder centered at the peak vorticity point $(x_n, t_n)$:
\[
Q_n(\kappa) := B(x_n, \kappa r_n) \times [t_n - \kappa^2 \tau_n, t_n], \quad \kappa > 0.
\]

### What Does Parabolic Regularity Actually Guarantee?

#### Theorem 4.1 (Short-Time Parabolic Envelope Below Singularity)
Suppose $u$ is a classical solution on $[0, t_n]$. On the cylinder $Q_n(1)$:
1. By definition of $M_n$, $|\omega(x, t)| \le M_n$ everywhere on $\mathbb{T}^3 \times [0, t_n]$.
2. The vorticity equation on $Q_n(1)$ is:
   \[
   \partial_t \omega + u \cdot \nabla \omega = \nu \Delta \omega + (S \omega).
   \]
3. For backwards time $s \in [t_n - \tau_n, t_n]$, the maximum enstrophy production rate is bounded by:
   \[
   \left| \frac{d}{dt} |\omega|^2 \right| \le 2 |S| |\omega|^2 + \nu \Delta |\omega|^2 - 2\nu |\nabla \omega|^2.
   \]
   Because $|S| \le C BMO$ rather than $L^\infty$, this does **not** give a closed differential inequality for $|\omega|^2$ without assuming Beale–Kato–Majda.
4. If one assumes a priori that $|\omega(x, t)| \ge \alpha M_n$ at $(x_n, t_n)$, parabolic smoothing guarantees that for $s \in [t_n - \delta \tau_n, t_n]$ and $|x - x_n| \le \delta r_n$ (for some small $\delta = \delta(\alpha) > 0$):
   \[
   |\omega(x, s)| \ge \frac{\alpha}{2} M_n.
   \]

### Classification of the Scale:
* **The Parabolic Core $B(x_n, \delta r_n)$ is a `CONDITIONAL_REGULARITY_SCALE`:**
  It holds if $(x_n, t_n)$ is an isolated non-degenerate peak, but fails if extreme spatial oscillation or high-frequency cancellation occurs at sub-diffusive scales.
* **Volume of the Core:**
  \[
  |B(x_n, \delta r_n)| = \frac{4\pi}{3} \delta^3 r_n^3 = \frac{4\pi}{3} \delta^3 \nu^{3/2} M_n^{-3/2}.
  \]
  Notice that the spatial volume vanishes as $M_n^{-3/2}$.

---

## 3. The Scale-Mismatch Obstacle to Bridge $B_2$

Recall the backward diffusion:
\[
A_s(x_n) = x_n - \int_s^{t_n} u(A_\tau, \tau) d\tau + \sqrt{2\nu} (W_{t_n} - W_s).
\]
Over the duration $\Delta t = t_n - s = \tau_n = M_n^{-1}$:
1. **Diffusive Displacement:**
   \[
   \mathbb{E} \left[ |\sqrt{2\nu}(W_{t_n} - W_s)|^2 \right]^{1/2} = \sqrt{6\nu \tau_n} = \sqrt{6} \, r_n.
   \]
   The typical Brownian displacement $\sqrt{6} r_n$ is **larger** than the core radius $\delta r_n$ (since $\delta < 1$)!
2. **Convective Drift Displacement:**
   \[
   \left| \int_s^{t_n} u(A_\tau, \tau) d\tau \right| \approx |u(x_n, t_n)| \tau_n = \frac{|u(x_n, t_n)|}{M_n}.
   \]
   If $|u(x_n, t_n)| \gg \sqrt{\nu M_n}$, the drift sweeps the stochastic particle out of the parabolic cylinder $B(x_n, \delta r_n)$ in a fraction of the time scale $\tau_n$!

### Structural Conclusion:
Even within the exact parabolic regularity envelope, **the backward stochastic particle does not remain confined to the high-vorticity core**.
Both the diffusive spread ($\sim \sqrt{\nu \tau_n} \sim r_n$) and the convective drift ($\sim u \tau_n$) are equal to or larger than the core volume, causing the particle to escape with probability approaching 1 unless an unproved confinement mechanism exists.
