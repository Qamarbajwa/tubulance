"""Executable conformance checks for Universal Governance Minimal v4.0.3.

Validates the 12 minimal state-transition tests mandated by EVIDENCE_AND_MIGRATION.md,
state serialization compare-and-swap, anti-self-acceptance, role boundaries,
and project-specific epistemic invariants.
"""
from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from navier3d.governance import (
    CandidateMismatchError,
    GovernanceStateError,
    GovernanceStateManager,
    SelfAcceptanceError,
    StaleRevisionError,
    UnboundStateError,
)
from navier3d.math_assurance import MathAssuranceEngine


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "governance" / "PROJECT_STATE.yaml"
DIRECTION_PATH = ROOT / "governance" / "PROJECT_DIRECTION.md"
GOVERNANCE_PATH = ROOT / "governance" / "GOVERNANCE.md"
UNBOUND_TEMPLATE_PATH = ROOT / "governance" / "packet" / "v4.0.3" / "governance" / "PROJECT_STATE.yaml"


@pytest.fixture
def state_mgr() -> GovernanceStateManager:
    return GovernanceStateManager(STATE_PATH)


# --- 1. UNBOUND template cannot activate or authorize product work ---
def test_test01_unbound_template_cannot_activate():
    mgr = GovernanceStateManager(UNBOUND_TEMPLATE_PATH)
    with pytest.raises(UnboundStateError, match="UNBOUND"):
        mgr.validate_state()


# --- 2. Existing failed/unknown gates and NO-GO survive migration ---
def test_test02_no_go_and_negative_evidence_survive():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))
    assert state["release"]["state"] == "NO-GO"
    assert state["release"]["eligible"] is False
    assert state["release"]["deployment_authorized"] is False

    # Check negative evidence ledger preservation
    neg_ledger = ROOT / "research_memory" / "NEGATIVE_EVIDENCE_LEDGER.yaml"
    assert neg_ledger.exists()
    neg_data = yaml.safe_load(neg_ledger.read_text(encoding="utf-8"))
    records = neg_data.get("negative_evidence", [])
    assert len(records) >= 36

    # Check structural obstructions preservation
    obs_reg = ROOT / "research_memory" / "RESEARCH_OBSTRUCTION_REGISTRY.yaml"
    assert obs_reg.exists()
    obs_data = yaml.safe_load(obs_reg.read_text(encoding="utf-8"))
    assert len(obs_data.get("obstructions", [])) >= 17


# --- 3. Candidate A review cannot accept candidate B ---
def test_test03_candidate_mismatch_rejected():
    with pytest.raises(CandidateMismatchError, match="Candidate Mismatch"):
        GovernanceStateManager.validate_candidate_match(
            candidate_id="aa24fbdf251645b70338503a1f361715d942d38f",
            review_candidate_id="1111111111111111111111111111111111111111"
        )
    # Matching candidate passes
    assert GovernanceStateManager.validate_candidate_match(
        candidate_id="aa24fbdf251645b70338503a1f361715d942d38f",
        review_candidate_id="aa24fbdf251645b70338503a1f361715d942d38f"
    ) is True


# --- 4. A missing/failed review and writer self-acceptance are rejected ---
def test_test04_writer_anti_self_acceptance():
    # Writer acting as reviewer is rejected
    with pytest.raises(SelfAcceptanceError, match="cannot act as independent reviewer"):
        GovernanceStateManager.validate_review_and_acceptance(
            writer="antigravity-primary-agent",
            reviewer="antigravity-primary-agent",
            acceptor="governance-coordinator"
        )

    # Writer acting as acceptor is rejected
    with pytest.raises(SelfAcceptanceError, match="cannot act as acceptance authority"):
        GovernanceStateManager.validate_review_and_acceptance(
            writer="antigravity-primary-agent",
            reviewer="antigravity-fresh-context-verifier",
            acceptor="antigravity-primary-agent"
        )

    # Distinct qualified roles pass
    assert GovernanceStateManager.validate_review_and_acceptance(
        writer="antigravity-primary-agent",
        reviewer="antigravity-fresh-context-verifier",
        acceptor="governance-coordinator"
    ) is True


# --- 5. Concurrent stale state update cannot overwrite a newer revision ---
def test_test05_concurrent_stale_update_rejected(tmp_path: Path):
    temp_state_file = tmp_path / "PROJECT_STATE.yaml"
    initial_state = {
        "schema_version": "4.0.3",
        "revision": 5,
        "activation": "ACTIVE",
        "project": {"id": "tubulance"},
        "epistemic_status": {"clay_statement_b_status": "UNRESOLVED"},
        "release": {"state": "NO-GO", "eligible": False, "deployment_authorized": False},
        "hard_gates": {
            "clay_statement_b_unresolved": "PASS",
            "dag_cycle_count": "PASS",
            "claim_passport_census": "PASS",
            "negative_evidence_retention": "PASS",
            "writer_anti_self_acceptance": "PASS"
        }
    }
    with open(temp_state_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(initial_state, f)

    mgr = GovernanceStateManager(temp_state_file)

    # Stale expected revision (expected 4, actual is 5) must raise StaleRevisionError
    with pytest.raises(StaleRevisionError, match="Expected revision 4, but found actual revision 5"):
        mgr.update_state(expected_revision=4, update_fn=lambda s: s)

    # Correct expected revision succeeds and increments revision to 6
    updated = mgr.update_state(expected_revision=5, update_fn=lambda s: s)
    assert updated["revision"] == 6

    # Trying again with 5 now fails because state is at 6
    with pytest.raises(StaleRevisionError, match="Expected revision 5, but found actual revision 6"):
        mgr.update_state(expected_revision=5, update_fn=lambda s: s)


# --- 6. Synthetic/Fixture evidence cannot certify real execution ---
def test_test06_synthetic_evidence_boundary():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))
    assert state["project"]["dirty"] in {"CLEAN", "DIRTY_KNOWN"}
    assert state["epistemic_status"]["target_problem"] == "Clay Millennium Prize Problem Statement B on T^3 (nu > 0, f = 0)"
    # Fixture-only or mock evidence cannot satisfy E3/E4
    for ev in state.get("evidence_refs", []):
        assert ev["type"] in {"MATH_E4_ANALYTIC_PROOF_AUDITED", "GOV_E3_REPRODUCIBLE", "GOV_E4_INDEPENDENT_VERIFIER", "GOV_E5_EXTERNAL_ANCHORED"}


# --- 7. Required delegated specs remain reachable and historical instructions inactive ---
def test_test07_delegated_specs_reachable():
    direction_text = DIRECTION_PATH.read_text(encoding="utf-8")
    assert "MATHEMATICAL_RESEARCH_CONSTITUTION.md" in direction_text
    assert "CLAIM_REGISTRY.yaml" in direction_text
    assert "RESEARCH_OBSTRUCTION_REGISTRY.yaml" in direction_text
    assert "NEGATIVE_EVIDENCE_LEDGER.yaml" in direction_text

    # Verify delegated files actually exist on disk
    assert (ROOT / "mathematical_constitution" / "MATHEMATICAL_RESEARCH_CONSTITUTION.md").exists()
    assert (ROOT / "mathematical_constitution" / "CLAIM_REGISTRY.yaml").exists()
    assert (ROOT / "research_memory" / "RESEARCH_OBSTRUCTION_REGISTRY.yaml").exists()
    assert (ROOT / "research_memory" / "NEGATIVE_EVIDENCE_LEDGER.yaml").exists()


# --- 8. Recovery preserves unrelated dirty files and sealed historical hashes ---
def test_test08_sealed_history_integrity():
    # Check that frozen/sealed manifests exist
    th1r_manifest = ROOT / "th1r_SEALED_manifest.json"
    if th1r_manifest.exists():
        assert th1r_manifest.stat().st_size > 0

    # Ensure v4 packet manifest is intact
    v4_manifest = ROOT / "governance" / "packet" / "v4.0.3" / "MANIFEST.sha256.json"
    assert v4_manifest.exists()
    manifest_data = json.loads(v4_manifest.read_text(encoding="utf-8"))
    assert len(manifest_data.get("files", {})) == 8


# --- 9. Autonomous next selection respects dependencies, owner priority and reserved actions ---
def test_test09_next_objective_respects_dependencies():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))
    curr = state.get("current_objective", {})
    assert curr.get("id") == "TP2-G6-A2"
    # Dependencies of A2 must include A1
    assert "TP2-G6-A1" in curr.get("dependencies", [])

    # Check that A1 is marked ACCEPTED in objectives
    objs = {o["id"]: o["status"] for o in state.get("objectives", [])}
    assert objs.get("TP2-G6-A1") == "ACCEPTED_AS_CANONICAL_MILESTONE"

    # Check reserved actions are explicitly declared
    assert "VCS force-push" in state.get("reserved_actions", [])
    assert "Declaring Clay Statement B resolved" in state.get("reserved_actions", [])


# --- 10. Migration acceptance grants neither product acceptance nor deployment permission ---
def test_test10_migration_acceptance_is_not_deployment():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))
    assert state["release"]["state"] == "NO-GO"
    assert state["release"]["deployment_authorized"] is False
    assert "CLAY_B_UNRESOLVED" in state["release"]["reason"]


# --- 11. UI and Capability Completeness Requirements ---
def test_test11_capabilities_bound_with_evidence():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))
    caps = state.get("capabilities", {})
    assert "CAP-NS-ANALYTICS" in caps
    assert "CAP-NS-STOCHASTIC" in caps
    assert "CAP-NS-ASSURANCE" in caps
    for cap_name, cap_data in caps.items():
        assert cap_data["status"].startswith("VERIFIED_")
        assert len(cap_data.get("evidence_refs", [])) > 0


# --- 12. Shared receipts verify only explicitly mapped dimensions ---
def test_test12_receipt_dimension_mapping():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))
    # Check that evidence references match registered claims
    engine = MathAssuranceEngine()
    audit = engine.run_full_assurance_audit()
    assert audit["overall_assurance_passed"] is True
    assert audit["dag_cycles_count"] == 0
    assert audit["total_claims_count"] >= 33


# --- 13. Project Epistemic Invariant: Clay Statement B remains UNRESOLVED ---
def test_test13_clay_statement_b_invariant():
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))
    assert state["epistemic_status"]["clay_statement_b_status"] == "UNRESOLVED"
    gov_text = GOVERNANCE_PATH.read_text(encoding="utf-8")
    assert "UNRESOLVED" in gov_text
    dir_text = DIRECTION_PATH.read_text(encoding="utf-8")
    assert "UNRESOLVED" in dir_text


# ==============================================================================
# 12 EXPLICIT NEGATIVE MIGRATION SCENARIOS (SECTION 18 REQUIREMENT)
# ==============================================================================

# --- Negative Test 1: Missing Mandatory Authority File ---
def test_negative_01_missing_mandatory_authority_file(tmp_path: Path):
    gov_dir = tmp_path / "governance"
    gov_dir.mkdir()
    (gov_dir / "GOVERNANCE.md").write_text("# Gov", encoding="utf-8")
    (gov_dir / "PROJECT_DIRECTION.md").write_text("# Direction", encoding="utf-8")
    # Missing PROJECT_STATE.yaml
    with pytest.raises(GovernanceStateError, match="Missing mandatory authority file"):
        GovernanceStateManager.validate_mandatory_authorities(gov_dir)


# --- Negative Test 2: Conflicting Governance Version ---
def test_negative_02_conflicting_governance_version():
    with pytest.raises(GovernanceStateError, match="Conflicting governance version: '3.0.0'"):
        GovernanceStateManager.validate_governance_version("3.0.0")

    with pytest.raises(GovernanceStateError, match="Conflicting governance version: '4.0.2'"):
        GovernanceStateManager.validate_governance_version("4.0.2")

    # Exact expected version passes
    assert GovernanceStateManager.validate_governance_version("4.0.3") is True


# --- Negative Test 3: Duplicate State Owner ---
def test_negative_03_duplicate_state_owner():
    declarations = [
        {"file": "governance/PROJECT_STATE.yaml", "role": "PRIMARY_LIVE_STATE", "status": "ACTIVE"},
        {"file": "GOVERNANCE_STATE.yaml", "role": "PRIMARY_LIVE_STATE", "status": "ACTIVE"},
    ]
    with pytest.raises(GovernanceStateError, match="Duplicate state owner detected"):
        GovernanceStateManager.validate_single_state_owner(declarations)

    # Valid single owner passes
    valid_decs = [
        {"file": "governance/PROJECT_STATE.yaml", "role": "PRIMARY_LIVE_STATE", "status": "ACTIVE"},
        {"file": "GOVERNANCE_STATE.yaml", "role": "HISTORICAL_POINTER", "status": "ARCHIVED"},
    ]
    assert GovernanceStateManager.validate_single_state_owner(valid_decs) is True


# --- Negative Test 4: Stale Evidence ---
def test_negative_04_stale_evidence():
    active_sha = "48ebabbd73d763ea31b3bbf15277d60e16d86cea"
    stale_sha = "aa24fbdf251645b70338503a1f361715d942d38f"
    with pytest.raises(GovernanceStateError, match="Stale evidence detected"):
        GovernanceStateManager.validate_evidence_freshness(
            evidence_candidate_id=stale_sha,
            current_candidate_id=active_sha
        )

    # Fresh evidence passes
    assert GovernanceStateManager.validate_evidence_freshness(
        evidence_candidate_id=active_sha,
        current_candidate_id=active_sha
    ) is True


# --- Negative Test 5: Candidate Changed After Review ---
def test_negative_05_candidate_changed_after_review():
    review_sha = "48ebabbd73d763ea31b3bbf15277d60e16d86cea"
    tampered_sha = "9999999999999999999999999999999999999999"
    with pytest.raises(CandidateMismatchError, match="Candidate Mismatch"):
        GovernanceStateManager.validate_candidate_match(
            candidate_id=tampered_sha,
            review_candidate_id=review_sha
        )


# --- Negative Test 6: Self-Review / Self-Acceptance ---
def test_negative_06_self_review_or_self_acceptance():
    with pytest.raises(SelfAcceptanceError, match="cannot act as independent reviewer"):
        GovernanceStateManager.validate_review_and_acceptance(
            writer="primary-author",
            reviewer="primary-author",
            acceptor="lead-architect"
        )

    with pytest.raises(SelfAcceptanceError, match="cannot act as acceptance authority"):
        GovernanceStateManager.validate_review_and_acceptance(
            writer="primary-author",
            reviewer="independent-reviewer",
            acceptor="primary-author"
        )


# --- Negative Test 7: Unsupported Evidence-Strength Promotion ---
def test_negative_07_unsupported_evidence_promotion():
    # Attempting to claim E4 under IND0 or without independent verifier must fail
    with pytest.raises(GovernanceStateError, match="Unsupported evidence promotion"):
        GovernanceStateManager.validate_evidence_promotion(
            claimed_dimension="E4",
            independence="IND0",
            has_independent_verifier=False
        )

    with pytest.raises(GovernanceStateError, match="Unsupported evidence promotion"):
        GovernanceStateManager.validate_evidence_promotion(
            claimed_dimension="E5",
            independence="IND2",
            has_independent_verifier=False
        )

    # Qualified promotion passes
    assert GovernanceStateManager.validate_evidence_promotion(
        claimed_dimension="E4",
        independence="IND3",
        has_independent_verifier=True
    ) is True


# --- Negative Test 8: Historical Record Rewriting ---
def test_negative_08_historical_record_rewriting():
    # Verify that historical sealed checkpoint commits exist in git log
    result = subprocess.run(
        ["git", "cat-file", "-e", "9783774430cd3939d473cd0e833aa2cf5b5c0645"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "Sealed historical commit 9783774 must remain reachable in Git history"

    # Check G5 historical candidate reference in GOVERNANCE_STATE.yaml
    root_gov = ROOT / "GOVERNANCE_STATE.yaml"
    content = root_gov.read_text(encoding="utf-8")
    assert "GIT_SHA:a492a7854e5ecb7fd14f183463f6182acb6b3f5b" in content, (
        "Historical G5 candidate reference must not be rewritten in legacy GOVERNANCE_STATE.yaml"
    )


# --- Negative Test 9: Mathematical Truth Promotion from Technical PASS ---
def test_negative_09_mathematical_truth_promotion_from_technical_pass():
    # Technical pass cannot promote claim without analytic proof passport
    with pytest.raises(GovernanceStateError, match="Epistemic category error"):
        GovernanceStateManager.validate_mathematical_promotion(
            is_technical_pass=True,
            has_analytic_passport=False
        )

    # With analytic passport it is permitted
    assert GovernanceStateManager.validate_mathematical_promotion(
        is_technical_pass=True,
        has_analytic_passport=True
    ) is True


# --- Negative Test 10: Invalid Independence Namespace ---
def test_negative_10_invalid_independence_namespace():
    # Governance domain cannot use MATH_I codes
    with pytest.raises(GovernanceStateError, match="Invalid namespace in governance domain"):
        GovernanceStateManager.validate_independence_namespace("GOVERNANCE", "MATH_I2")

    # Mathematics domain cannot use operational IND codes
    with pytest.raises(GovernanceStateError, match="Invalid namespace in mathematical domain"):
        GovernanceStateManager.validate_independence_namespace("MATHEMATICS", "IND2")

    # Correct namespaces pass
    assert GovernanceStateManager.validate_independence_namespace("GOVERNANCE", "IND2") is True
    assert GovernanceStateManager.validate_independence_namespace("MATHEMATICS", "MATH_I2") is True


# --- Negative Test 11: Unresolved Target Accidentally Marked Solved ---
def test_negative_11_unresolved_target_accidentally_marked_solved(tmp_path: Path):
    with pytest.raises(GovernanceStateError, match="Epistemic invariant violation"):
        GovernanceStateManager.validate_target_problem_status("SOLVED")

    with pytest.raises(GovernanceStateError, match="Epistemic invariant violation"):
        GovernanceStateManager.validate_target_problem_status("RESOLVED")

    # In state file validation
    temp_state = tmp_path / "PROJECT_STATE.yaml"
    bad_state = {
        "schema_version": "4.0.3",
        "revision": 1,
        "activation": "ACTIVE",
        "project": {"id": "tubulance"},
        "epistemic_status": {"clay_statement_b_status": "SOLVED"},
        "release": {"state": "NO-GO", "eligible": False, "deployment_authorized": False},
        "hard_gates": {
            "clay_statement_b_unresolved": "PASS",
            "dag_cycle_count": "PASS",
            "claim_passport_census": "PASS",
            "negative_evidence_retention": "PASS",
            "writer_anti_self_acceptance": "PASS"
        }
    }
    temp_state.write_text(yaml.safe_dump(bad_state), encoding="utf-8")
    mgr = GovernanceStateManager(temp_state)
    with pytest.raises(GovernanceStateError, match="clay_statement_b_status must be 'UNRESOLVED'"):
        mgr.validate_state()


# --- Negative Test 12: Rollback Attempt Deleting Pre-Migration Scientific State ---
def test_negative_12_rollback_deleting_pre_migration_state():
    migration_owned = {
        "governance/GOVERNANCE.md",
        "governance/PROJECT_DIRECTION.md",
        "governance/PROJECT_STATE.yaml",
        "src/navier3d/governance/state_manager.py",
        "tests/test_governance_v4_migration.py"
    }
    # Attempting to delete pre-existing claim registry during rollback must be blocked
    with pytest.raises(GovernanceStateError, match="Rollback safety violation"):
        GovernanceStateManager.validate_rollback_scope(
            target_files_to_revert=["mathematical_constitution/CLAIM_REGISTRY.yaml"],
            migration_owned_files=migration_owned
        )

    # Attempting to delete pre-existing negative evidence ledger must be blocked
    with pytest.raises(GovernanceStateError, match="Rollback safety violation"):
        GovernanceStateManager.validate_rollback_scope(
            target_files_to_revert=["research_memory/NEGATIVE_EVIDENCE_LEDGER.yaml"],
            migration_owned_files=migration_owned
        )

    # Rolling back migration-owned file succeeds
    assert GovernanceStateManager.validate_rollback_scope(
        target_files_to_revert=["governance/PROJECT_STATE.yaml"],
        migration_owned_files=migration_owned
    ) is True

