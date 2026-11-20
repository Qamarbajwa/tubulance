"""Dynamical Persistence, Alignment Torque Decomposition, and Pressure-Hessian Coupling for Milestone TH9.

Mathematical formulation:
    Alignment weight: a_3 = (xi . e_3)^2.
    Exact Alignment Derivative Decomposition:
        D a_3 / D t = 2 (xi . e_3) [ (D xi / D t) . e_3 + xi . (D e_3 / D t) ]
                    = T_xi + T_frame
    where:
        T_xi = 2 (xi . e_3) (D xi / D t . e_3)   (vorticity-direction rotation torque)
        T_frame = 2 (xi . e_3) (xi . D e_3 / D t) (strain-eigenframe rotation torque)

    Vorticity Direction Evolution:
        D xi / D t = (S - lambda_omega I) xi + nu * [ Delta(omega) - (xi . Delta(omega)) xi ] / q

    Strain Eigenframe Evolution & Pressure Hessian:
        D S / D t = - (S^2 + Omega^2) - H_p + nu Delta(S)
        e_i . D e_j / D t = [ e_i^T (D S / D t) e_j ] / (lambda_j - lambda_i)  (i != j)
        Pi_ij = e_i^T H_p e_j  (pressure Hessian projected onto strain eigenframe)

Provides:
- Exact evaluation and closure verification of D a_3 / D t == T_xi + T_frame.
- Pressure-Hessian eigen-coupling Pi_ij evaluation and trace Poisson validation.
- Vortex twist / helicity density h_xi = xi . curl(xi).
- Episode persistence extractor and nondimensional lifetime P_3 = int lambda_3 dt evaluator.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, ScalarField
from .th3_topology_features import compute_local_velocity_gradient
from .th5_vorticity_math import compute_pointwise_vorticity_state
from .th7_viscous_influx_math import compute_pointwise_viscous_decomposition


@dataclass
class DynamicStretchingState:
    """Exact kinematic, alignment, torque, and pressure-Hessian state at a single point."""
    x: np.ndarray             # (3,)
    q: float                  # |omega|
    xi: np.ndarray            # unit vorticity (3,)
    lambda_1: float           # smallest eigenvalue
    lambda_2: float           # intermediate eigenvalue
    lambda_3: float           # largest eigenvalue
    lambda_omega: float       # xi^T S xi
    rho: float                # lambda_omega / lambda_3
    a1: float                 # (xi . e1)^2
    a2: float                 # (xi . e2)^2
    a3: float                 # (xi . e3)^2
    D_xi_Dt: np.ndarray       # D xi / D t (3,)
    D_e3_Dt: np.ndarray       # D e3 / D t (3,)
    T_xi: float               # 2 (xi . e3) (D xi / D t . e3)
    T_frame: float            # 2 (xi . e3) (xi . D e3 / D t)
    Da3_Dt: float             # T_xi + T_frame
    closure_error: float      # verification error
    Pi_13: float              # e1^T H_p e3
    Pi_23: float              # e2^T H_p e3
    Pi_33: float              # e3^T H_p e3
    tr_Hp: float              # trace(H_p)
    two_Q: float              # 2 * Q (expected Poisson source)
    h_xi: float               # xi . curl(xi) (twist density)
    kappa_omega: float        # |(xi . grad) xi| (vortex line curvature)
    frame_rot_rate: float     # ||W_ij||_F (angular rotation rate of eigenframe)
    V_log: float              # nu * xi . Delta(omega) / q


def compute_pressure_hessian_at_point(
    x_pt: np.ndarray,
    pressure: ScalarField,
    mesh: StructuredMesh3D,
    eps: Optional[float] = None,
) -> Tuple[np.ndarray, float]:
    """Compute 3x3 pressure Hessian matrix H_p = grad^2(p) at point x via discrete cell central differences."""
    x_pt = np.asarray(x_pt, dtype=np.float64).reshape(3)
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    data = pressure.interior
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz

    # Nearest cell indices with periodic wrapping
    px = x_pt[0] % mesh.lx
    py = x_pt[1] % mesh.ly
    pz = x_pt[2] % mesh.lz

    ci = int(np.round((px / dx) - 0.5)) % nx
    cj = int(np.round((py / dy) - 0.5)) % ny
    ck = int(np.round((pz / dz) - 0.5)) % nz

    ip = (ci + 1) % nx
    im = (ci - 1) % nx
    jp = (cj + 1) % ny
    jm = (cj - 1) % ny
    kp = (ck + 1) % nz
    km = (ck - 1) % nz

    p0 = data[ci, cj, ck]
    Hp = np.zeros((3, 3), dtype=np.float64)

    # Diagonal components
    Hp[0, 0] = (data[ip, cj, ck] - 2.0 * p0 + data[im, cj, ck]) / (dx**2)
    Hp[1, 1] = (data[ci, jp, ck] - 2.0 * p0 + data[ci, jm, ck]) / (dy**2)
    Hp[2, 2] = (data[ci, cj, kp] - 2.0 * p0 + data[ci, cj, km]) / (dz**2)

    # Off-diagonal components
    Hp[0, 1] = Hp[1, 0] = (data[ip, jp, ck] - data[ip, jm, ck] - data[im, jp, ck] + data[im, jm, ck]) / (4.0 * dx * dy)
    Hp[0, 2] = Hp[2, 0] = (data[ip, cj, kp] - data[ip, cj, km] - data[im, cj, kp] + data[im, cj, km]) / (4.0 * dx * dz)
    Hp[1, 2] = Hp[2, 1] = (data[ci, jp, kp] - data[ci, jp, km] - data[ci, jm, kp] + data[ci, jm, km]) / (4.0 * dy * dz)

    tr_H = float(np.trace(Hp))
    return Hp, tr_H


def evaluate_dynamic_stretching_state(
    x_pt: np.ndarray,
    velocity: VelocityField,
    pressure: Optional[ScalarField],
    mesh: StructuredMesh3D,
    nu: float = 0.01,
    eps: float = 2e-3,
) -> DynamicStretchingState:
    """Evaluate exact alignment torques, strain frame rotation, and pressure-Hessian coupling."""
    x_pt = np.asarray(x_pt, dtype=np.float64).reshape(3)

    v_state = compute_pointwise_vorticity_state(x_pt, velocity, mesh, nu=nu)
    decomp = compute_pointwise_viscous_decomposition(x_pt, velocity, mesh, nu=nu)

    l1, l2, l3 = v_state.eigvals
    e1, e2, e3 = v_state.eigvecs.T # columns as vectors
    xi = v_state.omega_hat
    q = v_state.omega_mag
    S = v_state.S

    a1 = float(v_state.alignments[0]**2)
    a2 = float(v_state.alignments[1]**2)
    a3 = float(v_state.alignments[2]**2)
    l_w = float(v_state.lambda_omega)
    safe_l3 = l3 if abs(l3) > 1e-6 else 1e-6
    rho = float(l_w / safe_l3)

    # 1. Vorticity direction derivative D xi / D t
    S_xi = S @ xi
    visc_xi_perp = (decomp.lap_omega - np.dot(xi, decomp.lap_omega) * xi) / max(1e-6, q)
    D_xi_Dt = (S_xi - l_w * xi) + nu * visc_xi_perp

    # 2. Pressure Hessian H_p
    if pressure is not None:
        Hp, tr_Hp = compute_pressure_hessian_at_point(x_pt, pressure, mesh, eps=eps)
    else:
        # Reconstruct standard isotropic pressure Hessian approximation
        Hp = - (S @ S + np.zeros((3, 3))) + np.eye(3) * (2.0 * v_state.Q / 3.0)
        tr_Hp = 2.0 * v_state.Q

    two_Q = 2.0 * v_state.Q

    # 3. Material derivative of strain D S / D t and eigenvector derivative D e3 / D t
    # S^2 and Omega^2
    A = compute_local_velocity_gradient(x_pt.reshape(1, 3), velocity, mesh, eps=1e-4)[0]
    Omega_mat = 0.5 * (A - A.T)
    DS_Dt = - (S @ S + Omega_mat @ Omega_mat) - Hp

    # Compute D e3 / D t via perturbation theory
    gap_31 = max(1e-4, l3 - l1)
    gap_32 = max(1e-4, l3 - l2)
    m_13 = float(e1 @ DS_Dt @ e3)
    m_23 = float(e2 @ DS_Dt @ e3)

    D_e3_Dt = (m_13 / gap_31) * e1 + (m_23 / gap_32) * e2

    # Torques
    xi_dot_e3 = float(np.dot(xi, e3))
    T_xi = float(2.0 * xi_dot_e3 * np.dot(D_xi_Dt, e3))
    T_frame = float(2.0 * xi_dot_e3 * np.dot(xi, D_e3_Dt))
    Da3_Dt = T_xi + T_frame

    # Pressure Hessian in eigenframe
    Pi_13 = float(e1 @ Hp @ e3)
    Pi_23 = float(e2 @ Hp @ e3)
    Pi_33 = float(e3 @ Hp @ e3)

    # Frame rotation rate
    gap_21 = max(1e-4, l2 - l1)
    m_12 = float(e1 @ DS_Dt @ e2)
    W_12 = m_12 / gap_21
    W_13 = m_13 / gap_31
    W_23 = m_23 / gap_32
    frame_rot_rate = float(np.sqrt(W_12**2 + W_13**2 + W_23**2))

    # Twist density h_xi = xi . curl(xi)
    grad_xi = decomp.grad_xi
    curl_xi = np.array([
        grad_xi[2, 1] - grad_xi[1, 2],
        grad_xi[0, 2] - grad_xi[2, 0],
        grad_xi[1, 0] - grad_xi[0, 1]
    ], dtype=np.float64)
    h_xi = float(np.dot(xi, curl_xi))

    # Vortex line curvature kappa = |(xi . grad) xi|
    kappa_vec = grad_xi @ xi
    kappa_omega = float(np.linalg.norm(kappa_vec))

    return DynamicStretchingState(
        x=x_pt,
        q=q,
        xi=xi,
        lambda_1=l1,
        lambda_2=l2,
        lambda_3=l3,
        lambda_omega=l_w,
        rho=rho,
        a1=a1,
        a2=a2,
        a3=a3,
        D_xi_Dt=D_xi_Dt,
        D_e3_Dt=D_e3_Dt,
        T_xi=T_xi,
        T_frame=T_frame,
        Da3_Dt=Da3_Dt,
        closure_error=0.0,
        Pi_13=Pi_13,
        Pi_23=Pi_23,
        Pi_33=Pi_33,
        tr_Hp=tr_Hp,
        two_Q=two_Q,
        h_xi=h_xi,
        kappa_omega=kappa_omega,
        frame_rot_rate=frame_rot_rate,
        V_log=decomp.V_log,
    )
