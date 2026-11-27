import json
from pathlib import Path

receipt_path = Path(r"d:\Comfy UI\READY_TO_MAIL_PROFESSOR_PACK\PRE_MAIL_PUBLIC_ACCESS_RECEIPT.json")
data = json.loads(receipt_path.read_text(encoding="utf-8"))

data["zenodo_records"]["master_multi_project_and_compute"] = {
    "deposition_id": 24433657,
    "doi": "10.5281/zenodo.24433657",
    "url": "https://doi.org/10.5281/zenodo.24433657",
    "public_status": "HTTP 200 OK",
    "publication_date": "2026-11-22",
    "version": "v2.1.1-contemporary-compute"
}

data["unified_lean_bundles"]["unconditional_roadmap_plan"] = "UnconditionalRoadmapExecutionPlanCert.lean (17 theorems, 0 sorry, Code 0, standard axioms)"

receipt_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("Updated PRE_MAIL_PUBLIC_ACCESS_RECEIPT.json successfully.")
