# TP2-G3: COVARIANCE OPERATOR & RANK STRUCTURE AUDIT

**Authority:** Independent E4 Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance Standard:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Mathematical Operator Audit  

---

## 1. Instantaneous Covariance Production Rate Tensor

The instantaneous rate of change of the covariance matrix in backward history time $s$ is:
$$R_s := -\frac{\partial}{\partial s} C_s = \mathbb{E}[ \Sigma_s \Sigma_s^T ] = 2\nu \, \mathbb{E}\left[ D_s \, (J_\omega J_\omega^T)(A_s, s) \, D_s^T \right].$$

### Matrix Multiplication Structure:
- Noise matrix: $\Sigma = \sqrt{2\nu} D J_\omega$.
- Transpose: $\Sigma^T = \sqrt{2\nu} J_\omega^T D^T$.
- Outer product: $\Sigma \Sigma^T = 2\nu D (J_\omega J_\omega^T) D^T$.
- Under **Convention M** ($[J_\omega]_{jk} = \frac{\partial \omega_j}{\partial x_k}$), $[J_\omega J_\omega^T]_{jl} = \sum_k \frac{\partial \omega_j}{\partial x_k} \frac{\partial \omega_l}{\partial x_k}$.

---

## 2. Rank Structure & Spectral Positivity

Because $D_s = J_{X_{s,T}}(A_s) \in SL(3, \mathbb{R})$ is almost surely invertible ($\det D_s = 1$ by incompressibility):
$$\operatorname{rank}(D_s J_\omega) = \operatorname{rank}(J_\omega).$$
Therefore, along each realization of the stochastic flow:
$$\operatorname{rank}(\Sigma_s \Sigma_s^T) = \operatorname{rank}(J_\omega(A_s, s)).$$

### Complete Spectral Taxonomy:
1. **Zero Production ($\operatorname{rank} = 0$)**:
   $$\Sigma_s \Sigma_s^T = 0 \iff J_\omega(A_s, s) = 0 \quad (\text{vorticity locally constant along path}).$$
2. **Rank-1 Production ($\operatorname{rank} = 1$)**:
   Occurs when vorticity varies along only one spatial coordinate direction (e.g. 1D shear layer profile $\omega = \omega(y) \mathbf{e}_z$). Two eigenvalues of $\Sigma \Sigma^T$ are zero.
3. **Rank-2 Production ($\operatorname{rank} = 2$)**:
   Occurs in 2D vortex dynamics where vorticity is planar-dependent ($\omega = \omega(x, y) \mathbf{e}_z$). One eigenvalue of $\Sigma \Sigma^T$ is zero.
4. **Full-Rank / Strictly Positive Definite ($\operatorname{rank} = 3, \Sigma \Sigma^T \succ 0$)**:
   Requires fully 3D non-degenerate vorticity gradients ($J_\omega$ has 3 linearly independent columns).

### Positive Semi-Definiteness vs Positive Definiteness:
- $C_s = 2\nu \int_s^T \mathbb{E}[ D_r (J_\omega J_\omega^T) D_r^T ] dr$ is **always symmetric positive semi-definite** ($C_s \succeq 0$).
- $C_s$ is **strictly positive definite** ($C_s \succ 0$) for $s < T$ if and only if the expectation $\mathbb{E}[ D_r (J_\omega J_\omega^T) D_r^T ]$ has full rank when integrated over $[s, T]$.
