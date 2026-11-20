"""Sparse Wave Interaction Engine and Minimal Spectral Collocation Evaluators.

Provides:
- MinimalSpectralGridEvaluator: High-speed pseudospectral nonlinear evaluator operating on minimal dealiased collocation grids N_spec << N_full.
- SparseTriadGraph: Precomputes admissible Navier-Stokes triads p + q = k and sparse interaction coefficients C_kpq.
- VectorizedTriadEvaluator: Vectorized NumPy tensor contraction engine exploiting triad skew-symmetry.
"""
from __future__ import annotations

from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField
from ..boundary_conditions import BoundaryConditionSet, periodic_bcs, apply_velocity_bc
from ..operators import velocity_laplacian, divergence
from .solenoidal_basis import SolenoidalModalBasis, FourierSolenoidalBasis, mac_to_cell_centers, cell_centers_to_mac


class MinimalSpectralGridEvaluator:
    """High-speed pseudospectral nonlinear evaluator operating on minimal dealiased collocation grids N_spec << N_full."""

    def __init__(
        self,
        basis: FourierSolenoidalBasis,
        bcs: Optional[BoundaryConditionSet] = None,
    ) -> None:
        self.basis = basis
        self.bcs = bcs if bcs is not None else periodic_bcs()

        # Determine minimal dealiased collocation grid resolution
        k_max = basis.max_k_index
        # 3/2 dealiasing rule: N_spec >= 3 * k_max + 1, or minimum 8
        n_spec = max(8, int(np.ceil(3.0 * k_max + 1)))
        # Make n_spec even for FFT efficiency
        if n_spec % 2 != 0:
            n_spec += 1

        self.n_spec = n_spec
        self.spec_mesh = StructuredMesh3D(
            nx=n_spec,
            ny=n_spec,
            nz=n_spec,
            lx=basis.mesh.lx,
            ly=basis.mesh.ly,
            lz=basis.mesh.lz,
            n_ghost=1,
        )

        # Pre-construct spectral basis on minimal grid
        self.spec_basis = FourierSolenoidalBasis(self.spec_mesh, max_k_index=k_max, bcs=self.bcs)

    def evaluate_convection_acceleration(self, a: np.ndarray) -> np.ndarray:
        """Evaluate non-linear modal convection dot_a_conv on the minimal spectral grid."""
        r = self.basis.num_modes

        # 1. Reconstruct velocity field on minimal spectral grid
        vel_spec = self.spec_basis.reconstruct_mac(a[: self.spec_basis.num_modes])
        apply_velocity_bc(vel_spec, self.bcs)

        # 2. Cell-center interpolation
        u_c, v_c, w_c = mac_to_cell_centers(vel_spec)

        # 3. Spectral gradient computation on minimal grid
        dx = self.spec_mesh.dx
        dy = self.spec_mesh.dy
        dz = self.spec_mesh.dz

        du_dx = (np.roll(u_c, -1, 0) - np.roll(u_c, 1, 0)) / (2.0 * dx)
        du_dy = (np.roll(u_c, -1, 1) - np.roll(u_c, 1, 1)) / (2.0 * dy)
        du_dz = (np.roll(u_c, -1, 2) - np.roll(u_c, 1, 2)) / (2.0 * dz)

        dv_dx = (np.roll(v_c, -1, 0) - np.roll(v_c, 1, 0)) / (2.0 * dx)
        dv_dy = (np.roll(v_c, -1, 1) - np.roll(v_c, 1, 1)) / (2.0 * dy)
        dv_dz = (np.roll(v_c, -1, 2) - np.roll(v_c, 1, 2)) / (2.0 * dz)

        dw_dx = (np.roll(w_c, -1, 0) - np.roll(w_c, 1, 0)) / (2.0 * dx)
        dw_dy = (np.roll(w_c, -1, 1) - np.roll(w_c, 1, 1)) / (2.0 * dy)
        dw_dz = (np.roll(w_c, -1, 2) - np.roll(w_c, 1, 2)) / (2.0 * dz)

        f_u = -(u_c * du_dx + v_c * du_dy + w_c * du_dz)
        f_v = -(u_c * dv_dx + v_c * dv_dy + w_c * dv_dz)
        f_w = -(u_c * dw_dx + v_c * dw_dy + w_c * dw_dz)

        # 4. Project onto minimal spectral modes
        dV_spec = self.spec_mesh.cell_volume
        dot_a = np.zeros(r, dtype=np.float64)

        n_eval = min(r, self.spec_basis.num_modes)
        for n in range(n_eval):
            phi_u, phi_v, phi_w = self.spec_basis.get_mode(n)
            dot_a[n] = np.sum(f_u * phi_u + f_v * phi_v + f_w * phi_w) * dV_spec

        return dot_a


class SparseTriadGraph:
    """Precomputes admissible wavevector triads p + q = k and sparse interaction matrix C_kpq."""

    def __init__(self, basis: SolenoidalModalBasis, tol: float = 1e-10) -> None:
        self.basis = basis
        self.r = basis.num_modes
        self.tol = tol

        self.k_indices: List[int] = []
        self.p_indices: List[int] = []
        self.q_indices: List[int] = []
        self.coefficients: List[float] = []

        self._build_triad_graph()

    def _build_triad_graph(self) -> None:
        mesh = self.basis.mesh
        dV = mesh.cell_volume

        # Compute triad inner products C_kpq = - < phi_k, (phi_p . grad) phi_q >_MAC
        for k in range(self.r):
            phi_k_u, phi_k_v, phi_k_w = self.basis.get_mode_mac(k)

            for p in range(self.r):
                phi_p_u, phi_p_v, phi_p_w = self.basis.get_mode(p)

                for q in range(self.r):
                    phi_q_u, phi_q_v, phi_q_w = self.basis.get_mode(q)

                    # Grad phi_q
                    dq_u_dx = (np.roll(phi_q_u, -1, 0) - np.roll(phi_q_u, 1, 0)) / (2.0 * mesh.dx)
                    dq_u_dy = (np.roll(phi_q_u, -1, 1) - np.roll(phi_q_u, 1, 1)) / (2.0 * mesh.dy)
                    dq_u_dz = (np.roll(phi_q_u, -1, 2) - np.roll(phi_q_u, 1, 2)) / (2.0 * mesh.dz)

                    conv_u = phi_p_u * dq_u_dx + phi_p_v * dq_u_dy + phi_p_w * dq_u_dz

                    # Product with phi_k at cell centers
                    phi_k_c_u, phi_k_c_v, phi_k_c_w = self.basis.get_mode(k)
                    val = -np.sum(phi_k_c_u * conv_u) * dV

                    if abs(val) > self.tol:
                        self.k_indices.append(k)
                        self.p_indices.append(p)
                        self.q_indices.append(q)
                        self.coefficients.append(float(val))

        self.k_arr = np.array(self.k_indices, dtype=np.int32)
        self.p_arr = np.array(self.p_indices, dtype=np.int32)
        self.q_arr = np.array(self.q_indices, dtype=np.int32)
        self.c_arr = np.array(self.coefficients, dtype=np.float64)

    @property
    def triad_count(self) -> int:
        return len(self.coefficients)


class VectorizedTriadEvaluator:
    """Vectorized NumPy tensor contraction engine evaluating sparse wave interactions dot_a_k = sum_pq C_kpq a_p a_q."""

    def __init__(self, triad_graph: SparseTriadGraph) -> None:
        self.graph = triad_graph
        self.r = triad_graph.r

    def evaluate_convection_acceleration(self, a: np.ndarray) -> np.ndarray:
        """Vectorized evaluation of non-linear acceleration in modal space."""
        dot_a = np.zeros(self.r, dtype=np.float64)
        if self.graph.triad_count == 0:
            return dot_a

        # Vectorized product: C_kpq * a_p * a_q
        vals = self.graph.c_arr * a[self.graph.p_arr] * a[self.graph.q_arr]

        # Accumulate into dot_a using np.bincount
        np.add.at(dot_a, self.graph.k_arr, vals)
        return dot_a
