# ROADMAP.md — NS-TRAJECTORY-PERSISTENCE-2

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Governance Standard:** Autonomous Project Runtime Governance Kernel v2.10.1  
**Last Updated:** 2026-08-25  

---

## 1. Roadmap Milestones & Canonical Status

| Milestone | Title | Status | Primary Output / Result |
|---|---|---|---|
| **TP2-G1** | Forward/Backward Gradient Conventions | `ACCEPTED_CANONICAL` | Frozen Convention M $[J_f]_{ij} = \partial_j f_i$. |
| **TP2-G2** | Stochastic Lagrangian Cauchy Invariants | `ACCEPTED_CANONICAL` | Martingale representation $Z_s = D_s \omega(A_s)$. |
| **TP2-G1R** | Gradient Convention Reconciliation | `ACCEPTED_CANONICAL` | Resolved transpose discrepancy $D = (\nabla_x A)^{-1}$. |
| **TP2-G3** | Stochastic Cauchy Covariance Evolution | `ACCEPTED_CANONICAL_WITH_LIMITATIONS` | Covariance tensor $C_s$, trace variance $V_s$, strict $Q_s > 0$. |
| **NS-RPM-1** | Research Pathway Memory & Similarity | `ACCEPTED / VERIFIED` | Full `research_memory/` infrastructure operational. |
| **TP2-G4-A1** | Adversarial Analysis & Dimensional Incoherence | `ACCEPTED_CANONICAL_WITH_REFORMULATION` | Closed blind $Q \ge F(\|D\|)$ (`NS-OBS-009`); proved shear decoupling. |
| **TP2-G4-A2** | Tensor Dynamics & Frame Decoupling | `ACCEPTED_CANONICAL_WITH_REFORMULATION` | Derived $(D_t - \nu \Delta)G = SG - GA + T$; decoupled strain vs deformation frame. |
| **TP2-G4-A2-R1** | Degeneracy & Stochastic Orientation Correction | `ACCEPTED_CANONICAL_WITH_CORRECTIONS` | Global $q_i = \operatorname{tr}(P_i H)$; backward Itô SDEs; persistence definitions. |
| **TP2-G4-A3** | Stochastic Orientation Persistence No-Go & Relative QV Efficiency | `READY_FOR_EXECUTION` | Occupation limit proof; exit-time no-go; relative efficiency $\Theta$; $R_Q$ rate decomposition. |
| **TP2-G4-A4** | Vorticity-Relevant Amplification Bounds | `PLANNED` | Investigating $\mathcal{A}_\omega = |D\omega|^2/|\omega|^2$ and $\Theta$ dynamics. |

---

## 2. Active Increment

- **Current Milestone**: `TP2-G4-A3`
