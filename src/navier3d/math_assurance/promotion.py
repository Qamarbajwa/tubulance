"""Claim promotion gate and lifecycle transition validator."""
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

        # Prohibit skipping forward more than valid logical steps without required evidence
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
