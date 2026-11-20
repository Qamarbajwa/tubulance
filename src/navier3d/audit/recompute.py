"""Full Audit Recomputation CLI and Tamper Verifier.

Implements Sections 23, 24, 36, 40 of Milestone V0.
Usage: python -m navier3d.audit.recompute <run_id>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np

from .metrics import (
    calculate_velocity_l2_relative_error,
    calculate_wall_shear_relative_error,
)


def audit_recompute(run_id: str, base_dir: str | Path = "evidence") -> Dict[str, Any]:
    """Recompute metrics from raw data, verify SHA256 hashes, and validate manifest."""
    run_dir = Path(base_dir) / run_id
    if not run_dir.exists():
        return {"status": "FAIL", "reason": f"Run directory '{run_dir}' does not exist"}

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return {"status": "FAIL", "reason": f"Manifest '{manifest_path}' missing"}

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 1. SHA256 Hash Verification
    for entry in manifest.get("files", []):
        file_path = run_dir / entry["filename"]
        if not file_path.exists():
            return {"status": "FAIL", "reason": f"Missing file '{entry['filename']}' listed in manifest"}

        with open(file_path, "rb") as f:
            content = f.read()
            actual_hash = hashlib.sha256(content).hexdigest()

        if actual_hash != entry["sha256"]:
            return {
                "status": "FAIL",
                "reason": (
                    f"TAMPER DETECTED in file '{entry['filename']}': "
                    f"expected sha256={entry['sha256'][:10]}..., got actual={actual_hash[:10]}..."
                ),
            }

    # 2. Metrics Verification
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return {"status": "FAIL", "reason": f"Metrics file '{metrics_path}' missing"}

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # Recompute metrics if raw velocity arrays exist
    raw_u_ref_path = run_dir / "raw" / "u_reference.npy"
    raw_u_cand_path = run_dir / "raw" / "u_candidate.npy"

    if raw_u_ref_path.exists() and raw_u_cand_path.exists():
        u_ref = np.load(raw_u_ref_path)
        u_cand = np.load(raw_u_cand_path)
        recomputed_e_u = calculate_velocity_l2_relative_error(u_ref, u_cand)

        stored_e_u = metrics.get("velocity_relative_l2", {}).get("value")
        if stored_e_u is not None:
            if abs(recomputed_e_u - stored_e_u) > 1e-10:
                return {
                    "status": "FAIL",
                    "reason": f"Metric mismatch for velocity_relative_l2: stored={stored_e_u}, recomputed={recomputed_e_u}",
                }

    return {"status": "PASS", "run_id": run_id, "files_verified": len(manifest.get("files", []))}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m navier3d.audit.recompute <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]
    res = audit_recompute(run_id)
    if res["status"] == "PASS":
        print(f"\n==========================================")
        print(f"AUDIT PASS: {res['run_id']} ({res['files_verified']} files verified)")
        print(f"==========================================\n")
        return
    else:
        print(f"\n==========================================")
        print(f"AUDIT FAIL: {res.get('reason')}")
        print(f"==========================================\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
