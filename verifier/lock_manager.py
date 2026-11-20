"""Verifier Source Lock Manager and Hash Manifest Validator.

Implements Sections 7, 8, 9 of Milestone V1.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any


class VerifierLockError(RuntimeError):
    """Raised when verifier source code has been altered during milestone execution."""


class LockManager:
    """Manages VERIFIER_LOCK.json and verifier_manifest.json hashes."""

    def __init__(self, verifier_dir: str | Path = "verifier"):
        self.verifier_dir = Path(verifier_dir)
        self.lock_path = self.verifier_dir / "VERIFIER_LOCK.json"
        self.manifest_path = self.verifier_dir / "verifier_manifest.json"

    def compute_verifier_hashes(self) -> Dict[str, str]:
        """Compute SHA256 hashes for all python files in verifier/."""
        hashes = {}
        for root, _, files in os.walk(self.verifier_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.verifier_dir).as_posix()
                    with open(file_path, "rb") as f:
                        hashes[rel_path] = hashlib.sha256(f.read()).hexdigest()
        return hashes

    def create_lock(self) -> Dict[str, Any]:
        """Generate VERIFIER_LOCK.json and verifier_manifest.json."""
        hashes = self.compute_verifier_hashes()
        lock_data = {
            "version": "1.0",
            "files": hashes,
        }
        with open(self.lock_path, "w", encoding="utf-8") as f:
            json.dump(lock_data, f, indent=2)

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(lock_data, f, indent=2)

        return lock_data

    def check_verifier_lock(self) -> bool:
        """Verify that current verifier files match the locked manifest."""
        if not self.lock_path.exists():
            self.create_lock()
            return True

        with open(self.lock_path, "r", encoding="utf-8") as f:
            locked_data = json.load(f)

        current_hashes = self.compute_verifier_hashes()
        locked_hashes = locked_data.get("files", {})

        for rel_path, current_hash in current_hashes.items():
            locked_hash = locked_hashes.get(rel_path)
            if locked_hash is None:
                raise VerifierLockError(f"New verifier file '{rel_path}' added without lock update! VERIFICATION FAIL.")
            if current_hash != locked_hash:
                raise VerifierLockError(
                    f"VERIFIER MODIFIED: File '{rel_path}' hash changed! "
                    f"Expected {locked_hash[:10]}..., got {current_hash[:10]}... "
                    f"The coding agent is FORBIDDEN from editing verifier files to make tests pass!"
                )

        return True
