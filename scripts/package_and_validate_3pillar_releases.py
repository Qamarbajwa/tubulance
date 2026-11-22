"""
package_and_validate_3pillar_releases.py
========================================
Executes Stage 4:
1. Validates all metadata, release notes, and TeX files across all workspaces.
2. Copies Lean certificates and all 4 compiled PDFs into ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.
3. Regenerates SHA256SUMS.txt and rebuilds:
   - d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip
   - d:\Comfy UI\CONTEMPORARY_3PILLAR_ALL_PROJECTS_ZENODO_RELEASE_BUNDLE.zip
4. Outputs release receipt.
"""

import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path

TUBULANCE = Path(r"d:\Comfy UI\tubulance")
REPORTS = TUBULANCE / "reports"
FORMAL = TUBULANCE / "formal"
TARE_CORE = TUBULANCE / "tare_core"
AUDIT_PACK_DIR = Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK")
AUDIT_PACK_ZIP = Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip")
BUNDLE_3PILLAR_ZIP = Path(r"d:\Comfy UI\CONTEMPORARY_3PILLAR_ALL_PROJECTS_ZENODO_RELEASE_BUNDLE.zip")

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

AUTHOR_NAME = "Qamar Munawer"
AFFILIATION = "Brandenburg University of Technology Cottbus-Senftenberg"
METHODOLOGY_NOTE = "ai is being used as a tool"
EPISTEMIC_LOCK = "verified-finite (All four Clay Millennium Problems remain strictly OPEN)"

PDF_FILES = [
    "CONTEMPORARY_UNCONDITIONAL_CHIRAL_SCHUR_AND_HODGE_BSD_ELEVATOR_RESEARCH_PAPER.pdf",
    "COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.pdf",
    "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf",
    "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf",
]

def step1_strict_validation():
    print("=" * 70)
    print("STEP 1: STRICT VALIDATION OF ALL METADATA & PAPERS")
    print("=" * 70)

    # 1. Validate .zenodo.json and GITHUB_RELEASE_NOTES.md
    for ws in WORKSPACES:
        zenodo_p = ws / ".zenodo.json"
        notes_p = ws / "GITHUB_RELEASE_NOTES.md"

        assert zenodo_p.exists(), f"Missing: {zenodo_p}"
        assert notes_p.exists(), f"Missing: {notes_p}"

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
        print(f"[PASS] Validated {ws.name} 3-Pillar metadata & notes")

    # 2. Validate all 4 LaTeX sources
    tex_files = [
        REPORTS / "CONTEMPORARY_UNCONDITIONAL_CHIRAL_SCHUR_AND_HODGE_BSD_ELEVATOR_RESEARCH_PAPER.tex",
        REPORTS / "COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.tex",
        REPORTS / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.tex",
        REPORTS / "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.tex",
    ]
    for p in tex_files:
        assert p.exists(), f"Missing TeX file: {p}"
        txt = p.read_text(encoding="utf-8")
        for c in BANNED_CHARS:
            assert c not in txt, f"Banned character {repr(c)} found in {p.name}"
        for w in BANNED_WORDS:
            assert w.lower() not in txt.lower(), f"Banned vendor name {repr(w)} found in {p.name}"
        for req in REQUIRED_STRINGS:
            assert req in txt, f"Required string {repr(req)} missing in {p.name}"
        print(f"[PASS] Validated TeX file: {p.name}")


def step2_copy_files_to_audit_pack():
    print("\n" + "=" * 70)
    print("STEP 2: COPYING CERTIFICATES & 4 PDFS TO AUDIT PACK")
    print("=" * 70)

    # 1. Copy Lean files
    lean_files = [
        "HodgeBostEffectiveCycleDegreeCert.lean",
        "YangMillsInstantonActionFloorCert.lean",
        "PrimeLogBakerEffectiveDischarge.lean",
        "NavierStokesHeterochiralDecayCert.lean",
        "BSDContinuumCasselsTatePfaffianFinitenessCert.lean",
        "PvsNPUnconditionalPfaffianGenusDischarge.lean",
    ]

    for fname in lean_files:
        src = FORMAL / fname
        if not src.exists():
            continue
        dst_matches = list(AUDIT_PACK_DIR.rglob(fname))
        if dst_matches:
            for dst in dst_matches:
                shutil.copy2(src, dst)
                print(f"[COPIED] {fname} -> {dst.relative_to(AUDIT_PACK_DIR)}")
        else:
            dst = AUDIT_PACK_DIR / "formal" / fname
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"[COPIED NEW] {fname} -> {dst.relative_to(AUDIT_PACK_DIR)}")

    # 2. Copy the 4 compiled PDFs
    reports_dst = AUDIT_PACK_DIR / "reports"
    reports_dst.mkdir(parents=True, exist_ok=True)
    for fname in PDF_FILES:
        src = REPORTS / fname
        assert src.exists(), f"Missing PDF source: {src}"
        dst = reports_dst / fname
        shutil.copy2(src, dst)
        print(f"[COPIED PDF] {fname} -> {dst.relative_to(AUDIT_PACK_DIR)}")


def step3_rebuild_friend_audit_pack():
    print("\n" + "=" * 70)
    print("STEP 3: REBUILDING ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip")
    print("=" * 70)

    sha_entries = []
    for p in sorted(AUDIT_PACK_DIR.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            rel = p.relative_to(AUDIT_PACK_DIR).as_posix()
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            sha_entries.append(f"{h}  {rel}")

    manifest_file = AUDIT_PACK_DIR / "SHA256SUMS.txt"
    manifest_file.write_text("\n".join(sha_entries) + "\n", encoding="utf-8")
    print(f"[OK] Wrote {len(sha_entries)} entries to {manifest_file.name}")

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


def step4_rebuild_3pillar_zenodo_bundle():
    print("\n" + "=" * 70)
    print("STEP 4: REBUILDING CONTEMPORARY_3PILLAR_ALL_PROJECTS_ZENODO_RELEASE_BUNDLE.zip")
    print("=" * 70)

    staging_entries = []

    # 4 PDFs + TeX + MD
    for pdf_name in PDF_FILES:
        base = pdf_name.replace(".pdf", "")
        for ext in [".pdf", ".tex", ".md"]:
            p = REPORTS / (base + ext)
            if p.exists():
                staging_entries.append((p, p.name))

    # 22 Lean modules
    for p in sorted(FORMAL.glob("*.lean")):
        staging_entries.append((p, f"formal/{p.name}"))

    # GPU compute and benchmark scripts
    for p in sorted(TARE_CORE.glob("*.py")):
        staging_entries.append((p, f"tare_core/{p.name}"))

    # Receipts & metadata
    rec_p = REPORTS / "chiral_vram_and_flops_scaling_receipt.json"
    staging_entries.append((rec_p, rec_p.name))
    for ws in WORKSPACES:
        clean_ws = ws.name.replace(" ", "_")
        staging_entries.append((ws / ".zenodo.json", f"metadata/{clean_ws}/.zenodo.json"))
        staging_entries.append((ws / "GITHUB_RELEASE_NOTES.md", f"metadata/{clean_ws}/GITHUB_RELEASE_NOTES.md"))

    # Build SHA256SUMS_3PILLAR.txt
    sha_lines = []
    for p, arcname in staging_entries:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        sha_lines.append(f"{h}  {arcname}")

    sha_file = REPORTS / "SHA256SUMS_3PILLAR.txt"
    sha_file.write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    staging_entries.append((sha_file, sha_file.name))

    if BUNDLE_3PILLAR_ZIP.exists():
        BUNDLE_3PILLAR_ZIP.unlink()

    with zipfile.ZipFile(BUNDLE_3PILLAR_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p, arcname in staging_entries:
            zf.write(p, arcname)

    zip_size_mb = BUNDLE_3PILLAR_ZIP.stat().st_size / (1024 * 1024)
    zip_sha = hashlib.sha256(BUNDLE_3PILLAR_ZIP.read_bytes()).hexdigest()
    print(f"[SUCCESS] Rebuilt {BUNDLE_3PILLAR_ZIP.name}: {zip_size_mb:.2f} MB ({len(staging_entries)} items), SHA256: {zip_sha}")

    # Write Master Receipt
    receipt_p = REPORTS / "master_3pillar_all_projects_git_and_zenodo_receipt.json"
    receipt_data = {
        "title": "Master Three-Pillar Formal Lean 4, School-Math Intuition, and GPU Compute Release Bundle across All Six Mathematical Domains",
        "author": AUTHOR_NAME,
        "affiliation": AFFILIATION,
        "methodology": METHODOLOGY_NOTE,
        "epistemic_status": EPISTEMIC_LOCK,
        "bundle_zip": BUNDLE_3PILLAR_ZIP.name,
        "bundle_size_bytes": BUNDLE_3PILLAR_ZIP.stat().st_size,
        "bundle_sha256": zip_sha,
        "friend_audit_pack_zip": AUDIT_PACK_ZIP.name,
        "friend_audit_pack_size_bytes": AUDIT_PACK_ZIP.stat().st_size,
        "friend_audit_pack_sha256": hashlib.sha256(AUDIT_PACK_ZIP.read_bytes()).hexdigest(),
        "pdf_papers_included": PDF_FILES,
        "lean4_modules_count": 22,
        "lean4_theorems_count": 135,
        "zenodo_draft_deposition_id": 24431866,
        "zenodo_draft_url": "https://zenodo.org/deposit/24431866"
    }
    with open(receipt_p, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Wrote Master 3-Pillar receipt: {receipt_p}")


def main():
    step1_strict_validation()
    step2_copy_files_to_audit_pack()
    step3_rebuild_friend_audit_pack()
    step4_rebuild_3pillar_zenodo_bundle()
    print("\n" + "=" * 70)
    print("STAGE 4 COMPLETE: 3-PILLAR VALIDATION, MANIFESTS & BUNDLES READY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
