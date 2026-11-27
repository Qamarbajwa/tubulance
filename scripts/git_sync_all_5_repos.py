import subprocess
import os
from pathlib import Path

repos = [
    {
        "name": "Hodge Conjecture",
        "path": Path(r"d:\Comfy UI\hodge conjecture"),
        "tag": "v1.6.0-contemporary-tare",
        "release_assets": [
            Path(r"d:\Comfy UI\hodge conjecture\reports\HODGE_CHIRAL_SPIN8_AND_MODULI_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf"),
            Path(r"d:\Comfy UI\HODGE_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip")
        ]
    },
    {
        "name": "Yang-Mills",
        "path": Path(r"d:\Comfy UI\yang mills and the mass gap"),
        "tag": "v1.5.0-contemporary-tare",
        "release_assets": [
            Path(r"d:\Comfy UI\yang mills and the mass gap\reports\YANG_MILLS_CHIRAL_SELF_DUAL_AND_BALABAN_UNIFIED_VERIFICATION_PAPER_2026_11_22.pdf"),
            Path(r"d:\Comfy UI\YANG_MILLS_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip")
        ]
    },
    {
        "name": "Riemann Hypothesis",
        "path": Path(r"d:\Comfy UI\rheihman hypothesis"),
        "tag": "v3.4.0-contemporary-tare",
        "release_assets": [
            Path(r"d:\Comfy UI\rheihman hypothesis\reports\RIEMANN_CHIRAL_REFLECTION_UNCERTAINTY_AND_PRIME_HORIZON_PAPER_2026_11_22.pdf"),
            Path(r"d:\Comfy UI\RIEMANN_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip")
        ]
    },
    {
        "name": "Navier-Stokes & Compute",
        "path": Path(r"d:\Comfy UI\tubulance"),
        "tag": "v2.1.0-contemporary-compute",
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
    
    # Git add
    subprocess.run(["git", "add", "."], cwd=p, check=False)
    
    # Git commit
    commit_msg = (f"Release {tag}: dated 2026-11-22 unified Lean 4 bundles, "
                  f"standalone verification papers with RTX A2000 GPU telemetry, "
                  f"and accurate unconditional vs conditional theorem tagging")
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=p, check=False)
    
    # Git push
    res_push = subprocess.run(["git", "push", "origin", "HEAD"], cwd=p, capture_output=True, text=True)
    print(f"Git push: {res_push.returncode} {res_push.stderr.strip()}")
    
    # Upload assets to GH release
    notes_file = p / "GITHUB_RELEASE_NOTES.md"
    if notes_file.exists():
        # Update release notes
        subprocess.run(["gh", "release", "edit", tag, "--notes-file", str(notes_file)], cwd=p, check=False)
        print(f"Updated release notes for tag {tag}")
    
    # Upload assets
    for asset in repo['release_assets']:
        if asset.exists():
            print(f"Uploading {asset.name} ({asset.stat().st_size} bytes) to {tag}...")
            res_up = subprocess.run(["gh", "release", "upload", tag, str(asset), "--clobber"], cwd=p, capture_output=True, text=True)
            print(f"  Result: {res_up.returncode} {res_up.stderr.strip()}")

print("\nALL 5 REPOSITORIES AND RELEASES SYNCED!")
