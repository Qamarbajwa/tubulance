import numpy as np
import pytest

from jhtdb_terminal_benchmark import (
    Config,
    SnapshotSeparationError,
    assert_snapshot_separation,
    compute_terminal_layer,
    validate_terminal_layer,
)


def test_compute_terminal_layer_uses_beta_when_sufficient():
    cfg = Config(beta=0.56, min_terminal_shells=6, preferred_terminal_shells=8)
    layer = compute_terminal_layer(kc=16.0, delta_k=1.0, cfg=cfg)
    assert layer.source == "beta"
    assert layer.ks == pytest.approx(0.56 * 16.0)
    assert layer.n_t == pytest.approx(16.0 - 0.56 * 16.0)
    assert layer.n_t >= cfg.min_terminal_shells


def test_compute_terminal_layer_falls_back_to_resolution_derived():
    # beta=0.56 on a small kc gives too few shells -> must switch strategy.
    cfg = Config(beta=0.56, min_terminal_shells=6, preferred_terminal_shells=8)
    layer = compute_terminal_layer(kc=4.0, delta_k=1.0, cfg=cfg)
    assert layer.source == "resolution_derived"
    # kc - preferred_terminal_shells * delta_k = 4 - 8 = -4 -> clamped to 0
    assert layer.ks == 0.0
    assert layer.n_t == pytest.approx(4.0)


def test_compute_terminal_layer_clamps_ks_to_zero_when_kc_too_small():
    cfg = Config(beta=0.9, min_terminal_shells=6, preferred_terminal_shells=8)
    layer = compute_terminal_layer(kc=3.0, delta_k=1.0, cfg=cfg)
    assert layer.ks >= 0.0
    assert layer.n_t == pytest.approx(layer.kc - layer.ks)


def _shells_and_energy(kmax, terminal_shells, populated=True, floor=1e-20):
    shells = np.arange(kmax + 1)
    e = np.ones_like(shells, dtype=float)
    if not populated:
        for s in terminal_shells:
            if 0 <= s <= kmax:
                e[s] = floor / 10.0
    return shells, e


def test_validate_terminal_layer_flags_insufficient_shells():
    cfg = Config(min_terminal_shells=6)
    layer = compute_terminal_layer(kc=4.0, delta_k=1.0, cfg=cfg)  # n_t will be < 6
    shells, e_dns = _shells_and_energy(kmax=16, terminal_shells=range(0, 5))
    failures = validate_terminal_layer(layer, nyquist=32.0, shells=shells, e_dns=e_dns, cfg=cfg)
    assert any("N_T" in f for f in failures)


def test_validate_terminal_layer_flags_insufficient_populated_shells():
    cfg = Config(beta=0.5, min_terminal_shells=6, min_populated_terminal_shells=4, energy_floor=1e-20)
    layer = compute_terminal_layer(kc=16.0, delta_k=1.0, cfg=cfg)
    shells, e_dns = _shells_and_energy(kmax=32, terminal_shells=range(8, 17), populated=False)
    failures = validate_terminal_layer(layer, nyquist=32.0, shells=shells, e_dns=e_dns, cfg=cfg)
    assert any("measurable DNS energy" in f for f in failures)


def test_validate_terminal_layer_flags_cutoff_near_nyquist():
    cfg = Config(beta=0.5, min_terminal_shells=2, max_cutoff_fraction_of_nyquist=0.8)
    layer = compute_terminal_layer(kc=30.0, delta_k=1.0, cfg=cfg)
    shells, e_dns = _shells_and_energy(kmax=32, terminal_shells=range(15, 31))
    failures = validate_terminal_layer(layer, nyquist=32.0, shells=shells, e_dns=e_dns, cfg=cfg)
    assert any("Nyquist" in f for f in failures)


def test_validate_terminal_layer_flags_forcing_gap():
    cfg = Config(
        beta=0.5,
        min_terminal_shells=2,
        forcing_kmax=2.0,
        min_forcing_terminal_gap_shells=5.0,
    )
    layer = compute_terminal_layer(kc=6.0, delta_k=1.0, cfg=cfg)  # ks=3.0, gap to forcing=1.0 < 5.0
    shells, e_dns = _shells_and_energy(kmax=16, terminal_shells=range(3, 7))
    failures = validate_terminal_layer(layer, nyquist=32.0, shells=shells, e_dns=e_dns, cfg=cfg)
    assert any("forcing" in f for f in failures)


def test_validate_terminal_layer_passes_when_all_ok():
    cfg = Config(beta=0.5, min_terminal_shells=6, min_populated_terminal_shells=4)
    layer = compute_terminal_layer(kc=16.0, delta_k=1.0, cfg=cfg)
    shells, e_dns = _shells_and_energy(kmax=32, terminal_shells=range(8, 17))
    failures = validate_terminal_layer(layer, nyquist=32.0, shells=shells, e_dns=e_dns, cfg=cfg)
    assert failures == []


def test_assert_snapshot_separation_raises_on_overlap():
    cfg = Config(
        calibration_snapshots=(("isotropic1024coarse", 1.0),),
        validation_snapshots=(("isotropic1024coarse", 1.0), ("isotropic1024coarse", 2.0)),
    )
    with pytest.raises(SnapshotSeparationError):
        assert_snapshot_separation(cfg)


def test_assert_snapshot_separation_passes_when_disjoint():
    cfg = Config(
        calibration_snapshots=(("isotropic1024coarse", 1.0),),
        validation_snapshots=(("isotropic1024coarse", 2.0),),
    )
    assert_snapshot_separation(cfg) is None
