"""Repository Secret Scanner for Private Key Material.

Implements Sections 21, 22 of Milestone V2.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List


class SecretLeakError(ValueError):
    """Raised when PEM private key or secret key material is detected in the repository."""


SECRET_PATTERNS = [
    (r"-----BEGIN\s+(EC\s+|RSA\s+|OPENSSH\s+|Ed25519\s+)?PRIVATE\s+KEY-----", "PEM Private Key Header"),
    (r"PRIVATE_KEY\s*=\s*['\"][A-Za-z0-9+/=]{32,}['\"]", "Hardcoded Private Key Variable Assignment"),
]


def scan_repository_for_secrets(search_path: str | Path = ".") -> List[Dict[str, Any]]:
    """Scan repository for committed private keys or secret key material."""
    search_path = Path(search_path)
    leaks = []

    for root, _, files in os.walk(search_path):
        # Skip git directory, caches, virtual environments, scratch, and evidence raw binaries
        if any(skip_dir in root for skip_dir in [".git", "evidence", "scratch", "__pycache__", ".pytest_cache", ".venv", "node_modules"]):
            continue

        for file in files:
            # Ignore public key files and signature files
            if file.endswith((".pub", ".sig", ".sha256", ".npy", ".npz", ".log", ".pyc")):
                continue

            file_path = Path(root) / file
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern, desc in SECRET_PATTERNS:
                    if re.search(pattern, content):
                        leaks.append({
                            "file": str(file_path),
                            "description": desc,
                            "pattern": pattern,
                        })
            except Exception:
                continue

    if leaks:
        raise SecretLeakError(
            f"SECRET LEAK DETECTED in repository: {leaks}! Private keys MUST NOT be stored in Git!"
        )

    return leaks
