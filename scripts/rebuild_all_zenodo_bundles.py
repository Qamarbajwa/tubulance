import hashlib
import json
import os
import zipfile
from pathlib import Path

ROOT = Path(r"d:\Comfy UI")
REPORTS_DIR = ROOT / "tubulance" / "reports"

PDF_COMPUTE = REPORTS_DIR / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf"
PDF_HODGE = ROOT / "hodge conjecture" / "reports" / "HODGE_CHIRAL_SPIN8_AND_MODULI_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf"
PDF_YM = ROOT / "yang mills and the mass gap" / "reports" / "YANG_MILLS_CHIRAL_SELF_DUAL_AND_BALABAN_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf"
PDF_RH = ROOT / "rheihman hypothesis" / "reports" / "RIEMANN_CHIRAL_REFLECTION_UNCERTAINTY_AND_PRIME_HORIZON_PAPER_2026_11_22.pdf"
PDF_NS = REPORTS_DIR / "NAVIER_STOKES_HELICAL_TRIAD_AND_P_VS_NP_PFAFFIAN_UNIFIED_PAPER_2026_11_22.pdf"
PDF_BSD = ROOT / "birch and swinnerton dyer" / "reports" / "CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.pdf"
PDF_APPX = REPORTS_DIR / "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf"
PDF_COMM = REPORTS_DIR / "COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.pdf"

all_pdfs = [PDF_COMPUTE, PDF_HODGE, PDF_YM, PDF_RH, PDF_NS, PDF_BSD, PDF_APPX, PDF_COMM]

print("Checking source PDFs...")
for p in all_pdfs:
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
    if (ws / "examples" / "math_gov" / "LeanMillenniumExt").exists():
        for f in (ws / "examples" / "math_gov" / "LeanMillenniumExt").glob("*.lean"):
            z.write(f, arcname=f"hodge_conjecture/LeanMillenniumExt/{f.name}")
    z.write(PDF_HODGE, arcname=f"papers/01_HODGE_CHIRAL_SPIN8_AND_MODULI_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf")
    z.write(PDF_COMPUTE, arcname=f"papers/02_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF_APPX, arcname=f"papers/03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
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
    if (ws / "formal").exists():
        for f in (ws / "formal").glob("*.lean"):
            z.write(f, arcname=f"yang_mills/formal/{f.name}")
    if (ws / "reports").exists():
        for f in (ws / "reports").glob("*.*"):
            z.write(f, arcname=f"yang_mills/reports/{f.name}")
    z.write(PDF_YM, arcname=f"papers/01_YANG_MILLS_CHIRAL_SELF_DUAL_AND_BALABAN_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf")
    z.write(PDF_COMPUTE, arcname=f"papers/02_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF_APPX, arcname=f"papers/03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
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
    if (ws / "RiemannBlueprint").exists():
        for f in (ws / "RiemannBlueprint").glob("*.lean"):
            z.write(f, arcname=f"riemann_hypothesis/RiemannBlueprint/{f.name}")
    if (ws / "reports").exists():
        for f in (ws / "reports").glob("*.*"):
            z.write(f, arcname=f"riemann_hypothesis/reports/{f.name}")
    z.write(PDF_RH, arcname=f"papers/01_RIEMANN_CHIRAL_REFLECTION_UNCERTAINTY_AND_PRIME_HORIZON_PAPER_2026_11_22.pdf")
    z.write(PDF_COMPUTE, arcname=f"papers/02_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF_APPX, arcname=f"papers/03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
print(f"  [SUCCESS] {riemann_zip.name} ({riemann_zip.stat().st_size} bytes, SHA-256: {sha256_file(riemann_zip)})")

# 4. BSD BUNDLE
bsd_zip = ROOT / "BSD_E4_ELEVATOR_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"
print(f"\nBuilding {bsd_zip.name}...")
with zipfile.ZipFile(bsd_zip, "w", zipfile.ZIP_DEFLATED) as z:
    ws = ROOT / "birch and swinnerton dyer"
    for ext in ["*.lean", "*.json", "*.md", "*.py", "*.toml"]:
        for f in ws.glob(ext):
            if ".git" not in str(f) and ".lake" not in str(f):
                z.write(f, arcname=f"birch_and_swinnerton_dyer/{f.name}")
    if (ws / "formal").exists():
        for f in (ws / "formal").glob("*.lean"):
            z.write(f, arcname=f"birch_and_swinnerton_dyer/formal/{f.name}")
    if (ws / "reports").exists():
        for f in (ws / "reports").glob("*.*"):
            z.write(f, arcname=f"birch_and_swinnerton_dyer/reports/{f.name}")
    z.write(PDF_BSD, arcname=f"papers/01_CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.pdf")
    z.write(PDF_COMPUTE, arcname=f"papers/02_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf")
    z.write(PDF_APPX, arcname=f"papers/03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf")
print(f"  [SUCCESS] {bsd_zip.name} ({bsd_zip.stat().st_size} bytes, SHA-256: {sha256_file(bsd_zip)})")

# 5. CONTEMPORARY COMPUTE & TUBULANCE BUNDLE
compute_zip = ROOT / "CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip"
print(f"\nBuilding {compute_zip.name}...")
with zipfile.ZipFile(compute_zip, "w", zipfile.ZIP_DEFLATED) as z:
    ws = ROOT / "tubulance"
    for ext in ["*.lean", "*.json", "*.md", "*.py", "*.toml"]:
        for f in ws.glob(ext):
            if ".git" not in str(f) and ".lake" not in str(f):
                z.write(f, arcname=f"tubulance/{f.name}")
    if (ws / "formal").exists():
        for f in (ws / "formal").glob("*.lean"):
            z.write(f, arcname=f"tubulance/formal/{f.name}")
    for p in all_pdfs:
        z.write(p, arcname=f"papers/{p.name}")
print(f"  [SUCCESS] {compute_zip.name} ({compute_zip.stat().st_size} bytes, SHA-256: {sha256_file(compute_zip)})")

# 6. MASTER AUDIT PACK
audit_zip = ROOT / "ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip"
print(f"\nBuilding {audit_zip.name}...")
with zipfile.ZipFile(audit_zip, "w", zipfile.ZIP_DEFLATED) as z:
    for bundle in [hodge_zip, ym_zip, riemann_zip, bsd_zip, compute_zip]:
        z.write(bundle, arcname=f"bundles/{bundle.name}")
    for p in all_pdfs:
        z.write(p, arcname=f"master_papers/{p.name}")
print(f"  [SUCCESS] {audit_zip.name} ({audit_zip.stat().st_size} bytes, SHA-256: {sha256_file(audit_zip)})")

print("\nALL ZIP BUNDLES SUCCESSFULLY REBUILT!")
