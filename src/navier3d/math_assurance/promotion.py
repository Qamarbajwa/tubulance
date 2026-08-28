"""Claim promotion gate, lifecycle transition validator, and SOLVED eligibility engine."""
from typing import Dict, List, Any, Optional

LIFECYCLE_STAGES = [
    "IDEA",
    "HYPOTHESIS",
    "SUPPORTED_HYPOTHESIS",
    "CANDIDATE_LEMMA",
    "CANDIDATE_THEOREM",
    "INTERNALLY_DERIVED",
    "E3_REPRODUCIBLE",
    "E4_INDEPENDENTLY_VERIFIED",
    "FORMALLY_VERIFIED",
    "HUMAN_UNDERSTOOD",
    "NOVELTY_CHECKED",
    "PROJECT_CANONICAL",
    "EXTERNAL_EXPERT_VALIDATED",
    "COMMUNITY_ACCEPTED",
    "FIELD_CANONICALIZED"
]

STAGE_RANKS = {stage: i for i, stage in enumerate(LIFECYCLE_STAGES)}


class PromotionManager:
    @staticmethod
    def validate_transition(current_stage: str, next_stage: str, prerequisites: Dict[str, bool]) -> Dict[str, Any]:
        """Validate whether a claim transition from current_stage to next_stage is epistemically sound."""
        if current_stage not in STAGE_RANKS:
            return {"allowed": False, "reason": f"Unknown current stage: {current_stage}"}
        if next_stage not in STAGE_RANKS:
            return {"allowed": False, "reason": f"Unknown next stage: {next_stage}"}

        curr_rank = STAGE_RANKS[current_stage]
        next_rank = STAGE_RANKS[next_stage]

        if next_rank > curr_rank + 2 and next_stage not in ["FORMALLY_VERIFIED", "HUMAN_UNDERSTOOD"]:
            return {
                "allowed": False,
                "reason": f"Illegal jump from {current_stage} to {next_stage}. Lifecycle states cannot be bypassed."
            }

        # Check stage-specific prerequisites
        if next_stage == "PROJECT_CANONICAL":
            required_checks = ["e3_reproducible", "e4_verified", "understanding_package", "novelty_checked"]
            missing_checks = [chk for chk in required_checks if not prerequisites.get(chk, False)]
            if missing_checks:
                return {
                    "allowed": False,
                    "reason": f"Cannot promote to PROJECT_CANONICAL. Missing required prerequisites: {missing_checks}"
                }

        if next_stage in ["COMMUNITY_ACCEPTED", "FIELD_CANONICALIZED"]:
            required_checks = ["external_expert_validated", "community_accepted"]
            missing_checks = [chk for chk in required_checks if not prerequisites.get(chk, False)]
            if missing_checks:
                return {
                    "allowed": False,
                    "reason": f"Cannot promote to {next_stage}. Missing external validation prerequisites: {missing_checks}"
                }

        return {"allowed": True, "reason": "Transition valid under Mathematical Research Constitution."}

    @staticmethod
    def validate_solved_eligibility(
        claim_id: str,
        target_equivalence: bool,
        truth_status: str,
        assumption_drift: str,
        dependency_closure: bool,
        formalization_fidelity: bool,
        math_independence: str,
        external_validation: str,
        community_status: str
    ) -> Dict[str, Any]:
        """Strictly evaluate whether a claim is eligible to trigger SOLVED status."""
        # 1. Claim ID must be the primary locked problem
        if claim_id != "MILLENNIUM_NS_3D_TORUS":
            return {
                "solved_eligible": False,
                "verdict": "SUBTHEOREM_CANNOT_BE_SOLVED_ELIGIBLE",
                "reason": f"Claim ID '{claim_id}' is a subtheorem/lemma/counterexample, not the primary locked problem 'MILLENNIUM_NS_3D_TORUS'."
            }

        # 2. Target Equivalence must pass
        if not target_equivalence:
            return {
                "solved_eligible": False,
                "verdict": "TARGET_EQUIVALENCE_FAILED",
                "reason": "Claimed result solves a proxy or conditional sub-problem, not the primary target."
            }

        # 3. Truth status
        if truth_status != "PROVED_TARGET":
            return {
                "solved_eligible": False,
                "verdict": "TRUTH_STATUS_INSUFFICIENT",
                "reason": f"Truth status is '{truth_status}', expected 'PROVED_TARGET'."
            }

        # 4. Assumption drift
        if assumption_drift != "NONE":
            return {
                "solved_eligible": False,
                "verdict": "ASSUMPTION_DRIFT_DETECTED",
                "reason": f"Unearned higher-regularity assumptions present: {assumption_drift}."
            }

        # 5. Dependency closure
        if not dependency_closure:
            return {
                "solved_eligible": False,
                "verdict": "DEPENDENCY_CLOSURE_INCOMPLETE",
                "reason": "Prerequisite dependency nodes remain unverified."
            }

        # 6. Independence level
        if math_independence != "MATH_I4_HUMAN_SPECIALIST":
            return {
                "solved_eligible": False,
                "verdict": "INDEPENDENCE_INSUFFICIENT",
                "reason": f"Independence level is '{math_independence}', requires 'MATH_I4_HUMAN_SPECIALIST'."
            }

        # 7. External validation & Community status
        if external_validation not in ["MULTI_SPECIALIST_REVIEWED", "PUBLIC_SCRUTINY"]:
            return {
                "solved_eligible": False,
                "verdict": "EXTERNAL_VALIDATION_INSUFFICIENT",
                "reason": f"External validation is '{external_validation}', requires 'MULTI_SPECIALIST_REVIEWED' or 'PUBLIC_SCRUTINY'."
            }

        if community_status != "COMMUNITY_ACCEPTED":
            return {
                "solved_eligible": False,
                "verdict": "COMMUNITY_STATUS_INSUFFICIENT",
                "reason": f"Community status is '{community_status}', requires 'COMMUNITY_ACCEPTED'."
            }

        return {
            "solved_eligible": True,
            "verdict": "SOLVED_ELIGIBLE_RATIFIED",
            "reason": "All 8 constitutional criteria for Millennium target resolution satisfied."
        }
