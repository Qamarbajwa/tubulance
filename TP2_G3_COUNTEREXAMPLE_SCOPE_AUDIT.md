# TP2-G3: COUNTEREXAMPLE DOMAIN SCOPE & NO-GO REFINEMENT

**Authority:** Independent E4 Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3`  
**Governance Standard:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Counterexample Scope Audit  

---

## 1. Domain Scope Audit of the Couette Counterexample

In the worker report `TP2_G3_COUNTEREXAMPLE_LEDGER.md`, plane Couette shear flow
$$u(x, y, z) = (S y, 0, 0), \quad \omega(x, y, z) = (0, 0, -S) = \text{const}$$
was used to claim:
$$\text{UNIVERSAL\_STRICT\_DECOHERENCE\_BY\_VISCOSITY = FALSE}.$$

### Domain Classification Discrepancy:
- The declared mathematical domain for TP2-G3 is:
  1. The periodic 3-torus $\mathbb{T}^3$; or
  2. The whole space $\mathbb{R}^3$ with smooth decaying energy fields ($u \in L^2(\mathbb{R}^3)$).
- Plane Couette shear flow is an **affine unbounded velocity field**:
  $$u \notin L^2(\mathbb{R}^3), \quad u \text{ is not periodic on } \mathbb{T}^3.$$
- Therefore, plane Couette flow cannot serve as an in-class counterexample within the restricted finite-energy periodic/decaying solution classes.

---

## 2. Refined Mathematical No-Go Statement

While Couette flow is outside the finite-energy class, it provides an exact algebraic sanity check demonstrating that viscosity $\nu > 0$ does not *algebraically* force quadratic variation in the absence of spatial gradients.

Within the declared class ($\mathbb{T}^3$ or decaying $\mathbb{R}^3$), the exact quadratic variation identity:
$$\frac{\partial}{\partial s} V_s = - 2\nu \, \mathbb{E}\left[ \| D_s J_\omega(A_s, s) \|_F^2 \right]$$
proves that variance production requires $J_\omega \neq 0$ on stochastic trajectories.

### Authoritative Refined Finding:
$$\boxed{\textbf{VISCOSITY\_ALONE\_DOES\_NOT\_ALGEBRAICALLY\_FORCE\_POSITIVE\_QUADRATIC\_VARIATION}}$$

**Formal Classification**:
`EXACT_SMOOTH_AFFINE_NS_SANITY_COUNTEREXAMPLE_OUTSIDE_DECLARED_ENERGY_DOMAIN`
*(Affirms that stochastic decoherence is fundamentally driven by spatial vorticity gradients $J_\omega$ rather than by the scalar parameter $\nu$ alone).*
