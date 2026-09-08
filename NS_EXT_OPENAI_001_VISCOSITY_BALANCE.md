# NS-EXT-OPENAI-001 — VISCOUS BALANCE AND REYNOLDS NUMBER ASYMPTOTICS

**Programme**: `EXTERNAL_ASSIMILATION_AND_TRANSFER`  
**Focus**: Term-by-Term Navier–Stokes Balance and Effective Reynolds Numbers  
**Governing Viscosity**: Constant $\nu > 0$  

---

## 1. Local Reynolds Number Scaling

In fluid dynamics, the competition between nonlinear convection and viscous dissipation is quantified by dimensionless Reynolds numbers. For the anisotropic core, we define directional Reynolds numbers:

1. **Radial Reynolds Number ($Re_r$)**:
   $$Re_r(\tau) \equiv \frac{|u_r| \, \ell_r}{\nu} \asymp \frac{\tau^{-1/2} \cdot \tau^{1/2}}{\nu} = \frac{\mathcal{O}(1)}{\nu} \asymp 1.$$
   **Finding**: The radial Reynolds number remains strictly $\mathcal{O}(1)$ as $\tau \to 0^+$. Radial advection and radial viscous diffusion are in **permanent, exact balance**.

2. **Azimuthal (Swirl) Reynolds Number ($Re_\theta$)**:
   $$Re_\theta(\tau) \equiv \frac{|u_\theta| \, \ell_r}{\nu} \asymp \frac{\tau^{-1/2 - h} \cdot \tau^{1/2}}{\nu} = \frac{\tau^{-h}}{\nu} \xrightarrow[\tau \to 0^+]{} \infty.$$
   **Finding**: Because $h > 0$, the azimuthal Reynolds number diverges to infinity! The swirl dynamics become asymptotically inviscid relative to the radial diffusion scale.

3. **Axial Reynolds Number ($Re_z$)**:
   $$Re_z(\tau) \equiv \frac{|u_z| \, \ell_z}{\nu} \asymp \frac{\tau^{-1/2 - h} \cdot \tau^{1/2 - h}}{\nu} = \frac{\tau^{-1 - 2h}}{\nu} \xrightarrow[\tau \to 0^+]{} \infty.$$
   **Finding**: The axial Reynolds number diverges even faster ($\sim \tau^{-1 - 2h}$), indicating that axial convection completely overpowers axial viscous diffusion.

---

## 2. Term-by-Term Asymptotic Balance in the Equations of Motion

To determine why viscosity fails to prevent the singularity, we evaluate every differential operator in cylindrical coordinates $(r, \theta, z)$ with axisymmetry ($\partial_\theta \equiv 0$).

### 2.1 Azimuthal Momentum Equation
$$\underbrace{\partial_t u_\theta}_{(1)} + \underbrace{u_r \partial_r u_\theta}_{(2)} + \underbrace{u_z \partial_z u_\theta}_{(3)} + \underbrace{\frac{u_r u_\theta}{r}}_{(4)} = \underbrace{\nu \left( \partial_r^2 u_\theta + \frac{1}{r}\partial_r u_\theta - \frac{u_\theta}{r^2} \right)}_{(5)} + \underbrace{\nu \partial_z^2 u_\theta}_{(6)}.$$

Asymptotic scalings of each term:
- Term (1) Unsteady acceleration:
  $$\partial_t u_\theta \sim \frac{u_\theta}{\tau} \sim \tau^{-3/2 - h}.$$
- Term (2) Radial convection:
  $$u_r \partial_r u_\theta \sim \tau^{-1/2} \cdot \frac{\tau^{-1/2 - h}}{\tau^{1/2}} = \tau^{-3/2 - h}.$$
- Term (3) Axial convection:
  $$u_z \partial_z u_\theta \sim \tau^{-1/2 - h} \cdot \frac{\tau^{-1/2 - h}}{\tau^{1/2 - h}} = \tau^{-3/2 - h}.$$
- Term (4) Geometric Coriolis / curvature convection:
  $$\frac{u_r u_\theta}{r} \sim \frac{\tau^{-1/2} \cdot \tau^{-1/2 - h}}{\tau^{1/2}} = \tau^{-3/2 - h}.$$
- Term (5) Radial viscous diffusion:
  $$\nu \Delta_r u_\theta \sim \nu \frac{u_\theta}{\ell_r^2} \sim \nu \frac{\tau^{-1/2 - h}}{\tau} = \nu \tau^{-3/2 - h}.$$
- Term (6) Axial viscous diffusion:
  $$\nu \partial_z^2 u_\theta \sim \nu \frac{u_\theta}{\ell_z^2} \sim \nu \frac{\tau^{-1/2 - h}}{\tau^{1 - 2h}} = \nu \tau^{-3/2 + h}.$$

### Critical Conclusion for Azimuthal Balance
Notice the comparison between Term (5) and Term (6):
$$\frac{\text{Axial Diffusion (6)}}{\text{Radial Diffusion (5)}} = \frac{\tau^{-3/2 + h}}{\tau^{-3/2 - h}} = \tau^{2h} \xrightarrow[\tau \to 0^+]{} 0.$$
Because the filament elongates axially ($\ell_z \gg \ell_r$), **axial diffusion is completely negligible** compared to radial diffusion!
Meanwhile, Terms (1), (2), (3), (4), and (5) **all balance at the exact same leading order $\tau^{-3/2 - h}$**:
$$\partial_t u_\theta + u_r \partial_r u_\theta + u_z \partial_z u_\theta + \frac{u_r u_\theta}{r} - \nu \left( \partial_r^2 u_\theta + \frac{1}{r}\partial_r u_\theta - \frac{u_\theta}{r^2} \right) = \mathcal{O}\left(\tau^{-3/2 + h}\right).$$

---

### 2.2 Axial Momentum Equation
$$\underbrace{\partial_t u_z}_{(1)} + \underbrace{u_r \partial_r u_z}_{(2)} + \underbrace{u_z \partial_z u_z}_{(3)} = \underbrace{-\partial_z p}_{(4)} + \underbrace{\nu \left( \partial_r^2 u_z + \frac{1}{r}\partial_r u_z \right)}_{(5)} + \underbrace{\nu \partial_z^2 u_z}_{(6)}.$$

Asymptotic scalings:
- Term (1) Unsteady: $\partial_t u_z \sim \tau^{-3/2 - h}$.
- Term (2) Radial convection: $u_r \partial_r u_z \sim \tau^{-3/2 - h}$.
- Term (3) Axial convection: $u_z \partial_z u_z \sim \tau^{-3/2 - h}$.
- Term (4) Axial pressure gradient: $-\partial_z p \sim \frac{p}{\ell_z} \sim \frac{\tau^{-1 - 2h}}{\tau^{1/2 - h}} = \tau^{-3/2 - h}$.
- Term (5) Radial diffusion: $\nu \Delta_r u_z \sim \nu \tau^{-3/2 - h}$.
- Term (6) Axial diffusion: $\nu \partial_z^2 u_z \sim \nu \tau^{-3/2 + h}$ (subleading by $\tau^{2h}$).

Again, all leading terms (unsteady, convection, axial pressure gradient, and radial diffusion) **match identically at order $\tau^{-3/2 - h}$**.

---

## 3. Why Viscosity Fails to Stop the Singularity

It is often conjectured that 3D Navier–Stokes solutions cannot blow up because viscous dissipation $\nu \Delta u$ dominates at high wavenumbers ($k^2 \to \infty$). Why does this standard intuition fail here?

### The Mathematical Reason: Scaling Invariance of Radial Diffusion
1. **Dissipation matches convection**: At scale $\ell_r \sim \sqrt{\tau}$, the Laplace operator scales as $\Delta \sim 1/\ell_r^2 \sim 1/\tau$. Viscosity acts with rate $\nu / \tau$, which is the natural time-scale of the collapse.
2. **Radial diffusion does not suppress the core; it shapes it**: Rather than damping the velocity to zero, radial diffusion balances radial inflow to establish a stationary profile in self-similar coordinates $\xi = r/\sqrt{\tau}$. This is mathematically identical to how viscosity operates in Burgers' vortex: the vortex tube does not diffuse away because the continuous radial inflow $u_r = -\alpha r$ replenishes the vorticity at the same rate that diffusion spreads it.
3. **Anisotropy defeats 3D scalar dissipation bounds**: In isotropic scaling ($\ell_x \sim \ell_y \sim \ell_z \sim \tau^{1/2}$), the total enstrophy dissipation $\nu \int |\nabla u|^2 dx$ would scale as $\nu (\tau^{-1})^2 \tau^{3/2} = \nu \tau^{-1/2}$, which is integrable in time ($\int_0^1 \tau^{-1/2} d\tau < \infty$). But here, because of axial elongation and swirl:
   $$\nu \int |\nabla u|^2 dx \sim \nu (\tau^{-1 - h})^2 \cdot \tau^{3/2 - h} = \nu \tau^{-1/2 - 3h}.$$
   For $h > 1/6$, the integral $\int_0^1 \tau^{-1/2 - 3h} d\tau$ diverges!
   Even for small $h < 1/6$ where energy dissipation remains finite, the $L^\infty$ gradient $\|\nabla u\|_{L^\infty} \sim \tau^{-1 - h}$ blows up faster than the scale-critical rate $\tau^{-1}$.

### Summary of Term Hierarchies
$$\begin{array}{|l|c|c|l|}
\hline
\textbf{Equation} & \textbf{Leading Order Terms } (\tau^{-3/2 - h}) & \textbf{Subleading Terms } (\le \tau^{-3/2 + h}) & \textbf{Balance Type} \\
\hline
\text{Radial } (r) & \partial_r p \text{ balances } u_\theta^2 / r & \partial_t u_r, \, (u\cdot\nabla)u_r, \, \nu\Delta u_r & \text{Centripetal Equilibrium} \\
\text{Azimuthal } (\theta) & \partial_t u_\theta, \, u_r \partial_r u_\theta, \, u_z \partial_z u_\theta, \, \nu \Delta_r u_\theta & \nu \partial_z^2 u_\theta & \text{Convective–Diffusive Self-Similar ODE} \\
\text{Axial } (z) & \partial_t u_z, \, (u\cdot\nabla)u_z, \, \partial_z p, \, \nu \Delta_r u_z & \nu \partial_z^2 u_z & \text{Pressure–Convection–Diffusion ODE} \\
\hline
\end{array}$$
