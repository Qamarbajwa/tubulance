"""Field containers for the staggered (MAC) grid representation.

Layout
------
Pressure is cell-centered; each velocity component is face-centered on the
faces normal to it. Every field -- pressure and all three velocity
components -- uses the **same** ghost-padding convention: ``n_ghost`` ghost
layers on every side of every axis, including the velocity component's own
face-normal axis. This is a deliberate simplification over only padding
tangential axes: the normal axis also needs ghost data once diffusion,
higher-order convection, periodic wrap, or corner treatment are added
(Milestones 2, 6, 7), and a single padding rule for all fields keeps
indexing uniform and easy to reason about. See ``docs/architecture.md``
for a worked 2x2x2 indexing diagram.

Shapes and index ranges (``nx, ny, nz`` = interior cell counts, ``ng`` =
``n_ghost``)
-------------------------------------------------------------------------
Pressure ``p`` (cell-centered, ``nx*ny*nz`` unknowns):
    shape ``(nx+2*ng, ny+2*ng, nz+2*ng)``.
    Interior (non-ghost) index range along x: ``ng .. ng+nx-1`` (``nx``
    cell centers); analogously for y, z. Cell center ``i`` (0-based within
    the interior) sits at physical coordinate ``(i+0.5)*dx``.

``u`` (x-faces, ``(nx+1)*ny*nz`` unknowns before BC elimination):
    shape ``(nx+1+2*ng, ny+2*ng, nz+2*ng)``.
    Along x (face-normal axis): interior index range ``ng .. ng+nx``
    (``nx+1`` face points, **including both domain-boundary faces**
    exactly). Local interior index ``i`` (0-based, ``i = 0..nx``) sits at
    ``x = i*dx``; ``i=0`` is the ``x_min`` boundary, ``i=nx`` is the
    ``x_max`` boundary -- these are real unknowns assigned directly by the
    boundary condition, not ghost cells. Ghost index ranges:
    ``0 .. ng-1`` (beyond ``x_min``) and ``ng+nx+1 .. nx+2*ng`` (beyond
    ``x_max``); these support one-sided stencils that reach past the
    boundary face (needed starting Milestone 2/6) and are filled by
    node-reflection formulas, not the half-cell wall mirror used
    tangentially. Along y, z (tangential axes): interior index range
    ``ng .. ng+ny-1`` / ``ng .. ng+nz-1``, exactly like pressure, with
    ``ng``-wide ghost layers filled by the half-cell wall mirror (the wall
    sits *between* the ghost cell and the first interior cell here, since
    ``u`` is not stored exactly on tangential boundaries).

``v`` (y-faces) and ``w`` (z-faces) are defined analogously with the roles
of x/normal and the tangential axes permuted.

``FaceField.interior`` and ``ScalarField.interior`` both simply return
``data[ng:-ng, ng:-ng, ng:-ng]`` -- the uniform padding means no
per-axis special-casing is needed to obtain the non-ghost region.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ._indexing import axis_index
from .mesh import StructuredMesh3D


class _GhostPaddedField:
    """Named-accessor mixin shared by :class:`ScalarField` and :class:`FaceField`.

    Both store ``data`` padded by ``n_ghost`` on every side of every axis
    (see module docstring), so the index arithmetic for "the g-th ghost
    layer" or "the interior range" is identical for both and is written
    here once rather than as repeated handwritten ``data[ng:-ng, ...]``
    expressions in operator code.
    """

    data: np.ndarray
    n_ghost: int

    def interior_range(self, axis: int) -> slice:
        """The slice of ``axis`` occupied by interior (non-ghost) values."""
        ng = self.n_ghost
        return slice(ng, self.data.shape[axis] - ng)

    def shifted_range(self, axis: int, offset: int) -> slice:
        """``interior_range(axis)`` translated by ``offset`` cells (positive
        or negative). Combined with ``interior_range`` on the other two
        axes, this builds the neighbor views a central-difference stencil
        needs (e.g. ``offset=+1``/``-1`` for a Laplacian's plus/minus
        neighbor) without hand-writing ``ng+1 : -ng+1``-style arithmetic at
        each call site. Only valid where the shifted range stays within
        ``data``'s allocated bounds, i.e. ``abs(offset) <= n_ghost``."""
        ng = self.n_ghost
        n = self.data.shape[axis]
        return slice(ng + offset, n - ng + offset)

    def first_interior_layer(self, axis: int, side: str) -> np.ndarray:
        """The interior plane immediately adjacent to the ``side`` ghost
        region of ``axis`` (``side`` is ``"lo"`` or ``"hi"``). Returns a view."""
        ng = self.n_ghost
        if side == "lo":
            i = ng
        elif side == "hi":
            i = self.data.shape[axis] - ng - 1
        else:
            raise ValueError(f"side must be 'lo' or 'hi', got {side!r}")
        return self.data[axis_index(axis, i)]

    def ghost_layer(self, axis: int, side: str, g: int = 0) -> np.ndarray:
        """The ``g``-th ghost layer along ``axis`` on ``side`` (``"lo"``/``"hi"``),
        ``g=0`` nearest the interior, ``g=n_ghost-1`` farthest. Returns a
        view spanning the *full* padded width of the other two axes
        (including their own ghosts), so edge/corner ghost cells are
        directly reachable when a caller explicitly needs them; ordinary
        interior-adjacent stencil code should combine this with
        ``interior_range`` on the other axes instead."""
        ng = self.n_ghost
        if not 0 <= g < ng:
            raise ValueError(f"g must be in [0, {ng}), got {g!r}")
        if side == "lo":
            i = ng - 1 - g
        elif side == "hi":
            i = self.data.shape[axis] - ng + g
        else:
            raise ValueError(f"side must be 'lo' or 'hi', got {side!r}")
        return self.data[axis_index(axis, i)]


@dataclass
class ScalarField(_GhostPaddedField):
    """A cell-centered scalar field (e.g. pressure), ghost-padded on all axes."""

    data: np.ndarray
    n_ghost: int

    @classmethod
    def zeros(cls, mesh: StructuredMesh3D) -> "ScalarField":
        ng = mesh.n_ghost
        shape = (mesh.nx + 2 * ng, mesh.ny + 2 * ng, mesh.nz + 2 * ng)
        return cls(data=np.zeros(shape, dtype=np.float64), n_ghost=ng)

    @property
    def interior(self) -> np.ndarray:
        """View of the interior (non-ghost) cells, shape ``(nx, ny, nz)``."""
        ng = self.n_ghost
        return self.data[ng:-ng, ng:-ng, ng:-ng]

    @interior.setter
    def interior(self, value: np.ndarray) -> None:
        ng = self.n_ghost
        self.data[ng:-ng, ng:-ng, ng:-ng] = value


@dataclass
class FaceField(_GhostPaddedField):
    """A face-centered scalar field for one velocity component on the MAC grid.

    Parameters
    ----------
    data : np.ndarray
        Padded storage array (see module docstring for shapes).
    n_ghost : int
        Ghost-cell width, applied uniformly to all three axes.
    normal_axis : int
        ``0``, ``1``, or ``2`` for x-, y-, or z-normal faces respectively.
    """

    data: np.ndarray
    n_ghost: int
    normal_axis: int

    @classmethod
    def zeros(cls, mesh: StructuredMesh3D, normal_axis: int) -> "FaceField":
        if normal_axis not in (0, 1, 2):
            raise ValueError(f"normal_axis must be 0, 1, or 2, got {normal_axis!r}")
        ng = mesh.n_ghost
        shape = [mesh.nx + 2 * ng, mesh.ny + 2 * ng, mesh.nz + 2 * ng]
        n_cells = {0: mesh.nx, 1: mesh.ny, 2: mesh.nz}[normal_axis]
        shape[normal_axis] = (n_cells + 1) + 2 * ng
        return cls(data=np.zeros(tuple(shape), dtype=np.float64), n_ghost=ng, normal_axis=normal_axis)

    @property
    def interior(self) -> np.ndarray:
        """View of the non-ghost region: shape has ``n_cells+1`` along the
        normal axis (both boundary faces included) and ``n_cells`` along
        each tangential axis."""
        ng = self.n_ghost
        return self.data[ng:-ng, ng:-ng, ng:-ng]

    @interior.setter
    def interior(self, value: np.ndarray) -> None:
        ng = self.n_ghost
        self.data[ng:-ng, ng:-ng, ng:-ng] = value

    def boundary_layer(self, side: str) -> np.ndarray:
        """The exact domain-boundary plane along this field's own
        face-normal axis (a real unknown, not a ghost cell -- see module
        docstring). ``side`` is ``"lo"`` (``x_min``-type face) or
        ``"hi"`` (``x_max``-type face). Returns a view."""
        return self.first_interior_layer(self.normal_axis, side)


@dataclass
class VelocityField:
    """The three MAC-grid velocity components."""

    u: FaceField
    v: FaceField
    w: FaceField

    @classmethod
    def zeros(cls, mesh: StructuredMesh3D) -> "VelocityField":
        return cls(
            u=FaceField.zeros(mesh, normal_axis=0),
            v=FaceField.zeros(mesh, normal_axis=1),
            w=FaceField.zeros(mesh, normal_axis=2),
        )

    def components(self) -> tuple[FaceField, FaceField, FaceField]:
        return (self.u, self.v, self.w)


@dataclass
class FlowState:
    """The state advanced by the time integrator: velocity, pressure, time, step.

    ``pressure`` is deliberately just "the pressure field" with no
    Chorin-specific assumptions baked in, so that Milestone 4's initial
    non-incremental projection can later be swapped for an incremental or
    rotational pressure-correction scheme (``projection.py``) without any
    change to this class or to ``mesh.py``.
    """

    velocity: VelocityField
    pressure: ScalarField
    time: float = 0.0
    step: int = 0

    @classmethod
    def zeros(cls, mesh: StructuredMesh3D) -> "FlowState":
        return cls(velocity=VelocityField.zeros(mesh), pressure=ScalarField.zeros(mesh))
