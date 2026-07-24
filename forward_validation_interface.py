"""
Forward-validation interface (Milestone 6 prep, Part G)
============================================================

This module defines the INTERFACE for the forward-time validation stage
-- it does not implement a forward solver. Per the 2026-07-24 instruction:
"Do not begin controller retuning until the real a-priori placement
results are available." Nothing here should be treated as a working
integrator; every method raises NotImplementedError and exists only so
the shape of Milestone 6 is agreed on ahead of time.

The forward test is: initialize a model run from a real filtered DNS
snapshot,

    u_model(t0) = mean(u_DNS(t0))   [i.e. the filtered/resolved DNS field]

integrate forward with the terminal-layer model, and at each comparison
time t0 + n*dt compare against the DNS's own (real) evolution on:

  - kinetic-energy evolution
  - energy spectrum E(k)
  - nonlinear transfer T(k)
  - spectral flux Pi(k)
  - vorticity statistics
  - structure functions
  - terminal heat
  - backscatter
  - controller evolution (C_gamma / GP / GI, if the controller is active)

This is the only stage that can support a genuine predictive-accuracy
claim -- see report_generator.NOT_SUPPORTED_STATEMENTS. All milestones up
to and including 5 are a-priori (instantaneous or finite-difference)
comparisons and cannot substitute for it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from jhtdb_terminal_benchmark import Config


@dataclass(frozen=True)
class ForwardState:
    """Model state at some time t, produced by ForwardSolver.initialize()/step()."""

    velocity: np.ndarray  # (3, nz, ny, nx), real space
    time: float
    controller_state: dict = field(default_factory=dict)  # e.g. {"c_gamma": ...}


@dataclass(frozen=True)
class ForwardComparisonPoint:
    """The required comparison set at one forward-validation checkpoint
    (t0 + n*dt). Every field is None until Milestone 6 actually computes
    it -- this dataclass only fixes the required shape.
    """

    time: float
    kinetic_energy_evolution: dict | None = None
    energy_spectrum: dict | None = None
    nonlinear_transfer: dict | None = None
    spectral_flux: dict | None = None
    vorticity_statistics: dict | None = None
    structure_functions: dict | None = None
    terminal_heat: dict | None = None
    backscatter: dict | None = None
    controller_evolution: dict | None = None


class ForwardSolver(Protocol):
    """Interface a Milestone 6 forward integrator must implement. Not
    implemented here -- see module docstring."""

    def initialize(self, u_dns_t0: np.ndarray, cfg: Config) -> ForwardState:
        """u_model(t0) = filtered/resolved u_DNS(t0) -- see module docstring."""
        ...

    def step(self, state: ForwardState, dt: float) -> ForwardState:
        """Advance the model one confirmed Delta-t. Requires the same
        confirmed-dt discipline as measure_transfer.py / AGENTS.md -- no
        guessed time steps."""
        ...

    def compare_to_dns(self, state: ForwardState, dns_snapshot: np.ndarray) -> ForwardComparisonPoint:
        """Compare the evolved model state against a real DNS snapshot at
        the same time -- must populate every field of
        ForwardComparisonPoint, not a subset."""
        ...


class NotYetImplementedForwardSolver:
    """Placeholder concrete instance so calling code can be written and
    tested against the interface shape before Milestone 6 exists. Every
    method raises immediately -- there is no working forward solver yet.
    """

    def initialize(self, u_dns_t0: np.ndarray, cfg: Config) -> ForwardState:
        raise NotImplementedError(
            "Milestone 6 (forward-in-time validation) is not implemented. "
            "Do not attempt to fill this in until the Milestone 5 real-data "
            "a-priori placement results are available -- see README.md "
            "'Decision point after real execution'."
        )

    def step(self, state: ForwardState, dt: float) -> ForwardState:
        raise NotImplementedError("Milestone 6 forward integration is not implemented.")

    def compare_to_dns(self, state: ForwardState, dns_snapshot: np.ndarray) -> ForwardComparisonPoint:
        raise NotImplementedError("Milestone 6 forward-vs-DNS comparison is not implemented.")
