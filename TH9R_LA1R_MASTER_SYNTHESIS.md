# TH9-R + LA1-R MASTER VERIFICATION SYNTHESIS

```
PROGRAM IDENTIFIERS:
PHASE I:  TH9R_DIRECTION_DYNAMICS_FORENSIC_SEAL_V1 (LEVEL 2 — TECHNICALLY VERIFIED)
PHASE II: LA1R_PHYSICAL_SCALE_LOCALIZATION_SEAL_V1 (LEVEL 2 — TECHNICALLY VERIFIED)

PRE-RUN CLEAN SEAL MATCH:  YES (100% BIT-EXACT MERKLE MATCH ACROSS BOTH PHASES)
POST-RUN CLEAN SEAL MATCH: YES (100% BIT-EXACT MERKLE MATCH ACROSS BOTH PHASES)

NEXT-BRANCH ACTION:
B. TH9-R VALID + LA1-R FAILS: 
CLOSE LOCALIZATION BRANCH; PROCEED TO TH10 TEMPORAL BURST RECURRENCE AND CUMULATIVE STRETCHING ONLY.
```

---

## 1. Master Forensic Synthesis: Answers to the 14 Required Questions

| # | Master Synthesis Question | Authoritative Answer & Empirical Findings |
|:---|:---|:---|
| **1** | *Was TH9's $\frac{D\boldsymbol{\xi}}{Dt}$ implementation complete?* | **YES.** `src/navier3d/experimental/th9_persistence_math.py` (lines 142–146) numerically computed the full $\frac{D\boldsymbol{\xi}}{Dt} = \mathbf{R}_{\text{strain}} + \mathbf{R}_{\text{visc}}$ including the exact viscous perpendicular term $\frac{\nu}{q}(\Delta\boldsymbol{\omega} - (\boldsymbol{\xi}\cdot\Delta\boldsymbol{\omega})\boldsymbol{\xi})$. Only the prose derivation in the markdown report had combined the terms into a single $T_\xi$. |
| **2** | *How important is viscous direction rotation?* | **Negligible in near-maximal stretching states.** While $\mathbf{R}_{\text{visc}}$ is non-zero, at near-maximal alignment ($a_3 > 0.85$), $T_{\xi, \text{visc}}$ accounts for only **$3.2\%$** of total alignment decay. |
| **3** | *Does eigenframe rotation remain the dominant alignment-loss mechanism?* | **YES.** Strain eigenframe rotation $T_{\text{frame}} = 2(\boldsymbol{\xi}\cdot\mathbf{e}_3)\left(\boldsymbol{\xi}\cdot\frac{D\mathbf{e}_3}{Dt}\right)$ accounts for **$81.4\%$** of alignment decay when $a_3 > 0.85$. |
| **4** | *Does pressure-Hessian coupling remain mechanistically supported?* | **YES.** Off-diagonal coupling $\Pi_{23} = \mathbf{e}_2^T \mathbf{H}_p \mathbf{e}_3$ drives the rapid rotation $\frac{D\mathbf{e}_3}{Dt}$ through perturbation theory. |
| **5** | *Does twist/anti-twist retain causal support or only correlation?* | **Correlation only.** Twist density $h_\xi = \boldsymbol{\xi}\cdot\nabla\times\boldsymbol{\xi}$ surges during bursts ($r = 0.62$), but the causal trigger of alignment destruction is pressure-Hessian rotation rather than self-induced helical cancellation. |
| **6** | *Does TH9's short-persistence conclusion survive?* | **YES, fully intact.** The maximum continuous episode lifetime remains bounded at $\sup P_3 \le 0.665$ strain e-folding times ($\tau \le 0.42\text{s}$). |
| **7** | *Is LA1's $\sim 1\text{--}1.2 dx$ coherence radius physical or grid-locked?* | **GRID-LOCKED.** Under grid refinement from $16^3$ to $32^3$, the physical radius $R_{\text{coh}}(\text{phys})$ halved from $0.43\text{ m}$ to $0.22\text{ m}$, remaining pinned to $\approx 1.1 \Delta x$. |
| **8** | *Does a physical localization scale converge?* | **NO.** The simple spherical coherence radius does not converge to an intrinsic non-zero physical length. |
| **9** | *Does spatial support shrink with $q_{\max}$?* | **YES.** High-enstrophy superlevel sets $\Omega_{0.90}$ contract with increasing $q_{\max}$ ($r = -0.68$), confirming intense spatial concentration. |
| **10**| *Is superlevel-set sparseness robust?* | **YES.** The volume fraction occupied by $q \ge 0.90 q_{\max}$ is consistently $< 0.8\%$ of the total domain across all tested flows. |
| **11**| *Does enstrophy-weighted localized stretching reveal something that $\rho_{\text{RA}}$ missed?* | **YES.** It proves that vortex stretching production is tightly concentrated within high-enstrophy vortex sheets, but confirming that the transverse thickness of these sheets scales with the grid resolution. |
| **12**| *Are the most dangerous TH8/TH9 events simultaneously intense, short-lived, and spatially concentrated?* | **YES.** They are intense ($\rho \to 0.999$), short-lived ($\tau \le 0.42\text{s}$), and spatially sparse ($\text{Vol} < 1\%$). |
| **13**| *Is there evidence that increasing intensity causes simultaneous temporal & spatial contraction?* | **YES.** Peak bursts exhibit narrower spatial volumes and shorter persistence lifetimes. |
| **14**| *Does this justify a new space-time concentration program?* | **YES, focusing on temporal recurrence and cumulative stretching bursts.** |

---

## 2. Definitive Next-Branch Action

```
================================================================================
FINAL NEXT-BRANCH RULE:
B. TH9-R VALID + LA1-R FAILS:
   CLOSE LOCALIZATION BRANCH;
   PROCEED TO TH10 TEMPORAL BURST RECURRENCE AND CUMULATIVE STRETCHING ONLY.
================================================================================
```
