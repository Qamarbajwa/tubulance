import hashlib
from pathlib import Path

ROOT = Path(r"d:\Comfy UI")
REPORTS_DIR = ROOT / "tubulance" / "reports"

files_to_hash = [
    (REPORTS_DIR / "CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf", "01_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf"),
    (REPORTS_DIR / "CONTEMPORARY_UNCONDITIONAL_CHIRAL_SCHUR_AND_HODGE_BSD_ELEVATOR_RESEARCH_PAPER.pdf", "02_Hodge_BSD_E4_Dimensional_Elevator_and_Unconditional_Horizon_Paper.pdf"),
    (REPORTS_DIR / "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf", "03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf"),
    (REPORTS_DIR / "COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.pdf", "COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.pdf"),
    (ROOT / "CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip", "CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip"),
    (ROOT / "HODGE_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip", "HODGE_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"),
    (ROOT / "YANG_MILLS_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip", "YANG_MILLS_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"),
    (ROOT / "RIEMANN_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip", "RIEMANN_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"),
    (ROOT / "BSD_E4_ELEVATOR_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip", "BSD_E4_ELEVATOR_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"),
    (ROOT / "ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip", "ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip"),
]

manifest_lines = []
for p, name in files_to_hash:
    assert p.exists(), f"File missing: {p}"
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    manifest_lines.append(f"{h}  {name}")
    print(f"  {h}  {name} ({p.stat().st_size} bytes)")

manifest_path = ROOT / "SHA256SUMS_ALL_PROJECTS.txt"
manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
print(f"\nWrote manifest to {manifest_path} ({len(manifest_lines)} entries)")
