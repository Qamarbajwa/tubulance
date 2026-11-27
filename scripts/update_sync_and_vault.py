from pathlib import Path
import re

# 1. Update knowledge base frontmatters
kb_updates = {
    '01_Hodge_Conjecture/01_Hodge_Knowledge_Base.md': {'head_commit': 'c63c650', 'release_tag': 'v1.6.0-contemporary-tare'},
    '02_Yang_Mills_4D/02_Yang_Mills_Knowledge_Base.md': {'head_commit': '6dc2dbc', 'release_tag': 'v1.5.0-contemporary-tare'},
    '03_Riemann_Hypothesis/03_Riemann_Knowledge_Base.md': {'head_commit': '363d118', 'release_tag': 'v3.4.0-contemporary-tare'},
    '04_Navier_Stokes_3D/04_Navier_Stokes_Knowledge_Base.md': {'head_commit': '0940d37', 'release_tag': 'v2.1.0-contemporary-compute'},
    '05_Birch_Swinnerton_Dyer/05_Birch_Swinnerton_Dyer_Knowledge_Base.md': {'head_commit': '89f5443', 'release_tag': 'v1.0.0-contemporary-bsd'}
}

vault_root = Path(r"D:\Comfy UI\idea memory\obsidian brains\big picture")
for rel_path, updates in kb_updates.items():
    p = vault_root / rel_path
    if p.exists():
        text = p.read_text(encoding='utf-8')
        for k, v in updates.items():
            text = re.sub(rf'^{k}:.*$', f'{k}: {v}', text, flags=re.MULTILINE)
        p.write_text(text, encoding='utf-8')
        print(f"Updated {p.name}")

# 2. Update sort_and_sync_obsidian_central_brain.py Section 4
sync_py = vault_root / 'scripts' / 'sort_and_sync_obsidian_central_brain.py'
text = sync_py.read_text(encoding='utf-8')

old_zenodo_block = '''        "## 4. Permanent Zenodo DOIs & Proof Bundles",
        "- **Hodge:** `10.5281/zenodo.24381741` (`v1.5.0-rosetta`, Concept `24329779`)",
        "- **Yang–Mills:** `10.5281/zenodo.24393101` (`v1.3.0-rosetta`, Concept `24327876`)",
        "- **Riemann:** `10.5281/zenodo.24398285`, `24398293` (`v3.3.0-rosetta`)",
        "- **Navier–Stokes:** `10.5281/zenodo.24381824` (`v1.2.0-rosetta`, Concept `24378624`)",
        "- **Master Audit Pack:** `d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip` (`4/4 PASS`)",'''

new_zenodo_block = '''        "## 4. Permanent Zenodo DOIs & Proof Bundles",
        "- **Master Multi-Project & Compute:** `10.5281/zenodo.24433657` (`v2.1.1-contemporary-compute`, HTTP 200 OK)",
        "- **BSD Formalization:** `10.5281/zenodo.24431632` (`v1.0.0-contemporary-bsd`, HTTP 200 OK)",
        "- **Hodge:** `10.5281/zenodo.24381741` (`v1.5.0-rosetta`, Concept `24329779`)",
        "- **Yang–Mills:** `10.5281/zenodo.24393101` (`v1.3.0-rosetta`, Concept `24327876`)",
        "- **Riemann:** `10.5281/zenodo.24398285`, `24398293` (`v3.3.0-rosetta`)",
        "- **Navier–Stokes:** `10.5281/zenodo.24381824` (`v1.2.0-rosetta`, Concept `24378624`)",
        "- **Master Audit Pack:** `d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip` (`4/4 PASS`)",
        "- **Professor Pack:** `d:/Comfy UI/READY_TO_MAIL_PROFESSOR_PACK/` (`10/10 PDFs + En/De Letters + Verified Receipt`)",'''

if old_zenodo_block in text:
    text = text.replace(old_zenodo_block, new_zenodo_block)
    print("Updated job5 zenodo block in sort_and_sync_obsidian_central_brain.py")
else:
    print("old_zenodo_block not found in job5")

old_payload_block = '''        "## 4. Permanent Zenodo DOIs & Companion Bundles",
        "- **Hodge:** `10.5281/zenodo.24381741` (`v1.5.0-rosetta`, Concept `24329779`)",
        "- **Yang–Mills:** `10.5281/zenodo.24393101` (`v1.3.0-rosetta`, Concept `24327876`)",
        "- **Riemann:** `10.5281/zenodo.24398285`, `24398293` (`v3.3.0-rosetta`)",
        "- **Navier–Stokes:** `10.5281/zenodo.24381824` (`v1.2.0-rosetta`, Concept `24378624`)",
        "- **Master Audit Pack:** `d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip` (`4/4 PASS`)",'''

new_payload_block = '''        "## 4. Permanent Zenodo DOIs & Companion Bundles",
        "- **Master Multi-Project & Compute:** `10.5281/zenodo.24433657` (`v2.1.1-contemporary-compute`, HTTP 200 OK)",
        "- **BSD Formalization:** `10.5281/zenodo.24431632` (`v1.0.0-contemporary-bsd`, HTTP 200 OK)",
        "- **Hodge:** `10.5281/zenodo.24381741` (`v1.5.0-rosetta`, Concept `24329779`)",
        "- **Yang–Mills:** `10.5281/zenodo.24393101` (`v1.3.0-rosetta`, Concept `24327876`)",
        "- **Riemann:** `10.5281/zenodo.24398285`, `24398293` (`v3.3.0-rosetta`)",
        "- **Navier–Stokes:** `10.5281/zenodo.24381824` (`v1.2.0-rosetta`, Concept `24378624`)",
        "- **Master Audit Pack:** `d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip` (`4/4 PASS`)",
        "- **Professor Pack:** `d:/Comfy UI/READY_TO_MAIL_PROFESSOR_PACK/` (`10/10 PDFs + En/De Letters + Verified Receipt`)",'''

if old_payload_block in text:
    text = text.replace(old_payload_block, new_payload_block)
    print("Updated job7 payload block in sort_and_sync_obsidian_central_brain.py")
else:
    print("old_payload_block not found in job7")

# Also update author in directives if needed
text = text.replace("author attribution to Arqam", "author attribution to Qamar Munawer")

sync_py.write_text(text, encoding='utf-8')
print("Successfully wrote updated sort_and_sync_obsidian_central_brain.py")
