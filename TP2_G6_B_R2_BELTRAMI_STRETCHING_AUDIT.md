# TP2-G6-B-R2: Beltrami Vortex Stretching and Benchmark Qualification

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R2 (Audit Question 2)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. Mathematical Derivation of Beltrami Vortex Stretching

Let $u$ be any smooth Beltrami velocity field on $\mathbb{T}^3$ satisfying the curl eigen-relation:
\[
\nabla \times u = k u, \quad \omega = k u \quad (k \in \mathbb{R} \setminus \{0\}).
\]
Incompressibility $\nabla \cdot u = 0$ is automatic since $\nabla \cdot (\nabla \times u) = 0$.

### 1.1 Non-Linear Convection and Vortex Stretching Vector
Using the vector identity $(u \cdot \nabla)u = (\nabla \times u) \times u + \nabla \frac{|u|^2}{2}$:
\[
(u \cdot \nabla)u = (k u) \times u + \nabla \frac{|u|^2}{2} = 0 + \nabla \frac{|u|^2}{2} = \nabla \frac{|u|^2}{2}.
\]
Therefore, the vortex stretching vector $(\omega \cdot \nabla)u$ is:
\[
(\omega \cdot \nabla)u = (k u \cdot \nabla)u = k (u \cdot \nabla)u = k \nabla \frac{|u|^2}{2}.
\]
At the same time, the vorticity advection vector is:
\[
(u \cdot \nabla)\omega = (u \cdot \nabla)(k u) = k (u \cdot \nabla)u = k \nabla \frac{|u|^2}{2}.
\]
Subtracting the two vectors:
\[
\boxed{ (\omega \cdot \nabla)u - (u \cdot \nabla)\omega \equiv 0 \quad \text{identically for ALL Beltrami fields} }.
\]
In the 3D vorticity equation:
\[
\partial_t \omega + (u \cdot \nabla)\omega = (\omega \cdot \nabla)u + \nu \Delta \omega \iff \partial_t \omega = \nu \Delta \omega.
\]
The non-linear terms $(\omega \cdot \nabla)u$ and $(u \cdot \nabla)\omega$ **cancel each other identically** in the vorticity transport equation. Every Beltrami field decays as a purely linear diffusion mode:
\[
u(x, t) = e^{-\nu k^2 t} u_0(x), \quad \omega(x, t) = e^{-\nu k^2 t} \omega_0(x).
\]

---

## 2. Pointwise Symmetric Stretching Contraction: $\omega \cdot S \omega$

Now consider the symmetric stretching contraction $\omega \cdot S \omega$, where $S = \frac{1}{2}(\nabla u + (\nabla u)^\top)$:
\[
\omega \cdot S \omega = \omega \cdot (\omega \cdot \nabla)u = (k u) \cdot \left(k \nabla \frac{|u|^2}{2}\right) = \boxed{ k^2 u \cdot \nabla \frac{|u|^2}{2} }.
\]

### 2.1 Spatial Mean vs Pointwise Value
Because $\nabla \cdot u = 0$, the spatial integral over $\mathbb{T}^3$ is an exact divergence:
\[
\int_{\mathbb{T}^3} \omega \cdot S \omega \, dx = k^2 \int_{\mathbb{T}^3} u \cdot \nabla \frac{|u|^2}{2} \, dx = k^2 \int_{\mathbb{T}^3} \nabla \cdot \left( u \frac{|u|^2}{2} \right) dx = 0.
\]
Thus, the **mean enstrophy production of any Beltrami field on $\mathbb{T}^3$ is identically zero**.

### 2.2 Subclass Classification: Constant-Speed vs General ABC Fields
Pointwise, however, $\omega \cdot S \omega$ depends on the spatial gradient of kinetic energy:
1. **Constant-Speed / Single Helical Mode Subclass:**
   If $|u_0|^2$ is spatially uniform (e.g. $u_0 = (\cos kz, \sin kz, 0)$ or single helical waves with constant amplitude), then:
   \[
   \nabla |u_0|^2 \equiv 0 \implies \boxed{ \omega \cdot S \omega \equiv 0 \quad \text{identically everywhere in space and time} }.
   \]
2. **General Multi-Mode ABC Flow Subclass:**
   For general ABC flows with $A, B, C \ne 0$:
   \[
   u = (A \sin kz + C \cos ky, B \sin kx + A \cos kz, C \sin ky + B \cos kx),
   \]
   the speed $|u|^2$ is not spatially constant. The contraction $\omega \cdot S \omega = k^2 u \cdot \nabla \frac{|u|^2}{2}$ is **positive in some spatial regions and negative in others**, even though its net dynamic contribution to $\partial_t \omega$ cancels with advection.

---

## 3. R1 Benchmark Qualification and Disposition

- **Audit Finding:** In `TP2-G6-B-R1`, the statement $\omega \cdot S \omega \equiv 0$ in Family 2 is **strictly valid for the constant-speed / single-helical Beltrami benchmark**, and holds on spatial average for all Beltrami flows, but is not pointwise identically zero for general multi-mode ABC flows.
- **Disposition:** `RETAINED_WITH_QUALIFICATION`.
- **Corrected Formulation:** The Beltrami benchmark row in the adversarial matrix is explicitly qualified as:
  `CONSTANT-SPEED / SINGLE-HELICAL BELTRAMI BENCHMARK` (where $\omega \cdot S \omega \equiv 0$ pointwise). For general ABC flows, the non-linear vorticity transport cancels dynamically ($(\omega \cdot \nabla)u - (u \cdot \nabla)\omega \equiv 0$), while $\int_{\mathbb{T}^3} \omega \cdot S \omega dx = 0$ globally.
