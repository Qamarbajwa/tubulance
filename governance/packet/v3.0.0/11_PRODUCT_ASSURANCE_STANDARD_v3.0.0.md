# PRODUCT ASSURANCE STANDARD — v3.0.0

## 1. Purpose

A product is not considered working merely because it compiles, starts, demonstrates one happy path, passes unit tests, or is reported complete by an AI/developer.

Every officially supported consequential capability must have an assurance contract proportional to its consequence.

The permanent chain is:

`Capability → Requirement → Assurance Contract → Tests → Evidence → Hard Gates/KPIs → Technical Acceptance → Release Eligibility`

## 2. Definition of Working

For each consequential capability define the applicable clauses below.

### Intent
What user/business outcome must exist?

### Valid input contract
What inputs, actors, states and versions are accepted?

### Invalid/adversarial input contract
What happens with malformed, missing, duplicate, stale, conflicting, unauthorized, oversized, corrupt or adversarial input?

### Preconditions
What must be true before execution?

### Transformation/process contract
What important rules govern processing?

### Invariants
What must never happen?

### Output contract
What externally observable result must occur?

### Postconditions
What state must hold after success?

### Failure contract
What happens on error, exception, timeout, dependency failure, interruption or partial completion?

### Retry/idempotency/concurrency contract
What happens on retry, replay, duplicate invocation, race or concurrent execution?

### Recovery/rollback contract
How does the system return to correct state after failure?

### Persistence/restart contract
What survives restart/reload/reconciliation?

### Security/authority contract
Which actor may perform which action on which resource under what authority?

### Performance/capacity contract
What measurable user/business expectation must be satisfied under declared workload?

### Compatibility/environment contract
Which versions/environments are supported and which require real-environment proof?

### Evidence requirement
What strength, environment and independence are required before acceptance?

## 3. Two assurance questions

For consequential capabilities answer separately:

### A. Implementation conformance
Does the implementation satisfy the technical contract?

### B. Intent fidelity
Does the contract itself faithfully represent accepted owner/product intent?

Independent reviewers should challenge both where risk warrants it.

## 4. Test families

Use only applicable categories, but explain what each proves and does not prove.

### Static
Types, lint, schemas, config, compilation, static security analysis.

Proves structural/static properties only; not runtime behavior.

### Unit
Isolated local logic.

Does not prove integration or real dependencies.

### Integration
Interactions among components/services/databases/APIs.

Does not automatically prove full user workflow or production environment.

### End-to-end
Complete workflows from initiating input to observable outcome.

Still limited to the environment and data actually exercised.

### Contract/interface
Schemas, protocol behavior, version compatibility and boundary semantics.

### Property-based
General invariants across generated inputs.

### Metamorphic
Expected relationships under transformed inputs where an exact oracle is difficult.

### Differential/independent oracle
Compare against trusted independent implementation/specification/calculation/reference dataset.

### Regression
Protect previously repaired behavior and important historical defects.

### Negative/malformed
Verify safe rejection/handling of invalid and hostile inputs.

### Boundary/edge
Zero/min/max/transitions/unusual states.

### Error/exception
Exercise explicit exception paths.

### Failure injection
Cause safe bounded dependency/network/resource/process/state failures and observe behavior.

### Recovery
Verify actual state correctness after recovery, not merely that an error was logged.

### State/data integrity
Detect silent loss, duplication, corruption, impossible states and transactional violations.

### Security/adversarial
Challenge auth, permissions, trust boundaries, injections, escalation, secrets, replay and abuse cases.

### Performance
Latency, throughput, resource use and user-visible responsiveness.

### Stress
Behavior beyond normal workload and controlled failure characteristics.

### Soak/endurance
Leaks, degradation, drift and resource accumulation over time.

### Compatibility
Declared OS/runtime/browser/host/provider/version matrix.

### Real-environment
Actual host application/device/service/environment when the support claim depends on it.

### User/workflow
Realistic user sequences, including interruption and recovery.

### Independent verification
Distinct reviewer/verifier or external evidence path.

## 5. Test-to-proof record

Each important test should answer:

1. What test is this?
2. Why does it exist?
3. Which capability/requirement does it examine?
4. What exact claim does PASS support?
5. What does PASS explicitly not prove?
6. What does FAIL imply?
7. Evidence strength?
8. Environment class?
9. Independence class?
10. Which hard gate/KPI does it affect?
11. Is failure release-blocking?
12. Exact candidate tested?
13. Can it be reproduced?

Test count and coverage percentages are secondary indicators, never technical truth by themselves.

## 6. Evidence hierarchy

Keep evidence dimensions independent.

### Strength
E1 narrative, E2 direct observation, E3 reproducible machine, E4 independent, E5 externally anchored.

### Environment
STATIC, ISOLATED, FIXTURE, MOCK, SIMULATED, INTEGRATED_LOCAL, LIVE_LOCAL, REPRESENTATIVE, STAGING, PRODUCTION_OBSERVED, EXTERNAL_SYSTEM.

### Independence
IND0 self, IND1 fresh/degraded, IND2 distinct reviewer, IND3 external/materially independent.

Never infer one axis from another.

## 7. KPI derivation

Do not invent vanity KPIs.

For each consequential failure mode:

`Failure → Consequence → Tolerance → Measurement → Threshold → Gate/KPI → Action`

Examples of likely hard gates:

- unauthorized financial mutation = 0;
- cross-tenant disclosure = 0;
- critical security escape = 0;
- silent critical data corruption = 0;
- unknown candidate identity = 0;
- missing required rollback proof = 0.

Examples of ordinary KPIs:

- p95 latency;
- task success rate;
- availability;
- provider error rate;
- queue depth;
- cost per successful operation;
- retry rate;
- user conversion/engagement;
- model-quality metrics.

KPIs cannot override hard-gate failures.

## 8. Bug-to-memory rule

Every confirmed material bug should become, where technically meaningful:

`Bug → Root cause → Minimal reproducer → Regression test → Repair → Verification → Memory`

Record:

- bug ID;
- capability;
- symptoms;
- root cause;
- severity;
- reproducer;
- repair;
- regression test;
- candidate/version;
- evidence;
- recurrence risk.

## 9. Severity

Generic default:

- **CRITICAL** — catastrophic/security/data/financial/core invalidation; release-blocking.
- **HIGH** — major supported capability broken/unreliable; normally release-blocking.
- **MEDIUM** — meaningful limited defect; explicit disposition required.
- **LOW** — minor consequence; may be accepted with rationale.

Projects may adapt severity names but must keep release consequences explicit.

## 10. Observability requirement

Where runtime truth matters, provide enough observability to diagnose:

- candidate/build identity;
- request/transaction identity;
- state transitions;
- dependencies;
- errors/exceptions;
- relevant timings/metrics;
- audit of consequential actions.

Do not log secrets/sensitive data unnecessarily.

## 11. Reproducibility

Acceptance-relevant evidence should identify where applicable:

- source revision;
- build/artifact hash;
- dependency versions;
- runtime/OS/host versions;
- configuration identity/class;
- dataset/input identity;
- command/tool invocation;
- expected vs actual outcome.

## 12. Meaning of 100% functioning

Only use this scope-bounded definition:

> 100% of the capabilities officially declared as supported for the candidate release have satisfied their required assurance contracts inside the explicitly verified scope and environments, all release-blocking gates pass, and no known unresolved release-blocking defect remains.

Never translate this into a universal bug-free guarantee.
