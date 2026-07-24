"""
Run identity and provenance (Milestone 5.5)
===============================================

Every real-data run gets an identifier derived from the manifest content,
the code revision, and its input provenance, plus a full provenance
record (git commit, dirty-tree status, package versions, Python version,
hardware, timestamps, output hashes, test-suite status). Output
directories are treated as immutable: re-running the same manifest
against the same code should reproduce the same run ID; a different
run ID targeting an existing output directory is refused unless the
caller explicitly forces an overwrite.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_directory(directory: Path) -> dict[str, str]:
    """SHA256 of every file under `directory`, keyed by path relative to it."""
    hashes = {}
    if not directory.exists():
        return hashes
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            hashes[str(path.relative_to(directory))] = sha256_file(path)
    return hashes


def git_info(repo_dir: str = ".") -> dict:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_dir, text=True, stderr=subprocess.DEVNULL
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=repo_dir, text=True, stderr=subprocess.DEVNULL
        )
        dirty = bool(status.strip())
        return {"commit": commit, "dirty": dirty, "available": True}
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        return {"commit": None, "dirty": None, "available": False, "error": str(exc)}


def package_versions() -> dict:
    versions = {"python": sys.version}
    for name in ("numpy", "scipy", "pandas", "matplotlib", "h5py", "yaml"):
        try:
            mod = __import__(name)
            versions[name] = getattr(mod, "__version__", "unknown")
        except ImportError:
            versions[name] = None
    return versions


def hardware_info() -> dict:
    info = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "total_memory_mb": None,
    }
    try:
        import psutil

        info["total_memory_mb"] = psutil.virtual_memory().total / (1024 * 1024)
    except ImportError:
        pass
    return info


def compute_run_id(manifest_hash: str, extra_provenance: dict) -> str:
    """Deterministic ID from manifest content + code revision + declared
    input provenance. Deliberately does NOT fold in the dirty-tree flag
    (a dirty tree can't be cheaply content-hashed here) -- dirty runs are
    still identified and flagged as reproducibility-compromised in the
    provenance record, not silently hashed as if reproducible.
    """
    git = git_info()
    payload = json.dumps(
        {"manifest_hash": manifest_hash, "git_commit": git.get("commit"), "extra": extra_provenance},
        sort_keys=True,
        default=str,
    )
    return sha256_bytes(payload.encode())


@dataclass
class RunIdentity:
    run_id: str
    manifest_path: str
    manifest_hash: str
    git_commit: str | None
    git_dirty: bool | None
    git_available: bool
    package_versions: dict
    hardware: dict
    seed: int | None
    start_time: str
    end_time: str | None = None
    status: str = "running"  # "running" | "completed" | "failed"
    output_hashes: dict | None = None
    test_suite_status: dict | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)

    @staticmethod
    def from_json(text: str) -> "RunIdentity":
        return RunIdentity(**json.loads(text))


def new_run_identity(manifest_path: str, run_id: str, manifest_hash_value: str, seed: int | None) -> RunIdentity:
    git = git_info()
    return RunIdentity(
        run_id=run_id,
        manifest_path=str(manifest_path),
        manifest_hash=manifest_hash_value,
        git_commit=git.get("commit"),
        git_dirty=git.get("dirty"),
        git_available=git.get("available", False),
        package_versions=package_versions(),
        hardware=hardware_info(),
        seed=seed,
        start_time=datetime.now(timezone.utc).isoformat(),
        output_hashes={},
    )
