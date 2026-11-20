"""Unit tests for Program NS-CONE-BRIDGE-1: High-Vorticity Time-Slice Cone Geometry & Flux Audit."""
from __future__ import annotations

import numpy as np
import pytest

from navier3d.mesh import StructuredMesh3D
from navier3d.boundary_conditions import periodic_bcs
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.experimental.cone_bridge1_analytical_math import (
    TimeSlicePairwiseResult,
    StructureDisorderResult,
    AbsoluteVorticityFluxResult,
    compute_projective_cross_product,
    audit_time_slice_pairwise_directions,
    audit_internal_vs_external_disorder,
    audit_absolute_vorticity_flux,
)


def test_cone_bridge1_pairwise_and_flux_suite():
    """Verify time-slice pairwise direction analysis and absolute vorticity flux diagnostics."""
    mesh = StructuredMesh3D(nx=16, ny=16, nz=16, lx=2*np.pi, ly=2*np.pi, lz=2*np.pi, n_ghost=2)
    bcs = periodic_bcs()
    v0 = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=42)

    center = np.array([np.pi, np.pi, np.pi])

    # Test projective cross product
    xi1 = np.array([1.0, 0.0, 0.0])
    xi2 = np.array([0.0, 1.0, 0.0])
    assert np.isclose(compute_projective_cross_product(xi1, xi2), 1.0)
    assert np.isclose(compute_projective_cross_product(xi1, -xi1), 0.0)

    # Test time-slice pairwise audit
    pair_res = audit_time_slice_pairwise_directions(
        velocity=v0,
        mesh=mesh,
        center_pt=center,
        nu=0.01,
        R_cylinder=2.0,
        threshold_tau=0.75,
        flow_id="test_flow_iso",
        time_val=0.0,
    )
    assert pair_res.num_points >= 1
    assert 0.0 <= pair_res.sup_pairwise_cross <= 1.0
    assert 0.0 <= pair_res.mean_pairwise_angle_deg <= 90.0

    # Test internal vs external disorder
    disorder_res = audit_internal_vs_external_disorder(
        velocity=v0,
        mesh=mesh,
        center_pt=center,
        nu=0.01,
        R_cylinder=2.0,
        threshold_tau=0.50,
        flow_id="test_flow_iso",
        time_val=0.0,
    )
    assert disorder_res.num_components >= 1
    assert 0.0 <= disorder_res.mean_internal_disorder_deg <= 90.0
    assert 0.0 <= disorder_res.external_disorder_deg <= 90.0

    # Test absolute vorticity flux
    flux_res = audit_absolute_vorticity_flux(
        velocity=v0,
        mesh=mesh,
        center_pt=center,
        nu=0.01,
        R_radius=1.5,
        flow_id="test_flow_iso",
        time_val=0.0,
    )
    assert flux_res.abs_vorticity_flux >= 0.0
    assert flux_res.axial_vorticity_flux >= 0.0
    assert flux_res.flux_bound_ratio >= 1.0
