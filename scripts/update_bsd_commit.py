from pathlib import Path

sync_py = Path(r"D:\Comfy UI\idea memory\obsidian brains\big picture\scripts\sort_and_sync_obsidian_central_brain.py")
t = sync_py.read_text(encoding="utf-8")
t = t.replace('"head_commit": "89f5443"', '"head_commit": "57b7dbd"')
sync_py.write_text(t, encoding="utf-8")

p_bsd = Path(r"D:\Comfy UI\idea memory\obsidian brains\big picture\05_Birch_Swinnerton_Dyer\05_Birch_Swinnerton_Dyer_Knowledge_Base.md")
t_bsd = p_bsd.read_text(encoding="utf-8")
t_bsd = t_bsd.replace("head_commit: 89f5443", "head_commit: 57b7dbd")
p_bsd.write_text(t_bsd, encoding="utf-8")
print("BSD updated.")
