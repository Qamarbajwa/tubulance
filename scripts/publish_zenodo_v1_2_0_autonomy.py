#!/usr/bin/env python3
"""Deterministic release packager and Zenodo REST API publisher for v1.2.0-rosetta.

Publishes a new version linked to Concept DOI 10.5281/zenodo.24378624.
Includes:
- NS-NONLINEAR-SELF-FOCUS-003: Non-Local Triad Phase Decoherence and Helical Parity Suppression (CLM-043)
- Co-Scientist Dark Factory Autonomy Engine (Autonomy Level 2 - Closed Loop Execution)
- NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md (Expanded Plain-Language Guide for the Common Person)
- Comprehensive test suites and negative evidence registries
- Master Rosetta audit receipt
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(r"d:/Comfy UI/tubulance")
DIST_ZIP = ROOT / "dist" / "TUBULANCE_RELEASE_v1.2.0_AUTONOMY.zip"
ZENODO_API = "https://zenodo.org/api"
CONCEPT_RECID = "24378624"
DRAFT_DEP_ID = "24381824"  # Pre-spawned draft for concept 24378624

BUNDLE_FILES = [
    "NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md",
    "docs/NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md",
    "NS_NONLINEAR_SELF_FOCUS_003_NONLOCAL_TRIAD_DECOHERENCE.md",
    "COSCIENTIST_MATH_GOVERNANCE_INTEGRATION.md",
    "src/navier3d/coscientist/__init__.py",
    "src/navier3d/coscientist/contracts.py",
    "src/navier3d/coscientist/kernel.py",
    "src/navier3d/coscientist/autonomy.py",
    "tests/test_coscientist_autonomy_cycle.py",
    "tests/test_coscientist_math_governance.py",
    "tests/test_ns_nonlinear_self_focus_003_suite.py",
    "governance/GOVERNANCE.md",
    "governance/PROJECT_STATE.yaml",
    "mathematical_constitution/CLAIM_REGISTRY.yaml",
    "mathematical_constitution/UNDERSTANDING_REGISTER.yaml",
    "mathematical_constitution/NOVELTY_REGISTER.yaml",
    "research_memory/RESEARCH_PATHWAY_REGISTRY.yaml",
    "research_memory/RESEARCH_OBSTRUCTION_REGISTRY.yaml",
    "research_memory/NEGATIVE_EVIDENCE_LEDGER.yaml",
    "paper/seeing_negatively_article_and_system_map.pdf",
    "paper/seeing_negatively_article_and_system_map.tex",
    "paper/cl30_helical_schur_superfluid_monograph.pdf",
    "paper/cl30_helical_schur_superfluid_monograph.tex",
    "paper/win_win_cocycle_dichotomy_arch.png",
    "scripts/probe_cl30_helical_schur_and_vorticity_cocycle.py",
    "scripts/probe_win_win_cocycle_dichotomy_arch.py",
    "scripts/aggregate_rosetta_master_audit.py",
    "probe_cl30_helical_schur_results.json",
    "rosetta_master_audit_receipt.json",
    ".zenodo.json",
]


def get_token() -> str:
    for var in ("ZENODO_TOKEN", "ZENODO_ACCESS_TOKEN", "ZENODO_API_TOKEN"):
        val = os.environ.get(var, "").strip()
        if val:
            return val
    raise RuntimeError("Missing ZENODO_TOKEN / ZENODO_ACCESS_TOKEN in environment")


def build_deterministic_zip() -> Path:
    DIST_ZIP.parent.mkdir(parents=True, exist_ok=True)
    fixed_dt = (2026, 11, 19, 23, 45, 0)
    with zipfile.ZipFile(DIST_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in sorted(BUNDLE_FILES):
            src = ROOT / rel
            if not src.exists():
                raise FileNotFoundError(f"Missing bundle file: {src}")
            zi = zipfile.ZipInfo(rel, date_time=fixed_dt)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, src.read_bytes())
    return DIST_ZIP


def api_json(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} on {method} {url}: {body}") from e


def upload_to_bucket(bucket_url: str, file_path: Path, token: str) -> dict:
    url = f"{bucket_url.rstrip('/')}/{file_path.name}"
    data = file_path.read_bytes()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} uploading {file_path.name}: {body}") from e


def build_metadata() -> dict:
    description = (
        "<p><strong>Cl(3,0) Helical Schur Isolation, Co-Scientist Autonomy Level 2 Kernel, "
        "Non-Local Triad Decoherence (CLM-043), and Plain-Language 3D Navier-Stokes Guide (Release v1.2.0-rosetta)</strong></p>"
        "<p>This major release delivers milestone <code>NS-NONLINEAR-SELF-FOCUS-003</code> and the autonomous "
        "Co-Scientist Dark Factory Autonomy Level 2 closed-loop engine for 3D incompressible Navier-Stokes research on the periodic torus T<sup>3</sup>.</p>"
        "<h3>1. Milestone NS-NONLINEAR-SELF-FOCUS-003: Non-Local Triad Decoherence</h3>"
        "<ul>"
        "<li><strong>Incompressibility Skew-Symmetry Cancellation:</strong> Proved that uniform non-local advection &lang;(u<sub>&le;Q-3</sub>&middot;&nabla;)&omega;<sub>Q</sub>, &omega;<sub>Q</sub>&rang; vanishes identically by incompressibility &nabla;&middot;u = 0 (the playground swing cancellation analogy).</li>"
        "<li><strong>Calderon-Zygmund Commutator Bound:</strong> Commutator enstrophy transfer into shell Q is bounded by C<sub>CZ</sub> ||&nabla;u<sub>&le;Q-3</sub>||<sub>L<sup>&infin;</sup></sub> ||&omega;<sub>Q</sub>||<sub>L<sup>2</sup></sub><sup>2</sup> &le; C k<sub>0</sub><sup>3/2</sup> 2<sup>Q/2</sup> ||&omega;||<sub>L<sup>2</sup></sub> ||&omega;<sub>Q</sub>||<sub>L<sup>2</sup></sub><sup>2</sup>.</li>"
        "<li><strong>Viscous Dissipation Domination:</strong> The ratio of non-local transfer to viscous dissipation decays as O(2<sup>-3Q/2</sup>) &rarr; 0, demonstrating that distant large-scale eddies cannot bypass the local viscous barrier to drive high-frequency blowup.</li>"
        "<li><strong>Helical Beltrami Parity Suppression:</strong> Chiral triad coupling M(k, p, q) decays as O(2<sup>-Q</sup>) due to Beltrami eigenmode parity cancellation.</li>"
        "</ul>"
        "<h3>2. Co-Scientist Dark Factory: Autonomy Level 2 (Closed-Loop Research)</h3>"
        "<p>Implements <code>src/navier3d/coscientist/autonomy.py</code> and <code>tests/test_coscientist_autonomy_cycle.py</code> (Autonomy Level 2):</p>"
        "<ul>"
        "<li>Automated Socratic inversion and assumption mapping (Idea-to-Product OS Addendum v1.0 &sect;2).</li>"
        "<li>Autonomous multi-agent hypothesis generation, adversarial reflection against counterexample matrices (ABC Beltrami flows, parallel shear, 2D embedded flows).</li>"
        "<li>Evolutionary mutation and hardening on counterexample detection.</li>"
        "<li>Blinded pairwise Elo tournament matches without proof promotion authority (I-04).</li>"
        "<li>Independent verifier manifest verification with strict builder-verifier separation (I-06).</li>"
        "</ul>"
        "<h3>3. Expanded Plain-Language Guide for Everyone</h3>"
        "<p>Includes updated <code>NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md</code> with new everyday real-world examples (the playground swing non-local cancellation, three-musician triad chords), an exhaustive 14-item measurement dictionary, and clear descriptions of all project discoveries.</p>"
        "<h3>4. Strict Scientific Honesty Notice</h3>"
        "<p>All four Clay Millennium problems (3D Navier-Stokes Global Regularity Statement B, Hodge Conjecture, "
        "4D Yang-Mills Mass Gap, and Riemann Hypothesis) remain strictly <strong>UNRESOLVED</strong>. "
        "Project Release Status is strictly <strong>NO-GO</strong> with Deployment Authority <strong>NONE</strong>.</p>"
    )
    return {
        "metadata": {
            "title": "Cl(3,0) Helical Schur Isolation, Co-Scientist Autonomy Level 2 Kernel, Non-Local Triad Decoherence (CLM-043), and Plain-Language 3D Navier-Stokes Guide",
            "upload_type": "software",
            "description": description,
            "creators": [{"name": "Bajwa, Qamar"}],
            "access_right": "open",
            "license": "apache-2.0",
            "version": "v1.2.0-rosetta",
            "keywords": [
                "Navier-Stokes",
                "Millennium Prize",
                "Vortex stretching",
                "Non-local triads",
                "Turbulence",
                "Enstrophy cascade",
                "Constantin-Fefferman cocycle",
                "Clifford algebra Cl(3,0)",
                "Co-Scientist Dark Factory",
                "Autonomy Level 2",
                "Plain-Language Science Guide",
            ],
            "related_identifiers": [
                {
                    "identifier": "https://github.com/Qamarbajwa/tubulance/releases/tag/v1.2.0-rosetta",
                    "relation": "isSupplementTo",
                    "scheme": "url",
                },
                {
                    "identifier": "10.5281/zenodo.24378624",
                    "relation": "isVersionOf",
                    "scheme": "doi",
                },
                {
                    "identifier": "10.5281/zenodo.24381620",
                    "relation": "isNewVersionOf",
                    "scheme": "doi",
                },
                {
                    "identifier": "10.5281/zenodo.24378371",
                    "relation": "references",
                    "scheme": "doi",
                },
                {
                    "identifier": "10.5281/zenodo.24378644",
                    "relation": "references",
                    "scheme": "doi",
                },
                {
                    "identifier": "10.5281/zenodo.24380054",
                    "relation": "references",
                    "scheme": "doi",
                },
            ],
        }
    }


def main():
    token = get_token()
    zip_path = build_deterministic_zip()
    print(f"Built deterministic release zip: {zip_path} ({zip_path.stat().st_size} bytes)")

    # Check draft deposition status
    dep_url = f"{ZENODO_API}/deposit/depositions/{DRAFT_DEP_ID}"
    dep = api_json("GET", dep_url, token)
    dep_id = dep["id"]
    bucket_url = dep["links"]["bucket"]
    print(f"Found draft deposition id={dep_id}, state={dep.get('state')}")

    # Remove old zip if present in the draft
    for f in dep.get("files", []):
        if "TUBULANCE_RELEASE_v1.1.0" in f.get("filename", ""):
            del_url = f.get("links", {}).get("self")
            if del_url:
                try:
                    api_json("DELETE", del_url, token)
                    print(f"Removed outdated file from draft: {f.get('filename')}")
                except Exception as e:
                    print(f"Warning: could not delete {f.get('filename')}: {e}")

    # Upload release artifacts to bucket
    uploads = [
        ROOT / "NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md",
        ROOT / "NS_NONLINEAR_SELF_FOCUS_003_NONLOCAL_TRIAD_DECOHERENCE.md",
        ROOT / "paper" / "seeing_negatively_article_and_system_map.pdf",
        ROOT / "paper" / "cl30_helical_schur_superfluid_monograph.pdf",
        zip_path,
        ROOT / "rosetta_master_audit_receipt.json",
    ]
    for fp in uploads:
        if not fp.exists():
            raise FileNotFoundError(f"Missing upload file: {fp}")
        res = upload_to_bucket(bucket_url, fp, token)
        print(f"Uploaded {fp.name}: size={res.get('size')} checksum={res.get('checksum')}")

    # Update metadata
    meta = build_metadata()
    api_json("PUT", dep_url, token, payload=meta)
    print("Updated deposition metadata.")

    # Publish deposition
    pub_url = f"{ZENODO_API}/deposit/depositions/{dep_id}/actions/publish"
    pub = api_json("POST", pub_url, token)
    doi = pub["doi"]
    concept_doi = pub.get("conceptdoi", "10.5281/zenodo.24378624")
    record_url = pub["links"]["record_html"]
    print(f"=== PUBLISHED ZENODO RELEASE v1.2.0-rosetta ===")
    print(f"VERSION DOI: {doi}")
    print(f"CONCEPT DOI: {concept_doi}")
    print(f"RECORD URL: {record_url}")

    # Update rosetta_master_audit_receipt.json
    receipt_path = ROOT / "rosetta_master_audit_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["zenodo_dois"]["navier_stokes_tubulance"] = doi
    receipt["zenodo_dois"]["navier_stokes_tubulance_concept"] = concept_doi
    receipt["zenodo_dois"]["navier_stokes_tubulance_v1_1_0"] = "10.5281/zenodo.24381620"
    receipt["zenodo_dois"]["navier_stokes_tubulance_v1_2_0"] = doi

    if "workspaces" in receipt and "navier_stokes" in receipt["workspaces"]:
        ns = receipt["workspaces"]["navier_stokes"]
        ns["zenodo_version_doi"] = doi
        ns["zenodo_concept_doi"] = concept_doi
        ns["release_tag"] = "v1.2.0-rosetta"
        ns["plain_language_explainer_present"] = True
        ns["coscientist_kernel_present"] = True
        ns["coscientist_autonomy_level_2_present"] = True
        ns["clm043_nonlocal_triad_present"] = True

    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"Updated rosetta_master_audit_receipt.json with new version DOI {doi}.")


if __name__ == "__main__":
    main()
