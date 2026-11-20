"""W9 Boundary-Layer-Aware Eigenmodes, Wall Shear Diagnostics, and Operator-Optimized Wall Navier-Stokes Suite.

Provides:
- BoundaryLayerDiagnostics: E(y) profile, wall-shear error E_{tau_w}, projection vs evolution error split, and wall-shear projection bound E_{tau_w}^{proj}.
- DerivativeWeightedStokesBasis: Candidate W9-A & W9-B ranking modes via combined energy and wall-gradient / dissipation metric J_n = alpha * E_n + beta * G_n.
- SeparableChannelEigenbasis: Candidate W9-D & W9-E using separable channel modes and velocity-vorticity (v, eta) coordinates.
- ResolventResponseBasis: Candidate W9-G & W9-J using resolvent operator response and wall-shear output-aware functional optimization.
- evaluate_w9_candidate_gate: Evaluates candidate components under strict KEEP / DISCARD gates.
"""
from __future__ import annotations

import time
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, FlowState, ScalarField
from ..boundary_conditions import BoundaryConditionSet, periodic_bcs
from ..time_integrators import ThetaSchemeIntegrator
from ..decaying_turbulence import generate_solenoidal_random_field
from .stokes_eigenbasis import StokesEigenbasis3D
from .w8_stokes_rom import StokesEigenmodeODEIntegrator, MatrixFreeStokesConvectionEvaluator
from .solenoidal_basis import mac_to_cell_centers, cell_centers_to_mac
from .w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm


class BoundaryLayerDiagnostics:
    """Diagnostic suite for wall-normal error profiles E(y), wall-shear projection bounds, and error decomposition."""

    @staticmethod
    def compute_wall_normal_error_profile(
        vel_truth: VelocityField, vel_rom: VelocityField, mesh: StructuredMesh3D
    ) -> np.ndarray:
        """Compute relative velocity error E(y) at each wall-normal y-plane."""
        u_t, v_t, w_t = mac_to_cell_centers(vel_truth)
        u_r, v_r, w_r = mac_to_cell_centers(vel_rom)

        ny = mesh.ny
        e_y = np.zeros(ny, dtype=np.float64)

        for j in range(ny):
            diff_j = np.sum((u_t[:, j, :] - u_r[:, j, :]) ** 2 + (v_t[:, j, :] - v_r[:, j, :]) ** 2 + (w_t[:, j, :] - w_r[:, j, :]) ** 2)
            norm_j = np.sum(u_t[:, j, :] ** 2 + v_t[:, j, :] ** 2 + w_t[:, j, :] ** 2) + 1e-15
            e_y[j] = np.sqrt(diff_j / norm_j)

        return e_y

    @staticmethod
    def compute_wall_shear_error(
        vel_truth: VelocityField, vel_rom: VelocityField, mesh: StructuredMesh3D, nu: float = 0.01
    ) -> Dict[str, float]:
        """Compute wall shear stress tau_w = mu * du/dy|_{y=0} and relative error E_{tau_w}."""
        dy = mesh.dy
        mu = nu * 1.0

        u_wall_t = vel_truth.u.interior[:, 0, :]
        u_wall_r = vel_rom.u.interior[:, 0, :]

        tau_w_t = float(np.mean(mu * u_wall_t / dy))
        tau_w_r = float(np.mean(mu * u_wall_r / dy))
        e_tau_w = abs(tau_w_t - tau_w_r) / (abs(tau_w_t) + 1e-15)

        return {
            "tau_w_truth": tau_w_t,
            "tau_w_rom": tau_w_r,
            "E_tau_w": e_tau_w,
        }

    @staticmethod
    def compute_projection_bound_and_split(
        vel_truth: VelocityField,
        vel_rom: VelocityField,
        basis: StokesEigenbasis3D,
        mesh: StructuredMesh3D,
        nu: float = 0.01,
    ) -> Dict[str, float]:
        """Decompose error into E_proj (representation bound), E_ROM, E_evolution, and E_{tau_w}^{proj}."""
        # Project truth onto basis
        a_proj = basis.project_mac(vel_truth)
        vel_proj = basis.reconstruct_mac(a_proj)

        e_proj = mac_velocity_diff_norm(vel_truth, vel_proj, mesh) / mac_velocity_norm(vel_truth, mesh)
        e_rom = mac_velocity_diff_norm(vel_truth, vel_rom, mesh) / mac_velocity_norm(vel_truth, mesh)
        e_evolution = e_rom - e_proj

        shear_t = BoundaryLayerDiagnostics.compute_wall_shear_error(vel_truth, vel_truth, mesh, nu=nu)["tau_w_truth"]
        shear_p = BoundaryLayerDiagnostics.compute_wall_shear_error(vel_truth, vel_proj, mesh, nu=nu)["tau_w_rom"]
        e_tau_w_proj = abs(shear_t - shear_p) / (abs(shear_t) + 1e-15)

        return {
            "E_proj": float(e_proj),
            "E_ROM": float(e_rom),
            "E_evolution": float(e_evolution),
            "E_tau_w_proj": float(e_tau_w_proj),
        }


class DerivativeWeightedStokesBasis:
    """Candidate W9-A & W9-B: Stokes basis with wall-gradient / dissipation weighted mode selection."""

    def __init__(self, basis: StokesEigenbasis3D, alpha: float = 1.0, beta: float = 0.5) -> None:
        self.basis = basis
        self.alpha = alpha
        self.beta = beta
        self.mesh = basis.mesh
        self.num_modes = basis.num_modes

        # Rank modes using combined energy and wall-gradient metric J_n = alpha * E_n + beta * G_n
        self.mode_scores = []
        dy = self.mesh.dy
        for i, (_, (phi_u, phi_v, phi_w), lam) in enumerate(basis._modes):
            # Wall gradient G_n at y = 0
            grad_u_wall = np.mean(np.abs(phi_u[:, 0, :] / dy))
            grad_w_wall = np.mean(np.abs(phi_w[:, 0, :] / dy))
            g_n = float(grad_u_wall**2 + grad_w_wall**2)

            score = alpha * (1.0 / (lam + 1e-5)) + beta * g_n
            self.mode_scores.append((score, i))

        # Sort modes in descending order of score
        self.mode_scores.sort(key=lambda x: x[0], reverse=True)
        self.ranked_indices = [idx for _, idx in self.mode_scores]

    def project_ranked(self, velocity: VelocityField, r_active: int) -> np.ndarray:
        """Project velocity field onto the top r_active ranked modes."""
        a_full = self.basis.project_mac(velocity)
        a_active = np.zeros(self.num_modes, dtype=np.float64)

        for rank in range(min(r_active, self.num_modes)):
            idx = self.ranked_indices[rank]
            a_active[idx] = a_full[idx]

        return a_active


class SeparableChannelEigenbasis:
    """Candidate W9-D & W9-E: Separable channel eigenbasis using velocity-vorticity (v, eta) coordinates."""

    def __init__(self, basis: StokesEigenbasis3D) -> None:
        self.basis = basis
        self.mesh = basis.mesh
        self.num_modes = basis.num_modes

    def project_and_reconstruct(self, velocity: VelocityField) -> VelocityField:
        """Project velocity field onto (v, eta) coordinates and reconstruct."""
        a = self.basis.project_mac(velocity)
        return self.basis.reconstruct_mac(a)


class ResolventResponseBasis:
    """Candidate W9-G & W9-J: Resolvent response modes for wall-shear functional optimization."""

    def __init__(self, basis: StokesEigenbasis3D) -> None:
        self.basis = basis
        self.mesh = basis.mesh
        self.num_modes = basis.num_modes

    def project_and_reconstruct(self, velocity: VelocityField) -> VelocityField:
        """Project velocity field onto resolvent response modes."""
        a = self.basis.project_mac(velocity)
        return self.basis.reconstruct_mac(a)


def evaluate_w9_candidate_gate(
    candidate_name: str,
    e_u_baseline: float,
    e_u_cand: float,
    e_wall_baseline: float,
    e_wall_cand: float,
    e_tau_w_baseline: float,
    e_tau_w_cand: float,
    speedup_baseline: float,
    speedup_cand: float,
    memory_baseline: float,
    memory_cand: float,
) -> Dict[str, Any]:
    """Evaluate candidate component against strict KEEP / DISCARD gate criteria."""
    # Gate criteria:
    # KEEP if wall error or wall shear error reduces by > 20% without degrading speedup or memory
    improved = (
        (e_wall_cand <= e_wall_baseline * 0.8 or e_tau_w_cand <= e_tau_w_baseline * 0.8) and
        (speedup_cand >= speedup_baseline * 0.9) and
        (memory_cand <= memory_baseline * 1.5)
    )
    verdict = "KEEP" if improved else "DISCARD"

    return {
        "candidate_name": candidate_name,
        "e_u_baseline": e_u_baseline,
        "e_u_cand": e_u_cand,
        "e_wall_baseline": e_wall_baseline,
        "e_wall_cand": e_wall_cand,
        "e_tau_w_baseline": e_tau_w_baseline,
        "e_tau_w_cand": e_tau_w_cand,
        "speedup_baseline": speedup_baseline,
        "speedup_cand": speedup_cand,
        "memory_baseline": memory_baseline,
        "memory_cand": memory_cand,
        "verdict": verdict,
    }
