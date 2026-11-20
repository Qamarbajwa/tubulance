# TP2-G1: PRIMARY SOURCE FORMULA AUDIT

**Authority:** Independent Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Primary Source Register  

---

## 1. Primary Source Formula Register

| Source Reference | Specific Result / Equation | Original Paper Notation | TP2 Project Notation | Exact Formula Alignment | Mathematical Status |
|---|---|---|---|---|---|
| **Constantin & Iyer (2008)**, CPAM 61, 330–345 | Theorem 2.1, Section 2 (Weber Formula) | $u(x,t) = \mathbf{P} \mathbb{E}[ (\nabla X^{-1})^T u_0(X^{-1}) ]$ | $u(x,t) = \mathbf{P} \mathbb{E}[ (\nabla_x A_{0,t}(x))^T u_0(A_{0,t}(x)) ]$ | **IDENTICAL** | Published, peer-reviewed |
| **Constantin & Iyer (2008)**, CPAM 61, 330–345 | Section 3, eq (3.2) (Vorticity Representation) | $\omega(x,t) = \mathbb{E}[ (\nabla X(X^{-1})) \omega_0(X^{-1}) ]$ | $\omega(x,t) = \mathbb{E}[ F_{0,t}(A_{0,t}(x)) \omega_0(A_{0,t}(x)) ]$ | **IDENTICAL** | Published, peer-reviewed |
| **Eyink, Gupta & Zaki (2020)**, JFM 901, A2 (Part I) | Eq (2.3)–(2.4) (Stochastic Cauchy Invariant) | $Z(s) = \nabla \xi_s \cdot \omega(\xi_s, s); \quad \omega(x,t) = \mathbb{E} Z(s)$ | $Z_s^{x,t} = D_t^s(x) \omega(A_t^s(x), s); \quad \omega(x,t) = \mathbb{E} Z_s^{x,t}$ | **EQUIVALENT** ($\nabla \xi \equiv D$) | Published, peer-reviewed |
| **Galeati (2025)**, J. Math. Pures Appl. 200, 103723 | Theorem 1.1 & 1.4 (Leray Trajectory Uniqueness) | Pathwise uniqueness of $dX_t = u(X_t) dt + \sqrt{2\nu} dW_t$ for a.e. $x \in \mathbb{R}^3$ for $u_0 \in L^2$ | Unique stochastic trajectories $X_t(x)$ for a.e. $x$; flow differentiability excluded | **EQUIVALENT** | Published, peer-reviewed |
| **Mahithitarmmatorn (2026)**, arXiv:2608.16915 | Section 2, eq (2.1)–(2.6) (Weber Covariance & Norm Non-Equivalence) | Weber field $w = (\nabla A)^T u_0(A)$; $\|\mathbb{E}D\| \not\sim \mathbb{E}\|D\|$ | Weber covariance vs Vorticity Cauchy covariance; norm bound warning | **EQUIVALENT** | Preprint (24 Jul 2026) |

---

## 2. Rigorous Translation and Verification of Assumptions

1. **Constantin–Iyer (2008)**:
   - *Assumptions*: $u \in C([0, T]; C^k(\mathbb{R}^3))$ ($k \ge 2$), $\nabla \cdot u = 0$.
   - *Translation*: The mapping $a \mapsto X_{s,t}(a)$ is a $C^{k-1}$ stochastic diffeomorphism.
2. **Eyink–Gupta–Zaki (2020)**:
   - *Assumptions*: Smooth Navier–Stokes fields (evaluated via DNS and Monte Carlo stochastic trajectories).
   - *Translation*: $Z(s)$ is a martingaloid whose expectation is conserved in backward time $s$.
3. **Galeati (2025)**:
   - *Assumptions*: $u \in L_t^\infty L_x^2 \cap L_t^2 H_x^1$ (generic Leray weak solution).
   - *Translation*: Gives pathwise trajectory uniqueness, but explicitly **does not** imply Sobolev or Hölder differentiability of the stochastic flow map.
