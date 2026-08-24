"""Run Phase 0 research memory preflight for TP2-G4-A2."""
from navier3d.research_memory import ResearchMemoryEngine

engine = ResearchMemoryEngine()
preflight = engine.run_preflight_search(
    task_id="TP2-G4-A2-PREFLIGHT",
    query_tags=[
        "vorticity_gradient",
        "finite_time_deformation",
        "singular_vectors",
        "strain_eigenframe",
        "pressure_hessian",
        "viscous_direction",
        "frame_rotation",
        "trajectory_persistence",
        "alignment",
        "orientation",
        "critical_scaling",
        "stochastic_cauchy"
    ],
    query_obstructions=[
        "NS-OBS-002",
        "NS-OBS-003",
        "NS-OBS-004",
        "NS-OBS-005",
        "NS-OBS-007",
        "NS-OBS-009"
    ]
)

print("=== TP2-G4-A2 PRE-FLIGHT PATHWAY SEARCH RESULTS ===")
print("Related Pathways count:", len(preflight["top_related_pathways"]))
for p in preflight["top_related_pathways"]:
    print(f" * {p['pathway_id']}: {p['title']} (Status: {p['status']})")
    print(f"   Shared Tags: {p['shared_tags']}")
    print(f"   Shared Obstructions: {p['shared_obstructions']}")

print("\nRelevant Negative Evidence count:", len(preflight["relevant_negative_evidence"]))
for neg in preflight["relevant_negative_evidence"]:
    print(f" - [{neg['record_id']}] ({neg['pathway_id']}): {neg['title']} -> {neg['mathematical_verdict']}")

print("\nActive Obstructions count:", len(preflight["active_obstructions"]))
for obs in preflight["active_obstructions"]:
    print(f" - [{obs['obstruction_id']}]: {obs['name']}")
