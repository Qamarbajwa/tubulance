"""Fresh-context verifier checks for A4 scope, status, and overreach guards."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_required_a4_artifact_set_exists() -> None:
    required = [
        "TP2_G5_A4_SCALE_CRITICAL_WINDOW.md",
        "TP2_G5_A4_CHI_VARIANCE_IDENTITY.md",
        "TP2_G5_A4_STOCHASTIC_HISTORY_DICHOTOMY.md",
        "TP2_G5_A4_RIGID_BRANCH_GEOMETRY.md",
        "TP2_G5_A4_DECOHERENT_BRANCH_COVARIANCE.md",
        "TP2_G5_A4_LEI_REN_TIAN_BRIDGE.md",
        "TP2_G5_A4_CONSTANTIN_FEFFERMAN_BRIDGE.md",
        "TP2_G5_A4_GRUJIC_SPARSENESS_ANALYTICITY_BRIDGE.md",
        "TP2_G5_A4_NONCIRCULARITY_AUDIT.md",
        "TP2_G5_A4_ADVERSARIAL_EXACT_FLOW_CALIBRATION.md",
        "TP2_G5_A4_NEGATIVE_EVIDENCE.md",
        "TP2_G5_A4_NOVELTY_AUDIT.md",
        "TP2_G5_A4_UNDERSTANDING_GATE.md",
        "TP2_G5_A4_INDEPENDENT_VERIFICATION.md",
        "TP2_G5_A4_ACCEPTANCE_DECISION.md",
    ]
    assert all((ROOT / name).is_file() for name in required)


def test_envelope_is_a4_and_eligible() -> None:
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A4.yaml"))["task_execution_envelope"]
    assert envelope["identity"]["task_id"] == "TP2-G5-A4"
    assert envelope["eligibility"]["eligible"] is True
    assert envelope["classification"]["risk_tier"] == "T3"
    assert envelope["classification"]["action_class"] == "B"
    assert "TP2-G5-A5" in " ".join(envelope["stop_conditions"])


def test_exact_candidate_is_machine_observed_and_remote_base_is_preserved() -> None:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True).split()[0]
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A4.yaml"))["task_execution_envelope"]
    candidate = envelope["completion_record"]["final_candidate_id"].split(":", 1)[1]
    assert envelope["base_state"]["base_candidate_id"] == f"GIT_SHA:{remote}"
    assert subprocess.run(["git", "merge-base", "--is-ancestor", candidate, head], cwd=ROOT).returncode == 0


def test_dichotomy_is_subsequence_qualified() -> None:
    text = read("TP2_G5_A4_STOCHASTIC_HISTORY_DICHOTOMY.md")
    assert "compactification" in text
    assert "subsequence" in text
    assert "OSCILLATORY" in text


def test_rigid_branch_has_two_integrated_nonnegative_conclusions() -> None:
    text = read("TP2_G5_A4_RIGID_BRANCH_GEOMETRY.md")
    assert "separate conclusions" in text
    assert "M_D" in text and "C_D" in text
    assert "pointwise" in text


def test_geometric_transfers_are_classified_not_promoted() -> None:
    text = "\n".join(read(name) for name in [
        "TP2_G5_A4_LEI_REN_TIAN_BRIDGE.md",
        "TP2_G5_A4_CONSTANTIN_FEFFERMAN_BRIDGE.md",
        "TP2_G5_A4_GRUJIC_SPARSENESS_ANALYTICITY_BRIDGE.md",
    ])
    assert "NO_DIRECT_TRANSFER" in text
    assert "CIRCULAR_FOR_CLAY_CLOSURE" in text


def test_decoherent_covariance_preserves_trace_vs_spectrum_boundary() -> None:
    text = read("TP2_G5_A4_DECOHERENT_BRANCH_COVARIANCE.md")
    assert "trace" in text
    assert "eigenvalue" in text
    assert "INSUFFICIENT_INFORMATION" in text


def test_adversarial_calibration_keeps_kinematic_and_exact_flow_labels() -> None:
    text = read("TP2_G5_A4_ADVERSARIAL_EXACT_FLOW_CALIBRATION.md")
    assert "Periodic shear" in text
    assert "Beltrami" in text
    assert "KINEMATIC" in text
    assert "not" in text and "upgraded" in text


def test_acceptance_taxonomy_and_stop_are_truthful() -> None:
    decision = read("TP2_G5_A4_ACCEPTANCE_DECISION.md")
    assert "SCENARIO_DICHOTOMY_ESTABLISHED" in decision
    assert "RIGID_BRANCH_PARTIALLY_CONSTRAINED" in decision
    assert "DECOHERENT_BRANCH_PARTIALLY_CONSTRAINED" in decision
    assert "BOTH_BRANCHES_REMAIN_OPEN" in decision
    assert "TP2-G5-A5" in decision
    assert "UNRESOLVED" in decision


def test_receipts_are_candidate_bound_and_ind1() -> None:
    receipt = json.loads((ROOT / "governance/evidence/TP2-G5-A4-ACCEPTANCE.json").read_text(encoding="utf-8"))
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A4.yaml"))["task_execution_envelope"]
    state = yaml.safe_load(read("GOVERNANCE_STATE.yaml"))["governance_state"]
    assert receipt["candidate_identity_type"] == "GIT_SHA"
    assert receipt["independence"] == "IND1"
    assert receipt["strength"] == "E3"
    assert receipt["candidate_id"].startswith("GIT_SHA:")
    assert receipt["candidate_id"] == envelope["completion_record"]["final_candidate_id"]
    assert receipt["candidate_id"] == state["project_binding"]["current_candidate_id"]
