# MIGRATION & BOOTSTRAP PROTOCOL — v3.0.0

## 1. Purpose

Apply governance safely to:

- a new project;
- an existing project without governance;
- an existing project already governed by another system or earlier version.

The protocol is fail-closed and non-destructive: adoption cannot rewrite historical evidence or manufacture release readiness.

---

## 2. Phase 0 — Detect adoption mode

### DAY0
Use when implementation is new/empty enough that no material legacy truth must be preserved.

### MID_PROJECT_UNGOVERNED
Use when material implementation exists but there is no trustworthy formal governance/evidence system.

### MIGRATION_GOVERNED
Use when governance/rules/authority state/evidence/acceptance/release machinery already exists.

### AD_HOC
Use only when durable project state is unavailable.

Record the selected mode and evidence supporting it.

---

## 3. Universal first step — truth baseline

Before modifying governance or code inspect actual project state.

Record where applicable:

- repository/workspace identity;
- branch and exact HEAD/state hash;
- dirty-tree/workspace state;
- remotes;
- deployed/released state;
- architecture/components;
- dependencies/locks;
- tests actually runnable;
- CI/CD actually present;
- environments;
- high-risk domains;
- known defects/failures;
- existing release blockers;
- evidence stores/receipts;
- owner/action queues;
- agent/tool capabilities;
- secrets/sensitive-data concerns without exposing secrets.

Do not trust prose when executable/runtime evidence contradicts it.

---

# PATH A — DAY0 NEW PROJECT

## A1. Establish owner intent

Create `PROJECT_INTENT.md`.

Owner provides only product-level information needed to define:

- purpose;
- desired outcomes;
- supported scope;
- non-goals;
- unacceptable outcomes;
- business/spend/customer exposure boundaries;
- risk tolerance;
- legal/privacy decisions already known;
- reserved owner decisions.

Do not ask the owner to design tests, technical architecture or low-level KPIs unless they specifically want to.

## A2. Initialize governance state

Create `GOVERNANCE_STATE.yaml` from the template.

Set:

- `adoption_mode: DAY0`;
- `bootstrap.level: LIGHT` initially;
- standing mandate active after owner intent is confirmed.

## A3. Derive technical direction

Engineering may autonomously:

- propose/decide technical architecture inside owner boundaries;
- derive initial capability inventory;
- derive the technical roadmap/dependency graph;
- derive assurance contracts and technical acceptance tests.

Escalate only unresolved choices that materially alter owner-reserved domains.

## A4. Start bounded execution

Execute the next eligible objective under a Task Execution Envelope.

Upgrade bootstrap before crossing T3/T4/T5 ceilings.

---

# PATH B — MID_PROJECT_UNGOVERNED

## B1. Preserve reality before governance claims

Create a baseline snapshot/receipt before broad mutation.

Do not rename existing code `accepted` merely because governance has now been installed.

## B2. Recover direction

Where possible derive from actual product/code/docs and owner input:

- project intent;
- supported capabilities;
- architecture;
- current deployment reality;
- roadmap/pending work.

Owner confirms intent/business boundaries, not implementation correctness.

## B3. Legacy state classification

Classify consequential inherited capabilities as one of:

- `OBSERVED_ONLY`;
- `LEGACY_UNVERIFIED`;
- `PARTIALLY_CHARACTERIZED`;
- `VERIFIED_BY_RECOVERED_EVIDENCE`;
- `ACCEPTED_UNDER_CURRENT_GOVERNANCE`.

Recovered old tests may count as evidence only to the extent their candidate/environment/provenance can be established.

## B4. Risk-first retrofit

Do not retro-audit every line before continuing.

Prioritize by:

`CONSEQUENCE × CENTRALITY × CHANGE_FREQUENCY × UNCERTAINTY × RECOVERY_DIFFICULTY`.

Use touch-and-lift: when consequential legacy code is changed, establish/repair its contracts and verification proportionally.

## B5. Establish release truth

If no trustworthy release evidence exists:

`release.current_state = NOT_RELEASE_ELIGIBLE` or `UNKNOWN` according to actual evidence.

Do not infer readiness from production existence alone.

## B6. Continue autonomous work

Once baseline and intent are bound, execute eligible technical work under the standing mandate while retrofit debt remains tracked.

---

# PATH C — MIGRATION_GOVERNED

## C1. Freeze historical governance truth

Before edits identify and preserve:

- old governance version(s);
- manifests/hashes;
- state files;
- accepted checkpoints;
- release state;
- evidence receipts;
- negative evidence;
- owner-action lists;
- policy/authority rules;
- protected tests/evaluators;
- prior migration history.

Never edit sealed historical governance in place merely to align wording.

## C2. Authority semantic audit

Search for ambiguous concepts such as:

- `approved: true`;
- `owner approval required`;
- `human acceptance`;
- `acceptance_authority`;
- `release go`;
- `owner release sha`;
- `owner certifies tests`;
- roadmap/architecture decisions that unnecessarily require owner technical sign-off.

For each, determine what authority was actually intended:

- OWNER_INTENT;
- BUSINESS_POLICY;
- LEGAL_COMPLIANCE;
- IMPLEMENTATION;
- VERIFICATION;
- RELEASE_ELIGIBILITY;
- DEPLOYMENT_AUTHORITY.

Do not retroactively reinterpret historical records without recording the mapping.

## C3. Release-state preservation

A governance migration SHALL preserve the most conservative truthful release state.

If current state is NO-GO/BLOCKED/UNKNOWN, migration remains NO-GO/BLOCKED/UNKNOWN until missing technical evidence is actually produced.

Governance wording cannot promote the candidate.

## C4. Migrate standing mandate

Replace routine owner technical authorization with the standing autonomous development mandate while retaining explicit reserved boundaries.

Confirm:

- eligible technical work can continue without case-by-case owner certification;
- dependency/risk/security/spend rules still gate autonomy;
- reserved external actions remain blocked.

## C5. Migrate direction semantics

For architecture/roadmap rules:

- keep owner intent protected;
- allow engineering to derive technical architecture/sequence when scope remains unchanged;
- change owner approval requirements to reserved-boundary triggers rather than complexity triggers.

## C6. Migrate evidence semantics

Preserve prior evidence levels where meaningful, but add independent dimensions for:

- environment realism;
- independence;
- candidate identity.

Do not relabel an old simulated receipt as live evidence.

## C7. Migrate acceptance semantics

Replace generic acceptance with explicit states:

- implementation candidate;
- tested;
- reproduced;
- independently verified;
- technical acceptance;
- release eligibility;
- deployment authorization.

Historical generic approval records remain historical; map their known meaning rather than rewriting them.

## C8. Reclassify OWNER actions

Use `18_OWNER_ACTION_RECLASSIFICATION_TEMPLATE_v3.0.0.md`.

Technical derivable/automatable items move out of owner queue.

True business/legal/exposure/deployment items remain reserved.

## C9. Governance conformance test

Run `19_GOVERNANCE_CONFORMANCE_STANDARD_v3.0.0.md` before declaring migration accepted.

The governance change must not self-certify.

## C10. Checkpoint migration

Record:

- old governance identity;
- new governance identity;
- files changed;
- semantic mappings;
- contradictions unresolved;
- release state before/after;
- verification evidence;
- reviewer independence;
- exact migration candidate/checkpoint.

## C11. Continue project development

If the next technical objective is eligible and no reserved blocker exists, continue development immediately after migration acceptance.

Do not stop merely because governance migration completed.

---

# PATH D — AD_HOC

When there is no durable repository/workspace:

- state this limitation;
- keep binding/candidate/evidence in-session;
- use bounded envelopes;
- do not claim durable checkpoint integrity or remote evidence not available;
- do not imply that future sessions can safely resume without an exported checkpoint.

---

## 4. Migration acceptance criteria

A migration is accepted only when evidence shows:

1. owner technical certification is no longer required for ordinary dependency-satisfied technical work;
2. owner intent/business/legal/deployment boundaries remain protected;
3. autonomy cannot bypass dependencies;
4. autonomy cannot bypass risk/security/spend/tool constraints;
5. release remains fail-closed;
6. missing/stale evidence blocks stronger claims;
7. writers cannot self-certify independent verification;
8. candidate identity is machine-derived where practical;
9. tests on candidate A cannot authorize candidate B;
10. blocker types are explicit;
11. owner-action items are reclassified;
12. technical criteria can be derived from owner intent and independently challenged;
13. hard gates are separate from KPIs;
14. KPIs cannot override critical invariant failures;
15. negative evidence/history is preserved;
16. existing regression checks continue to pass or failures are explicitly recorded;
17. governance contradictions are resolved or openly tracked;
18. next technical objective can be derived from eligibility/dependencies without routine owner technical approval;
19. genuine reserved actions still stop safely;
20. current release state is not promoted without actual new evidence.
