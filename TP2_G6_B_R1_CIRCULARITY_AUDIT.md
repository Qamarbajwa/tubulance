# TP2-G6-B-R1: Circularity Firewall and Regularity Equivalence Audit

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R1 (Work Package 5 / Circularity Firewall)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Bridge:** `B1 — Non-Circular Xi Control`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. The Principle of Non-Circularity

Under Mathematical Research Constitution v1.0.1 (§3 & §12), any candidate mathematical estimate or structural obstruction proposed to advance Bridge $B_1$ or Bridge $B_3$ must pass a strict **Circularity Audit**.

A derivation is classified as **CIRCULAR FOR GLOBAL REGULARITY** if it imports, explicitly or implicitly, any hypothesis that is already known to be equivalent to smooth continuation past a singularity time $T_*$. Such results may be mathematically valid identities, but they provide **zero closure** toward resolving Clay Statement B.

---

## 2. Catalog of Prohibited Circularity Anchors

The following regularity criteria are established in the literature as continuation-equivalent and are strictly quarantined from serving as foundational hypotheses in `TP2-G6`:

| Anchor ID | Mathematical Anchor | Literature Formulation | Regularity Equivalence |
|---|---|---|---|
| **`CIRC-001`** | **Beale–Kato–Majda Criterion** | $\int_0^{T_*} \|\omega(t)\|_{L^\infty} dt < \infty$ | BKM (1984); Kato (1984). Equivalent to global smoothness on $[0, T_*]$. |
| **`CIRC-002`** | **Serrin / Prodi–Serrin Integrability** | $u \in L^p(0, T_*; L^q(\mathbb{T}^3)), \quad \frac{2}{p} + \frac{3}{q} \le 1$ | Serrin (1962); Ladyzhenskaya (1967). Guarantees smoothness on $[0, T_*]$. |
| **`CIRC-003`** | **Escauriaza–Seregin–Šverák Endpoint** | $u \in L^\infty(0, T_*; L^3(\mathbb{T}^3))$ | ESS (2003). Endpoint critical space; blowup equivalent to $L^3$ divergence. |
| **`CIRC-004`** | **$L^1_t L^\infty_x$ Strain History** | $\int_0^{T_*} \|S(t)\|_{L^\infty} dt < \infty$ | Controlling strain history bounds deformation and vorticity by Gronwall; BKM-equivalent. |
| **`CIRC-005`** | **A-Priori Smoothness Radius Bounds** | $\rho_{\text{analyticity}}(t) \ge c_0 > 0$ as $t \to T_*$ | Grujić (2001). Non-vanishing analyticity radius excludes singularity directly. |
| **`CIRC-006`** | **Uniform Pressure Hessian Control** | $\sup_{t \in [0, T_*]} \|\operatorname{Hess}(p)(t)\|_{L^\infty} < \infty$ | Unboundedness of $\nabla^2 p$ is necessary for finite-time singularity. |
| **`CIRC-007`** | **A-Priori Bound on Deformation Tensor** | $\sup_{x \in \mathbb{T}^3} \|D_{0, T_*}(x)\| < \infty$ | Bounded Lagrangian deformation implies bounded strain history. |

---

## 3. Audit of TP2-G6-B-R1 Work Packages Against the Firewall

### 3.1 WP1 (Branch-R Definition)
- **Inputs:** Uses only the local vorticity amplitude $M_n = |\omega(x_n, t_n)|$ and the intrinsic window $L_n = a/M_n$.
- **Circularity Check:** **PASS**. Branch R is defined as a purely local-in-time asymptotic target ($\lim J_n(a) = 0$). It does not assume BKM or Serrin integrability.

### 3.2 WP2 (Flow Family Matrix)
- **Inputs:** Exact periodic shear flows and decaying Beltrami flows on $\mathbb{T}^3$.
- **Circularity Check:** **PASS**. Both families are exact, unconditionally global smooth Navier–Stokes solutions. Their properties ($\omega \cdot S \omega = 0$, $C_s$ rank deficiency) are rigorous algebraic facts, not conditional on unproved regularity.

### 3.3 WP3 (Scaling Audit)
- **Inputs:** Parabolic dilation $u_\lambda = \lambda u(\lambda x, \lambda^2 t)$ and the exact vorticity-gradient transport equation $(D_t - \nu \Delta)G = SG - GA + T$.
- **Circularity Check:** **PASS**. Parabolic invariance $J_\lambda(a) \equiv J_0(a)$ is an exact symmetry property of the Navier–Stokes equations. The gradient injection bound $\|T\| \gtrsim M_n^2 / \ell_n$ is derived directly from the Biot–Savart singular integral kernel without assuming strain bounds.

### 3.4 WP4 (Covariance Spectral Audit)
- **Inputs:** Direct integration of the matrix outer product $(D_r J_\omega)(D_r J_\omega)^\top$ for periodic shear.
- **Circularity Check:** **PASS**. The exact rank-1 degeneracy $\lambda_2(C_s) = \lambda_3(C_s) \equiv 0$ is proved unconditionally for all non-trivial periodic shear solutions.

---

## 4. Circularity Boundary for Future Bridge Work

Any candidate lemma proposed to establish a lower bound $\mathbb{E}_{\mu_r}[\Xi_r] \ge c_0 > 0$ along Branch R must be evaluated against the following strict criterion:

$$\boxed{ \text{\textbf{Constitutional Rule:}} \quad \text{If the proof of } \mathbb{E}_{\mu_r}[\Xi_r] \ge c_0 \text{ relies on } \int_0^T \|S\|_{L^\infty} dt < \infty \text{ or } \|\omega\|_{L^\infty} < \infty, \text{ it is CIRCULAR and cannot close Bridge } B_1. }$$
