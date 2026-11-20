# TP2 Literature / Claim Matrix

**Cutoff:** 23 August 2026  
**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Status:** literature/research audit only; not a proof artifact and not a canonical theorem-state update by itself.

## TP2 object under audit

\[
Z_s^{x,t}=D_t^s(x)\,\omega(A_t^s(x),s),\qquad
\omega(x,t)=\mathbb E Z_s^{x,t},
\]

with proposed dimensionless stochastic Cauchy coherence

\[
\chi(x,t;s)=\frac{|\mathbb E Z_s^{x,t}|^2}{\mathbb E|Z_s^{x,t}|^2}\in[0,1].
\]

The exact variance identity is

\[
|\omega(x,t)|^2=\mathbb E|Z_s^{x,t}|^2-\operatorname{Var}(Z_s^{x,t}).
\]

This matrix is intended to be **complete for the theorem/result families that materially constrain TP2**: critical regularity, vorticity/strain geometry, blow-up exclusion, finite-time deformation, stochastic Lagrangian representation, stochastic Cauchy invariants, covariance/cancellation, weak-solution trajectory uniqueness, and current no-go evidence. It is not a bibliography of every Navier–Stokes regularity criterion ever published.

### Legend

- **CRITICAL**: invariant at Navier–Stokes parabolic scaling.
- **ENERGY/SUPERCRITICAL GAP**: available a-priori energy information lies below the critical regularity threshold.
- **COVARIANT REPRESENTATION**: exact representation respects Navier–Stokes scaling but is not itself a continuation norm.
- **χ overlap**: `NONE`, `INDIRECT`, `MODERATE`, `DIRECT`, `VERY DIRECT`.

---

## A. Rigorous regularity, blow-up and geometric constraints

| Paper / theorem | Exact result | Main assumptions | Scaling | Trajectory dependence | Geometry dependence | Stochastic component | What it rules out | What remains open | χ overlap |
|---|---|---|---|---|---|---|---|---|---|
| **Leray (1934)** | Global finite-energy weak solutions exist in 3D. | Divergence-free finite-energy data; weak formulation. | ENERGY/SUPERCRITICAL GAP | None | None | None | Nonexistence of all global weak solutions. | Smoothness and uniqueness; mechanism preventing singularity. | INDIRECT |
| **Caffarelli–Kohn–Nirenberg (1982)** | Suitable weak solutions are regular outside a singular set of parabolic 1-dimensional Hausdorff measure zero. | Suitable weak solution + local energy inequality. | Local ε-regularity is scale critical. | None | Space-time concentration geometry. | None | Large/extended singular sets. | Whether singularities exist at all; dynamical exclusion mechanism. | INDIRECT |
| **Beale–Kato–Majda (1984, Euler)** | Smooth Euler breakdown requires divergence of accumulated maximum vorticity, classically \(\int_0^T\|\omega\|_\infty dt=\infty\). | Smooth 3D Euler solution. | Scale-invariant in Euler scaling; history criterion. | Time-history implicit | Vorticity magnitude | None | Breakdown with finite accumulated maximum vorticity. | Viscous NS closure; no mechanism forcing finiteness. | MODERATE |
| **Constantin–Fefferman (1993)** | Sufficient coherence of vorticity direction in high-vorticity regions implies smoothness. | Smooth/localized data; directional-coherence hypothesis where vorticity is large. | Geometry-sensitive; later work sharpens critical thresholds. | Frozen-time geometry | **Direct vorticity-direction geometry** | None | Blow-up while high-vorticity directions remain sufficiently coherent. | Why NS dynamics should enforce the required coherence. | MODERATE–HIGH |
| **Nečas–Růžička–Šverák (1996)** | Backward Leray self-similar profile in \(L^3(\mathbb R^3)\) is trivial. | Exact backward self-similar ansatz; profile \(U\in L^3\). | **CRITICAL** | None | Self-similar geometry | None | Major exact self-similar/type-I scenario in critical \(L^3\). | Non-self-similar/type-II scenarios. | INDIRECT |
| **Constantin–Fefferman–Majda (1996, Euler)** | Vortex-line geometric constraints exclude classes of Euler blow-up scenarios. | Smooth Euler; geometric assumptions on vortex lines. | N/A to viscous NS | Deterministic vortex-line evolution | Strong | None | Geometrically regular Euler blow-up scenarios. | Viscous/stochastic analog and unconditional control. | MODERATE |
| **Koch–Tataru (2001)** | Small divergence-free data in \(BMO^{-1}\) yield global well-posed solutions. | Small critical \(BMO^{-1}\) data. | **CRITICAL** | None | None | None | Blow-up from sufficiently small critical data. | Large critical data; no persistence mechanism. | INDIRECT |
| **Beirão da Veiga–Berselli (2002)** | Vorticity-direction coherence criteria are relaxed to a family reaching the \(1/2\)-Hölder threshold; under the stated conditions a weak solution becomes regular. | Weak solution, suitable initial regularity, directional Hölder/Sobolev control in high-vorticity region. | **CRITICAL at the 1/2-Hölder threshold** | Frozen-time geometry | **Direct direction coherence** | None | Blow-up under critically coherent vorticity direction. | No theorem forcing the coherence a priori. | MODERATE–HIGH |
| **Escauriaza–Seregin–Šverák (2003)** | Endpoint \(u\in L_t^\infty L_x^3\) implies regularity/smoothness. | Appropriate weak/strong solution setting; endpoint critical bound. | **CRITICAL** | None | None | None | Blow-up while endpoint \(L^3\) remains bounded. | Deriving the critical bound from energy-level information. | **Key non-circularity benchmark** |
| **Deng–Hou–Yu (2005, Euler)** | Local vortex-filament geometry yields non-blow-up conditions and maximum-stretching bounds. | Euler; control of evolving vortex-line length/curvature/direction divergence. | N/A to NS | Deterministic evolving structures | Strong | None | Several coherent vortex-filament blow-up scenarios. | Viscous/stochastic counterpart; unconditional persistence bound. | MODERATE |
| **Grujić (2013)** | One-dimensional sparseness of intense velocity/vorticity super-level sets at analyticity scales prevents finite-time singularity; gives scaling-critical geometric conditions. | Mild solution near candidate singular time; quantified super-level-set sparseness. | **CRITICAL** | None | Spatial intermittency/sparseness | None | Blow-up when intense regions become sufficiently sparse. | Why NS must enforce that sparseness; no stochastic-history closure. | MODERATE |
| **Tao (2014/2016, averaged NS)** | An averaged NS nonlinearity preserving the energy cancellation can blow up in finite time. | Modified/averaged bilinear nonlinearity, not true NS. | Designed to preserve NS-like scaling/energy structure. | None | Finer nonlinear/Fourier structure matters | None | Proof strategies using only energy identity plus generic upper-bound harmonic analysis. | Which finer true-NS structure blocks the cascade. | INDIRECT but decisive no-go |
| **Miller / Neustupa–Penel strain-eigenvalue line** | Blow-up requires divergence of scale-critical norms of the positive middle strain eigenvalue \(\lambda_2^+\); finiteness gives continuation. | Mild/strong NS; critical mixed norm of \(\lambda_2^+\). | **CRITICAL**, \(2/p+3/q=2\) for strain. | Time-integrated Eulerian history | **Strain eigenvalue geometry** | None | Blow-up without persistent critical planar stretching/axial compression. | Why critical \(\lambda_2^+\) control should follow a priori. | MODERATE–HIGH |
| **Miller (2021), locally anisotropic vorticity** | Scale-critical control of vorticity projected onto a varying plane gives regularity, under control of the varying normal. | Mild NS; projected vorticity in critical \(L_t^4L_x^2\)-type condition; regular plane field. | **CRITICAL** | None | Local anisotropic vorticity geometry | None | Blow-up when selected vorticity directions remain critically controlled. | No stochastic/history mechanism enforcing the condition. | MODERATE–HIGH |
| **Miller (2024/2026), strain–vorticity interaction** | Exact identity \(\langle-\Delta S,\omega\otimes\omega\rangle=0\); model equation is globally regular; new NS criteria clarify depletion by advection. | Divergence-free fields / corresponding mild-solution hypotheses. | Exact structural identity; criteria respect critical NS structure. | Mostly Eulerian | Strain–vorticity cancellation | None | Simplistic norm-only descriptions of the nonlinearity. | Turning structural depletion into unconditional NS regularity. | HIGH |
| **Chen–Galdi–Poggi–Schikorra (2026 preprint)** | Refines Serrin interior regularity for distributional solutions under local critical \(L_t^{s'}L_x^s\), \(2/s'+3/s=1\), with substantially relaxed time-integrability assumptions. | Distributional solution + stated local critical integrability; extra local condition in part of exponent range. | **CRITICAL** | None | None | None | More weakly formulated critical-space singular scenarios. | Still conditional on critical integrability. | **Key non-circularity benchmark** |

---

## B. Lagrangian, deformation-history and stochastic structure

| Paper / theorem | Exact result | Main assumptions | Scaling | Trajectory dependence | Geometry dependence | Stochastic component | What it rules out / establishes | What remains open | χ overlap |
|---|---|---|---|---|---|---|---|---|---|
| **Lüthi–Tsinober–Kinzelbach (2005), experiment** | Lagrangian velocity-gradient measurements show vortex lines and material lines do not evolve identically; viscosity is important in vorticity dynamics/alignment. | Quasi-homogeneous isotropic turbulence, finite Reynolds number, 3D particle tracking. | N/A | **Deterministic Lagrangian measurement** | Vorticity/strain alignment | No | Naive physical identification of viscous vorticity with an infinitesimal material line. | No theorem-level regularity implication. | MODERATE |
| **Chevillard–Meneveau (2006), Recent Fluid Deformation** | Builds a stochastic Lagrangian velocity-gradient closure where pressure/viscous effects depend on recent deformation history and reproduces important turbulence statistics. | Statistical closure model; not exact NS theorem. | N/A | **Finite-time deformation history** | Velocity-gradient/strain | Model stochastic forcing | Demonstrates that recent history contains predictive information missing from instantaneous strain. | Heuristic closure; high-Re limitations; no regularity theorem. | MODERATE |
| **Constantin–Iyer (2008)** | Exact stochastic Lagrangian representation of smooth NS; vorticity is the expectation of stochastic deformation of initial vorticity. | Smooth solution regime; periodic or decaying whole-space setting; differentiable stochastic flow. | **COVARIANT REPRESENTATION** | **Stochastic** | Deformation gradient | **Central** | Establishes an exact stochastic history representation of viscosity and stretching. | Representation alone gives no a-priori deformation/cancellation bound sufficient for global regularity. | **DIRECT** |
| **Robinson–Sadowski (2009)** | Under stated weak-solution assumptions, particle trajectories are unique for a.e. initial point; related suitable-weak result covers \(H^{1/2}\) data. | Weak/suitable solution plus specified extra regularity. | Not a new critical regularity theorem. | **Deterministic trajectories** | Singular-set avoidance | Limited | Shows trajectory meaning survives below classical smoothness under extra assumptions. | Generic Leray-level trajectory theory was not yet reached. | MODERATE |
| **Constantin–Iyer (2011), boundaries** | Extends stochastic-Lagrangian representation to domains with boundaries and incorporates boundary-vorticity influence. | Smooth bounded-domain setting. | COVARIANT REPRESENTATION with boundary terms | **Stochastic** | Boundary-vorticity geometry | **Central** | Shows stochastic history representation is not confined to periodic/whole-space flows. | Boundary generation complicates any universal closure. | DIRECT |
| **Moriconi–Pereira (2013)** | Defines first/second-order **strain persistence times** from Lagrangian strain-eigenvalue statistics; connects them heuristically to vorticity statistics. | DNS-informed ensembles + heuristic closure hypotheses. | N/A | **Lagrangian time correlations** | Strain eigenvalues | No | Shows one naive strain timescale is inadequate and explicitly elevates persistence duration. | No rigorous NS regularity result. | MODERATE–HIGH |
| **Ni–Ouellette–Voth (2014)** | DNS shows vorticity preferentially aligns with the strongest **finite-time Lagrangian stretching direction** defined by the Cauchy–Green tensor, more strongly than with instantaneous strain eigenvectors. | DNS of isotropic turbulence. | N/A | **Finite-time deformation** | Alignment geometry | No | Instantaneous Eulerian strain is not the complete stretching/alignment history. | No blow-up/continuation theorem. | HIGH |
| **Haller et al. (2020), active barriers** | Derives objective material surfaces that maximally inhibit diffusive transport of active vector fields such as vorticity; the governing field involves a time-averaged pullback of diffusive terms. | Smooth general flows. | Geometric representation, not a regularity norm. | **Finite-time Lagrangian pullback** | Coherent transport barriers | No explicit Brownian paths | Establishes exact history-sensitive geometry of viscous vorticity transport. | Does not control maximum vorticity or prove continuation. | HIGH |
| **Eyink–Gupta–Zaki (2020), Part I** | Develops stochastic Cauchy invariants; verifies conservation of their mean in DNS events; variance grows exponentially backward, demonstrating stochastic Lagrangian chaos. | Exact smooth-flow representation + Monte Carlo evaluation of DNS histories. | COVARIANT REPRESENTATION / statistics | **Stochastic backward histories** | Deformation + orientation | **Central** | Shows conserved mean can coexist with very large path-to-path dispersion. | No theorem that variance growth universally depletes terminal vorticity or prevents blow-up. | **VERY DIRECT** |
| **Eyink–Gupta–Zaki (2020), Part II** | In channel turbulence, interior vorticity arises from broadly distributed stochastic histories; opposite-sign Lagrangian contributions can rotate and cancel (“virtual reconnection”). | DNS channel flow + exact stochastic representation. | N/A for empirical statistics | **Stochastic** | Orientation/sign cancellation | **Central** | Demonstrates physically that cross-history cancellation is real and dynamically important. | No universal quantitative lower bound on cancellation or upper bound on coherence. | **VERY DIRECT** |
| **Encinas-Bartos–Haller (2024)** | Derives asymptotic links between vorticity alignment and Lyapunov/finite-time stretching directions in 3D flows, including viscous settings. | Smooth flow; key asymptotic statements include bounded-vorticity-type hypotheses. | N/A as continuation criterion | **Finite-time/Lyapunov history** | Strong alignment geometry | No | Gives rigorous connections between accumulated stretching and vorticity orientation. | Cannot be used circularly to prove bounded vorticity when boundedness is assumed. | HIGH, but circularity-sensitive |
| **Galeati (2025)** | For any Leray solution with \(u_0\in L^2\), deterministic and stochastic Lagrangian trajectories are unique for Lebesgue-a.e. initial condition; with \(u_0\in H^{1/2}\), pathwise stochastic uniqueness holds from every initial point. | Leray solution; \(L^2\) data for a.e. result; \(H^{1/2}\) for stronger stochastic result. | Energy-class result; \(H^{1/2}\) is velocity-critical. | **Deterministic + stochastic** | None directly | **Yes** | Removes a major objection that trajectories become meaningless at Leray regularity. | Does **not** provide differentiable flow/Jacobian control at generic Leray regularity. | **DIRECT foundational** |
| **Mahithitarmmatorn (24 Jul 2026 preprint)** | Derives closed deterministic mean/covariance equations for the stochastic Weber field, second moment of inverse deformation gradient and two-point covariance; gives explicit counterexamples showing \(\|\mathbb ED\|\) does not control \(\mathbb E\|D\|\); obtains a gauge-invariant quotient criterion equivalent to Serrin; explicitly makes no global-regularity claim. | Smooth NS on \(\mathbb T^3\); Constantin–Iyer Weber representation. | **COVARIANT; quotient criterion critical/Serrin-equivalent** | **Stochastic** | Deformation/covariance | **Central** | Rules out a naive mean-deformation → mean-norm closure; proves covariance cannot simply be ignored. | A non-circular estimate converting covariance structure into critical regularity remains missing. | **VERY DIRECT — closest current overlap** |

---

## C. Weak-solution/no-go and physical evidence relevant to TP2

| Paper / result | Exact result | Main assumptions | Scaling | Trajectory dependence | Geometry dependence | Stochastic component | What it rules out / indicates | What remains open | χ overlap |
|---|---|---|---|---|---|---|---|---|---|
| **Buckmaster–Vicol (2019)** | Finite-energy distributional NS weak solutions can be nonunique in the weak class constructed. | Broad finite-energy weak class; convex integration. | Weak-class phenomenon | None | Intermittent convex-integration geometry | No | Any assumption that finite energy alone guarantees classical uniqueness. | Leray-Hopf/suitable/smooth uniqueness not settled by this theorem. | INDIRECT |
| **Hou–Wang–Yang (2025 preprint)** | Claims a rigorous computer-assisted construction of nonunique **unforced Leray–Hopf** solutions via a self-similar profile and unstable eigenpair. | Computer-assisted verification around a specific self-similar construction. | Self-similar/critical structure | None | Self-similar spectral geometry | No | If independently confirmed/accepted, a major weak-solution uniqueness scenario. | Preprint status; does not answer smooth-data global regularity. | INDIRECT |
| **Emam–Kamal–Johnson (accepted 29 Jul 2026, Phys. Rev. Fluids)** | DNS removes viscous tilting of vorticity while retaining other dynamics; turbulence changes drastically and the energy spectrum departs strongly from normal NS behavior. | DNS of isotropic turbulence with a deliberately modified vorticity evolution. | N/A | Compares orientation/stretching histories | **Strong directional geometry** | No Brownian paths | Strong physical evidence that viscous directional realignment is essential, not a negligible correction. | No theorem tying viscous tilting to critical coherence decay or regularity. | **HIGH physical relevance** |

---

# Claim-by-claim consequences for TP2

## 1. “History matters” is already known

Finite-time deformation, strain persistence time, vortex-line evolution, Lyapunov/Cauchy–Green alignment and stochastic histories are established research themes.

**Therefore TP2 novelty cannot simply be:** “trajectory history matters.”

## 2. “Direction/coherence matters” is already known

Constantin–Fefferman, Beirão da Veiga–Berselli, Grujić, Miller and related geometric criteria already prove that directional/geometric organization can determine whether intense vorticity remains regular.

**Therefore TP2 novelty cannot simply be:** “vorticity direction/coherence matters.”

## 3. “Viscosity has a stochastic Lagrangian representation” is established

Constantin–Iyer gives the exact representation; Eyink–Gupta–Zaki develops stochastic Cauchy invariants and demonstrates large stochastic-history variance/cancellation in DNS.

**Therefore TP2 cannot claim novelty for stochastic Lagrangian representation or stochastic Cauchy invariants.**

## 4. Expected deformation norm is too coarse to be the primary new closure

The 2026 Weber mean/covariance work gives explicit counterexamples to inferring expected deformation norm from mean deformation.

This strengthens the warning that applying

\[
|\mathbb EZ|\le \mathbb E|Z|
\]

too early may remove precisely the cancellation that distinguishes viscous stochastic dynamics.

## 5. Critical-space non-circularity is the main theorem gate

Any TP2 criterion must be compared against:

- Ladyzhenskaya–Prodi–Serrin;
- Escauriaza–Seregin–Šverák \(L_t^\infty L_x^3\);
- critical strain-eigenvalue criteria;
- critical vorticity-direction/anisotropic criteria;
- 2026 refined Serrin interior criteria.

If a proposed bound on \(\chi\), covariance or stochastic deformation requires one of these critical controls as an input, the result is a **conditional reformulation**, not a closure of the Millennium gap.

## 6. Weak-solution trajectory language survives much deeper than classical smoothness

Galeati 2025 substantially strengthens the foundation for discussing deterministic/stochastic trajectories for Leray solutions.

But a crucial separation remains:

\[
\text{trajectory existence/uniqueness}
\not\Rightarrow
\text{differentiable stochastic flow/Jacobian control}.
\]

TP2 must not import Constantin–Iyer deformation-gradient formulas into generic Leray regularity without an independent theorem justifying the needed differentiability.

---

# The genuine mathematical gap

After the above theorem-by-theorem comparison, the missing result is **not** any of the following:

- stretching amplifies vorticity;
- accumulated exposure matters;
- vorticity geometry matters;
- finite-time deformation matters;
- viscosity can be represented with stochastic trajectories;
- stochastic Cauchy invariants exist;
- stochastic histories can have large variance;
- stochastic contributions can cancel.

Those are already present in the literature at various levels of rigor.

The unresolved chain is:

\[
\boxed{
\text{Navier–Stokes a-priori information}
\Longrightarrow
\text{quantitative stochastic-history decoherence/cancellation}
\Longrightarrow
\text{critical terminal-vorticity control}
\Longrightarrow
\text{continuation/global regularity}.
}
\]

More specifically, no source in this audit proves a non-circular, scale-critical bound of the form

\[
\chi(x,t;s)\le \Phi(\text{a-priori controlled NS data}),
\]

or

\[
\chi(x,t;s)\,\mathbb E|Z_s^{x,t}|^2
\le
\Psi(\text{a-priori controlled NS data}),
\]

or an equivalent maximizer/spacetime-integrated estimate that is both:

1. strong enough to imply a known continuation criterion; and
2. derived without assuming Serrin/BKM/critical-strain/critical-vorticity control in disguise.

That is the sharpest genuine TP2 gap found in this audit.

---

# TP2 gates implied by the literature

## TP2-G1 — Representation convention
Prove forward/backward Constantin–Iyer vorticity formulas with one fixed Jacobian convention. No ambiguous \(J^{-1}\), \(J^{-T}\), \(F\), \(A\), or \(D\).

## TP2-G2 — Exact scaling
Compute Navier–Stokes scaling of:

- \(Z_s^{x,t}\);
- \(\mathbb E|Z|^2\);
- \(\operatorname{Var}(Z)\);
- \(\chi\);
- every candidate time/space integral.

A proposed continuation criterion must be critical or stronger in a non-circular sense.

## TP2-G3 — Vorticity-Cauchy covariance evolution
Derive the exact backward-Itô / deterministic covariance equation for the **vorticity Cauchy contribution** \(Z\), rather than assuming the Weber-velocity covariance equation transfers unchanged.

## TP2-G4 — Non-circularity
Attempt closure from only genuinely available inputs such as:

- Leray energy inequality;
- incompressibility;
- exact NS identities;
- exact stochastic representation where justified.

If Serrin/BKM/critical strain is inserted as an assumption, classify the result as `CONDITIONAL_REFORMULATION`.

## TP2-G5 — Geometry-equivalence
Determine whether control of \(\chi\) is already equivalent to, stronger than, weaker than, or independent of:

- Constantin–Fefferman directional coherence;
- \(1/2\)-Hölder vorticity-direction control;
- middle strain-eigenvalue criteria;
- Grujić sparseness;
- finite-time Cauchy–Green/Lyapunov alignment.

## TP2-G6 — Counterexample independence tests
Construct smooth exact/model flows exhibiting:

1. large \(\mathbb E|Z|^2\) with small \(\chi\);
2. large \(\mathbb E|Z|^2\) with \(\chi\approx1\);
3. modest deformation with high \(\chi\).

This determines whether \(\chi\) contains independent information or merely re-encodes deformation magnitude.

## TP2-G7 — Low-regularity boundary
Use Galeati only for trajectory existence/uniqueness unless a separate theorem provides the flow differentiability/Jacobian needed for \(D_t^s\).

## TP2-G8 — Viscous-tilting bridge
Derive the exact vorticity-direction equation and investigate whether the viscous directional terms can quantitatively force growth of stochastic variance or loss of \(\chi\). This is the most direct potential bridge between the 2026 viscous-tilting DNS evidence and a rigorous TP2 mechanism.

---

# Priority ordering after the audit

1. **TP2-G1 + G2:** representation and scaling must be sealed first.
2. **TP2-G3:** derive the exact \(Z\)-covariance/variance evolution.
3. **TP2-G6:** attack the candidate quantity with counterexamples before building a theorem around it.
4. **TP2-G5:** prove whether \(\chi\) is genuinely new information relative to existing geometric criteria.
5. **TP2-G4:** only then attempt a critical continuation bridge.
6. **TP2-G8:** connect directional viscosity to stochastic decoherence if the exact equations support it.

The best current TP2 hypothesis is therefore:

\[
\boxed{
\text{Dangerous growth requires simultaneous persistence of}
\quad
\text{pathwise amplification}
+\text{stretching alignment}
+\text{vorticity-direction coherence}
+\text{stochastic cross-history coherence}.
}
\]

This remains a **hypothesis**, not a theorem.

---

# Primary/current source register

- Caffarelli, Kohn & Nirenberg (1982), *Partial regularity of suitable weak solutions of the Navier–Stokes equations*, CPAM 35, 771–831, DOI: `10.1002/cpa.3160350604`.
- Beale, Kato & Majda (1984), *Remarks on the breakdown of smooth solutions for the 3-D Euler equations*, CMP 94, 61–66, DOI: `10.1007/BF01212349`.
- Constantin & Fefferman (1993), *Direction of vorticity and the problem of global regularity for the Navier–Stokes equations*, IUMJ 42, 775–789, DOI: `10.1512/iumj.1993.42.42034`.
- Nečas, Růžička & Šverák (1996), *On Leray's self-similar solutions of the Navier–Stokes equations*, Acta Math. 176, 283–294, DOI: `10.1007/BF02551584`.
- Koch & Tataru (2001), *Well-posedness for the Navier–Stokes equations*, Adv. Math. 157, 22–35.
- Beirão da Veiga & Berselli (2002), *On the regularizing effect of the vorticity direction in incompressible viscous flows*, Differential Integral Equations 15, 345–356, DOI: `10.57262/die/1356060864`.
- Escauriaza, Seregin & Šverák (2003), *L3,∞-solutions of the Navier–Stokes equations and backward uniqueness*, Russian Math. Surveys 58, 211–250, DOI: `10.1070/RM2003v058n02ABEH000609`.
- Lüthi, Tsinober & Kinzelbach (2005), *Lagrangian measurement of vorticity dynamics in turbulent flow*, JFM 528, 87–118, DOI: `10.1017/S0022112004003283`.
- Chevillard & Meneveau (2006), *Lagrangian dynamics and statistical geometric structure of turbulence*, PRL 97, 174501, DOI: `10.1103/PhysRevLett.97.174501`.
- Constantin & Iyer (2008), *A stochastic Lagrangian representation of the three-dimensional incompressible Navier–Stokes equations*, CPAM 61, 330–345, DOI: `10.1002/cpa.20192`, arXiv:`math/0511067`.
- Robinson & Sadowski (2009), particle-trajectory uniqueness papers, CMP 290, 15–22 and Nonlinearity 22, 2093–2099.
- Constantin & Iyer (2011), *A stochastic-Lagrangian approach to the Navier–Stokes equations in domains with boundary*, Ann. Appl. Probab. 21.
- Grujić (2013), *A geometric measure-type regularity criterion for solutions to the 3D Navier–Stokes equations*, Nonlinearity 26, 289–296, arXiv:`1111.0217`.
- Moriconi & Pereira (2013), *Vorticity Statistics and the Time Scales of Turbulent Strain*, Phys. Rev. E 88, 013005, arXiv:`1204.5150`.
- Ni, Ouellette & Voth (2014), *Alignment of vorticity and rods with Lagrangian fluid stretching in turbulence*, JFM 743, R3, DOI: `10.1017/jfm.2014.32`.
- Tao (2016), *Finite time blowup for an averaged three-dimensional Navier–Stokes equation*, JAMS 29, 601–674, arXiv:`1402.0290`.
- Buckmaster & Vicol (2019), *Nonuniqueness of weak solutions to the Navier–Stokes equation*, Ann. Math. 189, 101–144, DOI: `10.4007/annals.2019.189.1.3`.
- Miller (2020), *A regularity criterion ... involving only the middle eigenvalue of the strain tensor*, Arch. Rational Mech. Anal. 235, 99–139, arXiv:`1710.05569`.
- Haller et al. (2020), *Objective barriers to the transport of dynamically active vector fields*, JFM 905, A17, arXiv:`2002.06569`.
- Eyink, Gupta & Zaki (2020), *Stochastic Lagrangian Dynamics of Vorticity*, Parts I–II, JFM, arXiv:`1912.06677`, `1912.06684`.
- Miller (2021), *A locally anisotropic regularity criterion ... in terms of vorticity*, arXiv:`2002.02152`.
- Encinas-Bartos & Haller (2024), *Vorticity alignment with Lyapunov vectors and rate-of-strain eigenvectors*, Eur. J. Mech. B/Fluids 105, 259–274, DOI: `10.1016/j.euromechflu.2024.02.003`.
- Miller (2024; journal publication listed 2026), *On the interaction of strain and vorticity for solutions of the Navier–Stokes equation*, arXiv:`2407.02691`.
- Galeati (2025), *Almost-everywhere uniqueness of Lagrangian trajectories for 3D Navier–Stokes revisited*, J. Math. Pures Appl. 200, 103723, DOI: `10.1016/j.matpur.2025.103723`, arXiv:`2406.12788`.
- Hou, Wang & Yang (2025 preprint), *Nonuniqueness of Leray-Hopf solutions to the unforced incompressible 3D Navier–Stokes Equation*, arXiv:`2509.25116`.
- Emam, Kamal & Johnson (2026), *Turbulence Without the Viscous Tilting of Vorticity*, accepted in Physical Review Fluids 29 July 2026, DOI: `10.1103/lk2n-878k`, arXiv:`2606.17330`.
- Chen, Galdi, Poggi & Schikorra (2026 preprint), *On Serrin Interior Regularity Criterion for Navier–Stokes Equations*, arXiv:`2606.24733`.
- Mahithitarmmatorn (2026 preprint), *Exact mean-covariance dynamics of the Weber field in the stochastic Lagrangian representation of the 3D Navier–Stokes equations*, arXiv:`2608.16915`.

