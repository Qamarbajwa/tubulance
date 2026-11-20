import sys, subprocess, time
from pathlib import Path

root = Path(r"d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK")
text = (root / "run_all_rosetta_audits.py").read_text(encoding="utf-8")
import re
m = re.search(r"probes = \[(.*?)\]", text, re.DOTALL)
for p in m.group(1).splitlines():
    p = p.strip().strip('",')
    if p.endswith(".py"):
        script_path = root / p
        t0 = time.time()
        if "test_prime_dimensions" in p:
            print(f"{p:<75} [SKIPPED FOR QUICK CHECK]")
            continue
        proc = subprocess.run([sys.executable, str(script_path)], cwd=str(script_path.parent), capture_output=True, text=True, timeout=60)
        status = "PASS" if proc.returncode == 0 else "FAIL"
        elapsed = round(time.time() - t0, 2)
        print(f"{p:<75} [{status}] ({elapsed}s)")
        if proc.returncode != 0:
            print("  STDERR:", proc.stderr)
            print("  STDOUT:", proc.stdout)
