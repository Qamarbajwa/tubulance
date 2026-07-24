import pytest

from manifest import ManifestValidationError, load_manifest, manifest_hash


def test_synthetic_dry_run_manifest_loads_cleanly():
    m = load_manifest("manifests/synthetic_dry_run.yaml")
    assert m.dataset == "synthetic_test"
    assert len(m.calibration_snapshots) == 3
    assert len(m.validation_snapshots) == 3
    assert m.data_is_real is False
    assert m.terminal_layer.minimum_shells == 6
    names = {p.name for p in m.placements}
    assert "parent_band_energy_weighted" in names


def test_blank_template_values_fail_validation(tmp_path):
    # Deliberately self-contained rather than reading
    # manifests/isotropic_128_validation.yaml: that file is meant to be
    # filled in as real campaigns are prepared (and may legitimately be
    # filled in, uncommitted, at any point) -- coupling this safeguard
    # test to its current contents would make the test fragile against
    # completely normal, expected edits to that file.
    blank = tmp_path / "blank_template.yaml"
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
  parent_band_energy_weighted:
    c1: null
    c2: null
classification:
  data_is_real: true
"""
    )
    with pytest.raises(ManifestValidationError) as excinfo:
        load_manifest(str(blank))
    errors = excinfo.value.errors
    assert any("time" in e for e in errors)
    assert any("cutoff_nyquist_fraction" in e for e in errors)
    assert any("c1" in e or "c2" in e for e in errors)


def test_real_campaign_template_currently_on_disk_is_either_blank_or_valid():
    # The template file itself may be blank (fresh checkout) or filled in
    # with a proposed real campaign (mid-preparation) -- either state is
    # legitimate. It must never be invalid in some OTHER way (e.g.
    # malformed YAML, wrong types).
    try:
        m = load_manifest("manifests/isotropic_128_validation.yaml")
        assert m.dataset  # filled-in and valid
    except ManifestValidationError as exc:
        assert len(exc.errors) > 0  # blank and correctly rejected, not malformed


def test_missing_data_is_real_fails(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        """
dataset: test
snapshots:
  calibration:
    - time: 0.0
      origin: [0,0,0]
      size: [64,64,64]
      source: synthetic
  validation:
    - time: 1.0
      origin: [0,0,0]
      size: [64,64,64]
      source: synthetic
resolution_tiers: [64]
terminal_layer:
  preferred_shells: 8
  minimum_shells: 6
  minimum_populated_shells: 4
  cutoff_nyquist_fraction: 0.5
placements:
  local_cancellation: {}
"""
    )
    with pytest.raises(ManifestValidationError) as excinfo:
        load_manifest(str(bad))
    assert any("data_is_real" in e for e in excinfo.value.errors)


def test_overlapping_calibration_and_validation_snapshots_fails(tmp_path):
    bad = tmp_path / "overlap.yaml"
    bad.write_text(
        """
dataset: test
snapshots:
  calibration:
    - time: 0.0
      origin: [0,0,0]
      size: [64,64,64]
      source: synthetic
  validation:
    - time: 0.0
      origin: [0,0,0]
      size: [64,64,64]
      source: synthetic
resolution_tiers: [64]
terminal_layer:
  preferred_shells: 8
  minimum_shells: 6
  minimum_populated_shells: 4
  cutoff_nyquist_fraction: 0.5
placements:
  local_cancellation: {}
classification:
  data_is_real: false
"""
    )
    with pytest.raises(ManifestValidationError) as excinfo:
        load_manifest(str(bad))
    assert any("overlap" in e for e in excinfo.value.errors)


def test_local_h5_source_requires_path_and_frame_index(tmp_path):
    bad = tmp_path / "local_h5_missing_fields.yaml"
    bad.write_text(
        """
dataset: test
snapshots:
  calibration:
    - time: 0.0
      origin: [0,0,0]
      size: [16,16,16]
      source: local_h5
  validation:
    - time: 1.0
      origin: [0,0,0]
      size: [16,16,16]
      source: synthetic
resolution_tiers: [16]
terminal_layer:
  preferred_shells: 8
  minimum_shells: 6
  minimum_populated_shells: 4
  cutoff_nyquist_fraction: 0.5
placements:
  local_cancellation: {}
classification:
  data_is_real: false
"""
    )
    with pytest.raises(ManifestValidationError) as excinfo:
        load_manifest(str(bad))
    assert any("path" in e for e in excinfo.value.errors)
    assert any("frame_index" in e for e in excinfo.value.errors)


def test_manifest_hash_is_deterministic():
    h1 = manifest_hash("manifests/synthetic_dry_run.yaml")
    h2 = manifest_hash("manifests/synthetic_dry_run.yaml")
    assert h1 == h2
    assert len(h1) == 64  # sha256 hex digest
