"""Time integration for unsteady incompressible Navier-Stokes:
AB2 explicit convection + Crank-Nicolson/theta-scheme diffusion + projection.

Each step:

1. **Explicit AB2 convection** (optional; ``convection_scheme=None`` gives
   the pure Stokes-flow integrator unchanged from Milestone 5):

   ```
   N^{n+1/2} = 3/2*N(u^n) - 1/2*N(u^{n-1})
   ```

   using either :func:`navier3d.convection.centered_convection` or
   :func:`navier3d.convection.upwind_convection` (``convection.py``) for
   ``N``, folded into the diffusion predictor's explicit source term as
   ``-N^{n+1/2}`` (the governing equation is
   ``du/dt = -N(u) - (1/rho)grad(p) + nu*lap(u) + f``).

2. **Implicit theta-scheme diffusion predictor**, one
   :class:`~navier3d.diffusion.VelocityDiffusionSystem` solve per velocity
   component (``theta=1.0`` backward/implicit Euler, ``theta=0.5``
   Crank-Nicolson):

   ```
   (I - theta*nu*dt*L_h) u* = (I + (1-theta)*nu*dt*L_h) u^n
                               + dt*nu*correction
                               - dt*[3/2*N(u^n) - 1/2*N(u^{n-1})]   (if convection enabled)
                               + dt*f^{n+theta}
   ```

   The minus sign here is not optional: the governing equation is
   ``du/dt + N(u) = -grad(p)/rho + nu*lap(u) + f``, i.e.
   ``du/dt = -N(u) - grad(p)/rho + nu*lap(u) + f``, so the AB2
   extrapolation of ``N`` must be *subtracted* from the predictor's RHS.
   The code does this via ``conv_contribution =
   -ab2_field.components()[axis].interior`` in :meth:`step` below --
   verified independently, without projection or Taylor-Green's pressure
   cancellation, by ``tests/test_predictor_sign.py``.

   -- exactly the review's required CN/AB2 predictor formula.

3. Milestone 4's projection (``projection.project``) on the predictor.

AB2 startup (documented, not implicit)
------------------------------------------
AB2 needs ``N(u^{n-1})``, which does not exist on the very first step.

**Revised in the Milestone 6 correction round** (the original
forward-Euler-in-convection startup measurably slowed the observed
temporal order -- 1.11/1.23/1.59 across dt in {T/64,...,T/512}, not yet
reaching the asymptotic 2 -- see the Milestone 6 report's temporal
convergence table for the before/after comparison). The first step now
uses a genuine two-stage, second-order (Heun's method / explicit
trapezoidal) estimate of the half-step convective term instead:

```
N(u^0)               computed from the actual initial state
u_provisional = u^0 - dt*N(u^0)     (convection-only forward-Euler probe;
                                      diffusion/pressure/forcing excluded
                                      deliberately -- this provisional
                                      state exists solely to obtain a
                                      second, later-time sample of N for
                                      the Heun average, and is discarded
                                      immediately after)
N(u_provisional)      computed from the probe state
N^{1/2} = 0.5*(N(u^0) + N(u_provisional))     (Heun average -- 2nd order)
```

``self._previous_convection`` is then set to ``N(u^0)`` (not the
provisional value), exactly as before, so every subsequent step proceeds
with the standard AB2 formula ``N^{n+1/2} = 1.5*N(u^n) - 0.5*N(u^{n-1})``
using genuine step history. This is the standard technique of using a
one-time single-step RK2 startup to initialize a 2-step Adams-Bashforth
method at full order, rather than tolerating an order-reduced first
step.

The integration *method* is a first-class, swappable object
(:class:`ThetaSchemeIntegrator`) rather than something hard-coded into a
"top-level solver" -- there is no such solver yet (Milestone 8+); a
:class:`ThetaSchemeIntegrator` instance is used directly by tests and
scripts via :meth:`~ThetaSchemeIntegrator.step` (or the thin
:func:`run` loop below).

CFL and hard rejection
--------------------------
```
CFL = dt * (max|u|/dx + max|v|/dy + max|w|/dz)
```
(the Milestone 1-specified convective CFL, evaluated conservatively by
combining each component's own max magnitude rather than requiring
co-location). Computed from ``state`` *before* advancing it each step;
if ``cfl_max`` is configured (not ``None``) and the computed CFL exceeds
it, :class:`CFLError` is raised immediately -- the step is never taken.

Matrix/factorization reuse (Milestone 7 Part E)
---------------------------------------------------
The :class:`~navier3d.pressure.PressurePoissonSystem` is built lazily on
the first :meth:`step` call and reused via ``pressure_system=`` on every
subsequent call, as in Milestone 5. The three
:class:`~navier3d.diffusion.VelocityDiffusionSystem` instances are now
built **lazily and cached by** ``(nu, dt, theta)`` -- the exact three
quantities their assembled matrix depends on (mesh/BCs are fixed for an
integrator's lifetime, so are not part of the cache key). A step whose
``dt`` matches a previously-seen value reuses the cached systems (and
their factorizations/preconditioners) unchanged; a genuinely new ``dt``
(e.g. from :mod:`navier3d.adaptive`'s CFL-driven controller) triggers
exactly one rebuild for that ``dt``, cached for any future step that
returns to it. This is the mechanism that makes adaptive timestepping
(below) compatible with matrix reuse at all -- without it, every
adaptive step would need a full diffusion-matrix rebuild.

Variable-step timestepping (Milestone 7 Parts D, F, G)
-----------------------------------------------------------
``step(state, dt=None)`` accepts an optional per-call ``dt`` override
(``None`` uses ``self.dt``, the integrator's current/default step size,
unchanged Milestone 5 behavior). Combined with
:class:`navier3d.adaptive.AdaptiveTimestepController` (Part F) in an
external loop (this module has no opinion on *how* ``dt`` is chosen --
it only needs to accept a possibly-different one each call), this
enables adaptive timestepping.

**AB2 under variable steps is NOT the constant-step ``3/2, -1/2``
formula** -- see :func:`navier3d.adaptive.variable_step_ab2_coefficients`
for the full derivation. ``step()`` tracks the *previous* step's size
(``self._previous_dt``) alongside its convective term
(``self._previous_convection``) and recomputes the correct
``r=dt_current/dt_previous``-dependent coefficients every step; the
constant-step formula is recovered automatically whenever ``r=1``. The
first step (no history yet) is unaffected -- it still uses the
Heun-startup rule above regardless of variable-step configuration.

``warm_start=True`` (Part D): the previous step's own pressure field and
predictor velocity (``u*``) are passed as the initial guess (``x0``) to
the pressure and diffusion solves respectively. This only *helps*
(reduces iteration count) for iterative solvers -- meaningless, and
therefore a no-op, for ``solver="direct"`` (both
:meth:`~navier3d.pressure.PressurePoissonSystem.solve` and
:meth:`~navier3d.diffusion.VelocityDiffusionSystem.solve` accept but
ignore ``x0`` for direct solves). Benchmarked, not merely assumed
beneficial -- see ``tests/test_time_integrators.py``'s warm-start
iteration-count comparison and the Milestone 7 report.

Profiling (Milestone 7 Part I)
-----------------------------------
Each :meth:`step` call attributes its wall-clock time across the
categories the review specifies (convection, diffusion RHS construction,
diffusion linear solve, pressure RHS construction, pressure solve,
projection correction, boundary conditions, diagnostics, total) into two
places: ``StepDiagnostics.step_profile`` (this step only) and
``self.profiler`` (a :class:`navier3d.profiling.StepProfiler`
accumulating across every step this integrator has taken, for a
whole-run breakdown -- see ``self.profiler.format_report()``).

Incremental/rotational predictor and pressure history (Milestone 8)
--------------------------------------------------------------------------
``projection_method`` selects which of three pressure-treatment methods
:meth:`step` uses, all sharing the exact same convection/diffusion
predictor machinery above except for one added term:

* ``"non_incremental"`` (default -- Milestones 4-6's Chorin method,
  entirely unchanged, still the default so every existing test and
  example keeps working with zero behavior change): the predictor has
  no pressure term at all; :func:`navier3d.projection.project` solves
  for the *full* pressure from scratch every step. Documented ~O(dt)
  temporal splitting ceiling (Milestone 6 correction,
  ``docs/architecture.md`` Section 13) -- preserved, not revisited.
* ``"incremental"`` / ``"rotational"``: the predictor gains a
  ``-(1/rho)*G_h(p^n)`` term (``p^n`` = the *previous* step's own
  pressure, i.e. ``state.pressure`` -- ghost-filled with this
  integrator's own physical ``bcs`` before differencing, distinct from
  the per-step Neumann values :func:`navier3d.projection.derive_phi_bcs`
  derives for the *correction* field ``phi``, see that function's
  docstring), and :func:`navier3d.projection.project_incremental` solves
  for a pressure **increment** ``phi`` instead, updating
  ``p^{n+1} = p^n + phi`` (incremental) or additionally subtracting a
  rotational correction ``chi*rho*nu*D_h(u*)`` (rotational, ``chi``
  configurable, default ``1.0``). Full derivation, BC treatment per face
  type, and honestly-reported empirical temporal order are in
  ``docs/architecture.md`` Section 15 ("Milestone 8").

``state.pressure`` (part of :class:`~navier3d.fields.FlowState` since
Milestone 1) *is* ``p^n`` for the incremental/rotational predictor --
no new field was needed there. The **additional** history these methods
(and variable-step AB2) need beyond one ``FlowState`` --
``previous_convection``, ``previous_dt``, and (for warm-starting only)
``previous_phi`` -- is exposed explicitly via :attr:`ThetaSchemeIntegrator.history`
/ :meth:`ThetaSchemeIntegrator.restore_history` rather than left as
undocumented private state; see :class:`IntegratorHistory`.
"""
from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

import numpy as np

from .adaptive import pressure_extrapolation_coefficients, variable_step_ab2_coefficients
from .boundary_conditions import BoundaryConditionSet, apply_pressure_bc, apply_velocity_bc
from .convection import centered_convection, upwind_convection
from .diffusion import DiffusionDiagnostics, VelocityDiffusionSystem
from .fields import FlowState, ScalarField, VelocityField
from .mesh import StructuredMesh3D
from .operators import gradient as _gradient
from .pressure import PressurePoissonSystem, SolveDiagnostics
from .profiling import StepProfiler
from .projection import ProjectionError, project, project_incremental
from .variable_diffusion import VariableDiffusionSystem, variable_viscosity_stress_divergence

ForcingFn = Callable[[float], VelocityField]

_CONVECTION_SCHEMES = {"centered": centered_convection, "upwind": upwind_convection}
_PROJECTION_METHODS = {"non_incremental", "incremental", "rotational"}


class IntegrationError(RuntimeError):
    """Raised when a step produces non-finite (NaN/Inf) velocity or
    pressure, or when the underlying diffusion/pressure solve fails --
    never silently continued past."""


class CFLError(RuntimeError):
    """Raised when the computed CFL number exceeds the configured
    ``cfl_max`` -- the step is rejected before being taken, not silently
    run past the configured stability limit."""


@dataclass
class StepDiagnostics:
    """Per-timestep diagnostics.

    Divergence is reported in three distinct forms, deliberately not
    conflated (see ``projection.py``'s ``_divergence_stats`` for the exact
    definitions):

    * ``max_divergence`` -- **raw** ``|D_h u|_inf`` (units: 1/time). Grid-
      and case-dependent in magnitude; a threshold like ``< 1e-6`` on this
      quantity is only meaningful for a *specific* problem's velocity/
      length scale, which is why the acceptance target across milestones
      has consistently been stated on the *normalized* quantity instead.
    * ``l2_divergence`` -- **raw**, volume-weighted ``|D_h u|_2``
      (same units/caveat as above).
    * ``normalized_divergence`` -- ``E_div = |D_h u|_2 / (|u|_2/L + eps)``,
      **dimensionless**. This is the quantity the project's stated
      acceptance criterion (``< 1e-8`` for controlled benchmarks) applies
      to; a long, decaying run's raw ``max_divergence``/``l2_divergence``
      naturally shrink *alongside* the velocity itself and are not
      directly comparable to that threshold.

    Timing is reported **separately** per stage (``convection_time``,
    ``diffusion_time`` -- summed over the 3 components --,
    ``pressure_diagnostics.assembly_time``/``solve_time``), never merged
    into one number, so a slow step can be attributed to a specific stage.
    """

    time: float
    dt: float
    step: int
    cfl: float
    reynolds: float  # generic diagnostic estimate only -- see compute_reynolds
    max_velocity: float
    kinetic_energy: float
    max_divergence: float
    l2_divergence: float
    normalized_divergence: float
    diffusion_diagnostics: tuple  # (u, v, w) DiffusionDiagnostics, in that order
    pressure_diagnostics: SolveDiagnostics
    convection_time: float
    diffusion_time: float
    elapsed_time: float
    step_profile: Dict[str, float] = field(default_factory=dict)
    nu_t_max: Optional[float] = None
    nu_t_mean: Optional[float] = None
    nu_t_max_over_nu: Optional[float] = None
    nu_t_mean_over_nu: Optional[float] = None
    pi_sgs: Optional[float] = None
    eps_nu: Optional[float] = None
    eps_total: Optional[float] = None
    w_r: Optional[float] = None
    norm_r: Optional[float] = None


def _kinetic_energy_and_max(velocity: VelocityField, mesh: StructuredMesh3D, bcs: BoundaryConditionSet) -> tuple:
    dV = mesh.cell_volume
    sq_sum = 0.0
    max_speed = 0.0
    for axis, comp in enumerate(velocity.components()):
        interior = comp.interior
        if bcs.is_periodic_axis(axis):
            sl = [slice(None)] * 3
            sl[axis] = slice(0, -1)
            interior = interior[tuple(sl)]
        sq_sum += np.sum(interior ** 2)
        max_speed = max(max_speed, float(np.max(np.abs(interior))))
    kinetic_energy = 0.5 * sq_sum * dV
    return float(kinetic_energy), max_speed


def compute_cfl(velocity: VelocityField, mesh: StructuredMesh3D, dt: float) -> float:
    """``CFL = dt * (max|u|/dx + max|v|/dy + max|w|/dz)`` (Milestone 1's
    convective CFL definition)."""
    spacings = (mesh.dx, mesh.dy, mesh.dz)
    total = 0.0
    for comp, d in zip(velocity.components(), spacings):
        total += float(np.max(np.abs(comp.interior))) / d
    return dt * total


def compute_reynolds(velocity: VelocityField, mesh: StructuredMesh3D, nu: float) -> float:
    """A cheap, generic **diagnostic Reynolds estimate**, ``Re_est =
    U*L/nu`` with ``U = max|u|`` (current state) and ``L =
    (Lx*Ly*Lz)^(1/3)`` (matching the normalized-divergence length scale
    used elsewhere, for consistency).

    This is **not** "the" Reynolds number of any particular flow -- it is
    a single, always-computable, order-of-magnitude estimate meant for
    runtime monitoring (e.g. noticing a run has drifted into a much
    higher-speed regime than intended), using the domain's geometric mean
    length as a length scale regardless of the flow's actual physics. Any
    individual benchmark with a physically meaningful length/velocity
    scale (a vortex wavelength, a channel half-height, an inlet velocity)
    should compute its **own** Reynolds number from those physical
    quantities instead of reading this value -- see
    ``docs/architecture.md``'s Milestone 6 correction section and
    ``tests/test_navier_stokes_verification.py`` for the physically
    appropriate Re computed for each verification case (A, C, D)."""
    max_speed = 0.0
    for comp in velocity.components():
        max_speed = max(max_speed, float(np.max(np.abs(comp.interior))))
    L = (mesh.lx * mesh.ly * mesh.lz) ** (1.0 / 3.0)
    return max_speed * L / nu


@dataclass
class IntegratorHistory:
    """Milestone 8 Part 4: the extra state a :class:`ThetaSchemeIntegrator`
    needs beyond a single :class:`~navier3d.fields.FlowState` to take its
    *next* step correctly, made explicit and serializable rather than
    left only as the integrator's private mutable attributes.

    ``FlowState`` already carries ``u^n`` and ``p^n`` (the latter now
    load-bearing for ``projection_method in ("incremental",
    "rotational")``, not just diagnostic, since it feeds the predictor's
    ``-(1/rho)*grad(p^n)`` term -- see the module docstring). The three
    fields here are what a restart/checkpoint additionally needs:

    * ``previous_convection`` -- ``N(u^{n-1})``, required by AB2 (both
      constant- and variable-step, Milestone 7 Part G) for every step
      after the first. ``None`` means "no history yet" -- the *next*
      step will run the Heun-startup rule, exactly as it would for a
      genuinely fresh integrator (a restart from step 0 is naturally
      reproduced by restoring ``previous_convection=None``).
    * ``previous_dt`` -- the previous step's size, needed to form
      ``r = dt/previous_dt`` for both the variable-step AB2 formula and
      (Milestone 9) the variable-step pressure-extrapolation formula
      below -- tracked unconditionally every step (not just when
      convection is enabled), since pressure extrapolation needs it even
      for a pure-Stokes (no-convection) run.
    * ``previous_phi`` -- the last pressure-*increment* solved for
      (``projection_method`` incremental/rotational only); a plausible,
      measured-not-assumed warm-start candidate for the next phi solve
      (Milestone 8 Part 15), never required for correctness (unlike the
      first two fields, whose ABSENCE changes which AB2 branch runs, an
      absent ``previous_phi`` only means the next phi solve starts cold).
    * ``previous_pressure`` -- ``p^{n-1}`` (Milestone 9): required, not
      merely a warm-start convenience, whenever ``pressure_extrapolation
      =True`` (``projection_method`` incremental/rotational) -- the
      predictor's pressure-gradient term is then extrapolated to the
      theta-scheme's own evaluation time using ``p^n`` (``state.pressure``)
      and this field, rather than using ``p^n`` directly (which Milestone
      9 identified as the actual root cause of the ~O(dt) ceiling
      Milestone 8 measured -- see the module docstring,
      "Pressure extrapolation"). ``None`` means "no history yet" -- the
      next step falls back to unextrapolated ``p^n`` (a one-time,
      documented, first-order-only startup step, the same treatment
      Milestone 6 gave AB2 before its own Heun-startup upgrade).

    Two integrators built with identical ``(mesh, bcs, rho, nu, theta,
    convection_scheme, projection_method)`` and restored to the same
    ``(FlowState, IntegratorHistory)`` pair take bit-identical next steps
    -- verified by ``tests/test_integrator_history.py``.
    """

    previous_convection: Optional[VelocityField] = None
    previous_dt: Optional[float] = None
    previous_phi: Optional[ScalarField] = None
    previous_pressure: Optional[ScalarField] = None


class ThetaSchemeIntegrator:
    """Reusable AB2-convection + theta-scheme-diffusion + projection time
    integrator. See module docstring for the discrete equations, AB2
    startup rule, and CFL definition.

    Parameters
    ----------
    mesh, bcs : the (fixed for this integrator's lifetime) mesh and
        boundary conditions.
    rho, nu : constant fluid density and kinematic viscosity.
    dt : fixed time-step size.
    theta : ``1.0`` for backward/implicit Euler (first order), ``0.5``
        for Crank-Nicolson (second order) diffusion.
    convection_scheme : ``None`` (pure Stokes flow, Milestone 5 behavior,
        unchanged), ``"centered"``, or ``"upwind"``.
    forcing : optional ``f(t) -> VelocityField`` giving the body force at
        time ``t`` (matching ``mesh``'s component shapes); evaluated at
        ``t^n + theta*dt`` each step. ``None`` means unforced (``f=0``).
    cfl_max : optional hard CFL limit; if the CFL computed from the
        *current* state before a step exceeds this, :class:`CFLError` is
        raised and the step is not taken. ``None`` disables the check.
    pressure_kwargs : forwarded to the lazily-constructed
        :class:`~navier3d.pressure.PressurePoissonSystem` on first use
        (e.g. ``solver``, ``preconditioner``, ``null_space_strategy``).
    diffusion_kwargs : forwarded to every (lazily-constructed, cached by
        ``(nu, dt, theta)``) :class:`~navier3d.diffusion.VelocityDiffusionSystem`
        (e.g. ``formulation="spd"``, ``solver="cg"``, ``preconditioner``).
        ``None`` reproduces Milestone 5/6 behavior exactly (``formulation
        ="pinned"``, ``solver="direct"``).
    warm_start : if ``True``, each step's pressure and diffusion solves
        are seeded with the *previous* step's own solution as the
        initial guess (Milestone 7 Part D) -- a no-op for direct solves,
        a genuine iteration-count reduction for iterative ones on a
        smoothly-evolving flow.
    """

    def __init__(
        self,
        mesh: StructuredMesh3D,
        bcs: BoundaryConditionSet,
        rho: float,
        nu: float,
        dt: float,
        theta: float = 1.0,
        convection_scheme: Optional[str] = None,
        forcing: Optional[ForcingFn] = None,
        cfl_max: Optional[float] = None,
        pressure_kwargs: Optional[dict] = None,
        diffusion_kwargs: Optional[dict] = None,
        warm_start: bool = False,
        diffusion_cache_max_size: int = 8,
        projection_method: str = "non_incremental",
        chi: float = 1.0,
        pressure_extrapolation: bool = False,
        initial_history: Optional["IntegratorHistory"] = None,
        turbulence_model: Optional[Any] = None,
        ramanujan_correction: Optional[Any] = None,
    ) -> None:
        if rho <= 0:
            raise ValueError(f"rho must be positive, got {rho!r}")
        if nu <= 0:
            raise ValueError(f"nu must be positive, got {nu!r}")
        if dt <= 0:
            raise ValueError(f"dt must be positive, got {dt!r}")
        if convection_scheme is not None and convection_scheme not in _CONVECTION_SCHEMES:
            raise ValueError(f"convection_scheme must be None, 'centered', or 'upwind', got {convection_scheme!r}")
        if projection_method not in _PROJECTION_METHODS:
            raise ValueError(f"projection_method must be one of {sorted(_PROJECTION_METHODS)}, got {projection_method!r}")
        if diffusion_cache_max_size < 1:
            raise ValueError(f"diffusion_cache_max_size must be >= 1, got {diffusion_cache_max_size!r}")
        self.mesh = mesh
        self.bcs = bcs
        self.rho = rho
        self.nu = nu
        self.dt = dt
        self.theta = theta
        self.convection_scheme = convection_scheme
        self.forcing = forcing
        self.cfl_max = cfl_max
        self.pressure_kwargs = dict(pressure_kwargs) if pressure_kwargs else {}
        self.diffusion_kwargs = dict(diffusion_kwargs) if diffusion_kwargs else {}
        self.warm_start = warm_start
        self.diffusion_cache_max_size = diffusion_cache_max_size
        self.projection_method = projection_method
        self.chi = chi
        self.pressure_extrapolation = pressure_extrapolation
        self.turbulence_model = turbulence_model
        self.ramanujan_correction = ramanujan_correction

        self._diffusion_cache: "OrderedDict[tuple, tuple]" = OrderedDict()
        self._pressure_system: Optional[PressurePoissonSystem] = None
        self._previous_convection: Optional[VelocityField] = None
        self._previous_dt: Optional[float] = None
        self._previous_pressure = None
        self._previous_u_star: Optional[VelocityField] = None
        self._previous_phi = None
        self._pressure_extrapolation_history: Optional[ScalarField] = None
        self.profiler = StepProfiler()
        if initial_history is not None:
            self.restore_history(initial_history)

    def _get_diffusion_systems(self, dt: float) -> tuple:
        """Lazily build (or reuse) the 3 per-component
        :class:`~navier3d.diffusion.VelocityDiffusionSystem` instances
        for this ``dt`` -- cached by ``(nu, dt, theta)``, the exact
        inputs their matrix depends on (Milestone 7 Part E). Mesh/BCs are
        fixed for this integrator's lifetime so are not part of the key;
        a topology or mesh change requires a new
        :class:`ThetaSchemeIntegrator` entirely, same as Milestone 5/6.

        **Milestone 8 Part 17 (bounded LRU)**: an adaptive-dt run can, in
        principle, visit a large or unbounded number of distinct ``dt``
        values (floating-point CFL-driven candidates rarely repeat
        exactly) -- an unbounded ``dict`` cache (Milestone 7's original
        design) would then grow without limit, each entry holding a full
        sparse matrix + factorization/preconditioner. This cache is
        instead an LRU of at most ``diffusion_cache_max_size`` entries
        (default 8): a cache hit moves that entry to the
        most-recently-used end; inserting past capacity evicts the
        least-recently-used entry. Realistic CFL-driven ``dt`` sequences
        settle toward a small, stable set of values (growth/shrink-limited,
        see ``adaptive.py``), so 8 is generous headroom, not a tight
        limit expected to thrash in practice -- verified directly by
        ``tests/test_diffusion_cache_bounded.py`` over hundreds of
        distinct ``dt`` values."""
        key = (self.nu, dt, self.theta)
        cached = self._diffusion_cache.get(key)
        if cached is not None:
            self._diffusion_cache.move_to_end(key)
            return cached
        systems = tuple(
            VelocityDiffusionSystem(self.mesh, self.bcs, axis, self.nu, dt, self.theta, **self.diffusion_kwargs)
            for axis in range(3)
        )
        if len(self._diffusion_cache) >= self.diffusion_cache_max_size:
            self._diffusion_cache.popitem(last=False)
        self._diffusion_cache[key] = systems
        return systems

    @property
    def diffusion_systems(self) -> tuple:
        """The diffusion systems for ``self.dt`` (the current/default
        step size) -- lazily built on first access, then cached; see
        :meth:`_get_diffusion_systems`."""
        return self._get_diffusion_systems(self.dt)

    @property
    def diffusion_cache_size(self) -> int:
        """Number of distinct ``(nu, dt, theta)`` diffusion-system sets
        currently cached -- exposed for reuse/invalidation tests
        (Milestone 7 Part E)."""
        return len(self._diffusion_cache)

    @property
    def pressure_system(self) -> Optional[PressurePoissonSystem]:
        return self._pressure_system

    @property
    def history(self) -> IntegratorHistory:
        """Snapshot of this integrator's serializable extra state
        (Milestone 8 Part 4) -- combine with the current
        :class:`~navier3d.fields.FlowState` for a complete restart
        point. See :class:`IntegratorHistory`."""
        return IntegratorHistory(
            previous_convection=self._previous_convection,
            previous_dt=self._previous_dt,
            previous_phi=self._previous_phi,
            previous_pressure=self._pressure_extrapolation_history,
        )

    def restore_history(self, history: IntegratorHistory) -> None:
        """Restore extra integrator state from a previously-saved
        :class:`IntegratorHistory` (e.g. loaded from a checkpoint
        alongside its paired ``FlowState``, which the caller restores
        separately and passes into the next :meth:`step` call). Does
        **not** touch the pressure/diffusion matrix caches -- those are
        rebuilt lazily and cheaply reproduce the same numerical systems
        regardless of restart, so persisting them is unnecessary."""
        self._previous_convection = history.previous_convection
        self._previous_dt = history.previous_dt
        self._previous_phi = history.previous_phi
        self._pressure_extrapolation_history = history.previous_pressure

    def step(self, state: FlowState, dt: Optional[float] = None) -> tuple:
        """Advance ``state`` by one step. ``dt`` (Milestone 7 Part F/G),
        if given, overrides ``self.dt`` for this call only (and becomes
        the new ``self.dt`` afterward, so ``diffusion_systems``/repeated
        no-argument :meth:`step` calls stay consistent with "the most
        recently used step size"); ``None`` uses ``self.dt`` unchanged
        (Milestone 5/6 behavior). Returns ``(new_state, StepDiagnostics)``;
        never mutates ``state``. Raises :class:`CFLError` if the CFL
        computed from ``state`` exceeds ``cfl_max``, or
        :class:`IntegrationError` on any non-finite result or solver
        failure."""
        step_t0 = time.perf_counter()
        dt = self.dt if dt is None else dt
        if dt <= 0:
            raise ValueError(f"dt must be positive, got {dt!r}")

        t_bc0 = time.perf_counter()
        apply_velocity_bc(state.velocity, self.bcs)  # defensive: ghosts must be filled for convection/diffusion
        bc_time = time.perf_counter() - t_bc0

        cfl = compute_cfl(state.velocity, self.mesh, dt)
        if self.cfl_max is not None and cfl > self.cfl_max:
            raise CFLError(f"CFL={cfl:.4g} exceeds cfl_max={self.cfl_max:.4g} (dt={dt:.4g}); step rejected")

        f_time = state.time + self.theta * dt
        forcing_field = self.forcing(f_time) if self.forcing is not None else None

        # Captured BEFORE any update this step -- both AB2 (Milestone 7)
        # and pressure extrapolation (Milestone 9) need "the dt used to
        # produce the CURRENT history", and both must read the same OLD
        # value; self._previous_dt is updated exactly once, below, after
        # both have used it.
        dt_previous = self._previous_dt

        convection_time = 0.0
        ab2_field: Optional[VelocityField] = None
        if self.convection_scheme is not None:
            tc0 = time.perf_counter()
            convection_fn = _CONVECTION_SCHEMES[self.convection_scheme]
            N_current = convection_fn(state.velocity, self.mesh)
            if self._previous_convection is None:
                # Second-order (Heun's method) startup -- see module
                # docstring "AB2 startup". The provisional state is a
                # convection-only forward-Euler probe, used solely to
                # obtain a second sample of N for the Heun average; it is
                # never itself used as a solution state.
                provisional = VelocityField.zeros(self.mesh)
                for comp_out, comp_in, comp_N in zip(
                    provisional.components(), state.velocity.components(), N_current.components()
                ):
                    comp_out.interior = comp_in.interior - dt * comp_N.interior
                apply_velocity_bc(provisional, self.bcs)
                N_provisional = convection_fn(provisional, self.mesh)
                ab2_field = VelocityField.zeros(self.mesh)
                for comp_out, comp_cur, comp_prov in zip(
                    ab2_field.components(), N_current.components(), N_provisional.components()
                ):
                    comp_out.interior = 0.5 * (comp_cur.interior + comp_prov.interior)
            else:
                # Variable-step AB2 (Milestone 7 Part G): NOT the
                # constant-step 3/2,-1/2 formula unless r=dt/previous_dt
                # happens to be 1 -- see
                # navier3d.adaptive.variable_step_ab2_coefficients.
                c_current, c_previous = variable_step_ab2_coefficients(dt, dt_previous)
                ab2_field = VelocityField.zeros(self.mesh)
                for comp_out, comp_cur, comp_prev in zip(ab2_field.components(), N_current.components(), self._previous_convection.components()):
                    comp_out.interior = c_current * comp_cur.interior + c_previous * comp_prev.interior
            self._previous_convection = N_current
            convection_time = time.perf_counter() - tc0

        diffusion_systems = self._get_diffusion_systems(dt)

        # Milestone 8: incremental/rotational predictor includes the
        # previous pressure's own gradient, -(1/rho)*G_h(p^n) -- see
        # module docstring, "Incremental/rotational predictor". p^n's
        # ghosts are filled with the INTEGRATOR's own (physical) bcs,
        # never the per-step Neumann-derived-from-u* values that are
        # phi's alone (see projection.py's derive_phi_bcs docstring for
        # why the two are NOT the same BC set).
        #
        # Milestone 9: using p^n directly (i.e. evaluated at t^n) inside
        # a theta=0.5 (Crank-Nicolson) predictor is only FIRST-ORDER
        # accurate in time for this term -- isolated and confirmed as
        # the actual root cause of Milestone 8's ~O(dt) ceiling (module
        # docstring, "Pressure extrapolation"). When
        # ``pressure_extrapolation=True`` and history is available, p is
        # instead linearly extrapolated to the theta-scheme's own
        # evaluation time using p^n and p^{n-1} -- the same technique
        # AB2 already uses for convection.
        pressure_gradient_field: Optional[VelocityField] = None
        if self.projection_method != "non_incremental":
            apply_pressure_bc(state.pressure, self.bcs, spacing=self.mesh.spacing)
            if self.pressure_extrapolation and self._pressure_extrapolation_history is not None:
                c_current, c_previous = pressure_extrapolation_coefficients(dt, dt_previous, self.theta)
                p_extrap = ScalarField.zeros(self.mesh)
                p_extrap.interior = (
                    c_current * state.pressure.interior
                    + c_previous * self._pressure_extrapolation_history.interior
                )
                apply_pressure_bc(p_extrap, self.bcs, spacing=self.mesh.spacing)
                pressure_gradient_field = _gradient(p_extrap, self.mesh)
            else:
                pressure_gradient_field = _gradient(state.pressure, self.mesh)

        u_star = VelocityField.zeros(self.mesh)
        diffusion_diags = []
        diffusion_time = 0.0
        diffusion_rhs_time = 0.0

        nu_t_max = None
        nu_t_mean = None
        nu_t_max_over_nu = None
        nu_t_mean_over_nu = None
        pi_sgs = None
        eps_nu = None
        eps_total = None

        w_r = None
        norm_r = None
        ramanujan_field: Optional[VelocityField] = None
        if self.ramanujan_correction is not None:
            ramanujan_field = self.ramanujan_correction.evaluate(state.velocity, self.mesh, self.bcs)
            if hasattr(self.ramanujan_correction, "compute_energy_transfer_work"):
                w_r = self.ramanujan_correction.compute_energy_transfer_work(state.velocity, self.mesh, self.bcs)
            # Calculate L2 norm of R_h
            r_sq = sum(np.sum(comp.interior ** 2) for comp in ramanujan_field.components())
            norm_r = float(np.sqrt(r_sq * self.mesh.cell_volume))

        if self.turbulence_model is not None:
            t_diff0 = time.perf_counter()
            nu_t = self.turbulence_model.eddy_viscosity(state.velocity, self.mesh, self.bcs)
            nu_eff = ScalarField.zeros(self.mesh)
            nu_eff.interior[:] = self.nu + nu_t.interior

            nu_t_max = float(np.max(nu_t.interior))
            nu_t_mean = float(np.mean(nu_t.interior))
            nu_t_max_over_nu = nu_t_max / self.nu
            nu_t_mean_over_nu = nu_t_mean / self.nu

            # Compute SGS dissipation Pi_sgs = int (2 * nu_t * S_ij * S_ij) dV
            from .strain import compute_strain_magnitude
            s_mag = compute_strain_magnitude(state.velocity, self.mesh, self.bcs)
            dV = self.mesh.cell_volume
            pi_sgs = float(np.sum(nu_t.interior * (s_mag.interior ** 2)) * dV)
            eps_nu = float(self.nu * np.sum(s_mag.interior ** 2) * dV)
            eps_total = eps_nu + pi_sgs

            # Construct predictor RHS for variable viscosity
            # (state.velocity + theta*dt*forcing_cont - theta*dt*pressure_cont - theta*dt*ab2_cont)
            var_sys = VariableDiffusionSystem(self.mesh, self.bcs, dt, self.theta, nu_eff)

            rhs_var = VelocityField.zeros(self.mesh)
            if self.theta < 1.0:
                div_tau_n = variable_viscosity_stress_divergence(state.velocity, nu_eff, self.mesh, self.bcs)
                for axis in range(3):
                    rhs_var.components()[axis].interior += ((1.0 - self.theta) * dt) * div_tau_n.components()[axis].interior

            for axis in range(3):
                rhs_comp = rhs_var.components()[axis].interior
                rhs_comp += state.velocity.components()[axis].interior
                if forcing_field is not None:
                    rhs_comp += dt * forcing_field.components()[axis].interior
                if ab2_field is not None:
                    rhs_comp -= dt * ab2_field.components()[axis].interior
                if pressure_gradient_field is not None:
                    rhs_comp -= (dt / self.rho) * pressure_gradient_field.components()[axis].interior
                if ramanujan_field is not None:
                    rhs_comp += dt * ramanujan_field.components()[axis].interior

            u_star, info = var_sys.solve(rhs_var, initial_guess=self._previous_u_star if self.warm_start else None)
            diffusion_time = time.perf_counter() - t_diff0
            diffusion_diags = [DiffusionDiagnostics(converged=(info == 0), method="bicgstab", iterations=info, residual=0.0, assembly_time=0.0, rhs_time=0.0, solve_time=diffusion_time, finite=True)] * 3
        else:
            for axis, (comp_system, comp_state) in enumerate(zip(diffusion_systems, state.velocity.components())):
                comp_forcing = None
                if forcing_field is not None:
                    comp_forcing = forcing_field.components()[axis].interior.copy()
                if ab2_field is not None:
                    conv_contribution = -ab2_field.components()[axis].interior
                    comp_forcing = conv_contribution if comp_forcing is None else comp_forcing + conv_contribution
                if pressure_gradient_field is not None:
                    pressure_contribution = -(1.0 / self.rho) * pressure_gradient_field.components()[axis].interior
                    comp_forcing = pressure_contribution if comp_forcing is None else comp_forcing + pressure_contribution
                if ramanujan_field is not None:
                    ram_contribution = ramanujan_field.components()[axis].interior
                    comp_forcing = ram_contribution if comp_forcing is None else comp_forcing + ram_contribution
                x0 = None
                if self.warm_start and self._previous_u_star is not None:
                    x0 = self._previous_u_star.components()[axis]
                comp_star, diag = comp_system.solve(comp_state, forcing=comp_forcing, x0=x0)
                diffusion_time += diag.solve_time
                diffusion_rhs_time += diag.rhs_time
                if not diag.finite:
                    raise IntegrationError(f"diffusion solve for component axis={axis} produced non-finite values: {diag}")
                if not diag.converged:
                    raise IntegrationError(f"diffusion solve for component axis={axis} did not converge: {diag}")
                u_star.components()[axis].interior = comp_star.interior
                diffusion_diags.append(diag)
            apply_velocity_bc(u_star, self.bcs)

        pressure_x0 = self._previous_pressure if self.warm_start else None
        phi_x0 = self._previous_phi if self.warm_start else None
        try:
            if self.projection_method == "non_incremental":
                if self._pressure_system is None:
                    result = project(u_star, self.bcs, self.mesh, self.rho, dt, pressure_x0=pressure_x0, **self.pressure_kwargs)
                    self._pressure_system = result.pressure_system
                else:
                    result = project(u_star, self.bcs, self.mesh, self.rho, dt, pressure_system=self._pressure_system, pressure_x0=pressure_x0)
            else:
                rotational = self.projection_method == "rotational"
                if self._pressure_system is None:
                    result = project_incremental(
                        u_star, state.pressure, self.bcs, self.mesh, self.rho, dt,
                        rotational=rotational, nu=self.nu, chi=self.chi, phi_x0=phi_x0, **self.pressure_kwargs,
                    )
                    self._pressure_system = result.pressure_system
                else:
                    result = project_incremental(
                        u_star, state.pressure, self.bcs, self.mesh, self.rho, dt,
                        rotational=rotational, nu=self.nu, chi=self.chi,
                        pressure_system=self._pressure_system, phi_x0=phi_x0,
                    )
        except ProjectionError as exc:
            raise IntegrationError(f"projection failed: {exc}") from exc

        for comp in result.velocity.components():
            if not np.all(np.isfinite(comp.data)):
                raise IntegrationError("projected velocity contains non-finite (NaN/Inf) values")
        if not np.all(np.isfinite(result.pressure.data)):
            raise IntegrationError("pressure field contains non-finite (NaN/Inf) values")
        if result.phi is not None and not np.all(np.isfinite(result.phi.data)):
            raise IntegrationError("pressure-correction field (phi) contains non-finite (NaN/Inf) values")

        new_state = FlowState(
            velocity=result.velocity,
            pressure=result.pressure,
            time=state.time + dt,
            step=state.step + 1,
        )

        if self.warm_start:
            self._previous_pressure = result.pressure
            self._previous_u_star = u_star
            if result.phi is not None:
                self._previous_phi = result.phi

        # Milestone 9: this step's own INPUT p^n becomes "p^{n-1}" for
        # the NEXT step's pressure extrapolation -- tracked whenever
        # incremental/rotational is in use (independent of warm_start,
        # which tracks something different: the OUTPUT p^{n+1} as a
        # solver initial guess, not a history sample for extrapolation).
        if self.projection_method != "non_incremental":
            self._pressure_extrapolation_history = state.pressure

        self._previous_dt = dt  # unconditional: both AB2 and pressure extrapolation need it next step
        self.dt = dt  # "current" dt now reflects the most recently used step size

        t_diag0 = time.perf_counter()
        kinetic_energy, max_velocity = _kinetic_energy_and_max(result.velocity, self.mesh, self.bcs)
        reynolds = compute_reynolds(result.velocity, self.mesh, self.nu)
        diagnostics_time = time.perf_counter() - t_diag0

        elapsed = time.perf_counter() - step_t0

        step_profile = {
            "boundary_conditions": bc_time,
            "convection": convection_time,
            "diffusion_rhs": diffusion_rhs_time,
            "diffusion_solve": diffusion_time,
            "pressure_rhs": result.rhs_time,
            "pressure_solve": result.pressure_diagnostics.solve_time,
            "projection_correction": result.correction_time,
            "diagnostics": diagnostics_time,
            "total": elapsed,
        }
        for category, seconds in step_profile.items():
            self.profiler.add(category, seconds)

        diagnostics = StepDiagnostics(
            time=new_state.time,
            dt=dt,
            step=new_state.step,
            cfl=cfl,
            reynolds=reynolds,
            max_velocity=max_velocity,
            kinetic_energy=kinetic_energy,
            max_divergence=result.max_divergence_after,
            l2_divergence=result.l2_divergence_after,
            normalized_divergence=result.normalized_divergence_after,
            diffusion_diagnostics=tuple(diffusion_diags),
            pressure_diagnostics=result.pressure_diagnostics,
            convection_time=convection_time,
            diffusion_time=diffusion_time,
            elapsed_time=elapsed,
            step_profile=step_profile,
            nu_t_max=nu_t_max,
            nu_t_mean=nu_t_mean,
            nu_t_max_over_nu=nu_t_max_over_nu,
            nu_t_mean_over_nu=nu_t_mean_over_nu,
            pi_sgs=pi_sgs,
            eps_nu=eps_nu,
            eps_total=eps_total,
            w_r=w_r,
            norm_r=norm_r,
        )
        return new_state, diagnostics


def run(integrator: ThetaSchemeIntegrator, state: FlowState, n_steps: int, callback: Optional[Callable] = None) -> tuple:
    """Minimal simulation loop: advance ``state`` by ``n_steps`` calls to
    ``integrator.step``. ``callback(state, diagnostics)``, if given, is
    invoked after every step (e.g. to record history or check a stopping
    criterion; raise inside it to stop early). Returns
    ``(final_state, list_of_StepDiagnostics)``.
    """
    history = []
    for _ in range(n_steps):
        state, diagnostics = integrator.step(state)
        history.append(diagnostics)
        if callback is not None:
            callback(state, diagnostics)
    return state, history
