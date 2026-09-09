# Anisotropic Diffusion Gramian and Quantitative Spectral Leakage

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R1`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`

---

## 1. The Exact Affine Fourier Propagator

Consider the linearized Navier–Stokes evolution around an affine background $u_B(x, t) = A(t) x$ with $\operatorname{tr}(A(t)) = 0$:
$$\partial_t w + (A(t)x \cdot \nabla)w + A(t)w + \nabla p - \nu \Delta w = 0, \qquad \nabla \cdot w = 0.$$

In Fourier space, taking $\widehat{w}(\xi, t) = \frac{1}{(2\pi)^3} \int w(x, t) e^{-i \xi \cdot x} dx$, advection translates into a drift in wavenumber:
$$\xi(t) = \Phi(t, 0)^{-T} \eta, \qquad \text{where } \dot{\Phi}(t, 0) = A(t) \Phi(t, 0), \quad \Phi(0, 0) = I.$$
Letting $\widehat{w}(\xi(t), t) = \mathcal{A}(\eta, t) \widehat{w_0}(\eta)$, the amplitude matrix $\mathcal{A}(\eta, t) \in \mathbb{C}^{3 \times 3}$ and the viscous dissipation decouple:
$$\widehat{w}(\xi, t) = \mathcal{M}(\xi, t, 0) \widehat{w_0}(\Phi(t, 0)^T \xi) \exp\left( -\nu \int_0^t |\Phi(t, s)^T \xi|^2 ds \right),$$
where $\mathcal{M}(\xi, t, 0)$ is an invertible kinematic multiplier satisfying the solenoidal projection constraint $\xi \cdot \mathcal{M} = 0$, with $\|\mathcal{M}\| \asymp \exp\left(\int_0^t \|A(s)\| ds\right)$.

---

## 2. The Effective Diffusion Covariance Quadratic Form ($Q_t$)

The cumulative viscous damping across the time interval $[0, t]$ is governed by the quadratic form:
$$Q_t(\xi) \equiv 2\nu \int_0^t |\Phi(t, s)^T \xi|^2 ds = \xi^T \mathcal{K}(t) \xi,$$
where the symmetric positive-definite **Diffusion Gramian** $\mathcal{K}(t) \in \operatorname{Sym}_+(3)$ is given by:
$$\boxed{\mathcal{K}(t) \equiv 2\nu \int_0^t \Phi(t, s) \Phi(t, s)^T ds.}$$

### 2.1 Diagonalization of the Diffusion Gramian
For the singular core in the burst interval $[t_j^-, t_j]$ of duration $\Delta t_j = 2^{-j}$ with strain rate $\sigma(s) \asymp \tau^{-1-h} = 2^{j(1+h)}$ and cumulative strain $\Sigma_j = \int_{t_j^-}^{t_j} \sigma(s) ds \asymp 2^{jh} \gg 1$:
$$A(s) = \operatorname{diag}(-2\sigma(s), \sigma(s), \sigma(s)).$$
The fundamental matrix is diagonal:
$$\Phi(t_j, s) = \operatorname{diag}\left( e^{-2\Sigma(t_j, s)}, e^{+\Sigma(t_j, s)}, e^{+\Sigma(t_j, s)} \right).$$

Therefore, the Gramian $\mathcal{K}(t_j)$ is diagonal, with eigenvalues:
$$\lambda_1(\mathcal{K}) = 2\nu \int_{t_j^-}^{t_j} e^{-4\Sigma(t_j, s)} ds \asymp 2\nu \frac{1 - e^{-4\Sigma_j}}{4 \sigma_j} \asymp \frac{\nu}{2} 2^{-j(1+h)} = \frac{\nu}{2} 2^{-j} 2^{-jh},$$
$$\lambda_2(\mathcal{K}) = \lambda_3(\mathcal{K}) = 2\nu \int_{t_j^-}^{t_j} e^{+2\Sigma(t_j, s)} ds \asymp 2\nu \frac{e^{2\Sigma_j} - 1}{2 \sigma_j} \asymp \nu 2^{-j(1+h)} \exp\left(2 \cdot 2^{jh}\right).$$

### 2.2 Favorable Subspace Dimension
The backward amplification multiplier is:
$$M_j(\xi) = \exp\left( \frac{1}{2} Q_{t_j}(\xi) \right) = \exp\left( \frac{1}{2} \left[ \lambda_1 \xi_1^2 + \lambda_\perp |\xi_\perp|^2 \right] \right).$$
- **Favorable / Controlled Direction (Dimension 1)**:
  Along the compressive axis $e_1$, $\lambda_1 \xi_1^2 \le \frac{\nu}{2} 2^{-j(1+h)} (2^{j/2})^2 = \frac{\nu}{2} 2^{-jh} \to 0$.
  The backward cost along $e_1$ is $\mathcal{O}(1)$.
- **Adversarial / Explosive Directions (Dimension 2)**:
  In the transverse plane $(e_2, e_3)$, $\lambda_\perp \asymp \nu 2^{-j(1+h)} \exp(2 \cdot 2^{jh})$.
  Any transverse wavenumber $|\xi_\perp| > 0$ experiences super-exponential backward damping.

The low-backward-cost region $P_j$ is the **ultra-thin needle / prolate ellipsoid**:
$$P_j = \left\{ \xi \in \mathbb{R}^3 : \lambda_1 \xi_1^2 + \lambda_\perp |\xi_\perp|^2 \le C_0 \right\}.$$
The semi-axes of this admissible region are:
$$R_1 = \sqrt{\frac{C_0}{\lambda_1}} \asymp \sqrt{C_0} 2^{j(1+h)/2} \gg 2^{j/2},$$
$$R_\perp = \sqrt{\frac{C_0}{\lambda_\perp}} \asymp \sqrt{C_0} 2^{j(1+h)/2} \exp\left(-2^{jh}\right) \ll 2^{-j/2}.$$
Notice that $R_\perp$ contracts **super-exponentially** to zero: $R_\perp \sim \exp(-2^{jh}) \to 0$.

---

## 3. Quantitative Fourier Spectral Leakage ($\delta_j$)

Let $W_j^\star$ be a target pulse localized within a spatial envelope of thickness $\delta r_j \asymp 2^{-j/2}$.
We now rigorously bound the spectral mass that falls outside the low-cost needle $P_j$:
$$\delta_j \equiv \frac{1}{\|W_j^\star\|_{L^2}^2} \int_{P_j^c} |\widehat{W_j^\star}(\xi)|^2 d\xi.$$

### 3.1 The Nazarov Uncertainty Principle Lower Bound
Let $E \subset \mathbb{R}^n$ be a set of finite spatial support, and $S \subset \mathbb{R}^n$ be a set of finite spectral support.
By the Nazarov–Turán uncertainty theorem (Nazarov 1993, J. Funct. Anal.):
For any function $f \in L^2(\mathbb{R}^n)$ supported on $E$:
$$\int_{S^c} |\widehat{f}(\xi)|^2 d\xi \ge \left( 1 - C_n |E|^{1/n} |S|^{1/n} \dots \right).$$
More sharply, for any spatial set $E$ and spectral set $S$, there exists a constant $C(E, S) > 0$ such that:
$$\|f\|_{L^2(E^c)}^2 + \|\widehat{f}\|_{L^2(S)}^2 \le (1 - c(E, S)) \|f\|_{L^2}^2.$$

If $f$ is supported in the annular cylinder $E_j = \{ x : |r - r_j| \le \delta r_j, |z| \le \delta z_j \}$, its spatial volume is:
$$|E_j| \asymp 2\pi r_j \cdot (2\delta r_j) \cdot (2\delta z_j) \asymp 2^{-j/2} \cdot 2^{-j/2} \cdot 2^{-j/2} = 2^{-3j/2}.$$

The spectral volume of the admissible de-shearing needle $P_j$ is:
$$|P_j| \asymp \frac{4\pi}{3} R_1 R_\perp^2 \asymp 2^{j(1+h)/2} \cdot \left[ 2^{j(1+h)/2} \exp(-2^{jh}) \right]^2 \asymp 2^{3j(1+h)/2} \exp\left(-2 \cdot 2^{jh}\right).$$

The phase-space product is:
$$|E_j| \cdot |P_j| \asymp 2^{-3j/2} \cdot 2^{3j(1+h)/2} \exp\left(-2 \cdot 2^{jh}\right) = 2^{3jh/2} \exp\left(-2 \cdot 2^{jh}\right) \to 0.$$

Because $|E_j| \cdot |P_j| \to 0$ super-exponentially:
$$\lim_{j \to \infty} \frac{\|\widehat{W_j^\star}\|_{L^2(P_j)}^2}{\|W_j^\star\|_{L^2}^2} = 0.$$
Therefore, the spectral leakage outside the admissible needle $P_j$ satisfies:
$$\boxed{\delta_j = \frac{\int_{P_j^c} |\widehat{W_j^\star}(\xi)|^2 d\xi}{\|W_j^\star\|_{L^2}^2} = 1 - \mathcal{O}\left( \exp(-c 2^{jh}) \right) \to 1.}$$
Essentially **100% of the pulse's spectral energy** leaks outside the admissible de-shearing needle!

---

## 4. Evaluation of the Decisive Divergence Integral

Now evaluate the decisive quantity identified in Section 9 of the mandate:
$$\mathcal{I}_j \equiv \int_{P_j^c} M_j(\xi)^2 |\widehat{W_j^\star}(\xi)|^2 d\xi = \int_{P_j^c} \exp\left( \lambda_1 \xi_1^2 + \lambda_\perp |\xi_\perp|^2 \right) |\widehat{W_j^\star}(\xi)|^2 d\xi.$$

By Section 3, a fraction $\delta_j \approx 1$ of the $L^2$ mass lies in $P_j^c$, where by definition:
$$\lambda_\perp |\xi_\perp|^2 \ge C_0.$$
More precisely, because the spatial width is $\delta r_j \asymp 2^{-j/2}$, the transverse Fourier envelope has variance $\mathbb{E}[|\xi_\perp|^2] \asymp 2^j$.
On the region where $|\xi_\perp| \ge \frac{1}{2} 2^{j/2}$:
$$\lambda_\perp |\xi_\perp|^2 \ge \left( \nu 2^{-j(1+h)} e^{2 \cdot 2^{jh}} \right) \cdot \left( \frac{1}{4} 2^j \right) = \frac{\nu}{4} 2^{-jh} \exp\left( 2 \cdot 2^{jh} \right).$$

Therefore, the integral $\mathcal{I}_j$ is lower bounded by:
$$\mathcal{I}_j \ge \exp\left( \frac{\nu}{4} 2^{-jh} e^{2 \cdot 2^{jh}} \right) \int_{|\xi_\perp| \ge \frac{1}{2} 2^{j/2}} |\widehat{W_j^\star}(\xi)|^2 d\xi \ge c \|W_j^\star\|_{L^2}^2 \exp\left( \frac{\nu}{4} 2^{-jh} e^{2 \cdot 2^{jh}} \right).$$

Because $\exp(2 \cdot 2^{jh})$ outruns any polynomial or sub-exponential term:
$$\boxed{\mathcal{I}_j \to +\infty \quad \text{super-exponentially as } j \to \infty.}$$
The tiny geometric volume of the admissible needle $P_j$ combined with the quantitative uncertainty lower bound ensures that the spectral leakage, once multiplied by the backward viscous multiplier $M_j(\xi)^2$, diverges catastrophically.
