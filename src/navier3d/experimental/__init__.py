"""Experimental research modules for navier3d.

These modules are retained strictly for mathematical research and non-production testing.
Production defaults and solvers do not export or enable experimental modules.
"""
from .ramanujan_correction import RamanujanCorrection, SpectralCorrection

__all__ = [
    "SpectralCorrection",
    "RamanujanCorrection",
]
