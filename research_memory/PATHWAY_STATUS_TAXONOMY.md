# RESEARCH PATHWAY STATUS TAXONOMY & RELATION ONTOLOGY

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Infrastructure:** `NS-RPM-1 (Research Pathway Memory, Similarity & Resurrection Infrastructure)`  
**Governance:** Autonomous Project Governance v2.9.4  
**Date:** 2026-08-24T17:38:00Z  

---

## 1. Core Principle

> **A research pathway may terminate or be superseded, but it never disappears from the scientific search space.**  
> Every new result must be compared not only with current theory, but with the project's own abandoned, negative, dormant, and superseded research branches.

---

## 2. Pathway Lifecycle Status Taxonomy

Every pathway in `RESEARCH_PATHWAY_REGISTRY.yaml` is assigned exactly one primary lifecycle status:

| Status Code | Definition | Governance Rule |
|---|---|---|
| `ACTIVE` | Currently executing candidate under active bounded contract. | Exactly one or bounded active set per increment. |
| `COMPLETED_CANONICAL` | Formally proven, independently verified, and technically accepted into canonical scientific state. | Sealed; immutable without formal reconciliation. |
| `COMPLETED_CANONICAL_WITH_LIMITATIONS` | Verified and accepted, but subject to explicit, documented domain or regularity limitations. | Valid for in-class inferences; cannot extrapolate beyond stated limits. |
| `FALSIFIED` | The central starting thesis was disproved by rigorous counterexample or analytical proof. | Preserved with exact `what_was_falsified` vs `what_was_not_falsified` separation. |
| `TERMINATED_BY_OBSTRUCTION` | Halted because progress requires bypassing an identified structural obstruction in `RESEARCH_OBSTRUCTION_REGISTRY.yaml`. | Inactive until an explicit `reopen_condition` is triggered. |
| `SUPERSEDED_AS_PRIMARY_OBJECT` | The underlying object was proved to be a reparameterization or subset of another object, shifting primary focus. | Historical record preserved; descendants inherit surviving results. |
| `REFORMULATED` | The thesis was translated into a more precise or equivalent mathematical framework. | Linked via `REFORMULATES` relation. |
| `DORMANT` | Deprioritized or paused without formal falsification; awaiting new tools or higher priority. | Evaluated at 5-gate cadences and upon relevant trigger events. |
| `RESURRECTION_CANDIDATE` | A dormant or terminated pathway whose `reopen_conditions` were satisfied by a newly discovered result. | Blocks automatic execution; requires verifier/acceptance evaluation. |

---

## 3. Pathway Relation Ontology

Relationships between pathways form a directed scientific graph:

- `DERIVED_FROM`: Pathway $B$ originated directly from the findings of $A$.
- `REFORMULATES`: Pathway $B$ rewrites the mathematical thesis of $A$ in a new framework without changing its truth value.
- `SUPERSEDES`: Pathway $B$ replaces $A$ as the primary analytical line of inquiry.
- `FALSIFIES`: Pathway $B$ constructed a counterexample or proof that disproves the core thesis of $A$.
- `WEAKENS`: Pathway $B$ proves a version of $A$ under more restrictive assumptions.
- `STRENGTHENS`: Pathway $B$ proves a version of $A$ under broader or critical assumptions.
- `SHARES_OBSTRUCTION_WITH`: Pathway $B$ encountered the exact same obstruction ID as $A$.
- `MATHEMATICALLY_ANALOGOUS_TO`: Pathway $B$ utilizes analytical techniques structurally isomorphic to $A$.
- `EMPIRICALLY_RESEMBLES`: Pathway $B$ produces numerical/empirical signatures resembling $A$.
- `STOCHASTIC_ANALOGUE_OF`: Pathway $B$ is the stochastic Lagrangian extension of deterministic Eulerian pathway $A$.
- `DETERMINISTIC_ANALOGUE_OF`: Pathway $B$ is the deterministic limit of stochastic pathway $A$.
- `REOPENED_BY`: Pathway $A$ was resurrected as a candidate due to new evidence from $B$.
- `MERGED_INTO`: Pathway $A$ was synthesized with another branch to form composite pathway $B$.
