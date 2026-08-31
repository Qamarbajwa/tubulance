"""Fresh-context verifier checks for the TP2-G5-A5 synthesis packet."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_verifier_role_is_distinct_and_ind1() -> None:
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A5.yaml"))["task_execution_envelope"]
    roles = envelope["roles_and_authority"]
    assert roles["writer"]["id"] != roles["reviewer_or_verifier"]["id"]
    assert roles["reviewer_or_verifier"]["expected_independence"] == "IND1"


def test_a5_inputs_are_all_explicitly_accepted() -> None:
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A5.yaml"))["task_execution_envelope"]
    dependencies = {item["id"]: item["state"] for item in envelope["eligibility"]["dependencies"]}
    assert all(dependencies[f"TP2-G5-A{i}"] == "ACCEPTED" for i in range(5))
    assert dependencies["OWNER_CONTINUATION_AUTHORIZATION"] == "SATISFIED"


def test_synthesis_is_not_a_new_theorem() -> None:
    text = read("TP2_G5_A5_PATHWAY_SYNTHESIS.md") + read("TP2_G5_A5_SYNTHESIS_REPORT.md")
    assert "does not introduce a new" in text
    assert "diagnostic" in text
    assert "regularity theorem" in text


def test_branch_status_is_conservative() -> None:
    text = read("TP2_G5_A5_ACCEPTANCE_DECISION.md")
    for marker in ("Both stochastic-history branches remain open", "EVIDENCE_INSUFFICIENT_FOR_GLOBAL_EXCLUSION", "No A6"):
        assert marker in text


def test_candidate_binding_is_machine_checkable() -> None:
    state = yaml.safe_load(read("GOVERNANCE_STATE.yaml"))["governance_state"]
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A5.yaml"))["task_execution_envelope"]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True).split()[0]
    assert head == remote
    assert state["project_binding"]["current_candidate_id"] == envelope["completion_record"]["final_candidate_id"]
    assert state["project_binding"]["current_candidate_id"].startswith("GIT_SHA:")


def test_receipt_acceptance_is_bounded() -> None:
    receipt = json.loads((ROOT / "governance/evidence/TP2-G5-A5-ACCEPTANCE.json").read_text(encoding="utf-8"))
    text = " ".join(receipt["claim_not_supported"])
    assert "Global regularity or blow-up" in text
    assert "Product release eligibility" in text
    assert receipt["result"] == "PASS"


def test_historical_a4_packet_remains_preserved() -> None:
    assert (ROOT / "governance/task_envelopes/TP2-G5-A4.yaml").is_file()
    assert (ROOT / "governance/evidence/TP2-G5-A4-ACCEPTANCE.json").is_file()
    assert "A5 will require a separate authorized increment" in read("TP2_G5_A4_ACCEPTANCE_DECISION.md")


def test_stop_boundary_excludes_successor_execution() -> None:
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A5.yaml"))["task_execution_envelope"]
    forbidden = " ".join(envelope["mutation_scope"]["forbidden"])
    assert "A6" in forbidden
    assert "successor" in forbidden
