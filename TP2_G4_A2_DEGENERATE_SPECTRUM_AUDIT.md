# TP2-G4-A2: DEGENERATE SPECTRUM & GAUGE-INVARIANT PROJECTOR AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2`  
**Governance Standard:** Autonomous Project Governance v2.9.4  
**Date:** 2026-08-25T00:27:00Z  

---

## 1. The Degeneracy Barrier in Eigenvector Tracking

When two or more singular values of the Cauchy–Green metric $\Gamma_s = D_s^T D_s$ coincide ($\sigma_i = \sigma_j$), the individual eigenvectors $v_i, v_j$ are non-unique and experience an $SO(2)$ gauge freedom. Attempting to differentiate $v_i(s)$ produces a zero denominator $\sigma_i^2 - \sigma_j^2 = 0$ in the classical perturbation series:
\[
\partial_s v_i = \sum_{j \neq i} \frac{v_j^T (\partial_s \Gamma_s) v_i}{\sigma_i^2 - \sigma_j^2} v_j.
\]
To maintain mathematical rigor and avoid manufacturing artificial rotational singularities, the theory must be formulated in terms of **gauge-invariant spectral subspace projectors**.

---

## 2. Classification of Spectral Regimes

We partition the spectrum of $\Gamma_s$ into three distinct regimes:

| Regime Code | Spectral Condition | Well-Posed Observables | Mathematical Status |
|---|---|---|---|
| `SIMPLE_SPECTRUM_REGIME` | $\min_{i \neq j} |\sigma_i^2 - \sigma_j^2| \ge \delta > 0$ | $P_1, P_2, P_3$, individual $p_1, p_2, p_3$ | Analytically differentiable |
| `NEAR_DEGENERATE_REGIME` | $0 < |\sigma_i^2 - \sigma_j^2| < \delta$ | Subspace projector $\mathcal{P}_{ij} = P_i + P_j$, combined weight $p_{ij} = p_i + p_j$ | Uniform resolvent bounds |
| `EXACT_DEGENERATE_SUBSPACE` | $\sigma_i = \sigma_j$ for $i \neq j$ | Invariant subspace projector $\mathcal{P}_\alpha$, total weight $p_\alpha = \operatorname{tr}(\mathcal{P}_\alpha M)$ | Gauge-invariant |

---

## 3. Gauge-Invariant Subspace Projector Formulation

Let $\Gamma_s$ have $m \le 3$ distinct eigenvalue clusters $\{\mu_\alpha\}_{\alpha=1}^m$ with multiplicities $d_\alpha$:
\[
\Gamma_s = \sum_{\alpha=1}^m \mu_\alpha \mathcal{P}_\alpha, \quad \mathcal{P}_\alpha := \sum_{i \in I_\alpha} P_i, \quad \sum_{\alpha=1}^m \mathcal{P}_\alpha = I.
\]
By Riesz Dunford spectral theory, the subspace projector is given by the contour integral of the resolvent:
\[
\mathcal{P}_\alpha = \frac{1}{2\pi i} \oint_{\mathcal{C}_\alpha} (z I - \Gamma_s)^{-1} dz,
\]
which remains $C^\infty$ with respect to $s$ even when individual eigenvalues within the cluster coalesce.

### 3.1 Clustered Projector Evolution Equation
Differentiating the resolvent identity yields the exact, well-posed subspace projector evolution:
\[
\boxed{ \partial_s \mathcal{P}_\alpha = \sum_{\beta \neq \alpha} \frac{\mathcal{P}_\beta (\partial_s \Gamma_s) \mathcal{P}_\alpha + \mathcal{P}_\alpha (\partial_s \Gamma_s) \mathcal{P}_\beta}{\mu_\alpha - \mu_\beta} }.
\]
This expression is non-singular because $\mu_\alpha \neq \mu_\beta$ for distinct clusters $\alpha \neq \beta$.

---

## 4. Invariance of Orientation Observables

The core physical quantities derived in Gate `TP2-G4` are rigorously invariant under arbitrary orthogonal rotations within degenerate eigenspaces:

1. **Quadratic Variation Integrand**:
\[
\|D_s J_\omega\|_F^2 = \operatorname{tr}(J_\omega^T \Gamma_s J_\omega) = \sum_{\alpha=1}^m \mu_\alpha \operatorname{tr}(J_\omega^T \mathcal{P}_\alpha J_\omega) = \|J_\omega\|_F^2 \sum_{\alpha=1}^m \mu_\alpha p_\alpha,
\]
where $p_\alpha := \operatorname{tr}(\mathcal{P}_\alpha M) = \sum_{i \in I_\alpha} p_i$.
2. **Orientation Factor $\mathcal{A}_{\text{grad}}$**:
\[
\mathcal{A}_{\text{grad}} = \sum_{\alpha=1}^m \mu_\alpha p_\alpha, \quad \sum_{\alpha=1}^m p_\alpha = \operatorname{tr}\left( \left(\sum_\alpha \mathcal{P}_\alpha\right) M \right) = \operatorname{tr}(M) = 1.
\]
3. **Orientation Efficiency $\eta$**:
\[
\eta := \frac{\mathcal{A}_{\text{grad}}}{\sigma_1^2} = \sum_{\alpha=1}^m \left( \frac{\mu_\alpha}{\mu_1} \right) p_\alpha \in (0, 1].
\]

### 4.1 Case Analysis
- **Fully Isotropic Limit ($\sigma_1 = \sigma_2 = \sigma_3 = 1$)**:
  $\Gamma_s = I$, $\mathcal{P}_1 = I$, $p_1 = 1$, $\mathcal{A}_{\text{grad}} = 1$, $\eta = 1.0$ identically.
- **Transversely Isotropic Limit ($\sigma_1 = \sigma_2 = K, \sigma_3 = K^{-2}$)**:
  $\mathcal{P}_{12} = I - v_3 v_3^T$, $p_{12} = \operatorname{tr}(\mathcal{P}_{12} M) = 1 - p_3$.
  \[
  \eta = p_{12} + (1 - p_{12}) K^{-6}.
  \]
  Thus $\eta$ is uniquely determined by $p_{12}$ and does not require resolving $v_1$ vs $v_2$.
