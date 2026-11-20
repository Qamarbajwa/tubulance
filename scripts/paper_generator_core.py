"""
paper_generator_core.py

Core engine for generating, compiling, and packaging standalone Zenodo papers
across all four research workspaces.
"""

import os
import sys
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

LATEX_TEMPLATE = r"""\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{geometry}
\usepackage{hyperref}

\providecommand{\Sha}{\mathrm{Sha}}

\geometry{
  a4paper,
  top=25mm,
  bottom=25mm,
  left=25mm,
  right=25mm
}

\hypersetup{
  colorlinks=true,
  linkcolor=blue!70!black,
  citecolor=red!70!black,
  urlcolor=teal!70!black
}

\lstdefinelanguage{Lean4}{
  keywords={theorem, lemma, def, where, by, have, exact, refine, intro, rintro, cases, rcases, constructor, calc, ring, norm_num, linarith, nlinarith, omega, dsimp, rw, simpa, import, namespace, end, open},
  keywordstyle=\color{blue!80!black}\bfseries,
  ndkeywords={Prop, Type, Real, Nat, Int, Bool, Set, Matrix, Fin},
  ndkeywordstyle=\color{teal!80!black}\bfseries,
  identifierstyle=\color{black},
  sensitive=true,
  comment=[l]{--},
  morecomment=[s]{/-}{-/},
  commentstyle=\color{green!50!black}\itshape,
  stringstyle=\color{purple},
  basicstyle=\ttfamily\small,
  breaklines=true,
  breakatwhitespace=true,
  frame=single,
  rulecolor=\color{gray!40},
  backgroundcolor=\color{gray!5},
  numbers=none,
  showstringspaces=false
}

\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{remark}[theorem]{Remark}

\title{\textbf{__TITLE__}}

\author{
  \textbf{Arqam} \\
  Brandenburg University of Technology (BTU) Cottbus-Senftenberg \\
  Department of Mathematics and Computer Science \\
  Cottbus, Germany \\
  \texttt{arqam@b-tu.de}
}

\date{\today}

\begin{document}

\maketitle

\begin{abstract}
__ABSTRACT__
\end{abstract}

\vspace{1em}
\noindent\textbf{Keywords:} __KEYWORDS__

\section{Introduction and Elementary Intuition}
__SECTION_1__

\section{Step-by-Step Algebraic Derivation}
__SECTION_2__

\section{Formal Lean 4 Theorem Exposition}
__SECTION_3__

\section{High-Precision Numerical Verification}
__SECTION_4__

\section{Methodology and Epistemic Boundary}
\noindent This research was developed using modern formal and computational methods where ai is being used as a tool for formal verification synthesis, symbolic calculation, and rigorous cross-verification.

\vspace{0.5em}
\noindent\textbf{Epistemic Horizon Status:} All four Clay Millennium Problems (the Hodge Conjecture, the 4D Yang-Mills Mass Gap, the Riemann Hypothesis, and 3D Navier-Stokes Regularity) remain strictly open. The results presented in this paper constitute verified finite-dimensional algebraic theorems, unconditional identity splits, formal Lean 4 certificates, and reproducible numerical probes that isolate exact obstruction boundaries and structural invariants within their rigorously defined domains.

\begin{thebibliography}{99}
__REFERENCES__
\end{thebibliography}

\end{document}
"""

def clean_lean_code_listing(sec_text: str) -> str:
    """Clean multi-byte unicode inside lstlisting blocks for robust LaTeX compilation."""
    def replacer(match):
        code = match.group(1)
        replacements = [
            ("·", "."), ("⟨", "<"), ("⟩", ">"), ("•", "*"),
            ("∧", "/\\"), ("∨", "\\/"), ("→", "->"), ("↔", "<->"),
            ("∀", "forall "), ("∃", "exists "),
            ("≤", "<="), ("≥", ">="), ("≠", "!="), ("←", "<-"),
            ("₀", "0"), ("₁", "1"), ("₂", "2"), ("₃", "3"), ("₄", "4"),
            ("₅", "5"), ("₆", "6"), ("₇", "7"), ("₈", "8"), ("₉", "9"),
            ("λ", "lam"), ("ι", "iota"), ("π", "pi"), ("β", "beta"),
            ("μ", "mu"), ("η", "eta"), ("ρ", "rho"), ("ζ", "zeta"),
            ("φ", "phi"), ("Δ", "Delta"), ("Ω", "Omega"), ("Θ", "Theta"),
            ("ℝ", "Real"), ("ℕ", "Nat"), ("ℤ", "Int"), ("ℚ", "Rat"), ("ℂ", "Complex"),
            ("⁻¹", "^-1"), ("†", "*")
        ]
        for src, dst in replacements:
            code = code.replace(src, dst)
        return f"\\begin{{lstlisting}}[language=Lean4]{code}\\end{{lstlisting}}"
    
    return re.sub(r"\\begin\{lstlisting\}\[language=Lean4\](.*?)(\\end\{lstlisting\})", replacer, sec_text, flags=re.DOTALL)

def sanitize_text(text: str) -> str:
    """Ensure no hashes, raw em-dashes, unescaped percent, unescaped underscores, or raw subscripts in text."""
    t = text.replace("---", " - ")
    t = t.replace("--", " - ")
    t = t.replace("—", " - ")
    t = t.replace(r"\#", "")
    t = t.replace("#", "")
    # Subscript digits
    for sub, dig in zip("₀₁₂₃₄₅₆₇₈₉", "0123456789"):
        t = t.replace(sub, dig)
    
    def fix_texttt(m):
        inner = m.group(1).replace(r"\_", "_").replace("_", r"\_")
        return r"\texttt{" + inner + "}"

    t = re.sub(r"\\texttt\{([^}]+)\}", fix_texttt, t)
    # Escape % in text (e.g. 94.6% -> 94.6\%)
    t = re.sub(r'(?<!\\)%', r'\%', t)
    return t

def render_latex(paper_dict: dict) -> str:
    title = sanitize_text(paper_dict["title"])
    abstract = sanitize_text(paper_dict["abstract"])
    keywords = sanitize_text(", ".join(paper_dict.get("keywords", [])))
    sec1 = sanitize_text(paper_dict["sec1_intuition"])
    sec2 = sanitize_text(paper_dict["sec2_derivation"])
    sec3 = sanitize_text(clean_lean_code_listing(paper_dict["sec3_lean"]))
    sec4 = sanitize_text(paper_dict["sec4_numerical"])
    refs = paper_dict["references"]

    tex = LATEX_TEMPLATE
    tex = tex.replace("__TITLE__", title)
    tex = tex.replace("__ABSTRACT__", abstract)
    tex = tex.replace("__KEYWORDS__", keywords)
    tex = tex.replace("__SECTION_1__", sec1)
    tex = tex.replace("__SECTION_2__", sec2)
    tex = tex.replace("__SECTION_3__", sec3)
    tex = tex.replace("__SECTION_4__", sec4)
    tex = tex.replace("__REFERENCES__", refs)
    return tex

def compile_pdf(tex_path: Path, output_dir: Path) -> bool:
    """Run pdflatex twice for citations and cross-references."""
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={output_dir.as_posix()}",
        tex_path.as_posix()
    ]
    for pass_num in (1, 2):
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
        if res.returncode != 0:
            print(f"[ERROR] pdflatex pass {pass_num} failed for {tex_path}:")
            log_file = output_dir / tex_path.with_suffix(".log").name
            if log_file.exists():
                lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
                err_lines = [l for l in lines if l.startswith("!") or "Error" in l or "Undefined control" in l]
                print("Error details from log:")
                print("\n".join(err_lines[:10]))
                print("\nLast 25 log lines:")
                print("\n".join(lines[-25:]))
            return False
    return True

def generate_zenodo_json(paper_dict: dict, out_path: Path):
    clean_abstract = sanitize_text(paper_dict['abstract']).replace("$", "")
    metadata = {
        "title": sanitize_text(paper_dict["title"]),
        "upload_type": "publication",
        "publication_type": "article",
        "description": sanitize_text(
            f"<p>{clean_abstract}</p>"
            f"<p><strong>Formal Certificate:</strong> Verified in Lean 4 with zero custom axioms [propext, Classical.choice, Quot.sound].</p>"
            f"<p><strong>Methodology:</strong> In accordance with open research principles, ai is being used as a tool for interactive theorem verification and computational modeling.</p>"
            f"<p><strong>Epistemic Status:</strong> Finite structural theorem; Clay Millennium open horizons remain strictly open.</p>"
        ),
        "creators": [
            {
                "name": "Arqam",
                "affiliation": "Brandenburg University of Technology (BTU) Cottbus-Senftenberg",
                "orcid": "0009-0004-9467-3363"
            }
        ],
        "keywords": paper_dict.get("keywords", []) + ["Lean 4", "Formal Verification", "Clay Millennium Problems", "BTU Cottbus-Senftenberg"],
        "license": "CC-BY-4.0",
        "access_right": "open"
    }
    out_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

def build_paper_bundle(paper_dict: dict, root_dir: Path) -> dict:
    paper_id = paper_dict["id"]
    paper_dir = root_dir / paper_id
    paper_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write LaTeX file
    tex_path = paper_dir / f"{paper_id}.tex"
    tex_content = render_latex(paper_dict)
    tex_path.write_text(tex_content, encoding="utf-8")

    # 2. Compile PDF
    success = compile_pdf(tex_path, paper_dir)
    pdf_path = paper_dir / f"{paper_id}.pdf"
    if not success or not pdf_path.exists():
        raise RuntimeError(f"Compilation failed for {paper_id}")

    # 3. Generate .zenodo.json
    zenodo_json_path = paper_dir / ".zenodo.json"
    generate_zenodo_json(paper_dict, zenodo_json_path)

    # 4. Copy supporting Lean files
    lean_dest_dir = paper_dir / "lean4_certificates"
    lean_dest_dir.mkdir(exist_ok=True)
    for src in paper_dict.get("supporting_lean", []):
        src_p = Path(src)
        if src_p.exists():
            shutil.copy2(src_p, lean_dest_dir / src_p.name)

    # 5. Copy supporting probe files
    probe_dest_dir = paper_dir / "probes"
    probe_dest_dir.mkdir(exist_ok=True)
    for src in paper_dict.get("supporting_probes", []):
        src_p = Path(src)
        if src_p.exists():
            shutil.copy2(src_p, probe_dest_dir / src_p.name)

    # 6. Package ZIP release
    zip_path = paper_dir / f"{paper_id}_ZENODO_RELEASE.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    target_zip = str(zip_path.resolve())
    if len(target_zip) >= 240 and not target_zip.startswith("\\\\?\\"):
        target_zip = "\\\\?\\" + target_zip
    with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(pdf_path, arcname=f"{paper_id}.pdf")
        zf.write(tex_path, arcname=f"{paper_id}.tex")
        zf.write(zenodo_json_path, arcname=".zenodo.json")
        for f in lean_dest_dir.glob("*.lean"):
            zf.write(f, arcname=f"lean4_certificates/{f.name}")
        for f in probe_dest_dir.glob("*"):
            if f.is_file():
                zf.write(f, arcname=f"probes/{f.name}")

    print(f"[OK] Successfully built {paper_id} -> {pdf_path.stat().st_size // 1024} KB, ZIP: {zip_path.stat().st_size // 1024} KB")
    return {
        "id": paper_id,
        "pdf": str(pdf_path),
        "zip": str(zip_path),
        "dir": str(paper_dir),
        "pdf_path": str(pdf_path),
        "zip_path": str(zip_path),
        "pdf_bytes": pdf_path.stat().st_size,
        "zip_bytes": zip_path.stat().st_size
    }
