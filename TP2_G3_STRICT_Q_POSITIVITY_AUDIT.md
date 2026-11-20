# TP2-G3: STRICT QUADRATIC VARIATION POSITIVITY & FULL-SUPPORT AUDIT

**Authority:** Independent E4 Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3-E4R`  
**Governance Standard:** Autonomous Project Governance v2.9.4 (Tier T4)  
**Status:** Authoritative Mathematical Audit  

---

## 1. Problem Formulation

Let $u \in C([0, T]; C^2)$ be a classical, smooth solution of the 3D incompressible Navier–Stokes equations on the 3-torus $\mathbb{T}^3$ (or decaying whole-space $\mathbb{R}^3$ with $u \in L^2$).
For a fixed terminal observation point $(x, T)$ with nonzero vorticity $|\omega(x, T)| > 0$, consider the instantaneous quadratic variation production rate:
$$Q_s := 2\nu \, \mathbb{E}\left[ \| D_s J_\omega(A_s, s) \|_F^2 \right], \quad s < T.$$

### The Core Scientific Question:
*Does $|\omega(x, T)| > 0$ strictly imply $Q_s > 0$ for every strict lookback $s < T$?*

---

## 2. Rigorous Mathematical Proof

### Step A: Non-degenerate Diffusion and Full Topological Support
The backward stochastic Lagrangian trajectory $A_s = X_{s,T}^{-1}(x)$ satisfies the backward SDE:
$$d A_s = - u(A_s, s) ds + \sqrt{2\nu} \, \widehat{d}W_s, \quad A_T = x.$$
For $\nu > 0$ and $u \in C^1$, the backward Fokker–Planck (parabolic) operator is uniformly parabolic. By classical parabolic PDE theory (Aronson Gaussian bounds / Hörmander theorem), the transition probability density $p(s, a; T, x)$ is **strictly positive** for all $a \in \mathbb{T}^3$ (or all $a \in \mathbb{R}^3$) whenever $s < T$:
$$p(s, a; T, x) > 0 \quad \forall a \in \mathbb{T}^3, \; \forall s < T.$$
Thus, the marginal probability measure of $A_s$ has **full topological support** on $\mathbb{T}^3$ (or $\mathbb{R}^3$).

### Step B: Almost-Sure Invertibility of $D_s$
Under the classical $C^1$ flow regime, $D_s = J_{X_{s,T}}(A_s) \in SL(3, \mathbb{R})$ satisfies $\det(D_s) = 1$ almost surely.
Therefore, $D_s$ is strictly invertible on every sample path.

### Step C: Implication of $Q_s = 0$
Since the Frobenius norm squared is non-negative ($\|D_s J_\omega(A_s, s)\|_F^2 \ge 0$), $Q_s = 0$ requires:
$$\mathbb{E}\left[ \| D_s J_\omega(A_s, s) \|_F^2 \right] = 0 \implies D_s J_\omega(A_s, s) = 0 \quad \text{almost surely}.$$
Because $D_s$ is invertible almost surely:
$$J_\omega(A_s, s) = 0 \quad \text{almost surely under the distribution of } A_s.$$

### Step D: Full Support and Continuity Forces $J_\omega \equiv 0$
The mapping $y \mapsto \|J_\omega(y, s)\|_F^2$ is continuous on $\mathbb{T}^3$. Since the distribution of $A_s$ has full topological support (measure of any non-empty open set is strictly positive), the only continuous non-negative function that vanishes almost surely is identically zero:
$$J_\omega(y, s) \equiv 0 \quad \forall y \in \mathbb{T}^3.$$

### Step E: Spatial Uniformity of Vorticity
Since the spatial Jacobian vanishes identically on connected $\mathbb{T}^3$:
$$\nabla_M \omega(\cdot, s) \equiv 0 \implies \omega(y, s) = \omega_0 = \text{constant vector} \quad \forall y \in \mathbb{T}^3.$$

### Step F: Solvability / Periodic Boundary Constraint Forces $\omega_0 = 0$
On the 3-torus $\mathbb{T}^3$, vorticity is the curl of a periodic vector field: $\omega = \nabla \times u$.
By the divergence theorem on periodic domains:
$$\int_{\mathbb{T}^3} \omega(y, s) dy = \int_{\mathbb{T}^3} (\nabla \times u)(y, s) dy = 0.$$
Substituting the constant $\omega(y, s) = \omega_0$:
$$\omega_0 \cdot \operatorname{Vol}(\mathbb{T}^3) = 0 \implies \omega_0 = 0 \implies \omega(\cdot, s) \equiv 0.$$
*(In whole-space $\mathbb{R}^3$, an $L^2$-integrable constant field must likewise be identically zero).*

### Step G: Smooth Navier–Stokes Uniqueness Forces $\omega(\cdot, T) \equiv 0$
If $\omega(\cdot, s) \equiv 0$ at an earlier time $s < T$, then by the Biot–Savart law, the velocity field $u(\cdot, s)$ is purely harmonic / constant (and zero on periodic torus with zero mean).
By forward uniqueness of classical solutions to the Navier–Stokes equations:
$$\omega(\cdot, T) \equiv 0.$$
This directly contradicts the initial hypothesis $|\omega(x, T)| > 0$.

### Conclusion of Proof:
$$\boxed{ \text{For any classical smooth solution on } \mathbb{T}^3 \text{ (or decaying } \mathbb{R}^3\text{), if } |\omega(x, T)| > 0, \text{ then } Q_s > 0 \text{ for every } s < T. }$$

---

## 3. Scientific Classification and Disambiguation

We classify this result as:
$$\boxed{\textbf{SMOOTH\_IN\_CLASS\_NONTRIVIAL\_TERMINAL\_VORTICITY\_IMPLIES\_STRICT\_EXPECTED\_QV\_PRODUCTION}}$$
*(Classification: `KNOWN_IMPLICATION` / `PROJECT_DERIVATION_FROM_KNOWN_RESULTS`).*

### Disambiguation of Coexisting Truths:
1. `VISCOSITY_ALONE_DOES_NOT_ALGEBRAICALLY_FORCE_POINTWISE_STRICT_PRODUCTION`:
   Refers to the pointwise algebraic integrand: $\nu > 0$ alone does not make $\|D J_\omega\|_F^2$ positive if $J_\omega = 0$ along a path (e.g. Couette shear).
2. `SMOOTH_IN_CLASS_NONTRIVIAL_TERMINAL_VORTICITY_IMPLIES_STRICT_EXPECTED_QV_PRODUCTION`:
   Refers to the integral across Brownian histories on periodic/decaying domains: any non-zero terminal state requires non-trivial spatial gradients in its history, which Brownian motion explores with full topological support, forcing $Q_s > 0$.

---

## 4. Consequence for $\chi_s$ Monotonicity

For $|\omega(x, T)| > 0$, the coherence ratio $\chi_s = \frac{c}{c + V_s}$ has derivative:
$$\frac{\partial}{\partial s} \chi_s = \frac{c}{(c + V_s)^2} Q_s.$$
Since $Q_s > 0$ for all $s < T$, $\chi_s$ is **strictly monotonically increasing** forward in time toward $\chi_T = 1$:
$$\boxed{ \frac{\partial}{\partial s} \chi_s > 0 \quad \forall s < T \quad (\text{STRICT\_CHI\_LOOKBACK\_MONOTONICITY\_IN\_SMOOTH\_NONTRIVIAL\_CLASS}) }$$

> [!WARNING]
> **Qualitative Strict Monotonicity $\neq$ Quantitative Regularity Control**:
> $Q_s > 0$ merely asserts qualitative positivity ($Q_s \neq 0$). It does **not** provide any lower bound $Q_s \ge F(\text{stretching})$ to outgrow explosive pathwise deformation near potential singularities.
> Therefore, **the regularity bridge remains strictly OPEN**.
