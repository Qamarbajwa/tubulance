# Agent guardrails for this repo

This project validates a "terminal-layer" sub-filter turbulence model
against real JHTDB data. It is a real physics experiment, not a demo — the
following rules exist because getting them wrong produces numbers that look
like results but aren't. Follow them before adding new theory, new
benchmarks, or new data sources.

## Never guess physical constants or time units

If a quantity (a viscosity, a forcing wavenumber, a frame-to-frame `Δt`,
a dataset's units) is not confirmed against official JHTDB/Giverny
documentation or a live query's returned metadata, do not fill it in with a
plausible-looking number. Leave it as an explicit, unset config field and
make the code fail clearly (raise, or produce a clearly-labeled "unavailable"
output) rather than silently produce a number that looks physical but isn't.
See `measure_transfer.TimeCoordinate.dt_confirmed` and
`Config.forcing_kmax` for the existing pattern: `None`/unconfirmed by
default, checked explicitly, never assumed.

**Why:** a previous session correctly refused to guess
`isotropic1024coarse`'s frame interval rather than fabricate a `seconds_per_frame`
value — that discipline is intentional, not an oversight to "helpfully" fix.

## Never mix synthetic and real data silently

`fetch_velocity_cutout()` must only return real JHTDB velocity (via the
live Giverny call or a cached local HDF5 export). Synthetic velocity fields
are fine in `tests/` for code-correctness checks, but must never be
substituted for real data in a script whose output is meant to say
something about the model's physics.

## Terminal layer width is resolution-aware, not a fixed `beta`

`beta = ks/kc` is a preference, not a spec. Two runs can share the same
`beta` while representing the terminal layer with radically different
numbers of independent shells
(`N_T = (kc - ks) / delta_k`, `delta_k = 2*pi/domain_length`). Always derive
the actual layer through `compute_terminal_layer()` and gate physical
claims through `validate_terminal_layer()` — don't reintroduce a bare
`ks = beta * kc` in new scripts. Minimums: `N_T >= 6` required, `>= 8`
preferred (`Config.min_terminal_shells` / `preferred_terminal_shells`).

## Label finite-difference results honestly

`E(k, t2) - E(k, t1)` (or that divided by a confirmed `Δt`) is a
finite-difference energy-evolution measurement. It bundles resolved-resolved
transfer, resolved/unresolved (subfilter) transfer, forcing, viscosity, and
pressure effects over the interval. Do not describe it as "the nonlinear
cascade" or "the subgrid transfer" in isolation — say what it actually is.
`nonlinear_transfer.py` computes the *true* instantaneous nonlinear
transfer `T(k)` from a single snapshot (no `Δt` needed) — prefer it over
the finite-difference approximation whenever the claim is specifically
about cascade/transfer behavior, and use `verify_global_conservation()` to
sanity-check any new field/resolution/dealias combination before trusting
its output.

## Run classification is a ladder, not a vibe

Every real-data run should be classified via `run_classification.
classify_run()`: `blocked` → `pipeline_only` → `apriori_operator_valid` →
`finite_difference_comparison_valid` → `nonlinear_transfer_comparison_
valid` → `forward_validation_required`. Reaching a rung only means the
corresponding calculation ran validly (adequate resolution, conserved
transfer, etc.) — it does NOT mean the model matches DNS. Use
`positive_result_bar()` to check the specific "first real positive result"
criteria before calling anything "consistent with the theory," and even
then the correct word is **a-priori consistency**, never "validated" —
full validation requires a forward-in-time run, which does not exist yet.

## Removal and return are not the same thing as "the model's transfer"

The terminal operator's `gamma(k)*E(k)` is the *total* removal from shell
`k`, split into a heat fraction (a genuine kinetic-energy sink) and a
return/backscatter fraction (redistributed, not destroyed). Never compare
DNS `T(k)` against the bare removal `-gamma(k)*E(k)` and call it "the
model's transfer" — that penalizes the model for energy it intentionally
returns elsewhere. The complete predicted transfer is
`T_model(k) = T_remove(k) + T_return(k)`.

## Backscatter placement is a set of preregistered hypotheses, not a solved problem

`T_return(k)`'s spectral *placement* (which shell receives the returned
energy) is not specified by the theory beyond the aggregate heat/return
split. `backscatter_placement.py` implements four candidates
(`local_cancellation`, `parent_band_energy_weighted`, `turnover_weighted`,
`dns_oracle_diagnostic`), all **preregistered**: their functional form is
fixed in code before being run against real data, so a later "best fit"
can't be mistaken for a physical discovery.

- `local_cancellation` is the algebraic control case (reduced effective
  damping), not a claim about inverse cascade.
- `parent_band_energy_weighted` requires `Config.parent_band_c1`/`c2` to
  be set explicitly — there is no default. Don't add one; the absence is
  what makes it preregistered rather than tunable-after-the-fact.
- `dns_oracle_diagnostic` uses real DNS transfer to place the model's
  return. It is **diagnostic only** — never report it as, or alongside, a
  predictive-performance claim, and never let it participate in
  `select_placement()`'s winner selection (it's already excluded from
  `DEPLOYABLE_PLACEMENTS` for this reason — don't remove that exclusion).
- Don't add a new placement value without a real basis for where the
  energy actually goes, and don't select a "winning" placement using the
  same snapshots later reported as validation — see
  `placement_comparison.select_placement()` (calibration only) vs.
  `run_validation_comparison()` (disjoint validation set).
- A metric restricted to `terminal_region` cannot discriminate the three
  below-`ks` placements from each other or from plain removal — see the
  structural note in `placement_comparison.py`'s `_METRIC_GETTERS`
  docstring before adding a new selection metric.
- `identifiability_report()` can honestly return
  `backscatter_placement_not_identifiable`. That is a valid, expected
  result when placement-induced spread doesn't exceed snapshot-to-snapshot
  variability — don't treat it as a failure to work around, and don't
  overinterpret small score differences as a discovery.

## Don't set a threshold before seeing the distribution

When a criterion needs a numerical severity threshold (e.g. "no severe
bottleneck") and no real-data distribution has been observed yet, report
the distribution (see `snapshot_ensemble.dataset_level_classification()`'s
`bottleneck_ratio_distribution`) rather than inventing a cutoff. This is
the same discipline as not guessing physical constants, applied to
statistical/classification thresholds instead of physical values.

## Keep calibration and validation snapshots disjoint

If model constants (`beta`, `alpha_s`, `n_shape`, `m_shape`, `gp`, `gi`) are
ever tuned against a snapshot, that snapshot cannot also be reported as an
independent validation result. Register snapshots in
`Config.calibration_snapshots` / `Config.validation_snapshots` and call
`assert_snapshot_separation(cfg)` (already wired into
`jhtdb_terminal_benchmark.main()`) before treating a run as validation.

## Two open blockers (see README.md "Open validation blockers")

1. **Real spatial resolution** — only 16³ local cutouts exist as of
   2026-07-24; a meaningful physical test needs 128³+ via SciServer/Giverny.
   `convergence_table.py` is the scaffold for testing this across grid
   sizes once real data exists at each tier — do not fill in a missing
   tier's row with fabricated data; leave it `status="no_data"`.
2. **Confirmed temporal separation** — no confirmed `Δt` for
   `isotropic1024coarse` frames exists in this project yet. Don't add one
   without a citable source recorded in the relevant `TimeCoordinate`. Note
   this blocker does NOT apply to `nonlinear_transfer.py` /
   `nonlinear_transfer_validation.py` — true transfer `T(k)` is
   instantaneous and needs only one snapshot.

Until both are resolved, treat any run of `jhtdb_terminal_benchmark.py`,
`compare_model_to_dns.py`, or `nonlinear_transfer_validation.py` against
the local 16³ files as pipeline validation only (they all raise or report
`blocked`/`pipeline_only` against it) — never as support for or against the
terminal-layer theory. This also blocks `snapshot_ensemble.py`'s
≥5-independent-snapshot requirement, `convergence_table.py`'s 64³/128³/
256³ tiers, and `placement_comparison.py`'s calibration/validation
placement study — that infrastructure exists and is tested with synthetic
data for code correctness, but has not actually been run against real
high-resolution JHTDB data as of 2026-07-24 (no SciServer/Giverny access
in this environment). Don't present a synthetic-data ensemble/convergence/
placement run as if it were real validation, and never call
`report_generator.generate_reports(..., data_is_real=True)` on synthetic
output.

## Record real run provenance, don't infer it

`run_metadata.py`'s `build_run_metadata()` is the standard place to record
what a real run actually fetched (dataset, spatial origin, cube size,
stride, time coordinate) alongside the derived geometry (`kc`, `ks`,
`delta_k`, `N_T`, Nyquist/forcing separation) and resource use. Pull
spatial origin from the actual fetch source (e.g.
`spatial_origin_from_local_h5()` reads real HDF5 attrs) — never from
`Config.start_xyz`/`size_xyz`/`stride_xyz` defaults, which the local-file
fetch path doesn't use at all and would misrepresent what was actually
pulled. Fields that can't be determined are reported as an explicit "not
recorded" note, never silently omitted or defaulted.

## Forward validation is Milestone 6, not now

`forward_validation_interface.py` fixes the *shape* of the eventual
forward-in-time solver (`ForwardSolver` protocol) without implementing
it — `NotYetImplementedForwardSolver` raises on every method by design.
Do not implement a real forward integrator, and do not begin controller
(`gp`/`gi`/`C_gamma`) retuning, until real Milestone 5 a-priori placement
results exist. Every milestone through 5 is a-priori (instantaneous or
finite-difference); only a genuine forward run initialized from
`u_bar_DNS(t0)` and compared against DNS at `t0 + n*dt` can support a
predictive-accuracy claim.

## Manifests are the only sanctioned way to configure a real run

`run_real_validation.py` reads a YAML manifest (`manifest.py`) rather
than accepting scattered CLI flags for physical values. Never add a
"just fill in a default" fallback to `load_manifest()` — a blank
physical value (a snapshot time, `cutoff_nyquist_fraction`,
`parent_band_c1`/`c2`, `classification.data_is_real`) must raise
`ManifestValidationError`, listing every problem found. This is the same
"never guess physical constants" discipline expressed as manifest
validation rather than a `Config` default.

## Preflight before fetch, always

`run_real_validation.py --preflight` must remain able to run every check
except a genuinely live SciServer/Giverny query without fetching any
data. If you add a new preflight check that requires data, gate it behind
the checks that establish SciServer availability first — never let a
preflight run silently attempt a real fetch. The SciServer/Giverny/mount/
auth checks are blocking only when a manifest snapshot declares
`source: sciserver`; don't make them unconditionally blocking, or every
local/synthetic dry run breaks for no reason.

## Real-data assertion is enforced at the data layer, not just reporting

`data_sources.resolve_data_source()` refuses to build a fetch callable
when `data_is_real=true` and a snapshot's `source` is `synthetic` --
this check exists independently of (and in addition to)
`report_generator`'s data-provenance warning. If you add a new data
source type, it must go through `resolve_data_source()`, not bypass it,
or the safety rail silently stops applying to it.

## Run outputs are immutable; don't "just fix" a stale run in place

`run_identity.py` computes a deterministic `run_id` from the manifest
hash and git commit. `run_real_validation.py` refuses to let a different
run overwrite an existing output directory without `--force`. If a run
needs to change, that means the manifest or the code changed -- point it
at a new `--output` directory (or use `--force` deliberately, the same
way `git push --force` is deliberate) rather than editing files inside an
existing run's output directory by hand. Checkpointed stages
(`checkpoint.json`) assume their corresponding stage output file was
written before the checkpoint entry -- don't reorder "write result" and
"mark stage done" in `run_real_validation.run()`.

## Milestone 5.7's forward solver is synthetic-only, permanently

`pseudo_spectral_solver.py` is the first forward-in-time integrator in
this repo. It exists solely for the Milestone 5.7 forcing/material/size
stress test and has no code path that accepts real DNS input -- do not add
one. The earlier rule "do not begin controller retuning until real
Milestone 5 a-priori placement results exist" was about real-data forward
validation (Milestone 6, still not implemented -- see
`forward_validation_interface.py`); it does not authorize turning this
synthetic solver into, or substituting it for, that real solver. If a
genuine Milestone 6 forward solver is built later, implement it as a new
class satisfying the same `ForwardSolver` protocol -- do not repurpose
`SyntheticForwardSolver` or relax its refusal to accept real DNS.

## GP=24/GI=8 are a tested hypothesis, not tuned constants

`controller.py` is the first code that actually reads `Config.gp`/`gi`
(dormant defaults since Milestone 1). Per H7 in the Milestone 5.7
specification, treat any controller gain pair as a hypothesis to test, not
a fact to assume. Comparison group B's calibration-only retune (see
`milestone_5_7_stress_test.tune_controller_gains`) is a small preregistered
grid search (`GAIN_TUNING_GRID`) -- do not add new candidate gains to that
grid after seeing validation-set results; a "retune" that used the
validation cases would violate the same calibration/validation separation
`assert_case_separation()` exists to enforce.

## The forcing-aware candidate operator is explicitly unvalidated

`terminal_operator_forcing_aware.gamma_candidate_forcing_aware` is marked
`IS_CANDIDATE_MODEL = True` for a reason: it is comparison group C, not a
replacement for the baseline operator (`gamma_baseline`, used unmodified by
groups A/B/F). Its only structural requirement is H1 (collapses exactly to
baseline as `Phi_l -> 0`, enforced by
`tests/test_terminal_operator_forcing_aware.py`). Do not report its output
as, or alongside, a validated improvement -- see `stress_test_report.
NOT_SUPPORTED_STATEMENTS`.

## Material interface_only is not "approximately Newtonian"

`material_state.py` declares 5 materials; only `incompressible_newtonian_
liquid` and `high_viscosity_newtonian_liquid` are `implemented=True` (the
latter is the same solver at higher `viscosity`, not a new code path). The
other three are `material_interface_only` -- `MaterialState.require_
implemented()` raises rather than letting a caller silently run them
through the Newtonian solver. If a real constitutive law is added for one
of them later, flip its `implemented` flag in the registry; don't work
around the check.

## Milestone 5.7's resolution degeneracy: ks=0 zeroes gamma silently

At `grid_n=32` with this solver's default `cutoff_fraction=0.5` and
`beta=0.56`, `compute_terminal_layer` falls back to `ks=0` (too few shells
for the beta-derived layer), and `estimate_tau_s` at `ks=0` returns `inf`
(the entry-shell energy is exactly zero -- the `k=0` mode is removed by the
divergence-free projection) -- which makes `gamma` identically zero
everywhere without raising. `milestone_5_7_stress_test.run_one` treats
`layer.ks <= 0` as an explicit resolution failure on top of `validate_
terminal_layer`'s shell-count check specifically because of this; if you
write a new script that calls `terminal_operator`/`estimate_tau_s`
directly at low resolution, add the same `ks > 0` guard rather than trusting
`validate_terminal_layer` alone to catch it.

## Milestone 5.7 campaign shards, not one long run

`run_milestone_5_7_chunk.py` writes one JSON shard per invocation
deliberately -- this environment's command layer caps a single command at
~45s wall-clock, and a 64^3 run costs roughly 0.25s/step, so a full 14-case
comparison-group sweep does not fit in one call. `assemble_milestone_5_7_
report.py` merges whatever shards exist; it does not require full
coverage and reports ungenerated grid tiers as `no_data`. Don't try to
collapse the campaign back into one long-running script -- it will simply
be killed partway through with no output, unlike the shard approach.

## Milestone 5.7a: the original 189-run campaign had 10 confirmed problems (9 defects + 1 scope limitation) -- audited and repaired, not rerun wholesale

The original Milestone 5.7 report overclaimed in several places: the
weak-forcing limit (Phi_l<<1) was never actually reached (cold-start bias),
the energy-budget closure metric omitted dK/dt and produced nonsensical
"doesn't close" verdicts during normal spin-up transients, two forcing
cases were literal duplicate definitions, `n_runs=189` included 3 genuine
stale-shard duplicate rows the assembler never deduplicated, the anisotropy
detector had no isotropic-control baseline (and a separate sign bug made
its magnitude always exactly 0), and `controller_stable` conflated
"bounded" with "effective." 9 of these 10 were genuine code/reporting
defects, now repaired; the 10th (material dependence untested beyond
Newtonian liquids) was confirmed as a scope limitation, not a bug -- no
material code was added or attempted. A second-pass review of the audit
report ITSELF (not the solver) then found and fixed 7 more problems: an
understated clip-effect summary, a strongest-permitted-statement that cited
clip-altered non-closing 128^3 results as confirmatory, an overly
permissive `candidate_behavior_observed` status that 17/19 rows fell into
(including baseline runs that never touched the candidate operator), no
visibility into controller-label distribution, no separate spectral
pile-up status, and an anisotropy claim that needed "demonstration-level"
framing. All root causes, fixes, and verification evidence (both passes)
are in `runs/milestone_5_7a/milestone5_7a_audit_report.md` (and `.json`).
Key fixes if you touch this code again:
- `energy_budget.summarize_energy_budget()` now REQUIRES `dt` as a keyword
  argument and normalizes by `max(mean_power_input, mean_viscous+heat)`,
  not `mean_power_input` alone -- see that module's docstring before
  "fixing" the closure metric again.
- `SolverConfig.initial_kinetic_energy` (warm-start) is how you reach
  Phi_l<<1 in this solver -- a cold start cannot, by construction, produce
  a small Phi_l for any nonzero forcing power.
- `forcing_test_matrix.py`'s general-purpose cases use
  `k_f_mode="moderate_below_ks"`; only `forcing_far_below_ks` uses
  `"far_below_ks"`. Check `forcing_fingerprint.assert_no_unexpected_
  collisions()` before adding a new case, so a duplicate config fails loud
  instead of producing silently-identical diagnostics again.
- Every run now carries a deterministic `run_id`
  (`milestone_5_7_stress_test.compute_run_identity`); shard assemblers
  should dedup on it (`assemble_milestone_5_7_report.py --dedup`, default
  on) rather than trusting "one row per shard file."
- Anisotropy significance should go through
  `structure_metrics.is_anisotropic_response_significant()` against an
  `isotropic_control_baseline()`, not a bare `anisotropy_magnitude >
  threshold` check -- and even then, treat it as demonstration-level with
  a 2-seed baseline, not statistical validation.
- 32^3 remains diagnostic-only (`ks=0`) and must be excluded from any
  k_f/k_s-based conclusion; 128^3 in the 5.7a rerun is a 4-step SPOT CHECK
  (2 cases) only, not a resolution-convergence claim -- and BOTH of those
  128^3 spot checks were materially altered by the forcing-amplitude clip,
  so they cannot serve as independent confirmation of anything, only as
  "consistent with" a resolved-tier (64^3) finding.
- `stress_test_classification.compute_audited_status()`'s `scientific_status`
  can never assign a candidate-operator finding (`candidate_limit_
  consistency_observed` / `candidate_improvement_not_testable`) to a run
  outside comparison group C, and never asserts "candidate improvement" at
  all -- there is no real-data ground truth anywhere in this synthetic
  milestone to judge improvement against. It also now has an orthogonal
  `spectral_status` (pile-up) dimension: a run can close its energy budget
  while persistently piling up energy above the cutoff, and that is NOT
  terminal-model support -- check both before citing a run as supportive.
- The legacy `classification_labels` entry `controller_stable` only ever
  meant "bounded," and predates the richer `controller_labels` tuple
  (`controller.classify_controller_run`) -- treat `controller_stable` as
  deprecated; `controller_labels` is authoritative for any effectiveness
  claim (converged / target_achieved / budget_error_reduced).

## Workflow context

Theories are developed in conversations outside this repo and brought here
once testable. Expect iterative additions — new parameters, new pass/fail
checks, new operators — as they arrive. When a new theoretical rule shows up
without full derivation, ask for the specific claim/hypothesis rather than
guessing what it implies for the code.
