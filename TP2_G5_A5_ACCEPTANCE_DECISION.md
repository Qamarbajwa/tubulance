# TP2-G5-A5 — Acceptance Decision

## Governance and candidate

`STANDING_MANDATE = ACTIVE`
`RISK = T3`
`ACTION = B`
`CLAY_STATEMENT_B = UNRESOLVED`
`TP2-G5-A0..A4 = ACCEPTED_WITH_LIMITATIONS`

Scientific candidate: `GIT_SHA:a492a7854e5ecb7fd14f183463f6182acb6b3f5b` (final A5 implementation candidate).

## R1 provenance repair

`TP2-G5-A5-R1` preserves the scientific candidate above and identifies
`GIT_SHA:ad00e0c6421a62ced5537d495aaeb5fe94c8462e` as the existing
post-candidate acceptance/evidence checkpoint. The candidate-to-checkpoint
diff is restricted to A5 governance/evidence bookkeeping; the accepted A0-A5
scientific scope has `SCIENTIFIC_SCOPE_DIFF = NONE`. The current repository
HEAD is intentionally derived with `git rev-parse HEAD` rather than embedded
in a commit containing that value.

The authoritative complete pre-R1 test census is `176 passed`, executed with
the full relevant `python -m pytest` command against the committed
`ad00e0c6421a62ced5537d495aaeb5fe94c8462e` tree. The local workflow's
independence ceiling remains `IND1`; this is not external peer review and does
not establish `E4_PASS`.

The T3 risk tier belongs to the TP2-G5-A5 execution envelope; T4 is the
broader program risk ceiling recorded by governance.

## Scientific decision

`V3_IMPLEMENTATION_CONFORMANCE = ACCEPTED`
`V3_INTENT_FIDELITY = ACCEPTED`
`MRC_MATHEMATICAL_TRUTH = ACCEPTED_WITH_LIMITATIONS`
`MRC_NOVELTY = ACCEPTED_WITH_LIMITATIONS`
`MRC_SIGNIFICANCE = ACCEPTED_WITH_LIMITATIONS`
`PROJECT_SCIENTIFIC_STATUS = ACCEPTED_WITH_LIMITATIONS`

Outcome taxonomy: `BOTH_BRANCHES_REMAIN_OPEN`; `EVIDENCE_INSUFFICIENT_FOR_GLOBAL_EXCLUSION`; `N2_NOT_FOUND_IN_AUDITED_SOURCES` remains the novelty ceiling.

The whole G5 campaign is accepted as a coherent scale-critical diagnostic synthesis. The campaign does not prove global regularity, blow-up, bounded Xi, a BKM/Serrin continuation theorem, branch exclusion, isotropy, or direct transfer of the audited geometric criteria. Both stochastic-history branches remain open and `EVIDENCE_INSUFFICIENT_FOR_GLOBAL_EXCLUSION` is the final scientific limitation.

## Stop

TP2-G5-A5 is complete. No A6 or successor mathematical increment is executed by this acceptance.
