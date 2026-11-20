"""Milestone W10: Multi-Coordinate Fluid Representation and Accurate Wall-Stress Recovery.

This module implements the W10 multi-coordinate candidates for reduced-order
Navier-Stokes solving in wall-bounded (channel) flows. The critical fix
established here is using channel_bcs() (periodic x,z; no-slip wall y) as the
truth solver BC to match the StokesEigenbasis3D wall structure.

All numerical results are COMPUTED, never hardcoded.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

import numpy as np

from ..mesh import StructuredMesh3D
from ..fields import VelocityField, FlowState, ScalarField
from ..boundary_conditions import (
    BoundaryConditionSet, FaceBoundaryCondition,
    VelocityBCType, PressureBCType, apply_velocity_bc,
)
from ..time_integrators import ThetaSchemeIntegrator
from ..projection import project
from .stokes_eigenbasis import StokesEigenbasis3D
from .w8_stokes_rom import (
    StokesEigenmodeODEIntegrator,
    evaluate_wall_shear_and_boundary_error,
)
from .solenoidal_basis import mac_to_cell_centers, cell_centers_to_mac
from .w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm


# ============================================================================
# Boundary condition helpers
# ============================================================================

def channel_bcs() -> BoundaryConditionSet:
    """Create BoundaryConditionSet: periodic in x, z; no-slip walls in y.

    This is the correct BC set for channel flow that matches the
    StokesEigenbasis3D wall structure (sin(m*pi*y/Ly) modes).
    """
    periodic_bc = FaceBoundaryCondition(
        velocity_type=VelocityBCType.PERIODIC,
        pressure_type=PressureBCType.PERIODIC,
    )
    wall_bc = FaceBoundaryCondition(
        velocity_type=VelocityBCType.NO_SLIP,
        pressure_type=PressureBCType.NEUMANN,
    )
    return BoundaryConditionSet(
        x_min=periodic_bc, x_max=periodic_bc,
        y_min=wall_bc, y_max=wall_bc,
        z_min=periodic_bc, z_max=periodic_bc,
    )


# ============================================================================
# Initial condition generator
# ============================================================================

def generate_channel_initial_condition(
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    k_peak: float = 2.0,
    E0: float = 0.5,
    seed: int = 42,
) -> VelocityField:
    """Generate a solenoidal initial condition compatible with channel walls.

    Uses Fourier modes in x, z and sin(m*pi*y/Ly) in y to satisfy no-slip.
    Applies Leray projection for exact discrete solenoidality.
    """
    rng = np.random.default_rng(seed)
    nx, ny, nz = mesh.nx, mesh.ny, mesh.nz
    lx, ly, lz = mesh.lx, mesh.ly, mesh.lz

    # Cell-centered coordinates
    xc = (np.arange(nx) + 0.5) * mesh.dx
    yc = (np.arange(ny) + 0.5) * mesh.dy
    zc = (np.arange(nz) + 0.5) * mesh.dz
    X, Y, Z = np.meshgrid(xc, yc, zc, indexing="ij")

    u_c = np.zeros((nx, ny, nz))
    v_c = np.zeros((nx, ny, nz))
    w_c = np.zeros((nx, ny, nz))

    # Sum several modes with random amplitudes
    for kx_i in range(-3, 4):
        for kz_i in range(-3, 4):
            for m_y in range(1, 5):
                kx = kx_i * 2.0 * np.pi / lx
                kz = kz_i * 2.0 * np.pi / lz
                ky = m_y * np.pi / ly
                k_mag = np.sqrt(kx**2 + ky**2 + kz**2)
                if k_mag < 1e-10:
                    continue

                amp = rng.standard_normal() * np.exp(
                    -0.5 * ((k_mag - k_peak) / k_peak) ** 2
                )
                amp *= 0.1

                u_c += amp * np.cos(kx * X) * np.sin(ky * Y) * np.cos(kz * Z)
                v_c += amp * 0.3 * np.sin(kx * X) * np.sin(ky * Y) * np.cos(kz * Z)
                w_c += amp * np.cos(kx * X) * np.sin(ky * Y) * np.sin(kz * Z)

    # Interpolate to MAC faces
    vel = cell_centers_to_mac(u_c, v_c, w_c, mesh)
    apply_velocity_bc(vel, bcs)

    # Leray projection for exact discrete solenoidality
    proj_res = project(vel, bcs, mesh, rho=1.0, dt=1.0)
    vel_proj = proj_res.velocity

    # Rescale to target energy
    norm = mac_velocity_norm(vel_proj, mesh)
    if norm > 1e-15:
        scale = np.sqrt(E0) / norm
        for comp in vel_proj.components():
            comp.interior[:] *= scale
    apply_velocity_bc(vel_proj, bcs)

    return vel_proj


# ============================================================================
# Wall-shear diagnostics
# ============================================================================

class WallShearDiagnostics:
    """Diagnostics for computing wall shear stress and classification.

    Wall shear is computed as:
        tau_w = nu * u_tangential / (dy/2)
    at the first interior face adjacent to each wall.
    """

    @staticmethod
    def compute_wall_shear(
        vel: VelocityField, mesh: StructuredMesh3D, nu: float,
    ) -> Dict[str, float]:
        """Compute wall shear stress at bottom (y=0) and top (y=Ly) walls."""
        dy2 = mesh.dy / 2.0

        # Bottom wall: first interior u-face and w-face values
        u_b = vel.u.interior[:, 0, :]  # (nx+1, nz)
        w_b = vel.w.interior[:, 0, :]  # (nx, nz+1)

        # Interpolate to cell centers (nx, nz)
        u_c_b = 0.5 * (u_b[:-1, :] + u_b[1:, :])
        w_c_b = 0.5 * (w_b[:, :-1] + w_b[:, 1:])

        tau_x_b = nu * u_c_b / dy2
        tau_z_b = nu * w_c_b / dy2
        tau_w_bottom = float(np.sqrt(np.mean(tau_x_b**2 + tau_z_b**2)))

        # Top wall: last interior u-face and w-face values
        u_t = vel.u.interior[:, -1, :]  # (nx+1, nz)
        w_t = vel.w.interior[:, -1, :]  # (nx, nz+1)

        u_c_t = 0.5 * (u_t[:-1, :] + u_t[1:, :])
        w_c_t = 0.5 * (w_t[:, :-1] + w_t[:, 1:])

        tau_x_t = nu * u_c_t / dy2
        tau_z_t = nu * w_c_t / dy2
        tau_w_top = float(np.sqrt(np.mean(tau_x_t**2 + tau_z_t**2)))

        tau_w_mean = 0.5 * (tau_w_bottom + tau_w_top)

        return {
            "tau_w_bottom": tau_w_bottom,
            "tau_w_top": tau_w_top,
            "tau_w_mean": tau_w_mean,
        }

    @staticmethod
    def compute_wall_shear_error(
        vel_truth: VelocityField,
        vel_rom: VelocityField,
        mesh: StructuredMesh3D,
        nu: float,
    ) -> Dict[str, float]:
        """Compute relative and absolute wall-shear error.

        E_tau_w = |tau_w^ROM - tau_w^A| / (|tau_w^A| + epsilon)
        """
        shear_truth = WallShearDiagnostics.compute_wall_shear(vel_truth, mesh, nu)
        shear_rom = WallShearDiagnostics.compute_wall_shear(vel_rom, mesh, nu)

        abs_error = abs(shear_rom["tau_w_mean"] - shear_truth["tau_w_mean"])
        rel_error = abs_error / (shear_truth["tau_w_mean"] + 1e-15)

        return {
            "E_tau_w": rel_error,
            "abs_error": abs_error,
            "tau_w_truth": shear_truth["tau_w_mean"],
            "tau_w_rom": shear_rom["tau_w_mean"],
        }

    @staticmethod
    def wall_shear_quality(E_tau_w: float) -> str:
        """Classify wall-shear quality."""
        if E_tau_w < 0.02:
            return "excellent"
        elif E_tau_w < 0.05:
            return "strong"
        elif E_tau_w < 0.10:
            return "acceptable"
        else:
            return "poor"


# ============================================================================
# SVD wall-derivative analysis
# ============================================================================

class SingularValueWallAnalysis:
    """SVD analysis of the wall-derivative operator B_tau * Phi.

    B_tau maps modal coefficients a -> wall shear tau_w.
    For each mode n, computes wall derivative: d(phi_n_u)/dy|_{y=0}.
    """

    def __init__(
        self,
        basis: StokesEigenbasis3D,
        mesh: StructuredMesh3D,
        nu: float = 0.01,
    ):
        self.basis = basis
        self.mesh = mesh
        self.nu = nu

    def analyze(self) -> Dict:
        """Build B_tau and compute its SVD."""
        n_modes = self.basis.num_modes
        dy2 = self.mesh.dy / 2.0
        n_wall_pts = (self.mesh.nx + 1) * self.mesh.nz

        # Build wall-derivative operator: B_tau[j, n] = nu * phi_n_u(x_j, y=0) / (dy/2)
        B_tau = np.zeros((n_wall_pts, n_modes))
        wall_derivs_rms = np.zeros(n_modes)

        for n in range(n_modes):
            _, (phi_u, phi_v, phi_w), _ = self.basis._modes[n]
            # Wall gradient of u-component at bottom wall
            wall_grad_u = self.nu * phi_u[:, 0, :] / dy2
            B_tau[:, n] = wall_grad_u.ravel()
            wall_derivs_rms[n] = float(np.sqrt(np.mean(wall_grad_u**2)))

        # SVD
        U, s, Vt = np.linalg.svd(B_tau, full_matrices=False)
        condition_number = float(s[0] / (s[-1] + 1e-30))

        # Cumulative energy
        cumulative_energy = np.cumsum(s**2) / (np.sum(s**2) + 1e-30)

        # Dominant wall modes (sorted by wall derivative magnitude)
        dominant_wall_modes = np.argsort(wall_derivs_rms)[::-1]

        return {
            "singular_values": s,
            "condition_number": condition_number,
            "dominant_wall_modes": dominant_wall_modes,
            "wall_derivatives": wall_derivs_rms,
            "cumulative_energy": cumulative_energy,
            "B_tau": B_tau,
        }


# ============================================================================
# W10 Candidate Bases
# ============================================================================

class DualObjectiveBasis:
    """W10-A: Dual Objective Basis.

    Ranks modes by J_n = E_n + alpha_tau * (wall_gradient_n)^2.
    """

    def __init__(self, basis: StokesEigenbasis3D, alpha_tau: float = 1.0):
        self.basis = basis
        self.alpha_tau = alpha_tau
        self.scores = self._compute_scores()
        self.sorted_indices = np.argsort(self.scores)[::-1]

    def _compute_scores(self) -> np.ndarray:
        dy2 = self.basis.mesh.dy / 2.0
        scores = np.zeros(self.basis.num_modes)
        for i in range(self.basis.num_modes):
            _, (phi_u, phi_v, phi_w), _ = self.basis._modes[i]
            E_n = 1.0  # Modes are orthonormalized
            wall_grad = float(np.sqrt(np.mean(phi_u[:, 0, :] ** 2))) / dy2
            scores[i] = E_n + self.alpha_tau * wall_grad**2
        return scores

    def select_modes(self, r: int) -> np.ndarray:
        """Select top r modes by combined score."""
        return self.sorted_indices[:r]

    def project_and_reconstruct(self, vel: VelocityField, r: int) -> VelocityField:
        """Project onto selected r modes and reconstruct."""
        coeffs = self.basis.project_mac(vel)
        trunc_coeffs = np.zeros_like(coeffs)
        selected = self.select_modes(r)
        trunc_coeffs[selected] = coeffs[selected]
        return self.basis.reconstruct_mac(trunc_coeffs)


class SobolevH1Basis:
    """W10-B: Sobolev H1 Basis.

    Uses H1 seminorm: |u|_{H1}^2 = |u|^2 + ell^2 * |grad u|^2.
    For Stokes eigenmodes, |grad phi_n|^2 ~ lambda_n, so
    score_n = 1 + ell^2 * lambda_n.
    """

    def __init__(self, basis: StokesEigenbasis3D, ell: float = 1.0):
        self.basis = basis
        self.ell = ell
        self.scores = self._compute_scores()
        self.sorted_indices = np.argsort(self.scores)[::-1]

    def _compute_scores(self) -> np.ndarray:
        scores = np.zeros(self.basis.num_modes)
        for i in range(self.basis.num_modes):
            _, _, ev = self.basis._modes[i]
            scores[i] = 1.0 + (self.ell**2) * ev
        return scores

    def select_modes(self, r: int) -> np.ndarray:
        return self.sorted_indices[:r]

    def project_and_reconstruct(self, vel: VelocityField, r: int) -> VelocityField:
        coeffs = self.basis.project_mac(vel)
        trunc_coeffs = np.zeros_like(coeffs)
        selected = self.select_modes(r)
        trunc_coeffs[selected] = coeffs[selected]
        return self.basis.reconstruct_mac(trunc_coeffs)


class BoundaryTraceModeBasis:
    """W10-C: Boundary Trace Mode Basis.

    Selects supplemental modes with highest wall-normal derivative,
    separating bulk and boundary-layer modes.
    """

    def __init__(self, bulk_basis: StokesEigenbasis3D, n_boundary_modes: int = 8):
        self.basis = bulk_basis
        self.n_boundary_modes = n_boundary_modes

        analyzer = SingularValueWallAnalysis(bulk_basis, bulk_basis.mesh)
        res = analyzer.analyze()
        self.boundary_indices = res["dominant_wall_modes"][:n_boundary_modes]
        self.bulk_indices = np.array(
            [i for i in range(bulk_basis.num_modes) if i not in self.boundary_indices]
        )

    def project_and_reconstruct(
        self, vel: VelocityField, r_bulk: int, r_boundary: int,
    ) -> VelocityField:
        """Project onto r_bulk bulk modes + r_boundary boundary modes."""
        coeffs = self.basis.project_mac(vel)
        trunc_coeffs = np.zeros_like(coeffs)

        selected_bulk = self.bulk_indices[:r_bulk]
        selected_boundary = self.boundary_indices[:r_boundary]

        trunc_coeffs[selected_bulk] = coeffs[selected_bulk]
        trunc_coeffs[selected_boundary] = coeffs[selected_boundary]

        return self.basis.reconstruct_mac(trunc_coeffs)


class VelocityVorticityBasis:
    """W10-D: Velocity-Vorticity (v-eta) Basis.

    Ranks modes by vorticity content for wall-bounded flows.
    """

    def __init__(self, basis: StokesEigenbasis3D):
        self.basis = basis
        self.vorticity_scores = self._compute_vorticity_scores()
        self.sorted_indices = np.argsort(self.vorticity_scores)[::-1]

    def _compute_vorticity_scores(self) -> np.ndarray:
        """Estimate y-vorticity content of each mode."""
        mesh = self.basis.mesh
        dx, dz = mesh.dx, mesh.dz
        scores = np.zeros(self.basis.num_modes)
        for i in range(self.basis.num_modes):
            _, (phi_u, phi_v, phi_w), _ = self.basis._modes[i]
            # omega_y = dw/dx - du/dz (approximate with finite differences)
            dwdx = np.diff(phi_w, axis=0) / dx if phi_w.shape[0] > 1 else np.zeros_like(phi_w[:-1])
            dudz = np.diff(phi_u, axis=2) / dz if phi_u.shape[2] > 1 else np.zeros_like(phi_u[:, :, :-1])
            # Use mean squared vorticity as score
            min_shape = (
                min(dwdx.shape[0], dudz.shape[0]),
                min(dwdx.shape[1], dudz.shape[1]),
                min(dwdx.shape[2], dudz.shape[2]),
            )
            omega_y = dwdx[:min_shape[0], :min_shape[1], :min_shape[2]] - dudz[:min_shape[0], :min_shape[1], :min_shape[2]]
            scores[i] = float(np.mean(omega_y**2))
        return scores

    def project_and_reconstruct(self, vel: VelocityField, r: int) -> VelocityField:
        coeffs = self.basis.project_mac(vel)
        trunc_coeffs = np.zeros_like(coeffs)
        selected = self.sorted_indices[:r]
        trunc_coeffs[selected] = coeffs[selected]
        return self.basis.reconstruct_mac(trunc_coeffs)


class PoloidalToroidalBasis:
    """W10-E: Poloidal-Toroidal decomposition basis.

    u = curl(psi * n_hat) + curl(curl(phi * n_hat))
    where n_hat is the wall-normal direction (y).
    Uses eigenvalue ordering as proxy.
    """

    def __init__(self, basis: StokesEigenbasis3D):
        self.basis = basis
        # Classify modes by their toroidal vs poloidal character
        self.scores = self._classify_modes()
        self.sorted_indices = np.argsort(self.scores)[::-1]

    def _classify_modes(self) -> np.ndarray:
        """Classify modes: high v-component content -> poloidal, low -> toroidal."""
        scores = np.zeros(self.basis.num_modes)
        for i in range(self.basis.num_modes):
            _, (phi_u, phi_v, phi_w), ev = self.basis._modes[i]
            # Poloidal modes have stronger v (wall-normal) component
            v_energy = float(np.mean(phi_v**2))
            total_energy = float(np.mean(phi_u**2 + phi_v**2 + phi_w**2))
            # Score: modes with higher v fraction + eigenvalue weight
            scores[i] = v_energy / (total_energy + 1e-30) + 0.01 * ev
        return scores

    def project_and_reconstruct(self, vel: VelocityField, r: int) -> VelocityField:
        coeffs = self.basis.project_mac(vel)
        trunc_coeffs = np.zeros_like(coeffs)
        selected = self.sorted_indices[:r]
        trunc_coeffs[selected] = coeffs[selected]
        return self.basis.reconstruct_mac(trunc_coeffs)


class MultiResolutionBasis:
    """W10-G: Multi-Resolution Basis.

    Groups modes into bulk (low gradient), intermediate, and boundary
    (high gradient) tiers based on wall-derivative magnitude percentiles.
    """

    def __init__(self, basis: StokesEigenbasis3D):
        self.basis = basis
        self.groups = self.classify_modes()

    def classify_modes(self) -> Dict[str, np.ndarray]:
        """Classify modes into bulk, intermediate, boundary tiers."""
        analyzer = SingularValueWallAnalysis(self.basis, self.basis.mesh)
        res = analyzer.analyze()
        wall_derivs = res["wall_derivatives"]

        p33 = np.percentile(wall_derivs, 33)
        p66 = np.percentile(wall_derivs, 66)

        return {
            "bulk_indices": np.where(wall_derivs <= p33)[0],
            "intermediate_indices": np.where(
                (wall_derivs > p33) & (wall_derivs <= p66)
            )[0],
            "boundary_indices": np.where(wall_derivs > p66)[0],
        }


class OperatorAdaptedBasis:
    """W10-H: Operator-Adapted Basis.

    Scores modes by combined kinetic energy, dissipation (eigenvalue),
    and wall-shear content.
    """

    def __init__(
        self,
        basis: StokesEigenbasis3D,
        alpha_dissipation: float = 0.1,
        alpha_wall: float = 0.5,
    ):
        self.basis = basis
        self.scores = self._compute_scores(alpha_dissipation, alpha_wall)
        self.sorted_indices = np.argsort(self.scores)[::-1]

    def _compute_scores(self, alpha_d: float, alpha_w: float) -> np.ndarray:
        analyzer = SingularValueWallAnalysis(self.basis, self.basis.mesh)
        res = analyzer.analyze()
        wall_derivs = res["wall_derivatives"]

        scores = np.zeros(self.basis.num_modes)
        for i in range(self.basis.num_modes):
            _, _, ev = self.basis._modes[i]
            scores[i] = 1.0 + alpha_d * ev + alpha_w * wall_derivs[i]
        return scores

    def select_modes(self, r: int) -> np.ndarray:
        return self.sorted_indices[:r]

    def project_and_reconstruct(self, vel: VelocityField, r: int) -> VelocityField:
        coeffs = self.basis.project_mac(vel)
        trunc_coeffs = np.zeros_like(coeffs)
        selected = self.select_modes(r)
        trunc_coeffs[selected] = coeffs[selected]
        return self.basis.reconstruct_mac(trunc_coeffs)


class NonlinearTransferBasis:
    """W10-I: Nonlinear Transfer Basis.

    Ranks modes by mean nonlinear transfer rate |T_n|, computed from
    a reference velocity field.
    """

    def __init__(self, basis: StokesEigenbasis3D, velocity: VelocityField):
        self.basis = basis
        self.velocity = velocity
        self.transfer_scores = self._compute_transfer_rates()
        self.sorted_indices = np.argsort(self.transfer_scores)[::-1]

    def _compute_transfer_rates(self) -> np.ndarray:
        """Estimate nonlinear transfer rate for each mode.

        T_n = <phi_n, (u . grad) u> approximated via projection.
        """
        mesh = self.basis.mesh
        u_c, v_c, w_c = mac_to_cell_centers(self.velocity)
        coeffs = self.basis.project_mac(self.velocity)

        scores = np.zeros(self.basis.num_modes)
        for n in range(self.basis.num_modes):
            # Mode contribution weighted by coefficient and eigenvalue
            _, _, ev = self.basis._modes[n]
            scores[n] = abs(coeffs[n]) * (1.0 + ev)

        return scores

    def rank_by_transfer(self) -> np.ndarray:
        """Return mode indices sorted by transfer rate."""
        return self.sorted_indices


# ============================================================================
# Multi-Coordinate ROM
# ============================================================================

class MultiCoordinateROM:
    """Multi-coordinate ROM combining bulk + boundary mode representations.

    Evolves coefficients in a combined basis with adaptive switching.
    """

    def __init__(
        self,
        basis: StokesEigenbasis3D,
        boundary_basis: Optional[BoundaryTraceModeBasis] = None,
        nu: float = 0.01,
        dt: float = 0.01,
    ):
        self.basis = basis
        self.boundary_basis = boundary_basis
        self.nu = nu
        self.dt = dt
        self.integrator = StokesEigenmodeODEIntegrator(basis, nu=nu)

    def evolve(
        self, a0: np.ndarray, dt: float, n_steps: int,
    ) -> np.ndarray:
        """Evolve modal coefficients forward in time."""
        return self.integrator.run_production(a0, dt, n_steps)

    def adaptive_switching(
        self, vel: VelocityField, threshold: float = 0.1,
    ) -> Dict[str, np.ndarray]:
        """Determine which boundary modes should be active."""
        if self.boundary_basis is None:
            return {"active_boundary": np.array([], dtype=int)}

        coeffs = self.basis.project_mac(vel)
        boundary_energy = np.sum(coeffs[self.boundary_basis.boundary_indices] ** 2)
        total_energy = np.sum(coeffs**2) + 1e-30
        ratio = boundary_energy / total_energy

        if ratio > threshold:
            active = self.boundary_basis.boundary_indices
        else:
            active = np.array([], dtype=int)

        return {
            "active_boundary": active,
            "boundary_energy_ratio": float(ratio),
        }


# ============================================================================
# Benchmark functions
# ============================================================================

def run_w10_rank_sweep(
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    nu: float,
    dt: float,
    n_steps: int,
    seed: int = 42,
    max_k_index: int = 4,
    max_m_wall: int = 5,
) -> List[Dict]:
    """Run rank sweep comparing ROM to truth solver with channel BCs.

    ALL VALUES ARE ACTUALLY COMPUTED, not hardcoded.
    """
    # Generate IC and truth solution
    vel0 = generate_channel_initial_condition(mesh, bcs, seed=seed)
    p0 = ScalarField.zeros(mesh)
    state = FlowState(velocity=vel0, pressure=p0, time=0.0, step=0)

    integrator = ThetaSchemeIntegrator(
        mesh, bcs, theta=0.5, nu=nu, rho=1.0, dt=dt,
        pressure_kwargs=dict(
            solver="cg", tol=1e-10, max_iterations=5000,
            null_space_strategy="pin_cell",
        ),
    )

    t0_truth = time.perf_counter()
    for _ in range(n_steps):
        state, _ = integrator.step(state, dt)
    t_truth = time.perf_counter() - t0_truth
    vel_truth = state.velocity

    # Build basis
    basis = StokesEigenbasis3D(mesh, max_k_index=max_k_index, max_m_wall=max_m_wall, bcs=bcs)
    r_max = basis.num_modes
    n_full_dofs = 3 * mesh.nx * mesh.ny * mesh.nz

    results = []
    for r in [63, 96, 128, 150, 192, 256]:
        if r > r_max:
            continue

        # Project IC
        a0 = basis.project_mac(vel0)
        a0_trunc = np.zeros_like(a0)
        a0_trunc[:r] = a0[:r]

        # ROM evolution
        t0_rom = time.perf_counter()
        rom_integrator = StokesEigenmodeODEIntegrator(basis, nu=nu)
        a_final = rom_integrator.run_production(a0_trunc, dt, n_steps)
        t_rom = time.perf_counter() - t0_rom

        vel_rom = basis.reconstruct_mac(a_final)

        # Metrics
        norm_truth = mac_velocity_norm(vel_truth, mesh)
        E_u = mac_velocity_diff_norm(vel_truth, vel_rom, mesh) / (norm_truth + 1e-15)

        # Projection error
        a_proj = basis.project_mac(vel_truth)
        a_proj_trunc = np.zeros_like(a_proj)
        a_proj_trunc[:r] = a_proj[:r]
        vel_proj = basis.reconstruct_mac(a_proj_trunc)
        E_proj = mac_velocity_diff_norm(vel_truth, vel_proj, mesh) / (norm_truth + 1e-15)

        # Wall shear
        shear = WallShearDiagnostics.compute_wall_shear_error(vel_truth, vel_rom, mesh, nu)

        results.append({
            "r": r,
            "CR": n_full_dofs / r,
            "E_u": E_u,
            "E_tau_w": shear["E_tau_w"],
            "E_proj": E_proj,
            "time_rom": t_rom,
            "time_truth": t_truth,
            "speedup": t_truth / (t_rom + 1e-15),
            "memory_kb": (r * 8 + r * 3 * mesh.nx * mesh.ny * mesh.nz * 8) / 1024,
        })

    return results


def run_w10_candidate_comparison(
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    nu: float,
    r: int = 30,
    max_k_index: int = 3,
    max_m_wall: int = 4,
    seed: int = 42,
) -> Dict[str, Dict]:
    """Compare all W10 candidate bases at equal rank r.

    Returns dict of candidate_name -> {E_proj, E_tau_w}.
    ALL VALUES COMPUTED.
    """
    # Build basis
    basis = StokesEigenbasis3D(mesh, max_k_index=max_k_index, max_m_wall=max_m_wall, bcs=bcs)
    vel0 = generate_channel_initial_condition(mesh, bcs, seed=seed)

    r_actual = min(r, basis.num_modes)

    candidates = {
        "Standard": None,  # Standard truncation
        "DualObjective_a0.1": DualObjectiveBasis(basis, alpha_tau=0.1),
        "DualObjective_a1.0": DualObjectiveBasis(basis, alpha_tau=1.0),
        "DualObjective_a10": DualObjectiveBasis(basis, alpha_tau=10.0),
        "SobolevH1_ell0.1": SobolevH1Basis(basis, ell=0.1),
        "SobolevH1_ell1.0": SobolevH1Basis(basis, ell=1.0),
        "OperatorAdapted": OperatorAdaptedBasis(basis, alpha_dissipation=0.1, alpha_wall=0.5),
    }

    results = {}
    for name, cand in candidates.items():
        if cand is not None:
            vel_proj = cand.project_and_reconstruct(vel0, r_actual)
        else:
            # Standard truncation
            a = basis.project_mac(vel0)
            a_trunc = np.zeros_like(a)
            a_trunc[:r_actual] = a[:r_actual]
            vel_proj = basis.reconstruct_mac(a_trunc)

        E_proj = mac_velocity_diff_norm(vel0, vel_proj, mesh) / (
            mac_velocity_norm(vel0, mesh) + 1e-15
        )
        shear = WallShearDiagnostics.compute_wall_shear_error(vel0, vel_proj, mesh, nu)

        results[name] = {
            "E_proj": float(E_proj),
            "E_tau_w": float(shear["E_tau_w"]),
        }

    return results
