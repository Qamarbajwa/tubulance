# TP2-G6-C1: LITERATURE RECONCILIATION AND EXTERNAL EVIDENCE LEDGER

## Work Package WP14: Two-Particle Dispersion, Stochastic Flows, and Turbulence Theory

---

### 1. Purpose and Methodology

Under **Universal Governance Minimal v4.0.3** (Section 12) and **Mathematical Research Constitution v1.0.1** (Axiom AEV-1, Evidence Provenance), this document audits the external mathematical and physical literature on two-particle relative dispersion, stochastic flows of diffeomorphisms, and singular Lagrangian transport.

A crucial constitutional mandate for `TP2-G6-C1` is to **strictly separate rigorous mathematical theorems from empirical turbulence phenomenology**. Empirical laws (such as Richardson's $t^3$ dispersion law or Batchelor's ballistic/exponential regimes) cannot be imported as mathematical assumptions for generic Navier–Stokes solutions.

---

### 2. External Literature Audit Matrix

| Reference ID | Authors & Citation | Key Result / Phenomenological Law | Mathematical Hypotheses Required | Transfer Status to 3D NS Under Energy Bounds | Epistemic Assessment |
|---|---|---|---|---|---|
| **LIT-C1-01** | Kunita, H. (1984, 1990)<br>*Stochastic Flows and Stochastic Differential Equations*, Cambridge | Theory of stochastic flows of diffeomorphisms: $C^k$-differentiability of SDE flow maps | Drift $b \in C^{k, \alpha}$ (smooth/Lipschitz coefficients) | `LOCAL_ONLY_BLOCKED_AT_BLOWUP` | Rigorous foundation of Coupling C-SYNC and the first/second stochastic jets. Fails if $\|\nabla u\|_{L^\infty}$ blows up. |
| **LIT-C1-02** | Richardson, L. F. (1926)<br>*Proc. Roy. Soc. London A* 110: 709–737 | Empirical pair dispersion law: $\frac{d}{dt}\langle r^2 \rangle \propto r^{4/3} \implies \langle r^2 \rangle \sim \varepsilon t^3$ | Fully developed turbulence, inertial range scaling | `PHENOMENOLOGICAL_NO_DIRECT_TRANSFER` | Empirical scaling law in the inertial subrange. Not a theorem for generic Navier–Stokes solutions. |
| **LIT-C1-03** | Batchelor, G. K. (1950, 1952)<br>*Quart. J. Roy. Meteorol. Soc.* 76: 133–146 | Pair dispersion in viscous dissipation subrange: $\langle r^2(t) \rangle \sim r_0^2 e^{2\gamma t}$ | Smooth, uniform persistent strain rate $\gamma \sim (\varepsilon/\nu)^{1/2}$ | `MODEL_ONLY_CONDITIONAL_ON_STRAIN` | Describes pair separation under uniform persistent strain. Corresponds to C-SYNC with constant $\bar{S}$. Does not prove absence of blowup. |
| **LIT-C1-04** | Crippa, G. & De Lellis, C. (2008)<br>*J. Reine Angew. Math.* 616: 107–146 | Estimates and regularity for regular Lagrangian flows with $W^{1, p}$ drift | Divergence-free drift $b \in L^1_t W^{1, p}_x$ ($p > 1$) | `VALUABLE_ANALYTIC_FOUNDATION` | Provides rigorous logarithmic estimate: $\int \log(\frac{|X(t, x) - X(t, y)|}{|x-y|} + 1) dx dy \le C \|\nabla b\|_{L^1_t L^p_x}$. In 3D NS, energy drift has $p=2$, but only in $L^2_t$, requiring Cauchy–Schwarz in time. |
| **LIT-C1-05** | Bernard, D., Gawędzki, K. & Kupiainen, A. (1998)<br>*J. Stat. Phys.* 90: 519–569 | Spontaneous stochasticity: non-uniqueness of Lagrangian trajectories in rough drift | Rough velocity fields ($u \in C^\alpha$, $\alpha < 1$, e.g., Kraichnan model) | `INSIGHTFUL_LIMIT_THEORY` | Shows that for non-Lipschitz velocity fields, independent noise particles can separate even as initial separation $h \to 0$. Governs the inviscid/high-Re limit. |
| **LIT-C1-06** | Falkovich, G., Gawędzki, K. & Vergassola, M. (2001)<br>*Rev. Mod. Phys.* 73: 913–975 | Comprehensive review of particles and fields in turbulence | Kraichnan ensemble, delta-correlated in time | `HEURISTIC_PHYSICAL_BENCHMARK` | Provides exact solvable pair dispersion statistics for white-noise-in-time drifts. Real Navier–Stokes drift is nonlinearly self-correlated. |
| **LIT-C1-07** | Le Jan, Y. & Raimond, O. (2002, 2004)<br>*Ann. Probab.* 30(2): 826–873;<br>*Ann. Inst. H. Poincaré* 40: 427–450 | Integration of Brownian flows and coalescing stochastic flows | Correlated Brownian fields, smooth to rough transitions | `MATHEMATICAL_PROBABILITY_FRAMEWORK` | Formalizes the continuum between synchronous coupling (diffeomorphisms) and independent coupling (pair Markov diffusion). |
| **LIT-C1-08** | Constantin, P. & Iyer, G. (2008, 2011)<br>*Ann. Appl. Probab.* 18: 1336–1346 | Stochastic Lagrangian representation of Navier–Stokes | Classical smooth solutions | `CANONICAL_PROJECT_FOUNDATION` | Proves single-particle representation. C1 generalizes their single-particle flow to two-particle jets. |
| **LIT-C1-09** | Hajłasz, P. (1996)<br>*Potential Anal.* 5(4): 403–415 | Sobolev spaces on metric measure spaces via maximal functions | $u \in W^{1, p}$ ($p \ge 1$) | `NON_CIRCULAR_A_PRIORI_TOOL` | Proves $|u(x) - u(y)| \le C |x-y| (M|\nabla u|(x) + M|\nabla u|(y))$. Valid unconditionally at Navier–Stokes energy level. |

---

### 3. Separation of Rigorous Theory from Empirical Turbulence Laws

To enforce constitutional non-circularity, we formally partition the literature:

#### 3.1 What is Mathematically Admissible as Foundation
1. **Kunita Flow Theory**: For any smooth velocity field on $[0, T^*)$, the backward stochastic flow is a spatial diffeomorphism, and the first- and second-order jets ($D_s, H_s$) satisfy deterministic linear matrix ODEs along each Brownian path.
2. **Hajłasz–Sobolev Inequalities**: Velocity increments satisfy $|u(x+h) - u(x)| \le C |h| (M|\nabla u|(x) + M|\nabla u|(x+h))$ Lebesgue-almost-everywhere, with $M|\nabla u| \in L^2_t L^2_x$ bounded by initial kinetic energy $\mathcal{E}_0$.
3. **Plancherel / Energy Structure Functions**: $S_2(h, t) \le |h|^2 \|\nabla u(t)\|_{L^2}^2$ is an exact geometric identity.

#### 3.2 What is Strictly Prohibited as Premise
1. **Assuming Richardson $t^3$ Scaling**: Richardson scaling assumes a fully developed, self-similar turbulent cascade with Kolmogorov spectrum $E(k) \sim k^{-5/3}$. Assuming this for generic candidate blowup solutions of 3D Navier–Stokes is **strictly unproven and circular**.
2. **Assuming Batchelor Exponential Dispersion Without Strain Bounds**: Batchelor's exponential separation $r(t) \sim r_0 e^{\gamma t}$ assumes an unconditioned positive Lyapunov exponent $\gamma > 0$. Proving that the fluid Lyapunov exponent is strictly positive in generic 3D flows is an open problem in ergodic theory and fluid mechanics.

---

### 4. Novelty Assessment

In accordance with Section 21 of the prompt instructions:
- The exact derivations of the two-particle backward SDE, common-mode cancellation, the bilateral pullback jet formula $\Xi^{\text{pair}} = \frac{\|D_s J_\omega D_s + H_s : \omega\|_F^2}{|D_s \omega|^2}$, and the synchronous/independent duality dilemma are **novel within the audited Navier–Stokes persistence literature**.
- The novelty of these results is formally classified as:
  $$\boxed{\mathbf{N2\_NOT\_FOUND\_IN\_AUDITED\_SOURCES}}$$
- Under the Mathematical Research Constitution v1.0.1, internal agent review cannot promote this to external field novelty (`N3` / `N4`); it remains canonical at level `N2`.
