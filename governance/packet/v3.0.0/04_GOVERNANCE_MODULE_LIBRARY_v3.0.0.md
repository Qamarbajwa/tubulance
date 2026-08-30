# GOVERNANCE MODULE LIBRARY — v3.0.0

> Reference library. Activate only modules relevant to the current project/task. Do not create empty paperwork for irrelevant modules.

# MODULE CORE-PROJECT-BINDING — Project Identity & Context Isolation

Activate always.

- Bind exact project/workspace/repository/state source.
- Foreign-project context has no authority unless explicitly adopted.
- Verify current candidate/checkpoint before consequential work.
- Record adoption mode and governance version.
- On context loss, rebind from durable state.

# MODULE CORE-AUTHORITY — Typed Authority & Reserved Decisions

Activate always.

- Separate owner intent, business policy, legal/compliance, implementation, verification, release eligibility and deployment authority.
- Ban generic approval when meanings could be confused.
- High technical risk increases evidence requirements; it does not automatically make the owner a technical certifier.
- Reserved authority applies only to the consequential action/decision actually reserved.

# MODULE CORE-RISK — Risk & Action Classification

Activate always.

Classify technical risk T1-T5 and action class A-F independently.

Raise controls for blast radius, irreversibility, security/financial/data/legal consequence, uncertainty and recovery difficulty.

# MODULE CORE-DEPENDENCY — Eligibility Graph & Concurrency

Activate always for multi-step work.

- Maintain objective dependencies.
- Execute sequentially where dependency requires.
- Run independent tasks in parallel only when mutable scopes, state versions and integration order do not conflict.
- Establish synchronization barriers before shared-schema, auth, permission, release-candidate, financial-state or other project-wide transitions.

# MODULE CORE-EVIDENCE — Evidence, Candidate Identity & Provenance

Activate always.

- Bind evidence to exact candidate.
- Record strength, environment and independence separately.
- Preserve negative evidence.
- Stale evidence cannot authorize a changed candidate.
- Prefer reproducible commands/receipts over narrative claims.

# MODULE CORE-ASSURANCE — Capability Contracts & Definition of Working

Activate for consequential capabilities.

Define intent, inputs, invalid inputs, preconditions, transformations, invariants, outputs, postconditions, failure/recovery, persistence, security, performance and required environments.

Map capability → tests → evidence → gates/KPIs → technical acceptance.

# MODULE CORE-TEST-INTEGRITY — Test/Evaluator Protection

Activate whenever tests/gates/evaluators change.

- Do not weaken required tests to pass.
- Treat changes to verifier-owned checks as consequential.
- Preserve independent oracles where practical.
- Review test intent as well as implementation.

# MODULE CORE-GIT-STATE — Source Control & Checkpoints

Activate when Git/VCS/state manifests exist.

- Preserve unrelated dirty work.
- Small reversible checkpoints.
- No force-push/history rewrite without explicit exceptional authority.
- Bind evidence to accepted SHA/hash.
- Verify remote identity after safe push when policy permits.

# MODULE SECURITY — Security & Threat Model

Activate when confidentiality, integrity, authentication, authorization, secrets, external input, network exposure or privileged operations are material.

Minimum considerations:

- threat actors and trust boundaries;
- authentication and authorization;
- least privilege;
- tenant/resource isolation;
- injection and malicious input;
- secret handling;
- unsafe deserialization/path traversal/file access;
- privilege escalation;
- replay/idempotency where relevant;
- dependency/supply-chain risk;
- logging/audit without secret leakage;
- secure failure defaults;
- security regression tests;
- adversarial challenge.

Zero-tolerance invariants should become hard gates.

# MODULE PRIVACY-DATA — Privacy, Sensitive Data & Data Governance

Activate when personal, confidential, regulated or high-value data is processed.

Define:

- data classes and provenance;
- collection purpose;
- minimization;
- access/retention/deletion;
- encryption and secret/key boundaries;
- residency requirements where applicable;
- logging/redaction;
- backup/restore;
- export/import;
- consent/policy requirements reserved to owner/legal;
- data-integrity invariants.

Technical implementation does not manufacture legal/compliance authority.

# MODULE AUTHZ-IDENTITY — Identity, Tenant, Principal & Permission Systems

Activate for auth/tenant/principal/role/permission work.

Verify:

- deterministic identity/ownership;
- authorization consistency;
- least privilege;
- tenant/resource isolation;
- stale/deleted/duplicate identity behavior;
- privilege transition/revocation;
- session/token lifecycle;
- migration/reconciliation;
- no unauthorized orphaning;
- denial behavior and auditability.

# MODULE FINANCIAL — Billing, Money & Financial State

Activate for payments, billing, credits, quotas with financial effect, subscriptions, invoicing or real-money providers.

Separate:

- business pricing/policy authority;
- technical billing correctness;
- real-money activation authority.

Verify as applicable:

- unauthorized financial mutation = 0;
- cross-account/tenant mutation = 0;
- duplicate charge from retry/replay = 0;
- idempotency;
- ledger/state reconciliation;
- partial failure;
- provider mismatch;
- refund/rollback/forward recovery;
- audit/provenance;
- spend limits and kill switches.

Real-money activation requires Class E/F authority as project policy defines.

# MODULE MIGRATION — Schema/Data/State Migration

Activate for database/schema/state/model-format migrations.

Require:

- source/target version identity;
- preconditions;
- dry-run/rehearsal where practical;
- forward migration test;
- backward compatibility window or explicit break decision;
- rollback/forward recovery;
- data integrity counts/checksums/invariants;
- stale clients/workers behavior;
- backup/restore proof where consequential;
- exact migration hash/version;
- post-migration verification.

# MODULE INTEGRATION — External APIs, Providers, Webhooks & Protocols

Activate for external services/protocol boundaries.

Define:

- request/response contracts;
- authentication/provider identity;
- timeouts/retries/backoff;
- rate limits;
- malformed/partial/out-of-order responses;
- idempotency/replay;
- version compatibility;
- provider outage/degraded mode;
- observability;
- reconciliation;
- real-provider verification where the supported claim requires it.

# MODULE DISTRIBUTED — Queues, Events, Concurrency & Distributed State

Activate for async/event/queue/concurrent/distributed systems.

Define:

- delivery semantics;
- ordering;
- duplication;
- idempotency;
- retries/dead-letter handling;
- poison messages;
- concurrency limits;
- race conditions;
- leases/locks;
- partition/outage behavior;
- eventual consistency expectations;
- reconciliation and observability.

# MODULE INFRASTRUCTURE — Infrastructure, Configuration & Deployment Topology

Activate for cloud/on-prem/local infrastructure or runtime configuration changes.

Define:

- desired vs actual state;
- environments;
- infrastructure as code where practical;
- config/secrets separation;
- drift detection;
- deployment topology;
- capacity assumptions;
- rollback/replacement strategy;
- backup/recovery;
- cost envelope;
- region/residency where relevant.

Manual production changes must be recorded and reconciled back to declarative truth.

# MODULE RELEASE — Build, Packaging, Signing & Distribution

Activate for release candidates and distribution.

Verify:

- exact candidate identity;
- reproducible build/package where practical;
- dependency lock state;
- signing/notarization as required;
- version compatibility;
- installer/update/uninstall behavior;
- rollback;
- release notes/known limitations;
- environment-specific configuration;
- staged rollout/canary when appropriate.

Technical release eligibility is separate from reserved deployment/publication authority.

# MODULE PERFORMANCE — Performance, Capacity, Stress & Soak

Activate when performance matters to supported behavior.

Derive technical thresholds from owner/business expectations and failure consequences.

Measure applicable:

- p50/p95/p99 latency;
- throughput;
- concurrency;
- CPU/memory/GPU/disk/network;
- queue depth;
- error/retry rate;
- headroom;
- degradation behavior;
- breaking point;
- long-duration leaks/drift.

Performance KPIs cannot override correctness/security gates.

# MODULE RESILIENCE — Failure Injection, Recovery & Disaster Recovery

Activate for stateful, external-dependency or availability-critical systems.

Exercise applicable:

- timeout;
- dependency unavailable;
- partial response;
- process crash;
- restart;
- disk/network failure;
- corrupt/stale state;
- duplicate/out-of-order event;
- resource exhaustion;
- backup restore;
- rollback/forward recovery;
- failover.

Verify post-recovery state, not merely error detection.

# MODULE OBSERVABILITY — Logs, Metrics, Traces & Audit

Activate for consequential/runtime systems.

Provide enough observability to establish what actually happened:

- structured logs;
- request/transaction/correlation identity;
- timestamps;
- state transitions;
- failure context;
- dependency status;
- metrics/traces where justified;
- audit events for consequential actions;
- candidate/build/version identity.

Do not log secrets/sensitive data unnecessarily.

# MODULE INCIDENT — Incident & Break-Glass Governance

Activate for production incidents or emergency change paths.

Break-glass is pre-authorized degraded governance, not automatic privilege escalation.

Require:

- verified incident trigger;
- actor already has emergency authority;
- smallest credible containment action;
- pre-change state where possible;
- rollback/containment path;
- audit record;
- post-incident retrospective and normal-governance re-verification.

Emergency mode must not be used to bypass ordinary release governance for convenience.

# MODULE UI-UX — UI, Accessibility & User Workflow

Activate for user-facing interfaces.

Verify:

- core workflows end-to-end;
- state transitions/loading/empty/error states;
- keyboard/accessibility requirements where applicable;
- responsive/viewport/device requirements;
- localization where supported;
- authorization consistency between UI and backend;
- no false success indicators;
- recovery from user mistakes;
- cross-route/page consistency.

Screenshots prove appearance only, not underlying behavior.

# MODULE DESKTOP-LOCAL — Desktop, Plugin & Local Application Behavior

Activate for desktop/local apps/plugins.

Consider:

- supported OS/application versions;
- installation/registration;
- local permissions;
- file/path behavior;
- inter-process communication;
- lifecycle start/stop/restart;
- offline/degraded behavior;
- update/rollback;
- local security boundary;
- real-host-application verification.

# MODULE MOBILE — Mobile Lifecycle & Store Distribution

Activate for mobile apps.

Consider:

- lifecycle/background/termination;
- offline/sync;
- permissions;
- device/OS matrix;
- signing/store requirements;
- push/deep links;
- secure local storage;
- network transitions;
- update compatibility;
- accessibility.

# MODULE AI-AUTONOMY — AI Agents, Models & Autonomous Workflows

Activate when AI/model/agent output causes decisions/actions.

Verify applicable:

- prompt/input injection resistance;
- fabricated state/tool result handling;
- tool authorization;
- capability/resource/tenant boundaries;
- spend/concurrency/execution limits;
- retries/loops;
- stale context;
- provider/model failure;
- fallback behavior;
- provenance of model/provider/config;
- quality evaluation on held-out/adversarial cases;
- false-success prevention;
- human/reserved escalation triggers;
- action auditability.

Agents may not grant themselves authority.

# MODULE ML-EVALUATION — ML/Data Model Evaluation

Activate for trained/statistical ML systems.

Minimum:

- data identity/provenance;
- train/validation/test separation;
- leakage checks;
- model/config identity;
- reproducible metrics;
- baseline comparison.

For material deployment add applicable robustness, calibration, bias/fairness, safety, privacy/security, drift monitoring and rollback.

One benchmark improvement is not universal superiority.

# MODULE RESEARCH-SCIENTIFIC — Research, Mathematics & Scientific Computation

Activate for research/scientific claims.

Preserve:

- problem identity;
- assumptions;
- pathway/hypothesis identity;
- negative evidence;
- datasets/parameters/seeds;
- numerical precision/units;
- baselines/controls;
- reproducibility;
- literature/provenance where applicable;
- theorem/dependency audit for proof-like work;
- distinction between computational evidence and proof.

Use falsifiable interrogation when mechanism is uncertain:

`IDENTIFY UNKNOWN → ISOLATE → BASELINE → HYPOTHESIS → PREDICT → PERTURB → OBSERVE → COMPARE → REFINE → REINTEGRATE → REGRESSION`.

# MODULE ARTIFACT-DATA — Data Pipelines, Generated Artifacts & Documents

Activate for generated datasets/reports/files/models.

Track:

- source identity;
- transformation steps;
- schema/format;
- validation;
- lineage;
- output hash/version;
- deterministic/reproducible generation where practical;
- manual edits;
- compatibility;
- corrupt/partial input behavior.

# MODULE SUPPLY-CHAIN — Dependencies & Third-Party Supply Chain

Activate for material dependency changes.

Check:

- exact versions/locks;
- provenance;
- license/policy where applicable;
- known security issues;
- transitive effects;
- API/behavioral compatibility;
- update/rollback plan;
- build reproducibility.

# MODULE COMPATIBILITY — Version & Environment Compatibility

Activate when multiple versions/environments are declared supported.

Maintain explicit supported matrix for relevant:

- OS;
- runtimes;
- browsers;
- host applications;
- database versions;
- providers;
- schemas/protocols;
- devices;
- plugins/extensions.

Do not infer untested compatibility from similarity.

# MODULE COST-RESOURCE — Resource, Spend & Budget Governance

Activate when API/cloud/compute/resource cost is material.

Separate owner/business spend envelope from engineering optimization.

Track:

- approved envelope;
- expected/actual cost;
- per-operation cost where useful;
- anomaly/overrun behavior;
- quotas/kill switches;
- retry amplification;
- model/provider routing;
- cost-performance trade-offs.

Exceeding the authorized envelope is a reserved authority boundary.

# MODULE LEGACY-RETROFIT — Existing Project Retrofit

Activate for mid-project adoption.

- Preserve baseline.
- Do not mark legacy code accepted without evidence.
- Characterize before refactor.
- Prioritize retrofit by risk, blast radius, centrality, uncertainty and change frequency.
- Use touch-and-lift: when consequential legacy code is changed, lift its contract/evidence proportionally.
- Track `LEGACY_UNVERIFIED` explicitly.

# MODULE GOVERNANCE-MIGRATION — Governance Evolution & Supersession

Activate when changing governance.

- Old governance files/manifests/evidence remain historical truth.
- Create explicit supersession/migration receipt.
- Map semantic changes.
- Preserve release blockers and negative evidence.
- Validate new governance against conformance tests.
- Governance cannot self-certify its own migration.
- Do not modify sealed historical governance in place.

# MODULE RELEASE-OBSERVATION — Post-Deployment Observation & Learning

Activate after deployment.

- Verify actual deployed candidate identity.
- Observe health, errors, performance and critical business/safety invariants.
- Compare expected vs actual.
- Record incidents/regressions.
- Feed findings into regression memory and roadmap.
- Deployment success is not established until the deployed state is actually observed.
