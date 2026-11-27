with open(r"d:\Comfy UI\tubulance\tare_core\export_theorem_audit_appendix.py", "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find('benchmarks = gpu.get("benchmarks", {})')
idx2 = text.find('benchmarks = gpu.get("benchmarks", {})', idx1 + 1)
print("Second occurrence from", idx2, "to", idx2 + 1500)
print(text[idx2:idx2 + 1500])
