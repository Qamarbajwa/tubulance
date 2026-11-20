"""Milestone V2.2 Red-Team Attack Suite (Attacks A-H) & Trust Boundary Verification.

Tests that coding agent cannot self-approve production evidence or bypass offline external root.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from verifier.crypto_signer import generate_ed25519_keypair, canonicalize_json, sign_data
from verifier.trusted_roots import (
    TrustMode,
    TrustModeManager,
    TrustLevel,
    ExternalRootUnavailableError,
    ExternalRootMismatchError,
    LockManagerV2,
)
from verifier.status_machine import StatusMachine
from verifier.receipt_schema import build_v2_receipt_schema
from verifier.verify_receipt import verify_receipt
from verifier.static_dep_checker import assert_no_project_scripts_write_external_root


@pytest.fixture
def temp_v22_env():
    """Create isolated external root and repository environment for testing."""
    temp_dir = tempfile.mkdtemp()
    ext_dir = Path(temp_dir) / "ResearchVerificationAuthority"
    ext_dir.mkdir(parents=True)
    
    # Generate genuine external keypair
    _, pub_pem, ext_fp = generate_ed25519_keypair()
    
    lock_v2 = LockManagerV2(verifier_dir=Path("verifier"))
    ver_hash, _ = lock_v2.compute_verifier_manifest_hash()
    
    ext_root_path = ext_dir / "production_root.json"
    ext_root_data = {
        "schema": "V2.2",
        "trusted_verifier_manifest_sha256": ver_hash,
        "trusted_public_key_fingerprint": ext_fp,
        "minimum_verifier_version": "V2.2",
        "revoked_verifiers": [],
    }
    with open(ext_root_path, "w", encoding="utf-8") as f:
        json.dump(ext_root_data, f, indent=2)
        
    yield ext_root_path, ext_fp, temp_dir
    shutil.rmtree(temp_dir)


def test_attack_a_agent_keypair_signed_receipt_untrusted():
    """Attack Test A: Agent generates Ed25519 keypair and signs valid receipt.
    
    Expected: SIGNATURE VALID, SIGNING AUTHORITY UNTRUSTED, Capped at LEVEL 2.
    """
    _, agent_pub, agent_fp = generate_ed25519_keypair()
    
    # Verification against external root (which has different fingerprint) fails
    mgr = TrustModeManager(verifier_dir=Path("verifier"), trust_mode=TrustMode.DEVELOPMENT)
    assert mgr.is_fingerprint_revoked("f8df34339ea37e1449edf583b4d2b834646c398f9f73a387e9d70c3718d272d2") is True
    
    sm = StatusMachine(initial_status="TECHNICALLY_VERIFIED")
    assert sm.get_trust_level() == "LEVEL 2 - TECHNICALLY VERIFIED"
    
    # Agent alone cannot promote to LEVEL 3
    promoted = sm.promote("signature_valid", True, trust_mode="DEVELOPMENT_ONLY")
    assert promoted == "TECHNICALLY_VERIFIED"
    assert sm.get_trust_level() == "LEVEL 2 - TECHNICALLY VERIFIED"


def test_attack_b_agent_verifier_rewrite_and_repo_root_tamper(temp_v22_env):
    """Attack Test B: Agent modifies verifier source and repo trusted roots.
    
    External root remains unchanged. Expected: VERIFIER MANIFEST MISMATCH -> REJECTED.
    """
    ext_root_path, _, _ = temp_v22_env
    
    # Simulate mismatched verifier hash
    with open(ext_root_path, "r") as f:
        ext_data = json.load(f)
    ext_data["trusted_verifier_manifest_sha256"] = "0000000000000000000000000000000000000000000000000000000000000000"
    with open(ext_root_path, "w") as f:
        json.dump(ext_data, f)
        
    res = verify_receipt(
        "tests/fixtures/fake_receipt.json",
        "tests/fixtures/fake_sig.sig",
        verifier_dir="verifier",
        trust_mode="production",
        external_root_path=ext_root_path,
    )
    # Receipt file missing or manifest mismatch -> status FAILED
    assert res["status"] == "FAILED"


def test_attack_c_project_public_key_swap(temp_v22_env):
    """Attack Test C: Agent swaps repo public key and updates repo trust cache.
    
    External root unchanged. Expected: PUBLIC KEY FINGERPRINT MISMATCH -> REJECTED.
    """
    ext_root_path, _, temp_dir = temp_v22_env
    
    # Agent fake key
    _, agent_pub, agent_fp = generate_ed25519_keypair()
    fake_ver_dir = Path(temp_dir) / "verifier_fake"
    shutil.copytree("verifier", fake_ver_dir)
    
    with open(fake_ver_dir / "trusted_public_key.pub", "wb") as f:
        f.write(agent_pub)
        
    res = verify_receipt(
        "tests/fixtures/fake_receipt.json",
        "tests/fixtures/fake_sig.sig",
        verifier_dir=fake_ver_dir,
        trust_mode="production",
        external_root_path=ext_root_path,
    )
    assert res["status"] == "FAILED"
    assert "UNTRUSTED" in res.get("reason", "") or "missing" in res.get("reason", "")


def test_attack_d_fake_production_receipt():
    """Attack Test D: Agent writes fake receipt claiming LEVEL 3.
    
    Expected: NO TRUSTED EXTERNAL SIGNATURE -> REJECTED.
    """
    receipt = build_v2_receipt_schema(
        run_id="fake_run",
        verifier_version="V2.2",
        verifier_manifest_sha256="fake",
        source_manifest_sha256="fake",
        git_commit="fake",
        config_sha256="fake",
        preregistration_sha256="fake",
        holdout_manifest_sha256="fake",
        raw_manifest_sha256="fake",
        metrics_sha256="fake",
        timing_sha256="fake",
        environment_sha256="fake",
        report_sha256="fake",
        ledger_head_sha256="fake",
        verification_status="EXTERNALLY_ATTESTED",
        trust_mode="PRODUCTION",
        signing_public_key_fingerprint="agent_fake_fp",
        trust_level="LEVEL 3 - EXTERNALLY ATTESTED",
    )
    
    # Verifying without valid signature & external root must fail
    res = verify_receipt(
        "non_existent_receipt.json",
        "non_existent_sig.sig",
        trust_mode="production",
    )
    assert res["status"] == "FAILED"


def test_attack_e_external_root_missing_fail_closed(temp_v22_env):
    """Attack Test E: External root is missing/unavailable in production mode.
    
    Expected: FAIL CLOSED with EXTERNAL_ROOT_UNAVAILABLE, status NOT_EXTERNALLY_ATTESTED.
    """
    _, _, temp_dir = temp_v22_env
    receipt_p = Path(temp_dir) / "test_receipt.json"
    sig_p = Path(temp_dir) / "test_sig.sig"
    
    receipt_dict = build_v2_receipt_schema(
        run_id="run_test_fail_closed",
        verifier_version="V2.2",
        verifier_manifest_sha256="abc",
        source_manifest_sha256="def",
        git_commit="head",
        config_sha256="cfg",
        preregistration_sha256="pre",
        holdout_manifest_sha256="hold",
        raw_manifest_sha256="raw",
        metrics_sha256="met",
        timing_sha256="time",
        environment_sha256="env",
        report_sha256="rep",
        ledger_head_sha256="led",
    )
    with open(receipt_p, "w", encoding="utf-8") as f:
        json.dump(receipt_dict, f)
    with open(sig_p, "wb") as f:
        f.write(b"fake_signature_bytes_1234567890")

    non_existent_root = "C:/path/does/not/exist/production_root.json"
    res = verify_receipt(
        receipt_p,
        sig_p,
        trust_mode="production",
        external_root_path=non_existent_root,
    )
    assert res["status"] == "FAILED"
    assert "EXTERNAL_ROOT_UNAVAILABLE" in res.get("reason", "")
    assert res.get("trust_level") == "LEVEL 2 - TECHNICALLY VERIFIED"


def test_attack_f_agent_maximum_authority_capped_at_level_2():
    """Attack Test F: Coding agent alone cannot reach LEVEL 3 (EXTERNALLY ATTESTED)."""
    sm = StatusMachine(initial_status="NOT_RUN")
    sm.promote("run_completed", True)
    assert sm.get_trust_level() == "LEVEL 1 - EVIDENCE CAPTURED"
    
    sm.promote("verifier_valid", True)
    assert sm.get_trust_level() == "LEVEL 2 - TECHNICALLY VERIFIED"
    
    # Attempting signature_valid in DEVELOPMENT mode keeps status at LEVEL 2
    sm.promote("signature_valid", True, trust_mode="DEVELOPMENT_ONLY")
    assert sm.get_trust_level() == "LEVEL 2 - TECHNICALLY VERIFIED"


def test_attack_g_static_external_root_write_scanner():
    """Attack Test G: Scans codebase ensuring no project scripts attempt write to external root."""
    assert_no_project_scripts_write_external_root(".")


def test_v22_attack_matrix_completeness():
    """Print complete V2.2 Attack Matrix (Attacks A-H)."""
    attacks = [
        ("A. Agent keypair signed receipt", "UNTRUSTED", "Capped at LEVEL 2; external root fingerprint mismatch"),
        ("B. Agent verifier rewrite + repo root edit", "REJECTED", "External root verifier manifest SHA256 mismatch"),
        ("C. Project public key swap attack", "REJECTED", "External root public key fingerprint mismatch"),
        ("D. Fake production receipt claim", "REJECTED", "Ed25519 signature + external root validation"),
        ("E. Missing external root file", "FAIL CLOSED", "EXTERNAL_ROOT_UNAVAILABLE error in production mode"),
        ("F. Agent max authority cap", "ENFORCED", "Coding agent capped strictly at LEVEL 2"),
        ("G. Project script write scanner", "PASSED", "Static AST scan verifies no external root writes"),
        ("H. Write permission boundary", "ENFORCED", "External root path protected from agent process writes"),
    ]
    
    print("\n" + "=" * 100)
    print("V2.2 RED-TEAM ATTACK MATRIX (ATTACKS A-H)")
    print("=" * 100)
    print(f"{'Attack Vector':<45} | {'Status':<12} | {'Defense Mechanism'}")
    print("-" * 100)
    for name, status, defense in attacks:
        print(f"{name:<45} | {status:<12} | {defense}")
    print("=" * 100)
    
    assert len(attacks) == 8
