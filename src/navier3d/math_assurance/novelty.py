"""Novelty register and literature cross-referencing manager."""
import os
import yaml
from typing import Dict, List, Any, Optional


VALID_NOVELTY_TIERS = [
    "N0_KNOWN_FOUNDATION",
    "N1_PROJECT_REFORMULATION",
    "N2_NOT_FOUND_IN_LITERATURE",
    "N3_FUNDAMENTALLY_NOVEL"
]


class NoveltyManager:
    def __init__(self, constitution_dir: Optional[str] = None):
        if constitution_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            constitution_dir = os.path.join(base_dir, "mathematical_constitution")
        self.constitution_dir = constitution_dir
        self.novelty_file = os.path.join(constitution_dir, "NOVELTY_REGISTER.yaml")
        self.records = self._load_records()

    def _load_records(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.novelty_file):
            return {}
        with open(self.novelty_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return {item["claim_id"]: item for item in data.get("novelty_records", [])}

    def validate_novelty_record(self, claim_id: str) -> Dict[str, Any]:
        """Verify that novelty tier and literature audit are well-formed."""
        rec = self.records.get(claim_id)
        if not rec:
            return {"valid": False, "reason": f"No novelty record found for claim {claim_id}"}

        tier = rec.get("novelty_tier", "")
        is_valid_tier = tier in VALID_NOVELTY_TIERS
        has_justification = bool(rec.get("justification", "").strip())

        return {
            "valid": is_valid_tier and has_justification,
            "novelty_tier": tier,
            "has_justification": has_justification,
            "record": rec
        }
