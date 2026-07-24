"""
Run manifest (Milestone 5.5)
===============================

A manifest is the single, reproducible description of a real-data
validation run: dataset, calibration/validation snapshots, resolution
tiers, terminal-layer requirements, preregistered placement parameters,
and the explicit real-data assertion. `load_manifest()` parses and
validates it -- values left blank (`null`/`~`/missing) for anything
physical are a hard validation failure, never silently defaulted. See
manifests/isotropic_128_validation.yaml for a template with intentionally
blank physical values, and manifests/synthetic_dry_run.yaml for a fully
filled, synthetic-source manifest used by the acceptance test.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml


class ManifestValidationError(ValueError):
    """Raised with every validation problem found, not just the first --
    see `errors` for the full list."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Manifest validation failed:\n  - " + "\n  - ".join(errors))


@dataclass(frozen=True)
class SnapshotSpec:
    time: float
    origin: tuple[int, int, int]
    size: tuple[int, int, int]
    stride: tuple[int, int, int] = (1, 1, 1)
    source: str = "sciserver"  # "sciserver" | "local_h5" | "synthetic"
    path: str | None = None  # required for local_h5
    frame_index: int | None = None  # required for local_h5


@dataclass(frozen=True)
class TerminalLayerSpec:
    preferred_shells: int
    minimum_shells: int
    minimum_populated_shells: int
    cutoff_nyquist_fraction: float


@dataclass(frozen=True)
class PlacementSpec:
    name: str
    params: dict = field(default_factory=dict)
    enabled: bool = True


@dataclass(frozen=True)
class Manifest:
    dataset: str
    calibration_snapshots: tuple[SnapshotSpec, ...]
    validation_snapshots: tuple[SnapshotSpec, ...]
    resolution_tiers: tuple[int, ...]
    terminal_layer: TerminalLayerSpec
    placements: tuple[PlacementSpec, ...]
    data_is_real: bool
    raw_text: str


_VALID_SOURCES = {"sciserver", "local_h5", "synthetic"}
_KNOWN_PLACEMENTS = {
    "local_cancellation",
    "parent_band_energy_weighted",
    "turnover_weighted",
    "dns_oracle_diagnostic",
}


def _require(d: dict, key: str, path: str, errors: list[str]):
    if key not in d or d[key] is None:
        errors.append(f"{path}.{key} is missing or blank -- must be set explicitly, not defaulted")
        return None
    return d[key]


def _parse_snapshot(raw: dict, path: str, errors: list[str]) -> SnapshotSpec | None:
    if not isinstance(raw, dict):
        errors.append(f"{path} must be a mapping")
        return None

    time = _require(raw, "time", path, errors)
    origin = _require(raw, "origin", path, errors)
    size = _require(raw, "size", path, errors)
    if origin is not None and (not isinstance(origin, (list, tuple)) or len(origin) != 3):
        errors.append(f"{path}.origin must be a 3-element list")
        origin = None
    if size is not None and (not isinstance(size, (list, tuple)) or len(size) != 3):
        errors.append(f"{path}.size must be a 3-element list")
        size = None

    source = raw.get("source", "sciserver")
    if source not in _VALID_SOURCES:
        errors.append(f"{path}.source={source!r} must be one of {sorted(_VALID_SOURCES)}")

    stride = raw.get("stride", [1, 1, 1])
    if not isinstance(stride, (list, tuple)) or len(stride) != 3:
        errors.append(f"{path}.stride must be a 3-element list")
        stride = [1, 1, 1]

    path_field = raw.get("path")
    frame_index = raw.get("frame_index")
    if source == "local_h5":
        if path_field is None:
            errors.append(f"{path}.path is required when source='local_h5'")
        if frame_index is None:
            errors.append(f"{path}.frame_index is required when source='local_h5'")

    if time is None or origin is None or size is None:
        return None

    return SnapshotSpec(
        time=float(time),
        origin=tuple(int(v) for v in origin),
        size=tuple(int(v) for v in size),
        stride=tuple(int(v) for v in stride),
        source=source,
        path=path_field,
        frame_index=frame_index,
    )


def _parse_snapshot_list(raw: list, path: str, errors: list[str]) -> tuple[SnapshotSpec, ...]:
    if not raw:
        errors.append(f"{path} must contain at least one snapshot")
        return ()
    out = []
    for i, entry in enumerate(raw):
        spec = _parse_snapshot(entry, f"{path}[{i}]", errors)
        if spec is not None:
            out.append(spec)
    return tuple(out)


def _check_calibration_validation_disjoint(
    calibration: tuple[SnapshotSpec, ...], validation: tuple[SnapshotSpec, ...], errors: list[str]
) -> None:
    def key(s: SnapshotSpec) -> tuple:
        return (s.time, s.origin, s.size, s.source, s.path, s.frame_index)

    overlap = {key(s) for s in calibration} & {key(s) for s in validation}
    if overlap:
        errors.append(
            f"snapshots.calibration and snapshots.validation overlap ({len(overlap)} shared "
            "snapshot(s)) -- a snapshot must not be used for both calibration and validation"
        )


def load_manifest(path: str) -> Manifest:
    text = Path(path).read_text()
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ManifestValidationError([f"invalid YAML: {exc}"]) from exc

    errors: list[str] = []
    if not isinstance(raw, dict):
        raise ManifestValidationError(["manifest root must be a mapping"])

    dataset = _require(raw, "dataset", "", errors)

    snapshots = raw.get("snapshots", {})
    calibration = _parse_snapshot_list(snapshots.get("calibration", []), "snapshots.calibration", errors)
    validation = _parse_snapshot_list(snapshots.get("validation", []), "snapshots.validation", errors)
    if calibration and validation:
        _check_calibration_validation_disjoint(calibration, validation, errors)

    resolution_tiers = raw.get("resolution_tiers")
    if not resolution_tiers:
        errors.append("resolution_tiers is missing or empty")
        resolution_tiers = ()
    else:
        resolution_tiers = tuple(int(v) for v in resolution_tiers)

    tl_raw = raw.get("terminal_layer", {})
    tl_path = "terminal_layer"
    preferred = _require(tl_raw, "preferred_shells", tl_path, errors)
    minimum = _require(tl_raw, "minimum_shells", tl_path, errors)
    min_populated = _require(tl_raw, "minimum_populated_shells", tl_path, errors)
    cutoff_fraction = _require(tl_raw, "cutoff_nyquist_fraction", tl_path, errors)
    terminal_layer = None
    if None not in (preferred, minimum, min_populated, cutoff_fraction):
        terminal_layer = TerminalLayerSpec(
            preferred_shells=int(preferred),
            minimum_shells=int(minimum),
            minimum_populated_shells=int(min_populated),
            cutoff_nyquist_fraction=float(cutoff_fraction),
        )

    placements_raw = raw.get("placements", {})
    if not placements_raw:
        errors.append("placements is missing or empty -- at least one strategy must be configured")
    placements = []
    for name, params in (placements_raw or {}).items():
        params = params or {}
        if name not in _KNOWN_PLACEMENTS:
            errors.append(f"placements.{name} is not a known strategy ({sorted(_KNOWN_PLACEMENTS)})")
            continue
        enabled = params.get("enabled", True)
        if name == "parent_band_energy_weighted" and enabled:
            if params.get("c1") is None or params.get("c2") is None:
                errors.append(
                    "placements.parent_band_energy_weighted.c1/c2 are required and must be "
                    "preregistered explicitly -- not left blank, not tuned after seeing results"
                )
        placements.append(PlacementSpec(name=name, params=params, enabled=enabled))

    classification_raw = raw.get("classification", {})
    data_is_real = classification_raw.get("data_is_real")
    if data_is_real is None:
        errors.append("classification.data_is_real is missing -- must be explicitly true or false")
    elif not isinstance(data_is_real, bool):
        errors.append("classification.data_is_real must be a boolean")

    if errors:
        raise ManifestValidationError(errors)

    return Manifest(
        dataset=dataset,
        calibration_snapshots=calibration,
        validation_snapshots=validation,
        resolution_tiers=resolution_tiers,
        terminal_layer=terminal_layer,
        placements=tuple(placements),
        data_is_real=bool(data_is_real),
        raw_text=text,
    )


def manifest_hash(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
