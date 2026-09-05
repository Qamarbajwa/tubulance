# ROADMAP.md — NS-TRAJECTORY-PERSISTENCE-2

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 (active) with v2.10.1 preserved historically; Mathematical Research Constitution v1.0.1 remains active
**Last Updated:** 2026-09-01

---

## 1. Roadmap Milestones & Canonical Status

| Milestone | Title | Status | Primary Output / Result |
|---|---|---|---|
| **TP2-G1** | Forward/Backward Gradient Conventions | `ACCEPTED_CANONICAL` | Frozen Convention M $[J_f]_{ij} = \partial_j f_i$. |

## TP2-G5-A3 Bounded Checkpoint (2026-08-30)

`TP2-G5-A3` is `ACCEPTED_CANONICAL_WITH_LIMITATIONS` within the validated v3.0.0 envelope. The exact amplitude/direction identities, deformation-metric split, Gamma form, and conditional condition-number envelope are recorded and tested. Literature bridges are conservative no-direct-transfer results; `TH9-R` is partially reused for diagnostics only. `E_mu[Xi]` remains distinct from Eulerian spatial averages, and `Clay Statement B` remains `UNRESOLVED`.

`TP2-G5-A4` is the active successor under a new candidate-bound envelope. It is authorized only for conditional hypothetical-singularity scenario analysis; `TP2-G5-A5` remains forbidden by the A4 envelope.
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
| **TP2-G5-A5** | Whole-G5 Campaign Synthesis and Open-Bridge Map | `ACCEPTED_WITH_LIMITATIONS` | Canonical synthesis of accepted A0-A4 evidence; no new theorem or Clay resolution. |
| **TP2-G6-B-R1** | Rigid-Branch Adversarial Attack | `ACCEPTED_AS_CANONICAL_BOUNDED_INCREMENT` | Definition hardened; parabolic invariance $J_\lambda \equiv J_0$; maximal covariance rank deficiency; verdict: `RIGID_SIGNATURE_PARTIALLY_REALIZED`. |
| **TP2-G6-B-R2** | Scientific Claim Audit and Repair | `ACCEPTED_AS_CANONICAL_CORRECTIVE_INCREMENT` | Lattice-compatible scaling theorem (CLM-031); Beltrami stretching qualified; Branch-R semantics disambiguated (R-A); gradient injection downgraded. |

---

## 2. Active Increment

### TP2-G5-A1 Amendment (2026-08-30)

The authorized A1 increment is now complete with status ACCEPTED_WITH_LIMITATIONS.
Its exact stopped Z, R, D J_omega, N, [N,R], and Xi equations are recorded in
the TP2-G5-A1 artifacts. The active stop is TP2-G5-A2: do not execute it from
this increment.

### TP2-G5-A2 Amendment (2026-08-30)

TP2-G5-A2 is complete with status ACCEPTED_WITH_LIMITATIONS. The exact Xi
drift factorization, Riccati origin, nonnegative Ito compensation, geometry
sign audit, pressure-entry audit, and weighted-measure non-closure are sealed
in the A2 artifacts. TP2-G5-A3 is not executed or authorized by this increment.

- **Current Milestone**: `TP2-G5-A1` (`AUTHORIZED_NOT_EXECUTED`)

  - **Accepted prerequisite**: `TP2-G5-A0` (`ACCEPTED_WITH_LIMITATIONS_AND_CONTRACT_SEALED`).
  - **A1 contract**: `TP2_G5_A0_RESEARCH_CONTRACT.md`.
  - **Stop condition**: do not begin A1 within the A0 increment.

### v3 Migration Direction Amendment (2026-08-30)

The preceding A1 line and A2 stop wording are preserved as historical increment records. The current scientific state is `TP2-G5-A2 = ACCEPTED_WITH_LIMITATIONS`; the expected descendant remains `TP2-G5-A3`. A3 is not executed by the governance migration. Under v3, A3 requires a new candidate-bound Task Execution Envelope and eligibility evidence; its exact objective is `NOT_VERIFIED` in the current repository state, so no A3 envelope is authorized by this migration commit.

Governance migration status is operationally separate from scientific progress, mathematical truth, release eligibility, publication readiness, deployment authorization, community acceptance, and Clay Statement B, which remains `UNRESOLVED`.

### TP2-G5-A4 Amendment (2026-08-31)

`TP2-G5-A4` is the current bounded increment under `governance/task_envelopes/TP2-G5-A4.yaml`, with `RISK=T3`, `ACTION=B`, and base candidate `d55b495e91617a58262e2959529c9eb202fffbc8` verified against `origin/main`. The accepted candidate is the exact `J_n=-log chi_n` / relative-variance identity and the compactified-subsequence stochastic-history dichotomy. Rigid and decoherent branches are only partially constrained; both remain open. No bridge to spatial direction coherence, sparseness, analyticity, isotropy, or regularity is promoted. Stop after A4; do not execute A5.

### TP2-G5-A5 Amendment (2026-09-01)

`TP2-G5-A5` is complete under `governance/task_envelopes/TP2-G5-A5.yaml`. It synthesizes accepted A0-A4 evidence into a candidate-bound claim/evidence matrix, load-bearing result map, obstruction ledger, and open-bridge statement. The result is `ACCEPTED_WITH_LIMITATIONS`: both A4 branches remain open, `Clay Statement B` remains `UNRESOLVED`, and no release, publication, or deployment status changes. Stop after A5; no A6 or successor mathematical increment is executed.

### TP2-G6-B-R1 Amendment (2026-09-05)

`TP2-G6-B-R1` is complete under `governance/task_envelopes/TP2-G6-B-R1.yaml`. It executes an adversarial attack on the Rigid Branch (Branch R). The mathematical definition of Branch R is hardened, parabolic rescaling invariance $J_\lambda(a) \equiv J_0(a)$ is proved (`CLM-028`), and maximal covariance rank deficiency is established for periodic shear (`CLM-029`). The verdict is `RIGID_SIGNATURE_PARTIALLY_REALIZED`: Branch R is smoothly realized without vortex stretching, but active stretching injects vorticity gradients via $T = (\nabla S)\omega$, obstructing $J_n(a) \to 0$ on viscous scales. Clay Statement B remains `UNRESOLVED`. Stop after R1.

### TP2-G6-B-R2 Amendment (2026-09-06)

`TP2-G6-B-R2` is complete under `governance/task_envelopes/TP2-G6-B-R2.yaml`. It conducts a fail-closed scientific re-audit of R1 across 7 questions. `CLM-028` is domain-qualified and superseded by `CLM-031` (lattice-compatible $\lambda \in \mathbb{N}$ on fixed $\mathbb{T}^3$). Beltrami stretching is qualified for constant-speed modes ($\omega \cdot S \omega \equiv 0$). Branch-R semantics are disambiguated: R1 proved only Regime R-A (initial data families), while singular continuation R-C remains `OPEN`. `NS-NEG-014` is downgraded from proved obstruction to `OPEN_CONDITIONAL_SCALING_HYPOTHESIS`. `CLM-029` (rank-1 covariance) is retained. `CLM-030` is superseded by `CLM-032`. Clay Statement B remains strictly `UNRESOLVED`. Stop after R2.


