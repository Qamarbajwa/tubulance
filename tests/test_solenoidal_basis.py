"""Unit tests for solenoidal vector basis representations and pressure elimination theorem."""
import numpy as np
import pytest

from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType, apply_velocity_bc, apply_pressure_bc
from navier3d.decaying_turbulence import generate_matched_solenoidal_fields
from navier3d.fields import ScalarField, VelocityField
from navier3d.mesh import StructuredMesh3D
from navier3d.operators import divergence, gradient
from navier3d.reduced.solenoidal_basis import FourierSolenoidalBasis, PODSolenoidalBasis, cell_centers_to_mac, mac_to_cell_centers


def periodic_bcs() -> BoundaryConditionSet:
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    return BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)


def test_fourier_basis_solenoidality_and_orthonormality() -> None:
    """Verify FourierSolenoidalBasis divergence-free property, orthonormality, and Parseval identity."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()

    basis = FourierSolenoidalBasis(mesh, max_k_index=2, bcs=bcs)
    r = basis.num_modes

    assert r > 0

    # 1. Orthonormality G_ij = <phi_i, phi_j> = delta_ij
    G = basis.check_orthonormality()
    I_r = np.eye(r)

    assert np.allclose(G, I_r, atol=1e-12)

    # 2. Solenoidality: analytical divergence k . e == 0
    for n in range(r):
        kx, ky, kz = basis.get_wavevector(n)
        phi_u, phi_v, phi_w = basis.get_mode(n)
        k_vec = np.array([kx, ky, kz])
        if np.linalg.norm(k_vec) > 1e-10:
            idx = np.unravel_index(np.argmax(phi_u**2 + phi_v**2 + phi_w**2), phi_u.shape)
            e_vec = np.array([phi_u[idx], phi_v[idx], phi_w[idx]])
            dot_prod = float(np.dot(k_vec, e_vec))
            assert abs(dot_prod) < 1e-12, f"Mode {n} failed divergence free: k.e = {dot_prod}"

    # 3. Parseval Energy Identity: 0.5 * int ||u_r||^2 dV == 0.5 * sum_n a_n^2
    vel, _ = generate_matched_solenoidal_fields(mesh, mesh, bcs, k_peak=2.0, E0=1.0, seed=42)
    a = basis.project(vel)
    u_r, v_r, w_r = basis.reconstruct_cell_centers(a)

    e_reconstructed = float(0.5 * np.sum(u_r**2 + v_r**2 + w_r**2) * mesh.cell_volume)
    e_modal = float(0.5 * np.sum(a**2))

    assert np.isclose(e_reconstructed, e_modal, rtol=1e-12)


def test_pressure_elimination_theorem() -> None:
    """Verify mathematical & numerical pressure elimination <phi_k, grad p> = 0 for solenoidal modes."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()
    basis = FourierSolenoidalBasis(mesh, max_k_index=2, bcs=bcs)
    dV = mesh.cell_volume

    # Generate arbitrary smooth + random cell-centered pressure fields
    x = np.linspace(0, 2.0 * np.pi, 16, endpoint=False)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    p_smooth = ScalarField.zeros(mesh)
    p_smooth.interior[:] = np.sin(2.0 * X) * np.cos(3.0 * Y) + np.sin(4.0 * Z)

    apply_pressure_bc(p_smooth, bcs)

    # Gradient grad p on MAC faces
    grad_p = gradient(p_smooth, mesh)
    gp_u, gp_v, gp_w = mac_to_cell_centers(grad_p)

    for k in range(basis.num_modes):
        phi_u, phi_v, phi_w = basis.get_mode(k)
        inner_prod = float(np.sum(phi_u * gp_u + phi_v * gp_v + phi_w * gp_w) * dV)
        assert abs(inner_prod) < 1e-12, f"Mode {k} failed pressure elimination: <phi_k, grad p> = {inner_prod}"


def test_pod_basis_construction_and_energy_capture() -> None:
    """Verify PODSolenoidalBasis snapshot extraction, divergence-free inheritance, and energy spectrum."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi, n_ghost=1)
    bcs = periodic_bcs()

    # Generate 5 solenoidal snapshots
    snapshots = [
        generate_matched_solenoidal_fields(mesh, mesh, bcs, k_peak=2.0, E0=1.0, seed=s)[0]
        for s in range(5)
    ]

    pod_basis = PODSolenoidalBasis(snapshots, mesh, bcs)

    assert pod_basis.num_modes == 5

    # Check orthonormality of POD modes
    G = pod_basis.check_orthonormality()
    assert np.allclose(G, np.eye(5), atol=1e-12)

    # Check energy ratios
    r90 = pod_basis.required_modes_for_energy(0.90)
    r99 = pod_basis.required_modes_for_energy(0.99)

    assert 1 <= r90 <= 5
    assert 1 <= r99 <= 5
    assert r90 <= r99
