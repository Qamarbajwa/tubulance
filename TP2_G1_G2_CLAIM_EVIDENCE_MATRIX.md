# TP2-G1 / G2: CLAIM–EVIDENCE MATRIX & PRIMARY SOURCE COMPARISON

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gates:** `TP2-G1 (Convention)` & `TP2-G2 (Scaling)`  
**Cutoff Date:** 24 August 2026  
**Governance:** Mid-Project Governance v2.9  

---

## 1. Primary Source Verification Table

| Primary Source | Exact Result / Formula | Specific Assumptions | Nature of Inclusion | Publication Status | Gate Relevance & Verdict |
|---|---|---|---|---|---|
| **Constantin & Iyer (2008)**, CPAM 61, 330–345 | $u = \mathbf{P} \mathbb{E}[(\nabla A)^T u_0(A)]$; $\omega = \mathbb{E}[(\nabla A)^{-1} \omega_0(A)]$ (Theorem 2.1, Section 3) | Smooth solution on $\mathbb{R}^3$ or $\mathbb{T}^3$; $C^2$ stochastic diffeomorphism | Quoted and verified algebraically | Published (Peer-reviewed) | Direct basis for $D_t^s(x) = (\nabla_x A)^{-1} = F(A(x))$. |
| **Constantin & Iyer (2011)**, Ann. Appl. Probab. 21 | Stochastic Lagrangian formulation in bounded domains with boundary vorticity generation | Smooth bounded domain, normal/tangential boundary decomposition | Quoted / referenced | Published (Peer-reviewed) | Confirms representation generalizability; whole-space/torus baseline is self-contained. |
| **Eyink, Gupta & Zaki (2020)**, JFM Parts I & II | Stochastic Cauchy invariant $Z(s) = \nabla X(s,t) \cdot \omega(X(s,t), s)$ with conserved mean and growing variance | Smooth DNS flow fields; backward Itô integration | Quoted and compared | Published (Peer-reviewed) | Directly confirms $Z_s^{x,t}$ structure and physical relevance of stochastic cancellation. |
| **Galeati (2025)**, J. Math. Pures Appl. 200, 103723 | Trajectory uniqueness for Lebesgue-a.e. initial condition for any Leray solution ($u_0 \in L^2$); everywhere for $u_0 \in H^{1/2}$ | Incompressible Leray weak solutions; stochastic regularization by noise | Quoted and sharply bounded | Published (Peer-reviewed) | Establishes trajectory uniqueness but **does not provide flow differentiability** $\nabla_x A$. |
| **Mahithitarmmatorn (2026)**, arXiv:2608.16915 | Closed deterministic mean/covariance equations for stochastic Weber field; quotient criterion equivalent to Serrin; counterexample to $\|\mathbb{E}D\| \sim \mathbb{E}\|D\|$ | Smooth NS on $\mathbb{T}^3$; Constantin–Iyer Weber representation | Quoted and analyzed | Preprint (24 Jul 2026) | Demonstrates covariance necessity and confirms that taking norms inside $\mathbb{E}$ destroys critical cancellation. |

---

## 2. Claim-by-Claim Evidence Assessment for TP2 Foundation

1. **Claim: Representation Formula Equivalence**
   - *Status*: **VERIFIED EXACT**.
   - *Evidence*: Symbolic proof in SymPy and analytical derivation in `TP2_G1_FORWARD_BACKWARD_EQUIVALENCE.md` confirm $\nabla_x \times ((\nabla A)^T v(A)) \equiv (\nabla A)^{-1} (\nabla \times v)(A)$.
2. **Claim: Matrix Multiplier in Vorticity Formula**
   - *Status*: **VERIFIED EXACT**.
   - *Evidence*: $D_t^s(x) = F_{s,t}(A_{s,t}(x)) = (\nabla_x A_{s,t}(x))^{-1}$. The transpose appears only in the Weber 1-form/velocity formula.
3. **Claim: Navier–Stokes Scaling Invariance of $\chi$**
   - *Status*: **VERIFIED EXACT**.
   - *Evidence*: Derived in `TP2_G2_SCALING_AUDIT.md` and confirmed in `tests/test_tp2_g1_g2_suite.py`. Exponent $[\chi] = \lambda^0$.
4. **Claim: Regularity Implication of $\chi \le 1$**
   - *Status*: **FALSIFIED AS A REGULARITY THEOREM**.
   - *Evidence*: $\chi \le 1$ holds by Cauchy–Schwarz for all random vectors. It provides no regularity control unless coupled with scale-critical dimensional norms.
5. **Claim: Extension to Generic Leray Solutions**
   - *Status*: **QUARANTINED / LOW-REGULARITY BOUNDARY ENFORCED**.
   - *Evidence*: Galeati 2025 provides trajectory uniqueness without $W^{1,p}$ or $C^1$ flow differentiability. Generic Leray solutions cannot support $D_t^s(x)$ without higher regularity.

---

## 3. Novelty Statement

**Zero novelty is claimed in this increment.**  
All representations and scaling properties are established from primary literature (Constantin–Iyer 2008, Eyink et al. 2020, Galeati 2025, Mahithitarmmatorn 2026) and classical differential geometry/probability theory.
