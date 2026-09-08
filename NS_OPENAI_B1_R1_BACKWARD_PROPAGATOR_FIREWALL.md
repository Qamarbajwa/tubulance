# NS-OPENAI-B1-R1 — THE BACKWARD PARABOLIC PROPAGATOR FIREWALL

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-R1 — Autonomous Precursor Cascade Realizability Re-Audit`  
**Standard**: `Mathematical Research Constitution v1.0.1`  
**Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Risk Ceiling**: `R3`  
**Focus**: Rigorous Analysis of Full Operator Invertibility $\mathcal{U}_B(t_j, 0)^{-1}$ vs Ray-Tracing De-Shearing  

---

## 1. The Operator Invertibility Problem

Let $\mathcal{U}_B(t, s): L^2_\sigma(\mathbb{T}^3) \to L^2_\sigma(\mathbb{T}^3)$ be the forward evolution operator of the linearized Navier–Stokes system:
$$\partial_t w = \mathcal{L}_B(t) w \equiv \nu \Delta w - \mathbb{P} \left[ (u_B \cdot \nabla)w + (w \cdot \nabla)u_B \right].$$

Because $\nu > 0$, the generator $\mathcal{L}_B(t)$ is a second-order elliptic operator with non-positive symmetric part:
$$\langle \nu \Delta w, w \rangle_{L^2} = - \nu \|\nabla w\|_{L^2}^2 \le - \nu (2\pi)^2 \|w\|_{L^2}^2.$$
Consequently, $\mathcal{U}_B(t, 0)$ is a **strictly parabolic, compact, smoothing semigroup**:
$$\mathcal{U}_B(t_j, 0): L^2_\sigma(\mathbb{T}^3) \longrightarrow \bigcap_{m \ge 0} H^m_\sigma(\mathbb{T}^3).$$

### 1.1 The Range Condition
To solve $W_j^\star = \mathcal{U}_B(t_j, 0) w_j(0)$ for a smooth initial datum $w_j(0)$, the target state $W_j^\star$ **must belong to the range of the forward operator**:
$$W_j^\star \in \operatorname{Ran}\left( \mathcal{U}_B(t_j, 0) \right).$$
Since $\mathcal{U}_B(t_j, 0)$ is compact on $L^2_\sigma(\mathbb{T}^3)$, its range $\operatorname{Ran}(\mathcal{U}_B(t_j, 0))$ is a **dense but non-closed, meager subspace** of $L^2_\sigma(\mathbb{T}^3)$.
The inverse operator $\mathcal{U}_B(t_j, 0)^{-1}$ is an **unbounded, discontinuous operator** defined only on $\operatorname{Ran}(\mathcal{U}_B)$.

---

## 2. The Pure Heat Analogue and the Hadamard Barrier

To expose the exact mathematical barrier, consider first the pure heat equation ($u_B \equiv 0$):
$$\partial_t w - \nu \Delta w = 0 \implies \widehat{w}(k, t_j) = e^{-\nu |k|^2 t_j} \widehat{w}(k, 0).$$
Solving for the initial state gives the formal multiplier:
$$\widehat{w}(k, 0) = e^{+\nu |k|^2 t_j} \widehat{W}_j^\star(k).$$
For $w(0)$ to exist in $L^2(\mathbb{T}^3)$, the Fourier transform $\widehat{W}_j^\star(k)$ must satisfy the Gevrey class-1 analyticity condition:
$$\sum_{k \in \mathbb{Z}^3} e^{2\nu |k|^2 t_j} |\widehat{W}_j^\star(k)|^2 < \infty.$$
If $W_j^\star$ is compactly supported or merely $C^\infty$ (such as the bump function envelope $\rho_j(x)$), its Fourier transform decays only polynomially or at best like $\exp(-c |k|)$, **NOT** $\exp(-\nu |k|^2 t_j)$!
The sum diverges catastrophically:
$$\|w(0)\|_{L^2}^2 = \sum_{k \in \mathbb{Z}^3} e^{2\nu |k|^2 t_j} |\widehat{W}_j^\star(k)|^2 = +\infty.$$
This is the classic **Hadamard ill-posedness** of the backward heat equation.

---

## 3. Why Ray De-Shearing Does NOT Prove Full PDE Invertibility

In `NS-OPENAI-B1`, the project asserted that hyperbolic strain evades this barrier by de-shearing the carrier wavevector along the characteristic:
$$\dot{k}_j = -(\nabla u_B)^T k_j \implies |k_j(0)| \le K_0 = \mathcal{O}(1).$$

### The Mathematical Flaw: Ray vs Wavepacket Spectrum
A wavepacket $W_j^\star(x)$ is **not** a single delta function $\delta(k - k_j^\star)$ in Fourier space!
By the Heisenberg uncertainty principle, a wavepacket localized in space within an annular envelope $\chi_j(x)$ of width $\delta r_j \asymp 2^{-j/2}$ possesses a **continuous Fourier spectrum of width $\Delta k \asymp 2^{j/2}$**:
$$W_j^\star(x) = \chi_j(x) e^{i k_j^\star \cdot x} \implies \widehat{W}_j^\star(k) = \widehat{\chi}_j(k - k_j^\star).$$

1. **Off-Characteristic Modes**:
   The background velocity gradient $\nabla u_B(x, t)$ is spatially localized to the core filament $r \lesssim r_j$.
   Away from the filament, or for Fourier modes $k$ whose wavevector orientation is slightly misaligned with the compressive axis $v_3$, the adjoint characteristic does **not** de-shear the wavevector!
2. **The Residual Heat Operator**:
   Splitting the solution into the WKB ray approximation and a remainder:
   $$w_j = w_{j, \text{WKB}} + \mathcal{R}_j.$$
   While $w_{j, \text{WKB}}$ satisfies an $\mathcal{O}(1)$ dissipation bound along its central ray, the remainder $\mathcal{R}_j$ is governed by:
   $$\partial_t \mathcal{R}_j - \nu \Delta \mathcal{R}_j + \mathbb{P}[(u_B \cdot \nabla)\mathcal{R}_j + (\mathcal{R}_j \cdot \nabla)u_B] = - \mathcal{S}_{\text{WKB}},$$
   where $\mathcal{S}_{\text{WKB}}$ contains spatial derivatives of the envelope $\nabla^2 \chi_j$, pressure Poisson terms, and geometric curvature terms.
3. **Backward Ill-Posedness of the Remainder**:
   Running this equation backwards from $t_j$ to $0$ with target $\mathcal{R}_j(t_j) = 0$ requires solving an inhomogeneous backward parabolic equation with spatial source terms of order $2^{j/2}$.
   The non-local Leray projector $\mathbb{P}$ spreads Fourier modes across all directions in $\mathbb{Z}^3$, feeding energy into directions that undergo **unmitigated backward heat explosion** $\exp(+\nu 2^j)$!

$$\boxed{\text{Wavevector de-shearing along one central ray does NOT bound the operator norm } \|\mathcal{U}_B(t_j, 0)^{-1}\|.}}$$

---

## 4. Exact Quantity Controlling the Inverse Operator Norm

To rigorously establish backward invertibility, one must control the **resolvent / semigroup inverse norm**:
$$\|\mathcal{U}_B(t_j, 0)^{-1}\|_{\mathcal{L}(X, Y)} = \sup_{W \in X, \|W\| \le 1} \inf \left\{ \|w_0\|_Y : \mathcal{U}_B(t_j, 0) w_0 = W \right\}.$$

In the presence of time-dependent shear $S(t) \sim \tau^{-1-h}$, the operator inverse norm is governed by the **Gramian operator**:
$$\mathcal{G}(t_j, 0) = \int_0^{t_j} \mathcal{U}_B(t_j, s) \mathcal{U}_B(t_j, s)^* \, ds.$$
Because $\mathcal{U}_B$ has an infinite sequence of eigenvalues accumulating at $0$, the Gramian has an infinite sequence of eigenvalues $\mu_n \to 0$ decaying like $\exp(-c \nu n^{2/3})$.
Its inverse norm explodes:
$$\|\mathcal{G}(t_j, 0)^{-1}\| = +\infty.$$

Unless the target state $W_j^\star$ is explicitly proved to lie in the exact range of the Gramian $\operatorname{Ran}(\mathcal{G}^{1/2})$, backward solvability in any standard Sobolev space $H^s(\mathbb{T}^3)$ is **unsupported**.

---

## 5. Epistemic Conclusion

$$\boxed{\mathbf{FIREWALL\ VERDICT:\ BACKWARD\ PARABOLIC\ SOLVABILITY\ IS\ OPEN.}}$$
The claim that $w_j(0) = \mathcal{U}_B(t_j, 0)^{-1} W_j^\star$ exists as a smooth function in $C^\infty(\mathbb{T}^3)$ is an **unproved conjecture**.
Ray de-shearing is a necessary condition for a localized geometric optics solution, but is **not sufficient** to prove bounded invertibility of the full 3D incompressible Navier–Stokes PDE operator.
