"""Independent Verifier test suite for Mathematical Assurance Layer (NS-MRC-1)."""
import pytest
from navier3d.math_assurance import MathAssuranceEngine, AssumptionManager, ClaimManager


def test_v1_epistemic_separation_of_canonical_meanings():
    """V1: Verify strict separation between PROJECT_CANONICAL and FIELD_CANONICAL."""
    claim_mgr = ClaimManager()
    canonical_claims = claim_mgr.get_canonical_claims()
    assert len(canonical_claims) >= 5

    # CLM-001 is from Constantin & Iyer 2008 -> FIELD_CANONICAL
    clm1 = claim_mgr.get_claim("CLM-001")
    assert clm1["passport"]["project_status"] == "PROJECT_CANONICAL"
    assert clm1["passport"]["external_validation"] == "KNOWN_LITERATURE"
    assert clm1["passport"]["community_status"] == "COMMUNITY_ACCEPTED"

    # CLM-011 is project original -> PROJECT_CANONICAL, NOT_COMMUNITY_ACCEPTED
    clm11 = claim_mgr.get_claim("CLM-011")
    assert clm11["passport"]["project_status"] == "PROJECT_CANONICAL"
    assert clm11["passport"]["external_validation"] == "NOT_EXTERNALLY_REVIEWED"
    assert clm11["passport"]["community_status"] == "NOT_COMMUNITY_ACCEPTED"


def test_v2_target_equivalence_gate():
    """V2: Verify that claiming global regularity under conditional BKM assumption is rejected."""
    engine = MathAssuranceEngine()

    # Attempting to claim global regularity with BKM assumption ASM-007
    res_bkm = engine.audit_target_equivalence(
        claimed_result="GLOBAL_REGULARITY",
        actual_assumptions=["ASM-001", "ASM-002", "ASM-007"]
    )
    assert res_bkm["target_matched"] is False
    assert res_bkm["verdict"] == "KNOWN_CONDITIONAL_CRITERION_NOT_TARGET_CLOSURE"

    # Clean unconditioned formulation
    res_clean = engine.audit_target_equivalence(
        claimed_result="GLOBAL_REGULARITY",
        actual_assumptions=["ASM-001", "ASM-002", "ASM-003", "ASM-004"]
    )
    assert res_clean["target_matched"] is True
    assert res_clean["verdict"] == "TARGET_EQUIVALENCE_VALID"


def test_v3_mathematical_regression_invariants_presence():
    """V3: Verify that proof incidents have corresponding mathematical regression rules."""
    import yaml
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    const_dir = os.path.join(base_dir, "mathematical_constitution")

    with open(os.path.join(const_dir, "PROOF_INCIDENT_REGISTER.yaml"), "r", encoding="utf-8") as f:
        inc_data = yaml.safe_load(f)

    with open(os.path.join(const_dir, "MATHEMATICAL_REGRESSION_RULES.yaml"), "r", encoding="utf-8") as f:
        rule_data = yaml.safe_load(f)

    incidents = inc_data.get("incidents", [])
    rules = rule_data.get("rules", [])

    assert len(incidents) >= 4
    assert len(rules) >= 4

    rule_ids = {r["rule_id"] for r in rules}
    for inc in incidents:
        assert inc["regression_rule_id"] in rule_ids
