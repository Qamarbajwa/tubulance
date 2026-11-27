import json
import os
import urllib.request

token = os.environ.get("ZENODO_TOKEN") or os.environ.get("ZENODO_ACCESS_TOKEN") or os.environ.get("ZENODO_API_TOKEN")
req = urllib.request.Request("https://zenodo.org/api/deposit/depositions", headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        depositions = json.loads(resp.read().decode("utf-8"))
        print(f"Total depositions found: {len(depositions)}")
        for dep in depositions[:15]:
            dep_id = dep.get("id")
            state = dep.get("state")
            sub = dep.get("submitted")
            doi = dep.get("doi")
            title = (dep.get("title") or "")[:60]
            print(f"ID: {dep_id} | State: {state} | Submitted: {sub} | DOI: {doi} | Title: {title}")
except Exception as e:
    print("Error:", e)
