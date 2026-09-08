# TP2-G6-C1: COMMON-MODE CANCELLATION THEOREM AND BOUNDARIES

## Work Package WP2: Common-Mode Translation Invariance

---

### 1. Executive Summary and Formulation

In Work Package WP4 and Benchmark BM-A2-04 of increment `TP2-G6-A2`, the primary physical obstruction preventing a single stochastic Lagrangian particle from sampling an Eulerian high-vorticity spike was the **convective sweeping deficit**: a spatially uniform or large-scale background velocity $U_n$ carries the single particle away from the localized spike core ($r_n = \nu^{1/2} M_n^{-1/2}$) over the turnover timescale $\tau_n = M_n^{-1}$.

This work package proves the **Common-Mode Cancellation Theorem**: in two-particle relative transport, any spatially homogeneous velocity component $U(t)$ cancels **identically and instantaneously** from the relative equations of motion under both synchronous (C-SYNC) and independent (C-IND) Brownian couplings.

We further delineate the exact mathematical boundary of this theorem: while it decisively eliminates the uniform sweeping obstruction, it does **not** control spatial shear, strain, pressure-induced non-local deformation, or deformation-vorticity decoupling.

---

### 2. Theorem Statement and Rigorous Proof

**Theorem 2.1 (Common-Mode Velocity Cancellation)**.
*Let $u(x, t)$ be an arbitrary divergence-free velocity field on $\mathbb{T}^3 \times [0, T]$ decomposed into a spatially uniform component $U(t)$ and a spatially varying fluctuation field $v(x, t)$:*
$$
u(x, t) = U(t) + v(x, t), \qquad U(t) = \int_{\mathbb{T}^3} u(x, t)\, dx, \quad \int_{\mathbb{T}^3} v(x, t)\, dx = 0.
$$
*Let $A_s^{(1)} = A_s(x)$ and $A_s^{(2)} = A_s(x+h)$ be two backward stochastic trajectories evolving under either Coupling C-SYNC or Coupling C-IND. Then:*
1. *The relative velocity difference satisfies:*
   $$
   u(A_s^{(2)}, s) - u(A_s^{(1)}, s) = v(A_s^{(2)}, s) - v(A_s^{(1)}, s) \quad \text{identically for all } s \in [0, t].
   $$
2. *Under Coupling C-SYNC, the relative separation vector $\delta A_s = A_s^{(2)} - A_s^{(1)}$ satisfies:*
   $$
   d(\delta A_s) = - \left[ v(A_s^{(2)}, s) - v(A_s^{(1)}, s) \right] ds, \qquad \delta A_t = h.
   $$
3. *Under Coupling C-IND, the relative separation vector satisfies:*
   $$
   d(\delta A_s) = - \left[ v(A_s^{(2)}, s) - v(A_s^{(1)}, s) \right] ds + \sqrt{4\nu}\, dB_s, \qquad \delta A_t = h.
   $$
*In both couplings, the uniform velocity field $U(t)$ is completely eliminated from the relative trajectory dynamics.*

*Proof*.
By direct algebraic substitution:
$$
\begin{aligned}
u(A_s^{(2)}, s) - u(A_s^{(1)}, s) &= \left[ U(s) + v(A_s^{(2)}, s) \right] - \left[ U(s) + v(A_s^{(1)}, s) \right] \\
&= (U(s) - U(s)) + \left[ v(A_s^{(2)}, s) - v(A_s^{(1)}, s) \right] \\
&= v(A_s^{(2)}, s) - v(A_s^{(1)}, s).
\end{aligned}
$$
Substituting this into the relative SDE for C-SYNC ($d(\delta A_s) = - [u(A_s^{(2)}, s) - u(A_s^{(1)}, s)] ds$) yields (2).
Substituting into the relative SDE for C-IND ($d(\delta A_s) = - [u(A_s^{(2)}, s) - u(A_s^{(1)}, s)] ds + \sqrt{4\nu} dB_s$) yields (3).
The cancellation is exact, pointwise in space, pathwise in $\Omega$, and valid for all $s \in [0, t]$. $\blacksquare$

---

### 3. Impact on the A2 Convective Sweeping Obstruction

In Benchmark BM-A2-04, a candidate blowup spike of amplitude $M_n \to \infty$ had:
- Core radius: $r_n = \nu^{1/2} M_n^{-1/2}$.
- Local turnover time: $\tau_n = M_n^{-1}$.
- Single-particle convective displacement: $\Delta x_{\text{conv}} \sim U_n \tau_n$.
When $U_n \gg \nu^{1/2} M_n^{1/2}$, the single particle was swept out of the core to distance $d_n \gg r_n$, driving the transition probability $\mathbb{P}(A_s(x) \in E_s(\alpha)) \to 0$ exponentially fast.

Under Theorem 2.1:
- The relative displacement $\delta A_s$ is entirely insensitive to $U_n$.
- Even if $U_n = 10^8$, the separation vector $\delta A_s$ evolves solely in response to the velocity increments $\delta v = v(A^{(2)}) - v(A^{(1)})$ and Brownian noise.
- **Direct Consequence**: The sweeping obstruction created by uniform background translation is **completely neutralized** in the relative coordinate frame.

---

### 4. Precise Epistemic Boundaries of What Common-Mode Cancellation Does NOT Solve

To maintain strict constitutional assurance, we catalogue what Theorem 2.1 **fails** to provide:

| Phenomenon | Mathematical Status under Theorem 2.1 | Why Common-Mode Cancellation Does NOT Resolve It |
|---|---|---|
| **Linear Shear Drift** | **UNRESOLVED** | If $v(x) = S x$, the relative drift is $\delta v = S \delta A_s$. If $\|S\| \sim M_n$, relative drift is of order $M_n |\delta A_s|$, which scales critically with turnover time. |
| **Hyperbolic Strain** | **UNRESOLVED** | In a hyperbolic saddle point $\nabla u = \operatorname{diag}(\lambda, \mu, -(\lambda+\mu))$, the relative separation explodes exponentially along unstable axes and collapses along stable axes. |
| **Deformation Decoupling** | **UNRESOLVED** | Benchmark BM-A2-05 operates via the deformation tensor $D_s$, which evolves as $dD_s = -D_s (\nabla u) ds$. Since $\nabla u = \nabla v$, $D_s$ is unaffected by $U(t)$ but remains fully subject to alignment-induced extinction inside vortex cores. |
| **Independent Noise Drift Coupling** | **UNRESOLVED** | In C-IND, while $U(t)$ cancels from the relative drift, the absolute positions $A_s^{(1)}$ and $A_s^{(2)}$ still depend on $U(t)$ via the base trajectories. The evaluation points for $\nabla v$ still track the base flow. |
| **Eulerian Coverage (Bridge B2)** | **UNRESOLVED** | Canceling $U(t)$ ensures the two particles maintain a scale-consistent separation $|\delta A_s| \sim |h|$, but does not guarantee that either particle hits the Eulerian superlevel set $E_s(\alpha)$. |

---

### 5. Epistemic Classification

- **Theorem Status**: **`MATHEMATICAL_IDENTITY`** / **`NON_CIRCULAR`**.
- **Bridge Impact**: Decisively eliminates the uniform translation component of `NS-OBS-018` (BM-A2-04).
- **Prohibition**: Common-mode cancellation must **never** be cited as a proof of Bridge $B_2$ closure or regularity. It is a necessary kinematic prerequisite, not a sufficient dynamical bound.
