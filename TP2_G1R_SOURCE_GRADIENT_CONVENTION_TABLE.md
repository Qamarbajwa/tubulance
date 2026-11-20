# TP2-G1R: PRIMARY SOURCE GRADIENT CONVENTION TABLE

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1R`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Primary Source Convention Audit  

---

## 1. Primary Source Convention Matrix

| Primary Source | Source Symbol | Source Component Convention | Project Convention M Equivalent | Transpose Required? | Definitive Mathematical Evidence in Source |
|---|---|---|---|---|---|
| **Constantin & Iyer (2008)**, CPAM 61, 330–345 | $\nabla X, \nabla X^{-1}$ | **Convention M** ($[\nabla X]_{ij} = \frac{\partial X_i}{\partial a_j}$) | $F_M = J_X, B_M = J_{X^{-1}}$ | **NO** (Source uses Convention M) | In Theorem 2.1, the Weber velocity formula is written $u = \mathbf{P} \mathbb{E}[ (\nabla X^{-1})^T u_0(X^{-1}) ]$, with explicit transpose $T$ for 1-form pullback; in Section 3 eq (3.2), vorticity representation is written $\omega = \mathbb{E}[ (\nabla X(X^{-1})) \omega_0(X^{-1}) ]$ without transpose. |
| **Constantin & Iyer (2011)**, Ann. Appl. Probab. 21 | $\nabla A, \nabla X$ | **Convention M** ($[\nabla A]_{ij} = \frac{\partial A_i}{\partial x_j}$) | $F_M = J_X, B_M = J_A$ | **NO** (Source uses Convention M) | Identical Jacobian convention to 2008 paper; normal/tangential boundary decomposition confirms standard differential geometry conventions. |
| **Eyink, Gupta & Zaki (2020)**, JFM 901, A2 (Part I) | $\nabla \xi, \nabla X$ | **Convention F** ($[\nabla \xi]_{ij} = \frac{\partial \xi_j}{\partial x_i}$) | $G_\xi = J_\xi^T = B_M^T$ | **YES** ($G_\xi = B_M^T$, so $(\nabla \xi)^{-T} = B_M^{-1} = F_M$) | In eq (2.3), Cauchy invariant is written in tensor contraction notation $Z(s) = \nabla \xi_s \cdot \omega(\xi_s, s)$. In fluid mechanics tensor notation, $M \cdot v \equiv M^T v$ or $M_{ji} v_j$, which represents the pushforward $F_{ij} \omega_j$. |
| **Mahithitarmmatorn (2026)**, arXiv:2608.16915 | $\nabla A, \mathcal{A}$ | **Convention M** ($[\nabla A]_{ij} = \frac{\partial A_i}{\partial x_j}$) | $\mathcal{A} = B_M = J_A$ | **NO** (Source uses Convention M) | In eq (2.1), Weber field is written $w = (\nabla A)^T u_0(A) = \mathcal{A}^T u_0(A)$. The inverse deformation gradient is defined as $\mathcal{A} = \nabla A = (\nabla X)^{-1}$, exactly matching Convention M. |
| **Modern JFM Backward Vorticity Literature** | $\widetilde D = (\nabla_a \widetilde X)^T = (\nabla_{x_f} \widetilde A)^{-T}$ | **Convention F** ($[\nabla f]_{ij} = \frac{\partial f_j}{\partial x_i}$) | $\nabla_F X = F_M^T, \nabla_F A = B_M^T$ | **YES** ($(\nabla_F A)^{-T} \equiv (B_M^T)^{-T} = B_M^{-1} = F_M$) | The printed inverse-transpose $(\nabla_F A)^{-T}$ is the exact translation of $(B_M^T)^{-T} = B_M^{-1}$ from Convention F into Convention M. |

---

## 2. Summary of Source Findings

1. Pure mathematical literature (Constantin & Iyer 2008, 2011; Mahithitarmmatorn 2026) operates strictly in **Convention M** ($[J]_{ij} = \partial_j f_i$).
2. Fluid dynamics literature (Eyink et al. 2020; modern JFM stochastic Cauchy papers) operates in **Convention F** ($[G]_{ij} = \partial_i f_j$).
3. The presence of the inverse-transpose $(\nabla A)^{-T}$ in JFM papers is mathematically necessitated by Convention F:
   $$(\nabla_F A)^{-T} \equiv (B_M^T)^{-T} \equiv B_M^{-1} \equiv F_M.$$
4. Both literatures describe the **identical physical stretching of vorticity vectors**.
