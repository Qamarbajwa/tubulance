"""Machine-Derived Scientific Status Transition Pipeline.

Implements Sections 42, 43 of Milestone V2 and Milestone V2.2.
"""
from __future__ import annotations

from typing import Dict, Any, List

VALID_STATUSES = [
    "NOT_RUN",
    "RUN_FAILED",
    "EVIDENCE_CAPTURED",
    "VERIFICATION_FAILED",
    "TECHNICALLY_VERIFIED",
    "EXTERNALLY_ATTESTED",
    "REPLICATED",
    "SCIENTIFICALLY_ACCEPTED",
]

TRUST_LEVEL_MAP = {
    "NOT_RUN": "LEVEL 0 - NARRATED",
    "RUN_FAILED": "LEVEL 0 - NARRATED",
    "VERIFICATION_FAILED": "LEVEL 0 - NARRATED",
    "EVIDENCE_CAPTURED": "LEVEL 1 - EVIDENCE CAPTURED",
    "TECHNICALLY_VERIFIED": "LEVEL 2 - TECHNICALLY VERIFIED",
    "EXTERNALLY_ATTESTED": "LEVEL 3 - EXTERNALLY ATTESTED",
    "REPLICATED": "LEVEL 4 - INDEPENDENTLY REPLICATED",
    "SCIENTIFICALLY_ACCEPTED": "LEVEL 4 - INDEPENDENTLY REPLICATED",
}



class StatusMachine:
    """Controls machine-derived scientific status transitions."""

    def __init__(self, initial_status: str = "NOT_RUN"):
        if initial_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{initial_status}'")
        self.status = initial_status

    def get_trust_level(self) -> str:
        """Return the current formal scientific trust level."""
        return TRUST_LEVEL_MAP.get(self.status, "LEVEL 0 - NARRATED")

    def promote(self, gate: str, passed: bool, details: Dict[str, Any] = None, trust_mode: str = "DEVELOPMENT_ONLY") -> str:
        """Promote scientific status through machine gates. Halts on failure."""
        if not passed:
            if gate in ("hash", "oracle", "claim"):
                self.status = "VERIFICATION_FAILED"
            else:
                self.status = "RUN_FAILED"
            return self.status

        transitions = {
            "run_completed": "EVIDENCE_CAPTURED",
            "hash_valid": "EVIDENCE_CAPTURED",
            "verifier_valid": "TECHNICALLY_VERIFIED",
            "signature_valid": "EXTERNALLY_ATTESTED",
            "replication_valid": "SCIENTIFICALLY_ACCEPTED",
        }

        if gate in transitions:
            if gate == "signature_valid" and trust_mode == "DEVELOPMENT_ONLY":
                self.status = "TECHNICALLY_VERIFIED"
            elif gate == "signature_valid" and trust_mode != "PRODUCTION":
                self.status = "TECHNICALLY_VERIFIED" # Capped unless production
            else:
                self.status = transitions[gate]

        return self.status
