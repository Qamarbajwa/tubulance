# TP2-G6-C1: THE STOCHASTIC JET LIMIT AND THE CANONICAL XI CONNECTION

## Work Package WP9: Rigorous Derivation of Bilateral Deformation Pullbacks

---

### 1. Purpose and Historical Context

In Gate TP2-G4 and Campaign TP2-G5, the central mathematical object of the programme was established as the **relative quadratic variation density**:
$$
\Xi = \frac{\|D J_\omega\|_F^2}{|D \omega|^2} \quad \text{on } \{\omega \ne 0\},
$$
where $D = D_s(x)$ is the deformation tensor, $\omega = \omega(A_s(x), s)$ is the transported vorticity, and $J_\omega = \nabla \omega(A_s(x), s) \in \mathbb{R}^{3 \times 3}$ is the Eulerian vorticity Jacobian matrix. The exact rate bridge $d_s \ln \chi_s = 2\nu \mathbb{E}_{\mu_s}[\Xi]$ forms the surviving analytical foundation of the persistence framework (`CLM-014`).

This work package investigates the exact mathematical connection between the **two-particle difference quotient**:
$$
\lim_{|h| \to 0} \frac{|Z_s(x+h) - Z_s(x)|^2}{|h|^2}
$$
and the $\Xi$ framework. We prove that the infinitesimal limit of the two-particle history increment generates a **bilateral deformation pullback** $D_s J_\omega D_s$ supplemented by an explicit **flow curvature source term** governed by the second-order stochastic jet $H_s = \nabla_x^2 A_s$.

---

### 2. Exact Infinitesimal Derivation

Let $Z_s(x) = D_s(x) \omega(A_s(x), s) \in \mathbb{R}^3$. We compute the full spatial Jacobian matrix of this vector field on $\mathbb{T}^3$:
$$
(\nabla_x Z_s(x))_{ik} = \frac{\partial (Z_s)_i}{\partial x_k}(x).
$$
Applying the product rule to $(Z_s)_i = \sum_{j=1}^3 (D_s)_{ij}(x) \omega_j(A_s(x), s)$:
$$
\frac{\partial (Z_s)_i}{\partial x_k} = \sum_{j=1}^3 \frac{\partial (D_s)_{ij}}{\partial x_k} \omega_j(A_s(x), s) + \sum_{j=1}^3 (D_s)_{ij} \frac{\partial}{\partial x_k} \left[ \omega_j(A_s(x), s) \right].
$$
By the chain rule on the second term:
$$
\frac{\partial}{\partial x_k} \left[ \omega_j(A_s(x), s) \right] = \sum_{m=1}^3 \frac{\partial \omega_j}{\partial y_m}(A_s(x), s) \frac{\partial A_s^m}{\partial x_k}(x).
$$
Recall the fundamental definitions:
- The Jacobian of the backward flow is the deformation tensor: $\frac{\partial A_s^m}{\partial x_k} = (D_s)_{mk}$.
- The Eulerian vorticity Jacobian is: $(J_\omega)_{jm} = \frac{\partial \omega_j}{\partial y_m}$.
- The second spatial derivative of the flow is the second-order jet: $(H_s)_{ijk} = \frac{\partial (D_s)_{ij}}{\partial x_k} = \frac{\partial^2 A_s^i}{\partial x_j \partial x_k}$.

Substituting these into the second term:
$$
\sum_{j=1}^3 \sum_{m=1}^3 (D_s)_{ij} (J_\omega)_{jm} (D_s)_{mk} = \left( D_s(x)\, J_\omega(A_s(x), s)\, D_s(x) \right)_{ik}.
$$
Substituting into the first term:
$$
\sum_{j=1}^3 (H_s)_{ijk} \omega_j = \left( H_s(x) : \omega(A_s(x), s) \right)_{ik}.
$$

Summing both contributions yields the exact matrix identity:
$$
\boxed{
\nabla_x Z_s(x) = D_s(x)\, J_\omega(A_s(x), s)\, D_s(x) + H_s(x) : \omega(A_s(x), s) \in \mathbb{R}^{3 \times 3}.
}
$$

---

### 3. Directional and Omnidirectional Pair Limits

Let $h = |h| e_h$ with $e_h \in \mathbb{S}^2$. By Taylor expansion under Coupling C-SYNC:
$$
Z_s(x+h) - Z_s(x) = |h| \left( \nabla_x Z_s(x) \right) e_h + \mathcal{O}(|h|^2).
$$
Squaring and dividing by $|h|^2$:
$$
\lim_{|h| \to 0} \frac{|Z_s(x+h) - Z_s(x)|^2}{|h|^2} = \left| \left( \nabla_x Z_s(x) \right) e_h \right|^2.
$$
Averaging over all initial separation orientations $e_h$ uniformly on the unit sphere $\mathbb{S}^2$ with normalized surface measure $d\sigma(e_h)$:
$$
\int_{\mathbb{S}^2} \left| \left( \nabla_x Z_s(x) \right) e_h \right|^2 d\sigma(e_h) = \frac{1}{3} \sum_{i=1}^3 \sum_{k=1}^3 \left( (\nabla_x Z_s)_{ik} \right)^2 = \frac{1}{3} \|\nabla_x Z_s(x)\|_F^2.
$$
Dividing by $|Z_s(x)|^2 = |D_s \omega|^2$:
$$
\boxed{
\Xi^{\text{pair}}(x) \equiv \lim_{|h| \to 0} \frac{3}{|h|^2} \int_{\mathbb{S}^2} \frac{|Z_s(x+h) - Z_s(x)|^2}{|Z_s(x)|^2}\, d\sigma(e_h) = \frac{\left\| D_s J_\omega D_s + H_s : \omega \right\|_F^2}{|D_s \omega|^2}.
}
$$

---

### 4. Comparison Between $\Xi^{\text{pair}}$ and Classical $\Xi$

We compare the two-particle jet limit $\Xi^{\text{pair}}$ with the single-particle quadratic variation density $\Xi$:

| Feature | Single-Particle $\Xi$ (TP2-G4/G5) | Two-Particle Jet Limit $\Xi^{\text{pair}}$ (TP2-G6-C) |
|---|---|---|
| **Mathematical Definition** | $\Xi = \frac{\|D_s J_\omega\|_F^2}{|D_s \omega|^2}$ | $\Xi^{\text{pair}} = \frac{\|D_s J_\omega D_s + H_s : \omega\|_F^2}{|D_s \omega|^2}$ |
| **Left Action** | Multiplied by $D_s$ on left | Multiplied by $D_s$ on left |
| **Right Action** | None (acts on standard basis) | Multiplied by $D_s$ on right (pullback by flow gradient) |
| **Curvature Sensitivity** | Insensitive to flow curvature $\nabla^2 A_s$ | **Explicitly sensitive** to second jet $H_s = \nabla^2 A_s$ |
| **Physical Meaning** | Rate of change of Cauchy vector magnitude | Full Riemannian metric deformation of vorticity field |
| **Affine Flow Agreement** | In linear shear/strain ($\nabla^2 u = 0$), $H_s = 0$, yielding $\frac{\|D_s J_\omega D_s\|_F^2}{|D_s \omega|^2}$ | Identical up to right-multiplication by $D_s$ |

---

### 5. Conceptual Significance and Bridge Synthesis

1. **Exact Structural Link**: The two-particle route is **not a disconnected heuristic**; its infinitesimal limit under C-SYNC is the exact second-order jet extension of the $\Xi$ framework.
2. **The Right-Multiplication by $D_s$**: In single-particle $\Xi$, $D_s$ acted only on the Eulerian vorticity vector $\omega$, while $J_\omega$ was evaluated at $A_s$. In the two-particle limit, $D_s$ also multiplies $J_\omega$ on the right, which accounts for the physical stretching of the separation vector $h$ itself:
   $$
   \delta A_s \approx D_s h.
   $$
3. **The Role of Flow Curvature ($H_s : \omega$)**: The presence of $H_s : \omega$ captures non-local strain gradients $\nabla^2 u$. When intense vortex stretching occurs, the spatial variation of strain curls and bends material segments, injecting quadratic variation directly through the second jet.
