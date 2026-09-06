# TP2-G6-A1: Pressure Poisson Balance, Enstrophy Equipartition, and Non-Local Hessian

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A1 (Work Package 1)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Bridge:** `B1 — Non-Circular Xi Control`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. The Exact Pressure Poisson System on $\mathbb{T}^3$

Let $u(x, t)$ be a smooth, divergence-free velocity field satisfying the 3D incompressible Navier–Stokes equations on the periodic torus $\mathbb{T}^3$:
\[
\partial_t u + (u \cdot \nabla)u = -\nabla p + \nu \Delta u, \quad \nabla \cdot u = 0.
\]
Taking the divergence of the momentum equation and applying $\nabla \cdot u = 0$ yields:
\[
\nabla \cdot ((u \cdot \nabla)u) = \partial_i (u_j \partial_j u_i) = (\partial_i u_j)(\partial_j u_i) = \operatorname{tr}((\nabla u)^2).
\]
Decomposing the velocity gradient tensor $A = \nabla u$ into its symmetric strain $S$ and skew-symmetric rotation $\Omega$:
\[
A = S + \Omega, \quad S = \frac{1}{2}(A + A^\top), \quad \Omega = \frac{1}{2}(A - A^\top), \quad \Omega_{ij} = -\frac{1}{2} \epsilon_{ijk} \omega_k.
\]
The squared tensor trace expands as:
\[
\operatorname{tr}((\nabla u)^2) = \operatorname{tr}((S + \Omega)^2) = \operatorname{tr}(S^2) + 2\operatorname{tr}(S\Omega) + \operatorname{tr}(\Omega^2).
\]
By symmetry and contraction:
- $\operatorname{tr}(S\Omega) = S_{ij} \Omega_{ji} = -S_{ij} \Omega_{ij} = 0$ (symmetric contracted against skew-symmetric).
- $\operatorname{tr}(\Omega^2) = \Omega_{ij} \Omega_{ji} = -\Omega_{ij} \Omega_{ij} = -\frac{1}{4} \epsilon_{ijk}\epsilon_{ijm} \omega_k \omega_m = -\frac{1}{4}(2\delta_{km})\omega_k \omega_m = -\frac{1}{2}|\omega|^2$.

Thus, we obtain the **exact classical pressure Poisson equation**:
\[
\boxed{ -\Delta p = \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2 = Q_{\text{OW}}(x, t) },
\]
where $Q_{\text{OW}}(x, t) := \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2$ is the second invariant of $\nabla u$ (the Okubo–Weiss parameter).

---

## 2. Global Enstrophy–Strain Equipartition Identity

### Theorem 1 (Global Enstrophy–Strain Balance on $\mathbb{T}^3$)
For any smooth, divergence-free velocity field on the periodic torus $\mathbb{T}^3$:
\[
\boxed{ \int_{\mathbb{T}^3} \operatorname{tr}(S^2) \, dx = \frac{1}{2} \int_{\mathbb{T}^3} |\omega|^2 \, dx }.
\]

### Proof
Integrating the pressure Poisson equation over the periodic torus $\mathbb{T}^3$:
\[
\int_{\mathbb{T}^3} (-\Delta p) \, dx = \int_{\mathbb{T}^3} \left( \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2 \right) dx.
\]
By the divergence theorem on $\mathbb{T}^3$ with periodic boundary conditions:
\[
\int_{\mathbb{T}^3} \Delta p \, dx = \int_{\partial \mathbb{T}^3} \nabla p \cdot n \, d\sigma \equiv 0.
\]
Therefore, $\int_{\mathbb{T}^3} \left( \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2 \right) dx = 0$, proving the theorem. $\blacksquare$

### Corollary 1.1 (Absence of Global Strain Dominance)
It is mathematically impossible for strain to globally dominate enstrophy, or for enstrophy to globally dominate strain on $\mathbb{T}^3$. Any region of extreme vortex stretching or vorticity concentration must be accompanied by a spatially compensating region of opposite sign in $Q_{\text{OW}}$.

---

## 3. Local Extrema and Topological Structure of Pressure

The sign of the Laplacian of pressure dictates the local dominance of strain versus rotation:
1. **Pressure Minima ($\Delta p \ge 0$):**
   \[
   -\Delta p \le 0 \implies \boxed{ \frac{1}{2}|\omega|^2 \ge \operatorname{tr}(S^2) }.
   \]
   *Physical Meaning:* Local pressure minima are **vortex cores** where rotation strictly dominates deformation.
2. **Pressure Maxima ($\Delta p \le 0$):**
   \[
   -\Delta p \ge 0 \implies \boxed{ \operatorname{tr}(S^2) \ge \frac{1}{2}|\omega|^2 }.
   \]
   *Physical Meaning:* Local pressure maxima are **hyperbolic saddle points** where strain strictly dominates rotation.

---

## 4. The Non-Local Pressure Hessian Tensor

On the periodic torus $\mathbb{T}^3$, solving $-\Delta p = Q_{\text{OW}}$ for the zero-mean pressure gives:
\[
p(x) = (-\Delta)^{-1} \left( \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2 \right).
\]
Applying two spatial derivatives yields the **pressure Hessian matrix** $\Pi_{ij} := \partial_i \partial_j p$:
\[
\boxed{ \Pi_{ij}(x, t) = \mathcal{R}_i \mathcal{R}_j \left( \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2 \right) },
\]
where $\mathcal{R}_i = \partial_i (-\Delta)^{-1/2}$ are the periodic Riesz transforms on $\mathbb{T}^3$.

Because $\sum_{i=1}^3 \mathcal{R}_i^2 = -I$, the trace of the Hessian recovers the Laplacian:
\[
\operatorname{tr}(\Pi) = \sum_{i=1}^3 \Pi_{ii} = \Delta p = -\left(\operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2\right).
\]
The deviatoric (trace-free) part of the pressure Hessian is:
\[
\Pi^{\text{dev}} := \Pi - \frac{1}{3}\operatorname{tr}(\Pi) I = \left( \mathcal{R} \otimes \mathcal{R} + \frac{1}{3} I \right) \left( \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2 \right).
\]
This operator is non-local and possesses a singular Calderón–Zygmund kernel of order $|x - y|^{-3}$ on $\mathbb{T}^3$.
