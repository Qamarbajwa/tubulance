"""Clustered Local POD Bases with Continuous Subspace Projection Switching.

Provides:
- ClusteredLocalPODBasis: Collection of local POD bases {Phi^(1), ..., Phi^(M)} selecting the optimal subspace at runtime.
"""
from __future__ import annotations

from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet
from .solenoidal_basis import SolenoidalModalBasis, PODSolenoidalBasis
from .w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm


class ClusteredLocalPODBasis(SolenoidalModalBasis):
    """Collection of local POD bases {Phi^(1), ..., Phi^(M)} selecting the optimal subspace at runtime."""

    def __init__(
        self,
        local_snapshot_groups: List[List[VelocityField]],
        mesh: StructuredMesh3D,
        bcs: Optional[BoundaryConditionSet] = None,
        max_modes_per_cluster: int = 8,
    ) -> None:
        super().__init__(mesh, bcs)

        self.clusters: List[PODSolenoidalBasis] = []
        for group in local_snapshot_groups:
            if len(group) > 0:
                self.clusters.append(PODSolenoidalBasis(group, mesh, bcs, max_modes=max_modes_per_cluster))

        if len(self.clusters) == 0:
            raise ValueError("Must provide at least one non-empty local snapshot cluster.")

        self.active_cluster_idx: int = 0
        self.switch_count: int = 0

    @property
    def current_basis(self) -> PODSolenoidalBasis:
        return self.clusters[self.active_cluster_idx]

    @property
    def num_modes(self) -> int:
        return self.current_basis.num_modes

    def select_best_cluster(self, velocity: VelocityField) -> Tuple[int, float]:
        """Select local POD basis minimizing projection error for the given field state."""
        best_idx = self.active_cluster_idx
        norm_v = mac_velocity_norm(velocity, self.mesh)
        if norm_v < 1e-15:
            norm_v = 1.0

        best_err = 1e9

        for idx, basis in enumerate(self.clusters):
            a_proj = basis.project_mac(velocity)
            v_rec = basis.reconstruct_mac(a_proj)
            err = mac_velocity_diff_norm(velocity, v_rec, self.mesh) / norm_v

            if err < best_err:
                best_err = err
                best_idx = idx

        if best_idx != self.active_cluster_idx:
            self.active_cluster_idx = best_idx
            self.switch_count += 1

        return best_idx, float(best_err)

    def get_mode(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.current_basis.get_mode(index)

    def get_mode_mac(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.current_basis.get_mode_mac(index)

    def get_laplacian_eigenvalues(self) -> np.ndarray:
        return self.current_basis.get_laplacian_eigenvalues()
