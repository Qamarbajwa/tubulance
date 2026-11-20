#!/usr/bin/env python3
"""Create Zenodo newversion of deposition 24378625 for v1.2.0-rosetta and publish."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(r"d:/Comfy UI/tubulance")
DIST_ZIP = ROOT / "dist" / "TUBULANCE_CL30_ROSETTA_RELEASE_v1.2.0.zip"
ZENODO_API = "https://zenodo.org/api"
PREV_DEPOSITION_ID = 24378625

BUNDLE_FILES = [
    "paper/cl30_helical_schur_superfluid_monograph.pdf",
    "paper/cl30_helical_schur_superfluid_monograph.tex",
    "paper/win_win_cocycle_dichotomy_arch.png",
    "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.md",
    "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf",
    "formal/NavierStokesWinWinArchCert.lean",
    "formal/RosettaUniversalMetaTheorems.lean",
    "scripts/probe_cl30_helical_schur_and_vorticity_cocycle.py",
    "scripts/probe_win_win_cocycle_dichotomy_arch.py",
    "scripts/aggregate_rosetta_master_audit.py",
    "probe_cl30_helical_schur_results.json",
    "probe_win_win_cocycle_dichotomy_arch_results.json",
    "rosetta_master_audit_receipt.json",
    "CL30_ROSETTA_RELEASE_MANIFEST.json",
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
    fixed_dt = (2026, 11, 20, 15, 30, 0)
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
    print(f"Built deterministic v1.2.0 bundle: {zip_path} ({zip_path.stat().st_size} bytes)")

    # Create new version from existing deposition 24378625
    nv = api_json("POST", f"{ZENODO_API}/deposit/depositions/{PREV_DEPOSITION_ID}/actions/newversion", token)
    draft_url = nv["links"]["latest_draft"]
    draft = api_json("GET", draft_url, token)
    dep_id = draft["id"]
    bucket_url = draft["links"]["bucket"]
    print(f"Created Zenodo newversion draft id={dep_id}")

    # Remove inherited files from draft before uploading updated v1.2.0 files
    for old_file in draft.get("files", []):
        api_delete(f"{ZENODO_API}/deposit/depositions/{dep_id}/files/{old_file['id']}", token)

    uploads = [
        ROOT / "paper" / "cl30_helical_schur_superfluid_monograph.pdf",
        ROOT / "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf",
        ROOT / "rosetta_master_audit_receipt.json",
        zip_path,
    ]
    for fp in uploads:
        res = upload_to_bucket(bucket_url, fp, token)
        print(f"Uploaded {fp.name}: size={res.get('size')} checksum={res.get('checksum')}")

    # Update metadata for v1.2.0-rosetta
    meta = draft["metadata"]
    meta["version"] = "v1.2.0-rosetta"
    meta["publication_date"] = "2026-11-20"
    meta["description"] = (
        meta.get("description", "")
        + "<p><strong>v1.2.0-rosetta Additions:</strong> Adds the 3D Navier-Stokes Win-Win "
        "SO(3) Cocycle Dichotomy Arch probe (<code>probe_win_win_cocycle_dichotomy_arch.py</code>, "
        "<code>0.1758 -&gt; 0.1157 -&gt; 0.0138</code> across <code>b=1,2,4</code>), "
        "Lean 4 certificates <code>NavierStokesWinWinArchCert.lean</code> and "
        "<code>RosettaUniversalMetaTheorems.lean</code> (all 5 Rosetta Meta-Theorems, zero custom axioms), "
        "and the general-reader essay/atlas <code>SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf</code>.</p>"
    )
    meta["related_identifiers"] = [
        {
            "identifier": "https://github.com/Qamarbajwa/tubulance/releases/tag/v1.2.0-rosetta",
            "relation": "isSupplementTo",
            "scheme": "url",
        },
        {"identifier": "10.5281/zenodo.24378371", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24378372", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24378373", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24378644", "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.24381741", "relation": "references", "scheme": "doi"},
    ]
    api_json("PUT", f"{ZENODO_API}/deposit/depositions/{dep_id}", token, {"metadata": meta})

    pub = api_json("POST", f"{ZENODO_API}/deposit/depositions/{dep_id}/actions/publish", token)
    doi = pub["doi"]
    concept_doi = pub.get("conceptdoi", "")
    record_url = pub["links"]["record_html"]
    print(f"PUBLISHED ZENODO v1.2.0 DOI: {doi}")
    print(f"CONCEPT DOI: {concept_doi}")
    print(f"RECORD URL: {record_url}")

    receipt_path = ROOT / "rosetta_master_audit_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["zenodo_deposition"] = {
        "deposition_id": dep_id,
        "doi": doi,
        "concept_doi": concept_doi,
        "record_url": record_url,
        "version": "v1.2.0-rosetta",
        "github_release": "https://github.com/Qamarbajwa/tubulance/releases/tag/v1.2.0-rosetta",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
