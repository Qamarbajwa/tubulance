#!/usr/bin/env python3
"""Publish each standalone PDF paper in tubulance as its own dedicated Zenodo publication DOI."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(r"d:/Comfy UI/tubulance")
ZENODO_API = "https://zenodo.org/api"


def get_token() -> str:
    for var in ("ZENODO_TOKEN", "ZENODO_ACCESS_TOKEN", "ZENODO_API_TOKEN"):
        val = os.environ.get(var, "").strip()
        if val:
            return val
    raise RuntimeError("Missing ZENODO_TOKEN in environment")


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


def upload_to_bucket(bucket_url: str, file_path: Path, token: str) -> dict:
    url = f"{bucket_url.rstrip('/')}/{file_path.name}"
    req = urllib.request.Request(
        url,
        data=file_path.read_bytes(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))


def publish_paper(token: str, pdf_path: Path, tex_path: Path, title: str, description: str, keywords: list[str]) -> dict:
    payload = {
        "metadata": {
            "title": title,
            "upload_type": "publication",
            "publication_type": "preprint",
            "description": description,
            "creators": [{"name": "Munawer, Qamar", "affiliation": "Brandenburg University of Technology (BTU) Cottbus-Senftenberg"}],
            "access_right": "open",
            "license": "cc-by-4.0",
            "publication_date": "2026-11-20",
            "keywords": keywords,
            "related_identifiers": [
                {"identifier": "10.5281/zenodo.24399167", "relation": "isSupplementedBy", "scheme": "doi"},
                {"identifier": "10.5281/zenodo.24403353", "relation": "references", "scheme": "doi"},
            ],
        }
    }
    dep = api_json("POST", f"{ZENODO_API}/deposit/depositions", token, payload)
    dep_id = dep["id"]
    bucket_url = dep["links"]["bucket"]
    upload_to_bucket(bucket_url, pdf_path, token)
    upload_to_bucket(bucket_url, tex_path, token)
    pub = api_json("POST", f"{ZENODO_API}/deposit/depositions/{dep_id}/actions/publish", token)
    return {
        "deposition_id": dep_id,
        "doi": pub["doi"],
        "concept_doi": pub.get("conceptdoi", ""),
        "record_url": pub["links"]["record_html"],
        "pdf": pdf_path.name,
    }


def main():
    token = get_token()

    p1 = publish_paper(
        token=token,
        pdf_path=ROOT / "paper" / "cl30_helical_schur_superfluid_monograph.pdf",
        tex_path=ROOT / "paper" / "cl30_helical_schur_superfluid_monograph.tex",
        title="Superfluid Empty Cores, Cl(3,0) Helical Schur Isolation, and Multiscale SO(3) Vorticity Cocycle Depletion",
        description=(
            "<p>Standalone technical monograph deriving and verifying the Cl(3,0) ~= M_2(C) Beltrami helical "
            "Schur-complement decomposition (S_Schur = 2660.0), O(3)-even parity blindness (P_+ T_hel^2 P_- = 0.0), "
            "half-operator reconstruction (K_half + K_half^T = 4 T_hel), and multiscale (b=1->2->4) Constantin-Fefferman "
            "SO(3) vorticity cocycle depletion (0.2713 -> 0.0140) on L=12 T^3.</p>"
            "<p><strong>Scientific Honesty:</strong> Clay 3D Navier-Stokes Global Regularity (NS_GLOBAL_REGULARITY_OPEN = true) "
            "and all four Clay Millennium Problems remain strictly OPEN.</p>"
        ),
        keywords=["Navier-Stokes", "Clifford algebra Cl(3,0)", "Schur complement", "Constantin-Fefferman cocycle", "Superfluid vortex cores"],
    )
    print("PAPER 1 PUBLISHED:", p1)

    p2 = publish_paper(
        token=token,
        pdf_path=ROOT / "paper" / "seeing_negatively_article_and_system_map.pdf",
        tex_path=ROOT / "paper" / "seeing_negatively_article_and_system_map.tex",
        title="Seeing Negatively: Why the Deepest Laws of Reality Hide in What Is Missing (The Rosetta Measurement Atlas)",
        description=(
            "<p>Complete general-reader essay and Rosetta Measurement Atlas unifying Hodge Conjecture, 4D Yang-Mills, "
            "Riemann Hypothesis, and 3D Navier-Stokes via the 5 Universal Rosetta mechanisms: Orthogonal Diagonal Triple Gram, "
            "Schur-Complement Baseline Taring, Chiral Half-Domain Reconstruction, 1D Line vs 2D Plane Cocycle Twist, and "
            "Active-Core SVD Concentration.</p>"
            "<p><strong>Scientific Honesty:</strong> All four Clay Millennium Problems remain strictly OPEN.</p>"
        ),
        keywords=["Seeing Negatively", "Rosetta Measurement Atlas", "Schur complement", "Millennium Problems", "Lean 4"],
    )
    print("PAPER 2 PUBLISHED:", p2)

    receipt_path = ROOT / "rosetta_master_audit_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["individual_paper_zenodo_dois"] = {
        "cl30_helical_schur_superfluid_monograph": p1,
        "seeing_negatively_article_and_system_map": p2,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
