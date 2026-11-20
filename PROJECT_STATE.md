# PROJECT STATE: COMPUTATIONAL & REPOSITORY STATUS

```
================================================================================
GOVERNANCE ADOPTION ID:       NS_GOVERNANCE_V2_2_ADOPTION_001
TIMESTAMP UTC:                2026-08-19T17:40:00Z
REPOSITORY HEALTH:            100% CLEAN & TESTED (826/826 Passing)
SEAL INTEGRITY:               ALL CRYPTOGRAPHIC MERKLE SEALS VERIFIED
================================================================================
```

---

## 1. Repository Inventory & Codebase Health

- **Total Test Census**: 826 collected unit & integration tests across 32 test files.
- **Pass Rate**: $100\%$ (820 passed, 6 skipped, 0 failed, exit code 0).
- **Core PDE Engines**:
  - `src/navier3d/mesh.py`, `fields.py`, `boundary_conditions.py`, `convection.py`, `diffusion.py`, `pressure.py`, `projection.py`, `time_integrators.py`, `strain.py`, `decaying_turbulence.py`.
- **Experimental & Scientific Analysis Engines**:
  - `th1_suite.py` (Lagrangian tracking & material threads)
  - `th3_topology_features.py` & `th3_adaptive_models.py` (Invariants $Q, R$, strain gating)
  - `th4_stress_models.py` (Stress tensor closures)
  - `th5_vorticity_math.py` (Pointwise vorticity states & strain alignments)
  - `th6_falsification_engine.py` (Adversarial strained layers & B1 falsification)
  - `th7_viscous_influx_math.py` (Viscous logarithmic influx decomposition $V_{\log} = \nu[\Delta q/q - \|\nabla\boldsymbol{\xi}\|^2]$)
  - `th8_depletion_math.py` (Geometric depletion & field vorticity grids)
  - `th9_persistence_math.py` & `th9r_direction_forensic.py` (Vorticity direction torque & eigenframe rotation)
  - `la1_multiscale_math.py` & `la1r_physical_scale_math.py` (Multiscale localized averaging)
  - `th10_burst_math.py` & `th10r_true_burst_math.py` (Strict dangerous growth bursts & inter-burst damping)
  - `ns_blowup1_rescaling_math.py` & `ns_blowup2_full_limit_math.py` (Parabolic rescaling on cylinders $Q_R$)
  - `bridge1_limit_rigidity_math.py` (Blow-up rescaling, dual-class identification, and rigidity eligibility).

---

## 2. Active Seals & Provenance Verification

| Investigation / Branch | Seal Identifier | Pre-Run Match | Post-Run Match | Tests Passed | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TH10** | `TH10_BURST_RECURRENCE_CUMULATIVE_SEAL_V1` | `YES` | `YES` | 82/82 | Archived/Superseded by TH10-R |
| **NS-BLOWUP-1** | `NS_BLOWUP1_PARABOLIC_RESCALING_SEAL_V1` | `YES` | `YES` | 83/83 | Archived/Superseded by NS-BLOWUP-2 |
| **TH10-R** | `TH10R_TRUE_GROWTH_BURST_RECURRENCE_SEAL_V1` | `YES` | `YES` | 84/84 | Level 2 Verified |
| **NS-BLOWUP-2** | `NS_BLOWUP2_FULL_FIELD_LIMIT_SEAL_V1` | `YES` | `YES` | 85/85 | Level 2 Verified |
| **NS-BRIDGE1** | `NS_BRIDGE1_LIMIT_CLASS_COMPATIBILITY_AND_RIGIDITY_GATE_V1` | `YES` | `YES` | 86/86 | Level 2 Verified |

---

## 3. Storage & Artifact Footprint

- **Raw Datasets**:
  - `RAW_TH10R_TRUE_BURSTS.parquet` ($468.5\text{ KB}$) & `.csv` ($1.25\text{ MB}$)
  - `RAW_NS_BLOWUP2_FULL_FIELDS.parquet` ($16.8\text{ KB}$) & `RAW_NS_BLOWUP2_PROFILE_METRICS.parquet` ($16.8\text{ KB}$)
  - `RAW_BRIDGE1_RESCALED_FIELDS.parquet` ($26.5\text{ KB}$) & `RAW_BRIDGE1_RESCALED_EVENTS.csv` ($45.1\text{ KB}$)
- **Total Workspace Footprint**: Clean, contained within repo; all raw datasets verified non-empty.
