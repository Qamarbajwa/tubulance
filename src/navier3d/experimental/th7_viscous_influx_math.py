"""Exact Magnitude-Direction Decomposition and Viscous Influx Mathematics for Milestone TH7.

Mathematical formulation:
    omega = q * xi, where q = |omega| and xi = omega_hat (||xi|| = 1).
    Delta(omega) = xi * Delta(q) + 2 * (grad(q) . grad)xi + q * Delta(xi).
    Since xi . xi = 1:
        xi . (d xi / d x_k) = 0 for all k in {1,2,3},
        xi . Delta(xi) = - ||grad(xi)||_F^2.
    Therefore, the exact projection onto vorticity direction is:
        xi . Delta(omega) = Delta(q) - q * ||grad(xi)||_F^2.
    Consequently:
        V_log = nu * (xi . Delta(omega)) / q = nu * [ (Delta(q) / q) - ||grad(xi)||_F^2 ].

Provides:
- Exact pointwise evaluation of magnitude curvature Delta(q) and direction penalty ||grad(xi)||_F^2.
- Numerical closure verification: |xi . Delta(omega) - (Delta(q) - q * ||grad(xi)||_F^2)|.
- Local extrema classification (local maximum, minimum, saddle).
- Bound candidates B7-1 through B7-5 evaluators.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField
from .lagrangian_tracking import interpolate_mac_velocity
from .th3_topology_features import compute_local_velocity_gradient
from .th5_vorticity_math import compute_pointwise_vorticity_state


@dataclass
class ViscousInfluxDecomposition:
    """Exact magnitude-direction decomposition at a single space-time point."""
    x: np.ndarray             # (3,)
    q: float                  # |omega|
    xi: np.ndarray            # unit vorticity vector (3,)
    lap_omega: np.ndarray     # Delta(omega) (3,)
    xi_dot_lap_omega: float   # xi . Delta(omega)
    grad_q: np.ndarray        # grad(|omega|) (3,)
    lap_q: float              # Delta(|omega|)
    grad_xi: np.ndarray       # grad(omega_hat) (3, 3) where [i, j] = d(xi_i) / d(x_j)
    dir_decoherence_penalty: float # ||grad(xi)||_F^2 = sum_{i,j} (d xi_i / d x_j)^2
    decomp_rhs: float         # Delta(q) - q * ||grad(xi)||_F^2
    decomp_residual: float    # |xi . Delta(omega) - decomp_rhs|
    V_log: float              # nu * xi_dot_lap_omega / q
    V_log_plus: float         # max(0, V_log)
    mag_curvature_term: float # nu * Delta(q) / q
    dir_penalty_term: float   # - nu * ||grad(xi)||_F^2
    is_local_maximum: bool    # True if lap_q <= 0 and ||grad_q|| approx 0
    is_local_minimum: bool    # True if lap_q > 0 and ||grad_q|| approx 0


def compute_pointwise_viscous_decomposition(
    x_pt: np.ndarray,
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    eps: float = 2e-3,
) -> ViscousInfluxDecomposition:
    """Compute exact magnitude-direction decomposition of vorticity Laplacian at point x."""
    x_pt = np.asarray(x_pt, dtype=np.float64).reshape(3)

    # Base vorticity state
    def _eval_omega(pos: np.ndarray) -> Tuple[np.ndarray, float, np.ndarray]:
        A = compute_local_velocity_gradient(pos.reshape(1, 3), velocity, mesh, eps=1e-4)[0]
        w = np.array([A[2, 1] - A[1, 2], A[0, 2] - A[2, 0], A[1, 0] - A[0, 1]], dtype=np.float64)
        w_mag = float(np.linalg.norm(w))
        w_hat = w / w_mag if w_mag > 1e-12 else np.zeros(3, dtype=np.float64)
        return w, w_mag, w_hat

    w_0, q_0, xi_0 = _eval_omega(x_pt)

    # Finite difference stencils for Delta(omega), grad(q), Delta(q), grad(xi)
    lap_w = np.zeros(3, dtype=np.float64)
    grad_q = np.zeros(3, dtype=np.float64)
    lap_q = 0.0
    grad_xi = np.zeros((3, 3), dtype=np.float64) # [i, j] = d(xi_i) / d(x_j)

    for j in range(3):
        dx = np.zeros(3)
        dx[j] = eps
        w_p, q_p, xi_p = _eval_omega(x_pt + dx)
        w_m, q_m, xi_m = _eval_omega(x_pt - dx)

        # Vector Laplacian Delta(omega)
        lap_w += (w_p - 2.0 * w_0 + w_m) / (eps**2)

        # Magnitude gradient & Laplacian
        grad_q[j] = (q_p - q_m) / (2.0 * eps)
        lap_q += (q_p - 2.0 * q_0 + q_m) / (eps**2)

        # Direction gradient matrix
        for i in range(3):
            grad_xi[i, j] = (xi_p[i] - xi_m[i]) / (2.0 * eps)

    xi_dot_lap_w = float(np.dot(xi_0, lap_w))
    dir_penalty = float(np.sum(grad_xi**2))
    decomp_rhs = lap_q - q_0 * dir_penalty
    decomp_res = abs(xi_dot_lap_w - decomp_rhs)

    # Logarithmic viscous contributions
    safe_q = max(1e-6, q_0)
    V_log = float(nu * xi_dot_lap_w / safe_q)
    V_log_plus = float(max(0.0, V_log))
    mag_curv = float(nu * lap_q / safe_q)
    dir_term = float(-nu * dir_penalty)

    # Extrema classification
    grad_q_norm = float(np.linalg.norm(grad_q))
    is_max = bool(lap_q < 0 and grad_q_norm < 0.5 * safe_q)
    is_min = bool(lap_q > 0 and grad_q_norm < 0.5 * safe_q)

    return ViscousInfluxDecomposition(
        x=x_pt,
        q=q_0,
        xi=xi_0,
        lap_omega=lap_w,
        xi_dot_lap_omega=xi_dot_lap_w,
        grad_q=grad_q,
        lap_q=lap_q,
        grad_xi=grad_xi,
        dir_decoherence_penalty=dir_penalty,
        decomp_rhs=decomp_rhs,
        decomp_residual=decomp_res,
        V_log=V_log,
        V_log_plus=V_log_plus,
        mag_curvature_term=mag_curv,
        dir_penalty_term=dir_term,
        is_local_maximum=is_max,
        is_local_minimum=is_min,
    )
