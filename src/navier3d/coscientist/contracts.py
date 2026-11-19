"""Research Agent Contracts for 3D Navier-Stokes Co-Scientist OS.

Formalizes the inputs, outputs, invariants, and failure dispositions for the
six specialized scientific agents (Generation, Reflection, Proximity, Evolution,
Ranking, and Independent Verification) under COSCIENTIST_DF_v0_1 and
Google Drive Governance OS (Idea-to-Product OS Addendum v1.0 & Amendment v1.0).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from .kernel import digest, Hypothesis, Stage, VerificationReceipt


class EvolutionOperator(str, Enum):
    """Permitted hypothesis evolution operators (COSCIENTIST_DF_v0_1 §04)."""
    GROUND = "GROUND"
    CLARIFY = "CLARIFY"
    SIMPLIFY = "SIMPLIFY"
    COMBINE = "COMBINE"
    DIVERGE = "DIVERGE"
    TEST_REFINEMENT = "TEST_REFINEMENT"


@dataclass(frozen=True)
class KnowledgeGap:
    """Knowledge gap and assumption mapping record (Idea-to-Product OS Addendum v1.0 §4)."""
    gap_id: str
    affected_concept: str
    decision_blocked: str
    current_hypothesis: str
    confidence: float
    evidence_base: str
    impact_level: str  # "HIGH", "MEDIUM", "LOW"
    uncertainty_level: str  # "HIGH", "MEDIUM", "LOW"
    cheapest_discriminating_experiment: str
    status: str = "OPEN"  # "OPEN", "RESOLVED", "REJECTED", "ACCEPTED_RISK"


@dataclass(frozen=True)
class SocraticInversionContract:
    """Socratic inversion contract (Idea-to-Product OS Addendum v1.0 §2).

    Mandates explaining credible mathematical approaches, assumptions,
    trade-offs, and falsification tests before generating code or proofs.
    """
    topic: str
    credible_approaches: Tuple[str, ...]
    governing_assumptions: Tuple[str, ...]
    trade_offs: Tuple[str, ...]
    falsification_tests: Tuple[str, ...]
    key_unanswered_questions: Tuple[str, ...]  # Maximum 3 essential questions


@dataclass(frozen=True)
class GenerationContract:
    """Generation Agent contract (COSCIENTIST_DF_v0_1 §04).

    Produces well-formed candidate hypotheses with testable predictions,
    explicit assumptions, falsifiers, and citations.
    Cannot assert proven novelty or verified truth.
    """
    goal_id: str
    hypothesis_id: str
    statement: str
    assumptions: Tuple[str, ...]
    falsifiers: Tuple[str, ...]
    predictions: Tuple[str, ...]
    citations: Tuple[str, ...]
    mechanism: Optional[str] = None
    creator_role: str = "GENERATION_AGENT"

    def to_hypothesis(self) -> Hypothesis:
        return Hypothesis(
            hypothesis_id=self.hypothesis_id,
            statement=self.statement,
            content_digest=digest(self.statement),
            stage=Stage.DRAFT,
            assumptions=self.assumptions,
            falsifiers=self.falsifiers,
            citations=self.citations,
        )


@dataclass(frozen=True)
class ReflectionContract:
    """Reflection Agent contract (COSCIENTIST_DF_v0_1 §04).

    Evaluates hypotheses against known literature, structural obstructions,
    and negative evidence. Cannot self-admit candidates to tournament.
    """
    hypothesis_id: str
    target_digest: str
    review_type: str  # "INITIAL", "FULL_GROUNDED", "ASSUMPTION", "OBSERVATION", "COUNTEREXAMPLE"
    contradiction_found: bool
    governing_obstructions: Tuple[str, ...] = ()
    negative_evidence_refs: Tuple[str, ...] = ()
    flaws: Tuple[str, ...] = ()
    verdict: str = "PENDING"  # "ACCEPTABLE_FOR_GROUNDING", "FLAWED", "QUARANTINE_RECOMMENDED"


@dataclass(frozen=True)
class ProximityContract:
    """Proximity Agent contract (COSCIENTIST_DF_v0_1 §04).

    Maps structural and geometric similarity between candidate hypotheses
    and existing research pathways in the research memory registry.
    """
    hypothesis_id: str
    target_digest: str
    shared_tags: Tuple[str, ...] = ()
    shared_obstructions: Tuple[str, ...] = ()
    closest_pathway_ids: Tuple[str, ...] = ()
    similarity_score: float = 0.0


@dataclass(frozen=True)
class EvolutionContract:
    """Evolution Agent contract (COSCIENTIST_DF_v0_1 §04).

    Applies a mutation operator to parent hypotheses to create refined children.
    Resets all inherited verification, elo, and gate status (I-11).
    """
    parent_id: str
    parent_digest: str
    operator: EvolutionOperator
    child_id: str
    child_statement: str
    rationale: str
    new_assumptions: Tuple[str, ...] = ()
    new_falsifiers: Tuple[str, ...] = ()
    new_citations: Tuple[str, ...] = ()

    def to_child_hypothesis(self) -> Hypothesis:
        return Hypothesis(
            hypothesis_id=self.child_id,
            statement=self.child_statement,
            content_digest=digest(self.child_statement),
            parent_ids=(self.parent_id,),
            stage=Stage.DRAFT,
            assumptions=self.new_assumptions,
            falsifiers=self.new_falsifiers,
            citations=self.new_citations,
            elo=1200.0,
        )


@dataclass(frozen=True)
class TournamentContract:
    """Tournament / Ranking Agent contract (COSCIENTIST_DF_v0_1 §04).

    Conducts blinded A/B comparisons with order-swapping diagnostics.
    Cannot influence proof status (I-04).
    """
    match_id: str
    left_id: str
    right_id: str
    blind_label_a: str
    blind_label_b: str
    outcome: str  # "LEFT", "RIGHT", "TIE", "ABSTAIN"
    replicate_order_swapped_outcome: Optional[str] = None
    comparison_rationale: str = ""


@dataclass(frozen=True)
class IndependentVerificationContract:
    """Independent Verifier contract (COSCIENTIST_DF_v0_1 §04, Governance Amendment v1.0).

    Enforces strict separation of builder/author from verifier (I-06).
    Requires exact target digest matching (I-05), protected test execution,
    and authoritative verification receipts.
    """
    hypothesis_id: str
    exact_target_digest: str
    evidence_digest: str
    claim_type: str  # "MATH_PROOF" or "EMPIRICAL_REPLICATION"
    builder_identity: str
    verifier_identity: str
    protected_suite_cmd: str
    protected_suite_output: str
    protected_suite_passed: bool
    semantic_review_passed: bool
    verifier_authority_bound: bool

    def to_receipt(self) -> VerificationReceipt:
        if self.builder_identity == self.verifier_identity:
            raise ValueError("SELF_VERIFICATION_FORBIDDEN: Builder cannot act as its own verifier.")
        return VerificationReceipt(
            hypothesis_id=self.hypothesis_id,
            exact_target_digest=self.exact_target_digest,
            evidence_digest=self.evidence_digest,
            claim_type=self.claim_type,
            builder_identity=self.builder_identity,
            verifier_identity=self.verifier_identity,
            independently_verified=True,
            protected_suite_passed=self.protected_suite_passed,
            semantic_review_passed=self.semantic_review_passed,
            verifier_authority_bound=self.verifier_authority_bound,
        )
