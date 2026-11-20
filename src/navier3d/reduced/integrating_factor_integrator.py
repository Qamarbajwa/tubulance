"""Integrating-Factor (Exponential Time Differencing) Modal ODE Integrator.

Provides:
- IntegratingFactorModalODEIntegrator: Solves linear viscous dissipation exactly via diagonal integrating factor b_k = e^(nu * lambda_k * t) * a_k.
"""
from __future__ import annotations

from typing import Optional, Tuple, List
import numpy as np

from .solenoidal_basis import SolenoidalModalBasis, FourierSolenoidalBasis
from .modal_integrator import ModalODEIntegrator, ModalStepDiagnostics
from .sparse_triad_engine import MinimalSpectralGridEvaluator, VectorizedTriadEvaluator, SparseTriadGraph
from .modal_tensor import evaluate_pseudospectral_convection


class IntegratingFactorModalODEIntegrator(ModalODEIntegrator):
    """Integrating-factor RK4 modal ODE integrator solving linear viscous decay exactly.

    b_k(t) = e^(nu * lambda_k * t) * a_k(t)
    dot_b_k(t) = e^(nu * lambda_k * t) * [ N_k(a(t)) + F_k ]
    """

    def __init__(
        self,
        basis: SolenoidalModalBasis,
        nu: float = 0.001,
        evaluation_mode: str = "minimal_spectral",
        analysis_mode: bool = True,
    ) -> None:
        super().__init__(basis, nu, evaluation_mode)
        self.analysis_mode = analysis_mode

        if evaluation_mode == "minimal_spectral" and isinstance(basis, FourierSolenoidalBasis):
            self.minimal_evaluator = MinimalSpectralGridEvaluator(basis, bcs=basis.bcs)

    def nonlinear_rhs(self, a: np.ndarray, F: Optional[np.ndarray] = None) -> np.ndarray:
        """Evaluate non-linear convection acceleration N_k(a) + F_k."""
        if self.evaluation_mode == "minimal_spectral" and hasattr(self, "minimal_evaluator"):
            dot_a_conv = self.minimal_evaluator.evaluate_convection_acceleration(a)
        else:
            dot_a_conv = evaluate_pseudospectral_convection(self.basis, a)

        if F is not None:
            dot_a_conv += F
        return dot_a_conv

    def step_rk4_if(self, a: np.ndarray, dt: float, t_curr: float = 0.0, F: Optional[np.ndarray] = None) -> np.ndarray:
        """Advance modal state by one timestep using Integrating-Factor RK4."""
        lams = self.basis.get_laplacian_eigenvalues()
        r = len(a)

        # Exponential factor E(dt) = exp(-nu * lambda * dt)
        e_half = np.exp(-self.nu * lams * 0.5 * dt)
        e_full = np.exp(-self.nu * lams * dt)

        # RK4 stages for integrating factor
        N1 = self.nonlinear_rhs(a, F)

        a_stage2 = e_half * (a + 0.5 * dt * N1)
        N2 = self.nonlinear_rhs(a_stage2, F)

        a_stage3 = e_half * a + 0.5 * dt * N2
        N3 = self.nonlinear_rhs(a_stage3, F)

        a_stage4 = e_full * a + e_half * dt * N3
        N4 = self.nonlinear_rhs(a_stage4, F)

        # Update
        a_next = e_full * a + (dt / 6.0) * (e_full * N1 + 2.0 * e_half * N2 + 2.0 * e_half * N3 + N4)
        return a_next

    def run_production(self, a0: np.ndarray, dt: float, n_steps: int) -> np.ndarray:
        """High-speed production run without diagnostic logging overhead."""
        a = a0.copy()
        t = 0.0
        for _ in range(n_steps):
            a = self.step_rk4_if(a, dt, t_curr=t)
            t += dt
        return a
