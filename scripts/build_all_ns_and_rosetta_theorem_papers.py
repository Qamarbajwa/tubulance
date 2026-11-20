"""
build_all_ns_and_rosetta_theorem_papers.py

Master compilation, packaging, and auditing script for:
- Paper 00: The Master 4-Workspace & 7-Domain Common-Person Relational Guide
- Papers T01 through T05: 3D Navier-Stokes Theorem Modules
- Papers T06 through T10: Cross-Workspace Rosetta Theorem Modules

Generates LaTeX source files, compiles them via pdflatex (two passes each, 0 errors),
packages individual Zenodo release bundles with Lean certificates and JSON probe receipts,
copies all PDFs into ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK, regenerates SHA256SUMS.txt,
and rebuilds ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip.
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
import zipfile
from pathlib import Path

# Add current scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from paper_generator_core import build_paper_bundle
from papers_rosetta_common import PAPER_00
from papers_ns_theorems import NS_THEOREMS_PAPERS
from papers_rosetta_theorems import ROSETTA_THEOREMS_PAPERS
from build_p_vs_np_t11_paper import PAPER_T11
from papers_bsd_t12 import PAPER_T12

ALL_13_PAPERS = [PAPER_00] + NS_THEOREMS_PAPERS + ROSETTA_THEOREMS_PAPERS + [PAPER_T11, PAPER_T12]

TUBULANCE_DIR = Path(r"d:/Comfy UI/tubulance")
ZENODO_PAPERS_DIR = TUBULANCE_DIR / "zenodo_theorem_papers"

AUDIT_PACK_DIR = Path(r"d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK")
AUDIT_PACK_ZIP = Path(r"d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip")

HODGE_PAPERS_DIR = AUDIT_PACK_DIR / "01_hodge_conjecture/papers"
YM_PAPERS_DIR = AUDIT_PACK_DIR / "02_yang_mills_4d/papers"
RH_PAPERS_DIR = AUDIT_PACK_DIR / "03_riemann_hypothesis/papers"
NS_PAPERS_DIR = AUDIT_PACK_DIR / "04_navier_stokes_3d/papers"

def write_pack_sha256sums() -> int:
    lines = []
    for p in sorted(AUDIT_PACK_DIR.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix == ".pyc":
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
            if "__pycache__" in p.parts or p.suffix == ".pyc":
                continue
            arc = p.relative_to(AUDIT_PACK_DIR).as_posix()
            zf.write(p, arcname=arc)
    return AUDIT_PACK_ZIP.stat().st_size

def main():
    print("=" * 78)
    print("STARTING 13 STANDALONE ROSETTA, NS, P vs NP & BSD PAPERS BUILD PIPELINE")
    print("=" * 78)

    ZENODO_PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []

    for idx, paper in enumerate(ALL_13_PAPERS):
        paper_id = paper["id"]
        print(f"\n[{idx+1}/13] Compiling and packaging: {paper_id}...")
        try:
            res = build_paper_bundle(paper, ZENODO_PAPERS_DIR)
            print(f"      -> PASS: PDF ({res['pdf_bytes']} bytes), ZIP ({res['zip_bytes']} bytes)")
            all_results.append({
                "id": paper_id,
                "title": paper["title"],
                "status": "PASS",
                "pdf_path": res["pdf_path"],
                "zip_path": res["zip_path"],
                "pdf_bytes": res["pdf_bytes"],
                "zip_bytes": res["zip_bytes"]
            })
        except Exception as e:
            print(f"      -> FAIL: {e}")
            all_results.append({
                "id": paper_id,
                "title": paper["title"],
                "status": "FAIL",
                "error": str(e)
            })

    # Verify all passed
    failed = [r for r in all_results if r["status"] != "PASS"]
    if failed:
        print("\n" + "!" * 78)
        print(f"ABORTING: {len(failed)} papers failed compilation!")
        for f in failed:
            print(f" - {f['id']}: {f.get('error', 'unknown error')}")
        print("!" * 78)
        return 1

    print("\n" + "=" * 78)
    print("ALL 13 PAPERS COMPILED SUCCESSFULLY! DISTRIBUTING TO AUDIT PACK...")
    print("=" * 78)

    # 1. Distribute Paper 00
    p00_pdf = ZENODO_PAPERS_DIR / "ROSETTA_00_What_Is_Happening_And_What_Relates_To_What_Master_Common_Person_Guide/ROSETTA_00_What_Is_Happening_And_What_Relates_To_What_Master_Common_Person_Guide.pdf"
    if p00_pdf.exists():
        shutil.copy2(p00_pdf, AUDIT_PACK_DIR / p00_pdf.name)
        for dest_dir in (HODGE_PAPERS_DIR, YM_PAPERS_DIR, RH_PAPERS_DIR, NS_PAPERS_DIR):
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p00_pdf, dest_dir / p00_pdf.name)
        print(f" -> Distributed Paper 00 to audit pack root and all 4 workspaces' papers/ directories.")

    # 1b. Distribute all 4 Common-Person Guides to audit pack root
    guides = [
        HODGE_PAPERS_DIR / "HODGE_00_What_Is_Happening_And_What_Relates_To_What_Common_Person_Guide.pdf",
        YM_PAPERS_DIR / "YM_00_What_Is_Happening_And_What_Relates_To_What_Common_Person_Guide.pdf",
        RH_PAPERS_DIR / "RH_00_What_Is_Happening_And_What_Relates_To_What_Common_Person_Guide.pdf",
    ]
    for g in guides:
        if g.exists():
            shutil.copy2(g, AUDIT_PACK_DIR / g.name)
            print(f" -> Copied {g.name} to audit pack root.")

    # 2. Distribute T01 through T05 to NS_PAPERS_DIR
    for p in NS_THEOREMS_PAPERS:
        pdf_file = ZENODO_PAPERS_DIR / p["id"] / f"{p['id']}.pdf"
        if pdf_file.exists():
            shutil.copy2(pdf_file, NS_PAPERS_DIR / pdf_file.name)
            print(f" -> Copied {pdf_file.name} to 04_navier_stokes_3d/papers/")

    # 3. Distribute T06 through T10 (Cross-Workspace) to all 4 workspaces' papers/ dirs
    for p in ROSETTA_THEOREMS_PAPERS:
        pdf_file = ZENODO_PAPERS_DIR / p["id"] / f"{p['id']}.pdf"
        if pdf_file.exists():
            for dest_dir in (HODGE_PAPERS_DIR, YM_PAPERS_DIR, RH_PAPERS_DIR, NS_PAPERS_DIR):
                shutil.copy2(pdf_file, dest_dir / pdf_file.name)
            print(f" -> Copied cross-workspace {pdf_file.name} to all 4 workspaces' papers/ dirs")

    # 3b. Distribute T11 (P vs NP) and T12 (BSD) to all 4 workspaces' papers/ dirs
    for p in [PAPER_T11, PAPER_T12]:
        pdf_file = ZENODO_PAPERS_DIR / p["id"] / f"{p['id']}.pdf"
        if pdf_file.exists():
            for dest_dir in (HODGE_PAPERS_DIR, YM_PAPERS_DIR, RH_PAPERS_DIR, NS_PAPERS_DIR):
                shutil.copy2(pdf_file, dest_dir / pdf_file.name)
            print(f" -> Copied {pdf_file.name} to all 4 workspaces' papers/ dirs")

    # 3c. Sync Lean certificates and probes into audit pack
    lean_certs = [
        TUBULANCE_DIR / "formal/PvsNPContinuumPfaffianGenusBarrierCert.lean",
        TUBULANCE_DIR / "formal/BSDContinuumCasselsTatePfaffianFinitenessCert.lean",
    ]
    for lc in lean_certs:
        if lc.exists():
            shutil.copy2(lc, AUDIT_PACK_DIR / "04_navier_stokes_3d/lean4_certificates" / lc.name)
            print(f" -> Synced {lc.name} to 04_navier_stokes_3d/lean4_certificates/")

    probe_files = [
        TUBULANCE_DIR / "scripts/probe_continuum_p_vs_np_pfaffian_genus.py",
        TUBULANCE_DIR / "probes/probe_continuum_p_vs_np_pfaffian_genus_receipt.json",
        TUBULANCE_DIR / "scripts/probe_continuum_bsd_sha_pfaffian_finiteness.py",
        TUBULANCE_DIR / "probes/probe_continuum_bsd_sha_pfaffian_finiteness_receipt.json",
    ]
    for pf in probe_files:
        if pf.exists():
            shutil.copy2(pf, AUDIT_PACK_DIR / "04_navier_stokes_3d/probes" / pf.name)
            print(f" -> Synced {pf.name} to 04_navier_stokes_3d/probes/")

    # 4. Regenerate SHA256SUMS.txt
    print("\nRegenerating SHA256SUMS.txt for ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK...")
    file_count = write_pack_sha256sums()
    print(f" -> Manifest updated with {file_count} files.")

    # 5. Rebuild audit pack ZIP
    print("\nRebuilding ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip...")
    zip_size = rebuild_audit_pack_zip()
    print(f" -> ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip rebuilt ({zip_size:,} bytes).")

    print("\n" + "=" * 78)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 78)
    for r in all_results:
        print(f" - {r['id']:<70} [{r['status']}] ({r.get('pdf_bytes', 0):,} bytes)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
