# TP2-G4-A2: LITERATURE & NOVELTY AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2`  
**Governance Standard:** Autonomous Project Governance v2.9.4  
**Date:** 2026-08-25T00:29:00Z  

---

## 1. Audited Literature Matrix

We explicitly compare the mathematical objects and mechanisms of `TP2-G4-A2` against foundational and modern literature:

| Research Reference | Primary Object Studied | Relationship to TP2-G4-A2 | Novelty / Lineage Classification |
|---|---|---|---|
| **Ashurst et al. (1987)** | Vorticity vector alignment with strain eigenframe ($\omega \cdot e_2$) | Studied vector $\omega$, not tensor $J_\omega$. Found alignment with intermediate strain $e_2$. | `KNOWN_HISTORICAL_BACKGROUND` |
| **Lapeyre, Klein & Hua (1999)** | Passive scalar gradient $\nabla \theta$ vs strain eigenbasis | Studied passive scalar without source term $T_{ij} = (\partial_j S_{ik})\omega_k$. | `KNOWN_ANALOGUE_PASSIVE` |
| **Encinas-Bartos & Haller (2024)** | Lagrangian stretching directions and Cauchy–Green alignment | Proved asymptotic alignment for passive material elements assuming $C^1$ smooth velocity. | `KNOWN_CAUCHY_GREEN_THEORY` |
| **Constantin & Iyer (2008)** | Stochastic Lagrangian representation of 3D Navier–Stokes | Established martingale representation $Z_s = D_s \omega(A_s)$, but did not decompose $Q_s$ via SVD projectors $p_i$. | `PRIMARY_THEORETICAL_FOUNDATION` |
| **TH9-R (Internal Milestone)** | Vorticity direction $\xi$ evolution under deviatoric pressure Hessian torque | Derived strain-frame rotation rate $\dot{e}_i$, but did not connect to stochastic deformation frame $v_i$. | `PROJECT_ANCESTOR_REFORMULATED` |
| **TP2-G4-A2 (Current Milestone)** | SVD orientation weights $p_i = \|v_i^T J_\omega\|^2 / \|J_\omega\|^2$ and efficiency $\eta = \sum p_i (\sigma_i/\sigma_1)^2$ for stochastic Cauchy quadratic variation | First exact SVD decomposition connecting stochastic covariance production to vorticity-gradient component-space orientation. | `PROJECT_REFORMULATION / POSSIBLY_NOVEL_NOT_ESTABLISHED` |

---

## 2. Distinction of Physical Objects

To prevent category errors across literature comparisons:

1. **Vorticity Vector Alignment**: Angle between 1D vector $\omega$ and Eulerian strain eigenvectors $e_i$.
2. **Passive Scalar Gradient Alignment**: Angle between $\nabla \theta$ and strain eigenvectors $e_i$ (governed by advection-diffusion without vortex stretching).
3. **Vorticity Gradient Tensor Orientation ($p_i$)**: Distribution of the 3D vector gradient energy $\nabla \omega_k$ across the right singular frame $v_i$ of the time-integrated stochastic deformation $D_s$.
4. **Finite-Time Deformation Frame ($v_i$)**: Nonlocal time-integrated principal axes of $\Gamma_s = D_s^T D_s$, distinct from instantaneous strain eigenvectors $e_i$.

No previous literature surveyed equates or derives the exact balance $\partial_s \ln \chi_s = \frac{2\nu \mathbb{E}[\|J_\omega\|^2 \sum p_i \sigma_i^2]}{|\omega(T)|^2 + V_s}$ in the context of Navier–Stokes singularity exclusion.
