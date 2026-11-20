"""Subgrid-scale (SGS) turbulence models for Large-Eddy Simulation (LES).

Provides the LESModel interface, SmagorinskyModel, and DynamicSmagorinskyModel closures:
- Static Smagorinsky:
    nu_t = (C_s * f_d * Delta)^2 * |S|
    Delta = (dx * dy * dz)^(1/3)

- Dynamic Smagorinsky:
    Calculates dynamic coefficient C_d = C_s^2 from Germano identity:
    L_ij^d = L_ij - (1/3) L_kk delta_ij
    M_ij = -2 [ Delta_hat^2 |S_hat| S_hat_ij - Filter(Delta^2 |S| S_ij) ]
    C_d = (L^d : M) / (M : M + reg_eps)

Guarantees:
- Positivity nu_t >= 0 (in non-negative clipping mode).
- Exact regression for C_s = 0 / zero strain.
- Non-finite (NaN/Inf) detection.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import warnings
import numpy as np

from .boundary_conditions import BoundaryConditionSet, VelocityBCType
from .fields import ScalarField, VelocityField
from .mesh import StructuredMesh3D
from .strain import compute_strain_components, compute_strain_magnitude


class LESModel(ABC):
    """Abstract base class for subgrid-scale turbulence models."""

    @abstractmethod
    def eddy_viscosity(
        self,
        velocity: VelocityField,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet | None = None,
        nu: float = 1e-3,
        rho: float = 1.0,
    ) -> ScalarField:
        """Compute eddy viscosity nu_t at cell centers."""
        ...


class SmagorinskyModel(LESModel):
    """Classic Smagorinsky SGS eddy-viscosity closure.

    Parameters
    ----------
    cs : float
        Smagorinsky model coefficient C_s >= 0.
    wall_damping : str | bool | None, default=None
        Damping model name:
        - None / False: No wall damping.
        - "geometric" / True: Empirical geometry-based surrogate damping f_d = 1 - exp(-y_w / Delta).
        - "van_driest": True wall-unit van Driest damping f_d = 1 - exp(-y^+ / A^+).
    wall_damping_scale : float, default=1.0
        Damping length scale factor for geometric damping.
    a_plus : float, default=26.0
        Van Driest damping constant A^+.
    """

    def __init__(
        self,
        cs: float,
        wall_damping: str | bool | None = None,
        wall_damping_scale: float = 1.0,
        a_plus: float = 26.0,
    ) -> None:
        if cs < 0.0:
            raise ValueError(f"Smagorinsky coefficient cs must be non-negative, got {cs}")
        self.cs = float(cs)

        if wall_damping is True:
            warnings.warn(
                "wall_damping=True is deprecated; use wall_damping='geometric' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.wall_damping = "geometric"
        elif wall_damping is False or wall_damping is None:
            self.wall_damping = None
        elif isinstance(wall_damping, str):
            mode = wall_damping.lower()
            if mode not in ("geometric", "van_driest"):
                raise ValueError(f"Invalid wall_damping mode: '{wall_damping}'. Must be 'geometric' or 'van_driest'.")
            self.wall_damping = mode
        else:
            raise ValueError(f"Invalid wall_damping argument type: {type(wall_damping)}")

        self.wall_damping_scale = float(wall_damping_scale)
        self.a_plus = float(a_plus)

    def filter_width(self, mesh: StructuredMesh3D) -> float:
        """Geometric-mean filter width Delta = (dx * dy * dz)^(1/3)."""
        return float((mesh.dx * mesh.dy * mesh.dz) ** (1.0 / 3.0))

    def _compute_wall_distance(
        self, mesh: StructuredMesh3D, bcs: BoundaryConditionSet | None
    ) -> np.ndarray | None:
        """Compute minimum distance from cell centers to physical no-slip walls."""
        if bcs is None or self.wall_damping is None:
            return None

        wall_faces = []
        if bcs.x_min.velocity_type == VelocityBCType.NO_SLIP:
            wall_faces.append(("x", 0.0))
        if bcs.x_max.velocity_type == VelocityBCType.NO_SLIP:
            wall_faces.append(("x", mesh.lx))
        if bcs.y_min.velocity_type == VelocityBCType.NO_SLIP:
            wall_faces.append(("y", 0.0))
        if bcs.y_max.velocity_type == VelocityBCType.NO_SLIP:
            wall_faces.append(("y", mesh.ly))
        if bcs.z_min.velocity_type == VelocityBCType.NO_SLIP:
            wall_faces.append(("z", 0.0))
        if bcs.z_max.velocity_type == VelocityBCType.NO_SLIP:
            wall_faces.append(("z", mesh.lz))

        if not wall_faces:
            return None

        Xc, Yc, Zc = np.meshgrid(
            mesh.cell_centers_x(), mesh.cell_centers_y(), mesh.cell_centers_z(), indexing="ij"
        )
        dist_min = np.full((mesh.nx, mesh.ny, mesh.nz), np.inf)

        for axis, pos in wall_faces:
            if axis == "x":
                dist_min = np.minimum(dist_min, np.abs(Xc - pos))
            elif axis == "y":
                dist_min = np.minimum(dist_min, np.abs(Yc - pos))
            elif axis == "z":
                dist_min = np.minimum(dist_min, np.abs(Zc - pos))

        return dist_min

    def _compute_wall_shear_rate(
        self, velocity: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet | None
    ) -> float:
        """Estimate characteristic wall shear rate |du_parallel / dn|_wall on MAC grid."""
        if bcs is None:
            return 0.0

        rates = []
        ng = mesh.n_ghost
        u, v, w = velocity.u.data, velocity.v.data, velocity.w.data

        # Check y_min / y_max no-slip wall shear
        if bcs.y_min.velocity_type == VelocityBCType.NO_SLIP:
            u_wall = np.abs(u[ng : ng + mesh.nx + 1, ng, ng : ng + mesh.nz])
            rates.append(np.mean(u_wall) / (0.5 * mesh.dy))
        if bcs.y_max.velocity_type == VelocityBCType.NO_SLIP:
            u_wall = np.abs(u[ng : ng + mesh.nx + 1, ng + mesh.ny - 1, ng : ng + mesh.nz])
            rates.append(np.mean(u_wall) / (0.5 * mesh.dy))

        if not rates:
            return 1.0
        return float(np.mean(rates))

    def eddy_viscosity(
        self,
        velocity: VelocityField,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet | None = None,
        nu: float = 1e-3,
        rho: float = 1.0,
    ) -> ScalarField:
        """Compute Smagorinsky eddy viscosity nu_t at cell centers."""
        nu_t = ScalarField.zeros(mesh)
        if self.cs == 0.0:
            return nu_t

        s_mag = compute_strain_magnitude(velocity, mesh, bcs)
        delta = self.filter_width(mesh)
        cs_eff = self.cs

        if self.wall_damping is not None:
            wall_dist = self._compute_wall_distance(mesh, bcs)
            if wall_dist is not None:
                if self.wall_damping == "geometric":
                    f_d = 1.0 - np.exp(-wall_dist / (self.wall_damping_scale * delta))
                elif self.wall_damping == "van_driest":
                    shear_rate = self._compute_wall_shear_rate(velocity, mesh, bcs)
                    tau_w = rho * nu * shear_rate
                    u_tau = np.sqrt(max(1e-12, tau_w / rho))
                    y_plus = (wall_dist * u_tau) / max(1e-12, nu)
                    f_d = 1.0 - np.exp(-y_plus / self.a_plus)
                else:
                    f_d = 1.0
                cs_eff = self.cs * f_d

        nu_t_val = ((cs_eff * delta) ** 2) * s_mag.interior
        if not np.all(np.isfinite(nu_t_val)):
            raise ValueError("Non-finite values (NaN/Inf) encountered in Smagorinsky eddy viscosity")

        if np.any(nu_t_val < -1e-15):
            raise ValueError(f"Negative eddy viscosity encountered: min={np.min(nu_t_val)}")

        nu_t.interior[:] = np.maximum(0.0, nu_t_val)
        return nu_t


def _box_filter_3d(arr: np.ndarray, size: int = 3) -> np.ndarray:
    """Apply periodic 3D uniform box filter of size x size x size to arr."""
    half = size // 2
    pad_arr = np.pad(arr, ((half, half), (half, half), (half, half)), mode="wrap")
    out = np.zeros_like(arr)
    count = size ** 3
    for i in range(size):
        for j in range(size):
            for k in range(size):
                out += pad_arr[i : i + arr.shape[0], j : j + arr.shape[1], k : k + arr.shape[2]]
    return out / count


class DynamicSmagorinskyModel(LESModel):
    """Dynamic Smagorinsky model using Germano identity and least-squares coefficient estimation.

    Parameters
    ----------
    test_filter_ratio : float, default=2.0
        Ratio alpha = Delta_hat / Delta of test filter to grid filter width.
    averaging_mode : str, default="global"
        Coefficient averaging mode: "global", "local", "plane", or "neighborhood".
    neighborhood_size : int, default=3
        Box filter size (3 or 5) for "neighborhood" volume averaging.
    coefficient_clipping : str, default="nonnegative"
        Clipping policy: "nonnegative" (C_d >= 0) or "none".
    allow_backscatter : bool, default=False
        Whether to permit negative eddy viscosity (backscatter).
    c_d_max : float, default=0.25
        Maximum bound for C_d = C_s^2.
    reg_eps : float, default=1e-8
        Denominator regularization factor.
    """

    def __init__(
        self,
        test_filter_ratio: float = 2.0,
        averaging_mode: str = "global",
        neighborhood_size: int = 3,
        coefficient_clipping: str = "nonnegative",
        allow_backscatter: bool = False,
        c_d_max: float = 0.25,
        reg_eps: float = 1e-8,
    ) -> None:
        if test_filter_ratio <= 1.0:
            raise ValueError(f"test_filter_ratio must be > 1.0, got {test_filter_ratio}")
        self.test_filter_ratio = float(test_filter_ratio)

        avg_mode = averaging_mode.lower()
        if avg_mode not in ("global", "local", "plane", "neighborhood"):
            raise ValueError(f"Invalid averaging_mode '{averaging_mode}'. Must be 'global', 'local', 'plane', or 'neighborhood'.")
        self.averaging_mode = avg_mode
        self.neighborhood_size = int(neighborhood_size)

        clip_mode = coefficient_clipping.lower()
        if clip_mode not in ("nonnegative", "none"):
            raise ValueError(f"Invalid coefficient_clipping '{coefficient_clipping}'. Must be 'nonnegative' or 'none'.")
        self.coefficient_clipping = clip_mode

        self.allow_backscatter = allow_backscatter
        self.c_d_max = float(c_d_max)
        self.reg_eps = float(reg_eps)

        self._last_diagnostics: dict = {}

    def filter_width(self, mesh: StructuredMesh3D) -> float:
        """Geometric-mean filter width Delta = (dx * dy * dz)^(1/3)."""
        return float((mesh.dx * mesh.dy * mesh.dz) ** (1.0 / 3.0))

    def get_last_diagnostics(self) -> dict:
        """Retrieve dynamic coefficient statistics and Germano residual from last evaluation."""
        return dict(self._last_diagnostics)

    def eddy_viscosity(
        self,
        velocity: VelocityField,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet | None = None,
        nu: float = 1e-3,
        rho: float = 1.0,
    ) -> ScalarField:
        """Compute dynamic eddy viscosity nu_t at cell centers."""
        from .filtering import compute_germano_tensors

        # 1. Compute Germano tensors L_ij^d, M_ij, L_M (P), M_M (Q)
        L_dev, M_dev, P, Q = compute_germano_tensors(
            velocity, mesh, bcs=bcs, test_filter_ratio=self.test_filter_ratio
        )

        q_mean = float(np.mean(Q))
        denom_eps = self.reg_eps * max(1e-15, q_mean)

        # 2. Compute raw pre-clipping coefficient field C_d_raw = P / (Q + eps)
        c_d_raw = P / (Q + denom_eps)

        # 3. Apply averaging strategy
        if self.averaging_mode == "global":
            p_sum = float(np.sum(P))
            q_sum = float(np.sum(Q))
            c_d_raw_scalar = p_sum / (q_sum + denom_eps)
            c_d_grid = np.full((mesh.nx, mesh.ny, mesh.nz), c_d_raw_scalar)
        elif self.averaging_mode == "plane":
            # Average P and Q over xy-planes for each z
            p_plane = np.mean(P, axis=(0, 1), keepdims=True)
            q_plane = np.mean(Q, axis=(0, 1), keepdims=True)
            c_d_plane = p_plane / (q_plane + denom_eps)
            c_d_grid = np.broadcast_to(c_d_plane, (mesh.nx, mesh.ny, mesh.nz)).copy()
        elif self.averaging_mode == "neighborhood":
            # Ratio of 3D box-filtered spatial volume averages: A[P] / A[Q]
            p_avg = _box_filter_3d(P, size=self.neighborhood_size)
            q_avg = _box_filter_3d(Q, size=self.neighborhood_size)
            c_d_grid = p_avg / (q_avg + denom_eps)
        else:  # local (pointwise)
            c_d_grid = np.copy(c_d_raw)

        c_d_pre_clip = np.copy(c_d_grid)

        # 4. Clipping and backscatter policies
        if self.coefficient_clipping == "nonnegative" and not self.allow_backscatter:
            c_d_grid = np.maximum(0.0, c_d_grid)

        c_d_grid = np.minimum(self.c_d_max, c_d_grid)

        # 5. Compute dynamic eddy viscosity nu_t = C_d * Delta^2 * |S|
        s_mag = compute_strain_magnitude(velocity, mesh, bcs)
        delta = self.filter_width(mesh)
        delta_sq = delta ** 2

        nu_t_val = c_d_grid * delta_sq * s_mag.interior

        if not self.allow_backscatter:
            nu_t_val = np.maximum(0.0, nu_t_val)
        else:
            # Safety floor: nu + nu_t >= 0.1 * nu => nu_t >= -0.9 * nu
            nu_t_val = np.maximum(-0.9 * nu, nu_t_val)

        if not np.all(np.isfinite(nu_t_val)):
            raise ValueError("Non-finite values (NaN/Inf) encountered in dynamic eddy viscosity")

        nu_t = ScalarField.zeros(mesh)
        nu_t.interior[:] = nu_t_val

        # 6. Diagnostic statistics & raw Numerator/Denominator tracking
        c_d_nonneg = np.maximum(0.0, c_d_grid)
        c_s_equiv = np.sqrt(c_d_nonneg)

        # Germano residual R_ij = L_ij^d - C_d * M_ij
        res_sq = 0.0
        for comp in ("xx", "yy", "zz", "xy", "xz", "yz"):
            factor = 1.0 if comp in ("xx", "yy", "zz") else 2.0
            r_comp = L_dev[comp] - c_d_grid * M_dev[comp]
            res_sq += np.sum(factor * (r_comp ** 2))

        germano_res = float(np.sqrt(res_sq / max(1, mesh.nx * mesh.ny * mesh.nz)))

        p_pos = np.maximum(0.0, P)
        p_neg = np.minimum(0.0, P)

        self._last_diagnostics = {
            "c_d_mean": float(np.mean(c_d_grid)),
            "c_d_min": float(np.min(c_d_grid)),
            "c_d_max": float(np.max(c_d_grid)),
            "c_d_median": float(np.median(c_d_grid)),
            "c_d_p90": float(np.percentile(c_d_grid, 90)),
            "c_d_p99": float(np.percentile(c_d_grid, 99)),
            "c_d_raw_mean": float(np.mean(c_d_raw)),
            "c_d_raw_min": float(np.min(c_d_raw)),
            "c_d_raw_max": float(np.max(c_d_raw)),
            "c_d_raw_median": float(np.median(c_d_raw)),
            "c_d_raw_p1": float(np.percentile(c_d_raw, 1)),
            "c_d_raw_p10": float(np.percentile(c_d_raw, 10)),
            "c_d_raw_p90": float(np.percentile(c_d_raw, 90)),
            "c_d_raw_p99": float(np.percentile(c_d_raw, 99)),
            "P_mean": float(np.mean(P)),
            "Q_mean": float(np.mean(Q)),
            "P_pos_mean": float(np.mean(p_pos)),
            "P_neg_mean": float(np.mean(p_neg)),
            "f_minus": float(np.mean(c_d_raw < 0.0)),
            "c_s_equiv_mean": float(np.mean(c_s_equiv)),
            "c_s_equiv_max": float(np.max(c_s_equiv)),
            "clipped_fraction": float(np.mean(c_d_pre_clip < 0.0)) if self.coefficient_clipping == "nonnegative" else 0.0,
            "germano_residual": germano_res,
        }

        return nu_t


def _compute_cell_velocity_gradients(
    velocity: VelocityField, mesh: StructuredMesh3D
) -> dict[str, np.ndarray]:
    """Compute all 9 components of velocity gradient tensor g_ij = du_i / dx_j at cell centers."""
    u_face = velocity.u.interior[:-1, :, :]
    v_face = velocity.v.interior[:, :-1, :]
    w_face = velocity.w.interior[:, :, :-1]

    u_c = 0.5 * (np.roll(u_face, 1, axis=0) + u_face)
    v_c = 0.5 * (np.roll(v_face, 1, axis=1) + v_face)
    w_c = 0.5 * (np.roll(w_face, 1, axis=2) + w_face)

    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    du_dx = (np.roll(u_c, -1, axis=0) - np.roll(u_c, 1, axis=0)) / (2.0 * dx)
    du_dy = (np.roll(u_c, -1, axis=1) - np.roll(u_c, 1, axis=1)) / (2.0 * dy)
    du_dz = (np.roll(u_c, -1, axis=2) - np.roll(u_c, 1, axis=2)) / (2.0 * dz)

    dv_dx = (np.roll(v_c, -1, axis=0) - np.roll(v_c, 1, axis=0)) / (2.0 * dx)
    dv_dy = (np.roll(v_c, -1, axis=1) - np.roll(v_c, 1, axis=1)) / (2.0 * dy)
    dv_dz = (np.roll(v_c, -1, axis=2) - np.roll(v_c, 1, axis=2)) / (2.0 * dz)

    dw_dx = (np.roll(w_c, -1, axis=0) - np.roll(w_c, 1, axis=0)) / (2.0 * dx)
    dw_dy = (np.roll(w_c, -1, axis=1) - np.roll(w_c, 1, axis=1)) / (2.0 * dy)
    dw_dz = (np.roll(w_c, -1, axis=2) - np.roll(w_c, 1, axis=2)) / (2.0 * dz)

    return {
        "du_dx": du_dx, "du_dy": du_dy, "du_dz": du_dz,
        "dv_dx": dv_dx, "dv_dy": dv_dy, "dv_dz": dv_dz,
        "dw_dx": dw_dx, "dw_dy": dw_dy, "dw_dz": dw_dz,
    }


class WALEModel(LESModel):
    """Wall-Adapting Local Eddy-viscosity (WALE) SGS closure (Nicoud & Ducros 1999).

    Computes eddy viscosity nu_t = (C_w * Delta)^2 * (S_sd^3/2) / (S_mag^5 + S_sd^5/4 + eps).
    Automatically yields nu_t -> 0 at wall boundaries without wall-damping functions.

    Parameters
    ----------
    cw : float, default=0.325
        WALE model constant C_w >= 0.
    eps : float, default=1e-12
        Regularization parameter to prevent division by zero.
    """

    def __init__(self, cw: float = 0.325, eps: float = 1e-12) -> None:
        if cw < 0.0:
            raise ValueError(f"WALE model coefficient cw must be non-negative, got {cw}")
        self.cw = float(cw)
        self.eps = float(eps)

    def filter_width(self, mesh: StructuredMesh3D) -> float:
        """Geometric-mean filter width Delta = (dx * dy * dz)^(1/3)."""
        return float((mesh.dx * mesh.dy * mesh.dz) ** (1.0 / 3.0))

    def eddy_viscosity(
        self,
        velocity: VelocityField,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet | None = None,
        nu: float = 1e-3,
        rho: float = 1.0,
    ) -> ScalarField:
        """Compute WALE eddy viscosity nu_t at cell centers."""
        if self.cw == 0.0:
            return ScalarField.zeros(mesh)

        g = _compute_cell_velocity_gradients(velocity, mesh)

        # g_ij g_jk matrix product components
        g11, g12, g13 = g["du_dx"], g["du_dy"], g["du_dz"]
        g21, g22, g23 = g["dv_dx"], g["dv_dy"], g["dv_dz"]
        g31, g32, g33 = g["dw_dx"], g["dw_dy"], g["dw_dz"]

        # g2_ij = g_ik g_kj
        g2_11 = g11*g11 + g12*g21 + g13*g31
        g2_12 = g11*g12 + g12*g22 + g13*g32
        g2_13 = g11*g13 + g12*g23 + g13*g33

        g2_21 = g21*g11 + g22*g21 + g23*g31
        g2_22 = g21*g12 + g22*g22 + g23*g32
        g2_23 = g21*g13 + g22*g23 + g23*g33

        g2_31 = g31*g11 + g32*g21 + g33*g31
        g2_32 = g31*g12 + g32*g22 + g33*g32
        g2_33 = g31*g13 + g32*g23 + g33*g33

        # Traceless symmetric tensor S_ij^d = 0.5 * (g2_ij + g2_ji) - (1/3) tr(g2) delta_ij
        tr_g2 = g2_11 + g2_22 + g2_33
        sd_11 = g2_11 - (1.0 / 3.0) * tr_g2
        sd_22 = g2_22 - (1.0 / 3.0) * tr_g2
        sd_33 = g2_33 - (1.0 / 3.0) * tr_g2

        sd_12 = 0.5 * (g2_12 + g2_21)
        sd_13 = 0.5 * (g2_13 + g2_31)
        sd_23 = 0.5 * (g2_23 + g2_32)

        # Contraction S_ij^d S_ij^d
        S_sd = (
            sd_11**2 + sd_22**2 + sd_33**2
            + 2.0 * (sd_12**2 + sd_13**2 + sd_23**2)
        )

        # Strain tensor S_ij = 0.5 * (g_ij + g_ji)
        S_11 = g11
        S_22 = g22
        S_33 = g33
        S_12 = 0.5 * (g12 + g21)
        S_13 = 0.5 * (g13 + g31)
        S_23 = 0.5 * (g23 + g32)

        # Contraction S_ij S_ij
        S_sq = (
            S_11**2 + S_22**2 + S_33**2
            + 2.0 * (S_12**2 + S_13**2 + S_23**2)
        )

        delta = self.filter_width(mesh)
        c_wale_sq = (self.cw * delta) ** 2

        num = S_sd ** 1.5
        den = (S_sq ** 2.5) + (S_sd ** 1.25) + self.eps

        nu_t_val = c_wale_sq * (num / den)
        nu_t_val = np.maximum(0.0, nu_t_val)

        out = ScalarField.zeros(mesh)
        out.interior[:] = nu_t_val
        return out


class VremanModel(LESModel):
    """Vreman SGS eddy-viscosity closure (Vreman 2004).

    Computes eddy viscosity nu_t = C_v * sqrt(B_beta / (alpha_ij alpha_ij + eps)).
    Automatically yields nu_t = 0 for laminar shear flows and at solid walls.

    Parameters
    ----------
    cv : float, default=0.07
        Vreman model constant C_v >= 0 (C_v ≈ 2.5 * C_s^2).
    eps : float, default=1e-12
        Regularization parameter to prevent division by zero.
    """

    def __init__(self, cv: float = 0.07, eps: float = 1e-12) -> None:
        if cv < 0.0:
            raise ValueError(f"Vreman model coefficient cv must be non-negative, got {cv}")
        self.cv = float(cv)
        self.eps = float(eps)

    def filter_width(self, mesh: StructuredMesh3D) -> float:
        """Geometric-mean filter width Delta = (dx * dy * dz)^(1/3)."""
        return float((mesh.dx * mesh.dy * mesh.dz) ** (1.0 / 3.0))

    def eddy_viscosity(
        self,
        velocity: VelocityField,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet | None = None,
        nu: float = 1e-3,
        rho: float = 1.0,
    ) -> ScalarField:
        """Compute Vreman eddy viscosity nu_t at cell centers."""
        if self.cv == 0.0:
            return ScalarField.zeros(mesh)

        g = _compute_cell_velocity_gradients(velocity, mesh)

        # Alpha tensor alpha_ij = du_j / dx_i (note transpose of g_ij)
        a11, a12, a13 = g["du_dx"], g["dv_dx"], g["dw_dx"]
        a21, a22, a23 = g["du_dy"], g["dv_dy"], g["dw_dy"]
        a31, a32, a33 = g["du_dz"], g["dv_dz"], g["dw_dz"]

        dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

        # beta_ij = sum_m Delta_m^2 alpha_mi alpha_mj
        b11 = (dx**2) * a11*a11 + (dy**2) * a21*a21 + (dz**2) * a31*a31
        b22 = (dx**2) * a12*a12 + (dy**2) * a22*a22 + (dz**2) * a32*a32
        b33 = (dx**2) * a13*a13 + (dy**2) * a23*a23 + (dz**2) * a33*a33

        b12 = (dx**2) * a11*a12 + (dy**2) * a21*a22 + (dz**2) * a31*a32
        b13 = (dx**2) * a11*a13 + (dy**2) * a21*a23 + (dz**2) * a31*a33
        b23 = (dx**2) * a12*a13 + (dy**2) * a22*a23 + (dz**2) * a32*a33

        # Invariant B_beta = b11*b22 - b12^2 + b11*b33 - b13^2 + b22*b33 - b23^2
        B_beta = (
            (b11 * b22 - b12**2)
            + (b11 * b33 - b13**2)
            + (b22 * b33 - b23**2)
        )
        B_beta = np.maximum(0.0, B_beta)

        # Contraction a_ij a_ij
        a_sq = (
            a11**2 + a12**2 + a13**2
            + a21**2 + a22**2 + a23**2
            + a31**2 + a32**2 + a33**2
        )

        nu_t_val = self.cv * np.sqrt(B_beta / (a_sq + self.eps))
        nu_t_val = np.maximum(0.0, nu_t_val)

        out = ScalarField.zeros(mesh)
        out.interior[:] = nu_t_val
        return out


def compute_sgs_mechanical_work(
    velocity: VelocityField,
    nu_t: ScalarField,
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
) -> tuple[float, float, float]:
    """Compute discrete mechanical work of SGS stress W_sgs = <u, div tau_sgs>_MAC
    and independent cell-centered dissipation integral Pi_sgs = int (2 nu_t S_ij S_ij) dV.

    Returns (W_sgs, Pi_sgs, rel_error).
    On periodic domains, discrete energy consistency guarantees W_sgs == -Pi_sgs <= 0.
    """
    from .variable_diffusion import variable_viscosity_stress_divergence

    # 1. Compute SGS stress divergence div(2 nu_t S_ij)
    div_tau_sgs = variable_viscosity_stress_divergence(velocity, nu_t, mesh, bcs)

    # 2. Compute mechanical work W_sgs using MAC dual control volume weighting
    dV = mesh.cell_volume
    w_u = np.sum(velocity.u.interior[:-1, :, :] * div_tau_sgs.u.interior[:-1, :, :]) * dV if bcs.is_periodic_axis(0) else np.sum(velocity.u.interior * div_tau_sgs.u.interior) * dV
    w_v = np.sum(velocity.v.interior[:, :-1, :] * div_tau_sgs.v.interior[:, :-1, :]) * dV if bcs.is_periodic_axis(1) else np.sum(velocity.v.interior * div_tau_sgs.v.interior) * dV
    w_w = np.sum(velocity.w.interior[:, :, :-1] * div_tau_sgs.w.interior[:, :, :-1]) * dV if bcs.is_periodic_axis(2) else np.sum(velocity.w.interior * div_tau_sgs.w.interior) * dV

    W_sgs = float(w_u + w_v + w_w)

    # 3. Compute native MAC discrete dissipation integral Pi_sgs
    s_comp = compute_strain_components(velocity, mesh, bcs)
    s_xx = s_comp["s_xx"]
    s_yy = s_comp["s_yy"]
    s_zz = s_comp["s_zz"]
    s_xy = s_comp["s_xy"]
    s_xz = s_comp["s_xz"]
    s_yz = s_comp["s_yz"]

    nu_cc = nu_t.interior
    mode_x = "wrap" if bcs.is_periodic_axis(0) else "edge"
    mode_y = "wrap" if bcs.is_periodic_axis(1) else "edge"
    mode_z = "wrap" if bcs.is_periodic_axis(2) else "edge"

    nu_pad_z = np.pad(nu_cc, ((1, 1), (0, 0), (0, 0)), mode=mode_x)
    nu_pad_z = np.pad(nu_pad_z, ((0, 0), (1, 1), (0, 0)), mode=mode_y)
    nu_z_edge = 0.25 * (
        nu_pad_z[:-1, :-1, :] + nu_pad_z[1:, :-1, :] + nu_pad_z[:-1, 1:, :] + nu_pad_z[1:, 1:, :]
    )

    nu_pad_y = np.pad(nu_cc, ((1, 1), (0, 0), (0, 0)), mode=mode_x)
    nu_pad_y = np.pad(nu_pad_y, ((0, 0), (0, 0), (1, 1)), mode=mode_z)
    nu_y_edge = 0.25 * (
        nu_pad_y[:-1, :, :-1] + nu_pad_y[1:, :, :-1] + nu_pad_y[:-1, :, 1:] + nu_pad_y[1:, :, 1:]
    )

    nu_pad_x = np.pad(nu_cc, ((0, 0), (1, 1), (0, 0)), mode=mode_y)
    nu_pad_x = np.pad(nu_pad_x, ((0, 0), (0, 0), (1, 1)), mode=mode_z)
    nu_x_edge = 0.25 * (
        nu_pad_x[:, :-1, :-1] + nu_pad_x[:, 1:, :-1] + nu_pad_x[:, :-1, 1:] + nu_pad_x[:, 1:, 1:]
    )

    pi_normal = np.sum(2.0 * nu_cc * (s_xx**2 + s_yy**2 + s_zz**2)) * dV
    pi_xy = np.sum(4.0 * nu_z_edge[:-1, :-1, :] * (s_xy[:-1, :-1, :]**2)) * dV if bcs.is_periodic_axis(0) else np.sum(4.0 * nu_z_edge * (s_xy**2)) * dV
    pi_xz = np.sum(4.0 * nu_y_edge[:-1, :, :-1] * (s_xz[:-1, :, :-1]**2)) * dV if bcs.is_periodic_axis(0) else np.sum(4.0 * nu_y_edge * (s_xz**2)) * dV
    pi_yz = np.sum(4.0 * nu_x_edge[:, :-1, :-1] * (s_yz[:, :-1, :-1]**2)) * dV if bcs.is_periodic_axis(1) else np.sum(4.0 * nu_x_edge * (s_yz**2)) * dV

    Pi_sgs = float(pi_normal + pi_xy + pi_xz + pi_yz)

    # Relation: W_sgs == -Pi_sgs
    rel_err = abs(W_sgs + Pi_sgs) / (abs(Pi_sgs) + 1e-15)
    return W_sgs, Pi_sgs, rel_err
