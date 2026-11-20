# TP2-G1: FORWARD–BACKWARD STOCHASTIC REPRESENTATION EQUIVALENCE

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1 (Equivalence Derivation)`  
**Governance:** Mid-Project Governance v2.9  
**Status:** Authoritative Mathematical Derivation  

---

## 1. The Two Formulations

Let $u$ be a smooth solution of the 3D incompressible Navier–Stokes equations on $[0, T]$, $\omega = \nabla \times u$, and $\nu > 0$.

### Formulation A: Forward Stochastic Flow Formulation
Let $a \in \mathbb{R}^3$ and $s \le t$.
The forward stochastic flow $X_{s,t}(a)$ solves:
$$d_t X_{s,t}(a) = u(X_{s,t}(a), t) dt + \sqrt{2\nu} dW_t, \quad X_{s,s}(a) = a.$$
The forward Jacobian is $F_{s,t}(a) = \nabla_a X_{s,t}(a)$, satisfying:
$$\frac{d}{dt} F_{s,t}(a) = \nabla u(X_{s,t}(a), t) \, F_{s,t}(a), \quad F_{s,s}(a) = I_3, \quad \det F_{s,t}(a) = 1.$$
The inverse map is $A_{s,t}(x) = X_{s,t}^{-1}(x)$, so $X_{s,t}(A_{s,t}(x)) = x$.
In this formulation, the Cauchy contribution at $(x,t)$ pulled from time $s$ is:
$$Z_s^{x,t} = F_{s,t}(A_{s,t}(x)) \, \omega(A_{s,t}(x), s), \qquad \omega(x,t) = \mathbb{E}\left[ F_{s,t}(A_{s,t}(x)) \, \omega(A_{s,t}(x), s) \right].$$

### Formulation B: Backward-Terminal-Point Formulation (Constantin–Iyer / Weber)
In Constantin & Iyer (2008), the velocity field is represented via the stochastic Weber formula:
$$u(x,t) = \mathbf{P} \, \mathbb{E}\left[ (\nabla_x A_{s,t}(x))^T \, u(A_{s,t}(x), s) \right],$$
where $\mathbf{P}$ is the Leray projector ($\nabla \cdot \mathbf{P} v = 0$, $\mathbf{P} \nabla q = 0$).
Taking the curl on both sides defines the vorticity:
$$\omega(x,t) = \nabla_x \times u(x,t) = \nabla_x \times \mathbb{E}\left[ (\nabla_x A_{s,t}(x))^T \, u(A_{s,t}(x), s) \right].$$

---

## 2. Rigorous Algebraic Proof of Equivalence

We prove that for any smooth vector field $v(a)$ and smooth volume-preserving diffeomorphism $x \mapsto A(x)$:
$$\nabla_x \times \left( (\nabla_x A(x))^T v(A(x)) \right) = (\nabla_x A(x))^{-1} (\nabla_a \times v)(A(x)).$$

### Step 1: Component Expansion
Let $w(x) = (\nabla_x A(x))^T v(A(x))$. In index notation:
$$w_i(x) = \sum_{k=1}^3 \frac{\partial A^k}{\partial x_i} v_k(A(x)).$$
Taking the spatial partial derivative $\partial_j w_i = \frac{\partial w_i}{\partial x_j}$:
$$\frac{\partial w_i}{\partial x_j} = \sum_{k=1}^3 \frac{\partial^2 A^k}{\partial x_j \partial x_i} v_k(A(x)) + \sum_{k=1}^3 \sum_{l=1}^3 \frac{\partial A^k}{\partial x_i} \frac{\partial A^l}{\partial x_j} \frac{\partial v_k}{\partial a_l}(A(x)).$$

### Step 2: Commutation of Second Derivatives
The curl of $w$ has $m$-th component:
$$(\nabla_x \times w)_m = \sum_{i,j=1}^3 \epsilon_{mij} \frac{\partial w_i}{\partial x_j}.$$
Substituting the derivative expansion:
$$(\nabla_x \times w)_m = \sum_{k=1}^3 v_k(A(x)) \underbrace{\sum_{i,j=1}^3 \epsilon_{mij} \frac{\partial^2 A^k}{\partial x_j \partial x_i}}_{= 0 \text{ by symmetry}} + \sum_{k,l=1}^3 \frac{\partial v_k}{\partial a_l}(A(x)) \sum_{i,j=1}^3 \epsilon_{mij} \frac{\partial A^k}{\partial x_i} \frac{\partial A^l}{\partial x_j}.$$
Since $A(x) \in C^2$, Clairaut's theorem gives $\frac{\partial^2 A^k}{\partial x_j \partial x_i} = \frac{\partial^2 A^k}{\partial x_i \partial x_j}$.
Because $\epsilon_{mij} = -\epsilon_{mji}$ is skew-symmetric, the first term vanishes identically:
$$\sum_{i,j=1}^3 \epsilon_{mij} \frac{\partial^2 A^k}{\partial x_j \partial x_i} = 0.$$

### Step 3: Exact Minor/Cofactor Identity
Recall the fundamental matrix identity for any $3 \times 3$ invertible matrix $M$:
$$\sum_{i,j=1}^3 \epsilon_{mij} M_{ki} M_{lj} = (\det M) \sum_{n=1}^3 \epsilon_{kln} (M^{-1})_{nm}.$$
Setting $M = \nabla_x A(x)$, where $M_{ki} = \frac{\partial A^k}{\partial x_i}$:
$$\sum_{i,j=1}^3 \epsilon_{mij} \frac{\partial A^k}{\partial x_i} \frac{\partial A^l}{\partial x_j} = (\det \nabla_x A) \sum_{n=1}^3 \epsilon_{kln} \left[(\nabla_x A)^{-1}\right]_{nm}.$$
By incompressibility of the flow, $\det \nabla_x A = (\det F)^{-1} = 1$.
Therefore:
$$(\nabla_x \times w)_m = \sum_{n=1}^3 \left[(\nabla_x A)^{-1}\right]_{nm} \underbrace{\sum_{k,l=1}^3 \epsilon_{kln} \frac{\partial v_k}{\partial a_l}(A(x))}_{(\nabla_a \times v)_n(A(x))}.$$
In matrix-vector notation:
$$\nabla_x \times \left( (\nabla_x A(x))^T v(A(x)) \right) = (\nabla_x A(x))^{-1} (\nabla_a \times v)(A(x)).$$

### Step 4: Expectation and Leray Projection
Since differentiation in $x$ commutes with the expectation operator $\mathbb{E}$:
$$\nabla_x \times \mathbb{E}\left[ (\nabla_x A_{s,t}(x))^T u(A_{s,t}(x), s) \right] = \mathbb{E}\left[ \nabla_x \times \left( (\nabla_x A_{s,t}(x))^T u(A_{s,t}(x), s) \right) \right]$$
$$= \mathbb{E}\left[ (\nabla_x A_{s,t}(x))^{-1} (\nabla_a \times u)(A_{s,t}(x), s) \right] = \mathbb{E}\left[ (\nabla_x A_{s,t}(x))^{-1} \omega(A_{s,t}(x), s) \right].$$
Since $\nabla_x A_{s,t}(x) = [F_{s,t}(A_{s,t}(x))]^{-1}$, we have $(\nabla_x A_{s,t}(x))^{-1} = F_{s,t}(A_{s,t}(x))$.
Thus:
$$\mathbb{E}\left[ (\nabla_x A_{s,t}(x))^{-1} \omega(A_{s,t}(x), s) \right] \equiv \mathbb{E}\left[ F_{s,t}(A_{s,t}(x)) \omega(A_{s,t}(x), s) \right].$$
The two formulations are **algebraically and probabilistically identical**.

---

## 3. Matrix Inverse and Transpose Summary Table

| Object | Definition | Relation to Forward $F$ | Relation to Backward $J = \nabla_x A$ |
|---|---|---|---|
| Forward Deformation | $F_{s,t}(a) = \nabla_a X_{s,t}(a)$ | $F_{s,t}(a)$ | $J(X_{s,t}(a))^{-1}$ |
| Inverse Jacobian | $J_{s,t}(x) = \nabla_x A_{s,t}(x)$ | $[F_{s,t}(A_{s,t}(x))]^{-1}$ | $J_{s,t}(x)$ |
| **Vorticity Multiplier $D_t^s(x)$** | **Multiplier on $\omega(A(x), s)$** | **$F_{s,t}(A_{s,t}(x))$** | **$[\nabla_x A_{s,t}(x)]^{-1}$** |
| Weber Multiplier | Multiplier on $u(A(x), s)$ | $[F_{s,t}(A_{s,t}(x))]^{-T}$ | $[\nabla_x A_{s,t}(x)]^T$ |
