# Evidence Compatibility Map — v3.0.0 / MRC to Universal Governance Minimal v4.0.3

This document defines the evidence taxonomy and compatibility rules under Universal Governance Minimal v4.0.3 in the `tubulance` repository.

## 1. Evidence Namespace Separation

Operational governance evidence and mathematical domain evidence use distinct, non-conflicting namespaces:

| Evidence Domain | Active Namespace | Standard / Schema | Independence Metric |
|---|---|---|---|
| **Operational Governance** | `E1`–`E5` | Universal Governance Minimal v4.0.3 (`EVIDENCE_AND_MIGRATION.md`) | `IND0`, `IND1`, `IND2`, `IND3` |
| **Mathematical Domain** | `MATH_E1`–`MATH_E5` | Mathematical Research Constitution v1.0.1 | `MATH_I1`, `MATH_I2`, `MATH_I3`, `MATH_I4` |
| **Historical Receipts** | `GOV_E1`–`GOV_E5`, `GOV_I1`–`GOV_I4` | Preserved historical records (v2.10.1 / v3.0.0) | Historical labels remain unchanged. |

---

## 2. Operational Evidence Dimensions (v4.0.3)

New operational governance evidence records under v4.0.3 must bind the following five dimensions:

1. **E1 (Static / Inspection):** Narrative inspection, manual diff review, static lint checks (assertion only; not machine verification).
2. **E2 (Automated Tests):** Deterministic machine execution passing all assertions (`pytest`).
3. **E3 (Candidate-Bound Execution):** Reproducible automated test run bound directly to the candidate Git commit SHA.
4. **E4 (Independent Verification):** Verification performed and recorded by an independent persona/agent (`IND1` fresh-context, `IND2` separate qualified verifier).
5. **E5 (Externally Anchored):** Published peer-reviewed citation, external benchmark archive, or formal machine-checked proof (e.g. Lean / Isabelle).

---

## 3. Mandatory Receipt Fields

Every formal evidence receipt must include:
- `schema_version`: `"4.0.3"`
- `evidence_id`: Unique identifier
- `task_id`: Bounded task execution envelope ID
- `candidate_id`: Exact Git commit SHA (e.g. `GIT_SHA:48ebabb...`)
- `candidate_identity_type`: `"GIT_SHA"`
- `dimension`: `E1` | `E2` | `E3` | `E4` | `E5`
- `environment`: `STATIC` | `FIXTURE` | `INTEGRATED_LOCAL` | `SANDBOX` | `REPRESENTATIVE`
- `independence`: `IND0` | `IND1` | `IND2` | `IND3`
- `producer`: Role, tool, and execution persona
- `action`: Specific evaluation performed
- `command_or_invocation`: Exact command line executed
- `exit_code`: Numeric exit code (0 for PASS)
- `result`: `"PASS"` | `"FAIL"`
- `claims_supported` / `claims_not_supported`: Explicit boundaries of claim support
- `hard_gate_ids`: Conformance gates verified
- `timestamp`: UTC timestamp

---

## 4. Stale Evidence & Candidate Invalidation Rules

- **Candidate Invalidation:** Any modification to files in the candidate scope invalidates all prior review and acceptance receipts.
- **No Evidence Promotion:** An E1 inspection or E2 local test cannot be promoted to E3 or E4 without rerun against the exact frozen candidate.
- **Fail-Closed Principle:** Missing, stale, or candidate-mismatched receipts prohibit milestone acceptance.
