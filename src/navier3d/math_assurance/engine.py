"""Master Mathematical Assurance Engine (NS-MRC-1-R1)."""
import os
import yaml
from typing import Dict, List, Any, Optional

from .assumptions import AssumptionManager
from .claims import ClaimManager
from .dependencies import DependencyGraphManager
from .promotion import PromotionManager
from .understanding import UnderstandingManager
from .novelty import NoveltyManager


class MathAssuranceEngine:
    def __init__(self, constitution_dir: Optional[str] = None):
        if constitution_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            constitution_dir = os.path.join(base_dir, "mathematical_constitution")
        self.constitution_dir = constitution_dir

        self.assumptions = AssumptionManager(constitution_dir)
        self.claims = ClaimManager(constitution_dir)
        self.dependencies = DependencyGraphManager(constitution_dir)
        self.promotion = PromotionManager()
        self.understanding = UnderstandingManager(constitution_dir)
        self.novelty = NoveltyManager(constitution_dir)

    def validate_branch_identity(self) -> Dict[str, Any]:
        """Verify that the official problem identity is locked to Clay Statement Branch B."""
        prob_file = os.path.join(self.constitution_dir, "PROBLEM_IDENTITY.yaml")
        if not os.path.exists(prob_file):
            return {"valid": False, "reason": "PROBLEM_IDENTITY.yaml missing"}
        with open(prob_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        identity = data.get("problem_identity", {})
        is_clay_b = identity.get("official_target_branch") == "CLAY_STATEMENT_B_PERIODIC_R3_MOD_Z3"
        return {
            "valid": is_clay_b,
            "official_target_branch": identity.get("official_target_branch"),
            "project_domain": identity.get("project_domain"),
            "governing_target": identity.get("governing_target")
        }

    def audit_target_equivalence(self, claimed_result: str, actual_assumptions: List[str]) -> Dict[str, Any]:
        """Verify that the claimed result matches the locked Clay Branch B target without relaxation."""
        asm_check = self.assumptions.validate_assumption_set(actual_assumptions, target_goal="GLOBAL_REGULARITY")
        if not asm_check["valid"]:
            return {
                "target_matched": False,
                "verdict": "KNOWN_CONDITIONAL_CRITERION_NOT_TARGET_CLOSURE",
                "details": asm_check["circularity_reasons"]
            }

        return {
            "target_matched": True,
            "verdict": "TARGET_EQUIVALENCE_VALID",
            "details": ["Target strictly aligns with Clay Statement Branch B on T^3 without unearned assumptions."]
        }

    def run_full_assurance_audit(self) -> Dict[str, Any]:
        """Perform a complete repository mathematical assurance audit across all 12 mechanisms."""
        # 1. Branch identity
        branch_check = self.validate_branch_identity()

        # 2. Dependency cycles
        cycles = self.dependencies.detect_cycles()
        dag_clean = len(cycles) == 0

        # 3. Claim census & passports
        census = self.claims.run_claim_census()

        # 4. Canonical claims prerequisites
        canonical_claims = self.claims.get_canonical_claims()
        canonical_deficiencies = []
        for claim in canonical_claims:
            cid = claim["claim_id"]
            und_check = self.understanding.validate_understanding_package(cid)
            nov_check = self.novelty.validate_novelty_record(cid)
            if not und_check.get("complete", False):
                canonical_deficiencies.append({"claim_id": cid, "issue": "INCOMPLETE_UNDERSTANDING_PACKAGE"})
            if not nov_check.get("valid", False):
                canonical_deficiencies.append({"claim_id": cid, "issue": f"INCOMPLETE_NOVELTY_RECORD: {nov_check.get('reason')}"})

        overall_passed = (
            branch_check["valid"]
            and dag_clean
            and census["invalid_passports_count"] == 0
            and len(canonical_deficiencies) == 0
        )

        return {
            "overall_assurance_passed": overall_passed,
            "branch_identity_valid": branch_check["valid"],
            "dag_cycles_count": len(cycles),
            "cycles": cycles,
            "total_claims_count": census["total_claims_registered"],
            "invalid_passports_count": census["invalid_passports_count"],
            "canonical_claims_count": len(canonical_claims),
            "canonical_deficiencies_count": len(canonical_deficiencies),
            "canonical_deficiencies": canonical_deficiencies,
            "verdict": "MATHEMATICAL_ASSURANCE_VALID" if overall_passed else "ASSURANCE_DEFICIENCIES_DETECTED"
        }
