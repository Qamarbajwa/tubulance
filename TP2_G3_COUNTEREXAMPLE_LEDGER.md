# TP2-G3: COUNTEREXAMPLE LEDGER & NO-GO ADVERSARIAL AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Permanent Adversarial Record  

---

## 1. Adversarial Falsification: Universal Viscous Decoherence

### The Question Under Attack:
*Does viscosity $\nu > 0$ universally force stochastic Cauchy decoherence ($\chi < 1$ or $V_s > 0$) for every 3D Navier–Stokes solution?*

---

## 2. Counterexample 1: Uniform Shear Flow (Couette Flow)

- **Velocity Field**:
  $$u(x, y, z) = (S y, 0, 0), \quad S \in \mathbb{R} \setminus \{0\}.$$
- **Incompressibility & Navier–Stokes Solution**:
  $$\nabla \cdot u = 0, \quad (u \cdot \nabla) u = 0, \quad \Delta u = 0 \implies \partial_t u + (u \cdot \nabla) u = \nu \Delta u \text{ with } p = \text{const}.$$
- **Vorticity Field**:
  $$\omega(x, y, z) = \nabla \times u = (0, 0, -S) = \text{constant in space and time}.$$
- **Spatial Vorticity Jacobian**:
  $$J_\omega(x, y, z) \equiv 0 \quad \text{everywhere in } \mathbb{R}^3.$$
- **Evaluation of G3 Covariance and Variance**:
  $$\Sigma_s = \sqrt{2\nu} D_s J_\omega(A_s, s) \equiv 0.$$
  $$C_s = 2\nu \int_s^T \mathbb{E}[ D_r (J_\omega J_\omega^T) D_r^T ] dr \equiv 0.$$
  $$V_s = \operatorname{tr}(C_s) \equiv 0.$$
  $$\chi_s = \frac{|\omega(x, T)|^2}{|\omega(x, T)|^2 + 0} \equiv 1.0 \quad \text{for all } s \in [0, T].$$

### Verdict on Universal Viscous Decoherence:
$$\boxed{\textbf{UNIVERSAL\_STRICT\_DECOHERENCE\_BY\_VISCOSITY = FALSE}}$$

**Scientific Conclusion**:
Viscosity $\nu > 0$ alone **cannot** induce stochastic decoherence or variance growth in regions where vorticity is spatially uniform. Stochastic decoherence strictly requires nonzero vorticity gradients ($J_\omega \neq 0$).

---

## 3. Counterexample 2: Deterministic Rigid Rotation / Beltrami Flow

- In any exact Navier–Stokes flow where vorticity is collinear with an eigenvector of diffusion or locally uniform, $J_\omega$ may have low rank or vanishing projections.
- In directions orthogonal to the span of the rows of $J_\omega$, the covariance tensor $C_s$ has zero eigenvalues ($\operatorname{rank}(C_s) < 3$).
- Therefore, stochastic Cauchy cancellation can be **strictly anisotropic or rank-deficient**.
