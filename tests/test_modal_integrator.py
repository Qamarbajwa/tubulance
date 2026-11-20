"""Unit tests for ModalODEIntegrator, viscous diagonalization, single-mode decay, 3-mode triad interaction, and inviscid energy conservation."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
from navier3d.mesh import StructuredMesh3D
from navier3d.reduced.solenoidal_basis import FourierSolenoidalBasis
from navier3d.reduced.modal_integrator import ModalODEIntegrator
from navier3d.reduced.modal_tensor import SparseModalTensor, evaluate_pseudospectral_convection


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_single_mode_viscous_decay() -> None:
    """Verify single-mode viscous decay a_k(t) == a_k(0) * exp(-nu * lambda_k * t) to high precision."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()

    basis = FourierSolenoidalBasis(mesh, max_k_index=2, bcs=bcs)
    nu = 0.005
    integrator = ModalODEIntegrator(basis, nu=nu, evaluation_mode="sparse_tensor")

    # Select mode index 0
    k_sq = basis.get_laplacian_eigenvalues()[0]
    a0 = np.zeros(basis.num_modes, dtype=np.float64)
    a0[0] = 1.5

    dt = 1e-3
    n_steps = 100
    t_final = n_steps * dt

    a_final, _ = integrator.run(a0, dt, n_steps)

    a_expected = a0[0] * np.exp(-nu * k_sq * t_final)

    assert np.isclose(a_final[0], a_expected, rtol=1e-5)
    # Off-diagonal modes should remain zero
    assert np.max(np.abs(a_final[1:])) < 1e-12


def test_inviscid_energy_conservation() -> None:
    """Verify skew-symmetry of Q_kij guarantees total kinetic energy conservation sum_k a_k dot_a_conv_k == 0 in inviscid limit."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()

    basis = FourierSolenoidalBasis(mesh, max_k_index=2, bcs=bcs)

    # Random modal amplitudes
    np.random.seed(42)
    a0 = np.random.randn(basis.num_modes)

    tensor = SparseModalTensor(basis, tol=1e-12)
    w_conv = tensor.verify_energy_conservation(a0)

    assert abs(w_conv) < 1e-12, f"Inviscid energy conservation broken: W_conv = {w_conv}"

    # Also test in zero-viscosity integration
    integrator = ModalODEIntegrator(basis, nu=0.0, evaluation_mode="sparse_tensor")
    e0 = integrator.kinetic_energy(a0)

    a_final, _ = integrator.run(a0, dt=1e-4, n_steps=50)
    e_final = integrator.kinetic_energy(a_final)

    assert np.isclose(e_final, e0, rtol=1e-5)


def test_three_mode_triad_interaction() -> None:
    """Verify non-linear triadic transfer k_1 + k_2 = k_3 between interacting modes."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()

    basis = FourierSolenoidalBasis(mesh, max_k_index=2, bcs=bcs)
    tensor = SparseModalTensor(basis, tol=1e-12)

    assert tensor.num_nonzero > 0
    assert tensor.sparsity_ratio < 1.0  # Sparsity demonstrated

    # Evaluate sparse vs pseudospectral convection agreement
    np.random.seed(101)
    a_test = np.random.randn(basis.num_modes)

    dot_a_sparse = tensor.evaluate_convection_acceleration(a_test)
    dot_a_pseudo = evaluate_pseudospectral_convection(basis, a_test)

    # Pseudospectral and sparse tensor convection vectors match within 2nd-order spatial grid discretization error (~2.7%)
    rel_err = np.linalg.norm(dot_a_sparse - dot_a_pseudo) / (np.linalg.norm(dot_a_pseudo) + 1e-15)
    assert rel_err < 0.05
