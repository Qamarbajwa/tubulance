"""Fresh-context, candidate-bound assurance checks for TP2-G5-A3."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_required_a3_artifacts_exist_and_state_is_unresolved() -> None:
    required = [
        "TP2_G5_A3_AMPLITUDE_DIRECTION_DECOMPOSITION.md",
        "TP2_G5_A3_DEFORMATION_METRIC_XI_GEOMETRY.md",
        "TP2_G5_A3_CONDITION_NUMBER_AUDIT.md",
        "TP2_G5_A3_ENSTROPHY_DISSIPATION_BRIDGE.md",
        "TP2_G5_A3_INVERSE_LENGTH_SCALE_COMPARISON.md",
        "TP2_G5_A3_VORTICITY_DIRECTION_LITERATURE_BRIDGE.md",
        "TP2_G5_A3_SPARSENESS_ANALYTICITY_BRIDGE.md",
        "TP2_G5_A3_TH9R_RESURRECTION_AUDIT.md",
        "TP2_G5_A3_MU_WEIGHTED_GEOMETRY.md",
        "TP2_G5_A3_GEOMETRIC_NO_GO_RESULTS.md",
        "TP2_G5_A3_NOVELTY_AUDIT.md",
        "TP2_G5_A3_UNDERSTANDING_GATE.md",
        "TP2_G5_A3_INDEPENDENT_VERIFICATION.md",
        "TP2_G5_A3_ACCEPTANCE_DECISION.md",
    ]
    assert all((ROOT / name).exists() for name in required)
    state = read("CURRENT_SCIENTIFIC_STATE.md")
    assert "Clay Statement B" in state and "UNRESOLVED" in state


def test_exact_identity_and_domain_guards_are_recorded() -> None:
    geometry = read("TP2_G5_A3_DEFORMATION_METRIC_XI_GEOMETRY.md")
    amplitude = read("TP2_G5_A3_AMPLITUDE_DIRECTION_DECOMPOSITION.md")
    condition = read("TP2_G5_A3_CONDITION_NUMBER_AUDIT.md")
    assert "Xi = M_D + C_D" in geometry
    assert "Gamma = D^T D" in geometry
    assert "beta_j" in geometry and "not an ordinary spatial derivative" in geometry
    assert "kappa_omega^2" in amplitude and "q > 0" in amplitude
    assert "Cond(D)^(-2)" in condition and "Cond(D)^2" in condition


def test_mu_eulerian_guard() -> None:
    text = read("TP2_G5_A3_ENSTROPHY_DISSIPATION_BRIDGE.md") + read("TP2_G5_A3_MU_WEIGHTED_GEOMETRY.md")
    assert "not an Eulerian" in text
    assert "measure identification" in text or "measure-identification" in text


def test_bridge_claim_guard() -> None:
    bridge = read("TP2_G5_A3_VORTICITY_DIRECTION_LITERATURE_BRIDGE.md")
    bridge += read("TP2_G5_A3_SPARSENESS_ANALYTICITY_BRIDGE.md")
    nogo = read("TP2_G5_A3_GEOMETRIC_NO_GO_RESULTS.md")
    assert "NO_DIRECT_TRANSFER" in bridge
    assert "CONDITIONAL" in bridge
    assert "does not" in nogo


def test_novelty_and_frame_boundaries_are_not_promoted() -> None:
    novelty = read("TP2_G5_A3_NOVELTY_AUDIT.md")
    frames = read("TP2_G5_A3_TH9R_RESURRECTION_AUDIT.md")
    assert "N2_NOT_FOUND_IN_AUDITED_SOURCES" in novelty
    assert "N3" not in novelty and "N4" not in novelty
    assert "PARTIALLY_REUSED" in frames
    assert "not the instantaneous strain eigenframe" in frames


def test_candidate_bound_envelope_and_eligibility_receipt() -> None:
    envelope = yaml.safe_load(read("governance/task_envelopes/TP2-G5-A3.yaml"))
    eligibility = json.loads(read("governance/evidence/TP2-G5-A3-ELIGIBILITY.json"))
    assert envelope["task_execution_envelope"]["identity"]["task_id"] == "TP2-G5-A3"
    assert envelope["task_execution_envelope"]["eligibility"]["eligible"] is True
    assert envelope["task_execution_envelope"]["base_state"]["base_candidate_id"] == "GIT_SHA:cad737cd1bfda3098e0db331dcb329c6e21f39c1"
    assert eligibility["candidate_id"] == "GIT_SHA:cad737cd1bfda3098e0db331dcb329c6e21f39c1"
    assert eligibility["result"] == "PASS"


def test_acceptance_forbids_a4_and_preserves_clay_status() -> None:
    decision = read("TP2_G5_A3_ACCEPTANCE_DECISION.md")
    envelope = read("governance/task_envelopes/TP2-G5-A3.yaml")
    assert "Clay Statement B = UNRESOLVED" in decision
    assert "TP2-G5-A4 was not executed" in decision
    assert "Execute TP2-G5-A4" in envelope
