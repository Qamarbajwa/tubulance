"""Boundary-condition specification and ghost-cell enforcement.

Two independent things live here:

1. A typed, validated representation of "what BC applies on each of the
   six domain faces" (:class:`FaceBoundaryCondition`, :class:`BoundaryConditionSet`).
2. Functions that use that representation to fill the ghost-cell layers of
   :class:`~navier3d.fields.ScalarField` / :class:`~navier3d.fields.FaceField`
   arrays in place.

Corner/edge convention
-----------------------
Ghost cells are filled with a fixed sequential sweep over axes (x, then y,
then z). Where ghost regions from two or three axes overlap (edges and
corners of the padded array), the value therefore comes from whichever
axis was swept last (z), applied to data that already includes the
previous sweeps' ghost values. This is deterministic and is the standard
convention in staggered-grid codes; no Milestone 1 functionality reads
corner/edge ghost values, so exact corner physics is not addressed here.

Normal vs. tangential ghost formulas
-------------------------------------
A velocity component's own face-normal axis and its two tangential axes
need *different* ghost formulas, because a MAC grid stores the normal
component exactly on the boundary face but the tangential components half
a cell away from it:

* **Face-normal component, boundary face itself** (a real unknown, not a
  ghost cell -- see ``docs/architecture.md`` for the index-range table):
  assigned directly (Dirichlet).
  ``no_slip`` / ``free_slip`` / ``symmetry`` -> 0 (impermeable wall).
  ``velocity_inlet`` -> the configured normal component.
  ``pressure_outlet`` -> zero-gradient extrapolation from the adjacent cell.
  ``periodic`` -> the two boundary faces are the same physical location and
  are averaged together.

* **Face-normal component, ghost layers beyond the boundary face** (added
  for future one-sided stencils; not yet exercised by any Milestone 1
  functionality): filled by *reflection about the boundary node* (the
  node itself, not a half-cell wall, since the boundary face is an exact
  grid point here): Dirichlet-type BCs use ``ghost = 2*V - mirror``,
  zero-gradient (``pressure_outlet``) uses ``ghost = mirror``, and
  ``periodic`` wraps around the domain skipping the duplicated boundary
  point.

* **Tangential component ghost** (a true ghost cell; the wall lies
  halfway between it and the first interior cell):
  ``no_slip`` (stationary wall) -> ``ghost = -interior``.
  ``velocity_inlet`` with tangential wall speed ``U_w`` (this is also how
  a *moving* wall, e.g. a lid-driven-cavity lid, is specified: a
  zero-normal-component velocity_inlet) -> ``ghost = 2*U_w - interior``.
  ``free_slip`` / ``symmetry`` / ``pressure_outlet`` -> ``ghost = interior``
  (zero-gradient / zero shear).

* **Pressure ghost** (always a true ghost on all axes; pressure has no
  boundary-coincident points on a MAC grid):
  ``neumann`` -> ``ghost = interior`` when ``pressure_gradient_value`` is
  unset (the **homogeneous** zero-gradient case, ``dp/dn = 0``); when set,
  ``ghost(k) = interior(k) + (2k+1)*d*g`` where ``g = dp/dn`` (outward
  normal) and ``d`` is the grid spacing along that axis -- the ``k=0``
  case (the only one read by any Milestone 1/2 operator) is the standard
  second-order ghost-node formula derived from a central difference
  straddling the wall; ``k>0`` extends it assuming a locally linear
  profile (only exercised if ``n_ghost>1`` is used with an inhomogeneous
  gradient, which nothing in this package currently does). Deriving the
  *value* of ``g`` for a given projection step
  (``dp/dn = (rho/dt) * (u_n* - u_n_required)``) is Milestone 4 work
  (``projection.py``); this module only *applies* a given ``g``, homogeneous
  by default.
  ``dirichlet`` -> ``ghost = 2*value - interior`` (linear extrapolation to
  the prescribed face value).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple, Union

import numpy as np

from ._indexing import axis_index as _idx
from ._indexing import axis_slice as _slc
from .fields import FaceField, FlowState, ScalarField, VelocityField

if TYPE_CHECKING:
    from .config import BoundaryConditionsConfig


class BoundaryConditionError(ValueError):
    """Raised when a boundary-condition specification is invalid or inconsistent."""


class VelocityBCType(str, Enum):
    PERIODIC = "periodic"
    NO_SLIP = "no_slip"
    FREE_SLIP = "free_slip"
    VELOCITY_INLET = "velocity_inlet"
    PRESSURE_OUTLET = "pressure_outlet"
    SYMMETRY = "symmetry"


class PressureBCType(str, Enum):
    PERIODIC = "periodic"
    NEUMANN = "neumann"
    DIRICHLET = "dirichlet"


# Each velocity BC implies a physically-consistent set of allowed pressure
# BCs. This is enforced at construction time so inconsistent configurations
# (e.g. a no-slip wall with a Dirichlet pressure) fail immediately rather
# than producing a subtly ill-posed Poisson problem later.
_COMPATIBLE_PRESSURE_BC = {
    VelocityBCType.PERIODIC: {PressureBCType.PERIODIC},
    VelocityBCType.NO_SLIP: {PressureBCType.NEUMANN},
    VelocityBCType.FREE_SLIP: {PressureBCType.NEUMANN},
    VelocityBCType.SYMMETRY: {PressureBCType.NEUMANN},
    VelocityBCType.VELOCITY_INLET: {PressureBCType.NEUMANN},
    VelocityBCType.PRESSURE_OUTLET: {PressureBCType.DIRICHLET},
}

_FACE_NAMES = ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max")
_AXIS_FACE_PAIRS = (("x_min", "x_max"), ("y_min", "y_max"), ("z_min", "z_max"))
_AXIS_FACES = {0: ("x_min", "x_max"), 1: ("y_min", "y_max"), 2: ("z_min", "z_max")}


@dataclass(frozen=True, eq=False)
class FaceBoundaryCondition:
    """The velocity and pressure boundary condition for a single domain face.

    ``pressure_gradient_value`` is only meaningful when ``pressure_type``
    is ``neumann``: it is ``dp/dn`` (outward normal), defaulting to
    ``0.0`` (homogeneous) when unset. It may be a single scalar (uniform
    over the whole face) **or** a 2-D ``numpy`` array giving a spatially
    varying value across the face's two tangential axes -- needed by
    Milestone 4's projection step, which derives ``dp/dn`` from a
    generally non-uniform predictor velocity
    (``docs/architecture.md`` Section 10). An array may be given at either
    the tangential axes' full ghost-padded shape (as returned by
    ``FaceField.boundary_layer``, directly usable by
    ``apply_pressure_bc``) or their interior-only shape (as
    ``pressure.py``'s matrix assembly needs); both are accepted and
    auto-detected where shape matters.

    ``eq=False``: instances compare by identity, not by value. The
    default dataclass-generated ``__eq__``/``__hash__`` would attempt to
    compare/hash the ``pressure_gradient_value`` field, which raises
    (numpy arrays have no scalar truth value and are unhashable) as soon
    as an array-valued gradient is used; nothing in this codebase relies
    on value-equality for this class.
    """

    velocity_type: VelocityBCType
    pressure_type: PressureBCType
    velocity_value: Optional[Tuple[float, float, float]] = None
    pressure_value: Optional[float] = None
    pressure_gradient_value: Optional[Union[float, np.ndarray]] = None

    def __post_init__(self) -> None:
        allowed = _COMPATIBLE_PRESSURE_BC[self.velocity_type]
        if self.pressure_type not in allowed:
            raise BoundaryConditionError(
                f"velocity BC {self.velocity_type.value!r} is not compatible with "
                f"pressure BC {self.pressure_type.value!r}; expected one of "
                f"{sorted(t.value for t in allowed)}"
            )
        if self.velocity_type is VelocityBCType.VELOCITY_INLET and self.velocity_value is None:
            raise BoundaryConditionError("velocity_inlet requires velocity_value=(u, v, w)")
        if self.pressure_type is PressureBCType.DIRICHLET and self.pressure_value is None:
            raise BoundaryConditionError("dirichlet pressure BC requires pressure_value")
        if self.pressure_type is not PressureBCType.NEUMANN and self.pressure_gradient_value is not None:
            raise BoundaryConditionError(
                f"pressure_gradient_value is only meaningful for pressure_type='neumann', "
                f"got pressure_type={self.pressure_type.value!r}"
            )

    @property
    def pressure_gradient(self) -> Union[float, np.ndarray]:
        """``dp/dn`` (outward normal), ``0.0`` if unset."""
        return self.pressure_gradient_value if self.pressure_gradient_value is not None else 0.0


@dataclass(frozen=True)
class BoundaryConditionSet:
    """Boundary conditions for all six faces of the domain, mutually validated."""

    x_min: FaceBoundaryCondition
    x_max: FaceBoundaryCondition
    y_min: FaceBoundaryCondition
    y_max: FaceBoundaryCondition
    z_min: FaceBoundaryCondition
    z_max: FaceBoundaryCondition

    def __post_init__(self) -> None:
        for lo_name, hi_name in _AXIS_FACE_PAIRS:
            lo_periodic = self[lo_name].velocity_type is VelocityBCType.PERIODIC
            hi_periodic = self[hi_name].velocity_type is VelocityBCType.PERIODIC
            if lo_periodic != hi_periodic:
                raise BoundaryConditionError(
                    f"periodic boundary conditions must be specified on both "
                    f"{lo_name} and {hi_name} together; got "
                    f"{self[lo_name].velocity_type.value!r} and "
                    f"{self[hi_name].velocity_type.value!r}"
                )

    def __getitem__(self, face_name: str) -> FaceBoundaryCondition:
        if face_name not in _FACE_NAMES:
            raise KeyError(face_name)
        return getattr(self, face_name)

    def is_periodic_axis(self, axis: int) -> bool:
        lo_name = _AXIS_FACES[axis][0]
        return self[lo_name].velocity_type is VelocityBCType.PERIODIC

    @classmethod
    def from_config(cls, bc_config: "BoundaryConditionsConfig") -> "BoundaryConditionSet":
        """Build a validated :class:`BoundaryConditionSet` from a config section."""
        kwargs = {}
        for name in _FACE_NAMES:
            face_cfg = getattr(bc_config, name)
            velocity_value = (
                tuple(float(v) for v in face_cfg.velocity_value)
                if face_cfg.velocity_value is not None
                else None
            )
            kwargs[name] = FaceBoundaryCondition(
                velocity_type=VelocityBCType(face_cfg.velocity),
                pressure_type=PressureBCType(face_cfg.pressure),
                velocity_value=velocity_value,
                pressure_value=face_cfg.pressure_value,
                pressure_gradient_value=getattr(face_cfg, "pressure_gradient_value", None),
            )
        return cls(**kwargs)


def periodic_bcs() -> BoundaryConditionSet:
    """Helper returning a fully periodic BoundaryConditionSet on all 6 faces."""
    p_bc = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p_bc, x_max=p_bc, y_min=p_bc, y_max=p_bc, z_min=p_bc, z_max=p_bc)


# --------------------------------------------------------------------------
# Pressure (cell-centered, ghost-padded on every axis, no duplicated points)
# --------------------------------------------------------------------------

def _fill_periodic_ghosts_cell_like(data: np.ndarray, axis: int, ng: int) -> None:
    """Periodic wrap for arrays with no duplicated boundary point (pressure on
    any axis; a velocity component's tangential axes)."""
    n = data.shape[axis]
    data[_slc(axis, slice(0, ng))] = data[_slc(axis, slice(n - 2 * ng, n - ng))]
    data[_slc(axis, slice(n - ng, n))] = data[_slc(axis, slice(ng, 2 * ng))]


def apply_pressure_bc(pressure: ScalarField, bcs: BoundaryConditionSet, spacing: Optional[Tuple[float, float, float]] = None) -> None:
    """Fill the ghost cells of a cell-centered pressure field in place.

    ``spacing`` (``(dx, dy, dz)``) is only required if any face uses an
    **inhomogeneous** Neumann ``pressure_gradient_value``; homogeneous
    Neumann (the default, ``dp/dn=0``), Dirichlet, and periodic faces
    don't need it, so it may be omitted (``None``) unless an inhomogeneous
    gradient is configured, in which case omitting it raises ``ValueError``.
    """
    data = pressure.data
    ng = pressure.n_ghost
    for axis, (lo_name, hi_name) in enumerate((("x_min", "x_max"), ("y_min", "y_max"), ("z_min", "z_max"))):
        lo_bc, hi_bc = bcs[lo_name], bcs[hi_name]
        if lo_bc.pressure_type is PressureBCType.PERIODIC:
            _fill_periodic_ghosts_cell_like(data, axis, ng)
            continue
        n = data.shape[axis]
        d = spacing[axis] if spacing is not None else None
        for k in range(ng):
            g = ng - 1 - k
            interior = ng + k
            lo_interior = data[_idx(axis, interior)]
            if lo_bc.pressure_type is PressureBCType.NEUMANN:
                if lo_bc.pressure_gradient_value is not None:
                    if d is None:
                        raise ValueError(f"{lo_name}: inhomogeneous Neumann requires `spacing`")
                    data[_idx(axis, g)] = lo_interior + (2 * k + 1) * d * lo_bc.pressure_gradient_value
                else:
                    data[_idx(axis, g)] = lo_interior
            else:
                data[_idx(axis, g)] = 2.0 * lo_bc.pressure_value - lo_interior

            hg = n - ng + k
            h_interior = n - ng - 1 - k
            hi_interior = data[_idx(axis, h_interior)]
            if hi_bc.pressure_type is PressureBCType.NEUMANN:
                if hi_bc.pressure_gradient_value is not None:
                    if d is None:
                        raise ValueError(f"{hi_name}: inhomogeneous Neumann requires `spacing`")
                    data[_idx(axis, hg)] = hi_interior + (2 * k + 1) * d * hi_bc.pressure_gradient_value
                else:
                    data[_idx(axis, hg)] = hi_interior
            else:
                data[_idx(axis, hg)] = 2.0 * hi_bc.pressure_value - hi_interior


# --------------------------------------------------------------------------
# Velocity: face-normal axis (boundary-coincident point + node-reflection ghosts)
# --------------------------------------------------------------------------

def _fill_periodic_ghosts_face_like(data: np.ndarray, axis: int, ng: int) -> None:
    """Periodic wrap for a velocity component's own normal axis, where index
    ``ng`` and index ``n-ng-1`` are the *same* physical boundary point.

    Ghosts must skip that duplicated point, which shifts the source slice
    by one relative to :func:`_fill_periodic_ghosts_cell_like`.
    """
    n = data.shape[axis]
    lo_b = ng
    hi_b = n - ng - 1
    data[_slc(axis, slice(0, ng))] = data[_slc(axis, slice(hi_b - ng, hi_b))]
    data[_slc(axis, slice(n - ng, n))] = data[_slc(axis, slice(lo_b + 1, lo_b + 1 + ng))]


def _normal_boundary_value(bc: FaceBoundaryCondition, component: int, adjacent: np.ndarray) -> np.ndarray:
    if bc.velocity_type is VelocityBCType.PRESSURE_OUTLET:
        return adjacent
    if bc.velocity_type is VelocityBCType.VELOCITY_INLET:
        return bc.velocity_value[component]
    # NO_SLIP, FREE_SLIP, SYMMETRY: impermeable wall.
    return 0.0


def _normal_ghost_value(bc: FaceBoundaryCondition, boundary_value: np.ndarray, mirror_source: np.ndarray) -> np.ndarray:
    if bc.velocity_type is VelocityBCType.PRESSURE_OUTLET:
        return mirror_source  # zero-gradient reflection about the boundary node
    # NO_SLIP, FREE_SLIP, SYMMETRY, VELOCITY_INLET: Dirichlet reflection about the boundary node.
    return 2.0 * boundary_value - mirror_source


def _set_normal_axis_bc(data: np.ndarray, axis: int, ng: int, component: int, lo_bc: FaceBoundaryCondition, hi_bc: FaceBoundaryCondition) -> None:
    n = data.shape[axis]
    lo_b, hi_b = ng, n - ng - 1

    if lo_bc.velocity_type is VelocityBCType.PERIODIC:
        avg = 0.5 * (data[_idx(axis, lo_b)] + data[_idx(axis, hi_b)])
        data[_idx(axis, lo_b)] = avg
        data[_idx(axis, hi_b)] = avg
        _fill_periodic_ghosts_face_like(data, axis, ng)
        return

    # Boundary faces: real unknowns, assigned directly (Dirichlet or zero-gradient outflow).
    data[_idx(axis, lo_b)] = _normal_boundary_value(lo_bc, component, data[_idx(axis, lo_b + 1)])
    data[_idx(axis, hi_b)] = _normal_boundary_value(hi_bc, component, data[_idx(axis, hi_b - 1)])

    # Ghost layers beyond the boundary faces: reflection about the boundary node.
    for k in range(ng):
        g_lo, src_lo = ng - 1 - k, ng + 1 + k
        data[_idx(axis, g_lo)] = _normal_ghost_value(lo_bc, data[_idx(axis, lo_b)], data[_idx(axis, src_lo)])

        g_hi, src_hi = n - ng + k, n - ng - 2 - k
        data[_idx(axis, g_hi)] = _normal_ghost_value(hi_bc, data[_idx(axis, hi_b)], data[_idx(axis, src_hi)])


# --------------------------------------------------------------------------
# Velocity: tangential axes (true ghost cells, wall halfway between them)
# --------------------------------------------------------------------------

def _tangential_ghost_value(bc: FaceBoundaryCondition, component: int, interior: np.ndarray) -> np.ndarray:
    if bc.velocity_type is VelocityBCType.NO_SLIP:
        return -interior
    if bc.velocity_type is VelocityBCType.VELOCITY_INLET:
        return 2.0 * bc.velocity_value[component] - interior
    # FREE_SLIP, SYMMETRY, PRESSURE_OUTLET: zero-gradient mirror.
    return interior


def _fill_tangential_axis_bc(data: np.ndarray, axis: int, ng: int, component: int, lo_bc: FaceBoundaryCondition, hi_bc: FaceBoundaryCondition) -> None:
    if lo_bc.velocity_type is VelocityBCType.PERIODIC:
        _fill_periodic_ghosts_cell_like(data, axis, ng)
        return
    n = data.shape[axis]
    for k in range(ng):
        g = ng - 1 - k
        interior = ng + k
        data[_idx(axis, g)] = _tangential_ghost_value(lo_bc, component, data[_idx(axis, interior)])

        hg = n - ng + k
        h_interior = n - ng - 1 - k
        data[_idx(axis, hg)] = _tangential_ghost_value(hi_bc, component, data[_idx(axis, h_interior)])


def _apply_component_bc(field: FaceField, component: int, bcs: BoundaryConditionSet) -> None:
    data = field.data
    ng = field.n_ghost
    for axis in range(3):
        lo_name, hi_name = _AXIS_FACES[axis]
        lo_bc, hi_bc = bcs[lo_name], bcs[hi_name]
        if axis == field.normal_axis:
            _set_normal_axis_bc(data, axis, ng, component, lo_bc, hi_bc)
        else:
            _fill_tangential_axis_bc(data, axis, ng, component, lo_bc, hi_bc)


def apply_velocity_bc(velocity: VelocityField, bcs: BoundaryConditionSet) -> None:
    """Enforce boundary values / fill ghost cells for all three velocity components in place."""
    _apply_component_bc(velocity.u, 0, bcs)
    _apply_component_bc(velocity.v, 1, bcs)
    _apply_component_bc(velocity.w, 2, bcs)


def apply_boundary_conditions(state: FlowState, bcs: BoundaryConditionSet, spacing: Optional[Tuple[float, float, float]] = None) -> None:
    """Enforce all boundary conditions on a :class:`~navier3d.fields.FlowState` in place.

    ``spacing`` is forwarded to :func:`apply_pressure_bc`; see its docstring.
    """
    apply_velocity_bc(state.velocity, bcs)
    apply_pressure_bc(state.pressure, bcs, spacing=spacing)
