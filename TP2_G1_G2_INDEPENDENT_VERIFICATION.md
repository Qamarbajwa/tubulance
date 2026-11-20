# TP2-G1 / G2: INDEPENDENT MATHEMATICAL VERIFICATION REPORT

**Authority:** Independent Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gates:** `TP2-G1 (Stochastic Conventions)` & `TP2-G2 (Exact Scaling Audit)`  
**Governance:** Mid-Project Autonomous Governance v2.9 (Tier T4)  
**Candidate Base SHA:** `2e9a4fb5dd6ddc5ec377328f9387c16acab1fe5f`  
**Status:** Authoritative Independent Verification  

---

## 1. Independent Executive Summary

The Independent Verification Authority has completed a mathematical, evidential, and adversarial audit of candidate artifacts for gates **TP2-G1** and **TP2-G2**.

The producing worker's candidate claims, derivations, tests, and self-issued `PASS` verdict were treated as `UNTRUSTED_CANDIDATE_EVIDENCE` and re-evaluated from scratch against primary literature (Constantin & Iyer 2008, 2011; Eyink, Gupta & Zaki 2020; Galeati 2025; Mahithitarmmatorn 2026).

---

## 2. Cryptographic and Artifact State Verification

| Candidate Artifact | SHA-256 Checksum | Size | Verification Status |
|---|---|---|---|
| `TP2_G1_STOCHASTIC_CONVENTION_CONTRACT.md` | `7bf415f1d31140ce3bf48f0a51c7f989a8473ade79a9014592e30491782e2184` | 7782 B | Confirmed |
| `TP2_G1_FORWARD_BACKWARD_EQUIVALENCE.md` | `4747b589d49a57147cf9ff973fb144bff5149e0870a2e7485489e38fdf720f31` | 5747 B | Confirmed |
| `TP2_G2_SCALING_AUDIT.md` | `cef186baacf3cd9fa48be5baee7190a058df0ec30fb2cc80adecc707e93718e2` | 6874 B | Confirmed |
| `TP2_G2_CHI_INVARIANCE_TESTS.md` | `9a1bc11c0b2eb181a43b2b08ad5bcf6a5cd5ee51af5496665da27c1418af7e3d` | 4965 B | Confirmed |
| `TP2_G1_G2_CLAIM_EVIDENCE_MATRIX.md` | `4948d896772c04ad672d3e3fbbd1424510413f9b5fd94122ac7efc836ca19ae6` | 4149 B | Confirmed |
| `TP2_G1_G2_NEGATIVE_EVIDENCE.md` | `b81e5267c73b4d4c5b36fc593b144a51cda2db5bb9c7b5ffcf57bfed56f84f2c` | 3295 B | Confirmed |
| `TP2_G1_G2_FINAL_REVIEW_PACKET.md` | `34fc5193885d396c76ad9334820972675b7917f630cd59f7a3abec265606554a` | 4863 B | Confirmed |
| `tests/test_tp2_g1_g2_suite.py` | `626c53b0733919c36a2e86e4b3f6069b21278cc6cfe39476f3080f67668cf8e1` | 6728 B | Confirmed |
| `TP2_LITERATURE_CLAIM_MATRIX_2026-08-23.md` | `22c073654ea21c62fb3f73ddf62341a4646d852818831c425e3e20cf285ccb40` | 29936 B | Authoritative Baseline |

---

## 3. Systematic Resolution of Challenges 1–10

### Challenge 1: Constantin–Iyer Forward Representation
- Forward trajectory starting at $a$ at time $s$:
  $$X_{s,t}(a) = a + \int_s^t u(X_{s,\tau}(a), \tau) d\tau + \sqrt{2\nu}(W_t - W_s), \quad t \ge s.$$
- Forward deformation gradient: $F_{s,t}(a) = \nabla_a X_{s,t}(a)$.
- Spatial inverse map: $A_{s,t}(x) = X_{s,t}^{-1}(x)$, so $X_{s,t}(A_{s,t}(x)) = x$.
- **Independent Result**: $\omega(x,t) = \mathbb{E}[ F_{s,t}(A_{s,t}(x)) \, \omega(A_{s,t}(x), s) ]$. Verified.

### Challenge 2: Backward Stochastic Cauchy Representation
- In Constantin & Iyer (2008), the inverse map $A_{s,t}(x)$ is the spatial inverse of the forward flow.
- In Eyink, Gupta & Zaki (2020), the backward trajectory $\xi_s(x) = A_{s,t}(x)$ is parameterized backward from terminal position $x$ at time $t$.
- The deformation matrix appearing in the vorticity representation $\omega(x,t) = \mathbb{E}[ D_t^s(x) \omega(A_t^s(x), s) ]$ is identically:
  $$D_t^s(x) = \left[ \nabla_x A_{s,t}(x) \right]^{-1} = F_{s,t}(A_{s,t}(x)).$$
- The transpose inverse $(\nabla_x A)^{-T} = F^{-T}$ belongs strictly to the **Weber 1-form/velocity representation** $u = \mathbf{P} \mathbb{E}[ (\nabla A)^T u_0(A) ]$, while the curl of the pullback converts the transpose-inverse into the direct inverse $(\nabla A)^{-1} = F$.

### Challenge 3: Equivalence & Conversion Crosswalk
- The forward-flow and backward-terminal formulations describe the **same physical and probabilistic object**.
- An exhaustive matrix conversion crosswalk is established in `TP2_G1_MATRIX_CONVENTION_CROSSWALK.md`.

### Challenge 4: Exact Curl / Cofactor Identity
- General identity: For any $C^2$ diffeomorphism $A: \mathbb{R}^3 \to \mathbb{R}^3$ and $C^1$ vector field $v$:
  $$\nabla_x \times \left( (\nabla_x A(x))^T v(A(x)) \right) \equiv (\det \nabla_x A(x)) \, (\nabla_x A(x))^{-1} (\nabla_a \times v)(A(x)).$$
- Tested on fully non-symmetric, non-diagonal, anisotropic 3D quadratic mappings with non-unit determinants: identity holds to exact symbolic precision ($0 \equiv 0$).

### Challenge 5: Stochastic Differential Equations & Multiplication Ordering
- For the forward deformation gradient $F_{s,t}(a) = \nabla_a X_{s,t}(a)$, spatial differentiation of $\nabla_a dW = 0$ leaves:
  $$\frac{d F}{dt} = (\nabla u) \, F, \quad F(s) = I_3.$$
- Multiplication order is **strictly left-multiplication by $\nabla u$**: $(\nabla u) F \neq F (\nabla u)$.
- For the backward inverse Jacobian $J(x,s) = \nabla_x A_{s,t}(x)$: $\frac{d}{ds} J = - J (\nabla u)$.

### Challenge 6: Low-Regularity Boundary (Galeati 2025 Barrier)
- Galeati (2025) proves trajectory uniqueness for Lebesgue-a.e. initial condition for any Leray solution ($u_0 \in L^2$).
- **Crucial Separation**: Trajectory uniqueness $\neq$ flow differentiability. Generic Leray solutions do not possess $C^1$ or $W^{1,p}$ regularity to define $\nabla_x A$ or $D_t^s(x)$.
- Constantin–Iyer representation is mathematically valid on classical/mild solution lifespans $[0, T^*)$ and must not be asserted for rough Leray solutions without higher regularity.

### Challenge 7: Scaling Reproduction from Scratch
- Under $u_\lambda(x,t) = \lambda u(\lambda x, \lambda^2 t)$:
  - Exponents: $[u]=1, [\omega]=2, [S]=2, [X]=-1, [A]=-1, [F]=0, [D]=0, [Z]=2, [\mathbb{E} Z]=2, [|\mathbb{E} Z|^2]=4, [\mathbb{E}|Z|^2]=4, [\operatorname{Var}(Z)]=4, [\chi]=0$.
  - Scaling invariance: $\chi_\lambda(x,t;s) = \chi(\lambda x, \lambda^2 t; \lambda^2 s) \implies [\chi] = \lambda^0$. Verified.

### Challenge 8: Candidate Coherence Ratio $\chi$ & Degeneracy Convention
- $\chi \in [0, 1]$ is verified by Cauchy–Schwarz.
- **Degenerate State Governance**: When $\mathbb{E}|Z|^2 = 0$, both vorticity $\omega(x,t) = 0$ and variance are zero. Canonical state is governed as:
  $$\boxed{\text{CHI\_UNDEFINED\_DEGENERATE\_ZERO\_STATE}}$$
  (with implementation shorthand $\chi := 1$ solely for the variance identity $0 = 1 \cdot 0$).

### Challenge 9: Test Suite Audit & Mutation Testing
- Test suite expanded to 9 fully independent tests across `tests/test_tp2_g1_g2_suite.py` and `tests/test_tp2_independent_verification.py`.
- 6 mutation tests executed against operator transposition, inversion, determinant omission, and scaling errors in `TP2_G1_G2_MUTATION_TEST_REPORT.json`.
- **Mutation Kill Rate**: 100% (6/6 mutants killed).

### Challenge 10: Primary Source Formula Audit
- Full audit completed and registered in `TP2_G1_PRIMARY_SOURCE_FORMULA_AUDIT.md`.
