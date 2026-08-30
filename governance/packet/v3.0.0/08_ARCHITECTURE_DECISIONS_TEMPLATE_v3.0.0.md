# ARCHITECTURE DECISIONS — TEMPLATE v3.0.0

> Architecture is primarily technical authority. Owner authority is required only when a technical choice materially changes an owner-reserved intent/business/legal/privacy/spend/exposure/risk boundary.

## Architecture snapshot

Record what is objectively observed in the actual project.

| Area | Observed current state | Evidence | Confidence |
|---|---|---|---|
| Runtime/stack | | | |
| Data/storage | | | |
| Auth/identity | | | |
| External integrations | | | |
| Deployment | | | |
| Test/CI | | | |
| Other | | | |

## Decision states

Use one of:

- `OBSERVED` — factual current architecture established by evidence.
- `DERIVED_TECHNICAL` — engineering decision derived inside accepted project boundaries.
- `DECIDED_TECHNICAL` — technically accepted decision with rationale/evidence.
- `OWNER_RESERVED_DECISION` — decision materially affects owner-reserved boundary and awaits/records that authority.
- `OPEN_TECHNICAL` — technical uncertainty not yet resolved.
- `SUPERSEDED` — historical decision replaced by a later one.

Do not mark an item `OWNER_RESERVED_DECISION` merely because it is complicated.

## Decision log

### ADR-XXXX — <title>

- State:
- Date:
- Problem:
- Intent/requirement trace:
- Options considered:
- Technical evidence:
- Risk tier:
- Affected contracts/capabilities:
- Decision:
- Why:
- Invariants:
- Consequences/trade-offs:
- Verification required:
- Rollback/migration path:
- Owner-reserved boundary affected? `YES | NO`
- If YES, authority type and receipt:
- Supersedes:

## Architecture change rule

A previously decided technical architecture item may be changed autonomously when:

- the change remains inside accepted owner intent and risk/business/legal boundaries;
- dependencies and affected contracts are identified;
- risk is reclassified;
- affected tests/evidence are rerun;
- the new decision is independently reviewed where consequence requires.

Owner approval is required only if the change itself alters a reserved owner domain.
