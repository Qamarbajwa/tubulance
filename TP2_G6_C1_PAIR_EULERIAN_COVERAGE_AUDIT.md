# TP2-G6-C1: PAIR-TO-EULERIAN COVERAGE AUDIT AND SEGMENT INTERSECTION

## Work Package WP11: Endpoint and Segment Coverage Analysis for Bridge B2

---

### 1. Purpose and Target Formulation

The overarching goal of Route `TP2-G6-C` is to determine whether relative two-particle transport can provide non-circular lower bounds on Eulerian high-vorticity regions $E_s(\alpha) = \{y \in \mathbb{T}^3 : |\omega(y, s)| \ge \alpha M(s)\}$, overcoming the single-particle ceiling proved in `TP2-G6-A2` (`B2_SINGLE_PARTICLE_NO_GO`).

In single-particle transport, the sampling object is a **0-dimensional point** $A_s(x) \in \mathbb{T}^3$. In two-particle transport, we obtain both:
1. **Endpoint Pair**: $\{A_s^{(1)}, A_s^{(2)}\} \subset \mathbb{T}^3$ (two 0D points).
2. **Material Line Segment**: $\Gamma_s(x, h) = [A_s^{(1)}, A_s^{(2)}] \subset \mathbb{T}^3$ (a 1-dimensional manifold).

This work package audits whether endpoint hitting or segment intersection can provide uniform, scale-invariant coverage of $E_s(\alpha)$ under subcritical energy bounds.

---

### 2. Formal Coverage Events and Functionals

Let $E_s(\alpha) = \{y \in \mathbb{T}^3 : |\omega(y, s)| \ge \alpha M(s)\}$ be the Eulerian superlevel set at lookback time $s$. By Chebyshev's inequality (WP1 of A2):
$$
|E_s(\alpha)| \le \frac{2\Omega_0}{\alpha^2 M(s)^2} \to 0 \quad \text{as } M(s) \to \infty.
$$

We define three ascending coverage criteria:

#### 2.1 Event 1: Endpoint Coverage ($\mathcal{H}_{\text{end}}$)
$$
\mathcal{H}_{\text{end}}(s) = \left\{ A_s^{(1)} \in E_s(\alpha) \ \lor \ A_s^{(2)} \in E_s(\alpha) \right\}.
$$
The endpoint coverage probability is:
$$
\mathbb{P}(\mathcal{H}_{\text{end}}(s)) = \mathbb{P}(A_s^{(1)} \in E_s) + \mathbb{P}(A_s^{(2)} \in E_s) - \mathbb{P}(A_s^{(1)} \in E_s \ \land \ A_s^{(2)} \in E_s).
$$
- If the two particles are separated by $|h| \gg r_n = \nu^{1/2} M_n^{-1/2}$, they sample independently under C-IND, doubling the hitting probability: $\mathbb{P}(\mathcal{H}_{\text{end}}) \approx 2 \mathbb{P}(A_s^{(1)} \in E_s)$.
- However, since $\mathbb{P}(A_s^{(1)} \in E_s) \to 0$ as $M_n \to \infty$ (by BM-A2-04), multiplying zero by 2 still yields zero:
  $$
  \lim_{M_n \to \infty} \mathbb{P}(\mathcal{H}_{\text{end}}(s)) = 0.
  $$
- **Finding**: Merely adding a second endpoint does not resolve the measure deficit.

#### 2.2 Event 2: Material Segment Intersection ($\mathcal{H}_{\text{seg}}$)
Under Coupling C-SYNC, the straight line segment in universal cover $\mathbb{R}^3$:
$$
\Gamma_s(x, h) = \left\{ (1 - \theta) A_s^{(1)} + \theta A_s^{(2)} : \theta \in [0, 1] \right\}
$$
is a 1D material curve of length $L_s = |\delta A_s|$.
The segment intersection event is:
$$
\mathcal{H}_{\text{seg}}(s) = \left\{ \Gamma_s(x, h) \cap E_s(\alpha) \ne \emptyset \right\}.
$$
A 1D curve has a much larger geometric cross-section than a 0D point. By the Poincaré kinematic formula in integral geometry, the probability that a random segment of length $L_s$ intersects a convex core of radius $r_n$ scales with the **surface area / cross-section**:
$$
\text{Cross-Section} \sim r_n^2 \cdot L_s \sim \nu M_n^{-1} L_s.
$$

#### 2.3 Functional 3: Pair Occupation Functional ($\mathcal{O}_E$)
$$
\mathcal{O}_E(x, h) = \int_0^t \mathbf{1}_{\left\{ \Gamma_s(x, h) \cap E_s(\alpha) \ne \emptyset \right\}}\, ds.
$$
Measures the total lookback residence time during which the material segment straddles or touches the high-vorticity core.

---

### 3. Obstruction Analysis of Segment Coverage

Can $\mathbb{P}(\mathcal{H}_{\text{seg}}) \ge c > 0$ be proved unconditionally?
We audit the two regimes of initial separation $|h|$:

#### Regime A: Sub-Viscous Initial Separation ($|h| \le r_n$)
- When $|h| \le r_n = \nu^{1/2} M_n^{-1/2}$, the segment length is smaller than the core radius.
- While common-mode velocity $U(t)$ cancels (WP2), the **velocity gradient difference** across the core is:
  $$
  |\delta u| \sim \|\nabla u\|_{L^\infty} |\delta A_s| \sim M_n r_n = \nu^{1/2} M_n^{1/2}.
  $$
- Over the turnover timescale $\tau_n = M_n^{-1}$, the segment is subject to intense local hyperbolic strain:
  $$
  \frac{d}{ds} \log |\delta A_s| \sim - e_s^T S e_s \sim \pm M_n.
  $$
- Along the compressing axis, the segment collapses: $|\delta A_s| \sim |h| e^{-M_n \tau_n} = |h| e^{-1}$.
- Along the expanding axis, the segment stretches and is **expelled along the unstable manifold** outside the core radius $r_n$.
- Most decisively: if the center of the segment starts at distance $d_n > r_n$, the segment never touches the core, and since the core volume shrinks as $M_n^{-3/2}$, the Lebesgue probability of starting within $r_n$ of the core vanishes as $M_n^{-3/2} \to 0$.

#### Regime B: Macroscopic Initial Separation ($|h| \gg r_n$)
- When $|h| \sim 1$ (macroscopic), the segment length is $L_s \sim 1 \gg r_n$.
- A long segment easily intersects small localized sets on $\mathbb{T}^3$.
- **However, Scale-Critical Resolution is Lost**:
  Along a segment of length $\mathcal{O}(1)$, the path-averaged gradient:
  $$
  \mathcal{S}_s = \int_0^1 \nabla u(A_s^{(1)} + \theta \delta A_s, s)\, d\theta
  $$
  is dominated by the low-vorticity background ($|\nabla u| \sim 1$). The high-vorticity core of size $r_n \sim M_n^{-1/2}$ occupies only a fraction:
  $$
  \Delta \theta = \frac{r_n}{|h|} \sim M_n^{-1/2} \to 0.
  $$
  The core's contribution to the path integral is at most:
  $$
  \int_{\text{core}} \nabla u\, d\theta \sim M_n \times M_n^{-1/2} = M_n^{1/2},
  $$
  which is diluted across the unit interval. The segment does not isolate the local core dynamics.

---

### 4. Bridge B2 Status under Two-Particle Transport

| Coverage Concept | Geometric Manifold | Scaling with Core $M_n \to \infty$ | Resolves Bridge B2 Unconditionally? |
|---|---|---|---|
| **Single-Particle Point** | 0D point | Vanishes as $M_n^{-3/2}$ + convective expulsion | **NO** (Proved in A2: Ceiling at B2-L1) |
| **Two-Particle Endpoints** | Two 0D points | Vanishes as $2 \times M_n^{-3/2}$ | **NO** (Same scaling as single particle) |
| **Material Segment ($|h| \le r_n$)** | 1D curve (local) | Strained and expelled along unstable manifold | **NO** (Requires initial location in core) |
| **Material Segment ($|h| \sim 1$)** | 1D curve (global) | Intersects, but dilutes core gradient to $M_n^{1/2}$ | **NO** (Loses scale-critical isolation) |

**Foundational Conclusion for Increment C1**:
The two-particle framework creates a mathematically richer geometric structure (segment intersection $\mathcal{H}_{\text{seg}}$), but **does not by itself prove Bridge Level B2-L3 or B2-L4**. Full Eulerian coverage requires quantitative dispersion estimates over an ensemble of pairs, which forms the objective of successor increment `TP2-G6-C2`.
