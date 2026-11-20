# TP2-G1: STOCHASTIC CONVENTION CONTRACT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1 (Stochastic Representation Convention Gate)`  
**Governance:** Mid-Project Governance v2.9  
**Status:** Authoritative Mathematical Specification  

---

## 1. Domain, Trajectories, and Time Orientations

Let $\Omega = \mathbb{R}^3$ or $\mathbb{T}^3$, $\nu > 0$, and let $u \in C([0, T]; C^k(\Omega; \mathbb{R}^3))$ ($k \ge 2$) be a smooth divergence-free velocity field satisfying the 3D incompressible Navier–Stokes equations:
$$\partial_t u + (u \cdot \nabla) u + \nabla p = \nu \Delta u, \quad \nabla \cdot u = 0.$$
Let $\omega = \nabla \times u$ denote the vorticity field.

Let $(\Omega_{\text{prob}}, \mathcal{F}, (\mathcal{F}_t)_{t \ge 0}, \mathbb{P})$ be a filtered probability space supporting a standard 3D Brownian motion $W_t$.

### 1.1 Forward Stochastic Flow
For initial time $s \ge 0$ and initial label $a \in \Omega$, the **forward stochastic flow** $X_{s,t}(a)$ for $t \ge s$ is defined by the Itô stochastic differential equation:
$$X_{s,t}(a) = a + \int_s^t u(X_{s,\tau}(a), \tau) d\tau + \sqrt{2\nu} (W_t - W_s), \quad t \ge s.$$
Under $C^k$ regularity ($k \ge 2$) of $u$, the mapping $a \mapsto X_{s,t}(a)$ is almost surely a $C^{k-1}$ stochastic diffeomorphism of $\Omega$ (Kunita 1990).

### 1.2 Inverse Map / Backward Trajectory
For terminal time $t \ge s$ and terminal spatial position $x \in \Omega$, the **inverse flow map** $A_{s,t}(x)$ (also written $A_t^s(x)$) is defined by:
$$A_{s,t}(x) := X_{s,t}^{-1}(x) \in \Omega.$$
By definition:
$$X_{s,t}(A_{s,t}(x)) = x \quad \text{for all } x \in \Omega, \qquad A_{s,t}(X_{s,t}(a)) = a \quad \text{for all } a \in \Omega.$$
$A_{s,t}(x)$ is the random origin point at time $s$ of the stochastic trajectory that arrives at position $x$ at time $t$.

---

## 2. Jacobians and Deformation Operators

### 2.1 Forward Deformation Gradient
The forward deformation gradient $F_{s,t}(a)$ is the spatial Jacobian of the forward flow:
$$[F_{s,t}(a)]_{ij} := \frac{\partial X_{s,t}^i(a)}{\partial a_j}, \quad F_{s,s}(a) = I_3.$$
Because the Brownian increment $\sqrt{2\nu} dW_t$ is spatially homogeneous ($\nabla_a dW_t = 0$), $F_{s,t}(a)$ satisfies the pathwise random ODE:
$$\frac{d}{dt} F_{s,t}(a) = \nabla u(X_{s,t}(a), t) \, F_{s,t}(a), \quad F_{s,s}(a) = I_3.$$
Since $\operatorname{tr}(\nabla u) = \nabla \cdot u = 0$, Liouville's theorem yields:
$$\det F_{s,t}(a) = \exp\left( \int_s^t \nabla \cdot u(X_{s,\tau}(a), \tau) d\tau \right) = 1 \quad \text{almost surely}.$$

### 2.2 Inverse Jacobian and Terminal Deformation Operator
Differentiating $X_{s,t}(A_{s,t}(x)) = x$ with respect to $x_j$ by the chain rule:
$$\sum_{k=1}^3 \frac{\partial X_{s,t}^i}{\partial a_k}(A_{s,t}(x)) \, \frac{\partial A_{s,t}^k}{\partial x_j}(x) = \delta_{ij} \implies \nabla_a X_{s,t}(A_{s,t}(x)) \cdot \nabla_x A_{s,t}(x) = I_3.$$
Therefore, the spatial Jacobian of the inverse map $A_{s,t}(x)$ is:
$$\nabla_x A_{s,t}(x) = \left[ F_{s,t}(A_{s,t}(x)) \right]^{-1}.$$
We define the **stochastic Cauchy deformation operator** $D_t^s(x)$ acting on initial/intermediate vorticity:
$$\boxed{ D_t^s(x) := F_{s,t}(A_{s,t}(x)) = \left[ \nabla_x A_{s,t}(x) \right]^{-1} }$$

---

## 3. Constantin–Iyer Stochastic Vorticity Representation

The stochastic Cauchy contribution $Z_s^{x,t}$ and terminal vorticity $\omega(x,t)$ are given by:
$$\boxed{ Z_s^{x,t} := D_t^s(x) \, \omega(A_{s,t}(x), s) = \left[ \nabla_x A_{s,t}(x) \right]^{-1} \omega(A_{s,t}(x), s) }$$
$$\boxed{ \omega(x,t) = \mathbb{E} \left[ Z_s^{x,t} \right] = \mathbb{E} \left[ D_t^s(x) \, \omega(A_{s,t}(x), s) \right] }$$

---

## 4. Rigorous Answers to G1 Required Questions

### Q1: What exactly is $D_t^s(x)$?
$D_t^s(x)$ is the forward deformation matrix $F_{s,t}(a) = \nabla_a X_{s,t}(a)$ evaluated at the random initial position $a = A_{s,t}(x) = X_{s,t}^{-1}(x)$, which identically equals the matrix inverse of the backward/inverse spatial Jacobian $\nabla_x A_{s,t}(x)$. It is an elements-of-$SL(3, \mathbb{R})$ matrix ($\det D_t^s(x) = 1$) that maps vorticity vectors at the origin point $A_t^s(x)$ to their pathwise stretched orientation at $(x,t)$.

### Q2: Does the correct vorticity expression contain $F$, $F^{-1}$, $F^T$, or $F^{-T}$?
- In terms of the **forward flow Jacobian** $F_{s,t}(a)$: evaluated at $a = A_{s,t}(x)$, the vorticity formula contains **$F_{s,t}(A_{s,t}(x))$** directly (direct forward deformation).
- In terms of the **spatial Jacobian of the inverse map** $J_{\text{back}}(x) := \nabla_x A_{s,t}(x)$: the vorticity formula contains the **inverse $(J_{\text{back}}(x))^{-1}$**.
- In terms of the **Weber velocity formulation** ($u = \mathbf{P} \mathbb{E}[ (\nabla A)^T u_0(A) ]$): the velocity formula contains the **transpose** $(\nabla A)^T = F^{-T}$. Taking the curl converts this transpose-inverse into the direct inverse $(\nabla A)^{-1} = F$.
- **Previous Project Correction**: Any formula expressing vorticity with $(\nabla A)^T$ or $F^{-1}$ without the pullback curl inversion was an algebraic typo. The vorticity representation contains $D = (\nabla A)^{-1} = F(A(x))$.

### Q3: What stochastic differential equation is obeyed by the relevant deformation matrix?
Along the forward path $X_{s,t}(a)$, $F_{s,t}(a)$ solves the linear random ODE:
$$d_t F_{s,t}(a) = \nabla u(X_{s,t}(a), t) \, F_{s,t}(a) \, dt, \quad F_{s,s}(a) = I_3.$$
For $D_t^s(x) = (\nabla_x A_{s,t}(x))^{-1}$, under the backward flow parameterized by $s \in [0, t]$ at fixed terminal $(x,t)$, $D_t^s(x)$ satisfies the backward stochastic transport/stretching equation.

### Q4: What time orientation is used in the backward formulation?
The terminal space-time point $(x,t)$ is fixed. Time $s$ runs backward on the interval $[0, t]$ (from $s=t$ down to $s=0$). The filtration is the backward filtration $\mathcal{F}_t^s = \sigma(W_\tau - W_s : s \le \tau \le t)$, and expectations are conditioned on the terminal position $X(t) = x$.

### Q5: Which identities require a smooth stochastic diffeomorphism?
The identity $\nabla_x \times \left( (\nabla_x A)^T v(A(x)) \right) = (\det \nabla A) (\nabla_x A)^{-1} (\nabla_a \times v)(A(x))$ rigorously requires:
1. $C^2$ spatial regularity of $A_{s,t}(x)$, so that cross second derivatives $\frac{\partial^2 A^k}{\partial x_i \partial x_j} = \frac{\partial^2 A^k}{\partial x_j \partial x_i}$ commute and vanish under contraction with $\epsilon_{mij}$.
2. $C^1$ spatial regularity of velocity $u$ to ensure existence and uniqueness of the flow Jacobians.
3. Incompressibility ($\nabla \cdot u = 0$) ensuring $\det \nabla A = 1$.

### Q6: Which of those assumptions are unavailable for generic Leray solutions despite Galeati's trajectory-uniqueness result?
Galeati (2025) establishes trajectory uniqueness for Lebesgue-a.e. initial point for general Leray solutions ($u_0 \in L^2$), and for every initial point for $u_0 \in H^{1/2}$.
**Crucial Boundary:**
- Galeati provides almost-everywhere uniqueness of individual Lagrangian curves $t \mapsto X_t(a)$.
- It does **NOT** establish spatial differentiability ($C^1$ or $W^{1,p}$ Sobolev regularity) of the stochastic flow map $a \mapsto X_{s,t}(a)$ or $x \mapsto A_{s,t}(x)$.
- Generic Leray solutions ($u \in L_t^\infty L_x^2 \cap L_t^2 H_x^1$) fail the Cauchy–Lipschitz or Ladyzhenskaya–Prodi–Serrin thresholds required for flow differentiability.
- Therefore, the deformation operator $D_t^s(x) = \nabla_x A_{s,t}(x)^{-1}$ cannot be evaluated in the classical sense for generic Leray solutions without higher regularity.
- **Rule:** The Constantin–Iyer representation is mathematically valid for classical/mild solutions on their lifespan $[0, T^*)$, but cannot be asserted as an a-priori weak-solution representation on generic Leray solutions.
