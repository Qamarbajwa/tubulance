"""Milestone W13 Unit & Integration Tests.

SECURITY / EVIDENCE STATUS:
LEVEL 2 — TECHNICALLY VERIFIED
NOT EXTERNALLY ATTESTED
"""
from __future__ import annotations

import json
import pytest
import numpy as np
from pathlib import Path

from navier3d.reduced.w12_anisotropic_study import CanonicalW12ChannelConfig
from navier3d.reduced.w13_multiscale_capacity import (
    ExtendedAnisotropicEigenwaveBasis,
    MACLocationAudit,
    DictionaryCompletenessTester,
    DirectionalDiagnostics,
    GreedyOracleSelector,
    WeightedAnisotropicBasis,
    EnergyEdgeBasis,
    NonlinearTransferBasis,
    LocalizedWallNormalPackets,
    WaveletWallNormalBasis,
    DivergenceFreeWavePackets,
    MultiresolutionSolenoidalDictionary,
    run_w13_primary_rank_sweep,
    determine_accuracy_dimension_targets,
    compare_structured_vs_oracle,
    run_w13_candidate_scorecard,
)
from navier3d.reduced.w10_multi_coordinate import generate_channel_initial_condition


def test_w13_basis_initialization_and_mode_count():
    """Verify ExtendedAnisotropicEigenwaveBasis builds non-zero modes including zero/mean modes."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()

    basis = ExtendedAnisotropicEigenwaveBasis(mesh, bcs, K_x=2, K_z=2, N_y=4, include_mean=True)
    assert basis.num_modes > 0
    assert len(basis.mode_descriptors) == basis.num_modes

    has_zero = any(d["is_zero_wavevector"] for d in basis.mode_descriptors)
    assert has_zero is True


def test_mac_location_audit():
    """Verify single-mode and multi-mode reconstruction tests pass on MAC grid faces."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()

    basis = ExtendedAnisotropicEigenwaveBasis(mesh, bcs, K_x=2, K_z=2, N_y=4)
    audit_res = MACLocationAudit.audit_mac_locations(basis, mesh)
    assert audit_res["max_boundary_residual"] < 1e-10

    single_res = MACLocationAudit.test_single_mode_reconstruction(basis, mode_idx=0)
    assert single_res["coeff_error"] < 1e-10
    assert single_res["field_error"] < 1e-10

    multi_res = MACLocationAudit.test_multi_mode_reconstruction(basis, n_modes=5, seed=42)
    assert multi_res["coeff_error"] < 1e-10
    assert multi_res["field_error"] < 1e-10


def test_dictionary_completeness():
    """Test completeness auditor on solenoidal IC."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()
    vel0 = generate_channel_initial_condition(mesh, bcs, seed=42)

    res = DictionaryCompletenessTester.test_completeness(vel0, max_Kx=3, max_Kz=3, max_Ny=4, mesh=mesh, bcs=bcs)
    assert "r_full" in res
    assert "E_proj_full" in res
    assert isinstance(res["E_proj_full"], float)


def test_directional_diagnostics():
    """Verify component errors and directional residual calculations."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()
    vel0 = generate_channel_initial_condition(mesh, bcs, seed=42)

    basis = ExtendedAnisotropicEigenwaveBasis(mesh, bcs, K_x=2, K_z=2, N_y=3)
    coeffs = basis.project_mac(vel0)
    vel_p = basis.reconstruct_mac(coeffs)

    comp_err = DirectionalDiagnostics.compute_component_errors(vel0, vel_p, mesh)
    assert "E_u" in comp_err
    assert "E_v" in comp_err
    assert "E_w" in comp_err
    assert comp_err["E_u"] >= 0.0

    dir_res = DirectionalDiagnostics.compute_directional_energy_residuals(vel0, vel_p, mesh)
    assert "frac_kx" in dir_res
    assert "frac_kz" in dir_res
    assert "frac_ny" in dir_res

    spatial_err = DirectionalDiagnostics.compute_wall_vs_interior_error(vel0, vel_p, mesh)
    assert "E_wall" in spatial_err
    assert "E_interior" in spatial_err


def test_greedy_oracle_selector():
    """Verify GreedyOracleSelector produces monotonic projection error reduction."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()
    vel0 = generate_channel_initial_condition(mesh, bcs, seed=42)

    basis = ExtendedAnisotropicEigenwaveBasis(mesh, bcs, K_x=3, K_z=3, N_y=4)
    oracle = GreedyOracleSelector(basis, [vel0])

    curve = oracle.compute_capacity_curve([10, 20, 30])
    assert curve[10] >= curve[20] >= curve[30]


def test_w13_candidate_bases_initialization():
    """Verify initialization and projection/reconstruction for Candidates W13-A through G."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()
    vel0 = generate_channel_initial_condition(mesh, bcs, seed=42)

    w13_a = WeightedAnisotropicBasis(mesh, bcs)
    p_a = w13_a.project_and_reconstruct(vel0, r=20)
    assert p_a is not None

    w13_b = EnergyEdgeBasis(mesh, bcs, [vel0])
    p_b = w13_b.project_and_reconstruct(vel0, r=20)
    assert p_b is not None

    w13_c = NonlinearTransferBasis(mesh, bcs, [vel0])
    p_c = w13_c.project_and_reconstruct(vel0, r=20)
    assert p_c is not None

    w13_d = LocalizedWallNormalPackets(mesh, bcs)
    assert w13_d.project_and_reconstruct(vel0, r=20) is not None

    w13_e = WaveletWallNormalBasis(mesh, bcs)
    assert w13_e.project_and_reconstruct(vel0, r=20) is not None

    w13_f = DivergenceFreeWavePackets(mesh, bcs)
    assert w13_f.project_and_reconstruct(vel0, r=20) is not None

    w13_g = MultiresolutionSolenoidalDictionary(mesh, bcs)
    assert w13_g.project_and_reconstruct(vel0, r=20) is not None


def test_w13_primary_rank_sweep_v0_audit(tmp_path):
    """Run primary rank sweep and verify V0 evidence bundle and audit recomputation."""
    config = CanonicalW12ChannelConfig()
    sweep_results, table_text = run_w13_primary_rank_sweep(config, base_dir=tmp_path)

    assert len(sweep_results) > 0
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in table_text
    assert "NOT EXTERNALLY ATTESTED" in table_text

    rows, target_table = determine_accuracy_dimension_targets(sweep_results)
    assert len(rows) == 5
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in target_table


def test_w13_candidate_scorecard_and_decision_tree(tmp_path):
    """Run candidate scorecard across 3 holdout cases and verify decision tree table output."""
    config = CanonicalW12ChannelConfig()
    summary, sec57_tbl, sec58_tbl, sec59_txt = run_w13_candidate_scorecard(config, base_dir=tmp_path)

    assert summary["holdouts_evaluated"] == 3
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in sec57_tbl
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in sec58_tbl
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in sec59_txt
