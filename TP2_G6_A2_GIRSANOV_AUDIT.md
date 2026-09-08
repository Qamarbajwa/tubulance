# TP2-G6-A2: Girsanov Transformation Audit and Exponential Weight Degeneracy

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A2 (Work Package 6)`  
**Target Bridge:** `B2 — History-to-Eulerian Coverage`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Girsanov Formulation for Backward Diffusion

Consider the backward SDE:
\[
d A_s = - u(A_s, s) \, ds + \sqrt{2\nu} \, dW_s, \quad s \in [0, t], \quad A_t = x.
\]
To relate the law of $A_s$ to the law of a pure Brownian motion $\tilde{A}_s = x + \sqrt{2\nu}(W_t - W_s)$, one applies the Girsanov theorem.

Define the stochastic exponential martingale candidate:
\[
\mathcal{M}_{s, t} := \exp\left( - \frac{1}{\sqrt{2\nu}} \int_s^t u(A_\tau, \tau) \cdot dW_\tau - \frac{1}{4\nu} \int_s^t |u(A_\tau, \tau)|^2 d\tau \right).
\]
If $\mathcal{M}_{s, t}$ is a true martingale under $\mathbb{P}$, then under the equivalent measure $\mathbb{Q}$ defined by $d\mathbb{Q} = \mathcal{M}_{0, t} d\mathbb{P}$, the process:
\[
\tilde{W}_\tau := W_\tau + \frac{1}{\sqrt{2\nu}} \int_\tau^t u(A_\sigma, \sigma) d\sigma
\]
is a standard Brownian motion, and $A_s$ behaves under $\mathbb{Q}$ as pure Brownian motion without drift.

---

## 2. The Novikov and Kazamaki Integrability Barriers

For $\mathcal{M}_{s, t}$ to be a uniformly integrable martingale, the classical sufficiency criteria are:

### 1. Novikov's Condition:
\[
\mathbb{E}_{\mathbb{P}} \left[ \exp\left( \frac{1}{4\nu} \int_0^t |u(A_\tau, \tau)|^2 d\tau \right) \right] < \infty.
\]

### 2. Kazamaki's Condition:
\[
\sup_{\sigma \in [0, t]} \mathbb{E}_{\mathbb{P}} \left[ \exp\left( \frac{1}{8\nu} \int_\sigma^t u(A_\tau, \tau) \cdot dW_\tau \right) \right] < \infty.
\]

### Audit Against Admissible Subcritical Data:
Can either Novikov or Kazamaki be verified using only the Leray–Hopf energy inequality:
\[
\sup_{\tau} \|u(\tau)\|_{L^2(\mathbb{T}^3)}^2 + 2\nu \int_0^t \|\nabla u(\sigma)\|_{L^2(\mathbb{T}^3)}^2 d\sigma \le E_0 < \infty?
\]

#### The Obstruction:
1. **Pathwise vs. Spatial Integration:**
   The integral in Novikov's condition is evaluated **along the random trajectory** $\tau \mapsto A_\tau$:
   \[
   \int_0^t |u(A_\tau, \tau)|^2 d\tau.
   \]
   Spatial energy bounds $\int_{\mathbb{T}^3} |u(x, \tau)|^2 dx \le E_0$ do **not** bound the pointwise trajectory evaluation $|u(A_\tau, \tau)|^2$.
2. **Exponential of Supercritical Quantity:**
   By Sobolev embedding on $\mathbb{T}^3$, $u \in L^2_t L^6_x$. In 3D space, a function in $L^6$ can have local singularities of the form $|u(x)| \sim |x|^{-\gamma}$ for any $\gamma < 1/2$.
   If $\gamma \in (0, 1/2)$, $|u(x)|^2 \sim |x|^{-2\gamma}$ with $2\gamma \in (0, 1)$.
   The Brownian path $A_\tau$ visits neighborhoods of such singularities.
   Taking the exponential of an integral of a potentially unbounded pathwise process produces divergent moments:
   \[
   \mathbb{E} \left[ \exp\left( \frac{1}{4\nu} \int_0^t |u(A_\tau, \tau)|^2 d\tau \right) \right] = \infty.
   \]
3. **Novikov Requires $u \in L^\infty$:**
   To guarantee Novikov's condition uniformly for all starting points $x$, one must assume:
   \[
   \int_0^t \|u(\cdot, \tau)\|_{L^\infty}^2 d\tau < \infty,
   \]
   which is again the **continuation-level Serrin criterion**!

---

## 3. Exponential Weight Degeneracy

Even if one restricts to short time $\Delta t = t - s \ll 1$ where Girsanov formally applies, the measure conversion factor is:
\[
\frac{d\mathbb{P}}{d\mathbb{Q}} = \exp\left( \frac{1}{\sqrt{2\nu}} \int_s^t u \cdot d\tilde{W}_\tau - \frac{1}{4\nu} \int_s^t |u|^2 d\tau \right).
\]
On any set where the drift velocity is large, e.g. $|u| \sim U_n \gg 1$:
\[
\frac{d\mathbb{P}}{d\mathbb{Q}} \le \exp\left( - \frac{U_n^2 \Delta t}{4\nu} + \mathcal{O}(U_n \sqrt{\Delta t}) \right).
\]
As $U_n^2 \Delta t / \nu \to \infty$, the Radon–Nikodym derivative **decays exponentially to zero**.

### Theorem 6.1 (Girsanov Coverage Collapse)
Let $E \subset \mathbb{T}^3$ be any target set. Under Girsanov transformation to Brownian motion $\mathbb{Q}$:
\[
\mathbb{P}(A_s(x) \in E) = \mathbb{E}_{\mathbb{Q}} \left[ \mathbf{1}_E(\tilde{A}_s(x)) \frac{d\mathbb{P}}{d\mathbb{Q}} \right].
\]
Because $\frac{d\mathbb{P}}{d\mathbb{Q}}$ can be exponentially small $\sim e^{- c U_n^2 \Delta t / \nu}$ on trajectories intersecting high-velocity regions, Girsanov comparison does **not** provide a uniform lower bound on $\mathbb{P}(A_s \in E)$ or $\mu_s(A_s^{-1}(E))$.

### Circularity Finding:
The Girsanov route is either:
* **`CIRCULAR`** (if one assumes $u \in L^\infty$ or Serrin $L^q_t L^p_x$ to bound the exponential martingale from below), or
* **`INSUFFICIENT`** (under subcritical energy bounds, where Novikov fails and exponential weights degenerate).
