# TP2-G6-A2: High-Vorticity Superlevel Geometry and Deformation Weighting Audit

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-A2 (Work Package 8)`  
**Target Bridge:** `B2 — History-to-Eulerian Coverage`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Geometric Sparseness of High-Vorticity Sets

Let $M(s) = \|\omega(\cdot, s)\|_{L^\infty(\mathbb{T}^3)}$ and $\Omega(s) = \frac{1}{2} \int_{\mathbb{T}^3} |\omega(x, s)|^2 dx$.
For any $\alpha \in (0, 1)$, the high-vorticity superlevel set is:
\[
E_s(\alpha) = \{ x \in \mathbb{T}^3 : |\omega(x, s)| \ge \alpha M(s) \}.
\]

### Proposition 8.1 (Asymptotic Vanishing of Volume)
If the solution experiences a hypothetical finite-time singularity at $T^*$ with $M(s) \to \infty$, and if the total enstrophy satisfies $\Omega(s) = o(M(s)^2)$ (which is guaranteed if enstrophy remains bounded, or grows as a sub-quadratic power $M(s)^\gamma$ with $\gamma < 2$):
\[
|E_s(\alpha)| \le \frac{2 \Omega(s)}{\alpha^2 M(s)^2} \to 0 \quad \text{as } s \nearrow T^*.
\]

The high-vorticity region occupies an asymptotically vanishing fraction of the torus $\mathbb{T}^3$.

---

## 2. Decoupling Between History Measure and Peak Vorticity

The stochastic history measure $\mu_s^x$ is defined by:
\[
d\mu_s^x = \frac{|Z_s(x)|^2}{S_s(x)} d\mathbb{P}, \quad \text{where } Z_s(x) = D_s(x) \omega(A_s(x), s).
\]

Does the weight $|Z_s(x)|^2$ force trajectories to concentrate on $E_s(\alpha)$?

### Analysis of the Matrix Deformation Interaction:
Let the singular value decomposition of the deformation tensor $D_s(x)$ be:
\[
D_s(x) = U_s(x) \Sigma_s(x) V_s(x)^T, \quad \Sigma_s = \operatorname{diag}(\sigma_1, \sigma_2, \sigma_3), \quad \sigma_1 \ge \sigma_2 \ge \sigma_3 > 0.
\]
Because $\det(D_s(x)) = 1$ (by flow incompressibility), $\sigma_1 \sigma_2 \sigma_3 = 1$, and $\sigma_1 \ge 1 \ge \sigma_3 > 0$.

The magnitude $|Z_s|^2$ is:
\[
|Z_s|^2 = |D_s \omega(A_s)|^2 = \omega(A_s)^T D_s^T D_s \omega(A_s) = \sum_{i=1}^3 \sigma_i^2 (\omega(A_s) \cdot v_i)^2.
\]

### Two Decoupling Mechanisms:

#### Mechanism 1: Alignment with the Compression Eigenvector (Vorticity Damping)
Suppose $A_s(x) \in E_s(\alpha)$, so $|\omega(A_s(x))| \ge \alpha M(s)$ is maximal.
However, suppose the vorticity vector $\omega(A_s)$ happens to align with the compression direction $v_3$:
\[
\omega(A_s) \approx |\omega(A_s)| v_3.
\]
Then:
\[
|Z_s|^2 \approx \sigma_3^2 |\omega(A_s)|^2.
\]
If the trajectory has experienced sustained compressive strain along $v_3$ so that $\sigma_3 \sim e^{-\int \lambda_3 d\tau} \ll 1$, then:
\[
|Z_s|^2 \ll |\omega(A_s)|^2.
\]
Even though the trajectory is inside the peak vorticity core $E_s(\alpha)$, its contribution to the history measure $\mu_s^x$ is **exponentially extinguished**!

#### Mechanism 2: Alignment with the Stretching Eigenvector in Low-Vorticity Wake (Saddle Trapping)
Conversely, suppose $A_s(x) \notin E_s(\alpha)$, so $|\omega(A_s(x))| \sim 1 \ll M(s)$ is small.
Suppose this trajectory traverses a hyperbolic straining saddle where $\sigma_1 \sim e^{\int \lambda_1 d\tau} \gg 1$, and $\omega(A_s)$ aligns with the stretching direction $v_1$:
\[
|Z_s|^2 \ge \sigma_1^2 |\omega(A_s)|^2 \sim e^{2 \int \lambda_1 d\tau} \gg 1.
\]
If $\sigma_1 \gtrsim M(s)$, the quantity $|Z_s|^2$ in this **low-vorticity region** can equal or exceed the value of $|Z_s|^2$ inside the vortex core!

### Theorem 8.2 (History Measure Decoupling Theorem)
The condition that $|Z_s(x)|$ is large does **not** imply that $|\omega(A_s(x), s)|$ is large.
Specifically:
\[
\mu_s^x \left( A_s^{-1}(E_s(\alpha)) \right) = \frac{\mathbb{E}_{\mathbb{P}}\left[ |D_s \omega(A_s)|^2 \mathbf{1}_{E_s(\alpha)}(A_s) \right]}{\mathbb{E}_{\mathbb{P}}\left[ |D_s \omega(A_s)|^2 \right]}
\]
can be made arbitrarily close to $0$ by constructing divergence-free configurations where trajectories in $E_s(\alpha)$ undergo compression along $\omega$, while trajectories in $\mathbb{T}^3 \setminus E_s(\alpha)$ undergo stretching along $\omega$.

---

## 3. Quarantine of Classical Regularity Criteria

We audit classical geometric criteria to determine if they can rescue Bridge $B_2$:
1. **Constantin–Fefferman Direction Coherence (1993):**
   Requires $|\sin \angle(\omega(x), \omega(y))| \le C |x - y|^\beta$ uniformly in a neighborhood of peak vorticity.
   *Status:* `CIRCULAR` (assumes geometric direction smoothness equivalent to BKM).
2. **Grujić Analyticity and Spatial Sparseness (2001, 2013):**
   Requires a positive spatial analyticity radius $\rho(t) \ge c > 0$.
   *Status:* `CONTINUATION_EQUIVALENT` (a lower bound on analyticity radius prevents finite-time blowup).
3. **Beale–Kato–Majda / Serrin Criteria:**
   *Status:* `CIRCULAR`.

All classical geometric rescues require assumptions that directly assume regularity.
They cannot be used non-circularly to prove Bridge $B_2$.
