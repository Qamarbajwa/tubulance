# TP2-G6-A1: Strain Eigenframe Depletion, Vieillefosse Dynamics, and Non-Local Pressure Mitigation

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A1 (Work Package 2)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Bridge:** `B1 — Non-Circular Xi Control`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. Exact Deviatoric Strain Transport Equation

Let $u(x, t)$ be a smooth divergence-free solution to 3D Navier–Stokes on $\mathbb{T}^3$. Differentiating the momentum equation $\partial_t u + (u \cdot \nabla)u = -\nabla p + \nu \Delta u$ yields the transport equation for the velocity gradient tensor $A = \nabla u$:
\[
(D_t - \nu \Delta) A = -A^2 - \nabla^2 p,
\]
where $D_t = \partial_t + u \cdot \nabla$ denotes the material derivative.

Decomposing $A$ into its symmetric rate-of-strain tensor $S$ and skew-symmetric rotation tensor $\Omega$:
\[
A = S + \Omega, \quad S_{ij} = \frac{1}{2}(\partial_j u_i + \partial_i u_j), \quad \Omega_{ij} = \frac{1}{2}(\partial_j u_i - \partial_i u_j).
\]
Expanding the quadratic term $A^2$:
\[
A^2 = (S + \Omega)^2 = S^2 + S\Omega + \Omega S + \Omega^2.
\]
Taking the symmetric part:
\[
\operatorname{Sym}(A^2) = S^2 + \Omega^2 + \frac{1}{2}(S\Omega + \Omega S + (S\Omega)^\top + (\Omega S)^\top).
\]
Since $S^\top = S$ and $\Omega^\top = -\Omega$, we have:
\[
(S\Omega)^\top = \Omega^\top S^\top = -\Omega S, \quad (\Omega S)^\top = S^\top \Omega^\top = -S\Omega.
\]
Thus, the mixed terms cancel identically:
\[
\frac{1}{2}\left( S\Omega + \Omega S - \Omega S - S\Omega \right) \equiv 0.
\]
We obtain the **exact symmetric strain transport equation**:
\[
(D_t - \nu \Delta) S = -(S^2 + \Omega^2) - \nabla^2 p.
\]
Both sides are trace-free since $\operatorname{tr}(S) = \nabla \cdot u = 0$ and $\operatorname{tr}(S^2 + \Omega^2) + \Delta p = Q_{\text{OW}} - Q_{\text{OW}} = 0$. Separating the tensor into deviatoric parts gives:
\[
\boxed{ (D_t - \nu \Delta) S = -(S^2 + \Omega^2)_{\text{dev}} - \Pi^{\text{dev}} },
\]
where:
- $(S^2 + \Omega^2)_{\text{dev}} = S^2 + \Omega^2 - \frac{1}{3}\left( \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2 \right) I$,
- $\Pi^{\text{dev}} = \nabla^2 p - \frac{1}{3}\Delta p \, I = \left( \mathcal{R} \otimes \mathcal{R} + \frac{1}{3} I \right) Q_{\text{OW}}$ is the non-local deviatoric pressure Hessian.

---

## 2. The Vieillefosse System and Restricted Euler Failure

In the local restricted Euler model (Vieillefosse 1982, 1984; Cantwell 1992), two major simplifications are introduced:
1. Viscous diffusion is neglected ($\nu = 0$).
2. The non-local deviatoric pressure Hessian is dropped ($\Pi^{\text{dev}} \approx 0$).

Under these assumptions, the local invariants of $A$:
\[
P = -\operatorname{tr}(A) = 0, \quad Q = -\frac{1}{2}\operatorname{tr}(A^2) = \frac{1}{4}|\omega|^2 - \frac{1}{2}\operatorname{tr}(S^2), \quad R = -\frac{1}{3}\operatorname{tr}(A^3) = -\frac{1}{3}\operatorname{tr}(S^3) - \frac{1}{4} \omega \cdot S \omega,
\]
satisfy the closed autonomous ODE system along fluid particle trajectories:
\[
\frac{dQ}{dt} = -3R, \quad \frac{dR}{dt} = \frac{2}{3} Q^2.
\]

### Proposition 2.1 (Finite-Time Blow-Up of Restricted Euler)
The restricted Euler system possesses the exact first integral:
\[
H(Q, R) = R^2 + \frac{4}{27} Q^3 = \text{const}.
\]
Particle trajectories are attracted to the **Vieillefosse tail** ($\Delta = 27 R^2 + 4 Q^3 = 0$ with $R > 0, Q < 0$), where:
\[
\frac{dR}{dt} = \frac{2}{3} \left( -\frac{27}{4} R^2 \right)^{2/3} = \frac{3}{2} R^{4/3}.
\]
Integration yields finite-time blow-up:
\[
R(t) = \frac{R(0)}{\left( 1 - \frac{1}{2} R(0)^{1/3} t \right)^3} \longrightarrow +\infty \quad \text{as } t \uparrow T_* = \frac{2}{R(0)^{1/3}} < \infty.
\]

In terms of the ordered strain eigenvalues $\alpha_1 \ge \alpha_2 \ge \alpha_3$ ($\alpha_1 + \alpha_2 + \alpha_3 = 0$):
- Along the Vieillefosse tail, $\alpha_1 = \alpha_2 = \alpha > 0$ and $\alpha_3 = -2\alpha < 0$.
- The two positive strain eigenvalues self-amplify quadratically without resistance: $\dot{\alpha} \sim \alpha^2$.

---

## 3. Dynamic Restoring Role of the Non-Local Pressure Hessian

In actual incompressible 3D Navier–Stokes flows, the non-local deviatoric pressure Hessian $\Pi^{\text{dev}}$ is **never zero**.

Projecting the strain transport equation onto the orthonormal eigenbasis $\{e_1, e_2, e_3\}$ of $S$ with $S e_i = \alpha_i e_i$:
\[
D_t \alpha_i = -\alpha_i^2 - (\Omega^2)_{ii} + \frac{1}{3} Q_{\text{OW}} - e_i \cdot \Pi^{\text{dev}} e_i + \nu e_i \cdot (\Delta S) e_i.
\]
Note that $(\Omega^2)_{ii} = -|\omega \times e_i|^2 / 4 \le 0$, representing vortex centrifugal effects.

### The Restoring Mechanism:
1. In regions of intense positive stretching ($\alpha_1, \alpha_2 > 0$), fluid elements undergo biaxial stretching and uniaxial compression ($\alpha_3 \ll 0$).
2. By the Poisson equation $-\Delta p = Q_{\text{OW}}$, if strain dominates rotation locally ($Q_{\text{OW}} > 0$), a pressure peak is created.
3. The non-local elliptic inversion produces an adverse pressure curvature along the stretching directions:
   \[
   e_1 \cdot \Pi^{\text{dev}} e_1 > 0, \quad e_2 \cdot \Pi^{\text{dev}} e_2 > 0.
   \]
4. In the equation for $\alpha_1$, the term $-e_1 \cdot \Pi^{\text{dev}} e_1$ has a **strictly negative sign**, opposing the quadratic self-amplification $-\alpha_1^2$.
5. This mechanism dynamically **depletes the intermediate and maximum strain eigenvalues**, shifting $\alpha_2$ toward negative or weakly positive values, which prevents the unconstrained Vieillefosse blow-up.

---

## 4. The Obstruction: Non-Local Phase Misalignment

Despite the restoring effect of $\Pi^{\text{dev}}$, does strain eigenframe depletion guarantee global smoothness for all smooth initial data?

### Theorem 2 (Phase Misalignment Obstruction)
Let $\Pi^{\text{dev}} = \mathcal{K} * Q_{\text{OW}}$, where $\mathcal{K}_{ij}(x) = \text{p.v.} \frac{3 x_i x_j - |x|^2 \delta_{ij}}{4\pi |x|^5}$ is the singular Calderón–Zygmund kernel on $\mathbb{R}^3$ (or its periodic summation on $\mathbb{T}^3$).

1. The value of $\Pi^{\text{dev}}(x, t)$ depends globally on the distribution of $Q_{\text{OW}}(y, t)$ over all $y \in \mathbb{T}^3$.
2. There exists no universal positive constant $c > 0$ such that:
   \[
   e_1(x) \cdot \Pi^{\text{dev}}(x) e_1(x) \ge c \, \alpha_1(x)^2 \quad \text{pointwise on } \mathbb{T}^3.
   \]
3. In particular, configurations exist where the spatial integral in the Calderón–Zygmund convolution undergoes phase cancellation, causing:
   \[
   e_1(x) \cdot \Pi^{\text{dev}}(x) e_1(x) \approx 0 \quad \text{or even } e_1(x) \cdot \Pi^{\text{dev}}(x) e_1(x) < 0
   \]
   at points of extreme local strain concentration.

### Conclusion for Bridge $B_1$:
Pressure–strain coupling exerts a powerful dissipative/depleting influence on the strain eigenframe, explaining why turbulent flows prefer $\alpha_2 \approx 0$ or weakly positive. However, because $\Pi^{\text{dev}}$ is non-local and lacks uniform pointwise coercivity against $\alpha_1^2$, **eigenframe depletion alone cannot close Bridge $B_1$ unconditionally**. It must be combined with non-circular integral estimates.
