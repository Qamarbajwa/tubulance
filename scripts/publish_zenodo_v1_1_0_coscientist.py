#!/usr/bin/env python3
"""Deterministic release packager and Zenodo REST API publisher for v1.1.0-rosetta.

Publishes a new version linked to Concept DOI 10.5281/zenodo.24378624.
Includes:
- NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md (Plain-Language Guide for the Common Person)
- Co-Scientist Dark Factory Kernel & Contracts
- Seeing Negatively Essay & System Map
- Cl(3,0) Helical Schur-Complement Superfluid Monograph
- Rosetta Master Audit Receipt
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
DIST_ZIP = ROOT / "dist" / "TUBULANCE_RELEASE_v1.1.0_COSCIENTIST.zip"
ZENODO_API = "https://zenodo.org/api"
CONCEPT_RECID = "24378624"
DRAFT_DEP_ID = "24381620"  # Pre-spawned draft for concept 24378624

BUNDLE_FILES = [
    "NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md",
    "docs/NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md",
    "COSCIENTIST_MATH_GOVERNANCE_INTEGRATION.md",
    "src/navier3d/coscientist/__init__.py",
    "src/navier3d/coscientist/contracts.py",
    "src/navier3d/coscientist/kernel.py",
    "tests/test_coscientist_math_governance.py",
    "governance/GOVERNANCE.md",
    "governance/PROJECT_STATE.yaml",
    "mathematical_constitution/UNDERSTANDING_REGISTER.yaml",
    "mathematical_constitution/NOVELTY_REGISTER.yaml",
    "research_memory/RESEARCH_PATHWAY_REGISTRY.yaml",
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
    fixed_dt = (2026, 11, 19, 23, 0, 0)
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
        "<p><strong>Cl(3,0) Helical Schur-Complement Isolation, Co-Scientist Dark Factory Kernel, "
        "and Plain-Language 3D Navier-Stokes Guide (Release v1.1.0-rosetta)</strong></p>"
        "<p>This release provides a major expansion to the 3D Navier-Stokes Tubulance project, "
        "adding the autonomous Co-Scientist Dark Factory architecture, Google Drive Governance OS bindings, "
        "and a complete, accessible plain-language guide for the common person explaining the millennium prize, "
        "real-world whirlpools, measurement metrics, and observed mathematical phenomena.</p>"
        "<h3>1. Plain-Language Guide for Everyone</h3>"
        "<p>Includes <code>NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md</code>, an intuitive guide using everyday real-world examples:</p>"
        "<ul>"
        "<li><strong>Draining Bathtub & Sink Whirlpools:</strong> Why water spins faster as it draws near the drain hole, and why the funnel doesn't reach infinite speed.</li>"
        "<li><strong>Figure Skater Effect (Vortex Stretching):</strong> How fluid conservation of angular momentum pulls vortex filaments skinnier, causing them to accelerate.</li>"
        "<li><strong>Stirring Honey vs. Coffee (Viscous Dissipation):</strong> The molecular friction tax that turns swirls into microscopic heat.</li>"
        "<li><strong>Smoke Rings & Dolphin Bubble Rings:</strong> Why vortex tori remain coherent across a room or pool.</li>"
        "<li><strong>Complete Measurement Dictionary:</strong> What each mathematical quantity is called, what it measures, and how it is computed (Velocity u, Vorticity &omega;, Rate-of-strain S, Vortex stretching (S&omega;)&middot;&omega;, Enstrophy E, Dissipation D, Foias-Temam scale l_&omega;, Dyadic octaves P_q, Advective flux &Pi;_Q<sup>adv</sup>, and the Viscous 2<sup>-4Q</sup> damping penalty).</li>"
        "</ul>"
        "<h3>2. Project Observations & Negative Evidence</h3>"
        "<ul>"
        "<li><strong>OpenAI Precursor Cost Barrier (CLM-040, NEG-EV-046):</strong> Proved that backward time-reconstruction of a prescribed blowup pulse hits a super-exponential exp(exp(t)) cost barrier; calm unforced water can never naturally create such an entrance state.</li>"
        "<li><strong>ABC Beltrami Non-Stretching Optical Illusion (CLM-041-R1, NEG-EV-047):</strong> Proved that aligned helical flows carry fierce vorticity but identically zero vortex stretching ((u&middot;&nabla;)u = &nabla;(&frac12;|u|<sup>2</sup>)), producing false alarms on unnormalized metrics.</li>"
        "<li><strong>Forward Dyadic Transfer & Triad Backscatter (CLM-042, NEG-EV-049, NS-OBS-022):</strong> Proved forward enstrophy flux in Taylor-Green vortex collisions, while showing that triad phase-reversals and the 2<sup>-4Q</sup> viscous tax rapidly deplete the cascade before runaway.</li>"
        "<li><strong>Constantin-Fefferman Cocycle Depletion & Cl(3,0) Schur Floor:</strong> Measured rapid vortex axis misalignment (&delta;<sub>NS</sub> &rarr; 0.645) choking stretching by 20x, with machine-verified positive Schur-complement floor S<sub>Schur</sub> = 2660.0.</li>"
        "</ul>"
        "<h3>3. Co-Scientist Dark Factory Kernel</h3>"
        "<p>Implements <code>src/navier3d/coscientist/kernel.py</code> and <code>contracts.py</code> under fail-closed scientific research gates SR0&ndash;SR8, enforcing invariants I-01 through I-12 and binding the Google Drive Governance OS master record.</p>"
        "<h3>4. Strict Scientific Honesty Notice</h3>"
        "<p>All four Clay Millennium problems (3D Navier-Stokes Global Regularity Statement B, Hodge Conjecture, "
        "4D Yang-Mills Mass Gap, and Riemann Hypothesis) remain strictly <strong>UNRESOLVED</strong>. "
        "Project Release Status is strictly <strong>NO-GO</strong> with Deployment Authority <strong>NONE</strong>.</p>"
    )
    return {
        "metadata": {
            "title": "Cl(3,0) Helical Schur-Complement Isolation, Co-Scientist Dark Factory Kernel, and Plain-Language 3D Navier-Stokes Guide",
            "upload_type": "software",
            "description": description,
            "creators": [{"name": "Bajwa, Qamar"}],
            "access_right": "open",
            "license": "apache-2.0",
            "version": "v1.1.0-rosetta",
            "keywords": [
                "Navier-Stokes",
                "Millennium Prize",
                "Vortex stretching",
                "Turbulence",
                "Enstrophy cascade",
                "Constantin-Fefferman cocycle",
                "Clifford algebra Cl(3,0)",
                "Co-Scientist Dark Factory",
                "Plain-Language Science Guide",
                "Superfluid vortex tangles",
            ],
            "related_identifiers": [
                {
                    "identifier": "https://github.com/Qamarbajwa/tubulance/releases/tag/v1.1.0-rosetta",
                    "relation": "isSupplementTo",
                    "scheme": "url",
                },
                {
                    "identifier": "10.5281/zenodo.24378624",
                    "relation": "isVersionOf",
                    "scheme": "doi",
                },
                {
                    "identifier": "10.5281/zenodo.24378625",
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

    # Remove old v1.0.0 zip if present in the draft
    for f in dep.get("files", []):
        if "v1.0.0" in f.get("filename", ""):
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
    print(f"=== PUBLISHED ZENODO RELEASE v1.1.0-rosetta ===")
    print(f"VERSION DOI: {doi}")
    print(f"CONCEPT DOI: {concept_doi}")
    print(f"RECORD URL: {record_url}")

    # Update rosetta_master_audit_receipt.json
    receipt_path = ROOT / "rosetta_master_audit_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["zenodo_dois"]["navier_stokes_tubulance"] = doi
    receipt["zenodo_dois"]["navier_stokes_tubulance_concept"] = concept_doi
    receipt["zenodo_dois"]["navier_stokes_tubulance_v1_0_0"] = "10.5281/zenodo.24378625"
    receipt["zenodo_dois"]["navier_stokes_tubulance_v1_1_0"] = doi

    if "workspaces" in receipt and "navier_stokes" in receipt["workspaces"]:
        ns = receipt["workspaces"]["navier_stokes"]
        ns["zenodo_version_doi"] = doi
        ns["zenodo_concept_doi"] = concept_doi
        ns["release_tag"] = "v1.1.0-rosetta"
        ns["plain_language_explainer_present"] = True
        ns["coscientist_kernel_present"] = True

    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"Updated rosetta_master_audit_receipt.json with new version DOI {doi}.")


if __name__ == "__main__":
    main()
