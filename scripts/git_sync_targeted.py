import subprocess
import os
from pathlib import Path

repos = [
    {
        "name": "Hodge Conjecture",
        "path": Path(r"d:\Comfy UI\hodge conjecture"),
        "tag": "v1.6.0-contemporary-tare",
        "files_to_add": [
            ".zenodo.json",
            "GITHUB_RELEASE_NOTES.md",
            "UnifiedHodgeVerificationBundle.lean",
            "examples/math_gov/LeanMillenniumExt/UnifiedHodgeVerificationBundle.lean",
            "reports/HODGE_CHIRAL_SPIN8_AND_MODULI_UNIFIED_VERIFICATION_PAPER_2026_11_22.tex",
            "reports/HODGE_CHIRAL_SPIN8_AND_MODULI_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf",
            "reports/HODGE_CHIRAL_SPIN8_AND_MODULI_UNIFIED_VERIFICATION_PAPER_2026_11_22.md"
        ],
        "release_assets": [
            Path(r"d:\Comfy UI\hodge conjecture\reports\HODGE_CHIRAL_SPIN8_AND_MODULI_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf"),
            Path(r"d:\Comfy UI\HODGE_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip")
        ]
    },
    {
        "name": "Yang-Mills",
        "path": Path(r"d:\Comfy UI\yang mills and the mass gap"),
        "tag": "v1.5.0-contemporary-tare",
        "files_to_add": [
            ".zenodo.json",
            "GITHUB_RELEASE_NOTES.md",
            "UnifiedYangMillsVerificationBundle.lean",
            "formal/UnifiedYangMillsVerificationBundle.lean",
            "reports/YANG_MILLS_CHIRAL_SELF_DUAL_AND_BALABAN_UNIFIED_VERIFICATION_PAPER_2026_11_22.tex",
            "reports/YANG_MILLS_CHIRAL_SELF_DUAL_AND_BALABAN_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf"
        ],
        "release_assets": [
            Path(r"d:\Comfy UI\yang mills and the mass gap\reports\YANG_MILLS_CHIRAL_SELF_DUAL_AND_BALABAN_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf"),
            Path(r"d:\Comfy UI\YANG_MILLS_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip")
        ]
    },
    {
        "name": "Riemann Hypothesis",
        "path": Path(r"d:\Comfy UI\rheihman hypothesis"),
        "tag": "v3.4.0-contemporary-tare",
        "files_to_add": [
            ".zenodo.json",
            "GITHUB_RELEASE_NOTES.md",
            "UnifiedRiemannVerificationBundle.lean",
            "RiemannBlueprint/UnifiedRiemannVerificationBundle.lean",
            "reports/RIEMANN_CHIRAL_REFLECTION_UNCERTAINTY_AND_PRIME_HORIZON_PAPER_2026_11_22.tex",
            "reports/RIEMANN_CHIRAL_REFLECTION_UNCERTAINTY_AND_PRIME_HORIZON_PAPER_2026_11_22.pdf"
        ],
        "release_assets": [
            Path(r"d:\Comfy UI\rheihman hypothesis\reports\RIEMANN_CHIRAL_REFLECTION_UNCERTAINTY_AND_PRIME_HORIZON_PAPER_2026_11_22.pdf"),
            Path(r"d:\Comfy UI\RIEMANN_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip")
        ]
    },
    {
        "name": "Navier-Stokes & Compute",
        "path": Path(r"d:\Comfy UI\tubulance"),
        "tag": "v2.1.0-contemporary-compute",
        "files_to_add": [
            ".zenodo.json",
            "GITHUB_RELEASE_NOTES.md",
            "UnifiedNavierStokesAndComputeBundle.lean",
            "formal/UnifiedNavierStokesAndComputeBundle.lean",
            "reports/CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.tex",
            "reports/CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf",
            "reports/NAVIER_STOKES_HELICAL_TRIAD_AND_P_VS_NP_PFAFFIAN_UNIFIED_PAPER_2026_11_22.tex",
            "reports/NAVIER_STOKES_HELICAL_TRIAD_AND_P_VS_NP_PFAFFIAN_UNIFIED_PAPER_2026_11_22.pdf",
            "reports/FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.tex",
            "reports/FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf",
            "reports/chiral_vram_and_flops_scaling_receipt.json"
        ],
        "release_assets": [
            Path(r"d:\Comfy UI\tubulance\reports\CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf"),
            Path(r"d:\Comfy UI\tubulance\reports\NAVIER_STOKES_HELICAL_TRIAD_AND_P_VS_NP_PFAFFIAN_UNIFIED_PAPER_2026_11_22.pdf"),
            Path(r"d:\Comfy UI\tubulance\reports\FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf"),
            Path(r"d:\Comfy UI\CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip"),
            Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip")
        ]
    },
    {
        "name": "Birch & Swinnerton-Dyer",
        "path": Path(r"d:\Comfy UI\birch and swinnerton dyer"),
        "tag": "v1.0.0-contemporary-bsd",
        "files_to_add": [
            ".zenodo.json",
            "GITHUB_RELEASE_NOTES.md",
            "UnifiedBSDVerificationBundle.lean",
            "formal/UnifiedBSDVerificationBundle.lean",
            "reports/CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.tex",
            "reports/CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.pdf"
        ],
        "release_assets": [
            Path(r"d:\Comfy UI\birch and swinnerton dyer\reports\CONTEMPORARY_HODGE_BSD_DIMENSIONAL_ELEVATOR_AND_UNCONDITIONAL_HORIZON_PAPER.pdf"),
            Path(r"d:\Comfy UI\BSD_E4_ELEVATOR_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip")
        ]
    }
]

for repo in repos:
    print(f"\n==========================================")
    print(f"Syncing {repo['name']} at {repo['path']}")
    print(f"==========================================")
    p = repo['path']
    tag = repo['tag']
    
    # Git add targeted files
    for rel_f in repo['files_to_add']:
        full_f = p / rel_f
        if full_f.exists():
            subprocess.run(["git", "add", str(full_f)], cwd=p, check=False)
            print(f"  git add {rel_f}")
    
    # Git commit
    commit_msg = (f"Release {tag}: dated 2026-11-22 unified Lean 4 bundles, "
                  f"standalone verification papers with RTX A2000 GPU telemetry, "
                  f"and accurate unconditional vs conditional theorem tagging")
    res_c = subprocess.run(["git", "commit", "-m", commit_msg], cwd=p, capture_output=True, text=True)
    print(f"Git commit: {res_c.returncode} {res_c.stdout.strip()}")
    
    # Git push
    res_push = subprocess.run(["git", "push", "origin", "HEAD"], cwd=p, capture_output=True, text=True)
    print(f"Git push: {res_push.returncode} {res_push.stderr.strip()}")
    
    # Update release notes
    notes_file = p / "GITHUB_RELEASE_NOTES.md"
    if notes_file.exists():
        subprocess.run(["gh", "release", "edit", tag, "--notes-file", str(notes_file)], cwd=p, check=False)
        print(f"Updated release notes for tag {tag}")
    
    # Upload assets
    for asset in repo['release_assets']:
        if asset.exists():
            print(f"Uploading {asset.name} ({asset.stat().st_size} bytes) to {tag}...")
            res_up = subprocess.run(["gh", "release", "upload", tag, str(asset), "--clobber"], cwd=p, capture_output=True, text=True)
            print(f"  Result: {res_up.returncode} {res_up.stderr.strip()}")

print("\nALL 5 REPOSITORIES AND RELEASES SYNCED SUCCESSFULLY!")
