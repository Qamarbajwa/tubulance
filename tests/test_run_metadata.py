from jhtdb_terminal_benchmark import Config, TerminalLayer
from run_metadata import build_run_metadata, spatial_origin_from_local_h5


def test_spatial_origin_from_local_h5_reads_real_attrs():
    origin = spatial_origin_from_local_h5("isotropic1024coarse.h5")
    assert origin.start_xyz == (100, 100, 100)
    assert origin.size_xyz == (16, 16, 16)
    assert origin.stride_xyz == (1, 1, 1)
    assert "isotropic1024coarse.h5" in origin.source


def test_build_run_metadata_reports_not_recorded_when_unavailable():
    cfg = Config()
    layer = TerminalLayer(kc=16.0, ks=8.0, delta_k=1.0, n_t=8.0, beta_effective=0.5, source="beta")

    metadata = build_run_metadata(cfg, layer, nyquist=32.0)

    assert metadata["spatial_origin"]["note"].startswith("not recorded")
    assert metadata["time_coordinate"]["note"].startswith("not recorded")
    assert "forcing_kmax not confirmed" in metadata["forcing_separation"]["note"]
    assert metadata["kc"] == 16.0
    assert metadata["nyquist_separation"]["nyquist_minus_kc"] == 16.0


def test_build_run_metadata_uses_supplied_spatial_origin_and_forcing():
    cfg = Config(forcing_kmax=2.0)
    layer = TerminalLayer(kc=16.0, ks=8.0, delta_k=1.0, n_t=8.0, beta_effective=0.5, source="beta")
    origin = spatial_origin_from_local_h5("isotropic1024coarse.h5")

    metadata = build_run_metadata(
        cfg,
        layer,
        nyquist=32.0,
        spatial_origin=origin,
        runtime_seconds=1.5,
        peak_memory_mb=12.0,
        populated_terminal_shells=5,
    )

    assert metadata["spatial_origin"]["start_xyz"] == (100, 100, 100)
    assert metadata["forcing_separation"]["gap_ks_minus_forcing_kmax"] == 6.0
    assert metadata["runtime_seconds"] == 1.5
    assert metadata["populated_terminal_shells"] == 5
