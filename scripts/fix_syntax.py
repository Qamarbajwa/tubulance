import re
from pathlib import Path

target_file = Path(r"d:\Comfy UI\tubulance\tare_core\export_theorem_audit_appendix.py")
content = target_file.read_text(encoding="utf-8")

# Fix line 1512:
# Replace: tex.append(r"\textbf{Strict Epistemic Integrity Lock:}\\\")
# With:    tex.append(r"\textbf{Strict Epistemic Integrity Lock:}\\\\")
content = content.replace(r'tex.append(r"\textbf{Strict Epistemic Integrity Lock:}\\\")', r'tex.append(r"\textbf{Strict Epistemic Integrity Lock:}\\\\")')
# Also fix other lines if needed
target_file.write_text(content, encoding="utf-8")
print("Fixed raw string backslash syntax.")
