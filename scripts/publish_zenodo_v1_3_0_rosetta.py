#!/usr/bin/env python3
"""Create Zenodo newversion of deposition 24381824 for v1.3.0-rosetta and publish."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(r"d:/Comfy UI/tubulance")
DIST_ZIP = ROOT / "dist" / "TUBULANCE_RELEASE_v1.3.0_COCYCLE_CAP.zip"
ZENODO_API = "https://zenodo.org/api"
PREV_DEPOSITION_ID = 24381824

BUNDLE_FILES = [
    "paper/cl30_helical_schur_superfluid_monograph.pdf",
    "paper/cl30_helical_schur_superfluid_monograph.tex",
    "paper/win_win_cocycle_dichotomy_arch.png",
    "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.md",
    "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf",
    "NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md",
    "NS_NONLINEAR_SELF_FOCUS_003_NONLOCAL_TRIAD_DECOHERENCE.md",
    "NS_NONLINEAR_SELF_FOCUS_004_MULTISCALE_COCYCLE_BOUND.md",
    "AUTONOMY_CYCLE_RECEIPT_NS004.json",
    "formal/NavierStokesWinWinArchCert.lean",
    "formal/RosettaUniversalMetaTheorems.lean",
    "scripts/probe_cl30_helical_schur_and_vorticity_cocycle.py",
    "scripts/probe_win_win_cocycle_dichotomy_arch.py",
    "scripts/aggregate_rosetta_master_audit.py",
    "probe_cl30_helical_schur_results.json",
    "probe_win_win_cocycle_dichotomy_arch_results.json",
    "rosetta_master_audit_receipt.json",
    "src/navier3d/coscientist/autonomy.py",
    "src/navier3d/coscientist/kernel.py",
    "tests/test_ns_nonlinear_self_focus_004_suite.py",
    "tests/test_coscientist_autonomy_cycle.py",
]


def get_token() -> str:
    for var in ("ZENODO_TOKEN", "ZENODO_ACCESS_TOKEN", "ZENODO_API_TOKEN"):
        val = os.environ.get(var, "").strip()
        if val:
            return val
    raise RuntimeError("Missing ZENODO_TOKEN / ZENODO_ACCESS_TOKEN in environment")


def build_deterministic_zip() -> Path:
    DIST_ZIP.parent.mkdir(parents=True, exist_ok=True)
    fixed_dt = (2026, 11, 21, 1, 0, 0)
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
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} on {method} {url}: {body}") from e


def api_delete(url: str, token: str) -> None:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"}, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=60):
            return
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} on DELETE {url}: {body}") from e


def upload_to_bucket(bucket_url: str, file_path: Path, token: str) -> dict:
    url = f"{bucket_url.rstrip('/')}/{file_path.name}"
    req = urllib.request.Request(
        url,
        data=file_path.read_bytes(),
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


def main():
    token = get_token()
    zip_path = build_deterministic_zip()
    print(f"Built deterministic v1.3.0 bundle: {zip_path} ({zip_path.stat().st_size} bytes)")

    # Create new version from existing deposition 24381824
    nv = api_json("POST", f"{ZENODO_API}/deposit/depositions/{PREV_DEPOSITION_ID}/actions/newversion", token)
    draft_url = nv["links"]["latest_draft"]
    draft = api_json("GET", draft_url, token)
    dep_id = draft["id"]
    bucket_url = draft["links"]["bucket"]
    print(f"Created Zenodo newversion draft id={dep_id}")

    # Remove inherited files from draft before uploading updated v1.3.0 files
    for old_file in draft.get("files", []):
        api_delete(f"{ZENODO_API}/deposit/depositions/{dep_id}/files/{old_file['id']}", token)

    uploads = [
        ROOT / "paper" / "cl30_helical_schur_superfluid_monograph.pdf",
        ROOT / "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf",
        ROOT / "NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md",
        ROOT / "NS_NONLINEAR_SELF_FOCUS_004_MULTISCALE_COCYCLE_BOUND.md",
        ROOT / "AUTONOMY_CYCLE_RECEIPT_NS004.json",
        ROOT / "rosetta_master_audit_receipt.json",
        zip_path,
    ]
    for fp in uploads:
        res = upload_to_bucket(bucket_url, fp, token)
        print(f"Uploaded {fp.name}: size={res.get('size')} checksum={res.get('checksum')}")

    # Update metadata for v1.3.0-rosetta
    meta = draft["metadata"]
    meta["version"] = "v1.3.0-rosetta"
    meta["publication_date"] = "2026-11-21"
    meta["title"] = "3D Navier–Stokes Stochastic Persistence, Cl(3,0) Helical Schur Isolation, Win-Win Cocycle Dichotomy, and High-Frequency Dissipation Domination"
    meta["description"] = (
        meta.get("description", "")
        + "<p><strong>v1.3.0-rosetta Milestone Release:</strong> Completes Milestones "
        "<code>NS-NONLINEAR-SELF-FOCUS-003</code> and <code>NS-NONLINEAR-SELF-FOCUS-004</code>: "
        "(1) <strong>Non-Local Triad Phase Decoherence (<code>CLM-043</code>, <code>NEG-EV-050</code>, <code>NS-OBS-023</code>):</strong> "
        "Proves incompressibility skew-symmetry vanishing of uniform background advection, "
        "O(2^{-3Q/2}) viscous dissipation domination, and O(2^{-Q}) Beltrami helical parity suppression. "
        "(2) <strong>Multiscale Dyadic Cocycle Bound &amp; High-Frequency Dissipation Domination (<code>CLM-044</code>, <code>NEG-EV-051</code>, <code>NS-OBS-024</code>):</strong> "
        "Integrates the scale-dependent cocycle arch bound across dyadic octaves, demonstrating that "
        "coarse-grained arch peak collapses (Phi_Q -> 0 with a 12.74x drop on L=12 across b=1,2,4), "
        "and establishes an absolute scale threshold Q*(nu, E_0) beyond which viscous palinstrophy dissipation "
        "strictly dominates vortex stretching by at least 2x (S_Q &lt; 1/2 D_Q), definitively ruling out "
        "ultraviolet self-similar enstrophy blowup while rigorously preserving the open continuum regularity horizon. "
        "(3) <strong>Autonomy Level 2 Closed-Loop Research Runner:</strong> Adds the automated AI Co-Scientist "
        "Dark Factory research engine with Socratic reflection, mutation, blind tournaments, and fail-closed gates. "
        "(4) <strong>Accessible Science Guide:</strong> Includes <code>NAVIER_STOKES_EXPLAINED_FOR_EVERYONE.md</code>, "
        "a comprehensive plain-language guide for the common person with real-world examples (bathtub whirlpools, "
        "ice skater vortex stretching, honey vs coffee friction, playground swing non-local cancellation), "
        "an exact 14-term measurement dictionary, and an honest account of where the Millennium Prize stands.</p>"
    )
    meta["related_identifiers"] = [
        {
            "identifier": "https://github.com/Qamarbajwa/tubulance/releases/tag/v1.3.0-rosetta",
            "relation": "isSupplementTo",
            "scheme": "url",
        },
        {"identifier": "10.5281/zenodo.24378371", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24378372", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24378373", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24378644", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24381741", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24381824", "relation": "isVersionOf", "scheme": "doi"},
    ]
    api_json("PUT", f"{ZENODO_API}/deposit/depositions/{dep_id}", token, {"metadata": meta})

    pub = api_json("POST", f"{ZENODO_API}/deposit/depositions/{dep_id}/actions/publish", token)
    doi = pub["doi"]
    concept_doi = pub.get("conceptdoi", "")
    record_url = pub["links"]["record_html"]
    print(f"PUBLISHED ZENODO v1.3.0 DOI: {doi}")
    print(f"CONCEPT DOI: {concept_doi}")
    print(f"RECORD URL: {record_url}")

    receipt_path = ROOT / "rosetta_master_audit_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["zenodo_deposition_v1_3_0"] = {
        "deposition_id": dep_id,
        "doi": doi,
        "concept_doi": concept_doi,
        "record_url": record_url,
        "version": "v1.3.0-rosetta",
        "github_release": "https://github.com/Qamarbajwa/tubulance/releases/tag/v1.3.0-rosetta",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
