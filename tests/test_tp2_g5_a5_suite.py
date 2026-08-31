"""Deterministic boundary checks for the TP2-G5-A5 campaign synthesis."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_a5_artifact_set_is_complete() -> None:
    required = [
        "TP2_G5_A5_SYNTHESIS_REPORT.md",
        "TP2_G5_A5_CLAIM_EVIDENCE_MATRIX.md",
        "TP2_G5_A5_LOAD_BEARING_RESULT_SYNTHESIS.md",
        "TP2_G5_A5_OBSTRUCTION_AND_NEGATIVE_EVIDENCE_MAP.md",
        "TP2_G5_A5_PATHWAY_SYNTHESIS.md",
        "TP2_G5_A5_NONCIRCULARITY_AND_OPEN_BRIDGES.md",
        "TP2_G5_A5_NOVELTY_STATUS.md",
        "TP2_G5_A5_UNDERSTANDING_GATE.md",
        "TP2_G5_A5_INDEPENDENT_VERIFICATION.md",
        "TP2_G5_A5_ACCEPTANCE_DECISION.md",
    ]
    assert all((ROOT / name).is_file() for name in required)


def test_a5_is_explicitly_bounded_to_a0_a4() -> None:
    text = read("TP2_G5_A5_SYNTHESIS_REPORT.md")
    assert "only the accepted A0–A4 evidence" in text
    assert "does not introduce a new PDE estimate" in text
    assert "No A6 or successor mathematical execution" in text


def test_campaign_decision_preserves_unresolved_target() -> None:
    text = read("TP2_G5_A5_ACCEPTANCE_DECISION.md")
    assert "ACCEPTED_WITH_LIMITATIONS" in text
    assert "CLAY_STATEMENT_B = UNRESOLVED" in text
    assert "BOTH_BRANCHES_REMAIN_OPEN" in text


def test_exact_a4_boundaries_are_present_in_synthesis() -> None:
    text = read("TP2_G5_A5_SYNTHESIS_REPORT.md")
    for marker in ("J_n=-log chi_n", "M_D", "C_D", "covariance-trace", "history-to-Eulerian"):
        assert marker in text


def test_no_overclaim_guard() -> None:
    combined = "\n".join(read(name) for name in (
        "TP2_G5_A5_SYNTHESIS_REPORT.md",
        "TP2_G5_A5_CLAIM_EVIDENCE_MATRIX.md",
        "TP2_G5_A5_ACCEPTANCE_DECISION.md",
    ))
    assert "does not prove global regularity" in combined
    assert "does not exclude either" in combined
    assert "does not claim external novelty" not in combined  # novelty guard is in its dedicated artifact
    assert "N2" in combined


def test_open_bridge_map_is_explicit() -> None:
    text = read("TP2_G5_A5_NONCIRCULARITY_AND_OPEN_BRIDGES.md")
    for marker in ("history-to-space", "covariance spectral control", "continuation implication", "not isotropy"):
        assert marker in text


def test_load_bearing_synthesis_keeps_three_inputs() -> None:
    text = read("TP2_G5_A5_LOAD_BEARING_RESULT_SYNTHESIS.md")
    for marker in ("LBR-005", "LBR-006", "LBR-007", "None of them alone proves regularity"):
        assert marker in text


def test_v3_envelope_is_eligible_and_stops_at_a5() -> None:
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A5.yaml"))["task_execution_envelope"]
    assert envelope["identity"]["task_id"] == "TP2-G5-A5"
    assert envelope["eligibility"]["eligible"] is True
    assert envelope["classification"]["risk_tier"] == "T3"
    assert any("A6" in item for item in envelope["stop_conditions"])
    assert any("unrelated dirty work" in item.lower() for item in envelope["mutation_scope"]["forbidden"])


def test_all_a5_receipts_match_schema_and_candidate() -> None:
    schema = json.loads((ROOT / "governance/packet/v3.0.0/13_EVIDENCE_RECEIPT_SCHEMA_v3.0.0.json").read_text(encoding="utf-8"))
    state = yaml.safe_load(read("GOVERNANCE_STATE.yaml"))["governance_state"]
    for path in sorted((ROOT / "governance/evidence").glob("TP2-G5-A5-*.json")):
        receipt = json.loads(path.read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema).iter_errors(receipt))
        assert not errors, f"{path.name}: {[e.message for e in errors]}"
        assert receipt["candidate_identity_type"] == "GIT_SHA"
        assert receipt["candidate_id"] == state["project_binding"]["current_candidate_id"]
        assert receipt["independence"] == "IND1"


def test_a5_does_not_change_release_eligibility() -> None:
    state = yaml.safe_load(read("GOVERNANCE_STATE.yaml"))["governance_state"]
    assert state["release"]["release_eligible"] is False
    assert state["release"]["deployment_authorized"] is False


def test_understanding_gate_is_not_specialist_certification() -> None:
    text = read("TP2_G5_A5_UNDERSTANDING_GATE.md")
    assert "U4_COMPLETE_PACKAGE" in text
    assert "not a specialist proof certification" in text


def test_novelty_ceiling_is_preserved() -> None:
    text = read("TP2_G5_A5_NOVELTY_STATUS.md")
    assert "N2_NOT_FOUND_IN_AUDITED_SOURCES" in text
    assert "does not claim external novelty" in text
    assert "N3 or N4" in text


def test_a5_verifier_separates_writer_and_external_review() -> None:
    text = read("TP2_G5_A5_INDEPENDENT_VERIFICATION.md")
    assert "IND1" in text
    assert "not external peer review" in text
    assert "No new regularity" in text


def test_a5_preserves_a4_history_and_negative_evidence() -> None:
    text = read("TP2_G5_A5_OBSTRUCTION_AND_NEGATIVE_EVIDENCE_MAP.md")
    for marker in ("NS-OBS-015", "NS-OBS-016", "EVIDENCE_INSUFFICIENT_FOR_GLOBAL_EXCLUSION"):
        assert marker in text


def test_a5_does_not_relabel_literature_bridges() -> None:
    text = read("TP2_G5_A5_SYNTHESIS_REPORT.md")
    assert "NO_DIRECT_TRANSFER" in text
    assert "PREPRINT" in text

