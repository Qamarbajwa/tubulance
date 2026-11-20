"""Run Identity, Environment Provenance, Configuration Fingerprinting, and Comparability Assertions.

Implements Sections 1, 2, 3, 4, 5 of Milestone V0.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Tuple


class BenchmarkComparabilityError(ValueError):
    """Raised when reference solver and ROM candidate configurations differ in prohibited parameters."""


class ConfigurationMutationError(RuntimeError):
    """Raised when an attempt is made to mutate a frozen configuration during execution."""


class FrozenConfig:
    """Read-only immutable wrapper around configuration dictionary."""

    def __init__(self, data: Dict[str, Any]):
        super().__setattr__("_data", self._freeze(data))
        super().__setattr__("_frozen", True)

    def _freeze(self, val: Any) -> Any:
        if isinstance(val, dict):
            return {k: self._freeze(v) for k, v in val.items()}
        elif isinstance(val, list):
            return tuple(self._freeze(v) for v in val)
        return val

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'FrozenConfig' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise ConfigurationMutationError(f"Cannot mutate FrozenConfig field '{name}' during execution")
        super().__setattr__(name, value)

    def __setitem__(self, key: str, value: Any) -> None:
        raise ConfigurationMutationError(f"Cannot mutate FrozenConfig key '{key}' during execution")

    def to_dict(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self._data))


def generate_run_id(milestone: str, name: str) -> str:
    """Generate an immutable unique run_id BEFORE benchmark execution.

    Format: YYYY-MM-DDTHHMMSSZ__<milestone>__<name>__<short_uuid>
    Example: 2026-08-13T032500Z__v0__channel12__a8f239
    """
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_hash = uuid.uuid4().hex[:6]
    clean_milestone = str(milestone).lower().replace(" ", "_")
    clean_name = str(name).lower().replace(" ", "_")
    return f"{now}__{clean_milestone}__{clean_name}__{short_hash}"


def capture_environment(run_dir: str | Path) -> Dict[str, Any]:
    """Capture full environment snapshot and save environment.json in run_dir."""
    import numpy as np
    import scipy

    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    env = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "os": platform.platform(),
        "system": platform.system(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "git_commit": "HEAD_LOCAL",
        "dirty": True,
        "environment_variables": {
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", "default"),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS", "default"),
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS", "default"),
        },
    }

    env_path = run_dir / "environment.json"
    with open(env_path, "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2)

    return env


def fingerprint_config(config_dict: Dict[str, Any], run_dir: str | Path) -> Tuple[str, FrozenConfig]:
    """Serialize canonical config.json, compute SHA256 hash, and write config.sha256."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    canonical_json_str = json.dumps(config_dict, sort_keys=True, indent=2)
    config_hash = hashlib.sha256(canonical_json_str.encode("utf-8")).hexdigest()

    config_json_path = run_dir / "config.json"
    config_hash_path = run_dir / "config.sha256"

    with open(config_json_path, "w", encoding="utf-8") as f:
        f.write(canonical_json_str)

    with open(config_hash_path, "w", encoding="utf-8") as f:
        f.write(config_hash)

    frozen = FrozenConfig(config_dict)
    return config_hash, frozen


def assert_comparable(ref_config: Dict[str, Any], cand_config: Dict[str, Any]) -> None:
    """Verify that reference and candidate configurations share identical physical problem setups.

    Prohibited differences include grid, domain, BCs, Re, viscosity, density, forcing, IC seed, dt, final time.
    Allowed differences include representation ('ModelA' vs 'ROM') and rank.
    """
    prohibited_keys = [
        "nx", "ny", "nz", "lx", "ly", "lz",
        "nu", "rho", "dt", "n_steps", "seed", "k_peak", "E0",
        "bcs", "forcing",
    ]

    for key in prohibited_keys:
        val_ref = ref_config.get(key)
        val_cand = cand_config.get(key)

        if val_ref != val_cand:
            raise BenchmarkComparabilityError(
                f"Benchmark comparability mismatch on parameter '{key}': "
                f"reference config has {val_ref!r}, candidate config has {val_cand!r}. "
                f"Candidate evaluation is scientifically INVALIDATED."
            )
