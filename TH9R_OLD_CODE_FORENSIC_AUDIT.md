# TH9-R FORENSIC CODE AUDIT: VORTICITY DIRECTION DYNAMICS

## 1. Audit Findings in Original TH9 Codebase
A line-by-line inspection of `src/navier3d/experimental/th9_persistence_math.py` (lines 142–146) reveals:
```python
    # 1. Vorticity direction derivative D xi / D t
    S_xi = S @ xi
    visc_xi_perp = (decomp.lap_omega - np.dot(xi, decomp.lap_omega) * xi) / max(1e-6, q)
    D_xi_Dt = (S_xi - l_w * xi) + nu * visc_xi_perp
```

### Verdict on Original Code:
- **R_visc WAS present and correctly computed** in the numerical execution of `D_xi_Dt` and `T_xi`.
- In the prose of `TH9_FINAL_SCIENTIFIC_REPORT.md`, `T_xi` was presented without explicitly writing out its two constituent sub-terms ($T_{\xi, \text{strain}}$ and $T_{\xi, \text{visc}}$).
- **Conclusion**: `OLD TH9 NUMERICS VALID — PROSE DERIVATION INCOMPLETE ONLY`.
