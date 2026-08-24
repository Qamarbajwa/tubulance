# TP2-G4-A2: TH9-R RESURRECTION AUDIT & TRANSFERABILITY MATRIX

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2`  
**Governance Standard:** Autonomous Project Governance v2.9.4  
**Date:** 2026-08-25T00:28:00Z  

---

## 1. Background & Resurrection Context

In milestone `NS-RPM-1`, pathway `TH9-R (Eigenframe Rotation & Pressure-Hessian Direction Evolution)` was held as `TERMINATED_BY_OBSTRUCTION` due to the finite-window numerical persistence gap (`NS-OBS-003`).

In `TP2-G4-A1`, the SVD orientation decomposition $\|D J_\omega\|_F^2 = \|J_\omega\|_F^2 \sum p_i \sigma_i^2$ independently proved that finite-time deformation magnitude $\sigma_1$ cannot force quadratic variation production $Q_s$ without directional orientation control. This promoted `TH9-R` to `RESURRECTION_CANDIDATE`.

---

## 2. Granular Transferability Classification Matrix

We rigorously audit each mathematical component of `TH9-R` to determine what transfers to `TP2-G4-A2`:

| Component / Result from TH9-R | Classification | Mathematical Justification & Scope |
|---|---|---|
| **Deviatoric Pressure Hessian Torque** | `DIRECTLY_REUSABLE` | The formula $e_j \cdot D_t e_i = \frac{-\Pi_{ji}^{\text{dev}} - [\Omega^2]_{ji} + \nu [\Delta S]_{ji}}{\lambda_i - \lambda_j}$ holds identically in 3D incompressible Navier–Stokes under Convention M. |
| **Twist-Antitwist Dynamic Cancellation** | `ANALOGOUS_ONLY` | In `TH9-R`, frame rotation limits alignment between $\xi = \omega / |\omega|$ and $e_3$. In `G4-A2`, the question is whether frame rotation prevents $G = J_\omega$ from concentrating in $v_3$ or neutral $v_2$. |
| **Strain-to-Deformation Bridge ($R_{ij}$)** | `REQUIRES_NEW_BRIDGE` | `TH9-R` operated strictly on the instantaneous strain frame $e_i$. `G4-A2` requires linking $e_i$ to the time-integrated singular frame $v_i$ via the doubly stochastic overlap matrix $R_{ij} = |v_i \cdot e_j|^2$. |
| **Finite-Window Empirical Persistence Bounding** | `NOT_APPLICABLE` | Empirical observation of short alignment bursts in DNS cannot be used as an analytical substitute for a-priori regularity bounds (`NS-OBS-003`). |
| **Static Alignment Depletion ($\delta > 0$)** | `FALSIFIED_PERMANENT` | Static depletion bounds remain permanently falsified (`NEG-EV-002`). |

---

## 3. Comparison with Modern Lagrangian Alignment Literature (Encinas-Bartos & Haller 2024)

Recent mathematical physics literature on Lagrangian stretching and finite-time Lyapunov exponents (e.g., Encinas-Bartos & Haller, *J. Fluid Mech.* 2024; Ni, Ouellette & Voth, *J. Fluid Mech.* 2012) establishes that:
1. **Passive Material Vectors**: In smooth chaotic advection, passive vectors generically align asymptotically with the dominant Lagrangian stretching direction ($v_1$).
2. **Active Vorticity Gradient**: For active fluid fields, $G = J_\omega$ is not a passive vector; its source term $T_{ij} = (\partial_j S_{ik}) \omega_k$ continuously injects gradient components orthogonal to $v_1$.
3. **Smoothness Assumption Barrier**: All existing Lagrangian stretching alignment theorems assume a-priori $C^1$ velocity fields with finite Lyapunov exponents. Presupposing these bounds to prove Navier–Stokes regularity is circular (`NS-OBS-004`).
