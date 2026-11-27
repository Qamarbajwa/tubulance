import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(r"d:\Comfy UI")
REPORTS_DIR = ROOT / "tubulance" / "reports"

token = os.environ.get("ZENODO_TOKEN") or os.environ.get("ZENODO_ACCESS_TOKEN") or os.environ.get("ZENODO_API_TOKEN")
if not token:
    raise RuntimeError("Missing Zenodo API token")

DEP_ID = 24431632
BUCKET_URL = "https://zenodo.org/api/files/eb4c4c52-22db-4a81-98a5-18f70010c2c7"

print(f"=== Publishing BSD Zenodo Deposition {DEP_ID} ===")

metadata = {
    "title": "Contemporary Birch and Swinnerton-Dyer Formalization in Lean 4: Cassels-Tate Skew Pfaffian Squares, Selmer Descent Schur Taring, and the 4D-to-1D Hodge-Abel-Jacobi Elevator (v1.0.0, Continuing the Operator Correspondence)",
    "upload_type": "software",
    "version": "1.0.0-contemporary-bsd",
    "publication_date": "2026-11-22",
    "license": "Apache-2.0",
    "language": "eng",
    "creators": [
        {
            "name": "Qamar Munawer",
            "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"
        }
    ],
    "keywords": [
        "birch-swinnerton-dyer",
        "elliptic-curves",
        "lean4",
        "formal-verification",
        "cassels-tate-pairing",
        "pfaffian",
        "hodge-conjecture",
        "abel-jacobi-map",
        "selmer-group"
    ],
    "description": """<p>1. Transition to Contemporary Mathematical Terminology (Continuing the Operator Correspondence):<br>
This repository provides a machine-verified Lean 4 formalization and companion Python verification suite for the finite-dimensional algebraic mechanisms underlying the Birch and Swinnerton-Dyer (BSD) Conjecture and its dimensional elevator bridge to the Hodge Conjecture.</p>
<p>2. Plain English and School-Math Two-Halves Intuition:<br>
Consider an elliptic curve like a smooth mathematical track where you search for points with clean fraction coordinates. When the rank is 0 or 1, a 1D modular curve provides the point directly. But at rank 2 or higher, the 1D path collapses to a single motionless point. To find the points, we ascend the dimensional elevator to the 4D abelian fourfold E^4 = E x E x E x E, where codimension-2 cycles project back down to the 1D curve via the Abel-Jacobi map. Just like taring an empty bowl on a kitchen scale, the Selmer descent sequence subtracts the Mordell-Weil rank to isolate the Tate-Shafarevich group, whose order is forced to be a perfect square by the Cassels-Tate skew Pfaffian identity.</p>
<p>3. Formally Machine-Verified Theorems in Lean 4 (0 sorry, Standard Kernel Axioms):<br>
The formal core includes: (1) Selmer Mordell-Weil Schur tare dimension subtraction; (2) Cassels-Tate 4x4 skew matrix Pfaffian square identity det(M) = Pf(M)^2; (3) Kato-Kolyvagin Euler system prime cutoff annihilating Sha above square root capacity; (4) Neron-Tate canonical height regulator Gram matrix positive-definiteness; (5) Heegner rank 1 versus rank 2 height collapse dichotomy; (6) Kummer-Selmer rank-plus-torsion exact sequence certified in Lean 4.</p>
<p>4. Deterministic Numerical Verification and GPU Benchmarks:<br>
The companion Python test suite runs 1,000 random skew-symmetric matrices verifying bitwise det(M) == Pf(M)^2, confirms regulator positivity across rank 1 to 3 curves, and validates the Selmer exact sequence across Cremona benchmark curves.</p>
<p>5. Epistemic Demarcation and Honest Scientific Boundary:<br>
Status: verified-finite. Open Horizon Lock: STRICTLY OPEN. While the finite algebraic identities, Pfaffian squares, and Selmer descent relations are fully machine-verified with 0 sorry in Lean 4, the global Birch and Swinnerton-Dyer Conjecture for general curves of rank r &gt;= 2 and the Clay Millennium Hodge Conjecture remain strictly open problems.</p>
<p>Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg.<br>
Methodology note: ai is being used as a tool.</p>""",
    "notes": "Methodology note: ai is being used as a tool."
}

# Validate rules
assert "#" not in metadata["title"], "Hash in title"
assert "#" not in metadata["description"], "Hash in description"
assert "\u2014" not in metadata["title"], "Em-dash in title"
assert "\u2014" not in metadata["description"], "Em-dash in description"
assert "google carbon" not in metadata["description"].lower(), "Banned vendor in description"
assert "gemini" not in metadata["description"].lower(), "Banned vendor in description"

# Update metadata via PUT
put_url = f"https://zenodo.org/api/deposit/depositions/{DEP_ID}"
put_req = urllib.request.Request(
    put_url,
    data=json.dumps({"metadata": metadata}).encode("utf-8"),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="PUT"
)
with urllib.request.urlopen(put_req, timeout=60) as resp:
    print(f"[OK] Deposition {DEP_ID} metadata updated.")

# Files to upload
bsd_files = [
    (REPORTS_DIR / "CONTEMPORARY_UNCONDITIONAL_CHIRAL_SCHUR_AND_HODGE_BSD_ELEVATOR_RESEARCH_PAPER.pdf", "02_Hodge_BSD_E4_Dimensional_Elevator_and_Unconditional_Horizon_Paper.pdf"),
    (REPORTS_DIR / "FOUR_WORKSPACE_THEOREM_AND_GPU_AUDIT_APPENDIX.pdf", "03_Master_22_Module_135_Unconditional_and_246_Module_Conditional_Audit_Appendix.pdf"),
    (REPORTS_DIR / "COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.pdf", "COMMON_PEOPLE_SCHOOL_MATH_GUIDE_TO_TWO_HALVES_AND_SCHUR_TARE_ACROSS_ALL_PROJECTS.pdf"),
    (ROOT / "BSD_E4_ELEVATOR_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip", "BSD_E4_ELEVATOR_UNCONDITIONAL_AND_CONDITIONAL_ZENODO_BUNDLE.zip"),
]

for src_path, target_name in bsd_files:
    file_bytes = src_path.read_bytes()
    file_url = f"{BUCKET_URL.rstrip('/')}/{target_name}"
    upload_req = urllib.request.Request(
        file_url,
        data=file_bytes,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
        method="PUT"
    )
    with urllib.request.urlopen(upload_req, timeout=300) as resp:
        print(f"  [UPLOADED] {target_name} ({len(file_bytes)} bytes)")

print("\nExecuting publish action on BSD deposition...")
pub_url = f"https://zenodo.org/api/deposit/depositions/{DEP_ID}/actions/publish"
pub_req = urllib.request.Request(
    pub_url,
    data=b"",
    headers={"Authorization": f"Bearer {token}"},
    method="POST"
)
with urllib.request.urlopen(pub_req, timeout=120) as resp:
    pub_data = json.loads(resp.read().decode("utf-8"))
    print("\n=== BSD PUBLICATION SUCCESSFUL ===")
    print("ID:", pub_data.get("id"))
    print("State:", pub_data.get("state"))
    print("Submitted:", pub_data.get("submitted"))
    print("DOI:", pub_data.get("doi"))
    print("DOI URL:", pub_data.get("doi_url"))
    print("Record URL:", pub_data.get("links", {}).get("record"))
