from pathlib import Path
root = Path('d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK')
text = (root / 'run_all_rosetta_audits.py').read_text(encoding='utf-8')
import re
m = re.search(r'probes = \[(.*?)\]', text, re.DOTALL)
for p in m.group(1).splitlines():
    p = p.strip().strip('",')
    if p.endswith('.py'):
        exists = (root / p).exists()
        print(f"{p:<80} Exists: {exists}")
