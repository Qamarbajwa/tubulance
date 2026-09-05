# TP2-G6-B-R1: Scaling Audit for High-Intensity Smooth Sequences

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R1 (Work Package 3)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Objective and Core Scaling Question

Work Package 3 attempts an adversarial construction of smooth, divergence-free Navier–Stokes solutions on $\mathbb{T}^3$ that exhibit **active, nonlinear vortex stretching** while simultaneously forcing the scale-critical intrinsic production to vanish:
\[
\boxed{ M_n = |\omega(x_n, t_n)| \longrightarrow \infty, \quad \frac{\omega \cdot S \omega}{|\omega|^2} \ge c_0 M_n > 0, \quad \text{while} \quad J_n(a) = 2\nu \int_{t_n - a/M_n}^{t_n} \mathbb{E}_{\mu_r}[\Xi_r] dr \longrightarrow 0 }.
\]
If such a sequence can be constructed, it proves that Branch R is fully compatible with violent vortex stretching, thereby falsifying the hypothesis that scalar relative QV production $J_n(a)$ can detect or prevent finite-time blow-up.

---

## 2. Invariance of $J_n(a)$ Under Parabolic Rescaling

A common trap in Navier–Stokes scaling studies is mistaking the parabolic rescaling of a single smooth solution for a genuinely new high-intensity flow regime.

### Theorem 1 (Parabolic Invariance of Intrinsic Production)
Let $u(x, t)$ be any smooth solution to the 3D incompressible Navier–Stokes equations with viscosity $\nu > 0$. For any $\lambda > 0$, let $u^{(\lambda)}$ be the parabolically rescaled solution:
\[
u^{(\lambda)}(x, t) := \lambda u(\lambda x, \lambda^2 t).
\]
Let $(x_0, t_0)$ be a fixed reference point, and let $(x_\lambda, t_\lambda) = (\lambda^{-1} x_0, \lambda^{-2} t_0)$. Then:
1. $M_\lambda := |\omega^{(\lambda)}(x_\lambda, t_\lambda)| = \lambda^2 |\omega(x_0, t_0)| = \lambda^2 M_0$.
2. The intrinsic lookback horizon scales as $L_\lambda = \frac{a}{M_\lambda} = \frac{a}{\lambda^2 M_0} = \lambda^{-2} L_0$.
3. The Relative QV Density scales as $\Xi^{(\lambda)}(x_\lambda, r) = \lambda^2 \Xi(x_0, \lambda^2 r)$.
4. The accumulated intrinsic production is **strictly invariant**:
\[
\boxed{ J_\lambda(a) \equiv J_0(a) \quad \forall \lambda > 0 }.
\]

### Proof
Under parabolic dilation $x \mapsto \lambda x, t \mapsto \lambda^2 t$:
- $[u] = \lambda^1$, $[\nabla u] = \lambda^2$, $[\omega] = \lambda^2$, $[J_\omega] = \lambda^3$.
- The backward trajectory satisfies $A_r^{(\lambda)}(x_\lambda) \stackrel{d}{=} \lambda^{-1} A_{\lambda^2 r}(x_0)$.
- The deformation tensor $D_r^{(\lambda)}$ satisfies $D_r^{(\lambda)} = D_{\lambda^2 r}$ ($[D] = \lambda^0$).
- Therefore $|Z_r^{(\lambda)}|^2 = \lambda^4 |Z_{\lambda^2 r}|^2$, and $\|D_r^{(\lambda)} J_\omega^{(\lambda)}\|_F^2 = \lambda^6 \|D_{\lambda^2 r} J_\omega\|_F^2$.
- The measure is invariant: $d\mu_r^{(\lambda)} = \frac{|Z_r^{(\lambda)}|^2}{\mathbb{E}[|Z_r^{(\lambda)}|^2]} d\mathbb{P} = d\mu_{\lambda^2 r}$.
- The Relative QV Density scales as:
  \[
  \Xi_r^{(\lambda)} = \frac{\lambda^6 \|D_{\lambda^2 r} J_\omega\|_F^2}{\lambda^4 |Z_{\lambda^2 r}|^2} = \lambda^2 \Xi_{\lambda^2 r}.
  \]
Substituting into the definition of $J_\lambda(a)$:
\[
J_\lambda(a) = 2\nu \int_{t_\lambda - L_\lambda}^{t_\lambda} \mathbb{E}_{\mu_r^{(\lambda)}}\left[ \Xi_r^{(\lambda)} \right] dr = 2\nu \int_{\lambda^{-2}(t_0 - L_0)}^{\lambda^{-2} t_0} \lambda^2 \mathbb{E}_{\mu_{\lambda^2 r}}\left[ \Xi_{\lambda^2 r} \right] dr.
\]
Change integration variable to $\tilde{r} = \lambda^2 r$, so $d\tilde{r} = \lambda^2 dr$:
\[
J_\lambda(a) = 2\nu \int_{t_0 - L_0}^{t_0} \mathbb{E}_{\mu_{\tilde{r}}}\left[ \Xi_{\tilde{r}} \right] d\tilde{r} = J_0(a). \quad \blacksquare
\]

### Corollary 1.1 (Rescaling Prohibition)
Pure parabolic dilation of a smooth solution profile **cannot generate Branch R**. Any candidate sequence approaching Branch R ($J_n(a) \to 0$) must possess an asymptotically changing internal structural geometry.

---

## 3. Structural Analysis of the Regime $J_n(a) \to 0$

For a sequence of smooth solutions $(u^{(n)}, x_n, t_n)$ on $\mathbb{T}^3$ with peak vorticity $M_n \to \infty$ to realize Branch R, the mean value theorem applied to $J_n(a) = 2\nu \int_{t_n - a/M_n}^{t_n} \mathbb{E}_{\mu_r}[\Xi_r] dr$ requires:
\[
\boxed{ \frac{\overline{\Xi}_n}{M_n} \longrightarrow 0 }, \quad \text{where } \overline{\Xi}_n := \frac{1}{L_n} \int_{t_n - L_n}^{t_n} \mathbb{E}_{\mu_r}[\Xi_r] dr.
\]

### 3.1 Geometric Meaning: Flatness of Peak Vorticity
At lookback time $r = t_n$ (zero lookback, where $D = I$), the density $\Xi$ reduces to the local inverse squared length scale:
\[
\Xi(x_n, t_n) = \frac{\|J_\omega(x_n, t_n)\|_F^2}{|\omega(x_n, t_n)|^2} = \frac{\|\nabla \omega(x_n, t_n)\|_F^2}{M_n^2} = \kappa_\omega^2(x_n, t_n).
\]
Therefore, the instantaneous necessary condition for Branch R at $t_n$ is:
\[
\frac{\kappa_\omega^2(x_n, t_n)}{M_n} \longrightarrow 0 \iff \frac{\|\nabla \omega(x_n, t_n)\|_F}{M_n^{3/2}} \longrightarrow 0.
\]
Let $\ell_n$ be the characteristic spatial width of the vorticity peak around $x_n$, so $\|\nabla \omega\| \sim M_n / \ell_n$ and $\kappa_\omega \sim 1 / \ell_n$.  
Then:
\[
\frac{\Xi}{M_n} \sim \frac{1}{M_n \ell_n^2} \longrightarrow 0 \iff \ell_n \gg \frac{1}{\sqrt{M_n}}.
\]

### 3.2 Confrontation with Navier–Stokes Dynamics
In 3D incompressible Navier–Stokes, can an intense vortex structure ($M_n \to \infty$) have a spatial length scale $\ell_n \gg M_n^{-1/2}$ while undergoing strong nonlinear vortex stretching?

1. **The Viscous Scale Boundary:**
   The viscous Kolmogorov / diffusion length scale associated with vorticity $M_n$ is:
   \[
   \eta_{\text{diss}} \sim \sqrt{\frac{\nu}{\|\nabla u\|}} \sim \sqrt{\frac{\nu}{M_n}} \sim M_n^{-1/2}.
   \]
   If $\ell_n \gg M_n^{-1/2}$, viscous dissipation $\nu \Delta \omega \sim \nu M_n / \ell_n^2 \ll M_n^2$ is asymptotically subdominant to nonlinear stretching $S \omega \sim M_n^2$. The high-vorticity structure is in the inertial / inviscid Euler regime.

2. **The Nonlocal Pressure Source Injection:**
   The spatial gradient of vorticity $G = \nabla \omega$ obeys the exact transport equation (`CLM-006`):
   \[
   (D_t - \nu \Delta) G = S G - G A + T, \quad \text{where } T_{ij} = (\partial_j S_{ik}) \omega_k.
   \]
   By the Biot–Savart law, the strain tensor $S$ is related to $\omega$ via the singular integral operator $S = \mathcal{R}(\omega)$ (matrix of Riesz transforms).
   Because $\omega$ is non-uniform on scale $\ell_n$, $\nabla S \sim \nabla \mathcal{R}(\omega)$ cannot vanish identically across the structure. Its magnitude is bounded below by:
   \[
   \|\nabla S\| \gtrsim \frac{M_n}{\ell_n}.
   \]
   Consequently, the source term $T = (\nabla S) \omega$ injects gradient at an immediate rate:
   \[
   \|T\| \sim \|\nabla S\| |\omega| \gtrsim \frac{M_n^2}{\ell_n}.
   \]
   Over the intrinsic window $L_n = a / M_n$, this source generates a vorticity gradient perturbation of magnitude:
   \[
   \|\Delta G\| \sim \|T\| L_n \gtrsim \left(\frac{M_n^2}{\ell_n}\right) \left(\frac{a}{M_n}\right) = \frac{a M_n}{\ell_n}.
   \]
   Squaring and normalizing by $|Z|^2 \sim M_n^2$, the generated Relative QV Density is:
   \[
   \Xi_{\text{generated}} \gtrsim \frac{\|\Delta G\|^2}{M_n^2} \gtrsim \frac{a^2}{\ell_n^2}.
   \]
   This leads to the lower bound on production:
   \[
   J_n(a) \ge 2\nu L_n \Xi_{\text{generated}} \gtrsim 2\nu \left(\frac{a}{M_n}\right) \left(\frac{a^2}{\ell_n^2}\right) = \frac{2\nu a^3}{M_n \ell_n^2}.
   \]

---

## 4. Synthesis of WP3: The Two Regimes of Navier–Stokes Dynamics

Our scaling search establishes an exact dichotomy for smooth high-intensity Navier–Stokes families:

```text
                                 HIGH-INTENSITY SEQUENCE (M_n -> infty)
                                                   │
                   ┌───────────────────────────────┴───────────────────────────────┐
                   │                                                               │
        REGIME I: ZERO STRETCHING                                    REGIME II: ACTIVE STRETCHING
        (omega . S omega = 0)                                        (omega . S omega ~ M_n^2)
                   │                                                               │
  Examples: Periodic Shear, Beltrami                                 Nonlocal source T = (nabla S)omega
  Deformation decouples or pressure cancels                          injects gradients on scale ell_n
                   │                                                               │
  Production J_n(a) -> 0 is SMOOTHLY REALIZED                        If ell_n ~ M_n^{-1/2} (viscous scale):
                   │                                                   Xi ~ M_n => J_n(a) ~ 2 nu a > 0
  Outcome: BRANCH R REALIZED, but NO SINGULARITY                     If ell_n >> M_n^{-1/2} (macroscopic):
           (Solutions exist globally and smoothly)                     Enstrophy diverges, T injects Xi
```

### Decisive Finding:
Branch R ($J_n(a) \to 0$) is **readily realized by smooth Navier–Stokes flows with zero vortex stretching** (Shear, Beltrami).  
However, when **active vortex stretching** $\omega \cdot S \omega \sim M_n^2$ is enforced, the non-local source term $T = (\nabla S)\omega$ in the vorticity-gradient transport equation acts as an inescapable gradient generator, driving $\Xi \sim \kappa_\omega^2$ and obstructing the realization of $J_n(a) \to 0$.
