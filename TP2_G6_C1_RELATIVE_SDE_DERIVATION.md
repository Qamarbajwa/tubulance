# TP2-G6-C1: EXACT RELATIVE SDE DERIVATION VIA PATH INTEGRALS

## Work Package WP3: Path-Averaged Velocity Gradient Representation

---

### 1. Purpose and Mathematical Setting

This work package derives the **exact, unlinearized relative equations of motion** for the separation vector $\delta A_s = A_s^{(2)} - A_s^{(1)}$ between two stochastic Lagrangian backward trajectories on $\mathbb{T}^3$.

By using the fundamental theorem of calculus along the straight segment connecting the two particles, the non-linear difference $u(A_s^{(2)}) - u(A_s^{(1)})$ is expressed exactly as a linear action of a path-averaged gradient matrix $\mathcal{S}_s$ on $\delta A_s$. This formulation is valid prior to any infinitesimal approximation ($h \to 0$), establishing the rigorous foundation for both finite-separation pair dispersion and the infinitesimal stochastic jet limit.

---

### 2. Path-Averaged Gradient Operator $\mathcal{S}_s$

#### 2.1 Fundamental Theorem of Calculus Identity
Let $u(\cdot, s) \in C^1(\mathbb{T}^3; \mathbb{R}^3)$ be $\mathbb{Z}^3$-periodic. For any two points $y_1, y_2 \in \mathbb{R}^3$, the straight line path parameterized by $\theta \in [0, 1]$ is:
$$
\gamma(\theta) = y_1 + \theta (y_2 - y_1) = (1 - \theta) y_1 + \theta y_2.
$$
By the chain rule:
$$
\frac{d}{d\theta} u(\gamma(\theta), s) = \nabla u(\gamma(\theta), s) \cdot (y_2 - y_1).
$$
Integrating from $\theta = 0$ to $\theta = 1$:
$$
u(y_2, s) - u(y_1, s) = \left[ \int_0^1 \nabla u(y_1 + \theta(y_2 - y_1), s)\, d\theta \right] (y_2 - y_1).
$$

#### 2.2 Definition of $\mathcal{S}_s$ Along Backward Trajectories
Applying this identity to the backward trajectories $y_1 = A_s^{(1)}$ and $y_2 = A_s^{(2)} = A_s^{(1)} + \delta A_s$:
$$
\boxed{
\mathcal{S}_s(x, h) = \int_0^1 \nabla u\left( A_s^{(1)} + \theta\, \delta A_s, s \right) d\theta \in \mathbb{R}^{3 \times 3}.
}
$$
In component notation with index convention $(\nabla u)_{ij} = \frac{\partial u_i}{\partial x_j}$:
$$
(\mathcal{S}_s)_{ij} = \int_0^1 \frac{\partial u_i}{\partial x_j}\left( A_s^{(1)}(x) + \theta\, \delta A_s(x, h), s \right) d\theta.
$$
Because $\operatorname{div} u = \operatorname{tr}(\nabla u) = 0$ everywhere, the trace of $\mathcal{S}_s$ vanishes identically:
$$
\operatorname{tr}(\mathcal{S}_s) = \int_0^1 \operatorname{tr}\left(\nabla u(A_s^{(1)} + \theta\, \delta A_s, s)\right) d\theta = \int_0^1 0\, d\theta = 0.
$$
Thus, $\mathcal{S}_s \in \mathfrak{sl}(3, \mathbb{R})$ is a **traceless matrix** for every path and every lookback time $s$.

---

### 3. Exact Relative SDEs

#### 3.1 Synchronous Coupling (C-SYNC)
Under Coupling C-SYNC, the Brownian noises cancel pathwise (WP1), yielding:
$$
\boxed{
\frac{d}{ds} \delta A_s = - \mathcal{S}_s(x, h)\, \delta A_s, \qquad \delta A_t = h.
}
$$
This is an **exact, non-autonomous linear system** for $\delta A_s$, where the coefficient matrix $\mathcal{S}_s$ depends non-linearly on the trajectory segment.

#### 3.2 Independent Coupling (C-IND)
Under Coupling C-IND, relative Brownian diffusion is present (WP1):
$$
\boxed{
d(\delta A_s) = - \mathcal{S}_s(x, h)\, \delta A_s\, ds + \sqrt{4\nu}\, dB_s, \qquad \delta A_t = h,
}
$$
where $B_s = \frac{1}{\sqrt{2}}(W_s^{(2)} - W_s^{(1)})$ is a standard 3D Brownian motion.

---

### 4. Decomposition into Symmetric Strain and Antisymmetric Vorticity

The velocity gradient decomposes canonically into rate-of-strain $S = \frac{1}{2}(\nabla u + (\nabla u)^T)$ and vorticity tensor $\Omega = \frac{1}{2}(\nabla u - (\nabla u)^T)$:
$$
\nabla u = S + \Omega, \qquad \Omega_{ij} = - \frac{1}{2} \epsilon_{ijk} \omega_k.
$$
Applying this decomposition to the path-averaged matrix:
$$
\mathcal{S}_s = \bar{S}_s + \bar{\Omega}_s,
$$
where:
$$
\bar{S}_s = \int_0^1 S\left( A_s^{(1)} + \theta \delta A_s, s \right) d\theta, \qquad \bar{\Omega}_s = \int_0^1 \Omega\left( A_s^{(1)} + \theta \delta A_s, s \right) d\theta.
$$
- $\bar{S}_s$ is symmetric and traceless ($\operatorname{tr} \bar{S}_s = 0$), governing **relative stretching and compression**.
- $\bar{\Omega}_s$ is skew-symmetric ($\bar{\Omega}_s^T = - \bar{\Omega}_s$), governing **relative rigid rotation**.

---

### 5. Torus Topology, Universal Cover, and Stopping Times

#### 5.1 Universal Covering Space Formulation
On the flat torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$, straight line segments are well-defined only locally. If $|\delta A_s| \ge 1/2$, the straight segment in $\mathbb{R}^3$ may wrap around the fundamental domain, admitting multiple non-homotopic geodesics on $\mathbb{T}^3$.
To eliminate topological ambiguity:
1. Lift the backward SDEs to the universal covering space $\mathbb{R}^3$, where $u(x, t)$ is periodic: $u(x + k, t) = u(x, t)$ for all $k \in \mathbb{Z}^3$.
2. In $\mathbb{R}^3$, $\delta A_s \in \mathbb{R}^3$ is uniquely defined for all $s \in [0, t]$.

#### 5.2 Stopping Times
We define two canonical stopping times for relative transport:
1. **Separation Wrap-Around Time $\tau_{\text{wrap}}$**:
   $$
   \tau_{\text{wrap}} = \inf \left\{ s \in [0, t] : |\delta A_s| \ge \frac{1}{2} \right\}.
   $$
   For $s \in [\tau_{\text{wrap}}, t]$, $\delta A_s$ remains within the injectivity radius of $\mathbb{T}^3$.
2. **Collision Time $\tau_0$**:
   $$
   \tau_0 = \inf \left\{ s \in [0, t] : |\delta A_s| = 0 \right\}.
   $$
   This represents the first instant of particle collision.

---

### 6. Epistemic Assessment

- **Identity Validity**: Exact for all $u \in C^1$.
- **Trace Invariance**: $\operatorname{tr}(\mathcal{S}_s) \equiv 0$ strictly preserves Liouville's theorem for the relative system.
- **Foundational Status**: Forms the rigorous mathematical bridge between finite-displacement pair dispersion ($|h| > 0$) and the infinitesimal stochastic jet ($|h| \to 0$).
