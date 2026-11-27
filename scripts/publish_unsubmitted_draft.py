import os
import requests
import json
from pathlib import Path

token = os.environ.get("ZENODO_TOKEN")
if not token:
    raise RuntimeError("ZENODO_TOKEN is not set.")

headers = {"Authorization": f"Bearer {token}"}
dep_id = 24430756

# 1. Fetch current deposition
r = requests.get(f"https://zenodo.org/api/deposit/depositions/{dep_id}", headers=headers)
r.raise_for_status()
dep = r.json()
bucket_url = dep["links"]["bucket"]

print(f"Deposition {dep_id} bucket: {bucket_url}")

# 2. Delete old files
for f in dep.get("files", []):
    fid = f["id"]
    fname = f["filename"]
    print(f"Deleting old file {fname} ({fid})...")
    del_r = requests.delete(f"https://zenodo.org/api/deposit/depositions/{dep_id}/files/{fid}", headers=headers)
    print(f"Delete status: {del_r.status_code}")

# 3. Upload fresh files
files_to_upload = [
    Path(r"d:\Comfy UI\CONTEMPORARY_CHIRAL_VRAM_AND_SCHUR_COMPUTE_ZENODO_BUNDLE.zip"),
    Path(r"d:\Comfy UI\READY_TO_MAIL_PROFESSOR_PACK\00_Contemporary_Cross_Project_Matrix_Atlas_Paper.pdf"),
    Path(r"d:\Comfy UI\READY_TO_MAIL_PROFESSOR_PACK\01_GPU_Compute_50_to_99_Percent_VRAM_and_Schur_Condensation_Paper.pdf"),
    Path(r"d:\Comfy UI\READY_TO_MAIL_PROFESSOR_PACK\02_Hodge_BSD_E4_Dimensional_Elevator_and_Unconditional_Horizon_Paper.pdf"),
    Path(r"d:\Comfy UI\READY_TO_MAIL_PROFESSOR_PACK\03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf"),
    Path(r"d:\Comfy UI\READY_TO_MAIL_PROFESSOR_PACK\08_Common_People_School_Math_Guide_To_Two_Halves_And_Schur_Tare.pdf"),
    Path(r"d:\Comfy UI\rheihman hypothesis\MasterContinuumBridgePremiseACert.lean"),
    Path(r"d:\Comfy UI\rheihman hypothesis\UnconditionalRoadmapExecutionPlanCert.lean")
]

for p in files_to_upload:
    if not p.exists():
        print(f"WARNING: File {p} does not exist!")
        continue
    fname = p.name
    print(f"Uploading {fname} ({p.stat().st_size} bytes)...")
    with open(p, "rb") as fp:
        up_r = requests.put(f"{bucket_url}/{fname}", data=fp, headers=headers)
        up_r.raise_for_status()
    print(f"  Uploaded {fname} successfully.")

# 4. Sanitize metadata
meta = dep.get("metadata", {})
desc = meta.get("description", "")
notes = meta.get("notes", "")

# Remove vendor names
desc = desc.replace("The author expresses deep and sincere gratitude to Google Carbon (Gemini 4 Carbon) for technical assistance in CUDA memory architecture, Lean 4 formal verification, and structural HBIM development.", "")
desc = desc.replace("Acknowledgments: Technical assistance from Google Carbon (Gemini 4 Carbon).", "")
notes = notes.replace("Technical assistance from Google Carbon (Gemini 4 Carbon).", "")
notes = notes.replace("Google Carbon (Gemini 4 Carbon)", "")

# Ensure clean methodology note
if "ai is being used as a tool" not in desc:
    desc += "<br><br>Methodology note: ai is being used as a tool."
if "ai is being used as a tool" not in notes:
    notes += " Methodology note: ai is being used as a tool."

# Remove em-dash and en-dash
desc = desc.replace("—", "-").replace("–", "-")
notes = notes.replace("—", "-").replace("–", "-")
title = meta["title"].replace("—", "-").replace("–", "-")

# Ensure zero #
desc = desc.replace("#", "")
notes = notes.replace("#", "")
title = title.replace("#", "")

meta["description"] = desc
meta["notes"] = notes
meta["title"] = title
meta["publication_date"] = "2026-11-22"
meta["creators"] = [{"name": "Qamar Munawer", "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"}]

# Update metadata
print("Updating sanitized metadata...")
put_r = requests.put(f"https://zenodo.org/api/deposit/depositions/{dep_id}", json={"metadata": meta}, headers=headers)
put_r.raise_for_status()
print("Metadata updated successfully.")

# 5. Publish deposition
print(f"Publishing deposition {dep_id}...")
pub_r = requests.post(f"https://zenodo.org/api/deposit/depositions/{dep_id}/actions/publish", headers=headers)
pub_r.raise_for_status()
pub_data = pub_r.json()
print("Publish successful!")
print("Published DOI:", pub_data.get("doi"))
print("State:", pub_data.get("state"))
print("Submitted:", pub_data.get("submitted"))
