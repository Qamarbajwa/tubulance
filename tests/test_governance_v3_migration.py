"""Executable conformance checks for NS-GOV-MIG-V300-001.

These checks validate the operational migration layer. They do not certify
mathematical truth or Navier-Stokes regularity.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "governance" / "packet" / "v3.0.0"
STATE_PATH = ROOT / "GOVERNANCE_STATE.yaml"
ENVELOPE_PATH = ROOT / "governance" / "task_envelopes" / "TP2-G5-A5.yaml"
RECEIPT_PATH = ROOT / "governance" / "evidence" / "NS-GOV-MIG-V300-001-packet.json"
V2_STATE = ROOT / "governance" / "migrations" / "GOVERNANCE_STATE_v2.10.1_HISTORICAL.yaml"
R1_RECEIPT_PATH = ROOT / "governance" / "evidence" / "TP2-G5-A5_R1_PROVENANCE.json"
R1_DIFF_PATH = ROOT / "TP2_G5_A5_R1_CANDIDATE_TO_ACCEPTANCE_DIFF.txt"

SCIENTIFIC_CANDIDATE = "a492a7854e5ecb7fd14f183463f6182acb6b3f5b"
ACCEPTANCE_EVIDENCE_COMMIT = "ad00e0c6421a62ced5537d495aaeb5fe94c8462e"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_schema(instance: dict, schema_name: str) -> None:
    schema = load_json(PACKET / schema_name)
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
    assert not errors, "\n".join(error.message for error in errors)


def test_gc_01_project_binding_is_machine_observed() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    envelope_path = ROOT / "governance" / "task_envelopes" / "TP2-G5-A5.yaml"
    envelope = yaml.safe_load(envelope_path.read_text(encoding="utf-8"))["task_execution_envelope"]
    top = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=ROOT, text=True).strip()
    assert Path(top).resolve() == ROOT.resolve()
    assert state["project_binding"]["project_id"] == "tubulance"
    assert state["project_binding"]["repository_or_workspace"] == "D:/Comfy UI/tubulance"
    completion = envelope.get("completion_record", {})
    expected = completion.get("final_candidate_id") or envelope["base_state"]["base_candidate_id"]
    assert state["project_binding"]["current_candidate_id"] == expected


def test_gc_02_context_is_project_local() -> None:
    state_text = STATE_PATH.read_text(encoding="utf-8")
    assert "project_id: \"tubulance\"" in state_text
    assert "repository_or_workspace: \"D:/Comfy UI/tubulance\"" in state_text


def test_gc_03_owner_intent_is_preserved() -> None:
    intent = (ROOT / "PROJECT_INTENT.md").read_text(encoding="utf-8")
    assert "not to maximize candidate" in intent
    assert "Clay Statement B remains `UNRESOLVED`" in intent


def test_gc_04_no_routine_owner_technical_certification() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    assert state["standing_mandate"]["active"] is True
    assert state["standing_mandate"]["autonomous_technical_work_allowed"] is True
    assert state["standing_mandate"]["owner_technical_certification_required"] is False


def test_gc_05_typed_authority_is_explicit() -> None:
    policy = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]["authority_policy"]
    for key in ("owner_intent_authority", "business_policy_authority", "legal_compliance_authority", "implementation_authority", "verification_authority", "release_eligibility_authority", "deployment_authority"):
        assert key in policy


def test_gc_06_generic_approval_is_not_used_as_authority() -> None:
    state = STATE_PATH.read_text(encoding="utf-8")
    envelope = ENVELOPE_PATH.read_text(encoding="utf-8")
    assert "generic_approved_flag_prohibited: true" in state
    assert "approved: true" not in state.lower()
    assert "approved: true" not in envelope.lower()


def test_gc_07_dependency_eligibility_is_structured() -> None:
    envelope = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]
    eligibility = envelope["eligibility"]
    assert eligibility["eligible"] is True
    assert all(item["state"] in {"ACCEPTED", "SATISFIED", "N/A"} for item in eligibility["dependencies"])


def test_gc_08_blockers_are_typed() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    allowed = {"TECHNICAL", "EVIDENCE", "DEPENDENCY", "EXTERNAL", "INFRASTRUCTURE", "OWNER_INTENT", "BUSINESS_POLICY", "LEGAL_COMPLIANCE", "SECURITY", "FINANCIAL_EXPOSURE", "DEPLOYMENT_AUTHORITY", "UNKNOWN"}
    assert all(item["class"] in allowed for item in state["blockers"])
    assert "needs owner approval" not in STATE_PATH.read_text(encoding="utf-8").lower()


def test_gc_09_risk_and_action_are_separate() -> None:
    risk = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]["risk_and_action"]
    envelope = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]["classification"]
    assert risk["active_risk_tier"] == "T4"
    assert risk["active_action_class"] == "B"
    assert envelope["risk_tier"] == "T3" and envelope["action_class"] == "B"


def test_gc_10_standing_mandate_is_bounded() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    bounds = " ".join(state["standing_mandate"]["bounded_by"])
    assert "accepted project intent" in bounds
    assert "risk ceiling T4" in bounds
    assert "approved financial envelope" in bounds


def test_gc_11_assurance_contract_exists() -> None:
    envelope = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]
    contract = envelope["assurance_contract"]
    assert contract["intent"] and contract["invariants"] and contract["failure_contracts"]


def test_gc_12_intent_fidelity_is_separate() -> None:
    contract = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]["assurance_contract"]
    assert contract["intent_fidelity_review_required"] is True


def test_gc_13_evidence_dimensions_are_independent() -> None:
    receipt = load_json(RECEIPT_PATH)
    assert {receipt["strength"], receipt["environment"], receipt["independence"]} == {"E3", "INTEGRATED_LOCAL", "IND1"}


def test_gc_14_candidate_binding_is_exact() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    receipt_path = ROOT / "governance" / "evidence" / "TP2-G5-A5-ACCEPTANCE.json"
    receipt = load_json(receipt_path if receipt_path.exists() else RECEIPT_PATH)
    assert receipt["candidate_id"] == state["project_binding"]["current_candidate_id"]
    assert receipt["candidate_identity_type"] == "GIT_SHA"


def test_gc_15_stale_evidence_fails_closed() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    receipt = load_json(RECEIPT_PATH)
    mutated = copy.deepcopy(receipt)
    mutated["candidate_id"] = "GIT_SHA:stale-candidate"
    assert mutated["candidate_id"] != state["project_binding"]["current_candidate_id"]
    assert state["evidence_policy"]["stale_evidence_fails_closed"] is True


def test_gc_16_writer_cannot_self_certify() -> None:
    envelope = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]
    roles = envelope["roles_and_authority"]
    assert roles["writer"]["id"] != roles["reviewer_or_verifier"]["id"]
    assert roles["reviewer_or_verifier"]["expected_independence"] == "IND1"


def test_gc_17_test_integrity_is_declared() -> None:
    envelope = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]
    assert "CORE-TEST-INTEGRITY" in envelope["classification"]["active_modules"]
    assert any("unrelated dirty work" in item for item in envelope["mutation_scope"]["forbidden"])


def test_gc_18_negative_history_is_referenced() -> None:
    envelope = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]
    assert "research_memory/NEGATIVE_EVIDENCE_LEDGER.yaml" in envelope["completion_record"]["negative_evidence_refs"]


def test_gc_19_hard_gates_and_kpis_are_separate() -> None:
    acceptance = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]["acceptance"]
    assert acceptance["hard_gates"] and acceptance["kpis"]
    assert all(item["release_blocking"] is False for item in acceptance["kpis"])


def test_gc_20_release_and_deployment_are_separate() -> None:
    release = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]["release"]
    assert release["release_eligible"] is False
    assert release["deployment_authorized"] is False


def test_gc_21_candidate_is_machine_derived() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    assert state["project_binding"]["current_candidate_id"].startswith("GIT_SHA:")


def test_gc_22_migration_is_fail_closed_for_release() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    assert state["release"]["current_state"] == "NOT_RELEASE_ELIGIBLE"
    assert state["release"]["release_eligible"] is False


def test_gc_23_historical_provenance_survives() -> None:
    assert V2_STATE.is_file()
    assert (ROOT / "governanace" / "v2.10.1_SHA256_MANIFEST.json").is_file()
    assert "v2.10.1" in V2_STATE.read_text(encoding="utf-8")


def test_gc_24_owner_action_reclassification_is_explicit() -> None:
    mapping = (ROOT / "governance" / "authority_compatibility_v3.0.0.md").read_text(encoding="utf-8")
    assert "TECHNICALLY_DERIVABLE" not in mapping
    assert "IMPLEMENTATION_AUTHORITY" in mapping
    assert "no actionable OWNER-* queue" in (ROOT / "GOVERNANCE_MIGRATION_V2_10_1_TO_V3_0_0.md").read_text(encoding="utf-8")


def test_gc_25_reserved_actions_remain_blocked() -> None:
    envelope = yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8"))["task_execution_envelope"]
    assert envelope["roles_and_authority"]["reserved_external_authority"]["required"] is False
    assert any("Force-push" in item for item in envelope["mutation_scope"]["forbidden"])


def test_gc_26_git_state_safety_is_explicit() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]["git_or_checkpoint"]
    assert state["force_push_prohibited"] is True
    assert state["unrelated_dirty_work_preserved"] is True


def test_gc_27_environment_honesty_is_explicit() -> None:
    receipt = load_json(RECEIPT_PATH)
    assert receipt["environment"] == "INTEGRATED_LOCAL"
    assert "Remote replication" in " ".join(receipt["claim_not_supported"])


def test_gc_28_governance_review_is_declared() -> None:
    migration = (ROOT / "GOVERNANCE_MIGRATION_V2_10_1_TO_V3_0_0.md").read_text(encoding="utf-8")
    assert "CONFORMANT_WITH_DECLARED_LIMITATIONS" in migration
    assert "IND1" in migration


def test_gc_29_next_step_is_not_ceremonial_owner_approval() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    assert state["next_action"]["objective_id"] == "TP2-G5-A5"
    assert state["next_action"]["blocker_class"] is None
    assert "validated v3 envelope" in state["next_action"]["description"]


def test_gc_30_truthful_release_reporting() -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    assert state["release"]["current_state"] == "NOT_RELEASE_ELIGIBLE"
    assert state["direction"]["clay_statement_b_status"] == "UNRESOLVED"


def test_state_schema() -> None:
    assert_schema(yaml.safe_load(STATE_PATH.read_text(encoding="utf-8")), "06A_GOVERNANCE_STATE_SCHEMA_v3.0.0.json")


def test_envelope_schema() -> None:
    assert_schema(yaml.safe_load(ENVELOPE_PATH.read_text(encoding="utf-8")), "05A_TASK_EXECUTION_ENVELOPE_SCHEMA_v3.0.0.json")


def test_evidence_receipt_schema() -> None:
    assert_schema(load_json(RECEIPT_PATH), "13_EVIDENCE_RECEIPT_SCHEMA_v3.0.0.json")


def test_packet_manifest_hashes() -> None:
    manifest = load_json(PACKET / "22_SHA256_MANIFEST_v3.0.0.json")
    assert len(manifest["files"]) == 26
    for entry in manifest["files"]:
        path = PACKET / entry["file"]
        assert path.is_file(), entry["file"]
        data = path.read_bytes()
        assert len(data) == entry["bytes"], entry["file"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], entry["file"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "2.0.0"),
        ("governance_version", "2.0.0"),
    ],
)
def test_adversarial_state_version_mutation_fails(field: str, value: str) -> None:
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))
    state["governance_state"][field] = value
    validator = Draft202012Validator(load_json(PACKET / "06A_GOVERNANCE_STATE_SCHEMA_v3.0.0.json"))
    assert list(validator.iter_errors(state))


def test_adversarial_receipt_candidate_mutation_is_stale() -> None:
    receipt = load_json(RECEIPT_PATH)
    receipt["candidate_id"] = "GIT_SHA:other-candidate"
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    assert receipt["candidate_id"] != state["project_binding"]["current_candidate_id"]


def test_r1_provenance_receipt_separates_scientific_acceptance_and_current_head() -> None:
    receipt = load_json(R1_RECEIPT_PATH)
    state = yaml.safe_load(STATE_PATH.read_text(encoding="utf-8"))["governance_state"]
    provenance = state["provenance"]

    assert receipt["scientific_candidate_commit"] == SCIENTIFIC_CANDIDATE
    assert receipt["acceptance_evidence_commit"] == ACCEPTANCE_EVIDENCE_COMMIT
    assert provenance["scientific_candidate_commit"] == SCIENTIFIC_CANDIDATE
    assert provenance["acceptance_evidence_commit"] == ACCEPTANCE_EVIDENCE_COMMIT
    assert receipt["current_repository_head"]["sha"] is None
    assert receipt["current_repository_head"]["derivation_command"] == "git rev-parse HEAD"
    assert receipt["current_repository_head"]["self_reference_avoided"] is True


def test_r1_reconciles_current_governance_fields_without_rewriting_history() -> None:
    state_text = STATE_PATH.read_text(encoding="utf-8")
    state = yaml.safe_load(state_text)["governance_state"]
    git_state = state["git_or_checkpoint"]

    assert state["project_binding"]["current_candidate_id"] == f"GIT_SHA:{SCIENTIFIC_CANDIDATE}"
    assert state["project_binding"]["verified_checkpoint_id"] == f"GIT_SHA:{ACCEPTANCE_EVIDENCE_COMMIT}"
    assert git_state["accepted_scientific_checkpoint"] == SCIENTIFIC_CANDIDATE
    assert git_state["accepted_scientific_receipt"] == SCIENTIFIC_CANDIDATE
    assert git_state["historical_migration_checkpoint"] == "d55b495e91617a58262e2959529c9eb202fffbc8"
    assert state_text.count("remote_distribution_state:") == 1
    assert "A3 execution evidence must be finalized" not in state_text
    assert "T4 is the broader program risk ceiling" in state_text


def test_r1_diff_receipt_proves_governance_only_post_candidate_changes() -> None:
    diff_text = R1_DIFF_PATH.read_text(encoding="utf-8")
    assert f"SCIENTIFIC_CANDIDATE_COMMIT: {SCIENTIFIC_CANDIDATE}" in diff_text
    assert f"ACCEPTANCE_EVIDENCE_COMMIT: {ACCEPTANCE_EVIDENCE_COMMIT}" in diff_text
    assert "git diff --name-status" in diff_text
    assert "git diff --stat" in diff_text
    assert f"git diff {SCIENTIFIC_CANDIDATE}..{ACCEPTANCE_EVIDENCE_COMMIT} -- <scientific-paths>" in diff_text
    assert "SCIENTIFIC_SCOPE_DIFF: NONE" in diff_text
    assert "ANCESTRY_SCIENTIFIC_TO_ACCEPTANCE: PASS" in diff_text
    assert "ANCESTRY_ACCEPTANCE_TO_CURRENT_HEAD: PASS" in diff_text
    assert "LOCAL_REMOTE_MATCH: PASS" in diff_text
    assert "DIRTY_SCOPE_INTERSECTION: NONE" in diff_text
    receipt = load_json(R1_RECEIPT_PATH)
    assert receipt["dirty_state"]["unrelated_path_count"] == 873
    assert receipt["dirty_state"]["scope_intersection"] == "NONE"


def test_r1_acceptance_receipt_binds_test_census_to_observed_tree() -> None:
    receipt = load_json(R1_RECEIPT_PATH)
    assert receipt["test_census"]["candidate_commit"] == ACCEPTANCE_EVIDENCE_COMMIT
    assert receipt["test_census"]["authoritative_pre_r1_result"] == "176 passed in 4.02s"
    assert receipt["test_census"]["independence"] == "IND1"
