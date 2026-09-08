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

    @staticmethod
    def validate_evidence_promotion(
        claimed_dimension: str,
        independence: str,
        has_independent_verifier: bool
    ) -> bool:
        """Ensure evidence strength cannot be promoted without qualified independent verification."""
        if claimed_dimension in ("E4", "E5"):
            if independence in ("IND0", "MATH_I1") or not has_independent_verifier:
                raise GovernanceStateError(
                    f"Unsupported evidence promotion: Cannot claim {claimed_dimension} "
                    f"under {independence} without independent verifier."
                )
        return True

    @staticmethod
    def validate_independence_namespace(domain: str, independence_code: str) -> bool:
        """Ensure strict separation of operational (IND0-IND3) vs mathematical (MATH_I1-MATH_I4) namespaces."""
        if domain.upper() == "GOVERNANCE":
            if independence_code.startswith("MATH_I"):
                raise GovernanceStateError(
                    f"Invalid namespace in governance domain: '{independence_code}'. "
                    f"Operational evidence must use IND0-IND3."
                )
        elif domain.upper() == "MATHEMATICS":
            if independence_code.startswith("IND"):
                raise GovernanceStateError(
                    f"Invalid namespace in mathematical domain: '{independence_code}'. "
                    f"Mathematical claim passports must use MATH_I1-MATH_I4."
                )
        return True

    @staticmethod
    def validate_rollback_scope(
        target_files_to_revert: list[str | Path],
        migration_owned_files: set[str | Path]
    ) -> bool:
        """Prevent rollback from deleting pre-existing scientific state or historical records."""
        migration_owned_normalized = {Path(p).as_posix().lower() for p in migration_owned_files}
        for f in target_files_to_revert:
            norm_f = Path(f).as_posix().lower()
            if norm_f not in migration_owned_normalized:
                raise GovernanceStateError(
                    f"Rollback safety violation: Attempted to delete or revert pre-existing "
                    f"scientific file '{f}' not owned by this migration."
                )
        return True

    @staticmethod
    def validate_mandatory_authorities(gov_dir: Path | str) -> bool:
        """Verify that all 3 mandatory v4.0.3 authority files exist."""
        p = Path(gov_dir)
        required = ["GOVERNANCE.md", "PROJECT_DIRECTION.md", "PROJECT_STATE.yaml"]
        missing = [f for f in required if not (p / f).exists()]
        if missing:
            raise GovernanceStateError(
                f"Missing mandatory authority file(s): {missing}. All 3 operational authorities must exist."
            )
        return True

    @staticmethod
    def validate_governance_version(version_str: str) -> bool:
        """Reject conflicting governance version declarations."""
        expected = "4.0.3"
        if version_str.strip() != expected:
            raise GovernanceStateError(
                f"Conflicting governance version: '{version_str}'. Expected '{expected}'."
            )
        return True

    @staticmethod
    def validate_single_state_owner(declarations: list[dict[str, Any]]) -> bool:
        """Reject duplicate or conflicting live state owner declarations."""
        active_owners = [
            d for d in declarations
            if d.get("role") == "PRIMARY_LIVE_STATE" and d.get("status") == "ACTIVE"
        ]
        if len(active_owners) > 1:
            owner_files = [d.get("file") for d in active_owners]
            raise GovernanceStateError(
                f"Duplicate state owner detected: Multiple files claim PRIMARY_LIVE_STATE: {owner_files}."
            )
        if len(active_owners) == 0:
            raise GovernanceStateError("No active PRIMARY_LIVE_STATE owner declared.")
        return True

    @staticmethod
    def validate_evidence_freshness(evidence_candidate_id: str, current_candidate_id: str) -> bool:
        """Reject stale evidence tied to an older or different candidate SHA."""
        if not evidence_candidate_id or not current_candidate_id:
            raise GovernanceStateError("Evidence and current candidate IDs cannot be empty.")
        if evidence_candidate_id.strip() != current_candidate_id.strip():
            raise GovernanceStateError(
                f"Stale evidence detected: Evidence was produced for candidate '{evidence_candidate_id}', "
                f"but active candidate is '{current_candidate_id}'."
            )
        return True

    @staticmethod
    def validate_mathematical_promotion(is_technical_pass: bool, has_analytic_passport: bool) -> bool:
        """Enforce that technical test/code PASS cannot promote a mathematical claim without analytic proof passport."""
        if is_technical_pass and not has_analytic_passport:
            raise GovernanceStateError(
                "Epistemic category error: Technical/test PASS cannot promote mathematical claim status "
                "without audited analytic proof passport (MRC v1.0.1)."
            )
        return True

    @staticmethod
    def validate_target_problem_status(status: str) -> bool:
        """Enforce project invariant: Clay Statement B must remain UNRESOLVED."""
        if status.strip().upper() != "UNRESOLVED":
            raise GovernanceStateError(
                f"Epistemic invariant violation: Clay Statement B status cannot be set to '{status}'. "
                f"Must strictly remain 'UNRESOLVED'."
            )
        return True

