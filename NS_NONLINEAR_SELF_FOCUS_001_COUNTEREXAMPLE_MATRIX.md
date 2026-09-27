# NS_NONLINEAR_SELF_FOCUS_001_COUNTEREXAMPLE_MATRIX

## Falsification-First Counterexample Matrix for Forward Self-Focusing Diagnostics (`NS-NONLINEAR-SELF-FOCUS-001`, Section 13)

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

## 1. Falsification Methodology

Under `Mathematical Research Constitution v1.0.1` and the falsification-first protocol (Section 13), **every candidate self-focusing diagnostic must be tested against exact and canonical non-blowing-up solutions before any claim of dynamical sufficiency or mechanism survival is permitted.**

A candidate diagnostic suffers a **False Positive** if it takes values in the "self-focusing / supercritical regime" ($> 1$ or $\to \infty$) on a flow where nonlinear vortex stretching is either identically absent or dynamically inert (purely decaying under viscosity).

We evaluate the complete suite of project diagnostics across the **seven mandated testbeds**:
1. $\omega \cdot S\omega = \lambda_\omega |\omega|^2$ (local signed vortex stretching production, `EXACT_IDENTITY`);
2. $P(t) = \int_{\mathbb{T}^3} \omega \cdot S\omega\,dx$ and $\mathcal{A}(t) = P(t)/D(t)$ (global enstrophy amplification ratio, `PROJECT_DIAGNOSTIC`);
3. $\mathscr{S}_\varepsilon(x,t) = \frac{|S\omega|}{\nu|\Delta\omega|+\varepsilon}$ (pointwise stretching-to-Laplacian vector ratio, `PROJECT_DIAGNOSTIC`);
4. $\ell_\omega(x,t) = \left(\frac{|\omega|^2+\varepsilon_\omega}{|\nabla\omega|^2}\right)^{1/2}$ (local vorticity gradient length scale, `PROJECT_DIAGNOSTIC`);
5. $\mathcal{R}_\omega(x,t) = \frac{|S|\ell_\omega^2}{\nu}$ (unsigned strain-scale competition ratio, `HEURISTIC`);
6. $\mathcal{R}_{\omega,\text{signed}}(x,t) = \frac{\lambda_\omega \ell_\omega^2}{\nu}$ (signed axial stretching competition ratio, `PROJECT_DIAGNOSTIC`);
7. $\widetilde{\mathcal{R}}_{\omega,\text{Lag}}(x,t) := \frac{\omega \cdot S\omega - \frac{1}{2}u \cdot \nabla|\omega|^2}{\nu|\nabla\omega|^2}$ (Beltrami-corrected material enstrophy production ratio, `PROJECT_DIAGNOSTIC`).

---

## 2. Master Falsification-First Counterexample Matrix

| # | Testbed Flow | Domain & Autonomous Status on $\mathbb{T}^3$ ($f=0$) | Unsigned $\mathcal{R}_\omega = \frac{|S|\ell_\omega^2}{\nu}$ | Pointwise $\mathscr{S}_\varepsilon = \frac{\|S\omega\|}{\nu\|\Delta\omega\|+\varepsilon}$ | Pointwise Signed $\mathcal{R}_{\omega,\text{signed}} = \frac{\lambda_\omega\ell_\omega^2}{\nu}$ | Beltrami-Corrected $\widetilde{\mathcal{R}}_{\omega,\text{Lag}}$ | Global Ratio $\mathcal{A}(t) = \frac{P(t)}{D(t)}$ | Falsification Verdict & Diagnostic Lesson |
| :-: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Pure Shear Flow** $u = (A e^{-\nu k^2 t}\sin(ky), 0, 0)$ | Exact solution on $\mathbb{T}^3$ ($f=0$) | $\frac{A e^{-\nu k^2 t}}{\sqrt{2}\nu k}\tan^2(ky) \gg 1$ (**FALSE POSITIVE**) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | **Falsifies unsigned $\mathcal{R}_\omega$**: $|S| > 0$ and $|\omega| > 0$, yet $\omega \perp \text{Ran}(S)$ so $S\omega \equiv \mathbf{0}$. Must use $\mathscr{S}_\varepsilon$ or $\mathcal{R}_{\omega,\text{signed}}$. |
| **2** | **General 2D-in-3D Flow** $u = (u_1(x,y,t), u_2(x,y,t), 0)$ | Exact invariant subspace on $\mathbb{T}^3$ ($f=0$) | Arbitrarily large $O(Re) \gg 1$ (**FALSE POSITIVE**) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | **Falsifies unsigned $\mathcal{R}_\omega$**: $\omega = (0,0,\omega_3)$ lies in $\ker(S)$. All vector/signed diagnostics vanish identically. |
| **3** | **Beltrami / ABC Flow** $\omega = \Lambda u$ ($|\Lambda| = k_0$, $A,B,C \ne 0$) | Exact eigenfunction solution $u(t) = e^{-\nu \Lambda^2 t}u_0$ on $\mathbb{T}^3$ ($f=0$) | $O(Re) \gg 1$ (**FALSE POSITIVE**) | $\frac{\|\nabla\|u\|^2\|}{2\nu\Lambda\|u\|} \gg 1$ (**FALSE POSITIVE**) | $\frac{u \cdot \nabla\|u\|^2}{2\nu|\nabla u|^2} \gtrless 0$ (**FALSE POSITIVE** on $\{u\cdot\nabla|u|^2 > 0\}$) | $\mathbf{0}$ (Exact Zero everywhere!) | $\mathbf{0}$ (Exact Zero for all $t \ge 0$!) | **Crucial Falsification of Naive Pointwise $\lambda_\omega > 0$ & $\mathscr{S}_\varepsilon > 1$**: On ABC flows with non-constant $|u|^2$, $\omega \cdot S\omega = \frac{1}{2}u \cdot \nabla|\omega|^2 \ne 0$ pointwise! Yet it merely balances spatial advection $(u\cdot\nabla)\frac{|\omega|^2}{2}$, so $\widetilde{\mathcal{R}}_{\omega,\text{Lag}} \equiv 0$ and $P(t) \equiv 0$. |
| **4** | **Taylor–Green Vortex** $u_0 = (\sin x\cos y\cos z, -\cos x\sin y\cos z, 0)$ | Smooth periodic IVP on $\mathbb{T}^3$ ($f=0$) | $O(Re)$ at $t=0$ | $> 0$ at $t=0$; grows for $t > 0$ | $\gtrless 0$ pointwise at $t=0$; positive mean for $t > 0$ | $\gtrless 0$ at $t=0$; positive core for $t > 0$ | $\mathcal{A}(0) = \mathbf{0}$, but $\frac{d\mathcal{A}}{dt}(0) > 0$ & $\mathcal{A}(t) > 1$ for $t \in (t_1, t_2)$ ($\nu \ll 1$) | **True Transient Self-Focusing Benchmark**: Symmetry makes $P(0) = 0$, while $\frac{dP}{dt}(0) = \frac{3}{32}\pi^3 > 0$ drives genuine forward enstrophy amplification ($\mathcal{A}(t) > 1$) and scale shrinking $\bar{\ell}_\omega(t) \downarrow$. |
| **5** | **Lamb–Oseen Diffusing Vortex** $\omega(r,t) = \frac{\Gamma}{4\pi\nu t}e^{-r^2/(4\nu t)}\mathbf{e}_z$ | Exact 2D axisymmetric solution on $\mathbb{R}^3$ (or periodized array) | $\frac{\Gamma}{4\pi\nu}\Phi(r/\sqrt{\nu t}) \gg 1$ (**FALSE POSITIVE**) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | $\mathbf{0}$ (Exact Zero) | **Pure Viscous Spreading**: $\ell_\omega(t) = \frac{\sqrt{4\nu t}}{r/\sqrt{\nu t}} \propto \sqrt{\nu t}$ expands monotonically; $S\omega \equiv \mathbf{0}$. |
| **6** | **Burgers Vortex** $\omega_z(r) = \frac{\alpha\Gamma}{4\pi\nu}e^{-\alpha r^2/(4\nu)}$ in strain $S_{\text{ext}} = \operatorname{diag}(-\frac{\alpha}{2},-\frac{\alpha}{2},\alpha)$ | Exact on $\mathbb{R}^3$, **NON-AUTONOMOUS / INFINITE ENERGY** (Requires externally imposed strain $\alpha$) | $\frac{\sqrt{6}}{2}\frac{\alpha\ell_\omega^2}{\nu} = O(1)$ | $\frac{\alpha \omega_z}{\nu|\Delta\omega_z|} = 1$ at $r=0$ | $\frac{\alpha \ell_\omega^2}{\nu} = O(1)$ (integrates to $\mathcal{A} = 1$) | $\mathcal{A}_{\text{core}} = 1$ (Steady Equilibrium) | $\mathcal{A}(t) \equiv \mathbf{1}$ ($P = D$) | **Critical Scale-Competition Archetype**: Demonstrates exact balance $\lambda_\omega \ell_\omega^2/\nu = O(1)$ at the Burgers radius $r_B = \sqrt{4\nu/\alpha}$, **but $S_{\text{ext}}$ is externally imposed at $\infty$ and cannot persist steadily on unforced $\mathbb{T}^3$**. |
| **7** | **Periodic Hyperbolic Stagnation / Interacting Vortex Tubes** | Smooth divergence-free periodic flow on $\mathbb{T}^3$ ($f=0$) | $O(Re) > 1$ | $> 1$ in stagnation stretching core | $> 1$ in aligned axial core | $> 1$ in aligned axial core | $\mathcal{A}(0) > 1$ for $\nu < \nu_{\text{crit}}$ | **Authentic Autonomous Forward Focusing**: Two orthogonal or antiparallel vortex tubes on $\mathbb{T}^3$ mutually induce axial strain $S[\omega]$ with $P(0) > 0$ and $\mathcal{A}(0) > 1$ without external forcing. |

---

## 3. Detailed Analytical Derivations of Each Counterexample

### 3.1 Testbed 1 & 2: Pure Shear Flow and General 2D-in-3D Flow
Let $u(x,y,z,t) = (f(y,t), 0, 0)$ with $f(y,t) = A e^{-\nu k^2 t}\sin(ky)$ on $\mathbb{T}^3$. Then:
$$\omega = (0, 0, -\partial_y f), \qquad S = \begin{pmatrix} 0 & \frac{1}{2}\partial_y f & 0 \\ \frac{1}{2}\partial_y f & 0 & 0 \\ 0 & 0 & 0 \end{pmatrix}, \qquad |S| = \frac{1}{\sqrt{2}}|\partial_y f|.$$
Multiplying $S$ by $\omega$ gives:
$$S\omega = \begin{pmatrix} 0 & \frac{1}{2}\partial_y f & 0 \\ \frac{1}{2}\partial_y f & 0 & 0 \\ 0 & 0 & 0 \end{pmatrix}\begin{pmatrix} 0 \\ 0 \\ -\partial_y f \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \\ 0 \end{pmatrix} \implies \omega \cdot S\omega \equiv 0, \quad \lambda_\omega \equiv 0, \quad \mathscr{S}_\varepsilon \equiv 0, \quad \mathcal{A}(t) \equiv 0.$$
However, the unsigned ratio $\mathcal{R}_\omega = |S|\ell_\omega^2/\nu$ equals $\frac{A e^{-\nu k^2 t}\cos^2(ky)}{\sqrt{2}\nu k^3 \sin^2(ky)} > 0$, which can be made arbitrarily large by choosing $A \gg \nu k^3$! The exact same cancellation $S\omega \equiv \mathbf{0}$ holds for every 2D-in-3D flow $u = (u_1(x,y,t), u_2(x,y,t), 0)$ because $\omega = \omega_3(x,y,t)\mathbf{e}_3$ and $S_{i3} = S_{3i} = 0$.

> **Mandatory Rule 1**: Never use the unsigned product $|S||\omega|$ or unsigned $\mathcal{R}_\omega = |S|\ell_\omega^2/\nu$ as a sufficiency indicator for self-focusing; always project onto $S\omega$ ($\mathscr{S}_\varepsilon$) and $\omega \cdot S\omega = \lambda_\omega |\omega|^2$ ($\mathcal{R}_{\omega,\text{signed}}$).

### 3.2 Testbed 3: Beltrami and Arnold–Beltrami–Childress (ABC) Flows
Let $u_0(x) \in C^\infty_\sigma(\mathbb{T}^3)$ be a strong Beltrami field satisfying $\omega_0 = \nabla \times u_0 = \Lambda u_0$ ($\Lambda \in \mathbb{R} \setminus \{0\}$, such as the standard ABC flow $u_0 = (A\sin z + C\cos y, B\sin x + A\cos z, C\sin y + B\cos x)$ with $\Lambda = 1$).
Because the Lamb vector vanishes identically ($\mathcal{L} := u \times \omega = u \times (\Lambda u) = \mathbf{0}$), the nonlinear convective term is a pure pressure gradient:
$$(u \cdot \nabla)u = \omega \times u + \nabla\left(\frac{1}{2}|u|^2\right) = \nabla\left(\frac{1}{2}|u|^2\right).$$
Therefore, the exact nonlinear Navier–Stokes solution on $\mathbb{T}^3$ is purely linear heat decay:
$$u(x,t) = e^{-\nu \Lambda^2 t}u_0(x), \qquad \omega(x,t) = \Lambda e^{-\nu \Lambda^2 t}u_0(x), \qquad p(x,t) = -\frac{1}{2}e^{-2\nu\Lambda^2 t}|u_0(x)|^2.$$
Now let us compute the vortex stretching term $\omega \cdot S\omega$ for this exact decaying Beltrami flow! Since $\omega = \Lambda u$:
$$(S\omega)_i = \omega_j S_{ij} = \omega_j \partial_j u_i = \Lambda u_j \partial_j u_i = \Lambda (u \cdot \nabla)u_i = \frac{\Lambda}{2}\partial_i(|u|^2) = \frac{1}{2\Lambda}\partial_i(|\omega|^2),$$
and taking the inner product with $\omega = \Lambda u$ gives the remarkable identity (`EXACT_IDENTITY`):

$$\boxed{\omega(x,t) \cdot S(x,t)\omega(x,t) = \frac{\Lambda^2}{2}\,(u \cdot \nabla)|u(x,t)|^2 = \frac{1}{2}\,(u \cdot \nabla)|\omega(x,t)|^2}$$

Look at what this implies for a general ABC flow ($A,B,C \ne 0$) where $|u_0(x)|^2$ is NOT spatially constant:
1. **Pointwise $\omega \cdot S\omega$ and $\lambda_\omega(x,t)$ are NON-ZERO**! Specifically, wherever fluid particles move toward higher speed ($(u \cdot \nabla)|u|^2 > 0$), $\omega \cdot S\omega > 0$ and $\lambda_\omega(x,t) > 0$, and for small $\nu$, both $\mathscr{S}_\varepsilon(x,t) = \frac{|\nabla|u|^2|}{2\nu \Lambda |u|}$ and $\mathcal{R}_{\omega,\text{signed}}(x,t)$ can be arbitrarily large ($\gg 1$)!
2. **Yet NO material enstrophy growth occurs**, because in the local enstrophy balance:
   $$\frac{1}{2}\partial_t |\omega|^2 + \underbrace{\frac{1}{2}(u \cdot \nabla)|\omega|^2 - \omega \cdot S\omega}_{=\,0 \text{ identically!}} = \frac{\nu}{2}\Delta|\omega|^2 - \nu|\nabla\omega|^2.$$
   The pointwise stretching $\omega \cdot S\omega$ is $100\%$ consumed by the spatial advection $(u \cdot \nabla)\frac{|\omega|^2}{2}$ as fluid elements travel through the stationary wave pattern!
3. **Globally on $\mathbb{T}^3$**, integrating by parts with $\operatorname{div} u = 0$ yields:
   $$P(t) = \int_{\mathbb{T}^3} \omega \cdot S\omega\,dx = \frac{1}{2}\int_{\mathbb{T}^3} (u \cdot \nabla)|\omega|^2\,dx = -\frac{1}{2}\int_{\mathbb{T}^3} (\operatorname{div} u)|\omega|^2\,dx = 0 \implies \boxed{\mathcal{A}(t) \equiv 0}.$$

> **Mandatory Rule 2 (Beltrami Falsification Filter)**: Pointwise $\lambda_\omega(x,t) > 0$ or $\mathscr{S}_\varepsilon(x,t) > 1$ is insufficient if $\omega \cdot S\omega$ equals $\frac{1}{2}(u \cdot \nabla)|\omega|^2$. Genuine Lagrangian enstrophy amplification requires either:
> - **Global production** $P(t) = \int_{\mathbb{T}^3} \omega \cdot S\omega\,dx > \nu \int_{\mathbb{T}^3}|\nabla\omega|^2\,dx$ ($\mathcal{A}(t) > 1$), where the Beltrami advection term integrates identically to zero; or
> - **Beltrami-subtracted Lagrangian excess** $\omega \cdot S\omega - \frac{1}{2}(u \cdot \nabla)|\omega|^2 = \omega \cdot (\omega \cdot \nabla u - u \cdot \nabla \omega) = \omega \cdot (\nabla \times (u \times \omega)) > \nu|\nabla\omega|^2$ (or evaluation at a spatial maximum $x_*(t)$ of $|\omega(\cdot,t)|^2$ where $\nabla|\omega(x_*(t),t)|^2 = \mathbf{0}$).

### 3.3 Testbed 4: Taylor–Green Vortex on $\mathbb{T}^3$
Consider the classical 3D Taylor–Green initial data on $\mathbb{T}^3$:
$$u_0(x,y,z) = \begin{pmatrix} \sin x \cos y \cos z \\ -\cos x \sin y \cos z \\ 0 \end{pmatrix}, \qquad \omega_0(x,y,z) = \begin{pmatrix} -\cos x \sin y \sin z \\ -\sin x \cos y \sin z \\ 2\sin x \sin y \cos z \end{pmatrix}.$$
- At $t = 0$, $\|\omega_0\|_{L^2(\mathbb{T}^3)}^2 = 3\pi^3$ and $\|\nabla\omega_0\|_{L^2(\mathbb{T}^3)}^2 = 9\pi^3$, so the initial global active length scale is exact:
  $$\bar{\ell}_\omega(0) = \frac{\|\omega_0\|_{L^2}}{\|\nabla\omega_0\|_{L^2}} = \frac{1}{\sqrt{3}} \approx 0.57735.$$
- By odd/even trigonometric parity across $[0, 2\pi]^3$, the global stretching integral at $t = 0$ vanishes: $P(0) = \int_{\mathbb{T}^3} \omega_0 \cdot S_0 \omega_0\,dx = 0$, so $\mathcal{A}(0) = 0$.
- However, unlike Beltrami flows, the Lamb vector $u_0 \times \omega_0$ has a non-trivial solenoidal projection $\mathbb{P}(u_0 \times \omega_0) \ne \mathbf{0}$, generating pressure-strain and triad interactions at $O(t)$ that break the $t=0$ reflection cancellation:
  $$\frac{dP}{dt}\Big|_{t=0} > 0, \qquad P(t) = c_{\text{TG}}\,t + O(t^2) > 0 \quad (t > 0 \text{ small}).$$
- For sufficiently small viscosity $\nu < \nu_{\text{crit}}$ (e.g., $\nu \le 0.01$), $P(t)$ rapidly exceeds $D(t) = \nu\|\nabla\omega(t)\|_{L^2}^2$, driving $\mathcal{A}(t) > 1$, increasing $\|\omega(t)\|_{L^2}^2$, and shrinking $\bar{\ell}_\omega(t) = \|\omega(t)\|_{L^2}/\|\nabla\omega(t)\|_{L^2}$ below $1/\sqrt{3}$ as energy cascades into dyadic shells $|k| \ge \sqrt{5}$.

### 3.4 Testbed 5 & 6: Lamb–Oseen vs. Burgers Vortex (External Strain Caveat)
- **Lamb–Oseen Vortex**: $\omega(r,t) = \frac{\Gamma}{4\pi\nu t}e^{-r^2/(4\nu t)}\mathbf{e}_z$ has $\omega \cdot S\omega \equiv 0$, $P(t) \equiv 0$, $\mathcal{A}(t) \equiv 0$, and its core scale grows diffusively as $\ell_\omega(t) \propto \sqrt{\nu t} \to \infty$.
- **Burgers Vortex**: Adding the axisymmetric uniaxial straining field $u_{\text{ext}}(x,y,z) = (-\frac{\alpha}{2}x, -\frac{\alpha}{2}y, \alpha z)$ ($\alpha > 0$) produces $\lambda_\omega = \alpha > 0$ along $\mathbf{e}_z$. Radial inward convection $-\frac{\alpha}{2}r\partial_r \omega_z$ balances radial diffusion $\nu r^{-1}\partial_r(r\partial_r \omega_z)$ at the steady Burgers radius $r_B = \sqrt{4\nu/\alpha}$, where $\mathcal{R}_{\omega,\text{signed}} = \alpha r_B^2 / (4\nu) = 1$ and global production equals dissipation ($\mathcal{A} = 1$).
- **Falsification Warning on Burgers Vortex**: $u_{\text{ext}}$ grows linearly at infinity ($|u_{\text{ext}}(x)| \propto |x|$, infinite kinetic energy on $\mathbb{R}^3$ and incompatible with periodicity on $\mathbb{T}^3$). On $\mathbb{T}^3$ with $f = 0$, any large-scale straining cell $S_{\text{low}}$ loses energy to both viscous damping and the back-reaction of the stretched vortex tube. Therefore, **a steady Burgers vortex cannot be invoked as an autonomous self-focusing mechanism on $\mathbb{T}^3$**; a valid periodic mechanism must explain how $S[\omega]$ is regenerated dynamically by $\omega$ itself!
