# MATHEMATICAL RESEARCH CONSTITUTION & ASSURANCE LAYER — v1.0.0

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Parent Governance:** Autonomous Project Runtime Governance Kernel v2.10.1 (High Assurance, Risk Tier T4)  
**Scope:** Universal Mathematical Epistemology, Proof Lifecycle, Claim Assurance, and Canonicalization  

---

## 1. Foundational Epistemic Hierarchy

```text
v2.10.1 PROJECT RUNTIME GOVERNANCE
          │
          ├── truth / evidence (E1–E5) / agent roles / Git / acceptance
          │
          ▼
MATHEMATICAL RESEARCH CONSTITUTION (NS-MRC-1)
          │
          ├── Problem Identity Lock (§2)
          ├── Assumption Register & Drift Detection (§3)
          ├── Claim Registry & Multidimensional Claim Passport (§4)
          ├── Claim Lifecycle State Machine (§5)
          ├── Known Results & Dependency Graph (§6)
          ├── Proof Incident Registry & Mathematical Regression Rules (§7)
          ├── Load-Bearing Result Registry (§8)
          ├── Correctness–Novelty–Significance Separation (§9)
          ├── Understanding Package Gate (§10)
          ├── Assumption Minimization, Alternative Proofs & Generalization (§11)
          ├── Formalization Fidelity Gate (§12)
          └── External Acceptance Ladder & Canonicalization (§13)
          │
          ▼
RESEARCH PATHWAY MEMORY (NS-RPM-1)
          │
          ├── pathways / obstructions / negative evidence / resurrection
          │
          ▼
NAVIER–STOKES SCIENTIFIC PROGRAM (NS-TRAJECTORY-PERSISTENCE-2)
```

---

## 2. Principle of Epistemic Separation

$$\boxed{ \text{Internal Verification } \neq \text{ Novelty } \neq \text{ Significance } \neq \text{ Understanding } \neq \text{ External Validation } \neq \text{ Community Acceptance} }$$

A mathematical claim must never receive a monolithic label such as `ACCEPTED_CANONICAL` without specifying its coordinates across all independent dimensions of the **Claim Passport**.

### 2.1 Two Meanings of Canonical
To avoid conflating internal project consensus with global scientific consensus, the project enforces two strictly distinct canonical states:
1. **`PROJECT_CANONICAL`**: The claim has passed all internal verification gates (E3 reproducible machine tests, E4 independent proof audit, understanding package validation, and mathematical regression checks) and is frozen as internal scientific truth for this repository.
2. **`FIELD_CANONICAL`**: The claim has been externally published, peer-reviewed, independently scrutinized by human mathematical specialists, and absorbed into the broader mathematical community's standard body of literature.

The term **`SOLVED`** is strictly reserved for `FIELD_CANONICAL` resolution of the governing Millennium problem.

---

## 3. The 12 Permanent Mathematical Assurance Mechanisms

### Mechanism 1: Problem Identity Lock
- The target problem formulation, domain ($\mathbb{T}^3$), initial data class ($u_0 \in C^\infty$, $\nabla \cdot u_0 = 0$), boundary conditions, quantifiers ($\forall u_0 \ \exists! u \in C^\infty([0, \infty))$), and allowed equivalent formulations are permanently frozen in `PROBLEM_IDENTITY.yaml`.
- Prohibits hidden relaxation shifts (e.g. solving a localized, smoothed, or conditional sub-problem and claiming target closure).

### Mechanism 2: Assumption Register & Automatic Drift Detection
- Every assumption used in any derivation is registered with a permanent ID in `ASSUMPTION_REGISTER.yaml` and classified as:
  - `FOUNDATIONAL`: Explicitly part of the problem identity (e.g. incompressibility $\nabla \cdot u = 0$).
  - `DERIVED`: Rigorously proved from foundational assumptions.
  - `KNOWN_CONSEQUENCE`: Proven literature fact (e.g. energy inequality $\frac{1}{2}\|u(t)\|_{L^2}^2 + \nu \int \|\nabla u\|^2 \le \frac{1}{2}\|u_0\|_{L^2}^2$).
  - `TEMPORARY_HYPOTHESIS`: Bounded working hypothesis under active test.
  - `ADDITIONAL_PROHIBITED`: Unearned higher regularity (e.g. $\|u\|_{L^\infty_t L^\infty_x} < \infty$, $\|\nabla u\|_{L^1_t L^\infty_x} < \infty$).
- **Circularity Detector**: Any proof step that implicitly or explicitly invokes an `ADDITIONAL_PROHIBITED` assumption to prove global regularity is immediately flagged as `CIRCULAR_FOR_GLOBAL_REGULARITY`.

### Mechanism 3: Claim Registry & Multidimensional Claim Passport
- Every lemma, theorem, no-go proposition, and structural identity is registered in `CLAIM_REGISTRY.yaml` with a 10-dimensional **Claim Passport**:
  1. `Truth Status`: `IDEA` $\to$ `HYPOTHESIS` $\to$ `CANDIDATE_LEMMA` $\to$ `PROVED_LEMMA` $\to$ `PROVED_THEOREM`.
  2. `Evidence Strength`: `E1` (self-report) to `E5` (externally anchored/tamper-resistant).
  3. `Independence Level`: `I1` (same session) $\to$ `I2` (different session/same model) $\to$ `I3` (distinct model) $\to$ `I4` (independent external agent/human).
  4. `Formalization State`: `NOT_FORMALIZED` $\to$ `PARTIALLY_FORMALIZED` $\to$ `FORMALLY_VERIFIED`.
  5. `Understanding Level`: `U0_NONE` $\to$ `U1_RAW_PROOF` $\to$ `U2_EXPERT_EXPLANATION` $\to$ `U3_COMPLETE_PACKAGE`.
  6. `Novelty Classification`: `N0_KNOWN` $\to$ `N1_PROJECT_REFORMULATION` $\to$ `N2_NOT_FOUND_IN_LITERATURE` $\to$ `N3_FUNDAMENTALLY_NOVEL`.
  7. `Significance Rating`: `S0_TECHNICAL_STEP` $\to$ `S1_USEFUL_LEMMA` $\to$ `S2_MAJOR_NO_GO_OR_INSIGHT` $\to$ `S3_PARADIGM_CLOSURE`.
  8. `External Validation`: `NOT_EXTERNALLY_REVIEWED` $\to$ `SPECIALIST_REVIEWED` $\to$ `PUBLIC_PREPRINT_SCRUTINIZED`.
  9. `Community Status`: `NOT_COMMUNITY_ACCEPTED` $\to$ `COMMUNITY_ACCEPTED`.
  10. `Project Status`: `CANDIDATE` $\to$ `PROJECT_CANONICAL_WITH_LIMITATIONS` $\to$ `PROJECT_CANONICAL` $\to$ `FIELD_CANONICAL`.

### Mechanism 4: Known Results Ledger
- Literature theorems (Leray 1934, Beale-Kato-Majda 1984, Constantin-Iyer 2008, Eyink 2009, Kato 1966) are cataloged in `KNOWN_RESULTS_LEDGER.yaml` with their exact hypotheses, failure modes, and relationship to current project targets.

### Mechanism 5: Claim Dependency Graph
- Machine-readable DAG in `CLAIM_DEPENDENCY_GRAPH.yaml`.
- No claim can be promoted to `PROJECT_CANONICAL` if any ancestor node in its proof dependency tree is unverified or circular.

### Mechanism 6: Proof Incident Registry & Mathematical Regression Rules
- Every discovered mathematical mistake, overclaim, or boundary violation is permanently recorded in `PROOF_INCIDENT_REGISTER.yaml`.
- Each incident generates an actionable invariant in `MATHEMATICAL_REGRESSION_RULES.yaml` accompanied by an automated regression test.

### Mechanism 7: Load-Bearing Result Registry
- Identifies in `LOAD_BEARING_RESULT_REGISTRY.yaml` the precise lemma, estimate, or identity that carries the core mathematical novelty and burden of an argument, preventing 100-page derivations from obscuring where the real mathematics lives.

### Mechanism 8: Correctness–Novelty–Significance Separation
- Reviews must strictly isolate proof validity (is it correct?) from novelty (was it known?) and significance (does it matter?). A mathematically flawless proof of a known fact is `CORRECT` but `N0_KNOWN`.

### Mechanism 9: Understanding Package Gate
- Every major canonical claim must provide a 3-layer **Understanding Package** registered in `UNDERSTANDING_REGISTER.yaml`:
  - **Level 1**: One-sentence core physical/geometric mechanism.
  - **Level 2**: One-page structural architecture and proof roadmap.
  - **Level 3**: Complete, rigorous line-by-line proof with explicit failure conditions and essential assumptions.

### Mechanism 10: Assumption Minimization Gate
- Once a theorem is proved, it enters `ASSUMPTION_MINIMIZATION_QUEUE.yaml` to test which hypotheses are genuinely essential versus artifacts of the proof technique.

### Mechanism 11: Alternative Proofs & Generalization Gate
- Canonical results enter `ALTERNATIVE_PROOF_QUEUE.yaml` and `GENERALIZATION_QUEUE.yaml` to discover alternate physical mechanisms and test broader geometric applicability.

### Mechanism 12: External Acceptance Ladder
- Formalizes the transition path from internal project truth to global mathematical canon:
  $$\text{PROJECT\_CANONICAL} \longrightarrow \text{SPECIALIST\_REVIEWED} \longrightarrow \text{PREPRINT\_SCRUTINIZED} \longrightarrow \text{COMMUNITY\_ACCEPTED} \longrightarrow \text{FIELD\_CANONICAL}.$$

---

## 4. Strict Claim Lifecycle State Machine

```text
IDEA
  │
  ▼
HYPOTHESIS
  │
  ▼
SUPPORTED_HYPOTHESIS (Empirical / Numerical / Asymptotic Evidence)
  │
  ▼
CANDIDATE_LEMMA / CANDIDATE_THEOREM
  │
  ▼
INTERNALLY_DERIVED (Complete Line-by-Line Analytical Proof)
  │
  ▼
E3_REPRODUCIBLE (Deterministic Machine Verification / Code Tests)
  │
  ▼
E4_INDEPENDENTLY_VERIFIED (Blind-First Independent E4 Proof Audit)
  │
  ▼
FORMALLY_VERIFIED (Optional: Lean / Computer-Assisted Verification)
  │
  ▼
HUMAN_UNDERSTOOD (Understanding Package Levels 1–3 Complete)
  │
  ▼
NOVELTY_CHECKED (Literature Priority Audit Completed)
  │
  ▼
PROJECT_CANONICAL (Sealed Internal Project Truth)
  │
  ▼
EXTERNAL_EXPERT_VALIDATED
  │
  ▼
COMMUNITY_ACCEPTED
  │
  ▼
FIELD_CANONICALIZED
```

**Prohibited Transitions**:
- Direct jumps such as `AI_GENERATED` $\to$ `PROJECT_CANONICAL` or `E3_REPRODUCIBLE` $\to$ `PROJECT_CANONICAL` (skipping independent E4 and understanding package) are strictly blocked.
