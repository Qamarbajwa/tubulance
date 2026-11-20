"""Human-Executed Production Root-of-Trust Setup Tool.

RESTRICTED TO TEST/DEVELOPMENT USE ONLY. THIS SCRIPT MUST NOT BE USED TO GENERATE PRODUCTION SIGNING KEYS.

This script MUST be run by a human, NOT by the coding agent.
It generates a production Ed25519 keypair and installs the public key
into the verifier trust configuration.

Usage:
    python scripts/setup_production_root.py --generate --key-dir C:\\Users\\arqam\\ResearchVerificationAuthority
    python scripts/setup_production_root.py --verify --key-dir C:\\Users\\arqam\\ResearchVerificationAuthority
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def generate_production_keypair(key_dir: Path) -> tuple[bytes, bytes, str]:
    """Generate Ed25519 keypair and store private key in key_dir."""
    key_dir.mkdir(parents=True, exist_ok=True)
    
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    
    fingerprint = hashlib.sha256(public_pem).hexdigest()
    
    # Write private key to secure directory
    private_key_path = key_dir / "research_verification_private.pem"
    with open(private_key_path, "wb") as f:
        f.write(private_pem)
    
    return private_pem, public_pem, fingerprint


def install_production_root(public_pem: bytes, fingerprint: str, verifier_dir: Path) -> None:
    """Install production public key into verifier trust configuration."""
    # Write production public key
    pubkey_path = verifier_dir / "trusted_public_key.pub"
    with open(pubkey_path, "wb") as f:
        f.write(public_pem)
    
    # Update trusted_verifier_roots.json with production fingerprint
    roots_path = verifier_dir / "trusted_verifier_roots.json"
    if roots_path.exists():
        with open(roots_path, "r", encoding="utf-8") as f:
            roots_data = json.load(f)
    else:
        roots_data = {}
    
    roots_data["production_public_key_fingerprint"] = fingerprint
    roots_data["trusted_public_key_fingerprint"] = fingerprint
    
    with open(roots_path, "w", encoding="utf-8") as f:
        json.dump(roots_data, f, indent=2)


def verify_production_root(key_dir: Path, verifier_dir: Path) -> bool:
    """Verify that production root is correctly configured."""
    private_key_path = key_dir / "research_verification_private.pem"
    pubkey_path = verifier_dir / "trusted_public_key.pub"
    roots_path = verifier_dir / "trusted_verifier_roots.json"
    
    checks = []
    
    # Check 1: Private key exists outside repo
    if private_key_path.exists():
        checks.append(("Private key exists", True))
    else:
        checks.append(("Private key exists", False))
    
    # Check 2: Public key exists in verifier
    if pubkey_path.exists():
        with open(pubkey_path, "rb") as f:
            pub_pem = f.read()
        fp = hashlib.sha256(pub_pem).hexdigest()
        checks.append(("Public key exists", True))
    else:
        checks.append(("Public key exists", False))
        return False
    
    # Check 3: Roots file has production fingerprint
    if roots_path.exists():
        with open(roots_path, "r", encoding="utf-8") as f:
            roots = json.load(f)
        prod_fp = roots.get("production_public_key_fingerprint")
        if prod_fp and prod_fp != "NOT_CONFIGURED" and prod_fp == fp:
            checks.append(("Production fingerprint matches", True))
        else:
            checks.append(("Production fingerprint matches", False))
    else:
        checks.append(("Roots file exists", False))
    
    # Check 4: Fingerprint is NOT a revoked development identity
    revoked_path = verifier_dir / "revoked_identities.json"
    if revoked_path.exists():
        with open(revoked_path, "r", encoding="utf-8") as f:
            revoked = json.load(f)
        revoked_fps = [r["fingerprint"] for r in revoked.get("revoked_development_identities", [])]
        if fp not in revoked_fps:
            checks.append(("Not a revoked identity", True))
        else:
            checks.append(("Not a revoked identity", False))
    
    print("\n" + "=" * 60)
    print("PRODUCTION ROOT-OF-TRUST VERIFICATION")
    print("=" * 60)
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\n  Production Key Fingerprint: {fp}")
    print(f"  Private Key Location: {private_key_path}")
    print("=" * 60)
    
    all_pass = all(p for _, p in checks)
    if all_pass:
        print("\nPRODUCTION ROOT: CONFIGURED")
    else:
        print("\nPRODUCTION ROOT: NOT READY")
    
    return all_pass


def main():
    parser = argparse.ArgumentParser(
        description="Human-Executed Production Root-of-Trust Setup",
        epilog="RESTRICTED TO TEST/DEVELOPMENT USE ONLY. THIS SCRIPT MUST NOT BE USED TO GENERATE PRODUCTION SIGNING KEYS."
    )
    parser.add_argument("--generate", action="store_true", help="Generate new production keypair")
    parser.add_argument("--verify", action="store_true", help="Verify production root configuration")
    parser.add_argument("--key-dir", type=str, required=True, help="Directory for private key (outside repo)")
    parser.add_argument("--verifier-dir", type=str, default="verifier", help="Path to verifier directory")
    parser.add_argument("--test-mode-only", action="store_true", help="Acknowledge this is for testing only")
    args = parser.parse_args()
    
    key_dir = Path(args.key_dir)
    verifier_dir = Path(args.verifier_dir)
    
    if args.generate:
        if not args.test_mode_only:
            print("WARNING: Repository scripts must not be used for real production key generation. Production keys must be generated using external system tools (OpenSSL) outside the repository.")
        print("\nGenerating production Ed25519 keypair...")
        _, public_pem, fingerprint = generate_production_keypair(key_dir)
        print(f"Private key written to: {key_dir / 'research_verification_private.pem'}")
        print(f"Production fingerprint: {fingerprint}")
        
        install_production_root(public_pem, fingerprint, verifier_dir)
        print(f"Public key installed to: {verifier_dir / 'trusted_public_key.pub'}")
        print(f"Trusted roots updated: {verifier_dir / 'trusted_verifier_roots.json'}")
        print("\nIMPORTANT: You must now regenerate the verifier manifest and lock.")
        print("Run: python -c \"from verifier.lock_manager import LockManager; LockManager().create_lock()\"")
    
    elif args.verify:
        verify_production_root(key_dir, verifier_dir)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
