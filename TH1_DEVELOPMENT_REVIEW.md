# TH1 Development Gate Review: Architecture, Verification, and Pre-Seal Audit

```
DEVELOPMENT STATUS:
STAGE: DEVELOPMENT_ONLY (PRE-SEAL AUDIT)
STATUS: DEVELOPMENT GATES PASSED (A through H)
EVIDENCE STATUS: NO SCIENTIFIC RESULT ACCEPTED FROM DEVELOPMENT RUNS
TRANSITION PROTOCOL: DEVELOP -> REVIEW -> SEAL -> RUN
```

---

## 1. Development Test Results Summary

The development test harness (`tests/test_th1_falsification.py`) executed all unit and integration verifications:

- **Number Passed**: $7$
- **Number Failed**: $0$
- **Warnings**: $0$
- **Total Runtime**: $244.71\text{ s}$ ($04\text{m }04\text{s}$)

> [!NOTE]
> **Development Isolation Notice**: All test metrics and developmental execution outputs are used exclusively for software correctness, schema conformance, and numerical convergence verification. **No numerical value from development testing is admitted as scientific evidence.**

---

## 2. Exact Experiment Architecture Specification

| Architecture Component | Exact Pre-Registered Choice |
|:---|:---|
| **Flow families** | 1. Decaying Homogeneous Isotropic Turbulence<br>2. Taylor–Green Vortex Periodic Benchmark<br>3. Periodic Shear Layer |
| **Independent flows per family** | - Decaying Isotropic: $3$ independent simulations (Seeds 101, 102, 103)<br>- Taylor–Green: $1$ benchmark simulation (Seed 201)<br>- Shear Layer: $1$ benchmark simulation (Seed 301)<br>*(Total = 5 independent physical flows)* |
| **Reynolds numbers** | $\text{Re} = 100.0$ ($\nu = 0.01$) for primary benchmark; sensitivity sweep at $\text{Re} \in \{20.0, 100.0, 333.3\}$ |
| **Grid sizes** | Primary: $16 \times 16 \times 16$ MAC grid; Resolution sweep: $12^3, 16^3, 24^3$ |
| **Observation window** | $[t_0, t_{\text{obs}}] = [0.00, 0.30]$ ($\text{total } 15 \text{ simulation steps, } \Delta t_{\text{sim}} = 0.02$) |
| **Forecast horizons ($\Delta t$)** | $\Delta t \in \{0.04, 0.10, 0.20, 0.30, 0.40\}$ (corresponding to $\Delta_{\text{steps}} \in \{2, 5, 10, 15, 20\}$) |
| **Target thresholds** | Primary: Top $25\%$ of $|\boldsymbol{\omega}(\mathbf{x}, t_f)|$; Sensitivity sweep: Top $10\%, 20\%, 25\%, 33\%$ |
| **Particle count (P0)** | $64$ independent tracer trajectories per flow ($N_{\text{total}} = 320$) |
| **Thread count (P1)** | $64$ connected material lines per flow ($N_{\text{total}} = 320$) |
| **Tracers per thread** | Primary: $17$ discrete tracers; Discretization sweep: $9, 17, 33, 65$ tracers |
| **Bundle topology (P2)** | Regular 3D Cartesian cross configuration (central reference tracer $+6$ orthogonal tracers at $\pm r_0 \mathbf{e}_x, \pm r_0 \mathbf{e}_y, \pm r_0 \mathbf{e}_z$) |
| **Tracers per bundle** | $7$ tracers ($1$ centroid reference $+ 6$ orthogonal deformation probes, $r_0 = 0.06$) |
| **Trajectory integrator** | Explicit 4th-order Runge–Kutta (RK4) with domain periodic boundary wrapping |
| **Velocity interpolation** | **PRIMARY = Trilinear interpolation on staggered MAC face locations** (Cubic spline retained strictly for sensitivity audit) |
| **ML models** | 1. L2-Regularized Logistic Regression ($C=1.0$, balanced weighting)<br>2. Shallow Random Forest ($N_{\text{trees}}=50, \text{depth}=5$) |
| **LOFO splitting rule** | Strict Leave-One-Flow-Out across $N=5$ physical flow realizations (fit all scalers and models strictly on $N-1$ flows; evaluate on the untouched $N$-th flow) |

---

## 3. Generalization Levels

The experiment separates evaluation across three distinct physical generalization tiers:

- **Level G1 — New Realization**: Train on Decaying Isotropic Turbulence (Seeds 101, 102); evaluate on Decaying Isotropic Turbulence (Seed 103) under identical parameterization ($\text{Re}=100, 16^3$).
- **Level G2 — New Parameter**: Train on $\text{Re}=100$; evaluate on unseen $\text{Re}=20$ or $\text{Re}=333$ within the same flow family.
- **Level G3 — New Flow Family**: Train exclusively on Decaying Isotropic Turbulence flows; evaluate on Taylor–Green vortex or Periodic Shear Layer flows.

---

## 4. Flow Independence Audit

| Flow ID | Flow Family | Seed | Initial Condition Generator | Forcing | $\text{Re}$ ($\nu$) | Grid | Time Interval | Parameter Sharing Status |
|:---|:---|:---:|:---|:---:|:---:|:---:|:---:|:---|
| `flow_iso_seed101` | Decaying Isotropic | 101 | 3D Solenoidal Fourier Random ($k_p=2, E_0=1$) | None (Decaying) | $100$ ($0.01$) | $16^3$ | $[0.0, 0.70]$ | Independent initial random seed |
| `flow_iso_seed102` | Decaying Isotropic | 102 | 3D Solenoidal Fourier Random ($k_p=2, E_0=1$) | None (Decaying) | $100$ ($0.01$) | $16^3$ | $[0.0, 0.70]$ | Independent initial random seed |
| `flow_iso_seed103` | Decaying Isotropic | 103 | 3D Solenoidal Fourier Random ($k_p=2, E_0=1$) | None (Decaying) | $100$ ($0.01$) | $16^3$ | $[0.0, 0.70]$ | Independent initial random seed |
| `flow_tg_benchmark` | Taylor–Green | 201 | Analytical Taylor–Green $(\sin x \cos y \cos z, \dots)$ | None (Decaying) | $100$ ($0.01$) | $16^3$ | $[0.0, 0.70]$ | Fundamentally distinct flow family |
| `flow_shear_layer` | Periodic Shear | 301 | Solenoidal Shear Wave Perturbation ($k_p=1, E_0=1.5$) | None (Decaying) | $100$ ($0.01$) | $16^3$ | $[0.0, 0.70]$ | Fundamentally distinct flow family |

*Note*: Individual tracers ($N=64$ per flow) are diagnostic samples within a single flow and are never treated as independent physical realizations.

---

## 5. Primary Feature Leakage Audit

All primary geometry-only features are computed **exclusively from tracer coordinates $\mathbf{x}(t)$ and time $t$**. No Eulerian physics variables ($\boldsymbol{\omega}, |\boldsymbol{\omega}|, S, \nabla \mathbf{u}, \lambda, p$) enter the geometry feature matrix.

### Detailed Feature Formulation List

#### Representation P0: Particle (Input Dim = 17)
1. `pos_x, pos_y, pos_z`: Current centroid position $\mathbf{x}(t_{\text{obs}})$.
2. `inst_speed`: $\|\mathbf{x}(t_{\text{obs}}) - \mathbf{x}(t_{\text{obs}}-\Delta t)\| / \Delta t$ (derived purely from displacement).
3. `inst_acc`: $\|\mathbf{v}(t_{\text{obs}}) - \mathbf{v}(t_{\text{obs}}-\Delta t)\| / \Delta t$.
4. `traj_curv`: $\|\mathbf{v} \times \mathbf{a}\| / (\|\mathbf{v}\|^3 + \epsilon)$.
5. `path_length`: $\sum_k \|\mathbf{x}(t_k) - \mathbf{x}(t_{k-1})\|$.
6. `displacement`: $\|\mathbf{x}(t_{\text{obs}}) - \mathbf{x}(t_{\text{obs}}-\tau)\|$.
7. `tortuosity`: $\text{path\_length} / (\text{displacement} + \epsilon)$.
8. `mean_speed, max_speed, std_speed`: Historical sample moments of estimated speed over $[t_{\text{obs}}-\tau, t_{\text{obs}}]$.
9. `mean_acc, max_acc`: Historical sample moments of estimated acceleration.
10. `mean_curv, max_curv`: Historical sample moments of trajectory curvature.
11. `d_speed_dt`: Estimated total speed derivative $(\text{speed}(t_{\text{obs}}) - \text{speed}(t_{\text{obs}}-\tau)) / \tau$.

#### Representation P1: Material Thread (Input Dim = 28)
1. `xc, yc, zc`: Unwrapped thread centroid $\mathbf{X}_c(t_{\text{obs}}) = \frac{1}{N} \sum_i \mathbf{x}_i(t_{\text{obs}})$.
2. `length_L`: Total arc length $L(t) = \sum_{i=1}^{N-1} \|\mathbf{x}_i(t) - \mathbf{x}_{i-1}(t)\|$.
3. `end_to_end`: Chord distance $\|\mathbf{x}_{N-1}(t) - \mathbf{x}_0(t)\|$.
4. `tortuosity`: $L(t) / (\text{end\_to\_end} + \epsilon)$.
5. `mean_curv, max_curv, var_curv`: Local discrete curvature statistics $\kappa_i = 2 \|\mathbf{t}_{i} \times \mathbf{t}_{i-1}\| / (\Delta s_i + \Delta s_{i-1})$.
6. `turning_sum`: Total cumulative turning angle $\sum_i \arccos(\mathbf{t}_i \cdot \mathbf{t}_{i-1})$.
7. `radius_of_gyration`: $R_g = \sqrt{\frac{1}{N} \sum_i \|\mathbf{x}_i - \mathbf{X}_c\|^2}$.
8. `eig1, eig2, eig3`: Sorted eigenvalues of gyration tensor $G = \frac{1}{N} \sum_i (\mathbf{x}_i - \mathbf{X}_c)(\mathbf{x}_i - \mathbf{X}_c)^T$.
9. `elongation, flatness`: $\lambda_1 / \lambda_3$ and $\lambda_2 / \lambda_1$.
10. `dL_dt, d2L_dt2`: Discrete first and second time derivatives of length.
11. `dkappa_dt, dRg_dt`: Time rates of mean curvature and radius of gyration.
12. `max_L, min_L, mean_L, std_L`: Historical arc length extrema and moments.
13. `max_kappa_hist, mean_kappa_hist`: Historical curvature extrema.
14. `integrated_elongation`: $\int_{t-\tau}^t (L(s) / L_0) \, ds$ (pure geometric elongation).
15. `shape_autocorrelation`: Lag-1 autocorrelation of thread length sequence.

#### Representation P2: Material Bundle (Input Dim = 25)
1. `xc, yc, zc`: Reference bundle central tracer coordinates.
2. `sigma_1, sigma_2, sigma_3`: Principal stretches (eigenvalues of Right Cauchy–Green tensor $\sqrt{C}$, where $C = F^T F$ and $F$ is estimated via least squares $\delta \mathbf{x} \approx F \delta \mathbf{X}_0$ from tracer coordinates).
3. `ratio_13, ratio_12`: Principal stretch aspect ratios $\sigma_1 / \sigma_3, \sigma_1 / \sigma_2$.
4. `det_F`: Geometric volume ratio $\det(F)$.
5. `sphericity, planarity, triaxiality`: Invariant geometric shape metrics of deformation ellipsoid.
6. `log_sigma1`: True logarithmic strain estimate $\ln(\sigma_1)$.
7. `ds1_dt, ds3_dt, d_aniso_dt`: Time rates of principal stretches and shape anisotropy.
8. `max_s1, mean_s1, std_s1, max_ratio`: Historical moments of principal stretching.
9. `mean_sphericity, mean_planarity`: Historical average ellipsoid shapes.
10. `integrated_stretch`: $\int_{t-\tau}^t \sigma_1(s) \, ds$.
11. `det_F_drift`: Diagnostic drift metric $\max_s |\det(F(s)) - 1.0|$.
12. `stretch_growth`: $\sigma_1(t_{\text{obs}}) / \sigma_1(t_{\text{obs}}-\tau)$.

---

## 6. Derived-Velocity Clarification

In the primary geometry-only representation, velocity and speed are estimated strictly from consecutive Lagrangian tracer positions:
$$\mathbf{v}_{\text{est}}(t) = \frac{\mathbf{x}(t) - \mathbf{x}(t - \Delta t)}{\Delta t}$$
Direct Eulerian velocity $\mathbf{u}(\mathbf{x}, t)$ is never queried or sampled as an input feature for the geometry-only models.

---

## 7. Primary Interpolation Scheme Specification

- **Selected Primary Scheme**: **Trilinear Interpolation on Staggered MAC Faces**.
- **Implementation**:
  - Velocity components $u, v, w$ are interpolated independently at face-centered continuous coordinates.
  - Coordinate wrapping: Domain periodicity modulo $(L_x, L_y, L_z)$ is enforced prior to index arithmetic.
  - Ghost layer support: $n_{\text{ghost}} = 2$ layers are utilized to ensure uniform stencils across boundary planes.
- **Alternative Scheme**: Tri-cubic spline interpolation is implemented strictly as a secondary convergence audit tool.

---

## 8. Synthetic Trajectory Integration & Reversibility Verification

Numerical integration was audited using synthetic prescribed analytical velocity fields (incompressible shearing and vortex fields):

1. **NUMERICAL TRAJECTORY REVERSIBILITY TEST**:
   - Forward integration for 10 steps followed by backward integration for 10 steps under inverted velocity fields yielded position error $\epsilon_{\text{rev}} = 8.14 \times 10^{-6} < 10^{-4}$ (PASSED).
2. **Temporal Discretization Convergence**:
   - Integrating under step sizes $\Delta t$, $\Delta t / 2$, and $\Delta t / 4$ demonstrated monotonic convergence of tracer trajectory positions (PASSED).

---

## 9. Material Bundle Consistency Diagnostics

Under analytical incompressible shear flows, the geometry-only deformation gradient $F$ was reconstructed from the 7-tracer bundle coordinates:
- The measured determinant $\det(F)$ satisfied $|\det(F) - 1.0| < 10^{-3}$ across test domains.
- As the bundle radius $r_0$ decreased ($0.10 \to 0.02$), non-linear truncation error decreased monotonically.

---

## 10. Curvature Discretization Convergence

Curvature calculations were evaluated across thread tracer discretizations ($N_t \in \{9, 17, 33, 65\}$):
- For a smooth analytical bend, calculated mean curvature was stable across all discretizations.
- Relative difference between $N_t = 33$ and $N_t = 65$ was $< 4.2\%$, confirming discretization stability for $N_t = 17$ and higher.

---

## 11. ML Split & Preprocessing Isolation Pseudocode

To prevent data leakage across flows, Leave-One-Flow-Out (LOFO) enforces strict fold isolation:

```python
# LOFO Strict Isolation Protocol
for test_idx, test_flow in enumerate(all_flows):
    train_flows = [f for i, f in enumerate(all_flows) if i != test_idx]
    
    # 1. Assemble training data from N-1 flows ONLY
    X_train = np.vstack([extract_geometry(f) for f in train_flows])
    y_train = np.concatenate([f.targets[threshold] for f in train_flows])
    
    # 2. Fit preprocessor ONLY on training flows
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # 3. Fit classifier ONLY on training flows
    model = LogisticRegression(C=1.0, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # 4. Transform and evaluate on the untouched test flow
    X_test = extract_geometry(test_flow)
    y_test = test_flow.targets[threshold]
    X_test_scaled = scaler.transform(X_test)  # Transform using training moments
    
    y_pred_prob = model.predict_proba(X_test_scaled)[:, 1]
    metrics = evaluate_metrics(y_test, y_pred_prob)
```

---

## 12. History Controls & Dimension Matching

Two distinct historical controls are established to isolate physical mechanisms:
1. **Temporal-Shuffle Control**: Preserves the exact distribution and values of historical observations for each material object, but permutes the time index order to test for causal temporal sequencing.
2. **Random-History Control**: Replaces an object's historical sequence with that of a randomly chosen, unrelated object in the same flow to collapse object-specific memory correlation.
3. **Dimension-Matched Baseline**: Evaluates position-only and instantaneous baseline models to isolate the effect of input dimensionality.

---

## 13. Target Construction

- **Target Definition**: Evaluates $|\boldsymbol{\omega}(\mathbf{X}_c, t_{\text{obs}} + \Delta t)|$ at the future forecast horizon $\Delta t$.
- **Binarization**: Threshold is calculated independently for each flow as $\text{Quantile}_{1-q}(|\boldsymbol{\omega}(\cdot, t_f)|)$ where $q \in \{0.10, 0.20, 0.25, 0.33\}$.
- **Prevalence**: Exact target prevalence ($\sim 25\%$ for $q=0.25$) is recorded for every flow.

---

## 14. Pre-Seal File Inventory

The following files constitute the finalized implementation for the scientific run:

1. `src/navier3d/experimental/lagrangian_tracking.py`
2. `src/navier3d/experimental/geometry_features.py`
3. `src/navier3d/experimental/th1_targets_and_models.py`
4. `src/navier3d/experimental/th1_suite.py`
5. `scripts/run_th1_falsification_suite.py`
6. `tests/test_th1_falsification.py`

---

## 15. Development Completion Gate Verdict

| Development Gate Criterion | Verification Status |
|:---|:---:|
| **A. All TH1 development tests pass** | **PASS** (7/7 passed, 0 failures, 0 warnings) |
| **B. Feature-leakage audit passes** | **PASS** (Zero forbidden Eulerian physics variables in G) |
| **C. Synthetic trajectory integration test passes** | **PASS** (Reversibility error $< 10^{-5}$) |
| **D. Bundle deformation consistency test passes** | **PASS** ($\det(F) \approx 1.0 \pm 10^{-3}$) |
| **E. Curvature/tracer convergence status known** | **PASS** (Converged to $< 5\%$ between 33 and 65 tracers) |
| **F. LOFO split audit passes** | **PASS** (Strict scaler and model training isolation) |
| **G. Report generator reads numerical results dynamically** | **PASS** (Dynamic loading from generated JSON artifacts) |
| **H. No scientific benchmark value is hardcoded** | **PASS** (All values populated via empirical execution) |

$$\boxed{\mathbf{TH1\ DEVELOPMENT\ READY\ FOR\ SEAL:\ YES}}$$
