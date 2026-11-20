"""Validated simulation configuration for navier3d.

Configuration is expressed as a tree of frozen dataclasses so that a
:class:`SimulationConfig` is always internally consistent once constructed.
Use :meth:`SimulationConfig.from_yaml` to load a configuration file, or
:meth:`SimulationConfig.from_dict` to build one from an in-memory mapping
(e.g. in tests). Both paths run full validation and raise
:class:`ConfigError` with a specific, actionable message on failure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence, Union

import yaml


class ConfigError(ValueError):
    """Raised when a simulation configuration is missing or invalid."""


_ALLOWED_CONVECTION_SCHEMES = {"central", "upwind", "limited"}
_ALLOWED_TIME_INTEGRATORS = {"ab2_cn", "explicit_euler", "implicit_euler"}
_ALLOWED_PRESSURE_SOLVERS = {
    "conjugate_gradient",
    "bicgstab",
    "gmres",
    "direct",
    "pyamg",
}
_ALLOWED_VELOCITY_BC = {
    "periodic",
    "no_slip",
    "free_slip",
    "velocity_inlet",
    "pressure_outlet",
    "symmetry",
}
_ALLOWED_PRESSURE_BC = {"periodic", "neumann", "dirichlet"}
_FACE_NAMES = ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max")
_AXIS_FACE_PAIRS = (("x_min", "x_max"), ("y_min", "y_max"), ("z_min", "z_max"))


@dataclass(frozen=True)
class DomainConfig:
    """Physical extent of the Cartesian domain, in meters."""

    length_x: float
    length_y: float
    length_z: float

    def validate(self) -> None:
        for name in ("length_x", "length_y", "length_z"):
            value = getattr(self, name)
            if not value > 0:
                raise ConfigError(f"domain.{name} must be positive, got {value!r}")


@dataclass(frozen=True)
class MeshConfig:
    """Cell counts and spacing strategy for the structured mesh."""

    nx: int
    ny: int
    nz: int
    spacing: str = "uniform"

    def validate(self) -> None:
        for name in ("nx", "ny", "nz"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ConfigError(f"mesh.{name} must be a positive integer, got {value!r}")
        if self.spacing != "uniform":
            raise ConfigError(
                f"mesh.spacing={self.spacing!r} is not yet supported; only 'uniform' "
                "spacing is implemented in this milestone (nonuniform spacing is a "
                "documented future extension)"
            )


@dataclass(frozen=True)
class FluidConfig:
    """Constant-density Newtonian fluid properties."""

    density: float
    kinematic_viscosity: float

    def validate(self) -> None:
        if not self.density > 0:
            raise ConfigError(f"fluid.density must be positive, got {self.density!r}")
        if not self.kinematic_viscosity > 0:
            raise ConfigError(
                f"fluid.kinematic_viscosity must be positive, got "
                f"{self.kinematic_viscosity!r}"
            )


@dataclass(frozen=True)
class TimeConfig:
    """Time-advancement parameters."""

    dt: float
    end_time: float
    adaptive: bool = True
    cfl_target: float = 0.5
    integrator: str = "ab2_cn"

    def validate(self) -> None:
        if not self.dt > 0:
            raise ConfigError(f"time.dt must be positive, got {self.dt!r}")
        if not self.end_time > 0:
            raise ConfigError(f"time.end_time must be positive, got {self.end_time!r}")
        if not 0.0 < self.cfl_target <= 1.0:
            raise ConfigError(f"time.cfl_target must be in (0, 1], got {self.cfl_target!r}")
        if self.integrator not in _ALLOWED_TIME_INTEGRATORS:
            raise ConfigError(
                f"time.integrator={self.integrator!r} is not recognized; expected one "
                f"of {sorted(_ALLOWED_TIME_INTEGRATORS)}"
            )


@dataclass(frozen=True)
class ConvectionConfig:
    """Choice of convective discretization scheme."""

    scheme: str = "central"

    def validate(self) -> None:
        if self.scheme not in _ALLOWED_CONVECTION_SCHEMES:
            raise ConfigError(
                f"convection.scheme={self.scheme!r} is not recognized; expected one "
                f"of {sorted(_ALLOWED_CONVECTION_SCHEMES)}"
            )


@dataclass(frozen=True)
class PressureConfig:
    """Pressure Poisson solver selection and tolerances."""

    solver: str = "conjugate_gradient"
    tolerance: float = 1.0e-10
    max_iterations: int = 10000

    def validate(self) -> None:
        if self.solver not in _ALLOWED_PRESSURE_SOLVERS:
            raise ConfigError(
                f"pressure.solver={self.solver!r} is not recognized; expected one of "
                f"{sorted(_ALLOWED_PRESSURE_SOLVERS)}"
            )
        if not self.tolerance > 0:
            raise ConfigError(f"pressure.tolerance must be positive, got {self.tolerance!r}")
        if (
            not isinstance(self.max_iterations, int)
            or isinstance(self.max_iterations, bool)
            or self.max_iterations < 1
        ):
            raise ConfigError(
                f"pressure.max_iterations must be a positive integer, got "
                f"{self.max_iterations!r}"
            )


@dataclass(frozen=True)
class FaceBCConfig:
    """Boundary-condition specification for a single domain face.

    ``velocity_value`` is required (and only meaningful) for
    ``velocity="velocity_inlet"``; it is interpreted componentwise as
    ``(u, v, w)``. Because the face-normal component is enforced directly
    and the tangential components are enforced via ghost-cell mirroring,
    ``velocity_inlet`` with a zero normal component doubles as a
    prescribed-velocity moving wall (e.g. a lid-driven-cavity lid).

    ``pressure_value`` is required for ``pressure="dirichlet"``.

    ``pressure_gradient_value`` is optional and only meaningful for
    ``pressure="neumann"``: ``dp/dn`` (outward normal), ``0.0``
    (homogeneous) if unset.
    """

    velocity: str
    pressure: str
    velocity_value: Optional[Sequence[float]] = None
    pressure_value: Optional[float] = None
    pressure_gradient_value: Optional[float] = None

    def validate(self, face_name: str) -> None:
        if self.velocity not in _ALLOWED_VELOCITY_BC:
            raise ConfigError(
                f"boundary_conditions.{face_name}.velocity={self.velocity!r} is not "
                f"recognized; expected one of {sorted(_ALLOWED_VELOCITY_BC)}"
            )
        if self.pressure not in _ALLOWED_PRESSURE_BC:
            raise ConfigError(
                f"boundary_conditions.{face_name}.pressure={self.pressure!r} is not "
                f"recognized; expected one of {sorted(_ALLOWED_PRESSURE_BC)}"
            )
        if self.velocity == "velocity_inlet" and self.velocity_value is None:
            raise ConfigError(
                f"boundary_conditions.{face_name}: velocity='velocity_inlet' requires "
                "velocity_value=[u, v, w]"
            )
        if self.velocity_value is not None and len(tuple(self.velocity_value)) != 3:
            raise ConfigError(
                f"boundary_conditions.{face_name}.velocity_value must have exactly 3 "
                f"components (u, v, w), got {self.velocity_value!r}"
            )
        if self.pressure == "dirichlet" and self.pressure_value is None:
            raise ConfigError(
                f"boundary_conditions.{face_name}: pressure='dirichlet' requires "
                "pressure_value"
            )
        if self.pressure != "neumann" and self.pressure_gradient_value is not None:
            raise ConfigError(
                f"boundary_conditions.{face_name}: pressure_gradient_value is only "
                f"meaningful for pressure='neumann', got pressure={self.pressure!r}"
            )


@dataclass(frozen=True)
class BoundaryConditionsConfig:
    """Boundary conditions for all six faces of the domain."""

    x_min: FaceBCConfig
    x_max: FaceBCConfig
    y_min: FaceBCConfig
    y_max: FaceBCConfig
    z_min: FaceBCConfig
    z_max: FaceBCConfig

    def validate(self) -> None:
        for name in _FACE_NAMES:
            getattr(self, name).validate(name)
        for lo_name, hi_name in _AXIS_FACE_PAIRS:
            lo_periodic = getattr(self, lo_name).velocity == "periodic"
            hi_periodic = getattr(self, hi_name).velocity == "periodic"
            if lo_periodic != hi_periodic:
                raise ConfigError(
                    f"periodic boundary conditions must be specified on both "
                    f"{lo_name} and {hi_name} together; got "
                    f"velocity={getattr(self, lo_name).velocity!r} on {lo_name} and "
                    f"velocity={getattr(self, hi_name).velocity!r} on {hi_name}"
                )


@dataclass(frozen=True)
class SimulationConfig:
    """Top-level, fully validated simulation configuration."""

    domain: DomainConfig
    mesh: MeshConfig
    fluid: FluidConfig
    time: TimeConfig
    boundary_conditions: BoundaryConditionsConfig
    convection: ConvectionConfig = field(default_factory=ConvectionConfig)
    pressure: PressureConfig = field(default_factory=PressureConfig)

    def validate(self) -> None:
        self.domain.validate()
        self.mesh.validate()
        self.fluid.validate()
        self.time.validate()
        self.convection.validate()
        self.pressure.validate()
        self.boundary_conditions.validate()

    @classmethod
    def from_dict(cls, raw: dict) -> "SimulationConfig":
        """Build and validate a :class:`SimulationConfig` from a plain mapping."""
        try:
            domain = DomainConfig(**raw["domain"])
            mesh = MeshConfig(**raw["mesh"])
            fluid = FluidConfig(**raw["fluid"])
            time_cfg = TimeConfig(**raw["time"])
            convection = ConvectionConfig(**raw.get("convection", {}))
            pressure = PressureConfig(**raw.get("pressure", {}))
            bc_raw = raw["boundary_conditions"]
            boundary_conditions = BoundaryConditionsConfig(
                **{name: FaceBCConfig(**bc_raw[name]) for name in _FACE_NAMES}
            )
        except KeyError as exc:
            raise ConfigError(f"missing required configuration section/key: {exc}") from exc
        except TypeError as exc:
            raise ConfigError(f"invalid configuration field: {exc}") from exc

        config = cls(
            domain=domain,
            mesh=mesh,
            fluid=fluid,
            time=time_cfg,
            boundary_conditions=boundary_conditions,
            convection=convection,
            pressure=pressure,
        )
        config.validate()
        return config

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "SimulationConfig":
        """Load and validate a :class:`SimulationConfig` from a YAML file."""
        path = Path(path)
        if not path.is_file():
            raise ConfigError(f"configuration file not found: {path}")
        with path.open("r") as fh:
            raw = yaml.safe_load(fh)
        if not isinstance(raw, dict):
            raise ConfigError(f"configuration file {path} did not parse to a mapping")
        return cls.from_dict(raw)
