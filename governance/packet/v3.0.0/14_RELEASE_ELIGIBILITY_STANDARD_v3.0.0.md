# RELEASE ELIGIBILITY STANDARD — v3.0.0

## 1. Principle

Release eligibility is a technical/evidence-derived state. Deployment authorization is a separate reserved action when project policy requires it.

The owner is never asked to certify technical correctness.

## 2. State model

Use the following conceptual progression where applicable:

```text
DEFINED
→ SPECIFIED
→ IMPLEMENTING
→ IMPLEMENTATION_CANDIDATE
→ TESTED
→ REPRODUCED
→ INDEPENDENTLY_VERIFIED
→ REAL_ENVIRONMENT_VERIFIED
→ RELEASE_ELIGIBLE
→ DEPLOYMENT_AUTHORIZED
→ DEPLOYED
→ OBSERVED
```

Not every capability needs every state. A project-level release candidate must satisfy all required states/gates for its declared scope.

## 3. Candidate identity gate

Before release evaluation establish the exact candidate using a machine-derived identity when possible:

- Git SHA/tree hash;
- build/artifact/container digest;
- dependency lock identity;
- migration/schema identity;
- configuration fingerprint/class;
- dataset/model identity where applicable.

If candidate identity is unknown or relevant evidence applies to another candidate:

`RELEASE_ELIGIBLE = FALSE`.

## 4. Scope gate

The candidate must declare:

- officially supported capabilities;
- explicitly unsupported/deferred capabilities;
- supported environments/versions;
- workload/capacity assumptions;
- known accepted limitations;
- required external dependencies.

No undeclared capability may be silently counted as verified.

## 5. Hard release gates

Projects must define candidate-specific gates. Generic examples:

- required capability assurance contracts pass;
- unresolved CRITICAL acceptance defects = 0;
- unresolved HIGH defects that project policy marks blocking = 0;
- critical security findings = 0;
- prohibited cross-tenant/resource isolation violations = 0;
- unauthorized financial mutations = 0 where applicable;
- critical adversarial escapes = 0 where applicable;
- blocking migration failures = 0;
- missing required rollback/recovery verification = 0;
- unknown candidate identity = 0;
- stale required evidence = 0;
- missing required independent verification = 0;
- missing required real-environment/staging proof = 0;
- governance/evidence integrity blockers = 0;
- required deployment package/build verification passes.

A failed mandatory gate means:

`NOT_RELEASE_ELIGIBLE`.

No KPI can compensate.

## 6. KPIs

Operational/product KPIs may include:

- latency percentiles;
- throughput;
- success rate;
- availability;
- retry/error rate;
- cost;
- queue depth;
- model quality;
- user/product metrics.

Each KPI records:

- failure mode/consequence it represents;
- measurement method;
- threshold/target;
- environment;
- release-blocking vs informational status;
- action if threshold is missed.

A KPI should become a hard gate if its violation represents an unacceptable invariant rather than a tunable quality target.

## 7. Evidence matrix for release

For every release-blocking claim record:

| Claim/Gate | Candidate | Strength | Environment | Independence | Receipt | State |
|---|---|---|---|---|---|---|
| | | | | | | |

A receipt must never be interpreted beyond its environment or independence scope.

## 8. Real-environment requirement

If a declared capability depends materially on a real host application, service, device, provider, runtime, network or deployment environment, mocks/simulations alone do not establish release eligibility for that real-environment claim.

Specify the minimum real-environment evidence required per capability/risk.

## 9. Independent verification

For T3 material acceptance and T4/T5 consequential claims, use independent verification proportional to risk.

If the available environment cannot provide required independence, retain the corresponding state as not independently verified rather than manufacturing independence.

## 10. Security/financial/legal separation

- Security correctness is technically verified.
- Business approval controls business policy/exposure.
- Legal/compliance approval controls reserved legal decisions.
- Real-money activation is a reserved exposure decision.
- Deployment authorization allows an already eligible candidate to deploy.

None substitutes for another.

## 11. Release decision output

Return one of:

- `NOT_RELEASE_ELIGIBLE`
- `RELEASE_ELIGIBLE_WITH_DECLARED_LIMITATIONS`
- `RELEASE_ELIGIBLE`

and separately:

- `DEPLOYMENT_AUTHORIZATION_NOT_REQUIRED`
- `DEPLOYMENT_AUTHORIZATION_REQUIRED`
- `DEPLOYMENT_AUTHORIZED`

## 12. Owner deployment request

Only after eligibility is established, use:

> Exact candidate `<ID>` is `RELEASE_ELIGIBLE` for `<scope/environments>`. Required hard gates: PASS. Known accepted limitations: `<...>`. Remaining technical blockers: none. Deployment would create `<customer/financial/public exposure>`. Do you authorize deployment within `<exposure envelope>`?

Never use:

> Do you approve/certify that the code is technically correct?

## 13. Post-deployment observation

After deployment:

- verify deployed candidate identity;
- observe critical hard-gate invariants and operational KPIs;
- capture incidents/regressions;
- compare actual vs expected;
- update regression memory and roadmap.

Deployment is not the end of technical truth; observed runtime evidence can invalidate earlier assumptions and force release rollback/reclassification.
