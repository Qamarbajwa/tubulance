"""Core engine for NS-RPM-1 Research Pathway Memory, Similarity & Resurrection."""
import os
import json
import yaml
import jsonschema
import csv
from typing import Dict, List, Any, Optional

class ResearchMemoryEngine:
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.memory_dir = os.path.join(root_dir, "research_memory")
        self.schema_path = os.path.join(self.memory_dir, "RESEARCH_PATHWAY_SCHEMA.json")
        self.pathway_registry_path = os.path.join(self.memory_dir, "RESEARCH_PATHWAY_REGISTRY.yaml")
        self.obstruction_registry_path = os.path.join(self.memory_dir, "RESEARCH_OBSTRUCTION_REGISTRY.yaml")
        self.negative_evidence_path = os.path.join(self.memory_dir, "NEGATIVE_EVIDENCE_LEDGER.yaml")
        self.relation_graph_path = os.path.join(self.memory_dir, "PATHWAY_RELATION_GRAPH.yaml")
        self.similarity_matrix_path = os.path.join(self.memory_dir, "PATHWAY_SIMILARITY_MATRIX.csv")
        self.resurrection_queue_path = os.path.join(self.memory_dir, "RESEARCH_RESURRECTION_QUEUE.yaml")
        self.review_cadence_path = os.path.join(self.memory_dir, "RESEARCH_REVIEW_CADENCE.yaml")
        
        self.pathways: List[Dict[str, Any]] = []
        self.obstructions: List[Dict[str, Any]] = []
        self.negative_evidence: List[Dict[str, Any]] = []
        self.graph_edges: List[Dict[str, Any]] = []
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.pathway_registry_path):
            with open(self.pathway_registry_path, "r", encoding="utf-8") as f:
                self.pathways = yaml.safe_load(f).get("pathways", [])
        if os.path.exists(self.obstruction_registry_path):
            with open(self.obstruction_registry_path, "r", encoding="utf-8") as f:
                self.obstructions = yaml.safe_load(f).get("obstructions", [])
        if os.path.exists(self.negative_evidence_path):
            with open(self.negative_evidence_path, "r", encoding="utf-8") as f:
                self.negative_evidence = yaml.safe_load(f).get("negative_evidence", [])
        if os.path.exists(self.relation_graph_path):
            with open(self.relation_graph_path, "r", encoding="utf-8") as f:
                self.graph_edges = yaml.safe_load(f).get("edges", [])

    def validate(self) -> Dict[str, Any]:
        """Validate schema conformance, referential integrity, and graph consistency."""
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        errors = []
        pathway_ids = {p["pathway_id"] for p in self.pathways}
        obstruction_ids = {o["obstruction_id"] for o in self.obstructions}

        # 1. Validate each pathway against JSON schema
        for p in self.pathways:
            try:
                jsonschema.validate(instance=p, schema=schema)
            except jsonschema.ValidationError as e:
                errors.append(f"Pathway {p.get('pathway_id')} schema validation error: {e.message}")

            # Check parent/descendant IDs
            for parent in p.get("parent_pathways", []):
                if parent not in pathway_ids:
                    errors.append(f"Pathway {p['pathway_id']} references unknown parent {parent}")
            for desc in p.get("descendant_pathways", []):
                if desc not in pathway_ids and desc != "TP2-G4": # allow upcoming TP2-G4
                    errors.append(f"Pathway {p['pathway_id']} references unknown descendant {desc}")

            # Check obstruction IDs
            for obs in p.get("obstruction_ids", []):
                if obs not in obstruction_ids:
                    errors.append(f"Pathway {p['pathway_id']} references unknown obstruction {obs}")

        # 2. Validate negative evidence ledger references
        for neg in self.negative_evidence:
            if neg["pathway_id"] not in pathway_ids:
                errors.append(f"Negative evidence {neg['record_id']} references unknown pathway {neg['pathway_id']}")
            if neg["governing_obstruction"] not in obstruction_ids:
                errors.append(f"Negative evidence {neg['record_id']} references unknown obstruction {neg['governing_obstruction']}")

        # 3. Validate graph edge references
        valid_nodes = pathway_ids | {"TP2-G4"}
        for edge in self.graph_edges:
            if edge["source"] not in valid_nodes:
                errors.append(f"Graph edge source {edge['source']} not found in pathways")
            if edge["target"] not in valid_nodes:
                errors.append(f"Graph edge target {edge['target']} not found in pathways")

        return {
            "valid": len(errors) == 0,
            "pathways_count": len(self.pathways),
            "obstructions_count": len(self.obstructions),
            "negative_evidence_count": len(self.negative_evidence),
            "graph_edges_count": len(self.graph_edges),
            "errors": errors
        }

    def explain_similarity(self, id1: str, id2: str) -> Dict[str, Any]:
        """Explain the multi-dimensional similarity between two pathways."""
        p1 = next((p for p in self.pathways if p["pathway_id"] == id1), None)
        p2 = next((p for p in self.pathways if p["pathway_id"] == id2), None)
        
        # Handle TP2-G4 virtual pathway if requested
        if id1 == "TP2-G4":
            p1 = {
                "pathway_id": "TP2-G4",
                "title": "Adversarial Quadratic Variation Analysis",
                "trajectory_dependence": "LAGRANGIAN_STOCHASTIC",
                "stochastic_component": True,
                "obstruction_ids": ["NS-OBS-004", "NS-OBS-005"],
                "similarity_tags": ["stochastic_cauchy", "quadratic_variation", "deformation_amplification", "production_rate_Q"]
            }
        if id2 == "TP2-G4":
            p2 = {
                "pathway_id": "TP2-G4",
                "title": "Adversarial Quadratic Variation Analysis",
                "trajectory_dependence": "LAGRANGIAN_STOCHASTIC",
                "stochastic_component": True,
                "obstruction_ids": ["NS-OBS-004", "NS-OBS-005"],
                "similarity_tags": ["stochastic_cauchy", "quadratic_variation", "deformation_amplification", "production_rate_Q"]
            }

        if not p1 or not p2:
            return {"error": f"One or both pathways ({id1}, {id2}) not found."}

        shared_obstructions = list(set(p1.get("obstruction_ids", [])) & set(p2.get("obstruction_ids", [])))
        shared_tags = list(set(p1.get("similarity_tags", [])) & set(p2.get("similarity_tags", [])))

        return {
            "pathway_1": id1,
            "pathway_2": id2,
            "trajectory_similarity": "EXACT_MATCH" if p1["trajectory_dependence"] == p2["trajectory_dependence"] else "PARTIAL",
            "stochastic_similarity": "BOTH_STOCHASTIC" if (p1["stochastic_component"] and p2["stochastic_component"]) else ("BOTH_DETERMINISTIC" if (not p1["stochastic_component"] and not p2["stochastic_component"]) else "DUAL_STOCHASTIC_DETERMINISTIC"),
            "shared_obstructions": shared_obstructions,
            "shared_tags": shared_tags
        }

    def run_preflight_search(self, task_id: str, query_tags: List[str], query_obstructions: List[str]) -> Dict[str, Any]:
        """Perform mandatory pre-flight research memory search for a new gate."""
        related_pathways = []
        for p in self.pathways:
            overlap_tags = set(p.get("similarity_tags", [])) & set(query_tags)
            overlap_obs = set(p.get("obstruction_ids", [])) & set(query_obstructions)
            if overlap_tags or overlap_obs:
                related_pathways.append({
                    "pathway_id": p["pathway_id"],
                    "title": p["title"],
                    "status": p["status"],
                    "shared_tags": list(overlap_tags),
                    "shared_obstructions": list(overlap_obs),
                    "surviving_results": p.get("surviving_results", []),
                    "negative_results": p.get("negative_results", [])
                })

        relevant_neg_evidence = [
            neg for neg in self.negative_evidence
            if neg["governing_obstruction"] in query_obstructions or neg["pathway_id"] in [rp["pathway_id"] for rp in related_pathways]
        ]

        return {
            "task_id": task_id,
            "query_tags": query_tags,
            "query_obstructions": query_obstructions,
            "top_related_pathways": related_pathways,
            "relevant_negative_evidence": relevant_neg_evidence,
            "active_obstructions": [obs for obs in self.obstructions if obs["obstruction_id"] in query_obstructions]
        }

def validate_registry_and_schema(root_dir: str = ".") -> Dict[str, Any]:
    engine = ResearchMemoryEngine(root_dir)
    return engine.validate()

def run_preflight_search(task_id: str, tags: List[str], obstructions: List[str], root_dir: str = ".") -> Dict[str, Any]:
    engine = ResearchMemoryEngine(root_dir)
    return engine.run_preflight_search(task_id, tags, obstructions)
