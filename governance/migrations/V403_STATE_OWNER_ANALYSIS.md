# State Ownership and Mutation Control Analysis: Universal Governance Minimal v4.0.3

**Project ID:** `tubulance`  
**Standard:** Universal Governance Minimal v4.0.3 (Section 9 & 11)  
**Date:** `2026-09-08`  

---

## 1. Canonical State Ownership

Under Universal Governance Minimal v4.0.3, the single canonical source of truth for live project state is:
```
governance/PROJECT_STATE.yaml
```
- The legacy project-root file `GOVERNANCE_STATE.yaml` functions strictly as a backward-compatible pointer and transition bridge.
- All live status mutations, objective selections, candidate bindings, and gate verifications must be executed against `governance/PROJECT_STATE.yaml`.

---

## 2. Serialized Mutation & Concurrency Controls

State mutation is protected by machine-enforced concurrency control in `src/navier3d/governance/state_manager.py`:

1. **Monotonic Revision Compare-and-Swap:**
   - The state file contains an integer field: `revision: N`.
   - Every mutation requires supplying `expected_revision == N`.
   - The manager validates that the file has not been modified concurrently.
   - Upon successful write, the revision is atomically incremented to `N + 1`, and `coordination.last_updated_at` is updated to the current UTC timestamp.
   - Any attempt to write with a stale revision raises `StaleRevisionError` and fails closed.
2. **Single State Coordinator:**
   - Only the designated coordinator role (`antigravity-primary-agent` during execution, Autonomous Project Governance Coordinator during acceptance) can commit state changes.
   - Competing agents or autonomous background tasks cannot independently overwrite state.

---

## 3. Separation of Review, Acceptance, and Candidate Freeze

1. **Candidate Freeze Before Review:**
   - Before independent review begins, the candidate Git commit SHA must be frozen.
   - If any file within the candidate scope is modified, the candidate SHA changes, immediately invalidating any prior review evidence.
2. **Strict Anti-Self-Acceptance:**
   - `src/navier3d/governance/state_manager.py` enforces:
     - `writer != reviewer` (enforced via `SelfAcceptanceError`)
     - `writer != acceptor` (enforced via `SelfAcceptanceError`)
   - The implementation author cannot review or accept its own work.
3. **Rejection Persistence:**
   - A rejected migration or candidate remains strictly `REJECTED` or `BLOCKED` until a new candidate SHA is generated and fresh independent review is produced.
