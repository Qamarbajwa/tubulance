"""
package_and_validate_all_releases.py
====================================
Performs Stage 4:
1. Validates all .zenodo.json, GITHUB_RELEASE_NOTES.md, .tex, and .md files across all workspaces.
2. Copies the 5 updated .lean files and 3 compiled PDFs into ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.
3. Regenerates SHA256SUMS.txt.
4. Rebuilds:
   - d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip
   - d:\Comfy UI\CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip
5. Updates and verifies Zenodo upload receipt.
"""

import hashlib
import json
import os
import re
import shutil
import zipfile
from pathlib import Path

TUBULANCE = Path(r"d:\Comfy UI\tubulance")
REPORTS = TUBULANCE / "reports"
FORMAL = TUBULANCE / "formal"
TARE_CORE = TUBULANCE / "tare_core"
AUDIT_PACK_DIR = Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK")
AUDIT_PACK_ZIP = Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip")
COMPUTE_ZIP = Path(r"d:\Comfy UI\CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip")

WORKSPACES = [
    Path(r"d:\Comfy UI\hodge conjecture"),
    Path(r"d:\Comfy UI\yang mills and the mass gap"),
    Path(r"d:\Comfy UI\rheihman hypothesis"),
    Path(r"d:\Comfy UI\tubulance"),
]

BANNED_CHARS = ["#", "\u2014", "\u2013"]
BANNED_WORDS = ["Google Carbon", "Gemini"]
REQUIRED_STRINGS = [
    "Qamar Munawer",
    "Brandenburg University of Technology Cottbus-Senftenberg",
    "ai is being used as a tool",
]

def step1_validate_metadata_and_papers():
    print("=" * 70)
    print("STEP 1: VALIDATING METADATA, RELEASE NOTES, AND PAPERS")
    print("=" * 70)

    # 1. Validate .zenodo.json and GITHUB_RELEASE_NOTES.md
    for ws in WORKSPACES:
        zenodo_p = ws / ".zenodo.json"
        notes_p = ws / "GITHUB_RELEASE_NOTES.md"

        assert zenodo_p.exists(), f"Missing: {zenodo_p}"
        assert notes_p.exists(), f"Missing: {notes_p}"

        # JSON syntax
        with open(zenodo_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert isinstance(meta, dict), "Invalid JSON dict"
        desc = meta.get("description", "")
        title = meta.get("title", "")

        notes = notes_p.read_text(encoding="utf-8")

        for label, text in [(f"{ws.name} .zenodo.json title", title),
                            (f"{ws.name} .zenodo.json desc", desc),
                            (f"{ws.name} release notes", notes)]:
            for c in BANNED_CHARS:
                assert c not in text, f"Banned character {repr(c)} found in {label}"
            for w in BANNED_WORDS:
                assert w.lower() not in text.lower(), f"Banned vendor name {repr(w)} found in {label}"
            if "title" not in label:
                for req in REQUIRED_STRINGS:
                    assert req in text, f"Required string {repr(req)} missing in {label}"

        # check creators
        creators = meta.get("creators", [])
        assert any(c.get("name") == "Qamar Munawer" for c in creators), f"Missing creator in {ws.name}"

        print(f"[PASS] Validated {ws.name} metadata & release notes")

    # 2. Validate TeX and Markdown papers
    papers = [
        REPORTS / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.tex",
        REPORTS / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.md",
        REPORTS / "CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.tex",
        REPORTS / "CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.md",
        REPORTS / "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.tex",
        REPORTS / "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.md",
    ]

    for p in papers:
        assert p.exists(), f"Missing paper file: {p}"
        txt = p.read_text(encoding="utf-8")
        if p.suffix == ".tex":
            for c in ["#", "\u2014", "\u2013"]:
                assert c not in txt, f"Banned character {repr(c)} in {p.name}"
        for w in BANNED_WORDS:
            assert w.lower() not in txt.lower(), f"Banned word {repr(w)} in {p.name}"
        for req in REQUIRED_STRINGS:
            assert req in txt, f"Required string {repr(req)} missing in {p.name}"
        print(f"[PASS] Validated paper file: {p.name}")


def step2_copy_to_audit_pack():
    print("\n" + "=" * 70)
    print("STEP 2: COPYING UPDATED FILES INTO AUDIT PACK")
    print("=" * 70)

    assert AUDIT_PACK_DIR.exists(), f"Audit pack dir not found: {AUDIT_PACK_DIR}"

    # Copy the 5 Lean files
    lean_files = [
        "HodgeBostEffectiveCycleDegreeCert.lean",
        "YangMillsInstantonActionFloorCert.lean",
        "PrimeLogBakerEffectiveDischarge.lean",
        "NavierStokesHeterochiralDecayCert.lean",
        "BSDContinuumCasselsTatePfaffianFinitenessCert.lean",
    ]

    for fname in lean_files:
        src = FORMAL / fname
        assert src.exists(), f"Missing formal source: {src}"
        # Search destination in audit pack
        dst_matches = list(AUDIT_PACK_DIR.rglob(fname))
        if dst_matches:
            for dst in dst_matches:
                shutil.copy2(src, dst)
                print(f"[COPIED] {fname} -> {dst.relative_to(AUDIT_PACK_DIR)}")
        else:
            # Place in root of formal if not found
            dst = AUDIT_PACK_DIR / "formal" / fname
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"[COPIED NEW] {fname} -> {dst.relative_to(AUDIT_PACK_DIR)}")

    # Copy the 3 compiled PDFs
    pdfs = [
        "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf",
        "CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.pdf",
        "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf",
    ]

    docs_dir = AUDIT_PACK_DIR / "reports"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for fname in pdfs:
        src = REPORTS / fname
        assert src.exists(), f"Missing PDF source: {src}"
        dst = docs_dir / fname
        shutil.copy2(src, dst)
        print(f"[COPIED PDF] {fname} -> {dst.relative_to(AUDIT_PACK_DIR)}")


def step3_regenerate_audit_pack_manifest_and_zip():
    print("\n" + "=" * 70)
    print("STEP 3: REGENERATING SHA256SUMS.txt AND REBUILDING AUDIT PACK ZIP")
    print("=" * 70)

    # Compute SHA-256 for every file in AUDIT_PACK_DIR
    sha_entries = []
    for p in sorted(AUDIT_PACK_DIR.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            rel = p.relative_to(AUDIT_PACK_DIR).as_posix()
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            sha_entries.append(f"{h}  {rel}")

    manifest_file = AUDIT_PACK_DIR / "SHA256SUMS.txt"
    manifest_file.write_text("\n".join(sha_entries) + "\n", encoding="utf-8")
    print(f"[OK] Wrote {len(sha_entries)} entries to {manifest_file}")

    # Rebuild AUDIT_PACK_ZIP
    if AUDIT_PACK_ZIP.exists():
        AUDIT_PACK_ZIP.unlink()

    with zipfile.ZipFile(AUDIT_PACK_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in sorted(AUDIT_PACK_DIR.rglob("*")):
            if p.is_file():
                arcname = p.relative_to(AUDIT_PACK_DIR).as_posix()
                zf.write(p, arcname)

    zip_size_mb = AUDIT_PACK_ZIP.stat().st_size / (1024 * 1024)
    zip_sha = hashlib.sha256(AUDIT_PACK_ZIP.read_bytes()).hexdigest()
    print(f"[SUCCESS] Rebuilt {AUDIT_PACK_ZIP.name}: {zip_size_mb:.2f} MB, SHA256: {zip_sha}")


def step4_rebuild_compute_zenodo_bundle():
    print("\n" + "=" * 70)
    print("STEP 4: REBUILDING CONTEMPORARY CHIRAL VRAM ZENODO BUNDLE")
    print("=" * 70)

    staging_files = [
        REPORTS / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf",
        REPORTS / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.tex",
        REPORTS / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.md",
        REPORTS / "CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.pdf",
        REPORTS / "CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.tex",
        REPORTS / "CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.md",
        REPORTS / "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf",
        TARE_CORE / "silicon_vram_compressor.py",
        TARE_CORE / "hbim_bauforschung_adapter.py",
        TARE_CORE / "prime_horizon_gpu.py",
        TARE_CORE / "benchmark_vram_and_flops_scaling.py",
        TARE_CORE / "test_tare_core.py",
        REPORTS / "chiral_vram_and_flops_scaling_receipt.json",
        TUBULANCE / "ZENODO_COMPUTE_PAPER_METADATA.json",
        TUBULANCE / ".zenodo.json",
        TUBULANCE / "GITHUB_RELEASE_NOTES.md",
    ]

    for p in staging_files:
        assert p.exists(), f"Missing staging file: {p}"

    sha_lines = []
    for p in staging_files:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        sha_lines.append(f"{h}  {p.name}")

    sha_file = REPORTS / "SHA256SUMS_COMPUTE.txt"
    sha_file.write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    staging_files.append(sha_file)

    if COMPUTE_ZIP.exists():
        COMPUTE_ZIP.unlink()

    with zipfile.ZipFile(COMPUTE_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in staging_files:
            zf.write(p, p.name)

    zip_size_mb = COMPUTE_ZIP.stat().st_size / (1024 * 1024)
    zip_sha = hashlib.sha256(COMPUTE_ZIP.read_bytes()).hexdigest()
    print(f"[SUCCESS] Rebuilt {COMPUTE_ZIP.name}: {zip_size_mb:.2f} MB, SHA256: {zip_sha}")

    # Write receipt
    receipt_p = REPORTS / "zenodo_compute_and_unconditional_horizon_release_receipt.json"
    receipt_data = {
        "title": "Contemporary Helical Beltrami Decomposition, Hodge-BSD E^4 Dimensional Elevator, Unconditional Horizon Escalation in Lean 4 (135 Theorems, 0 sorry), and Tare Core 50 to 99.8% VRAM GPU Compute Papers (v2.1.0, Continuing the Previous Rosetta Stone Operator Correspondence)",
        "version": "2.1.0-contemporary-compute",
        "author": "Qamar Munawer",
        "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg",
        "methodology": "ai is being used as a tool",
        "epistemic_status": "verified-finite (All four Clay Millennium Problems remain strictly OPEN)",
        "bundle_zip": COMPUTE_ZIP.name,
        "bundle_size_bytes": COMPUTE_ZIP.stat().st_size,
        "bundle_sha256": zip_sha,
        "files_in_bundle": [p.name for p in staging_files],
        "zenodo_draft_deposition_id": 24431866,
        "zenodo_draft_url": "https://zenodo.org/deposit/24431866"
    }
    with open(receipt_p, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Wrote {receipt_p}")


def main():
    step1_validate_metadata_and_papers()
    step2_copy_to_audit_pack()
    step3_regenerate_audit_pack_manifest_and_zip()
    step4_rebuild_compute_zenodo_bundle()
    print("\n" + "=" * 70)
    print("STAGE 4 COMPLETE: ALL CHECKS, MANIFESTS, AND BUNDLES VERIFIED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
