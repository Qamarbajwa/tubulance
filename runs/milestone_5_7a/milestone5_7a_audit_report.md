# Milestone 5.7a audit report: Audit and Repair of the Forcing-Material-Size Stress Test

> **WARNING:** SYNTHETIC-ONLY REPORT -- every number below comes from the Milestone 5.7/5.7a synthetic pseudo-spectral stress-test solver (pseudo_spectral_solver.py), not from real JHTDB DNS data. This is evidence about the MODEL'S CODE AND ASSUMPTIONS, not about real turbulence. It must never be cited alongside or in place of the real JHTDB validation campaign (jhtdb_terminal_benchmark.py / run_real_validation.py). Milestone 5.7a changed NO real-data code path: it only audits and repairs the synthetic 5.7 stress-test infrastructure.

**Summary:** 9 implementation/reporting defects were repaired and verified; 1 item (material dependence) was confirmed as a scope limitation, not a bug -- see each audit item's `category` field.

## Scope constraints honored
- No new physical claims, material models, or candidate terminal laws were added.
- gamma_candidate_forcing_aware's functional form is unchanged from Milestone 5.7.
- The real JHTDB manifest and real-validation pipeline were not touched.
- Nothing has been committed until this report and its corrections were reviewed.

## Revised strongest permitted statement

> In the audited synthetic 64^3 stress-test domain, the forcing-aware candidate is verified to reduce to the original terminal operator in a measured weak-forcing case with Phi_l~=0.047, as required by its construction. The corrected benchmark reaches nonlinear-dominated, competing, and forcing-dominated regimes, and its complete energy budget closes within the configured tolerance for 18 of 19 minimal-matrix runs. A resolved 64^3 test shows that direct forcing at or above k_s violates the original model's cascade-arrival assumption. This result identifies an applicability boundary of the model's assumptions, not validation against real turbulence. The 128^3 results remain short, clip-altered spot checks and provide no convergence evidence. Material-dependent physics remains untested beyond Newtonian viscosity variation.

## Boundary finding: which resolution tier actually supports the cascade-arrival result
> The 64^3 resolved synthetic test challenges the cascade-arrival assumption.

- **Basis:** overlap_64_A (grid_n=64, not clip-altered, energy budget closes within tolerance) is classified assumption_challenged: forcing placed at/above k_s directly and measurably breaks the original terminal operator's cascade-arrival assumption at a resolved tier.
- **128^3 caveat:** overlap_128_spotcheck is consistent with this finding (same qualitative classification) but is NOT independent confirmation: it is a 4-step spot check, its energy budget does not close within tolerance, and it was materially altered by the forcing-amplitude clip. It should be cited as consistent, never as corroborating evidence on its own.

## Audit items: critique -> root cause -> fix -> verification

### Item 1 [defect_repaired]: Weak-forcing limit (Phi_l<<1) was never actually tested -- all runs measured forcing_dominated.
- **Root cause:** Cold-start bias: the solver always initialized velocity from a small-amplitude random field, so u_l started near zero and Phi_l = P_f/(u_l^3/l) was enormous at t=0 for ANY nonzero forcing power, regardless of preregistered intent.
- **Fix:** Added SolverConfig.initial_kinetic_energy (warm-start knob) and forcing.initial_kinetic_energy_for_target_phi_l() which inverts Phi_l for the u_l needed to hit a target ratio at t=0. initialize_state() rescales the random field to match.
- **Files changed:** forcing.py, pseudo_spectral_solver.py
- **Verification:** weak_64_A measured Phi_l=0.047 (nonlinear_dominated), competing_64_A measured Phi_l~1.4 (competing), strong_64_A measured Phi_l~9-50 range (forcing_dominated) -- see minimal_matrix_rows below. All three preregistered regime bins are now empirically reached.

### Item 2 [defect_repaired]: Energy-budget "conserves energy" claim contradicted the actual metrics (128^3 run: relative_closure_error~=0.98, closes_within_tolerance=false).
- **Root cause:** relative_closure_error compared mean(power_input) against mean(viscous_dissipation+terminal_heat) ALONE, omitting dK/dt entirely -- invalid during any spin-up/decay transient where most power legitimately goes into changing KE, not into dissipation.
- **Fix:** Derived relative_closure_error from full_timestep_residual (already includes dK/dt via _step_once's dk_measured/dk_predicted bookkeeping), converted to a rate (/dt), and normalized by max(mean_power_input, mean_viscous+heat) instead of mean_power_input alone (a warm-start decay run has power_input far smaller than viscous dissipation, so normalizing by power_input alone inflates a small residual into a huge relative error). summarize_energy_budget() now requires dt as a keyword argument. Old (invalid) metric kept as input_vs_dissipation_only_gap for transparency only.
- **Files changed:** energy_budget.py, pseudo_spectral_solver.py
- **Verification:** Same weak_isotropic/grid64/initial_kinetic_energy=5.0 configuration: closure error dropped from 263.9/false (bug) to 0.079/true (fixed metric) in direct comparison during development; 18 of 19 minimal-matrix rows now report closes_within_tolerance=true -- the sole exception (overlap_128_spotcheck, a 4-step 128^3 spot check of the forcing-overlaps-terminal-layer case, relative_closure_error=0.259) is a large transient over very few steps AND was independently materially altered by the forcing-amplitude clip (see item 6 / forcing_clip_summary) -- it is not read as a resolution-convergence result either way (see item 3 / boundary_finding).

### Item 3 [defect_repaired]: 128^3 execution status was self-contradictory (spot check misrepresented as tier completion).
- **Root cause:** stress_test_report.py's grid_tiers_executed / grid_tiers_skipped_no_data distinction is binary (executed vs no_data) with no third state for 'a single spot-check row exists, this is not a resolution-convergence claim.'
- **Fix:** Added is_spot_check flag threaded from run_milestone_5_7a_minimal_matrix.py's CASE_SPECS through to each shard row, plus AuditedStatus.resolution_status (resolved/diagnostic_tier_only/not_executed) as an orthogonal field. This audit report's tier_status section explicitly separates spot_check_executed from complete_campaign_executed per tier -- see below.
- **Files changed:** stress_test_classification.py, milestone_5_7_stress_test.py, run_milestone_5_7a_minimal_matrix.py, generate_milestone_5_7a_audit_report.py
- **Verification:** tier_status.128 below reports spot_check_executed=true, complete_campaign_executed=false, n_spot_check_rows=2, explicitly. See also boundary_finding: the robust cascade-arrival-assumption result comes from the RESOLVED 64^3 overlap test; the 128^3 overlap spot check is consistent with it but is not independent confirmation (it was also clip-altered -- see item 6).

### Item 4 [defect_repaired]: n_runs=189 vs n_runs_expected=84 was unexplained/suspicious.
- **Root cause:** n_runs_expected=84 was a hardcoded default representing ONLY the single-grid-tier, single-material count (14 cases x 6 groups). The actual 189-row campaign spanned 2 grid tiers x 6 groups x incompressible_newtonian_liquid (168 rows) + 1 grid128 spot check + a high_viscosity_newtonian_liquid grid32/group-A pass (14 rows) + 3 one-off material_not_implemented placeholder probes (3 rows) = 186 legitimate rows, PLUS 3 genuine stale-shard duplicate rows (g32_A_highvisc_actual.json reran 3 of the same 14 cases already present in g32_A_highvisc.json, and assemble_milestone_5_7_report.py had no dedup logic) = 189.
- **Fix:** Added compute_run_identity() (SHA256 of all outcome-determining fields, excluding RNG phase) threaded into every row as run_id. assemble_milestone_5_7_report.py now dedups by run_id (falling back to (case,grid_n,group,material,forcing_type) for legacy rows without run_id) and reports what was dropped.
- **Files changed:** milestone_5_7_stress_test.py, assemble_milestone_5_7_report.py
- **Verification:** Rerunning the dedup-enabled assembler against the ORIGINAL 35 shard files: loaded 189 rows, dropped exactly 3 duplicates (weak_isotropic/moderate_steady_isotropic/strong_isotropic, all grid_n=32/group=A/material=high_viscosity_newtonian_liquid), 186 rows remain -- output at runs/milestone_5_7a/original_campaign_dedup_corrected/.

### Item 5 [defect_repaired]: Several nominally distinct forcing cases produced bit-identical diagnostics.
- **Root cause:** moderate_steady_isotropic and forcing_far_below_ks were literal duplicate case definitions (identical forcing_type/power/k_f_mode='far_below_ks'/tau_f) in forcing_test_matrix.py -- a genuine matrix-design bug, confirmed by direct inspection of the original report's raw values (phi=449.852..., theta=0.01412..., identical to many decimal places for both cases at grid32).
- **Fix:** Gave general-purpose cases their own k_f_mode='moderate_below_ks' (0.6*ks), reserving 'far_below_ks' (0.3*ks) exclusively for the case that specifically tests scale separation (forcing_far_below_ks). Added forcing_fingerprint.py to hash every case's RESOLVED configuration and hard-fail (assert_no_unexpected_collisions) on any future unexpected collision.
- **Files changed:** forcing_test_matrix.py, forcing_fingerprint.py
- **Verification:** detect_forcing_collisions() over ALL_CASES: 0 collision groups at grid_n=64 and grid_n=128 (the fix is confirmed effective at both resolutions used in the minimal-matrix rerun); exactly 1 collision group remains at grid_n=32 (moderate_steady_isotropic vs forcing_far_below_ks), which is the SEPARATE, DOCUMENTED, unavoidable ks=0 degeneracy described in item 9 below, not a residual matrix bug -- see fingerprint_collisions section.

### Item 6 [defect_repaired]: The forcing-amplitude safety clip was suspected of controlling the experiment.
- **Root cause:** pseudo_spectral_solver.make_forcing_hat applies a lam_max safety clip to the requested forcing amplitude but the original code never recorded whether the clip fired or by how much -- there was no way to check the suspicion either way.
- **Fix:** make_forcing_hat now returns (total, new_shapes, clip_diagnostics) with requested_amplitude/applied_amplitude/clip_active per injection scale. EnergyBudgetSample carries these per step; summarize_energy_budget computes forcing_clip_active_fraction and forcing_clip_materially_altered_case (fires only if clip_active_fraction>0.1 AND amplitude_alteration>0.1).
- **Files changed:** pseudo_spectral_solver.py, energy_budget.py
- **Verification:** 17 of 19 minimal-matrix cases were NOT materially altered by clipping. The 2 that WERE (weak_128_spotcheck, overlap_128_spotcheck) are BOTH 128^3 spot checks -- neither can be interpreted as a faithful test of its nominal requested forcing, and this is now stated explicitly wherever those two rows are cited (see forcing_clip_summary, tier_status.128, boundary_finding).

### Item 7 [defect_repaired]: "controller_stable" was too weak a classification (conflates bounded with effective).
- **Root cause:** controller.controller_diagnostics()['is_stable'] only checked boundedness (|trajectory|<1e6), which the original classification pipeline mapped directly to a single label 'controller_stable' -- a controller that is bounded but oscillating, never converging, or never reducing the actual energy-budget error would still be called 'stable.'
- **Fix:** Added ControllerClassificationThresholds and classify_controller_run(), returning an orthogonal tuple of labels from {controller_bounded, controller_nonoscillatory, controller_converged, controller_target_achieved, controller_budget_error_reduced, controller_unstable} instead of one flat label.
- **Files changed:** controller.py, milestone_5_7_stress_test.py
- **Verification:** See controller_label_distribution below: 19/19 rows get controller_bounded, but only 2/19 (weak_64_D, weak_64_E) also get controller_converged, and NO row gets controller_target_achieved or controller_budget_error_reduced in this minimal matrix -- i.e. the richer labels show the controller is mostly only shown to be bounded, not effective. The legacy classification_labels 'controller_stable' entry is now explicitly marked deprecated relative to controller_labels (see LEGACY_LABEL_DEPRECATION_NOTICE) rather than left to imply success.

### Item 8 [defect_repaired]: The anisotropy detector was likely over-sensitive (173/186 runs flagged, including isotropic cases).
- **Root cause:** anisotropic_response_identified fired whenever anisotropy_magnitude exceeded a fixed threshold (0.02) with NO comparison against how much anisotropy an isotropically-forced control run shows purely from finite-sample/single-realization/short-run noise. Compounded by a separate bug: anisotropy_invariants() computed sqrt(max(-0.5*trace(b@b),0)), which is <=0 for real b, so the ORIGINAL magnitude was always exactly 0 -- meaning the 173/186 flag rate in the original report came from a different, likely also-flawed code path or was measured before this sign bug was introduced; either way the magnitude computation itself needed a structural fix, independent of the threshold question.
- **Fix:** Fixed anisotropy_invariants() to magnitude=sqrt(max(trace(b@b),0)) (a valid non-negative quantity). Added structure_metrics.isotropic_control_baseline()/is_anisotropic_response_significant() (mean+z*std of matched isotropic-forcing control runs) and milestone_5_7_stress_test.run_isotropic_control_ensemble().
- **Files changed:** structure_metrics.py, milestone_5_7_stress_test.py
- **Verification:** See anisotropy_reclassification below -- and its explicit 'finding' text: this is a two-family demonstration that the corrected method distinguishes signal from noise, NOT a statistical validation of anisotropy classification across the full campaign.

### Item 9 [defect_repaired]: The 32^3 campaign cannot test k_f/k_s physics (ks=0 degeneracy) but was mixed into overall counts.
- **Root cause:** compute_terminal_layer degenerates to ks=0 at grid_n=32 in this solver's beta-derived layer construction, which collapses ALL of far_below_ks/near_ks/moderate_below_ks onto the delta_k floor -- 32^3 structurally cannot resolve distinct k_f/k_s positions, but the original applicability_map()/report aggregated 32^3 rows into the same by_k_f_vs_ks buckets as 64^3/128^3 without flagging this.
- **Fix:** Added is_diagnostic_tier=(grid_n in GRID_TIER_DIAGNOSTIC_ONLY) or (layer.ks<=0) computed per run, and AuditedStatus.resolution_status which can only reach 'resolved' when NOT diagnostic-tier. This audit report's applicability-map section computes k_f/k_s-based aggregates ONLY over grid_n>=64 rows explicitly (see applicability_map_k_f_ks_64_and_above below), separate from the full (all-tier) aggregate kept for transparency.
- **Files changed:** milestone_5_7_stress_test.py, stress_test_classification.py, generate_milestone_5_7a_audit_report.py
- **Verification:** fingerprint_collisions.32 confirms the ks=0 degeneracy directly: moderate_steady_isotropic and forcing_far_below_ks (and structurally near_ks too, though it differs in forcing_type so its fingerprint doesn't collide) all resolve k_f=delta_k=1.0 at grid_n=32.

### Item 10 [scope_limitation_confirmed]: Material dependence was not actually tested (only Newtonian implemented).
- **Root cause:** material_state.py only implements incompressible_newtonian_liquid and high_viscosity_newtonian_liquid; the other 3 of 5 preregistered material types (compressible_gas, low_mach_newtonian_gas, viscoelastic-family) correctly return material_interface_only-blocked results, but the original report's language did not always make the resulting material-scope limitation explicit enough.
- **Note:** This is a known, already-disclosed scope limitation (see AGENTS.md 'Material interface_only is not approximately Newtonian'), NOT a code defect -- no fix was made or attempted here, per the audit's explicit instruction not to add new material models. It is confirmed and restated here as a standing limitation, not counted among the 9 repaired defects.
- **Fix:** No code change (out of 5.7a scope by explicit user instruction). Restated as a limitation in this report's Remaining Limitations section.
- **Verification:** Confirmed via material_state.py: only 2 of 5 MATERIAL_TYPES are implemented; MaterialNotImplementedError raised for the rest, never silently approximated.

## Forcing-case fingerprint collisions (by grid tier)
- grid_n=32: ks=0, kc=8, 1 collision group(s)
  - ['moderate_steady_isotropic', 'forcing_far_below_ks']
- grid_n=64: ks=8.96, kc=16, 0 collision group(s)
- grid_n=128: ks=17.92, kc=32, 0 collision group(s)

## Anisotropy reclassification (isotropic-control baseline)
- **weak_isotropic_family**: case_anisotropy_magnitude=0.01819, control_baseline_mean=0.02088, control_baseline_std=0.005077, naive_label_present=False, significant_vs_control=False
- **strong_directional_family**: case_anisotropy_magnitude=0.5603, control_baseline_mean=0.0505, control_baseline_std=0.01924, naive_label_present=True, significant_vs_control=True
- The corrected anisotropy method behaves sensibly in two demonstration families: not significant for weak_isotropic (isotropic forcing), significant for strong_directional_fixed (directional forcing). It is NOT yet a statistical validation of anisotropy classification across the full campaign -- only 2 isotropic-control seeds were run per family (compute-limited, below the 5.7a spec's own recommended ensemble size), and the original 189/186-row campaign's 173 flagged runs were not individually rechecked against a matched control baseline here.

## H1 candidate-vs-baseline agreement (weak-forcing limit)
- H1 check: terminal_operator_forcing_aware.gamma_candidate_forcing_aware is constructed to reduce EXACTLY to the baseline operator as Phi_l -> 0. weak_64_A (group A, baseline) and weak_64_C (group C, candidate) run the identical weak_isotropic case/grid/seed/steps, differing only in terminal_gamma_mode. This shows the candidate is numerically consistent with the baseline in the weak-forcing limit -- it is NOT evidence group C is physically better than group A; there is no ground truth in this synthetic milestone to judge 'better' against.
- Phi_l: A=0.046615, C=0.046615
- Energy budget A: {'mean_power_input': 0.0024833613391243865, 'mean_viscous_dissipation': 0.5740853610550389, 'mean_terminal_heat': 0.000442044092541369, 'relative_closure_error': 0.018135837923772016, 'closes_within_tolerance': True}
- Energy budget C: {'mean_power_input': 0.0024833613391243865, 'mean_viscous_dissipation': 0.5740845606177295, 'mean_terminal_heat': 0.00044290471599737433, 'relative_closure_error': 0.018135703975376293, 'closes_within_tolerance': True}
- diagnostics agree to >=5 significant figures at Phi_l=0.0466, consistent with the candidate's by-construction reduction to baseline in the weak-forcing limit

## Forcing-amplitude clip summary
- 17 of 19 minimal-matrix cases were NOT materially altered by clipping. Both cases that WERE (overlap_128_spotcheck, weak_128_spotcheck) are the 128^3 spot checks -- neither can be interpreted as a faithful test of its nominal requested forcing.
  - competing_64_A: clip_active_fraction=0.02, materially_altered=False
  - directional_64_A: clip_active_fraction=0.04, materially_altered=False
  - directional_64_iso_seed1: clip_active_fraction=0.04, materially_altered=False
  - directional_64_iso_seed2: clip_active_fraction=0.04, materially_altered=False
  - near_ks_64_A: clip_active_fraction=0.04, materially_altered=False
  - overlap_128_spotcheck: clip_active_fraction=0.5, materially_altered=True
  - overlap_64_A: clip_active_fraction=0.04, materially_altered=False
  - pulsed_64_A: clip_active_fraction=0.02, materially_altered=False
  - rapid_64_A: clip_active_fraction=0.02, materially_altered=False
  - slow_64_A: clip_active_fraction=0.02, materially_altered=False
  - strong_64_A: clip_active_fraction=0.02, materially_altered=False
  - weak_128_spotcheck: clip_active_fraction=0.25, materially_altered=True
  - weak_64_A: clip_active_fraction=0.02, materially_altered=False
  - weak_64_C: clip_active_fraction=0.02, materially_altered=False
  - weak_64_D: clip_active_fraction=0.02, materially_altered=False
  - weak_64_E: clip_active_fraction=0.02, materially_altered=False
  - weak_64_F: clip_active_fraction=0.02, materially_altered=False
  - weak_64_iso_seed1: clip_active_fraction=0, materially_altered=False
  - weak_64_iso_seed2: clip_active_fraction=0.02, materially_altered=False

## Controller-label distribution (richer classification vs the legacy label)
- 10 of 19 rows show ONLY controller_bounded -- bounded but not shown to be nonoscillatory, converged, on-target, or better than a baseline. Controller effectiveness (as opposed to mere boundedness) remains mostly unestablished in this minimal matrix; see Milestone 5.7b (proposed next milestone) for a dedicated controller-effectiveness test.
- **Legacy-label notice:** classification_labels' `controller_stable` entry predates the Milestone 5.7a richer controller_labels classification (controller.classify_controller_run) and only ever meant 'c_gamma stayed numerically bounded.' It must be read as DEPRECATED wherever controller_labels is also available -- controller_labels is authoritative for any claim about controller effectiveness (converged / target_achieved / budget_error_reduced), not merely boundedness.
  - `controller_bounded`: 19/19
  - `controller_nonoscillatory`: 9/19
  - `controller_converged`: 2/19
  - `controller_target_achieved`: 0/19
  - `controller_budget_error_reduced`: 0/19
  - `controller_unstable`: 0/19

## Resolution-tier status (orthogonal to campaign completeness)
- grid_n=32: complete_campaign_executed=True, spot_check_executed=False -- diagnostic_only -- ks=0 degeneracy; excluded from all k_f/k_s-based applicability conclusions in this report (see item 9)
- grid_n=64: complete_campaign_executed=True, spot_check_executed=False -- resolved -- 17 rows in the 5.7a minimal corrected matrix (this report's primary evidence tier)
- grid_n=128: complete_campaign_executed=False, spot_check_executed=True -- spot_check_only -- 2 row(s) executed (4 steps each, compute-limited in this environment); NOT a resolution-convergence claim, and BOTH spot checks (overlap_128_spotcheck, weak_128_spotcheck) were materially altered by the forcing-amplitude clip -- neither is a faithful test of its nominal requested forcing either.

## Minimal corrected matrix: audited status (corrected vocabulary, v2)
- n_rows=19
  - pipeline_status: passed=19
  - resolution_status: resolved=19
  - energy_budget_status: closed=18, partial=1
  - forcing_regime_status: measured=17, altered_by_clip=2
  - scientific_status: synthetic_run_valid=16, assumption_challenged=2, candidate_limit_consistency_observed=1
  - spectral_status: persistent_pileup=12, transient_pileup=5, no_detected_pileup=2

(For comparison, the first-pass, now-superseded scientific_status distribution used the old candidate_behavior_observed-style vocabulary -- kept below purely for the audit trail, not as a current claim.)
- historical (v1, superseded) scientific_status: candidate_behavior_observed=17, assumption_challenged=2

## Original 189-run campaign: dedup correction
- original_n_runs_reported: 189
- corrected_n_runs_after_dedup: 186
- n_duplicates_dropped: 3
- root_cause: 3 stale-shard duplicate rows (g32_A_highvisc_actual.json reran 3 of the 14 cases already present in g32_A_highvisc.json; assembler had no dedup logic) -- see audit item 4.
- corrected_report_path: runs/milestone_5_7a/original_campaign_dedup_corrected/milestone5_7_report.json

## Applicability map -- k_f vs k_s, grid_n>=64 ONLY (32^3 excluded, see item 9)
- **below**: pipeline_only=16, energy_budget_valid=16, controller_stable=16, forcing_sensitive=8, anisotropic_response_identified=9, terminal_model_requires_extension=15, terminal_model_supported_in_domain=1
- **near**: pipeline_only=1, energy_budget_valid=1, controller_stable=1, forcing_sensitive=1, anisotropic_response_identified=1, terminal_model_requires_extension=1
- **overlap_or_above**: pipeline_only=2, controller_stable=2, forcing_sensitive=2, forcing_overlap_invalidates_assumption=2, terminal_model_not_supported=1, energy_budget_valid=1, terminal_model_requires_extension=1

## Remaining limitations
- Theta_f / temporal forcing (item 3 of the original 12-item prompt): min_steps_for_forcing_case() ensures periodic/pulsed/impulsive cases run >=2 nominal periods where wall-clock budget allows, but the 'slow' case (tau_f=5.0) only reached ~0.3 nominal periods at dt=0.03/n_steps=50 in this environment's per-command time budget -- reported as measured theta_f=1.16 (resonant_or_competing), not a full-period demonstration. No autocorrelation-based EFFECTIVE tau_f measurement was implemented; only the nominal (input) tau_f is compared.
- Material dependence remains untested beyond incompressible/high-viscosity Newtonian liquids (see audit item 10, category=scope_limitation_confirmed) -- out of scope for 5.7a by explicit instruction.
- The isotropic-control baselines used here (2 seeds per family) are smaller than the 5.7a spec's own recommended ensemble size; they demonstrate the corrected METHOD distinguishes signal from noise for these two specific families, not a full re-classification of every anisotropy label from the original 189/186-row campaign.
- 128^3 is spot-check only (4 steps, 2 cases), and BOTH spot checks were materially altered by the forcing-amplitude clip -- no resolution-convergence claim, and no independent confirmation claim, is made or supportable from this data (see boundary_finding).
- The 32^3 tier remains diagnostic-only by construction (ks=0) and contributes to NO k_f/k_s-based conclusion in this report.
- Controller effectiveness (beyond mere boundedness) remains mostly unestablished: 19/19 rows are controller_bounded, only 2/19 are also controller_converged, and none reach controller_target_achieved or controller_budget_error_reduced in this minimal matrix (see controller_label_distribution).
- candidate_difference_observed is defined in the scientific_status vocabulary but never assigned in this pass -- no run in the minimal matrix has an actual computed A-vs-C difference metric other than the single weak-limit consistency check (weak_64_A vs weak_64_C).
- No new solver runs were added beyond the preregistered minimal 64^3(+128^3 spot check) matrix and the isotropic-control seeds -- this is intentionally a repair/audit pass, not an expanded campaign.
