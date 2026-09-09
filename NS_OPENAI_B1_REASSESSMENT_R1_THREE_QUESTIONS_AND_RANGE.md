# Exact Parabolic Range, Analytic Smoothing, and the Three Reachability Questions

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R1`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`

---

## 1. Epistemic Separation: Three Distinct Questions

In assessing whether the unforced Navier–Stokes flow can generate an active pulse state at scale $j$, one must strictly separate three distinct mathematical questions:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Q1: EXACT PROFILE REACHABILITY                                                  │
│ Does W* lie in the exact range of the forward solution operator?                │
│ W* in Range(U(t_*, 0)) <==> exists w_0 in X such that U(t_*, 0) w_0 = W* exactly │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ (If Q1 fails, investigate Q2)
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Q2: APPROXIMATE PROFILE REACHABILITY                                            │
│ For a given epsilon > 0, does there exist w_0 in X with bounded norm such that  │
│ ||U(t_*, 0) w_0 - W*||_X <= epsilon?                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ (If Q2 fails or is too costly, investigate Q3)
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Q3: STRESS REACHABILITY                                                         │
│ Does there exist an unforced reachable state W = U(t_*, 0) w_0 such that the    │
│ resulting Reynolds stress matches the target core stress within tolerance:      │
│ ||C(W) - T*|| <= epsilon_stress, with acceptable exterior stress leakage?       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

A no-go verdict for Q1 (exact reachability) does **not** automatically establish a no-go for Q2 or Q3.
The true physical requirement of the blowup construction is **Q3 (Stress Reachability)**.

---

## 2. Exact Parabolic Range Theorem (Pure Heat Benchmark)

Consider pure heat diffusion on the flat torus $\mathbb{T}^3 = (\mathbb{R}/2\pi\mathbb{Z})^3$ with viscosity $\nu > 0$:
$$\partial_t w - \nu \Delta w = 0, \qquad w(0) = w_0 \in L^2(\mathbb{T}^3).$$
The solution is given by the Fourier series:
$$w(x, t) = \sum_{k \in \mathbb{Z}^3} \widehat{w_0}(k) e^{-\nu t |k|^2} e^{i k \cdot x}.$$

### 2.1 Characterization of the Exact Semigroup Range
**Theorem 2.1 (Exact Heat Range)**:
Let $t > 0$. A target velocity field $W^\star \in L^2(\mathbb{T}^3)$ belongs to $\operatorname{Range}(e^{\nu t \Delta})$ if and only if its Fourier coefficients satisfy:
$$\sum_{k \in \mathbb{Z}^3} e^{2\nu t |k|^2} |\widehat{W^\star}(k)|^2 < \infty.$$

### 2.2 Impossibility for Exactly Compactly Supported Targets
Suppose $W^\star(x)$ is a non-trivial smooth target state that is **identically zero** on an open set $U \subset \mathbb{T}^3$ (e.g. outside the annular filament $r \in [r_j - \delta r_j, r_j + \delta r_j]$).

By the classical Paley–Wiener–Schwartz theorem:
1. If $W^\star$ has compact spatial support, its Fourier transform $\widehat{W^\star}(\zeta)$ extends to an entire function of exponential type on $\mathbb{C}^3$.
2. By the Phragmén–Lindelöf principle, a non-zero entire function of exponential type cannot satisfy Gaussian decay in any real direction:
   $$\limsup_{|k| \to \infty} \frac{\ln |\widehat{W^\star}(k)|}{|k|^2} = 0.$$
   In particular, $|\widehat{W^\star}(k)|$ cannot decay faster than $\exp(-c |k|)$.
3. Consequently, for any $\nu t > 0$:
   $$\sum_{k \in \mathbb{Z}^3} e^{2\nu t |k|^2} |\widehat{W^\star}(k)|^2 = +\infty.$$

**Corollary 2.1 (Exact Reachability No-Go for Compact Targets)**:
No non-zero smooth function with compact spatial support belongs to $\operatorname{Range}(e^{\nu t \Delta})$ for any $t > 0$.

---

## 3. Instantaneous Analytic Smoothing for Linearized Navier–Stokes

Now consider the unforced linearized Navier–Stokes operator around a smooth background flow $u_B(x, t)$:
$$\partial_t w + \mathbb{P} \left[ (u_B \cdot \nabla)w + (w \cdot \nabla)u_B \right] - \nu \Delta w = 0, \qquad \nabla \cdot w = 0.$$

### 3.1 Spatial Analyticity of Parabolic Evolutions
By classical parabolic regularity theory (e.g. Foias–Temam 1989, Grujić–Kukavica 1998):
1. Because the leading-order operator is the Laplacian $-\nu \Delta$, the linearized solution operator $\mathcal{U}(t, 0)$ possesses **instantaneous spatial analytic smoothing**.
2. For any initial datum $w_0 \in L^2(\mathbb{T}^3)$ and any $t > 0$, the solution $w(t) = \mathcal{U}(t, 0)w_0$ is real-analytic in space ($w(t) \in C^\omega(\mathbb{T}^3)$).
3. The radius of spatial analyticity satisfies the parabolic lower bound:
   $$\rho(t) \ge c \min\left( \sqrt{\nu t}, 1 \right) > 0.$$

### 3.2 Identity Theorem for Real-Analytic Functions
By the principle of unique continuation for real-analytic functions on connected manifolds:
- If $f \in C^\omega(\mathbb{T}^3)$ vanishes identically on an open non-empty set $U \subset \mathbb{T}^3$, then $f \equiv 0$ on the entire torus $\mathbb{T}^3$.

### 3.3 The Rigorous Q1 Verdict
**Theorem 3.1 (Q1 Exact Compact Reachability No-Go)**:
Let $W_j^\star$ be any target pulse state that is compactly supported in an annular filament (so that $W_j^\star(x) = 0$ on an open exterior region).
Then:
$$\boxed{W_j^\star \notin \operatorname{Range}\left( \mathcal{U}(t_j, 0) \right)}.$$
Exact profile reachability is **mathematically impossible** for any strictly localized target pulse.

---

## 4. Transition to Quantitative Approximate Reachability (Q2 & Q3)

Because Q1 is definitively resolved as `NO-GO`, the scientific fate of the autonomous cascade depends entirely on:
1. **Q2**: Can an unforced initial state $w_0$ produce an approximate pulse $W(t_j)$ within $L^2$ error $\epsilon_j$?
2. **Q3**: Can a smooth, spatially non-compact pulse (such as a Gaussian or Gevrey packet with small analytic tails) reproduce the target Reynolds stress $T^\star$ within tolerance $\varepsilon_{\mathrm{stress}}$ without corrupting the exterior self-similar profile?

To answer Q2 and Q3, we must compute the exact diffusion Gramian $Q_{t_j}$ and evaluate quantitative uncertainty inequalities.
