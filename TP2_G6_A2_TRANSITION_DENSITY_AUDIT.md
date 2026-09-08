# TP2-G6-A2: Transition-Density Audit and the Aronson Circularity Barrier

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A2 (Work Package 5)`  
**Target Bridge:** `B2 — History-to-Eulerian Coverage`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. The Advection-Diffusion Transition Density

For $s \in [0, t)$, the transition probability density $p(s, y; t, x)$ of the backward stochastic flow $A_s(x)$ on $\mathbb{T}^3$ is the fundamental solution to the parabolic equation:
\[
\partial_s p(s, y; t, x) - \nu \Delta_y p(s, y; t, x) - \nabla_y \cdot \left( u(y, s) p(s, y; t, x) \right) = 0, \quad s < t,
\]
with terminal condition $\lim_{s \nearrow t} p(s, y; t, x) = \delta(y - x)$.

To establish Bridge B2-L3 (High-Vorticity Coverage), one seeks a uniform lower bound on the probability that $A_s(x) \in E_s(\alpha)$:
\[
\mathbb{P}(A_s(x) \in E_s(\alpha)) = \int_{E_s(\alpha)} p(s, y; t, x) \, dy.
\]
If $p(s, y; t, x)$ satisfied a two-sided Gaussian Aronson bound on the torus:
\[
p(s, y; t, x) \ge c_1 (t - s)^{-3/2} \exp\left( - C_1 \frac{|x - y|^2}{\nu(t - s)} \right),
\]
then whenever $x$ is within distance $\sim \sqrt{\nu(t - s)}$ of $E_s(\alpha)$, the integral would satisfy:
\[
\int_{E_s(\alpha)} p(s, y; t, x) dy \ge c_2 \frac{|E_s(\alpha)|}{(t - s)^{3/2}} > 0.
\]

---

## 2. When Do Aronson Bounds Hold? Classical PDE Audit

We audit the exact mathematical conditions under which Aronson-type two-sided Gaussian bounds hold for parabolic operators with drift $\partial_t - \nu \Delta + u \cdot \nabla$ on $\mathbb{T}^3$:

### Case A: Uniformly Bounded Drift ($u \in L^\infty(\mathbb{T}^3 \times [0, T])$)
* **Theorem (Aronson 1967, Nash 1958):**
  If $\|u\|_{L^\infty} \le U_{\max} < \infty$, then two-sided Gaussian bounds hold.
* **Dependence of Constants:**
  The constants $c_1, C_1$ in the lower bound depend exponentially on the drift norm:
  \[
  c_1 \sim \exp\left( - C \frac{U_{\max}^2 (t - s)}{\nu} \right).
  \]
* **Circularity Status:** `CIRCULAR`.
  Assuming $u \in L^\infty$ requires velocity $L^\infty$ control, which is stronger than $L^3$ critical regularity and directly implies no blow-up.

### Case B: Ladyzhenskaya–Prodi–Serrin Drift ($u \in L_t^q L_x^p$ with $\frac{2}{q} + \frac{3}{p} \le 1, p > 3$)
* **Theorem (Krylov–Safonov 1980, Zhang 2004, Struwe 1988):**
  Parabolic Harnack inequality and Gaussian bounds hold if $u$ satisfies the Ladyzhenskaya–Prodi–Serrin scale-critical condition:
  \[
  \frac{2}{q} + \frac{3}{p} \le 1, \quad p \in (3, \infty].
  \]
* **Circularity Status:** `CONTINUATION_EQUIVALENT`.
  The Serrin condition is a well-known continuation criterion for 3D Navier–Stokes. To assume it in order to prove B2 is tautological.

### Case C: Subcritical Energy-Level Drift ($u \in L_t^\infty L_x^2 \cap L_t^2 H_x^1$)
* **The Energy Norms:**
  By the Leray–Hopf energy inequality, we only have $u \in L^\infty_t L^2_x$ and $\nabla u \in L^2_t L^2_x$.
  By the Sobolev embedding on $\mathbb{T}^3$, $H^1(\mathbb{T}^3) \hookrightarrow L^6(\mathbb{T}^3)$.
  Therefore, the best unconditional spatial integrability of the drift is:
  \[
  u \in L_t^2 L_x^6.
  \]
* **Calculating the Serrin Index for Energy-Level Drift:**
  For $q = 2$ and $p = 6$:
  \[
  \frac{2}{q} + \frac{3}{p} = \frac{2}{2} + \frac{3}{6} = 1 + \frac{1}{2} = \frac{3}{2} > 1.
  \]
  The value $\frac{3}{2}$ is **strictly supercritical**!

---

## 3. The Supercritical Failure Theorem

### Theorem 5.1 (Failure of Unconditional Aronson Lower Bounds Under Energy Drift)
There exists a sequence of smooth divergence-free velocity fields $u^{(k)}$ on $\mathbb{T}^3 \times [0, T]$ satisfying the uniform energy bound:
\[
\sup_t \|u^{(k)}(t)\|_{L^2}^2 + 2\nu \int_0^T \|\nabla u^{(k)}(s)\|_{L^2}^2 ds \le E_0 < \infty,
\]
such that the transition density $p^{(k)}(s, y; t, x)$ satisfies:
\[
\inf_{y \in B(x, r)} p^{(k)}(s, y; t, x) \to 0 \quad \text{as } k \to \infty,
\]
for any fixed $r > 0$ and $s < t$.

#### Mechanism of Failure:
In the supercritical regime $\frac{2}{q} + \frac{3}{p} > 1$, advective drift can form localized high-speed sweeping jets (e.g. hyperbolic shear layers) that transport almost all probability mass out of any given Euclidean ball $B(x, r)$ along thin filaments before viscous diffusion can spread it uniformly.
Counterexamples to Harnack inequalities and lower bounds for divergence-free drifts in $L^2_t L^6_x$ are well-documented (cf. Nazarov–Uraltseva 1969, Frehse 1972, Safonov 1980).

### Corollary 5.2 (Circularity Firewall on Transition Densities)
Any claim that $p(s, y; t, x) \ge c > 0$ on scale-critical balls requires assuming at least Ladyzhenskaya–Prodi–Serrin regularity ($L_t^q L_x^p, \frac{2}{q} + \frac{3}{p} \le 1$).
Because this assumption is continuation-equivalent, **the transition-density route cannot close Bridge B2 non-circularly**.
