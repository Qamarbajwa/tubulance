"""
Indexer and Cross-Workspace Vault Mapper for Local OpenAI and Claude Mathematical Releases

Reads local benchmark archives under d:/Comfy UI/external_benchmarks/:
1. openai_math (721 manuscripts, 373 result families, Oct 2026 release)
2. openai_navier_stokes_euler (2,659 Lean 4 files + technical reports, Sept 2026 release)
3. alpoge_claude_rh_2026 (175,187 Lean 4 files, Nov 2026 release)

Categorizes every family and writes a complete JSON index + per-workspace
one-by-one Obsidian vault maps under D:/Comfy UI/idea memory/obsidian brains/big picture/.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Date: 2026-11-22
Methodology Note: ai is being used as a tool
Epistemic Boundary: status: verified-finite, open_horizon_lock: STRICTLY OPEN
"""

import json
import re
from pathlib import Path

EXT_ROOT = Path(r"d:\Comfy UI\external_benchmarks")
VAULT_ROOT = Path(r"D:\Comfy UI\idea memory\obsidian brains\big picture")


def extract_braced_group(text, start_idx):
    """Extract balanced {...} group starting at start_idx (pointing to '{')."""
    if start_idx >= len(text) or text[start_idx] != "{":
        return "", start_idx
    depth = 0
    i = start_idx
    buf = []
    while i < len(text):
        ch = text[i]
        if ch == "{":
            if depth > 0:
                buf.append(ch)
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return "".join(buf), i + 1
            buf.append(ch)
        else:
            buf.append(ch)
        i += 1
    return "".join(buf), i


def parse_openai_math_catalog():
    repo = EXT_ROOT / "openai_math"
    tex = (repo / "overview.tex").read_text(encoding="utf-8", errors="ignore")
    lean_docs_dir = repo / "lean" / "docs"
    lean_ids = {p.stem for p in lean_docs_dir.glob("*.md")} if lean_docs_dir.exists() else set()

    sec_matches = list(re.finditer(r"\\cataloguesection\{([^}]+)\}\{[^}]+\}", tex))
    families = []
    for idx, m in enumerate(sec_matches):
        sec_name = m.group(1)
        start_pos = m.end()
        end_pos = sec_matches[idx + 1].start() if idx + 1 < len(sec_matches) else len(tex)
        block = tex[start_pos:end_pos]
        pos = 0
        while True:
            hit = block.find(r"\resultentry", pos)
            if hit == -1:
                break
            cur = hit + len(r"\resultentry")
            while cur < len(block) and block[cur].isspace():
                cur += 1
            g_id, cur = extract_braced_group(block, cur)
            while cur < len(block) and block[cur].isspace():
                cur += 1
            g_title, cur = extract_braced_group(block, cur)
            while cur < len(block) and block[cur].isspace():
                cur += 1
            g_desc, cur = extract_braced_group(block, cur)
            while cur < len(block) and block[cur].isspace():
                cur += 1
            g_links, cur = extract_braced_group(block, cur)

            preprint_paths = re.findall(r"blob/main/(preprints/[^}]+?\.pdf)", g_links)
            clean_title = re.sub(r"\s+", " ", g_title).replace("--", "-").strip()
            clean_desc = re.sub(r"\s+", " ", g_desc).replace("--", "-").strip()

            families.append({
                "id": g_id.strip(),
                "subject": sec_name,
                "title": clean_title,
                "description": clean_desc,
                "has_lean_doc": g_id.strip() in lean_ids,
                "lean_doc_rel": f"lean/docs/{g_id.strip()}.md" if g_id.strip() in lean_ids else None,
                "preprint_pdfs": preprint_paths,
            })
            pos = cur
    return families


def assign_vault_workspace(fam):
    """Map an OpenAI math family into our 5 Clay/BSD workspaces or 00_Big_Picture."""
    text = f"{fam['subject']} {fam['title']} {fam['description']}".lower()
    if any(k in text for k in ["birch", "swinnerton-dyer", "selmer", "tate-shafarevich", "tate--shafarevich", "elliptic curve", "modular curve", "rational cube"]):
        return "05_Birch_Swinnerton_Dyer"
    if fam["subject"] == "Algebraic and complex geometry" or any(k in text for k in ["hodge", "milne", "abelian variet", "k3 surface", "shimura", "kuga-satake", "motive", "chow"]):
        return "01_Hodge_Conjecture"
    if fam["subject"] == "Number theory" or any(k in text for k in ["riemann", "zeta", "dirichlet", "hecke", "siegel zero", "prime", "multiplicative", "character sum", "goldbach"]):
        return "03_Riemann_Hypothesis"
    if fam["subject"] in ("Partial differential equations", "Real and complex analysis", "Differential geometry") or any(k in text for k in ["navier-stokes", "euler equation", "vlasov", "local smoothing", "kakeya", "wave equation", "curvature", "ricci"]):
        return "04_Navier_Stokes_3D"
    if fam["subject"] in ("Mathematical physics", "Probability and statistical mechanics") or any(k in text for k in ["gauge", "yang-mills", "ising", "heisenberg", "six-vertex", "spin glass", "quantum", "gibbs"]):
        return "02_Yang_Mills_4D"
    return "00_Big_Picture"


def sanitize_vault_text(s):
    """Keep clean Obsidian prose without robotic hash symbols or em/en-dashes."""
    return s.replace("#", "").replace("—", ": ").replace("–", "-")


def write_openai_math_vault_notes(families):
    groups = {
        "01_Hodge_Conjecture": [],
        "02_Yang_Mills_4D": [],
        "03_Riemann_Hypothesis": [],
        "04_Navier_Stokes_3D": [],
        "05_Birch_Swinnerton_Dyer": [],
        "00_Big_Picture": [],
    }
    for f in families:
        groups[assign_vault_workspace(f)].append(f)

    out_json = VAULT_ROOT / "00_Big_Picture" / "Probes" / "openai_math_373_catalog.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps({"total": len(families), "groups": groups}, indent=2), encoding="utf-8")

    # 1. Full one-by-one master table for ALL 373 families in 00_Big_Picture
    master_lines = [
        "status: external-archive-indexed",
        "open_horizon_lock: STRICTLY OPEN",
        "date: 2026-11-22",
        "author: Qamar Munawer",
        "institution: Brandenburg University of Technology Cottbus-Senftenberg",
        "disclosure: ai is being used as a tool",
        "local_path: d:\\Comfy UI\\external_benchmarks\\openai_math",
        "tags: [external-release, openai, math-catalog, 373-families, vault-map]",
        "",
        "External Release 04: Complete One-by-One Map of All 373 OpenAI Math Families (Oct 2026)",
        "",
        "Master Index: [[External_OpenAI_And_Claude_Releases_Master_Index]] | Big Picture: [[00_MOC_Big_Picture]]",
        "",
        "***",
        "",
        "1. Workspace Distribution Summary",
        "",
        f"Total local families parsed from overview.tex: {len(families)} (with {sum(1 for f in families if f['has_lean_doc'])} Lean comparator docs in lean/docs/).",
        "",
        "| Vault Workspace | Mapped Families | With Lean Docs | Target Vault Hub |",
        "| :--- | :---: | :---: | :--- |",
    ]
    hub_links = {
        "01_Hodge_Conjecture": "[[01_Hodge_Knowledge_Base]]",
        "02_Yang_Mills_4D": "[[02_Yang_Mills_Knowledge_Base]]",
        "03_Riemann_Hypothesis": "[[03_Riemann_Knowledge_Base]]",
        "04_Navier_Stokes_3D": "[[04_Navier_Stokes_Knowledge_Base]]",
        "05_Birch_Swinnerton_Dyer": "[[05_Birch_Swinnerton_Dyer_Knowledge_Base]]",
        "00_Big_Picture": "[[00_MOC_Big_Picture]]",
    }
    for ws, lst in groups.items():
        lean_c = sum(1 for f in lst if f["has_lean_doc"])
        master_lines.append(f"| {ws} | {len(lst)} | {lean_c} | {hub_links[ws]} |")

    master_lines.extend([
        "",
        "Important Epistemic & Withdrawal Note (from history.md):",
        "* Oct 7, 2026 Withdrawals: Algebraicity of Weil classes on split abelian eightfolds, Algebraicity of Kuga-Satake Correspondences for K3 Surfaces, and The rational Hodge conjecture for products of K3 surfaces were withdrawn due to a sign error in stabilization-trace cancellation.",
        "* All external claims remain externally audited (status: verified-finite for our internal bridges; open_horizon_lock: STRICTLY OPEN for all Clay Millennium Problems and BSD).",
        "",
        "***",
        "",
        "2. Complete One-by-One Registry (All 373 Families)",
        "",
        "| ID | Workspace | Subject | Lean Doc | Title & Local PDF Paths |",
        "| :---: | :--- | :--- | :---: | :--- |",
    ])
    for f in sorted(families, key=lambda x: int(x["id"])):
        ws = assign_vault_workspace(f)
        lean_tag = f"`{f['lean_doc_rel']}`" if f["has_lean_doc"] else "No"
        pdfs = "; ".join(f["preprint_pdfs"][:2]) if f["preprint_pdfs"] else "see CONTENTS.md"
        t_clean = sanitize_vault_text(f["title"]).replace("|", "/")
        master_lines.append(f"| {f['id']} | {ws} | {f['subject']} | {lean_tag} | {t_clean} ({pdfs}) |")

    master_path = VAULT_ROOT / "00_Big_Picture" / "External_Release_04_OpenAI_Math_373_Families_Map.md"
    master_path.write_text("\n".join(master_lines), encoding="utf-8")

    # 2. Per-workspace filtered one-by-one map notes for Hodge, Yang-Mills, Riemann, NS, BSD
    ws_note_paths = {}
    for ws in ["01_Hodge_Conjecture", "02_Yang_Mills_4D", "03_Riemann_Hypothesis", "04_Navier_Stokes_3D", "05_Birch_Swinnerton_Dyer"]:
        lst = groups[ws]
        lines = [
            "status: external-archive-mapped",
            "open_horizon_lock: STRICTLY OPEN",
            "date: 2026-11-22",
            "author: Qamar Munawer",
            "institution: Brandenburg University of Technology Cottbus-Senftenberg",
            "disclosure: ai is being used as a tool",
            "local_path: d:\\Comfy UI\\external_benchmarks\\openai_math",
            f"tags: [external-release, openai, math-catalog, {ws.lower()}]",
            "",
            f"OpenAI Math Archive (Oct 2026) One-by-One Map for {ws} ({len(lst)} Families)",
            "",
            f"Knowledge Base: {hub_links[ws]} | Full 373 Catalog: [[External_Release_04_OpenAI_Math_373_Families_Map]] | Master Index: [[External_OpenAI_And_Claude_Releases_Master_Index]]",
            "",
            "***",
            "",
            f"| ID | Subject | Lean Doc | Title & Summary | Local PDF |",
            "| :---: | :--- | :---: | :--- | :--- |",
        ]
        for f in lst:
            lean_tag = f"`{f['lean_doc_rel']}`" if f["has_lean_doc"] else "No"
            pdfs = ", ".join(f["preprint_pdfs"][:1]) if f["preprint_pdfs"] else "see overview"
            title_c = sanitize_vault_text(f["title"]).replace("|", "/")
            desc_c = sanitize_vault_text(f["description"]).replace("|", "/")
            lines.append(f"| {f['id']} | {f['subject']} | {lean_tag} | **{title_c}**: {desc_c} | `{pdfs}` |")

        note_path = VAULT_ROOT / ws / "Discussions" / f"External_Release_OpenAI_Math_Map_{ws}.md"
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text("\n".join(lines), encoding="utf-8")
        ws_note_paths[ws] = note_path

    return groups, master_path, ws_note_paths, out_json


if __name__ == "__main__":
    fams = parse_openai_math_catalog()
    groups, master_p, ws_notes, j_path = write_openai_math_vault_notes(fams)
    print("Parsed OpenAI Math families:", len(fams))
    for k, v in groups.items():
        print(f"  {k:26s}: {len(v):3d} families ({sum(1 for e in v if e['has_lean_doc']):3d} Lean docs)")
    print("Master catalog note:", master_p)
    print("Catalog JSON:", j_path)
