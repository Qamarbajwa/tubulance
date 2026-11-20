"""Discrete spatial differential operators on the MAC grid.

Second-order central differences throughout. Every function here is
**pure**: it allocates and returns a new field, never mutates its
argument(s). None of these functions apply boundary conditions -- they
assume the caller has already called
:func:`~navier3d.boundary_conditions.apply_pressure_bc` /
:func:`~navier3d.boundary_conditions.apply_velocity_bc` (or
:func:`~navier3d.boundary_conditions.apply_boundary_conditions`) so that
ghost cells already hold values consistent with the desired boundary
condition. This keeps boundary-condition physics in exactly one place
(``boundary_conditions.py``) and out of operator code, per the
``docs/architecture.md`` module-responsibility table.

Which ghosts each operator actually reads
------------------------------------------
* :func:`gradient` reads one ghost layer of the pressure field beyond
  each boundary face (needed to form the one-sided difference *at* the
  boundary face). Result correctness at the boundary therefore depends
  on ``apply_pressure_bc`` having been called.
* :func:`divergence` reads **only** each velocity component's interior
  (including both boundary-face values, which are real unknowns, not
  ghosts) -- it never reads a ghost cell. Its result is therefore
  independent of whether ``apply_velocity_bc`` has been called, *except*
  that for a periodic axis the two boundary-face representations must
  already be synchronized (equal) for the result to be physically
  meaningful; see ``docs/architecture.md`` "Periodic duplicate normal
  faces".
* :func:`scalar_laplacian` reads one ghost layer of the scalar field on
  every axis; depends on ``apply_pressure_bc``.
* :func:`velocity_laplacian` reads one ghost layer of each velocity
  component on **all three** of its axes, including its own face-normal
  axis -- this is the first Milestone 2 use of the normal-axis ghost
  layers that Milestone 1 allocated but did not yet exercise. Depends on
  ``apply_velocity_bc``.

Compatibility
-------------
``gradient`` and ``divergence`` are constructed as an exactly compatible
pair: composing them, ``divergence(gradient(p))``, is algebraically
identical (to floating-point roundoff) to :func:`scalar_laplacian`,
because both read/write the same face locations with the same index
shifts. This is verified in ``tests/test_operators.py`` and is the
property Milestone 4's pressure projection will depend on.
"""
from __future__ import annotations

import numpy as np

from .fields import FaceField, ScalarField, VelocityField
from .mesh import StructuredMesh3D


class OperatorError(ValueError):
    """Raised when a field's shape/ghost width is incompatible with the given mesh."""


def _check_scalar(field: ScalarField, mesh: StructuredMesh3D, name: str) -> None:
    if field.n_ghost != mesh.n_ghost:
        raise OperatorError(
            f"{name}: scalar field n_ghost={field.n_ghost} does not match "
            f"mesh.n_ghost={mesh.n_ghost}"
        )
    ng = field.n_ghost
    expected = (mesh.nx + 2 * ng, mesh.ny + 2 * ng, mesh.nz + 2 * ng)
    if field.data.shape != expected:
        raise OperatorError(
            f"{name}: scalar field shape {field.data.shape} is incompatible with "
            f"mesh (nx={mesh.nx}, ny={mesh.ny}, nz={mesh.nz}) at n_ghost={ng}; "
            f"expected shape {expected}"
        )


def _check_face(field: FaceField, mesh: StructuredMesh3D, expected_axis: int, name: str) -> None:
    if field.normal_axis != expected_axis:
        raise OperatorError(
            f"{name}: expected a face field with normal_axis={expected_axis}, "
            f"got normal_axis={field.normal_axis}"
        )
    if field.n_ghost != mesh.n_ghost:
        raise OperatorError(
            f"{name}: face field n_ghost={field.n_ghost} does not match "
            f"mesh.n_ghost={mesh.n_ghost}"
        )
    ng = field.n_ghost
    n_cells = (mesh.nx, mesh.ny, mesh.nz)
    shape = [mesh.nx + 2 * ng, mesh.ny + 2 * ng, mesh.nz + 2 * ng]
    shape[expected_axis] = (n_cells[expected_axis] + 1) + 2 * ng
    if field.data.shape != tuple(shape):
        raise OperatorError(
            f"{name}: face field shape {field.data.shape} is incompatible with "
            f"mesh (nx={mesh.nx}, ny={mesh.ny}, nz={mesh.nz}) at n_ghost={ng}; "
            f"expected shape {tuple(shape)}"
        )


def _check_velocity(velocity: VelocityField, mesh: StructuredMesh3D, name: str) -> None:
    _check_face(velocity.u, mesh, 0, name)
    _check_face(velocity.v, mesh, 1, name)
    _check_face(velocity.w, mesh, 2, name)


def _interior_shifted(field, axis: int, offset: int) -> np.ndarray:
    """``field``'s interior region shifted by ``offset`` along ``axis``
    only, built from the field's own named ``interior_range``/
    ``shifted_range`` accessors (``fields.py``) rather than hand-written
    ``ng:-ng``-style index arithmetic. Used to form central-difference
    stencils."""
    idx = [field.shifted_range(a, offset) if a == axis else field.interior_range(a) for a in range(3)]
    return field.data[tuple(idx)]


def _face_gradient_term(data: np.ndarray, ng: int, axis: int, n_cells: int, d: float) -> np.ndarray:
    """``(p[i] - p[i-1]) / d`` for face index ``i = 0..n_cells`` along ``axis``
    (``n_cells+1`` face values, matching a normal_axis=``axis`` FaceField's
    interior shape), tangential axes restricted to their interior range.

    Unlike :func:`_interior_shifted` this does not build on
    ``ScalarField``'s named accessors: the output has ``n_cells+1`` values
    along ``axis`` (one more than the input scalar field's own
    ``n_cells``-wide interior), so it is not a same-shape "shift" of
    ``phi``'s interior -- it is a genuinely different (one-wider) slice,
    which ``interior_range``/``shifted_range`` do not represent."""
    hi_idx, lo_idx = [], []
    for a in range(3):
        if a == axis:
            hi_idx.append(slice(ng, ng + n_cells + 1))
            lo_idx.append(slice(ng - 1, ng + n_cells))
        else:
            hi_idx.append(slice(ng, -ng))
            lo_idx.append(slice(ng, -ng))
    return (data[tuple(hi_idx)] - data[tuple(lo_idx)]) / d


def _cell_divergence_term(data: np.ndarray, ng: int, axis: int, n_cells: int, d: float) -> np.ndarray:
    """``(u[i+1] - u[i]) / d`` for cell index ``i = 0..n_cells-1`` along
    ``axis`` (``n_cells`` values, matching a ScalarField's interior
    shape), using only the ``n_cells+1`` real face values (no ghosts)."""
    hi_idx, lo_idx = [], []
    for a in range(3):
        if a == axis:
            hi_idx.append(slice(ng + 1, ng + n_cells + 1))
            lo_idx.append(slice(ng, ng + n_cells))
        else:
            hi_idx.append(slice(ng, -ng))
            lo_idx.append(slice(ng, -ng))
    return (data[tuple(hi_idx)] - data[tuple(lo_idx)]) / d


def _centered_laplacian(field, spacing: tuple) -> np.ndarray:
    interior = field.interior
    lap = np.zeros_like(interior)
    for axis, d in enumerate(spacing):
        plus = _interior_shifted(field, axis, +1)
        minus = _interior_shifted(field, axis, -1)
        lap += (plus - 2.0 * interior + minus) / (d * d)
    return lap


def gradient(phi: ScalarField, mesh: StructuredMesh3D) -> VelocityField:
    """Pressure (or any cell-centered scalar) gradient, evaluated at the
    MAC velocity face locations.

    ``(dphi/dx)_{i+1/2,j,k} = (phi_{i+1,j,k} - phi_{i,j,k}) / dx`` at u-faces,
    and analogously for v-, w-faces. Requires ``phi``'s ghosts to already
    be filled (see module docstring).

    Parameters
    ----------
    phi : ScalarField
        Shape ``(nx+2ng, ny+2ng, nz+2ng)``.
    mesh : StructuredMesh3D

    Returns
    -------
    VelocityField
        ``result.u.interior`` shape ``(nx+1, ny, nz)``, etc. -- the same
        shape as a real velocity field's interior.
    """
    _check_scalar(phi, mesh, "gradient")
    result = VelocityField.zeros(mesh)
    cell_counts = (mesh.nx, mesh.ny, mesh.nz)
    spacings = (mesh.dx, mesh.dy, mesh.dz)
    for axis, comp in enumerate(result.components()):
        comp.interior = _face_gradient_term(phi.data, phi.n_ghost, axis, cell_counts[axis], spacings[axis])
    return result


def divergence(velocity: VelocityField, mesh: StructuredMesh3D) -> ScalarField:
    """MAC velocity divergence, evaluated at pressure cell centers.

    ``(div u)_{i,j,k} = (u_{i+1/2,j,k} - u_{i-1/2,j,k})/dx +``
    ``(v_{i,j+1/2,k} - v_{i,j-1/2,k})/dy +``
    ``(w_{i,j,k+1/2} - w_{i,j,k-1/2})/dz``.

    Uses only each component's real interior (boundary-inclusive) face
    values -- no ghost cells are read, so this does not depend on
    ``apply_velocity_bc`` having been called, except that a periodic
    axis's two boundary-face representations must already be
    synchronized (see ``docs/architecture.md`` "Periodic duplicate
    normal faces").

    Parameters
    ----------
    velocity : VelocityField
    mesh : StructuredMesh3D

    Returns
    -------
    ScalarField
        ``result.interior`` shape ``(nx, ny, nz)``.
    """
    _check_velocity(velocity, mesh, "divergence")
    result = ScalarField.zeros(mesh)
    cell_counts = (mesh.nx, mesh.ny, mesh.nz)
    spacings = (mesh.dx, mesh.dy, mesh.dz)
    div = np.zeros(result.interior.shape, dtype=np.float64)
    for axis, comp in enumerate(velocity.components()):
        div += _cell_divergence_term(comp.data, comp.n_ghost, axis, cell_counts[axis], spacings[axis])
    result.interior = div
    return result


def scalar_laplacian(phi: ScalarField, mesh: StructuredMesh3D) -> ScalarField:
    """Cell-centered scalar Laplacian, standard 7-point second-order stencil.

    Requires ``phi``'s ghosts to already be filled.

    Parameters
    ----------
    phi : ScalarField
    mesh : StructuredMesh3D

    Returns
    -------
    ScalarField
        ``result.interior`` shape ``(nx, ny, nz)``.
    """
    _check_scalar(phi, mesh, "scalar_laplacian")
    result = ScalarField.zeros(mesh)
    result.interior = _centered_laplacian(phi, mesh.spacing)
    return result


def velocity_laplacian(velocity: VelocityField, mesh: StructuredMesh3D) -> VelocityField:
    """Component-wise velocity Laplacian, each component evaluated at its
    own staggered (face-centered) location.

    Requires each component's ghosts to already be filled on **all three**
    of its axes, including its own face-normal axis (the ghost layers
    beyond each boundary face, allocated in Milestone 1 but first read
    here).

    Parameters
    ----------
    velocity : VelocityField
    mesh : StructuredMesh3D

    Returns
    -------
    VelocityField
        Same shapes as ``velocity`` itself.
    """
    _check_velocity(velocity, mesh, "velocity_laplacian")
    result = VelocityField.zeros(mesh)
    for comp_out, comp_in in zip(result.components(), velocity.components()):
        comp_out.interior = _centered_laplacian(comp_in, mesh.spacing)
    return result
