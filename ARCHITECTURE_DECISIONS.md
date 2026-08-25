# ARCHITECTURE_DECISIONS.md — NS-TRAJECTORY-PERSISTENCE-2

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Governance Standard:** Autonomous Project Runtime Governance Kernel v2.10.1  
**Last Updated:** 2026-08-25  

---

## 1. Architectural Decision Records (ADRs)

### ADR-001: Convention M Standardization
- **Decision**: $[J_f]_{ij} := \partial_j f_i$. $A = J_u$, $G = J_\omega$, $B = J_A = \nabla_x A$, $D = B^{-1}$.
- **Rationale**: Eliminates transpose confusion across forward and backward Cauchy operators.

### ADR-002: Separation of Eulerian Strain and Lagrangian Deformation Frames
- **Decision**: $S(x, t)$ (instantaneous Eulerian strain) and $\Gamma_s = D_s^T D_s$ (finite-time Lagrangian deformation) are strictly distinct tensors coupled via the doubly stochastic matrix $R_{ij} = |v_i \cdot e_j|^2$.
- **Rationale**: Pressure Hessian acts directly on $\dot{e}_i$, but only indirectly on $v_i$.

### ADR-003: Stochastic Semimartingale Orientation Framework
- **Decision**: The orientation observables $H = G G^T, q_i = \operatorname{tr}(P_i H), p_i = q_i/h$ are governed by backward Itô SDEs driven by spatial diffusion noise, not deterministic ODEs.
- **Rationale**: Brownian path variation $\sqrt{2\nu} \sum_\ell (\partial_\ell H) \widehat{d}W^\ell$ is strictly non-vanishing in spatially inhomogeneous flows.

### ADR-004: Parabolic Scaling Normalization
- **Decision**: All comparative rates must be normalized to match velocity gradient dimension $\lambda^2$, via $R_Q(s) = \frac{Q_s}{S_s} = \partial_s \ln \chi_s$.
- **Rationale**: $Q_s$ ($\lambda^6$) and $\|D\|^2$ ($\lambda^0$) are scaling-incompatible (`NS-OBS-009`).
