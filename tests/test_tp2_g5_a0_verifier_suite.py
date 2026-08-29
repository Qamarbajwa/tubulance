"""Independent/fallback verifier checks for TP2-G5-A0 claim discipline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_verifier_acceptance_is_limited_and_clay_problem_unresolved():
    decision = (ROOT / "TP2_G5_A0_ACCEPTANCE_DECISION.md").read_text(encoding="utf-8")
    assert "ACCEPTED_WITH_LIMITATIONS" in decision
    assert "CLAY_STATEMENT_B = UNRESOLVED" in decision
    assert "A1 is not executed" in decision


def test_verifier_checks_no_joint_realization_overclaim():
    audit = (ROOT / "TP2_G5_A0_JOINT_JET_REALIZATION_AUDIT.md").read_text(encoding="utf-8")
    assert "D-only theorem" in audit
    assert "KINEMATIC_COUNTEREXAMPLE" in audit
    assert "Current classification:** `OPEN`" in audit


def test_verifier_checks_zero_state_and_circularity_guards():
    identity = (ROOT / "TP2_G5_A0_XI_IDENTITY_AND_DOMAIN.md").read_text(encoding="utf-8")
    contract = (ROOT / "TP2_G5_A0_RESEARCH_CONTRACT.md").read_text(encoding="utf-8")
    assert "S_s=0" in identity and "mu_s" in identity
    assert "BKM, Serrin" in contract
    assert "`log Xi` is not" in contract
