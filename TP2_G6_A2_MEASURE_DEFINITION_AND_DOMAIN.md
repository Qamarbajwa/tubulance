# TP2-G6-A2: Rigorous Measure Definitions, Domains, and Normalizations

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A2 (Work Package 1)`  
**Target Bridge:** `B2 — History-to-Eulerian Coverage`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. The Stochastic Flow and Probability Space

Let $(\Omega, \mathcal{F}, (\mathcal{F}_t)_{t \ge 0}, \mathbb{P})$ be a standard filtered probability space carrying a 3D standard Brownian motion $W_t$.

For a smooth divergence-free velocity field $u \in C([0, T]; C^\infty(\mathbb{T}^3; \mathbb{R}^3))$ with $\nabla \cdot u = 0$, and for any observation time $t \in (0, T]$ and evaluation point $x \in \mathbb{T}^3$, the backward stochastic flow $s \mapsto A_s(x) = A_{t, s}(x)$ for $s \in [0, t]$ is the unique strong solution to the backward stochastic differential equation:
\[
d A_s(x) = - u(A_s(x), s) \, ds + \sqrt{2\nu} \, dW_s, \quad s \in [0, t], \quad A_t(x) = x,
\]
where the Brownian increment $dW_s = W_s - W_{s - ds}$ acts backwards in time (or equivalently under forwardized time $\tau = t - s \in [0, t]$).

The forwardized spatial gradient of the backward flow, denoted by the deformation tensor $D_s(x) = \nabla_x A_s(x) \in \mathbb{R}^{3 \times 3}$, satisfies the pathwise random ordinary differential equation:
\[
\frac{d}{ds} D_s(x) = - D_s(x) \nabla u(A_s(x), s), \quad s \in [0, t], \quad D_t(x) = I_{3 \times 3}.
\]

---

## 2. The Physical Stochastic History Measure $\mu_s$

Let $\omega(x, s) = \nabla \times u(x, s)$ denote the vorticity field. The backward-pulled Lagrangian vorticity vector along the stochastic trajectory is:
\[
Z_s(x) := D_s(x) \omega(A_s(x), s) \in \mathbb{R}^3.
\]

The enstrophy / Cauchy-energy denominator at history time $s$ is the stochastic expectation:
\[
S_s(x) := \mathbb{E}_{\mathbb{P}} \left[ |Z_s(x)|^2 \right] = \mathbb{E}_{\mathbb{P}} \left[ |D_s(x) \omega(A_s(x), s)|^2 \right].
\]

### Definition 1.1 (Stochastic History Measure $\mu_s^x$)
On the non-zero enstrophy domain $\{x \in \mathbb{T}^3 : S_s(x) > 0\}$, the physical stochastic history probability measure $\mu_s^x$ on the path space $(\Omega, \mathcal{F})$ is defined by the Radon–Nikodym derivative:
\[
d\mu_s^x(\omega) := \frac{|Z_s(x)|^2}{S_s(x)} \, d\mathbb{P}(\omega) = \frac{|D_s(x) \omega(A_s(x), s)|^2}{\mathbb{E}_{\mathbb{P}}[|D_s(x) \omega(A_s(x), s)|^2]} \, d\mathbb{P}(\omega).
\]

### Normalization and Domain:
1. **Total Mass:**
   \[
   \int_\Omega d\mu_s^x = \mathbb{E}_{\mathbb{P}} \left[ \frac{|Z_s(x)|^2}{S_s(x)} \right] = \frac{S_s(x)}{S_s(x)} = 1.
   \]
2. **Support:** Supported on the sub-event of trajectories where $Z_s(x) \ne 0$.
3. **Spatially Averaged History Measure $\bar{\mu}_s$:**
   Integrating over the spatial observation points with respect to normalized spatial Lebesgue measure $\bar{dx} = \frac{dx}{|\mathbb{T}^3|}$:
   \[
   d\bar{\mu}_s(\omega) := \left( \frac{\int_{\mathbb{T}^3} |Z_s(x)|^2 dx}{\int_{\mathbb{T}^3} S_s(x) dx} \right) d\mathbb{P}(\omega).
   \]

---

## 3. Eulerian Reference Measures and Superlevel Sets

### Definition 1.2 (Eulerian Measures)
1. **Lebesgue Volume Measure on $\mathbb{T}^3$:** Denoted by $dx$. Total volume $|\mathbb{T}^3| = 1$.
2. **Normalized Torus Measure:** $\bar{dx} = dx / |\mathbb{T}^3| = dx$.
3. **Enstrophy Density Measure:** $d\mathcal{E}_s(x) := \frac{|\omega(x, s)|^2}{\|\omega(s)\|_{L^2}^2} dx$.

### Definition 1.3 (High-Vorticity Superlevel Sets)
Let $M(s) := \|\omega(\cdot, s)\|_{L^\infty(\mathbb{T}^3)}$ denote the peak vorticity amplitude at time $s$. For any threshold parameter $\alpha \in (0, 1)$, the high-vorticity superlevel set is defined by:
\[
E_s(\alpha) := \left\{ y \in \mathbb{T}^3 : |\omega(y, s)| \ge \alpha M(s) \right\}.
\]

### Fundamental Chebyshev Volume Bound:
By Chebyshev's inequality on $L^2$:
\[
\|\omega(s)\|_{L^2}^2 = \int_{\mathbb{T}^3} |\omega(y, s)|^2 dy \ge \int_{E_s(\alpha)} |\omega(y, s)|^2 dy \ge \alpha^2 M(s)^2 |E_s(\alpha)|.
\]
Therefore, the spatial volume of $E_s(\alpha)$ is bounded universally by:
\[
|E_s(\alpha)| \le \frac{\|\omega(s)\|_{L^2}^2}{\alpha^2 M(s)^2} = \frac{2 \Omega(s)}{\alpha^2 M(s)^2}.
\]
As $M(s) \to \infty$ (at a hypothetical finite-time singularity), if the total enstrophy $\Omega(s)$ is finite or grows slower than $M(s)^2$, the spatial volume of the high-vorticity set must collapse to zero:
\[
|E_s(\alpha)| \le \mathcal{O}(M(s)^{-2}) \to 0.
\]

---

## 4. The Measure Alignment Obligation

The central quantity in the enstrophy growth identity is the pathwise relative deformation density:
\[
\Xi_s(x) = \frac{\|D_s(x) J_\omega(A_s(x), s)\|_F^2}{|D_s(x) \omega(A_s(x), s)|^2},
\]
which enters via the stochastic expectation:
\[
\mathbb{E}_{\mu_s^x}[\Xi_s(x)] = \int_\Omega \Xi_s(x, \omega) \, d\mu_s^x(\omega).
\]

**The Non-Equivalence Principle:**
The history measure $\mu_s^x$ is defined on the probability space $\Omega$ and weighted by the deformation-vorticity product $|D_s \omega|^2$. It is **not** Lebesgue measure $dx$.
Any claim that bounds on $\Xi$ or $\omega$ in Eulerian space $(dx)$ transfer to bounds under $\mathbb{E}_{\mu_s}$ requires a proved measure-theoretic bridge.
