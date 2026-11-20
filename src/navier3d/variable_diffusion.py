"""Conservative variable-viscosity stress divergence operator and linear system.

Computes:
    (div tau_eff)_i = d/dx_j [ 2 * nu_eff * S_ij ]
where nu_eff = nu + nu_t is stored at pressure-cell centers.

Normal stress components 2 * nu_eff * S_xx live at cell centers.
Shear stress components 2 * nu_eff * S_xy live at shared edge locations:
- z-edges for (u, v) shear
- y-edges for (u, w) shear
- x-edges for (v, w) shear

For constant nu_eff = nu_c on divergence-free fields, this operator reduces
identically to nu_c * velocity_laplacian(u).
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import LinearOperator, bicgstab, cg, gmres

from .boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from .fields import ScalarField, VelocityField
from .mesh import StructuredMesh3D
from .strain import compute_strain_components


class DiffusionSystemError(ValueError):
    """Raised when an invalid solver configuration is requested."""


def variable_viscosity_stress_divergence(
    velocity: VelocityField,
    nu_eff: ScalarField,
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
) -> VelocityField:
    """Compute conservative divergence of stress tensor tau_eff = 2 * nu_eff * S_ij

    Returns VelocityField located at MAC face locations.
    """
    apply_velocity_bc(velocity, bcs)

    # 1. Compute strain components
    strain = compute_strain_components(velocity, mesh)
    s_xx = strain["s_xx"]
    s_yy = strain["s_yy"]
    s_zz = strain["s_zz"]
    s_xy = strain["s_xy"]
    s_xz = strain["s_xz"]
    s_yz = strain["s_yz"]

    nu_cc = nu_eff.interior  # shape (nx, ny, nz)

    mode_x = "wrap" if bcs.is_periodic_axis(0) else "edge"
    mode_y = "wrap" if bcs.is_periodic_axis(1) else "edge"
    mode_z = "wrap" if bcs.is_periodic_axis(2) else "edge"

    # 2. Interpolate nu_eff onto edge locations
    # z-edges (nx+1, ny+1, nz) from 4 surrounding cell centers along (x, y)
    nu_pad_z = np.pad(nu_cc, ((1, 1), (0, 0), (0, 0)), mode=mode_x)
    nu_pad_z = np.pad(nu_pad_z, ((0, 0), (1, 1), (0, 0)), mode=mode_y)
    nu_z_edge = 0.25 * (
        nu_pad_z[:-1, :-1, :] + nu_pad_z[1:, :-1, :] + nu_pad_z[:-1, 1:, :] + nu_pad_z[1:, 1:, :]
    )

    # y-edges (nx+1, ny, nz+1) from 4 surrounding cell centers along (x, z)
    nu_pad_y = np.pad(nu_cc, ((1, 1), (0, 0), (0, 0)), mode=mode_x)
    nu_pad_y = np.pad(nu_pad_y, ((0, 0), (0, 0), (1, 1)), mode=mode_z)
    nu_y_edge = 0.25 * (
        nu_pad_y[:-1, :, :-1] + nu_pad_y[1:, :, :-1] + nu_pad_y[:-1, :, 1:] + nu_pad_y[1:, :, 1:]
    )

    # x-edges (nx, ny+1, nz+1) from 4 surrounding cell centers along (y, z)
    nu_pad_x = np.pad(nu_cc, ((0, 0), (1, 1), (0, 0)), mode=mode_y)
    nu_pad_x = np.pad(nu_pad_x, ((0, 0), (0, 0), (1, 1)), mode=mode_z)
    nu_x_edge = 0.25 * (
        nu_pad_x[:, :-1, :-1] + nu_pad_x[:, 1:, :-1] + nu_pad_x[:, :-1, 1:] + nu_pad_x[:, 1:, 1:]
    )

    # 3. Form stress components tau = 2 * nu_eff * S
    tau_xx = 2.0 * nu_cc * s_xx       # at cell centers (nx, ny, nz)
    tau_yy = 2.0 * nu_cc * s_yy       # at cell centers (nx, ny, nz)
    tau_zz = 2.0 * nu_cc * s_zz       # at cell centers (nx, ny, nz)

    tau_xy = 2.0 * nu_z_edge * s_xy   # at z-edges (nx+1, ny+1, nz)
    tau_xz = 2.0 * nu_y_edge * s_xz   # at y-edges (nx+1, ny, nz+1)
    tau_yz = 2.0 * nu_x_edge * s_yz   # at x-edges (nx, ny+1, nz+1)

    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz
    res = VelocityField.zeros(mesh)

    # Component u (at x-faces, interior shape (nx+1, ny, nz))
    # d(tau_xx)/dx across cell centers (interior faces 0..nx)
    pad_x = "wrap" if bcs.is_periodic_axis(0) else "edge"
    tau_xx_pad = np.pad(tau_xx, ((1, 1), (0, 0), (0, 0)), mode=pad_x)
    d_tau_xx_dx = (tau_xx_pad[1:, :, :] - tau_xx_pad[:-1, :, :]) / dx

    # d(tau_xy)/dy across z-edges
    d_tau_xy_dy = (tau_xy[:, 1:, :] - tau_xy[:, :-1, :]) / dy

    # d(tau_xz)/dz across y-edges
    d_tau_xz_dz = (tau_xz[:, :, 1:] - tau_xz[:, :, :-1]) / dz

    res.u.interior[:] = d_tau_xx_dx + d_tau_xy_dy + d_tau_xz_dz

    # Component v (at y-faces, interior shape (nx, ny+1, nz))
    pad_y = "wrap" if bcs.is_periodic_axis(1) else "edge"
    tau_yy_pad = np.pad(tau_yy, ((0, 0), (1, 1), (0, 0)), mode=pad_y)
    d_tau_yy_dy = (tau_yy_pad[:, 1:, :] - tau_yy_pad[:, :-1, :]) / dy

    d_tau_xy_dx = (tau_xy[1:, :, :] - tau_xy[:-1, :, :]) / dx
    d_tau_yz_dz = (tau_yz[:, :, 1:] - tau_yz[:, :, :-1]) / dz

    res.v.interior[:] = d_tau_xy_dx + d_tau_yy_dy + d_tau_yz_dz

    # Component w (at z-faces, interior shape (nx, ny, nz+1))
    pad_z = "wrap" if bcs.is_periodic_axis(2) else "edge"
    tau_zz_pad = np.pad(tau_zz, ((0, 0), (0, 0), (1, 1)), mode=pad_z)
    d_tau_zz_dz = (tau_zz_pad[:, :, 1:] - tau_zz_pad[:, :, :-1]) / dz

    d_tau_xz_dx = (tau_xz[1:, :, :] - tau_xz[:-1, :, :]) / dx
    d_tau_yz_dy = (tau_yz[:, 1:, :] - tau_yz[:, :-1, :]) / dy

    res.w.interior[:] = d_tau_xz_dx + d_tau_yz_dy + d_tau_zz_dz

    return res


def assemble_variable_diffusion_matrix(
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    dt: float,
    theta: float,
    nu_eff: ScalarField,
) -> np.ndarray:
    """Explicitly assemble the reduced 2D matrix A for [I - theta*dt*div(2 nu_eff S)] over independent DOFs.

    Used for matrix symmetry error testing and positive definiteness verification.
    """
    sys = VariableDiffusionSystem(mesh, bcs, dt, theta, nu_eff)

    # Independent DOF ranges
    u_range_x = slice(0, mesh.nx) if bcs.is_periodic_axis(0) else slice(1, mesh.nx)
    v_range_y = slice(0, mesh.ny) if bcs.is_periodic_axis(1) else slice(1, mesh.ny)
    w_range_z = slice(0, mesh.nz) if bcs.is_periodic_axis(2) else slice(1, mesh.nz)

    u_nx = (mesh.nx) if bcs.is_periodic_axis(0) else (mesh.nx - 1)
    v_ny = (mesh.ny) if bcs.is_periodic_axis(1) else (mesh.ny - 1)
    w_nz = (mesh.nz) if bcs.is_periodic_axis(2) else (mesh.nz - 1)

    u_size = u_nx * mesh.ny * mesh.nz
    v_size = mesh.nx * v_ny * mesh.nz
    w_size = mesh.nx * mesh.ny * w_nz
    total_size = u_size + v_size + w_size

    A_mat = np.zeros((total_size, total_size))

    for j in range(total_size):
        e_j = np.zeros(total_size)
        e_j[j] = 1.0

        vel = VelocityField.zeros(mesh)
        vel.u.interior[u_range_x, :, :] = e_j[:u_size].reshape((u_nx, mesh.ny, mesh.nz))
        if bcs.is_periodic_axis(0):
            vel.u.interior[-1, :, :] = vel.u.interior[0, :, :]

        vel.v.interior[:, v_range_y, :] = e_j[u_size : u_size + v_size].reshape((mesh.nx, v_ny, mesh.nz))
        if bcs.is_periodic_axis(1):
            vel.v.interior[:, -1, :] = vel.v.interior[:, 0, :]

        vel.w.interior[:, :, w_range_z] = e_j[u_size + v_size :].reshape((mesh.nx, mesh.ny, w_nz))
        if bcs.is_periodic_axis(2):
            vel.w.interior[:, :, -1] = vel.w.interior[:, :, 0]

        apply_v = sys.apply(vel)

        out = np.empty(total_size)
        out[:u_size] = apply_v.u.interior[u_range_x, :, :].ravel()
        out[u_size : u_size + v_size] = apply_v.v.interior[:, v_range_y, :].ravel()
        out[u_size + v_size :] = apply_v.w.interior[:, :, w_range_z].ravel()

        A_mat[:, j] = out

    return A_mat


def compute_symmetry_error(A: np.ndarray) -> float:
    """Relative matrix symmetry error E_sym = ||A - A^T|| / ||A||."""
    diff_norm = float(np.linalg.norm(A - A.T))
    a_norm = float(np.linalg.norm(A))
    return diff_norm / (a_norm + 1e-15)


class VariableDiffusionSystem:
    """Linear operator and solver for variable-coefficient predictor step:
        [ I - theta * dt * (div tau_eff) ] u* = rhs
    """

    def __init__(
        self,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet,
        dt: float,
        theta: float,
        nu_eff: ScalarField,
        solver: str = "auto",
    ) -> None:
        self.mesh = mesh
        self.bcs = bcs
        self.dt = dt
        self.theta = theta
        self.nu_eff = nu_eff
        self.solver = solver.lower()

    def apply(self, vel: VelocityField) -> VelocityField:
        div_tau = variable_viscosity_stress_divergence(vel, self.nu_eff, self.mesh, self.bcs)
        res = VelocityField.zeros(self.mesh)
        factor = self.theta * self.dt
        for axis in range(3):
            res.components()[axis].interior[:] = (
                vel.components()[axis].interior - factor * div_tau.components()[axis].interior
            )
        return res

    def solve(
        self,
        rhs: VelocityField,
        initial_guess: VelocityField | None = None,
        tol: float = 1e-8,
        max_iter: int = 500,
    ) -> tuple[VelocityField, int]:
        """Solve the variable-coefficient system via iterative Krylov solver (CG / BiCGSTAB / GMRES)."""
        u_shape = rhs.u.interior.shape
        v_shape = rhs.v.interior.shape
        w_shape = rhs.w.interior.shape

        u_size = rhs.u.interior.size
        v_size = rhs.v.interior.size
        w_size = rhs.w.interior.size
        total_size = u_size + v_size + w_size

        def _matvec(v_vec: np.ndarray) -> np.ndarray:
            vel = VelocityField.zeros(self.mesh)
            vel.u.interior[:] = v_vec[:u_size].reshape(u_shape)
            vel.v.interior[:] = v_vec[u_size : u_size + v_size].reshape(v_shape)
            vel.w.interior[:] = v_vec[u_size + v_size :].reshape(w_shape)

            apply_vec = self.apply(vel)
            out = np.empty(total_size)
            out[:u_size] = apply_vec.u.interior.ravel()
            out[u_size : u_size + v_size] = apply_vec.v.interior.ravel()
            out[u_size + v_size :] = apply_vec.w.interior.ravel()
            return out

        A = LinearOperator((total_size, total_size), matvec=_matvec, dtype=np.float64)

        b_vec = np.empty(total_size)
        b_vec[:u_size] = rhs.u.interior.ravel()
        b_vec[u_size : u_size + v_size] = rhs.v.interior.ravel()
        b_vec[u_size + v_size :] = rhs.w.interior.ravel()

        x0 = None
        if initial_guess is not None:
            x0 = np.empty(total_size)
            x0[:u_size] = initial_guess.u.interior.ravel()
            x0[u_size : u_size + v_size] = initial_guess.v.interior.ravel()
            x0[u_size + v_size :] = initial_guess.w.interior.ravel()

        # Check solver requirements
        if self.solver == "cg":
            # Explicitly verify symmetry for CG
            if total_size <= 2000:
                A_mat = assemble_variable_diffusion_matrix(self.mesh, self.bcs, self.dt, self.theta, self.nu_eff)
                e_sym = compute_symmetry_error(A_mat)
                if e_sym > 1e-6:
                    raise DiffusionSystemError(
                        f"CG solver rejected for non-symmetric variable diffusion matrix (E_sym = {e_sym:.4e}). Use 'bicgstab' or 'gmres'."
                    )

        if self.solver == "cg":
            sol_vec, info = cg(A, b_vec, x0=x0, rtol=tol, maxiter=max_iter)
        elif self.solver in ("bicgstab", "auto"):
            sol_vec, info = bicgstab(A, b_vec, x0=x0, rtol=tol, maxiter=max_iter)
            if info != 0 and info is not None:
                sol_vec, info = cg(A, b_vec, x0=x0, rtol=tol, maxiter=max_iter)
        elif self.solver == "gmres":
            sol_vec, info = gmres(A, b_vec, x0=x0, rtol=tol, maxiter=max_iter)
        else:
            raise DiffusionSystemError(f"Unsupported solver '{self.solver}'. Must be 'auto', 'cg', 'bicgstab', or 'gmres'.")

        sol_vel = VelocityField.zeros(self.mesh)
        sol_vel.u.interior[:] = sol_vec[:u_size].reshape(u_shape)
        sol_vel.v.interior[:] = sol_vec[u_size : u_size + v_size].reshape(v_shape)
        sol_vel.w.interior[:] = sol_vec[u_size + v_size :].reshape(w_shape)
        apply_velocity_bc(sol_vel, self.bcs)

        return sol_vel, info if info is not None else 0
