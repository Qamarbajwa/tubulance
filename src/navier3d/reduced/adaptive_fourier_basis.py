"""Transferable Adaptive Fourier Solenoidal Basis and Dynamic Wavevector Tracking.

Provides:
- AdaptiveFourierSolenoidalBasis: Universal transferable wavevector basis tracking active wavevector set K(t).
- EnergyEdgeActivationPolicy: Dynamically expands or prunes wavevector bandwidth based on boundary energy flux.
"""
from __future__ import annotations

from typing import List, Set, Tuple, Dict, Any, Optional
import numpy as np

from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet
from .solenoidal_basis import SolenoidalModalBasis, FourierSolenoidalBasis


class AdaptiveFourierSolenoidalBasis(FourierSolenoidalBasis):
    """Transferable Fourier solenoidal basis tracking active wavevector set K(t).

    Wavevector modes are domain-universal and independent of trajectory seed.
    """

    def __init__(
        self,
        mesh: StructuredMesh3D,
        initial_max_k: int = 2,
        max_allowed_k: int = 4,
        bcs: Optional[BoundaryConditionSet] = None,
        edge_energy_threshold: float = 0.01,
        hysteresis_prune_threshold: float = 0.001,
    ) -> None:
        self.current_max_k = initial_max_k
        self.max_allowed_k = max_allowed_k
        self.edge_energy_threshold = edge_energy_threshold
        self.hysteresis_prune_threshold = hysteresis_prune_threshold

        super().__init__(mesh, max_k_index=initial_max_k, bcs=bcs)
        self.active_indices: Set[int] = set(range(self.num_modes))

    def update_active_wavevectors(self, a: np.ndarray) -> Set[int]:
        """Check energy distribution near boundary wavevectors and adapt active set K(t)."""
        r = len(a)
        energies = a**2
        total_energy = float(np.sum(energies))
        if total_energy < 1e-15:
            return self.active_indices

        # Group modes by wavenumber magnitude k_mag
        lams = self.get_laplacian_eigenvalues()
        k_mags = np.sqrt(lams)

        max_k_active = self.current_max_k

        # Calculate energy fraction in the highest current wavenumber shell
        edge_mask = (k_mags >= max_k_active - 0.5) & (k_mags <= max_k_active + 0.5)
        edge_energy = float(np.sum(energies[edge_mask]))
        edge_ratio = edge_energy / total_energy

        # Expand bandwidth if edge energy is high
        if edge_ratio > self.edge_energy_threshold and self.current_max_k < self.max_allowed_k:
            self.current_max_k += 1
            # Rebuild underlying Fourier basis for larger k_max
            super().__init__(self.mesh, max_k_index=self.current_max_k, bcs=self.bcs)
            self.active_indices = set(range(self.num_modes))

        # Prune bandwidth if edge energy is very low
        elif edge_ratio < self.hysteresis_prune_threshold and self.current_max_k > 1:
            self.current_max_k -= 1
            super().__init__(self.mesh, max_k_index=self.current_max_k, bcs=self.bcs)
            self.active_indices = set(range(self.num_modes))

        return self.active_indices
