# GOVERNANCE OPERATOR GUIDE — v3.0.0

> Written for the human project owner/operator.

## 1. Your role under v3

You are not expected to certify code you cannot personally verify.

Your authority is primarily:

- what the product should do;
- why it should exist;
- supported scope/non-goals;
- business policy;
- budget/spend envelope;
- risk tolerance and unacceptable outcomes;
- customer/public exposure policy;
- legal/privacy decisions reserved to you/counsel;
- final deployment/exposure authorization where you choose to reserve it.

The technical system is responsible for deriving and proving:

- architecture inside those boundaries;
- technical contracts;
- tests;
- failure/recovery behavior;
- technical KPIs;
- independent verification;
- release eligibility.

If an AI asks you “Do you certify this implementation as correct?” the governance is being applied incorrectly.

## 2. What you should be asked

Good questions:

- “Is this capability part of the intended product?”
- “Is charging real customers allowed now?”
- “Which privacy/business policy do you want?”
- “May spending exceed the current €X envelope?”
- “Candidate X is already release-eligible; authorize deployment?”

Bad questions:

- “Do you approve these unit tests?”
- “Is this schema migration technically safe?”
- “Please provide/certify the Git SHA.”
- “Do you authorize this refactor as technically correct?”
- “Should p99 be 250 ms or 300 ms?” when engineering can derive a threshold from your user expectation.

## 3. Installing into a new project

1. Copy the packet into a governance folder or attach it to the active AI tool.
2. Use `01_UNIVERSAL_ACTIVATION_PROMPT_v3.0.0.md`.
3. Create `PROJECT_INTENT.md` using the template.
4. Confirm product intent and reserved boundaries.
5. Let the orchestrator derive architecture, capability map and initial roadmap.
6. The system begins in LIGHT mode and upgrades controls as risk increases.

You do not need to approve every technical increment.

## 4. Installing into an existing project with no governance

Use activation prompt and select `MID_PROJECT_UNGOVERNED`.

The first operation should be a read-only baseline snapshot, not a giant rewrite.

Expect the system to label some old behavior `LEGACY_UNVERIFIED`. That is not a condemnation; it means historical evidence is insufficient for a stronger claim.

New work becomes governed immediately. Legacy work is lifted progressively, especially when high-risk or touched.

## 5. Migrating an existing governed project

Use `MIGRATION_GOVERNED`.

The migration should:

- preserve old governance and hashes;
- preserve evidence/failures;
- identify contradictory states;
- replace ambiguous technical owner approvals with typed authority;
- keep true business/legal/exposure decisions reserved;
- keep release NO-GO if it was NO-GO;
- independently test the governance migration itself.

Do not delete old governance to make the repository look cleaner until the migration policy says archival/deletion is safe and provenance is preserved.

## 6. Files that normally live in the project

At minimum:

- `GOVERNANCE_STATE.yaml`
- `PROJECT_INTENT.md`
- `ARCHITECTURE_DECISIONS.md`
- `ROADMAP.md`
- `CAPABILITY_ASSURANCE_MATRIX.md` once consequential capabilities exist
- release/evidence/negative-evidence records when meaningful

Do not create dozens of empty files merely to satisfy governance aesthetics.

## 7. How the AI should operate day-to-day

The normal cycle is:

```text
re-bind project
→ inspect actual state
→ select next eligible objective
→ create bounded task envelope
→ implement
→ test normal + negative + failures/recovery where needed
→ independently verify where risk requires
→ record candidate-bound evidence
→ technically accept/reject
→ checkpoint/commit/push safely
→ update state
→ continue to next eligible objective
```

You should only be interrupted at a genuine owner/external boundary.

## 8. How release works

The system evaluates `RELEASE_ELIGIBLE` from hard gates and evidence.

If you reserve deployment authority, you receive a request similar to:

> Candidate abc123 is release-eligible for the stated production scope. All mandatory gates pass. Known limitation: X. Deploying will expose Y users / enable Z spend. Authorize deployment?

Your YES authorizes the exposure/deployment. It does not magically certify the code.

## 9. Interpreting evidence

A result should tell you three things:

1. **Strength** — observed, reproducible, independent, anchored?
2. **Environment** — mock, simulation, local live, staging, production observed?
3. **Independence** — writer self-check or truly separate verifier?

This prevents a signed simulated test from being mistaken for real production proof.

## 10. Interpreting “100% functioning”

The governance uses a scoped definition only:

> all declared supported capabilities passed their required assurance contracts in the declared verified environments with all release-blocking gates passing and no known unresolved blocking defect.

It does not claim universal perfection or zero unknown bugs.

## 11. Recommended placement

A practical repository layout:

```text
/governance/
  packet/                 # sealed v3.0.0 distribution or reference
  state/
    GOVERNANCE_STATE.yaml
  direction/
    PROJECT_INTENT.md
    ARCHITECTURE_DECISIONS.md
    ROADMAP.md
  assurance/
    CAPABILITY_ASSURANCE_MATRIX.md
    RELEASE_READINESS.md
  evidence/
    receipts/
    negative/
    verification/
```

If the project already has a governance folder/layout, adapt rather than duplicating unnecessarily.

## 12. Prompting different tools

The packet is tool-neutral. Common patterns:

- IDE/coding-agent rules file: runtime kernel as project/orchestrator instructions.
- Worker/subagent: micro-kernel + exact envelope.
- Plain chat: activation prompt + runtime kernel + current project files.
- API orchestrator: runtime kernel in system layer, envelope per task.
- Single-agent tool: use fresh-context review as IND1 fallback; do not claim strong independence.

The exact file name used by a product (AGENTS, rules, instructions, etc.) may vary; governance semantics do not.

## 13. Governance evolution

For future updates:

- never edit a sealed version in place;
- create a new version;
- write migration notes;
- regenerate manifest/index;
- migrate each project explicitly;
- retain prior receipts and release truth.
