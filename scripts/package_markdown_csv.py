"""Package all markdown and CSV files in the project into a single zip archive."""
from __future__ import annotations

import zipfile
from pathlib import Path

def main():
    root = Path(".")
    zip_path = Path("tubulance_markdown_and_csv_reports.zip")

    md_files = sorted(list(root.glob("**/*.md")))
    csv_files = sorted(list(root.glob("**/*.csv")))

    exclude_dirs = {".git", ".pytest_cache", "__pycache__", "venv", ".venv", "env"}

    selected_files = []
    for p in md_files + csv_files:
        if any(part in exclude_dirs for part in p.parts):
            continue
        selected_files.append(p)

    num_md = len([f for f in selected_files if f.suffix.lower() == ".md"])
    num_csv = len([f for f in selected_files if f.suffix.lower() == ".csv"])

    print(f"Total files found: {len(selected_files)} ({num_md} Markdown files, {num_csv} CSV files)")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in selected_files:
            zipf.write(file_path, arcname=str(file_path.as_posix()))

    sz = zip_path.stat().st_size
    print(f"Created zip archive: {zip_path.resolve()} ({sz:,} bytes)")

if __name__ == "__main__":
    main()
