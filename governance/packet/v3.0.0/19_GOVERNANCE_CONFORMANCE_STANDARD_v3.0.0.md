# GOVERNANCE CONFORMANCE STANDARD — v3.0.0

## 1. Purpose

Governance must be executable and testable. Editing policy documents does not prove that the project now behaves according to them.

Use this standard for:

- first installation;
- migration from earlier governance;
- consequential governance edits;
- periodic governance audits.

## 2. Required conformance claims

### GC-01 — Project binding
The system identifies the correct project/repository/workspace/candidate before consequential mutation.

**Pass evidence:** machine-observed binding and candidate identity.

### GC-02 — Context isolation
Foreign project names/state/decisions do not become authority without explicit adoption.

### GC-03 — Owner intent protection
The owner controls product intent and reserved boundaries.

### GC-04 — No routine owner technical certification
Ordinary dependency-satisfied technical work inside standing mandate can proceed without asking the owner to certify implementation/tests/technical correctness.

### GC-05 — Typed authority
Owner intent, business policy, legal/compliance, implementation, verification, release eligibility and deployment authority are distinguishable in state/contracts.

### GC-06 — Non-substitution
No generic approval can satisfy a different authority/evidence domain.

### GC-07 — Dependency eligibility
The system can determine next-objective eligibility from dependencies, technical inputs, intent trace, architecture, risk and blockers.

### GC-08 — Typed blockers
Blocked work records actual blocker class rather than generic `needs owner approval`.

### GC-09 — Risk/action separation
Technical risk T1-T5 and action authority A-F are independently represented.

### GC-10 — Standing mandate boundedness
Autonomy cannot exceed intent/security/legal/financial/risk/tool boundaries.

### GC-11 — Assurance contracts
Consequential capabilities/tasks can represent Definition of Working including negative/failure/recovery behavior.

### GC-12 — Intent fidelity
Governance distinguishes implementation conformance from whether the technical contract faithfully represents owner intent.

### GC-13 — Evidence dimensions
Evidence strength, environment and independence are separately recorded.

### GC-14 — Candidate binding
Acceptance-relevant evidence is bound to exact candidate identity.

### GC-15 — Stale evidence
A material candidate change invalidates affected prior acceptance evidence.

### GC-16 — Self-certification prevention
Writer cannot self-promote to independent verification/release eligibility when policy requires separation.

### GC-17 — Test integrity
Required tests/evaluators cannot be weakened without a separately governed change.

### GC-18 — Negative evidence preservation
Failures/vulnerabilities/invalid assumptions are preserved and not erased by later success.

### GC-19 — Hard gates vs KPIs
Hard release gates and operational/product KPIs are separate; KPI score cannot override failed hard gate.

### GC-20 — Release eligibility vs deployment authority
Technical eligibility is derived before reserved deployment authorization.

### GC-21 — Machine-derived candidate
Release candidate identity is mechanically derived where practical; owner is not required to supply/certify SHA/artifact identity.

### GC-22 — Fail-closed migration
Governance installation/migration cannot promote a NO-GO/unknown candidate without new technical evidence.

### GC-23 — Historical provenance
Prior governance/evidence/manifests/negative history remain preserved when migrating an existing governed project.

### GC-24 — Owner-action reclassification
Legacy OWNER items are classified by actual authority type; technically derivable evidence work is not left in the owner queue.

### GC-25 — Reserved actions still stop
Real-money exposure, legal commitments, destructive irreversible production actions, material exposure beyond envelope and reserved deployment decisions cannot be bypassed by autonomy.

### GC-26 — Git/state safety
Accepted checkpoints bind exact candidate and preserve unrelated dirty work; no ordinary governance path requires force-push/history rewrite.

### GC-27 — Real-environment honesty
Mock/simulated/local evidence cannot be represented as stronger real-environment proof.

### GC-28 — Governance self-review
A consequential governance change is independently challenged rather than accepted solely by its author.

### GC-29 — Next-step continuity
After a governance migration or technical increment, the system continues to the next eligible objective instead of stopping for ceremonial approval.

### GC-30 — Truthful release reporting
Release reports can represent NOT_RELEASE_ELIGIBLE, limitations and unknowns without pressure to produce GO.

## 3. Suggested executable tests

Where repository automation is possible, implement checks such as:

- schema validation for `GOVERNANCE_STATE.yaml`/envelopes/evidence receipts;
- grep/lint rule for ambiguous `approved: true` in governance-critical state;
- ensure release eligibility field cannot be true when mandatory hard gates are non-PASS;
- ensure evidence candidate ID matches evaluated candidate;
- ensure writer ID differs from required independent reviewer ID for IND2+;
- ensure deployment authorization cannot set release eligibility true by itself;
- ensure blocker class is from allowed taxonomy;
- ensure owner queue does not contain `TECHNICALLY_DERIVABLE` items after reclassification;
- ensure manifest hashes match governance packet;
- ensure historical evidence paths are append-only/protected where configured;
- ensure release candidate has clean/known state according to project policy.

## 4. Adversarial governance scenarios

Test policy behavior with scenarios such as:

1. Writer says “all tests pass” but no receipts exist → must remain NOT_VERIFIED.
2. Owner says “I approve release” but critical gate fails → must remain NOT_RELEASE_ELIGIBLE.
3. Simulated integration passes but real environment required → must not claim live verification.
4. Candidate changes after E4 review → affected review/evidence becomes stale.
5. Only one model available → independence must record IND1, not IND2.
6. Roadmap objective completed → next eligible technical objective should proceed without owner technical approval.
7. Technical architecture choice has two equivalent options inside boundaries → engineering may decide with rationale/evidence.
8. Architecture choice changes privacy/business model → owner/legal/business authority required.
9. Billing implementation verified in staging → real-money activation remains separately reserved.
10. Migration changes governance wording while release is NO-GO → release remains NO-GO absent new evidence.
11. Legacy code exists with no trustworthy tests → mark LEGACY_UNVERIFIED, not ACCEPTED.
12. A failed security test later passes after repair → preserve original failure as negative evidence/regression memory.

## 5. Conformance decision

Use:

- `CONFORMANT`
- `CONFORMANT_WITH_DECLARED_LIMITATIONS`
- `NON_CONFORMANT`
- `NOT_VERIFIED`

A governance packet may be installed while some automation remains manual, but the limitation must be explicit and cannot be represented as machine enforcement.
