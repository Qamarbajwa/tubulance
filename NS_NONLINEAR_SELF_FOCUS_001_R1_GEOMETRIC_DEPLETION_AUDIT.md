# NS_NONLINEAR_SELF_FOCUS_001_R1_GEOMETRIC_DEPLETION_AUDIT

## Polar Gradient Decomposition, Nodal Zero-Set Regularization, Reassessment of `NS-OBS-021`, and Beltrami/Lamb Calculus Audit (`NS-NONLINEAR-SELF-FOCUS-001-R1`, Sections 11–15)

| Field | Value |
| :--- | :--- |
| **Milestone ID** | `NS-NONLINEAR-SELF-FOCUS-001-R1` |
| **Parent Milestone** | `NS-NONLINEAR-SELF-FOCUS-001` |
| **Active Governance** | `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3` (`NS-GOV-MIG-V404-001 = MIGRATION_BLOCKED`) |
| **Mathematical Authority** | `Mathematical Research Constitution v1.0.1` |
| **Disposition of `NS-OBS-021`** | Downgraded to **`HEURISTIC_TENSION`** (`NS-OBS-021-R1`, backed by `EXACT_IDENTITY_ONLY` gradient split) |

---

## 1. Explicit Proof and Classification of the Length-Scale Decomposition (Section 11)

Let $\omega: \mathbb{T}^3_L \times [0,T] \to \mathbb{R}^3$ be a smooth vorticity field, and let $\Omega_+(t) := \{x \in \mathbb{T}^3_L : |\omega(x,t)| > 0\}$ be its open support at time $t$. On $\Omega_+(t)$, both the scalar magnitude $|\omega(x,t)| = \sqrt{\sum_{i=1}^3 \omega_i(x,t)^2} > 0$ and the unit direction vector $\xi(x,t) := \frac{\omega(x,t)}{|\omega(x,t)|} \in \mathbb{S}^2$ are $C^\infty$ smooth.

### Proposition 1.1 (Exact Polar Decomposition of Vorticity Gradient on $\Omega_+(t)$)
At every point $x \in \Omega_+(t)$, the following two identities hold identically:
$$\boxed{|\nabla\omega(x,t)|^2 = \big|\nabla|\omega(x,t)|\big|^2 + |\omega(x,t)|^2\,|\nabla\xi(x,t)|^2}$$
$$\boxed{\frac{|\nabla\omega(x,t)|^2}{|\omega(x,t)|^2} = \big|\nabla \ln|\omega(x,t)|\big|^2 + |\nabla\xi(x,t)|^2}$$

**Explicit Step-by-Step Proof:**
1. Since $\xi(x,t) \in \mathbb{S}^2$ has unit Euclidean length $\sum_{i=1}^3 \xi_i(x,t)^2 = 1$ on $\Omega_+(t)$, differentiating with respect to $x_k$ ($k \in \{1,2,3\}$) yields the orthogonality condition:
   $$\frac{\partial}{\partial x_k}\left(\sum_{i=1}^3 \xi_i^2\right) = 2\sum_{i=1}^3 \xi_i\,\partial_k \xi_i = 0 \implies \boxed{\xi(x,t) \cdot \partial_k \xi(x,t) = 0 \quad (\forall k \in \{1,2,3\})}.$$
2. Writing $\omega_i(x,t) = |\omega(x,t)|\,\xi_i(x,t)$ on $\Omega_+(t)$ and applying the product rule for $\partial_k = \frac{\partial}{\partial x_k}$:
   $$\partial_k \omega_i = \big(\partial_k |\omega|\big)\,\xi_i + |\omega|\,\partial_k \xi_i.$$
3. Squaring and summing over $i, k \in \{1,2,3\}$:
   $$\begin{aligned}
   |\nabla\omega|^2 = \sum_{k=1}^3 \sum_{i=1}^3 (\partial_k \omega_i)^2
   &= \sum_{k=1}^3 \left[\big(\partial_k |\omega|\big)^2 \underbrace{\sum_{i=1}^3 \xi_i^2}_{=\,1} + 2\,|\omega|\big(\partial_k |\omega|\big)\underbrace{\sum_{i=1}^3 \xi_i\,\partial_k \xi_i}_{=\,0} + |\omega|^2 \sum_{i=1}^3 (\partial_k \xi_i)^2\right]\\
   &= \sum_{k=1}^3 \big(\partial_k |\omega|\big)^2 + |\omega|^2 \sum_{k=1}^3 \sum_{i=1}^3 (\partial_k \xi_i)^2 = \big|\nabla|\omega|\big|^2 + |\omega|^2\,|\nabla\xi|^2.
   \end{aligned}$$
4. Dividing both sides by $|\omega(x,t)|^2 > 0$ on $\Omega_+(t)$ and using $\frac{\partial_k |\omega|}{|\omega|} = \partial_k \ln|\omega|$ yields:
   $$\frac{|\nabla\omega|^2}{|\omega|^2} = \big|\nabla \ln|\omega|\big|^2 + |\nabla\xi|^2. \qquad \blacksquare$$

> **Epistemic & Novelty Classification (Section 11)**:
> This identity is classified strictly as **`EXACT_GEOMETRIC_DECOMPOSITION` / `KNOWN`** (standard polar / spherical decomposition of the Dirichlet energy density of a vector field $\omega = |\omega|\xi$, appearing in harmonic map theory and in Constantin 1994 *SIAM Review* 36(1):73–98 and Gibbon, Holm, Kerr & Roulstone 2006). It is **not claimed as novel**.

---

## 2. Nodal Zero-Set Audit and Rigorous Global Formulations (Section 12)

Because $\xi = \omega/|\omega|$ is undefined on the nodal zero set $\mathcal{Z}_\omega(t) := \{x \in \mathbb{T}^3_L : |\omega(x,t)| = 0\}$ and $\ln|\omega| \to -\infty$ as $|\omega| \to 0$, **singular quotients such as $\frac{|\nabla\omega|^2}{|\omega|^2}$, $|\nabla\ln|\omega||^2$, and $|\nabla\xi|^2$ must never be integrated directly over $\mathbb{T}^3_L$ across $\mathcal{Z}_\omega(t)$**.

We establish three rigorous formulations that avoid any zero-set singularity:

1. **Pointwise Non-Zero Domain Formulation (`POINTWISE_ON_SUPPORT`)**:
   The unregularized quotient identity $\frac{|\nabla\omega|^2}{|\omega|^2} = |\nabla\ln|\omega||^2 + |\nabla\xi|^2$ is stated and evaluated strictly pointwise on the open set $\Omega_+(t) = \{x \in \mathbb{T}^3_L : |\omega(x,t)| > 0\}$.
2. **Enstrophy-Weighted Palinstrophy Integral (`WEIGHTED_L2_INTEGRAL`)**:
   When multiplied through by $|\omega(x,t)|^2$, the identity becomes:
   $$|\nabla\omega(x,t)|^2 = \big|\nabla|\omega(x,t)|\big|^2 + |\omega(x,t)|^2\,|\nabla\xi(x,t)|^2 \qquad \forall x \in \Omega_+(t).$$
   By Stampacchia's theorem for Sobolev/smooth functions, $\nabla\omega(x,t) = \mathbf{0}$ and $\nabla|\omega(x,t)| = \mathbf{0}$ for Lebesgue-almost-every $x \in \mathcal{Z}_\omega(t)$. Setting $|\omega|^2|\nabla\xi|^2 := 0$ on $\mathcal{Z}_\omega(t)$ yields the **exact globally valid palinstrophy decomposition on $\mathbb{T}^3_L$**:
   $$\boxed{D(t) = \nu \int_{\mathbb{T}^3_L} |\nabla\omega(x,t)|^2\,dx = \nu \int_{\Omega_+(t)} \big|\nabla|\omega(x,t)|\big|^2\,dx + \nu \int_{\Omega_+(t)} |\omega(x,t)|^2\,|\nabla\xi(x,t)|^2\,dx}$$
   Both integrals on the right-hand side are finite, non-negative, and bounded above by $D(t)$ (`0 \le \nu \int_{\Omega_+} |\omega|^2|\nabla\xi|^2\,dx \le D(t)`).
3. **$\varepsilon$-Regularized Inverse Length Scale and Superlevel-Set Truncation (`REGULARIZED_OR_TRUNCATED`)**:
   - For pointwise diagnostics on all of $\mathbb{T}^3_L$, $\ell_{\omega,\varepsilon}^{-2}(x,t) := \frac{|\nabla\omega(x,t)|^2}{|\omega(x,t)|^2 + \varepsilon}$ ($\varepsilon > 0$) is globally smooth on $\mathbb{T}^3_L$ and vanishes on the interior of $\mathcal{Z}_\omega(t)$.
   - For unweighted integral bounds of $|\nabla\xi|^2$, one must integrate strictly over the **Constantin–Fefferman high-vorticity superlevel set** $\Omega_M(t) := \{x \in \mathbb{T}^3_L : |\omega(x,t)| > M\}$ ($M > 0$), where:
     $$\int_{\Omega_M(t)} |\nabla\xi(x,t)|^2\,dx \le \frac{1}{M^2}\int_{\Omega_M(t)} |\omega(x,t)|^2\,|\nabla\xi(x,t)|^2\,dx \le \frac{D(t)}{\nu\,M^2} < \infty.$$

---

## 3. Adversarial Reassessment of `NS-OBS-021` (Section 13)

In `NS-NONLINEAR-SELF-FOCUS-001`, `NS-OBS-021` was registered with status `OPEN_STRUCTURAL_OBSTRUCTION`, claiming that overcoming Constantin–Fefferman geometric depletion forces $|\nabla\xi| \gtrsim \ell_\omega^{-1}$ and therefore injects a palinstrophy penalty $\nu|\omega|^2|\nabla\xi|^2 \gtrsim \nu|\omega|^2\ell_\omega^{-2}$.

Let us separate the **exact mathematical content** from the **unproved heuristic leap**:

| Layer | Mathematical Statement | Rigorous Status |
| :--- | :--- | :---: |
| **Layer 1 (Exact Palinstrophy Split)** | On $\Omega_+(t)$, $|\nabla\omega|^2 = |\nabla|\omega||^2 + |\omega|^2|\nabla\xi|^2$, so directional curvature $|\nabla\xi|^2$ contributes non-negatively to global viscous dissipation $D(t) = \nu\int_{\Omega_+} |\nabla|\omega||^2\,dx + \nu\int_{\Omega_+} |\omega|^2|\nabla\xi|^2\,dx$. | **`EXACT_IDENTITY_ONLY`** |
| **Layer 2 (Constantin–Fefferman 1993 & Beirão da Veiga–Berselli 2002 Theorems)** | If there exist $M > 0, \delta > 0, \rho > 0$ such that $|\xi(x,t) - \xi(y,t)| \le |x-y|^\alpha / \rho$ (with $\alpha = 1$ in C-F 1993, $\alpha = 1/2$ in BdV-B 2002) for all $x,y \in \Omega_M(t)$ with $|x-y| \le \delta$, then $u$ remains smooth on $[0,T_*]$. Equivalently, **if blowup occurs at $T_*$, then $\sup_{x,y \in \Omega_M(t), |x-y|\le\delta} \frac{|\xi(x,t)-\xi(y,t)|}{|x-y|^{1/2}} \to +\infty$ as $t \uparrow T_*$**. | **`KNOWN_THEOREM`** |
| **Layer 3 (The Unproved Heuristic Leap in `NS-OBS-021`)** | Asserting that at every amplifying time $t$, $|\nabla\xi(x,t)| \ge c\,\ell_\omega(x,t)^{-1}$ holds across the enstrophy-carrying core $\Omega_M(t)$ such that $\nu\int_{\Omega_+} |\omega|^2|\nabla\xi|^2\,dx \gtrsim P(t)$. | **NOT PROVED (`HEURISTIC_TENSION`)** |

### Why Layer 3 Is Not a Proved Structural Obstruction
1. **Hölder Exponent $1/2$ vs. Gradient Scaling**: Beirão da Veiga & Berselli (2002) proved that regularity holds even under $C^{1/2}$ direction coherence ($|\xi(x)-\xi(y)| \le C|x-y|^{1/2}$). Moreover, a supremum of $|\nabla\xi|$ blowing up at isolated collision points does **not** automatically imply that the $L^2(|\omega|^2\,dx)$-weighted average $\int_{\Omega_+} |\omega|^2|\nabla\xi|^2\,dx / \|\omega\|_2^2$ scales as $\bar{\ell}_\omega(t)^{-2}$!
2. **No Pointwise Lower Bound Theorem**: No theorem in the literature establishes $|\nabla\xi| \ge c\,\ell_\omega^{-1}$ as a necessary condition for instantaneous enstrophy growth $P(t) > D(t)$. For example, in a multi-shell resonant triad on $\mathbb{T}^3_L$ at $t=0$ with small viscosity $\nu \ll 1$, $P(0) > D(0)$ ($\mathcal{A}(0) \gg 1$) holds while $|\nabla\xi|$ is fixed at $O(1)$!

> **Mandatory Reclassification of `NS-OBS-021` (Section 13)**:
> Following the directive *"Disposition `NS-OBS-021` as one of `EXACT_IDENTITY_ONLY`, `HEURISTIC_TENSION`, `CONDITIONAL_OBSTRUCTION`, `PROVED_STRUCTURAL_OBSTRUCTION`. Use the weakest justified state"*, we reclassify `NS-OBS-021` (via prospective record `NS-OBS-021-R1`) as:
> $$\boxed{\texttt{HEURISTIC\_TENSION}}$$
> (recording that while Layer 1 is an `EXACT_IDENTITY_ONLY` and Layer 2 is a `KNOWN_THEOREM`, the quantitative competition between $\nu\int |\omega|^2|\nabla\xi|^2\,dx$ and $P(t)$ is currently a **heuristic tension** rather than a proved structural obstruction).

---

## 4. Beltrami / Lamb Vector Calculus Identity Audit (Section 14)

Let $u, \omega \in C^\infty(\mathbb{T}^3_L; \mathbb{R}^3)$ satisfy $\operatorname{div} u = 0$ and $\omega = \nabla \times u$ (so $\operatorname{div}\omega = 0$).
By the standard vector-calculus curl-of-cross-product expansion in $\mathbb{R}^3$:
$$\nabla \times (u \times \omega) = u(\operatorname{div}\omega) - \omega(\operatorname{div} u) + (\omega \cdot \nabla)u - (u \cdot \nabla)\omega = (\omega \cdot \nabla)u - (u \cdot \nabla)\omega.$$
Taking the inner product with $\omega$ and using $\omega \cdot (\omega \cdot \nabla)u = \omega_i \omega_j \partial_j u_i = \omega_i \omega_j S_{ij} = \omega \cdot S\omega$ and $\omega \cdot (u \cdot \nabla)\omega = u_j \omega_i \partial_j \omega_i = \frac{1}{2}(u \cdot \nabla)|\omega|^2$, we obtain:

$$\boxed{\omega \cdot S\omega - \frac{1}{2}(u \cdot \nabla)|\omega|^2 = \omega \cdot \big(\nabla \times (u \times \omega)\big)}$$

> **Classification (Section 14)**: This is a **`STANDARD_VECTOR_CALCULUS_IDENTITY`** (`KNOWN`). It is **not** promoted as a novel mathematical theorem.

---

## 5. Complete Verification of the Periodic Beltrami Counterexample (Section 15)

Let $u(\cdot,t) \in C^\infty_\sigma(\mathbb{T}^3_L)$ be a strong Beltrami field satisfying $\omega(x,t) = \lambda\,u(x,t)$ for a constant $\lambda \in \mathbb{R} \setminus \{0\}$ (such as the Arnold–Beltrami–Childress flow $u = (A\sin k_0 z + C\cos k_0 y,\, B\sin k_0 x + A\cos k_0 z,\, C\sin k_0 y + B\cos k_0 x)$ with $\lambda = k_0 = \frac{2\pi}{L}$ and $A,B,C \ne 0$).
1. **Vanishing of the Lamb Vector**:
   $$u(x,t) \times \omega(x,t) = u(x,t) \times \big(\lambda\,u(x,t)\big) = \mathbf{0} \quad \forall x \in \mathbb{T}^3_L.$$
2. **Exact Pointwise Stretching Formula**:
   Substituting $u \times \omega = \mathbf{0}$ into the identity of Section 4 gives:
   $$\omega(x,t) \cdot S(x,t)\omega(x,t) - \frac{1}{2}(u \cdot \nabla)|\omega(x,t)|^2 = \omega \cdot (\nabla \times \mathbf{0}) = 0 \implies \boxed{\omega(x,t) \cdot S(x,t)\omega(x,t) = \frac{1}{2}(u \cdot \nabla)|\omega(x,t)|^2}.$$
   When $A,B,C \ne 0$, $|\omega(x,t)|^2 = \lambda^2 |u(x,t)|^2$ is spatially non-constant and $(u \cdot \nabla)|\omega|^2 \not\equiv 0$, so **pointwise signed stretching $\omega \cdot S\omega = \lambda_\omega |\omega|^2$ takes strictly positive values on open subsets of $\mathbb{T}^3_L$**.
3. **Exact Vanishing of Global Production $P(t)$ on $\mathbb{T}^3_L$**:
   Integrating over the periodic torus $\mathbb{T}^3_L$ and applying the divergence theorem with periodic boundary conditions and $\operatorname{div} u = 0$:
   $$\int_{\mathbb{T}^3_L} (u \cdot \nabla)|\omega|^2\,dx = \int_{\mathbb{T}^3_L} \nabla \cdot \big(u\,|\omega|^2\big)\,dx - \int_{\mathbb{T}^3_L} (\operatorname{div} u)\,|\omega|^2\,dx = 0 - 0 = 0.$$
   Therefore:
   $$\boxed{P(t) = \int_{\mathbb{T}^3_L} \omega(x,t) \cdot S(x,t)\omega(x,t)\,dx = \frac{1}{2}\int_{\mathbb{T}^3_L} (u \cdot \nabla)|\omega(x,t)|^2\,dx = 0 \implies \mathcal{A}(t) = 0}.$$

> **Verdict (Section 15)**: The calculation passes completely and is **retained as a valid analytical falsification (`NEG-EV-047`)** of naive pointwise stretching diagnostics that fail to subtract spatial enstrophy advection $\frac{1}{2}(u\cdot\nabla)|\omega|^2$.
