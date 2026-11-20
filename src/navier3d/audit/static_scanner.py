"""Static Code Scanner for Hardcoded Benchmark Results.

Implements Section 8 of Milestone V0.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List


SUSPICIOUS_PATTERNS = [
    (r"expected_speedup\s*=\s*\d+(\.\d+)?", "Hardcoded speedup variable assignment"),
    (r"reported_error\s*=\s*\d+(\.\d+)?", "Hardcoded reported error assignment"),
    (r"benchmark_result\s*=\s*\{.*'E_u':\s*0\.\d+.*\}", "Hardcoded benchmark result dictionary"),
    (r"result\.error\s*=\s*0\.\d+", "Hardcoded result object mutation"),
]


def scan_codebase_for_hardcoded_results(search_path: str | Path) -> List[Dict[str, Any]]:
    """Scan Python files for hardcoded result metrics or fabricated result assignments.

    Distinguishes assertion tolerances (e.g. assert error < 0.05) from fabricated result assignments.
    """
    search_path = Path(search_path)
    violations = []

    for root, _, files in os.walk(search_path):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = Path(root) / file
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception:
                continue

            for line_no, line in enumerate(lines, start=1):
                # Skip comments and explicit tolerance assertions
                stripped = line.strip()
                if stripped.startswith("#") or "assert " in stripped:
                    continue

                for pattern, desc in SUSPICIOUS_PATTERNS:
                    if re.search(pattern, line):
                        violations.append({
                            "file": str(file_path),
                            "line_no": line_no,
                            "line_content": line.strip(),
                            "pattern": pattern,
                            "description": desc,
                        })

    return violations
