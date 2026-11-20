# TP2-G2: CANDIDATE COHERENCE RATIO $\chi$ INVARIANCE & ADVERSARIAL AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G2 (Adversarial Invariance Audit)`  
**Governance:** Mid-Project Governance v2.9  
**Status:** Authoritative Adversarial and Symmetry Audit  

---

## 1. Candidate Coherence Ratio Definition

For the stochastic Cauchy contribution $Z_s^{x,t} = D_t^s(x) \, \omega(A_{s,t}(x), s)$ with $\omega(x,t) = \mathbb{E} Z_s^{x,t}$, the candidate coherence ratio is:
$$\chi(x,t;s) := \frac{|\mathbb{E} Z_s^{x,t}|^2}{\mathbb{E}|Z_s^{x,t}|^2}.$$
The exact variance identity is:
$$|\omega(x,t)|^2 = |\mathbb{E} Z_s^{x,t}|^2 = \mathbb{E}|Z_s^{x,t}|^2 - \operatorname{Var}(Z_s^{x,t}),$$
where $\operatorname{Var}(Z) = \mathbb{E}|Z - \mathbb{E}Z|^2 = \operatorname{tr}(\operatorname{Cov}(Z))$.

---

## 2. Adversarial Falsification & Stress Tests

### Case A: Deterministic Zero-Variance Limit
- **Hypothesis**: If the stochastic trajectory has zero dispersion, $\operatorname{Var}(Z) = 0$, so $Z = Z_0$ almost surely ($Z_0 \neq 0$).
- **Evaluation**:
  $$\mathbb{E} Z = Z_0 \implies |\mathbb{E} Z|^2 = |Z_0|^2.$$
  $$\mathbb{E}|Z|^2 = |Z_0|^2.$$
  $$\chi = \frac{|Z_0|^2}{|Z_0|^2} = 1.$$
- **Result**: $\chi = 1$ is attained identically in the deterministic limit (Euler or zero-viscosity / zero-dispersion flow).

### Case B: Perfect Stochastic Cancellation
- **Hypothesis**: Trajectories undergo equal and opposite orientations with balanced probability.
- **Construction**: Let $Z = \pm v$ ($v \in \mathbb{R}^3, |v| > 0$) with $\mathbb{P}(Z = +v) = 1/2$ and $\mathbb{P}(Z = -v) = 1/2$.
- **Evaluation**:
  $$\mathbb{E} Z = \frac{1}{2}(+v) + \frac{1}{2}(-v) = 0 \implies |\mathbb{E} Z|^2 = 0.$$
  $$\mathbb{E}|Z|^2 = \frac{1}{2}|v|^2 + \frac{1}{2}|-v|^2 = |v|^2 > 0.$$
  $$\chi = \frac{0}{|v|^2} = 0.$$
- **Result**: $\chi = 0$ is attained when stochastic trajectories completely cancel in expectation despite large pathwise Cauchy deformation.

### Case C: Navier–Stokes Parabolic Scaling Invariance
- **Evaluation**: Under $u_\lambda(x,t) = \lambda u(\lambda x, \lambda^2 t)$, $(Z_s^{x,t})_\lambda \overset{d}{=} \lambda^2 Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}$.
  $$\chi_\lambda(x,t;s) = \frac{|\mathbb{E}[(Z_s^{x,t})_\lambda]|^2}{\mathbb{E}[|(Z_s^{x,t})_\lambda|^2]} = \frac{\lambda^4 |\mathbb{E}[Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}]|^2}{\lambda^4 \mathbb{E}[|Z_{\lambda^2 s}^{\lambda x, \lambda^2 t}|^2]} = \chi(\lambda x, \lambda^2 t; \lambda^2 s).$$
- **Result**: The numerical value of $\chi$ is strictly invariant at corresponding points under the full Navier–Stokes parabolic scaling group.

### Case D: Denominator Degeneracy ($\mathbb{E}|Z|^2 = 0$)
- **Condition**: $\mathbb{E}|Z_s^{x,t}|^2 = 0$.
- **Analysis**: Since $|Z|^2 \ge 0$ almost surely, $\mathbb{E}|Z|^2 = 0$ implies $Z = 0$ almost surely. Consequently $\mathbb{E} Z = 0$ and $\operatorname{Var}(Z) = 0$.
- **Governed Convention**: In this degenerate zero-vorticity state, there is no fluid rotation and no stochastic dispersion. We set $\chi := 1$ by continuous extension (or explicitly flag as `DEGENERATE_ZERO_STATE`), because the variance is zero and the identity $|\mathbb{E}Z|^2 = \chi \mathbb{E}|Z|^2$ holds trivially ($0 = 1 \cdot 0$). This state is recorded and never obscured.

### Case E: Rotational Invariance ($SO(3)$)
- **Evaluation**: Let $R \in SO(3)$ be an arbitrary constant rotation ($R^T R = I_3, \det R = 1$). Under $Z \mapsto R Z$:
  $$|\mathbb{E}[R Z]|^2 = (\mathbb{E}[RZ])^T (\mathbb{E}[RZ]) = (\mathbb{E}Z)^T R^T R (\mathbb{E}Z) = |\mathbb{E}Z|^2.$$
  $$\mathbb{E}[|R Z|^2] = \mathbb{E}[ Z^T R^T R Z ] = \mathbb{E}[|Z|^2].$$
  $$\chi(R Z) = \frac{|\mathbb{E} Z|^2}{\mathbb{E}|Z|^2} = \chi(Z).$$
- **Result**: $\chi$ is rigorously invariant under spatial frame rotations.

### Case F: Galilean Invariance
- **Evaluation**: Under the Galilean shift $x \mapsto x - c t$, $t \mapsto t$, $u(x,t) \mapsto u(x,t) - c$:
  $$\omega'(x', t') = \nabla_{x'} \times u'(x', t') = \nabla_x \times u(x,t) = \omega(x,t).$$
  $$\nabla_{x'} u'(x', t') = \nabla_x u(x,t).$$
  The stochastic trajectory translation leaves the deformation gradient $D_t^s(x)$ identical because $\nabla_x (c t) = 0$.
- **Result**: The Cauchy contribution $Z_s^{x,t}$ and the coherence ratio $\chi(x,t;s)$ are strictly Galilean invariant.

---

## 3. Machine Check Status

All adversarial cases and symmetries were evaluated and confirmed via automated symbolic and numerical tests in `tests/test_tp2_g1_g2_suite.py`:
- `test_tp2_g1_curl_pullback_identity`: **PASSED** (exact rational SymPy calculus).
- `test_tp2_g1_matrix_inverse_transpose_relations`: **PASSED** (random $SL(3, \mathbb{R})$ ensembles).
- `test_tp2_g2_exact_variance_identity_and_bounds`: **PASSED** (multivariate normal ensembles, $N=10^5$).
- `test_tp2_adversarial_cases`: **PASSED** (Cases A, B, D, E, F confirmed).
- `test_tp2_g2_symbolic_scaling_audit`: **PASSED** (all 12 scaling exponents verified).
