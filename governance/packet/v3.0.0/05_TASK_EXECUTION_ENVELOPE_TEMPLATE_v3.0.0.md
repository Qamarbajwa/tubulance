# TASK EXECUTION ENVELOPE TEMPLATE — v3.0.0

Create one envelope for every mutable bounded objective.

```yaml
task_execution_envelope:
  schema_version: "3.0.0"

  identity:
    task_id: "TASK-XXXX"
    project_id: "..."
    project_name: "..."
    governance_version: "3.0.0"
    adoption_mode: "DAY0"  # DAY0 | MID_PROJECT_UNGOVERNED | MIGRATION_GOVERNED | AD_HOC

  direction:
    intent_refs:
      - "INTENT/OUTCOME/CONSTRAINT reference"
    roadmap_objective: "OBJ-XXXX"
    owner_non_goals:
      - "..."
    owner_reserved_boundaries:
      - "..."

  objective:
    exact_objective: "..."
    rationale: "..."
    done_boundary: "..."

  base_state:
    repository_or_workspace: "..."
    branch_or_state_channel: "..."
    base_candidate_id: "..."
    dirty_state: "CLEAN"  # CLEAN | DIRTY_KNOWN | DIRTY_UNKNOWN | N/A
    preserved_unrelated_work:
      - "..."

  eligibility:
    dependencies:
      - id: "..."
        state: "ACCEPTED | SATISFIED | BLOCKED | N/A"
        evidence_ref: "..."
    technical_inputs_available: true
    traceable_to_intent: true
    architecture_permits: true
    inside_standing_mandate: true
    candidate_state_known: true
    risk_inside_ceiling: true
    blocking_invariant_present: false
    reserved_authority_required_for_technical_mutation: false
    eligible: true
    blocker_class: null
    blocker_detail: null

  classification:
    risk_tier: "T1"  # T1 | T2 | T3 | T4 | T5
    action_class: "A"  # A | B | C | D | E | F
    risk_reasons:
      - "..."
    active_modules:
      - "..."
    not_activated_material_modules:
      - module: "..."
        reason: "..."

  roles_and_authority:
    orchestrator: "..."
    writer:
      id: "..."
      qualified: true
      risk_ceiling: "..."
    reviewer_or_verifier:
      id: "..."
      qualified: true
      expected_independence: "IND0"  # IND0 | IND1 | IND2 | IND3
    implementation_authority: "AUTONOMOUS_WITHIN_ENVELOPE"
    verification_authority: "..."
    release_eligibility_authority: "EVIDENCE_DERIVED_GATE | ..."
    reserved_external_authority:
      required: false
      type: "NONE"  # OWNER_INTENT | BUSINESS_POLICY | LEGAL_COMPLIANCE | FINANCIAL_EXPOSURE | DEPLOYMENT_AUTHORITY | NONE
      trigger: null

  mutation_scope:
    allowed:
      - "..."
    forbidden:
      - "..."
    protected:
      - "..."
    allowed_tools_actions:
      - "..."
    forbidden_tools_actions:
      - "..."

  assurance_contract:
    capability_or_requirement_ids:
      - "CAP-XXXX"
    intent: "..."
    valid_inputs:
      - "..."
    invalid_input_behavior:
      - input_class: "..."
        expected_behavior: "..."
    preconditions:
      - "..."
    transformation_rules:
      - "..."
    invariants:
      - id: "INV-XXXX"
        statement: "..."
        zero_tolerance: true
    outputs:
      - "..."
    postconditions:
      - "..."
    failure_contracts:
      - condition: "..."
        expected_behavior: "..."
    retry_idempotency_concurrency:
      - "..."
    persistence_restart_recovery:
      - "..."
    security_authority:
      - "..."
    performance_capacity:
      - "..."
    required_real_environment:
      - "..."
    intent_fidelity_review_required: true

  acceptance:
    hard_gates:
      - id: "GATE-XXXX"
        condition: "..."
        required_state: "PASS"
    kpis:
      - id: "KPI-XXXX"
        metric: "..."
        threshold: "..."
        release_blocking: false
    required_evidence:
      minimum_strength: "E2"  # E2 | E3 | E4 | E5
      required_environments:
        - "..."
      minimum_independence: "IND0"  # IND0 | IND1 | IND2 | IND3
      candidate_bound: true

  verification_plan:
    static:
      - "..."
    unit:
      - "..."
    integration:
      - "..."
    end_to_end:
      - "..."
    negative_boundary:
      - "..."
    failure_recovery:
      - "..."
    security:
      - "..."
    performance:
      - "..."
    real_environment:
      - "..."
    adversarial:
      - "..."
    independent_review:
      - "..."

  recovery:
    rollback_or_forward_recovery: "..."
    checkpoint_required_before_mutation: true
    state_integrity_check: "..."

  stop_conditions:
    - "scope ambiguity"
    - "risk exceeds ceiling"
    - "unexpected destructive/external effect"
    - "candidate identity becomes unknown"
    - "required reserved authority is reached"
    - "evidence contradicts fundamental contract assumption"

  completion_record:
    final_candidate_id: null
    status: "NOT_STARTED"
    evidence_receipts: []
    technical_acceptance: "NOT_EVALUATED"
    release_eligibility_effect: "NONE"  # NONE | MAY_ADVANCE | BLOCKS | N/A
    negative_evidence_refs: []
    checkpoint_id: null
```

## Envelope rule

The envelope may be extended, but none of the following concepts may be collapsed into a single ambiguous `approved` flag:

- owner intent;
- business/legal authority;
- implementation authority;
- technical verification;
- release eligibility;
- deployment authorization.
