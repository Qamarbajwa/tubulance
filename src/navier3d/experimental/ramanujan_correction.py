"""Experimental Spectral Corrections for navier3d.

Provides:
- SpectralCorrection: Abstract base class for optional velocity spectral corrections.
- RamanujanCorrection: Ramanujan-inspired quadratic spectral scale interaction correction.

Retained strictly for mathematical research and non-production testing.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np
from scipy.fft import fftfreq, irfftn, rfftfreq, rfftn

from ..boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from ..projection import project


class SpectralCorrection(ABC):
    """Abstract interface for optional spectral corrections R_h(u)."""

    @abstractmethod
    def evaluate(
        self,
        velocity: VelocityField,
        mesh: StructuredMesh3D,
        bcs: Optional[BoundaryConditionSet] = None,
    ) -> VelocityField:
        """Evaluate correction acceleration R_h(u) at MAC face locations."""
        pass


class RamanujanCorrection(SpectralCorrection):
    """Ramanujan-inspired quadratic spectral scale interaction correction.

    Parameters
    ----------
    lambda_ : float
        Coupling coefficient scale lambda.
    alpha : float, default 1.0
        Spectral wavenumber power exponent for non-local scale weighting.
    k_ref : float, default 1.0
        Reference wavenumber scaling factor.
    k_c : float, optional
        High-wavenumber exponential cutoff. If None, no cutoff is applied.
    dealiasing : bool, default True
        Whether to apply 2/3 truncation dealiasing to the quadratic term.
    """

    def __init__(
        self,
        lambda_: float = 1.0,
        alpha: float = 1.0,
        k_ref: float = 1.0,
        k_c: Optional[float] = None,
        dealiasing: bool = True,
    ) -> None:
        self.lambda_ = float(lambda_)
        self.alpha = float(alpha)
        self.k_ref = float(k_ref)
        self.k_c = float(k_c) if k_c is not None else None
        self.dealiasing = bool(dealiasing)

    def _get_wavenumbers(
        self, mesh: StructuredMesh3D
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Compute 3D wavenumber arrays for a uniform periodic mesh."""
        lx, ly, lz = mesh.lx, mesh.ly, mesh.lz
        nx, ny, nz = mesh.nx, mesh.ny, mesh.nz

        kx = 2.0 * np.pi * fftfreq(nx, d=lx / nx)
        ky = 2.0 * np.pi * fftfreq(ny, d=ly / ny)
        kz = 2.0 * np.pi * rfftfreq(nz, d=lz / nz)

        KX, KY, KZ = np.meshgrid(kx, ky, kz, indexing="ij")
        K_sq = KX**2 + KY**2 + KZ**2
        K_mag = np.sqrt(K_sq)
        return KX, KY, KZ, K_sq, K_mag

    def _mac_to_cell_centers(self, velocity: VelocityField) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Interpolate MAC face velocity components to cell centers."""
        u_face = velocity.u.interior[:-1, :, :]
        v_face = velocity.v.interior[:, :-1, :]
        w_face = velocity.w.interior[:, :, :-1]

        u_prev = np.roll(u_face, 1, axis=0)
        v_prev = np.roll(v_face, 1, axis=1)
        w_prev = np.roll(w_face, 1, axis=2)

        u_c = 0.5 * (u_prev + u_face)
        v_c = 0.5 * (v_prev + v_face)
        w_c = 0.5 * (w_prev + w_face)
        return u_c, v_c, w_c

    def _cell_centers_to_mac(
        self, R_uc: np.ndarray, R_vc: np.ndarray, R_wc: np.ndarray, mesh: StructuredMesh3D
    ) -> VelocityField:
        """Interpolate cell-centered correction components to MAC faces."""
        R_h = VelocityField.zeros(mesh)

        u_next = np.roll(R_uc, -1, axis=0)
        v_next = np.roll(R_vc, -1, axis=1)
        w_next = np.roll(R_wc, -1, axis=2)

        # Faces 0 to nx-1
        R_h.u.interior[:-1, :, :] = 0.5 * (R_uc + u_next)
        R_h.v.interior[:, :-1, :] = 0.5 * (R_vc + v_next)
        R_h.w.interior[:, :, :-1] = 0.5 * (R_wc + w_next)

        # Duplicate face nx = face 0 for periodic completeness
        R_h.u.interior[-1, :, :] = R_h.u.interior[0, :, :]
        R_h.v.interior[:, -1, :] = R_h.v.interior[:, 0, :]
        R_h.w.interior[:, :, -1] = R_h.w.interior[:, :, 0]

        return R_h

    def evaluate(
        self,
        velocity: VelocityField,
        mesh: StructuredMesh3D,
        bcs: Optional[BoundaryConditionSet] = None,
    ) -> VelocityField:
        """Evaluate the Ramanujan quadratic spectral correction R_h(u)."""
        if abs(self.lambda_) < 1e-15:
            return VelocityField.zeros(mesh)

        u_c, v_c, w_c = self._mac_to_cell_centers(velocity)

        # 3D rfft of cell-centered velocity
        u_hat = rfftn(u_c)
        v_hat = rfftn(v_c)
        w_hat = rfftn(w_c)

        KX, KY, KZ, K_sq, K_mag = self._get_wavenumbers(mesh)

        # Compute vorticity in spectral space: w_hat(k) = i k x u_hat(k)
        wx_hat = 1j * (KY * w_hat - KZ * v_hat)
        wy_hat = 1j * (KZ * u_hat - KX * w_hat)
        wz_hat = 1j * (KX * v_hat - KY * u_hat)

        # Spectral scale weight W(k)
        W = (K_mag / self.k_ref) ** self.alpha
        if self.k_c is not None and self.k_c > 0:
            W = W * np.exp(-K_mag / self.k_c)
        W[K_mag == 0] = 0.0

        # Scale-weighted vorticity field in spectral space
        wsx_hat = W * wx_hat
        wsy_hat = W * wy_hat
        wsz_hat = W * wz_hat

        # Inverse FFT of vorticity fields
        wx_c = irfftn(wx_hat, s=(mesh.nx, mesh.ny, mesh.nz))
        wy_c = irfftn(wy_hat, s=(mesh.nx, mesh.ny, mesh.nz))
        wz_c = irfftn(wz_hat, s=(mesh.nx, mesh.ny, mesh.nz))

        wsx_c = irfftn(wsx_hat, s=(mesh.nx, mesh.ny, mesh.nz))
        wsy_c = irfftn(wsy_hat, s=(mesh.nx, mesh.ny, mesh.nz))
        wsz_c = irfftn(wsz_hat, s=(mesh.nx, mesh.ny, mesh.nz))

        # Galilean-invariant physical cross product Q_c(x) = w_c(x) x ws_c(x)
        Qx_c = wy_c * wsz_c - wz_c * wsy_c
        Qy_c = wz_c * wsx_c - wx_c * wsz_c
        Qz_c = wx_c * wsy_c - wy_c * wsx_c

        # 3D FFT of Q_c
        Qx_hat = rfftn(Qx_c)
        Qy_hat = rfftn(Qy_c)
        Qz_hat = rfftn(Qz_c)

        # Dealiasing (2/3 rule)
        if self.dealiasing:
            kx_max = np.pi / mesh.dx
            ky_max = np.pi / mesh.dy
            kz_max = np.pi / mesh.dz
            k_cutoff = (2.0 / 3.0) * min(kx_max, ky_max, kz_max)
            mask = K_mag > k_cutoff
            Qx_hat[mask] = 0.0
            Qy_hat[mask] = 0.0
            Qz_hat[mask] = 0.0

        # Transform dealiased Q back to physical space
        Qx_c = irfftn(Qx_hat, s=(mesh.nx, mesh.ny, mesh.nz))
        Qy_c = irfftn(Qy_hat, s=(mesh.nx, mesh.ny, mesh.nz))
        Qz_c = irfftn(Qz_hat, s=(mesh.nx, mesh.ny, mesh.nz))

        # Scale by lambda
        Qx_c *= self.lambda_
        Qy_c *= self.lambda_
        Qz_c *= self.lambda_

        # Interpolate to MAC faces
        Q_h = self._cell_centers_to_mac(Qx_c, Qy_c, Qz_c, mesh)
        if bcs is not None:
            apply_velocity_bc(Q_h, bcs)

        # Compute fluctuating velocity u' = u - mean(u)
        mean_u = float(np.mean(u_c))
        mean_v = float(np.mean(v_c))
        mean_w = float(np.mean(w_c))

        up = VelocityField.zeros(mesh)
        up.u.interior[:] = velocity.u.interior - mean_u
        up.v.interior[:] = velocity.v.interior - mean_v
        up.w.interior[:] = velocity.w.interior - mean_w

        # Project Q_h orthogonal to fluctuating velocity u'
        dV = mesh.cell_volume
        u_dot_q = sum(
            np.sum(up_comp.interior[:-1, :, :] * q_comp.interior[:-1, :, :] if axis == 0 else
                   (up_comp.interior[:, :-1, :] * q_comp.interior[:, :-1, :] if axis == 1 else
                    up_comp.interior[:, :, :-1] * q_comp.interior[:, :, :-1]))
            for axis, (up_comp, q_comp) in enumerate(zip(up.components(), Q_h.components()))
        ) * dV

        u_norm_sq = sum(
            np.sum(up_comp.interior[:-1, :, :] ** 2 if axis == 0 else
                   (up_comp.interior[:, :-1, :] ** 2 if axis == 1 else
                    up_comp.interior[:, :, :-1] ** 2))
            for axis, up_comp in enumerate(up.components())
        ) * dV

        c_proj = float(u_dot_q / (u_norm_sq + 1e-15))
        Q_neutral = VelocityField.zeros(mesh)
        for axis, (q_out, q_in, up_in) in enumerate(zip(Q_neutral.components(), Q_h.components(), up.components())):
            q_out.interior[:] = q_in.interior - c_proj * up_in.interior

        if bcs is not None:
            apply_velocity_bc(Q_neutral, bcs)

        # Final Discrete MAC Leray Projection D_h R_h = 0
        if bcs is not None:
            proj_res = project(Q_neutral, bcs, mesh, rho=1.0, dt=1.0, solver="direct", null_space_strategy="pin_cell")
            R_h = proj_res.velocity
        else:
            R_h = Q_neutral

        return R_h

    def compute_energy_transfer_work(
        self, velocity: VelocityField, mesh: StructuredMesh3D, bcs: Optional[BoundaryConditionSet] = None
    ) -> float:
        """Compute net energy transfer work W_R = < u, R_h(u) > = int u . R_h(u) dV."""
        R_h = self.evaluate(velocity, mesh, bcs)
        dV = mesh.cell_volume
        W_R = float(
            sum(
                np.sum(u_comp.interior[:-1, :, :] * r_comp.interior[:-1, :, :] if axis == 0 else
                       (u_comp.interior[:, :-1, :] * r_comp.interior[:, :-1, :] if axis == 1 else
                        u_comp.interior[:, :, :-1] * r_comp.interior[:, :, :-1]))
                for axis, (u_comp, r_comp) in enumerate(zip(velocity.components(), R_h.components()))
            )
            * dV
        )
        return W_R
