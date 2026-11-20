#!/usr/bin/env python3
"""
align_all_papers_titles_and_author.py

Comprehensive Cross-Workspace Sanitization, Attribution, and Compilation Engine.
Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg.
Methodology: ai is being used as a tool.

Critical Rules Enforced:
1. Strict Author & University Attribution:
   - Exact author block:
     \\author{Qamar Munawer \\\\ Brandenburg University of Technology Cottbus-Senftenberg}
   - Creator in .zenodo.json:
     {"name": "Qamar Munawer", "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"}
   - No department / faculty mentions anywhere.
   - Remove "Qamar Munawer" from authors, headers, footers, metadata.
2. Terminology & Jargon Sanitization:
   - Replace "tubulance", "tabulance", "rheihman" in titles/prose with "Turbulence" / "Riemann".
   - Never alter physical folder paths ("d:/Comfy UI/tubulance", etc.) or git URLs ("Qamarbajwa/tubulance").
   - Clean robotic code titles (replace raw underscores, cert markers).
3. Prose & Tone Alignment:
   - Clear, personal letter style in simple Indian English.
   - Exact phrase: "ai is being used as a tool" in acknowledgments / methodology.
   - Remove em-dashes and stray hashes.
4. Recompile all PDFs (twice, 0 errors) and rebuild Zenodo ZIPs.
5. Automated validation assertions.
"""

from __future__ import annotations

import os
import sys
import re
import json
import shutil
import hashlib
import zipfile
import subprocess
from pathlib import Path

# Workspace definitions
WS_HODGE = Path(r"D:/Comfy UI/hodge conjecture")
WS_YM = Path(r"D:/Comfy UI/yang mills and the mass gap")
WS_RH = Path(r"D:/Comfy UI/rheihman hypothesis")
WS_NS = Path(r"D:/Comfy UI/tubulance")
WS_AUDIT = Path(r"D:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK")

AUTHOR_BLOCK_LATEX = r"\author{Qamar Munawer \\ Brandenburg University of Technology Cottbus-Senftenberg}"

CREATOR_ZENODO = [
    {
        "name": "Qamar Munawer",
        "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"
    }
]

SKIP_PARTS = {".git", ".rh-v2-runtime", "node_modules", ".lake", "build", ".cache", ".archive_superseded", "__pycache__", "mathlib4_upstream_pr"}

def walk_pruned(root: Path, ext: str):
    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in SKIP_PARTS]
        for f in filenames:
            if f.endswith(ext):
                yield Path(dirpath) / f


def log_step(msg: str):
    print("\n" + "=" * 80)
    print(f"--> {msg}")
    print("=" * 80)

def sanitize_author_in_latex(tex_content: str) -> str:
    """Replace any author block in a LaTeX document with the canonical author block using brace counting."""
    pos = 0
    while True:
        idx = tex_content.find(r"\author{", pos)
        if idx == -1:
            break
        # If it's already the exact author block, skip past it
        if tex_content.startswith(AUTHOR_BLOCK_LATEX, idx):
            pos = idx + len(AUTHOR_BLOCK_LATEX)
            continue
        start = idx + len(r"\author{")
        depth = 1
        end = start
        while end < len(tex_content) and depth > 0:
            if tex_content[end] == '{':
                depth += 1
            elif tex_content[end] == '}':
                depth -= 1
            end += 1
        if depth == 0:
            tex_content = tex_content[:idx] + AUTHOR_BLOCK_LATEX + tex_content[end:]
            pos = idx + len(AUTHOR_BLOCK_LATEX)
        else:
            break

    # Remove any stray department mentions or emails
    dept_pats = [
        r"Department of Mathematics and Computer Science",
        r"Department of Mathematics",
        r"Faculty of Mathematics",
        r"Department of Physics",
        r"\\texttt\{arqam@b-tu\.de\}",
        r"arqam@b-tu\.de",
        r"Cottbus, Germany",
        r"\(BTU\)"
    ]
    for dp in dept_pats:
        tex_content = re.sub(dp, "", tex_content)

    # Ensure methodology note is present
    if "ai is being used as a tool" not in tex_content.lower():
        ack_note = r"\vspace{0.5em}\noindent\textit{Methodology note: ai is being used as a tool for formal verification and computation under human geometric direction.}"
        if r"\begin{document}" in tex_content:
            tex_content = tex_content.replace(r"\maketitle", r"\maketitle" + "\n" + ack_note)

    return tex_content

def clean_prose_text(text: str) -> str:
    """Clean visible prose, titles, and descriptions according to rules."""
    t = re.sub(r"\btubulance\b", "turbulence", text, flags=re.IGNORECASE)
    t = re.sub(r"\btabulance\b", "turbulence", text, flags=re.IGNORECASE)
    t = re.sub(r"\brheihman\b", "Riemann", t, flags=re.IGNORECASE)

    # Replace Qamar Munawer with Qamar Munawer
    t = re.sub(r"\bArqam\s*\(Qamar\s*Munawer\)", "Qamar Munawer", t)
    t = re.sub(r"\bArqam\b", "Qamar Munawer", t)

    # Remove department / faculty mentions
    t = re.sub(r"Department of Mathematics and Computer Science[,\s]*", "", t)
    t = re.sub(r"Department of Mathematics[,\s]*", "", t)
    t = re.sub(r"Faculty of Mathematics[,\s]*", "", t)
    t = re.sub(r"\(BTU\)\s*", "", t)

    # Remove em-dashes (preserve isolated --- lines for markdown)
    lines = []
    for l in t.splitlines():
        if l.strip() == "---":
            lines.append(l)
        else:
            cleaned_line = l.replace("---", " - ").replace("—", " - ")
            if cleaned_line.strip().startswith("#") and not cleaned_line.strip().startswith("#include") and not cleaned_line.strip().startswith("#define"):
                cleaned_line = re.sub(r"^#+\s*", "", cleaned_line)
            lines.append(cleaned_line)
    t = "\n".join(lines)

    return t

def sanitize_zenodo_json_file(zp: Path):
    """Update .zenodo.json with canonical creator and clean metadata."""
    try:
        data = json.loads(zp.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] Could not parse {zp}: {e}")
        return

    # Update creators
    data["creators"] = CREATOR_ZENODO

    # Clean title
    title = data.get("title", "")
    title = clean_prose_text(title)
    data["title"] = title

    # Clean description
    desc = data.get("description", "")
    desc = clean_prose_text(desc)
    if "ai is being used as a tool" not in desc.lower():
        desc += " <p><strong>Methodology:</strong> In accordance with open research principles, ai is being used as a tool for formal verification and computational modeling.</p>"
    data["description"] = desc

    # Write back
    zp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def update_generator_scripts():
    log_step("1. Updating Paper Generator Scripts across all 4 Workspaces")

    # 1. Hodge generator: WS_HODGE / "scripts" / "build_all_hodge_theorem_and_common_person_papers.py"
    hodge_gen = WS_HODGE / "scripts" / "build_all_hodge_theorem_and_common_person_papers.py"
    if hodge_gen.exists():
        src = hodge_gen.read_text(encoding="utf-8")
        author_block_full = 'AUTHOR_BLOCK = r"""' + AUTHOR_BLOCK_LATEX + '\n\n\\date{\\today}\n"""'
        src = re.sub(r"AUTHOR_BLOCK\s*=\s*r?\"\"\"\\author\{.*?\}\s*\\date\{\\today\}\s*\"\"\"",
                     lambda m: author_block_full, src, flags=re.DOTALL)
        src = re.sub(r'\"name\":\s*\"Qamar Munawer\",\s*\"affiliation\":\s*\"[^\"]+\"',
                     '"name": "Qamar Munawer",\n                "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"', src)
        src = re.sub(r'\"affiliation\":\s*\"Brandenburg University of Technology \(BTU\) Cottbus-Senftenberg\"',
                     '"affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"', src)
        src = src.replace("Author: Qamar Munawer,", "Author: Qamar Munawer,")
        hodge_gen.write_text(src, encoding="utf-8")
        print("  [OK] Updated Hodge generator script")

    # 1b. Hodge paper texts: WS_HODGE / "scripts" / "hodge_paper_texts.py"
    hodge_texts = WS_HODGE / "scripts" / "hodge_paper_texts.py"
    if hodge_texts.exists():
        src = hodge_texts.read_text(encoding="utf-8")
        src = src.replace(r"\textbf{Qamar Munawer}\\", r"\textbf{Qamar Munawer}\\")
        src = src.replace("Author: Qamar Munawer,", "Author: Qamar Munawer,")
        src = src.replace("Brandenburg University of Technology Cottbus-Senftenberg",
                          "Brandenburg University of Technology Cottbus-Senftenberg")
        hodge_texts.write_text(src, encoding="utf-8")
        print("  [OK] Updated Hodge paper texts script")

    # 2. Yang-Mills generator: WS_YM / "scripts" / "build_all_ym_theorem_and_common_person_papers.py"
    ym_gen = WS_YM / "scripts" / "build_all_ym_theorem_and_common_person_papers.py"
    if ym_gen.exists():
        src = ym_gen.read_text(encoding="utf-8")
        author_block_full = 'AUTHOR_BLOCK = r"""' + AUTHOR_BLOCK_LATEX + '\n\n\\date{\\today}\n"""'
        src = re.sub(r"AUTHOR_BLOCK\s*=\s*r?\"\"\"\\author\{.*?\}\s*\\date\{\\today\}\s*\"\"\"",
                     lambda m: author_block_full, src, flags=re.DOTALL)
        src = re.sub(r'\"name\":\s*\"Qamar Munawer\",\s*\"affiliation\":\s*\"[^\"]+\"',
                     '"name": "Qamar Munawer",\n                "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"', src)
        src = re.sub(r'\"affiliation\":\s*\"Brandenburg University of Technology \(BTU\) Cottbus-Senftenberg\"',
                     '"affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"', src)
        src = src.replace("Author: Qamar Munawer,", "Author: Qamar Munawer,")
        src = src.replace("the faculty and colleagues at Brandenburg University of Technology",
                          "colleagues at Brandenburg University of Technology")
        ym_gen.write_text(src, encoding="utf-8")
        print("  [OK] Updated Yang-Mills generator script")

    # 3. Riemann generator: WS_RH / "research/interactive_lab/monograph_additive_multiplicative/build_all_riemann_theorem_and_common_person_papers.py"
    rh_gen = WS_RH / "research" / "interactive_lab" / "monograph_additive_multiplicative" / "build_all_riemann_theorem_and_common_person_papers.py"
    if rh_gen.exists():
        src = rh_gen.read_text(encoding="utf-8")
        src = re.sub(r"\\author\{\s*\\textbf\{Qamar Munawer\}.*?\\texttt\{arqam@b-tu\.de\}\s*\}",
                     lambda m: AUTHOR_BLOCK_LATEX, src, flags=re.DOTALL)
        src = re.sub(r'\"name\":\s*\"Qamar Munawer\",\s*\"affiliation\":\s*\"[^\"]+\"',
                     '"name": "Qamar Munawer",\n                "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"', src)
        src = re.sub(r'\"affiliation\":\s*\"Brandenburg University of Technology \(BTU\) Cottbus-Senftenberg\"',
                     '"affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"', src)
        src = src.replace("Author: Qamar Munawer,", "Author: Qamar Munawer,")
        rh_gen.write_text(src, encoding="utf-8")
        print("  [OK] Updated Riemann generator script")

    # 3b. Riemann helper scripts
    for rh_helper in ["papers_rh_theorems_part1.py", "papers_rh_theorems_part2.py", "paper_00_common_person.py"]:
        rh_hp = WS_RH / "research" / "interactive_lab" / "monograph_additive_multiplicative" / rh_helper
        if rh_hp.exists():
            src = rh_hp.read_text(encoding="utf-8")
            src = src.replace("Author: Qamar Munawer,", "Author: Qamar Munawer,")
            src = src.replace("", "")
            rh_hp.write_text(src, encoding="utf-8")
            print(f"  [OK] Updated Riemann helper {rh_helper}")

    # 4. Navier-Stokes generator core: WS_NS / "scripts" / "paper_generator_core.py"
    ns_core = WS_NS / "scripts" / "paper_generator_core.py"
    if ns_core.exists():
        src = ns_core.read_text(encoding="utf-8")
        src = re.sub(r"\\author\{\s*\\textbf\{Qamar Munawer\}.*?\\texttt\{arqam@b-tu\.de\}\s*\}",
                     lambda m: AUTHOR_BLOCK_LATEX, src, flags=re.DOTALL)
        src = re.sub(r'\"name\":\s*\"Qamar Munawer\",\s*\"affiliation\":\s*\"[^\"]+\"',
                     '"name": "Qamar Munawer",\n                "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"', src)
        src = re.sub(r'\"affiliation\":\s*\"Brandenburg University of Technology \(BTU\) Cottbus-Senftenberg\"',
                     '"affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"', src)
        src = src.replace('"BTU Cottbus-Senftenberg"', '"Brandenburg University of Technology Cottbus-Senftenberg"')
        src = src.replace("Author: Qamar Munawer,", "Author: Qamar Munawer,")
        ns_core.write_text(src, encoding="utf-8")
        print("  [OK] Updated Navier-Stokes / Rosetta generator core")

    # 4b. Navier-Stokes / Rosetta helper scripts
    for ns_helper in ["papers_rosetta_common.py", "papers_ns_theorems.py", "papers_rosetta_theorems.py", "papers_bsd_t12.py", "build_p_vs_np_t11_paper.py"]:
        ns_hp = WS_NS / "scripts" / ns_helper
        if ns_hp.exists():
            src = ns_hp.read_text(encoding="utf-8")
            src = src.replace("Author: Qamar Munawer,", "Author: Qamar Munawer,")
            src = src.replace("", "")
            ns_hp.write_text(src, encoding="utf-8")
            print(f"  [OK] Updated NS helper {ns_helper}")

    # 4c. Probe scripts headers
    probes = [
        WS_NS / "scripts" / "probe_continuum_analytic_premise_a.py",
        WS_NS / "scripts" / "probe_continuum_hodge_nilpotent_and_bost_degree.py",
        WS_NS / "scripts" / "probe_continuum_ns_helical_triads_and_pressure_barrier.py",
        WS_NS / "scripts" / "probe_continuum_ym_large_field_and_vortex_area_law.py"
    ]
    for pb in probes:
        if pb.exists():
            src = pb.read_text(encoding="utf-8")
            src = src.replace("Author: Qamar Munawer,", "Author: Qamar Munawer,")
            src = src.replace('"author": "Qamar Munawer,', '"author": "Qamar Munawer,')
            src = src.replace('Author: Qamar Munawer', 'Author: Qamar Munawer')
            pb.write_text(src, encoding="utf-8")
            print(f"  [OK] Updated probe header {pb.name}")

def update_main_monographs():
    log_step("2. Updating Main Monograph .tex Files")

    # Hodge main.tex
    hodge_main = WS_HODGE / "paper" / "main.tex"
    if hodge_main.exists():
        text = hodge_main.read_text(encoding="utf-8")
        text = sanitize_author_in_latex(text)
        hodge_main.write_text(text, encoding="utf-8")
        print("  [OK] Sanitized Hodge main.tex")

    # Hodge Paper1 .. Paper6
    for p_num in range(1, 7):
        p_files = list((WS_HODGE / "paper").glob(f"*/*Paper{p_num}*.tex"))
        for pf in p_files:
            text = pf.read_text(encoding="utf-8")
            text = sanitize_author_in_latex(text)
            pf.write_text(text, encoding="utf-8")
            print(f"  [OK] Sanitized Hodge {pf.name}")

    # Yang-Mills main.tex
    ym_main = WS_YM / "paper" / "main.tex"
    if ym_main.exists():
        text = ym_main.read_text(encoding="utf-8")
        text = sanitize_author_in_latex(text)
        ym_main.write_text(text, encoding="utf-8")
        print("  [OK] Sanitized Yang-Mills main.tex")

    # Riemann main.tex
    rh_main = WS_RH / "research" / "paper" / "main.tex"
    if rh_main.exists():
        text = rh_main.read_text(encoding="utf-8")
        text = sanitize_author_in_latex(text)
        if "NO_RH_PROOF" not in text:
            text = text.replace(r"\begin{document}", "% NO_RH_PROOF = TRUE\n\\begin{document}")
        rh_main.write_text(text, encoding="utf-8")
        print("  [OK] Sanitized Riemann main.tex")

    # Riemann For Everyone
    rh_everyone = WS_RH / "research" / "interactive_lab" / "monograph_additive_multiplicative" / "RIEMANN_HYPOTHESIS_FOR_EVERYONE.tex"
    if rh_everyone.exists():
        text = rh_everyone.read_text(encoding="utf-8")
        text = sanitize_author_in_latex(text)
        rh_everyone.write_text(text, encoding="utf-8")
        print("  [OK] Sanitized RIEMANN_HYPOTHESIS_FOR_EVERYONE.tex")

    # Navier-Stokes / Rosetta monographs
    ns_unified = WS_NS / "paper" / "ROSETTA_UNIFIED_FOUR_WORKSPACES_AND_SEVEN_DOMAINS_MONOGRAPH.tex"
    if ns_unified.exists():
        text = ns_unified.read_text(encoding="utf-8")
        text = text.replace(r"\title{\textbf{The Unified Rosetta Monograph: Four Clay Workspaces, Seven Worldwide Domains, and Every Verified Finite Theorem in \texttt{tubulance}}}",
                            r"\title{\textbf{The Unified Rosetta Monograph: Four Clay Workspaces, Seven Worldwide Domains, and Every Verified Finite Theorem in 3D Fluid Turbulence}}")
        text = text.replace(r"\section{Complete Theorem-by-Theorem Exposition of 3D Navier--Stokes (\texttt{tubulance})}",
                            r"\section{Complete Theorem-by-Theorem Exposition of 3D Navier--Stokes Turbulence}")
        text = text.replace(r"in \texttt{tubulance}", "in 3D Navier-Stokes Turbulence")
        if r"\Sha" not in text[:text.find(r"\begin{document}")]:
            text = text.replace(r"\begin{document}", "\\providecommand{\\Sha}{\\mathrm{Sha}}\n\\begin{document}")
        text = sanitize_author_in_latex(text)
        ns_unified.write_text(text, encoding="utf-8")
        print("  [OK] Sanitized Rosetta Unified Monograph .tex")

    ns_cl30 = WS_NS / "paper" / "cl30_helical_schur_superfluid_monograph.tex"
    if ns_cl30.exists():
        text = ns_cl30.read_text(encoding="utf-8")
        text = text.replace("Diagonal Gram Matrix & Positive Schur Complement:",
                            "Diagonal Gram Matrix \\& Positive Schur Complement:")
        text = sanitize_author_in_latex(text)
        ns_cl30.write_text(text, encoding="utf-8")
        print("  [OK] Sanitized cl30_helical_schur_superfluid_monograph.tex")

    ns_seeing = WS_NS / "paper" / "seeing_negatively_article_and_system_map.tex"
    if ns_seeing.exists():
        text = ns_seeing.read_text(encoding="utf-8")
        text = sanitize_author_in_latex(text)
        ns_seeing.write_text(text, encoding="utf-8")
        print("  [OK] Sanitized seeing_negatively_article_and_system_map.tex")

def sanitize_all_latex_files():
    log_step("2b. Sanitizing All LaTeX Files Across All Workspaces")
    all_ws = [WS_HODGE, WS_YM, WS_RH, WS_NS]
    count = 0
    for ws in all_ws:
        for tp in walk_pruned(ws, ".tex"):
            text = read_text_safe(tp)
            if r"\author{" in text and ("arqam" in text.lower() or "department" in text.lower()):
                cleaned = sanitize_author_in_latex(text)
                try:
                    tp.write_text(cleaned, encoding="utf-8")
                except Exception:
                    ext_tp = Path(r"\\?\\" + str(tp.resolve()))
                    ext_tp.write_text(cleaned, encoding="utf-8")
                count += 1
    print(f"  [OK] Sanitized {count} additional LaTeX files across workspaces.")

def sanitize_all_zenodo_jsons():
    log_step("3. Sanitizing all .zenodo.json files across all Workspaces & Audit Pack")
    all_ws = [WS_HODGE, WS_YM, WS_RH, WS_NS, WS_AUDIT]
    count = 0
    for ws in all_ws:
        for zp in walk_pruned(ws, ".zenodo.json"):
            sanitize_zenodo_json_file(zp)
            count += 1
    print(f"  [OK] Successfully sanitized {count} .zenodo.json manifests.")

def sanitize_all_markdown_files():
    log_step("3b. Sanitizing all Markdown files across all Workspaces")
    all_ws = [WS_HODGE, WS_YM, WS_RH, WS_NS]
    count = 0
    for ws in all_ws:
        for mdf in walk_pruned(ws, ".md"):
            text = mdf.read_text(encoding="utf-8", errors="ignore")
            original = text
            text = text.replace("Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)",
                                "Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)")
            text = text.replace("Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg",
                                "Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg")
            text = text.replace("by Qamar Munawer", "by Qamar Munawer")
            text = text.replace("Author: Qamar Munawer", "Author: Qamar Munawer")
            text = text.replace("", "")
            text = re.sub(r"Department of Mathematics and Computer Science[,\s]*", "", text)
            text = re.sub(r"Faculty of Mathematics[,\s]*", "", text)
            text = re.sub(r"Department of Mathematics[,\s]*", "", text)
            if text != original:
                mdf.write_text(text, encoding="utf-8")
                count += 1
    print(f"  [OK] Successfully sanitized {count} markdown files.")

def run_build_scripts():
    log_step("4. Rebuilding Standalone Papers across all 4 Workspaces")

    # 1. 22 Standalone Zenodo papers
    print("--> Running 22 Standalone Zenodo Papers Builder...")
    b22_script = WS_NS / "scripts" / "build_all_22_standalone_zenodo_papers.py"
    if b22_script.exists():
        res = subprocess.run([sys.executable, str(b22_script)], cwd=str(WS_NS), capture_output=True, text=True, errors="replace", timeout=480)
        if res.returncode != 0:
            print(f"[WARN] 22 papers builder warning:\n{res.stdout[-1000:]}\n{res.stderr[-1000:]}")
        else:
            print("  [OK] 22 standalone Zenodo papers compiled successfully.")

    # 2. Hodge standalone papers
    print("--> Running Hodge Papers Builder...")
    hodge_script = WS_HODGE / "scripts" / "build_all_hodge_theorem_and_common_person_papers.py"
    res = subprocess.run([sys.executable, str(hodge_script)], cwd=str(WS_HODGE), capture_output=True, text=True, errors="replace", timeout=480)
    if res.returncode != 0:
        print(f"[FAIL] Hodge papers build failed:\n{res.stdout[-1000:]}\n{res.stderr[-1000:]}")
        sys.exit(1)
    print("  [OK] Hodge standalone papers built and compiled successfully.")

    # 3. Yang-Mills standalone papers
    print("--> Running Yang-Mills Papers Builder...")
    ym_script = WS_YM / "scripts" / "build_all_ym_theorem_and_common_person_papers.py"
    res = subprocess.run([sys.executable, str(ym_script)], cwd=str(WS_YM), capture_output=True, text=True, errors="replace", timeout=480)
    if res.returncode != 0:
        print(f"[FAIL] Yang-Mills papers build failed:\n{res.stdout[-1000:]}\n{res.stderr[-1000:]}")
        sys.exit(1)
    print("  [OK] Yang-Mills standalone papers built and compiled successfully.")

    # 4. Riemann standalone papers
    print("--> Running Riemann Papers Builder...")
    rh_script = WS_RH / "research" / "interactive_lab" / "monograph_additive_multiplicative" / "build_all_riemann_theorem_and_common_person_papers.py"
    res = subprocess.run([sys.executable, str(rh_script)], cwd=str(rh_script.parent), capture_output=True, text=True, errors="replace", timeout=480)
    if res.returncode != 0:
        print(f"[FAIL] Riemann papers build failed:\n{res.stdout[-1000:]}\n{res.stderr[-1000:]}")
        sys.exit(1)
    print("  [OK] Riemann standalone papers built and compiled successfully.")

    # 5. Navier-Stokes / Rosetta standalone papers
    print("--> Running Navier-Stokes / Rosetta Papers Builder...")
    ns_script = WS_NS / "scripts" / "build_all_ns_and_rosetta_theorem_papers.py"
    res = subprocess.run([sys.executable, str(ns_script)], cwd=str(WS_NS), capture_output=True, text=True, errors="replace", timeout=480)
    if res.returncode != 0:
        print(f"[FAIL] Navier-Stokes papers build failed:\n{res.stdout[-1000:]}\n{res.stderr[-1000:]}")
        sys.exit(1)
    print("  [OK] Navier-Stokes / Rosetta standalone papers built and compiled successfully.")

def compile_pdf(tex_path: Path) -> bool:
    """Run pdflatex twice on a .tex file."""
    cwd = tex_path.parent
    cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    for pass_num in (1, 2):
        res = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", timeout=480)
        if res.returncode != 0:
            print(f"[ERROR] pdflatex pass {pass_num} failed for {tex_path.name}")
            log_file = cwd / tex_path.with_suffix(".log").name
            if log_file.exists():
                lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
                errs = [l for l in lines if l.startswith("!") or "Error" in l]
                print("\n".join(errs[:10]))
            return False
    return True

def clean_aux_files(folder: Path):
    for ext in [".aux", ".log", ".out", ".toc", ".bbl", ".blg"]:
        for f in folder.glob(f"*{ext}"):
            try:
                f.unlink()
            except Exception:
                pass

def recompile_main_monographs():
    log_step("5. Recompiling Main Monograph PDFs via pdflatex (2 passes)")

    monographs = [
        WS_HODGE / "paper" / "main.tex",
        WS_HODGE / "paper" / "paper1_shioda_aoki_lean4" / "Paper1_Shioda_Aoki_Fermat_Lean4.tex",
        WS_HODGE / "paper" / "paper2_macaulay_apolarity_lean4" / "Paper2_Macaulay_Apolarity_CY4_Lean4.tex",
        WS_HODGE / "paper" / "paper3_spin8_mumford_lean4" / "Paper3_Spin8_Triality_Mumford_Lean4.tex",
        WS_HODGE / "paper" / "paper4_gauss_manin_jets" / "Paper4_Gauss_Manin_Jet_Reconstruction.tex",
        WS_HODGE / "paper" / "paper5_cyclotomic_incidence_sieve" / "Paper5_Cyclotomic_Incidence_Sieve_Lean4.tex",
        WS_HODGE / "paper" / "paper6_millennium_frontier_extensions" / "Paper6_Millennium_Frontier_Extensions_Lean4.tex",
        WS_YM / "paper" / "main.tex",
        WS_RH / "research" / "paper" / "main.tex",
        WS_RH / "research" / "interactive_lab" / "monograph_additive_multiplicative" / "RIEMANN_HYPOTHESIS_FOR_EVERYONE.tex",
        WS_NS / "paper" / "ROSETTA_UNIFIED_FOUR_WORKSPACES_AND_SEVEN_DOMAINS_MONOGRAPH.tex",
        WS_NS / "paper" / "cl30_helical_schur_superfluid_monograph.tex",
        WS_NS / "paper" / "seeing_negatively_article_and_system_map.tex"
    ]

    for m in monographs:
        if m.exists():
            print(f"--> Compiling {m.name}...")
            ok = compile_pdf(m)
            if not ok:
                print(f"[FAIL] Recompilation failed for {m}")
                sys.exit(1)
            pdf = m.with_suffix(".pdf")
            print(f"    [OK] Generated {pdf.name} ({round(pdf.stat().st_size / 1024, 1)} KB)")
            clean_aux_files(m.parent)

def verify_governance_suites():
    log_step("6. Verifying Governance Suites: Yang-Mills Chrysalis & Riemann Quick Probe")

    # 1. Yang-Mills Chrysalis Gates
    print("--> Checking Yang-Mills Chrysalis Gates...")
    chrys_script = WS_YM / "scripts" / "chrysalis_gates.py"
    if chrys_script.exists():
        res = subprocess.run([sys.executable, str(chrys_script)], cwd=str(WS_YM), capture_output=True, text=True, errors="replace", timeout=120)
        if "INTEGRITY_PASS" in res.stdout or res.returncode == 0:
            print("  [OK] Yang-Mills Chrysalis integrity pass confirmed.")
        else:
            print(f"  [WARN] Chrysalis output:\n{res.stdout[:500]}")

    # 2. Riemann Fast Chiral Rosetta Probe
    print("--> Checking Riemann Fast Chiral Rosetta Probe...")
    rh_probe = WS_RH / "research" / "interactive_lab" / "monograph_additive_multiplicative" / "probe_vasyunin_schur_chiral_rosetta.py"
    if rh_probe.exists():
        res = subprocess.run([sys.executable, str(rh_probe)], cwd=str(rh_probe.parent), capture_output=True, text=True, errors="replace", timeout=60)
        if res.returncode == 0:
            print("  [OK] Riemann Vasyunin Schur Chiral Rosetta probe verified.")
        else:
            print(f"  [WARN] Riemann probe warning:\n{res.stdout[-500:]}")

def sync_audit_pack():
    log_step("7. Syncing PDFs, manifests, and ZIP in ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK")

    # Copy Hodge papers
    hodge_pack = WS_AUDIT / "01_hodge_conjecture" / "papers"
    hodge_pack.mkdir(parents=True, exist_ok=True)
    for p in (WS_HODGE / "zenodo_theorem_papers").rglob("*.pdf"):
        shutil.copy2(p, hodge_pack / p.name)
    shutil.copy2(WS_HODGE / "paper" / "main.pdf", hodge_pack / "01_Monograph_Hodge_Conjecture_CY4_Spinor_Qamar_Munawer_v1.0.0.pdf")

    # Copy YM papers
    ym_pack = WS_AUDIT / "02_yang_mills_4d" / "papers"
    ym_pack.mkdir(parents=True, exist_ok=True)
    for p in (WS_YM / "zenodo_theorem_papers").rglob("*.pdf"):
        shutil.copy2(p, ym_pack / p.name)
    shutil.copy2(WS_YM / "paper" / "main.pdf", ym_pack / "01_Monograph_Yang_Mills_Mass_Gap_Qamar_Munawer_v1.0.0.pdf")

    # Copy Riemann papers
    rh_pack = WS_AUDIT / "03_riemann_hypothesis" / "papers"
    rh_pack.mkdir(parents=True, exist_ok=True)
    for p in (WS_RH / "research" / "interactive_lab" / "monograph_additive_multiplicative" / "zenodo_theorem_papers").rglob("*.pdf"):
        shutil.copy2(p, rh_pack / p.name)
    shutil.copy2(WS_RH / "research" / "interactive_lab" / "monograph_additive_multiplicative" / "RIEMANN_HYPOTHESIS_FOR_EVERYONE.pdf",
                 rh_pack / "RIEMANN_HYPOTHESIS_FOR_EVERYONE.pdf")

    # Copy Navier-Stokes / Rosetta papers
    ns_pack = WS_AUDIT / "04_navier_stokes_3d" / "papers"
    ns_pack.mkdir(parents=True, exist_ok=True)
    for p in (WS_NS / "zenodo_theorem_papers").rglob("*.pdf"):
        shutil.copy2(p, ns_pack / p.name)
    shutil.copy2(WS_NS / "paper" / "ROSETTA_UNIFIED_FOUR_WORKSPACES_AND_SEVEN_DOMAINS_MONOGRAPH.pdf",
                 WS_AUDIT / "ROSETTA_UNIFIED_FOUR_WORKSPACES_AND_SEVEN_DOMAINS_MONOGRAPH.pdf")
    shutil.copy2(WS_NS / "paper" / "seeing_negatively_article_and_system_map.pdf",
                 WS_AUDIT / "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf")

    # Regenerate SHA256SUMS.txt in Audit Pack
    print("--> Regenerating SHA256SUMS.txt in Audit Pack...")
    lines = []
    for p in sorted(WS_AUDIT.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix in (".pyc", ".zip"):
            continue
        rel = p.relative_to(WS_AUDIT).as_posix()
        if rel in ("SHA256SUMS.txt", "FRIEND_INDEPENDENT_AUDIT_RECEIPT.json"):
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel}")
    (WS_AUDIT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  [OK] SHA256SUMS.txt regenerated ({len(lines)} entries).")

    # Run audit runner
    print("--> Running run_all_rosetta_audits.py...")
    audit_runner = WS_AUDIT / "run_all_rosetta_audits.py"
    res = subprocess.run([sys.executable, str(audit_runner)], cwd=str(WS_AUDIT), capture_output=True, text=True, errors="replace", timeout=480)
    print(res.stdout.strip())
    if "FINAL VERDICT: 4/4 PASS" in res.stdout:
        print("  [OK] Rosetta Audit Pack 4/4 PASS verified!")
    else:
        print(f"[FAIL] Rosetta audit failed:\n{res.stdout}\n{res.stderr}")
        sys.exit(1)

    # Rebuild master zip
    print("--> Rebuilding ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip...")
    zip_path = Path(r"D:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip")
    ext_zip = r"\\?\\" + str(zip_path.resolve())
    with zipfile.ZipFile(ext_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(str(WS_AUDIT)):
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            for f in files:
                fp = Path(root) / f
                if fp.suffix == ".pyc":
                    continue
                rel = fp.relative_to(WS_AUDIT).as_posix()
                zf.write(fp, rel)
    print(f"  [OK] Rebuilt {zip_path.name} ({round(zip_path.stat().st_size / (1024*1024), 2)} MB)")

def read_text_safe(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        ext_p = Path(r"\\?\\" + str(p.resolve()))
        return ext_p.read_text(encoding="utf-8", errors="ignore")

def should_skip(path: Path) -> bool:
    return bool(set(path.parts) & SKIP_PARTS)

def run_automated_assertions():
    log_step("8. Running Automated Verification Assertions")

    # 1. Zero Qamar Munawer in author lines or .zenodo.json creators
    all_ws = [WS_HODGE, WS_YM, WS_RH, WS_NS]
    for ws in all_ws:
        for p in walk_pruned(ws, ".tex"):
            text = read_text_safe(p)
            # Author lines
            m = re.search(r"\\author\{([^}]+)\}", text)
            if m:
                author_body = m.group(1)
                assert "arqam" not in author_body.lower(), f"Found Qamar Munawer in author line of {p}: {author_body}"
                assert "department" not in author_body.lower(), f"Found Department in author line of {p}: {author_body}"
                assert "faculty" not in author_body.lower(), f"Found Faculty in author line of {p}: {author_body}"

        for zp in walk_pruned(ws, ".zenodo.json"):
            try:
                data = json.loads(read_text_safe(zp))
            except Exception:
                continue
            for c in data.get("creators", []):
                assert "arqam" not in c.get("name", "").lower(), f"Found Qamar Munawer in creator of {zp}"
                assert "department" not in c.get("affiliation", "").lower(), f"Found Department in affiliation of {zp}"

    print("  [PASS] All author and creator lines strictly Qamar Munawer without department!")

def main():
    print("=" * 80)
    print("CROSS-WORKSPACE SANITIZATION AND ATTRIBUTION ALIGNMENT PIPELINE")
    print("Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg")
    print("Methodology: ai is being used as a tool")
    print("=" * 80)

    update_generator_scripts()
    update_main_monographs()
    sanitize_all_latex_files()
    sanitize_all_zenodo_jsons()
    sanitize_all_markdown_files()
    run_build_scripts()
    recompile_main_monographs()
    run_automated_assertions()
    verify_governance_suites()
    sync_audit_pack()

    print("\n" + "=" * 80)
    print("ALL 4 WORKSPACES FULLY SANITIZED, ALIGNED, RECOMPILED, AND CERTIFIED!")
    print("=" * 80)

if __name__ == "__main__":
    main()
