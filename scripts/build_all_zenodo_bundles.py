import hashlib
import json
import os
import zipfile
from pathlib import Path

ROOT = Path(r"d:\Comfy UI")
REPORTS_DIR = ROOT / "tubulance" / "reports"

PDF1 = REPORTS_DIR / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf"
PDF2 = REPORTS_DIR / "CONTEMPORARY_UNCONDITIONAL_CHIRAL_SCHUR_AND_HODGE_BSD_ELEVATOR_RESEARCH_PAPER.pdf"
PDF2_ALT = REPORTS_DIR / "CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.pdf"
PDF3 = REPORTS_DIR / "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf"
PDF_COMM = REPORTS_DIR / "COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.pdf"

print("Checking source PDFs...")
for p in [PDF1, PDF2, PDF2_ALT, PDF3, PDF_COMM]:
    assert p.exists(), f"Missing PDF: {p}"
    print(f"  [OK] {p.name} ({p.stat().st_size} bytes)")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. HODGE BUNDLE
hodge_zip = ROOT / "HODGE_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"
print(f"\nBuilding {hodge_zip.name}...")
with zipfile.ZipFile(hodge_zip, "w", zipfile.ZIP_DEFLATED) as z:
    ws = ROOT / "hodge conjecture"
    for ext in ["*.lean", "*.json", "*.md", "*.py", "*.toml"]:
        for f in ws.glob(ext):
            if ".git" not in str(f) and ".lake" not in str(f):
                z.write(f, arcname=f"hodge_conjecture/{f.name}")
    if (ws / "reports").exists():
        for f in (ws / "reports").glob("*.*"):
            z.write(f, arcname=f"hodge_conjecture/reports/{f.name}")
    z.write(PDF1, arcname=f"papers/01_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF2, arcname=f"papers/02_Hodge_BSD_E4_Dimensional_Elevator_and_Unconditional_Horizon_Paper.pdf")
    z.write(PDF3, arcname=f"papers/03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
print(f"  [SUCCESS] {hodge_zip.name} ({hodge_zip.stat().st_size} bytes, SHA-256: {sha256_file(hodge_zip)})")

# 2. YANG-MILLS BUNDLE
ym_zip = ROOT / "YANG_MILLS_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"
print(f"\nBuilding {ym_zip.name}...")
with zipfile.ZipFile(ym_zip, "w", zipfile.ZIP_DEFLATED) as z:
    ws = ROOT / "yang mills and the mass gap"
    for ext in ["*.lean", "*.json", "*.md", "*.py", "*.toml"]:
        for f in ws.glob(ext):
            if ".git" not in str(f) and ".lake" not in str(f):
                z.write(f, arcname=f"yang_mills/{f.name}")
    if (ws / "reports").exists():
        for f in (ws / "reports").glob("*.*"):
            z.write(f, arcname=f"yang_mills/reports/{f.name}")
    z.write(PDF1, arcname=f"papers/01_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF2, arcname=f"papers/02_Hodge_BSD_E4_Dimensional_Elevator_and_Unconditional_Horizon_Paper.pdf")
    z.write(PDF3, arcname=f"papers/03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
print(f"  [SUCCESS] {ym_zip.name} ({ym_zip.stat().st_size} bytes, SHA-256: {sha256_file(ym_zip)})")

# 3. RIEMANN BUNDLE
riemann_zip = ROOT / "RIEMANN_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"
print(f"\nBuilding {riemann_zip.name}...")
with zipfile.ZipFile(riemann_zip, "w", zipfile.ZIP_DEFLATED) as z:
    ws = ROOT / "rheihman hypothesis"
    for ext in ["*.lean", "*.json", "*.md", "*.py", "*.toml"]:
        for f in ws.glob(ext):
            if ".git" not in str(f) and ".lake" not in str(f):
                z.write(f, arcname=f"riemann_hypothesis/{f.name}")
    if (ws / "reports").exists():
        for f in (ws / "reports").glob("*.*"):
            z.write(f, arcname=f"riemann_hypothesis/reports/{f.name}")
    if (ws / "scripts").exists():
        for f in (ws / "scripts").glob("*.py"):
            z.write(f, arcname=f"riemann_hypothesis/scripts/{f.name}")
    z.write(PDF1, arcname=f"papers/01_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF2, arcname=f"papers/02_Hodge_BSD_E4_Dimensional_Elevator_and_Unconditional_Horizon_Paper.pdf")
    z.write(PDF3, arcname=f"papers/03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
print(f"  [SUCCESS] {riemann_zip.name} ({riemann_zip.stat().st_size} bytes, SHA-256: {sha256_file(riemann_zip)})")

# 4. BSD BUNDLE
bsd_zip = ROOT / "BSD_E4_ELEVATOR_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"
print(f"\nBuilding {bsd_zip.name}...")
with zipfile.ZipFile(bsd_zip, "w", zipfile.ZIP_DEFLATED) as z:
    ws = ROOT / "birch and swinnerton dyer"
    for ext in ["*.lean", "*.json", "*.md", "*.py", "*.toml"]:
        for f in ws.glob(ext):
            if ".git" not in str(f) and ".lake" not in str(f):
                z.write(f, arcname=f"birch_swinnerton_dyer/{f.name}")
    for sub in ["formal", "scripts", "reports", "dist"]:
        if (ws / sub).exists():
            for f in (ws / sub).rglob("*.*"):
                if ".git" not in str(f):
                    rel = f.relative_to(ws)
                    z.write(f, arcname=f"birch_swinnerton_dyer/{rel}")
    z.write(PDF1, arcname=f"papers/01_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF2, arcname=f"papers/02_Hodge_BSD_E4_Dimensional_Elevator_and_Unconditional_Horizon_Paper.pdf")
    z.write(PDF3, arcname=f"papers/03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
print(f"  [SUCCESS] {bsd_zip.name} ({bsd_zip.stat().st_size} bytes, SHA-256: {sha256_file(bsd_zip)})")

# 5. CONTEMPORARY CHIRAL VRAM AND SCHUR COMPUTE BUNDLE
compute_zip = ROOT / "CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip"
print(f"\nBuilding {compute_zip.name}...")
with zipfile.ZipFile(compute_zip, "w", zipfile.ZIP_DEFLATED) as z:
    ws = ROOT / "tubulance"
    z.write(PDF1, arcname="01_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF2, arcname="02_Hodge_BSD_E4_Dimensional_Elevator_and_Unconditional_Horizon_Paper.pdf")
    z.write(PDF3, arcname="03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
    z.write(PDF_COMM, arcname="COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.pdf")
    for f in (ws / "tare_core").glob("*.py"):
        z.write(f, arcname=f"tare_core/{f.name}")
    for f in REPORTS_DIR.glob("*.*"):
        if f.suffix in [".pdf", ".tex", ".md", ".json"]:
            z.write(f, arcname=f"reports/{f.name}")
    if (ws / ".zenodo.json").exists():
        z.write(ws / ".zenodo.json", arcname=".zenodo.json")
    if (ws / "GITHUB_RELEASE_NOTES.md").exists():
        z.write(ws / "GITHUB_RELEASE_NOTES.md", arcname="GITHUB_RELEASE_NOTES.md")
print(f"  [SUCCESS] {compute_zip.name} ({compute_zip.stat().st_size} bytes, SHA-256: {sha256_file(compute_zip)})")

print("\nAll individual workspace Zenodo bundles created successfully!")
