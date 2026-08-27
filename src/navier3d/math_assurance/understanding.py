"""Understanding package validator and manager."""
import os
import yaml
from typing import Dict, List, Any, Optional


class UnderstandingManager:
    def __init__(self, constitution_dir: Optional[str] = None):
        if constitution_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            constitution_dir = os.path.join(base_dir, "mathematical_constitution")
        self.constitution_dir = constitution_dir
        self.understanding_file = os.path.join(constitution_dir, "UNDERSTANDING_REGISTER.yaml")
        self.packages = self._load_packages()

    def _load_packages(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.understanding_file):
            return {}
        with open(self.understanding_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return {item["claim_id"]: item for item in data.get("understanding_packages", [])}

    def validate_understanding_package(self, claim_id: str) -> Dict[str, Any]:
        """Verify that Level 1, Level 2, and Level 3 understanding components are complete."""
        pkg = self.packages.get(claim_id)
        if not pkg:
            return {"complete": False, "reason": f"No understanding package found for claim {claim_id}"}

        has_l1 = bool(pkg.get("level_1_mechanism", "").strip())
        has_l2 = bool(pkg.get("level_2_architecture", "").strip())
        has_l3 = bool(pkg.get("level_3_rigorous_q_and_a", {}).get("why_it_works", "").strip())

        is_complete = has_l1 and has_l2 and has_l3
        return {
            "complete": is_complete,
            "has_level_1": has_l1,
            "has_level_2": has_l2,
            "has_level_3": has_l3,
            "package": pkg
        }
