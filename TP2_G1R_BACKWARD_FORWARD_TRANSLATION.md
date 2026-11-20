# TP2-G1R: BACKWARD–FORWARD TRANSLATION & RESULT RESOLUTION

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1R`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Convention Translation Report  

---

## 1. The Discrepancy under Audit

Modern stochastic-Cauchy literature (e.g. Eyink–Gupta–Zaki 2020 and subsequent fluid dynamics papers) expresses the backward stochastic Cauchy deformation as:
$$\widetilde D_T^{,s}(x_f) = (\nabla_a \widetilde X_s^T)^T = (\nabla_{x_f} \widetilde A_T^s)^{-T}.$$
Meanwhile, the project's Convention M verification reports:
$$D_t^s(x) = (\nabla_x A_{s,t}(x))^{-1} = F_{s,t}(A_{s,t}(x)).$$

---

## 2. Rigorous Mathematical Translation

### 2.1 Convention Definitions
Let $x \mapsto A(x)$ be the inverse map.
- In **Convention M** (Mathematical Jacobian):
  $$[B_M]_{ij} = \frac{\partial A_i}{\partial x_j}.$$
- In **Convention F** (Fluid Mechanics Gradient Tensor):
  $$[G_A]_{ij} = \frac{\partial A_j}{\partial x_i} = [B_M^T]_{ij} \implies G_A = B_M^T.$$

### 2.2 Translation of the JFM Backward Formula
In JFM literature using Convention F, the author denotes $\nabla_{x_f} \widetilde A$ as the matrix $G_A$.
Substituting $G_A = B_M^T$ into the printed JFM expression $(\nabla_{x_f} \widetilde A)^{-T}$:
$$\boxed{ (\nabla_{x_f} \widetilde A)^{-T} \equiv (G_A)^{-T} = (B_M^T)^{-T} = B_M^{-1} }$$
Since $B_M^{-1} = F_M(A(x))$ under Convention M:
$$\boxed{ (G_A)^{-T} \equiv F_M(A(x)) \equiv D_M }$$

### 2.3 Translation of the JFM Forward Formula
In JFM literature using Convention F, the forward gradient is $G_X = F_M^T$.
The printed JFM expression $(\nabla_a \widetilde X)^T$ translates to:
$$\boxed{ (\nabla_a \widetilde X)^T \equiv (G_X)^T = (F_M^T)^T = F_M \equiv D_M }$$

---

## 3. Authoritative Scientific Finding

$$\boxed{\textbf{RESULT A — CONVENTION DIFFERENCE RESOLVED}}$$

### Precise Declaration:
The apparent inverse versus inverse-transpose discrepancy between
$$D_t^s(x) = (\nabla_x A_{s,t}(x))^{-1}$$
and
$$\widetilde D_T^{,s}(x_f) = (\nabla_{x_f} \widetilde A_T^s)^{-T}$$
is **purely a gradient-convention translation** between:
1. **Convention M** ($[J]_{ij} = \frac{\partial f_i}{\partial x_j}$); and
2. **Convention F** ($[G]_{ij} = \frac{\partial f_j}{\partial x_i}$).

Both mathematical expressions specify the **exact same physical and probabilistic tensor transformation**:
$$Z_i(x,t; s) = \frac{\partial X_{s,t}^i}{\partial a_j}(A_{s,t}(x)) \, \omega_j(A_{s,t}(x), s) = [B_M^{-1}]_{ij}(x) \, \omega_j(A_{s,t}(x), s).$$

No real transpose or inverse error exists in the previous G1 derivation.
