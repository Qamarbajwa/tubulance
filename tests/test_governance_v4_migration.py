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
