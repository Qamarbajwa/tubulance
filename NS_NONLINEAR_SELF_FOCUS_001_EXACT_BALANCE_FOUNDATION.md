# NS_NONLINEAR_SELF_FOCUS_001_EXACT_BALANCE_FOUNDATION

## Exact Local and Global Enstrophy Balances, Dyadic Scale-Local Transfer, Pressure-Hessian Coupling, and Project Integration (`NS-NONLINEAR-SELF-FOCUS-001`)

| Field | Value |
| :--- | :--- |
| **Programme ID** | `NS-NONLINEAR-SELF-FOCUS-001` |
| **Locked Target** | Unforced 3D Incompressible Navier–Stokes on $\mathbb{T}^3 = (\mathbb{R}/2\pi\mathbb{Z})^3$, $\nu > 0$, $f \equiv 0$ |
| **Clay Statement B** | `UNRESOLVED` |
| **Release / Deployment** | `NO-GO` / `NONE` |
| **`NS-OPENAI-B2` Status** | `BLOCKED` |
| **Active Governance** | `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3` (`NS-GOV-MIG-V404-001 = MIGRATION_BLOCKED`) |
| **Mathematical Authority** | `Mathematical Research Constitution v1.0.1` |

---

## 1. Why Forward Nonlinear Self-Focusing Differs Fundamentally from Linear Precursor Reconstruction (Section 6)

In the closed OpenAI unforced transfer branch (`NS-EXT-OPENAI-001` $\to$ `NS-OPENAI-B1-REASSESSMENT-R4`), the mathematical question was an **inverse / reachability problem** for the periodic linearized advection-diffusion operator $\mathcal{U}_{\mathbf{u}_B}(t_j, t_{j-1})$:
- Given a prescribed spatially localized ($R_j = 2^{-j/2}$), ultrahigh-frequency ($\kappa_j \asymp \exp(2^{jh})$) two-family Kelvin wave packet at the end of a burst window $t_j$, could a smooth finite-energy initial state $\mathbf{w}(t_{j-1})$ evolve into that target under linear advection by a smooth background $\mathbf{u}_B$?
- Because linear transport by a smooth background $\mathbf{u}_B$ over $\Delta t_j = 2^{-j}$ can stretch wavenumbers by at most $\exp\!\big(\int_{t_{j-1}}^{t_j} \|\nabla \mathbf{u}_B\|_{L^\infty}\,ds\big) = O(1)$ whenever $\gamma_j \Delta t_j \asymp 1$, the initial state $\mathbf{w}(t_{j-1})$ was forced to already reside at wavenumber $\kappa_{\text{init}} \asymp \kappa_j \asymp \exp(2^{jh})$. It therefore suffered the catastrophic backward-heat amplification barrier $\exp(+\nu \kappa_j^2 \Delta t_j) \ge \exp(c\,2^{-jh}\exp(2\cdot 2^{jh}))$ (`CLM-040`).

By contrast, **forward non-perturbative self-focusing** is a **forward initial-value problem** for the full nonlinear Navier–Stokes equations:
1. **No backward heat inversion is required**: Initial data $u_0 \in C^\infty_\sigma(\mathbb{T}^3)$ begins entirely at $O(1)$ wavenumbers ($|k| \sim 1$) with finite energy $\|u_0\|_{L^2}^2 = 2\mathcal{E}_0$ and finite enstrophy $\|\omega_0\|_{L^2}^2$.
2. **Scale-local quadratic triad generation**: The nonlinear convective/stretching bilinear form $\mathbb{P}(u \cdot \nabla u)$ or $\nabla \times (u \times \omega) = (\omega \cdot \nabla)u - (u \cdot \nabla)\omega$ couples Fourier modes $k = p + q$, transferring energy and enstrophy **forward** shell-by-shell ($2^q \to 2^{q+1} \to 2^{q+2}$).
3. **Dynamic amplification of the straining field itself**: Unlike a fixed background $\mathbf{u}_B$ with prescribed $\|\nabla \mathbf{u}_B\|_{L^\infty}$, the strain tensor $S[\omega] = \frac{1}{2}(\nabla K_{\text{BS}} * \omega + (\nabla K_{\text{BS}} * \omega)^\top)$ grows simultaneously with $\omega$ via the singular Biot–Savart / Calderón–Zygmund operator ($\|S\|_{L^p} \asymp \|\omega\|_{L^p}$ for $1 < p < \infty$). Thus the local turnover rate $|S(x,t)|$ accelerates as the active length scale $\ell_\omega(x,t)$ shrinks.

---

## 2. Exact Local Enstrophy Balance Identity (`EXACT_IDENTITY`, Section 7)

Let $u: [0,T] \times \mathbb{T}^3 \to \mathbb{R}^3$ be a smooth solution of the unforced 3D incompressible Navier–Stokes equations:
$$\partial_t u + (u \cdot \nabla)u + \nabla p = \nu \Delta u, \qquad \operatorname{div} u = 0.$$
Taking the curl $\omega := \nabla \times u$ eliminates the pressure gradient $\nabla \times \nabla p \equiv 0$ and yields the exact vorticity transport-stretching equation (`EXACT_IDENTITY`):
$$\partial_t \omega + (u \cdot \nabla)\omega = (\omega \cdot \nabla)u + \nu \Delta \omega.$$

Decomposing the velocity gradient tensor $\nabla u$ into its symmetric part (strain rate tensor $S$) and skew-symmetric part (vorticity tensor $\Omega$):
$$(\nabla u)_{ij} = \partial_j u_i = S_{ij} + \Omega_{ij}, \qquad S_{ij} := \frac{1}{2}(\partial_j u_i + \partial_i u_j), \qquad \Omega_{ij} := \frac{1}{2}(\partial_j u_i - \partial_i u_j) = -\frac{1}{2}\epsilon_{ijk}\omega_k,$$
we have $(\omega \cdot \nabla)u_i = \omega_j \partial_j u_i = S_{ij}\omega_j + \frac{1}{2}(\omega \times \omega)_i = (S\omega)_i$.
Taking the inner product with $\omega(x,t)$ and using the vector calculus identity $\omega \cdot \Delta \omega = \frac{1}{2}\Delta(|\omega|^2) - |\nabla \omega|^2$ (where $|\nabla \omega|^2 := \sum_{i,j=1}^3 (\partial_j \omega_i)^2$), we obtain the **Exact Local Enstrophy Balance Identity** (`EXACT_IDENTITY`):

$$\boxed{\frac{1}{2}(\partial_t + u \cdot \nabla)|\omega(x,t)|^2 = \underbrace{\omega(x,t) \cdot S(x,t)\omega(x,t)}_{\text{local vortex stretching production}} + \underbrace{\frac{\nu}{2}\Delta|\omega(x,t)|^2}_{\text{spatial viscous redistribution}} - \underbrace{\nu|\nabla\omega(x,t)|^2}_{\text{pointwise palinstrophy dissipation}}}$$

Every term has an exact physical and mathematical role:
- $\frac{1}{2}(\partial_t + u \cdot \nabla)|\omega|^2$: Material derivative of local enstrophy density along Lagrangian fluid trajectories $X(a,t)$;
- $\omega \cdot S\omega$: Local quadratic-in-$\omega$, linear-in-$S$ vortex stretching production (cubic in $\nabla u$), which can be positive, zero, or negative depending on the alignment of $\omega$ with the principal eigenvectors of $S$;
- $\frac{\nu}{2}\Delta|\omega|^2$: Viscous spatial diffusion of enstrophy density (integrates to zero over $\mathbb{T}^3$, and is $\le 0$ at any spatial local maximum of $|\omega(\cdot,t)|^2$);
- $-\nu|\nabla\omega|^2$: Strictly non-positive pointwise viscous dissipation of enstrophy (palinstrophy sink).

---

## 3. Exact Global Enstrophy Balance and Amplification Diagnostic on $\mathbb{T}^3$ (Section 8)

Integrating the exact local enstrophy balance over the periodic torus $\mathbb{T}^3$ and using periodicity together with $\operatorname{div} u = 0$:
$$\int_{\mathbb{T}^3} (u \cdot \nabla)\frac{|\omega|^2}{2}\,dx = -\int_{\mathbb{T}^3} (\operatorname{div} u)\frac{|\omega|^2}{2}\,dx = 0, \qquad \int_{\mathbb{T}^3} \frac{\nu}{2}\Delta|\omega|^2\,dx = 0,$$
we obtain the **Exact Global Enstrophy Identity** (`EXACT_IDENTITY`):

$$\boxed{\frac{1}{2}\frac{d}{dt}\int_{\mathbb{T}^3} |\omega(x,t)|^2\,dx = P(t) - D(t)}$$

where:
$$P(t) := \int_{\mathbb{T}^3} \omega(x,t) \cdot S(x,t)\omega(x,t)\,dx \quad \text{(global vortex stretching production)},$$
$$D(t) := \nu \int_{\mathbb{T}^3} |\nabla\omega(x,t)|^2\,dx \quad \text{(global viscous enstrophy dissipation / palinstrophy)}.$$

### Definition 3.1 (Instantaneous Global Enstrophy Amplification Ratio, `PROJECT_DIAGNOSTIC`)
For any non-trivial smooth divergence-free velocity field $u(\cdot,t)$ on $\mathbb{T}^3$ with $\|\omega(t)\|_{L^2(\mathbb{T}^3)} > 0$ (so $D(t) \ge \nu \|\omega(t)\|_{L^2(\mathbb{T}^3)}^2 > 0$ by the Poincaré inequality on mean-zero vorticity $\int_{\mathbb{T}^3}\omega\,dx = 0$), define the dimensionless amplification ratio:

$$\boxed{\mathcal{A}(t) := \frac{P(t)}{D(t)} = \frac{\int_{\mathbb{T}^3} \omega(x,t) \cdot S(x,t)\omega(x,t)\,dx}{\nu \int_{\mathbb{T}^3} |\nabla\omega(x,t)|^2\,dx}}$$

Then the global enstrophy evolution obeys the exact identity:
$$\frac{1}{2}\frac{d}{dt}\|\omega(t)\|_{L^2(\mathbb{T}^3)}^2 = D(t)\big(\mathcal{A}(t) - 1\big).$$
Hence:
- $\mathcal{A}(t) > 1 \iff \frac{d}{dt}\|\omega(t)\|_{L^2}^2 > 0$ (instantaneous global enstrophy amplification);
- $\mathcal{A}(t) = 1 \iff \frac{d}{dt}\|\omega(t)\|_{L^2}^2 = 0$ (instantaneous stretching–dissipation equilibrium);
- $\mathcal{A}(t) < 1 \iff \frac{d}{dt}\|\omega(t)\|_{L^2}^2 < 0$ (instantaneous global viscous enstrophy decay).

---

## 4. Signed Alignment $\lambda_\omega$ versus Magnitude (Section 10)

On the open support $\Omega_+(t) := \{x \in \mathbb{T}^3 : |\omega(x,t)| > 0\}$, define the unit vorticity direction field and signed axial stretching rate (`EXACT_IDENTITY` / `PROJECT_DIAGNOSTIC`):
$$\xi(x,t) := \frac{\omega(x,t)}{|\omega(x,t)|} \in \mathbb{S}^2, \qquad \lambda_\omega(x,t) := \xi(x,t)^\top S(x,t)\xi(x,t),$$
with $\lambda_\omega(x,t) := 0$ where $\omega(x,t) = 0$. Then identically on $\mathbb{T}^3$:
$$\omega(x,t) \cdot S(x,t)\omega(x,t) = \lambda_\omega(x,t)\,|\omega(x,t)|^2.$$

Since $S(x,t)$ is real symmetric and trace-free ($\operatorname{tr}(S) = \operatorname{div} u = 0$), it possesses three real eigenvalues ordered as:
$$\lambda_1(x,t) \ge \lambda_2(x,t) \ge \lambda_3(x,t), \qquad \lambda_1 + \lambda_2 + \lambda_3 = 0, \qquad \lambda_1 \ge 0 \ge \lambda_3,$$
with corresponding orthonormal eigenvectors $\mathbf{e}_1(x,t), \mathbf{e}_2(x,t), \mathbf{e}_3(x,t)$. Expanding $\xi = \sum_{k=1}^3 (\xi \cdot \mathbf{e}_k)\mathbf{e}_k = \sum_{k=1}^3 \cos\theta_k\,\mathbf{e}_k$ with $\sum_{k=1}^3 \cos^2\theta_k = 1$, we obtain:

$$\boxed{\lambda_\omega(x,t) = \lambda_1(x,t)\cos^2\theta_1(x,t) + \lambda_2(x,t)\cos^2\theta_2(x,t) + \lambda_3(x,t)\cos^2\theta_3(x,t)}$$

### Critical Alignment Distinctions
1. **Large Strain Magnitude Without Stretching ($\lambda_\omega \le 0$ despite $|S| \gg 1$)**:
   - In any 2D flow or pure shear flow ($u = (f(y), 0, 0)$), $\lambda_1 = \frac{1}{2}|f'(y)|$, $\lambda_2 = 0$, $\lambda_3 = -\frac{1}{2}|f'(y)|$, and $\xi = (0,0,\pm 1) = \pm \mathbf{e}_2$. Hence $\cos\theta_1 = \cos\theta_3 = 0$, $\cos^2\theta_2 = 1$, and $\lambda_\omega = \lambda_2 = 0$ identically!
   - Even in fully 3D flows, if $\xi$ aligns predominantly with the intermediate eigenvector $\mathbf{e}_2$ when $\lambda_2 \le 0$ (axisymmetric extension / sheet formation $\lambda_1 > 0 > \lambda_2 \ge \lambda_3$) or with the compressive eigenvector $\mathbf{e}_3$, then $\lambda_\omega \le 0$, turning vortex stretching into **vortex compression** ($\omega \cdot S\omega \le 0$).
2. **Role of the Intermediate Eigenvalue $\lambda_2$ (Betchov / Neustupa–Penel / Miller)**:
   - Because $\lambda_1 + \lambda_2 + \lambda_3 = 0$ and $|S|^2 = \lambda_1^2 + \lambda_2^2 + \lambda_3^2$, Betchov's identity for homogeneous/periodic turbulence states that $\int_{\mathbb{T}^3} \det(S)\,dx = \int_{\mathbb{T}^3} \lambda_1\lambda_2\lambda_3\,dx = -\frac{1}{3}\int_{\mathbb{T}^3}\operatorname{tr}(S^3)\,dx = \frac{1}{4}\int_{\mathbb{T}^3} \omega \cdot S\omega\,dx$ (up to pressure-strain commutator terms). Positive global production $P(t) > 0$ statistically correlates with $\lambda_2 > 0$ (biaxial strain / vortex sheet-to-tube collapse $\lambda_1 \ge \lambda_2 > 0 > \lambda_3 = -(\lambda_1+\lambda_2)$).

---

## 5. Dyadic / Littlewood–Paley Scale-Local Enstrophy Balance (Sections 14 & 15)

Let $\{\Delta_q\}_{q \ge 0}$ be a smooth periodic Littlewood–Paley dyadic partition of unity on $\mathbb{T}^3$ (with $\sum_{q=0}^\infty \Delta_q \omega = \omega$ for mean-zero $\omega$, where $\Delta_q$ localizes Fourier frequencies to the dyadic shell $\mathcal{C}_q = \{k \in \mathbb{Z}^3 \setminus \{0\} : \frac{3}{4}2^q \le |k| \le \frac{8}{3}2^q\}$ and $S_{q-1} := \sum_{p=0}^{q-1}\Delta_p$).
Denote $\omega_q := \Delta_q \omega$ and $u_q := \Delta_q u$, and define the $q$-shell enstrophy (`PROJECT_DIAGNOSTIC`):
$$E_q^\omega(t) := \frac{1}{2}\|\omega_q(t)\|_{L^2(\mathbb{T}^3)}^2.$$

Applying $\Delta_q$ to the vorticity equation $\partial_t \omega + \nabla \cdot (u \otimes \omega - \omega \otimes u) = \nu \Delta \omega$ and taking the $L^2(\mathbb{T}^3)$ inner product with $\omega_q$ yields the **Exact Dyadic Shell Enstrophy Balance** (`EXACT_IDENTITY`):

$$\boxed{\frac{d}{dt}E_q^\omega(t) + D_q^\omega(t) = T_q^{\text{adv}}(t) + P_q^{\text{stretch}}(t) = -\big(\Pi_q^\omega(t) - \Pi_{q-1}^\omega(t)\big) + P_q^{\text{stretch}}(t)}$$

where:
1. **Shell Viscous Dissipation (`EXACT_IDENTITY` + Bernstein Bounds)**:
   $$D_q^\omega(t) := \nu \|\nabla \omega_q(t)\|_{L^2(\mathbb{T}^3)}^2 \asymp \nu\,2^{2q}\,\|\omega_q(t)\|_{L^2(\mathbb{T}^3)}^2 = 2\nu\,2^{2q}\,E_q^\omega(t).$$
2. **Inter-Shell Advective Enstrophy Flux $T_q^{\text{adv}}(t) = -\big(\Pi_q^\omega(t) - \Pi_{q-1}^\omega(t)\big)$ (`EXACT_IDENTITY`)**:
   Using Bony's paraproduct decomposition $u \cdot \nabla \omega = T_u \nabla \omega + T_{\nabla\omega} u + R(u, \nabla\omega)$, the low-frequency advection $(S_{q-1}u \cdot \nabla)\omega_q$ is divergence-free and satisfies $\int_{\mathbb{T}^3} \omega_q \cdot (S_{q-1}u \cdot \nabla)\omega_q\,dx = 0$! Thus only the **commutator and local/high-low interactions** survive:
   $$T_q^{\text{adv}}(t) := -\int_{\mathbb{T}^3} \omega_q \cdot \Delta_q(u \cdot \nabla \omega)\,dx = -\int_{\mathbb{T}^3} \omega_q \cdot [\Delta_q, S_{q-1}u \cdot \nabla]\omega\,dx - \int_{\mathbb{T}^3} \omega_q \cdot \Delta_q\big((I - S_{q-1})u \cdot \nabla \omega\big)\,dx.$$
   Summing over all shells $q \ge 0$ gives exact conservative cancellation $\sum_{q=0}^\infty T_q^{\text{adv}}(t) = -\int_{\mathbb{T}^3} \omega \cdot (u \cdot \nabla)\omega\,dx = 0$, so $T_q^{\text{adv}}(t) = -\big(\Pi_q^\omega(t) - \Pi_{q-1}^\omega(t)\big)$ with $\Pi_q^\omega(t) := \sum_{p=0}^q \int_{\mathbb{T}^3} \omega_p \cdot \Delta_p(u \cdot \nabla\omega)\,dx$.
3. **Shell Vortex Stretching Production $P_q^{\text{stretch}}(t)$ (`EXACT_IDENTITY`)**:
   $$P_q^{\text{stretch}}(t) := \int_{\mathbb{T}^3} \omega_q \cdot \Delta_q(S\omega)\,dx = \underbrace{\int_{\mathbb{T}^3} \omega_q \cdot (S_{q-1}S)\omega_q\,dx}_{\text{large-scale strain stretching } P_{q,\text{low}}^{\text{stretch}}} + \underbrace{\int_{\mathbb{T}^3} \omega_q \cdot [\Delta_q, S_{q-1}S]\omega\,dx}_{\text{strain commutator}} + \underbrace{\int_{\mathbb{T}^3} \omega_q \cdot \Delta_q\big((I-S_{q-1})S\,\omega\big)\,dx}_{\text{scale-local self-stretching } P_{q,\text{local}}^{\text{stretch}}}.$$

### Why Scale-Local Dyadic Transfer Avoids the `CLM-040` Backward-Heat Barrier
In `CLM-040`, a linear perturbation $\mathbf{w}$ had to jump from $O(1)$ modes to $\kappa_j \asymp \exp(2^{jh})$ in a single linear step, incurring $\exp(+\nu \kappa_j^2 \Delta t_j)$ cost. In the dyadic nonlinear balance above, shell $q$ is fed directly by shell $q-1$ and local triads $|p - q| \le 2$. For shell $q$ to grow ($\frac{d}{dt}E_q^\omega > 0$), it is NOT required to overcome $\exp(+\nu 2^{2q}\Delta t)$; it only needs the instantaneous local triad rate to exceed the local shell dissipation rate:
$$\frac{T_q^{\text{adv}}(t) + P_q^{\text{stretch}}(t)}{2 E_q^\omega(t)} > \nu\,2^{2q} \iff \frac{|S_{\le q}| + \|\omega_q\|_{L^\infty}}{\nu\,2^{2q}} \gtrsim 1.$$
This is a **polynomial / dyadic scale competition** ($|S_{\le q}|\ell_q^2/\nu \gtrsim 1$ with $\ell_q = 2^{-q}$), rather than an inverse heat equation problem!

---

## 6. Nonlocal Pressure-Strain Coupling & Constantin–Fefferman Direction Coherence (Sections 16 & 17)

### 6.1 Pressure Poisson Equation and Pressure Hessian $P_{ij} = \partial_i\partial_j p$ (`EXACT_IDENTITY`)
Taking the divergence of the Navier–Stokes equation on $\mathbb{T}^3$ gives the exact pressure Poisson equation (`EXACT_IDENTITY`):
$$-\Delta p = \partial_i u_j \partial_j u_i = \operatorname{tr}(S^2) - \frac{1}{2}|\omega|^2 = |S|^2 - \frac{1}{2}|\omega|^2.$$
Using the periodic Riesz transforms $\mathcal{R}_i := \partial_i (-\Delta)^{-1/2}$ on mean-zero periodic functions, the trace-free pressure Hessian $P_{ij}^\circ := \partial_i\partial_j p - \frac{1}{3}(\Delta p)\delta_{ij}$ is given explicitly by:
$$\partial_i\partial_j p = \mathcal{R}_i \mathcal{R}_j \left(|S|^2 - \frac{1}{2}|\omega|^2\right) - \frac{1}{3}\delta_{ij}\left(|S|^2 - \frac{1}{2}|\omega|^2\right).$$
Meanwhile, the symmetric strain rate tensor $S_{ij}$ satisfies the exact evolution equation (`EXACT_IDENTITY`):
$$(\partial_t + u \cdot \nabla)S_{ij} + S_{ik}S_{kj} - \frac{1}{4}\left(\omega_i\omega_j - |\omega|^2\delta_{ij}\right) + \partial_i\partial_j p = \nu \Delta S_{ij}.$$
Contracting with $\xi_i \xi_j$ (along the vorticity unit vector $\xi = \omega/|\omega|$ where $\omega_i\omega_j \xi_i\xi_j - |\omega|^2 = 0$), the local vorticity term $\frac{1}{4}(\omega_i\omega_j - |\omega|^2\delta_{ij})$ **vanishes identically along $\xi$**! Specifically:
$$\xi_i\xi_j \left(\omega_i\omega_j - |\omega|^2\delta_{ij}\right) = |\omega|^2 (\xi \cdot \xi)^2 - |\omega|^2 (\xi \cdot \xi) = 0.$$
Consequently, the Lagrangian evolution of the axial stretching rate $\lambda_\omega = \xi^\top S \xi$ satisfies the exact Ohkitani–Vieillefosse–Constantin identity (`EXACT_IDENTITY`):

$$\boxed{(\partial_t + u \cdot \nabla)\lambda_\omega = |S\xi|^2 - 2\lambda_\omega^2 - \xi^\top (\nabla \nabla p)\xi + \nu\,\xi^\top (\Delta S)\xi + \frac{2\nu}{|\omega|}\xi^\top S \big(\Delta\omega - (\xi \cdot \Delta\omega)\xi\big)}$$

This identity reveals a fundamental structural mechanism of 3D Navier–Stokes:
- Local vorticity $\omega(x,t)$ **cannot directly amplify its own axial strain component $\lambda_\omega(x,t)$ through the local quadratic term $\frac{1}{4}(\omega_i\omega_j - |\omega|^2\delta_{ij})$** because that tensor vanishes along $\xi$!
- Instead, sustained growth of $\lambda_\omega$ depends entirely on the **nonlocal pressure Hessian projection** $-\xi^\top (\nabla\nabla p)\xi = \xi_i\xi_j \mathcal{R}_i\mathcal{R}_j\big(\frac{1}{2}|\omega|^2 - |S|^2\big) + \frac{1}{3}\big(\frac{1}{2}|\omega|^2 - |S|^2\big)$. Thus self-focusing in 3D Navier–Stokes is inherently **nonlocal**: surrounding vortex tubes or antiparallel pairs must generate a negative axial pressure curvature $\xi^\top (\nabla\nabla p)\xi < 0$ to counteract the Riccati self-damping $-S_{ik}S_{kj}\xi_i\xi_j$.

### 6.2 Constantin–Fefferman Vorticity Direction Coherence (Section 17)
By the singular integral representation of $S[\omega]$ on $\mathbb{T}^3$ (Constantin 1994), for $x \in \mathbb{T}^3$:
$$S(x,t) = \frac{3}{4\pi}\operatorname{P.V.}\int_{\mathbb{R}^3} \frac{1}{|y|^5}\left[\frac{1}{2}\big(y \otimes (y \times \omega(x-y,t)) + (y \times \omega(x-y,t)) \otimes y\big)\right]dy,$$
so the local stretching rate $\lambda_\omega(x,t) = \xi(x,t)^\top S(x,t)\xi(x,t)$ takes the exact geometric singular integral form (`EXACT_IDENTITY`):

$$\boxed{\lambda_\omega(x,t) = \frac{3}{4\pi}\operatorname{P.V.}\int_{\mathbb{R}^3} D(\hat{y}, \xi(x,t), \xi(x-y,t))\,\frac{|\omega(x-y,t)|}{|y|^3}\,dy}$$

where $\hat{y} = y/|y|$ and the geometric kernel is:
$$D(\hat{y}, \xi_1, \xi_2) := (\hat{y} \cdot \xi_1)\big(\hat{y} \cdot (\xi_1 \times \xi_2)\big).$$
Because $\xi_1 \times \xi_2 = (\xi_1 - \xi_2) \times \xi_1$ vanishes identically when $\xi(x-y,t) = \pm \xi(x,t)$, we have the **exact geometric depletion inequality**:
$$|D(\hat{y}, \xi(x,t), \xi(x-y,t))| \le |\xi(x,t) \times \xi(x-y,t)| = |\sin\angle(\xi(x,t), \xi(x-y,t))| \le |\xi(x,t) - \xi(x-y,t)|.$$
- **If $\xi$ is directionally coherent** on the dissipative scale ($|\xi(x)-\xi(y)| \le |x-y|/\rho$ for $|x-y| \le r$), the singular $|y|^{-3}$ kernel is regularized to $|y|^{-2}/\rho$, depleting $\lambda_\omega(x,t)$ and preventing blowup (Constantin–Fefferman 1993).
- **Therefore, any genuine forward self-focusing mechanism must create multi-directional vorticity curvature** ($|\nabla \xi| \sim \rho^{-1} \gtrsim \ell_\omega^{-1}$, such as antiparallel colliding tubes with helical core twisting or orthogonal intersecting tubes) within a ball of radius $\ell_\omega(t)$ so that $D(\hat{y}, \xi(x), \xi(x-y))$ stays $O(1)$ across $|y| \sim \ell_\omega(t)$.

---

## 7. Integration with Existing Project Mathematical Objects (Section 19)

| Existing Project Object | Source Milestone / Claim | Exact Mathematical Connection to `NS-NONLINEAR-SELF-FOCUS-001` |
| :--- | :--- | :--- |
| **Pressure-Strain Alignment Operator $\Xi[\omega]$** | `TP2-G6-A1` (`CLM-033`) | $\Xi[\omega](x,t) := \omega_i (\partial_i\partial_j p)\omega_j = |\omega|^2\,\xi^\top(\nabla\nabla p)\xi$. Appears with a minus sign directly in the Ohkitani–Vieillefosse evolution equation for $\lambda_\omega$: $(\partial_t + u\cdot\nabla)\lambda_\omega = |S\xi|^2 - 2\lambda_\omega^2 - |\omega|^{-2}\Xi[\omega] + \nu\text{-terms}$. Negative $\Xi[\omega] < 0$ is the exact nonlocal pressure-Hessian driver required to sustain $\lambda_\omega > 0$. |
| **Strain Condition Number / Eigenvalue Ratio $\kappa_\sigma(S)$** | `TP2-G6-A1` / `TP2-G6-B-R1` | Relates the principal strain eigenvalues $\lambda_1 \ge \lambda_2 \ge \lambda_3$ ($\sum \lambda_i = 0$). Biaxial extension ($\lambda_2 > 0$, $\lambda_2/\lambda_1 \in (0, 1]$) maximizes the solid angle of $\mathbb{S}^2$ on which $\lambda_\omega(\xi) = \sum \lambda_i \cos^2\theta_i > 0$. |
| **Two-Particle Relative Dispersion & Jet Regularity** | `TP2-G6-C1` (`CLM-035`) | Tracks $\delta X(t) = X(a+h,t) - X(a,t)$ and common-mode cancellation in the stochastic representation $\omega(x,t) = \mathbb{E}[(\nabla X)\omega_0(X^{-1})]$. Forward shrinking of $\ell_\omega(t) \to 0$ corresponds to rapid divergence of backward two-particle trajectories $|\delta X|/\ell_\omega$ across the active filament boundary. |
| **Deformable vs. Rigid Branch Obstructions** | `TP2-G6-B-R1` / `TP2-G6-B-R2` | Showed that rigid rotation ($\nabla\xi \equiv 0$, $\Omega \gg S$) yields zero stretching ($\lambda_\omega = 0$), whereas pure deformable strain without rotation suffers Riccati blowup saturation unless replenished by $\Xi[\omega] < 0$ and multi-directional curvature $|\nabla\xi| \sim \ell_\omega^{-1}$. |
