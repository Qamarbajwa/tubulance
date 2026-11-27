from pathlib import Path
import re

target_file = Path(r"d:\Comfy UI\tubulance\tare_core\export_theorem_audit_appendix.py")
content = target_file.read_text(encoding="utf-8")

# Update sanitize_latex
old_san = '''def sanitize_latex(text: str) -> str:
    """Escapes special LaTeX characters and replaces forbidden tokens (#, em-dashes)."""
    # Replace em-dashes
    t = text.replace("---", ", ").replace("--", ", ")
    # Replace hashes
    t = t.replace("#P", "sharp-P").replace("#", "No. ")
    # Replace percent signs if unescaped
    t = re.sub(r"(?<!\\)%", r"\\%", t)
    # Replace math symbols first
    t = t.replace("<=", r"$\\le$").replace(">=", r"$\\ge$")
    t = t.replace("â‰¥", r"$\\ge$").replace("â‰¤", r"$\\le$").replace("â‰ ", r"$\\ne$").replace("Â·", r"$\\cdot$")
    t = t.replace("Î±", r"$\\alpha$").replace("Î¸", r"$\\theta$").replace("Î½", r"$\\nu$").replace("Ï€", r"$\\pi$")
    t = t.replace("<", r"$<$").replace(">", r"$>$")
    # Replace unescaped underscores
    t = re.sub(r"(?<!\\)_", r"\\_", t)
    return t'''

new_san = '''def sanitize_latex(text: str) -> str:
    """Escapes special LaTeX characters and replaces forbidden tokens (#, em-dashes)."""
    # Replace em-dashes
    t = text.replace("---", ", ").replace("--", ", ")
    # Replace hashes
    t = t.replace("#P", "sharp-P").replace("#", "No. ")
    # Replace percent signs if unescaped
    t = re.sub(r"(?<!\\\\)%", r"\\%", t)
    # Replace inequalities and operators
    t = t.replace("!=", r"$\\ne$")
    t = t.replace("<=", r"$\\le$").replace(">=", r"$\\ge$")
    t = t.replace("â‰¥", r"$\\ge$").replace("â‰¤", r"$\\le$").replace("â‰ ", r"$\\ne$").replace("Â·", r"$\\cdot$")
    t = t.replace("Î±", r"$\\alpha$").replace("Î¸", r"$\\theta$").replace("Î½", r"$\\nu$").replace("Ï€", r"$\\pi$")
    # Replace carets e.g. S^3, 4^k, E^4, n^2
    t = re.sub(r"\\b([A-Za-z0-9]+)\\^([A-Za-z0-9]+)\\b", r"$\\1^{\\2}$", t)
    t = t.replace("<", r"$<$").replace(">", r"$>$")
    # Replace unescaped underscores
    t = re.sub(r"(?<!\\\\)_", r"\\_", t)
    return t'''

content = content.replace(old_san, new_san)

# Fix line 1451
old_line = r"clean_pt = sanitize_latex(f\"{thm['premise']} $\implies$ {thm['target']}\")"
new_line = r"""clean_p = sanitize_latex(thm['premise'])
        clean_t = sanitize_latex(thm['target'])
        clean_pt = f"{clean_p} $\\implies$ {clean_t}""""

content = content.replace(old_line, new_line)

target_file.write_text(content, encoding="utf-8")
print("Updated sanitize_latex and table row generation.")
