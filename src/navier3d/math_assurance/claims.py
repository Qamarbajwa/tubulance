"""Claim registry and multidimensional Claim Passport management."""
import os
import yaml
from typing import Dict, List, Any, Optional


REQUIRED_PASSPORT_DIMENSIONS = [
    "truth_status",
    "evidence_strength",
    "independence_level",
    "formalization_state",
    "understanding_level",
    "novelty",
    "significance",
    "external_validation",
    "community_status",
    "project_status"
]

VALID_PROJECT_STATUSES = [
    "CANDIDATE",
    "PROJECT_CANONICAL_WITH_LIMITATIONS",
    "PROJECT_CANONICAL",
    "FIELD_CANONICAL"
]


class ClaimManager:
    def __init__(self, constitution_dir: Optional[str] = None):
        if constitution_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            constitution_dir = os.path.join(base_dir, "mathematical_constitution")
        self.constitution_dir = constitution_dir
        self.claims_file = os.path.join(constitution_dir, "CLAIM_REGISTRY.yaml")
        self.claims = self._load_claims()

    def _load_claims(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.claims_file):
            return {}
        with open(self.claims_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return {item["claim_id"]: item for item in data.get("claims", [])}

    def get_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        return self.claims.get(claim_id)

    def validate_passport(self, passport: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all 10 independent passport dimensions are fully specified."""
        missing = [dim for dim in REQUIRED_PASSPORT_DIMENSIONS if dim not in passport]
        project_status = passport.get("project_status", "")
        valid_status = project_status in VALID_PROJECT_STATUSES

        return {
            "valid": len(missing) == 0 and valid_status,
            "missing_dimensions": missing,
            "project_status_valid": valid_status,
            "passport": passport
        }

    def get_canonical_claims(self) -> List[Dict[str, Any]]:
        """Return all claims that have reached project or field canonical status."""
        return [
            claim for claim in self.claims.values()
            if claim.get("passport", {}).get("project_status") in ["PROJECT_CANONICAL", "PROJECT_CANONICAL_WITH_LIMITATIONS", "FIELD_CANONICAL"]
        ]
