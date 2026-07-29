"""
Synthetic pseudo-spectral forward solver (Milestone 5.7)
=============================================================

The first forward-in-time integrator in this repo. It exists ONLY to
generate synthetic, controlled turbulence for the Milestone 5.7
forcing/material/size stress test. It must never be pointed at real JHTDB
data and no output of this module may be described as "forward validation"
of the terminal-layer theory -- that is Milestone 6, gated in AGENTS.md on
real Milestone 5 a-priori placement results, which do not yet exist. Every
report built from this module states this explicitly (see
stress_test_report.py).

It conforms to the `ForwardSolver` protocol in forward_validation_
interface.py (`initialize`/`step`/`compare_to_dns`) so a genuine Milestone 6
solver can reuse the same call shape -- see `SyntheticForwardSolver` at the
bottom of this file.

Numerics
--------
3D pseudo-spectral, incompressible Navier-Stokes, periodic domain, with:

  - the true nonlinear term (nonlinear_transfer.nonlinear_term_hat,
    divergence-free projected, optionally dealiased);
  - explicit forcing injection (forcing.ForcingState, 10 forcing types);
  - the terminal operator's total per-mode removal gamma(k) (heat +
    return, jhtdb_terminal_benchmark.terminal_operator), with the return
    fraction placed via backscatter_placement.compute_t_return and
    reinjected as a same-step kick (dns_oracle_diagnostic is refused here
    -- it requires real DNS transfer and is diagnostic-only, never
    deployable in a running solver);
  - viscosity.

Time stepping is IMEX/ETD-Euler: the linear operator L(k) = nu*k^2 +
gamma(k) (viscosity + terminal removal) is integrated exactly via
exp(-L*dt) (unconditionally stable for the stiffest part of the system);
the nonlinear term and forcing are treated explicitly at the old state
(first-order in dt). This is a stress-test tool, not a production DNS
solver -- accuracy is bounded by the same first-order truncation any
explicit-nonlinear IMEX scheme has, and every run reports the resulting
`unresolved_residual` energy-budget channel rather than assuming it is
zero. Smaller dt reduces it; `stable_dt_estimate()` provides a CFL-based
starting point.

Energy-channel attribution within one step is EXACT for the linear part:
the true total linear removal this step is `K(u*E) - K(u)` (a single
number); it is split between viscous and terminal removal using the ratio
of their instantaneous rate estimates at the old state, then renormalized
so the two parts sum exactly to the true total -- so the reported
`viscous_dissipation` + `terminal_heat` + `return`-kick bookkeeping cannot
itself introduce spurious residual, only the explicit nonlinear/forcing
step can (see docstring of `_step_once`).

Discrete energy equation (Milestone 5.7a audit)
------------------------------------------------
Every EnergyBudgetSample is meant to satisfy, exactly up to numerical
truncation error:

    P_input = dK/dt + viscous_dissipation + terminal_heat
              + wave_channel + compressive_channel + surface_channel
              + internal_channel + full_timestep_residual/dt

with `dK/dt = (K_next - K) / dt` and the last four channels always 0.0 for
this incompressible-Newtonian-only solver (see
terminal_operator_forcing_aware.TerminalEnergySplit). `return_power` is
NOT in this equation: it is a same-step internal redistribution (energy
leaves one shell's removal and is reinjected elsewhere), not a net sink,
and must never be summed into a dissipation total.

IMPORTANT (root-caused in the Milestone 5.7a audit): a *summary* metric
that compares `mean(P_input)` against `mean(viscous_dissipation +
terminal_heat)` ALONE, without `dK/dt`, is not a valid closure check --
during any spin-up transient (K still rising), most of P_input legitimately
goes into `dK/dt`, not dissipation, and such a metric will report a large
spurious "closure error" even though the complete budget above closes
almost exactly. `energy_budget.summarize_energy_budget`'s
`relative_closure_error` was fixed in the 5.7a audit to be derived from
`full_timestep_residual` (which already has `dK/dt` folded in via
`_step_once`'s `dk_measured`/`dk_predicted` bookkeeping), not from the
naive input-vs-dissipation comparison -- see that module's docstring for
the before/after and the concrete 128^3 run (`relative_closure_error`
previously reported 0.98 while `unresolved_residual` was ~0.06% of
`power_input`) that exposed the bug.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import numpy as np

from jhtdb_terminal_benchmark import (
    Config as TerminalConfig,
    wavenumbers,
    project_divergence_free,
    kinetic_energy_hat,
    shell_spectrum,
    compute_terminal_layer,
    validate_terminal_layer,
    estimate_tau_s,
    terminal_operator,
    InsufficientResolutionError,
    TerminalLayer,
)
from nonlinear_transfer import nonlinear_term_hat, dealias_mask
from comparison_metrics import shell_collapse_gamma_alpha
from backscatter_placement import compute_t_return, DIAGNOSTIC_ONLY, PlacementConfigError
from forcing import ForcingState, forcing_dominance_ratio, forcing_timescale_ratio, forcing_alignment, eddy_turnover_time
from material_state import MaterialState, get_material
from controller import ControllerConfig, ControllerState, controller_step
from forward_validation_interface import ForwardState, ForwardComparisonPoint, ForwardSolver
from terminal_operator_forcing_aware import gamma_candidate_forcing_aware


class SolverConfigError(ValueError):
    pass


@dataclass(frozen=True)
class SolverConfig:
    grid_n: int
    domain_length: float
    viscosity: float
    forcing: ForcingState
    material: MaterialState
    dt: float

    beta: float = 0.56
    alpha_s: float = 0.70
    n_shape: int = 4
    m_shape: int = 3
    cutoff_fraction: float = 0.50
    min_terminal_shells: int = 6
    preferred_terminal_shells: int = 8
    min_populated_terminal_shells: int = 4

    apply_terminal_operator: bool = True
    backscatter_placement: str = "local_cancellation"
    parent_band_c1: float | None = None
    parent_band_c2: float | None = None

    # Comparison-group hooks (milestone_5_7_stress_test.py groups A-F):
    #   "baseline"                -> jhtdb_terminal_benchmark.terminal_operator, unmodified (groups A/B/F)
    #   "candidate_forcing_aware" -> terminal_operator_forcing_aware.gamma_candidate_forcing_aware (group C)
    # hard_cutoff=True additionally (or independently) hard-zeros modes above
    # kc every step (group E); the energy this removes is booked into the
    # terminal_heat channel of that step's EnergyBudgetSample, since it is
    # genuinely destroyed kinetic energy, same as the smooth operator's heat
    # fraction.
    terminal_gamma_mode: str = "baseline"
    hard_cutoff: bool = False

    dealias: bool = True
    seed: int = 0

    use_controller: bool = True
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    c_gamma_fixed: float = 1.0  # used when use_controller=False

    forcing_amplitude_safety_factor: float = 10.0

    # Milestone 5.7a audit fix: Phi_l = P_f/(u_l^3/l) is measured relative
    # to the CURRENT local velocity scale, not the forcing power alone. A
    # cold start (near-zero initial velocity) makes Phi_l enormous for any
    # nonzero forcing regardless of how "weak" that forcing's absolute
    # power is, because u_l is tiny early on -- confirmed root cause of
    # every Milestone 5.7 run (including the case literally named
    # "weak_isotropic") measuring in the forcing_dominated regime. Setting
    # initial_kinetic_energy lets a run start already turbulent (a "warm
    # start"), so a genuinely weak forcing can be tested against an
    # already-developed velocity scale, actually reaching Phi_l << 1. None
    # (default) preserves the original cold-start behavior.
    initial_kinetic_energy: float | None = None

    def __post_init__(self):
        self.material.require_implemented()
        if self.grid_n < 4:
            raise SolverConfigError("grid_n too small")
        if self.viscosity <= 0:
            raise SolverConfigError("viscosity must be > 0")
        if self.dt <= 0:
            raise SolverConfigError("dt must be > 0")
        if self.initial_kinetic_energy is not None and self.initial_kinetic_energy <= 0:
            raise SolverConfigError("initial_kinetic_energy must be > 0 when set")
        if self.backscatter_placement in DIAGNOSTIC_ONLY:
            raise SolverConfigError(
                f"backscatter_placement={self.backscatter_placement!r} is diagnostic-only "
                "(requires real DNS transfer) and cannot drive a running solver."
            )
        if self.terminal_gamma_mode not in ("baseline", "candidate_forcing_aware"):
            raise SolverConfigError(f"unknown terminal_gamma_mode {self.terminal_gamma_mode!r}")

    def to_terminal_config(self) -> TerminalConfig:
        return TerminalConfig(
            domain_length=self.domain_length,
            beta=self.beta,
            alpha_s=self.alpha_s,
            n_shape=self.n_shape,
            m_shape=self.m_shape,
            cutoff_fraction=self.cutoff_fraction,
            min_terminal_shells=self.min_terminal_shells,
            preferred_terminal_shells=self.preferred_terminal_shells,
            min_populated_terminal_shells=self.min_populated_terminal_shells,
            backscatter_placement=self.backscatter_placement,
            parent_band_c1=self.parent_band_c1,
            parent_band_c2=self.parent_band_c2,
        )


def stable_dt_estimate(*, grid_n: int, domain_length: float, viscosity: float, u_rms: float, safety: float = 0.3) -> float:
    """CFL/diffusive-limited dt starting point (not a hard bound; the ETD
    scheme is unconditionally stable for the viscous/terminal linear part,
    but the explicit nonlinear+forcing part is not)."""
    delta_k = 2.0 * np.pi / domain_length
    kmax = delta_k * (grid_n // 2)
    dx = domain_length / grid_n
    advective = dx / max(u_rms, 1e-6)
    diffusive = 1.0 / max(viscosity * kmax * kmax, 1e-12)
    return float(safety * min(advective, diffusive))


@dataclass(frozen=True)
class EnergyBudgetSample:
    """One step's energy-budget sample.

    Discrete energy equation this step is meant to satisfy exactly
    (Milestone 5.7a audit -- see module docstring "Discrete energy
    equation" section):

        P_input = dK/dt + viscous_dissipation + terminal_heat
                  + wave_channel + compressive_channel + surface_channel
                  + internal_channel + full_timestep_residual/dt

    `dK/dt` is `(kinetic_energy_next - kinetic_energy) / dt` (not stored on
    this sample -- compute it from consecutive samples' `kinetic_energy`,
    or read `full_timestep_residual` directly, which already has dK/dt
    folded in). `return_power` is NOT a term in this equation -- it is
    internal redistribution (same-step reinjection), not a net sink; it is
    recorded for diagnostic purposes only.

    `linear_channel_split_exact=True` always: the viscous/heat split of the
    linear (ETD-integrated) part of the step is exact by construction (the
    two counterfactual rates are renormalized to sum to the true measured
    linear-part energy change -- see `_step_once`). This is a DIFFERENT,
    weaker claim than "the full timestep conserves energy": the nonlinear
    term and forcing are treated explicitly (first-order in dt), so
    `full_timestep_residual` is generally nonzero and shrinks with dt (see
    `tests/test_pseudo_spectral_solver.py::test_residual_shrinks_with_dt_*`)
    -- it is a real truncation-error diagnostic, not evidence of a bug, and
    must never be described as "conserves energy" without also reporting
    its magnitude relative to `power_input`.
    """

    time: float
    kinetic_energy: float
    power_input: float
    viscous_dissipation: float
    terminal_heat: float
    return_power: float
    wave_channel: float = 0.0
    compressive_channel: float = 0.0
    surface_channel: float = 0.0
    internal_channel: float = 0.0
    unresolved_residual: float = 0.0
    c_gamma: float = 1.0
    forcing_alignment: float = float("nan")
    energy_above_cutoff: float = 0.0
    linear_channel_split_exact: bool = True
    forcing_requested_amplitude: float = 0.0
    forcing_applied_amplitude: float = 0.0
    forcing_clip_active: bool = False

    @property
    def full_timestep_residual(self) -> float:
        """Alias for unresolved_residual under its Milestone 5.7a audit
        name -- the complete-budget residual, dK/dt included, NOT just a
        comparison of P_input against dissipation alone."""
        return self.unresolved_residual


@dataclass(frozen=True)
class SolverState:
    velocity_hat: np.ndarray  # (3, n, n, n) complex, spectral
    time: float
    controller_state: ControllerState
    forcing_shapes: dict = field(default_factory=dict)  # persisted forcing patterns per k_f (temporal coherence)
    step_count: int = 0


def _random_divergence_free_field(kmag, kx, ky, kz, *, k0: float, seed: int) -> np.ndarray:
    """A generic synthetic starting velocity field: random phase, energy
    concentrated near wavenumber k0 (E(k) ~ k^4 exp(-2(k/k0)^2), a standard
    synthetic-turbulence initial spectrum shape), projected divergence-free."""
    rng = np.random.default_rng(seed)
    shape = kmag.shape
    raw = rng.normal(size=(3,) + shape) + 1j * rng.normal(size=(3,) + shape)
    amp = (kmag**2) * np.exp(-(kmag / max(k0, 1e-6)) ** 2)
    raw = raw * amp[None, ...]
    return project_divergence_free(raw, kx, ky, kz)


def _twice_modal_energy(uh: np.ndarray) -> np.ndarray:
    n3 = np.prod(uh.shape[1:])
    return np.sum(np.abs(uh) ** 2, axis=0) / (n3 * n3)


def _forcing_envelope(forcing_type: str, t: float, tau_f: float) -> float:
    if forcing_type in ("periodic", "rotating_direction"):
        return float(0.5 * (1.0 + np.cos(2.0 * np.pi * t / tau_f)))
    if forcing_type == "pulsed":
        phase = (t % tau_f) / tau_f
        return 1.0 if phase < 0.5 else 0.0
    if forcing_type == "impulsive":
        phase = (t % tau_f) / tau_f
        return 1.0 if phase < 0.05 else 0.0
    return 1.0


def _direction_vector(forcing_type: str, t: float, tau_f: float, direction) -> Optional[np.ndarray]:
    if direction is None:
        return None
    d = np.array(direction, dtype=float)
    norm = np.linalg.norm(d)
    if norm < 1e-30:
        return None
    d = d / norm
    if forcing_type == "rotating_direction":
        # Simplified: rotate within the plane orthogonal to the z-axis
        # component of the base direction (documented simplification --
        # general 3D axis rotation is not implemented).
        theta = 2.0 * np.pi * t / tau_f
        rot = np.array(
            [d[0] * np.cos(theta) - d[1] * np.sin(theta), d[0] * np.sin(theta) + d[1] * np.cos(theta), d[2]]
        )
        n2 = np.linalg.norm(rot)
        return rot / n2 if n2 > 1e-30 else d
    return d


def make_forcing_hat(
    cfg: SolverConfig, kx, ky, kz, kmag, u_hat: np.ndarray, t: float, rng: np.random.Generator, forcing_shapes: dict
) -> tuple[np.ndarray, dict, dict]:
    """Build the forcing spectral field for this step, matching the target
    instantaneous power exactly when the forcing pattern is well-aligned
    with the current velocity field, and falling back to a bounded,
    self-normalized amplitude otherwise (see module docstring on the
    forcing-amplitude safety clip -- a documented numerical simplification,
    not a physical claim).

    Milestone 5.7a audit: returns a third element, `clip_diagnostics`,
    instrumenting the `lam_max` safety clip per injection scale --
    `requested_amplitude` (the unclipped `lam`), `applied_amplitude` (after
    clipping), and `clip_active` (whether they differ). This lets a caller
    detect when the clip -- not the forcing case's nominal parameters -- is
    controlling the effective injected forcing (see stress_test_report's
    forcing_clip_materially_altered_case classification)."""
    n3 = np.prod(kmag.shape)
    n3sq = n3 * n3
    total = np.zeros_like(u_hat)
    new_shapes = dict(forcing_shapes)
    f = cfg.forcing
    n_scales = len(f.injection_wavenumbers)
    envelope = _forcing_envelope(f.forcing_type, t, f.timescale)
    direction = _direction_vector(f.forcing_type, t, f.timescale, f.direction)

    requested_amplitude = 0.0
    applied_amplitude = 0.0
    clip_active = False

    for k_f in f.injection_wavenumbers:
        mask = (kmag >= max(k_f - f.bandwidth / 2.0, 1e-9)) & (kmag <= k_f + f.bandwidth / 2.0)
        if not mask.any():
            continue
        shape = kmag.shape
        fresh = rng.normal(size=(3,) + shape) + 1j * rng.normal(size=(3,) + shape)
        if direction is not None:
            directed = (rng.normal(size=shape) + 1j * rng.normal(size=shape))
            directed_vec = direction[:, None, None, None] * directed[None, ...]
            fresh = f.spatial_coherence * directed_vec + (1.0 - f.spatial_coherence) * fresh
        fresh = fresh * mask[None, ...]
        prev = new_shapes.get(k_f)
        if prev is not None and prev.shape == fresh.shape:
            blend = f.temporal_coherence * prev + np.sqrt(max(1.0 - f.temporal_coherence**2, 0.0)) * fresh
        else:
            blend = fresh
        pattern = project_divergence_free(blend, kx, ky, kz)
        new_shapes[k_f] = pattern

        p_target = f.power_input * envelope / max(n_scales, 1)
        if p_target == 0.0:
            continue
        proj_power = float(np.real(np.sum(np.conj(u_hat) * pattern))) / n3sq
        shape_energy = float(np.sum(np.abs(pattern) ** 2)) / n3sq
        lam_fallback = np.sign(p_target) * np.sqrt(abs(p_target) / max(shape_energy, 1e-30))
        lam_max = abs(lam_fallback) * cfg.forcing_amplitude_safety_factor
        if abs(proj_power) > 1e-30:
            lam_unclipped = p_target / proj_power
            lam = float(np.clip(lam_unclipped, -lam_max, lam_max))
        else:
            lam_unclipped = lam_fallback
            lam = float(lam_fallback)
        requested_amplitude += abs(lam_unclipped)
        applied_amplitude += abs(lam)
        if abs(lam) < abs(lam_unclipped) - 1e-15 * max(abs(lam_unclipped), 1.0):
            clip_active = True
        total = total + lam * pattern

    clip_diagnostics = {
        "requested_amplitude": float(requested_amplitude),
        "applied_amplitude": float(applied_amplitude),
        "clip_active": bool(clip_active),
    }
    return total, new_shapes, clip_diagnostics


def _step_once(
    state: SolverState, cfg: SolverConfig, kx, ky, kz, kmag, nyquist, layer: TerminalLayer, rng: np.random.Generator
) -> tuple[SolverState, EnergyBudgetSample]:
    uh = state.velocity_hat
    n3 = np.prod(kmag.shape)
    nu = cfg.viscosity
    dt = cfg.dt

    k0 = kinetic_energy_hat(uh)

    # --- terminal operator (heat+return removal rate) at old state -------
    if cfg.apply_terminal_operator:
        tau_s = estimate_tau_s(uh, kmag, layer.ks)
        if cfg.terminal_gamma_mode == "candidate_forcing_aware":
            u_rms = float(np.sqrt(2.0 * k0 / 3.0)) if k0 > 0 else 1e-6
            ell_f = 2.0 * np.pi / cfg.forcing.injection_wavenumber
            tau_l = eddy_turnover_time(max(u_rms, 1e-6), ell_f)
            try:
                phi_l = forcing_dominance_ratio(abs(cfg.forcing.power_input), max(u_rms, 1e-6), ell_f)
            except ValueError:
                phi_l = 0.0
            theta_f = forcing_timescale_ratio(cfg.forcing.timescale, max(tau_l, 1e-9))
            op = gamma_candidate_forcing_aware(
                uh, kmag, layer.kc, layer.beta_effective, cfg.alpha_s, cfg.n_shape, cfg.m_shape,
                state.controller_state.c_gamma, tau_s, phi_l=phi_l, theta_f=theta_f,
            )
        else:
            op = terminal_operator(
                uh, kmag, layer.kc, layer.beta_effective, cfg.alpha_s, cfg.n_shape, cfg.m_shape, state.controller_state.c_gamma, tau_s
            )
        gamma = op["gamma"]
        alpha = op["alpha"]
        terminal_power_rate = op["terminal_power"]
        heat_power_rate = op["heat_power"]
        return_power_rate = op["return_power"]
    else:
        gamma = np.zeros_like(kmag)
        alpha = np.ones_like(kmag)
        terminal_power_rate = heat_power_rate = return_power_rate = 0.0

    twice_modal = _twice_modal_energy(uh)
    viscous_power_rate = float(np.sum(nu * kmag**2 * twice_modal))

    # --- forcing at old state ---------------------------------------------
    f_hat, new_shapes, clip_diag = make_forcing_hat(cfg, kx, ky, kz, kmag, uh, state.time, rng, state.forcing_shapes)
    f_hat = project_divergence_free(f_hat, kx, ky, kz)
    power_input_rate = float(np.real(np.sum(np.conj(uh) * f_hat))) / (n3 * n3)

    # --- nonlinear term (optionally dealiased) -----------------------------
    if cfg.dealias:
        mask = dealias_mask(kx, ky, kz, nyquist)
        uh_work = uh * mask
    else:
        uh_work = uh
    nh = nonlinear_term_hat(uh_work, kx, ky, kz)
    nh_perp = project_divergence_free(nh, kx, ky, kz)
    if cfg.dealias:
        nh_perp = nh_perp * mask

    # --- ETD-Euler linear step (viscosity + terminal removal, exact) ------
    L = nu * kmag**2 + gamma
    E = np.exp(-L * dt)
    phi1 = np.where(L > 1e-300, (1.0 - E) / np.where(L > 1e-300, L, 1.0), dt)

    rhs_explicit = nh_perp + f_hat
    uh_after_linear = uh * E
    uh_new = uh_after_linear + rhs_explicit * phi1

    k_after_linear = kinetic_energy_hat(uh_after_linear)
    total_linear_removed = k0 - k_after_linear  # exact, this-step

    denom = viscous_power_rate + terminal_power_rate
    if denom > 1e-300:
        visc_frac = viscous_power_rate / denom
    else:
        visc_frac = 0.5
    viscous_dissipation = total_linear_removed * visc_frac
    terminal_removed = total_linear_removed * (1.0 - visc_frac)

    if terminal_power_rate > 1e-300:
        heat_frac = heat_power_rate / terminal_power_rate
    else:
        heat_frac = 1.0
    terminal_heat = terminal_removed * heat_frac
    return_available = terminal_removed * (1.0 - heat_frac)

    # --- return placement: reinject as a same-step kick --------------------
    shells, e_ref = shell_spectrum(uh, kmag)
    gamma_shell, alpha_shell = shell_collapse_gamma_alpha(uh, kmag, gamma, alpha)
    return_kick_hat = np.zeros_like(uh)
    if return_available > 0 and cfg.apply_terminal_operator:
        try:
            t_return_shell = compute_t_return(
                cfg.backscatter_placement, shells, e_ref, gamma_shell, alpha_shell,
                ks=layer.ks, c1=cfg.parent_band_c1, c2=cfg.parent_band_c2,
            )
        except PlacementConfigError:
            t_return_shell = np.zeros_like(e_ref)
        total_t_return = float(t_return_shell.sum())
        if total_t_return > 1e-300:
            fractions = np.clip(t_return_shell, 0.0, None) / total_t_return
            for shell_k, frac in zip(shells, fractions):
                if frac <= 0:
                    continue
                shell_mask = (kmag >= shell_k - 0.5) & (kmag < shell_k + 0.5)
                if not shell_mask.any():
                    continue
                pattern = rng.normal(size=(3,) + kmag.shape) + 1j * rng.normal(size=(3,) + kmag.shape)
                pattern = pattern * shell_mask[None, ...]
                pattern = project_divergence_free(pattern, kx, ky, kz)
                shape_energy = float(np.sum(np.abs(pattern) ** 2)) / (n3 * n3)
                target_energy = return_available * frac
                if shape_energy > 1e-30 and target_energy > 0:
                    amp = np.sqrt(target_energy / shape_energy)
                    return_kick_hat = return_kick_hat + amp * pattern

    uh_new = uh_new + return_kick_hat

    # --- comparison-group E: hard spectral cutoff ---------------------------
    # Zeros every mode above kc outright each step (no smooth damping, no
    # heat/return split). The energy this removes is genuinely destroyed, so
    # it is booked into heat_power_rate for this step's budget accounting --
    # it is not "returned" anywhere, unlike the smooth operator's return
    # fraction.
    if cfg.hard_cutoff:
        k_before_hard = kinetic_energy_hat(uh_new)
        keep_mask = kmag <= layer.kc
        uh_new = uh_new * keep_mask[None, ...]
        k_after_hard = kinetic_energy_hat(uh_new)
        hard_cutoff_removed_rate = (k_before_hard - k_after_hard) / dt
        heat_power_rate = heat_power_rate + hard_cutoff_removed_rate

    k_final = kinetic_energy_hat(uh_new)

    dk_measured = (k_final - k0) / dt
    dk_predicted = power_input_rate - viscous_power_rate - heat_power_rate
    residual = (dk_measured - dk_predicted) * dt  # energy units, this step

    _, e_new = shell_spectrum(uh_new, kmag)
    energy_above_cutoff = float(e_new[shells > layer.kc].sum())

    u_real = np.fft.ifftn(uh, axes=(1, 2, 3)).real
    f_real = np.fft.ifftn(f_hat, axes=(1, 2, 3)).real
    a_f = forcing_alignment(u_real, f_real)

    # --- controller ---------------------------------------------------------
    if cfg.use_controller:
        new_controller = controller_step(
            state.controller_state, cfg.controller, target_power=power_input_rate, measured_power=terminal_power_rate, dt=dt
        )
    else:
        new_controller = ControllerState(
            c_gamma=cfg.c_gamma_fixed,
            integral=state.controller_state.integral,
            step_count=state.controller_state.step_count + 1,
            error_history=state.controller_state.error_history,
            c_gamma_history=state.controller_state.c_gamma_history + (cfg.c_gamma_fixed,),
        )

    new_state = SolverState(
        velocity_hat=uh_new,
        time=state.time + dt,
        controller_state=new_controller,
        forcing_shapes=new_shapes,
        step_count=state.step_count + 1,
    )
    sample = EnergyBudgetSample(
        time=state.time,
        kinetic_energy=k0,
        power_input=power_input_rate,
        viscous_dissipation=viscous_power_rate,
        terminal_heat=heat_power_rate,
        return_power=return_power_rate,
        unresolved_residual=residual,
        c_gamma=state.controller_state.c_gamma,
        forcing_alignment=a_f,
        energy_above_cutoff=energy_above_cutoff,
        forcing_requested_amplitude=clip_diag["requested_amplitude"],
        forcing_applied_amplitude=clip_diag["applied_amplitude"],
        forcing_clip_active=clip_diag["clip_active"],
    )
    return new_state, sample


def initialize_state(cfg: SolverConfig, kx, ky, kz, kmag) -> SolverState:
    velocity = _random_divergence_free_field(kmag, kx, ky, kz, k0=cfg.forcing.injection_wavenumber, seed=cfg.seed)
    if cfg.initial_kinetic_energy is not None:
        current_ke = kinetic_energy_hat(velocity)
        if current_ke > 1e-300:
            scale = np.sqrt(cfg.initial_kinetic_energy / current_ke)
            velocity = velocity * scale
    controller_state = ControllerState(c_gamma=cfg.c_gamma_fixed if not cfg.use_controller else 1.0)
    return SolverState(velocity_hat=velocity, time=0.0, controller_state=controller_state)


def run_solver(cfg: SolverConfig, n_steps: int) -> tuple[SolverState, list[EnergyBudgetSample], TerminalLayer]:
    """Run the solver for n_steps. Raises InsufficientResolutionError up
    front if the terminal layer cannot be resolved at this grid_n -- same
    resolution-awareness discipline as every other script in this repo."""
    kx, ky, kz = wavenumbers(cfg.grid_n, cfg.domain_length)
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    nyquist = float(np.max(np.abs(kx[:, 0, 0])))
    delta_k = 2.0 * np.pi / cfg.domain_length
    kc = cfg.cutoff_fraction * nyquist
    tcfg = cfg.to_terminal_config()
    layer = compute_terminal_layer(kc, delta_k, tcfg)

    state = initialize_state(cfg, kx, ky, kz, kmag)
    rng = np.random.default_rng(cfg.seed + 1)
    samples: list[EnergyBudgetSample] = []
    for _ in range(n_steps):
        state, sample = _step_once(state, cfg, kx, ky, kz, kmag, nyquist, layer, rng)
        samples.append(sample)
    return state, samples, layer


# --- ForwardSolver protocol adapter (synthetic-only) -------------------------


class SyntheticForwardSolver:
    """Conforms to forward_validation_interface.ForwardSolver. This is a
    SYNTHETIC-ONLY adapter for the Milestone 5.7 stress test -- it must
    never be used with real DNS input. `initialize()` here takes a
    SolverConfig instead of real u_dns_t0, deliberately breaking exact
    protocol-signature compatibility so it cannot be silently substituted
    for a real Milestone 6 solver; see `step`/`compare_to_dns` for the
    parts that do match the protocol shape."""

    def __init__(self, cfg: SolverConfig):
        self.cfg = cfg
        kx, ky, kz = wavenumbers(cfg.grid_n, cfg.domain_length)
        self.kx, self.ky, self.kz = kx, ky, kz
        self.kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
        self.nyquist = float(np.max(np.abs(kx[:, 0, 0])))
        delta_k = 2.0 * np.pi / cfg.domain_length
        kc = cfg.cutoff_fraction * self.nyquist
        self.layer = compute_terminal_layer(kc, delta_k, cfg.to_terminal_config())
        self.rng = np.random.default_rng(cfg.seed + 1)
        self._solver_state: SolverState | None = None

    def initialize(self, u_dns_t0=None, cfg=None) -> ForwardState:
        self._solver_state = initialize_state(self.cfg, self.kx, self.ky, self.kz, self.kmag)
        return self._to_forward_state(self._solver_state)

    def step(self, state: ForwardState, dt: float) -> ForwardState:
        if self._solver_state is None:
            raise RuntimeError("call initialize() before step()")
        local_cfg = self.cfg if abs(dt - self.cfg.dt) < 1e-15 else _with_dt(self.cfg, dt)
        self._solver_state, _sample = _step_once(
            self._solver_state, local_cfg, self.kx, self.ky, self.kz, self.kmag, self.nyquist, self.layer, self.rng
        )
        return self._to_forward_state(self._solver_state)

    def compare_to_dns(self, state: ForwardState, dns_snapshot) -> ForwardComparisonPoint:
        raise NotImplementedError(
            "SyntheticForwardSolver never compares against real DNS -- there is no DNS "
            "in a synthetic-only run. Use energy_budget.py / structure_metrics.py to "
            "compare against this solver's own targets instead."
        )

    def _to_forward_state(self, s: SolverState) -> ForwardState:
        u_real = np.fft.ifftn(s.velocity_hat, axes=(1, 2, 3)).real
        return ForwardState(velocity=u_real, time=s.time, controller_state={"c_gamma": s.controller_state.c_gamma})


def _with_dt(cfg: SolverConfig, dt: float) -> SolverConfig:
    import dataclasses

    return dataclasses.replace(cfg, dt=dt)
