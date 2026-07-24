"""
Preflight checks (Milestone 5.5)
====================================

Everything here runs WITHOUT fetching any cutout -- environment
availability, resource estimates, and manifest-internal consistency only.
No large cutout should be fetched until `run_preflight()` reports
`passed=True`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from jhtdb_terminal_benchmark import Config, compute_terminal_layer
from manifest import Manifest
from memory_estimate import estimate_disk_usage_mb, estimate_peak_memory

_SCISERVER_MOUNT_CANDIDATES = (
    Path("/home/idies/workspace/turb"),
    Path("/home/idies/workspace/Temporary"),
)


@dataclass(frozen=True)
class PreflightCheck:
    name: str
    passed: bool
    detail: str
    blocking: bool = True


@dataclass(frozen=True)
class PreflightReport:
    checks: tuple[PreflightCheck, ...]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks if c.blocking)

    def summary_lines(self) -> list[str]:
        lines = []
        for c in self.checks:
            status = "PASS" if c.passed else ("FAIL" if c.blocking else "WARN")
            lines.append(f"[{status}] {c.name}: {c.detail}")
        return lines


def predicted_terminal_layer(grid_n: int, manifest: Manifest):
    tl = manifest.terminal_layer
    cfg = Config(
        cutoff_fraction=tl.cutoff_nyquist_fraction,
        min_terminal_shells=tl.minimum_shells,
        preferred_terminal_shells=tl.preferred_shells,
    )
    nyquist = grid_n / 2.0
    kc = cfg.cutoff_fraction * nyquist
    delta_k = 1.0  # 2*pi / domain_length, domain_length = 2*pi by convention (see Config)
    return compute_terminal_layer(kc, delta_k, cfg)


def _needs_sciserver(manifest: Manifest) -> bool:
    return any(
        s.source == "sciserver" for s in manifest.calibration_snapshots + manifest.validation_snapshots
    )


def check_sciserver_import(*, blocking: bool) -> PreflightCheck:
    try:
        import SciServer  # noqa: F401

        return PreflightCheck("sciserver_import", True, "SciServer package importable", blocking=blocking)
    except ImportError:
        return PreflightCheck(
            "sciserver_import",
            False,
            "SciServer package not importable in this environment",
            blocking=blocking,
        )


def check_giverny_import(*, blocking: bool) -> PreflightCheck:
    try:
        import giverny  # noqa: F401

        return PreflightCheck("giverny_import", True, "giverny package importable", blocking=blocking)
    except ImportError:
        return PreflightCheck(
            "giverny_import", False, "giverny package not importable in this environment", blocking=blocking
        )


def check_turbulence_volume_mounted(*, blocking: bool) -> PreflightCheck:
    for candidate in _SCISERVER_MOUNT_CANDIDATES:
        if candidate.exists():
            return PreflightCheck("turbulence_volume_mounted", True, f"found {candidate}", blocking=blocking)
    return PreflightCheck(
        "turbulence_volume_mounted",
        False,
        f"none of {[str(c) for c in _SCISERVER_MOUNT_CANDIDATES]} exist in this environment",
        blocking=blocking,
    )


def check_authentication(*, blocking: bool) -> PreflightCheck:
    token_present = bool(os.environ.get("SCISERVER_TOKEN") or os.environ.get("CASJOBS_TOKEN"))
    return PreflightCheck(
        "authentication",
        token_present,
        "found a SciServer/CasJobs token env var" if token_present else "no SciServer/CasJobs token env var found",
        blocking=blocking,
    )


def check_dataset_and_snapshot_accessibility(manifest: Manifest) -> PreflightCheck:
    needs_sciserver = any(
        s.source == "sciserver" for s in manifest.calibration_snapshots + manifest.validation_snapshots
    )
    if not needs_sciserver:
        return PreflightCheck(
            "dataset_snapshot_accessibility",
            True,
            "no snapshot uses source='sciserver' -- nothing to check here",
            blocking=False,
        )
    return PreflightCheck(
        "dataset_snapshot_accessibility",
        False,
        "manifest has sciserver-sourced snapshots but this environment cannot verify dataset/"
        "snapshot accessibility without a live SciServer session (requires sciserver_import to pass first)",
    )


def check_memory_estimate(manifest: Manifest) -> PreflightCheck:
    import psutil

    try:
        available_mb = psutil.virtual_memory().available / (1024 * 1024)
    except Exception:
        available_mb = None

    estimates = [estimate_peak_memory(n) for n in manifest.resolution_tiers]
    worst = max(estimates, key=lambda e: e.peak_estimate_mb)
    if available_mb is None:
        return PreflightCheck(
            "memory_estimate",
            True,
            f"largest tier ({worst.grid_n}^3) estimated peak {worst.peak_estimate_mb:.0f} MB; "
            "available system memory unknown, cannot compare",
            blocking=False,
        )
    fits = worst.peak_estimate_mb < 0.8 * available_mb
    return PreflightCheck(
        "memory_estimate",
        fits,
        f"largest tier ({worst.grid_n}^3) estimated peak {worst.peak_estimate_mb:.0f} MB vs "
        f"{available_mb:.0f} MB available",
    )


def check_disk_estimate(manifest: Manifest, output_dir: str) -> PreflightCheck:
    import shutil

    n_snapshots = len(manifest.calibration_snapshots) + len(manifest.validation_snapshots)
    n_placements = len([p for p in manifest.placements if p.enabled])
    estimated_mb = estimate_disk_usage_mb(n_snapshots, n_placements)

    try:
        free_mb = shutil.disk_usage(Path(output_dir).parent if Path(output_dir).parent.exists() else ".").free / (
            1024 * 1024
        )
    except OSError:
        free_mb = None

    if free_mb is None:
        return PreflightCheck("disk_estimate", True, f"estimated {estimated_mb:.0f} MB; free space unknown", blocking=False)
    fits = estimated_mb < 0.9 * free_mb
    return PreflightCheck(
        "disk_estimate", fits, f"estimated {estimated_mb:.0f} MB vs {free_mb:.0f} MB free"
    )


def check_shell_count_requirements(manifest: Manifest) -> PreflightCheck:
    problems = []
    for n in manifest.resolution_tiers:
        layer = predicted_terminal_layer(n, manifest)
        if layer.n_t < manifest.terminal_layer.minimum_shells:
            problems.append(f"{n}^3: predicted N_T={layer.n_t:.2f} < minimum {manifest.terminal_layer.minimum_shells}")
    if problems:
        return PreflightCheck("shell_count_requirements", False, "; ".join(problems))
    return PreflightCheck(
        "shell_count_requirements",
        True,
        f"all {len(manifest.resolution_tiers)} resolution tier(s) predicted to satisfy minimum_shells",
    )


def check_calibration_validation_separation(manifest: Manifest) -> PreflightCheck:
    def key(s):
        return (s.time, s.origin, s.size, s.source, s.path, s.frame_index)

    overlap = {key(s) for s in manifest.calibration_snapshots} & {key(s) for s in manifest.validation_snapshots}
    return PreflightCheck(
        "calibration_validation_separation",
        not overlap,
        "disjoint" if not overlap else f"{len(overlap)} snapshot(s) shared between calibration and validation",
    )


def check_placement_parameters(manifest: Manifest) -> PreflightCheck:
    for p in manifest.placements:
        if not p.enabled:
            continue
        if p.name == "parent_band_energy_weighted":
            if p.params.get("c1") is None or p.params.get("c2") is None:
                return PreflightCheck("placement_parameters", False, "parent_band_energy_weighted missing c1/c2")
    return PreflightCheck("placement_parameters", True, "all enabled placements have required parameters")


def check_real_data_assertion(manifest: Manifest) -> PreflightCheck:
    """The one check that must never be bypassable: if the manifest
    asserts data_is_real=true, no snapshot may use a synthetic source.
    data_sources.resolve_data_source() enforces this again at fetch time
    -- this is the early, no-data-fetched-yet version of the same rule.
    """
    sources = {s.source for s in manifest.calibration_snapshots + manifest.validation_snapshots}
    if manifest.data_is_real and "synthetic" in sources:
        return PreflightCheck(
            "real_data_assertion",
            False,
            "classification.data_is_real=true but at least one snapshot uses source='synthetic'",
        )
    return PreflightCheck(
        "real_data_assertion", True, f"data_is_real={manifest.data_is_real}, sources={sorted(sources)} consistent"
    )


def run_preflight(manifest: Manifest, output_dir: str) -> PreflightReport:
    needs_sciserver = _needs_sciserver(manifest)
    checks = [
        check_sciserver_import(blocking=needs_sciserver),
        check_giverny_import(blocking=needs_sciserver),
        check_turbulence_volume_mounted(blocking=needs_sciserver),
        check_authentication(blocking=needs_sciserver),
        check_dataset_and_snapshot_accessibility(manifest),
        check_memory_estimate(manifest),
        check_disk_estimate(manifest, output_dir),
        check_shell_count_requirements(manifest),
        check_calibration_validation_separation(manifest),
        check_placement_parameters(manifest),
        check_real_data_assertion(manifest),
    ]
    return PreflightReport(checks=tuple(checks))
