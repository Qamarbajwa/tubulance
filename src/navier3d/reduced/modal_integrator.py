"""Modal ODE Time Integrator for Reduced-Order Navier-Stokes Modeling.

Provides:
- ModalODEIntegrator: Solves the modal ODE system:
    dot_a_k = -nu * lambda_k * a_k + sum_ij Q_kij * a_i * a_j + F_k
  directly in coefficient space.

Diagnostic Features:
- Exact modal kinetic energy E_K = 0.5 * sum_n a_n^2.
- Exact modal enstrophy Omega = 0.5 * sum_n lambda_n a_n^2.
- Helicity computation H = int u . curl(u) dV.
- Closure error residual R_k^closure = dot_a_k^full_projected - dot_a_k^ROM.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple
import numpy as np

from .solenoidal_basis import SolenoidalModalBasis, mac_to_cell_centers
from .modal_tensor import SparseModalTensor, evaluate_pseudospectral_convection
from ..fields import VelocityField
from ..mesh import StructuredMesh3D


@dataclass
class ModalStepDiagnostics:
    time: float
    step: int
    dt: float
    kinetic_energy: float
    enstrophy: float
    helicity: float
    cfl_equivalent: float


class ModalODEIntegrator:
    """Time integrator for reduced-order modal Navier-Stokes equations.

    Parameters
    ----------
    basis : SolenoidalModalBasis
        Divergence-free vector basis.
    nu : float
        Kinematic viscosity nu.
    evaluation_mode : str, default="sparse_tensor"
        "sparse_tensor" or "pseudospectral".
    sparse_tensor_tol : float, default=1e-12
        Tolerance for building non-zero entries in SparseModalTensor.
    """

    def __init__(
        self,
        basis: SolenoidalModalBasis,
        nu: float = 0.002,
        evaluation_mode: str = "sparse_tensor",
        sparse_tensor_tol: float = 1e-12,
    ) -> None:
        self.basis = basis
        self.nu = float(nu)
        self.evaluation_mode = evaluation_mode.lower()

        self.r = basis.num_modes
        self.eigenvalues = basis.get_laplacian_eigenvalues()

        if self.evaluation_mode == "sparse_tensor":
            self.tensor: Optional[SparseModalTensor] = SparseModalTensor(basis, tol=sparse_tensor_tol)
        else:
            self.tensor = None

    def rhs(self, a: np.ndarray, F: Optional[np.ndarray] = None) -> np.ndarray:
        """Compute RHS dot_a = -nu * lambda * a + Q(a, a) + F."""
        # Viscous diffusion term: -nu * lambda_k * a_k
        dot_a_visc = -self.nu * self.eigenvalues * a

        # Convection term: Q(a, a)
        if self.evaluation_mode == "sparse_tensor" and self.tensor is not None:
            dot_a_conv = self.tensor.evaluate_convection_acceleration(a)
        else:
            dot_a_conv = evaluate_pseudospectral_convection(self.basis, a)

        dot_a = dot_a_visc + dot_a_conv
        if F is not None:
            dot_a += F
        return dot_a

    def step_rk4(self, a: np.ndarray, dt: float, F: Optional[np.ndarray] = None) -> np.ndarray:
        """Perform a single 4th-order Runge-Kutta step in coefficient space."""
        k1 = self.rhs(a, F)
        k2 = self.rhs(a + 0.5 * dt * k1, F)
        k3 = self.rhs(a + 0.5 * dt * k2, F)
        k4 = self.rhs(a + dt * k3, F)

        return a + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    def kinetic_energy(self, a: np.ndarray) -> float:
        """Compute total kinetic energy E_K = 0.5 * sum_n a_n^2."""
        return float(0.5 * np.sum(a**2))

    def enstrophy(self, a: np.ndarray) -> float:
        """Compute total enstrophy Omega = 0.5 * sum_n lambda_n a_n^2."""
        return float(0.5 * np.sum(self.eigenvalues * (a**2)))

    def helicity(self, a: np.ndarray) -> float:
        """Compute total helicity H = int u . curl(u) dV."""
        mesh = self.basis.mesh
        u_c, v_c, w_c = self.basis.reconstruct_cell_centers(a)
        dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

        # Vorticity curl(u) = (dw/dy - dv/dz, du/dz - dw/dx, dv/dx - du/dy)
        du_dy = (np.roll(u_c, -1, 1) - np.roll(u_c, 1, 1)) / (2.0 * dy)
        du_dz = (np.roll(u_c, -1, 2) - np.roll(u_c, 1, 2)) / (2.0 * dz)

        dv_dx = (np.roll(v_c, -1, 0) - np.roll(v_c, 1, 0)) / (2.0 * dx)
        dv_dz = (np.roll(v_c, -1, 2) - np.roll(v_c, 1, 2)) / (2.0 * dz)

        dw_dx = (np.roll(w_c, -1, 0) - np.roll(w_c, 1, 0)) / (2.0 * dx)
        dw_dy = (np.roll(w_c, -1, 1) - np.roll(w_c, 1, 1)) / (2.0 * dy)

        wx = dw_dy - dv_dz
        wy = du_dz - dw_dx
        wz = dv_dx - du_dy

        H = np.sum(u_c * wx + v_c * wy + w_c * wz) * mesh.cell_volume
        return float(H)

    def compute_closure_residual(self, a_full_projected: np.ndarray, dot_a_full_projected: np.ndarray) -> np.ndarray:
        """Compute closure residual R_k^closure = dot_a_k^full_projected - dot_a_k^ROM."""
        dot_a_rom = self.rhs(a_full_projected)
        return dot_a_full_projected - dot_a_rom

    def run(
        self,
        a0: np.ndarray,
        dt: float,
        n_steps: int,
        F: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, List[ModalStepDiagnostics]]:
        """Run modal simulation for n_steps."""
        a = a0.copy()
        history: List[ModalStepDiagnostics] = []

        dx_min = min(self.basis.mesh.dx, self.basis.mesh.dy, self.basis.mesh.dz)

        for step in range(1, n_steps + 1):
            t = step * dt
            a = self.step_rk4(a, dt, F)

            ke = self.kinetic_energy(a)
            ens = self.enstrophy(a)
            hel = self.helicity(a)

            # Equivalent max velocity for CFL estimation
            v_max = np.sqrt(2.0 * ke)
            cfl = v_max * dt / dx_min

            history.append(
                ModalStepDiagnostics(
                    time=t, step=step, dt=dt, kinetic_energy=ke, enstrophy=ens, helicity=hel, cfl_equivalent=cfl
                )
            )

        return a, history
