# TP2-G6-C1: STOCHASTIC JET LIMIT AND DEFORMATION RECONCILIATION

## Work Package WP4: The Infinitesimal Separation Limit and Canonical Jet Tensor

---

### 1. Purpose and Notation Reconciliation

This work package investigates the **infinitesimal limit** of two-particle relative dispersion:
$$
h \to 0, \qquad h \in \mathbb{R}^3 \setminus \{0\},
$$
establishing the rigorous connection between the finite-separation pair difference $\delta A_s(x, h)$ and the **stochastic jet** (the spatial derivative of the stochastic flow map).

A critical governance requirement for increment `TP2-G6-C1` is to **reconcile repository notation** between the stochastic flow derivative $J_s(x) = \nabla_x A_s(x)$ and the canonical project deformation tensor $D_s(x)$, eliminating competing definitions across the codebase.

---

### 2. The Canonical Repository Convention: $D_s \equiv J_s$

Throughout the `NS-TRAJECTORY-PERSISTENCE-2` programme (from TP2-G4 through TP2-G6-A2), the deformation tensor $D_s(x)$ is defined as the **spatial gradient matrix of the backward stochastic flow map**:
$$
\boxed{
D_s(x) \equiv J_s(x) = \nabla_x A_s(x) \in \mathbb{R}^{3 \times 3}.
}
$$
In index notation, with $A_s(x) = (A_s^1, A_s^2, A_s^3)^T$ and $x = (x_1, x_2, x_3)^T$:
$$
(D_s)_{ij}(x) = (J_s)_{ij}(x) = \frac{\partial A_s^i}{\partial x_j}(x).
$$

#### 2.1 Backward Evolution Equation
Recall the backward SDE for $A_s(x)$ with terminal condition at $s = t$:
$$
A_s(x) = x - \int_s^t u(A_\tau(x), \tau)\, d\tau + \sqrt{2\nu} (W_t - W_s).
$$
Differentiating with respect to the initial spatial coordinate $x_j$:
$$
\frac{\partial A_s^i}{\partial x_j} = \delta_{ij} - \int_s^t \frac{\partial u_i}{\partial y_k}(A_\tau(x), \tau) \frac{\partial A_\tau^k}{\partial x_j}\, d\tau.
$$
Differentiating with respect to lookback time $s$ (backwards from $t$ to $0$):
$$
\boxed{
\frac{d}{ds} D_s(x) = - \nabla u(A_s(x), s)\, D_s(x), \qquad D_t(x) = I.
}
$$
Here $(\nabla u)_{ik} = \frac{\partial u_i}{\partial y_k}$, so the velocity gradient matrix multiplies the deformation tensor on the **left**.

#### 2.2 Determinant Invariance
Taking the trace and using Jacobi's formula for the derivative of the determinant:
$$
\frac{d}{ds} \det(D_s) = \operatorname{tr}\left( \operatorname{adj}(D_s) \frac{d D_s}{ds} \right) = - \operatorname{tr}(\nabla u) \det(D_s) = - (\operatorname{div} u) \det(D_s) = 0.
$$
Since $D_t = I \implies \det(D_t) = 1$, we have:
$$
\boxed{
\det(D_s(x)) \equiv 1 \quad \text{a.s. for all } s \in [0, t], \ x \in \mathbb{T}^3.
}
$$

---

### 3. Convergence of Synchronous Pair SDE to the Stochastic Jet

Under **Coupling C-SYNC**, the relative separation satisfies (WP3):
$$
\frac{d}{ds} \delta A_s(x, h) = - \mathcal{S}_s(x, h)\, \delta A_s(x, h), \qquad \delta A_t = h,
$$
where $\mathcal{S}_s(x, h) = \int_0^1 \nabla u(A_s^{(1)} + \theta \delta A_s, s) d\theta$.

**Theorem 4.1 (Stochastic Jet Limit of C-SYNC)**.
*Let $u \in C([0, T]; C^2(\mathbb{T}^3))$. Then for every $x \in \mathbb{T}^3$ and almost every Brownian path $\omega \in \Omega$, the difference quotient converges uniformly on $[0, t]$:*
$$
\lim_{|h| \to 0} \sup_{s \in [0, t]} \left\| \frac{\delta A_s(x, h)}{h} - D_s(x) \right\| = 0.
$$

*Proof*.
Define the matrix difference quotient $Q_s(h) \in \mathbb{R}^{3 \times 3}$ whose $j$-th column is $\frac{\delta A_s(x, |h| e_j)}{|h|}$.
Then $Q_t(h) = I$. By WP3, $Q_s(h)$ satisfies:
$$
\frac{d}{ds} Q_s(h) = - \mathcal{S}_s(x, h)\, Q_s(h), \qquad Q_t(h) = I.
$$
As $|h| \to 0$, the segment $A_s^{(1)} + \theta \delta A_s \to A_s(x)$ uniformly because $\sup_{s \in [0, t]} |\delta A_s| \le |h| \exp(\int_0^t \|\nabla u\|_{L^\infty} d\tau) \to 0$.
Since $\nabla u$ is uniformly continuous on $\mathbb{T}^3 \times [0, t]$:
$$
\lim_{|h| \to 0} \sup_{s \in [0, t]} \|\mathcal{S}_s(x, h) - \nabla u(A_s(x), s)\| = 0.
$$
By standard continuous dependence of ODE solutions on coefficients, $Q_s(h) \to D_s(x)$ uniformly on $[0, t]$. $\blacksquare$

---

### 4. Non-Existence of Stochastic Jet Limit for Independent Coupling C-IND

Under **Coupling C-IND**, the relative separation satisfies (WP3):
$$
\delta A_s(x, h) = h - \int_s^t \mathcal{S}_\tau(x, h) \delta A_\tau(x, h)\, d\tau + \sqrt{4\nu} (B_t - B_s).
$$
Dividing by $|h|$:
$$
\frac{\delta A_s(x, h)}{|h|} = \frac{h}{|h|} - \int_s^t \mathcal{S}_\tau \frac{\delta A_\tau}{|h|}\, d\tau + \frac{\sqrt{4\nu} (B_t - B_s)}{|h|}.
$$
For any $s < t$, the Brownian increment $B_t - B_s$ is non-zero almost surely ($\mathbb{P}(B_t - B_s = 0) = 0$).
Therefore:
$$
\lim_{|h| \to 0} \left\| \frac{\sqrt{4\nu} (B_t - B_s)}{|h|} \right\| = \infty \quad \text{a.s.}
$$
**Conclusion**: Coupling C-IND **does not admit an infinitesimal derivative limit**. The difference quotient explodes as $|h|^{-1}$. C-IND cannot generate tangent vectors or stochastic jets.

---

### 5. Second-Order Stochastic Jet: $\nabla_x^2 A_s$

For smooth flows ($u \in C^2$), the second spatial derivative of the backward flow $H_s(x) = \nabla_x^2 A_s(x) \in \mathbb{R}^{3 \times 3 \times 3}$ satisfies:
$$
(H_s)_{ijk} = \frac{\partial^2 A_s^i}{\partial x_j \partial x_k}.
$$
Differentiating the first-order ODE $\frac{d}{ds} D_s = - (\nabla u) D_s$ with respect to $x_k$:
$$
\boxed{
\frac{d}{ds} (H_s)_{ijk} = - \frac{\partial u_i}{\partial y_m} (H_s)_{mjk} - \frac{\partial^2 u_i}{\partial y_m \partial y_n} (D_s)_{mj} (D_s)_{nk}, \qquad H_t(x) = 0.
}
$$
- The first term represents linear advection of curvature by the velocity gradient.
- The second term is the **nonlinear curvature source**: the velocity Hessian $\nabla^2 u$ contracted with two copies of the deformation tensor $D_s$.
- This second-order jet provides the exact mathematical representation of how spatial strain gradients bend and stretch material segments.

---

### 6. Summary of Reconciled Mathematical Objects

| Mathematical Object | Notation | Exact Definition | Governing Coupling |
|---|---|---|---|
| **Backward Flow** | $A_s(x)$ | $x - \int_s^t u(A_\tau) d\tau + \sqrt{2\nu} (W_t - W_s)$ | Base single trajectory |
| **Relative Separation** | $\delta A_s(x, h)$ | $A_s(x+h) - A_s(x)$ | C-SYNC or C-IND |
| **Path-Averaged Gradient** | $\mathcal{S}_s(x, h)$ | $\int_0^1 \nabla u(A_s^{(1)} + \theta \delta A_s) d\theta$ | Pair segment |
| **First-Order Jet (Deformation)** | $D_s(x) \equiv J_s(x)$ | $\nabla_x A_s(x)$, $\frac{d}{ds} D_s = - (\nabla u) D_s$ | C-SYNC ($h \to 0$) |
| **Second-Order Jet (Hessian)** | $H_s(x) \equiv \nabla^2 A_s(x)$ | $\nabla_x^2 A_s(x)$, source $- (\nabla^2 u)(D_s, D_s)$ | C-SYNC ($h \to 0$) |
| **Relative Pair Diffusion** | $\sqrt{4\nu} B_s$ | $\sqrt{2\nu} (W_s^{(2)} - W_s^{(1)})$ | C-IND ($|h| > 0$ only) |
