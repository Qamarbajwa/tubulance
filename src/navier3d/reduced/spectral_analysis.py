"""Spectral Analysis, Effective Dissipation Eigenvalues, and Temporal Harmonic Diagnostics.

Provides:
- effective_pod_eigenvalues: Computes effective dissipation eigenvalues lambda_n^eff = <phi_n, -L_h phi_n>_MAC.
- mode_frequency_analysis: Analyzes temporal spectrum of modal coefficients a_n(t).
- spatial_temporal_compression_ratio: Evaluates total spatial + temporal compression.
"""
from __future__ import annotations

from typing import List, Tuple, Dict, Any
import numpy as np

from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from ..operators import velocity_laplacian
from .solenoidal_basis import SolenoidalModalBasis, PODSolenoidalBasis


def effective_pod_eigenvalues(
    basis: SolenoidalModalBasis,
    bcs: Optional[BoundaryConditionSet] = None,
) -> np.ndarray:
    """Compute effective Laplacian dissipation eigenvalues lambda_n^eff = <phi_n, -L_h phi_n>_MAC."""
    r = basis.num_modes
    dV = basis.mesh.cell_volume
    lams = np.zeros(r, dtype=np.float64)

    for n in range(r):
        phi_u, phi_v, phi_w = basis.get_mode_mac(n)
        a_unit = np.zeros(r)
        a_unit[n] = 1.0

        vel_n = basis.reconstruct_mac(a_unit)
        if bcs is not None:
            apply_velocity_bc(vel_n, bcs)

        lap_vel = velocity_laplacian(vel_n, basis.mesh)

        lap_u = lap_vel.u.interior[:-1, :, :]
        lap_v = lap_vel.v.interior[:, :-1, :]
        lap_w = lap_vel.w.interior[:, :, :-1]

        # lambda_n^eff = - <phi_n, L_h phi_n>_MAC / <phi_n, phi_n>_MAC
        num = -np.sum(phi_u * lap_u + phi_v * lap_v + phi_w * lap_w) * dV
        den = np.sum(phi_u**2 + phi_v**2 + phi_w**2) * dV
        lams[n] = float(num / (den + 1e-15))

    return lams


def mode_frequency_analysis(
    a_history: np.ndarray,
    dt: float,
    top_harmonics_per_mode: int = 3,
) -> Dict[str, Any]:
    """Analyze temporal spectrum a_n(t) -> omega_nm and evaluate harmonic representation accuracy."""
    n_steps, r = a_history.shape
    freqs = np.fft.rfftfreq(n_steps, d=dt)

    mode_harmonics = {}
    total_coeffs = 0

    for n in range(r):
        a_t = a_history[:, n]
        a_fft = np.fft.rfft(a_t) / n_steps
        amp = np.abs(a_fft)

        # Extract top dominant frequencies
        top_idx = np.argsort(amp)[::-1][:top_harmonics_per_mode]

        dom_freqs = freqs[top_idx].tolist()
        dom_amps = amp[top_idx].tolist()

        mode_harmonics[n] = {
            "frequencies": dom_freqs,
            "amplitudes": dom_amps,
        }
        total_coeffs += len(top_idx)

    # Compute spatial-temporal compression ratio
    n_full_dofs = r * n_steps  # In modal space
    cr_time = n_full_dofs / (total_coeffs + 1e-15)

    return {
        "mode_harmonics": mode_harmonics,
        "total_harmonic_coefficients": total_coeffs,
        "temporal_compression_ratio": float(cr_time),
    }
