"""
Acceptance test for the Milestone 5.5 SciServer execution package.

Demonstrates, entirely with synthetic local data (no SciServer needed),
the 10 required scenarios from the acceptance-test list:
  1. manifest validation
  2. preflight failure without SciServer
  3. immutable run creation
  4. interrupted-run recovery
  5. calibration/validation separation
  6. placement conservation failures surfaced, not silently dropped
  7. synthetic-data report warning
  8. real-data assertion requirement
  9. report and output hashing
  10. deterministic rerun behavior
"""

import json
from pathlib import Path

import pandas as pd
import pytest

import run_real_validation as rrv
from data_sources import DataSourceError, resolve_data_source
from manifest import ManifestValidationError, SnapshotSpec, load_manifest, manifest_hash
from preflight import run_preflight
from run_identity import RunIdentity, compute_run_id, sha256_file

SYNTHETIC_MANIFEST = "manifests/synthetic_dry_run.yaml"


@pytest.fixture(scope="module")
def completed_run(tmp_path_factory):
    output = tmp_path_factory.mktemp("acceptance_run")
    identity = rrv.run(SYNTHETIC_MANIFEST, str(output), skip_tests=True)
    return output, identity


# 1. Manifest validation -----------------------------------------------
def test_1_manifest_validation_rejects_blank_template(tmp_path):
    # See tests/test_manifest.py::test_blank_template_values_fail_validation
    # for why this uses a self-contained blank manifest rather than
    # manifests/isotropic_128_validation.yaml, which is meant to be filled
    # in as real campaigns are prepared.
    blank = tmp_path / "blank.yaml"
    blank.write_text(
        """
dataset: isotropic1024coarse
snapshots:
  calibration:
    - time: null
      origin: [null, null, null]
      size: [128, 128, 128]
      source: sciserver
  validation:
    - time: null
      origin: [null, null, null]
      size: [128, 128, 128]
      source: sciserver
resolution_tiers: [64, 128, 256]
terminal_layer:
  preferred_shells: 8
  minimum_shells: 6
  minimum_populated_shells: 4
  cutoff_nyquist_fraction: null
placements:
  local_cancellation: {}
classification:
  data_is_real: true
"""
    )
    with pytest.raises(ManifestValidationError):
        load_manifest(str(blank))


def test_1_manifest_validation_accepts_filled_manifest():
    m = load_manifest(SYNTHETIC_MANIFEST)
    assert m.dataset == "synthetic_test"


# 2. Preflight failure without SciServer --------------------------------
def test_2_preflight_fails_without_sciserver_when_required(tmp_path):
    m = load_manifest(SYNTHETIC_MANIFEST)
    sciserver_snapshot = SnapshotSpec(time=0.0, origin=(0, 0, 0), size=(64, 64, 64), source="sciserver")
    m2 = m.__class__(
        **{**m.__dict__, "calibration_snapshots": (sciserver_snapshot,) + m.calibration_snapshots}
    )
    report = run_preflight(m2, str(tmp_path))
    assert report.passed is False
    names = {c.name: c for c in report.checks}
    assert names["sciserver_import"].blocking is True
    assert names["sciserver_import"].passed is False


# 3. Immutable run creation ----------------------------------------------
def test_3_completed_run_has_identity_and_is_idempotent(completed_run):
    output, identity = completed_run
    assert identity.status == "completed"
    assert (output / "run_identity.json").exists()

    identity2 = rrv.run(SYNTHETIC_MANIFEST, str(output), skip_tests=True)
    assert identity2.run_id == identity.run_id
    assert identity2.status == "completed"


def test_3_refuses_to_overwrite_different_run(tmp_path, completed_run):
    output, _identity = completed_run
    modified = tmp_path / "modified.yaml"
    modified.write_text(Path(SYNTHETIC_MANIFEST).read_text().replace("time: 12.0", "time: 13.0"))

    with pytest.raises(rrv.RunAbortedError, match="Refusing to overwrite"):
        rrv.run(str(modified), str(output), skip_tests=True)


# 4. Interrupted-run recovery ---------------------------------------------
def test_4_interrupted_run_recovers_with_resume(tmp_path):
    output = tmp_path / "interrupted"
    output.mkdir()
    identity = rrv.run(SYNTHETIC_MANIFEST, str(output), skip_tests=True)
    assert identity.status == "completed"

    # Roll back to simulate a crash right after the "selection" stage --
    # keep the genuine selection_stage.json (a real crash would have
    # written it before updating the checkpoint) and mark status running.
    ident = RunIdentity.from_json((output / "run_identity.json").read_text())
    ident.status = "running"
    ident.end_time = None
    (output / "run_identity.json").write_text(ident.to_json())
    (output / "checkpoint.json").write_text(json.dumps({"completed_stages": ["selection"]}))

    with pytest.raises(rrv.RunAbortedError, match="interrupted"):
        rrv.run(SYNTHETIC_MANIFEST, str(output), skip_tests=True)  # no --resume

    resumed = rrv.run(SYNTHETIC_MANIFEST, str(output), skip_tests=True, resume=True)
    assert resumed.status == "completed"


# 5. Calibration/validation separation -------------------------------------
def test_5_overlapping_snapshots_rejected_at_manifest_load(tmp_path):
    bad = tmp_path / "overlap.yaml"
    bad.write_text(Path(SYNTHETIC_MANIFEST).read_text().replace("time: 10.0", "time: 0.0"))
    with pytest.raises(ManifestValidationError, match="overlap"):
        load_manifest(str(bad))


# 6. Placement conservation failures surfaced, not silently dropped --------
def test_6_placement_statuses_are_only_ok_or_blocked_never_silently_wrong(completed_run):
    output, _identity = completed_run
    df = pd.read_json(output / "validation_stage.json")
    assert set(df["status"].unique()) <= {"ok", "blocked"}
    if (df["status"] == "blocked").any():
        blocked = df[df["status"] == "blocked"]
        assert blocked["flux_relative_l2_error"].isna().all()


def test_6_conservation_failure_is_deterministically_surfaced_as_blocked(tmp_path):
    # A parent_band with a band that has essentially no DNS energy in it
    # (c1/c2 extremely close together) cannot satisfy return-power
    # conservation -- compare_placements_on_snapshot must report this as
    # a blocked status with a reason, never as a silently-passing "ok".
    import numpy as np

    from jhtdb_terminal_benchmark import Config
    from placement_comparison import compare_placements_on_snapshot

    cfg = Config(parent_band_c1=0.999, parent_band_c2=0.9995)
    rng = np.random.default_rng(0)
    velocity = rng.normal(size=(64, 64, 64, 3))

    result = compare_placements_on_snapshot(velocity, cfg, str(tmp_path))
    entry = result["per_placement"]["parent_band_energy_weighted"]
    assert entry["status"] == "blocked"
    assert "reason" in entry and len(entry["reason"]) > 0


# 7. Synthetic-data report warning ------------------------------------------
def test_7_report_carries_synthetic_data_warning(completed_run):
    output, _identity = completed_run
    report = json.loads((output / "report" / "milestone5_report.json").read_text())
    assert report["data_is_real"] is False
    assert "SYNTHETIC" in report["data_provenance_warning"]
    assert "WARNING" in (output / "report" / "milestone5_report.md").read_text()


# 8. Real-data assertion requirement -----------------------------------------
def test_8_real_data_assertion_blocks_synthetic_source():
    spec = SnapshotSpec(time=0.0, origin=(0, 0, 0), size=(32, 32, 32), source="synthetic")
    with pytest.raises(DataSourceError, match="data_is_real"):
        resolve_data_source(spec, data_is_real=True)


# 9. Report and output hashing ------------------------------------------------
def test_9_output_hashes_are_present_and_correct(completed_run):
    output, identity = completed_run
    assert identity.output_hashes
    any_relpath = next(iter(identity.output_hashes))
    assert sha256_file(output / any_relpath) == identity.output_hashes[any_relpath]


# 10. Deterministic rerun behavior --------------------------------------------
def test_10_run_id_is_deterministic_for_same_manifest_and_code():
    h = manifest_hash(SYNTHETIC_MANIFEST)
    id1 = compute_run_id(h, {"dataset": "synthetic_test", "data_is_real": False})
    id2 = compute_run_id(h, {"dataset": "synthetic_test", "data_is_real": False})
    assert id1 == id2
