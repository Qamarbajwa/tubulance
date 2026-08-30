# ARCHITECTURE_DECISIONS.md — NS-TRAJECTORY-PERSISTENCE-2

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0, with v2.10.1 preserved as historical governance and Mathematical Research Constitution v1.0.1 active as the domain epistemic layer
**Last Updated:** 2026-08-30

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

### ADR-005: Governed Migration Layout
- **Decision**: Keep the historical `governanace/` directory and v2.10.1 artifacts unchanged. Use `governance/packet/v3.0.0/` for an exact v3 packet copy, `governance/task_envelopes/` for v3 envelopes, and `governance/migrations/` for migration-preservation records. Keep the active v3 state at root `GOVERNANCE_STATE.yaml` for continuity with existing tooling.
- **Rationale**: This is the least disruptive layout that preserves historical provenance, avoids duplicate active state, and supports candidate-bound v3 verification.

### ADR-006: Mathematical/Operational Governance Separation
- **Decision**: v3 governs project binding, authority, task execution, evidence, release/distribution state, and conformance. Mathematical Research Constitution v1.0.1 continues to govern mathematical truth, claim typing, assumption drift, novelty, significance, understanding, dependency closure, and `SOLVED_ELIGIBLE` restrictions.
- **Rationale**: Technical acceptance, mathematical truth, project canonical status, publication readiness, community acceptance, and Clay solution status are non-substitutable.
