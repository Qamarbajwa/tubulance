# TP2-G6-C1: TWO-PARTICLE HISTORY WEIGHT CANDIDATES AND DIMENSIONAL AUDIT

## Work Package WP8: Formulation, Scaling, and Deformation-Decoupling Analysis

---

### 1. Purpose and Constitutional Requirement

In the single-particle $\Xi$ framework established in TP2-G4 and audited in TP2-G6-A2, the stochastic history measure is defined by:
$$
d\mu_s^x = \frac{|Z_s(x)|^2}{S_s(x)}\, d\mathbb{P}, \qquad Z_s(x) = D_s(x) \omega(A_s(x), s), \quad S_s(x) = \mathbb{E}[|Z_s(x)|^2].
$$
Work Package WP8 and Theorem 8.1 of increment `TP2-G6-A2` proved the **History Measure Decoupling Theorem**: the weight $|Z_s(x)|^2$ decouples from local Eulerian vorticity intensity $|\omega|^2$ because the deformation matrix $D_s$ can align with compressing axes to extinguish $|Z_s|^2 \to 0$ in high-vorticity cores, or expand in hyperbolic saddles to amplify $|Z_s|^2 \to \infty$ in low-vorticity regions.

This work package formulates and audits candidate **two-particle history weights** constructed from pair trajectories $(A_s(x), A_s(x+h))$. Each candidate is evaluated against:
1. Physical dimensions and parabolic scaling invariance.
2. Infinitesimal reduction as $|h| \to 0$.
3. Vulnerability to deformation-decoupling.
4. Bridge relevance (`B2`, `B3`, or `B0`).

---

### 2. Candidate Weight Formulations

Let $A_s^{(1)} = A_s(x)$ and $A_s^{(2)} = A_s(x+h)$ be backward trajectories, with corresponding deformation tensors $D_s^{(1)} = \nabla_x A_s(x)$ and $D_s^{(2)} = \nabla_x A_s(x+h)$.
The transported Cauchy vorticity vectors are:
$$
Z_s^{(1)} = D_s^{(1)} \omega(A_s^{(1)}, s), \qquad Z_s^{(2)} = D_s^{(2)} \omega(A_s^{(2)}, s).
$$
We define the vector vorticity increment:
$$
\delta Z_s(x, h) = Z_s^{(2)} - Z_s^{(1)} = D_s^{(2)} \omega(A_s^{(2)}, s) - D_s^{(1)} \omega(A_s^{(1)}, s) \in \mathbb{R}^3.
$$

We investigate three distinct candidate families:

---

#### Candidate Family 1: Absolute Pair Difference Weight ($W_s^{(2)}$)
$$
\boxed{
W_s^{(2)}(x, h) = |\delta Z_s(x, h)|^2 = \left| D_s^{(2)} \omega(A_s^{(2)}, s) - D_s^{(1)} \omega(A_s^{(1)}, s) \right|^2.
}
$$
- **Physical Dimensions**:
  $[x] = L$, $[t] = T$, $[u] = L T^{-1}$, $[\omega] = T^{-1}$.
  The deformation tensor $D_s = \nabla_x A_s$ is dimensionless: $[D_s] = 1$.
  Therefore, $[Z_s] = T^{-1}$, which implies:
  $$
  [W_s^{(2)}] = T^{-2}.
  $$
- **Parabolic Scaling**:
  Under Navier–Stokes parabolic rescaling $x \mapsto \lambda x$, $t \mapsto \lambda^2 t$, $u \mapsto \lambda^{-1} u$:
  $[\omega] \mapsto \lambda^{-2} \omega$, $[D_s] \mapsto D_s$ (scale-invariant).
  Thus:
  $$
  W_s^{(2)} \mapsto \lambda^{-4} W_s^{(2)}.
  $$
- **Infinitesimal Behavior ($h \to 0$)**:
  As $|h| \to 0$, $\delta Z_s \to 0$ continuously. Specifically:
  $$
  W_s^{(2)} \sim |h|^2 \|\nabla_x Z_s(x)\|^2 \to 0.
  $$
  Because $W_s^{(2)}$ vanishes quadratically as $h \to 0$, it cannot be used as an intrinsic density without normalization by $|h|^2$.
- **Bridge Classification**: **`B0`** (Dimensionally inconsistent with scale-invariant rate $\Xi$).

---

#### Candidate Family 2: Spatial Difference-Quotient Weight ($W_s^\nabla$)
$$
\boxed{
W_s^\nabla(x, h) = \frac{|\delta Z_s(x, h)|^2}{|\delta A_s(x, h)|^2} = \frac{\left| D_s^{(2)} \omega(A_s^{(2)}, s) - D_s^{(1)} \omega(A_s^{(1)}, s) \right|^2}{|A_s(x+h) - A_s(x)|^2}.
}
$$
- **Physical Dimensions**:
  $[|\delta Z_s|^2] = T^{-2}$, $[|\delta A_s|^2] = L^2$.
  Therefore:
  $$
  [W_s^\nabla] = L^{-2} T^{-2}.
  $$
- **Parabolic Scaling**:
  Under $x \mapsto \lambda x$, $t \mapsto \lambda^2 t$:
  $[|\delta Z_s|^2] \mapsto \lambda^{-4}$, $[|\delta A_s|^2] \mapsto \lambda^2$.
  Thus:
  $$
  W_s^\nabla \mapsto \lambda^{-6} W_s^\nabla.
  $$
- **Infinitesimal Behavior ($h \to 0$) under C-SYNC**:
  By Theorem 4.1, under Coupling C-SYNC:
  $$
  \lim_{|h| \to 0} W_s^\nabla(x, h) = \frac{\|(\nabla_x Z_s) e_h\|^2}{\|D_s e_h\|^2}, \qquad e_h = \frac{h}{|h|}.
  $$
  This directly generates a directional gradient density of the transported vorticity field!
- **Bridge Classification**: **`B2`** (Candidate for history-to-Eulerian gradient coverage).

---

#### Candidate Family 3: Tensorial Pair Covariance Weight ($\mathbb{W}_s$)
$$
\boxed{
\mathbb{W}_s(x, h) = \delta Z_s(x, h) \otimes \delta Z_s(x, h) \in \mathbb{R}^{3 \times 3}.
}
$$
- **Physical Dimensions**: $[\mathbb{W}_s] = T^{-2}$.
- **Symmetric Positive Semi-Definite Matrix**: For any unit vector $n \in \mathbb{S}^2$, $n^T \mathbb{W}_s n = (n \cdot \delta Z_s)^2 \ge 0$.
- **Rank**: $\operatorname{rank}(\mathbb{W}_s) = 1$ pathwise for every individual Brownian realization. Full rank can only emerge after stochastic expectation $\mathbb{E}[\mathbb{W}_s]$.
- **Bridge Classification**: **`B3`** (Directly relevant to covariance spectrum and multidirectional dispersion).

---

### 3. Deformation-Decoupling Stress Test of $W_s^\nabla$

We now subject the leading candidate $W_s^\nabla$ to the exact adversarial mechanism that defeated the single-particle measure in BM-A2-05.

Expand the numerator $\delta Z_s = Z_s^{(2)} - Z_s^{(1)}$:
$$
\begin{aligned}
\delta Z_s &= D_s(x+h) \omega(A_s(x+h), s) - D_s(x) \omega(A_s(x), s) \\
&= D_s(x) \left[ \omega(A_s^{(2)}, s) - \omega(A_s^{(1)}, s) \right] + \left[ D_s(x+h) - D_s(x) \right] \omega(A_s^{(2)}, s).
\end{aligned}
$$
Let $|h| \ll 1$ and consider the leading-order term:
$$
\delta Z_s \approx D_s(x) \left( \nabla \omega(A_s(x), s)\, \delta A_s \right) + \left( \nabla_x D_s(x) \cdot h \right) \omega(A_s(x), s).
$$
Dividing by $|\delta A_s|$:
$$
\frac{\delta Z_s}{|\delta A_s|} \approx D_s(x) \left( \nabla \omega(A_s) e_s \right) + \frac{(\nabla_x D_s \cdot h) \omega(A_s)}{|\delta A_s|}.
$$

#### The Decoupling Vulnerability:
1. **Multiplication by $D_s$ Persists**: The physical Eulerian gradient term $\nabla \omega(A_s) e_s$ is multiplied on the left by the **exact same deformation tensor $D_s(x)$**.
2. **Eigenvector Extinction**: If the vector $\xi_{\text{grad}} = \nabla \omega(A_s) e_s$ aligns with the contracting singular direction of $D_s(x)$ (eigenvalue $\sigma_3 \sim e^{-\lambda(t-s)}$), then:
   $$
   \left| D_s(x) \xi_{\text{grad}} \right| \le \sigma_3 |\xi_{\text{grad}}| \sim e^{-\lambda(t-s)} |\nabla \omega|.
   $$
   The pair history weight $W_s^\nabla$ is exponentially extinguished inside the core, exactly as in the single-particle case!
3. **Hyperbolic Amplification in Low-Vorticity Zones**: If a particle pair passes through a hyperbolic saddle where $|\nabla \omega| \sim 1$ but $\xi_{\text{grad}}$ aligns with the expanding direction of $D_s$ (eigenvalue $\sigma_1 \sim e^{\lambda(t-s)}$), $W_s^\nabla$ is amplified by $e^{2\lambda(t-s)}$, concentrating the two-particle measure away from the high-gradient core.

---

### 4. Epistemic Assessment

| Weight Candidate | Physical Dimension | Infinitesimal Limit ($h \to 0$) | Deformation-Decoupling Status | Target Bridge |
|---|---|---|---|---|
| **$W_s^{(2)} = |\delta Z|^2$** | $T^{-2}$ | Vanishes as $\mathcal{O}(|h|^2)$ | **Vulnerable** | `B0` |
| **$W_s^\nabla = \frac{|\delta Z|^2}{|\delta A|^2}$** | $L^{-2} T^{-2}$ | Converges to directional jet density | **Vulnerable** to $D_s$ alignment | `B2` |
| **$\mathbb{W}_s = \delta Z \otimes \delta Z$** | $T^{-2}$ | Vanishes as $\mathcal{O}(|h|^2)$ | **Vulnerable** (Rank 1 pathwise) | `B3` |

**Fundamental Conclusion**:
Constructing a two-particle history weight by taking differences $\delta Z_s = Z_s^{(2)} - Z_s^{(1)}$ **does not eliminate deformation-vorticity decoupling**. The deformation tensor $D_s$ acts multiplicatively on both particles, preserving the susceptibility to alignment-induced extinction inside vortex cores. To overcome this requires relative covariance dispersion where the deformation tensor itself is averaged over independent orientations.
