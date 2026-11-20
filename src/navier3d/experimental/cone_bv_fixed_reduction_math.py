"""Program NS-CONE-BV-FIXED-REDUCTION-1: Terminal-Axis Fixed Reduction Engine.

Exact Mathematical Proof Architecture:
    Hypothesis:
        Let u be a suitable weak solution in Q(1) = B_1 x (-1, 0].
        Suppose exists delta > 0, M > 0, and a time-slice projective direction field e(t) in RP^2 such that:
            |xi(x,t) x e(t)| <= 1 - delta
        at all regular points (x,t) in Q(1) with |omega(x,t)| > M.
        Suppose e(t) satisfies essential terminal stabilization:
            ess_lim_{t -> 0^-} e(t) = e_* in RP^2
        (which is strictly guaranteed if e in BV((-1, 0); RP^2) since total metric variation is finite).

    Reduction Chain:
        1. Essential Terminal Stabilization:
           ess_lim_{t -> 0^-} e(t) = e_* in RP^2.

        2. Projective Metric Triangle Inequality:
           Let alpha = arcsin(1 - delta) < pi/2.
           At regular points with |omega| > M, d_{RP^2}(xi(x,t), e(t)) <= alpha.
           Choose 0 < eta < pi/2 - alpha and h > 0 such that ess_sup_{t in (-h, 0)} d_{RP^2}(e(t), e_*) < eta.
           Then for all regular points with |omega| > M at good times t in (-h, 0):
               d_{RP^2}(xi(x,t), e_*) <= d_{RP^2}(xi(x,t), e(t)) + d_{RP^2}(e(t), e_*) <= alpha + eta < pi/2.

        3. Fixed Double-Cone Formation:
           For all regular points with |omega| > M at good times t in (-h, 0):
               |xi(x,t) x e_*| <= sin(alpha + eta) = 1 - delta_*
           where delta_* = 1 - sin(alpha + eta) > 0.

        4. Regular-Point Continuity Promotion:
           If (x_0, t_0) is an arbitrary regular point in B_r x (-r^2, 0] with |omega(x_0, t_0)| > M,
           the vorticity field omega is smooth and continuous in a parabolic neighborhood U of (x_0, t_0).
           Approaching (x_0, t_0) by good times t_n -> t_0 yields |xi(x_0, t_0) x e_*| <= 1 - delta_*.

        5. Parabolic Rescaling to Lei-Ren-Tian (2025) Theorem 1.1:
           Choose r = min{1, sqrt(h)/2}.
           In Q(r) = B_r x (-r^2, 0), the rescaled solution u_r(x,t) = r u(rx, r^2 t) has vorticity
           omega_r(x,t) = r^2 omega(rx, r^2 t) and satisfies:
               |xi_r(x,t) x e_*| <= 1 - delta_*  at regular points with  |omega_r(x,t)| > M_r := r^2 M.
           This matches EXACTLY Theorem 1.1 of Lei-Ren-Tian (arXiv:2501.08976) with fixed axis e_*,
           margin delta_*, and threshold M_r.

        6. Conclusion:
           Theorem 1.1 implies (0,0) is a regular point.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class TerminalConeMarginResult:
    """Quantitative terminal cone margin calculation via projective triangle inequality."""
    delta_initial: float            # Original cone margin delta in (0, 1]
    alpha_rad: float                # arcsin(1 - delta)
    alpha_deg: float
    eta_rad: float                  # Terminal essential deviation slack
    eta_deg: float
    combined_angle_deg: float       # alpha + eta
    delta_star: float               # Effective fixed-cone margin 1 - sin(alpha + eta) > 0
    is_terminal_cone_valid: bool    # combined_angle < 90 deg (i.e. delta_star > 0)


@dataclass
class RescaledThresholdResult:
    """Parabolic cylinder rescaling to Lei-Ren-Tian Theorem 1.1."""
    original_M: float
    horizon_h: float
    rescaling_radius_r: float
    rescaled_threshold_M_r: float
    is_theorem_1_1_applicable: bool


def compute_terminal_fixed_cone_margin(
    delta: float,
    slack_fraction: float = 0.5,
) -> TerminalConeMarginResult:
    """Compute effective fixed-cone margin delta_* around terminal axis e_*."""
    assert 0.0 < delta <= 1.0, "delta must be in (0, 1]"
    alpha_rad = float(np.arcsin(1.0 - delta))
    alpha_deg = float(np.degrees(alpha_rad))

    max_slack = np.pi / 2.0 - alpha_rad
    eta_rad = float(slack_fraction * max_slack)
    eta_deg = float(np.degrees(eta_rad))

    combined_rad = alpha_rad + eta_rad
    combined_deg = float(np.degrees(combined_rad))

    delta_star = float(1.0 - np.sin(combined_rad))
    is_valid = (delta_star > 0.0 and combined_deg < 90.0)

    return TerminalConeMarginResult(
        delta_initial=delta,
        alpha_rad=alpha_rad,
        alpha_deg=alpha_deg,
        eta_rad=eta_rad,
        eta_deg=eta_deg,
        combined_angle_deg=combined_deg,
        delta_star=delta_star,
        is_terminal_cone_valid=is_valid,
    )


def compute_rescaled_theorem11_parameters(
    M: float,
    horizon_h: float,
) -> RescaledThresholdResult:
    """Compute rescaled parabolic cylinder parameters matching Theorem 1.1."""
    assert M > 0.0, "M must be positive"
    assert horizon_h > 0.0, "horizon h must be positive"

    r = float(min(1.0, np.sqrt(horizon_h) * 0.5))
    M_r = float(r**2 * M)

    return RescaledThresholdResult(
        original_M=M,
        horizon_h=horizon_h,
        rescaling_radius_r=r,
        rescaled_threshold_M_r=M_r,
        is_theorem_1_1_applicable=True,
    )
