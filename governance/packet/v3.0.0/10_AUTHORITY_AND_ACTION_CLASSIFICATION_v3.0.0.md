# AUTHORITY & ACTION CLASSIFICATION — v3.0.0

## 1. Purpose

Prevent generic approval from conflating product intent, technical correctness, business/legal authority, release eligibility and deployment authorization.

## 2. Authority domains

### OWNER_INTENT_AUTHORITY
May decide:
- product purpose;
- supported outcomes/scope;
- non-goals;
- unacceptable product outcomes;
- material product-direction changes;
- business-level quality priorities.

Does not prove implementation correctness.

### BUSINESS_POLICY_AUTHORITY
May decide:
- pricing/business rules;
- approved spend envelope;
- customer exposure policy;
- marketplace/vendor preference where technically equivalent;
- commercial operating boundaries.

Does not prove technical safety/correctness.

### LEGAL_COMPLIANCE_AUTHORITY
Reserved for owner/counsel/compliance where applicable.

Engineering may implement requirements and surface risks, but cannot manufacture legal conclusions or consent.

### IMPLEMENTATION_AUTHORITY
Controls technical implementation choices inside accepted boundaries.

Default: autonomous within a valid task envelope and standing mandate.

### VERIFICATION_AUTHORITY
Evaluates whether the exact candidate satisfies the technical contract using required evidence.

Must remain sufficiently independent according to risk.

### RELEASE_ELIGIBILITY_AUTHORITY
A machine-/evidence-governed gate that derives whether the exact candidate satisfies all required release conditions.

It cannot be overridden by confidence or generic approval.

### DEPLOYMENT_AUTHORITY
Where reserved, authorizes an already release-eligible candidate to cross the production/customer/financial/publication boundary.

It does not certify technical correctness.

## 3. Non-substitution table

| State/authority | Does NOT imply |
|---|---|
| OWNER_INTENT_CONFIRMED | implementation works |
| BUSINESS_POLICY_APPROVED | security/billing correctness |
| IMPLEMENTATION_CANDIDATE_COMPLETE | tested/verified |
| TESTED | reproduced/independently verified |
| INDEPENDENTLY_VERIFIED | release eligible |
| RELEASE_ELIGIBLE | deployment authorized |
| DEPLOYMENT_AUTHORIZED | missing technical evidence is waived |

## 4. Action classes

### CLASS A — Read-only/local analysis
Examples:
- inspect code/docs/state;
- run read-only diagnostics;
- research;
- review evidence.

Default: autonomous.

### CLASS B — Reversible internal development mutation
Examples:
- code change on working branch;
- test addition;
- internal refactor;
- non-production config change.

Default: autonomous inside task envelope after proportional verification.

### CLASS C — Bounded external/provider interaction
Examples:
- sandbox API call;
- pre-approved cloud/model usage;
- non-public staging interaction.

Autonomous only inside approved spend/privacy/risk envelope.

### CLASS D — Externally visible/customer-facing action within pre-approved policy
Examples:
- publish to a pre-approved test cohort;
- update non-sensitive public content under established publication policy.

Allowed only when prerequisites are satisfied and project policy pre-authorizes it.

### CLASS E — Real-money/material exposure
Examples:
- enabling production billing;
- initiating spend beyond ordinary bounded engineering usage;
- material new customer exposure.

Requires explicit owner/business authority for the exposure. Technical readiness must be independently established first.

### CLASS F — Legal/destructive/irreversible/high-consequence
Examples:
- destructive production data action;
- legal commitment;
- irreversible migration without accepted recovery path;
- security-sensitive privilege action beyond approved envelope.

Requires explicit reserved human authority and strongest practical technical evidence.

## 5. Risk tier vs action class

Risk and authority are independent.

Examples:

- T4/B: a local security-sensitive authorization refactor. High technical risk, but no owner approval is needed merely to implement/test it.
- T2/E: a simple toggle that activates real billing. Low code complexity, but explicit business/exposure authority is required.
- T5/F: irreversible production migration. Strongest technical evidence plus reserved human authority.

## 6. Reserved-authority trigger rule

Do not escalate the entire technical task merely because a later step is reserved.

Example:

`IMPLEMENT BILLING SAFELY` may proceed autonomously through local/staging verification.

`ACTIVATE REAL MONEY` remains blocked until Class E authority is granted.

## 7. Required escalation format

When reserved authority is genuinely needed, report:

- exact action needing authority;
- authority domain;
- candidate identity;
- technical readiness state;
- evidence supporting readiness;
- risks/known limitations;
- exposure envelope;
- alternatives/trade-offs if relevant;
- what technical work can continue without the decision.
