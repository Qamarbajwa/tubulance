#!/usr/bin/env python3
"""Deterministic release packager and Zenodo REST API publisher for v1.0.0-rosetta."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(r"d:/Comfy UI/tubulance")
DIST_ZIP = ROOT / "dist" / "TUBULANCE_CL30_ROSETTA_RELEASE_v1.0.0.zip"
ZENODO_API = "https://zenodo.org/api"

BUNDLE_FILES = [
    "paper/cl30_helical_schur_superfluid_monograph.pdf",
    "paper/cl30_helical_schur_superfluid_monograph.tex",
    "scripts/probe_cl30_helical_schur_and_vorticity_cocycle.py",
    "scripts/aggregate_rosetta_master_audit.py",
    "probe_cl30_helical_schur_results.json",
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
    fixed_dt = (2026, 11, 19, 20, 0, 0)
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
    zen = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    description = (
        "<p><strong>Cl(3,0) Helical Schur-Complement Isolation, O(3)-Even Parity Blindness, and Multiscale "
        "Constantin-Fefferman SO(3) Vorticity Cocycle Depletion in 3D Navier-Stokes and Superfluid Vortex Tangles "
        "(Release v1.0.0-rosetta)</strong></p>"
        "<p>This release provides the machine-verified matrix operator probe "
        "<code>probe_cl30_helical_schur_and_vorticity_cocycle.py</code> (<code>CL30_HELICAL_SCHUR_COCYCLE_OK</code>) "
        "and the four-workspace master audit aggregator <code>aggregate_rosetta_master_audit.py</code> "
        "(<code>rosetta_master_audit_receipt.json</code>, <code>4/4 PASS</code>). The mathematical formulation "
        "originated from comparing an irrotational Bose-Einstein superfluid against 3D rotational Navier-Stokes "
        "turbulence through the lens of <em>Seeing Negatively</em>:</p>"
        "<ul>"
        "<li><strong>Superfluid Empty Cores &amp; Matrix Vortex Stretching:</strong> In an irrotational Bose-Einstein "
        "superfluid (&psi; = &radic;&rho; e<sup>i&theta;</sup>), the positive bulk (&rho; &gt; 0) carries a 1D Abelian "
        "U(1) phase-gradient velocity u<sub>s</sub> = (&hbar;/m)&nabla;&theta; with &Omega; &equiv; 0; all rotational "
        "curvature resides in the negative-space empty vortex cores (&rho; = 0) and non-Abelian SO(3) holonomy "
        "crossings (D&Omega;/Dt = [S, &Omega;] + &nu;&Delta;&Omega;).</li>"
        "<li><strong>Cl(3,0) &cong; M<sub>2</sub>(C) Beltrami Split &amp; O(3)-Even Parity Blindness:</strong> "
        "Across 2,660 helical modes on an L=12 periodic torus (curl eigenvalue error &le; 1.78e-16), the operator "
        "triple {Q<sub>E</sub> = P<sub>+</sub> + P<sub>&minus;</sub>, Q<sub>Z</sub>, T<sub>hel</sub> = P<sub>+</sub> &minus; P<sub>&minus;</sub>} "
        "has diagonal Gram matrix diag(2660.0, 621106.65, 2660.0) (normalized off-diag 1.18e-15), vanishing O(3)-even "
        "projection &Pi;<sub>O(3)-even</sub>(T<sub>hel</sub>) = 0.0, positive Schur complement S<sub>Schur</sub> = 2660.0 &gt; 0, "
        "squared-density parity blindness P<sub>+</sub> T<sub>hel</sub><sup>2</sup> P<sub>&minus;</sub> = 0.0, and "
        "exact observable half-operator reconstruction K<sub>half</sub> + K<sub>half</sub><sup>T</sup> = 4 T<sub>hel</sub> (err = 0.0).</li>"
        "<li><strong>Multiscale (b = 1 &rarr; 2 &rarr; 4) Constantin-Fefferman SO(3) Cocycle Depletion:</strong> "
        "&delta;<sub>NS</sub>(b) = 1 &minus; &langle;(&omega;&#770;<sub>x</sub> &middot; &omega;&#770;<sub>x+b</sub>)<sup>2</sup>&rangle; "
        "is identically 0.0 for a 1D/Abelian parallel vortex tube across b &isin; {1, 2, 4}, whereas in a 3D heterochiral "
        "Taylor-Green + Kida-Pelz vortex tangle it grows 0.4200 &rarr; 0.6411 &rarr; 0.6452, driving a nearly 20x "
        "monotone contraction of block vortex-stretching transfer &rho;<sub>stretch</sub><sup>BLK</sup>(b): "
        "0.2713 &rarr; 0.1441 &rarr; 0.0140.</li>"
        "<li><strong>Unified 4-Workspace Rosetta Master Audit (4/4 PASS):</strong> Cross-references Hodge Conjecture "
        "(184 zero-axiom declarations / 100 extension theorems), 4D Yang-Mills Mass Gap (release v1.1.0-rosetta, "
        "commit 77d52d8 / baseline 0f3f012, C<sub>dom</sub> = 13.47, c<sub>cocycle</sub> = 1.3407, 720/720 blocks), "
        "Riemann Hypothesis (live Zenodo DOIs 10.5281/zenodo.24378371&ndash;24378373, 1.63133e-55 residual, "
        "&delta;<sub>PC</sub>(6) = 0.157648), and 3D Navier-Stokes (CL30_HELICAL_SCHUR_COCYCLE_OK).</li>"
        "</ul>"
        "<p><strong>Scientific Honesty Notice:</strong> All four Clay Millennium problems (Hodge Conjecture, "
        "4D Yang-Mills Mass Gap, Riemann Hypothesis <code>NO_RH_PROOF = true</code>, and 3D Navier-Stokes Global "
        "Regularity <code>NS_GLOBAL_REGULARITY_OPEN = true</code>) remain strictly <strong>OPEN</strong>.</p>"
    )
    return {
        "metadata": {
            "title": zen["title"],
            "upload_type": "software",
            "description": description,
            "creators": [{"name": "Bajwa, Qamar"}],
            "access_right": "open",
            "license": "apache-2.0",
            "version": "v1.0.0-rosetta",
            "keywords": zen["keywords"],
            "related_identifiers": [
                {
                    "identifier": "https://github.com/Qamarbajwa/tubulance/releases/tag/v1.0.0-rosetta",
                    "relation": "isSupplementTo",
                    "scheme": "url",
                },
                {
                    "identifier": "10.5281/zenodo.24378371",
                    "relation": "references",
                    "scheme": "doi",
                },
                {
                    "identifier": "10.5281/zenodo.24378372",
                    "relation": "references",
                    "scheme": "doi",
                },
                {
                    "identifier": "10.5281/zenodo.24378373",
                    "relation": "references",
                    "scheme": "doi",
                },
            ],
        }
    }


def main():
    token = get_token()
    zip_path = build_deterministic_zip()
    print(f"Built deterministic bundle: {zip_path} ({zip_path.stat().st_size} bytes)")

    dep = api_json("POST", f"{ZENODO_API}/deposit/depositions", token, build_metadata())
    dep_id = dep["id"]
    bucket_url = dep["links"]["bucket"]
    print(f"Created Zenodo draft deposition id={dep_id}")

    uploads = [
        ROOT / "paper" / "cl30_helical_schur_superfluid_monograph.pdf",
        ROOT / "rosetta_master_audit_receipt.json",
        zip_path,
    ]
    for fp in uploads:
        res = upload_to_bucket(bucket_url, fp, token)
        print(f"Uploaded {fp.name}: size={res.get('size')} checksum={res.get('checksum')}")

    pub = api_json("POST", f"{ZENODO_API}/deposit/depositions/{dep_id}/actions/publish", token)
    doi = pub["doi"]
    record_url = pub["links"]["record_html"]
    print(f"PUBLISHED ZENODO DOI: {doi}")
    print(f"RECORD URL: {record_url}")

    receipt_path = ROOT / "rosetta_master_audit_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["zenodo_deposition"] = {
        "deposition_id": dep_id,
        "doi": doi,
        "record_url": record_url,
        "github_release": "https://github.com/Qamarbajwa/tubulance/releases/tag/v1.0.0-rosetta",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("Updated rosetta_master_audit_receipt.json with Zenodo DOI.")


if __name__ == "__main__":
    main()
