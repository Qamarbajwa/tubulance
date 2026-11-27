import json
import os
import urllib.request

token = os.environ.get("ZENODO_TOKEN") or os.environ.get("ZENODO_ACCESS_TOKEN") or os.environ.get("ZENODO_API_TOKEN")

for dep_id in [24431866, 24431632, 24430756]:
    req = urllib.request.Request(f"https://zenodo.org/api/deposit/depositions/{dep_id}", headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"=== Deposition {dep_id} ===")
            print("Title:", data.get("title"))
            print("State:", data.get("state"))
            print("Submitted:", data.get("submitted"))
            print("DOI:", data.get("doi"))
            print("Files count:", len(data.get("files", [])))
            for f in data.get("files", []):
                print(f"  - {f.get('filename')} ({f.get('filesize')} bytes)")
    except Exception as e:
        print(f"Error {dep_id}:", e)
