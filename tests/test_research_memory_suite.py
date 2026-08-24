"""Automated test suite for NS-RPM-1 Research Pathway Memory Infrastructure."""
import os
import csv
import yaml
import pytest
from navier3d.research_memory import (
    ResearchMemoryEngine,
    validate_registry_and_schema,
    run_preflight_search,
)


def test_schema_and_referential_integrity():
    """Verify that all backfilled pathways strictly conform to schema and referential integrity."""
    result = validate_registry_and_schema()
    assert result["valid"] is True, f"Validation failed with errors: {result['errors']}"
    assert result["pathways_count"] == 13
    assert result["obstructions_count"] >= 8
    assert result["negative_evidence_count"] >= 10
    assert result["graph_edges_count"] >= 15


def test_negative_evidence_ledger_completeness():
    """Verify that every negative evidence record contains falsified hypotheses and governing obstructions."""
    engine = ResearchMemoryEngine()
    for neg in engine.negative_evidence:
        assert "record_id" in neg
        assert "falsified_hypothesis" in neg
        assert "governing_obstruction" in neg
        assert neg["governing_obstruction"].startswith("NS-OBS-")


def test_relation_graph_structure():
    """Verify that the relation graph contains required ontological relation types."""
    engine = ResearchMemoryEngine()
    relations = {edge["relation"] for edge in engine.graph_edges}
    expected_relations = {
        "DERIVED_FROM",
        "REFORMULATES",
        "SUPERSEDES",
        "STOCHASTIC_ANALOGUE_OF",
        "MATHEMATICALLY_ANALOGOUS_TO",
        "SHARES_OBSTRUCTION_WITH",
    }
    assert expected_relations.issubset(relations), f"Missing relations: {expected_relations - relations}"


def test_similarity_matrix_structure_and_symmetry():
    """Verify that the multidimensional similarity matrix is symmetric with 1.0 diagonal."""
    matrix_path = "research_memory/PATHWAY_SIMILARITY_MATRIX.csv"
    assert os.path.exists(matrix_path)
    
    with open(matrix_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    header = reader[0][1:] # pathway IDs
    rows = reader[1:]
    
    assert len(header) == len(rows)
    
    for i, row in enumerate(rows):
        p_id = row[0]
        assert p_id == header[i]
        scores = [float(val) for val in row[1:]]
        # Diagonal must be 1.0
        assert scores[i] == 1.0
        # Check symmetry
        for j, score in enumerate(scores):
            other_score = float(rows[j][i+1])
            assert score == other_score, f"Asymmetry at ({p_id}, {header[j]}): {score} != {other_score}"


def test_resurrection_queue_structure():
    """Verify that resurrection queue lists dormant pathways and prerequisite gates."""
    engine = ResearchMemoryEngine()
    with open(engine.resurrection_queue_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    triggers = data.get("resurrection_triggers", [])
    queue = data.get("active_queue", [])
    
    assert len(triggers) >= 4
    assert len(queue) >= 3
    
    for item in queue:
        assert "pathway_id" in item
        assert "reopen_hypothesis" in item
        assert "prerequisite_gate" in item


def test_g4_preflight_pathway_search():
    """Verify that the mandatory pre-flight search for TP2-G4 correctly surfaces historical connections."""
    query_tags = ["stochastic_cauchy", "quadratic_variation", "deformation_amplification", "production_rate_Q"]
    query_obstructions = ["NS-OBS-004", "NS-OBS-005"]
    
    result = run_preflight_search("TP2-G4-PREFLIGHT", query_tags, query_obstructions)
    
    assert result["task_id"] == "TP2-G4-PREFLIGHT"
    related_ids = [p["pathway_id"] for p in result["top_related_pathways"]]
    
    # Must surface TP2-G3 (immediate parent)
    assert "TP2-G3" in related_ids
    # Must surface NS-TRAJECTORY-PERSISTENCE-1
    assert "NS-TRAJECTORY-PERSISTENCE-1" in related_ids
    
    # Must retrieve active obstructions NS-OBS-004 and NS-OBS-005
    retrieved_obs_ids = [obs["obstruction_id"] for obs in result["active_obstructions"]]
    assert "NS-OBS-004" in retrieved_obs_ids
    assert "NS-OBS-005" in retrieved_obs_ids
    
    # Verify similarity explanation
    engine = ResearchMemoryEngine()
    comp = engine.explain_similarity("TP2-G4", "TH9-R")
    assert "error" not in comp
    assert "NS-OBS-004" not in comp.get("shared_obstructions", []) # TH9-R has 003, 007
    assert comp["stochastic_similarity"] == "DUAL_STOCHASTIC_DETERMINISTIC"
