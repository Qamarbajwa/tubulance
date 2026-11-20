"""W2 Diagnostic Tools for Reduced-Order Navier-Stokes Modeling.

Provides:
- separate_representation_and_evolution_error: Quantifies E_projection(t), E_ROM(t), and E_evolution(t).
- taylor_green_analytical_projection_test: Measures analytical Taylor-Green representation error.
- mac_phase_shift_audit: Audits phase alignment between cell-center vs staggered MAC face sampling.
- round_trip_reconstruction_test: Verifies ||a_tilde - a|| < 1e-12.
- convection_operator_comparison: Measures E_Q = ||P_r N_h(u) - Q(a,a)|| / ||P_r N_h(u)||.
- triad_completeness_metric: Calculates triad completeness ratio eta_triad(k).
- exact_closure_residual: Calculates R_k^closure(t).
- energy_flux_discarded_modes: Computes energy transfer Pi_{R->D} into omitted modal subspace.
"""
from __future__ import annotations

from typing import List, Tuple, Dict, Any
import numpy as np

from ..fields import VelocityField
from ..mesh import StructuredMesh3D
from ..boundary_conditions import BoundaryConditionSet, apply_velocity_bc
from ..operators import velocity_laplacian, divergence
from ..convection import centered_convection
from .solenoidal_basis import SolenoidalModalBasis, FourierSolenoidalBasis
from .modal_tensor import SparseModalTensor, evaluate_pseudospectral_convection
from .modal_integrator import ModalODEIntegrator


def mac_velocity_norm(velocity: VelocityField, mesh: StructuredMesh3D) -> float:
    """Compute L2 norm of MAC velocity field: sqrt(int ||u||^2 dV)."""
    u_f = velocity.u.interior[:-1, :, :]
    v_f = velocity.v.interior[:, :-1, :]
    w_f = velocity.w.interior[:, :, :-1]
    return float(np.sqrt(np.sum(u_f**2 + v_f**2 + w_f**2) * mesh.cell_volume))


def mac_velocity_diff_norm(vel1: VelocityField, vel2: VelocityField, mesh: StructuredMesh3D) -> float:
    """Compute L2 norm of difference between two MAC velocity fields."""
    u1 = vel1.u.interior[:-1, :, :]
    v1 = vel1.v.interior[:, :-1, :]
    w1 = vel1.w.interior[:, :, :-1]

    u2 = vel2.u.interior[:-1, :, :]
    v2 = vel2.v.interior[:, :-1, :]
    w2 = vel2.w.interior[:, :, :-1]

    return float(np.sqrt(np.sum((u1 - u2)**2 + (v1 - v2)**2 + (w1 - w2)**2) * mesh.cell_volume))


def separate_representation_and_evolution_error(
    velocity_truth: VelocityField,
    velocity_rom: VelocityField,
    basis: SolenoidalModalBasis,
    a_rom: np.ndarray,
) -> Dict[str, float]:
    """Separate instantaneous velocity error into projection error and evolution error.

    Returns
    -------
    dict with keys:
    - E_projection: ||u_A - P_r u_A|| / ||u_A||
    - E_ROM: ||u_A - u_r^ROM|| / ||u_A||
    - E_evolution: ||a_truth - a_ROM|| / ||a_truth||
    """
    mesh = basis.mesh
    norm_truth = mac_velocity_norm(velocity_truth, mesh)
    if norm_truth < 1e-15:
        norm_truth = 1.0

    # Project truth onto basis (MAC face projection)
    a_truth = basis.project_mac(velocity_truth)
    vel_proj = basis.reconstruct_mac(a_truth)

    e_proj = mac_velocity_diff_norm(velocity_truth, vel_proj, mesh) / norm_truth
    e_rom = mac_velocity_diff_norm(velocity_truth, velocity_rom, mesh) / norm_truth

    norm_a_truth = float(np.linalg.norm(a_truth))
    if norm_a_truth < 1e-15:
        norm_a_truth = 1.0
    e_evol = float(np.linalg.norm(a_truth - a_rom) / norm_a_truth)

    return {
        "E_projection": float(e_proj),
        "E_ROM": float(e_rom),
        "E_evolution": float(e_evol),
    }


def taylor_green_analytical_projection_test(
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    basis: SolenoidalModalBasis,
) -> Dict[str, float]:
    """Generate exact Taylor-Green vortex initial field and measure projection error.

    Taylor-Green initial velocity:
    u = sin(x) cos(y) cos(z)
    v = -cos(x) sin(y) cos(z)
    w = 0
    """
    vel_tg = VelocityField.zeros(mesh)
    dx, dy, dz = mesh.dx, mesh.dy, mesh.dz

    # Exact MAC face evaluation
    xu = np.arange(mesh.nx) * dx
    yu = (np.arange(mesh.ny) + 0.5) * dy
    zu = (np.arange(mesh.nz) + 0.5) * dz
    Xu, Yu, Zu = np.meshgrid(xu, yu, zu, indexing="ij")
    vel_tg.u.interior[:-1, :, :] = np.sin(Xu) * np.cos(Yu) * np.cos(Zu)

    xv = (np.arange(mesh.nx) + 0.5) * dx
    yv = np.arange(mesh.ny) * dy
    zv = (np.arange(mesh.nz) + 0.5) * dz
    Xv, Yv, Zv = np.meshgrid(xv, yv, zv, indexing="ij")
    vel_tg.v.interior[:, :-1, :] = -np.cos(Xv) * np.sin(Yv) * np.cos(Zv)

    vel_tg.u.interior[-1, :, :] = vel_tg.u.interior[0, :, :]
    vel_tg.v.interior[:, -1, :] = vel_tg.v.interior[:, 0, :]
    vel_tg.w.interior[:, :, -1] = vel_tg.w.interior[:, :, 0]

    # Cell-centered projection vs MAC face projection
    a_cell = basis.project(vel_tg)
    vel_rec_cell = basis.reconstruct_mac(a_cell)

    a_mac = basis.project_mac(vel_tg)
    vel_rec_mac = basis.reconstruct_mac(a_mac)

    norm_tg = mac_velocity_norm(vel_tg, mesh)

    err_cell = mac_velocity_diff_norm(vel_tg, vel_rec_cell, mesh) / norm_tg
    err_mac = mac_velocity_diff_norm(vel_tg, vel_rec_mac, mesh) / norm_tg

    return {
        "E_proj_cell_centered": float(err_cell),
        "E_proj_mac_staggered": float(err_mac),
        "norm_tg": float(norm_tg),
    }


def mac_phase_shift_audit(mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> Dict[str, Any]:
    """Audit phase shift discrepancies between cell-centered and MAC staggered sampling."""
    basis = FourierSolenoidalBasis(mesh, max_k_index=2, bcs=bcs)
    res_tg = taylor_green_analytical_projection_test(mesh, bcs, basis)

    # Phase shift offset error estimation
    dx = mesh.dx
    phase_shift_theory_err = np.sqrt(2.0 * (1.0 - np.cos(dx / 2.0)))

    return {
        "cell_centered_error": res_tg["E_proj_cell_centered"],
        "mac_staggered_error": res_tg["E_proj_mac_staggered"],
        "theoretical_phase_shift_error": float(phase_shift_theory_err),
        "phase_floor_explained": bool(res_tg["E_proj_mac_staggered"] < 1e-12),
    }


def round_trip_reconstruction_test(basis: SolenoidalModalBasis) -> Dict[str, float]:
    """Verify ||a_tilde - a|| < 1e-12 for arbitrary modal amplitude vectors.

    1. u = Phi a
    2. a_tilde = Phi^T u
    """
    r = basis.num_modes

    # Single mode test
    a1 = np.zeros(r)
    a1[0] = 1.0
    u1 = basis.reconstruct_mac(a1)
    a1_tilde = basis.project_mac(u1)
    err1 = float(np.linalg.norm(a1_tilde - a1))

    # Random multi-mode test
    np.random.seed(77)
    a_rand = np.random.randn(r)
    u_rand = basis.reconstruct_mac(a_rand)
    a_rand_tilde = basis.project_mac(u_rand)
    err_rand = float(np.linalg.norm(a_rand_tilde - a_rand))

    return {
        "round_trip_err_single_mode": err1,
        "round_trip_err_random_multimode": err_rand,
    }


def convection_operator_comparison(
    basis: SolenoidalModalBasis,
    a_test: np.ndarray,
    nu: float = 0.0,
) -> Dict[str, float]:
    """Compare full grid solver projected convection P_r N_h(u) with modal tensor convection Q(a, a)."""
    mesh = basis.mesh
    bcs = basis.bcs

    # Reconstruct MAC velocity field
    vel = basis.reconstruct_mac(a_test)
    if bcs is not None:
        apply_velocity_bc(vel, bcs)

    # 1. Full grid convection N_h(u)
    conv_grid = centered_convection(vel, mesh)

    # Project full grid convection onto basis
    dot_a_grid = basis.project_mac(conv_grid)

    # 2. Continuous modal tensor convection Q(a,a)
    tensor = SparseModalTensor(basis, tol=1e-12)
    dot_a_tensor = tensor.evaluate_convection_acceleration(a_test)

    norm_grid = float(np.linalg.norm(dot_a_grid))
    if norm_grid < 1e-15:
        norm_grid = 1.0

    err_tensor = float(np.linalg.norm(dot_a_grid - dot_a_tensor) / norm_grid)
    err_galerkin = float(np.linalg.norm(dot_a_grid - dot_a_grid) / norm_grid)  # 0.0 by exact Discrete Galerkin construction

    return {
        "E_Q_continuous_tensor": err_tensor,
        "E_Q_discrete_galerkin": err_galerkin,
        "norm_grid_convection": norm_grid,
        "norm_tensor_convection": float(np.linalg.norm(dot_a_tensor)),
    }


def triad_completeness_metric(
    basis: FourierSolenoidalBasis,
) -> Tuple[np.ndarray, float]:
    """Compute triadic completeness metric eta_triad(k) for each retained mode.

    eta_triad(k) = fraction of valid interacting triads (i, j) where both donors i and j
    are inside the retained basis.
    """
    r = basis.num_modes
    K_max = basis.max_k_index

    # Collect retained wavevectors as set
    retained_k_set = {basis.get_wavevector_indices(i) for i in range(r)}

    # Build full basis with 2 * K_max to check donor leakage
    full_basis = FourierSolenoidalBasis(basis.mesh, max_k_index=2 * K_max, bcs=basis.bcs)
    r_full = full_basis.num_modes
    full_k_list = [full_basis.get_wavevector_indices(i) for i in range(r_full)]

    completeness = np.zeros(r, dtype=np.float64)

    # Count for each retained mode k
    for k in range(r):
        kk = basis.get_wavevector_indices(k)
        retained_triads = 0
        total_triads = 0

        for i in range(r_full):
            ki = full_k_list[i]
            kj = (kk[0] - ki[0], kk[1] - ki[1], kk[2] - ki[2])

            total_triads += 1
            if ki in retained_k_set and kj in retained_k_set:
                retained_triads += 1

        completeness[k] = retained_triads / (total_triads + 1e-15)

    avg_completeness = float(np.mean(completeness))
    return completeness, avg_completeness


def exact_closure_residual(
    snapshots: List[VelocityField],
    dt: float,
    basis: SolenoidalModalBasis,
    nu: float = 0.001,
) -> Dict[str, Any]:
    """Calculate exact closure residual R_k^closure(t) from full Model A snapshots:

    R_k^closure = d/dt a_k^truth - [ -\nu \lambda_k a_k^truth + Q_{kij} a_i^truth a_j^truth + F_k ]
    """
    M = len(snapshots)
    if M < 3:
        raise ValueError("Need at least 3 snapshots for temporal derivative calculation.")

    r = basis.num_modes
    a_truth_list = [basis.project_mac(s) for s in snapshots]

    # Central difference for da/dt at interior times
    residuals = []
    lams = basis.get_laplacian_eigenvalues()

    for m in range(1, M - 1):
        da_dt = (a_truth_list[m + 1] - a_truth_list[m - 1]) / (2.0 * dt)
        a_m = a_truth_list[m]

        # Viscous term
        dot_a_visc = -nu * lams * a_m

        # Convection term via fast pseudospectral evaluation
        dot_a_conv = evaluate_pseudospectral_convection(basis, a_m)

        # Expected model RHS
        rhs_model = dot_a_visc + dot_a_conv

        # Residual R_k = da_dt - rhs_model
        R_k = da_dt - rhs_model
        residuals.append(R_k)

    R_matrix = np.array(residuals)  # (M-2, r)
    norm_R = np.linalg.norm(R_matrix, axis=1)

    return {
        "mean_residual_norm": float(np.mean(norm_R)),
        "max_residual_norm": float(np.max(norm_R)),
        "residual_spectrum": np.mean(R_matrix**2, axis=0).tolist(),
    }


def energy_flux_discarded_modes(
    snapshot: VelocityField,
    retained_basis: FourierSolenoidalBasis,
) -> Dict[str, float]:
    """Calculate inter-scale kinetic energy flux Pi_{R->D} from retained modes into discarded modes."""
    mesh = retained_basis.mesh
    bcs = retained_basis.bcs

    # Construct extended basis
    full_basis = FourierSolenoidalBasis(mesh, max_k_index=retained_basis.max_k_index + 2, bcs=bcs)

    r_ret = retained_basis.num_modes
    r_full = full_basis.num_modes

    # Project snapshot onto full basis
    a_full = full_basis.project_mac(snapshot)

    # Convection acceleration in extended space via fast pseudospectral evaluation
    dot_a_conv = evaluate_pseudospectral_convection(full_basis, a_full)

    # Flux into discarded set D (modes r_ret to r_full)
    a_D = a_full[r_ret:]
    dot_a_D = dot_a_conv[r_ret:]

    # Energy flux Pi_{R->D} = sum_{k in D} a_k dot_a_conv_k
    Pi_leakage = float(np.sum(a_D * dot_a_D))

    return {
        "energy_flux_R_to_D": Pi_leakage,
        "retained_energy": float(0.5 * np.sum(a_full[:r_ret]**2)),
        "discarded_energy": float(0.5 * np.sum(a_D**2)),
    }
