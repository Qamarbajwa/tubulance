"""
Forcing-aware terminal operator schema (Milestone 5.7)
==========================================================

Milestone 5.7 does not replace jhtdb_terminal_benchmark.terminal_operator().
It tests whether that operator remains valid once forcing, material, and
size are explicit inputs. This module provides:

1. `gamma_baseline(...)` -- a thin wrapper around the *unmodified* original
   gamma(k) = (c_gamma/tau_s) * q(k)^n formula. This is "comparison group A"
   (original terminal model, fixed gains) and "group B" (same formula,
   gains retuned only on calibration cases) in the stress test -- both use
   this function, differing only in what c_gamma/tau_s they are called
   with.

2. `GammaDependencies` -- the extended conceptual signature from the
   specification,

       gamma = gamma(q, Phi_l, tau_f/tau_l, M, l/L, l/lc)

   bundled as a frozen dataclass so every call site is forced to supply
   (or explicitly decline) each dependency, rather than silently ignoring
   some of them.

3. `gamma_candidate_forcing_aware(...)` -- a CANDIDATE modification, marked
   explicitly as such. It is NOT the validated model; it is "comparison
   group C" in the stress test. Its only structural commitment is H1
   (weak-forcing consistency): as Phi_l -> 0, it must reduce exactly to
   `gamma_baseline`. Away from that limit, the candidate applies a
   monotonic multiplicative correction bounded so it can never zero out or
   invert the sign of gamma -- a specific, falsifiable, but explicitly
   unvalidated functional form. Do not treat its predictions as evidence
   about the real theory; it exists so H1/H3/H6 have something concrete to
   run in "group C" and compare against "group A".

4. `TerminalEnergySplit` -- the extended energy-channel schema

       E_terminal = E_heat + E_return + E_wave + E_compressive
                    + E_surface + E_internal

   For the current incompressible Newtonian benchmark the extra four
   channels are always exactly zero (there is no wave, compressive,
   surface, or internal-energy physics in this solver) -- the schema
   supports them so a future material/solver can populate them without a
   shape change, but this module never fabricates a nonzero value for a
   channel with no underlying physics.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from jhtdb_terminal_benchmark import terminal_operator


@dataclass(frozen=True)
class GammaDependencies:
    """The extended conceptual dependency list from the Milestone 5.7 spec:
    gamma = gamma(q, Phi_l, tau_f/tau_l, M, l/L, l/lc).

    q                terminal coordinate, (|k|-ks)/(kc-ks), already used by
                     the original operator
    phi_l            forcing-dominance ratio at the structure scale under
                     consideration (forcing.forcing_dominance_ratio)
    theta_f          tau_f/tau_l (forcing.forcing_timescale_ratio)
    material_name    material_state.MaterialState.name
    l_over_L         structure size over system/domain size
    l_over_lc        structure size over the terminal cutoff scale (2*pi/kc)
    """

    q: np.ndarray
    phi_l: float
    theta_f: float
    material_name: str
    l_over_L: float
    l_over_lc: float


def gamma_baseline(uh, kmag, kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s) -> dict:
    """Comparison groups A and B: the unmodified original terminal
    operator. Never modified by this module -- see
    jhtdb_terminal_benchmark.terminal_operator for the formula."""
    return terminal_operator(uh, kmag, kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s)


# --- Candidate model (comparison group C) -----------------------------------
#
# CANDIDATE MODEL -- NOT VALIDATED. Fixed here, before running against the
# stress-test matrix, so a later "it happens to fit" cannot be mistaken for
# a physical discovery (same preregistration discipline as
# backscatter_placement.py). Its only required property is H1: it must
# collapse exactly onto gamma_baseline when phi_l -> 0.
#
# Functional form: multiply the baseline gamma(k) by a bounded correction
#
#     correction(phi_l, theta_f) = 1 + kappa * tanh(log10(1 + phi_l)) * f(theta_f)
#     f(theta_f) = theta_f / (1 + theta_f)     (0 when tau_f->0 i.e. very
#                                                rapid forcing relative to
#                                                the structure, ->1 as
#                                                tau_f>>tau_l i.e. quasi-steady)
#
# kappa (CANDIDATE_KAPPA) sets the maximum fractional change in gamma the
# candidate is willing to apply; it is a preregistered constant, not fit to
# any run in this milestone.
CANDIDATE_KAPPA = 0.5
IS_CANDIDATE_MODEL = True


def gamma_candidate_forcing_aware(
    uh, kmag, kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s, *, phi_l: float, theta_f: float, kappa: float = CANDIDATE_KAPPA
) -> dict:
    """CANDIDATE MODEL. See module docstring. Reduces exactly to
    gamma_baseline as phi_l -> 0 (H1)."""
    base = terminal_operator(uh, kmag, kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s)
    if not np.isfinite(phi_l) or phi_l <= 0:
        return base
    f_theta = theta_f / (1.0 + theta_f) if np.isfinite(theta_f) and theta_f >= 0 else 0.0
    correction = 1.0 + kappa * np.tanh(np.log10(1.0 + phi_l)) * f_theta
    gamma = base["gamma"] * correction
    alpha = base["alpha"]
    n3 = np.prod(uh.shape[1:])
    twice_modal_energy = np.sum(np.abs(uh) ** 2, axis=0) / (n3 * n3)
    removed_density = gamma * twice_modal_energy
    return {
        "gamma": gamma,
        "alpha": alpha,
        "terminal_power": float(removed_density.sum()),
        "heat_power": float((alpha * removed_density).sum()),
        "return_power": float(((1.0 - alpha) * removed_density).sum()),
        "candidate_model": True,
        "correction_applied": float(correction),
    }


@dataclass(frozen=True)
class TerminalEnergySplit:
    """E_terminal = E_heat + E_return + E_wave + E_compressive + E_surface + E_internal.

    e_wave/e_compressive/e_surface/e_internal are forced to 0.0 by
    from_incompressible_newtonian() -- this solver/material has no such
    physics -- but the field exists so a future material can populate it
    without changing this schema's shape.
    """

    e_heat: float
    e_return: float
    e_wave: float = 0.0
    e_compressive: float = 0.0
    e_surface: float = 0.0
    e_internal: float = 0.0

    @property
    def e_terminal(self) -> float:
        return (
            self.e_heat
            + self.e_return
            + self.e_wave
            + self.e_compressive
            + self.e_surface
            + self.e_internal
        )

    @classmethod
    def from_incompressible_newtonian(cls, heat_power: float, return_power: float) -> "TerminalEnergySplit":
        return cls(e_heat=heat_power, e_return=return_power)
