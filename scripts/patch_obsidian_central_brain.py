"""
patch_obsidian_central_brain.py
===============================
Updates sort_and_sync_obsidian_central_brain.py with current release tags,
commits, and the new Chiral VRAM/FLOP scaling metrics.
"""

from pathlib import Path

script_path = Path(r"D:\Comfy UI\idea memory\obsidian brains\big picture\scripts\sort_and_sync_obsidian_central_brain.py")
text = script_path.read_text(encoding="utf-8")

old_ns_block = '''        "04_Navier_Stokes_Knowledge_Base.md": {
            "workspace": "04_Navier_Stokes_3D",
            "status": "verified-finite",
            "open_horizon_lock": "STRICTLY OPEN (3D Navier-Stokes Continuum Smooth Global Regularity / NS_GLOBAL_REGULARITY_OPEN = TRUE)",
            "head_commit": "8f26785",
            "release_tag": "v1.2.0-rosetta",
            "zenodo_dois": [
                "10.5281/zenodo.24381824",
                "10.5281/zenodo.24381620",
                "10.5281/zenodo.24378625",
                "10.5281/zenodo.24378624"
            ],
            "lean_modules_verified": 18,
            "key_finite_metrics": "diag(2660.0, 621106.65, 2660.0); S_Schur = 2660.0; Win-Win arch 0.0138; 18 modules; 13 papers"
        }'''

new_ns_block = '''        "04_Navier_Stokes_Knowledge_Base.md": {
            "workspace": "04_Navier_Stokes_3D",
            "status": "verified-finite",
            "open_horizon_lock": "STRICTLY OPEN (3D Navier-Stokes Continuum Smooth Global Regularity / NS_GLOBAL_REGULARITY_OPEN = TRUE)",
            "head_commit": "056f646",
            "release_tag": "v2.1.0-contemporary-compute",
            "zenodo_dois": [
                "10.5281/zenodo.24430756",
                "10.5281/zenodo.24381824",
                "10.5281/zenodo.24381620",
                "10.5281/zenodo.24378625",
                "10.5281/zenodo.24378624"
            ],
            "lean_modules_verified": 22,
            "key_finite_metrics": "N=512..8192 scaling; 50% half / 75% chiral / 99.8% boundary VRAM; 2x/8x/256x speedup; +14.62 dB HBIM SNR"
        }'''

assert old_ns_block in text, "old_ns_block not found in script!"
text = text.replace(old_ns_block, new_ns_block)

# Also update commit tags for Hodge, Yang-Mills, Riemann if needed
old_hodge = '"head_commit": "6c7572a",\n            "release_tag": "v1.5.0-rosetta",'
new_hodge = '"head_commit": "8078400",\n            "release_tag": "v1.6.0-rosetta",'
if old_hodge in text:
    text = text.replace(old_hodge, new_hodge)

old_ym = '"head_commit": "b65b756",\n            "release_tag": "v1.4.0-rosetta",'
new_ym = '"head_commit": "b1b849b",\n            "release_tag": "v1.5.0-rosetta",'
if old_ym in text:
    text = text.replace(old_ym, new_ym)

old_rh = '"head_commit": "485eb93",\n            "release_tag": "v3.3.0-rosetta",'
new_rh = '"head_commit": "9ec66c5",\n            "release_tag": "v3.4.0-rosetta",'
if old_rh in text:
    text = text.replace(old_rh, new_rh)

script_path.write_text(text, encoding="utf-8")
print(f"Successfully patched: {script_path}")
