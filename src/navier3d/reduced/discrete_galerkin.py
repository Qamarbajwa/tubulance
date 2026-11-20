"""Discrete-Operator Galerkin Projection for Reduced-Order Navier-Stokes Modeling.

Defines reduced operators directly from the production MAC grid solver operators:
  A_r = Phi^T M L_h Phi
  Q_r(a, a) = Phi^T M N_h(Phi a)

Ensures Model B approximates numerical Model A exactly, eliminating discretization discrepancies.
"""
from __future__ import annotations

from typing import Tuple, Optional
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from ..operators import velocity_laplacian
from ..convection import centered_convection
from .solenoidal_basis import SolenoidalModalBasis


class DiscreteOperatorGalerkinROM:
    """Discrete-operator Galerkin ROM projecting Model A grid operators directly onto modal space."""

    def __init__(
        self,
        basis: SolenoidalModalBasis,
        nu: float = 0.001,
        bcs: Optional[BoundaryConditionSet] = None,
    ) -> None:
        self.basis = basis
        self.mesh = basis.mesh
        self.nu = nu
        self.bcs = bcs if bcs is not None else BoundaryConditionSet.all_periodic()
        self.r = basis.num_modes

        # Precompute discrete linear operator matrix A_r = nu * <phi_k, L_h phi_j>_MAC
        self.A_r = np.zeros((self.r, self.r), dtype=np.float64)
        self._build_linear_operator()

    def _build_linear_operator(self) -> None:
        """Project full grid 2nd-order Laplacian operator L_h directly onto modal basis."""
        r = self.r
        for k in range(r):
            a_unit = np.zeros(r)
            a_unit[k] = 1.0
            vel_k = self.basis.reconstruct_mac(a_unit)
            apply_velocity_bc(vel_k, self.bcs)

            # Evaluate full grid MAC Laplacian L_h(vel_k)
            lap_vel = velocity_laplacian(vel_k, self.mesh)

            # Project onto basis
            proj_lap = self.basis.project_mac(lap_vel)

            # Store A_r[:, k] = nu * proj_lap
            self.A_r[:, k] = self.nu * proj_lap

    def evaluate_rhs(self, a: np.ndarray) -> np.ndarray:
        """Evaluate discrete-operator Galerkin RHS: dot_a = A_r a + P_r N_h(Phi a)."""
        # 1. Linear viscous term A_r a
        dot_a_visc = self.A_r @ a

        # 2. Reconstruct MAC velocity field u = Phi a
        vel = self.basis.reconstruct_mac(a)
        apply_velocity_bc(vel, self.bcs)

        # 3. Full grid convection N_h(u)
        conv_grid = centered_convection(vel, self.mesh)

        # 4. Project full grid convection onto modal basis: P_r N_h(u)
        dot_a_conv = self.basis.project_mac(conv_grid)

        return dot_a_visc + dot_a_conv

    def step_rk4(self, a: np.ndarray, dt: float) -> np.ndarray:
        """Advance modal amplitudes a by one timestep dt using 4th-order Runge-Kutta."""
        k1 = self.evaluate_rhs(a)
        k2 = self.evaluate_rhs(a + 0.5 * dt * k1)
        k3 = self.evaluate_rhs(a + 0.5 * dt * k2)
        k4 = self.evaluate_rhs(a + dt * k3)
        return a + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    def run(self, a0: np.ndarray, dt: float, n_steps: int) -> Tuple[np.ndarray, np.ndarray]:
        """Run discrete-operator Galerkin ROM for n_steps."""
        a = a0.copy()
        history = [a.copy()]
        for _ in range(n_steps):
            a = self.step_rk4(a, dt)
            history.append(a.copy())
        return a, np.array(history)
