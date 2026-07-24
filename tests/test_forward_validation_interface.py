import numpy as np
import pytest

from forward_validation_interface import (
    ForwardComparisonPoint,
    ForwardState,
    NotYetImplementedForwardSolver,
)
from jhtdb_terminal_benchmark import Config


def test_forward_state_and_comparison_point_shapes_are_fixed():
    state = ForwardState(velocity=np.zeros((3, 4, 4, 4)), time=0.0)
    assert state.controller_state == {}

    point = ForwardComparisonPoint(time=1.0)
    for field_name in (
        "kinetic_energy_evolution",
        "energy_spectrum",
        "nonlinear_transfer",
        "spectral_flux",
        "vorticity_statistics",
        "structure_functions",
        "terminal_heat",
        "backscatter",
        "controller_evolution",
    ):
        assert getattr(point, field_name) is None


def test_not_yet_implemented_solver_raises_on_every_method():
    solver = NotYetImplementedForwardSolver()
    velocity = np.zeros((4, 4, 4, 3))
    cfg = Config()

    with pytest.raises(NotImplementedError):
        solver.initialize(velocity, cfg)

    state = ForwardState(velocity=np.zeros((3, 4, 4, 4)), time=0.0)
    with pytest.raises(NotImplementedError):
        solver.step(state, dt=0.01)

    with pytest.raises(NotImplementedError):
        solver.compare_to_dns(state, velocity)
