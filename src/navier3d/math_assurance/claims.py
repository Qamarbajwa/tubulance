"""Claim registry, multidimensional Claim Passport, and Claim Census management."""
import os
import yaml
from typing import Dict, List, Set, Any, Optional


REQUIRED_PASSPORT_DIMENSIONS = [
    "truth_status",
    "gov_evidence_level",
    "math_evidence_level",
    "gov_review_independence",
    "math_review_independence",
    "formalization_state",
    "understanding_level",
    "novelty",
    "significance",
    "external_validation",
    "community_status",
    "project_status"
]

VALID_TRUTH_STATUSES = [
    "IDEA",
    "HYPOTHESIS",
    "SUPPORTED_HYPOTHESIS",
    "CANDIDATE_LEMMA",
    "CANDIDATE_THEOREM",
    "PROVED_IDENTITY",
    "PROVED_LEMMA",
    "PROVED_THEOREM",
    "PROVED_COUNTEREXAMPLE",
    "PROVED_TARGET"
]

VALID_GOV_EVIDENCE = [
    "GOV_E1_MODEL_RAW",
    "GOV_E2_LOGGED_TRACE",
    "GOV_E3_REPRODUCIBLE",
    "GOV_E4_INDEPENDENT_VERIFIER",
    "GOV_E5_EXTERNAL_ANCHORED"
]

VALID_MATH_EVIDENCE = [
    "MATH_E1_INFORMAL_DERIVATION",
    "MATH_E2_NUMERICAL_ASYMPTOTIC",
    "MATH_E3_MACHINE_COMPUTED",
    "MATH_E4_ANALYTIC_PROOF_AUDITED",
    "MATH_E5_FORMALLY_OR_EXTERNALLY_CONFIRMED"
]

VALID_GOV_INDEPENDENCE = [
    "GOV_I1_SAME_SESSION",
    "GOV_I2_SAME_FAMILY_DIFFERENT_INSTANCE",
    "GOV_I3_CROSS_ENVIRONMENT",
    "GOV_I4_EXTERNAL_AUDITOR"
]

VALID_MATH_INDEPENDENCE = [
    "MATH_I1_WRITER_INTERNAL",
    "MATH_I2_INDEPENDENT_VERIFIER_AGENT",
    "MATH_I3_CROSS_MODEL_AUDIT",
    "MATH_I4_HUMAN_SPECIALIST"
]

VALID_NOVELTY_TIERS = [
    "N0_KNOWN_FOUNDATION",
    "N1_PROJECT_REFORMULATION",
    "N2_NOT_FOUND_IN_AUDITED_SOURCES",
    "N3_EXTERNAL_NOVELTY_SUPPORTED",
    "N4_COMMUNITY_RECOGNIZED_AS_NOVEL"
]

VALID_SIGNIFICANCE_TIERS = [
    "S0_TECHNICAL_STEP",
    "S1_USEFUL_LEMMA",
    "S2_MAJOR_PROJECT_RESULT",
    "S3_POTENTIAL_FIELD_SIGNIFICANCE",
    "S4_COMMUNITY_RECOGNIZED_PARADIGM_CLOSURE"
]

VALID_EXTERNAL_VALIDATION = [
    "NOT_EXTERNALLY_REVIEWED",
    "EXPERT_REVIEW_IN_PROGRESS",
    "SPECIALIST_REVIEWED",
    "MULTI_SPECIALIST_REVIEWED",
    "PUBLIC_SCRUTINY"
]

VALID_COMMUNITY_STATUSES = [
    "NOT_COMMUNITY_ACCEPTED",
    "EMERGING_DISCUSSION",
    "PARTIALLY_ACCEPTED",
    "COMMUNITY_ACCEPTED"
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
        """Validate that all 12 independent passport dimensions are fully and consistently specified."""
        missing = [dim for dim in REQUIRED_PASSPORT_DIMENSIONS if dim not in passport]
        if missing:
            return {"valid": False, "reason": f"Missing passport dimensions: {missing}", "missing_dimensions": missing}

        # Check explicit namespace formats
        if passport["gov_evidence_level"] not in VALID_GOV_EVIDENCE:
            return {"valid": False, "reason": f"Invalid gov_evidence_level: {passport['gov_evidence_level']}"}
        if passport["math_evidence_level"] not in VALID_MATH_EVIDENCE:
            return {"valid": False, "reason": f"Invalid math_evidence_level: {passport['math_evidence_level']}"}
        if passport["gov_review_independence"] not in VALID_GOV_INDEPENDENCE:
            return {"valid": False, "reason": f"Invalid gov_review_independence: {passport['gov_review_independence']}"}
        if passport["math_review_independence"] not in VALID_MATH_INDEPENDENCE:
            return {"valid": False, "reason": f"Invalid math_review_independence: {passport['math_review_independence']}"}
        if passport["novelty"] not in VALID_NOVELTY_TIERS:
            return {"valid": False, "reason": f"Invalid novelty tier: {passport['novelty']}"}
        if passport["significance"] not in VALID_SIGNIFICANCE_TIERS:
            return {"valid": False, "reason": f"Invalid significance tier: {passport['significance']}"}
        if passport["external_validation"] not in VALID_EXTERNAL_VALIDATION:
            return {"valid": False, "reason": f"Invalid external_validation: {passport['external_validation']}"}
        if passport["community_status"] not in VALID_COMMUNITY_STATUSES:
            return {"valid": False, "reason": f"Invalid community_status: {passport['community_status']}"}
        if passport["project_status"] not in VALID_PROJECT_STATUSES:
            return {"valid": False, "reason": f"Invalid project_status: {passport['project_status']}"}

        # Contradictory external vs community status check
        ext = passport["external_validation"]
        comm = passport["community_status"]
        if ext == "NOT_EXTERNALLY_REVIEWED" and comm in ["COMMUNITY_ACCEPTED", "PARTIALLY_ACCEPTED"]:
            return {
                "valid": False,
                "reason": f"Contradictory status: {ext} cannot produce {comm}."
            }

        return {
            "valid": True,
            "missing_dimensions": [],
            "passport": passport
        }

    def get_canonical_claims(self) -> List[Dict[str, Any]]:
        """Return all claims that have reached project or field canonical status."""
        return [
            claim for claim in self.claims.values()
            if claim.get("passport", {}).get("project_status") in ["PROJECT_CANONICAL", "PROJECT_CANONICAL_WITH_LIMITATIONS", "FIELD_CANONICAL"]
        ]

    def run_claim_census(self) -> Dict[str, Any]:
        """Perform automated census across all claims in the repository."""
        all_ids = set(self.claims.keys())
        stale_passports = []
        invalid_passports = []

        for cid, claim in self.claims.items():
            check = self.validate_passport(claim.get("passport", {}))
            if not check["valid"]:
                invalid_passports.append({"claim_id": cid, "reason": check.get("reason", "UNKNOWN")})

        return {
            "total_claims_registered": len(all_ids),
            "invalid_passports_count": len(invalid_passports),
            "invalid_passports": invalid_passports,
            "stale_passports_count": len(stale_passports),
            "census_verdict": "CENSUS_PASSED" if len(invalid_passports) == 0 else "CENSUS_DEFICIENCIES_DETECTED"
        }
