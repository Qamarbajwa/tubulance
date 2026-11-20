import re
from pathlib import Path

def check_file(path_str):
    text = Path(path_str).read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"=== Checking {path_str} ===")
    for i, line in enumerate(lines):
        # find unescaped _ or ^
        # ignore lines with code blocks, listings, import, or python keys
        if any(k in line for k in ["#", '"""', "supporting_", "PACK_ROOT", "id\":", "keywords\":", "\\texttt", "\\lst", "lstlisting", "\\bibitem", "\\label", "\\ref"]):
            continue
        # strip math blocks $...$ and check if remaining has _ or ^
        clean = re.sub(r'\$.*?\$', '', line)
        clean = re.sub(r'\\\(.*?\\\)', '', clean)
        clean = re.sub(r'\\\[.*?\\\]', '', clean)
        clean = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', clean)
        if any(c in clean for c in ['^', '_']):
            # check if _ is in python identifier
            # remove words like sec1_intuition
            clean_words = re.sub(r'\b[a-zA-Z0-9_]+\b', '', clean)
            if '^' in clean:
                print(f"  Line {i+1} has '^': {line.strip()[:100]}")
            if '_' in clean_words:
                print(f"  Line {i+1} has '_': {line.strip()[:100]}")

check_file("d:/Comfy UI/tubulance/scripts/papers_rosetta_common.py")
check_file("d:/Comfy UI/tubulance/scripts/papers_ns_theorems.py")
check_file("d:/Comfy UI/tubulance/scripts/papers_rosetta_theorems.py")
