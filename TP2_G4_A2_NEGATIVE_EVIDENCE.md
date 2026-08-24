# TP2-G4-A2: NEGATIVE EVIDENCE & NO-GO AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2`  
**Governance Standard:** Autonomous Project Governance v2.9.4  
**Date:** 2026-08-25T00:29:30Z  

---

## 1. Explicit Negative Evidence Records for TP2-G4-A2

### Record NEG-EV-015: Neutral-Subspace Suppression Falsifies "$p_3$-Only" Suppression Model
- **Falsified Hypothesis**: Quadratic variation suppression $\eta \to 0$ under large deformation requires concentration of $J_\omega$ in the contracting direction $v_3$ ($p_3 \to 1$).
- **Counterexample / Proof**: Exact smooth periodic shear solutions $u = (U(y, t), 0, 0)$ on $\mathbb{T}^3$ have $p_1 = 0, p_2 = 1, p_3 = 0$ with $\sigma_2 = 1$ and $\sigma_1 \sim \alpha \to \infty$. Thus $\eta = 1 / \sigma_1^2 \to 0$ without any concentration in $v_3$.
- **Governing Obstruction**: `NS-OBS-005`
- **Verdict**: `FALSIFIED_SINGLE_SUPPRESSION_MODE`

### Record NEG-EV-016: Qualitative Positivity $p_1 > 0$ Fails to Guarantee Regularity
- **Falsified Hypothesis**: Proving $p_1(s) > 0$ qualitatively is sufficient to close the Navier–Stokes regularity problem.
- **Counterexample / Proof**: If $p_1(s) \sim e^{-K \int \|S\| dt} \to 0$ exponentially during high-strain events, $\mathcal{A}_{\text{grad}} \sim p_1 \sigma_1^2 + \sigma_2^2$ can remain bounded while $\sigma_1^2 \to \infty$. A scale-critical regularity theorem requires an a-priori quantitative lower bound $p_1 \ge c_0 > 0$.
- **Governing Obstruction**: `NS-OBS-005`
- **Verdict**: `EPISTEMIC_GAP`

### Record NEG-EV-017: Non-Transferability of Passive Alignment Theorems to Active Vorticity Gradients
- **Falsified Hypothesis**: Asymptotic alignment of passive material vectors with Lagrangian stretching directions (Encinas-Bartos & Haller 2024) applies directly to the vorticity gradient $G = J_\omega$.
- **Counterexample / Proof**: The exact PDE $(D_t - \nu \Delta) G = S G - G A + T$ contains the active source term $T_{ij} = (\partial_j S_{ik}) \omega_k$, which continuously generates gradient components independent of passive advective alignment.
- **Governing Obstruction**: `NS-OBS-007`
- **Verdict**: `FALSIFIED_PASSIVE_ANALOGY`

### Record NEG-EV-018: Inapplicability to Non-Smooth Leray-Hopf Solutions
- **Falsified Hypothesis**: The deformation frame equation $\partial_s \Gamma_s = -A_s^T \Gamma_s - \Gamma_s A_s$ applies to generic Leray weak solutions.
- **Counterexample / Proof**: Generic Leray weak solutions do not possess $C^1$ velocity fields; flow maps $A_s(x)$ are non-differentiable without higher regularity (`NS-OBS-006`).
- **Governing Obstruction**: `NS-OBS-006`
- **Verdict**: `ANALYTICAL_DOMAIN_BOUNDARY`
