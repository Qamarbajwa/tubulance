# TP2-G1: MATRIX CONVENTION CONVERSION CROSSWALK

**Authority:** Independent Verification Authority  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G1`  
**Governance:** Mid-Project Autonomous Governance v2.9  
**Status:** Authoritative Matrix Crosswalk  

---

## 1. Master Matrix Conversion Table

| Symbol | Flow Direction | Map Type | Differentiation Variable | Vector / Covector Action | Correct Matrix Representation | Primary Source |
|---|---|---|---|---|---|---|
| $F_{s,t}(a)$ | Forward ($s \to t$) | Forward trajectory $X_{s,t}(a)$ | Initial label $a$ ($\nabla_a$) | Tangent vector pushforward | $F_{s,t}(a) = \nabla_a X_{s,t}(a)$ | Kunita (1990); Constantin & Iyer (2008) |
| $J_{s,t}(x)$ | Backward ($t \to s$) | Inverse map $A_{s,t}(x) = X_{s,t}^{-1}(x)$ | Terminal position $x$ ($\nabla_x$) | 1-form pullback matrix | $\nabla_x A_{s,t}(x) = [F_{s,t}(A_{s,t}(x))]^{-1}$ | Constantin & Iyer (2008) eq (2.3) |
| $(\nabla_x A)^T$ | Backward ($t \to s$) | Inverse map $A_{s,t}(x)$ | Terminal position $x$ ($\nabla_x$) | 1-form pullback (Weber velocity) | $[\nabla_x A_{s,t}(x)]^T = [F_{s,t}(A_{s,t}(x))]^{-T}$ | Constantin & Iyer (2008) eq (2.4); Mahithitarmmatorn (2026) |
| $D_t^s(x)$ | Backward ($t \to s$) | Inverse map evaluation | Terminal position $x$ ($\nabla_x$) | Vorticity vector Cauchy multiplier | $D_t^s(x) = [\nabla_x A_{s,t}(x)]^{-1} = F_{s,t}(A_{s,t}(x))$ | Constantin & Iyer (2008) eq (3.2); Eyink, Gupta & Zaki (2020) eq (2.4) |
| $\nabla \xi_s(x)$ | Backward ($t \to s$) | Backward trajectory $\xi_s(x) = X(s; x, t)$ | Terminal position $x$ ($\nabla_x$) | Vorticity Cauchy multiplier | $\nabla \xi_s(x) \equiv D_t^s(x) = (\nabla_x A)^{-1}$ | Eyink, Gupta & Zaki (2020) Part I eq (2.3) |

---

## 2. Derivation of Transpose / Inverse Relations

1. **Relation between Forward and Backward Jacobians**:
   $$\nabla_x A_{s,t}(x) \cdot \nabla_a X_{s,t}(A_{s,t}(x)) = I_3 \implies \nabla_x A_{s,t}(x) = \left[ F_{s,t}(A_{s,t}(x)) \right]^{-1}.$$
2. **Transpose Relations**:
   $$\left( [\nabla_x A_{s,t}(x)]^T \right)^{-1} = \left( [\nabla_x A_{s,t}(x)]^{-1} \right)^T = [F_{s,t}(A_{s,t}(x))]^T = F_{s,t}(A_{s,t}(x))^T.$$
3. **Resolution of Literature Apparent Conflicts**:
   - The matrix appearing in the Weber velocity formula is $(\nabla A)^T = F^{-T}$ because velocity $u_i dx^i$ transforms as a differential 1-form.
   - The matrix appearing in the vorticity formula is $D = (\nabla A)^{-1} = F$ because vorticity 2-forms under 3D volume-preserving Hodge duality transform as tangent vectors.
   - Any literature notation writing $(\nabla \xi)^T$ or $J^{-T}$ in the vorticity formula is a covector-vs-vector transpose error. The mathematically correct operator on vorticity is $D = (\nabla A)^{-1} = F(A(x))$.
