"""Python utility to compute multidimensional pathway similarity matrix for NS-RPM-1."""
import yaml
import csv
import itertools
import numpy as np

def compute_similarity(p1, p2):
    """Compute multidimensional similarity S(p1, p2) in [0.0, 1.0]."""
    if p1["pathway_id"] == p2["pathway_id"]:
        return 1.000

    score = 0.0
    weights = {
        "trajectory": 0.20,
        "stochastic": 0.15,
        "obstructions": 0.20,
        "tags": 0.25,
        "domain_reg": 0.10,
        "lineage": 0.10
    }

    # 1. Trajectory dependence
    if p1["trajectory_dependence"] == p2["trajectory_dependence"]:
        score += weights["trajectory"] * 1.0
    elif {p1["trajectory_dependence"], p2["trajectory_dependence"]} == {"LAGRANGIAN_DETERMINISTIC", "LAGRANGIAN_STOCHASTIC"}:
        score += weights["trajectory"] * 0.70
    elif "HYBRID" in (p1["trajectory_dependence"], p2["trajectory_dependence"]):
        score += weights["trajectory"] * 0.50

    # 2. Stochastic component
    if p1["stochastic_component"] == p2["stochastic_component"]:
        score += weights["stochastic"] * 1.0

    # 3. Shared obstructions
    obs1 = set(p1.get("obstruction_ids", []))
    obs2 = set(p2.get("obstruction_ids", []))
    if obs1 and obs2:
        jaccard_obs = len(obs1 & obs2) / len(obs1 | obs2)
        score += weights["obstructions"] * jaccard_obs

    # 4. Similarity tags Jaccard
    tags1 = set(p1.get("similarity_tags", []))
    tags2 = set(p2.get("similarity_tags", []))
    if tags1 and tags2:
        jaccard_tags = len(tags1 & tags2) / len(tags1 | tags2)
        score += weights["tags"] * jaccard_tags

    # 5. Domain / Regularity
    if p1.get("domain") == p2.get("domain"):
        score += weights["domain_reg"] * 0.5
    if p1.get("regularity_class") == p2.get("regularity_class"):
        score += weights["domain_reg"] * 0.5

    # 6. Lineage connection (parent/child)
    if p1["pathway_id"] in p2.get("parent_pathways", []) or p2["pathway_id"] in p1.get("parent_pathways", []):
        score += weights["lineage"] * 1.0
    elif p1["pathway_id"] in p2.get("descendant_pathways", []) or p2["pathway_id"] in p1.get("descendant_pathways", []):
        score += weights["lineage"] * 1.0

    return round(score, 3)

def generate_similarity_matrix():
    with open("research_memory/RESEARCH_PATHWAY_REGISTRY.yaml", "r") as f:
        data = yaml.safe_load(f)
    
    pathways = data["pathways"]
    # Also add TP2-G4 candidate node for comparison
    tp2_g4 = {
        "pathway_id": "TP2-G4",
        "title": "Adversarial Quadratic Variation & Deformation Analysis",
        "parent_pathways": ["TP2-G3"],
        "descendant_pathways": [],
        "trajectory_dependence": "LAGRANGIAN_STOCHASTIC",
        "stochastic_component": True,
        "domain": "T^3 or R^3",
        "regularity_class": "C^infinity",
        "obstruction_ids": ["NS-OBS-004", "NS-OBS-005"],
        "similarity_tags": ["stochastic_cauchy", "quadratic_variation", "deformation_amplification", "production_rate_Q", "adversarial_counterexample", "riccati"]
    }
    all_pathways = pathways + [tp2_g4]
    ids = [p["pathway_id"] for p in all_pathways]

    matrix = []
    for p1 in all_pathways:
        row = [p1["pathway_id"]]
        for p2 in all_pathways:
            row.append(compute_similarity(p1, p2))
        matrix.append(row)

    with open("research_memory/PATHWAY_SIMILARITY_MATRIX.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pathway_id"] + ids)
        writer.writerows(matrix)

    print("PATHWAY_SIMILARITY_MATRIX.csv generated successfully.")

if __name__ == "__main__":
    generate_similarity_matrix()
