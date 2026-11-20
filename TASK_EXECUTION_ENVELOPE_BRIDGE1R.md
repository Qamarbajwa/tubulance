# TASK EXECUTION ENVELOPE: NS-BRIDGE1-R
## Critical Limit Consistency & Cross-Resolution Gate

```
================================================================================
TASK IDENTIFIER:              TASK_NS_BRIDGE1R_001
PROJECT IDENTIFIER:           tubulance (3D Incompressible Navier-Stokes)
STATE VERSION:                NS_GOVERNANCE_V2_2_ADOPTION_001_R1
BASE SHA:                     HEAD
TASK TYPE:                    SCIENTIFIC_INTERROGATION
SELECTED METHOD:              P11A — Scientific System Interrogation
AUTHORITY LEVEL:              Level 2 — Technically Verified
STATUS:                       READY_TO_EXECUTE
================================================================================
```

---

## 1. Objective & Scope
Perform cross-resolution multi-scale verification ($16^3 \to 32^3$) on nested space-time cylinders $Q_R = B_R(0) \times (-R^2, 0]$ across the coexisting Townsend Sheet and Burgers Tube limiting classes to test:
1. **Scale-Persistent Cone Confinement**: Does $\theta_{\text{cone}} \le 35^\circ$ remain tightly bounded under dyadic grid refinement?
2. **Critical $L^3$ Mass Tightness**: Does localized scale-critical $L^3$ velocity mass remain uniformly bounded without spatial blow-up under resolution doubling?
3. **Dual-Class Robustness**: Does the $75\% / 25\%$ Townsend / Burgers partition persist across refined grids?

---

## 2. Inputs & Locked Decisions
- **Authoritative Inputs**:
  - `CURRENT_SCIENTIFIC_STATE.md` (SSOT under `NS_GOVERNANCE_V2_2_ADOPTION_001_R1`)
  - `BRIDGE1_LIMIT_CLASS_DECISION.json` (Verdict C: Dual-Class Coexistence)
  - `src/navier3d/experimental/bridge1_limit_rigidity_math.py`
- **Locked Decisions**:
  - Parabolic dilation rule: $u_\lambda = \lambda u(\lambda x, \lambda^2 t), \omega_\lambda = \lambda^2 \omega, r_k = q_k^{-1/2}$.
  - Galilean normalization against box center velocity.
  - Zero modification to verified previous sealed evidence.

---

## 3. File Permissions & Tool Authority
- **Allowed New Files**:
  - `src/navier3d/experimental/bridge1r_limit_consistency_math.py`
  - `tests/test_bridge1r_limit_suite.py`
  - `scripts/create_bridge1r_clean_seal.py`
  - `scripts/run_bridge1r_master_program.py`
  - `BRIDGE1R_*` JSON/MD deliverables and raw Parquet/CSV outputs.
- **Forbidden Files**:
  - Any mutation of core PDE files in `src/navier3d/` or existing sealed manifests.
- **Allowed Tools**:
  - `view_file`, `write_to_file`, `replace_file_content`, `run_command`, `manage_task`, `schedule`.

---

## 4. Acceptance Criteria & Test Contract
1. **Pre-Run Merkle Seal**: `PRE-RUN CLEAN SEAL MATCH = YES` recorded in `BRIDGE1R_CLEAN_MANIFEST.json`.
2. **100% Test Passage**: All tests in `tests/test_bridge1r_limit_suite.py` must pass with zero failures.
3. **Post-Run Merkle Seal**: `POST-RUN CLEAN SEAL MATCH = YES` confirmed after batch execution.
4. **Deliverables Complete**: All deliverables produced, non-empty, and verified.
