# `tubulance` — 3D Navier–Stokes Regularity, $\mathrm{Cl}(3,0)$ Helical Schur & Unified Rosetta Audit (`v1.2.0-rosetta`)

- **Unified 4-Workspace & 7-Domain Monograph:** [paper/ROSETTA_UNIFIED_FOUR_WORKSPACES_AND_SEVEN_DOMAINS_MONOGRAPH.pdf](paper/ROSETTA_UNIFIED_FOUR_WORKSPACES_AND_SEVEN_DOMAINS_MONOGRAPH.pdf) | [TeX](paper/ROSETTA_UNIFIED_FOUR_WORKSPACES_AND_SEVEN_DOMAINS_MONOGRAPH.tex)
- **General-Reader Essay & Rosetta Measurement Atlas:** [SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.md](SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.md) | [PDF](SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf) (Zenodo DOI [`10.5281/zenodo.24403362`](https://zenodo.org/record/24403362))
- **$\mathrm{Cl}(3,0)$ Superfluid Monograph:** [paper/cl30_helical_schur_superfluid_monograph.pdf](paper/cl30_helical_schur_superfluid_monograph.pdf) (Zenodo DOI [`10.5281/zenodo.24403360`](https://zenodo.org/record/24403360))
- **Lean 4 Certificates (`formal/`):**
  - [RosettaUniversalMetaTheorems.lean](formal/RosettaUniversalMetaTheorems.lean), [NavierStokesWinWinArchCert.lean](formal/NavierStokesWinWinArchCert.lean), [RosettaGrandPlanStage4Cert.lean](formal/RosettaGrandPlanStage4Cert.lean), [NavierStokesNS1NS2BridgeCert.lean](formal/NavierStokesNS1NS2BridgeCert.lean), [RosettaFourWorkspaceProofBridgesCert.lean](formal/RosettaFourWorkspaceProofBridgesCert.lean), [RosettaMongeAmpereSeesawCrossProofsCert.lean](formal/RosettaMongeAmpereSeesawCrossProofsCert.lean), [RosettaWorldwideSevenDomainsCert.lean](formal/RosettaWorldwideSevenDomainsCert.lean)
- **Key Probes (`scripts/`):**
  - [probe_cl30_helical_schur_and_vorticity_cocycle.py](scripts/probe_cl30_helical_schur_and_vorticity_cocycle.py), [probe_win_win_cocycle_dichotomy_arch.py](scripts/probe_win_win_cocycle_dichotomy_arch.py), [probe_win_win_arch_resolution_scaling.py](scripts/probe_win_win_arch_resolution_scaling.py), [probe_ns_time_evolution_win_win_arch.py](scripts/probe_ns_time_evolution_win_win_arch.py), [probe_adversarial_nogo_barriers.py](scripts/probe_adversarial_nogo_barriers.py), [probe_four_workspace_proof_bridges.py](scripts/probe_four_workspace_proof_bridges.py), [probe_monge_ampere_seesaw_cross_proofs.py](scripts/probe_monge_ampere_seesaw_cross_proofs.py), [probe_worldwide_7domains_rosetta.py](scripts/probe_worldwide_7domains_rosetta.py)
- **GitHub Release & Zenodo DOIs:** https://github.com/Qamarbajwa/tubulance/releases/tag/v1.2.0-rosetta | [`10.5281/zenodo.24399167`](https://zenodo.org/record/24399167) | [`10.5281/zenodo.24403353`](https://zenodo.org/record/24403353)
- **Master Audit Receipt:** [rosetta_master_audit_receipt.json](rosetta_master_audit_receipt.json) (`4/4 PASS`, Zero-Axiom Finite-Dimensional & Parameterized Bridge Certification in Lean 4; in this work, ai is being used as a tool by Arqam, Brandenburg University of Technology Cottbus-Senftenberg)

---

# JHTDB terminal-layer benchmark

This folder contains the first real-data benchmark harness for the finite-scale
terminal-layer turbulence model.

## Why it must run on SciServer

The official JHTDB project recommends SciServer because its compute containers
are directly connected to the turbulence database and provide the Giverny
libraries and mounted data volumes. A local authorization token may also be
used, but the precise client call depends on the current Giverny release.

## Setup

1. Create a SciServer account.
2. Open **Compute** and create an **Essentials 4.0** container.
3. Mount the **Turbulence** data volume.
4. Download the current official `DEMO_SciServer_python_notebooks.zip`.
5. Copy the velocity-cutout call from the demo into
   `fetch_velocity_cutout()` in `jhtdb_terminal_benchmark.py`.
6. Run:

```bash
python jhtdb_terminal_benchmark.py
```

## First outputs

- `apriori_metrics.csv`
- `spectra.csv`
- `spectral_comparison.png`

## Pass/fail checks

The first test should report:

- zero energy above the selected cutoff for the filtered and terminal fields;
- spectral error below the cutoff;
- spectral error specifically inside the terminal layer;
- terminal heat and return fractions;
- DNS, filtered-DNS, and terminal-field vorticity statistics.

This is an **a-priori operator test**. It does not yet prove that the model
evolves correctly in time. After it passes, use two JHTDB snapshots separated
by a known interval to measure the actual sub-filter energy transfer, then run
the complete forward model for the same interval.

## Validation status (2026-07-24)

**Pipeline validation passed; physical validation inconclusive because of
insufficient spectral resolution.**

The full workflow (fetch → filter → terminal operator → spectrum →
frame-to-frame transfer difference) was exercised end-to-end against two real
JHTDB `isotropic1024coarse` cutouts cached locally
(`isotropic1024coarse.h5`, `isotropic1024coarse (1).h5`), both only 16³ —
far below the 128³+ this benchmark is designed for. Findings from that run:

- The complete pipeline works: fetch → filter → terminal operator →
  spectrum → frame-to-frame transfer difference.
- Most measured energy change occurred at `k=1`.
- A small gain appeared at `k=3`.
- A small loss appeared at `k=4`, close to the cutoff.
- Shells `k≥5` were empty in both frames.
- The terminal layer at this resolution spans too few populated shells to
  test its physical behavior — heat/backscatter behavior cannot be
  distinguished from plain filtering.

**This run does not support or reject the terminal-layer theory.** It only
confirms the code path is correct. `jhtdb_terminal_benchmark.py` now enforces
this automatically: it computes `run_status.json` with a `blocked`/`ok`
status and, when blocked, records exactly which physical requirement below
was not met instead of silently producing physics metrics that shouldn't be
trusted.

## Open validation blockers

Both must be resolved before a run of this benchmark can be treated as a real
test of the terminal-layer theory, not just a pipeline smoke test.

### 1. Real spatial resolution

The benchmark needs at least a 128³ JHTDB cutout (256³ supported when
resources allow) so the terminal layer spans enough independent wavenumber
shells to have a shape distinguishable from a hard cutoff.

The terminal layer's independent shell count is

```
N_T = (kc - ks) / delta_k
```

with `delta_k = 2*pi / domain_length`. Requirements enforced in
`Config`/`compute_terminal_layer`/`validate_terminal_layer`:

- `N_T >= 6` required (`min_terminal_shells`)
- `N_T >= 8` preferred (`preferred_terminal_shells`)

A fixed `beta = ks/kc` is **not** used when it would produce fewer than the
required shells: the terminal-layer start is instead derived as
`ks = kc - N_T * delta_k`, and `beta` is reported as an *effective*,
resolution-aware value (`beta_effective`) rather than assumed a priori. Two
runs can share the same `beta` while representing the terminal layer with
radically different numbers of modes — `N_T` is the number that actually
matters.

The physical benchmark in `main()` stops (status `blocked` in
`run_status.json`) when any of the following hold:

- fewer than 6 terminal shells exist;
- fewer than 4 terminal shells contain measurable DNS energy
  (`min_populated_terminal_shells`, `energy_floor`);
- the cutoff is too close to Nyquist (`max_cutoff_fraction_of_nyquist`,
  default 0.8);
- the forcing and terminal ranges lack sufficient scale separation (checked
  only when `Config.forcing_kmax` is set — `isotropic1024coarse`'s forcing
  wavenumber range has not been confirmed against official JHTDB
  documentation in this project, so this check is off by default rather
  than silently assumed to pass).

### 2. Confirmed temporal separation

`measure_transfer.py` no longer accepts bare frame indices as a stand-in for
real time. It requires two explicit `TimeCoordinate` objects (`time_1`,
`time_2`) and computes `delta_t = t2 - t1` only when both carry
`dt_confirmed=True` with a recorded source. Local HDF5 exports' `t_start`/
`t_end`/`t_step` attrs record what was passed to the cutout query, not a
documented physical `Δt` — so a local-file-derived `TimeCoordinate` is always
`dt_confirmed=False`, and adjacent frame numbers are never assumed to be
unit-spaced in real time.

Each `TimeCoordinate` records: dataset name, requested time, returned time
(when known), interpolation method, frame index (when applicable), and
whether time is dimensional or nondimensional. When `delta_t` cannot be
established, `measure_transfer.py` still reports the dimensionless
`delta_E_per_frame(k)` diagnostic but clearly labels the rate as unavailable,
in both console output and `transfer_measurement_metadata.json`.
`compare_model_to_dns.py` (the next benchmark, below) treats confirmed
`Δt` as a hard requirement and raises immediately rather than producing
numbers that can't be physically interpreted.

Use official JHTDB/Giverny metadata or documentation as the authority for
`Δt`; do not infer it from frame spacing.

## The next benchmark: DNS vs. model comparison

`compare_model_to_dns.py` implements the forward-validation-adjacent stage:
given two DNS snapshots at a confirmed time separation,

1. fetch both velocity snapshots at confirmed times;
2. apply the same spectral filter to both;
3. compute shell energies `E(k,t1)`, `E(k,t2)`;
4. compute the measured shell-energy rate
   `Edot_DNS(k) = (E(k,t2) - E(k,t1)) / Δt`;
5. evaluate the terminal operator once on the first snapshot;
6. compare its predicted shell-wise removal with the measured DNS evolution
   (heat and backscatter/return kept as separate predicted series);
7. report region-by-region comparisons: ordinary resolved region, terminal
   region, final two shells before `kc`, and total energy below/above `kc`.

Metrics reported per region: correlation between `Edot_DNS(k)` and
`Edot_model(k)`, relative L2 error, sign-agreement fraction, plus an overall
terminal power ratio

```
terminal_power_ratio = sum(-Edot_model(k), ks<=k<=kc) / sum(-Edot_DNS(k), ks<=k<=kc)
```

and a qualitative note on whether the DNS shows net forward transfer, local
backscatter, or both over the interval (a descriptive read of the sign
pattern, not a decomposed flux calculation).

This script has the same two hard requirements as above (confirmed `Δt`,
resolution-adequate terminal layer) and raises immediately, before doing any
spectral work, if either is unmet — it will not run against the local 16³
cutouts or against any snapshot pair without a confirmed `Δt`.

## Milestone 3: nonlinear-transfer validation (2026-07-24)

`nonlinear_transfer.py` implements the true, instantaneous nonlinear
spectral transfer — not the finite-difference approximation above. For
incompressible velocity `u`, it computes `N(x) = -(u.grad)u`, projects it
onto the divergence-free subspace, and forms the modal transfer

```
T(k_vec) = Re[ conj(u_hat(k_vec)) . N_hat_perp(k_vec) ] / n3^2
```

aggregated to shells `T(k)`, with cumulative spectral flux
`Pi(k) = -sum_{p<=k} T(p)` (positive = forward/direct cascade). Unlike the
finite-difference stage, this needs only **one** DNS snapshot — no
confirmed `Δt` required — because `T(k)` is instantaneous. Global
conservation (`sum_k T(k) ≈ 0`, the inviscid/unforced energy-conserving
property of the nonlinear term) is checked and reported; optional 2/3-rule
dealiasing (`dealias=True`) reduces the residual by removing aliased
triads, not by cancellation. See the module docstring for the full sign
convention and `tests/test_nonlinear_transfer.py` for the analytic checks
(a single Fourier mode pair and the Taylor-Green vortex both have exactly
zero self-transfer by a parity argument; a resonant triad does not).

`nonlinear_transfer_validation.py` compares DNS `T(k)`/`Pi(k)` against the
terminal operator's predicted shell-wise removal (heat and backscatter kept
separate), region by region: forcing region (only when `Config.forcing_kmax`
is set), inertial/resolved region, terminal region, and the final two
populated shells before `kc`. It reports, in addition to the per-region
correlation/relative-L2/sign-agreement: `flux_relative_l2_error`,
`terminal_processing_to_dns_flux_ratio` (model's terminal removal power
vs. the DNS flux actually arriving at `kc`), `fraction_terminal_shells_
showing_local_backscatter`, and `bottleneck_ratio_relative_to_filtered_dns`
(terminal-model vs. plain-filtered-DNS energy pileup in the last two
shells before `kc`). Same hard resolution requirement as above; raises
immediately rather than running against the local 16³ cutout.

Every real-data run is classified via `run_classification.py` into one of:
`blocked`, `pipeline_only`, `apriori_operator_valid`,
`finite_difference_comparison_valid`, `nonlinear_transfer_comparison_valid`,
`forward_validation_required` — a strict ladder documented in that module.
Reaching `nonlinear_transfer_comparison_valid` does not by itself mean the
theory is supported: `run_classification.positive_result_bar()` encodes the
"first real positive result" criteria (`N_T >= 6`, `>= 4` populated
terminal shells, transfer conservation residual within tolerance, zero
energy above cutoff in the filtered/terminal fields, and
`corr(T_DNS, T_model) > 0`). Only when all of those hold does a run reach
`forward_validation_required` — and even then that is **a-priori
consistency, not full validation**. Full validation requires running the
terminal model forward in time from a DNS snapshot and comparing evolved
statistics over several turnover times, which is not implemented.

`convergence_table.py` is the resolution-convergence scaffold: it runs the
same pipeline at 64³ (diagnostic only), 128³ (minimum physical test), 256³
(preferred), and above, producing a table of grid size, `kc`, `ks`,
effective `beta`, terminal shell count, populated terminal shell count,
spectrum/transfer/flux error, bottleneck ratio, runtime, and peak memory.
As of 2026-07-24 only the local 16³ cutout is real data — every other tier
requires an explicit `fetch` callable and reports `status="no_data"`
instead of a fabricated row when none is supplied (see blocker #1 above).

## Milestone 4: complete predicted transfer, expanded metrics, ensemble infra (2026-07-24)

**Correctness fix.** Milestone 3's `T_model(k)` used `-gamma(k)*E(k)` (the
*total* removal, heat and return combined) as if it were all a net loss.
Only the heat fraction is a genuine kinetic-energy sink — the return
(backscatter) fraction is redistributed, not destroyed, so comparing DNS
`T(k)` against the total removal systematically penalized the model for
energy it intentionally returns elsewhere. `nonlinear_transfer_validation.py`
now constructs the complete predicted transfer

```
T_model(k) = T_remove(k) + T_return(k),  T_remove(k) = -gamma(k)E(k)
```

`T_return(k)` needs a spectral *placement* (which shell receives the
returned energy) that the terminal operator does not currently specify
beyond the aggregate heat/return split. `Config.backscatter_placement`
documents this assumption; `"local"` (the only implemented value)
reinjects the return fraction at the same shell it left — the placement
consistent with having no other information, not a guessed spatial rule.
Under `"local"`, `T_model(k)` reduces exactly to `-alpha(k)*gamma(k)*E(k)`
(heat only), and `model_transfer_conservation` in the result confirms
`sum_k T_model(k) = -total_heat` to numerical precision. If the theory
later specifies a real placement rule, add it as a new
`backscatter_placement` value rather than assuming `"local"` is physically
correct.

**Three separate comparisons**, no longer collapsed into one score:

- `removal_only_comparison`: `T_DNS(k)` vs. `T_remove(k)`, restricted to
  shells where DNS shows net loss.
- `regions` (`forcing_region`, `inertial_resolved_region`,
  `terminal_region`, `final_two_shells_before_kc`): `T_DNS(k)` vs. the
  *complete* `T_model(k)`, across the full permitted range.
- `flux_comparison` + `flux_plateau_error_below_ks`: `Pi_DNS(k)` vs.
  `Pi_model(k)` (now built from the corrected `T_model`), plus the mean
  absolute flux difference below `ks` (where a clean inertial range would
  show a roughly constant plateau).

**Shape vs. magnitude metrics.** `comparison_metrics.extended_region_metrics()`
adds Spearman rank correlation, cosine similarity, normalized mean absolute
error, and peak-shell location error alongside the existing Pearson
correlation/relative-L2/sign-agreement — a model can have the right
spectral shape with the wrong magnitude, or vice versa; these are reported
separately rather than folded into one number.

**Run metadata.** `run_metadata.py` records, per real run: dataset, exact
spatial origin/cube size/stride (read from the actual HDF5 export's attrs
via `spatial_origin_from_local_h5()`, never from `Config` defaults that a
local-file fetch doesn't actually use), time coordinate, filtering method,
FFT normalization convention, `kc`/`ks`/`delta_k`/`N_T`, populated terminal
shells, effective `beta`, Nyquist separation, forcing separation, runtime,
and peak memory. Anything not determinable is reported as an explicit
"not recorded" note — never inferred.

**Multi-snapshot ensemble.** `snapshot_ensemble.py` runs the nonlinear-
transfer validation across multiple snapshots and reports per-snapshot
metrics plus mean/std/median/worst-case. `dataset_level_classification()`
implements the item-6 rule: a dataset may be described as showing
a-priori consistency only when *all* of — ≥5 snapshots pass structural
checks, nonlinear/model-transfer conservation within tolerance, zero
energy above cutoff, `N_T ≥ 6`, ≥4 populated terminal shells, and transfer
agreement positive in a *majority* of snapshots — hold. Deliberately
*not* auto-determined: bottleneck severity. No numerical severity
threshold has been set from a real-data distribution yet, so the function
reports the `bottleneck_ratio` distribution across snapshots instead of
inventing a pass/fail cutoff — thresholds get set after seeing the real
distribution, not before.

**Visual outputs.** `nonlinear_transfer_validation.py` now produces a
6-panel per-snapshot dashboard (energy spectra, shell transfer, cumulative
flux, removal/heat/return components, terminal-layer zoom, residual
`T_model - T_DNS` by shell). `snapshot_ensemble.py` and
`convergence_table.py` add dataset-level plots (metric distributions,
bottleneck ratio vs. terminal shell count, metric variation across
snapshots, convergence vs. resolution).

**Still blocked: real data.** This environment has no SciServer/Giverny
access, so tiers 64³/128³/256³ and the ≥5-independent-snapshot ensemble
requirement (README items 4–5 of this milestone) remain infrastructure
only — built, tested with synthetic snapshots for code correctness, and
ready to run, but not actually executed against real high-resolution
JHTDB data. Do not read any synthetic-data run through this infrastructure
as evidence about the terminal-layer theory.

## Milestone 5: backscatter-placement discrimination (2026-07-24)

Milestone 4 established that "local" reinjection (`local_cancellation`)
is mathematically consistent but represents **reduced effective damping,
not a modeled inverse cascade** — the return fraction cancels the removal
at the *same* shell it left, so `T_model(k)` there is just `-alpha(k)*
gamma(k)*E(k)`. That's a legitimate algebraic control case, not a
complete physical claim about where backscattered energy actually goes.

**Preregistered placement strategies** (`backscatter_placement.py`),
fixed *before* being run against real data so a later best fit can't be
mistaken for a physical discovery:

- `local_cancellation` — same-shell reinjection (the Milestone 4 default;
  algebraic control case).
- `parent_band_energy_weighted` — reinjects into `[c1*ks, c2*ks]`
  (`0 < c1 < c2 < 1`), weighted by existing energy in that band.
  `Config.parent_band_c1`/`c2` have **no default** — they must be set
  explicitly, which is what "preregistered" means in practice: commit to
  a band before seeing results, don't tune it afterward.
- `turnover_weighted` — reinjects below `ks`, weighted by `E(k)/tau(k)`
  with `tau(k) ~ [k^3 E(k)]^(-1/2)` (eddy turnover time).
- `dns_oracle_diagnostic` — reinjects proportional to the DNS's own
  positive `T(k)` below `ks`. **Diagnostic only** — it uses the answer
  (real DNS transfer) to place the model's return, so it can never be a
  deployable predictive model or appear in a predictive-performance
  claim. Its only legitimate use is as an upper bound: how well *some*
  placement could do if the true return destination were known.

**Conservation is enforced per strategy, not assumed** (Part C):
`verify_placement_conservation()` checks both `sum_k T_return(k) ==
P_return` and `sum_k T_model(k) == -total_heat`, and *raises*
(`PlacementConservationError`) if either residual exceeds
`conservation_tolerance` — a placement that can't place its return
energy (e.g. an empty `parent_band`) fails loudly rather than silently
dropping energy.

**A structural finding worth noting explicitly**: `parent_band_energy_
weighted`, `turnover_weighted`, and `dns_oracle_diagnostic` all reinject
strictly *below* `ks`, so they are indistinguishable from each other —
and from plain `T_remove` — when measured only inside `terminal_region`.
Only `local_cancellation` changes `T_model` within the terminal region
itself. A selection metric restricted to `terminal_region` therefore
cannot discriminate the other three placements at all; `flux_*` and
`inertial_resolved_region` metrics (which are sensitive to where the
returned energy actually lands) are the ones that can. `placement_
comparison.select_placement()` defaults to `flux_relative_l2_error` for
exactly this reason — see the `_METRIC_GETTERS` docstring in
`placement_comparison.py`.

**Comparison and selection (Parts D–E)**. `placement_comparison.py`:

- `compare_placements_on_snapshot()` runs all four strategies on one
  snapshot and reports removal-only, full-transfer, and flux agreement
  (correlation, Spearman, cosine similarity, relative L2, normalized MAE,
  sign agreement, peak-shell location error) plus conservation residuals
  for each.
- `select_placement()` picks a winning *deployable* placement (the
  oracle is excluded) using **only** a calibration snapshot set.
- `run_validation_comparison()` reports all four placements' metrics on a
  **disjoint** validation snapshot set — validation-set outcomes never
  feed back into selection.
- `identifiability_report()` answers Part E directly: for each metric, is
  the spread *induced by placement choice* (across placements, per
  snapshot) larger than the spread *induced by which snapshot was used*
  (across snapshots, per placement)? If fewer than half the tracked
  metrics show placement-induced spread exceeding snapshot-to-snapshot
  spread, the result is `backscatter_placement_not_identifiable` — this
  is a real possible outcome, not a fallback to avoid; on synthetic
  random-noise test data used to verify the code, this is exactly what
  it (correctly) reports.

**Report generation (Part F)**. `report_generator.generate_reports()`
assembles ensemble, convergence, and placement-comparison results into
one JSON and one Markdown report, fixing the strongest permitted
statement:

> "Real-DNS a-priori results show instantaneous consistency under the
> tested filtering, cutoff, and placement assumptions."

`data_is_real` must be asserted **explicitly** by the caller (default
`False`) — it is never inferred from whether an ensemble run "succeeded,"
because a fully synthetic run can look structurally valid. When not
marked real, the report carries a prominent data-provenance warning in
both the JSON and the Markdown.

**Forward-validation interface (Part G)**. `forward_validation_
interface.py` fixes the *shape* of Milestone 6 (a `ForwardSolver`
protocol: `initialize()` from a filtered DNS snapshot, `step()` by a
confirmed `Δt`, `compare_to_dns()` against kinetic-energy evolution,
`E(k)`, `T(k)`, `Π(k)`, vorticity statistics, structure functions,
terminal heat, backscatter, and controller evolution) without
implementing a solver — every method on `NotYetImplementedForwardSolver`
raises immediately. Do not begin controller retuning until real Milestone
5 a-priori placement results exist.

**Still blocked: real data (Part A).** As with Milestone 4, this
environment has no SciServer/Giverny access. Parts B–G above are real,
tested infrastructure — Part A (actually running 64³/128³/256³ tiers and
≥5 independent real snapshots on SciServer) has not been executed. No
report produced in this environment should ever be generated with
`data_is_real=True`.

## Milestone 5.5: SciServer execution package (2026-07-24)

Milestone 5 built the *analysis* infrastructure; this milestone builds
the *operational* infrastructure to actually run it on SciServer as one
reproducible command:

```bash
python run_real_validation.py \
  --manifest manifests/isotropic_128_validation.yaml \
  --output runs/isotropic_128_validation
```

**Manifest (`manifest.py`).** A single YAML file (see `manifests/
isotropic_128_validation.yaml` for the real-execution template) fully
describes a run: dataset, calibration/validation snapshots, resolution
tiers, terminal-layer requirements, preregistered placement parameters,
and the explicit `classification.data_is_real` flag. `load_manifest()`
validates strictly — any blank (`null`) physical value (a snapshot time,
`cutoff_nyquist_fraction`, `parent_band_c1`/`c2`, `data_is_real` itself)
is a hard `ManifestValidationError` listing every problem found, never a
silent default. `manifests/synthetic_dry_run.yaml` is the fully-filled,
`source: synthetic` counterpart used for local testing.

**Preflight (`preflight.py`), no data fetched.**
`python run_real_validation.py --manifest ... --output ... --preflight`
runs eleven checks — SciServer/Giverny importability, mounted turbulence
volume, authentication, dataset/snapshot accessibility, memory estimate
(`memory_estimate.py`, `M_peak ≈ (u_hat + grad + u + advective + N +
N_hat + N_hat_perp) × safety_factor`), disk estimate, predicted shell
count per resolution tier (computed from `terminal_layer` + geometry
alone, no data needed), calibration/validation separation, explicit
placement parameters, and the real-data assertion — before any cutout is
fetched. The SciServer/Giverny/mount/auth checks are only *blocking* when
a snapshot actually declares `source: sciserver`; a pure local/synthetic
manifest is never blocked by SciServer's absence.

**Data sources (`data_sources.py`).** The one non-bypassable safety rail:
`resolve_data_source()` refuses outright if `data_is_real: true` and a
snapshot's `source` is `synthetic` — checked once at preflight and again
at fetch time, so a real-data validation run cannot silently execute
against synthetic data because of a manifest typo.

**Run identity (`run_identity.py`).** Every run gets `run_id =
SHA256(manifest_hash + git_commit + declared provenance)`, plus a full
`run_identity.json`: git commit, dirty-tree status (reported, not folded
into the hash — a dirty tree can't be cheaply content-hashed, so it's
flagged as reproducibility-compromised instead of silently included),
manifest hash, package versions, Python version, hardware, start/end
time, SHA256 of every output file, and test-suite status. **Output
directories are immutable**: re-running the same manifest against the
same code is a no-op (`already completed`); a *different* run ID
targeting an existing directory is refused unless `--force`.

**Checkpointed, resumable execution.** The chain (calibration →
validation → selection → ensemble → identifiability → report) is
checkpointed at the stage level via `checkpoint.json` — `--resume`
continues from the last completed stage. Snapshots are processed one
fetch at a time (never all held in memory simultaneously) with `del` +
`gc.collect()` between stages.

**Acceptance test (`tests/test_run_real_validation.py`, 13 tests).**
Demonstrates all 10 required scenarios entirely with synthetic local
data: manifest validation, preflight failure without SciServer (only
when actually required), immutable run creation, interrupted-run
recovery, calibration/validation separation, placement conservation
failures surfaced as `status="blocked"` (never silently dropped),
synthetic-data report warning, real-data assertion requirement, output
hashing, and deterministic run-ID computation.

**Still blocked: real data.** As always — no SciServer/Giverny access in
this environment. This milestone makes the eventual real run a single
command; it does not, and cannot, execute that command here.

## Milestone 5.7: Forcing-Material-Size Stress Test of the Terminal-Layer Model (2026-07-29)

Every milestone through 5.5 tests the terminal operator a-priori or
finite-difference, against real (or intended-real) DNS snapshots, with
forcing appearing only as an unconfirmed wavenumber ceiling
(`Config.forcing_kmax`). Milestone 5.7 asks a different question: **does
the terminal operator remain valid when forcing changes the structure
faster or more strongly than the cascade?** It answers this with a fully
separate synthetic/theoretical framework -- it does not touch, alter, or
run against the real JHTDB campaign, its manifests, or `run_real_
validation.py`.

**This milestone required the first forward-in-time integrator in this
repo** (`pseudo_spectral_solver.py`). AGENTS.md's existing rule -- "do not
begin controller retuning until real Milestone 5 a-priori placement results
exist" -- was written about real-data forward validation (Milestone 6) and
is unaffected: this solver is synthetic-only by construction (there is no
code path that can accept real DNS input), conforms to the `ForwardSolver`
protocol from `forward_validation_interface.py` so a genuine Milestone 6
solver can reuse its call shape, and every report it produces carries a
non-optional synthetic-only warning. It does not begin real controller
retuning; it tests the previously dormant `Config.gp=24`/`gi=8` defaults as
a hypothesis (H7), for the first time actually reading them.

**New modules**: `forcing.py` (explicit forcing state `F = {P_f, k_f,
tau_f, d_f, C_f, B_f}`, 10 forcing types, `Phi_l`/`Theta_f`/`A_f`
diagnostics), `material_state.py` (5 material types; only incompressible
and high-viscosity Newtonian are `implemented`, everything else is
`material_interface_only`, never silently approximated), `pseudo_spectral_
solver.py` (ETD-Euler pseudo-spectral incompressible NS solver with
forcing injection, terminal-operator sink/return, hard-cutoff and
no-operator variants), `controller.py` (the first actual GP/GI PI
controller), `terminal_operator_forcing_aware.py` (the extended `gamma(q,
Phi_l, tau_f/tau_l, M, l/L, l/lc)` schema; the baseline wraps the original
operator unmodified; a CANDIDATE forcing-aware correction is implemented
and explicitly marked unvalidated), `energy_budget.py`, `structure_
metrics.py` (anisotropy tensor, directional spectra, strain statistics,
connected-component structure detection), `forcing_test_matrix.py` (14
preregistered forcing cases, 3 calibration / 11 validation, disjoint),
`stress_test_classification.py` (a non-binary, per-domain classification
vocabulary), `phase_maps.py`, `milestone_5_7_stress_test.py` (the
orchestrator: 6 comparison groups A-F), and `stress_test_report.py`.

**Comparison groups**: A original operator with fixed gains (GP=24,
GI=8); B original operator with gains retuned only on the 3 calibration
cases (a small preregistered gain grid, never touching validation cases);
C the forcing-aware CANDIDATE operator (unvalidated); D no terminal
operator; E hard spectral cutoff; F smooth damping with no backscatter
(`alpha_s=1.0`).

**Resolution tiers actually executed**: 32^3 (diagnostic-only, as
specified -- `compute_terminal_layer` degenerates to `ks=0` at this
resolution and grid, which additionally makes `estimate_tau_s` return
`inf`, silently zeroing gamma everywhere; `milestone_5_7_stress_test.py`
treats `layer.ks<=0` as an explicit resolution failure on top of the base
repo's shell-count check, specifically because of this), 64^3 (the
physical minimum tier -- properly resolves a beta-sourced terminal layer),
and one 128^3 diagnostic-pipeline spot-check (8 steps only -- confirms the
pipeline runs at this resolution but is far too short to support any
physical claim; the rest of the 128^3 tier is `status="no_data"`,
compute-limited in this environment, never fabricated). 189 total runs
executed across grid tiers, comparison groups, materials, and the full
14-case forcing matrix; results in `runs/milestone_5_7/`.

**Headline empirical finding**: every run where forcing was injected at or
above `k_s` (`forcing_overlap_terminal_layer`, `small_scale_forcing`; 12/12
runs across all 6 comparison groups at the 64^3 tier) was classified
`terminal_model_not_supported` + `forcing_overlap_invalidates_assumption`
-- H3 is directly and consistently confirmed within this synthetic test:
the original terminal operator's cascade-arrival assumption breaks exactly
where the specification predicted it would. Conversely, **H1 (weak-forcing
consistency) is verified at the operator level** (`test_h1_weak_forcing_
consistency_candidate_reduces_to_baseline`, `test_h1_weak_forcing_
candidate_and_baseline_nearly_identical` -- the candidate operator reduces
to the baseline to machine precision as `Phi_l -> 0`) **but was not
empirically exercised by this campaign's full-solver runs**: with the
preregistered power/viscosity/timescale presets used, every completed run
measured `Phi_l` in the `forcing_dominated` regime (even the case named
`weak_isotropic`) -- a short synthetic spin-up at low Reynolds number
simply never reached a state where the nonlinear cascade dominates the
chosen forcing power. This is a genuine limitation of the executed
campaign's parameter choices, not of the model or the diagnostic, and is
recorded as an unresolved question rather than smoothed over.

See `runs/milestone_5_7/milestone5_7_report.md` for the full applicability
map, per-run classification, and the complete supported / not-supported
statement lists (mirroring `report_generator.py`'s discipline for
Milestone 5). To extend the campaign: `run_milestone_5_7_chunk.py --grid-n
N --group G --cases ...` writes one JSON shard per invocation (kept small
deliberately so each run fits this environment's per-command time budget);
`assemble_milestone_5_7_report.py` merges however many shards exist into
the final report -- it does not require every cell of the matrix to be
filled, and reports any requested-but-unexecuted grid tier as `no_data`.

## Milestone 5.7a: Audit and Repair of the Forcing-Material-Size Stress Test (2026-07-29)

A detailed technical critique of the Milestone 5.7 report above identified
10 confirmed problems (the weak-forcing limit was never actually reached;
the energy-budget "conserves energy" claim contradicted its own 128^3
metrics; the 189-run count included 3 undetected stale-shard duplicates;
two forcing cases were literal duplicate definitions; the forcing-amplitude
clip's effect was unmeasured; `controller_stable` conflated bounded with
effective; the anisotropy detector had no statistical control baseline (and
a separate sign bug); 32^3 rows were mixed into k_f/k_s conclusions despite
a `ks=0` degeneracy; material dependence beyond Newtonian liquids remains
untested). Of those 10, **9 were genuine implementation/reporting defects,
now repaired and verified**; the 10th (material dependence) was correctly
identified as a scope limitation, not a bug -- no material code was added,
per the audit's explicit instruction. A second review of this audit's
first-generated report found 7 further report-level problems (a clip-effect
summary that undersold two materially-altered 128^3 spot checks; a
strongest-permitted-statement that cited those same clip-altered,
non-closing 128^3 results as if confirmatory; an overly permissive
`candidate_behavior_observed` scientific-status bucket that 17/19 rows fell
into, including baseline runs that never touched the candidate operator; no
visibility into the fact that most runs' richer controller classification
reduces to "merely bounded"; no separate accounting for energy-budget
closure vs. spectral pile-up, which are different questions; and an
anisotropy claim that needed to be stated as demonstration-level, not
statistical validation) -- all fixed at report-generation time, without
rerunning the solver, in the current report.

Milestone 5.7a audited and repaired the underlying infrastructure -- it
added **no new physical claims, materials, or candidate terminal laws** --
then reran a minimal, corrected 64^3 matrix (19 rows: warm-started
Phi_l-targeted cases, timescale-targeted cases, the near-k_s/overlap cases,
D-F baselines, an isotropic-control ensemble, and two 128^3 spot checks).

Every root cause, fix, and piece of verification evidence (fingerprint
collision checks, isotropic-control significance tests, the H1
candidate-vs-baseline agreement measurement, the corrected dedup of the
original 189-row campaign to 186, the corrected minimal-matrix rerun, the
orthogonal `spectral_status` pile-up classification, and the controller-label
distribution) is in `runs/milestone_5_7a/milestone5_7a_audit_report.md` (and
`.json`), generated by `generate_milestone_5_7a_audit_report.py`. The
robust, resolved-tier finding is: **the 64^3 test shows forcing at or above
k_s violates the cascade-arrival assumption** -- the 128^3 overlap spot
check is consistent with this but is explicitly NOT independent
confirmation (it did not close its energy budget and was materially altered
by the forcing-amplitude clip). See `AGENTS.md`'s "Milestone 5.7a" section
for the durable coding rules this audit produced (e.g.
`summarize_energy_budget()` now requires `dt`; use
`SolverConfig.initial_kinetic_energy` to reach `Phi_l<<1`; dedup shards by
`run_id`; `scientific_status` can never assign a candidate finding to a
non-candidate/group-A run; the legacy `controller_stable` label is
deprecated in favor of `controller_labels`). The original `runs/milestone_5_7/`
artifacts are left in place unmodified for the audit trail; the
dedup-corrected recount of that same campaign (186 rows) is at
`runs/milestone_5_7a/original_campaign_dedup_corrected/`.

## Scientific safeguards

- Frame-to-frame shell-energy changes (`measure_transfer.py`,
  `compare_model_to_dns.py`) are **finite-difference energy-evolution
  measurements**, not an isolated nonlinear-cascade transfer, unless
  forcing, viscosity, pressure, and filtering contributions have been
  separated out. Both label their output this way.
- The genuine nonlinear spectral-transfer (flux) calculation
  (`nonlinear_transfer.py`) requires velocity derivatives and is now
  implemented — prefer it over the finite-difference approximation when
  making any claim about cascade behavior specifically.
- Never tune model constants (`beta`, `alpha_s`, `n_shape`, `m_shape`, `gp`,
  `gi`) using the same snapshot(s) later reported as an independent
  validation result. `Config.calibration_snapshots` and
  `Config.validation_snapshots` are enforced disjoint by
  `assert_snapshot_separation()` — populate both explicitly and keep them
  non-overlapping.
- Do not classify a run as physically supportive merely because energy is
  conserved or the cutoff is enforced — those are necessary preconditions
  checked at every rung of `run_classification.py`, not evidence the
  theory is correct.

See `AGENTS.md` for the durable version of these rules aimed at future
coding-agent sessions on this repo.
