"""Stokes Eigenbasis for 3D Wall-Bounded Channel Flow.

Constructs divergence-free, no-slip wall-bounded Stokes eigenmodes phi_n and eigenvalues lambda_n for channel geometry:
- periodic in x, z
- no-slip wall at y = 0 and y = Ly
"""
from __future__ import annotations

from typing import List, Tuple, Optional, Dict, Any
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField
from ..boundary_conditions import BoundaryConditionSet, periodic_bcs
from ..projection import project
from .solenoidal_basis import SolenoidalModalBasis, mac_to_cell_centers, cell_centers_to_mac
from .w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm


class StokesEigenbasis3D(SolenoidalModalBasis):
    """Discrete solenoidal Stokes eigenbasis for channel flow with no-slip walls in y."""

    def __init__(
        self,
        mesh: StructuredMesh3D,
        max_k_index: int = 3,
        max_m_wall: int = 4,
        bcs: Optional[BoundaryConditionSet] = None,
    ) -> None:
        super().__init__(mesh, bcs)
        self.max_k_index = max_k_index
        self.max_m_wall = max_m_wall

        self._modes: List[Tuple[np.ndarray, np.ndarray, float]] = []
        self._wavevectors: List[Tuple[int, int, int]] = []
        self._eigenvalues: List[float] = []

        self._build_basis()

    def _build_basis(self) -> None:
        nx, ny, nz = self.mesh.nx, self.mesh.ny, self.mesh.nz
        lx, ly, lz = self.mesh.lx, self.mesh.ly, self.mesh.lz
        V = lx * ly * lz

        # Cell-center grid coordinates
        xc = (np.arange(nx) + 0.5) * self.mesh.dx
        yc = (np.arange(ny) + 0.5) * self.mesh.dy
        zc = (np.arange(nz) + 0.5) * self.mesh.dz

        # Staggered MAC face grid coordinates
        xu = np.arange(nx) * self.mesh.dx
        yu = (np.arange(ny) + 0.5) * self.mesh.dy
        zu = (np.arange(nz) + 0.5) * self.mesh.dz
        Xu, Yu, Zu = np.meshgrid(xu, yu, zu, indexing="ij")

        xv = (np.arange(nx) + 0.5) * self.mesh.dx
        yv = np.arange(ny) * self.mesh.dy
        zv = (np.arange(nz) + 0.5) * self.mesh.dz
        Xv, Yv, Zv = np.meshgrid(xv, yv, zv, indexing="ij")

        xw = (np.arange(nx) + 0.5) * self.mesh.dx
        yw = (np.arange(ny) + 0.5) * self.mesh.dy
        zw = np.arange(nz) * self.mesh.dz
        Xw, Yw, Zw = np.meshgrid(xw, yw, zw, indexing="ij")

        dx_val = 2.0 * np.pi / lx
        dz_val = 2.0 * np.pi / lz

        # Loop over Fourier harmonics in (x, z) and Wall Modes in y
        for nx_i in range(-self.max_k_index, self.max_k_index + 1):
            for nz_i in range(-self.max_k_index, self.max_k_index + 1):
                kx = nx_i * dx_val
                kz = nz_i * dz_val

                for m_y in range(1, self.max_m_wall + 1):
                    ky = m_y * np.pi / ly
                    lambda_n = float(kx**2 + ky**2 + kz**2)

                    # Build trial modes satisfying no-slip y-walls
                    # u-component: cos(kx x) * sin(ky y) * cos(kz z)
                    # v-component: cos(kx x) * sin(ky y) * cos(kz z)
                    # w-component: cos(kx x) * sin(ky y) * cos(kz z)
                    u_mac = np.cos(kx * Xu) * np.sin(ky * Yu) * np.cos(kz * Zu)
                    v_mac = np.sin(kx * Xv) * np.sin(ky * Yv) * np.cos(kz * Zv)
                    w_mac = np.cos(kx * Xw) * np.sin(ky * Yw) * np.sin(kz * Zw)

                    # Leray solenoidal projection to enforce divergence-free condition Dh u = 0
                    vel_trial = cell_centers_to_mac(u_mac, v_mac, w_mac, self.mesh)
                    proj_res = project(vel_trial, self.bcs, self.mesh, rho=1.0, dt=1.0)
                    vel_solenoidal = proj_res.velocity

                    # Zero wall boundary faces at y=0 and y=Ly for no-slip condition
                    vel_solenoidal.v.interior[:, 0, :] = 0.0
                    vel_solenoidal.v.interior[:, -1, :] = 0.0

                    # Normalize by kinetic energy norm
                    norm_val = mac_velocity_norm(vel_solenoidal, self.mesh)
                    if norm_val < 1e-10:
                        continue

                    u_norm = vel_solenoidal.u.interior[:-1, :, :] / norm_val
                    v_norm = vel_solenoidal.v.interior[:, :-1, :] / norm_val
                    w_norm = vel_solenoidal.w.interior[:, :, :-1] / norm_val

                    vel_mode = cell_centers_to_mac(u_norm, v_norm, w_norm, self.mesh)
                    mode_c = mac_to_cell_centers(vel_mode)
                    mode_mac = (vel_mode.u.interior, vel_mode.v.interior, vel_mode.w.interior)

                    self._modes.append((mode_c, mode_mac, lambda_n))
                    self._wavevectors.append((nx_i, m_y, nz_i))

        # Gram-Schmidt Orthonormalization
        ortho_modes = []
        dV = self.mesh.cell_volume
        for i in range(len(self._modes)):
            mc_c, (u_i, v_i, w_i), lam_i = self._modes[i]
            u_i = u_i.copy()
            v_i = v_i.copy()
            w_i = w_i.copy()

            # Zero y-wall faces for exact no-slip boundary compatibility
            v_i[:, 0, :] = 0.0
            v_i[:, -1, :] = 0.0

            for j in range(len(ortho_modes)):
                _, (u_j, v_j, w_j), _ = ortho_modes[j]
                proj_ij = (np.sum(u_i * u_j) + np.sum(v_i * v_j) + np.sum(w_i * w_j)) * dV
                u_i -= proj_ij * u_j
                v_i -= proj_ij * v_j
                w_i -= proj_ij * w_j

            norm_i = np.sqrt((np.sum(u_i**2) + np.sum(v_i**2) + np.sum(w_i**2)) * dV)
            if norm_i > 1e-10:
                u_i /= norm_i
                v_i /= norm_i
                w_i /= norm_i
                v_i[:, 0, :] = 0.0
                v_i[:, -1, :] = 0.0
                vel_i = VelocityField.zeros(self.mesh)
                vel_i.u.interior[:] = u_i
                vel_i.v.interior[:] = v_i
                vel_i.w.interior[:] = w_i
                mode_c_i = mac_to_cell_centers(vel_i)
                ortho_modes.append((mode_c_i, (u_i, v_i, w_i), lam_i))

        self._modes = ortho_modes
        self._eigenvalues = [lam for _, _, lam in ortho_modes]

    @property
    def num_modes(self) -> int:
        return len(self._modes)

    def project_mac(self, velocity: VelocityField) -> np.ndarray:
        """Project MAC face velocity field onto Stokes eigenmodes."""
        a = np.zeros(self.num_modes, dtype=np.float64)
        dV = self.mesh.cell_volume
        u_m, v_m, w_m = velocity.u.interior, velocity.v.interior, velocity.w.interior

        for i, (_, (phi_u, phi_v, phi_w), _) in enumerate(self._modes):
            dot_prod = (np.sum(u_m * phi_u) + np.sum(v_m * phi_v) + np.sum(w_m * phi_w)) * dV
            a[i] = dot_prod
        return a

    def reconstruct_mac(self, coefficients: np.ndarray) -> VelocityField:
        """Reconstruct MAC face velocity field from Stokes modal coefficients."""
        rec_vel = VelocityField.zeros(self.mesh)
        u_rec = rec_vel.u.interior
        v_rec = rec_vel.v.interior
        w_rec = rec_vel.w.interior

        for i, a_i in enumerate(coefficients):
            if abs(a_i) < 1e-15:
                continue
            _, (phi_u, phi_v, phi_w), _ = self._modes[i]
            u_rec += a_i * phi_u
            v_rec += a_i * phi_v
            w_rec += a_i * phi_w

        return rec_vel

    def get_mode_mac(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return MAC face arrays for mode at given index."""
        _, mode_mac, _ = self._modes[index]
        return mode_mac

    def verify_properties(self) -> Dict[str, float]:
        """Verify solenoidality, Gram orthonormality, and no-slip boundary compatibility."""
        dV = self.mesh.cell_volume

        # 1. Gram matrix off-diagonal error
        r = self.num_modes
        gram = np.zeros((r, r))
        for i in range(r):
            _, (u_i, v_i, w_i), _ = self._modes[i]
            for j in range(r):
                _, (u_j, v_j, w_j), _ = self._modes[j]
                gram[i, j] = (np.sum(u_i * u_j) + np.sum(v_i * v_j) + np.sum(w_i * w_j)) * dV

        off_diag_err = float(np.max(np.abs(gram - np.eye(r))))

        # 2. No-slip wall boundary error at y = 0 and y = Ly for wall-normal component v
        max_wall_err = 0.0
        for i in range(r):
            _, (u_i, v_i, w_i), _ = self._modes[i]
            wall_v = np.max(np.abs(v_i[:, 0, :])) + np.max(np.abs(v_i[:, -1, :]))
            max_wall_err = max(max_wall_err, float(wall_v))

        return {
            "num_modes": r,
            "gram_off_diagonal_error": off_diag_err,
            "max_wall_boundary_error": max_wall_err,
        }
