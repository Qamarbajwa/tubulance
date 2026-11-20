"""Quadratic Mode-Interaction Tensor and Nonlinear Convection Mechanics.

Provides:
- compute_mode_gradient: Computes spatial gradient tensor d phi_j / dx_l at cell centers.
- SparseModalTensor: Constructs and stores non-zero triadic interaction coefficients Q_kij.
- evaluate_pseudospectral_convection: Computes modal nonlinear acceleration via grid evaluation.

Mathematical Property:
Skew-symmetry Q_kij = -Q_jik guarantees strict inviscid energy conservation:
sum_k a_k (sum_ij Q_kij a_i a_j) = 0.
"""
from __future__ import annotations

from typing import List, Tuple, Dict
import numpy as np

from .solenoidal_basis import SolenoidalModalBasis
from ..mesh import StructuredMesh3D


def compute_mode_gradient(
    phi_u: np.ndarray, phi_v: np.ndarray, phi_w: np.ndarray, mesh: StructuredMesh3D
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute cell-centered 3D derivatives d(phi_u, phi_v, phi_w) / d(x, y, z) using central differences."""
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    du_dx = (np.roll(phi_u, -1, 0) - np.roll(phi_u, 1, 0)) / (2.0 * dx)
    du_dy = (np.roll(phi_u, -1, 1) - np.roll(phi_u, 1, 1)) / (2.0 * dy)
    du_dz = (np.roll(phi_u, -1, 2) - np.roll(phi_u, 1, 2)) / (2.0 * dz)

    dv_dx = (np.roll(phi_v, -1, 0) - np.roll(phi_v, 1, 0)) / (2.0 * dx)
    dv_dy = (np.roll(phi_v, -1, 1) - np.roll(phi_v, 1, 1)) / (2.0 * dy)
    dv_dz = (np.roll(phi_v, -1, 2) - np.roll(phi_v, 1, 2)) / (2.0 * dz)

    dw_dx = (np.roll(phi_w, -1, 0) - np.roll(phi_w, 1, 0)) / (2.0 * dx)
    dw_dy = (np.roll(phi_w, -1, 1) - np.roll(phi_w, 1, 1)) / (2.0 * dy)
    dw_dz = (np.roll(phi_w, -1, 2) - np.roll(phi_w, 1, 2)) / (2.0 * dz)

    return du_dx, du_dy, du_dz, dv_dx, dv_dy, dv_dz, dw_dx, dw_dy, dw_dz


class SparseModalTensor:
    """Explicit sparse representation of modal quadratic interaction tensor Q_kij.

    Q_kij = - < phi_k, (phi_i . grad) phi_j >
    """

    def __init__(self, basis: SolenoidalModalBasis, tol: float = 1e-12) -> None:
        self.basis = basis
        self.tol = tol
        self.r = basis.num_modes

        # Store triadic list as tuple of numpy arrays for vectorized ODE evaluation
        self.k_indices: np.ndarray = np.array([], dtype=np.int32)
        self.i_indices: np.ndarray = np.array([], dtype=np.int32)
        self.j_indices: np.ndarray = np.array([], dtype=np.int32)
        self.values: np.ndarray = np.array([], dtype=np.float64)

        self._build_tensor()

    def _build_tensor(self) -> None:
        r = self.r
        mesh = self.basis.mesh
        dV = mesh.cell_volume

        k_list, i_list, j_list, val_list = [], [], [], []

        # Precompute gradient components for all modes
        grads = []
        modes = []
        for n in range(r):
            phi = self.basis.get_mode(n)
            modes.append(phi)
            grads.append(compute_mode_gradient(phi[0], phi[1], phi[2], mesh))

        k_idx_vecs = [self.basis.get_wavevector_indices(n) for n in range(r)] if hasattr(self.basis, "get_wavevector_indices") else None

        Q_dense = np.zeros((r, r, r), dtype=np.float64)

        for k in range(r):
            phi_k_u, phi_k_v, phi_k_w = modes[k]
            kk = k_idx_vecs[k] if k_idx_vecs is not None else None
            for i in range(r):
                phi_i_u, phi_i_v, phi_i_w = modes[i]
                ki = k_idx_vecs[i] if k_idx_vecs is not None else None
                for j in range(r):
                    if k_idx_vecs is not None:
                        kj = k_idx_vecs[j]
                        # Triad selection rule: k_k must equal ± k_i ± k_j
                        sum1 = (ki[0] + kj[0], ki[1] + kj[1], ki[2] + kj[2])
                        sum2 = (ki[0] - kj[0], ki[1] - kj[1], ki[2] - kj[2])
                        sum3 = (-ki[0] + kj[0], -ki[1] + kj[1], -ki[2] + kj[2])
                        sum4 = (-ki[0] - kj[0], -ki[1] - kj[1], -ki[2] - kj[2])
                        if kk != sum1 and kk != sum2 and kk != sum3 and kk != sum4:
                            continue
                    du_dx, du_dy, du_dz, dv_dx, dv_dy, dv_dz, dw_dx, dw_dy, dw_dz = grads[j]

                    # (phi_i . grad) phi_j component-wise
                    conv_u = phi_i_u * du_dx + phi_i_v * du_dy + phi_i_w * du_dz
                    conv_v = phi_i_u * dv_dx + phi_i_v * dv_dy + phi_i_w * dv_dz
                    conv_w = phi_i_u * dw_dx + phi_i_v * dw_dy + phi_i_w * dw_dz

                    # Q_kij = - < phi_k, (phi_i . grad) phi_j >
                    Q_dense[k, i, j] = -np.sum(phi_k_u * conv_u + phi_k_v * conv_v + phi_k_w * conv_w) * dV

        # Skew-symmetrize Q_skew = 0.5 * (Q - Q^T_{k<->j}) for exact discrete inviscid energy conservation
        Q_skew = 0.5 * (Q_dense - np.transpose(Q_dense, (2, 1, 0)))

        mask = np.abs(Q_skew) > self.tol
        self.k_indices, self.i_indices, self.j_indices = np.where(mask)
        self.values = Q_skew[self.k_indices, self.i_indices, self.j_indices]

    @property
    def num_nonzero(self) -> int:
        return len(self.values)

    @property
    def sparsity_ratio(self) -> float:
        """Ratio of non-zero interaction terms N_Q to total dense tensor size r^3."""
        total_possible = self.r ** 3
        if total_possible == 0:
            return 0.0
        return float(self.num_nonzero / total_possible)

    def evaluate_convection_acceleration(self, a: np.ndarray) -> np.ndarray:
        """Compute modal non-linear convection acceleration dot_a_conv_k = sum_ij Q_kij a_i a_j."""
        dot_a = np.zeros(self.r, dtype=np.float64)
        if len(self.values) == 0:
            return dot_a

        # Vectorized accumulation
        term_vals = self.values * a[self.i_indices] * a[self.j_indices]
        np.add.at(dot_a, self.k_indices, term_vals)
        return dot_a

    def verify_energy_conservation(self, a: np.ndarray) -> float:
        """Compute total non-linear kinetic energy transfer work W_conv = sum_k a_k dot_a_conv_k."""
        dot_a = self.evaluate_convection_acceleration(a)
        return float(np.sum(a * dot_a))


def evaluate_pseudospectral_convection(basis: SolenoidalModalBasis, a: np.ndarray) -> np.ndarray:
    """Compute modal non-linear convection acceleration via spatial grid evaluation.

    1. Reconstruct cell-centered velocity u_r = sum_n a_n phi_n.
    2. Compute f_conv(x) = - (u_r . grad) u_r.
    3. Project f_conv onto modes: dot_a_k = < f_conv, phi_k >.
    """
    mesh = basis.mesh
    u_c, v_c, w_c = basis.reconstruct_cell_centers(a)

    du_dx, du_dy, du_dz, dv_dx, dv_dy, dv_dz, dw_dx, dw_dy, dw_dz = compute_mode_gradient(u_c, v_c, w_c, mesh)

    f_u = -(u_c * du_dx + v_c * du_dy + w_c * du_dz)
    f_v = -(u_c * dv_dx + v_c * dv_dy + w_c * dv_dz)
    f_w = -(u_c * dw_dx + v_c * dw_dy + w_c * dw_dz)

    dV = mesh.cell_volume
    r = basis.num_modes
    dot_a = np.zeros(r, dtype=np.float64)

    for n in range(r):
        phi_u, phi_v, phi_w = basis.get_mode(n)
        dot_a[n] = np.sum(f_u * phi_u + f_v * phi_v + f_w * phi_w) * dV

    return dot_a
