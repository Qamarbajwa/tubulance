# APPROACH REGISTRY: COMPUTATIONAL & MODELING METHODS

```
================================================================================
ADOPTION ID:                  NS_GOVERNANCE_V2_2_ADOPTION_001
RECONCILIATION DATE:          2026-08-19
================================================================================
```

---

## 1. Active Computational Approaches

1. **Staggered MAC Mesh & Fourier Projection Solvers**:
   - Staggered grid representation with ghost cells for exact mass conservation ($\nabla \cdot \mathbf{u} = 0$).
   - Spectral/FFT Poisson pressure solver with Theta-scheme fractional step time integration.
2. **Lagrangian Trajectory & Alignment Tracker**:
   - 4th-order Runge-Kutta particle advection tracking strain eigensystem along material paths.
3. **Viscous Influx Decomposition Engine**:
   - Finite difference calculation of $V_{\log} = \nu[\Delta q/q - \|\nabla\boldsymbol{\xi}\|_F^2]$.
4. **Parabolic Blow-Up Dilation Engine**:
   - Invariant rescaling on local cylinders $Q_R = B_R(0) \times (-R^2, 0]$ with $r_k = q_k^{-1/2}$, $y = (x-x_k)/r_k, s = (t-t_k)/r_k^2$.
5. **Exact Model Distance Classifiers**:
   - Objective $L^2(Q_R)$ distance metrics against 3D Townsend shear sheets and axisymmetric Burgers vortex tubes.
