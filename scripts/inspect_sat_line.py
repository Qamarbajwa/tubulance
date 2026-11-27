from pathlib import Path

target_file = Path(r"d:\Comfy UI\tubulance\tare_core\export_theorem_audit_appendix.py")
content = target_file.read_text(encoding="utf-8")

# Fix line 1503 and 1506:
content = content.replace(
    r"genus $g = 210$ ($4^g = 1.13\\times 10^{{15}}$)",
    r"genus $g = 210$ ($4^g = 1.13\\times 10^{{15}}$)".replace("($4^g", "($4^g$") # wait, let's write the exact string:
)

# Let's replace the whole sat line and cad line:
old_sat_line = 'tex.append(f"3-SAT Pfaffian Genus Phase Transition & 64 vars, $\\\\alpha \\\\in [1.5, 5.0]$ & Critical $\\\\alpha_c = {p_pt}$, genus $g = 210$ ($4^g = 1.13\\\\times 10^{{15}}$) & \\\\textbf{{PASS}} \\\\\\\\")'
new_sat_line = 'tex.append(f"3-SAT Pfaffian Genus Phase Transition & 64 vars, $\\\\alpha \\\\in [1.5, 5.0]$ & Critical $\\\\alpha_c = {p_pt}$, genus $g = 210$ ($4^g = 1.13\\\\times 10^{{15}}$) & \\\\textbf{{PASS}} \\\\\\\\")'.replace("($4^g", "($4^g")

# Actually let's look at the exact line in file:
for line in content.splitlines():
    if "3-SAT Pfaffian Genus Phase Transition" in line and "tex.append" in line:
        print("Found SAT line:", repr(line))
        # It has: ($4^g = 1.13\\times 10^{{15}}$)
        # In LaTeX, that produces: ($4^g = 1.13\times 10^{15}$)
        # Notice: There is no $ between ( and 4!
        # It should be: ($4^g = 1.13\\times 10^{{15}}$) -> with $ right after (: ($4^g = 1.13\\times 10^{15}$)
        fixed_line = line.replace("($4^g", "($4^g").replace("($4^g = 1.13", "($4^g = 1.13")
        # Wait, if line has: ($4^g
        # That has $4^g, which closes math mode at g!
        # If we want the whole expression in math mode:
        # ($4^g = 1.13 \times 10^{15}$) -> ($(4^g = 1.13 \\times 10^{15})$)
        fixed_line = line.replace("($4^g = 1.13\\\\times 10^{{15}}$)", "($4^g = 1.13 \\\\times 10^{{15}}$)")
        content = content.replace(line, '    tex.append(f"3-SAT Pfaffian Genus Phase Transition & 64 vars, $\\\\alpha \\\\in [1.5, 5.0]$ & Critical $\\\\alpha_c = {p_pt}$, genus $g = 210$ ($4^g = 1.13\\\\times 10^{{15}}$) & \\\\textbf{{PASS}} \\\\\\\\")'.replace("($4^g = 1.13\\\\times 10^{{15}}$)", "($4^g = 1.13\\\\times 10^{{15}}$)"))

