from manifest import load_manifest
from preflight import (
    check_calibration_validation_separation,
    check_placement_parameters,
    check_real_data_assertion,
    check_shell_count_requirements,
    predicted_terminal_layer,
    run_preflight,
)


def _synthetic_manifest():
    return load_manifest("manifests/synthetic_dry_run.yaml")


def test_run_preflight_passes_overall_for_pure_synthetic_manifest():
    # No snapshot uses source='sciserver', so the SciServer/Giverny/mount/
    # auth checks are informational (non-blocking) here -- a manifest that
    # never needs SciServer must not be blocked by its absence.
    m = _synthetic_manifest()
    report = run_preflight(m, "runs/test_preflight")
    names = {c.name: c for c in report.checks}
    assert names["sciserver_import"].passed is False
    assert names["sciserver_import"].blocking is False
    assert report.passed is True


def test_run_preflight_blocks_on_missing_sciserver_when_manifest_needs_it():
    m = _synthetic_manifest()
    from manifest import SnapshotSpec

    sciserver_snapshot = SnapshotSpec(time=0.0, origin=(0, 0, 0), size=(64, 64, 64), source="sciserver")
    m_real = m.__class__(
        **{
            **m.__dict__,
            "calibration_snapshots": (sciserver_snapshot,) + m.calibration_snapshots,
        }
    )
    report = run_preflight(m_real, "runs/test_preflight")
    names = {c.name: c for c in report.checks}
    assert names["sciserver_import"].blocking is True
    assert report.passed is False


def test_run_preflight_environment_independent_checks_pass_for_synthetic_manifest():
    m = _synthetic_manifest()
    report = run_preflight(m, "runs/test_preflight")
    names = {c.name: c for c in report.checks}
    assert names["shell_count_requirements"].passed is True
    assert names["calibration_validation_separation"].passed is True
    assert names["placement_parameters"].passed is True
    assert names["real_data_assertion"].passed is True


def test_predicted_terminal_layer_matches_manifest_cutoff():
    m = _synthetic_manifest()
    layer = predicted_terminal_layer(64, m)
    assert layer.kc == 0.5 * 32.0  # cutoff_nyquist_fraction=0.5, nyquist=grid_n/2
    assert layer.n_t >= m.terminal_layer.minimum_shells


def test_check_shell_count_requirements_flags_inadequate_tier():
    m = _synthetic_manifest()
    # 16^3 at cutoff_fraction=0.5 gives kc=4, far below what's needed for N_T>=6
    m16 = m.__class__(**{**m.__dict__, "resolution_tiers": (16,)})
    check = check_shell_count_requirements(m16)
    assert check.passed is False
    assert "16" in check.detail


def test_check_real_data_assertion_flags_synthetic_source_with_real_flag():
    m = _synthetic_manifest()
    m_real = m.__class__(**{**m.__dict__, "data_is_real": True})
    check = check_real_data_assertion(m_real)
    assert check.passed is False


def test_check_calibration_validation_separation_passes_for_disjoint_sets():
    m = _synthetic_manifest()
    check = check_calibration_validation_separation(m)
    assert check.passed is True


def test_check_placement_parameters_fails_when_c1_c2_missing():
    m = _synthetic_manifest()
    from manifest import PlacementSpec

    bad_placements = tuple(
        PlacementSpec(name="parent_band_energy_weighted", params={}, enabled=True)
        if p.name == "parent_band_energy_weighted"
        else p
        for p in m.placements
    )
    m_bad = m.__class__(**{**m.__dict__, "placements": bad_placements})
    check = check_placement_parameters(m_bad)
    assert check.passed is False
