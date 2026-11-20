# Milestone TH1R Forensic Audit: Material-History Claims, Feature Representations, and Governance Reconciliation

```
AUDIT STATUS: FORENSIC INVESTIGATION COMPLETE
EVIDENCE CLASSIFICATION: PREVIOUS TH1 RUN = TH1_DEV_EXPLORATORY
FINDINGS: CRITICAL ARTIFACTS IDENTIFIED IN TEMPORAL SHUFFLE AND POSITION LEAKAGE
```

---

## 1. Executive Summary of Forensic Findings

A comprehensive line-by-line inspection of the exploratory development pipeline (`geometry_features.py`, `lagrangian_tracking.py`, `th1_targets_and_models.py`, `th1_suite.py`, and `run_th1_falsification_suite.py`) revealed three fundamental design flaws that explain the exploratory findings:

1. **Tabular Column Permutation vs. True Trajectory Time Shuffling**:
   - In `geometry_features.py` (lines 404–418), `apply_temporal_shuffle` and `apply_history_reversal` were implemented by permuting or reversing the **columns (feature axes)** of the pre-extracted tabular matrix $X$.
   - Because standard linear classifiers ($L_2$-logistic regression) are invariant to column reordering (the optimizer simply permutes the learned weights), the model was mathematically forced to produce **bit-identical predictions** ($AUC_{\text{ord}} = AUC_{\text{shuff}} = AUC_{\text{rev}} = 0.5319597156996415$).
   - **Verdict**: Temporal order was **never tested** in the exploratory run; the identical AUCs were a pure mathematical artifact of tabular column permutation.
2. **Order-Invariant Summary Features**:
   - The majority of extracted historical features were time-integrated summary statistics (mean, variance, max, min, total displacement) which are intrinsically invariant to temporal ordering.
3. **Absolute Spatial Location Leakage**:
   - All representation levels ($P_0, P_1, P_2$) included the current spatial coordinates $[x, y, z]$ or centroid $[X_c, Y_c, Z_c]$ in the feature vector.
   - In spatially inhomogeneous flows (such as periodic shear layers or Taylor–Green vortices), absolute coordinates act as a proxy for spatial flow phase (memorizing where vortex cores or shear bands reside) rather than measuring Lagrangian material deformation.

---

## 2. Critical History-Order Audit: Feature Classification

Every feature in the exploratory historical feature set is classified below based on whether its mathematical definition is sensitive to the sequence order of time observations:

| Feature Name | Exact Mathematical Formulation | Order-Sensitive? | Changes Under True Temporal Shuffle? |
|:---|:---|:---:|:---:|
| `xc, yc, zc` | $\mathbf{x}(t_{\text{obs}})$ | No (Instantaneous) | No |
| `length_L(t_obs)` | $L(t_{\text{obs}}) = \sum_i \|\mathbf{x}_i(t_{\text{obs}}) - \mathbf{x}_{i-1}(t_{\text{obs}})\|$ | No (Instantaneous) | No |
| `end_to_end` | $\|\mathbf{x}_{N-1}(t_{\text{obs}}) - \mathbf{x}_0(t_{\text{obs}})\|$ | No (Instantaneous) | No |
| `tortuosity` | $L(t_{\text{obs}}) / d_{\text{end}}(t_{\text{obs}})$ | No (Instantaneous) | No |
| `mean_curv, max_curv` | $\frac{1}{N-2}\sum \kappa_i(t_{\text{obs}})$ | No (Instantaneous) | No |
| `radius_of_gyration` | $\sqrt{\frac{1}{N} \sum \|\mathbf{x}_i(t_{\text{obs}}) - \mathbf{X}_c\|^2}$ | No (Instantaneous) | No |
| `principal_axes_eig` | $\text{eig}(\frac{1}{N}\sum (\mathbf{x}_i - \mathbf{X}_c)(\mathbf{x}_i - \mathbf{X}_c)^T)$ | No (Instantaneous) | No |
| `mean_L, std_L` | $\frac{1}{W}\sum_{k=0}^{W-1} L(t_k), \ \text{std}_k(L(t_k))$ | **ORDER-INVARIANT** | **No** |
| `max_L, min_L` | $\max_k L(t_k), \ \min_k L(t_k)$ | **ORDER-INVARIANT** | **No** |
| `max_kappa, mean_kappa` | $\max_k \bar{\kappa}(t_k), \ \frac{1}{W}\sum_k \bar{\kappa}(t_k)$ | **ORDER-INVARIANT** | **No** |
| `integrated_elongation` | $\int_{t-\tau}^t (L(s)/L_0) ds \approx \sum_k L(t_k) \Delta t$ | **ORDER-INVARIANT** | **No** |
| `dL_dt` | $(L(t_{\text{obs}}) - L(t_{\text{obs}}-\tau)) / \tau$ | Boundary endpoints only | Only if endpoints permuted |
| `d2L_dt2` | Second difference of length | Order-Sensitive | Yes |
| `dkappa_dt, dRg_dt` | Endpoint difference | Boundary endpoints only | Only if endpoints permuted |
| `shape_autocorrelation` | $\text{Corr}(L(t_k), L(t_{k-1}))$ | **ORDER-SENSITIVE** | **Yes** |

---

## 3. Forensic Inspection of Temporal Permutation

In `geometry_features.py`:
```python
def apply_temporal_shuffle(history_matrix: np.ndarray, seed: int = 42) -> np.ndarray:
    rng = np.random.RandomState(seed)
    shuffled = history_matrix.copy()
    n_samples, total_dim = shuffled.shape
    perm = rng.permutation(total_dim)  # BUG: Permutes columns (features), NOT time steps
    return shuffled[:, perm]
```

### Analytical Proof of Zero Effect:
Let the training design matrix be $X \in \mathbb{R}^{N \times D}$ and the permutation matrix be $P \in \mathbb{R}^{D \times D}$.
For any regularized linear model minimizing $\|X \mathbf{w} - \mathbf{y}\|_2^2 + \lambda \|\mathbf{w}\|_2^2$:
- The transformed problem minimizes $\|(X P) \mathbf{w}' - \mathbf{y}\|_2^2 + \lambda \|\mathbf{w}'\|_2^2$.
- The unique solution is $\mathbf{w}' = P^T \mathbf{w}$.
- For test point $\mathbf{x}_{\text{test}}$, the prediction is $(P^T \mathbf{x}_{\text{test}})^T \mathbf{w}' = \mathbf{x}_{\text{test}}^T P P^T \mathbf{w} = \mathbf{x}_{\text{test}}^T \mathbf{w}$.
- Therefore, the test predictions and ROC-AUC are **mathematically identical down to machine precision**.

$$\boxed{\mathbf{STATEMENT:\ TEMPORAL\ ORDER\ WAS\ REMOVED\ BY\ FEATURE\ ENGINEERING\ AND\ TABULAR\ PERMUTATION.}}$$

---

## 4. Absolute Location Leakage vs. Intrinsic Deformation

In the exploratory run, the feature dimensions were:
- **P0 Particle**: $[x, y, z, \text{speed}, \text{acc}, \dots]$ (Position represents $3/6 = 50\%$ of instantaneous features).
- **P1 Thread**: $[X_c, Y_c, Z_c, L, d_{\text{end}}, \dots]$ (Centroid position represents $3/16 = 18.8\%$ of instantaneous features).
- **P2 Bundle**: $[X_c, Y_c, Z_c, \sigma_1, \sigma_2, \sigma_3, \dots]$.

In inhomogeneous flows (periodic shear layers and Taylor–Green benchmarks), intense vorticity is localized at specific coordinates $(x, y, z)$. Classifiers trained with $[x, y, z]$ easily achieve $\text{AUC} > 0.60$ purely by identifying high-vorticity spatial bands, without extracting any Lagrangian deformation mechanics.

### Reconciliation Strategy for TH1R:
To isolate material deformation, features must be partitioned into:
1. **Absolute Location Models**: Features including global coordinates $\mathbf{x}(t)$ or centroid $\mathbf{X}_c(t)$.
2. **Intrinsic Deformation Models**: Pure internal geometry relative to centroid:
   - Particle: Displacement increments $\Delta \mathbf{x}(t_k) = \mathbf{x}(t_k) - \mathbf{x}(t_{k-1})$, speeds, and trajectory curvature (origin centered at current position $\mathbf{x}(t_{\text{obs}}) = \mathbf{0}$).
   - Thread: Intrinsic arc length, internal node curvature, tortuosity, gyration tensor eigenvalues, and relative orientation changes with $\mathbf{X}_c$ removed.
   - Bundle: Right Cauchy–Green eigenvalues (principal stretches $\sigma_1, \sigma_2, \sigma_3$), volume determinant $\det(F)$, and ellipsoid shape invariants with $\mathbf{X}_c$ removed.

---

## 5. Summary of Required Development Corrections for TH1R

1. **True Time-Lag History Representation**:
   - Replace order-invariant summary statistics with explicit ordered lag vectors:
     $$\mathbf{S}_{\text{ordered}} = [s(t_{\text{obs}}), s(t_{\text{obs}} - \Delta t), s(t_{\text{obs}} - 2\Delta t), \dots, s(t_{\text{obs}} - \tau)]$$
     for key intrinsic scalars (e.g. length $L(t)$, speed $v(t)$, principal stretch $\sigma_1(t)$).
2. **True Trajectory Time-Shuffling**:
   - Implement `shuffle_trajectory_time_order()` that randomly permutes the temporal sequence $t_0, t_1, \dots, t_W$ **at the raw trajectory level before lag feature extraction**.
3. **Strict Spatial Normalization**:
   - Implement `intrinsic` vs `absolute` feature flags across P0, P1, and P2.
4. **Dimension-Matched Controls**:
   - Match feature vector dimensions across P0, P1, and P2 when comparing topological information content.
5. **Pre-Seal Protocol**:
   - Retain existing exploratory artifacts in `evidence/th1/` labeled as `TH1_DEV_EXPLORATORY`.
   - Maintain development isolation until explicit review approval.
