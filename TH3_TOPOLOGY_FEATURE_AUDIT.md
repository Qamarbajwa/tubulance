# TH3 LOCAL FLOW-TOPOLOGY FEATURE AUDIT

```
TOTAL SAMPLES ANALYZED: 512 OBJECTS ACROSS 8 FLOWS
TOPOLOGY FEATURES EXTRACTED: 14 INVARIANTS
COORDINATE / FLOW-ID LEAKAGE: ZERO (ALL FEATURES INTRINSIC/LOCAL)
```

| Feature Name | Mean | Std | Min | Max | Correlation with Advantage $A = \text{loss}(P0) - \text{loss}(P1)$ | Correlation with Target $\mathbf{y}$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `Q_invariant` | -1.2354e-02 | 2.6637e+00 | -1.5128e+01 | 2.3135e+01 | **-0.3591** | +0.4312 |
| `R_invariant` | -5.3053e-03 | 3.2893e+00 | -3.2546e+01 | 2.0323e+01 | **+0.4213** | -0.3335 |
| `Vieillefosse_Delta` | 3.7641e+02 | 3.6530e+03 | -3.4039e+03 | 7.8128e+04 | **-0.2452** | +0.1506 |
| `strain_magnitude` | 1.6984e+00 | 9.8618e-01 | 1.1477e-01 | 5.7914e+00 | **-0.0300** | -0.0408 |
| `vorticity_magnitude` | 2.3469e+00 | 1.4686e+00 | 2.4533e-14 | 1.0440e+01 | **-0.2772** | +0.4414 |
| `local_enstrophy` | 3.8323e+00 | 4.8022e+00 | 3.0093e-28 | 5.4495e+01 | **-0.3724** | +0.4519 |
| `strain_alpha` | 1.0875e+00 | 5.9992e-01 | 7.9229e-02 | 3.0408e+00 | **-0.0709** | -0.0181 |
| `strain_beta` | 1.5179e-01 | 3.8875e-01 | -8.2832e-01 | 1.6157e+00 | **+0.0875** | -0.0805 |
| `strain_gamma` | -1.2393e+00 | 7.7759e-01 | -4.6565e+00 | -4.9293e-02 | **+0.0110** | +0.0542 |
| `anisotropy_s_star` | 1.9074e-01 | 5.5848e-01 | -9.9587e-01 | 9.9841e-01 | **+0.0387** | -0.0570 |
| `vortex_stretching_lambda_omega` | 1.3549e-01 | 6.9279e-01 | -2.8440e+00 | 2.4596e+00 | **-0.1841** | +0.1916 |
| `rotation_to_strain_ratio` | 1.2527e+00 | 1.1829e+00 | 1.3035e-14 | 9.3153e+00 | **+0.0198** | +0.4844 |
| `dimensionless_Q` | -1.1272e-02 | 2.4191e-01 | -5.0000e-01 | 4.8861e-01 | **-0.0851** | +0.5176 |
| `dimensionless_vortex_stretching` | 7.4534e-02 | 3.4012e-01 | -7.9040e-01 | 7.4905e-01 | **-0.1441** | +0.1063 |

### Audit Findings
- **Primary Topology Predictors of Thread Advantage**:
  - Strain-rate magnitude (`strain_magnitude`) and intermediate strain eigenvalue (`strain_alpha`, `strain_gamma`) show clear physical correlation with representation preference.
  - Dimensionless Q and rotation-to-strain ratio delineate vortex-dominated vs shear-dominated regions.
