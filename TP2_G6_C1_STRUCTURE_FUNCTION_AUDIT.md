# TP2-G6-C1: SCALE-CRITICAL STRUCTURE FUNCTION AUDIT AND LEBESGUE BOUNDS

## Work Package WP7: Exact L2 Increment Estimates and the Spatial-to-Trajectory Gap

---

### 1. Purpose and Theoretical Context

In fluid turbulence literature, spatial increments of velocity are classically characterized through the **Eulerian velocity structure functions**:
$$
S_p(h, t) = \int_{\mathbb{T}^3} |u(x+h, t) - u(x, t)|^p\, dx, \qquad p \ge 1.
$$
While empirical turbulence models postulate Kolmogorov phenomenological scalings (such as $S_2(h) \sim (\varepsilon |h|)^{2/3}$ in the inertial subrange), a rigorous mathematical programme targeting Clay Statement B must establish what follows **unconditionally** from the Navier–Stokes equations under the Leray energy inequality.

This work package proves the exact, non-circular $L^2$ structure function bound:
$$
\int_0^T S_2(h, t)\, dt \le |h|^2 \int_0^T \|\nabla u(t)\|_{L^2}^2\, dt \le \frac{\mathcal{E}_0}{2\nu}\, |h|^2.
$$
We then audit whether this quadratic bound can constrain relative stochastic dispersion at intrinsic scales, and prove the existence of an impassable firewall between spatial Lebesgue averages and stochastic trajectory expectations.

---

### 2. Exact Mathematical Derivation of the $S_2(h)$ Bound

**Theorem 7.1 (Exact Quadratic Structure Function Bound)**.
*Let $u \in L^2([0, T]; H^1(\mathbb{T}^3))$ be an arbitrary weak solution to the 3D incompressible Navier–Stokes equations satisfying the initial energy bound $\frac{1}{2}\|u_0\|_{L^2}^2 \le \mathcal{E}_0$. Then for every displacement vector $h \in \mathbb{R}^3$ and every $t \in [0, T]$:*
$$
S_2(h, t) \le |h|^2 \|\nabla u(t)\|_{L^2(\mathbb{T}^3)}^2.
$$
*Moreover, integrating over time $[0, T]$ yields the uniform bound:*
$$
\int_0^T S_2(h, t)\, dt \le \frac{\mathcal{E}_0}{2\nu}\, |h|^2.
$$

*Proof*.
By the fundamental theorem of calculus along the straight segment:
$$
u(x+h, t) - u(x, t) = \int_0^1 \nabla u(x + \theta h, t)\, h\, d\theta.
$$
Applying the Cauchy–Schwarz inequality on the scalar product and Jensen's inequality with respect to the probability measure $d\theta$ on $[0, 1]$:
$$
\begin{aligned}
|u(x+h, t) - u(x, t)|^2 &= \left| \int_0^1 \nabla u(x + \theta h, t)\, h\, d\theta \right|^2 \\
&\le |h|^2 \left| \int_0^1 |\nabla u(x + \theta h, t)|\, d\theta \right|^2 \\
&\le |h|^2 \int_0^1 |\nabla u(x + \theta h, t)|^2\, d\theta.
\end{aligned}
$$
Integrating both sides over the periodic torus $\mathbb{T}^3$ with respect to spatial Lebesgue measure $dx$:
$$
S_2(h, t) = \int_{\mathbb{T}^3} |u(x+h, t) - u(x, t)|^2\, dx \le |h|^2 \int_{\mathbb{T}^3} \left[ \int_0^1 |\nabla u(x + \theta h, t)|^2\, d\theta \right] dx.
$$
By Fubini–Tonelli theorem, we interchange the order of integration:
$$
\int_{\mathbb{T}^3} \left[ \int_0^1 |\nabla u(x + \theta h, t)|^2\, d\theta \right] dx = \int_0^1 \left[ \int_{\mathbb{T}^3} |\nabla u(x + \theta h, t)|^2\, dx \right] d\theta.
$$
By periodic translation invariance of the Lebesgue measure on $\mathbb{T}^3$:
$$
\int_{\mathbb{T}^3} |\nabla u(x + \theta h, t)|^2\, dx = \int_{\mathbb{T}^3} |\nabla u(y, t)|^2\, dy = \|\nabla u(t)\|_{L^2}^2 \quad \text{for every } \theta \in [0, 1].
$$
Therefore:
$$
\int_0^1 \|\nabla u(t)\|_{L^2}^2\, d\theta = \|\nabla u(t)\|_{L^2}^2.
$$
Multiplying by $|h|^2$ establishes:
$$
S_2(h, t) \le |h|^2 \|\nabla u(t)\|_{L^2}^2.
$$
Finally, integrating over $t \in [0, T]$ and applying the Leray energy inequality:
$$
\nu \int_0^T \|\nabla u(t)\|_{L^2}^2\, dt \le \frac{1}{2}\|u_0\|_{L^2}^2 \le \mathcal{E}_0 \implies \int_0^T \|\nabla u(t)\|_{L^2}^2\, dt \le \frac{\mathcal{E}_0}{2\nu}.
$$
Substituting gives the unconditional time-integrated bound:
$$
\int_0^T S_2(h, t)\, dt \le \frac{\mathcal{E}_0}{2\nu}\, |h|^2. \quad \blacksquare
$$

---

### 3. Spectral Formulation via Fourier Transform

To confirm the robustness of Theorem 7.1, we verify it via Plancherel's theorem on $\mathbb{T}^3 = [0, 1]^3$.
Let $u(x, t) = \sum_{k \in \mathbb{Z}^3} \hat{u}(k, t) e^{2\pi i k \cdot x}$. The increment is:
$$
u(x+h) - u(x) = \sum_{k \in \mathbb{Z}^3} \hat{u}(k, t) \left( e^{2\pi i k \cdot h} - 1 \right) e^{2\pi i k \cdot x}.
$$
By Parseval's identity:
$$
S_2(h, t) = \sum_{k \in \mathbb{Z}^3} |\hat{u}(k, t)|^2 |e^{2\pi i k \cdot h} - 1|^2 = \sum_{k \in \mathbb{Z}^3} |\hat{u}(k, t)|^2 \left( 4 \sin^2(\pi k \cdot h) \right).
$$
Using the elementary trigonometric inequality $|\sin(\xi)| \le |\xi|$ for all $\xi \in \mathbb{R}$:
$$
4 \sin^2(\pi k \cdot h) \le 4 \pi^2 (k \cdot h)^2 \le 4 \pi^2 |k|^2 |h|^2.
$$
Since $\|\nabla u(t)\|_{L^2}^2 = \sum_{k \in \mathbb{Z}^3} 4 \pi^2 |k|^2 |\hat{u}(k, t)|^2$, we immediately obtain:
$$
S_2(h, t) \le |h|^2 \sum_{k \in \mathbb{Z}^3} 4\pi^2 |k|^2 |\hat{u}(k, t)|^2 = |h|^2 \|\nabla u(t)\|_{L^2}^2.
$$
The spectral proof demonstrates that $S_2(h) \le |h|^2 \|\nabla u\|_{L^2}^2$ is an exact geometric identity holding mode-by-mode.

---

### 4. The Spatial-to-Trajectory Gap (Bridge B2 Barrier)

While Theorem 7.1 provides an elegant, non-circular $L^2$ bound on spatial velocity increments, **it cannot be directly applied to control the relative separation of stochastic particles $\delta A_s$**.

#### 4.1 The Expectation Mismatch
The evolution of relative separation involves the expectation along stochastic paths:
$$
\mathbb{E}\left[ |\delta u(A_s(x), h)|^2 \right] = \mathbb{E}\left[ |u(A_s(x+h), s) - u(A_s(x), s)|^2 \right].
$$
Under Coupling C-SYNC, spatial Lebesgue measure is preserved individually:
$$
\int_{\mathbb{T}^3} |u(A_s(x+h), s) - u(A_s(x), s)|^2\, dx = \int_{\mathbb{T}^3} |u(y_2, s) - u(y_1, s)|^2\, dx,
$$
where $y_1 = A_s(x)$ and $y_2 = A_s(x+h)$.
However:
1. $y_2 - y_1 = \delta A_s(x, h)$ is **not equal to $h$**! The displacement vector itself has been dynamically distorted by the flow.
2. In Candidate Blowup Regimes, the flow compresses space in some directions and expands it in others. The distorted vector $\delta A_s$ can align with the compressed axis, where the local gradient $|\nabla u|$ is of order $M_n \gg 1$.
3. Averaging over all starting points $x \in \mathbb{T}^3$ against Lebesgue measure $dx$ yields:
   $$
   \int_{\mathbb{T}^3} S_2(\delta A_s(x, h), s)\, dx.
   $$
   Because $\delta A_s(x, h)$ varies with $x$, this is an integral of a random field over non-uniform displacements.

#### 4.2 Pointwise Concentration vs Lebesgue Integrability
In candidate blowup scenarios:
- The enstrophy $\|\nabla u(t)\|_{L^2}^2 = \int |\omega|^2 dx$ remains bounded by initial enstrophy $\Omega_0$ for short times, or is bounded in time integral $\int_0^T \|\nabla u\|_{L^2}^2 dt \le \mathcal{E}_0 / (2\nu)$.
- However, the local vorticity $|\omega|$ can concentrate in a small set of measure $|E_s| \sim M_n^{-3/2}$ with peak amplitude $M_n \to \infty$.
- The $L^2$ norm spreads the energy across the entire volume: $\int_{\mathbb{T}^3} |\nabla u|^2 dx \sim M_n^2 \cdot M_n^{-3/2} = M_n^{1/2}$ (or remains $\mathcal{O}(1)$ if diluted).
- Thus, an $L^2$ bound $S_2(h) \le |h|^2 \|\nabla u\|_{L^2}^2$ tells us that on *average* over space, velocity increments are small. But along a specific trajectory entering the peak core, the local increment is:
  $$
  |\delta u| \sim M_n |\delta A_s|,
  $$
  which is enormous and blows up as $M_n \to \infty$.

---

### 5. Epistemic Assessment

- **Theorem 7.1 Status**: **`MATHEMATICAL_IDENTITY`** / **`NON_CIRCULAR`**.
- **Utility**: Rigorously establishes that on macroscopic spatial scales $|h| \sim 1$, the integrated velocity increment is quadratically bounded by the initial kinetic energy $\mathcal{E}_0$.
- **Firewall Gate**:
  $$\boxed{\mathbf{RULE\ SF\text{-}1:\ NO\ LEBESGUE\text{-}TO\text{-}TRAJECTORY\ LEAP}}$$
  Any derivation that substitutes the spatial structure function bound $S_2(h) \le C |h|^2$ for the pathwise stochastic drift $\delta u_s$ along individual backward trajectories is **epistemically invalid** unless accompanied by an unconditioned bound on the push-forward Radon–Nikodym density $\rho_s$.
