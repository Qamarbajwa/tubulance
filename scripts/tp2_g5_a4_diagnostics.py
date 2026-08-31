"""Executable algebra and measure diagnostics for TP2-G5-A4.

The functions in this module are deliberately finite-dimensional helpers.  They
mirror the accepted stochastic identities without pretending to construct a
Navier--Stokes singularity or a pathwise stochastic history.
"""

from __future__ import annotations

from math import exp, log
from typing import Iterable

import numpy as np


def intrinsic_window(max_vorticity: float, a: float) -> float:
    """Return the scale-critical lookback ``L=a/M``."""
    if max_vorticity <= 0 or a <= 0:
        raise ValueError("max_vorticity and a must be positive")
    return a / max_vorticity


def chi_from_relative_qv(J: float) -> float:
    """Return chi when ``J=-log(chi)``."""
    if J < 0:
        raise ValueError("relative quadratic variation must be nonnegative")
    return exp(-J)


def relative_variance_from_chi(chi: float) -> float:
    if not 0 < chi <= 1:
        raise ValueError("chi must lie in (0, 1]")
    return 1.0 / chi - 1.0


def relative_variance_from_relative_qv(J: float) -> float:
    return relative_variance_from_chi(chi_from_relative_qv(J))


def chi_variance_identity(mean_squared: float, second_moment: float) -> tuple[float, float]:
    """Return ``(chi, relative variance)`` for ``0 < |m|^2 <= S``."""
    if mean_squared <= 0 or second_moment < mean_squared:
        raise ValueError("require 0 < |m|^2 <= S")
    chi = mean_squared / second_moment
    return chi, relative_variance_from_chi(chi)


def separate_nonnegative_integrals(total: float, first_fraction: float) -> tuple[float, float]:
    """A deterministic witness for ``0 <= A,B`` and ``A+B=total``."""
    if total < 0 or not 0 <= first_fraction <= 1:
        raise ValueError("invalid nonnegative split")
    first = total * first_fraction
    return first, total - first


def normalized_bad_set_bound(integral: float, epsilon: float, horizon: float) -> float:
    """Markov bound under ``(1/L) integral mu_r dr`` for a nonnegative metric."""
    if integral < 0 or epsilon <= 0 or horizon <= 0:
        raise ValueError("integral, epsilon, and horizon must be valid")
    return min(1.0, integral / (epsilon * horizon))


def classify_cluster_subsequence(values: Iterable[float], *, tolerance: float = 1e-12) -> str:
    """Classify an already selected convergent/cluster subsequence.

    A positive finite or infinite cluster is D; a zero cluster is R.  The
    helper intentionally does not claim that one of these labels describes an
    oscillatory sequence before subsequence extraction.
    """
    vals = np.asarray(list(values), dtype=float)
    if vals.size == 0 or np.any(~np.isfinite(vals)) or np.any(vals < 0):
        raise ValueError("values must be finite and nonnegative")
    limit = float(vals[-1])
    if vals[-1] <= tolerance:
        return "RIGID"
    if limit > tolerance:
        return "DECOHERENT"
    return "OSCILLATORY_BEFORE_SUBSEQUENCE"


def scale_audit() -> dict[str, int]:
    """Return the parabolic weights used by the A4 dimensional audit."""
    return {"M": 2, "L": -2, "Xi": 2, "dt": -2, "J": 0}


def covariance_trace_lower_bound(mean_squared: float, relative_qv: float) -> float:
    """Trace lower bound for ``tr C / |m|^2`` from the variance identity."""
    if mean_squared <= 0 or relative_qv < 0:
        raise ValueError("invalid covariance normalization")
    return relative_variance_from_relative_qv(relative_qv)


def anisotropic_metric_example(K: float) -> tuple[float, float]:
    """Return ``(||D omega||^2, ||D J||^2)`` for a simple kinematic family."""
    if K <= 0:
        raise ValueError("K must be positive")
    D = np.diag([K, 1.0, 1.0 / K])
    omega = np.array([1.0, 0.0, 0.0])
    J = np.zeros((3, 3))
    J[2, 1] = 1.0
    return float(np.dot(D @ omega, D @ omega)), float(np.sum((D @ J) ** 2))


def periodic_shear_calibration() -> dict[str, float]:
    """Couette calibration: spatially uniform vorticity gradient gives Xi=J=0."""
    return {"J_omega_norm_squared": 0.0, "Xi": 0.0, "chi": 1.0, "J": 0.0}
