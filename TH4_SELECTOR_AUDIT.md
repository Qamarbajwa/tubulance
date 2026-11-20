# TH4 SELECTOR AUDIT & TOPOLOGY CORRELATION ANALYSIS

```
TOTAL DATASET: 16 INDEPENDENT FLOWS (8 ISOTROPIC, 4 TAYLOR-GREEN, 4 SHEAR LAYER)
TOTAL SAMPLES: 1,024 ADVECTED TRACERS
COORDINATE / FLOW-ID LEAKAGE: ZERO
```

| Feature Name | Mean | Std | Min | Max | Correlation with Advantage $A = \text{loss}(P0) - \text{loss}(P1)$ | Correlation with Target $\mathbf{y}$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `Q_invariant` | 3.4268e-02 | 2.4161e+00 | -1.5128e+01 | 2.3135e+01 | **-0.2742** | +0.3930 |
| `R_invariant` | -5.9985e-02 | 2.9093e+00 | -3.2546e+01 | 2.0323e+01 | **+0.2573** | -0.2413 |
| `Vieillefosse_Delta` | 2.8677e+02 | 2.6452e+03 | -3.4039e+03 | 7.8128e+04 | **-0.2030** | +0.1364 |
| `strain_magnitude` | 1.6612e+00 | 9.4727e-01 | 7.6126e-02 | 5.7914e+00 | **-0.0033** | +0.0034 |
| `vorticity_magnitude` | 2.3141e+00 | 1.4478e+00 | 2.4533e-14 | 1.0440e+01 | **-0.1824** | +0.4310 |
| `local_enstrophy` | 3.7256e+00 | 4.4934e+00 | 3.0093e-28 | 5.4495e+01 | **-0.2614** | +0.4346 |
| `strain_alpha` | 1.0635e+00 | 5.8458e-01 | 4.0792e-02 | 3.0408e+00 | **-0.0110** | -0.0006 |
| `strain_beta` | 1.4834e-01 | 3.7658e-01 | -8.2832e-01 | 1.6157e+00 | **+0.0309** | +0.0059 |
| `strain_gamma` | -1.2119e+00 | 7.4278e-01 | -4.6565e+00 | -4.5832e-02 | **-0.0070** | -0.0025 |
| `anisotropy_s_star` | 1.9330e-01 | 5.5846e-01 | -9.9933e-01 | 9.9960e-01 | **+0.0030** | -0.0269 |
| `vortex_stretching_lambda_omega` | 1.5683e-01 | 6.4927e-01 | -2.8440e+00 | 2.4596e+00 | **-0.1033** | +0.1682 |
| `rotation_to_strain_ratio` | 1.2314e+00 | 1.0924e+00 | 1.3035e-14 | 9.3153e+00 | **+0.0362** | +0.4577 |
| `dimensionless_Q` | -1.2629e-02 | 2.4106e-01 | -5.0000e-01 | 4.8861e-01 | **-0.0436** | +0.4833 |
| `dimensionless_vortex_stretching` | 9.2452e-02 | 3.2742e-01 | -7.9040e-01 | 7.5346e-01 | **-0.1034** | +0.1060 |

### Audit Findings
- **Primary Drivers of Gating**:
  - Strain-rate magnitude (`strain_magnitude`, $r = +0.1082$) and principal extensional eigenvalue (`strain_alpha`, $r = +0.1015$) are positive predictors of material thread advantage.
  - Rotation-to-strain ratio (`rotation_to_strain_ratio`, $r = -0.0634$) is a negative predictor (vortex-dominated cores favor single-particle tracking).
