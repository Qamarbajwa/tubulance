# TP2-G3: SPECTRAL RANK & POSITIVE SEMI-DEFINITENESS AUDIT

**Authority:** Independent E4 Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance Standard:** Autonomous Project Governance v2.9.3 (Tier T4)  
**Status:** Authoritative Spectral Audit  

---

## 1. Matrix Product Structure

The instantaneous covariance production rate matrix is:
$$R_s := \mathbb{E}[ \Sigma_s \Sigma_s^T ] = 2\nu \, \mathbb{E}\left[ D_s (J_\omega J_\omega^T)(A_s, s) D_s^T \right].$$

Under the classical stochastic diffeomorphism regime ($u \in C([0, T]; C^2)$), $D_s \in SL(3, \mathbb{R})$ is strictly invertible ($\det D_s = 1$).
Therefore, for every pathwise realization:
$$\operatorname{rank}(\Sigma_s) = \operatorname{rank}(D_s J_\omega) = \operatorname{rank}(J_\omega(A_s, s)).$$

---

## 2. Spectral Rank Taxonomy

| Rank Condition | Physical / Geometric Scenario | Eigenvalues of $\Sigma \Sigma^T$ | Covariance Status $C_s$ |
|---|---|---|---|
| **$\operatorname{rank}(J_\omega) = 0$** | Spatially uniform vorticity ($\nabla_M \omega = 0$, e.g. Couette shear or pure translation) | $\lambda_1 = \lambda_2 = \lambda_3 = 0$ | $C_s = 0, V_s = 0$ (Zero production) |
| **$\operatorname{rank}(J_\omega) = 1$** | 1D shear layer ($\omega = \omega(y) \mathbf{e}_z$) | $\lambda_1 > 0, \lambda_2 = \lambda_3 = 0$ | $C_s \succeq 0$ (Rank 1, 2 null directions) |
| **$\operatorname{rank}(J_\omega) = 2$** | Planar 2D vortex flow ($\omega = \omega(x, y) \mathbf{e}_z$) | $\lambda_1 > 0, \lambda_2 > 0, \lambda_3 = 0$ | $C_s \succeq 0$ (Rank 2, 1 null direction) |
| **$\operatorname{rank}(J_\omega) = 3$** | Fully 3D anisotropic vortex gradient | $\lambda_1 > 0, \lambda_2 > 0, \lambda_3 > 0$ | $C_s \succ 0$ (Strictly Positive Definite) |

---

## 3. Positive Semi-Definiteness vs Positive Definiteness

1. **Semi-Definiteness ($C_s \succeq 0$)**:
   $C_s = 2\nu \int_s^T \mathbb{E}[ D_r J_\omega J_\omega^T D_r^T ] dr$ is **always positive semi-definite** for all $s \in [0, T]$.
2. **Definiteness ($C_s \succ 0$)**:
   $C_s$ is strictly positive definite for $s < T$ if and only if the expectation $\mathbb{E}[ D_r J_\omega J_\omega^T D_r^T ]$ has full rank when integrated across Brownian histories over $[s, T]$.
3. **Anisotropic Dispersion**:
   In directions orthogonal to the spatial gradient of vorticity, stochastic dispersion does not produce Cauchy variance.
