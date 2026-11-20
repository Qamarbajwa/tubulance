"""MAC-grid strain-rate tensor S_ij and strain magnitude |S|.

Computes the six independent components of the strain-rate tensor:
    S_xx = du/dx,  S_yy = dv/dy,  S_zz = dw/dz   (at cell centers)
    S_xy = 0.5*(du/dy + dv/dx)                   (at z-edges)
    S_xz = 0.5*(du/dz + dw/dx)                   (at y-edges)
    S_yz = 0.5*(dv/dz + dw/dy)                   (at x-edges)

Interpolates all shear components consistently onto pressure-cell centers to
compute the scalar invariant:
    |S| = sqrt(2 * S_ij * S_ij)
    2 * S_ij * S_ij = 2 * (S_xx^2 + S_yy^2 + S_zz^2 + 2*S_xy^2 + 2*S_xz^2 + 2*S_yz^2)
"""
from __future__ import annotations

import numpy as np

from .boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from .fields import ScalarField, VelocityField
from .mesh import StructuredMesh3D


def compute_strain_components(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet | None = None,
) -> dict[str, np.ndarray]:
    """Compute the six strain-rate components at their native MAC locations.

    Returns dict with keys 's_xx', 's_yy', 's_zz', 's_xy', 's_xz', 's_yz'.
    - Normal strains live at cell centers (shape (nx, ny, nz)).
    - Shear strains live at shared edge locations:
      s_xy at z-edges (shape (nx+1, ny+1, nz))
      s_xz at y-edges (shape (nx+1, ny, nz+1))
      s_yz at x-edges (shape (nx, ny+1, nz+1))
    """
    if bcs is not None:
        apply_velocity_bc(velocity, bcs)

    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    u = velocity.u.data
    v = velocity.v.data
    w = velocity.w.data
    ng = mesh.n_ghost

    # Normal strains at cell centers (interior indexing: ng..ng+nx, etc.)
    s_xx = (u[ng + 1 : ng + mesh.nx + 1, ng : ng + mesh.ny, ng : ng + mesh.nz] -
            u[ng : ng + mesh.nx, ng : ng + mesh.ny, ng : ng + mesh.nz]) / dx

    s_yy = (v[ng : ng + mesh.nx, ng + 1 : ng + mesh.ny + 1, ng : ng + mesh.nz] -
            v[ng : ng + mesh.nx, ng : ng + mesh.ny, ng : ng + mesh.nz]) / dy

    s_zz = (w[ng : ng + mesh.nx, ng : ng + mesh.ny, ng + 1 : ng + mesh.nz + 1] -
            w[ng : ng + mesh.nx, ng : ng + mesh.ny, ng : ng + mesh.nz]) / dz

    # Shear strain S_xy = 0.5 * (du/dy + dv/dx) at z-edges (faces x, y)
    # du/dy at z-edges: (u[i, j, k] - u[i, j-1, k]) / dy
    # dv/dx at z-edges: (v[i, j, k] - v[i-1, j, k]) / dx
    du_dy = (u[ng : ng + mesh.nx + 1, ng : ng + mesh.ny + 1, ng : ng + mesh.nz] -
             u[ng : ng + mesh.nx + 1, ng - 1 : ng + mesh.ny, ng : ng + mesh.nz]) / dy

    dv_dx = (v[ng : ng + mesh.nx + 1, ng : ng + mesh.ny + 1, ng : ng + mesh.nz] -
             v[ng - 1 : ng + mesh.nx, ng : ng + mesh.ny + 1, ng : ng + mesh.nz]) / dx

    s_xy = 0.5 * (du_dy + dv_dx)

    # Shear strain S_xz = 0.5 * (du/dz + dw/dx) at y-edges
    du_dz = (u[ng : ng + mesh.nx + 1, ng : ng + mesh.ny, ng : ng + mesh.nz + 1] -
             u[ng : ng + mesh.nx + 1, ng : ng + mesh.ny, ng - 1 : ng + mesh.nz]) / dz

    dw_dx = (w[ng : ng + mesh.nx + 1, ng : ng + mesh.ny, ng : ng + mesh.nz + 1] -
             w[ng - 1 : ng + mesh.nx, ng : ng + mesh.ny, ng : ng + mesh.nz + 1]) / dx

    s_xz = 0.5 * (du_dz + dw_dx)

    # Shear strain S_yz = 0.5 * (dv/dz + dw/dy) at x-edges
    dv_dz = (v[ng : ng + mesh.nx, ng : ng + mesh.ny + 1, ng : ng + mesh.nz + 1] -
             v[ng : ng + mesh.nx, ng : ng + mesh.ny + 1, ng - 1 : ng + mesh.nz]) / dz

    dw_dy = (w[ng : ng + mesh.nx, ng : ng + mesh.ny + 1, ng : ng + mesh.nz + 1] -
             w[ng : ng + mesh.nx, ng - 1 : ng + mesh.ny, ng : ng + mesh.nz + 1]) / dy

    s_yz = 0.5 * (dv_dz + dw_dy)

    return {
        "s_xx": s_xx,
        "s_yy": s_yy,
        "s_zz": s_zz,
        "s_xy": s_xy,
        "s_xz": s_xz,
        "s_yz": s_yz,
    }


def compute_strain_magnitude(
    velocity: VelocityField,
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet | None = None,
) -> ScalarField:
    """Compute strain magnitude |S| = sqrt(2 * S_ij * S_ij) at cell centers.

    Interpolates shear components from edge locations onto cell centers:
    - S_xy (at z-edges) averaged over 4 surrounding z-edges to cell center
    - S_xz (at y-edges) averaged over 4 surrounding y-edges to cell center
    - S_yz (at x-edges) averaged over 4 surrounding x-edges to cell center
    """
    comp = compute_strain_components(velocity, mesh, bcs)
    s_xx = comp["s_xx"]
    s_yy = comp["s_yy"]
    s_zz = comp["s_zz"]
    s_xy = comp["s_xy"]
    s_xz = comp["s_xz"]
    s_yz = comp["s_yz"]

    # Average S_xy from z-edges (nx+1, ny+1, nz) onto cell centers (nx, ny, nz)
    s_xy_cc = 0.25 * (
        s_xy[:-1, :-1, :] + s_xy[1:, :-1, :] + s_xy[:-1, 1:, :] + s_xy[1:, 1:, :]
    )

    # Average S_xz from y-edges (nx+1, ny, nz+1) onto cell centers (nx, ny, nz)
    s_xz_cc = 0.25 * (
        s_xz[:-1, :, :-1] + s_xz[1:, :, :-1] + s_xz[:-1, :, 1:] + s_xz[1:, :, 1:]
    )

    # Average S_yz from x-edges (nx, ny+1, nz+1) onto cell centers (nx, ny, nz)
    s_yz_cc = 0.25 * (
        s_yz[:, :-1, :-1] + s_yz[:, 1:, :-1] + s_yz[:, :-1, 1:] + s_yz[:, 1:, 1:]
    )

    two_s_ij_sq = 2.0 * (
        s_xx ** 2 + s_yy ** 2 + s_zz ** 2 +
        2.0 * (s_xy_cc ** 2) + 2.0 * (s_xz_cc ** 2) + 2.0 * (s_yz_cc ** 2)
    )

    mag = ScalarField.zeros(mesh)
    mag.interior[:] = np.sqrt(np.maximum(0.0, two_s_ij_sq))
    return mag
