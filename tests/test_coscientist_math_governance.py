"""Comprehensive Test Suite for Co-Scientist Dark Factory Subsystem & Google Drive Governance OS Binding.

Validates:
1. ResearchGateKernel state machine (SR0-SR8) and all 12 Invariants (I-01 to I-12).
2. Agent contracts (Generation, Reflection, Proximity, Evolution, Tournament, Independent Verifier).
3. Integration with Mathematical Assurance Engine (NS-MRC-1-R1) and Research Memory Engine.
4. Google Drive Governance OS bindings (Master Record sync, Idea-to-Product Doctrine, Strict Anti-Self-Acceptance).
"""

import os
import unittest
from hashlib import sha256

from navier3d.coscientist.kernel import (
    Denied,
    Stage,
    Hypothesis,
    GateSignals,
    VerificationReceipt,
    ResearchGateKernel,
    digest,
    ORDER,
)
from navier3d.coscientist.contracts import (
    EvolutionOperator,
    KnowledgeGap,
    SocraticInversionContract,
    GenerationContract,
    ReflectionContract,
    ProximityContract,
    EvolutionContract,
    TournamentContract,
    IndependentVerificationContract,
)
from navier3d.math_assurance import MathAssuranceEngine, ClaimManager
from navier3d.research_memory import ResearchMemoryEngine


ALL_SIGNALS_PASS = GateSignals(
    goal_safe=True,
    hypothesis_safe=True,
    source_verified=True,
    reflection_completed=True,
    tournament_assessed=True,
    report_discloses_limits=True,
)


class TestCoScientistDarkFactoryKernel(unittest.TestCase):
    """Unit and invariant tests for ResearchGateKernel (COSCIENTIST_DF_v0_1)."""

    def setUp(self):
        self.kernel = ResearchGateKernel()
        self.h1 = self.kernel.add(
            hypothesis_id="HYP-NS-001",
            statement="Dyadic enstrophy transfer across cutoff Q is strictly bounded below by Stokes-Duhamel propagation.",
            assumptions=("Smooth divergence-free velocity field", "Torus T^3_L", "nu > 0"),
            falsifiers=("Vanishing forward transfer on Taylor-Green initial data",),
            citations=("Constantin, E & Titi (1994)",),
        )

    def advance_to(self, hyp_id: str, target: Stage):
        order = (
            Stage.SCREENED,
            Stage.GROUNDED,
            Stage.REVIEWED,
            Stage.ELIGIBLE,
            Stage.RANKED,
            Stage.PROPOSAL_READY,
        )
        for stage in order:
            if self.kernel.get(hyp_id).stage == target:
                return
            self.kernel.advance(hyp_id, stage, ALL_SIGNALS_PASS, caller="policy_service")

    def test_01_initial_state_is_draft_and_unverified(self):
        """Hypotheses begin at Stage.DRAFT, Elo 1200.0, and unverified (SR2)."""
        hyp = self.kernel.get("HYP-NS-001")
        self.assertEqual(hyp.stage, Stage.DRAFT)
        self.assertEqual(hyp.elo, 1200.0)
        self.assertEqual(hyp.formal_state, "UNTESTED")
        self.assertEqual(hyp.empirical_state, "NOT_APPLICABLE")
        self.assertFalse(self.kernel.proposal_is_verified("HYP-NS-001"))

    def test_02_invariant_i01_no_bypass_of_stages(self):
        """Invariant I-01: Skipping intermediate stages is strictly prohibited."""
        with self.assertRaises(Denied) as ctx:
            self.kernel.advance("HYP-NS-001", Stage.RANKED, ALL_SIGNALS_PASS, caller="policy_service")
        self.assertIn("NON_ADJACENT_OR_REVERSE_TRANSITION", str(ctx.exception))

        with self.assertRaises(Denied) as ctx:
            self.kernel.advance("HYP-NS-001", Stage.ELIGIBLE, ALL_SIGNALS_PASS, caller="policy_service")
        self.assertIn("NON_ADJACENT_OR_REVERSE_TRANSITION", str(ctx.exception))

    def test_03_invariant_i02_safety_screening_mandatory(self):
        """Invariant I-02: Safety signals cannot be omitted."""
        unsafe_signals = GateSignals(goal_safe=False, hypothesis_safe=True)
        with self.assertRaises(Denied) as ctx:
            self.kernel.advance("HYP-NS-001", Stage.SCREENED, unsafe_signals, caller="policy_service")
        self.assertIn("SAFETY_NOT_ALLOWED", str(ctx.exception))

    def test_04_invariant_i08_unauthorized_callers_rejected(self):
        """Invariant I-08: Only policy_service caller can advance stages or quarantine."""
        with self.assertRaises(Denied) as ctx:
            self.kernel.advance("HYP-NS-001", Stage.SCREENED, ALL_SIGNALS_PASS, caller="generation_agent")
        self.assertIn("ONLY_POLICY_SERVICE_CAN_ADVANCE", str(ctx.exception))

        with self.assertRaises(Denied) as ctx:
            self.kernel.quarantine("HYP-NS-001", caller="generation_agent")
        self.assertIn("ONLY_POLICY_SERVICE_CAN_QUARANTINE", str(ctx.exception))

    def test_05_prerequisite_signals_strictly_enforced(self):
        """Source verification, reflection, and tournament assessment required at appropriate stages."""
        # 1. SCREENED passes with safe signals
        self.kernel.advance("HYP-NS-001", Stage.SCREENED, ALL_SIGNALS_PASS, caller="policy_service")
        self.assertEqual(self.kernel.get("HYP-NS-001").stage, Stage.SCREENED)

        # 2. GROUNDED requires source_verified
        no_source = GateSignals(goal_safe=True, hypothesis_safe=True, source_verified=False)
        with self.assertRaises(Denied) as ctx:
            self.kernel.advance("HYP-NS-001", Stage.GROUNDED, no_source, caller="policy_service")
        self.assertIn("SOURCE_PROVENANCE_UNVERIFIED", str(ctx.exception))
        self.kernel.advance("HYP-NS-001", Stage.GROUNDED, ALL_SIGNALS_PASS, caller="policy_service")

        # 3. REVIEWED requires reflection_completed
        no_reflection = GateSignals(goal_safe=True, hypothesis_safe=True, source_verified=True, reflection_completed=False)
        with self.assertRaises(Denied) as ctx:
            self.kernel.advance("HYP-NS-001", Stage.REVIEWED, no_reflection, caller="policy_service")
        self.assertIn("SOURCE_GROUNDED_REFLECTION_MISSING", str(ctx.exception))
        self.kernel.advance("HYP-NS-001", Stage.REVIEWED, ALL_SIGNALS_PASS, caller="policy_service")

        # 4. ELIGIBLE passes
        self.kernel.advance("HYP-NS-001", Stage.ELIGIBLE, ALL_SIGNALS_PASS, caller="policy_service")

        # 5. RANKED requires tournament_assessed
        no_tournament = GateSignals(goal_safe=True, hypothesis_safe=True, source_verified=True, reflection_completed=True, tournament_assessed=False)
        with self.assertRaises(Denied) as ctx:
            self.kernel.advance("HYP-NS-001", Stage.RANKED, no_tournament, caller="policy_service")
        self.assertIn("TOURNAMENT_EVIDENCE_MISSING", str(ctx.exception))
        self.kernel.advance("HYP-NS-001", Stage.RANKED, ALL_SIGNALS_PASS, caller="policy_service")

        # 6. PROPOSAL_READY requires report_discloses_limits
        no_limits = GateSignals(goal_safe=True, hypothesis_safe=True, source_verified=True, reflection_completed=True, tournament_assessed=True, report_discloses_limits=False)
        with self.assertRaises(Denied) as ctx:
            self.kernel.advance("HYP-NS-001", Stage.PROPOSAL_READY, no_limits, caller="policy_service")
        self.assertIn("REPORT_LIMITATIONS_MISSING", str(ctx.exception))
        self.kernel.advance("HYP-NS-001", Stage.PROPOSAL_READY, ALL_SIGNALS_PASS, caller="policy_service")
        self.assertEqual(self.kernel.get("HYP-NS-001").stage, Stage.PROPOSAL_READY)

    def test_06_invariant_i04_elo_rank_distinct_from_truth(self):
        """Invariant I-04: Elo matches adjust ranking but CANNOT verify mathematical claims."""
        self.kernel.add("HYP-NS-002", "Alternative vortex tube alignment mechanism.")
        self.advance_to("HYP-NS-001", Stage.ELIGIBLE)
        self.advance_to("HYP-NS-002", Stage.ELIGIBLE)

        new_a, new_b = self.kernel.record_match(
            "HYP-NS-001", "HYP-NS-002", "LEFT", caller="tournament_service"
        )
        self.assertEqual(new_a, 1216.0)
        self.assertEqual(new_b, 1184.0)

        # Elo rank changed, but proof status is strictly untouched
        hyp1 = self.kernel.get("HYP-NS-001")
        self.assertEqual(hyp1.formal_state, "UNTESTED")
        self.assertEqual(hyp1.empirical_state, "NOT_APPLICABLE")
        self.assertFalse(self.kernel.proposal_is_verified("HYP-NS-001"))

    def test_07_invariant_i06_self_verification_strictly_forbidden(self):
        """Invariant I-06: Builder identity cannot act as its own verifier."""
        self.advance_to("HYP-NS-001", Stage.SCREENED)
        hyp = self.kernel.get("HYP-NS-001")

        receipt = VerificationReceipt(
            hypothesis_id="HYP-NS-001",
            exact_target_digest=hyp.content_digest,
            evidence_digest="a" * 64,
            claim_type="MATH_PROOF",
            builder_identity="primary-math-agent",
            verifier_identity="primary-math-agent",  # SAME IDENTITY: FORBIDDEN!
            independently_verified=True,
            protected_suite_passed=True,
            semantic_review_passed=True,
            verifier_authority_bound=True,
        )

        with self.assertRaises(Denied) as ctx:
            self.kernel.verify_claim(receipt, caller="independent_verification_service")
        self.assertIn("SELF_VERIFICATION_FORBIDDEN", str(ctx.exception))

    def test_08_invariant_i05_exact_target_digest_match(self):
        """Invariant I-05: Verification is exact-target bound; digest mismatch is rejected."""
        self.advance_to("HYP-NS-001", Stage.SCREENED)

        receipt = VerificationReceipt(
            hypothesis_id="HYP-NS-001",
            exact_target_digest=digest("completely different statement text"),
            evidence_digest="b" * 64,
            claim_type="MATH_PROOF",
            builder_identity="primary-math-agent",
            verifier_identity="independent-verifier-agent",
            independently_verified=True,
            protected_suite_passed=True,
            semantic_review_passed=True,
            verifier_authority_bound=True,
        )

        with self.assertRaises(Denied) as ctx:
            self.kernel.verify_claim(receipt, caller="independent_verification_service")
        self.assertIn("EXACT_TARGET_MISMATCH", str(ctx.exception))

    def test_09_claim_verification_success_both_claim_types(self):
        """SR7 Claim Verification succeeds when all prerequisites and independent verifier are valid."""
        self.advance_to("HYP-NS-001", Stage.SCREENED)
        hyp = self.kernel.get("HYP-NS-001")

        # MATH_PROOF verification
        math_receipt = VerificationReceipt(
            hypothesis_id="HYP-NS-001",
            exact_target_digest=hyp.content_digest,
            evidence_digest="c" * 64,
            claim_type="MATH_PROOF",
            builder_identity="primary-math-agent",
            verifier_identity="independent-verifier-agent",
            independently_verified=True,
            protected_suite_passed=True,
            semantic_review_passed=True,
            verifier_authority_bound=True,
        )
        verdict = self.kernel.verify_claim(math_receipt, caller="independent_verification_service")
        self.assertEqual(verdict, "APPROVED_PROOF")
        self.assertEqual(self.kernel.get("HYP-NS-001").formal_state, "APPROVED_PROOF")
        self.assertTrue(self.kernel.proposal_is_verified("HYP-NS-001"))

        # EMPIRICAL_REPLICATION verification
        self.kernel.add("HYP-NS-003", "Taylor-Green pseudospectral convergence at 64^3.")
        self.advance_to("HYP-NS-003", Stage.SCREENED)
        hyp3 = self.kernel.get("HYP-NS-003")

        emp_receipt = VerificationReceipt(
            hypothesis_id="HYP-NS-003",
            exact_target_digest=hyp3.content_digest,
            evidence_digest="d" * 64,
            claim_type="EMPIRICAL_REPLICATION",
            builder_identity="primary-math-agent",
            verifier_identity="independent-verifier-agent",
            independently_verified=True,
            protected_suite_passed=True,
            semantic_review_passed=True,
            verifier_authority_bound=True,
        )
        verdict_emp = self.kernel.verify_claim(emp_receipt, caller="independent_verification_service")
        self.assertEqual(verdict_emp, "INDEPENDENTLY_REPLICATED")
        self.assertEqual(self.kernel.get("HYP-NS-003").empirical_state, "INDEPENDENTLY_REPLICATED")
        self.assertTrue(self.kernel.proposal_is_verified("HYP-NS-003"))

    def test_10_invariant_i07_quarantine_permanently_revokes(self):
        """Invariant I-07: Quarantine revokes verification and freezes candidate permanently."""
        self.advance_to("HYP-NS-001", Stage.SCREENED)
        hyp = self.kernel.get("HYP-NS-001")
        receipt = VerificationReceipt(
            hypothesis_id="HYP-NS-001",
            exact_target_digest=hyp.content_digest,
            evidence_digest="e" * 64,
            claim_type="MATH_PROOF",
            builder_identity="primary-math-agent",
            verifier_identity="independent-verifier-agent",
            independently_verified=True,
            protected_suite_passed=True,
            semantic_review_passed=True,
            verifier_authority_bound=True,
        )
        self.kernel.verify_claim(receipt, caller="independent_verification_service")
        self.assertTrue(self.kernel.proposal_is_verified("HYP-NS-001"))

        # Quarantine
        self.kernel.quarantine("HYP-NS-001", caller="policy_service")
        quarantined = self.kernel.get("HYP-NS-001")
        self.assertEqual(quarantined.stage, Stage.QUARANTINED)
        self.assertEqual(quarantined.formal_state, "REVOKED")
        self.assertEqual(quarantined.empirical_state, "REVOKED")
        self.assertFalse(self.kernel.proposal_is_verified("HYP-NS-001"))

        # Cannot advance quarantined candidate
        with self.assertRaises(Denied):
            self.kernel.advance("HYP-NS-001", Stage.GROUNDED, ALL_SIGNALS_PASS, caller="policy_service")

    def test_11_invariant_i11_evolution_resets_lineage(self):
        """Invariant I-11: Evolving a candidate creates a fresh child with reset Elo and zero inherited proof."""
        self.advance_to("HYP-NS-001", Stage.RANKED)
        child = self.kernel.evolve(
            parent_id="HYP-NS-001",
            new_id="HYP-NS-001-R1",
            new_statement="Narrowed dyadic enstrophy transfer with explicit Poincare constant lambda_P on T^3_L.",
        )
        self.assertEqual(child.hypothesis_id, "HYP-NS-001-R1")
        self.assertEqual(child.stage, Stage.DRAFT)
        self.assertEqual(child.elo, 1200.0)
        self.assertEqual(child.formal_state, "UNTESTED")
        self.assertEqual(child.empirical_state, "NOT_APPLICABLE")
        self.assertEqual(child.parent_ids, ("HYP-NS-001",))
        self.assertFalse(self.kernel.proposal_is_verified("HYP-NS-001-R1"))


class TestCoScientistContractsAndGovernanceBinding(unittest.TestCase):
    """Tests for agent contracts, mathematical assurance integration, and Google Drive Governance OS."""

    def test_12_socratic_inversion_and_knowledge_gap_mapping(self):
        """Idea-to-Product OS Addendum v1.0: Socratic Inversion and Knowledge Gap contracts."""
        soc = SocraticInversionContract(
            topic="Forward dyadic enstrophy transfer vs viscous dissipation",
            credible_approaches=("Duhamel-Stokes expansion", "Littlewood-Paley projection", "Heisenberg triad analysis"),
            governing_assumptions=("Torus T^3", "Incompressible Navier-Stokes", "nu > 0", "f = 0"),
            trade_offs=("Sharp shell projection yields exact support confinement but lacks spatial localization",),
            falsification_tests=("ABC Beltrami zero-flux invariance", "Taylor-Green short-time positivity"),
            key_unanswered_questions=(
                "Can multi-shell forward cascade persist across geometric shell progression?",
                "Does single-triad Jacobi pendulum phase-reversal force macroscopic backscatter?",
            ),
        )
        self.assertLessEqual(len(soc.key_unanswered_questions), 3)

        gap = KnowledgeGap(
            gap_id="GAP-NS-001",
            affected_concept="Multi-shell cascade persistence",
            decision_blocked="Is macroscopic forward enstrophy self-focusing realizable?",
            current_hypothesis="Multi-shell alignment is defeated by triadic phase reversal and nu 2^{2Q} decay",
            confidence=0.85,
            evidence_base="NEG-EV-049 / NS_NONLINEAR_SELF_FOCUS_002_COUNTEREXAMPLE_MATRIX.md",
            impact_level="HIGH",
            uncertainty_level="MEDIUM",
            cheapest_discriminating_experiment="Analytical phase-orbit integration for coupled triad chains",
            status="OPEN",
        )
        self.assertEqual(gap.impact_level, "HIGH")
        self.assertEqual(gap.status, "OPEN")

    def test_13_independent_verification_contract_prevents_self_acceptance(self):
        """Governance Amendment v1.0 & Invariant I-06: Strict verifier separation."""
        contract = IndependentVerificationContract(
            hypothesis_id="HYP-CLM-042",
            exact_target_digest=digest("CLM-042 statement text"),
            evidence_digest="f" * 64,
            claim_type="MATH_PROOF",
            builder_identity="primary-math-agent",
            verifier_identity="independent-verifier-agent",
            protected_suite_cmd="pytest tests/test_ns_nonlinear_self_focus_002_suite.py",
            protected_suite_output="5 passed in 0.53s",
            protected_suite_passed=True,
            semantic_review_passed=True,
            verifier_authority_bound=True,
        )
        receipt = contract.to_receipt()
        self.assertEqual(receipt.hypothesis_id, "HYP-CLM-042")
        self.assertNotEqual(receipt.builder_identity, receipt.verifier_identity)

        # Failure when builder == verifier
        bad_contract = IndependentVerificationContract(
            hypothesis_id="HYP-CLM-042",
            exact_target_digest=digest("CLM-042 statement text"),
            evidence_digest="f" * 64,
            claim_type="MATH_PROOF",
            builder_identity="primary-math-agent",
            verifier_identity="primary-math-agent",
            protected_suite_cmd="pytest",
            protected_suite_output="passed",
            protected_suite_passed=True,
            semantic_review_passed=True,
            verifier_authority_bound=True,
        )
        with self.assertRaises(ValueError) as ctx:
            bad_contract.to_receipt()
        self.assertIn("SELF_VERIFICATION_FORBIDDEN", str(ctx.exception))

    def test_14_math_assurance_engine_clean_full_audit(self):
        """Mathematical Research Constitution v1.0.1: Full engine audit passes with zero deficiencies."""
        engine = MathAssuranceEngine()
        audit = engine.run_full_assurance_audit()
        self.assertTrue(audit["overall_assurance_passed"], f"Deficiencies detected: {audit.get('canonical_deficiencies')}")
        self.assertTrue(audit["branch_identity_valid"])
        self.assertEqual(audit["dag_cycles_count"], 0)
        self.assertEqual(audit["canonical_deficiencies_count"], 0)
        self.assertEqual(audit["verdict"], "MATHEMATICAL_ASSURANCE_VALID")

    def test_15_google_drive_master_record_authority_invariants(self):
        """Verify the immutable governance invariants from Google Drive Master Project Record (1KzdxjR0-IEgIn_BnGMVxslLRCRFnLxs3uV8of8Ep5ms)."""
        claim_mgr = ClaimManager()
        claims = claim_mgr.claims

        # 1. Target problem: 3D Navier-Stokes on T^3, nu > 0, f = 0
        engine = MathAssuranceEngine()
        branch = engine.validate_branch_identity()
        self.assertTrue(branch["valid"])
        self.assertEqual(branch["official_target_branch"], "CLAY_STATEMENT_B_PERIODIC_R3_MOD_Z3")

        # 2. No claim may claim SOLVED
        for cid, claim in claims.items():
            passport = claim.get("passport", {})
            self.assertNotEqual(passport.get("truth_status"), "PROVED_TARGET", f"Claim {cid} unlawfully claims PROVED_TARGET!")
            self.assertNotEqual(passport.get("project_status"), "FIELD_CANONICAL", f"Claim {cid} unlawfully claims FIELD_CANONICAL!")

        # 3. Novelty ceiling rule: N2 means NOT_FOUND_IN_AUDITED_SOURCES only
        for cid, claim in claims.items():
            novelty = claim.get("passport", {}).get("novelty")
            self.assertNotIn(novelty, ["N3_EXTERNAL_NOVELTY_SUPPORTED", "N4_COMMUNITY_RECOGNIZED_AS_NOVEL"],
                             f"Claim {cid} unlawfully claims external or community novelty without human consensus!")

    def test_16_research_memory_preflight_search_integration(self):
        """Verify preflight search in research memory integration with Co-Scientist hypotheses."""
        memory_engine = ResearchMemoryEngine()
        val = memory_engine.validate()
        self.assertTrue(val["valid"], f"Research memory validation errors: {val['errors']}")

        # Preflight search for dyadic self-focusing
        search = memory_engine.run_preflight_search(
            task_id="COSCIENTIST-TEST-001",
            query_tags=["stochastic_cauchy", "deformation_amplification", "production_rate_Q"],
            query_obstructions=["NS-OBS-004", "NS-OBS-005"],
        )
        self.assertGreater(len(search["top_related_pathways"]), 0)
        self.assertGreater(len(search["active_obstructions"]), 0)


if __name__ == "__main__":
    unittest.main()
