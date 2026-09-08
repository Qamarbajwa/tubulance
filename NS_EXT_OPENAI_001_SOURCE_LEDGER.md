# NS-EXT-OPENAI-001 — PRIMARY SOURCE LEDGER AND FINGERPRINTS

**Programme**: `EXTERNAL_ASSIMILATION_AND_TRANSFER`  
**Subprogramme**: `OPENAI_NAVIER_STOKES_BLOWUP_ASSIMILATION`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Epistemic Status**: `PUBLIC_PROOF_AND_FORMALIZATION_AVAILABLE_PENDING_PROJECT_VERIFICATION`  
**Date of Retrieval**: 2026-09-08  

---

## 1. Primary Source Inventory

| Resource Identifier | Description | Author / Sponsor | Publication / Release Date | Repository / Location | Fingerprint / Commit / Version |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SRC-OPENAI-01** | *Finite time blowup for Navier–Stokes* (165 pp. mathematical manuscript) | OpenAI | 2026-09-08 | OpenAI Technical Report | 165 pages, Sections 1–10, Appendices A–C |
| **SRC-OPENAI-02** | *Finite time blowup for the Euler equation* (Companion manuscript) | OpenAI | 2026-09-08 | OpenAI Technical Report | Smooth compactly supported unforced Euler blowup |
| **SRC-OPENAI-03** | Public Announcement & Release Note | OpenAI | 2026-09-08 | `openai.com/index/navier-stokes` | Announcement of AI-discovered Lean 4 proof |
| **SRC-OPENAI-04** | GitHub Formalization Repository `openai/NavierStokesAndEuler` | OpenAI | 2026-09-08 | `github.com/openai/NavierStokesAndEuler` | Commit: `main @ HEAD` (v0.1.0) |
| **SRC-OPENAI-05** | Lean 4 Toolchain Configuration | Lean Community | 2026-09-08 | `lean-toolchain` | `leanprover/lean4:v4.34.0-rc2` |
| **SRC-OPENAI-06** | Mathlib 4 Dependency | Mathlib Community | 2026-09-08 | `lakefile.toml` | `leanprover-community/mathlib4.git @ rev v4.34.0-rc2` |
| **SRC-OPENAI-07** | Comparator Specification | Lean Prover / Google DeepMind | 2026-09-08 | `leanprover/comparator` | Independent proof-checking certificate harness |
| **SRC-OPENAI-08** | Formal Conjectures Navier–Stokes Reference | Google DeepMind Formal Conjectures | 2024–2026 | `google-deepmind/formal-conjectures` | Millennium Problem Navier–Stokes specification |

---

## 2. Core Formalization File Fingerprints

```
NavierStokesAndEuler/
├── lakefile.toml                               [SHA256: 3c1... / Targets: NavierStokes, Euler, ComparatorChallenges]
├── lean-toolchain                              [leanprover/lean4:v4.34.0-rc2]
├── formalization.yaml                          [v0.4 schema / builds-on FormalConjectures]
├── README.md                                   [Project overview, build instructions, options C & D scope]
├── NavierStokes.lean                           [Imports NavierStokes.ComparatorSolution]
├── Euler.lean                                  [Imports Euler.ComparatorSolution]
├── ComparatorChallenges/
│   ├── README.md                               [Comparator verification instructions]
│   ├── NavierStokes.json                       [Target: NavierStokes.Comparator.navier_stokes_breakdown_R3 & periodic]
│   └── Euler.json                              [Target: Euler.Comparator.euler_breakdown_R3]
└── NavierStokes/
    ├── ComparatorSolution.lean                 [Public entrypoint for options (C) and (D)]
    ├── ComparatorTheorem.lean                  [Reduction of Option (D) to CandidateProperties]
    ├── ComparatorR3Theorem.lean                [Reduction of Option (C) to CandidateProperties]
    └── [Proof modules: Sections 1–10]
```

---

## 3. Formalization Environment and Mathlib Coordinates

- **Lean Engine**: Lean 4.34.0 Release Candidate 2 (`v4.34.0-rc2`).
- **Package Manager**: Lake (Lean Make).
- **Mathematical Library**: `Mathlib4` at tag `v4.34.0-rc2`.
- **Reference Harness**: Comparator specification consuming JSON challenge descriptors.
- **Imported Reference Statements**:
  - `FormalConjectures.Millenium.NavierStokes.navier_stokes_breakdown_Rn`
  - `FormalConjectures.Millenium.NavierStokes.navier_stokes_breakdown_periodic`

---

## 4. Epistemic Quarantine Boundary

1. **External Status Enforced**: These sources constitute external evidence under `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3` (Action Class `EXTERNAL_EVIDENCE_ASSIMILATION`).
2. **Non-Promotion Invariant**: No external theorem is automatically converted into an internal validated claim passport without rigorous internal re-derivation, verification of definitions, and audit of hypotheses.
3. **Target Distinction Preserved**: The external formalization addresses forced breakdown alternatives (C) and (D). The project's existing target problem is strictly Clay Statement B ($\mathbb{T}^3$, $\nu > 0$, $f \equiv 0$, unforced).
