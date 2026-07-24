"""
Peak memory and disk estimation (Milestone 5.5)
===================================================

Estimates the memory footprint of one nonlinear-transfer validation call
BEFORE fetching a large cutout, so preflight can refuse a resolution tier
that won't fit rather than discovering it mid-run via an OOM kill.

The arrays actually allocated per snapshot (see nonlinear_transfer.py):
  u_hat (complex)                       3 * n^3
  velocity gradient tensor (real)       9 * n^3
  u, advective term, N (real, x3)       3 * n^3 each
  N_hat, N_hat_perp (complex, x2)       3 * n^3 each
plus the raw fetched velocity array (real) and a numpy-overhead safety
factor for transient temporaries numpy allocates during elementwise ops.

This does NOT implement a full float32 compute pipeline -- numpy/FFT
promote to float64/complex128 internally regardless of input dtype in
the general case. `dtype_bytes=4` here estimates the benefit of storing
the raw fetched velocity (and other retained-in-memory arrays) as
float32 between pipeline stages; the FFT/transfer computation itself
still runs in float64/complex128. Documented explicitly so this isn't
read as a claim of full mixed-precision support.
"""

from __future__ import annotations

from dataclasses import dataclass

COMPLEX_BYTES = 16  # complex128
DEFAULT_SAFETY_FACTOR = 1.5  # headroom for numpy elementwise temporaries


@dataclass(frozen=True)
class MemoryEstimate:
    grid_n: int
    dtype_bytes: int
    breakdown_mb: dict
    subtotal_mb: float
    peak_estimate_mb: float
    safety_factor: float


def estimate_peak_memory(
    grid_n: int, *, dtype_bytes: int = 8, safety_factor: float = DEFAULT_SAFETY_FACTOR
) -> MemoryEstimate:
    n3 = grid_n ** 3
    mb = 1024 * 1024

    breakdown = {
        "velocity_raw": 3 * n3 * dtype_bytes / mb,
        "u_hat": 3 * n3 * COMPLEX_BYTES / mb,
        "velocity_gradient_tensor": 9 * n3 * dtype_bytes / mb,
        "u_real_reconstructed": 3 * n3 * dtype_bytes / mb,
        "advective_term": 3 * n3 * dtype_bytes / mb,
        "nonlinear_term_N": 3 * n3 * dtype_bytes / mb,
        "N_hat": 3 * n3 * COMPLEX_BYTES / mb,
        "N_hat_perp": 3 * n3 * COMPLEX_BYTES / mb,
    }
    subtotal = sum(breakdown.values())
    peak = subtotal * safety_factor

    return MemoryEstimate(
        grid_n=grid_n,
        dtype_bytes=dtype_bytes,
        breakdown_mb=breakdown,
        subtotal_mb=subtotal,
        peak_estimate_mb=peak,
        safety_factor=safety_factor,
    )


def estimate_disk_usage_mb(n_snapshots: int, n_placements: int, *, per_run_mb: float = 3.0) -> float:
    """Rough estimate of output disk usage: CSVs, JSON summaries, and PNG
    dashboards per snapshot-placement combination. Does not include any
    raw velocity caching (this project never caches large raw cutouts to
    disk by design)."""
    return n_snapshots * n_placements * per_run_mb
