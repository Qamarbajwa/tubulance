"""Modal Eddy Viscosity Closure Models for Reduced-Order Navier-Stokes Integration.

Provides:
- fit_modal_eddy_viscosity: Fits modal eddy viscosity coefficients nu_ROM,k from exact closure residuals.
- ClosedModalODEIntegrator: Integrates modal ODEs with closure damping -nu_ROM,k * a_k.
"""
from __future__ import annotations

from typing import Tuple, List, Optional
import numpy as np

from ..fields import VelocityField
from .solenoidal_basis import SolenoidalModalBasis
from .modal_tensor import evaluate_pseudospectral_convection
from .modal_integrator import ModalODEIntegrator
from .w2_diagnostics import exact_closure_residual


def fit_modal_eddy_viscosity(
    snapshots: List[VelocityField],
    dt: float,
    basis: SolenoidalModalBasis,
    nu: float = 0.001,
) -> np.ndarray:
    """Fit modal eddy viscosity coefficients nu_ROM,k from snapshot residual correlations.

    nu_ROM,k = - < R_k^closure, a_k^truth > / < (a_k^truth)^2 >
    """
    res_dict = exact_closure_residual(snapshots, dt, basis, nu)
    r = basis.num_modes

    a_truth_list = np.array([basis.project_mac(s) for s in snapshots])  # (M, r)
    a_interior = a_truth_list[1:-1]  # (M-2, r)

    # Convert residual spectrum list back to array
    residuals = []
    lams = basis.get_laplacian_eigenvalues()
    M = len(snapshots)

    for m in range(1, M - 1):
        da_dt = (a_truth_list[m + 1] - a_truth_list[m - 1]) / (2.0 * dt)
        a_m = a_truth_list[m]
        rhs_model = -nu * lams * a_m + evaluate_pseudospectral_convection(basis, a_m)
        R_k = da_dt - rhs_model
        residuals.append(R_k)

    R_matrix = np.array(residuals)  # (M-2, r)

    # Compute modal eddy viscosity nu_ROM,k
    num = np.mean(R_matrix * a_interior, axis=0)
    den = np.mean(a_interior**2, axis=0) + 1e-15

    nu_rom = -num / den

    # Ensure non-negative damping for stability
    nu_rom = np.maximum(0.0, nu_rom)
    return nu_rom


class ClosedModalODEIntegrator(ModalODEIntegrator):
    """Modal ODE integrator extended with modal eddy viscosity closure damping."""

    def __init__(
        self,
        basis: SolenoidalModalBasis,
        nu: float = 0.001,
        nu_rom: Optional[np.ndarray] = None,
        evaluation_mode: str = "pseudospectral",
    ) -> None:
        super().__init__(basis, nu, evaluation_mode)
        self.nu_rom = nu_rom if nu_rom is not None else np.zeros(basis.num_modes, dtype=np.float64)

    def rhs(self, a: np.ndarray, F: Optional[np.ndarray] = None) -> np.ndarray:
        """Modal ODE RHS with closure: dot_a = -nu * lambda * a - nu_ROM * a + conv(a) + F."""
        dot_a_unclosed = super().rhs(a, F)
        # Add closure damping
        return dot_a_unclosed - self.nu_rom * a
