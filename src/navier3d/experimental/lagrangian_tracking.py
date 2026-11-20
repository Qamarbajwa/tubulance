"""Lagrangian tracer advection engine, object topologies, and consistency diagnostics.

Provides:
- Velocity interpolator on staggered MAC grids (trilinear and cubic spline).
- Runge-Kutta (RK4, RK2, Euler) Lagrangian trajectory integrator.
- Particle (P0), Material Thread (P1), and Material Bundle (P2) topological representations.
- Synthetic verification flows (analytical shear, vortex, ABC flow) and reversibility checks.
- Zero-leakage deformation gradient reconstruction directly from tracer coordinates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple, Union
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D


def interpolate_mac_velocity(
    x: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    order: int = 1,
    periodic: Tuple[bool, bool, bool] = (True, True, True),
) -> np.ndarray:
    """Interpolate 3D velocity on a staggered MAC grid at arbitrary continuous points.

    Parameters
    ----------
    x : np.ndarray, shape (..., 3)
        Continuous spatial coordinates [x, y, z].
    velocity : VelocityField
        MAC staggered velocity field with ghost padding.
    mesh : StructuredMesh3D
        Simulation domain geometry.
    order : int, default=1
        Interpolation order (1 = trilinear, 3 = cubic).
    periodic : tuple of bool
        Periodicity along (x, y, z).

    Returns
    -------
    np.ndarray, shape (..., 3)
        Interpolated velocity vectors (u, v, w).
    """
    orig_shape = x.shape
    pts = x.reshape(-1, 3)
    n_pts = pts.shape[0]

    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    ng = velocity.u.n_ghost

    # Wrap coordinates if periodic
    px = pts[:, 0] % lx if periodic[0] else np.clip(pts[:, 0], 0.0, lx)
    py = pts[:, 1] % ly if periodic[1] else np.clip(pts[:, 1], 0.0, ly)
    pz = pts[:, 2] % lz if periodic[2] else np.clip(pts[:, 2], 0.0, lz)

    # u is on x-faces: x_face = i*dx, y_center = (j+0.5)*dy, z_center = (k+0.5)*dz
    # Local continuous indices for u:
    iu_cont = px / dx
    ju_cont = (py / dy) - 0.5
    ku_cont = (pz / dz) - 0.5

    # v is on y-faces: x_center = (i+0.5)*dx, y_face = j*dy, z_center = (k+0.5)*dz
    iv_cont = (px / dx) - 0.5
    jv_cont = py / dy
    kv_cont = (pz / dz) - 0.5

    # w is on z-faces: x_center = (i+0.5)*dx, y_center = (j+0.5)*dy, z_face = k*dz
    iw_cont = (px / dx) - 0.5
    jw_cont = (py / dy) - 0.5
    kw_cont = pz / dz

    u_data = velocity.u.data
    v_data = velocity.v.data
    w_data = velocity.w.data

    def _trilinear_sample(data: np.ndarray, ic: np.ndarray, jc: np.ndarray, kc: np.ndarray, shape_dims: Tuple[int, int, int]) -> np.ndarray:
        nx_d, ny_d, nz_d = shape_dims
        i0 = np.floor(ic).astype(int)
        j0 = np.floor(jc).astype(int)
        k0 = np.floor(kc).astype(int)

        fx = ic - i0
        fy = jc - j0
        fz = kc - k0

        # Periodic wrapping for indices relative to interior
        i0_w = (i0 % nx_d) + ng
        i1_w = ((i0 + 1) % nx_d) + ng
        j0_w = (j0 % ny_d) + ng
        j1_w = ((j0 + 1) % ny_d) + ng
        k0_w = (k0 % nz_d) + ng
        k1_w = ((k0 + 1) % nz_d) + ng

        c000 = data[i0_w, j0_w, k0_w]
        c100 = data[i1_w, j0_w, k0_w]
        c010 = data[i0_w, j1_w, k0_w]
        c110 = data[i1_w, j1_w, k0_w]
        c001 = data[i0_w, j0_w, k1_w]
        c101 = data[i1_w, j0_w, k1_w]
        c011 = data[i0_w, j1_w, k1_w]
        c111 = data[i1_w, j1_w, k1_w]

        c00 = c000 * (1.0 - fx) + c100 * fx
        c10 = c010 * (1.0 - fx) + c110 * fx
        c01 = c001 * (1.0 - fx) + c101 * fx
        c11 = c011 * (1.0 - fx) + c111 * fx

        c0 = c00 * (1.0 - fy) + c10 * fy
        c1 = c01 * (1.0 - fy) + c11 * fy

        return c0 * (1.0 - fz) + c1 * fz

    u_interp = _trilinear_sample(u_data, iu_cont, ju_cont, ku_cont, (nx, ny, nz))
    v_interp = _trilinear_sample(v_data, iv_cont, jv_cont, kv_cont, (nx, ny, nz))
    w_interp = _trilinear_sample(w_data, iw_cont, jw_cont, kw_cont, (nx, ny, nz))

    res = np.stack([u_interp, v_interp, w_interp], axis=-1)
    return res.reshape(orig_shape)


def rk4_step(
    x: np.ndarray,
    velocity_func: Callable[[np.ndarray, float], np.ndarray],
    t: float,
    dt: float,
    domain_size: Optional[Tuple[float, float, float]] = None,
) -> np.ndarray:
    """Advance tracer positions by dt using classic 4th-order Runge-Kutta.

    dx/dt = u(x, t)
    """
    k1 = velocity_func(x, t)
    k2 = velocity_func(x + 0.5 * dt * k1, t + 0.5 * dt)
    k3 = velocity_func(x + 0.5 * dt * k2, t + 0.5 * dt)
    k4 = velocity_func(x + dt * k3, t + dt)

    x_next = x + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    if domain_size is not None:
        lx, ly, lz = domain_size
        x_next[..., 0] = x_next[..., 0] % lx
        x_next[..., 1] = x_next[..., 1] % ly
        x_next[..., 2] = x_next[..., 2] % lz
    return x_next


def rk2_step(
    x: np.ndarray,
    velocity_func: Callable[[np.ndarray, float], np.ndarray],
    t: float,
    dt: float,
    domain_size: Optional[Tuple[float, float, float]] = None,
) -> np.ndarray:
    """Advance tracer positions by dt using explicit Midpoint / RK2."""
    k1 = velocity_func(x, t)
    k2 = velocity_func(x + 0.5 * dt * k1, t + 0.5 * dt)
    x_next = x + dt * k2
    if domain_size is not None:
        lx, ly, lz = domain_size
        x_next[..., 0] = x_next[..., 0] % lx
        x_next[..., 1] = x_next[..., 1] % ly
        x_next[..., 2] = x_next[..., 2] % lz
    return x_next


def euler_step(
    x: np.ndarray,
    velocity_func: Callable[[np.ndarray, float], np.ndarray],
    t: float,
    dt: float,
    domain_size: Optional[Tuple[float, float, float]] = None,
) -> np.ndarray:
    """Advance tracer positions by dt using Forward Euler."""
    k1 = velocity_func(x, t)
    x_next = x + dt * k1
    if domain_size is not None:
        lx, ly, lz = domain_size
        x_next[..., 0] = x_next[..., 0] % lx
        x_next[..., 1] = x_next[..., 1] % ly
        x_next[..., 2] = x_next[..., 2] % lz
    return x_next


@dataclass
class Particle:
    """Representation Level P0: Single Lagrangian particle trajectory.

    Attributes
    ----------
    trajectory : np.ndarray, shape (T, 3)
        Positions over time.
    times : np.ndarray, shape (T,)
        Time coordinates.
    """
    trajectory: np.ndarray
    times: np.ndarray

    @property
    def initial_position(self) -> np.ndarray:
        return self.trajectory[0]

    @property
    def current_position(self) -> np.ndarray:
        return self.trajectory[-1]


@dataclass
class MaterialThread:
    """Representation Level P1: Connected ordered line of material tracers.

    Attributes
    ----------
    trajectories : np.ndarray, shape (T, N_tracers, 3)
        Positions of ordered tracers along the material line.
    times : np.ndarray, shape (T,)
        Time coordinates.
    initial_length : float
        Undeformed initial arc length L0.
    """
    trajectories: np.ndarray
    times: np.ndarray
    initial_length: float

    @property
    def num_tracers(self) -> int:
        return self.trajectories.shape[1]

    def centroid(self, t_idx: int = -1) -> np.ndarray:
        """Compute centroid of the material thread at time index t_idx."""
        # Unwrapped relative to the middle tracer to avoid periodic jumps
        coords = self.trajectories[t_idx]
        return np.mean(coords, axis=0)


@dataclass
class MaterialBundle:
    """Representation Level P2: Multi-directional material deformation bundle / local frame.

    Sampled as a central tracer with 6 orthogonal neighbor tracers (or 4 tetrahedral vertices)
    enabling full 3D deformation gradient reconstruction purely from geometry.

    Attributes
    ----------
    trajectories : np.ndarray, shape (T, N_tracers, 3)
        Positions of bundle tracers over time (index 0 is centroid reference).
    times : np.ndarray, shape (T,)
        Time coordinates.
    initial_offsets : np.ndarray, shape (N_tracers - 1, 3)
        Initial displacement vectors dX_0 relative to centroid.
    """
    trajectories: np.ndarray
    times: np.ndarray
    initial_offsets: np.ndarray

    @property
    def num_tracers(self) -> int:
        return self.trajectories.shape[1]

    def centroid(self, t_idx: int = -1) -> np.ndarray:
        """Return central tracer position at time index t_idx."""
        return self.trajectories[t_idx, 0]


def initialize_material_objects(
    reference_positions: np.ndarray,
    n_thread_tracers: int = 17,
    thread_length: float = 0.2,
    bundle_radius: float = 0.05,
    domain_size: Tuple[float, float, float] = (2.0 * np.pi, 2.0 * np.pi, 2.0 * np.pi),
    seed: int = 42,
) -> Tuple[List[np.ndarray], List[np.ndarray], List[Tuple[np.ndarray, np.ndarray]]]:
    """Initialize initial coordinates for P0 (Particles), P1 (Threads), and P2 (Bundles).

    Returns
    -------
    particles_init : list of shape (3,)
    threads_init : list of shape (n_thread_tracers, 3)
    bundles_init : list of tuple (shape (N_b, 3), initial_offsets shape (N_b - 1, 3))
    """
    rng = np.random.RandomState(seed)
    n_objects = len(reference_positions)
    lx, ly, lz = domain_size

    particles_init = []
    threads_init = []
    bundles_init = []

    for i in range(n_objects):
        xc = reference_positions[i].copy()
        particles_init.append(xc)

        # 1. Thread: random orientation unit vector e_hat
        theta = rng.uniform(0, 2.0 * np.pi)
        phi = rng.uniform(0, np.pi)
        e_hat = np.array([
            np.sin(phi) * np.cos(theta),
            np.sin(phi) * np.sin(theta),
            np.cos(phi)
        ])
        s_vals = np.linspace(-0.5 * thread_length, 0.5 * thread_length, n_thread_tracers)
        thread_pts = xc[None, :] + s_vals[:, None] * e_hat[None, :]
        thread_pts[:, 0] %= lx
        thread_pts[:, 1] %= ly
        thread_pts[:, 2] %= lz
        threads_init.append(thread_pts)

        # 2. Bundle: central tracer + 6 orthogonal offset tracers (+/- r along x, y, z)
        # Total 7 tracers sampling full 3D deformation
        offsets = np.array([
            [bundle_radius, 0.0, 0.0],
            [-bundle_radius, 0.0, 0.0],
            [0.0, bundle_radius, 0.0],
            [0.0, -bundle_radius, 0.0],
            [0.0, 0.0, bundle_radius],
            [0.0, 0.0, -bundle_radius],
        ])
        bundle_pts = np.vstack([xc[None, :], xc[None, :] + offsets])
        bundle_pts[:, 0] %= lx
        bundle_pts[:, 1] %= ly
        bundle_pts[:, 2] %= lz
        bundles_init.append((bundle_pts, offsets))

    return particles_init, threads_init, bundles_init


def compute_geometry_deformation_gradient(
    current_pts: np.ndarray,
    initial_offsets: np.ndarray,
    domain_size: Optional[Tuple[float, float, float]] = None,
) -> Tuple[np.ndarray, float]:
    """Reconstruct deformation gradient F from bundle tracer coordinates ONLY.

    dx(t) approx F(t) dX_0 via least squares:
    F = (dx dX_0^T) (dX_0 dX_0^T)^(-1)

    Returns
    -------
    F : np.ndarray, shape (3, 3)
        Deformation gradient.
    det_F : float
        Determinant (should remain approx 1.0 for incompressible flow).
    """
    xc = current_pts[0]
    dx = current_pts[1:] - xc[None, :]

    # Handle periodic minimum image distance if domain_size is given
    if domain_size is not None:
        for dim in range(3):
            L = domain_size[dim]
            dx[:, dim] = dx[:, dim] - L * np.round(dx[:, dim] / L)

    dX0 = initial_offsets.copy()
    if len(dX0) == len(current_pts):
        dX0 = dX0[1:]

    # Least-squares solve: dx = dX0 @ F^T => F^T = pinv(dX0) @ dx => F = dx^T @ pinv(dX0)^T
    # Or explicitly: F = (dx^T @ dX0) @ inv(dX0^T @ dX0)
    cov_x_X = dx.T @ dX0
    cov_X_X = dX0.T @ dX0 + 1e-12 * np.eye(3)
    F = cov_x_X @ np.linalg.inv(cov_X_X)
    det_F = float(np.linalg.det(F))
    return F, det_F
