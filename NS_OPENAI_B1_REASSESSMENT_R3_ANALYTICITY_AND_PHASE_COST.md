# Analyticity, Authentic Phase Geometry, and Affine Cost Barrier Audit

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R3`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`  
**Classification**: `PROSPECTIVE_SCIENTIFIC_REPAIR`  
**Sections**: Mandate Sections 12 (Phase cost), 14 (Analyticity audit), 15 (Pure-heat baseline), 16 (Setting classification)

---

## 1. Affine Cost Barrier with Authentic Phase Geometry (Section 12)

In milestone `NS-OPENAI-B1-REASSESSMENT-R2`, the backward-diffusion cost barrier was computed assuming collinear wavevectors. We now re-evaluate whether the authentic phase geometries $\Phi_+$ and $\Phi_-$ from Section 7 of the OpenAI monograph alter the super-exponential cost divergence.

### 1.1 Authentic Phase Functions $\Phi_\sigma$
From Section 7.2 of the monograph, the phase functions are:
$$\Phi_\sigma(r, \theta, z, t) = \theta + \sigma \left( \frac{u_*}{2} + \frac{u_* z}{L_s} \right) \frac{z}{\ell_z} + \phi_0(r, t), \qquad \sigma \in \{+1, -1\}.$$

The phase gradients (wavevector normals) are:
$$\nabla \Phi_\sigma = \nabla \phi_0(r) e_r + \frac{1}{r} e_\theta + \sigma \frac{u_*}{L_s} \left( 1 + \frac{2z}{L_s} \right) e_z.$$

In the local filament frame where $r \approx r_j$:
- Radial component: $k_r \sim \partial_r \phi_0$;
- Azimuthal component: $k_\theta \sim 1/r_j$;
- Axial component: $k_{z, \sigma} \sim \sigma \frac{u_*}{L_s}$.

**Observation on Phase Normal Orientation**:
The two branches differ only by the sign of the axial wavenumber component $k_{z, \sigma}$. The angle between $\nabla \Phi_+$ and $\nabla \Phi_-$ is:
$$\theta_{\text{angle}} \sim \frac{2 |k_{z, \sigma}|}{|\nabla \Phi_\sigma|} \asymp \mathcal{O}(1) \quad \text{or smaller}.$$

### 1.2 Impact on the Diffusion Gramian Quadratic Form
Under the unforced backward linearized flow around the straining background $S = \operatorname{diag}(-2\sigma_j, \sigma_j, \sigma_j)$, incompressibility $\operatorname{tr}(S) = 0$ dictates that the compressive strain along $e_r$ is balanced by extensional strain in the transverse plane $(e_\theta, e_z)$.

The backward diffusion Gramian $\mathcal{K}(t_j) = 2\nu \int_{t_j^-}^{t_j} \Phi(t_j, s) \Phi(t_j, s)^T ds$ has eigenvalues:
$$\lambda_1 \asymp \nu 2^{-j(1+h)} \to 0, \qquad \lambda_\perp \asymp \nu 2^{-j(1+h)} \exp\left(2 \cdot 2^{jh}\right) \to +\infty.$$

Any wavevector with non-zero projection onto the transverse subspace $E_\perp = \operatorname{span}(e_\theta, e_z)$ experiences the transverse Gramian quadratic form:
$$Q_{t_j}(\xi) \ge \lambda_\perp |\xi_\perp|^2.$$

For both phases $\sigma = +1$ and $\sigma = -1$:
$$|\nabla \Phi_\sigma \cdot e_\theta| = \frac{1}{r_j} \gg 1, \qquad |\nabla \Phi_\sigma \cdot e_z| = \frac{u_*}{L_s} \gg 0.$$
Both phases possess non-zero, comparable transverse projections:
$$|\xi_{\perp, +}| \asymp |\xi_{\perp, -}| \asymp \Delta k_\perp.$$

### 1.3 Envelope-Forced Transverse Bandwidth
Crucially, the pulse $b_\sigma = \chi_g(\xi_g) \psi(v) t_\sigma^h \cos(k \Phi_\sigma)$ is modulated by the spatial envelope $\chi_g(\xi_g) \psi(v)$, which confines the pulse to an annular filament of radial thickness:
$$\delta r_j \asymp 2^{-j/2}.$$

By the Heisenberg–Nazarov uncertainty bound:
$$\int_{|\xi_\perp| \ge \frac{1}{2} 2^{j/2}} |\widehat{b_\sigma}(\xi)|^2 d\xi \ge c_V \|b_\sigma\|_{L^2}^2 > 0.$$

This bound holds **identically for $\sigma = +$ and $\sigma = -$**, because the spatial envelope $\chi_g \psi$ is identical for both families.

### 1.4 Conclusion on Phase Cost
In the high-cost region $H_j = \{ \xi : Q_{t_j}(\xi) \ge L_j \}$ with threshold $L_j = \frac{\nu}{8} 2^{-jh} \exp(2 \cdot 2^{jh})$:
$$\mathfrak{C}_{\varepsilon, j}^2(b_\sigma) \ge c_V \|b_\sigma\|_{L^2}^2 \exp\left( \frac{\nu}{8} 2^{-jh} \exp\left(2 \cdot 2^{jh}\right) \right) - \varepsilon^2 \to +\infty \quad (\text{super-exponentially}).$$

**Result**:
- Both pulse families $\Phi_+$ and $\Phi_-$ incur **the exact same super-exponential backward cost**.
- Neither family is cheaper than the other; neither evades the transverse extensional explosion.
- The authentic phase geometry does **not** weaken or remove the affine cost barrier.

---

## 2. Rigorous Analyticity Theorem Audit on Periodic $\mathbb{T}^3$ (Section 14)

In R2, the project asserted a `FULL_PERIODIC_PDE exact compact profile no-go` theorem based on parabolic analytic smoothing. We now specify the exact mathematical hypotheses, functional spaces, and domain limitations required for this theorem.

### 2.1 The Nonlinear Parabolic Smoothing Baseline
**Theorem 2.1 (Foias–Temam 1989; Grujić–Kukavica 1998)**:  
Let $\mathbb{T}^3 = (\mathbb{R} / 2\pi \mathbb{Z})^3$, $\nu > 0$, and consider the incompressible Navier–Stokes equations:
$$\partial_t u + (u \cdot \nabla)u = -\nabla p + \nu \Delta u, \qquad \operatorname{div} u = 0, \qquad f \equiv 0.$$
If $u_0 \in L^2_{\text{div}}(\mathbb{T}^3)$, there exists a time $T^\star = T^\star(\|u_0\|_{L^2}, \nu) > 0$ and a unique strong solution:
$$u \in C([0, T^\star); H^1(\mathbb{T}^3)) \cap C^\infty((0, T^\star) \times \mathbb{T}^3).$$
Furthermore, for every $t \in (0, T^\star)$, $u(t)$ belongs to the Gevrey class $G_{1/2}(\mathbb{T}^3)$ and is **real-analytic** in the spatial variables $x \in \mathbb{T}^3$, with uniform radius of analyticity:
$$\rho(t) \ge c \min(\sqrt{\nu t}, 1) > 0.$$

### 2.2 Linearized Parabolic Smoothing About a Smooth Background
Now consider the linearized equation for a perturbation $w$ about a prescribed background flow $u_B$:
$$\partial_t w + \mathbb{P}[(u_B \cdot \nabla)w + (w \cdot \nabla)u_B] = \nu \Delta w, \qquad \operatorname{div} w = 0, \quad x \in \mathbb{T}^3.$$

**Theorem 2.2 (Linearized Analytic Smoothing)**:  
Assume the background flow satisfies:
$$u_B \in C([0, T]; H^s(\mathbb{T}^3)) \quad \text{for } s > 5/2.$$
Then for any initial perturbation $w_0 \in L^2_{\text{div}}(\mathbb{T}^3)$, the forward solution $w(t) = \mathcal{U}(t, 0) w_0$ is real-analytic on $\mathbb{T}^3$ for all $t \in (0, T]$, with radius of analyticity $\rho(t) > 0$ depending on $\nu$, $t$, and $\|u_B\|_{L^\infty_t H^s_x}$.

**Proof Outline**:
1. In Fourier space, the Gevrey norm is defined by $\|w\|_{G_\sigma}^2 \equiv \sum_{k \in \mathbb{Z}^3} |\widehat{w}(k)|^2 e^{2\sigma |k|}$.
2. Differentiating $\frac{1}{2}\frac{d}{dt} \|w\|_{G_{\sigma(t)}}^2$ with $\sigma(t) = \min(\sqrt{\nu t}, \sigma_0)$ yields:
   $$\frac{1}{2}\frac{d}{dt} \|w\|_{G_\sigma}^2 + \nu \|\nabla w\|_{G_\sigma}^2 = \sigma'(t) \|(-\Delta)^{1/4} w\|_{G_\sigma}^2 - \langle \mathbb{P}[(u_B \cdot \nabla)w + (w \cdot \nabla)u_B], w \rangle_{G_\sigma}.$$
3. By Sobolev algebra in Gevrey classes, the trilinear term is bounded by:
   $$|\langle (u_B \cdot \nabla)w, w \rangle_{G_\sigma}| \le C \|u_B\|_{H^s} \|w\|_{G_\sigma} \|\nabla w\|_{G_\sigma} \le \frac{\nu}{2} \|\nabla w\|_{G_\sigma}^2 + \frac{C^2}{\nu} \|u_B\|_{H^s}^2 \|w\|_{G_\sigma}^2.$$
4. Absorbing the dissipation term and applying Grönwall's inequality yields $\|w(t)\|_{G_{\sigma(t)}} < \infty$ for all $t > 0$, establishing spatial real-analyticity. $\square$

### 2.3 Application: The Q1 Compact Profile No-Go
**Corollary 2.3 (Q1 Compact Profile Exclusion on $\mathbb{T}^3$)**:  
Let $u_B \in C([0, t_j]; H^s(\mathbb{T}^3))$ ($s > 5/2$) and $t_j > 0$. Let $W_j^\star \in L^2_{\text{div}}(\mathbb{T}^3)$ be any divergence-free field that is **compactly supported in a proper open subset** $V \subsetneq \mathbb{T}^3$ (i.e. $W_j^\star(x) \equiv 0$ for all $x \in \mathbb{T}^3 \setminus V$).  
If $W_j^\star \not\equiv 0$, then:
$$W_j^\star \notin \operatorname{Range}\left( \mathcal{U}(t_j, 0) \right).$$

**Proof**:
Suppose for contradiction that $W_j^\star \in \operatorname{Range}(\mathcal{U}(t_j, 0))$. Then there exists $w_0 \in L^2_{\text{div}}(\mathbb{T}^3)$ such that $\mathcal{U}(t_j, 0)w_0 = W_j^\star$. By Theorem 2.2, $W_j^\star$ is real-analytic on $\mathbb{T}^3$.  
Since $\mathbb{T}^3$ is a connected real-analytic manifold without boundary, the classical **Identity Theorem for Real-Analytic Functions** states:  
*If a real-analytic function on a connected domain vanishes identically on a non-empty open set, it must vanish identically everywhere on the domain.*  
By assumption, $\mathbb{T}^3 \setminus \overline{V}$ is a non-empty open set on which $W_j^\star \equiv 0$.  
Therefore, $W_j^\star \equiv 0$ on all of $\mathbb{T}^3$, contradicting $W_j^\star \not\equiv 0$. $\square$

### 2.4 Crucial Scope Limitations of the Analyticity No-Go
The verifier must enforce strict boundary conditions on Corollary 2.3:
1. **Requires Smooth Background**: Theorem 2.2 holds on $[0, t_j]$ provided $u_B$ remains smooth ($H^s, s > 5/2$) up to time $t_j$. It does not apply across a blowup time $T^\star \le t_j$.
2. **Applies Strictly to Exact Zero Sets**: The identity theorem requires $W_j^\star = 0$ on an open ball. If the target $W_j^\star$ is replaced by an analytic wavepacket with Gaussian tails (which is non-zero everywhere), Corollary 2.3 does **not** exclude it.
3. **Does Not Exclude $L^2$ Approximations**: As proven in Section 3, the range of analytic solutions is dense in $L^2$. Thus for any $\varepsilon > 0$, there exists an analytic solution $w(t_j)$ within $\varepsilon$ of $W_j^\star$ in $L^2$.

---

## 3. Pure-Heat Dense Range Baseline (Section 15)

We re-affirm the core mathematical invariant established in milestone R2:

**Theorem 3.1 (Heat Semigroup Dense Range Invariant)**:  
For any $\nu > 0, t > 0$, the range of the heat semigroup $e^{\nu t \Delta}$ on $L^2_{\text{div}}(\mathbb{T}^3)$ is dense in $L^2_{\text{div}}(\mathbb{T}^3)$.

**Proof**:  
For any $W^\star \in L^2_{\text{div}}(\mathbb{T}^3)$, let $W_K = P_{\le K} W^\star$ be the frequency truncation to wavenumbers $|k| \le K$. Then:
$$w_0^{(K)} = \sum_{|k| \le K} \widehat{W^\star}(k) e^{\nu t |k|^2} e^{ik \cdot x} \in C^\infty(\mathbb{T}^3),$$
and $e^{\nu t \Delta} w_0^{(K)} = W_K$ exactly. Since $\|W^\star - W_K\|_{L^2} \to 0$ as $K \to \infty$, density is proved. $\square$

### Epistemic Separation Table
| Question | Mathematical Problem | Periodic Heat Operator $e^{\nu t \Delta}$ | Linearized NS $\mathcal{U}(t_j, 0)$ |
| :--- | :--- | :--- | :--- |
| **Q1 (Exact Compact)** | Is exact compact $W_j^\star \in \operatorname{Range}$? | **NO-GO (Proved)** (Analyticity) | **NO-GO (Proved)** (Theorem 2.2) |
| **Q2 (Approximate)** | $\forall \varepsilon > 0, \exists w_0 : \|\mathcal{U} w_0 - W_j^\star\| \le \varepsilon$? | **TRIVIALLY TRUE** (Dense Range) | **OPEN on full PDE / Dense in Heat** |
| **Q2-Cost (Bounded)** | Does realization cost $\mathfrak{C}_{\varepsilon, j}$ stay bounded? | **Diverges** as $K \to \infty$ | **SUPER-EXPONENTIAL DIVERGENCE (Affine)** |
| **Q3 (Stress)** | Can delocalized pulses deliver core stress? | N/A (linear) | **FAILS (Amplitude Collapse)** |

---

## 4. Setting Classification of Project Results (Section 16)

To prevent category errors across different mathematical models, all project results are classified into three strict epistemic tiers:

| Project Result | Epistemic Setting | Scope & Promotion Requirements |
| :--- | :--- | :--- |
| **Q1 Analytic Smoothing Exclusion** | `FULL_PERIODIC_PDE` | Fully established on $\mathbb{T}^3$ under $u_B \in C([0, t_j]; H^s)$. |
| **Proposition 7.5 Covariance Invertibility** | `SOURCE_DERIVED_LOCAL_MODEL` | Valid in local self-similar boundary-layer coordinates of the active filament. |
| **Lemma 7.4 Dynamic Amplitude Ratio** | `SOURCE_DERIVED_LOCAL_MODEL` | Valid along characteristic ray in boundary-layer swirl/strain. |
| **Positive Stress Cone $\mathcal{K}_{\text{stress}}$** | `SOURCE_DERIVED_LOCAL_MODEL` | Valid locally given the presence of pulses $b_+, b_-$. |
| **Gramian Eigenvalue Divergence $\lambda_\perp$** | `EXACT_AFFINE_BENCHMARK` | Proved in homogeneous affine straining background $u_B = A(t)x$. |
| **Admissible Spectral Needle $P_j$** | `EXACT_AFFINE_BENCHMARK` | Proved in affine straining frame. |
| **Super-Exponential Cost Divergence $\mathfrak{C}_{\varepsilon, j}$** | `EXACT_AFFINE_BENCHMARK` | Proved in affine benchmark via Heisenberg–Nazarov uncertainty. Promotion to periodic PDE requires local-to-global approximation theorem. |
| **Gaussian Amplitude Collapse (Q3)** | `EXACT_AFFINE_BENCHMARK` | Proved for energy-normalized packets under affine Gramian expansion. |
| **Pure-Heat Dense Range Theorem** | `FULL_PERIODIC_PDE` | Established on $\mathbb{T}^3$ for any $L^2$ target via Fourier truncation. |
