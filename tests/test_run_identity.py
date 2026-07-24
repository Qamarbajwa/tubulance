from pathlib import Path

from run_identity import (
    RunIdentity,
    compute_run_id,
    git_info,
    hardware_info,
    hash_directory,
    new_run_identity,
    package_versions,
    sha256_bytes,
    sha256_file,
)


def test_sha256_file_matches_sha256_bytes(tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("hello world")
    assert sha256_file(p) == sha256_bytes(b"hello world")


def test_hash_directory_covers_all_files(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("b")

    hashes = hash_directory(tmp_path)
    assert set(hashes) == {"a.txt", str(Path("sub") / "b.txt")}


def test_git_info_reports_current_repo():
    info = git_info(".")
    assert info["available"] is True
    assert info["commit"] is not None
    assert len(info["commit"]) == 40


def test_compute_run_id_is_deterministic_for_same_inputs():
    id1 = compute_run_id("abc123", {"dataset": "x"})
    id2 = compute_run_id("abc123", {"dataset": "x"})
    assert id1 == id2


def test_compute_run_id_differs_for_different_manifest_hash():
    id1 = compute_run_id("abc123", {"dataset": "x"})
    id2 = compute_run_id("def456", {"dataset": "x"})
    assert id1 != id2


def test_package_versions_reports_numpy():
    versions = package_versions()
    assert versions["numpy"] is not None


def test_hardware_info_has_cpu_count():
    info = hardware_info()
    assert info["cpu_count"] is not None and info["cpu_count"] > 0


def test_new_run_identity_round_trips_through_json():
    identity = new_run_identity("manifests/synthetic_dry_run.yaml", "deadbeef", "abc123", seed=0)
    text = identity.to_json()
    restored = RunIdentity.from_json(text)
    assert restored.run_id == "deadbeef"
    assert restored.manifest_hash == "abc123"
    assert restored.status == "running"
