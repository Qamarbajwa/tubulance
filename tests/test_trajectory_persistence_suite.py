"""Unit tests for Program NS-TRAJECTORY-PERSISTENCE-1."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.experimental.trajectory_persistence_math import (
    TrajectoryBudgetComponents,
    MaximizerBoundResult,
    DiffusionFalsificationResult,
    compute_exact_trajectory_budget,
    compute_spatial_maximizer_bound,
    audit_diffusion_falsification_case,
    audit_persistence_vs_intermittency,
)


def test_trajectory_persistence_suite():
    """Verify exact 3-component trajectory budget, maximizer bound, and diffusion falsification."""
    # 1. Exact trajectory budget
    xi = np.array([0.0, 0.0, 1.0])
    S = np.diag([1.0, -1.0, 2.0])
    budget = compute_exact_trajectory_budget(
        xi=xi,
        S=S,
        omega_mag=5.0,
        lap_omega_mag=-2.5,
        grad_xi_norm_sq=0.4,
        nu=0.01,
    )
    assert budget.is_identity_exact is True
    assert np.isclose(budget.stretching_rate, 2.0)
    assert np.isclose(budget.viscous_redistribution_rate, 0.01 * (-2.5) / 5.0)
    assert np.isclose(budget.directional_diffusion_rate, -0.01 * 0.4)
    assert np.isclose(budget.total_log_rate, 2.0 - 0.005 - 0.004)

    # 2. Maximizer bound
    max_res = compute_spatial_maximizer_bound(
        omega_0_max=10.0,
        integrated_lambda3=1.5,
        integrated_dir_diss=0.2,
    )
    assert max_res.is_bound_rigorous is True
    assert np.isclose(max_res.predicted_upper_bound, 10.0 * np.exp(1.3))

    # 3. Diffusion falsification
    diff_case = audit_diffusion_falsification_case()
    assert diff_case.is_stretching_zero_but_vorticity_changing is True
    assert diff_case.stretching_rate == 0.0
    assert diff_case.actual_log_rate != 0.0

    # 4. Persistence vs intermittency
    persist_audit = audit_persistence_vs_intermittency()
    assert persist_audit["case2_coherent_persistence"]["exposure_E"] > persist_audit["case1_intermittent_spike"]["exposure_E"]
    assert persist_audit["case2_coherent_persistence"]["vorticity_amplification"] > 1000.0
