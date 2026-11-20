# TP2-G3: NEGATIVE EVIDENCE & SCIENTIFIC DISCLOSURE

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Mandatory Negative Evidence Disclosure  

---

## 1. What Did Not Pass / What Was Falsified

1. **Falsification of Universal Viscous Decoherence**:
   The conjecture that viscosity $\nu > 0$ alone is sufficient to force stochastic Cauchy decoherence ($\chi < 1$) is **FALSE**.
   In any flow region where vorticity is spatially uniform ($J_\omega = 0$, such as plane Couette shear flow), the noise matrix $\Sigma \equiv 0$, covariance $C_s \equiv 0$, variance $V_s \equiv 0$, and $\chi_s \equiv 1$ identically, despite $\nu > 0$.
2. **Failure of Monotonicity to Provide a Regularity Closure**:
   While $\chi_s$ monotonically decreases backward in time ($\partial_s \chi_s \ge 0$), this monotonicity is purely a consequence of the non-negativity of Itô quadratic variation ($\int \Sigma \Sigma^T dr \succeq 0$). It does **not** provide any lower bound on the rate of decoherence.
3. **No A-Priori Lower Bound on Variance Growth**:
   Navier–Stokes a-priori energy estimates do not bound $\mathbb{E}[\|D_r J_\omega\|_F^2]$ from below. Without geometric or critical assumptions, stochastic cancellation cannot be proved to outgrow deformation amplification near potential singularities.

---

## 2. Technical Boundaries & Limitations

1. **Smoothness Requirement**:
   The derivation of $d_s Z_s$ requires $u \in C([0, T]; C^2)$ so that the flow map $A_s$ is a $C^1$ diffeomorphism. The formulas cannot be evaluated on generic Leray weak solutions without higher regularity.
2. **Boundary Terms Excluded**:
   All formulas assume $\mathbb{T}^3$ or whole-space $\mathbb{R}^3$ with zero boundary flux. Domains with physical boundaries generate additional local-time boundary vorticity integrals (Constantin & Iyer 2011) that are not covered in this gate.
3. **$\chi$ Is Not an Independent Degree of Freedom**:
   At fixed terminal $(x, T)$, $\chi_s$ is algebraically determined by $V_s$.
