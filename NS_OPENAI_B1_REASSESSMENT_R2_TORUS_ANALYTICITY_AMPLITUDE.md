# Torus Compatibility, Analyticity, and Gaussian Amplitude Audits

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R2`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`  
**Classification**: `PROSPECTIVE_CORRECTION`  
**Sections**: R2 Sections 6 (Torus), 7 (Analyticity), 8 (Gaussian amplitude)

---

## 1. Torus Compatibility Audit (Section 6)

### 1.1 The Problem

The affine background flow $u_B(x, t) = A(t) x$ is **not periodic** on $\mathbb{T}^3 = (\mathbb{R}/2\pi\mathbb{Z})^3$. The function $x \mapsto A(t) x$ is multi-valued on the torus unless $A(t) = 0$.

Consequently, every theorem proved in the exact affine setting describes a **local** phenomenon near the filament center, not a global periodic PDE result.

### 1.2 Classification of Existing Results

| Result | Setting | Classification |
|--------|---------|----------------|
| Kelvin wave de-shearing (CLM-037-A) | Affine $u_B = A(t)x$ on $\mathbb{R}^3$ | **EXACT_AFFINE_BENCHMARK** |
| Gramian eigenvalues $\lambda_1, \lambda_\perp$ | Affine strain, constant $\sigma_j$ | **EXACT_AFFINE_BENCHMARK** |
| Admissible needle $P_j$ | Affine strain | **EXACT_AFFINE_BENCHMARK** |
| Two-family stress cone (CLM-037-B) | Affine strain, $\dim(E_{\mathrm{comp}}) = 1$ | **EXACT_AFFINE_BENCHMARK** |
| Q1 analytic smoothing no-go | Full Navier–Stokes on $\mathbb{T}^3$ | **FULL_PERIODIC_PDE** |
| Q2 cost divergence | Affine Gramian + uncertainty | **EXACT_AFFINE_BENCHMARK** |
| Q3 stress delocalization | Affine Gramian + Gaussian tails | **EXACT_AFFINE_BENCHMARK** |
| CLM-038 barrier theorem | Affine strain background | **EXACT_AFFINE_BENCHMARK** |

### 1.3 What Would Be Needed for FULL_PERIODIC_PDE

To promote affine results to full periodic PDE results, one would need:

1. **Local approximation argument**: On scales $\ell \ll 1$, the actual NS background near the filament is well-approximated by affine flow. This requires bounding:
   $$\|u_B(x, t) - A(t)(x - x_0)\|_{C^1(B(x_0, \ell))} \leq \delta \cdot \|A(t)\| \cdot \ell$$
   for $\delta \ll 1$ and $\ell \asymp \delta r_j \asymp 2^{-j/2}$.

2. **Perturbation stability**: The Gramian eigenvalue computation must be stable under $C^1$ perturbations of $A(t)$. Specifically, one needs:
   $$\left| \lambda_\perp^{\mathrm{true}} - \lambda_\perp^{\mathrm{affine}} \right| \leq \delta' \cdot \lambda_\perp^{\mathrm{affine}}$$
   for some small $\delta' > 0$.

3. **Periodicity-compatible localization**: The pulse envelope $\chi_j$ must be well-defined on $\mathbb{T}^3$, not just on $\mathbb{R}^3$. For $\delta r_j \asymp 2^{-j/2} \to 0$, this is eventually satisfied since the support fits inside a fundamental domain.

### 1.4 Current Status

Item 3 is straightforward for $j$ large. Items 1 and 2 have **not been rigorously established** in the current project. The OpenAI construction itself works in local self-similar coordinates, so the same gap exists there.

**Assessment**: The affine benchmark captures the correct local physics, and the barrier is expected to survive promotion. But this is an **expectation**, not a theorem. Classification: **EXACT_AFFINE_BENCHMARK_WITH_EXPECTED_LOCAL_VALIDITY**.

---

## 2. Analyticity Audit (Section 7)

### 2.1 Pure Heat Analyticity

**Theorem 2.1 (Pure Heat Analytic Smoothing)**:  
For the heat equation $\partial_t w - \nu \Delta w = 0$ on $\mathbb{T}^3$ with $w_0 \in L^2(\mathbb{T}^3)$, the solution $w(t) = e^{\nu t \Delta} w_0$ is real-analytic in $x$ for all $t > 0$, with radius of analyticity:
$$\rho(t) = \sqrt{2\nu t}.$$

**Proof**: The Fourier coefficients satisfy $|\widehat{w}(k, t)| = |\widehat{w_0}(k)| e^{-\nu t |k|^2}$. For any $\sigma < \sqrt{2\nu t}$:
$$\sum_k |\widehat{w}(k, t)|^2 e^{2\sigma |k|} \leq \sum_k |\widehat{w_0}(k)|^2 e^{-2\nu t |k|^2 + 2\sigma |k|} < \infty,$$
since the exponent $-2\nu t |k|^2 + 2\sigma |k| \to -\infty$ as $|k| \to \infty$. This is the Gevrey-$1$ regularity characterization.  
$\square$

This is **unconditional** — it holds for any $L^2$ initial data, on $\mathbb{T}^3$, with no coefficient regularity issues.

### 2.2 Variable-Coefficient Parabolic Equations

For the linearized Navier–Stokes equation:
$$\partial_t w + \mathbb{P}[(u_B \cdot \nabla)w + (w \cdot \nabla)u_B] - \nu \Delta w = 0,$$
where $u_B$ is a smooth time-dependent background flow.

**Correct statement**: If $u_B \in C^\infty([0, T] \times \mathbb{T}^3)$, then by the Foias–Temam (1989) theory, the solution $w(t)$ is indeed real-analytic in $x$ for $t > 0$, with a radius of analyticity satisfying:
$$\rho(t) \geq c(\nu, \|u_B\|_{L^\infty_t H^1_x}) \cdot \min(\sqrt{\nu t}, 1) > 0.$$

This result requires:
- $u_B$ is **smooth** (at minimum $C^1$ in space, continuous in time)
- The domain is $\mathbb{T}^3$ (compact, no boundary)
- $\nu > 0$ strictly

### 2.3 What Cannot Be Claimed

1. **Singular coefficients**: If $u_B$ has blow-up-type singularity (e.g. $\|u_B(t)\|_{H^1} \to \infty$ as $t \to T^\star$), the radius of analyticity $\rho(t)$ may shrink to zero, and the analytic smoothing result degrades.

2. **Affine flow coefficients**: The affine flow $u_B = A(t)x$ has $\|u_B\|_{H^1} \asymp \|A(t)\|$ which is bounded on each compact time interval. So the Foias–Temam result DOES apply on compact intervals away from the putative singularity. But near the singularity time $T^\star$, $\|A(t)\|$ diverges and the radius of analyticity may collapse.

3. **Key distinction**: The Q1 no-go (Theorem 3.1 of the R1 three-questions document) uses the identity theorem for real-analytic functions. This requires only that $w(t_j)$ be analytic at one specific time $t_j < T^\star$. Since $t_j < T^\star$ and $u_B$ is smooth on $[0, t_j]$, the Foias–Temam result applies at $t_j$. The Q1 result is **correctly stated** for the FULL_PERIODIC_PDE setting.

### 2.4 Corrected Classification

| Claim | Analyticity Basis | Status |
|-------|-------------------|--------|
| Q1 exact no-go for compact profiles | Foias–Temam on $[0, t_j]$ with smooth $u_B$ | **VALID_FULL_PERIODIC_PDE** |
| Gevrey-class radius $\rho(t) = \sqrt{2\nu t}$ | Pure heat only | **VALID_PURE_HEAT_BENCHMARK** |
| Variable-coefficient parabolic analyticity | Requires smooth $u_B$ on $[0, t_j]$ | **VALID_WITH_SMOOTHNESS_HYPOTHESIS** |

---

## 3. Gaussian Delocalization Amplitude Repair (Section 8)

### 3.1 The Error in R1

The R1 document (`NS_OPENAI_B1_REASSESSMENT_R1_ANALYTIC_PACKET_AND_STRESS_TAIL.md`, Section 3.2) claims:
$$\|C(W_j)\|_{L^\infty(r \geq 2r_j)} \asymp (A_j^\star)^2 \asymp 2^{j(1+2h)}.$$

This implicitly assumes the amplitude $A_j^\star$ is **maintained** even when the Gaussian width $\sigma_r$ is increased from $\delta r_j$ to $\sigma_r \gg \delta r_j$.

But if the wavepacket is $L^2$-normalized, increasing the width **decreases** the peak amplitude:

### 3.2 $L^2$-Normalized Gaussian Amplitude

For a Gaussian in cylindrical coordinates with radial width $\sigma_r$ and axial width $\sigma_z$:
$$W_j(r, z) = A_{\mathrm{peak}} \exp\left(-\frac{(r-r_j)^2}{2\sigma_r^2} - \frac{z^2}{2\sigma_z^2}\right) b_\pm e^{ik_j^\star z}.$$

The $L^2$ norm (ignoring $2\pi r$ Jacobian corrections for simplicity):
$$\|W_j\|_{L^2}^2 \asymp A_{\mathrm{peak}}^2 \cdot (\sqrt{2\pi} \sigma_r)^2 \cdot (\sqrt{2\pi} \sigma_z) \asymp A_{\mathrm{peak}}^2 \sigma_r^2 \sigma_z.$$

If we fix the target energy $\|W_j\|_{L^2}^2 = E_j \asymp 2^{-j(1/2 - 3h)}$ (the energy prescribed by the OpenAI construction), then:
$$A_{\mathrm{peak}}^2 \asymp \frac{E_j}{\sigma_r^2 \sigma_z}.$$

### 3.3 Two Scenarios

**Scenario A: Maintain amplitude, increase energy.**  
If we insist $A_{\mathrm{peak}} = A_j^\star \asymp 2^{j(1/2+h)}$ and widen to $\sigma_r \asymp 2^{-j/2} \exp(2^{jh})$:
$$\|W_j\|_{L^2}^2 \asymp (A_j^\star)^2 \sigma_r^2 \sigma_z \asymp 2^{j(1+2h)} \cdot 2^{-j} \exp(2 \cdot 2^{jh}) \cdot 2^{-j/2} \asymp 2^{j(2h - 1/2)} \exp(2 \cdot 2^{jh}).$$
This is **super-exponentially large** — the pulse energy diverges. This is physically impossible for a pulse that must be seeded from finite initial data.

**Scenario B: Fix energy, reduce amplitude.**  
If we fix $\|W_j\|_{L^2}^2 = E_j$ and widen to $\sigma_r \asymp 2^{-j/2} \exp(2^{jh})$ with $\sigma_z \asymp 2^{-j/2}$:
$$A_{\mathrm{peak}}^2 \asymp \frac{E_j}{\sigma_r^2 \sigma_z} \asymp \frac{2^{-j(1/2-3h)}}{2^{-j} \exp(2 \cdot 2^{jh}) \cdot 2^{-j/2}} = \frac{2^{j(1+3h-1/2)}}{\exp(2 \cdot 2^{jh})} = 2^{j(1/2+3h)} \exp(-2 \cdot 2^{jh}).$$
The peak amplitude **decays super-exponentially** to zero.

### 3.4 Corrected Exterior Stress Estimate

In Scenario B (energy-fixed, width-expanded), the exterior stress is:
$$\|C(W_j)\|_{L^\infty(r \geq 2r_j)} \asymp A_{\mathrm{peak}}^2 \asymp 2^{j(1/2+3h)} \exp(-2 \cdot 2^{jh}) \to 0.$$

This is **opposite** to the R1 claim! The exterior stress goes to zero, not infinity.

### 3.5 But the Interior Stress Also Vanishes

The flip side: the **interior core stress** needed for the blowup construction is:
$$\|C(W_j)\|_{L^\infty(\mathrm{core})} \asymp A_{\mathrm{peak}}^2 \asymp 2^{j(1/2+3h)} \exp(-2 \cdot 2^{jh}) \to 0.$$

The blowup construction requires interior core stress of order:
$$T^\star \asymp (A_j^\star)^2 \asymp 2^{j(1+2h)} \to +\infty.$$

The ratio of achieved to required stress is:
$$\frac{A_{\mathrm{peak}}^2}{(A_j^\star)^2} \asymp \frac{2^{j(1/2+3h)} \exp(-2 \cdot 2^{jh})}{2^{j(1+2h)}} = 2^{j(h-1/2)} \exp(-2 \cdot 2^{jh}) \to 0.$$

So the energy-normalized delocalized pulse produces **vanishing** stress — far too weak for the blowup construction.

### 3.6 Corrected Q3 Verdict

The R1 Q3 argument is **incorrect in its mechanism** but **correct in its conclusion**:

- R1 claimed: delocalized pulse produces **infinite** exterior stress that destroys the profile.
- R2 correction: delocalized pulse produces **vanishing** stress everywhere — too weak for the construction.

Either way, Q3 (stress reachability) fails. The failure mode is different:
- R1 narrative: "parasitic stress floods the exterior" (wrong for energy-normalized pulses)
- R2 correction: "achievable stress is super-exponentially weaker than required" (correct)

**The Q3 barrier survives in corrected form.**

---

## 4. Summary of Corrections

| Section | R1 Claim | R2 Correction | Impact on Barrier |
|---------|----------|---------------|-------------------|
| Torus (§6) | Implicit: results apply on $\mathbb{T}^3$ | Most results are EXACT_AFFINE_BENCHMARK; Q1 alone is FULL_PERIODIC_PDE | Barrier classification narrowed, conclusion unchanged |
| Analyticity (§7) | All parabolic evolutions give analytic solutions | True for pure heat and smooth-coefficient cases; degrades near singularity | Q1 no-go valid; no change to conclusion |
| Amplitude (§8) | Exterior stress $(A_j^\star)^2 \to \infty$ | For energy-normalized pulse, stress $\to 0$ everywhere | Q3 failure mechanism changes from "too much exterior stress" to "too little interior stress"; conclusion unchanged |
