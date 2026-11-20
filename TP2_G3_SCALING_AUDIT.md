# TP2-G3: SCALING AUDIT OF COVARIANCE & VARIANCE OBJECTS

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Scaling Audit  

---

## 1. Navier–Stokes Parabolic Scaling Framework

Under the Navier–Stokes scaling parameter $\lambda > 0$:
$$u_\lambda(x,t) = \lambda u(\lambda x, \lambda^2 t), \quad [u] = \lambda^1, \quad [x] = \lambda^{-1}, \quad [t] = \lambda^{-2}, \quad [\nu] = \lambda^0.$$

From previous gate TP2-G2:
$$[\omega] = \lambda^2, \quad [S] = \lambda^2, \quad [D] = \lambda^0, \quad [Z] = \lambda^2, \quad [\chi] = \lambda^0.$$

---

## 2. Derivation of Exponents for G3 Differential and Covariance Objects

1. **Vorticity Spatial Gradient $J_\omega = \nabla_M \omega$**:
   $$[J_\omega]_{ij} = \frac{\partial \omega_i}{\partial x_j} \implies [J_\omega] = [\nabla] + [\omega] = 1 + 2 = \boxed{\lambda^3}.$$
2. **Stochastic Noise Matrix $\Sigma = \sqrt{2\nu} D J_\omega$**:
   $$[\Sigma] = [\sqrt{\nu}] + [D] + [J_\omega] = 0 + 0 + 3 = \boxed{\lambda^3}.$$
3. **Instantaneous Covariance Production Tensor $\Sigma \Sigma^T$**:
   $$[\Sigma \Sigma^T] = [\Sigma] + [\Sigma^T] = 3 + 3 = \boxed{\lambda^6}.$$
4. **Time Differential $ds$ / $dr$**:
   $$[ds] = [dt] = \boxed{\lambda^{-2}}.$$
5. **Integrated Covariance Tensor $C_s = \int_s^T \mathbb{E}[\Sigma_r \Sigma_r^T] dr$**:
   $$[C_s] = [\Sigma \Sigma^T] + [dr] = 6 + (-2) = \boxed{\lambda^4}.$$
6. **Scalar Variance $V_s = \operatorname{tr}(C_s)$**:
   $$[V_s] = [C_s] = \boxed{\lambda^4}.$$
   *(Matches the enstrophy density scaling $[|\omega|^2] = \lambda^4$).*
7. **Time Derivative of Covariance $\frac{\partial}{\partial s} C_s = -\mathbb{E}[\Sigma_s \Sigma_s^T]$**:
   $$\left[ \frac{\partial C}{\partial s} \right] = [C] - [s] = 4 - (-2) = \boxed{\lambda^6} \equiv [\Sigma \Sigma^T].$$
8. **Time Derivative of Scalar Variance $\frac{\partial}{\partial s} V_s$**:
   $$\left[ \frac{\partial V}{\partial s} \right] = \boxed{\lambda^6}.$$
9. **Coherence Ratio $\chi_s = \frac{|\omega|^2}{|\omega|^2 + V_s}$**:
   $$[\chi_s] = [|\omega|^2] - [V_s] = 4 - 4 = \boxed{\lambda^0 \quad (\text{Exact Scale Invariant})}.$$
10. **Time Derivative of Coherence Ratio $\frac{\partial}{\partial s} \chi_s$**:
    $$\left[ \frac{\partial \chi}{\partial s} \right] = [\chi] - [s] = 0 - (-2) = \boxed{\lambda^2}.$$

---

## 3. Summary Exponent Table

| Object | Definition | Parabolic Scaling Exponent | Scaling Classification |
|---|---|---|---|
| $J_\omega$ | Spatial Jacobian of vorticity $\nabla_M \omega$ | $+3$ | Scale-Critical Gradient |
| $\Sigma$ | Stochastic noise matrix $\sqrt{2\nu} D J_\omega$ | $+3$ | Scale-Critical Noise |
| $\Sigma \Sigma^T$ | Quadratic variation density rate | $+6$ | Instantaneous Rate |
| $C_s$ | Full $3 \times 3$ covariance tensor $\operatorname{Cov}(Z_s)$ | $+4$ | Enstrophy Density Scale |
| $V_s$ | Scalar variance $\operatorname{tr}(C_s)$ | $+4$ | Enstrophy Density Scale |
| $\partial_s C_s$ | Covariance rate of change | $+6$ | Instantaneous Rate |
| $\partial_s V_s$ | Scalar variance rate of change | $+6$ | Instantaneous Rate |
| $\chi_s$ | Coherence ratio $|\mathbb{E}Z|^2 / \mathbb{E}|Z|^2$ | **$0$** | **EXACT_SCALE_INVARIANT_QUANTITY** |
| $\partial_s \chi_s$ | Rate of change of coherence ratio | $+2$ | Vorticity Scale |
