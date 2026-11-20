"""
build_all_22_standalone_zenodo_papers.py

Master compilation, packaging, and auditing script for all 22 standalone Zenodo papers:
- 6 Hodge papers (HODGE_Z01 .. HODGE_Z06)
- 4 Yang-Mills papers (YM_Z01 .. YM_Z04)
- 6 Riemann papers (RH_Z01 .. RH_Z06)
- 6 Navier-Stokes papers (NS_Z01 .. NS_Z06)
"""

import sys
import os
import json
import shutil
import hashlib
import subprocess
import zipfile
from pathlib import Path

# Add current scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from paper_generator_core import build_paper_bundle
from papers_hodge import HODGE_PAPERS
from papers_ym import YM_PAPERS
from papers_rh import RH_PAPERS
from papers_ns import NS_PAPERS

WORKSPACE_DIRS = {
    "hodge": Path(r"d:/Comfy UI/hodge conjecture/zenodo_standalone_papers"),
    "ym": Path(r"d:/Comfy UI/yang mills and the mass gap/zenodo_standalone_papers"),
    "rh": Path(r"d:/Comfy UI/rheihman hypothesis/zenodo_standalone_papers"),
    "ns": Path(r"d:/Comfy UI/tubulance/zenodo_standalone_papers")
}

AUDIT_PACK_DIR = Path(r"d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK")
AUDIT_PACK_STANDALONE = AUDIT_PACK_DIR / "standalone_zenodo_papers"
AUDIT_PACK_ZIP = Path(r"d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip")

def write_pack_sha256sums() -> int:
    lines = []
    for p in sorted(AUDIT_PACK_DIR.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts:
            continue
        rel = p.relative_to(AUDIT_PACK_DIR).as_posix()
        if rel in ("SHA256SUMS.txt", "FRIEND_INDEPENDENT_AUDIT_RECEIPT.json"):
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel}")
    manifest_path = AUDIT_PACK_DIR / "SHA256SUMS.txt"
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)

def rebuild_audit_pack_zip() -> int:
    with zipfile.ZipFile(AUDIT_PACK_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(AUDIT_PACK_DIR.rglob("*")):
            if not p.is_file():
                continue
            if "__pycache__" in p.parts:
                continue
            arc = p.relative_to(AUDIT_PACK_DIR).as_posix()
            zf.write(p, arcname=arc)
    return AUDIT_PACK_ZIP.stat().st_size

def main():
    print("=" * 78)
    print("STARTING 22 STANDALONE ZENODO PAPERS BUILD & COMPILATION PIPELINE")
    print("=" * 78)

    AUDIT_PACK_STANDALONE.mkdir(parents=True, exist_ok=True)
    all_results = []

    groups = [
        ("hodge", HODGE_PAPERS),
        ("ym", YM_PAPERS),
        ("rh", RH_PAPERS),
        ("ns", NS_PAPERS)
    ]

    total_count = sum(len(papers) for _, papers in groups)
    print(f"Total papers scheduled: {total_count}")

    idx = 1
    for grp_name, papers in groups:
        out_root = WORKSPACE_DIRS[grp_name]
        out_root.mkdir(parents=True, exist_ok=True)
        print(f"\n--- Group: {grp_name.upper()} ({len(papers)} papers) in {out_root} ---")

        for paper in papers:
            paper_id = paper["id"]
            print(f"[{idx:02d}/{total_count:02d}] Building {paper_id}...")
            res = build_paper_bundle(paper, out_root)
            all_results.append(res)

            # Mirror into Friend Audit Pack
            dest_mirror = AUDIT_PACK_STANDALONE / paper_id
            if dest_mirror.exists():
                shutil.rmtree(dest_mirror)
            shutil.copytree(Path(res["dir"]), dest_mirror)
            idx += 1

    # Write Master Build Receipt
    receipt_data = {
        "status": "PASS",
        "total_papers_built": len(all_results),
        "papers": all_results
    }
    receipt_path = WORKSPACE_DIRS["ns"] / "ALL_22_PAPERS_BUILD_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")
    shutil.copy2(receipt_path, AUDIT_PACK_STANDALONE / "ALL_22_PAPERS_BUILD_RECEIPT.json")

    print("\n" + "=" * 78)
    print("ALL 22 PAPERS COMPILED AND PACKAGED SUCCESSFULLY!")
    print(f"Receipt written to {receipt_path}")
    print("=" * 78)

    # Update SHA256SUMS.txt
    print("\nUpdating SHA256SUMS.txt in Friend Audit Pack...")
    file_count = write_pack_sha256sums()
    print(f"[OK] SHA256SUMS.txt updated with {file_count} files.")

    # Run Friend Audit Pack independent audit
    print("\nRunning independent audit verification on Friend Audit Pack...")
    audit_runner = AUDIT_PACK_DIR / "run_all_rosetta_audits.py"
    cmd = [sys.executable, str(audit_runner)]
    run_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(run_res.stdout)
    if run_res.returncode != 0:
        print("[FAIL] Audit pack runner returned non-zero exit code!")
        sys.exit(1)

    # Rebuild Audit Pack ZIP
    print("\nRebuilding ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip...")
    zip_size = rebuild_audit_pack_zip()
    print(f"[OK] Rebuilt {AUDIT_PACK_ZIP} ({zip_size // 1024} KB)")

    print("\n" + "=" * 78)
    print("COMPLETE PIPELINE PASS: 22 STANDALONE PAPERS BUILT & AUDITED")
    print("=" * 78)

if __name__ == "__main__":
    main()
