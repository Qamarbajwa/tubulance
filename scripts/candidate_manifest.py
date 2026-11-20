"""Candidate Verifier Manifest Generator for Human Review.

Generates candidate_verifier_manifest.json containing current verifier manifest SHA256
and individual python file hashes for human inspection and manual external root updates.

THIS SCRIPT DOES NOT WRITE TO EXTERNAL TRUST ROOTS.
THE HUMAN MUST MANUALLY UPDATE production_root.json OUTSIDE THE REPOSITORY.

Usage:
    python scripts/candidate_manifest.py [--output candidate_verifier_manifest.json]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from verifier.trusted_roots import LockManagerV2


def generate_candidate_manifest(output_path: str | Path = "candidate_verifier_manifest.json", verifier_dir: str | Path = "verifier") -> Path:
    """Generate candidate verifier manifest JSON for human review."""
    lock_v2 = LockManagerV2(verifier_dir=verifier_dir)
    overall_hash, file_hashes = lock_v2.compute_verifier_manifest_hash()

    manifest_data = {
        "schema": "V2.2_CANDIDATE",
        "verifier_version": "V2.2",
        "overall_verifier_manifest_sha256": overall_hash,
        "files": file_hashes,
        "notice": "HUMAN REVIEW REQUIRED: Copy 'overall_verifier_manifest_sha256' into external production_root.json manually.",
    }

    out_p = Path(output_path)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print("\n==================================================================")
    print("CANDIDATE VERIFIER MANIFEST GENERATED FOR HUMAN REVIEW")
    print("==================================================================")
    print(f"Overall Verifier Manifest SHA256: {overall_hash}")
    print(f"Candidate Manifest File:          {out_p.resolve()}")
    print("------------------------------------------------------------------")
    print("NOTICE: THIS TOOL DOES NOT MODIFY EXTERNAL TRUST ROOTS.")
    print("The human authority must manually inspect and update production_root.json")
    print("outside the repository.")
    print("==================================================================\n")

    return out_p


def main():
    parser = argparse.ArgumentParser(description="Candidate Verifier Manifest Generator")
    parser.add_argument("--output", type=str, default="candidate_verifier_manifest.json", help="Output path for candidate manifest")
    parser.add_argument("--verifier-dir", type=str, default="verifier", help="Verifier directory")
    args = parser.parse_args()

    generate_candidate_manifest(args.output, args.verifier_dir)


if __name__ == "__main__":
    main()
