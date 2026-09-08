# Authority and Evidence Compatibility Map — v3.0.0 to v4.0.3

Historical labels remain historical. This document records the operational semantics and compatibility crosswalk for Universal Governance Minimal v4.0.3 in the `tubulance` repository without rewriting historical Git receipts or acceptance decisions.

## 1. Governance Authority Mapping

| Legacy / v3.0.0 Concept | Meaning in tubulance | v4.0.3 Canonical Authority | Migration & Compatibility Rule |
|---|---|---|---|
| `acceptance_authority` | Autonomous governance acceptance of bounded increments | Section 4 `Acceptance Authority` | Does not imply mathematical truth or commercial release eligibility. |
| `standing_mandate` | Standing authorization for autonomous research | Section 2 & 13.6 `Standing Mandate` | Autonomous technical work permitted within envelope; no routine owner technical certification required. |
| `human_acceptance` / `owner_approval` | Historical review wording | `VERIFICATION_AUTHORITY` / `INDEPENDENT_REVIEW` | Owner approval cannot substitute for deterministic technical or mathematical proof. |
| `approved: true` | Prohibited generic boolean flag | Explicit state enum: `ACCEPTED_BOUNDED`, `SELF_CHECKED`, etc. | Generic untyped approval flags remain strictly prohibited. |
| `release GO` | Prohibited deployment flag | Section 12 `release.state: NO-GO` | Release state is strictly `NO-GO`; research repository only. |
| `Clay Statement B status` | Fundamental open scientific problem | Mathematical Research Constitution v1.0.1 | Strictly `UNRESOLVED`; no governance action can alter this invariant. |
| `three entry files` | Fragmented v3 packet | `GOVERNANCE.md` (HOW), `PROJECT_DIRECTION.md` (WHAT/WHY), `PROJECT_STATE.yaml` (LIVE STATE) | Single entry interface; narrow technical sources delegated without duplication. |

---

## 2. Risk Tier Mapping

| Legacy v3.0.0 Tier | v4.0.3 Risk Class | Typical Scope in tubulance | Verification Minimum |
|---|---|---|---|
| **T1** | **R0** | Comment formatting, whitespace, typo fixes | Targeted inspection / clean diff; self-checked. |
| **T2** | **R1** | Test additions, utility scripts, non-critical tooling | Full automated test suite execution (`pytest`). |
| **T3** | **R2** | Numerical solvers, persistence estimators, analytical derivations | Automated tests + candidate-bound execution trace. |
| **T4** | **R3** | Governance migrations, constitutional amendments, foundational lemmas | Candidate execution + independent verifier review (`IND1`/`MATH_I2`). |
| **T5** | **R3 + Reserved** | VCS force-push, history deletion, external credentials | Strictly prohibited for autonomous agents. |

---

## 3. Evidence Dimension Mapping

| v3.0.0 Evidence Level | v4.0.3 Evidence Dimension | Meaning in tubulance |
|---|---|---|
| `GOV_E1_MODEL_RAW` | E1 (Inspection) | Static inspection, model output trace (assertion only). |
| `GOV_E2_LOGGED_TRACE` | E2 (Automated Tests) | Deterministic test execution log (`pytest`). |
| `GOV_E3_REPRODUCIBLE` | E3 (Candidate Execution) | Machine-reproducible test run bound to candidate Git SHA. |
| `GOV_E4_INDEPENDENT_VERIFIER` | E4 (Independent Verification) | Verification performed by fresh-context reviewer (`IND1`/`IND2`, `MATH_I2`). |
| `GOV_E5_EXTERNAL_ANCHORED` | E5 (Externally Anchored) | Literature citation, external mathematical database, or community archive. |

*Rule:* Historical receipts retain their `GOV_E*` / `MATH_E*` identifiers. New v4.0.3 receipts adopt the versioned schema defined in `EVIDENCE_AND_MIGRATION.md`.
