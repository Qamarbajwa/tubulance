from pathlib import Path

sync_py = Path(r"D:\Comfy UI\idea memory\obsidian brains\big picture\scripts\sort_and_sync_obsidian_central_brain.py")
text = sync_py.read_text(encoding="utf-8")

commits = {
    '01_Hodge_Knowledge_Base.md': ('c63c650', '691db11'),
    '02_Yang_Mills_Knowledge_Base.md': ('6dc2dbc', 'f14390a'),
    '03_Riemann_Knowledge_Base.md': ('363d118', '36be1f7'),
    '04_Navier_Stokes_Knowledge_Base.md': ('0940d37', '252fdec'),
    '05_Birch_Swinnerton_Dyer_Knowledge_Base.md': ('89f5443', '57b7dbd')
}

for kb, (old_c, new_c) in commits.items():
    text = text.replace(f'"head_commit": "{old_c}"', f'"head_commit": "{new_c}"')

sync_py.write_text(text, encoding="utf-8")
print("Updated commits in sort_and_sync_obsidian_central_brain.py")
