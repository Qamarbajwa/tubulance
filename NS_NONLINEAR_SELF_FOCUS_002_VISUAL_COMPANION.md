# NS-NONLINEAR-SELF-FOCUS-002: Visual Research Companion — Dyadic Flux, Operator Split, and State-Distinguishing Dynamics

**Milestone:** `NS-NONLINEAR-SELF-FOCUS-002`  
**Parent Milestone:** `NS-NONLINEAR-SELF-FOCUS-001-R1`  
**Active Governance:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority:** `Mathematical Research Constitution v1.0.1`  

---

## 1. Exact Low/High Enstrophy Balance & Skew-Adjoint vs. Self-Adjoint Operator Split

```mermaid
flowchart LR
    subgraph LowBand["Low-Frequency Band P_{<=Q} omega (k_0 <= |k| < k_0 2^{Q+1})"]
        ELow["E_{<=Q}(t) = (1/2)||P_{<=Q} omega||_2^2"]
        SLowIntra["Intra-Band Stretching\nP_{<=Q}^{intra} = <S omega_{<=Q}, omega_{<=Q}>"]
        DLow["Viscous Loss\n-D_{<=Q} = -nu ||grad P_{<=Q} omega||_2^2"]
    end

    subgraph CrossBoundary["Cutoff Boundary |k| = k_0 2^{Q+1} (Exact R_Q = 0)"]
        PiAdv["Conservative Advective Flux (Skew-Adjoint A_u^* = -A_u)\nPi_Q^{adv}(t) = -<(u.grad)omega_{<=Q}, omega_{>Q}>\nLeaves (<=Q) with -Pi_Q^{adv}, Enters (>Q) with +Pi_Q^{adv}"]
        PCross["Cross-Scale Stretching Co-Production (Self-Adjoint M_S^* = +M_S)\nP_Q^{cross}(t) = <S omega_{<=Q}, omega_{>Q}>\nEnters BOTH (<=Q) and (>Q) with +P_Q^{cross}"]
    end

    subgraph HighBand["High-Frequency Band P_{>Q} omega (|k| >= k_0 2^{Q+1})"]
        EHigh["E_{>Q}(t) = (1/2)||P_{>Q} omega||_2^2"]
        SHighIntra["Intra-Band Stretching\nP_{>Q}^{intra} = <S omega_{>Q}, omega_{>Q}>"]
        DHigh["Viscous Cutoff Loss\n-D_{>Q} <= -nu k_0^2 2^{2(Q+1)} ||P_{>Q} omega||_2^2"]
    end

    SLowIntra --> ELow
    ELow --> DLow
    ELow -- "-Pi_Q^{adv}(t)" --> PiAdv
    PiAdv -- "+Pi_Q^{adv}(t)" --> EHigh
    PCross -- "+P_Q^{cross}(t)" --> ELow
    PCross -- "+P_Q^{cross}(t)" --> EHigh
    SHighIntra --> EHigh
    EHigh --> DHigh
```

---

## 2. Exact One-Shell Bandwidth Step and State-Distinguishing Branching (`CLM-042`)

```mermaid
flowchart TD
    Init["Initial State at t = t_0 in Shell Q=0 (|k| = sqrt(3) k_0 in [k_0, 2k_0))\nIdentical Instantaneous Invariants:\n||omega(t_0)||_2 = Omega_0, ||grad omega(t_0)||_2 = sqrt(3) k_0 Omega_0\nP(t_0) = 0, A(t_0) = 0, E_{>0}(t_0) = 0"]

    Init --> BranchA["State A: Beltrami / ABC Eigenflow\nomega_0^{(A)} = sqrt(3) k_0 u_0^{(A)}\nu_0^{(A)} x omega_0^{(A)} = 0 Pointwise"]
    Init --> BranchB["State B: Taylor-Green / Opposite-Helicity Triad\ns_k = +1, s_l = -1 on |k| = |l| = sqrt(3) k_0\n||P_1 curl(u_0^{(B)} x omega_0^{(B)})||_2 > 0"]

    BranchA --> OutA["Zero Nonlinear Drive Across Q=0:\nF_1^{(A)}(t_0) = 0, G_0^{(A)}(t_0) = 0\n==> Pi_0^{adv}(t) = 0, E_{>0}^{(A)}(t) = 0 for all t >= t_0"]
    BranchB --> Step1["Exact One-Shell Injection Into Shell C_1 ([2k_0, 4k_0)):\nF_{>0}^{(B)}(t_0) = P_1 curl(u_0^{(B)} x omega_0^{(B)}) != 0\nModes |m| = sqrt(6)k_0, sqrt(12)k_0 in C_1 (Zero in q >= 2)"]
    Step1 --> OutB["CLM-042 Duhamel Viscous-Discounted Lower Bound on [t_0, t_0 + Delta t]:\nE_{>0}^{(B)}(t_0 + Delta t) >= (1/4) psi_0(Delta t)^2 ||F_1^{(B)}(t_0)||_2^2 - (1/8) L_F^2 (Delta t)^4 > 0\nIntegral_{t_0}^{t_0+Delta t} Pi_0^{adv}[B](t) dt > 0"]
    OutB --> Barrier["Macroscopic Closure Barrier (NS-OBS-022):\n1. Viscous Factor psi_Q^2 <= (16 nu k_0^2 2^{2Q})^{-2} = O(nu^{-2} 2^{-4Q})\n2. Minimal Triad Phase Rotation C_{klm}(t) Reverses Sign at t_0 + T_{half}"]
```

---

## 3. Minimal Triad Helicity & Phase-Reversal Cycle (`NEG-EV-049`)

```mermaid
stateDiagram-v2
    [*] --> ResonantBeltrami: s_k = s_l, |k| = |l| (Same Helicity on Sphere)
    [*] --> ForwardPhase: s_k = +1, s_l = -1, C_{klm}(t_0) > 0 (Opposite Helicity)

    ResonantBeltrami --> ZeroTransfer: Gamma_m = |m|^2(s_k|k| - s_l|l|) = 0\nPi_Q^{omega,tot}(t) == 0 (Exact Beltrami Annihilation)
    ForwardPhase --> PeakHighMode: Enstrophy Transfers (<=Q) -> m in C_{Q+1}\nPi_Q^{omega,tot}(t) > 0 on [t_0, t_0 + T_{half})
    PeakHighMode --> BackscatterPhase: Triad Phase Passes pi/2 at t_0 + T_{half}\nC_{klm}(t) < 0 ==> Pi_Q^{omega,tot}(t) < 0 (Inverse Backscatter)
    PeakHighMode --> ViscousDamping: High-Shell Viscosity nu |m|^2 Damps Mode m\nCaps Peak Enstrophy at O(nu^{-2} 2^{-4Q} ||F_{Q+1}||_2^2)
```
