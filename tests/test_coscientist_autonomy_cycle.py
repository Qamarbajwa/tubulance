"""Test suite for Co-Scientist Dark Factory Autonomy Engine (Autonomy Level 2).

Verifies:
- End-to-end closed loop autonomous execution (SR0 -> SR8)
- Socratic inversion & assumption mapping contract
- Adversarial reflection against counterexample matrix
- Evolutionary mutation on counterexample encounter
- Elo tournament execution without proof promotion
- Independent verifier gate enforcement (author != verifier)
- Epistemic invariants preservation (Clay B UNRESOLVED, Release NO-GO)
"""

import pytest
from navier3d.coscientist.autonomy import (
    AutonomousResearchRunner,
    AutonomyLevel,
    AutonomyReceipt,
)
from navier3d.coscientist.kernel import ResearchGateKernel


def test_autonomy_cycle_clean_execution():
    """Verify clean closed-loop execution for a well-posed non-local triad hypothesis."""
    runner = AutonomousResearchRunner()
    receipt = runner.run_cycle(
        goal_id="GOAL-NS-NONLOCAL-TRIAD-001",
        topic="Non-local dyadic Fourier triad enstrophy transfer",
        candidate_statement="Non-local triad enstrophy transfer from scales p << q to shell Q is suppressed by at least 2^(-3Q/2) relative to viscous dissipation",
        assumptions=("Incompressible 3D Navier-Stokes on periodic T^3", "Smooth initial data with finite enstrophy", "nu > 0"),
        falsifiers=("Observation of persistent O(1) non-local triad enstrophy transfer as Q -> infinity",),
        counterexamples=("Parallel shear flow", "2D embedded flow"),
        known_obstructions=("NS-OBS-022", "NS-OBS-020B-R4"),
        verifier_agent_id="ADVERSARIAL_INDEPENDENT_RESEARCH_VERIFIER",
    )

    assert isinstance(receipt, AutonomyReceipt)
    assert receipt.autonomy_level == AutonomyLevel.LEVEL_2_CLOSED_LOOP_RESEARCH
    assert receipt.socratic_inversion_ok is True
    assert receipt.tournament_matches_played == 1
    assert receipt.independent_verifier_passed is True
    assert receipt.clay_statement_b_unresolved is True
    assert receipt.release_no_go is True
    assert len(receipt.receipt_digest) == 64


def test_autonomy_cycle_with_counterexample_evolution():
    """Verify that encountering a counterexample triggers autonomous mutation/grounding."""
    runner = AutonomousResearchRunner()
    receipt = runner.run_cycle(
        goal_id="GOAL-NS-BELTRAMI-STRETCH-001",
        topic="Beltrami helical mode self-stretching",
        candidate_statement="Parallel helical swirl concentrates without bounds",
        assumptions=("Incompressible flow",),
        falsifiers=("Zero vortex stretching in ABC flows",),
        counterexamples=("ABC Beltrami flow (u parallel to omega)",),
        known_obstructions=("NEG-EV-047",),
        verifier_agent_id="ADVERSARIAL_INDEPENDENT_RESEARCH_VERIFIER",
    )

    assert receipt.reflection_contradiction_found is True
    assert "-R1" in receipt.hypothesis_id
    assert "restricted to orthogonal non-Beltrami modes" in receipt.hypothesis_statement
    assert receipt.clay_statement_b_unresolved is True
    assert receipt.release_no_go is True
