# RESOURCE BUDGET & GOVERNANCE BOUNDS

```
================================================================================
ADOPTION ID:                  NS_GOVERNANCE_V2_2_ADOPTION_001
RECONCILIATION DATE:          2026-08-19
================================================================================
```

---

## 1. Resource Limits

- **Maximum Iterations per Autonomous Cycle**: 30 steps.
- **Maximum Wallclock Time per Simulation Batch**: 15 minutes (with periodic background task tracking).
- **Maximum Grid Resolution**: $32^3$ for cross-resolution validation (prevents memory explosion on workstation).
- **Storage Cap**: $< 100\text{ MB}$ total raw datasets (using efficient Parquet compression).
- **Diminishing-Return Detection**: Abort parameter sweeps if variance $< 10^{-4}$ across 3 successive refinements.
