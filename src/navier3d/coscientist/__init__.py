"""Research Co-Scientist Dark Factory Subsystem for 3D Navier-Stokes.

Implements the multi-agent scientific discovery architecture, no-bypass
research gate state machine (SR0-SR8), and dual control planes specified in
COSCIENTIST_DF_v0_1 and Google Drive Governance OS.
"""

from .kernel import (
    Denied,
    Stage,
    Hypothesis,
    GateSignals,
    VerificationReceipt,
    ResearchGateKernel,
    digest,
    ORDER,
)
from .contracts import (
    GenerationContract,
    ReflectionContract,
    ProximityContract,
    EvolutionContract,
    TournamentContract,
    IndependentVerificationContract,
)
from .autonomy import (
    AutonomousResearchRunner,
    AutonomyLevel,
    AutonomyReceipt,
)

__all__ = [
    "Denied",
    "Stage",
    "Hypothesis",
    "GateSignals",
    "VerificationReceipt",
    "ResearchGateKernel",
    "digest",
    "ORDER",
    "GenerationContract",
    "ReflectionContract",
    "ProximityContract",
    "EvolutionContract",
    "TournamentContract",
    "IndependentVerificationContract",
    "AutonomousResearchRunner",
    "AutonomyLevel",
    "AutonomyReceipt",
]
