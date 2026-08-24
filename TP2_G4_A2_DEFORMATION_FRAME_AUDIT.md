# TP2-G4-A2: DEFORMATION FRAME & SPECTRAL PROJECTOR DYNAMICS

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2`  
**Governance Standard:** Autonomous Project Governance v2.9.4  
**Date:** 2026-08-25T00:26:30Z  

---

## 1. Lower-Endpoint Evolution of the Stochastic Deformation Tensor $D_s$

Recall from Gate `TP2-G1` and `TP2-G1R` that for $s \le T$ and fixed terminal point $x \in \mathbb{T}^3$, $A_{s, T}(x)$ satisfies the backward stochastic flow equation:
\[
d A_s(x) = -u(A_s(x), s) ds + \sqrt{2\nu} d\widetilde{B}_s, \quad A_T(x) = x.
\]
The spatial Jacobian of the backward map is $B_s(x) := J_{A_{s, T}}(x) = \nabla_x A_s(x)$, and the backward Cauchy deformation tensor is defined under Convention M as:
\[
D_s(x) := [J_{A_{s, T}}(x)]^{-1} = F_{s, T}(A_s(x)).
\]
For a smooth deterministic flow (or conditional realization), the lower endpoint derivative $\partial_s$ of the forward flow map $F_{s, T}(a)$ satisfies:
\[
\partial_s F_{s, T}(a) = -F_{s, T}(a) J_u(a, s) = -F_{s, T}(a) A(a, s).
\]
Evaluating at $a = A_s(x)$:
\[
\boxed{ \partial_s D_s = -D_s A_s },
\]
where $A_s := A(A_s(x), s) = J_u(A_s(x), s)$.

---

## 2. Evolution of the Right Cauchy–Green Metric Tensor $\Gamma_s$

Define the symmetric positive-definite metric tensor:
\[
\Gamma_s := D_s^T D_s \in SL(3, \mathbb{R}), \quad \det(\Gamma_s) = 1.
\]
Differentiating with respect to the lower endpoint $s$:
\[
\partial_s \Gamma_s = (\partial_s D_s)^T D_s + D_s^T (\partial_s D_s) = (-D_s A_s)^T D_s + D_s^T (-D_s A_s) = -A_s^T D_s^T D_s - D_s^T D_s A_s.
\]
Thus:
\[
\boxed{ \partial_s \Gamma_s = -A_s^T \Gamma_s - \Gamma_s A_s }.
\]

### 2.1 Strain and Vorticity Decomposition
Decompose $A_s = S_s + \Omega_s$, where $S_s = \frac{1}{2}(A_s + A_s^T)$ is symmetric and $\Omega_s = \frac{1}{2}(A_s - A_s^T)$ is skew-symmetric ($A_s^T = S_s - \Omega_s$).
Then:
\[
\partial_s \Gamma_s = -(S_s - \Omega_s) \Gamma_s - \Gamma_s (S_s + \Omega_s) = -(S_s \Gamma_s + \Gamma_s S_s) + (\Omega_s \Gamma_s - \Gamma_s \Omega_s).
\]
1. $-(S_s \Gamma_s + \Gamma_s S_s)$: Symmetric strain stretching of the metric tensor.
2. $[\Omega_s, \Gamma_s] = \Omega_s \Gamma_s - \Gamma_s \Omega_s$: Rigid rotational precession induced by fluid vorticity.

---

## 3. Spectral Decomposition and Projector Dynamics

Let $\Gamma_s$ have eigenvalues $\mu_i(s) = \sigma_i(s)^2$ with orthonormal eigenvectors $v_i(s)$ (the right singular vectors of $D_s$):
\[
\Gamma_s = \sum_{i=1}^3 \sigma_i^2 P_i, \quad P_i := v_i v_i^T, \quad P_i P_j = \delta_{ij} P_i, \quad \sum_{i=1}^3 P_i = I.
\]
In the simple spectrum regime ($\sigma_1 > \sigma_2 > \sigma_3 > 0$), we project $\partial_s \Gamma_s$:
\[
\partial_s \Gamma_s = \sum_{i=1}^3 (\partial_s \sigma_i^2) P_i + \sum_{i=1}^3 \sigma_i^2 (\partial_s P_i).
\]
Multiplying on the left by $P_j$ and right by $P_k$:
- For $j = k$:
\[
\boxed{ \partial_s (\sigma_i^2) = \operatorname{tr}(P_i \partial_s \Gamma_s) = -2 v_i^T A_s \Gamma_s v_i = -2 \sigma_i^2 (v_i^T S_s v_i) }.
\]
- For $j \neq k$:
Since $P_j P_k = 0 \implies (\partial_s P_j) P_k + P_j (\partial_s P_k) = 0$, we obtain:
\[
P_j (\partial_s \Gamma_s) P_k = (\sigma_k^2 - \sigma_j^2) P_j (\partial_s P_k) P_k.
\]
Therefore, the spectral projector evolution is:
\[
\boxed{ \partial_s P_i = \sum_{j \neq i} \frac{P_j (\partial_s \Gamma_s) P_i + P_i (\partial_s \Gamma_s) P_j}{\sigma_i^2 - \sigma_j^2} }.
\]

---

## 4. Rigorous Definition and Interpretation of Orientation Weights $p_i$

Given $G = J_\omega \in \mathbb{R}^{3 \times 3}$, $H = G G^T$, and $M = H / \|G\|_F^2$:
\[
p_i := \operatorname{tr}(P_i M) = \operatorname{tr}\left( v_i v_i^T \frac{G G^T}{\|G\|_F^2} \right) = \frac{v_i^T G G^T v_i}{\|G\|_F^2} = \frac{\|v_i^T G\|_2^2}{\|G\|_F^2}.
\]

### 4.1 Properties of $p_i$
1. **Positivity**: $p_i = \frac{\|G^T v_i\|_2^2}{\|G\|_F^2} \ge 0$ for all $i \in \{1, 2, 3\}$.
2. **Partition of Unity**:
\[
\sum_{i=1}^3 p_i = \frac{\sum_{i=1}^3 v_i^T G G^T v_i}{\|G\|_F^2} = \frac{\operatorname{tr}\left( \left(\sum_i v_i v_i^T\right) G G^T \right)}{\|G\|_F^2} = \frac{\operatorname{tr}(I G G^T)}{\|G\|_F^2} = 1.
\]

### 4.2 Physical Meaning: Component-Space vs Derivative-Space
Let $g_k = \nabla \omega_k \in \mathbb{R}^3$ be the gradient of the $k$-th vorticity component ($k \in \{1, 2, 3\}$), which forms the rows of $G$:
\[
G = \begin{pmatrix} g_1^T \\ g_2^T \\ g_3^T \end{pmatrix}, \quad G_{kj} = \partial_j \omega_k.
\]
Then $G G^T$ is the $3 \times 3$ matrix of inner products between the three vorticity component gradients:
\[
[G G^T]_{kl} = g_k \cdot g_l = \nabla \omega_k \cdot \nabla \omega_l.
\]
Therefore:
\[
p_i = \frac{1}{\|G\|_F^2} \sum_{k, l=1}^3 v_{i, k} v_{i, l} (g_k \cdot g_l) = \frac{\left\| \sum_{k=1}^3 v_{i, k} \nabla \omega_k \right\|_{L^2}^2}{\sum_{k=1}^3 \|\nabla \omega_k\|_{L^2}^2}.
\]
$$\boxed{ \text{Crucial Distinction: } p_i \text{ measures the alignment of the vorticity component combination } \sum_k v_{i, k} \omega_k \text{ in gradient space.} }$$
It is **not** the geometric direction of the physical $\nabla$ operator, but the projection of the vorticity vector's variation onto the stretching frame $v_i$.
