"""Ensemble POD and Hybrid Fourier-POD Solenoidal Bases for Reduced-Order Navier-Stokes Modeling.

Provides:
- EnsemblePODSolenoidalBasis: Constructs snapshot POD modes from multi-realization / multi-Re snapshot sets.
- HybridSolenoidalBasis: Combines Fourier (large-scale) and POD modes with Gram-Schmidt MAC face orthonormalization.
"""
from __future__ import annotations

from typing import List, Tuple, Optional
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet
from .solenoidal_basis import SolenoidalModalBasis, FourierSolenoidalBasis, PODSolenoidalBasis, mac_to_cell_centers


class EnsemblePODSolenoidalBasis(PODSolenoidalBasis):
    """Snapshot POD basis constructed across multiple trajectories / realizations / Reynolds numbers."""

    def __init__(
        self,
        snapshot_collections: List[List[VelocityField]],
        mesh: StructuredMesh3D,
        bcs: Optional[BoundaryConditionSet] = None,
        max_modes: Optional[int] = None,
    ) -> None:
        # Flatten snapshot collections
        flat_snapshots = [s for coll in snapshot_collections for s in coll]
        if len(flat_snapshots) == 0:
            raise ValueError("Ensemble snapshot list cannot be empty.")
        super().__init__(flat_snapshots, mesh, bcs=bcs, max_modes=max_modes)


class HybridSolenoidalBasis(SolenoidalModalBasis):
    """Hybrid basis combining Fourier solenoidal modes and POD solenoidal modes.

    Orthonormalized using Modified Gram-Schmidt under the staggered MAC face inner product:
      < u, v >_MAC = sum ( u_x v_x + u_y v_y + u_z v_z ) * dV
    """

    def __init__(
        self,
        mesh: StructuredMesh3D,
        fourier_max_k: int = 1,
        pod_basis: Optional[PODSolenoidalBasis] = None,
        num_pod_modes: Optional[int] = None,
        bcs: Optional[BoundaryConditionSet] = None,
    ) -> None:
        super().__init__(mesh, bcs)

        self._modes: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self._modes_mac: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self._laplacian_eigenvalues: List[float] = []

        self._build_hybrid_basis(fourier_max_k, pod_basis, num_pod_modes)

    def _build_hybrid_basis(
        self,
        fourier_max_k: int,
        pod_basis: Optional[PODSolenoidalBasis],
        num_pod_modes: Optional[int],
    ) -> None:
        # 1. Collect initial raw candidates: Fourier modes first, then POD modes
        fourier_base = FourierSolenoidalBasis(self.mesh, max_k_index=fourier_max_k, bcs=self.bcs)

        candidates_c: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        candidates_mac: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        lams: List[float] = []

        # Add Fourier modes
        for n in range(fourier_base.num_modes):
            candidates_c.append(fourier_base.get_mode(n))
            candidates_mac.append(fourier_base.get_mode_mac(n))
            lams.append(float(fourier_base.get_laplacian_eigenvalues()[n]))

        # Add POD modes if provided
        if pod_basis is not None and pod_basis.num_modes > 0:
            n_pod = pod_basis.num_modes if num_pod_modes is None else min(num_pod_modes, pod_basis.num_modes)
            for n in range(n_pod):
                candidates_c.append(pod_basis.get_mode(n))
                candidates_mac.append(pod_basis.get_mode_mac(n))
                lams.append(float(pod_basis.get_laplacian_eigenvalues()[n]))

        # 2. Perform Modified Gram-Schmidt on MAC face components to enforce exact MAC orthonormality
        dV = self.dV
        num_cand = len(candidates_mac)

        ortho_mac: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        ortho_c: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        ortho_lams: List[float] = []

        for k in range(num_cand):
            u_m, v_m, w_m = candidates_mac[k]
            u_c, v_c, w_c = candidates_c[k]

            u_m = u_m.copy()
            v_m = v_m.copy()
            w_m = w_m.copy()

            u_c = u_c.copy()
            v_c = v_c.copy()
            w_c = w_c.copy()

            # Subtract projections onto previously orthogonalized modes
            for j in range(len(ortho_mac)):
                uj_m, vj_m, wj_m = ortho_mac[j]
                uj_c, vj_c, wj_c = ortho_c[j]

                proj = np.sum(u_m * uj_m + v_m * vj_m + w_m * wj_m) * dV

                u_m -= proj * uj_m
                v_m -= proj * vj_m
                w_m -= proj * wj_m

                u_c -= proj * uj_c
                v_c -= proj * vj_c
                w_c -= proj * wj_c

            # Check norm
            norm = np.sqrt(np.sum(u_m**2 + v_m**2 + w_m**2) * dV)
            if norm > 1e-8:
                ortho_mac.append((u_m / norm, v_m / norm, w_m / norm))
                ortho_c.append((u_c / norm, v_c / norm, w_c / norm))
                ortho_lams.append(lams[k])

        self._modes = ortho_c
        self._modes_mac = ortho_mac
        self._laplacian_eigenvalues = ortho_lams

    @property
    def num_modes(self) -> int:
        return len(self._modes)

    def get_mode(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self._modes[index]

    def get_mode_mac(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self._modes_mac[index]

    def get_laplacian_eigenvalues(self) -> np.ndarray:
        return np.array(self._laplacian_eigenvalues, dtype=np.float64)
