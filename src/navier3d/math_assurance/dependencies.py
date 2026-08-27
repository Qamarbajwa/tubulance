"""Dependency DAG validation, cycle detection, and lineage traversal."""
import os
import yaml
from typing import Dict, List, Set, Any, Optional


class DependencyGraphManager:
    def __init__(self, constitution_dir: Optional[str] = None):
        if constitution_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            constitution_dir = os.path.join(base_dir, "mathematical_constitution")
        self.constitution_dir = constitution_dir
        self.graph_file = os.path.join(constitution_dir, "CLAIM_DEPENDENCY_GRAPH.yaml")
        self.nodes, self.edges = self._load_graph()

    def _load_graph(self):
        if not os.path.exists(self.graph_file):
            return {}, []
        with open(self.graph_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        nodes = {item["id"]: item for item in data.get("nodes", [])}
        edges = data.get("edges", [])
        return nodes, edges

    def get_direct_prerequisites(self, node_id: str) -> List[str]:
        """Return all direct parents (prerequisites) of a node."""
        return [edge["source"] for edge in self.edges if edge["target"] == node_id]

    def get_all_ancestors(self, node_id: str) -> Set[str]:
        """Return full transitive closure of prerequisite nodes."""
        ancestors = set()
        to_visit = list(self.get_direct_prerequisites(node_id))
        while to_visit:
            curr = to_visit.pop()
            if curr not in ancestors:
                ancestors.add(curr)
                to_visit.extend(self.get_direct_prerequisites(curr))
        return ancestors

    def detect_cycles(self) -> List[List[str]]:
        """Detect any circular dependencies in the DAG using DFS."""
        adj = {}
        for edge in self.edges:
            src = edge["source"]
            tgt = edge["target"]
            adj.setdefault(src, []).append(tgt)

        visited = {} # 0: unvisited, 1: visiting, 2: visited
        cycles = []

        def dfs(node, path):
            visited[node] = 1
            path.append(node)
            for neighbor in adj.get(node, []):
                if visited.get(neighbor, 0) == 1:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                elif visited.get(neighbor, 0) == 0:
                    dfs(neighbor, path)
            path.pop()
            visited[node] = 2

        for node in list(self.nodes.keys()):
            if visited.get(node, 0) == 0:
                dfs(node, [])

        return cycles
