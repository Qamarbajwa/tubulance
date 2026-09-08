# Project Direction — NS-TRAJECTORY-PERSISTENCE-2

**Governance Version:** `Universal Governance Minimal v4.0.3`  
**Project ID:** `tubulance`  
**Program Name:** `3D Navier-Stokes Stochastic Persistence & Regularity Program`  
**Status:** `ACTIVE`  

---

## 1. Intent and Boundaries

> **The purpose of this project is not to maximize candidate proofs, successful experiments, theorem counts, or AI agreement. The purpose is to maximize reliable, novel, explainable, reproducible, cumulative mathematical understanding while preserving uncertainty, negative evidence, and abandoned research pathways.**

### 1.1 Target Problem
- **Problem Statement:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$ with $\nu > 0$ and $f = 0$.
- **Target Status:** Strictly **`UNRESOLVED`**.
- **Scope Limit:** Project work investigates whether stochastic Lagrangian Cauchy representations (Constantin–Iyer 2008, Eyink 2009) and finite-time trajectory persistence provide a rigorous mechanism for global regularity, or whether exact flow structures exhibit insurmountable analytical obstructions.
- **Release & Deployment Boundary:** This repository is an open-science pure mathematical research program, NOT a commercial product release candidate. Release state is strictly maintained as **`NO-GO`**.

---

## 2. Delegated Source Map

Narrowly delegated technical sources retain their specialized authority and must not be rewritten or duplicated:

| Source Path | Delegated Technical Role | Authoritative Version / Status | Conflict / Supersession Rule |
|---|---|---|---|
| `mathematical_constitution/MATHEMATICAL_RESEARCH_CONSTITUTION.md` | Supreme mathematical research constitution and assurance standard | v1.0.1 | Outranks all heuristic or informal claims. |
| `mathematical_constitution/CLAIM_REGISTRY.yaml` | Canonical ledger of mathematical claims and 12-dimensional passports | 33 registered claims (`CLM-001` to `CLM-033`) | Only claims with complete valid passports are canonical. |
| `mathematical_constitution/CLAIM_DEPENDENCY_GRAPH.yaml` | Claim dependency DAG (cycle detection and provenance) | 34 nodes, 72 edges, 0 cycles | Circular reasoning is strictly prohibited. |
| `research_memory/RESEARCH_OBSTRUCTION_REGISTRY.yaml` | Permanent catalog of proved mathematical obstructions | 17 obstructions (`NS-OBS-001` to `NS-OBS-017`) | Obstructions cannot be erased by governance changes. |
| `research_memory/NEGATIVE_EVIDENCE_LEDGER.yaml` | Permanent negative evidence ledger | 36 records (`NEG-EV-001` to `NEG-EV-036`) | Falsified hypotheses remain permanent scientific truth. |
| `CURRENT_SCIENTIFIC_STATE.md` | Comprehensive scientific narrative and historical audit record | Current at `aa24fbd` | Describes active mathematical state across gates G1–G6. |
| `ROADMAP.md` | Execution roadmap and sequencing of program milestones | Active gate: `TP2-G6` | Governs execution order; next target is `TP2-G6-A2`. |
| `ARCHITECTURE_DECISIONS.md` | Technical and computational architecture records | Preserved | Governs solver architecture, indexing, and memory. |

---

## 3. Capability Contracts and Actors

### 3.1 Actors
- **Primary Research Agent (`antigravity-primary-agent`):** Implementation role (analytical derivations, test scripts, numerical solvers).
- **Independent Verifier (`antigravity-fresh-context-verifier`):** Verification role (`IND1`/`IND2`, `MATH_I2`). Audits claims, replicates evidence, validates circularity firewalls.
- **Project Coordinator:** Acceptance role. Confirms pass/fail gates and coordinates state updates.

### 3.2 Scientific Research Capabilities
1. **`CAP-NS-ANALYTICS` (Analytical Derivations & Asymptotics):**
   - Exact PDEs and identities on $\mathbb{T}^3$.
   - Scale-critical estimates and Calderón–Zygmund singular integral bounds.
   - Requirement: Dimensionally consistent exponents under parabolic scaling ($[x]=-1, [t]=-2, [u]=1, [\omega]=2, [Q]=6$).
2. **`CAP-NS-STOCHASTIC` (Forwardized Lagrangian Martingales):**
   - Stochastic flow $d X_t = u(X_t, t)dt + \sqrt{2\nu} d W_t$ and Cauchy representation $\chi_s$.
   - Push-forward measure $\mu_s$ and pathwise deformation metric $\Xi_s$.
3. **`CAP-NS-ASSURANCE` (Mathematical Assurance Engine):**
   - Automated census of claim passports, DAG cycle detection, understanding and novelty validation (`src/navier3d/math_assurance/`).

---

## 4. System Architecture & Integrations

```
┌─────────────────────────────────────────────────────────────┐
│                 PROJECT GOVERNANCE (HOW)                    │
│      Universal Governance Minimal v4.0.3 (GOVERNANCE.md)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             MATHEMATICAL RESEARCH CONSTITUTION              │
│        MRC v1.0.1 (MATHEMATICAL_RESEARCH_CONSTITUTION.md)    │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│     CLAIM PASSPORT DAG       │ │    RESEARCH MEMORY &        │
│   33 claims / 0 cycles       │ │    NEGATIVE EVIDENCE        │
│  (CLAIM_REGISTRY.yaml)       │ │  (17 OBS / 36 NEG-EV)       │
└──────────────┬───────────────┘ └─────────────┬───────────────┘
               │                               │
               ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│              COMPUTATIONAL & ANALYTICAL CODE                │
│       Solvers (navier3d) | Tests (pytest) | Verifiers       │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Active Roadmap & Milestones

- **Current Program:** `NS-TRAJECTORY-PERSISTENCE-2`
- **Active Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`
  - `B1`: Non-Circular $\Xi$ Control
  - `B2`: Stochastic History $\mu_s$ to Eulerian Spatial Volume Measure $dx$
  - `B3`: Covariance Spectrum & Multidirectional 3D Dispersion
  - `B4`: Target-Equivalent Continuation Criterion matching Clay Statement B
- **Completed Milestone:** `TP2-G6-A1` (Pressure–Strain Phase Coupling, Poisson Balance, Calderón–Zygmund Limits; closed at commit `aa24fbd`).
- **Next Authorized Increment:** `TP2-G6-A2` (Scale-Critical Transport, Parabolic Regularity Envelopes, and Stochastic Push-Forward Measure Bounds targeting Bridge $B_2$).
