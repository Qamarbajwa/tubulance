# UNIVERSAL AUTONOMOUS PROJECT GOVERNANCE — v3.0.0

## Purpose

This packet is a project-neutral governance system for AI-assisted or autonomous development, research, engineering, data, integration, and tool-building work.

It is designed to work in four situations:

1. **DAY0** — a new project with little or no implementation.
2. **MID_PROJECT_UNGOVERNED** — an existing project with implementation but no formal governance.
3. **MIGRATION_GOVERNED** — an existing project already governed by another framework or an earlier version.
4. **AD_HOC** — a bounded session where durable repository state is unavailable.

The core design principle is:

> **The owner is the authority for intent and reserved business/risk decisions. Technical truth is established by contracts, tests, reproducible candidate-bound evidence, and independent verification where required.**

Owner confidence, developer confidence, AI confidence, test count, code coverage, or an aggregate KPI must never substitute for missing technical evidence.

---

## Governing model

```text
OWNER INTENT
    ↓
TECHNICAL REQUIREMENTS
    ↓
RISK + FAILURE MODEL
    ↓
CAPABILITY ASSURANCE CONTRACTS
    ↓
IMPLEMENTATION
    ↓
TESTING + CHALLENGE
    ↓
REPRODUCIBLE CANDIDATE-BOUND EVIDENCE
    ↓
INDEPENDENT VERIFICATION WHERE REQUIRED
    ↓
HARD GATES + KPI EVALUATION
    ↓
TECHNICAL ACCEPTANCE
    ↓
RELEASE ELIGIBILITY
    ↓
RESERVED DEPLOYMENT AUTHORIZATION WHERE REQUIRED
    ↓
DEPLOYMENT
    ↓
OBSERVATION + INCIDENT/REGRESSION MEMORY
```

---

## Non-substitutable authority domains

- **OWNER_INTENT_AUTHORITY** — what should exist, why, supported scope, unacceptable outcomes, non-goals.
- **BUSINESS_POLICY_AUTHORITY** — pricing, market/business policy, financial envelope, customer exposure policy, vendor/business choices.
- **LEGAL_COMPLIANCE_AUTHORITY** — decisions reserved to owner/counsel/compliance.
- **IMPLEMENTATION_AUTHORITY** — technical implementation inside accepted boundaries.
- **VERIFICATION_AUTHORITY** — technical conformance based on evidence.
- **RELEASE_ELIGIBILITY_AUTHORITY** — derives whether an exact candidate satisfies all release gates.
- **DEPLOYMENT_AUTHORITY** — authorizes an already eligible candidate to cross a reserved production/exposure boundary.

No authority may substitute for another.

---

## Core packet

| File | Purpose |
|---|---|
| `00_README_v3.0.0.md` | Packet map and design philosophy |
| `01_UNIVERSAL_ACTIVATION_PROMPT_v3.0.0.md` | First prompt to activate governance in any tool |
| `02_RUNTIME_GOVERNANCE_KERNEL_v3.0.0.md` | Always-loaded orchestrator law |
| `03_WORKER_MICRO_KERNEL_v3.0.0.md` | Minimal rules for workers/subagents |
| `04_GOVERNANCE_MODULE_LIBRARY_v3.0.0.md` | Task-activated domain controls |
| `05_TASK_EXECUTION_ENVELOPE_TEMPLATE_v3.0.0.md` | Per-task bounded execution contract |
| `05A_TASK_EXECUTION_ENVELOPE_SCHEMA_v3.0.0.json` | Machine-readable envelope validation |
| `06_GOVERNANCE_STATE_TEMPLATE_v3.0.0.yaml` | Durable project governance state |
| `06A_GOVERNANCE_STATE_SCHEMA_v3.0.0.json` | Machine-readable state validation |
| `07_PROJECT_INTENT_TEMPLATE_v3.0.0.md` | Owner intent and product boundary template |
| `08_ARCHITECTURE_DECISIONS_TEMPLATE_v3.0.0.md` | Evidence-aware technical decisions |
| `09_ROADMAP_TEMPLATE_v3.0.0.md` | Dependency + eligibility driven roadmap |
| `10_AUTHORITY_AND_ACTION_CLASSIFICATION_v3.0.0.md` | Typed authority and action classes |
| `11_PRODUCT_ASSURANCE_STANDARD_v3.0.0.md` | Definition of Working and testing/assurance rules |
| `12_CAPABILITY_ASSURANCE_MATRIX_TEMPLATE_v3.0.0.md` | Capability → tests → evidence → gates/KPIs |
| `13_EVIDENCE_RECEIPT_SCHEMA_v3.0.0.json` | Machine-readable evidence receipt schema |
| `14_RELEASE_ELIGIBILITY_STANDARD_v3.0.0.md` | Hard release gates, KPIs, and release state machine |
| `15_RELEASE_READINESS_TEMPLATE_v3.0.0.md` | Candidate release dossier template |
| `16_MIGRATION_AND_BOOTSTRAP_PROTOCOL_v3.0.0.md` | DAY0, ungoverned adoption, governed migration |
| `17_GOVERNANCE_MIGRATION_RECEIPT_TEMPLATE_v3.0.0.md` | Migration provenance and contradiction record |
| `18_OWNER_ACTION_RECLASSIFICATION_TEMPLATE_v3.0.0.md` | Reclassify legacy OWNER-* items |
| `19_GOVERNANCE_CONFORMANCE_STANDARD_v3.0.0.md` | Tests for the governance system itself |
| `20_OPERATOR_GUIDE_v3.0.0.md` | Human-owner deployment guide |
| `21_MASTER_MODULE_INDEX_v3.0.0.json` | Machine-readable module map |
| `22_SHA256_MANIFEST_v3.0.0.json` | Packet integrity hashes |
| `23_CHANGELOG_v3.0.0.md` | Major-version semantic change record |

A combined single-file edition is also generated for environments that cannot attach multiple files.

---

## Adoption modes

### DAY0 — new project

1. Establish `PROJECT_INTENT.md` with owner authority.
2. Create `GOVERNANCE_STATE.yaml` from the template.
3. Let engineering derive the initial technical architecture and roadmap inside the accepted intent/risk boundaries.
4. Owner input is required only where genuine intent/business/legal/risk choices remain unresolved.
5. Start with `bootstrap_level: LIGHT`; upgrade before T3+ work.

### MID_PROJECT_UNGOVERNED — existing project, no governance

1. Do **not** treat existing code as accepted merely because it exists.
2. Capture a truthful baseline: repo/state identity, tests, architecture, high-risk domains, current release/deployment reality, known defects, dirty work.
3. Mark inherited consequential behavior as `LEGACY_UNVERIFIED` until proportionally characterized/verified.
4. Govern all new work immediately.
5. Retrofit touched/high-risk legacy areas first; do not require an all-at-once retro-audit before any progress.

### MIGRATION_GOVERNED — existing governance

1. Preserve prior governance artifacts, manifests, evidence, failures, and accepted checkpoints.
2. Audit old authority semantics against v3.0.0.
3. Map ambiguous generic approvals into typed authority.
4. Do not rewrite history to make previous governance appear compliant.
5. Migrate in a bounded, reversible governance increment and verify the migration itself.
6. Existing release state remains fail-closed; governance migration cannot transform missing evidence into PASS.

### AD_HOC — no durable workspace

Use the runtime kernel + a minimal task envelope in one session. Keep candidate identity and state in the conversation. Do not claim durable governance continuity that does not exist.

---

## Risk tiers

- **T1** — trivial, non-behavioral, easily reversible.
- **T2** — low-risk internal change, contract-preserving and reversible.
- **T3** — material feature/shared semantic/cross-module behavior.
- **T4** — auth, permissions, sensitive data, money, migrations, infrastructure, signing, high blast radius.
- **T5** — destructive/irreversible/high-consequence security, finance, privilege, legal/safety-critical, critical recovery.

Risk controls are proportional. High risk does **not** mean the owner must technically certify the work; it means stronger technical verification and any genuinely reserved human authority must both be satisfied.

---

## Evidence model

Evidence has three independent dimensions.

### Strength

- **E1** — narrative/model self-report. Never acceptance evidence.
- **E2** — direct observation of actual artifacts/state.
- **E3** — reproducible machine evidence.
- **E4** — independent reviewer/verifier evidence.
- **E5** — externally anchored/tamper-resistant evidence.

### Environment

Examples:

`STATIC | ISOLATED | FIXTURE | MOCK | SIMULATED | INTEGRATED_LOCAL | LIVE_LOCAL | REPRESENTATIVE | STAGING | PRODUCTION_OBSERVED | EXTERNAL_SYSTEM`

### Independence

- **IND0** — same writer/self-check.
- **IND1** — fresh context but same model/actor family; degraded separation.
- **IND2** — distinct qualified reviewer/verifier in the same operating environment.
- **IND3** — materially independent external/CI/human/third-party verification path.

A strong receipt in one dimension does not silently upgrade another dimension.

Examples:

- E5 signed mock result is still a mock result.
- LIVE_LOCAL observation is not automatically independent.
- E4 review is not automatically production proof.

---

## “100% functioning” definition

Use only this defensible scope-bounded meaning:

> **100% of the capabilities officially declared as supported for the candidate release have satisfied their required assurance contracts in the explicitly declared environments, versions, configurations, workloads and operating scope; all required hard release gates pass; no known unresolved release-blocking defect remains; and no stronger claim is made than the evidence supports.**

This is not a claim of universal bug-free software.

---

## Versioning

v3.0.0 is intentionally a major governance version because it changes authority semantics from generic technical/human approval toward **typed authority + evidence-derived technical acceptance + separate release eligibility and deployment authorization**.

Do not edit a sealed packet in place. Supersede it with a new version and regenerate the manifest.
