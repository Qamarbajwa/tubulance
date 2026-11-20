"""Version-Controlled Hashed Metric Calculations with Lineage Metadata.

Implements Sections 7, 9, 21 of Milestone V0.
"""
from __future__ import annotations

import inspect
import hashlib
from typing import Any, Dict

import numpy as np


def get_metric_function_hash(func: Any) -> str:
    """Compute SHA256 hash of a metric function's source code."""
    try:
        source = inspect.getsource(func)
    except Exception:
        source = func.__name__
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def calculate_velocity_l2_relative_error(
    u_ref: np.ndarray, u_cand: np.ndarray, dV: float = 1.0,
) -> float:
    """Compute relative L2 velocity error ||u_ref - u_cand||_2 / (||u_ref||_2 + eps)."""
    diff_l2 = np.sqrt(np.sum((u_ref - u_cand) ** 2) * dV)
    ref_l2 = np.sqrt(np.sum(u_ref ** 2) * dV)
    return float(diff_l2 / (ref_l2 + 1e-15))


def calculate_wall_shear_relative_error(
    tau_ref: float, tau_cand: float,
) -> float:
    """Compute relative wall shear error |tau_ref - tau_cand| / (|tau_ref| + eps)."""
    return float(abs(tau_ref - tau_cand) / (abs(tau_ref) + 1e-15))


def build_metric_entry(
    name: str,
    value: float,
    units: str | None,
    source_files: list[str],
    metric_function: Any,
    run_id: str,
    config_hash: str,
) -> Dict[str, Any]:
    """Build a standardized lineage-tagged metric entry for metrics.json."""
    return {
        "name": name,
        "value": float(value),
        "units": units,
        "source_files": source_files,
        "metric_function": metric_function.__name__,
        "metric_function_hash": get_metric_function_hash(metric_function),
        "run_id": run_id,
        "config_hash": config_hash,
    }
