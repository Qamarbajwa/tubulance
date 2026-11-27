import json
with open(r"d:\Comfy UI\rheihman hypothesis\scripts\probe_unconditional_premise_discharge_receipt.json", "r") as f:
    d = json.load(f)
print("total_theorems_audited:", d.get("total_theorems_audited"))
print("total_unconditional_theorems:", d.get("total_unconditional_theorems"))
print("total_conditional_theorems:", d.get("total_conditional_theorems"))
print("unconditional_ratio_pct:", d.get("unconditional_ratio_pct"))
print("epistemic_boundary:", d.get("epistemic_boundary"))
print("riemann_details:", d.get("riemann_details"))
print("cross_workspace_details:", d.get("cross_workspace_details"))
