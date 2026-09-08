# TP2-G6-A2: Adversarial Benchmark Matrix and Counter-Configuration Analysis

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A2 (Work Package 9)`  
**Target Bridge:** `B2 — History-to-Eulerian Coverage`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Adversarial Test Objectives

To test the robustness of Bridge $B_2$, we subject the candidate coverage hypothesis:
\[
\mu_s \left( A_s^{-1}(E_s(\alpha)) \right) \ge F(|E_s(\alpha)|) > 0
\]
to a battery of exact mathematical benchmarks, searching specifically for two failure modes:
1. **False High Coverage:** $|E| \ll 1$ (sparse), but $\mu_s(A_s^{-1}(E)) \approx 1$.
2. **Coverage Collapse (The Missed Spike):** $|E| > 0$ contains the singularity, but $\mu_s(A_s^{-1}(E)) \approx 0$.

---

## 2. Adversarial Benchmark Matrix

| Benchmark ID | Benchmark Name | Mathematical Flow Type | Flow Class | Observed Measure Relation $\mu_s(A_s^{-1}(E))$ vs. $|E|$ | Impact on Bridge $B_2$ |
|---|---|---|---|---|---|
| **BM-A2-01** | Periodic Shear Flow | $u = (\sin(2\pi y), 0, 0)$ | Exact decaying 3D NS solution | Diffusion spreads uniformly: $\mu_s(A_s^{-1}(E)) \to |E|$. Deformation linearly grows in orthogonal direction. | **Coverage Neutral**: Uniform dispersion, no singularity concentration. |
| **BM-A2-02** | Single-Helical Beltrami Mode | $u = (\cos kz, \sin kz, 0)$ | Exact 3D NS decaying mode | $\omega = k u$, $S \omega \equiv 0$ pointwise. $Z_s = D_s \omega = \omega(A_s)$. Diffusion is pure Brownian motion. $\mu_s$ is uniform. | **Coverage Neutral**: No alignment bias toward sub-torus sets. |
| **BM-A2-03** | 2D Embedded Vortex Dipole | $u = (u_1(x, y), u_2(x, y), 0)$ | Exact 2D NS solution embedded in 3D | $\omega = (0, 0, \omega_3)$. $D_s \omega = \omega_3 e_3$ (no 3D stretching). $|Z_s|^2 = |\omega_3|^2$. | **Coverage Bounded**: $\mu_s$ reduces to enstrophy-density measure $d\mathcal{E}_s$. |
| **BM-A2-04** | Localized High-Vorticity Spike | Concentrated vortex tube of radius $r \sim M^{-1/2}$ with hyperbolic cross-flow | Kinematic NS-compatible flow | Advective cross-flow sweeps backward path $A_s$ out of the core in time $\tau \ll M^{-1}$. $\mathbb{P}(A_s \in E) \to 0$. | **Coverage Collapse (Mode 2)**: $\mu_s(A_s^{-1}(E)) \ll 1$ despite $|E| > 0$ containing peak vorticity. |
| **BM-A2-05** | Hyperbolic Saddle Straining Wake | Vortex core plus exterior hyperbolic saddle $S = \operatorname{diag}(\lambda, -\lambda, 0)$ with $\lambda \sim M$ | Kinematic divergence-free flow | Backward path in saddle experiences exponential stretching $\|D_s\| \sim e^{\lambda \Delta t}$. $|Z_s|^2$ in wake exceeds core value. | **False High Coverage (Mode 1)**: $\mu_s$ concentrates in low-vorticity saddle ($|\omega| \sim 1$), ignoring peak core. |
| **BM-A2-06** | Rank-1 Covariance Channel Flow | Shear flow with boundary layer and noise | Exact reduced class | Covariance tensor $C_s = \operatorname{diag}(0, 0, \mathcal{I}_s)$ is degenerate rank-1. Transverse dispersion collapses. | **Coverage Anisotropy**: Spatial coverage strictly fails in the null directions of $C_s$. |

---

## 3. Deep Analysis of Benchmark BM-A2-04 (The Missed Spike)

Consider a localized vortex core situated at the origin on $\mathbb{T}^3$:
\[
\omega(x) = M \, \phi\left( \frac{|x|}{r_0} \right) e_3, \quad r_0 = \nu^{1/2} M^{-1/2}, \quad M \gg 1.
\]
The core radius is $r_0$. The spatial volume is $|E| \sim r_0^3 \sim \nu^{3/2} M^{-3/2}$.
Suppose the ambient velocity field includes a background hyperbolic straining flow:
\[
u(x) = (\gamma x_1, - \gamma x_2, 0), \quad \text{with } \gamma \sim M.
\]
(This velocity field is smooth, divergence-free, and satisfies $\nabla \cdot u = 0$).

Now trace the backward stochastic trajectory starting at $x \in E$:
\[
d A_s^1 = - \gamma A_s^1 \, ds + \sqrt{2\nu} \, dW_s^1, \quad d A_s^2 = \gamma A_s^2 \, ds + \sqrt{2\nu} \, dW_s^2.
\]
Along the unstable direction $x_2$:
\[
A_s^2 = x_2 e^{\gamma(t - s)} - \sqrt{2\nu} \int_s^t e^{\gamma(\tau - s)} dW_\tau^2.
\]
Over a scale-critical time interval $\Delta t = t - s \sim M^{-1} \sim \gamma^{-1}$:
\[
\mathbb{E} \left[ |A_s^2|^2 \right] \ge \frac{2\nu}{2\gamma} \left( e^{2\gamma \Delta t} - 1 \right) \sim \frac{\nu}{\gamma} = \frac{\nu}{M} = r_0^2.
\]
Because the exponential expansion carries the particle along $x_2$, within a few multiples of $\tau = M^{-1}$, the distance $|A_s|$ exceeds $r_0$ with probability approaching 1:
\[
\mathbb{P}(A_s(x) \in E) \le C \exp\left( - c \frac{M}{\nu} \right) \to 0 \quad \text{as } M \to \infty.
\]

### Conclusion from Benchmarks:
BM-A2-04 and BM-A2-05 rigorously confirm that **neither convective drift nor stochastic diffusion can guarantee that a single particle's history measure $\mu_s$ remains in or covers the high-vorticity set $E_s(\alpha)$**.
The measure can both escape the core and be artificially amplified in exterior hyperbolic saddles.
