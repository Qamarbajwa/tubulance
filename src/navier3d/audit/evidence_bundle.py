"""Evidence Bundle Management, Write-Once Storage, Manifest SHA256 Hashing, and Ledger.

Implements Sections 6, 7, 24, 25, 27 of Milestone V0.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


class WriteProtectionError(RuntimeError):
    """Raised when an attempt is made to overwrite existing raw evidence or complete evidence bundle."""


class EvidenceBundle:
    """Manages an immutable evidence bundle directory structure for a run_id."""

    def __init__(self, run_id: str, base_dir: str | Path = "evidence"):
        self.run_id = run_id
        self.base_dir = Path(base_dir)
        self.run_dir = self.base_dir / run_id
        self.raw_dir = self.run_dir / "raw"
        self.completed = False

        if self.run_dir.exists() and (self.run_dir / "manifest.json").exists():
            self.completed = True

    def init_bundle(self) -> Path:
        """Create bundle directory structure."""
        if self.completed:
            raise WriteProtectionError(f"Evidence bundle '{self.run_id}' is already finalized and write-protected.")
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        return self.run_dir

    def save_raw_array(self, name: str, array: np.ndarray) -> Path:
        """Save a raw numpy array to raw/ directory in write-once mode."""
        self.init_bundle()
        file_path = self.raw_dir / f"{name}.npy"
        if file_path.exists():
            raise WriteProtectionError(f"Raw array '{name}.npy' already exists in '{self.run_id}'. Overwriting raw data is FORBIDDEN.")
        np.save(file_path, array)
        return file_path

    def save_raw_json(self, name: str, data: Dict[str, Any]) -> Path:
        """Save a raw JSON file to raw/ directory in write-once mode."""
        self.init_bundle()
        file_path = self.raw_dir / f"{name}.json"
        if file_path.exists():
            raise WriteProtectionError(f"Raw JSON '{name}.json' already exists in '{self.run_id}'. Overwriting raw data is FORBIDDEN.")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return file_path

    def save_metrics(self, metrics_data: Dict[str, Any]) -> Path:
        """Save metrics.json to the run directory."""
        self.init_bundle()
        file_path = self.run_dir / "metrics.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metrics_data, f, indent=2)
        return file_path

    def finalize(self) -> Dict[str, Any]:
        """Compute SHA256 manifest for all files in raw/ and finalize bundle."""
        if self.completed:
            raise WriteProtectionError(f"Evidence bundle '{self.run_id}' is already finalized.")

        manifest_entries = []
        for root, _, files in os.walk(self.run_dir):
            for file in files:
                if file in ("manifest.json", "manifest.sha256"):
                    continue
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.run_dir).as_posix()

                with open(file_path, "rb") as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content).hexdigest()
                    file_size = len(content)

                manifest_entries.append({
                    "filename": rel_path,
                    "size_bytes": file_size,
                    "sha256": file_hash,
                })

        manifest = {
            "run_id": self.run_id,
            "finalized_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "files": sorted(manifest_entries, key=lambda x: x["filename"]),
        }

        manifest_path = self.run_dir / "manifest.json"
        manifest_str = json.dumps(manifest, indent=2)
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest_str)

        manifest_hash = hashlib.sha256(manifest_str.encode("utf-8")).hexdigest()
        with open(self.run_dir / "manifest.sha256", "w", encoding="utf-8") as f:
            f.write(manifest_hash)

        self.completed = True
        return manifest


def append_to_research_ledger(
    run_id: str,
    milestone: str,
    config_hash: str,
    status: str,
    ledger_path: str | Path = "research_ledger.jsonl",
) -> Dict[str, Any]:
    """Append a record to the append-only research ledger. Never deletes or rewrites history."""
    entry = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "run_id": run_id,
        "milestone": milestone,
        "config_hash": config_hash,
        "status": status,
    }

    ledger_path = Path(ledger_path)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry
