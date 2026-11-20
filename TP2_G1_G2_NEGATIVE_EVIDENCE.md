# TP2-G1 / G2: NEGATIVE EVIDENCE & NO-GO AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gates:** `TP2-G1` & `TP2-G2`  
**Governance:** Mid-Project Governance v2.9  
**Status:** Permanent Scientific Forensic Record  

---

## 1. Forensic Audit of Previous TP1 Statements

In the preceding increment report `TRAJECTORY_PERSISTENCE1_FINAL_REPORT.md` (Section 1, Bridge 2), the following statement was recorded:
$$\|\omega(t)\|_{L^\infty} \le \|\omega_0\|_{L^\infty} \mathbb{E}\left[ \|\mathbf{J}_t^{-1}\|_{L^\infty} \right].$$

### Deficiencies and Corrections:
1. **Undefined Jacobian Convention**:
   - The symbol $\mathbf{J}_t^{-1}$ was ambiguous regarding whether $\mathbf{J}_t$ denoted the forward flow Jacobian $\nabla_a X_t$ or the inverse flow Jacobian $\nabla_x A_t$.
   - **Correction**: Under the governed convention established in `TP2_G1_STOCHASTIC_CONVENTION_CONTRACT.md`, the vorticity deformation operator is explicitly $D_t^0(x) = F_{0,t}(A_{0,t}(x)) = (\nabla_x A_{0,t}(x))^{-1}$.
2. **Destruction of Stochastic Cancellation by Coarse Triangle Inequality**:
   - Moving the $L^\infty$ and matrix norm inside the expectation $\mathbb{E}[ \cdot ]$ replaces $\mathbb{E}[D \omega]$ by $\mathbb{E}[\|D\|] \|\omega\|$, completely discarding the stochastic phase cancellation and directional decorrelation across Brownian trajectories.
   - As proved by Mahithitarmmatorn (2026), $\|\mathbb{E} D\|$ can remain order $O(1)$ while $\mathbb{E}\|D\|$ grows arbitrarily large (or exponentially backward). A bound based on $\mathbb{E}[\|D\|]$ is super-exponentially loose and cannot close regularity.

---

## 2. Falsification of $\chi$ as an Autonomous Regularity Criterion

- **Hypothesis**: The bound $\chi(x,t;s) \le 1$ prevents blow-up of Navier–Stokes.
- **Falsification**:
  By the Cauchy–Schwarz inequality in probability space, for any random vector $Z \in L^2(\Omega_{\text{prob}})$,
  $$|\mathbb{E} Z|^2 \le \mathbb{E}|Z|^2 \implies \chi = \frac{|\mathbb{E} Z|^2}{\mathbb{E}|Z|^2} \le 1.$$
  This bound is an intrinsic geometric property of Hilbert space inner products. It holds identically for smooth, turbulent, and singular hypothetical blow-up solutions.
- **Verdict**: $\chi$ is an `EXACT_SCALE_INVARIANT_QUANTITY`, not a regularity theorem or continuation criterion by itself.

---

## 3. Low-Regularity Extrapolation Barrier (Galeati 2025 Boundary)

- **Misconception**: Because Galeati (2025) proved trajectory uniqueness for Leray solutions with $u_0 \in L^2$, the Constantin–Iyer representation and its deformation gradients $D_t^s(x)$ can be applied directly to generic Leray weak solutions.
- **Negative Evidence**:
  - Trajectory uniqueness is a property of almost every 1D path $t \mapsto X_t(a)$.
  - The deformation operator $D_t^s(x) = (\nabla_x A_{s,t}(x))^{-1}$ requires spatial differentiability ($C^1$ or $W^{1,p}$ with $p > d$) of the stochastic flow map.
  - Generic Leray solutions ($u \in L_t^\infty L_x^2 \cap L_t^2 H_x^1$) do not possess the spatial regularity required by Kunita's stochastic flow theorem.
  - **Governed Barrier**: The Constantin–Iyer representation is valid on the smooth existence interval $[0, T^*)$ of a classical/mild solution. Extrapolation to weak solutions without flow differentiability is strictly quarantined.
