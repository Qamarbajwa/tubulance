# Visual Research Companion: Two-Family Pulse Covariance & Stress Cone

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R3`  
**Standard**: `SOURCE_DERIVED_LOCAL_MODEL`  
**Mandate Section**: Section 20 Visual Research Companion  
**Classification**: `INFORMATIVE_VISUAL_ARTIFACT`

---

## Overview

This visual artifact resolves the geometric misconception in milestone `NS-OPENAI-B1-REASSESSMENT-R2` that led to the erroneous rank-1 inference (`CLM-037-B-R2`). The four panels below trace the authentic mechanics from Section 7 of the OpenAI monograph:
1. **Panel A**: Opposite helical phase wavefronts $\Phi_+$ and $\Phi_-$;
2. **Panel B**: Dynamic amplitude evolution and the ratio $y/x = c_0 \sqrt{1 + s(v)^2}$;
3. **Panel C**: The resulting distinct radial momentum flux vectors $H_+$ and $H_-$;
4. **Panel D**: The positive stress cone $\mathcal{K}_{\text{stress}}$ and target $T$ representation.

---

## Panel A: The Two Pulse Phases $\Phi_+$ and $\Phi_-$

In the cylindrical boundary-layer coordinates $(\theta, z)$, the phase functions are sheared by the background circulation $u_*$:
$$\Phi_\sigma(\theta, z) = \theta + \sigma \left( \frac{u_*}{2} + \frac{u_* z}{L_s} \right) \frac{z}{\ell_z} + \phi_0(r).$$

```
        WAVEFRONTS OF POSITIVE HELICITY (Φ+)             WAVEFRONTS OF NEGATIVE HELICITY (Φ-)
       z ▲                                              z ▲
         │     /       /       /                          │     \       \       \
         │    /       /       /                           │      \       \       \
         │   /       /       /                            │       \       \       \
         │  /       /       /                             │        \       \       \
         │ /       /       /                              │         \       \       \
       ──┼─────────────────────────► θ                  ──┼─────────────────────────► θ
         │ Wavevector: ∇Φ+ = (kr, 1/r, +k_z)              │ Wavevector: ∇Φ- = (kr, 1/r, -k_z)
         │ Sheared in direction of background swirl       │ Sheared against direction of background swirl
```

---

## Panel B: Evolved Radial and Tangential Amplitudes ($t_\sigma^h$)

Under the amplitude ODE $(t_\sigma^h)' = A_{\Phi_\sigma} t_\sigma^h - d t_\sigma^h$, the vector amplitude decomposes along $(e_r - s_a K_a, N_a)$ as:
$$t_\sigma^h = x(e_r - s_a K_a) + y N_a.$$

```
                                  DYNAMIC AMPLITUDE RATIO
                    y/x ▲
                        │                    y/x = c0 √(1 + s(v)²)
                    2.5 ┼                        *             *
                        │                       *               *
                    2.0 ┼                      *                 *
                        │                     *                   *
                    1.5 ┼                    *                     *
                        │                   *                       *
                    1.0 ┼                  *                         *
                        │       * * * * * *                           * * * * * *
                    0.5 ┼
                        │
                    ────┼─────────┬─────────┬─────────┬─────────┬─────────┬─────────► v
                       -3        -2        -1         0         1         2         3
                        │
                        │ Branch σ = +1: s+(v) = +(u*/2 + u*v/Ls)
                        │ Branch σ = -1: s-(v) = -(u*/2 + u*v/Ls)
```

The amplitude ratio $y/x$ is an even function of $s(v)$, but the tangential projection onto $K$ retains the odd sign $\sigma$.

---

## Panel C: Covariance Vectors $H_+$ and $H_-$

Evaluating $H_\sigma = \langle\langle w_r w_{\tan} \rangle_\theta \rangle_Y$ in the $(N, K)$ basis:
$$H_+ = h_+ (-A_c N - u_* K), \qquad H_- = h_- (-A_c N + u_* K).$$

```
                                   COVARIANCE VECTORS IN (N, K) PLANE
                                                 K ▲ (Shear axis)
                                                   │
                                                   │           H- = h-(-Ac N + u* K)
                                                   │          /
                                                   │         /
                                                   │        /  +u* K
                                                   │       /
                                                   │      /
                              -Ac N                │     /
              ◄────────────────────────────────────┼────┴────────────────────────► N (Normal axis)
                     \                             │
                      \                            │
                       \                           │
                        \  -u* K                   │
                         \                         │
                          \                        │
                           ▼                       │
                     H+ = h+(-Ac N - u* K)         │
                                                   │
```

Because $H_+$ has component $-u_* K$ and $H_-$ has component $+u_* K$, they point into opposite half-planes along $K$.
The determinant of the matrix $H = [H_+ \mid H_-]$ is:
$$\det H = -2 h_+ h_- A_c u_* \neq 0.$$
The two columns are **strictly non-collinear** and span the full 2D space.

---

## Panel D: Positive Stress Cone $\mathcal{K}_{\text{stress}}$ and Target $T$ Inversion

The open convex cone generated by positive linear combinations $y_+ H_+ + y_- H_-$ ($y_+, y_- > 0$) is:
$$\mathcal{K}_{\text{stress}} = \left\{ T = T_N N + T_K K : T_N < 0, \; |T_K| < \frac{u_*}{A_c} (-T_N) \right\}.$$

```
                                      THE ATTAINABLE STRESS CONE
                                                 K ▲
                                                   │
                         \   ATTAINABLE CONE       │
                          \  (Positive Weights)    │
                           \                       │
                            \        * T (Target)  │
                             \      /              │
                              \    /               │
                               \  /                │
                                \/                 │
              ◄──────────────────┼─────────────────┼────────────────────────► N
              Compres-          /\ (Apex at origin)│
              sive             /  \                │
              Zone            /    \               │
                             /      \              │
                            /        \             │
                           /          \            │
                          /            \           │
                         / Boundary:    \          │
                        |TK| = (u*/Ac)(-TN)        │
                                                   │
```

### Inversion Coordinates:
For any target $T \in \operatorname{int}(\mathcal{K}_{\text{stress}})$:
$$h_+ y_+ = \frac{1}{2} \left( -\frac{T_N}{A_c} - \frac{T_K}{u_*} \right) > 0, \qquad h_- y_- = \frac{1}{2} \left( -\frac{T_N}{A_c} + \frac{T_K}{u_*} \right) > 0.$$
Both pulses are excited with strictly positive energy.

---

## Summary of Resolution

$$\boxed{\begin{aligned}
\text{Static dyad } \Re(b_\sigma \otimes \overline{b_\sigma}) &\implies \operatorname{rank} = 1 \quad (\text{R2 False Simplification}) \\
\text{Dynamic momentum flux } C(b_\sigma) &\implies \operatorname{rank} = 2, \; \det H \neq 0 \quad (\text{R3 Source-Faithful Reproduction})
\end{aligned}}$$

Classification: `SOURCE_DERIVED_LOCAL_MODEL`.
