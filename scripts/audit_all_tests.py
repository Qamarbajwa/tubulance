"""Execute all repository tests and record full test report."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


def main():
    t0 = time.time()
    cmd = ["python", "-m", "pytest", "-q"]
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - t0

    stdout = res.stdout
    stderr = res.stderr
    print("Execution completed in", round(duration, 2), "s")
    print("Exit code:", res.returncode)
    print("Summary line (tail):")
    lines = [l.strip() for l in stdout.strip().splitlines() if l.strip()]
    for l in lines[-5:]:
        print("  ", l)

    # Parse passed, failed, skipped, warnings
    # e.g., "798 passed, 3 skipped, 3 warnings in 450.12s"
    report = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "exit_code": res.returncode,
        "duration_sec": round(duration, 2),
        "stdout_tail": lines[-10:],
        "raw_stdout": stdout,
        "raw_stderr": stderr,
    }

    with open("FULL_TEST_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("Saved to FULL_TEST_REPORT.json")


if __name__ == "__main__":
    main()
