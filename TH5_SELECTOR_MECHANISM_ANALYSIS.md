# TH5 SELECTOR MECHANISM ANALYSIS: TRANSLATING GATING INTO KINEMATICS

## Physical Mechanism of the TH4 Adaptive Lagrangian Selector

The empirical success of the TH4 topology selector ($g(\mathbf{z})$) is governed by two fundamental kinematic regimes:

1. **High Strain / Shear Layer Regime ($Q < 0, \|\mathbf{S}\|_F > \text{threshold}$)**:
   - Connected material threads align along the principal extensional direction $\mathbf{e}_3$, tracking the material deformation gradient $\mathbf{F}$. Thread stretching rate $\lambda_t = \hat{\mathbf{t}}^T \mathbf{S} \hat{\mathbf{t}}$ directly mirrors local vortex stretching $\lambda_\omega$, giving material threads superior predictive capacity.

2. **Vortex-Dominated / Isotropic Regime ($Q > 0, \mathcal{R}_\omega > 1.0$)**:
   - In coherent vortex cores and disordered isotropic decay, material threads undergo rapid rotational tumbling and folding, while $\boldsymbol{\omega}$ aligns preferentially with $\mathbf{e}_2$. The thread tangent decouples from $\boldsymbol{\omega}$, introducing geometric noise. Point particle trajectory history captures the mean Lagrangian advection and dissipation without spurious rotational deformation.

### Simplified Analytical Surrogate Rule:
```
IF Q < 0 AND ||S||_F > median(||S||_F):
    USE MATERIAL THREAD REPRESENTATION (P1)
ELSE:
    USE POINT PARTICLE HISTORY (P0)
```
