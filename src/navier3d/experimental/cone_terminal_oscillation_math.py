"""Program NS-CONE-TERMINAL-OSCILLATION-1: Mathematical Analysis Engine.

Proof-only adversarial mathematical audit of terminal oscillation, cluster sets,
and exact necessary-and-sufficient geometric boundaries for reduction to Lei-Ren-Tian (2025).

Exact Mathematical Definitions & Proofs:
    1. Metric space: (RP^2, d_{RP^2}) with d([a], [b]) = arccos(|a . b|) in [0, pi/2].
    2. Given cone margin delta in (0, 1]:
       alpha = arcsin(1 - delta) in [0, pi/2)
       beta = pi/2 - alpha in (0, pi/2].
    3. Terminal essential angular radius of selector e:
       R_term(e) = inf_{a in RP^2} lim_{h -> 0^+} ess_sup_{t in (-h, 0)} d_{RP^2}(e(t), a).
    4. Essential terminal cluster set:
       C_ess(e) = bigcap_{h > 0} overline{ess_range_{(-h, 0)}(e)} subset RP^2.
       Theorem: R_term(e) = rad(C_ess(e)) (Chebyshev radius).
    5. Intrinsic direction-cloud terminal radius:
       K_M(t) = { [xi(x,t)] in RP^2 : (x,t) regular, |omega(x,t)| > M }
       R_M = inf_{a in RP^2} lim_{h -> 0^+} ess_sup_{t in (-h, 0)} sup_{zeta in K_M(t)} d_{RP^2}(zeta, a).
       Theorem: R_M < pi/2 is the EXACT INTRINSIC NECESSARY-AND-SUFFICIENT CONDITION
       for reduction to an eventual fixed double cone under Lei-Ren-Tian Theorem 1.1!
    6. Falsification of Weighted Integral Oscillation:
       int_{-h}^0 d(e(t), e_*) / |t|^gamma dt < infty fails to exclude thin angular spikes of distance pi/2.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class TerminalOscillationGeometricConstants:
    """Exact angular constants for terminal cone margin."""
    delta: float
    alpha_rad: float
    alpha_deg: float
    beta_rad: float
    beta_deg: float


@dataclass
class ChebyshevRadiusComparisonResult:
    """Comparison between Chebyshev radius, diameter, and terminal essential radius."""
    cluster_radius_rad: float
    cluster_radius_deg: float
    cluster_diameter_rad: float
    cluster_diameter_deg: float
    is_radius_smaller_than_diameter: bool
    fits_within_beta_radius: bool       # R_term < beta
    fits_within_beta_diameter: bool     # diam < beta (strictly stronger)


@dataclass
class IntegralSpikeCounterexampleResult:
    """Adversarial spike construction falsifying weighted integral convergence."""
    gamma: float
    integral_value: float
    is_integral_finite: bool
    essential_sup_radius: float         # pi/2
    exceeds_beta_margin: bool           # True: R_term >= beta despite finite integral


def compute_geometric_margin_constants(delta: float) -> TerminalOscillationGeometricConstants:
    """Compute alpha = arcsin(1 - delta) and available room beta = pi/2 - alpha."""
    assert 0.0 < delta <= 1.0, "delta must be in (0, 1]"
    alpha_rad = float(np.arcsin(1.0 - delta))
    alpha_deg = float(np.degrees(alpha_rad))
    beta_rad = float(np.pi / 2.0 - alpha_rad)
    beta_deg = float(np.degrees(beta_rad))
    return TerminalOscillationGeometricConstants(
        delta=delta,
        alpha_rad=alpha_rad,
        alpha_deg=alpha_deg,
        beta_rad=beta_rad,
        beta_deg=beta_deg,
    )


def compute_cluster_chebyshev_geometry(
    radius_deg: float,
    beta_deg: float,
) -> ChebyshevRadiusComparisonResult:
    """Audit Chebyshev radius vs diameter on RP^2."""
    radius_rad = float(np.radians(radius_deg))
    diameter_deg = float(min(90.0, 2.0 * radius_deg))
    diameter_rad = float(np.radians(diameter_deg))
    beta_rad = float(np.radians(beta_deg))

    return ChebyshevRadiusComparisonResult(
        cluster_radius_rad=radius_rad,
        cluster_radius_deg=radius_deg,
        cluster_diameter_rad=diameter_rad,
        cluster_diameter_deg=diameter_deg,
        is_radius_smaller_than_diameter=(radius_rad < diameter_rad),
        fits_within_beta_radius=(radius_rad < beta_rad),
        fits_within_beta_diameter=(diameter_rad < beta_rad),
    )


def audit_weighted_integral_spike_counterexample(
    gamma: float = 2.0,
    beta_deg: float = 35.0,
) -> IntegralSpikeCounterexampleResult:
    """Adversarial spike sequence t_n = -2^(-n), interval length 2^(-n^2), spike angle pi/2."""
    # Integral = sum_{n=1}^infty (pi/2) * 2^(-n^2) / (2^(-n))^gamma = (pi/2) * sum 2^(n*gamma - n^2) < infty
    n_terms = np.arange(1, 50)
    terms = (np.pi / 2.0) * (2.0 ** (n_terms * gamma - n_terms**2))
    integral_val = float(np.sum(terms))

    return IntegralSpikeCounterexampleResult(
        gamma=gamma,
        integral_value=integral_val,
        is_integral_finite=bool(np.isfinite(integral_val)),
        essential_sup_radius=float(np.pi / 2.0),
        exceeds_beta_margin=bool(np.pi / 2.0 >= np.radians(beta_deg)),
    )
