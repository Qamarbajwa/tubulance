# TP2-G2: EXACT NAVIER–STOKES SCALING AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G2 (Exact Scaling Gate)`  
**Governance:** Mid-Project Governance v2.9  
**Status:** Authoritative Mathematical Derivation  

---

## 1. Parabolic Navier–Stokes Invariant Scaling

The incompressible Navier–Stokes equations in $\mathbb{R}^3$ (with viscosity $\nu > 0$ fixed):
$$\partial_t u + (u \cdot \nabla) u + \nabla p = \nu \Delta u, \quad \nabla \cdot u = 0,$$
are invariant under the family of parabolic rescalings parameterized by $\lambda > 0$:
$$u_\lambda(x, t) = \lambda u(\lambda x, \lambda^2 t), \qquad p_\lambda(x, t) = \lambda^2 p(\lambda x, \lambda^2 t).$$
Under this scaling:
- Spatial coordinates scale as $x \mapsto \lambda x \implies [x] = \lambda^{-1}$.
- Temporal coordinates scale as $t \mapsto \lambda^2 t \implies [t] = \lambda^{-2}$.
- Spatial gradient scales as $\nabla_x \mapsto \lambda \nabla_y \implies [\nabla] = \lambda^1$.

---

## 2. Derivation of Object Exponents

### 2.1 Velocity and Differential Operators
- Velocity: $[u] = \lambda^1$.
- Vorticity $\omega = \nabla \times u$:
  $$\omega_\lambda(x,t) = \nabla_x \times u_\lambda(x,t) = \lambda \nabla_x \times [u(\lambda x, \lambda^2 t)] = \lambda^2 (\nabla_y \times u)(\lambda x, \lambda^2 t) = \lambda^2 \omega(\lambda x, \lambda^2 t) \implies [\omega] = \lambda^2.$$
- Rate-of-strain tensor $S = \frac{1}{2}(\nabla u + (\nabla u)^T)$:
  $$S_\lambda(x,t) = \lambda^2 S(\lambda x, \lambda^2 t) \implies [S] = \lambda^2.$$

### 2.2 Brownian Motion and Stochastic Trajectories
Standard 3D Brownian motion $W_t$ satisfies the parabolic self-similarity:
$$W_{\lambda^2 t} \overset{d}{=} \lambda W_t.$$
The forward stochastic trajectory $X_{s,t}^\lambda(a)$ under rescaled velocity $u_\lambda$ satisfies:
$$X_{s,t}^\lambda(a) = a + \int_s^t \lambda u(\lambda X_{s,\tau}^\lambda(a), \lambda^2 \tau) d\tau + \sqrt{2\nu}(W_t - W_s).$$
Multiplying by $\lambda$ and substituting $\tau' = \lambda^2 \tau$, $d\tau' = \lambda^2 d\tau$, $B_{\tau'} = \lambda W_{\tau'/\lambda^2}$:
$$\lambda X_{s,t}^\lambda(a) = \lambda a + \int_{\lambda^2 s}^{\lambda^2 t} u(\lambda X_{s,\tau'/\lambda^2}^\lambda(a), \tau') d\tau' + \sqrt{2\nu}(B_{\lambda^2 t} - B_{\lambda^2 s}).$$
Therefore:
$$\lambda X_{s,t}^\lambda(a) \overset{d}{=} X_{\lambda^2 s, \lambda^2 t}(\lambda a) \implies X_{s,t}^\lambda(a) \overset{d}{=} \lambda^{-1} X_{\lambda^2 s, \lambda^2 t}(\lambda a) \implies [X] = \lambda^{-1}.$$
Similarly for the inverse map $A_{s,t}^\lambda(x)$:
$$A_{s,t}^\lambda(x) \overset{d}{=} \lambda^{-1} A_{\lambda^2 s, \lambda^2 t}(\lambda x) \implies [A] = \lambda^{-1}.$$

### 2.3 Deformation Gradients $F$ and $D$
- Forward deformation gradient $F_{s,t}^\lambda(a) = \nabla_a X_{s,t}^\lambda(a)$:
  $$F_{s,t}^\lambda(a) = \nabla_a \left[ \lambda^{-1} X_{\lambda^2 s, \lambda^2 t}(\lambda a) \right] = \lambda^{-1} \cdot \lambda \nabla_y X_{\lambda^2 s, \lambda^2 t}(\lambda a) = F_{\lambda^2 s, \lambda^2 t}(\lambda a) \implies [F] = \lambda^0.$$
- Inverse deformation operator $D_t^s(x) = (\nabla_x A_{s,t}(x))^{-1} = F_{s,t}(A_{s,t}(x))$:
  $$(D_t^s)^\lambda(x) = F_{s,t}^\lambda(A_{s,t}^\lambda(x)) \overset{d}{=} F_{\lambda^2 s, \lambda^2 t}(A_{\lambda^2 s, \lambda^2 t}(\lambda x)) = D_{\lambda^2 t}^{\lambda^2 s}(\lambda x) \implies [D] = \lambda^0.$$
Both deformation operators are **dimensionless and scale-invariant**.

### 2.4 Stochastic Cauchy Vector $Z_s^{x,t}$ and Statistical Moments
- Cauchy contribution $Z_s^{x,t} = D_t^s(x) \, \omega(A_{s,t}(x), s)$:
  $$(Z_s^{x,t})_\lambda = (D_t^s)^\lambda(x) \, \omega_\lambda(A_t^{s, \lambda}(x), s) \overset{d}{=} D_{\lambda^2 t}^{\lambda^2 s}(\lambda x) \cdot \lambda^2 \omega(A_{\lambda^2 t}^{\lambda^2 s}(\lambda x), \lambda^2 s) = \lambda^2 Z_{\lambda^2 s}^{\lambda x, \lambda^2 t} \implies [Z] = \lambda^2.$$
- Expectation $\mathbb{E} Z$:
  $$\mathbb{E}[(Z_s^{x,t})_\lambda] = \lambda^2 \mathbb{E}[Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}] = \lambda^2 \omega(\lambda x, \lambda^2 t) \implies [\mathbb{E} Z] = \lambda^2.$$
- Squared norm of expectation $|\mathbb{E} Z|^2$:
  $$|\mathbb{E}[(Z_s^{x,t})_\lambda]|^2 = \lambda^4 |\mathbb{E}[Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}]|^2 \implies [|\mathbb{E} Z|^2] = \lambda^4.$$
- Mean-square norm $\mathbb{E}|Z|^2$:
  $$\mathbb{E}[|(Z_s^{x,t})_\lambda|^2] = \lambda^4 \mathbb{E}[|Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}|^2] \implies [\mathbb{E}|Z|^2] = \lambda^4.$$
- Variance $\operatorname{Var}(Z) = \mathbb{E}|Z|^2 - |\mathbb{E}Z|^2$:
  $$\operatorname{Var}((Z_s^{x,t})_\lambda) = \lambda^4 \operatorname{Var}(Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}) \implies [\operatorname{Var}(Z)] = \lambda^4.$$

### 2.5 Candidate Coherence Ratio $\chi(x,t;s)$
$$\chi_\lambda(x,t;s) = \frac{|\mathbb{E}[(Z_s^{x,t})_\lambda]|^2}{\mathbb{E}[|(Z_s^{x,t})_\lambda|^2]} = \frac{\lambda^4 |\mathbb{E}[Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}]|^2}{\lambda^4 \mathbb{E}[|Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}|^2]} = \chi(\lambda x, \lambda^2 t; \lambda^2 s) \implies \boxed{[\chi] = \lambda^0}.$$

---

## 3. Classification and Criticality Taxonomy

### 3.1 Classification of $\chi$
$$\boxed{ \chi(x,t;s) \in \text{EXACT\_SCALE\_INVARIANT\_QUANTITY} }$$
**Crucial Distinction:** $\chi$ is **NOT** a regularity criterion.
By Cauchy–Schwarz, $0 \le \chi(x,t;s) \le 1$ holds for **every** random vector in $L^2(\Omega_{\text{prob}})$, regardless of whether the fluid solution is smooth, turbulent, or singular. Bounding $\chi \le 1$ provides zero regularity information by itself.

### 3.2 Enumeration of Mathematically Admissible Critical Forms
To construct a scale-critical continuation or regularity quantity, $\chi$ or its complementary variance must be coupled to dimensional critical norms:
Let $d x \sim \lambda^{-3}$, $d t \sim \lambda^{-2}$.

1. **Critical Mixed Spacetime Vorticity-Norm Formulations**:
   - $\|\omega\|_{L_t^p L_x^q}$ is critical if $\frac{2}{p} + \frac{3}{q} = 2$.
   - The stochastic root-mean-square norm $\left\| \left( \mathbb{E}|Z_0^{\cdot, t}|^2 \right)^{1/2} \right\|_{L_x^{3/2}}$ is scale-critical:
     $$\lambda^2 \cdot (\lambda^{-3})^{2/3} = \lambda^2 \cdot \lambda^{-2} = \lambda^0.$$
2. **Critical Coherence-Modulated Dissipation Forms**:
   - Scale-critical variance integral:
     $$\mathcal{I}_{\text{crit}} = \int_0^T \left\| \sqrt{1 - \chi(\cdot, t; 0)} \left( \mathbb{E}|Z_0^{\cdot, t}|^2 \right)^{1/2} \right\|_{L_x^{3/2}} dt \quad (\text{Scale Exponent } \lambda^0).$$
3. **Mahithitarmmatorn Quotient Criterion Form**:
   - The spatial quotient:
     $$Q_{\text{crit}}(t) = \frac{\| \mathbb{E}|Z_0^{\cdot, t}|^2 \|_{L_x^{3/4}}}{\| \omega(\cdot, t) \|_{L_x^{3/2}}^2} \quad (\text{Scale Exponent } \lambda^0).$$

*(Note: These forms are enumerated as mathematically admissible critical candidates; none is asserted as proved or preferred in this increment).*
