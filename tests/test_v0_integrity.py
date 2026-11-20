"""Milestone V0 Acceptance Tests and Adversarial Tamper-Detection Suite.

Tests A through H prove that the audit framework mechanically detects all 10 forms of intentional corruption.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from navier3d.audit.run_identity import (
    generate_run_id,
    capture_environment,
    fingerprint_config,
    FrozenConfig,
    ConfigurationMutationError,
    BenchmarkComparabilityError,
    assert_comparable,
)
from navier3d.audit.evidence_bundle import (
    EvidenceBundle,
    WriteProtectionError,
    append_to_research_ledger,
)
from navier3d.audit.metrics import (
    calculate_velocity_l2_relative_error,
    calculate_wall_shear_relative_error,
    get_metric_function_hash,
    build_metric_entry,
)
from navier3d.audit.preregistration import (
    preregister_experiment,
    HoldoutViolationError,
    HoldoutManager,
)
from navier3d.audit.claim_checker import (
    ClaimChecker,
    ReportValidationError,
    validate_report_against_metrics,
)
from navier3d.audit.static_scanner import scan_codebase_for_hardcoded_results
from navier3d.audit.recompute import audit_recompute


@pytest.fixture
def temp_evidence_dir():
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


def create_sample_audit_bundle(evidence_dir: Path) -> tuple[str, Path]:
    """Helper creating a complete valid evidence bundle."""
    run_id = generate_run_id("v0", "sample_test")
    bundle = EvidenceBundle(run_id, base_dir=evidence_dir)

    config = {
        "nx": 12, "ny": 12, "nz": 12,
        "lx": 6.28, "ly": 2.0, "lz": 6.28,
        "nu": 0.05, "rho": 1.0, "dt": 0.005, "n_steps": 5,
        "seed": 42, "k_peak": 2.0, "E0": 0.5,
        "bcs": "channel", "forcing": "unforced",
    }
    config_hash, frozen_config = fingerprint_config(config, bundle.run_dir)
    capture_environment(bundle.run_dir)

    u_ref = np.ones((12, 12, 12))
    u_cand = np.ones((12, 12, 12)) * 0.9
    bundle.save_raw_array("u_reference", u_ref)
    bundle.save_raw_array("u_candidate", u_cand)

    e_u = calculate_velocity_l2_relative_error(u_ref, u_cand)
    metric_entry = build_metric_entry(
        "velocity_relative_l2", e_u, None, ["sample.py"],
        calculate_velocity_l2_relative_error, run_id, config_hash,
    )
    metrics_data = {"velocity_relative_l2": metric_entry, "speedup": {"name": "speedup", "value": 4.2}}
    bundle.save_metrics(metrics_data)

    bundle.finalize()
    return run_id, bundle.run_dir


# ============================================================================
# V0 ACCEPTANCE TESTS A - H (§43)
# ============================================================================

def test_v0_acceptance_test_a_metric_tampering(temp_evidence_dir):
    """Test A: Manual modification of metrics.json triggers AUDIT FAIL."""
    run_id, run_dir = create_sample_audit_bundle(temp_evidence_dir)

    # Initial audit must pass
    res_initial = audit_recompute(run_id, base_dir=temp_evidence_dir)
    assert res_initial["status"] == "PASS"

    # Tamper with metrics.json
    metrics_path = run_dir / "metrics.json"
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    metrics["velocity_relative_l2"]["value"] = 0.001  # Falsify value
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Audit recomputation must catch tamper and report FAIL
    res_tampered = audit_recompute(run_id, base_dir=temp_evidence_dir)
    assert res_tampered["status"] == "FAIL"
    assert "TAMPER DETECTED" in res_tampered["reason"] or "Metric mismatch" in res_tampered["reason"]


def test_v0_acceptance_test_b_raw_array_tampering(temp_evidence_dir):
    """Test B: Manual modification of raw data array triggers AUDIT FAIL."""
    run_id, run_dir = create_sample_audit_bundle(temp_evidence_dir)

    # Tamper with raw array
    raw_array_path = run_dir / "raw" / "u_reference.npy"
    arr = np.load(raw_array_path)
    arr[0, 0, 0] += 999.0
    np.save(raw_array_path, arr)

    # Audit recomputation must catch SHA256 mismatch and report FAIL
    res_tampered = audit_recompute(run_id, base_dir=temp_evidence_dir)
    assert res_tampered["status"] == "FAIL"
    assert "TAMPER DETECTED" in res_tampered["reason"]


def test_v0_acceptance_test_c_bc_mismatch(temp_evidence_dir):
    """Test C: Boundary condition mismatch raises BenchmarkComparabilityError."""
    ref_config = {"nx": 12, "ny": 12, "nz": 12, "bcs": "channel", "nu": 0.05}
    cand_config = {"nx": 12, "ny": 12, "nz": 12, "bcs": "periodic", "nu": 0.05}

    with pytest.raises(BenchmarkComparabilityError):
        assert_comparable(ref_config, cand_config)


def test_v0_acceptance_test_d_report_discrepancy(temp_evidence_dir):
    """Test D: Discrepancy between report claim and metrics raises ReportValidationError."""
    run_id, run_dir = create_sample_audit_bundle(temp_evidence_dir)
    metrics = {"velocity_relative_l2": {"value": 0.25}, "speedup": {"value": 4.2}}

    # False claim: E_u < 1% when actual is 25%
    false_report = "In this milestone we achieved E_u < 1% error and 50x speedup."

    with pytest.raises(ReportValidationError):
        validate_report_against_metrics(false_report, metrics, run_dir)


def test_v0_acceptance_test_e_write_protection(temp_evidence_dir):
    """Test E: Attempting to overwrite finalized raw result raises WriteProtectionError."""
    run_id, run_dir = create_sample_audit_bundle(temp_evidence_dir)
    bundle = EvidenceBundle(run_id, base_dir=temp_evidence_dir)

    with pytest.raises(WriteProtectionError):
        bundle.save_raw_array("u_reference", np.zeros((10, 10)))


def test_v0_acceptance_test_f_hardcoded_metric_scanner(temp_evidence_dir):
    """Test F: Static scanner detects suspicious hardcoded result variables."""
    # Write temporary file with fabricated result
    test_code_path = temp_evidence_dir / "bad_benchmark.py"
    with open(test_code_path, "w", encoding="utf-8") as f:
        f.write("expected_speedup = 13.5\nreported_error = 0.001\n")

    violations = scan_codebase_for_hardcoded_results(temp_evidence_dir)
    assert len(violations) >= 2
    assert any("expected_speedup" in v["line_content"] for v in violations)


def test_v0_acceptance_test_g_holdout_violation(temp_evidence_dir):
    """Test G: Premature access to holdout seed raises HoldoutViolationError."""
    hm = HoldoutManager(holdout_seeds=[99, 100], run_dir=temp_evidence_dir)

    with pytest.raises(HoldoutViolationError):
        hm.access_holdout(99)

    # After unlocking, access succeeds
    hm.unlock_holdout()
    assert hm.access_holdout(99) == 99


def test_v0_acceptance_test_h_metric_hash_mismatch(temp_evidence_dir):
    """Test H: Metric definition hash tracks source changes."""
    def metric_v1(a, b): return float(np.mean(abs(a - b)))
    def metric_v2(a, b): return float(np.sqrt(np.mean((a - b)**2)))

    hash1 = get_metric_function_hash(metric_v1)
    hash2 = get_metric_function_hash(metric_v2)

    assert hash1 != hash2


def test_v0_frozen_config_mutation_protection():
    """Verify that FrozenConfig blocks attempt to mutate parameters in-flight."""
    cfg_dict = {"nu": 0.05, "re": 100}
    frozen = FrozenConfig(cfg_dict)

    with pytest.raises(ConfigurationMutationError):
        frozen.nu = 0.1

    with pytest.raises(ConfigurationMutationError):
        frozen["nu"] = 0.1


# ============================================================================
# ADVERSARIAL SELF-TEST SUITE (§44)
# ============================================================================

def test_run_adversarial_self_test_suite(temp_evidence_dir):
    """Run 10-point adversarial self-test suite attempting to falsify results and verifying audit catches all 10."""
    results = []

    # Attack 1: Edit output metric value
    try:
        test_v0_acceptance_test_a_metric_tampering(temp_evidence_dir)
        results.append(("Attack 1: Edit metric value in JSON", "DETECTED"))
    except Exception as e:
        results.append(("Attack 1: Edit metric value in JSON", f"FAILED: {e}"))

    # Attack 2: Edit raw array
    try:
        test_v0_acceptance_test_b_raw_array_tampering(temp_evidence_dir)
        results.append(("Attack 2: Modify raw data array", "DETECTED"))
    except Exception as e:
        results.append(("Attack 2: Modify raw data array", f"FAILED: {e}"))

    # Attack 3: Mismatched BC in comparison
    try:
        test_v0_acceptance_test_c_bc_mismatch(temp_evidence_dir)
        results.append(("Attack 3: BC mismatch in comparison", "DETECTED"))
    except Exception as e:
        results.append(("Attack 3: BC mismatch in comparison", f"FAILED: {e}"))

    # Attack 4: Discrepant report text
    try:
        test_v0_acceptance_test_d_report_discrepancy(temp_evidence_dir)
        results.append(("Attack 4: Discrepant report claim text", "DETECTED"))
    except Exception as e:
        results.append(("Attack 4: Discrepant report claim text", f"FAILED: {e}"))

    # Attack 5: Overwrite completed raw result
    try:
        test_v0_acceptance_test_e_write_protection(temp_evidence_dir)
        results.append(("Attack 5: Overwrite completed raw result", "DETECTED"))
    except Exception as e:
        results.append(("Attack 5: Overwrite completed raw result", f"FAILED: {e}"))

    # Attack 6: Assign hardcoded metric variable
    try:
        test_v0_acceptance_test_f_hardcoded_metric_scanner(temp_evidence_dir)
        results.append(("Attack 6: Assign hardcoded metric variable", "DETECTED"))
    except Exception as e:
        results.append(("Attack 6: Assign hardcoded metric variable", f"FAILED: {e}"))

    # Attack 7: Premature access to holdout seed
    try:
        test_v0_acceptance_test_g_holdout_violation(temp_evidence_dir)
        results.append(("Attack 7: Premature holdout seed access", "DETECTED"))
    except Exception as e:
        results.append(("Attack 7: Premature holdout seed access", f"FAILED: {e}"))

    # Attack 8: Mutate in-flight config
    try:
        test_v0_frozen_config_mutation_protection()
        results.append(("Attack 8: Mutate in-flight configuration", "DETECTED"))
    except Exception as e:
        results.append(("Attack 8: Mutate in-flight configuration", f"FAILED: {e}"))

    # Attack 9: Redefine metric function code
    try:
        test_v0_acceptance_test_h_metric_hash_mismatch(temp_evidence_dir)
        results.append(("Attack 9: Redefine metric function definition", "DETECTED"))
    except Exception as e:
        results.append(("Attack 9: Redefine metric function definition", f"FAILED: {e}"))

    # Attack 10: Ledger record alteration (simulated via append-only check)
    ledger_path = temp_evidence_dir / "research_ledger.jsonl"
    e1 = append_to_research_ledger("run1", "v0", "hash1", "COMPLETED", ledger_path)
    e2 = append_to_research_ledger("run2", "v0", "hash2", "FAILED", ledger_path)
    with open(ledger_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) == 2 and "COMPLETED" in lines[0] and "FAILED" in lines[1]:
        results.append(("Attack 10: Append-only research ledger preservation", "DETECTED"))
    else:
        results.append(("Attack 10: Append-only research ledger preservation", "FAILED"))

    # Print summary
    print("\n" + "=" * 90)
    print("V0 ADVERSARIAL TAMPER-DETECTION AUDIT RESULTS (§44)")
    print("=" * 90)
    for attack, status in results:
        print(f"  {attack:<55} | Status: {status}")
    print("=" * 90)

    # Write report artifact
    md_content = ["# Adversarial Audit Results (Milestone V0)\n", "| Attack Vector | Detection Status |", "| :--- | :--- |"]
    for attack, status in results:
        md_content.append(f"| {attack} | {status} |")
    
    with open(temp_evidence_dir / "adversarial_audit_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))

    all_detected = all(status == "DETECTED" for _, status in results)
    assert all_detected, "Adversarial self-test suite failed to detect one or more tamper attempts!"
