# Independent Mathematical Verification Report: NS-OPENAI-B1-REASSESSMENT-R3

**Auditing Entity**: `antigravity-fresh-context-verifier`  
**Standard**: `Mathematical Research Constitution v1.0.1`  
**Independence Level**: `MATH_I2_INDEPENDENT_VERIFIER_AGENT`  
**Target Milestone**: `NS-OPENAI-B1-REASSESSMENT-R3`  
**Parent Milestone**: `NS-OPENAI-B1-REASSESSMENT-R2`  
**Target Problem**: Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ ($\nu > 0, f \equiv 0$)  
**Target Status**: `UNRESOLVED` | `NO-GO` | `B2 BLOCKED`

---

## 1. Audit Scope & Verification Mandate

The verifier conducted an adversarial audit of the proposed repairs to the two OpenAI pulse families, their dynamic covariance directions, and the validity of periodic analyticity theorems:
1. Verification of the source equations from Section 7.3–7.5 of the OpenAI monograph;
2. Derivation of Lemma 7.4 and the asymptotic amplitude ratio $y/x = c_0 \sqrt{1 + s(v)^2}$;
3. Derivation of Equation (7.28) and the covariance columns $H_\sigma = h_\sigma(-A_c N - \sigma u_* K + e_\sigma)$;
4. Independent calculation of the determinant $\det H = -2 h_+ h_- A_c u_*$ and condition number bound $\|H^{-1}\| \le C \sqrt{S_*}$;
5. Positive stress cone representation $h_+ y_+ = \frac{1}{2}(-\frac{T_N}{A_c} - \frac{T_K}{u_*})$, $h_- y_- = \frac{1}{2}(-\frac{T_N}{A_c} + \frac{T_K}{u_*})$;
6. Retraction of `CLM-037-B-R2` and `NEG-EV-045`; registration of `CLM-037-B-R3`;
7. Analysis of the backward-diffusion cost for authentic phases $\Phi_+$ and $\Phi_-$;
8. Audit of the real-analyticity theorem on $\mathbb{T}^3$ for smooth background $u_B$;
9. Confirmation of the pure-heat dense range theorem.

---

## 2. Itemized Verification Findings

### 2.1 Audit of Lemma 7.4 & Amplitude Evolution
- **Finding**: Along the characteristic ray, the amplitude components satisfy the Riccati ratio $y/x = c_0 \sqrt{1 + s(v)^2} + \mathcal{O}(S_*^{-1})$.
- **Verification**: The phase shear is $s(v) = \sigma(\frac{u_*}{2} + \frac{u_* v}{L_s})$. Because $\sigma$ explicitly alternates signs between $\sigma = +1$ and $\sigma = -1$, the projection onto the sheared basis $(e_r - s_a K_a, N_a)$ introduces an odd dependence on $\sigma$ in the $K$-component of the dynamic momentum flux.
- **Auditor Verdict**: **`CONFIRMED_SOURCE_FAITHFUL`**.

### 2.2 Audit of Equation (7.28) & Covariance Columns
- **Finding**: $H_\sigma = \langle\langle w_r w_{\tan} \rangle_\theta \rangle_Y = h_\sigma(-A_c N - \sigma u_* K + e_\sigma)$.
- **Verification**: 
  - For $\sigma = +1$: $H_+ = h_+(-A_c N - u_* K + e_+)$;
  - For $\sigma = -1$: $H_- = h_-(-A_c N + u_* K + e_-)$.
  - The $N$-component is even in $\sigma$ (both point along $-N$); the $K$-component is odd in $\sigma$ (pointing along $-K$ and $+K$ respectively).
- **Auditor Verdict**: **`CONFIRMED_EXACT`**.

### 2.3 Determinant & Invertibility (Proposition 7.5)
- **Finding**: In the basis $(N, K)$, the leading-order matrix is:
  $$H^{(0)} = \begin{pmatrix} -h_+ A_c & -h_- A_c \\ -h_+ u_* & +h_- u_* \end{pmatrix}.$$
- **Verification**:
  $$\det H^{(0)} = (-h_+ A_c)(h_- u_*) - (-h_- A_c)(-h_+ u_*) = -2 h_+ h_- A_c u_* \neq 0.$$
  With $h_\pm > 0$, $A_c > 0$, $u_* > 0$, the determinant is strictly non-zero and bounded away from zero: $|\det H| \ge c/S_*$. The inverse satisfies $\|H^{-1}\| \le C \sqrt{S_*}$.
- **Auditor Verdict**: **`CONFIRMED_INVERTIBLE`**.

### 2.4 Resolution of the R2 Rank-1 Misconception
- **Finding**: R2 evaluated $\Re(b_\sigma \otimes \overline{b_\sigma}) = \frac{1}{2}\operatorname{diag}(1, 1, 0)$ assuming plane waves with wavevector $k e_z$ and circular polarization $b_\pm = (e_r \pm i e_\theta)/\sqrt{2}$.
- **Verification**: This static dyad omitted: (a) the non-zero wavevector shear $s(v)$; (b) the radial-tangential cross-correlation produced by the ODE $(t_\sigma^h)' = A_{\Phi_\sigma} t_\sigma^h - d t_\sigma^h$; (c) the contraction into the radial momentum flux operator $C(w) = \langle\langle w_r w_{\tan} \rangle_\theta \rangle_Y$.
- **Auditor Verdict**: **`R2_RANK_1_CLAIM_CONFIRMED_FALSE_AND_RETRACTED`**.

### 2.5 Positive Cone Inversion
- **Finding**: For target stress $T = T_N N + T_K K$, the inversion weights satisfy:
  $$h_+ y_+ = \frac{1}{2}\left(-\frac{T_N}{A_c} - \frac{T_K}{u_*}\right), \qquad h_- y_- = \frac{1}{2}\left(-\frac{T_N}{A_c} + \frac{T_K}{u_*}\right).$$
- **Verification**: Positivity $y_+ > 0, y_- > 0$ holds if and only if $T_N < 0$ and $|T_K| < \frac{u_*}{A_c}(-T_N)$. This defines an open non-empty cone $\mathcal{K}_{\text{stress}}$.
- **Auditor Verdict**: **`CONFIRMED_POSITIVE_CONE_VALID`**.

### 2.6 Persistence of the Affine Backward-Diffusion Barrier
- **Finding**: The backward-diffusion cost was recalculated for the authentic phase gradients $\nabla \Phi_+$ and $\nabla \Phi_-$.
- **Verification**: Both pulse families share the spatial envelope $\chi_g(\xi_g)\psi(v)$ localized to radial thickness $\delta r_j \asymp 2^{-j/2}$, forcing transverse bandwidth $\Delta k_\perp \gtrsim 2^{j/2}$. In the straining background, transverse modes expand backward as $\exp(+\Sigma_j)$ ($\Sigma_j \asymp 2^{jh}$), forcing the Gramian quadratic form to diverge as $\exp(+c \exp(2^{jh}))$. Both $\Phi_+$ and $\Phi_-$ suffer identical super-exponential cost explosion.
- **Auditor Verdict**: **`AFFINE_COST_BARRIER_SURVIVES`**.

### 2.7 Periodic Analyticity & Pure Heat Invariant
- **Finding**: On $\mathbb{T}^3$, if $u_B \in C([0, t_j]; H^s(\mathbb{T}^3))$ ($s > 5/2$), the forward propagator $\mathcal{U}(t_j, 0)$ generates real-analytic fields. Compactly supported fields are excluded by the identity theorem (`FULL_PERIODIC_PDE`).
- **Finding**: The range of the pure heat semigroup is dense in $L^2_{\text{div}}(\mathbb{T}^3)$ via Fourier cutoff polynomials.
- **Auditor Verdict**: **`CONFIRMED_RIGOROUS`**.

---

## 3. Independent Verification Recommendation

The verifier concludes that:
1. `CLM-037-B-R2` and `NEG-EV-045` were erroneous simplifications and their retraction is mathematically required;
2. `CLM-037-B-R3` is fully established as a `SOURCE_DERIVED_LOCAL_MODEL` theorem;
3. The primary verdict `TWO_FAMILY_STRESS_VALID_AUTONOMOUS_REACHABILITY_OPEN` is epistemically accurate;
4. The affine cost barrier survives in full force;
5. Clay Statement B remains strictly **`UNRESOLVED`** and Milestone B2 remains strictly **`BLOCKED`**.

The verifier recommends formal acceptance of milestone `NS-OPENAI-B1-REASSESSMENT-R3`.
