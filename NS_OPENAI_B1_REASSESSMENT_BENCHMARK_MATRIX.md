# Adversarial Benchmark Matrix (A through G)

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`

---

## 1. Overview and Benchmark Specifications

To exhaustively test the single-pulse autonomous entrance problem against adversarial flow topologies, we implement and audit seven canonical benchmarks (A through G).
For each benchmark, we determine:
1. Terminal pulse frequency $|k(t_*)|$;
2. Backward carrier wavevector evolution $k(t)$ and backward frequency $|k(0)|$;
3. Cumulative backward viscous dissipation integral $\mathcal{D}_{\mathrm{back}} = \nu \int_0^{t_*} |k(t)|^2 dt$;
4. Minimum initial data norm / inverse cost $\mathfrak{C}(W^\star, t_*)$;
5. Transverse spectral width $\Delta k_\perp$;
6. Phase evolution and sensitivity $\delta \Phi$;
7. Polarization dynamics in the moving frame.

---

## 2. Benchmark Definitions & Analytical Results

### Benchmark A: Constant Axisymmetric Hyperbolic Strain
- **Background**: $u_B(x) = A x$, $A = \operatorname{diag}(-2\sigma_0, \sigma_0, \sigma_0)$, $\sigma_0 > 0$ constant. Duration $t_*$.
- **Backward Wavevector**:
  $$k_1(t) = k_1^\star e^{-2\sigma_0 (t_* - t)}, \qquad k_\perp(t) = k_\perp^\star e^{+\sigma_0 (t_* - t)}.$$
- **Damping Integral**:
  - Compressive axis ($k_\perp^\star = 0$): $\mathcal{D}_{\mathrm{back}} = \nu (k_1^\star)^2 \frac{1 - e^{-4\sigma_0 t_*}}{4\sigma_0} \le \frac{\nu (k_1^\star)^2}{4\sigma_0}$.
  - Transverse axis ($k_1^\star = 0, k_\perp^\star \ne 0$): $\mathcal{D}_{\mathrm{back}} = \nu |k_\perp^\star|^2 \frac{e^{2\sigma_0 t_*} - 1}{2\sigma_0}$.
- **Backward Frequency**: $k_1(0) = k_1^\star e^{-2\sigma_0 t_*} \downarrow$; $k_\perp(0) = k_\perp^\star e^{+\sigma_0 t_*} \uparrow$.
- **Inverse Cost**: If $k_\perp^\star \ne 0$, $\mathfrak{C} \ge \exp\left( \frac{\nu |k_\perp^\star|^2}{4\sigma_0} e^{2\sigma_0 t_*} \right)$.
- **Polarization**: Fixed along $e_\perp$; strictly preserved since $A$ is diagonal.
- **Classification**: `STABLE_RAY_EXISTS_BUT_TRANSVERSE_BLOWUP`.

---

### Benchmark B: Time-Dependent Singular Hyperbolic Strain (OpenAI Core)
- **Background**: $u_B(x, t) = A(t) x$, $A(t) = \sigma(t) \operatorname{diag}(-2, 1, 1)$, $\sigma(t) = \sigma_0 (1 - t)^{-1-h}$ with $h \in (0, 1/6)$.
- **Burst Duration**: $t \in [t_j^-, t_j]$ of length $\Delta t_j = 2^{-j}$; $\Sigma_j = \int_{t_j^-}^{t_j} \sigma(s) ds \asymp 2^{jh} \gg 1$.
- **Backward Wavevector**:
  $$k_1(t_j^-) = k_1^\star e^{-2\Sigma_j} \asymp 2^{j/2} \exp(-2 \cdot 2^{jh}) \to 0,$$
  $$k_\perp(t_j^-) = k_\perp^\star e^{+\Sigma_j} \asymp |k_\perp^\star| \exp(2^{jh}) \to \infty.$$
- **Damping Integral**:
  - Longitudinal: $\mathcal{D}_{\mathrm{back}} \le \frac{\nu}{4} 2^{-jh} \to 0$.
  - Transverse: $\mathcal{D}_{\mathrm{back}} \ge \frac{\nu}{2} |k_\perp^\star|^2 2^{-j(1+h)} \exp(2 \cdot 2^{jh}) \to +\infty$.
- **Inverse Cost**: $\mathfrak{C}(W_j^\star, t_j) \ge \exp\left( +c \exp(2^{jh}) \right) \to +\infty$ for any wavepacket with $|k_\perp^\star| \gtrsim 2^{j/2}$.
- **Classification**: `SUPER_EXPONENTIAL_HADAMARD_EXPLOSION`.

---

### Benchmark C: Rotating Strain Eigenframe (Strain + Vorticity)
- **Background**: $A(t) = S(t) + \Omega(t)$, where $S(t) = R(t) \operatorname{diag}(-2\sigma, \sigma, \sigma) R(t)^T$, $\Omega(t) = \omega(t) J_3$, $\omega(t) \asymp \sigma(t) \asymp \tau^{-1-h}$.
- **Backward Wavevector**:
  Wavevectors precess continuously in the rotating frame:
  $$\dot{k} = -(S(t) + \Omega(t))^T k = (-S(t) + \Omega(t)) k.$$
- **Gyroscopic Mixing**: Because $\Omega$ continuously rotates wavevector components between the compressive axis $e_1$ and the extensional axes $e_2, e_3$, no wavevector remains in the compressive subspace:
  $$\inf_{k(t_*)} \max_{t \in [t_j^-, t_j]} |k_\perp(t)| \ge \frac{1}{\sqrt{2}} |k(t_*)|.$$
- **Damping Integral**: Complete loss of stable ray:
  $$\mathcal{D}_{\mathrm{back}} \ge c \nu |k(t_*)|^2 \Delta t_j \exp(c 2^{jh}) \to +\infty.$$
- **Polarization**: Undergoes rapid gyroscopic drift $\dot{b} \sim \omega(t) b$; phase alignment destroyed.
- **Classification**: `GYROSCOPIC_RAY_MIXING_TOTAL_EXPLOSION`.

---

### Benchmark D: 1D Periodic Shear Flow
- **Background**: $u_B(x) = (U_0 \sin(y), 0, 0)$ on $\mathbb{T}^3$.
- **Linearized Advection**: Non-affine; carrier wavenumber $k = (k_x, k_y, k_z)$.
- **Wavevector Evolution**: Only $k_y$ changes under shear:
  $$\dot{k}_x = 0, \qquad \dot{k}_y = -k_x U_0 \cos(y), \qquad \dot{k}_z = 0.$$
- **Backward Frequency**: $k(t)$ is at most linearly sheared ($|k(0)| \asymp |k(t_*)| + U_0 t_* |k_x|$).
- **Damping Integral**: $\mathcal{D}_{\mathrm{back}} \sim \nu |k(t_*)|^2 t_*$. For high frequency $|k| \sim 2^{j/2}$ across $t_* \sim 1$:
  $$\mathcal{D}_{\mathrm{back}} \sim \nu 2^j \cdot 1 = \nu 2^j \to +\infty.$$
  Backward cost explodes as $\exp(\nu 2^j)$ (classical direct preload damping `NS-OBS-020A`).
- **Classification**: `PERIODIC_SHEAR_PRELOAD_DAMPING_NO_GO`.

---

### Benchmark E: Affine Incompressible Strain + Exact Viscosity (Kelvin Wave)
- **Background**: Exact solution $u_B = A(t)x$ with exact Kelvin mode $w(t, x) = a(t) e^{i k(t) \cdot x}$.
- **Backward Frequency**:
  - If $k(t_*) = (2^{j/2}, 0, 0)$, $k(0) = \mathcal{O}(1)$.
  - If $k(t_*) = (0, 2^{j/2}, 0)$, $k(0) = 2^{j/2} e^{2^{jh}} \to \infty$.
- **Dissipation**: Exactly matches Plancherel integral $\exp\left(-\nu \int_0^{t_*} |k(s)|^2 ds\right)$.
- **Solenoidal Constraint**: $k(t) \cdot a(t) = 0$ holds identically for all $t$.
- **Classification**: `EXACT_SOLVABILITY_CONFIRMS_UNIDIRECTIONAL_STABILITY`.

---

### Benchmark F: Localized Kelvin Wavepacket
- **Ansatz**: $W_j^\star(x) = \chi(x / \delta r_j) a_j^\star e^{i k_j^\star \cdot x}$ with $\delta r_j \asymp 2^{-j/2}$.
- **Transverse Spectral Width**: $\Delta k_\perp = \|\nabla_\perp \chi\|_{L^2} / \delta r_j \asymp 2^{j/2}$.
- **Transverse Spillover**: Non-zero Fourier energy $|\widehat{W_j^\star}(\xi)|^2 > 0$ for modes with $|\xi_\perp| \ge \frac{1}{2} 2^{j/2}$.
- **Backward Viscous Dissipation**:
  $$\mathcal{D}_{\mathrm{back}}(\xi) \ge \frac{\nu}{4} 2^{-jh} \exp(2 \cdot 2^{jh}) \to +\infty.$$
- **Backward Norm**: $\mathfrak{C}(W_j^\star, t_j) \ge \exp\left(+c \exp(2^{jh})\right) \to +\infty$.
- **Classification**: `LOCALIZATION_BACKWARD_DIFFUSION_NO_GO`.

---

### Benchmark G: Two-Family Stress Realization Wavepacket
- **Ansatz**: $W^\star = W_+^\star + W_-^\star$, with $k_+^\star \nparallel k_-^\star$ required to span the 2D stress cone $K$.
- **Compressive Dimension**: $\dim(\mathbb{E}_{\mathrm{comp}}) = 1$.
- **Directional Deficit**: At most one wavevector (say $k_+^\star$) can be aligned with $\mathbb{E}_{\mathrm{comp}}$. The second wavevector $k_-^\star$ has $|\Pi_{\mathbb{E}_{\mathrm{ext}}}(k_-^\star)| \ge \frac{1}{\sqrt{2}} |k_-^\star| \asymp 2^{j/2}$.
- **Backward Dissipation**:
  $$\mathcal{D}_{\mathrm{back}}(k_-^\star) \ge \frac{\nu}{4} 2^{-jh} \exp(2 \cdot 2^{jh}) \to +\infty.$$
- **Relative Phase**: Accumulated phase difference $\Delta \Phi \asymp 2^{jh} \gg 1$ causes hyper-sensitive phase detuning.
- **Classification**: `TWO_FAMILY_DIRECTIONAL_DEFICIT_NO_GO`.

---

## 3. Adversarial Benchmark Summary Matrix

| Benchmark | Background Topology | Carrier Backward $|k(0)|$ | Transverse Cost $\mathcal{D}_{\mathrm{back}}$ | Inverse Cost $\mathfrak{C}$ | Primary Obstruction |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A: Constant Strain** | Affine hyperbolic | $\mathcal{O}(1)$ along $e_1$ | $\exp(2\sigma_0 t_*)$ on $e_\perp$ | Diverges if $k_\perp \ne 0$ | Transverse exponential growth |
| **B: OpenAI Singular Strain** | Singular $\tau^{-1-h}$ | $2^{j/2} e^{-2 \cdot 2^{jh}} \to 0$ | $\exp(2 \cdot 2^{jh}) \to \infty$ | $\exp(+c \exp(2^{jh}))$ | Super-exponential Hadamard blowup |
| **C: Rotating Frame** | Strain + Vorticity | Precesses out of ray | $\exp(c 2^{jh})$ | $\infty$ (Total loss of ray) | Gyroscopic vorticity mixing |
| **D: Periodic Shear** | Periodic $U(y)$ | $2^{j/2}$ (no de-shearing) | $\nu 2^j t_* \to \infty$ | $\exp(\nu 2^j)$ | Direct preload damping (OBS-020A) |
| **E: Affine Kelvin** | Linear $A(t)x$ | $\mathcal{O}(1)$ on 1D line | $\mathcal{O}(1)$ on line only | Finite on line only | 1D measure-zero line |
| **F: Localized Wavepacket** | Annular localized | Non-localized modes | $\exp(2 \cdot 2^{jh}) \to \infty$ | $\exp(+c \exp(2^{jh})) \to \infty$ | **Uncertainty Barrier (OBS-020B)** |
| **G: Two-Family Stress** | Paired helical modes | One $\mathcal{O}(1)$, one $\infty$ | $\exp(2 \cdot 2^{jh}) \to \infty$ | $\exp(+c \exp(2^{jh})) \to \infty$ | **Compressive Deficit (rank 1 vs 2)** |
