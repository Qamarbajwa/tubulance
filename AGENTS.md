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

## Workflow context

Theories are developed in conversations outside this repo and brought here
once testable. Expect iterative additions — new parameters, new pass/fail
checks, new operators — as they arrive. When a new theoretical rule shows up
without full derivation, ask for the specific claim/hypothesis rather than
guessing what it implies for the code.
