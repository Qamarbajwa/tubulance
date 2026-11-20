"""Static Dependency and Security Checker for Research Experiment Code.

Implements Section 8, 9 of Milestone V1 and Section 22 of Milestone V2.2.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import List, Tuple


class StaticDependencyError(ImportError):
    """Raised when experimental code imports verifier modules or attempts prohibited external root access."""


def assert_no_verifier_imports_in_experiment(repo_dir: str | Path = ".", raise_on_error: bool = False) -> List[Tuple[Path, str]]:
    """Scan all project python files outside verifier/ for imports of verifier modules."""
    repo_path = Path(repo_dir)
    prohibited_files: List[Tuple[Path, str]] = []

    for root, _, files in os.walk(repo_path):
        rel_root = Path(root).relative_to(repo_path)
        # Skip verifier, tests, build, and hidden directories
        parts = rel_root.parts
        if any(p in ("verifier", "tests", ".git", ".pytest_cache", "__pycache__", "venv") for p in parts):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                try:
                    tree = ast.parse(content, filename=str(file_path))
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name == "verifier" or alias.name.startswith("verifier."):
                                prohibited_files.append((file_path, alias.name))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and (node.module == "verifier" or node.module.startswith("verifier.")):
                            prohibited_files.append((file_path, node.module))

    if prohibited_files and raise_on_error:
        details = "\n".join(f"  - {p[0]} imports '{p[1]}'" for p in prohibited_files)
        raise StaticDependencyError(
            f"STATIC DEPENDENCY CHECK FAILED!\n"
            f"Experimental code contains direct imports of verifier modules:\n{details}\n"
            f"The research agent is FORBIDDEN from importing verifier internal functions inside experiment solvers!"
        )

    return prohibited_files


def assert_no_project_scripts_write_external_root(repo_dir: str | Path = ".") -> None:
    """Scan codebase ensuring project scripts do not attempt to write to external trust root paths."""
    repo_path = Path(repo_dir)
    violating_files = []

    target_keywords = ["production_root.json", "EXTERNAL_VERIFIER_ROOT_PATH"]

    for root, _, files in os.walk(repo_path):
        rel_root = Path(root).relative_to(repo_path)
        parts = rel_root.parts
        # Skip tests directory for this static scan as tests simulate/verify boundary behaviors
        if any(p in ("tests", ".git", ".pytest_cache", "__pycache__", "venv") for p in parts):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for kw in target_keywords:
                    if kw in content:
                        # Check for write mode open / write_text
                        lines = content.splitlines()
                        for idx, line in enumerate(lines, 1):
                            if kw in line and any(w in line for w in ['"w"', "'w'", '"wb"', "'wb'", '"a"', "'a'", "write_text"]):
                                violating_files.append((file_path, idx, line.strip()))

    if violating_files:
        details = "\n".join(f"  - {v[0]}:{v[1]} -> '{v[2]}'" for v in violating_files)
        raise RuntimeError(
            f"PROHIBITED EXTERNAL ROOT WRITE ATTEMPT DETECTED!\n"
            f"Project scripts contain write calls targeting external trust root:\n{details}\n"
            f"Repository scripts are strictly FORBIDDEN from modifying external trust root production_root.json!"
        )
