# NS_NONLINEAR_SELF_FOCUS_001_SCALE_INVARIANCE_AUDIT

## Parabolic Scale-Invariance Audit of Local Stretching vs. Diffusion Diagnostics and Local Length Scales (`NS-NONLINEAR-SELF-FOCUS-001`)

| Field | Value |
| :--- | :--- |
| **Programme ID** | `NS-NONLINEAR-SELF-FOCUS-001` |
| **Locked Target** | Unforced 3D Incompressible Navier–Stokes on $\mathbb{T}^3$, $\nu > 0$, $f \equiv 0$ |
| **Clay Statement B** | `UNRESOLVED` |
| **Release / Deployment** | `NO-GO` / `NONE` |
| **`NS-OPENAI-B2` Status** | `BLOCKED` |
| **Active Governance** | `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3` (`NS-GOV-MIG-V404-001 = MIGRATION_BLOCKED`) |
| **Mathematical Authority** | `Mathematical Research Constitution v1.0.1` |

---

## 1. Natural Parabolic Scaling of 3D Navier–Stokes (Section 9)

The incompressible 3D Navier–Stokes equations $\partial_t u + (u \cdot \nabla)u + \nabla p = \nu \Delta u$ ($\operatorname{div} u = 0$) with fixed kinematic viscosity $\nu > 0$ are invariant under the one-parameter family of **natural parabolic space-time rescalings** (`EXACT_IDENTITY`):

$$\boxed{u_\lambda(x,t) := \lambda\,u(\lambda x, \lambda^2 t), \qquad p_\lambda(x,t) := \lambda^2\,p(\lambda x, \lambda^2 t) \qquad (\lambda > 0)}$$

(On the periodic torus $\mathbb{T}^3_L = (\mathbb{R}/2\pi L\mathbb{Z})^3$, this rescaling maps a solution on $\mathbb{T}^3_L$ to a solution on $\mathbb{T}^3_{L/\lambda}$, or for integer $\lambda \in \mathbb{N}$ preserves periodicity on $\mathbb{T}^3$ itself by embedding a $\lambda$-periodic sub-lattice.)

Let $y := \lambda x$ and $\tau := \lambda^2 t$.By the chain rule ($\partial_{x_j} = \lambda \partial_{y_j}$, $\partial_t = \lambda^2 \partial_\tau$), every derived kinematic and dynamic quantity transforms with an exact homogeneous scaling weight $\lambda^w$:

| Quantity | Formula | Rescaled Value at $(x,t)$ in Terms of $(y,\tau) = (\lambda x, \lambda^2 t)$ | Scaling Weight $w$ ($\lambda^w$) | Physical Dimension ($[\nu] = L^2 T^{-1}$) |
| :--- | :--- | :--- | :---: | :---: |
| **Velocity** | $u(x,t)$ | $u_\lambda(x,t) = \lambda\,u(y,\tau)$ | $+1$ | $L T^{-1}$ |
| **Vorticity** | $\omega = \nabla \times u$ | $\omega_\lambda(x,t) = \lambda^2\,\omega(y,\tau)$ | $+2$ | $T^{-1}$ |
| **Strain Tensor** | $S = \frac{1}{2}(\nabla u + \nabla u^\top)$ | $S_\lambda(x,t) = \lambda^2\,S(y,\tau)$ | $+2$ | $T^{-1}$ |
| **Vorticity Gradient** | $\nabla \omega$ | $\nabla \omega_\lambda(x,t) = \lambda^3\,(\nabla \omega)(y,\tau)$ | $+3$ | $L^{-1} T^{-1}$ |
| **Vorticity Laplacian** | $\Delta \omega$ | $\Delta \omega_\lambda(x,t) = \lambda^4\,(\Delta \omega)(y,\tau)$ | $+4$ | $L^{-2} T^{-1}$ |
| **Stretching Vector** | $S\omega = (\omega \cdot \nabla)u$ | $(S\omega)_\lambda(x,t) = \lambda^4\,(S\omega)(y,\tau)$ | $+4$ | $T^{-2}$ |
| **Viscous Diffusion Vector** | $\nu \Delta \omega$ | $\nu \Delta \omega_\lambda(x,t) = \lambda^4\,\nu (\Delta \omega)(y,\tau)$ | $+4$ | $T^{-2}$ |
| **Local Enstrophy Production** | $\omega \cdot S\omega$ | $(\omega \cdot S\omega)_\lambda(x,t) = \lambda^6\,(\omega \cdot S\omega)(y,\tau)$ | $+6$ | $T^{-3}$ |
| **Local Palinstrophy Density** | $\nu |\nabla \omega|^2$ | $\nu |\nabla \omega_\lambda(x,t)|^2 = \lambda^6\,\nu |\nabla \omega(y,\tau)|^2$ | $+6$ | $T^{-3}$ |
| **Unit Direction** | $\xi = \omega / |\omega|$ | $\xi_\lambda(x,t) = \xi(y,\tau)$ | $0$ | Dimensionless ($1$) |
| **Signed Axial Strain** | $\lambda_\omega = \xi^\top S \xi$ | $(\lambda_\omega)_\lambda(x,t) = \lambda^2\,\lambda_\omega(y,\tau)$ | $+2$ | $T^{-1}$ |

---

## 2. Audit of the Pointwise Stretching-to-Diffusion Diagnostic $\mathscr{S}(x,t)$ (Section 9)

Consider the candidate local diagnostic defined in Section 9 (`PROJECT_DIAGNOSTIC`):

$$\boxed{\mathscr{S}_\varepsilon(x,t) := \frac{|S(x,t)\omega(x,t)|}{\nu|\Delta\omega(x,t)| + \varepsilon} \qquad (\varepsilon > 0)}$$

and its unregularized limit on $\{\Delta\omega(x,t) \ne 0\}$:
$$\mathscr{S}_0(x,t) := \frac{|S(x,t)\omega(x,t)|}{\nu|\Delta\omega(x,t)|}.$$

### Proposition 2.1 (Exact Scale-Invariance of $\mathscr{S}_0$ and Asymptotic Scale-Invariance of $\mathscr{S}_\varepsilon$)
1. **Unregularized Diagnostic ($\varepsilon = 0$)**: Under $u_\lambda(x,t) = \lambda u(\lambda x, \lambda^2 t)$, both numerator $|S_\lambda \omega_\lambda| = \lambda^4 |S\omega|$ and denominator $\nu |\Delta \omega_\lambda| = \lambda^4 \nu |\Delta \omega|$ carry identical scaling weight $w = +4$. Consequently, $\mathscr{S}_0$ is **strictly dimensionless and scale-invariant** ($\lambda^0$):
   $$\mathscr{S}_0[u_\lambda](x,t) = \frac{\lambda^4 |S(y,\tau)\omega(y,\tau)|}{\lambda^4 \nu |\Delta\omega(y,\tau)|} = \mathscr{S}_0[u](\lambda x, \lambda^2 t).$$
2. **Regularized Diagnostic ($\varepsilon > 0$)**: With fixed constant $\varepsilon > 0$ (of dimension $T^{-2}$), under $u_\lambda$:
   $$\mathscr{S}_\varepsilon[u_\lambda](x,t) = \frac{\lambda^4 |S(y,\tau)\omega(y,\tau)|}{\lambda^4 \nu |\Delta\omega(y,\tau)| + \varepsilon} = \frac{|S(y,\tau)\omega(y,\tau)|}{\nu |\Delta\omega(y,\tau)| + \lambda^{-4}\varepsilon} = \mathscr{S}_{\lambda^{-4}\varepsilon}[u](\lambda x, \lambda^2 t).$$
   Thus:
   - If $\varepsilon$ transforms covariantly with weight $+4$ ($\varepsilon_\lambda = \lambda^4 \varepsilon$, e.g. $\varepsilon = \eta \nu^2 L_0^{-4}$), then $\mathscr{S}_{\varepsilon_\lambda}[u_\lambda](x,t) = \mathscr{S}_\varepsilon[u](\lambda x, \lambda^2 t)$ is **exact scale-invariant**.
   - If $\varepsilon > 0$ is held fixed as a small numerical floor, then in the high-gradient self-focusing regime ($\lambda \to \infty$, where $\lambda^4 \nu |\Delta\omega| \gg \varepsilon$), $\mathscr{S}_\varepsilon[u_\lambda](x,t) \to \mathscr{S}_0[u](\lambda x, \lambda^2 t)$ is **asymptotically scale-invariant** with relative error $O(\varepsilon \lambda^{-4})$.

### Structural Strengths and Weaknesses of $\mathscr{S}_\varepsilon(x,t)$
- **Strength 1 (Eliminates 2D and Pure Shear False Positives)**: Because the numerator is the vector norm $|S\omega|$ rather than $|S||\omega|$, whenever $\omega$ lies in the nullspace of $S$ (as in all 2D flows and pure shear flows), $S\omega \equiv \mathbf{0}$ and therefore $\mathscr{S}_\varepsilon(x,t) \equiv 0$.
- **Strength 2 (Measures Direct PDE Term Ratio)**: In the vorticity PDE $\partial_t \omega + (u \cdot \nabla)\omega = S\omega + \nu \Delta\omega$, $\mathscr{S}_0(x,t)$ is the exact Euclidean norm ratio of the local vortex stretching source $S\omega$ to the viscous diffusion vector $\nu \Delta\omega$.
- **Weakness 1 (Sign Blindness between Stretching and Compression)**: Since $|S\omega| = \sqrt{(\lambda_\omega |\omega|)^2 + |(I - \xi\xi^\top)S\omega|^2} \ge |\lambda_\omega||\omega|$, $\mathscr{S}_\varepsilon$ cannot distinguish between axial stretching ($\lambda_\omega > 0$) and axial compression ($\lambda_\omega < 0$) or pure vorticity rotation ($S\omega \perp \omega$, where $\lambda_\omega = 0$ but $|S\omega| > 0$).
- **Weakness 2 (Nodal Zeros of $\Delta\omega$)**: At isolated inflection surfaces where $\Delta\omega(x,t) = 0$ while $|\nabla\omega(x,t)| \ne 0$, $\mathscr{S}_0$ blows up artificially (regulated to $|S\omega|/\varepsilon$ in $\mathscr{S}_\varepsilon$), even if palinstrophy dissipation $\nu|\nabla\omega|^2$ is large.

To remedy both weaknesses, we pair $\mathscr{S}_\varepsilon(x,t)$ with the gradient-based local length scale $\ell_\omega(x,t)$ and the signed competition diagnostic $\mathcal{R}_{\omega,\text{signed}}(x,t)$.

---

## 3. Local Vorticity Length Scale $\ell_\omega(x,t)$ and Competition Ratios (Sections 11 & 12)

### Definition 3.1 (Local Vorticity Gradient Length Scale, `PROJECT_DIAGNOSTIC`)
For $\varepsilon_\omega > 0$ (of dimension $T^{-2}$, regularizing nodal zeros of $\omega$), define the local inverse squared vorticity length scale:

$$\boxed{\ell_\omega^{-2}(x,t) := \frac{|\nabla\omega(x,t)|^2}{|\omega(x,t)|^2 + \varepsilon_\omega}, \qquad \ell_\omega(x,t) := \left(\frac{|\omega(x,t)|^2 + \varepsilon_\omega}{|\nabla\omega(x,t)|^2}\right)^{1/2}}$$

Under the parabolic rescaling $u_\lambda(x,t) = \lambda u(\lambda x, \lambda^2 t)$ (with $\varepsilon_\omega \to \lambda^4 \varepsilon_\omega$ or $\varepsilon_\omega = 0$ on $\{\omega \ne 0\}$):
$$\ell_{\omega_\lambda}^{-2}(x,t) = \frac{\lambda^6 |\nabla\omega(\lambda x, \lambda^2 t)|^2}{\lambda^4 |\omega(\lambda x, \lambda^2 t)|^2} = \lambda^2\,\ell_\omega^{-2}(\lambda x, \lambda^2 t) \implies \boxed{\ell_{\omega_\lambda}(x,t) = \lambda^{-1}\,\ell_\omega(\lambda x, \lambda^2 t)}$$
Thus $\ell_\omega(x,t)$ transforms with exact scaling weight $w = -1$ ($\lambda^{-1}$, physical dimension $[L]^1$), faithfully measuring the transverse thickness / gradient radius of a vortex tube or sheet at $(x,t)$.

### Definition 3.2 (Unsigned and Signed Local Scale-Competition Numbers, `PROJECT_DIAGNOSTIC`)
Using $\ell_\omega(x,t)$, the local viscous diffusion rate per unit enstrophy is:
$$\tau_{\text{diff}}^{-1}(x,t) := \frac{\nu|\nabla\omega(x,t)|^2}{|\omega(x,t)|^2 + \varepsilon_\omega} = \frac{\nu}{\ell_\omega(x,t)^2} \qquad (\text{weight } \lambda^{+2}, \text{ dimension } T^{-1}).$$
Comparing the local strain rate $|S(x,t)|$, the vector stretching rate $|S\omega|/|\omega|$, and the signed axial stretching rate $\lambda_\omega(x,t) = \xi^\top S \xi$ against $\tau_{\text{diff}}^{-1}(x,t)$ yields three dimensionless ($\lambda^0$) local competition ratios:

1. **Unsigned Strain–Diffusion Competition Ratio (`PROJECT_DIAGNOSTIC` / `HEURISTIC`)**:
   $$\boxed{\mathcal{R}_\omega(x,t) := \frac{|S(x,t)|\,\ell_\omega(x,t)^2}{\nu} = \frac{|S(x,t)|\big(|\omega(x,t)|^2 + \varepsilon_\omega\big)}{\nu |\nabla\omega(x,t)|^2}}$$
2. **Vector Stretching–Diffusion Competition Ratio (`PROJECT_DIAGNOSTIC`)**:
   $$\boxed{\mathcal{R}_{\omega,\text{vec}}(x,t) := \frac{|S(x,t)\omega(x,t)|\,\ell_\omega(x,t)^2}{\nu |\omega(x,t)|} = \frac{|S(x,t)\omega(x,t)|\sqrt{|\omega(x,t)|^2 + \varepsilon_\omega}}{\nu |\nabla\omega(x,t)|^2}}$$
3. **Signed Axial Enstrophy Competition Ratio (`PROJECT_DIAGNOSTIC`)**:
   $$\boxed{\mathcal{R}_{\omega,\text{signed}}(x,t) := \frac{\lambda_\omega(x,t)\,\ell_\omega(x,t)^2}{\nu} = \frac{(\omega(x,t) \cdot S(x,t)\omega(x,t))\big(1 + \varepsilon_\omega / |\omega(x,t)|^2\big)}{\nu |\nabla\omega(x,t)|^2}}$$

Notice the exact pointwise inequality chain on $\{\omega \ne 0\}$ (for $\varepsilon_\omega = 0$):
$$\mathcal{R}_{\omega,\text{signed}}(x,t) = \frac{\omega \cdot S\omega}{\nu|\nabla\omega|^2} \le \left|\mathcal{R}_{\omega,\text{signed}}(x,t)\right| \le \mathcal{R}_{\omega,\text{vec}}(x,t) = \frac{|S\omega||\omega|}{\nu|\nabla\omega|^2} \le \mathcal{R}_\omega(x,t) = \frac{|S||\omega|^2}{\nu|\nabla\omega|^2}.$$
And in the exact local enstrophy PDE (Section 7):
$$\frac{1}{2}(\partial_t + u \cdot \nabla)|\omega|^2 - \frac{\nu}{2}\Delta|\omega|^2 = \omega \cdot S\omega - \nu|\nabla\omega|^2 = \nu|\nabla\omega|^2\big(\mathcal{R}_{\omega,\text{signed}}(x,t) - 1\big).$$
At any spatial maximum $x_*(t)$ of $|\omega(\cdot,t)|^2$ where $\Delta|\omega(x_*(t),t)|^2 \le 0$ and $\nabla|\omega(x_*(t),t)|^2 = 0$, instantaneous growth $\partial_t |\omega(x_*(t),t)|^2 > 0$ **strictly requires**:
$$\boxed{\mathcal{R}_{\omega,\text{signed}}(x_*(t),t) = \frac{\lambda_\omega(x_*(t),t)\,\ell_\omega(x_*(t),t)^2}{\nu} > 1 \implies \mathcal{R}_\omega(x_*(t),t) = \frac{|S(x_*(t),t)|\,\ell_\omega(x_*(t),t)^2}{\nu} > 1}$$

---

## 4. Classification of the Three Small-Scale Regimes as $\ell_\omega \to 0$ (Section 12)

Suppose a family of vortex structures in $\mathbb{T}^3$ develops progressively smaller transverse length scales $\ell_\omega(t) \to 0$. The behavior of the competition number $\mathcal{R}_{\omega,\text{signed}} = \lambda_\omega \ell_\omega^2 / \nu$ (and $\mathcal{R}_\omega = |S|\ell_\omega^2/\nu$) partitions the dynamics into three mutually exclusive regimes:

| Regime | Asymptotic Behavior as $\ell_\omega \to 0$ | Strain vs. Scale Scaling | Physical & Mathematical Consequence |
| :--- | :--- | :--- | :--- |
| **Regime I: Subcritical (Diffusion-Dominated)** | $\dfrac{|S|\ell_\omega^2}{\nu} \longrightarrow 0$ | $|S(t)| \ll \nu\,\ell_\omega(t)^{-2}$ (e.g., $\ell_\omega \sim (T_*-t)^\alpha$, $|S| \sim (T_*-t)^{-2\alpha + \delta}$ with $\delta > 0$) | Viscous dissipation $\nu|\nabla\omega|^2 \sim \nu|\omega|^2/\ell_\omega^2$ strictly dominates vortex stretching $\omega \cdot S\omega \le |S||\omega|^2$. Peak enstrophy decays ($\partial_t \|\omega\|_{L^\infty}^2 < 0$), quenching small-scale focus. |
| **Regime II: Critical Balance (Parabolic / Burgers-Type Equilibrium)** | $\dfrac{\lambda_\omega \ell_\omega^2}{\nu} \sim O(1)$ (specifically $\ge 1$) | $\lambda_\omega(t) \asymp \nu\,\ell_\omega(t)^{-2}$, matching natural Leray self-similar scaling $\ell_\omega(t) \sim \sqrt{\nu(T_*-t)}$ and $\lambda_\omega(t) \sim (T_*-t)^{-1}$ | Stretching and diffusion remain in scale-critical balance as $\ell_\omega \to 0$. In a steady external strain field this produces the Burgers vortex equilibrium ($\mathcal{R}_{\omega,\text{signed}} = 1$); for blowup on $\mathbb{T}^3$, $\mathcal{R}_{\omega,\text{signed}}$ must stay strictly $> 1$ across shrinking scales while $\int_0^{T_*} \lambda_\omega^+(t)\,dt = \infty$ (Ponce/BKM). |
| **Regime III: Supercritical (Advection-Stretching Dominated)** | $\dfrac{\lambda_\omega \ell_\omega^2}{\nu} \longrightarrow +\infty$ | $\lambda_\omega(t) \gg \nu\,\ell_\omega(t)^{-2}$ (e.g., Euler-like collapse $\ell_\omega(t) \sim (T_*-t)^\alpha$ with $\alpha < 1/2$ and $\lambda_\omega(t) \sim (T_*-t)^{-1}$) | Vortex stretching completely outpaces viscous diffusion at the active scale $\ell_\omega(t)$. However, by Constantin–Fefferman (1993), sustaining $\lambda_\omega \gg \nu \ell_\omega^{-2}$ requires the vorticity direction curvature $|\nabla\xi|$ to blow up at least as fast as $\ell_\omega^{-1}$ within the active core, triggering intense cross-diffusion $\nu|\nabla\xi|^2|\omega|^2$ in $|\nabla\omega|^2 = |\nabla|\omega||^2 + |\omega|^2|\nabla\xi|^2$ that pushes $\ell_\omega^{-2} = |\nabla|\omega||^2/|\omega|^2 + |\nabla\xi|^2$ back toward Regime II/I! |

### Crucial Decomposition of $\ell_\omega^{-2}$ into Amplitude Gradient and Direction Curvature (`EXACT_IDENTITY`)
Since $\omega = |\omega|\xi$ with $|\xi|=1$ and $\xi \cdot \partial_j \xi = 0$, the Frobenius norm of $\nabla\omega$ splits orthogonally (`EXACT_IDENTITY`):
$$|\nabla\omega|^2 = |\nabla(|\omega|)|^2 + |\omega|^2\,|\nabla\xi|^2.$$
Dividing by $|\omega|^2$ on $\{\omega \ne 0\}$ gives the **Exact Inverse Length-Scale Decomposition** (`EXACT_IDENTITY`):

$$\boxed{\ell_\omega^{-2}(x,t) = \frac{|\nabla\omega(x,t)|^2}{|\omega(x,t)|^2} = \underbrace{\big|\nabla \ln |\omega(x,t)|\big|^2}_{\ell_{|\omega|}^{-2}(x,t) \text{ (amplitude core thickness)}} + \underbrace{|\nabla\xi(x,t)|^2}_{\ell_\xi^{-2}(x,t) \text{ (vorticity direction curvature)}}}$$

This identity links Section 11 ($\ell_\omega$) directly to Section 17 (Constantin–Fefferman direction coherence):
- Even if the amplitude profile $|\omega|$ were relatively broad ($\ell_{|\omega|} \gg \sqrt{\nu/|S|}$), strong directional twisting $|\nabla\xi| \to \infty$ automatically forces $\ell_\omega^{-2} = \ell_{|\omega|}^{-2} + \ell_\xi^{-2} \ge |\nabla\xi|^2 \to \infty$, thereby increasing viscous dissipation $\nu|\nabla\omega|^2 = \nu|\nabla|\omega||^2 + \nu|\omega|^2|\nabla\xi|^2$!
- Conversely, if $|\nabla\xi|$ remains bounded ($|\nabla\xi| \le \rho_0^{-1}$), Constantin–Fefferman direction coherence depletes the singular integral for $\lambda_\omega(x,t)$, preventing $|S|$ from growing uncontrollably.
- Thus any viable forward self-focusing mechanism must operate in the **critical window** where $\ell_{|\omega|}^{-1}(t) \asymp \ell_\xi^{-1}(t) \asymp \ell_\omega^{-1}(t)$ and $\lambda_\omega(t)\ell_\omega(t)^2/\nu = O(1) > 1$ (Regime II).
