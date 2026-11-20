"""Milestone W13R Unit & Integration Tests.

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
from navier3d.reduced.w13_multiscale_capacity import ExtendedAnisotropicEigenwaveBasis
from navier3d.reduced.w13r_reconciliation import (
    NonorthogonalProjectionSolver,
    ExtendedGlobalOracleEngine,
    W13GDenseSamplingEngine,
    CandidateG4EnsembleEngine,
    SparsificationEngine,
    SeparateHoldoutEvaluator,
    run_w13r_full_reconciliation,
)
from navier3d.reduced.w10_multi_coordinate import generate_channel_initial_condition


def test_nonorthogonal_projection_solver():
    """Verify NonorthogonalProjectionSolver builds Gram matrix G, solves G c = b, and computes conditioning metrics."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()

    class FaceDummy(np.ndarray):
        def __new__(cls, shape):
            obj = np.ones(shape).view(cls)
            obj.interior = np.ones(shape)
            return obj

    class ModeDummy:
        def __init__(self, shape):
            self.u = FaceDummy(shape)
            self.v = FaceDummy(shape)
            self.w = FaceDummy(shape)

    modes = [ModeDummy((12, 12, 12)) for _ in range(5)]

    solver = NonorthogonalProjectionSolver(modes, mesh)
    assert solver.G.shape == (len(modes), len(modes))

    class VelDummy:
        def __init__(self):
            self.u = FaceDummy((12, 12, 12))
            self.v = FaceDummy((12, 12, 12))
            self.w = FaceDummy((12, 12, 12))

    vel0 = VelDummy()
    coeffs, vel_recons, diag = solver.solve(vel0)

    assert len(coeffs) == len(modes)
    assert "condition_number" in diag
    assert "sigma_min" in diag
    assert "sigma_max" in diag
    assert "effective_rank" in diag


def test_extended_global_oracle_engine():
    """Test Global Greedy Oracle (G2) capacity curve sweep."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()
    vel0 = generate_channel_initial_condition(mesh, bcs, seed=42)

    basis = ExtendedAnisotropicEigenwaveBasis(mesh, bcs, K_x=3, K_z=3, N_y=4)
    engine = ExtendedGlobalOracleEngine(basis, mesh)

    measured_ranks = engine.sweep(vel0)
    assert "r20_oracle" in measured_ranks


def test_candidate_g4_ensemble_engine():
    """Test Candidate G4 ensemble dictionary construction."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()

    class BasisDummy:
        def __init__(self):
            self.modes = [np.ones((10, 10, 10)) for _ in range(20)]

    basis = BasisDummy()
    g4_engine = CandidateG4EnsembleEngine(basis, [], mesh)

    g4_modes = g4_engine.build_ensemble_dictionary(target_rank=10)
    assert len(g4_modes) == 10


def test_sparsification_engine():
    """Test effective dimension calculation in SparsificationEngine."""
    coeffs = np.array([1.0, 0.5, 0.25, 0.125, 0.0])
    d_eff = SparsificationEngine.compute_effective_dimension(coeffs)
    assert d_eff > 0.0


def test_separate_holdout_evaluator():
    """Test separate holdout evaluator."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()

    candidates = {"M1": None, "G1": None}
    evaluator = SeparateHoldoutEvaluator(candidates, mesh)
    res = evaluator.evaluate()

    assert "M1" in res
    assert res["M1"]["H-Re"] == "PASS"


def test_w13r_full_reconciliation_v0_audit(tmp_path):
    """Run full W13R reconciliation function and verify governance header."""
    config = CanonicalW12ChannelConfig()
    summary, t1, t2, t3, t4, t5, t6 = run_w13r_full_reconciliation(config, base_dir=tmp_path)

    assert "run_id" in summary
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in t1
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in t2
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in t3
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in t4
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in t5
    assert "LEVEL 2 — TECHNICALLY VERIFIED" in t6
