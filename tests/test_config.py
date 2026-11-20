"""Tests for navier3d.config."""
from pathlib import Path

import pytest

from navier3d.config import ConfigError, SimulationConfig


def _bc_face(velocity="periodic", pressure="periodic", **kwargs):
    return dict(velocity=velocity, pressure=pressure, **kwargs)


def _valid_raw() -> dict:
    return {
        "domain": {"length_x": 1.0, "length_y": 2.0, "length_z": 3.0},
        "mesh": {"nx": 8, "ny": 12, "nz": 16},
        "fluid": {"density": 1.2, "kinematic_viscosity": 0.02},
        "time": {"dt": 0.001, "end_time": 1.0, "cfl_target": 0.4, "integrator": "ab2_cn"},
        "convection": {"scheme": "central"},
        "pressure": {"solver": "conjugate_gradient", "tolerance": 1e-9, "max_iterations": 500},
        "boundary_conditions": {
            "x_min": _bc_face(), "x_max": _bc_face(),
            "y_min": _bc_face(), "y_max": _bc_face(),
            "z_min": _bc_face(), "z_max": _bc_face(),
        },
    }


def test_valid_config_parses() -> None:
    config = SimulationConfig.from_dict(_valid_raw())
    assert config.mesh.nx == 8
    assert config.mesh.ny == 12
    assert config.mesh.nz == 16
    assert config.fluid.density == 1.2
    assert config.time.integrator == "ab2_cn"


def test_defaults_apply_when_sections_omitted() -> None:
    raw = _valid_raw()
    del raw["convection"]
    del raw["pressure"]
    config = SimulationConfig.from_dict(raw)
    assert config.convection.scheme == "central"
    assert config.pressure.solver == "conjugate_gradient"


def test_missing_required_section_raises() -> None:
    raw = _valid_raw()
    del raw["fluid"]
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


@pytest.mark.parametrize("nx", [0, -1, 1.5])
def test_invalid_mesh_cell_count_raises(nx) -> None:
    raw = _valid_raw()
    raw["mesh"]["nx"] = nx
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_nonuniform_spacing_not_yet_supported_raises() -> None:
    raw = _valid_raw()
    raw["mesh"]["spacing"] = "nonuniform"
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_invalid_density_raises() -> None:
    raw = _valid_raw()
    raw["fluid"]["density"] = -1.0
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_invalid_cfl_target_raises() -> None:
    raw = _valid_raw()
    raw["time"]["cfl_target"] = 1.5
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_unknown_integrator_raises() -> None:
    raw = _valid_raw()
    raw["time"]["integrator"] = "rk4"
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_unknown_convection_scheme_raises() -> None:
    raw = _valid_raw()
    raw["convection"]["scheme"] = "quick"
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_unknown_pressure_solver_raises() -> None:
    raw = _valid_raw()
    raw["pressure"]["solver"] = "multigrid_v2"
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_velocity_inlet_without_value_raises() -> None:
    raw = _valid_raw()
    raw["boundary_conditions"]["x_min"] = _bc_face(velocity="velocity_inlet", pressure="neumann")
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_velocity_value_wrong_length_raises() -> None:
    raw = _valid_raw()
    raw["boundary_conditions"]["x_min"] = _bc_face(
        velocity="velocity_inlet", pressure="neumann", velocity_value=[1.0, 0.0]
    )
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_dirichlet_pressure_without_value_raises() -> None:
    raw = _valid_raw()
    raw["boundary_conditions"]["x_min"] = _bc_face(velocity="pressure_outlet", pressure="dirichlet")
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_periodic_must_be_paired_on_both_faces() -> None:
    raw = _valid_raw()
    raw["boundary_conditions"]["x_min"] = _bc_face(velocity="periodic", pressure="periodic")
    raw["boundary_conditions"]["x_max"] = _bc_face(velocity="no_slip", pressure="neumann")
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_pressure_gradient_value_on_non_neumann_raises() -> None:
    raw = _valid_raw()
    raw["boundary_conditions"]["x_min"] = _bc_face(
        velocity="pressure_outlet", pressure="dirichlet", pressure_value=0.0, pressure_gradient_value=1.0
    )
    with pytest.raises(ConfigError):
        SimulationConfig.from_dict(raw)


def test_pressure_gradient_value_on_neumann_parses() -> None:
    raw = _valid_raw()
    raw["boundary_conditions"]["x_min"] = _bc_face(velocity="no_slip", pressure="neumann", pressure_gradient_value=2.5)
    raw["boundary_conditions"]["x_max"] = _bc_face(velocity="no_slip", pressure="neumann")
    config = SimulationConfig.from_dict(raw)
    assert config.boundary_conditions.x_min.pressure_gradient_value == 2.5


def test_from_yaml_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        SimulationConfig.from_yaml(tmp_path / "does_not_exist.yaml")


def test_from_yaml_round_trip(tmp_path: Path) -> None:
    import yaml

    raw = _valid_raw()
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(yaml.safe_dump(raw))
    config = SimulationConfig.from_yaml(yaml_path)
    assert config.mesh.nx == 8
    assert config.domain.length_z == 3.0
