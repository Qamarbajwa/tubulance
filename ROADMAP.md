# ROADMAP.md — NS-TRAJECTORY-PERSISTENCE-2

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Governance Standard:** Autonomous Project Runtime Governance Kernel v2.10.1  
**Last Updated:** 2026-08-29

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
| **TP2-G5-A0** | Landscape, Literature Boundary, Object Identity, Zero-State Taxonomy, and Research Contract | `ACCEPTED_WITH_LIMITATIONS_AND_CONTRACT_SEALED` | Xi remains the primary scale-critical relative QV density; literature collision watch, domain contract, and joint-jet open problem sealed. |
| **TP2-G5-A1** | Exact stochastic dynamics of $N$, $R$, and $\Xi$ | `AUTHORIZED_NOT_EXECUTED` | Must derive solely from `TP2_G5_A0_RESEARCH_CONTRACT.md`; no A1 work is included in A0. |

---

## 2. Active Increment

### TP2-G5-A1 Amendment (2026-08-30)

The authorized A1 increment is now complete with status ACCEPTED_WITH_LIMITATIONS.
Its exact stopped Z, R, D J_omega, N, [N,R], and Xi equations are recorded in
the TP2-G5-A1 artifacts. The active stop is TP2-G5-A2: do not execute it from
this increment.

- **Current Milestone**: `TP2-G5-A1` (`AUTHORIZED_NOT_EXECUTED`)

  - **Accepted prerequisite**: `TP2-G5-A0` (`ACCEPTED_WITH_LIMITATIONS_AND_CONTRACT_SEALED`).
  - **A1 contract**: `TP2_G5_A0_RESEARCH_CONTRACT.md`.
  - **Stop condition**: do not begin A1 within the A0 increment.
