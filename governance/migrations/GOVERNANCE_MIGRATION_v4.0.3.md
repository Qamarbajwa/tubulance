# Governance Migration Record: v3.0.0 to v4.0.3
## NS-GOV-MIG-V403-001

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Project ID:** `tubulance`  
**Date:** `2026-09-07`  
**Migration Mode:** `MIGRATION_GOVERNED`  
**Previous Governance:** Universal Autonomous Project Governance v3.0.0  
**New Governance:** Universal Governance Minimal v4.0.3  
**Constitutional Standard:** Mathematical Research Constitution v1.0.1 (Unchanged and Preserved)  
**Target Status:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ remains strictly `UNRESOLVED`  

---

## 1. Migration Purpose & Preimages

This migration upgrades the operational runtime governance of the `tubulance` repository to Universal Governance Minimal v4.0.3. The upgrade streamlines operational entry into three authoritative entry points while reinforcing state serialization, lean governance budgeting, and explicit anti-self-acceptance.

### 1.1 Source Distribution
- **Distribution Package:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`
- **Archived Staging Location:** `governance/packet/v4.0.3/`
- **Package Integrity:** Verified via `tools/verify-package.mjs` (8/8 files matching `MANIFEST.sha256.json`).

### 1.2 Retained Preimages & Invariants
- `mathematical_constitution/MATHEMATICAL_RESEARCH_CONSTITUTION.md` (v1.0.1): Preserved unchanged.
- `mathematical_constitution/CLAIM_REGISTRY.yaml`: 33 registered claims (`CLM-001` through `CLM-033`) preserved with 100% census pass.
- `mathematical_constitution/CLAIM_DEPENDENCY_GRAPH.yaml`: 34 nodes, 72 edges, 0 cycles.
- `research_memory/RESEARCH_OBSTRUCTION_REGISTRY.yaml`: 17 structural obstructions (`NS-OBS-001` through `NS-OBS-017`) preserved.
- `research_memory/NEGATIVE_EVIDENCE_LEDGER.yaml`: 36 permanent negative evidence records (`NEG-EV-001` through `NEG-EV-036`) preserved.
- Previous baseline candidate: `aa24fbdf251645b70338503a1f361715d942d38f` (closure of `TP2-G6-A1`).

---

## 2. Operational Entry Point Mapping

| Role | Legacy v3.0.0 Location | v4.0.3 Canonical Authority | Operational Meaning |
|---|---|---|---|
| **HOW** | `governance/packet/v3.0.0/02_RUNTIME_GOVERNANCE_KERNEL_v3.0.0.md` | `governance/GOVERNANCE.md` | Universal operating rules + Section 13 project binding. |
| **WHAT / WHY** | `PROJECT_INTENT.md`, `ROADMAP.md` | `governance/PROJECT_DIRECTION.md` | Project intent, architecture, delegated source map, contracts. |
| **LIVE STATUS** | Root `GOVERNANCE_STATE.yaml` | `governance/PROJECT_STATE.yaml` | Live machine state, revision tracking, hard gates, active candidate. |

---

## 3. Consequence & Evidence Vocabulary Mapping

| v3.0.0 Risk Tier | v4.0.3 Risk Class | Minimum Evidence Required in tubulance |
|---|---|---|
| T1 (Trivial) | **R0** | Inspection / targeted lint check; self-checked. |
| T2 (Standard) | **R1** | Automated test suite execution (`pytest`). |
| T3 (Consequential) | **R2** | Automated tests + candidate-bound execution trace. |
| T4 (Foundational) | **R3** | Automated tests + candidate execution + independent verification (`IND1`/`MATH_I2`). |
| T5 (Reserved) | **R3 + Reserved** | Strictly prohibited for autonomous agents without explicit owner instruction. |

Evidence dimension mapping:
- Historical evidence labels (`GOV_E1` through `GOV_E5`, `MATH_E1` through `MATH_E5`) remain fully valid in historical receipts.
- New operational receipts under v4.0.3 use the versioned schema defined in `EVIDENCE_AND_MIGRATION.md` (E1: Inspection, E2: Automated Tests, E3: Candidate Execution, E4: Independent Verification, E5: External Anchor).

---

## 4. State Concurrency & Revision Checking

Universal Governance Minimal v4.0.3 introduces explicit revision serialization:
- Every update to `governance/PROJECT_STATE.yaml` increments the integer field `revision: N -> N+1`.
- A writer must read the expected revision, make modifications, and verify that the target revision has not diverged.
- Stale writes against an out-of-date revision fail closed.

---

## 5. Rollback Procedure

In the event of an unexpected post-cutover failure:
1. Revert `governance/GOVERNANCE.md`, `governance/PROJECT_DIRECTION.md`, and `governance/PROJECT_STATE.yaml`.
2. Restore root `GOVERNANCE_STATE.yaml` schema version to `3.0.0`.
3. Sealed historical receipts and mathematical constitution files remain untouched.
