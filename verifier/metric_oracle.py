"""Independent Metric Oracle implementing the Two-Independent-Implementation Rule.

Implements Sections 5, 6 of Milestone V1.
MUST NOT import navier3d.audit.metrics or any experimental modules.
"""
from __future__ import annotations

import math
from typing import Dict, Any, Tuple

import numpy as np


def oracle_velocity_relative_l2(raw_ref: np.ndarray, raw_cand: np.ndarray) -> float:
    """Independent oracle for L2 relative velocity error using explicit flattened sum-of-squares."""
    ref_flat = np.asarray(raw_ref, dtype=np.float64).ravel()
    cand_flat = np.asarray(raw_cand, dtype=np.float64).ravel()

    diff_sum_sq = 0.0
    ref_sum_sq = 0.0

    for i in range(len(ref_flat)):
        d = ref_flat[i] - cand_flat[i]
        diff_sum_sq += d * d
        ref_sum_sq += ref_flat[i] * ref_flat[i]

    diff_l2 = math.sqrt(diff_sum_sq)
    ref_l2 = math.sqrt(ref_sum_sq)

    return float(diff_l2 / (ref_l2 + 1e-15))


def oracle_wall_shear_relative_error(tau_ref: float, tau_cand: float) -> float:
    """Independent oracle for relative wall shear error."""
    ref_val = float(tau_ref)
    cand_val = float(tau_cand)
    return float(abs(ref_val - cand_val) / (abs(ref_val) + 1e-15))


def oracle_subspace_overlap(Phi_B: np.ndarray, Phi_W: np.ndarray) -> Tuple[float, float, float]:
    """Independent oracle computing cross-Gram matrix, Frobenius norm, max singular value, and min principal angle."""
    # Phi_B: (n_dofs, r_bulk), Phi_W: (n_dofs, r_boundary)
    C = np.dot(Phi_B.T, Phi_W)
    frob_norm = float(np.sqrt(np.sum(C * C)))

    U, s, Vt = np.linalg.svd(C, full_matrices=False)
    sigma_max = float(s[0]) if len(s) > 0 else 0.0

    s_clamped = np.clip(s, 0.0, 1.0)
    principal_angles_deg = np.degrees(np.arccos(s_clamped))
    min_angle = float(np.min(principal_angles_deg)) if len(s) > 0 else 90.0

    return frob_norm, sigma_max, min_angle
