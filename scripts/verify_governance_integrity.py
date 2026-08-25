import os
import json
import hashlib

with open("governanace/v2.10.0_SHA256_MANIFEST.json", "r") as f:
    manifest = json.load(f)

print("=== GOVERNANCE v2.10.0 INTEGRITY CHECK ===")
for filename, meta in manifest.items():
    filepath = os.path.join("governanace", filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        match = (h == meta["sha256"])
        status = "MATCH" if match else "MISMATCH"
        print(f"[{status}] {filename} -> {h[:16]}")
    else:
        print(f"[REFERENCE_ONLY / NOT_PRESENT] {filename}")
