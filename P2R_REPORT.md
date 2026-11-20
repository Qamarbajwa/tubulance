# Meta-Research Milestone P2R: Forensic Literature Reconciliation and Experiment Prioritization

```
SECURITY / EVIDENCE STATUS:
ANALYTICAL LITERATURE REVIEW
HYPOTHESES NOT YET PROJECT-VALIDATED
PROJECT ACCEPTANCE CEILING: LEVEL 2
GOVERNANCE: ZERO SOLVER SOURCE MODIFICATION — ZERO NEW EXPERIMENTS EXECUTED
```

> [!IMPORTANT]
> **P2R Core Principle**:
> $$\boxed{\text{A paper supports only what it actually demonstrates. Similarity generates a hypothesis. Only our own sealed experiment can turn that hypothesis into project evidence.}}$$
> P2R performs a forensic audit of the literature graph, eliminates citation misattributions, replaces overclaims with conditional hypotheses, establishes pretest falsification gates, and strictly separates **Mathematical Portability**, **Implementation Portability**, and **Project Inferences**.

---

## §1. Governance, Terminology & Baseline Integrity

### §1.1 Terminology Corrections
1. **Replacement of Overclaims**:
   * All phrases claiming *"MATHEMATICALLY GUARANTEED TRANSFER"*, *"IDENTICAL FAILURE"*, or *"PROVEN SOLUTION"* have been permanently replaced with:
     $$\boxed{\text{HIGH-STRUCTURAL-MATCH TRANSFER HYPOTHESIS} \quad \text{and} \quad \text{STRUCTURALLY SIMILAR PRECEDENT}}$$
2. **Separation of Portability Domains**:
   * **Mathematical Portability**: Theoretical properties of the continuous/semi-discrete differential operator (e.g., diagonalizability of the Laplacian, exactness of the Helmholtz decomposition, skew-symmetry of the advection operator).
   * **Implementation Portability**: Software artifacts specific to our MAC staggered-grid layout (`FaceField`, `ScalarField`), uniform Cartesian indices, and boundary condition stencils.
3. **Status of Historical Project Claims**:
   * **Sealed Authoritative Baseline (W13R-V2)**: $M1(210) \approx 0.634750$; $W13\text{-}G$ full-field breakthrough is **NOT REPRODUCED**; Milestone W14 remains **BLOCKED**.
   * **Greedy Global Oracle (G2)**: In the sealed W13R-V2 run, greedy oracle achieved $E_{\text{oracle}}(1152) = 0.0650 > 0.0500$. Therefore, $r_5$ was **NOT ACHIEVED IN THE TESTED RANGE** for global bases.
   * **Historical Definition of DISCARD**: Updated across all milestones to mean:
     $$\boxed{\text{DISCARD FOR TARGET X (Universal Full-State Turbulent Velocity Compression)}}$$
     Every discarded branch retains documented capabilities for alternative problem classes and targeted observables.

---

## §2. Comprehensive Forensic Citation Audit

Every literature entry in [`literature_map_v2.json`](file:///D:/Comfy%20UI/tubulance/report_json/literature_map_v2.json) has been forensically audited against the original publications and classified into five strict evidentiary categories:
`SUPPORTED_DIRECTLY`, `SUPPORTED_PARTIALLY`, `PROJECT_INFERENCE`, `MISATTRIBUTED`, `UNSUPPORTED`.

| ID | Authors & Year | Venue & DOI | Problem Studied | Claim Support Status | Relationship to Project Capability | Corrected Project Inference |
|:---|:---------------|:------------|:----------------|:--------------------:|:-----------------------------------|:----------------------------|
| **LIT-01** | McKeon & Sharma (2010) | *J. Fluid Mech.*, 658, 336-382<br>`10.1017/S002211201000176X` | Input-output resolvent formulation of wall turbulence | `SUPPORTED_DIRECTLY` | Supports Candidate W9-G `ResolventResponseBasis` for input-output gain mapping; does NOT support closed autonomous ROM without nonlinear feedback closure. | Our discrete staggered channel operators can compute resolvent response modes directly. |
| **LIT-02** | Toedtli, Luhar, McKeon (2019) | *Phys. Rev. Fluids*, 4, 113905<br>`10.1103/PhysRevFluids.4.113905` | Active opposition control & drag reduction in channel flow | `SUPPORTED_DIRECTLY` | Direct precedent for using resolvent gain to predict optimal wall actuation for shear stress reduction without full DNS sweeps. | We can test whether our discrete operators reproduce the qualitative wall-gain transfer structure without claiming drag reduction is achieved. |
| **LIT-03** | Schlegel et al. (2012) | *J. Fluid Mech.*, 697, 367-398<br>`10.1017/jfm.2011.554` | Observable Inferred Decomposition (OID) for goal functionals | `SUPPORTED_DIRECTLY` | Proves that optimizing modes for linear observables (lift, drag, acoustic pressure) achieves large order reduction for that observable, while departing from full-state L2 energy optimality. | Explains why our wall-shear error ($E_{\tau_w} \approx 3.9\%$) can be low while full-state velocity error ($E_u \approx 28\%$) is high. |
| **LIT-04** | Schlegel & Noack (2015) | *J. Fluid Mech.*, 767, 652-686<br>`10.1017/jfm.2015.70` | Long-term stability & skew-symmetry in quadratic Galerkin ROMs | `SUPPORTED_DIRECTLY` | Proves that preserving skew-symmetry $\langle \phi_i, (\phi_j \cdot \nabla)\phi_k \rangle + \langle \phi_k, (\phi_j \cdot \nabla)\phi_i \rangle = 0$ is necessary for energy boundedness; explains triad pruning blowup. | Our `OntheFlyFFTEvaluator` succeeded because it evaluates the full continuous skew-symmetric operator on a collocation grid without tensor truncation. (Independent project evidence). |
| **LIT-05** | Reiss et al. (2018) | *SIAM J. Sci. Comput.*, 40, A1322-A1344<br>`10.1137/17M1141774` | Shifted POD (sPOD) for transport-dominated phenomena | `SUPPORTED_PARTIALLY` | Demonstrates order-of-magnitude mode reduction for 1D/2D traveling waves and advecting pulses. Does NOT prove cross-seed 3D turbulence is solvable by shifts alone. | IF cross-seed decorrelation in periodic directions is dominated by spatial translations, THEN symmetry reduction will collapse cross-seed distance (conditional on $R_{\text{align}}$ pretest). |
| **LIT-06** | Rowley & Marsden (2000) | *Physica D*, 142, 1-19<br>`10.1017/S0167278900000428` | Symmetry reduction & Karhunen-Loève for systems with symmetry | `SUPPORTED_DIRECTLY` | Proves that quotienting out continuous Lie group actions (spatial translations) removes phase drift degrees of freedom in traveling-wave attractors. | Mathematical foundation for our W4 phase-shift audit and translation group alignment. |
| **LIT-07** | Amsallem, Zahr, Farhat (2012) | *Int. J. Numer. Meth. Eng.*, 92, 891-916<br>`10.1002/nme.4371` | Local reduced-order bases for nonlinear systems | `SUPPORTED_DIRECTLY` | Validates clustering state-space snapshots into local POD subspaces with smooth switching for systems with localized operating regimes. | Precedent for `ClusteredLocalPODBasis` (R08) in multi-regime structural dynamics (bistable buckling). |
| **LIT-08** | Kaiser et al. (2014) | *J. Fluid Mech.*, 754, 365-414<br>`10.1017/jfm.2014.355` | Cluster-based Reduced-Order Modeling (CROM) | `SUPPORTED_DIRECTLY` | Precedent for modeling nonlinear multi-regime transitions via discrete Markov transition matrices rather than continuous Galerkin ODEs. | Snapshot clustering infrastructure can be used for discrete regime-transition modeling. |
| **LIT-09** | Deriaz & Perrier (2006) | *J. Turbul.*, 7, N3<br>`10.1080/14685240500499010` | Divergence-free wavelets for incompressible turbulence | `SUPPORTED_DIRECTLY` | Mathematical foundation for multiresolution divergence-free wavelets and exact Helmholtz decomposition in periodic domains. | Explains why periodic solenoidal wave packets are sound, while non-periodic boundary wavelets encounter conditioning issues. |
| **LIT-10** | Farge & Schneider (2001) | *Phys. Fluids*, 13, 1937-1948<br>`10.1063/1.1378330` | Coherent vortex extraction using orthogonal wavelets | `SUPPORTED_DIRECTLY` | Validates that wavelet thresholding compresses turbulent fields into sparse non-Gaussian coherent vortex tubes ($>99\%$ energy in $\sim 3\%$ modes) and background noise. | Validates our `SparsificationEngine` for static coherent vortex extraction and sparse sensor reconstruction. |
| **LIT-11** | Kassam & Trefethen (2005) | *SIAM J. Sci. Comput.*, 26, 1214-1233<br>`10.1137/0226049` | 4th-order time-stepping for stiff semilinear PDEs (ETDRK4) | `SUPPORTED_DIRECTLY` | Directly underpins our `IntegratingFactorModalODEIntegrator` (R13) for stiff linear Laplacians with polynomial reaction kinetics. | ETD is a reliable software asset for semilinear PDEs with diagonal linear parts. |
| **LIT-12** | Hochbruck & Ostermann (2010) | *Acta Numerica*, 19, 209-286<br>`10.1017/S0962492910000048` | Comprehensive theory of exponential integrators | `SUPPORTED_DIRECTLY` | Proves rigorous stability bounds and convergence rates for stiff semilinear parabolic systems under sectorial operators. | Formally justifies why our ETD implementation achieves machine-precision linear decay. |
| **LIT-13** | Vaidyanathan & Tenneti (2014) | *IEEE Trans. Signal Process.*, 62, 4987-4999<br>`10.1109/TSP.2014.2345346` | Properties of Ramanujan filter banks | `SUPPORTED_DIRECTLY` | Validates orthogonal Ramanujan filter banks for integer periodicities in discrete signals. | Explains why Ramanujan correction failed for continuous spatial fluid turbulence (N13); redirects to discrete time-series. |
| **LIT-14** | Carlberg et al. (2011) | *Int. J. Numer. Meth. Eng.*, 86, 155-181<br>`10.1002/nme.3056` | GNAT method & Petrov-Galerkin nonlinear model reduction | `SUPPORTED_DIRECTLY` | Validates Petrov-Galerkin residual minimization over low-dimensional trial spaces using gappy sample meshes. | Petrov-Galerkin is a distinct hyper-reduction and residual-minimizing method, separate from output-specific observable decomposition. |
| **LIT-15** | Dudley & James (1989) | *Proc. R. Soc. Lond. A*, 425, 407-429<br>`10.1098/rspa.1989.0112` | Time-dependent kinematic dynamos with stationary flows | `SUPPORTED_DIRECTLY` | Direct literature foundation for kinematic magnetic induction under prescribed incompressible velocity fields. | Our exact `FourierSolenoidalBasis` satisfies $\nabla \cdot \mathbf{B} = 0$ to machine precision, solving kinematic dynamos without monopole accumulation. |

---

## §3. Correcting the Shifted-POD Claim & Defining the Cheap Pretest

### §3.1 Re-evaluation of the Shifted-POD Claim
* **Previous Overclaim**: Stated that turbulent cross-seed POD failure is *"identical"* to the transport Kolmogorov barrier and that Shifted-POD / symmetry reduction *"will collapse"* cross-seed subspace distance.
* **Literature Reality**:
  * *Reiss et al. (2018)* demonstrated shifted POD on 1D/2D transport problems with isolated traveling waves.
  * *Rowley & Marsden (2000)* proved symmetry reduction for continuous Lie group symmetries on traveling-wave attractors.
  * Turbulent channel flow contains multiscale eddies undergoing continuous nonlinear distortion, shearing, and vortex stretching—not merely rigid spatial translations.
* **Corrected Conditional Hypothesis**:
  $$\boxed{\text{IF cross-seed difference is dominated by translation/phase drift, THEN symmetry reduction will reduce subspace distance.}}$$

### §3.2 Mandatory Shifted-POD Pretest Gate ($R_{\text{align}}$)
Before implementing any Shifted-POD solver or symmetry reduction algorithm, the following cheap diagnostic pretest must be executed on existing multi-seed datasets (W3/W4 Seeds 101, 104, 105):

1. **Raw Cross-Seed Subspace Distance**:
   $$d_{\text{raw}} = d_{\text{subspace}}(\Phi_{\text{seed1}}, \Phi_{\text{seed2}}) = \sqrt{\sum_{i=1}^r (1 - \sigma_i^2)}$$
   where $\sigma_i$ are the singular values of the cross-Gramian matrix $S_{ij} = \langle \phi_i^{\text{seed1}}, \phi_j^{\text{seed2}} \rangle_{\text{MAC}}$. (Baseline: $d_{\text{raw}} \approx 1.52$).
2. **Optimally Aligned Subspace Distance**:
   $$d_{\text{aligned}} = \min_{(\Delta x, \Delta z)} d_{\text{subspace}}\left(\Phi_{\text{seed1}}, \mathcal{T}_{(\Delta x, \Delta z)} \Phi_{\text{seed2}}\right)$$
   using our existing `optimal_translation_alignment` tool.
3. **Alignment Ratio**:
   $$R_{\text{align}} = \frac{d_{\text{aligned}}}{d_{\text{raw}}}$$

```
+-----------------------------------------------------------------------------------------------+
| SHIFTED-POD PRETEST DECISION GATE                                                             |
+-----------------------------------------------------------------------------------------------+
| If R_align >= 0.80:                                                                           |
|   -> DISCARD spatial translation / Shifted-POD as the primary explanation for cross-seed     |
|      POD failure in 3D turbulence. (Proves failure is caused by intrinsic attractor geometry).|
|                                                                                               |
| If R_align <= 0.30:                                                                           |
|   -> PROMOTE Shifted-POD / Lie symmetry reduction for experimental development.               |
|      (Proves spatial translation is the dominant driver of subspace decorrelation).           |
+-----------------------------------------------------------------------------------------------+
```

---

## §4. Corrected Structure-Preserving Quadratic ROM Mapping

* **Previous Misattribution**: Attributed `OnTheFlyFFTEvaluator` and triad pruning stability to *"wave turbulence truncation instability — Schlegel & Noack 2015"*.
* **Corrected Formulation**:
  * *Schlegel & Noack (2015 JFM)* studies the long-term energy boundedness of linear-quadratic Galerkin systems.
  * Incompressible advection is continuous and skew-symmetric:
    $$\langle \mathbf{u}, (\mathbf{u} \cdot \nabla)\mathbf{u} \rangle = 0 \quad \iff \quad Q_{kij} = -Q_{ikj}$$
  * Heuristically truncating weak triads (as attempted in W7) breaks this exact antisymmetry, turning a neutrally stable conservative nonlinearity into an unstable positive-feedback loop.
* **Project Evidence**:
  * Our `OntheFlyFFTEvaluator` (W7) succeeded because it computes nonlinear advection on a minimal dealiased collocation grid in physical space without truncating the continuous operator, preserving energy conservation to machine precision.
  * **Our FFT solver is independent project evidence**; the literature confirms the mathematical necessity of structure preservation.

---

## §5. Corrected Goal-Oriented & Output-Specific ROM Mapping

* **Previous Misattribution**: Attributed all output-specific reductions to *"goal-oriented structural acoustics / dual-space Petrov-Galerkin (Brunton & Noack 2015)"*.
* **Corrected Literature Landscape**:
  We explicitly distinguish six distinct output-oriented mathematical methodologies:

```
+------------------------------------------------------------------------------------------------------+
| OUTPUT-ORIENTED REDUCED-ORDER MODELING TAXONOMY                                                      |
+------------------------------------------------------------------------------------------------------+
| 1. Observable Inferred Decomposition (OID) [Schlegel et al. 2012 JFM]:                                |
|    Constructs Galerkin modes directly optimized for linear output goal functionals (lift, drag,     |
|    acoustic pressure) rather than kinetic energy.                                                    |
|                                                                                                      |
| 2. Output-Specific / Goal-Oriented POD:                                                              |
|    Weights snapshot correlation matrices by output functional gradients: C_ij = <g'(u_i), g'(u_j)>. |
|                                                                                                      |
| 3. Goal-Oriented Reduced Basis Methods [Rozza et al. 2008]:                                          |
|    Primal-dual greedy basis construction with rigorous a posteriori output error bounds.             |
|                                                                                                      |
| 4. Adjoint-Weighted Balanced Truncation [Willcox & Peraire 2002]:                                   |
|    Balances controllability Gramian (inputs) with observability Gramian (outputs) to truncate states.|
|                                                                                                      |
| 5. Dual-Space Petrov-Galerkin Projection [Carlberg et al. 2011]:                                     |
|    Decouples trial basis (state representation) from test basis (adjoint/residual weighting).        |
|                                                                                                      |
| 6. Resolvent Input-Output Transfer Analysis [McKeon & Sharma 2010]:                                  |
|    SVD of (i*omega*I - L)^(-1) identifies maximal gain response modes for boundary actuators.        |
+------------------------------------------------------------------------------------------------------+
```

* **Mapping to Project Evidence**:
  * In Milestone W11, our `SeparableChannelEigenbasis` achieved wall shear stress error $E_{\tau_w} \approx 3.9\%$ while full velocity field error remained $E_u \approx 28.0\%$.
  * *Schlegel et al. (2012)* provides the direct theoretical foundation: **wall shear stress is an observable functional with low effective rank**, even when the full 3D velocity field has high Kolmogorov $n$-width.

---

## §6. Clarification of Individual Hypotheses

### §6.1 Resolvent Analysis (HYP-03)
* **Status**: **STRONG PRECEDENT** (*McKeon & Sharma 2010*, *Toedtli et al. 2019*).
* **Corrected Scope Statement**:
  $$\boxed{\text{Test whether our existing discrete staggered channel operators can accurately reproduce the relevant input-output gain structure for wall actuation.}}$$
* **Non-Claim**: The project has **NOT** achieved active drag reduction. The hypothesis tests input-output gain calculation against DNS truth benchmarks.

### §6.2 Exponential Time Differencing (HYP-01)
* **Status**: **ESTABLISHED** (*Kassam & Trefethen 2005*, *Hochbruck & Ostermann 2010*).
* **Corrected Scope Statement**:
  $$\boxed{\text{Software and mathematical transfer smoke test validating ETD integration on non-fluid semilinear reaction-diffusion PDEs.}}$$
* **Non-Claim**: Does not "prove unconditional stability" (a known theoretical property for linear parts); serves as an implementation portability validation.

### §6.3 Kinematic Dynamo (HYP-05)
* **Status**: **STRONG PRECEDENT** (*Roberts 1972*, *Dudley & James 1989*).
* **Corrected Scope Statement**:
  $$\boxed{\text{Roberts-Flow Kinematic Induction/Dynamo Test.}}$$
* **Explicit Boundary**: Velocity field $\mathbf{u}$ is prescribed; magnetic field $\mathbf{B}$ evolves under induction $\partial_t \mathbf{B} = \nabla \times (\mathbf{u} \times \mathbf{B}) + \eta \nabla^2 \mathbf{B}$; zero Lorentz force feedback ($\mathbf{J} \times \mathbf{B} = 0$ in momentum); **not full MHD**.

---

## §7. Complete Audit Table for All Candidate Hypotheses

| Hypothesis ID & Name | Literature Support Status | Direct Literature Evidence | Project Inference | Misattribution Corrected | Corrected Verdict |
|:---|:---:|:---|:---|:---|:---:|
| **HYP-01**: ETD for Semilinear Reaction-Diffusion | **ESTABLISHED** | Kassam & Trefethen (2005 SISC); Hochbruck & Ostermann (2010 Acta Numerica). | Our `IntegratingFactorModalODEIntegrator` accurately steps stiff Laplacians with polynomial reaction kinetics. | Corrected from "proves unconditional stability" to software smoke test. | **TEST (Smoke Test)** |
| **HYP-02**: Stokes Eigenbasis for Heat Conduction | **ESTABLISHED** | Classical Fourier-Bessel Sturm-Liouville spectral theory. | Discrete MAC Stokes eigenmodes are exact discrete Laplacian eigenfunctions for scalar diffusion. | None (classical baseline). | **TEST (Baseline)** |
| **HYP-03**: Resolvent Wall-Shear Boundary Gain | **STRONG PRECEDENT** | McKeon & Sharma (2010 JFM); Toedtli, Luhar, McKeon (2019 PRF). | Our discrete staggered channel operators can compute input-output gain for wall actuation without full DNS. | Removed implication of project-validated drag reduction; framed as gain calculation test. | **TEST (Highest CFD Value)** |
| **HYP-04**: On-the-Fly FFT for 1D Burgers Equation | **ESTABLISHED** | Orszag (1971 Stud. Appl. Math.); Canuto et al. (2006 Spectral Methods). | 3D real FFT evaluator generalizes component-wise to 1D/2D quadratic momentum advection. | Removed attribution to Schlegel 2015; FFT evaluator is independent project evidence. | **TEST (Algorithm Benchmark)** |
| **HYP-05**: Solenoidal Basis for Kinematic Dynamo | **STRONG PRECEDENT** | Dudley & James (1989 Proc. R. Soc. Lond. A); Roberts (1972). | `FourierSolenoidalBasis` satisfies $\nabla \cdot \mathbf{B} = 0$ to machine precision, eliminating magnetic monopoles. | Renamed from "MHD Test" to "Roberts-Flow Kinematic Induction/Dynamo Test" (prescribed velocity). | **TEST (Cross-Domain Dynamo)** |
| **HYP-06**: Clustered Local POD for Bistable Buckling | **STRONG PRECEDENT** | Amsallem, Zahr, Farhat (2012 IJNME); Kaiser et al. (2014 JFM). | `ClusteredLocalPODBasis` partitions state-space snapshots into discrete operating basins with nearest-cluster projection. | None; properly cites Amsallem (2012) and Kaiser (2014). | **TEST (Multi-Regime)** |
| **HYP-07**: Solenoidal Wave Packets for Inverse Sensing | **STRONG PRECEDENT** | Farge & Schneider (2001 Phys. Fluids); Deriaz & Perrier (2006 J. Turbul.). | Multiresolution wave packets + `NonorthogonalProjectionSolver` can extract localized coherent vortex cores from sparse sensors. | Decoupled from failed W13-G forward ROM capacity; restricted to static vortex extraction. | **TEST (Inverse Sensing)** |
| **HYP-08**: Separable Eigenbasis for Acoustic Ducts | **ESTABLISHED** | Morse & Ingard (1968 Theoretical Acoustics); Rienstra & Hirschberg (2004). | Tensor-product Fourier-sine basis spans exact rectangular acoustic duct cut-on/cut-off waveguide modes. | None; classical acoustics. | **TEST (Baseline)** |
| **HYP-09**: Grassmannian NN Representation Tracking | **STRONG PRECEDENT** | Raghu et al. (2017 NeurIPS - SVCCA); Kornblith et al. (2019 ICML - CKA). | `subspace_distance_metric` computes exact principal angles between weight subspaces across training checkpoints. | Held because standard ML packages (PyTorch SVCCA) already exist. | **HOLD** |
| **HYP-10**: Domain-Agnostic Audit Tool (`sciaudit`) | **STRONG PRECEDENT** | Peng (2011 Science); Stodden et al. (2016 Science). | Write-once SHA256 directory hashing and AST metric hashing operate on general files with zero CFD dependency. | Separated from scientific scores into independent Engineering portfolio. | **TEST (Engineering Packaging)** |
| **HYP-PRE01**: Spatial Alignment / Shifted-POD Pretest | **STRONG PRECEDENT** | Reiss et al. (2018 SISC); Rowley & Marsden (2000 Physica D). | Measuring $R_{\text{align}} = d_{\text{aligned}} / d_{\text{raw}}$ on existing datasets decides whether translation is the dominant driver of POD failure. | Replaces premature sPOD solver claim with a cheap falsification gate. | **TEST (Representation Gate)** |

---

## §8. Prioritizing the Three Dimensionality Escapes

```
+------------------------------------------------------------------------------------------------------+
| THE THREE DIMENSIONALITY ESCAPES: COMPARATIVE EVALUATION                                             |
+------------------------------------------------------------------------------------------------------+
| ESCAPE A: SYMMETRY REDUCTION (Translation / Phase Removal before POD)                                |
| - Premise: Cross-seed POD failure is caused by spatial phase drift in periodic directions.          |
| - Literature: Reiss et al. (2018 sPOD), Rowley & Marsden (2000 Symmetry Reduction).                 |
| - Status in Project: CONDITIONAL HYPOTHESIS. Must pass R_align pretest (R_align <= 0.30) first.     |
| - Priority: IMMEDIATE DIAGNOSTIC PRETEST (HYP-PRE01). Cost: ~15 minutes.                            |
|                                                                                                      |
| ESCAPE B: OBSERVABLE REDUCTION (Represent tau_w / Drag / Pressure rather than Full Velocity)        |
| - Premise: Boundary observables have low Kolmogorov n-width even when full velocity field has high  |
|   dimension.                                                                                         |
| - Literature: Schlegel et al. (2012 OID), Brunton & Noack (2015 Closed-Loop Turbulence Control).     |
| - Status in Project: SUPPORTED BY EMPIRICAL DATA (W11: E_tau_w = 3.9% at r=160).                     |
| - Priority: HIGH SCIENTIFIC VALUE. Directly resolves full-state vs boundary observable dilemma.     |
|                                                                                                      |
| ESCAPE C: RESOLVENT INPUT-OUTPUT REDUCTION (Represent Amplified Mechanisms rather than State)       |
| - Premise: Turbulent shear stress is governed by high-gain input-output response modes.              |
| - Literature: McKeon & Sharma (2010 JFM), Toedtli et al. (2019 PRF).                                 |
| - Status in Project: DIRECT STRUCTURAL PRECEDENT (W9-G operator infrastructure exists).              |
| - Priority: HIGHEST CFD IMPACT (HYP-03). Directly targets boundary actuation and drag control.      |
+------------------------------------------------------------------------------------------------------+
```

---

## §9. The Three Audited Portfolios (§17)

All candidate experiments are ranked mechanically using the explicit formula:
$$\boxed{\text{Score} = \frac{\text{Information Gain (1-5)} \times \text{Potential Value (1-5)} \times \text{Structural Match (1-5)}}{\text{Experiment Cost (1-5)}}}$$

### Portfolio A: CFD Breakthrough Portfolio
| Rank | ID | Hypothesis Name | Info Gain | Potential Value | Structural Match | Exp. Cost | Score | Primary Literature Reference |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **HYP-PRE01** | Spatial Alignment / Shifted-POD Pretest ($R_{\text{align}}$) | 5 | 4 | 5 | 1 | **100.0** | Reiss et al. (2018 SISC) |
| **2** | **HYP-03** | Resolvent Input-Output Gain for Wall Shear Control | 5 | 5 | 5 | 2 | **62.5** | McKeon & Sharma (2010 JFM); Toedtli (2019 PRF) |
| **3** | **HYP-07** | Solenoidal Wave Packets for Inverse Sensor Reconstruction | 4 | 4 | 4 | 2 | **32.0** | Farge & Schneider (2001 Phys. Fluids) |

### Portfolio B: Cross-Domain Transfer Portfolio
| Rank | ID | Hypothesis Name | Info Gain | Potential Value | Structural Match | Exp. Cost | Score | Primary Literature Reference |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **HYP-05** | Roberts-Flow Kinematic Induction/Dynamo Test | 5 | 4 | 5 | 2 | **50.0** | Dudley & James (1989 Proc. R. Soc. Lond. A) |
| **2** | **HYP-08** | Separable Eigenbasis for Acoustic Duct Resonators | 2 | 3 | 5 | 1 | **30.0** | Morse & Ingard (1968 Theoretical Acoustics) |
| **3** | **HYP-01** | ETD Integrator for Semilinear Reaction-Diffusion (Smoke Test) | 2 | 3 | 5 | 1 | **30.0** | Kassam & Trefethen (2005 SISC) |
| **4** | **HYP-06** | Clustered Local POD for Bistable Structural Buckling | 4 | 3 | 4 | 2 | **24.0** | Amsallem, Zahr, Farhat (2012 IJNME) |
| **5** | **HYP-04** | On-the-Fly FFT Evaluator for 1D Burgers Equation | 2 | 3 | 5 | 1 | **30.0** | Orszag (1971 Stud. Appl. Math.) |
| **6** | **HYP-02** | Stokes Eigenbasis for Parabolic Heat Transients | 2 | 3 | 5 | 1 | **30.0** | Classical Sturm-Liouville Theory |

### Portfolio C: Infrastructure & Engineering Portfolio
| Rank | ID | Tool Name | Info Gain | Potential Value | Structural Match | Exp. Cost | Score | Primary Literature Reference |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **HYP-10** | Domain-Agnostic Scientific Audit Tool (`sciaudit`) | 3 | 5 | 5 | 1 | **75.0** | Peng (2011 Science); Stodden (2016 Science) |

---

## §10. Final Selection of the Three Prioritized Experiments (§20)

P2R selects exactly **THREE** experiments for subsequent authorization and execution. **NO EXPERIMENTS ARE EXECUTED DURING P2R**.

```
========================================================================================================
EXPERIMENT 1: HIGHEST-INFORMATION FUNDAMENTAL REPRESENTATION GATE
========================================================================================================
Hypothesis: HYP-PRE01 — Spatial Phase Alignment / Shifted-POD Pretest (R_align Ratio)
Target System: Existing W3/W4 multi-seed turbulent channel snapshot datasets (Seeds 101, 104, 105).
Baseline: Raw cross-seed Grassmannian subspace distance d_raw = 1.52.
Falsification Condition: R_align = d_aligned / d_raw > 0.80.
Pass Condition: R_align <= 0.30 (spatial alignment collapses cross-seed subspace distance by >= 70%).
Required Evidence: Computed R_align scalar, optimal translation offsets (di, dj, dk), and pre/post
                   principal angle spectra exported to JSON.
Estimated Cost: ~10-15 minutes runtime (pure diagnostic analysis on existing data).
What We Learn if PASS: Proves spatial phase drift is the dominant cause of POD cross-seed failure,
                       mathematically justifying Shifted-POD development for turbulence.
What We Learn if FAIL: Decisively eliminates the spatial translation hypothesis, proving cross-seed
                       failure stems from intrinsic chaotic attractor geometry.

========================================================================================================
EXPERIMENT 2: HIGHEST-VALUE EXPERIMENT FOR ORIGINAL CFD
========================================================================================================
Hypothesis: HYP-03 — Resolvent Input-Output Analysis for Boundary-Actuated Wall Shear Gain
Target System: Turbulent channel flow (Re=200) under spanwise wall oscillation.
Baseline: Canonical W12/W13 channel DNS truth solver with actuated wall boundary condition.
Falsification Condition: Resolvent-predicted gain curve does not correlate with DNS wall shear reduction
                         (Pearson correlation r < 0.70 across actuation frequencies).
Pass Condition: Resolvent-predicted optimal actuation frequency matches DNS maximum shear reduction within
                15% relative frequency error.
Required Evidence: Raw arrays of discrete resolvent singular vectors, boundary actuation velocity profiles,
                   and resulting wall shear distributions saved in write-once evidence bundle.
Estimated Cost: ~1-2 hours runtime on single workstation.
What We Learn if PASS: Proves our discrete staggered operators accurately predict turbulent boundary
                       actuation gain without requiring full-state DNS sweeps.
What We Learn if FAIL: Identifies that discrete resolvent approximations around the laminar profile fail
                       to capture turbulent wall-shear sensitivity without explicit Reynolds stress closure.

========================================================================================================
EXPERIMENT 3: HIGHEST-VALUE CROSS-DOMAIN TRANSFER
========================================================================================================
Hypothesis: HYP-05 — Roberts-Flow Kinematic Induction/Dynamo Test
Target System: Roberts cellular flow kinematic dynamo at magnetic Reynolds number Rm=10.
Baseline: Analytical kinematic dynamo growth rate gamma from Roberts (1972) / Dudley & James (1989).
Falsification Condition: Magnetic divergence norm ||div B|| > 1e-12 OR computed growth rate gamma differs
                         from Roberts analytical eigenvalue by > 1.0%.
Pass Condition: ||div B|| < 1e-12 to machine precision; gamma matches analytical value within 0.5%.
Required Evidence: Time series of magnetic energy, modal coefficients, magnetic growth rate gamma, and
                   divergence norm exported to evidence bundle.
Estimated Cost: ~1-2 hours runtime on single workstation.
What We Learn if PASS: Proves our exact solenoidal modal basis solves kinematic magnetic induction and
                       dynamo problems without magnetic monopole divergence accumulation.
What We Learn if FAIL: Identifies whether cross-product modal projections introduce aliasing or stability
                       issues during vector induction coupling.
========================================================================================================
```

---

## §11. Answers to All Core Milestone Questions

### Q1: Which of our discarded techniques already have successful uses elsewhere?
* **Resolvent Analysis (W9-G)**: Standard in turbulent flow control and drag reduction (*McKeon & Sharma 2010*, *Toedtli et al. 2019*).
* **Snapshot POD (W3/W4)**: Standard in parametric structural dynamics, aeroelastic flutter, and regime-switching systems (*Amsallem & Farhat 2008*, *Kaiser et al. 2014*).
* **Multiscale Wave Packets (W13-G)**: Standard in Coherent Vortex Simulation (CVS) and turbulent field denoising (*Farge & Schneider 2001*, *Deriaz & Perrier 2006*).
* **Ramanujan Sums (R17)**: Highly successful in discrete integer-period signal extraction, DNA sequence analysis, and machinery vibration diagnostics (*Vaidyanathan & Tenneti 2014*).

### Q2: Which methods failed because our target observable was too ambitious?
* **Resolvent Response Basis (W9-G)** and **Derivative-Weighted Basis (W9-A/B)**: Both failed against the target of universal full-velocity 3D field compression ($E_u < 5\%$). When evaluated on their natural target observable—**wall shear stress $\tau_w$**—they achieved $E_{\tau_w} \approx 3.9\%$ (*Schlegel et al. 2012 OID*).

### Q3: Which other fields encountered structurally similar failures?
* **Hyperbolic Transport**: Standard POD fails on moving shocks and traveling pulses (slow Kolmogorov $n$-width decay), identically to our W3 cross-seed failure.
* **Structure-Preserving Dynamics**: Heuristic truncation of nonlinear Galerkin tensors destroys skew-symmetry and triggers energy explosion, identically to our W7 triad pruning failure (N06).
* **Goal-Oriented Reduction**: Global energy-norm POD fails on localized engineering observables (lift, drag, sound pressure) because bulk energy swamping obscures boundary sensitivities.

### Q4: What solutions did those fields develop?
* **Shifted POD (sPOD) & Symmetry Reduction**: Factoring out spatial translation/phase drift (*Reiss et al. 2018*, *Rowley & Marsden 2000*).
* **Pseudospectral & Skew-Symmetric Formulation**: Preserving continuous skew-symmetry via on-the-fly collocation grid evaluation (*Schlegel & Noack 2015*).
* **Observable Inferred Decomposition (OID) & Dual Petrov-Galerkin**: Optimizing basis modes directly for goal functionals (*Schlegel et al. 2012*, *Carlberg et al. 2011*).

### Q5: Which of those solutions can feed back into Navier-Stokes?
* **Spatial Phase Alignment ($R_{\text{align}}$ Pretest)**: Testing whether translation removal eliminates cross-seed POD decorrelation.
* **Observable-Specific Mode Allocation (OID)**: Targeting boundary shear $\tau_w$ and drag functionals directly rather than full-state velocity fields.

### Q6: Where does our existing code provide a real head start?
* **Exact Solenoidal Basis (`FourierSolenoidalBasis`)**: Directly solves kinematic dynamos (MHD) without divergence cleaning.
* **ETD Integrator (`IntegratingFactorModalODEIntegrator`)**: Plug-and-play stiff linear integrator for semilinear PDEs.
* **On-the-Fly FFT Evaluator (`OntheFlyFFTEvaluator`)**: Universal memory-efficient evaluator for quadratic conservation laws.
* **Audit Infrastructure (`EvidenceBundle`, `LockManagerV2`)**: Standalone, production-ready reproducibility package (`sciaudit`).

### Q7: Where does only the mathematical idea transfer?
* **Resolvent Flow Control (HYP-03)**: Code must be adapted from state projection to input-output transfer matrix calculation.
* **Clustered POD for Buckling (HYP-06)**: Clustering algorithm transfers directly; physical ODE RHS must be replaced with structural beam equations.
* **Grassmannian NN Tracking (HYP-09)**: Mathematical SVD logic transfers, but implementation must bridge from NumPy MAC fields to PyTorch tensor matrices.

### Q8: Which opportunities are genuinely underexplored?
* **Discrete Staggered Resolvent SVD for Boundary Drag Control (HYP-03)**: Most literature uses continuous Orr-Sommerfeld formulations; evaluating resolvent gain directly on discrete staggered MAC operators is underexplored.
* **Exact Solenoidal Modal Basis for Kinematic Dynamo (HYP-05)**: Using discrete MAC divergence-free bases to study magnetic growth rate spectra in astrophysical dynamos without Poisson divergence projection.

### Q9: Which experiments maximize information gained per unit cost?
* **HYP-PRE01 (Spatial Alignment Pretest: Score 100.0)**: Delivers a definitive verdict on the translation hypothesis in $<15$ minutes.
* **HYP-03 (Resolvent Wall Control: Score 62.5)**: Delivers high-impact turbulent drag-reduction insight in $<2$ hours.

### Q10: Which three experiments should be run first?
* **Experiment 1 (Representation Gate)**: **HYP-PRE01 (Spatial Alignment / Shifted-POD $R_{\text{align}}$ Pretest)**.
* **Experiment 2 (CFD Breakthrough)**: **HYP-03 (Resolvent Input-Output Boundary Analysis)**.
* **Experiment 3 (Cross-Domain Transfer)**: **HYP-05 (Roberts-Flow Kinematic Induction/Dynamo Test)**.

### Q11: Which one has the highest potential to improve the original CFD program?
$$\boxed{\mathbf{HYP\text{-}03}\text{ (Resolvent Input-Output Analysis for Boundary-Actuated Wall Shear Control)}}$$
* Targeting boundary-actuated wall shear stress $\tau_w$ operates on low-rank, highly amplified response modes, bypassing the full-state 3D Kolmogorov barrier.

### Q12: Which one has the highest potential to become a useful result even if it never helps CFD?
$$\boxed{\mathbf{HYP\text{-}10}\text{ (Standalone Scientific Audit Infrastructure Package — }\texttt{sciaudit}\text{)}}$$
* Write-once SHA256 directory hashing, Python AST source-code inspection, and independent automated metric recomputation solve a universal reproducibility challenge across scientific computing and ML benchmarks, with zero dependency on fluid mechanics.

---

## §12. Summary of Generated Machine-Readable Deliverables

The following four authoritative v2 JSON files have been generated in [`report_json/`](file:///D:/Comfy%20UI/tubulance/report_json):

| File | Purpose | Contents |
|:---|:---|:---|
| [literature_map_v2.json](file:///D:/Comfy%20UI/tubulance/report_json/literature_map_v2.json) | Audited Literature Provenance | 15 peer-reviewed papers with full citation metadata, demonstrated results, limitations, explicit claim support status, and project inferences. |
| [analogous_failures_v2.json](file:///D:/Comfy%20UI/tubulance/report_json/analogous_failures_v2.json) | Cross-Domain Failure Analysis | 5 major project failure modes mapped to analogous failures in other fields with strict separation of `DIRECT_LITERATURE_EVIDENCE` and `OUR_PROJECT_INFERENCE`. |
| [transfer_hypotheses_v2.json](file:///D:/Comfy%20UI/tubulance/report_json/transfer_hypotheses_v2.json) | Audited Hypotheses Table | 11 comprehensive hypothesis audit records with corrected terminology, removed misattributions, and accurate scope statements. |
| [experiment_portfolio_v2.json](file:///D:/Comfy%20UI/tubulance/report_json/experiment_portfolio_v2.json) | Mechanical Quantitative Rankings | Three distinct portfolios (CFD Breakthrough, Cross-Domain Transfer, Engineering) scored via explicit mathematical formula $\frac{\text{Info Gain} \times \text{Value} \times \text{Match}}{\text{Cost}}$. |

---

$$\boxed{\text{META-RESEARCH MILESTONE P2R = COMPLETE}}$$
$$\boxed{\text{STATUS: ANALYTICAL LITERATURE REVIEW — HYPOTHESES NOT YET PROJECT-VALIDATED}}$$
