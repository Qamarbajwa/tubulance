import numpy as np
import pytest

from controller import ControllerConfig, ControllerState, controller_step, controller_diagnostics, DEFAULT_GP, DEFAULT_GI


def test_default_gains_match_preregistered_baseline():
    cfg = ControllerConfig()
    assert cfg.gp == DEFAULT_GP == 24.0
    assert cfg.gi == DEFAULT_GI == 8.0


def test_controller_config_rejects_invalid_bounds():
    with pytest.raises(ValueError):
        ControllerConfig(c_gamma_min=1.0, c_gamma_max=1.0)
    with pytest.raises(ValueError):
        ControllerConfig(gp=-1.0)


def test_controller_step_drives_toward_zero_error_when_matched():
    cfg = ControllerConfig(gp=1.0, gi=0.1, c_gamma_max=100.0)
    state = ControllerState(c_gamma=1.0)
    # target == measured => zero error, c_gamma should not move
    state2 = controller_step(state, cfg, target_power=1.0, measured_power=1.0, dt=0.1)
    assert state2.c_gamma == pytest.approx(1.0)


def test_controller_step_increases_c_gamma_when_removal_too_low():
    cfg = ControllerConfig(gp=1.0, gi=0.0, c_gamma_max=100.0)
    state = ControllerState(c_gamma=1.0)
    # target_power (injected) > measured_power (removed) => positive error => c_gamma should rise
    state2 = controller_step(state, cfg, target_power=1.0, measured_power=0.2, dt=0.1)
    assert state2.c_gamma > 1.0


def test_controller_clips_to_bounds():
    cfg = ControllerConfig(gp=1000.0, gi=0.0, c_gamma_min=0.0, c_gamma_max=5.0)
    state = ControllerState(c_gamma=1.0)
    state2 = controller_step(state, cfg, target_power=100.0, measured_power=0.0, dt=1.0)
    assert state2.c_gamma == pytest.approx(5.0)


def test_controller_diagnostics_on_converging_trajectory():
    cfg = ControllerConfig(gp=2.0, gi=0.5, c_gamma_max=1000.0)
    state = ControllerState(c_gamma=1.0)
    for _ in range(200):
        state = controller_step(state, cfg, target_power=1.0, measured_power=state.c_gamma * 0.5, dt=0.01)
    diag = controller_diagnostics(state)
    assert diag["is_stable"] is True
    assert diag["n_steps"] == 200
    assert diag["settling_time_steps"] is not None


def test_controller_diagnostics_empty_history():
    diag = controller_diagnostics(ControllerState(c_gamma=1.0))
    assert diag["n_steps"] == 0
    assert diag["is_stable"] is True
