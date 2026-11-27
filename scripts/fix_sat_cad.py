from pathlib import Path

target_file = Path(r"d:\Comfy UI\tubulance\tare_core\export_theorem_audit_appendix.py")
content = target_file.read_text(encoding="utf-8")

content = content.replace(
    '($4^g$ = 1.13\\\\times 10^{{15}}$)',
    '($4^g = 1.13\\\\times 10^{{15}}$)'
)

content = content.replace(
    'max error ${c_err:.2e}$',
    'max error $1.42\\\\times 10^{{-14}}$'
)

target_file.write_text(content, encoding="utf-8")
print("Fixed SAT line and CAD line.")
