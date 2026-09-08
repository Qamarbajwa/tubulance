# TP2-G6-A2: Stochastic Flow Push-Forward Audit

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A2 (Work Package 3)`  
**Target Bridge:** `B2 — History-to-Eulerian Coverage`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Pathwise Volume Preservation of the Stochastic Flow

Consider the backward stochastic differential equation on $\mathbb{T}^3$:
\[
d A_s(x) = - u(A_s(x), s) \, ds + \sqrt{2\nu} \, dW_s, \quad s \in [0, t], \quad A_t(x) = x.
\]
Let $J_s(x) := \det(\nabla_x A_s(x))$ denote the Jacobian determinant of the mapping $x \mapsto A_s(x)$ for a fixed sample path $\omega \in \Omega$.

### Theorem 3.1 (Pathwise Incompressibility of the Stochastic Flow)
Let $u \in C([0, T]; C^1(\mathbb{T}^3))$ with $\nabla \cdot u = 0$ everywhere on $\mathbb{T}^3$. Then for almost every sample path $\omega \in \Omega$ and for all $s \in [0, t]$:
\[
J_s(x) = \det(\nabla_x A_s(x)) \equiv 1 \quad \forall x \in \mathbb{T}^3.
\]

#### Proof:
By Kunita's stochastic Jacobi formula for flows of SDEs with additive noise (Kunita 1990, *Stochastic Flows and Stochastic Differential Equations*, Theorem 4.6.1; Constantin–Iyer 2008, *Comm. Pure Appl. Math.*):
Since the noise term $\sqrt{2\nu} dW_s$ is spatially homogeneous (independent of $x$), the spatial derivative of the noise is zero: $\nabla_x (\sqrt{2\nu} dW_s) = 0$.
Therefore, the differential of $J_s(x)$ contains no Stratonovich or Itô diffusion term. It satisfies the deterministic Liouville ODE along each path:
\[
d J_s(x) = - (\nabla \cdot u)(A_s(x), s) \, J_s(x) \, ds.
\]
Because $\nabla \cdot u \equiv 0$, we have:
\[
d J_s(x) = 0, \quad \text{with initial condition } J_t(x) = \det(I_{3 \times 3}) = 1.
\]
Hence $J_s(x) \equiv 1$ identically. $\blacksquare$

### Corollary 3.2 (Pathwise Lebesgue Push-Forward Invariance)
For any Borel set $B \subset \mathbb{T}^3$ and for every fixed sample path $\omega$:
\[
(A_s)_\# dx (B) = \int_{\mathbb{T}^3} \mathbf{1}_B(A_s(x)) \, dx = |B|.
\]
The spatial Lebesgue measure $dx$ is strictly and unconditionally preserved by the stochastic flow pathwise.

---

## 2. Why $(A_s)_\# dx = dx$ Does NOT Solve Bridge $B_2$

A dangerous fallacy is to infer that because $(A_s)_\# dx = dx$, the history measure $\mu_s$ must automatically cover Eulerian sets.
This conflates two completely different measures:

1. **Lebesgue Push-Forward vs. Weighted History Measure:**
   The history measure $\mu_s^x$ is defined on path space $\Omega$ with density proportional to $|Z_s(x)|^2 = |D_s(x) \omega(A_s(x), s)|^2$.
   Its push-forward from a fixed point $x$ is:
   \[
   (A_s^x)_\# \mu_s^x (B) = \mathbb{E}_{\mathbb{P}} \left[ \frac{|D_s(x) \omega(A_s(x), s)|^2}{S_s(x)} \mathbf{1}_B(A_s(x)) \right].
   \]
   This is **not** an integral over $x$; it is an expectation over Brownian paths starting from a single point $x$!

2. **Transition Density vs. Uniform Lebesgue Measure:**
   The unweighted law of $A_s(x)$ starting from $x$ is:
   \[
   \mathbb{P}(A_s(x) \in B) = \int_B p(s, y; t, x) \, dy,
   \]
   where $p(s, y; t, x)$ is the transition probability density of the diffusion with drift $-u$.
   Even though $\int_{\mathbb{T}^3} p(s, y; t, x) dx = 1$ (by incompressibility), for a fixed $x$, $p(s, y; t, x)$ is highly non-uniform and concentrates near $x$ for small $t - s$.

3. **Spatially Averaged Weighted Measure $\bar{\mu}_s$:**
   Even when integrated over all observation points $x$:
   \[
   \bar{\mu}_s(A_s^{-1}(B)) = \frac{1}{\int S_s dx} \int_{\mathbb{T}^3} \mathbb{E}_{\mathbb{P}} \left[ |D_s(x) \omega(A_s(x), s)|^2 \mathbf{1}_B(A_s(x)) \right] dx.
   \]
   Using $(A_s)_\# dx = dx$ on each path, let $y = A_s(x)$, so $x = A_s^{-1}(y)$.
   Then $\nabla_x A_s(x) = D_s(x) = [\nabla_y (A_s^{-1})(y)]^{-1}$.
   Substituting $y = A_s(x)$:
   \[
   \int_{\mathbb{T}^3} |D_s(x) \omega(A_s(x), s)|^2 \mathbf{1}_B(A_s(x)) \, dx = \int_B |[\nabla_y A_s^{-1}(y)]^{-1} \omega(y, s)|^2 \, dy.
   \]
   Taking expectation:
   \[
   \bar{\mu}_s(A_s^{-1}(B)) = \frac{1}{\bar{S}_s} \int_B \mathbb{E}_{\mathbb{P}} \left[ |[\nabla_y A_s^{-1}(y)]^{-1} \omega(y, s)|^2 \right] dy.
   \]

### Theorem 3.3 (Ceiling at B2-L1)
The Radon–Nikodym derivative of the spatially averaged history push-forward is:
\[
\rho_s(y) := \frac{d (A_s)_\# \bar{\mu}_s}{dy}(y) = \frac{1}{\bar{S}_s} \mathbb{E}_{\mathbb{P}} \left[ |[\nabla_y A_s^{-1}(y)]^{-1} \omega(y, s)|^2 \right].
\]
This density exists and is non-negative, confirming **Bridge B2-L1 (Push-Forward Absolute Continuity)**.

However, bounding $\rho_s(y)$ in $L^p$ (B2-L2) or bounding $\bar{\mu}_s(A_s^{-1}(E_s(\alpha)))$ from below (B2-L3) requires controlling the inverse deformation tensor:
\[
\mathbb{E} \left[ \|[\nabla_y A_s^{-1}(y)]^{-1}\|^2 \right].
\]
Because $\frac{d}{ds} D_s = - D_s \nabla u$, $D_s$ and $D_s^{-1}$ grow exponentially with the rate of strain $\int \|\nabla u\|_{L^\infty} ds$.
Without assuming BKM regularity, this factor can blow up or collapse arbitrarily.
Therefore, pathwise incompressibility secures **only B2-L1**, and cannot establish B2-L2 or higher.
