import numpy as np
import pytest

from forcing import ForcingState
from material_state import get_material, MaterialNotImplementedError
from pseudo_spectral_solver import (
    SolverConfig, SolverConfigError, run_solver, stable_dt_estimate, SyntheticForwardSolver,
)
from backscatter_placement import DIAGNOSTIC_ONLY

NEWTONIAN = get_material("incompressible_newtonian_liquid")


def _cfg(**overrides):
    force = overrides.pop("forcing", ForcingState(power_input=0.05, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random"))
    defaults = dict(grid_n=16, domain_length=2 * np.pi, viscosity=0.05, forcing=force, material=NEWTONIAN, dt=0.01, seed=0)
    defaults.update(overrides)
    return SolverConfig(**defaults)


def test_solver_config_rejects_unimplemented_material():
    bad_material = get_material("low_mach_newtonian_gas")
    with pytest.raises(MaterialNotImplementedError):
        _cfg(material=bad_material)


def test_solver_config_rejects_diagnostic_only_placement():
    with pytest.raises(SolverConfigError):
        _cfg(backscatter_placement="dns_oracle_diagnostic")
    assert "dns_oracle_diagnostic" in DIAGNOSTIC_ONLY


def test_solver_config_rejects_bad_grid_or_dt():
    with pytest.raises(SolverConfigError):
        _cfg(grid_n=2)
    with pytest.raises(SolverConfigError):
        _cfg(dt=0.0)
    with pytest.raises(SolverConfigError):
        _cfg(viscosity=0.0)


def test_stable_dt_estimate_is_positive():
    dt = stable_dt_estimate(grid_n=16, domain_length=2 * np.pi, viscosity=0.05, u_rms=1.0)
    assert dt > 0


def test_run_produces_finite_trajectory():
    cfg = _cfg(dt=0.006)
    state, samples, layer = run_solver(cfg, 15)
    ke = np.array([s.kinetic_energy for s in samples])
    assert np.all(np.isfinite(ke))
    assert np.all(ke >= 0)


def test_energy_budget_closes_reasonably_for_unforced_decay():
    """No forcing (power_input=0), no terminal operator -- pure viscous
    decay. dK/dt should closely match -viscous_dissipation (residual small
    relative to the viscous rate)."""
    zero_force = ForcingState(power_input=0.0, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    cfg = _cfg(forcing=zero_force, apply_terminal_operator=False, use_controller=False, dt=0.005)
    state, samples, layer = run_solver(cfg, 20)
    for s in samples[2:]:  # skip first couple of transient steps
        if s.viscous_dissipation > 1e-8:
            assert abs(s.unresolved_residual) < 0.5 * s.viscous_dissipation * cfg.dt + 1e-10


def test_forcing_power_tracks_target_on_average():
    target = 0.05
    force = ForcingState(power_input=target, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    cfg = _cfg(forcing=force, dt=0.008)
    state, samples, layer = run_solver(cfg, 30)
    tail = [s.power_input for s in samples[10:]]
    assert np.mean(tail) == pytest.approx(target, rel=0.5)  # loose: amplitude clip can bite early on


def test_hard_cutoff_group_zeros_energy_above_kc():
    force = ForcingState(power_input=1.0, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    cfg = _cfg(forcing=force, apply_terminal_operator=False, hard_cutoff=True, use_controller=False, c_gamma_fixed=0.0, dt=0.006)
    state, samples, layer = run_solver(cfg, 15)
    assert samples[-1].energy_above_cutoff == pytest.approx(0.0, abs=1e-12)


def test_h1_weak_forcing_candidate_and_baseline_nearly_identical():
    """H1 at the solver level: under very weak forcing (Phi_l << 1 by
    construction: tiny power relative to injection scale), the candidate
    forcing-aware operator and the baseline operator should produce
    near-identical kinetic-energy trajectories."""
    weak_force = ForcingState(power_input=1e-5, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    cfg_base = _cfg(forcing=weak_force, terminal_gamma_mode="baseline", dt=0.006, seed=1)
    cfg_cand = _cfg(forcing=weak_force, terminal_gamma_mode="candidate_forcing_aware", dt=0.006, seed=1)
    _s1, samples_base, _l1 = run_solver(cfg_base, 15)
    _s2, samples_cand, _l2 = run_solver(cfg_cand, 15)
    ke_base = np.array([s.kinetic_energy for s in samples_base])
    ke_cand = np.array([s.kinetic_energy for s in samples_cand])
    np.testing.assert_allclose(ke_base, ke_cand, rtol=1e-6, atol=1e-12)


def test_forward_solver_adapter_initialize_and_step():
    force = ForcingState(power_input=0.02, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    cfg = _cfg(forcing=force, dt=0.006)
    solver = SyntheticForwardSolver(cfg)
    state0 = solver.initialize()
    assert state0.velocity.shape == (3, 16, 16, 16)
    assert state0.time == pytest.approx(0.0)
    state1 = solver.step(state0, cfg.dt)
    assert state1.time == pytest.approx(cfg.dt)
    assert "c_gamma" in state1.controller_state


def test_forward_solver_adapter_never_compares_to_real_dns():
    force = ForcingState(power_input=0.02, injection_wavenumber=3.0, timescale=1.0, forcing_type="isotropic_random")
    cfg = _cfg(forcing=force)
    solver = SyntheticForwardSolver(cfg)
    state0 = solver.initialize()
    with pytest.raises(NotImplementedError):
        solver.compare_to_dns(state0, dns_snapshot=None)


@pytest.mark.parametrize("forcing_type,kwargs", [
    ("isotropic_random", {}),
    ("fixed_direction", {"direction": (1.0, 0.0, 0.0)}),
    ("rotating_direction", {"direction": (0.0, 1.0, 0.0)}),
    ("periodic", {}),
    ("pulsed", {}),
    ("impulsive", {}),
    ("narrow_band", {}),
    ("broad_band", {}),
    ("small_scale", {}),
])
def test_every_single_scale_forcing_type_runs_without_error(forcing_type, kwargs):
    force = ForcingState(power_input=0.02, injection_wavenumber=3.0, timescale=0.5, forcing_type=forcing_type, **kwargs)
    cfg = _cfg(forcing=force, dt=0.006)
    state, samples, layer = run_solver(cfg, 6)
    assert np.isfinite(samples[-1].kinetic_energy)


def test_multi_scale_forcing_runs():
    force = ForcingState(power_input=0.02, injection_wavenumber=2.0, timescale=1.0, forcing_type="multi_scale", extra_wavenumbers=(5.0,))
    cfg = _cfg(forcing=force, dt=0.006)
    state, samples, layer = run_solver(cfg, 6)
    assert np.isfinite(samples[-1].kinetic_energy)
