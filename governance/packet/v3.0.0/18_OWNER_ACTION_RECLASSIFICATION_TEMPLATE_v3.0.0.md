# OWNER ACTION RECLASSIFICATION — TEMPLATE v3.0.0

## Purpose

Legacy governance often routes technical work to the owner because an item was labeled `OWNER-*`. This template determines whether owner authority is actually required.

## Classification options

- `OWNER_INTENT`
- `BUSINESS_DECISION`
- `BUDGET_SPEND`
- `LEGAL_COUNSEL`
- `EXTERNAL_ACCOUNT_PROVISIONING`
- `INFRASTRUCTURE`
- `TECHNICALLY_DERIVABLE`
- `AUTOMATABLE_EVIDENCE`
- `FINANCIAL_EXPOSURE`
- `DEPLOYMENT_AUTHORIZATION`

Multiple classifications may apply.

## Reclassification table

| Legacy ID | Legacy request | Why owner was asked | Actual classification | Technical work autonomous? | Reserved action remaining | Evidence/status |
|---|---|---|---|---|---|---|
| OWNER-001 | | | | | | |

## Rules

### Terms/privacy/legal wording
Owner/legal authority for policy/commitment. Engineering implements and verifies technical behavior.

### Marketplace inclusion/exclusion
Business intent unless a purely technical compatibility decision.

### AI/provenance disclosures
Business/legal policy plus technical implementation. Policy authority does not prove implementation.

### Provider/API funding
Owner sets spend envelope. Engineering may use/provision within delegated infrastructure authority. Technical behavior is evidence-driven.

### Billing enforcement / real-money activation
Owner/business authorizes real-money exposure. Engineering establishes technical readiness separately. Authorization cannot make unsafe billing safe.

### Live spend trials
Owner authorizes budget/exposure. Technical correctness remains evidence-driven.

### Infrastructure provisioning
Treat as infrastructure/external action; owner involvement only when credentials/contracts/spend/business choices genuinely require it.

### Vendor/CAPTCHA/provider selection
Owner decides product/cost/privacy preference where material. Engineering owns technical integration/verification.

### Synthetic/adversarial benchmarks
Autonomous technical work when inputs/exposure stay inside approved envelope.

### Stress/performance targets
Owner gives user/business expectations: expected users, delay tolerance, growth, criticality, budget sensitivity. Engineering derives p95/p99/throughput/headroom targets.

### Release SHA/environment
Machine-derived. Owner must not manually certify candidate identity.

### Operational controls
Owner defines risk/business expectations. Engineering derives technical controls.

### Dispatch authority
Prefer stable action classes and standing mandate over repeated case-by-case technical approval.

### Production accounts/services
External provisioning only when credentials/contracts/money/provider ownership truly require it.

### Final release GO
Rename to `DEPLOYMENT_AUTHORIZATION` when the intended owner action is permission to deploy an already release-eligible candidate.

## Reclassification outcome

After classification, remove `TECHNICALLY_DERIVABLE` and `AUTOMATABLE_EVIDENCE` work from the owner queue and place it into the executable dependency graph.

Do not remove genuine business/legal/spend/exposure/deployment authority.
