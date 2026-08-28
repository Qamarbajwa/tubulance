"""Automated unit and integration test suite for Mathematical Assurance Engine (NS-MRC-1-R1)."""
import pytest
from navier3d.math_assurance import (
    MathAssuranceEngine,
    AssumptionManager,
    ClaimManager,
    DependencyGraphManager,
    PromotionManager,
    UnderstandingManager,
    NoveltyManager
)


def test_1_field_canonical_does_not_imply_solved():
    """1: Verify that FIELD_CANONICAL does not automatically grant SOLVED status."""
    mgr = ClaimManager()
    clm1 = mgr.get_claim("CLM-001")
    assert clm1["passport"]["project_status"] == "PROJECT_CANONICAL"
    assert clm1["passport"]["community_status"] == "COMMUNITY_ACCEPTED"
    # Solved check on subtheorem must fail
    res = PromotionManager.validate_solved_eligibility(
        claim_id=clm1["claim_id"],
        target_equivalence=True,
        truth_status="PROVED_THEOREM",
        assumption_drift="NONE",
        dependency_closure=True,
        formalization_fidelity=True,
        math_independence="MATH_I4_HUMAN_SPECIALIST",
        external_validation="MULTI_SPECIALIST_REVIEWED",
        community_status="COMMUNITY_ACCEPTED"
    )
    assert res["solved_eligible"] is False
    assert res["verdict"] == "SUBTHEOREM_CANNOT_BE_SOLVED_ELIGIBLE"


def test_2_only_locked_target_can_become_solved_eligible():
    """2: Verify that only MILLENNIUM_NS_3D_TORUS can be evaluated for SOLVED_ELIGIBLE."""
    res_sub = PromotionManager.validate_solved_eligibility(
        claim_id="CLM-011",
        target_equivalence=True,
        truth_status="PROVED_TARGET",
        assumption_drift="NONE",
        dependency_closure=True,
        formalization_fidelity=True,
        math_independence="MATH_I4_HUMAN_SPECIALIST",
        external_validation="MULTI_SPECIALIST_REVIEWED",
        community_status="COMMUNITY_ACCEPTED"
    )
    assert res_sub["solved_eligible"] is False

    res_target = PromotionManager.validate_solved_eligibility(
        claim_id="MILLENNIUM_NS_3D_TORUS",
        target_equivalence=True,
        truth_status="PROVED_TARGET",
        assumption_drift="NONE",
        dependency_closure=True,
        formalization_fidelity=True,
        math_independence="MATH_I4_HUMAN_SPECIALIST",
        external_validation="MULTI_SPECIALIST_REVIEWED",
        community_status="COMMUNITY_ACCEPTED"
    )
    assert res_target["solved_eligible"] is True
    assert res_target["verdict"] == "SOLVED_ELIGIBLE_RATIFIED"


def test_3_failed_target_equivalence_blocks_solved_eligibility():
    """3: Verify that failing target-equivalence blocks SOLVED_ELIGIBLE."""
    res = PromotionManager.validate_solved_eligibility(
        claim_id="MILLENNIUM_NS_3D_TORUS",
        target_equivalence=False,
        truth_status="PROVED_TARGET",
        assumption_drift="NONE",
        dependency_closure=True,
        formalization_fidelity=True,
        math_independence="MATH_I4_HUMAN_SPECIALIST",
        external_validation="MULTI_SPECIALIST_REVIEWED",
        community_status="COMMUNITY_ACCEPTED"
    )
    assert res["solved_eligible"] is False
    assert res["verdict"] == "TARGET_EQUIVALENCE_FAILED"


def test_4_n2_not_found_cannot_auto_promote_to_external_novelty():
    """4: Verify that N2_NOT_FOUND_IN_AUDITED_SOURCES is bounded and distinct from N3/N4."""
    nov_mgr = NoveltyManager()
    rec = nov_mgr.validate_novelty_record("CLM-011")
    assert rec["valid"] is True
    assert rec["novelty_tier"] == "N2_NOT_FOUND_IN_AUDITED_SOURCES"
    assert rec["novelty_tier"] != "N3_EXTERNAL_NOVELTY_SUPPORTED"
    assert rec["novelty_tier"] != "N4_COMMUNITY_RECOGNIZED_AS_NOVEL"


def test_5_internal_agent_cannot_assign_community_novelty():
    """5: Verify that internal verification cannot assign N4 community novelty."""
    mgr = ClaimManager()
    for claim in mgr.claims.values():
        assert claim["passport"]["novelty"] != "N4_COMMUNITY_RECOGNIZED_AS_NOVEL"


def test_6_and_7_significance_independent_of_correctness_and_novelty():
    """6 & 7: Verify that correctness, novelty, and significance are independent coordinates."""
    mgr = ClaimManager()
    # Correct and known foundation: CLM-001 (N0, S1)
    clm1 = mgr.get_claim("CLM-001")["passport"]
    assert clm1["truth_status"] == "PROVED_THEOREM"
    assert clm1["novelty"] == "N0_KNOWN_FOUNDATION"
    assert clm1["significance"] == "S1_USEFUL_LEMMA"

    # Correct and novel project insight: CLM-003 (N2, S2)
    clm3 = mgr.get_claim("CLM-003")["passport"]
    assert clm3["truth_status"] == "PROVED_THEOREM"
    assert clm3["novelty"] == "N2_NOT_FOUND_IN_AUDITED_SOURCES"
    assert clm3["significance"] == "S2_MAJOR_PROJECT_RESULT"


def test_8_external_and_community_statuses_cannot_contradict():
    """8: Verify schema rejection when external validation is missing but community accepted is claimed."""
    mgr = ClaimManager()
    contradictory_passport = {
        "truth_status": "PROVED_THEOREM",
        "gov_evidence_level": "GOV_E4_INDEPENDENT_VERIFIER",
        "math_evidence_level": "MATH_E4_ANALYTIC_PROOF_AUDITED",
        "gov_review_independence": "GOV_I2_SAME_FAMILY_DIFFERENT_INSTANCE",
        "math_review_independence": "MATH_I2_INDEPENDENT_VERIFIER_AGENT",
        "formalization_state": "NOT_FORMALIZED",
        "understanding_level": "U3_COMPLETE_PACKAGE",
        "novelty": "N1_PROJECT_REFORMULATION",
        "significance": "S1_USEFUL_LEMMA",
        "external_validation": "NOT_EXTERNALLY_REVIEWED",
        "community_status": "COMMUNITY_ACCEPTED", # Contradiction!
        "project_status": "PROJECT_CANONICAL"
    }
    check = mgr.validate_passport(contradictory_passport)
    assert check["valid"] is False
    assert "Contradictory status" in check["reason"]


def test_9_and_10_explicit_evidence_and_independence_namespaces():
    """9 & 10: Verify explicit namespaces in passports (no bare ambiguous E4 or I3)."""
    mgr = ClaimManager()
    for cid, claim in mgr.claims.items():
        p = claim["passport"]
        assert p["gov_evidence_level"].startswith("GOV_E")
        assert p["math_evidence_level"].startswith("MATH_E")
        assert p["gov_review_independence"].startswith("GOV_I")
        assert p["math_review_independence"].startswith("MATH_I")


def test_11_and_12_claim_census_and_stale_passports():
    """11 & 12: Verify automated claim census across the registry."""
    mgr = ClaimManager()
    census = mgr.run_claim_census()
    assert census["total_claims_registered"] >= 13
    assert census["invalid_passports_count"] == 0
    assert census["census_verdict"] == "CENSUS_PASSED"


def test_13_official_clay_branch_identity_fixed():
    """13: Verify that problem identity is permanently bound to Clay Statement Branch B."""
    engine = MathAssuranceEngine()
    branch_check = engine.validate_branch_identity()
    assert branch_check["valid"] is True
    assert branch_check["official_target_branch"] == "CLAY_STATEMENT_B_PERIODIC_R3_MOD_Z3"


def test_14_conditional_criterion_fails_target_equivalence():
    """14: Verify that conditional criteria (e.g. assuming bounded vorticity) fail target equivalence."""
    engine = MathAssuranceEngine()
    res = engine.audit_target_equivalence("GLOBAL_REGULARITY", ["ASM-001", "ASM-002", "ASM-007"])
    assert res["target_matched"] is False
    assert res["verdict"] == "KNOWN_CONDITIONAL_CRITERION_NOT_TARGET_CLOSURE"


def test_15_and_16_a4_acceptance_and_g4_closure_prerequisites():
    """15 & 16: Verify that test pass counts alone do not constitute acceptance."""
    # Test pass alone does not bypass required acceptance decisions
    trans_missing_e4 = PromotionManager.validate_transition(
        "E3_REPRODUCIBLE", "PROJECT_CANONICAL",
        {"e3_reproducible": True, "e4_verified": False, "understanding_package": True, "novelty_checked": True}
    )
    assert trans_missing_e4["allowed"] is False
