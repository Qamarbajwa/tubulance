"""Legacy forwarder for navier3d experimental spectral corrections.

RamanujanCorrection is an experimental research module isolated under:
`navier3d.experimental.ramanujan_correction`
"""
from navier3d.experimental.ramanujan_correction import RamanujanCorrection, SpectralCorrection

__all__ = [
    "SpectralCorrection",
    "RamanujanCorrection",
]
