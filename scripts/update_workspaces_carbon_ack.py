"""
update_workspaces_carbon_ack.py
===============================
Updates Workspaces 01, 02, and 03 GITHUB_RELEASE_NOTES.md and .zenodo.json
with the Google Carbon (Gemini 4 Carbon) technical acknowledgment,
commits, pushes, and updates the live GitHub releases.
"""

import json
import os
import subprocess
from pathlib import Path

workspaces = [
    {
        "name": "Workspace 01: Hodge Conjecture",
        "dir": Path(r"d:\Comfy UI\hodge conjecture"),
        "tag": "v1.6.0-rosetta",
        "title": "Contemporary Chiral Spin(8) Half-Domain Cohomology Decomposition and Arakelov-Bost Slope Reduction for the Hodge Conjecture in Lean 4 (v1.6.0, Continuing the Previous Rosetta Stone Operator Correspondence)",
        "commit_msg": "chore(metadata): add Google Carbon technical acknowledgment to Hodge release notes",
    },
    {
        "name": "Workspace 02: 4D Yang-Mills",
        "dir": Path(r"d:\Comfy UI\yang mills and the mass gap"),
        "tag": "v1.5.0-rosetta",
        "title": "Contemporary Chiral Self-Dual Curvature Decomposition, Balaban Renormalization Contraction, and Osterwalder-Schrader Clustering for 4D Yang-Mills in Lean 4 (v1.5.0, Continuing the Previous Rosetta Stone Operator Correspondence)",
        "commit_msg": "chore(metadata): add Google Carbon technical acknowledgment to 4D Yang-Mills release notes",
    },
    {
        "name": "Workspace 03: Riemann Hypothesis",
        "dir": Path(r"d:\Comfy UI\rheihman hypothesis"),
        "tag": "v3.4.0-rosetta",
        "title": "Contemporary Chiral Half-Plane Reflection, Non-Commuting Prime-Archimedean Uncertainty, Baker Linear-Form Envelope, and 10^18 Prime Horizon in Lean 4 (v3.4.0, Continuing the Previous Rosetta Stone Operator Correspondence)",
        "commit_msg": "chore(metadata): add Google Carbon technical acknowledgment to Riemann release notes",
    },
]

ack_text = "Acknowledgments: Technical assistance from Google Carbon (Gemini 4 Carbon) for technical assistance in formal verification, operator derivations, and numerical software engineering."
intro_ack = " The author expresses deep and sincere gratitude to Google Carbon (Gemini 4 Carbon) for technical assistance in formal proof engineering, mathematical derivations, and numerical computing."

for ws in workspaces:
    base_dir = ws["dir"]
    notes_p = base_dir / "GITHUB_RELEASE_NOTES.md"
    zenodo_p = base_dir / ".zenodo.json"

    # 1. Update GITHUB_RELEASE_NOTES.md
    text = notes_p.read_text(encoding="utf-8")
    if "Google Carbon (Gemini 4 Carbon)" not in text:
        # Insert into introductory paragraph
        idx = text.find("numerical software engineering.")
        if idx != -1:
            idx_end = idx + len("numerical software engineering.")
            text = text[:idx_end] + intro_ack + text[idx_end:]
        elif "GPU computing." in text:
            idx = text.find("GPU computing.")
            idx_end = idx + len("GPU computing.")
            text = text[:idx_end] + intro_ack + text[idx_end:]
        elif "GPU testing." in text:
            idx = text.find("GPU testing.")
            idx_end = idx + len("GPU testing.")
            text = text[:idx_end] + intro_ack + text[idx_end:]

        # Also add at bottom
        if "Methodology note: ai is being used as a tool." in text:
            text = text.replace(
                "Methodology note: ai is being used as a tool.",
                "Methodology note: ai is being used as a tool.\n" + ack_text
            )

    # Validate rules
    assert "#" not in text
    assert "\u2014" not in text
    assert "\u2013" not in text
    notes_p.write_text(text, encoding="utf-8")
    print(f"[{ws['name']}] Updated notes: {notes_p}")

    # 2. Update .zenodo.json
    with open(zenodo_p, "r", encoding="utf-8") as f:
        z = json.load(f)
    z["description"] = text.replace("\n", "<br>")
    z["notes"] = "Methodology note: ai is being used as a tool. " + ack_text
    with open(zenodo_p, "w", encoding="utf-8") as f:
        json.dump(z, f, indent=2, ensure_ascii=False)
    print(f"[{ws['name']}] Updated zenodo: {zenodo_p}")

    # 3. Git commit and push
    subprocess.run(["git", "add", ".zenodo.json", "GITHUB_RELEASE_NOTES.md"], cwd=str(base_dir), check=True)
    subprocess.run(["git", "commit", "-m", ws["commit_msg"]], cwd=str(base_dir), check=True)
    b = subprocess.run(["git", "branch", "--show-current"], cwd=str(base_dir), capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "push", "origin", b], cwd=str(base_dir), check=True)

    # 4. Edit GitHub release
    r = subprocess.run(
        ["gh", "release", "edit", ws["tag"], "--title", ws["title"], "--notes-file", "GITHUB_RELEASE_NOTES.md"],
        cwd=str(base_dir),
        capture_output=True,
        text=True,
    )
    print(f"[{ws['name']}] gh release edit: code {r.returncode}")
    assert r.returncode == 0

print("Workspaces 01, 02, and 03 updated and pushed successfully!")
