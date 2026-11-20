"""Pre-Registration Framework and Final Holdout Lock Management.

Implements Sections 15, 16, 17 of Milestone V0.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


class HoldoutViolationError(RuntimeError):
    """Raised when tuning/optimization code attempts to access locked holdout datasets prematurely."""


def preregister_experiment(
    milestone: str,
    hypothesis: str,
    config: Dict[str, Any],
    metrics: list[str],
    success_criteria: Dict[str, Any],
    run_dir: str | Path,
) -> Dict[str, Any]:
    """Write preregistered_experiment.json before benchmark execution and freeze it with SHA256."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    prereg = {
        "milestone": milestone,
        "hypothesis": hypothesis,
        "config": config,
        "metrics": metrics,
        "success_criteria": success_criteria,
    }

    json_str = json.dumps(prereg, sort_keys=True, indent=2)
    hash_str = hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    prereg_path = run_dir / "preregistered_experiment.json"
    hash_path = run_dir / "preregistered_experiment.sha256"

    with open(prereg_path, "w", encoding="utf-8") as f:
        f.write(json_str)

    with open(hash_path, "w", encoding="utf-8") as f:
        f.write(hash_str)

    return prereg


class HoldoutManager:
    """Manages holdout seed and dataset access locks."""

    def __init__(self, holdout_seeds: list[int], run_dir: str | Path):
        self.holdout_seeds = holdout_seeds
        self.unlocked = False
        self.run_dir = Path(run_dir)
        self._write_manifest()

    def _write_manifest(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "holdout_seeds": self.holdout_seeds,
            "unlocked": self.unlocked,
        }
        with open(self.run_dir / "holdout_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def access_holdout(self, seed: int) -> int:
        """Access holdout seed. Fails if unlocked == False."""
        if not self.unlocked:
            raise HoldoutViolationError(
                f"Premature access to holdout seed {seed} before tuning was finalized! "
                f"Holdout lock is ACTIVE."
            )
        return seed

    def unlock_holdout(self) -> None:
        self.unlocked = True
        self._write_manifest()
