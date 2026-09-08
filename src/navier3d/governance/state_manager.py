"""Universal Governance Minimal v4.0.3 State Manager and Serialization Engine.

Implements machine-enforced revision compare-and-swap, state schema validation,
anti-self-acceptance, candidate binding, and epistemic invariant checking.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import yaml


class GovernanceStateError(Exception):
    """Base exception for governance state errors."""
    pass


class StaleRevisionError(GovernanceStateError):
    """Raised when an update attempts to overwrite a newer state revision."""
    pass


class SelfAcceptanceError(GovernanceStateError):
    """Raised when a writer attempts to review or accept its own work."""
    pass


class CandidateMismatchError(GovernanceStateError):
    """Raised when acceptance candidate does not match reviewed candidate."""
    pass


class UnboundStateError(GovernanceStateError):
    """Raised when an operation attempts to run against an UNBOUND state template."""
    pass


class GovernanceStateManager:
    """Manages reading, validating, and atomically updating v4.0.3 project state."""

    def __init__(self, state_path: Optional[str | Path] = None):
        if state_path is None:
            base_dir = Path(__file__).resolve().parents[3]
            state_path = base_dir / "governance" / "PROJECT_STATE.yaml"
        self.state_path = Path(state_path)

    def load_state(self) -> Dict[str, Any]:
        """Load state YAML from disk."""
        if not self.state_path.exists():
            raise FileNotFoundError(f"Governance state file not found: {self.state_path}")
        with open(self.state_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def validate_state(self, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate core v4.0.3 state invariants."""
        if state is None:
            state = self.load_state()

        # 1. Reject UNBOUND template
        activation = state.get("activation")
        if activation == "UNBOUND" or not activation:
            raise UnboundStateError("State template is UNBOUND; cannot authorize project work.")

        # 2. Check schema version
        schema_version = state.get("schema_version")
        if schema_version != "4.0.3":
            raise GovernanceStateError(f"Unsupported schema version: {schema_version}; expected '4.0.3'")

        # 3. Check revision integer
        revision = state.get("revision")
        if not isinstance(revision, int) or revision < 1:
            raise GovernanceStateError(f"Invalid revision number: {revision}; must be integer >= 1")

        # 4. Check project binding
        project = state.get("project", {})
        if project.get("id") != "tubulance":
            raise GovernanceStateError(f"Invalid project id: {project.get('id')}; expected 'tubulance'")

        # 5. Check epistemic invariant: Clay Statement B remains UNRESOLVED
        epistemic = state.get("epistemic_status", {})
        if epistemic.get("clay_statement_b_status") != "UNRESOLVED":
            raise GovernanceStateError("Violation of core invariant: clay_statement_b_status must be 'UNRESOLVED'")

        # 6. Check release boundary: NO-GO
        release = state.get("release", {})
        if release.get("state") != "NO-GO" or release.get("eligible") is True or release.get("deployment_authorized") is True:
            raise GovernanceStateError("Violation of release boundary: release.state must be 'NO-GO'")

        # 7. Check hard gates
        hard_gates = state.get("hard_gates", {})
        required_gates = [
            "clay_statement_b_unresolved",
            "dag_cycle_count",
            "claim_passport_census",
            "negative_evidence_retention",
            "writer_anti_self_acceptance"
        ]
        missing_gates = [g for g in required_gates if g not in hard_gates]
        if missing_gates:
            raise GovernanceStateError(f"Missing required hard gates in state: {missing_gates}")

        return {"valid": True, "revision": revision, "activation": activation}

    def update_state(
        self,
        expected_revision: int,
        update_fn: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Atomically update state using compare-and-swap on the revision integer."""
        current_state = self.load_state()
        actual_revision = current_state.get("revision", 0)

        if actual_revision != expected_revision:
            raise StaleRevisionError(
                f"Concurrent state modification detected. Expected revision {expected_revision}, "
                f"but found actual revision {actual_revision}."
            )

        # Apply update transformation
        updated_state = update_fn(current_state)

        # Increment revision and record update timestamp
        updated_state["revision"] = actual_revision + 1
        coordination = updated_state.setdefault("coordination", {})
        coordination["last_expected_revision"] = actual_revision
        coordination["last_updated_at"] = datetime.now(timezone.utc).isoformat()

        # Validate updated state before persisting
        self.validate_state(updated_state)

        # Write to disk
        with open(self.state_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(updated_state, f, sort_keys=False)

        return updated_state

    @staticmethod
    def validate_review_and_acceptance(
        writer: str,
        reviewer: str,
        acceptor: str
    ) -> bool:
        """Enforce strict role separation: Writer != Reviewer and Writer != Acceptor."""
        if not writer or not reviewer or not acceptor:
            raise GovernanceStateError("Writer, Reviewer, and Acceptor must all be explicitly defined.")

        if writer.strip().lower() == reviewer.strip().lower():
            raise SelfAcceptanceError(
                f"Anti-Self-Acceptance Violation: Writer '{writer}' cannot act as independent reviewer."
            )

        if writer.strip().lower() == acceptor.strip().lower():
            raise SelfAcceptanceError(
                f"Anti-Self-Acceptance Violation: Writer '{writer}' cannot act as acceptance authority."
            )

        return True

    @staticmethod
    def validate_candidate_match(candidate_id: str, review_candidate_id: str) -> bool:
        """Enforce exact candidate matching between review and acceptance."""
        if not candidate_id or not review_candidate_id:
            raise CandidateMismatchError("Candidate IDs cannot be empty.")

        if candidate_id.strip() != review_candidate_id.strip():
            raise CandidateMismatchError(
                f"Candidate Mismatch: Review observed candidate '{review_candidate_id}', "
                f"which does not match acceptance candidate '{candidate_id}'."
            )

        return True
