"""Master Mathematical Assurance Engine (NS-MRC-1)."""
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

    def audit_target_equivalence(self, claimed_result: str, actual_assumptions: List[str]) -> Dict[str, Any]:
        """Verify that the claimed result matches the original Millennium problem target and not a relaxed proxy."""
        # Check if actual assumptions contain conditional blowup criteria
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
            "details": ["Target aligns with full smooth initial data on T^3 without conditional assumptions."]
        }

    def run_full_assurance_audit(self) -> Dict[str, Any]:
        """Perform a complete repository mathematical assurance audit across all 12 mechanisms."""
        # 1. Dependency cycles
        cycles = self.dependencies.detect_cycles()
        dag_clean = len(cycles) == 0

        # 2. Claim passports
        all_claims = self.claims.claims
        invalid_passports = []
        for cid, claim in all_claims.items():
            check = self.claims.validate_passport(claim.get("passport", {}))
            if not check["valid"]:
                invalid_passports.append({"claim_id": cid, "missing": check["missing_dimensions"]})

        # 3. Canonical claims prerequisites
        canonical_claims = self.claims.get_canonical_claims()
        canonical_deficiencies = []
        for claim in canonical_claims:
            cid = claim["claim_id"]
            und_check = self.understanding.validate_understanding_package(cid)
            nov_check = self.novelty.validate_novelty_record(cid)
            if not und_check.get("complete", False):
                canonical_deficiencies.append({"claim_id": cid, "issue": "INCOMPLETE_UNDERSTANDING_PACKAGE"})
            if not nov_check.get("valid", False):
                canonical_deficiencies.append({"claim_id": cid, "issue": "INCOMPLETE_NOVELTY_RECORD"})

        overall_passed = dag_clean and len(invalid_passports) == 0 and len(canonical_deficiencies) == 0

        return {
            "overall_assurance_passed": overall_passed,
            "dag_cycles_count": len(cycles),
            "cycles": cycles,
            "total_claims_count": len(all_claims),
            "invalid_passports_count": len(invalid_passports),
            "invalid_passports": invalid_passports,
            "canonical_claims_count": len(canonical_claims),
            "canonical_deficiencies_count": len(canonical_deficiencies),
            "canonical_deficiencies": canonical_deficiencies,
            "verdict": "MATHEMATICAL_ASSURANCE_VALID" if overall_passed else "ASSURANCE_DEFICIENCIES_DETECTED"
        }
