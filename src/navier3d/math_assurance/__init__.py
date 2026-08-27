"""Mathematical Research Constitution & Assurance Package (NS-MRC-1)."""
from .engine import MathAssuranceEngine
from .assumptions import AssumptionManager
from .claims import ClaimManager
from .dependencies import DependencyGraphManager
from .promotion import PromotionManager
from .understanding import UnderstandingManager
from .novelty import NoveltyManager

__all__ = [
    "MathAssuranceEngine",
    "AssumptionManager",
    "ClaimManager",
    "DependencyGraphManager",
    "PromotionManager",
    "UnderstandingManager",
    "NoveltyManager",
]
