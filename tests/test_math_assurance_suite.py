"""Automated unit and integration test suite for Mathematical Assurance Engine (NS-MRC-1)."""
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


def test_assumption_manager_foundational_loading():
    """Verify loading and classification of foundational problem assumptions."""
    mgr = AssumptionManager()
    assert len(mgr.assumptions) >= 6
    asm1 = mgr.get_assumption("ASM-001")
    assert asm1 is not None
    assert asm1["name"] == "INCOMPRESSIBILITY"
    assert asm1["classification"] == "FOUNDATIONAL"


def test_assumption_drift_and_circularity_detector():
    """Verify that invoking BKM or Serrin assumptions triggers CIRCULAR_FOR_GLOBAL_REGULARITY."""
    mgr = AssumptionManager()

    # Valid foundational set
    valid_set = ["ASM-001", "ASM-002", "ASM-003", "ASM-004"]
    res_valid = mgr.validate_assumption_set(valid_set, target_goal="GLOBAL_REGULARITY")
    assert res_valid["valid"] is True
    assert res_valid["is_circular_for_target"] is False
    assert res_valid["verdict"] == "VALID_ASSUMPTIONS"

    # Circular set including BKM
    circular_set = ["ASM-001", "ASM-002", "ASM-007"] # ASM-007 is BKM
    res_circ = mgr.validate_assumption_set(circular_set, target_goal="GLOBAL_REGULARITY")
    assert res_circ["valid"] is False
    assert res_circ["is_circular_for_target"] is True
    assert res_circ["verdict"] == "CIRCULAR_FOR_GLOBAL_REGULARITY"
    assert len(res_circ["circularity_reasons"]) > 0


def test_claim_passport_multidimensional_validation():
    """Verify that all 10 independent dimensions of the Claim Passport are enforced."""
    mgr = ClaimManager()
    assert len(mgr.claims) >= 10

    # Test valid claim passport
    clm4 = mgr.get_claim("CLM-004")
    assert clm4 is not None
    passport = clm4["passport"]
    check = mgr.validate_passport(passport)
    assert check["valid"] is True
    assert len(check["missing_dimensions"]) == 0

    # Test incomplete passport missing dimensions
    incomplete_passport = {
        "truth_status": "PROVED_THEOREM",
        "project_status": "PROJECT_CANONICAL"
    }
    check_bad = mgr.validate_passport(incomplete_passport)
    assert check_bad["valid"] is False
    assert len(check_bad["missing_dimensions"]) > 0


def test_dependency_dag_cycle_detection_and_lineage():
    """Verify DAG integrity, absence of cycles, and correct ancestor queries."""
    graph_mgr = DependencyGraphManager()
    assert len(graph_mgr.nodes) >= 10
    assert len(graph_mgr.edges) >= 10

    # Check that repository DAG has no cycles
    cycles = graph_mgr.detect_cycles()
    assert len(cycles) == 0

    # Check ancestors of CLM-011 (Relative QV density)
    ancestors = graph_mgr.get_all_ancestors("CLM-011")
    assert "CLM-001" in ancestors
    assert "CLM-003" in ancestors
    assert "CLM-004" in ancestors
    assert "ASM-001" in ancestors


def test_promotion_state_machine_prohibits_illegal_jumps():
    """Verify that lifecycle transitions enforce step-by-step verification."""
    # Test valid progression
    p1 = PromotionManager.validate_transition("IDEA", "HYPOTHESIS", {})
    assert p1["allowed"] is True

    # Test illegal jump skipping verification
    p_bad = PromotionManager.validate_transition("IDEA", "PROJECT_CANONICAL", {})
    assert p_bad["allowed"] is False

    # Test PROJECT_CANONICAL promotion requiring all prerequisites
    p_canonical_missing = PromotionManager.validate_transition(
        "NOVELTY_CHECKED", "PROJECT_CANONICAL",
        {"e3_reproducible": True, "e4_verified": True, "understanding_package": False, "novelty_checked": True}
    )
    assert p_canonical_missing["allowed"] is False

    p_canonical_good = PromotionManager.validate_transition(
        "NOVELTY_CHECKED", "PROJECT_CANONICAL",
        {"e3_reproducible": True, "e4_verified": True, "understanding_package": True, "novelty_checked": True}
    )
    assert p_canonical_good["allowed"] is True


def test_understanding_packages_three_levels():
    """Verify 3-level understanding package completeness."""
    und_mgr = UnderstandingManager()
    check = und_mgr.validate_understanding_package("CLM-004")
    assert check["complete"] is True
    assert check["has_level_1"] is True
    assert check["has_level_2"] is True
    assert check["has_level_3"] is True


def test_novelty_register_audit():
    """Verify novelty classification and literature cross-reference audit."""
    nov_mgr = NoveltyManager()
    check1 = nov_mgr.validate_novelty_record("CLM-001")
    assert check1["valid"] is True
    assert check1["novelty_tier"] == "N0_KNOWN_FOUNDATION"

    check11 = nov_mgr.validate_novelty_record("CLM-011")
    assert check11["valid"] is True
    assert check11["novelty_tier"] == "N2_NOT_FOUND_IN_LITERATURE"


def test_full_mathematical_assurance_engine_audit():
    """Verify that the master assurance engine passes the entire repository audit."""
    engine = MathAssuranceEngine()
    audit_res = engine.run_full_assurance_audit()
    assert audit_res["overall_assurance_passed"] is True
    assert audit_res["dag_cycles_count"] == 0
    assert audit_res["invalid_passports_count"] == 0
    assert audit_res["canonical_deficiencies_count"] == 0
    assert audit_res["verdict"] == "MATHEMATICAL_ASSURANCE_VALID"
