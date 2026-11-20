"""Ed25519 Asymmetric Cryptographic Signing and Public-Key Fingerprinting.

Implements Sections 5, 7, 9, 10, 11, 12, 54, 55 of Milestone V2.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Tuple

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class InvalidSignatureError(ValueError):
    """Raised when Ed25519 signature verification fails."""


class UntrustedPublicKeyError(ValueError):
    """Raised when public key fingerprint does not match trusted root fingerprint."""


def generate_ed25519_keypair() -> Tuple[bytes, bytes, str]:
    """Generate a new Ed25519 keypair. Returns (private_pem, public_pem, fingerprint)."""
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

    fingerprint = compute_public_key_fingerprint(public_pem)
    return private_pem, public_pem, fingerprint


def compute_public_key_fingerprint(public_pem: bytes | str) -> str:
    """Compute SHA256 hex fingerprint of public key PEM."""
    if isinstance(public_pem, str):
        public_pem = public_pem.encode("utf-8")
    return hashlib.sha256(public_pem).hexdigest()


def sign_data(data_bytes: bytes, private_pem: bytes) -> bytes:
    """Sign arbitrary data bytes using Ed25519 private key PEM."""
    private_key = serialization.load_pem_private_key(private_pem, password=None)
    assert isinstance(private_key, ed25519.Ed25519PrivateKey)
    return private_key.sign(data_bytes)


def verify_data_signature(data_bytes: bytes, signature_bytes: bytes, public_pem: bytes) -> bool:
    """Verify data signature using Ed25519 public key PEM."""
    try:
        public_key = serialization.load_pem_public_key(public_pem)
        assert isinstance(public_key, ed25519.Ed25519PublicKey)
        public_key.verify(signature_bytes, data_bytes)
        return True
    except Exception as e:
        raise InvalidSignatureError(f"Ed25519 signature verification FAILED: {e}")


def canonicalize_json(data: Dict[str, Any]) -> bytes:
    """Return deterministic canonical JSON bytes for hashing and signing."""
    return json.dumps(data, sort_keys=True, indent=2).encode("utf-8")
