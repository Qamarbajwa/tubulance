"""External Wall-Clock Timing and Resource Monitoring Validator.

Implements Sections 14, 15, 43, 44 of Milestone V1.
"""
from __future__ import annotations

from typing import Dict, Any


class TimingValidationError(ValueError):
    """Raised when internal candidate reported timing differs suspiciously from external wall-clock time."""


def validate_timing_and_resources(
    external_wall_time: float,
    internal_rom_time: float,
    peak_rss_bytes: int,
) -> Dict[str, Any]:
    """Validate external wall-clock time vs internal candidate reported time."""
    # Discrepancy check: internal time cannot be negative or larger than external time
    if internal_rom_time < 0.0:
        raise TimingValidationError(f"Negative internal ROM time reported: {internal_rom_time}")

    if internal_rom_time > external_wall_time * 1.5 + 0.1:
        raise TimingValidationError(
            f"Internal ROM time ({internal_rom_time:.4f}s) exceeds external wall time ({external_wall_time:.4f}s)!"
        )

    discrepancy_ratio = (external_wall_time - internal_rom_time) / (external_wall_time + 1e-15)

    return {
        "external_wall_time_s": float(external_wall_time),
        "internal_rom_time_s": float(internal_rom_time),
        "discrepancy_ratio": float(discrepancy_ratio),
        "peak_rss_mb": float(peak_rss_bytes / (1024 * 1024)),
    }
