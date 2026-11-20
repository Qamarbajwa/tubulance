"""Maximum-Vorticity Stretching Depletion and Strain Eigenstructure Mathematics for Milestone TH8.

Mathematical formulation:
    q = |omega|, xi = omega / q, ||xi|| = 1.
    Strain eigensystem: S e_i = lambda_i e_i with lambda_1 <= lambda_2 <= lambda_3.
    Direction weights: a_i = (xi . e_i)^2 with a1 + a2 + a3 = 1.
    Realized stretching: lambda_omega = xi^T S xi = lambda_1 a1 + lambda_2 a2 + lambda_3 a3.
    
    Exact Depletion Decomposition:
        D_abs = lambda_3 - lambda_omega = (lambda_3 - lambda_1) a1 + (lambda_3 - lambda_2) a2 >= 0.
        
    Depletion Ratio:
        D_ratio = lambda_omega / lambda_3 (for lambda_3 > 0).

Provides:
- Extraction of spatial maximizers x*(t) and near-maximum sets M_alpha(t).
- Exact decomposition into e1 misalignment contribution and e2 misalignment contribution.
- Peak viscous non-amplification verification (V_log <= 0 at spatial maxima).
- Falsification evaluation of universal delta-depletion hypothesis lambda_omega <= (1 - delta) lambda_3.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField
from .th3_topology_features import compute_local_velocity_gradient
from .th5_vorticity_math import compute_pointwise_vorticity_state
from .th7_viscous_influx_math import compute_pointwise_viscous_decomposition


@dataclass
class PeakDepletionRecord:
    """Exact stretching depletion record at a maximum or near-maximum space-time point."""
    x: np.ndarray             # (3,)
    q: float                  # |omega|
    q_max: float              # global maximum |omega| at this time step
    alpha: float              # q / q_max
    lambda_1: float           # smallest strain eigenvalue
    lambda_2: float           # intermediate strain eigenvalue
    lambda_3: float           # largest strain eigenvalue
    lambda_omega: float       # xi^T S xi
    a1: float                 # (xi . e1)^2
    a2: float                 # (xi . e2)^2
    a3: float                 # (xi . e3)^2
    D_abs: float              # lambda_3 - lambda_omega
    D_ratio: float            # lambda_omega / lambda_3
    depletion_fraction: float # 1 - D_ratio
    e1_contrib: float         # (lambda_3 - lambda_1) * a1
    e2_contrib: float         # (lambda_3 - lambda_2) * a2
    closure_error: float      # |D_abs - (e1_contrib + e2_contrib)|
    V_log: float              # nu * xi . Delta(omega) / q
    V_log_plus: float         # max(0, V_log)
    lap_q: float              # Delta(|omega|)
    Q: float                  # second velocity gradient invariant
    R: float                  # third velocity gradient invariant
    is_exact_max: bool        # True if alpha == 1.0


def extract_field_vorticity_grid(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute cell-centered 3D vorticity magnitude grid and coordinate grids."""
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    # Velocity components on faces
    u = velocity.u.interior
    v = velocity.v.interior
    w = velocity.w.interior

    # Cell-centered velocity gradients via central differences
    # u is on x-faces (nx+1, ny, nz), v on y-faces (nx, ny+1, nz), w on z-faces (nx, ny, nz+1)
    # Cell-center averages:
    # dw/dy - dv/dz
    dw_dy = (w[:, 1:, :] - w[:, :-1, :]) / dy if w.shape[1] > 1 else np.zeros((nx, ny, nz))
    # Pad to (nx, ny, nz)
    # Use standard pointwise sampling grid for robustness
    xs = (np.arange(nx) + 0.5) * dx
    ys = (np.arange(ny) + 0.5) * dy
    zs = (np.arange(nz) + 0.5) * dz
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")

    # Sample vorticity magnitude across grid
    q_grid = np.zeros((nx, ny, nz), dtype=np.float64)
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                pt = np.array([xs[i], ys[j], zs[k]])
                A = compute_local_velocity_gradient(pt.reshape(1, 3), velocity, mesh, eps=1e-4)[0]
                wv = np.array([A[2, 1] - A[1, 2], A[0, 2] - A[2, 0], A[1, 0] - A[0, 1]])
                q_grid[i, j, k] = np.linalg.norm(wv)

    return q_grid, X, Y, Z


def evaluate_pointwise_depletion(
    x_pt: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    q_max: float,
    nu: float = 0.01,
) -> PeakDepletionRecord:
    """Evaluate exact stretching depletion and eigenstructure decomposition at point x."""
    x_pt = np.asarray(x_pt, dtype=np.float64).reshape(3)

    # Vorticity state and eigensystem
    v_state = compute_pointwise_vorticity_state(x_pt, velocity, mesh, nu=nu)
    decomp = compute_pointwise_viscous_decomposition(x_pt, velocity, mesh, nu=nu)

    l1, l2, l3 = v_state.eigvals
    a1 = float(v_state.alignments[0]**2)
    a2 = float(v_state.alignments[1]**2)
    a3 = float(v_state.alignments[2]**2)

    l_w = float(v_state.lambda_omega)
    D_abs = float(l3 - l_w)

    e1_c = float((l3 - l1) * a1)
    e2_c = float((l3 - l2) * a2)
    closure = abs(D_abs - (e1_c + e2_c))

    safe_l3 = l3 if abs(l3) > 1e-6 else 1e-6
    D_ratio = float(l_w / safe_l3)
    dep_frac = float(1.0 - D_ratio)

    q = float(v_state.omega_mag)
    alpha = float(q / q_max) if q_max > 1e-6 else 1.0
    is_exact = bool(np.isclose(alpha, 1.0, atol=1e-4))

    return PeakDepletionRecord(
        x=x_pt,
        q=q,
        q_max=q_max,
        alpha=alpha,
        lambda_1=l1,
        lambda_2=l2,
        lambda_3=l3,
        lambda_omega=l_w,
        a1=a1,
        a2=a2,
        a3=a3,
        D_abs=D_abs,
        D_ratio=D_ratio,
        depletion_fraction=dep_frac,
        e1_contrib=e1_c,
        e2_contrib=e2_c,
        closure_error=closure,
        V_log=decomp.V_log,
        V_log_plus=decomp.V_log_plus,
        lap_q=decomp.lap_q,
        Q=v_state.Q,
        R=v_state.R,
        is_exact_max=is_exact,
    )
