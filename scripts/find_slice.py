with open(r"d:\Comfy UI\tubulance\tare_core\export_theorem_audit_appendix.py", "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find('benchmarks = gpu.get("benchmarks", {})')
idx2 = text.find(r'tex.append(r"\bottomrule")', idx1)
print("Found slice from", idx1, "to", idx2)
print(text[idx1:idx2])
