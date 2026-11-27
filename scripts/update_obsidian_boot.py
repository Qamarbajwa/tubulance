from pathlib import Path

boot_file = Path(r"D:\Comfy UI\idea memory\obsidian brains\big picture\00_AGENT_BOOT_STATE.md")
content = boot_file.read_text(encoding="utf-8")

old_sec4 = """## 4. Permanent Zenodo DOIs & Proof Bundles
- **Hodge:** `10.5281/zenodo.24381741` (`v1.5.0-rosetta`, Concept `24329779`)
- **Yang–Mills:** `10.5281/zenodo.24393101` (`v1.3.0-rosetta`, Concept `24327876`)
- **Riemann:** `10.5281/zenodo.24398285`, `24398293` (`v3.3.0-rosetta`)
- **Navier–Stokes:** `10.5281/zenodo.24381824` (`v1.2.0-rosetta`, Concept `24378624`)
- **Master Audit Pack:** `d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip` (`4/4 PASS`)"""

new_sec4 = """## 4. Permanent Zenodo DOIs & Proof Bundles
- **Master Multi-Project & Compute:** `10.5281/zenodo.24431866` (`v2.1.0-contemporary-compute`, HTTP 200 OK)
- **BSD Formalization:** `10.5281/zenodo.24431632` (`v1.0.0-contemporary-bsd`, HTTP 200 OK)
- **Hodge:** `10.5281/zenodo.24381741` (`v1.5.0-rosetta`, Concept `24329779`)
- **Yang–Mills:** `10.5281/zenodo.24393101` (`v1.3.0-rosetta`, Concept `24327876`)
- **Riemann:** `10.5281/zenodo.24398285`, `24398293` (`v3.3.0-rosetta`)
- **Navier–Stokes:** `10.5281/zenodo.24381824` (`v1.2.0-rosetta`, Concept `24378624`)
- **Master Audit Pack:** `d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip` (`4/4 PASS`, SHA-256 `43bbb9d1efbf...`)
- **Professor Pack:** `d:/Comfy UI/READY_TO_MAIL_PROFESSOR_PACK/` (`3/3 PDFs + En/De Letters + Verified Receipt`)"""

assert old_sec4 in content, "old_sec4 not found"
content = content.replace(old_sec4, new_sec4)
boot_file.write_text(content, encoding="utf-8")
print(f"Updated {boot_file.name} successfully (total lines: {len(content.splitlines())}).")
