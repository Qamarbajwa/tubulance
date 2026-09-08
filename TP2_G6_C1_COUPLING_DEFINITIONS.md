# TP2-G6-C1: TWO-PARTICLE BROWNIAN COUPLING DEFINITIONS AND DUALITY

## Work Package WP1: Exact Formulations of Synchronous and Independent Pair Couplings

---

### 1. Executive Summary and Epistemic Purpose

Under **Universal Governance Minimal v4.0.3** and **Mathematical Research Constitution v1.0.1**, this work package establishes the foundational mathematical definitions of two-particle stochastic Lagrangian transport for the 3D incompressible Navier–Stokes equations on the periodic flat torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$.

Increment `TP2-G6-A2` proved that single-particle stochastic Lagrangian history measures $\mu_s^x$ are structurally incapable of providing Eulerian high-vorticity coverage beyond level $B_2\text{-L1}$ (`NS-OBS-018`, `NEG-EV-037`), mandating the activation of **Programme TP2-G6-C: Two-Particle Dispersion and Stochastic Jet Route**.

Before formulating relative SDEs or evaluating spatial dispersion, the coupling between the Brownian noises driving the two backward trajectories must be rigorously specified. In multi-point stochastic Lagrangian flows, two distinct couplings are mathematically fundamental:
1. **Coupling C-SYNC (Synchronous Noise)**: The two particles share identical Brownian paths ($dW^{(1)} \equiv dW^{(2)}$).
2. **Coupling C-IND (Independent Noise)**: The two particles are driven by statistically independent Brownian paths ($dW^{(1)} \perp dW^{(2)}$).

This work package proves that C-SYNC and C-IND serve diametrically opposed mathematical functions: **C-SYNC governs spatial differentiability and stochastic jets**, while **C-IND governs pair dispersion and relative spatial diffusion**. Conflating these two couplings is an epistemic error strictly barred by this foundational framework.

---

### 2. Particle Trajectories and Geometric Setup

Let $u \in C([0, T]; C^1(\mathbb{T}^3))$ be a divergence-free velocity field satisfying $\operatorname{div} u = 0$. For a terminal time $t > 0$ and lookback time $s \in [0, t]$, we consider two backward particle trajectories starting at distinct initial points $x \in \mathbb{T}^3$ and $x + h \in \mathbb{T}^3$ ($h \in \mathbb{R}^3 \setminus \{0\}$):
$$
A_s^{(1)} = A_s(x), \qquad A_s^{(2)} = A_s(x+h).
$$
The relative separation vector is defined by:
$$
\delta A_s(x, h) = A_s^{(2)} - A_s^{(1)} = A_s(x+h) - A_s(x).
$$
On the torus $\mathbb{T}^3$, $\delta A_s$ is understood in the universal covering space $\mathbb{R}^3$ for initial separations $|h| < 1/2$, with canonical projection $\pi: \mathbb{R}^3 \to \mathbb{T}^3$.

---

### 3. Coupling C-SYNC — Synchronous Brownian Noise

#### 3.1 Definition
In the synchronous coupling, both particles are driven by the **exact same** 3D standard Brownian motion $W_s \in \mathbb{R}^3$:
$$
\begin{aligned}
dA_s^{(1)} &= - u(A_s^{(1)}, s)\, ds + \sqrt{2\nu}\, dW_s, \qquad &A_t^{(1)} = x, \\
dA_s^{(2)} &= - u(A_s^{(2)}, s)\, ds + \sqrt{2\nu}\, dW_s, \qquad &A_t^{(2)} = x+h.
\end{aligned}
$$

#### 3.2 Relative SDE under C-SYNC
Subtracting the two equations yields:
$$
\boxed{
d(\delta A_s) = - \left[ u(A_s^{(2)}, s) - u(A_s^{(1)}, s) \right] ds, \qquad \delta A_t = h.
}
$$
**Crucial Mathematical Identity**: The Brownian noise terms $\sqrt{2\nu}\, dW_s$ cancel **identically and pathwise**. 

#### 3.3 Functional Domain and Strengths of C-SYNC
1. **Differentiability of the Flow**: For smooth $u$, the backward map $x \mapsto A_s(x, \omega)$ is a $C^1$-diffeomorphism on $\mathbb{T}^3$ for almost every Brownian path $\omega \in \Omega$.
2. **Infinitesimal Jet Limit**: Because the noise cancels, the limit
   $$
   J_s(x) = \lim_{|h| \to 0} \frac{\delta A_s(x, h)}{h} = \nabla_x A_s(x)
   $$
   exists pathwise as a standard linear ODE for the Jacobian matrix.
3. **Volume Preservation**: The pathwise Jacobian satisfies $\det(J_s(x)) \equiv 1$ a.s., ensuring volume preservation of material volumes.

#### 3.4 Inherent Limitation of C-SYNC for Spatial Dispersion
Because relative diffusion is identically zero:
- If $u \equiv 0$ (pure diffusion), $d(\delta A_s) = 0 \implies \delta A_s \equiv h$. The two particles translate rigidly together; their separation remains static for all time.
- C-SYNC produces relative separation **only** through velocity gradients $\nabla u$. It provides **no intrinsic stochastic spreading** between particles to explore Eulerian high-vorticity regions independently.

---

### 4. Coupling C-IND — Independent Brownian Noise

#### 4.1 Definition
In the independent coupling, each particle is driven by its own independent 3D standard Brownian motion $W_s^{(1)}, W_s^{(2)}$ defined on a common product probability space $(\Omega \times \Omega, \mathcal{F}_1 \otimes \mathcal{F}_2, \mathbb{P}_1 \otimes \mathbb{P}_2)$:
$$
\begin{aligned}
dA_s^{(1)} &= - u(A_s^{(1)}, s)\, ds + \sqrt{2\nu}\, dW_s^{(1)}, \qquad &A_t^{(1)} = x, \\
dA_s^{(2)} &= - u(A_s^{(2)}, s)\, ds + \sqrt{2\nu}\, dW_s^{(2)}, \qquad &A_t^{(2)} = x+h,
\end{aligned}
$$
with cross-covariance $\mathbb{E}[dW_s^{(1)} \otimes dW_s^{(2)}] = 0$.

#### 4.2 Relative SDE under C-IND
Subtracting the two equations yields:
$$
d(\delta A_s) = - \left[ u(A_s^{(2)}, s) - u(A_s^{(1)}, s) \right] ds + \sqrt{2\nu} \left( dW_s^{(2)} - dW_s^{(1)} \right).
$$
We define the normalized relative Brownian motion:
$$
B_s = \frac{1}{\sqrt{2}} \left( W_s^{(2)} - W_s^{(1)} \right).
$$
Since $W_s^{(1)}$ and $W_s^{(2)}$ are independent standard Brownian motions, $B_s$ is a standard 3D Brownian motion:
$$
\mathbb{E}[B_s \otimes B_s] = \frac{1}{2} (s I + s I) = s I.
$$
Therefore:
$$
\sqrt{2\nu} \left( dW_s^{(2)} - dW_s^{(1)} \right) = \sqrt{2\nu} \cdot \sqrt{2}\, dB_s = \sqrt{4\nu}\, dB_s.
$$
The exact relative SDE under C-IND is:
$$
\boxed{
d(\delta A_s) = - \left[ u(A_s^{(2)}, s) - u(A_s^{(1)}, s) \right] ds + \sqrt{4\nu}\, dB_s, \qquad \delta A_t = h.
}
$$

#### 4.3 Functional Domain and Strengths of C-IND
1. **Effective Relative Diffusivity**: The relative diffusion coefficient is $2\nu_{\text{rel}} = 4\nu$ (twice the single-particle molecular diffusivity).
2. **Autonomous Spatial Spreading**: Even when $u \equiv 0$, the relative separation evolves as a Brownian motion:
   $$
   \mathbb{E}[|\delta A_s - h|^2] = 4\nu (t - s) \cdot 3 = 12\nu (t - s).
   $$
3. **Transition Density & Area Coverage**: The pair $(A_s^{(1)}, A_s^{(2)})$ possesses an absolute continuous joint transition density in $\mathbb{T}^3 \times \mathbb{T}^3$, allowing the particles to sample spatial regions independently.

#### 4.4 Inherent Limitation of C-IND for Tangent Flows / Jets
As $h \to 0$:
$$
\frac{\delta A_s}{h} = \frac{h - \int_s^t \delta u\, d\tau + \sqrt{4\nu} (B_t - B_s)}{h} = I - \int_s^t \frac{\delta u}{h} d\tau + \sqrt{4\nu} \frac{B_t - B_s}{h}.
$$
Because $|B_t - B_s| > 0$ almost surely, the quotient diverges as $|h|^{-1} \to \infty$. **C-IND does not admit a spatial derivative limit**. It cannot be used to define stochastic jets or deformation tensors.

---

### 5. Systematic Comparison and Epistemic Firewall

The table below establishes the strict separation between C-SYNC and C-IND:

| Mathematical Property | Coupling C-SYNC (Synchronous) | Coupling C-IND (Independent) |
|---|---|---|
| **Noise Structure** | $dW^{(1)} = dW^{(2)} = dW$ | $dW^{(1)} \perp dW^{(2)}$ |
| **Relative Noise Term** | $0$ (cancels pathwise) | $\sqrt{4\nu}\, dB_s$ (relative Brownian motion) |
| **Relative Diffusivity** | $\nu_{\text{rel}} = 0$ | $\nu_{\text{rel}} = 2\nu$ (total variance $4\nu \Delta t$) |
| **Flow Regularity** | Generates $C^1$ diffeomorphism flow | Generates pair Markov diffusion process |
| **Infinitesimal Limit ($h \to 0$)** | Exists pathwise: $J_s(x) = \nabla_x A_s(x)$ | **Diverges** almost surely ($\sim |h|^{-1}$) |
| **Stochastic Jet Capability** | **YES** (natural jet foundation) | **NO** (singular at zero separation) |
| **Independent Spatial Coverage** | **NO** (particles rigidly coupled when $\nabla u \to 0$) | **YES** (diffusive spreading of pair endpoints) |
| **Common-Mode Sweeping** | **CANCELS EXACTLY** ($U(t)$ removed) | **CANCELS EXACTLY** ($U(t)$ removed) |
| **Connection to $\Xi$ Framework** | Direct ($\Xi$ is normalized jet observable) | Indirect (requires expectation averaging) |

---

### 6. Constitutional Enforcement Rule

$$\boxed{\mathbf{RULE\ CP\text{-}1:\ NO\ HYBRID\ CONFLATION}}$$
Every assertion, theorem, SDE, and estimate in Programme `TP2-G6-C` must explicitly declare whether it operates under **`Coupling C-SYNC`** or **`Coupling C-IND`**. 
- Any proof claiming spatial differentiation or jet convergence under C-IND is **void**.
- Any proof claiming non-zero stochastic diffusion of separation under C-SYNC is **void**.
