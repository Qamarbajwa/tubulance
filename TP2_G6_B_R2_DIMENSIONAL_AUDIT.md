# TP2-G6-B-R2: Dimensional Audit and Stretching Exponent Reconciliation

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R2 (Audit Question 5)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. Dimensional Master Table

Let $[L]$ denote length, $[T]$ denote time, and $\lambda$ denote the parabolic scaling dilation factor ($x \mapsto \lambda x, t \mapsto \lambda^2 t$).

| Quantity | Mathematical Symbol | Physical Dimension $[L, T]$ | Parabolic Scaling Weight $[\lambda]$ | Exact Meaning |
|---|---|---|---|---|
| Velocity | $u$ | $L T^{-1}$ | $\lambda^1$ | Solution field |
| Strain Tensor | $S = \frac{1}{2}(\nabla u + \nabla u^\top)$ | $T^{-1}$ | $\lambda^2$ | Symmetric velocity gradient |
| Vorticity Vector | $\omega = \nabla \times u$ | $T^{-1}$ | $\lambda^2$ | Curl of velocity |
| Peak Vorticity | $M_n = \|\omega(\cdot, t_n)\|_{L^\infty}$ | $T^{-1}$ | $\lambda^2$ | Maximum local amplitude |
| Intrinsic Window | $L_n = a / M_n$ ($a$ dimensionless) | $T$ | $\lambda^{-2}$ | Lookback time interval |
| Kinematic Viscosity | $\nu$ | $L^2 T^{-1}$ | $\lambda^0$ | Physical fluid parameter |
| Vorticity Gradient | $G = \nabla \omega = J_\omega$ | $L^{-1} T^{-1}$ | $\lambda^3$ | Spatial derivative of vorticity |
| Gradient Source | $T = (\nabla S)\omega$ | $L^{-1} T^{-2}$ | $\lambda^5$ | Source in gradient equation |
| Relative QV Density | $\Xi = \|D J_\omega\|_F^2 / |D\omega|^2$ | $L^{-2}$ | $\lambda^2$ | Inverse squared length scale |
| Intrinsic Production | $J_n(a) = 2\nu \int_{s_n}^{t_n} \mathbb{E}_{\mu_r}[\Xi_r] dr$ | $1$ (Dimensionless) | $\lambda^0$ | Accumulated log-coherence rate |

---

## 2. Disambiguation of the Three "Vortex Stretching" Objects

In `TP2-G6-B-R1`, the phrase "stretching of order $M_n$" versus "stretching of order $M_n^2$" appeared in close proximity without distinguishing their mathematical roles.

The project formally disambiguates the three distinct stretching quantities:

### 2.1 The Vortex Stretching Rate: $\sigma_{\text{stretch}}$ (Dimension $T^{-1}$, Scaling $M_n^1$)
\[
\sigma_{\text{stretch}} := \frac{\omega \cdot S \omega}{|\omega|^2} = \xi \cdot S \xi, \quad \text{where } \xi = \frac{\omega}{|\omega|}.
\]
- **Physical Role:** The instantaneous fractional growth rate $\frac{d}{dt} \ln |\omega|$.
- **Scaling Magnitude:** When strain aligns with peak vorticity, $\|S\| \sim M_n$, so:
  \[
  \sigma_{\text{stretch}} \sim M_n \quad (\text{Order } 1 \text{ in } M_n).
  \]

### 2.2 The Vortex Stretching Vector: $\mathcal{V}_{\text{stretch}}$ (Dimension $T^{-2}$, Scaling $M_n^2$)
\[
\mathcal{V}_{\text{stretch}} := (\omega \cdot \nabla)u = S \omega + \Omega \omega.
\]
- **Physical Role:** The vector forcing term on the right-hand side of the 3D vorticity equation:
  \[
  \partial_t \omega + (u \cdot \nabla)\omega = \mathcal{V}_{\text{stretch}} + \nu \Delta \omega.
  \]
- **Scaling Magnitude:**
  \[
  \|\mathcal{V}_{\text{stretch}}\| \le \|S\| |\omega| \sim M_n^2 \quad (\text{Order } 2 \text{ in } M_n).
  \]

### 2.3 The Enstrophy Production Density: $\mathcal{P}_{\text{enstrophy}}$ (Dimension $T^{-3}$, Scaling $M_n^3$)
\[
\mathcal{P}_{\text{enstrophy}} := \omega \cdot S \omega = \omega \cdot \mathcal{V}_{\text{stretch}} = |\omega|^2 \sigma_{\text{stretch}}.
\]
- **Physical Role:** The integrand in the global enstrophy production identity:
  \[
  \frac{1}{2} \frac{d}{dt} \int_{\mathbb{T}^3} |\omega|^2 dx = \int_{\mathbb{T}^3} \mathcal{P}_{\text{enstrophy}} dx - \nu \int_{\mathbb{T}^3} |\nabla \omega|^2 dx.
  \]
- **Scaling Magnitude:**
  \[
  |\mathcal{P}_{\text{enstrophy}}| \le \|S\| |\omega|^2 \sim M_n^3 \quad (\text{Order } 3 \text{ in } M_n).
  \]

---

## 3. Standardization for All Subsequent Increments

All project artifacts, claims, and proofs must strictly use the disambiguated terminology:
- Use **"Stretching Rate"** when referring to $\sigma_{\text{stretch}} = \frac{\omega \cdot S \omega}{|\omega|^2} \sim M_n$.
- Use **"Stretching Vector"** when referring to $\mathcal{V}_{\text{stretch}} = S \omega \sim M_n^2$.
- Use **"Enstrophy Production Density"** when referring to $\mathcal{P}_{\text{enstrophy}} = \omega \cdot S \omega \sim M_n^3$.
This eliminates all exponent ambiguity.
