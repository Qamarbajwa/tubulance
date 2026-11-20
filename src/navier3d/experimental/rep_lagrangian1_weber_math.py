"""Program NS-REP-LAGRANGIAN-1: Stochastic Lagrangian / Weber / Cauchy Invariant Audit.

Primary References:
    1. Peter Constantin & Gautam Iyer (2008),
       "A stochastic-Lagrangian approach to the Navier-Stokes equations",
       arXiv:math/0511067 / Comm. Pure Appl. Math. 61 (2008), 330-345.
    2. Exact Closed Stochastic Weber System (2026),
       "Exact Closed Stochastic Weber System for 3D Incompressible Navier-Stokes",
       arXiv:2608.16915.

Mathematical Architecture:
    1. Constantin-Iyer Representation:
       u(x,t) = P E[ J_t(x)^T u_0(A_t(x)) ]
       omega(x,t) = E[ J_t(x)^{-T} omega_0(A_t(x)) ]
       where dX_t = u(X_t, t) dt + sqrt(2 nu) dW_t, X_t(A_t(x)) = x, J_t = grad A_t.

    2. Exact Closed Decomposition (arXiv:2608.16915):
       u = P( M^T N + R )
       M(x,t) = E[J_t(x)], N(x,t) = E[u_0(A_t(x))]
       R(x,t) = E[ (J - M)^T (V - N) ]
       Q(x,t) = E[ J^T J ] - M^T M  (Deformation Covariance Tensor).

    3. Navier-Stokes Scaling Dimensions:
       [x] ~ L, [t] ~ L^2, [u] ~ L T^(-1) ~ L^(-1)
       [J] ~ 1 (Dimensionless)
       [M] ~ 1 (Dimensionless)
       [N] ~ L^(-1) (Scales as velocity)
       [Q] ~ 1 (Scale-Critical / Dimensionless)
       [R] ~ L^(-1) (Scales as velocity)
       ||R||_{L^3(R^3)} ~ 1 (Scale-Critical / Dimensionless)
       ||Q||_{L^infty(R^3)} ~ 1 (Scale-Critical / Dimensionless).

    4. Regularity Barrier Translation:
       ||u||_{L^3} <= ||P(M^T N)||_{L^3} + ||P R||_{L^3} <= ||M||_{L^infty} ||u_0||_{L^3} + C ||R||_{L^3}.
       The non-covariance part is bounded by initial data. Singularity requires divergence of ||Q||_{L^infty} or ||R||_{L^3}.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class StochasticWeberScalingEntry:
    """Navier-Stokes scaling classification for stochastic Weber variables."""
    variable_name: str
    mathematical_symbol: str
    scaling_exponent_lambda: int      # u_lambda(x,t) = lambda^a u(lambda x, lambda^2 t)
    physical_dimension: str
    critical_functional_space: str
    is_scale_invariant: bool


@dataclass
class RegularityBarrierTranslationResult:
    """Translation of classical regularity criteria into stochastic Weber covariance variables."""
    criterion_name: str
    classical_formulation: str
    stochastic_weber_formulation: str
    is_equivalent_barrier: bool
    controlling_variable: str


@dataclass
class LimitingFlowWeberProfile:
    """Stochastic Weber covariance properties of core limiting flows (Townsend/Burgers)."""
    flow_name: str
    mean_deformation_behavior: str
    covariance_tensor_Q_behavior: str
    correlation_R_behavior: str
    is_stationary_or_linearly_growing: bool


def generate_stochastic_weber_scaling_table() -> List[StochasticWeberScalingEntry]:
    """Generate exact scaling table for Constantin-Iyer / Weber decomposition variables."""
    return [
        StochasticWeberScalingEntry(
            variable_name="Stochastic Jacobian",
            mathematical_symbol="J_t = grad A_t",
            scaling_exponent_lambda=0,
            physical_dimension="Dimensionless [1]",
            critical_functional_space="L^infty_t L^infty_x",
            is_scale_invariant=True,
        ),
        StochasticWeberScalingEntry(
            variable_name="Mean Deformation Matrix",
            mathematical_symbol="M = E[J_t]",
            scaling_exponent_lambda=0,
            physical_dimension="Dimensionless [1]",
            critical_functional_space="L^infty_t L^infty_x",
            is_scale_invariant=True,
        ),
        StochasticWeberScalingEntry(
            variable_name="Transported Velocity Mean",
            mathematical_symbol="N = E[u_0(A_t)]",
            scaling_exponent_lambda=1,
            physical_dimension="Velocity [L T^(-1)]",
            critical_functional_space="L^infty_t L^3_x",
            is_scale_invariant=True, # L^3 norm is scale invariant
        ),
        StochasticWeberScalingEntry(
            variable_name="Deformation Covariance Tensor",
            mathematical_symbol="Q = E[J^T J] - M^T M",
            scaling_exponent_lambda=0,
            physical_dimension="Dimensionless [1]",
            critical_functional_space="L^infty_t L^infty_x",
            is_scale_invariant=True,
        ),
        StochasticWeberScalingEntry(
            variable_name="Deformation-Velocity Correlation Field",
            mathematical_symbol="R = E[(J-M)^T (V-N)]",
            scaling_exponent_lambda=1,
            physical_dimension="Velocity [L T^(-1)]",
            critical_functional_space="L^infty_t L^3_x",
            is_scale_invariant=True,
        ),
    ]


def translate_regularity_criteria_to_weber() -> List[RegularityBarrierTranslationResult]:
    """Translate classical criteria (L^3, Serrin, Koch-Tataru) into stochastic Weber system."""
    return [
        RegularityBarrierTranslationResult(
            criterion_name="Escauriaza-Seregin-Sverak (2003)",
            classical_formulation="u in L^infty_t L^3_x(R^3)",
            stochastic_weber_formulation="||R(.,t)||_{L^3} < infty and ||M(.,t)||_{L^infty} < infty (since ||N||_{L^3} <= ||u_0||_{L^3})",
            is_equivalent_barrier=True,
            controlling_variable="Deformation-Velocity Correlation R",
        ),
        RegularityBarrierTranslationResult(
            criterion_name="Serrin Class L^p_t L^q_x (2/p + 3/q = 1)",
            classical_formulation="int_{-T}^0 ||u(t)||_{L^q}^p dt < infty",
            stochastic_weber_formulation="int_{-T}^0 (||M||_{L^infty} ||u_0||_{L^q} + ||R(t)||_{L^q})^p dt < infty",
            is_equivalent_barrier=True,
            controlling_variable="Serrin Integral of R",
        ),
        RegularityBarrierTranslationResult(
            criterion_name="Koch-Tataru (2001) BMO^{-1}",
            classical_formulation="sup_{t,r} r^{-3} int_{Q_r} |u|^2 dx dt < epsilon_0",
            stochastic_weber_formulation="sup_{t,r} r^{-3} int_{Q_r} (|M^T N|^2 + |R|^2) dx dt < epsilon_0",
            is_equivalent_barrier=True,
            controlling_variable="Local Parabolic Energy of R and M^T N",
        ),
    ]


def compute_limiting_flow_weber_profiles() -> List[LimitingFlowWeberProfile]:
    """Compute stochastic Weber covariance properties of Townsend sheets and Burgers tubes."""
    return [
        LimitingFlowWeberProfile(
            flow_name="Townsend Strained Shear Sheet",
            mean_deformation_behavior="M_12(t) = -t S_12 (linear growth in shear direction)",
            covariance_tensor_Q_behavior="Q_11(t) = 2 nu t (partial_2 u_1)^2 (linearly growing with viscosity)",
            correlation_R_behavior="R_1(t) decays exponentially under background compression exp(-gamma t)",
            is_stationary_or_linearly_growing=True,
        ),
        LimitingFlowWeberProfile(
            flow_name="Burgers Strained Vortex Tube",
            mean_deformation_behavior="M_rr(t) = exp(gamma t), M_zz(t) = exp(-gamma t) (steady strain drift)",
            covariance_tensor_Q_behavior="Q(t) reaches bounded stationary profile Q_steady < infty balancing strain against diffusion",
            correlation_R_behavior="R(t) is strictly bounded: ||R(t)||_{L^3} <= C ||omega_0||_{L^1}",
            is_stationary_or_linearly_growing=True,
        ),
    ]
