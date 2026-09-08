# Universal Governance Minimal v4.0.3 — Negative Test Execution Report

**Project**: `tubulance` (3D Navier–Stokes Stochastic Persistence & Regularity Program)  
**Task Envelope**: `NS-GOV-MIG-V403-001`  
**Execution Date**: 2026-09-08  
**Test Suite**: `tests/test_governance_v4_migration.py`  
**Status**: `12/12 NEGATIVE TESTS PASSED` (Total suite: 25/25 passed)

---

## 1. Executive Summary

Universal Governance Minimal v4.0.3 requires fail-closed verification across 12 explicit negative test scenarios. These tests verify that invalid transitions, improper role collapsing, candidate mismatches, stale evidence, epistemic overreach, duplicate state owners, and unsafe rollbacks are machine-rejected by the runtime governance manager (`src/navier3d/governance/state_manager.py`) and math assurance engine (`src/navier3d/math_assurance/`).

All 12 negative test scenarios executed successfully and confirmed strict fail-closed rejection.

---

## 2. Negative Test Scenarios & Results Matrix

| # | Scenario Name | Target Component | Injected Fault / Invalid State | Expected Rejection | Actual Result |
|---|---|---|---|---|---|
| **01** | `test_negative_01_missing_mandatory_authority_file` | `GovernanceStateManager` | Directory missing `PROJECT_STATE.yaml` | `GovernanceStateError` ("Missing mandatory authority file") | **PASSED** (Fail-closed) |
| **02** | `test_negative_02_conflicting_governance_version` | `GovernanceStateManager` | Version declared as "3.0.0" or "4.0.2" | `GovernanceStateError` ("Conflicting governance version") | **PASSED** (Fail-closed) |
| **03** | `test_negative_03_duplicate_state_owner` | `GovernanceStateManager` | Two active files claiming `PRIMARY_LIVE_STATE` | `GovernanceStateError` ("Duplicate state owner detected") | **PASSED** (Fail-closed) |
| **04** | `test_negative_04_stale_evidence` | `GovernanceStateManager` | Evidence candidate SHA differs from active candidate | `GovernanceStateError` ("Stale evidence detected") | **PASSED** (Fail-closed) |
| **05** | `test_negative_05_candidate_changed_after_review` | `GovernanceStateManager` | Acceptance candidate SHA differs from reviewed SHA | `CandidateMismatchError` ("Candidate Mismatch") | **PASSED** (Fail-closed) |
| **06** | `test_negative_06_self_review_or_self_acceptance` | `GovernanceStateManager` | Writer acts as Reviewer or Writer acts as Acceptor | `SelfAcceptanceError` ("cannot act as...") | **PASSED** (Fail-closed) |
| **07** | `test_negative_07_unsupported_evidence_promotion` | `GovernanceStateManager` | Claiming E4/E5 under IND0 or without independent verifier | `GovernanceStateError` ("Unsupported evidence promotion") | **PASSED** (Fail-closed) |
| **08** | `test_negative_08_historical_record_rewriting` | Git History & Legacy Anchor | Attempt to overwrite or erase sealed commit `9783774` or legacy G5 candidate | Verified reachable in git log; anchor immutable | **PASSED** (Fail-closed) |
| **09** | `test_negative_09_mathematical_truth_promotion_from_technical_pass` | `GovernanceStateManager` & `PromotionManager` | Attempt to promote mathematical claim to PROVEN via test pass alone | `GovernanceStateError` ("Epistemic category error") | **PASSED** (Fail-closed) |
| **10** | `test_negative_10_invalid_independence_namespace` | `GovernanceStateManager` | Using `MATH_I` codes in governance or `IND` codes in math passports | `GovernanceStateError` ("Invalid namespace in...") | **PASSED** (Fail-closed) |
| **11** | `test_negative_11_unresolved_target_accidentally_marked_solved` | `GovernanceStateManager` | Setting `clay_statement_b_status` to "SOLVED" or "RESOLVED" | `GovernanceStateError` ("Epistemic invariant violation") | **PASSED** (Fail-closed) |
| **12** | `test_negative_12_rollback_deleting_pre_migration_state` | `GovernanceStateManager` | Rollback list includes pre-existing scientific state file (`CLAIM_REGISTRY.yaml`) | `GovernanceStateError` ("Rollback safety violation") | **PASSED** (Fail-closed) |

---

## 3. Epistemic and Governance Invariants Enforced

1. **Epistemic Category Discipline**:
   Passing unit tests, verifiers, or linters cannot alter the mathematical truth status of any registered claim. Only human-reviewed and audited analytic proof passports under MRC v1.0.1 can advance claim lifecycle stages.
2. **Anti-Self-Acceptance**:
   The primary author/writer agent (`antigravity-primary-agent`) is machine-prohibited from issuing reviews or acceptance decisions for its own work.
3. **Immutability of Historical Scientific Baselines**:
   Historical records, sealed manifests, negative evidence ledgers, and accepted checkpoint commits (including `TP2-G6-B-R1` at `9783774430cd3939d473cd0e833aa2cf5b5c0645`) are protected from deletion or mutation by rollback or migration operations.
4. **Target Problem Permanence**:
   Clay Millennium Prize Problem Statement B remains strictly `UNRESOLVED`. Any attempt to set it to solved within governance state files aborts immediately.
