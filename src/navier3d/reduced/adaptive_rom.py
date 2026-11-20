"""Adaptive Mode Activation, Enriched ROM, and Online Error Indicators.

Provides:
- AdaptiveSolenoidalROM: Dynamically manages active mode set A(t) based on modal energy thresholding with hysteresis.
- OnlineClosureErrorEstimator: Practical online residual & unresolved energy indicator.
- AdaptiveEnrichedROM: Enriches or prunes active modes when closure error indicator exceeds threshold tau.
"""
from __future__ import annotations

from typing import List, Set, Tuple, Dict, Any, Optional
import numpy as np

from ..fields import VelocityField
from .solenoidal_basis import SolenoidalModalBasis
from .modal_integrator import ModalODEIntegrator
from .w2_diagnostics import evaluate_pseudospectral_convection


class OnlineClosureErrorEstimator:
    """Computes practical online error indicators for reduced-order integration."""

    def __init__(self, basis: SolenoidalModalBasis, nu: float = 0.001) -> None:
        self.basis = basis
        self.nu = nu
        self.lams = basis.get_laplacian_eigenvalues()

    def estimate_residual_norm(
        self,
        a_curr: np.ndarray,
        a_prev: np.ndarray,
        dt: float,
        active_indices: Optional[Set[int]] = None,
    ) -> float:
        """Estimate closure residual norm ||R_closure|| online from recent steps."""
        if len(a_curr) != len(a_prev):
            return 0.0

        da_dt = (a_curr - a_prev) / dt

        # Evaluate RHS
        dot_a_visc = -self.nu * self.lams * a_curr
        dot_a_conv = evaluate_pseudospectral_convection(self.basis, a_curr)
        rhs_model = dot_a_visc + dot_a_conv

        res = da_dt - rhs_model

        if active_indices is not None:
            mask = np.zeros(len(res), dtype=bool)
            for idx in active_indices:
                if idx < len(res):
                    mask[idx] = True
            res = res[~mask]  # Unresolved residual

        return float(np.linalg.norm(res))


class AdaptiveSolenoidalROM:
    """Adaptive mode selection ROM maintaining active mode set A(t) with hysteresis."""

    def __init__(
        self,
        basis: SolenoidalModalBasis,
        nu: float = 0.001,
        energy_threshold: float = 0.999,
        hysteresis_factor: float = 0.1,
    ) -> None:
        self.basis = basis
        self.nu = nu
        self.r_full = basis.num_modes
        self.energy_threshold = energy_threshold
        self.hysteresis_factor = hysteresis_factor

        # Active set of mode indices
        self.active_set: Set[int] = set(range(min(4, self.r_full)))

    def update_active_set(self, a: np.ndarray) -> Set[int]:
        """Update active mode set A(t) based on modal energy thresholding with hysteresis."""
        r = len(a)
        energies = a**2
        total_energy = float(np.sum(energies))
        if total_energy < 1e-15:
            return self.active_set

        # Sort mode indices descending by energy
        sorted_indices = np.argsort(energies)[::-1]

        # Cumulative energy fraction
        cum_energy = np.cumsum(energies[sorted_indices]) / total_energy
        cutoff_idx = int(np.searchsorted(cum_energy, self.energy_threshold))
        cutoff_idx = min(cutoff_idx, r - 1)

        target_indices = set(sorted_indices[: cutoff_idx + 1])

        # Hysteresis: retain existing active modes unless their energy drops below hysteresis threshold
        min_active_energy = energies[sorted_indices[cutoff_idx]] * self.hysteresis_factor

        new_active = set(target_indices)
        for idx in self.active_set:
            if idx < r and energies[idx] >= min_active_energy:
                new_active.add(idx)

        self.active_set = new_active
        return self.active_set

    def evaluate_rhs_active(self, a: np.ndarray) -> np.ndarray:
        """Evaluate modal RHS zeroing out inactive modes."""
        # Standard pseudospectral RHS
        lams = self.basis.get_laplacian_eigenvalues()
        dot_a_visc = -self.nu * lams * a
        dot_a_conv = evaluate_pseudospectral_convection(self.basis, a)

        dot_a = dot_a_visc + dot_a_conv

        # Zero out inactive modes
        mask = np.zeros(len(a), dtype=bool)
        for idx in self.active_set:
            if idx < len(a):
                mask[idx] = True
        dot_a[~mask] = 0.0
        return dot_a

    def step_rk4(self, a: np.ndarray, dt: float) -> Tuple[np.ndarray, Set[int]]:
        """Advance modal state by one timestep using RK4 with adaptive active mode set."""
        k1 = self.evaluate_rhs_active(a)
        k2 = self.evaluate_rhs_active(a + 0.5 * dt * k1)
        k3 = self.evaluate_rhs_active(a + 0.5 * dt * k2)
        k4 = self.evaluate_rhs_active(a + dt * k3)

        a_next = a + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

        # Update active set
        active = self.update_active_set(a_next)
        return a_next, active

    def run(self, a0: np.ndarray, dt: float, n_steps: int) -> Tuple[np.ndarray, List[Set[int]]]:
        """Run adaptive ROM for n_steps."""
        a = a0.copy()
        history_active = [set(self.active_set)]
        for _ in range(n_steps):
            a, active = self.step_rk4(a, dt)
            history_active.append(set(active))
        return a, history_active


class AdaptiveEnrichedROM:
    """Enriches or prunes active mode count when online residual indicator exceeds tolerance tau."""

    def __init__(
        self,
        basis: SolenoidalModalBasis,
        nu: float = 0.001,
        tau_enrich: float = 0.05,
        tau_prune: float = 0.005,
        initial_modes: int = 4,
    ) -> None:
        self.basis = basis
        self.nu = nu
        self.tau_enrich = tau_enrich
        self.tau_prune = tau_prune
        self.estimator = OnlineClosureErrorEstimator(basis, nu)
        self.r_active = min(initial_modes, basis.num_modes)

    def step(self, a_curr: np.ndarray, a_prev: np.ndarray, dt: float) -> Tuple[np.ndarray, int, float]:
        """Check residual indicator and update active mode count r_active."""
        res_norm = self.estimator.estimate_residual_norm(a_curr, a_prev, dt)

        # Enrich if residual is large
        if res_norm > self.tau_enrich and self.r_active < self.basis.num_modes:
            self.r_active = min(self.basis.num_modes, self.r_active + 2)
        # Prune if residual is very small
        elif res_norm < self.tau_prune and self.r_active > 2:
            self.r_active = max(2, self.r_active - 1)

        # Mask inactive modes beyond r_active
        a_next = a_curr.copy()
        if self.r_active < len(a_next):
            a_next[self.r_active :] = 0.0

        return a_next, self.r_active, res_norm
