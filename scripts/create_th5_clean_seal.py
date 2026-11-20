"""Create immutable Clean Scientific Manifest for Milestone TH5."""
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
    # 1. Capture git state BEFORE manifest creation
    commit_sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    status_text = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
    diff_text = subprocess.run(["git", "diff", "--binary"], capture_output=True, text=True).stdout

    with open("git_status.txt", "w", encoding="utf-8") as f:
        f.write(status_text)

    with open("git_diff.patch", "w", encoding="utf-8") as f:
        f.write(diff_text)

    status_sha256 = compute_sha256(Path("git_status.txt"))
    diff_sha256 = compute_sha256(Path("git_diff.patch"))

    # 2. Dependency closure for TH5
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
        "tests/test_th3_adaptive_suite.py",
        "tests/test_th4_stress_suite.py",
        "tests/test_th5_vorticity_suite.py",
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
        "seal_id": "TH5_REGULARITY_STRUCTURE_SEAL_V1",
        "timestamp_utc": "2026-08-16T18:00:00Z",
        "governance_state": "SEALED_FROZEN_FOR_TH5_AUTONOMOUS_PROGRAM",
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

    manifest_path = Path("TH5_CLEAN_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"TH5 Clean manifest created at {manifest_path.resolve()}")
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
