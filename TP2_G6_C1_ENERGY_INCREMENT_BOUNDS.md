# TP2-G6-C1: ENERGY-LEVEL VELOCITY INCREMENT BOUNDS AND MAXIMAL OPERATORS

## Work Package WP6: Sobolev Increments and Pathwise Control Limits

---

### 1. Executive Summary

A central premise of Programme `TP2-G6-C` is that while the single-particle velocity $u(x, t)$ is poorly controlled under subcritical energy bounds ($u \in L^\infty_t L^2_x \cap L^2_t H^1_x$), the **velocity increment** $\delta_h u(x) = u(x+h) - u(x)$ possesses an intrinsic scaling factor $|h|$ governed by the gradient $\nabla u$.

This work package investigates whether modern harmonic analysis estimates—specifically the **Hajłasz–Sobolev maximal inequality**:
$$
|u(x+h) - u(x)| \le C |h| \left( M|\nabla u|(x) + M|\nabla u|(x+h) \right),
$$
can provide useful probabilistic control over the relative trajectory SDE without circular regularity assumptions.

We prove that while this estimate is mathematically rigorous and non-circular, it yields **only weak spatial and time-averaged bounds**. Attempting to turn it into pathwise or expectation bounds along stochastic trajectories encounters the exact same push-forward measure gap identified in `NS-OBS-017` and `NS-OBS-018`.

---

### 2. The Hajłasz–Sobolev Maximal Inequality

**Theorem 6.1 (Pointwise Increment Bound via Maximal Functions)**.
*Let $u \in H^1(\mathbb{T}^3)$. Then for almost every $x, y \in \mathbb{T}^3$:*
$$
|u(x) - u(y)| \le C\, |x - y| \left( M|\nabla u|(x) + M|\nabla u|(y) \right),
$$
*where $M$ is the Hardy–Littlewood maximal operator on $\mathbb{T}^3$:*
$$
Mf(x) = \sup_{r > 0} \frac{1}{|B(x, r)|} \int_{B(x, r)} |f(z)|\, dz,
$$
*and $C > 0$ is a universal dimensional constant.*

*Proof*.
By the classical theorem of Hajłasz (1996) and Bojarski (1988) on Sobolev spaces: for any locally integrable function $u$ with $\nabla u \in L^1_{\text{loc}}$, for Lebesgue-almost-every pair $(x, y)$, the line segment average satisfies:
$$
\int_0^1 |\nabla u(x + \theta(y - x))|\, d\theta \le C \left( M|\nabla u|(x) + M|\nabla u|(y) \right).
$$
Multiplying by $|x - y|$ and applying the fundamental theorem of calculus yields the inequality. $\blacksquare$

---

### 3. Energy-Level Integrability Bounds

By the Hardy–Littlewood maximal theorem:
$$
\|Mf\|_{L^p(\mathbb{T}^3)} \le C_p \|f\|_{L^p(\mathbb{T}^3)} \quad \text{for all } p \in (1, \infty].
$$
For $p = 2$, since $\nabla u \in L^2_t L^2_x(\mathbb{T}^3)$ with $\int_0^T \|\nabla u(t)\|_{L^2}^2 dt \le \frac{\mathcal{E}_0}{2\nu}$:
$$
\int_0^T \|M|\nabla u|(\cdot, t)\|_{L^2(\mathbb{T}^3)}^2 dt \le C_2^2 \int_0^T \|\nabla u(t)\|_{L^2}^2 dt \le \frac{C_2^2 \mathcal{E}_0}{2\nu} < \infty.
$$
Therefore, the function:
$$
g(x, t) = M|\nabla u|(x, t)
$$
belongs unconditionally to $L^2([0, T]; L^2(\mathbb{T}^3))$.

---

### 4. Application to Stochastic Backward Trajectories

Let $A_s^{(1)} = A_s(x)$ and $A_s^{(2)} = A_s(x+h)$. Applying Theorem 6.1:
$$
|\delta u_s| = |u(A_s^{(2)}, s) - u(A_s^{(1)}, s)| \le C |\delta A_s| \left( M|\nabla u|(A_s^{(1)}, s) + M|\nabla u|(A_s^{(2)}, s) \right).
$$
Substituting into the relative SDE for C-SYNC:
$$
\left| \frac{d}{ds} \log |\delta A_s| \right| \le \frac{|\delta u_s|}{|\delta A_s|} \le C \left( M|\nabla u|(A_s^{(1)}, s) + M|\nabla u|(A_s^{(2)}, s) \right).
$$
Integrating backwards from $t$ to $s$:
$$
|\delta A_s| \le |h| \exp\left( C \int_s^t \left[ M|\nabla u|(A_\tau^{(1)}, \tau) + M|\nabla u|(A_\tau^{(2)}, \tau) \right] d\tau \right).
$$

---

### 5. Why Maximal Bounds Fail to Yield Pathwise Regularity

The expression above establishes an exponential growth bound for pair separation. However, to utilize this bound without circularity, one must bound:
$$
\mathbb{E}\left[ \exp\left( C \int_s^t M|\nabla u|(A_\tau(x), \tau)\, d\tau \right) \right].
$$

#### 5.1 The Integrability Deficit
- By Khasminskii's lemma and Portenko's theorem for diffusion processes, bounding the exponential moment $\mathbb{E}[\exp(\int_0^t V(A_\tau, \tau) d\tau)]$ requires $V \in L^q_t L^p_x$ with:
  $$
  \frac{2}{q} + \frac{d}{p} < 1 \quad \text{or at least } \le 1.
  $$
- In $d = 3$, $M|\nabla u|$ has the exact same integrability as $\nabla u$, which is $L^2_t L^2_x$.
- The Serrin index of $M|\nabla u|$ is:
  $$
  \frac{2}{q} + \frac{3}{p} = \frac{2}{2} + \frac{3}{2} = 1 + 1.5 = 2.5 \gg 1.
  $$
- **The Scaling Gap**: The energy bound misses the critical threshold for exponential integrability by $\Delta = 1.5$ derivatives!
- Consequently, along almost every Brownian path, the integral $\int_0^t M|\nabla u|(A_\tau, \tau) d\tau$ can be arbitrarily large or infinite in the presence of candidate singular concentrations, permitting $|\delta A_s|$ to explode or collapse.

#### 5.2 The Push-Forward Measure Trap
To compute the expectation of the maximal function directly:
$$
\mathbb{E}\left[ M|\nabla u|(A_s(x), s) \right] = \int_{\mathbb{T}^3} M|\nabla u|(y, s)\, p(s, y; t, x)\, dy.
$$
- Even though $(A_s)_\# dx = dx$ on spatial average (Level B2-L1), the transition density $p(s, y; t, x)$ for a fixed starting point $x$ satisfies no uniform $L^2$ or $L^\infty$ bounds under energy drift (WP5 of A2).
- If $M|\nabla u|$ concentrates in a small ball of radius $r_n = \nu^{1/2} M_n^{-1/2}$, the expectation cannot be bounded by energy alone without assuming higher regularity.

---

### 6. Epistemic Summary

| Quantity | A Priori Status from Energy | Usefulness for Pathwise Control | Failure Mechanism |
|---|---|---|---|
| **$S_2(h) = \|\delta_h u\|_{L^2}^2$** | Bounded: $\le |h|^2 \|\nabla u\|_{L^2}^2$ | High for spatial averages; zero for pathwise | Lebesgue average $\ne$ stochastic expectation |
| **$M|\nabla u| \in L^2_t L^2_x$** | Bounded unconditionally | Moderate for weak estimates | Serrin index $2.5 > 1$ (supercritical deficit $1.5$) |
| **Pathwise $|\delta A_s| / |h|$** | Uncontrolled | Fails to bound without BKM | Exponential of supercritical process diverges |

**Verdict**: Increment bounds via maximal operators provide a rigorous structural explanation for why relative velocities scale with $|h|$, but **cannot close the regularity problem pathwise under subcritical energy bounds**.
