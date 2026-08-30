# ROADMAP / EXECUTABLE ELIGIBILITY GRAPH — TEMPLATE v3.0.0

> The roadmap is a dependency-aware technical execution graph derived from accepted intent. The owner sets product direction; engineering may autonomously decompose, reorder and refine technical objectives when scope and reserved boundaries are unchanged.

## Objective states

`PROPOSED | READY | ACTIVE | CANDIDATE | VERIFIED | ACCEPTED | BLOCKED | DEFERRED | SUPERSEDED`

## Eligibility rule

An objective can become READY only when:

- dependencies are accepted/satisfied;
- required technical inputs exist;
- it traces to accepted intent;
- architecture permits it;
- risk/action remain within authorized envelope;
- candidate/project state is known;
- no blocking invariant exists;
- the technical mutation itself does not require a reserved owner/external action.

A downstream deployment/exposure step may remain separately blocked even while the technical implementation is eligible.

## Objectives

### OBJ-XXXX — <title>

- Status:
- Intent trace:
- Objective:
- User/business outcome served:
- Dependencies:
- Affected capabilities:
- Expected risk tier:
- Expected action class:
- Done when:
- Required evidence:
- Required real environment:
- Hard gates affected:
- Reserved-authority trigger, if any:
- Current blocker class:
- Current blocker detail:
- Candidate/checkpoint:
- Evidence refs:
- Notes:

## Autonomous roadmap maintenance

The orchestrator may autonomously:

- split an objective into smaller dependency-correct increments;
- reorder objectives when evidence/dependencies justify it;
- add technically necessary prerequisite/repair/verification objectives that clearly trace to accepted intent;
- add regression/assurance work revealed by defects;
- mark technical objectives blocked/unblocked from evidence.

Owner input is required only if roadmap alternatives materially alter product intent, business policy, legal/privacy posture, approved spend/exposure, or another reserved boundary.

## Parked/non-goal work

- 
