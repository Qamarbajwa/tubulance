# Stronger Project-Specific Controls Inventory & State Mapping (v4.0.3 → v4.0.4)

**Migration ID:** `NS-GOV-MIG-V404-001`  
**Migration Mode:** `MIGRATION_GOVERNED`  
**Mathematical Authority:** `Mathematical Research Constitution v1.0.1` (Preserved Unmodified)  
**Target State:** Non-Conflicting Staged Preparation (`MIGRATION_BLOCKED` pending `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.4.zip` source archive verification)

---

## 1. Inventory of Stronger Project-Specific Controls (Section 9)

The Navier–Stokes research repository (`tubulance`) enforces domain-specific scientific and mathematical controls via `Mathematical Research Constitution v1.0.1` and `src/navier3d/math_assurance/` that are strictly stronger than generic `UNIVERSAL_GOVERNANCE_MINIMAL` (both `v4.0.3` and `v4.0.4`). Every one of these 17 stronger controls is explicitly retained and bound:

| # | Control Domain | Generic Universal Governance (`v4.0.3` / `v4.0.4`) | Stronger Navier–Stokes Project Control (`MRC v1.0.1` + Binding) | Disposition |
|---:|:---|:---|:---|:---|
| 1 | **Mathematical Writer / Reviewer / Acceptor Separation** | Generic R1–R3 role separation (`writer != reviewer`, `acceptor` distinct for R3) | Mandatory 3-role separation for all mathematical theorem claims (`antigravity-primary-agent` ≠ `MATH_I2` fresh-context verifier ≠ `GOV_I2` governance coordinator); automated `writer_anti_self_acceptance` gate | **PRESERVED (STRONGER)** |
| 2 | **Mathematical Claim-Passport Rules** | Generic capability/evidence tracking | Mandatory 12-dimensional Claim Passport (`truth_status`, `gov_evidence_level`, `math_evidence_level`, `gov_review_independence`, `math_review_independence`, `formalization_state`, `understanding_level`, `novelty`, `significance`, `external_validation`, `community_status`, `project_status`) enforced by `ClaimManager` | **PRESERVED (STRONGER)** |
| 3 | **Evidence Hierarchy (`E1–E5`)** | Single operational evidence axis (`E1`–`E5`) | Dual orthogonal evidence namespaces: `GOV_E1_MODEL_RAW`..`GOV_E5_EXTERNAL_ANCHORED` AND `MATH_E1_INFORMAL_DERIVATION`..`MATH_E5_FORMALLY_OR_EXTERNALLY_CONFIRMED` | **PRESERVED (STRONGER)** |
| 4 | **Independence Hierarchy (`IND0–IND3`)** | Single independence scale (`IND0`–`IND3`) | Dual orthogonal independence namespaces: `GOV_I1`..`GOV_I4` AND `MATH_I1_WRITER_INTERNAL`..`MATH_I4_HUMAN_SPECIALIST` | **PRESERVED (STRONGER)** |
| 5 | **Falsification-First Research** | Preserve failed tests and defects | Mandatory adversarial falsification suites (`test_th1_falsification.py`, `test_th6_falsification_suite.py`, R1–R4 reassessments) required before any positive claim is accepted | **PRESERVED (STRONGER)** |
| 6 | **Fail-Closed Unresolved State** | Release `NO-GO` until gates pass | `clay_statement_b_status: "UNRESOLVED"` locked as an immutable hard gate (`PASS_ENFORCED`); only `CLM-TARGET` with `MATH_E5` + `MATH_I4` can alter target status | **PRESERVED (STRONGER)** |
| 7 | **External-Review Requirements** | External review optional unless bound | Contradiction firewall in `claims.py`: `NOT_EXTERNALLY_REVIEWED` cannot combine with `COMMUNITY_ACCEPTED` or `PARTIALLY_ACCEPTED`; `N2_NOT_FOUND_IN_AUDITED_SOURCES` cannot auto-promote to `N3`/`N4` | **PRESERVED (STRONGER)** |
| 8 | **Negative-Evidence Preservation** | Do not delete failed evidence | Append-only `research_memory/NEGATIVE_EVIDENCE_LEDGER.yaml` (`47_OF_47_PRESERVED_PASS`) and `RESEARCH_OBSTRUCTION_REGISTRY.yaml` (`24_OF_24_PRESERVED_PASS`) enforced by automated tests | **PRESERVED (STRONGER)** |
| 9 | **No Proof by Tests Alone** | Tests verify software behavior | `MATHEMATICAL_REGRESSION_RULES.yaml`: unit/integration/numerical tests (`MATH_E2`/`MATH_E3`) can falsify conjectures or verify helper code, but can NEVER certify `PROVED_THEOREM` (`MATH_E4` required) | **PRESERVED (STRONGER)** |
| 10 | **No Proof by Symbolic Computation Alone** | Automated checks support evidence | Symbolic scripts (SymPy/algebraic checks, `MATH_E3_MACHINE_COMPUTED`) require audited analytical proof (`MATH_E4`) of domain validity, boundary conditions, and regularity | **PRESERVED (STRONGER)** |
| 11 | **No Proof by Lean Compilation Alone** | Formal checks support verification | `FORMALIZATION_FIDELITY_REGISTER.yaml`: formal compilation certifies only the formal syntax unless target-equivalence gate (`v2_target_equivalence_gate`) proves exact isomorphism to Clay Statement B on $\mathbb{T}^3$ | **PRESERVED (STRONGER)** |
| 12 | **No Proof by AI Confidence** | Raw model output is `E1` | AI consensus or confidence (`GOV_E1_MODEL_RAW`) is zero mathematical evidence; `PROJECT_SYNTHESIS` claims are strictly prohibited from holding `PROVED_THEOREM` status | **PRESERVED (STRONGER)** |
| 13 | **Candidate-Bound Evidence** | Evidence bound to candidate SHA | `frozen_candidate` and `last_verified_checkpoint` SHA bindings in `PROJECT_STATE.yaml` plus cryptographic Merkle seals (`*_SEALED_manifest.json`) | **PRESERVED (STRONGER)** |
| 14 | **Historical Immutability** | Archive historical governance | `immutable_records` list in task envelopes; retracted/superseded claims (`CLM-036`, `CLM-037-B-R2`, `CLM-038`) remain permanently in `CLAIM_REGISTRY.yaml` and are corrected only prospectively | **PRESERVED (STRONGER)** |
| 15 | **Release / Deployment Separation** | Separate `eligible` and `deployment_authorized` | Pure mathematical research lock: `state: "NO-GO"`, `eligible: false`, `deployment_authorized: false`, `reason: "PURE_MATHEMATICAL_RESEARCH_PROGRAM_CLAY_B_UNRESOLVED"` | **PRESERVED (STRONGER)** |
| 16 | **Serialized State Writes** | Single `PROJECT_STATE.yaml` | `REVISION_COMPARE_AND_SWAP` (`revision: 17`, `last_expected_revision: 16`) preventing concurrent or stale state overwrites | **PRESERVED (STRONGER)** |
| 17 | **Git Checkpoint Discipline** | Normal safe Git operations | Full 40-character SHA verification (`git rev-parse HEAD` == `origin/main`), prohibition on `git push --force`, and immutable commit history | **PRESERVED (STRONGER)** |

---

## 2. State Mapping: `v4.0.3` Live State → `v4.0.4` Staged State Model (Section 11)

Every field of `governance/PROJECT_STATE.yaml` (revision 17) is mapped into the `v4.0.4` schema without resetting any status field, gate, blocker, or scientific invariant:

| Field Path in `PROJECT_STATE.yaml` | Live `v4.0.3` Value (Rev 17) | Staged `v4.0.4` Value (Rev 18 Candidate) | Semantic Mapping / Preservation Rule |
|:---|:---|:---|:---|
| `schema_version` | `"4.0.3"` | `"4.0.4"` | Schema version header bump only upon verified cutover |
| `revision` | `17` | `18` (staged) | Compare-and-swap increment (`last_expected_revision: 17`) |
| `activation` | `"ACTIVE"` | `"STAGED_CANDIDATE_BLOCKED_ON_SOURCE_ZIP"` | Fail-closed until `v4.0.4.zip` is verified and accepted |
| `project.id` / `branch` | `"tubulance"` / `"main"` | `"tubulance"` / `"main"` | Identity preserved |
| `governance_binding.active_version` | `"4.0.3"` | `"4.0.4"` (staged) | Runtime governance target version |
| `governance_binding.constitutional_standard` | `"Mathematical Research Constitution v1.0.1"` | `"Mathematical Research Constitution v1.0.1"` | Exact preservation of domain mathematical authority |
| `governance_binding.adoption_mode` | `"MIGRATION_GOVERNED"` | `"MIGRATION_GOVERNED"` | Mid-project governed migration mode |
| `epistemic_status.clay_statement_b_status` | `"UNRESOLVED"` | `"UNRESOLVED"` | **Hard Invariant Preserved** |
| `epistemic_status.scientific_program_status` | `"NS-OPENAI-B1-REASSESSMENT-R4_PERIODIC_COST_BARRIER_PROVED"` | `"NS-OPENAI-B1-REASSESSMENT-R4_PERIODIC_COST_BARRIER_PROVED"` | **Hard Invariant Preserved** (zero reinterpretation of R4) |
| `epistemic_status.active_milestone` | `"NS-OPENAI-B1-REASSESSMENT-R4"` | `"NS-OPENAI-B1-REASSESSMENT-R4"` | **Hard Invariant Preserved** (`NS-OPENAI-B2` remains `BLOCKED`) |
| `current_objective` | `NS-OPENAI-B1-REASSESSMENT-R4` (`COMPLETED_PERIODIC_COST_BARRIER_PROVED`) | `NS-OPENAI-B1-REASSESSMENT-R4` (`COMPLETED_PERIODIC_COST_BARRIER_PROVED`) | Identical; no silent research direction change |
| `objectives` | 14 historical canonical milestones (`R4` down to `TP2-G6-B-R1`) | All 14 historical milestones preserved verbatim | Append-only objective history |
| `hard_gates.clay_statement_b_unresolved` | `"PASS_ENFORCED"` | `"PASS_ENFORCED"` | Preserved |
| `hard_gates.dag_cycle_count` | `"0_CYCLES_PASS"` | `"0_CYCLES_PASS"` | Preserved |
| `hard_gates.claim_passport_census` | `"44_OF_44_VALID_PASS"` | `"44_OF_44_VALID_PASS"` | Preserved (no claim relabeling or promotion) |
| `hard_gates.negative_evidence_retention` | `"47_OF_47_PRESERVED_PASS"` | `"47_OF_47_PRESERVED_PASS"` | Preserved |
| `hard_gates.structural_obstruction_retention` | `"24_OF_24_PRESERVED_PASS"` | `"24_OF_24_PRESERVED_PASS"` | Preserved |
| `release.state` | `"NO-GO"` | `"NO-GO"` | **Hard Invariant Preserved** |
| `release.eligible` | `false` | `false` | **Hard Invariant Preserved** |
| `release.deployment_authorized` | `false` | `false` | **Hard Invariant Preserved** (`DEPLOYMENT AUTHORITY = NONE`) |
| `known_risks` | 5 structural risks (`RISK-DIRECT-PRELOAD-DAMPING`, `RISK-AUTONOMOUS-PRECURSOR-PHASE` w/ `NS-OBS-020B-R4`, etc.) | All 5 structural risks preserved verbatim | Preserved |
