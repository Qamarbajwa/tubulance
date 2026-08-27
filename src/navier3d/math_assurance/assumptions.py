"""Assumption management and automatic circularity / drift detection."""
import os
import yaml
from typing import Dict, List, Any, Optional


class AssumptionManager:
    def __init__(self, constitution_dir: Optional[str] = None):
        if constitution_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            constitution_dir = os.path.join(base_dir, "mathematical_constitution")
        self.constitution_dir = constitution_dir
        self.assumptions_file = os.path.join(constitution_dir, "ASSUMPTION_REGISTER.yaml")
        self.assumptions = self._load_assumptions()

    def _load_assumptions(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.assumptions_file):
            return {}
        with open(self.assumptions_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return {item["assumption_id"]: item for item in data.get("assumptions", [])}

    def get_assumption(self, assumption_id: str) -> Optional[Dict[str, Any]]:
        return self.assumptions.get(assumption_id)

    def validate_assumption_set(self, assumption_ids: List[str], target_goal: str = "GLOBAL_REGULARITY") -> Dict[str, Any]:
        """Check assumption set for validity, unearned hypotheses, and circularity."""
        missing = []
        prohibited = []
        unjustified = []
        foundational = []
        derived = []

        for aid in assumption_ids:
            asm = self.get_assumption(aid)
            if not asm:
                missing.append(aid)
                continue

            classification = asm.get("classification", "")
            if classification in ["FOUNDATIONAL", "KNOWN_CONSEQUENCE"]:
                foundational.append(aid)
            elif classification == "DERIVED":
                derived.append(aid)
            elif classification == "ADDITIONAL_PROHIBITED":
                prohibited.append(asm)
            elif classification == "UNJUSTIFIED":
                unjustified.append(asm)

        is_circular = False
        circularity_reasons = []

        if target_goal == "GLOBAL_REGULARITY":
            for p in prohibited:
                is_circular = True
                circularity_reasons.append(f"Prohibited assumption '{p['name']}' ({p['assumption_id']}): {p.get('circularity_flag', 'CIRCULAR')}")
            for u in unjustified:
                is_circular = True
                circularity_reasons.append(f"Unjustified a-priori assumption '{u['name']}' ({u['assumption_id']}): {u.get('circularity_flag', 'UNJUSTIFIED')}")

        return {
            "valid": len(missing) == 0 and not is_circular,
            "missing_ids": missing,
            "foundational_count": len(foundational),
            "derived_count": len(derived),
            "prohibited_count": len(prohibited),
            "unjustified_count": len(unjustified),
            "is_circular_for_target": is_circular,
            "circularity_reasons": circularity_reasons,
            "verdict": "CIRCULAR_FOR_GLOBAL_REGULARITY" if is_circular else ("INVALID_MISSING_IDS" if missing else "VALID_ASSUMPTIONS")
        }
