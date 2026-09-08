# NS-OPENAI-B1 — PULSE ENTRANCE-STATE CATALOG

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1`  
**Standard**: `Mathematical Research Constitution v1.0.1`  
**Risk Ceiling**: `R3`  
**Focus**: Exact Specification of the $j$-th Required Pulse Entrance State $W_j^\star = w_j(t_j^-)$  

---

## 1. Mathematical Definition of the Entrance State $W_j^\star$

In the OpenAI forced Navier–Stokes blowup mechanism, finite-time singularity formation at $t_* = 1$ is sustained by an infinite sequence of discrete pulses $j = 1, 2, 3, \dots$. Each pulse is injected externally in the forced system at time $t_j = 1 - \tau_j$, where:
$$\tau_j = 2^{-j}, \qquad t_j = 1 - 2^{-j} \xrightarrow[j \to \infty]{} 1.$$

In the **unforced setting** ($f \equiv 0$), an external injection cannot exist. The state immediately before activation must instead arrive as the autonomous endpoint of the Navier–Stokes Cauchy evolution:
$$W_j^\star(x) \equiv w_j(x, t_j^-) = \lim_{t \nearrow t_j} w_j(x, t).$$

$$\boxed{W_j^\star(x) \text{ is the exact target velocity field required at } t = t_j^- \text{ to sustain the cascade.}}$$

---

## 2. Exhaustive Parametric Characterization of $W_j^\star$

From the assimilated construction and Lean 4 formalization, $W_j^\star$ possesses the following rigorous structural profile in local cylindrical coordinates $(r, \theta, z)$ centered at the filament axis:

### 2.1 Spatial Localization and Support Envelope
- **Core Radial Scale**: $r_j \asymp \tau_j^{1/2} = 2^{-j/2}$.
- **Radial Localization**: Annular filament localized around $r \in [r_j / 2, 2 r_j]$.
  $$\rho_j(r) = \chi\left(\frac{r - r_j}{\delta r_j}\right), \qquad \delta r_j \asymp 2^{-j/2}.$$
- **Axial Extent**: Filament length scales anisotropically:
  $$\ell_{z, j} \asymp \tau_j^{1/2 - h} = 2^{-j(1/2 - h)}, \qquad 0 < h \ll 1 \quad (\text{e.g. } h = 0.05).$$
  Note that $\ell_{z, j} / r_j = 2^{jh} \to \infty$, exhibiting the "fluid spaghetti" aspect ratio.
- **Global Embedding on $\mathbb{T}^3$**: Periodic wrapping via partition of unity, centered at $x_j^* \in \mathbb{T}^3$ (without loss of generality, $x_j^* = 0$).

### 2.2 Amplitude and Velocity Scaling
- **Characteristic Core Velocity**:
  $$U_j \asymp \tau_j^{-1/2 - h} = 2^{j(1/2 + h)}.$$
- **Pulse Perturbation Magnitude**:
  The pulse carries amplitude proportional to the background strain velocity:
  $$\|W_j^\star\|_{L^\infty(\mathbb{T}^3)} \asymp A_j^\star = c_w \cdot 2^{j(1/2 + h)}, \qquad c_w \in (0, 1).$$
- **Local Kinetic Energy of Single Pulse**:
  $$\mathcal{E}(W_j^\star) = \frac{1}{2} \int_{\mathbb{T}^3} |W_j^\star|^2 dx \asymp (A_j^\star)^2 \cdot \text{Vol}(\operatorname{supp} W_j^\star) \asymp 2^{j(1 + 2h)} \cdot \left( 2^{-j} \cdot 2^{-j(1/2 - h)} \right) = 2^{j(3h - 1/2)}.$$
  For $h < 1/6$ (e.g. $h = 0.05$), $3h - 1/2 = -0.35 < 0$, so:
  $$\mathcal{E}(W_j^\star) \asymp 2^{-0.35 j} \xrightarrow[j \to \infty]{} 0.$$
  The kinetic energy of each incoming pulse is strictly vanishing!

### 2.3 Carrier Frequency and Wavevector Orientation
- **Wavenumber Magnitude**:
  $$|k_j^\star| \asymp \tau_j^{-1/2} = 2^{j/2}.$$
- **Wavevector Components in Cylindrical Basis**:
  $$k_j^\star = k_{r, j}^\star \hat{r} + \frac{m_j}{r_j} \hat{\theta} + k_{z, j}^\star \hat{z},$$
  where $k_{r, j}^\star \asymp 2^{j/2}$, $k_{z, j}^\star \asymp 2^{j/2}$, and the azimuthal mode number $m_j \in \mathbb{Z} \setminus \{0\}$ satisfies $m_j / r_j \asymp 2^{j/2}$ ($m_j = \mathcal{O}(1)$).

### 2.4 Polarization and Incompressibility
- **Solenoidal Constraint**: $\nabla \cdot W_j^\star = 0$ requires:
  $$k_j^\star \cdot \zeta_j^\star = 0 + \mathcal{O}(2^{-j/2}),$$
  where $\zeta_j^\star \in \mathbb{S}^2$ is the polarization unit vector.
- **Helical Structure**: The pulse is an active helical wavepacket with polarization spanned by:
  $$\zeta_j^\star \in \operatorname{span}\left\{ \hat{k}_j^\star \times \hat{r}, \, \hat{k}_j^\star \times (\hat{k}_j^\star \times \hat{r}) \right\}.$$

### 2.5 Temporal Width and Active Window
- **Duration of Active Burst**:
  $$\Delta t_j \asymp \tau_j = 2^{-j}.$$
- **Pulse Epoch Interval**:
  $$I_j = [t_j, t_j + \Delta t_j] = [1 - 2^{-j}, 1 - 2^{-(j+1)}].$$

### 2.6 Quadratic Reynolds Stress Contribution
- **Averaged Momentum Flux**:
  $$Q_j^\star = \langle W_j^\star \otimes W_j^\star \rangle_{\text{fast oscillation}} = (A_j^\star)^2 \, (\zeta_j^\star \otimes \zeta_j^\star).$$
- **Stress Cone Membership**:
  $Q_j^\star$ must lie inside the open convex cone $K \subset \operatorname{Sym}^+(3)$ of Reynolds stresses that drives the mean self-similar flow against viscous dissipation:
  $$Q_j^\star \in K \iff \zeta_{r, j}^\star \zeta_{z, j}^\star < 0 \quad \text{and} \quad |\zeta_{\theta, j}^\star|^2 \ge c_K > 0.$$

### 2.7 Admissible Error Tolerance $\varepsilon_j^\star$
To successfully substitute for the forced pulse, the unforced arriving state $u(t_j)$ must satisfy:
$$\|\Pi_j u(t_j) - W_j^\star\|_{X_j} \le \varepsilon_j^\star,$$
where:
- $\Pi_j$ is the spatial projector onto the annular region $\operatorname{supp}(W_j^\star)$ and frequency band $|k| \in [2^{j/2 - 1}, 2^{j/2 + 1}]$.
- $X_j = L^\infty(\mathbb{T}^3) \cap H^1(\mathbb{T}^3)$.
- **Tolerance Scale**:
  $$\varepsilon_j^\star \asymp 2^{-j \delta_0} A_j^\star = c_\varepsilon 2^{j(1/2 + h - \delta_0)}, \qquad \delta_0 > 0.$$

---

## 3. Structural Summary Matrix of $W_j^\star$

| Attribute | Scaling / Formula | Physical Role |
| :--- | :--- | :--- |
| **Arrival Time** $t_j$ | $1 - 2^{-j}$ | Onset of the $j$-th self-similar contraction epoch |
| **Duration** $\Delta t_j$ | $2^{-j}$ | Lifetime of pulse before energy transfers to core |
| **Core Radius** $r_j$ | $2^{-j/2}$ | Location of the active annular shear layer |
| **Axial Length** $\ell_{z, j}$ | $2^{-j(1/2 - h)}$ | High aspect ratio filament ($2^{jh} \to \infty$) |
| **Carrier Wavenumber** $|k_j^\star|$ | $2^{j/2}$ | Resonant spatial scale matching viscous balance |
| **Peak Amplitude** $A_j^\star$ | $c_w 2^{j(1/2 + h)}$ | Velocity required to produce target Reynolds stress |
| **Kinetic Energy** $\mathcal{E}_j^\star$ | $\mathcal{O}(2^{-j(1/2 - 3h)})$ | Vanishing energy as $j \to \infty$ ($h < 1/6$) |
| **Reynolds Stress** $Q_j^\star$ | $\sim (A_j^\star)^2 (\zeta^\star \otimes \zeta^\star) \in K$ | Drives axial momentum and sustains core rotation |
| **Required Tolerance** $\varepsilon_j^\star$ | $c_\varepsilon 2^{j(1/2 + h - \delta_0)}$ | Contraction barrier for asymptotic matching |

---

## 4. WHAT_THE_FLUID_IS_DOING

In physical terms, the target pulse state $W_j^\star$ is not an arbitrary turbulent eddy. It is a highly organized, rapidly oscillating **helical vortex wavepacket** wrapped around an ultra-thin spinning fluid thread. 

As the thread contracts from scale $j-1$ to scale $j$, its rotation speed accelerates while its radius shrinks by $\sqrt{2}$. At exactly time $t_j = 1 - 2^{-j}$, the thread requires an injection of helical Reynolds stress to prevent viscous friction from spreading the vortex core outward. The pulse $W_j^\star$ acts as an internal aerodynamic impeller: its tilted helical wavecrests pull fluid inward and sling it axially, converting local kinetic energy into the exact directional thrust needed to propel the core into the next, even smaller, self-similar contraction.

In the OpenAI proof, this impeller is materialized by turning on an external force $f_j(x, t)$. In our unforced B1 programme, this impeller must arrive on its own — shaped solely by the background Navier–Stokes flow acting on a subtle ripple present in the fluid at $t = 0$.
