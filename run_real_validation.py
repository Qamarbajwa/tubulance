"""
Real-data validation runner (Milestone 5.5)
===============================================

    python run_real_validation.py --manifest manifests/isotropic_128_validation.yaml \\
        --output runs/isotropic_128_validation

    python run_real_validation.py --manifest manifests/isotropic_128_validation.yaml \\
        --output runs/isotropic_128_validation --preflight

Execution chain: environment check -> data fetch -> provenance capture ->
structural validation -> E(k)/T(k)/Pi(k) -> placement comparison ->
ensemble aggregation -> identifiability -> classification -> report and
hashes.

Output directories are immutable: re-running the same manifest against
the same code reproduces the same run ID and is a no-op if already
completed; a DIFFERENT run ID targeting an existing output directory is
refused unless --force is passed. --resume continues a run interrupted
mid-stage using its checkpoint file (stage-level granularity: calibration
/ validation / selection / ensemble / identifiability / report -- not
per-snapshot within a stage).
"""

from __future__ import annotations

import argparse
import dataclasses
import gc
import json
import subprocess
import sys
from pathlib import Path

from data_sources import resolve_data_source
from jhtdb_terminal_benchmark import Config
from manifest import Manifest, ManifestValidationError, load_manifest, manifest_hash
from placement_comparison import (
    identifiability_report,
    run_validation_comparison,
    select_placement,
)
from preflight import run_preflight
from report_generator import generate_reports
from run_identity import RunIdentity, compute_run_id, hash_directory, new_run_identity
from snapshot_ensemble import run_ensemble

STAGES = ["calibration", "validation", "selection", "ensemble", "identifiability", "report"]


class RunAbortedError(RuntimeError):
    pass


def build_config(manifest: Manifest) -> Config:
    tl = manifest.terminal_layer
    return Config(
        dataset=manifest.dataset,
        cutoff_fraction=tl.cutoff_nyquist_fraction,
        min_terminal_shells=tl.minimum_shells,
        preferred_terminal_shells=tl.preferred_shells,
        min_populated_terminal_shells=tl.minimum_populated_shells,
    )


def _parent_band_params(manifest: Manifest) -> tuple[float | None, float | None]:
    for p in manifest.placements:
        if p.name == "parent_band_energy_weighted" and p.enabled:
            return p.params.get("c1"), p.params.get("c2")
    return None, None


def _fetchers(manifest: Manifest, snapshots, *, seed: int):
    return [
        (lambda spec=spec: resolve_data_source(spec, data_is_real=manifest.data_is_real, seed=seed)())
        for spec in snapshots
    ]


def _load_checkpoint(output: Path) -> dict:
    path = output / "checkpoint.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"completed_stages": []}


def _save_checkpoint(output: Path, checkpoint: dict) -> None:
    (output / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2))


def _stage_done(checkpoint: dict, stage: str) -> bool:
    return stage in checkpoint["completed_stages"]


def _mark_stage_done(output: Path, checkpoint: dict, stage: str) -> None:
    checkpoint["completed_stages"].append(stage)
    _save_checkpoint(output, checkpoint)


def capture_test_suite_status(skip: bool) -> dict:
    if skip:
        return {"skipped": True}
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True, timeout=1800
        )
        tail = "\n".join(result.stdout.strip().splitlines()[-5:])
        return {"skipped": False, "returncode": result.returncode, "summary": tail}
    except Exception as exc:
        return {"skipped": False, "error": str(exc)}


def run(
    manifest_path: str,
    output_dir: str,
    *,
    force: bool = False,
    resume: bool = False,
    skip_tests: bool = False,
    seed: int = 0,
) -> RunIdentity:
    manifest = load_manifest(manifest_path)  # raises ManifestValidationError

    preflight = run_preflight(manifest, output_dir)
    if not preflight.passed:
        raise RunAbortedError(
            "Preflight failed -- refusing to fetch any data. Failing checks:\n  "
            + "\n  ".join(c.detail for c in preflight.checks if c.blocking and not c.passed)
        )

    m_hash = manifest_hash(manifest_path)
    run_id = compute_run_id(m_hash, {"dataset": manifest.dataset, "data_is_real": manifest.data_is_real})

    output = Path(output_dir)
    identity_path = output / "run_identity.json"

    if identity_path.exists():
        existing = RunIdentity.from_json(identity_path.read_text())
        if existing.run_id == run_id and existing.status == "completed":
            print(f"Run {run_id} already completed at {output} -- nothing to do.")
            return existing
        if existing.run_id == run_id and existing.status == "running":
            if not resume:
                raise RunAbortedError(
                    f"Run {run_id} at {output} appears interrupted (status='running'). "
                    "Pass --resume to continue it."
                )
            identity = existing
        elif existing.run_id != run_id:
            if not force:
                raise RunAbortedError(
                    f"Output directory {output} already contains a DIFFERENT completed/running "
                    f"run (run_id={existing.run_id}, this manifest -> run_id={run_id}). "
                    "Refusing to overwrite. Use --force to override, or a new --output directory."
                )
            print(f"WARNING: --force overwriting existing run {existing.run_id} with {run_id}.")
            identity = new_run_identity(manifest_path, run_id, m_hash, seed)
        else:
            identity = new_run_identity(manifest_path, run_id, m_hash, seed)
    else:
        output.mkdir(parents=True, exist_ok=True)
        identity = new_run_identity(manifest_path, run_id, m_hash, seed)

    identity_path.write_text(identity.to_json())
    checkpoint = _load_checkpoint(output)

    cfg = build_config(manifest)
    c1, c2 = _parent_band_params(manifest)
    cfg = dataclasses.replace(cfg, parent_band_c1=c1, parent_band_c2=c2)

    calibration_fetchers = _fetchers(manifest, manifest.calibration_snapshots, seed=seed)
    validation_fetchers = _fetchers(manifest, manifest.validation_snapshots, seed=seed + 1000)

    selection = None
    validation_df = None
    ensemble_result = None
    identifiability = None

    try:
        if not _stage_done(checkpoint, "selection"):
            selection = select_placement(calibration_fetchers, cfg, str(output / "calibration"))
            (output / "selection_stage.json").write_text(json.dumps(selection, indent=2, default=str))
            _mark_stage_done(output, checkpoint, "selection")
        else:
            selection = json.loads((output / "selection_stage.json").read_text())
        gc.collect()

        if not _stage_done(checkpoint, "validation"):
            validation_df = run_validation_comparison(validation_fetchers, cfg, str(output / "validation"), c1=c1, c2=c2)
            validation_df.to_json(output / "validation_stage.json", orient="records")
            _mark_stage_done(output, checkpoint, "validation")
        else:
            import pandas as pd

            validation_df = pd.read_json(output / "validation_stage.json", orient="records")
        gc.collect()

        if not _stage_done(checkpoint, "identifiability"):
            identifiability = identifiability_report(validation_df)
            (output / "identifiability_stage.json").write_text(json.dumps(identifiability, indent=2, default=str))
            _mark_stage_done(output, checkpoint, "identifiability")
        else:
            identifiability = json.loads((output / "identifiability_stage.json").read_text())

        if not _stage_done(checkpoint, "ensemble"):
            selected_placement = selection.get("selected_placement") or "local_cancellation"
            cfg_selected = dataclasses.replace(cfg, backscatter_placement=selected_placement)
            ensemble_fetchers = _fetchers(manifest, manifest.validation_snapshots, seed=seed + 1000)
            ensemble_result = run_ensemble(
                ensemble_fetchers,
                cfg_selected,
                str(output / "ensemble"),
                min_snapshots=len(manifest.validation_snapshots),
            )
            (output / "ensemble_stage.json").write_text(json.dumps(ensemble_result, indent=2, default=str))
            _mark_stage_done(output, checkpoint, "ensemble")
        else:
            ensemble_result = json.loads((output / "ensemble_stage.json").read_text())
        gc.collect()

        if not _stage_done(checkpoint, "report"):
            generate_reports(
                str(output / "report"),
                data_is_real=manifest.data_is_real,
                ensemble_result=ensemble_result,
                placement_selection=selection,
                placement_validation_df=validation_df,
                identifiability=identifiability,
            )
            _mark_stage_done(output, checkpoint, "report")

        test_status = capture_test_suite_status(skip_tests)

        identity.status = "completed"
        identity.end_time = _now_iso()
        identity.test_suite_status = test_status
        identity.output_hashes = hash_directory(output)
        identity_path.write_text(identity.to_json())

    except Exception:
        identity.status = "failed"
        identity.end_time = _now_iso()
        identity_path.write_text(identity.to_json())
        raise

    return identity


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the real-data JHTDB terminal-layer validation chain.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--preflight", action="store_true", help="Run preflight checks only; fetch nothing.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing run with a different run ID.")
    parser.add_argument("--resume", action="store_true", help="Resume an interrupted run from its checkpoint.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip capturing test-suite status (faster).")
    parser.add_argument("--seed", type=int, default=0, help="Seed for synthetic-source snapshots only.")
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest)
    except ManifestValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    if args.preflight:
        report = run_preflight(manifest, args.output)
        for line in report.summary_lines():
            print(line)
        print(f"\nOverall: {'PASS' if report.passed else 'FAIL'}")
        sys.exit(0 if report.passed else 1)

    try:
        identity = run(
            args.manifest,
            args.output,
            force=args.force,
            resume=args.resume,
            skip_tests=args.skip_tests,
            seed=args.seed,
        )
    except RunAbortedError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    print(f"Run {identity.run_id} finished with status={identity.status}")
    sys.exit(0 if identity.status == "completed" else 1)


if __name__ == "__main__":
    main()
