# TP2-G6-A1: Calderón–Zygmund Singular Integrals, Scale-Critical Estimates, and the Eulerian–Lagrangian Measure Gap

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A1 (Work Package 3)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Bridge:** `B1 — Non-Circular Xi Control`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. Riesz Representation of Strain and Strain Gradients on $\mathbb{T}^3$

For any divergence-free vector field $u \in H^1(\mathbb{T}^3)$ with $\nabla \cdot u = 0$ and $\nabla \times u = \omega$, the Biot–Savart law on the periodic torus expresses $u$ via the inverse Laplacian:
\[
u = (-\Delta)^{-1}(\nabla \times \omega).
\]
In terms of the periodic Riesz transforms $\mathcal{R}_i = \partial_i (-\Delta)^{-1/2}$, the velocity gradient tensor $A_{ij} = \partial_j u_i$ satisfies:
\[
\partial_j u_i = \epsilon_{ikm} \mathcal{R}_j \mathcal{R}_k \omega_m.
\]
The symmetric rate-of-strain tensor $S_{ij} = \frac{1}{2}(\partial_j u_i + \partial_i u_j)$ is therefore given by:
\[
S_{ij} = \frac{1}{2} \left( \epsilon_{ikm} \mathcal{R}_j \mathcal{R}_k + \epsilon_{jkm} \mathcal{R}_i \mathcal{R}_k \right) \omega_m =: \mathcal{M}_{ij}(\omega),
\]
where $\mathcal{M}_{ij}$ is a symmetric linear combination of degree-0 Fourier multiplier operators on $\mathbb{T}^3$.

Differentiating once more yields the representation of the strain gradient $\nabla S$:
\[
\partial_k S_{ij} = \mathcal{M}_{ij}(\partial_k \omega).
\]
Because spatial differentiation commutes with the Riesz transforms on $\mathbb{T}^3$, $\nabla S$ is precisely the image of the vorticity gradient $\nabla \omega$ under the same singular Calderón–Zygmund operator family.

---

## 2. Calderón–Zygmund $L^p$ Bounds and Scale-Criticality

### Theorem 3 (Calderón–Zygmund Regularity on $\mathbb{T}^3$)
For any $1 < p < \infty$, there exists a universal constant $C_p = C(p) < \infty$ such that for every smooth divergence-free velocity field on $\mathbb{T}^3$:
\[
\|S\|_{L^p(\mathbb{T}^3)} \le C_p \|\omega\|_{L^p(\mathbb{T}^3)},
\]
and
\[
\|\nabla S\|_{L^p(\mathbb{T}^3)} \le C_p \|\nabla \omega\|_{L^p(\mathbb{T}^3)}.
\]
Furthermore, $C_p \sim \frac{p^2}{p-1}$ as $p \to 1$ or $p \to \infty$.

### Scale-Critical Exponent $p = 3$:
Under the parabolic rescaling $u_\lambda(x, t) = \lambda u(\lambda x, \lambda^2 t)$, the scale-invariant Lebesgue space for velocity is $L^3(\mathbb{T}^3)$, and for vorticity and velocity gradients is $L^{3/2}(\mathbb{T}^3)$. For the gradient of vorticity and strain, the scale-critical Sobolev space is $\dot{W}^{1, 3/2}$ or $L^1$ in critical scaling.

At $p = 3$:
\[
\|\nabla S\|_{L^3(\mathbb{T}^3)} \le C_3 \|\nabla \omega\|_{L^3(\mathbb{T}^3)}.
\]
However, the critical Navier–Stokes regularity criteria (e.g., Ladyzhenskaya–Prodi–Serrin $L_t^p L_x^q$ with $\frac{2}{p} + \frac{3}{q} = 1$, or Beale–Kato–Majda $\int_0^T \|\omega(\cdot, t)\|_{L^\infty} dt < \infty$) require endpoint control at $q = \infty$.

---

## 3. The Endpoint Breakdown at $p = \infty$ and $p = 1$

It is a fundamental theorem of harmonic analysis that Riesz transforms fail to be bounded on $L^\infty(\mathbb{T}^3)$ and $L^1(\mathbb{T}^3)$:
1. **At $p = \infty$:**
   \[
   \|S\|_{L^\infty} \not\le C \|\omega\|_{L^\infty}, \quad \|\nabla S\|_{L^\infty} \not\le C \|\nabla \omega\|_{L^\infty}.
   \]
   Instead, the optimal substitution is bounded mean oscillation:
   \[
   \|S\|_{BMO(\mathbb{T}^3)} \le C \|\omega\|_{L^\infty(\mathbb{T}^3)}.
   \]
2. **At $p = 1$:**
   The operator maps $L^1$ only into weak-$L^1$ ($L^{1, \infty}$).

Because $BMO$ admits logarithmic singularities (e.g., $S(x) \sim \log(1/|x|)$), Calderón–Zygmund estimates **cannot prevent localized pointwise concentration or singular peaking** of strain without additional geometric or structural constraints.

---

## 4. Evaluation Against Bridge $B_1$ and the Eulerian–Lagrangian Measure Gap

Recall the definition of the pathwise deformation metric:
\[
\Xi_s = \frac{\|D_s J_\omega(A_s, s)\|_F^2}{|D_s \omega(A_s, s)|^2},
\]
and its role in the exact forwardized enstrophy evolution identity:
\[
\partial_s \log \chi_s = 2\nu \, \mathbb{E}_{\mu_s}[\Xi_s].
\]

### The Crucial Structural Question:
Can Eulerian Calderón–Zygmund bounds $\|\nabla S\|_{L^p(dx)} \le C_p \|\nabla \omega\|_{L^p(dx)}$ establish a non-circular lower or upper bound on $\mathbb{E}_{\mu_s}[\Xi_s]$?

### Analysis of the Obstacle:
1. **Eulerian vs. Stochastic Measure Disconnect:**
   The Calderón–Zygmund bounds are formulated exclusively with respect to the spatial Lebesgue volume measure $dx$ on $\mathbb{T}^3$:
   \[
   \int_{\mathbb{T}^3} |\nabla S(x)|^p \, dx \le C_p^p \int_{\mathbb{T}^3} |\nabla \omega(x)|^p \, dx.
   \]
   In sharp contrast, $\mathbb{E}_{\mu_s}[\Xi_s]$ is an expectation with respect to the stochastic history push-forward measure $\mu_s$:
   \[
   \mathbb{E}_{\mu_s}[\Xi_s] = \int_{\mathbb{T}^3} \Xi_s(x) \, d\mu_s(x).
   \]
2. **Radon–Nikodym Singularity:**
   Even if $u$ is smooth on $[0, s]$, the Radon–Nikodym density $\rho_s(x) = \frac{d\mu_s}{dx}(x)$ satisfies a backward Fokker–Planck / transport equation whose bounds depend exponentially on $\int_0^s \|\nabla u(\tau)\|_{L^\infty} d\tau$.
   To bound $\mu_s$ uniformly by $C \, dx$ would require assuming a priori that $\|\nabla u\|_{L^\infty}$ is integrable, which is the **exact Beale–Kato–Majda regularity condition**.
3. **Pointwise Decoupling:**
   Because Calderón–Zygmund theory only controls $L^p$ norms ($p < \infty$) and not $L^\infty$, $\Xi_s(x)$ can be arbitrarily small or large on sets of non-zero measure where $\mu_s$ is concentrated, while the global $L^p(dx)$ norm remains moderate.

### Structural Finding:
Bridge $B_1$ (non-circular $\Xi$ control) **cannot be closed within purely Eulerian $L^p$ Calderón–Zygmund theory**. It intrinsically requires an estimate governing the measure transfer $d\mu_s \leftrightarrow dx$, which is precisely **Bridge $B_2$**.
Attempts to deduce $B_1$ from $L^p$ singular integrals without solving the $B_2$ measure alignment inevitably incur BKM circularity.
