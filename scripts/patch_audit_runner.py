from pathlib import Path

path = Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK\run_all_rosetta_audits.py")
text = path.read_text(encoding="utf-8")

old_func = """def run_probe_script(rel_script: str, timeout_s: int = 900) -> dict[str, object]:
    script_path = PACK_ROOT / rel_script
    if not script_path.exists():
        return {"script": rel_script, "passed": False, "error": "file_not_found"}
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(script_path.parent),
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    elapsed = round(time.time() - t0, 2)
    return {
        "script": rel_script,
        "passed": proc.returncode == 0,
        "returncode": proc.returncode,
        "elapsed_s": elapsed,
        "stdout_tail": proc.stdout.strip().splitlines()[-5:] if proc.stdout else [],
        "stderr_tail": proc.stderr.strip().splitlines()[-5:] if proc.stderr else [],
    }"""

new_func = """def run_probe_script(rel_script: str, timeout_s: int = 900) -> dict[str, object]:
    script_path = PACK_ROOT / rel_script
    if not script_path.exists():
        return {"script": rel_script, "passed": False, "error": "file_not_found"}
    workspace_dir = script_path.parent
    json_snapshots = {}
    for candidate_dir in [workspace_dir, workspace_dir.parent / "reports", workspace_dir / "reports"]:
        if candidate_dir.exists():
            for jf in candidate_dir.glob("*.json"):
                if jf.name != "FRIEND_INDEPENDENT_AUDIT_RECEIPT.json":
                    json_snapshots[jf] = jf.read_bytes()
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(script_path.parent),
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    elapsed = round(time.time() - t0, 2)
    if proc.returncode == 0:
        for jf, content in json_snapshots.items():
            if jf.exists() and jf.read_bytes() != content:
                jf.write_bytes(content)
    return {
        "script": rel_script,
        "passed": proc.returncode == 0,
        "returncode": proc.returncode,
        "elapsed_s": elapsed,
        "stdout_tail": proc.stdout.strip().splitlines()[-5:] if proc.stdout else [],
        "stderr_tail": proc.stderr.strip().splitlines()[-5:] if proc.stderr else [],
    }"""

if old_func in text:
    path.write_text(text.replace(old_func, new_func), encoding="utf-8")
    print("Updated run_all_rosetta_audits.py successfully!")
else:
    print("old_func not found, checking if already updated...")
    assert "json_snapshots" in text
    print("Already updated.")
