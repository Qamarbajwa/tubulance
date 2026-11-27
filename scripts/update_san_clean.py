from pathlib import Path
import re

target_file = Path(r"d:\Comfy UI\tubulance\tare_core\export_theorem_audit_appendix.py")
content = target_file.read_text(encoding="utf-8")

s_idx = content.find("def sanitize_latex(")
e_idx = content.find("def sanitize_ident(")

new_san = '''def sanitize_latex(text: str) -> str:
    """Escapes special LaTeX characters and replaces forbidden tokens (#, em-dashes)."""
    # Replace em-dashes
    t = text.replace("---", ", ").replace("--", ", ")
    # Replace hashes
    t = t.replace("#P", "sharp-P").replace("#", "No. ")
    # Replace percent signs if unescaped
    t = re.sub(r"(?<!\\\\)%", r"\\%", t)
    # Math operators and comparisons
    t = t.replace("!=", r"$\\ne$")
    t = t.replace("<=", r"$\\le$").replace(">=", r"$\\ge$")
    t = t.replace("≥", r"$\\ge$").replace("≤", r"$\\le$").replace("≠", r"$\\ne$").replace("·", r"$\\cdot$")
    t = t.replace("α", r"$\\alpha$").replace("θ", r"$\\theta$").replace("ν", r"$\\nu$").replace("π", r"$\\pi$")
    t = t.replace("Omega(n^2)", r"$\\Omega(n^2)$")
    t = t.replace("S^3", r"$S^3$").replace("4^k", r"$4^k$").replace("E^4", r"$E^4$").replace("n^2", r"$n^2$").replace("4^g", r"$4^g$")
    t = re.sub(r"\\b([A-Za-z0-9]+)\\^([A-Za-z0-9]+)\\b", r"$\\1^{\\2}$", t)
    t = t.replace("<", r"$<$").replace(">", r"$>$")
    # Replace unescaped underscores
    t = re.sub(r"(?<!\\\\)_", r"\\_", t)
    return t

'''

content = content[:s_idx] + new_san + content[e_idx:]
target_file.write_text(content, encoding="utf-8")
print("Updated sanitize_latex in export_theorem_audit_appendix.py")
