# TP2-G6-B-R1: Mathematical Definition and Formal Hardening of Branch R

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R1 (Work Package 1)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Context and Objective

The stochastic-history scenario framework established in `TP2-G5-A4` proved that along any hypothetical blow-up sequence $(x_n, t_n)$ on $\mathbb{T}^3$, every subsequence possesses a further compactified subsequence realizing either:
- **Branch D (Decoherent / Dissipative):** $\limsup_{n \to \infty} J_n(a) > 0$ (yielding persistent relative variance and covariance trace lower bounds).
- **Branch R (Rigid / Persistent):** $\lim_{n \to \infty} J_n(a) = 0$ (relative variance vanishes, and normalized history integrals of $\Xi$ vanish).

The objective of Work Package 1 is to **harden the definition of Branch R** into an exact, unambiguous mathematical object so that any candidate flow family can be deterministically audited against it.

---

## 2. Rigorous Specification of the Branch-R Signature

Let $u$ be a smooth, divergence-free solution to the 3D incompressible Navier–Stokes equations on $\mathbb{T}^3 = [0, 2\pi)^3$ with kinematic viscosity $\nu > 0$ and zero external forcing $f = 0$.

### 2.1 Terminal State Sequence and Peak Vorticity
Let $\{(x_n, t_n)\}_{n=1}^\infty \subset \mathbb{T}^3 \times [0, T_*)$ be a sequence of space-time evaluation points with $t_n \nearrow T_* \le \infty$.  
Define the peak local vorticity amplitude:
\[
M_n := |\omega(x_n, t_n)| > 0.
\]
In a dangerous / hypothetical blow-up scenario, $\lim_{n \to \infty} M_n = \infty$.

### 2.2 Scale-Critical Intrinsic Lookback Window
For any fixed dimensionless parameter $a > 0$, define the **intrinsic lookback window**:
\[
L_n := \frac{a}{M_n}.
\]
The evaluation horizon is $[s_n, t_n]$ where the lookback start time is:
\[
s_n := t_n - L_n = t_n - \frac{a}{M_n}.
\]
*(Admissibility condition: $s_n \ge 0$, which holds for all sufficiently large $n$ when $M_n \to \infty$ or for sufficiently small $a$).*

### 2.3 Stochastic Lagrangian Dynamics and Backward Process
For each terminal point $(x_n, t_n)$ and lookback time $r \in [s_n, t_n]$, let $A_r = A_r(x_n, t_n)$ satisfy the backward stochastic differential equation:
\[
dA_r = -u(A_r, r) dr + \sqrt{2\nu} d\widehat{W}_r, \quad A_{t_n} = x_n,
\]
where $\widehat{W}_r$ is a backward standard 3D Brownian motion.  
Let $D_r = D_r(x_n, t_n) \in SL(3, \mathbb{R})$ be the Cauchy deformation tensor satisfying:
\[
\frac{d}{dr} D_r = -D_r (\nabla u)(A_r, r), \quad D_{t_n} = I.
\]
The backward Cauchy vorticity martingale vector is:
\[
Z_r := D_r \omega(A_r, r), \quad \mathbb{E}[Z_r \mid \mathcal{F}_{t_n}] = \omega(x_n, t_n).
\]

### 2.4 Physical Energy-Weighted Measure $\mu_r$
Define the expected Cauchy energy budget:
\[
S_r := \mathbb{E}\left[ |Z_r|^2 \right] = \mathbb{E}\left[ |D_r \omega(A_r, r)|^2 \right].
\]
On the non-degenerate domain $\{|Z_r| > 0\}$, the physical probability measure $d\mu_r$ is defined by:
\[
d\mu_r := \frac{|Z_r|^2}{S_r} d\mathbb{P}.
\]
Because $\int d\mu_r = \frac{\mathbb{E}[|Z_r|^2]}{S_r} = 1$, $\mu_r$ is a rigorous, normalized probability measure on paths.

### 2.5 Primary Relative Quadratic Variation Density $\Xi$
On $\{\omega \neq 0\}$, the Primary Relative QV Density is:
\[
\Xi_r := \frac{\|D_r J_\omega(A_r, r)\|_F^2}{|D_r \omega(A_r, r)|^2} = \frac{\|D_r J_\omega(A_r, r)\|_F^2}{|Z_r|^2}.
\]
- If $J_\omega(A_r, r) = 0$ while $\omega(A_r, r) \neq 0$, then $\Xi_r \equiv 0$ without singularity.
- The stopping time for the denominator is $\tau_{R} := \inf \{r \in [s_n, t_n] : |Z_r| = 0\}$. By backward uniqueness of smooth Navier–Stokes, $\tau_R < s_n$ almost surely when $M_n > 0$.

### 2.6 Dimensionless Accumulated Production $J_n(a)$
The total scale-critical relative quadratic variation production accumulated across the intrinsic window is:
\[
\boxed{ J_n(a) := 2\nu \int_{s_n}^{t_n} \mathbb{E}_{\mu_r}\left[ \Xi_r \right] dr }.
\]
By the exact scale-critical rate identity (`CLM-011`, `CLM-024`):
\[
\boxed{ J_n(a) = -\ln \chi_n(s_n) }, \quad \text{where} \quad \chi_n(s_n) := \frac{|\mathbb{E}[Z_{s_n}]|^2}{\mathbb{E}[|Z_{s_n}|^2]} = \frac{M_n^2}{S_{s_n}}.
\]
The relative stochastic variance of the vorticity vector is therefore algebraically exact:
\[
\frac{\operatorname{Var}(Z_{s_n})}{|\mathbb{E}[Z_{s_n}]|^2} = \frac{S_{s_n} - M_n^2}{M_n^2} = \frac{1}{\chi_n(s_n)} - 1 = \exp(J_n(a)) - 1.
\]

---

## 3. Mathematical Classification of Branch R

A sequence of evaluation states $\{(u^{(n)}, x_n, t_n)\}_{n=1}^\infty$ is said to **realize Branch R** at lookback scale $a > 0$ if and only if:
\[
\boxed{ \lim_{n \to \infty} J_n(a) = 0 }.
\]

### 3.1 Equivalent Formulations Along Branch R
The condition $\lim_{n \to \infty} J_n(a) = 0$ is mathematically equivalent to each of the following exact statements:
1. **Vanishing Coherence Loss:** $\lim_{n \to \infty} \chi_n(s_n) = 1$.
2. **Vanishing Relative Variance:** $\lim_{n \to \infty} \frac{\operatorname{Var}(Z_{s_n})}{\mathbb{E}[|Z_{s_n}|^2]} = 0$.
3. **Decoupled Amplitude & Direction Components:** Under the G5-A3 decomposition $\Xi = M_D + C_D$ (where $M_D \ge 0$ is magnitude stretching and $C_D \ge 0$ is directional alignment):
   \[
   \lim_{n \to \infty} \int_{s_n}^{t_n} \mathbb{E}_{\mu_r}[M_D(r)] dr = 0 \quad \text{and} \quad \lim_{n \to \infty} \int_{s_n}^{t_n} \mathbb{E}_{\mu_r}[C_D(r)] dr = 0.
   \]

### 3.2 The "Dangerous" Rigid Signature
In an adversarial attack, we seek to determine whether Branch R can coexist with severe, potentially singular vortex amplification:
\[
\boxed{ M_n = |\omega(x_n, t_n)| \to \infty \quad \text{with} \quad \lim_{n \to \infty} J_n(a) = 0 \quad \text{and} \quad \limsup_{n \to \infty} \frac{\omega(x_n, t_n) \cdot S(x_n, t_n) \omega(x_n, t_n)}{M_n^2} > 0 }.
\]
- If a smooth Navier–Stokes family realizes this signature, it proves that the scalar relative quantity $J_n(a) \to 0$ cannot detect or prevent violent nonlinear vortex stretching.
- If Navier–Stokes dynamics structurally forbids this signature, the obstruction isolates a candidate regularity lemma for Bridge $B_1$.

---

## 4. Separation of Exact, Asymptotic, and Heuristic Statements

| Level | Mathematical Statement | Epistemic Status |
|---|---|---|
| **Exact** | $J_n(a) = -\ln \chi_n = 2\nu \int_{s_n}^{t_n} \mathbb{E}_{\mu_r}[\Xi_r] dr$ is scale-invariant and algebraically exact on non-degenerate domains. | `PROVED_IDENTITY` |
| **Exact** | Parabolic rescaling $u_\lambda(x, t) = \lambda u(\lambda x, \lambda^2 t)$ leaves $J_n(a)$ strictly constant ($J^{(\lambda)}(a) \equiv J^{(1)}(a)$). | `PROVED_IDENTITY` |
| **Asymptotic** | Branch R is the compactified limit class defined by $J_{n_k}(a) \to 0$. | `RIGOROUS_DEFINITION` |
| **Asymptotic** | Branch R implies $\int_{s_n}^{t_n} \mathbb{E}_{\mu_r}[M_D] dr \to 0$ and $\int_{s_n}^{t_n} \mathbb{E}_{\mu_r}[C_D] dr \to 0$. | `PROVED_THEOREM` |
| **Conditional** | Pointwise smallness $\Xi(x_n, t_n) \to 0$ implies $J_n(a) \to 0$. | `FALSE / UNPROVED` (Requires history-integral control). |
| **Conditional** | $J_n(a) \to 0$ implies spatial directional coherence in an Eulerian neighborhood. | `FALSE / UNPROVED` (`NS-OBS-014`, `NS-OBS-015`). |
| **Heuristic** | "Rigid history prevents blow-up" or "Rigid history implies blow-up". | `HEURISTIC_PROHIBITED` (Neither statement is proved). |
