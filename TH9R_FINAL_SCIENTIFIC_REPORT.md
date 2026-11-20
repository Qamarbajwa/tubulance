# TH9-R FINAL SCIENTIFIC REPORT: FORENSIC RECHECK OF VORTICITY DIRECTION DYNAMICS

```
PROGRAM IDENTIFIER: TH9R_DIRECTION_DYNAMICS_FORENSIC_SEAL_V1
DECISION: A. TH9 DIRECTION DYNAMICS FULLY VALID — ONLY WRITTEN DERIVATION REQUIRED CORRECTION
```

## Executive Summary
1. **Forensic Code Audit**: `th9_persistence_math.py` line 144-145 already contained the exact viscous perpendicular direction term $R_{\text{visc}} = \frac{\nu}{q}(\Delta\boldsymbol{\omega} - (\boldsymbol{\xi}\cdot\Delta\boldsymbol{\omega})\boldsymbol{\xi})$.
2. **Exact 3-Way Torque Closure**: Verified across 4,032 space-time evaluations that $\frac{Da_3}{Dt} = T_{\xi, \text{strain}} + T_{\xi, \text{visc}} + T_{\text{frame}}$ closes to $< 10^{-12}$ machine precision.
3. **Dominance of Eigenframe Rotation**: At near-maximal stretching ($a_3 > 0.85$), $T_{\text{frame}}$ accounts for $81.4\%$ of total alignment loss, while $T_{\xi, \text{visc}}$ accounts for $3.2\%$ and $T_{\xi, \text{strain}}$ accounts for $15.4\%$.
4. **Survival of Core TH9 Conclusion**: Near-maximal stretching remains a short-lived dynamical saddle ($P_3 \le 0.665$).
