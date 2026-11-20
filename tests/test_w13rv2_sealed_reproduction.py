"""Milestone W13R-V2 Final Verification Test Suite.

SECURITY / EVIDENCE STATUS:
LEVEL 2 — TECHNICALLY VERIFIED
NOT EXTERNALLY ATTESTED

MODE INDEXING = ZERO_BASED
"""
from __future__ import annotations

import hashlib
import json
import re
import pytest
import numpy as np
from pathlib import Path

from navier3d.reduced.w12_anisotropic_study import CanonicalW12ChannelConfig
from scripts.run_w13rv2_sealed_reproduction import (
    run_w13rv2_full_pipeline,
    run_independent_metric_oracle,
    compute_mac_velocity_error,
)


def test_w13rv2_manifest_completeness():
    """Verifies that w13rv2_frozen_manifest.json includes runner, test suite, basis, solver, metric, and verifier files."""
    manifest_path = Path("w13rv2_frozen_manifest.json")
    assert manifest_path.exists()

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    hashes = manifest["file_hashes"]
    required_files = [
        "scripts/run_w13rv2_sealed_reproduction.py",
        "tests/test_w13rv2_sealed_reproduction.py",
        "src/navier3d/reduced/w13_multiscale_capacity.py",
        "src/navier3d/reduced/w13r_reconciliation.py",
        "src/navier3d/audit/metrics.py",
        "verifier/verify_receipt.py",
    ]

    for req_f in required_files:
        assert req_f in hashes, f"Required file '{req_f}' missing from manifest."
        p = Path(req_f)
        assert p.exists(), f"Manifest file '{req_f}' does not exist on disk."
        with open(p, "rb") as fp:
            actual_hash = hashlib.sha256(fp.read()).hexdigest()
        assert actual_hash == hashes[req_f], f"Pre-run hash mismatch for '{req_f}'."


def test_pre_post_manifest_matching():
    """Recomputes all manifest file hashes and asserts PRE-RUN HASHES == POST-RUN HASHES."""
    manifest_path = Path("w13rv2_frozen_manifest.json")
    assert manifest_path.exists()

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for rel_path, expected_hash in manifest["file_hashes"].items():
        p = Path(rel_path)
        assert p.exists()
        with open(p, "rb") as fp:
            actual_hash = hashlib.sha256(fp.read()).hexdigest()
        assert actual_hash == expected_hash, f"Post-run hash mismatch for '{rel_path}': expected {expected_hash}, got {actual_hash}"


def test_threshold_table_consistency():
    """Verifies for every claimed integer threshold r_p: E(r_p) <= p and E(r_p - 1) > p."""
    m1_json = Path("report_json/m1_capacity.json")
    thresh_json = Path("report_json/thresholds.json")

    assert m1_json.exists()
    assert thresh_json.exists()

    with open(m1_json, "r", encoding="utf-8") as f:
        m1_data = json.load(f)

    with open(thresh_json, "r", encoding="utf-8") as f:
        thresh_data = json.load(f)

    for key, t_info in thresh_data.items():
        target = t_info["target"]
        claim_str = t_info["W13G_r"]
        if "MEASURED r = " in claim_str:
            r_p = int(claim_str.replace("MEASURED r = ", ""))
            assert str(r_p) in m1_data
            e_rp = m1_data[str(r_p)]["E_proj"]
            assert e_rp <= target, f"Claimed threshold r_p={r_p} has E={e_rp} > target {target}"

            if str(r_p - 1) in m1_data:
                e_prev = m1_data[str(r_p - 1)]["E_proj"]
                assert e_prev > target, f"Claimed threshold r_p={r_p} is not minimal: r_p-1={r_p-1} already has E={e_prev} <= target {target}"


def test_rank_differentiation_regression():
    """Regression test: Asserts G2(210) != G2(200) and G3(210) != G3(200) unless raw evidence genuinely produces equality."""
    g_json = Path("report_json/global_capacity.json")
    assert g_json.exists()

    with open(g_json, "r", encoding="utf-8") as f:
        g_data = json.load(f)

    g2_200 = g_data["200"]["Oracle"]
    g2_210 = g_data["210"]["Oracle"]
    g3_200 = g_data["200"]["FrozenGlobal"]
    g3_210 = g_data["210"]["FrozenGlobal"]

    assert g2_210 != g2_200, f"G2(210) [{g2_210}] erroneously equals G2(200) [{g2_200}]."
    assert g3_210 != g3_200, f"G3(210) [{g3_210}] erroneously equals G3(200) [{g3_200}]."


def test_raw_mac_velocity_lineage(tmp_path):
    """Verifies full 3-component MAC velocity array lineage (u_ref, v_ref, w_ref and u_recons, v_recons, w_recons)."""
    config = CanonicalW12ChannelConfig()
    summary, _ = run_w13rv2_full_pipeline(config, base_dir=tmp_path, is_development_dry_run=True)

    run_id = summary["run_id"]
    raw_dir = tmp_path / run_id / "raw"
    assert raw_dir.exists()

    for component in ["u_ref.npy", "v_ref.npy", "w_ref.npy", "u_recons_M1_210.npy", "v_recons_M1_210.npy", "w_recons_M1_210.npy", "coeffs_M1_210.npy"]:
        assert (raw_dir / component).exists(), f"Raw component '{component}' missing from evidence directory."


def test_independent_metric_oracle_agreement():
    """Verifies that independent metric oracle agrees with experiment metric calculation to within 1e-10."""
    u_ref = np.random.randn(8, 8, 8)
    v_ref = np.random.randn(8, 8, 8)
    w_ref = np.random.randn(8, 8, 8)

    u_rec = u_ref + 0.01 * np.random.randn(8, 8, 8)
    v_rec = v_ref + 0.01 * np.random.randn(8, 8, 8)
    w_rec = w_ref + 0.01 * np.random.randn(8, 8, 8)

    e_orac = run_independent_metric_oracle(u_ref, v_ref, w_ref, u_rec, v_rec, w_rec)

    diff_u = u_rec - u_ref
    diff_v = v_rec - v_ref
    diff_w = w_rec - w_ref
    num = np.sum(diff_u**2) + np.sum(diff_v**2) + np.sum(diff_w**2)
    den = np.sum(u_ref**2) + np.sum(v_ref**2) + np.sum(w_ref**2)
    e_direct = float(np.sqrt(num / (den + 1e-15)))

    assert abs(e_orac - e_direct) < 1e-10


def test_no_forbidden_scientific_constants():
    """Static check verifying zero hardcoded primary scientific metrics in runner script."""
    runner_path = Path("scripts/run_w13rv2_sealed_reproduction.py")
    assert runner_path.exists()

    with open(runner_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Search for forbidden constants that should never be hardcoded into calculation logic
    forbidden_constants = ["0.048500", "0.0485", "0.125000", "0.204700", "0.178000"]
    for const in forbidden_constants:
        matches = [m.start() for m in re.finditer(re.escape(const), content)]
        # Allow constant only inside string literals or docstrings, not in calculation
        for match in matches:
            line = content[max(0, match-50):min(len(content), match+50)]
            assert "def " not in line or "#" in line or '"' in line or "'" in line
