"""Structured Cartesian mesh for navier3d.

The mesh is uniform-spacing-only in this milestone (nonuniform spacing is a
documented future extension). It underlies a staggered Marker-and-Cell
(MAC) grid: pressure lives at cell centers and each velocity component
lives at the centers of the faces normal to it (see
:mod:`navier3d.fields`).

Neighbor access for structured cells is deliberately *not* an explicit
index/list structure: neighbors of cell ``(i, j, k)`` are simply
``data[i-1, j, k]``, ``data[i+1, j, k]``, etc. on the padded array, which
the ghost-cell layer (``n_ghost``) makes valid even at domain boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StructuredMesh3D:
    """A uniform structured Cartesian mesh of cells over ``[0, lx] x [0, ly] x [0, lz]``.

    Parameters
    ----------
    nx, ny, nz : int
        Number of interior cells along each axis.
    lx, ly, lz : float
        Physical domain length along each axis.
    n_ghost : int
        Width of the ghost-cell layer used for boundary-condition
        enforcement and (in later milestones) finite-difference/volume
        stencils. Central schemes need 1; limited/upwind schemes added in
        Milestone 7 may require 2.
    """

    nx: int
    ny: int
    nz: int
    lx: float
    ly: float
    lz: float
    n_ghost: int = 1

    def __post_init__(self) -> None:
        for name in ("nx", "ny", "nz"):
            value = getattr(self, name)
            if value < 1:
                raise ValueError(f"{name} must be >= 1, got {value}")
        for name in ("lx", "ly", "lz"):
            value = getattr(self, name)
            if not value > 0:
                raise ValueError(f"{name} must be positive, got {value}")
        if self.n_ghost < 1:
            raise ValueError(f"n_ghost must be >= 1, got {self.n_ghost}")

    @property
    def dx(self) -> float:
        """Cell size along x."""
        return self.lx / self.nx

    @property
    def dy(self) -> float:
        """Cell size along y."""
        return self.ly / self.ny

    @property
    def dz(self) -> float:
        """Cell size along z."""
        return self.lz / self.nz

    @property
    def spacing(self) -> tuple[float, float, float]:
        """``(dx, dy, dz)``."""
        return (self.dx, self.dy, self.dz)

    @property
    def cell_volume(self) -> float:
        """Volume of a single cell (uniform spacing, so constant)."""
        return self.dx * self.dy * self.dz

    @property
    def face_area_x(self) -> float:
        """Area of a face with normal along x."""
        return self.dy * self.dz

    @property
    def face_area_y(self) -> float:
        """Area of a face with normal along y."""
        return self.dx * self.dz

    @property
    def face_area_z(self) -> float:
        """Area of a face with normal along z."""
        return self.dx * self.dy

    def cell_centers_x(self) -> np.ndarray:
        """1-D array of interior cell-center x-coordinates, length ``nx``."""
        return (np.arange(self.nx) + 0.5) * self.dx

    def cell_centers_y(self) -> np.ndarray:
        """1-D array of interior cell-center y-coordinates, length ``ny``."""
        return (np.arange(self.ny) + 0.5) * self.dy

    def cell_centers_z(self) -> np.ndarray:
        """1-D array of interior cell-center z-coordinates, length ``nz``."""
        return (np.arange(self.nz) + 0.5) * self.dz

    def face_coords_x(self) -> np.ndarray:
        """1-D array of x-face coordinates, length ``nx + 1`` (includes both boundaries)."""
        return np.arange(self.nx + 1) * self.dx

    def face_coords_y(self) -> np.ndarray:
        """1-D array of y-face coordinates, length ``ny + 1`` (includes both boundaries)."""
        return np.arange(self.ny + 1) * self.dy

    def face_coords_z(self) -> np.ndarray:
        """1-D array of z-face coordinates, length ``nz + 1`` (includes both boundaries)."""
        return np.arange(self.nz + 1) * self.dz

    def meshgrid_centers(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """3-D ``(X, Y, Z)`` meshgrid of interior cell centers, ``indexing='ij'``."""
        return np.meshgrid(
            self.cell_centers_x(), self.cell_centers_y(), self.cell_centers_z(), indexing="ij"
        )

    @classmethod
    def from_config(cls, config: "navier3d.config.SimulationConfig", n_ghost: int = 1) -> "StructuredMesh3D":  # noqa: F821
        """Construct a mesh from a validated :class:`~navier3d.config.SimulationConfig`."""
        return cls(
            nx=config.mesh.nx,
            ny=config.mesh.ny,
            nz=config.mesh.nz,
            lx=config.domain.length_x,
            ly=config.domain.length_y,
            lz=config.domain.length_z,
            n_ghost=n_ghost,
        )
