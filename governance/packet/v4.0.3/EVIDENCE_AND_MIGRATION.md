# Delegated evidence and migration contract

This is a technical companion to GOVERNANCE.md sections 8-11, not a fourth operational authority. Read when binding receipts, validators or a migration; do not load it for every trivial edit.

## Evidence dimensions and compatibility

The v4.0.3 scale retains v4.0.1 meanings: E1 static/inspection, E2 automated tests, E3 candidate-bound execution, E4 independent verification, E5 externally anchored evidence. Self-report alone is ASSERTION, not verification. Level is not sufficient: always specify scope, environment, independence, method and result.

Legacy v3.1: E1 narrative/self-report, E2 direct observation, E3 reproducible machine evidence, E4 independent verification, E5 anchored. Preserve original labels and `scheme_version`. A v3.1 E2 observation does not automatically become a v4 E2 automated test. Derive any new classification from the actual evidence, never numerical equivalence. Retain old risk tier and rationale; map T1-T5 to R0-R3 by consequence, not an automatic lookup that lowers protection.

Independence: IND0 writer/same context; IND1 limited fresh-context separation; IND2 distinct qualified verifier; IND3 materially independent external verification. Names, separate task IDs and self-attestation alone do not prove qualification. Actual verifier capability/provenance must be available or marked NOT_VERIFIED.

Environments: STATIC, MOCK, FIXTURE, ISOLATED_SYNTHETIC, INTEGRATED_LOCAL, REPRESENTATIVE, SANDBOX, STAGING, PRODUCTION_OBSERVED. Record dataset origin and allowed effects as well as URL/build/configuration class. Never store credentials.

## Required receipt fields

A receipt contains: unique id; scheme_version; contract/capability and exact scope; candidate digest algorithm plus ordered path list/manifest ref; relevant dependency/config/environment identity; command/tool and method; UTC timestamp; result/exit code where meaningful; producer role/task; independence and provenance limits; artifact reference plus digest; claim and limitations. Use null/UNKNOWN honestly; missing required values prohibit acceptance.

Reviews add writer identity, reviewer identity, observed candidate, reproduced evidence IDs, mutation constraints, findings, verdict and remaining deviations. Acceptances add acceptor identity, matching candidate, matching PASS review ID, independently reproduced critical receipts, exact bounded outcome and unchanged release boundary. Append corrections and supersession; do not rewrite a failed receipt.

Scope fingerprint convention: SHA-256 of each ordered UTF-8 repository-relative path, NUL, raw file bytes, NUL. Bind the path order explicitly. Capture relevant out-of-scope dependencies/build configuration separately; a small scope digest does not bind the entire app. Absence/deletion needs an explicit tombstone manifest record rather than hashing an empty file. Never include secret material or secret hashes.

## Project validator obligations

Bind the project's real schema/validator implementation by path and version. It must reject missing/dangling receipts, unknown schemes, malformed digest/path scope, invalid statuses, stale candidate/environment, review FAIL or missing PASS, writer-as-acceptor, unmet dependencies, stale state revision, unknown required hard gates and release promotion without all required gates. Preserve earlier failures. Validate paths safely inside the declared evidence roots; do not follow arbitrary evidence URLs or run commands embedded in receipts.

Test deliberate negative cases, not just valid fixtures. A shape checker cannot prove reviewer independence, truthful execution, permission or visual fidelity; qualified verification must challenge those separately. The included tools/verify-package.mjs is only a distribution checker, NOT this project validator.

## Migration acceptance record

Record source package hash; old active binding; exact owned preimages; new candidate scope/fingerprint; source-to-project adaptations; retained stronger restrictions; direction/source delegation map; old-to-new status/risk/evidence mapping; current-candidate and failure-history continuity; required tests and results; review and acceptance IDs; cutover steps; observed post-cutover identity; recovery procedure and verification.

Before cutover re-read both project state revision and owned file hashes under serialization. Mismatch blocks writes. Keep acceptance metadata outside the frozen source fingerprint to avoid a circular self-hash. Any source change after PASS needs affected re-review. Mark cutover POSTCHECK_FAILED if consumer binding diverges; recover or correct within authority, never declare ACTIVE just because files exist.

## Minimal state-transition tests required in each adopting project

1. UNBOUND template cannot activate or authorize product work.
2. Existing failed/unknown gates and NO-GO survive migration.
3. Candidate A review cannot accept candidate B.
4. A missing/failed review and writer self-acceptance are rejected.
5. Concurrent stale state update cannot overwrite a newer revision.
6. A UI fixture cannot certify an ordinary persisted or production journey.
7. Required delegated specs remain reachable and historical instructions are inactive.
8. Recovery preserves unrelated dirty files and sealed historical hashes.
9. Autonomous next selection respects dependencies, owner priority and reserved actions.
10. Migration acceptance grants neither product acceptance nor deployment permission.
11. A required responsive, accessibility, role/surface or failure-state dimension without matching evidence prevents UI capability completion even if its backend and success screen pass.
12. A shared receipt verifies only the explicitly mapped dimensions and candidate/environment it actually covers; a test-directory path cannot certify every UI state.
