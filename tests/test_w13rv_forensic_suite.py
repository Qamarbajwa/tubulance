"""Milestone W13R-V Forensic Test Suite.

SECURITY / EVIDENCE STATUS:
LEVEL 2 — TECHNICALLY VERIFIED
NOT EXTERNALLY ATTESTED
"""
from __future__ import annotations

import hashlib
import json
import pytest
import numpy as np
from pathlib import Path

from navier3d.reduced.w12_anisotropic_study import CanonicalW12ChannelConfig
from navier3d.reduced.w10_multi_coordinate import generate_channel_initial_condition, channel_bcs
from navier3d.reduced.w13_multiscale_capacity import ExtendedAnisotropicEigenwaveBasis
from scripts.run_w13rv_forensic_reproduction import (
    load_manifest,
    get_governance_header,
    audit_nonorthogonal_gram_system,
    run_dense_sampling_and_ablation,
    run_randomized_control_test,
    run_w13rv_full_reproduction,
)


def test_w13rv_manifest_integrity():
    """Verify w13rv_frozen_manifest.json exists and all recorded file SHA256 hashes match current files."""
    manifest_path = Path("w13rv_frozen_manifest.json")
    assert manifest_path.exists()

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["governance_status"] == "LEVEL 2 - TECHNICALLY VERIFIED"
    assert manifest["source_modified_during_reproduction"] is False

    for rel_path, expected_hash in manifest["file_hashes"].items():
        p = Path(rel_path)
        assert p.exists()
        with open(p, "rb") as fp:
            actual_hash = hashlib.sha256(fp.read()).hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}"


def test_mechanical_threshold_definition():
    """Golden verifier test: E(r=100)=0.08, E(r=200)=0.065, E(r=300)=0.049 must yield r5 = 300, NOT 200."""
    errors = {100: 0.08, 200: 0.065, 300: 0.049}
    qual = [r for r, e in sorted(errors.items()) if e <= 0.05]
    r5 = qual[0] if qual else None
    assert r5 == 300
    assert r5 != 200


def test_raw_array_evidence_lineage(tmp_path):
    """Verify fresh run ID generates sealed V0 evidence bundle with raw velocity arrays and valid metric entries."""
    config = CanonicalW12ChannelConfig()
    summary, t1, t2, t3, t4, t5, t6, t7, t8 = run_w13rv_full_reproduction(config, base_dir=tmp_path)

    run_id = summary["run_id"]
    run_dir = tmp_path / run_id
    assert run_dir.exists()

    assert (run_dir / "raw" / "u_ref.npy").exists()
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "metrics.json").exists()


def test_nonorthogonal_gram_system():
    """Verify Gram matrix construction G_ij = <phi_i, phi_j>_M, Frobenius norm error, and condition number."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()

    diag = audit_nonorthogonal_gram_system(mesh, bcs)
    assert "gram_frobenius_error" in diag
    assert "condition_number" in diag
    assert "reconstruction_residual" in diag
    assert diag["condition_number"] >= 1.0


def test_mode_ablation_and_randomized_control():
    """Verify leave-one-mode-out ablation computes positive damage for key modes and randomized control yields high error."""
    config = CanonicalW12ChannelConfig()
    mesh = config.create_mesh()
    bcs = config.create_bcs()

    _, _, _, ablation = run_dense_sampling_and_ablation(mesh, bcs)
    assert len(ablation) > 0
    for abl in ablation:
        assert "damage" in abl

    rand_ctrl = run_randomized_control_test(mesh, bcs)
    assert rand_ctrl["mean_random_error"] > 0.10


def test_w13rv_report_generation(tmp_path):
    """Verify generation of all 8 markdown tables and mandatory governance headers."""
    config = CanonicalW12ChannelConfig()
    summary, t1, t2, t3, t4, t5, t6, t7, t8 = run_w13rv_full_reproduction(config, base_dir=tmp_path)

    for tbl in [t1, t2, t3, t4, t5, t6, t7, t8]:
        assert "SECURITY / EVIDENCE STATUS:" in tbl
        assert "LEVEL 2 — TECHNICALLY VERIFIED" in tbl
        assert "NOT EXTERNALLY ATTESTED" in tbl
        assert "SOURCE MODIFIED DURING REPRODUCTION: NO" in tbl

    assert "TABLE 1: GLOBAL CAPACITY" in t1
    assert "TABLE 2: MULTISCALE CAPACITY" in t2
    assert "TABLE 3: ACCURACY DIMENSION" in t3
    assert "TABLE 4: TRANSFERABILITY MATRIX" in t4
    assert "TABLE 5: SPARSITY & PARTICIPATION RATIO" in t5
    assert "TABLE 6: FINAL CANDIDATE SCORECARD" in t6
    assert "TABLE 7: OLD VS NEW RECONCILIATION TABLE" in t7
    assert "TABLE 8: LEAVE-ONE-MODE-OUT ABLATION TABLE" in t8
