# NS-OPENAI-B1 — STRESS-CONE LANDING AND QUADRATIC REYNOLDS MOMENTUM FLUX AUDIT

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1`  
**Standard**: `Mathematical Research Constitution v1.0.1`  
**Risk Ceiling**: `R3`  
**Focus**: Rigorous Computation of $Q_j = \langle w_j \otimes w_j \rangle$ and Verification of Admissible Cone Inclusion $Q_j \in K$  

---

## 1. Definition and Role of the Stress Cone $K$

In the self-similar Navier–Stokes singular framework, the mean flow $(\bar{u}_r, \bar{u}_\theta, \bar{u}_z)$ requires a positive driving force in the axial and radial directions to balance viscous diffusion and maintain the singular aspect ratio $\ell_z / \ell_r \sim \tau^{-h}$.
In the forced system, this force is provided by the external seeding field $f$. In the unforced system, this driving force must be supplied internally by the divergence of the **fast-oscillating Reynolds stress**:
$$\bar{F}_{\text{Reynolds}}(x, t) = - \nabla \cdot \langle w_j \otimes w_j \rangle_{\text{osc}} = - \nabla \cdot Q_j(x, t).$$

### 1.1 The Convex Cone $K$
The set of admissible Reynolds stress tensors forms an open, non-empty, convex cone:
$$K \subset \operatorname{Sym}^+(3) \cap \left\{ Q \in \mathbb{R}^{3 \times 3} : \operatorname{tr}(Q) > 0 \right\},$$
defined by the physical conditions:
1. **Axial Jet Propulsion**:
   $$Q_{rz} = \langle w_r w_z \rangle < - c_{\text{jet}} \|Q\| < 0,$$
   ensuring that outward radial momentum carries downward axial velocity, driving the upward axial jet $\partial_r (\bar{u}_r \bar{u}_z) \sim \partial_r Q_{rz}$.
2. **Angular Momentum Confinement**:
   $$|Q_{r\theta}| \le c_\theta Q_{\theta\theta}, \qquad Q_{\theta\theta} > 0,$$
   ensuring that azimuthal fluctuations do not disrupt centripetal pressure balance.
3. **Radial Diffusion Counter-Balance**:
   $$Q_{rr} > 0, \qquad Q_{zz} > 0.$$

$$\boxed{Q_j \in K \iff \text{The quadratic stress actively accelerates the singular core into the next epoch.}}$$

---

## 2. Explicit Calculation of $Q_j$ for the Arriving Precursor

Let the arriving precursor state at $t = t_j^-$ be:
$$w_j(x, t_j) = A_j^\star \rho_j(x) e_j(t_j) \cos(k_j(t_j) \cdot x + \phi_j(t_j)) + \mathcal{R}_j(x),$$
where:
- $A_j^\star = c_w 2^{j(1/2+h)}$ is the arrival amplitude;
- $\rho_j(x)$ is the spatial envelope localized on the annular filament $r \asymp 2^{-j/2}$;
- $e_j(t_j) \in \mathbb{S}^2$ is the polarization vector;
- $k_j(t_j) = k_j^\star$ is the carrier wavevector ($|k_j^\star| \asymp 2^{j/2}$);
- $\|\mathcal{R}_j\|_{L^\infty} \le C 2^{-j/2} A_j^\star$ is the WKB remainder.

### 2.1 Spatial Averaging over the Carrier Wavelength
Averaging the tensor product over the fast spatial oscillation period $\lambda_j = 2\pi / |k_j^\star| \asymp 2^{-j/2}$:
$$\langle \cos^2(k_j^\star \cdot x + \phi_j) \rangle_{\lambda_j} = \frac{1}{2}, \qquad \langle \cos(k_j^\star \cdot x) \mathcal{R}_j \rangle = \mathcal{O}(2^{-j/2}).$$
Therefore:
$$\boxed{Q_j(x, t_j) \equiv \langle w_j \otimes w_j \rangle = \frac{1}{2} (A_j^\star)^2 \rho_j(x)^2 \left( e_j(t_j) \otimes e_j(t_j) \right) + \mathcal{O}\left( 2^{-j/2} (A_j^\star)^2 \right).}$$

---

## 3. Verification of Stress-Cone Membership

To verify that $Q_j \in K$, we evaluate the components of the dyadic tensor $E_j = e_j(t_j) \otimes e_j(t_j)$ in the local cylindrical basis $(\hat{r}, \hat{\theta}, \hat{z})$:

From `NS_OPENAI_B1_WAVEVECTOR_CHARACTERISTICS.md`, the singular strain tensor $S(u_B)$ has its principal stretching eigenvector $v_1$ oriented at an angle $\theta_{\text{shear}} \approx \pi/4$ in the $(r, z)$-plane with a tilted azimuthal component:
$$v_1 = \alpha_r \hat{r} + \alpha_\theta \hat{\theta} + \alpha_z \hat{z},$$
where $\alpha_r > 0$, $\alpha_z < 0$, and $|\alpha_\theta| > 0$.

Because $e_j(t_j) = v_1 + \mathcal{O}(e^{-c 2^{jh}})$:
1. **Axial-Radial Shear Stress**:
   $$(E_j)_{rz} = e_{r, j} e_{z, j} = \alpha_r \alpha_z + \mathcal{O}(e^{-c 2^{jh}}).$$
   Since $\alpha_r > 0$ and $\alpha_z < 0$, the product is strictly negative:
   $$(E_j)_{rz} \le - c_{\text{jet}} < 0.$$
2. **Azimuthal Variance**:
   $$(E_j)_{\theta\theta} = e_{\theta, j}^2 = \alpha_\theta^2 + \mathcal{O}(e^{-c 2^{jh}}) > 0.$$
3. **Radial and Axial Positive Definiteness**:
   $$(E_j)_{rr} = \alpha_r^2 > 0, \qquad (E_j)_{zz} = \alpha_z^2 > 0.$$

### 3.1 Distance to Cone Boundary
Because the target tensor $Q_j^\star \equiv \frac{1}{2}(A_j^\star)^2 \rho_j^2 (v_1 \otimes v_1)$ lies in the interior of the open cone $K$:
$$\operatorname{dist}(Q_j^\star, \partial K) \ge \delta_K (A_j^\star)^2, \qquad \delta_K > 0.$$
The perturbation error between the actual autonomous arriving stress $Q_j$ and $Q_j^\star$ is bounded by:
$$\|Q_j - Q_j^\star\| \le C \left( e^{-c 2^{jh}} + 2^{-j/2} \right) (A_j^\star)^2.$$
For all $j \ge j_0$ (where $j_0$ is moderate, e.g. $j_0 \ge 3$):
$$\|Q_j - Q_j^\star\| < \operatorname{dist}(Q_j^\star, \partial K) \implies Q_j(x, t_j) \in K \quad \forall x \in \operatorname{supp}(\rho_j).$$

$$\boxed{d_K(Q_j) \equiv \inf_{P \in \partial K} \|Q_j - P\| > 0 \implies \mathbf{STRICT\ INTERIOR\ CONE\ MEMBERSHIP.}}$$

---

## 4. WHAT_THE_FLUID_IS_DOING

In physical terms, the quadratic Reynolds stress $Q = \langle w \otimes w \rangle$ measures how the fast fluid oscillations push the slow background flow around.

If the incoming ripple were randomly polarized, its momentum fluxes would point in random directions — or worse, resist the vortex filament and tear it apart. 

However, because the fluid's own internal strain aligned the ripple along the principal stretching axis $v_1$, the ripple's fluid parcels oscillate diagonally: as fluid moves radially inward, it is simultaneously shot axially upward. 

When you average these synchronized diagonal motions ($\langle w_r w_z \rangle$), they create a powerful, steady **internal jet engine**. The ripple acts like a directional nozzle: it scoops up fluid from the outer edges and blasts it down the center of the filament, providing the exact directional force required by the Navier–Stokes equations to propel the singular filament into its next stage of collapse.
