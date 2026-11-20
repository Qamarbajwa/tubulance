# TP2-G1R: COMPONENTWISE CAUCHY DERIVATION & ORACLE IDENTITY

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1R`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Mathematical Oracle  

---

## 1. Forward Material Deformation in Components (Convention M)

Let $a \mapsto X(a,t)$ be the forward fluid trajectory:
$$\frac{d}{dt} X_i(a,t) = u_i(X(a,t), t), \quad X_i(a,0) = a_i.$$
Define the forward Jacobian matrix under **Convention M**:
$$F_{ij}(a,t) := \frac{\partial X_i}{\partial a_j}(a,t), \quad F_{ij}(a,0) = \delta_{ij}.$$
Taking the time derivative of $F_{ij}$:
$$\frac{d}{dt} F_{ij}(a,t) = \frac{\partial}{\partial a_j} \left( \frac{d X_i}{dt} \right) = \frac{\partial}{\partial a_j} \left( u_i(X(a,t), t) \right) = \frac{\partial u_i}{\partial x_k}(X(a,t), t) \frac{\partial X_k}{\partial a_j}(a,t).$$
In matrix notation:
$$\boxed{ \frac{d F}{dt} = (\nabla_M u) \, F, \quad [F]_{ij} = \frac{\partial X_i}{\partial a_j} }$$

### Theorem (Classical Cauchy Vorticity Formula in Components):
For an incompressible fluid ($\nabla \cdot u = 0 \implies \det F = 1$), the vorticity field $\omega(x,t) = \nabla \times u$ along the trajectory satisfies:
$$\boxed{ \omega_i(X(a,t), t) = F_{ij}(a,t) \, \omega_{0j}(a) = \frac{\partial X_i}{\partial a_j}(a,t) \, \omega_{0j}(a) }$$

---

## 2. Inverse-Map Component Relations

Let $x \mapsto A(x,t) = X_t^{-1}(x)$ be the inverse flow map, so $X_i(A(x,t), t) = x_i$.
Define the inverse Jacobian matrix under **Convention M**:
$$B_{ij}(x,t) := \frac{\partial A_i}{\partial x_j}(x,t).$$
Differentiating the identity $X_i(A(x,t), t) = x_i$ with respect to $x_j$ by the chain rule:
$$\frac{\partial X_i}{\partial a_k}(A(x,t), t) \, \frac{\partial A_k}{\partial x_j}(x,t) = \frac{\partial x_i}{\partial x_j} = \delta_{ij}.$$
In components:
$$\boxed{ F_{ik}(A(x,t), t) \, B_{kj}(x,t) = \delta_{ij} }$$
Therefore, under Convention M:
$$\boxed{ B(x,t) = [F(A(x,t), t)]^{-1}, \qquad F(A(x,t), t) = [B(x,t)]^{-1} }$$

---

## 3. Exact Componentwise Derivation of the Curl / Pullback Identity

Let $v(a)$ be a smooth vector field on $\mathbb{R}^3$, and let $A: \mathbb{R}^3 \to \mathbb{R}^3$ be a smooth diffeomorphism.
Consider the pullback of the differential 1-form $v_k da^k$ to $x$-space:
$$w_i(x) := \frac{\partial A_j}{\partial x_i}(x) \, v_j(A(x)) = B_{ji}(x) \, v_j(A(x)) = [B^T (v \circ A)]_i.$$

We compute the curl $(\nabla \times w)_i = \epsilon_{ijk} \partial_j w_k$ explicitly in components:
$$\partial_j w_k = \frac{\partial}{\partial x_j} \left( \frac{\partial A_l}{\partial x_k} v_l(A(x)) \right) = \frac{\partial^2 A_l}{\partial x_j \partial x_k} v_l(A(x)) + \frac{\partial A_l}{\partial x_k} \frac{\partial A_m}{\partial x_j} \frac{\partial v_l}{\partial a_m}(A(x)).$$
Taking the contraction with the Levi-Civita permutation symbol $\epsilon_{ijk}$:
$$(\nabla \times w)_i = \sum_{l=1}^3 v_l(A(x)) \underbrace{\epsilon_{ijk} \frac{\partial^2 A_l}{\partial x_j \partial x_k}}_{= 0 \text{ by symmetry}} + \epsilon_{ijk} \frac{\partial A_m}{\partial x_j} \frac{\partial A_l}{\partial x_k} \frac{\partial v_l}{\partial a_m}(A(x)).$$
Recall the algebraic cofactor identity for any $3 \times 3$ matrix $B$:
$$\epsilon_{ijk} B_{mj} B_{lk} = \epsilon_{ijk} \frac{\partial A_m}{\partial x_j} \frac{\partial A_l}{\partial x_k} = (\det B) \, \epsilon_{mln} [B^{-1}]_{in}.$$
Substituting this into the curl expression:
$$(\nabla \times w)_i = (\det B) \sum_{n=1}^3 [B^{-1}]_{in} \underbrace{\sum_{m,l=1}^3 \epsilon_{mln} \frac{\partial v_l}{\partial a_m}(A(x))}_{= \sum_{m,l=1}^3 \epsilon_{nml} \frac{\partial v_l}{\partial a_m} = (\nabla_a \times v)_n(A(x))}.$$
Thus:
$$\boxed{ (\nabla_x \times w)_i = (\det B) \, [B^{-1}]_{in} \, (\nabla_a \times v)_n(A(x)) }$$

### Conclusion of Derivation:
1. For general diffeomorphisms:
   $$\nabla_x \times \left( B^T (v \circ A) \right) = (\det B) \, B^{-1} (\nabla_a \times v)(A).$$
2. Under incompressibility ($\det B = 1$):
   $$\boxed{ \nabla_x \times \left( B^T (v \circ A) \right) = B^{-1} (\nabla_a \times v)(A) = F(A) (\nabla_a \times v)(A) }$$
3. The resulting vector multiplier acting on the initial vorticity vector $(\nabla_a \times v)$ is **strictly $B^{-1} \equiv F(A)$**, **NEVER $B^{-T}$ or $B^T$** under Convention M.
