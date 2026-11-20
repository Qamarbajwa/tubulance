"""External Verified Launcher and Child-Process Trust Boundary.

Implements Sections 11, 12, 13, 14, 15, 16, 32, 33 of Milestone V1.
Usage: python verified_run.py --script scripts/run_v0_audited_benchmark.py --milestone v1 --name channel_test
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

from verifier.trusted_roots import LockManagerV2
from verifier.verify_run import verify_run


def compute_source_merkle_manifest(source_dir: str | Path = "src/navier3d") -> dict:
    """Compute Merkle-like manifest of source tree BEFORE launching benchmark."""
    source_dir = Path(source_dir)
    entries = []

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith((".py", ".json", ".toml", ".yaml")):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(source_dir).as_posix()
                with open(file_path, "rb") as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content).hexdigest()
                entries.append({
                    "path": rel_path,
                    "size_bytes": len(content),
                    "sha256": file_hash,
                })

    entries.sort(key=lambda x: x["path"])
    manifest_str = json.dumps(entries, indent=2)
    overall_hash = hashlib.sha256(manifest_str.encode("utf-8")).hexdigest()

    return {
        "overall_source_hash": overall_hash,
        "files": entries,
    }


def main():
    parser = argparse.ArgumentParser(description="External Verified Launcher for Milestone V1")
    parser.add_argument("--script", type=str, default="scripts/run_v0_audited_benchmark.py")
    parser.add_argument("--milestone", type=str, default="v1")
    parser.add_argument("--name", type=str, default="audited_run")
    args = parser.parse_args()

    # 1. Cryptographically Secure Run ID Generation
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    crypto_suffix = secrets.token_hex(6)
    run_id = f"{now_str}__{args.milestone}__{args.name}__{crypto_suffix}"

    run_dir = Path("evidence") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # 2. Capture Source Merkle Manifest BEFORE Launch
    source_manifest = compute_source_merkle_manifest()
    with open(run_dir / "source_manifest.json", "w", encoding="utf-8") as f:
        json.dump(source_manifest, f, indent=2)

    # 3. Verify Verifier Lock against External Trusted Roots
    lock_mgr = LockManagerV2()
    lock_mgr.verify_against_trusted_roots()

    print(f"==================================================")
    print(f"LAUNCHING VERIFIED CHILD PROCESS")
    print(f"  Run ID: {run_id}")
    print(f"  Source Merkle Hash: {source_manifest['overall_source_hash'][:12]}...")
    print(f"==================================================")

    # 4. Launch Child Process & Measure External Wall-Clock Time
    t0_ext = time.perf_counter()
    env = os.environ.copy()
    env["V1_RUN_ID"] = run_id

    proc = subprocess.Popen([sys.executable, args.script], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    t1_ext = time.perf_counter()
    ext_wall_time = t1_ext - t0_ext

    # Save command, stdout, stderr
    with open(run_dir / "command.txt", "w", encoding="utf-8") as f:
        f.write(f"Executable: {sys.executable}\nScript: {args.script}\nExit Code: {proc.returncode}\n")
    with open(run_dir / "stdout.log", "w", encoding="utf-8") as f:
        f.write(stdout)
    with open(run_dir / "stderr.log", "w", encoding="utf-8") as f:
        f.write(stderr)

    if proc.returncode != 0:
        print(f"CHILD PROCESS FAILED with exit code {proc.returncode}")
        print(stderr)
        sys.exit(proc.returncode)

    print(f"Child process finished in {ext_wall_time:.4f}s. Invoking Independent Verifier...")

    # 5. Invoke Independent Verifier
    receipt = verify_run(run_id)
    if receipt.get("verification_status") in ("TECHNICALLY_VERIFIED", "VERIFIED", "EXTERNALLY_ATTESTED") or receipt.get("status") == "VERIFIED":
        print(f"\n==========================================")
        print(f"VERIFICATION RECEIPT ISSUED: {receipt.get('verification_status', 'VERIFIED')}")
        print(f"  Receipt ID: {run_id}")
        print(f"==========================================\n")
    else:
        print(f"\n==========================================")
        print(f"VERIFICATION FAIL: {receipt.get('reason')}")
        print(f"==========================================\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
