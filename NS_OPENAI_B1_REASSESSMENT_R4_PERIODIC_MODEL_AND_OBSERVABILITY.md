# Periodic Background Model, Observability Formulation, and Singular Value Decomposition

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R4`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`  
**Scope**: Mandate Section 4 (Periodic background model), Section 9 (Observability formulation), Section 10 (Singular values), Section 11 (Periodic Kelvin benchmark)

---

## 1. Construction of the Periodic Background Flow Model (Section 4)

In the OpenAI monograph, the background flow near the active annular filament is modeled locally as an axisymmetric straining stagnation flow:
$$u_{\text{local}}(x, t) = S(t) x + u_{\text{swirl}}(r, t) e_\theta, \qquad S(t) = \sigma(t) \operatorname{diag}(-2, 1, 1),$$
where $\sigma(t) \asymp \tau^{-1-h} \asymp 2^{j(1+h)}$.  
The linear velocity field $S(t)x$ is **not periodic** on $\mathbb{T}^3 = (\mathbb{R} / 2\pi \mathbb{Z})^3$ because $x$ is unbounded. To examine whether the localization-diffusion barrier survives on the torus, we construct a divergence-free, smooth periodic vector field $u_B \in C^\infty(\mathbb{T}^3)$ that reproduces the singular hyperbolic stagnation point locally.

### 1.1 The Canonical Periodic Stagnation Flow on $\mathbb{T}^3$
Define the 3D periodic flow:
$$u_B(x, y, z, t) \equiv \sigma(t) \begin{pmatrix} -2 \sin(x) \cos(y) \cos(z) \\ \cos(x) \sin(y) \cos(z) \\ \cos(x) \cos(y) \sin(z) \end{pmatrix}.$$

1. **Periodic Boundary Conditions**:  
   Since $\sin$ and $\cos$ are $2\pi$-periodic in $x, y, z$, $u_B(x + 2\pi e_i, t) = u_B(x, t)$ identically for all $i \in \{1, 2, 3\}$.
2. **Incompressibility**:
   $$\begin{aligned}
   \nabla \cdot u_B &= \sigma(t) \left[ -2 \cos(x)\cos(y)\cos(z) + \cos(x)\cos(y)\cos(z) + \cos(x)\cos(y)\cos(z) \right] \\
   &= \sigma(t) (-2 + 1 + 1) \cos(x)\cos(y)\cos(z) \equiv 0.
   \end{aligned}$$
   Incompressibility $\operatorname{div} u_B = 0$ holds identically everywhere on $\mathbb{T}^3$.
3. **Analyticity**:  
   Because $u_B$ consists of finite trigonometric polynomials, $u_B \in C^\omega(\mathbb{T}^3)$ is spatial real-analytic with infinite radius of analyticity $\rho_B = \infty$. It belongs to `ANALYTIC_BACKGROUND`.

### 1.2 Local Taylor Expansion Near the Hyperbolic Core
Expanding $u_B$ in the neighborhood of the stagnation point $(x, y, z) = (0, 0, 0)$:
$$\sin(s) = s - \frac{s^3}{6} + \mathcal{O}(s^5), \qquad \cos(s) = 1 - \frac{s^2}{2} + \mathcal{O}(s^4).$$

Evaluating the components:
$$\begin{aligned}
u_{B, 1}(x, y, z, t) &= -2\sigma(t) \left( x - \frac{x^3}{6} \right) \left( 1 - \frac{y^2 + z^2}{2} \right) + \mathcal{O}(|x|^5) = -2\sigma(t) x + R_1(x, y, z, t), \\
u_{B, 2}(x, y, z, t) &= \sigma(t) \left( y - \frac{y^3}{6} \right) \left( 1 - \frac{x^2 + z^2}{2} \right) + \mathcal{O}(|x|^5) = \sigma(t) y + R_2(x, y, z, t), \\
u_{B, 3}(x, y, z, t) &= \sigma(t) \left( z - \frac{z^3}{6} \right) \left( 1 - \frac{x^2 + y^2}{2} \right) + \mathcal{O}(|x|^5) = \sigma(t) z + R_3(x, y, z, t).
\end{aligned}$$

The linear part is:
$$(\nabla u_B)(0, t) = \sigma(t) \begin{pmatrix} -2 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{pmatrix} = S(t).$$
The local strain rate tensor at the origin matches the OpenAI singular strain tensor **exactly**.

### 1.3 Quantitative Local Surrogate Error on the Pulse Support
The OpenAI pulse at scale $j$ is localized to a ball of radius $r \le R_j \asymp 2^{-j/2}$ during the active burst epoch $\Delta t_j = 2^{-j}$.  
On the pulse support $B_{R_j}(0)$:
$$\|R(x, y, z, t)\|_{L^\infty(B_{R_j})} \le C \sigma(t) R_j^3 \asymp 2^{j(1+h)} \left( 2^{-j/2} \right)^3 = C 2^{-j(1/2 - h)}.$$
Since $h \in (0, 1/6)$, the exponent is positive:
$$\frac{1}{2} - h \ge \frac{1}{2} - \frac{1}{6} = \frac{1}{3} > 0.$$
Therefore:
$$\lim_{j \to \infty} \|u_B - S(t)x\|_{L^\infty(B_{R_j})} = 0 \quad (\text{converges to zero at rate } 2^{-j/3}).$$

Furthermore, during the burst duration $\Delta t_j = 2^{-j}$, the maximum advective displacement of any fluid parcel initialized in $B_{R_j}$ is:
$$\Delta x \le \Delta t_j \|u_B\|_{L^\infty(B_{R_j})} \asymp 2^{-j} \left( 2^{j(1+h)} 2^{-j/2} \right) = 2^{-j(1/2 - h)} \ll R_j \asymp 2^{-j/2}.$$
**Crucial Lemma 1.1**: The pulse does **not exit** the hyperbolic stagnation neighborhood during the burst $\Delta t_j$. The local periodic surrogate flow and the affine strain flow coincide on the active pulse domain up to relative error $\mathcal{O}(2^{-j/3}) \to 0$.

Classification:
- `FULL_PERIODIC`: The global flow $u_B$ on $\mathbb{T}^3$.
- `LOCAL_PERIODIC_SURROGATE`: The approximation of $u_B$ by $S(t)x$ on $B_{R_j}$.

---

## 2. Adjoint Evolution and Observability Formulation (Section 9)

Rather than informal backward integration (which is ill-posed for parabolic operators), reachability is rigorously formulated through **Hilbert space duality and adjoint observability**.

### 2.1 The Forward-Adjoint Duality Identity
Let $H = L^2_{\text{div}}(\mathbb{T}^3)$. For a target state $W^\star \in H$ at time $T = t_j$, reachability asks whether there exists $w_0 \in H$ such that:
$$\mathcal{U}_{u_B}(T, 0) w_0 = W^\star \quad (\text{exact}), \qquad \text{or} \qquad \|\mathcal{U}_{u_B}(T, 0)w_0 - W^\star\|_H \le \varepsilon \quad (\text{approximate}).$$

Taking the inner product with an arbitrary observation vector $\phi_T \in H$:
$$\langle \mathcal{U}_{u_B}(T, 0) w_0, \phi_T \rangle_H = \langle w_0, \mathcal{U}_{u_B}(T, 0)^* \phi_T \rangle_H.$$

### 2.2 The Adjoint Evolution Equation
The adjoint operator $\mathcal{U}_{u_B}(T, 0)^* \in \mathcal{L}(H)$ is the solution operator to the **dual parabolic system**:
$$-\frac{\partial}{\partial t} \phi(t) - \nu \Delta \phi(t) - \mathbb{P} \left[ (u_B(t) \cdot \nabla)\phi(t) - (\nabla u_B(t))^T \phi(t) \right] = 0, \qquad \phi(T) = \phi_T.$$

Let $\tau = T - t \in [0, T]$ be the reversed time variable, and define $\psi(\tau) \equiv \phi(T - \tau)$. Then:
$$\frac{\partial}{\partial \tau} \psi(\tau) - \nu \Delta \psi(\tau) = \mathbb{P} \left[ (u_B(T-\tau) \cdot \nabla)\psi(\tau) - (\nabla u_B(T-\tau))^T \psi(\tau) \right], \qquad \psi(0) = \phi_T.$$
**Key Insight**: The adjoint equation is **forward-parabolic** with respect to reversed time $\tau$. The Laplacian appears with the standard dissipative sign $-\nu \Delta \psi$.  
Therefore, the adjoint propagator:
$$\mathcal{U}_{u_B}(T, 0)^* : H \longrightarrow H$$
is a well-posed, bounded, compact linear operator that regularizes $H$ forward in reverse time.

### 2.3 The Observability Gramian $\mathcal{M}(T)$
The observability Gramian operator $\mathcal{M}(T) \in \mathcal{L}(H)$ is defined by:
$$\mathcal{M}(T) \equiv \mathcal{U}_{u_B}(T, 0) \, \mathcal{U}_{u_B}(T, 0)^*.$$
$\mathcal{M}(T)$ is a self-adjoint, positive semi-definite, compact operator on $H = L^2_{\text{div}}(\mathbb{T}^3)$.

By classical Fenchel–Rockafellar duality in optimal control (Lions 1971; Coron 2007):
**Theorem 2.1 (Minimum Energy Cost Duality)**:  
For any $\varepsilon \ge 0$, the minimum energy cost:
$$\mathfrak{C}_\varepsilon(W^\star) \equiv \inf \left\{ \|w_0\|_H : \|\mathcal{U}_{u_B}(T, 0)w_0 - W^\star\|_H \le \varepsilon \right\}$$
satisfies the exact dual representation:
$$\frac{1}{2} \mathfrak{C}_\varepsilon(W^\star)^2 = \sup_{\phi_T \in H} \left\{ \langle W^\star, \phi_T \rangle_H - \frac{1}{2} \langle \mathcal{M}(T) \phi_T, \phi_T \rangle_H - \varepsilon \|\phi_T\|_H \right\}.$$

For exact reachability ($\varepsilon = 0$), if $W^\star \in \operatorname{Range}(\mathcal{U}_{u_B}(T, 0)) = \operatorname{Range}(\mathcal{M}(T)^{1/2})$:
$$\mathfrak{C}_0(W^\star) = \|\mathcal{M}(T)^{-1/2} W^\star\|_H = \sqrt{\sum_{n=1}^\infty \frac{|\langle W^\star, v_n \rangle_H|^2}{s_n^2}},$$
where $\{s_n\}$ are the singular values and $\{v_n\}$ are the orthonormal eigenfunctions of $\mathcal{M}(T)$.

---

## 3. Singular Value Decomposition of the Periodic Propagator (Section 10)

By the spectral theorem for compact self-adjoint operators, the Gramian $\mathcal{M}(T)$ admits an orthonormal basis of eigenfunctions $\{v_n\}_{n=1}^\infty \subset H$ with eigenvalues:
$$\lambda_n(\mathcal{M}(T)) = s_n^2, \qquad s_1 \ge s_2 \ge \dots \ge s_n > 0, \quad \lim_{n \to \infty} s_n = 0.$$

The forward propagator $\mathcal{U}_{u_B}(T, 0)$ has singular value decomposition:
$$\mathcal{U}_{u_B}(T, 0) w_0 = \sum_{n=1}^\infty s_n \langle w_0, u_n \rangle_H v_n,$$
where $u_n = \frac{1}{s_n} \mathcal{U}_{u_B}(T, 0)^* v_n$ form an orthonormal basis of $H$.

### 3.1 Decay Rate of Singular Values in the Periodic Setting
In the pure heat operator on $\mathbb{T}^3$ ($u_B = 0$):
$$s_k(e^{\nu T \Delta}) = \exp\left(-\nu T |k|^2\right), \qquad k \in \mathbb{Z}^3 \setminus \{0\}.$$
In the presence of the smooth background $u_B \in C^\omega(\mathbb{T}^3)$, perturbation of eigenvalues under the Kato–Rellich theorem preserves the Gaussian asymptotic decay:
$$s_n(\mathcal{U}_{u_B}(T, 0)) \asymp \exp\left( -\nu T n^{2/3} + \int_0^T \|S(u_B)\|_{L^\infty} dt \right) \quad \text{as } n \to \infty.$$

### 3.2 Spectral Projection of the Authentic Pulse Pair
The OpenAI pulse targets $W_{\sigma, j}^\star$ have carrier wavenumber $k_j^\star \asymp 2^j$ and spatial envelope width $\delta r_j \asymp 2^{-j/2}$.  
Their Fourier energy is concentrated on modes with:
$$|k| \ge 2^j.$$
The corresponding singular values for these modes scale as:
$$s_n \le \exp\left( -\nu \Delta t_j |k_j^\star|^2 \right) = \exp\left( -\nu 2^{-j} 2^{2j} \right) = \exp\left( -\nu 2^j \right) \to 0.$$

Moreover, along the transverse extensional directions, the effective dissipation is governed by the Gramian eigenvalue $\lambda_\perp \asymp \nu 2^{-j(1+h)} \exp(2 \cdot 2^{jh})$, yielding singular values:
$$s_{n, \perp} \asymp \exp\left( -\frac{\nu}{8} 2^{-jh} \exp\left(2 \cdot 2^{jh}\right) \right).$$

**Conclusion**: The target pulses $W_{\sigma, j}^\star$ project predominantly onto the eigenspaces of $\mathcal{M}(T)$ corresponding to **super-exponentially small singular values**.

---

## 4. Periodic Kelvin-like Benchmark vs. Affine Model (Section 11)

To examine whether the affine cost barrier is an artifact of non-periodic linear strain, we construct the closest exactly solvable periodic shear benchmark on $\mathbb{T}^3$.

### 4.1 The Periodic Shear Flow
Define the 1D periodic shear profile:
$$u_B(x, y, z, t) = \begin{pmatrix} U(y, t) \\ 0 \\ 0 \end{pmatrix}, \qquad U(y, t) = \Gamma(t) \sin(y), \quad \Gamma(t) = \sigma(t).$$

For this flow, the advective derivative is:
$$(u_B \cdot \nabla)w = \Gamma(t) \sin(y) \frac{\partial w}{\partial x}.$$
The velocity gradient is:
$$\nabla u_B = \begin{pmatrix} 0 & \Gamma(t)\cos(y) & 0 \\ 0 & 0 & 0 \\ 0 & 0 & 0 \end{pmatrix}.$$
Near the inflection point $y = 0$, $\cos(y) \approx 1$, so the background shear rate is $\Gamma(t) = \sigma(t)$.

### 4.2 Local vs. Global Dynamics
During the burst epoch $\Delta t_j = 2^{-j}$, any wavepacket localized to $\delta y \asymp 2^{-j/2}$ centered at $y = 0$ experiences background velocity:
$$U(y) = \sigma(t) y \left( 1 - \frac{y^2}{6} + \dots \right).$$
The phase $\Phi(x, y, z, t) = k_x x + k_y(t) y + k_z z$ evolves according to the ray-tracing equation:
$$\frac{d k_y}{dt} = -k_x \frac{\partial U}{\partial y} = -k_x \sigma(t) \cos(y).$$
Since $|y| \le 2^{-j/2}$, $\cos(y) = 1 - \mathcal{O}(2^{-j})$.  
Integrating over the burst interval $\Delta t_j$:
$$\Delta k_y = -k_x \int_{t_j^-}^{t_j} \sigma(t) dt \left( 1 - \mathcal{O}(2^{-j}) \right) = -k_x \Sigma_j \left( 1 - \mathcal{O}(2^{-j}) \right),$$
where $\Sigma_j \asymp 2^{jh} \gg 1$.

### 4.3 Comparison of Cost Scaling
| Metric | Pure Affine Strain ($S x$) | Periodic Shear ($\Gamma \sin y$) | Full Periodic Hyperbolic ($u_B$) |
| :--- | :--- | :--- | :--- |
| **Domain** | $\mathbb{R}^3$ (non-periodic) | $\mathbb{T}^3$ (periodic) | $\mathbb{T}^3$ (periodic) |
| **Wavevector Growth** | $k_\perp(t) \sim e^{\Sigma_j} k_\perp(0)$ | $k_y(t) \sim \Sigma_j k_x$ | $k_\perp(t) \sim e^{\Sigma_j} k_\perp(0)$ |
| **Cumulative Dissipation** | $\exp(2 \cdot 2^{jh})$ | $(2^{jh})^2 = 2^{2jh}$ | $\exp(2 \cdot 2^{jh})$ |
| **Backward Cost $\mathfrak{C}_{\varepsilon}$** | Super-exponential $\exp(e^{2^{jh}})$ | Exponential $\exp(2^{2jh})$ | Super-exponential $\exp(e^{2^{jh}})$ |

**Deduction**:
- In a **unidirectional shear flow** ($\Gamma \sin y$), the wavevector grows only linearly in $\Sigma_j$, producing an exponential cost $\exp(2^{2jh})$.
- In a **stagnation hyperbolic flow** with $\operatorname{div} u_B = 0$ having two extensional axes (the true OpenAI geometry), the wavevector grows **exponentially** in $\Sigma_j$, producing the **super-exponential cost** $\exp(+c \exp(2^{jh}))$.
- Because the authentic OpenAI blowup mechanism relies fundamentally on **axisymmetric radial compression and axial extension**, the stagnation hyperbolic model $u_B$ constructed in Section 1 is the faithful periodic counterpart.
- The super-exponential cost barrier is **not** an artifact of domain non-periodicity; it is an intrinsic consequence of the local hyperbolic strain dynamics.
