# SOURCE OF TRUTH DESIGNATION

```
================================================================================
ADOPTION ID:                  NS_GOVERNANCE_V2_2_ADOPTION_001_R1
RECONCILIATION DATE:          2026-08-19
PRINCIPLE:                    Single Source of Truth (SSOT). Avoid duplicate 
                              independently editable records describing the 
                              same scientific or operational fact.
================================================================================
```

---

## 1. Domain Designation Table

| Area of Knowledge / State | Authoritative Source of Truth | Derived / Secondary View |
| :--- | :--- | :--- |
| **Scientific State & Epistemic Facts** | `CURRENT_SCIENTIFIC_STATE.md` | `walkthrough.md`, reports |
| **Scientific Hypothesis Status** | `HYPOTHESIS_REGISTRY.json` | `HYPOTHESIS_REGISTER.md` |
| **Falsified Universal Routes** | `PERMANENT_NO_GO_LEDGER.json` | `PROJECT_RECONCILIATION.md` |
| **Scientific Lineage & Reasoning** | `SCIENTIFIC_BRANCH_GRAPH.json` | `PROJECT_RECONCILIATION.md` |
| **Claim Epistemic Level** | `CLAIM_CLASSIFICATION_LEDGER.json` | `CURRENT_STATE_MATRIX.md` |
| **Physical Phenomena Catalog** | `BEHAVIORAL_PHENOMENA_REGISTRY.json` | `APPROACH_REGISTRY.md` |
| **Mechanism Interactions** | `MECHANISM_INTERACTION_MATRIX.json` | `CURRENT_SCIENTIFIC_STATE.md` |
| **External Literature Matches** | `EXTERNAL_MECHANISM_MATCHES.json` / Theorem Matrices | `RESEARCH_LEDGER.md` |
| **Repository & Codebase Health** | `PROJECT_STATE.md` | `PROJECT_PROFILE.md` |
| **Active Task Dependencies** | `TASK_GRAPH.md` | `NEXT_ACTION.md` |
| **Cryptographic Manifest Closures** | Sealed `*_CLEAN_MANIFEST.json` files | `VERIFICATION_CONTRACT.md` |
| **Governance Version & Adoption State** | `STATE_VERSION.md` | `CONTEXT_MANIFEST.md` |
