"""External Authority Tool signing receipts using Ed25519 private key outside repository.

Implements Sections 5, 7, 9 of Milestone V2.
Usage: python scripts/external_sign_receipt.py <run_id> --key <path_to_private_key_pem>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from verifier.crypto_signer import sign_data, canonicalize_json
from verifier.receipt_schema import compute_receipt_canonical_hash


def sign_receipt_for_run(run_id: str, private_key_pem_path: str | Path, base_dir: str | Path = "evidence", trust_mode: str = "development") -> str:
    """Sign receipt for a verified run using an external Ed25519 private key."""
    run_dir = Path(base_dir) / run_id
    receipt_path = run_dir / "verification_receipt.json"

    if not receipt_path.exists():
        raise FileNotFoundError(f"Unsigned receipt '{receipt_path}' not found!")

    with open(receipt_path, "r", encoding="utf-8") as f:
        receipt_data = json.load(f)

    with open(private_key_pem_path, "rb") as f:
        private_pem = f.read()

    if trust_mode == "production":
        private_key = serialization.load_pem_private_key(private_pem, password=None)
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        fingerprint = hashlib.sha256(public_pem).hexdigest()

        try:
            with open("verifier/revoked_identities.json", "r", encoding="utf-8") as f:
                revoked = json.load(f)
            revoked_fps = [r["fingerprint"] for r in revoked.get("revoked_development_identities", [])]
        except (FileNotFoundError, json.JSONDecodeError):
            revoked_fps = []
            
        if fingerprint in revoked_fps:
            raise ValueError("REVOKED IDENTITY: Cannot sign with a revoked development key in production mode")
            
        receipt_data["trust_mode"] = "PRODUCTION"
        receipt_data["signing_public_key_fingerprint"] = fingerprint
        receipt_data["verification_status"] = "EXTERNALLY_ATTESTED"
    else:
        receipt_data["trust_mode"] = "DEVELOPMENT_ONLY"
        receipt_data["signing_public_key_fingerprint"] = ""
        receipt_data["verification_status"] = "TECHNICALLY_VERIFIED"

    canonical_bytes = canonicalize_json(receipt_data)

    sig_bytes = sign_data(canonical_bytes, private_pem)

    # Write back updated receipt and signature file
    with open(receipt_path, "w", encoding="utf-8") as f:
        f.write(canonical_bytes.decode("utf-8"))

    sig_path = run_dir / "verification_receipt.sig"
    with open(sig_path, "wb") as f:
        f.write(sig_bytes)

    return str(sig_path)


def main():
    parser = argparse.ArgumentParser(description="External Receipt Signer")
    parser.add_argument("run_id", type=str, help="Run ID to sign")
    parser.add_argument("--key", type=str, required=True, help="Path to Ed25519 private key PEM file")
    parser.add_argument("--trust-mode", type=str, choices=["development", "production"], default="development", help="Trust mode for signature")
    args = parser.parse_args()

    sig_path = sign_receipt_for_run(args.run_id, args.key, trust_mode=args.trust_mode)
    print(f"Receipt successfully signed! Signature written to: {sig_path}")


if __name__ == "__main__":
    main()
