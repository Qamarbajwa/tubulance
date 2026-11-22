"""
release_tubulance_compute.py
============================
Commits, tags, pushes, and creates the live GitHub release v2.1.0-contemporary-compute
for 3D Navier-Stokes & tare_core with the compute paper PDF and Zenodo bundle.
"""

import json
import os
import subprocess
from pathlib import Path

cwd = Path(r"d:\Comfy UI\tubulance")
tag = "v2.1.0-contemporary-compute"
title = "Contemporary Chiral Half-Domain Matrix Packing, Block-Involution Splitting, and Guyan-Schur Static Condensation: 50 to 99.8 Percent GPU VRAM Reduction and 8x to 256x Compute Acceleration on an 8 GB NVIDIA RTX A2000 Workstation (v2.1.0, Continuing the Previous Rosetta Stone Operator Correspondence)"

# 1. git add
subprocess.run([
    "git", "add",
    "tare_core/",
    "reports/",
    "scripts/",
    ".zenodo.json",
    "ZENODO_COMPUTE_PAPER_METADATA.json",
    "GITHUB_RELEASE_NOTES.md",
], cwd=str(cwd), check=True)

# 2. git commit
subprocess.run([
    "git", "commit", "-m",
    "release(v2.1.0-contemporary-compute): publish standalone Chiral Half-Domain 50-99.8% VRAM & 8x-256x FLOP GPU Compute Paper, scaling benchmark receipt, and Zenodo bundle"
], cwd=str(cwd), check=True)

# 3. git tag
subprocess.run([
    "git", "tag", "-f", "-a", tag, "-F", "GITHUB_RELEASE_NOTES.md"
], cwd=str(cwd), check=True)

# 4. git push branch and tag
b = subprocess.run(["git", "branch", "--show-current"], cwd=str(cwd), capture_output=True, text=True).stdout.strip()
subprocess.run(["git", "push", "origin", b], cwd=str(cwd), check=True)
subprocess.run(["git", "push", "origin", tag, "--force"], cwd=str(cwd), check=True)

# 5. gh release create
assets = [
    r"d:\Comfy UI\tubulance\reports\CONTEMPORARY_CHIRAL_HALF_DOMAIN_VRAM_AND_SCHUR_COMPUTE_PAPER.pdf",
    r"d:\Comfy UI\CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip",
    r"d:\Comfy UI\tubulance\reports\FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf",
]

cmd = ["gh", "release", "create", tag, "-t", title, "-F", "GITHUB_RELEASE_NOTES.md"] + assets
r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
print("gh release create stdout:", r.stdout)
print("gh release create stderr:", r.stderr)
print("Returncode:", r.returncode)
assert r.returncode == 0
print(f"Successfully created GitHub release {tag}!")
