# Exact Affine Kelvin-Wave Benchmark and Backward Dissipation Re-Audit

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`

---

## 1. The Affine Incompressible Benchmark

Consider an unforced background velocity field that is affine in space:
$$u_B(x, t) = A(t) x, \qquad \operatorname{tr}(A(t)) = \operatorname{div} u_B = 0,$$
where $A(t) \in C^\infty([0, t_*]; \mathfrak{sl}(3, \mathbb{R}))$.
We decompose $A(t) = S(t) + \Omega(t)$ into symmetric rate-of-strain $S = \frac{1}{2}(A + A^T)$ and skew-symmetric vorticity $\Omega = \frac{1}{2}(A - A^T)$.

The linearized Navier–Stokes system for a perturbation $w(x, t)$ with pressure $p(x, t)$ is:
$$\partial_t w + (A(t) x \cdot \nabla) w + A(t) w + \nabla p - \nu \Delta w = 0, \qquad \nabla \cdot w = 0.$$

### 1.1 Exact Kelvin Wave Ansatz
We seek exact Kelvin plane-wave solutions of the form:
$$w(x, t) = a(t) e^{i k(t) \cdot x}, \qquad p(x, t) = q(t) e^{i k(t) \cdot x}.$$

Substituting this ansatz into the linearized momentum equation yields:
$$\left[ \dot{a}(t) + i (\dot{k}(t) + A(t)^T k(t)) \cdot x \, a(t) + A(t) a(t) + i k(t) q(t) + \nu |k(t)|^2 a(t) \right] e^{i k(t) \cdot x} = 0.$$

To eliminate the spatial coordinate $x$ for all $x \in \mathbb{R}^3$, the coefficient of $i x \cdot (\dots)$ must vanish identically:
$$\boxed{\dot{k}(t) = -A(t)^T k(t)}.$$

### 1.2 Fundamental Solution Matrix
Let $\Phi(t, s) \in \mathrm{SL}(3, \mathbb{R})$ be the forward flow fundamental matrix satisfying:
$$\frac{d}{dt} \Phi(t, s) = A(t) \Phi(t, s), \qquad \Phi(s, s) = I.$$
By Liouville's formula, $\det \Phi(t, s) = \exp\left(\int_s^t \operatorname{tr} A(\sigma) d\sigma\right) = 1$.

Differentiating $\Phi(t, s)^T \Phi(t, s)^{-T} = I$ confirms:
$$\frac{d}{dt} \Phi(t, s)^{-T} = -A(t)^T \Phi(t, s)^{-T}.$$
Therefore, the exact wavevector trajectory is given by:
$$\boxed{k(t) = \Phi(t, s)^{-T} k(s)}.$$
In particular, expressing the wavevector at time $t \in [0, t_*]$ in terms of its terminal value $k(t_*)$ at $t_*$:
$$k(t) = \Phi(t, t_*)^{-T} k(t_*) = \Phi(t_*, t)^T k(t_*).$$

### 1.3 Pressure Elimination & Amplitude Evolution
The incompressibility condition $\nabla \cdot w = 0$ requires $k(t) \cdot a(t) = 0$ for all $t$.
Taking the dot product of the momentum equation with $k(t)$ and using $k(t) \cdot \dot{a}(t) = -\dot{k}(t) \cdot a(t) = k(t)^T A(t) a(t)$:
$$k(t)^T A(t) a(t) + k(t)^T A(t) a(t) + i |k(t)|^2 q(t) = 0 \implies q(t) = 2 i \frac{k(t)^T A(t) a(t)}{|k(t)|^2}.$$

Substituting $q(t)$ back into the momentum equation yields the projected amplitude ODE:
$$\dot{a}(t) = \left( \frac{2 k(t) k(t)^T}{|k(t)|^2} - I \right) A(t) a(t) - \nu |k(t)|^2 a(t).$$
Letting $a(t) = \tilde{a}(t) \exp\left(-\nu \int_0^t |k(s)|^2 ds\right)$, the inviscid amplitude $\tilde{a}(t)$ satisfies:
$$\frac{d}{dt} \tilde{a}(t) = \mathbb{P}_{k(t)^\perp} \left( -A(t) \tilde{a}(t) \right) + \frac{k(t) k(t)^T}{|k(t)|^2} A(t) \tilde{a}(t),$$
which is purely kinematic and preserves the solenoidal constraint $k(t) \cdot \tilde{a}(t) = 0$.

---

## 2. Backward Evolution and Dissipation Functional

Given a terminal wavevector $k^\star = k(t_*) \in \mathbb{R}^3$ at time $t_*$, its backward trajectory for $t \in [0, t_*]$ is:
$$k(t) = \Phi(t_*, t)^T k^\star.$$
The exact cumulative backward viscous dissipation functional is:
$$\boxed{\mathcal{D}_{\mathrm{back}}(k^\star; t_*) = \nu \int_0^{t_*} |k(t)|^2 dt = \nu \int_0^{t_*} \left| \Phi(t_*, t)^T k^\star \right|^2 dt}.$$

The backward propagator on pure Fourier modes acts as:
$$\mathcal{U}(t_*, 0)^{-1} \left( a^\star e^{i k^\star \cdot x} \right) = a_0 e^{i k(0) \cdot x},$$
where the amplitude ratio satisfies:
$$\frac{|a_0|}{|a^\star|} \asymp \exp\left( +\frac{1}{2} \mathcal{D}_{\mathrm{back}}(k^\star; t_*) - \int_0^{t_*} \sigma_{\mathrm{eff}}(s) ds \right).$$

---

## 3. Directional Classification in the Strain Eigenframe

To evaluate $\mathcal{D}_{\mathrm{back}}$, consider the canonical hyperbolic/axisymmetric strain tensor:
$$A(t) = S(t) = \operatorname{diag}(\lambda_1(t), \lambda_2(t), \lambda_3(t)), \qquad \lambda_1 + \lambda_2 + \lambda_3 = 0.$$
Let $\Lambda_i(t_*, t) = \int_t^{t_*} \lambda_i(s) ds$. The fundamental matrix is diagonal:
$$\Phi(t_*, t)^T = \operatorname{diag}\left( e^{\Lambda_1(t_*, t)}, e^{\Lambda_2(t_*, t)}, e^{\Lambda_3(t_*, t)} \right).$$

For the OpenAI singular core in the burst interval $[t_j^-, t_j]$ of duration $\Delta t_j = 2^{-j}$, the strain eigenvalues scale as:
$$\lambda_1(t) = -2\sigma(t), \qquad \lambda_2(t) = \sigma(t), \qquad \lambda_3(t) = \sigma(t),$$
where $\sigma(t) \asymp \tau^{-1-h} = 2^{j(1+h)}$, so that the cumulative burst strain is:
$$\Sigma_j = \int_{t_j^-}^{t_j} \sigma(s) ds \asymp 2^{jh} \gg 1.$$

Now classify any terminal wavevector $k^\star = (k_1^\star, k_2^\star, k_3^\star)$ continued backward from $t_j$ to $t_j^-$:

### 3.1 Case 1: Pure Compressive Subspace ($\mathbb{E}_{\mathrm{comp}} = \operatorname{span}\{e_1\}$)
If $k_2^\star = k_3^\star = 0$ and $k_1^\star \ne 0$:
$$k_1(t) = k_1^\star \exp\left( -2 \int_t^{t_j} \sigma(s) ds \right) = k_1^\star e^{-2 \Sigma(t_j, t)}.$$
- **Backward Frequency**: $|k(t)|$ strictly decreases backward ($|k(t)| \downarrow$).
- **Ancestral Frequency**: At $t = t_j^-$, $|k(t_j^-)| = k_1^\star e^{-2 \Sigma_j} \asymp 2^{j/2} e^{-2 \cdot 2^{jh}} \to 0$.
- **Backward Dissipation**:
  $$\mathcal{D}_{\mathrm{back}} = \nu (k_1^\star)^2 \int_{t_j^-}^{t_j} e^{-4 \Sigma(t_j, t)} dt \le \nu \frac{(k_1^\star)^2}{4 \sigma_j} = \nu \frac{2^j}{4 \cdot 2^{j(1+h)}} = \frac{\nu}{4} 2^{-jh} \to 0.$$
- **Verdict**: Controlled backward evolution with bounded (vanishing) viscous cost.

### 3.2 Case 2: Transverse Extensional Subspace ($\mathbb{E}_{\mathrm{ext}} = \operatorname{span}\{e_2, e_3\}$)
If $k_1^\star = 0$ and $k_\perp^\star = (k_2^\star, k_3^\star) \ne 0$:
$$k_\perp(t) = k_\perp^\star \exp\left( +\int_t^{t_j} \sigma(s) ds \right) = k_\perp^\star e^{+\Sigma(t_j, t)}.$$
- **Backward Frequency**: $|k(t)|$ explodes exponentially backward ($|k(t)| \uparrow$).
- **Ancestral Frequency**: At $t = t_j^-$, $|k(t_j^-)| = |k_\perp^\star| e^{+\Sigma_j} \asymp |k_\perp^\star| \exp(2^{jh}) \to \infty$.
- **Backward Dissipation**:
  $$\mathcal{D}_{\mathrm{back}} = \nu |k_\perp^\star|^2 \int_{t_j^-}^{t_j} e^{+2 \Sigma(t_j, t)} dt \ge \nu \frac{|k_\perp^\star|^2}{2 \sigma_j} \left( e^{2 \Sigma_j} - 1 \right) \asymp \nu |k_\perp^\star|^2 2^{-j(1+h)} \exp\left( 2 \cdot 2^{jh} \right).$$
- **Verdict**: Super-exponential Hadamard explosion whenever $|k_\perp^\star| > 0$.

### 3.3 Case 3: Mixed Directions ($k_1^\star \ne 0$ and $k_\perp^\star \ne 0$)
For any generic wavevector not lying strictly on the 1D line $\mathbb{E}_{\mathrm{comp}}$:
$$|k(t)|^2 = (k_1^\star)^2 e^{-4 \Sigma(t_j, t)} + |k_\perp^\star|^2 e^{+2 \Sigma(t_j, t)}.$$
As $t \to t_j^-$, the second term dominates completely:
$$|k(t_j^-)| \ge |k_\perp^\star| \exp(2^{jh}) \to \infty,$$
$$\mathcal{D}_{\mathrm{back}} \ge \nu |k_\perp^\star|^2 2^{-j(1+h)} \exp\left( 2 \cdot 2^{jh} \right) \to +\infty.$$

---

## 4. True Backward Cost Functional and Range-of-Semigroup Formulation

Let $\mathcal{U}(t_*, 0): X \to X$ denote the forward linearized solution operator $\mathcal{U}(t_*, 0) w_0 = w(t_*)$ on a Hilbert space $X$ (e.g. $X = L_\sigma^2(\mathbb{R}^3)$ or $H_\sigma^m(\mathbb{T}^3)$).

### 4.1 Backward Cost Definition
For any target terminal state $W^\star \in X$, define the exact backward cost:
$$\mathfrak{C}(W^\star; t_*) = \inf \left\{ \|w_0\|_X : \mathcal{U}(t_*, 0) w_0 = W^\star \right\}.$$
If no such $w_0 \in X$ exists, we define $\mathfrak{C}(W^\star; t_*) = +\infty$, which corresponds to:
$$W^\star \notin \operatorname{Range}\left( \mathcal{U}(t_*, 0) \right).$$

### 4.2 Fourier Characterization of the Range
By Plancherel's theorem, the forward operator $\mathcal{U}(t_*, 0)$ acts in Fourier space as:
$$\widehat{w}(\xi, t_*) = M(\xi; t_*, 0) \widehat{w_0}(\Phi(t_*, 0)^{-T} \xi) \exp\left( -\nu \int_0^{t_*} |\Phi(t_*, s)^T \xi|^2 ds \right),$$
where $M(\xi; t_*, 0)$ is a unitary/bounded rotation matrix.

Inverting this relation gives:
$$\widehat{w_0}(\eta) = M(\Phi(t_*, 0)^T \eta)^{-1} \widehat{W^\star}(\Phi(t_*, 0)^T \eta) \exp\left( +\nu \int_0^{t_*} |\Phi(t, 0)^{-T} \eta|^2 dt \right).$$
Therefore, the $L^2$-backward cost is:
$$\mathfrak{C}(W^\star; t_*)^2 = \int_{\mathbb{R}^3} |\widehat{W^\star}(\xi)|^2 \exp\left( +2\nu \int_0^{t_*} |\Phi(t_*, t)^T \xi|^2 dt \right) d\xi.$$

### 4.3 Decisive Range Theorem
**Theorem 4.1**: A smooth target state $W^\star \in C^\infty \cap L^2$ belongs to $\operatorname{Range}(\mathcal{U}(t_*, 0))$ if and only if its Fourier transform $\widehat{W^\star}(\xi)$ decays faster than the anisotropic Gaussian/super-exponential weight:
$$\sup_{\xi \in \operatorname{supp}(\widehat{W^\star})} \left( 2\nu \int_0^{t_*} |\Phi(t_*, t)^T \xi|^2 dt \right) < \infty,$$
or $\widehat{W^\star}(\xi)$ has compact Fourier support strictly contained in the stable subspace $\mathbb{E}_{\mathrm{comp}}$.

If $\widehat{W^\star}(\xi)$ has any spectral support outside $\mathbb{E}_{\mathrm{comp}}$:
$$\operatorname{dist}_{\mathrm{ang}}\left( \operatorname{supp} \widehat{W^\star}, \mathbb{E}_{\mathrm{comp}} \right) = \theta_0 > 0,$$
then $\mathfrak{C}(W^\star; t_*) = +\infty$ or diverges as $\exp(+c \exp(2^{jh}))$ as $j \to \infty$.
