"""Unit test suite for Milestone P3-A Translation Diagnostic module."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.fields import VelocityField
from navier3d.boundary_conditions import apply_velocity_bc
from navier3d.reduced.w10_multi_coordinate import channel_bcs, generate_channel_initial_condition
from navier3d.reduced.solenoidal_basis import PODSolenoidalBasis
from navier3d.operators import divergence
from navier3d.reduced.w2_diagnostics import mac_velocity_norm, mac_velocity_diff_norm
from navier3d.reduced.p3a_translation_diagnostic import (
    fourier_shift_2d_xz,
    shift_velocity_field_xz,
    compute_cross_correlation_map_xz,
    find_optimal_periodic_alignment,
    compute_subspace_metrics,
    fourier_phase_amplitude_analysis,
)


@pytest.fixture
def channel_setup():
    """Create a standard 16x16x16 channel mesh and boundary conditions."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2.0 * np.pi, ly=2.0, lz=np.pi)
    bcs = channel_bcs()
    return mesh, bcs


def test_shift_identity(channel_setup):
    """Zero shift must return the exact field to machine precision."""
    mesh, bcs = channel_setup
    vel = generate_channel_initial_condition(mesh, bcs, seed=42)

    shifted = shift_velocity_field_xz(vel, mesh, 0.0, 0.0)
    diff = mac_velocity_diff_norm(vel, shifted, mesh)
    assert diff < 1e-12


def test_shift_preserves_solenoidality_and_walls(channel_setup):
    """Shifting in (x, z) must preserve discrete divergence and wall boundary conditions."""
    mesh, bcs = channel_setup
    vel = generate_channel_initial_condition(mesh, bcs, seed=101)

    div_orig = np.max(np.abs(divergence(vel, mesh).interior))
    assert div_orig < 1e-8

    # Shift by arbitrary subgrid amounts
    shifted = shift_velocity_field_xz(vel, mesh, 0.35 * mesh.dx, -0.72 * mesh.dz)

    div_shifted = np.max(np.abs(divergence(shifted, mesh).interior))
    assert div_shifted < 1e-8

    # Wall boundary check: v must remain zero at y=0 and y=Ly faces
    # v.interior shape is (nx, ny+1, nz) -> index 0 and -1 along y axis are the walls
    assert np.max(np.abs(shifted.v.interior[:, 0, :])) < 1e-12
    assert np.max(np.abs(shifted.v.interior[:, -1, :])) < 1e-12


def test_synthetic_shift_recovery(channel_setup):
    """The alignment solver must accurately recover known synthetic subgrid shifts."""
    mesh, bcs = channel_setup
    vel_A = generate_channel_initial_condition(mesh, bcs, seed=104)

    dx_true = float(2.35 * mesh.dx)
    dz_true = float(1.72 * mesh.dz)

    # Shift vel_A by dx_true, dz_true to create vel_B
    vel_B = shift_velocity_field_xz(vel_A, mesh, dx_true, dz_true)

    # Align vel_B back to vel_A (finds shift T(dx*, dz*) vel_B ≈ vel_A)
    res = find_optimal_periodic_alignment(vel_A, vel_B, mesh, subgrid=True)

    dx_expected = (-dx_true) % mesh.lx
    dz_expected = (-dz_true) % mesh.lz

    assert abs(res["dx_optimal"] - dx_expected) < 0.05 * mesh.dx
    assert abs(res["dz_optimal"] - dz_expected) < 0.05 * mesh.dz
    assert res["R_field"] < 0.01  # Should recover almost the exact field


def test_subspace_metrics_self(channel_setup):
    """Subspace distance between a basis and itself must be zero."""
    mesh, bcs = channel_setup
    vel1 = generate_channel_initial_condition(mesh, bcs, seed=1)
    vel2 = generate_channel_initial_condition(mesh, bcs, seed=2)
    vel3 = generate_channel_initial_condition(mesh, bcs, seed=3)

    basis = PODSolenoidalBasis([vel1, vel2, vel3], mesh, bcs=bcs, max_modes=3)
    metrics = compute_subspace_metrics(basis, basis, rank=3)

    assert metrics["d_chordal"] < 1e-6
    assert metrics["d_geodesic"] < 1e-6
    assert metrics["d_spectral_deg"] < 1e-6


def test_phase_amplitude_separation(channel_setup):
    """Pure spatial translation should induce large phase error but negligible amplitude error."""
    mesh, bcs = channel_setup
    vel = generate_channel_initial_condition(mesh, bcs, seed=201)
    vel_shifted = shift_velocity_field_xz(vel, mesh, 0.5 * mesh.lx, 0.25 * mesh.lz)

    res = fourier_phase_amplitude_analysis(vel, vel_shifted, mesh)

    # Pure translation preserves Fourier magnitude to high accuracy (< 0.1%)
    assert res["relative_amplitude_error"] < 1e-3
    assert res["mean_phase_error_deg"] > 10.0  # Phase error must be non-zero
