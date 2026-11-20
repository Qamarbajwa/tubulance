"""Independent CLI verifying signatures, public-key fingerprints, and receipt hash bounds.

Implements Sections 7, 8, 10, 11, 12, 13, 54, 55 of Milestone V2 and Milestone V2.2.
Usage: python verifier/verify_receipt.py <receipt_json_path> <signature_sig_path>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

from .crypto_signer import (
    verify_data_signature,
    compute_public_key_fingerprint,
    canonicalize_json,
    InvalidSignatureError,
)
from .trusted_roots import (
    LockManagerV2,
    UntrustedPublicKeyError,
    load_revoked_identities,
    TrustModeManager,
    TrustMode,
    TrustLevel,
    ExternalRootUnavailableError,
    ExternalRootMismatchError,
)


def verify_receipt(
    receipt_json_path: str | Path,
    signature_sig_path: str | Path,
    verifier_dir: str | Path = "verifier",
    trust_mode: str = "development",
    external_root_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Verify receipt JSON against Ed25519 signature, external trust roots, and manifest hashes."""
    receipt_path = Path(receipt_json_path)
    sig_path = Path(signature_sig_path)
    ver_dir = Path(verifier_dir)

    if not receipt_path.exists():
        return {
            "status": "FAILED",
            "reason": f"Receipt file '{receipt_path}' missing",
            "trust_level": TrustLevel.LEVEL_2.value,
        }

    if not sig_path.exists():
        return {
            "status": "FAILED",
            "reason": f"Signature file '{sig_path}' missing",
            "trust_level": TrustLevel.LEVEL_2.value,
        }

    # 1. Load receipt
    with open(receipt_path, "r", encoding="utf-8") as f:
        receipt_data = json.load(f)

    # 2. Load signature bytes
    with open(sig_path, "rb") as f:
        signature_bytes = f.read()

    # 3. Load public key
    pubkey_path = ver_dir / "trusted_public_key.pub"
    if not pubkey_path.exists():
        return {
            "status": "FAILED",
            "reason": f"Public key file '{pubkey_path}' missing",
            "trust_level": TrustLevel.LEVEL_2.value,
        }

    with open(pubkey_path, "r", encoding="utf-8") as f:
        pubkey_pem = f.read().encode("utf-8")
    curr_fp = compute_public_key_fingerprint(pubkey_pem)

    # 4. In Production Mode: Verify External Authoritative Root FIRST
    if trust_mode == "production":
        if external_root_path is None:
            external_root_path = os.environ.get(
                "EXTERNAL_VERIFIER_ROOT_PATH",
                r"C:\Users\arqam\ResearchVerificationAuthority\production_root.json",
            )
        ext_path = Path(external_root_path)

        if not ext_path.exists():
            return {
                "status": "FAILED",
                "reason": f"EXTERNAL_ROOT_UNAVAILABLE: External root file '{ext_path}' missing. Fail closed.",
                "trust_level": TrustLevel.LEVEL_2.value,
                "verification_status": "NOT_EXTERNALLY_ATTESTED",
            }

        try:
            with open(ext_path, "r", encoding="utf-8") as f:
                ext_data = json.load(f)
        except Exception as e:
            return {
                "status": "FAILED",
                "reason": f"EXTERNAL_ROOT_UNAVAILABLE: Unreadable external root '{ext_path}': {e}",
                "trust_level": TrustLevel.LEVEL_2.value,
                "verification_status": "NOT_EXTERNALLY_ATTESTED",
            }

        # Validate public key fingerprint against external root
        trusted_ext_fp = ext_data.get("trusted_public_key_fingerprint")
        if trusted_ext_fp and curr_fp != trusted_ext_fp:
            return {
                "status": "FAILED",
                "reason": f"UNTRUSTED SIGNING AUTHORITY: Key fingerprint {curr_fp[:10]}... != external root {trusted_ext_fp[:10]}...",
                "trust_level": TrustLevel.LEVEL_2.value,
                "verification_status": "NOT_EXTERNALLY_ATTESTED",
            }

        # Validate verifier manifest hash against external root
        lock_v2 = LockManagerV2(verifier_dir=ver_dir)
        curr_ver_hash, _ = lock_v2.compute_verifier_manifest_hash()
        trusted_ver_hash = ext_data.get("trusted_verifier_manifest_sha256")
        if trusted_ver_hash and curr_ver_hash != trusted_ver_hash:
            return {
                "status": "FAILED",
                "reason": f"VERIFIER MANIFEST MISMATCH: Verifier hash {curr_ver_hash[:10]}... != external root {trusted_ver_hash[:10]}...",
                "trust_level": TrustLevel.LEVEL_2.value,
                "verification_status": "NOT_EXTERNALLY_ATTESTED",
            }

        # Check revoked identities
        revoked_fingerprints = load_revoked_identities(ver_dir)
        if curr_fp in revoked_fingerprints:
            return {
                "status": "FAILED",
                "reason": "REVOKED IDENTITY: Signing key is a revoked development identity",
                "trust_level": TrustLevel.LEVEL_2.value,
            }

        if receipt_data.get("trust_mode") == "DEVELOPMENT_ONLY":
            return {
                "status": "FAILED",
                "reason": "DEVELOPMENT RECEIPT: Cannot verify development receipt in production mode",
                "trust_level": TrustLevel.LEVEL_2.value,
            }

    # 5. Canonicalize receipt & verify Ed25519 signature
    canonical_bytes = canonicalize_json(receipt_data)
    try:
        verify_data_signature(canonical_bytes, signature_bytes, pubkey_pem)
    except InvalidSignatureError as e:
        return {
            "status": "FAILED",
            "reason": f"SIGNATURE INVALID: {e}",
            "trust_level": TrustLevel.LEVEL_2.value,
        }

    if trust_mode == "production":
        return {
            "status": "VERIFIED",
            "signature": "VALID",
            "verifier_root": "EXTERNALLY_ATTESTED",
            "trust_level": TrustLevel.LEVEL_3.value,
            "verification_status": "EXTERNALLY_ATTESTED",
            "run_id": receipt_data.get("run_id"),
        }
    else:
        # Development mode
        lock_v2 = LockManagerV2(verifier_dir=ver_dir)
        curr_ver_hash, _ = lock_v2.compute_verifier_manifest_hash()
        if receipt_data.get("verifier_manifest_sha256") != curr_ver_hash:
            return {
                "status": "FAILED",
                "reason": f"HASH MISMATCH: verifier_manifest_sha256 mismatch",
                "trust_level": TrustLevel.LEVEL_2.value,
            }

        return {
            "status": "VERIFIED",
            "signature": "VALID",
            "verifier_root": "PROJECT_CACHE_ONLY",
            "trust_level": TrustLevel.LEVEL_2.value,
            "verification_status": "TECHNICALLY_VERIFIED",
            "run_id": receipt_data.get("run_id"),
        }


def main():
    parser = argparse.ArgumentParser(description="Verify a scientific receipt")
    parser.add_argument("receipt_json_path", help="Path to receipt JSON")
    parser.add_argument("signature_sig_path", help="Path to signature file")
    parser.add_argument("--trust-mode", choices=["development", "production"], default="development", help="Trust mode for verification")
    parser.add_argument("--external-root", help="Path to external production_root.json file")
    args = parser.parse_args()

    res = verify_receipt(
        args.receipt_json_path,
        args.signature_sig_path,
        trust_mode=args.trust_mode,
        external_root_path=args.external_root,
    )
    if res["status"] == "VERIFIED":
        print(f"\n==========================================")
        print(f"SIGNATURE VALID")
        print(f"VERIFIER ROOT: {res.get('verifier_root')}")
        print(f"TRUST LEVEL: {res.get('trust_level')}")
        print(f"RECEIPT STATUS: VERIFIED ({res['run_id']})")
        print(f"==========================================\n")
    else:
        print(f"\n==========================================")
        print(f"RECEIPT INVALID / FAIL CLOSED: {res.get('reason')}")
        print(f"TRUST LEVEL: {res.get('trust_level', 'LEVEL 2 - TECHNICALLY VERIFIED')}")
        print(f"==========================================\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
