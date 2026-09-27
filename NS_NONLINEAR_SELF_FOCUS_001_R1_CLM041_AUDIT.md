# NS_NONLINEAR_SELF_FOCUS_001_R1_CLM041_AUDIT

## Adversarial Normalization, Zero/Sign Case Split, Poincaré Constant Repair, and Reclassification of `CLM-041` (`NS-NONLINEAR-SELF-FOCUS-001-R1`)

| Field | Value |
| :--- | :--- |
| **Milestone ID** | `NS-NONLINEAR-SELF-FOCUS-001-R1` |
| **Parent Milestone** | `NS-NONLINEAR-SELF-FOCUS-001` (Historical artifacts preserved unchanged) |
| **Active Governance** | `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3` (`NS-GOV-MIG-V404-001 = MIGRATION_BLOCKED`) |
| **Mathematical Authority** | `Mathematical Research Constitution v1.0.1` |
| **Locked Target** | $\mathbb{T}^3_L = (\mathbb{R}/L\mathbb{Z})^3$, $\nu > 0$, $f \equiv 0$ |
| **Immutable Hard Gates** | `Clay Statement B = UNRESOLVED`, `Release = NO-GO`, `Deployment Authority = NONE`, `NS-OPENAI-B2 = BLOCKED` |
| **`CLM-041` Reclassification** | **`CLM041_PROJECT_REFORMULATION`** (Prospective replacement `CLM-041-R1` narrowed to `PROVED_LEMMA` / `N1_PROJECT_REFORMULATION` / `S1_USEFUL_LEMMA`) |
| **Reassessed Milestone Verdict** | **`KNOWN_THEORY_REFORMULATION_WITH_NEW_RESEARCH_PROGRAM`** (with `FOUNDATION_VALID_THEOREM_NOT_YET_FOUND`) |

---

## 1. Executive Answer to the Final Controlling Question

$$\boxed{\begin{aligned}
&\textbf{Controlling Question: }\text{Does CLM-041 contain a genuinely new dynamical restriction on}\\
&\text{forward Navier–Stokes concentration, or is it principally an exact reparameterization}\\
&\text{of known enstrophy, strain and length-scale relations?}
\end{aligned}}$$

**Direct Adversarial Answer:**
`CLM-041` is **principally an exact algebraic, variational, and Plancherel–Markov reparameterization of known enstrophy, strain, and Foias–Temam length-scale relations**, combined with a standard vector-calculus identity for the Lamb vector curl. It **does not** establish a new dynamical restriction on 3D Navier–Stokes solutions beyond the classical global enstrophy balance $\frac{1}{2}\frac{d}{dt}\|\omega\|_2^2 = P(t) - D(t)$ and kinematic Sobolev/Fourier inequalities valid for arbitrary divergence-free vector fields.

Specifically:
1. **Part (1)** ($\mathcal{A} = \frac{\bar{\lambda}_\omega\bar{\ell}_\omega^2}{\nu}$) is an **exact algebraic tautology of definitions** obtained by multiplying and dividing $P(t)/D(t)$ by $\|\omega(t)\|_{L^2}^2$.
2. **Part (2)** ($\bar{\ell}_\omega \ge \sqrt{\nu\mathcal{A}/\lambda_1^+}$ and $\bar{\ell}_\omega \le \lambda_{\rm P}^{-1/2}$) combines the elementary pointwise Rayleigh quotient bound $\omega \cdot S\omega \le \lambda_{\max}(S)|\omega|^2$ (`STANDARD_COROLLARY`) with the mean-zero Poincaré inequality on $\mathbb{T}^3_L$ (`KNOWN`). Furthermore, the original wording wrote $\bar{\ell}_\omega \le 1$ without fixing $\lambda_{\rm P} = (2\pi/L)^2 = 1$ ($L = 2\pi$) and omitted explicit positivity preconditions ($D(t) > 0, P(t) > 0, \lambda_1^+(t) > 0$).
3. **Part (3)** ($\sum_{q \ge Q_*(t)} \nu\|\nabla \dot{\Delta}_q \omega\|_2^2 \ge \frac{1}{2}D(t)$) is a **static Markov/Chebyshev tail inequality on the Plancherel measure** $|\hat{\omega}(k)|^2$ for the threshold wavenumber $2^{2 Q_*(t)} \le \frac{1}{2\bar{\ell}_\omega(t)^2} = \frac{\|\nabla\omega\|_2^2}{2\|\omega\|_2^2}$. It holds for *any* $H^1$ periodic field independent of the Navier–Stokes equations, requires an **orthogonal** dyadic shell projection (rather than a non-orthogonal smooth Littlewood–Paley partition where $\sum_q \hat{\psi}_q(k)^2 \ne 1$), and its time-derivative corollary improperly ignored integer-jump discontinuities of $Q_*(t)$ and suppressed inter-shell commutator cross-terms.
4. **Part (4)** ($\omega \cdot S\omega - \frac{1}{2}(u\cdot\nabla)|\omega|^2 = \omega \cdot \nabla \times (u \times \omega)$) is a **standard vector-calculus identity** for solenoidal fields. Its value lies in falsifying naive pointwise stretching diagnostics on non-constant ABC Beltrami flows (`NEG-EV-047`), not as a novel PDE theorem.

---

## 2. Frozen Copy of Registered `CLM-041` (Section 2)

The exact statement of `CLM-041` as registered in `mathematical_constitution/CLAIM_REGISTRY.yaml` (commit `77e5f6c51c1873b44f10892ca94e2e3ab070d163`) is frozen below verbatim for audit:

> **`claim_id`**: `"CLM-041"`
> **`claim_type`**: `"MATHEMATICAL_PROPOSITION"`
> **`name`**: `"CONDITIONAL_SCALE_SHRINKING_ENSTROPHY_AMPLIFICATION_AND_DYADIC_BOUND"`
> **`milestone`**: `"NS-NONLINEAR-SELF-FOCUS-001"`
> **`statement`**: `"For any smooth unforced solution u in C^infty([0,T] x T^3) of 3D incompressible Navier-Stokes with nu > 0, f = 0, and ||omega(t)||_{L^2(T^3)} > 0, let bar_ell_omega(t) = ||omega(t)||_{L^2} / ||grad omega(t)||_{L^2} in (0, 1] be the global active dissipation length scale and bar_lambda_omega(t) = P(t) / ||omega(t)||_{L^2}^2 be the enstrophy-weighted signed stretching rate. Then: (1) A(t) = P(t)/D(t) = bar_lambda_omega(t) bar_ell_omega(t)^2 / nu is an exact identity; (2) whenever instantaneous enstrophy growth occurs (A(t) > 1), the positive stretching rate lambda_1^+(t) satisfies lambda_1^+(t) bar_ell_omega(t)^2 / nu >= A(t) > 1, bracketing bar_ell_omega(t) in [sqrt(nu A(t) / lambda_1^+(t)), 1]; (3) at least half of the global palinstrophy dissipation D(t) resides in dyadic shells q >= Q_*(t) = max(0, floor((1/2) log_2(1 / (2 bar_ell_omega(t)^2)))), requiring high-shell nonlinear production sum_{q >= Q_*} (T_q^{adv} + P_q^{stretch}) >= D(t)/2 whenever high-shell enstrophy is non-decreasing; and (4) the Beltrami-subtracted Lagrangian production omega . S omega - (1/2)(u . grad)|omega|^2 = omega . (curl(u x omega)) vanishes identically on all Beltrami/ABC flows while integrating globally to P(t)."`
> **`passport`**: `truth_status: PROVED_THEOREM`, `novelty: N1_PROJECT_REFORMULATION`, `significance: S2_MAJOR_PROJECT_RESULT`.

### Audit Inventory of Frozen `CLM-041` Attributes
- **Quantifiers & Regularity**: $\forall u \in C^\infty([0,T]\times\mathbb{T}^3)$ solving unforced incompressible NS with $\nu > 0, f = 0$, at times $t \in [0,T]$ where $\|\omega(t)\|_{L^2(\mathbb{T}^3)} > 0$.
- **Unstated Domain Normalization Defect**: Assumed $\mathbb{T}^3 = (\mathbb{R}/2\pi\mathbb{Z})^3$ ($L = 2\pi \implies \lambda_{\rm P} = 1$) in writing $\bar{\ell}_\omega(t) \in (0, 1]$ and $Q_*(t) = \max(0, \lfloor \frac{1}{2}\log_2(1/(2\bar{\ell}_\omega^2))\rfloor)$ without stating the dependence on arbitrary torus period $L > 0$.
- **Zero/Sign Precondition Gaps**: Defined $\lambda_1^+(t)$ using $\lambda_\omega(x,t) = \xi^\top S \xi$ without handling the nodal zero set $\{x : |\omega(x,t)| = 0\}$ where $\xi$ is undefined, and wrote $\sqrt{\nu\mathcal{A}(t)/\lambda_1^+(t)}$ under $\mathcal{A}(t) > 1$ without explicitly proving first that $\mathcal{A}(t) > 0 \implies P(t) > 0 \implies \lambda_1^+(t) > 0$.
- **Dyadic Partition Ambiguity**: Used $\dot{\Delta}_q$ without specifying whether $\dot{\Delta}_q$ is a sharp $L^2$-orthogonal shell projector ($\sum_{q \ge 0} |\hat{\psi}_q(k)|^2 \equiv 1$) or a smooth overlapping Littlewood–Paley partition of unity ($\sum_{q \ge 0} \hat{\psi}_q(k) \equiv 1$, where $\sum_q \|\nabla \dot{\Delta}_q \omega\|_2^2 \ne \|\nabla\omega\|_2^2$).

---

## 3. Reconstruction of Definitions and Algebraic Tautology Audit (Section 3)

Let $\mathbb{T}^3_L := (\mathbb{R}/L\mathbb{Z})^3$ be the three-dimensional periodic torus of side length $L > 0$. For any smooth divergence-free velocity field $u(\cdot,t) \in C^\infty_\sigma(\mathbb{T}^3_L)$ with vorticity $\omega = \nabla \times u$ and strain rate tensor $S = \frac{1}{2}(\nabla u + \nabla u^\top)$:

1. **Global Vortex Stretching Production**:
   $$P(t) := \int_{\mathbb{T}^3_L} \omega(x,t) \cdot S(x,t)\omega(x,t)\,dx \in \mathbb{R}.$$
2. **Global Palinstrophy Dissipation**:
   $$D(t) := \nu \int_{\mathbb{T}^3_L} |\nabla\omega(x,t)|^2\,dx = \nu \|\nabla\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 \ge 0.$$
3. **Global Enstrophy Amplification Ratio** (defined strictly on $\{t \in [0,T] : D(t) > 0\}$):
   $$\mathcal{A}(t) := \frac{P(t)}{D(t)} \in \mathbb{R}.$$
4. **Enstrophy-Weighted Signed Stretching Rate** (defined strictly on $\{t \in [0,T] : \|\omega(t)\|_{L^2(\mathbb{T}^3_L)} > 0\}$):
   $$\bar{\lambda}_\omega(t) := \frac{P(t)}{\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2} \in \mathbb{R}.$$
5. **Global Foias–Temam Vorticity Length Scale** (defined strictly on $\{t \in [0,T] : \|\nabla\omega(t)\|_{L^2(\mathbb{T}^3_L)} > 0\}$):
   $$\bar{\ell}_\omega(t) := \frac{\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}}{\|\nabla\omega(t)\|_{L^2(\mathbb{T}^3_L)}} > 0, \qquad \bar{\ell}_\omega(t)^2 = \frac{\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2}{\|\nabla\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2}.$$

### Explicit Recognition of Algebraic Factorization (`DEFINITION_FACTORIZATION`)
Whenever $\|\omega(t)\|_{L^2(\mathbb{T}^3_L)} > 0$ (which on $\mathbb{T}^3_L$ automatically implies $\|\nabla\omega(t)\|_{L^2(\mathbb{T}^3_L)} > 0$ and $D(t) > 0$ because $\int_{\mathbb{T}^3_L} \omega\,dx = \mathbf{0}$), substituting the definitions of $\bar{\lambda}_\omega(t)$ and $\bar{\ell}_\omega(t)^2$ gives:

$$\frac{\bar{\lambda}_\omega(t)\,\bar{\ell}_\omega(t)^2}{\nu} = \frac{1}{\nu} \left(\frac{P(t)}{\|\omega(t)\|_{L^2}^2}\right) \left(\frac{\|\omega(t)\|_{L^2}^2}{\|\nabla\omega(t)\|_{L^2}^2}\right) = \frac{P(t)}{\nu\,\|\nabla\omega(t)\|_{L^2}^2} = \frac{P(t)}{D(t)} = \mathcal{A}(t).$$

> **Mandatory Classification (Section 3)**:
> The relation $\mathcal{A}(t) = \frac{\bar{\lambda}_\omega(t)\bar{\ell}_\omega(t)^2}{\nu}$ is an **exact algebraic factorization of definitions** (`EXACT_DEFINITION_IDENTITY` / `PROJECT_REPARAMETRIZATION`). It holds for any twice-differentiable vector field with non-zero curl on $\mathbb{T}^3_L$, requires zero PDE dynamics, and **must not be classified as a Navier–Stokes dynamical theorem**.

---

## 4. Complete Zero and Sign Case Split (Section 4)

To prevent division by zero, imaginary square roots, or undefined unit vectors, we partition all possible states at time $t \in [0,T]$ into five exhaustive, mutually exclusive regimes:

| Case | Defining Condition | Status of $\|\omega\|_2, D(t)$ | Status of $P(t), \mathcal{A}(t), \bar{\lambda}_\omega(t)$ | Status of $\lambda_1^+(t)$ and Bracket $\sqrt{\nu\mathcal{A}/\lambda_1^+}$ |
| :--- | :--- | :--- | :--- | :--- |
| **Case 0 (Trivial / Rest Flow)** | $\omega(\cdot,t) \equiv \mathbf{0}$ on $\mathbb{T}^3_L$ | $\|\omega\|_2 = 0$, $D(t) = 0$ (since $u$ is spatially constant $u \equiv \bar{u}$) | $P(t) = 0$. Quotients $\mathcal{A}(t), \bar{\lambda}_\omega(t), \bar{\ell}_\omega(t)$ are **undefined ($0/0$)**. | $S \equiv 0 \implies \lambda_1^+(t) = 0$. Expression $\sqrt{\nu\mathcal{A}/\lambda_1^+}$ is **undefined** and prohibited. |
| **Case I (Negative Production / Net Compression)** | $\|\omega\|_2 > 0$ and $P(t) < 0$ | $\|\omega\|_2 > 0$, $D(t) > 0$, $\bar{\ell}_\omega(t) \in (0, \lambda_{\rm P}^{-1/2}]$ well-defined | $P(t) < 0 \iff \bar{\lambda}_\omega(t) < 0 \iff \mathcal{A}(t) < 0$. Global enstrophy strictly decays ($\frac{1}{2}\frac{d}{dt}\|\omega\|_2^2 = P - D < -D < 0$). | $\lambda_1^+(t) \ge 0$. Because $\mathcal{A}(t) < 0$, $\frac{\nu\mathcal{A}}{\lambda_1^+} \le 0$, so **$\sqrt{\nu\mathcal{A}/\lambda_1^+}$ is non-real or zero and MUST NOT BE USED**. |
| **Case II (Zero Global Production)** | $\|\omega\|_2 > 0$ and $P(t) = 0$ (e.g., 2D flows, pure shear, Beltrami/ABC flows, Taylor–Green at $t=0$) | $\|\omega\|_2 > 0$, $D(t) > 0$, $\bar{\ell}_\omega(t) \in (0, \lambda_{\rm P}^{-1/2}]$ well-defined | $P(t) = 0 \iff \bar{\lambda}_\omega(t) = 0 \iff \mathcal{A}(t) = 0$. Global enstrophy decays purely diffusively ($\frac{1}{2}\frac{d}{dt}\|\omega\|_2^2 = -D < 0$). | Either $\lambda_1^+(t) > 0$ ( yielding trivial lower bound $\sqrt{\nu\cdot 0/\lambda_1^+} = 0 < \bar{\ell}_\omega$) or $\lambda_1^+(t) = 0$ ($0/0$ undefined). Formula $\sqrt{\nu\mathcal{A}/\lambda_1^+}$ is restricted out of Case II. |
| **Case III (Subcritical Positive Production)** | $\|\omega\|_2 > 0$ and $0 < P(t) \le D(t)$ | $\|\omega\|_2 > 0$, $D(t) > 0$ | $0 < \mathcal{A}(t) \le 1$ and $\bar{\lambda}_\omega(t) > 0$. Enstrophy is non-increasing ($\frac{d}{dt}\|\omega\|_2^2 \le 0$). | Since $P(t) > 0$, Theorem 5.1 below proves $\lambda_1^+(t) \ge \bar{\lambda}_\omega(t) > 0$ strictly! Hence $\sqrt{\nu\mathcal{A}(t)/\lambda_1^+(t)} \in (0, \bar{\ell}_\omega(t)]$ is **real, finite, and strictly positive**. |
| **Case IV (Supercritical Positive Production / Amplification)** | $\|\omega\|_2 > 0$ and $P(t) > D(t) > 0$ | $\|\omega\|_2 > 0$, $D(t) > 0$ | $\mathcal{A}(t) > 1$ and $\bar{\lambda}_\omega(t) > \nu/\bar{\ell}_\omega(t)^2 > 0$. Global enstrophy strictly grows ($\frac{d}{dt}\|\omega\|_2^2 > 0$). | $\lambda_1^+(t) \ge \bar{\lambda}_\omega(t) > 0$ strictly. Both $\frac{\lambda_1^+(t)\bar{\ell}_\omega(t)^2}{\nu} \ge \mathcal{A}(t) > 1$ and $\sqrt{\frac{\nu\mathcal{A}(t)}{\lambda_1^+(t)}} \le \bar{\ell}_\omega(t) \le \lambda_{\rm P}^{-1/2}$ are **unconditionally well-defined, real, and positive**. |

---

## 5. Precise Definition of $\lambda_1^+(t)$ and Proof of $\bar{\lambda}_\omega(t) \le \lambda_1^+(t)$ (Section 5)

### Definition 5.1 (Canonical Strain vs. Vorticity-Support Definitions of $\lambda_1^+(t)$)
To eliminate all ambiguity on the vorticity zero set $\mathcal{Z}_\omega(t) := \{x \in \mathbb{T}^3_L : \omega(x,t) = \mathbf{0}\}$, we distinguish two precise quantities:

1. **Global Maximum Strain Eigenvalue** $\lambda_{\max,S}^+(t)$ (defined everywhere without reference to $\xi$):
   $$\lambda_{\max,S}^+(t) := \sup_{x \in \mathbb{T}^3_L} \max\big(\lambda_{\max}(S(x,t)),\, 0\big) = \sup_{x \in \mathbb{T}^3_L} \lambda_1(x,t),$$
   where $\lambda_1(x,t) \ge \lambda_2(x,t) \ge \lambda_3(x,t)$ are the ordered real eigenvalues of the symmetric trace-free matrix $S(x,t)$. Note that because $\lambda_1(x,t) + \lambda_2(x,t) + \lambda_3(x,t) = \operatorname{div} u(x,t) = 0$, we have $\lambda_1(x,t) \ge \frac{1}{3}(\lambda_1+\lambda_2+\lambda_3) = 0$ at **every** point $x \in \mathbb{T}^3_L$! Thus $\max(\lambda_1(x,t), 0) = \lambda_1(x,t) \ge 0$ identically!
2. **Active Vorticity-Support Directional Stretching Supremum** $\lambda_{1,\omega}^+(t)$ (defined on $\Omega_+(t) := \{x \in \mathbb{T}^3_L : |\omega(x,t)| > 0\}$):
   $$\lambda_{1,\omega}^+(t) := \sup_{x \in \Omega_+(t)} \max\!\left(\frac{\omega(x,t) \cdot S(x,t)\omega(x,t)}{|\omega(x,t)|^2},\, 0\right).$$

### Proposition 5.2 (Exact Ordering, Positivity, and Equality Conditions)
For any smooth divergence-free field $u(\cdot,t)$ on $\mathbb{T}^3_L$ with $\|\omega(t)\|_{L^2(\mathbb{T}^3_L)} > 0$:
$$\boxed{\bar{\lambda}_\omega(t) \le \max\big(\bar{\lambda}_\omega(t), 0\big) \le \lambda_{1,\omega}^+(t) \le \lambda_{\max,S}^+(t)}$$

**Proof:**
1. On the open non-empty set $\Omega_+(t) = \{|\omega(\cdot,t)| > 0\}$, the unit vector $\xi(x,t) = \omega(x,t)/|\omega(x,t)| \in \mathbb{S}^2$ is smooth, and by the Courant–Fischer variational theorem for symmetric matrices:
   $$\lambda_\omega(x,t) := \frac{\omega(x,t)\cdot S(x,t)\omega(x,t)}{|\omega(x,t)|^2} = \xi(x,t)^\top S(x,t)\xi(x,t) \le \max_{|\eta|=1} \eta^\top S(x,t)\eta = \lambda_1(x,t) \le \lambda_{\max,S}^+(t).$$
   Taking $\max(\cdot, 0)$ and the supremum over $x \in \Omega_+(t)$ proves $\lambda_{1,\omega}^+(t) \le \lambda_{\max,S}^+(t)$.
2. On the complement $\mathcal{Z}_\omega(t) = \{|\omega(\cdot,t)| = 0\}$, the integrand $\omega(x,t) \cdot S(x,t)\omega(x,t)$ equals $0$ identically. Therefore, the global production integral over $\mathbb{T}^3_L$ restricts cleanly to $\Omega_+(t)$:
   $$P(t) = \int_{\mathbb{T}^3_L} \omega \cdot S\omega\,dx = \int_{\Omega_+(t)} \lambda_\omega(x,t)\,|\omega(x,t)|^2\,dx \le \int_{\Omega_+(t)} \lambda_{1,\omega}^+(t)\,|\omega(x,t)|^2\,dx = \lambda_{1,\omega}^+(t)\,\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2.$$
   Dividing by $\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 > 0$ gives $\bar{\lambda}_\omega(t) \le \lambda_{1,\omega}^+(t) \le \lambda_{\max,S}^+(t)$.
3. **Strict Positivity when $P(t) > 0$**: If $P(t) > 0$ (Cases III and IV, in particular whenever $\mathcal{A}(t) > 0$), then $0 < \bar{\lambda}_\omega(t) \le \lambda_{1,\omega}^+(t) \le \lambda_{\max,S}^+(t)$, so **both $\lambda_{1,\omega}^+(t) > 0$ and $\lambda_{\max,S}^+(t) > 0$ are strictly positive**!
4. **Equality and Degeneracy Cases**:
   - $\bar{\lambda}_\omega(t) = \lambda_{1,\omega}^+(t)$ holds if and only if $\lambda_\omega(x,t)$ is a non-negative constant $c \ge 0$ on the entire support $\Omega_+(t)$ (which occurs trivially with $c = 0$ in 2D/shear flows where $S\omega \equiv \mathbf{0}$, and cannot occur with $c > 0$ on $\mathbb{T}^3_L$ for smooth periodic flows with stagnation points where $S(x_0,t) = 0$).
   - $\lambda_{1,\omega}^+(t) = \lambda_{\max,S}^+(t)$ holds if and only if the global maximum of $\lambda_1(x,t)$ on $\mathbb{T}^3_L$ is attained at a point $x_* \in \overline{\Omega_+(t)}$ where $\xi(x_*,t) = \pm \mathbf{e}_1(x_*,t)$ is perfectly aligned with the leading eigenvector of $S(x_*,t)$. $\blacksquare$

---

## 6. Repair of the Poincaré Constant on $\mathbb{T}^3_L$ (Section 6)

Let $\mathbb{T}^3_L = (\mathbb{R}/L\mathbb{Z})^3$ have period $L > 0$ in each coordinate direction. The Fourier expansion of $\omega(\cdot,t)$ is:
$$\omega(x,t) = \sum_{k \in \frac{2\pi}{L}\mathbb{Z}^3 \setminus \{\mathbf{0}\}} \hat{\omega}(k,t)\,e^{i k \cdot x},$$
where the $k = \mathbf{0}$ mode vanishes identically because $\int_{\mathbb{T}^3_L} \omega(x,t)\,dx = \int_{\mathbb{T}^3_L} (\nabla \times u)\,dx = \mathbf{0}$.

The first positive eigenvalue of the negative Laplacian $-\Delta$ on mean-zero periodic functions on $\mathbb{T}^3_L$ is attained at the six fundamental wavevectors $k \in \big\{(\pm \frac{2\pi}{L}, 0, 0), (0, \pm \frac{2\pi}{L}, 0), (0, 0, \pm \frac{2\pi}{L})\big\}$ and equals:

$$\boxed{\lambda_{\rm P}(L) = \left(\frac{2\pi}{L}\right)^2}$$

By Plancherel's identity on $\mathbb{T}^3_L$:
$$\|\nabla\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 = L^3 \sum_{k \ne \mathbf{0}} |k|^2\,|\hat{\omega}(k,t)|^2 \ge \left(\frac{2\pi}{L}\right)^2 L^3 \sum_{k \ne \mathbf{0}} |\hat{\omega}(k,t)|^2 = \lambda_{\rm P}(L)\,\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2.$$
Taking the reciprocal and square root yields the **Exact Normalized Upper Bound on $\bar{\ell}_\omega(t)$**:

$$\boxed{\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 \le \lambda_{\rm P}(L)^{-1}\,\|\nabla\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 \implies \bar{\ell}_\omega(t) \le \lambda_{\rm P}(L)^{-1/2} = \frac{L}{2\pi}}$$

- **Equality condition**: $\bar{\ell}_\omega(t) = \lambda_{\rm P}(L)^{-1/2} = \frac{L}{2\pi}$ holds if and only if $\hat{\omega}(k,t)$ is supported exclusively on the lowest wavenumber shell $|k| = \frac{2\pi}{L}$.
- **Reduction to $1$**: The bound $\bar{\ell}_\omega(t) \le 1$ is valid **if and only if the torus side length is normalized to $L = 2\pi$** (so that $\mathbb{T}^3 = (\mathbb{R}/2\pi\mathbb{Z})^3$ and $\lambda_{\rm P}(2\pi) = 1$). On a unit torus $\mathbb{T}^3_1 = (\mathbb{R}/\mathbb{Z})^3$ ($L = 1$), $\lambda_{\rm P}(1) = 4\pi^2$ and $\bar{\ell}_\omega(t) \le \frac{1}{2\pi} \approx 0.15915$. All project statements must henceforth write $\lambda_{\rm P}^{-1/2} = \frac{L}{2\pi}$ explicitly.

---

## 7. Audit of the Lower Length-Scale Bound (Section 7)

In Cases III and IV ($\|\omega(t)\|_{L^2(\mathbb{T}^3_L)} > 0$ and $P(t) > 0$, so $\mathcal{A}(t) > 0$ and $\lambda_1^+(t) \ge \bar{\lambda}_\omega(t) > 0$), combining the algebraic factorization $\mathcal{A}(t) = \frac{\bar{\lambda}_\omega(t)\bar{\ell}_\omega(t)^2}{\nu}$ with $\bar{\lambda}_\omega(t) \le \lambda_1^+(t)$ (for either $\lambda_1^+ = \lambda_{1,\omega}^+$ or $\lambda_1^+ = \lambda_{\max,S}^+$) gives:
$$\mathcal{A}(t) = \frac{\bar{\lambda}_\omega(t)\,\bar{\ell}_\omega(t)^2}{\nu} \le \frac{\lambda_1^+(t)\,\bar{\ell}_\omega(t)^2}{\nu} \implies \boxed{\bar{\ell}_\omega(t)^2 \ge \frac{\nu\,\mathcal{A}(t)}{\lambda_1^+(t)} \implies \sqrt{\frac{\nu\,\mathcal{A}(t)}{\lambda_1^+(t)}} \le \bar{\ell}_\omega(t) \le \lambda_{\rm P}^{-1/2}}$$

### Epistemic Classification of the Lower Bound (Section 7)
Is $\bar{\ell}_\omega(t)^2 \ge \frac{\nu\mathcal{A}(t)}{\lambda_1^+(t)}$ a new theorem, a direct algebraic corollary, a known strain/enstrophy estimate, or a diagnostic reformulation?
- Mathematically, multiplying both sides by $D(t) = \nu\|\nabla\omega\|_2^2$ and $\lambda_1^+(t)$ shows that $\bar{\ell}_\omega^2 \ge \frac{\nu\mathcal{A}}{\lambda_1^+}$ is **algebraically identical** to:
  $$\frac{\|\omega\|_2^2}{\|\nabla\omega\|_2^2} \ge \frac{\nu\,(P / (\nu\|\nabla\omega\|_2^2))}{\lambda_1^+} = \frac{P}{\lambda_1^+\,\|\nabla\omega\|_2^2} \iff P(t) \le \lambda_1^+(t)\,\|\omega(t)\|_{L^2}^2!$$
- That is, after cancelling $\nu\|\nabla\omega\|_2^2$ from numerator and denominator, the lower bound $\bar{\ell}_\omega(t)^2 \ge \frac{\nu\mathcal{A}(t)}{\lambda_1^+(t)}$ is **100% equivalent to the elementary Rayleigh–Ritz bound $P(t) \le \lambda_1^+(t)\|\omega(t)\|_{L^2}^2$ divided by $D(t)$**!
- Therefore, it is classified strictly as a **`DIRECT_ALGEBRAIC_COROLLARY` / `DIAGNOSTIC_REFORMULATION` of the classical strain-eigenvalue enstrophy production bound** (Ponce 1985; Foias–Temam 1989; Constantin 1994), **not** a new PDE theorem.

---

## 8. Formal Reclassification Decision (`CLM-041` $\to$ `CLM-041-R1`, Sections 17, 18, 19)

1. **Section 18 Reclassification Choice for `CLM-041`**:
   $$\boxed{\texttt{CLM041\_PROJECT\_REFORMULATION} \quad (\text{Prospective Registry Entry } \texttt{CLM-041-R1}: \texttt{PROVED\_LEMMA}, \; \texttt{N1\_PROJECT\_REFORMULATION}, \; \texttt{S1\_USEFUL\_LEMMA})}$$
   - **Mathematical Correctness**: True when normalized with $\lambda_{\rm P} = (2\pi/L)^2$, explicit positivity preconditions $P(t) > 0$, and an $L^2$-orthogonal dyadic shell decomposition.
   - **Novelty**: `N1_PROJECT_REFORMULATION` (algebraic synthesis of Foias–Temam quotient $\bar{\ell}_\omega$, Rayleigh–Ritz strain bound $P \le \lambda_1^+\|\omega\|_2^2$, Plancherel–Markov tail inequality, and vector-calculus Lamb-curl identity).
   - **Dynamical Leverage**: **Low as a standalone bound** (does not constrain Navier–Stokes trajectories beyond the classical global enstrophy balance), **High as a falsification filter and coordinate system** for formulating the next genuine dynamical dyadic transfer problem (`Section 23`).

2. **Section 19 Reassessed Milestone Verdict**:
   $$\boxed{\texttt{KNOWN\_THEORY\_REFORMULATION\_WITH\_NEW\_RESEARCH\_PROGRAM}}$$
   *(with companion epistemic status `FOUNDATION_VALID_THEOREM_NOT_YET_FOUND`, replacing the preliminary `PROMISING_SCALE_LOCAL_ROUTE` label until a genuinely dynamical inter-shell concentration theorem is proved).*
