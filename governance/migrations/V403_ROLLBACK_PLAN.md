# Universal Governance Minimal v4.0.3 — Rollback Plan

**Project**: `tubulance` (3D Navier–Stokes Stochastic Persistence & Regularity Program)  
**Document Identifier**: `NS-GOV-MIG-V403-001-ROLLBACK`  
**Applicability**: Emergency reversal of governance migration increment `NS-GOV-MIG-V403-001`  
**Base Reversion Target SHA**: `aa24fbdf251645b70338503a1f361715d942d38f` (Closure of `TP2-G6-A1`)  
**Strict Safety Constraints**: Machine-enforced by `GovernanceStateManager.validate_rollback_scope()`

---

## 1. Rollback Preconditions and Triggers

Rollback of `NS-GOV-MIG-V403-001` is authorized ONLY if:
1. An unresolvable circular dependency or fatal failure is discovered in the v4.0.3 state serialization or governance files that prevents authorized scientific execution.
2. The owner explicitly commands rollback to Universal Autonomous Project Governance v3.0.0.

---

## 2. Inviolable Rollback Scope Boundaries

The rollback procedure is strictly bounded to prevent data loss or contamination of historical mathematical evidence:

### Allowed Rollback Targets (Migration-Owned Files Only):
- `governance/GOVERNANCE.md`
- `governance/PROJECT_DIRECTION.md`
- `governance/PROJECT_STATE.yaml`
- `governance/authority_compatibility_v4.0.3.md`
- `governance/evidence_compatibility_v4.0.3.md`
- `governance/task_envelopes/NS-GOV-MIG-V403-001.yaml`
- `governance/migrations/` (all migration reports)
- `governance/packet/` (staged package)
- `governance/evidence/NS-GOV-MIG-V403-001-*` (migration evidence)
- `src/navier3d/governance/`
- `tests/test_governance_v4_migration.py`

### Machine-Prohibited Rollback Targets (Must NOT be Reverted or Deleted):
- `mathematical_constitution/` (MRC v1.0.1, CLAIM_REGISTRY.yaml, CLAIM_DEPENDENCY_GRAPH.yaml)
- `research_memory/` (RESEARCH_OBSTRUCTION_REGISTRY.yaml, NEGATIVE_EVIDENCE_LEDGER.yaml)
- `CURRENT_SCIENTIFIC_STATE.md` (scientific findings, CLM-001 through CLM-033)
- `TP2_G6_A1_*` (accepted canonical milestone files)
- `TP2_G6_B_R1_*` (sealed historical files at commit `9783774430cd3939d473cd0e833aa2cf5b5c0645`)
- Historical test suites (`tests/test_tp2_*.py`, `tests/test_math_assurance_*.py`)

Any rollback script or command attempting to touch or delete files outside the allowed migration-owned set will trigger `GovernanceStateError: Rollback safety violation` via `GovernanceStateManager.validate_rollback_scope()`.

---

## 3. Step-by-Step Rollback Procedure

If emergency rollback is commanded:

1. **Verify Working Tree Cleanliness**:
   ```bash
   git status --short
   ```
2. **Execute Scoped Git Revert**:
   Create a single non-destructive revert commit that removes or restores only migration-owned files back to their state at `aa24fbdf251645b70338503a1f361715d942d38f`.
   ```bash
   git checkout aa24fbdf251645b70338503a1f361715d942d38f -- GOVERNANCE_STATE.yaml
   git rm -r governance/GOVERNANCE.md governance/PROJECT_DIRECTION.md governance/PROJECT_STATE.yaml governance/packet/ governance/migrations/ governance/evidence/NS-GOV-MIG-V403-001* src/navier3d/governance/ tests/test_governance_v4_migration.py
   ```
3. **Preserve External Intake**:
   Ensure `research_memory/EXTERNAL_EVIDENCE_INTAKE_20260908_ABCMZ.md` and entry `EXT-004` in `mathematical_constitution/EXTERNAL_VALIDATION_LEDGER.yaml` remain intact (intake records are independent of governance runtime version).
4. **Verify Restored v3.0.0 State**:
   Run full test suite:
   ```bash
   python -m pytest -k "tp2 or math_assurance" -q
   ```
5. **Commit Rollback with Explicit Bounded Message**:
   ```bash
   git commit -m "revert(governance): rollback NS-GOV-MIG-V403-001 to v3.0.0 runtime baseline"
   git push origin main
   ```
