"""Create immutable Clean Scientific Manifest for Program NS-CONE-TERMINAL-OSCILLATION-1."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
import numpy as np
import scipy
import sklearn


def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    commit_sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    status_text = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
    diff_text = subprocess.run(["git", "diff", "--binary"], capture_output=True, text=True).stdout

    with open("git_status.txt", "w", encoding="utf-8") as f:
        f.write(status_text)

    with open("git_diff.patch", "w", encoding="utf-8") as f:
        f.write(diff_text)

    status_sha256 = compute_sha256(Path("git_status.txt"))
    diff_sha256 = compute_sha256(Path("git_diff.patch"))

    closure_files = [
        "src/navier3d/mesh.py",
        "src/navier3d/fields.py",
        "src/navier3d/boundary_conditions.py",
        "src/navier3d/convection.py",
        "src/navier3d/diffusion.py",
        "src/navier3d/pressure.py",
        "src/navier3d/projection.py",
        "src/navier3d/time_integrators.py",
        "src/navier3d/strain.py",
        "src/navier3d/decaying_turbulence.py",
        "src/navier3d/operators.py",
        "src/navier3d/_indexing.py",
        "src/navier3d/linear_solvers.py",
        "src/navier3d/experimental/__init__.py",
        "src/navier3d/experimental/lagrangian_tracking.py",
        "src/navier3d/experimental/geometry_features.py",
        "src/navier3d/experimental/th1_targets_and_models.py",
        "src/navier3d/experimental/th1_suite.py",
        "src/navier3d/experimental/th3_topology_features.py",
        "src/navier3d/experimental/th3_adaptive_models.py",
        "src/navier3d/experimental/th4_stress_models.py",
        "src/navier3d/experimental/th5_vorticity_math.py",
        "src/navier3d/experimental/th6_falsification_engine.py",
        "src/navier3d/experimental/th7_viscous_influx_math.py",
        "src/navier3d/experimental/th8_depletion_math.py",
        "src/navier3d/experimental/th9_persistence_math.py",
        "src/navier3d/experimental/th9r_direction_forensic.py",
        "src/navier3d/experimental/la1_multiscale_math.py",
        "src/navier3d/experimental/la1r_physical_scale_math.py",
        "src/navier3d/experimental/th10_burst_math.py",
        "src/navier3d/experimental/th10r_true_burst_math.py",
        "src/navier3d/experimental/ns_blowup1_rescaling_math.py",
        "src/navier3d/experimental/ns_blowup2_full_limit_math.py",
        "src/navier3d/experimental/bridge1_limit_rigidity_math.py",
        "src/navier3d/experimental/bridge1r_limit_consistency_math.py",
        "src/navier3d/experimental/theorem_gate1_audit_math.py",
        "src/navier3d/experimental/cone_bridge1_analytical_math.py",
        "src/navier3d/experimental/cone_lemma_proof1_math.py",
        "src/navier3d/experimental/cone_bv_fixed_reduction_math.py",
        "src/navier3d/experimental/cone_terminal_oscillation_math.py",
        "tests/test_th3_adaptive_suite.py",
        "tests/test_th4_stress_suite.py",
        "tests/test_th5_vorticity_suite.py",
        "tests/test_th6_falsification_suite.py",
        "tests/test_th7_viscous_suite.py",
        "tests/test_th8_depletion_suite.py",
        "tests/test_th9_persistence_suite.py",
        "tests/test_th9r_forensic_suite.py",
        "tests/test_la1_multiscale_suite.py",
        "tests/test_la1r_physical_suite.py",
        "tests/test_th10_burst_suite.py",
        "tests/test_th10r_true_suite.py",
        "tests/test_ns_blowup1_suite.py",
        "tests/test_ns_blowup2_suite.py",
        "tests/test_bridge1_limit_suite.py",
        "tests/test_bridge1r_limit_suite.py",
        "tests/test_theorem_gate1_suite.py",
        "tests/test_cone_bridge1_suite.py",
        "tests/test_cone_lemma_proof1_suite.py",
        "tests/test_cone_bv_fixed_reduction_suite.py",
        "tests/test_cone_terminal_oscillation_suite.py",
        "th1r_scientific_config.json",
    ]

    dependency_entries = []
    merkle_parts = []
    for rel_p in sorted(closure_files):
        p = Path(rel_p)
        assert p.exists(), f"Closure file missing: {p}"
        h = compute_sha256(p)
        sz = p.stat().st_size
        dependency_entries.append({
            "path": rel_p.replace("\\", "/"),
            "size_bytes": sz,
            "sha256": h,
        })
        merkle_parts.append(f"{rel_p}:{h}")

    overall_merkle = hashlib.sha256("\n".join(merkle_parts).encode("utf-8")).hexdigest()
    config_sha256 = compute_sha256(Path("th1r_scientific_config.json"))

    manifest = {
        "seal_id": "NS_CONE_TERMINAL_OSCILLATION1_PROOF_SEAL_V1",
        "timestamp_utc": "2026-08-20T04:45:00Z",
        "governance_state": "SEALED_FROZEN_FOR_NS_CONE_TERMINAL_OSCILLATION1_PROGRAM",
        "git": {
            "commit_sha": commit_sha,
            "status_file": "git_status.txt",
            "status_sha256": status_sha256,
            "diff_file": "git_diff.patch",
            "diff_sha256": diff_sha256,
        },
        "environment": {
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "scipy_version": scipy.__version__,
            "sklearn_version": sklearn.__version__,
            "os": platform.platform(),
            "cpu": platform.processor(),
        },
        "scientific_config_sha256": config_sha256,
        "dependency_closure": dependency_entries,
        "overall_closure_merkle_hash": overall_merkle,
    }

    manifest_path = Path("CONE_TERMINAL_OSCILLATION_CLEAN_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"CONE-TERMINAL-OSCILLATION-1 Clean manifest created at {manifest_path.resolve()}")
    print("Pre-run verification:")

    all_match = True
    for entry in dependency_entries:
        p = Path(entry["path"])
        cur_h = compute_sha256(p)
        if cur_h != entry["sha256"]:
            print(f"  MISMATCH: {p}")
            all_match = False
        else:
            print(f"  OK: {p}")

    print(f"PRE-RUN CLEAN SEAL MATCH = {'YES' if all_match else 'NO'}")


if __name__ == "__main__":
    main()
