# TP2-G1R: GRADIENT CONVENTION CONTRACT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1R (Convention & Operator Reconciliation)`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Mathematical Specification  

---

## 1. Explicit Definition of the Two Gradient Conventions

To permanently eliminate notation-dependent ambiguity between mathematics and fluid-mechanics literature, we explicitly define two distinct tensor conventions for the spatial derivative of a vector field $f: \mathbb{R}^3 \to \mathbb{R}^3$.

### 1.1 Convention M — Mathematical / Jacobian Convention (Default Project Standard)
Under **Convention M**, the gradient / Jacobian tensor $J_f$ is defined such that the target component index $i$ corresponds to the row, and the differentiation coordinate index $j$ corresponds to the column:
$$\boxed{ [J_f]_{ij} := \frac{\partial f_i}{\partial x_j} }$$
- For the forward stochastic flow $a \mapsto X_{s,t}(a)$:
  $$[F_M]_{ij} := [J_{X_{s,t}}]_{ij} = \frac{\partial X_{s,t}^i(a)}{\partial a_j}.$$
- For the inverse flow map $x \mapsto A_{s,t}(x) = X_{s,t}^{-1}(x)$:
  $$[B_M]_{ij} := [J_{A_{s,t}}]_{ij} = \frac{\partial A_{s,t}^i(x)}{\partial x_j}.$$
- In this convention, the chain rule on $X(A(x)) = x$ yields the matrix product:
  $$F_M(A(x)) \cdot B_M(x) = I_3 \implies B_M(x) = [F_M(A(x))]^{-1}, \quad F_M(A(x)) = [B_M(x)]^{-1}.$$

### 1.2 Convention F — Fluid Mechanics / Dyadic Transpose Convention
Under **Convention F**, common in continuum mechanics and fluid dynamics (e.g. Eyink et al., Batchelor, standard tensor analysis where $(\nabla f) \equiv \nabla \otimes f$):
$$\boxed{ [G_f]_{ij} := \frac{\partial f_j}{\partial x_i} = [J_f]_{ji} = [J_f^T]_{ij} }$$
Thus:
$$\boxed{ G_f \equiv J_f^T }$$
- In Convention F, the forward deformation gradient is denoted $\nabla_a X = G_X = F_M^T$.
- In Convention F, the inverse map gradient is denoted $\nabla_x A = G_A = B_M^T$.

---

## 2. Master Project Policy on Gradient Notation

1. **Project Baseline**: All internal mathematical derivations, code, and test suites in `NS-TRAJECTORY-PERSISTENCE-2` shall strictly follow **Convention M**.
2. **Explicit Symbol Binding**: The ambiguous symbol $\nabla f$ alone shall **never** be used in acceptance-critical equations without explicitly stating the convention. The symbols $J_f$ (for Convention M) and $G_f$ (for Convention F) must be used when contrasting literature sources.
3. **Stochastic Cauchy Multiplier Definition**:
   The stochastic Cauchy operator $D_t^s(x)$ acting on initial vorticity $\omega(A(x), s)$ is defined componentwise:
   $$Z_i(x,t; s) = D_{ij}(x,t; s) \, \omega_j(A_{s,t}(x), s),$$
   where under Convention M:
   $$\boxed{ D_{ij}(x,t; s) = [F_M]_{ij}(A_{s,t}(x)) = [B_M^{-1}]_{ij}(x) }$$
