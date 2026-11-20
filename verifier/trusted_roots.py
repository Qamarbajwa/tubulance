"""External Trusted Roots Manager & Verifier Pinning.

Implements Sections 4, 14, 15, 54, 55, 56, 57 of Milestone V2 and Milestone V2.2.
"""
from __future__ import annotations

import enum
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

from .crypto_signer import compute_public_key_fingerprint


class TrustLevel(enum.Enum):
    LEVEL_0 = "LEVEL 0 - NARRATED"
    LEVEL_1 = "LEVEL 1 - EVIDENCE CAPTURED"
    LEVEL_2 = "LEVEL 2 - TECHNICALLY VERIFIED"
    LEVEL_3 = "LEVEL 3 - EXTERNALLY ATTESTED"
    LEVEL_4 = "LEVEL 4 - INDEPENDENTLY REPLICATED"


class TrustMode(enum.Enum):
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class ExternalRootUnavailableError(RuntimeError):
    """Raised when external authoritative trust root is missing or unreadable in production mode."""


class ExternalRootMismatchError(RuntimeError):
    """Raised when verifier manifest or public key fingerprint does not match external root."""


class ExternalRootWriteForbiddenError(RuntimeError):
    """Raised when project code attempts write access to external root."""


class TrustLevel(enum.Enum):
    LEVEL_0 = "LEVEL 0 - NARRATED"
    LEVEL_1 = "LEVEL 1 - EVIDENCE CAPTURED"
    LEVEL_2 = "LEVEL 2 - TECHNICALLY VERIFIED"
    LEVEL_3 = "LEVEL 3 - EXTERNALLY ATTESTED"
    LEVEL_4 = "LEVEL 4 - INDEPENDENTLY REPLICATED"


class DevelopmentIdentityError(RuntimeError):
    """Raised when a revoked development identity is used in production."""


class ExternalRootUnavailableError(RuntimeError):
    """Raised when external authoritative trust root is missing or unreadable in production mode."""


class ExternalRootMismatchError(RuntimeError):
    """Raised when verifier manifest or public key fingerprint does not match external root."""


class ExternalRootWriteForbiddenError(RuntimeError):
    """Raised when project code attempts write access to external root."""


def load_revoked_identities(verifier_dir: str | Path) -> List[str]:
    revoked_path = Path(verifier_dir) / "revoked_identities.json"
    if not revoked_path.exists():
        return []
    with open(revoked_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [ident["fingerprint"] for ident in data.get("revoked_development_identities", [])]


class TrustModeManager:
    def __init__(self, verifier_dir: str | Path = "verifier", trust_mode: TrustMode = TrustMode.DEVELOPMENT):
        self.verifier_dir = Path(verifier_dir)
        self.trust_mode = trust_mode
        self.revoked_fingerprints = load_revoked_identities(self.verifier_dir)

    def is_fingerprint_revoked(self, fingerprint: str) -> bool:
        return fingerprint in self.revoked_fingerprints

    def validate_production_readiness(self) -> bool:
        if self.trust_mode == TrustMode.DEVELOPMENT:
            return True

        roots_path = self.verifier_dir / "trusted_verifier_roots.json"
        if not roots_path.exists():
            raise DevelopmentIdentityError("trusted_verifier_roots.json is missing")

        with open(roots_path, "r", encoding="utf-8") as f:
            roots_data = json.load(f)

        prod_fp = roots_data.get("production_public_key_fingerprint")
        if not prod_fp or prod_fp == "NOT_CONFIGURED":
            raise DevelopmentIdentityError("production_public_key_fingerprint is not configured")

        if self.is_fingerprint_revoked(prod_fp):
            raise DevelopmentIdentityError("production_public_key_fingerprint is revoked")

        pubkey_path = self.verifier_dir / "trusted_public_key.pub"
        if not pubkey_path.exists():
            raise DevelopmentIdentityError("trusted_public_key.pub is missing")

        with open(pubkey_path, "r", encoding="utf-8") as f:
            pubkey_pem = f.read().encode("utf-8")

        curr_fp = compute_public_key_fingerprint(pubkey_pem)
        if curr_fp != prod_fp:
            raise DevelopmentIdentityError("Public key fingerprint does not match production fingerprint")

        return True

    def verify_external_root(self, external_root_path: str | Path | None = None) -> Dict[str, Any]:
        """Verify verification state against external authoritative root (production_root.json)."""
        if external_root_path is None:
            external_root_path = os.environ.get(
                "EXTERNAL_VERIFIER_ROOT_PATH",
                r"C:\Users\arqam\ResearchVerificationAuthority\production_root.json",
            )

        if self.trust_mode == TrustMode.PRODUCTION:
            ext_path = Path(external_root_path)
            if not ext_path.exists():
                raise ExternalRootUnavailableError(
                    f"EXTERNAL_ROOT_UNAVAILABLE: External root file '{ext_path}' not found! "
                    f"Production verification failed closed."
                )

            try:
                with open(ext_path, "r", encoding="utf-8") as f:
                    ext_data = json.load(f)
            except Exception as e:
                raise ExternalRootUnavailableError(
                    f"EXTERNAL_ROOT_UNAVAILABLE: Failed to read external root file '{ext_path}': {e}"
                )

            lock_v2 = LockManagerV2(self.verifier_dir)
            curr_ver_hash, _ = lock_v2.compute_verifier_manifest_hash()
            trusted_ver_hash = ext_data.get("trusted_verifier_manifest_sha256")

            if trusted_ver_hash and curr_ver_hash != trusted_ver_hash:
                raise ExternalRootMismatchError(
                    f"VERIFIER MANIFEST MISMATCH: Current verifier hash {curr_ver_hash[:10]}... "
                    f"does not match external root hash {trusted_ver_hash[:10]}...!"
                )

            pubkey_path = self.verifier_dir / "trusted_public_key.pub"
            if pubkey_path.exists():
                with open(pubkey_path, "r", encoding="utf-8") as f:
                    pubkey_pem = f.read()
                curr_fp = compute_public_key_fingerprint(pubkey_pem)
                trusted_fp = ext_data.get("trusted_public_key_fingerprint")
                if trusted_fp and curr_fp != trusted_fp:
                    raise ExternalRootMismatchError(
                        f"PUBLIC KEY FINGERPRINT MISMATCH: Repository key fingerprint {curr_fp[:10]}... "
                        f"does not match external root fingerprint {trusted_fp[:10]}...!"
                    )

            return {
                "status": "VALID",
                "trust_level": TrustLevel.LEVEL_3.value,
                "external_root": str(ext_path),
            }
        else:
            # DEVELOPMENT mode: Repo root is strictly PROJECT_CACHE_ONLY
            return {
                "status": "DEVELOPMENT_ONLY",
                "trust_level": TrustLevel.LEVEL_2.value,
                "cache_only": True,
            }

    def stamp_trust_mode(self) -> str:
        if self.trust_mode == TrustMode.DEVELOPMENT:
            return "DEVELOPMENT_ONLY"
        return "PRODUCTION"

    def verify_external_root(self, external_root_path: str | Path | None = None) -> Dict[str, Any]:
        if external_root_path is None:
            external_root_path = os.environ.get("EXTERNAL_VERIFIER_ROOT_PATH", r"C:\Users\arqam\ResearchVerificationAuthority\production_root.json")
            
        if self.trust_mode == TrustMode.PRODUCTION:
            ext_path = Path(external_root_path)
            if not ext_path.exists():
                raise ExternalRootUnavailableError("EXTERNAL_ROOT_UNAVAILABLE: External root file not found! Production verification failed closed.")
                
            try:
                with open(ext_path, "r", encoding="utf-8") as f:
                    ext_data = json.load(f)
            except Exception as e:
                raise ExternalRootUnavailableError("EXTERNAL_ROOT_UNAVAILABLE: External root file not found! Production verification failed closed.") from e
                
            curr_ver_hash, _ = LockManagerV2(self.verifier_dir).compute_verifier_manifest_hash()
            if ext_data.get("trusted_verifier_manifest_sha256") != curr_ver_hash:
                raise ExternalRootMismatchError("VERIFIER MANIFEST MISMATCH: Verifier hash does not match external root!")
                
            pubkey_path = self.verifier_dir / "trusted_public_key.pub"
            with open(pubkey_path, "r", encoding="utf-8") as f:
                pubkey_pem = f.read().encode("utf-8")
                
            curr_fp = compute_public_key_fingerprint(pubkey_pem)
            if ext_data.get("trusted_public_key_fingerprint") != curr_fp:
                raise ExternalRootMismatchError("PUBLIC KEY FINGERPRINT MISMATCH: Signing key fingerprint does not match external root!")
                
            return {"status": "VALID", "trust_level": TrustLevel.LEVEL_3.value, "external_root": str(ext_path)}
        else:
            return {"status": "DEVELOPMENT_ONLY", "trust_level": TrustLevel.LEVEL_2.value, "cache_only": True}


class UntrustedVerifierRootError(RuntimeError):
    """Raised when verifier source hash is not listed in trusted_verifier_roots.json."""


class UntrustedPublicKeyError(RuntimeError):
    """Raised when repository public key does not match trusted public key fingerprint."""


class RevokedVerifierError(RuntimeError):
    """Raised when verifier version has been revoked."""


class LockManagerV2:
    """Manages external trust root verification for Verifier V2.0 / V2.2."""

    def __init__(self, verifier_dir: str | Path = "verifier"):
        self.verifier_dir = Path(verifier_dir)
        self.roots_path = self.verifier_dir / "trusted_verifier_roots.json"
        self.revoked_path = self.verifier_dir / "revoked_verifiers.json"
        self.pubkey_path = self.verifier_dir / "trusted_public_key.pub"

    def compute_verifier_manifest_hash(self) -> Tuple[str, Dict[str, str]]:
        """Compute Merkle-like manifest of verifier directory and its SHA256 hash."""
        hashes = {}
        for root, _, files in os.walk(self.verifier_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.verifier_dir).as_posix()
                    with open(file_path, "rb") as f:
                        hashes[rel_path] = hashlib.sha256(f.read()).hexdigest()

        sorted_manifest_str = json.dumps({k: hashes[k] for k in sorted(hashes.keys())}, indent=2)
        overall_hash = hashlib.sha256(sorted_manifest_str.encode("utf-8")).hexdigest()
        return overall_hash, hashes

    def verify_against_trusted_roots(self) -> bool:
        """Verify current verifier source hash against project cache roots manifest."""
        overall_hash, _ = self.compute_verifier_manifest_hash()

        if not self.roots_path.exists():
            raise UntrustedVerifierRootError(
                "UNTRUSTED VERIFIER ROOT: trusted_verifier_roots.json missing! Verification FAIL."
            )

        with open(self.roots_path, "r", encoding="utf-8") as f:
            roots_data = json.load(f)

        # Check version revocation
        if self.revoked_path.exists():
            with open(self.revoked_path, "r", encoding="utf-8") as f:
                revoked_data = json.load(f)
                if overall_hash in revoked_data.get("revoked_hashes", []):
                    raise RevokedVerifierError(f"VERIFIER VERSION REVOKED for hash {overall_hash[:10]}...")

        trusted_hashes = roots_data.get("trusted_verifier_hashes", [])
        if overall_hash not in trusted_hashes:
            raise UntrustedVerifierRootError(
                f"UNTRUSTED VERIFIER ROOT: Current verifier hash {overall_hash[:10]}... "
                f"is NOT in trusted_verifier_roots.json! "
                f"The experimental agent is FORBIDDEN from self-approving verifier modifications!"
            )

        # Check public key fingerprint pinning
        if self.pubkey_path.exists():
            with open(self.pubkey_path, "r", encoding="utf-8") as f:
                pubkey_pem = f.read()
            curr_fp = compute_public_key_fingerprint(pubkey_pem)
            trusted_fp = roots_data.get("trusted_public_key_fingerprint")
            if trusted_fp and curr_fp != trusted_fp:
                raise UntrustedPublicKeyError(
                    f"UNTRUSTED PUBLIC KEY: Repository public key fingerprint {curr_fp[:10]}... "
                    f"does not match trusted root fingerprint {trusted_fp[:10]}...!"
                )

        return True
