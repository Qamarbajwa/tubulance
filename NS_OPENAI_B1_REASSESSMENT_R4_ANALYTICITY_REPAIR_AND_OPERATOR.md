# Exact Linearized Operator and Coefficient Regularity Repair for Analyticity

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R4`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`  
**Scope**: Mandate Section 2 (Analyticity claim repair) & Section 3 (Exact linearized operator)

---

## 1. Audit and Repair of the R3 Analyticity Claim (Section 2)

In milestone `NS-OPENAI-B1-REASSESSMENT-R3`, the following assertion was recorded:
$$\text{Assertion (R3): } u_B \in C([0, T]; H^s(\mathbb{T}^3)), \quad s > 5/2 \implies \mathcal{U}(T, 0) L^2_{\text{div}}(\mathbb{T}^3) \subset C^\omega(\mathbb{T}^3).$$

An adversarial mathematical audit confirms that **this assertion was overstated**. In linear parabolic PDE theory, spatial real-analyticity ($C^\omega$) of the solution requires spatial real-analyticity of the PDE coefficients. Finite Sobolev regularity ($H^s$) of the background flow $u_B$ does **not** suffice to prove that the forward evolution family maps $L^2$ into real-analytic functions.

To restore epistemic rigor, we delineate three fundamentally distinct cases:

### Case A: The Pure Heat Equation on $\mathbb{T}^3$
$$\partial_t w - \nu \Delta w = 0, \qquad x \in \mathbb{T}^3, \quad t > 0.$$
- **Solution Operator**: $w(t) = e^{\nu t \Delta} w_0 = \sum_{k \in \mathbb{Z}^3} \widehat{w}_0(k) e^{-\nu t |k|^2} e^{ik \cdot x}$.
- **Smoothing Mechanism**: For any initial datum $w_0 \in L^2(\mathbb{T}^3)$ and any $t > 0$, the Fourier coefficients satisfy:
  $$|\widehat{w}(k, t)| \le \|w_0\|_{L^2} e^{-\nu t |k|^2}.$$
  Because the dissipation exponent is quadratic ($-\nu t |k|^2$), the Fourier series converges uniformly in the entire complex strip $\{ z \in \mathbb{C}^3 : |\operatorname{Im}(z)| < \infty \}$.
- **Regularity**: $w(t)$ is **entire real-analytic** on $\mathbb{C}^3$ for all $t > 0$.
- **Status**: **`EXACT_ANALYTIC_SMOOTHING_PROVED`**.

---

### Case B: The Full Nonlinear Navier–Stokes Equation
$$\partial_t u + \mathbb{P}[(u \cdot \nabla)u] - \nu \Delta u = 0, \qquad \operatorname{div} u = 0.$$
- **Smoothing Mechanism (Foias–Temam 1989; Grujić–Kukavica 1998)**:
  Let $A = -\mathbb{P}\Delta$ and define the Gevrey operator $e^{\tau(t) A^{1/2}}$. Testing the equation in the Gevrey space $G_{\tau}$ with $\tau(t) = \min(\sqrt{\nu t}, \tau_0)$:
  $$\frac{1}{2}\frac{d}{dt} \|u\|_{G_\tau}^2 + \nu \|A^{1/2} u\|_{G_\tau}^2 = \tau'(t) \|A^{1/4} u\|_{G_\tau}^2 - \langle \mathbb{P}[(u \cdot \nabla)u], A u \rangle_{G_\tau}.$$
  Because the advecting velocity is **the exact same field** $u$ that is being smoothed by the dissipation, the trilinear convective term satisfies the closed Gevrey inequality:
  $$|\langle \mathbb{P}[(u \cdot \nabla)u], A u \rangle_{G_\tau}| \le C \|u\|_{G_\tau} \|A^{1/2} u\|_{G_\tau} \|A u\|_{G_\tau} \le \frac{\nu}{2} \|A u\|_{G_\tau}^2 + \frac{C'}{\nu} \|u\|_{G_\tau}^2 \|A^{1/2} u\|_{G_\tau}^2.$$
  This allows Grönwall absorption and proves that any strong solution originating from $u_0 \in H^1_{\text{div}}(\mathbb{T}^3)$ becomes spatial real-analytic with radius $\rho(t) \ge c\min(\sqrt{\nu t}, 1) > 0$.
- **Status**: **`NONLINEAR_ANALYTIC_SMOOTHING_PROVED`**.

---

### Case C: The Linearized Equation with Prescribed Background $u_B(x, t)$
$$\partial_t w + \mathbb{P}[(u_B \cdot \nabla)w + (w \cdot \nabla)u_B] - \nu \Delta w = 0, \qquad \operatorname{div} w = 0.$$
In this system, the advecting field $u_B$ is **decoupled** from the perturbation $w$. The regularizing effect of the Stokes operator $-\nu \Delta$ acts exclusively on $w$.

Let us examine the Gevrey-1 (analyticity) energy estimate for $w$:
$$\frac{1}{2}\frac{d}{dt} \|w\|_{G_\sigma}^2 + \nu \|\nabla w\|_{G_\sigma}^2 \le \sigma'(t) \|A^{1/4} w\|_{G_\sigma}^2 + |\langle \mathbb{P}[(u_B \cdot \nabla)w + (w \cdot \nabla)u_B], w \rangle_{G_\sigma}|.$$
In Fourier space, the convective term is:
$$\widehat{(u_B \cdot \nabla w)}(k) = \sum_{j \in \mathbb{Z}^3} i (k - j) \cdot \widehat{u}_B(j) \, \widehat{w}(k - j).$$
Multiplying by the exponential Gevrey weight $e^{\sigma |k|}$ and using the sub-additive triangle inequality $|k| \le |j| + |k - j|$:
$$e^{\sigma |k|} |\widehat{(u_B \cdot \nabla w)}(k)| \le \sum_{j \in \mathbb{Z}^3} |k - j| \left( e^{\sigma |j|} |\widehat{u}_B(j)| \right) \left( e^{\sigma |k - j|} |\widehat{w}(k - j)| \right).$$
Notice the factor:
$$\sum_{j \in \mathbb{Z}^3} e^{\sigma |j|} |\widehat{u}_B(j)| = \|u_B\|_{G_\sigma}.$$

#### Epistemic Classification of Background Regularity:

1. **Class 1: `SOBOLEV_BACKGROUND` ($u_B \in C([0, T]; H^s(\mathbb{T}^3))$ for finite $s$)**:
   - The Fourier coefficients of $u_B$ decay only polynomially: $|\widehat{u}_B(j)| \sim (1 + |j|)^{-s}$.
   - Consequently, $\|u_B\|_{G_\sigma} = \sum_j e^{\sigma |j|} (1 + |j|)^{-s} = +\infty$ for every $\sigma > 0$.
   - **Conclusion**: Spatial real-analyticity of $w(t)$ **cannot be proved** from finite Sobolev regularity of $u_B$. Solutions $w(t)$ gain infinite Sobolev differentiability ($C^\infty$) if $u_B \in C^\infty$, but are **not** necessarily real-analytic.

2. **Class 2: `GEVREY_BACKGROUND` ($u_B \in C([0, T]; G_\alpha(\mathbb{T}^3))$ with index $\alpha > 1$)**:
   - The Fourier coefficients decay as $|\widehat{u}_B(j)| \le C \exp(-c |j|^{1/\alpha})$.
   - The solution $w(t)$ gains Gevrey regularity of matching index $G_\alpha$, but not strict real-analyticity ($G_1 = C^\omega$).

3. **Class 3: `ANALYTIC_BACKGROUND` ($u_B \in C([0, T]; C^\omega(\mathbb{T}^3))$ with uniform radius $\rho_B > 0$)**:
   - The Fourier coefficients decay exponentially: $|\widehat{u}_B(j)| \le C \exp(-\rho_B |j|)$.
   - For every $\sigma \in (0, \rho_B)$, the norm $\|u_B\|_{G_\sigma} < \infty$ is strictly bounded.
   - The Gevrey commutator estimate closes:
     $$|\langle \mathbb{P}[(u_B \cdot \nabla)w], w \rangle_{G_\sigma}| \le C \|u_B\|_{G_\sigma} \|w\|_{G_\sigma} \|\nabla w\|_{G_\sigma} \le \frac{\nu}{2} \|\nabla w\|_{G_\sigma}^2 + \frac{C^2}{\nu} \|u_B\|_{G_\sigma}^2 \|w\|_{G_\sigma}^2.$$
   - **Theorem 1.1**: Under an `ANALYTIC_BACKGROUND` with spatial analyticity radius $\rho_B > 0$, the forward linearized propagator $\mathcal{U}_{u_B}(t, 0)$ maps $L^2_{\text{div}}(\mathbb{T}^3)$ into $C^\omega(\mathbb{T}^3)$, with radius of analyticity $\rho(t) = \min(c\sqrt{\nu t}, \rho_B) > 0$.

### 1.4 Synthesis of the Analyticity Repair
$$\boxed{\begin{aligned}
u_B \in H^s \ (s > 5/2) &\centernot\implies \mathcal{U}_{u_B}(T, 0)L^2 \subset C^\omega \quad (\text{R3 claim retracted}) \\
u_B \in C^\omega \ (\rho_B > 0) &\implies \mathcal{U}_{u_B}(T, 0)L^2 \subset C^\omega \quad (\text{Valid with radius } \min(c\sqrt{\nu T}, \rho_B)) \\
u_B \in C^\infty \ (\text{smooth non-analytic}) &\implies \mathcal{U}_{u_B}(T, 0)L^2 \subset C^\infty \quad (\text{Sobolev smoothing only})
\end{aligned}}$$

---

## 2. Construction of the Exact Periodic Linearized Operator (Section 3)

Let $\mathbb{T}^3 = (\mathbb{R} / 2\pi \mathbb{Z})^3$. We define the canonical Hilbert spaces of divergence-free vector fields:
$$H \equiv L^2_{\text{div}}(\mathbb{T}^3) = \left\{ w \in L^2(\mathbb{T}^3; \mathbb{R}^3) : \operatorname{div} w = 0, \; \int_{\mathbb{T}^3} w \, dx = 0 \right\},$$
$$V \equiv H^1_{\text{div}}(\mathbb{T}^3) = H^1(\mathbb{T}^3; \mathbb{R}^3) \cap H, \qquad V' \equiv H^{-1}_{\text{div}}(\mathbb{T}^3).$$

Let $\mathbb{P}: L^2(\mathbb{T}^3) \to H$ be the Leray–Helmholtz orthogonal projection. The Stokes operator is:
$$A \equiv -\mathbb{P} \Delta = -\Delta \quad \text{on } \mathcal{D}(A) = H^2(\mathbb{T}^3) \cap H.$$
$A$ is a self-adjoint, positive-definite operator on $H$ with compact inverse and discrete spectrum $\lambda_k = |k|^2$ for $k \in \mathbb{Z}^3 \setminus \{0\}$.

### 2.1 The Time-Dependent Linearized Generator $L_{u_B}(t)$
Let $u_B \in C([0, T]; V)$ be a prescribed periodic background flow with $\operatorname{div} u_B = 0$. For any $w \in \mathcal{D}(A)$, we define:
$$L_{u_B}(t) w \equiv -\nu A w - B(t) w,$$
where the linearized advection-straining operator $B(t)$ is defined by:
$$B(t) w \equiv \mathbb{P} \left[ (u_B(t) \cdot \nabla)w + (w \cdot \nabla)u_B(t) \right].$$

### 2.2 Continuity and Sectoriality Estimates
For any $w \in V$ and $\phi \in V$, the bilinear form associated with $B(t)$ satisfies:
$$\langle B(t) w, \phi \rangle = \int_{\mathbb{T}^3} \left[ ((u_B \cdot \nabla)w) \cdot \phi + ((w \cdot \nabla)u_B) \cdot \phi \right] dx.$$
By incompressibility $\operatorname{div} u_B = 0$, $\int ((u_B \cdot \nabla)w) \cdot w \, dx = 0$. Thus:
$$\langle B(t)w, w \rangle = \int_{\mathbb{T}^3} ((w \cdot \nabla)u_B) \cdot w \, dx = \int_{\mathbb{T}^3} w^T S(u_B) w \, dx,$$
where $S(u_B) = \frac{1}{2}(\nabla u_B + (\nabla u_B)^T)$ is the background strain rate tensor.

Therefore, the coercive dissipation satisfies:
$$\langle L_{u_B}(t)w, w \rangle = -\nu \|\nabla w\|_{L^2}^2 - \int_{\mathbb{T}^3} w^T S(u_B) w \, dx \le -\nu \|\nabla w\|_{L^2}^2 + \|S(u_B(t))\|_{L^\infty} \|w\|_{L^2}^2.$$

By the Poincaré inequality on $\mathbb{T}^3$ ($\|\nabla w\|_{L^2}^2 \ge \|w\|_{L^2}^2$):
$$\langle L_{u_B}(t)w, w \rangle \le -(\nu - \|S(u_B(t))\|_{L^\infty}) \|w\|_{L^2}^2.$$

### 2.3 Generation of the Evolution Family $\mathcal{U}_{u_B}(t, s)$
By standard Kato–Tanabe evolution theory for non-autonomous parabolic equations:
**Theorem 2.1**:  
Assume $u_B \in C([0, T]; H^s(\mathbb{T}^3))$ with $s > 5/2$. There exists a unique two-parameter family of bounded linear operators:
$$\left\{ \mathcal{U}_{u_B}(t, s) : 0 \le s \le t \le T \right\} \subset \mathcal{L}(H)$$
satisfying:
1. $\mathcal{U}_{u_B}(s, s) = I$ for all $s \in [0, T]$;
2. $\mathcal{U}_{u_B}(t, r) \mathcal{U}_{u_B}(r, s) = \mathcal{U}_{u_B}(t, s)$ for all $0 \le s \le r \le t \le T$;
3. For every $w_0 \in H$, the mapping $(t, s) \mapsto \mathcal{U}_{u_B}(t, s) w_0$ is continuous into $H$;
4. For every $w_0 \in H$ and $t > s$, $w(t) = \mathcal{U}_{u_B}(t, s) w_0$ belongs to $C((s, T]; \mathcal{D}(A)) \cap C^1((s, T]; H)$ and solves:
   $$\frac{\partial}{\partial t} w(t) = L_{u_B}(t) w(t), \qquad \lim_{t \downarrow s} \|w(t) - w_0\|_H = 0.$$
5. **Energy Bound**:
   $$\|\mathcal{U}_{u_B}(t, s)\|_{\mathcal{L}(H)} \le \exp\left( \int_s^t \|S(u_B(\tau))\|_{L^\infty} d\tau \right).$$

This constructs the rigorous, non-affine evolution operator on the full periodic 3-torus $\mathbb{T}^3$.
