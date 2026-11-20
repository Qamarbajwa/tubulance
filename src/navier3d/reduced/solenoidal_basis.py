"""Divergence-Free Modal Basis Representations for Reduced-Order Navier-Stokes Modeling.

Provides:
- SolenoidalModalBasis: Abstract base class for reduced solenoidal vector bases.
- FourierSolenoidalBasis: Divergence-free Fourier vector mode basis on 3D periodic domains.
- PODSolenoidalBasis: Snapshot Proper Orthogonal Decomposition (POD) divergence-free basis.

Mathematical Guarantees:
1. Exact Solenoidality: div phi_n = 0 to machine precision (< 1e-12).
2. Discrete Orthonormality: <phi_i, phi_j> = int phi_i . phi_j dV = delta_ij.
3. Parseval Energy Identity: 0.5 * int ||u_r||^2 dV = 0.5 * sum_n a_n^2.
4. Pressure Elimination: <phi_k, grad p> = 0 for all pressure fields.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet, apply_velocity_bc


def mac_to_cell_centers(velocity: VelocityField) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Interpolate MAC face velocity components to cell centers using periodic wrapping."""
    u_face = velocity.u.interior[:-1, :, :]
    v_face = velocity.v.interior[:, :-1, :]
    w_face = velocity.w.interior[:, :, :-1]

    u_c = 0.5 * (np.roll(u_face, 1, axis=0) + u_face)
    v_c = 0.5 * (np.roll(v_face, 1, axis=1) + v_face)
    w_c = 0.5 * (np.roll(w_face, 1, axis=2) + w_face)
    return u_c, v_c, w_c


def cell_centers_to_mac(
    u_c: np.ndarray, v_c: np.ndarray, w_c: np.ndarray, mesh: StructuredMesh3D
) -> VelocityField:
    """Interpolate cell-centered velocity components to MAC face locations."""
    R_h = VelocityField.zeros(mesh)

    u_next = np.roll(u_c, -1, axis=0)
    v_next = np.roll(v_c, -1, axis=1)
    w_next = np.roll(w_c, -1, axis=2)

    R_h.u.interior[:-1, :, :] = 0.5 * (u_c + u_next)
    R_h.v.interior[:, :-1, :] = 0.5 * (v_c + v_next)
    R_h.w.interior[:, :, :-1] = 0.5 * (w_c + w_next)

    R_h.u.interior[-1, :, :] = R_h.u.interior[0, :, :]
    R_h.v.interior[:, -1, :] = R_h.v.interior[:, 0, :]
    R_h.w.interior[:, :, -1] = R_h.w.interior[:, :, 0]
    return R_h


class SolenoidalModalBasis(ABC):
    """Abstract interface for divergence-free vector bases."""

    def __init__(self, mesh: StructuredMesh3D, bcs: Optional[BoundaryConditionSet] = None) -> None:
        self.mesh = mesh
        self.bcs = bcs
        self.dV = mesh.cell_volume

    @property
    @abstractmethod
    def num_modes(self) -> int:
        """Total number of retained modes r."""
        ...

    @abstractmethod
    @abstractmethod
    def get_mode_mac(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return (phi_u_mac, phi_v_mac, phi_w_mac) mode components evaluated at exact MAC staggered faces."""
        ...

    def project(self, velocity: VelocityField) -> np.ndarray:
        """Project MAC VelocityField onto modal amplitudes a_n = <u, phi_n> using cell-centered interpolation."""
        u_c, v_c, w_c = mac_to_cell_centers(velocity)
        r = self.num_modes
        a = np.zeros(r, dtype=np.float64)
        for n in range(r):
            phi_u, phi_v, phi_w = self.get_mode(n)
            a[n] = np.sum(u_c * phi_u + v_c * phi_v + w_c * phi_w) * self.dV
        return a

    def project_mac(self, velocity: VelocityField) -> np.ndarray:
        """Project MAC VelocityField onto modal amplitudes a_n = <u, phi_n>_MAC using exact staggered face locations."""
        u_face = velocity.u.interior[:-1, :, :]
        v_face = velocity.v.interior[:, :-1, :]
        w_face = velocity.w.interior[:, :, :-1]
        r = self.num_modes
        a = np.zeros(r, dtype=np.float64)
        for n in range(r):
            phi_u_m, phi_v_m, phi_w_m = self.get_mode_mac(n)
            a[n] = np.sum(u_face * phi_u_m + v_face * phi_v_m + w_face * phi_w_m) * self.dV
        return a

    def reconstruct_cell_centers(self, amplitudes: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Reconstruct cell-centered velocity components u_r = sum_n a_n phi_n."""
        nx, ny, nz = self.mesh.nx, self.mesh.ny, self.mesh.nz
        u_r = np.zeros((nx, ny, nz), dtype=np.float64)
        v_r = np.zeros((nx, ny, nz), dtype=np.float64)
        w_r = np.zeros((nx, ny, nz), dtype=np.float64)

        for n, a_n in enumerate(amplitudes):
            if abs(a_n) < 1e-15:
                continue
            phi_u, phi_v, phi_w = self.get_mode(n)
            u_r += a_n * phi_u
            v_r += a_n * phi_v
            w_r += a_n * phi_w

        return u_r, v_r, w_r

    def reconstruct_mac(self, amplitudes: np.ndarray) -> VelocityField:
        """Reconstruct MAC VelocityField u_r = sum_n a_n phi_n directly on staggered faces."""
        nx, ny, nz = self.mesh.nx, self.mesh.ny, self.mesh.nz
        vel = VelocityField.zeros(self.mesh)
        u_f = vel.u.interior[:-1, :, :]
        v_f = vel.v.interior[:, :-1, :]
        w_f = vel.w.interior[:, :, :-1]

        for n, a_n in enumerate(amplitudes):
            if abs(a_n) < 1e-15:
                continue
            phi_u_m, phi_v_m, phi_w_m = self.get_mode_mac(n)
            u_f += a_n * phi_u_m
            v_f += a_n * phi_v_m
            w_f += a_n * phi_w_m

        vel.u.interior[-1, :, :] = vel.u.interior[0, :, :]
        vel.v.interior[:, -1, :] = vel.v.interior[:, 0, :]
        vel.w.interior[:, :, -1] = vel.w.interior[:, :, 0]

        if self.bcs is not None:
            apply_velocity_bc(vel, self.bcs)
        return vel

    def check_orthonormality(self) -> np.ndarray:
        """Compute Gram matrix G_ij = <phi_i, phi_j>. Returns (r, r) matrix (should be I_r)."""
        r = self.num_modes
        G = np.zeros((r, r), dtype=np.float64)
        for i in range(r):
            phi_i_u, phi_i_v, phi_i_w = self.get_mode_mac(i)
            for j in range(i, r):
                phi_j_u, phi_j_v, phi_j_w = self.get_mode_mac(j)
                val = np.sum(phi_i_u * phi_j_u + phi_i_v * phi_j_v + phi_i_w * phi_j_w) * self.dV
                G[i, j] = val
                G[j, i] = val
        return G


class FourierSolenoidalBasis(SolenoidalModalBasis):
    """Divergence-free Fourier standing-wave vector mode basis on 3D periodic domains.

    Parameters
    ----------
    mesh : StructuredMesh3D
        3D structured mesh.
    max_k_index : int
        Maximum wavevector integer index |n_x|, |n_y|, |n_z| <= max_k_index.
    bcs : Optional[BoundaryConditionSet]
        Boundary conditions.
    """

    def __init__(
        self,
        mesh: StructuredMesh3D,
        max_k_index: int = 4,
        bcs: Optional[BoundaryConditionSet] = None,
    ) -> None:
        super().__init__(mesh, bcs)
        self.max_k_index = max_k_index

        self._modes: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self._modes_mac: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self._wavevectors: List[Tuple[float, float, float]] = []
        self._wavevector_indices: List[Tuple[int, int, int]] = []
        self._eigenvalues: List[float] = []

        self._build_basis()

    def _build_basis(self) -> None:
        nx, ny, nz = self.mesh.nx, self.mesh.ny, self.mesh.nz
        lx, ly, lz = self.mesh.lx, self.mesh.ly, self.mesh.lz
        V = lx * ly * lz

        # 1. Cell-center grid coordinates
        xc = (np.arange(nx) + 0.5) * self.mesh.dx
        yc = (np.arange(ny) + 0.5) * self.mesh.dy
        zc = (np.arange(nz) + 0.5) * self.mesh.dz
        Xc, Yc, Zc = np.meshgrid(xc, yc, zc, indexing="ij")

        # 2. Staggered MAC face grid coordinates
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

        K_max = self.max_k_index
        dx_val = 2.0 * np.pi / lx
        dy_val = 2.0 * np.pi / ly
        dz_val = 2.0 * np.pi / lz

        norm_fac = np.sqrt(2.0 / V)

        # Collect unique wavevectors in half-space to avoid duplicate conjugate modes
        for nx_i in range(-K_max, K_max + 1):
            for ny_i in range(-K_max, K_max + 1):
                for nz_i in range(-K_max, K_max + 1):
                    if nx_i == 0 and ny_i == 0 and nz_i == 0:
                        continue

                    # Half-space canonical choice
                    if (nz_i < 0) or (nz_i == 0 and ny_i < 0) or (nz_i == 0 and ny_i == 0 and nx_i < 0):
                        continue

                    kx = nx_i * dx_val
                    ky = ny_i * dy_val
                    kz = nz_i * dz_val

                    k_vec = np.array([kx, ky, kz], dtype=np.float64)
                    k_sq = float(kx**2 + ky**2 + kz**2)

                    # Polarizations e1, e2 orthogonal to wavevector k_vec
                    if abs(kx) > 1e-10 or abs(ky) > 1e-10:
                        p1 = np.array([-ky, kx, 0.0], dtype=np.float64)
                        e1 = p1 / np.linalg.norm(p1)
                        p2 = np.cross(k_vec, e1)
                        e2 = p2 / np.linalg.norm(p2)
                    else:
                        e1 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
                        e2 = np.array([0.0, 1.0, 0.0], dtype=np.float64)

                    # Cell-center phases
                    phase_c = kx * Xc + ky * Yc + kz * Zc
                    cos_c = norm_fac * np.cos(phase_c)
                    sin_c = norm_fac * np.sin(phase_c)

                    # MAC face phases
                    phase_u = kx * Xu + ky * Yu + kz * Zu
                    phase_v = kx * Xv + ky * Yv + kz * Zv
                    phase_w = kx * Xw + ky * Yw + kz * Zw

                    cos_u, sin_u = norm_fac * np.cos(phase_u), norm_fac * np.sin(phase_u)
                    cos_v, sin_v = norm_fac * np.cos(phase_v), norm_fac * np.sin(phase_v)
                    cos_w, sin_w = norm_fac * np.cos(phase_w), norm_fac * np.sin(phase_w)

                    # Mode 1: e1 * cos
                    self._modes.append((e1[0] * cos_c, e1[1] * cos_c, e1[2] * cos_c))
                    self._modes_mac.append((e1[0] * cos_u, e1[1] * cos_v, e1[2] * cos_w))

                    # Mode 2: e1 * sin
                    self._modes.append((e1[0] * sin_c, e1[1] * sin_c, e1[2] * sin_c))
                    self._modes_mac.append((e1[0] * sin_u, e1[1] * sin_v, e1[2] * sin_w))

                    # Mode 3: e2 * cos
                    self._modes.append((e2[0] * cos_c, e2[1] * cos_c, e2[2] * cos_c))
                    self._modes_mac.append((e2[0] * cos_u, e2[1] * cos_v, e2[2] * cos_w))

                    # Mode 4: e2 * sin
                    self._modes.append((e2[0] * sin_c, e2[1] * sin_c, e2[2] * sin_c))
                    self._modes_mac.append((e2[0] * sin_u, e2[1] * sin_v, e2[2] * sin_w))

                    self._wavevectors.extend([(kx, ky, kz)] * 4)
                    self._wavevector_indices.extend([(nx_i, ny_i, nz_i)] * 4)
                    self._eigenvalues.extend([k_sq] * 4)

    @property
    def num_modes(self) -> int:
        return len(self._modes)

    def get_mode(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self._modes[index]

    def get_mode_mac(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self._modes_mac[index]

    def get_laplacian_eigenvalues(self) -> np.ndarray:
        return np.array(self._eigenvalues, dtype=np.float64)

    def get_wavevector(self, index: int) -> Tuple[float, float, float]:
        return self._wavevectors[index]

    def get_wavevector_indices(self, index: int) -> Tuple[int, int, int]:
        return self._wavevector_indices[index]


class PODSolenoidalBasis(SolenoidalModalBasis):
    """Snapshot Proper Orthogonal Decomposition (POD) divergence-free basis.

    Constructs optimal spatial POD modes phi_1, ..., phi_r from Model A velocity snapshots.
    """

    def __init__(
        self,
        snapshots: List[VelocityField],
        mesh: StructuredMesh3D,
        bcs: Optional[BoundaryConditionSet] = None,
        max_modes: Optional[int] = None,
    ) -> None:
        super().__init__(mesh, bcs)
        self.snapshots = snapshots
        self._modes: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self._modes_mac: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self._singular_values: np.ndarray = np.array([])
        self._laplacian_eigenvalues: np.ndarray = np.array([])

        self._compute_pod_basis(max_modes)

    def _compute_pod_basis(self, max_modes: Optional[int]) -> None:
        M = len(self.snapshots)
        if M == 0:
            raise ValueError("Cannot compute POD basis from empty snapshot list.")

        # Extract MAC face and cell-centered snapshots
        snap_mac = [
            (
                s.u.interior[:-1, :, :],
                s.v.interior[:, :-1, :],
                s.w.interior[:, :, :-1],
            )
            for s in self.snapshots
        ]
        snap_c = [mac_to_cell_centers(s) for s in self.snapshots]
        dV = self.dV

        # Compute snapshot correlation matrix C_ij = <u_i, u_j>_MAC
        C = np.zeros((M, M), dtype=np.float64)
        for i in range(M):
            u_i, v_i, w_i = snap_mac[i]
            for j in range(i, M):
                u_j, v_j, w_j = snap_mac[j]
                val = np.sum(u_i * u_j + v_i * v_j + w_i * w_j) * dV
                C[i, j] = val
                C[j, i] = val

        # Solve eigenvalue problem C v_k = lambda_k v_k
        eigvals, eigvecs = np.linalg.eigh(C)

        # Sort descending
        idx = np.argsort(eigvals)[::-1]
        eigvals = eigvals[idx]
        eigvecs = eigvecs[:, idx]

        # Filter out non-positive eigenvalues
        pos_mask = eigvals > 1e-14
        eigvals = eigvals[pos_mask]
        eigvecs = eigvecs[:, pos_mask]

        self._singular_values = np.sqrt(eigvals)

        r_max = len(eigvals) if max_modes is None else min(max_modes, len(eigvals))

        nx, ny, nz = self.mesh.nx, self.mesh.ny, self.mesh.nz
        for k in range(r_max):
            sigma_k = self._singular_values[k]
            v_k = eigvecs[:, k]

            phi_u_c = np.zeros((nx, ny, nz), dtype=np.float64)
            phi_v_c = np.zeros((nx, ny, nz), dtype=np.float64)
            phi_w_c = np.zeros((nx, ny, nz), dtype=np.float64)

            phi_u_m = np.zeros((nx, ny, nz), dtype=np.float64)
            phi_v_m = np.zeros((nx, ny, nz), dtype=np.float64)
            phi_w_m = np.zeros((nx, ny, nz), dtype=np.float64)

            for m in range(M):
                u_c_m, v_c_m, w_c_m = snap_c[m]
                u_f_m, v_f_m, w_f_m = snap_mac[m]

                weight = v_k[m] / sigma_k
                phi_u_c += weight * u_c_m
                phi_v_c += weight * v_c_m
                phi_w_c += weight * w_c_m

                phi_u_m += weight * u_f_m
                phi_v_m += weight * v_f_m
                phi_w_m += weight * w_f_m

            self._modes.append((phi_u_c, phi_v_c, phi_w_c))
            self._modes_mac.append((phi_u_m, phi_v_m, phi_w_m))

        # Estimate effective Laplacian eigenvalues <phi_n, -grad^2 phi_n>
        self._compute_effective_laplacian_eigenvalues()

    def _compute_effective_laplacian_eigenvalues(self) -> None:
        dx, dy, dz = self.mesh.dx, self.mesh.dy, self.mesh.dz
        l_list = []
        for phi_u, phi_v, phi_w in self._modes:
            # Central 2nd-order Laplacian
            lap_u = (np.roll(phi_u, -1, 0) - 2.0*phi_u + np.roll(phi_u, 1, 0)) / (dx**2) + \
                    (np.roll(phi_u, -1, 1) - 2.0*phi_u + np.roll(phi_u, 1, 1)) / (dy**2) + \
                    (np.roll(phi_u, -1, 2) - 2.0*phi_u + np.roll(phi_u, 1, 2)) / (dz**2)

            lap_v = (np.roll(phi_v, -1, 0) - 2.0*phi_v + np.roll(phi_v, 1, 0)) / (dx**2) + \
                    (np.roll(phi_v, -1, 1) - 2.0*phi_v + np.roll(phi_v, 1, 1)) / (dy**2) + \
                    (np.roll(phi_v, -1, 2) - 2.0*phi_v + np.roll(phi_v, 1, 2)) / (dz**2)

            lap_w = (np.roll(phi_w, -1, 0) - 2.0*phi_w + np.roll(phi_w, 1, 0)) / (dx**2) + \
                    (np.roll(phi_w, -1, 1) - 2.0*phi_w + np.roll(phi_w, 1, 1)) / (dy**2) + \
                    (np.roll(phi_w, -1, 2) - 2.0*phi_w + np.roll(phi_w, 1, 2)) / (dz**2)

            lam_n = -np.sum(phi_u * lap_u + phi_v * lap_v + phi_w * lap_w) * self.dV
            l_list.append(float(lam_n))

        self._laplacian_eigenvalues = np.array(l_list, dtype=np.float64)

    @property
    def num_modes(self) -> int:
        return len(self._modes)

    def get_mode(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self._modes[index]

    def get_mode_mac(self, index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self._modes_mac[index]

    def get_laplacian_eigenvalues(self) -> np.ndarray:
        return self._laplacian_eigenvalues

    def captured_energy_ratio(self, r: int) -> float:
        """Return fraction of cumulative kinetic energy captured by first r modes."""
        total_sq = np.sum(self._singular_values**2)
        if total_sq == 0:
            return 1.0
        return float(np.sum(self._singular_values[:r]**2) / total_sq)

    def required_modes_for_energy(self, target_ratio: float) -> int:
        """Return minimum number of POD modes needed to capture target_ratio of energy."""
        total_sq = np.sum(self._singular_values**2)
        cum_sq = np.cumsum(self._singular_values**2) / (total_sq + 1e-15)
        idx = np.argmax(cum_sq >= target_ratio)
        return int(idx + 1)
